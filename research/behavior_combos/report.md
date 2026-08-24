# Behavior Combination Forward Test

- Train thresholds: **2022-2023**
- Forward test: **2024-2025**
- Base next-10-session >=15% gap rate: **0.38%**

## Top combinations (minimum 150 stock-days)

| Rule | Days | Hits | Hit rate | Lift |
|---|---:|---:|---:|---:|
| effort_low + undercut_low + hvclose_low + ret20_high | 189 | 5 | 2.65% | 7.05x |
| absorb_high + effort_low + downreject_low + undercut_low | 611 | 16 | 2.62% | 6.98x |
| effort_low + undercut_low + volcluster_high + hvclose_low | 202 | 5 | 2.48% | 6.59x |
| effort_low + downreject_low + undercut_low + hvclose_low | 567 | 13 | 2.29% | 6.11x |
| absorb_high + effort_low + undercut_low | 703 | 16 | 2.28% | 6.06x |
| downreject_low + undercut_low + hvclose_low + ret20_high | 223 | 5 | 2.24% | 5.97x |
| effort_low + undercut_low + hvclose_low | 620 | 13 | 2.10% | 5.59x |
| absorb_high + effort_low + undercut_low + volcluster_high | 394 | 8 | 2.03% | 5.41x |
| undercut_low + hvclose_low + ret20_high | 257 | 5 | 1.95% | 5.18x |
| effort_low + downreject_low + undercut_low + volcluster_high | 689 | 13 | 1.89% | 5.03x |
| downreject_low + undercut_low + volcluster_high + hvclose_low | 268 | 5 | 1.87% | 4.97x |
| effort_low + downreject_low + undercut_low | 2210 | 39 | 1.76% | 4.70x |
| downreject_low + undercut_low + hvclose_low | 745 | 13 | 1.74% | 4.65x |
| effort_low + downreject_low + undercut_low + ret20_high | 987 | 16 | 1.62% | 4.32x |
| undercut_low + volcluster_high + hvclose_low | 317 | 5 | 1.58% | 4.20x |
| effort_low + undercut_low | 2508 | 39 | 1.56% | 4.14x |
| effort_low + undercut_low + volcluster_high | 836 | 13 | 1.56% | 4.14x |
| effort_low + downreject_low + hvclose_low + ret20_high | 325 | 5 | 1.54% | 4.10x |
| undercut_low + hvclose_low | 849 | 13 | 1.53% | 4.08x |
| absorb_high + effort_low + undercut_low + ret20_high | 473 | 7 | 1.48% | 3.94x |
| effort_low + undercut_low + ret20_high | 1115 | 16 | 1.43% | 3.82x |
| effort_low + hvclose_low + ret20_high | 350 | 5 | 1.43% | 3.81x |
| absorb_high + downreject_low + undercut_low | 1283 | 16 | 1.25% | 3.32x |
| effort_low + undercut_low + ret20_high + vol_expand | 326 | 4 | 1.23% | 3.27x |
| downreject_low + hvclose_low + ret20_high | 411 | 5 | 1.22% | 3.24x |

## Notes

- These combinations are searched only from thresholds fixed on the earlier 2022-23 period.
- Because many combinations are tested, top results can still be selection noise; any promising rule must be validated on a third unseen period or broader universe.
