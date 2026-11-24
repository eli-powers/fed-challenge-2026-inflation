# Brief D: methods and backtest (Opus 5.5)

You are a research collaborator for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with Fed judges; data cutoff Nov 18, 2026). Explain technical concepts plainly. Today is 2026-11-12.

Project root: `./`. Subtask folder: `02_Research/Subtasks/04_oct_pce_build/` (called `SUB/` below). Some paths contain spaces.

## Project context
BEA releases October 2026 PCE on Nov 25, after the cutoff. We are building our own October core and headline PCE estimate bottom-up: price each PCE component from the October CPI or PPI series BEA itself names, carry forward what can't be observed, and aggregate with September spending shares. October PPI is released tomorrow, Nov 13, 8:30 AM ET. Your job today is to write the method as rerunnable code and backtest it against BEA's first-published ("first print") monthly numbers, under rules that were fixed before any results existed. The mapping and all data are already saved locally. **Do not download anything**; if something is missing, report it.

The decision this backtest feeds: if backtest MAE on monthly core is at or below 0.05 pp *and* the build beats a core-CPI-only benchmark, the estimate goes on a slide as the team's number. Otherwise it is a cross-check next to the Cleveland Fed nowcast. The rules below were locked by the student before results. **Do not change, tune or reinterpret them after seeing results.** If a rule is ambiguous or unworkable, pick the most literal reading, apply it, and list it under "Deviations and judgment calls".

## Inputs (all local)
- Mapping: `SUB/outputs/component_mapping.csv` (224 pricing lines; columns include leaf_bea_line, pricing_bea_line, is_subline, share fields, in_core, bea_seasonal_status, source_tag, tier, series_to_use, blend_inputs, needs_bea_sa_estimate, flags). Also `SUB/outputs/A_parent_leaves.csv`, `A_hierarchy.csv`, `A_stale_series.csv`, `manual_review_list.csv`, and the helper `SUB/code/A_common.py`.
- Source series, current vintage, Jan 2015 – Oct 2026 (CPI) / Sep 2026 (PPI): `SUB/outputs/component_series_history.csv`, coverage in `component_series_coverage.csv`.
- PPI as first released: `SUB/outputs/ppi_first_release.csv` (20 of 28 PPI series).
- Targets: `SUB/outputs/pce_first_prints.csv` (first-print m/m within the same vintage, Jan 2024 – Sep 2026; flags for delayed releases). Benchmarks: `SUB/outputs/core_cpi_first_prints.csv`, `SUB/outputs/cleveland_nowcast_history.csv`. Raw ALFRED files for `PCEPILFE`, `PCEPI`, `CPILFESL` are in `03_Data/Raw/`.
- BEA component data, current vintage (2026-11-10), monthly, all lines: price indexes `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json`, nominal spending `..._U20405_2026-11-10.json`.
- BEA source tables by date: `03_Data/Raw/BEA_Table244UD_PCE_price_source_data_*.xlsx` (2025-02-28, 2026-02-20, current 2026-09-30) and the line-by-line changes in `SUB/outputs/source_table_changes.csv`.
- CPI relative importance, Dec 2025: `03_Data/pipelines/Price indexes/CPI/raw/bls_cpi_relative_importance_2025_2026-11-10.xlsx`.
- Background (read first): `SUB/stress_test.md` §4–6 and both "Checkpoint outcome" sections; `SUB/report.md` (verified reports from the mapping, verification and data agents).

## Locked method

**Aggregation.** Monthly change ≈ Σ wᵢπᵢ, with wᵢ = previous-month nominal spending shares (U20405, current vintage; flag this as not real-time). Headline first, then core. Core membership comes from BEA's hierarchy (`in_core` in the mapping), with shares rescaled within core. Parent leaves are priced on their sub-lines and rolled up with within-leaf shares. Tenant rent (leaf 156): 100% CPI rent of primary residence (assumption). The two uncovered net lines (145, 333; 0.30% of PCE) are left out and weights rescaled. NPISH (leaf 342) is treated as one assumed item at leaf level.

**Tiers.** observed = an October CPI/PPI series BEA names; proxied = only line 163 (farm dwellings, on CPI owners' equivalent rent); assumed = carried forward. A line whose source series has no published value for the target month is treated as assumed **for that month** (e.g. `SEMC04`, the household-operations CPIs).

**Seasonal treatment, by BEA's Seasonal Status column.**
- `SA` → use the BLS seasonally adjusted series.
- `NSA` → use the unadjusted series as is. As a check only, run an F-test on month dummies for each and report which show seasonality.
- `SA by BEA` → method B: BEA's implied adjustment for calendar month *m* = average over past years of (BEA's SA component m/m − the source's NSA m/m) for that calendar month. For any backtest month, use prior years only. State the years used. BEA filled the missing October 2025 CPIs with the geometric mean of September and November; say how you treat October 2025 and keep it out of the October factor if the source value is missing.
- Method A (your own month-dummy or X-13-style adjustment of the NSA source) is a cross-check: run it for the `SA by BEA` PPI lines and report both. Method B is the one used in the estimate.
- State plainly that BEA re-estimates seasonal factors at each annual update, so current-vintage history embeds later information; the no-look-ahead condition is only partly met.

**Blend weights.** CPI relative importance (Dec 2025) where it exists; otherwise weights fitted on BEA's component history (constrained to be non-negative and sum to one, estimated only on data before the backtest month); equal weights as fallback. Report which was used per blend.

**Assumed items.** Carry forward each at its recent average m/m of BEA's own component index. Candidate windows: 3, 6, 12 months. Choose the window by lowest mean absolute error of the **assumed tier's total contribution** against BEA's (current-vintage) assumed-tier contribution over the rule months, not by total core MAE. The student's prior is 6 months. Disclose that the choice and the test use the same months. Portfolio management (line 268) is assumed in October 2026; report the old PPI-based value as a sensitivity only.

**Bands.** Report two: (a) bottom-up: per assumed or proxied item, weight × historical SD of its m/m, combined in quadrature, plus proxy error where available; (b) the backtest's empirical RMSE. The reported band is the wider. Add a separately stated allowance for portfolio management, whose new method has almost no history. Event check: did the two "financial services furnished without payment" lines (255, 256) shift after past policy-rate changes? If so, widen their band; don't model it. (The Fed raised rates in September 2026.) Use only local data; if you need rate-change dates you don't have, say so.

**Rates.** Extend BEA's published SA September 2026 index by the October estimate. 1m; 3m annualized = (I_Oct/I_Jul)⁴ − 1; 6m annualized = (I_Oct/I_Apr)² − 1; 12m = I_Oct/I_Oct2025 − 1. Bands scale about 4×, 2× and 1×.

## Locked backtest specification
- **Months in the decision rule:** Dec 2025 – Sep 2026 (10 months). Also run and report, but exclude from the rule: Nov 2025 (CPI affected by the shutdown), Oct 2023 and Oct 2024 (October-specific seasonal check; if inputs don't allow, say it couldn't be tested). Oct 2025 is excluded entirely.
- **Target:** BEA first print, m/m from index levels within the same ALFRED vintage. Secondary: current vintage.
- **Information set:** everything published by the day after that month's PPI release. PPI inputs at first release where `ppi_first_release.csv` has them; otherwise revised data, with the component flagged. CPI: current vintage, flagging months whose SA values were revised in February 2026 (reference months through Dec 2025). Seasonal factors and carry-forward averages: only months before the target month.
- **Methods by month:** BEA's sources as in force for that print. Dec 2025 – Jul 2026 prints: the 2026-02-20 table (portfolio management priced from its PPIs `PCU5239405239401` and `PCU5239405239402`; legal services on an unpublished CPI, so treated as assumed; software on its CPI alone; line 211 on its former CPI item). Aug – Sep 2026 prints: the current table. Report the two groups separately as well as together.
- **Benchmarks:** (1) no change: last month's first-print core m/m; (2) core CPI only: OLS of core PCE m/m on core CPI m/m, re-estimated each month on data through the prior month, expanding window from 2017, current-vintage data; (3) Cleveland Fed nowcast, last value before the PCE release. Only (2) is in the rule.
- **Metrics:** bias, MAE, RMSE, largest miss, rounding hit rate (does our estimate, rounded to one decimal, equal BEA's one-decimal first print?), and 12-month error. For core MAE also report SE = SD(|miss|)/√n over the rule months.
- **Decision rule, to apply and report plainly:**
  - Threshold leg: if MAE ± 1 SE includes 0.05 → "inconclusive at this sample size"; whole range below 0.05 → pass; whole range above → fail.
  - Benchmark leg: "beats" = lower MAE than benchmark (2) on the same months. Report the difference; a gap under 0.01 pp is within noise and must be labeled so.
  - Report MAE, its SE and n together wherever MAE appears. Note that at n = 10 the SE is itself loosely estimated.
- Estimates are carried at full precision, reported to 2 decimals.
- **Miss attribution:** for each month, split the miss by tier (observed as published; observed needing our seasonal estimate; blends; proxied; assumed) by comparing our component contributions with BEA's current-vintage ones. Label it diagnostic and revised.
- **Caveats to state:** ten months is a small sample, so give ranges, not rankings; the Sep 30, 2026 annual update changed history; component-level first prints don't exist.

## Your task
1. **Identity test (gate).** For every backtest month, feed BEA's own current-vintage component m/m through the aggregation above and compare with BEA's published current-vintage headline and core m/m. Deliverable: `outputs/identity_test.csv` and the largest gap. If any gap exceeds 0.01 pp, find the cause before going on and report it.
2. **Mapping validation.** For each pricing line with a source series: correlation and mean gap between the source m/m (treated per the seasonal rule) and BEA's component m/m over Jan 2024 – Sep 2026. Flag poor fits as a possible wrong series, missed blend or wrong source. Deliverable: `outputs/mapping_validation.csv`. Don't change the mapping; list proposed changes.
3. **Seasonal tests.** Deliverable: `outputs/seasonal_tests.csv` (per NSA or `SA by BEA` input: F-test result, method B implied adjustment for October and years used, method A value for the PPI lines).
4. **Backtest.** Deliverable: `outputs/backtest_results.csv` (per month and method: estimate, first print, current vintage, miss; plus a summary block with all metrics for our build and each benchmark, by group of months) and `outputs/backtest_attribution.csv`.
5. **Decision rule.** State the outcome of each leg in one line each, with the numbers.
6. **Build script, ready for tomorrow.** One entry point, `code/D_build.py --month YYYY-MM`, that produces the estimate, rates, bands and contributions for any month from saved inputs. Run it as a dry run for **2026-09** as if September PCE were unreleased and report the result against the first print. It must also run for 2026-10 and fail cleanly, listing the missing PPI inputs. **Do not report any October 2026 estimate.** Document in `code/README.md` the full run order for the whole subtask (A_, C_, C2_, D_ scripts) and exactly what to rerun once October PPI is in the history file.
7. **Q&A facts, as data:** the main sources of backtest error by tier, and the note that BEA revises Jul–Sep with the October release, so 3m and 6m rates can move for reasons unrelated to our estimate.

## Rules
- Every number comes from a saved script in `SUB/code/` (prefix `D_`), rerunnable from the project root with `python3`. No hand calculations. Scripts read only saved files.
- Never edit anything under `03_Data/` or `07_Archive/`, any workbook, or any file not prefixed `D_` (other than the output files named here and `code/README.md`). Don't read `AGENTS.md`.
- Report data, not policy interpretation. Separate facts, assumptions and uncertainty. Never invent numbers.
- Give every number its series ID or BEA line, reference month, vintage and seasonal basis.
- Keep an eye out for irregularities (a component whose source diverges sharply from BEA's history, a month that dominates the error; when did it last happen?). Log them under "Worth a look". Finding nothing is fine.
- If you hit a problem you can't resolve from local files, stop that part, say exactly what is missing, and finish the rest.

## Output
Save to `SUB/`: the output CSVs above (each with a header comment or companion `_meta.csv`), `notes_D.md` (raw notes as you go), `sources_D.md` (every input file, with a one-line note). Do NOT write report.md. Return the report as your final message, in this structure: Decision-rule outcome (two lines) · Findings (by task number) · Deviations and judgment calls · Worth a look (only if something stood out) · Spot-check examples (5, exact file and row) · What to verify. Concise, as a professional economist.
