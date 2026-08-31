from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from ema20_fib0236_exit_study import get_entry_signal, load_symbols, s
from ema20_fib0236_v2_study import find_impulse_before

# Fixed rules from the best exit-matrix result.
STOP_BUFFER = 0.0075  # EMA20 - 0.75%
T1_R = 1.5
MAX_HOLD = 40

T2_VARIANTS = [
    "2R",
    "2p5R",
    "3R",
    "prior_high",
    "ext0382",
    "ext0618",
]


def target2(sig: dict, risk: float, name: str) -> float:
    entry = sig["entry"]
    impulse_height = sig["impulse_high"] - sig["impulse_low"]
    if name == "2R":
        return entry + 2.0 * risk
    if name == "2p5R":
        return entry + 2.5 * risk
    if name == "3R":
        return entry + 3.0 * risk
    if name == "prior_high":
        return sig["impulse_high"]
    if name == "ext0382":
        return sig["impulse_high"] + 0.382 * impulse_height
    if name == "ext0618":
        return sig["impulse_high"] + 0.618 * impulse_height
    raise ValueError(name)


def simulate(df: pd.DataFrame, sig: dict, t2: float):
    entry = sig["entry"]
    stop = sig["ema20"] * (1.0 - STOP_BUFFER)
    risk = entry - stop
    if risk <= 0:
        return None
    t1 = entry + T1_R * risk
    if t2 <= t1:
        return None

    realized = 0.0
    t1_hit = False
    t2_hit = False
    exit_date = pd.NaT
    outcome = "TIME"
    runner_stop = stop
    end = min(len(df), sig["entry_i"] + MAX_HOLD + 1)

    for j in range(sig["entry_i"], end):
        o = float(df["Open"].iloc[j])
        h = float(df["High"].iloc[j])
        l = float(df["Low"].iloc[j])
        active_stop = runner_stop if t1_hit else stop

        # Conservative daily-bar ordering: stop before target on ambiguous bars.
        if l <= active_stop:
            fill = min(active_stop, o) if j > sig["entry_i"] else active_stop
            realized += (0.5 if t1_hit else 1.0) * (fill - entry)
            outcome = "STOP_AFTER_T1" if t1_hit else "STOP"
            exit_date = df.index[j]
            break

        if not t1_hit and h >= t1:
            fill1 = max(t1, o) if o >= t1 else t1
            realized += 0.5 * (fill1 - entry)
            t1_hit = True
            runner_stop = entry  # breakeven after T1
            if h >= t2:
                fill2 = max(t2, o) if o >= t2 else t2
                realized += 0.5 * (fill2 - entry)
                t2_hit = True
                outcome = "T2_SAME_BAR"
                exit_date = df.index[j]
                break
            continue

        if t1_hit and h >= t2:
            fill2 = max(t2, o) if o >= t2 else t2
            realized += 0.5 * (fill2 - entry)
            t2_hit = True
            outcome = "T2"
            exit_date = df.index[j]
            break

    if pd.isna(exit_date):
        j = end - 1
        close = float(df["Close"].iloc[j])
        realized += (0.5 if t1_hit else 1.0) * (close - entry)
        exit_date = df.index[j]
        outcome = "TIME_AFTER_T1" if t1_hit else "TIME"

    return {
        "stop": stop,
        "t1": t1,
        "t2": t2,
        "t1_hit": t1_hit,
        "t2_hit": t2_hit,
        "outcome": outcome,
        "exit_date": exit_date,
        "holding_days": int(df.index.get_loc(exit_date) - sig["entry_i"]),
        "r_multiple": realized / risk,
    }


def metrics(t: pd.DataFrame):
    if t.empty:
        return {"trades": 0}
    r = pd.to_numeric(t["r_multiple"], errors="coerce").dropna()
    wins = r[r > 0]
    losses = r[r < 0]
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
    p = argparse.ArgumentParser(description="Optimize T2 for EMA20 + Fib 0.236 strong-impulse setup")
    p.add_argument("--symbols", default="data/us_1b_universe.txt")
    p.add_argument("--period", default="5y")
    p.add_argument("--output-dir", default="ema20_fib_t2_output")
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
            print("batch failed", e)
            continue

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
                    stop = sig["ema20"] * (1.0 - STOP_BUFFER)
                    risk = sig["entry"] - stop
                    if risk <= 0:
                        continue
                    for name in T2_VARIANTS:
                        t2 = target2(sig, risk, name)
                        res = simulate(df, sig, t2)
                        if res is None:
                            continue
                        rows.append({**sig, "t2_variant": name, **res})
            except Exception as e:
                print("skip", sym, e)
        time.sleep(0.35)

    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    if not t.empty:
        for c in ["entry_date", "exit_date"]:
            t[c] = pd.to_datetime(t[c], errors="coerce")
        t = t.sort_values(["entry_date", "symbol", "t2_variant"]).reset_index(drop=True)
    t.to_csv(out / "t2_trades.csv", index=False)

    summary = []
    yearly = []
    if not t.empty:
        for name, g in t.groupby("t2_variant"):
            m = metrics(g)
            m["t2_variant"] = name
            summary.append(m)
            for year, yg in g.groupby(g.entry_date.dt.year):
                ym = metrics(yg)
                ym.update({"t2_variant": name, "year": int(year)})
                yearly.append(ym)

    sdf = pd.DataFrame(summary)
    if not sdf.empty:
        sdf = sdf.sort_values(["profit_factor_r", "avg_r"], ascending=False).reset_index(drop=True)
    sdf.to_csv(out / "t2_summary.csv", index=False)
    pd.DataFrame(yearly).to_csv(out / "t2_yearly.csv", index=False)
    (out / "top_results.json").write_text(json.dumps({
        "signals": signal_count,
        "fixed_rules": {
            "entry": "EMA20 first clean pullback, D strong impulse signal",
            "stop": "EMA20 - 0.75%",
            "t1": "1.5R, sell 50%",
            "runner_stop_after_t1": "breakeven",
        },
        "results": sdf.to_dict("records") if not sdf.empty else [],
    }, indent=2), encoding="utf-8")

    print(f"\nSignals: {signal_count}")
    print("\n=== T2 OPTIMIZATION ===")
    print(sdf.to_string(index=False) if not sdf.empty else "No results")


if __name__ == "__main__":
    main()
