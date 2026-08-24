from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

from build_universes import build_tsx

TZ = ZoneInfo('America/Toronto')
OUTROOT = Path('single_day_reversal_results')


def load_symbols(market: str) -> list[str]:
    if market == 'us':
        syms = Path('data/us_1b_universe.txt').read_text().splitlines()
    elif market == 'hk':
        syms = Path('data/hk_5b_universe.txt').read_text().splitlines()
    elif market == 'canada':
        syms = [s for s in build_tsx() if '-PR-' not in s.upper() and '-PF-' not in s.upper()]
    else:
        raise ValueError(market)
    return list(dict.fromkeys(s.strip() for s in syms if s.strip()))


def split_download(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
    out = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        lv0 = set(map(str, raw.columns.get_level_values(0)))
        if len({'Open','High','Low','Close','Volume'} & lv0) >= 3:
            for s in symbols:
                try:
                    x = raw.xs(s, axis=1, level=1, drop_level=True).dropna(how='all')
                    if not x.empty: out[s] = x
                except Exception:
                    pass
        else:
            for s in symbols:
                try:
                    x = raw.xs(s, axis=1, level=0, drop_level=True).dropna(how='all')
                    if not x.empty: out[s] = x
                except Exception:
                    pass
    elif len(symbols) == 1:
        out[symbols[0]] = raw.dropna(how='all')
    return out


def batch_daily(symbols: list[str], chunk: int = 100) -> dict[str, pd.DataFrame]:
    out = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i+chunk]
        pending = list(group)
        print(f'Batch {i+1}-{min(i+chunk,len(symbols))}/{len(symbols)}')
        for attempt in range(2):
            if not pending: break
            try:
                raw = yf.download(pending, period='6mo', interval='1d', auto_adjust=True,
                                  progress=False, threads=True, group_by='ticker')
                got = split_download(raw, pending)
                out.update(got)
                pending = [s for s in pending if s not in got]
            except Exception as exc:
                print('download error', exc)
            if pending and attempt == 0: time.sleep(2)
        time.sleep(0.8)
    return out


def completed(df: pd.DataFrame) -> pd.DataFrame:
    x = df.dropna(subset=['Open','High','Low','Close','Volume']).copy()
    if x.empty: return x
    idx = pd.DatetimeIndex(x.index)
    today = datetime.now(TZ).date()
    # Scheduled after North American close, so today's daily bar is intended to count.
    # If Yahoo has not finalized it yet, it is still usable as current close snapshot.
    x.index = idx.tz_localize(None) if idx.tz is not None else idx
    return x


def setup_row(df: pd.DataFrame, i: int):
    if i < 25: return None
    o = pd.to_numeric(df['Open'], errors='coerce')
    h = pd.to_numeric(df['High'], errors='coerce')
    l = pd.to_numeric(df['Low'], errors='coerce')
    c = pd.to_numeric(df['Close'], errors='coerce')
    v = pd.to_numeric(df['Volume'], errors='coerce')
    rng = h.iloc[i] - l.iloc[i]
    if not np.isfinite(rng) or rng <= 0: return None
    prev10low = l.iloc[i-10:i].min()
    clv = (c.iloc[i]-l.iloc[i])/rng
    body = abs(c.iloc[i]-o.iloc[i])/rng
    undercut = l.iloc[i] < prev10low
    reclaim = c.iloc[i] > prev10low
    core = undercut and reclaim and c.iloc[i] > o.iloc[i] and clv >= .70 and body >= .35
    if not core: return None
    ema20 = c.iloc[:i+1].ewm(span=20, adjust=False).mean().iloc[-1]
    vol20 = v.iloc[max(0,i-19):i+1].mean()
    prev5high = h.iloc[max(0,i-5):i].max()
    vol_expand = bool(np.isfinite(vol20) and vol20 > 0 and v.iloc[i] >= 1.10*vol20)
    ema20_reclaim = bool(l.iloc[i] < ema20 and c.iloc[i] > ema20)
    prev_high_reclaim = bool(c.iloc[i] > prev5high)
    score = 5 + int(vol_expand) + int(ema20_reclaim) + int(prev_high_reclaim)
    return {
        'reversal_date': str(df.index[i].date()), 'reversal_close': float(c.iloc[i]),
        'reversal_high': float(h.iloc[i]), 'reversal_low': float(l.iloc[i]),
        'prev5_high': float(prev5high), 'clv': float(clv), 'body_frac': float(body),
        'vol_ratio20': float(v.iloc[i]/vol20) if vol20 > 0 else np.nan,
        'vol_expand': vol_expand, 'ema20_reclaim_on_day1': ema20_reclaim,
        'prev5_high_reclaim_on_day1': prev_high_reclaim, 'score': score,
    }


def analyze_symbol(sym: str, df: pd.DataFrame, market: str):
    d = completed(df)
    if len(d) < 35: return []
    c = pd.to_numeric(d['Close'], errors='coerce')
    v = pd.to_numeric(d['Volume'], errors='coerce')
    if market == 'canada':
        # Practical liquidity screen in place of a slow per-symbol market-cap call.
        dv20 = (c*v).tail(20).mean()
        if not np.isfinite(dv20) or dv20 < 5_000_000: return []
    latest = len(d)-1
    out = []
    # WATCH = today's core reversal. CONFIRMED = a core reversal 1-3 sessions ago whose
    # first confirmation occurs today (avoid repeating the same entry on later days).
    for i in range(max(25, latest-3), latest+1):
        s = setup_row(d, i)
        if s is None: continue
        if i == latest:
            out.append({'symbol':sym, 'market':market.upper(), 'status':'WATCH', 'delay':0,
                        'entry_price':np.nan, 'stop':s['reversal_low'], 'risk_pct':np.nan,
                        'us_high_quality':False, **s})
            continue
        rev_high = s['reversal_high']; p5 = s['prev5_high']
        first_hit = None
        for j in range(i+1, min(i+4, len(d))):
            close = float(c.iloc[j])
            ema20 = float(c.iloc[:j+1].ewm(span=20,adjust=False).mean().iloc[-1])
            if close > rev_high and close > ema20:
                first_hit = j
                break
        if first_hit != latest: continue
        entry = float(c.iloc[latest]); stop = s['reversal_low']; risk = entry-stop
        if risk <= 0: continue
        risk_pct = risk/entry
        if risk_pct > .20: continue
        both_highs = entry > rev_high and entry > p5
        us_hq = bool(market == 'us' and both_highs)
        out.append({'symbol':sym, 'market':market.upper(), 'status':'CONFIRMED_ENTRY',
                    'delay':latest-i, 'entry_price':entry, 'stop':stop,
                    'risk_pct':risk_pct, 'target_1R':entry+risk,
                    'target_2R':entry+2*risk, 'both_highs':both_highs,
                    'us_high_quality':us_hq, **s})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--market', choices=['us','hk','canada','all'], default='all')
    args = ap.parse_args()
    markets = ['us','hk','canada'] if args.market == 'all' else [args.market]
    all_rows = []
    for market in markets:
        syms = load_symbols(market)
        print(market, 'universe', len(syms))
        data = batch_daily(syms)
        rows = []
        for sym in syms:
            d = data.get(sym)
            if d is None or d.empty: continue
            rows.extend(analyze_symbol(sym, d, market))
        outdir = OUTROOT/market; outdir.mkdir(parents=True, exist_ok=True)
        z = pd.DataFrame(rows)
        if not z.empty:
            order = {'CONFIRMED_ENTRY':0,'WATCH':1}
            z['_ord'] = z.status.map(order).fillna(9)
            z = z.sort_values(['_ord','score','risk_pct'], ascending=[True,False,True], na_position='last').drop(columns='_ord')
        z.to_csv(outdir/'all.csv', index=False)
        z[z.status=='WATCH'].to_csv(outdir/'watch.csv', index=False) if not z.empty else z.to_csv(outdir/'watch.csv',index=False)
        z[z.status=='CONFIRMED_ENTRY'].to_csv(outdir/'confirmed_entry.csv', index=False) if not z.empty else z.to_csv(outdir/'confirmed_entry.csv',index=False)
        summary = {
            'market':market, 'universe':len(syms), 'downloaded':len(data),
            'watch':int((z.status=='WATCH').sum()) if not z.empty else 0,
            'confirmed_entry':int((z.status=='CONFIRMED_ENTRY').sum()) if not z.empty else 0,
            'updated_et':datetime.now(TZ).isoformat(timespec='seconds')
        }
        (outdir/'summary.json').write_text(json.dumps(summary, indent=2))
        print(summary)
        all_rows.extend(rows)
    if args.market == 'all':
        OUTROOT.mkdir(exist_ok=True)
        pd.DataFrame(all_rows).to_csv(OUTROOT/'all_markets.csv', index=False)

if __name__ == '__main__':
    main()
