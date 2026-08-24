# Single-Day Reversal — Broad Unseen Validation

- Frozen universe: **119 symbols** (US 79, HK 20, Canada 20)
- Downloaded successfully: **119**
- Window: **2020-01-01 to 2026-08-24**
- Stock-days: **197118**
- Core signals: **3401**

Universe and rules were frozen before this run and exclude the original discovery universe.

## Main results

| Group | N | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg max-up 10d | Avg max-DD 10d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BASELINE | 197118 | 0.25% | 53.0% | 0.41% | 53.9% | 0.80% | 55.1% | 5.37% | -4.59% |
| CORE | 3401 | 0.36% | 54.9% | 0.39% | 53.1% | 0.59% | 53.5% | 5.62% | -5.19% |
| SCORE>=6 | 1782 | 0.37% | 56.0% | 0.38% | 53.0% | 0.37% | 53.1% | 5.74% | -5.73% |
| SCORE>=7 | 219 | 0.56% | 56.0% | 0.59% | 56.9% | 0.94% | 60.1% | 5.33% | -4.36% |
| SCORE>=8 | 20 | 0.51% | 57.9% | 1.30% | 68.4% | 1.94% | 52.6% | 6.22% | -3.26% |
| VOL_EXPAND | 1451 | 0.35% | 55.4% | 0.37% | 52.7% | 0.41% | 53.7% | 5.93% | -6.03% |
| EMA20_RECLAIM | 539 | 0.47% | 57.2% | 0.48% | 55.2% | 0.49% | 54.3% | 5.08% | -4.41% |
| PREV_HIGH_RECLAIM | 31 | 1.01% | 63.3% | 1.15% | 66.7% | 1.66% | 53.3% | 5.74% | -3.20% |
| US_CORE | 2284 | 0.38% | 55.9% | 0.31% | 53.0% | 0.57% | 53.9% | 5.77% | -5.41% |
| US_SCORE>=7 | 139 | 0.35% | 52.5% | 0.15% | 51.1% | 0.62% | 55.4% | 5.38% | -4.97% |
| HK_CORE | 551 | 0.17% | 48.4% | 0.48% | 48.4% | 0.37% | 48.2% | 5.81% | -5.36% |
| HK_SCORE>=7 | 25 | 1.03% | 54.2% | 1.23% | 70.8% | 1.26% | 70.8% | 6.08% | -4.11% |
| CA_CORE | 566 | 0.45% | 57.5% | 0.62% | 57.7% | 0.89% | 57.2% | 4.83% | -4.12% |
| CA_SCORE>=7 | 55 | 0.88% | 65.5% | 1.40% | 65.5% | 1.62% | 67.3% | 4.88% | -2.91% |

## Exact confirmation combinations (N>=10)

| Combination | N | Mean 5d | Win 5d | Mean 10d | Win 10d |
|---|---:|---:|---:|---:|---:|
| vol_expand=1;ema20_reclaim=1;prev_high_reclaim=1 | 20 | 1.30% | 68.4% | 1.94% | 52.6% |
| vol_expand=0;ema20_reclaim=0;prev_high_reclaim=0 | 1619 | 0.39% | 53.1% | 0.84% | 53.9% |
| vol_expand=1;ema20_reclaim=1;prev_high_reclaim=0 | 191 | 0.51% | 55.0% | 0.79% | 60.2% |
| vol_expand=1;ema20_reclaim=0;prev_high_reclaim=0 | 1235 | 0.34% | 52.0% | 0.31% | 52.5% |
| vol_expand=0;ema20_reclaim=1;prev_high_reclaim=0 | 325 | 0.40% | 54.5% | 0.24% | 51.1% |

## Decision rule

- Only promote this setup if the broad unseen universe preserves a meaningful 5–10 day return/win-rate edge and the stronger confirmation bucket has enough samples.
- Score 8 from the discovery set had only 14 samples, so it must not be trusted unless it replicates here.
