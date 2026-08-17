from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

import pandas as pd
import yfinance as yf
from yfinance import EquityQuery

from build_universes import build_hk

MIN_MARKET_CAP = 5_000_000_000  # HKD 5B
PAGE_SIZE = 250
OUTDIR = Path('data')


def _normalize_symbol(symbol: str) -> str:
    s = str(symbol or '').strip().upper()
    if not s:
        return ''
    if s.endswith('.HK'):
        return s
    try:
        n = int(float(s))
        return f'{n:04d}.HK'
    except Exception:
        return s


def _screen_hk() -> pd.DataFrame:
    query = EquityQuery(
        'and',
        [
            EquityQuery('eq', ['region', 'hk']),
            EquityQuery('gte', ['intradaymarketcap', MIN_MARKET_CAP]),
        ],
    )
    rows = []
    offset = 0
    while True:
        last_error = None
        response = None
        for attempt in range(4):
            try:
                response = yf.screen(
                    query,
                    offset=offset,
                    size=PAGE_SIZE,
                    sortField='ticker',
                    sortAsc=True,
                )
                break
            except Exception as exc:
                last_error = exc
                delay = 3 * (2 ** attempt)
                print(f'HK screen offset={offset} failed ({exc}); retry in {delay}s')
                time.sleep(delay)
        if response is None:
            raise RuntimeError(f'HK Yahoo screener failed: {last_error}')

        quotes = response.get('quotes') or []
        if not quotes:
            break
        for q in quotes:
            sym = _normalize_symbol(q.get('symbol'))
            if not sym.endswith('.HK'):
                continue
            cap = q.get('marketCap')
            if cap is None:
                cap = q.get('intradaymarketcap')
            try:
                cap = float(cap)
            except Exception:
                cap = None
            if cap is None or cap < MIN_MARKET_CAP:
                continue
            rows.append({
                'symbol': sym,
                'market_cap_hkd': round(cap),
                'market_cap_hkd_bn': round(cap / 1e9, 2),
                'name': q.get('shortName') or q.get('longName') or q.get('displayName') or '',
            })
        print(f'HK screen offset {offset}: {len(quotes)} quotes, kept {len(rows)}')
        offset += len(quotes)
        if len(quotes) < PAGE_SIZE:
            break
        time.sleep(1)

    if not rows:
        raise RuntimeError('Yahoo HK screener returned no usable HKD 5B+ equities')
    return pd.DataFrame(rows).drop_duplicates('symbol')


def _one_cap(symbol: str):
    try:
        cap = yf.Ticker(symbol).fast_info.market_cap
        if cap is None:
            return None
        cap = float(cap)
        if cap >= MIN_MARKET_CAP:
            return {'symbol': symbol, 'market_cap_hkd': round(cap), 'market_cap_hkd_bn': round(cap/1e9, 2), 'name': ''}
    except Exception:
        return None
    return None


def _fallback_parallel() -> pd.DataFrame:
    symbols = build_hk()
    print('Fallback: checking HKEX universe in parallel:', len(symbols))
    rows = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {ex.submit(_one_cap, s): s for s in symbols}
        for i, fut in enumerate(as_completed(futures), 1):
            row = fut.result()
            if row:
                rows.append(row)
            if i % 100 == 0:
                print('Market-cap checked', i, '/', len(symbols), '| kept', len(rows))
    if not rows:
        raise RuntimeError('Fallback HK market-cap scan returned no HKD 5B+ equities')
    return pd.DataFrame(rows).drop_duplicates('symbol')


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    try:
        df = _screen_hk()
        print('Used Yahoo EquityQuery screener')
    except Exception as exc:
        print('Yahoo EquityQuery unavailable for HK:', exc)
        df = _fallback_parallel()

    df = df.sort_values(['market_cap_hkd', 'symbol'], ascending=[False, True]).reset_index(drop=True)
    txt = OUTDIR / 'hk_5b_universe.txt'
    csv = OUTDIR / 'hk_5b_universe.csv'
    txt.write_text('\n'.join(df['symbol'].tolist()) + '\n')
    df.to_csv(csv, index=False)
    print(f'HK market-cap universe >= HK${MIN_MARKET_CAP:,.0f}: {len(df)} symbols')
    print(df.head(30).to_string(index=False))


if __name__ == '__main__':
    main()
