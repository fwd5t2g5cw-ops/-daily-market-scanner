from pathlib import Path
import pandas as pd

SRC=Path('research/pre_gap_oos/events.csv')
OUT=Path('research/power_gap_oos')
OUT.mkdir(parents=True,exist_ok=True)

# Older unseen-date validation focused only on >=15% Power Gaps.
def summarize(df,name):
    g=df[(df.group=='GAP') & (df.gap_pct>=15)].copy()
    c=df[df.group=='CONTROL'].copy()
    lines=[f'## {name}', '', f'- Power gaps >=15%: **{len(g)}**', f'- Controls: **{len(c)}**']
    for t in [3,4,5,6]:
        gr=(g.max_score_10d>=t).mean() if len(g) else 0
        cr=(c.max_score_10d>=t).mean() if len(c) else 0
        lines.append(f'- Score >= {t} within T-10..T-1: power gap **{gr:.0%}**, controls **{cr:.0%}**, separation **{gr-cr:+.0%}**')
    if len(g):
        lines += ['', '| Symbol | Date | Gap | Max score in prior 10d |', '|---|---|---:|---:|']
        for _,r in g.sort_values('gap_pct',ascending=False).iterrows():
            lines.append(f"| {r.symbol} | {r.date} | {r.gap_pct:.1f}% | {int(r.max_score_10d)} |")
    return lines

def main():
    df=pd.read_csv(SRC)
    lines=['# Older Out-of-Sample Power-Gap Test','', 'Uses the existing 2023-01-01 to 2025-08-31 holdout events. A Power Gap is an opening gap >=15%. The score is the same 6-component chart-pattern score used in the earlier holdout test.','']
    lines += summarize(df,'All holdout dates')
    lines += ['', '## Interpretation','', '- If Power Gaps show materially higher pre-gap scores than controls, the chart pattern may be specific to large gaps even though it failed for all >=4% gaps.', '- If separation remains flat or negative, the current chart-only pattern does not generalize even for Power Gaps.', '']
    (OUT/'report.md').write_text('\n'.join(lines))
    df[(df.group=='GAP') & (df.gap_pct>=15)].to_csv(OUT/'power_gap_events.csv',index=False)
    print('\n'.join(lines))

if __name__=='__main__': main()
