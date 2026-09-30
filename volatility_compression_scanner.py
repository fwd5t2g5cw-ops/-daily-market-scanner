"""Daily US volatility-compression scanner.

The model is direction-neutral: it ranks how tightly price/volatility has
contracted, then reports an expansion only after price actually leaves the
prior range with true-range confirmation.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


OUTPUT_COLUMNS = [
    "symbol",
    "as_of",
    "close",
    "score",
    "state",
    "edge_context",
    "expansion_signal",
    "hv20_pctile",
    "atr14_pctile",
    "bb_width_pctile",
    "sma_spread_pctile",
    "tr_contraction",
    "volume_contraction",
    "coil_width_pctile",
    "nr7",
    "prior_10d_high",
    "prior_10d_low",
    "latest_tr_vs_prev5_median",
    "atr14_current_pct",
    "range_20d_pct",
    "return_20d_pct",
    "return_60d_pct",
    "sma50_distance_pct",
    "max_abs_gap_20d_pct",
    "max_abs_gap_60d_pct",
    "days_since_10pct_gap",
    "avg_dollar_volume_20d",
    "prebreakout_pivot",
    "distance_to_pivot_pct",
    "prior_structure_high",
    "distance_above_prior_structure_pct",
    "rs_63d_vs_spy_pct",
    "rs_percentile",
    "prebreakout_eligible",
    "rejection_reasons",
    "bars",
]


@dataclass(frozen=True)
class ScannerConfig:
    percentile_window: int = 252
    min_bars: int = 160
    expansion_tr_multiple: float = 1.2


# A takeover/event gap followed by a near-motionless shelf looks statistically
# compressed, but it is not the pre-breakout supply/demand contraction sought by
# this scanner. These absolute guards sit outside the percentile-based score.
EVENT_GAP_COOLDOWN_DAYS = 60
MAX_RETURN_60D_PCT = 30.0
MAX_PRIOR_STRUCTURE_DISTANCE_PCT = 12.0
MIN_LIVE_ATR14_PCT = 0.65
MIN_LIVE_RANGE20_PCT = 2.0


def _percentile_of_latest(series: pd.Series, window: int = 252) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return math.nan
    sample = clean.iloc[-window:]
    value = float(sample.iloc[-1])
    return float((sample <= value).mean() * 100.0)


def _wilder_atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = frame["close"].shift(1)
    tr = pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def _true_range(frame: pd.DataFrame) -> pd.Series:
    prev_close = frame["close"].shift(1)
    return pd.concat(
        [
            frame["high"] - frame["low"],
            (frame["high"] - prev_close).abs(),
            (frame["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def _prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    work.columns = [str(column).lower() for column in work.columns]
    required = {"open", "high", "low", "close"}
    missing = required.difference(work.columns)
    if missing:
        raise ValueError(f"missing OHLC columns: {sorted(missing)}")
    if "volume" not in work.columns:
        work["volume"] = np.nan
    work = work[["open", "high", "low", "close", "volume"]].apply(
        pd.to_numeric, errors="coerce"
    )
    work = work.dropna(subset=["open", "high", "low", "close"])
    work = work[(work[["open", "high", "low", "close"]] > 0).all(axis=1)]
    return work.sort_index().loc[lambda x: ~x.index.duplicated(keep="last")]


def _safe_score(percentile: float) -> float:
    return 0.0 if not np.isfinite(percentile) else max(0.0, 100.0 - percentile)


def analyze_symbol(
    symbol: str,
    frame: pd.DataFrame,
    config: ScannerConfig | None = None,
    benchmark: pd.DataFrame | None = None,
) -> dict[str, object] | None:
    """Return a direction-neutral compression assessment for one symbol."""
    cfg = config or ScannerConfig()
    data = _prepare_frame(frame)
    if len(data) < cfg.min_bars:
        return None

    close = data["close"]
    open_ = data["open"]
    log_return = np.log(close / close.shift(1))
    hv20 = log_return.rolling(20).std(ddof=1) * np.sqrt(252) * 100
    tr = _true_range(data)
    atr14_pct = _wilder_atr(data, 14) / close * 100

    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std(ddof=0)
    bb_width = ((sma20 + 2 * std20) - (sma20 - 2 * std20)) / sma20 * 100

    sma5 = close.rolling(5).mean()
    sma10 = close.rolling(10).mean()
    sma_spread = (
        (
            pd.concat([sma5, sma10, sma20], axis=1).max(axis=1)
            - pd.concat([sma5, sma10, sma20], axis=1).min(axis=1)
        )
        / close
        * 100
    )

    tr5 = tr.rolling(5).mean()
    tr20 = tr.rolling(20).mean()
    tr_ratio = tr5 / tr20.replace(0, np.nan)
    volume5 = data["volume"].rolling(5).mean()
    volume20 = data["volume"].rolling(20).mean()
    volume_ratio = volume5 / volume20.replace(0, np.nan)
    coil_width = (
        (data["high"].rolling(10).max() - data["low"].rolling(10).min()) / close * 100
    )

    hv_pct = _percentile_of_latest(hv20, cfg.percentile_window)
    atr_pct = _percentile_of_latest(atr14_pct, cfg.percentile_window)
    bb_pct = _percentile_of_latest(bb_width, cfg.percentile_window)
    sma_pct = _percentile_of_latest(sma_spread, cfg.percentile_window)
    coil_pct = _percentile_of_latest(coil_width, cfg.percentile_window)

    latest_tr_ratio = float(tr_ratio.iloc[-1])
    latest_volume_ratio = float(volume_ratio.iloc[-1])
    tr_contraction = np.isfinite(latest_tr_ratio) and latest_tr_ratio <= 0.75
    volume_contraction = (
        np.isfinite(latest_volume_ratio) and latest_volume_ratio <= 0.75
    )
    prior7 = tr.iloc[-7:]
    nr7 = bool(len(prior7) == 7 and tr.iloc[-1] <= prior7.min())

    # Six continuous components plus two small binary confirmations.
    score = (
        0.20 * _safe_score(hv_pct)
        + 0.20 * _safe_score(atr_pct)
        + 0.20 * _safe_score(bb_pct)
        + 0.15 * _safe_score(sma_pct)
        + 0.15 * _safe_score(coil_pct)
        + (5.0 if tr_contraction else 0.0)
        + (3.0 if volume_contraction else 0.0)
        + (2.0 if nr7 else 0.0)
    )
    score = round(min(100.0, max(0.0, score)), 2)

    core = [hv_pct, atr_pct, bb_pct, sma_pct, coil_pct]
    tight25 = sum(np.isfinite(value) and value <= 25 for value in core)
    tight35 = sum(np.isfinite(value) and value <= 35 for value in core)
    if score >= 75 and tight25 >= 3:
        state = "COILED"
    elif score >= 60 and tight35 >= 2:
        state = "COMPRESSED"
    elif score >= 40:
        state = "TIGHTENING"
    else:
        state = "LOOSE"

    prior = data.iloc[-11:-1]
    prior_high = float(prior["high"].max())
    prior_low = float(prior["low"].min())
    prev5_median = float(tr.iloc[-6:-1].median())
    tr_multiple = (
        float(tr.iloc[-1] / prev5_median)
        if np.isfinite(prev5_median) and prev5_median > 0
        else math.nan
    )
    latest_close = float(close.iloc[-1])

    # Location and event-risk context. Compression after a large gap is not the
    # same setup as a mature base tightening immediately below an unbroken pivot.
    sma50 = close.rolling(50).mean()
    sma50_distance = float((latest_close / sma50.iloc[-1] - 1) * 100)
    atr14_current = float(atr14_pct.iloc[-1])
    range_20d = float(
        (data["high"].iloc[-20:].max() - data["low"].iloc[-20:].min())
        / latest_close
        * 100
    )
    return_20d = float((latest_close / close.iloc[-21] - 1) * 100)
    return_60d = float((latest_close / close.iloc[-61] - 1) * 100)
    gap_pct = (open_ / close.shift(1) - 1) * 100
    max_abs_gap_20d = float(gap_pct.iloc[-20:].abs().max())
    max_abs_gap_60d = float(gap_pct.iloc[-60:].abs().max())
    shock_positions = np.flatnonzero((gap_pct.abs() >= 10).fillna(False).to_numpy())
    days_since_gap = (
        int(len(data) - 1 - shock_positions[-1]) if len(shock_positions) else 999
    )
    avg_dollar_volume = float((close * data["volume"]).rolling(20).mean().iloc[-1])
    prebreakout_pivot = float(data["high"].iloc[-21:-1].max())
    distance_to_pivot = float((latest_close / prebreakout_pivot - 1) * 100)
    prior_structure_high = float(data["high"].iloc[-126:-21].max())
    distance_above_prior_structure = float(
        (latest_close / prior_structure_high - 1) * 100
    )

    rs_63d_vs_spy = math.nan
    if len(close) >= 64 and benchmark is not None:
        benchmark_data = _prepare_frame(benchmark)
        benchmark_close = benchmark_data["close"]
        if len(benchmark_close) >= 64:
            stock_return = latest_close / float(close.iloc[-64]) - 1
            spy_return = (
                float(benchmark_close.iloc[-1]) / float(benchmark_close.iloc[-64]) - 1
            )
            rs_63d_vs_spy = float((stock_return - spy_return) * 100)

    expansion_signal = "NONE"
    if np.isfinite(tr_multiple) and tr_multiple >= cfg.expansion_tr_multiple:
        if latest_close > prior_high:
            expansion_signal = "UP_EXPANSION_CONFIRMED"
        elif latest_close < prior_low:
            expansion_signal = "DOWN_EXPANSION_CONFIRMED"

    if expansion_signal != "NONE":
        edge_context = "RANGE_EXIT_CONFIRMED"
    elif state in {"COILED", "COMPRESSED"}:
        edge_context = (
            "NEAR_UPPER_EDGE"
            if latest_close >= prior_high * 0.98
            else (
                "NEAR_LOWER_EDGE" if latest_close <= prior_low * 1.02 else "INSIDE_COIL"
            )
        )
    else:
        edge_context = "NO_EDGE"

    as_of = data.index[-1]
    if isinstance(as_of, pd.Timestamp):
        as_of = as_of.date().isoformat()
    else:
        as_of = str(as_of)

    return {
        "symbol": symbol,
        "as_of": as_of,
        "close": round(latest_close, 4),
        "score": score,
        "state": state,
        "edge_context": edge_context,
        "expansion_signal": expansion_signal,
        "hv20_pctile": round(hv_pct, 2),
        "atr14_pctile": round(atr_pct, 2),
        "bb_width_pctile": round(bb_pct, 2),
        "sma_spread_pctile": round(sma_pct, 2),
        "tr_contraction": bool(tr_contraction),
        "volume_contraction": bool(volume_contraction),
        "coil_width_pctile": round(coil_pct, 2),
        "nr7": nr7,
        "prior_10d_high": round(prior_high, 4),
        "prior_10d_low": round(prior_low, 4),
        "latest_tr_vs_prev5_median": round(tr_multiple, 3),
        "atr14_current_pct": round(atr14_current, 2),
        "range_20d_pct": round(range_20d, 2),
        "return_20d_pct": round(return_20d, 2),
        "return_60d_pct": round(return_60d, 2),
        "sma50_distance_pct": round(sma50_distance, 2),
        "max_abs_gap_20d_pct": round(max_abs_gap_20d, 2),
        "max_abs_gap_60d_pct": round(max_abs_gap_60d, 2),
        "days_since_10pct_gap": days_since_gap,
        "avg_dollar_volume_20d": round(avg_dollar_volume, 2),
        "prebreakout_pivot": round(prebreakout_pivot, 4),
        "distance_to_pivot_pct": round(distance_to_pivot, 2),
        "prior_structure_high": round(prior_structure_high, 4),
        "distance_above_prior_structure_pct": round(
            distance_above_prior_structure, 2
        ),
        "rs_63d_vs_spy_pct": round(rs_63d_vs_spy, 2),
        "bars": len(data),
    }


def _chunks(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def _drop_incomplete_session(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or not isinstance(frame.index, pd.DatetimeIndex):
        return frame
    now_utc = datetime.now(timezone.utc)
    if ZoneInfo is None:  # pragma: no cover
        return frame
    now_et = now_utc.astimezone(ZoneInfo("America/New_York"))
    last_date = frame.index[-1].date()
    if last_date == now_et.date() and (now_et.hour, now_et.minute) < (16, 15):
        return frame.iloc[:-1]
    return frame


def _alpaca_symbol(symbol: str) -> str:
    return symbol.replace("-", ".")


def fetch_alpaca(
    symbols: list[str], api_key: str, api_secret: str, feed: str = "sip"
) -> dict[str, pd.DataFrame]:
    """Fetch split-adjusted daily bars from Alpaca with pagination."""
    reverse = {_alpaca_symbol(symbol): symbol for symbol in symbols}
    collected: dict[str, list[dict[str, object]]] = {symbol: [] for symbol in symbols}
    start = (datetime.now(timezone.utc) - timedelta(days=1100)).date().isoformat()
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": api_secret,
    }
    for batch in _chunks(list(reverse), 150):
        token: str | None = None
        while True:
            params = {
                "symbols": ",".join(batch),
                "timeframe": "1Day",
                "start": start,
                "adjustment": "all",
                "feed": feed,
                "sort": "asc",
                "limit": 10000,
            }
            if token:
                params["page_token"] = token
            response = requests.get(
                "https://data.alpaca.markets/v2/stocks/bars",
                headers=headers,
                params=params,
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            bars = payload.get("bars", {})
            for alpaca_name, rows in bars.items():
                original = reverse.get(alpaca_name)
                if original:
                    collected[original].extend(rows)
            token = payload.get("next_page_token")
            if not token:
                break

    output: dict[str, pd.DataFrame] = {}
    for symbol, rows in collected.items():
        if not rows:
            continue
        frame = pd.DataFrame(rows).rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        )
        frame.index = pd.to_datetime(frame["t"], utc=True)
        output[symbol] = _drop_incomplete_session(frame)
    return output


def fetch_yahoo(symbols: list[str]) -> dict[str, pd.DataFrame]:
    """Best-effort fallback; Alpaca is preferred for dependable automation."""
    import yfinance as yf

    output: dict[str, pd.DataFrame] = {}
    for batch in _chunks(symbols, 80):
        data = yf.download(
            tickers=" ".join(batch),
            period="3y",
            interval="1d",
            auto_adjust=True,
            group_by="ticker",
            threads=True,
            progress=False,
        )
        if len(batch) == 1 and not isinstance(data.columns, pd.MultiIndex):
            output[batch[0]] = _drop_incomplete_session(data)
        else:
            for symbol in batch:
                yahoo_symbol = symbol.replace("-", ".")
                for candidate in (symbol, yahoo_symbol):
                    if candidate in data.columns.get_level_values(0):
                        frame = data[candidate].dropna(how="all")
                        if not frame.empty:
                            output[symbol] = _drop_incomplete_session(frame)
                        break
        time.sleep(0.25)
    return output


def load_symbols(path: Path, limit: int | None = None) -> list[str]:
    symbols = []
    seen = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        symbol = raw.strip().upper()
        if symbol and not symbol.startswith("#") and symbol not in seen:
            symbols.append(symbol)
            seen.add(symbol)
    return symbols[:limit] if limit else symbols


def result_frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    results = pd.DataFrame(rows)
    results["rs_percentile"] = (
        results["rs_63d_vs_spy_pct"].rank(pct=True, method="average") * 100
    ).round(0)

    def rejection_reasons(row: pd.Series) -> str:
        reasons: list[str] = []
        if row["state"] not in {"COILED", "COMPRESSED"}:
            reasons.append("NOT_COMPRESSED")
        if row["expansion_signal"] != "NONE":
            reasons.append("ALREADY_EXPANDING")
        if (
            row["max_abs_gap_60d_pct"] >= 10
            or row["days_since_10pct_gap"] < EVENT_GAP_COOLDOWN_DAYS
        ):
            reasons.append("POST_GAP_COIL")
        if row["return_20d_pct"] > 15:
            reasons.append("RECENT_SURGE")
        if row["return_60d_pct"] > MAX_RETURN_60D_PCT:
            reasons.append("EXTENDED_60D_RUN")
        if row["sma50_distance_pct"] > 12:
            reasons.append("EXTENDED_FROM_SMA50")
        elif row["sma50_distance_pct"] < -3:
            reasons.append("BELOW_SMA50")
        if not -5 <= row["distance_to_pivot_pct"] <= 1:
            reasons.append("NOT_NEAR_UNBROKEN_PIVOT")
        if (
            row["distance_above_prior_structure_pct"]
            > MAX_PRIOR_STRUCTURE_DISTANCE_PCT
        ):
            reasons.append("DETACHED_FROM_PRIOR_STRUCTURE")
        if (
            row["atr14_current_pct"] < MIN_LIVE_ATR14_PCT
            and row["range_20d_pct"] < MIN_LIVE_RANGE20_PCT
        ):
            reasons.append("EVENT_PRICE_PEG")
        if (
            row["close"] < 5
            or pd.isna(row["avg_dollar_volume_20d"])
            or row["avg_dollar_volume_20d"] < 5_000_000
        ):
            reasons.append("LOW_LIQUIDITY")
        if pd.isna(row["rs_percentile"]):
            reasons.append("MISSING_RS")
        elif row["rs_percentile"] < 70:
            reasons.append("WEAK_RS")
        return "|".join(reasons)

    results["rejection_reasons"] = results.apply(rejection_reasons, axis=1)
    results["prebreakout_eligible"] = results["rejection_reasons"].eq("")
    results = results.reindex(columns=OUTPUT_COLUMNS)
    return results.sort_values(
        ["prebreakout_eligible", "score", "rs_percentile", "symbol"],
        ascending=[False, False, False, True],
    )


def write_outputs(
    results: pd.DataFrame,
    symbols: list[str],
    found: set[str],
    provider: str,
    outdir: Path,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    compression_watch = results[results["state"].isin(["COILED", "COMPRESSED"])]
    eligible_mask = results["prebreakout_eligible"].fillna(False).astype(bool)
    watch = results[eligible_mask]
    compression_eligible = (
        compression_watch["prebreakout_eligible"].fillna(False).astype(bool)
    )
    rejected = compression_watch[~compression_eligible]
    top50 = watch.head(50)
    missing = sorted(set(symbols).difference(found))

    results.to_csv(outdir / "all.csv", index=False)
    watch.to_csv(outdir / "watch.csv", index=False)
    watch.to_csv(outdir / "prebreakout_watch.csv", index=False)
    compression_watch.to_csv(outdir / "compression_watch.csv", index=False)
    rejected.to_csv(outdir / "rejected_compression.csv", index=False)
    top50.to_csv(outdir / "top50.csv", index=False)
    (outdir / "tradingview.txt").write_text(
        ",".join(watch["symbol"].tolist()),
        encoding="utf-8",
    )
    (outdir / "missing_symbols.txt").write_text("\n".join(missing), encoding="utf-8")
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "requested_symbols": len(symbols),
        "symbols_with_data": len(found),
        "coverage": round(len(found) / len(symbols), 4) if symbols else 0,
        "ranked": len(results),
        "compression_watch": len(compression_watch),
        "actionable_prebreakout_watch": len(watch),
        "rejected_compression": len(rejected),
        "coiled": int((results["state"] == "COILED").sum()) if len(results) else 0,
        "confirmed_expansions": int((results["expansion_signal"] != "NONE").sum())
        if len(results)
        else 0,
    }
    (outdir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", type=Path, default=Path("data/us_1b_universe.txt"))
    parser.add_argument(
        "--outdir", type=Path, default=Path("volatility_compression_results/us")
    )
    parser.add_argument(
        "--provider", choices=["auto", "alpaca", "yahoo"], default="auto"
    )
    parser.add_argument("--feed", default=os.getenv("ALPACA_FEED", "sip"))
    parser.add_argument("--min-coverage", type=float, default=0.85)
    parser.add_argument("--limit", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    symbols = load_symbols(args.symbols, args.limit)
    if not symbols:
        raise SystemExit("symbol list is empty")

    key = os.getenv("ALPACA_API_KEY_ID")
    secret = os.getenv("ALPACA_API_SECRET_KEY")
    provider = args.provider
    if provider == "auto":
        provider = "alpaca" if key and secret else "yahoo"
    request_symbols = list(dict.fromkeys([*symbols, "SPY"]))
    if provider == "alpaca":
        if not key or not secret:
            raise SystemExit(
                "Alpaca requires ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY"
            )
        frames = fetch_alpaca(request_symbols, key, secret, args.feed)
    else:
        frames = fetch_yahoo(request_symbols)

    found_symbols = set(symbols).intersection(frames)
    coverage = len(found_symbols) / len(symbols)
    if coverage < args.min_coverage:
        raise SystemExit(
            f"coverage {coverage:.1%} is below required {args.min_coverage:.1%}; "
            "refusing to publish a misleading partial scan"
        )

    rows = []
    benchmark = frames.get("SPY")
    for symbol in symbols:
        frame = frames.get(symbol)
        if frame is None or frame.empty:
            continue
        assessment = analyze_symbol(symbol, frame, benchmark=benchmark)
        if assessment:
            rows.append(assessment)
    results = result_frame(rows)
    write_outputs(results, symbols, found_symbols, provider, args.outdir)
    actionable = int(results["prebreakout_eligible"].sum()) if len(results) else 0
    print(
        f"Scanned {len(found_symbols)}/{len(symbols)} symbols via {provider}; "
        f"ranked {len(results)}, actionable pre-breakout watch {actionable}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
