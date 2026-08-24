# Pre-Gap 60-Day Chart Pattern Research — Matched Controls

- Compression snapshots used: **2**
- Unique symbols in snapshots: **54**
- Distinct >= 4% opening-gap events: **33**
- Same-stock matched control dates: **99**

Controls are earlier dates from the **same stock**, 20–120 sessions before its gap, with no >=4% gap in the following five sessions. This is a much cleaner test of what changes as a gap approaches.

## Largest pre-gap differences vs same-stock controls

| Feature | Gap mean/rate | Control mean/rate | Difference |
|---|---:|---:|---:|
| ema20_gt_ema50 | 79% | 55% | +24% |
| shallow_pullback_8 | 73% | 52% | +21% |
| trend_stack | 58% | 38% | +19% |
| near_high_5 | 42% | 26% | +16% |
| range_contract_075 | 61% | 46% | +14% |
| volume_expand_110 | 27% | 39% | -12% |
| atr_contract_080 | 3% | 13% | -10% |
| higher_lows_2of2 | 30% | 22% | +8% |

## Largest numeric shifts

| Feature | Gap | Control | Std. difference |
|---|---:|---:|---:|
| ema20_slope10_pct | 2.30 | 0.18 | +0.55 |
| dist_from_60d_high_pct | 8.55 | 12.13 | -0.40 |
| pullback_from_60d_close_high_pct | 6.98 | 10.42 | -0.39 |
| up_days20_pct | 51.97 | 49.24 | +0.28 |
| max_drawdown60_pct | -14.50 | -16.62 | +0.24 |
| ret60_pct | 5.71 | 1.91 | +0.23 |
| vol10_vs40 | 1.02 | 1.08 | -0.21 |
| higher_low_score | 1.12 | 0.98 | +0.20 |

## Best exploratory combinations

| Rule | Gap hits | Control hits | Gap coverage | Sample precision |
|---|---:|---:|---:|---:|
| near_high_5 + range_contract_075 + atr_expand_110 | 3 | 1 | 9% | 75% |
| near_high_5 + range_vs_prior_075 + atr_expand_110 | 3 | 1 | 9% | 75% |
| range_contract_075 + range_vs_prior_075 + atr_expand_110 | 5 | 2 | 15% | 71% |
| range_contract_075 + atr_expand_110 + trend_stack | 5 | 2 | 15% | 71% |
| range_vs_prior_075 + atr_expand_110 + trend_stack | 5 | 2 | 15% | 71% |
| range_contract_075 + atr_expand_110 + ema20_gt_ema50 | 6 | 3 | 18% | 67% |
| range_vs_prior_075 + atr_expand_110 + ema20_gt_ema50 | 6 | 3 | 18% | 67% |
| shallow_pullback_8 + range_vs_prior_075 + atr_expand_110 | 5 | 3 | 15% | 62% |
| range_contract_075 + atr_expand_110 + close_gt_ema20 | 5 | 3 | 15% | 62% |
| range_vs_prior_075 + volume_dry_080 + ema20_gt_ema50 | 4 | 3 | 12% | 57% |

## Gap examples

| Symbol | Gap date | Opening gap |
|---|---|---:|
| CRNX | 2026-07-07 | 98.9% |
| UTZ | 2026-07-21 | 89.0% |
| APGE | 2026-06-22 | 46.7% |
| SAFT | 2026-07-24 | 41.2% |
| ATAI | 2026-07-16 | 31.8% |
| DSGR | 2026-07-16 | 26.3% |
| ATAI | 2026-04-20 | 24.7% |
| TECH | 2026-06-25 | 19.3% |
| SAIC | 2026-06-01 | 15.3% |
| V | 2026-04-29 | 8.8% |
| DGX | 2026-07-23 | 8.7% |
| AMCR | 2026-05-06 | 7.9% |
| ROKU | 2026-05-01 | 7.7% |
| ATAI | 2026-05-18 | 7.3% |
| ACA | 2026-06-22 | 6.7% |
| EXPD | 2026-05-05 | 6.6% |
| BBVA | 2026-07-30 | 6.3% |
| UTZ | 2026-05-06 | 6.1% |
| PAYO | 2026-05-07 | 5.6% |
| IDT | 2026-06-04 | 5.5% |
| KO | 2026-04-28 | 5.4% |
| PHVS | 2026-05-08 | 5.4% |
| SEIC | 2026-04-23 | 5.1% |
| KO | 2026-07-28 | 5.0% |
| LNG | 2026-08-06 | 5.0% |
| USFD | 2026-08-06 | 4.8% |
| KFY | 2026-06-23 | 4.6% |
| SON | 2026-07-23 | 4.6% |
| MA | 2026-04-29 | 4.4% |
| ROKU | 2026-06-12 | 4.3% |

## Guardrails

- All features use only data available before the event date.
- This remains an exploratory selected sample; any scanner rule must be validated on older unseen market data.
- A failure to find a strong chart signature is a valid result; surprise M&A/news gaps may simply not be predictable from price/volume alone.
