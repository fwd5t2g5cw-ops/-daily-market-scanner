from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import time

import numpy as np
import pandas as pd
import yfinance as yf
from yfinance import EquityQuery

JP_TZ = ZoneInfo('Asia/Tokyo')
BENCHMARK = '1306.T'  # TOPIX ETF
OUTDIR = Path('double_reclaim_results/japan')

MIN_MARKET_CAP_USD = 1_000_000_000
PAGE_SIZE = 250
BREAKOUT_LOOKBACK = 50
BREAKOUT_MIN_PCT = 1.0
MAX_BREAKOUT_AGE = 30
TOUCH_TOL_PCT = 0.25
MAX_UNDERCUT_PCT = 3.0
RS_LOOKBACK = 63


def _usd_jpy() -> float:
    raw = yf.download('JPY=X', period='5d', interval='1d', auto_adjust=True,
                      progress=False, threads=False)
    if raw is None or raw.empty:
        raise RuntimeError('USD/JPY data unavailable')
    close = raw['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    rate = float(pd.to_numeric(close, errors='coerce').dropna().iloc[-1])
    if not np.isfinite(rate) or rate <= 0:
        raise RuntimeError('Invalid USD/JPY rate')
    return rate


def _load_universe() -> tuple[list[str], dict[str, float], float]:
    fx = _usd_jpy()
    min_cap_jpy = MIN_MARKET_CAP_USD * fx
    print(f'USDJPY={fx:.4f}; Japan market-cap floor = JPY {min_cap_jpy:,.0f} (USD 1B)')

    query = EquityQuery('and', [
        EquityQuery('eq', ['region', 'jp']),
        EquityQuery('gte', ['intradaymarketcap', min_cap_jpy]),
    ])
    rows = []
    offset = 0
    while True:
        response = None
        last_error = None
        for attempt in range(4):
            try:
                response = yf.screen(query, offset=offset, size=PAGE_SIZE,
                                     sortField='ticker', sortAsc=True)
                break
            except Exception as exc:
                last_error = exc
                delay = 3 * (2 ** attempt)
                print(f'Japan screener offset={offset} failed ({exc}); retry in {delay}s')
                time.sleep(delay)
        if response is None:
            raise RuntimeError(f'Japan Yahoo screener failed: {last_error}')
        quotes = response.get('quotes') or []
        if not quotes:
            break
        for q in quotes:
            sym = str(q.get('symbol') or '').strip().upper()
            if not sym.endswith('.T'):
                continue
            cap = q.get('marketCap')
            if cap is None:
                cap = q.get('intradaymarketcap')
            try:
                cap = float(cap)
            except Exception:
                continue
            if cap < min_cap_jpy:
                continue
            rows.append((sym, cap))
        print(f'Japan screen offset {offset}: {len(quotes)} quotes, kept {len(rows)}')
        offset += len(quotes)
        if len(quotes) < PAGE_SIZE:
            break
        time.sleep(0.5)

    if not rows:
        raise RuntimeError('No Japan equities passed USD 1B market-cap filter')
    cap_map = dict(rows)
    symbols = list(dict.fromkeys(s for s, _ in rows))
    print('Japan USD 1B+ universe', len(symbols))
    return symbols, cap_map, fx


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


def _batch(symbols: list[str], period: str, interval: str, chunk: int) -> dict[str, pd.DataFrame]:
    out = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i+chunk]
        print(f'{interval} batch {i+1}-{min(i+chunk, len(symbols))}/{len(symbols)}')
        try:
            raw = yf.download(group, period=period, interval=interval, auto_adjust=True,
                              prepost=False, progress=False, threads=True, group_by='ticker')
            out.update(_split_download(raw, group))
        except Exception as exc:
            print(interval, 'batch failed:', exc)
        time.sleep(0.4)
    return out


def _completed_daily(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    x = df.copy().dropna(subset=['Close'])
    today = datetime.now(JP_TZ).date()
    if len(x) and pd.DatetimeIndex(x.index).date[-1] == today:
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
    pos = int(hits[-1])
    age = len(df) - 1 - pos
    if age < 1 or age > MAX_BREAKOUT_AGE:
        return None
    return pos, float(resistance.iloc[pos]), age


def _congestion_score(df: pd.DataFrame, breakout_pos: int, breakout_level: float):
    score = 0
    pre = df.iloc[max(0, breakout_pos-20):breakout_pos]
    pre10 = df.iloc[max(0, breakout_pos-10):breakout_pos]
    post = df.iloc[breakout_pos+1:]
    pre_flag = post_flag = False
    if len(pre) >= 15:
        lo20, hi20 = float(pre['Low'].min()), float(pre['High'].max())
        r20 = (hi20/lo20-1)*100 if lo20 > 0 else 999
        if r20 <= 12:
            score += 1; pre_flag = True
        if len(pre10) >= 7:
            lo10, hi10 = float(pre10['Low'].min()), float(pre10['High'].max())
            r10 = (hi10/lo10-1)*100 if lo10 > 0 else 999
            if r20 > 0 and r10 <= r20*.75:
                score += 1; pre_flag = True
    if len(post) >= 5:
        plo, phi = float(post['Low'].min()), float(post['High'].max())
        pr = (phi/plo-1)*100 if plo > 0 else 999
        closes = pd.to_numeric(post['Close'], errors='coerce')
        near = ((closes >= breakout_level*.94) & (closes <= breakout_level*1.06)).mean()
        if pr <= 10 and near >= .60:
            score += 1; post_flag = True
    v = pd.to_numeric(df['Volume'], errors='coerce')
    if len(v) >= 20 and v.tail(10).mean() <= .85*v.tail(20).mean():
        score += 1; post_flag = True
    status = 'BOTH' if pre_flag and post_flag else ('PRE_BREAKOUT' if pre_flag else ('FORMING_NOW' if post_flag else 'NONE'))
    return score, status


def _grade(rs: float, cluster: float) -> str:
    if rs >= 15 and cluster <= .5: return 'A'
    if rs >= 10 and cluster <= 1.0: return 'B'
    if rs >= 10 and cluster <= 2.0: return 'C'
    return 'D'


def _dynamic_ema20(completed_closes: pd.Series, current: float) -> float:
    s = pd.concat([pd.to_numeric(completed_closes, errors='coerce').dropna(), pd.Series([current])], ignore_index=True)
    return float(s.ewm(span=20, adjust=False).mean().iloc[-1])


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    symbols, cap_map, fx = _load_universe()
    daily = _batch(symbols + ([BENCHMARK] if BENCHMARK not in symbols else []), '18mo', '1d', 180)
    bench = _completed_daily(daily.get(BENCHMARK, pd.DataFrame()))
    if bench.empty or len(bench) < RS_LOOKBACK + 2:
        raise RuntimeError('TOPIX benchmark data unavailable')
    bench_ret = float(bench['Close'].iloc[-1] / bench['Close'].iloc[-1-RS_LOOKBACK] - 1)

    shortlist = []
    for sym in symbols:
        d = _completed_daily(daily.get(sym, pd.DataFrame()))
        if len(d) < 260: continue
        bo = _recent_breakout(d)
        if bo is None: continue
        bpos, level, age = bo
        close = float(d['Close'].iloc[-1])
        ema20_prev = float(pd.to_numeric(d['Close'], errors='coerce').ewm(span=20, adjust=False).mean().iloc[-1])
        cluster_prev = abs(ema20_prev/level - 1)*100 if level > 0 else 999
        if cluster_prev > 3.0: continue
        stock_ret = float(close / float(d['Close'].iloc[-1-RS_LOOKBACK]) - 1)
        rs = (stock_ret - bench_ret)*100
        if rs < 0: continue
        cong, cong_status = _congestion_score(d, bpos, level)
        shortlist.append({'symbol':sym,'breakout_level':level,'breakout_age':age,
                          'rs_prev_pct':rs,'congestion_score':cong,'congestion_status':cong_status,
                          'market_cap_jpy':cap_map.get(sym,np.nan),'_daily':d})

    print('Technical shortlist', len(shortlist))
    intra = _batch([x['symbol'] for x in shortlist], '1d', '5m', 80)
    rows = []
    for x in shortlist:
        sym = x['symbol']; intr = intra.get(sym)
        if intr is None or intr.empty: continue
        intr = intr.dropna(subset=['Close','Low'])
        if intr.empty: continue
        current = float(intr['Close'].iloc[-1]); day_low = float(intr['Low'].min())
        d = x['_daily']; level = float(x['breakout_level'])
        ema20 = _dynamic_ema20(d['Close'], current)
        cluster = abs(ema20/level-1)*100 if level > 0 else np.nan
        if cluster > 3: continue
        stock_ret = current/float(d['Close'].iloc[-RS_LOOKBACK])-1
        rs = (stock_ret-bench_ret)*100
        high52 = float(pd.to_numeric(d['High'], errors='coerce').tail(252).max())
        pct_below = (1-current/high52)*100 if high52 > 0 else np.nan
        touched_bo = day_low <= level*(1+TOUCH_TOL_PCT/100)
        touched_ema = day_low <= ema20*(1+TOUCH_TOL_PCT/100)
        not_deep = day_low >= level*(1-MAX_UNDERCUT_PCT/100)
        above = current > level and current > ema20
        double = touched_bo and touched_ema and not_deep and above
        touched_both = touched_bo and touched_ema and not_deep
        grade = _grade(rs,cluster)
        undercut = (day_low/level-1)*100
        depth = max(0.0,-undercut)
        shallow = 2 if depth <= .5 else (1 if depth <= 1.0 else 0)
        headroom = 1 if 2 <= pct_below <= 8 else 0
        final = 'A+' if grade == 'A' and depth <= 1.0 and 2 <= pct_below <= 8 else grade
        status = 'READY_NOW' if double else ('RECLAIM_PENDING' if touched_both else 'WATCH_CLUSTER')
        quality = {'A+':8,'A':6,'B':4,'C':2,'D':0}[final] + int(x['congestion_score']) + shallow + headroom
        cap_jpy = float(x['market_cap_jpy']) if pd.notna(x['market_cap_jpy']) else np.nan
        rows.append({
            'symbol':sym,'status':status,'grade':final,'quality_score':quality,
            'market_cap_jpy_bn':round(cap_jpy/1e9,2) if np.isfinite(cap_jpy) else np.nan,
            'market_cap_usd_bn':round(cap_jpy/fx/1e9,2) if np.isfinite(cap_jpy) else np.nan,
            'current_price_jpy':round(current,2),'day_low_jpy':round(day_low,2),
            'breakout_level_jpy':round(level,2),'ema20_live_jpy':round(ema20,2),
            'ema20_breakout_distance_pct':round(cluster,3),'rs_vs_topix_pct':round(rs,2),
            'pct_below_52w_high':round(pct_below,2),'breakout_age_days':x['breakout_age'],
            'undercut_vs_breakout_pct':round(undercut,2),'congestion_score':x['congestion_score'],
            'congestion_status':x['congestion_status'],'touched_breakout_today':touched_bo,
            'touched_ema20_today':touched_ema,'above_both_now':above,
        })

    out = pd.DataFrame(rows)
    all_path = OUTDIR/'japan_double_reclaim_all.csv'
    top_path = OUTDIR/'japan_double_reclaim_top30.csv'
    ready_path = OUTDIR/'japan_double_reclaim_ready_now.csv'
    if out.empty:
        out.to_csv(all_path,index=False); out.to_csv(top_path,index=False); out.to_csv(ready_path,index=False)
        print('No candidates'); return
    status_order={'READY_NOW':0,'RECLAIM_PENDING':1,'WATCH_CLUSTER':2}
    grade_order={'A+':0,'A':1,'B':2,'C':3,'D':4}
    out['_s']=out['status'].map(status_order).fillna(9); out['_g']=out['grade'].map(grade_order).fillna(9)
    out=out.sort_values(['_s','_g','quality_score','rs_vs_topix_pct'],ascending=[True,True,False,False]).drop(columns=['_s','_g'])
    out.to_csv(all_path,index=False); out.head(30).to_csv(top_path,index=False)
    ready=out[out['status']=='READY_NOW']; ready.to_csv(ready_path,index=False)
    print('\n=== JAPAN TOP 30 / USD 1B+ ===')
    cols=['symbol','status','grade','quality_score','market_cap_usd_bn','current_price_jpy','breakout_level_jpy','ema20_live_jpy','rs_vs_topix_pct','pct_below_52w_high']
    print(out[cols].head(30).to_string(index=False))
    print('\nREADY_NOW',len(ready),'TOTAL WATCH',len(out))


if __name__ == '__main__':
    main()
