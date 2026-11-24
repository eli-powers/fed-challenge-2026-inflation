# notes_C: breadth and component-sum gap (brief C, run 2026-11-14)

Status: Round 1, not audited. All numbers come from `code/C_*.py` (run from the project root with `python3 -I`), which read saved files only.

## Scripts and outputs
| Script | Writes (in `outputs/`) |
|---|---|
| `code/C_common.py` | shared engine (imports the audited `04_oct_pce_build/code/D_common.py`; logic follows `07_breadth_reconciliation/code/recon.py`, unedited) |
| `code/C_breadth.py` | `C_breadth.csv`, `C_breadth_ts.csv`, `C_carried_forward.csv`, `C_carried_forward_lines.csv`, `C_carried_forward_stress.csv`, `C_flip_distance_oct.csv`, `C_hospital_lines.csv`, `C_leaf_rollup_check.csv` |
| `code/C_sum_gap.py` | `C_sum_gap.csv`, `C_sum_gap_basis_reconciliation.csv`, `C_sum_gap_monthly_residual.csv` |
| `code/C_waller_variants.py` | `C_waller_variants.csv` |

Report 07's old scratchpad dependency did not matter: `recon.py` and `oct_leaf.py` run as is (`oct_leaf.py` needs the code folder as argument). I did not rely on them; `C_breadth.py` asserts that it reproduces their eight Sep/Oct breadth figures to within 0.06 pp and it does.

## Definitions used (conservative choices, all recorded)
- **Breadth** = share of core PCE nominal spending weight whose k-month rate is strictly above 3%. 3m rates are annualized first: `100*((I_t/I_(t-3))^4 - 1)`. 12m: `100*(I_t/I_(t-12) - 1)`.
- **Weight basis (primary): start-of-window.** Nominal spending shares (U20405) of the window's base month: Jun 2026 for Sep 3m, Sep 2025 for Sep 12m, Jul 2026 for Oct 3m, Oct 2025 for Oct 12m. Rescaling over the covered set cancels in the ratio. Sensitivity rows in `C_breadth.csv` (role `sensitivity`) use 12m-ago weights for the 3m rate: Sep sub-line 43.60, Oct 43.83 (the two labels on the October tab).
- **Primary method: sub-line** (184 core pricing lines; 13 leaves split into 48 sub-lines, the Sep 30, 2026 BEA source table). **Robustness: leaf** (149 core leaves).
- **Sub-line weights:** leaf nominal x (sub-line nominal / sum of that leaf's sub-line nominals); tenant rent (156 -> sub-line 157) and NPISH (342) take the leaf nominal. Same as `recon.py`.
- **October** = estimate: BEA's Sep index (vintage Nov 10) extended by the audited build's October m/m for each pricing line (`04_oct_pce_build/outputs/D_build_2026-10_lines.csv`, column `pi`). BEA publishes October PCE on Nov 25, after the Nov 18 cutoff.
- **Headline** units: all 177 BEA leaves (lines 145 and 333 have no price index) or their 212 sub-line units. My Sep 12m headline leaf figure 59.80 equals report 05's.
- **Supercore** = services ex energy and housing within core: leaves with line >= 150, excluding 153-164 and 169-171 (same rule as `analyze_baskets.py` `supercore()`); 78 leaves / 110 sub-lines.
- **Core services** (Waller basis) = services leaves (line >= 150) in the core set, housing included: 84 leaves / 116 sub-lines.
- **Net lines.** Sub-line 16 (belongs to leaf 13, used autos net) has a negative nominal value; it carries -0.009% of core weight. Excluding it moves breadth by +0.004 to +0.005 pp. Immaterial; left in, as in report 07.
- **Time series** applies the current 184-line sub-line set to all history (BEA current-vintage U20405/U20404 start Jan 2017, so 12m rates start Jan 2018 and 3m rates would start Apr 2017; the series starts Jan 2018 as asked).

## 1. Breadth, Sep 2026 (BEA published) and Oct 2026 (estimate): `C_breadth.csv`
Core, start-of-window weights (percent of weight with rate > 3%):

| | Sep 3m ann | Oct 3m ann (est) | Sep 12m | Oct 12m (est) |
|---|---:|---:|---:|---:|
| sub-line (primary) | 43.667 | 43.752 | 57.713 | 51.127 |
| leaf (robustness) | 44.814 | 45.467 | 60.626 | 54.038 |

Report 07's expected figures (57.7 -> 51.1, 43.7 -> 43.8; leaf 60.6 -> ~54.0, 44.8 -> ~45.5) are **reproduced** to the rounding shown there. Headline and supercore rows are in the CSV; the supercore 12m figure falls by 14.5 pp (leaf) and 14.5 pp (sub-line) Sep to Oct (see Worth a look).

**Leaf October is approximate, and how approximate.** For the 12 split leaves other than tenant rent, October leaf m/m = fixed-share roll-up (September within-leaf shares) of sub-line m/m. BEA's leaf index is a chained Fisher. `C_leaf_rollup_check.csv` tests the same roll-up on the 36 months Oct 2023-Sep 2026 against BEA's own leaf m/m: mean absolute error 0.004 pp, 95th percentile 0.017 pp, maximum 0.080 pp (financial service charges, leaf 258). Shifting every split leaf's October m/m by plus or minus its own historical maximum error leaves leaf breadth unchanged (12m 54.038, 3m 45.467), because no split leaf is closer to 3% than the shift: the nearest are leaf 187 at 3.14% (12m, error max 0.005 pp) and leaf 317 at 2.93% (3m ann., error max 0.004 pp). So the leaf October figures are exact for practical purposes at the 3% threshold; the remaining approximation is that they inherit the build's sub-line estimates.

## 2. Time series: `C_breadth_ts.csv`
Monthly Jan 2018-Sep 2026 (BEA published) plus Oct 2026 (estimate), sub-line primary and leaf robustness columns. Reference rows `avg_2018_2019` (simple mean of the 24 months, Jan 2018-Dec 2019): **3m ann. 39.73, 12m 35.70** (sub-line); leaf 39.20, 35.25.
Published-history extremes (sub-line): 3m ann. max 76.4 (Feb 2022), min 24.2 (Nov 2020); 12m max 78.8 (Aug 2022), min 26.6 (Nov 2020). The 12m series has been above its 2018-19 average in 98.6% of months since Jan 2021 (3m: 91.3%). Last 14 months, sub-line, 12m: 58.8 (Sep 2025), 56.2, 51.8, 52.4, 55.0, 50.5, 60.6, 60.7, 59.8, 60.8, 60.4, 60.1, 57.7 (Sep 2026), 51.1 (Oct est). 3m ann.: 48.6, 38.7, 31.3, 35.0, 30.3, 53.7, 40.4, 49.8, 62.7, 52.2, 57.9, 36.5, 43.7, 43.8.

## 3. Carried-forward share of the October 12m change: `C_carried_forward.csv`
Definition: "carried forward" = the build's tier `assumed` (24 core lines, 11.23% of core weight on Oct-2025 shares; 11.4% on the build's Sep-2026 shares). Attribution per line: contribution to October breadth minus contribution to September breadth, each on that month's own start-of-window weights, which sums exactly to the -6.586 pp change; also split into rate crossings of 3% (Oct weights) and weight shift.

| Build tier | lines | core weight % | change in 12m breadth (pp) | of which crossings | lines crossing |
|---|---:|---:|---:|---:|---|
| assumed (carried forward) | 24 | 11.23 | **-0.003** | 0.000 | 0 |
| observed_needs_seasonal | 14 | 18.75 | -8.989 | -9.064 | 4 down |
| observed_published | 140 | 66.47 | +2.402 | +2.359 | 1 down, 8 up |
| blend | 5 | 3.39 | +0.005 | 0.000 | 0 |
| proxied | 1 | 0.16 | 0.000 | 0.000 | 0 |
| total | 184 | 100 | -6.586 | -6.705 | 5 down, 8 up |

**Re-derivation does not reproduce report 07's "about 1.8 of the 6.6 pp".** On this definition none of the 24 assumed lines crosses 3% between Sep and Oct, so they contribute about zero. The leaf-level version gives the same: assumed -0.016 pp of -6.588. If Oct breadth is computed with the assumed lines forced to keep their Sep side of 3%, it is 51.127, unchanged. I could not find the 1.8 in any tier, weight basis or granularity. The number 1.8 coincides with the weight of one line, Government hospitals (1.80% of core weight), which is not an assumed line; this may be a coincidence, and I did not find report 07's calculation (its code does not contain it; report 07 states it as a flag). Judgment calls for Eli or the report-07 author to say what was meant.
Why the assumed tier barely moves the 12m: its October m/m is the line's 12-month average m/m, so October 12m rate = Sep 12m rate adjusted only by (average - the m/m that drops out), and no assumed line sits close to 3%. Stress (`C_carried_forward_stress.csv`): shifting all 24 assumed lines by -1 or +1 SD of their own m/m at once moves 12m breadth only to 50.88-51.25 (base 51.13); the weight within 1 SD of the 3% flip point is 0.37% (12m) but **8.53%** for the 3m rate, where all-minus/all-plus gives 3m breadth 43.03-51.56 (base 43.75). So the carried-forward block is a soft spot for the 3m figure, not the 12m.

**Where the drop actually sits** (`C_hospital_lines.csv`, `C_flip_distance_oct.csv`): three hospital lines (184 nonprofit, 185 proprietary, 186 government; 8.78% of core weight on Oct-2025 shares) go from 3.337% 12m in Sep to 2.734% (estimate) and account for -8.72 pp of the -6.586 net change (they are in tier `observed_needs_seasonal`, one PPI series, `PCU622---622---`, no first release, with our method-B seasonal adjustment of -0.372 pp). October m/m used: 0.305%. October m/m needed to keep the 12m rate above 3%: 0.564% (+0.26 pp, about 1.1 of the line's 36-month m/m SDs of 0.227). If the three lines were just above 3%, October 12m breadth would be 59.91 (the same m/m puts the 3m rate above 3% too and gives 52.66; the 3m effect there is a by-product, not a stress test). The other down-crossings: tax preparation (301, 0.28%, 3.99 -> 2.47) and window coverings (28, 0.17%, 5.38 -> 2.54). Eight lines cross up (flowers, amusement parks, cosmetics, sporting equipment, luggage, package tours, educational books, musical instruments), +2.36 pp.

## 4. Component-sum gap: `C_sum_gap.csv`
Formulas (also in the docstring of `code/C_sum_gap.py`). Core set C, weights `w_i` = nominal shares of the window's base month rescaled over C, `g_i = p_i(t1)/p_i(t0) - 1`, `ann(x) = (1+x)^(12/k) - 1`, `R_pub` = published (Sep: U20404 line 374) or estimated (Oct: Sep line-374 index x (1 + build core m/m 0.29507)) annualized rate.
- `S_ann = sum_i w_i ann(g_i)` (the workbook's sum of contributions: each rate annualized, then weighted).
- `A_fix = ann(sum_i w_i g_i)`: fixed start-of-window shares, aggregate annualized.
- `A_chain = (prod_t (1 + L_t))^(12/k) - 1`, `L_t = sum_i s_i(t-1) pi_i(t)`: shares updated each month (chained Laspeyres).
- `A_fish = (prod_t F_t)^(12/k) - 1`, `F_t = sqrt((1+L_t)(1+Pa_t))`, `1 + Pa_t = 1/sum_i [s_i(t)/(1+pi_i(t))]`: chained monthly Fisher (geometric mean of Laspeyres and Paasche). October 2026 has no October shares, so F_Oct = 1 + L_Oct (the Paasche step is not measurable).
- Gap `G = S_ann - R_pub = (a) + (b) + (c)`: **(a)** convexity = `S_ann - A_fix`; **(b)** fixed-share vs chained Fisher = `A_fix - A_fish` = (b1) `A_fix - A_chain` (weights frozen vs updated monthly) + (b2) `A_chain - A_fish` (Laspeyres vs Fisher within the month); **(c)** residual = `A_fish - R_pub`. The identity is asserted in code to 1e-9.

Results in pp, sub-line primary (leaf in the CSV):

| Period, horizon | Published/est. rate | Sum S_ann | Gap G | (a) convexity | (b) fixed-share vs chained Fisher | (c) residual |
|---|---:|---:|---:|---:|---:|---:|
| Sep 3m ann. | 2.9025 | 3.1986 | 0.2961 | 0.1671 | 0.0333 | 0.0957 |
| Sep 12m | 3.1212 | 3.1859 | 0.0648 | 0.0000 | 0.0278 | 0.0370 |
| Oct 3m ann. (est) | 3.5508 | 3.7795 | 0.2287 | 0.1907 | 0.0327 | 0.0053 |
| Oct 12m (est) | 3.2424 | 3.3055 | 0.0630 | 0.0000 | 0.0359 | 0.0272 |

Leaf basis: Sep 3m 0.2681 (a 0.1383, b 0.0367, c 0.0931); Sep 12m 0.0627; Oct 3m 0.1980 (a 0.1619, b 0.0317, c 0.0043); Oct 12m 0.0610.

**The "0.130" and the "0.23" are not on the same basis.** The workbook's Sep sum (3.032, from `components.csv` after `analyze_baskets.fix_3m`) already annualizes the aggregate of raw contributions, so it equals my `A_fix` on the 149 leaves (3.0324, checked) and the 0.130 gap is (b) 0.037 + (c) 0.093 = 0.130 with **(a) already removed**. The October tab's sum (3.7795, `W_pce_oct_tab_lines.csv`, individually annualized, checked equal to my `S_ann`) has not been through `fix_3m`, so its 0.23 includes convexity (a) of 0.19. The like-for-like Sep figure (individually annualized, 149 leaves) is 3.1707, which equals the pipeline's retrieval-stage Sep sum in report 05 (3.171) and gives a gap of 0.268. On a common (aggregate-annualized) basis Oct 3m is 0.038 (sub-line) vs Sep 0.130. `C_sum_gap_basis_reconciliation.csv` lays the four published sums beside their gaps. So "convexity plus fixed-share" is right for the October tab, but for Sep's 0.130 convexity is zero by construction and the remainder is the fixed-share term (about 0.04) and an unexplained residual (about 0.09).

12m gap 0.063 in both months is entirely (b) + (c): 0.028 + 0.037 (Sep), 0.036 + 0.027 (Oct). The (b2) piece (Laspeyres vs Fisher within the month) is the larger part of (b) in the Sep rows and Oct 12m; in Oct 3m (b1) is 0.008 of 0.033 (b1 and b2 for every row are in the CSV).
Residual (c): covered set excludes BEA lines 145 and 333 (0.30% of PCE, no price index; they are inside BEA's core, per report 05); I did not model them, so I cannot say how much of (c) they explain. Over Oct 2023-Sep 2026 the monthly difference between the covered-set Fisher and BEA's published core m/m has mean +0.002 pp and SD 0.017 pp (`C_sum_gap_monthly_residual.csv`); the Sep 3m residual (0.0957 annualized = 0.023 over the three months) is about 1.4 monthly SDs, so it is within the usual noise. The October residual is small partly by construction: the Oct "published" aggregate is itself the build's fixed-share m/m for the last month.
Not verified: BEA's exact monthly aggregation formula (chain of monthly Fisher vs annual-weight chaining); I label (b)+(c) as "vs a chained-Fisher approximation on the covered set" rather than claim an exact BEA decomposition.

## 5. Cross-checks
- **Waller (Nov 10, `speeches/2026-11-10_Waller_economic_outlook.pdf`, read in full text):** "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September." Count basis on our core services items, 12m rate, Sep 2026: **63.1% of leaves (53 of 84)** and **58.6% of sub-lines (68 of 116)**; excluding housing leaves 64.1% / 59.1%; supercore leaves 64.1% (50 of 78). Neither count exceeds 70%. **Weighted** core-services share (start-of-window weights): **70.8% leaf**, 67.0% sub-line; latest-shares leaf 71.1%. So the 70% figure is reproduced only by a weight-based leaf share, not a count. October estimate: count 60.7% leaf (51 of 84), 56.9% sub-line; weighted 59.7% leaf, 55.9% sub-line. `C_waller_variants.csv` has all variants. I cannot tell which component list Waller used (the speech has no footnote on it); that is for Eli to read and flag if a different list (for example BEA's published table) is behind it.
- **Logan (Nov 10, `speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html`):** gives the framing (price increases concentrated in narrow shocked categories vs widespread) but no breadth statistic; his number is non-housing, non-transportation core services 3.2% over the 12 months to September. No count or weight share to compare. Our all-core 12m breadth in Sep is 57.7% (weight) / 48.9% (count, sub-line 90 of 184).
- **2025 finalists (`Previous_Finalists_copy`):** I searched the Davidson, Harvard, PACE and UCLA 2025 material and the 2023/2024 winner PDFs for breadth, diffusion, share of components. No inflation-breadth statistic appears. "Broad-based" appears for growth (Harvard 26:31) and labor-market diffusion for UCLA (about 29:11), and the 2025 finals summary lists "payroll diffusion and sector concentration" as a labor-side measure, plus a slide candidate that says to pair price breadth with weighted contributions. Breadth of this type on core PCE is not in the 2025 material I could read. (The Chicago and Penn folders contain no files, so only Davidson, Harvard, PACE, UCLA and the 2023/2024 winner PDFs were searched.)

## Limits
- October figures depend on the build's October m/m estimates (hospital lines, one PPI series, are decisive for the 12m change). BEA publishes Oct on Nov 25.
- October 2025 was a missing CPI month; the Oct 2026 12m rates of CPI-sourced lines use BEA's published (BEA-filled) Oct 2025 index as the base. I did not test the effect.
- Time series applies today's 184-line set to history; BEA's table changes at Sep 30, 2026 were not backcast line by line (the history is BEA's current-vintage indexes for those lines).
- The 3m series is noisy: 62.7 (May 2026) to 36.5 (Aug 2026) within three months.
