from __future__ import annotations

import argparse
from pathlib import Path
from datetime import time
import numpy as np
import pandas as pd
import yfinance as yf

NY = 'America/New_York'
FIB_ENTRY = 0.786
FIB_DEN = 1.0 - FIB_ENTRY


def _flat(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    if isinstance(x.columns, pd.MultiIndex):
        x.columns = x.columns.get_level_values(0)
    return x


def _localize_index(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    idx = pd.DatetimeIndex(x.index)
    if idx.tz is None:
        idx = idx.tz_localize(NY)
    else:
        idx = idx.tz_convert(NY)
    x.index = idx
    return x


def _download_5m(symbol: str, start: str, end: str):
    try:
        d = yf.download(symbol, start=start, end=end, interval='5m', auto_adjust=True,
                        prepost=False, progress=False, threads=False)
        if d is None or d.empty:
            return None
        return _localize_index(_flat(d))
    except Exception as e:
        print('download failed', symbol, e)
        return None


def _ema20_from_candidate(row: pd.Series) -> float:
    close = float(row['close'])
    pct = float(row['pct_above_ema20'])
    return close / (1.0 + pct / 100.0)


def _grade(rs: float, cluster_pct: float) -> str:
    if pd.notna(rs) and pd.notna(cluster_pct):
        if rs >= 15.0 and cluster_pct <= 0.5:
            return 'A'
        if rs >= 10.0 and cluster_pct <= 1.0:
            return 'B'
        if rs >= 10.0 and cluster_pct <= 2.0:
            return 'C'
    return 'D'


def evaluate_candidate(row: pd.Series, intraday: pd.DataFrame, end_date: pd.Timestamp,
                       touch_tolerance_pct: float = 0.25,
                       max_undercut_pct: float = 3.0):
    dt = pd.Timestamp(row['date']).date()
    day = intraday[intraday.index.date == dt].copy()
    if day.empty:
        return None

    entry_rows = day[day.index.time >= time(15, 55)]
    if entry_rows.empty:
        return None
    entry_ts = entry_rows.index[0]
    entry_price = float(entry_rows.iloc[0]['Open'])

    before = day[day.index < entry_ts]
    if before.empty:
        return None
    day_low = float(before['Low'].min())

    breakout = float(row['breakout_level'])
    ema20 = _ema20_from_candidate(row)
    tol = touch_tolerance_pct / 100.0

    touched_breakout = day_low <= breakout * (1.0 + tol)
    touched_ema20 = day_low <= ema20 * (1.0 + tol)
    not_too_deep = day_low >= breakout * (1.0 - max_undercut_pct / 100.0)
    above_both = entry_price > breakout and entry_price > ema20
    strict_double_reclaim = bool(touched_breakout and touched_ema20 and not_too_deep and above_both)

    cluster_pct = abs(ema20 / breakout - 1.0) * 100.0 if breakout > 0 else np.nan
    rs = pd.to_numeric(pd.Series([row.get('rs_vs_spy_pct', np.nan)]), errors='coerce').iloc[0]
    trade_grade = _grade(float(rs) if pd.notna(rs) else np.nan, cluster_pct)

    common = {
        'date': str(dt), 'symbol': row['symbol'],
        'entry_time': str(entry_ts), 'entry_price': round(entry_price, 4),
        'day_low_before_entry': round(day_low, 4),
        'breakout_level': round(breakout, 4), 'ema20_est': round(ema20, 4),
        'ema20_breakout_distance_pct': round(cluster_pct, 3) if pd.notna(cluster_pct) else np.nan,
        'trade_grade': trade_grade,
        'touched_breakout': touched_breakout, 'touched_ema20': touched_ema20,
        'above_both_355': above_both,
        'congestion_score': row.get('congestion_score', np.nan),
        'congestion_status': row.get('congestion_status', ''),
        'rs_vs_spy_pct': row.get('rs_vs_spy_pct', np.nan),
        'pct_below_52w_high': row.get('pct_below_52w_high', np.nan),
    }

    if not strict_double_reclaim:
        return {**common, 'strict_double_reclaim': False, 'outcome': 'NO_TRADE'}

    stop = day_low
    risk = entry_price - stop
    if risk <= 0:
        return None

    target0 = stop + risk / FIB_DEN
    fib0382 = stop + ((1.0 - 0.382) / FIB_DEN) * risk
    target_r = (target0 - entry_price) / risk

    future = intraday[(intraday.index >= entry_ts) & (intraday.index.date <= end_date.date())]
    outcome = 'OPEN'
    exit_ts = pd.NaT
    exit_price = np.nan
    realized_r = np.nan
    bars = 0

    for ts, bar in future.iterrows():
        bars += 1
        lo = float(bar['Low'])
        hi = float(bar['High'])
        hit_stop = lo <= stop
        hit_target = hi >= target0
        if hit_stop and hit_target:
            outcome = 'STOP_SAME_BAR_AMBIGUOUS'
            exit_ts = ts; exit_price = stop; realized_r = -1.0
            break
        if hit_stop:
            outcome = 'STOP'
            exit_ts = ts; exit_price = stop; realized_r = -1.0
            break
        if hit_target:
            outcome = 'TARGET0'
            exit_ts = ts; exit_price = target0; realized_r = target_r
            break

    return {
        **common,
        'strict_double_reclaim': True,
        'stop': round(stop, 4), 'fib_0382': round(fib0382, 4),
        'target0': round(target0, 4), 'risk_per_share': round(risk, 4),
        'target_r': round(target_r, 3), 'outcome': outcome,
        'exit_time': '' if pd.isna(exit_ts) else str(exit_ts),
        'exit_price': '' if pd.isna(exit_price) else round(float(exit_price), 4),
        'realized_r': '' if pd.isna(realized_r) else round(float(realized_r), 3),
        'bars_5m_to_exit': bars if outcome != 'OPEN' else '',
    }


def _summarize(g: pd.DataFrame, label: str, key: str):
    resolved = g[g['outcome'].isin(['TARGET0','STOP','STOP_SAME_BAR_AMBIGUOUS'])]
    wins = int((resolved['outcome'] == 'TARGET0').sum())
    losses = int((resolved['outcome'] != 'TARGET0').sum())
    return {
        key: label,
        'trades': len(g),
        'resolved': len(resolved),
        'wins': wins,
        'losses': losses,
        'win_rate_pct': round(100*wins/len(resolved), 2) if len(resolved) else np.nan,
        'open': int((g['outcome'] == 'OPEN').sum()),
        'avg_realized_r': round(pd.to_numeric(resolved['realized_r'], errors='coerce').mean(), 3) if len(resolved) else np.nan,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--end-date', default='2026-08-14')
    ap.add_argument('--touch-tolerance-pct', type=float, default=0.25)
    ap.add_argument('--outdir', default='backtest_355_results')
    args = ap.parse_args()

    inp = pd.read_csv(args.input)
    inp['date'] = pd.to_datetime(inp['date']).dt.strftime('%Y-%m-%d')
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    start = (pd.to_datetime(inp['date']).min() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    end = (pd.Timestamp(args.end_date) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = pd.Timestamp(args.end_date)

    rows = []
    failed = []
    for i, (sym, grp) in enumerate(inp.groupby('symbol'), 1):
        print(f'[{i}/{inp.symbol.nunique()}] {sym}')
        d = _download_5m(sym, start, end)
        if d is None:
            failed.append(sym)
            continue
        for _, row in grp.iterrows():
            try:
                r = evaluate_candidate(row, d, end_date,
                                       touch_tolerance_pct=args.touch_tolerance_pct)
                if r is not None:
                    rows.append(r)
            except Exception as e:
                print('skip', sym, row['date'], e)

    all_df = pd.DataFrame(rows)
    all_df.to_csv(outdir / 'all_candidates_355.csv', index=False)
    trades = all_df[all_df['strict_double_reclaim'] == True].copy() if not all_df.empty else pd.DataFrame()
    if not trades.empty:
        grade_order = {'A':0, 'B':1, 'C':2, 'D':3}
        trades['_grade_order'] = trades['trade_grade'].map(grade_order).fillna(9)
        trades = trades.sort_values(['date','_grade_order','congestion_score','rs_vs_spy_pct'], ascending=[True,True,False,False]).drop(columns=['_grade_order'])
    trades.to_csv(outdir / 'strict_double_reclaim_trades.csv', index=False)
    pd.DataFrame({'symbol': failed}).to_csv(outdir / 'failed_symbols.csv', index=False)

    by_date = []
    by_grade = []
    if not trades.empty:
        for dt, g in trades.groupby('date'):
            by_date.append(_summarize(g, dt, 'date'))
        for grade in ['A','B','C','D']:
            g = trades[trades['trade_grade'] == grade]
            if len(g):
                by_grade.append(_summarize(g, grade, 'trade_grade'))
        abc = trades[trades['trade_grade'].isin(['A','B','C'])]
        if len(abc):
            by_grade.append(_summarize(abc, 'A+B+C', 'trade_grade'))

    pd.DataFrame(by_date).to_csv(outdir / 'summary_by_date.csv', index=False)
    pd.DataFrame(by_grade).to_csv(outdir / 'summary_by_grade.csv', index=False)

    print('Strict double-reclaim trades:', len(trades))
    print('Failed symbols:', len(failed))
    if not trades.empty:
        print(trades[['date','symbol','trade_grade','rs_vs_spy_pct','ema20_breakout_distance_pct','entry_price','stop','target0','outcome','realized_r']].to_string(index=False))
        print('\n=== GRADE SUMMARY ===')
        print(pd.DataFrame(by_grade).to_string(index=False))

if __name__ == '__main__':
    main()
