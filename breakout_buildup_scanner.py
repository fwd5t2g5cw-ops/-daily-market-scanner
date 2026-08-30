from __future__ import annotations

import argparse
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
    return pd.to_numeric(v, errors="coerce").dropna().astype(float)


def linreg_slope(values: pd.Series) -> float:
    s = as_series(values)
    if len(s) < 3:
        return np.nan
    x = np.arange(len(s), dtype=float)
    return float(np.polyfit(x, s.to_numpy(dtype=float), 1)[0])


def load_universe(path: str, limit: int | None = None) -> pd.DataFrame:
    syms = [x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith("#")]
    out = pd.DataFrame({"symbol": syms}).drop_duplicates("symbol")
    return out.head(limit) if limit else out


def count_independent_resistance_tests(high: pd.Series, low: pd.Series, top: float, tol_pct: float,
                                       min_gap: int, min_pullback_pct: float) -> tuple[int, list[int]]:
    """Count distinct tests, not every candle sitting near resistance.

    A test must reach the resistance zone, be separated from the prior test by min_gap bars,
    and between tests price must pull back by at least min_pullback_pct from the top.
    """
    floor = top * (1.0 - tol_pct / 100.0)
    candidates = [i for i, h in enumerate(high.to_numpy()) if h >= floor]
    if not candidates:
        return 0, []

    tests = [candidates[0]]
    for i in candidates[1:]:
        prev = tests[-1]
        if i - prev < min_gap:
            continue
        between_low = float(low.iloc[prev:i + 1].min())
        pullback_pct = (top - between_low) / top * 100.0 if top > 0 else 0.0
        if pullback_pct >= min_pullback_pct:
            tests.append(i)
    return len(tests), tests


def find_impulse(low: pd.Series, high: pd.Series, buildup_start: int, buildup_days: int,
                 lookback: int, early_buildup_days: int) -> tuple[float, float, int, int] | None:
    """Find the most recent impulse that drove price into the current high-area buildup.

    v2 anchor: impulse high is allowed in the few days immediately before OR at the start of
    the buildup, which avoids anchoring Fib to an obsolete lower high. The impulse low is the
    lowest low preceding that anchor within the configured lookback.
    """
    n = len(high)
    hi_start = max(0, buildup_start - 5)
    hi_end = min(n, buildup_start + max(1, early_buildup_days))
    if hi_end <= hi_start:
        return None

    anchor_slice = high.iloc[hi_start:hi_end]
    hi_local = int(np.argmax(anchor_slice.to_numpy()))
    hi_pos = hi_start + hi_local
    impulse_high = float(high.iloc[hi_pos])

    lo_start = max(0, hi_pos - lookback)
    if hi_pos <= lo_start:
        return None
    lo_slice = low.iloc[lo_start:hi_pos]
    if lo_slice.empty:
        return None
    lo_local = int(np.argmin(lo_slice.to_numpy()))
    lo_pos = lo_start + lo_local
    impulse_low = float(low.iloc[lo_pos])

    if impulse_high <= impulse_low:
        return None
    return impulse_low, impulse_high, lo_pos, hi_pos


def analyze(symbol: str, df: pd.DataFrame, args) -> dict | None:
    if df is None or len(df) < args.min_history:
        return None
    df = df.dropna(subset=["Open", "Close", "High", "Low", "Volume"]).copy()
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
    liquid = last_close >= args.min_price and avg_vol20 >= args.min_avg_volume and dollar_vol20 >= args.min_dollar_volume
    if not liquid:
        return None

    lookback = min(args.high_lookback, n)
    hist_high = float(high.iloc[-lookback:].max())
    pct_below_hist_high = (last_close / hist_high - 1.0) * 100.0
    near_historical_high = last_close >= hist_high * (1.0 - args.max_below_high_pct / 100.0)

    b = args.buildup_days
    buildup_start = n - b
    if buildup_start < 10:
        return None

    b_high = high.iloc[-b:]
    b_low = low.iloc[-b:]
    b_vol = volume.iloc[-b:]
    prior_buildup_top = float(high.iloc[-b:-1].max())
    buildup_bottom = float(b_low.min())
    buildup_height = prior_buildup_top - buildup_bottom
    buildup_height_pct = buildup_height / buildup_bottom * 100.0 if buildup_bottom > 0 else np.nan

    # Reject absurdly tiny/noisy and excessively wide "bases" before scoring.
    practical_width = args.min_buildup_width_pct <= buildup_height_pct <= args.max_buildup_width_pct

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

    body = (df["Close"] - df["Open"]).abs().iloc[-b:]
    candle_body_slope = linreg_slope(body)
    candles_shrinking = bool(not np.isnan(candle_body_slope) and candle_body_slope < 0)

    volume_slope = linreg_slope(b_vol)
    volume_contracting = bool(not np.isnan(volume_slope) and volume_slope < 0)

    resistance_touches, touch_indices = count_independent_resistance_tests(
        b_high, b_low, prior_buildup_top, args.touch_tolerance_pct,
        args.min_touch_gap_days, args.min_between_touch_pullback_pct,
    )
    recent_touch = bool(touch_indices and touch_indices[-1] >= b - args.recent_touch_days)
    repeated_tests = resistance_touches >= args.min_resistance_touches and recent_touch

    impulse = find_impulse(low, high, buildup_start, b, args.impulse_lookback, args.early_buildup_anchor_days)
    if impulse is None:
        return None
    impulse_low, impulse_high, impulse_low_pos, impulse_high_pos = impulse
    impulse_height = impulse_high - impulse_low
    fib_0236 = impulse_high - 0.236 * impulse_height
    buildup_above_0236 = buildup_bottom >= fib_0236

    # The current buildup should be associated with the impulse high, not a much lower obsolete high.
    impulse_reaches_buildup = impulse_high >= prior_buildup_top * (1.0 - args.impulse_high_tolerance_pct / 100.0)
    buildup_near_high = prior_buildup_top >= hist_high * (1.0 - args.max_below_high_pct / 100.0)

    breakout_level = prior_buildup_top * (1.0 + args.breakout_buffer_pct / 100.0)
    breakout = last_close > breakout_level
    breakout_rel_vol = float(volume.iloc[-1] / avg_vol20) if avg_vol20 > 0 else np.nan

    mandatory_pass = bool(
        near_historical_high and buildup_near_high and practical_width
        and impulse_reaches_buildup and buildup_above_0236
        and volume_contracting and range_contracting and repeated_tests
    )
    status = "BREAKOUT" if mandatory_pass and breakout else "WATCH" if mandatory_pass else "REJECT"

    entry = prior_buildup_top if mandatory_pass else np.nan
    stop = buildup_bottom if mandatory_pass else np.nan
    risk = entry - stop if mandatory_pass else np.nan
    target1 = entry + 1.5 * risk if mandatory_pass and risk > 0 else np.nan
    target2 = entry + 0.618 * impulse_height if mandatory_pass else np.nan
    rr1 = (target1 - entry) / risk if mandatory_pass and risk > 0 else np.nan
    rr2 = (target2 - entry) / risk if mandatory_pass and risk > 0 else np.nan

    score = sum([
        3 if near_historical_high else 0,
        3 if buildup_above_0236 else 0,
        3 if volume_contracting else 0,
        2 if range_contracting else 0,
        2 if repeated_tests else 0,
        2 if impulse_reaches_buildup else 0,
        1 if candles_shrinking else 0,
        2 if breakout else 0,
    ])

    def rnd(x):
        return round(float(x), 3) if x is not None and not pd.isna(x) else np.nan

    return {
        "symbol": symbol, "status": status, "score": score, "close": rnd(last_close),
        "hist_high": rnd(hist_high), "pct_below_hist_high": rnd(pct_below_hist_high),
        "buildup_days": b, "buildup_top": rnd(prior_buildup_top), "buildup_bottom": rnd(buildup_bottom),
        "buildup_height_pct": rnd(buildup_height_pct), "practical_width": practical_width,
        "resistance_touches": resistance_touches, "range_contracting": range_contracting,
        "candles_shrinking_bonus": candles_shrinking, "volume_contracting": volume_contracting,
        "breakout_rel_volume": rnd(breakout_rel_vol), "impulse_low": rnd(impulse_low),
        "impulse_high": rnd(impulse_high), "impulse_low_pos": impulse_low_pos,
        "impulse_high_pos": impulse_high_pos, "fib_0236": rnd(fib_0236),
        "impulse_reaches_buildup": impulse_reaches_buildup, "buildup_above_0236": buildup_above_0236,
        "near_historical_high": near_historical_high, "mandatory_pass": mandatory_pass,
        "entry": rnd(entry), "stop": rnd(stop), "target1": rnd(target1), "target2": rnd(target2),
        "rr_target1": rnd(rr1), "rr_target2": rnd(rr2),
    }


def scan(universe: pd.DataFrame, args) -> pd.DataFrame:
    symbols = universe["symbol"].tolist()
    rows = []
    for st in range(0, len(symbols), args.batch_size):
        batch = symbols[st:st + args.batch_size]
        print(f"Downloading {st + 1}-{min(st + len(batch), len(symbols))} of {len(symbols)}...")
        try:
            data = yf.download(batch, period=args.period, interval="1d", group_by="ticker", auto_adjust=True, threads=True, progress=False)
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
    out["_status_rank"] = out["status"].map({"BREAKOUT": 2, "WATCH": 1, "REJECT": 0}).fillna(0)
    out = out.sort_values(["_status_rank", "score", "pct_below_hist_high", "rr_target2"], ascending=[False, False, False, False])
    return out.drop(columns=["_status_rank"]).reset_index(drop=True)


def main():
    p = argparse.ArgumentParser(description="Breakout Buildup Playbook scanner v2")
    p.add_argument("--symbols", required=True)
    p.add_argument("--output", default="breakout_buildup_results.csv")
    p.add_argument("--limit", type=int)
    p.add_argument("--period", default="2y")
    p.add_argument("--batch-size", type=int, default=100)
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
    args = p.parse_args()

    universe = load_universe(args.symbols, args.limit)
    out = scan(universe, args)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)
    actionable = out[out["status"].isin(["BREAKOUT", "WATCH"])].copy() if not out.empty else out
    print("\n=== BREAKOUT BUILDUP PLAYBOOK V2 ===")
    if actionable.empty:
        print("(no qualifying setups)")
    else:
        cols = ["symbol", "status", "score", "close", "pct_below_hist_high", "buildup_top", "buildup_bottom",
                "buildup_height_pct", "resistance_touches", "impulse_low", "impulse_high", "fib_0236",
                "entry", "stop", "target1", "target2", "rr_target1", "rr_target2"]
        print(actionable[cols].head(30).to_string(index=False))
    print(f"\nSaved: {args.output}")


if __name__ == "__main__":
    main()
