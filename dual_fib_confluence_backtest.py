#!/usr/bin/env python3
"""Backtest the dual-Fibonacci 0.382 / 1.618 confluence setup.

The setup uses two custom Fibonacci legs:

* Leg A (bearish): pivot high is level 1.000 and the following pivot low is
  level 0.786.
* Leg B (bullish): a later, lower pivot low is level 1.000 and the following
  pivot high is level 0.786.

The candidate is valid when the two projected 0.382 prices are within the
chosen tolerance and Leg A's +1.618 is close to Leg B's -1.618.  A signal is
the first daily close above the upper 0.382 price after all pivots are known.
Entry is the following open.  Success means target before stop; stop wins ties
on a daily bar because daily OHLC cannot reveal intraday ordering.

The program accepts one CSV, a directory of CSV files, or a ticker universe
downloaded through the optional yfinance package.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

import numpy as np
import pandas as pd


FIB_ANCHOR_LEVEL = 0.786


@dataclass(frozen=True)
class Pivot:
    index: int
    kind: str
    price: float
    confirmed_index: int


@dataclass(frozen=True)
class Leg:
    start: Pivot
    end: Pivot


@dataclass
class Trade:
    symbol: str
    a_high_date: str
    a_low_date: str
    b_low_date: str
    b_high_date: str
    signal_date: str
    entry_date: str
    fib_a_0382: float
    fib_b_0382: float
    overlap_0382_pct: float
    fib_a_1618: float
    fib_b_neg1618: float
    overlap_1618_pct: float
    entry: float
    stop: float
    target: float
    planned_r: float
    outcome: str
    exit_date: str
    exit_price: float
    realized_r: float
    holding_days: int
    max_favourable_r: float
    max_adverse_r: float


def fib_price(price_at_1: float, price_at_0786: float, level: float) -> float:
    """Return price at a Fib level from the user's two custom anchors."""
    slope = (price_at_1 - price_at_0786) / (1.0 - FIB_ANCHOR_LEVEL)
    return price_at_0786 + (level - FIB_ANCHOR_LEVEL) * slope


def relative_gap(a: float, b: float) -> float:
    """Symmetric relative distance.  0.02 means two percent."""
    midpoint = (abs(a) + abs(b)) / 2.0
    return abs(a - b) / midpoint if midpoint else math.inf


def normalize_ohlcv(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {
        "datetime": "date",
        "timestamp": "date",
        "adj_close": "close",
        "adjclose": "close",
    }
    df = df.rename(columns={k: v for k, v in aliases.items() if k in df.columns})
    if "date" not in df.columns:
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index().rename(columns={df.index.name or "index": "date"})
        else:
            raise ValueError("CSV must contain a Date/Datetime/Timestamp column")
    required = ["date", "open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns: {', '.join(missing)}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_localize(None)
    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=required).sort_values("date").drop_duplicates("date")
    return df.reset_index(drop=True)


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    previous = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous).abs(),
            (df["low"] - previous).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window, min_periods=window).mean()


def confirmed_pivots(df: pd.DataFrame, left: int, right: int) -> tuple[list[Pivot], list[Pivot]]:
    """Find local pivots; each pivot becomes available only `right` bars later."""
    highs = df["high"].to_numpy(float)
    lows = df["low"].to_numpy(float)
    pivot_highs: list[Pivot] = []
    pivot_lows: list[Pivot] = []
    for i in range(left, len(df) - right):
        left_highs, right_highs = highs[i - left : i], highs[i + 1 : i + right + 1]
        left_lows, right_lows = lows[i - left : i], lows[i + 1 : i + right + 1]
        if highs[i] > np.max(left_highs) and highs[i] >= np.max(right_highs):
            pivot_highs.append(Pivot(i, "H", float(highs[i]), i + right))
        if lows[i] < np.min(left_lows) and lows[i] <= np.min(right_lows):
            pivot_lows.append(Pivot(i, "L", float(lows[i]), i + right))
    return pivot_highs, pivot_lows


def valid_leg(
    df: pd.DataFrame,
    start: Pivot,
    end: Pivot,
    min_leg_pct: float,
    min_leg_atr: float,
    max_leg_bars: int,
) -> bool:
    if not (0 < end.index - start.index <= max_leg_bars):
        return False
    move = abs(end.price - start.price)
    if move / max(abs(start.price), 1e-12) < min_leg_pct:
        return False
    local_atr = atr(df).iloc[start.index]
    return not (pd.notna(local_atr) and move < min_leg_atr * float(local_atr))


def build_legs(
    df: pd.DataFrame,
    highs: list[Pivot],
    lows: list[Pivot],
    min_leg_pct: float,
    min_leg_atr: float,
    max_leg_bars: int,
) -> tuple[list[Leg], list[Leg]]:
    bearish: list[Leg] = []
    bullish: list[Leg] = []
    for h in highs:
        candidates = [l for l in lows if h.index < l.index <= h.index + max_leg_bars]
        for l in candidates:
            if h.price > l.price and valid_leg(df, h, l, min_leg_pct, min_leg_atr, max_leg_bars):
                bearish.append(Leg(h, l))
    for l in lows:
        candidates = [h for h in highs if l.index < h.index <= l.index + max_leg_bars]
        for h in candidates:
            if h.price > l.price and valid_leg(df, l, h, min_leg_pct, min_leg_atr, max_leg_bars):
                bullish.append(Leg(l, h))
    return bearish, bullish


def evaluate_outcome(
    df: pd.DataFrame,
    entry_index: int,
    entry: float,
    stop: float,
    target: float,
    max_holding: int,
) -> dict:
    risk = entry - stop
    end = min(len(df), entry_index + max_holding)
    window = df.iloc[entry_index:end]
    best_high = entry
    worst_low = entry
    for offset, (_, row) in enumerate(window.iterrows()):
        best_high = max(best_high, float(row.high))
        worst_low = min(worst_low, float(row.low))
        stop_hit = float(row.low) <= stop
        target_hit = float(row.high) >= target
        # Conservative daily-bar rule: a same-day tie is a failure.
        if stop_hit:
            return {
                "outcome": "FAIL_STOP",
                "exit_index": entry_index + offset,
                "exit_price": stop,
                "realized_r": -1.0,
                "holding_days": offset + 1,
                "mfe_r": (best_high - entry) / risk,
                "mae_r": (worst_low - entry) / risk,
            }
        if target_hit:
            planned_r = (target - entry) / risk
            return {
                "outcome": "SUCCESS_TARGET",
                "exit_index": entry_index + offset,
                "exit_price": target,
                "realized_r": planned_r,
                "holding_days": offset + 1,
                "mfe_r": (best_high - entry) / risk,
                "mae_r": (worst_low - entry) / risk,
            }
    last_index = max(entry_index, end - 1)
    last_close = float(df.iloc[last_index].close)
    return {
        "outcome": "UNRESOLVED",
        "exit_index": last_index,
        "exit_price": last_close,
        "realized_r": (last_close - entry) / risk,
        "holding_days": max(0, end - entry_index),
        "mfe_r": (best_high - entry) / risk,
        "mae_r": (worst_low - entry) / risk,
    }


def backtest_symbol(symbol: str, raw: pd.DataFrame, args: argparse.Namespace) -> list[Trade]:
    df = normalize_ohlcv(raw)
    if len(df) < 80:
        return []
    highs, lows = confirmed_pivots(df, args.pivot_left, args.pivot_right)
    bearish, bullish = build_legs(
        df, highs, lows, args.min_leg_pct, args.min_leg_atr, args.max_leg_bars
    )
    candidates: list[tuple[float, Trade]] = []
    for leg_a in bearish:
        a_high, a_low = leg_a.start, leg_a.end
        a_0382 = fib_price(a_high.price, a_low.price, 0.382)
        a_1618 = fib_price(a_high.price, a_low.price, 1.618)
        for leg_b in bullish:
            b_low, b_high = leg_b.start, leg_b.end
            if not (a_low.index < b_low.index < b_high.index):
                continue
            if b_low.index - a_low.index > args.max_pair_gap:
                continue
            if b_low.price >= a_low.price:
                continue
            b_0382 = fib_price(b_low.price, b_high.price, 0.382)
            b_neg1618 = fib_price(b_low.price, b_high.price, -1.618)
            gap_0382 = relative_gap(a_0382, b_0382)
            gap_1618 = relative_gap(a_1618, b_neg1618)
            if gap_0382 > args.tolerance or gap_1618 > args.tolerance:
                continue
            zone_high = max(a_0382, b_0382)
            target = (a_1618 + b_neg1618) / 2.0
            stop = b_low.price
            available = max(a_low.confirmed_index, b_high.confirmed_index)
            signal_index: Optional[int] = None
            search_end = min(len(df) - 1, available + args.signal_wait)
            for i in range(available, search_end + 1):
                if float(df.iloc[i].close) > zone_high:
                    signal_index = i
                    break
            if signal_index is None or signal_index + 1 >= len(df):
                continue
            entry_index = signal_index + 1
            entry = float(df.iloc[entry_index].open)
            if not (target > entry > stop):
                continue
            planned_r = (target - entry) / (entry - stop)
            if planned_r < args.min_rr:
                continue
            result = evaluate_outcome(
                df, entry_index, entry, stop, target, args.max_holding
            )
            date = lambda i: df.iloc[i].date.strftime("%Y-%m-%d")
            trade = Trade(
                symbol=symbol,
                a_high_date=date(a_high.index),
                a_low_date=date(a_low.index),
                b_low_date=date(b_low.index),
                b_high_date=date(b_high.index),
                signal_date=date(signal_index),
                entry_date=date(entry_index),
                fib_a_0382=a_0382,
                fib_b_0382=b_0382,
                overlap_0382_pct=gap_0382 * 100.0,
                fib_a_1618=a_1618,
                fib_b_neg1618=b_neg1618,
                overlap_1618_pct=gap_1618 * 100.0,
                entry=entry,
                stop=stop,
                target=target,
                planned_r=planned_r,
                outcome=result["outcome"],
                exit_date=date(result["exit_index"]),
                exit_price=result["exit_price"],
                realized_r=result["realized_r"],
                holding_days=result["holding_days"],
                max_favourable_r=result["mfe_r"],
                max_adverse_r=result["mae_r"],
            )
            score = gap_0382 + gap_1618
            candidates.append((score, trade))

    # Several anchor combinations can describe the same signal.  Keep the
    # tightest confluence, then enforce independent events with a cooldown.
    best_by_signal: dict[tuple[str, str], tuple[float, Trade]] = {}
    for score, trade in candidates:
        key = (trade.symbol, trade.signal_date)
        if key not in best_by_signal or score < best_by_signal[key][0]:
            best_by_signal[key] = (score, trade)
    ordered = sorted((v[1] for v in best_by_signal.values()), key=lambda t: t.signal_date)
    independent: list[Trade] = []
    last_entry: Optional[pd.Timestamp] = None
    for trade in ordered:
        current = pd.Timestamp(trade.entry_date)
        if last_entry is None or (current - last_entry).days >= args.cooldown_calendar_days:
            independent.append(trade)
            last_entry = current
    return independent


def read_csvs(input_path: Path, symbol_override: Optional[str]) -> Iterator[tuple[str, pd.DataFrame]]:
    if input_path.is_file():
        yield symbol_override or input_path.stem.upper(), pd.read_csv(input_path)
        return
    if not input_path.is_dir():
        raise FileNotFoundError(input_path)
    for path in sorted(input_path.glob("*.csv")):
        yield path.stem.upper(), pd.read_csv(path)


def download_universe(path: Path, period: str) -> Iterator[tuple[str, pd.DataFrame]]:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install optional downloader: pip install yfinance") from exc
    tickers = []
    for line in path.read_text(encoding="utf-8").splitlines():
        ticker = line.split(",", 1)[0].strip()
        if ticker and not ticker.startswith("#") and ticker.lower() not in {"symbol", "ticker"}:
            tickers.append(ticker)
    for ticker in tickers:
        try:
            raw = yf.download(ticker, period=period, auto_adjust=False, progress=False, threads=False)
            if raw.empty:
                print(f"WARN {ticker}: no data", file=sys.stderr)
                continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            yield ticker, raw.reset_index()
        except Exception as exc:  # keep a large universe running
            print(f"WARN {ticker}: {exc}", file=sys.stderr)


def summarize(trades: list[Trade], errors: list[str]) -> dict:
    completed = [t for t in trades if t.outcome != "UNRESOLVED"]
    successes = [t for t in trades if t.outcome == "SUCCESS_TARGET"]
    failures = [t for t in trades if t.outcome == "FAIL_STOP"]
    qualified = [t for t in trades if t.planned_r >= 2.5]
    return {
        "signals": len(trades),
        "success_target": len(successes),
        "fail_stop": len(failures),
        "unresolved": len(trades) - len(completed),
        "success_rate_completed_pct": round(100 * len(successes) / len(completed), 2) if completed else None,
        "failure_rate_completed_pct": round(100 * len(failures) / len(completed), 2) if completed else None,
        "average_planned_r": round(float(np.mean([t.planned_r for t in trades])), 3) if trades else None,
        "average_realized_r": round(float(np.mean([t.realized_r for t in trades])), 3) if trades else None,
        "median_holding_days": round(float(np.median([t.holding_days for t in completed])), 1) if completed else None,
        "signals_with_planned_r_at_least_2_5": len(qualified),
        "success_rate_r_at_least_2_5_pct": round(
            100 * sum(t.outcome == "SUCCESS_TARGET" for t in qualified)
            / max(1, sum(t.outcome != "UNRESOLVED" for t in qualified)),
            2,
        ) if qualified else None,
        "errors": errors,
    }


def write_outputs(trades: list[Trade], output_dir: Path, errors: list[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [asdict(t) for t in trades]
    pd.DataFrame(rows).to_csv(output_dir / "dual_fib_trades.csv", index=False)
    summary = summarize(trades, errors)
    (output_dir / "dual_fib_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = [
        "# 雙重 Fibonacci 共振回測結果",
        "",
        f"- 獨立訊號：{summary['signals']}",
        f"- 成功（先到1.618）：{summary['success_target']}",
        f"- 失敗（先穿止蝕）：{summary['fail_stop']}",
        f"- 90日未完成：{summary['unresolved']}",
        f"- 已完成案例成功率：{summary['success_rate_completed_pct']}%",
        f"- 平均計劃R：{summary['average_planned_r']}",
        f"- 平均實現R：{summary['average_realized_r']}",
        "",
        "同一日同時觸及目標及止蝕，按保守規則列作失敗。",
    ]
    (output_dir / "dual_fib_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Backtest dual-Fib 0.382 and 1.618 confluence")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="OHLC CSV file or directory of CSV files")
    source.add_argument("--universe", type=Path, help="Ticker list; downloads data with yfinance")
    p.add_argument("--symbol", help="Symbol label for one input CSV")
    p.add_argument("--period", default="10y", help="yfinance history period (default: 10y)")
    p.add_argument("--output", type=Path, default=Path("dual_fib_output"))
    p.add_argument("--tolerance", type=float, default=0.02, help="Confluence tolerance (default: 0.02)")
    p.add_argument("--pivot-left", type=int, default=3)
    p.add_argument("--pivot-right", type=int, default=3)
    p.add_argument("--min-leg-pct", type=float, default=0.015)
    p.add_argument("--min-leg-atr", type=float, default=0.75)
    p.add_argument("--max-leg-bars", type=int, default=40)
    p.add_argument("--max-pair-gap", type=int, default=120)
    p.add_argument("--signal-wait", type=int, default=40)
    p.add_argument("--max-holding", type=int, default=90)
    p.add_argument("--min-rr", type=float, default=0.0)
    p.add_argument("--cooldown-calendar-days", type=int, default=45)
    p.add_argument("--max-events", type=int, default=500)
    p.add_argument("--max-symbols", type=int, default=0, help="Limit downloaded/processed symbols; 0 means all")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = parser().parse_args(argv)
    source: Iterable[tuple[str, pd.DataFrame]]
    source = read_csvs(args.input, args.symbol) if args.input else download_universe(args.universe, args.period)
    all_trades: list[Trade] = []
    errors: list[str] = []
    for symbol_number, (symbol, raw) in enumerate(source, start=1):
        if args.max_symbols > 0 and symbol_number > args.max_symbols:
            break
        try:
            trades = backtest_symbol(symbol, raw, args)
            all_trades.extend(trades)
            print(f"{symbol}: {len(trades)} independent signals", file=sys.stderr)
        except Exception as exc:
            message = f"{symbol}: {type(exc).__name__}: {exc}"
            errors.append(message)
            print(f"WARN {message}", file=sys.stderr)
    all_trades.sort(key=lambda t: (t.entry_date, t.symbol), reverse=True)
    if args.max_events > 0:
        all_trades = all_trades[: args.max_events]
    all_trades.sort(key=lambda t: (t.entry_date, t.symbol))
    write_outputs(all_trades, args.output, errors)
    print(json.dumps(summarize(all_trades, errors), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
