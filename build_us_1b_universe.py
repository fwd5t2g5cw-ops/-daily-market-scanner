from __future__ import annotations

import argparse
from pathlib import Path
import time

import pandas as pd
import yfinance as yf
from yfinance import EquityQuery


DEFAULT_MIN_MARKET_CAP = 1_000_000_000
PAGE_SIZE = 250  # Yahoo/yfinance maximum for custom screen queries


def build_query(min_market_cap: int) -> EquityQuery:
    # EquityQuery already restricts the asset class to equities.  Region=US plus
    # the major US equity exchanges keeps ETFs/funds/warrants out of this list.
    return EquityQuery(
        "and",
        [
            EquityQuery("eq", ["region", "us"]),
            EquityQuery("gte", ["intradaymarketcap", min_market_cap]),
            EquityQuery("is-in", ["exchange", "NMS", "NGM", "NCM", "NYQ", "ASE"]),
        ],
    )


def fetch_page(query: EquityQuery, offset: int, retries: int = 4) -> dict:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return yf.screen(
                query,
                offset=offset,
                size=PAGE_SIZE,
                sortField="ticker",
                sortAsc=True,
            )
        except Exception as exc:
            last_error = exc
            delay = 2 ** attempt * 3
            print(f"screen offset={offset} failed ({exc}); retry in {delay}s")
            time.sleep(delay)
    raise RuntimeError(f"Yahoo screener failed at offset={offset}: {last_error}")


def normalize_quote(q: dict) -> dict | None:
    symbol = str(q.get("symbol") or "").strip().upper().replace(".", "-")
    if not symbol:
        return None

    market_cap = q.get("marketCap")
    if market_cap is None:
        market_cap = q.get("intradaymarketcap")
    try:
        market_cap = int(float(market_cap)) if market_cap is not None else None
    except (TypeError, ValueError):
        market_cap = None

    return {
        "symbol": symbol,
        "name": q.get("shortName") or q.get("longName") or q.get("displayName") or "",
        "exchange": q.get("exchange") or q.get("fullExchangeName") or "",
        "market_cap": market_cap,
        "price": q.get("regularMarketPrice") or q.get("intradayprice"),
    }


def build_us_1b_universe(min_market_cap: int = DEFAULT_MIN_MARKET_CAP) -> pd.DataFrame:
    query = build_query(min_market_cap)
    rows: list[dict] = []
    offset = 0
    total_hint: int | None = None

    while True:
        response = fetch_page(query, offset)
        quotes = response.get("quotes") or []

        if total_hint is None:
            for key in ("total", "count"):
                try:
                    if response.get(key) is not None:
                        total_hint = int(response[key])
                        break
                except (TypeError, ValueError):
                    pass
            if total_hint is not None:
                print(f"Yahoo reports about {total_hint} matching US equities")

        if not quotes:
            break

        for q in quotes:
            row = normalize_quote(q)
            if row and (row["market_cap"] is None or row["market_cap"] >= min_market_cap):
                rows.append(row)

        print(f"Fetched {len(quotes)} quotes at offset {offset}; accumulated {len(rows)}")
        offset += len(quotes)

        if len(quotes) < PAGE_SIZE:
            break
        if total_hint is not None and offset >= total_hint:
            break
        time.sleep(1.5)

    if not rows:
        raise RuntimeError("US $1B+ universe is empty; Yahoo screener returned no usable equities")

    df = pd.DataFrame(rows).drop_duplicates(subset=["symbol"], keep="first")
    if "market_cap" in df.columns:
        df = df.sort_values(["market_cap", "symbol"], ascending=[False, True], na_position="last")
    else:
        df = df.sort_values("symbol")
    return df.reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-market-cap", type=int, default=DEFAULT_MIN_MARKET_CAP)
    ap.add_argument("--outdir", default="data")
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    df = build_us_1b_universe(args.min_market_cap)
    txt_path = out / "us_1b_universe.txt"
    csv_path = out / "us_1b_universe.csv"

    txt_path.write_text("\n".join(df["symbol"].tolist()) + "\n")
    df.to_csv(csv_path, index=False)

    print(f"\nUS market-cap universe >= ${args.min_market_cap:,.0f}: {len(df)} symbols")
    print(f"TXT: {txt_path}")
    print(f"CSV: {csv_path}")
    print("\nTop 20 by market cap:")
    print(df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
