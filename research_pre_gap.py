from __future__ import annotations

import io, itertools, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import fisher_exact

PATH='latest/us/us_pre_breakout_compression_today.csv'
OUT=Path('research/pre_gap'); OUT.mkdir(parents=True,exist_ok=True)
GAP_PCT=4.0
LOOKBACK_GAP=90
PRE=60


def sh(*args):
    return subprocess.check_output(['git',*args],text=True,stderr=subprocess.DEVNULL).strip()

def snapshots(maxn=12):
    commits=sh('log','--format=%H','--',PATH).splitlines()[:maxn]
    out=[]
    for sha in commits:
        try:
            txt=sh('show',f'{sha}:{PATH}')
            df=pd.read_csv(io.StringIO(txt))
            dt=pd.Timestamp(sh('show','-s','--format=%cI',sha)).tz_convert(None)
            if not df.empty:
                out.append((sha,dt.normalize(),df))
        except Exception as e:
            print('snapshot skip',sha,e)
    return out

def download(symbol):
    for k in range(3):
        try:
            d=yf.download(symbol,period='18mo',interval='1d',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close'])
            if len(d)>=120: return d
        except Exception as e: print(symbol,'download',k+1,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()

def feats(d, end_i):
    # features known at end_i only (T-1 for real gap; snapshot day for control)
    if end_i<PRE or end_i>=len(d): return None
    w=d.iloc[end_i-PRE+1:end_i+1].copy()
    if len(w)<PRE: return None
    c=w.Close.astype(float); h=w.High.astype(float); l=w.Low.astype(float); v=w.Volume.astype(float)
    ret=c.pct_change()
    prev=d.iloc[:end_i+1].Close.astype(float)
    ema20=prev.ewm(span=20,adjust=False).mean(); ema50=prev.ewm(span=50,adjust=False).mean()
    tr=pd.concat([(h-l),(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    range10=(h.tail(10).max()/l.tail(10).min()-1)*100
    range20=(h.tail(20).max()/l.tail(20).min()-1)*100
    prev20=w.iloc[-30:-10]
    prev20range=(prev20.High.max()/prev20.Low.min()-1)*100 if len(prev20) else np.nan
    thirds=np.array_split(l.to_numpy(),3)
    low_meds=[float(np.nanmedian(x)) for x in thirds]
    higher_low=int(low_meds[1]>low_meds[0])+int(low_meds[2]>low_meds[1])
    peak=float(c.max()); last=float(c.iloc[-1]); high60=float(h.max())
    dd=(c/c.cummax()-1)*100
    return {
      'ret60_pct':(last/float(c.iloc[0])-1)*100,
      'max_drawdown60_pct':float(dd.min()),
      'pullback_from_60d_close_high_pct':(peak-last)/peak*100,
      'dist_from_60d_high_pct':(high60-last)/high60*100,
      'ema20_gt_ema50':bool(ema20.iloc[-1]>ema50.iloc[-1]),
      'close_gt_ema20':bool(last>ema20.iloc[-1]),
      'ema20_slope10_pct':(float(ema20.iloc[-1])/float(ema20.iloc[-11])-1)*100 if len(ema20)>=11 else np.nan,
      'higher_low_score':higher_low,
      'range10_pct':range10,
      'range20_pct':range20,
      'range10_vs20':range10/range20 if range20>0 else np.nan,
      'range10_vs_prev20':range10/prev20range if prev20range>0 else np.nan,
      'atr10_vs40':float(tr.tail(10).mean()/tr.tail(40).mean()) if tr.tail(40).mean()>0 else np.nan,
      'vol10_vs40':float(v.tail(10).mean()/v.tail(40).mean()) if v.tail(40).mean()>0 else np.nan,
      'up_days20_pct':float((ret.tail(20)>0).mean()*100),
      'ret_std10_pct':float(ret.tail(10).std()*100),
      'near_high_5':bool((high60-last)/high60*100<=5),
      'shallow_pullback_8':bool((peak-last)/peak*100<=8),
      'range_contract_075':bool(range20>0 and range10/range20<=0.75),
      'range_vs_prior_075':bool(prev20range>0 and range10/prev20range<=0.75),
      'volume_dry_080':bool(v.tail(40).mean()>0 and v.tail(10).mean()/v.tail(40).mean()<=0.80),
      'atr_contract_080':bool(tr.tail(40).mean()>0 and tr.tail(10).mean()/tr.tail(40).mean()<=0.80),
      'trend_stack':bool(last>ema20.iloc[-1]>ema50.iloc[-1]),
      'higher_lows_2of2':bool(higher_low==2),
    }

def main():
    snaps=snapshots()
    print('snapshots',[(s[:7],str(dt.date()),len(df)) for s,dt,df in snaps])
    symbols=sorted(set().union(*[set(df.symbol.astype(str)) for _,_,df in snaps]))
    print('unique compression symbols',len(symbols))
    data={}
    for i,s in enumerate(symbols,1):
        print(i,'/',len(symbols),s)
        data[s]=download(s)
        time.sleep(.15)

    events=[]; seen_gap=set(); seen_control=set()
    for sha,snap_date,df in snaps:
        for s in df.symbol.astype(str):
            d=data.get(s)
            if d is None or d.empty: continue
            idx=pd.DatetimeIndex(d.index).tz_localize(None)
            eligible=np.where(idx<=snap_date)[0]
            if not len(eligible): continue
            end=int(eligible[-1])
            # locate most recent >=4% opening gap in prior 90 bars
            start=max(1,end-LOOKBACK_GAP+1)
            op=d.Open.astype(float).to_numpy(); cl=d.Close.astype(float).to_numpy()
            gp=(op[1:]/cl[:-1]-1)*100
            cand=[j for j in range(start,end+1) if gp[j-1]>=GAP_PCT]
            if cand:
                j=cand[-1]
                key=(s,str(idx[j].date()))
                if key in seen_gap: continue
                f=feats(d,j-1)
                if not f: continue
                seen_gap.add(key)
                events.append({'symbol':s,'group':'GAP','event_date':idx[j].date(),'snapshot_date':snap_date.date(),'gap_pct':gp[j-1],**f})
            else:
                key=(s,str(snap_date.date()))
                if key in seen_control: continue
                f=feats(d,end)
                if not f: continue
                seen_control.add(key)
                events.append({'symbol':s,'group':'CONTROL','event_date':idx[end].date(),'snapshot_date':snap_date.date(),'gap_pct':0.0,**f})

    ev=pd.DataFrame(events)
    ev.to_csv(OUT/'events.csv',index=False)
    if ev.empty or ev.group.nunique()<2:
        (OUT/'report.md').write_text('# Pre-Gap Research\n\nInsufficient two-group sample.\n')
        return

    num=[c for c in ev.columns if c not in {'symbol','group','event_date','snapshot_date'} and ev[c].dtype!=bool]
    rows=[]
    for c in num:
        g=pd.to_numeric(ev.loc[ev.group=='GAP',c],errors='coerce'); q=pd.to_numeric(ev.loc[ev.group=='CONTROL',c],errors='coerce')
        if c=='gap_pct': continue
        rows.append({'feature':c,'gap_mean':g.mean(),'control_mean':q.mean(),'difference':g.mean()-q.mean()})
    pd.DataFrame(rows).to_csv(OUT/'feature_summary.csv',index=False)

    bins=['near_high_5','shallow_pullback_8','range_contract_075','range_vs_prior_075','volume_dry_080','atr_contract_080','trend_stack','higher_lows_2of2','ema20_gt_ema50','close_gt_ema20']
    br=[]
    ng=(ev.group=='GAP').sum(); nc=(ev.group=='CONTROL').sum()
    for c in bins:
        a=int(ev.loc[ev.group=='GAP',c].sum()); b=ng-a; x=int(ev.loc[ev.group=='CONTROL',c].sum()); y=nc-x
        _,p=fisher_exact([[a,b],[x,y]])
        br.append({'feature':c,'gap_rate':a/ng,'control_rate':x/nc,'rate_diff':a/ng-x/nc,'fisher_p':p})
    bin_df=pd.DataFrame(br).sort_values('rate_diff',ascending=False); bin_df.to_csv(OUT/'binary_summary.csv',index=False)

    rules=[]
    for r in range(2,5):
        for combo in itertools.combinations(bins,r):
            m=np.logical_and.reduce([ev[c].astype(bool).to_numpy() for c in combo])
            support=int(m.sum())
            if support<3: continue
            gap_hits=int(((ev.group=='GAP').to_numpy() & m).sum())
            control_hits=support-gap_hits
            gap_cov=gap_hits/ng; ctrl_cov=control_hits/nc
            precision=gap_hits/support
            lift=(gap_cov/ctrl_cov) if ctrl_cov>0 else np.inf
            rules.append({'rule':' + '.join(combo),'support':support,'gap_hits':gap_hits,'control_hits':control_hits,'precision_in_sample':precision,'gap_coverage':gap_cov,'control_coverage':ctrl_cov,'lift':lift})
    rules=pd.DataFrame(rules)
    if not rules.empty: rules=rules.sort_values(['precision_in_sample','gap_coverage','support'],ascending=[False,False,False])
    rules.to_csv(OUT/'rule_candidates.csv',index=False)

    topbin=bin_df.head(6)
    toprules=rules.head(10) if not rules.empty else pd.DataFrame()
    gap_syms=ev.loc[ev.group=='GAP',['symbol','event_date','gap_pct']].sort_values('gap_pct',ascending=False)
    md=[]
    md += ['# Pre-Gap 60-Day Chart Pattern Research','',f'- Compression snapshots used: **{len(snaps)}**',f'- Unique symbols studied: **{len(symbols)}**',f'- Gap events (open >= prior close +{GAP_PCT:.0f}%): **{ng}**',f'- Compression controls with no such gap in prior {LOOKBACK_GAP} sessions: **{nc}**','',
           '## Strongest pre-gap binary differences','', '| Feature | Gap group | Control | Difference |','|---|---:|---:|---:|']
    for _,r in topbin.iterrows(): md.append(f"| {r.feature} | {r.gap_rate:.0%} | {r.control_rate:.0%} | {r.rate_diff:+.0%} |")
    md += ['','## Best exploratory combinations','', '> Exploratory only: this is a selected Compression sample, not the whole market. A rule must later be tested out-of-sample.','', '| Rule | Gap hits | Control hits | Gap coverage | Sample precision |','|---|---:|---:|---:|---:|']
    for _,r in toprules.iterrows(): md.append(f"| {r.rule} | {int(r.gap_hits)} | {int(r.control_hits)} | {r.gap_coverage:.0%} | {r.precision_in_sample:.0%} |")
    md += ['','## Detected gap examples','', '| Symbol | Gap date | Opening gap |','|---|---|---:|']
    for _,r in gap_syms.head(30).iterrows(): md.append(f"| {r.symbol} | {r.event_date} | {r.gap_pct:.1f}% |")
    md += ['','## Interpretation guardrails','', '- Every feature is calculated using data available **before** the gap day.','- Controls come from the same Compression lists, which reduces but does not eliminate selection bias.','- M&A/news gaps can be inherently unpredictable from charts; the next phase should separate those if the chart signature differs.','- The goal is to identify repeatable 45–60 session structures, then validate them on older unseen periods before adding a live scanner.','']
    (OUT/'report.md').write_text('\n'.join(md))
    print('\n'.join(md[:40]))

if __name__=='__main__': main()
