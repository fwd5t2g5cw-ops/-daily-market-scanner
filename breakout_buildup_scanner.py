from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


# Standalone implementation of the uploaded Breakout Trading Playbook.
# Source rules kept intact:
#   1) Buildup forms near a historical high.
#   2) Buildup stays above the prior impulse's 0.236 retracement.
#   3) Volume generally contracts during the buildup.
#   4) Entry = breakout above buildup top.
#   5) Stop = buildup bottom.
#   6) Target 1 = entry + 1.5 * buildup height.
#   7) Target 2 = entry + 0.618 * prior impulse height.
#
# The source document does not define exact machine-detection windows/tolerances.
# Those are therefore explicit, configurable v1 assumptions below rather than
# being silently presented as rules from the document.


def as_series(v):
    if isinstance(v, pd.DataFrame):
        if v.shape[1] == 0:
            return pd.Series(dtype=float)
        v = v.iloc[:, 0]
    return pd.to_numeric(v, errors="coerce").dropna().astype(float)


def linreg_slope(values: pd.Series) -> float:
    s = as_series(values)
    if len(s) < 3:
        return np.nan
    x = np.arange(len(s), dtype=float)
    return float(np.polyfit(x, s.to_numpy(dtype=float), 1)[0])


def load_universe(path: str, limit: int | None = None) -> pd.DataFrame:
    syms = [
        x.strip().upper()
        for x in Path(path).read_text().splitlines()
        if x.strip() and not x.startswith("#")
    ]
    out = pd.DataFrame({"symbol": syms}).drop_duplicates("symbol")
    return out.head(limit) if limit else out


def analyze(symbol: str, df: pd.DataFrame, args) -> dict | None:
    if df is None or len(df) < args.min_history:
        return None

    df = df.dropna(subset=["Close", "High", "Low", "Volume"]).copy()
    if len(df) < args.min_history:
        return None

    close = as_series(df["Close"])
    high = as_series(df["High"])
    low = as_series(df["Low"])
    volume = as_series(df["Volume"])
    if min(len(close), len(high), len(low), len(volume)) < args.min_history:
        return None

    n = len(close)
    last_close = float(close.iloc[-1])
    avg_vol20 = float(volume.rolling(20).mean().iloc[-1])
    dollar_vol20 = last_close * avg_vol20

    liquid = (
        last_close >= args.min_price
        and avg_vol20 >= args.min_avg_volume
        and dollar_vol20 >= args.min_dollar_volume
    )
    if not liquid:
        return None

    # --- Historical-high context ---
    lookback = min(args.high_lookback, n)
    hist_high = float(high.iloc[-lookback:].max())
    pct_below_hist_high = (last_close / hist_high - 1.0) * 100.0
    near_historical_high = last_close >= hist_high * (1.0 - args.max_below_high_pct / 100.0)

    # --- Buildup window ---
    b = args.buildup_days
    if n < max(args.min_history, b + args.impulse_lookback + 5):
        return None

    b_high = high.iloc[-b:]
    b_low = low.iloc[-b:]
    b_close = close.iloc[-b:]
    b_vol = volume.iloc[-b:]

    buildup_top = float(b_high.max())
    buildup_bottom = float(b_low.min())
    buildup_height = buildup_top - buildup_bottom
    buildup_height_pct = (buildup_height / buildup_bottom * 100.0) if buildup_bottom > 0 else np.nan

    # Mechanical v1 contraction test: second half has a smaller price range than first half,
    # and the last quarter is smaller still. This operationalizes "range gradually narrows".
    half = max(2, b // 2)
    q = max(2, b // 4)
    first_half_range = float(b_high.iloc[:half].max() - b_low.iloc[:half].min())
    second_half_range = float(b_high.iloc[-half:].max() - b_low.iloc[-half:].min())
    last_quarter_range = float(b_high.iloc[-q:].max() - b_low.iloc[-q:].min())
    range_contracting = (
        first_half_range > 0
        and second_half_range <= first_half_range * args.range_contract_ratio
        and last_quarter_range <= second_half_range * args.last_quarter_ratio
    )

    # Candle bodies should generally get smaller (bonus point in the document).
    body = (df["Close"] - df["Open"]).abs().iloc[-b:]
    candle_body_slope = linreg_slope(body)
    candles_shrinking = bool(not np.isnan(candle_body_slope) and candle_body_slope < 0)

    # Volume should generally trend down through the buildup.
    volume_slope = linreg_slope(b_vol)
    volume_contracting = bool(not np.isnan(volume_slope) and volume_slope < 0)

    # More frequent tests of resistance: count highs within tolerance of buildup top,
    # and require at least one recent touch.
    touch_floor = buildup_top * (1.0 - args.touch_tolerance_pct / 100.0)
    resistance_touches = int((b_high >= touch_floor).sum())
    recent_touch = bool((b_high.iloc[-args.recent_touch_days:] >= touch_floor).any())
    repeated_tests = resistance_touches >= args.min_resistance_touches and recent_touch

    # --- Prior impulse and Fib 0.236 ---
    # v1 assumption: impulse high is the highest high immediately before the buildup;
    # impulse low is the lowest low within a configurable lookback ending at that high.
    pre = n - b
    start = max(0, pre - args.impulse_lookback)
    pre_high = high.iloc[start:pre]
    if pre_high.empty:
        return None

    impulse_high_pos_local = int(np.argmax(pre_high.to_numpy()))
    impulse_high_pos = start + impulse_high_pos_local
    impulse_high = float(high.iloc[impulse_high_pos])

    low_start = max(0, impulse_high_pos - args.impulse_lookback)
    impulse_low_slice = low.iloc[low_start:impulse_high_pos + 1]
    if impulse_low_slice.empty:
        return None
    impulse_low = float(impulse_low_slice.min())
    impulse_height = impulse_high - impulse_low
    if impulse_height <= 0:
        return None

    fib_0236 = impulse_high - 0.236 * impulse_height
    buildup_above_0236 = buildup_bottom >= fib_0236

    # "Buildup near historical high" is checked against both the historical high context
    # and the buildup top itself.
    buildup_near_high = buildup_top >= hist_high * (1.0 - args.max_below_high_pct / 100.0)

    # Breakout: today's close above the PREVIOUS buildup resistance, optionally with a small buffer.
    prior_buildup_top = float(high.iloc[-b:-1].max())
    breakout_level = prior_buildup_top * (1.0 + args.breakout_buffer_pct / 100.0)
    breakout = last_close > breakout_level

    # Keep volume contraction as the core source rule. Breakout volume is reported but not mandatory,
    # because the uploaded document does not state a mandatory breakout-volume threshold.
    breakout_rel_vol = float(volume.iloc[-1] / avg_vol20) if avg_vol20 > 0 else np.nan

    mandatory_pass = bool(
        near_historical_high
        and buildup_near_high
        and buildup_above_0236
        and volume_contracting
        and range_contracting
        and repeated_tests
    )

    status = "BREAKOUT" if mandatory_pass and breakout else "WATCH" if mandatory_pass else "REJECT"

    entry = prior_buildup_top if mandatory_pass else np.nan
    stop = buildup_bottom if mandatory_pass else np.nan
    risk = entry - stop if mandatory_pass else np.nan
    target1 = entry + 1.5 * (entry - stop) if mandatory_pass and risk > 0 else np.nan
    target2 = entry + 0.618 * impulse_height if mandatory_pass else np.nan
    rr1 = (target1 - entry) / risk if mandatory_pass and risk > 0 else np.nan
    rr2 = (target2 - entry) / risk if mandatory_pass and risk > 0 else np.nan

    score = 0
    score += 3 if near_historical_high else 0
    score += 3 if buildup_above_0236 else 0
    score += 3 if volume_contracting else 0
    score += 2 if range_contracting else 0
    score += 2 if repeated_tests else 0
    score += 1 if candles_shrinking else 0
    score += 2 if breakout else 0

    def rnd(x):
        return round(float(x), 3) if x is not None and not pd.isna(x) else np.nan

    return {
        "symbol": symbol,
        "status": status,
        "score": score,
        "close": rnd(last_close),
        "hist_high": rnd(hist_high),
        "pct_below_hist_high": rnd(pct_below_hist_high),
        "buildup_days": b,
        "buildup_top": rnd(prior_buildup_top),
        "buildup_bottom": rnd(buildup_bottom),
        "buildup_height_pct": rnd(buildup_height_pct),
        "resistance_touches": resistance_touches,
        "range_contracting": range_contracting,
        "candles_shrinking_bonus": candles_shrinking,
        "volume_contracting": volume_contracting,
        "breakout_rel_volume": rnd(breakout_rel_vol),
        "impulse_low": rnd(impulse_low),
        "impulse_high": rnd(impulse_high),
        "fib_0236": rnd(fib_0236),
        "buildup_above_0236": buildup_above_0236,
        "near_historical_high": near_historical_high,
        "mandatory_pass": mandatory_pass,
        "entry": rnd(entry),
        "stop": rnd(stop),
        "target1": rnd(target1),
        "target2": rnd(target2),
        "rr_target1": rnd(rr1),
        "rr_target2": rnd(rr2),
    }


def scan(universe: pd.DataFrame, args) -> pd.DataFrame:
    symbols = universe["symbol"].tolist()
    rows: list[dict] = []

    for st in range(0, len(symbols), args.batch_size):
        batch = symbols[st:st + args.batch_size]
        print(f"Downloading {st + 1}-{min(st + len(batch), len(symbols))} of {len(symbols)}...")
        try:
            data = yf.download(
                batch,
                period=args.period,
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                threads=True,
                progress=False,
            )
        except Exception as exc:
            print("Batch failed:", exc)
            continue

        for symbol in batch:
            try:
                sdf = data if len(batch) == 1 else data[symbol]
                row = analyze(symbol, sdf, args)
                if row:
                    rows.append(row)
            except Exception as exc:
                print("Skipping", symbol, exc)
        time.sleep(0.4)

    if not rows:
        return pd.DataFrame()

    out = pd.DataFrame(rows)
    status_rank = out["status"].map({"BREAKOUT": 2, "WATCH": 1, "REJECT": 0}).fillna(0)
    out["_status_rank"] = status_rank
    out = out.sort_values(
        ["_status_rank", "score", "pct_below_hist_high", "rr_target1"],
        ascending=[False, False, False, False],
    ).drop(columns=["_status_rank"])
    return out.reset_index(drop=True)


def main():
    p = argparse.ArgumentParser(description="Standalone Breakout Buildup Playbook scanner")
    p.add_argument("--symbols", required=True, help="Text file containing one Yahoo Finance symbol per line")
    p.add_argument("--output", default="breakout_buildup_results.csv")
    p.add_argument("--limit", type=int)
    p.add_argument("--period", default="2y")
    p.add_argument("--batch-size", type=int, default=100)

    # Explicit v1 machine-detection assumptions.
    p.add_argument("--min-history", type=int, default=180)
    p.add_argument("--high-lookback", type=int, default=252)
    p.add_argument("--max-below-high-pct", type=float, default=5.0)
    p.add_argument("--buildup-days", type=int, default=15)
    p.add_argument("--impulse-lookback", type=int, default=80)
    p.add_argument("--range-contract-ratio", type=float, default=0.85)
    p.add_argument("--last-quarter-ratio", type=float, default=0.90)
    p.add_argument("--touch-tolerance-pct", type=float, default=1.5)
    p.add_argument("--min-resistance-touches", type=int, default=3)
    p.add_argument("--recent-touch-days", type=int, default=5)
    p.add_argument("--breakout-buffer-pct", type=float, default=0.0)

    # Basic liquidity filters; not part of the document, only for practical scanning.
    p.add_argument("--min-price", type=float, default=5.0)
    p.add_argument("--min-avg-volume", type=float, default=200000)
    p.add_argument("--min-dollar-volume", type=float, default=5000000)

    args = p.parse_args()

    universe = load_universe(args.symbols, args.limit)
    out = scan(universe, args)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)

    actionable = out[out["status"].isin(["BREAKOUT", "WATCH"])].copy() if not out.empty else out
    print("\n=== BREAKOUT BUILDUP PLAYBOOK ===")
    if actionable.empty:
        print("(no qualifying setups)")
    else:
        cols = [
            "symbol", "status", "score", "close", "pct_below_hist_high",
            "buildup_top", "buildup_bottom", "fib_0236", "resistance_touches",
            "volume_contracting", "range_contracting", "candles_shrinking_bonus",
            "entry", "stop", "target1", "target2", "rr_target1", "rr_target2",
        ]
        print(actionable[cols].head(30).to_string(index=False))

    print(f"\nSaved: {args.output}")


if __name__ == "__main__":
    main()
