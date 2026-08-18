from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

from build_universes import build_tsx

# Exact defaults from Trend Pullback Stock Screener v1.1 Pine script.
EMA_FAST = 20
EMA_MID = 50
SMA_LONG = 200
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500_000
MIN_DOLLAR_VOL = 20_000_000.0
HIGH_LOOKBACK = 252
MAX_BELOW_HIGH = 20.0
RESISTANCE_BARS = 50
MIN_BREAKOUT_PCT = 1.0
MAX_RETEST_BARS = 30
MAX_UNDERCUT_PCT = 3.0
MAX_ABOVE_EMA20 = 12.0
RS_LOOKBACK = 63

MARKETS = {
    'us': {
        'tz': 'America/New_York',
        'outdir': Path('double_reclaim_results/us'),
        'universe': Path('data/us_1b_universe.txt'),
        'cap_min': 1_000_000_000,
        'cap_label': 'market_cap_usd',
        'benchmark': 'SPY',
        'benchmark_tz': 'America/New_York',
    },
    'hk': {
        'tz': 'Asia/Hong_Kong',
        'outdir': Path('double_reclaim_results/hk'),
        'universe': Path('data/hk_5b_universe.txt'),
        'cap_min': 5_000_000_000,
        'cap_label': 'market_cap_hkd',
        # Preserve the existing HK behaviour for now; Canada is the targeted fix.
        'benchmark': 'SPY',
        'benchmark_tz': 'America/New_York',
    },
    'canada': {
        'tz': 'America/Toronto',
        'outdir': Path('double_reclaim_results/canada'),
        'universe': None,
        'cap_min': 1_000_000_000,
        'cap_label': 'market_cap_cad',
        'benchmark': 'XIU.TO',
        'benchmark_tz': 'America/Toronto',
    },
}


def _is_common_tsx_symbol(symbol: str) -> bool:
    s = symbol.upper()
    return '-PR-' not in s and '-PF-' not in s


def _load_symbols(market: str) -> list[str]:
    cfg = MARKETS[market]
    if market == 'canada':
        syms = [s for s in build_tsx() if _is_common_tsx_symbol(s)]
    else:
        path: Path = cfg['universe']
        if not path.exists():
            raise RuntimeError(f'{path} not found')
        syms = [s.strip().upper() for s in path.read_text().splitlines() if s.strip()]
    return list(dict.fromkeys(syms))


def _split_download(raw: pd.DataFrame, symbols: list[str]) -> dict[str, pd.DataFrame]:
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


def _batch_download(symbols: list[str], *, period: str, interval: str, chunk: int) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), chunk):
        group = symbols[i:i + chunk]
        print(f'{interval} batch {i+1}-{min(i+chunk, len(symbols))}/{len(symbols)}')
        pending = list(group)
        for attempt in range(1, 3):
            if not pending:
                break
            try:
                raw = yf.download(
                    pending,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    prepost=False,
                    progress=False,
                    threads=True,
                    group_by='ticker',
                )
                got = _split_download(raw, pending)
                out.update(got)
                pending = [s for s in pending if s not in got]
                if pending:
                    print(f'{interval} retry pending {len(pending)} symbol(s) in this batch')
            except Exception as exc:
                print(f'{interval} batch attempt {attempt} failed:', exc)
            if attempt == 1 and pending:
                time.sleep(2)
        if pending:
            print(f'{interval} unavailable after retry: {len(pending)} symbol(s):', ', '.join(pending[:20]),
                  '...' if len(pending) > 20 else '')
        time.sleep(0.5)
    return out


def _single_download(symbol: str, *, period: str, interval: str, attempts: int = 4) -> pd.DataFrame:
    for attempt in range(1, attempts + 1):
        try:
            raw = yf.download(symbol, period=period, interval=interval, auto_adjust=True,
                              prepost=False, progress=False, threads=False)
            if raw is not None and not raw.empty:
                if isinstance(raw.columns, pd.MultiIndex):
                    try:
                        raw = raw.xs(symbol, axis=1, level=1, drop_level=True)
                    except Exception:
                        raw.columns = raw.columns.get_level_values(0)
                if 'Close' in raw.columns:
                    return raw.dropna(how='all')
        except Exception as exc:
            print(f'{symbol} attempt {attempt}/{attempts} failed:', exc)
        if attempt < attempts:
            time.sleep(2 * attempt)
    return pd.DataFrame()


def _completed_daily(df: pd.DataFrame, tz_name: str) -> pd.DataFrame:
    if df is None or df.empty or 'Close' not in df.columns:
        return pd.DataFrame()
    x = df.copy().dropna(subset=['Close'])
    if x.empty:
        return x
    today = datetime.now(ZoneInfo(tz_name)).date()
    if pd.DatetimeIndex(x.index).date[-1] == today:
        x = x.iloc[:-1]
    return x


def _today_bar(intr: pd.DataFrame) -> dict[str, float] | None:
    need = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if intr is None or intr.empty or not need.issubset(intr.columns):
        return None
    x = intr.dropna(subset=['Open', 'High', 'Low', 'Close'])
    if x.empty:
        return None
    vol = pd.to_numeric(x['Volume'], errors='coerce').fillna(0)
    return {
        'open': float(x['Open'].iloc[0]),
        'high': float(pd.to_numeric(x['High'], errors='coerce').max()),
        'low': float(pd.to_numeric(x['Low'], errors='coerce').min()),
        'close': float(x['Close'].iloc[-1]),
        'volume': float(vol.sum()),
    }


def _append_current(d: pd.DataFrame, bar: dict[str, float]) -> pd.DataFrame:
    row = pd.DataFrame([{
        'Open': bar['open'], 'High': bar['high'], 'Low': bar['low'],
        'Close': bar['close'], 'Volume': bar['volume'],
    }])
    cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    hist = d.copy()
    for c in cols:
        hist[c] = pd.to_numeric(hist[c], errors='coerce')
    return pd.concat([hist[cols].reset_index(drop=True), row], ignore_index=True)


def _latest_valid_breakout(completed: pd.DataFrame) -> tuple[int, float, int] | None:
    if len(completed) < RESISTANCE_BARS + MAX_RETEST_BARS + 5:
        return None
    h = pd.to_numeric(completed['High'], errors='coerce')
    c = pd.to_numeric(completed['Close'], errors='coerce')
    resistance = h.shift(1).rolling(RESISTANCE_BARS).max()
    breakout = (c > resistance * (1 + MIN_BREAKOUT_PCT / 100.0)) & (c.shift(1) <= resistance)
    hits = np.flatnonzero(breakout.fillna(False).to_numpy())
    if not len(hits):
        return None
    pos = int(hits[-1])
    # Pine is evaluated on today's current bar, so barsSinceBreakout counts today as one bar.
    age_today = len(completed) - pos
    if age_today < 1 or age_today > MAX_RETEST_BARS:
        return None
    level = float(resistance.iloc[pos])
    if not np.isfinite(level) or level <= 0:
        return None
    return pos, level, age_today


def _ema(series: pd.Series, span: int) -> float:
    return float(pd.to_numeric(series, errors='coerce').ewm(span=span, adjust=False).mean().iloc[-1])


def _market_cap(symbol: str) -> float:
    for attempt in range(1, 3):
        try:
            value = yf.Ticker(symbol).fast_info.market_cap
            return float(value) if value is not None else np.nan
        except Exception as exc:
            print('market cap failed', symbol, exc)
            if attempt == 1:
                time.sleep(1.5)
    return np.nan


def _benchmark_state(market: str) -> dict[str, float | bool | str]:
    cfg = MARKETS[market]
    symbol = str(cfg['benchmark'])
    benchmark_tz = str(cfg['benchmark_tz'])
    daily_raw = _single_download(symbol, period='18mo', interval='1d')
    completed = _completed_daily(daily_raw, benchmark_tz)
    intr = _single_download(symbol, period='1d', interval='5m')
    bar = _today_bar(intr)
    if len(completed) < 220 or bar is None:
        raise RuntimeError(f'{symbol} benchmark data unavailable')
    full = _append_current(completed, bar)
    close = float(full['Close'].iloc[-1])
    ema20 = _ema(full['Close'], EMA_FAST)
    ema50 = _ema(full['Close'], EMA_MID)
    # Pine close[63] from current bar -> completed daily close 63 bars back from today.
    prior = float(completed['Close'].iloc[-RS_LOOKBACK])
    ret = close / prior - 1.0
    healthy = close > ema20 and ema20 > ema50
    return {'symbol': symbol, 'close': close, 'ema20': ema20, 'ema50': ema50,
            'return': ret, 'healthy': healthy}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--market', choices=sorted(MARKETS), required=True)
    args = ap.parse_args()
    market = args.market
    cfg = MARKETS[market]
    outdir: Path = cfg['outdir']
    outdir.mkdir(parents=True, exist_ok=True)

    symbols = _load_symbols(market)
    print(market, 'universe', len(symbols))
    benchmark = _benchmark_state(market)
    print(benchmark['symbol'], 'marketHealthy =', benchmark['healthy'])

    daily = _batch_download(symbols, period='18mo', interval='1d', chunk=120 if market == 'canada' else 180)
    if market == 'canada':
        missing_daily = [s for s in symbols if s not in daily]
        print('Canada daily data loaded for', len(daily), 'of', len(symbols), 'symbols; unavailable', len(missing_daily))

    # Pre-shortlist only by the Pine condition that cannot be rescued by today's bar:
    # a prior breakout whose age on today's bar is 1..30.
    prelim: list[dict] = []
    for sym in symbols:
        d0 = daily.get(sym)
        if d0 is None or d0.empty:
            continue
        d = _completed_daily(d0, cfg['tz'])
        if len(d) < 260:
            continue
        bo = _latest_valid_breakout(d)
        if bo is None:
            continue
        _, level, age = bo
        prelim.append({'symbol': sym, 'breakout_level': level, 'breakout_age_days': age, '_daily': d})

    print('Recent-breakout shortlist', len(prelim))
    intra = _batch_download([x['symbol'] for x in prelim], period='1d', interval='5m', chunk=60 if market == 'canada' else 80)

    rows: list[dict] = []
    for x in prelim:
        sym = x['symbol']
        bar = _today_bar(intra.get(sym, pd.DataFrame()))
        if bar is None:
            continue
        d: pd.DataFrame = x['_daily']
        full = _append_current(d, bar)
        close = bar['close']
        level = float(x['breakout_level'])

        ema20 = _ema(full['Close'], EMA_FAST)
        ema50 = _ema(full['Close'], EMA_MID)
        sma200 = float(pd.to_numeric(full['Close'], errors='coerce').rolling(SMA_LONG).mean().iloc[-1])
        ema50_10 = float(pd.to_numeric(full['Close'], errors='coerce').ewm(span=EMA_MID, adjust=False).mean().iloc[-11])
        sma200_series = pd.to_numeric(full['Close'], errors='coerce').rolling(SMA_LONG).mean()
        sma200_20 = float(sma200_series.iloc[-21])

        trend_alignment = close > ema20 and ema20 > ema50 and ema50 > sma200
        ema50_rising = ema50 > ema50_10
        sma200_rising = sma200 > sma200_20
        strong_uptrend = trend_alignment and ema50_rising and sma200_rising

        distance_above_ema20 = ((close / ema20) - 1.0) * 100.0 if ema20 > 0 else np.nan
        not_overextended = bool(np.isfinite(distance_above_ema20) and distance_above_ema20 <= MAX_ABOVE_EMA20)

        avg_volume = float(pd.to_numeric(full['Volume'], errors='coerce').rolling(20).mean().iloc[-1])
        avg_dollar_vol = float((pd.to_numeric(full['Close'], errors='coerce') * pd.to_numeric(full['Volume'], errors='coerce')).rolling(20).mean().iloc[-1])
        liquid_stock = close >= MIN_PRICE and avg_volume >= MIN_AVG_VOLUME and avg_dollar_vol >= MIN_DOLLAR_VOL

        year_high = float(pd.to_numeric(full['High'], errors='coerce').rolling(HIGH_LOOKBACK).max().iloc[-1])
        pct_below_high = ((year_high - close) / year_high) * 100.0 if year_high > 0 else np.nan
        near_year_high = bool(np.isfinite(pct_below_high) and pct_below_high <= MAX_BELOW_HIGH)

        prior_close_63 = float(d['Close'].iloc[-RS_LOOKBACK])
        stock_return = close / prior_close_63 - 1.0
        relative_strength = stock_return - float(benchmark['return'])
        outperforming_benchmark = relative_strength > 0
        market_pass = bool(benchmark['healthy'])

        lowest_allowed = level * (1.0 - MAX_UNDERCUT_PCT / 100.0)
        slight_undercut = bar['low'] < level and bar['low'] >= lowest_allowed
        reclaimed_level = close > level
        bullish_reclaim_candle = close > bar['open'] and close >= (bar['high'] + bar['low']) / 2.0
        candle_range = bar['high'] - bar['low']
        strong_bearish_momentum = candle_range > 0 and close < bar['open'] and (bar['open'] - close) / candle_range >= 0.65
        reclaim_trigger = bool(slight_undercut and reclaimed_level and bullish_reclaim_candle and not strong_bearish_momentum)

        entry_candidate = bool(
            strong_uptrend and not_overextended and liquid_stock and near_year_high and
            outperforming_benchmark and market_pass and reclaim_trigger
        )
        if not entry_candidate:
            continue

        cap = np.nan
        if market == 'canada':
            cap = _market_cap(sym)
            if pd.isna(cap) or cap < cfg['cap_min']:
                continue
            time.sleep(0.2)

        rows.append({
            'symbol': sym,
            'marker': 'ENTRY',
            'blue_marker': True,
            'candle': 'BULL',
            'current_price': round(close, 4),
            'day_open': round(bar['open'], 4),
            'day_high': round(bar['high'], 4),
            'day_low': round(bar['low'], 4),
            'day_volume': round(bar['volume'], 0),
            'breakout_level': round(level, 4),
            'breakout_age_days': int(x['breakout_age_days']),
            'ema20_live': round(ema20, 4),
            'ema50_live': round(ema50, 4),
            'sma200_live': round(sma200, 4),
            'distance_above_ema20_pct': round(distance_above_ema20, 3),
            'avg_volume_20': round(avg_volume, 0),
            'avg_dollar_volume_20': round(avg_dollar_vol, 0),
            'pct_below_52w_high': round(pct_below_high, 3),
            'benchmark_symbol': benchmark['symbol'],
            'rs_vs_benchmark_pct': round(relative_strength * 100.0, 3),
            # Compatibility columns retained for downstream readers; values are benchmark-dependent.
            'rs_vs_spy_pct': round(relative_strength * 100.0, 3),
            'market_pass': market_pass,
            'strong_uptrend': strong_uptrend,
            'not_overextended': not_overextended,
            'liquid_stock': liquid_stock,
            'near_year_high': near_year_high,
            'outperforming_benchmark': outperforming_benchmark,
            'outperforming_spy': outperforming_benchmark,
            'slight_undercut': slight_undercut,
            'reclaimed_level': reclaimed_level,
            'bullish_reclaim_candle': bullish_reclaim_candle,
            cfg['cap_label']: round(float(cap), 0) if pd.notna(cap) else np.nan,
        })

    out = pd.DataFrame(rows)
    pine_path = outdir / f'{market}_pine_entry_today.csv'
    blue_path = outdir / f'{market}_blue_marker_today.csv'
    out.to_csv(pine_path, index=False)
    # Blue marker now means the TradingView Reclaim Entry marker, not generic reclaim-breakout.
    out.to_csv(blue_path, index=False)
    print(f'Exact Pine ENTRY candidates: {len(out)} -> {pine_path}')


if __name__ == '__main__':
    main()
