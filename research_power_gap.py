from pathlib import Path
import pandas as pd
import numpy as np

SRC=Path('research/pre_gap/events.csv')
OUT=Path('research/power_gap'); OUT.mkdir(parents=True,exist_ok=True)

FEATURES=['ema20_gt_ema50','trend_stack','shallow_pullback_8','near_high_5','range_contract_075','range_vs_prior_075','volume_dry_080','volume_expand_110','atr_contract_080','atr_expand_110','higher_lows_2of2','close_gt_ema20']
NUM=['ret60_pct','max_drawdown60_pct','pullback_from_60d_close_high_pct','dist_from_60d_high_pct','ema20_slope10_pct','higher_low_score','range10_pct','range20_pct','range10_vs20','range10_vs_prev20','atr10_vs40','vol10_vs40','up_days20_pct','ret_std10_pct']

def bucket(g):
    if g>=15: return 'POWER_15_PLUS'
    if g>=7: return 'MID_7_15'
    return 'SMALL_4_7'

def main():
    ev=pd.read_csv(SRC)
    gaps=ev[ev.group=='GAP'].copy()
    ctr=ev[ev.group=='CONTROL'].copy()
    gaps['bucket']=gaps.gap_pct.map(bucket)
    rows=[]
    for b,g in gaps.groupby('bucket'):
        row={'bucket':b,'events':len(g)}
        for f in FEATURES:
            if f in g: row[f]=pd.to_numeric(g[f],errors='coerce').mean()
        for f in NUM:
            if f in g: row[f]=pd.to_numeric(g[f],errors='coerce').mean()
        rows.append(row)
    out=pd.DataFrame(rows)
    order=pd.CategoricalDtype(['POWER_15_PLUS','MID_7_15','SMALL_4_7'],ordered=True)
    out['bucket']=out.bucket.astype(order); out=out.sort_values('bucket')
    out.to_csv(OUT/'bucket_summary.csv',index=False)

    # Compare power gaps directly against matched controls from same study.
    p=gaps[gaps.bucket=='POWER_15_PLUS']
    comp=[]
    for f in FEATURES:
        if f in p and f in ctr:
            a=pd.to_numeric(p[f],errors='coerce').mean(); c=pd.to_numeric(ctr[f],errors='coerce').mean()
            comp.append({'feature':f,'power_rate':a,'control_rate':c,'difference':a-c})
    for f in NUM:
        if f in p and f in ctr:
            a=pd.to_numeric(p[f],errors='coerce').mean(); c=pd.to_numeric(ctr[f],errors='coerce').mean()
            sd=np.sqrt((pd.to_numeric(p[f],errors='coerce').var()+pd.to_numeric(ctr[f],errors='coerce').var())/2)
            comp.append({'feature':f,'power_mean':a,'control_mean':c,'difference':a-c,'std_diff':(a-c)/sd if sd and np.isfinite(sd) else np.nan})
    pd.DataFrame(comp).to_csv(OUT/'power_vs_controls.csv',index=False)

    lines=['# Power Gap Chart-Pattern Research','',f'- Total gap events: **{len(gaps)}**',f'- Power gaps >=15%: **{len(p)}**',f'- Mid gaps 7–15%: **{len(gaps[(gaps.gap_pct>=7)&(gaps.gap_pct<15)])}**',f'- Small gaps 4–7%: **{len(gaps[(gaps.gap_pct>=4)&(gaps.gap_pct<7)])}**','',
           '## Bucket feature rates','']
    show=['ema20_gt_ema50','trend_stack','shallow_pullback_8','near_high_5','range_contract_075','higher_lows_2of2','close_gt_ema20']
    lines += ['| Bucket | N | '+' | '.join(show)+' |','|---|---:|'+'|'.join(['---:']*len(show))+'|']
    for _,r in out.iterrows():
        vals=' | '.join(f"{float(r.get(f,np.nan)):.0%}" if pd.notna(r.get(f,np.nan)) else '-' for f in show)
        lines.append(f"| {r.bucket} | {int(r.events)} | {vals} |")
    lines += ['','## Gap examples >=15%','', '| Symbol | Date | Gap |','|---|---|---:|']
    for _,r in p.sort_values('gap_pct',ascending=False).iterrows(): lines.append(f"| {r.symbol} | {r.event_date} | {r.gap_pct:.1f}% |")
    lines += ['','## Interpretation','', '- This split tests whether large Power Gaps have a different 45–60 session chart signature from ordinary 4–7% gaps.','- Features are inherited from the matched-control study and use only information available before the gap day.','- If the >=15% bucket shows a materially stronger signature, the next scanner should target Power Gaps rather than all gaps.','']
    (OUT/'report.md').write_text('\n'.join(lines))
    print('\n'.join(lines))

if __name__=='__main__': main()
