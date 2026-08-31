from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from ema20_fib0236_v2_study import find_impulse_before, load_symbols, s

# Signal definition: use D_strong_impulse from V2.
EMA_FIB_DIST_PCT = 0.50
MIN_IMPULSE_PCT = 20.0
MAX_BELOW_52W_HIGH_PCT = 3.0
MAX_PULLBACK_BELOW_236_PCT = 0.50

STOP_VARIANTS = {
    "S1_fib236_minus_0p50pct": "fib236_buffer",
    "S2_ema20_minus_0p75pct": "ema20_buffer",
    "S3_fib382": "fib382",
}
T1_VARIANTS = ["prior_high", "1R", "1p5R"]
MANAGEMENT = ["hold_original_stop", "breakeven_after_t1"]


def get_entry_signal(symbol: str, df: pd.DataFrame, i: int, imp: dict, last_key):
    key = (imp["lo"], imp["hi"])
    if key == last_key:
        return None
    if imp["impulse_pct"] < MIN_IMPULSE_PCT:
        return None
    if imp["high"] < imp["high52"] * (1.0 - MAX_BELOW_52W_HIGH_PCT / 100.0):
        return None

    fib236, fib382, ema20 = imp["fib236"], imp["fib382"], imp["ema20"]
    confluence = abs(ema20 - fib236) / fib236 * 100.0
    if confluence > EMA_FIB_DIST_PCT:
        return None

    pull = df.iloc[imp["hi"] + 1:i]
    if pull.empty:
        return None
    pull_low = float(s(pull["Low"]).min())
    allowed_floor = fib236 * (1.0 - MAX_PULLBACK_BELOW_236_PCT / 100.0)
    if pull_low < allowed_floor or pull_low <= fib382:
        return None

    if (s(pull["Low"]) <= ema20).any():
        return None

    o, h, l = map(float, [df["Open"].iloc[i], df["High"].iloc[i], df["Low"].iloc[i]])
    if o <= ema20:
        entry = o
    elif l <= ema20 <= h:
        entry = ema20
    else:
        return None
    if l <= fib382 or entry <= fib382:
        return None

    return {
        "symbol": symbol,
        "entry_i": i,
        "entry_date": df.index[i],
        "entry": float(entry),
        "ema20": float(ema20),
        "fib236": float(fib236),
        "fib382": float(fib382),
        "impulse_low": float(imp["low"]),
        "impulse_high": float(imp["high"]),
        "impulse_pct": float(imp["impulse_pct"]),
        "confluence_pct": float(confluence),
    }


def stop_price(sig: dict, stop_name: str) -> float:
    if stop_name == "S1_fib236_minus_0p50pct":
        return sig["fib236"] * 0.995
    if stop_name == "S2_ema20_minus_0p75pct":
        return sig["ema20"] * 0.9925
    if stop_name == "S3_fib382":
        return sig["fib382"]
    raise ValueError(stop_name)


def target1(sig: dict, stop: float, t1_name: str) -> float:
    risk = sig["entry"] - stop
    if t1_name == "prior_high":
        return sig["impulse_high"]
    if t1_name == "1R":
        return sig["entry"] + risk
    if t1_name == "1p5R":
        return sig["entry"] + 1.5 * risk
    raise ValueError(t1_name)


def target2(sig: dict) -> float:
    # Fib extension target: prior impulse high + 0.618 of impulse height.
    return sig["impulse_high"] + 0.618 * (sig["impulse_high"] - sig["impulse_low"])


def simulate_partial(df: pd.DataFrame, sig: dict, stop: float, t1: float, t2: float,
                     management: str, max_hold: int = 40):
    entry = sig["entry"]
    risk = entry - stop
    if risk <= 0 or t1 <= entry or t2 <= t1:
        return None

    qty1 = 0.5
    qty2 = 0.5
    realized = 0.0
    t1_hit = False
    t2_hit = False
    runner_stop = stop
    outcome = "TIME"
    exit_date = pd.NaT
    end = min(len(df), sig["entry_i"] + max_hold + 1)

    for j in range(sig["entry_i"], end):
        o = float(df["Open"].iloc[j]); h = float(df["High"].iloc[j]); l = float(df["Low"].iloc[j])

        # Conservative ordering on ambiguous daily bars: stop before target.
        active_stop = runner_stop if t1_hit else stop
        if l <= active_stop:
            fill = min(active_stop, o) if j > sig["entry_i"] else active_stop
            if t1_hit:
                realized += qty2 * (fill - entry)
            else:
                realized += (qty1 + qty2) * (fill - entry)
            outcome = "STOP_AFTER_T1" if t1_hit else "STOP"
            exit_date = df.index[j]
            break

        if not t1_hit and h >= t1:
            fill1 = max(t1, o) if o >= t1 else t1
            realized += qty1 * (fill1 - entry)
            t1_hit = True
            if management == "breakeven_after_t1":
                runner_stop = entry
            # If the same bar can also touch T2, count T2 only after T1 once stop ambiguity is cleared.
            if h >= t2:
                fill2 = max(t2, o) if o >= t2 else t2
                realized += qty2 * (fill2 - entry)
                t2_hit = True
                outcome = "T2_SAME_BAR"
                exit_date = df.index[j]
                break
            continue

        if t1_hit and h >= t2:
            fill2 = max(t2, o) if o >= t2 else t2
            realized += qty2 * (fill2 - entry)
            t2_hit = True
            outcome = "T2"
            exit_date = df.index[j]
            break

    if pd.isna(exit_date):
        j = end - 1
        close = float(df["Close"].iloc[j])
        if t1_hit:
            realized += qty2 * (close - entry)
        else:
            realized += (qty1 + qty2) * (close - entry)
        exit_date = df.index[j]
        outcome = "TIME_AFTER_T1" if t1_hit else "TIME"

    return {
        "exit_date": exit_date,
        "outcome": outcome,
        "t1_hit": t1_hit,
        "t2_hit": t2_hit,
        "r_multiple": realized / risk,
        "holding_days": int(df.index.get_loc(exit_date) - sig["entry_i"]),
    }


def metrics(t: pd.DataFrame):
    if t.empty:
        return {"trades": 0}
    r = pd.to_numeric(t["r_multiple"], errors="coerce").dropna()
    wins, losses = r[r > 0], r[r < 0]
    gp, gl = float(wins.sum()), float(-losses.sum())
    ordered = t.sort_values("exit_date")
    eq = ordered["r_multiple"].fillna(0).cumsum()
    dd = eq - eq.cummax()
    return {
        "trades": int(len(t)),
        "win_rate_pct": round(float((r > 0).mean() * 100), 2),
        "avg_r": round(float(r.mean()), 3),
        "median_r": round(float(r.median()), 3),
        "profit_factor_r": round(gp / gl, 3) if gl > 0 else None,
        "max_drawdown_r": round(float(dd.min()), 3),
        "t1_hit_rate_pct": round(float(t["t1_hit"].mean() * 100), 2),
        "t2_hit_rate_pct": round(float(t["t2_hit"].mean() * 100), 2),
        "avg_holding_days": round(float(t["holding_days"].mean()), 2),
        "total_r": round(float(r.sum()), 3),
    }


def main():
    p = argparse.ArgumentParser(description="EMA20 + Fib 0.236 D-signal exit matrix study")
    p.add_argument("--symbols", default="data/us_1b_universe.txt")
    p.add_argument("--period", default="5y")
    p.add_argument("--output-dir", default="ema20_fib_exit_output")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=80)
    p.add_argument("--impulse-lookback", type=int, default=80)
    p.add_argument("--recent-high-days", type=int, default=20)
    a = p.parse_args()

    symbols = load_symbols(a.symbols, a.limit)
    rows = []
    signal_count = 0
    for st in range(0, len(symbols), a.batch_size):
        batch = symbols[st:st + a.batch_size]
        print(f"Downloading {st+1}-{min(st+len(batch),len(symbols))} / {len(symbols)}")
        try:
            data = yf.download(batch, period=a.period, interval="1d", group_by="ticker", auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print("batch failed", e); continue

        for sym in batch:
            try:
                df = (data if len(batch) == 1 else data[sym]).dropna(subset=["Open","High","Low","Close","Volume"]).copy()
                if len(df) < 220:
                    continue
                last_key = None
                for i in range(180, len(df)):
                    imp = find_impulse_before(df, i, a.impulse_lookback, a.recent_high_days)
                    if imp is None:
                        continue
                    sig = get_entry_signal(sym, df, i, imp, last_key)
                    if sig is None:
                        continue
                    last_key = (imp["lo"], imp["hi"])
                    signal_count += 1
                    t2 = target2(sig)
                    for stop_name in STOP_VARIANTS:
                        stop = stop_price(sig, stop_name)
                        if stop >= sig["entry"]:
                            continue
                        for t1_name in T1_VARIANTS:
                            t1 = target1(sig, stop, t1_name)
                            if t1 >= t2:
                                continue
                            for mgmt in MANAGEMENT:
                                res = simulate_partial(df, sig, stop, t1, t2, mgmt, 40)
                                if res is None:
                                    continue
                                rows.append({
                                    **sig,
                                    "stop_variant": stop_name,
                                    "stop": stop,
                                    "t1_variant": t1_name,
                                    "t1": t1,
                                    "t2": t2,
                                    "management": mgmt,
                                    **res,
                                })
            except Exception as e:
                print("skip", sym, e)
        time.sleep(0.35)

    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    if not t.empty:
        for c in ["entry_date", "exit_date"]:
            t[c] = pd.to_datetime(t[c], errors="coerce")
        t = t.sort_values(["entry_date", "symbol", "stop_variant", "t1_variant", "management"]).reset_index(drop=True)
    t.to_csv(out / "exit_matrix_trades.csv", index=False)

    summary = []
    if not t.empty:
        for (sv, tv, mg), g in t.groupby(["stop_variant", "t1_variant", "management"]):
            m = metrics(g)
            m.update({"stop_variant": sv, "t1_variant": tv, "management": mg})
            summary.append(m)
    sdf = pd.DataFrame(summary)
    if not sdf.empty:
        sdf = sdf.sort_values(["profit_factor_r", "avg_r"], ascending=False).reset_index(drop=True)
    sdf.to_csv(out / "exit_matrix_summary.csv", index=False)
    (out / "top_results.json").write_text(json.dumps({
        "signals": signal_count,
        "top_by_profit_factor": sdf.head(10).to_dict("records") if not sdf.empty else [],
        "top_by_avg_r": sdf.sort_values("avg_r", ascending=False).head(10).to_dict("records") if not sdf.empty else [],
    }, indent=2), encoding="utf-8")

    print(f"\nSignals: {signal_count}")
    print("\n=== TOP BY PROFIT FACTOR ===")
    print(sdf.head(10).to_string(index=False) if not sdf.empty else "No results")
    print("\n=== TOP BY AVG R ===")
    print(sdf.sort_values("avg_r", ascending=False).head(10).to_string(index=False) if not sdf.empty else "No results")


if __name__ == "__main__":
    main()
