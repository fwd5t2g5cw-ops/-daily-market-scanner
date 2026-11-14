from __future__ import annotations

import math
import os
import shutil
import textwrap
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
PDF_DIR = OUT / "pdf"
CHART_DIR = OUT / "dual_fib_case_charts"
SUCCESS_DIR = CHART_DIR / "success_cases"
FAIL_DIR = CHART_DIR / "failure_cases"
SUMMARY_DIR = CHART_DIR / "summary_charts"

FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
MPL_FONT = font_manager.FontProperties(fname=FONT_REG)
MPL_BOLD = font_manager.FontProperties(fname=FONT_BOLD)
plt.rcParams["font.family"] = MPL_FONT.get_name()
plt.rcParams["axes.unicode_minus"] = False


def load_cases() -> pd.DataFrame:
    sources = [
        ("美股首1,000", ROOT / "dual_fib_final_us" / "dual_fib_trades.csv"),
        ("美股未見樣本", ROOT / "dual_fib_unseen_us" / "dual_fib_trades.csv"),
        ("港股驗證", ROOT / "dual_fib_hk" / "dual_fib_trades.csv"),
    ]
    frames = []
    for market, path in sources:
        d = pd.read_csv(path)
        d["sample"] = market
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d = d[
        (d["overlap_0382_pct"] <= 2.0)
        & (d["overlap_1618_pct"] <= 0.5)
        & (d["planned_r"].between(1.5, 4.0))
    ].copy()
    # Completed observation only: target/stop can finish early; otherwise require 90 sessions.
    d = d[(d["outcome"] != "UNRESOLVED") | (d["holding_days"] >= 90)].copy()
    d["category_zh"] = d["outcome"].map(
        {"SUCCESS_TARGET": "成功到達1.618", "FAIL_STOP": "失敗跌穿止蝕", "UNRESOLVED": "90日限時離場"}
    )
    d["case_id"] = np.arange(1, len(d) + 1)
    assert len(d) == 100
    assert (d["outcome"] == "SUCCESS_TARGET").sum() == 15
    assert (d["outcome"] == "FAIL_STOP").sum() == 39
    assert (d["outcome"] == "UNRESOLVED").sum() == 46
    return d


def derived_anchors(row):
    # Recover the user's 1 and 0.786 anchor prices from two projected levels.
    slope_a = (row.fib_a_1618 - row.fib_a_0382) / (1.618 - 0.382)
    a_high = row.fib_a_0382 + (1.0 - 0.382) * slope_a
    a_low = row.fib_a_0382 + (0.786 - 0.382) * slope_a
    slope_b = (row.fib_b_0382 - row.fib_b_neg1618) / (0.382 - (-1.618))
    b_low = row.fib_b_0382 + (1.0 - 0.382) * slope_b
    b_high = row.fib_b_0382 + (0.786 - 0.382) * slope_b
    return a_high, a_low, b_low, b_high


def case_chart(row, path: Path):
    a_high, a_low, b_low, b_high = derived_anchors(row)
    is_success = row.outcome == "SUCCESS_TARGET"
    outcome_price = row.target if is_success else row.stop
    c = "#178b57" if is_success else "#c73e3a"
    fig, ax = plt.subplots(figsize=(9.0, 5.1), dpi=160)
    fig.patch.set_facecolor("#f7f8fa")
    ax.set_facecolor("white")
    xs = np.arange(6)
    ys = [a_high, a_low, b_low, b_high, row.entry, outcome_price]
    ax.plot(xs[:4], ys[:4], color="#667085", lw=2.0, marker="o", zorder=3)
    ax.plot(xs[3:5], ys[3:5], color="#2f6fed", lw=2.2, marker="o", zorder=3)
    ax.plot(xs[4:], ys[4:], color=c, lw=3.2, marker="o", zorder=4)
    ax.axhspan(min(row.fib_a_0382, row.fib_b_0382), max(row.fib_a_0382, row.fib_b_0382), color="#2f6fed", alpha=.12)
    ax.axhline(row.target, color="#178b57", lw=1.4, ls="--", label=f"目標 {row.target:.2f}")
    ax.axhline(row.entry, color="#344054", lw=1.2, ls=":", label=f"入場 {row.entry:.2f}")
    ax.axhline(row.stop, color="#c73e3a", lw=1.4, ls="--", label=f"止蝕 {row.stop:.2f}")
    labels = ["A高點\n1", "A低點\n0.786", "B低點\n1", "B高點\n0.786", "入場", "目標" if is_success else "止蝕"]
    ax.set_xticks(xs, labels, fontproperties=MPL_FONT, fontsize=9)
    ax.set_ylabel("價格", fontproperties=MPL_FONT)
    title = f"{row.symbol}  |  {row.entry_date}  |  {'成功' if is_success else '失敗'} {row.realized_r:+.2f}R"
    ax.set_title(title, fontproperties=MPL_BOLD, fontsize=14, loc="left", pad=12, color="#101828")
    subtitle = (
        f"{row.sample}  ·  0.382差 {row.overlap_0382_pct:.2f}%  ·  1.618差 {row.overlap_1618_pct:.2f}%  ·  "
        f"計劃 {row.planned_r:.2f}R  ·  持有 {int(row.holding_days)}日  ·  MFE {row.max_favourable_r:.2f}R"
    )
    ax.text(0, 1.01, subtitle, transform=ax.transAxes, fontproperties=MPL_FONT, fontsize=8.5, color="#475467", va="bottom")
    ax.grid(axis="y", color="#eaecf0", lw=.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(loc="best", frameon=False, prop=MPL_FONT, fontsize=8)
    ax.text(.995, .01, "結構圖：按已確認轉折及交易水平繪製，並非完整K線走勢", transform=ax.transAxes,
            ha="right", va="bottom", fontproperties=MPL_FONT, fontsize=7, color="#667085")
    fig.tight_layout(pad=1.5)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def summary_charts(d: pd.DataFrame):
    counts = d["category_zh"].value_counts().reindex(["成功到達1.618", "失敗跌穿止蝕", "90日限時離場"])
    fig, ax = plt.subplots(figsize=(10, 5.4), dpi=170)
    bars = ax.bar(counts.index, counts.values, color=["#178b57", "#c73e3a", "#667085"], width=.58)
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x()+b.get_width()/2, v+.8, f"{v}宗\n{v}%", ha="center", fontproperties=MPL_BOLD, fontsize=11)
    ax.set_title("100宗完整案例：結果分布", fontproperties=MPL_BOLD, fontsize=17, loc="left")
    ax.set_ylabel("案例數目", fontproperties=MPL_FONT)
    ax.set_ylim(0, max(counts.values)*1.22)
    ax.grid(axis="y", color="#eaecf0")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=10)
    for t in ax.get_xticklabels(): t.set_fontproperties(MPL_FONT)
    fig.tight_layout()
    p1 = SUMMARY_DIR / "01_outcome_distribution.png"
    fig.savefig(p1, bbox_inches="tight")
    plt.close(fig)

    suc = d[d.outcome == "SUCCESS_TARGET"].sort_values("realized_r")
    fig, ax = plt.subplots(figsize=(10, 7.2), dpi=170)
    labels = [f"{r.symbol}  {r.entry_date}" for r in suc.itertuples()]
    ax.barh(labels, suc.realized_r, color="#178b57")
    for y, v in enumerate(suc.realized_r): ax.text(v+.03, y, f"+{v:.2f}R", va="center", fontproperties=MPL_FONT, fontsize=8)
    ax.set_title("15宗成功案例：實現回報", fontproperties=MPL_BOLD, fontsize=17, loc="left")
    ax.set_xlabel("實現回報（R）", fontproperties=MPL_FONT)
    ax.grid(axis="x", color="#eaecf0")
    ax.spines[["top", "right", "left"]].set_visible(False)
    for t in ax.get_yticklabels(): t.set_fontproperties(MPL_FONT)
    fig.tight_layout()
    p2 = SUMMARY_DIR / "02_success_realized_r.png"
    fig.savefig(p2, bbox_inches="tight")
    plt.close(fig)

    fail = d[d.outcome == "FAIL_STOP"].sort_values("max_favourable_r")
    fig, ax = plt.subplots(figsize=(10, 11.5), dpi=170)
    labels = [f"{r.symbol}  {r.entry_date}" for r in fail.itertuples()]
    colors_fail = ["#e59a23" if v >= 1 else "#c73e3a" for v in fail.max_favourable_r]
    ax.barh(labels, fail.max_favourable_r, color=colors_fail)
    ax.axvline(1, color="#344054", ls="--", lw=1, label="曾升至 +1R")
    ax.set_title("39宗失敗案例：止蝕前最大有利升幅（MFE）", fontproperties=MPL_BOLD, fontsize=17, loc="left")
    ax.set_xlabel("止蝕前最高曾錄得幾多R", fontproperties=MPL_FONT)
    ax.grid(axis="x", color="#eaecf0")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(prop=MPL_FONT, frameon=False)
    for t in ax.get_yticklabels(): t.set_fontproperties(MPL_FONT)
    fig.tight_layout()
    p3 = SUMMARY_DIR / "03_failure_mfe.png"
    fig.savefig(p3, bbox_inches="tight")
    plt.close(fig)

    return [p1, p2, p3]


def build_pdf(d: pd.DataFrame, summary_paths, pdf_path: Path):
    page_assets = CHART_DIR / "pdf_pages"
    page_assets.mkdir(exist_ok=True)

    def save_cover(path: Path, heading: str, subheading: str, lines: list[str], table=None):
        fig = plt.figure(figsize=(8.27, 11.69), dpi=150, facecolor="white")
        ax = fig.add_axes([.09,.08,.82,.84]); ax.axis("off")
        ax.text(0, .96, heading, fontproperties=MPL_BOLD, fontsize=23, color="#101828", va="top")
        ax.text(0, .89, subheading, fontproperties=MPL_FONT, fontsize=14, color="#2f6fed", va="top")
        y=.79
        for line in lines:
            ax.text(0, y, textwrap.fill(line, 45), fontproperties=MPL_FONT, fontsize=11, color="#344054", va="top", linespacing=1.5)
            y -= .11
        if table:
            cols, rows = table
            t=ax.table(cellText=rows, colLabels=cols, cellLoc="center", colLoc="center", bbox=[0,.12,1,.25])
            t.auto_set_font_size(False); t.set_fontsize(9)
            for (r,c),cell in t.get_celld().items():
                cell.get_text().set_fontproperties(MPL_FONT if r else MPL_BOLD)
                cell.set_edgecolor("#d0d5dd"); cell.set_facecolor("#e9eef8" if r==0 else "white")
        fig.savefig(path, bbox_inches="tight"); plt.close(fig)

    cols=["結果","案例","平均R","平均持有日數"]
    rows=[]
    for key,label in [("SUCCESS_TARGET","到達1.618"),("FAIL_STOP","跌穿止蝕"),("UNRESOLVED","90日限時離場")]:
        x=d[d.outcome==key]; rows.append([label,str(len(x)),f"{x.realized_r.mean():+.3f}R",f"{x.holding_days.mean():.1f}"])
    rows.append(["全部","100",f"{d.realized_r.mean():+.3f}R",f"{d.holding_days.mean():.1f}"])
    cover=page_assets/"cover.png"
    save_cover(cover,"雙重 Fibonacci 緊密目標共振策略","成功與失敗案例圖表 · 100宗完整觀察樣本",[
        "篩選條件：兩組0.382差距不超過2%；兩組1.618差距不超過0.5%；下一日開市價計劃回報風險介乎1.5R至4R；入場後最多觀察90個交易日。",
        "15宗到達1.618列為成功，39宗先跌穿止蝕列為失敗；其餘46宗90日限時離場獨立列出。個別案例頁是交易結構圖，不是完整日線K線。"
    ],(cols,rows))

    success_cover=page_assets/"success_cover.png"; fail_cover=page_assets/"failure_cover.png"
    save_cover(success_cover,"成功案例結構圖","15宗到達1.618",["每張圖顯示兩組錨點、0.382重疊區、入場、止蝕、目標、實現R、持有日數及MFE。"])
    save_cover(fail_cover,"失敗案例結構圖","39宗先跌穿止蝕",["橙色摘要柱代表止蝕前曾升至最少+1R；個別圖可用來比較失敗前是否曾有足夠浮盈保護。"])

    timeout_pages=[]
    timeouts=d[d.outcome=="UNRESOLVED"].sort_values("realized_r",ascending=False)
    for page_no,start in enumerate(range(0,len(timeouts),23),1):
        x=timeouts.iloc[start:start+23]
        fig=plt.figure(figsize=(8.27,11.69),dpi=150,facecolor="white"); ax=fig.add_axes([.06,.06,.88,.88]); ax.axis("off")
        ax.text(0,.98,"90日限時離場案例索引",fontproperties=MPL_BOLD,fontsize=20,va="top",color="#101828")
        ax.text(0,.935,f"第{page_no}部分 · 未先到目標或止蝕，以第90個交易日收市價計算",fontproperties=MPL_FONT,fontsize=10,va="top",color="#475467")
        vals=[[r.symbol,r.entry_date,r.sample,f"{r.realized_r:+.2f}",f"{r.max_favourable_r:+.2f}",f"{r.max_adverse_r:+.2f}"] for r in x.itertuples()]
        t=ax.table(cellText=vals,colLabels=["股票","入場日","樣本","90日R","MFE","MAE"],cellLoc="center",colLoc="center",bbox=[0,.04,1,.83])
        t.auto_set_font_size(False); t.set_fontsize(8)
        for (rr,cc),cell in t.get_celld().items():
            cell.get_text().set_fontproperties(MPL_FONT if rr else MPL_BOLD); cell.set_edgecolor("#d0d5dd"); cell.set_facecolor("#e9eef8" if rr==0 else "white")
        p=page_assets/f"timeouts_{page_no}.png"; fig.savefig(p,bbox_inches="tight"); plt.close(fig); timeout_pages.append(p)

    success_paths=[SUCCESS_DIR/f"{r.entry_date}_{r.symbol.replace('/','-')}.png" for r in d[d.outcome=="SUCCESS_TARGET"].sort_values(["entry_date","symbol"]).itertuples()]
    fail_paths=[FAIL_DIR/f"{r.entry_date}_{r.symbol.replace('/','-')}.png" for r in d[d.outcome=="FAIL_STOP"].sort_values(["entry_date","symbol"]).itertuples()]
    pages=[cover,*summary_paths,success_cover,*success_paths,fail_cover,*fail_paths,*timeout_pages]
    c=pdfcanvas.Canvas(str(pdf_path),pagesize=A4); c.setTitle("Dual Fib Success and Failure Case Charts")
    W,H=A4
    for n,p in enumerate(pages,1):
        from PIL import Image as PILImage
        with PILImage.open(p) as im: iw,ih=im.size
        scale=min((W-20*mm)/iw,(H-25*mm)/ih); w,h=iw*scale,ih*scale
        c.drawImage(str(p),(W-w)/2,(H-h)/2+3*mm,width=w,height=h,preserveAspectRatio=True,mask='auto')
        c.setFillColor(colors.HexColor("#667085")); c.setFont("Helvetica",7)
        c.drawString(10*mm,6*mm,"Dual Fibonacci backtest - 2026-11-14")
        c.drawRightString(W-10*mm,6*mm,f"Page {n} / {len(pages)}")
        c.showPage()
    c.save()


def main():
    if CHART_DIR.exists(): shutil.rmtree(CHART_DIR)
    for p in [PDF_DIR, SUCCESS_DIR, FAIL_DIR, SUMMARY_DIR]: p.mkdir(parents=True, exist_ok=True)
    d = load_cases()
    summary_paths = summary_charts(d)
    for r in d[d.outcome == "SUCCESS_TARGET"].itertuples():
        case_chart(r, SUCCESS_DIR / f"{r.entry_date}_{r.symbol.replace('/','-')}.png")
    for r in d[d.outcome == "FAIL_STOP"].itertuples():
        case_chart(r, FAIL_DIR / f"{r.entry_date}_{r.symbol.replace('/','-')}.png")
    index_cols = ["case_id","sample","symbol","entry_date","outcome","category_zh","entry","stop","target","planned_r","realized_r","holding_days","overlap_0382_pct","overlap_1618_pct","max_favourable_r","max_adverse_r"]
    d[index_cols].to_csv(CHART_DIR / "case_index_100.csv", index=False, encoding="utf-8-sig")
    pdf_path = PDF_DIR / "Dual_Fib_Success_Failure_Case_Charts.pdf"
    build_pdf(d, summary_paths, pdf_path)
    readme = CHART_DIR / "README.txt"
    readme.write_text("雙重 Fibonacci 成功與失敗案例圖表\n\n成功案例：15宗\n失敗止蝕：39宗\n90日限時離場：46宗（見PDF及CSV索引）\n\n個別PNG為交易結構圖，並非完整K線圖。\n", encoding="utf-8")
    zip_path = OUT / "Dual_Fib_Case_Charts_Package.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pdf_path, pdf_path.name)
        z.write(ROOT / "create_dual_fib_case_charts.py", "create_dual_fib_case_charts.py")
        for p in CHART_DIR.rglob("*"):
            if p.is_file(): z.write(p, Path("case_charts") / p.relative_to(CHART_DIR))
    print(pdf_path)
    print(zip_path)


if __name__ == "__main__":
    main()
