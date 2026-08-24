from __future__ import annotations

import io, itertools, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import fisher_exact

PATH='latest/us/us_pre_breakout_compression_today.csv'
OUT=Path('research/pre_gap'); OUT.mkdir(parents=True,exist_ok=True)
GAP_PCT=4.0; LOOKBACK_GAP=90; PRE=60


def sh(*args): return subprocess.check_output(['git',*args],text=True,stderr=subprocess.DEVNULL).strip()

def snapshots(maxn=12):
    out=[]
    for sha in sh('log','--format=%H','--',PATH).splitlines()[:maxn]:
        try:
            df=pd.read_csv(io.StringIO(sh('show',f'{sha}:{PATH}')))
            dt=pd.Timestamp(sh('show','-s','--format=%cI',sha)).tz_convert(None).normalize()
            if not df.empty: out.append((sha,dt,df))
        except Exception as e: print('snapshot skip',sha,e)
    return out

def download(s):
    for k in range(3):
        try:
            d=yf.download(s,period='18mo',interval='1d',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>=180: return d
        except Exception as e: print(s,'download',k+1,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()

def feats(d,end_i):
    if end_i<PRE or end_i>=len(d): return None
    w=d.iloc[end_i-PRE+1:end_i+1].copy()
    c=w.Close.astype(float); h=w.High.astype(float); l=w.Low.astype(float); v=w.Volume.astype(float)
    ret=c.pct_change(); prev=d.iloc[:end_i+1].Close.astype(float)
    ema20=prev.ewm(span=20,adjust=False).mean(); ema50=prev.ewm(span=50,adjust=False).mean()
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    range10=(h.tail(10).max()/l.tail(10).min()-1)*100; range20=(h.tail(20).max()/l.tail(20).min()-1)*100
    p20=w.iloc[-30:-10]; p20r=(p20.High.max()/p20.Low.min()-1)*100
    thirds=np.array_split(l.to_numpy(),3); meds=[float(np.nanmedian(x)) for x in thirds]
    hl=int(meds[1]>meds[0])+int(meds[2]>meds[1])
    last=float(c.iloc[-1]); peak=float(c.max()); high60=float(h.max()); dd=(c/c.cummax()-1)*100
    return {
      'ret60_pct':(last/float(c.iloc[0])-1)*100,'max_drawdown60_pct':float(dd.min()),
      'pullback_from_60d_close_high_pct':(peak-last)/peak*100,'dist_from_60d_high_pct':(high60-last)/high60*100,
      'ema20_slope10_pct':(float(ema20.iloc[-1])/float(ema20.iloc[-11])-1)*100,'higher_low_score':hl,
      'range10_pct':range10,'range20_pct':range20,'range10_vs20':range10/range20 if range20 else np.nan,
      'range10_vs_prev20':range10/p20r if p20r else np.nan,'atr10_vs40':float(tr.tail(10).mean()/tr.tail(40).mean()),
      'vol10_vs40':float(v.tail(10).mean()/v.tail(40).mean()),'up_days20_pct':float((ret.tail(20)>0).mean()*100),
      'ret_std10_pct':float(ret.tail(10).std()*100),
      'near_high_5':bool((high60-last)/high60*100<=5),'shallow_pullback_8':bool((peak-last)/peak*100<=8),
      'range_contract_075':bool(range10/range20<=.75 if range20 else False),'range_vs_prior_075':bool(range10/p20r<=.75 if p20r else False),
      'volume_dry_080':bool(v.tail(10).mean()/v.tail(40).mean()<=.8),'volume_expand_110':bool(v.tail(10).mean()/v.tail(40).mean()>=1.10),
      'atr_contract_080':bool(tr.tail(10).mean()/tr.tail(40).mean()<=.8),'atr_expand_110':bool(tr.tail(10).mean()/tr.tail(40).mean()>=1.10),
      'trend_stack':bool(last>ema20.iloc[-1]>ema50.iloc[-1]),'higher_lows_2of2':bool(hl==2),
      'ema20_gt_ema50':bool(ema20.iloc[-1]>ema50.iloc[-1]),'close_gt_ema20':bool(last>ema20.iloc[-1])}

def main():
    snaps=snapshots(); symbols=sorted(set().union(*[set(x.symbol.astype(str)) for _,_,x in snaps]))
    print('snapshots',[(s[:7],str(dt.date()),len(df)) for s,dt,df in snaps]); print('unique symbols',len(symbols))
    data={s:download(s) for s in symbols}
    gap_events={}
    for _,snap,df in snaps:
      for s in df.symbol.astype(str):
        d=data.get(s)
        if d is None or d.empty: continue
        idx=pd.DatetimeIndex(d.index).tz_localize(None); elig=np.where(idx<=snap)[0]
        if not len(elig): continue
        end=int(elig[-1]); op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy(); gp=(op[1:]/cl[:-1]-1)*100
        start=max(PRE+1,end-LOOKBACK_GAP+1)
        for j in range(start,end+1):
            if gp[j-1]>=GAP_PCT: gap_events[(s,str(idx[j].date()))]=(s,j,float(gp[j-1]),snap)
    rows=[]
    for s,j,gp,snap in gap_events.values():
        d=data[s]; idx=pd.DatetimeIndex(d.index).tz_localize(None); f=feats(d,j-1)
        if not f: continue
        rows.append({'symbol':s,'group':'GAP','event_date':idx[j].date(),'gap_pct':gp,**f})
        # matched same-stock controls: earlier dates 20-120 sessions before the gap, no >=4% gap in next 5 sessions
        op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy(); g=(op[1:]/cl[:-1]-1)*100
        cand=[]
        lo=max(PRE,j-120); hi=max(PRE,j-20)
        for k in range(lo,hi+1):
            future=g[k:min(k+5,len(g))] if k<len(g) else []
            if len(future) and np.nanmax(future)<GAP_PCT: cand.append(k)
        if cand:
            picks=np.unique(np.linspace(0,len(cand)-1,min(3,len(cand))).round().astype(int))
            for z in picks:
                k=cand[int(z)]; cf=feats(d,k)
                if cf: rows.append({'symbol':s,'group':'CONTROL','event_date':idx[k].date(),'gap_pct':0.0,**cf})
    ev=pd.DataFrame(rows); ev.to_csv(OUT/'events.csv',index=False)
    ng=int((ev.group=='GAP').sum()); nc=int((ev.group=='CONTROL').sum())
    nums=[c for c in ev.columns if c not in {'symbol','group','event_date'} and ev[c].dtype!=bool and c!='gap_pct']
    fs=[]
    for c in nums:
        a=pd.to_numeric(ev.loc[ev.group=='GAP',c],errors='coerce'); b=pd.to_numeric(ev.loc[ev.group=='CONTROL',c],errors='coerce')
        sd=np.sqrt((a.var()+b.var())/2); smd=(a.mean()-b.mean())/sd if sd and np.isfinite(sd) else np.nan
        fs.append({'feature':c,'gap_mean':a.mean(),'control_mean':b.mean(),'difference':a.mean()-b.mean(),'std_mean_diff':smd})
    fs=pd.DataFrame(fs).sort_values('std_mean_diff',key=lambda x:x.abs(),ascending=False); fs.to_csv(OUT/'feature_summary.csv',index=False)
    bins=['near_high_5','shallow_pullback_8','range_contract_075','range_vs_prior_075','volume_dry_080','volume_expand_110','atr_contract_080','atr_expand_110','trend_stack','higher_lows_2of2','ema20_gt_ema50','close_gt_ema20']
    bs=[]
    for c in bins:
        a=int(ev.loc[ev.group=='GAP',c].sum()); x=int(ev.loc[ev.group=='CONTROL',c].sum()); _,p=fisher_exact([[a,ng-a],[x,nc-x]])
        bs.append({'feature':c,'gap_rate':a/ng,'control_rate':x/nc,'rate_diff':a/ng-x/nc,'fisher_p':p})
    bs=pd.DataFrame(bs).sort_values('rate_diff',key=lambda x:x.abs(),ascending=False); bs.to_csv(OUT/'binary_summary.csv',index=False)
    # combos allow both contraction and expansion hypotheses; rank by lift and minimum support
    rules=[]
    for r in (2,3):
      for combo in itertools.combinations(bins,r):
        m=np.logical_and.reduce([ev[c].astype(bool).to_numpy() for c in combo]); sup=int(m.sum())
        if sup<4: continue
        gh=int(((ev.group=='GAP').to_numpy() & m).sum()); ch=sup-gh; gc=gh/ng; cc=ch/nc; prec=gh/sup
        rules.append({'rule':' + '.join(combo),'support':sup,'gap_hits':gh,'control_hits':ch,'gap_coverage':gc,'control_coverage':cc,'precision_in_sample':prec,'lift':gc/cc if cc else np.inf})
    rules=pd.DataFrame(rules)
    if not rules.empty: rules=rules.sort_values(['precision_in_sample','gap_coverage','support'],ascending=[False,False,False])
    rules.to_csv(OUT/'rule_candidates.csv',index=False)
    gap_syms=ev.loc[ev.group=='GAP',['symbol','event_date','gap_pct']].sort_values('gap_pct',ascending=False)
    md=['# Pre-Gap 60-Day Chart Pattern Research — Matched Controls','',f'- Compression snapshots used: **{len(snaps)}**',f'- Unique symbols in snapshots: **{len(symbols)}**',f'- Distinct >= {GAP_PCT:.0f}% opening-gap events: **{ng}**',f'- Same-stock matched control dates: **{nc}**','',
        'Controls are earlier dates from the **same stock**, 20–120 sessions before its gap, with no >=4% gap in the following five sessions. This is a much cleaner test of what changes as a gap approaches.','',
        '## Largest pre-gap differences vs same-stock controls','', '| Feature | Gap mean/rate | Control mean/rate | Difference |','|---|---:|---:|---:|']
    for _,r in bs.head(8).iterrows(): md.append(f"| {r.feature} | {r.gap_rate:.0%} | {r.control_rate:.0%} | {r.rate_diff:+.0%} |")
    md += ['','## Largest numeric shifts','', '| Feature | Gap | Control | Std. difference |','|---|---:|---:|---:|']
    for _,r in fs.head(8).iterrows(): md.append(f"| {r.feature} | {r.gap_mean:.2f} | {r.control_mean:.2f} | {r.std_mean_diff:+.2f} |")
    md += ['','## Best exploratory combinations','', '| Rule | Gap hits | Control hits | Gap coverage | Sample precision |','|---|---:|---:|---:|---:|']
    for _,r in rules.head(10).iterrows(): md.append(f"| {r.rule} | {int(r.gap_hits)} | {int(r.control_hits)} | {r.gap_coverage:.0%} | {r.precision_in_sample:.0%} |")
    md += ['','## Gap examples','', '| Symbol | Gap date | Opening gap |','|---|---|---:|']
    for _,r in gap_syms.head(30).iterrows(): md.append(f"| {r.symbol} | {r.event_date} | {r.gap_pct:.1f}% |")
    md += ['','## Guardrails','', '- All features use only data available before the event date.','- This remains an exploratory selected sample; any scanner rule must be validated on older unseen market data.','- A failure to find a strong chart signature is a valid result; surprise M&A/news gaps may simply not be predictable from price/volume alone.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md[:50]))

if __name__=='__main__': main()
