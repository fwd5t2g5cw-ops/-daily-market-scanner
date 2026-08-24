# Two-Stage Single-Day Reversal Validation

- Source: frozen broad unseen reversal signals (3401 core events)
- Entry confirmation window: next 1–3 sessions
- Entry is confirmation-day close; returns are measured after entry, so reversal-day gains are not counted.

## Rules

- REV_HIGH: close above reversal-day high
- PREV5_HIGH: close above the pre-reversal 5-day high
- REV_HIGH+EMA20: reversal-high breakout while closing above EMA20
- BOTH_HIGHS: close above both reversal high and pre-reversal 5-day high
- BOTH_HIGHS+EMA20: both-high breakout and above EMA20

## Overall results

| Rule | N | Avg delay | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg maxDD 10d |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| REV_HIGH+EMA20 | 1271 | 1.76 | 0.11% | 53.2% | 0.40% | 55.4% | 0.77% | 56.2% | -4.67% |
| PREV5_HIGH | 481 | 2.08 | 0.17% | 52.2% | 0.31% | 52.0% | 1.05% | 55.9% | -4.31% |
| BOTH_HIGHS | 477 | 2.10 | 0.16% | 51.8% | 0.28% | 51.6% | 1.05% | 56.0% | -4.34% |
| BOTH_HIGHS+EMA20 | 451 | 2.13 | 0.19% | 52.1% | 0.26% | 50.8% | 0.99% | 56.1% | -4.32% |
| REV_HIGH | 2229 | 1.50 | -0.01% | 50.7% | 0.04% | 53.1% | 0.44% | 54.8% | -5.19% |

## By market (N>=10)

| Market | Rule | N | Mean 5d | Win 5d | Mean 10d | Win 10d | Avg maxDD 10d |
|---|---|---:|---:|---:|---:|---:|---:|
| CA | REV_HIGH+EMA20 | 234 | 0.42% | 57.3% | 1.14% | 61.5% | -3.50% |
| CA | REV_HIGH | 372 | 0.33% | 57.0% | 0.94% | 61.0% | -3.90% |
| CA | PREV5_HIGH | 92 | 0.23% | 53.3% | 1.14% | 57.6% | -3.45% |
| CA | BOTH_HIGHS | 91 | 0.21% | 52.7% | 1.11% | 57.1% | -3.49% |
| CA | BOTH_HIGHS+EMA20 | 87 | 0.03% | 50.6% | 0.73% | 55.2% | -3.54% |
| HK | REV_HIGH+EMA20 | 174 | 0.74% | 58.6% | 0.83% | 51.1% | -5.04% |
| HK | REV_HIGH | 314 | 0.62% | 53.5% | 0.58% | 50.3% | -5.19% |
| HK | PREV5_HIGH | 69 | 0.45% | 52.2% | 0.89% | 46.4% | -4.72% |
| HK | BOTH_HIGHS | 68 | 0.44% | 51.5% | 0.98% | 47.1% | -4.72% |
| HK | BOTH_HIGHS+EMA20 | 68 | 0.40% | 51.5% | 0.88% | 47.1% | -4.68% |
| US | REV_HIGH+EMA20 | 863 | 0.32% | 54.0% | 0.66% | 55.5% | -4.91% |
| US | BOTH_HIGHS+EMA20 | 296 | 0.30% | 50.7% | 1.09% | 58.4% | -4.47% |
| US | PREV5_HIGH | 320 | 0.30% | 51.6% | 1.06% | 57.5% | -4.47% |
| US | BOTH_HIGHS | 318 | 0.26% | 51.3% | 1.05% | 57.5% | -4.50% |
| US | REV_HIGH | 1543 | -0.15% | 51.9% | 0.29% | 54.0% | -5.50% |

## Decision

- The two-stage version is useful only if confirmation improves 5–10 day expectancy and/or drawdown versus buying the reversal close, with enough samples to survive market splits.
