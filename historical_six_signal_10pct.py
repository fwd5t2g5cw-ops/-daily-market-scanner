from __future__ import annotations

import argparse
import csv
import io
import random
import subprocess
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

MARKETS = {
    "us": {"label": "US", "dir": "us", "prefix": "us", "tz": "America/Toronto"},
    "canada": {"label": "Canada", "dir": "canada", "prefix": "canada", "tz": "America/Toronto"},
    "hk": {"label": "HK", "dir": "hk", "prefix": "hk", "tz": "Asia/Hong_Kong"},
}

CATEGORIES = [
    ("entry_marker", "Entry Marker", "{prefix}_entry_marker_today.csv"),
    ("high_conviction", "High Conviction Entry", "{prefix}_high_conviction_entry_today.csv"),
    ("ready_now", "Double Reclaim READY NOW", "{prefix}_double_reclaim_ready_now.csv"),
    ("reclaim_breakout", "Reclaim Breakout", "{prefix}_reclaim_breakout_today.csv"),
    ("pre_entry", "Pre-Entry Watch", "{prefix}_pre_entry_watch_today.csv"),
    ("compression", "Pre-Breakout Compression", "{prefix}_pre_breakout_compression_today.csv"),
]

UP_THRESHOLD = 1.10
DOWN_THRESHOLD = 0.90


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL)


def git_history(path: str):
    try:
        raw = run_git("log", "--reverse", "--format=%H|%cI", "--", path)
    except subprocess.CalledProcessError:
        return []
    out = []
    for line in raw.splitlines():
        if "|" not in line:
            continue
        sha, iso = line.split("|", 1)
        out.append((sha.strip(), iso.strip()))
    return out


def show_file(sha: str, path: str) -> str | None:
    try:
        return run_git("show", f"{sha}:{path}")
    except subprocess.CalledProcessError:
        return None


def parse_csv(text: str | None):
    if not text or not text.strip():
        return []
    return list(csv.DictReader(io.StringIO(text)))


def local_date(iso: str, tz_name: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone(ZoneInfo(tz_name)).date().isoformat()


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def tv_symbol(market: str, symbol: str) -> str:
    if market == "canada":
        base = symbol[:-3] if symbol.endswith(".TO") else symbol
        base = base.replace("-UN", ".UN").replace("-A", ".A").replace("-B", ".B").replace("-U", ".U")
        base = base.replace("-", ".")
        return f"TSX:{base}"
    if market == "hk":
        base = symbol.split(".")[0].lstrip("0") or "0"
        return f"HKEX:{base}"
    return symbol


def tv_url(market: str, symbol: str) -> str:
    return "https://www.tradingview.com/chart/?symbol=" + quote(tv_symbol(market, symbol), safe="")


def collect_first_signals():
    first = {}

    for market, cfg in MARKETS.items():
        for category_key, category_label, filename_template in CATEGORIES:
            path = f"latest/{cfg['dir']}/" + filename_template.format(prefix=cfg["prefix"])
            daily = {}
            for sha, iso in git_history(path):
                d = local_date(iso, cfg["tz"])
                prev = daily.get(d)
                if prev is None or iso > prev[0]:
                    daily[d] = (iso, sha)

            seen = set()
            for d in sorted(daily):
                _, sha = daily[d]
                rows = parse_csv(show_file(sha, path))
                for row in rows:
                    symbol = (row.get("symbol") or "").strip().upper()
                    if not symbol or symbol in seen:
                        continue
                    price = as_float(row.get("current_price"))
                    if price is None or price <= 0:
                        continue
                    seen.add(symbol)
                    first[(market, category_key, symbol)] = {
                        "market": market,
                        "market_label": cfg["label"],
                        "category": category_key,
                        "category_label": category_label,
                        "symbol": symbol,
                        "signal_date": d,
                        "signal_price": price,
                        "tradingview_symbol": tv_symbol(market, symbol),
                        "tradingview_url": tv_url(market, symbol),
                    }
    return list(first.values())


def split_download(raw: pd.DataFrame, symbols: list[str]):
    out = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(map(str, raw.columns.get_level_values(0)))
        fields = {"Open", "High", "Low", "Close", "Volume"}
        ticker_first = len(fields & level0) < 3
        for s in symbols:
            try:
                d = raw.xs(s, axis=1, level=0 if ticker_first else 1, drop_level=True)
                d = d.dropna(how="all")
                if not d.empty:
                    out[s] = d
            except Exception:
                pass
    elif len(symbols) == 1:
        out[symbols[0]] = raw.dropna(how="all")
    return out


def download_history(symbols: list[str], start: str, end_exclusive: str, batch_size=80):
    data = {}
    failed = []
    for i in range(0, len(symbols), batch_size):
        group = symbols[i:i + batch_size]
        for attempt in range(3):
            try:
                raw = yf.download(
                    group,
                    start=start,
                    end=end_exclusive,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=True,
                    group_by="ticker",
                )
                got = split_download(raw, group)
                data.update(got)
                if got:
                    break
            except Exception as e:
                print("batch failed", i, attempt + 1, e)
            time.sleep(2 * (attempt + 1) + random.random())
        for s in group:
            if s not in data:
                failed.append(s)
        time.sleep(0.4 + random.random() * 0.5)

    still = []
    for n, s in enumerate(dict.fromkeys(failed), 1):
        recovered = False
        for attempt in range(3):
            try:
                raw = yf.download(
                    s,
                    start=start,
                    end=end_exclusive,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )
                if raw is not None and not raw.empty:
                    if isinstance(raw.columns, pd.MultiIndex):
                        raw.columns = raw.columns.get_level_values(0)
                    data[s] = raw.dropna(how="all")
                    recovered = True
                    break
            except Exception as e:
                print("single failed", s, attempt + 1, e)
            time.sleep(1.5 * (attempt + 1) + random.random())
        if not recovered:
            still.append(s)
        if n % 50 == 0:
            time.sleep(4)
    return data, still


def first_cross_date(frame: pd.DataFrame, col: str, threshold: float, direction: str):
    if frame.empty:
        return ""
    series = pd.to_numeric(frame[col], errors="coerce")
    mask = series >= threshold if direction == "up" else series <= threshold
    idx = frame.index[mask.fillna(False)]
    if len(idx) == 0:
        return ""
    return str(pd.Timestamp(idx[0]).date())


def evaluate(signals: list[dict], end_date: str):
    if not signals:
        return [], []

    start_date = min(x["signal_date"] for x in signals)
    dl_start = (datetime.strptime(start_date, "%Y-%m-%d").date() - timedelta(days=7)).isoformat()
    end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    dl_end = (end_dt + timedelta(days=1)).isoformat()

    by_market = defaultdict(list)
    for x in signals:
        by_market[x["market"]].append(x["symbol"])

    market_data = {}
    failures = []
    for market, syms in by_market.items():
        unique = list(dict.fromkeys(syms))
        print("Downloading", market, len(unique), "symbols")
        d, failed = download_history(unique, dl_start, dl_end)
        market_data[market] = d
        failures.extend({"market": market, "symbol": s} for s in failed)

    rows = []
    for sig in signals:
        frame = market_data.get(sig["market"], {}).get(sig["symbol"])
        base = dict(sig)
        if frame is None or frame.empty:
            rows.append({
                **base,
                "sessions_observed": 0,
                "max_high": "",
                "max_up_pct": "",
                "min_low": "",
                "max_down_pct": "",
                "up10": False,
                "down10": False,
                "first_up10_date": "",
                "first_down10_date": "",
                "order": "NO_DATA",
                "last_close": "",
                "last_date": "",
            })
            continue

        frame = frame.copy()
        frame.index = pd.to_datetime(frame.index).tz_localize(None).normalize()
        signal_ts = pd.Timestamp(sig["signal_date"])
        end_ts = pd.Timestamp(end_date)
        future = frame[(frame.index > signal_ts) & (frame.index <= end_ts)].copy()
        future = future.dropna(subset=["High", "Low", "Close"], how="any")

        if future.empty:
            rows.append({
                **base,
                "sessions_observed": 0,
                "max_high": "",
                "max_up_pct": "",
                "min_low": "",
                "max_down_pct": "",
                "up10": False,
                "down10": False,
                "first_up10_date": "",
                "first_down10_date": "",
                "order": "NO_FUTURE_SESSION",
                "last_close": "",
                "last_date": "",
            })
            continue

        price = float(sig["signal_price"])
        max_high = float(pd.to_numeric(future["High"], errors="coerce").max())
        min_low = float(pd.to_numeric(future["Low"], errors="coerce").min())
        max_up = (max_high / price - 1.0) * 100.0
        max_down = (min_low / price - 1.0) * 100.0
        up_date = first_cross_date(future, "High", price * UP_THRESHOLD, "up")
        down_date = first_cross_date(future, "Low", price * DOWN_THRESHOLD, "down")
        up10 = bool(up_date)
        down10 = bool(down_date)

        if up10 and down10:
            if up_date < down_date:
                order = "UP_FIRST"
            elif down_date < up_date:
                order = "DOWN_FIRST"
            else:
                order = "BOTH_SAME_DAY"
        elif up10:
            order = "UP_ONLY"
        elif down10:
            order = "DOWN_ONLY"
        else:
            order = "NONE"

        rows.append({
            **base,
            "sessions_observed": int(len(future)),
            "max_high": round(max_high, 4),
            "max_up_pct": round(max_up, 2),
            "min_low": round(min_low, 4),
            "max_down_pct": round(max_down, 2),
            "up10": up10,
            "down10": down10,
            "first_up10_date": up_date,
            "first_down10_date": down_date,
            "order": order,
            "last_close": round(float(future["Close"].iloc[-1]), 4),
            "last_date": str(pd.Timestamp(future.index[-1]).date()),
        })
    return rows, failures


def summary_rows(rows: list[dict]):
    out = []
    for category_key, category_label, _ in CATEGORIES:
        g = [r for r in rows if r["category"] == category_key and r["order"] != "NO_DATA"]
        with_future = [r for r in g if r["sessions_observed"] > 0]
        eligible10 = [r for r in with_future if r["sessions_observed"] >= 10]
        up = [r for r in with_future if r["up10"]]
        down = [r for r in with_future if r["down10"]]
        both = [r for r in with_future if r["up10"] and r["down10"]]

        def pct(n, d):
            return round(100 * n / d, 2) if d else ""

        out.append({
            "category": category_key,
            "category_label": category_label,
            "signals_with_price_data": len(g),
            "signals_with_future_sessions": len(with_future),
            "up10_count": len(up),
            "up10_rate_pct": pct(len(up), len(with_future)),
            "down10_count": len(down),
            "down10_rate_pct": pct(len(down), len(with_future)),
            "both_count": len(both),
            "up_only_count": sum(r["order"] == "UP_ONLY" for r in with_future),
            "down_only_count": sum(r["order"] == "DOWN_ONLY" for r in with_future),
            "up_first_count": sum(r["order"] == "UP_FIRST" for r in with_future),
            "down_first_count": sum(r["order"] == "DOWN_FIRST" for r in with_future),
            "both_same_day_count": sum(r["order"] == "BOTH_SAME_DAY" for r in with_future),
            "eligible_10_sessions": len(eligible10),
            "eligible10_up_count": sum(r["up10"] for r in eligible10),
            "eligible10_up_rate_pct": pct(sum(r["up10"] for r in eligible10), len(eligible10)),
            "eligible10_down_count": sum(r["down10"] for r in eligible10),
            "eligible10_down_rate_pct": pct(sum(r["down10"] for r in eligible10), len(eligible10)),
        })
    return out


def market_summary_rows(rows: list[dict]):
    out = []
    for category_key, category_label, _ in CATEGORIES:
        for market, cfg in MARKETS.items():
            g = [r for r in rows if r["category"] == category_key and r["market"] == market and r["sessions_observed"] > 0]
            if not g:
                continue
            out.append({
                "category": category_key,
                "category_label": category_label,
                "market": cfg["label"],
                "signals": len(g),
                "up10_count": sum(r["up10"] for r in g),
                "down10_count": sum(r["down10"] for r in g),
                "both_count": sum(r["up10"] and r["down10"] for r in g),
            })
    return out


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def fmt_symbol(r):
    if r["market"] == "hk":
        return r["symbol"].replace(".HK", "")
    return r["symbol"]


def write_report(path: Path, rows: list[dict], summary: list[dict], end_date: str, failures: list[dict]):
    lines = [
        "# Six-Signal ±10% Historical Research",
        "",
        f"Forward window ends: **{end_date}**.",
        "",
        "Method: for each market/category/symbol, use the first final daily scanner appearance and its published current_price as the reference. "
        "Forward performance starts on the **next trading session**. +10% uses subsequent daily High; -10% uses subsequent daily Low. "
        "If both thresholds are hit on the same daily bar, order is marked BOTH_SAME_DAY because intraday order is unknown.",
        "",
        "The same stock can appear in multiple scanner categories; that is intentional.",
        "",
        "## Summary",
        "",
        "| Category | Signals | +10% | +10% rate | -10% | -10% rate | Both | 10+ sessions eligible | +10% eligible rate | -10% eligible rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summary:
        lines.append(
            f"| {s['category_label']} | {s['signals_with_future_sessions']} | {s['up10_count']} | "
            f"{s['up10_rate_pct']}% | {s['down10_count']} | {s['down10_rate_pct']}% | {s['both_count']} | "
            f"{s['eligible_10_sessions']} | {s['eligible10_up_rate_pct']}% | {s['eligible10_down_rate_pct']}% |"
        )

    for category_key, category_label, _ in CATEGORIES:
        g = [r for r in rows if r["category"] == category_key and r["sessions_observed"] > 0]
        up = sorted((r for r in g if r["up10"]), key=lambda r: float(r["max_up_pct"]), reverse=True)
        down = sorted((r for r in g if r["down10"]), key=lambda r: float(r["max_down_pct"]))

        lines += ["", f"## {category_label}", "", f"### +10% or more — {len(up)}", ""]
        if not up:
            lines.append("—")
        for r in up:
            sym = fmt_symbol(r)
            lines.append(
                f"- [{sym}]({r['tradingview_url']}) — {r['market_label']} — signal {r['signal_date']} @ {r['signal_price']:.4f}; "
                f"max **+{r['max_up_pct']:.2f}%**; first +10% {r['first_up10_date']}; "
                f"max adverse {r['max_down_pct']:.2f}%; order {r['order']}; sessions {r['sessions_observed']}"
            )

        lines += ["", f"### -10% or worse — {len(down)}", ""]
        if not down:
            lines.append("—")
        for r in down:
            sym = fmt_symbol(r)
            lines.append(
                f"- [{sym}]({r['tradingview_url']}) — {r['market_label']} — signal {r['signal_date']} @ {r['signal_price']:.4f}; "
                f"max **{r['max_down_pct']:.2f}%**; first -10% {r['first_down10_date']}; "
                f"max favorable +{r['max_up_pct']:.2f}%; order {r['order']}; sessions {r['sessions_observed']}"
            )

    if failures:
        lines += ["", "## Price-download failures", ""]
        for r in failures:
            lines.append(f"- {r['market']}: {r['symbol']}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="latest/six_signal_10pct")
    ap.add_argument("--end-date", default=None)
    args = ap.parse_args()

    end_date = args.end_date or date.today().isoformat()
    signals = collect_first_signals()
    print("First-signal records:", len(signals))
    rows, failures = evaluate(signals, end_date)

    outdir = Path(args.outdir)
    write_csv(outdir / "all_signal_forward_performance.csv", rows)
    hits = [r for r in rows if r.get("up10") or r.get("down10")]
    write_csv(outdir / "plus_minus_10_hits.csv", hits)
    summary = summary_rows(rows)
    write_csv(outdir / "category_summary.csv", summary)
    write_csv(outdir / "category_market_summary.csv", market_summary_rows(rows))
    write_csv(outdir / "price_download_failures.csv", failures)
    write_report(outdir / "report.md", rows, summary, end_date, failures)

    print(pd.DataFrame(summary).to_string(index=False))
    print("Hits:", len(hits), "Failures:", len(failures))


if __name__ == "__main__":
    main()
