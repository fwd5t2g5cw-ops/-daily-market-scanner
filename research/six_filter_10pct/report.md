# Six-Filter ±10% Follow-Through Research

Analysis end date: **2026-10-18**.

Method: for each market and each of the six scanner categories, take the first day a symbol appeared in that category and use that published scanner `current_price` as the signal price. To avoid look-ahead, performance starts from the **next trading session**. A +10% hit occurs when a later daily High reaches 110% of signal price; a -10% hit occurs when a later daily Low reaches 90% of signal price. One symbol may appear in multiple categories because the goal is to compare stages independently.

## Overall comparison

| Filter | Signals | +10% | -10% | Both | +10% rate | -10% rate | 10-session +10% | 10-session -10% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Entry Marker | 113 | 20 | 45 | 3 | 17.70% | 39.82% | 9.09% | 13.13% |
| High Conviction Entry | 54 | 13 | 22 | 1 | 24.07% | 40.74% | 16.67% | 10.42% |
| Double Reclaim READY NOW | 326 | 49 | 132 | 11 | 15.03% | 40.49% | 9.47% | 18.95% |
| Reclaim Breakout | 569 | 91 | 249 | 18 | 16.05% | 43.92% | 7.59% | 16.73% |
| Pre-Entry Watch | 1059 | 203 | 468 | 40 | 19.33% | 44.57% | 9.15% | 12.74% |
| Pre-Breakout Compression | 365 | 35 | 117 | 2 | 9.67% | 32.32% | 2.43% | 10.33% |

## Entry Marker

### 🟢 Reached +10% — 20

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-31 | 30 | 26.27% | -14.87% | 2026-09-07 | 2026-10-15 | UP10_FIRST |
| US | [PBR](https://www.tradingview.com/chart/?symbol=PBR) | 2026-09-22 | 20.75 | 25.78% | -2.65% | 2026-10-05 | — | UP10_ONLY |
| US | [DHT](https://www.tradingview.com/chart/?symbol=DHT) | 2026-09-24 | 21.68 | 24.15% | -1.64% | 2026-10-05 | — | UP10_ONLY |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| US | [MPC](https://www.tradingview.com/chart/?symbol=MPC) | 2026-09-25 | 393.1 | 23.45% | -3.32% | 2026-10-05 | — | UP10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [GMAB](https://www.tradingview.com/chart/?symbol=GMAB) | 2026-08-31 | 33.16 | 21.14% | -2.86% | 2026-10-05 | — | UP10_ONLY |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-09-24 | 104.8 | 20.46% | -1.27% | 2026-10-02 | — | UP10_ONLY |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-08-23 | 25.99 | 18.28% | -9.47% | 2026-09-16 | — | UP10_ONLY |
| US | [A](https://www.tradingview.com/chart/?symbol=A) | 2026-09-02 | 151.3 | 17.26% | -6.81% | 2026-09-22 | — | UP10_ONLY |
| US | [SNOW](https://www.tradingview.com/chart/?symbol=SNOW) | 2026-08-23 | 332.8 | 15.55% | -9.18% | 2026-09-03 | — | UP10_ONLY |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-09-02 | 172.9 | 15.01% | -8.95% | 2026-09-24 | — | UP10_ONLY |
| US | [CRL](https://www.tradingview.com/chart/?symbol=CRL) | 2026-09-24 | 294.4 | 13.22% | -3.32% | 2026-10-06 | — | UP10_ONLY |
| US | [ESTC](https://www.tradingview.com/chart/?symbol=ESTC) | 2026-09-21 | 89.7 | 13.03% | -5.66% | 2026-10-12 | — | UP10_ONLY |
| HK | [2359](https://www.tradingview.com/chart/?symbol=HKEX%3A2359) | 2026-09-08 | 194.9 | 12.47% | -5.08% | 2026-09-30 | — | UP10_ONLY |
| US | [BP](https://www.tradingview.com/chart/?symbol=BP) | 2026-10-02 | 44.79 | 12.23% | -1.56% | 2026-10-16 | — | UP10_ONLY |
| US | [URBN](https://www.tradingview.com/chart/?symbol=URBN) | 2026-09-07 | 80.95 | 11.91% | -9.05% | 2026-10-16 | — | UP10_ONLY |
| US | [HTFL](https://www.tradingview.com/chart/?symbol=HTFL) | 2026-09-24 | 48.57 | 11.84% | -4.26% | 2026-10-06 | — | UP10_ONLY |
| US | [EQH](https://www.tradingview.com/chart/?symbol=EQH) | 2026-08-26 | 49.87 | 10.74% | -1.62% | 2026-09-17 | — | UP10_ONLY |
| US | [WAT](https://www.tradingview.com/chart/?symbol=WAT) | 2026-08-23 | 410.7 | 10.68% | -4.32% | 2026-10-06 | — | UP10_ONLY |

### 🔴 Reached -10% — 45

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [QMCO](https://www.tradingview.com/chart/?symbol=QMCO) | 2026-10-09 | 30.41 | -1.41% | -39.43% | — | 2026-10-12 | DOWN10_ONLY |
| US | [GEN](https://www.tradingview.com/chart/?symbol=GEN) | 2026-08-23 | 28.94 | 9.36% | -29.72% | — | 2026-09-24 | DOWN10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| US | [LPLA](https://www.tradingview.com/chart/?symbol=LPLA) | 2026-08-28 | 370.7 | 0.60% | -20.26% | — | 2026-09-16 | DOWN10_ONLY |
| US | [ALSN](https://www.tradingview.com/chart/?symbol=ALSN) | 2026-09-04 | 131.2 | 0.90% | -19.91% | — | 2026-09-16 | DOWN10_ONLY |
| US | [OII](https://www.tradingview.com/chart/?symbol=OII) | 2026-09-02 | 51.66 | 1.53% | -19.88% | — | 2026-09-14 | DOWN10_ONLY |
| US | [PLSE](https://www.tradingview.com/chart/?symbol=PLSE) | 2026-10-09 | 53.97 | 0.03% | -19.73% | — | 2026-10-13 | DOWN10_ONLY |
| US | [JAZZ](https://www.tradingview.com/chart/?symbol=JAZZ) | 2026-08-23 | 254.1 | 4.83% | -18.08% | — | 2026-10-07 | DOWN10_ONLY |
| US | [WT](https://www.tradingview.com/chart/?symbol=WT) | 2026-10-05 | 24.46 | 0.90% | -17.62% | — | 2026-10-13 | DOWN10_ONLY |
| US | [RVMD](https://www.tradingview.com/chart/?symbol=RVMD) | 2026-09-03 | 210.9 | 1.01% | -16.58% | — | 2026-09-18 | DOWN10_ONLY |
| US | [UBS](https://www.tradingview.com/chart/?symbol=UBS) | 2026-09-03 | 55.7 | 0.00% | -16.45% | — | 2026-09-16 | DOWN10_ONLY |
| US | [OMF](https://www.tradingview.com/chart/?symbol=OMF) | 2026-09-03 | 64.59 | 1.18% | -16.33% | — | 2026-09-23 | DOWN10_ONLY |
| US | [GPN](https://www.tradingview.com/chart/?symbol=GPN) | 2026-09-02 | 92.82 | 2.25% | -16.05% | — | 2026-09-23 | DOWN10_ONLY |
| US | [ATI](https://www.tradingview.com/chart/?symbol=ATI) | 2026-09-04 | 210.6 | -0.13% | -15.95% | — | 2026-09-14 | DOWN10_ONLY |
| US | [FHI](https://www.tradingview.com/chart/?symbol=FHI) | 2026-08-23 | 63.69 | 3.36% | -15.50% | — | 2026-09-16 | DOWN10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-31 | 30 | 26.27% | -14.87% | 2026-09-07 | 2026-10-15 | UP10_FIRST |
| US | [CAI](https://www.tradingview.com/chart/?symbol=CAI) | 2026-10-05 | 30.38 | 7.18% | -14.85% | — | 2026-10-06 | DOWN10_ONLY |
| US | [HRMY](https://www.tradingview.com/chart/?symbol=HRMY) | 2026-09-21 | 42.08 | 0.69% | -14.47% | — | 2026-10-12 | DOWN10_ONLY |
| US | [BBVA](https://www.tradingview.com/chart/?symbol=BBVA) | 2026-09-07 | 29.52 | -1.48% | -14.18% | — | 2026-10-01 | DOWN10_ONLY |
| US | [SWK](https://www.tradingview.com/chart/?symbol=SWK) | 2026-08-26 | 99.77 | 0.21% | -14.09% | — | 2026-09-10 | DOWN10_ONLY |
| US | [COF](https://www.tradingview.com/chart/?symbol=COF) | 2026-09-03 | 220.5 | 0.13% | -13.92% | — | 2026-09-23 | DOWN10_ONLY |
| US | [DRI](https://www.tradingview.com/chart/?symbol=DRI) | 2026-08-23 | 221.6 | 1.73% | -13.76% | — | 2026-09-25 | DOWN10_ONLY |
| US | [MRSH](https://www.tradingview.com/chart/?symbol=MRSH) | 2026-08-28 | 192.6 | -0.57% | -13.69% | — | 2026-09-17 | DOWN10_ONLY |
| US | [MHK](https://www.tradingview.com/chart/?symbol=MHK) | 2026-09-04 | 133.6 | -0.26% | -13.46% | — | 2026-09-21 | DOWN10_ONLY |
| Canada | [MG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMG) | 2026-08-23 | 100.5 | -0.97% | -13.20% | — | 2026-08-26 | DOWN10_ONLY |
| US | [GM](https://www.tradingview.com/chart/?symbol=GM) | 2026-08-23 | 87.94 | 0.17% | -13.07% | — | 2026-09-30 | DOWN10_ONLY |
| US | [LNC](https://www.tradingview.com/chart/?symbol=LNC) | 2026-09-02 | 44.12 | 2.89% | -12.84% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-26 | 176.7 | 2.30% | -12.77% | — | 2026-09-22 | DOWN10_ONLY |
| US | [ANET](https://www.tradingview.com/chart/?symbol=ANET) | 2026-08-26 | 202.3 | 7.48% | -12.61% | — | 2026-09-03 | DOWN10_ONLY |
| US | [OKE](https://www.tradingview.com/chart/?symbol=OKE) | 2026-09-02 | 96.02 | 3.42% | -12.36% | — | 2026-09-29 | DOWN10_ONLY |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-08-23 | 104.2 | 3.15% | -12.09% | — | 2026-10-07 | DOWN10_ONLY |
| US | [MRX](https://www.tradingview.com/chart/?symbol=MRX) | 2026-09-03 | 75.72 | 4.48% | -11.46% | — | 2026-09-16 | DOWN10_ONLY |
| US | [WES](https://www.tradingview.com/chart/?symbol=WES) | 2026-09-04 | 49.55 | 0.70% | -11.35% | — | 2026-09-29 | DOWN10_ONLY |
| US | [CSX](https://www.tradingview.com/chart/?symbol=CSX) | 2026-08-23 | 51.59 | 0.80% | -11.25% | — | 2026-09-21 | DOWN10_ONLY |
| US | [TTEK](https://www.tradingview.com/chart/?symbol=TTEK) | 2026-09-02 | 35.9 | 3.82% | -10.81% | — | 2026-10-07 | DOWN10_ONLY |
| US | [IMAX](https://www.tradingview.com/chart/?symbol=IMAX) | 2026-09-21 | 54.05 | 6.80% | -10.76% | — | 2026-10-08 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-08-26 | 34.81 | 9.65% | -10.63% | — | 2026-09-28 | DOWN10_ONLY |
| US | [BWIN](https://www.tradingview.com/chart/?symbol=BWIN) | 2026-09-02 | 31.04 | 5.38% | -10.62% | — | 2026-09-09 | DOWN10_ONLY |
| US | [PRU](https://www.tradingview.com/chart/?symbol=PRU) | 2026-09-03 | 123.2 | 0.29% | -10.23% | — | 2026-10-02 | DOWN10_ONLY |
| US | [BF-B](https://www.tradingview.com/chart/?symbol=BF-B) | 2026-08-23 | 28.43 | 2.95% | -10.13% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SCI](https://www.tradingview.com/chart/?symbol=SCI) | 2026-08-25 | 84.46 | 1.57% | -10.11% | — | 2026-10-05 | DOWN10_ONLY |
| US | [DE](https://www.tradingview.com/chart/?symbol=DE) | 2026-10-02 | 687.3 | 0.81% | -10.08% | — | 2026-10-12 | DOWN10_ONLY |
| US | [RPRX](https://www.tradingview.com/chart/?symbol=RPRX) | 2026-08-23 | 61.3 | 5.02% | -10.07% | — | 2026-10-08 | DOWN10_ONLY |
| US | [ING](https://www.tradingview.com/chart/?symbol=ING) | 2026-09-25 | 36.52 | 0.42% | -10.01% | — | 2026-10-15 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **17**; -10%-only sample: **42**.
- +10%-only common candles: BULL_CANDLE (7), BEAR_CANDLE (5), STRONG_BULL_CANDLE (3), BULLISH_ENGULFING (1).
- -10%-only common candles: BULL_CANDLE (25), STRONG_BULL_CANDLE (9), BULLISH_ENGULFING (5), HAMMER (2).
- Median RS: +10%-only **28.33** vs -10%-only **19.00**.
- Median % below 52w high: +10%-only **6.99** vs -10%-only **4.57**.
- Median breakout age: +10%-only **10.00** vs -10%-only **14.00**.
- Median quality score: +10%-only **6.00** vs -10%-only **5.00**.
- Median congestion score: +10%-only **1.00** vs -10%-only **2.00**.

## High Conviction Entry

### 🟢 Reached +10% — 13

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [PBR](https://www.tradingview.com/chart/?symbol=PBR) | 2026-09-22 | 20.75 | 25.78% | -2.65% | 2026-10-05 | — | UP10_ONLY |
| US | [DHT](https://www.tradingview.com/chart/?symbol=DHT) | 2026-09-24 | 21.68 | 24.15% | -1.64% | 2026-10-05 | — | UP10_ONLY |
| US | [MPC](https://www.tradingview.com/chart/?symbol=MPC) | 2026-09-25 | 393.1 | 23.45% | -3.32% | 2026-10-05 | — | UP10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-09-24 | 104.8 | 20.46% | -1.27% | 2026-10-02 | — | UP10_ONLY |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-08-23 | 25.99 | 18.28% | -9.47% | 2026-09-16 | — | UP10_ONLY |
| US | [SNOW](https://www.tradingview.com/chart/?symbol=SNOW) | 2026-08-23 | 332.8 | 15.55% | -9.18% | 2026-09-03 | — | UP10_ONLY |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-09-02 | 172.9 | 15.01% | -8.95% | 2026-09-24 | — | UP10_ONLY |
| US | [CRL](https://www.tradingview.com/chart/?symbol=CRL) | 2026-09-24 | 294.4 | 13.22% | -3.32% | 2026-10-06 | — | UP10_ONLY |
| US | [BP](https://www.tradingview.com/chart/?symbol=BP) | 2026-10-02 | 44.79 | 12.23% | -1.56% | 2026-10-16 | — | UP10_ONLY |
| US | [HTFL](https://www.tradingview.com/chart/?symbol=HTFL) | 2026-09-24 | 48.57 | 11.84% | -4.26% | 2026-10-06 | — | UP10_ONLY |
| US | [EQH](https://www.tradingview.com/chart/?symbol=EQH) | 2026-08-26 | 49.87 | 10.74% | -1.62% | 2026-09-17 | — | UP10_ONLY |
| US | [WAT](https://www.tradingview.com/chart/?symbol=WAT) | 2026-08-23 | 410.7 | 10.68% | -4.32% | 2026-10-06 | — | UP10_ONLY |

### 🔴 Reached -10% — 22

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [GEN](https://www.tradingview.com/chart/?symbol=GEN) | 2026-08-23 | 28.94 | 9.36% | -29.72% | — | 2026-09-24 | DOWN10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [LPLA](https://www.tradingview.com/chart/?symbol=LPLA) | 2026-08-28 | 370.7 | 0.60% | -20.26% | — | 2026-09-16 | DOWN10_ONLY |
| US | [OII](https://www.tradingview.com/chart/?symbol=OII) | 2026-09-02 | 51.66 | 1.53% | -19.88% | — | 2026-09-14 | DOWN10_ONLY |
| US | [PLSE](https://www.tradingview.com/chart/?symbol=PLSE) | 2026-10-09 | 53.97 | 0.03% | -19.73% | — | 2026-10-13 | DOWN10_ONLY |
| US | [RVMD](https://www.tradingview.com/chart/?symbol=RVMD) | 2026-09-03 | 210.9 | 1.01% | -16.58% | — | 2026-09-18 | DOWN10_ONLY |
| US | [GPN](https://www.tradingview.com/chart/?symbol=GPN) | 2026-09-02 | 92.82 | 2.25% | -16.05% | — | 2026-09-23 | DOWN10_ONLY |
| US | [CAI](https://www.tradingview.com/chart/?symbol=CAI) | 2026-10-05 | 30.38 | 7.18% | -14.85% | — | 2026-10-06 | DOWN10_ONLY |
| US | [HRMY](https://www.tradingview.com/chart/?symbol=HRMY) | 2026-09-21 | 42.08 | 0.69% | -14.47% | — | 2026-10-12 | DOWN10_ONLY |
| US | [BBVA](https://www.tradingview.com/chart/?symbol=BBVA) | 2026-09-07 | 29.52 | -1.48% | -14.18% | — | 2026-10-01 | DOWN10_ONLY |
| US | [SWK](https://www.tradingview.com/chart/?symbol=SWK) | 2026-08-26 | 99.77 | 0.21% | -14.09% | — | 2026-09-10 | DOWN10_ONLY |
| US | [DRI](https://www.tradingview.com/chart/?symbol=DRI) | 2026-09-02 | 220.1 | 0.59% | -13.15% | — | 2026-09-25 | DOWN10_ONLY |
| US | [LNC](https://www.tradingview.com/chart/?symbol=LNC) | 2026-09-02 | 44.12 | 2.89% | -12.84% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-26 | 176.7 | 2.30% | -12.77% | — | 2026-09-22 | DOWN10_ONLY |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-08-23 | 104.2 | 3.15% | -12.09% | — | 2026-10-07 | DOWN10_ONLY |
| US | [MRX](https://www.tradingview.com/chart/?symbol=MRX) | 2026-09-03 | 75.72 | 4.48% | -11.46% | — | 2026-09-16 | DOWN10_ONLY |
| US | [CSX](https://www.tradingview.com/chart/?symbol=CSX) | 2026-08-23 | 51.59 | 0.80% | -11.25% | — | 2026-09-21 | DOWN10_ONLY |
| US | [IMAX](https://www.tradingview.com/chart/?symbol=IMAX) | 2026-09-21 | 54.05 | 6.80% | -10.76% | — | 2026-10-08 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-08-26 | 34.81 | 9.65% | -10.63% | — | 2026-09-28 | DOWN10_ONLY |
| US | [BWIN](https://www.tradingview.com/chart/?symbol=BWIN) | 2026-09-02 | 31.04 | 5.38% | -10.62% | — | 2026-09-09 | DOWN10_ONLY |
| US | [PRU](https://www.tradingview.com/chart/?symbol=PRU) | 2026-09-03 | 123.2 | 0.29% | -10.23% | — | 2026-10-02 | DOWN10_ONLY |
| US | [ING](https://www.tradingview.com/chart/?symbol=ING) | 2026-09-25 | 36.52 | 0.42% | -10.01% | — | 2026-10-15 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **12**; -10%-only sample: **21**.
- +10%-only common candles: BEAR_CANDLE (5), BULL_CANDLE (4), BULLISH_ENGULFING (1), DOJI (1).
- -10%-only common candles: BULL_CANDLE (14), STRONG_BULL_CANDLE (4), BULLISH_ENGULFING (3).
- Median RS: +10%-only **27.70** vs -10%-only **27.27**.
- Median % below 52w high: +10%-only **6.31** vs -10%-only **4.10**.
- Median breakout age: +10%-only **11.00** vs -10%-only **14.00**.
- Median quality score: +10%-only **6.50** vs -10%-only **7.00**.
- Median congestion score: +10%-only **1.00** vs -10%-only **2.00**.

## Double Reclaim READY NOW

### 🟢 Reached +10% — 49

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [GRAL](https://www.tradingview.com/chart/?symbol=GRAL) | 2026-09-09 | 77.43 | 115.00% | -5.13% | 2026-09-21 | — | UP10_ONLY |
| US | [EFOR](https://www.tradingview.com/chart/?symbol=EFOR) | 2026-09-02 | 30.88 | 30.60% | -3.79% | 2026-09-14 | — | UP10_ONLY |
| US | [RVTY](https://www.tradingview.com/chart/?symbol=RVTY) | 2026-09-14 | 128.5 | 29.36% | 0.12% | 2026-09-16 | — | UP10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-31 | 30 | 26.27% | -14.87% | 2026-09-07 | 2026-10-15 | UP10_FIRST |
| US | [DXC](https://www.tradingview.com/chart/?symbol=DXC) | 2026-09-08 | 11.22 | 26.06% | -9.76% | 2026-10-08 | — | UP10_ONLY |
| US | [PBR](https://www.tradingview.com/chart/?symbol=PBR) | 2026-09-22 | 20.75 | 25.78% | -2.65% | 2026-10-05 | — | UP10_ONLY |
| US | [DHT](https://www.tradingview.com/chart/?symbol=DHT) | 2026-09-24 | 21.68 | 24.15% | -1.64% | 2026-10-05 | — | UP10_ONLY |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| HK | [2245](https://www.tradingview.com/chart/?symbol=HKEX%3A2245) | 2026-09-18 | 17.43 | 24.04% | -5.05% | 2026-09-23 | — | UP10_ONLY |
| US | [IDT](https://www.tradingview.com/chart/?symbol=IDT) | 2026-08-20 | 67.08 | 24.02% | -2.00% | 2026-09-29 | — | UP10_ONLY |
| US | [MPC](https://www.tradingview.com/chart/?symbol=MPC) | 2026-09-25 | 393.1 | 23.45% | -3.32% | 2026-10-05 | — | UP10_ONLY |
| US | [GTLB](https://www.tradingview.com/chart/?symbol=GTLB) | 2026-09-30 | 47.27 | 22.47% | 0.15% | 2026-10-06 | — | UP10_ONLY |
| US | [BMNR](https://www.tradingview.com/chart/?symbol=BMNR) | 2026-09-15 | 23.61 | 22.26% | -12.94% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [NEOG](https://www.tradingview.com/chart/?symbol=NEOG) | 2026-08-28 | 11.67 | 22.19% | -4.63% | 2026-09-16 | — | UP10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-09-22 | 103.9 | 21.57% | -4.26% | 2026-09-30 | — | UP10_ONLY |
| US | [CRVL](https://www.tradingview.com/chart/?symbol=CRVL) | 2026-09-11 | 69.37 | 20.18% | -0.32% | 2026-10-05 | — | UP10_ONLY |
| US | [CRL](https://www.tradingview.com/chart/?symbol=CRL) | 2026-09-17 | 281.7 | 18.33% | -2.05% | 2026-10-05 | — | UP10_ONLY |
| US | [PRGO](https://www.tradingview.com/chart/?symbol=PRGO) | 2026-09-21 | 14.13 | 18.05% | -2.62% | 2026-09-25 | — | UP10_ONLY |
| US | [TEAM](https://www.tradingview.com/chart/?symbol=TEAM) | 2026-10-01 | 189.9 | 17.80% | -1.79% | 2026-10-12 | — | UP10_ONLY |
| US | [GMAB](https://www.tradingview.com/chart/?symbol=GMAB) | 2026-09-15 | 34.14 | 17.66% | -1.22% | 2026-10-05 | — | UP10_ONLY |
| US | [A](https://www.tradingview.com/chart/?symbol=A) | 2026-09-02 | 151.3 | 17.26% | -6.81% | 2026-09-22 | — | UP10_ONLY |
| US | [PGY](https://www.tradingview.com/chart/?symbol=PGY) | 2026-08-20 | 20.23 | 17.05% | -20.42% | 2026-08-24 | 2026-09-24 | UP10_FIRST |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-09-01 | 170 | 16.97% | -7.40% | 2026-09-22 | — | UP10_ONLY |
| Canada | [SGY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASGY) | 2026-08-26 | 10.94 | 15.64% | -1.29% | 2026-09-10 | — | UP10_ONLY |
| HK | [2005](https://www.tradingview.com/chart/?symbol=HKEX%3A2005) | 2026-08-25 | 2.465 | 15.62% | -0.05% | 2026-08-28 | — | UP10_ONLY |
| US | [SNOW](https://www.tradingview.com/chart/?symbol=SNOW) | 2026-08-23 | 332.8 | 15.55% | -9.18% | 2026-09-03 | — | UP10_ONLY |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-09-15 | 26.68 | 15.22% | -10.23% | 2026-09-24 | 2026-10-16 | UP10_FIRST |
| US | [JOYY](https://www.tradingview.com/chart/?symbol=JOYY) | 2026-08-20 | 73.84 | 14.78% | -3.30% | 2026-10-06 | — | UP10_ONLY |
| US | [ADMA](https://www.tradingview.com/chart/?symbol=ADMA) | 2026-09-02 | 9.525 | 14.54% | -10.34% | 2026-10-09 | 2026-09-15 | DOWN10_FIRST |
| US | [ESTC](https://www.tradingview.com/chart/?symbol=ESTC) | 2026-09-29 | 88.82 | 14.15% | 0.05% | 2026-10-06 | — | UP10_ONLY |
| HK | [2359](https://www.tradingview.com/chart/?symbol=HKEX%3A2359) | 2026-09-02 | 193.1 | 13.52% | -4.19% | 2026-09-29 | — | UP10_ONLY |
| US | [W](https://www.tradingview.com/chart/?symbol=W) | 2026-09-08 | 99.95 | 13.16% | -5.70% | 2026-10-15 | — | UP10_ONLY |
| HK | [0517](https://www.tradingview.com/chart/?symbol=HKEX%3A517) | 2026-09-17 | 6.37 | 12.24% | -1.33% | 2026-10-09 | — | UP10_ONLY |
| US | [BP](https://www.tradingview.com/chart/?symbol=BP) | 2026-10-02 | 44.79 | 12.23% | -1.56% | 2026-10-16 | — | UP10_ONLY |
| HK | [0144](https://www.tradingview.com/chart/?symbol=HKEX%3A144) | 2026-08-25 | 16.13 | 12.03% | -4.60% | 2026-10-14 | — | UP10_ONLY |
| US | [NCNO](https://www.tradingview.com/chart/?symbol=NCNO) | 2026-08-26 | 21.54 | 11.84% | -17.99% | 2026-08-28 | 2026-09-23 | UP10_FIRST |
| US | [HTFL](https://www.tradingview.com/chart/?symbol=HTFL) | 2026-09-24 | 48.57 | 11.84% | -4.26% | 2026-10-06 | — | UP10_ONLY |
| US | [BWLP](https://www.tradingview.com/chart/?symbol=BWLP) | 2026-09-08 | 23.91 | 11.71% | -0.36% | 2026-09-17 | — | UP10_ONLY |
| US | [GO](https://www.tradingview.com/chart/?symbol=GO) | 2026-10-07 | 11.94 | 11.39% | -2.14% | 2026-10-15 | — | UP10_ONLY |
| US | [UGP](https://www.tradingview.com/chart/?symbol=UGP) | 2026-10-02 | 7.45 | 11.14% | 1.61% | 2026-10-05 | — | UP10_ONLY |
| US | [OLLI](https://www.tradingview.com/chart/?symbol=OLLI) | 2026-10-12 | 86.43 | 10.81% | 1.62% | 2026-10-15 | — | UP10_ONLY |
| HK | [0656](https://www.tradingview.com/chart/?symbol=HKEX%3A656) | 2026-08-21 | 5.115 | 10.75% | -11.83% | 2026-09-01 | 2026-10-08 | UP10_FIRST |
| Canada | [VLE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AVLE) | 2026-10-02 | 15.35 | 10.75% | -2.48% | 2026-10-14 | — | UP10_ONLY |
| US | [EQH](https://www.tradingview.com/chart/?symbol=EQH) | 2026-08-26 | 49.87 | 10.74% | -1.62% | 2026-09-17 | — | UP10_ONLY |
| US | [WAT](https://www.tradingview.com/chart/?symbol=WAT) | 2026-08-23 | 410.7 | 10.68% | -4.32% | 2026-10-06 | — | UP10_ONLY |
| US | [NUTX](https://www.tradingview.com/chart/?symbol=NUTX) | 2026-09-24 | 204.7 | 10.51% | -10.63% | 2026-10-05 | 2026-10-15 | UP10_FIRST |
| HK | [2276](https://www.tradingview.com/chart/?symbol=HKEX%3A2276) | 2026-09-21 | 43.92 | 10.38% | -27.00% | 2026-09-22 | 2026-09-25 | UP10_FIRST |
| US | [IOT](https://www.tradingview.com/chart/?symbol=IOT) | 2026-09-04 | 40.19 | 10.00% | -9.43% | 2026-10-05 | — | UP10_ONLY |

### 🔴 Reached -10% — 132

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [QMCO](https://www.tradingview.com/chart/?symbol=QMCO) | 2026-10-09 | 30.41 | -1.41% | -39.43% | — | 2026-10-12 | DOWN10_ONLY |
| HK | [2225](https://www.tradingview.com/chart/?symbol=HKEX%3A2225) | 2026-09-23 | 5.83 | 1.54% | -35.33% | — | 2026-09-28 | DOWN10_ONLY |
| US | [PCG](https://www.tradingview.com/chart/?symbol=PCG) | 2026-08-24 | 18.1 | 1.24% | -35.24% | — | 2026-08-28 | DOWN10_ONLY |
| US | [ALKT](https://www.tradingview.com/chart/?symbol=ALKT) | 2026-08-31 | 20.38 | 2.40% | -35.21% | — | 2026-09-10 | DOWN10_ONLY |
| US | [GPK](https://www.tradingview.com/chart/?symbol=GPK) | 2026-08-20 | 11.63 | 3.09% | -29.84% | — | 2026-09-03 | DOWN10_ONLY |
| US | [GEN](https://www.tradingview.com/chart/?symbol=GEN) | 2026-08-23 | 28.94 | 9.36% | -29.72% | — | 2026-09-24 | DOWN10_ONLY |
| US | [VOR](https://www.tradingview.com/chart/?symbol=VOR) | 2026-09-02 | 24.78 | 4.92% | -29.30% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [FF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFF) | 2026-09-14 | 0.9 | 2.78% | -28.89% | — | 2026-09-24 | DOWN10_ONLY |
| US | [CG](https://www.tradingview.com/chart/?symbol=CG) | 2026-08-23 | 49.37 | 1.92% | -28.28% | — | 2026-09-09 | DOWN10_ONLY |
| US | [CHWY](https://www.tradingview.com/chart/?symbol=CHWY) | 2026-09-02 | 24.17 | 5.01% | -27.27% | — | 2026-09-09 | DOWN10_ONLY |
| US | [GLIBA](https://www.tradingview.com/chart/?symbol=GLIBA) | 2026-09-02 | 26.73 | 0.75% | -27.24% | — | 2026-09-18 | DOWN10_ONLY |
| HK | [2276](https://www.tradingview.com/chart/?symbol=HKEX%3A2276) | 2026-09-21 | 43.92 | 10.38% | -27.00% | 2026-09-22 | 2026-09-25 | UP10_FIRST |
| US | [TRUP](https://www.tradingview.com/chart/?symbol=TRUP) | 2026-08-26 | 30.18 | 1.56% | -26.94% | — | 2026-09-08 | DOWN10_ONLY |
| US | [EXK](https://www.tradingview.com/chart/?symbol=EXK) | 2026-09-22 | 10.51 | -3.52% | -26.93% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [ELE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AELE) | 2026-09-17 | 30.19 | 4.51% | -26.90% | — | 2026-10-01 | DOWN10_ONLY |
| US | [MOS](https://www.tradingview.com/chart/?symbol=MOS) | 2026-09-14 | 25.06 | 2.79% | -26.54% | — | 2026-09-28 | DOWN10_ONLY |
| US | [GLIBK](https://www.tradingview.com/chart/?symbol=GLIBK) | 2026-09-04 | 26.26 | 0.21% | -26.09% | — | 2026-09-18 | DOWN10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| Canada | [EDR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEDR) | 2026-09-22 | 14.77 | -3.45% | -25.86% | — | 2026-09-23 | DOWN10_ONLY |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| US | [ZBIO](https://www.tradingview.com/chart/?symbol=ZBIO) | 2026-08-24 | 31.67 | 7.33% | -23.43% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [AC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AAC) | 2026-09-01 | 28.05 | 3.74% | -23.28% | — | 2026-10-02 | DOWN10_ONLY |
| US | [KKR](https://www.tradingview.com/chart/?symbol=KKR) | 2026-09-03 | 109.8 | -0.36% | -23.27% | — | 2026-09-16 | DOWN10_ONLY |
| US | [JBS](https://www.tradingview.com/chart/?symbol=JBS) | 2026-08-23 | 13.82 | 2.42% | -23.25% | — | 2026-09-11 | DOWN10_ONLY |
| US | [INTU](https://www.tradingview.com/chart/?symbol=INTU) | 2026-09-14 | 339.1 | -0.52% | -23.01% | — | 2026-09-18 | DOWN10_ONLY |
| HK | [9858](https://www.tradingview.com/chart/?symbol=HKEX%3A9858) | 2026-09-01 | 4.315 | 7.18% | -22.60% | — | 2026-10-02 | DOWN10_ONLY |
| HK | [1952](https://www.tradingview.com/chart/?symbol=HKEX%3A1952) | 2026-09-08 | 33.2 | 3.07% | -22.59% | — | 2026-09-10 | DOWN10_ONLY |
| US | [CNS](https://www.tradingview.com/chart/?symbol=CNS) | 2026-08-24 | 83.2 | 2.04% | -21.78% | — | 2026-09-11 | DOWN10_ONLY |
| US | [EAT](https://www.tradingview.com/chart/?symbol=EAT) | 2026-09-01 | 234 | 1.10% | -21.61% | — | 2026-09-11 | DOWN10_ONLY |
| US | [INSM](https://www.tradingview.com/chart/?symbol=INSM) | 2026-08-31 | 121.8 | 7.38% | -21.41% | — | 2026-10-01 | DOWN10_ONLY |
| US | [SE](https://www.tradingview.com/chart/?symbol=SE) | 2026-08-20 | 117.2 | 5.56% | -21.30% | — | 2026-09-14 | DOWN10_ONLY |
| US | [NU](https://www.tradingview.com/chart/?symbol=NU) | 2026-09-02 | 15.39 | 5.16% | -21.20% | — | 2026-09-16 | DOWN10_ONLY |
| US | [PAY](https://www.tradingview.com/chart/?symbol=PAY) | 2026-09-14 | 37.08 | 1.00% | -21.04% | — | 2026-09-22 | DOWN10_ONLY |
| Canada | [RIO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIO) | 2026-09-24 | 3.6 | 1.94% | -20.83% | — | 2026-09-30 | DOWN10_ONLY |
| US | [PCOR](https://www.tradingview.com/chart/?symbol=PCOR) | 2026-09-02 | 59.52 | 4.22% | -20.58% | — | 2026-09-10 | DOWN10_ONLY |
| US | [PGY](https://www.tradingview.com/chart/?symbol=PGY) | 2026-08-20 | 20.23 | 17.05% | -20.42% | 2026-08-24 | 2026-09-24 | UP10_FIRST |
| US | [LPLA](https://www.tradingview.com/chart/?symbol=LPLA) | 2026-08-28 | 370.7 | 0.60% | -20.26% | — | 2026-09-16 | DOWN10_ONLY |
| US | [JHX](https://www.tradingview.com/chart/?symbol=JHX) | 2026-09-03 | 29.64 | 6.04% | -19.91% | — | 2026-09-15 | DOWN10_ONLY |
| US | [OII](https://www.tradingview.com/chart/?symbol=OII) | 2026-09-02 | 51.66 | 1.53% | -19.88% | — | 2026-09-14 | DOWN10_ONLY |
| US | [PLSE](https://www.tradingview.com/chart/?symbol=PLSE) | 2026-09-18 | 53.92 | 5.23% | -19.66% | — | 2026-10-02 | DOWN10_ONLY |
| HK | [8279](https://www.tradingview.com/chart/?symbol=HKEX%3A8279) | 2026-09-18 | 1.415 | -0.35% | -19.43% | — | 2026-09-21 | DOWN10_ONLY |
| US | [BMRN](https://www.tradingview.com/chart/?symbol=BMRN) | 2026-08-25 | 66.12 | 2.39% | -18.48% | — | 2026-09-28 | DOWN10_ONLY |
| US | [LDOS](https://www.tradingview.com/chart/?symbol=LDOS) | 2026-08-26 | 137.4 | 3.33% | -18.46% | — | 2026-09-22 | DOWN10_ONLY |
| HK | [1184](https://www.tradingview.com/chart/?symbol=HKEX%3A1184) | 2026-09-22 | 8.26 | 0.48% | -18.28% | — | 2026-10-14 | DOWN10_ONLY |
| US | [JAZZ](https://www.tradingview.com/chart/?symbol=JAZZ) | 2026-08-23 | 254.1 | 4.83% | -18.08% | — | 2026-10-07 | DOWN10_ONLY |
| US | [NCNO](https://www.tradingview.com/chart/?symbol=NCNO) | 2026-08-26 | 21.54 | 11.84% | -17.99% | 2026-08-28 | 2026-09-23 | UP10_FIRST |
| US | [MT](https://www.tradingview.com/chart/?symbol=MT) | 2026-09-01 | 73.34 | 8.64% | -17.73% | — | 2026-10-01 | DOWN10_ONLY |
| US | [FLR](https://www.tradingview.com/chart/?symbol=FLR) | 2026-09-18 | 54.91 | 1.99% | -17.31% | — | 2026-09-28 | DOWN10_ONLY |
| US | [CCC](https://www.tradingview.com/chart/?symbol=CCC) | 2026-09-04 | 7.515 | 5.26% | -16.97% | — | 2026-09-09 | DOWN10_ONLY |
| US | [WT](https://www.tradingview.com/chart/?symbol=WT) | 2026-09-10 | 24.27 | 3.15% | -16.96% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [CGG.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACGG) | 2026-09-15 | 44.8 | 9.35% | -16.87% | — | 2026-09-24 | DOWN10_ONLY |
| US | [SEPN](https://www.tradingview.com/chart/?symbol=SEPN) | 2026-08-25 | 41.29 | 0.16% | -16.78% | — | 2026-09-03 | DOWN10_ONLY |
| US | [LYFT](https://www.tradingview.com/chart/?symbol=LYFT) | 2026-09-02 | 17.35 | 3.63% | -16.74% | — | 2026-09-09 | DOWN10_ONLY |
| US | [GTM](https://www.tradingview.com/chart/?symbol=GTM) | 2026-09-14 | 4.195 | 3.93% | -16.57% | — | 2026-09-25 | DOWN10_ONLY |
| US | [TPC](https://www.tradingview.com/chart/?symbol=TPC) | 2026-09-08 | 89.49 | 1.45% | -16.40% | — | 2026-10-14 | DOWN10_ONLY |
| US | [STT](https://www.tradingview.com/chart/?symbol=STT) | 2026-08-23 | 187.1 | 4.16% | -16.36% | — | 2026-10-14 | DOWN10_ONLY |
| US | [RVMD](https://www.tradingview.com/chart/?symbol=RVMD) | 2026-09-01 | 209.9 | 1.49% | -16.19% | — | 2026-09-18 | DOWN10_ONLY |
| Canada | [ALS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALS) | 2026-09-25 | 66.77 | 0.34% | -16.13% | — | 2026-10-14 | DOWN10_ONLY |
| US | [CART](https://www.tradingview.com/chart/?symbol=CART) | 2026-09-01 | 50.05 | 5.25% | -16.02% | — | 2026-09-17 | DOWN10_ONLY |
| US | [ATI](https://www.tradingview.com/chart/?symbol=ATI) | 2026-09-04 | 210.6 | -0.13% | -15.95% | — | 2026-09-14 | DOWN10_ONLY |
| US | [XPRO](https://www.tradingview.com/chart/?symbol=XPRO) | 2026-08-24 | 17.9 | 5.20% | -15.87% | — | 2026-09-16 | DOWN10_ONLY |
| US | [KFRC](https://www.tradingview.com/chart/?symbol=KFRC) | 2026-08-23 | 58.38 | 1.09% | -15.63% | — | 2026-09-03 | DOWN10_ONLY |
| US | [SPB](https://www.tradingview.com/chart/?symbol=SPB) | 2026-08-25 | 88.98 | 0.99% | -15.57% | — | 2026-09-30 | DOWN10_ONLY |
| HK | [0325](https://www.tradingview.com/chart/?symbol=HKEX%3A325) | 2026-09-08 | 72 | -0.07% | -15.56% | — | 2026-09-21 | DOWN10_ONLY |
| US | [FNV](https://www.tradingview.com/chart/?symbol=FNV) | 2026-09-10 | 260.7 | 3.23% | -15.55% | — | 2026-09-30 | DOWN10_ONLY |
| US | [USFD](https://www.tradingview.com/chart/?symbol=USFD) | 2026-09-01 | 106.7 | 0.93% | -15.46% | — | 2026-09-10 | DOWN10_ONLY |
| US | [CSW](https://www.tradingview.com/chart/?symbol=CSW) | 2026-08-23 | 330.1 | 0.81% | -15.19% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [FNV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFNV) | 2026-09-24 | 367.2 | 0.59% | -15.13% | — | 2026-09-30 | DOWN10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-31 | 30 | 26.27% | -14.87% | 2026-09-07 | 2026-10-15 | UP10_FIRST |
| US | [CAI](https://www.tradingview.com/chart/?symbol=CAI) | 2026-10-05 | 30.38 | 7.18% | -14.85% | — | 2026-10-06 | DOWN10_ONLY |
| US | [CQP](https://www.tradingview.com/chart/?symbol=CQP) | 2026-09-09 | 70.44 | 0.07% | -14.81% | — | 2026-09-24 | DOWN10_ONLY |
| US | [NET](https://www.tradingview.com/chart/?symbol=NET) | 2026-10-08 | 341.7 | 6.29% | -14.79% | — | 2026-10-15 | DOWN10_ONLY |
| US | [FSK](https://www.tradingview.com/chart/?symbol=FSK) | 2026-09-14 | 12.04 | -1.66% | -14.70% | — | 2026-09-29 | DOWN10_ONLY |
| US | [HRMY](https://www.tradingview.com/chart/?symbol=HRMY) | 2026-09-21 | 42.08 | 0.69% | -14.47% | — | 2026-10-12 | DOWN10_ONLY |
| HK | [3347](https://www.tradingview.com/chart/?symbol=HKEX%3A3347) | 2026-10-02 | 45.88 | 4.62% | -14.47% | — | 2026-10-14 | DOWN10_ONLY |
| US | [GPN](https://www.tradingview.com/chart/?symbol=GPN) | 2026-08-31 | 91.06 | 4.22% | -14.43% | — | 2026-09-30 | DOWN10_ONLY |
| HK | [2343](https://www.tradingview.com/chart/?symbol=HKEX%3A2343) | 2026-09-17 | 4.205 | 4.04% | -14.39% | — | 2026-10-15 | DOWN10_ONLY |
| US | [EXE](https://www.tradingview.com/chart/?symbol=EXE) | 2026-09-10 | 96.83 | -0.03% | -14.02% | — | 2026-09-21 | DOWN10_ONLY |
| US | [NMR](https://www.tradingview.com/chart/?symbol=NMR) | 2026-09-16 | 10.46 | -0.96% | -13.96% | — | 2026-10-08 | DOWN10_ONLY |
| US | [JCAP](https://www.tradingview.com/chart/?symbol=JCAP) | 2026-09-08 | 21.71 | 0.41% | -13.59% | — | 2026-09-23 | DOWN10_ONLY |
| US | [AOS](https://www.tradingview.com/chart/?symbol=AOS) | 2026-08-23 | 63.06 | 1.63% | -13.50% | — | 2026-09-10 | DOWN10_ONLY |
| US | [SWK](https://www.tradingview.com/chart/?symbol=SWK) | 2026-08-20 | 98.91 | 1.50% | -13.35% | — | 2026-09-10 | DOWN10_ONLY |
| US | [MHK](https://www.tradingview.com/chart/?symbol=MHK) | 2026-08-20 | 133.4 | 3.66% | -13.31% | — | 2026-09-21 | DOWN10_ONLY |
| US | [BNTX](https://www.tradingview.com/chart/?symbol=BNTX) | 2026-09-22 | 100.8 | 0.56% | -13.29% | — | 2026-10-13 | DOWN10_ONLY |
| US | [DRI](https://www.tradingview.com/chart/?symbol=DRI) | 2026-09-02 | 220.1 | 0.59% | -13.15% | — | 2026-09-25 | DOWN10_ONLY |
| HK | [2232](https://www.tradingview.com/chart/?symbol=HKEX%3A2232) | 2026-09-05 | 7.105 | 6.76% | -13.09% | — | 2026-09-11 | DOWN10_ONLY |
| Canada | [EDV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEDV) | 2026-09-25 | 84.9 | -2.63% | -13.09% | — | 2026-10-07 | DOWN10_ONLY |
| US | [MSTR](https://www.tradingview.com/chart/?symbol=MSTR) | 2026-10-09 | 154.3 | 2.65% | -13.09% | — | 2026-10-15 | DOWN10_ONLY |
| US | [GM](https://www.tradingview.com/chart/?symbol=GM) | 2026-08-23 | 87.94 | 0.17% | -13.07% | — | 2026-09-30 | DOWN10_ONLY |
| US | [STE](https://www.tradingview.com/chart/?symbol=STE) | 2026-08-28 | 233.6 | 0.75% | -12.97% | — | 2026-09-11 | DOWN10_ONLY |
| US | [BMNR](https://www.tradingview.com/chart/?symbol=BMNR) | 2026-09-15 | 23.61 | 22.26% | -12.94% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [NSP](https://www.tradingview.com/chart/?symbol=NSP) | 2026-08-25 | 52.4 | 3.62% | -12.86% | — | 2026-09-24 | DOWN10_ONLY |
| US | [LNC](https://www.tradingview.com/chart/?symbol=LNC) | 2026-09-02 | 44.12 | 2.89% | -12.84% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-26 | 176.7 | 2.30% | -12.77% | — | 2026-09-22 | DOWN10_ONLY |
| US | [TSCO](https://www.tradingview.com/chart/?symbol=TSCO) | 2026-08-31 | 34.91 | 2.61% | -12.55% | — | 2026-09-24 | DOWN10_ONLY |
| US | [QSR](https://www.tradingview.com/chart/?symbol=QSR) | 2026-09-14 | 78.89 | -1.44% | -12.50% | — | 2026-09-23 | DOWN10_ONLY |
| US | [ATHM](https://www.tradingview.com/chart/?symbol=ATHM) | 2026-08-28 | 22.8 | -0.31% | -12.50% | — | 2026-10-02 | DOWN10_ONLY |
| US | [BVS](https://www.tradingview.com/chart/?symbol=BVS) | 2026-08-25 | 14.08 | 2.98% | -12.36% | — | 2026-09-17 | DOWN10_ONLY |
| US | [EPR](https://www.tradingview.com/chart/?symbol=EPR) | 2026-08-20 | 61.23 | -0.77% | -12.31% | — | 2026-10-01 | DOWN10_ONLY |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-08-24 | 104.1 | 3.21% | -12.04% | — | 2026-10-07 | DOWN10_ONLY |
| HK | [0656](https://www.tradingview.com/chart/?symbol=HKEX%3A656) | 2026-08-21 | 5.115 | 10.75% | -11.83% | 2026-09-01 | 2026-10-08 | UP10_FIRST |
| US | [AHR](https://www.tradingview.com/chart/?symbol=AHR) | 2026-08-20 | 55.79 | 2.50% | -11.72% | — | 2026-10-06 | DOWN10_ONLY |
| Canada | [BHC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABHC) | 2026-08-31 | 8.8 | 9.66% | -11.48% | — | 2026-09-15 | DOWN10_ONLY |
| US | [TNET](https://www.tradingview.com/chart/?symbol=TNET) | 2026-09-03 | 69.49 | 3.61% | -11.44% | — | 2026-09-28 | DOWN10_ONLY |
| US | [ANET](https://www.tradingview.com/chart/?symbol=ANET) | 2026-09-17 | 199.5 | 8.96% | -11.41% | — | 2026-10-15 | DOWN10_ONLY |
| US | [HTO](https://www.tradingview.com/chart/?symbol=HTO) | 2026-08-20 | 64.29 | 1.40% | -11.28% | — | 2026-10-07 | DOWN10_ONLY |
| US | [CNMD](https://www.tradingview.com/chart/?symbol=CNMD) | 2026-09-03 | 49.47 | 0.10% | -11.12% | — | 2026-09-21 | DOWN10_ONLY |
| US | [TRIN](https://www.tradingview.com/chart/?symbol=TRIN) | 2026-09-17 | 18.02 | -0.30% | -11.04% | — | 2026-10-16 | DOWN10_ONLY |
| US | [WWW](https://www.tradingview.com/chart/?symbol=WWW) | 2026-09-04 | 20.78 | -0.57% | -10.92% | — | 2026-09-29 | DOWN10_ONLY |
| US | [RDNT](https://www.tradingview.com/chart/?symbol=RDNT) | 2026-09-10 | 74.3 | 7.36% | -10.86% | — | 2026-10-08 | DOWN10_ONLY |
| US | [DAR](https://www.tradingview.com/chart/?symbol=DAR) | 2026-09-15 | 66.54 | 0.81% | -10.79% | — | 2026-09-29 | DOWN10_ONLY |
| US | [ROG](https://www.tradingview.com/chart/?symbol=ROG) | 2026-10-13 | 146.5 | -0.97% | -10.77% | — | 2026-10-15 | DOWN10_ONLY |
| Canada | [PSK.TO](https://www.tradingview.com/chart/?symbol=TSX%3APSK) | 2026-09-07 | 36.3 | 1.50% | -10.74% | — | 2026-09-29 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-09-04 | 34.84 | 9.56% | -10.71% | — | 2026-09-28 | DOWN10_ONLY |
| US | [KB](https://www.tradingview.com/chart/?symbol=KB) | 2026-09-29 | 128 | -1.99% | -10.70% | — | 2026-10-15 | DOWN10_ONLY |
| US | [NUTX](https://www.tradingview.com/chart/?symbol=NUTX) | 2026-09-24 | 204.7 | 10.51% | -10.63% | 2026-10-05 | 2026-10-15 | UP10_FIRST |
| US | [EPC](https://www.tradingview.com/chart/?symbol=EPC) | 2026-08-25 | 28.95 | 1.25% | -10.54% | — | 2026-09-15 | DOWN10_ONLY |
| US | [WDS](https://www.tradingview.com/chart/?symbol=WDS) | 2026-09-15 | 23.96 | -0.75% | -10.52% | — | 2026-09-29 | DOWN10_ONLY |
| US | [TTEK](https://www.tradingview.com/chart/?symbol=TTEK) | 2026-09-01 | 35.75 | 4.25% | -10.43% | — | 2026-10-07 | DOWN10_ONLY |
| US | [FLNG](https://www.tradingview.com/chart/?symbol=FLNG) | 2026-10-01 | 31.33 | 1.14% | -10.41% | — | 2026-10-16 | DOWN10_ONLY |
| Canada | [TNZ.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATNZ) | 2026-09-21 | 69.33 | 7.18% | -10.36% | — | 2026-09-29 | DOWN10_ONLY |
| US | [GDRX](https://www.tradingview.com/chart/?symbol=GDRX) | 2026-09-14 | 3.57 | 0.20% | -10.36% | — | 2026-10-01 | DOWN10_ONLY |
| US | [ADMA](https://www.tradingview.com/chart/?symbol=ADMA) | 2026-09-02 | 9.525 | 14.54% | -10.34% | 2026-10-09 | 2026-09-15 | DOWN10_FIRST |
| Canada | [POU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APOU) | 2026-09-11 | 31.98 | 7.88% | -10.27% | — | 2026-10-02 | DOWN10_ONLY |
| US | [AUGO](https://www.tradingview.com/chart/?symbol=AUGO) | 2026-09-15 | 85.77 | 9.00% | -10.23% | — | 2026-09-28 | DOWN10_ONLY |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-09-15 | 26.68 | 15.22% | -10.23% | 2026-09-24 | 2026-10-16 | UP10_FIRST |
| US | [SCCO](https://www.tradingview.com/chart/?symbol=SCCO) | 2026-09-02 | 204.3 | 4.69% | -10.16% | — | 2026-09-14 | DOWN10_ONLY |
| US | [PR](https://www.tradingview.com/chart/?symbol=PR) | 2026-09-17 | 23.2 | 6.14% | -10.15% | — | 2026-09-29 | DOWN10_ONLY |
| HK | [3600](https://www.tradingview.com/chart/?symbol=HKEX%3A3600) | 2026-08-29 | 8.2 | 2.07% | -10.12% | — | 2026-09-14 | DOWN10_ONLY |
| US | [SCI](https://www.tradingview.com/chart/?symbol=SCI) | 2026-08-25 | 84.46 | 1.57% | -10.11% | — | 2026-10-05 | DOWN10_ONLY |
| US | [BF-B](https://www.tradingview.com/chart/?symbol=BF-B) | 2026-08-20 | 28.42 | 2.99% | -10.10% | — | 2026-09-16 | DOWN10_ONLY |
| US | [BWIN](https://www.tradingview.com/chart/?symbol=BWIN) | 2026-08-31 | 30.85 | 6.01% | -10.08% | — | 2026-09-09 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **38**; -10%-only sample: **121**.
- +10%-only common candles: —.
- -10%-only common candles: —.
- Median RS: +10%-only **24.22** vs -10%-only **21.19**.
- Median % below 52w high: +10%-only **8.09** vs -10%-only **8.46**.
- Median breakout age: +10%-only **16.00** vs -10%-only **16.00**.
- Median quality score: +10%-only **6.00** vs -10%-only **4.00**.
- Median congestion score: +10%-only **1.00** vs -10%-only **1.00**.

## Reclaim Breakout

### 🟢 Reached +10% — 91

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [GRAL](https://www.tradingview.com/chart/?symbol=GRAL) | 2026-08-31 | 79.37 | 109.75% | -7.45% | 2026-09-21 | — | UP10_ONLY |
| US | [IOVA](https://www.tradingview.com/chart/?symbol=IOVA) | 2026-09-10 | 8.145 | 87.85% | -0.80% | 2026-09-14 | — | UP10_ONLY |
| US | [MPC](https://www.tradingview.com/chart/?symbol=MPC) | 2026-08-26 | 362.3 | 33.93% | -1.62% | 2026-09-03 | — | UP10_ONLY |
| HK | [3396](https://www.tradingview.com/chart/?symbol=HKEX%3A3396) | 2026-09-16 | 19.89 | 31.83% | -12.57% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [RVTY](https://www.tradingview.com/chart/?symbol=RVTY) | 2026-09-08 | 127.1 | 30.81% | -4.87% | 2026-09-15 | — | UP10_ONLY |
| US | [EFOR](https://www.tradingview.com/chart/?symbol=EFOR) | 2026-08-26 | 31.45 | 28.24% | -5.53% | 2026-10-01 | — | UP10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-25 | 29.64 | 27.80% | -13.83% | 2026-09-04 | 2026-10-15 | UP10_FIRST |
| US | [TWLO](https://www.tradingview.com/chart/?symbol=TWLO) | 2026-09-18 | 243.8 | 26.50% | -2.85% | 2026-09-22 | — | UP10_ONLY |
| HK | [1112](https://www.tradingview.com/chart/?symbol=HKEX%3A1112) | 2026-09-16 | 17.68 | 26.02% | -8.31% | 2026-10-02 | — | UP10_ONLY |
| US | [PBR](https://www.tradingview.com/chart/?symbol=PBR) | 2026-09-22 | 20.75 | 25.78% | -2.65% | 2026-10-05 | — | UP10_ONLY |
| US | [DHT](https://www.tradingview.com/chart/?symbol=DHT) | 2026-09-24 | 21.68 | 24.15% | -1.64% | 2026-10-05 | — | UP10_ONLY |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| US | [IDT](https://www.tradingview.com/chart/?symbol=IDT) | 2026-08-20 | 67.08 | 24.02% | -2.00% | 2026-09-29 | — | UP10_ONLY |
| US | [HCM](https://www.tradingview.com/chart/?symbol=HCM) | 2026-09-02 | 12.04 | 24.00% | 6.23% | 2026-09-03 | — | UP10_ONLY |
| US | [GTLB](https://www.tradingview.com/chart/?symbol=GTLB) | 2026-09-29 | 46.72 | 23.92% | -0.50% | 2026-10-05 | — | UP10_ONLY |
| HK | [2245](https://www.tradingview.com/chart/?symbol=HKEX%3A2245) | 2026-09-02 | 17.5 | 23.54% | -8.69% | 2026-09-23 | — | UP10_ONLY |
| US | [NEOG](https://www.tradingview.com/chart/?symbol=NEOG) | 2026-08-24 | 11.6 | 22.98% | -4.01% | 2026-09-16 | — | UP10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-09-22 | 103.9 | 21.57% | -4.26% | 2026-09-30 | — | UP10_ONLY |
| US | [DXC](https://www.tradingview.com/chart/?symbol=DXC) | 2026-09-02 | 11.64 | 21.56% | -12.97% | 2026-10-13 | 2026-09-28 | DOWN10_FIRST |
| US | [GMAB](https://www.tradingview.com/chart/?symbol=GMAB) | 2026-08-31 | 33.16 | 21.14% | -2.86% | 2026-10-05 | — | UP10_ONLY |
| US | [CRVL](https://www.tradingview.com/chart/?symbol=CRVL) | 2026-08-31 | 68.88 | 21.04% | -5.37% | 2026-10-01 | — | UP10_ONLY |
| US | [BOX](https://www.tradingview.com/chart/?symbol=BOX) | 2026-08-26 | 33.37 | 20.11% | -8.78% | 2026-10-09 | — | UP10_ONLY |
| US | [CRL](https://www.tradingview.com/chart/?symbol=CRL) | 2026-09-09 | 278.4 | 19.72% | -4.00% | 2026-10-05 | — | UP10_ONLY |
| US | [BMNR](https://www.tradingview.com/chart/?symbol=BMNR) | 2026-09-10 | 24.21 | 19.21% | -15.12% | 2026-09-11 | 2026-10-15 | UP10_FIRST |
| US | [TEAM](https://www.tradingview.com/chart/?symbol=TEAM) | 2026-09-22 | 188.7 | 18.54% | -10.95% | 2026-10-12 | 2026-09-29 | DOWN10_FIRST |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-08-23 | 25.99 | 18.28% | -9.47% | 2026-09-16 | — | UP10_ONLY |
| US | [PRGO](https://www.tradingview.com/chart/?symbol=PRGO) | 2026-09-21 | 14.13 | 18.05% | -2.62% | 2026-09-25 | — | UP10_ONLY |
| US | [SIG](https://www.tradingview.com/chart/?symbol=SIG) | 2026-10-01 | 104.3 | 17.60% | -3.86% | 2026-10-15 | — | UP10_ONLY |
| US | [ARHS](https://www.tradingview.com/chart/?symbol=ARHS) | 2026-08-25 | 8.915 | 17.55% | -20.73% | 2026-10-01 | 2026-09-10 | DOWN10_FIRST |
| US | [A](https://www.tradingview.com/chart/?symbol=A) | 2026-09-02 | 151.3 | 17.26% | -6.81% | 2026-09-22 | — | UP10_ONLY |
| US | [PGY](https://www.tradingview.com/chart/?symbol=PGY) | 2026-08-20 | 20.23 | 17.05% | -20.42% | 2026-08-24 | 2026-09-24 | UP10_FIRST |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-09-01 | 170 | 16.97% | -7.40% | 2026-09-22 | — | UP10_ONLY |
| US | [ADMA](https://www.tradingview.com/chart/?symbol=ADMA) | 2026-08-28 | 9.35 | 16.68% | -8.66% | 2026-10-06 | — | UP10_ONLY |
| HK | [1070](https://www.tradingview.com/chart/?symbol=HKEX%3A1070) | 2026-08-28 | 15.65 | 16.49% | -1.98% | 2026-09-01 | — | UP10_ONLY |
| US | [HPQ](https://www.tradingview.com/chart/?symbol=HPQ) | 2026-09-08 | 31.18 | 16.18% | -6.43% | 2026-09-11 | — | UP10_ONLY |
| US | [NTNX](https://www.tradingview.com/chart/?symbol=NTNX) | 2026-08-26 | 65.44 | 16.11% | -0.29% | 2026-08-27 | — | UP10_ONLY |
| US | [MCK](https://www.tradingview.com/chart/?symbol=MCK) | 2026-08-24 | 874.2 | 16.11% | -3.07% | 2026-10-13 | — | UP10_ONLY |
| US | [VIA](https://www.tradingview.com/chart/?symbol=VIA) | 2026-10-02 | 29.29 | 16.01% | 0.55% | 2026-10-09 | — | UP10_ONLY |
| HK | [2276](https://www.tradingview.com/chart/?symbol=HKEX%3A2276) | 2026-09-03 | 41.8 | 15.98% | -23.30% | 2026-09-22 | 2026-09-25 | UP10_FIRST |
| US | [HAE](https://www.tradingview.com/chart/?symbol=HAE) | 2026-09-23 | 106.9 | 15.81% | -5.19% | 2026-10-08 | — | UP10_ONLY |
| Canada | [SGY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASGY) | 2026-08-26 | 10.94 | 15.64% | -1.29% | 2026-09-10 | — | UP10_ONLY |
| US | [SNOW](https://www.tradingview.com/chart/?symbol=SNOW) | 2026-08-23 | 332.8 | 15.55% | -9.18% | 2026-09-03 | — | UP10_ONLY |
| HK | [2005](https://www.tradingview.com/chart/?symbol=HKEX%3A2005) | 2026-08-24 | 2.475 | 15.15% | -2.44% | 2026-09-03 | — | UP10_ONLY |
| US | [WF](https://www.tradingview.com/chart/?symbol=WF) | 2026-08-25 | 71 | 15.13% | -3.49% | 2026-09-11 | — | UP10_ONLY |
| US | [SN](https://www.tradingview.com/chart/?symbol=SN) | 2026-09-16 | 170.7 | 15.04% | -3.89% | 2026-10-12 | — | UP10_ONLY |
| US | [JOYY](https://www.tradingview.com/chart/?symbol=JOYY) | 2026-08-20 | 73.84 | 14.78% | -3.30% | 2026-10-06 | — | UP10_ONLY |
| HK | [9858](https://www.tradingview.com/chart/?symbol=HKEX%3A9858) | 2026-08-28 | 4.035 | 14.62% | -17.22% | 2026-09-01 | 2026-10-13 | UP10_FIRST |
| US | [ESTC](https://www.tradingview.com/chart/?symbol=ESTC) | 2026-09-08 | 88.47 | 14.60% | -7.14% | 2026-10-06 | — | UP10_ONLY |
| US | [SHG](https://www.tradingview.com/chart/?symbol=SHG) | 2026-08-23 | 74.8 | 14.40% | -6.87% | 2026-09-03 | — | UP10_ONLY |
| US | [NEO](https://www.tradingview.com/chart/?symbol=NEO) | 2026-09-09 | 17.65 | 14.16% | -12.69% | 2026-09-17 | 2026-10-07 | UP10_FIRST |
| US | [W](https://www.tradingview.com/chart/?symbol=W) | 2026-09-04 | 99.38 | 13.81% | -5.16% | 2026-10-15 | — | UP10_ONLY |
| US | [EQNR](https://www.tradingview.com/chart/?symbol=EQNR) | 2026-08-26 | 41.31 | 13.78% | -1.44% | 2026-09-10 | — | UP10_ONLY |
| US | [ELF](https://www.tradingview.com/chart/?symbol=ELF) | 2026-10-01 | 104.1 | 13.60% | -1.82% | 2026-10-15 | — | UP10_ONLY |
| HK | [2359](https://www.tradingview.com/chart/?symbol=HKEX%3A2359) | 2026-09-02 | 193.1 | 13.52% | -4.19% | 2026-09-29 | — | UP10_ONLY |
| HK | [0517](https://www.tradingview.com/chart/?symbol=HKEX%3A517) | 2026-09-16 | 6.3 | 13.49% | -1.59% | 2026-10-09 | — | UP10_ONLY |
| US | [MTDR](https://www.tradingview.com/chart/?symbol=MTDR) | 2026-08-28 | 56.36 | 13.24% | -10.59% | 2026-09-10 | 2026-09-29 | UP10_FIRST |
| US | [TMO](https://www.tradingview.com/chart/?symbol=TMO) | 2026-08-28 | 622 | 13.18% | -4.45% | 2026-10-06 | — | UP10_ONLY |
| US | [AVT](https://www.tradingview.com/chart/?symbol=AVT) | 2026-09-18 | 96.12 | 13.01% | -6.94% | 2026-10-02 | — | UP10_ONLY |
| HK | [3774](https://www.tradingview.com/chart/?symbol=HKEX%3A3774) | 2026-10-10 | 27.94 | 12.74% | -4.72% | 2026-10-15 | — | UP10_ONLY |
| US | [CTSH](https://www.tradingview.com/chart/?symbol=CTSH) | 2026-09-08 | 59.93 | 12.51% | -8.73% | 2026-10-15 | — | UP10_ONLY |
| US | [WAT](https://www.tradingview.com/chart/?symbol=WAT) | 2026-08-20 | 404.7 | 12.31% | -2.91% | 2026-09-28 | — | UP10_ONLY |
| US | [BP](https://www.tradingview.com/chart/?symbol=BP) | 2026-10-02 | 44.79 | 12.23% | -1.56% | 2026-10-16 | — | UP10_ONLY |
| US | [RDVT](https://www.tradingview.com/chart/?symbol=RDVT) | 2026-09-10 | 72.95 | 12.12% | -0.70% | 2026-09-17 | — | UP10_ONLY |
| US | [MTD](https://www.tradingview.com/chart/?symbol=MTD) | 2026-10-01 | 1481 | 12.05% | -0.14% | 2026-10-15 | — | UP10_ONLY |
| HK | [0144](https://www.tradingview.com/chart/?symbol=HKEX%3A144) | 2026-08-25 | 16.13 | 12.03% | -4.60% | 2026-10-14 | — | UP10_ONLY |
| US | [URBN](https://www.tradingview.com/chart/?symbol=URBN) | 2026-09-07 | 80.95 | 11.91% | -9.05% | 2026-10-16 | — | UP10_ONLY |
| US | [NCNO](https://www.tradingview.com/chart/?symbol=NCNO) | 2026-08-26 | 21.54 | 11.84% | -17.99% | 2026-08-28 | 2026-09-23 | UP10_FIRST |
| US | [HTFL](https://www.tradingview.com/chart/?symbol=HTFL) | 2026-09-24 | 48.57 | 11.84% | -4.26% | 2026-10-06 | — | UP10_ONLY |
| US | [BWLP](https://www.tradingview.com/chart/?symbol=BWLP) | 2026-09-08 | 23.91 | 11.71% | -0.36% | 2026-09-17 | — | UP10_ONLY |
| Canada | [SU.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASU) | 2026-10-02 | 99.13 | 11.54% | -3.07% | 2026-10-16 | — | UP10_ONLY |
| HK | [1308](https://www.tradingview.com/chart/?symbol=HKEX%3A1308) | 2026-09-16 | 46.76 | 11.53% | -0.34% | 2026-10-12 | — | UP10_ONLY |
| US | [GTM](https://www.tradingview.com/chart/?symbol=GTM) | 2026-09-08 | 3.91 | 11.51% | -10.49% | 2026-09-15 | 2026-09-28 | UP10_FIRST |
| US | [GO](https://www.tradingview.com/chart/?symbol=GO) | 2026-10-07 | 11.94 | 11.39% | -2.14% | 2026-10-15 | — | UP10_ONLY |
| US | [CVX](https://www.tradingview.com/chart/?symbol=CVX) | 2026-09-22 | 202.4 | 11.34% | -0.20% | 2026-10-15 | — | UP10_ONLY |
| HK | [3328](https://www.tradingview.com/chart/?symbol=HKEX%3A3328) | 2026-09-08 | 7.825 | 11.18% | -1.15% | 2026-10-13 | — | UP10_ONLY |
| US | [UGP](https://www.tradingview.com/chart/?symbol=UGP) | 2026-10-02 | 7.45 | 11.14% | 1.61% | 2026-10-05 | — | UP10_ONLY |
| US | [NHC](https://www.tradingview.com/chart/?symbol=NHC) | 2026-08-28 | 223 | 11.13% | -4.25% | 2026-10-15 | — | UP10_ONLY |
| US | [SCSC](https://www.tradingview.com/chart/?symbol=SCSC) | 2026-08-31 | 57.07 | 11.04% | -3.63% | 2026-10-02 | — | UP10_ONLY |
| US | [OLLI](https://www.tradingview.com/chart/?symbol=OLLI) | 2026-10-12 | 86.43 | 10.81% | 1.62% | 2026-10-15 | — | UP10_ONLY |
| HK | [0656](https://www.tradingview.com/chart/?symbol=HKEX%3A656) | 2026-08-21 | 5.115 | 10.75% | -11.83% | 2026-09-01 | 2026-10-08 | UP10_FIRST |
| Canada | [VLE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AVLE) | 2026-10-02 | 15.35 | 10.75% | -2.48% | 2026-10-14 | — | UP10_ONLY |
| US | [EQH](https://www.tradingview.com/chart/?symbol=EQH) | 2026-08-26 | 49.87 | 10.74% | -1.62% | 2026-09-17 | — | UP10_ONLY |
| US | [ABM](https://www.tradingview.com/chart/?symbol=ABM) | 2026-08-20 | 47.11 | 10.59% | -3.43% | 2026-10-15 | — | UP10_ONLY |
| US | [DK](https://www.tradingview.com/chart/?symbol=DK) | 2026-09-14 | 74.42 | 10.55% | -11.88% | 2026-09-17 | 2026-09-24 | UP10_FIRST |
| US | [PI](https://www.tradingview.com/chart/?symbol=PI) | 2026-09-15 | 174.4 | 10.55% | -1.16% | 2026-10-02 | — | UP10_ONLY |
| US | [BBY](https://www.tradingview.com/chart/?symbol=BBY) | 2026-08-24 | 87.47 | 10.35% | -13.23% | 2026-09-23 | 2026-08-27 | DOWN10_FIRST |
| US | [NMR](https://www.tradingview.com/chart/?symbol=NMR) | 2026-08-25 | 9.92 | 10.28% | -9.27% | 2026-09-11 | — | UP10_ONLY |
| US | [ULTA](https://www.tradingview.com/chart/?symbol=ULTA) | 2026-09-21 | 558 | 10.22% | -4.29% | 2026-10-16 | — | UP10_ONLY |
| US | [RELX](https://www.tradingview.com/chart/?symbol=RELX) | 2026-08-23 | 35.9 | 10.19% | -8.94% | 2026-10-16 | — | UP10_ONLY |
| US | [IOT](https://www.tradingview.com/chart/?symbol=IOT) | 2026-09-04 | 40.19 | 10.00% | -9.43% | 2026-10-05 | — | UP10_ONLY |

### 🔴 Reached -10% — 249

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [DYN](https://www.tradingview.com/chart/?symbol=DYN) | 2026-09-03 | 24.94 | -0.96% | -43.34% | — | 2026-09-08 | DOWN10_ONLY |
| US | [ELVN](https://www.tradingview.com/chart/?symbol=ELVN) | 2026-08-26 | 60.88 | 1.54% | -39.30% | — | 2026-09-11 | DOWN10_ONLY |
| US | [QMCO](https://www.tradingview.com/chart/?symbol=QMCO) | 2026-10-08 | 29.16 | 5.62% | -36.83% | — | 2026-10-13 | DOWN10_ONLY |
| HK | [2225](https://www.tradingview.com/chart/?symbol=HKEX%3A2225) | 2026-09-23 | 5.83 | 1.54% | -35.33% | — | 2026-09-28 | DOWN10_ONLY |
| US | [ALKT](https://www.tradingview.com/chart/?symbol=ALKT) | 2026-08-31 | 20.38 | 2.40% | -35.21% | — | 2026-09-10 | DOWN10_ONLY |
| US | [PCG](https://www.tradingview.com/chart/?symbol=PCG) | 2026-08-20 | 17.96 | 2.03% | -34.73% | — | 2026-08-28 | DOWN10_ONLY |
| US | [ENVA](https://www.tradingview.com/chart/?symbol=ENVA) | 2026-08-24 | 247.7 | 1.56% | -33.47% | — | 2026-09-01 | DOWN10_ONLY |
| US | [FRNM](https://www.tradingview.com/chart/?symbol=FRNM) | 2026-10-05 | 16.84 | 2.73% | -30.94% | — | 2026-10-12 | DOWN10_ONLY |
| US | [GPK](https://www.tradingview.com/chart/?symbol=GPK) | 2026-08-20 | 11.63 | 3.09% | -29.84% | — | 2026-09-03 | DOWN10_ONLY |
| US | [GEN](https://www.tradingview.com/chart/?symbol=GEN) | 2026-08-23 | 28.94 | 9.36% | -29.72% | — | 2026-09-24 | DOWN10_ONLY |
| US | [MAN](https://www.tradingview.com/chart/?symbol=MAN) | 2026-09-14 | 58.02 | 1.84% | -29.33% | — | 2026-10-01 | DOWN10_ONLY |
| US | [VOR](https://www.tradingview.com/chart/?symbol=VOR) | 2026-09-02 | 24.78 | 4.92% | -29.30% | — | 2026-09-10 | DOWN10_ONLY |
| US | [ELE](https://www.tradingview.com/chart/?symbol=ELE) | 2026-09-21 | 21.73 | 3.39% | -28.95% | — | 2026-09-24 | DOWN10_ONLY |
| US | [CG](https://www.tradingview.com/chart/?symbol=CG) | 2026-08-23 | 49.37 | 1.92% | -28.28% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [FF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFF) | 2026-09-08 | 0.89 | 8.99% | -28.09% | — | 2026-09-24 | DOWN10_ONLY |
| US | [PJT](https://www.tradingview.com/chart/?symbol=PJT) | 2026-09-02 | 181.4 | 3.40% | -27.58% | — | 2026-09-11 | DOWN10_ONLY |
| US | [GLIBA](https://www.tradingview.com/chart/?symbol=GLIBA) | 2026-09-02 | 26.73 | 0.75% | -27.24% | — | 2026-09-18 | DOWN10_ONLY |
| Canada | [AG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AAG) | 2026-09-09 | 29.24 | -1.68% | -27.05% | — | 2026-09-14 | DOWN10_ONLY |
| US | [TRUP](https://www.tradingview.com/chart/?symbol=TRUP) | 2026-08-26 | 30.18 | 1.56% | -26.94% | — | 2026-09-08 | DOWN10_ONLY |
| US | [EXK](https://www.tradingview.com/chart/?symbol=EXK) | 2026-09-22 | 10.51 | -3.52% | -26.93% | — | 2026-09-23 | DOWN10_ONLY |
| US | [MOS](https://www.tradingview.com/chart/?symbol=MOS) | 2026-09-11 | 25.2 | 2.24% | -26.93% | — | 2026-09-25 | DOWN10_ONLY |
| Canada | [ELE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AELE) | 2026-09-17 | 30.19 | 4.51% | -26.90% | — | 2026-10-01 | DOWN10_ONLY |
| US | [BX](https://www.tradingview.com/chart/?symbol=BX) | 2026-08-23 | 143.4 | 1.67% | -26.46% | — | 2026-09-09 | DOWN10_ONLY |
| HK | [0613](https://www.tradingview.com/chart/?symbol=HKEX%3A613) | 2026-08-24 | 5.6 | 5.00% | -26.43% | — | 2026-08-26 | DOWN10_ONLY |
| US | [PHVS](https://www.tradingview.com/chart/?symbol=PHVS) | 2026-09-10 | 37.6 | 7.98% | -26.38% | — | 2026-09-23 | DOWN10_ONLY |
| US | [TRU](https://www.tradingview.com/chart/?symbol=TRU) | 2026-09-02 | 82.39 | 4.87% | -26.01% | — | 2026-09-16 | DOWN10_ONLY |
| US | [CHWY](https://www.tradingview.com/chart/?symbol=CHWY) | 2026-09-01 | 23.72 | 7.00% | -25.89% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [EDR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEDR) | 2026-09-22 | 14.77 | -3.45% | -25.86% | — | 2026-09-23 | DOWN10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.61 | 21.99% | -25.86% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| HK | [2315](https://www.tradingview.com/chart/?symbol=HKEX%3A2315) | 2026-08-24 | 65 | 24.08% | -25.69% | 2026-10-05 | 2026-08-25 | DOWN10_FIRST |
| US | [CWK](https://www.tradingview.com/chart/?symbol=CWK) | 2026-08-24 | 14.64 | 1.64% | -25.68% | — | 2026-09-01 | DOWN10_ONLY |
| US | [GLIBK](https://www.tradingview.com/chart/?symbol=GLIBK) | 2026-08-31 | 26.05 | 2.46% | -25.49% | — | 2026-09-25 | DOWN10_ONLY |
| US | [IMCR](https://www.tradingview.com/chart/?symbol=IMCR) | 2026-08-28 | 36.63 | 3.61% | -24.92% | — | 2026-09-11 | DOWN10_ONLY |
| US | [ZBIO](https://www.tradingview.com/chart/?symbol=ZBIO) | 2026-08-23 | 32.28 | 5.30% | -24.88% | — | 2026-09-24 | DOWN10_ONLY |
| US | [MNDY](https://www.tradingview.com/chart/?symbol=MNDY) | 2026-09-03 | 97.32 | 1.34% | -24.83% | — | 2026-09-08 | DOWN10_ONLY |
| US | [LAD](https://www.tradingview.com/chart/?symbol=LAD) | 2026-09-10 | 366.3 | 2.51% | -24.22% | — | 2026-09-17 | DOWN10_ONLY |
| US | [JLL](https://www.tradingview.com/chart/?symbol=JLL) | 2026-08-28 | 377.8 | -0.53% | -24.16% | — | 2026-09-10 | DOWN10_ONLY |
| US | [LW](https://www.tradingview.com/chart/?symbol=LW) | 2026-08-20 | 53.47 | 4.17% | -23.97% | — | 2026-09-09 | DOWN10_ONLY |
| HK | [1929](https://www.tradingview.com/chart/?symbol=HKEX%3A1929) | 2026-08-29 | 13.6 | -0.96% | -23.38% | — | 2026-09-02 | DOWN10_ONLY |
| US | [RHI](https://www.tradingview.com/chart/?symbol=RHI) | 2026-09-04 | 42.58 | -1.01% | -23.32% | — | 2026-09-09 | DOWN10_ONLY |
| HK | [2276](https://www.tradingview.com/chart/?symbol=HKEX%3A2276) | 2026-09-03 | 41.8 | 15.98% | -23.30% | 2026-09-22 | 2026-09-25 | UP10_FIRST |
| US | [JBS](https://www.tradingview.com/chart/?symbol=JBS) | 2026-08-23 | 13.82 | 2.42% | -23.25% | — | 2026-09-11 | DOWN10_ONLY |
| US | [KKR](https://www.tradingview.com/chart/?symbol=KKR) | 2026-08-31 | 109.7 | 1.07% | -23.23% | — | 2026-09-16 | DOWN10_ONLY |
| US | [MESO](https://www.tradingview.com/chart/?symbol=MESO) | 2026-08-26 | 16.83 | 8.91% | -23.11% | — | 2026-09-14 | DOWN10_ONLY |
| US | [INTU](https://www.tradingview.com/chart/?symbol=INTU) | 2026-09-14 | 339.1 | -0.52% | -23.01% | — | 2026-09-18 | DOWN10_ONLY |
| HK | [1952](https://www.tradingview.com/chart/?symbol=HKEX%3A1952) | 2026-09-08 | 33.2 | 3.07% | -22.59% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [RIO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIO) | 2026-09-18 | 3.66 | 7.38% | -22.13% | — | 2026-09-28 | DOWN10_ONLY |
| US | [PCOR](https://www.tradingview.com/chart/?symbol=PCOR) | 2026-08-26 | 60.44 | 7.20% | -21.79% | — | 2026-09-09 | DOWN10_ONLY |
| US | [EAT](https://www.tradingview.com/chart/?symbol=EAT) | 2026-09-01 | 234 | 1.10% | -21.61% | — | 2026-09-11 | DOWN10_ONLY |
| US | [INSM](https://www.tradingview.com/chart/?symbol=INSM) | 2026-08-31 | 121.8 | 7.38% | -21.41% | — | 2026-10-01 | DOWN10_ONLY |
| US | [STEP](https://www.tradingview.com/chart/?symbol=STEP) | 2026-09-04 | 50.93 | 2.09% | -21.36% | — | 2026-09-22 | DOWN10_ONLY |
| US | [SE](https://www.tradingview.com/chart/?symbol=SE) | 2026-08-20 | 117.2 | 5.56% | -21.30% | — | 2026-09-14 | DOWN10_ONLY |
| Canada | [AC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AAC) | 2026-08-31 | 27.32 | 6.52% | -21.23% | — | 2026-10-08 | DOWN10_ONLY |
| US | [NU](https://www.tradingview.com/chart/?symbol=NU) | 2026-09-02 | 15.39 | 5.16% | -21.20% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SON](https://www.tradingview.com/chart/?symbol=SON) | 2026-08-23 | 59.47 | 0.47% | -20.78% | — | 2026-09-03 | DOWN10_ONLY |
| US | [ARHS](https://www.tradingview.com/chart/?symbol=ARHS) | 2026-08-25 | 8.915 | 17.55% | -20.73% | 2026-10-01 | 2026-09-10 | DOWN10_FIRST |
| US | [PGY](https://www.tradingview.com/chart/?symbol=PGY) | 2026-08-20 | 20.23 | 17.05% | -20.42% | 2026-08-24 | 2026-09-24 | UP10_FIRST |
| US | [DRTS](https://www.tradingview.com/chart/?symbol=DRTS) | 2026-09-16 | 15.06 | 4.85% | -20.39% | — | 2026-10-14 | DOWN10_ONLY |
| US | [PAY](https://www.tradingview.com/chart/?symbol=PAY) | 2026-09-03 | 36.76 | 3.11% | -20.35% | — | 2026-09-22 | DOWN10_ONLY |
| US | [LPLA](https://www.tradingview.com/chart/?symbol=LPLA) | 2026-08-28 | 370.7 | 0.60% | -20.26% | — | 2026-09-16 | DOWN10_ONLY |
| HK | [6821](https://www.tradingview.com/chart/?symbol=HKEX%3A6821) | 2026-10-08 | 163 | 0.00% | -20.12% | — | 2026-10-09 | DOWN10_ONLY |
| US | [OII](https://www.tradingview.com/chart/?symbol=OII) | 2026-08-31 | 51.76 | 1.82% | -20.03% | — | 2026-09-14 | DOWN10_ONLY |
| US | [MFA-PB](https://www.tradingview.com/chart/?symbol=MFA-PB) | 2026-09-02 | 20.62 | -2.13% | -19.98% | — | 2026-09-25 | DOWN10_ONLY |
| US | [ALSN](https://www.tradingview.com/chart/?symbol=ALSN) | 2026-09-04 | 131.2 | 0.90% | -19.91% | — | 2026-09-16 | DOWN10_ONLY |
| US | [JHX](https://www.tradingview.com/chart/?symbol=JHX) | 2026-09-03 | 29.64 | 6.04% | -19.91% | — | 2026-09-15 | DOWN10_ONLY |
| US | [ADBE](https://www.tradingview.com/chart/?symbol=ADBE) | 2026-09-02 | 279.8 | 4.68% | -19.70% | — | 2026-09-10 | DOWN10_ONLY |
| US | [PLSE](https://www.tradingview.com/chart/?symbol=PLSE) | 2026-09-18 | 53.92 | 5.23% | -19.66% | — | 2026-10-02 | DOWN10_ONLY |
| US | [CNS](https://www.tradingview.com/chart/?symbol=CNS) | 2026-08-20 | 80.72 | 5.18% | -19.38% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [MARI.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMARI) | 2026-09-22 | 8.93 | -0.11% | -19.26% | — | 2026-10-07 | DOWN10_ONLY |
| US | [RYAN](https://www.tradingview.com/chart/?symbol=RYAN) | 2026-08-24 | 44.35 | 0.61% | -19.05% | — | 2026-09-09 | DOWN10_ONLY |
| US | [TPG](https://www.tradingview.com/chart/?symbol=TPG) | 2026-09-08 | 50.93 | -1.02% | -19.04% | — | 2026-09-18 | DOWN10_ONLY |
| US | [CART](https://www.tradingview.com/chart/?symbol=CART) | 2026-08-24 | 51.78 | 1.74% | -18.83% | — | 2026-09-09 | DOWN10_ONLY |
| US | [LDOS](https://www.tradingview.com/chart/?symbol=LDOS) | 2026-08-26 | 137.4 | 3.33% | -18.46% | — | 2026-09-22 | DOWN10_ONLY |
| Canada | [GGD.TO](https://www.tradingview.com/chart/?symbol=TSX%3AGGD) | 2026-09-21 | 4.42 | 4.52% | -18.33% | — | 2026-10-06 | DOWN10_ONLY |
| HK | [1184](https://www.tradingview.com/chart/?symbol=HKEX%3A1184) | 2026-09-22 | 8.26 | 0.48% | -18.28% | — | 2026-10-14 | DOWN10_ONLY |
| US | [RITM](https://www.tradingview.com/chart/?symbol=RITM) | 2026-08-20 | 10.16 | -1.46% | -18.21% | — | 2026-09-18 | DOWN10_ONLY |
| US | [BL](https://www.tradingview.com/chart/?symbol=BL) | 2026-08-25 | 31.63 | 9.71% | -18.12% | — | 2026-09-11 | DOWN10_ONLY |
| US | [BRO](https://www.tradingview.com/chart/?symbol=BRO) | 2026-08-20 | 72.07 | 3.75% | -18.12% | — | 2026-09-18 | DOWN10_ONLY |
| US | [BSY](https://www.tradingview.com/chart/?symbol=BSY) | 2026-08-23 | 37.08 | 3.41% | -18.12% | — | 2026-09-04 | DOWN10_ONLY |
| US | [JAZZ](https://www.tradingview.com/chart/?symbol=JAZZ) | 2026-08-23 | 254.1 | 4.83% | -18.08% | — | 2026-10-07 | DOWN10_ONLY |
| US | [NCNO](https://www.tradingview.com/chart/?symbol=NCNO) | 2026-08-26 | 21.54 | 11.84% | -17.99% | 2026-08-28 | 2026-09-23 | UP10_FIRST |
| US | [AJG](https://www.tradingview.com/chart/?symbol=AJG) | 2026-09-03 | 266.7 | -0.25% | -17.63% | — | 2026-09-18 | DOWN10_ONLY |
| HK | [8279](https://www.tradingview.com/chart/?symbol=HKEX%3A8279) | 2026-09-16 | 1.38 | 2.90% | -17.39% | — | 2026-09-22 | DOWN10_ONLY |
| Canada | [OBE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AOBE) | 2026-09-18 | 17.2 | -0.93% | -17.38% | — | 2026-09-25 | DOWN10_ONLY |
| US | [CEG](https://www.tradingview.com/chart/?symbol=CEG) | 2026-09-07 | 298.9 | 3.63% | -17.31% | — | 2026-09-14 | DOWN10_ONLY |
| HK | [9858](https://www.tradingview.com/chart/?symbol=HKEX%3A9858) | 2026-08-28 | 4.035 | 14.62% | -17.22% | 2026-09-01 | 2026-10-13 | UP10_FIRST |
| US | [TPC](https://www.tradingview.com/chart/?symbol=TPC) | 2026-08-20 | 90.35 | 2.42% | -17.20% | — | 2026-10-01 | DOWN10_ONLY |
| US | [FLR](https://www.tradingview.com/chart/?symbol=FLR) | 2026-09-09 | 54.82 | 2.15% | -17.18% | — | 2026-09-28 | DOWN10_ONLY |
| US | [BMRN](https://www.tradingview.com/chart/?symbol=BMRN) | 2026-08-24 | 65.06 | 4.06% | -17.15% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [HSLV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHSLV) | 2026-09-21 | 7.95 | 3.40% | -17.11% | — | 2026-09-28 | DOWN10_ONLY |
| US | [CCC](https://www.tradingview.com/chart/?symbol=CCC) | 2026-09-04 | 7.515 | 5.26% | -16.97% | — | 2026-09-09 | DOWN10_ONLY |
| US | [WT](https://www.tradingview.com/chart/?symbol=WT) | 2026-09-10 | 24.27 | 3.15% | -16.96% | — | 2026-09-15 | DOWN10_ONLY |
| US | [MT](https://www.tradingview.com/chart/?symbol=MT) | 2026-08-24 | 72.65 | 9.68% | -16.94% | — | 2026-10-01 | DOWN10_ONLY |
| HK | [1579](https://www.tradingview.com/chart/?symbol=HKEX%3A1579) | 2026-08-31 | 15.83 | -1.10% | -16.93% | — | 2026-09-09 | DOWN10_ONLY |
| US | [AVNT](https://www.tradingview.com/chart/?symbol=AVNT) | 2026-08-31 | 44.04 | -0.10% | -16.89% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [CGG.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACGG) | 2026-09-15 | 44.8 | 9.35% | -16.87% | — | 2026-09-24 | DOWN10_ONLY |
| US | [LYFT](https://www.tradingview.com/chart/?symbol=LYFT) | 2026-09-02 | 17.35 | 3.63% | -16.74% | — | 2026-09-09 | DOWN10_ONLY |
| US | [ALL](https://www.tradingview.com/chart/?symbol=ALL) | 2026-09-03 | 263.1 | 0.08% | -16.57% | — | 2026-09-22 | DOWN10_ONLY |
| Canada | [FNV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFNV) | 2026-09-17 | 373.3 | 1.37% | -16.50% | — | 2026-09-30 | DOWN10_ONLY |
| HK | [0325](https://www.tradingview.com/chart/?symbol=HKEX%3A325) | 2026-09-02 | 72.8 | 8.24% | -16.48% | — | 2026-09-10 | DOWN10_ONLY |
| US | [STT](https://www.tradingview.com/chart/?symbol=STT) | 2026-08-23 | 187.1 | 4.16% | -16.36% | — | 2026-10-14 | DOWN10_ONLY |
| US | [CNR](https://www.tradingview.com/chart/?symbol=CNR) | 2026-09-07 | 99.62 | 1.90% | -16.35% | — | 2026-09-22 | DOWN10_ONLY |
| US | [OMF](https://www.tradingview.com/chart/?symbol=OMF) | 2026-09-03 | 64.59 | 1.18% | -16.33% | — | 2026-09-23 | DOWN10_ONLY |
| US | [RLI](https://www.tradingview.com/chart/?symbol=RLI) | 2026-08-20 | 65.11 | 2.62% | -16.29% | — | 2026-09-22 | DOWN10_ONLY |
| US | [OMC](https://www.tradingview.com/chart/?symbol=OMC) | 2026-08-26 | 87.9 | 0.47% | -16.23% | — | 2026-09-09 | DOWN10_ONLY |
| US | [RVMD](https://www.tradingview.com/chart/?symbol=RVMD) | 2026-09-01 | 209.9 | 1.49% | -16.19% | — | 2026-09-18 | DOWN10_ONLY |
| US | [JCAP](https://www.tradingview.com/chart/?symbol=JCAP) | 2026-08-20 | 22.31 | 1.05% | -15.91% | — | 2026-09-18 | DOWN10_ONLY |
| US | [XPRO](https://www.tradingview.com/chart/?symbol=XPRO) | 2026-08-24 | 17.9 | 5.20% | -15.87% | — | 2026-09-16 | DOWN10_ONLY |
| Canada | [ALS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALS) | 2026-09-11 | 66.53 | 4.54% | -15.83% | — | 2026-10-15 | DOWN10_ONLY |
| US | [TOST](https://www.tradingview.com/chart/?symbol=TOST) | 2026-08-31 | 34.09 | 2.58% | -15.83% | — | 2026-09-17 | DOWN10_ONLY |
| US | [SEPN](https://www.tradingview.com/chart/?symbol=SEPN) | 2026-08-20 | 40.79 | 2.60% | -15.76% | — | 2026-09-03 | DOWN10_ONLY |
| US | [CQP](https://www.tradingview.com/chart/?symbol=CQP) | 2026-09-02 | 71.22 | 0.04% | -15.74% | — | 2026-09-18 | DOWN10_ONLY |
| US | [AXTA](https://www.tradingview.com/chart/?symbol=AXTA) | 2026-08-28 | 37 | 0.84% | -15.68% | — | 2026-09-14 | DOWN10_ONLY |
| US | [CDLR](https://www.tradingview.com/chart/?symbol=CDLR) | 2026-09-15 | 24.7 | 5.51% | -15.67% | — | 2026-09-30 | DOWN10_ONLY |
| US | [KFRC](https://www.tradingview.com/chart/?symbol=KFRC) | 2026-08-23 | 58.38 | 1.09% | -15.63% | — | 2026-09-03 | DOWN10_ONLY |
| US | [SPB](https://www.tradingview.com/chart/?symbol=SPB) | 2026-08-25 | 88.98 | 0.99% | -15.57% | — | 2026-09-30 | DOWN10_ONLY |
| US | [FNV](https://www.tradingview.com/chart/?symbol=FNV) | 2026-09-10 | 260.7 | 3.23% | -15.55% | — | 2026-09-30 | DOWN10_ONLY |
| US | [SPOT](https://www.tradingview.com/chart/?symbol=SPOT) | 2026-09-14 | 556.6 | 1.49% | -15.52% | — | 2026-09-22 | DOWN10_ONLY |
| US | [FHI](https://www.tradingview.com/chart/?symbol=FHI) | 2026-08-23 | 63.69 | 3.36% | -15.50% | — | 2026-09-16 | DOWN10_ONLY |
| US | [USFD](https://www.tradingview.com/chart/?symbol=USFD) | 2026-09-01 | 106.7 | 0.93% | -15.46% | — | 2026-09-10 | DOWN10_ONLY |
| US | [NOG](https://www.tradingview.com/chart/?symbol=NOG) | 2026-09-14 | 26.38 | 3.37% | -15.43% | — | 2026-09-21 | DOWN10_ONLY |
| US | [ATI](https://www.tradingview.com/chart/?symbol=ATI) | 2026-08-20 | 209.2 | 4.15% | -15.37% | — | 2026-09-14 | DOWN10_ONLY |
| Canada | [OGC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AOGC) | 2026-09-07 | 42.32 | 3.45% | -15.31% | — | 2026-09-28 | DOWN10_ONLY |
| US | [CSW](https://www.tradingview.com/chart/?symbol=CSW) | 2026-08-23 | 330.1 | 0.81% | -15.19% | — | 2026-09-09 | DOWN10_ONLY |
| US | [BMNR](https://www.tradingview.com/chart/?symbol=BMNR) | 2026-09-10 | 24.21 | 19.21% | -15.12% | 2026-09-11 | 2026-10-15 | UP10_FIRST |
| HK | [0005](https://www.tradingview.com/chart/?symbol=HKEX%3A5) | 2026-09-04 | 167.2 | 0.42% | -15.07% | — | 2026-10-02 | DOWN10_ONLY |
| US | [NTR](https://www.tradingview.com/chart/?symbol=NTR) | 2026-09-15 | 78.74 | -0.04% | -15.02% | — | 2026-09-25 | DOWN10_ONLY |
| US | [FSK](https://www.tradingview.com/chart/?symbol=FSK) | 2026-08-24 | 12.06 | 0.33% | -14.88% | — | 2026-09-29 | DOWN10_ONLY |
| US | [CAI](https://www.tradingview.com/chart/?symbol=CAI) | 2026-10-05 | 30.38 | 7.18% | -14.85% | — | 2026-10-06 | DOWN10_ONLY |
| US | [NET](https://www.tradingview.com/chart/?symbol=NET) | 2026-10-08 | 341.7 | 6.29% | -14.79% | — | 2026-10-15 | DOWN10_ONLY |
| US | [AMCR](https://www.tradingview.com/chart/?symbol=AMCR) | 2026-08-20 | 47.81 | 0.90% | -14.69% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [ONEX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AONEX) | 2026-08-25 | 116.6 | 1.22% | -14.65% | — | 2026-09-29 | DOWN10_ONLY |
| US | [UBS](https://www.tradingview.com/chart/?symbol=UBS) | 2026-08-26 | 54.52 | 2.69% | -14.64% | — | 2026-09-22 | DOWN10_ONLY |
| US | [MRSH](https://www.tradingview.com/chart/?symbol=MRSH) | 2026-08-24 | 194.7 | -0.13% | -14.58% | — | 2026-09-11 | DOWN10_ONLY |
| US | [WK](https://www.tradingview.com/chart/?symbol=WK) | 2026-09-14 | 75.9 | 4.22% | -14.56% | — | 2026-09-28 | DOWN10_ONLY |
| US | [GPN](https://www.tradingview.com/chart/?symbol=GPN) | 2026-08-31 | 91.06 | 4.22% | -14.43% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [ORE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AORE) | 2026-10-09 | 3.23 | -0.31% | -14.40% | — | 2026-10-14 | DOWN10_ONLY |
| US | [FUTU](https://www.tradingview.com/chart/?symbol=FUTU) | 2026-09-02 | 118.1 | 3.81% | -14.39% | — | 2026-10-01 | DOWN10_ONLY |
| HK | [2343](https://www.tradingview.com/chart/?symbol=HKEX%3A2343) | 2026-09-17 | 4.205 | 4.04% | -14.39% | — | 2026-10-15 | DOWN10_ONLY |
| US | [BBVA](https://www.tradingview.com/chart/?symbol=BBVA) | 2026-09-07 | 29.52 | -1.48% | -14.18% | — | 2026-10-01 | DOWN10_ONLY |
| US | [EXE](https://www.tradingview.com/chart/?symbol=EXE) | 2026-09-10 | 96.83 | -0.03% | -14.02% | — | 2026-09-21 | DOWN10_ONLY |
| US | [GSBD](https://www.tradingview.com/chart/?symbol=GSBD) | 2026-09-17 | 9.985 | -3.23% | -13.97% | — | 2026-10-07 | DOWN10_ONLY |
| US | [COF](https://www.tradingview.com/chart/?symbol=COF) | 2026-09-03 | 220.5 | 0.13% | -13.92% | — | 2026-09-23 | DOWN10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-08-25 | 29.64 | 27.80% | -13.83% | 2026-09-04 | 2026-10-15 | UP10_FIRST |
| US | [DRI](https://www.tradingview.com/chart/?symbol=DRI) | 2026-08-23 | 221.6 | 1.73% | -13.76% | — | 2026-09-25 | DOWN10_ONLY |
| US | [UNF](https://www.tradingview.com/chart/?symbol=UNF) | 2026-08-25 | 287.8 | 1.16% | -13.66% | — | 2026-09-18 | DOWN10_ONLY |
| HK | [2269](https://www.tradingview.com/chart/?symbol=HKEX%3A2269) | 2026-09-26 | 53 | 9.43% | -13.55% | — | 2026-10-16 | DOWN10_ONLY |
| US | [AOS](https://www.tradingview.com/chart/?symbol=AOS) | 2026-08-23 | 63.06 | 1.63% | -13.50% | — | 2026-09-10 | DOWN10_ONLY |
| HK | [1179](https://www.tradingview.com/chart/?symbol=HKEX%3A1179) | 2026-09-01 | 36.94 | 0.65% | -13.43% | — | 2026-09-14 | DOWN10_ONLY |
| US | [HRMY](https://www.tradingview.com/chart/?symbol=HRMY) | 2026-09-14 | 41.56 | 4.11% | -13.40% | — | 2026-10-12 | DOWN10_ONLY |
| US | [SWK](https://www.tradingview.com/chart/?symbol=SWK) | 2026-08-20 | 98.91 | 1.50% | -13.35% | — | 2026-09-10 | DOWN10_ONLY |
| US | [MHK](https://www.tradingview.com/chart/?symbol=MHK) | 2026-08-20 | 133.4 | 3.66% | -13.31% | — | 2026-09-21 | DOWN10_ONLY |
| US | [HLN](https://www.tradingview.com/chart/?symbol=HLN) | 2026-08-23 | 10 | 2.60% | -13.30% | — | 2026-09-29 | DOWN10_ONLY |
| US | [BNTX](https://www.tradingview.com/chart/?symbol=BNTX) | 2026-09-22 | 100.8 | 0.56% | -13.29% | — | 2026-10-13 | DOWN10_ONLY |
| US | [BBY](https://www.tradingview.com/chart/?symbol=BBY) | 2026-08-24 | 87.47 | 10.35% | -13.23% | 2026-09-23 | 2026-08-27 | DOWN10_FIRST |
| HK | [3347](https://www.tradingview.com/chart/?symbol=HKEX%3A3347) | 2026-09-29 | 45.22 | 6.94% | -13.22% | — | 2026-10-16 | DOWN10_ONLY |
| US | [BLK](https://www.tradingview.com/chart/?symbol=BLK) | 2026-08-24 | 1172 | 0.74% | -13.22% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [MG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMG) | 2026-08-23 | 100.5 | -0.97% | -13.20% | — | 2026-08-26 | DOWN10_ONLY |
| US | [DEO](https://www.tradingview.com/chart/?symbol=DEO) | 2026-08-23 | 94.62 | 1.20% | -13.19% | — | 2026-09-09 | DOWN10_ONLY |
| US | [FTDR](https://www.tradingview.com/chart/?symbol=FTDR) | 2026-08-31 | 80.87 | 2.97% | -13.13% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [FIH-U.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFIH.U) | 2026-08-26 | 19.45 | 0.72% | -13.11% | — | 2026-09-15 | DOWN10_ONLY |
| US | [LYG](https://www.tradingview.com/chart/?symbol=LYG) | 2026-09-03 | 6.1 | -0.00% | -13.11% | — | 2026-10-01 | DOWN10_ONLY |
| HK | [2232](https://www.tradingview.com/chart/?symbol=HKEX%3A2232) | 2026-09-05 | 7.105 | 6.76% | -13.09% | — | 2026-09-11 | DOWN10_ONLY |
| US | [MSTR](https://www.tradingview.com/chart/?symbol=MSTR) | 2026-10-09 | 154.3 | 2.65% | -13.09% | — | 2026-10-15 | DOWN10_ONLY |
| US | [GM](https://www.tradingview.com/chart/?symbol=GM) | 2026-08-23 | 87.94 | 0.17% | -13.07% | — | 2026-09-30 | DOWN10_ONLY |
| US | [KSPI](https://www.tradingview.com/chart/?symbol=KSPI) | 2026-09-01 | 104.1 | 2.43% | -13.00% | — | 2026-09-23 | DOWN10_ONLY |
| US | [STE](https://www.tradingview.com/chart/?symbol=STE) | 2026-08-28 | 233.6 | 0.75% | -12.97% | — | 2026-09-11 | DOWN10_ONLY |
| US | [DXC](https://www.tradingview.com/chart/?symbol=DXC) | 2026-09-02 | 11.64 | 21.56% | -12.97% | 2026-10-13 | 2026-09-28 | DOWN10_FIRST |
| US | [NSP](https://www.tradingview.com/chart/?symbol=NSP) | 2026-08-25 | 52.4 | 3.62% | -12.86% | — | 2026-09-24 | DOWN10_ONLY |
| US | [AR](https://www.tradingview.com/chart/?symbol=AR) | 2026-08-25 | 37.96 | 5.93% | -12.75% | — | 2026-09-21 | DOWN10_ONLY |
| US | [SBLK](https://www.tradingview.com/chart/?symbol=SBLK) | 2026-09-17 | 31.75 | 2.87% | -12.72% | — | 2026-10-14 | DOWN10_ONLY |
| US | [TSCO](https://www.tradingview.com/chart/?symbol=TSCO) | 2026-08-23 | 34.98 | 3.23% | -12.72% | — | 2026-09-24 | DOWN10_ONLY |
| US | [NEO](https://www.tradingview.com/chart/?symbol=NEO) | 2026-09-09 | 17.65 | 14.16% | -12.69% | 2026-09-17 | 2026-10-07 | UP10_FIRST |
| Canada | [NTR.TO](https://www.tradingview.com/chart/?symbol=TSX%3ANTR) | 2026-09-15 | 109.7 | 0.50% | -12.66% | — | 2026-10-01 | DOWN10_ONLY |
| US | [TNET](https://www.tradingview.com/chart/?symbol=TNET) | 2026-08-23 | 70.44 | 2.21% | -12.63% | — | 2026-09-28 | DOWN10_ONLY |
| US | [BHP](https://www.tradingview.com/chart/?symbol=BHP) | 2026-09-09 | 92.25 | -4.27% | -12.63% | — | 2026-09-28 | DOWN10_ONLY |
| US | [ANET](https://www.tradingview.com/chart/?symbol=ANET) | 2026-08-26 | 202.3 | 7.48% | -12.61% | — | 2026-09-03 | DOWN10_ONLY |
| Canada | [PRU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APRU) | 2026-09-08 | 6.485 | 5.78% | -12.57% | — | 2026-10-15 | DOWN10_ONLY |
| HK | [3396](https://www.tradingview.com/chart/?symbol=HKEX%3A3396) | 2026-09-16 | 19.89 | 31.83% | -12.57% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [PAG](https://www.tradingview.com/chart/?symbol=PAG) | 2026-08-25 | 219.8 | 0.58% | -12.52% | — | 2026-10-07 | DOWN10_ONLY |
| US | [ATHM](https://www.tradingview.com/chart/?symbol=ATHM) | 2026-08-28 | 22.8 | -0.31% | -12.50% | — | 2026-10-02 | DOWN10_ONLY |
| US | [QSR](https://www.tradingview.com/chart/?symbol=QSR) | 2026-09-02 | 78.89 | 2.71% | -12.50% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [EDV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEDV) | 2026-09-24 | 84.29 | 1.06% | -12.46% | — | 2026-10-07 | DOWN10_ONLY |
| US | [BTE](https://www.tradingview.com/chart/?symbol=BTE) | 2026-09-11 | 5.02 | 5.98% | -12.35% | — | 2026-09-25 | DOWN10_ONLY |
| US | [OKE](https://www.tradingview.com/chart/?symbol=OKE) | 2026-08-31 | 96 | 4.01% | -12.34% | — | 2026-09-29 | DOWN10_ONLY |
| US | [NUTX](https://www.tradingview.com/chart/?symbol=NUTX) | 2026-09-18 | 208.6 | 8.41% | -12.32% | — | 2026-10-15 | DOWN10_ONLY |
| US | [MGA](https://www.tradingview.com/chart/?symbol=MGA) | 2026-08-20 | 70.39 | 4.02% | -12.32% | — | 2026-09-01 | DOWN10_ONLY |
| US | [EPR](https://www.tradingview.com/chart/?symbol=EPR) | 2026-08-20 | 61.23 | -0.77% | -12.31% | — | 2026-10-01 | DOWN10_ONLY |
| US | [TRIN](https://www.tradingview.com/chart/?symbol=TRIN) | 2026-08-20 | 18.27 | 1.38% | -12.28% | — | 2026-10-16 | DOWN10_ONLY |
| US | [SENEA](https://www.tradingview.com/chart/?symbol=SENEA) | 2026-08-26 | 191.5 | 9.64% | -12.14% | — | 2026-10-06 | DOWN10_ONLY |
| US | [TIC](https://www.tradingview.com/chart/?symbol=TIC) | 2026-09-21 | 9.245 | 1.41% | -12.11% | — | 2026-09-30 | DOWN10_ONLY |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-08-23 | 104.2 | 3.15% | -12.09% | — | 2026-10-07 | DOWN10_ONLY |
| US | [HTHT](https://www.tradingview.com/chart/?symbol=HTHT) | 2026-09-01 | 46.97 | -0.79% | -12.09% | — | 2026-09-24 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-23 | 175.2 | 3.21% | -12.00% | — | 2026-09-22 | DOWN10_ONLY |
| US | [BVS](https://www.tradingview.com/chart/?symbol=BVS) | 2026-08-24 | 14.01 | 3.50% | -11.92% | — | 2026-09-18 | DOWN10_ONLY |
| US | [DK](https://www.tradingview.com/chart/?symbol=DK) | 2026-09-14 | 74.42 | 10.55% | -11.88% | 2026-09-17 | 2026-09-24 | UP10_FIRST |
| HK | [0656](https://www.tradingview.com/chart/?symbol=HKEX%3A656) | 2026-08-21 | 5.115 | 10.75% | -11.83% | 2026-09-01 | 2026-10-08 | UP10_FIRST |
| HK | [6655](https://www.tradingview.com/chart/?symbol=HKEX%3A6655) | 2026-09-18 | 16.33 | 0.98% | -11.76% | — | 2026-10-05 | DOWN10_ONLY |
| US | [CCK](https://www.tradingview.com/chart/?symbol=CCK) | 2026-08-20 | 117.1 | 3.74% | -11.73% | — | 2026-09-30 | DOWN10_ONLY |
| US | [AHR](https://www.tradingview.com/chart/?symbol=AHR) | 2026-08-20 | 55.79 | 2.50% | -11.72% | — | 2026-10-06 | DOWN10_ONLY |
| US | [FLNG](https://www.tradingview.com/chart/?symbol=FLNG) | 2026-09-02 | 31.77 | 3.79% | -11.65% | — | 2026-10-15 | DOWN10_ONLY |
| US | [DAR](https://www.tradingview.com/chart/?symbol=DAR) | 2026-09-08 | 67.13 | 2.26% | -11.57% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [BHC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABHC) | 2026-08-31 | 8.8 | 9.66% | -11.48% | — | 2026-09-15 | DOWN10_ONLY |
| US | [MRX](https://www.tradingview.com/chart/?symbol=MRX) | 2026-09-03 | 75.72 | 4.48% | -11.46% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SUN](https://www.tradingview.com/chart/?symbol=SUN) | 2026-09-16 | 78.93 | 0.43% | -11.45% | — | 2026-10-05 | DOWN10_ONLY |
| US | [NEU](https://www.tradingview.com/chart/?symbol=NEU) | 2026-08-23 | 937.6 | 0.19% | -11.42% | — | 2026-09-09 | DOWN10_ONLY |
| US | [VRTX](https://www.tradingview.com/chart/?symbol=VRTX) | 2026-09-04 | 546.2 | -2.06% | -11.38% | — | 2026-10-13 | DOWN10_ONLY |
| US | [WES](https://www.tradingview.com/chart/?symbol=WES) | 2026-09-04 | 49.55 | 0.70% | -11.35% | — | 2026-09-29 | DOWN10_ONLY |
| US | [BSBR](https://www.tradingview.com/chart/?symbol=BSBR) | 2026-09-14 | 5.945 | 1.26% | -11.35% | — | 2026-10-01 | DOWN10_ONLY |
| US | [ROG](https://www.tradingview.com/chart/?symbol=ROG) | 2026-10-09 | 147.3 | -0.40% | -11.31% | — | 2026-10-15 | DOWN10_ONLY |
| US | [HTO](https://www.tradingview.com/chart/?symbol=HTO) | 2026-08-20 | 64.29 | 1.40% | -11.28% | — | 2026-10-07 | DOWN10_ONLY |
| US | [LNC](https://www.tradingview.com/chart/?symbol=LNC) | 2026-08-26 | 43.33 | 4.77% | -11.26% | — | 2026-10-01 | DOWN10_ONLY |
| US | [CSX](https://www.tradingview.com/chart/?symbol=CSX) | 2026-08-23 | 51.59 | 0.80% | -11.25% | — | 2026-09-21 | DOWN10_ONLY |
| US | [MMM](https://www.tradingview.com/chart/?symbol=MMM) | 2026-08-25 | 179.4 | 0.73% | -11.23% | — | 2026-09-10 | DOWN10_ONLY |
| US | [WSBC](https://www.tradingview.com/chart/?symbol=WSBC) | 2026-08-25 | 40.51 | 2.74% | -11.08% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [IGM.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIGM) | 2026-08-25 | 88.75 | 1.31% | -10.96% | — | 2026-10-08 | DOWN10_ONLY |
| US | [TEAM](https://www.tradingview.com/chart/?symbol=TEAM) | 2026-09-22 | 188.7 | 18.54% | -10.95% | 2026-10-12 | 2026-09-29 | DOWN10_FIRST |
| US | [NSC](https://www.tradingview.com/chart/?symbol=NSC) | 2026-08-31 | 342.8 | 0.23% | -10.89% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [0013](https://www.tradingview.com/chart/?symbol=HKEX%3A13) | 2026-10-01 | 23 | 0.00% | -10.87% | — | 2026-10-13 | DOWN10_ONLY |
| US | [RDNT](https://www.tradingview.com/chart/?symbol=RDNT) | 2026-09-10 | 74.3 | 7.36% | -10.86% | — | 2026-10-08 | DOWN10_ONLY |
| US | [PR](https://www.tradingview.com/chart/?symbol=PR) | 2026-09-04 | 23.35 | 5.44% | -10.75% | — | 2026-09-29 | DOWN10_ONLY |
| US | [TSLX](https://www.tradingview.com/chart/?symbol=TSLX) | 2026-08-24 | 18.91 | -1.32% | -10.74% | — | 2026-10-07 | DOWN10_ONLY |
| US | [KB](https://www.tradingview.com/chart/?symbol=KB) | 2026-09-16 | 128 | 3.02% | -10.67% | — | 2026-10-15 | DOWN10_ONLY |
| US | [MDLZ](https://www.tradingview.com/chart/?symbol=MDLZ) | 2026-08-20 | 64.16 | 1.27% | -10.66% | — | 2026-10-01 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-08-26 | 34.81 | 9.65% | -10.63% | — | 2026-09-28 | DOWN10_ONLY |
| US | [ING](https://www.tradingview.com/chart/?symbol=ING) | 2026-09-15 | 36.77 | 0.86% | -10.62% | — | 2026-10-08 | DOWN10_ONLY |
| US | [MTDR](https://www.tradingview.com/chart/?symbol=MTDR) | 2026-08-28 | 56.36 | 13.24% | -10.59% | 2026-09-10 | 2026-09-29 | UP10_FIRST |
| US | [CNMD](https://www.tradingview.com/chart/?symbol=CNMD) | 2026-09-01 | 49.15 | 3.58% | -10.54% | — | 2026-10-07 | DOWN10_ONLY |
| US | [EPC](https://www.tradingview.com/chart/?symbol=EPC) | 2026-08-25 | 28.95 | 1.25% | -10.54% | — | 2026-09-15 | DOWN10_ONLY |
| US | [UNM](https://www.tradingview.com/chart/?symbol=UNM) | 2026-09-15 | 95.88 | 0.91% | -10.52% | — | 2026-10-01 | DOWN10_ONLY |
| US | [WDS](https://www.tradingview.com/chart/?symbol=WDS) | 2026-09-15 | 23.96 | -0.75% | -10.52% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [BTE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABTE) | 2026-09-11 | 6.96 | 8.19% | -10.49% | — | 2026-09-29 | DOWN10_ONLY |
| US | [GTM](https://www.tradingview.com/chart/?symbol=GTM) | 2026-09-08 | 3.91 | 11.51% | -10.49% | 2026-09-15 | 2026-09-28 | UP10_FIRST |
| US | [OXY](https://www.tradingview.com/chart/?symbol=OXY) | 2026-09-10 | 61.16 | 4.26% | -10.47% | — | 2026-09-29 | DOWN10_ONLY |
| US | [TTEK](https://www.tradingview.com/chart/?symbol=TTEK) | 2026-09-01 | 35.75 | 4.25% | -10.43% | — | 2026-10-07 | DOWN10_ONLY |
| US | [GDRX](https://www.tradingview.com/chart/?symbol=GDRX) | 2026-09-14 | 3.57 | 0.20% | -10.36% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [TNZ.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATNZ) | 2026-09-21 | 69.33 | 7.18% | -10.36% | — | 2026-09-29 | DOWN10_ONLY |
| HK | [3600](https://www.tradingview.com/chart/?symbol=HKEX%3A3600) | 2026-08-24 | 8.22 | 2.07% | -10.34% | — | 2026-09-14 | DOWN10_ONLY |
| US | [MH](https://www.tradingview.com/chart/?symbol=MH) | 2026-09-22 | 13.57 | 6.63% | -10.32% | — | 2026-09-28 | DOWN10_ONLY |
| Canada | [POU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APOU) | 2026-09-11 | 31.98 | 7.88% | -10.27% | — | 2026-10-02 | DOWN10_ONLY |
| US | [AUGO](https://www.tradingview.com/chart/?symbol=AUGO) | 2026-09-15 | 85.77 | 9.00% | -10.23% | — | 2026-09-28 | DOWN10_ONLY |
| US | [PH](https://www.tradingview.com/chart/?symbol=PH) | 2026-08-24 | 1015 | 2.99% | -10.22% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SCCO](https://www.tradingview.com/chart/?symbol=SCCO) | 2026-09-02 | 204.3 | 4.69% | -10.16% | — | 2026-09-14 | DOWN10_ONLY |
| Canada | [PSK.TO](https://www.tradingview.com/chart/?symbol=TSX%3APSK) | 2026-08-25 | 36.05 | 2.63% | -10.12% | — | 2026-10-02 | DOWN10_ONLY |
| US | [BF-B](https://www.tradingview.com/chart/?symbol=BF-B) | 2026-08-20 | 28.42 | 2.99% | -10.10% | — | 2026-09-16 | DOWN10_ONLY |
| US | [BWIN](https://www.tradingview.com/chart/?symbol=BWIN) | 2026-08-31 | 30.85 | 6.01% | -10.08% | — | 2026-09-09 | DOWN10_ONLY |
| US | [RPRX](https://www.tradingview.com/chart/?symbol=RPRX) | 2026-08-23 | 61.3 | 5.02% | -10.07% | — | 2026-10-08 | DOWN10_ONLY |
| US | [CCEP](https://www.tradingview.com/chart/?symbol=CCEP) | 2026-08-24 | 110.1 | 2.17% | -10.07% | — | 2026-09-23 | DOWN10_ONLY |
| HK | [2356](https://www.tradingview.com/chart/?symbol=HKEX%3A2356) | 2026-08-27 | 14.81 | 1.69% | -10.03% | — | 2026-08-28 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **73**; -10%-only sample: **231**.
- +10%-only common candles: BEAR_CANDLE (23), BULL_CANDLE (22), STRONG_BULL_CANDLE (7), BULLISH_ENGULFING (4).
- -10%-only common candles: BULL_CANDLE (80), BEAR_CANDLE (43), STRONG_BULL_CANDLE (29), DOJI (24).
- Median RS: +10%-only **21.94** vs -10%-only **17.63**.
- Median % below 52w high: +10%-only **7.15** vs -10%-only **8.22**.
- Median breakout age: +10%-only **14.00** vs -10%-only **13.00**.
- Median quality score: +10%-only **4.00** vs -10%-only **4.00**.
- Median congestion score: +10%-only **1.00** vs -10%-only **1.00**.

## Pre-Entry Watch

### 🟢 Reached +10% — 203

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| HK | [2299](https://www.tradingview.com/chart/?symbol=HKEX%3A2299) | 2026-09-25 | 5.8 | 102.76% | 85.86% | 2026-09-28 | — | UP10_ONLY |
| US | [XP](https://www.tradingview.com/chart/?symbol=XP) | 2026-09-18 | 20.01 | 63.57% | -1.15% | 2026-10-05 | — | UP10_ONLY |
| US | [SDGR](https://www.tradingview.com/chart/?symbol=SDGR) | 2026-09-14 | 20.75 | 62.80% | -1.98% | 2026-09-15 | — | UP10_ONLY |
| HK | [0565](https://www.tradingview.com/chart/?symbol=HKEX%3A565) | 2026-09-04 | 3.38 | 61.24% | -0.74% | 2026-09-07 | — | UP10_ONLY |
| US | [TXG](https://www.tradingview.com/chart/?symbol=TXG) | 2026-09-10 | 66.38 | 54.88% | -2.49% | 2026-09-15 | — | UP10_ONLY |
| US | [CDNA](https://www.tradingview.com/chart/?symbol=CDNA) | 2026-08-24 | 47.5 | 52.65% | -1.71% | 2026-08-27 | — | UP10_ONLY |
| US | [ECO](https://www.tradingview.com/chart/?symbol=ECO) | 2026-08-31 | 66.74 | 50.86% | 0.19% | 2026-09-10 | — | UP10_ONLY |
| US | [PCVX](https://www.tradingview.com/chart/?symbol=PCVX) | 2026-08-20 | 61.34 | 47.95% | -10.20% | 2026-10-05 | 2026-09-23 | DOWN10_FIRST |
| HK | [0805](https://www.tradingview.com/chart/?symbol=HKEX%3A805) | 2026-09-04 | 9.815 | 47.12% | -20.94% | 2026-09-25 | 2026-09-07 | DOWN10_FIRST |
| Canada | [CVVY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACVVY) | 2026-08-24 | 1.89 | 42.86% | -2.65% | 2026-08-27 | — | UP10_ONLY |
| HK | [1112](https://www.tradingview.com/chart/?symbol=HKEX%3A1112) | 2026-08-21 | 15.63 | 42.55% | -12.92% | 2026-08-26 | 2026-08-24 | DOWN10_FIRST |
| US | [OKTA](https://www.tradingview.com/chart/?symbol=OKTA) | 2026-09-08 | 167.6 | 40.22% | -0.85% | 2026-09-14 | — | UP10_ONLY |
| US | [VEON](https://www.tradingview.com/chart/?symbol=VEON) | 2026-08-28 | 60.84 | 40.15% | -1.41% | 2026-09-04 | — | UP10_ONLY |
| US | [ILMN](https://www.tradingview.com/chart/?symbol=ILMN) | 2026-09-03 | 221.7 | 39.56% | -9.77% | 2026-09-17 | — | UP10_ONLY |
| US | [DINO](https://www.tradingview.com/chart/?symbol=DINO) | 2026-08-20 | 92.72 | 39.53% | -1.45% | 2026-08-31 | — | UP10_ONLY |
| Canada | [TGO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATGO) | 2026-08-20 | 1.5 | 38.00% | -25.33% | 2026-10-09 | 2026-09-08 | DOWN10_FIRST |
| US | [FRO](https://www.tradingview.com/chart/?symbol=FRO) | 2026-08-20 | 43.56 | 37.17% | -11.47% | 2026-09-15 | 2026-08-26 | DOWN10_FIRST |
| US | [DHT](https://www.tradingview.com/chart/?symbol=DHT) | 2026-08-24 | 19.72 | 36.46% | -7.45% | 2026-09-11 | — | UP10_ONLY |
| US | [MPC](https://www.tradingview.com/chart/?symbol=MPC) | 2026-08-20 | 358.2 | 35.45% | -2.95% | 2026-09-03 | — | UP10_ONLY |
| US | [RVTY](https://www.tradingview.com/chart/?symbol=RVTY) | 2026-08-24 | 123 | 35.16% | -1.71% | 2026-09-15 | — | UP10_ONLY |
| US | [VLO](https://www.tradingview.com/chart/?symbol=VLO) | 2026-08-20 | 341.5 | 35.14% | -1.91% | 2026-09-08 | — | UP10_ONLY |
| US | [NTRA](https://www.tradingview.com/chart/?symbol=NTRA) | 2026-08-24 | 327.7 | 33.47% | -3.58% | 2026-09-17 | — | UP10_ONLY |
| US | [TEN](https://www.tradingview.com/chart/?symbol=TEN) | 2026-08-28 | 42.52 | 33.42% | -1.18% | 2026-09-11 | — | UP10_ONLY |
| HK | [6821](https://www.tradingview.com/chart/?symbol=HKEX%3A6821) | 2026-09-04 | 133.8 | 33.03% | -3.14% | 2026-09-14 | — | UP10_ONLY |
| HK | [3396](https://www.tradingview.com/chart/?symbol=HKEX%3A3396) | 2026-09-17 | 19.78 | 32.56% | -12.08% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [HAFN](https://www.tradingview.com/chart/?symbol=HAFN) | 2026-08-31 | 8.44 | 31.52% | -4.75% | 2026-09-10 | — | UP10_ONLY |
| US | [CRWD](https://www.tradingview.com/chart/?symbol=CRWD) | 2026-08-28 | 218.4 | 31.41% | -8.15% | 2026-09-15 | — | UP10_ONLY |
| Canada | [MNO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMNO) | 2026-09-14 | 1.93 | 29.53% | -9.33% | 2026-09-22 | — | UP10_ONLY |
| Canada | [MSA.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMSA) | 2026-08-26 | 8.19 | 28.45% | -6.92% | 2026-09-10 | — | UP10_ONLY |
| US | [PBR-A](https://www.tradingview.com/chart/?symbol=PBR-A) | 2026-09-04 | 18.25 | 28.11% | 0.60% | 2026-10-05 | — | UP10_ONLY |
| US | [ATRC](https://www.tradingview.com/chart/?symbol=ATRC) | 2026-08-28 | 48.54 | 27.11% | -3.98% | 2026-09-03 | — | UP10_ONLY |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-08-20 | 99.36 | 27.09% | -10.78% | 2026-09-15 | 2026-08-26 | DOWN10_FIRST |
| US | [NAT](https://www.tradingview.com/chart/?symbol=NAT) | 2026-08-20 | 6.99 | 27.04% | -11.70% | 2026-09-14 | 2026-08-26 | DOWN10_FIRST |
| US | [XERS](https://www.tradingview.com/chart/?symbol=XERS) | 2026-09-25 | 8.95 | 26.59% | 0.56% | 2026-09-28 | — | UP10_ONLY |
| Canada | [TNZ.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATNZ) | 2026-08-25 | 60.07 | 26.52% | -1.48% | 2026-08-31 | — | UP10_ONLY |
| US | [UGP](https://www.tradingview.com/chart/?symbol=UGP) | 2026-08-20 | 6.55 | 26.41% | -3.66% | 2026-09-02 | — | UP10_ONLY |
| US | [NVAX](https://www.tradingview.com/chart/?symbol=NVAX) | 2026-09-25 | 10.6 | 26.32% | -3.21% | 2026-10-05 | — | UP10_ONLY |
| Canada | [LCFS.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALCFS) | 2026-09-17 | 20.43 | 26.28% | -0.88% | 2026-09-24 | — | UP10_ONLY |
| Canada | [HMM-A.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHMM.A) | 2026-08-23 | 23.2 | 25.86% | -3.79% | 2026-09-01 | — | UP10_ONLY |
| US | [PBF](https://www.tradingview.com/chart/?symbol=PBF) | 2026-08-23 | 73.53 | 25.74% | -13.03% | 2026-09-11 | 2026-08-26 | DOWN10_FIRST |
| US | [ZETA](https://www.tradingview.com/chart/?symbol=ZETA) | 2026-08-24 | 28.47 | 25.57% | -4.46% | 2026-09-01 | — | UP10_ONLY |
| US | [DT](https://www.tradingview.com/chart/?symbol=DT) | 2026-09-01 | 52.86 | 25.43% | -6.24% | 2026-09-23 | — | UP10_ONLY |
| US | [TWLO](https://www.tradingview.com/chart/?symbol=TWLO) | 2026-09-17 | 246.2 | 25.24% | -3.81% | 2026-09-22 | — | UP10_ONLY |
| US | [CNH](https://www.tradingview.com/chart/?symbol=CNH) | 2026-08-25 | 11.56 | 25.09% | -1.90% | 2026-09-02 | — | UP10_ONLY |
| US | [RNG](https://www.tradingview.com/chart/?symbol=RNG) | 2026-08-25 | 65.61 | 24.83% | -3.98% | 2026-09-02 | — | UP10_ONLY |
| US | [IDT](https://www.tradingview.com/chart/?symbol=IDT) | 2026-08-20 | 67.19 | 23.81% | -2.16% | 2026-09-29 | — | UP10_ONLY |
| US | [PBR](https://www.tradingview.com/chart/?symbol=PBR) | 2026-09-14 | 21.15 | 23.40% | -4.49% | 2026-10-05 | — | UP10_ONLY |
| US | [PSX](https://www.tradingview.com/chart/?symbol=PSX) | 2026-08-24 | 242 | 22.92% | -3.48% | 2026-09-15 | — | UP10_ONLY |
| US | [TNK](https://www.tradingview.com/chart/?symbol=TNK) | 2026-08-25 | 90.03 | 22.90% | -7.98% | 2026-09-11 | — | UP10_ONLY |
| US | [CLMT](https://www.tradingview.com/chart/?symbol=CLMT) | 2026-08-23 | 49.01 | 22.16% | -6.69% | 2026-09-02 | — | UP10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.65 | 21.91% | -25.91% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| US | [NEO](https://www.tradingview.com/chart/?symbol=NEO) | 2026-08-20 | 16.53 | 21.90% | -6.78% | 2026-08-27 | — | UP10_ONLY |
| US | [TK](https://www.tradingview.com/chart/?symbol=TK) | 2026-08-28 | 13.05 | 21.84% | -1.46% | 2026-09-11 | — | UP10_ONLY |
| US | [GMAB](https://www.tradingview.com/chart/?symbol=GMAB) | 2026-08-24 | 33.02 | 21.65% | -2.45% | 2026-10-05 | — | UP10_ONLY |
| Canada | [VLE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AVLE) | 2026-09-03 | 14.01 | 21.34% | -2.93% | 2026-09-16 | — | UP10_ONLY |
| US | [SLDE](https://www.tradingview.com/chart/?symbol=SLDE) | 2026-08-20 | 22.52 | 21.05% | -1.18% | 2026-09-03 | — | UP10_ONLY |
| US | [NTAP](https://www.tradingview.com/chart/?symbol=NTAP) | 2026-09-11 | 199.3 | 20.87% | -6.81% | 2026-10-02 | — | UP10_ONLY |
| US | [ADPT](https://www.tradingview.com/chart/?symbol=ADPT) | 2026-08-20 | 25.44 | 20.83% | -7.51% | 2026-09-16 | — | UP10_ONLY |
| US | [PGEN](https://www.tradingview.com/chart/?symbol=PGEN) | 2026-09-16 | 7.435 | 20.78% | -15.13% | 2026-09-25 | 2026-10-16 | UP10_FIRST |
| Canada | [ALC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALC) | 2026-08-23 | 24.84 | 20.77% | -14.32% | 2026-10-08 | 2026-08-26 | DOWN10_FIRST |
| US | [HPE](https://www.tradingview.com/chart/?symbol=HPE) | 2026-09-23 | 61.03 | 20.53% | -10.35% | 2026-10-02 | 2026-10-16 | UP10_FIRST |
| Canada | [RUS.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARUS) | 2026-09-17 | 79.67 | 20.46% | -1.14% | 2026-09-30 | — | UP10_ONLY |
| US | [CMBT](https://www.tradingview.com/chart/?symbol=CMBT) | 2026-08-20 | 17.62 | 20.26% | -2.21% | 2026-09-04 | — | UP10_ONLY |
| US | [CIG-C](https://www.tradingview.com/chart/?symbol=CIG-C) | 2026-09-10 | 3.36 | 20.24% | -7.23% | 2026-10-05 | — | UP10_ONLY |
| US | [BOX](https://www.tradingview.com/chart/?symbol=BOX) | 2026-08-26 | 33.39 | 20.04% | -8.83% | 2026-10-09 | — | UP10_ONLY |
| Canada | [LOVE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALOVE) | 2026-08-20 | 1.98 | 19.70% | -2.02% | 2026-09-23 | — | UP10_ONLY |
| Canada | [XLY.TO](https://www.tradingview.com/chart/?symbol=TSX%3AXLY) | 2026-09-01 | 3.14 | 19.43% | -0.96% | 2026-09-14 | — | UP10_ONLY |
| Canada | [MATR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMATR) | 2026-09-02 | 18.75 | 19.41% | -3.52% | 2026-09-10 | — | UP10_ONLY |
| Canada | [HWO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHWO) | 2026-09-16 | 1.1 | 19.09% | -9.09% | 2026-10-13 | — | UP10_ONLY |
| US | [HNGE](https://www.tradingview.com/chart/?symbol=HNGE) | 2026-08-24 | 89.98 | 18.92% | -4.70% | 2026-10-02 | — | UP10_ONLY |
| US | [PHVS](https://www.tradingview.com/chart/?symbol=PHVS) | 2026-08-20 | 36.39 | 18.85% | -23.94% | 2026-09-08 | 2026-09-24 | UP10_FIRST |
| US | [FTNT](https://www.tradingview.com/chart/?symbol=FTNT) | 2026-08-28 | 166 | 18.75% | -8.55% | 2026-10-02 | — | UP10_ONLY |
| US | [SIG](https://www.tradingview.com/chart/?symbol=SIG) | 2026-09-28 | 103.3 | 18.72% | -3.03% | 2026-10-15 | — | UP10_ONLY |
| Canada | [HFPC-U.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHFPC.U) | 2026-08-23 | 2.11 | 18.48% | -7.11% | 2026-10-13 | — | UP10_ONLY |
| US | [MTD](https://www.tradingview.com/chart/?symbol=MTD) | 2026-08-25 | 1402 | 18.36% | -9.68% | 2026-09-28 | — | UP10_ONLY |
| Canada | [KEI.TO](https://www.tradingview.com/chart/?symbol=TSX%3AKEI) | 2026-08-31 | 8.39 | 18.36% | -0.24% | 2026-09-09 | — | UP10_ONLY |
| US | [LPG](https://www.tradingview.com/chart/?symbol=LPG) | 2026-08-25 | 50.79 | 18.07% | -6.48% | 2026-09-14 | — | UP10_ONLY |
| US | [ZYME](https://www.tradingview.com/chart/?symbol=ZYME) | 2026-08-20 | 26.57 | 17.95% | -7.41% | 2026-08-25 | — | UP10_ONLY |
| US | [TEAM](https://www.tradingview.com/chart/?symbol=TEAM) | 2026-09-15 | 189.8 | 17.85% | -11.46% | 2026-10-12 | 2026-09-29 | DOWN10_FIRST |
| US | [NSIT](https://www.tradingview.com/chart/?symbol=NSIT) | 2026-08-25 | 150.6 | 17.73% | -0.94% | 2026-09-11 | — | UP10_ONLY |
| US | [FIVN](https://www.tradingview.com/chart/?symbol=FIVN) | 2026-08-28 | 34.05 | 17.47% | -11.60% | 2026-09-22 | 2026-09-09 | DOWN10_FIRST |
| Canada | [ORE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AORE) | 2026-09-16 | 2.91 | 16.84% | -4.98% | 2026-09-21 | — | UP10_ONLY |
| Canada | [LGD.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALGD) | 2026-09-08 | 1.97 | 16.75% | -11.17% | 2026-09-18 | 2026-10-14 | UP10_FIRST |
| US | [ELPC](https://www.tradingview.com/chart/?symbol=ELPC) | 2026-09-09 | 12.45 | 16.55% | -3.94% | 2026-10-05 | — | UP10_ONLY |
| US | [HAE](https://www.tradingview.com/chart/?symbol=HAE) | 2026-09-14 | 106.3 | 16.42% | -4.69% | 2026-10-08 | — | UP10_ONLY |
| US | [NEOG](https://www.tradingview.com/chart/?symbol=NEOG) | 2026-09-15 | 12.25 | 16.41% | -9.14% | 2026-09-21 | — | UP10_ONLY |
| US | [PLTR](https://www.tradingview.com/chart/?symbol=PLTR) | 2026-09-21 | 183.1 | 16.30% | -0.58% | 2026-10-08 | — | UP10_ONLY |
| Canada | [WFC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWFC) | 2026-08-20 | 20.85 | 16.21% | -9.35% | 2026-10-06 | — | UP10_ONLY |
| US | [DK](https://www.tradingview.com/chart/?symbol=DK) | 2026-08-26 | 70.84 | 16.13% | -7.43% | 2026-09-11 | — | UP10_ONLY |
| Canada | [SU.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASU) | 2026-09-09 | 95.29 | 16.04% | -2.88% | 2026-10-13 | — | UP10_ONLY |
| US | [RDVT](https://www.tradingview.com/chart/?symbol=RDVT) | 2026-08-20 | 70.53 | 15.97% | -3.01% | 2026-09-14 | — | UP10_ONLY |
| Canada | [YGR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AYGR) | 2026-08-24 | 1.57 | 15.92% | -10.19% | 2026-10-13 | 2026-09-30 | DOWN10_FIRST |
| US | [HGTY](https://www.tradingview.com/chart/?symbol=HGTY) | 2026-08-24 | 13.4 | 15.90% | -10.37% | 2026-10-13 | 2026-09-10 | DOWN10_FIRST |
| US | [DE](https://www.tradingview.com/chart/?symbol=DE) | 2026-08-20 | 620.9 | 15.87% | -2.33% | 2026-09-02 | — | UP10_ONLY |
| HK | [0023](https://www.tradingview.com/chart/?symbol=HKEX%3A23) | 2026-08-21 | 17.21 | 15.86% | -5.00% | 2026-09-14 | — | UP10_ONLY |
| US | [TBBB](https://www.tradingview.com/chart/?symbol=TBBB) | 2026-08-26 | 49.91 | 15.83% | -3.63% | 2026-10-09 | — | UP10_ONLY |
| US | [AMN](https://www.tradingview.com/chart/?symbol=AMN) | 2026-10-01 | 35.87 | 15.72% | -3.51% | 2026-10-15 | — | UP10_ONLY |
| US | [HPQ](https://www.tradingview.com/chart/?symbol=HPQ) | 2026-09-01 | 31.32 | 15.68% | -6.83% | 2026-09-11 | — | UP10_ONLY |
| US | [A](https://www.tradingview.com/chart/?symbol=A) | 2026-08-24 | 153.4 | 15.67% | -8.08% | 2026-09-24 | — | UP10_ONLY |
| US | [SNOW](https://www.tradingview.com/chart/?symbol=SNOW) | 2026-08-23 | 332.8 | 15.56% | -9.18% | 2026-09-03 | — | UP10_ONLY |
| US | [GIC](https://www.tradingview.com/chart/?symbol=GIC) | 2026-08-20 | 38.73 | 15.49% | -1.27% | 2026-09-29 | — | UP10_ONLY |
| US | [SU](https://www.tradingview.com/chart/?symbol=SU) | 2026-09-01 | 68.99 | 15.45% | -4.54% | 2026-10-14 | — | UP10_ONLY |
| US | [ROIV](https://www.tradingview.com/chart/?symbol=ROIV) | 2026-08-20 | 36.84 | 15.36% | -10.42% | 2026-09-08 | 2026-10-14 | UP10_FIRST |
| HK | [3328](https://www.tradingview.com/chart/?symbol=HKEX%3A3328) | 2026-08-24 | 7.56 | 15.08% | -1.98% | 2026-09-28 | — | UP10_ONLY |
| US | [CNXN](https://www.tradingview.com/chart/?symbol=CNXN) | 2026-09-04 | 84.35 | 14.89% | -2.93% | 2026-10-01 | — | UP10_ONLY |
| US | [JOYY](https://www.tradingview.com/chart/?symbol=JOYY) | 2026-08-20 | 73.77 | 14.88% | -3.21% | 2026-10-06 | — | UP10_ONLY |
| Canada | [SOIL.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASOIL) | 2026-09-18 | 7.13 | 14.73% | -9.12% | 2026-10-09 | — | UP10_ONLY |
| US | [DAC](https://www.tradingview.com/chart/?symbol=DAC) | 2026-08-23 | 149.8 | 14.68% | -2.42% | 2026-10-05 | — | UP10_ONLY |
| US | [ASIC](https://www.tradingview.com/chart/?symbol=ASIC) | 2026-08-20 | 25.29 | 14.67% | -1.15% | 2026-09-04 | — | UP10_ONLY |
| US | [APA](https://www.tradingview.com/chart/?symbol=APA) | 2026-08-24 | 42.96 | 14.66% | -5.82% | 2026-09-15 | — | UP10_ONLY |
| US | [SHG](https://www.tradingview.com/chart/?symbol=SHG) | 2026-08-23 | 74.63 | 14.66% | -6.66% | 2026-09-03 | — | UP10_ONLY |
| Canada | [ARE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AARE) | 2026-09-29 | 52.31 | 14.62% | -7.23% | 2026-10-02 | — | UP10_ONLY |
| Canada | [BDT.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABDT) | 2026-09-16 | 75.5 | 14.57% | -5.48% | 2026-09-22 | — | UP10_ONLY |
| Canada | [GUD.TO](https://www.tradingview.com/chart/?symbol=TSX%3AGUD) | 2026-08-25 | 9.75 | 14.46% | -4.31% | 2026-09-30 | — | UP10_ONLY |
| US | [NUTX](https://www.tradingview.com/chart/?symbol=NUTX) | 2026-09-03 | 197.7 | 14.41% | -7.48% | 2026-09-14 | — | UP10_ONLY |
| US | [WT](https://www.tradingview.com/chart/?symbol=WT) | 2026-08-20 | 22.65 | 14.39% | -11.04% | 2026-08-26 | 2026-10-15 | UP10_FIRST |
| US | [HALO](https://www.tradingview.com/chart/?symbol=HALO) | 2026-08-26 | 107.1 | 14.38% | -3.35% | 2026-10-14 | — | UP10_ONLY |
| HK | [0081](https://www.tradingview.com/chart/?symbol=HKEX%3A81) | 2026-09-16 | 2.865 | 14.31% | -8.03% | 2026-09-30 | — | UP10_ONLY |
| HK | [3988](https://www.tradingview.com/chart/?symbol=HKEX%3A3988) | 2026-08-24 | 5.505 | 14.26% | -0.91% | 2026-09-03 | — | UP10_ONLY |
| US | [CRGY](https://www.tradingview.com/chart/?symbol=CRGY) | 2026-08-28 | 13.54 | 14.25% | -8.42% | 2026-09-14 | — | UP10_ONLY |
| HK | [6616](https://www.tradingview.com/chart/?symbol=HKEX%3A6616) | 2026-08-31 | 9.79 | 14.20% | -9.09% | 2026-09-09 | — | UP10_ONLY |
| HK | [3339](https://www.tradingview.com/chart/?symbol=HKEX%3A3339) | 2026-08-21 | 3.17 | 14.20% | -9.94% | 2026-08-28 | — | UP10_ONLY |
| US | [NET](https://www.tradingview.com/chart/?symbol=NET) | 2026-09-16 | 324.6 | 14.08% | -10.32% | 2026-09-23 | 2026-10-16 | UP10_FIRST |
| US | [AVTR](https://www.tradingview.com/chart/?symbol=AVTR) | 2026-08-25 | 14.42 | 14.08% | -1.60% | 2026-09-17 | — | UP10_ONLY |
| US | [HRMY](https://www.tradingview.com/chart/?symbol=HRMY) | 2026-08-23 | 38.15 | 14.00% | -5.66% | 2026-09-02 | — | UP10_ONLY |
| US | [SHEL](https://www.tradingview.com/chart/?symbol=SHEL) | 2026-08-20 | 93.65 | 13.91% | -3.84% | 2026-10-13 | — | UP10_ONLY |
| US | [GH](https://www.tradingview.com/chart/?symbol=GH) | 2026-08-20 | 167.9 | 13.80% | -8.27% | 2026-10-05 | — | UP10_ONLY |
| US | [CON](https://www.tradingview.com/chart/?symbol=CON) | 2026-08-20 | 34.81 | 13.76% | -4.28% | 2026-10-15 | — | UP10_ONLY |
| US | [BWLP](https://www.tradingview.com/chart/?symbol=BWLP) | 2026-08-20 | 23.51 | 13.61% | -6.15% | 2026-09-15 | — | UP10_ONLY |
| US | [SM](https://www.tradingview.com/chart/?symbol=SM) | 2026-08-28 | 36.62 | 13.49% | -11.11% | 2026-09-15 | 2026-09-29 | UP10_FIRST |
| HK | [0517](https://www.tradingview.com/chart/?symbol=HKEX%3A517) | 2026-09-16 | 6.3 | 13.49% | -1.59% | 2026-10-09 | — | UP10_ONLY |
| US | [MCK](https://www.tradingview.com/chart/?symbol=MCK) | 2026-08-26 | 896.6 | 13.20% | -5.50% | 2026-10-15 | — | UP10_ONLY |
| US | [AMRX](https://www.tradingview.com/chart/?symbol=AMRX) | 2026-09-18 | 18.71 | 13.17% | 0.13% | 2026-09-21 | — | UP10_ONLY |
| US | [PANW](https://www.tradingview.com/chart/?symbol=PANW) | 2026-08-31 | 382.1 | 13.14% | -15.90% | 2026-10-06 | 2026-09-02 | DOWN10_FIRST |
| US | [AMPL](https://www.tradingview.com/chart/?symbol=AMPL) | 2026-10-02 | 14.3 | 13.11% | 1.12% | 2026-10-09 | — | UP10_ONLY |
| Canada | [ARG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AARG) | 2026-08-23 | 8.06 | 13.03% | -5.26% | 2026-09-21 | — | UP10_ONLY |
| US | [SFL](https://www.tradingview.com/chart/?symbol=SFL) | 2026-08-28 | 12.37 | 13.02% | -2.30% | 2026-09-16 | — | UP10_ONLY |
| US | [TGB](https://www.tradingview.com/chart/?symbol=TGB) | 2026-08-20 | 8.69 | 13.00% | -13.12% | 2026-08-25 | 2026-09-14 | UP10_FIRST |
| US | [EXEL](https://www.tradingview.com/chart/?symbol=EXEL) | 2026-08-26 | 56.1 | 12.99% | -4.76% | 2026-10-15 | — | UP10_ONLY |
| Canada | [DCBO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ADCBO) | 2026-10-09 | 36.13 | 12.95% | 0.28% | 2026-10-15 | — | UP10_ONLY |
| US | [CRL](https://www.tradingview.com/chart/?symbol=CRL) | 2026-08-26 | 295.1 | 12.94% | -9.43% | 2026-10-06 | — | UP10_ONLY |
| US | [AVPT](https://www.tradingview.com/chart/?symbol=AVPT) | 2026-09-28 | 13.67 | 12.87% | -2.67% | 2026-10-06 | — | UP10_ONLY |
| HK | [1258](https://www.tradingview.com/chart/?symbol=HKEX%3A1258) | 2026-08-25 | 15.81 | 12.78% | -13.92% | 2026-08-26 | 2026-10-15 | UP10_FIRST |
| HK | [1308](https://www.tradingview.com/chart/?symbol=HKEX%3A1308) | 2026-09-01 | 46.24 | 12.78% | -6.79% | 2026-10-12 | — | UP10_ONLY |
| Canada | [SGY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASGY) | 2026-08-23 | 11.22 | 12.76% | -6.96% | 2026-09-14 | — | UP10_ONLY |
| US | [SAIC](https://www.tradingview.com/chart/?symbol=SAIC) | 2026-08-20 | 126.3 | 12.64% | -4.19% | 2026-08-31 | — | UP10_ONLY |
| US | [NMR](https://www.tradingview.com/chart/?symbol=NMR) | 2026-08-23 | 9.72 | 12.55% | -7.41% | 2026-09-04 | — | UP10_ONLY |
| US | [TEVA](https://www.tradingview.com/chart/?symbol=TEVA) | 2026-08-23 | 37.34 | 12.53% | -5.14% | 2026-10-09 | — | UP10_ONLY |
| US | [BIIB](https://www.tradingview.com/chart/?symbol=BIIB) | 2026-08-20 | 214.3 | 12.43% | -2.53% | 2026-10-12 | — | UP10_ONLY |
| US | [FCX](https://www.tradingview.com/chart/?symbol=FCX) | 2026-08-20 | 71.22 | 12.42% | -7.15% | 2026-08-24 | — | UP10_ONLY |
| US | [FRSH](https://www.tradingview.com/chart/?symbol=FRSH) | 2026-08-23 | 12.98 | 12.33% | -9.83% | 2026-10-06 | — | UP10_ONLY |
| US | [WAT](https://www.tradingview.com/chart/?symbol=WAT) | 2026-08-20 | 404.7 | 12.32% | -2.90% | 2026-09-28 | — | UP10_ONLY |
| US | [FFIV](https://www.tradingview.com/chart/?symbol=FFIV) | 2026-09-15 | 430.9 | 12.17% | -2.82% | 2026-10-09 | — | UP10_ONLY |
| US | [PRLB](https://www.tradingview.com/chart/?symbol=PRLB) | 2026-09-24 | 89.13 | 12.15% | -5.76% | 2026-09-29 | — | UP10_ONLY |
| US | [GCT](https://www.tradingview.com/chart/?symbol=GCT) | 2026-09-25 | 53.91 | 12.13% | -8.31% | 2026-10-15 | — | UP10_ONLY |
| Canada | [CRON.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACRON) | 2026-08-20 | 4.45 | 12.13% | -3.60% | 2026-08-25 | — | UP10_ONLY |
| US | [VEEV](https://www.tradingview.com/chart/?symbol=VEEV) | 2026-10-01 | 285.4 | 12.09% | -4.42% | 2026-10-15 | — | UP10_ONLY |
| US | [CRON](https://www.tradingview.com/chart/?symbol=CRON) | 2026-08-20 | 3.22 | 12.05% | -4.04% | 2026-08-25 | — | UP10_ONLY |
| Canada | [WCP.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWCP) | 2026-08-24 | 18.03 | 11.92% | -5.14% | 2026-10-16 | — | UP10_ONLY |
| US | [GILD](https://www.tradingview.com/chart/?symbol=GILD) | 2026-08-20 | 143.4 | 11.90% | -0.74% | 2026-10-15 | — | UP10_ONLY |
| US | [TMO](https://www.tradingview.com/chart/?symbol=TMO) | 2026-08-23 | 629.3 | 11.88% | -5.55% | 2026-10-06 | — | UP10_ONLY |
| Canada | [ACX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AACX) | 2026-09-04 | 7.7 | 11.69% | -6.10% | 2026-10-13 | — | UP10_ONLY |
| HK | [0144](https://www.tradingview.com/chart/?symbol=HKEX%3A144) | 2026-09-03 | 16.18 | 11.68% | -3.07% | 2026-10-14 | — | UP10_ONLY |
| Canada | [RIO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIO) | 2026-09-03 | 3.52 | 11.65% | -19.03% | 2026-09-22 | 2026-09-30 | UP10_FIRST |
| Canada | [SXGC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASXGC) | 2026-08-24 | 12.19 | 11.57% | -21.58% | 2026-09-22 | 2026-10-05 | UP10_FIRST |
| US | [XOM](https://www.tradingview.com/chart/?symbol=XOM) | 2026-08-25 | 160.6 | 11.53% | -3.31% | 2026-10-14 | — | UP10_ONLY |
| US | [WF](https://www.tradingview.com/chart/?symbol=WF) | 2026-08-28 | 73.33 | 11.47% | -6.56% | 2026-09-14 | — | UP10_ONLY |
| US | [HUM](https://www.tradingview.com/chart/?symbol=HUM) | 2026-09-11 | 409.8 | 11.40% | -9.92% | 2026-10-09 | — | UP10_ONLY |
| US | [FTRE](https://www.tradingview.com/chart/?symbol=FTRE) | 2026-10-05 | 21.11 | 11.37% | -6.30% | 2026-10-06 | — | UP10_ONLY |
| HK | [1801](https://www.tradingview.com/chart/?symbol=HKEX%3A1801) | 2026-08-21 | 101.2 | 11.36% | -13.98% | 2026-08-26 | 2026-10-09 | UP10_FIRST |
| US | [CF](https://www.tradingview.com/chart/?symbol=CF) | 2026-08-25 | 127.3 | 11.32% | -13.08% | 2026-09-02 | 2026-09-25 | UP10_FIRST |
| US | [NTR](https://www.tradingview.com/chart/?symbol=NTR) | 2026-08-26 | 73.61 | 11.29% | -9.10% | 2026-09-08 | — | UP10_ONLY |
| US | [ABBV](https://www.tradingview.com/chart/?symbol=ABBV) | 2026-08-20 | 261.8 | 11.29% | -6.33% | 2026-10-15 | — | UP10_ONLY |
| US | [SCCO](https://www.tradingview.com/chart/?symbol=SCCO) | 2026-08-20 | 198.7 | 11.10% | -7.66% | 2026-08-24 | — | UP10_ONLY |
| US | [URBN](https://www.tradingview.com/chart/?symbol=URBN) | 2026-10-05 | 81.6 | 11.02% | -4.42% | 2026-10-16 | — | UP10_ONLY |
| HK | [1138](https://www.tradingview.com/chart/?symbol=HKEX%3A1138) | 2026-10-05 | 19.77 | 10.98% | -9.76% | 2026-10-08 | — | UP10_ONLY |
| Canada | [ELF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AELF) | 2026-10-08 | 17.92 | 10.94% | 0.45% | 2026-10-15 | — | UP10_ONLY |
| US | [VOD](https://www.tradingview.com/chart/?symbol=VOD) | 2026-08-24 | 15.98 | 10.83% | -4.38% | 2026-09-14 | — | UP10_ONLY |
| US | [MTCH](https://www.tradingview.com/chart/?symbol=MTCH) | 2026-08-20 | 40.35 | 10.81% | -3.55% | 2026-09-15 | — | UP10_ONLY |
| US | [DB](https://www.tradingview.com/chart/?symbol=DB) | 2026-08-20 | 37.56 | 10.81% | -14.00% | 2026-09-03 | 2026-10-07 | UP10_FIRST |
| HK | [3866](https://www.tradingview.com/chart/?symbol=HKEX%3A3866) | 2026-08-21 | 4.88 | 10.76% | -2.66% | 2026-09-02 | — | UP10_ONLY |
| US | [MSFT](https://www.tradingview.com/chart/?symbol=MSFT) | 2026-09-17 | 497.8 | 10.73% | -1.34% | 2026-10-13 | — | UP10_ONLY |
| HK | [3968](https://www.tradingview.com/chart/?symbol=HKEX%3A3968) | 2026-08-21 | 49 | 10.71% | -1.47% | 2026-10-13 | — | UP10_ONLY |
| Canada | [ENI-UN.TO](https://www.tradingview.com/chart/?symbol=TSX%3AENI.UN) | 2026-09-28 | 2.34 | 10.68% | -2.99% | 2026-10-13 | — | UP10_ONLY |
| US | [V](https://www.tradingview.com/chart/?symbol=V) | 2026-08-20 | 365.7 | 10.67% | -2.46% | 2026-10-15 | — | UP10_ONLY |
| US | [RAPP](https://www.tradingview.com/chart/?symbol=RAPP) | 2026-08-20 | 47.85 | 10.62% | -43.73% | 2026-08-26 | 2026-09-10 | UP10_FIRST |
| US | [STNG](https://www.tradingview.com/chart/?symbol=STNG) | 2026-09-02 | 81.42 | 10.61% | -2.68% | 2026-09-17 | — | UP10_ONLY |
| Canada | [CJ.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACJ) | 2026-09-16 | 12.27 | 10.59% | -4.93% | 2026-10-14 | — | UP10_ONLY |
| US | [HP](https://www.tradingview.com/chart/?symbol=HP) | 2026-08-31 | 43.58 | 10.53% | -17.00% | 2026-09-02 | 2026-09-24 | UP10_FIRST |
| US | [S](https://www.tradingview.com/chart/?symbol=S) | 2026-09-25 | 23.98 | 10.51% | -12.09% | 2026-10-09 | 2026-10-16 | UP10_FIRST |
| US | [SJM](https://www.tradingview.com/chart/?symbol=SJM) | 2026-08-20 | 123 | 10.43% | -6.45% | 2026-08-27 | — | UP10_ONLY |
| US | [KB](https://www.tradingview.com/chart/?symbol=KB) | 2026-08-25 | 120.8 | 10.39% | -5.32% | 2026-09-03 | — | UP10_ONLY |
| US | [MT](https://www.tradingview.com/chart/?symbol=MT) | 2026-08-23 | 72.2 | 10.36% | -16.43% | 2026-09-08 | 2026-10-01 | UP10_FIRST |
| Canada | [CAS.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACAS) | 2026-09-04 | 17.09 | 10.36% | -3.86% | 2026-09-29 | — | UP10_ONLY |
| US | [BBY](https://www.tradingview.com/chart/?symbol=BBY) | 2026-08-24 | 87.48 | 10.35% | -13.23% | 2026-09-23 | 2026-08-27 | DOWN10_FIRST |
| US | [DOCU](https://www.tradingview.com/chart/?symbol=DOCU) | 2026-10-08 | 71.43 | 10.32% | -2.02% | 2026-10-16 | — | UP10_ONLY |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-08-26 | 180.3 | 10.30% | -12.68% | 2026-09-28 | 2026-09-10 | DOWN10_FIRST |
| Canada | [EPRX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEPRX) | 2026-09-29 | 11.86 | 10.29% | -22.43% | 2026-09-30 | 2026-10-02 | UP10_FIRST |
| US | [RGA](https://www.tradingview.com/chart/?symbol=RGA) | 2026-08-20 | 242.6 | 10.27% | -0.45% | 2026-10-16 | — | UP10_ONLY |
| Canada | [ALS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALS) | 2026-08-20 | 63.12 | 10.19% | -11.28% | 2026-09-22 | 2026-10-16 | UP10_FIRST |
| Canada | [IPCO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIPCO) | 2026-09-17 | 35.73 | 10.16% | -6.24% | 2026-10-16 | — | UP10_ONLY |
| US | [TWFG](https://www.tradingview.com/chart/?symbol=TWFG) | 2026-08-20 | 28.44 | 10.06% | -18.78% | 2026-08-25 | 2026-09-22 | UP10_FIRST |
| US | [COKE](https://www.tradingview.com/chart/?symbol=COKE) | 2026-08-24 | 192.6 | 10.00% | -4.24% | 2026-10-15 | — | UP10_ONLY |

### 🔴 Reached -10% — 468

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [CTVA](https://www.tradingview.com/chart/?symbol=CTVA) | 2026-09-01 | 87.73 | -83.34% | -86.92% | — | 2026-09-02 | DOWN10_ONLY |
| US | [NESR](https://www.tradingview.com/chart/?symbol=NESR) | 2026-08-31 | 35.11 | 0.97% | -47.45% | — | 2026-09-16 | DOWN10_ONLY |
| US | [DYN](https://www.tradingview.com/chart/?symbol=DYN) | 2026-08-20 | 25.98 | 3.43% | -45.61% | — | 2026-09-08 | DOWN10_ONLY |
| US | [RAPP](https://www.tradingview.com/chart/?symbol=RAPP) | 2026-08-20 | 47.85 | 10.62% | -43.73% | 2026-08-26 | 2026-09-10 | UP10_FIRST |
| US | [IMNM](https://www.tradingview.com/chart/?symbol=IMNM) | 2026-08-26 | 28.75 | 1.25% | -42.92% | — | 2026-09-10 | DOWN10_ONLY |
| US | [CGEM](https://www.tradingview.com/chart/?symbol=CGEM) | 2026-08-31 | 22.07 | 3.26% | -41.96% | — | 2026-09-14 | DOWN10_ONLY |
| US | [ANRO](https://www.tradingview.com/chart/?symbol=ANRO) | 2026-09-03 | 36.4 | 1.59% | -41.43% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [FM.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFM) | 2026-08-28 | 47.76 | 0.77% | -41.37% | — | 2026-09-10 | DOWN10_ONLY |
| HK | [6993](https://www.tradingview.com/chart/?symbol=HKEX%3A6993) | 2026-09-04 | 3.735 | 4.07% | -40.83% | — | 2026-09-18 | DOWN10_ONLY |
| US | [IMVT](https://www.tradingview.com/chart/?symbol=IMVT) | 2026-08-20 | 44.35 | 1.74% | -40.76% | — | 2026-08-31 | DOWN10_ONLY |
| Canada | [HMMC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHMMC) | 2026-09-10 | 8.15 | 3.93% | -40.67% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [RTG.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARTG) | 2026-10-02 | 0.05 | 0.00% | -40.00% | — | 2026-10-06 | DOWN10_ONLY |
| US | [RUSHB](https://www.tradingview.com/chart/?symbol=RUSHB) | 2026-08-23 | 79.16 | -25.66% | -38.85% | — | 2026-08-24 | DOWN10_ONLY |
| US | [ELVN](https://www.tradingview.com/chart/?symbol=ELVN) | 2026-08-23 | 59.82 | 3.64% | -38.22% | — | 2026-09-15 | DOWN10_ONLY |
| US | [DNTH](https://www.tradingview.com/chart/?symbol=DNTH) | 2026-08-25 | 112.1 | 0.02% | -38.07% | — | 2026-09-17 | DOWN10_ONLY |
| US | [ACAD](https://www.tradingview.com/chart/?symbol=ACAD) | 2026-08-23 | 29.5 | 4.27% | -37.66% | — | 2026-09-21 | DOWN10_ONLY |
| US | [PCG](https://www.tradingview.com/chart/?symbol=PCG) | 2026-08-20 | 17.96 | 2.03% | -34.73% | — | 2026-08-28 | DOWN10_ONLY |
| US | [MAN](https://www.tradingview.com/chart/?symbol=MAN) | 2026-08-26 | 61.96 | 3.10% | -33.83% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [TLG.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATLG) | 2026-09-22 | 2.36 | -2.54% | -33.05% | — | 2026-09-24 | DOWN10_ONLY |
| US | [AXGN](https://www.tradingview.com/chart/?symbol=AXGN) | 2026-08-23 | 50.4 | 4.98% | -31.75% | — | 2026-09-10 | DOWN10_ONLY |
| US | [SRRK](https://www.tradingview.com/chart/?symbol=SRRK) | 2026-08-23 | 56.5 | 9.31% | -31.52% | — | 2026-09-15 | DOWN10_ONLY |
| US | [MRP](https://www.tradingview.com/chart/?symbol=MRP) | 2026-08-28 | 30.61 | 1.72% | -31.17% | — | 2026-09-18 | DOWN10_ONLY |
| US | [FRNM](https://www.tradingview.com/chart/?symbol=FRNM) | 2026-10-05 | 16.83 | 2.79% | -30.90% | — | 2026-10-12 | DOWN10_ONLY |
| HK | [3928](https://www.tradingview.com/chart/?symbol=HKEX%3A3928) | 2026-08-31 | 28.3 | 1.70% | -29.75% | — | 2026-09-01 | DOWN10_ONLY |
| US | [GEN](https://www.tradingview.com/chart/?symbol=GEN) | 2026-08-23 | 28.93 | 9.40% | -29.69% | — | 2026-09-24 | DOWN10_ONLY |
| US | [CMPS](https://www.tradingview.com/chart/?symbol=CMPS) | 2026-09-18 | 15.19 | 2.37% | -29.43% | — | 2026-09-24 | DOWN10_ONLY |
| HK | [0992](https://www.tradingview.com/chart/?symbol=HKEX%3A992) | 2026-09-24 | 36.02 | 3.55% | -29.09% | — | 2026-10-08 | DOWN10_ONLY |
| Canada | [WEF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWEF) | 2026-08-20 | 19.49 | 2.36% | -28.99% | — | 2026-09-01 | DOWN10_ONLY |
| Canada | [NGEX.TO](https://www.tradingview.com/chart/?symbol=TSX%3ANGEX) | 2026-08-23 | 29.07 | 4.64% | -28.90% | — | 2026-09-01 | DOWN10_ONLY |
| US | [RCUS](https://www.tradingview.com/chart/?symbol=RCUS) | 2026-08-23 | 30.34 | 4.09% | -28.81% | — | 2026-09-10 | DOWN10_ONLY |
| US | [SYRE](https://www.tradingview.com/chart/?symbol=SYRE) | 2026-08-20 | 107.8 | 2.19% | -28.69% | — | 2026-08-26 | DOWN10_ONLY |
| US | [TRU](https://www.tradingview.com/chart/?symbol=TRU) | 2026-08-20 | 85.11 | 1.52% | -28.38% | — | 2026-09-04 | DOWN10_ONLY |
| US | [VRTS](https://www.tradingview.com/chart/?symbol=VRTS) | 2026-08-25 | 166.3 | 1.75% | -27.72% | — | 2026-09-11 | DOWN10_ONLY |
| Canada | [ELE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AELE) | 2026-09-17 | 30.24 | 4.34% | -27.02% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RELY](https://www.tradingview.com/chart/?symbol=RELY) | 2026-08-23 | 26.67 | 3.03% | -26.79% | — | 2026-09-09 | DOWN10_ONLY |
| US | [APAM](https://www.tradingview.com/chart/?symbol=APAM) | 2026-08-20 | 42.05 | 5.28% | -26.61% | — | 2026-09-11 | DOWN10_ONLY |
| US | [BKNG](https://www.tradingview.com/chart/?symbol=BKNG) | 2026-08-23 | 209.6 | 3.42% | -26.51% | — | 2026-09-08 | DOWN10_ONLY |
| US | [CBRL](https://www.tradingview.com/chart/?symbol=CBRL) | 2026-08-23 | 57.65 | 21.91% | -25.91% | 2026-10-15 | 2026-09-09 | DOWN10_FIRST |
| Canada | [JAG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AJAG) | 2026-09-22 | 8.19 | -3.05% | -25.89% | — | 2026-09-28 | DOWN10_ONLY |
| Canada | [DC-A.TO](https://www.tradingview.com/chart/?symbol=TSX%3ADC.A) | 2026-09-22 | 5.43 | -0.00% | -25.78% | — | 2026-09-28 | DOWN10_ONLY |
| US | [HESM](https://www.tradingview.com/chart/?symbol=HESM) | 2026-08-31 | 40.21 | 2.76% | -25.76% | — | 2026-10-07 | DOWN10_ONLY |
| US | [RHI](https://www.tradingview.com/chart/?symbol=RHI) | 2026-08-20 | 43.88 | 5.03% | -25.59% | — | 2026-09-08 | DOWN10_ONLY |
| US | [JLL](https://www.tradingview.com/chart/?symbol=JLL) | 2026-08-20 | 384.3 | 2.29% | -25.45% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [TGO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATGO) | 2026-08-20 | 1.5 | 38.00% | -25.33% | 2026-10-09 | 2026-09-08 | DOWN10_FIRST |
| US | [PJT](https://www.tradingview.com/chart/?symbol=PJT) | 2026-08-26 | 174.8 | 7.32% | -24.83% | — | 2026-09-15 | DOWN10_ONLY |
| US | [FRPT](https://www.tradingview.com/chart/?symbol=FRPT) | 2026-08-23 | 73.97 | 4.28% | -24.29% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [SWP.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASWP) | 2026-09-21 | 9.27 | 0.86% | -24.27% | — | 2026-09-28 | DOWN10_ONLY |
| US | [IMCR](https://www.tradingview.com/chart/?symbol=IMCR) | 2026-08-20 | 36.28 | 4.61% | -24.20% | — | 2026-09-11 | DOWN10_ONLY |
| US | [EWTX](https://www.tradingview.com/chart/?symbol=EWTX) | 2026-09-17 | 46.94 | -0.02% | -24.09% | — | 2026-09-23 | DOWN10_ONLY |
| US | [PHVS](https://www.tradingview.com/chart/?symbol=PHVS) | 2026-08-20 | 36.39 | 18.85% | -23.94% | 2026-09-08 | 2026-09-24 | UP10_FIRST |
| US | [ETSY](https://www.tradingview.com/chart/?symbol=ETSY) | 2026-08-24 | 87.03 | 3.77% | -23.92% | — | 2026-09-04 | DOWN10_ONLY |
| US | [CCS](https://www.tradingview.com/chart/?symbol=CCS) | 2026-08-25 | 70.31 | 0.27% | -23.89% | — | 2026-09-03 | DOWN10_ONLY |
| US | [NLY](https://www.tradingview.com/chart/?symbol=NLY) | 2026-08-20 | 23.29 | -3.07% | -23.74% | — | 2026-09-14 | DOWN10_ONLY |
| US | [CGON](https://www.tradingview.com/chart/?symbol=CGON) | 2026-08-20 | 77.61 | 3.89% | -23.50% | — | 2026-09-24 | DOWN10_ONLY |
| US | [PVLA](https://www.tradingview.com/chart/?symbol=PVLA) | 2026-08-26 | 154.3 | 4.22% | -23.39% | — | 2026-09-25 | DOWN10_ONLY |
| HK | [1184](https://www.tradingview.com/chart/?symbol=HKEX%3A1184) | 2026-09-02 | 8.805 | -1.95% | -23.34% | — | 2026-09-18 | DOWN10_ONLY |
| US | [TVTX](https://www.tradingview.com/chart/?symbol=TVTX) | 2026-08-20 | 64.46 | 6.62% | -23.27% | — | 2026-10-01 | DOWN10_ONLY |
| HK | [2628](https://www.tradingview.com/chart/?symbol=HKEX%3A2628) | 2026-09-08 | 30.56 | -2.17% | -23.10% | — | 2026-10-02 | DOWN10_ONLY |
| US | [ARGX](https://www.tradingview.com/chart/?symbol=ARGX) | 2026-08-28 | 1023 | 4.84% | -23.01% | — | 2026-10-02 | DOWN10_ONLY |
| US | [AGNC](https://www.tradingview.com/chart/?symbol=AGNC) | 2026-08-20 | 10.92 | -1.37% | -22.99% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [EPRX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEPRX) | 2026-09-29 | 11.86 | 10.29% | -22.43% | 2026-09-30 | 2026-10-02 | UP10_FIRST |
| US | [DELL](https://www.tradingview.com/chart/?symbol=DELL) | 2026-10-07 | 579 | 2.78% | -22.27% | — | 2026-10-14 | DOWN10_ONLY |
| Canada | [SEA.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASEA) | 2026-08-24 | 45.86 | 5.89% | -22.20% | — | 2026-09-14 | DOWN10_ONLY |
| US | [VG](https://www.tradingview.com/chart/?symbol=VG) | 2026-09-01 | 15.11 | 7.59% | -22.17% | — | 2026-09-21 | DOWN10_ONLY |
| US | [ARIS](https://www.tradingview.com/chart/?symbol=ARIS) | 2026-09-03 | 20.55 | 1.24% | -22.17% | — | 2026-09-14 | DOWN10_ONLY |
| US | [OPK](https://www.tradingview.com/chart/?symbol=OPK) | 2026-09-18 | 1.67 | 5.99% | -22.16% | — | 2026-10-06 | DOWN10_ONLY |
| Canada | [CS.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACS) | 2026-08-20 | 15.4 | 8.57% | -22.01% | — | 2026-09-14 | DOWN10_ONLY |
| HK | [3939](https://www.tradingview.com/chart/?symbol=HKEX%3A3939) | 2026-09-16 | 15.8 | -0.07% | -22.00% | — | 2026-09-17 | DOWN10_ONLY |
| Canada | [IAU.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIAU) | 2026-09-22 | 2.62 | -2.67% | -21.95% | — | 2026-09-28 | DOWN10_ONLY |
| US | [FAF](https://www.tradingview.com/chart/?symbol=FAF) | 2026-09-03 | 76.51 | -2.06% | -21.92% | — | 2026-09-18 | DOWN10_ONLY |
| US | [EXPE](https://www.tradingview.com/chart/?symbol=EXPE) | 2026-08-20 | 324.2 | 5.35% | -21.91% | — | 2026-09-08 | DOWN10_ONLY |
| US | [MU](https://www.tradingview.com/chart/?symbol=MU) | 2026-10-02 | 1097 | -0.76% | -21.81% | — | 2026-10-12 | DOWN10_ONLY |
| US | [CNS](https://www.tradingview.com/chart/?symbol=CNS) | 2026-08-24 | 83.16 | 2.09% | -21.74% | — | 2026-09-11 | DOWN10_ONLY |
| US | [CHYM](https://www.tradingview.com/chart/?symbol=CHYM) | 2026-08-31 | 33.11 | 7.37% | -21.72% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [0966](https://www.tradingview.com/chart/?symbol=HKEX%3A966) | 2026-09-02 | 21.96 | 6.38% | -21.72% | — | 2026-09-28 | DOWN10_ONLY |
| US | [SLG](https://www.tradingview.com/chart/?symbol=SLG) | 2026-08-20 | 58.1 | 2.12% | -21.62% | — | 2026-09-08 | DOWN10_ONLY |
| Canada | [SXGC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASXGC) | 2026-08-24 | 12.19 | 11.57% | -21.58% | 2026-09-22 | 2026-10-05 | UP10_FIRST |
| US | [RLAY](https://www.tradingview.com/chart/?symbol=RLAY) | 2026-08-25 | 20.57 | -2.19% | -21.58% | — | 2026-08-31 | DOWN10_ONLY |
| US | [VIRT](https://www.tradingview.com/chart/?symbol=VIRT) | 2026-08-26 | 65.74 | 4.21% | -21.57% | — | 2026-09-15 | DOWN10_ONLY |
| US | [NRIX](https://www.tradingview.com/chart/?symbol=NRIX) | 2026-08-20 | 27.05 | 1.66% | -21.52% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [JOY.TO](https://www.tradingview.com/chart/?symbol=TSX%3AJOY) | 2026-09-11 | 6.13 | 1.79% | -21.37% | — | 2026-09-21 | DOWN10_ONLY |
| US | [BAC](https://www.tradingview.com/chart/?symbol=BAC) | 2026-09-02 | 62.6 | 1.96% | -21.31% | — | 2026-09-22 | DOWN10_ONLY |
| US | [PAYX](https://www.tradingview.com/chart/?symbol=PAYX) | 2026-08-23 | 124.5 | 2.81% | -21.27% | — | 2026-09-23 | DOWN10_ONLY |
| US | [ALNT](https://www.tradingview.com/chart/?symbol=ALNT) | 2026-10-06 | 117.2 | -1.10% | -21.19% | — | 2026-10-13 | DOWN10_ONLY |
| US | [OII](https://www.tradingview.com/chart/?symbol=OII) | 2026-08-20 | 52.49 | 2.59% | -21.15% | — | 2026-09-14 | DOWN10_ONLY |
| US | [HQH](https://www.tradingview.com/chart/?symbol=HQH) | 2026-08-20 | 23.84 | 0.25% | -21.06% | — | 2026-09-15 | DOWN10_ONLY |
| US | [JHX](https://www.tradingview.com/chart/?symbol=JHX) | 2026-08-20 | 30.03 | 4.66% | -20.95% | — | 2026-09-15 | DOWN10_ONLY |
| US | [NGL](https://www.tradingview.com/chart/?symbol=NGL) | 2026-09-01 | 18.33 | 3.55% | -20.95% | — | 2026-09-16 | DOWN10_ONLY |
| HK | [0805](https://www.tradingview.com/chart/?symbol=HKEX%3A805) | 2026-09-04 | 9.815 | 47.12% | -20.94% | 2026-09-25 | 2026-09-07 | DOWN10_FIRST |
| Canada | [CGG.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACGG) | 2026-09-10 | 47.05 | 4.12% | -20.85% | — | 2026-09-22 | DOWN10_ONLY |
| US | [GKOS](https://www.tradingview.com/chart/?symbol=GKOS) | 2026-08-20 | 184.9 | 1.47% | -20.83% | — | 2026-09-14 | DOWN10_ONLY |
| US | [ABNB](https://www.tradingview.com/chart/?symbol=ABNB) | 2026-08-26 | 188.1 | 1.82% | -20.77% | — | 2026-09-09 | DOWN10_ONLY |
| US | [CMG](https://www.tradingview.com/chart/?symbol=CMG) | 2026-09-03 | 37.57 | -0.40% | -20.76% | — | 2026-09-16 | DOWN10_ONLY |
| Canada | [MAU.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMAU) | 2026-08-26 | 20 | 5.65% | -20.75% | — | 2026-09-01 | DOWN10_ONLY |
| US | [MANU](https://www.tradingview.com/chart/?symbol=MANU) | 2026-08-20 | 24.02 | 0.29% | -20.69% | — | 2026-09-01 | DOWN10_ONLY |
| US | [TRLV](https://www.tradingview.com/chart/?symbol=TRLV) | 2026-09-28 | 12.34 | 1.62% | -20.64% | — | 2026-09-30 | DOWN10_ONLY |
| US | [BXP](https://www.tradingview.com/chart/?symbol=BXP) | 2026-08-25 | 72.13 | -0.97% | -20.52% | — | 2026-09-09 | DOWN10_ONLY |
| US | [BMRN](https://www.tradingview.com/chart/?symbol=BMRN) | 2026-08-20 | 67.68 | 0.98% | -20.36% | — | 2026-09-25 | DOWN10_ONLY |
| US | [SSRM](https://www.tradingview.com/chart/?symbol=SSRM) | 2026-09-02 | 37.75 | 4.48% | -20.24% | — | 2026-09-28 | DOWN10_ONLY |
| US | [NMIH](https://www.tradingview.com/chart/?symbol=NMIH) | 2026-08-20 | 45.39 | 1.78% | -20.22% | — | 2026-09-25 | DOWN10_ONLY |
| US | [NVST](https://www.tradingview.com/chart/?symbol=NVST) | 2026-08-26 | 27.8 | 1.69% | -20.14% | — | 2026-09-15 | DOWN10_ONLY |
| US | [FIVE](https://www.tradingview.com/chart/?symbol=FIVE) | 2026-09-04 | 252.2 | 1.68% | -20.03% | — | 2026-09-23 | DOWN10_ONLY |
| US | [JAZZ](https://www.tradingview.com/chart/?symbol=JAZZ) | 2026-08-25 | 260.2 | -0.15% | -20.01% | — | 2026-09-23 | DOWN10_ONLY |
| US | [ALSN](https://www.tradingview.com/chart/?symbol=ALSN) | 2026-08-24 | 131.4 | 2.50% | -20.00% | — | 2026-09-16 | DOWN10_ONLY |
| Canada | [FRX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFRX) | 2026-08-26 | 17 | 2.47% | -19.88% | — | 2026-09-15 | DOWN10_ONLY |
| US | [EE](https://www.tradingview.com/chart/?symbol=EE) | 2026-08-24 | 39.43 | 3.42% | -19.81% | — | 2026-09-21 | DOWN10_ONLY |
| US | [VNO](https://www.tradingview.com/chart/?symbol=VNO) | 2026-08-25 | 39.94 | 0.10% | -19.78% | — | 2026-09-08 | DOWN10_ONLY |
| US | [SLM](https://www.tradingview.com/chart/?symbol=SLM) | 2026-09-07 | 27.08 | -0.81% | -19.76% | — | 2026-09-22 | DOWN10_ONLY |
| US | [ZM](https://www.tradingview.com/chart/?symbol=ZM) | 2026-08-20 | 106.3 | 2.19% | -19.68% | — | 2026-08-26 | DOWN10_ONLY |
| US | [KMX](https://www.tradingview.com/chart/?symbol=KMX) | 2026-08-20 | 61.05 | 6.93% | -19.66% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [ARIS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AARIS) | 2026-09-03 | 28.36 | 1.02% | -19.53% | — | 2026-09-14 | DOWN10_ONLY |
| US | [PRGS](https://www.tradingview.com/chart/?symbol=PRGS) | 2026-09-03 | 44.61 | -0.96% | -19.52% | — | 2026-09-11 | DOWN10_ONLY |
| US | [AMBP](https://www.tradingview.com/chart/?symbol=AMBP) | 2026-08-20 | 5.25 | 0.94% | -19.43% | — | 2026-09-15 | DOWN10_ONLY |
| US | [VIST](https://www.tradingview.com/chart/?symbol=VIST) | 2026-09-15 | 78.36 | -1.24% | -19.36% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [6990](https://www.tradingview.com/chart/?symbol=HKEX%3A6990) | 2026-08-21 | 533 | 1.88% | -19.29% | — | 2026-09-01 | DOWN10_ONLY |
| US | [FLR](https://www.tradingview.com/chart/?symbol=FLR) | 2026-09-01 | 56.25 | 3.73% | -19.29% | — | 2026-09-24 | DOWN10_ONLY |
| US | [APO](https://www.tradingview.com/chart/?symbol=APO) | 2026-08-31 | 136.6 | -0.71% | -19.26% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SON](https://www.tradingview.com/chart/?symbol=SON) | 2026-08-20 | 58.33 | 2.43% | -19.24% | — | 2026-09-03 | DOWN10_ONLY |
| US | [CDLR](https://www.tradingview.com/chart/?symbol=CDLR) | 2026-09-09 | 25.79 | 1.09% | -19.23% | — | 2026-09-24 | DOWN10_ONLY |
| US | [PTEN](https://www.tradingview.com/chart/?symbol=PTEN) | 2026-09-09 | 12.93 | 3.56% | -19.10% | — | 2026-09-21 | DOWN10_ONLY |
| US | [FSM](https://www.tradingview.com/chart/?symbol=FSM) | 2026-09-04 | 12.31 | 2.19% | -19.09% | — | 2026-09-28 | DOWN10_ONLY |
| US | [LTH](https://www.tradingview.com/chart/?symbol=LTH) | 2026-08-23 | 45.11 | 2.50% | -19.04% | — | 2026-09-16 | DOWN10_ONLY |
| Canada | [RIO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIO) | 2026-09-03 | 3.52 | 11.65% | -19.03% | 2026-09-22 | 2026-09-30 | UP10_FIRST |
| US | [ASND](https://www.tradingview.com/chart/?symbol=ASND) | 2026-09-03 | 271.1 | 0.50% | -19.03% | — | 2026-09-15 | DOWN10_ONLY |
| US | [SBUX](https://www.tradingview.com/chart/?symbol=SBUX) | 2026-08-28 | 107.8 | 0.05% | -19.01% | — | 2026-09-15 | DOWN10_ONLY |
| US | [VTOL](https://www.tradingview.com/chart/?symbol=VTOL) | 2026-08-20 | 45.94 | 3.05% | -18.96% | — | 2026-09-16 | DOWN10_ONLY |
| US | [KYMR](https://www.tradingview.com/chart/?symbol=KYMR) | 2026-08-26 | 125.5 | -0.39% | -18.96% | — | 2026-09-04 | DOWN10_ONLY |
| HK | [6699](https://www.tradingview.com/chart/?symbol=HKEX%3A6699) | 2026-09-02 | 96.1 | -0.16% | -18.83% | — | 2026-09-11 | DOWN10_ONLY |
| US | [TWFG](https://www.tradingview.com/chart/?symbol=TWFG) | 2026-08-20 | 28.44 | 10.06% | -18.78% | 2026-08-25 | 2026-09-22 | UP10_FIRST |
| US | [SF](https://www.tradingview.com/chart/?symbol=SF) | 2026-09-03 | 82.28 | -0.22% | -18.70% | — | 2026-09-22 | DOWN10_ONLY |
| Canada | [IMG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIMG) | 2026-09-22 | 29.44 | -2.48% | -18.55% | — | 2026-09-28 | DOWN10_ONLY |
| US | [OSK](https://www.tradingview.com/chart/?symbol=OSK) | 2026-08-20 | 152.7 | 4.28% | -18.54% | — | 2026-09-23 | DOWN10_ONLY |
| US | [WPM](https://www.tradingview.com/chart/?symbol=WPM) | 2026-09-03 | 156.6 | 2.78% | -18.50% | — | 2026-09-28 | DOWN10_ONLY |
| US | [INTA](https://www.tradingview.com/chart/?symbol=INTA) | 2026-09-01 | 42.22 | 5.89% | -18.50% | — | 2026-09-10 | DOWN10_ONLY |
| US | [SW](https://www.tradingview.com/chart/?symbol=SW) | 2026-08-23 | 49.39 | 2.29% | -18.48% | — | 2026-09-03 | DOWN10_ONLY |
| Canada | [IFP.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIFP) | 2026-08-20 | 14.81 | 6.28% | -18.43% | — | 2026-09-02 | DOWN10_ONLY |
| HK | [0038](https://www.tradingview.com/chart/?symbol=HKEX%3A38) | 2026-08-28 | 9.2 | 8.56% | -18.42% | — | 2026-10-12 | DOWN10_ONLY |
| US | [VZ](https://www.tradingview.com/chart/?symbol=VZ) | 2026-08-31 | 50.02 | 1.72% | -18.41% | — | 2026-10-05 | DOWN10_ONLY |
| US | [MDGL](https://www.tradingview.com/chart/?symbol=MDGL) | 2026-09-02 | 546.9 | 0.94% | -18.34% | — | 2026-10-02 | DOWN10_ONLY |
| HK | [6190](https://www.tradingview.com/chart/?symbol=HKEX%3A6190) | 2026-08-24 | 3 | 0.00% | -18.33% | — | 2026-09-07 | DOWN10_ONLY |
| US | [LPLA](https://www.tradingview.com/chart/?symbol=LPLA) | 2026-08-23 | 361.4 | 3.20% | -18.20% | — | 2026-09-22 | DOWN10_ONLY |
| US | [XPRO](https://www.tradingview.com/chart/?symbol=XPRO) | 2026-08-20 | 18.41 | 2.61% | -18.20% | — | 2026-09-16 | DOWN10_ONLY |
| Canada | [OBE.TO](https://www.tradingview.com/chart/?symbol=TSX%3AOBE) | 2026-09-14 | 17.37 | 2.99% | -18.19% | — | 2026-09-25 | DOWN10_ONLY |
| US | [PTGX](https://www.tradingview.com/chart/?symbol=PTGX) | 2026-08-23 | 154.3 | 2.44% | -18.10% | — | 2026-09-23 | DOWN10_ONLY |
| US | [AVNT](https://www.tradingview.com/chart/?symbol=AVNT) | 2026-08-23 | 44.66 | 1.37% | -18.05% | — | 2026-09-18 | DOWN10_ONLY |
| Canada | [MMP-UN.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMMP.UN) | 2026-09-03 | 4.75 | 0.39% | -17.89% | — | 2026-09-11 | DOWN10_ONLY |
| US | [FROG](https://www.tradingview.com/chart/?symbol=FROG) | 2026-10-09 | 102.2 | 1.13% | -17.81% | — | 2026-10-14 | DOWN10_ONLY |
| Canada | [SSRM.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASSRM) | 2026-09-02 | 52.22 | 4.27% | -17.62% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RITM](https://www.tradingview.com/chart/?symbol=RITM) | 2026-08-28 | 10.08 | -2.22% | -17.56% | — | 2026-09-18 | DOWN10_ONLY |
| US | [HQY](https://www.tradingview.com/chart/?symbol=HQY) | 2026-08-20 | 104.3 | 1.88% | -17.51% | — | 2026-08-27 | DOWN10_ONLY |
| US | [CNR](https://www.tradingview.com/chart/?symbol=CNR) | 2026-08-28 | 101 | 3.87% | -17.46% | — | 2026-09-18 | DOWN10_ONLY |
| Canada | [GGD.TO](https://www.tradingview.com/chart/?symbol=TSX%3AGGD) | 2026-09-04 | 4.37 | 5.72% | -17.39% | — | 2026-10-06 | DOWN10_ONLY |
| US | [MMI](https://www.tradingview.com/chart/?symbol=MMI) | 2026-08-20 | 32.7 | 1.77% | -17.31% | — | 2026-09-28 | DOWN10_ONLY |
| US | [FNV](https://www.tradingview.com/chart/?symbol=FNV) | 2026-08-28 | 266.2 | 1.93% | -17.28% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [SCR.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASCR) | 2026-09-15 | 45.93 | -1.26% | -17.27% | — | 2026-09-21 | DOWN10_ONLY |
| US | [OPY](https://www.tradingview.com/chart/?symbol=OPY) | 2026-08-28 | 119 | 5.77% | -17.23% | — | 2026-10-13 | DOWN10_ONLY |
| US | [AKO-B](https://www.tradingview.com/chart/?symbol=AKO-B) | 2026-08-23 | 31.36 | 0.92% | -17.22% | — | 2026-10-14 | DOWN10_ONLY |
| Canada | [EDV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEDV) | 2026-09-03 | 89.03 | 1.93% | -17.12% | — | 2026-09-29 | DOWN10_ONLY |
| US | [KN](https://www.tradingview.com/chart/?symbol=KN) | 2026-10-05 | 39.4 | 1.47% | -17.06% | — | 2026-10-13 | DOWN10_ONLY |
| US | [KFY](https://www.tradingview.com/chart/?symbol=KFY) | 2026-08-20 | 84.59 | 2.71% | -17.02% | — | 2026-09-09 | DOWN10_ONLY |
| US | [HP](https://www.tradingview.com/chart/?symbol=HP) | 2026-08-31 | 43.58 | 10.53% | -17.00% | 2026-09-02 | 2026-09-24 | UP10_FIRST |
| US | [RVMD](https://www.tradingview.com/chart/?symbol=RVMD) | 2026-08-20 | 211.7 | 5.94% | -16.92% | — | 2026-09-18 | DOWN10_ONLY |
| US | [WTW](https://www.tradingview.com/chart/?symbol=WTW) | 2026-08-20 | 341.1 | 2.69% | -16.92% | — | 2026-09-18 | DOWN10_ONLY |
| US | [MTN](https://www.tradingview.com/chart/?symbol=MTN) | 2026-08-23 | 152.8 | 1.35% | -16.87% | — | 2026-08-31 | DOWN10_ONLY |
| HK | [0316](https://www.tradingview.com/chart/?symbol=HKEX%3A316) | 2026-08-26 | 170.3 | -0.47% | -16.85% | — | 2026-08-28 | DOWN10_ONLY |
| US | [USFD](https://www.tradingview.com/chart/?symbol=USFD) | 2026-08-20 | 108.5 | 2.60% | -16.84% | — | 2026-09-09 | DOWN10_ONLY |
| US | [SCHW](https://www.tradingview.com/chart/?symbol=SCHW) | 2026-08-20 | 109.8 | 4.32% | -16.77% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [FVI.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFVI) | 2026-09-04 | 17.05 | 1.64% | -16.72% | — | 2026-10-07 | DOWN10_ONLY |
| HK | [3908](https://www.tradingview.com/chart/?symbol=HKEX%3A3908) | 2026-08-28 | 22.64 | 1.59% | -16.70% | — | 2026-09-08 | DOWN10_ONLY |
| US | [CAKE](https://www.tradingview.com/chart/?symbol=CAKE) | 2026-08-25 | 113.5 | 4.53% | -16.69% | — | 2026-09-10 | DOWN10_ONLY |
| US | [LFUS](https://www.tradingview.com/chart/?symbol=LFUS) | 2026-10-06 | 454.3 | -1.92% | -16.68% | — | 2026-10-13 | DOWN10_ONLY |
| US | [BNY](https://www.tradingview.com/chart/?symbol=BNY) | 2026-08-24 | 162.1 | 2.28% | -16.66% | — | 2026-09-30 | DOWN10_ONLY |
| US | [ALL](https://www.tradingview.com/chart/?symbol=ALL) | 2026-09-03 | 263.1 | 0.08% | -16.57% | — | 2026-09-22 | DOWN10_ONLY |
| US | [DRTS](https://www.tradingview.com/chart/?symbol=DRTS) | 2026-08-20 | 14.36 | 9.96% | -16.50% | — | 2026-10-16 | DOWN10_ONLY |
| US | [MT](https://www.tradingview.com/chart/?symbol=MT) | 2026-08-23 | 72.2 | 10.36% | -16.43% | 2026-09-08 | 2026-10-01 | UP10_FIRST |
| US | [MTG](https://www.tradingview.com/chart/?symbol=MTG) | 2026-08-20 | 30.71 | 2.96% | -16.38% | — | 2026-09-30 | DOWN10_ONLY |
| US | [STT](https://www.tradingview.com/chart/?symbol=STT) | 2026-08-23 | 187.1 | 4.15% | -16.37% | — | 2026-10-14 | DOWN10_ONLY |
| US | [IDYA](https://www.tradingview.com/chart/?symbol=IDYA) | 2026-08-20 | 39.11 | 9.13% | -16.34% | — | 2026-10-08 | DOWN10_ONLY |
| US | [AR](https://www.tradingview.com/chart/?symbol=AR) | 2026-09-02 | 39.59 | 1.57% | -16.34% | — | 2026-09-16 | DOWN10_ONLY |
| US | [RLI](https://www.tradingview.com/chart/?symbol=RLI) | 2026-08-20 | 65.1 | 2.63% | -16.28% | — | 2026-09-22 | DOWN10_ONLY |
| US | [SKE](https://www.tradingview.com/chart/?symbol=SKE) | 2026-08-26 | 34.72 | 1.96% | -16.22% | — | 2026-09-01 | DOWN10_ONLY |
| US | [ESNT](https://www.tradingview.com/chart/?symbol=ESNT) | 2026-08-20 | 68.53 | 2.25% | -15.93% | — | 2026-09-30 | DOWN10_ONLY |
| US | [PANW](https://www.tradingview.com/chart/?symbol=PANW) | 2026-08-31 | 382.1 | 13.14% | -15.90% | 2026-10-06 | 2026-09-02 | DOWN10_FIRST |
| US | [VIR](https://www.tradingview.com/chart/?symbol=VIR) | 2026-10-05 | 11.78 | 1.87% | -15.87% | — | 2026-10-13 | DOWN10_ONLY |
| Canada | [WPM.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWPM) | 2026-09-03 | 216.3 | 2.39% | -15.85% | — | 2026-09-28 | DOWN10_ONLY |
| US | [NEM](https://www.tradingview.com/chart/?symbol=NEM) | 2026-09-03 | 130.4 | 0.04% | -15.79% | — | 2026-09-28 | DOWN10_ONLY |
| US | [WEX](https://www.tradingview.com/chart/?symbol=WEX) | 2026-08-20 | 197.8 | 3.10% | -15.79% | — | 2026-09-25 | DOWN10_ONLY |
| US | [LNC](https://www.tradingview.com/chart/?symbol=LNC) | 2026-09-03 | 45.66 | -0.58% | -15.78% | — | 2026-09-18 | DOWN10_ONLY |
| US | [CDW](https://www.tradingview.com/chart/?symbol=CDW) | 2026-09-14 | 151.7 | 2.84% | -15.77% | — | 2026-09-25 | DOWN10_ONLY |
| Canada | [FNV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFNV) | 2026-08-28 | 370 | 2.28% | -15.76% | — | 2026-09-30 | DOWN10_ONLY |
| US | [AXTA](https://www.tradingview.com/chart/?symbol=AXTA) | 2026-08-28 | 37.02 | 0.78% | -15.72% | — | 2026-09-14 | DOWN10_ONLY |
| HK | [1501](https://www.tradingview.com/chart/?symbol=HKEX%3A1501) | 2026-09-03 | 34.98 | 1.77% | -15.67% | — | 2026-10-12 | DOWN10_ONLY |
| US | [NVS](https://www.tradingview.com/chart/?symbol=NVS) | 2026-09-02 | 162.5 | 1.24% | -15.67% | — | 2026-09-08 | DOWN10_ONLY |
| US | [CART](https://www.tradingview.com/chart/?symbol=CART) | 2026-08-23 | 49.83 | 5.72% | -15.65% | — | 2026-09-22 | DOWN10_ONLY |
| US | [TSM](https://www.tradingview.com/chart/?symbol=TSM) | 2026-10-06 | 482.3 | -1.35% | -15.59% | — | 2026-10-14 | DOWN10_ONLY |
| US | [GPN](https://www.tradingview.com/chart/?symbol=GPN) | 2026-08-20 | 92.28 | 3.61% | -15.56% | — | 2026-09-29 | DOWN10_ONLY |
| US | [BBT](https://www.tradingview.com/chart/?symbol=BBT) | 2026-08-20 | 31.58 | 1.20% | -15.55% | — | 2026-09-22 | DOWN10_ONLY |
| US | [FHI](https://www.tradingview.com/chart/?symbol=FHI) | 2026-08-23 | 63.7 | 3.34% | -15.51% | — | 2026-09-16 | DOWN10_ONLY |
| US | [XPEL](https://www.tradingview.com/chart/?symbol=XPEL) | 2026-08-20 | 50.36 | 2.52% | -15.48% | — | 2026-09-17 | DOWN10_ONLY |
| Canada | [RBY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARBY) | 2026-08-20 | 4.59 | 3.05% | -15.47% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [0656](https://www.tradingview.com/chart/?symbol=HKEX%3A656) | 2026-09-02 | 5.335 | 0.28% | -15.46% | — | 2026-09-25 | DOWN10_ONLY |
| Canada | [WDO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWDO) | 2026-08-26 | 34.74 | 7.14% | -15.46% | — | 2026-10-13 | DOWN10_ONLY |
| Canada | [RIC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIC) | 2026-08-26 | 32.99 | -0.34% | -15.44% | — | 2026-09-16 | DOWN10_ONLY |
| US | [OMC](https://www.tradingview.com/chart/?symbol=OMC) | 2026-08-20 | 87.07 | 1.82% | -15.44% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [SKE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASKE) | 2026-08-26 | 48.15 | 1.77% | -15.41% | — | 2026-09-01 | DOWN10_ONLY |
| US | [TDW](https://www.tradingview.com/chart/?symbol=TDW) | 2026-08-24 | 92.92 | 9.32% | -15.38% | — | 2026-09-28 | DOWN10_ONLY |
| US | [NOG](https://www.tradingview.com/chart/?symbol=NOG) | 2026-09-01 | 26.36 | 3.45% | -15.37% | — | 2026-09-21 | DOWN10_ONLY |
| US | [QSR](https://www.tradingview.com/chart/?symbol=QSR) | 2026-08-25 | 81.56 | -0.66% | -15.36% | — | 2026-09-17 | DOWN10_ONLY |
| Canada | [KNT.TO](https://www.tradingview.com/chart/?symbol=TSX%3AKNT) | 2026-08-28 | 30.35 | 1.12% | -15.32% | — | 2026-09-28 | DOWN10_ONLY |
| US | [TFX](https://www.tradingview.com/chart/?symbol=TFX) | 2026-08-28 | 139.7 | 3.21% | -15.29% | — | 2026-09-17 | DOWN10_ONLY |
| US | [INCY](https://www.tradingview.com/chart/?symbol=INCY) | 2026-08-20 | 127.2 | 2.81% | -15.28% | — | 2026-10-05 | DOWN10_ONLY |
| US | [PRK](https://www.tradingview.com/chart/?symbol=PRK) | 2026-08-24 | 203.5 | -0.01% | -15.28% | — | 2026-09-16 | DOWN10_ONLY |
| US | [PGEN](https://www.tradingview.com/chart/?symbol=PGEN) | 2026-09-16 | 7.435 | 20.78% | -15.13% | 2026-09-25 | 2026-10-16 | UP10_FIRST |
| US | [T](https://www.tradingview.com/chart/?symbol=T) | 2026-09-16 | 25.86 | -0.43% | -15.08% | — | 2026-10-09 | DOWN10_ONLY |
| US | [PLMR](https://www.tradingview.com/chart/?symbol=PLMR) | 2026-09-16 | 140.8 | 1.27% | -15.07% | — | 2026-09-24 | DOWN10_ONLY |
| HK | [2877](https://www.tradingview.com/chart/?symbol=HKEX%3A2877) | 2026-09-25 | 8.38 | -8.59% | -15.04% | — | 2026-09-28 | DOWN10_ONLY |
| US | [BRKR](https://www.tradingview.com/chart/?symbol=BRKR) | 2026-10-05 | 63.86 | 4.01% | -15.02% | — | 2026-10-07 | DOWN10_ONLY |
| US | [MTDR](https://www.tradingview.com/chart/?symbol=MTDR) | 2026-09-01 | 59.21 | 7.79% | -14.90% | — | 2026-09-22 | DOWN10_ONLY |
| US | [HOG](https://www.tradingview.com/chart/?symbol=HOG) | 2026-08-23 | 28.2 | 1.64% | -14.89% | — | 2026-09-21 | DOWN10_ONLY |
| Canada | [PME.TO](https://www.tradingview.com/chart/?symbol=TSX%3APME) | 2026-08-31 | 5.99 | 0.40% | -14.86% | — | 2026-10-02 | DOWN10_ONLY |
| US | [UNF](https://www.tradingview.com/chart/?symbol=UNF) | 2026-08-24 | 291.8 | 0.97% | -14.82% | — | 2026-09-17 | DOWN10_ONLY |
| US | [ALX](https://www.tradingview.com/chart/?symbol=ALX) | 2026-08-20 | 272.3 | 1.73% | -14.79% | — | 2026-09-16 | DOWN10_ONLY |
| US | [FWONK](https://www.tradingview.com/chart/?symbol=FWONK) | 2026-08-23 | 104.9 | 2.26% | -14.78% | — | 2026-09-15 | DOWN10_ONLY |
| US | [KSPI](https://www.tradingview.com/chart/?symbol=KSPI) | 2026-08-28 | 106.3 | 0.35% | -14.77% | — | 2026-09-21 | DOWN10_ONLY |
| US | [WHD](https://www.tradingview.com/chart/?symbol=WHD) | 2026-09-01 | 70.69 | 2.77% | -14.75% | — | 2026-09-28 | DOWN10_ONLY |
| US | [NSP](https://www.tradingview.com/chart/?symbol=NSP) | 2026-08-28 | 53.54 | 1.42% | -14.72% | — | 2026-09-09 | DOWN10_ONLY |
| US | [BRC](https://www.tradingview.com/chart/?symbol=BRC) | 2026-08-24 | 94.38 | 2.45% | -14.70% | — | 2026-09-10 | DOWN10_ONLY |
| US | [AMCR](https://www.tradingview.com/chart/?symbol=AMCR) | 2026-08-20 | 47.81 | 0.91% | -14.68% | — | 2026-09-10 | DOWN10_ONLY |
| US | [HLN](https://www.tradingview.com/chart/?symbol=HLN) | 2026-08-24 | 10.16 | 0.98% | -14.67% | — | 2026-09-09 | DOWN10_ONLY |
| US | [FWONA](https://www.tradingview.com/chart/?symbol=FWONA) | 2026-08-25 | 96.26 | 0.55% | -14.63% | — | 2026-09-08 | DOWN10_ONLY |
| US | [NTRS](https://www.tradingview.com/chart/?symbol=NTRS) | 2026-08-24 | 186.7 | 1.57% | -14.60% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [MDI.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMDI) | 2026-09-22 | 17.35 | 1.33% | -14.52% | — | 2026-10-14 | DOWN10_ONLY |
| US | [ENTG](https://www.tradingview.com/chart/?symbol=ENTG) | 2026-10-08 | 162.2 | 2.45% | -14.52% | — | 2026-10-15 | DOWN10_ONLY |
| Canada | [VLN.TO](https://www.tradingview.com/chart/?symbol=TSX%3AVLN) | 2026-08-20 | 18.41 | 2.99% | -14.50% | — | 2026-10-08 | DOWN10_ONLY |
| US | [OMF](https://www.tradingview.com/chart/?symbol=OMF) | 2026-08-23 | 63.19 | 3.42% | -14.48% | — | 2026-09-24 | DOWN10_ONLY |
| US | [BALL](https://www.tradingview.com/chart/?symbol=BALL) | 2026-08-24 | 64.42 | 0.46% | -14.45% | — | 2026-09-24 | DOWN10_ONLY |
| US | [AMD](https://www.tradingview.com/chart/?symbol=AMD) | 2026-10-02 | 615.7 | 6.95% | -14.44% | — | 2026-10-15 | DOWN10_ONLY |
| HK | [1579](https://www.tradingview.com/chart/?symbol=HKEX%3A1579) | 2026-08-25 | 15.37 | 7.05% | -14.44% | — | 2026-09-14 | DOWN10_ONLY |
| US | [CNMD](https://www.tradingview.com/chart/?symbol=CNMD) | 2026-08-20 | 51.38 | 2.20% | -14.42% | — | 2026-09-08 | DOWN10_ONLY |
| US | [NOV](https://www.tradingview.com/chart/?symbol=NOV) | 2026-08-31 | 21.29 | 2.57% | -14.33% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [ALC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALC) | 2026-08-23 | 24.84 | 20.77% | -14.32% | 2026-10-08 | 2026-08-26 | DOWN10_FIRST |
| US | [EPR-PG](https://www.tradingview.com/chart/?symbol=EPR-PG) | 2026-08-28 | 21.46 | -1.96% | -14.32% | — | 2026-09-11 | DOWN10_ONLY |
| US | [SWK](https://www.tradingview.com/chart/?symbol=SWK) | 2026-08-23 | 100 | 0.38% | -14.31% | — | 2026-09-10 | DOWN10_ONLY |
| Canada | [EIF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AEIF) | 2026-08-20 | 131.1 | -0.25% | -14.24% | — | 2026-08-31 | DOWN10_ONLY |
| US | [BMY](https://www.tradingview.com/chart/?symbol=BMY) | 2026-08-20 | 65.47 | 3.16% | -14.24% | — | 2026-10-05 | DOWN10_ONLY |
| US | [SN](https://www.tradingview.com/chart/?symbol=SN) | 2026-08-24 | 183 | 7.30% | -14.20% | — | 2026-09-10 | DOWN10_ONLY |
| US | [FLS](https://www.tradingview.com/chart/?symbol=FLS) | 2026-08-23 | 79.39 | 4.68% | -14.14% | — | 2026-09-14 | DOWN10_ONLY |
| US | [AYA](https://www.tradingview.com/chart/?symbol=AYA) | 2026-09-04 | 28.91 | 6.09% | -14.08% | — | 2026-09-14 | DOWN10_ONLY |
| US | [FANG](https://www.tradingview.com/chart/?symbol=FANG) | 2026-09-15 | 211.5 | -3.51% | -14.03% | — | 2026-09-21 | DOWN10_ONLY |
| US | [OVV](https://www.tradingview.com/chart/?symbol=OVV) | 2026-08-23 | 66.82 | 3.82% | -14.01% | — | 2026-09-21 | DOWN10_ONLY |
| US | [DB](https://www.tradingview.com/chart/?symbol=DB) | 2026-08-20 | 37.56 | 10.81% | -14.00% | 2026-09-03 | 2026-10-07 | UP10_FIRST |
| US | [HIG](https://www.tradingview.com/chart/?symbol=HIG) | 2026-09-03 | 140 | -0.25% | -13.99% | — | 2026-09-24 | DOWN10_ONLY |
| HK | [1801](https://www.tradingview.com/chart/?symbol=HKEX%3A1801) | 2026-08-21 | 101.2 | 11.36% | -13.98% | 2026-08-26 | 2026-10-09 | UP10_FIRST |
| US | [AMP](https://www.tradingview.com/chart/?symbol=AMP) | 2026-08-23 | 555.6 | 2.11% | -13.98% | — | 2026-09-22 | DOWN10_ONLY |
| US | [ANET](https://www.tradingview.com/chart/?symbol=ANET) | 2026-09-21 | 205.4 | 5.84% | -13.95% | — | 2026-10-15 | DOWN10_ONLY |
| US | [COF](https://www.tradingview.com/chart/?symbol=COF) | 2026-09-03 | 220.5 | 0.12% | -13.93% | — | 2026-09-23 | DOWN10_ONLY |
| US | [BHP](https://www.tradingview.com/chart/?symbol=BHP) | 2026-08-20 | 93.63 | 3.17% | -13.92% | — | 2026-09-14 | DOWN10_ONLY |
| HK | [1258](https://www.tradingview.com/chart/?symbol=HKEX%3A1258) | 2026-08-25 | 15.81 | 12.78% | -13.92% | 2026-08-26 | 2026-10-15 | UP10_FIRST |
| Canada | [KBL.TO](https://www.tradingview.com/chart/?symbol=TSX%3AKBL) | 2026-08-26 | 46.48 | 2.81% | -13.92% | — | 2026-09-09 | DOWN10_ONLY |
| US | [TILE](https://www.tradingview.com/chart/?symbol=TILE) | 2026-08-20 | 39.08 | 1.35% | -13.89% | — | 2026-09-09 | DOWN10_ONLY |
| HK | [0669](https://www.tradingview.com/chart/?symbol=HKEX%3A669) | 2026-08-24 | 143.2 | -1.52% | -13.83% | — | 2026-09-02 | DOWN10_ONLY |
| US | [LECO](https://www.tradingview.com/chart/?symbol=LECO) | 2026-08-23 | 281.8 | 3.53% | -13.81% | — | 2026-09-10 | DOWN10_ONLY |
| US | [HWC](https://www.tradingview.com/chart/?symbol=HWC) | 2026-09-15 | 75.93 | 0.03% | -13.78% | — | 2026-10-14 | DOWN10_ONLY |
| HK | [2343](https://www.tradingview.com/chart/?symbol=HKEX%3A2343) | 2026-09-01 | 4.175 | 6.59% | -13.77% | — | 2026-10-15 | DOWN10_ONLY |
| US | [DRI](https://www.tradingview.com/chart/?symbol=DRI) | 2026-08-23 | 221.6 | 1.73% | -13.76% | — | 2026-09-25 | DOWN10_ONLY |
| US | [ZBH](https://www.tradingview.com/chart/?symbol=ZBH) | 2026-08-28 | 100.9 | 1.66% | -13.68% | — | 2026-09-23 | DOWN10_ONLY |
| US | [IBKR](https://www.tradingview.com/chart/?symbol=IBKR) | 2026-08-23 | 93.87 | 5.10% | -13.67% | — | 2026-10-01 | DOWN10_ONLY |
| US | [AMGN](https://www.tradingview.com/chart/?symbol=AMGN) | 2026-08-20 | 433.7 | 3.07% | -13.67% | — | 2026-09-09 | DOWN10_ONLY |
| US | [XMTR](https://www.tradingview.com/chart/?symbol=XMTR) | 2026-09-28 | 103.1 | 9.50% | -13.61% | — | 2026-10-15 | DOWN10_ONLY |
| HK | [2269](https://www.tradingview.com/chart/?symbol=HKEX%3A2269) | 2026-09-21 | 53 | 9.43% | -13.55% | — | 2026-10-16 | DOWN10_ONLY |
| US | [FTI](https://www.tradingview.com/chart/?symbol=FTI) | 2026-08-23 | 77.45 | 4.20% | -13.49% | — | 2026-09-29 | DOWN10_ONLY |
| US | [DLTR](https://www.tradingview.com/chart/?symbol=DLTR) | 2026-08-20 | 128.4 | 6.71% | -13.49% | — | 2026-09-15 | DOWN10_ONLY |
| US | [VNOM](https://www.tradingview.com/chart/?symbol=VNOM) | 2026-09-15 | 45.96 | -1.03% | -13.47% | — | 2026-09-21 | DOWN10_ONLY |
| US | [CCK](https://www.tradingview.com/chart/?symbol=CCK) | 2026-08-23 | 119.5 | 1.71% | -13.46% | — | 2026-09-24 | DOWN10_ONLY |
| US | [BEKE](https://www.tradingview.com/chart/?symbol=BEKE) | 2026-08-28 | 18.32 | -0.05% | -13.43% | — | 2026-09-15 | DOWN10_ONLY |
| US | [MRSH](https://www.tradingview.com/chart/?symbol=MRSH) | 2026-08-23 | 192 | 1.32% | -13.41% | — | 2026-09-17 | DOWN10_ONLY |
| US | [GSBD](https://www.tradingview.com/chart/?symbol=GSBD) | 2026-08-20 | 9.92 | 1.06% | -13.41% | — | 2026-10-07 | DOWN10_ONLY |
| US | [BFH](https://www.tradingview.com/chart/?symbol=BFH) | 2026-09-03 | 108.8 | 2.43% | -13.40% | — | 2026-09-30 | DOWN10_ONLY |
| US | [MHK](https://www.tradingview.com/chart/?symbol=MHK) | 2026-08-20 | 133.5 | 3.60% | -13.35% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [2423](https://www.tradingview.com/chart/?symbol=HKEX%3A2423) | 2026-09-05 | 47.96 | 1.04% | -13.34% | — | 2026-09-11 | DOWN10_ONLY |
| US | [RRC](https://www.tradingview.com/chart/?symbol=RRC) | 2026-09-01 | 42.4 | 1.96% | -13.33% | — | 2026-09-21 | DOWN10_ONLY |
| US | [IVZ](https://www.tradingview.com/chart/?symbol=IVZ) | 2026-08-20 | 31.36 | 7.33% | -13.33% | — | 2026-10-14 | DOWN10_ONLY |
| US | [KRYS](https://www.tradingview.com/chart/?symbol=KRYS) | 2026-09-01 | 363.8 | 2.60% | -13.32% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [ERO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AERO) | 2026-10-02 | 54.05 | 3.00% | -13.25% | — | 2026-10-14 | DOWN10_ONLY |
| US | [CRSR](https://www.tradingview.com/chart/?symbol=CRSR) | 2026-10-14 | 14.32 | -6.08% | -13.24% | — | 2026-10-15 | DOWN10_ONLY |
| US | [BBY](https://www.tradingview.com/chart/?symbol=BBY) | 2026-08-24 | 87.48 | 10.35% | -13.23% | 2026-09-23 | 2026-08-27 | DOWN10_FIRST |
| US | [TTEK](https://www.tradingview.com/chart/?symbol=TTEK) | 2026-08-24 | 36.86 | 1.38% | -13.13% | — | 2026-09-30 | DOWN10_ONLY |
| US | [TGB](https://www.tradingview.com/chart/?symbol=TGB) | 2026-08-20 | 8.69 | 13.00% | -13.12% | 2026-08-25 | 2026-09-14 | UP10_FIRST |
| US | [NVGS](https://www.tradingview.com/chart/?symbol=NVGS) | 2026-09-16 | 24.49 | 4.04% | -13.11% | — | 2026-10-15 | DOWN10_ONLY |
| US | [DAR](https://www.tradingview.com/chart/?symbol=DAR) | 2026-08-20 | 67.84 | 1.19% | -13.09% | — | 2026-08-21 | DOWN10_ONLY |
| US | [BEN](https://www.tradingview.com/chart/?symbol=BEN) | 2026-08-24 | 34.62 | 1.19% | -13.08% | — | 2026-10-13 | DOWN10_ONLY |
| US | [CF](https://www.tradingview.com/chart/?symbol=CF) | 2026-08-25 | 127.3 | 11.32% | -13.08% | 2026-09-02 | 2026-09-25 | UP10_FIRST |
| US | [GM](https://www.tradingview.com/chart/?symbol=GM) | 2026-08-23 | 87.93 | 0.18% | -13.07% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [CDR.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACDR) | 2026-09-02 | 4.67 | 0.64% | -13.06% | — | 2026-09-23 | DOWN10_ONLY |
| US | [PBF](https://www.tradingview.com/chart/?symbol=PBF) | 2026-08-23 | 73.53 | 25.74% | -13.03% | 2026-09-11 | 2026-08-26 | DOWN10_FIRST |
| Canada | [FTT.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFTT) | 2026-10-06 | 112 | -0.46% | -12.94% | — | 2026-10-15 | DOWN10_ONLY |
| HK | [1112](https://www.tradingview.com/chart/?symbol=HKEX%3A1112) | 2026-08-21 | 15.63 | 42.55% | -12.92% | 2026-08-26 | 2026-08-24 | DOWN10_FIRST |
| Canada | [NTR.TO](https://www.tradingview.com/chart/?symbol=TSX%3ANTR) | 2026-09-04 | 110 | 2.65% | -12.91% | — | 2026-10-01 | DOWN10_ONLY |
| US | [STRA](https://www.tradingview.com/chart/?symbol=STRA) | 2026-08-25 | 86.03 | 0.11% | -12.90% | — | 2026-09-18 | DOWN10_ONLY |
| US | [OCSL](https://www.tradingview.com/chart/?symbol=OCSL) | 2026-08-20 | 13.11 | -0.96% | -12.89% | — | 2026-10-01 | DOWN10_ONLY |
| US | [WLYB](https://www.tradingview.com/chart/?symbol=WLYB) | 2026-08-20 | 53.19 | 1.72% | -12.87% | — | 2026-09-08 | DOWN10_ONLY |
| US | [SDRL](https://www.tradingview.com/chart/?symbol=SDRL) | 2026-09-03 | 50.07 | 0.36% | -12.84% | — | 2026-09-29 | DOWN10_ONLY |
| US | [APD](https://www.tradingview.com/chart/?symbol=APD) | 2026-08-26 | 306.7 | 1.70% | -12.84% | — | 2026-09-29 | DOWN10_ONLY |
| US | [AMH](https://www.tradingview.com/chart/?symbol=AMH) | 2026-08-20 | 34.37 | 0.51% | -12.83% | — | 2026-09-14 | DOWN10_ONLY |
| HK | [0005](https://www.tradingview.com/chart/?symbol=HKEX%3A5) | 2026-08-24 | 162.9 | 3.07% | -12.83% | — | 2026-10-08 | DOWN10_ONLY |
| US | [LYG](https://www.tradingview.com/chart/?symbol=LYG) | 2026-08-25 | 6.08 | 0.33% | -12.83% | — | 2026-10-01 | DOWN10_ONLY |
| US | [ACT](https://www.tradingview.com/chart/?symbol=ACT) | 2026-08-20 | 49.12 | 2.20% | -12.81% | — | 2026-09-30 | DOWN10_ONLY |
| US | [WSBC](https://www.tradingview.com/chart/?symbol=WSBC) | 2026-09-03 | 41.31 | 0.75% | -12.81% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [MDP.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMDP) | 2026-08-31 | 5.24 | 1.15% | -12.79% | — | 2026-09-09 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-24 | 176.7 | 2.32% | -12.76% | — | 2026-09-22 | DOWN10_ONLY |
| US | [ORI](https://www.tradingview.com/chart/?symbol=ORI) | 2026-08-26 | 42.45 | 0.59% | -12.70% | — | 2026-09-24 | DOWN10_ONLY |
| US | [VET](https://www.tradingview.com/chart/?symbol=VET) | 2026-08-31 | 12.83 | 6.39% | -12.70% | — | 2026-09-22 | DOWN10_ONLY |
| US | [RGEN](https://www.tradingview.com/chart/?symbol=RGEN) | 2026-08-26 | 180.3 | 10.30% | -12.68% | 2026-09-28 | 2026-09-10 | DOWN10_FIRST |
| US | [TNET](https://www.tradingview.com/chart/?symbol=TNET) | 2026-08-23 | 70.48 | 2.16% | -12.68% | — | 2026-09-28 | DOWN10_ONLY |
| US | [SYF](https://www.tradingview.com/chart/?symbol=SYF) | 2026-08-23 | 79.47 | 2.45% | -12.67% | — | 2026-09-23 | DOWN10_ONLY |
| US | [REGN](https://www.tradingview.com/chart/?symbol=REGN) | 2026-08-20 | 826.6 | 3.96% | -12.66% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [MER.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMER) | 2026-09-09 | 2.29 | 2.18% | -12.66% | — | 2026-10-02 | DOWN10_ONLY |
| US | [TLX](https://www.tradingview.com/chart/?symbol=TLX) | 2026-09-04 | 11.94 | 9.80% | -12.65% | — | 2026-10-01 | DOWN10_ONLY |
| US | [SENEA](https://www.tradingview.com/chart/?symbol=SENEA) | 2026-08-20 | 192.6 | 9.02% | -12.64% | — | 2026-10-06 | DOWN10_ONLY |
| Canada | [PSK.TO](https://www.tradingview.com/chart/?symbol=TSX%3APSK) | 2026-09-15 | 37.09 | -1.11% | -12.64% | — | 2026-09-25 | DOWN10_ONLY |
| Canada | [XTC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AXTC) | 2026-08-20 | 8.65 | -0.64% | -12.62% | — | 2026-09-01 | DOWN10_ONLY |
| US | [XYZ](https://www.tradingview.com/chart/?symbol=XYZ) | 2026-08-25 | 82.72 | 5.08% | -12.62% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [PRU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APRU) | 2026-09-08 | 6.485 | 5.78% | -12.57% | — | 2026-10-15 | DOWN10_ONLY |
| US | [BTE](https://www.tradingview.com/chart/?symbol=BTE) | 2026-09-14 | 5.03 | 5.77% | -12.52% | — | 2026-09-25 | DOWN10_ONLY |
| US | [UBS](https://www.tradingview.com/chart/?symbol=UBS) | 2026-08-20 | 53.2 | 5.23% | -12.52% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [MBX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMBX) | 2026-08-28 | 0.32 | -0.00% | -12.50% | — | 2026-09-08 | DOWN10_ONLY |
| HK | [2232](https://www.tradingview.com/chart/?symbol=HKEX%3A2232) | 2026-09-02 | 7.055 | 7.51% | -12.47% | — | 2026-09-11 | DOWN10_ONLY |
| US | [USB](https://www.tradingview.com/chart/?symbol=USB) | 2026-09-03 | 63.53 | -0.71% | -12.44% | — | 2026-10-01 | DOWN10_ONLY |
| US | [GNW](https://www.tradingview.com/chart/?symbol=GNW) | 2026-08-26 | 9.91 | 7.87% | -12.41% | — | 2026-10-01 | DOWN10_ONLY |
| US | [MGA](https://www.tradingview.com/chart/?symbol=MGA) | 2026-08-20 | 70.39 | 4.02% | -12.32% | — | 2026-09-01 | DOWN10_ONLY |
| Canada | [MHC-U.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMHC.U) | 2026-08-20 | 22.8 | 0.36% | -12.32% | — | 2026-09-10 | DOWN10_ONLY |
| US | [VCTR](https://www.tradingview.com/chart/?symbol=VCTR) | 2026-08-23 | 115.6 | 6.37% | -12.31% | — | 2026-09-15 | DOWN10_ONLY |
| US | [BTG](https://www.tradingview.com/chart/?symbol=BTG) | 2026-09-04 | 5.61 | 1.06% | -12.30% | — | 2026-10-07 | DOWN10_ONLY |
| US | [MBIN](https://www.tradingview.com/chart/?symbol=MBIN) | 2026-08-20 | 54.13 | 1.54% | -12.28% | — | 2026-09-30 | DOWN10_ONLY |
| US | [TRIN](https://www.tradingview.com/chart/?symbol=TRIN) | 2026-08-20 | 18.27 | 1.40% | -12.26% | — | 2026-10-16 | DOWN10_ONLY |
| HK | [2268](https://www.tradingview.com/chart/?symbol=HKEX%3A2268) | 2026-09-23 | 80.35 | 6.53% | -12.26% | — | 2026-10-16 | DOWN10_ONLY |
| US | [CNK](https://www.tradingview.com/chart/?symbol=CNK) | 2026-08-24 | 38.4 | 3.62% | -12.24% | — | 2026-09-08 | DOWN10_ONLY |
| Canada | [ALK.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALK) | 2026-09-04 | 1.88 | 7.98% | -12.23% | — | 2026-10-14 | DOWN10_ONLY |
| Canada | [CFP.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACFP) | 2026-09-14 | 15.62 | 6.21% | -12.23% | — | 2026-10-07 | DOWN10_ONLY |
| US | [CP](https://www.tradingview.com/chart/?symbol=CP) | 2026-08-20 | 94.83 | 1.96% | -12.21% | — | 2026-09-30 | DOWN10_ONLY |
| US | [MCO](https://www.tradingview.com/chart/?symbol=MCO) | 2026-08-20 | 498.8 | 4.39% | -12.18% | — | 2026-10-01 | DOWN10_ONLY |
| US | [S](https://www.tradingview.com/chart/?symbol=S) | 2026-09-25 | 23.98 | 10.51% | -12.09% | 2026-10-09 | 2026-10-16 | UP10_FIRST |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-08-23 | 104.2 | 3.15% | -12.09% | — | 2026-10-07 | DOWN10_ONLY |
| HK | [3396](https://www.tradingview.com/chart/?symbol=HKEX%3A3396) | 2026-09-17 | 19.78 | 32.56% | -12.08% | 2026-09-18 | 2026-10-15 | UP10_FIRST |
| US | [PEBO](https://www.tradingview.com/chart/?symbol=PEBO) | 2026-09-15 | 40.17 | 0.02% | -12.05% | — | 2026-09-30 | DOWN10_ONLY |
| US | [BLK](https://www.tradingview.com/chart/?symbol=BLK) | 2026-08-23 | 1157 | 2.12% | -12.03% | — | 2026-09-16 | DOWN10_ONLY |
| US | [AM](https://www.tradingview.com/chart/?symbol=AM) | 2026-08-28 | 22.29 | 4.06% | -12.02% | — | 2026-10-01 | DOWN10_ONLY |
| US | [CGAU](https://www.tradingview.com/chart/?symbol=CGAU) | 2026-08-28 | 23.44 | 1.54% | -11.99% | — | 2026-09-28 | DOWN10_ONLY |
| US | [DLO](https://www.tradingview.com/chart/?symbol=DLO) | 2026-08-26 | 15.36 | 5.14% | -11.98% | — | 2026-09-24 | DOWN10_ONLY |
| HK | [1093](https://www.tradingview.com/chart/?symbol=HKEX%3A1093) | 2026-08-28 | 9.68 | 4.96% | -11.98% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [DSV.TO](https://www.tradingview.com/chart/?symbol=TSX%3ADSV) | 2026-09-02 | 12.52 | 7.27% | -11.98% | — | 2026-09-15 | DOWN10_ONLY |
| US | [CAH](https://www.tradingview.com/chart/?symbol=CAH) | 2026-09-02 | 245.5 | 4.10% | -11.93% | — | 2026-09-22 | DOWN10_ONLY |
| US | [WPP](https://www.tradingview.com/chart/?symbol=WPP) | 2026-08-25 | 26.67 | 4.57% | -11.91% | — | 2026-09-02 | DOWN10_ONLY |
| US | [NSC](https://www.tradingview.com/chart/?symbol=NSC) | 2026-08-20 | 346.6 | 2.70% | -11.88% | — | 2026-09-21 | DOWN10_ONLY |
| US | [ASX](https://www.tradingview.com/chart/?symbol=ASX) | 2026-10-02 | 44.73 | 6.93% | -11.87% | — | 2026-10-16 | DOWN10_ONLY |
| US | [CQP](https://www.tradingview.com/chart/?symbol=CQP) | 2026-08-24 | 68.05 | 4.70% | -11.81% | — | 2026-09-29 | DOWN10_ONLY |
| US | [MSEX](https://www.tradingview.com/chart/?symbol=MSEX) | 2026-08-20 | 58.76 | 1.77% | -11.81% | — | 2026-09-24 | DOWN10_ONLY |
| US | [BWIN](https://www.tradingview.com/chart/?symbol=BWIN) | 2026-08-20 | 31.45 | 3.99% | -11.80% | — | 2026-09-09 | DOWN10_ONLY |
| US | [UNP](https://www.tradingview.com/chart/?symbol=UNP) | 2026-08-20 | 304 | 2.87% | -11.75% | — | 2026-09-21 | DOWN10_ONLY |
| US | [IMO](https://www.tradingview.com/chart/?symbol=IMO) | 2026-09-01 | 134.9 | 0.94% | -11.74% | — | 2026-09-29 | DOWN10_ONLY |
| US | [PCTY](https://www.tradingview.com/chart/?symbol=PCTY) | 2026-08-28 | 157.9 | 7.07% | -11.72% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [MHC-UN.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMHC.UN) | 2026-08-20 | 31.99 | -0.84% | -11.72% | — | 2026-09-11 | DOWN10_ONLY |
| US | [NAT](https://www.tradingview.com/chart/?symbol=NAT) | 2026-08-20 | 6.99 | 27.04% | -11.70% | 2026-09-14 | 2026-08-26 | DOWN10_FIRST |
| US | [CNC](https://www.tradingview.com/chart/?symbol=CNC) | 2026-09-02 | 67.34 | 5.75% | -11.70% | — | 2026-10-01 | DOWN10_ONLY |
| US | [AHR](https://www.tradingview.com/chart/?symbol=AHR) | 2026-08-20 | 55.77 | 2.54% | -11.69% | — | 2026-10-06 | DOWN10_ONLY |
| US | [ARMK](https://www.tradingview.com/chart/?symbol=ARMK) | 2026-08-23 | 59.77 | 0.64% | -11.69% | — | 2026-09-29 | DOWN10_ONLY |
| US | [FLNG](https://www.tradingview.com/chart/?symbol=FLNG) | 2026-09-02 | 31.78 | 3.76% | -11.67% | — | 2026-10-15 | DOWN10_ONLY |
| US | [CORT](https://www.tradingview.com/chart/?symbol=CORT) | 2026-10-05 | 122 | 0.64% | -11.67% | — | 2026-10-16 | DOWN10_ONLY |
| US | [OSCR](https://www.tradingview.com/chart/?symbol=OSCR) | 2026-08-23 | 32.04 | 9.27% | -11.67% | — | 2026-09-24 | DOWN10_ONLY |
| HK | [6160](https://www.tradingview.com/chart/?symbol=HKEX%3A6160) | 2026-08-26 | 228.2 | 2.10% | -11.66% | — | 2026-09-11 | DOWN10_ONLY |
| US | [AVAH](https://www.tradingview.com/chart/?symbol=AVAH) | 2026-09-04 | 13.58 | 8.32% | -11.63% | — | 2026-09-25 | DOWN10_ONLY |
| US | [FIVN](https://www.tradingview.com/chart/?symbol=FIVN) | 2026-08-28 | 34.05 | 17.47% | -11.60% | 2026-09-22 | 2026-09-09 | DOWN10_FIRST |
| US | [MEOH](https://www.tradingview.com/chart/?symbol=MEOH) | 2026-09-15 | 64.47 | 1.11% | -11.56% | — | 2026-09-22 | DOWN10_ONLY |
| US | [IOT](https://www.tradingview.com/chart/?symbol=IOT) | 2026-08-28 | 41.16 | 9.62% | -11.56% | — | 2026-09-02 | DOWN10_ONLY |
| US | [CDP](https://www.tradingview.com/chart/?symbol=CDP) | 2026-08-20 | 37.12 | 1.07% | -11.53% | — | 2026-08-31 | DOWN10_ONLY |
| US | [BBVA](https://www.tradingview.com/chart/?symbol=BBVA) | 2026-08-20 | 28.63 | 1.89% | -11.51% | — | 2026-10-07 | DOWN10_ONLY |
| Canada | [CWL.TO](https://www.tradingview.com/chart/?symbol=TSX%3ACWL) | 2026-09-09 | 1.13 | -0.00% | -11.50% | — | 2026-09-21 | DOWN10_ONLY |
| HK | [1919](https://www.tradingview.com/chart/?symbol=HKEX%3A1919) | 2026-08-26 | 17.55 | 2.34% | -11.49% | — | 2026-09-04 | DOWN10_ONLY |
| US | [FRO](https://www.tradingview.com/chart/?symbol=FRO) | 2026-08-20 | 43.56 | 37.17% | -11.47% | 2026-09-15 | 2026-08-26 | DOWN10_FIRST |
| US | [TEAM](https://www.tradingview.com/chart/?symbol=TEAM) | 2026-09-15 | 189.8 | 17.85% | -11.46% | 2026-10-12 | 2026-09-29 | DOWN10_FIRST |
| US | [PKG](https://www.tradingview.com/chart/?symbol=PKG) | 2026-08-23 | 252.8 | 0.46% | -11.44% | — | 2026-09-01 | DOWN10_ONLY |
| Canada | [TECK-B.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATECK.B) | 2026-09-08 | 99.25 | -0.72% | -11.43% | — | 2026-09-10 | DOWN10_ONLY |
| US | [CWT](https://www.tradingview.com/chart/?symbol=CWT) | 2026-08-24 | 50.85 | 0.28% | -11.41% | — | 2026-09-25 | DOWN10_ONLY |
| US | [NEU](https://www.tradingview.com/chart/?symbol=NEU) | 2026-08-23 | 937.3 | 0.22% | -11.39% | — | 2026-09-09 | DOWN10_ONLY |
| US | [AVT](https://www.tradingview.com/chart/?symbol=AVT) | 2026-09-25 | 100.9 | 7.65% | -11.36% | — | 2026-10-15 | DOWN10_ONLY |
| Canada | [AYA.TO](https://www.tradingview.com/chart/?symbol=TSX%3AAYA) | 2026-09-04 | 39.97 | 7.88% | -11.36% | — | 2026-09-14 | DOWN10_ONLY |
| US | [TR](https://www.tradingview.com/chart/?symbol=TR) | 2026-08-25 | 41.39 | 0.31% | -11.35% | — | 2026-09-18 | DOWN10_ONLY |
| US | [OKE](https://www.tradingview.com/chart/?symbol=OKE) | 2026-08-26 | 94.9 | 5.22% | -11.33% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [IPO.TO](https://www.tradingview.com/chart/?symbol=TSX%3AIPO) | 2026-09-11 | 18.17 | 8.42% | -11.32% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [ALS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALS) | 2026-08-20 | 63.12 | 10.19% | -11.28% | 2026-09-22 | 2026-10-16 | UP10_FIRST |
| US | [AVAL](https://www.tradingview.com/chart/?symbol=AVAL) | 2026-09-03 | 5.33 | 2.08% | -11.26% | — | 2026-09-28 | DOWN10_ONLY |
| US | [KEYS](https://www.tradingview.com/chart/?symbol=KEYS) | 2026-10-01 | 364 | 7.11% | -11.25% | — | 2026-10-15 | DOWN10_ONLY |
| US | [AEG](https://www.tradingview.com/chart/?symbol=AEG) | 2026-09-02 | 9.25 | 0.22% | -11.24% | — | 2026-10-07 | DOWN10_ONLY |
| US | [HTO](https://www.tradingview.com/chart/?symbol=HTO) | 2026-08-20 | 64.25 | 1.46% | -11.22% | — | 2026-10-07 | DOWN10_ONLY |
| US | [PAG](https://www.tradingview.com/chart/?symbol=PAG) | 2026-08-20 | 216.6 | 2.07% | -11.22% | — | 2026-10-07 | DOWN10_ONLY |
| US | [GEO](https://www.tradingview.com/chart/?symbol=GEO) | 2026-08-20 | 31.72 | 4.57% | -11.19% | — | 2026-10-16 | DOWN10_ONLY |
| Canada | [LGD.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALGD) | 2026-09-08 | 1.97 | 16.75% | -11.17% | 2026-09-18 | 2026-10-14 | UP10_FIRST |
| US | [SM](https://www.tradingview.com/chart/?symbol=SM) | 2026-08-28 | 36.62 | 13.49% | -11.11% | 2026-09-15 | 2026-09-29 | UP10_FIRST |
| Canada | [OVV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AOVV) | 2026-08-23 | 92.09 | 6.50% | -11.11% | — | 2026-09-22 | DOWN10_ONLY |
| US | [FLYW](https://www.tradingview.com/chart/?symbol=FLYW) | 2026-08-20 | 18.75 | 5.23% | -11.09% | — | 2026-09-23 | DOWN10_ONLY |
| HK | [2359](https://www.tradingview.com/chart/?symbol=HKEX%3A2359) | 2026-09-21 | 208 | 5.38% | -11.06% | — | 2026-10-16 | DOWN10_ONLY |
| US | [MMM](https://www.tradingview.com/chart/?symbol=MMM) | 2026-08-23 | 179 | 1.03% | -11.04% | — | 2026-09-14 | DOWN10_ONLY |
| US | [WT](https://www.tradingview.com/chart/?symbol=WT) | 2026-08-20 | 22.65 | 14.39% | -11.04% | 2026-08-26 | 2026-10-15 | UP10_FIRST |
| US | [BPOP](https://www.tradingview.com/chart/?symbol=BPOP) | 2026-09-03 | 171.3 | 0.31% | -11.03% | — | 2026-10-01 | DOWN10_ONLY |
| Canada | [QSR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AQSR) | 2026-09-03 | 110.6 | 0.85% | -11.01% | — | 2026-09-25 | DOWN10_ONLY |
| US | [ATR](https://www.tradingview.com/chart/?symbol=ATR) | 2026-08-20 | 133 | 2.77% | -11.00% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RY](https://www.tradingview.com/chart/?symbol=RY) | 2026-09-03 | 212.1 | -0.04% | -10.98% | — | 2026-10-08 | DOWN10_ONLY |
| Canada | [LFE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALFE) | 2026-09-17 | 9.165 | 0.89% | -10.97% | — | 2026-10-01 | DOWN10_ONLY |
| US | [RAL](https://www.tradingview.com/chart/?symbol=RAL) | 2026-10-05 | 73.96 | 1.69% | -10.94% | — | 2026-10-15 | DOWN10_ONLY |
| US | [IRDM](https://www.tradingview.com/chart/?symbol=IRDM) | 2026-09-25 | 48.89 | 1.53% | -10.90% | — | 2026-10-15 | DOWN10_ONLY |
| US | [EOG](https://www.tradingview.com/chart/?symbol=EOG) | 2026-08-23 | 153.1 | 3.48% | -10.86% | — | 2026-09-22 | DOWN10_ONLY |
| US | [FOXA](https://www.tradingview.com/chart/?symbol=FOXA) | 2026-09-15 | 67.57 | 0.22% | -10.82% | — | 2026-10-01 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-08-24 | 34.88 | 9.43% | -10.81% | — | 2026-09-28 | DOWN10_ONLY |
| US | [INSW](https://www.tradingview.com/chart/?symbol=INSW) | 2026-08-20 | 99.36 | 27.09% | -10.78% | 2026-09-15 | 2026-08-26 | DOWN10_FIRST |
| HK | [2356](https://www.tradingview.com/chart/?symbol=HKEX%3A2356) | 2026-08-24 | 14.93 | 0.87% | -10.76% | — | 2026-08-28 | DOWN10_ONLY |
| Canada | [BTE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABTE) | 2026-09-14 | 6.98 | 7.88% | -10.74% | — | 2026-09-29 | DOWN10_ONLY |
| US | [TRGP](https://www.tradingview.com/chart/?symbol=TRGP) | 2026-08-23 | 299.1 | 0.13% | -10.73% | — | 2026-09-30 | DOWN10_ONLY |
| US | [PARR](https://www.tradingview.com/chart/?symbol=PARR) | 2026-09-09 | 83.13 | 9.15% | -10.71% | — | 2026-09-25 | DOWN10_ONLY |
| US | [LYV](https://www.tradingview.com/chart/?symbol=LYV) | 2026-08-24 | 184.6 | 2.37% | -10.71% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [TECK-A.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATECK.A) | 2026-09-08 | 98.91 | -0.15% | -10.69% | — | 2026-09-14 | DOWN10_ONLY |
| US | [CXW](https://www.tradingview.com/chart/?symbol=CXW) | 2026-08-20 | 33.51 | 9.07% | -10.68% | — | 2026-10-16 | DOWN10_ONLY |
| US | [LUXE](https://www.tradingview.com/chart/?symbol=LUXE) | 2026-10-09 | 10.21 | 0.20% | -10.68% | — | 2026-10-15 | DOWN10_ONLY |
| US | [BLCO](https://www.tradingview.com/chart/?symbol=BLCO) | 2026-08-24 | 17.32 | 6.61% | -10.68% | — | 2026-10-12 | DOWN10_ONLY |
| US | [OXY](https://www.tradingview.com/chart/?symbol=OXY) | 2026-09-09 | 61.3 | 4.03% | -10.67% | — | 2026-09-29 | DOWN10_ONLY |
| US | [FOX](https://www.tradingview.com/chart/?symbol=FOX) | 2026-09-15 | 60.34 | 0.12% | -10.67% | — | 2026-10-01 | DOWN10_ONLY |
| US | [UMH](https://www.tradingview.com/chart/?symbol=UMH) | 2026-08-20 | 16.6 | 1.02% | -10.66% | — | 2026-10-08 | DOWN10_ONLY |
| US | [GEF](https://www.tradingview.com/chart/?symbol=GEF) | 2026-08-20 | 86.43 | 1.35% | -10.63% | — | 2026-10-14 | DOWN10_ONLY |
| US | [LB](https://www.tradingview.com/chart/?symbol=LB) | 2026-08-31 | 87.58 | 2.42% | -10.62% | — | 2026-10-15 | DOWN10_ONLY |
| US | [PR](https://www.tradingview.com/chart/?symbol=PR) | 2026-08-25 | 23.3 | 5.67% | -10.56% | — | 2026-09-29 | DOWN10_ONLY |
| US | [CFR](https://www.tradingview.com/chart/?symbol=CFR) | 2026-09-03 | 162.7 | 2.47% | -10.55% | — | 2026-10-07 | DOWN10_ONLY |
| US | [LLY](https://www.tradingview.com/chart/?symbol=LLY) | 2026-08-20 | 1244 | 2.53% | -10.54% | — | 2026-09-08 | DOWN10_ONLY |
| US | [HAS](https://www.tradingview.com/chart/?symbol=HAS) | 2026-08-24 | 95.41 | 4.86% | -10.52% | — | 2026-09-23 | DOWN10_ONLY |
| HK | [2319](https://www.tradingview.com/chart/?symbol=HKEX%3A2319) | 2026-08-24 | 18.82 | 2.55% | -10.47% | — | 2026-10-05 | DOWN10_ONLY |
| Canada | [LCS.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALCS) | 2026-09-18 | 12.26 | 3.69% | -10.44% | — | 2026-10-08 | DOWN10_ONLY |
| US | [RHP](https://www.tradingview.com/chart/?symbol=RHP) | 2026-08-24 | 131.1 | 0.63% | -10.42% | — | 2026-09-16 | DOWN10_ONLY |
| US | [ROIV](https://www.tradingview.com/chart/?symbol=ROIV) | 2026-08-20 | 36.84 | 15.36% | -10.42% | 2026-09-08 | 2026-10-14 | UP10_FIRST |
| US | [VRTX](https://www.tradingview.com/chart/?symbol=VRTX) | 2026-08-20 | 540.3 | 3.70% | -10.40% | — | 2026-10-13 | DOWN10_ONLY |
| US | [FBNC](https://www.tradingview.com/chart/?symbol=FBNC) | 2026-08-24 | 65.29 | -0.06% | -10.40% | — | 2026-10-07 | DOWN10_ONLY |
| US | [WCC](https://www.tradingview.com/chart/?symbol=WCC) | 2026-10-02 | 371.3 | 4.68% | -10.38% | — | 2026-10-15 | DOWN10_ONLY |
| US | [HGTY](https://www.tradingview.com/chart/?symbol=HGTY) | 2026-08-24 | 13.4 | 15.90% | -10.37% | 2026-10-13 | 2026-09-10 | DOWN10_FIRST |
| US | [HPE](https://www.tradingview.com/chart/?symbol=HPE) | 2026-09-23 | 61.03 | 20.53% | -10.35% | 2026-10-02 | 2026-10-16 | UP10_FIRST |
| Canada | [BTO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABTO) | 2026-09-03 | 7.83 | 1.15% | -10.34% | — | 2026-10-14 | DOWN10_ONLY |
| US | [BCPC](https://www.tradingview.com/chart/?symbol=BCPC) | 2026-08-20 | 179.6 | 1.87% | -10.34% | — | 2026-10-01 | DOWN10_ONLY |
| US | [CNI](https://www.tradingview.com/chart/?symbol=CNI) | 2026-08-20 | 128.2 | 0.93% | -10.32% | — | 2026-10-08 | DOWN10_ONLY |
| US | [NET](https://www.tradingview.com/chart/?symbol=NET) | 2026-09-16 | 324.6 | 14.08% | -10.32% | 2026-09-23 | 2026-10-16 | UP10_FIRST |
| US | [LLYVK](https://www.tradingview.com/chart/?symbol=LLYVK) | 2026-08-20 | 105.5 | 2.52% | -10.29% | — | 2026-10-01 | DOWN10_ONLY |
| US | [WDS](https://www.tradingview.com/chart/?symbol=WDS) | 2026-09-01 | 23.9 | 1.59% | -10.29% | — | 2026-10-02 | DOWN10_ONLY |
| US | [PDM](https://www.tradingview.com/chart/?symbol=PDM) | 2026-08-20 | 9.73 | 2.77% | -10.28% | — | 2026-09-14 | DOWN10_ONLY |
| US | [HSIC](https://www.tradingview.com/chart/?symbol=HSIC) | 2026-08-20 | 88.46 | 3.65% | -10.28% | — | 2026-10-08 | DOWN10_ONLY |
| US | [BSTZ](https://www.tradingview.com/chart/?symbol=BSTZ) | 2026-08-20 | 30.39 | 3.91% | -10.27% | — | 2026-10-15 | DOWN10_ONLY |
| US | [SBCF](https://www.tradingview.com/chart/?symbol=SBCF) | 2026-09-04 | 34.6 | 0.03% | -10.26% | — | 2026-10-14 | DOWN10_ONLY |
| Canada | [SDE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASDE) | 2026-09-01 | 13.41 | 6.34% | -10.22% | — | 2026-10-02 | DOWN10_ONLY |
| US | [WMB](https://www.tradingview.com/chart/?symbol=WMB) | 2026-08-31 | 75.05 | 1.67% | -10.22% | — | 2026-09-30 | DOWN10_ONLY |
| Canada | [POU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APOU) | 2026-09-11 | 31.96 | 7.95% | -10.21% | — | 2026-10-02 | DOWN10_ONLY |
| US | [BPYPP](https://www.tradingview.com/chart/?symbol=BPYPP) | 2026-08-28 | 16.37 | -0.55% | -10.20% | — | 2026-09-24 | DOWN10_ONLY |
| US | [PCVX](https://www.tradingview.com/chart/?symbol=PCVX) | 2026-08-20 | 61.34 | 47.95% | -10.20% | 2026-10-05 | 2026-09-23 | DOWN10_FIRST |
| Canada | [YGR.TO](https://www.tradingview.com/chart/?symbol=TSX%3AYGR) | 2026-08-24 | 1.57 | 15.92% | -10.19% | 2026-10-13 | 2026-09-30 | DOWN10_FIRST |
| Canada | [TOT.TO](https://www.tradingview.com/chart/?symbol=TSX%3ATOT) | 2026-09-23 | 36.3 | 2.92% | -10.17% | — | 2026-09-29 | DOWN10_ONLY |
| US | [CSX](https://www.tradingview.com/chart/?symbol=CSX) | 2026-08-20 | 50.97 | 2.04% | -10.16% | — | 2026-09-21 | DOWN10_ONLY |
| US | [BF-A](https://www.tradingview.com/chart/?symbol=BF-A) | 2026-08-20 | 28.96 | 2.97% | -10.15% | — | 2026-09-16 | DOWN10_ONLY |
| US | [SAN](https://www.tradingview.com/chart/?symbol=SAN) | 2026-08-23 | 14.59 | 3.15% | -10.14% | — | 2026-10-02 | DOWN10_ONLY |
| US | [PAYC](https://www.tradingview.com/chart/?symbol=PAYC) | 2026-09-02 | 236.2 | 8.61% | -10.10% | — | 2026-09-29 | DOWN10_ONLY |
| US | [RACE](https://www.tradingview.com/chart/?symbol=RACE) | 2026-08-24 | 424.4 | 0.30% | -10.08% | — | 2026-10-05 | DOWN10_ONLY |
| HK | [3600](https://www.tradingview.com/chart/?symbol=HKEX%3A3600) | 2026-08-21 | 8.195 | 2.38% | -10.07% | — | 2026-09-14 | DOWN10_ONLY |
| US | [BF-B](https://www.tradingview.com/chart/?symbol=BF-B) | 2026-08-20 | 28.41 | 3.03% | -10.07% | — | 2026-09-16 | DOWN10_ONLY |
| US | [LIVN](https://www.tradingview.com/chart/?symbol=LIVN) | 2026-09-02 | 82.4 | 1.36% | -10.06% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [MG.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMG) | 2026-08-20 | 97.02 | 3.97% | -10.06% | — | 2026-09-24 | DOWN10_ONLY |
| US | [WFC](https://www.tradingview.com/chart/?symbol=WFC) | 2026-08-28 | 86.69 | 6.11% | -10.02% | — | 2026-10-01 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **163**; -10%-only sample: **428**.
- +10%-only common candles: —.
- -10%-only common candles: —.
- Median RS: +10%-only **17.54** vs -10%-only **16.04**.
- Median % below 52w high: +10%-only **4.19** vs -10%-only **4.19**.
- Median distance to breakout: +10%-only **3.38** vs -10%-only **3.45**.
- Median % above EMA20: +10%-only **5.34** vs -10%-only **4.41**.
- Median compression score: +10%-only **5.00** vs -10%-only **6.00**.

## Pre-Breakout Compression

### 🟢 Reached +10% — 35

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| HK | [2299](https://www.tradingview.com/chart/?symbol=HKEX%3A2299) | 2026-10-02 | 5.85 | 101.03% | 84.27% | 2026-10-05 | — | UP10_ONLY |
| US | [TEN](https://www.tradingview.com/chart/?symbol=TEN) | 2026-09-03 | 43.28 | 31.08% | -0.49% | 2026-09-11 | — | UP10_ONLY |
| US | [IDT](https://www.tradingview.com/chart/?symbol=IDT) | 2026-08-20 | 67.19 | 23.81% | -2.16% | 2026-09-29 | — | UP10_ONLY |
| US | [BOX](https://www.tradingview.com/chart/?symbol=BOX) | 2026-08-26 | 33.39 | 20.04% | -8.83% | 2026-10-09 | — | UP10_ONLY |
| US | [PHVS](https://www.tradingview.com/chart/?symbol=PHVS) | 2026-08-23 | 36.27 | 19.24% | -23.68% | 2026-09-08 | 2026-09-24 | UP10_FIRST |
| US | [GMAB](https://www.tradingview.com/chart/?symbol=GMAB) | 2026-09-15 | 34.15 | 17.63% | -1.24% | 2026-10-05 | — | UP10_ONLY |
| Canada | [LOVE.TO](https://www.tradingview.com/chart/?symbol=TSX%3ALOVE) | 2026-09-21 | 2.03 | 16.75% | -2.46% | 2026-09-25 | — | UP10_ONLY |
| Canada | [WFC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWFC) | 2026-08-23 | 20.85 | 16.21% | -9.35% | 2026-10-06 | — | UP10_ONLY |
| Canada | [SU.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASU) | 2026-09-09 | 95.29 | 16.04% | -2.88% | 2026-10-13 | — | UP10_ONLY |
| Canada | [XLY.TO](https://www.tradingview.com/chart/?symbol=TSX%3AXLY) | 2026-09-10 | 3.24 | 15.74% | -2.78% | 2026-09-18 | — | UP10_ONLY |
| US | [SU](https://www.tradingview.com/chart/?symbol=SU) | 2026-09-09 | 69.02 | 15.40% | -4.58% | 2026-10-14 | — | UP10_ONLY |
| HK | [3328](https://www.tradingview.com/chart/?symbol=HKEX%3A3328) | 2026-08-24 | 7.56 | 15.08% | -1.98% | 2026-09-28 | — | UP10_ONLY |
| US | [SHEL](https://www.tradingview.com/chart/?symbol=SHEL) | 2026-08-23 | 93.33 | 14.30% | -3.51% | 2026-10-13 | — | UP10_ONLY |
| HK | [3988](https://www.tradingview.com/chart/?symbol=HKEX%3A3988) | 2026-08-24 | 5.505 | 14.26% | -0.91% | 2026-09-03 | — | UP10_ONLY |
| US | [HNGE](https://www.tradingview.com/chart/?symbol=HNGE) | 2026-09-16 | 93.73 | 14.16% | -4.25% | 2026-10-09 | — | UP10_ONLY |
| US | [DAC](https://www.tradingview.com/chart/?symbol=DAC) | 2026-08-28 | 150.7 | 13.98% | -1.75% | 2026-10-05 | — | UP10_ONLY |
| Canada | [SGY.TO](https://www.tradingview.com/chart/?symbol=TSX%3ASGY) | 2026-08-31 | 11.13 | 13.67% | -2.98% | 2026-09-10 | — | UP10_ONLY |
| US | [GIC](https://www.tradingview.com/chart/?symbol=GIC) | 2026-08-25 | 39.63 | 12.87% | -3.20% | 2026-10-02 | — | UP10_ONLY |
| US | [TBBB](https://www.tradingview.com/chart/?symbol=TBBB) | 2026-09-18 | 51.35 | 12.58% | -2.18% | 2026-10-13 | — | UP10_ONLY |
| Canada | [WCP.TO](https://www.tradingview.com/chart/?symbol=TSX%3AWCP) | 2026-08-31 | 17.96 | 12.36% | -3.12% | 2026-10-15 | — | UP10_ONLY |
| US | [MCK](https://www.tradingview.com/chart/?symbol=MCK) | 2026-09-01 | 906.8 | 11.93% | -6.56% | 2026-10-15 | — | UP10_ONLY |
| US | [CNXN](https://www.tradingview.com/chart/?symbol=CNXN) | 2026-09-18 | 86.68 | 11.80% | -1.44% | 2026-10-13 | — | UP10_ONLY |
| US | [HGTY](https://www.tradingview.com/chart/?symbol=HGTY) | 2026-09-16 | 13.9 | 11.73% | -5.18% | 2026-10-15 | — | UP10_ONLY |
| US | [HALO](https://www.tradingview.com/chart/?symbol=HALO) | 2026-09-17 | 109.7 | 11.64% | -2.76% | 2026-10-15 | — | UP10_ONLY |
| US | [CON](https://www.tradingview.com/chart/?symbol=CON) | 2026-09-15 | 35.62 | 11.17% | -4.40% | 2026-10-15 | — | UP10_ONLY |
| Canada | [GUD.TO](https://www.tradingview.com/chart/?symbol=TSX%3AGUD) | 2026-09-03 | 10.04 | 11.16% | -3.88% | 2026-10-16 | — | UP10_ONLY |
| Canada | [HFPC-U.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHFPC.U) | 2026-10-06 | 2.25 | 11.11% | -11.11% | 2026-10-13 | 2026-10-16 | UP10_FIRST |
| US | [SAIC](https://www.tradingview.com/chart/?symbol=SAIC) | 2026-08-23 | 128 | 11.10% | -5.50% | 2026-08-31 | — | UP10_ONLY |
| Canada | [ELF.TO](https://www.tradingview.com/chart/?symbol=TSX%3AELF) | 2026-10-08 | 17.92 | 10.94% | 0.45% | 2026-10-15 | — | UP10_ONLY |
| HK | [0144](https://www.tradingview.com/chart/?symbol=HKEX%3A144) | 2026-09-08 | 16.31 | 10.79% | -3.60% | 2026-10-14 | — | UP10_ONLY |
| US | [SFL](https://www.tradingview.com/chart/?symbol=SFL) | 2026-09-03 | 12.62 | 10.78% | -2.69% | 2026-09-17 | — | UP10_ONLY |
| HK | [0517](https://www.tradingview.com/chart/?symbol=HKEX%3A517) | 2026-09-18 | 6.455 | 10.77% | -0.54% | 2026-10-12 | — | UP10_ONLY |
| US | [BIIB](https://www.tradingview.com/chart/?symbol=BIIB) | 2026-08-24 | 218.1 | 10.49% | -4.21% | 2026-10-15 | — | UP10_ONLY |
| US | [NMR](https://www.tradingview.com/chart/?symbol=NMR) | 2026-08-25 | 9.91 | 10.39% | -9.18% | 2026-09-11 | — | UP10_ONLY |
| US | [ABBV](https://www.tradingview.com/chart/?symbol=ABBV) | 2026-08-24 | 264.5 | 10.16% | -7.28% | 2026-10-15 | — | UP10_ONLY |

### 🔴 Reached -10% — 117

| Market | Symbol | Signal | Signal px | Max +% | Max -% | +10 date | -10 date | Order |
|---|---|---:|---:|---:|---:|---:|---:|---|
| US | [PCG](https://www.tradingview.com/chart/?symbol=PCG) | 2026-08-25 | 18.36 | -0.19% | -36.16% | — | 2026-08-28 | DOWN10_ONLY |
| US | [MRP](https://www.tradingview.com/chart/?symbol=MRP) | 2026-08-28 | 30.61 | 1.72% | -31.17% | — | 2026-09-18 | DOWN10_ONLY |
| US | [BKNG](https://www.tradingview.com/chart/?symbol=BKNG) | 2026-08-25 | 213.8 | 0.60% | -27.94% | — | 2026-09-04 | DOWN10_ONLY |
| US | [APAM](https://www.tradingview.com/chart/?symbol=APAM) | 2026-08-23 | 42.26 | 4.76% | -26.98% | — | 2026-09-11 | DOWN10_ONLY |
| US | [HESM](https://www.tradingview.com/chart/?symbol=HESM) | 2026-08-31 | 40.21 | 2.76% | -25.76% | — | 2026-10-07 | DOWN10_ONLY |
| US | [TVTX](https://www.tradingview.com/chart/?symbol=TVTX) | 2026-09-03 | 66.54 | 3.29% | -25.67% | — | 2026-09-22 | DOWN10_ONLY |
| US | [IMCR](https://www.tradingview.com/chart/?symbol=IMCR) | 2026-09-01 | 36.86 | 2.96% | -25.39% | — | 2026-09-10 | DOWN10_ONLY |
| US | [PHVS](https://www.tradingview.com/chart/?symbol=PHVS) | 2026-08-23 | 36.27 | 19.24% | -23.68% | 2026-09-08 | 2026-09-24 | UP10_FIRST |
| US | [SLG](https://www.tradingview.com/chart/?symbol=SLG) | 2026-08-26 | 58.68 | -0.67% | -22.39% | — | 2026-09-08 | DOWN10_ONLY |
| US | [PAYX](https://www.tradingview.com/chart/?symbol=PAYX) | 2026-08-25 | 125 | 2.39% | -21.59% | — | 2026-09-23 | DOWN10_ONLY |
| US | [EE](https://www.tradingview.com/chart/?symbol=EE) | 2026-09-04 | 40.03 | 0.07% | -21.01% | — | 2026-09-15 | DOWN10_ONLY |
| US | [SON](https://www.tradingview.com/chart/?symbol=SON) | 2026-08-23 | 59.48 | 0.45% | -20.80% | — | 2026-09-03 | DOWN10_ONLY |
| US | [JAZZ](https://www.tradingview.com/chart/?symbol=JAZZ) | 2026-08-25 | 260.2 | -0.15% | -20.01% | — | 2026-09-23 | DOWN10_ONLY |
| US | [DRTS](https://www.tradingview.com/chart/?symbol=DRTS) | 2026-09-15 | 14.87 | 6.19% | -19.37% | — | 2026-10-14 | DOWN10_ONLY |
| US | [MT](https://www.tradingview.com/chart/?symbol=MT) | 2026-08-26 | 74.53 | 6.91% | -19.04% | — | 2026-09-30 | DOWN10_ONLY |
| US | [SBUX](https://www.tradingview.com/chart/?symbol=SBUX) | 2026-08-28 | 107.8 | 0.05% | -19.01% | — | 2026-09-15 | DOWN10_ONLY |
| US | [STT](https://www.tradingview.com/chart/?symbol=STT) | 2026-08-25 | 192.9 | 1.01% | -18.89% | — | 2026-09-30 | DOWN10_ONLY |
| US | [SCHW](https://www.tradingview.com/chart/?symbol=SCHW) | 2026-08-25 | 112.3 | -1.12% | -18.61% | — | 2026-09-22 | DOWN10_ONLY |
| US | [CART](https://www.tradingview.com/chart/?symbol=CART) | 2026-09-02 | 51.53 | 2.23% | -18.44% | — | 2026-09-09 | DOWN10_ONLY |
| US | [VZ](https://www.tradingview.com/chart/?symbol=VZ) | 2026-08-31 | 50.02 | 1.72% | -18.41% | — | 2026-10-05 | DOWN10_ONLY |
| US | [USFD](https://www.tradingview.com/chart/?symbol=USFD) | 2026-08-23 | 109.6 | 1.51% | -17.72% | — | 2026-09-09 | DOWN10_ONLY |
| Canada | [ALS.TO](https://www.tradingview.com/chart/?symbol=TSX%3AALS) | 2026-09-21 | 67.97 | 2.32% | -17.61% | — | 2026-10-13 | DOWN10_ONLY |
| US | [BNY](https://www.tradingview.com/chart/?symbol=BNY) | 2026-08-25 | 163.7 | 1.34% | -17.43% | — | 2026-09-29 | DOWN10_ONLY |
| US | [MTG](https://www.tradingview.com/chart/?symbol=MTG) | 2026-08-24 | 31.1 | 1.67% | -17.43% | — | 2026-09-29 | DOWN10_ONLY |
| US | [KFY](https://www.tradingview.com/chart/?symbol=KFY) | 2026-08-20 | 84.59 | 2.71% | -17.02% | — | 2026-09-09 | DOWN10_ONLY |
| US | [BMY](https://www.tradingview.com/chart/?symbol=BMY) | 2026-08-26 | 67.57 | -0.04% | -16.90% | — | 2026-09-23 | DOWN10_ONLY |
| US | [WEX](https://www.tradingview.com/chart/?symbol=WEX) | 2026-09-15 | 200.1 | 0.07% | -16.73% | — | 2026-09-22 | DOWN10_ONLY |
| US | [TFX](https://www.tradingview.com/chart/?symbol=TFX) | 2026-08-31 | 142.1 | 1.49% | -16.71% | — | 2026-09-15 | DOWN10_ONLY |
| Canada | [FNV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AFNV) | 2026-09-17 | 373.5 | 1.31% | -16.55% | — | 2026-09-30 | DOWN10_ONLY |
| US | [ESNT](https://www.tradingview.com/chart/?symbol=ESNT) | 2026-08-25 | 69 | 1.55% | -16.51% | — | 2026-09-30 | DOWN10_ONLY |
| US | [IVZ](https://www.tradingview.com/chart/?symbol=IVZ) | 2026-08-24 | 32.45 | 3.73% | -16.24% | — | 2026-10-12 | DOWN10_ONLY |
| US | [FTI](https://www.tradingview.com/chart/?symbol=FTI) | 2026-09-04 | 79.84 | 0.85% | -16.08% | — | 2026-09-18 | DOWN10_ONLY |
| US | [DB](https://www.tradingview.com/chart/?symbol=DB) | 2026-08-24 | 38.42 | 8.33% | -15.93% | — | 2026-10-02 | DOWN10_ONLY |
| US | [NVS](https://www.tradingview.com/chart/?symbol=NVS) | 2026-09-02 | 162.5 | 1.24% | -15.67% | — | 2026-09-08 | DOWN10_ONLY |
| US | [OMC](https://www.tradingview.com/chart/?symbol=OMC) | 2026-08-20 | 87.07 | 1.82% | -15.44% | — | 2026-09-09 | DOWN10_ONLY |
| US | [HOG](https://www.tradingview.com/chart/?symbol=HOG) | 2026-09-04 | 28.3 | -0.37% | -15.19% | — | 2026-09-21 | DOWN10_ONLY |
| US | [AMP](https://www.tradingview.com/chart/?symbol=AMP) | 2026-08-24 | 561.1 | 1.10% | -14.83% | — | 2026-09-22 | DOWN10_ONLY |
| HK | [0005](https://www.tradingview.com/chart/?symbol=HKEX%3A5) | 2026-09-05 | 166.7 | 0.72% | -14.82% | — | 2026-10-02 | DOWN10_ONLY |
| US | [FWONK](https://www.tradingview.com/chart/?symbol=FWONK) | 2026-08-23 | 104.9 | 2.26% | -14.78% | — | 2026-09-15 | DOWN10_ONLY |
| US | [AMCR](https://www.tradingview.com/chart/?symbol=AMCR) | 2026-08-20 | 47.81 | 0.91% | -14.68% | — | 2026-09-10 | DOWN10_ONLY |
| US | [HLN](https://www.tradingview.com/chart/?symbol=HLN) | 2026-08-24 | 10.16 | 0.98% | -14.67% | — | 2026-09-09 | DOWN10_ONLY |
| US | [MRSH](https://www.tradingview.com/chart/?symbol=MRSH) | 2026-08-24 | 194.7 | -0.13% | -14.59% | — | 2026-09-11 | DOWN10_ONLY |
| US | [AMGN](https://www.tradingview.com/chart/?symbol=AMGN) | 2026-09-01 | 438.1 | 1.76% | -14.53% | — | 2026-09-08 | DOWN10_ONLY |
| US | [EPR-PG](https://www.tradingview.com/chart/?symbol=EPR-PG) | 2026-08-28 | 21.46 | -1.96% | -14.32% | — | 2026-09-11 | DOWN10_ONLY |
| US | [CXW](https://www.tradingview.com/chart/?symbol=CXW) | 2026-09-11 | 34.93 | 4.64% | -14.31% | — | 2026-09-22 | DOWN10_ONLY |
| US | [GNW](https://www.tradingview.com/chart/?symbol=GNW) | 2026-09-02 | 10.13 | 5.53% | -14.31% | — | 2026-09-30 | DOWN10_ONLY |
| US | [OVV](https://www.tradingview.com/chart/?symbol=OVV) | 2026-09-15 | 66.97 | 3.58% | -14.20% | — | 2026-09-21 | DOWN10_ONLY |
| US | [UBS](https://www.tradingview.com/chart/?symbol=UBS) | 2026-08-25 | 54.23 | 3.24% | -14.18% | — | 2026-09-23 | DOWN10_ONLY |
| Canada | [RIC.TO](https://www.tradingview.com/chart/?symbol=TSX%3ARIC) | 2026-09-02 | 32.5 | 1.16% | -14.17% | — | 2026-09-16 | DOWN10_ONLY |
| US | [RJF](https://www.tradingview.com/chart/?symbol=RJF) | 2026-08-28 | 179.4 | 0.79% | -14.06% | — | 2026-09-22 | DOWN10_ONLY |
| US | [HSBC](https://www.tradingview.com/chart/?symbol=HSBC) | 2026-09-03 | 106.5 | 0.91% | -14.00% | — | 2026-10-01 | DOWN10_ONLY |
| US | [QSR](https://www.tradingview.com/chart/?symbol=QSR) | 2026-09-03 | 80.26 | 0.47% | -13.99% | — | 2026-09-17 | DOWN10_ONLY |
| US | [ACT](https://www.tradingview.com/chart/?symbol=ACT) | 2026-08-24 | 49.72 | 0.97% | -13.86% | — | 2026-09-30 | DOWN10_ONLY |
| US | [ZBH](https://www.tradingview.com/chart/?symbol=ZBH) | 2026-08-28 | 100.9 | 1.66% | -13.68% | — | 2026-09-23 | DOWN10_ONLY |
| US | [APD](https://www.tradingview.com/chart/?symbol=APD) | 2026-08-31 | 309.5 | 0.10% | -13.63% | — | 2026-09-21 | DOWN10_ONLY |
| US | [NSC](https://www.tradingview.com/chart/?symbol=NSC) | 2026-08-24 | 353 | 0.85% | -13.47% | — | 2026-09-16 | DOWN10_ONLY |
| US | [VNOM](https://www.tradingview.com/chart/?symbol=VNOM) | 2026-09-15 | 45.96 | -1.03% | -13.47% | — | 2026-09-21 | DOWN10_ONLY |
| US | [UNP](https://www.tradingview.com/chart/?symbol=UNP) | 2026-08-24 | 309.9 | 0.92% | -13.43% | — | 2026-09-18 | DOWN10_ONLY |
| US | [BLK](https://www.tradingview.com/chart/?symbol=BLK) | 2026-08-24 | 1173 | 0.72% | -13.23% | — | 2026-09-15 | DOWN10_ONLY |
| US | [BSAC](https://www.tradingview.com/chart/?symbol=BSAC) | 2026-08-25 | 36.15 | 0.69% | -13.03% | — | 2026-10-01 | DOWN10_ONLY |
| US | [FLNG](https://www.tradingview.com/chart/?symbol=FLNG) | 2026-09-16 | 32.22 | 2.34% | -12.88% | — | 2026-10-15 | DOWN10_ONLY |
| US | [DBX](https://www.tradingview.com/chart/?symbol=DBX) | 2026-09-03 | 35.7 | 6.92% | -12.86% | — | 2026-09-28 | DOWN10_ONLY |
| US | [AMH](https://www.tradingview.com/chart/?symbol=AMH) | 2026-08-20 | 34.37 | 0.51% | -12.83% | — | 2026-09-14 | DOWN10_ONLY |
| US | [GSBD](https://www.tradingview.com/chart/?symbol=GSBD) | 2026-08-23 | 9.84 | 1.88% | -12.70% | — | 2026-10-07 | DOWN10_ONLY |
| Canada | [MER.TO](https://www.tradingview.com/chart/?symbol=TSX%3AMER) | 2026-09-09 | 2.29 | 2.18% | -12.66% | — | 2026-10-02 | DOWN10_ONLY |
| Canada | [PSK.TO](https://www.tradingview.com/chart/?symbol=TSX%3APSK) | 2026-09-15 | 37.09 | -1.11% | -12.64% | — | 2026-09-25 | DOWN10_ONLY |
| Canada | [XTC.TO](https://www.tradingview.com/chart/?symbol=TSX%3AXTC) | 2026-08-20 | 8.65 | -0.64% | -12.62% | — | 2026-09-01 | DOWN10_ONLY |
| US | [WFC](https://www.tradingview.com/chart/?symbol=WFC) | 2026-09-02 | 89.27 | 3.05% | -12.62% | — | 2026-09-29 | DOWN10_ONLY |
| US | [CQP](https://www.tradingview.com/chart/?symbol=CQP) | 2026-08-26 | 68.54 | 3.95% | -12.45% | — | 2026-09-29 | DOWN10_ONLY |
| US | [LLYVK](https://www.tradingview.com/chart/?symbol=LLYVK) | 2026-08-25 | 108 | 0.13% | -12.38% | — | 2026-09-09 | DOWN10_ONLY |
| US | [OKE](https://www.tradingview.com/chart/?symbol=OKE) | 2026-08-31 | 96.01 | 4.00% | -12.35% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [POU.TO](https://www.tradingview.com/chart/?symbol=TSX%3APOU) | 2026-09-16 | 32.74 | 5.38% | -12.35% | — | 2026-09-25 | DOWN10_ONLY |
| US | [KARO](https://www.tradingview.com/chart/?symbol=KARO) | 2026-09-16 | 67.54 | 1.81% | -12.33% | — | 2026-09-24 | DOWN10_ONLY |
| US | [TRIN](https://www.tradingview.com/chart/?symbol=TRIN) | 2026-08-20 | 18.27 | 1.40% | -12.26% | — | 2026-10-16 | DOWN10_ONLY |
| US | [CHRD](https://www.tradingview.com/chart/?symbol=CHRD) | 2026-09-14 | 151.2 | 3.86% | -12.25% | — | 2026-09-22 | DOWN10_ONLY |
| US | [CP](https://www.tradingview.com/chart/?symbol=CP) | 2026-08-20 | 94.83 | 1.96% | -12.21% | — | 2026-09-30 | DOWN10_ONLY |
| US | [HSIC](https://www.tradingview.com/chart/?symbol=HSIC) | 2026-08-26 | 90.38 | 1.45% | -12.18% | — | 2026-10-08 | DOWN10_ONLY |
| US | [OCSL](https://www.tradingview.com/chart/?symbol=OCSL) | 2026-08-23 | 12.99 | -0.05% | -12.09% | — | 2026-10-07 | DOWN10_ONLY |
| US | [IMO](https://www.tradingview.com/chart/?symbol=IMO) | 2026-09-15 | 135.3 | -0.76% | -12.01% | — | 2026-09-29 | DOWN10_ONLY |
| US | [PR](https://www.tradingview.com/chart/?symbol=PR) | 2026-09-08 | 23.65 | 4.10% | -11.88% | — | 2026-09-22 | DOWN10_ONLY |
| US | [MSEX](https://www.tradingview.com/chart/?symbol=MSEX) | 2026-08-20 | 58.76 | 1.77% | -11.81% | — | 2026-09-24 | DOWN10_ONLY |
| US | [PBT](https://www.tradingview.com/chart/?symbol=PBT) | 2026-09-08 | 34.81 | 6.23% | -11.75% | — | 2026-10-01 | DOWN10_ONLY |
| US | [LYV](https://www.tradingview.com/chart/?symbol=LYV) | 2026-08-25 | 186.8 | 1.17% | -11.75% | — | 2026-09-11 | DOWN10_ONLY |
| US | [VRTX](https://www.tradingview.com/chart/?symbol=VRTX) | 2026-09-01 | 547.6 | 2.30% | -11.61% | — | 2026-10-13 | DOWN10_ONLY |
| US | [BBVA](https://www.tradingview.com/chart/?symbol=BBVA) | 2026-08-20 | 28.63 | 1.89% | -11.51% | — | 2026-10-07 | DOWN10_ONLY |
| US | [BLCO](https://www.tradingview.com/chart/?symbol=BLCO) | 2026-08-31 | 17.48 | 5.64% | -11.50% | — | 2026-10-12 | DOWN10_ONLY |
| US | [CNI](https://www.tradingview.com/chart/?symbol=CNI) | 2026-08-23 | 129.8 | -0.61% | -11.43% | — | 2026-09-21 | DOWN10_ONLY |
| US | [OXY](https://www.tradingview.com/chart/?symbol=OXY) | 2026-09-14 | 61.78 | 3.22% | -11.36% | — | 2026-09-29 | DOWN10_ONLY |
| US | [LLYVA](https://www.tradingview.com/chart/?symbol=LLYVA) | 2026-08-25 | 104 | 0.01% | -11.31% | — | 2026-09-09 | DOWN10_ONLY |
| US | [BCH](https://www.tradingview.com/chart/?symbol=BCH) | 2026-09-02 | 42.38 | 1.75% | -11.26% | — | 2026-10-02 | DOWN10_ONLY |
| Canada | [HFPC-U.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHFPC.U) | 2026-10-06 | 2.25 | 11.11% | -11.11% | 2026-10-13 | 2026-10-16 | UP10_FIRST |
| US | [TR](https://www.tradingview.com/chart/?symbol=TR) | 2026-08-28 | 41.27 | 0.07% | -11.09% | — | 2026-09-18 | DOWN10_ONLY |
| US | [LQDT](https://www.tradingview.com/chart/?symbol=LQDT) | 2026-08-24 | 43.23 | 4.09% | -10.96% | — | 2026-09-01 | DOWN10_ONLY |
| US | [GLP](https://www.tradingview.com/chart/?symbol=GLP) | 2026-08-31 | 51.35 | 5.73% | -10.94% | — | 2026-09-30 | DOWN10_ONLY |
| US | [SAN](https://www.tradingview.com/chart/?symbol=SAN) | 2026-08-24 | 14.72 | 2.24% | -10.94% | — | 2026-10-01 | DOWN10_ONLY |
| US | [WES](https://www.tradingview.com/chart/?symbol=WES) | 2026-09-03 | 49.19 | 1.42% | -10.71% | — | 2026-09-30 | DOWN10_ONLY |
| US | [WDS](https://www.tradingview.com/chart/?symbol=WDS) | 2026-09-15 | 23.98 | -0.83% | -10.59% | — | 2026-09-29 | DOWN10_ONLY |
| US | [KNTK](https://www.tradingview.com/chart/?symbol=KNTK) | 2026-09-01 | 55.03 | 3.43% | -10.59% | — | 2026-10-01 | DOWN10_ONLY |
| HK | [0293](https://www.tradingview.com/chart/?symbol=HKEX%3A293) | 2026-09-30 | 14.74 | -0.00% | -10.58% | — | 2026-10-15 | DOWN10_ONLY |
| US | [HAS](https://www.tradingview.com/chart/?symbol=HAS) | 2026-08-24 | 95.41 | 4.86% | -10.52% | — | 2026-09-23 | DOWN10_ONLY |
| US | [NWG](https://www.tradingview.com/chart/?symbol=NWG) | 2026-08-25 | 18.87 | 1.01% | -10.49% | — | 2026-10-08 | DOWN10_ONLY |
| US | [UMH](https://www.tradingview.com/chart/?symbol=UMH) | 2026-08-25 | 16.56 | 0.91% | -10.45% | — | 2026-10-08 | DOWN10_ONLY |
| US | [JPM](https://www.tradingview.com/chart/?symbol=JPM) | 2026-09-03 | 362.1 | -0.28% | -10.44% | — | 2026-10-01 | DOWN10_ONLY |
| US | [VOYA](https://www.tradingview.com/chart/?symbol=VOYA) | 2026-08-28 | 102.5 | 3.01% | -10.43% | — | 2026-10-01 | DOWN10_ONLY |
| US | [JXN](https://www.tradingview.com/chart/?symbol=JXN) | 2026-09-10 | 138.4 | 1.42% | -10.40% | — | 2026-09-17 | DOWN10_ONLY |
| US | [SHC](https://www.tradingview.com/chart/?symbol=SHC) | 2026-08-26 | 19.54 | 0.92% | -10.39% | — | 2026-10-08 | DOWN10_ONLY |
| US | [CIB](https://www.tradingview.com/chart/?symbol=CIB) | 2026-09-09 | 100 | 3.93% | -10.38% | — | 2026-10-01 | DOWN10_ONLY |
| US | [BCPC](https://www.tradingview.com/chart/?symbol=BCPC) | 2026-08-20 | 179.6 | 1.87% | -10.34% | — | 2026-10-01 | DOWN10_ONLY |
| US | [CHE](https://www.tradingview.com/chart/?symbol=CHE) | 2026-08-26 | 548.6 | -0.50% | -10.33% | — | 2026-09-24 | DOWN10_ONLY |
| US | [SMFG](https://www.tradingview.com/chart/?symbol=SMFG) | 2026-09-14 | 27.24 | -1.43% | -10.28% | — | 2026-10-15 | DOWN10_ONLY |
| US | [ZIM](https://www.tradingview.com/chart/?symbol=ZIM) | 2026-09-24 | 30.09 | 2.96% | -10.27% | — | 2026-09-29 | DOWN10_ONLY |
| Canada | [HWX.TO](https://www.tradingview.com/chart/?symbol=TSX%3AHWX) | 2026-09-02 | 14.44 | 1.59% | -10.25% | — | 2026-10-02 | DOWN10_ONLY |
| US | [JNJ](https://www.tradingview.com/chart/?symbol=JNJ) | 2026-08-24 | 273 | 2.94% | -10.21% | — | 2026-10-13 | DOWN10_ONLY |
| US | [BPYPP](https://www.tradingview.com/chart/?symbol=BPYPP) | 2026-08-28 | 16.37 | -0.55% | -10.20% | — | 2026-09-24 | DOWN10_ONLY |
| Canada | [BLCO.TO](https://www.tradingview.com/chart/?symbol=TSX%3ABLCO) | 2026-09-04 | 24.98 | -0.32% | -10.17% | — | 2026-10-13 | DOWN10_ONLY |
| US | [MFG](https://www.tradingview.com/chart/?symbol=MFG) | 2026-09-08 | 11.14 | 3.14% | -10.14% | — | 2026-10-15 | DOWN10_ONLY |
| Canada | [OVV.TO](https://www.tradingview.com/chart/?symbol=TSX%3AOVV) | 2026-08-31 | 91.09 | 7.67% | -10.13% | — | 2026-09-30 | DOWN10_ONLY |

### Pattern snapshot

- +10%-only sample: **33**; -10%-only sample: **115**.
- +10%-only common candles: —.
- -10%-only common candles: —.
- Median RS: +10%-only **19.23** vs -10%-only **12.98**.
- Median % below 52w high: +10%-only **1.70** vs -10%-only **1.84**.
- Median distance to breakout: +10%-only **1.47** vs -10%-only **1.62**.
- Median % above EMA20: +10%-only **3.64** vs -10%-only **3.18**.
- Median compression score: +10%-only **8.00** vs -10%-only **8.00**.

## Notes

- Results are observational, not a trading recommendation.
- Recent signals have less follow-up time; use the 10-session columns for a fairer stage-to-stage comparison.
- A symbol can be counted in both +10% and -10% if both thresholds were reached after its signal. The Order column shows which threshold happened first; same-day order cannot be resolved from daily OHLC.
- yfinance failures are retained separately so missing price history is visible rather than silently treated as a non-hit.

