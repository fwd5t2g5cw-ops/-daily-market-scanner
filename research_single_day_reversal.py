from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/single_day_reversal'); OUT.mkdir(parents=True,exist_ok=True)
START='2019-01-01'; END='2026-08-24'
HORIZONS=[1,3,5,10]


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2018-01-01',end='2026-08-25',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close','Volume'])
            if len(d)>300: return d
        except Exception as e: print(s,e)
        time.sleep(2*(k+1))
    return pd.DataFrame()


def classify(d):
    x=d.copy()
    c=x.Close.astype(float); o=x.Open.astype(float); h=x.High.astype(float); l=x.Low.astype(float); v=x.Volume.astype(float)
    rng=(h-l).replace(0,np.nan)
    clv=((c-l)/rng).clip(0,1)
    body=(c-o).abs()/rng
    ema20=c.ewm(span=20,adjust=False).mean()
    prev10low=l.shift(1).rolling(10).min()
    prev5high=h.shift(1).rolling(5).max()
    vol20=v.rolling(20).mean()
    ret5=c/c.shift(5)-1
    ret10=c/c.shift(10)-1

    # Core one-day reversal: intraday undercut/retest of prior support and strong reclaim into upper range.
    undercut=(l<prev10low)
    reclaim=(c>prev10low)
    strong_close=clv>=0.70
    bullish=c>o
    meaningful_body=body>=0.35
    vol_expand=v>=vol20*1.10
    ema20_reclaim=(l<ema20) & (c>ema20)
    prev_high_reclaim=c>prev5high

    setup=undercut & reclaim & strong_close & bullish & meaningful_body
    score=(undercut.astype(int)+reclaim.astype(int)+strong_close.astype(int)+bullish.astype(int)+meaningful_body.astype(int)+vol_expand.astype(int)+ema20_reclaim.astype(int)+prev_high_reclaim.astype(int))

    f=pd.DataFrame(index=x.index)
    f['setup']=setup
    f['score']=score
    f['clv']=clv
    f['body_frac']=body
    f['vol_ratio20']=v/vol20
    f['ema20_reclaim']=ema20_reclaim
    f['prev_high_reclaim']=prev_high_reclaim
    f['ret5_before']=ret5
    f['ret10_before']=ret10
    f['close']=c
    for n in HORIZONS:
        f[f'ret_fwd_{n}d']=c.shift(-n)/c-1
        f[f'maxup_fwd_{n}d']=h.shift(-1).rolling(n).max().shift(-(n-1))/c-1
        f[f'maxdd_fwd_{n}d']=l.shift(-1).rolling(n).min().shift(-(n-1))/c-1
    return f


def main():
    # Reuse symbols already present in prior research universe, plus 1810.HK target example.
    src=Path('research/pre_gap_oos/events.csv')
    syms=[]
    if src.exists():
        syms=sorted(pd.read_csv(src).symbol.astype(str).unique())
    syms=list(dict.fromkeys(syms+['1810.HK']))
    frames=[]
    for i,s in enumerate(syms,1):
        print(i,len(syms),s)
        d=dl(s)
        if d.empty: continue
        f=classify(d)
        f['symbol']=s
        f['date']=pd.DatetimeIndex(f.index).tz_localize(None)
        f=f[(f.date>=START)&(f.date<=END)]
        frames.append(f.reset_index(drop=True))
    z=pd.concat(frames,ignore_index=True)
    z.to_csv(OUT/'all_days.csv',index=False)
    sig=z[z.setup.fillna(False)].copy()
    sig.to_csv(OUT/'signals.csv',index=False)

    rows=[]
    for n in HORIZONS:
        a=pd.to_numeric(sig[f'ret_fwd_{n}d'],errors='coerce').dropna()
        base=pd.to_numeric(z[f'ret_fwd_{n}d'],errors='coerce').dropna()
        rows.append({
            'horizon':n,'signals':len(a),'mean_return':a.mean(),'median_return':a.median(),'win_rate':(a>0).mean(),
            'base_mean':base.mean(),'base_win_rate':(base>0).mean(),
            'mean_edge':a.mean()-base.mean(),'win_edge':(a>0).mean()-(base>0).mean()
        })
    summ=pd.DataFrame(rows)
    summ.to_csv(OUT/'summary.csv',index=False)

    # Grade by extra confirmation ingredients rather than altering the core pattern.
    sig['grade_score']=sig['score']
    grades=[]
    for cutoff in [5,6,7,8]:
        m=sig.grade_score>=cutoff
        r={'min_score':cutoff,'signals':int(m.sum())}
        for n in [3,5,10]:
            q=pd.to_numeric(sig.loc[m,f'ret_fwd_{n}d'],errors='coerce').dropna()
            r[f'mean_{n}d']=q.mean() if len(q) else np.nan
            r[f'win_{n}d']=(q>0).mean() if len(q) else np.nan
        grades.append(r)
    pd.DataFrame(grades).to_csv(OUT/'grade_summary.csv',index=False)

    # Target example diagnostic around 2026-08-18.
    ex=sig[(sig.symbol=='1810.HK') & (sig.date>=pd.Timestamp('2026-08-10')) & (sig.date<=pd.Timestamp('2026-08-24'))]
    ex.to_csv(OUT/'1810_aug2026.csv',index=False)

    md=['# Single-Day Reversal / Reclaim Research','',f'- Window: **{START} to {END}**',f'- Symbols: **{len(syms)}**',f'- Total stock-days: **{len(z)}**',f'- Core reversal signals: **{len(sig)}**','',
        'Core setup = undercut prior 10-day low intraday, close back above that level, bullish candle, close in top 30% of range, and body >=35% of daily range. Volume expansion / EMA20 reclaim / prior-5-day-high reclaim are confirmations, not hard requirements.','',
        '## Forward results','', '| Horizon | Signals | Mean | Median | Win rate | Baseline mean | Baseline win | Edge |','|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in summ.iterrows():
        md.append(f"| {int(r.horizon)}d | {int(r.signals)} | {r.mean_return:.2%} | {r.median_return:.2%} | {r.win_rate:.1%} | {r.base_mean:.2%} | {r.base_win_rate:.1%} | {r.mean_edge:+.2%} |")
    md += ['','## Confirmation score test','', '| Min score | Signals | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d |','|---:|---:|---:|---:|---:|---:|---:|---:|']
    gs=pd.DataFrame(grades)
    for _,r in gs.iterrows():
        md.append(f"| {int(r.min_score)} | {int(r.signals)} | {r.mean_3d:.2%} | {r.win_3d:.1%} | {r.mean_5d:.2%} | {r.win_5d:.1%} | {r.mean_10d:.2%} | {r.win_10d:.1%} |")
    md += ['','## 1810.HK diagnostic','']
    if ex.empty:
        md.append('- 1810.HK did not meet the current strict core definition between Aug 10 and Aug 24; inspect which component failed and loosen only if justified.')
    else:
        for _,r in ex.iterrows():
            md.append(f"- {pd.Timestamp(r.date).date()}: score {int(r.score)}, CLV {r.clv:.2f}, volume ratio {r.vol_ratio20:.2f}, EMA20 reclaim={bool(r.ema20_reclaim)}, prior-high reclaim={bool(r.prev_high_reclaim)}")
    md += ['','## Guardrails','', '- No future information is used in signal construction.', '- This first pass is deliberately simple. If it shows edge, validate on a broader unseen universe before adding to production scanners.', '']
    (OUT/'report.md').write_text('\n'.join(md))
    print('\n'.join(md))

if __name__=='__main__': main()
