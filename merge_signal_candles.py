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
    """Treat missing, blank, whitespace-only, or headerless CSV output as no signals."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        print(f'Ignoring unreadable/empty CSV {path}: {exc}')
        return pd.DataFrame()


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

    if base.empty:
        print('No double reclaim base rows; writing empty unified output and exiting cleanly')
        outdir.mkdir(parents=True, exist_ok=True)
        base.to_csv(outdir / f'{market}_signals_with_candles.csv', index=False)
        base.to_csv(outdir / f'{market}_entry_marker_today.csv', index=False)
        base.to_csv(outdir / f'{market}_double_reclaim_today.csv', index=False)
        base.to_csv(outdir / f'{market}_reclaim_breakout_today.csv', index=False)
        base.to_csv(outdir / f'{market}_reclaim_breakout_only_today.csv', index=False)
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

    unified = outdir / f'{market}_signals_with_candles.csv'
    base.to_csv(unified, index=False)
    base[base['entry_marker']].to_csv(outdir / f'{market}_entry_marker_today.csv', index=False)
    base[base['double_reclaim']].to_csv(outdir / f'{market}_double_reclaim_today.csv', index=False)
    base[base['reclaim_breakout']].to_csv(outdir / f'{market}_reclaim_breakout_today.csv', index=False)
    base[base['reclaim_breakout_only']].to_csv(outdir / f'{market}_reclaim_breakout_only_today.csv', index=False)

    print('Unified signals:', len(base))
    print('ENTRY:', int(base['entry_marker'].sum()),
          'Double Reclaim:', int(base['double_reclaim'].sum()),
          'Reclaim Breakout:', int(base['reclaim_breakout'].sum()))
    print('Wrote', unified)


if __name__ == '__main__':
    main()
