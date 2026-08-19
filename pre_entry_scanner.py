from __future__ import annotations

import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import yfinance as yf

EMA20=20; EMA50=50; SMA200=200; LOOKBACK=50; RS_LOOKBACK=63
MAX_TO_BREAKOUT=5.0; MAX_BELOW_HIGH=15.0; MIN_RS=5.0

MARKETS={
 'us': {'tz':'America/New_York','universe':Path('data/us_1b_universe.txt'),'out':Path('double_reclaim_results/us'),'benchmark':'SPY'},
 'hk': {'tz':'Asia/Hong_Kong','universe':Path('data/hk_5b_universe.txt'),'out':Path('double_reclaim_results/hk'),'benchmark':'SPY'},
 'canada': {'tz':'America/Toronto','universe':Path('data/tsx_universe.txt'),'out':Path('double_reclaim_results/canada'),'benchmark':'XIU.TO'},
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
        try:
            r=yf.download(g,period='18mo',interval='1d',auto_adjust=True,progress=False,threads=True,group_by='ticker')
            out.update(split(r,g))
        except Exception as e: print('batch failed',e)
    return out

def completed(df,tz):
    x=df.copy().dropna(subset=['Close'])
    if len(x) and pd.DatetimeIndex(x.index).date[-1]==datetime.now(ZoneInfo(tz)).date(): x=x.iloc[:-1]
    return x

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--market',choices=sorted(MARKETS),required=True); a=ap.parse_args()
    m=a.market; c=MARKETS[m]; p=c['universe']
    if not p.exists(): raise RuntimeError(f'{p} missing')
    syms=list(dict.fromkeys(x.strip().upper() for x in p.read_text().splitlines() if x.strip()))
    bench=yf.download(c['benchmark'],period='18mo',interval='1d',auto_adjust=True,progress=False)
    if isinstance(bench.columns,pd.MultiIndex): bench.columns=bench.columns.get_level_values(0)
    bench=completed(bench,c['tz'])
    br=float(bench['Close'].iloc[-1]/bench['Close'].iloc[-1-RS_LOOKBACK]-1)
    data=batch(syms)
    rows=[]
    for s,d0 in data.items():
        d=completed(d0,c['tz'])
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
        score=0
        score += 3 if dist<=1 else (2 if dist<=2.5 else 1)
        score += 2 if rs>=15 else (1 if rs>=10 else 0)
        score += 2 if below<=5 else (1 if below<=10 else 0)
        score += 1 if volume_contract else 0
        score += 1 if range_contract else 0
        score += 1 if above20<=10 else 0
        grade='A' if score>=8 else ('B' if score>=6 else 'C')
        rows.append({'symbol':s,'setup':'PRE_ENTRY','grade':grade,'score':score,'current_price':round(px,3),'breakout_level':round(resistance,3),'distance_to_breakout_pct':round(dist,2),'ema20':round(e20,3),'ema50':round(e50,3),'sma200':round(s200,3),'pct_above_ema20':round(above20,2),'rs_pct':round(rs,2),'pct_below_52w_high':round(below,2),'volume_contracting':volume_contract,'range_contracting':range_contract})
    out=pd.DataFrame(rows)
    c['out'].mkdir(parents=True,exist_ok=True)
    fn=c['out']/f'{m}_pre_entry_watch_today.csv'
    if not out.empty: out=out.sort_values(['grade','score','distance_to_breakout_pct','rs_pct'],ascending=[True,False,True,False])
    out.to_csv(fn,index=False)
    print('\nPRE_ENTRY',len(out)); print(out.head(30).to_string(index=False) if not out.empty else 'No candidates')
if __name__=='__main__': main()
