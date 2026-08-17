from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


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
            if not blue.empty:
                sort_cols = [c for c in ['grade', 'quality_score'] if c in blue.columns]
                if sort_cols:
                    blue = blue.sort_values(sort_cols, ascending=[True, False][:len(sort_cols)])
            blue.to_csv(blue_path, index=False)
            print(f'Blue markers today: {len(blue)} -> {blue_path}')


if __name__ == '__main__':
    main()
