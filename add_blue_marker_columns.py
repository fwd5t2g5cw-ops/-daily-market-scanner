from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import yfinance as yf


def _split_daily(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(map(str, raw.columns.get_level_values(0)))
        fields = {'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'}
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


def _add_candle_direction(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or 'symbol' not in df.columns:
        return df

    symbols = list(dict.fromkeys(df['symbol'].astype(str).str.upper()))
    try:
        raw = yf.download(
            symbols,
            period='5d',
            interval='1d',
            auto_adjust=True,
            progress=False,
            threads=True,
            group_by='ticker',
        )
        daily = _split_daily(raw, symbols)
    except Exception as exc:
        print('Could not fetch candle direction:', exc)
        daily = {}

    opens: dict[str, float] = {}
    closes: dict[str, float] = {}
    candles: dict[str, str] = {}

    for s in symbols:
        x = daily.get(s)
        if x is None or x.empty or not {'Open', 'Close'}.issubset(x.columns):
            candles[s] = 'UNKNOWN'
            continue
        x = x.dropna(subset=['Open', 'Close'])
        if x.empty:
            candles[s] = 'UNKNOWN'
            continue
        o = float(x['Open'].iloc[-1])
        c = float(x['Close'].iloc[-1])
        opens[s] = o
        closes[s] = c
        if c > o:
            candles[s] = 'BULL'
        elif c < o:
            candles[s] = 'BEAR'
        else:
            candles[s] = 'DOJI'

    syms = df['symbol'].astype(str).str.upper()
    df['day_open'] = syms.map(opens)
    df['day_close'] = syms.map(closes)
    df['candle'] = syms.map(candles).fillna('UNKNOWN')
    return df


def add_blue_marker_to_csv(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return
    try:
        df = pd.read_csv(path)
    except Exception:
        return
    required = {'touched_breakout_today', 'current_price', 'breakout_level', 'undercut_vs_breakout_pct'}
    if df.empty or not required.issubset(df.columns):
        return

    touched = df['touched_breakout_today'].astype(str).str.lower().isin(['true', '1', 'yes'])
    current = pd.to_numeric(df['current_price'], errors='coerce')
    breakout = pd.to_numeric(df['breakout_level'], errors='coerce')
    undercut = pd.to_numeric(df['undercut_vs_breakout_pct'], errors='coerce')

    # Blue marker = today's candle traded at/through the prior breakout level,
    # did not undercut more than the scanner's 3% tolerance, and is now back
    # above the breakout level. EMA20 is NOT required for this marker.
    blue = touched & (undercut >= -3.0) & (current > breakout)
    df['blue_marker'] = blue
    df['reclaimed_breakout_now'] = current > breakout

    if 'touched_ema20_today' in df.columns:
        touched_ema = df['touched_ema20_today'].astype(str).str.lower().isin(['true', '1', 'yes'])
        df['blue_marker_type'] = 'NONE'
        df.loc[blue, 'blue_marker_type'] = 'RECLAIM_BREAKOUT'
        df.loc[blue & touched_ema, 'blue_marker_type'] = 'DOUBLE_RECLAIM'
    else:
        df['blue_marker_type'] = df['blue_marker'].map({True: 'RECLAIM_BREAKOUT', False: 'NONE'})

    df.to_csv(path, index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--prefix', required=True)
    args = ap.parse_args()

    outdir = Path(args.dir)
    for path in outdir.glob('*.csv'):
        add_blue_marker_to_csv(path)

    all_path = outdir / f'{args.prefix}_double_reclaim_all.csv'
    blue_path = outdir / f'{args.prefix}_blue_marker_today.csv'
    if all_path.exists() and all_path.stat().st_size:
        df = pd.read_csv(all_path)
        if 'blue_marker' in df.columns:
            blue = df[df['blue_marker'].astype(str).str.lower().isin(['true', '1', 'yes'])].copy()
            blue = _add_candle_direction(blue)
            blue.to_csv(blue_path, index=False)
            if not blue.empty:
                display_cols = [c for c in ['symbol', 'candle', 'blue_marker_type', 'current_price', 'breakout_level', 'ema20_live'] if c in blue.columns]
                print('\n=== BLUE MARKERS TODAY ===')
                print(blue[display_cols].to_string(index=False))
            print(f'Blue markers today: {len(blue)} -> {blue_path}')


if __name__ == '__main__':
    main()
