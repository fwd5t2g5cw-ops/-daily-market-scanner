from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

SRC=Path('research/two_stage_reversal/events.csv')
OUT=Path('research/reversal_rr'); OUT.mkdir(parents=True,exist_ok=True)
MAX_HOLD=10
TARGETS=[1,2,3]


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


def simulate(d, entry_date, reversal_date, entry, r_mult):
    if entry_date not in d.index or reversal_date not in d.index: return None
    j=d.index.get_loc(entry_date); i=d.index.get_loc(reversal_date)
    if isinstance(j,slice) or isinstance(i,slice): return None
    stop=float(d.Low.iloc[i])
    risk=entry-stop
    if not np.isfinite(risk) or risk<=0: return None
    risk_pct=risk/entry
    # exclude structurally unusable trades with extreme stop distance
    if risk_pct>0.20: return None
    target=entry+r_mult*risk
    outcome='TIME'; exit_px=np.nan; exit_day=None; bars=0
    for k in range(1,MAX_HOLD+1):
        if j+k>=len(d): break
        lo=float(d.Low.iloc[j+k]); hi=float(d.High.iloc[j+k]); close=float(d.Close.iloc[j+k]); bars=k
        # Conservative ambiguity rule: if stop and target both trade same day, count stop first.
        if lo<=stop:
            outcome='STOP'; exit_px=stop; exit_day=d.index[j+k]; break
        if hi>=target:
            outcome='TARGET'; exit_px=target; exit_day=d.index[j+k]; break
    if not np.isfinite(exit_px):
        k=min(MAX_HOLD,len(d)-1-j)
        if k<=0: return None
        bars=k; exit_px=float(d.Close.iloc[j+k]); exit_day=d.index[j+k]
    ret=exit_px/entry-1
    rret=(exit_px-entry)/risk
    return {'stop':stop,'risk_pct':risk_pct,'target':target,'outcome':outcome,'exit_date':exit_day.date(),'bars_held':bars,'ret':ret,'R':rret}


def main():
    ev=pd.read_csv(SRC)
    ev['entry_date']=pd.to_datetime(ev.entry_date); ev['reversal_date']=pd.to_datetime(ev.reversal_date)
    rows=[]
    for n,s in enumerate(sorted(ev.symbol.unique()),1):
        print(n,ev.symbol.nunique(),s)
        d=dl(s)
        if d.empty: continue
        d.index=pd.DatetimeIndex(d.index).tz_localize(None)
        for _,r in ev[ev.symbol==s].iterrows():
            for t in TARGETS:
                q=simulate(d,pd.Timestamp(r.entry_date),pd.Timestamp(r.reversal_date),float(r.entry),t)
                if q is None: continue
                rows.append({'symbol':s,'market':r.market,'rule':r.rule,'reversal_date':r.reversal_date.date(),'entry_date':r.entry_date.date(),'target_R':t,**q})
    z=pd.DataFrame(rows); z.to_csv(OUT/'trades.csv',index=False)
    sr=[]
    for (rule,t),g in z.groupby(['rule','target_R']):
        sr.append({'rule':rule,'target_R':t,'N':len(g),'target_rate':(g.outcome=='TARGET').mean(),'stop_rate':(g.outcome=='STOP').mean(),'time_rate':(g.outcome=='TIME').mean(),'mean_return':g.ret.mean(),'median_return':g.ret.median(),'mean_R':g.R.mean(),'win_rate':(g.ret>0).mean(),'avg_risk_pct':g.risk_pct.mean(),'avg_bars':g.bars_held.mean()})
    summ=pd.DataFrame(sr).sort_values(['rule','target_R']); summ.to_csv(OUT/'summary.csv',index=False)
    mr=[]
    for (m,rule,t),g in z.groupby(['market','rule','target_R']):
        if len(g)<20: continue
        mr.append({'market':m,'rule':rule,'target_R':t,'N':len(g),'target_rate':(g.outcome=='TARGET').mean(),'stop_rate':(g.outcome=='STOP').mean(),'mean_return':g.ret.mean(),'mean_R':g.R.mean(),'win_rate':(g.ret>0).mean(),'avg_risk_pct':g.risk_pct.mean()})
    ms=pd.DataFrame(mr).sort_values(['market','rule','target_R']); ms.to_csv(OUT/'market_summary.csv',index=False)

    md=['# Single-Day Reversal — Stop / R-Multiple Validation','',
        '- Source: two-stage reversal entries from the frozen broad unseen universe.',
        '- Stop: reversal-day low.',
        '- Targets: 1R, 2R, 3R.',
        f'- Maximum holding period: {MAX_HOLD} sessions after entry.',
        '- If stop and target are both touched on the same daily bar, stop is assumed first (conservative).',
        '- Trades requiring >20% stop distance are excluded as structurally impractical.','',
        '## Overall','',
        '| Rule | Target | N | Target hit | Stop hit | Mean return | Mean R | Win rate | Avg stop distance |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in summ.iterrows():
        md.append(f"| {r.rule} | {int(r.target_R)}R | {int(r.N)} | {r.target_rate:.1%} | {r.stop_rate:.1%} | {r.mean_return:.2%} | {r.mean_R:.2f}R | {r.win_rate:.1%} | {r.avg_risk_pct:.2%} |")
    md += ['','## By market (N>=20)','',
           '| Market | Rule | Target | N | Target hit | Stop hit | Mean return | Mean R | Win rate | Avg stop distance |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in ms.iterrows():
        md.append(f"| {r.market} | {r.rule} | {int(r.target_R)}R | {int(r.N)} | {r.target_rate:.1%} | {r.stop_rate:.1%} | {r.mean_return:.2%} | {r.mean_R:.2f}R | {r.win_rate:.1%} | {r.avg_risk_pct:.2%} |")
    md += ['','## Reading the test','',
           '- A useful trading rule should have positive mean R after the conservative stop-first assumption, not merely a high target-hit rate.',
           '- Market-specific results matter because the prior validation showed different behavior in US, HK and Canada.','']
    (OUT/'report.md').write_text('\n'.join(md))
    print('\n'.join(md))

if __name__=='__main__': main()
