# Accumulation-Behavior Pre-Gap Research

- Window: **2022-01-01 to 2025-12-31**
- Symbols: **26**
- Eligible stock-days: **25636**
- Stock-days with >=15% opening gap within next 10 sessions: **113**

## Strongest behavior differences

| Feature | Pre-power-gap mean | Normal mean | Std difference |
|---|---:|---:|---:|
| effort_no_down20 | 0.133 | 0.616 | -0.74 |
| dist60high | -0.214 | -0.111 | -0.63 |
| down_reject20 | 0.018 | 0.247 | -0.63 |
| updown_vol20 | 0.959 | 1.217 | -0.41 |
| volume_cluster10 | 3.027 | 2.371 | +0.36 |
| highvol_close_strength10 | 0.454 | 0.509 | -0.30 |
| vol_asym20 | 0.960 | 1.057 | -0.26 |
| absorb20 | 1.867 | 1.464 | +0.26 |
| resilience20 | 1.146 | 1.318 | -0.21 |
| ret20 | -0.023 | 0.012 | -0.21 |

## Forward tail tests (thresholds learned on 2022-23, tested on 2024-25)

| Feature | Tail | Days | Hit rate | Base | Lift |
|---|---|---:|---:|---:|---:|
| undercut_reclaim20 | LOW | 3962 | 0.98% | 0.38% | 2.62x |
| ret20 | HIGH | 2492 | 0.56% | 0.38% | 1.50x |
| effort_no_down20 | LOW | 7338 | 0.53% | 0.38% | 1.42x |
| highvol_close_strength10 | LOW | 2641 | 0.49% | 0.38% | 1.31x |
| down_reject20 | LOW | 10547 | 0.46% | 0.38% | 1.24x |
| absorb20 | HIGH | 5223 | 0.44% | 0.38% | 1.17x |
| vol_asym20 | HIGH | 2544 | 0.35% | 0.38% | 0.94x |
| vol_asym20 | LOW | 2550 | 0.31% | 0.38% | 0.84x |
| resilience20 | HIGH | 2747 | 0.25% | 0.38% | 0.68x |
| range_contract10_40 | LOW | 2580 | 0.19% | 0.38% | 0.52x |
| volume_cluster10 | LOW | 5343 | 0.19% | 0.38% | 0.50x |
| effort_no_down20 | HIGH | 5714 | 0.18% | 0.38% | 0.47x |

## Behavior score forward test

| Min score | Days | Hit rate | Base | Lift |
|---:|---:|---:|---:|---:|
| 2 | 10757 | 0.32% | 0.38% | 0.84x |
| 3 | 7839 | 0.23% | 0.38% | 0.61x |
| 4 | 4798 | 0.13% | 0.38% | 0.33x |
| 5 | 2488 | 0.12% | 0.38% | 0.32x |
| 6 | 1084 | 0.09% | 0.38% | 0.25x |
| 7 | 271 | 0.37% | 0.38% | 0.98x |
| 8 | 3 | 0.00% | 0.38% | 0.00x |

## Guardrail

- Features use only price/volume data available on the signal date. Future gaps are used only as labels.
- Quantile thresholds are learned on 2022-23 and evaluated on 2024-25 to reduce look-ahead overfitting.
- This is still a limited 26-symbol research universe; any positive signal must later be tested on a much broader unseen universe.
