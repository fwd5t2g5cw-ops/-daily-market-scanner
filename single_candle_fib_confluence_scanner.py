#!/usr/bin/env python3
"""Scan for the user's two-single-candle Fibonacci confluence setup.

Candle A: high=1.000, low=0.786.
Candle B (later/lower): low=1.000, high=0.786.
Qualified when Candle A +1.618 and Candle B -1.618 differ by <=2%.
A buy signal is a daily close reclaiming Candle A 0.382 after Candle B is confirmed.
"""

from __future__ import annotations
import argparse
import math
import time
from pathlib import Path
import pandas as pd
import yfinance as yf

ANCHOR = 0.786

def fib_a(low: float, high: float, level: float) -> float:
    return low + (level - ANCHOR) * (high - low) / (1.0 - ANCHOR)

def fib_b(low: float, high: float, level: float) -> float:
    return high + (level - ANCHOR) * (low - high) / (1.0 - ANCHOR)

def gap(a: float, b: float) -> float:
    mid = (abs(a) + abs(b)) / 2
    return abs(a - b) / mid if mid else math.inf

def read_symbols(path: Path, limit: int) -> list[str]:
    symbols = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.split(",", 1)[0].strip()
        if s and not s.startswith("#") and s.lower() not in {"symbol", "ticker"}:
            symbols.append(s)
    return symbols[:limit] if limit else symbols

def normalize(raw: pd.DataFrame) -> pd.DataFrame:
    if raw.empty:
        return raw
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    df = raw.reset_index()
    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]
    date_col = "date" if "date" in df.columns else "datetime"
    df = df.rename(columns={date_col: "date"})
    need = ["date", "open", "high", "low", "close"]
    if any(c not in df.columns for c in need):
        return pd.DataFrame()
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce").dt.tz_localize(None)
    for c in ["open", "high", "low", "close", "volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=need).sort_values("date").drop_duplicates("date").reset_index(drop=True)

def pivots(df: pd.DataFrame, w: int) -> tuple[list[int], list[int]]:
    highs, lows = [], []
    for i in range(w, len(df) - w):
        h = float(df.at[i, "high"])
        l = float(df.at[i, "low"])
        if h >= float(df.loc[i-w:i+w, "high"].max()):
            highs.append(i)
        if l <= float(df.loc[i-w:i+w, "low"].min()):
            lows.append(i)
    return highs, lows

def classify(df: pd.DataFrame, signal: int | None, stop: float, level_0382: float,
             target: float, new_bars: int) -> str:
    last = len(df) - 1
    if signal is None:
        return "WATCH_BELOW_0382" if float(df.at[last, "close"]) <= level_0382 else "ABOVE_0382_UNCONFIRMED"
    after = df.iloc[signal:]
    if float(after["low"].min()) <= stop:
        return "FAILED_STOP"
    if float(after["high"].max()) >= target:
        return "TARGET_HIT"
    if float(df.at[last, "close"]) < level_0382:
        return "LOST_RECLAIM"
    if last - signal <= new_bars:
        return "NEW_RECLAIM"
    return "ACTIVE_ABOVE_0382"

def scan_symbol(symbol: str, raw: pd.DataFrame, args) -> dict | None:
    df = normalize(raw)
    if len(df) < 80:
        return None
    ph, pl = pivots(df, args.pivot_window)
    candidates = []
    last = len(df) - 1
    for i in ph:
        for j in pl:
            if j <= i + 1 or j - i > args.max_pair_bars:
                continue
            if last - j > args.max_setup_age:
                continue
            ah, al = float(df.at[i, "high"]), float(df.at[i, "low"])
            bl, bh = float(df.at[j, "low"]), float(df.at[j, "high"])
            if bl >= al or ah <= al or bh <= bl:
                continue
            a382 = fib_a(al, ah, 0.382)
            a1618 = fib_a(al, ah, 1.618)
            bneg = fib_b(bl, bh, -1.618)
            overlap = gap(a1618, bneg)
            if overlap > args.tolerance:
                continue
            target = (a1618 + bneg) / 2
            if target <= a382 or a382 <= bl:
                continue
            available = j + args.pivot_window
            signal = None
            for k in range(available, len(df)):
                prior = float(df.at[k-1, "close"]) if k else float("-inf")
                close = float(df.at[k, "close"])
                if close > a382 and (prior <= a382 or k == available):
                    signal = k
                    break
            entry_idx = signal + 1 if signal is not None and signal + 1 < len(df) else signal
            entry = float(df.at[entry_idx, "open"]) if entry_idx is not None else math.nan
            rr = (target-entry)/(entry-bl) if entry_idx is not None and entry > bl else math.nan
            state = classify(df, signal, bl, a382, target, args.new_signal_bars)
            row = {
                "symbol": symbol,
                "state": state,
                "high_candle_date": df.at[i, "date"].date().isoformat(),
                "high_candle_high": ah,
                "high_candle_low": al,
                "low_candle_date": df.at[j, "date"].date().isoformat(),
                "low_candle_high": bh,
                "low_candle_low_stop": bl,
                "fib_a_0382": a382,
                "fib_a_1618": a1618,
                "fib_b_neg1618": bneg,
                "extension_gap_pct": overlap * 100,
                "signal_date": df.at[signal, "date"].date().isoformat() if signal is not None else "",
                "entry_date": df.at[entry_idx, "date"].date().isoformat() if entry_idx is not None else "",
                "entry_next_open": entry,
                "target_midpoint": target,
                "planned_rr": rr,
                "last_date": df.at[last, "date"].date().isoformat(),
                "last_close": float(df.at[last, "close"]),
            }
            freshness = signal if signal is not None else j
            state_rank = {"NEW_RECLAIM": 5, "ACTIVE_ABOVE_0382": 4, "LOST_RECLAIM": 3,
                          "WATCH_BELOW_0382": 2, "ABOVE_0382_UNCONFIRMED": 1,
                          "TARGET_HIT": 0, "FAILED_STOP": -1}.get(state, 0)
            candidates.append((state_rank, freshness, -overlap, row))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return candidates[0][3]

def download(symbol: str, period: str) -> pd.DataFrame:
    for attempt in range(3):
        try:
            return yf.download(symbol, period=period, auto_adjust=False, progress=False, threads=False)
        except Exception:
            if attempt == 2:
                return pd.DataFrame()
            time.sleep(1.5 * (attempt + 1))
    return pd.DataFrame()

def write_report(rows: list[dict], out: Path, market: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    columns = ["symbol","state","extension_gap_pct","high_candle_date","low_candle_date",
               "fib_a_0382","last_close","signal_date","entry_next_open",
               "low_candle_low_stop","target_midpoint","planned_rr",
               "fib_a_1618","fib_b_neg1618","last_date",
               "high_candle_high","high_candle_low","low_candle_high","entry_date"]
    result = pd.DataFrame(rows)
    if result.empty:
        result = pd.DataFrame(columns=columns)
    else:
        result = result.sort_values(["state","extension_gap_pct","symbol"])
        result = result[[c for c in columns if c in result.columns]]
    result.to_csv(out / "results.csv", index=False)
    counts = result["state"].value_counts().to_dict() if not result.empty else {}
    active = result[result["state"].isin(["NEW_RECLAIM","ACTIVE_ABOVE_0382","LOST_RECLAIM","WATCH_BELOW_0382"])]
    lines = [
        f"# Single-Candle Fib Confluence Scanner — {market.upper()}",
        "",
        "Exact rule: high candle High=1/Low=0.786; later low candle Low=1/High=0.786; "
        f"+1.618 vs -1.618 gap <= {args.tolerance*100:.2f}%.",
        "",
        f"- Symbols scanned: {args.scanned}",
        f"- Qualified structures: {len(result)}",
        f"- State counts: {counts}",
        "",
        "## Current candidates",
        "",
    ]
    if active.empty:
        lines.append("No active candidates.")
    else:
        lines += ["|Symbol|State|Gap %|0.382|Last|Signal|Stop|Target|RR|",
                  "|---|---|---:|---:|---:|---|---:|---:|---:|"]
        for _, r in active.head(100).iterrows():
            lines.append(f"|{r.symbol}|{r.state}|{r.extension_gap_pct:.2f}|{r.fib_a_0382:.2f}|"
                         f"{r.last_close:.2f}|{r.signal_date}|{r.low_candle_low_stop:.2f}|"
                         f"{r.target_midpoint:.2f}|{r.planned_rr:.2f}|")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbols", type=Path, required=True)
    p.add_argument("--market", default="unknown")
    p.add_argument("--period", default="2y")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--pivot-window", type=int, default=2)
    p.add_argument("--max-pair-bars", type=int, default=120)
    p.add_argument("--max-setup-age", type=int, default=180)
    p.add_argument("--new-signal-bars", type=int, default=5)
    p.add_argument("--tolerance", type=float, default=0.02)
    global args
    args = p.parse_args()
    symbols = read_symbols(args.symbols, args.limit)
    rows = []
    for n, symbol in enumerate(symbols, 1):
        row = scan_symbol(symbol, download(symbol, args.period), args)
        if row:
            rows.append(row)
        if n % 50 == 0:
            print(f"{args.market}: {n}/{len(symbols)}", flush=True)
    args.scanned = len(symbols)
    write_report(rows, args.output, args.market)

if __name__ == "__main__":
    main()
