from __future__ import annotations
import time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

SRC=Path('research/pre_gap_oos/events.csv')
OUT=Path('research/high_tight_predictive'); OUT.mkdir(parents=True,exist_ok=True)
START=pd.Timestamp('2022-01-01'); END=pd.Timestamp('2025-12-31'); PRE=60; GAP=15.0; H=10


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2021-01-01',end='2026-01-15',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>PRE+H: return d
        except Exception: pass
        time.sleep(2*(k+1))
    return pd.DataFrame()


def is_high_tight(d,i):
    if i<PRE: return False
    w=d.iloc[i-PRE+1:i+1]
    c=w.Close.astype(float); h=w.High.astype(float); l=w.Low.astype(float)
    allc=d.iloc[:i+1].Close.astype(float)
    e20=allc.ewm(span=20,adjust=False).mean(); e50=allc.ewm(span=50,adjust=False).mean()
    last=float(c.iloc[-1]); hi=float(h.max())
    r10=(float(h.tail(10).max())/float(l.tail(10).min())-1)*100
    r20=(float(h.tail(20).max())/float(l.tail(20).min())-1)*100
    return bool((hi-last)/hi*100<=10 and e20.iloc[-1]>e50.iloc[-1] and last>e20.iloc[-1] and r20>0 and r10/r20<=0.75)


def main():
    syms=sorted(pd.read_csv(SRC).symbol.dropna().astype(str).unique())
    rows=[]
    for n,s in enumerate(syms,1):
        print(n,'/',len(syms),s)
        d=dl(s)
        if d.empty: continue
        idx=pd.DatetimeIndex(d.index).tz_localize(None)
        op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy(); gp=np.r_[np.nan,(op[1:]/cl[:-1]-1)*100]
        for i in range(PRE,len(d)-H):
            if not (START<=idx[i]<=END): continue
            ht=is_high_tight(d,i)
            future=gp[i+1:i+H+1]
            hit=bool(np.nanmax(future)>=GAP)
            rows.append({'symbol':s,'date':idx[i].date(),'high_tight':ht,'power_gap_next10':hit,'max_gap_next10':float(np.nanmax(future))})
    x=pd.DataFrame(rows); x.to_csv(OUT/'daily_signals.csv',index=False)
    ht=x[x.high_tight]; no=x[~x.high_tight]
    p_ht=ht.power_gap_next10.mean() if len(ht) else 0; p_no=no.power_gap_next10.mean() if len(no) else 0
    lift=p_ht/p_no if p_no else np.inf
    # Collapse repeated signals into episodes: first HIGH_TIGHT day after >=10 non-HT days
    eps=[]
    for s,g in x.groupby('symbol'):
        g=g.sort_values('date').reset_index(drop=True)
        last=-999
        for i,r in g.iterrows():
            if r.high_tight and i-last>10:
                eps.append(r)
                last=i
            elif r.high_tight:
                last=i
    ep=pd.DataFrame(eps)
    ep_rate=ep.power_gap_next10.mean() if len(ep) else 0
    lines=['# HIGH_TIGHT Predictive Validation','',f'- Window: **{START.date()} to {END.date()}**',f'- Symbols: **{len(syms)}**',f'- All eligible stock-days: **{len(x)}**',f'- HIGH_TIGHT stock-days: **{len(ht)}**','',
           f'- Power gap >=15% within next 10 sessions after HIGH_TIGHT: **{p_ht:.2%}**',f'- Same outcome on non-HIGH_TIGHT stock-days: **{p_no:.2%}**',f'- Relative lift: **{lift:.2f}x**','',
           f'- Non-overlapping HIGH_TIGHT episodes: **{len(ep)}**',f'- Episode hit rate within next 10 sessions: **{ep_rate:.2%}**','',
           '## Interpretation','', '- This is the key forward-style test: stand on each historical day, identify HIGH_TIGHT using only past data, then ask whether a >=15% opening gap occurs in the next 10 sessions.', '- A visually appealing pattern is only useful if the forward hit rate and lift are meaningfully above the ordinary stock-day baseline.', '']
    (OUT/'report.md').write_text('\n'.join(lines)); print('\n'.join(lines))

if __name__=='__main__': main()
