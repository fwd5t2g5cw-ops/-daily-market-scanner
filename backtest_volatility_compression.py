"""Event study for the direction-neutral volatility-compression model.

Signals are the first COILED/COMPRESSED bar in each episode (with a 20-session
cooldown). Outcomes measure subsequent volatility expansion and both breakout
directions. Matched controls are non-compressed days in the same symbol/year.
This is a descriptive event study, not a strategy or a buy/sell recommendation.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from volatility_compression_scanner import (
    ScannerConfig,
    _prepare_frame,
    _true_range,
    _wilder_atr,
    fetch_alpaca,
    fetch_yahoo,
    load_symbols,
)


HORIZONS = (5, 10, 20)
CONTROL_SEED = 20260930
SIGNAL_COOLDOWN = 20


def _rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    """Percentile rank of each value against its trailing window, including it."""

    def rank_latest(values: np.ndarray) -> float:
        latest = values[-1]
        valid = np.isfinite(values)
        if not np.isfinite(latest) or not valid.any():
            return np.nan
        return float(np.count_nonzero(values[valid] <= latest) / valid.sum() * 100)

    return series.rolling(window, min_periods=1).apply(rank_latest, raw=True)


def compression_series(
    frame: pd.DataFrame, config: ScannerConfig | None = None
) -> pd.DataFrame:
    """Calculate the scanner's daily score/state without using future bars."""
    cfg = config or ScannerConfig()
    data = _prepare_frame(frame)
    if len(data) < cfg.min_bars:
        return pd.DataFrame(index=data.index)

    close = data["close"]
    log_return = np.log(close / close.shift(1))
    hv20 = log_return.rolling(20).std(ddof=1) * np.sqrt(252) * 100
    tr = _true_range(data)
    atr_pct = _wilder_atr(data, 14) / close * 100

    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std(ddof=0)
    bb_width = ((sma20 + 2 * std20) - (sma20 - 2 * std20)) / sma20 * 100
    sma5 = close.rolling(5).mean()
    sma10 = close.rolling(10).mean()
    sma_spread = (
        (pd.concat([sma5, sma10, sma20], axis=1).max(axis=1)
        - pd.concat([sma5, sma10, sma20], axis=1).min(axis=1))
        / close
        * 100
    )
    coil_width = (data["high"].rolling(10).max() - data["low"].rolling(10).min()) / close * 100

    rank_window = cfg.percentile_window
    ranks = pd.DataFrame(
        {
            "hv20_pctile": _rolling_percentile(hv20, rank_window),
            "atr14_pctile": _rolling_percentile(atr_pct, rank_window),
            "bb_width_pctile": _rolling_percentile(bb_width, rank_window),
            "sma_spread_pctile": _rolling_percentile(sma_spread, rank_window),
            "coil_width_pctile": _rolling_percentile(coil_width, rank_window),
        },
        index=data.index,
    )

    tr_ratio = tr.rolling(5).mean() / tr.rolling(20).mean().replace(0, np.nan)
    volume_ratio = data["volume"].rolling(5).mean() / data["volume"].rolling(20).mean().replace(0, np.nan)
    tr_contracting = tr_ratio <= 0.75
    volume_contracting = volume_ratio <= 0.75
    nr7 = tr <= tr.rolling(7).min()

    weights = {
        "hv20_pctile": 0.20,
        "atr14_pctile": 0.20,
        "bb_width_pctile": 0.20,
        "sma_spread_pctile": 0.15,
        "coil_width_pctile": 0.15,
    }
    score = sum((100 - ranks[name]).clip(lower=0) * weight for name, weight in weights.items())
    score += tr_contracting.astype(float) * 5
    score += volume_contracting.fillna(False).astype(float) * 3
    score += nr7.fillna(False).astype(float) * 2
    score = score.clip(0, 100)

    tight25 = (ranks <= 25).sum(axis=1)
    tight35 = (ranks <= 35).sum(axis=1)
    state = pd.Series("LOOSE", index=data.index, dtype="object")
    state.loc[score >= 40] = "TIGHTENING"
    state.loc[(score >= 60) & (tight35 >= 2)] = "COMPRESSED"
    state.loc[(score >= 75) & (tight25 >= 3)] = "COILED"

    # The initial period is excluded exactly as it is in today's scanner.
    valid = pd.Series(False, index=data.index)
    valid.iloc[cfg.min_bars - 1 :] = True
    state.loc[~valid] = "INSUFFICIENT_HISTORY"

    result = ranks.copy()
    result["score"] = score.round(2)
    result["state"] = state
    result["hv20_pct"] = hv20
    result["atr14_pct"] = atr_pct
    result["true_range"] = tr
    result["prior20_tr_mean"] = tr.rolling(20).mean()
    result["prior10_high"] = data["high"].shift(1).rolling(10).max()
    result["prior10_low"] = data["low"].shift(1).rolling(10).min()
    result["tr_contracting"] = tr_contracting
    result["volume_contracting"] = volume_contracting
    result["nr7"] = nr7
    result["close"] = close
    result["high"] = data["high"]
    result["low"] = data["low"]
    result["log_return"] = log_return
    return result


def _outcome_row(
    symbol: str,
    date: pd.Timestamp,
    position: int,
    frame: pd.DataFrame,
    features: pd.DataFrame,
    horizon: int,
    cohort: str,
    signal_state: str,
    pair_id: str,
) -> dict[str, object]:
    future = frame.iloc[position + 1 : position + horizon + 1]
    feature = features.iloc[position]
    prior_and_future_close = pd.concat(
        [frame["close"].iloc[[position]], future["close"]]
    )
    fwd_vol = np.log(prior_and_future_close / prior_and_future_close.shift(1)).dropna()
    annualized_forward_vol = (
        float(fwd_vol.std(ddof=1) * np.sqrt(252) * 100) if len(fwd_vol) >= 2 else np.nan
    )
    baseline_vol = float(feature["hv20_pct"])
    vol_ratio = (
        annualized_forward_vol / baseline_vol
        if np.isfinite(annualized_forward_vol) and baseline_vol > 0
        else np.nan
    )
    prior_tr = float(feature["prior20_tr_mean"])
    forward_mean_tr = float(_true_range(future).mean())
    tr_ratio = forward_mean_tr / prior_tr if prior_tr > 0 else np.nan

    initial_close = float(frame["close"].iloc[position])
    forward_close = float(future["close"].iloc[-1])
    prior_high = float(feature["prior10_high"])
    prior_low = float(feature["prior10_low"])
    upside = (float(future["high"].max()) / initial_close - 1) * 100
    downside = (float(future["low"].min()) / initial_close - 1) * 100

    return {
        "symbol": symbol,
        "signal_date": date.date().isoformat(),
        "cohort": cohort,
        "signal_state": signal_state,
        "score": round(float(feature["score"]), 2),
        "horizon_sessions": horizon,
        "forward_vol_pct_annualized": round(annualized_forward_vol, 3),
        "forward_vol_ratio_vs_prior_hv20": round(vol_ratio, 3),
        "vol_expanded_1_5x": bool(vol_ratio >= 1.5) if np.isfinite(vol_ratio) else False,
        "forward_mean_tr_ratio_vs_prior20": round(tr_ratio, 3),
        "range_expanded_1_5x": bool(tr_ratio >= 1.5) if np.isfinite(tr_ratio) else False,
        "up_close_break_prior10": bool((future["close"] > prior_high).any()),
        "down_close_break_prior10": bool((future["close"] < prior_low).any()),
        "forward_close_return_pct": round((forward_close / initial_close - 1) * 100, 3),
        "max_up_excursion_pct": round(upside, 3),
        "max_down_excursion_pct": round(downside, 3),
        "pair_id": pair_id,
    }


def _collect_events(
    symbol: str,
    frame: pd.DataFrame,
    features: pd.DataFrame,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    if features.empty:
        return []
    state = features["state"]
    is_compressed = state.isin(["COILED", "COMPRESSED"])
    first_in_episode = is_compressed & ~is_compressed.shift(1, fill_value=False)
    positions = np.flatnonzero(first_in_episode.to_numpy())
    valid_control_positions = np.flatnonzero(
        (~is_compressed & state.isin(["LOOSE", "TIGHTENING"])).to_numpy()
    )
    dates = frame.index
    out: list[dict[str, object]] = []
    used_controls: set[int] = set()
    last_signal = -SIGNAL_COOLDOWN
    for position in positions:
        if position + max(HORIZONS) >= len(frame) or position - last_signal < SIGNAL_COOLDOWN:
            continue
        last_signal = int(position)
        signal_state = str(state.iloc[position])
        year = dates[position].year
        candidates = [
            int(control_pos)
            for control_pos in valid_control_positions
            if dates[control_pos].year == year
            and control_pos + max(HORIZONS) < len(frame)
            and abs(int(control_pos) - int(position)) >= SIGNAL_COOLDOWN
            and int(control_pos) not in used_controls
        ]
        control_position = (
            int(rng.choice(candidates)) if candidates else None
        )
        if control_position is not None:
            used_controls.add(control_position)

        pair_id = f"{symbol}:{dates[position].date().isoformat()}"
        for horizon in HORIZONS:
            out.append(
                _outcome_row(
                    symbol,
                    dates[position],
                    int(position),
                    frame,
                    features,
                    horizon,
                    "COMPRESSION",
                    signal_state,
                    pair_id,
                )
            )
            if control_position is not None:
                out.append(
                    _outcome_row(
                        symbol,
                        dates[control_position],
                        control_position,
                        frame,
                        features,
                        horizon,
                        "MATCHED_CONTROL",
                        "NON_COMPRESSED",
                        pair_id,
                    )
                )
    return out


def summarize_events(events: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "cohort",
        "signal_state",
        "horizon_sessions",
        "samples",
        "vol_expanded_1_5x_pct",
        "range_expanded_1_5x_pct",
        "up_close_break_pct",
        "down_close_break_pct",
        "both_directions_pct",
        "median_forward_vol_ratio",
        "median_forward_tr_ratio",
        "median_max_up_excursion_pct",
        "median_max_down_excursion_pct",
        "median_forward_return_pct",
    ]
    if events.empty:
        return pd.DataFrame(columns=columns)

    def summarize(group: pd.DataFrame) -> pd.Series:
        return pd.Series(
            {
                "samples": len(group),
                "vol_expanded_1_5x_pct": group["vol_expanded_1_5x"].mean() * 100,
                "range_expanded_1_5x_pct": group["range_expanded_1_5x"].mean() * 100,
                "up_close_break_pct": group["up_close_break_prior10"].mean() * 100,
                "down_close_break_pct": group["down_close_break_prior10"].mean() * 100,
                "both_directions_pct": (
                    group["up_close_break_prior10"] & group["down_close_break_prior10"]
                ).mean() * 100,
                "median_forward_vol_ratio": group[
                    "forward_vol_ratio_vs_prior_hv20"
                ].median(),
                "median_forward_tr_ratio": group[
                    "forward_mean_tr_ratio_vs_prior20"
                ].median(),
                "median_max_up_excursion_pct": group["max_up_excursion_pct"].median(),
                "median_max_down_excursion_pct": group["max_down_excursion_pct"].median(),
                "median_forward_return_pct": group["forward_close_return_pct"].median(),
            }
        )

    result = events.groupby(
        ["cohort", "signal_state", "horizon_sessions"], dropna=False
    ).apply(summarize, include_groups=False).reset_index()
    result["samples"] = result["samples"].astype(int)
    for column in columns[4:]:
        result[column] = result[column].round(2)
    return result.reindex(columns=columns)


def run_backtest(
    frames: dict[str, pd.DataFrame],
    symbols: list[str],
    provider: str,
    outdir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    rng = np.random.default_rng(CONTROL_SEED)
    rows: list[dict[str, object]] = []
    found: set[str] = set()
    for symbol in symbols:
        frame = frames.get(symbol)
        if frame is None or frame.empty:
            continue
        clean = _prepare_frame(frame)
        if len(clean) < 160 + max(HORIZONS):
            continue
        features = compression_series(clean)
        rows.extend(_collect_events(symbol, clean, features, rng))
        found.add(symbol)

    events = pd.DataFrame(rows)
    summary = summarize_events(events)
    outdir.mkdir(parents=True, exist_ok=True)
    events.to_csv(outdir / "events.csv", index=False)
    summary.to_csv(outdir / "summary.csv", index=False)
    metadata = {
        "provider": provider,
        "requested_symbols": len(symbols),
        "symbols_with_history": len(found),
        "signal_events": int(
            events.loc[events["cohort"] == "COMPRESSION", "pair_id"].nunique()
        )
        if not events.empty
        else 0,
        "matched_controls": int(
            events.loc[events["cohort"] == "MATCHED_CONTROL", "pair_id"].nunique()
        )
        if not events.empty
        else 0,
        "generated_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "method": {
            "signal": "first COILED/COMPRESSED bar in a compression episode",
            "cooldown_sessions": SIGNAL_COOLDOWN,
            "horizons_sessions": list(HORIZONS),
            "control": "one randomly selected non-compressed date per signal, matched by symbol and calendar year when available",
            "volatility_expansion": "forward annualized realized volatility >= 1.5x prior HV20",
            "range_expansion": "forward mean true range >= 1.5x prior 20-session mean true range",
            "direction": "up and down closing breaks beyond the signal-date prior 10-session range are reported separately",
        },
        "limitations": [
            "descriptive event study; overlapping outcome windows and repeated symbols mean observations are not fully independent",
            "current universe creates survivorship bias for historical results",
            "historical Yahoo data are auto-adjusted and may be rate-limited",
            "matched non-compressed controls are not a randomized causal experiment",
        ],
    }
    (outdir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return events, summary, metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", type=Path, default=Path("data/us_1b_universe.txt"))
    parser.add_argument("--outdir", type=Path, default=Path("volatility_compression_backtest"))
    parser.add_argument("--provider", choices=["auto", "alpaca", "yahoo"], default="auto")
    parser.add_argument("--feed", default="sip")
    parser.add_argument("--limit", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    symbols = load_symbols(args.symbols, args.limit)
    key = os.getenv("ALPACA_API_KEY_ID")
    secret = os.getenv("ALPACA_API_SECRET_KEY")
    provider = args.provider
    if provider == "auto":
        provider = "alpaca" if key and secret else "yahoo"
    requested = list(dict.fromkeys([*symbols, "SPY"]))
    if provider == "alpaca":
        if not key or not secret:
            raise SystemExit("Alpaca requires ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY")
        frames = fetch_alpaca(requested, key, secret, args.feed)
    else:
        frames = fetch_yahoo(requested)
    found = set(symbols).intersection(frames)
    coverage = len(found) / len(symbols) if symbols else 0
    if coverage < 0.80:
        raise SystemExit(f"historical coverage {coverage:.1%} is below 80%; refusing to publish")
    events, summary, metadata = run_backtest(frames, symbols, provider, args.outdir)
    print(
        f"Backtested {metadata['symbols_with_history']}/{len(symbols)} symbols; "
        f"compression episodes {metadata['signal_events']}, matched controls "
        f"{metadata['matched_controls']}."
    )
    if summary.empty:
        print("No complete compression events with forward outcomes were found.")
    else:
        print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
