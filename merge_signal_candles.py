from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf


def split_download(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
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


def download_daily(symbols: list[str]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), 100):
        group = symbols[i:i+100]
        try:
            raw = yf.download(group, period='10d', interval='1d', auto_adjust=True,
                              progress=False, threads=True, group_by='ticker')
            out.update(split_download(raw, group))
        except Exception as exc:
            print('candle download failed:', exc)
    return out


def classify_candle(df: pd.DataFrame) -> str:
    if df is None or df.empty or not {'Open','High','Low','Close'}.issubset(df.columns):
        return 'UNKNOWN'
    x = df.dropna(subset=['Open','High','Low','Close'])
    if x.empty:
        return 'UNKNOWN'
    cur = x.iloc[-1]
    o, h, l, c = map(float, [cur['Open'], cur['High'], cur['Low'], cur['Close']])
    r = h - l
    if r <= 0:
        return 'DOJI'
    body = abs(c-o)
    upper = h - max(o,c)
    lower = min(o,c) - l
    body_ratio = body / r
    if len(x) >= 2:
        prev = x.iloc[-2]
        po, pc = float(prev['Open']), float(prev['Close'])
        if c > o and pc < po and o <= pc and c >= po:
            return 'BULLISH_ENGULFING'
        if c < o and pc > po and o >= pc and c <= po:
            return 'BEARISH_ENGULFING'
    if body_ratio <= 0.10:
        return 'DOJI'
    if lower >= max(body * 2.0, r * 0.45) and upper <= max(body, r * 0.20):
        return 'HAMMER' if c >= o else 'HAMMER_BEAR_BODY'
    if upper >= max(body * 2.0, r * 0.45) and lower <= max(body, r * 0.20):
        return 'SHOOTING_STAR' if c <= o else 'SHOOTING_STAR_BULL_BODY'
    if c > o and body_ratio >= 0.65 and (h-c)/r <= 0.15:
        return 'STRONG_BULL_CANDLE'
    if c < o and body_ratio >= 0.65 and (c-l)/r <= 0.15:
        return 'STRONG_BEAR_CANDLE'
    return 'BULL_CANDLE' if c > o else 'BEAR_CANDLE'


def truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower().isin(['true','1','yes'])


def read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        print(f'Ignoring unreadable/empty CSV {path}: {exc}')
        return pd.DataFrame()


def numeric_first(df: pd.DataFrame, names: list[str]) -> pd.Series:
    for name in names:
        if name in df.columns:
            return pd.to_numeric(df[name], errors='coerce')
    return pd.Series(np.nan, index=df.index, dtype=float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--market', choices=['us','hk','canada'], required=True)
    args = ap.parse_args()
    market = args.market
    outdir = Path(f'double_reclaim_results/{market}')
    base_path = outdir / f'{market}_double_reclaim_all.csv'
    entry_path = outdir / f'{market}_pine_entry_today.csv'

    base = read_csv_safe(base_path)
    entry = read_csv_safe(entry_path)
    outdir.mkdir(parents=True, exist_ok=True)
    high_path = outdir / f'{market}_high_conviction_entry_today.csv'

    if base.empty:
        print('No double reclaim base rows; writing empty unified output and exiting cleanly')
        base.to_csv(outdir / f'{market}_signals_with_candles.csv', index=False)
        base.to_csv(outdir / f'{market}_entry_marker_today.csv', index=False)
        base.to_csv(outdir / f'{market}_double_reclaim_today.csv', index=False)
        base.to_csv(outdir / f'{market}_reclaim_breakout_today.csv', index=False)
        base.to_csv(outdir / f'{market}_reclaim_breakout_only_today.csv', index=False)
        base.to_csv(high_path, index=False)
        return

    entry_syms = set(entry['symbol'].astype(str)) if not entry.empty and 'symbol' in entry.columns else set()
    symbols = list(dict.fromkeys(base['symbol'].astype(str).tolist() + list(entry_syms)))
    daily = download_daily(symbols)
    candle_map = {s: classify_candle(daily.get(s, pd.DataFrame())) for s in symbols}

    current = pd.to_numeric(base.get('current_price'), errors='coerce')
    breakout = pd.to_numeric(base.get('breakout_level'), errors='coerce')
    undercut = pd.to_numeric(base.get('undercut_vs_breakout_pct'), errors='coerce')
    touched_bo = truthy(base['touched_breakout_today']) if 'touched_breakout_today' in base.columns else pd.Series(False, index=base.index)
    touched_ema = truthy(base['touched_ema20_today']) if 'touched_ema20_today' in base.columns else pd.Series(False, index=base.index)
    above_both = truthy(base['above_both_now']) if 'above_both_now' in base.columns else pd.Series(False, index=base.index)

    base['entry_marker'] = base['symbol'].astype(str).isin(entry_syms)
    base['double_reclaim'] = touched_bo & touched_ema & (undercut >= -3.0) & above_both
    base['reclaim_breakout'] = touched_bo & (undercut >= -3.0) & (current > breakout)
    base['reclaim_breakout_only'] = base['reclaim_breakout'] & ~base['entry_marker'] & ~base['double_reclaim']
    base['candle_pattern'] = base['symbol'].astype(str).map(candle_map).fillna('UNKNOWN')
    base['candle_side'] = np.where(base['candle_pattern'].str.contains('BULL|HAMMER', regex=True), 'BULL',
                           np.where(base['candle_pattern'].str.contains('BEAR|SHOOTING', regex=True), 'BEAR', 'NEUTRAL'))

    # HIGH CONVICTION ENTRY = formal ENTRY plus confirming structure/strength.
    rs = numeric_first(base, ['rs_vs_benchmark_pct','rs_vs_spy_pct','rs_vs_xiu_pct','rs_pct'])
    below_high = numeric_first(base, ['pct_below_52w_high'])
    above_ema20 = numeric_first(base, ['distance_above_ema20_pct','pct_above_ema20'])
    quality = numeric_first(base, ['quality_score','score'])
    grade = base['grade'].astype(str).str.upper() if 'grade' in base.columns else pd.Series('', index=base.index)

    hc_score = pd.Series(0, index=base.index, dtype=int)
    hc_score += np.where(base['double_reclaim'], 3, 0)
    hc_score += np.where(base['reclaim_breakout'], 2, 0)
    hc_score += np.where(rs >= 20, 2, np.where(rs >= 10, 1, 0))
    hc_score += np.where(grade.isin(['A+','A']), 2, np.where(grade.eq('B'), 1, 0))
    hc_score += np.where(quality >= 8, 1, 0)
    hc_score += np.where(below_high <= 5, 1, 0)
    hc_score += np.where(base['candle_side'].eq('BULL'), 1, 0)
    hc_score += np.where(above_ema20 <= 8, 1, 0)
    base['high_conviction_score'] = hc_score

    confirm_overlap = base['double_reclaim'] | base['reclaim_breakout']
    rs_ok = rs >= 10
    high_ok = below_high.isna() | (below_high <= 10)
    extension_ok = above_ema20.isna() | (above_ema20 <= 12)
    base['high_conviction_entry'] = base['entry_marker'] & confirm_overlap & rs_ok & high_ok & extension_ok & (base['high_conviction_score'] >= 6)

    reasons = []
    for idx, row in base.iterrows():
        r = []
        if bool(row['double_reclaim']): r.append('DOUBLE_RECLAIM')
        if bool(row['reclaim_breakout']): r.append('RECLAIM_BREAKOUT')
        rv = rs.loc[idx]
        if pd.notna(rv) and rv >= 20: r.append('RS20+')
        elif pd.notna(rv) and rv >= 10: r.append('RS10+')
        gv = grade.loc[idx]
        if gv in ('A+','A','B'): r.append(f'GRADE_{gv}')
        if row['candle_side'] == 'BULL': r.append('BULL_CANDLE')
        reasons.append('|'.join(r))
    base['high_conviction_reasons'] = reasons

    unified = outdir / f'{market}_signals_with_candles.csv'
    base.to_csv(unified, index=False)
    base[base['entry_marker']].to_csv(outdir / f'{market}_entry_marker_today.csv', index=False)
    base[base['double_reclaim']].to_csv(outdir / f'{market}_double_reclaim_today.csv', index=False)
    base[base['reclaim_breakout']].to_csv(outdir / f'{market}_reclaim_breakout_today.csv', index=False)
    base[base['reclaim_breakout_only']].to_csv(outdir / f'{market}_reclaim_breakout_only_today.csv', index=False)
    high = base[base['high_conviction_entry']].copy()
    if not high.empty:
        high = high.sort_values(['high_conviction_score'], ascending=False)
    high.to_csv(high_path, index=False)

    print('Unified signals:', len(base))
    print('ENTRY:', int(base['entry_marker'].sum()),
          'Double Reclaim:', int(base['double_reclaim'].sum()),
          'Reclaim Breakout:', int(base['reclaim_breakout'].sum()),
          'HIGH CONVICTION ENTRY:', int(base['high_conviction_entry'].sum()))
    print('Wrote', unified)
    print('Wrote', high_path)


if __name__ == '__main__':
    main()
