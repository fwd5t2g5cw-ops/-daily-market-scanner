from pathlib import Path
import numpy as np
import pandas as pd

import us_sci_congestion_backtest as base

# Narrow SCI-style setup based on the first backtest findings.
base.OUTDIR = Path('backtest_us_sci_narrow_results')
base.MAX_SUPPORT_CLUSTER_PCT = 0.25
base.CONGESTION_MIN_BARS = 6
base.CONGESTION_MAX_BARS = 8

ALLOWED_CANDLES = {'BULL_CANDLE', 'STRONG_BULL_CANDLE'}


def summarize(g: pd.DataFrame) -> dict:
    resolved = g[g['outcome'].isin(['TARGET0', 'STOP', 'STOP_AMBIGUOUS'])].copy()
    wins = int((resolved['outcome'] == 'TARGET0').sum())
    losses = len(resolved) - wins
    fib_hits = int((g['hit_fib0382'] == True).sum())
    avg_r = pd.to_numeric(resolved['realized_r'], errors='coerce').mean() if len(resolved) else np.nan
    days = pd.to_numeric(resolved['days_to_exit'], errors='coerce')
    stops_5 = ((resolved['outcome'] != 'TARGET0') & (days <= 5)).sum() if len(resolved) else 0
    return {
        'setup': 'SCI_NARROW_6_8D_CLUSTER025_BULL',
        'signals': len(g),
        'resolved': len(resolved),
        'wins_target0': wins,
        'losses': losses,
        'target0_win_rate_pct': round(100 * wins / len(resolved), 2) if len(resolved) else np.nan,
        'fib0382_hit_rate_pct': round(100 * fib_hits / len(g), 2) if len(g) else np.nan,
        'avg_realized_r': round(float(avg_r), 3) if pd.notna(avg_r) else np.nan,
        'avg_days_to_exit': round(float(days.mean()), 2) if len(resolved) else np.nan,
        'median_days_to_exit': round(float(days.median()), 2) if len(resolved) else np.nan,
        'stops_within_5d_pct': round(100 * stops_5 / losses, 2) if losses else np.nan,
    }


def grouped_summary(df: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for value, g in df.groupby(col):
        s = summarize(g)
        s[col] = value
        rows.append(s)
    return pd.DataFrame(rows)


def main() -> None:
    # Re-run the same underlying SCI detector with the narrower structural gates.
    base.main()

    path = base.OUTDIR / 'sci_style_setups.csv'
    if not path.exists():
        raise RuntimeError('Base narrow scan did not create sci_style_setups.csv')

    df = pd.read_csv(path)
    if df.empty:
        pd.DataFrame([summarize(df)]).to_csv(base.OUTDIR / 'narrow_summary.csv', index=False)
        return

    df = df[df['candle_pattern'].isin(ALLOWED_CANDLES)].copy()
    df.to_csv(base.OUTDIR / 'sci_narrow_setups.csv', index=False)

    pd.DataFrame([summarize(df)]).to_csv(base.OUTDIR / 'narrow_summary.csv', index=False)
    grouped_summary(df, 'congestion_bars').to_csv(base.OUTDIR / 'narrow_by_congestion_bars.csv', index=False)
    grouped_summary(df, 'candle_pattern').to_csv(base.OUTDIR / 'narrow_by_candle.csv', index=False)

    if not df.empty:
        df['width_bucket'] = pd.cut(
            df['congestion_width_pct'],
            bins=[-np.inf, 2.0, 3.0, 4.0, 5.0, 6.0, np.inf],
            labels=['<=2%', '2-3%', '3-4%', '4-5%', '5-6%', '>6%'],
        )
        grouped_summary(df, 'width_bucket').to_csv(base.OUTDIR / 'narrow_by_width.csv', index=False)

        df['rs_bucket'] = pd.cut(
            df['rs_vs_spy_pct'],
            bins=[-np.inf, 5, 10, 15, 20, np.inf],
            labels=['<=5%', '5-10%', '10-15%', '15-20%', '>20%'],
        )
        grouped_summary(df, 'rs_bucket').to_csv(base.OUTDIR / 'narrow_by_rs.csv', index=False)

    print('\n=== NARROW SCI SUMMARY ===')
    print(pd.DataFrame([summarize(df)]).to_string(index=False))
    if not df.empty:
        print('\n=== BY CONGESTION BARS ===')
        print(grouped_summary(df, 'congestion_bars').to_string(index=False))
        print('\n=== BY CANDLE ===')
        print(grouped_summary(df, 'candle_pattern').to_string(index=False))


if __name__ == '__main__':
    main()
