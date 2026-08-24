# Single-Day Reversal — Stop / R-Multiple Validation

- Source: two-stage reversal entries from the frozen broad unseen universe.
- Stop: reversal-day low.
- Targets: 1R, 2R, 3R.
- Maximum holding period: 10 sessions after entry.
- If stop and target are both touched on the same daily bar, stop is assumed first (conservative).
- Trades requiring >20% stop distance are excluded as structurally impractical.

## Overall

| Rule | Target | N | Target hit | Stop hit | Mean return | Mean R | Win rate | Avg stop distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BOTH_HIGHS | 1R | 471 | 29.7% | 18.3% | 1.02% | 0.15R | 57.5% | 7.24% |
| BOTH_HIGHS | 2R | 471 | 4.5% | 18.7% | 1.10% | 0.16R | 54.6% | 7.24% |
| BOTH_HIGHS | 3R | 471 | 0.8% | 18.7% | 1.13% | 0.16R | 54.6% | 7.24% |
| BOTH_HIGHS+EMA20 | 1R | 445 | 29.7% | 17.8% | 1.04% | 0.15R | 57.8% | 7.29% |
| BOTH_HIGHS+EMA20 | 2R | 445 | 3.8% | 18.2% | 1.07% | 0.15R | 54.6% | 7.29% |
| BOTH_HIGHS+EMA20 | 3R | 445 | 0.9% | 18.2% | 1.09% | 0.15R | 54.6% | 7.29% |
| PREV5_HIGH | 1R | 475 | 29.9% | 18.5% | 1.02% | 0.14R | 57.5% | 7.20% |
| PREV5_HIGH | 2R | 475 | 4.4% | 18.9% | 1.10% | 0.16R | 54.5% | 7.20% |
| PREV5_HIGH | 3R | 475 | 0.8% | 18.9% | 1.13% | 0.16R | 54.5% | 7.20% |
| REV_HIGH | 1R | 2219 | 42.8% | 37.2% | 0.38% | 0.07R | 54.2% | 4.94% |
| REV_HIGH | 2R | 2219 | 17.4% | 41.6% | 0.60% | 0.12R | 47.9% | 4.94% |
| REV_HIGH | 3R | 2219 | 7.3% | 42.3% | 0.70% | 0.14R | 46.9% | 4.94% |
| REV_HIGH+EMA20 | 1R | 1264 | 40.6% | 29.6% | 0.73% | 0.13R | 57.8% | 5.59% |
| REV_HIGH+EMA20 | 2R | 1264 | 13.4% | 32.7% | 0.83% | 0.15R | 51.7% | 5.59% |
| REV_HIGH+EMA20 | 3R | 1264 | 4.6% | 33.0% | 0.94% | 0.17R | 51.3% | 5.59% |

## By market (N>=20)

| Market | Rule | Target | N | Target hit | Stop hit | Mean return | Mean R | Win rate | Avg stop distance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CA | BOTH_HIGHS | 1R | 91 | 36.3% | 13.2% | 0.91% | 0.22R | 58.2% | 5.98% |
| CA | BOTH_HIGHS | 2R | 91 | 3.3% | 13.2% | 1.14% | 0.27R | 56.0% | 5.98% |
| CA | BOTH_HIGHS | 3R | 91 | 0.0% | 13.2% | 1.16% | 0.27R | 56.0% | 5.98% |
| CA | BOTH_HIGHS+EMA20 | 1R | 87 | 33.3% | 13.8% | 0.65% | 0.18R | 56.3% | 5.96% |
| CA | BOTH_HIGHS+EMA20 | 2R | 87 | 2.3% | 13.8% | 0.76% | 0.21R | 54.0% | 5.96% |
| CA | BOTH_HIGHS+EMA20 | 3R | 87 | 0.0% | 13.8% | 0.77% | 0.21R | 54.0% | 5.96% |
| CA | PREV5_HIGH | 1R | 92 | 35.9% | 14.1% | 0.93% | 0.22R | 58.7% | 5.91% |
| CA | PREV5_HIGH | 2R | 92 | 3.3% | 14.1% | 1.17% | 0.27R | 56.5% | 5.91% |
| CA | PREV5_HIGH | 3R | 92 | 0.0% | 14.1% | 1.18% | 0.27R | 56.5% | 5.91% |
| CA | REV_HIGH | 1R | 371 | 45.6% | 31.8% | 0.57% | 0.16R | 59.0% | 4.07% |
| CA | REV_HIGH | 2R | 371 | 18.3% | 36.1% | 0.82% | 0.24R | 53.4% | 4.07% |
| CA | REV_HIGH | 3R | 371 | 6.2% | 36.7% | 0.91% | 0.26R | 52.6% | 4.07% |
| CA | REV_HIGH+EMA20 | 1R | 234 | 41.5% | 26.9% | 0.85% | 0.18R | 61.1% | 4.54% |
| CA | REV_HIGH+EMA20 | 2R | 234 | 12.0% | 29.5% | 0.98% | 0.22R | 56.0% | 4.54% |
| CA | REV_HIGH+EMA20 | 3R | 234 | 1.7% | 29.5% | 1.02% | 0.22R | 55.6% | 4.54% |
| HK | BOTH_HIGHS | 1R | 68 | 27.9% | 14.7% | 0.73% | 0.09R | 51.5% | 8.26% |
| HK | BOTH_HIGHS | 2R | 68 | 5.9% | 14.7% | 0.68% | 0.07R | 47.1% | 8.26% |
| HK | BOTH_HIGHS | 3R | 68 | 1.5% | 14.7% | 0.90% | 0.10R | 47.1% | 8.26% |
| HK | BOTH_HIGHS+EMA20 | 1R | 68 | 27.9% | 14.7% | 0.79% | 0.09R | 51.5% | 8.33% |
| HK | BOTH_HIGHS+EMA20 | 2R | 68 | 4.4% | 14.7% | 0.66% | 0.06R | 47.1% | 8.33% |
| HK | BOTH_HIGHS+EMA20 | 3R | 68 | 1.5% | 14.7% | 0.80% | 0.08R | 47.1% | 8.33% |
| HK | PREV5_HIGH | 1R | 69 | 27.5% | 14.5% | 0.65% | 0.08R | 50.7% | 8.24% |
| HK | PREV5_HIGH | 2R | 69 | 5.8% | 14.5% | 0.60% | 0.06R | 46.4% | 8.24% |
| HK | PREV5_HIGH | 3R | 69 | 1.4% | 14.5% | 0.81% | 0.08R | 46.4% | 8.24% |
| HK | REV_HIGH | 1R | 313 | 47.0% | 37.4% | 0.70% | 0.10R | 54.0% | 4.82% |
| HK | REV_HIGH | 2R | 313 | 22.4% | 42.5% | 1.03% | 0.17R | 46.3% | 4.82% |
| HK | REV_HIGH | 3R | 313 | 8.9% | 44.1% | 0.98% | 0.14R | 44.1% | 4.82% |
| HK | REV_HIGH+EMA20 | 1R | 173 | 43.4% | 27.2% | 0.73% | 0.15R | 56.1% | 5.91% |
| HK | REV_HIGH+EMA20 | 2R | 173 | 18.5% | 29.5% | 0.91% | 0.21R | 49.7% | 5.91% |
| HK | REV_HIGH+EMA20 | 3R | 173 | 7.5% | 31.2% | 0.93% | 0.19R | 48.0% | 5.91% |
| US | BOTH_HIGHS | 1R | 312 | 28.2% | 20.5% | 1.12% | 0.14R | 58.7% | 7.39% |
| US | BOTH_HIGHS | 2R | 312 | 4.5% | 21.2% | 1.18% | 0.14R | 55.8% | 7.39% |
| US | BOTH_HIGHS | 3R | 312 | 1.0% | 21.2% | 1.17% | 0.14R | 55.8% | 7.39% |
| US | BOTH_HIGHS+EMA20 | 1R | 290 | 29.0% | 19.7% | 1.22% | 0.15R | 59.7% | 7.44% |
| US | BOTH_HIGHS+EMA20 | 2R | 290 | 4.1% | 20.3% | 1.26% | 0.15R | 56.6% | 7.44% |
| US | BOTH_HIGHS+EMA20 | 3R | 290 | 1.0% | 20.3% | 1.25% | 0.15R | 56.6% | 7.44% |
| US | PREV5_HIGH | 1R | 314 | 28.7% | 20.7% | 1.13% | 0.14R | 58.6% | 7.35% |
| US | PREV5_HIGH | 2R | 314 | 4.5% | 21.3% | 1.19% | 0.14R | 55.7% | 7.35% |
| US | PREV5_HIGH | 3R | 314 | 1.0% | 21.3% | 1.18% | 0.14R | 55.7% | 7.35% |
| US | REV_HIGH | 1R | 1535 | 41.2% | 38.5% | 0.27% | 0.04R | 53.1% | 5.17% |
| US | REV_HIGH | 2R | 1535 | 16.2% | 42.7% | 0.45% | 0.08R | 46.9% | 5.17% |
| US | REV_HIGH | 3R | 1535 | 7.2% | 43.3% | 0.59% | 0.11R | 46.1% | 5.17% |
| US | REV_HIGH+EMA20 | 1R | 857 | 39.8% | 30.8% | 0.70% | 0.11R | 57.3% | 5.81% |
| US | REV_HIGH+EMA20 | 2R | 857 | 12.7% | 34.2% | 0.77% | 0.12R | 51.0% | 5.81% |
| US | REV_HIGH+EMA20 | 3R | 857 | 4.8% | 34.3% | 0.92% | 0.15R | 50.9% | 5.81% |

## Reading the test

- A useful trading rule should have positive mean R after the conservative stop-first assumption, not merely a high target-hit rate.
- Market-specific results matter because the prior validation showed different behavior in US, HK and Canada.
