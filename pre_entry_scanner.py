from __future__ import annotations

import argparse
import time
from pathlib import Path
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import yfinance as yf
from yfinance import EquityQuery

from build_universes import build_tsx

EMA20=20; EMA50=50; SMA200=200; LOOKBACK=50; RS_LOOKBACK=63
MAX_TO_BREAKOUT=5.0; MAX_BELOW_HIGH=15.0; MIN_RS=5.0
MAX_ABOVE_EMA20=8.0
A_GRADE_MAX_ABOVE_EMA20=6.0
MIN_JAPAN_MARKET_CAP_USD=1_000_000_000
COMPRESSION_MAX_TO_BREAKOUT=2.0
COMPRESSION_MAX_BELOW_HIGH=10.0
COMPRESSION_MIN_SCORE=7

MARKETS={
 'us': {'tz':'America/New_York','close':dt_time(16,0),'universe':Path('data/us_1b_universe.txt'),'out':Path('double_reclaim_results/us'),'benchmark':'SPY'},
 'hk': {'tz':'Asia/Hong_Kong','close':dt_time(16,0),'universe':Path('data/hk_5b_universe.txt'),'out':Path('double_reclaim_results/hk'),'benchmark':'SPY'},
 'canada': {'tz':'America/Toronto','close':dt_time(16,0),'universe':None,'out':Path('double_reclaim_results/canada'),'benchmark':'XIU.TO'},
 'japan': {'tz':'Asia/Tokyo','close':dt_time(15,30),'universe':None,'out':Path('double_reclaim_results/japan'),'benchmark':'1306.T'},
}

def split(raw, syms):
    out={}
    if raw is None or raw.empty: return out
    if isinstance(raw.columns,pd.MultiIndex):
        for s in syms:
            try:
                x=raw.xs(s,axis=1,level=1,drop_level=True).dropna(how='all')
                if not x.empty: out[s]=x
            except Exception:
                try:
                    x=raw.xs(s,axis=1,level=0,drop_level=True).dropna(how='all')
                    if not x.empty: out[s]=x
                except Exception: pass
    elif len(syms)==1: out[syms[0]]=raw.dropna(how='all')
    return out

def batch(syms):
    out={}
    for i in range(0,len(syms),180):
        g=syms[i:i+180]
        print('daily',i+1,'-',min(i+180,len(syms)),'/',len(syms))
        pending=list(g)
        for attempt in range(1,3):
            if not pending: break
            try:
                r=yf.download(pending,period='18mo',interval='1d',auto_adjust=True,progress=False,threads=True,group_by='ticker')
                got=split(r,pending)
                out.update(got)
                pending=[s for s in pending if s not in got]
            except Exception as e:
                print('batch failed',e)
            if pending and attempt==1:
                time.sleep(2)
        if pending:
            print('daily unavailable after retry',len(pending),pending[:15])
        time.sleep(.4)
    return out

def completed(df,tz,market_close):
    """Keep today's daily bar after the local cash market has closed.

    Before the close (for example the 3PM US run), Yahoo's current daily bar is
    still in progress, so it is removed. After the close (for example the 6PM
    run), the completed current-session bar is retained. The old behaviour
    always removed today's bar and caused post-close PRE-ENTRY scans to lag by
    one trading day.
    """
    if df is None or df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    x=df.copy().dropna(subset=['Close'])
    if not len(x): return x
    now=datetime.now(ZoneInfo(tz))
    last_date=pd.DatetimeIndex(x.index).date[-1]
    if last_date==now.date() and now.time()<market_close:
        x=x.iloc[:-1]
    return x

def _download_daily_retry(symbol, *, period='18mo', attempts=5):
    for attempt in range(1, attempts+1):
        try:
            raw=yf.download(symbol,period=period,interval='1d',auto_adjust=True,progress=False,threads=False)
            if raw is not None and not raw.empty:
                if isinstance(raw.columns,pd.MultiIndex): raw.columns=raw.columns.get_level_values(0)
                if 'Close' in raw.columns and raw['Close'].notna().sum()>0:
                    return raw
        except Exception as exc:
            print(f'{symbol} benchmark attempt {attempt}/{attempts} failed:',exc)
        if attempt<attempts:
            delay=min(4*(2**(attempt-1)),30)
            print(f'{symbol} benchmark unavailable; retry in {delay}s')
            time.sleep(delay)
    return pd.DataFrame()

def _load_benchmark(symbol,tz,market_close):
    raw=_download_daily_retry(symbol)
    bench=completed(raw,tz,market_close)
    if len(bench) < RS_LOOKBACK+2:
        raise RuntimeError(f'{symbol} benchmark unavailable after retries (need at least {RS_LOOKBACK+2} completed bars, got {len(bench)})')
    close=pd.to_numeric(bench['Close'],errors='coerce').dropna()
    if len(close) < RS_LOOKBACK+2:
        raise RuntimeError(f'{symbol} benchmark close history insufficient after cleaning')
    ret=float(close.iloc[-1]/close.iloc[-1-RS_LOOKBACK]-1)
    print(f'{symbol} benchmark loaded: {len(close)} bars; {RS_LOOKBACK}d return={ret*100:.2f}%')
    return ret

def _compression_score(dist, below, above20, rs, volume_contract, range_contract):
    """Score CSX-style pre-breakout compression independently of reclaim score."""
    score=0
    score += 3 if dist<=1 else (2 if dist<=2 else (1 if dist<=3 else 0))
    score += 2 if below<=5 else (1 if below<=10 else 0)
    score += 2 if above20<=2 else (1 if above20<=4 else 0)
    score += 1 if rs>=5 else 0
    score += 1 if rs>=10 else 0
    score += 1 if volume_contract else 0
    score += 1 if range_contract else 0
    return score

def _compression_grade(score):
    if score>=8: return 'A'
    if score>=6: return 'B'
    return 'C'

def _load_japan_usd1b():
    fxraw=_download_daily_retry('JPY=X',period='5d')
    if fxraw is None or fxraw.empty: raise RuntimeError('USD/JPY unavailable for Japan PRE-ENTRY')
    close=fxraw['Close']
    if isinstance(close,pd.DataFrame): close=close.iloc[:,0]
    fx=float(pd.to_numeric(close,errors='coerce').dropna().iloc[-1])
    floor=MIN_JAPAN_MARKET_CAP_USD*fx
    print(f'Japan PRE-ENTRY USDJPY={fx:.4f}; JPY floor={floor:,.0f}')
    q=EquityQuery('and',[EquityQuery('eq',['region','jp']),EquityQuery('gte',['intradaymarketcap',floor])])
    syms=[]; offset=0; size=250
    while True:
        resp=None; last=None
        for attempt in range(4):
            try:
                resp=yf.screen(q,offset=offset,size=size,sortField='ticker',sortAsc=True); break
            except Exception as exc:
                last=exc; time.sleep(3*(2**attempt))
        if resp is None: raise RuntimeError(f'Japan PRE-ENTRY universe failed: {last}')
        quotes=resp.get('quotes') or []
        if not quotes: break
        for row in quotes:
            s=str(row.get('symbol') or '').strip().upper()
            cap=row.get('marketCap',row.get('intradaymarketcap'))
            try: cap=float(cap)
            except Exception: continue
            if s.endswith('.T') and cap>=floor: syms.append(s)
        offset+=len(quotes)
        if len(quotes)<size: break
        time.sleep(.5)
    syms=list(dict.fromkeys(syms))
    if not syms: raise RuntimeError('No Japan USD 1B+ symbols for PRE-ENTRY')
    print('Japan PRE-ENTRY universe',len(syms))
    return syms

def _load_symbols(m):
    if m=='canada':
        syms=[s for s in build_tsx() if '-PR-' not in s.upper() and '-PF-' not in s.upper()]
        return list(dict.fromkeys(syms))
    if m=='japan': return _load_japan_usd1b()
    p=MARKETS[m]['universe']
    if p is None or not p.exists(): raise RuntimeError(f'{p} missing')
    return list(dict.fromkeys(x.strip().upper() for x in p.read_text().splitlines() if x.strip()))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--market',choices=sorted(MARKETS),required=True); a=ap.parse_args()
    m=a.market; c=MARKETS[m]
    syms=_load_symbols(m)
    print(m,'PRE-ENTRY universe',len(syms))
    br=_load_benchmark(c['benchmark'],c['tz'],c['close'])
    data=batch(syms)
    rows=[]
    for s,d0 in data.items():
        d=completed(d0,c['tz'],c['close'])
        if len(d)<260: continue
        close=pd.to_numeric(d['Close'],errors='coerce'); high=pd.to_numeric(d['High'],errors='coerce'); low=pd.to_numeric(d['Low'],errors='coerce'); vol=pd.to_numeric(d['Volume'],errors='coerce')
        px=float(close.iloc[-1]); e20=float(close.ewm(span=20,adjust=False).mean().iloc[-1]); e50s=close.ewm(span=50,adjust=False).mean(); e50=float(e50s.iloc[-1]); s200s=close.rolling(200).mean(); s200=float(s200s.iloc[-1])
        strong=px>e20>e50>s200 and e50>float(e50s.iloc[-11]) and s200>float(s200s.iloc[-21])
        if not strong: continue
        resistance=float(high.shift(1).rolling(LOOKBACK).max().iloc[-1])
        if not np.isfinite(resistance) or resistance<=0: continue
        dist=(resistance-px)/resistance*100
        if dist<0 or dist>MAX_TO_BREAKOUT: continue
        high52=float(high.tail(252).max()); below=(high52-px)/high52*100
        if below>MAX_BELOW_HIGH: continue
        sr=float(px/close.iloc[-1-RS_LOOKBACK]-1); rs=(sr-br)*100
        if rs<MIN_RS: continue
        av20=float(vol.tail(20).mean()); av10=float(vol.tail(10).mean()); volume_contract=bool(av20>0 and av10<=av20*.90)
        r20=(float(high.tail(20).max())/float(low.tail(20).min())-1)*100
        r10=(float(high.tail(10).max())/float(low.tail(10).min())-1)*100
        range_contract=bool(r20>0 and r10<=r20*.75)
        above20=(px/e20-1)*100
        if above20>MAX_ABOVE_EMA20: continue
        score=0
        score += 3 if dist<=1 else (2 if dist<=2.5 else 1)
        score += 2 if rs>=15 else (1 if rs>=10 else 0)
        score += 2 if below<=5 else (1 if below<=10 else 0)
        score += 1 if volume_contract else 0
        score += 1 if range_contract else 0
        score += 2 if above20<=4 else (1 if above20<=6 else 0)
        if score>=8 and above20<=A_GRADE_MAX_ABOVE_EMA20: grade='A'
        elif score>=6: grade='B'
        else: grade='C'

        compression_score=_compression_score(dist,below,above20,rs,volume_contract,range_contract)
        compression_grade=_compression_grade(compression_score)
        compression_setup=bool(
            dist<=COMPRESSION_MAX_TO_BREAKOUT and
            below<=COMPRESSION_MAX_BELOW_HIGH and
            above20>=0 and above20<=4 and
            rs>=MIN_RS and
            compression_score>=COMPRESSION_MIN_SCORE
        )

        rows.append({
            'symbol':s,'setup':'PRE_ENTRY','grade':grade,'score':score,
            'compression_setup':compression_setup,'compression_grade':compression_grade,'compression_score':compression_score,
            'current_price':round(px,3),'breakout_level':round(resistance,3),'distance_to_breakout_pct':round(dist,2),
            'ema20':round(e20,3),'ema50':round(e50,3),'sma200':round(s200,3),'pct_above_ema20':round(above20,2),
            'rs_pct':round(rs,2),'pct_below_52w_high':round(below,2),
            'volume_contracting':volume_contract,'range_contracting':range_contract
        })
    out=pd.DataFrame(rows)
    c['out'].mkdir(parents=True,exist_ok=True)
    fn=c['out']/f'{m}_pre_entry_watch_today.csv'
    comp_fn=c['out']/f'{m}_pre_breakout_compression_today.csv'
    if not out.empty:
        out=out.sort_values(['grade','score','distance_to_breakout_pct','rs_pct'],ascending=[True,False,True,False])
    out.to_csv(fn,index=False)

    if not out.empty and 'compression_setup' in out.columns:
        comp=out[out['compression_setup']].copy()
        if not comp.empty:
            comp=comp.sort_values(['compression_grade','compression_score','distance_to_breakout_pct','rs_pct'],ascending=[True,False,True,False])
    else:
        comp=pd.DataFrame(columns=out.columns)
    comp.to_csv(comp_fn,index=False)

    print('\nPRE_ENTRY',len(out)); print(out.head(30).to_string(index=False) if not out.empty else 'No candidates')
    print('\nPRE_BREAKOUT_COMPRESSION',len(comp)); print(comp.head(30).to_string(index=False) if not comp.empty else 'No candidates')
if __name__=='__main__': main()
