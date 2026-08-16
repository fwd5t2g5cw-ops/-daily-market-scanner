from __future__ import annotations

import argparse, random, subprocess, sys, time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from historical_reclaim_test import congestion_metrics

MARKETS = {
    'us': {
        'label': 'US', 'universe': 'data/us_1b_universe.txt', 'benchmark': 'SPY',
        'min_price': 10.0, 'min_avg_volume': 500_000, 'min_dollar_vol': 20_000_000,
        'batch': 40,
    },
    'tsx': {
        'label': 'TSX', 'universe': 'data/tsx_universe.txt', 'benchmark': 'XIU.TO',
        'min_price': 5.0, 'min_avg_volume': 200_000, 'min_dollar_vol': 5_000_000,
        'batch': 35,
    },
    'hk': {
        'label': 'HK', 'universe': 'data/hk_universe.txt', 'benchmark': '2800.HK',
        'min_price': 1.0, 'min_avg_volume': 500_000, 'min_dollar_vol': 5_000_000,
        'batch': 30,
    },
}


def s(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0: return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors='coerce').astype(float)


def flatten(d):
    if d is None or d.empty: return d
    d = d.copy()
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    return d


def frame(data, symbol, single=False):
    try: d = data.copy() if single else data[symbol].copy()
    except Exception: return None
    d = flatten(d)
    need = ['Open','High','Low','Close','Volume']
    if d is None or any(c not in d.columns for c in need): return None
    d = d.dropna(subset=need)
    return d if len(d) >= 220 else None


def dl_single(sym, start, end, attempts=4):
    for a in range(attempts):
        try:
            d = yf.download(sym, start=start, end=end, interval='1d', auto_adjust=True,
                            threads=False, progress=False)
            if d is not None and not d.empty: return flatten(d)
        except Exception as e:
            print('single fail', sym, a+1, e)
        if a + 1 < attempts: time.sleep(4 * (2 ** a) + random.uniform(.5, 1.5))
    return None


def dl_batch(batch, start, end, attempts=3):
    for a in range(attempts):
        try:
            d = yf.download(batch, start=start, end=end, interval='1d', group_by='ticker',
                            auto_adjust=True, threads=True, progress=False)
            if d is not None and not d.empty: return d
        except Exception as e:
            print('batch fail', a+1, e)
        if a + 1 < attempts: time.sleep(6 * (2 ** a) + random.uniform(1, 2))
    return None


def ensure_universes():
    subprocess.run([sys.executable, 'build_universes.py', '--markets', 'tsx,hk'], check=True)


def load_symbols(cfg):
    p = Path(cfg['universe'])
    if not p.exists(): raise FileNotFoundError(str(p))
    return list(dict.fromkeys(x.strip().upper() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#')))


def ma_score(distance_pct):
    if pd.isna(distance_pct) or distance_pct < -3: return 0
    d = abs(float(distance_pct))
    if d <= 2: return 2
    if d <= 5: return 1
    return 0


def analyze(d, bench, as_of, cfg):
    cutoff = pd.Timestamp(as_of)
    x = d.loc[pd.to_datetime(d.index).normalize() <= cutoff].copy()
    bx = bench.loc[pd.to_datetime(bench.index).normalize() <= cutoff].copy()
    if len(x) < 220 or len(bx) < 70: return None

    c,h,l,v,o = map(s, [x.Close,x.High,x.Low,x.Volume,x.Open])
    bc = s(bx.Close)
    ema20 = c.ewm(span=20, adjust=False).mean(); ema50 = c.ewm(span=50, adjust=False).mean(); sma200 = c.rolling(200).mean()
    av20 = v.rolling(20).mean(); adv20 = (c*v).rolling(20).mean(); hi52s = h.rolling(252,min_periods=20).max()
    be20 = bc.ewm(span=20,adjust=False).mean(); be50 = bc.ewm(span=50,adjust=False).mean()
    vals = [ema20.iloc[-1],ema50.iloc[-1],sma200.iloc[-1],av20.iloc[-1],adv20.iloc[-1],hi52s.iloc[-1],be20.iloc[-1],be50.iloc[-1]]
    if any(pd.isna(z) for z in vals) or len(c)<=63 or len(bc)<=63: return None

    close=float(c.iloc[-1]); high=float(h.iloc[-1]); low=float(l.iloc[-1]); open_=float(o.iloc[-1])
    e20=float(ema20.iloc[-1]); e50=float(ema50.iloc[-1]); s200=float(sma200.iloc[-1]); av=float(av20.iloc[-1]); adv=float(adv20.iloc[-1]); hi52=float(hi52s.iloc[-1])

    strong = close>e20>e50>s200 and e50>float(ema50.iloc[-11]) and s200>float(sma200.iloc[-21])
    pct_e20=(close/e20-1)*100; pct_e50=(close/e50-1)*100; pct_s200=(close/s200-1)*100
    not_extended = pct_e20 <= 12
    liquid = close>=cfg['min_price'] and av>=cfg['min_avg_volume'] and adv>=cfg['min_dollar_vol']
    pct_high=(hi52-close)/hi52*100 if hi52>0 else np.nan; near_high = pd.notna(pct_high) and pct_high<=20
    sr=close/float(c.iloc[-64])-1; br=float(bc.iloc[-1])/float(bc.iloc[-64])-1; rs=sr-br; outperform=rs>0
    market_pass=float(bc.iloc[-1])>float(be20.iloc[-1])>float(be50.iloc[-1])

    prior=h.shift(1).rolling(50).max(); breakout=(c>prior*1.01)&(c.shift(1)<=prior)
    idx=np.flatnonzero(breakout.fillna(False).to_numpy()); today=len(c)-1
    eligible=[i for i in idx if i<today]
    if not eligible: return None
    bi=int(eligible[-1]); level=float(prior.iloc[bi]); age=today-bi
    if not (1<=age<=30) or not np.isfinite(level) or level<=0: return None

    slight=low<level and low>=level*.97; reclaimed=close>level
    bullish=close>open_ and close>=(high+low)/2
    rng=high-low; bear=rng>0 and close<open_ and (open_-close)/rng>=.65
    trigger=slight and reclaimed and bullish and not bear
    entry=strong and not_extended and liquid and near_high and outperform and market_pass and trigger
    if not entry: return None

    cong=congestion_metrics(c,h,l,v,bi,today,level)
    s20=ma_score(pct_e20); s50=ma_score(pct_e50); s200sc=ma_score(pct_s200)
    near_count=sum(abs(z)<=5 for z in [pct_e20,pct_e50,pct_s200] if pd.notna(z))
    cluster=1 if near_count>=2 else 0
    ma_support=s20+s50+s200sc+cluster
    total=int(cong['congestion_score'])+ma_support

    out={
        'date':as_of,'market':cfg['label'],'symbol':'','close':round(close,2),
        'total_setup_score':total,'congestion_score':int(cong['congestion_score']),
        'congestion_status':cong['congestion_status'],'ma_support_score':ma_support,
        'ema20_distance_pct':round(pct_e20,2),'ema50_distance_pct':round(pct_e50,2),'sma200_distance_pct':round(pct_s200,2),
        'support_cluster':cluster,'rs_vs_benchmark_pct':round(rs*100,2),'pct_below_52w_high':round(pct_high,2),
        'breakout_level':round(level,2),'breakout_date':str(pd.Timestamp(x.index[bi]).date()),'bars_since_breakout':age,
        'intraday_undercut_pct':round((low/level-1)*100,2),'close_above_level_pct':round((close/level-1)*100,2),
        'avg_volume_20d':int(av),'avg_dollar_volume_m':round(adv/1_000_000,2),
    }
    return out


def run_market(key, start_date, end_date, outdir):
    cfg=MARKETS[key]; syms=load_symbols(cfg)
    print(f"=== {cfg['label']} universe {len(syms)} ===")
    hist_start=(datetime.strptime(start_date,'%Y-%m-%d').date()-timedelta(days=700)).isoformat()
    hist_end=(datetime.strptime(end_date,'%Y-%m-%d').date()+timedelta(days=1)).isoformat()
    bench=dl_single(cfg['benchmark'],hist_start,hist_end,attempts=5)
    if bench is None: raise RuntimeError('benchmark failed '+cfg['benchmark'])
    bdates=pd.to_datetime(bench.index).normalize()
    dates=[str(x.date()) for x in bdates if pd.Timestamp(start_date)<=x<=pd.Timestamp(end_date)]
    print('trading dates', dates)

    rows=[]; failed=[]
    for st in range(0,len(syms),cfg['batch']):
        batch=syms[st:st+cfg['batch']]
        print(cfg['label'], st+1, min(st+len(batch),len(syms)), 'of', len(syms))
        data=dl_batch(batch,hist_start,hist_end)
        if data is None: failed.extend(batch); continue
        single=len(batch)==1
        for sym in batch:
            d=frame(data,sym,single)
            if d is None: failed.append(sym); continue
            for dt in dates:
                try:
                    r=analyze(d,bench,dt,cfg)
                    if r: r['symbol']=sym; rows.append(r)
                except Exception as e: print('skip',cfg['label'],sym,dt,e)
        time.sleep(random.uniform(1.0,1.8))

    # controlled recovery only for symbols that were absent/incomplete
    failed=list(dict.fromkeys(failed)); still=[]
    if failed:
        print(cfg['label'],'recovery',len(failed)); time.sleep(12)
        for i,sym in enumerate(failed,1):
            d=dl_single(sym,hist_start,hist_end,attempts=3)
            if d is None or len(d)<220: still.append(sym)
            else:
                for dt in dates:
                    try:
                        r=analyze(d,bench,dt,cfg)
                        if r: r['symbol']=sym; rows.append(r)
                    except Exception as e: print('recovery skip',sym,dt,e)
            time.sleep(random.uniform(.7,1.2))
            if i%50==0: time.sleep(10)

    df=pd.DataFrame(rows)
    if not df.empty:
        df=df.drop_duplicates(['date','market','symbol'])
        df=df.sort_values(['date','total_setup_score','congestion_score','ma_support_score','rs_vs_benchmark_pct','pct_below_52w_high'],ascending=[True,False,False,False,False,True])
        df['rank']=df.groupby('date').cumcount()+1
        top=df[df['rank']<=30].copy()
    else: top=df.copy()
    Path(outdir).mkdir(parents=True,exist_ok=True)
    df.to_csv(Path(outdir)/f'{key}_all_candidates.csv',index=False)
    top.to_csv(Path(outdir)/f'{key}_daily_top30.csv',index=False)
    pd.DataFrame({'symbol':still}).to_csv(Path(outdir)/f'{key}_failed_symbols.csv',index=False)
    return df,top,dates,len(syms),len(still)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--start',default='2026-08-03'); ap.add_argument('--end',default='2026-08-14')
    ap.add_argument('--markets',default='us,tsx,hk'); ap.add_argument('--outdir',default='historical_3market_results')
    a=ap.parse_args(); ensure_universes()
    all_top=[]; summary=[]
    for key in [x.strip() for x in a.markets.split(',') if x.strip()]:
        df,top,dates,n,failed=run_market(key,a.start,a.end,a.outdir)
        all_top.append(top)
        for dt in dates:
            cnt=0 if df.empty else int((df.date==dt).sum())
            summary.append({'market':MARKETS[key]['label'],'date':dt,'entry_candidates':cnt,'top30_rows':min(cnt,30),'universe_size':n,'still_failed_symbols':failed})
    combined=pd.concat(all_top,ignore_index=True) if all_top else pd.DataFrame()
    combined.to_csv(Path(a.outdir)/'daily_top30_all_markets.csv',index=False)
    pd.DataFrame(summary).to_csv(Path(a.outdir)/'daily_summary.csv',index=False)
    print(pd.DataFrame(summary).to_string(index=False))

if __name__=='__main__': main()
