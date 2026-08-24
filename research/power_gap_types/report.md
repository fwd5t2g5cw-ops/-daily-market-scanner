# Power-Gap Chart-Type Research

- Window: **2022-01-01 to 2025-12-31**
- Power gaps >=15%: **11**
- Same-stock controls: **33**

## Chart-type distribution

| Type | Power gaps | Power-gap rate | Controls | Control rate | Lift |
|---|---:|---:|---:|---:|---:|
| HIGH_TIGHT | 2 | 18% | 4 | 12% | 1.50x |
| HIGH_LOOSE | 2 | 18% | 5 | 15% | 1.20x |
| BASE_ACCUM | 1 | 9% | 6 | 18% | 0.50x |
| REVERSAL_DEPRESSED | 6 | 55% | 18 | 55% | 1.00x |

## Power-gap examples

| Symbol | Date | Gap | Type | Dist to 60d high | Range10/20 | EMA20 slope10 |
|---|---|---:|---|---:|---:|---:|
| PHVS | 2022-12-08 | 66.9% | REVERSAL_DEPRESSED | 73.2% | 0.57 | -22.9% |
| CRNX | 2023-09-11 | 57.1% | REVERSAL_DEPRESSED | 26.6% | 0.88 | -2.8% |
| APGE | 2024-03-05 | 43.5% | HIGH_LOOSE | 3.5% | 1.00 | 2.6% |
| PHVS | 2023-12-06 | 28.3% | REVERSAL_DEPRESSED | 4.6% | 1.00 | 2.8% |
| PAYO | 2022-05-13 | 22.2% | REVERSAL_DEPRESSED | 28.1% | 0.96 | -5.8% |
| ATAI | 2025-07-01 | 20.5% | BASE_ACCUM | 17.0% | 0.80 | 2.3% |
| ROKU | 2023-11-02 | 18.7% | REVERSAL_DEPRESSED | 37.7% | 0.48 | -9.9% |
| PAYO | 2022-08-12 | 17.9% | HIGH_TIGHT | 4.5% | 0.72 | 6.1% |
| ROKU | 2025-02-14 | 16.1% | HIGH_TIGHT | 5.3% | 0.72 | 2.7% |
| CRNX | 2024-02-28 | 15.3% | HIGH_LOOSE | 0.8% | 0.98 | 0.2% |
| PHVS | 2022-01-07 | 15.3% | REVERSAL_DEPRESSED | 11.9% | 0.76 | 2.5% |

## Interpretation

- HIGH_TIGHT = near the 60-session high, EMA20>EMA50, close>EMA20, and 10-day range compressed vs 20-day range.
- HIGH_LOOSE = near the high and in trend, but not tightly compressed.
- BASE_ACCUM = within 25% of high, limited drawdown, roughly flat/up over 60 sessions.
- REVERSAL_DEPRESSED = everything else; this includes low-position/reversal/news-repricing structures.
- A useful pre-gap scanner needs a type with meaningfully higher frequency in power gaps than same-stock controls, not merely a visually attractive pattern.
