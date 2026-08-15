"""Big Zone Scanner v1 — independent BO/EMA20/prior-high scanner."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
RESISTANCE_BARS=50; MIN_BREAKOUT_PCT=1.0; MAX_BO_AGE=30; EMA_LEN=20; VOL_LEN=20
def _series(x):
    if isinstance(x,pd.DataFrame): return x.iloc[:,0]
    return x
def download(ticker,period='2y'):
    try:
        d=yf.download(ticker,period=period,interval='1d',auto_adjust=True,progress=False,threads=False)
        if d is None or d.empty:return None
        if isinstance(d.columns,pd.MultiIndex):d.columns=d.columns.get_level_values(0)
        return d.dropna(subset=['Open','High','Low','Close','Volume'])
    except Exception:return None
def analyze(ticker,market):
    d=download(ticker)
    if d is None or len(d)<220:return None
    c,h,l,v=map(_series,[d.Close,d.High,d.Low,d.Volume]);ema20=c.ewm(span=EMA_LEN,adjust=False).mean();avgvol=v.rolling(VOL_LEN).mean();prior=h.shift(1).rolling(RESISTANCE_BARS).max();threshold=prior*(1+MIN_BREAKOUT_PCT/100);bo=(c>threshold)&(c.shift(1)<=prior);idx=np.flatnonzero(bo.fillna(False).to_numpy())
    if len(idx)==0:return None
    last=int(idx[-1]);age=len(d)-1-last
    if age<0 or age>MAX_BO_AGE:return None
    level=float(prior.iloc[last]);price=float(c.iloc[-1]);e20=float(ema20.iloc[-1]);low=float(l.iloc[-1]);vol=float(v.iloc[-1]);av=float(avgvol.iloc[-1]);ema_dist=min(abs(price/e20-1),abs(low/e20-1))*100 if e20>0 else 999;level_dist=min(abs(price/level-1),abs(low/level-1))*100 if level>0 else 999;bo_score=3 if age<=5 else 2 if age<=15 else 1;ema_score=3 if ema_dist<=2 else 2 if ema_dist<=5 else 1 if ema_dist<=8 else 0;level_score=3 if level_dist<=2 else 2 if level_dist<=5 else 1 if level_dist<=8 else 0;contraction=bool(pd.notna(av) and vol<av);score=bo_score+ema_score+level_score+(1 if contraction else 0);status='READY' if score>=8 and ema_score>=2 and level_score>=2 else 'WATCH' if score>=6 else 'EARLY'
    return {'Market':market,'Ticker':ticker,'Price':round(price,3),'Score':score,'Status':status,'BO_Date':str(d.index[last].date()),'BO_Age_Days':age,'Breakout_Level':round(level,3),'EMA20':round(e20,3),'Dist_EMA20_%':round(ema_dist,2),'Dist_Breakout_%':round(level_dist,2),'Volume_Contracting':contraction,'BO_Score':bo_score,'EMA20_Score':ema_score,'Level_Score':level_score}
def load_symbols(path,market):
    p=Path(path)
    if not p.exists():return []
    syms=[x.strip().upper() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#')]
    if market=='TSX':syms=[s for s in syms if s.endswith('.TO') and not s.endswith('.V')]
    return list(dict.fromkeys(syms))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--us-file',default='data/us_universe.txt');ap.add_argument('--tsx-file',default='data/canada_universe.txt');ap.add_argument('--hk-file',default='data/hk_universe.txt');ap.add_argument('--outdir',default='big_zone_results');a=ap.parse_args();out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True);rows=[]
    for market,path in [('US',a.us_file),('TSX',a.tsx_file),('HK',a.hk_file)]:
        for s in load_symbols(path,market):
            r=analyze(s,market)
            if r:rows.append(r)
    df=pd.DataFrame(rows)
    if df.empty:df.to_csv(out/'big_zone_all.csv',index=False);return
    df=df.sort_values(['Score','BO_Age_Days'],ascending=[False,True]);df.to_csv(out/'big_zone_all.csv',index=False);df[df.Status=='READY'].to_csv(out/'big_zone_ready.csv',index=False);df[df.Status=='WATCH'].to_csv(out/'big_zone_watch.csv',index=False)
    for market in ['US','TSX','HK']:
        m=df[(df.Market==market)&(df.Status.isin(['READY','WATCH']))];(out/f'big_zone_{market.lower()}_watchlist.txt').write_text('\n'.join(m.Ticker.astype(str))+'\n')
    print(df.head(50).to_string(index=False))
if __name__=='__main__':main()
