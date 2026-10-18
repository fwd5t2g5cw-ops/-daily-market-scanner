from __future__ import annotations

import argparse
import csv
import io
import math
import random
import subprocess
import time
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf


MARKETS = {
    "us": {
        "label": "US",
        "dir": "us",
        "prefix": "us",
        "tz": "America/Toronto",
    },
    "canada": {
        "label": "Canada",
        "dir": "canada",
        "prefix": "canada",
        "tz": "America/Toronto",
    },
    "hk": {
        "label": "HK",
        "dir": "hk",
        "prefix": "hk",
        "tz": "Asia/Hong_Kong",
    },
}

CATEGORIES = [
    ("entry_marker", "Entry Marker", "{prefix}_entry_marker_today.csv"),
    ("high_conviction", "High Conviction Entry", "{prefix}_high_conviction_entry_today.csv"),
    ("ready_now", "Double Reclaim READY NOW", "{prefix}_double_reclaim_ready_now.csv"),
    ("reclaim_breakout", "Reclaim Breakout", "{prefix}_reclaim_breakout_today.csv"),
    ("pre_entry", "Pre-Entry Watch", "{prefix}_pre_entry_watch_today.csv"),
    ("compression", "Pre-Breakout Compression", "{prefix}_pre_breakout_compression_today.csv"),
]

META_NUMERIC = [
    "quality_score",
    "score",
    "compression_score",
    "high_conviction_score",
    "congestion_score",
    "rs_metric",
    "pct_below_52w_high",
    "breakout_age_days",
    "distance_to_breakout_pct",
    "pct_above_ema20",
    "ema20_breakout_distance_pct",
    "undercut_vs_breakout_pct",
]

META_BOOL = [
    "volume_contracting",
    "range_contracting",
    "touched_breakout_today",
    "touched_ema20_today",
    "above_both_now",
]


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


def num(row: dict, *names: str):
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            try:
                return float(value)
            except Exception:
                pass
    return None


def truthy(v):
    if v in (None, ""):
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def signal_meta(row: dict):
    return {
        "status": row.get("status", "") or row.get("setup", ""),
        "grade": row.get("grade", ""),
        "quality_score": num(row, "quality_score"),
        "score": num(row, "score"),
        "compression_score": num(row, "compression_score"),
        "high_conviction_score": num(row, "high_conviction_score"),
        "congestion_score": num(row, "congestion_score"),
        "congestion_status": row.get("congestion_status", ""),
        "candle_pattern": row.get("candle_pattern", ""),
        "candle_side": row.get("candle_side", ""),
        "rs_metric": num(row, "rs_vs_spy_pct", "rs_vs_xiu_pct", "rs_vs_2800_pct", "rs_pct"),
        "pct_below_52w_high": num(row, "pct_below_52w_high"),
        "breakout_age_days": num(row, "breakout_age_days"),
        "distance_to_breakout_pct": num(row, "distance_to_breakout_pct"),
        "pct_above_ema20": num(row, "pct_above_ema20"),
        "ema20_breakout_distance_pct": num(row, "ema20_breakout_distance_pct"),
        "undercut_vs_breakout_pct": num(row, "undercut_vs_breakout_pct"),
        "volume_contracting": truthy(row.get("volume_contracting")),
        "range_contracting": truthy(row.get("range_contracting")),
        "touched_breakout_today": truthy(row.get("touched_breakout_today")),
        "touched_ema20_today": truthy(row.get("touched_ema20_today")),
        "above_both_now": truthy(row.get("above_both_now")),
        "breakout_level": num(row, "breakout_level"),
        "ema20": num(row, "ema20_live", "ema20"),
    }


def collect_first_signals():
    rows = []
    for market, cfg in MARKETS.items():
        for category, label, filename_tpl in CATEGORIES:
            path = f"latest/{cfg['dir']}/" + filename_tpl.format(prefix=cfg["prefix"])
            per_day = {}
            for sha, iso in git_history(path):
                d = local_date(iso, cfg["tz"])
                parsed = parse_csv(show_file(sha, path))
                per_day[d] = (iso, parsed)

            seen = set()
            for d in sorted(per_day):
                iso, day_rows = per_day[d]
                for row in day_rows:
                    symbol = (row.get("symbol") or "").strip().upper()
                    if not symbol or symbol in seen:
                        continue
                    price = num(row, "current_price", "close")
                    if price is None or price <= 0:
                        continue
                    seen.add(symbol)
                    rec = {
                        "market_key": market,
                        "market": cfg["label"],
                        "category": category,
                        "category_label": label,
                        "symbol": symbol,
                        "signal_date": d,
                        "signal_commit_iso": iso,
                        "signal_price": float(price),
                    }
                    rec.update(signal_meta(row))
                    rows.append(rec)
    return rows


def flatten_frame(d):
    if d is None or d.empty:
        return None
    x = d.copy()
    if isinstance(x.columns, pd.MultiIndex):
        if x.columns.nlevels > 1:
            x.columns = x.columns.get_level_values(0)
    if not {"High", "Low", "Close"}.issubset(set(x.columns)):
        return None
    x = x[["High", "Low", "Close"]].apply(pd.to_numeric, errors="coerce").dropna(how="all")
    if x.empty:
        return None
    idx = pd.to_datetime(x.index)
    try:
        idx = idx.tz_localize(None)
    except TypeError:
        idx = idx.tz_convert(None)
    x.index = idx.normalize()
    return x


def split_download(raw, symbols):
    out = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(map(str, raw.columns.get_level_values(0)))
        fields = {"Open", "High", "Low", "Close", "Volume"}
        ticker_level = 0 if len(fields & level0) < 3 else 1
        for sym in symbols:
            try:
                x = raw.xs(sym, axis=1, level=ticker_level, drop_level=True)
                x = flatten_frame(x)
                if x is not None and not x.empty:
                    out[sym] = x
            except Exception:
                pass
    elif len(symbols) == 1:
        x = flatten_frame(raw)
        if x is not None:
            out[symbols[0]] = x
    return out


def download_prices(symbols, start: str, end_exclusive: str, chunk=60):
    prices = {}
    failed = []
    for i in range(0, len(symbols), chunk):
        batch = symbols[i:i + chunk]
        print(f"price batch {i+1}-{min(i+chunk, len(symbols))}/{len(symbols)}")
        got = {}
        for attempt in range(3):
            try:
                raw = yf.download(
                    batch,
                    start=start,
                    end=end_exclusive,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=True,
                    group_by="ticker",
                )
                got = split_download(raw, batch)
                if got:
                    break
            except Exception as e:
                print("batch fail", attempt + 1, e)
            time.sleep(3 * (attempt + 1) + random.uniform(0.5, 1.5))
        prices.update(got)
        missing = [s for s in batch if s not in got]
        failed.extend(missing)
        time.sleep(random.uniform(0.4, 1.0))

    failed = list(dict.fromkeys(failed))
    if failed:
        print("single-symbol recovery", len(failed))
    still_failed = []
    for n, sym in enumerate(failed, 1):
        found = None
        for attempt in range(3):
            try:
                raw = yf.download(
                    sym,
                    start=start,
                    end=end_exclusive,
                    interval="1d",
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )
                found = flatten_frame(raw)
                if found is not None and not found.empty:
                    break
            except Exception as e:
                print("single fail", sym, attempt + 1, e)
            time.sleep(2 * (attempt + 1))
        if found is not None and not found.empty:
            prices[sym] = found
        else:
            still_failed.append(sym)
        if n % 40 == 0:
            time.sleep(5)
    return prices, still_failed


def first_hit_date(series: pd.Series, threshold: float, mode: str):
    if mode == "ge":
        m = series >= threshold
    else:
        m = series <= threshold
    if not bool(m.any()):
        return ""
    return str(pd.Timestamp(series.index[np.flatnonzero(m.to_numpy())[0]]).date())


def tv_symbol(market_key: str, symbol: str):
    if market_key == "canada":
        base = symbol[:-3] if symbol.endswith(".TO") else symbol
        return "TSX:" + base.replace("-", ".")
    if market_key == "hk":
        base = symbol.split(".")[0].lstrip("0") or "0"
        return "HKEX:" + base
    return symbol


def tv_url(market_key: str, symbol: str):
    return "https://www.tradingview.com/chart/?symbol=" + quote(tv_symbol(market_key, symbol), safe="")


def analyze_signals(signals, prices_by_market, end_date: str):
    out = []
    for n, s in enumerate(signals, 1):
        market = s["market_key"]
        symbol = s["symbol"]
        d = prices_by_market.get(market, {}).get(symbol)
        rec = dict(s)
        rec["tradingview_url"] = tv_url(market, symbol)
        rec.update({
            "followup_trading_days": 0,
            "max_high_after": "",
            "max_up_pct": "",
            "min_low_after": "",
            "max_down_pct": "",
            "first_up10_date": "",
            "days_to_up10": "",
            "first_down10_date": "",
            "days_to_down10": "",
            "hit_up10": False,
            "hit_down10": False,
            "hit_both": False,
            "hit_order": "NO_DATA",
            "up10_within_10d": False,
            "down10_within_10d": False,
            "eligible_10d": False,
            "latest_price_date": "",
            "latest_close": "",
            "current_return_pct": "",
        })
        if d is None or d.empty:
            out.append(rec)
            continue

        sig_dt = pd.Timestamp(s["signal_date"])
        end_dt = pd.Timestamp(end_date)
        future = d[(d.index > sig_dt) & (d.index <= end_dt)].dropna(subset=["High", "Low", "Close"], how="all")
        if future.empty:
            rec["hit_order"] = "NO_FOLLOWUP"
            out.append(rec)
            continue

        rec["followup_trading_days"] = int(len(future))
        rec["eligible_10d"] = bool(len(future) >= 10)
        px = float(s["signal_price"])
        hi = pd.to_numeric(future["High"], errors="coerce")
        lo = pd.to_numeric(future["Low"], errors="coerce")
        cl = pd.to_numeric(future["Close"], errors="coerce")

        max_hi = float(hi.max())
        min_lo = float(lo.min())
        rec["max_high_after"] = round(max_hi, 4)
        rec["max_up_pct"] = round((max_hi / px - 1) * 100, 2)
        rec["min_low_after"] = round(min_lo, 4)
        rec["max_down_pct"] = round((min_lo / px - 1) * 100, 2)

        up_date = first_hit_date(hi, px * 1.10, "ge")
        down_date = first_hit_date(lo, px * 0.90, "le")
        rec["first_up10_date"] = up_date
        rec["first_down10_date"] = down_date
        rec["hit_up10"] = bool(up_date)
        rec["hit_down10"] = bool(down_date)
        rec["hit_both"] = bool(up_date and down_date)

        if up_date:
            rec["days_to_up10"] = int(np.flatnonzero((hi >= px * 1.10).to_numpy())[0] + 1)
        if down_date:
            rec["days_to_down10"] = int(np.flatnonzero((lo <= px * 0.90).to_numpy())[0] + 1)

        first10 = future.iloc[:10]
        rec["up10_within_10d"] = bool((pd.to_numeric(first10["High"], errors="coerce") >= px * 1.10).any())
        rec["down10_within_10d"] = bool((pd.to_numeric(first10["Low"], errors="coerce") <= px * 0.90).any())

        if up_date and down_date:
            if up_date < down_date:
                rec["hit_order"] = "UP10_FIRST"
            elif down_date < up_date:
                rec["hit_order"] = "DOWN10_FIRST"
            else:
                rec["hit_order"] = "SAME_DAY_UNKNOWN"
        elif up_date:
            rec["hit_order"] = "UP10_ONLY"
        elif down_date:
            rec["hit_order"] = "DOWN10_ONLY"
        else:
            rec["hit_order"] = "NEITHER"

        latest_idx = cl.dropna().index[-1] if not cl.dropna().empty else None
        if latest_idx is not None:
            latest_close = float(cl.loc[latest_idx])
            rec["latest_price_date"] = str(pd.Timestamp(latest_idx).date())
            rec["latest_close"] = round(latest_close, 4)
            rec["current_return_pct"] = round((latest_close / px - 1) * 100, 2)

        out.append(rec)

    return out


def safe_pct(n, d):
    return round(100 * n / d, 2) if d else np.nan


def summarize(rows):
    df = pd.DataFrame(rows)
    summaries = []
    groups = []
    for cat, label, _ in CATEGORIES:
        groups.append(("ALL", cat, label, df[df.category == cat]))
        for market in ["US", "Canada", "HK"]:
            groups.append((market, cat, label, df[(df.category == cat) & (df.market == market)]))

    for market, cat, label, g in groups:
        if g.empty:
            summaries.append({
                "market": market, "category": cat, "category_label": label,
                "signals": 0, "with_followup": 0, "up10": 0, "down10": 0,
                "both": 0, "up10_only": 0, "down10_only": 0, "neither": 0,
                "up10_rate_pct": np.nan, "down10_rate_pct": np.nan,
                "up_first": 0, "down_first": 0, "same_day_unknown": 0,
                "median_days_to_up10": np.nan, "median_days_to_down10": np.nan,
                "eligible_10d": 0, "up10_within10": 0, "down10_within10": 0,
                "up10_within10_rate_pct": np.nan, "down10_within10_rate_pct": np.nan,
            })
            continue
        follow = g[g.followup_trading_days > 0]
        up = follow[follow.hit_up10 == True]
        down = follow[follow.hit_down10 == True]
        both = follow[(follow.hit_up10 == True) & (follow.hit_down10 == True)]
        up_only = follow[(follow.hit_up10 == True) & (follow.hit_down10 == False)]
        down_only = follow[(follow.hit_up10 == False) & (follow.hit_down10 == True)]
        neither = follow[(follow.hit_up10 == False) & (follow.hit_down10 == False)]
        elig = follow[follow.eligible_10d == True]
        summaries.append({
            "market": market,
            "category": cat,
            "category_label": label,
            "signals": int(len(g)),
            "with_followup": int(len(follow)),
            "up10": int(len(up)),
            "down10": int(len(down)),
            "both": int(len(both)),
            "up10_only": int(len(up_only)),
            "down10_only": int(len(down_only)),
            "neither": int(len(neither)),
            "up10_rate_pct": safe_pct(len(up), len(follow)),
            "down10_rate_pct": safe_pct(len(down), len(follow)),
            "up_first": int((follow.hit_order == "UP10_FIRST").sum()),
            "down_first": int((follow.hit_order == "DOWN10_FIRST").sum()),
            "same_day_unknown": int((follow.hit_order == "SAME_DAY_UNKNOWN").sum()),
            "median_days_to_up10": round(pd.to_numeric(up.days_to_up10, errors="coerce").median(), 2) if len(up) else np.nan,
            "median_days_to_down10": round(pd.to_numeric(down.days_to_down10, errors="coerce").median(), 2) if len(down) else np.nan,
            "eligible_10d": int(len(elig)),
            "up10_within10": int((elig.up10_within_10d == True).sum()),
            "down10_within10": int((elig.down10_within_10d == True).sum()),
            "up10_within10_rate_pct": safe_pct((elig.up10_within_10d == True).sum(), len(elig)),
            "down10_within10_rate_pct": safe_pct((elig.down10_within_10d == True).sum(), len(elig)),
        })
    return pd.DataFrame(summaries)


def pattern_rows(rows):
    df = pd.DataFrame(rows)
    out = []
    for cat, label, _ in CATEGORIES:
        g = df[df.category == cat].copy()
        up = g[(g.hit_up10 == True) & (g.hit_down10 == False)]
        down = g[(g.hit_down10 == True) & (g.hit_up10 == False)]
        for feature in META_NUMERIC:
            a = pd.to_numeric(up.get(feature), errors="coerce").dropna() if feature in up.columns else pd.Series(dtype=float)
            b = pd.to_numeric(down.get(feature), errors="coerce").dropna() if feature in down.columns else pd.Series(dtype=float)
            if len(a) == 0 and len(b) == 0:
                continue
            out.append({
                "category": cat,
                "category_label": label,
                "feature": feature,
                "type": "numeric_median",
                "up_only_n": int(len(a)),
                "up_only_value": round(float(a.median()), 3) if len(a) else np.nan,
                "down_only_n": int(len(b)),
                "down_only_value": round(float(b.median()), 3) if len(b) else np.nan,
            })
        for feature in META_BOOL:
            if feature not in g.columns:
                continue
            a = up[feature].dropna()
            b = down[feature].dropna()
            if len(a) == 0 and len(b) == 0:
                continue
            out.append({
                "category": cat,
                "category_label": label,
                "feature": feature,
                "type": "true_rate_pct",
                "up_only_n": int(len(a)),
                "up_only_value": round(100 * a.astype(bool).mean(), 2) if len(a) else np.nan,
                "down_only_n": int(len(b)),
                "down_only_value": round(100 * b.astype(bool).mean(), 2) if len(b) else np.nan,
            })
    return pd.DataFrame(out)


def ticker_display(market: str, symbol: str):
    if market == "HK":
        return symbol.split(".")[0]
    return symbol


def md_link(row):
    name = ticker_display(row["market"], row["symbol"])
    return f"[{name}]({row['tradingview_url']})"


def fmt_num(v, suffix="%"):
    if v in (None, ""):
        return "—"
    try:
        if math.isnan(float(v)):
            return "—"
    except Exception:
        pass
    return f"{float(v):.2f}{suffix}"


def top_candles(g, n=4):
    vals = [str(x).strip() for x in g.get("candle_pattern", pd.Series(dtype=str)).tolist() if str(x).strip() and str(x) != "nan"]
    if not vals:
        return "—"
    c = Counter(vals)
    return ", ".join(f"{k} ({v})" for k, v in c.most_common(n))


def write_report(path: Path, rows, summary: pd.DataFrame, end_date: str):
    df = pd.DataFrame(rows)
    lines = [
        "# Six-Filter ±10% Follow-Through Research",
        "",
        f"Analysis end date: **{end_date}**.",
        "",
        "Method: for each market and each of the six scanner categories, take the first day a symbol appeared in that category and use that published scanner `current_price` as the signal price. To avoid look-ahead, performance starts from the **next trading session**. A +10% hit occurs when a later daily High reaches 110% of signal price; a -10% hit occurs when a later daily Low reaches 90% of signal price. One symbol may appear in multiple categories because the goal is to compare stages independently.",
        "",
        "## Overall comparison",
        "",
        "| Filter | Signals | +10% | -10% | Both | +10% rate | -10% rate | 10-session +10% | 10-session -10% |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    allsum = summary[summary.market == "ALL"]
    for _, r in allsum.iterrows():
        lines.append(
            f"| {r.category_label} | {int(r.signals)} | {int(r.up10)} | {int(r.down10)} | {int(r.both)} | "
            f"{fmt_num(r.up10_rate_pct)} | {fmt_num(r.down10_rate_pct)} | "
            f"{fmt_num(r.up10_within10_rate_pct)} | {fmt_num(r.down10_within10_rate_pct)} |"
        )

    for cat, label, _ in CATEGORIES:
        g = df[df.category == cat].copy()
        lines += ["", f"## {label}", ""]
        for direction, title, sortcol, ascending in [
            ("up", "🟢 Reached +10%", "max_up_pct", False),
            ("down", "🔴 Reached -10%", "max_down_pct", True),
        ]:
            h = g[g.hit_up10 == True] if direction == "up" else g[g.hit_down10 == True]
            h = h.sort_values(sortcol, ascending=ascending)
            lines += [f"### {title} — {len(h)}", ""]
            if h.empty:
                lines.append("—")
                lines.append("")
                continue
            lines += [
                "| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |",
                "|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
            for _, r in h.iterrows():
                lines.append(
                    f"| {r.market} | {md_link(r)} | {r.signal_date} | {r.signal_price:.4g} | "
                    f"{fmt_num(r.max_up_pct)} | {fmt_num(r.max_down_pct)} | "
                    f"{r.first_up10_date or '—'} | {r.first_down10_date or '—'} | {r.hit_order} |"
                )
            lines.append("")

        up_only = g[(g.hit_up10 == True) & (g.hit_down10 == False)]
        down_only = g[(g.hit_down10 == True) & (g.hit_up10 == False)]
        lines += [
            "### Pattern snapshot",
            "",
            f"- +10%-only sample: **{len(up_only)}**; -10%-only sample: **{len(down_only)}**.",
            f"- +10%-only common candles: {top_candles(up_only)}.",
            f"- -10%-only common candles: {top_candles(down_only)}.",
        ]
        for feature, label2 in [
            ("rs_metric", "Median RS"),
            ("pct_below_52w_high", "Median % below 52w high"),
            ("breakout_age_days", "Median breakout age"),
            ("distance_to_breakout_pct", "Median distance to breakout"),
            ("pct_above_ema20", "Median % above EMA20"),
            ("quality_score", "Median quality score"),
            ("compression_score", "Median compression score"),
            ("congestion_score", "Median congestion score"),
        ]:
            if feature not in g.columns:
                continue
            a = pd.to_numeric(up_only[feature], errors="coerce").dropna()
            b = pd.to_numeric(down_only[feature], errors="coerce").dropna()
            if len(a) or len(b):
                av = f"{a.median():.2f}" if len(a) else "—"
                bv = f"{b.median():.2f}" if len(b) else "—"
                lines.append(f"- {label2}: +10%-only **{av}** vs -10%-only **{bv}**.")

    lines += [
        "",
        "## Notes",
        "",
        "- Results are observational, not a trading recommendation.",
        "- Recent signals have less follow-up time; use the 10-session columns for a fairer stage-to-stage comparison.",
        "- A symbol can be counted in both +10% and -10% if both thresholds were reached after its signal. The Order column shows which threshold happened first; same-day order cannot be resolved from daily OHLC.",
        "- yfinance failures are retained separately so missing price history is visible rather than silently treated as a non-hit.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="research/six_filter_10pct")
    ap.add_argument("--end", default=str(date.today()))
    args = ap.parse_args()

    signals = collect_first_signals()
    if not signals:
        raise RuntimeError("No historical scanner signals found")

    earliest = min(s["signal_date"] for s in signals)
    start = (datetime.fromisoformat(earliest).date() - timedelta(days=5)).isoformat()
    end_exclusive = (datetime.fromisoformat(args.end).date() + timedelta(days=2)).isoformat()

    prices_by_market = {}
    failures = []
    for market in MARKETS:
        syms = sorted({s["symbol"] for s in signals if s["market_key"] == market})
        print(f"=== {MARKETS[market]['label']}: {len(syms)} unique historical scanner symbols ===")
        prices, failed = download_prices(syms, start, end_exclusive)
        prices_by_market[market] = prices
        failures.extend({"market": MARKETS[market]["label"], "symbol": x} for x in failed)

    rows = analyze_signals(signals, prices_by_market, args.end)
    summary = summarize(rows)
    patterns = pattern_rows(rows)

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    all_df = pd.DataFrame(rows)
    all_df.to_csv(out / "all_signals.csv", index=False)
    all_df[all_df.hit_up10 == True].sort_values(["category", "max_up_pct"], ascending=[True, False]).to_csv(out / "up_10pct.csv", index=False)
    all_df[all_df.hit_down10 == True].sort_values(["category", "max_down_pct"], ascending=[True, True]).to_csv(out / "down_10pct.csv", index=False)
    all_df[(all_df.hit_up10 == True) & (all_df.hit_down10 == True)].to_csv(out / "both_10pct.csv", index=False)
    summary.to_csv(out / "summary_by_filter.csv", index=False)
    patterns.to_csv(out / "pattern_comparison.csv", index=False)
    pd.DataFrame(failures).to_csv(out / "price_download_failures.csv", index=False)
    write_report(out / "report.md", rows, summary, args.end)

    print("\nOVERALL")
    print(summary[summary.market == "ALL"].to_string(index=False))
    print("\nPrice download failures:", len(failures))


if __name__ == "__main__":
    main()

# workflow-trigger: six-filter-10pct
