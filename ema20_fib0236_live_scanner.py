from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def s(x):
    if isinstance(x, pd.DataFrame):
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").astype(float)


def load_symbols(path: str) -> list[str]:
    xs = [x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith("#")]
    return list(dict.fromkeys(xs))


def find_impulse_before(df: pd.DataFrame, i: int, impulse_lookback: int = 80, recent_high_days: int = 20):
    hist = df.iloc[:i]
    if len(hist) < 100:
        return None
    high, low, close = map(s, [hist["High"], hist["Low"], hist["Close"]])
    recent_n = min(recent_high_days, len(hist))
    recent = high.iloc[-recent_n:]
    hi = len(hist) - recent_n + int(np.argmax(recent.to_numpy()))
    if hi >= len(hist) - 1:
        return None
    lo_start = max(0, hi - impulse_lookback)
    if hi <= lo_start:
        return None
    lo_slice = low.iloc[lo_start:hi]
    lo = lo_start + int(np.argmin(lo_slice.to_numpy()))
    impulse_low = float(low.iloc[lo])
    impulse_high = float(high.iloc[hi])
    if impulse_high <= impulse_low:
        return None
    impulse_pct = (impulse_high / impulse_low - 1.0) * 100.0
    fib236 = impulse_high - 0.236 * (impulse_high - impulse_low)
    fib382 = impulse_high - 0.382 * (impulse_high - impulse_low)
    high52 = float(high.iloc[-min(252, len(hist)):].max())
    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    return {
        "lo": lo, "hi": hi, "low": impulse_low, "high": impulse_high,
        "impulse_pct": impulse_pct, "fib236": fib236, "fib382": fib382,
        "high52": high52, "ema20": ema20,
    }


def gap_tag(df: pd.DataFrame, lo: int, hi: int, impulse_height: float):
    if hi <= lo or impulse_height <= 0:
        return 0.0, np.nan, False
    op, cl = s(df["Open"]), s(df["Close"])
    best, best_j = 0.0, None
    for j in range(lo + 1, hi + 1):
        g = float(op.iloc[j] - cl.iloc[j - 1])
        if g > best:
            best, best_j = g, j
    if best_j is None:
        return 0.0, np.nan, False
    share = best / impulse_height
    pos = (best_j - lo) / max(1, hi - lo)
    return float(share), float(pos), bool(share >= 0.35 and pos <= 0.60)


def analyze_latest(symbol: str, df: pd.DataFrame):
    if len(df) < 220:
        return None
    i = len(df) - 1
    imp = find_impulse_before(df, i)
    if imp is None:
        return None

    # September production setup: D strong impulse.
    if imp["impulse_pct"] < 20.0:
        return None
    if imp["high"] < imp["high52"] * 0.97:
        return None

    fib236, fib382, ema20 = imp["fib236"], imp["fib382"], imp["ema20"]
    confluence = abs(ema20 - fib236) / fib236 * 100.0
    if confluence > 0.50:
        return None

    pull = df.iloc[imp["hi"] + 1:i]
    if pull.empty:
        return None
    pre_low = s(pull["Low"])
    pull_low = float(pre_low.min())
    allowed_floor = fib236 * 0.995
    if pull_low < allowed_floor or pull_low <= fib382:
        return None

    # First clean pullback only: EMA20 must not already have been touched before today.
    if (pre_low <= ema20).any():
        return None

    o = float(df["Open"].iloc[i])
    h = float(df["High"].iloc[i])
    l = float(df["Low"].iloc[i])
    c = float(df["Close"].iloc[i])

    # Important bug fix vs research v2: entry/current day may NOT undercut allowed Fib .236 floor.
    if l < allowed_floor or l <= fib382:
        return None

    dist_to_ema_pct = (c / ema20 - 1.0) * 100.0
    touched = l <= ema20 <= h or o <= ema20
    reclaimed = touched and c > ema20
    bullish_confirm = reclaimed and c > o

    if bullish_confirm:
        status = "DAILY_RECLAIM_CONFIRM"
    elif reclaimed:
        status = "RECLAIM_WAIT_CONFIRM"
    elif touched:
        status = "TOUCH_WAIT_CONFIRM"
    elif 0.0 < dist_to_ema_pct <= 1.50:
        status = "APPROACHING"
    else:
        return None

    stop = ema20 * 0.9925
    # Planning reference only. Actual entry is after confirmation, so T1/T2 must be recalculated from fill.
    ref_entry = c
    risk = ref_entry - stop
    t1 = ref_entry + 1.5 * risk if risk > 0 else np.nan
    t2 = ref_entry + 2.0 * risk if risk > 0 else np.nan
    gap_share, gap_pos, gap_dom = gap_tag(df, imp["lo"], imp["hi"], imp["high"] - imp["low"])

    return {
        "symbol": symbol,
        "status": status,
        "close": round(c, 4),
        "ema20": round(ema20, 4),
        "fib_0236": round(fib236, 4),
        "fib_0382": round(fib382, 4),
        "ema_fib_distance_pct": round(confluence, 3),
        "distance_close_to_ema20_pct": round(dist_to_ema_pct, 3),
        "impulse_low": round(imp["low"], 4),
        "impulse_high": round(imp["high"], 4),
        "impulse_pct": round(imp["impulse_pct"], 2),
        "pullback_low_before_today": round(pull_low, 4),
        "allowed_floor_0236_minus_0_5pct": round(allowed_floor, 4),
        "stop_ema20_minus_0_75pct": round(stop, 4),
        "reference_t1_1_5r": round(t1, 4) if pd.notna(t1) else np.nan,
        "reference_t2_2r": round(t2, 4) if pd.notna(t2) else np.nan,
        "gap_share": round(gap_share, 3),
        "gap_position": round(gap_pos, 3) if pd.notna(gap_pos) else np.nan,
        "gap_dominated_warning": gap_dom,
        "note": "Do not auto-buy on touch; wait for confirmation. Recalculate R targets from actual fill.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--period", default="2y")
    ap.add_argument("--batch-size", type=int, default=80)
    a = ap.parse_args()

    symbols = load_symbols(a.symbols)
    rows = []
    for st in range(0, len(symbols), a.batch_size):
        batch = symbols[st:st + a.batch_size]
        print(f"Downloading {st+1}-{min(st+len(batch),len(symbols))} of {len(symbols)}")
        try:
            data = yf.download(batch, period=a.period, interval="1d", group_by="ticker", auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print("batch failed", e)
            continue
        for sym in batch:
            try:
                df = (data if len(batch) == 1 else data[sym]).dropna(subset=["Open","High","Low","Close","Volume"]).copy()
                r = analyze_latest(sym, df)
                if r:
                    rows.append(r)
            except Exception as e:
                print("skip", sym, e)

    out = pd.DataFrame(rows)
    if not out.empty:
        rank = {"DAILY_RECLAIM_CONFIRM": 0, "RECLAIM_WAIT_CONFIRM": 1, "TOUCH_WAIT_CONFIRM": 2, "APPROACHING": 3}
        out["_rank"] = out["status"].map(rank).fillna(9)
        out = out.sort_values(["_rank", "ema_fib_distance_pct", "distance_close_to_ema20_pct"]).drop(columns=["_rank"])
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(a.output, index=False)
    print("\n=== EMA20 + FIB 0.236 LIVE SCANNER ===")
    print(out.head(50).to_string(index=False) if not out.empty else "(none)")
    print(f"\nCandidates: {len(out)}")
    print(f"Saved: {a.output}")


if __name__ == "__main__":
    main()
