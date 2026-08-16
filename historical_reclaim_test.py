from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def s(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors='coerce').astype(float)


def load_us_symbols():
    subprocess.run([sys.executable, 'build_universes.py', '--markets', 'us'], check=True)
    p = Path('data/us_universe.txt')
    return list(dict.fromkeys(x.strip().upper() for x in p.read_text().splitlines() if x.strip() and not x.startswith('#')))


def frame(data, symbol, single=False):
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    need = ['Open','High','Low','Close','Volume']
    if any(c not in d.columns for c in need):
        return None
    d = d.dropna(subset=need)
    return d if len(d) >= 220 else None


def analyze_reclaim(d: pd.DataFrame, spy: pd.DataFrame, as_of: str):
    """Reproduce Trend Pullback Stock Screener v1.1 ENTRY logic as closely as possible."""
    cutoff = pd.Timestamp(as_of)
    try:
        x = d.loc[pd.to_datetime(d.index).normalize() <= cutoff].copy()
        sx = spy.loc[pd.to_datetime(spy.index).normalize() <= cutoff].copy()
    except Exception:
        return None
    if len(x) < 220 or len(sx) < 70:
        return None

    c,h,l,v,o = map(s,[x.Close,x.High,x.Low,x.Volume,x.Open])
    sc = s(sx.Close)

    # Pine v1.1 defaults.
    ema20 = c.ewm(span=20, adjust=False).mean()
    ema50 = c.ewm(span=50, adjust=False).mean()
    sma200 = c.rolling(200).mean()
    avgvol = v.rolling(20).mean()
    avgdollar = (c * v).rolling(20).mean()
    yearhigh = h.rolling(252, min_periods=20).max()

    spy_ema20 = sc.ewm(span=20, adjust=False).mean()
    spy_ema50 = sc.ewm(span=50, adjust=False).mean()

    vals = [ema20.iloc[-1], ema50.iloc[-1], sma200.iloc[-1], avgvol.iloc[-1], avgdollar.iloc[-1], yearhigh.iloc[-1], spy_ema20.iloc[-1], spy_ema50.iloc[-1]]
    if any(pd.isna(z) for z in vals) or len(c) <= 63 or len(sc) <= 63:
        return None

    close=float(c.iloc[-1]); high=float(h.iloc[-1]); low=float(l.iloc[-1]); open_=float(o.iloc[-1]); vol=float(v.iloc[-1])
    e20=float(ema20.iloc[-1]); e50=float(ema50.iloc[-1]); s200=float(sma200.iloc[-1]); hi52=float(yearhigh.iloc[-1])
    av=float(avgvol.iloc[-1]); adv=float(avgdollar.iloc[-1])

    # 2. Trend calculation: close > EMA20 > EMA50 > SMA200, EMA50 rising vs 10 bars,
    # SMA200 rising vs 20 bars, and <=12% above EMA20.
    if len(ema50) <= 10 or len(sma200) <= 20:
        return None
    trend_alignment = close > e20 > e50 > s200
    ema50_rising = e50 > float(ema50.iloc[-11])
    sma200_rising = s200 > float(sma200.iloc[-21])
    strong_uptrend = bool(trend_alignment and ema50_rising and sma200_rising)
    pct_above_ema20 = ((close/e20)-1)*100 if e20 > 0 else np.nan
    not_overextended = bool(pd.notna(pct_above_ema20) and pct_above_ema20 <= 12.0)

    # 3. Liquidity defaults from Pine.
    liquid = bool(close >= 10 and av >= 500_000 and adv >= 20_000_000)

    # 4. <=20% below 52-week high and positive 63-session relative return vs SPY.
    pct_below_high = ((hi52-close)/hi52)*100 if hi52 > 0 else np.nan
    near_year_high = bool(pd.notna(pct_below_high) and pct_below_high <= 20.0)
    stock_return = close/float(c.iloc[-64])-1 if float(c.iloc[-64]) > 0 else np.nan
    spy_return = float(sc.iloc[-1])/float(sc.iloc[-64])-1 if float(sc.iloc[-64]) > 0 else np.nan
    relative_strength = stock_return - spy_return if pd.notna(stock_return) and pd.notna(spy_return) else np.nan
    outperforming_spy = bool(pd.notna(relative_strength) and relative_strength > 0)

    # 5. Market filter: SPY > EMA20 > EMA50.
    spy_close=float(sc.iloc[-1]); se20=float(spy_ema20.iloc[-1]); se50=float(spy_ema50.iloc[-1])
    market_pass = bool(spy_close > se20 > se50)

    # 6. Pine breakout logic exactly:
    # priorResistance = highest(high[1], 50)
    # breakout = close > priorResistance*1.01 and close[1] <= priorResistance
    prior = h.shift(1).rolling(50).max()
    threshold = prior * 1.01
    breakout = (c > threshold) & (c.shift(1) <= prior)

    bo_idx = np.flatnonzero(breakout.fillna(False).to_numpy())
    if len(bo_idx) == 0:
        return None
    today_i = len(c)-1
    eligible = [i for i in bo_idx if i < today_i]
    if not eligible:
        return None
    bi = int(eligible[-1])
    level = float(prior.iloc[bi])
    bars_since = today_i-bi
    valid_breakout_age = bool(1 <= bars_since <= 30)
    if not valid_breakout_age or not np.isfinite(level) or level <= 0:
        return None

    # 8. Pine reclaim trigger is SAME-DAY low undercut and same-day close reclaim.
    lowest_allowed = level * 0.97
    slight_undercut = bool(low < level and low >= lowest_allowed)
    reclaimed = bool(close > level)
    bullish_candle = bool(close > open_ and close >= (high+low)/2.0)
    candle_range = high-low
    strong_bearish = bool(candle_range > 0 and close < open_ and (open_-close)/candle_range >= 0.65)
    reclaim_trigger = bool(valid_breakout_age and slight_undercut and reclaimed and bullish_candle and not strong_bearish)

    entry_candidate = bool(
        strong_uptrend and not_overextended and liquid and near_year_high and
        outperforming_spy and market_pass and reclaim_trigger
    )
    if not entry_candidate:
        return None

    return {
        'date': as_of,
        'close': round(close,2),
        'breakout_date': str(pd.Timestamp(x.index[bi]).date()),
        'breakout_level': round(level,2),
        'bars_since_breakout': bars_since,
        'intraday_undercut_pct': round((low/level-1)*100,2),
        'close_above_level_pct': round((close/level-1)*100,2),
        'pct_below_52w_high': round(pct_below_high,2),
        'pct_above_ema20': round(pct_above_ema20,2),
        'rs_vs_spy_pct': round(relative_strength*100,2),
        'avg_volume_20d': int(av),
        'avg_dollar_volume_m': round(adv/1_000_000,2),
        'market_pass': market_pass,
        'entry_candidate': True,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dates', default='2026-08-04,2026-08-05,2026-08-06,2026-08-07')
    ap.add_argument('--batch-size', type=int, default=100)
    ap.add_argument('--outdir', default='reclaim_test_results')
    a=ap.parse_args()
    dates=[x.strip() for x in a.dates.split(',') if x.strip()]
    parsed=[datetime.strptime(x,'%Y-%m-%d').date() for x in dates]
    start=(min(parsed)-timedelta(days=650)).isoformat(); end=(max(parsed)+timedelta(days=1)).isoformat()

    spy=yf.download('SPY',start=start,end=end,interval='1d',auto_adjust=True,progress=False)
    if spy is None or spy.empty:
        raise RuntimeError('SPY download failed')
    if isinstance(spy.columns,pd.MultiIndex):
        spy.columns=spy.columns.get_level_values(0)

    syms=load_us_symbols(); rows=[]
    for st in range(0,len(syms),a.batch_size):
        batch=syms[st:st+a.batch_size]
        print(f'Downloading {st+1}-{min(st+a.batch_size,len(syms))} of {len(syms)}')
        try:
            data=yf.download(batch,start=start,end=end,interval='1d',group_by='ticker',auto_adjust=True,threads=True,progress=False)
        except Exception as e:
            print('Batch failed',e); continue
        single=len(batch)==1
        for sym in batch:
            d=frame(data,sym,single)
            if d is None: continue
            for dt in dates:
                try:
                    r=analyze_reclaim(d,spy,dt)
                    if r:
                        r['symbol']=sym; rows.append(r)
                except Exception as e:
                    print('skip',sym,dt,e)
        time.sleep(.35)

    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows)
    if not df.empty:
        df=df.sort_values(['date','rs_vs_spy_pct','pct_below_52w_high'],ascending=[True,False,True])
    df.to_csv(out/'reclaim_candidates.csv',index=False)
    psx=df[df.symbol.eq('PSX')] if not df.empty and 'symbol' in df.columns else pd.DataFrame()
    psx.to_csv(out/'psx_check.csv',index=False)

    print('\n=== PSX CHECK ===')
    print('(none)' if psx.empty else psx.to_string(index=False))
    print('\n=== COUNTS ===')
    print('(none)' if df.empty else df.groupby('date').size().to_string())

if __name__=='__main__':
    main()
