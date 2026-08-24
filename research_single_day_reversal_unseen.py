from pathlib import Path
import time
import numpy as np
import pandas as pd
import yfinance as yf

OUT=Path('research/single_day_reversal_unseen'); OUT.mkdir(parents=True,exist_ok=True)
START='2020-01-01'; END='2026-08-24'; H=[1,3,5,10]

# Frozen before the test. Deliberately excludes the original 27-symbol discovery universe.
US=['AAPL','MSFT','NVDA','AMZN','META','GOOGL','AVGO','TSLA','JPM','BAC','WMT','COST','HD','LOW','CAT','DE','GE','HON','UNH','LLY','JNJ','ABBV','MRK','PFE','XOM','CVX','COP','SLB','NEE','DUK','SO','PLD','AMT','O','LIN','FCX','NEM','AMD','MU','QCOM','TXN','ADBE','CRM','NOW','INTU','PANW','CRWD','UBER','ABNB','BKNG','DAL','UAL','MAR','MCD','SBUX','NKE','TGT','TJX','LULU','GS','MS','BLK','SCHW','C','AXP','VZ','T','CMCSA','DIS','NFLX','ORCL','IBM','CSCO','AMAT','LRCX','KLAC','ANET','MELI','SHOP']
HK=['0700.HK','9988.HK','3690.HK','9618.HK','9999.HK','1211.HK','1024.HK','0388.HK','1299.HK','2318.HK','0939.HK','3988.HK','1398.HK','0883.HK','0857.HK','2628.HK','0016.HK','0005.HK','0669.HK','2020.HK']
CA=['RY.TO','TD.TO','BMO.TO','BNS.TO','CM.TO','ENB.TO','TRP.TO','CNQ.TO','SU.TO','CNR.TO','CP.TO','BCE.TO','T.TO','ATD.TO','WCN.TO','CSU.TO','SHOP.TO','DOL.TO','NTR.TO','AEM.TO']
SYMS=US+HK+CA


def dl(s):
    for k in range(3):
        try:
            d=yf.download(s,start='2019-01-01',end='2026-08-25',auto_adjust=True,progress=False,threads=False)
            if isinstance(d.columns,pd.MultiIndex): d.columns=d.columns.get_level_values(0)
            d=d.dropna(subset=['Open','High','Low','Close','Volume'])
            if len(d)>250: return d
        except Exception as e: print(s,e)
        time.sleep(1+k)
    return pd.DataFrame()


def features(d):
    c=d.Close.astype(float); o=d.Open.astype(float); h=d.High.astype(float); l=d.Low.astype(float); v=d.Volume.astype(float)
    rng=(h-l).replace(0,np.nan); clv=((c-l)/rng).clip(0,1); body=(c-o).abs()/rng
    ema20=c.ewm(span=20,adjust=False).mean(); p10=l.shift(1).rolling(10).min(); p5h=h.shift(1).rolling(5).max(); v20=v.rolling(20).mean()
    under=l<p10; reclaim=c>p10; strong=clv>=.70; bull=c>o; bodyok=body>=.35
    vol=v>=v20*1.10; ema=(l<ema20)&(c>ema20); ph=c>p5h
    setup=under&reclaim&strong&bull&bodyok
    score=under.astype(int)+reclaim.astype(int)+strong.astype(int)+bull.astype(int)+bodyok.astype(int)+vol.astype(int)+ema.astype(int)+ph.astype(int)
    f=pd.DataFrame(index=d.index)
    f['setup']=setup; f['score']=score; f['vol_expand']=vol; f['ema20_reclaim']=ema; f['prev_high_reclaim']=ph
    f['clv']=clv; f['body_frac']=body; f['vol_ratio']=v/v20
    for n in H:
        f[f'ret{n}']=c.shift(-n)/c-1
        f[f'maxup{n}']=h.shift(-1).rolling(n).max().shift(-(n-1))/c-1
        f[f'maxdd{n}']=l.shift(-1).rolling(n).min().shift(-(n-1))/c-1
    return f


def stats(df,label):
    r={'group':label,'n':len(df)}
    for n in [3,5,10]:
        q=pd.to_numeric(df[f'ret{n}'],errors='coerce').dropna(); up=pd.to_numeric(df[f'maxup{n}'],errors='coerce').dropna(); dd=pd.to_numeric(df[f'maxdd{n}'],errors='coerce').dropna()
        r[f'mean{n}']=q.mean(); r[f'win{n}']=(q>0).mean(); r[f'med{n}']=q.median(); r[f'maxup{n}']=up.mean(); r[f'maxdd{n}']=dd.mean()
    return r


def main():
    frames=[]; ok=[]
    for i,s in enumerate(SYMS,1):
        print(i,len(SYMS),s)
        d=dl(s)
        if d.empty: continue
        f=features(d); f['symbol']=s; f['market']='HK' if s.endswith('.HK') else ('CA' if s.endswith('.TO') else 'US')
        f['date']=pd.DatetimeIndex(f.index).tz_localize(None); f=f[(f.date>=START)&(f.date<=END)].reset_index(drop=True)
        frames.append(f); ok.append(s)
    z=pd.concat(frames,ignore_index=True); sig=z[z.setup.fillna(False)].copy()
    z.to_csv(OUT/'all_days.csv',index=False); sig.to_csv(OUT/'signals.csv',index=False)

    rows=[stats(z,'BASELINE'),stats(sig,'CORE')]
    for k in [6,7,8]: rows.append(stats(sig[sig.score>=k],f'SCORE>={k}'))
    for c in ['vol_expand','ema20_reclaim','prev_high_reclaim']:
        rows.append(stats(sig[sig[c]],c.upper()))
    for m in ['US','HK','CA']:
        rows.append(stats(sig[sig.market==m],m+'_CORE'))
        rows.append(stats(sig[(sig.market==m)&(sig.score>=7)],m+'_SCORE>=7'))
    summary=pd.DataFrame(rows); summary.to_csv(OUT/'summary.csv',index=False)

    # Exact confirmation combinations among core signals.
    combos=[]
    for mask in range(8):
        q=sig.copy(); names=[]
        for bit,c in enumerate(['vol_expand','ema20_reclaim','prev_high_reclaim']):
            want=bool(mask&(1<<bit)); q=q[q[c]==want]; names.append(c+'='+str(int(want)))
        if len(q)>=10: combos.append(stats(q,';'.join(names)))
    combos=pd.DataFrame(combos).sort_values('mean10',ascending=False); combos.to_csv(OUT/'confirmation_combos.csv',index=False)

    md=['# Single-Day Reversal — Broad Unseen Validation','',f'- Frozen universe: **{len(SYMS)} symbols** (US {len(US)}, HK {len(HK)}, Canada {len(CA)})',f'- Downloaded successfully: **{len(ok)}**',f'- Window: **{START} to {END}**',f'- Stock-days: **{len(z)}**',f'- Core signals: **{len(sig)}**','',
        'Universe and rules were frozen before this run and exclude the original discovery universe.','',
        '## Main results','', '| Group | N | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg max-up 10d | Avg max-DD 10d |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in summary.iterrows():
        md.append(f"| {r['group']} | {int(r['n'])} | {r['mean3']:.2%} | {r['win3']:.1%} | {r['mean5']:.2%} | {r['win5']:.1%} | {r['mean10']:.2%} | {r['win10']:.1%} | {r['maxup10']:.2%} | {r['maxdd10']:.2%} |")
    md += ['','## Exact confirmation combinations (N>=10)','', '| Combination | N | Mean 5d | Win 5d | Mean 10d | Win 10d |','|---|---:|---:|---:|---:|---:|']
    for _,r in combos.iterrows(): md.append(f"| {r['group']} | {int(r['n'])} | {r['mean5']:.2%} | {r['win5']:.1%} | {r['mean10']:.2%} | {r['win10']:.1%} |")
    md += ['','## Decision rule','', '- Only promote this setup if the broad unseen universe preserves a meaningful 5–10 day return/win-rate edge and the stronger confirmation bucket has enough samples.', '- Score 8 from the discovery set had only 14 samples, so it must not be trusted unless it replicates here.','']
    (OUT/'report.md').write_text('\n'.join(md)); print('\n'.join(md))

if __name__=='__main__': main()
