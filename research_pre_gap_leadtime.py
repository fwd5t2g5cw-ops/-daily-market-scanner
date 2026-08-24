from __future__ import annotations

from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/pre_gap_leadtime'); OUT.mkdir(parents=True,exist_ok=True)
EVENTS=Path('research/pre_gap/events.csv')
LOOKBACK=50; RS_LOOKBACK=63
MAX_TO_BREAKOUT=5.0; MAX_BELOW_HIGH=15.0; MIN_RS=5.0; MAX_ABOVE_EMA20=8.0
COMPRESSION_MAX_TO_BREAKOUT=2.0; COMPRESSION_MAX_BELOW_HIGH=10.0; COMPRESSION_MIN_SCORE=7


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,period='18mo',interval='1d',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>=270: return d
        except Exception as e: print(s,k+1,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()


def comp_score(dist,below,above20,rs,vc,rc):
    score=3 if dist<=1 else (2 if dist<=2 else (1 if dist<=3 else 0))
    score+=2 if below<=5 else (1 if below<=10 else 0)
    score+=2 if above20<=2 else (1 if above20<=4 else 0)
    score+=1 if rs>=5 else 0; score+=1 if rs>=10 else 0
    score+=1 if vc else 0; score+=1 if rc else 0
    return score


def eval_day(d,bench,end_i):
    if end_i<260: return None
    x=d.iloc[:end_i+1]; c=x.Close.astype(float); h=x.High.astype(float); l=x.Low.astype(float); v=x.Volume.astype(float)
    px=float(c.iloc[-1]); e20s=c.ewm(span=20,adjust=False).mean(); e50s=c.ewm(span=50,adjust=False).mean(); s200s=c.rolling(200).mean()
    e20=float(e20s.iloc[-1]); e50=float(e50s.iloc[-1]); s200=float(s200s.iloc[-1])
    strong=px>e20>e50>s200 and e50>float(e50s.iloc[-11]) and s200>float(s200s.iloc[-21])
    resistance=float(h.shift(1).rolling(LOOKBACK).max().iloc[-1])
    if not np.isfinite(resistance) or resistance<=0: return None
    dist=(resistance-px)/resistance*100; high52=float(h.tail(252).max()); below=(high52-px)/high52*100
    bidx=pd.DatetimeIndex(bench.index).tz_localize(None); dt=pd.Timestamp(d.index[end_i]).tz_localize(None)
    be=np.where(bidx<=dt)[0]
    if not len(be) or be[-1]<RS_LOOKBACK: return None
    bc=bench.Close.astype(float); bi=int(be[-1]); br=float(bc.iloc[bi]/bc.iloc[bi-RS_LOOKBACK]-1)
    sr=float(px/c.iloc[-1-RS_LOOKBACK]-1); rs=(sr-br)*100
    av20=float(v.tail(20).mean()); av10=float(v.tail(10).mean()); vc=bool(av20>0 and av10<=av20*.90)
    r20=(float(h.tail(20).max())/float(l.tail(20).min())-1)*100; r10=(float(h.tail(10).max())/float(l.tail(10).min())-1)*100
    rc=bool(r20>0 and r10<=r20*.75); above20=(px/e20-1)*100
    pre=bool(strong and 0<=dist<=MAX_TO_BREAKOUT and below<=MAX_BELOW_HIGH and rs>=MIN_RS and above20<=MAX_ABOVE_EMA20)
    cs=comp_score(dist,below,above20,rs,vc,rc)
    comp=bool(pre and dist<=COMPRESSION_MAX_TO_BREAKOUT and below<=COMPRESSION_MAX_BELOW_HIGH and 0<=above20<=4 and cs>=COMPRESSION_MIN_SCORE)
    return {'pre_entry':pre,'compression':comp,'compression_score':cs,'dist_breakout':dist,'below_high':below,'above_ema20':above20,'rs':rs,'range_contract':rc,'volume_contract':vc}


def main():
    ev=pd.read_csv(EVENTS); gaps=ev[ev.group.eq('GAP')][['symbol','event_date','gap_pct']].drop_duplicates().copy()
    gaps['event_date']=pd.to_datetime(gaps.event_date)
    symbols=sorted(gaps.symbol.unique()); print('gaps',len(gaps),'symbols',len(symbols))
    bench=dl('SPY'); data={}
    for i,s in enumerate(symbols,1): print(i,'/',len(symbols),s); data[s]=dl(s)
    rows=[]
    for _,g in gaps.iterrows():
        s=g.symbol; d=data.get(s)
        if d is None or d.empty: continue
        idx=pd.DatetimeIndex(d.index).tz_localize(None); pos=np.where(idx==g.event_date)[0]
        if not len(pos): continue
        j=int(pos[0]); dayrows=[]
        for lead in range(10,0,-1):
            k=j-lead
            if k<0: continue
            z=eval_day(d,bench,k)
            if z: dayrows.append({'symbol':s,'gap_date':g.event_date.date(),'gap_pct':g.gap_pct,'lead_days':lead,'scan_date':idx[k].date(),**z})
        rows.extend(dayrows)
    r=pd.DataFrame(rows); r.to_csv(OUT/'daily_checks.csv',index=False)
    if r.empty: raise SystemExit('no rows')
    summary=[]
    for (s,gd),q in r.groupby(['symbol','gap_date']):
        pre=q[q.pre_entry]; comp=q[q.compression]
        summary.append({'symbol':s,'gap_date':gd,'gap_pct':q.gap_pct.iloc[0],
          'pre_entry_at_T10':bool(q.loc[q.lead_days.eq(10),'pre_entry'].any()),
          'compression_at_T10':bool(q.loc[q.lead_days.eq(10),'compression'].any()),
          'pre_entry_any_T10_T1':bool(pre.shape[0]),'compression_any_T10_T1':bool(comp.shape[0]),
          'earliest_pre_entry_lead':int(pre.lead_days.max()) if len(pre) else np.nan,
          'earliest_compression_lead':int(comp.lead_days.max()) if len(comp) else np.nan})
    s=pd.DataFrame(summary).sort_values('gap_pct',ascending=False); s.to_csv(OUT/'event_summary.csv',index=False)
    n=len(s)
    md=['# Current Scanner: 10-Day Pre-Gap Lead-Time Test','',f'- Gap events tested: **{n}**',
        f"- PRE-ENTRY already true exactly T-10: **{s.pre_entry_at_T10.sum()}/{n} ({s.pre_entry_at_T10.mean():.0%})**",
        f"- Compression already true exactly T-10: **{s.compression_at_T10.sum()}/{n} ({s.compression_at_T10.mean():.0%})**",
        f"- PRE-ENTRY detected at least once during T-10..T-1: **{s.pre_entry_any_T10_T1.sum()}/{n} ({s.pre_entry_any_T10_T1.mean():.0%})**",
        f"- Compression detected at least once during T-10..T-1: **{s.compression_any_T10_T1.sum()}/{n} ({s.compression_any_T10_T1.mean():.0%})**",'',
        'This recreates the **current US PRE-ENTRY / Compression scanner logic** on each historical day using only information available on that day.','',
        '| Symbol | Gap date | Gap | PRE @T-10 | Comp @T-10 | PRE within 10d | Comp within 10d | Earliest PRE | Earliest Comp |','|---|---|---:|:---:|:---:|:---:|:---:|---:|---:|']
    for _,x in s.iterrows():
        ep='-' if pd.isna(x.earliest_pre_entry_lead) else int(x.earliest_pre_entry_lead); ec='-' if pd.isna(x.earliest_compression_lead) else int(x.earliest_compression_lead)
        md.append(f"| {x.symbol} | {x.gap_date} | {x.gap_pct:.1f}% | {'Y' if x.pre_entry_at_T10 else ''} | {'Y' if x.compression_at_T10 else ''} | {'Y' if x.pre_entry_any_T10_T1 else ''} | {'Y' if x.compression_any_T10_T1 else ''} | {ep} | {ec} |")
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md[:20]))

if __name__=='__main__': main()
