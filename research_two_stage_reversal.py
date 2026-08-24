from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

SRC=Path('research/single_day_reversal_unseen/signals.csv')
OUT=Path('research/two_stage_reversal'); OUT.mkdir(parents=True,exist_ok=True)
FWD_ENTRY=3
HOLD=[3,5,10]

def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2019-01-01',end='2026-08-25',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close','Volume'])
            if len(d)>100: return d
        except Exception as e: print(s,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()

def market_of(s):
    if s.endswith('.HK'): return 'HK'
    if s.endswith('.TO'): return 'CA'
    return 'US'

def main():
    sig=pd.read_csv(SRC)
    sig['date']=pd.to_datetime(sig['date'])
    symbols=sorted(sig.symbol.astype(str).unique())
    events=[]
    for n,s in enumerate(symbols,1):
        print(n,len(symbols),s)
        d=dl(s)
        if d.empty: continue
        d=d.copy(); d.index=pd.DatetimeIndex(d.index).tz_localize(None)
        c=d.Close.astype(float); h=d.High.astype(float); l=d.Low.astype(float)
        ema20=c.ewm(span=20,adjust=False).mean()
        prev5h=h.shift(1).rolling(5).max()
        s0=sig[sig.symbol==s].copy()
        for _,r in s0.iterrows():
            day=pd.Timestamp(r.date)
            if day not in d.index: continue
            i=d.index.get_loc(day)
            if isinstance(i,slice) or i+1>=len(d): continue
            rev_high=float(h.iloc[i]); rev_close=float(c.iloc[i])
            p5=float(prev5h.iloc[i]) if pd.notna(prev5h.iloc[i]) else np.nan
            # Search next 1-3 sessions for first confirmation.
            choices=[]
            for j in range(i+1,min(i+1+FWD_ENTRY,len(d))):
                close=float(c.iloc[j]); high=float(h.iloc[j]); low=float(l.iloc[j])
                choices.append({
                    'j':j,'delay':j-i,'date':d.index[j],
                    'break_rev_high':close>rev_high,
                    'break_prev5_high':pd.notna(p5) and close>p5,
                    'ema20_hold':close>float(ema20.iloc[j]),
                    'both_breaks':(close>rev_high) and (pd.notna(p5) and close>p5),
                })
            rules={
                'REV_HIGH':lambda q:q['break_rev_high'],
                'PREV5_HIGH':lambda q:q['break_prev5_high'],
                'REV_HIGH+EMA20':lambda q:q['break_rev_high'] and q['ema20_hold'],
                'BOTH_HIGHS':lambda q:q['both_breaks'],
                'BOTH_HIGHS+EMA20':lambda q:q['both_breaks'] and q['ema20_hold'],
            }
            for name,fn in rules.items():
                hit=next((q for q in choices if fn(q)),None)
                if hit is None: continue
                j=hit['j']; entry=float(c.iloc[j])
                row={'symbol':s,'market':market_of(s),'reversal_date':day.date(),'entry_date':hit['date'].date(),'delay':hit['delay'],'rule':name,'entry':entry,'reversal_score':int(r.get('score',0))}
                for k in HOLD:
                    if j+k<len(d):
                        row[f'ret_{k}d']=float(c.iloc[j+k]/entry-1)
                        window_h=h.iloc[j+1:j+k+1]; window_l=l.iloc[j+1:j+k+1]
                        row[f'maxup_{k}d']=float(window_h.max()/entry-1)
                        row[f'maxdd_{k}d']=float(window_l.min()/entry-1)
                    else:
                        row[f'ret_{k}d']=np.nan; row[f'maxup_{k}d']=np.nan; row[f'maxdd_{k}d']=np.nan
                events.append(row)
    z=pd.DataFrame(events)
    z.to_csv(OUT/'events.csv',index=False)
    rows=[]
    for rule,g in z.groupby('rule'):
        r={'rule':rule,'N':len(g),'avg_delay':g.delay.mean()}
        for k in HOLD:
            q=g[f'ret_{k}d'].dropna(); r[f'mean_{k}d']=q.mean(); r[f'win_{k}d']=(q>0).mean(); r[f'median_{k}d']=q.median(); r[f'maxup_{k}d']=g[f'maxup_{k}d'].mean(); r[f'maxdd_{k}d']=g[f'maxdd_{k}d'].mean()
        rows.append(r)
    summ=pd.DataFrame(rows).sort_values('mean_5d',ascending=False)
    summ.to_csv(OUT/'summary.csv',index=False)
    mrows=[]
    for (m,rule),g in z.groupby(['market','rule']):
        if len(g)<10: continue
        mrows.append({'market':m,'rule':rule,'N':len(g),'mean_5d':g.ret_5d.mean(),'win_5d':(g.ret_5d>0).mean(),'mean_10d':g.ret_10d.mean(),'win_10d':(g.ret_10d>0).mean(),'maxdd_10d':g.maxdd_10d.mean()})
    ms=pd.DataFrame(mrows).sort_values(['market','mean_5d'],ascending=[True,False])
    ms.to_csv(OUT/'market_summary.csv',index=False)
    md=['# Two-Stage Single-Day Reversal Validation','',f'- Source: frozen broad unseen reversal signals ({len(sig)} core events)','- Entry confirmation window: next 1–3 sessions','- Entry is confirmation-day close; returns are measured after entry, so reversal-day gains are not counted.','', '## Rules','', '- REV_HIGH: close above reversal-day high', '- PREV5_HIGH: close above the pre-reversal 5-day high', '- REV_HIGH+EMA20: reversal-high breakout while closing above EMA20', '- BOTH_HIGHS: close above both reversal high and pre-reversal 5-day high', '- BOTH_HIGHS+EMA20: both-high breakout and above EMA20','', '## Overall results','', '| Rule | N | Avg delay | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg maxDD 10d |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in summ.iterrows(): md.append(f"| {r.rule} | {int(r.N)} | {r.avg_delay:.2f} | {r.mean_3d:.2%} | {r.win_3d:.1%} | {r.mean_5d:.2%} | {r.win_5d:.1%} | {r.mean_10d:.2%} | {r.win_10d:.1%} | {r.maxdd_10d:.2%} |")
    md += ['','## By market (N>=10)','', '| Market | Rule | N | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg maxDD 10d |','|---|---|---:|---:|---:|---:|---:|---:|']
    for _,r in ms.iterrows(): md.append(f"| {r.market} | {r.rule} | {int(r.N)} | {r.mean_5d:.2%} | {r.win_5d:.1%} | {r.mean_10d:.2%} | {r.win_10d:.1%} | {r.maxdd_10d:.2%} |")
    md += ['','## Decision','', '- The two-stage version is useful only if confirmation improves 5–10 day expectancy and/or drawdown versus buying the reversal close, with enough samples to survive market splits.','']
    (OUT/'report.md').write_text('\n'.join(md))
    print('\n'.join(md))

if __name__=='__main__': main()
