# Notes D: methods and backtest (Opus 5.5, 2026-11-12)

Raw working notes. All numbers come from `code/D_*.py`; outputs in `outputs/`. Units: percent m/m, SA, misses in pp.

## Run log
1. `D_identity_test.py` first run: locked-formula gaps up to 0.024 pp in rule months (core, Jul 2026), 0.045 pp overall (core, Apr 2025). Above the 0.01 gate, so investigated before going on.
   - Fisher formula alone (variant F) barely helps (max 0.043 overall).
   - Adding the two excluded net lines back through their gross components (+146 −149 +334 −338; variant C) cuts the max to 0.011 headline / 0.005 core; Fisher with that coverage (CF) to 0.004 / 0.0014.
   - **Cause:** the excluded lines 145 (net expenditures abroad) and 333 (net foreign travel) are small nets (0.30% of PCE) of large gross flows (334 = 1.18%, 338 = 0.94% of PCE) whose prices move differently; the net contributes up to ~0.04 pp. Residual after that is the Laspeyres-type vs Fisher formula (~+0.003 pp mean).
   - The locked method (exclude, rescale) was kept. This is a built-in error of the method, present in every month, reported not fixed.
2. `D_mapping_validation.py`: almost all CPI lines match BEA to within 0.001 pp/month (corr ≈ 1.000). Flags below.
3. `D_seasonal_tests.py`: 97 input series tested, 35 seasonal at 5%.
4. `D_backtest.py` first run → core MAE 0.0405. **Bug found:** the blend-weight fit (SLSQP) stalled at the starting point for line 178 (0.5/0.5, objective ~1e-4 below tolerance). First fix (scale to percent, ftol 1e-12) made line 299's fit for Aug 2026 *fail* and fall back to equal weights, giving core MAE 0.0413 ± 0.0087 (upper end 0.05002: inconclusive). Replaced SLSQP with exact constrained NNLS (scipy `nnls`, sum-to-one by a heavily weighted extra row). Final: core MAE 0.0405 ± 0.0086. These are numerical fixes to the locked rule ("non-negative, sum to one"), not changes to it. **Disclosed because the threshold outcome flips on this margin.**
5. Flag-parsing bug in `D_backtest.py` (wrong series listed as "PPI revised") fixed; numbers unaffected.
6. Coordinator-added sensitivity (`D_sensitivity_no_fr_ppi.py`).

## Judgment calls (all set before seeing backtest results unless marked)
- Source table for Nov 2025, Oct 2023, Oct 2024 prints: 2025-02-28 version (fish, dental SA; day care, child care NSA). Legal CPI exists for Oct 2023 (observed), missing Oct 2024 on (assumed).
- Old-table line 211: `CUUR0000SERF01` (C2's closest match). Old-table 305 priced like 299 (CPI legal services).
- Mapping tiers kept for stale-series lines (130, 54, 220, 221, 330–332, 328): assumed in every month including Oct 2023.
- Sub-line shares normalised to one within each parent leaf (max deviation is tiny); 158 dropped, 157 = 100%.
- Bimonthly CPI (`SEMC04`, lines 180/181): target value present but t−1 missing → 2-month geometric change if the gap ≤ 2 months; otherwise assumed. Observed in Jun and Aug 2026 (and Oct 2026 when built); assumed in the other rule months.
- Method B: years = all same calendar months before the target in BEA's U20404 (starts 2017); for lines 50, 299, 305 (source changed at the Sep 2026 update, revisions back to Jan 2021) only 2021+. Oct 2025 kept out of the October factor where a CPI input was missing; PPIs have Oct 2025 values and are used.
- Blend weights: RI for 87, 95 (from the mapping). Fitted (12-month log changes, NNLS, sum to one, data through t−1) for 50, 178, 285 (smartphones has no RI), 299, 305, and old 268. Old-268 fit on 2017–2020 only (BEA's current-vintage 268 is the new implicit method from 2021).
- Method A = −(mean October NSA m/m − mean of all months), years before the target.
- Carry-forward window chosen on the **core** assumed-tier contribution (rule is on core): 12 months (MAE 0.0190 vs 0.0213 for 6, 0.0250 for 3). Same months used for selection and test.
- Band (a): item SD over the 36 months before the target (BEA current vintage); proxy error for 163 replaces its SD; portfolio management kept out of (a) and stated separately.
- Benchmark (2) for Nov 2025: core CPI Oct 2025 filled with the geometric mean (prediction only; Oct/Nov 2025 dropped from the regression sample).
- Oct 2023 first print computed from the raw ALFRED file (pce_first_prints.csv starts Jan 2024); 12-month error not computable (no Oct 2022 in the file). Cleveland Oct 2023/2024 from the long chart file, last value before the first-print vintage date.
- F-test sample: all available months Feb 2015 – Sep 2026, including 2020.
- Validation flag rule: corr < 0.5, |mean gap| > 0.05, or MAE gap > 0.5 pp/month.

## Mapping validation flags (no mapping changes made; proposals)
- 299/305 legal (current composite): corr 0.33, mean gap +0.32 pp/month. BEA's current-vintage history is not well tracked by the five PPIs at fitted weights; e.g. Jan 2026 BEA +1.33 vs composite +4.88. Proposal: check whether BEA's back-cast composite applies to all of 2021–2026, or obtain BEA's fixed weights.
- 207 air transportation: corr 0.81 but MAE gap 1.26 pp/month (1.06% of PCE). BEA's SA series is much smoother than PPI + additive method B. Proposal: test method A or a multiplicative factor (not done; locked).
- 50 software (current): mean gap +0.17 pp/month; old-table CPI alone vs current BEA: +0.32 (expected: different method).
- 268 old two-PPI vs current BEA: corr 0.00 (expected: BEA history is the new implicit method).
- 301 tax prep, 216 spectator sports: noisy (MAE gap 2.7, 3.1); "judgmental trend" lines per BEA.
- 195/196 leasing: mean gap −0.12, only 21 months of source data.
- 163 farm dwellings (proxied, OER): corr −0.07; weight 0.14%.
- 69 educational books: mean gap −0.05 (tiny weight).

## Other observations
- Main-run attribution (core, rule months, mean |diff|): blend 0.032 (old months include the PM method change, an artifact of comparing with current vintage), SA-by-BEA 0.024, assumed 0.019, observed-as-published 0.019, identity 0.010, revision (current − first) 0.032.
- Revised-PPI sensitivity: core MAE 0.031 (vs 0.040 with first-release PPI) — first-release PPI is noisier than BEA's eventual inputs but is what BEA used at first print.
- Line 180 BEA m/m in Nov 2025 is exactly 0.000 (BEA flat while SEMC04 unpublished?).
- Policy-rate change dates are not saved locally (only SEP FEDTAR* projections); the 255/256 event check could not be done.
