# Single-Day Reversal / Reclaim Research

- Window: **2019-01-01 to 2026-08-24**
- Symbols: **27**
- Total stock-days: **49084**
- Core reversal signals: **840**

Core setup = undercut prior 10-day low intraday, close back above that level, bullish candle, close in top 30% of range, and body >=35% of daily range. Volume expansion / EMA20 reclaim / prior-5-day-high reclaim are confirmations, not hard requirements.

## Forward results

| Horizon | Signals | Mean | Median | Win rate | Baseline mean | Baseline win | Edge |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1d | 840 | 0.10% | 0.10% | 51.8% | 0.09% | 50.7% | +0.01% |
| 3d | 840 | 0.34% | 0.25% | 53.6% | 0.28% | 52.4% | +0.07% |
| 5d | 838 | 0.61% | 0.42% | 54.4% | 0.45% | 53.3% | +0.16% |
| 10d | 837 | 1.25% | 0.94% | 56.6% | 0.88% | 54.2% | +0.37% |

## Confirmation score test

| Min score | Signals | Mean 3d | Win 3d | Mean 5d | Win 5d | Mean 10d | Win 10d |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 840 | 0.34% | 53.6% | 0.61% | 54.4% | 1.25% | 56.6% |
| 6 | 449 | 0.41% | 52.3% | 0.71% | 53.8% | 1.61% | 56.7% |
| 7 | 64 | 0.29% | 48.4% | 0.66% | 59.4% | 3.53% | 70.3% |
| 8 | 14 | 2.37% | 78.6% | 4.45% | 78.6% | 7.51% | 71.4% |

## 1810.HK diagnostic

- 2026-08-18: score 5, CLV 0.73, volume ratio 0.95, EMA20 reclaim=False, prior-high reclaim=False

## Guardrails

- No future information is used in signal construction.
- This first pass is deliberately simple. If it shows edge, validate on a broader unseen universe before adding to production scanners.
