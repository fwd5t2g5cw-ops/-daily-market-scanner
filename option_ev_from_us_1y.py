from __future__ import annotations

from math import erf, exp, log, sqrt
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

INFILE = Path('backtest_us_1y_results/all_signals.csv')
OUTDIR = Path('backtest_us_1y_results')
DTE_ENTRY = 30
RISK_FREE = 0.04
TRADING_TO_CALENDAR = 365.0 / 252.0
MIN_IV = 0.15
MAX_IV = 1.20
FALLBACK_IV = 0.30


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def bs_call(s: float, k: float, t_years: float, r: float, sigma: float) -> float:
    if t_years <= 0:
        return max(s - k, 0.0)
    if sigma <= 0 or s <= 0 or k <= 0:
        return max(s - k * exp(-r * t_years), 0.0)
    vol = sigma * sqrt(t_years)
    d1 = (log(s / k) + (r + 0.5 * sigma * sigma) * t_years) / vol
    d2 = d1 - vol
    return s * norm_cdf(d1) - k * exp(-r * t_years) * norm_cdf(d2)


def realized_vol_map(symbols: list[str], dates: list[str]) -> dict[tuple[str, str], float]:
    result: dict[tuple[str, str], float] = {}
    by_sym: dict[str, list[str]] = {}
    for sym, dt in zip(symbols, dates):
        by_sym.setdefault(sym, []).append(dt)
    for i, (sym, dts) in enumerate(by_sym.items(), 1):
        print(f'IV proxy [{i}/{len(by_sym)}] {sym}')
        start = (pd.to_datetime(min(dts)) - pd.Timedelta(days=60)).strftime('%Y-%m-%d')
        end = (pd.to_datetime(max(dts)) + pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        try:
            raw = yf.download(sym, start=start, end=end, interval='1d', auto_adjust=True,
                              progress=False, threads=False)
            if raw is None or raw.empty:
                continue
            if isinstance(raw.columns, pd.MultiIndex):
                raw.columns = raw.columns.get_level_values(0)
            close = pd.to_numeric(raw['Close'], errors='coerce').dropna()
            rv = np.log(close / close.shift(1)).rolling(20).std() * sqrt(252.0)
            idx_dates = pd.DatetimeIndex(rv.index).date
            for dt in dts:
                d = pd.Timestamp(dt).date()
                mask = idx_dates <= d
                vals = rv.loc[mask].dropna()
                if len(vals):
                    v = float(vals.iloc[-1])
                    result[(sym, dt)] = float(np.clip(v, MIN_IV, MAX_IV))
        except Exception as exc:
            print('vol download failed', sym, exc)
    return result


def main() -> None:
    if not INFILE.exists():
        raise RuntimeError(f'{INFILE} not found; run us_1y_signal_backtest.py first')
    OUTDIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INFILE)
    mask = (
        df['entry_marker'].astype(bool)
        & df['double_reclaim'].astype(bool)
        & df['outcome'].isin(['TARGET0', 'STOP'])
    )
    x = df.loc[mask].copy()
    if x.empty:
        raise RuntimeError('No resolved ENTRY + Double Reclaim trades found')

    x['date'] = pd.to_datetime(x['date']).dt.strftime('%Y-%m-%d')
    vol_lookup = realized_vol_map(x['symbol'].astype(str).tolist(), x['date'].tolist())
    x['iv_proxy'] = [vol_lookup.get((str(s), str(d)), FALLBACK_IV) for s, d in zip(x['symbol'], x['date'])]

    # Normalized ATM model: strike equals underlying entry price.
    # This intentionally avoids pretending we know each historical listed strike grid.
    x['strike'] = pd.to_numeric(x['entry_price'], errors='coerce')
    x['entry_option'] = [
        bs_call(float(s), float(k), DTE_ENTRY / 365.0, RISK_FREE, float(iv))
        for s, k, iv in zip(x['entry_price'], x['strike'], x['iv_proxy'])
    ]

    exit_vals = []
    rem_dtes = []
    for _, row in x.iterrows():
        days = max(float(row['days_to_exit']), 0.0)
        remaining = max(DTE_ENTRY - days * TRADING_TO_CALENDAR, 0.0)
        rem_dtes.append(remaining)
        if row['outcome'] == 'TARGET0':
            # User requested conservative winner valuation: intrinsic value only.
            value = max(float(row['target0']) - float(row['strike']), 0.0)
        else:
            # Losers: estimate remaining time value at the stock stop price.
            value = bs_call(float(row['stop']), float(row['strike']), remaining / 365.0,
                            RISK_FREE, float(row['iv_proxy']))
        exit_vals.append(value)

    x['remaining_dte_at_exit'] = rem_dtes
    x['exit_option_est'] = exit_vals
    x['option_pnl_per_share'] = x['exit_option_est'] - x['entry_option']
    x['option_return_pct'] = 100.0 * x['option_pnl_per_share'] / x['entry_option']
    x['option_pnl_per_contract'] = 100.0 * x['option_pnl_per_share']

    x.to_csv(OUTDIR / 'option_ev_entry_double_reclaim_trades.csv', index=False)

    wins = x[x['outcome'] == 'TARGET0']
    losses = x[x['outcome'] == 'STOP']
    summary = pd.DataFrame([{
        'model': 'ENTRY + Double Reclaim | 30D ATM Call | winner intrinsic only',
        'resolved_trades': len(x),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate_pct': round(100.0 * len(wins) / len(x), 2),
        'avg_entry_option_per_share': round(x['entry_option'].mean(), 4),
        'avg_win_pnl_per_contract': round(wins['option_pnl_per_contract'].mean(), 2),
        'avg_loss_pnl_per_contract': round(losses['option_pnl_per_contract'].mean(), 2),
        'avg_ev_per_contract': round(x['option_pnl_per_contract'].mean(), 2),
        'median_ev_per_contract': round(x['option_pnl_per_contract'].median(), 2),
        'avg_return_pct': round(x['option_return_pct'].mean(), 2),
        'median_return_pct': round(x['option_return_pct'].median(), 2),
        'losses_within_5d_pct': round(100.0 * (pd.to_numeric(losses['days_to_exit'], errors='coerce') <= 5).mean(), 2),
        'avg_loss_days': round(pd.to_numeric(losses['days_to_exit'], errors='coerce').mean(), 2),
        'avg_remaining_dte_on_stop': round(losses['remaining_dte_at_exit'].mean(), 2),
        'avg_iv_proxy_pct': round(100.0 * x['iv_proxy'].mean(), 2),
    }])
    summary.to_csv(OUTDIR / 'option_ev_summary.csv', index=False)

    candle_rows = []
    for candle, g in x.groupby('candle_pattern'):
        candle_rows.append({
            'candle_pattern': candle,
            'trades': len(g),
            'win_rate_pct': round(100.0 * (g['outcome'] == 'TARGET0').mean(), 2),
            'avg_ev_per_contract': round(g['option_pnl_per_contract'].mean(), 2),
            'avg_return_pct': round(g['option_return_pct'].mean(), 2),
        })
    pd.DataFrame(candle_rows).sort_values('avg_ev_per_contract', ascending=False).to_csv(
        OUTDIR / 'option_ev_by_candle.csv', index=False)

    print('\n=== OPTION EV SUMMARY ===')
    print(summary.to_string(index=False))
    print('\n=== OPTION EV BY CANDLE ===')
    print(pd.DataFrame(candle_rows).sort_values('avg_ev_per_contract', ascending=False).to_string(index=False))


if __name__ == '__main__':
    main()
