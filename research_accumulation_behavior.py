from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/accumulation_behavior'); OUT.mkdir(parents=True,exist_ok=True)
SRC=Path('research/pre_gap_oos/events.csv')
START='2022-01-01'; END='2025-12-31'; POWER=15.0; FWD=10


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2021-01-01',end='2026-01-15',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close','Volume'])
            if len(d)>300: return d
        except Exception as e: print(s,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()

def build_features(d):
    x=d.copy()
    c=x.Close.astype(float); o=x.Open.astype(float); h=x.High.astype(float); l=x.Low.astype(float); v=x.Volume.astype(float)
    ret=c.pct_change(); rng=(h-l)/c.shift(1).replace(0,np.nan)
    clv=((c-l)/(h-l).replace(0,np.nan)).clip(0,1).fillna(.5)
    v20=v.rolling(20).median(); r20=rng.rolling(20).median()
    vol_rel=v/v20

    absorb=((vol_rel>=1.5) & (ret>=-0.01) & (clv>=0.5)).astype(int)
    effort_no_down=((vol_rel>=1.5) & (ret.abs()<=0.012) & (clv>=0.45)).astype(int)
    down_reject=((vol_rel>=1.3) & (ret<0) & (clv>=0.65)).astype(int)
    prior_low=l.shift(1).rolling(10).min()
    undercut_reclaim=((l<prior_low) & (c>prior_low)).astype(int)

    upmask=(ret>0); dnmask=(ret<0)
    upv=v.where(upmask,0).rolling(20).sum(); dnv=v.where(dnmask,0).rolling(20).sum()
    updown=(upv/dnv.replace(0,np.nan)).clip(0,10)
    neg=ret.where(ret<0,0).abs().rolling(20).mean(); pos=ret.where(ret>0,0).rolling(20).mean()
    resilience=(pos/neg.replace(0,np.nan)).clip(0,10)
    upcnt=upmask.astype(int).rolling(20).sum(); dncnt=dnmask.astype(int).rolling(20).sum()
    upavg=upv/upcnt.replace(0,np.nan); dnavg=dnv/dncnt.replace(0,np.nan)
    vol_asym=(upavg/dnavg.replace(0,np.nan)).clip(0,10)
    hvmask=(vol_rel>=1.3)
    hvcount=hvmask.astype(int).rolling(10).sum()
    hvstrength=(clv.where(hvmask,0).rolling(10).sum()/hvcount.replace(0,np.nan)).fillna(.5)

    f=pd.DataFrame(index=x.index)
    f['absorb20']=absorb.rolling(20).sum()
    f['effort_no_down20']=effort_no_down.rolling(20).sum()
    f['down_reject20']=down_reject.rolling(20).sum()
    f['undercut_reclaim20']=undercut_reclaim.rolling(20).sum()
    f['updown_vol20']=updown
    f['resilience20']=resilience
    f['vol_asym20']=vol_asym
    f['highvol_close_strength10']=hvstrength
    f['volume_cluster10']=hvcount
    f['range_contract10_40']=rng.rolling(10).mean()/rng.rolling(40).mean()
    f['vol_contract10_40']=v.rolling(10).mean()/v.rolling(40).mean()
    f['ret20']=c/c.shift(20)-1
    f['dist60high']=c/h.rolling(60).max()-1

    gap=(o/c.shift(1)-1)*100
    arr=gap.to_numpy(); y=np.zeros(len(x),dtype=int); maxg=np.full(len(x),np.nan)
    for i in range(len(x)):
        z=arr[i+1:min(i+1+FWD,len(x))]
        if len(z):
            maxg[i]=np.nanmax(z); y[i]=int(maxg[i]>=POWER)
    f['future_power_gap']=y; f['max_gap_next10']=maxg
    return f

def main():
    src=pd.read_csv(SRC); symbols=sorted(src.symbol.astype(str).unique())
    feats=['absorb20','effort_no_down20','down_reject20','undercut_reclaim20','updown_vol20','resilience20','vol_asym20','highvol_close_strength10','volume_cluster10','range_contract10_40','vol_contract10_40','ret20','dist60high']
    frames=[]
    for n,s in enumerate(symbols,1):
        print(n,len(symbols),s); d=dl(s)
        if d.empty: continue
        f=build_features(d); f['symbol']=s; f['date']=pd.DatetimeIndex(f.index).tz_localize(None)
        f=f[(f.date>=START)&(f.date<=END)].dropna(subset=feats+['max_gap_next10'])
        frames.append(f)
    z=pd.concat(frames,ignore_index=True); z.to_csv(OUT/'stock_days.csv',index=False)
    y=z.future_power_gap.astype(bool); ng=int(y.sum())
    rows=[]
    for c in feats:
        a=z.loc[y,c]; b=z.loc[~y,c]; sd=np.sqrt((a.var()+b.var())/2)
        smd=(a.mean()-b.mean())/sd if pd.notna(sd) and sd>0 else np.nan
        rows.append({'feature':c,'gap_mean':a.mean(),'normal_mean':b.mean(),'std_diff':smd})
    summ=pd.DataFrame(rows).sort_values('std_diff',key=lambda q:q.abs(),ascending=False); summ.to_csv(OUT/'feature_summary.csv',index=False)

    train=z[z.date<'2024-01-01']; test=z[z.date>='2024-01-01'].copy(); tests=[]
    for c in feats:
        q20=train[c].quantile(.20); q80=train[c].quantile(.80)
        for name,mask in [('HIGH',test[c]>=q80),('LOW',test[c]<=q20)]:
            base=test.future_power_gap.mean(); hit=test.loc[mask,'future_power_gap'].mean() if mask.sum() else np.nan
            tests.append({'feature':c,'tail':name,'threshold':q80 if name=='HIGH' else q20,'days':int(mask.sum()),'hit_rate':hit,'base_rate':base,'lift':hit/base if base>0 and pd.notna(hit) else np.nan})
    tails=pd.DataFrame(tests).sort_values('lift',ascending=False); tails.to_csv(OUT/'forward_tail_tests.csv',index=False)

    qs={c:train[c].quantile(.75) for c in ['absorb20','effort_no_down20','down_reject20','undercut_reclaim20','updown_vol20','resilience20','vol_asym20','highvol_close_strength10']}
    score=np.zeros(len(test),dtype=int)
    for c,t in qs.items(): score += (test[c]>=t).to_numpy()
    test['behavior_score']=score; score_rows=[]; base=test.future_power_gap.mean()
    for k in range(2,9):
        m=test.behavior_score>=k; hit=test.loc[m,'future_power_gap'].mean() if m.sum() else np.nan
        score_rows.append({'min_score':k,'days':int(m.sum()),'hit_rate':hit,'base_rate':base,'lift':hit/base if base>0 and pd.notna(hit) else np.nan})
    scores=pd.DataFrame(score_rows); scores.to_csv(OUT/'behavior_score_forward.csv',index=False)

    md=['# Accumulation-Behavior Pre-Gap Research','',f'- Window: **{START} to {END}**',f'- Symbols: **{len(symbols)}**',f'- Eligible stock-days: **{len(z)}**',f'- Stock-days with >=15% opening gap within next {FWD} sessions: **{ng}**','',
        '## Strongest behavior differences','', '| Feature | Pre-power-gap mean | Normal mean | Std difference |','|---|---:|---:|---:|']
    for _,r in summ.head(10).iterrows(): md.append(f"| {r.feature} | {r.gap_mean:.3f} | {r.normal_mean:.3f} | {r.std_diff:+.2f} |")
    md += ['','## Forward tail tests (thresholds learned on 2022-23, tested on 2024-25)','', '| Feature | Tail | Days | Hit rate | Base | Lift |','|---|---|---:|---:|---:|---:|']
    for _,r in tails.head(12).iterrows(): md.append(f"| {r.feature} | {r['tail']} | {int(r.days)} | {r.hit_rate:.2%} | {r.base_rate:.2%} | {r.lift:.2f}x |")
    md += ['','## Behavior score forward test','', '| Min score | Days | Hit rate | Base | Lift |','|---:|---:|---:|---:|---:|']
    for _,r in scores.iterrows(): md.append(f"| {int(r.min_score)} | {int(r.days)} | {r.hit_rate:.2%} | {r.base_rate:.2%} | {r.lift:.2f}x |")
    md += ['','## Guardrail','', '- Features use only price/volume data available on the signal date. Future gaps are used only as labels.', '- Quantile thresholds are learned on 2022-23 and evaluated on 2024-25 to reduce look-ahead overfitting.', '- This is still a limited 26-symbol research universe; any positive signal must later be tested on a much broader unseen universe.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))

if __name__=='__main__': main()
