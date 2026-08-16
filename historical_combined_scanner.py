from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import scanner as legacy_scanner

RESISTANCE_BARS = 50
MIN_BREAKOUT_PCT = 1.0
MAX_BO_AGE = 30
EMA_LEN = 20
VOL_LEN = 20


def parse_as_of(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--as-of must be YYYY-MM-DD") from exc


def series(x):
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 0:
            return pd.Series(dtype=float)
        x = x.iloc[:, 0]
    return pd.to_numeric(x, errors="coerce").dropna().astype(float)


def extract_symbol_frame(data: pd.DataFrame, symbol: str, single: bool) -> pd.DataFrame | None:
    try:
        d = data.copy() if single else data[symbol].copy()
    except Exception:
        return None
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    needed = ["Open", "High", "Low", "Close", "Volume"]
    if any(c not in d.columns for c in needed):
        return None
    d = d.dropna(subset=["Close", "Volume"])
    return d if not d.empty else None


def big_zone_analyze(ticker: str, market: str, d: pd.DataFrame):
    if d is None or len(d) < 220:
        return None
    d = d.dropna(subset=["Open", "High", "Low", "Close", "Volume"]).copy()
    if len(d) < 220:
        return None
    c, h, l, v = map(series, [d.Close, d.High, d.Low, d.Volume])
    ema20 = c.ewm(span=EMA_LEN, adjust=False).mean()
    avgvol = v.rolling(VOL_LEN).mean()
    prior = h.shift(1).rolling(RESISTANCE_BARS).max()
    threshold = prior * (1 + MIN_BREAKOUT_PCT / 100)
    bo = (c > threshold) & (c.shift(1) <= prior)
    idx = np.flatnonzero(bo.fillna(False).to_numpy())
    if len(idx) == 0:
        return None
    last = int(idx[-1])
    age = len(d) - 1 - last
    if age < 0 or age > MAX_BO_AGE:
        return None
    level = float(prior.iloc[last])
    price = float(c.iloc[-1])
    e20 = float(ema20.iloc[-1])
    low = float(l.iloc[-1])
    vol = float(v.iloc[-1])
    av = float(avgvol.iloc[-1])
    ema_dist = min(abs(price / e20 - 1), abs(low / e20 - 1)) * 100 if e20 > 0 else 999
    level_dist = min(abs(price / level - 1), abs(low / level - 1)) * 100 if level > 0 else 999
    bo_score = 3 if age <= 5 else 2 if age <= 15 else 1
    ema_score = 3 if ema_dist <= 2 else 2 if ema_dist <= 5 else 1 if ema_dist <= 8 else 0
    level_score = 3 if level_dist <= 2 else 2 if level_dist <= 5 else 1 if level_dist <= 8 else 0
    contraction = bool(pd.notna(av) and vol < av)
    score = bo_score + ema_score + level_score + (1 if contraction else 0)
    status = "READY" if score >= 8 and ema_score >= 2 and level_score >= 2 else "WATCH" if score >= 6 else "EARLY"
    return {
        "Market": market,
        "Ticker": ticker,
        "Price": round(price, 3),
        "Score": score,
        "Status": status,
        "BO_Date": str(pd.Timestamp(d.index[last]).date()),
        "BO_Age_Days": age,
        "Breakout_Level": round(level, 3),
        "EMA20": round(e20, 3),
        "Dist_EMA20_%": round(ema_dist, 2),
        "Dist_Breakout_%": round(level_dist, 2),
        "Volume_Contracting": contraction,
        "BO_Score": bo_score,
        "EMA20_Score": ema_score,
        "Level_Score": level_score,
    }


def load_market_universe(market: str) -> pd.DataFrame:
    universe_market = {"us": "us", "tsx": "tsx", "hkex": "hk"}[market]
    subprocess.run([sys.executable, "build_universes.py", "--markets", universe_market], check=True)
    if market == "us":
        return legacy_scanner.load_universe("data/us_universe.txt")
    path = {"tsx": "data/tsx_universe.txt", "hkex": "data/hk_universe.txt"}[market]
    syms = [x.strip().upper() for x in Path(path).read_text().splitlines() if x.strip() and not x.startswith("#")]
    if market == "tsx":
        syms = [s for s in syms if s.endswith(".TO") and not s.endswith(".V")]
    return pd.DataFrame({"symbol": list(dict.fromkeys(syms)), "security_name": "", "is_etf": False})


def historical_download(symbols: list[str], start: str, end: str, batch_size: int = 100):
    for st in range(0, len(symbols), batch_size):
        batch = symbols[st:st + batch_size]
        print(f"Downloading {st+1}-{min(st+batch_size, len(symbols))} of {len(symbols)} through historical cutoff...")
        try:
            data = yf.download(
                batch,
                start=start,
                end=end,
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                threads=True,
                progress=False,
            )
        except Exception as exc:
            print("Batch failed", exc)
            continue
        yield batch, data
        time.sleep(0.35)


def save_legacy_outputs(res: pd.DataFrame, out: Path, min_score: int = 1, min_rs: float = 70):
    legacy_dir = out / "legacy"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    scan_path = legacy_dir / "scan_results.csv"
    if res.empty:
        res.to_csv(scan_path, index=False)
        return pd.DataFrame()
    sel = res[(res.mandatory_pass) & (res.rs_percentile >= min_rs) & (res.score >= min_score)].copy()
    sel.to_csv(scan_path, index=False)
    stocks = sel[~sel.is_etf.fillna(False)].copy()
    etfs = sel[sel.is_etf.fillna(False)].copy()
    plan_parts = []
    for prefix, d in [("", stocks), ("etf_", etfs)]:
        masks = {
            "vcp_breakout.csv": d.vcp_breakout,
            "vcp_watch.csv": d.vcp_watch,
            "playbook_trigger.csv": d.playbook_trigger,
            "playbook_watch.csv": d.playbook_watch,
            "high_conviction.csv": d.high_conviction,
        }
        for name, mask in masks.items():
            d[mask].to_csv(legacy_dir / f"{prefix}{name}", index=False)
        triggered = d[d.plan_type.isin(["PLAYBOOK_TRIGGER", "VCP_BREAKOUT"])].sort_values(
            ["grade_score", "rr_target1"], ascending=[False, False]
        )
        pending = d[d.plan_type.isin(["PLAYBOOK_WATCH_PENDING_TRIGGER", "VCP_WATCH_PENDING_BREAKOUT"])].sort_values(
            ["watch_score", "trigger_distance_pct", "rs_percentile"], ascending=[False, True, False]
        )
        plans = pd.concat([triggered, pending])
        plans.to_csv(legacy_dir / f"{prefix}trade_plans.csv", index=False)
        if not plans.empty:
            plan_parts.append(plans)
    return pd.concat(plan_parts, ignore_index=True) if plan_parts else pd.DataFrame()


def rank_and_save(legacy: pd.DataFrame, bz: pd.DataFrame, out: Path):
    def symcol(df):
        for c in ["symbol", "Symbol", "Ticker", "ticker"]:
            if c in df.columns:
                return c
        return None

    ls, bs = symcol(legacy), symcol(bz)
    if ls:
        legacy = legacy.copy(); legacy["_symbol"] = legacy[ls].astype(str).str.upper()
    if bs:
        bz = bz.copy(); bz["_symbol"] = bz[bs].astype(str).str.upper()
    legacy["_legacy_score"] = pd.to_numeric(legacy.get("score", 0), errors="coerce").fillna(0) if not legacy.empty else pd.Series(dtype=float)
    bz["_big_zone_score"] = pd.to_numeric(bz.get("Score", 0), errors="coerce").fillna(0) if not bz.empty else pd.Series(dtype=float)
    legacy_symbols = set(legacy["_symbol"]) if "_symbol" in legacy.columns else set()
    bz_symbols = set(bz["_symbol"]) if "_symbol" in bz.columns else set()
    overlap_symbols = legacy_symbols & bz_symbols

    if not legacy.empty:
        legacy["overlap"] = legacy["_symbol"].isin(overlap_symbols)
        pt = legacy.get("plan_type", pd.Series("", index=legacy.index)).fillna("").astype(str)
        legacy["_action_rank"] = pt.map({"PLAYBOOK_TRIGGER": 4, "VCP_BREAKOUT": 4, "PLAYBOOK_WATCH_PENDING_TRIGGER": 3, "VCP_WATCH_PENDING_BREAKOUT": 3}).fillna(0)
        legacy["_grade_score_sort"] = pd.to_numeric(legacy.get("grade_score", 0), errors="coerce").fillna(0)
        legacy["_watch_score_sort"] = pd.to_numeric(legacy.get("watch_score", 0), errors="coerce").fillna(0)
        legacy["_trigger_distance_sort"] = pd.to_numeric(legacy.get("trigger_distance_pct", 999), errors="coerce").fillna(999)
        legacy["_rs_sort"] = pd.to_numeric(legacy.get("rs_percentile", 0), errors="coerce").fillna(0)
        legacy_ranked = legacy.sort_values(
            ["_action_rank", "_grade_score_sort", "_watch_score_sort", "_trigger_distance_sort", "_rs_sort", "overlap"],
            ascending=[False, False, False, True, False, False],
        )
    else:
        legacy_ranked = legacy.copy()
    legacy_ranked.head(12).to_csv(out / "legacy_top12.csv", index=False)

    if not bz.empty:
        bz["overlap"] = bz["_symbol"].isin(overlap_symbols)
        bz_ranked = bz.sort_values(["_big_zone_score", "overlap", "BO_Age_Days"], ascending=[False, False, True])
    else:
        bz_ranked = bz.copy()
    bz_ranked.head(12).to_csv(out / "big_zone_top12.csv", index=False)

    if ls and bs:
        merged = pd.merge(legacy, bz, on="_symbol", how="outer", suffixes=("_legacy", "_bigzone"))
    elif ls:
        merged = legacy.copy(); merged["_big_zone_score"] = 0
    elif bs:
        merged = bz.copy(); merged["_legacy_score"] = 0
    else:
        merged = pd.DataFrame(columns=["_symbol", "_legacy_score", "_big_zone_score"])
    for c in ["_legacy_score", "_big_zone_score"]:
        if c not in merged.columns:
            merged[c] = 0
        merged[c] = pd.to_numeric(merged[c], errors="coerce").fillna(0)
    merged["overlap"] = (merged["_legacy_score"] > 0) & (merged["_big_zone_score"] > 0)
    merged["combined_score"] = merged["_legacy_score"] + merged["_big_zone_score"] + merged["overlap"].astype(int) * 3
    merged = merged.sort_values(["combined_score", "overlap", "_big_zone_score", "_legacy_score"], ascending=[False, False, False, False])
    merged.to_csv(out / "combined_all.csv", index=False)
    merged.head(12).to_csv(out / "combined_top12.csv", index=False)
    merged[merged.overlap].sort_values("combined_score", ascending=False).to_csv(out / "overlap.csv", index=False)

    print("\n=== LEGACY TOP 12 ===")
    print("(none)" if legacy_ranked.empty else legacy_ranked[[c for c in ["_symbol", "plan_type", "signals", "grade_score", "trade_grade", "watch_score", "watch_grade", "trigger_distance_pct", "rs_percentile"] if c in legacy_ranked.columns]].head(12).to_string(index=False))
    print("\n=== BIG ZONE TOP 12 ===")
    print("(none)" if bz_ranked.empty else bz_ranked[[c for c in ["_symbol", "_big_zone_score", "Status", "BO_Age_Days", "Dist_EMA20_%", "Dist_Breakout_%"] if c in bz_ranked.columns]].head(12).to_string(index=False))
    print("\n=== COMBINED TOP 12 ===")
    print(merged[["_symbol", "combined_score", "overlap", "_legacy_score", "_big_zone_score"]].head(12).to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", choices=["us", "tsx", "hkex"], required=True)
    ap.add_argument("--as-of", required=True, type=parse_as_of)
    ap.add_argument("--batch-size", type=int, default=100)
    args = ap.parse_args()

    as_of = args.as_of
    market = args.market
    out = Path("historical_results") / as_of.isoformat() / market
    bz_dir = out / "big_zone"
    out.mkdir(parents=True, exist_ok=True); bz_dir.mkdir(parents=True, exist_ok=True)

    universe = load_market_universe(market)
    symbols = universe.symbol.astype(str).tolist()
    meta = universe.set_index("symbol").to_dict("index")
    # 650 calendar days gives enough pre-history for 252-trading-day RS and 200-day trend tests.
    start = (as_of - timedelta(days=650)).isoformat()
    end = (as_of + timedelta(days=1)).isoformat()  # yfinance end is exclusive

    spy = yf.download("SPY", start=start, end=end, interval="1d", auto_adjust=True, progress=False)
    spy_close = series(spy.Close) if spy is not None and not spy.empty else pd.Series(dtype=float)
    spy_returns = {d: legacy_scanner.pct_return(spy_close, d) for d in (63, 126, 252)}

    legacy_rows = []
    bz_rows = []
    bz_market = {"us": "US", "tsx": "TSX", "hkex": "HK"}[market]
    for batch, data in historical_download(symbols, start, end, args.batch_size):
        single = len(batch) == 1
        for symbol in batch:
            d = extract_symbol_frame(data, symbol, single)
            if d is None:
                continue
            try:
                row = legacy_scanner.analyze(symbol, d, spy_returns)
                if row:
                    row.update(meta.get(symbol, {})); legacy_rows.append(row)
            except Exception as exc:
                print("Legacy skip", symbol, exc)
            try:
                bz = big_zone_analyze(symbol, bz_market, d)
                if bz:
                    bz_rows.append(bz)
            except Exception as exc:
                print("Big Zone skip", symbol, exc)

    if legacy_rows:
        res = pd.DataFrame(legacy_rows)
        stockmask = ~res.is_etf.fillna(False)
        res["rs_percentile"] = np.nan
        res.loc[stockmask, "rs_percentile"] = (res.loc[stockmask, "rs_raw"].rank(pct=True, method="average") * 100).round(0)
        res.loc[~stockmask, "rs_percentile"] = (res.loc[~stockmask, "rs_raw"].rank(pct=True, method="average") * 100).round(0)
        res["rs_strong"] = res.rs_percentile >= 70
        res["score"] += res.rs_strong.astype(int)
        res["high_conviction"] = (res.vcp_breakout | res.vcp_watch) & (res.playbook_trigger | res.playbook_watch)
        res = legacy_scanner.add_grades(res)
    else:
        res = pd.DataFrame()

    legacy = save_legacy_outputs(res, out)
    bz = pd.DataFrame(bz_rows)
    if not bz.empty:
        bz = bz.sort_values(["Score", "BO_Age_Days"], ascending=[False, True])
    bz.to_csv(bz_dir / "big_zone_all.csv", index=False)
    if not bz.empty:
        bz[bz.Status == "READY"].to_csv(bz_dir / "big_zone_ready.csv", index=False)
        bz[bz.Status == "WATCH"].to_csv(bz_dir / "big_zone_watch.csv", index=False)

    rank_and_save(legacy, bz, out)
    (out / "AS_OF.txt").write_text(as_of.isoformat() + "\n")
    print(f"\nHistorical scan complete: market={market} as_of={as_of.isoformat()} output={out}")


if __name__ == "__main__":
    main()
