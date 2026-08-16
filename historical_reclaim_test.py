from __future__ import annotations

import argparse
import subprocess
import sys
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
    return pd.to_numeric(x, errors='coerce').dropna().astype(float)


def load_us_symbols():
    subprocess.run([sys.executable, 'build_universes.py', '--markets', 'us'], check=True)
    p = Path('data/us_universe.txt')
    return list(dict.fromkeys(x.strip().upper() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#')))


def frame(data, symbol, single=False):
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    need = ['Open','High','Low','Close','Volume']
    if any(c not in d.columns for c in need):
        return None
    d = d.dropna(subset=need)
    return d if len(d) >= 220 else None


def analyze_reclaim(d: pd.DataFrame, as_of: str):
    cutoff = pd.Timestamp(as_of)
    try:
        x = d.loc[pd.to_datetime(d.index).normalize() <= cutoff].copy()
    except Exception:
        return None
    if len(x) < 220:
        return None

    c,h,l,v = map(s,[x.Close,x.High,x.Low,x.Volume])
    ma20 = c.ewm(span=20, adjust=False).mean()
    ma50 = c.rolling(50).mean(); ma150 = c.rolling(150).mean(); ma200 = c.rolling(200).mean()
    h52 = h.rolling(252,min_periods=200).max(); l52=l.rolling(252,min_periods=200).min()
    av20=v.rolling(20).mean()
    if any(pd.isna(z.iloc[-1]) for z in [ma50,ma150,ma200,h52,l52,av20]):
        return None

    close=float(c.iloc[-1]); low=float(l.iloc[-1]); high=float(h.iloc[-1]); vol=float(v.iloc[-1]); avg=float(av20.iloc[-1])
    m20=float(ma20.iloc[-1]); m50=float(ma50.iloc[-1]); m150=float(ma150.iloc[-1]); m200=float(ma200.iloc[-1]); m200old=float(ma200.iloc[-21])
    hi52=float(h52.iloc[-1]); lo52=float(l52.iloc[-1])

    # Keep the same broad trend/quality gate as the Legacy scanner.
    liquid = close >= 5 and avg >= 300000 and close*avg >= 5_000_000
    trend = close > m50 > m150 > m200 and m200 > m200old and close >= 1.30*lo52 and close >= .75*hi52
    if not (liquid and trend):
        return None

    # Build historical breakout levels from prior 50-bar highs.  A level only becomes
    # eligible after price has actually broken above it, so the later signal is a RETEST/RECLAIM,
    # not a fresh breakout.
    prior50 = h.shift(1).rolling(50).max()
    breakout = (c > prior50) & (c.shift(1) <= prior50)
    bo_idx = np.flatnonzero(breakout.fillna(False).to_numpy())
    if len(bo_idx) == 0:
        return None

    # Look backward for the most recent established breakout level before today.
    today_i = len(c)-1
    eligible = [i for i in bo_idx if i < today_i]
    if not eligible:
        return None
    bi = int(eligible[-1]); level=float(prior50.iloc[bi])
    if not np.isfinite(level) or level <= 0:
        return None

    # Reclaim signal: within the last 3 sessions price trades through/under the old breakout
    # level, and today's close is back above it but not already too extended.
    recent_low=float(l.iloc[-3:].min())
    undercut_pct=(recent_low/level-1)*100
    close_above_pct=(close/level-1)*100
    reclaimed = recent_low <= level and close > level
    near_level = -3.0 <= undercut_pct <= 0 and 0 < close_above_pct <= 3.0
    not_extended = close <= m20*1.12
    candle_body=abs(close-float(s(x.Open).iloc[-1]))/close
    clean_candle=candle_body <= .10
    trigger=bool(reclaimed and near_level and not_extended and clean_candle)
    if not trigger:
        return None

    return {
        'date': as_of,
        'close': round(close,2),
        'reclaim_level': round(level,2),
        'undercut_pct': round(undercut_pct,2),
        'close_above_level_pct': round(close_above_pct,2),
        'pct_from_52w_high': round((close/hi52-1)*100,2),
        'pct_above_ema20': round((close/m20-1)*100,2),
        'relative_volume': round(vol/avg if avg else 0,2),
        'reclaim_trigger': True,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dates', default='2026-08-04,2026-08-05,2026-08-06,2026-08-07')
    ap.add_argument('--batch-size', type=int, default=100)
    ap.add_argument('--outdir', default='reclaim_test_results')
    a=ap.parse_args()
    dates=[x.strip() for x in a.dates.split(',') if x.strip()]
    parsed=[datetime.strptime(x,'%Y-%m-%d').date() for x in dates]
    start=(min(parsed)-timedelta(days=650)).isoformat(); end=(max(parsed)+timedelta(days=1)).isoformat()
    syms=load_us_symbols(); rows=[]
    for st in range(0,len(syms),a.batch_size):
        batch=syms[st:st+a.batch_size]
        print(f'Downloading {st+1}-{min(st+a.batch_size,len(syms))} of {len(syms)}')
        try:
            data=yf.download(batch,start=start,end=end,interval='1d',group_by='ticker',auto_adjust=True,threads=True,progress=False)
        except Exception as e:
            print('Batch failed',e); continue
        single=len(batch)==1
        for sym in batch:
            d=frame(data,sym,single)
            if d is None: continue
            for dt in dates:
                try:
                    r=analyze_reclaim(d,dt)
                    if r:
                        r['symbol']=sym; rows.append(r)
                except Exception as e:
                    print('skip',sym,dt,e)
        time.sleep(.35)
    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows)
    if not df.empty:
        df=df.sort_values(['date','pct_from_52w_high','close_above_level_pct'],ascending=[True,False,True])
    df.to_csv(out/'reclaim_candidates.csv',index=False)
    psx=df[df.symbol.eq('PSX')] if not df.empty and 'symbol' in df.columns else pd.DataFrame()
    psx.to_csv(out/'psx_check.csv',index=False)
    print('\n=== PSX CHECK ===')
    print('(none)' if psx.empty else psx.to_string(index=False))
    print('\n=== COUNTS ===')
    print('(none)' if df.empty else df.groupby('date').size().to_string())

if __name__=='__main__':
    main()
