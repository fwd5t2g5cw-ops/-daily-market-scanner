from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/behavior_older_validation'); OUT.mkdir(parents=True,exist_ok=True)
SRC=Path('research/accumulation_behavior/stock_days.csv')
POWER=15.0; FWD=10

def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2017-01-01',end='2022-01-15',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close','Volume'])
            if len(d)>300: return d
        except Exception as e: print(s,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()

def features(d):
    x=d.copy(); c=x.Close.astype(float); o=x.Open.astype(float); h=x.High.astype(float); l=x.Low.astype(float); v=x.Volume.astype(float)
    ret=c.pct_change(); rng=(h-l)/c.shift(1).replace(0,np.nan); clv=((c-l)/(h-l).replace(0,np.nan)).clip(0,1).fillna(.5)
    vol_rel=v/v.rolling(20).median()
    absorb=((vol_rel>=1.5)&(ret>=-0.01)&(clv>=0.5)).astype(int)
    effort=((vol_rel>=1.5)&(ret.abs()<=0.012)&(clv>=0.45)).astype(int)
    downrej=((vol_rel>=1.3)&(ret<0)&(clv>=0.65)).astype(int)
    pl=l.shift(1).rolling(10).min(); under=((l<pl)&(c>pl)).astype(int)
    upmask=ret>0; dnmask=ret<0
    upv=v.where(upmask,0).rolling(20).sum(); dnv=v.where(dnmask,0).rolling(20).sum()
    upcnt=upmask.astype(int).rolling(20).sum(); dncnt=dnmask.astype(int).rolling(20).sum()
    hv=vol_rel>=1.3; hvc=hv.astype(int).rolling(10).sum(); hvs=(clv.where(hv,0).rolling(10).sum()/hvc.replace(0,np.nan)).fillna(.5)
    f=pd.DataFrame(index=x.index)
    f['absorb20']=absorb.rolling(20).sum(); f['effort_no_down20']=effort.rolling(20).sum(); f['down_reject20']=downrej.rolling(20).sum(); f['undercut_reclaim20']=under.rolling(20).sum()
    f['highvol_close_strength10']=hvs; f['volume_cluster10']=hvc; f['ret20']=c/c.shift(20)-1
    f['vol_contract10_40']=v.rolling(10).mean()/v.rolling(40).mean(); f['range_contract10_40']=rng.rolling(10).mean()/rng.rolling(40).mean()
    gap=(o/c.shift(1)-1)*100; a=gap.to_numpy(); y=np.zeros(len(x),int)
    for i in range(len(x)):
        z=a[i+1:min(i+1+FWD,len(x))]
        if len(z): y[i]=int(np.nanmax(z)>=POWER)
    f['future_power_gap']=y
    return f

def main():
    newer=pd.read_csv(SRC,parse_dates=['date']); tr=newer[(newer.date>='2022-01-01')&(newer.date<'2024-01-01')]
    symbols=sorted(newer.symbol.unique())
    q={
      'absorb_high':tr.absorb20.quantile(.75),
      'effort_low':tr.effort_no_down20.quantile(.25),
      'downreject_low':tr.down_reject20.quantile(.25),
      'undercut_low':tr.undercut_reclaim20.quantile(.25),
      'hvclose_low':tr.highvol_close_strength10.quantile(.25),
      'ret20_high':tr.ret20.quantile(.75),
      'volcluster_high':tr.volume_cluster10.quantile(.75),
    }
    frames=[]
    for i,s in enumerate(symbols,1):
        print(i,len(symbols),s); d=dl(s)
        if d.empty: continue
        f=features(d); f['symbol']=s; f['date']=pd.DatetimeIndex(f.index).tz_localize(None)
        f=f[(f.date>='2018-01-01')&(f.date<='2021-12-31')].dropna()
        frames.append(f)
    z=pd.concat(frames,ignore_index=True); base=z.future_power_gap.mean()
    cond={
      'absorb_high':z.absorb20>=q['absorb_high'], 'effort_low':z.effort_no_down20<=q['effort_low'], 'downreject_low':z.down_reject20<=q['downreject_low'],
      'undercut_low':z.undercut_reclaim20<=q['undercut_low'], 'hvclose_low':z.highvol_close_strength10<=q['hvclose_low'], 'ret20_high':z.ret20>=q['ret20_high'], 'volcluster_high':z.volume_cluster10>=q['volcluster_high']}
    rules=[
      ('effort_low + undercut_low',['effort_low','undercut_low']),
      ('absorb_high + effort_low + undercut_low',['absorb_high','effort_low','undercut_low']),
      ('effort_low + downreject_low + undercut_low',['effort_low','downreject_low','undercut_low']),
      ('effort_low + undercut_low + hvclose_low',['effort_low','undercut_low','hvclose_low']),
      ('absorb_high + effort_low + downreject_low + undercut_low',['absorb_high','effort_low','downreject_low','undercut_low']),
      ('effort_low + undercut_low + hvclose_low + ret20_high',['effort_low','undercut_low','hvclose_low','ret20_high']),
      ('effort_low + undercut_low + volcluster_high + hvclose_low',['effort_low','undercut_low','volcluster_high','hvclose_low']),
    ]
    rows=[]
    for name,parts in rules:
        m=pd.Series(True,index=z.index)
        for p in parts: m &= cond[p]
        n=int(m.sum()); hits=int(z.loc[m,'future_power_gap'].sum()); rate=hits/n if n else np.nan
        rows.append({'rule':name,'days':n,'hits':hits,'hit_rate':rate,'base_rate':base,'lift':rate/base if base and n else np.nan})
    r=pd.DataFrame(rows).sort_values('lift',ascending=False); r.to_csv(OUT/'results.csv',index=False)
    md=['# Older Unseen Behavior Validation','', '- Validation period: **2018-2021**', '- Thresholds frozen from **2022-2023** research', f'- Eligible stock-days: **{len(z)}**', f'- Base next-10-session >=15% gap rate: **{base:.2%}**','', '| Rule | Days | Hits | Hit rate | Lift |','|---|---:|---:|---:|---:|']
    for _,x in r.iterrows(): md.append(f"| {x.rule} | {int(x.days)} | {int(x.hits)} | {x.hit_rate:.2%} | {x.lift:.2f}x |")
    md += ['','A rule is only interesting if the lift survives this older unseen period as well as the 2024-25 forward test.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))
if __name__=='__main__': main()
