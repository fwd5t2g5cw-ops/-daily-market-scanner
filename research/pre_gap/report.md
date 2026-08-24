# Pre-Gap 60-Day Chart Pattern Research

- Compression snapshots used: **2**
- Unique symbols studied: **54**
- Gap events (open >= prior close +4%): **26**
- Compression controls with no such gap in prior 90 sessions: **38**

## Strongest pre-gap binary differences

| Feature | Gap group | Control | Difference |
|---|---:|---:|---:|
| ema20_gt_ema50 | 81% | 100% | -19% |
| shallow_pullback_8 | 77% | 100% | -23% |
| close_gt_ema20 | 69% | 100% | -31% |
| range_contract_075 | 50% | 82% | -32% |
| trend_stack | 62% | 100% | -38% |
| range_vs_prior_075 | 50% | 89% | -39% |

## Best exploratory combinations

> Exploratory only: this is a selected Compression sample, not the whole market. A rule must later be tested out-of-sample.

| Rule | Gap hits | Control hits | Gap coverage | Sample precision |
|---|---:|---:|---:|---:|
| shallow_pullback_8 + ema20_gt_ema50 | 18 | 38 | 69% | 32% |
| shallow_pullback_8 + close_gt_ema20 | 17 | 38 | 65% | 31% |
| shallow_pullback_8 + trend_stack | 16 | 38 | 62% | 30% |
| trend_stack + ema20_gt_ema50 | 16 | 38 | 62% | 30% |
| trend_stack + close_gt_ema20 | 16 | 38 | 62% | 30% |
| ema20_gt_ema50 + close_gt_ema20 | 16 | 38 | 62% | 30% |
| shallow_pullback_8 + trend_stack + ema20_gt_ema50 | 16 | 38 | 62% | 30% |
| shallow_pullback_8 + trend_stack + close_gt_ema20 | 16 | 38 | 62% | 30% |
| shallow_pullback_8 + ema20_gt_ema50 + close_gt_ema20 | 16 | 38 | 62% | 30% |
| trend_stack + ema20_gt_ema50 + close_gt_ema20 | 16 | 38 | 62% | 30% |

## Detected gap examples

| Symbol | Gap date | Opening gap |
|---|---|---:|
| CRNX | 2026-07-07 | 98.9% |
| UTZ | 2026-07-21 | 89.0% |
| APGE | 2026-06-22 | 46.7% |
| SAFT | 2026-07-24 | 41.2% |
| ATAI | 2026-07-16 | 31.8% |
| DSGR | 2026-07-16 | 26.3% |
| TECH | 2026-06-25 | 19.3% |
| SAIC | 2026-06-01 | 15.3% |
| V | 2026-04-29 | 8.8% |
| DGX | 2026-07-23 | 8.7% |
| AMCR | 2026-05-06 | 7.9% |
| ACA | 2026-06-22 | 6.7% |
| EXPD | 2026-05-05 | 6.6% |
| BBVA | 2026-07-30 | 6.3% |
| IDT | 2026-06-04 | 5.5% |
| PHVS | 2026-05-08 | 5.4% |
| SEIC | 2026-04-23 | 5.1% |
| KO | 2026-07-28 | 5.0% |
| LNG | 2026-08-06 | 5.0% |
| USFD | 2026-08-06 | 4.8% |
| KFY | 2026-06-23 | 4.6% |
| SON | 2026-07-23 | 4.6% |
| MA | 2026-04-29 | 4.4% |
| ROKU | 2026-06-12 | 4.3% |
| IOSP | 2026-08-05 | 4.1% |
| PAYO | 2026-06-15 | 4.1% |

## Interpretation guardrails

- Every feature is calculated using data available **before** the gap day.
- Controls come from the same Compression lists, which reduces but does not eliminate selection bias.
- M&A/news gaps can be inherently unpredictable from charts; the next phase should separate those if the chart signature differs.
- The goal is to identify repeatable 45–60 session structures, then validate them on older unseen periods before adding a live scanner.
