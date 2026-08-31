from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import breakout_buildup_backtest as bb


def _series(x):
    if isinstance(x, pd.DataFrame):
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").astype(float)


def gap_metrics(df: pd.DataFrame, end_date, impulse_low: float, impulse_high: float, lookback: int = 90):
    """Estimate whether one early gap created too much of the measured impulse.

    gap_share = largest positive open-vs-prior-close gap / total impulse height.
    gap_position = 0 at impulse low and 1 at impulse high.
    This is designed to reject DSGR-like gap-created impulses while allowing a late-trend
    gap such as the PSX calibration example.
    """
    h = df.loc[:end_date].tail(lookback + 25).copy()
    if len(h) < 5 or impulse_high <= impulse_low:
        return np.nan, np.nan, False
    low_s, high_s, open_s, close_s = map(_series, [h["Low"], h["High"], h["Open"], h["Close"]])
    hi_candidates = np.where(np.isclose(high_s.to_numpy(), impulse_high, rtol=0, atol=max(0.01, impulse_high * 0.001)))[0]
    hi = int(hi_candidates[-1]) if len(hi_candidates) else int(np.argmin(np.abs(high_s.to_numpy() - impulse_high)))
    if hi <= 0:
        return np.nan, np.nan, False
    lo_start = max(0, hi - lookback)
    lo_slice = low_s.iloc[lo_start:hi]
    lo = lo_start + int(np.argmin(np.abs(lo_slice.to_numpy() - impulse_low)))
    if hi <= lo:
        return np.nan, np.nan, False
    imp_h = impulse_high - impulse_low
    best_gap = 0.0
    best_pos = np.nan
    for j in range(lo + 1, hi + 1):
        g = float(open_s.iloc[j] - close_s.iloc[j - 1])
        if g > best_gap:
            best_gap = g
            best_pos = (j - lo) / max(1, hi - lo)
    share = best_gap / imp_h if imp_h > 0 else np.nan
    dominated = bool(np.isfinite(share) and np.isfinite(best_pos) and share >= 0.35 and best_pos <= 0.60)
    return share, best_pos, dominated


def ema_fib_trade(symbol: str, df: pd.DataFrame, i: int, a):
    """Signal uses only data available before bar i; entry is a pre-hung limit at EMA20.

    Rules being tested:
      - strong impulse into/near 52-week high
      - EMA20 is within configured distance of Fib 0.236
      - bar i trades down to EMA20 (limit fill)
      - Fib 0.382 is the hard invalidation/stop
      - first objective is prior impulse high
    Forward 5/10/20-day returns are also recorded so the entry can be studied without
    over-committing to a single exit rule.
    """
    if i < max(a.min_history, 100):
        return None
    hist = df.iloc[:i].copy()
    close, high, low = map(_series, [hist["Close"], hist["High"], hist["Low"]])
    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])

    # Recent high must be part of the current structure, not an old peak.
    recent_n = min(a.recent_high_days, len(hist))
    recent_high_slice = high.iloc[-recent_n:]
    hi_pos = len(hist) - recent_n + int(np.argmax(recent_high_slice.to_numpy()))
    impulse_high = float(high.iloc[hi_pos])
    hist_high = float(high.iloc[-min(252, len(hist)):].max())
    if impulse_high < hist_high * (1.0 - a.max_below_high_pct / 100.0):
        return None

    lo_start = max(0, hi_pos - a.impulse_lookback)
    if hi_pos <= lo_start:
        return None
    lo_slice = low.iloc[lo_start:hi_pos]
    lo_pos = lo_start + int(np.argmin(lo_slice.to_numpy()))
    impulse_low = float(low.iloc[lo_pos])
    if impulse_high <= impulse_low:
        return None
    imp_h = impulse_high - impulse_low
    fib236 = impulse_high - 0.236 * imp_h
    fib382 = impulse_high - 0.382 * imp_h

    confluence_pct = abs(ema20 - fib236) / fib236 * 100.0
    if confluence_pct > a.ema_fib_max_distance_pct:
        return None

    # Price before candidate bar should still be in a shallow pullback, not already broken.
    prev_close = float(close.iloc[-1])
    if prev_close < fib382:
        return None

    o, h, l, c = map(float, [df["Open"].iloc[i], df["High"].iloc[i], df["Low"].iloc[i], df["Close"].iloc[i]])
    entry = ema20
    # Limit at EMA20: a gap below fills at the open; otherwise it fills if low reaches EMA20.
    if o <= entry:
        fill = o
    elif l <= entry <= h:
        fill = entry
    else:
        return None
    stop = fib382
    if fill <= stop:
        return None

    share, pos, dominated = gap_metrics(df, hist.index[-1], impulse_low, impulse_high, a.impulse_lookback)
    if a.apply_gap_filter and dominated:
        return None

    risk = fill - stop
    target = impulse_high
    if target <= fill or risk <= 0:
        return None

    exit_price = np.nan
    exit_date = pd.NaT
    outcome = "TIME20"
    hit_target = False
    end = min(len(df), i + 21)
    for j in range(i, end):
        oo, hh, ll = map(float, [df["Open"].iloc[j], df["High"].iloc[j], df["Low"].iloc[j]])
        hit_s = ll <= stop
        hit_t = hh >= target
        if hit_s and hit_t:
            exit_price, exit_date, outcome = stop, df.index[j], "STOP_SAME_BAR_AMBIG"
            break
        if hit_s:
            exit_price = min(stop, oo) if j > i else stop
            exit_date, outcome = df.index[j], "STOP"
            break
        if hit_t:
            exit_price = max(target, oo) if oo >= target else target
            exit_date, outcome, hit_target = df.index[j], "PRIOR_HIGH", True
            break
    if pd.isna(exit_date):
        j = end - 1
        exit_price, exit_date = float(df["Close"].iloc[j]), df.index[j]

    def fwd(days):
        j = min(len(df) - 1, i + days)
        return (float(df["Close"].iloc[j]) / fill - 1.0) * 100.0

    return {
        "symbol": symbol, "entry_date": df.index[i], "entry": fill, "ema20": ema20,
        "fib0236": fib236, "fib0382": fib382, "confluence_pct": confluence_pct,
        "impulse_low": impulse_low, "impulse_high": impulse_high,
        "gap_share": share, "gap_position": pos, "gap_dominated": dominated,
        "stop": stop, "target_prior_high": target, "exit_date": exit_date,
        "exit_price": exit_price, "outcome": outcome, "target_hit": hit_target,
        "r_multiple": (exit_price - fill) / risk,
        "holding_days": int(df.index.get_loc(exit_date) - i),
        "fwd_5d_pct": fwd(5), "fwd_10d_pct": fwd(10), "fwd_20d_pct": fwd(20),
    }


def summarize_ema(t: pd.DataFrame):
    if t.empty:
        return {"trades": 0}
    r = pd.to_numeric(t.r_multiple, errors="coerce").dropna()
    wins, losses = r[r > 0], r[r < 0]
    gp, gl = float(wins.sum()), float(-losses.sum())
    return {
        "trades": int(len(t)),
        "win_rate_pct": round(float((r > 0).mean() * 100), 2),
        "prior_high_hit_pct": round(float(t.target_hit.mean() * 100), 2),
        "avg_r": round(float(r.mean()), 3),
        "median_r": round(float(r.median()), 3),
        "profit_factor_r": round(gp / gl, 3) if gl > 0 else None,
        "avg_fwd_5d_pct": round(float(t.fwd_5d_pct.mean()), 3),
        "avg_fwd_10d_pct": round(float(t.fwd_10d_pct.mean()), 3),
        "avg_fwd_20d_pct": round(float(t.fwd_20d_pct.mean()), 3),
        "avg_holding_days": round(float(t.holding_days.mean()), 2),
        "total_r": round(float(r.sum()), 3),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", default="data/us_1b_universe.txt")
    p.add_argument("--period", default="5y")
    p.add_argument("--output-dir", default="gap_ema20_output")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=80)
    p.add_argument("--min-history", type=int, default=180)
    p.add_argument("--recent-high-days", type=int, default=20)
    p.add_argument("--impulse-lookback", type=int, default=80)
    p.add_argument("--max-below-high-pct", type=float, default=5.0)
    p.add_argument("--ema-fib-max-distance-pct", type=float, default=1.0)
    p.add_argument("--apply-gap-filter", action=argparse.BooleanOptionalAction, default=True)
    a = p.parse_args()

    symbols = bb.load_symbols(a.symbols, a.limit)
    base_rows, ema_rows = [], []
    for st in range(0, len(symbols), a.batch_size):
        batch = symbols[st:st + a.batch_size]
        print(f"Downloading {st+1}-{min(st+len(batch), len(symbols))} / {len(symbols)}")
        try:
            data = yf.download(batch, period=a.period, interval="1d", group_by="ticker", auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print("batch failed", e); continue
        for sym in batch:
            try:
                sdf = (data if len(batch) == 1 else data[sym]).dropna(subset=["Open","High","Low","Close","Volume"]).copy()
                # Existing breakout+buildup baseline, then classify gap domination.
                class BA: pass
                ba = BA()
                defaults = {
                    "buildup_days":15,"min_history":180,"min_price":5.0,"min_avg_volume":200000,
                    "min_dollar_volume":5000000,"high_lookback":252,"max_below_high_pct":5.0,
                    "min_buildup_width_pct":0.5,"max_buildup_width_pct":12.0,"range_contract_ratio":0.85,
                    "last_quarter_ratio":0.90,"touch_tolerance_pct":0.6,"min_touch_gap_days":2,
                    "min_between_touch_pullback_pct":0.8,"recent_touch_days":5,"min_resistance_touches":3,
                    "impulse_lookback":80,"early_buildup_anchor_days":5,"impulse_high_tolerance_pct":2.0,
                    "breakout_buffer_pct":0.0,"max_hold_days":60,"same_bar_policy":"conservative",
                    "one_trade_at_a_time":True,
                }
                for k,v in defaults.items(): setattr(ba,k,v)
                br = bb.backtest_symbol(sym, sdf, ba)
                for tr in br:
                    sh, gp, dom = gap_metrics(sdf, tr["setup_date"], tr["impulse_low"], tr["impulse_high"], 80)
                    tr["gap_share"], tr["gap_position"], tr["gap_dominated"] = sh, gp, dom
                    base_rows.append(tr)

                next_allowed = 0
                for i in range(a.min_history, len(sdf)):
                    if i < next_allowed: continue
                    tr = ema_fib_trade(sym, sdf, i, a)
                    if tr:
                        ema_rows.append(tr)
                        next_allowed = int(sdf.index.get_loc(tr["exit_date"])) + 1
            except Exception as e:
                print("skip", sym, e)
        time.sleep(0.35)

    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    base = pd.DataFrame(base_rows)
    ema = pd.DataFrame(ema_rows)
    base.to_csv(out / "breakout_gap_classified.csv", index=False)
    ema.to_csv(out / "ema20_fib0236_trades.csv", index=False)

    base_all = bb.metrics(base) if not base.empty else {"trades":0}
    base_filtered = bb.metrics(base[~base.gap_dominated].copy()) if not base.empty else {"trades":0}
    gap_rejected = int(base.gap_dominated.sum()) if not base.empty else 0
    comparison = {"baseline":base_all,"gap_filtered":base_filtered,"gap_rejected_trades":gap_rejected}
    (out / "breakout_gap_comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    ema_summary = summarize_ema(ema)
    (out / "ema20_fib0236_summary.json").write_text(json.dumps(ema_summary, indent=2), encoding="utf-8")

    print("\n=== BREAKOUT GAP FILTER COMPARISON ===")
    print(json.dumps(comparison, indent=2))
    print("\n=== EMA20 + FIB 0.236 STUDY ===")
    print(json.dumps(ema_summary, indent=2))

if __name__ == "__main__":
    main()
