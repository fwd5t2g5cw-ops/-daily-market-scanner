from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

UNIVERSE = Path('data/us_1b_universe.txt')
OUTDIR = Path('backtest_us_1y_results')
BENCHMARK = 'SPY'

EMA20, EMA50, SMA200 = 20, 50, 200
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500_000
MIN_DOLLAR_VOL = 20_000_000.0
HIGH_LOOKBACK = 252
MAX_BELOW_HIGH = 20.0
RESISTANCE_BARS = 50
MIN_BREAKOUT_PCT = 1.0
MAX_RETEST_BARS = 30
MAX_UNDERCUT_PCT = 3.0
MAX_ABOVE_EMA20 = 12.0
RS_LOOKBACK = 63
TOUCH_TOL_PCT = 0.25
FIB_ENTRY = 0.786
FIB_DEN = 1.0 - FIB_ENTRY
FOLLOW_DAYS = 20


def split(raw, syms):
    out = {}
    if raw is None or raw.empty: return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0=set(map(str,raw.columns.get_level_values(0)))
        fields={'Open','High','Low','Close','Volume'}
        by_ticker = len(fields & level0) < 3
        for s in syms:
            try:
                x=raw.xs(s,axis=1,level=0 if by_ticker else 1,drop_level=True).dropna(how='all')
                if not x.empty: out[s]=x
            except Exception: pass
    elif len(syms)==1:
        out[syms[0]]=raw.dropna(how='all')
    return out


def download(syms, chunk=120):
    out={}
    for i in range(0,len(syms),chunk):
        g=syms[i:i+chunk]
        print(f'batch {i+1}-{min(i+chunk,len(syms))}/{len(syms)}')
        try:
            raw=yf.download(g,period='2y',interval='1d',auto_adjust=True,progress=False,threads=True,group_by='ticker')
            out.update(split(raw,g))
        except Exception as e: print('batch failed',e)
    return out


def candle_pattern(o,h,l,c,po,pc):
    r=max(h-l,1e-9); body=abs(c-o); upper=h-max(o,c); lower=min(o,c)-l
    if body/r <= .10: return 'DOJI'
    if c>o and po>pc and c>=po and o<=pc: return 'BULLISH_ENGULFING'
    if c<o and pc>po and o>=pc and c<=po: return 'BEARISH_ENGULFING'
    if lower>=2*body and upper<=body: return 'HAMMER'
    if upper>=2*body and lower<=body: return 'SHOOTING_STAR'
    if c>o and body/r>=.65: return 'STRONG_BULL_CANDLE'
    if c<o and body/r>=.65: return 'STRONG_BEAR_CANDLE'
    return 'BULL_CANDLE' if c>o else 'BEAR_CANDLE'


def evaluate_symbol(sym, d, spy):
    d=d[['Open','High','Low','Close','Volume']].dropna().copy()
    spy=spy[['Open','High','Low','Close','Volume']].dropna().copy()
    common=d.index.intersection(spy.index)
    d=d.loc[common]; spy=spy.loc[common]
    if len(d)<320: return []

    c=d.Close; h=d.High; l=d.Low; o=d.Open; v=d.Volume
    e20=c.ewm(span=20,adjust=False).mean(); e50=c.ewm(span=50,adjust=False).mean(); s200=c.rolling(200).mean()
    avgvol=v.rolling(20).mean(); avgdol=(c*v).rolling(20).mean(); yh=h.rolling(252).max()
    res=h.shift(1).rolling(50).max(); bo=(c>res*1.01)&(c.shift(1)<=res)
    spyc=spy.Close; spye20=spyc.ewm(span=20,adjust=False).mean(); spye50=spyc.ewm(span=50,adjust=False).mean()

    last_bo=-10_000; level=np.nan
    rows=[]
    start=max(252, len(d)-260)  # about one trading year
    for i in range(start,len(d)-1):
        if bool(bo.iloc[i]):
            last_bo=i; level=float(res.iloc[i]); continue
        age=i-last_bo
        if age<1 or age>30 or not np.isfinite(level): continue

        close=float(c.iloc[i]); op=float(o.iloc[i]); hi=float(h.iloc[i]); lo=float(l.iloc[i])
        strong=(close>e20.iloc[i]>e50.iloc[i]>s200.iloc[i] and e50.iloc[i]>e50.iloc[i-10] and s200.iloc[i]>s200.iloc[i-20])
        notext=((close/e20.iloc[i]-1)*100)<=12
        liquid=(close>=10 and avgvol.iloc[i]>=500000 and avgdol.iloc[i]>=20000000)
        below=((yh.iloc[i]-close)/yh.iloc[i]*100) if yh.iloc[i]>0 else np.nan
        nearhigh=np.isfinite(below) and below<=20
        stockret=close/c.iloc[i-63]-1; spyret=spyc.iloc[i]/spyc.iloc[i-63]-1
        rs=stockret-spyret; outperf=rs>0
        market=(spyc.iloc[i]>spye20.iloc[i]>spye50.iloc[i])

        slight=(lo<level and lo>=level*.97); reclaimed=close>level
        bull=(close>op and close>=(hi+lo)/2)
        entry=bool(strong and notext and liquid and nearhigh and outperf and market and slight and reclaimed and bull)

        touched_bo=lo<=level*(1+TOUCH_TOL_PCT/100); touched_ema=lo<=e20.iloc[i]*(1+TOUCH_TOL_PCT/100)
        double=bool(touched_bo and touched_ema and lo>=level*.97 and close>level and close>e20.iloc[i])
        reclaim=bool(touched_bo and lo>=level*.97 and close>level)
        if not (entry or double or reclaim): continue

        stop=lo; risk=close-stop
        if risk<=0: continue
        target=stop+risk/FIB_DEN
        outcome='OPEN'; exit_i=None
        for j in range(i+1,min(len(d),i+1+FOLLOW_DAYS)):
            hit_s=float(l.iloc[j])<=stop; hit_t=float(h.iloc[j])>=target
            if hit_s and hit_t: outcome='STOP_AMBIGUOUS'; exit_i=j; break
            if hit_s: outcome='STOP'; exit_i=j; break
            if hit_t: outcome='TARGET0'; exit_i=j; break
        days=(exit_i-i) if exit_i is not None else np.nan
        patt=candle_pattern(op,hi,lo,close,float(o.iloc[i-1]),float(c.iloc[i-1]))
        rows.append({'date':str(pd.Timestamp(d.index[i]).date()),'symbol':sym,'entry_marker':entry,'double_reclaim':double,'reclaim_breakout':reclaim,'candle_pattern':patt,'entry_price':round(close,4),'stop':round(stop,4),'target0':round(target,4),'outcome':outcome,'days_to_exit':days,'rs_vs_spy_pct':round(rs*100,2),'pct_below_52w_high':round(float(below),2)})
    return rows


def main():
    OUTDIR.mkdir(exist_ok=True)
    syms=[x.strip().upper() for x in UNIVERSE.read_text().splitlines() if x.strip()]
    syms=list(dict.fromkeys(syms))
    data=download(syms+[BENCHMARK])
    spy=data.get(BENCHMARK)
    if spy is None or spy.empty: raise RuntimeError('SPY unavailable')
    rows=[]
    for n,s in enumerate(syms,1):
        if n%100==0: print('processed',n,'/',len(syms))
        d=data.get(s)
        if d is None or d.empty: continue
        try: rows.extend(evaluate_symbol(s,d,spy))
        except Exception as e: print('skip',s,e)
    out=pd.DataFrame(rows)
    out.to_csv(OUTDIR/'all_signals.csv',index=False)
    if out.empty:
        pd.DataFrame().to_csv(OUTDIR/'summary.csv',index=False); return
    summary=[]
    for name,mask in [('ENTRY',out.entry_marker),('DOUBLE_RECLAIM',out.double_reclaim),('RECLAIM_BREAKOUT',out.reclaim_breakout),('ENTRY+DOUBLE',out.entry_marker&out.double_reclaim)]:
        g=out[mask]
        resolved=g[g.outcome.isin(['TARGET0','STOP','STOP_AMBIGUOUS'])]
        wins=(resolved.outcome=='TARGET0').sum(); losses=len(resolved)-wins
        summary.append({'setup':name,'signals':len(g),'resolved':len(resolved),'wins':int(wins),'losses':int(losses),'win_rate_pct':round(100*wins/len(resolved),2) if len(resolved) else np.nan,'avg_days_to_exit':round(pd.to_numeric(resolved.days_to_exit,errors='coerce').mean(),2) if len(resolved) else np.nan,'median_days_to_exit':round(pd.to_numeric(resolved.days_to_exit,errors='coerce').median(),2) if len(resolved) else np.nan,'stops_within_5d_pct':round(100*((resolved.outcome!='TARGET0')&(pd.to_numeric(resolved.days_to_exit,errors='coerce')<=5)).sum()/losses,2) if losses else np.nan})
    pd.DataFrame(summary).to_csv(OUTDIR/'summary.csv',index=False)
    byc=[]
    for p,g in out.groupby('candle_pattern'):
        r=g[g.outcome.isin(['TARGET0','STOP','STOP_AMBIGUOUS'])]; w=(r.outcome=='TARGET0').sum()
        byc.append({'candle_pattern':p,'signals':len(g),'resolved':len(r),'wins':int(w),'win_rate_pct':round(100*w/len(r),2) if len(r) else np.nan})
    pd.DataFrame(byc).sort_values('signals',ascending=False).to_csv(OUTDIR/'summary_by_candle.csv',index=False)
    print(pd.DataFrame(summary).to_string(index=False))

if __name__=='__main__': main()
