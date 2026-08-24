from __future__ import annotations

from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/pre_gap_oos'); OUT.mkdir(parents=True,exist_ok=True)
GAP=4.0; PRE=60
HOLDOUT_END=pd.Timestamp('2025-08-31')
HOLDOUT_START=pd.Timestamp('2023-01-01')


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2022-01-01',end='2025-09-15',interval='1d',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>=300:return d
        except Exception as e: print(s,k+1,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()


def feat(d,k):
    if k<PRE or k<60:return None
    x=d.iloc[:k+1]; w=x.iloc[-PRE:]
    c=x.Close.astype(float); h=x.High.astype(float); l=x.Low.astype(float)
    e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean()
    last=float(c.iloc[-1]); high60=float(w.High.max()); closehigh=float(w.Close.max())
    r10=(float(w.High.tail(10).max())/float(w.Low.tail(10).min())-1)*100
    r20=(float(w.High.tail(20).max())/float(w.Low.tail(20).min())-1)*100
    vals={
      'ema20_gt_ema50':bool(e20.iloc[-1]>e50.iloc[-1]),
      'trend_stack':bool(last>e20.iloc[-1]>e50.iloc[-1]),
      'shallow_pullback_8':bool((closehigh-last)/closehigh*100<=8),
      'near_high_5':bool((high60-last)/high60*100<=5),
      'range_contract_075':bool(r20>0 and r10/r20<=.75),
      'ema20_slope_gt1':bool((float(e20.iloc[-1])/float(e20.iloc[-11])-1)*100>=1.0),
    }
    vals['score']=sum(int(vals[x]) for x in vals)
    return vals


def main():
    current=pd.read_csv('research/pre_gap/events.csv')
    syms=sorted(current.symbol.unique())
    print('holdout symbols',len(syms))
    rows=[]
    for ii,s in enumerate(syms,1):
        print(ii,'/',len(syms),s); d=dl(s)
        if d.empty: continue
        idx=pd.DatetimeIndex(d.index).tz_localize(None); op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy(); gp=np.r_[np.nan,(op[1:]/cl[:-1]-1)*100]
        gaps=[j for j in range(1,len(d)) if HOLDOUT_START<=idx[j]<=HOLDOUT_END and gp[j]>=GAP]
        # every gap event: max score during T-10..T-1
        for j in gaps:
            checks=[]
            for lead in range(10,0,-1):
                k=j-lead
                z=feat(d,k) if k>=0 else None
                if z: checks.append((lead,z))
            if checks:
                best=max(checks,key=lambda q:q[1]['score'])
                rows.append({'symbol':s,'group':'GAP','date':idx[j].date(),'gap_pct':gp[j],'max_score_10d':best[1]['score'],'earliest_score4':max([lead for lead,z in checks if z['score']>=4],default=np.nan),'earliest_score5':max([lead for lead,z in checks if z['score']>=5],default=np.nan)})
        # matched control dates: monthly-ish dates with no >=4% gap next 10 sessions
        elig=[k for k in range(PRE,len(d)-11) if HOLDOUT_START<=idx[k]<=HOLDOUT_END]
        controls=[]
        for k in elig[::20]:
            if np.nanmax(gp[k+1:k+11])<GAP: controls.append(k)
        for k in controls[:max(12,len(gaps)*3)]:
            checks=[]
            for lead in range(10,0,-1):
                q=k-lead+1; z=feat(d,q) if q>=0 else None
                if z: checks.append((lead,z))
            if checks:
                best=max(checks,key=lambda q:q[1]['score'])
                rows.append({'symbol':s,'group':'CONTROL','date':idx[k].date(),'gap_pct':0,'max_score_10d':best[1]['score'],'earliest_score4':max([lead for lead,z in checks if z['score']>=4],default=np.nan),'earliest_score5':max([lead for lead,z in checks if z['score']>=5],default=np.nan)})
    r=pd.DataFrame(rows); r.to_csv(OUT/'events.csv',index=False)
    g=r[r.group.eq('GAP')]; c=r[r.group.eq('CONTROL')]
    md=['# Older Out-of-Sample Pre-Gap Pattern Test','',f'- Holdout: **{HOLDOUT_START.date()} to {HOLDOUT_END.date()}**',f'- Symbols: **{len(syms)}** (same symbol universe, older unseen dates)',f'- Gap events >=4%: **{len(g)}**',f'- Matched non-gap control dates: **{len(c)}**','']
    for t in (3,4,5,6):
        gr=(g.max_score_10d>=t).mean() if len(g) else np.nan; cr=(c.max_score_10d>=t).mean() if len(c) else np.nan
        md.append(f'- Score >= {t} within prior 10 sessions: gap **{gr:.0%}**, controls **{cr:.0%}**, separation **{gr-cr:+.0%}**')
    md += ['','Score components: EMA20>EMA50, full trend stack, shallow <=8% pullback, within 5% of 60d high, 10d range contraction, EMA20 10d slope >=1%.','',
           'This is a genuine older-date holdout: the 2026 observations used to discover the pattern are not used as event dates here.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))

if __name__=='__main__':main()
