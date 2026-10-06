from __future__ import annotations

import argparse
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


MARKETS = {
    "us": {
        "label": "US",
        "universe": "data/us_1b_universe.txt",
        "benchmark": "SPY",
        "batch": 60,
    },
    "tsx": {
        "label": "TSX",
        "universe": "data/tsx_universe.txt",
        "benchmark": "XIU.TO",
        "batch": 45,
    },
    "hk": {
        "label": "HK",
        "universe": "data/hk_5b_universe.txt",
        "benchmark": "2800.HK",
        "batch": 40,
    },
}


@dataclass
class Params:
    lookback: int = 50
    rs_lookback: int = 63
    max_to_breakout_pct: float = 5.0
    max_below_52w_high_pct: float = 15.0
    min_rs_pct: float = 5.0
    max_above_ema20_pct: float = 8.0
    a_grade_max_above_ema20_pct: float = 6.0
    fast_breakout_days: int = 3
    extended_breakout_days: int = 10
    outcome_days: int = 20


def s(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").astype(float)


def flatten(d):
    if d is None or d.empty:
        return d
    d = d.copy()
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    return d


def normalize_frame(d):
    d = flatten(d)
    need = ["Open", "High", "Low", "Close", "Volume"]
    if d is None or any(c not in d.columns for c in need):
        return None
    d = d.dropna(subset=need).copy()
    d.index = pd.to_datetime(d.index).tz_localize(None).normalize()
    return d if len(d) >= 220 else None


def load_symbols(path: str):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return list(
        dict.fromkeys(
            x.strip().upper()
            for x in p.read_text().splitlines()
            if x.strip() and not x.startswith("#")
        )
    )


def dl_single(symbol: str, start: str, end: str, attempts: int = 5):
    for a in range(attempts):
        try:
            d = yf.download(
                symbol,
                start=start,
                end=end,
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            d = normalize_frame(d)
            if d is not None:
                return d
        except Exception as e:
            print("single download failed", symbol, a + 1, e)
        if a + 1 < attempts:
            time.sleep(min(3 * (2 ** a), 25) + random.uniform(0.2, 0.8))
    return None


def dl_batch(symbols, start: str, end: str, attempts: int = 3):
    for a in range(attempts):
        try:
            d = yf.download(
                symbols,
                start=start,
                end=end,
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            if d is not None and not d.empty:
                return d
        except Exception as e:
            print("batch download failed", a + 1, e)
        if a + 1 < attempts:
            time.sleep(min(4 * (2 ** a), 25) + random.uniform(0.5, 1.5))
    return None


def batch_frame(data, symbol: str, single: bool):
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    return normalize_frame(d)


def benchmark_returns(bench: pd.DataFrame, lookback: int):
    c = s(bench["Close"])
    return c / c.shift(lookback) - 1.0


def add_indicators(df: pd.DataFrame):
    out = df.copy()
    c, h, l, v = map(s, [out.Close, out.High, out.Low, out.Volume])
    out["EMA20"] = c.ewm(span=20, adjust=False).mean()
    out["EMA50"] = c.ewm(span=50, adjust=False).mean()
    out["SMA200"] = c.rolling(200).mean()
    out["PRIOR_HIGH"] = h.shift(1).rolling(50).max()
    out["HIGH52"] = h.rolling(252, min_periods=150).max()
    out["AVG_VOL20"] = v.rolling(20).mean()
    out["AVG_VOL10"] = v.rolling(10).mean()
    out["VOL20_PRIOR"] = v.shift(1).rolling(20).mean()
    out["RANGE20"] = h.rolling(20).max() / l.rolling(20).min() - 1.0
    out["RANGE10"] = h.rolling(10).max() / l.rolling(10).min() - 1.0
    return out


def compression_score(dist, below, above20, rs, volume_contract, range_contract):
    score = 0
    score += 3 if dist <= 1 else (2 if dist <= 2 else (1 if dist <= 3 else 0))
    score += 2 if below <= 5 else (1 if below <= 10 else 0)
    score += 2 if above20 <= 2 else (1 if above20 <= 4 else 0)
    score += 1 if rs >= 5 else 0
    score += 1 if rs >= 10 else 0
    score += 1 if volume_contract else 0
    score += 1 if range_contract else 0
    return score


def pre_entry_metrics(x: pd.DataFrame, i: int, bench_ret: pd.Series, p: Params):
    if i < 252 or i <= p.rs_lookback:
        return None

    c, h, l, v = map(s, [x.Close, x.High, x.Low, x.Volume])
    e20, e50, s200 = map(s, [x.EMA20, x.EMA50, x.SMA200])
    resistance = float(x.PRIOR_HIGH.iloc[i])
    high52 = float(x.HIGH52.iloc[i])
    px = float(c.iloc[i])

    vals = [px, e20.iloc[i], e50.iloc[i], s200.iloc[i], resistance, high52]
    if not all(np.isfinite(z) for z in vals) or resistance <= 0 or high52 <= 0:
        return None

    strong = (
        px > e20.iloc[i] > e50.iloc[i] > s200.iloc[i]
        and e50.iloc[i] > e50.iloc[i - 10]
        and s200.iloc[i] > s200.iloc[i - 20]
    )
    if not strong:
        return None

    dist = (resistance - px) / resistance * 100.0
    if dist < 0 or dist > p.max_to_breakout_pct:
        return None

    below = (high52 - px) / high52 * 100.0
    if below > p.max_below_52w_high_pct:
        return None

    stock_ret = px / float(c.iloc[i - p.rs_lookback]) - 1.0
    br = bench_ret.reindex([x.index[i]], method="ffill").iloc[0]
    if not np.isfinite(br):
        return None
    rs = (stock_ret - float(br)) * 100.0
    if rs < p.min_rs_pct:
        return None

    above20 = (px / float(e20.iloc[i]) - 1.0) * 100.0
    if above20 < 0 or above20 > p.max_above_ema20_pct:
        return None

    av20 = float(x.AVG_VOL20.iloc[i])
    av10 = float(x.AVG_VOL10.iloc[i])
    volume_contract = bool(np.isfinite(av20) and av20 > 0 and av10 <= av20 * 0.90)

    r20 = float(x.RANGE20.iloc[i])
    r10 = float(x.RANGE10.iloc[i])
    range_contract = bool(np.isfinite(r20) and r20 > 0 and r10 <= r20 * 0.75)

    score = 0
    score += 3 if dist <= 1 else (2 if dist <= 2.5 else 1)
    score += 2 if rs >= 15 else (1 if rs >= 10 else 0)
    score += 2 if below <= 5 else (1 if below <= 10 else 0)
    score += 1 if volume_contract else 0
    score += 1 if range_contract else 0
    score += 2 if above20 <= 4 else (1 if above20 <= 6 else 0)
    grade = "A" if score >= 8 and above20 <= p.a_grade_max_above_ema20_pct else ("B" if score >= 6 else "C")

    cscore = compression_score(dist, below, above20, rs, volume_contract, range_contract)
    compression = bool(
        dist <= 2.0
        and below <= 10.0
        and above20 <= 4.0
        and rs >= p.min_rs_pct
        and cscore >= 7
    )

    fast_quality = bool(
        score >= 8
        and dist <= 2.0
        and below <= 5.0
        and above20 <= 4.0
        and rs >= 10.0
    )

    return {
        "setup_close": px,
        "breakout_level": resistance,
        "distance_to_breakout_pct": dist,
        "ema20": float(e20.iloc[i]),
        "ema50": float(e50.iloc[i]),
        "sma200": float(s200.iloc[i]),
        "pct_above_ema20": above20,
        "rs_pct": rs,
        "pct_below_52w_high": below,
        "volume_contracting": volume_contract,
        "range_contracting": range_contract,
        "score": score,
        "grade": grade,
        "compression_score": cscore,
        "compression_setup": compression,
        "fast_quality": fast_quality,
    }


def breakout_index(x: pd.DataFrame, setup_i: int, level: float, max_days: int):
    c = s(x.Close)
    end = min(len(x) - 1, setup_i + max_days)
    for j in range(setup_i, end + 1):
        if float(c.iloc[j]) > level:
            return j
    return None


def breakout_trigger_metrics(x: pd.DataFrame, breakout_i: int):
    bar = x.iloc[breakout_i]
    prior_vol = float(x["VOL20_PRIOR"].iloc[breakout_i]) if "VOL20_PRIOR" in x.columns else np.nan
    vol = float(bar.Volume)
    ratio = vol / prior_vol if np.isfinite(prior_vol) and prior_vol > 0 else np.nan
    rng = float(bar.High) - float(bar.Low)
    close_pos = (float(bar.Close) - float(bar.Low)) / rng if rng > 0 else np.nan
    body = abs(float(bar.Close) - float(bar.Open)) / rng if rng > 0 else np.nan
    return {
        "breakout_volume_ratio": ratio,
        "breakout_volume_expansion_1_2x": bool(np.isfinite(ratio) and ratio >= 1.20),
        "breakout_volume_expansion_1_5x": bool(np.isfinite(ratio) and ratio >= 1.50),
        "breakout_close_position": close_pos,
        "breakout_body_fraction": body,
        "breakout_bullish_bar": bool(float(bar.Close) > float(bar.Open)),
    }


def outcome_metrics(x: pd.DataFrame, breakout_i: int, level: float, p: Params):
    entry_i = breakout_i + 1
    if entry_i >= len(x):
        return None

    entry = float(x.Open.iloc[entry_i])
    breakout_low = float(x.Low.iloc[breakout_i])
    stop = min(level, breakout_low)
    if not np.isfinite(entry) or not np.isfinite(stop) or entry <= stop:
        return None

    risk = entry - stop
    end = min(len(x), entry_i + p.outcome_days)
    future = x.iloc[entry_i:end]
    if future.empty:
        return None

    highs = s(future.High)
    lows = s(future.Low)
    closes = s(future.Close)
    mfe_pct = (float(highs.max()) / entry - 1.0) * 100.0
    mae_pct = (float(lows.min()) / entry - 1.0) * 100.0
    mfe_r = (float(highs.max()) - entry) / risk
    mae_r = (float(lows.min()) - entry) / risk

    first_hit = {}
    targets = {"1R": entry + risk, "2R": entry + 2 * risk, "2.5R": entry + 2.5 * risk, "3R": entry + 3 * risk}
    stopped = False
    stop_day = None
    for k, (_, bar) in enumerate(future.iterrows()):
        lo, hi = float(bar.Low), float(bar.High)
        if lo <= stop:
            stopped = True
            stop_day = k
            for name, target in targets.items():
                if name not in first_hit and hi >= target:
                    first_hit[name] = "AMBIGUOUS_SAME_DAY"
            break
        for name, target in targets.items():
            if name not in first_hit and hi >= target:
                first_hit[name] = k

    def close_ret(n):
        if len(closes) < n:
            return np.nan
        return (float(closes.iloc[n - 1]) / entry - 1.0) * 100.0

    one_day = s(x.Close.iloc[max(0, breakout_i - 5):end]).pct_change().abs()
    suspicious_single_day_move = bool((one_day > 0.75).any()) if len(one_day) else False

    return {
        **breakout_trigger_metrics(x, breakout_i),
        "entry_date": str(x.index[entry_i].date()),
        "entry": entry,
        "stop": stop,
        "risk_pct": (risk / entry) * 100.0,
        "gap_vs_breakout_pct": (entry / level - 1.0) * 100.0,
        "gap_under_2pct": bool((entry / level - 1.0) * 100.0 <= 2.0),
        "stopped_within_20d": stopped,
        "stop_day": stop_day if stop_day is not None else np.nan,
        "hit_1r_before_stop": isinstance(first_hit.get("1R"), int),
        "hit_2r_before_stop": isinstance(first_hit.get("2R"), int),
        "hit_2_5r_before_stop": isinstance(first_hit.get("2.5R"), int),
        "hit_3r_before_stop": isinstance(first_hit.get("3R"), int),
        "hit_10pct": bool(mfe_pct >= 10.0),
        "mfe_20d_pct": mfe_pct,
        "mae_20d_pct": mae_pct,
        "mfe_20d_r": mfe_r,
        "mae_20d_r": mae_r,
        "close_return_5d_pct": close_ret(5),
        "close_return_10d_pct": close_ret(10),
        "close_return_20d_pct": close_ret(20),
        "suspicious_single_day_move": suspicious_single_day_move,
        "extreme_mfe_over_150pct": bool(mfe_pct > 150.0),
    }


def find_episodes(symbol: str, df: pd.DataFrame, bench_ret: pd.Series, cfg: dict, p: Params, analysis_start: pd.Timestamp):
    x = add_indicators(df)
    rows = []
    prev_candidate = False
    cooldown_until = -1

    for i in range(252, len(x)):
        if x.index[i] < analysis_start:
            continue

        metrics = pre_entry_metrics(x, i, bench_ret, p)
        is_candidate = metrics is not None

        # Count the first day of a PRE_ENTRY episode only. This mirrors the
        # historical "first seen" observation and prevents one setup from being
        # counted repeatedly on consecutive days.
        if is_candidate and not prev_candidate and i > cooldown_until:
            level = metrics["breakout_level"]
            b3 = breakout_index(x, i, level, p.fast_breakout_days)
            b10 = breakout_index(x, i, level, p.extended_breakout_days)
            b = b3 if b3 is not None else b10

            row = {
                "market": cfg["label"],
                "symbol": symbol,
                "setup_date": str(x.index[i].date()),
                **metrics,
                "breakout_within_3d": b3 is not None,
                "breakout_within_10d": b10 is not None,
                "breakout_date": str(x.index[b].date()) if b is not None else "",
                "bars_to_breakout": (b - i) if b is not None else np.nan,
                "breakout_close": float(x.Close.iloc[b]) if b is not None else np.nan,
            }
            if b3 is not None:
                out = outcome_metrics(x, b3, level, p)
                if out:
                    row.update(out)
            rows.append(row)
            cooldown_until = (b if b is not None else i + p.extended_breakout_days) + 5

        prev_candidate = is_candidate

    return rows


def live_signal(symbol: str, df: pd.DataFrame, bench_ret: pd.Series, cfg: dict, p: Params):
    x = add_indicators(df)
    if len(x) < 253:
        return None
    i = len(x) - 1
    metrics = pre_entry_metrics(x, i, bench_ret, p)
    if metrics is not None:
        state = "FAST_PRE_ENTRY" if metrics["fast_quality"] else ("COMPRESSION_PRE_ENTRY" if metrics["compression_setup"] else "PRE_ENTRY")
        return {
            "market": cfg["label"],
            "symbol": symbol,
            "state": state,
            "date": str(x.index[i].date()),
            **metrics,
        }

    # Also flag a breakout today if a qualifying PRE_ENTRY existed in the prior
    # three bars. This is the direct-momentum trigger.
    c = s(x.Close)
    for back in range(1, p.fast_breakout_days + 1):
        j = i - back
        if j < 252:
            continue
        m = pre_entry_metrics(x, j, bench_ret, p)
        if m and float(c.iloc[i]) > m["breakout_level"]:
            return {
                "market": cfg["label"],
                "symbol": symbol,
                "state": "DIRECT_BREAKOUT",
                "date": str(x.index[i].date()),
                "setup_date": str(x.index[j].date()),
                "bars_to_breakout": i - j,
                **m,
                "breakout_close": float(c.iloc[i]),
                **breakout_trigger_metrics(x, i),
            }
    return None


def variant_summary(df: pd.DataFrame, name: str, mask: pd.Series):
    g = df[mask].copy()
    trades = g[g.breakout_within_3d == True].copy()
    return {
        "variant": name,
        "setups": len(g),
        "breakouts_within_3d": len(trades),
        "breakout_rate_pct": round(100.0 * len(trades) / len(g), 2) if len(g) else np.nan,
        "hit_10pct_pct": round(100.0 * pd.to_numeric(trades.get("hit_10pct"), errors="coerce").mean(), 2) if len(trades) else np.nan,
        "hit_2_5r_before_stop_pct": round(100.0 * pd.to_numeric(trades.get("hit_2_5r_before_stop"), errors="coerce").mean(), 2) if len(trades) else np.nan,
        "median_mfe_20d_pct": round(pd.to_numeric(trades.get("mfe_20d_pct"), errors="coerce").median(), 2) if len(trades) else np.nan,
        "median_mae_20d_pct": round(pd.to_numeric(trades.get("mae_20d_pct"), errors="coerce").median(), 2) if len(trades) else np.nan,
        "avg_close_return_20d_pct": round(pd.to_numeric(trades.get("close_return_20d_pct"), errors="coerce").mean(), 2) if len(trades) else np.nan,
        "median_bars_to_breakout": round(pd.to_numeric(trades.get("bars_to_breakout"), errors="coerce").median(), 2) if len(trades) else np.nan,
        "vol_1_2x_pct": round(100.0 * pd.to_numeric(trades.get("breakout_volume_expansion_1_2x"), errors="coerce").mean(), 2) if len(trades) else np.nan,
        "vol_1_5x_pct": round(100.0 * pd.to_numeric(trades.get("breakout_volume_expansion_1_5x"), errors="coerce").mean(), 2) if len(trades) else np.nan,
    }


def run_market(key: str, start: str, end: str, analysis_start: pd.Timestamp, outdir: Path, p: Params, mode: str, max_symbols: int):
    cfg = MARKETS[key]
    syms = load_symbols(cfg["universe"])
    if max_symbols > 0:
        syms = syms[:max_symbols]
    print("===", cfg["label"], len(syms), "symbols ===")

    bench = dl_single(cfg["benchmark"], start, end)
    if bench is None:
        raise RuntimeError(f"benchmark unavailable: {cfg['benchmark']}")
    br = benchmark_returns(bench, p.rs_lookback)

    rows, live, failed = [], [], []
    for st in range(0, len(syms), cfg["batch"]):
        batch = syms[st:st + cfg["batch"]]
        print(cfg["label"], st + 1, "to", min(st + len(batch), len(syms)))
        raw = dl_batch(batch, start, end)
        if raw is None:
            failed.extend(batch)
            continue
        single = len(batch) == 1
        for sym in batch:
            d = batch_frame(raw, sym, single)
            if d is None:
                failed.append(sym)
                continue
            try:
                if mode in ("backtest", "both"):
                    rows.extend(find_episodes(sym, d, br, cfg, p, analysis_start))
                if mode in ("live", "both"):
                    z = live_signal(sym, d, br, cfg, p)
                    if z:
                        live.append(z)
            except Exception as e:
                print("skip", sym, e)
        time.sleep(random.uniform(0.4, 0.9))

    outdir.mkdir(parents=True, exist_ok=True)
    episodes = pd.DataFrame(rows)
    if not episodes.empty:
        episodes = episodes.sort_values(["breakout_within_3d", "fast_quality", "score", "rs_pct"], ascending=[False, False, False, False])
    episodes.to_csv(outdir / f"{key}_episodes.csv", index=False)

    live_df = pd.DataFrame(live)
    if not live_df.empty:
        rank = {"DIRECT_BREAKOUT": 0, "FAST_PRE_ENTRY": 1, "COMPRESSION_PRE_ENTRY": 2, "PRE_ENTRY": 3}
        live_df["_rank"] = live_df.state.map(rank).fillna(9)
        live_df = live_df.sort_values(["_rank", "score", "rs_pct"], ascending=[True, False, False]).drop(columns="_rank")
    live_df.to_csv(outdir / f"{key}_live.csv", index=False)
    pd.DataFrame({"symbol": list(dict.fromkeys(failed))}).to_csv(outdir / f"{key}_failed.csv", index=False)
    return episodes, live_df


def main():
    ap = argparse.ArgumentParser(description="Direct Breakout Momentum scanner/backtest")
    ap.add_argument("--markets", default="us,tsx,hk")
    ap.add_argument("--start", default=None, help="analysis start YYYY-MM-DD; default 2 years")
    ap.add_argument("--end", default=None, help="end YYYY-MM-DD; default latest")
    ap.add_argument("--mode", choices=["backtest", "live", "both"], default="both")
    ap.add_argument("--outdir", default="direct_breakout_momentum_results")
    ap.add_argument("--max-symbols", type=int, default=0)
    a = ap.parse_args()

    end_ts = pd.Timestamp(a.end) if a.end else pd.Timestamp.utcnow().tz_localize(None).normalize() + pd.Timedelta(days=1)
    analysis_start = pd.Timestamp(a.start) if a.start else end_ts - pd.Timedelta(days=730)
    download_start = analysis_start - pd.Timedelta(days=450)
    start = download_start.strftime("%Y-%m-%d")
    end = end_ts.strftime("%Y-%m-%d")

    p = Params()
    outdir = Path(a.outdir)
    all_episodes, all_live = [], []

    for key in [x.strip() for x in a.markets.split(",") if x.strip()]:
        ep, lv = run_market(key, start, end, analysis_start, outdir, p, a.mode, a.max_symbols)
        if not ep.empty:
            all_episodes.append(ep)
        if not lv.empty:
            all_live.append(lv)

    combined = pd.concat(all_episodes, ignore_index=True) if all_episodes else pd.DataFrame()
    live = pd.concat(all_live, ignore_index=True) if all_live else pd.DataFrame()
    combined.to_csv(outdir / "all_markets_episodes.csv", index=False)
    live.to_csv(outdir / "all_markets_live.csv", index=False)

    summary_rows = []
    if not combined.empty:
        variants = [
            ("CORE_PRE_ENTRY", pd.Series(True, index=combined.index)),
            ("GRADE_A", combined.grade == "A"),
            ("SCORE_8_PLUS", combined.score >= 8),
            ("COMPRESSION", combined.compression_setup == True),
            ("RS_10_PLUS", combined.rs_pct >= 10),
            ("RS_15_PLUS", combined.rs_pct >= 15),
            ("DIST_2PCT_OR_LESS", combined.distance_to_breakout_pct <= 2),
            ("WITHIN_5PCT_52W_HIGH", combined.pct_below_52w_high <= 5),
            ("FAST_HIGH_QUALITY", combined.fast_quality == True),
            (
                "A_PLUS_COMPRESSION",
                (combined.grade == "A") & (combined.compression_setup == True),
            ),
            (
                "BREAKOUT_VOL_1_2X",
                combined.breakout_volume_expansion_1_2x == True,
            ),
            (
                "BREAKOUT_VOL_1_5X",
                combined.breakout_volume_expansion_1_5x == True,
            ),
            (
                "A_COMP_RS15",
                (combined.grade == "A")
                & (combined.compression_setup == True)
                & (combined.rs_pct >= 15),
            ),
            (
                "A_COMP_RS15_VOL1_2X",
                (combined.grade == "A")
                & (combined.compression_setup == True)
                & (combined.rs_pct >= 15)
                & (combined.breakout_volume_expansion_1_2x == True),
            ),
            (
                "A_COMP_RS15_VOL1_5X",
                (combined.grade == "A")
                & (combined.compression_setup == True)
                & (combined.rs_pct >= 15)
                & (combined.breakout_volume_expansion_1_5x == True),
            ),
            (
                "A_COMP_RS15_VOL1_2X_GAP2",
                (combined.grade == "A")
                & (combined.compression_setup == True)
                & (combined.rs_pct >= 15)
                & (combined.breakout_volume_expansion_1_2x == True)
                & (combined.gap_under_2pct == True),
            ),
            (
                "CLEAN_A_COMP_RS15_VOL1_2X_GAP2",
                (combined.grade == "A")
                & (combined.compression_setup == True)
                & (combined.rs_pct >= 15)
                & (combined.breakout_volume_expansion_1_2x == True)
                & (combined.gap_under_2pct == True)
                & (combined.suspicious_single_day_move == False)
                & (combined.extreme_mfe_over_150pct == False),
            ),
        ]
        for name, mask in variants:
            summary_rows.append(variant_summary(combined, name, mask))

        for market, g in combined.groupby("market"):
            summary_rows.append(variant_summary(g, f"CORE_{market}", pd.Series(True, index=g.index)))
            summary_rows.append(variant_summary(g, f"FAST_{market}", g.fast_quality == True))

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(outdir / "variant_summary.csv", index=False)

    trades = combined[combined.breakout_within_3d == True].copy() if not combined.empty else pd.DataFrame()
    if not trades.empty:
        trades = trades.sort_values(["mfe_20d_pct", "score", "rs_pct"], ascending=[False, False, False])
    trades.head(300).to_csv(outdir / "top_direct_breakouts.csv", index=False)

    clean_trades = trades.copy()
    if not clean_trades.empty:
        clean_trades = clean_trades[
            (clean_trades.suspicious_single_day_move == False)
            & (clean_trades.extreme_mfe_over_150pct == False)
            & (pd.to_numeric(clean_trades.risk_pct, errors="coerce") <= 20)
        ].copy()
        clean_trades = clean_trades.sort_values(
            ["mfe_20d_pct", "score", "rs_pct"], ascending=[False, False, False]
        )
    clean_trades.head(300).to_csv(outdir / "clean_top_direct_breakouts.csv", index=False)

    print("\n=== DIRECT BREAKOUT MOMENTUM SUMMARY ===")
    print(summary.to_string(index=False) if not summary.empty else "(no setups)")
    if not trades.empty:
        cols = [
            "market", "symbol", "setup_date", "breakout_date", "bars_to_breakout",
            "grade", "score", "compression_setup", "fast_quality",
            "distance_to_breakout_pct", "rs_pct", "pct_below_52w_high",
            "breakout_volume_ratio", "breakout_volume_expansion_1_2x",
            "gap_vs_breakout_pct", "mfe_20d_pct", "mae_20d_pct", "hit_2_5r_before_stop",
            "close_return_20d_pct",
        ]
        print("\n=== TOP DIRECT BREAKOUTS ===")
        print(trades[cols].head(50).to_string(index=False))
    if not live.empty:
        print("\n=== LIVE DIRECT MOMENTUM WATCH ===")
        print(live.head(60).to_string(index=False))


if __name__ == "__main__":
    main()
