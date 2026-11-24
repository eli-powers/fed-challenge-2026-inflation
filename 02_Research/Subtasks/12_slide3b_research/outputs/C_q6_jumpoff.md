# Q6.4 Jump-off check (Agent C, 2026-11-15)

Basis: SPF 2026Q3 median baseline (deadline 2026-08-11); oil assumption proxy EIA STEO aug26 (released 2026-08-11, completed 2026-08-06); core PCE actuals FRED PCEPILFE realtime 2026-10-29; Brent to 2026-11-11. Numbers from `code/C_q6_results.py`; decomposition table in `outputs/C_q6_jumpoff_decomposition.csv`.
Units: core PCE price index, SA. q/q ann. = quarterly-average index, annualized; Q4/Q4 = Q4 average over prior-year Q4 average.

## 1. Baseline 2026Q4 vs our October estimate
- Oct estimate: core m/m 0.29507% (`01_Finals/data/Slide1_Inflation_Data.xlsx` raw_Oct_build!B7, UMD build of Nov 13) on BEA Sep index 130.902 (PCEPILFE, realtime 2026-10-29) -> Oct index 131.288, **Oct y/y 3.242%** (matches Headline!C10 3.24 est.; the cell is a formula with no cached value).
- Actual 2026Q3 q/q ann. 2.468 (SPF 2026Q3 median for 2026Q3 was 2.70).
- SPF 2026Q3 median 2026Q4 q/q ann.: **2.6158**. Given our Oct estimate, it requires Nov and Dec core m/m of **0.053% each** (vs Oct est. 0.295%).
- If Nov = Dec = Oct m/m (0.295%): 2026Q4 q/q ann. 3.612, 2026 Q4/Q4 3.331.
- Baseline 2026 Q4/Q4 built from actual Q1-Q3 + SPF Q4: 3.082 (SPF published 2026 Q4/Q4 median 3.2876; gap = vintage break and Q3 miss, see A).

| Cell (central) | 2026Q4 q/q ann. | Nov = Dec m/m needed given Oct est. | 2026 Q4/Q4 |
|---|---|---|---|
| P1_steo_latest x pre | 2.812 | 0.101% | 3.131 |
| P1_steo_latest x post | 2.732 | 0.082% | 3.111 |
| P2_110_flat x pre | 2.848 | 0.110% | 3.140 |
| P2_110_flat x post | 2.765 | 0.090% | 3.119 |
| P3_feb26steo_plus25 x pre | 2.721 | 0.079% | 3.108 |
| P3_feb26steo_plus25 x post | 2.647 | 0.061% | 3.090 |

## 2. Size of the 2026Q3-Q4 part of the adjustment
Decomposition by the date of the oil-gap step (the mapping is linear in the gap steps; tiny compounding cross-terms aside).
`2026H2 steps only` = gap held at its 2026Q4 level from 2027Q1 on (only the realized/near-realized 2026Q3-Q4 oil moves); `2026Q3 step only` = gap held at its 2026Q3 level (fully realized quarter).

| Oil path | Regime | Gap steps | adj 2026Q4 q/q (pp) | adj 2027Q4 q/q (pp) | adj 2026 Q4/Q4 (pp) | adj 2027 Q4/Q4 (pp) | share of full 2027 Q4/Q4 adj |
|---|---|---|---|---|---|---|---|
| P1_steo_latest | pre | full | +0.197 | +0.078 | +0.049 | -0.002 | nan |
| P1_steo_latest | pre | 2026H2 steps only | +0.197 | +0.090 | +0.049 | +0.037 | nan |
| P1_steo_latest | pre | 2026Q3 step only | +0.031 | +0.008 | +0.008 | +0.010 | nan |
| P1_steo_latest | post | full | +0.116 | +0.869 | +0.029 | +0.527 | 1.00 |
| P1_steo_latest | post | 2026H2 steps only | +0.116 | +1.018 | +0.029 | +0.623 | 1.18 |
| P1_steo_latest | post | 2026Q3 step only | -0.039 | +0.209 | -0.010 | +0.270 | 0.51 |
| P2_110_flat | pre | full | +0.232 | +0.154 | +0.058 | +0.082 | 1.00 |
| P2_110_flat | pre | 2026H2 steps only | +0.232 | +0.107 | +0.058 | +0.043 | 0.52 |
| P2_110_flat | pre | 2026Q3 step only | +0.031 | +0.008 | +0.008 | +0.010 | 0.13 |
| P2_110_flat | post | full | +0.150 | +1.330 | +0.038 | +0.762 | 1.00 |
| P2_110_flat | post | 2026H2 steps only | +0.150 | +1.192 | +0.038 | +0.699 | 0.92 |
| P2_110_flat | post | 2026Q3 step only | -0.039 | +0.209 | -0.010 | +0.270 | 0.35 |
| P3_feb26steo_plus25 | pre | full | +0.105 | +0.149 | +0.026 | +0.018 | nan |
| P3_feb26steo_plus25 | pre | 2026H2 steps only | +0.105 | +0.045 | +0.026 | +0.022 | nan |
| P3_feb26steo_plus25 | pre | 2026Q3 step only | +0.031 | +0.008 | +0.008 | +0.010 | nan |
| P3_feb26steo_plus25 | post | full | +0.031 | +0.517 | +0.008 | +0.321 | 1.00 |
| P3_feb26steo_plus25 | post | 2026H2 steps only | +0.031 | +0.573 | +0.008 | +0.429 | 1.34 |
| P3_feb26steo_plus25 | post | 2026Q3 step only | -0.039 | +0.209 | -0.010 | +0.270 | 0.84 |

- P1_steo_latest: gap path, log pts: 2026Q3 12.2, 2026Q4 32.8, 2027Q1 25.0, 2027Q2 22.6, 2027Q3 19.9, 2027Q4 16.9
- P2_110_flat: gap path, log pts: 2026Q3 12.2, 2026Q4 37.2, 2027Q1 39.6, 2027Q2 43.8, 2027Q3 48.1, 2027Q4 52.6
- P3_feb26steo_plus25: gap path, log pts: 2026Q3 12.2, 2026Q4 21.5, 2027Q1 5.3, 2027Q2 9.4, 2027Q3 13.7, 2027Q4 18.2
