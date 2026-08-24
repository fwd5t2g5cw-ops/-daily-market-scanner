from pathlib import Path
import itertools
import pandas as pd

SRC=Path('research/accumulation_behavior/stock_days.csv')
OUT=Path('research/behavior_combos'); OUT.mkdir(parents=True,exist_ok=True)

def main():
    z=pd.read_csv(SRC,parse_dates=['date'])
    train=z[z.date<'2024-01-01'].copy(); test=z[z.date>='2024-01-01'].copy()
    base=test.future_power_gap.mean()
    defs={}
    specs={
      'absorb_high':('absorb20','.75','high'),
      'effort_low':('effort_no_down20','.25','low'),
      'downreject_low':('down_reject20','.25','low'),
      'undercut_low':('undercut_reclaim20','.25','low'),
      'volcluster_high':('volume_cluster10','.75','high'),
      'hvclose_low':('highvol_close_strength10','.25','low'),
      'ret20_high':('ret20','.75','high'),
      'ret20_low':('ret20','.25','low'),
      'dist_high_near':('dist60high','.75','high'),
      'range_expand':('range_contract10_40','.75','high'),
      'vol_expand':('vol_contract10_40','.75','high'),
    }
    thresholds={}
    for name,(col,q,side) in specs.items():
        t=train[col].quantile(float(q)); thresholds[name]=t
        defs[name]=(test[col]>=t) if side=='high' else (test[col]<=t)
    rows=[]
    for r in [1,2,3,4]:
      for combo in itertools.combinations(defs,r):
        m=pd.Series(True,index=test.index)
        for k in combo: m &= defs[k]
        n=int(m.sum())
        if n<150: continue
        hits=int(test.loc[m,'future_power_gap'].sum()); hit=hits/n
        rows.append({'rule':' + '.join(combo),'n':n,'hits':hits,'hit_rate':hit,'base_rate':base,'lift':hit/base if base else 0})
    df=pd.DataFrame(rows).sort_values(['lift','hits','n'],ascending=[False,False,False])
    df.to_csv(OUT/'combo_results.csv',index=False)
    md=['# Behavior Combination Forward Test','', '- Train thresholds: **2022-2023**', '- Forward test: **2024-2025**', f'- Base next-10-session >=15% gap rate: **{base:.2%}**','',
        '## Top combinations (minimum 150 stock-days)','', '| Rule | Days | Hits | Hit rate | Lift |','|---|---:|---:|---:|---:|']
    for _,x in df.head(25).iterrows(): md.append(f"| {x.rule} | {int(x.n)} | {int(x.hits)} | {x.hit_rate:.2%} | {x.lift:.2f}x |")
    md += ['','## Notes','', '- These combinations are searched only from thresholds fixed on the earlier 2022-23 period.', '- Because many combinations are tested, top results can still be selection noise; any promising rule must be validated on a third unseen period or broader universe.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))
if __name__=='__main__': main()
