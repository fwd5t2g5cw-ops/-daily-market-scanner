from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def s(x):
    if isinstance(x, pd.DataFrame):
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").astype(float)


def load_symbols(path: str, limit: int | None = None) -> list[str]:
    xs = [x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith("#")]
    xs = list(dict.fromkeys(xs))
    return xs[:limit] if limit else xs


@dataclass
class Variant:
    name: str
    ema_fib_dist_pct: float
    min_impulse_pct: float
    max_below_52w_high_pct: float
    max_pullback_below_236_pct: float


VARIANTS = [
    Variant("A_tight", 0.35, 15.0, 3.0, 0.25),
    Variant("B_balanced", 0.50, 15.0, 3.0, 0.50),
    Variant("C_loose", 0.75, 12.0, 5.0, 0.75),
    Variant("D_strong_impulse", 0.50, 20.0, 3.0, 0.50),
]


def gap_tag(df: pd.DataFrame, lo: int, hi: int, impulse_height: float):
    if hi <= lo or impulse_height <= 0:
        return np.nan, np.nan, False
    op, cl = s(df["Open"]), s(df["Close"])
    best = 0.0
    best_j = None
    for j in range(lo + 1, hi + 1):
        g = float(op.iloc[j] - cl.iloc[j - 1])
        if g > best:
            best, best_j = g, j
    if best_j is None:
        return 0.0, np.nan, False
    share = best / impulse_height
    pos = (best_j - lo) / max(1, hi - lo)
    dominated = share >= 0.35 and pos <= 0.60
    return float(share), float(pos), bool(dominated)


def find_impulse_before(df: pd.DataFrame, i: int, impulse_lookback: int, recent_high_days: int):
    """Use only bars before candidate entry day i."""
    hist = df.iloc[:i]
    if len(hist) < 100:
        return None
    high, low, close = map(s, [hist["High"], hist["Low"], hist["Close"]])
    recent_n = min(recent_high_days, len(hist))
    recent = high.iloc[-recent_n:]
    hi = len(hist) - recent_n + int(np.argmax(recent.to_numpy()))
    # High must have occurred before the candidate day; a pullback after it must exist.
    if hi >= len(hist) - 1:
        return None
    lo_start = max(0, hi - impulse_lookback)
    if hi <= lo_start:
        return None
    lo_slice = low.iloc[lo_start:hi]
    lo = lo_start + int(np.argmin(lo_slice.to_numpy()))
    impulse_low = float(low.iloc[lo])
    impulse_high = float(high.iloc[hi])
    if impulse_high <= impulse_low:
        return None
    impulse_pct = (impulse_high / impulse_low - 1.0) * 100.0
    fib236 = impulse_high - 0.236 * (impulse_high - impulse_low)
    fib382 = impulse_high - 0.382 * (impulse_high - impulse_low)
    high52 = float(high.iloc[-min(252, len(hist)):].max())
    ema20_series = close.ewm(span=20, adjust=False).mean()
    ema20 = float(ema20_series.iloc[-1])
    return {
        "lo": lo, "hi": hi, "low": impulse_low, "high": impulse_high,
        "impulse_pct": impulse_pct, "fib236": fib236, "fib382": fib382,
        "high52": high52, "ema20": ema20,
    }


def resolve(df: pd.DataFrame, i: int, entry: float, stop: float, target: float, max_hold: int = 40):
    risk = entry - stop
    if risk <= 0:
        return None
    end = min(len(df), i + max_hold + 1)
    exit_price = np.nan
    exit_date = pd.NaT
    outcome = "TIME"
    target_hit = False
    for j in range(i, end):
        o, h, l = map(float, [df["Open"].iloc[j], df["High"].iloc[j], df["Low"].iloc[j]])
        hs, ht = l <= stop, h >= target
        if hs and ht:
            exit_price, exit_date, outcome = stop, df.index[j], "STOP_SAME_BAR_AMBIG"
            break
        if hs:
            exit_price = min(stop, o) if j > i else stop
            exit_date, outcome = df.index[j], "STOP"
            break
        if ht:
            exit_price = max(target, o) if o >= target else target
            exit_date, outcome, target_hit = df.index[j], "PRIOR_HIGH", True
            break
    if pd.isna(exit_date):
        j = end - 1
        exit_price, exit_date = float(df["Close"].iloc[j]), df.index[j]
    return {
        "exit_date": exit_date, "exit_price": exit_price, "outcome": outcome,
        "target_hit": target_hit, "r_multiple": (exit_price - entry) / risk,
        "holding_days": int(df.index.get_loc(exit_date) - i),
    }


def candidate_for_variant(symbol: str, df: pd.DataFrame, i: int, imp: dict, v: Variant, last_impulse_key):
    # One signal per impulse: same identified low/high pair cannot fire repeatedly.
    key = (imp["lo"], imp["hi"])
    if key == last_impulse_key:
        return None

    if imp["impulse_pct"] < v.min_impulse_pct:
        return None
    if imp["high"] < imp["high52"] * (1.0 - v.max_below_52w_high_pct / 100.0):
        return None

    fib236, fib382, ema20 = imp["fib236"], imp["fib382"], imp["ema20"]
    confluence = abs(ema20 - fib236) / fib236 * 100.0
    if confluence > v.ema_fib_dist_pct:
        return None

    # The pullback is shallow BEFORE the entry day. It may slightly undercut 0.236,
    # but it must not approach 0.382.
    pull = df.iloc[imp["hi"] + 1:i]
    if pull.empty:
        return None
    pull_low = float(s(pull["Low"]).min())
    allowed_floor = fib236 * (1.0 - v.max_pullback_below_236_pct / 100.0)
    if pull_low < allowed_floor:
        return None
    if pull_low <= fib382:
        return None

    # Avoid repeated "hovering" entries: before today, EMA20 must not already have been
    # touched since the impulse high. This models the first clean pullback only.
    pre_low = s(pull["Low"])
    if (pre_low <= ema20).any():
        return None

    o, h, l = map(float, [df["Open"].iloc[i], df["High"].iloc[i], df["Low"].iloc[i]])
    # Pre-hung limit at EMA20: gap below fills at open; normal touch fills at EMA20.
    if o <= ema20:
        entry = o
    elif l <= ema20 <= h:
        entry = ema20
    else:
        return None

    # If the entry day itself has already collapsed to 0.382, reject as a failed shallow pullback.
    if l <= fib382 or entry <= fib382:
        return None

    result = resolve(df, i, entry, fib382, imp["high"], 40)
    if result is None:
        return None
    share, pos, dominated = gap_tag(df, imp["lo"], imp["hi"], imp["high"] - imp["low"])

    def fwd(n):
        j = min(len(df) - 1, i + n)
        return (float(df["Close"].iloc[j]) / entry - 1.0) * 100.0

    return {
        "variant": v.name, "symbol": symbol, "entry_date": df.index[i],
        "entry": entry, "ema20": ema20, "fib0236": fib236, "fib0382": fib382,
        "confluence_pct": confluence, "impulse_low": imp["low"], "impulse_high": imp["high"],
        "impulse_pct": imp["impulse_pct"], "pullback_low_before_entry": pull_low,
        "gap_share": share, "gap_position": pos, "gap_dominated_tag": dominated,
        "stop": fib382, "target_prior_high": imp["high"],
        "fwd_5d_pct": fwd(5), "fwd_10d_pct": fwd(10), "fwd_20d_pct": fwd(20),
        **result,
    }


def metrics(t: pd.DataFrame):
    if t.empty:
        return {"trades": 0}
    r = pd.to_numeric(t["r_multiple"], errors="coerce").dropna()
    wins, losses = r[r > 0], r[r < 0]
    gp, gl = float(wins.sum()), float(-losses.sum())
    ordered = t.sort_values("exit_date")
    eq = ordered["r_multiple"].fillna(0).cumsum()
    dd = eq - eq.cummax()
    return {
        "trades": int(len(t)),
        "win_rate_pct": round(float((r > 0).mean() * 100), 2),
        "prior_high_hit_pct": round(float(t["target_hit"].mean() * 100), 2),
        "avg_r": round(float(r.mean()), 3),
        "median_r": round(float(r.median()), 3),
        "profit_factor_r": round(gp / gl, 3) if gl > 0 else None,
        "max_drawdown_r": round(float(dd.min()), 3),
        "avg_fwd_5d_pct": round(float(t["fwd_5d_pct"].mean()), 3),
        "avg_fwd_10d_pct": round(float(t["fwd_10d_pct"].mean()), 3),
        "avg_fwd_20d_pct": round(float(t["fwd_20d_pct"].mean()), 3),
        "avg_holding_days": round(float(t["holding_days"].mean()), 2),
        "gap_dominated_pct": round(float(t["gap_dominated_tag"].mean() * 100), 2),
        "total_r": round(float(r.sum()), 3),
    }


def main():
    p = argparse.ArgumentParser(description="Tightened EMA20 + Fib 0.236 first-pullback study")
    p.add_argument("--symbols", default="data/us_1b_universe.txt")
    p.add_argument("--period", default="5y")
    p.add_argument("--output-dir", default="ema20_fib_v2_output")
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=80)
    p.add_argument("--impulse-lookback", type=int, default=80)
    p.add_argument("--recent-high-days", type=int, default=20)
    a = p.parse_args()

    symbols = load_symbols(a.symbols, a.limit)
    rows = []
    for st in range(0, len(symbols), a.batch_size):
        batch = symbols[st:st + a.batch_size]
        print(f"Downloading {st+1}-{min(st+len(batch),len(symbols))} / {len(symbols)}")
        try:
            data = yf.download(batch, period=a.period, interval="1d", group_by="ticker", auto_adjust=True, threads=True, progress=False)
        except Exception as e:
            print("batch failed", e); continue
        for sym in batch:
            try:
                df = (data if len(batch) == 1 else data[sym]).dropna(subset=["Open","High","Low","Close","Volume"]).copy()
                if len(df) < 220:
                    continue
                last_keys = {v.name: None for v in VARIANTS}
                for i in range(180, len(df)):
                    imp = find_impulse_before(df, i, a.impulse_lookback, a.recent_high_days)
                    if imp is None:
                        continue
                    for v in VARIANTS:
                        tr = candidate_for_variant(sym, df, i, imp, v, last_keys[v.name])
                        if tr is not None:
                            rows.append(tr)
                            last_keys[v.name] = (imp["lo"], imp["hi"])
            except Exception as e:
                print("skip", sym, e)
        time.sleep(0.35)

    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    t = pd.DataFrame(rows)
    if not t.empty:
        for c in ["entry_date","exit_date"]:
            t[c] = pd.to_datetime(t[c], errors="coerce")
        t = t.sort_values(["entry_date","symbol","variant"]).reset_index(drop=True)
    t.to_csv(out / "trades.csv", index=False)

    summary = {}
    yearly_rows = []
    if not t.empty:
        for v in VARIANTS:
            g = t[t.variant == v.name].copy()
            summary[v.name] = metrics(g)
            if not g.empty:
                for year, yg in g.groupby(g.entry_date.dt.year):
                    m = metrics(yg); m["variant"] = v.name; m["year"] = int(year)
                    yearly_rows.append(m)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame(yearly_rows).to_csv(out / "yearly.csv", index=False)

    print("\n=== EMA20 + FIB 0.236 V2 ===")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
