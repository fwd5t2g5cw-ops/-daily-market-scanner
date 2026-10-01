from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


MARKETS = {
    "us": {
        "label": "US",
        "universe": "data/us_1b_universe.txt",
        "benchmark": "SPY",
        "min_price": 10.0,
        "min_avg_volume": 500_000,
        "min_dollar_volume": 20_000_000,
        "batch": 60,
    },
    "tsx": {
        "label": "TSX",
        "universe": "data/tsx_universe.txt",
        "benchmark": "XIU.TO",
        "min_price": 5.0,
        "min_avg_volume": 200_000,
        "min_dollar_volume": 5_000_000,
        "batch": 45,
    },
    "hk": {
        "label": "HK",
        "universe": "data/hk_5b_universe.txt",
        "benchmark": "2800.HK",
        "min_price": 1.0,
        "min_avg_volume": 500_000,
        "min_dollar_volume": 5_000_000,
        "batch": 40,
    },
}


@dataclass
class Params:
    breakout_lookback: int = 50
    swing_low_lookback: int = 80
    max_pullback_days: int = 15
    reclaim_window_days: int = 5
    outcome_days: int = 20
    near_52w_pct: float = 3.0
    min_impulse_pct: float = 20.0
    fib_ema_confluence_pct: float = 0.50
    fib236_floor_buffer_pct: float = 0.50
    min_r_to_t1: float = 2.50


def s(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").astype(float)


def flatten(d):
    if d is None or d.empty:
        return d
    d = d.copy()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d


def normalize_frame(d):
    d = flatten(d)
    need = ["Open", "High", "Low", "Close", "Volume"]
    if d is None or any(c not in d.columns for c in need):
        return None
    d = d.dropna(subset=need).copy()
    d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
    return d if len(d) >= 220 else None


def load_symbols(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    out = []
    for line in p.read_text().splitlines():
        x = line.strip().upper()
        if x and not x.startswith("#"):
            out.append(x)
    return list(dict.fromkeys(out))


def dl_single(symbol: str, start: str, end: str, attempts: int = 4):
    for a in range(attempts):
        try:
            d = yf.download(
                symbol,
                start=start,
                end=end,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            d = normalize_frame(d)
            if d is not None:
                return d
        except Exception as e:
            print("single download failed", symbol, a + 1, e)
        if a + 1 < attempts:
            time.sleep(2 * (2 ** a) + random.uniform(0.2, 0.8))
    return None


def dl_batch(symbols: list[str], start: str, end: str, attempts: int = 3):
    for a in range(attempts):
        try:
            d = yf.download(
                symbols,
                start=start,
                end=end,
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            if d is not None and not d.empty:
                return d
        except Exception as e:
            print("batch download failed", a + 1, e)
        if a + 1 < attempts:
            time.sleep(4 * (2 ** a) + random.uniform(0.5, 1.5))
    return None


def batch_frame(data, symbol: str, single: bool):
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    return normalize_frame(d)


def benchmark_rs(bench: pd.DataFrame | None, date: pd.Timestamp, lookback: int = 63):
    if bench is None or bench.empty:
        return np.nan
    bx = bench.loc[bench.index <= date]
    if len(bx) <= lookback:
        return np.nan
    c = s(bx["Close"])
    return float(c.iloc[-1] / c.iloc[-1 - lookback] - 1.0)


def indicators(df: pd.DataFrame):
    c, h, v = map(s, [df.Close, df.High, df.Volume])
    out = df.copy()
    out["EMA20"] = c.ewm(span=20, adjust=False).mean()
    out["EMA50"] = c.ewm(span=50, adjust=False).mean()
    out["SMA200"] = c.rolling(200).mean()
    out["AVG_VOL20"] = v.rolling(20).mean()
    out["ADV20"] = (c * v).rolling(20).mean()
    out["PRIOR_HIGH"] = h.shift(1).rolling(50).max()
    out["HIGH52"] = h.shift(1).rolling(252, min_periods=100).max()
    return out


def is_bullish_confirmation(bar: pd.Series) -> bool:
    o, h, l, c = map(float, [bar.Open, bar.High, bar.Low, bar.Close])
    if h <= l:
        return c > o
    return c > o and c >= (h + l) / 2.0


def outcome_after_entry(df: pd.DataFrame, entry_i: int, entry: float, stop: float, t1: float, days: int):
    risk = entry - stop
    if risk <= 0:
        return {
            "outcome": "INVALID_RISK",
            "days_to_exit": np.nan,
            "mfe_r": np.nan,
            "mae_r": np.nan,
            "hit_1r": False,
            "hit_2r": False,
            "hit_2_5r": False,
        }

    future = df.iloc[entry_i:min(len(df), entry_i + days)]
    max_high = entry
    min_low = entry
    outcome = "OPEN"
    days_to_exit = np.nan

    for k, (_, bar) in enumerate(future.iterrows(), start=0):
        lo, hi = float(bar.Low), float(bar.High)
        max_high = max(max_high, hi)
        min_low = min(min_low, lo)
        hit_stop = lo <= stop
        hit_t1 = hi >= t1
        if hit_stop and hit_t1:
            outcome = "STOP_SAME_DAY_AMBIGUOUS"
            days_to_exit = k
            break
        if hit_stop:
            outcome = "STOP"
            days_to_exit = k
            break
        if hit_t1:
            outcome = "T1"
            days_to_exit = k
            break

    mfe_r = (max_high - entry) / risk
    mae_r = (min_low - entry) / risk
    return {
        "outcome": outcome,
        "days_to_exit": days_to_exit,
        "mfe_r": round(float(mfe_r), 3),
        "mae_r": round(float(mae_r), 3),
        "hit_1r": bool(mfe_r >= 1.0),
        "hit_2r": bool(mfe_r >= 2.0),
        "hit_2_5r": bool(mfe_r >= 2.5),
    }


def find_setups(symbol: str, df: pd.DataFrame, bench: pd.DataFrame | None, cfg: dict, p: Params):
    x = indicators(df)
    c, h, l, o = map(s, [x.Close, x.High, x.Low, x.Open])
    ema20, ema50, sma200 = map(s, [x.EMA20, x.EMA50, x.SMA200])
    avg_vol, adv20, prior_high, high52 = map(s, [x.AVG_VOL20, x.ADV20, x.PRIOR_HIGH, x.HIGH52])

    cross = (c > prior_high) & (c.shift(1) <= prior_high.shift(1))
    candidate_idx = np.flatnonzero(cross.fillna(False).to_numpy())
    rows = []
    last_reclaim_i = -10_000

    for b in candidate_idx:
        if b <= 200 or b <= last_reclaim_i + 3:
            continue
        if not all(np.isfinite(z) for z in [ema20.iloc[b], ema50.iloc[b], sma200.iloc[b], prior_high.iloc[b], high52.iloc[b], avg_vol.iloc[b], adv20.iloc[b]]):
            continue

        breakout_level = float(prior_high.iloc[b])
        if breakout_level <= 0:
            continue
        close_b = float(c.iloc[b])
        strong_trend = close_b > ema20.iloc[b] > ema50.iloc[b] > sma200.iloc[b]
        liquid = close_b >= cfg["min_price"] and avg_vol.iloc[b] >= cfg["min_avg_volume"] and adv20.iloc[b] >= cfg["min_dollar_volume"]
        near_high = breakout_level >= float(high52.iloc[b]) * (1.0 - p.near_52w_pct / 100.0)
        if not (strong_trend and liquid and near_high):
            continue

        first_undercut_i = None
        undercut_breakout = False
        undercut_ema20 = False
        search_end = min(len(x) - 2, b + p.max_pullback_days)
        for j in range(b + 1, search_end + 1):
            ub = float(l.iloc[j]) < breakout_level
            ue = float(l.iloc[j]) < float(ema20.iloc[j])
            if ub or ue:
                first_undercut_i = j
                undercut_breakout = ub
                undercut_ema20 = ue
                break
        if first_undercut_i is None:
            continue

        peak_slice = h.iloc[b:first_undercut_i]
        if peak_slice.empty:
            continue
        peak_rel = int(np.argmax(peak_slice.to_numpy()))
        peak_i = b + peak_rel
        t1 = float(h.iloc[peak_i])

        lo_start = max(0, b - p.swing_low_lookback)
        impulse_low_slice = l.iloc[lo_start:b + 1]
        if impulse_low_slice.empty:
            continue
        impulse_low_i = lo_start + int(np.argmin(impulse_low_slice.to_numpy()))
        impulse_low = float(l.iloc[impulse_low_i])
        if t1 <= impulse_low:
            continue
        impulse_pct = (t1 / impulse_low - 1.0) * 100.0
        if impulse_pct < p.min_impulse_pct:
            continue

        fib236 = t1 - 0.236 * (t1 - impulse_low)
        fib382 = t1 - 0.382 * (t1 - impulse_low)
        ema_at_undercut = float(ema20.iloc[first_undercut_i])
        confluence_pct = abs(ema_at_undercut - fib236) / fib236 * 100.0

        reclaim_i = None
        reclaim_end = min(len(x) - 2, first_undercut_i + p.reclaim_window_days)
        for k in range(first_undercut_i, reclaim_end + 1):
            pull_low_so_far = float(l.iloc[b + 1:k + 1].min())
            if pull_low_so_far <= fib382:
                break
            if float(c.iloc[k]) > breakout_level and float(c.iloc[k]) > float(ema20.iloc[k]) and is_bullish_confirmation(x.iloc[k]):
                reclaim_i = k
                break
        if reclaim_i is None:
            continue

        pull_low = float(l.iloc[b + 1:reclaim_i + 1].min())
        if pull_low <= fib382:
            continue
        entry_i = reclaim_i + 1
        if entry_i >= len(x):
            continue
        entry = float(o.iloc[entry_i])
        stop = pull_low
        if entry <= stop:
            continue
        r_to_t1 = (t1 - entry) / (entry - stop)

        strict236_floor = fib236 * (1.0 - p.fib236_floor_buffer_pct / 100.0)
        strict236 = pull_low >= strict236_floor
        confluence_ok = confluence_pct <= p.fib_ema_confluence_pct
        r25_ok = r_to_t1 >= p.min_r_to_t1
        both_undercut = undercut_breakout and undercut_ema20
        full_playbook = bool(confluence_ok and r25_ok)
        full_playbook_strict236 = bool(full_playbook and strict236)
        full_playbook_both = bool(full_playbook and both_undercut)

        sym_ret = np.nan
        if b >= 63:
            sym_ret = float(c.iloc[b] / c.iloc[b - 63] - 1.0)
        bench_ret = benchmark_rs(bench, x.index[b], 63)
        rs_pct = (sym_ret - bench_ret) * 100.0 if np.isfinite(sym_ret) and np.isfinite(bench_ret) else np.nan

        out = outcome_after_entry(x, entry_i, entry, stop, t1, p.outcome_days)
        row = {
            "market": cfg["label"],
            "symbol": symbol,
            "breakout_date": str(x.index[b].date()),
            "breakout_level": round(breakout_level, 4),
            "breakout_close": round(close_b, 4),
            "peak_date": str(x.index[peak_i].date()),
            "t1": round(t1, 4),
            "undercut_date": str(x.index[first_undercut_i].date()),
            "undercut_type": "BOTH" if both_undercut else ("BREAKOUT" if undercut_breakout else "EMA20"),
            "reclaim_date": str(x.index[reclaim_i].date()),
            "entry_date": str(x.index[entry_i].date()),
            "entry": round(entry, 4),
            "stop_false_break_low": round(stop, 4),
            "risk_per_share": round(entry - stop, 4),
            "r_to_t1": round(r_to_t1, 3),
            "impulse_low_date": str(x.index[impulse_low_i].date()),
            "impulse_low": round(impulse_low, 4),
            "impulse_high": round(t1, 4),
            "impulse_pct": round(impulse_pct, 2),
            "fib_0236": round(fib236, 4),
            "fib_0382": round(fib382, 4),
            "pullback_low": round(pull_low, 4),
            "pullback_reached_0382": bool(pull_low <= fib382),
            "strict_0236_hold": strict236,
            "ema20_at_undercut": round(ema_at_undercut, 4),
            "ema_fib0236_distance_pct": round(confluence_pct, 3),
            "fib_ema_confluence_ok": confluence_ok,
            "r25_ok": r25_ok,
            "both_breakout_ema20_undercut": both_undercut,
            "full_playbook": full_playbook,
            "full_playbook_strict236": full_playbook_strict236,
            "full_playbook_both": full_playbook_both,
            "bars_breakout_to_undercut": first_undercut_i - b,
            "bars_undercut_to_reclaim": reclaim_i - first_undercut_i,
            "bars_breakout_to_entry": entry_i - b,
            "rs_63d_vs_benchmark_pct": round(rs_pct, 2) if np.isfinite(rs_pct) else np.nan,
            **out,
        }
        rows.append(row)
        last_reclaim_i = reclaim_i
    return rows


def summarize_variant(df: pd.DataFrame, name: str, mask: pd.Series):
    g = df[mask].copy()
    resolved = g[g.outcome.isin(["T1", "STOP", "STOP_SAME_DAY_AMBIGUOUS"])] if not g.empty else g
    wins = int((resolved.outcome == "T1").sum()) if not resolved.empty else 0
    losses = int((resolved.outcome != "T1").sum()) if not resolved.empty else 0
    return {
        "variant": name,
        "setups": int(len(g)),
        "resolved": int(len(resolved)),
        "wins_t1": wins,
        "losses_stop": losses,
        "t1_win_rate_pct": round(100.0 * wins / len(resolved), 2) if len(resolved) else np.nan,
        "hit_2_5r_pct": round(100.0 * g.hit_2_5r.mean(), 2) if len(g) else np.nan,
        "avg_mfe_r": round(pd.to_numeric(g.mfe_r, errors="coerce").mean(), 3) if len(g) else np.nan,
        "median_r_to_t1": round(pd.to_numeric(g.r_to_t1, errors="coerce").median(), 3) if len(g) else np.nan,
    }


def live_watch(symbol: str, df: pd.DataFrame, cfg: dict, p: Params):
    x = indicators(df)
    c, h, l = map(s, [x.Close, x.High, x.Low])
    ema20 = s(x.EMA20)
    prior_high = s(x.PRIOR_HIGH)
    high52 = s(x.HIGH52)
    ema50, sma200 = map(s, [x.EMA50, x.SMA200])
    avg_vol, adv20 = map(s, [x.AVG_VOL20, x.ADV20])
    if len(x) < 220:
        return None
    end = len(x) - 1

    cross = (c > prior_high) & (c.shift(1) <= prior_high.shift(1))
    idx = [i for i in np.flatnonzero(cross.fillna(False).to_numpy()) if end - i <= 25]
    if not idx:
        return None
    b = idx[-1]
    if not all(np.isfinite(z) for z in [ema20.iloc[b], ema50.iloc[b], sma200.iloc[b], prior_high.iloc[b], high52.iloc[b], avg_vol.iloc[b], adv20.iloc[b]]):
        return None
    close_b = float(c.iloc[b])
    breakout_level = float(prior_high.iloc[b])
    strong = close_b > ema20.iloc[b] > ema50.iloc[b] > sma200.iloc[b]
    liquid = close_b >= cfg["min_price"] and avg_vol.iloc[b] >= cfg["min_avg_volume"] and adv20.iloc[b] >= cfg["min_dollar_volume"]
    near_high = breakout_level >= float(high52.iloc[b]) * (1.0 - p.near_52w_pct / 100.0)
    if not (strong and liquid and near_high):
        return None

    first_u = None
    ub = ue = False
    for j in range(b + 1, min(end, b + p.max_pullback_days) + 1):
        tb = float(l.iloc[j]) < breakout_level
        te = float(l.iloc[j]) < float(ema20.iloc[j])
        if tb or te:
            first_u = j
            ub = tb
            ue = te
            break

    if first_u is None:
        return {
            "market": cfg["label"],
            "symbol": symbol,
            "state": "WAIT_PULLBACK",
            "breakout_date": str(x.index[b].date()),
            "breakout_level": round(breakout_level, 4),
            "current_close": round(float(c.iloc[end]), 4),
            "ema20": round(float(ema20.iloc[end]), 4),
            "days_since_breakout": end - b,
        }

    peak_slice = h.iloc[b:first_u]
    if peak_slice.empty:
        return None
    peak_i = b + int(np.argmax(peak_slice.to_numpy()))
    t1 = float(h.iloc[peak_i])
    lo_start = max(0, b - p.swing_low_lookback)
    low_slice = l.iloc[lo_start:b + 1]
    impulse_low_i = lo_start + int(np.argmin(low_slice.to_numpy()))
    impulse_low = float(l.iloc[impulse_low_i])
    if t1 <= impulse_low:
        return None
    fib236 = t1 - 0.236 * (t1 - impulse_low)
    fib382 = t1 - 0.382 * (t1 - impulse_low)
    pull_low = float(l.iloc[b + 1:end + 1].min())
    if pull_low <= fib382:
        state = "INVALID_TOO_DEEP_0382"
    else:
        reclaimed = float(c.iloc[end]) > breakout_level and float(c.iloc[end]) > float(ema20.iloc[end]) and is_bullish_confirmation(x.iloc[end])
        state = "RECLAIM_CONFIRM" if reclaimed else "UNDERCUT_WAIT_RECLAIM"
    confluence = abs(float(ema20.iloc[first_u]) - fib236) / fib236 * 100.0
    return {
        "market": cfg["label"],
        "symbol": symbol,
        "state": state,
        "breakout_date": str(x.index[b].date()),
        "breakout_level": round(breakout_level, 4),
        "undercut_date": str(x.index[first_u].date()),
        "undercut_type": "BOTH" if ub and ue else ("BREAKOUT" if ub else "EMA20"),
        "current_close": round(float(c.iloc[end]), 4),
        "ema20": round(float(ema20.iloc[end]), 4),
        "t1": round(t1, 4),
        "fib_0236": round(fib236, 4),
        "fib_0382": round(fib382, 4),
        "pullback_low": round(pull_low, 4),
        "ema_fib0236_distance_pct": round(confluence, 3),
        "days_since_breakout": end - b,
    }


def run_market(key: str, start: str, end: str, outdir: Path, p: Params, mode: str, max_symbols: int = 0):
    cfg = MARKETS[key]
    symbols = load_symbols(cfg["universe"])
    if max_symbols > 0:
        symbols = symbols[:max_symbols]
    print(f"=== {cfg['label']} {len(symbols)} symbols ===")
    bench = dl_single(cfg["benchmark"], start, end, attempts=5)
    rows = []
    watches = []
    failed = []

    for st in range(0, len(symbols), cfg["batch"]):
        batch = symbols[st:st + cfg["batch"]]
        print(cfg["label"], st + 1, "to", min(st + len(batch), len(symbols)))
        data = dl_batch(batch, start, end)
        if data is None:
            failed.extend(batch)
            continue
        single = len(batch) == 1
        for sym in batch:
            d = batch_frame(data, sym, single)
            if d is None:
                failed.append(sym)
                continue
            try:
                if mode in ("backtest", "both"):
                    rows.extend(find_setups(sym, d, bench, cfg, p))
                if mode in ("live", "both"):
                    w = live_watch(sym, d, cfg, p)
                    if w:
                        watches.append(w)
            except Exception as e:
                print("skip", cfg["label"], sym, e)
        time.sleep(random.uniform(0.5, 1.0))

    outdir.mkdir(parents=True, exist_ok=True)
    all_df = pd.DataFrame(rows)
    if not all_df.empty:
        all_df = all_df.drop_duplicates(["market", "symbol", "breakout_date", "reclaim_date"])
        all_df = all_df.sort_values(
            ["full_playbook", "full_playbook_strict236", "r_to_t1", "breakout_date"],
            ascending=[False, False, False, True],
        )
    all_df.to_csv(outdir / f"{key}_all_setups.csv", index=False)

    qualified = all_df[all_df.full_playbook == True].copy() if not all_df.empty else pd.DataFrame()
    qualified.to_csv(outdir / f"{key}_qualified_full_playbook.csv", index=False)

    watch_df = pd.DataFrame(watches)
    if not watch_df.empty:
        order = {
            "RECLAIM_CONFIRM": 0,
            "UNDERCUT_WAIT_RECLAIM": 1,
            "WAIT_PULLBACK": 2,
            "INVALID_TOO_DEEP_0382": 3,
        }
        watch_df["_rank"] = watch_df.state.map(order).fillna(9)
        watch_df = watch_df.sort_values(
            ["_rank", "ema_fib0236_distance_pct"], na_position="last"
        ).drop(columns="_rank")
    watch_df.to_csv(outdir / f"{key}_live_watch.csv", index=False)
    pd.DataFrame({"symbol": list(dict.fromkeys(failed))}).to_csv(
        outdir / f"{key}_failed_symbols.csv", index=False
    )
    return all_df, qualified, watch_df


def main():
    ap = argparse.ArgumentParser(
        description="False-break -> reclaim -> second-breakout scanner/backtest"
    )
    ap.add_argument("--markets", default="us,tsx,hk")
    ap.add_argument("--start", default=None, help="YYYY-MM-DD; default two years before end")
    ap.add_argument("--end", default=None, help="YYYY-MM-DD; default latest")
    ap.add_argument("--mode", choices=["backtest", "live", "both"], default="both")
    ap.add_argument("--outdir", default="false_break_reclaim_results")
    ap.add_argument("--max-symbols", type=int, default=0, help="0 = full universe")
    ap.add_argument("--confluence-pct", type=float, default=0.50)
    ap.add_argument("--min-r", type=float, default=2.50)
    ap.add_argument("--outcome-days", type=int, default=20)
    a = ap.parse_args()

    end_ts = (
        pd.Timestamp(a.end)
        if a.end
        else pd.Timestamp.utcnow().tz_localize(None).normalize() + pd.Timedelta(days=1)
    )
    start_ts = pd.Timestamp(a.start) if a.start else end_ts - pd.Timedelta(days=730)
    start = start_ts.strftime("%Y-%m-%d")
    end = end_ts.strftime("%Y-%m-%d")
    p = Params(
        fib_ema_confluence_pct=a.confluence_pct,
        min_r_to_t1=a.min_r,
        outcome_days=a.outcome_days,
    )
    outdir = Path(a.outdir)

    combined = []
    combined_q = []
    combined_watch = []
    for key in [m.strip() for m in a.markets.split(",") if m.strip()]:
        all_df, q, w = run_market(
            key, start, end, outdir, p, a.mode, a.max_symbols
        )
        if not all_df.empty:
            combined.append(all_df)
        if not q.empty:
            combined_q.append(q)
        if not w.empty:
            combined_watch.append(w)

    all_combined = (
        pd.concat(combined, ignore_index=True) if combined else pd.DataFrame()
    )
    q_combined = (
        pd.concat(combined_q, ignore_index=True) if combined_q else pd.DataFrame()
    )
    w_combined = (
        pd.concat(combined_watch, ignore_index=True)
        if combined_watch
        else pd.DataFrame()
    )
    all_combined.to_csv(outdir / "all_markets_all_setups.csv", index=False)
    q_combined.to_csv(
        outdir / "all_markets_qualified_full_playbook.csv", index=False
    )
    w_combined.to_csv(outdir / "all_markets_live_watch.csv", index=False)

    summary_rows = []
    if not all_combined.empty:
        variants = [
            ("CORE_no_0382_reclaim", pd.Series(True, index=all_combined.index)),
            (
                "+Fib0236_EMA20_confluence",
                all_combined.fib_ema_confluence_ok == True,
            ),
            (
                "+R_at_least_2_5",
                (all_combined.fib_ema_confluence_ok == True)
                & (all_combined.r25_ok == True),
            ),
            (
                "+Strict_0236_hold",
                (all_combined.fib_ema_confluence_ok == True)
                & (all_combined.r25_ok == True)
                & (all_combined.strict_0236_hold == True),
            ),
            (
                "+Both_breakout_and_EMA20_undercut",
                (all_combined.fib_ema_confluence_ok == True)
                & (all_combined.r25_ok == True)
                & (all_combined.both_breakout_ema20_undercut == True),
            ),
        ]
        for name, mask in variants:
            summary_rows.append(summarize_variant(all_combined, name, mask))
        for market, g in all_combined.groupby("market"):
            summary_rows.append(
                summarize_variant(g, f"FULL_{market}", g.full_playbook == True)
            )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(outdir / "variant_summary.csv", index=False)

    print("\n=== FALSE BREAK -> RECLAIM BACKTEST SUMMARY ===")
    print(summary.to_string(index=False) if not summary.empty else "(no setups)")
    if not q_combined.empty:
        cols = [
            "market",
            "symbol",
            "breakout_date",
            "undercut_date",
            "reclaim_date",
            "entry_date",
            "undercut_type",
            "entry",
            "stop_false_break_low",
            "t1",
            "r_to_t1",
            "ema_fib0236_distance_pct",
            "strict_0236_hold",
            "outcome",
            "mfe_r",
        ]
        print("\n=== QUALIFIED FULL PLAYBOOK EXAMPLES ===")
        print(q_combined[cols].tail(40).to_string(index=False))
    if not w_combined.empty:
        print("\n=== CURRENT LIVE WATCH ===")
        print(w_combined.head(60).to_string(index=False))


if __name__ == "__main__":
    main()
