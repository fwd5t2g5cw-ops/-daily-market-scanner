from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

import us_1y_signal_backtest as base

OUTDIR = Path('backtest_us_entry_double_bullish_engulfing_results')
FOLLOW_DAYS = 20
FIB_ENTRY = 0.786
FIB_DEN = 1.0 - FIB_ENTRY


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    syms = [x.strip().upper() for x in base.UNIVERSE.read_text().splitlines() if x.strip()]
    syms = list(dict.fromkeys(syms))
    data = base.download(syms + [base.BENCHMARK])
    spy = data.get(base.BENCHMARK)
    if spy is None or spy.empty:
        raise RuntimeError('SPY unavailable')

    candidates = []
    for n, sym in enumerate(syms, 1):
        if n % 100 == 0:
            print('processed', n, '/', len(syms))
        d = data.get(sym)
        if d is None or d.empty:
            continue
        try:
            rows = base.evaluate_symbol(sym, d, spy)
        except Exception as exc:
            print('skip', sym, exc)
            continue
        for r in rows:
            if not (bool(r.get('entry_marker')) and bool(r.get('double_reclaim'))):
                continue
            if r.get('candle_pattern') != 'BULLISH_ENGULFING':
                continue

            dt = pd.Timestamp(r['date'])
            dd = d[['Open','High','Low','Close','Volume']].dropna().copy()
            idx_dates = pd.to_datetime(dd.index).normalize()
            matches = np.flatnonzero(idx_dates == dt.normalize())
            if len(matches) == 0:
                continue
            i = int(matches[-1])

            entry = float(r['entry_price'])
            stop = float(r['stop'])
            risk = entry - stop
            if risk <= 0:
                continue
            fib0382 = stop + ((1.0 - 0.382) / FIB_DEN) * risk
            target0 = stop + risk / FIB_DEN

            outcome = 'OPEN'
            exit_date = ''
            days_to_exit = np.nan
            hit0382 = False
            realized_r = np.nan
            for j in range(i + 1, min(len(dd), i + 1 + FOLLOW_DAYS)):
                lo = float(dd['Low'].iloc[j])
                hi = float(dd['High'].iloc[j])
                if hi >= fib0382:
                    hit0382 = True
                hit_s = lo <= stop
                hit_t = hi >= target0
                if hit_s and hit_t:
                    outcome = 'STOP_AMBIGUOUS'
                    exit_date = str(pd.Timestamp(dd.index[j]).date())
                    days_to_exit = j - i
                    realized_r = -1.0
                    break
                if hit_s:
                    outcome = 'STOP'
                    exit_date = str(pd.Timestamp(dd.index[j]).date())
                    days_to_exit = j - i
                    realized_r = -1.0
                    break
                if hit_t:
                    outcome = 'TARGET0'
                    exit_date = str(pd.Timestamp(dd.index[j]).date())
                    days_to_exit = j - i
                    realized_r = (target0-entry)/risk
                    hit0382 = True
                    break

            candidates.append({
                **r,
                'fib0382': round(fib0382,4),
                'target0': round(target0,4),
                'hit_fib0382': hit0382,
                'outcome': outcome,
                'exit_date': exit_date,
                'days_to_exit': days_to_exit,
                'realized_r': round(realized_r,3) if np.isfinite(realized_r) else np.nan,
            })

    out = pd.DataFrame(candidates)
    out.to_csv(OUTDIR/'trades.csv', index=False)
    if out.empty:
        pd.DataFrame([{'signals':0}]).to_csv(OUTDIR/'summary.csv', index=False)
        print('No matching trades')
        return

    resolved = out[out['outcome'].isin(['TARGET0','STOP','STOP_AMBIGUOUS'])]
    wins = int((resolved['outcome']=='TARGET0').sum())
    losses = len(resolved)-wins
    stop_days = pd.to_numeric(resolved.loc[resolved['outcome']!='TARGET0','days_to_exit'], errors='coerce')
    summary = pd.DataFrame([{
        'setup':'ENTRY + DOUBLE_RECLAIM + BULLISH_ENGULFING',
        'signals':len(out),
        'resolved':len(resolved),
        'wins_target0':wins,
        'losses':losses,
        'target0_win_rate_pct':round(100*wins/len(resolved),2) if len(resolved) else np.nan,
        'fib0382_hit_rate_pct':round(100*out['hit_fib0382'].astype(bool).mean(),2),
        'avg_days_to_exit':round(pd.to_numeric(resolved['days_to_exit'],errors='coerce').mean(),2) if len(resolved) else np.nan,
        'median_days_to_exit':round(pd.to_numeric(resolved['days_to_exit'],errors='coerce').median(),2) if len(resolved) else np.nan,
        'stops_within_5d_pct':round(100*(stop_days<=5).mean(),2) if losses else np.nan,
        'avg_realized_r':round(pd.to_numeric(resolved['realized_r'],errors='coerce').mean(),3) if len(resolved) else np.nan,
        'avg_entry_price':round(pd.to_numeric(out['entry_price'],errors='coerce').mean(),2),
        'avg_risk_pct':round(100*((pd.to_numeric(out['entry_price'])-pd.to_numeric(out['stop']))/pd.to_numeric(out['entry_price'])).mean(),2),
    }])
    summary.to_csv(OUTDIR/'summary.csv', index=False)

    # Diagnostics only; these do not filter the setup.
    out['rs_bucket'] = pd.cut(pd.to_numeric(out['rs_vs_spy_pct'], errors='coerce'), [-np.inf,0,5,10,15,np.inf], labels=['<=0','0-5','5-10','10-15','15+'])
    by_rs=[]
    for label,g in out.groupby('rs_bucket', observed=False):
        rr=g[g['outcome'].isin(['TARGET0','STOP','STOP_AMBIGUOUS'])]
        if len(rr)==0: continue
        w=int((rr['outcome']=='TARGET0').sum())
        by_rs.append({'rs_bucket':str(label),'signals':len(g),'resolved':len(rr),'target0_win_rate_pct':round(100*w/len(rr),2),'avg_realized_r':round(pd.to_numeric(rr['realized_r'],errors='coerce').mean(),3)})
    pd.DataFrame(by_rs).to_csv(OUTDIR/'summary_by_rs.csv', index=False)

    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
