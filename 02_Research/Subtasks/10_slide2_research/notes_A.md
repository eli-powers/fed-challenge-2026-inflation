# Notes, agent A (Nov 15, 2026)

## Method and checks
- Engine: 09_slide1_research/code/C_common.py imported read-only via code/A_common.py. Reproduction asserted to 0.01: core leaf 12m Sep 60.626, Oct 54.038; 3m Sep 44.814, Oct 45.467 (A_check_tags.py).
- Tag mapping: all 149 core leaves map one-to-one (leaf = line in component_id). Group counts and weights reproduce tag_summary.csv (4/30/42/73; 2.04/11.11/18.26/68.60%). tag_final re-derived from the rules in tag_rules.py with zero differences (E_P75 = 0.03468).
- Q2 sum of leaf contributions S matches 09 C_sum_gap.csv leaf rows: 12m Sep 3.1839 vs published 3.1212 (resid -0.063); Oct est 3.3035 vs 3.2424 (-0.061); 3m Sep 3.1707 vs 2.9025 (-0.268); Oct 3.7488 vs 3.5508 (-0.198). 3m residual is mostly annualization convexity (0.138 Sep, 0.162 Oct) per C_sum_gap.
- Energy spot check: independent recomputation (different algebra: zero energy columns of A, Leontief inverse) reproduces all 149 item energy shares within 5e-6; cutoff 0.03468 identical; no leaf changes side. It shares the documented design (bridge mapping, margin treatment, energy block) with tag_exposures.py, so it verifies arithmetic and data handling, not the design.
- Oct 12m breadth change -6.588 pp = untagged -8.801 + energy +1.163 + tariff +1.044 + AI +0.006. Rate crossings -6.705, weight shift +0.117. Hospital leaves 184-186 (all untagged): -8.721 pp contribution change (flip -8.780, weight shift +0.059); untagged ex hospitals -0.080.

## Tariff exemption (see outputs/A_q1_tariff_exemption.md)
- Key finding beyond the brief: the 2025 reciprocal tariffs (IEEPA) were struck down on Feb 20, 2026 (SCOTUS), replaced by Section 122 (Feb 24 to Jul 24), then Section 301 forced-labor tariffs (from Jul 24). Electronics (8471, 8517.13, 8542) are on the exemption lists of all three.
- Docs saved in 03_Data/Raw/tariff_exemption_2026-11-15/.

## Q2 findings
- Bowman: "roughly one-fourth" each for tariffs, energy, AI, and a fourth for persistence; method undisclosed (5 footnotes, none on method).
- Ours (12m Sep, method a): energy 29%, tariff -0.1%, AI 18%, untagged 53%. Method b: 23/8/13/56. Method c: 60/19/21/0.4.
- Tariff group's weighted 12m rate is 1.99% (Sep): at or below 2%, so under method a it owes ~0. New light trucks (1.9% weight) at 0.5% 12m pull it down.
- AI group is ~2% weight with an 12.5% group rate, 88% of its contribution from leaf 50 (software).

## Worth a look
1. Tariff group ran at 1.99% 12m (Sep), which is not above target; Bowman gives tariffs a quarter. Not obviously reconcilable with item tags; her method is undisclosed.
2. AI group result is one leaf: software (leaf 50) 18.5% 12m Sep but 3m ann. +0.4% Sep and -9.1% Oct est.; phones -12.7% 12m (quality adjustment). Check how BEA prices leaf 50.
3. Energy-tagged and untagged-ex-hospital breadth differ by about 9 to 15 pp (Sep 67.0 vs 57.9; Oct est 73.3 vs 57.8 at 12m); energy-tagged and all-untagged 2018-19 12m averages were 33.7 and 41.1.
4. Energy-tagged 12m breadth was already 72% in Sep 2025 and 58-77% through 2026, i.e. already high before 2026 (2018-19 average 33.7%); the untagged group was also 63-64% in Sep 2025.
5. Nursing homes (1.46% of core) sit 0.001 pp above the energy cutoff.
