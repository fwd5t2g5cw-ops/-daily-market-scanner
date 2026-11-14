from __future__ import annotations

import argparse
import math
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import yfinance as yf


UP = "#089981"
DOWN = "#f23645"
BLUE_A = "#2962ff"
BLUE_B = "#7b61ff"
GREEN = "#00a86b"
BG = "#ffffff"
GRID = "#e7e9ed"


def normalize(raw: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(raw.columns, pd.MultiIndex):
        if symbol in raw.columns.get_level_values(-1):
            raw = raw.xs(symbol, axis=1, level=-1)
        else:
            raw.columns = raw.columns.get_level_values(0)
    raw = raw.rename(columns={c: str(c).lower() for c in raw.columns})
    needed = ["open", "high", "low", "close", "volume"]
    out = raw[needed].copy().dropna(subset=needed[:4])
    out.index = pd.to_datetime(out.index).tz_localize(None)
    return out


def download_case(row) -> pd.DataFrame:
    start = pd.Timestamp(row.a_high_date) - pd.Timedelta(days=20)
    end = pd.Timestamp(row.exit_date) + pd.Timedelta(days=12)
    raw = yf.download(row.symbol, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"),
                      auto_adjust=False, progress=False, threads=False)
    df = normalize(raw, row.symbol)
    if df.empty:
        raise RuntimeError(f"No OHLCV returned for {row.symbol}")
    return df


def nearest_pos(index, date) -> int:
    target = pd.Timestamp(date)
    return int(np.argmin(np.abs(index.values.astype("datetime64[ns]") - target.to_datetime64())))


def candlesticks(ax, df: pd.DataFrame):
    x = np.arange(len(df))
    width = max(.35, min(.72, 85 / max(len(df), 1)))
    for i, (_, r) in enumerate(df.iterrows()):
        color = UP if r.close >= r.open else DOWN
        ax.vlines(i, r.low, r.high, color=color, linewidth=.7, zorder=2)
        lo = min(r.open, r.close)
        h = abs(r.close - r.open)
        if h == 0:
            ax.hlines(r.close, i-width/2, i+width/2, color=color, linewidth=1)
        else:
            ax.add_patch(Rectangle((i-width/2, lo), width, h, facecolor=color, edgecolor=color, linewidth=.5, zorder=3))
    return x, width


def add_marker(ax, df, date, text, color, ykind):
    i = nearest_pos(df.index, date)
    r = df.iloc[i]
    y = r.high if ykind == "high" else r.low
    dy = 14 if ykind == "high" else -18
    va = "bottom" if ykind == "high" else "top"
    ax.annotate(text, xy=(i,y), xytext=(0,dy), textcoords="offset points", ha="center", va=va,
                fontsize=7, color=color, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color=color, lw=.7))


def plot_case(row, df: pd.DataFrame, output: Path):
    fig = plt.figure(figsize=(15,8.5), facecolor=BG)
    gs = fig.add_gridspec(5,1,hspace=.04)
    ax = fig.add_subplot(gs[:4,0])
    av = fig.add_subplot(gs[4,0], sharex=ax)
    ax.set_facecolor(BG); av.set_facecolor(BG)
    x, width = candlesticks(ax, df)

    ax.axhspan(min(row.fib_a_0382,row.fib_b_0382), max(row.fib_a_0382,row.fib_b_0382), color=BLUE_A, alpha=.10)
    ax.axhline(row.fib_a_0382, color=BLUE_A, lw=1.1, label=f"A 0.382  {row.fib_a_0382:.2f}")
    ax.axhline(row.fib_b_0382, color=BLUE_B, lw=1.1, label=f"B 0.382  {row.fib_b_0382:.2f}")
    ax.axhline(row.fib_a_1618, color="#13a567", lw=.9, ls="--", alpha=.75, label=f"A 1.618  {row.fib_a_1618:.2f}")
    ax.axhline(row.fib_b_neg1618, color="#6abf69", lw=.9, ls="--", alpha=.75, label=f"B -1.618  {row.fib_b_neg1618:.2f}")
    ax.axhline(row.target, color=GREEN, lw=1.8, label=f"Target  {row.target:.2f}")
    ax.axhline(row.entry, color="#111827", lw=1.2, ls=":", label=f"Entry  {row.entry:.2f}")
    ax.axhline(row.stop, color=DOWN, lw=1.5, ls="--", label=f"Stop  {row.stop:.2f}")

    add_marker(ax,df,row.a_high_date,"A high / 1",BLUE_A,"high")
    add_marker(ax,df,row.a_low_date,"A low / .786",BLUE_A,"low")
    add_marker(ax,df,row.b_low_date,"B low / 1",BLUE_B,"low")
    add_marker(ax,df,row.b_high_date,"B high / .786",BLUE_B,"high")
    for date,text,color in [(row.entry_date,"ENTRY","#111827"),(row.exit_date,"TARGET" if row.outcome=="SUCCESS_TARGET" else "STOP",GREEN if row.outcome=="SUCCESS_TARGET" else DOWN)]:
        i=nearest_pos(df.index,date); ax.axvline(i,color=color,lw=.8,ls=":",alpha=.8)
        ax.text(i,.985,text,transform=ax.get_xaxis_transform(),ha="center",va="top",fontsize=8,color=color,fontweight="bold")

    outcome = "SUCCESS" if row.outcome == "SUCCESS_TARGET" else "FAILURE"
    title = f"{row.symbol}  |  {outcome}  {row.realized_r:+.2f}R  |  Entry {row.entry_date}  Exit {row.exit_date}"
    ax.set_title(title, loc="left", fontsize=16, fontweight="bold", pad=12)
    ax.text(0,1.01,f"Planned {row.planned_r:.2f}R  ·  Holding {int(row.holding_days)} sessions  ·  Daily OHLC (Yahoo Finance)",
            transform=ax.transAxes,fontsize=9,color="#4b5563",va="bottom")
    ax.legend(loc="upper left",ncol=4,fontsize=7,frameon=True,framealpha=.92)
    ax.grid(True,color=GRID,lw=.6)
    ax.yaxis.tick_right(); ax.yaxis.set_label_position("right"); ax.set_ylabel("Price")
    ax.spines[["top","left"]].set_visible(False)

    vol_colors=[UP if c>=o else DOWN for o,c in zip(df.open,df.close)]
    av.bar(x,df.volume,color=vol_colors,width=width,alpha=.75)
    av.grid(True,axis="y",color=GRID,lw=.5); av.yaxis.tick_right(); av.set_ylabel("Volume")
    av.spines[["top","left"]].set_visible(False)
    step=max(1,math.ceil(len(df)/12)); ticks=np.arange(0,len(df),step)
    av.set_xticks(ticks,[df.index[i].strftime("%Y-%m-%d") for i in ticks],rotation=35,ha="right",fontsize=8)
    plt.setp(ax.get_xticklabels(),visible=False)
    fig.tight_layout()
    fig.savefig(output,dpi=150,bbox_inches="tight")
    return fig


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cases",default="selected_20_price_chart_cases.csv"); ap.add_argument("--output",default="price_charts_20")
    args=ap.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    cases=pd.read_csv(args.cases)
    pdf_path=out/"Dual_Fib_10_Success_10_Failure_TradingView_Style.pdf"
    made=[]
    with PdfPages(pdf_path) as pdf:
        for row in cases.itertuples(index=False):
            df=download_case(row)
            group="success" if row.outcome=="SUCCESS_TARGET" else "failure"
            folder=out/group; folder.mkdir(exist_ok=True)
            p=folder/f"{row.symbol.replace('.','_')}_{row.entry_date}_{group}.png"
            fig=plot_case(row,df,p); pdf.savefig(fig,bbox_inches="tight"); plt.close(fig); made.append(p)
    zip_path=out/"Dual_Fib_20_TradingView_Style_Charts.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(pdf_path,pdf_path.name); z.write(args.cases,Path(args.cases).name)
        for p in made:z.write(p,p.relative_to(out))
    print(pdf_path); print(zip_path)


if __name__ == "__main__": main()
