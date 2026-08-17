from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import time
import numpy as np
import pandas as pd
import yfinance as yf

from build_universes import build_tsx

CA_TZ = ZoneInfo('America/Toronto')
BENCHMARK = 'XIU.TO'
OUTDIR = Path('double_reclaim_results/canada')

BREAKOUT_LOOKBACK = 50
BREAKOUT_MIN_PCT = 1.0
MAX_BREAKOUT_AGE = 30
TOUCH_TOL_PCT = 0.25
MAX_UNDERCUT_PCT = 3.0
RS_LOOKBACK = 63
MIN_MARKET_CAP = 1_000_000_000  # CAD 1B


def _is_common_tsx_symbol(symbol: str) -> bool:
    """Drop obvious preferred-share series that create many invalid Yahoo requests."""
    s = symbol.upper()
    return '-PR-' not in s and '-PF-' not in s


def _split_download(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(map(str, raw.columns.get_level_values(0)))
        fields = {'Open','High','Low','Close','Adj Close','Volume'}
        if len(fields & level0) >= 3:
            for s in symbols:
                try:
                    x = raw.xs(s, axis=1, level=1, drop_level=True).dropna(how='all')
                    if not x.empty:
                        out[s] = x
                except Exception:
                    pass
        else:
            for s in symbols:
                try:
                    x = raw.xs(s, axis=1, level=0, drop_level=True).dropna(how='all')
                    if not x.empty:
                        out[s] = x
                except Exception:
                    pass
    elif len(symbols) == 1:
        out[symbols[0]] = raw.dropna(how='all')
    return out


def _download_single_daily(symbol: str, attempts: int = 4) -> pd.DataFrame:
    """Fetch the benchmark separately so a late universe rate limit cannot kill RS."""
    for attempt in range(1, attempts + 1):
        try:
            raw = yf.download(symbol, period='18mo', interval='1d', auto_adjust=True,
                              progress=False, threads=False)
            if raw is not None and not raw.empty:
                if isinstance(raw.columns, pd.MultiIndex):
                    try:
                        raw = raw.xs(symbol, axis=1, level=1, drop_level=True)
                    except Exception:
                        try:
                            raw.columns = raw.columns.get_level_values(0)
                        except Exception:
                            pass
                if 'Close' in raw.columns:
                    return raw.dropna(how='all')
        except Exception as exc:
            print(f'benchmark fetch attempt {attempt}/{attempts} failed:', exc)
        if attempt < attempts:
            wait = 3 * attempt
            print(f'Waiting {wait}s before benchmark retry...')
            time.sleep(wait)
    return pd.DataFrame()


def _batch_daily(symbols: list[str], chunk: int = 100) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i+chunk]
        print(f'Daily batch {i+1}-{min(i+chunk,len(symbols))}/{len(symbols)}')
        for attempt in range(1, 3):
            try:
                raw = yf.download(group, period='18mo', interval='1d', auto_adjust=True,
                                  progress=False, threads=True, group_by='ticker')
                got = _split_download(raw, group)
                out.update(got)
                if got:
                    break
            except Exception as exc:
                print(f'daily batch attempt {attempt} failed', exc)
            if attempt == 1:
                time.sleep(3)
        # Gentle pacing materially reduces Yahoo 429/rate-limit failures.
        time.sleep(1.2)
    return out


def _batch_intraday(symbols: list[str], chunk: int = 60) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i+chunk]
        print(f'5m batch {i+1}-{min(i+chunk,len(symbols))}/{len(symbols)}')
        try:
            raw = yf.download(group, period='1d', interval='5m', auto_adjust=True,
                              prepost=False, progress=False, threads=True, group_by='ticker')
            out.update(_split_download(raw, group))
        except Exception as exc:
            print('5m batch failed', exc)
        time.sleep(1.0)
    return out


def _market_cap(symbol: str) -> float:
    for attempt in range(1, 3):
        try:
            v = yf.Ticker(symbol).fast_info.market_cap
            return float(v) if v is not None else np.nan
        except Exception as exc:
            print('market cap failed', symbol, exc)
            if attempt == 1:
                time.sleep(1.5)
    return np.nan


def _completed_daily(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    x = df.copy().dropna(subset=['Close'])
    if x.empty:
        return x
    idx = pd.DatetimeIndex(x.index)
    today = datetime.now(CA_TZ).date()
    if len(x) and idx.date[-1] == today:
        x = x.iloc[:-1]
    return x


def _recent_breakout(df: pd.DataFrame):
    if len(df) < BREAKOUT_LOOKBACK + 35:
        return None
    h = pd.to_numeric(df['High'], errors='coerce')
    c = pd.to_numeric(df['Close'], errors='coerce')
    resistance = h.shift(1).rolling(BREAKOUT_LOOKBACK).max()
    breakout = (c > resistance * (1 + BREAKOUT_MIN_PCT/100.0)) & (c.shift(1) <= resistance)
    hits = np.flatnonzero(breakout.fillna(False).to_numpy())
    if len(hits) == 0:
        return None
    pos = int(hits[-1]); age = len(df)-1-pos
    if age < 1 or age > MAX_BREAKOUT_AGE:
        return None
    return pos, float(resistance.iloc[pos]), age


def _congestion_score(df: pd.DataFrame, breakout_pos: int, breakout_level: float) -> tuple[int,str]:
    score = 0
    pre = df.iloc[max(0, breakout_pos-20):breakout_pos]
    pre10 = df.iloc[max(0, breakout_pos-10):breakout_pos]
    post = df.iloc[breakout_pos+1:]
    pre_flag = post_flag = False
    if len(pre) >= 15:
        lo20=float(pre['Low'].min()); hi20=float(pre['High'].max())
        r20=(hi20/lo20-1)*100 if lo20>0 else 999
        if r20<=12: score+=1; pre_flag=True
        if len(pre10)>=7:
            lo10=float(pre10['Low'].min()); hi10=float(pre10['High'].max())
            r10=(hi10/lo10-1)*100 if lo10>0 else 999
            if r20>0 and r10<=r20*.75: score+=1; pre_flag=True
    if len(post)>=5:
        plo=float(post['Low'].min()); phi=float(post['High'].max())
        pr=(phi/plo-1)*100 if plo>0 else 999
        closes=pd.to_numeric(post['Close'], errors='coerce')
        near=((closes>=breakout_level*.94)&(closes<=breakout_level*1.06)).mean()
        if pr<=10 and near>=.60: score+=1; post_flag=True
    v=pd.to_numeric(df['Volume'], errors='coerce')
    if len(v)>=20 and v.tail(10).mean()<=.85*v.tail(20).mean(): score+=1; post_flag=True
    if pre_flag and post_flag: status='BOTH'
    elif pre_flag: status='PRE_BREAKOUT'
    elif post_flag: status='FORMING_NOW'
    else: status='NONE'
    return score,status


def _grade(rs: float, cluster: float) -> str:
    if rs>=15 and cluster<=.5: return 'A'
    if rs>=10 and cluster<=1.0: return 'B'
    if rs>=10 and cluster<=2.0: return 'C'
    return 'D'


def _dynamic_ema20(completed_closes: pd.Series, current: float) -> float:
    s=pd.concat([pd.to_numeric(completed_closes,errors='coerce').dropna(),pd.Series([current])],ignore_index=True)
    return float(s.ewm(span=20,adjust=False).mean().iloc[-1])


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw_symbols=build_tsx()
    symbols=[s for s in raw_symbols if _is_common_tsx_symbol(s)]
    symbols=list(dict.fromkeys(symbols))
    print('TSX universe',len(raw_symbols),'| common/non-preferred candidates',len(symbols),
          '| minimum market cap CAD',f'{MIN_MARKET_CAP:,}')

    # Protect the benchmark from being lost if Yahoo rate-limits a later bulk batch.
    benchmark_raw = _download_single_daily(BENCHMARK)
    bench = _completed_daily(benchmark_raw)
    if bench.empty or len(bench)<RS_LOOKBACK+2:
        raise RuntimeError('benchmark XIU.TO unavailable after retries; aborting safely')
    bench_ret=float(bench['Close'].iloc[-1]/bench['Close'].iloc[-1-RS_LOOKBACK]-1)

    daily=_batch_daily(symbols)
    print('Daily data successfully loaded for',len(daily),'of',len(symbols),'symbols')

    prelim=[]
    for sym in symbols:
        d0=daily.get(sym)
        if d0 is None or d0.empty: continue
        d=_completed_daily(d0)
        if len(d)<260: continue
        bo=_recent_breakout(d)
        if bo is None: continue
        bpos,level,age=bo
        close=float(d['Close'].iloc[-1])
        ema20_prev=float(pd.to_numeric(d['Close'],errors='coerce').ewm(span=20,adjust=False).mean().iloc[-1])
        cluster_prev=abs(ema20_prev/level-1)*100 if level>0 else 999
        if cluster_prev>3: continue
        stock_ret=float(close/float(d['Close'].iloc[-1-RS_LOOKBACK])-1)
        rs=(stock_ret-bench_ret)*100
        if rs<0: continue
        cong,cong_status=_congestion_score(d,bpos,level)
        prelim.append({'symbol':sym,'breakout_level':level,'breakout_age':age,'rs_prev_pct':rs,
                       'congestion_score':cong,'congestion_status':cong_status,'_daily':d})

    print('Preliminary technical shortlist',len(prelim))
    shortlist=[]
    for i,x in enumerate(prelim,1):
        cap=_market_cap(x['symbol'])
        if pd.isna(cap) or cap<MIN_MARKET_CAP: continue
        x['market_cap']=cap; shortlist.append(x)
        if i%20==0:
            print('Market-cap checked',i,'/',len(prelim),'| kept',len(shortlist))
        time.sleep(0.25)
    print('Shortlist after CAD 1B market-cap filter',len(shortlist))

    intra=_batch_intraday([x['symbol'] for x in shortlist])
    rows=[]
    for x in shortlist:
        sym=x['symbol']; intr=intra.get(sym)
        if intr is None or intr.empty: continue
        if 'Close' not in intr.columns or 'Low' not in intr.columns: continue
        intr=intr.dropna(subset=['Close','Low'])
        if intr.empty: continue
        current=float(intr['Close'].iloc[-1]); day_low=float(intr['Low'].min())
        d=x['_daily']; level=float(x['breakout_level'])
        ema20=_dynamic_ema20(d['Close'],current)
        cluster=abs(ema20/level-1)*100 if level>0 else np.nan
        if cluster>3: continue
        stock_ret=current/float(d['Close'].iloc[-RS_LOOKBACK])-1
        rs=(stock_ret-bench_ret)*100
        high52=float(pd.to_numeric(d['High'],errors='coerce').tail(252).max())
        pct_below=(1-current/high52)*100 if high52>0 else np.nan
        touched_bo=day_low<=level*(1+TOUCH_TOL_PCT/100)
        touched_ema=day_low<=ema20*(1+TOUCH_TOL_PCT/100)
        not_deep=day_low>=level*(1-MAX_UNDERCUT_PCT/100)
        above=current>level and current>ema20
        double=touched_bo and touched_ema and not_deep and above
        touched_both=touched_bo and touched_ema and not_deep
        grade=_grade(rs,cluster)
        undercut=(day_low/level-1)*100
        depth=max(0.0,-undercut)
        shallow=2 if depth<=.5 else (1 if depth<=1.0 else 0)
        headroom=1 if 2<=pct_below<=8 else 0
        final='A+' if grade=='A' and depth<=1.0 and 2<=pct_below<=8 else grade
        status='READY_NOW' if double else ('RECLAIM_PENDING' if touched_both else 'WATCH_CLUSTER')
        quality={'A+':8,'A':6,'B':4,'C':2,'D':0}[final]+int(x['congestion_score'])+shallow+headroom
        rows.append({'symbol':sym,'status':status,'grade':final,'quality_score':quality,
                     'market_cap_cad':round(float(x['market_cap']),0),'market_cap_cad_bn':round(float(x['market_cap'])/1e9,2),
                     'current_price':round(current,3),'day_low':round(day_low,3),'breakout_level':round(level,3),'ema20_live':round(ema20,3),
                     'ema20_breakout_distance_pct':round(cluster,3),'rs_vs_xiu_pct':round(rs,2),'pct_below_52w_high':round(pct_below,2),
                     'breakout_age_days':x['breakout_age'],'undercut_vs_breakout_pct':round(undercut,2),
                     'shallow_bonus':shallow,'headroom_bonus':headroom,'congestion_score':x['congestion_score'],
                     'congestion_status':x['congestion_status'],'touched_breakout_today':touched_bo,'touched_ema20_today':touched_ema,
                     'above_both_now':above})

    out=pd.DataFrame(rows)
    if out.empty:
        out.to_csv(OUTDIR/'canada_double_reclaim_all.csv',index=False)
        out.to_csv(OUTDIR/'canada_double_reclaim_top30.csv',index=False)
        out.to_csv(OUTDIR/'canada_double_reclaim_ready_now.csv',index=False)
        print('No candidates'); return
    status_order={'READY_NOW':0,'RECLAIM_PENDING':1,'WATCH_CLUSTER':2}
    grade_order={'A+':0,'A':1,'B':2,'C':3,'D':4}
    out['_s']=out['status'].map(status_order).fillna(9); out['_g']=out['grade'].map(grade_order).fillna(9)
    out=out.sort_values(['_s','_g','quality_score','rs_vs_xiu_pct'],ascending=[True,True,False,False]).drop(columns=['_s','_g'])
    out.to_csv(OUTDIR/'canada_double_reclaim_all.csv',index=False)
    out.head(30).to_csv(OUTDIR/'canada_double_reclaim_top30.csv',index=False)
    ready=out[out['status']=='READY_NOW']; ready.to_csv(OUTDIR/'canada_double_reclaim_ready_now.csv',index=False)
    print('\n=== TOP 30 (CAD 1B+) ===')
    cols=['symbol','status','grade','quality_score','market_cap_cad_bn','current_price','breakout_level','ema20_live','ema20_breakout_distance_pct','rs_vs_xiu_pct','pct_below_52w_high','congestion_score']
    print(out[cols].head(30).to_string(index=False))
    print('\nREADY_NOW',len(ready),'TOTAL WATCH',len(out))


if __name__=='__main__':
    main()
