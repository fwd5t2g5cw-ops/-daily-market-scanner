from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

UNIVERSE = Path('data/us_1b_universe.txt')
OUTDIR = Path('backtest_us_sci_congestion_results')
BENCHMARK = 'SPY'

EMA20 = 20
EMA50 = 50
SMA200 = 200
RESISTANCE_BARS = 50
RS_LOOKBACK = 63
FOLLOW_DAYS = 20
FIB_ENTRY = 0.786
FIB_DEN = 1.0 - FIB_ENTRY

# SCI-style setup definition agreed with the user.
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500_000
MIN_DOLLAR_VOL = 20_000_000.0
MAX_BELOW_HIGH = 20.0
MAX_ABOVE_EMA20 = 12.0
MAX_BREAKOUT_AGE = 30
MAX_SUPPORT_CLUSTER_PCT = 1.5
MAX_UNDERCUT_PCT = 3.0
SUPPORT_TOUCH_TOL_PCT = 0.5
MIN_POST_BREAKOUT_PUSH_PCT = 3.0
CONGESTION_MIN_BARS = 3
CONGESTION_MAX_BARS = 8
MAX_CONGESTION_WIDTH_PCT = 6.0
MAX_CONGESTION_SLOPE_PCT = 3.0
MAX_CONGESTION_AVG_VOL_RATIO = 0.95


def split(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if raw is None or raw.empty:
        return out
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = set(map(str, raw.columns.get_level_values(0)))
        fields = {'Open', 'High', 'Low', 'Close', 'Volume'}
        by_ticker = len(fields & level0) < 3
        for s in symbols:
            try:
                x = raw.xs(s, axis=1, level=0 if by_ticker else 1, drop_level=True).dropna(how='all')
                if not x.empty:
                    out[s] = x
            except Exception:
                pass
    elif len(symbols) == 1:
        out[symbols[0]] = raw.dropna(how='all')
    return out


def download(symbols: list[str], chunk: int = 120) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i + chunk]
        print(f'batch {i+1}-{min(i+chunk, len(symbols))}/{len(symbols)}')
        try:
            raw = yf.download(
                group, period='2y', interval='1d', auto_adjust=True,
                progress=False, threads=True, group_by='ticker'
            )
            out.update(split(raw, group))
        except Exception as exc:
            print('batch failed', exc)
    return out


def candle_pattern(o, h, l, c, po, pc) -> str:
    r = max(h - l, 1e-9)
    body = abs(c - o)
    upper = h - max(o, c)
    lower = min(o, c) - l
    if body / r <= 0.10:
        return 'DOJI'
    if c > o and po > pc and c >= po and o <= pc:
        return 'BULLISH_ENGULFING'
    if c < o and pc > po and o >= pc and c <= po:
        return 'BEARISH_ENGULFING'
    if lower >= 2 * body and upper <= body:
        return 'HAMMER'
    if upper >= 2 * body and lower <= body:
        return 'SHOOTING_STAR'
    if c > o and body / r >= 0.65:
        return 'STRONG_BULL_CANDLE'
    if c < o and body / r >= 0.65:
        return 'STRONG_BEAR_CANDLE'
    return 'BULL_CANDLE' if c > o else 'BEAR_CANDLE'


def summarize(g: pd.DataFrame, label: str, key: str) -> dict:
    resolved = g[g['outcome'].isin(['TARGET0', 'STOP', 'STOP_AMBIGUOUS'])]
    wins = int((resolved['outcome'] == 'TARGET0').sum())
    losses = len(resolved) - wins
    target0382 = int((g['hit_fib0382'] == True).sum())
    return {
        key: label,
        'signals': len(g),
        'resolved': len(resolved),
        'wins_target0': wins,
        'losses': losses,
        'target0_win_rate_pct': round(100 * wins / len(resolved), 2) if len(resolved) else np.nan,
        'fib0382_hit_rate_pct': round(100 * target0382 / len(g), 2) if len(g) else np.nan,
        'avg_days_to_exit': round(pd.to_numeric(resolved['days_to_exit'], errors='coerce').mean(), 2) if len(resolved) else np.nan,
        'median_days_to_exit': round(pd.to_numeric(resolved['days_to_exit'], errors='coerce').median(), 2) if len(resolved) else np.nan,
        'stops_within_5d_pct': round(100 * (((resolved['outcome'] != 'TARGET0') & (pd.to_numeric(resolved['days_to_exit'], errors='coerce') <= 5)).sum()) / losses, 2) if losses else np.nan,
        'avg_realized_r': round(pd.to_numeric(resolved['realized_r'], errors='coerce').mean(), 3) if len(resolved) else np.nan,
    }


def evaluate_symbol(sym: str, d: pd.DataFrame, spy: pd.DataFrame) -> list[dict]:
    d = d[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().copy()
    spy = spy[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().copy()
    common = d.index.intersection(spy.index)
    d = d.loc[common]
    spy = spy.loc[common]
    if len(d) < 330:
        return []

    o, h, l, c, v = d.Open, d.High, d.Low, d.Close, d.Volume
    e20 = c.ewm(span=EMA20, adjust=False).mean()
    e50 = c.ewm(span=EMA50, adjust=False).mean()
    s200 = c.rolling(SMA200).mean()
    avgvol20 = v.rolling(20).mean()
    avgdol20 = (c * v).rolling(20).mean()
    year_high = h.rolling(252).max()
    resistance = h.shift(1).rolling(RESISTANCE_BARS).max()
    breakout = (c > resistance * 1.01) & (c.shift(1) <= resistance)

    spyc = spy.Close
    spye20 = spyc.ewm(span=20, adjust=False).mean()
    spye50 = spyc.ewm(span=50, adjust=False).mean()

    rows: list[dict] = []
    start = max(252, len(d) - 260)
    bo_indices = np.flatnonzero(breakout.fillna(False).to_numpy())

    for i in range(start, len(d) - 1):
        prior_bos = bo_indices[bo_indices < i]
        if not len(prior_bos):
            continue
        b = int(prior_bos[-1])
        age = i - b
        if age < CONGESTION_MIN_BARS + 1 or age > MAX_BREAKOUT_AGE:
            continue

        level = float(resistance.iloc[b])
        if not np.isfinite(level) or level <= 0:
            continue

        close = float(c.iloc[i]); op = float(o.iloc[i]); hi = float(h.iloc[i]); lo = float(l.iloc[i])
        ema20 = float(e20.iloc[i])
        if not np.isfinite(ema20) or ema20 <= 0:
            continue

        # Pine-like quality gates.
        strong_trend = bool(close > e20.iloc[i] > e50.iloc[i] > s200.iloc[i] and e50.iloc[i] > e50.iloc[i-10] and s200.iloc[i] > s200.iloc[i-20])
        not_overextended = ((close / ema20 - 1) * 100) <= MAX_ABOVE_EMA20
        liquid = bool(close >= MIN_PRICE and avgvol20.iloc[i] >= MIN_AVG_VOLUME and avgdol20.iloc[i] >= MIN_DOLLAR_VOL)
        below_high = ((year_high.iloc[i] - close) / year_high.iloc[i] * 100) if year_high.iloc[i] > 0 else np.nan
        near_high = bool(np.isfinite(below_high) and below_high <= MAX_BELOW_HIGH)
        stock_ret = close / c.iloc[i - RS_LOOKBACK] - 1
        spy_ret = spyc.iloc[i] / spyc.iloc[i - RS_LOOKBACK] - 1
        rs = stock_ret - spy_ret
        market_pass = bool(spyc.iloc[i] > spye20.iloc[i] > spye50.iloc[i])
        if not (strong_trend and not_overextended and liquid and near_high and rs > 0 and market_pass):
            continue

        cluster_pct = abs(ema20 / level - 1.0) * 100.0
        if cluster_pct > MAX_SUPPORT_CLUSTER_PCT:
            continue

        # There must be a real post-breakout push before the pullback/congestion.
        post = d.iloc[b + 1:i + 1]
        if post.empty:
            continue
        post_peak = float(post['High'].max())
        push_pct = (post_peak / level - 1.0) * 100.0
        if push_pct < MIN_POST_BREAKOUT_PUSH_PCT:
            continue

        found = None
        for n in range(CONGESTION_MIN_BARS, CONGESTION_MAX_BARS + 1):
            cs = i - n + 1
            if cs <= b:
                continue
            cong = d.iloc[cs:i + 1]
            ch = float(cong['High'].max())
            cl = float(cong['Low'].min())
            mid = (ch + cl) / 2.0
            width_pct = ((ch - cl) / mid * 100.0) if mid > 0 else np.inf
            if width_pct > MAX_CONGESTION_WIDTH_PCT:
                continue

            first_close = float(cong['Close'].iloc[0])
            last_close = float(cong['Close'].iloc[-1])
            slope_pct = abs(last_close / first_close - 1.0) * 100.0 if first_close > 0 else np.inf
            if slope_pct > MAX_CONGESTION_SLOPE_PCT:
                continue

            # Congestion sits on the breakout/EMA20 support area, allowing only a shallow undercut.
            support_floor = min(level, float(e20.iloc[i]))
            support_touch = cl <= max(level, ema20) * (1 + SUPPORT_TOUCH_TOL_PCT / 100.0)
            not_deep = cl >= support_floor * (1 - MAX_UNDERCUT_PCT / 100.0)
            if not (support_touch and not_deep):
                continue

            # Volume contracts across the whole congestion area vs the 20-day baseline just before it.
            base_vol = float(avgvol20.iloc[cs - 1]) if cs - 1 >= 0 else np.nan
            cong_vol = float(cong['Volume'].mean())
            vol_ratio = cong_vol / base_vol if np.isfinite(base_vol) and base_vol > 0 else np.nan
            if not (np.isfinite(vol_ratio) and vol_ratio <= MAX_CONGESTION_AVG_VOL_RATIO):
                continue

            found = (n, cs, width_pct, slope_pct, cl, vol_ratio)
            break

        if found is None:
            continue

        n, cs, width_pct, slope_pct, congestion_low, vol_ratio = found

        # Final bar is the reclaim candle: bullish, strong close, and back above both supports.
        slight_undercut = lo < max(level, ema20) and lo >= min(level, ema20) * (1 - MAX_UNDERCUT_PCT / 100.0)
        reclaim = close > level and close > ema20
        bullish_reclaim = close > op and close >= (hi + lo) / 2.0
        if not (slight_undercut and reclaim and bullish_reclaim):
            continue

        stop = min(lo, congestion_low)
        risk = close - stop
        if risk <= 0:
            continue
        fib0382 = stop + ((1.0 - 0.382) / FIB_DEN) * risk
        target0 = stop + risk / FIB_DEN
        target_r = (target0 - close) / risk

        outcome = 'OPEN'
        exit_i = None
        hit0382 = False
        realized_r = np.nan
        for j in range(i + 1, min(len(d), i + 1 + FOLLOW_DAYS)):
            day_low = float(l.iloc[j]); day_high = float(h.iloc[j])
            if day_high >= fib0382:
                hit0382 = True
            hit_stop = day_low <= stop
            hit_target = day_high >= target0
            if hit_stop and hit_target:
                outcome = 'STOP_AMBIGUOUS'; exit_i = j; realized_r = -1.0; break
            if hit_stop:
                outcome = 'STOP'; exit_i = j; realized_r = -1.0; break
            if hit_target:
                outcome = 'TARGET0'; exit_i = j; realized_r = target_r; hit0382 = True; break

        days = exit_i - i if exit_i is not None else np.nan
        patt = candle_pattern(op, hi, lo, close, float(o.iloc[i-1]), float(c.iloc[i-1]))
        rows.append({
            'date': str(pd.Timestamp(d.index[i]).date()),
            'symbol': sym,
            'breakout_date': str(pd.Timestamp(d.index[b]).date()),
            'breakout_level': round(level, 4),
            'breakout_age_days': age,
            'post_breakout_peak': round(post_peak, 4),
            'post_breakout_push_pct': round(push_pct, 3),
            'ema20': round(ema20, 4),
            'ema20_breakout_cluster_pct': round(cluster_pct, 3),
            'congestion_bars': n,
            'congestion_start': str(pd.Timestamp(d.index[cs]).date()),
            'congestion_width_pct': round(width_pct, 3),
            'congestion_slope_pct': round(slope_pct, 3),
            'congestion_avg_vol_ratio': round(vol_ratio, 3),
            'candle_pattern': patt,
            'entry_price': round(close, 4),
            'stop': round(stop, 4),
            'risk_pct': round((risk / close) * 100.0, 3),
            'fib0382': round(fib0382, 4),
            'target0': round(target0, 4),
            'target_r': round(target_r, 3),
            'hit_fib0382': hit0382,
            'outcome': outcome,
            'days_to_exit': days,
            'realized_r': round(float(realized_r), 3) if np.isfinite(realized_r) else np.nan,
            'rs_vs_spy_pct': round(rs * 100.0, 3),
            'pct_below_52w_high': round(float(below_high), 3),
        })
    return rows


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    symbols = [x.strip().upper() for x in UNIVERSE.read_text().splitlines() if x.strip()]
    symbols = list(dict.fromkeys(symbols))
    data = download(symbols + [BENCHMARK])
    spy = data.get(BENCHMARK)
    if spy is None or spy.empty:
        raise RuntimeError('SPY unavailable')

    rows: list[dict] = []
    for n, sym in enumerate(symbols, 1):
        if n % 100 == 0:
            print('processed', n, '/', len(symbols))
        d = data.get(sym)
        if d is None or d.empty:
            continue
        try:
            rows.extend(evaluate_symbol(sym, d, spy))
        except Exception as exc:
            print('skip', sym, exc)

    out = pd.DataFrame(rows)
    out.to_csv(OUTDIR / 'sci_style_setups.csv', index=False)
    if out.empty:
        pd.DataFrame().to_csv(OUTDIR / 'summary.csv', index=False)
        print('No SCI-style setups found')
        return

    pd.DataFrame([summarize(out, 'SCI_STYLE', 'setup')]).to_csv(OUTDIR / 'summary.csv', index=False)

    by_bars = [summarize(g, str(k), 'congestion_bars') for k, g in out.groupby('congestion_bars')]
    pd.DataFrame(by_bars).sort_values('congestion_bars').to_csv(OUTDIR / 'summary_by_congestion_bars.csv', index=False)

    width_bins = pd.cut(out['congestion_width_pct'], bins=[0, 2, 3, 4, 5, 6, np.inf], right=True)
    by_width = [summarize(out[width_bins == k], str(k), 'width_bucket') for k in width_bins.dropna().unique()]
    pd.DataFrame(by_width).to_csv(OUTDIR / 'summary_by_width.csv', index=False)

    cluster_bins = pd.cut(out['ema20_breakout_cluster_pct'], bins=[-0.001, 0.25, 0.5, 0.75, 1.0, 1.5, np.inf], right=True)
    by_cluster = [summarize(out[cluster_bins == k], str(k), 'cluster_bucket') for k in cluster_bins.dropna().unique()]
    pd.DataFrame(by_cluster).to_csv(OUTDIR / 'summary_by_cluster.csv', index=False)

    by_candle = [summarize(g, str(k), 'candle_pattern') for k, g in out.groupby('candle_pattern')]
    pd.DataFrame(by_candle).sort_values('signals', ascending=False).to_csv(OUTDIR / 'summary_by_candle.csv', index=False)

    print(pd.DataFrame([summarize(out, 'SCI_STYLE', 'setup')]).to_string(index=False))
    print('\nBy congestion bars:')
    print(pd.DataFrame(by_bars).to_string(index=False))


if __name__ == '__main__':
    main()
