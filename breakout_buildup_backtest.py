from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def as_series(v):
    if isinstance(v, pd.DataFrame):
        if v.shape[1] == 0:
            return pd.Series(dtype=float)
        v = v.iloc[:, 0]
    return pd.to_numeric(v, errors="coerce").astype(float)


def slope(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) < 3:
        return np.nan
    return float(np.polyfit(np.arange(len(s), dtype=float), s.to_numpy(float), 1)[0])


def load_symbols(path: str, limit: int | None) -> list[str]:
    syms = [x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith("#")]
    syms = list(dict.fromkeys(syms))
    return syms[:limit] if limit else syms


def independent_tests(high: pd.Series, low: pd.Series, top: float, tol_pct: float,
                      min_gap: int, min_pullback_pct: float) -> tuple[int, list[int]]:
    floor = top * (1.0 - tol_pct / 100.0)
    candidates = [j for j, h in enumerate(high.to_numpy()) if h >= floor]
    if not candidates:
        return 0, []
    tests = [candidates[0]]
    for j in candidates[1:]:
        prev = tests[-1]
        if j - prev < min_gap:
            continue
        between_low = float(low.iloc[prev:j + 1].min())
        pullback_pct = (top - between_low) / top * 100.0 if top > 0 else 0.0
        if pullback_pct >= min_pullback_pct:
            tests.append(j)
    return len(tests), tests


def find_impulse(low: pd.Series, high: pd.Series, buildup_start: int,
                 lookback: int, early_anchor_days: int) -> tuple[float, float, int, int] | None:
    # Same v2 anchor idea as scanner, but all indices are strictly pre-breakout.
    n = len(high)
    hi_start = max(0, buildup_start - 5)
    hi_end = min(n, buildup_start + max(1, early_anchor_days))
    if hi_end <= hi_start:
        return None
    anchor = high.iloc[hi_start:hi_end]
    hi_pos = hi_start + int(np.argmax(anchor.to_numpy()))
    impulse_high = float(high.iloc[hi_pos])
    lo_start = max(0, hi_pos - lookback)
    if hi_pos <= lo_start:
        return None
    lo_slice = low.iloc[lo_start:hi_pos]
    if lo_slice.empty:
        return None
    lo_pos = lo_start + int(np.argmin(lo_slice.to_numpy()))
    impulse_low = float(low.iloc[lo_pos])
    if impulse_high <= impulse_low:
        return None
    return impulse_low, impulse_high, lo_pos, hi_pos


def setup_at(df: pd.DataFrame, i: int, a) -> dict | None:
    """Evaluate setup using bars strictly BEFORE breakout bar i."""
    b = a.buildup_days
    if i < max(a.min_history, b + 10):
        return None
    hist = df.iloc[:i].copy()  # no breakout-day information
    if len(hist) < a.min_history:
        return None

    close = as_series(hist["Close"])
    high = as_series(hist["High"])
    low = as_series(hist["Low"])
    volume = as_series(hist["Volume"])
    if close.isna().any() or high.isna().any() or low.isna().any() or volume.isna().any():
        return None

    last_close = float(close.iloc[-1])
    avg_vol20 = float(volume.iloc[-20:].mean())
    if last_close < a.min_price or avg_vol20 < a.min_avg_volume or last_close * avg_vol20 < a.min_dollar_volume:
        return None

    lookback = min(a.high_lookback, len(hist))
    hist_high = float(high.iloc[-lookback:].max())
    near_high = last_close >= hist_high * (1.0 - a.max_below_high_pct / 100.0)

    b_high, b_low, b_vol = high.iloc[-b:], low.iloc[-b:], volume.iloc[-b:]
    top = float(b_high.max())
    bottom = float(b_low.min())
    width = top - bottom
    width_pct = width / bottom * 100.0 if bottom > 0 else np.nan
    practical_width = a.min_buildup_width_pct <= width_pct <= a.max_buildup_width_pct

    half = max(2, b // 2)
    q = max(2, b // 4)
    first_half_range = float(b_high.iloc[:half].max() - b_low.iloc[:half].min())
    second_half_range = float(b_high.iloc[-half:].max() - b_low.iloc[-half:].min())
    last_quarter_range = float(b_high.iloc[-q:].max() - b_low.iloc[-q:].min())
    range_contracting = (
        first_half_range > 0
        and second_half_range <= first_half_range * a.range_contract_ratio
        and last_quarter_range <= second_half_range * a.last_quarter_ratio
    )
    volume_contracting = bool(slope(b_vol) < 0)
    bodies = (hist["Close"] - hist["Open"]).abs().iloc[-b:]
    candles_shrinking = bool(slope(bodies) < 0)

    nt, test_idx = independent_tests(
        b_high, b_low, top, a.touch_tolerance_pct,
        a.min_touch_gap_days, a.min_between_touch_pullback_pct,
    )
    recent_touch = bool(test_idx and test_idx[-1] >= b - a.recent_touch_days)
    repeated_tests = nt >= a.min_resistance_touches and recent_touch

    buildup_start = len(hist) - b
    imp = find_impulse(low, high, buildup_start, a.impulse_lookback, a.early_buildup_anchor_days)
    if imp is None:
        return None
    impulse_low, impulse_high, lo_pos, hi_pos = imp
    impulse_height = impulse_high - impulse_low
    fib0236 = impulse_high - 0.236 * impulse_height
    above0236 = bottom >= fib0236
    impulse_reaches = impulse_high >= top * (1.0 - a.impulse_high_tolerance_pct / 100.0)
    buildup_near_high = top >= hist_high * (1.0 - a.max_below_high_pct / 100.0)

    mandatory = all([near_high, buildup_near_high, practical_width, impulse_reaches,
                     above0236, volume_contracting, range_contracting, repeated_tests])
    if not mandatory:
        return None

    return {
        "setup_date": hist.index[-1], "top": top, "bottom": bottom,
        "impulse_low": impulse_low, "impulse_high": impulse_high,
        "fib0236": fib0236, "width_pct": width_pct, "touches": nt,
        "candles_shrinking": candles_shrinking, "hist_high": hist_high,
        "impulse_height": impulse_height,
    }


def resolve_trade(df: pd.DataFrame, entry_i: int, entry: float, stop: float, t1: float, t2: float,
                  max_hold: int, same_bar_policy: str) -> dict:
    risk = entry - stop
    end = min(len(df), entry_i + max_hold + 1)
    t1_hit = False
    t1_date = pd.NaT
    t2_hit = False
    exit_price = np.nan
    exit_date = pd.NaT
    outcome = "TIME"

    for j in range(entry_i, end):
        o, h, l, c = map(float, [df["Open"].iloc[j], df["High"].iloc[j], df["Low"].iloc[j], df["Close"].iloc[j]])
        # On entry bar only the post-trigger path is unknowable from daily bars.
        hit_stop = l <= stop
        hit_t1 = h >= t1
        hit_t2 = h >= t2

        if j == entry_i and same_bar_policy == "ignore":
            hit_stop = hit_t1 = hit_t2 = False

        if hit_stop and (hit_t1 or hit_t2) and same_bar_policy == "conservative":
            exit_price, exit_date, outcome = stop, df.index[j], "STOP_SAME_BAR_AMBIG"
            break
        if hit_stop:
            # Gap-through stop is filled at open if open is below stop.
            exit_price = min(stop, o) if j > entry_i else stop
            exit_date, outcome = df.index[j], "STOP"
            break
        if hit_t1 and not t1_hit:
            t1_hit, t1_date = True, df.index[j]
        if hit_t2:
            t2_hit = True
            exit_price = max(t2, o) if o >= t2 else t2
            exit_date, outcome = df.index[j], "T2"
            break

    if pd.isna(exit_date):
        j = end - 1
        exit_price = float(df["Close"].iloc[j])
        exit_date = df.index[j]
        outcome = "TIME_T1" if t1_hit else "TIME"

    r = (exit_price - entry) / risk if risk > 0 else np.nan
    return {
        "exit_date": exit_date, "exit_price": exit_price, "outcome": outcome,
        "t1_hit": t1_hit, "t1_date": t1_date, "t2_hit": t2_hit,
        "r_multiple": r, "holding_days": int(df.index.get_loc(exit_date) - entry_i),
    }


def backtest_symbol(symbol: str, df: pd.DataFrame, a) -> list[dict]:
    df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"]).copy()
    if len(df) < a.min_history + a.buildup_days:
        return []
    trades = []
    next_allowed = 0
    for i in range(a.min_history, len(df)):
        if i < next_allowed:
            continue
        s = setup_at(df, i, a)
        if s is None:
            continue
        trigger = s["top"] * (1.0 + a.breakout_buffer_pct / 100.0)
        o, h, c = map(float, [df["Open"].iloc[i], df["High"].iloc[i], df["Close"].iloc[i]])
        # Require a real break and a close above the trigger to avoid intraday poke-only signals.
        if h < trigger or c <= trigger:
            continue
        entry = max(trigger, o)  # stop-order gap handling
        stop = s["bottom"]
        if entry <= stop:
            continue
        risk = entry - stop
        t1 = entry + 1.5 * (s["top"] - s["bottom"])
        t2 = entry + 0.618 * s["impulse_height"]
        result = resolve_trade(df, i, entry, stop, t1, t2, a.max_hold_days, a.same_bar_policy)
        trades.append({
            "symbol": symbol, "setup_date": s["setup_date"], "entry_date": df.index[i],
            "entry": entry, "stop": stop, "target1": t1, "target2": t2,
            "risk_per_share": risk, "buildup_width_pct": s["width_pct"],
            "touches": s["touches"], "fib0236": s["fib0236"],
            "impulse_low": s["impulse_low"], "impulse_high": s["impulse_high"],
            "candles_shrinking_bonus": s["candles_shrinking"], **result,
        })
        if a.one_trade_at_a_time:
            next_allowed = int(df.index.get_loc(result["exit_date"])) + 1
    return trades


def metrics(t: pd.DataFrame) -> dict:
    if t.empty:
        return {"trades": 0}
    r = pd.to_numeric(t["r_multiple"], errors="coerce").dropna()
    wins, losses = r[r > 0], r[r < 0]
    gp, gl = float(wins.sum()), float(-losses.sum())
    ordered = t.sort_values("exit_date").copy()
    eq = ordered["r_multiple"].fillna(0).cumsum()
    dd = eq - eq.cummax()
    return {
        "trades": int(len(t)), "win_rate_pct": round(float((r > 0).mean() * 100), 2),
        "avg_r": round(float(r.mean()), 3), "median_r": round(float(r.median()), 3),
        "profit_factor_r": round(gp / gl, 3) if gl > 0 else None,
        "max_drawdown_r": round(float(dd.min()), 3),
        "t1_hit_rate_pct": round(float(t["t1_hit"].mean() * 100), 2),
        "t2_hit_rate_pct": round(float(t["t2_hit"].mean() * 100), 2),
        "avg_holding_days": round(float(t["holding_days"].mean()), 2),
        "total_r": round(float(r.sum()), 3),
    }


def main():
    p = argparse.ArgumentParser(description="No-lookahead backtest for Breakout + Buildup Playbook v2")
    p.add_argument("--symbols", default="data/us_1b_universe.txt")
    p.add_argument("--output-dir", default="backtest_output")
    p.add_argument("--period", default="5y")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=80)
    p.add_argument("--min-history", type=int, default=180)
    p.add_argument("--high-lookback", type=int, default=252)
    p.add_argument("--max-below-high-pct", type=float, default=5.0)
    p.add_argument("--buildup-days", type=int, default=15)
    p.add_argument("--impulse-lookback", type=int, default=80)
    p.add_argument("--early-buildup-anchor-days", type=int, default=5)
    p.add_argument("--impulse-high-tolerance-pct", type=float, default=2.0)
    p.add_argument("--range-contract-ratio", type=float, default=0.85)
    p.add_argument("--last-quarter-ratio", type=float, default=0.90)
    p.add_argument("--touch-tolerance-pct", type=float, default=0.6)
    p.add_argument("--min-resistance-touches", type=int, default=3)
    p.add_argument("--min-touch-gap-days", type=int, default=2)
    p.add_argument("--min-between-touch-pullback-pct", type=float, default=0.8)
    p.add_argument("--recent-touch-days", type=int, default=5)
    p.add_argument("--breakout-buffer-pct", type=float, default=0.0)
    p.add_argument("--min-buildup-width-pct", type=float, default=0.5)
    p.add_argument("--max-buildup-width-pct", type=float, default=12.0)
    p.add_argument("--min-price", type=float, default=5.0)
    p.add_argument("--min-avg-volume", type=float, default=200000)
    p.add_argument("--min-dollar-volume", type=float, default=5000000)
    p.add_argument("--max-hold-days", type=int, default=60)
    p.add_argument("--same-bar-policy", choices=["conservative", "ignore"], default="conservative")
    p.add_argument("--one-trade-at-a-time", action=argparse.BooleanOptionalAction, default=True)
    a = p.parse_args()

    symbols = load_symbols(a.symbols, a.limit)
    rows: list[dict] = []
    for st in range(0, len(symbols), a.batch_size):
        batch = symbols[st:st + a.batch_size]
        print(f"Downloading {st + 1}-{min(st + len(batch), len(symbols))} / {len(symbols)}")
        try:
            data = yf.download(batch, period=a.period, interval="1d", group_by="ticker",
                               auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print("batch failed", e)
            continue
        for sym in batch:
            try:
                sdf = data if len(batch) == 1 else data[sym]
                rows.extend(backtest_symbol(sym, sdf, a))
            except Exception as e:
                print("skip", sym, e)
        time.sleep(0.35)

    outdir = Path(a.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    if not t.empty:
        for col in ["setup_date", "entry_date", "exit_date", "t1_date"]:
            t[col] = pd.to_datetime(t[col], errors="coerce")
        t = t.sort_values(["entry_date", "symbol"]).reset_index(drop=True)
    t.to_csv(outdir / "trades.csv", index=False)

    m = metrics(t)
    (outdir / "summary.json").write_text(json.dumps(m, indent=2), encoding="utf-8")

    if not t.empty:
        yearly = []
        for year, g in t.groupby(t["entry_date"].dt.year):
            mm = metrics(g)
            mm["year"] = int(year)
            yearly.append(mm)
        pd.DataFrame(yearly).sort_values("year").to_csv(outdir / "yearly.csv", index=False)
    else:
        pd.DataFrame().to_csv(outdir / "yearly.csv", index=False)

    print("\n=== BREAKOUT BUILDUP BACKTEST ===")
    print(json.dumps(m, indent=2))
    print(f"Saved outputs to {outdir}")


if __name__ == "__main__":
    main()
