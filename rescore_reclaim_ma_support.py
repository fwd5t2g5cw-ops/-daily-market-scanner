from __future__ import annotations

import time
from pathlib import Path
from datetime import timedelta

import pandas as pd
import yfinance as yf

INPUT = Path('data/reclaim_candidates_aug4_7.csv')
OUTDIR = Path('reclaim_rescore_results')


def score_ma(distance_pct: float) -> int:
    if pd.isna(distance_pct):
        return 0
    if 0 <= distance_pct <= 2:
        return 2
    if 2 < distance_pct <= 5:
        return 1
    return 0


def extract_symbol(data: pd.DataFrame, symbol: str):
    try:
        d = data[symbol].copy()
    except Exception:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    if 'Close' not in d.columns:
        return None
    d = d.dropna(subset=['Close'])
    return d if len(d) >= 220 else None


def main():
    df = pd.read_csv(INPUT).drop_duplicates(subset=['date', 'symbol']).copy()
    df['date'] = pd.to_datetime(df['date'])
    symbols = sorted(df['symbol'].unique())

    start = (df['date'].min() - timedelta(days=650)).date().isoformat()
    end = (df['date'].max() + timedelta(days=1)).date().isoformat()

    cache = {}
    failed = []
    batch_size = 30

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        print(f'Downloading candidate batch {i+1}-{min(i+batch_size, len(symbols))} of {len(symbols)}')
        try:
            data = yf.download(batch, start=start, end=end, interval='1d', group_by='ticker',
                               auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print('Batch failed:', e)
            failed.extend(batch)
            time.sleep(5)
            continue
        for sym in batch:
            d = extract_symbol(data, sym)
            if d is None:
                failed.append(sym)
            else:
                cache[sym] = d
        time.sleep(2)

    # Small retry pass only for missed candidate symbols.
    for sym in list(dict.fromkeys(failed)):
        if sym in cache:
            continue
        try:
            d = yf.download(sym, start=start, end=end, interval='1d', auto_adjust=True,
                            threads=False, progress=False)
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            if d is not None and not d.empty and len(d.dropna(subset=['Close'])) >= 220:
                cache[sym] = d.dropna(subset=['Close'])
        except Exception as e:
            print('Retry failed', sym, e)
        time.sleep(1)

    rows = []
    for _, r in df.iterrows():
        sym = r['symbol']
        d = cache.get(sym)
        if d is None:
            continue
        as_of = pd.Timestamp(r['date']).normalize()
        x = d.loc[pd.to_datetime(d.index).normalize() <= as_of].copy()
        if len(x) < 220:
            continue

        c = pd.to_numeric(x['Close'], errors='coerce').astype(float)
        ema20 = c.ewm(span=20, adjust=False).mean().iloc[-1]
        ema50 = c.ewm(span=50, adjust=False).mean().iloc[-1]
        sma200 = c.rolling(200).mean().iloc[-1]
        close = float(c.iloc[-1])

        d20 = (close / ema20 - 1) * 100 if ema20 > 0 else float('nan')
        d50 = (close / ema50 - 1) * 100 if ema50 > 0 else float('nan')
        d200 = (close / sma200 - 1) * 100 if sma200 > 0 else float('nan')

        s20 = score_ma(d20)
        s50 = score_ma(d50)
        s200 = score_ma(d200)
        near_count = sum(0 <= z <= 5 for z in [d20, d50, d200] if pd.notna(z))
        cluster = 1 if near_count >= 2 else 0
        ma_support = s20 + s50 + s200 + cluster
        total_setup = int(r['congestion_score']) + ma_support

        out = r.to_dict()
        out.update({
            'ema20': round(float(ema20), 2),
            'ema50': round(float(ema50), 2),
            'sma200': round(float(sma200), 2),
            'ema20_distance_pct': round(float(d20), 2),
            'ema50_distance_pct': round(float(d50), 2),
            'sma200_distance_pct': round(float(d200), 2),
            'ema20_support_score': s20,
            'ema50_support_score': s50,
            'sma200_support_score': s200,
            'support_cluster_bonus': cluster,
            'ma_support_score': ma_support,
            'total_setup_score': total_setup,
        })
        rows.append(out)

    outdf = pd.DataFrame(rows)
    if outdf.empty:
        raise RuntimeError('No candidates could be rescored')

    outdf['date'] = pd.to_datetime(outdf['date']).dt.strftime('%Y-%m-%d')
    outdf = outdf.sort_values(
        ['date', 'total_setup_score', 'congestion_score', 'ma_support_score', 'rs_vs_spy_pct', 'pct_below_52w_high'],
        ascending=[True, False, False, False, False, True]
    )
    outdf['rank'] = outdf.groupby('date').cumcount() + 1

    OUTDIR.mkdir(exist_ok=True)
    outdf.to_csv(OUTDIR / 'rescored_all.csv', index=False)
    outdf[outdf['rank'] <= 30].to_csv(OUTDIR / 'top30_by_date.csv', index=False)

    failed_final = sorted(set(symbols) - set(cache))
    pd.DataFrame({'symbol': failed_final}).to_csv(OUTDIR / 'failed_symbols.csv', index=False)

    print('\n=== TOP 30 BY DATE ===')
    cols = ['date','rank','symbol','total_setup_score','congestion_score','ma_support_score',
            'ema20_distance_pct','ema50_distance_pct','sma200_distance_pct','rs_vs_spy_pct']
    print(outdf[outdf['rank'] <= 30][cols].to_string(index=False))
    print(f'\nCandidates: {len(df)} | Unique symbols: {len(symbols)} | Failed: {len(failed_final)}')


if __name__ == '__main__':
    main()
