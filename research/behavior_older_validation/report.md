# Older Unseen Behavior Validation

- Validation period: **2018-2021**
- Thresholds frozen from **2022-2023** research
- Eligible stock-days: **21665**
- Base next-10-session >=15% gap rate: **0.39%**

| Rule | Days | Hits | Hit rate | Lift |
|---|---:|---:|---:|---:|
| effort_low + undercut_low + volcluster_high + hvclose_low | 303 | 1 | 0.33% | 0.84x |
| effort_low + undercut_low + hvclose_low | 1080 | 1 | 0.09% | 0.24x |
| effort_low + downreject_low + undercut_low | 3743 | 1 | 0.03% | 0.07x |
| effort_low + undercut_low | 4123 | 1 | 0.02% | 0.06x |
| absorb_high + effort_low + undercut_low | 840 | 0 | 0.00% | 0.00x |
| absorb_high + effort_low + downreject_low + undercut_low | 763 | 0 | 0.00% | 0.00x |
| effort_low + undercut_low + hvclose_low + ret20_high | 355 | 0 | 0.00% | 0.00x |

A rule is only interesting if the lift survives this older unseen period as well as the 2024-25 forward test.
