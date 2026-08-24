# Accumulation-Behavior Pre-Gap Research

- Window: **2022-01-01 to 2025-12-31**
- Symbols: **26**
- Eligible stock-days: **0**
- Stock-days with >=15% opening gap within next 10 sessions: **0**

## Strongest behavior differences

| Feature | Pre-power-gap mean | Normal mean | Std difference |
|---|---:|---:|---:|
| absorb20 | nan | nan | +nan |
| effort_no_down20 | nan | nan | +nan |
| down_reject20 | nan | nan | +nan |
| undercut_reclaim20 | nan | nan | +nan |
| updown_vol20 | nan | nan | +nan |
| resilience20 | nan | nan | +nan |
| vol_asym20 | nan | nan | +nan |
| highvol_close_strength10 | nan | nan | +nan |
| volume_cluster10 | nan | nan | +nan |
| range_contract10_40 | nan | nan | +nan |

## Forward tail tests (thresholds learned on 2022-23, tested on 2024-25)

| Feature | Tail | Days | Hit rate | Base | Lift |
|---|---|---:|---:|---:|---:|
| absorb20 | <bound method NDFrame.tail of feature      absorb20
tail             HIGH
threshold         NaN
days                0
hit_rate          NaN
base_rate         NaN
lift              NaN
Name: 0, dtype: object> | 0 | nan% | nan% | nanx |
| absorb20 | <bound method NDFrame.tail of feature      absorb20
tail              LOW
threshold         NaN
days                0
hit_rate          NaN
base_rate         NaN
lift              NaN
Name: 1, dtype: object> | 0 | nan% | nan% | nanx |
| effort_no_down20 | <bound method NDFrame.tail of feature      effort_no_down20
tail                     HIGH
threshold                 NaN
days                        0
hit_rate                  NaN
base_rate                 NaN
lift                      NaN
Name: 2, dtype: object> | 0 | nan% | nan% | nanx |
| effort_no_down20 | <bound method NDFrame.tail of feature      effort_no_down20
tail                      LOW
threshold                 NaN
days                        0
hit_rate                  NaN
base_rate                 NaN
lift                      NaN
Name: 3, dtype: object> | 0 | nan% | nan% | nanx |
| down_reject20 | <bound method NDFrame.tail of feature      down_reject20
tail                  HIGH
threshold              NaN
days                     0
hit_rate               NaN
base_rate              NaN
lift                   NaN
Name: 4, dtype: object> | 0 | nan% | nan% | nanx |
| down_reject20 | <bound method NDFrame.tail of feature      down_reject20
tail                   LOW
threshold              NaN
days                     0
hit_rate               NaN
base_rate              NaN
lift                   NaN
Name: 5, dtype: object> | 0 | nan% | nan% | nanx |
| undercut_reclaim20 | <bound method NDFrame.tail of feature      undercut_reclaim20
tail                       HIGH
threshold                   NaN
days                          0
hit_rate                    NaN
base_rate                   NaN
lift                        NaN
Name: 6, dtype: object> | 0 | nan% | nan% | nanx |
| undercut_reclaim20 | <bound method NDFrame.tail of feature      undercut_reclaim20
tail                        LOW
threshold                   NaN
days                          0
hit_rate                    NaN
base_rate                   NaN
lift                        NaN
Name: 7, dtype: object> | 0 | nan% | nan% | nanx |
| updown_vol20 | <bound method NDFrame.tail of feature      updown_vol20
tail                 HIGH
threshold             NaN
days                    0
hit_rate              NaN
base_rate             NaN
lift                  NaN
Name: 8, dtype: object> | 0 | nan% | nan% | nanx |
| updown_vol20 | <bound method NDFrame.tail of feature      updown_vol20
tail                  LOW
threshold             NaN
days                    0
hit_rate              NaN
base_rate             NaN
lift                  NaN
Name: 9, dtype: object> | 0 | nan% | nan% | nanx |
| resilience20 | <bound method NDFrame.tail of feature      resilience20
tail                 HIGH
threshold             NaN
days                    0
hit_rate              NaN
base_rate             NaN
lift                  NaN
Name: 10, dtype: object> | 0 | nan% | nan% | nanx |
| resilience20 | <bound method NDFrame.tail of feature      resilience20
tail                  LOW
threshold             NaN
days                    0
hit_rate              NaN
base_rate             NaN
lift                  NaN
Name: 11, dtype: object> | 0 | nan% | nan% | nanx |

## Behavior score forward test

| Min score | Days | Hit rate | Base | Lift |
|---:|---:|---:|---:|---:|
| 2 | 0 | nan% | nan% | nanx |
| 3 | 0 | nan% | nan% | nanx |
| 4 | 0 | nan% | nan% | nanx |
| 5 | 0 | nan% | nan% | nanx |
| 6 | 0 | nan% | nan% | nanx |
| 7 | 0 | nan% | nan% | nanx |
| 8 | 0 | nan% | nan% | nanx |

## Guardrail

- Features use only price/volume data available on the signal date. Future gaps are used only as labels.
- Quantile thresholds are learned on 2022-23 and evaluated on 2024-25 to reduce look-ahead overfitting.
- This is still a limited 26-symbol research universe; any positive signal must later be tested on a much broader unseen universe.
