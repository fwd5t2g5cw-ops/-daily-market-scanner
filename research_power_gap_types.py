from __future__ import annotations

import time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

SRC=Path('research/pre_gap_oos/events.csv')
OUT=Path('research/power_gap_types'); OUT.mkdir(parents=True,exist_ok=True)
START=pd.Timestamp('2022-01-01'); END=pd.Timestamp('2025-12-31')
GAP=15.0; PRE=60


def download(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2021-01-01',end='2026-01-10',interval='1d',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>=PRE+30: return d
        except Exception as e: print(s,'retry',k+1,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()


def feat(d,i):
    if i<PRE: return None
    w=d.iloc[i-PRE+1:i+1]
    c=w.Close.astype(float); h=w.High.astype(float); l=w.Low.astype(float)
    allc=d.iloc[:i+1].Close.astype(float)
    e20=allc.ewm(span=20,adjust=False).mean(); e50=allc.ewm(span=50,adjust=False).mean()
    last=float(c.iloc[-1]); hi=float(h.max()); peak=float(c.max())
    r10=(float(h.tail(10).max())/float(l.tail(10).min())-1)*100
    r20=(float(h.tail(20).max())/float(l.tail(20).min())-1)*100
    ret60=(last/float(c.iloc[0])-1)*100
    dd=float((c/c.cummax()-1).min()*100)
    dist=(hi-last)/hi*100
    pb=(peak-last)/peak*100
    slope=(float(e20.iloc[-1])/float(e20.iloc[-11])-1)*100
    return dict(ret60=ret60,maxdd60=dd,dist60high=dist,pullback60=pb,range10vs20=r10/r20 if r20 else np.nan,
                ema20gt50=bool(e20.iloc[-1]>e50.iloc[-1]),closegt20=bool(last>e20.iloc[-1]),ema20slope10=slope)


def classify(f):
    if f['dist60high']<=10 and f['ema20gt50'] and f['closegt20'] and f['range10vs20']<=0.75:
        return 'HIGH_TIGHT'
    if f['dist60high']<=10 and f['ema20gt50'] and f['closegt20']:
        return 'HIGH_LOOSE'
    if f['dist60high']<=25 and f['maxdd60']>=-20 and f['ret60']>=-5:
        return 'BASE_ACCUM'
    return 'REVERSAL_DEPRESSED'


def main():
    base=pd.read_csv(SRC)
    syms=sorted(base.symbol.dropna().astype(str).unique())
    rows=[]
    for n,s in enumerate(syms,1):
        print(n,'/',len(syms),s)
        d=download(s)
        if d.empty: continue
        idx=pd.DatetimeIndex(d.index).tz_localize(None)
        op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy()
        gp=np.r_[np.nan,(op[1:]/cl[:-1]-1)*100]
        gap_idx=[i for i in range(PRE,len(d)) if START<=idx[i]<=END and gp[i]>=GAP]
        for i in gap_idx:
            f=feat(d,i-1)
            if f: rows.append({'symbol':s,'group':'POWER_GAP','date':idx[i].date(),'gap_pct':gp[i],'chart_type':classify(f),**f})
            # three same-stock controls 30-150 sessions earlier, no >=15% gap in next 10 sessions
            cand=[]
            for k in range(max(PRE,i-150),max(PRE,i-30)+1):
                future=gp[k+1:min(k+11,len(gp))]
                if len(future) and np.nanmax(future)<GAP: cand.append(k)
            if cand:
                picks=np.unique(np.linspace(0,len(cand)-1,min(3,len(cand))).round().astype(int))
                for z in picks:
                    k=cand[int(z)]; cf=feat(d,k)
                    if cf: rows.append({'symbol':s,'group':'CONTROL','date':idx[k].date(),'gap_pct':0.0,'chart_type':classify(cf),**cf})
    ev=pd.DataFrame(rows); ev.to_csv(OUT/'events.csv',index=False)
    if ev.empty: return
    g=ev[ev.group=='POWER_GAP']; c=ev[ev.group=='CONTROL']
    types=['HIGH_TIGHT','HIGH_LOOSE','BASE_ACCUM','REVERSAL_DEPRESSED']
    lines=['# Power-Gap Chart-Type Research','',f'- Window: **{START.date()} to {END.date()}**',f'- Power gaps >=15%: **{len(g)}**',f'- Same-stock controls: **{len(c)}**','',
           '## Chart-type distribution','', '| Type | Power gaps | Power-gap rate | Controls | Control rate | Lift |','|---|---:|---:|---:|---:|---:|']
    for t in types:
        gh=int((g.chart_type==t).sum()); ch=int((c.chart_type==t).sum())
        gr=gh/len(g) if len(g) else 0; cr=ch/len(c) if len(c) else 0; lift=gr/cr if cr else np.inf
        lines.append(f'| {t} | {gh} | {gr:.0%} | {ch} | {cr:.0%} | {lift:.2f}x |')
    lines += ['', '## Power-gap examples','', '| Symbol | Date | Gap | Type | Dist to 60d high | Range10/20 | EMA20 slope10 |','|---|---|---:|---|---:|---:|---:|']
    for _,r in g.sort_values('gap_pct',ascending=False).iterrows():
        lines.append(f"| {r.symbol} | {r.date} | {r.gap_pct:.1f}% | {r.chart_type} | {r.dist60high:.1f}% | {r.range10vs20:.2f} | {r.ema20slope10:.1f}% |")
    lines += ['', '## Interpretation','', '- HIGH_TIGHT = near the 60-session high, EMA20>EMA50, close>EMA20, and 10-day range compressed vs 20-day range.', '- HIGH_LOOSE = near the high and in trend, but not tightly compressed.', '- BASE_ACCUM = within 25% of high, limited drawdown, roughly flat/up over 60 sessions.', '- REVERSAL_DEPRESSED = everything else; this includes low-position/reversal/news-repricing structures.', '- A useful pre-gap scanner needs a type with meaningfully higher frequency in power gaps than same-stock controls, not merely a visually attractive pattern.', '']
    (OUT/'report.md').write_text('\n'.join(lines))
    print('\n'.join(lines))

if __name__=='__main__': main()
