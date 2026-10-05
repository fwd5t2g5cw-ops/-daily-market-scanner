from __future__ import annotations

import argparse
import csv
import io
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

MARKETS = {
    "us": {
        "label": "US",
        "dir": "us",
        "prefix": "us",
        "tz": "America/Toronto",
        "tv_exchange": "NYSE",
    },
    "canada": {
        "label": "Canada",
        "dir": "canada",
        "prefix": "canada",
        "tz": "America/Toronto",
        "tv_exchange": "TSX",
    },
    "hk": {
        "label": "HK",
        "dir": "hk",
        "prefix": "hk",
        "tz": "Asia/Hong_Kong",
        "tv_exchange": "HKEX",
    },
}

# Known US exchange overrides. TradingView often resolves bare symbols too, but these
# make the most-used historical names one-click correct.
US_EXCHANGE_OVERRIDES = {
    "IQV": "NYSE",
    "SCCO": "NYSE",
    "XOM": "NYSE",
    "ESTC": "NYSE",
    "NUTX": "NASDAQ",
    "KB": "NYSE",
    "VOD": "NASDAQ",
    "BP": "NYSE",
}


def load_us_exchange_map():
    p = Path("data/us_1b_universe.csv")
    if not p.exists():
        return {}
    mapping = {}
    try:
        with p.open(newline="") as f:
            for row in csv.DictReader(f):
                symbol = (row.get("symbol") or "").strip().upper()
                exchange = (row.get("exchange") or "").strip().upper()
                tv = {"NMS": "NASDAQ", "NCM": "NASDAQ", "NGM": "NASDAQ", "NYQ": "NYSE", "ASE": "AMEX"}.get(exchange)
                if symbol and tv:
                    mapping[symbol] = tv
    except Exception:
        return {}
    return mapping


US_EXCHANGE_MAP = load_us_exchange_map()


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


def f(row: dict, *names: str):
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            try:
                return float(value)
            except Exception:
                pass
    return None


def truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def local_date(iso: str, tz_name: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt.astimezone(ZoneInfo(tz_name)).date().isoformat()


def tv_symbol(market: str, symbol: str) -> str:
    if market == "canada":
        base = symbol[:-3] if symbol.endswith(".TO") else symbol
        base = base.replace("-", ".")
        return f"TSX:{base}"
    if market == "hk":
        base = symbol.split(".")[0].lstrip("0") or "0"
        return f"HKEX:{base.zfill(4)}"
    exchange = US_EXCHANGE_OVERRIDES.get(symbol) or US_EXCHANGE_MAP.get(symbol)
    return f"{exchange}:{symbol}" if exchange else symbol


def tv_url(market: str, symbol: str) -> str:
    full = tv_symbol(market, symbol)
    return "https://www.tradingview.com/chart/?symbol=" + quote(full, safe="")


def collect_observations():
    # observations[(market, symbol)][date] = merged latest snapshot for that day.
    observations = defaultdict(dict)

    for market, cfg in MARKETS.items():
        files = [
            (
                "pre",
                f"latest/{cfg['dir']}/{cfg['prefix']}_pre_entry_watch_today.csv",
            ),
            (
                "signal",
                f"latest/{cfg['dir']}/{cfg['prefix']}_signals_with_candles.csv",
            ),
        ]

        for source, path in files:
            for sha, iso in git_history(path):
                date = local_date(iso, cfg["tz"])
                rows = parse_csv(show_file(sha, path))
                for row in rows:
                    symbol = (row.get("symbol") or "").strip().upper()
                    if not symbol:
                        continue
                    key = (market, symbol)
                    day = observations[key].setdefault(
                        date,
                        {
                            "date": date,
                            "market": market,
                            "symbol": symbol,
                            "_commit_iso": iso,
                        },
                    )
                    # Process history in chronological order; later snapshots on the
                    # same day overwrite earlier fields and therefore represent the
                    # final published state for that date.
                    day["_commit_iso"] = iso
                    price = f(row, "current_price", "close")
                    breakout = f(row, "breakout_level")
                    if price is not None:
                        day["price"] = price
                    if breakout is not None:
                        day[f"{source}_breakout"] = breakout

                    if source == "pre":
                        day["pre_seen"] = True
                        day["pre_grade"] = row.get("grade", "")
                        day["pre_score"] = row.get("score", "")
                        ema = f(row, "ema20")
                        if ema is not None:
                            day["ema20"] = ema
                    else:
                        day["signal_seen"] = True
                        day["status"] = row.get("status", "")
                        day["signal_grade"] = row.get("grade", "")
                        day["candle_pattern"] = row.get("candle_pattern", "")
                        day["candle_side"] = row.get("candle_side", "")
                        day["above_both"] = truthy(row.get("above_both_now"))
                        day["double_reclaim"] = truthy(row.get("double_reclaim"))
                        day["reclaim_breakout"] = truthy(row.get("reclaim_breakout"))
                        day["entry_marker"] = truthy(row.get("entry_marker"))
                        day_low = f(row, "day_low")
                        if day_low is not None:
                            day["day_low"] = day_low
                        ema = f(row, "ema20_live")
                        if ema is not None:
                            day["ema20"] = ema

    return observations


def build_rows(observations):
    winners = []
    all_history = []

    for (market, symbol), days_map in observations.items():
        days = sorted(days_map.values(), key=lambda x: (x["date"], x.get("_commit_iso", "")))
        if not days:
            continue

        first_seen = days[0]["date"]

        # Prefer first PRE-ENTRY target because it is the actual "front high" the
        # user was waiting to break. Fall back to the structural signal level.
        initial_level = None
        initial_level_date = None
        for d in days:
            if d.get("pre_breakout") is not None:
                initial_level = d["pre_breakout"]
                initial_level_date = d["date"]
                break
        if initial_level is None:
            for d in days:
                if d.get("signal_breakout") is not None:
                    initial_level = d["signal_breakout"]
                    initial_level_date = d["date"]
                    break
        if initial_level is None or initial_level <= 0:
            continue

        first_breakout = None
        for d in days:
            p = d.get("price")
            if p is not None and p > initial_level:
                first_breakout = d
                break

        max_day = max(
            (d for d in days if d.get("price") is not None),
            key=lambda d: d["price"],
            default=None,
        )

        history_row = {
            "market": MARKETS[market]["label"],
            "symbol": symbol,
            "first_seen_date": first_seen,
            "initial_breakout_level": round(initial_level, 4),
            "initial_level_date": initial_level_date,
            "first_breakout_date": first_breakout["date"] if first_breakout else "",
            "first_breakout_price": round(first_breakout["price"], 4) if first_breakout else "",
            "max_snapshot_date": max_day["date"] if max_day else "",
            "max_snapshot_price": round(max_day["price"], 4) if max_day else "",
            "max_gain_vs_initial_breakout_pct": (
                round((max_day["price"] / initial_level - 1.0) * 100.0, 2)
                if max_day else ""
            ),
            "tradingview_symbol": tv_symbol(market, symbol),
            "tradingview_url": tv_url(market, symbol),
        }
        all_history.append(history_row)

        if first_breakout is None:
            continue

        first_break_idx = days.index(first_breakout)
        false_break = None
        false_type = ""
        reclaim = None
        second_break = None

        # A false break means that after the first top breakout, a later signal
        # snapshot closes below its structural breakout level and/or EMA20.
        for d in days[first_break_idx + 1 :]:
            p = d.get("price")
            if p is None:
                continue
            sb = d.get("signal_breakout")
            ema = d.get("ema20")
            below_breakout = sb is not None and p < sb
            below_ema = ema is not None and p < ema
            if below_breakout or below_ema:
                false_break = d
                if below_breakout and below_ema:
                    false_type = "BREAKOUT+EMA20"
                elif below_breakout:
                    false_type = "BREAKOUT"
                else:
                    false_type = "EMA20"
                break

        if false_break:
            fb_i = days.index(false_break)
            for d in days[fb_i + 1 :]:
                p = d.get("price")
                if p is None:
                    continue
                sb = d.get("signal_breakout")
                ema = d.get("ema20")
                if sb is not None and ema is not None and p > sb and p > ema:
                    reclaim = d
                    break

            # A valid "second breakout" must happen on or after the reclaim.
            # This prevents ordinary bounces above the old high from being counted
            # before the reclaim confirmation itself.
            if reclaim is not None:
                reclaim_i = days.index(reclaim)
                for d in days[reclaim_i:]:
                    p = d.get("price")
                    if p is not None and p > initial_level:
                        second_break = d
                        break

        gain = (max_day["price"] / initial_level - 1.0) * 100.0 if max_day else 0.0
        if gain >= 10:
            strength = "10%+"
        elif gain >= 5:
            strength = "5%+"
        elif gain >= 2:
            strength = "2%+"
        else:
            strength = "BREAKOUT_ONLY"

        current = days[-1]
        winners.append(
            {
                **history_row,
                "breakout_strength": strength,
                "false_break": bool(false_break),
                "false_break_date": false_break["date"] if false_break else "",
                "false_break_type": false_type,
                "reclaim_date": reclaim["date"] if reclaim else "",
                "second_breakout_date": second_break["date"] if second_break else "",
                "second_breakout_after_false_break": bool(second_break),
                "current_snapshot_date": current["date"],
                "current_snapshot_price": round(current["price"], 4) if current.get("price") is not None else "",
                "current_status": current.get("status", ""),
                "current_candle": current.get("candle_pattern", ""),
            }
        )

    winners.sort(
        key=lambda r: (
            float(r["max_gain_vs_initial_breakout_pct"] or -999),
            r["symbol"],
        ),
        reverse=True,
    )
    all_history.sort(
        key=lambda r: (
            bool(r["first_breakout_date"]),
            float(r["max_gain_vs_initial_breakout_pct"] or -999),
        ),
        reverse=True,
    )
    return winners, all_history


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_summary(path: Path, winners: list[dict]):
    lines = [
        "# Historical Winners",
        "",
        "Auto-built from committed US / Canada / HK scanner snapshots.",
        "Max gain uses the highest **published scanner snapshot price**, not intraday high.",
        "",
        "## Breakouts ranked by follow-through",
        "",
        "| Market | Symbol | First seen | First breakout | Initial level | Max snapshot | Max gain | False break | Reclaim | Second breakout | TradingView |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|",
    ]
    for r in winners:
        tv = f"[Open]({r['tradingview_url']})"
        fb = (
            f"{r['false_break_date']} ({r['false_break_type']})"
            if r["false_break"]
            else "—"
        )
        lines.append(
            "| {market} | **{symbol}** | {first_seen_date} | {first_breakout_date} | "
            "{initial_breakout_level} | {max_snapshot_price} ({max_snapshot_date}) | "
            "**{max_gain_vs_initial_breakout_pct}%** | {fb} | {reclaim} | {second} | {tv} |".format(
                **r,
                fb=fb,
                reclaim=r["reclaim_date"] or "—",
                second=r["second_breakout_date"] or "—",
                tv=tv,
            )
        )

    lines += [
        "",
        "## Reclaim + second-breakout cases",
        "",
        "| Market | Symbol | False break | Reclaim | Second breakout | Max gain | TradingView |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    cases = [r for r in winners if r["second_breakout_after_false_break"]]
    for r in cases:
        lines.append(
            f"| {r['market']} | **{r['symbol']}** | {r['false_break_date']} "
            f"({r['false_break_type']}) | {r['reclaim_date'] or '—'} | "
            f"{r['second_breakout_date']} | **{r['max_gain_vs_initial_breakout_pct']}%** | "
            f"[Open]({r['tradingview_url']}) |"
        )
    if not cases:
        lines.append("| — | — | — | — | — | — | — |")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="latest")
    args = ap.parse_args()

    observations = collect_observations()
    winners, all_history = build_rows(observations)
    out = Path(args.outdir)

    write_csv(out / "historical_winners.csv", winners)
    write_csv(out / "historical_breakout_history.csv", all_history)
    write_summary(out / "historical_winners_summary.md", winners)

    print(f"Tracked candidates: {len(all_history)}")
    print(f"Confirmed first breakouts: {len(winners)}")
    print(f"False-break -> second-breakout cases: {sum(bool(x['second_breakout_after_false_break']) for x in winners)}")
    print("Top 20:")
    for r in winners[:20]:
        print(
            r["market"],
            r["symbol"],
            r["first_breakout_date"],
            f"{r['max_gain_vs_initial_breakout_pct']}%",
            "reclaim-second-break" if r["second_breakout_after_false_break"] else "",
        )


if __name__ == "__main__":
    main()
