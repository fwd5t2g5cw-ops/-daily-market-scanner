from pathlib import Path
import pandas as pd
import numpy as np

SRC=Path('research/single_day_reversal/signals.csv')
OUT=Path('research/single_day_reversal_components'); OUT.mkdir(parents=True,exist_ok=True)

def stat(q,label):
    r={'group':label,'n':len(q)}
    for n in [3,5,10]:
        x=pd.to_numeric(q[f'ret_fwd_{n}d'],errors='coerce').dropna()
        r[f'mean{n}']=x.mean(); r[f'win{n}']=(x>0).mean(); r[f'median{n}']=x.median()
    return r

def main():
    z=pd.read_csv(SRC)
    for c in ['vol_expand','ema20_reclaim','prev_high_reclaim']:
        z[c]=z[c].astype(str).str.lower().isin(['true','1'])
    rows=[stat(z,'CORE')]
    for c in ['vol_expand','ema20_reclaim','prev_high_reclaim']:
        rows += [stat(z[z[c]],c+'=YES'),stat(z[~z[c]],c+'=NO')]
    # Every exact 3-bit confirmation state.
    exact=[]
    for v in [False,True]:
      for e in [False,True]:
       for p in [False,True]:
        q=z[(z.vol_expand==v)&(z.ema20_reclaim==e)&(z.prev_high_reclaim==p)]
        exact.append(stat(q,f'VOL{int(v)} EMA{int(e)} HIGH{int(p)}'))
    # Incremental combinations, requiring at least specified confirmations.
    combo=[]
    specs=[('VOL+EMA',['vol_expand','ema20_reclaim']),('VOL+HIGH',['vol_expand','prev_high_reclaim']),('EMA+HIGH',['ema20_reclaim','prev_high_reclaim']),('ALL3',['vol_expand','ema20_reclaim','prev_high_reclaim'])]
    for name,cs in specs:
        m=np.ones(len(z),dtype=bool)
        for c in cs:m &= z[c].to_numpy()
        combo.append(stat(z[m],name))
    out=pd.DataFrame(rows+exact+combo); out.to_csv(OUT/'summary.csv',index=False)
    md=['# Single-Day Reversal Confirmation Components','', '| Group | N | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d |','|---|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in out.iterrows():
        md.append(f"| {r.group} | {int(r.n)} | {r.mean3:.2%} | {r.win3:.1%} | {r.mean5:.2%} | {r.win5:.1%} | {r.mean10:.2%} | {r.win10:.1%} |")
    md += ['','Score 8 means all five core conditions plus all three confirmations. Score 7 means any two of the three confirmations.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))
if __name__=='__main__': main()
