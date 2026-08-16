from __future__ import annotations

import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def s(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors='coerce').astype(float)


def load_us_symbols():
    p = Path('data/us_1b_universe.txt')
    if not p.exists():
        raise FileNotFoundError('data/us_1b_universe.txt not found. Run the US $1B+ universe builder first.')
    syms = list(dict.fromkeys(
        x.strip().upper() for x in p.read_text().splitlines()
        if x.strip() and not x.startswith('#')
    ))
    print(f'US $1B+ universe: {len(syms)} symbols')
    return syms


def frame(data, symbol, single=False):
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    need = ['Open', 'High', 'Low', 'Close', 'Volume']
    if any(c not in d.columns for c in need):
        return None
    d = d.dropna(subset=need)
    return d if len(d) >= 220 else None


def download_single(symbol: str, start: str, end: str, attempts: int = 4, base_wait: float = 6.0):
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            d = yf.download(symbol, start=start, end=end, interval='1d', auto_adjust=True,
                            threads=False, progress=False)
            if d is not None and not d.empty:
                if isinstance(d.columns, pd.MultiIndex):
                    d.columns = d.columns.get_level_values(0)
                return d
            last_err = RuntimeError('empty download')
        except Exception as e:
            last_err = e
        if attempt < attempts:
            wait = base_wait * (2 ** (attempt - 1)) + random.uniform(0.5, 2.0)
            print(f'Retry {symbol}: attempt {attempt}/{attempts} failed; sleeping {wait:.1f}s')
            time.sleep(wait)
    print(f'FAILED single download {symbol}: {last_err}')
    return None


def download_batch(batch, start: str, end: str, attempts: int = 3, base_wait: float = 8.0):
    last_err = None
    for attempt in range(1, attempts + 1):
        try:
            data = yf.download(batch, start=start, end=end, interval='1d', group_by='ticker',
                               auto_adjust=True, threads=True, progress=False)
            if data is not None and not data.empty:
                return data
            last_err = RuntimeError('empty batch')
        except Exception as e:
            last_err = e
        if attempt < attempts:
            wait = base_wait * (2 ** (attempt - 1)) + random.uniform(1.0, 3.0)
            print(f'Batch retry {attempt}/{attempts}; sleeping {wait:.1f}s')
            time.sleep(wait)
    print(f'FAILED batch: {last_err}')
    return None


def congestion_metrics(c, h, l, v, breakout_index, today_index, breakout_level):
    """Score whether a congestion/base existed before breakout or is forming after breakout.

    Score 0-4, used only for ranking; it never creates or removes an ENTRY signal.
      +1 pre-breakout 20-bar range <= 12%
      +1 pre-breakout last-10-bar range contracted >= 25% vs the 20-bar range
      +1 post-breakout/current action is tight around the breakout level
      +1 recent 10-bar average volume <= 85% of 20-bar average volume
    """
    score = 0
    pre_tight = False
    pre_contract = False
    forming = False
    vol_contract = False
    pre_range_pct = np.nan
    pre10_range_pct = np.nan
    post_range_pct = np.nan
    near_level_ratio = np.nan

    pre_start = max(0, breakout_index - 20)
    pre_h = h.iloc[pre_start:breakout_index]
    pre_l = l.iloc[pre_start:breakout_index]
    if len(pre_h) >= 10:
        pre_hi = float(pre_h.max())
        pre_lo = float(pre_l.min())
        if pre_lo > 0:
            pre_range_pct = (pre_hi / pre_lo - 1.0) * 100
            pre_tight = pre_range_pct <= 12.0
            if pre_tight:
                score += 1

        last10_h = pre_h.iloc[-10:]
        last10_l = pre_l.iloc[-10:]
        if len(last10_h) >= 8:
            r10_hi = float(last10_h.max())
            r10_lo = float(last10_l.min())
            if r10_lo > 0:
                pre10_range_pct = (r10_hi / r10_lo - 1.0) * 100
                if pd.notna(pre_range_pct) and pre_range_pct > 0:
                    pre_contract = pre10_range_pct <= pre_range_pct * 0.75
                    if pre_contract:
                        score += 1

    post = slice(breakout_index + 1, today_index + 1)
    post_c = c.iloc[post]
    post_h = h.iloc[post]
    post_l = l.iloc[post]
    if len(post_c) >= 5 and breakout_level > 0:
        p_hi = float(post_h.max())
        p_lo = float(post_l.min())
        if p_lo > 0:
            post_range_pct = (p_hi / p_lo - 1.0) * 100
        near_level = ((post_c / breakout_level - 1.0).abs() <= 0.06)
        near_level_ratio = float(near_level.mean()) if len(near_level) else np.nan
        forming = bool(pd.notna(post_range_pct) and post_range_pct <= 10.0 and
                       pd.notna(near_level_ratio) and near_level_ratio >= 0.60)
        if forming:
            score += 1

    if len(v) >= 20:
        v10 = float(v.iloc[-10:].mean())
        v20 = float(v.iloc[-20:].mean())
        if v20 > 0:
            vol_contract = v10 <= v20 * 0.85
            if vol_contract:
                score += 1

    if (pre_tight or pre_contract) and forming:
        status = 'BOTH'
    elif pre_tight or pre_contract:
        status = 'PRE_BREAKOUT'
    elif forming:
        status = 'FORMING_NOW'
    else:
        status = 'NONE'

    return {
        'congestion_score': int(score),
        'congestion_status': status,
        'pre_congestion_range_pct': round(pre_range_pct, 2) if pd.notna(pre_range_pct) else np.nan,
        'pre_10d_range_pct': round(pre10_range_pct, 2) if pd.notna(pre10_range_pct) else np.nan,
        'post_breakout_range_pct': round(post_range_pct, 2) if pd.notna(post_range_pct) else np.nan,
        'near_breakout_level_ratio': round(near_level_ratio, 2) if pd.notna(near_level_ratio) else np.nan,
        'congestion_pre_tight': bool(pre_tight),
        'congestion_pre_contracting': bool(pre_contract),
        'congestion_forming_now': bool(forming),
        'congestion_volume_contracting': bool(vol_contract),
    }


def analyze_reclaim(d: pd.DataFrame, spy: pd.DataFrame, as_of: str):
    """Reproduce Trend Pullback Stock Screener v1.1 ENTRY logic as closely as possible."""
    cutoff = pd.Timestamp(as_of)
    try:
        x = d.loc[pd.to_datetime(d.index).normalize() <= cutoff].copy()
        sx = spy.loc[pd.to_datetime(spy.index).normalize() <= cutoff].copy()
    except Exception:
        return None
    if len(x) < 220 or len(sx) < 70:
        return None

    c, h, l, v, o = map(s, [x.Close, x.High, x.Low, x.Volume, x.Open])
    sc = s(sx.Close)

    ema20 = c.ewm(span=20, adjust=False).mean()
    ema50 = c.ewm(span=50, adjust=False).mean()
    sma200 = c.rolling(200).mean()
    avgvol = v.rolling(20).mean()
    avgdollar = (c * v).rolling(20).mean()
    yearhigh = h.rolling(252, min_periods=20).max()
    spy_ema20 = sc.ewm(span=20, adjust=False).mean()
    spy_ema50 = sc.ewm(span=50, adjust=False).mean()

    vals = [ema20.iloc[-1], ema50.iloc[-1], sma200.iloc[-1], avgvol.iloc[-1],
            avgdollar.iloc[-1], yearhigh.iloc[-1], spy_ema20.iloc[-1], spy_ema50.iloc[-1]]
    if any(pd.isna(z) for z in vals) or len(c) <= 63 or len(sc) <= 63:
        return None

    close = float(c.iloc[-1]); high = float(h.iloc[-1]); low = float(l.iloc[-1]); open_ = float(o.iloc[-1])
    e20 = float(ema20.iloc[-1]); e50 = float(ema50.iloc[-1]); s200 = float(sma200.iloc[-1]); hi52 = float(yearhigh.iloc[-1])
    av = float(avgvol.iloc[-1]); adv = float(avgdollar.iloc[-1])

    trend_alignment = close > e20 > e50 > s200
    ema50_rising = e50 > float(ema50.iloc[-11])
    sma200_rising = s200 > float(sma200.iloc[-21])
    strong_uptrend = bool(trend_alignment and ema50_rising and sma200_rising)
    pct_above_ema20 = ((close / e20) - 1) * 100 if e20 > 0 else np.nan
    not_overextended = bool(pd.notna(pct_above_ema20) and pct_above_ema20 <= 12.0)

    liquid = bool(close >= 10 and av >= 500_000 and adv >= 20_000_000)
    pct_below_high = ((hi52 - close) / hi52) * 100 if hi52 > 0 else np.nan
    near_year_high = bool(pd.notna(pct_below_high) and pct_below_high <= 20.0)
    stock_return = close / float(c.iloc[-64]) - 1 if float(c.iloc[-64]) > 0 else np.nan
    spy_return = float(sc.iloc[-1]) / float(sc.iloc[-64]) - 1 if float(sc.iloc[-64]) > 0 else np.nan
    relative_strength = stock_return - spy_return if pd.notna(stock_return) and pd.notna(spy_return) else np.nan
    outperforming_spy = bool(pd.notna(relative_strength) and relative_strength > 0)

    spy_close = float(sc.iloc[-1]); se20 = float(spy_ema20.iloc[-1]); se50 = float(spy_ema50.iloc[-1])
    market_pass = bool(spy_close > se20 > se50)

    prior = h.shift(1).rolling(50).max()
    threshold = prior * 1.01
    breakout = (c > threshold) & (c.shift(1) <= prior)
    bo_idx = np.flatnonzero(breakout.fillna(False).to_numpy())
    if len(bo_idx) == 0:
        return None
    today_i = len(c) - 1
    eligible = [i for i in bo_idx if i < today_i]
    if not eligible:
        return None
    bi = int(eligible[-1]); level = float(prior.iloc[bi]); bars_since = today_i - bi
    if not (1 <= bars_since <= 30) or not np.isfinite(level) or level <= 0:
        return None

    lowest_allowed = level * 0.97
    slight_undercut = bool(low < level and low >= lowest_allowed)
    reclaimed = bool(close > level)
    bullish_candle = bool(close > open_ and close >= (high + low) / 2.0)
    candle_range = high - low
    strong_bearish = bool(candle_range > 0 and close < open_ and (open_ - close) / candle_range >= 0.65)
    reclaim_trigger = bool(slight_undercut and reclaimed and bullish_candle and not strong_bearish)

    entry_candidate = bool(strong_uptrend and not_overextended and liquid and near_year_high and
                           outperforming_spy and market_pass and reclaim_trigger)
    if not entry_candidate:
        return None

    congestion = congestion_metrics(c, h, l, v, bi, today_i, level)

    result = {
        'date': as_of,
        'close': round(close, 2),
        'breakout_date': str(pd.Timestamp(x.index[bi]).date()),
        'breakout_level': round(level, 2),
        'bars_since_breakout': bars_since,
        'intraday_undercut_pct': round((low / level - 1) * 100, 2),
        'close_above_level_pct': round((close / level - 1) * 100, 2),
        'pct_below_52w_high': round(pct_below_high, 2),
        'pct_above_ema20': round(pct_above_ema20, 2),
        'rs_vs_spy_pct': round(relative_strength * 100, 2),
        'avg_volume_20d': int(av),
        'avg_dollar_volume_m': round(adv / 1_000_000, 2),
        'market_pass': market_pass,
        'entry_candidate': True,
    }
    result.update(congestion)
    return result


def add_symbol_rows(rows, sym, d, spy, dates):
    if d is None:
        return
    for dt in dates:
        try:
            r = analyze_reclaim(d, spy, dt)
            if r:
                r['symbol'] = sym
                rows.append(r)
        except Exception as e:
            print('skip', sym, dt, e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dates', default='2026-08-04,2026-08-05,2026-08-06,2026-08-07')
    ap.add_argument('--batch-size', type=int, default=40)
    ap.add_argument('--outdir', default='reclaim_test_results')
    a = ap.parse_args()
    dates = [x.strip() for x in a.dates.split(',') if x.strip()]
    parsed = [datetime.strptime(x, '%Y-%m-%d').date() for x in dates]
    start = (min(parsed) - timedelta(days=650)).isoformat(); end = (max(parsed) + timedelta(days=1)).isoformat()

    spy = download_single('SPY', start, end, attempts=5, base_wait=5)
    if spy is None or spy.empty:
        raise RuntimeError('SPY download failed after retries')

    syms = load_us_symbols()
    rows = []
    failed = []
    processed = set()

    print('=== PRIORITY PSX DOWNLOAD ===')
    psx = download_single('PSX', start, end, attempts=5, base_wait=5)
    if psx is not None:
        add_symbol_rows(rows, 'PSX', psx, spy, dates)
        processed.add('PSX')
    else:
        failed.append('PSX')

    remaining = [x for x in syms if x not in processed]
    for st in range(0, len(remaining), a.batch_size):
        batch = remaining[st:st + a.batch_size]
        print(f'Downloading {st + 1}-{min(st + a.batch_size, len(remaining))} of {len(remaining)}')
        data = download_batch(batch, start, end, attempts=3, base_wait=8)
        if data is None:
            failed.extend(batch)
        else:
            single = len(batch) == 1
            for sym in batch:
                d = frame(data, sym, single)
                if d is None:
                    failed.append(sym)
                    continue
                add_symbol_rows(rows, sym, d, spy, dates)
        time.sleep(random.uniform(1.4, 2.4))

    failed = list(dict.fromkeys(failed))
    recovered = []
    still_failed = []
    if failed:
        print(f'=== RECOVERY PASS: {len(failed)} symbols ===')
        time.sleep(20)
        for i, sym in enumerate(failed, 1):
            d = download_single(sym, start, end, attempts=3, base_wait=7)
            if d is None:
                still_failed.append(sym)
            else:
                add_symbol_rows(rows, sym, d, spy, dates)
                recovered.append(sym)
            time.sleep(random.uniform(1.0, 1.8))
            if i % 50 == 0:
                print(f'Recovery {i}/{len(failed)}; cooling down 15s')
                time.sleep(15)

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=['date', 'symbol']).sort_values(
            ['date', 'congestion_score', 'rs_vs_spy_pct', 'pct_below_52w_high'],
            ascending=[True, False, False, True])
    df.to_csv(out / 'reclaim_candidates.csv', index=False)

    psxdf = df[df.symbol.eq('PSX')] if not df.empty and 'symbol' in df.columns else pd.DataFrame()
    psxdf.to_csv(out / 'psx_check.csv', index=False)

    status = pd.DataFrame({
        'metric': ['universe', 'recovered_after_retry', 'still_failed'],
        'value': [len(syms), len(recovered), len(still_failed)]
    })
    status.to_csv(out / 'download_status.csv', index=False)
    pd.DataFrame({'symbol': still_failed}).to_csv(out / 'still_failed_symbols.csv', index=False)

    print('\n=== PSX CHECK ===')
    print('(none)' if psxdf.empty else psxdf.to_string(index=False))
    print('\n=== COUNTS ===')
    print('(none)' if df.empty else df.groupby('date').size().to_string())
    if not df.empty:
        print('\n=== TOP BY CONGESTION SCORE ===')
        cols = ['date', 'symbol', 'congestion_score', 'congestion_status', 'rs_vs_spy_pct', 'breakout_level']
        print(df[cols].groupby('date', group_keys=False).head(10).to_string(index=False))
    print(f'\nRecovered after retry: {len(recovered)}')
    print(f'Still failed: {len(still_failed)}')


if __name__ == '__main__':
    main()
