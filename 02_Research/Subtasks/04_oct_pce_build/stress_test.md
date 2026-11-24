# Step 0 stress test: October 2026 PCE build

**Written:** 2026-11-11 (evening), by Claude (Fable 5.2), coordinator. **Status:** for Checkpoint A. No agents launched.

**Evidence basis.** Eli approved bounded read-only checks for Step 0 (§6 items 3, 4, 6 and the leaf-level source question). Tags: [O] opened by me, [S] search summary only. Every number below came from inline calculations, not saved scripts. They are **preliminary** and Phase 1 recomputes them with scripts.

---

## 1. Headline finding: BEA publishes a line-level price-source table

- **What it is.** BEA FAQ 521 links "Table 2.4.4U-D, Price Indexes for PCE: Source Data" (file `FAQ521-Sep26-update.xlsx`, table dated **2026-09-30**, FAQ published Oct 2, 2026) [O]. https://www.bea.gov/help/faq/521
- **Structure.** 356 rows with the same line numbers as U20404. Columns: PCE component, series code, price index source data, **seasonal status**. 232 rows carry a source.
- **Where it is.** A copy is in my scratchpad only, for inspection. It is not yet saved to `03_Data/Raw/`; that is a Phase 1 step.
- **What it settles** (each quoted from the table [O]):
  - §6 item 1, portfolio management (line 268): "Implicit: Quantity extrapolation based on CES employment and hours data. Current-dollar extrapolation based on quarterly QSS data and judgmental trend. Out months informed by market indicators and judgmental trend." The RBC report is confirmed in substance. The effective date still needs BEA's release note.
  - §6 item 2, seasonal treatment: the table states it per line. Values are `SA` (BLS-adjusted series), `NSA` (used unadjusted) and `SA by BEA` (BEA adjusts the series itself).
  - Legal services (line 299): a BEA composite of five legal-services PPIs, `SA by BEA`. This is the item missing from our 17-row PPI list.
- **Consequence.** This table replaces the 2021 Handbook as the source authority, and it removes most of §4's inference work. See §5 below for the locked decisions it touches.

---

## 2. Premise check

**The premise holds.** A CPI+PPI translation is the standard method, and component contributions do require a bottom-up build. No rival approach changes the task. Three corrections to the brief's facts:

1. **The universe is 176 matched leaves, not 178.**
   - The current Dallas workbook has 177 rows. One of them (rank 88, audio-video, photographic and information processing equipment services, BEA line 218) has no match in our mapping.
   - Headline leaf weights sum to **98.9%**. Line 218 is 0.79%. About **0.3% is still unexplained**.
   - Core weights sum to 100% only because they were rescaled across 158 leaves, so line 218 is silently missing from core.
2. **Fourteen leaves are parents in BEA's table**, with sources listed only on their sub-lines. They hold **24.6% of headline weight and 27.1% of core**.
   - The largest: other purchased meals (5.1%), tenant rent (3.5%), paramedical services (3.2%), NPISH (3.0%), financial service charges (2.7%).
   - Portfolio management (1.69% of PCE) sits inside the financial service charges leaf and is about 63% of it.
   - Financial services furnished without payment is split across three leaves: commercial banks, other depository institutions, pension funds.
3. **The existing PPI pipeline holds none of the needed series.** It has final-demand commodity indexes (`WPSFD…`). BEA's sources are industry PPIs (`PCU…`). All must be fetched.

**Preliminary source mix of the 176 leaves, by BEA's table** (share of headline weight; core in parentheses):

| BEA source type | Leaves | Headline | Core |
|---|---|---|---|
| Single CPI | 140 | 54.1% | 52.4% |
| Single PPI | 7 | 12.9% | 14.2% |
| BEA composite of CPIs/PPIs | 6 | 3.5% | 3.4% |
| Implicit (quantity extrapolation) | 2 | 1.4% | 1.5% |
| BEA input-cost index (CES, PPIs, CPIs) | 6 | 1.3% | 1.4% |
| Unpublished detail, CPI-deflated | 1 | 1.2% | 0 |
| Parent leaf, sources on sub-lines | 14 | 24.6% | 27.1% |
| Not in our mapping | — | 1.1% | — |

Seasonal status of those sources: CPI `SA` 34.4% of headline weight, CPI `NSA` 19.3%, PPI `SA by BEA` 12.9% (physicians, three hospital leaves, air transportation).

---

## 3. Feasibility against the timeline

**Feasible, and easier than the brief assumed**, because the source table replaces the Handbook parse. The real constraints:

- **Audit 1 before Nov 13 is the tightest point.** The three Nov 10 refresh audits took 3–4 rounds each. Proposal: if Audit 1 hasn't converged by PPI time, the build runs anyway and nothing is called slide-ready until both audits converge.
- **PPI-day risk.** The build should be a rerun, not new code. Proposal: on Nov 12, run the full pipeline end to end on September as if it were unreleased. This is the backtest's last month, so it costs nothing extra.
- **BLS blocks plain web requests** (the schedule page returned HTTP 403). Use the API through the existing `fetch_utils.py`.
- **Cut order.** I agree with §8, with one change: the Oct 2023–24 seasonal check matters more than the brief assumed (see failure mode 3), so I would cut headline before it. Eli decides.

**Read-only check results:**

| Check | Result |
|---|---|
| October PPI date | Nov 13, 2026, 8:30 ET [S]. BLS's own page blocked my request; reconfirm in Phase 1 |
| ALFRED, core and headline PCE first prints | In hand: `PCEPILFE`, `PCEPI`, 317 vintages each, monthly through 2026-10-29 [O] |
| ALFRED, PPI industry series | Vintages from 2015-04 through 2026-10-15 for physicians, hospitals, nursing care, home health, medical labs, air transportation, health insurance, offices of lawyers [O]. Three older financial series stop in Jan 2023 (discontinued codes) |
| ALFRED, CPI SA components | Vintages from 2011 (checked OER and used cars) [O] |
| Cleveland Fed nowcast, measures | CPI, core CPI, PCE, core PCE; m/m, y/y and quarterly [O] |
| Cleveland Fed nowcast, October 2026 (updated 11/10) | Core PCE 0.27 m/m, 3.21 y/y. PCE 0.31 m/m, 3.81 y/y [O] |
| Cleveland Fed nowcast, archive | The page's chart file holds daily nowcast histories by target month back to July 2013 [O] |
| BEA leaf-level source list | Exists (§1) [O] |

---

## 4. Failure modes the plan misses

1. **No aggregation identity test.**
   - Before pricing anything ourselves, feed BEA's *own* component m/m through Σwᵢπᵢ with previous-month shares and check that it reproduces BEA's published headline and core m/m.
   - This isolates weight, coverage and formula error from pricing error. It would have caught the 98.9% problem.
   - Proposal: make it a Phase 1 gate, run on every backtest month.
2. **The backtest needs the source table as it stood each month.**
   - The table is the Sep 30, 2026 version. Legal services reportedly changed in Jan 2026 and portfolio management on Sep 30.
   - The brief says "methods as in force that month" but names no source for them. Earlier versions of the FAQ 521 file are needed (BEA site or the Internet Archive). Unknown if they exist.
3. **Seasonal method B is thin for October, and Oct 2025 is unusable.**
   - Method B averages past Octobers. October 2025 CPI doesn't exist, so the nearest usable Octobers are 2024, 2023 and earlier.
   - BEA re-estimates its seasonal factors each annual update, so the current-vintage history already embeds later information. The "no look-ahead" rule can't be fully met; it must be flagged, not claimed.
   - The `SA by BEA` PPI items are 12.9% of headline directly, more inside parent leaves. They are the likely main source of 1-month error. Employ America's January miss was attributed to the same thing [S].
4. **Portfolio management is unobservable and untestable.**
   - "Out months informed by market indicators and judgmental trend" means there is no October input we can replicate. Tier: **assumed**.
   - It was priced from a PPI in every backtest month, so the backtest says nothing about the new method. Its band needs separate treatment (history since Sep 30 is one month).
5. **The band in locked decision 9 leaves out observed-tier error.**
   - It covers assumed and proxied items only. Observed items also miss, through scope differences, composites and seasonal adjustment.
   - The quadrature sum also assumes item errors are independent.
6. **The window choice and the decision rule use the same ten months.**
   - Choosing the carry-forward window by lowest backtest MAE, then judging the build by that same MAE, flatters the result slightly.
7. **Ten months can't separate 0.045 from 0.055.**
   - The decision threshold is 0.05 pp. With n ≈ 10 the sampling noise in MAE is roughly ±0.01–0.015 (a back-of-envelope figure that assumes normal, independent misses; the rule in §6 uses the measured SE instead). A near-threshold result is not a clear pass or fail.
8. **Component-level first prints don't exist in our files.**
   - The pipeline holds three U20404 vintages (Sep 27, Oct 1, Nov 10). Miss attribution by tier can only use current-vintage components. The brief already labels this diagnostic; it should also say revised.
9. **Negative-weight and netted lines.**
   - NPISH is gross output less sales receipts; insurance lines are net of claims. Their "price" is not a simple index of one source. These are candidates for the assumed tier regardless of what sources are listed.

**Are the brief's mitigations adequate?** For the Handbook's limits, yes, and now largely moot. For seasonal adjustment and the band, no: see proposals in §5.

---

## 5. Locked decisions: where I disagree or see gaps (Eli decides)

| # | Decision | Issue | Proposed change |
|---|---|---|---|
| 2 | 178 leaves | 176 matched; 14 are parents (24.6% of weight); line 218 missing | Keep Dallas leaves as the **reporting** unit. Price at BEA's lowest source-table line inside parent leaves, then roll up. Add line 218 and trace the last 0.3% |
| 3 | Handbook is the authority; concordance second | A newer, line-level BEA table exists | Authority order: Table 2.4.4U-D (Sep 30, 2026) → Handbook for composite detail → BLS concordance as tiebreaker for CPI item choice only |
| 8 | Test C first, then B | BEA states seasonal status per line | Follow BEA's column: `NSA` → use unadjusted; `SA` → BLS adjusted series; `SA by BEA` → method B. Keep C as a check on `NSA` lines only. Keep A as the cross-check, and pre-commit to reporting it for the `SA by BEA` PPIs |
| 9 | Band from assumed items in quadrature | Omits observed-tier error; assumes independence | Report two bands: the bottom-up one as locked, and the backtest's empirical error (RMSE). Use the wider. Add a separate allowance for portfolio management |
| 10 | MAE ≤ 0.05 and beats core-CPI-only | Under-specified (see §6) | Lock the open choices in §6 at Checkpoint A |

No disagreement with decisions 1, 4, 5, 6, 7 or 11. One addition to decision 5: the identity test (failure mode 1).

---

## 6. Open specification choices to lock before results

Each has my default. Nothing has been run, so nothing here is informed by results.

| Choice | Default |
|---|---|
| Metric for "beats" | Lower MAE on core m/m, unrounded, in pp |
| Target | BEA first print, m/m from index levels within the same ALFRED vintage |
| Months in the rule | Dec 2025 – Sep 2026 (10 months). Nov 2025 reported but excluded. Oct 2023 and Oct 2024 reported but excluded |
| Core-CPI-only benchmark | OLS of core PCE m/m on core CPI m/m, re-estimated each month on data through the prior month (expanding window from 2017), current-vintage data |
| Margin for "beats" | Any lower MAE counts. Report the difference and state that gaps under 0.01 pp are within noise |
| Near-threshold result | Compute SE = SD(\|miss\|) / √n over the months in the rule. If MAE ± 1 SE includes 0.05, the result is "inconclusive at this sample size". Whole range below 0.05 = pass on the threshold leg; whole range above = fail. Default placement when inconclusive: cross-check next to the Cleveland nowcast; Eli can override at Checkpoint C. Report MAE, its SE and the month count together wherever MAE is quoted. Caveat: at n = 10 the SE is itself loosely estimated, so one large miss widens the range |
| Carry-forward window | Chosen on the assumed tier's own contribution error, not on total core MAE. Disclose that the same months are used |
| Rounding | Estimates carried at full precision; reported to 2 decimals; hit rate judged at 1 decimal |
| Other benchmarks | Cleveland nowcast (last value before the PCE release) and no-change: reported, not part of the rule |

---

## 7. Inputs inventory

**NEW** marks sources that §6a doesn't list.

| Input | Status | Note |
|---|---|---|
| **NEW** BEA Table 2.4.4U-D, Sep 30, 2026 | To fetch properly (scratch copy inspected) | Source authority |
| **NEW** Earlier versions of Table 2.4.4U-D | Unknown if they exist | Methods in force in each backtest month |
| **NEW** Sub-line weights and prices inside the 14 parent leaves | In hand (U20404/U20405, Nov 10) | Roll-up within leaves |
| **NEW** Line 218 and the remaining 0.3% of headline weight | In hand, untraced | Coverage |
| **NEW** PPI industry series (`PCU…`) for every PPI source and composite | To fetch | None are in the pipeline |
| **NEW** CES and ECI inputs to BEA's input-cost indexes | To fetch if those lines are priced, else assumed | 6+ leaves and NPISH |
| **NEW** Cleveland nowcast daily archive (chart file, 2013–) | To fetch | Benchmark history; confirmed to exist |
| **NEW** Component-level first prints | Not available | Limits miss attribution |
| Newer BEA method articles (SCB) | To fetch | Lower priority now |
| BEA release and technical notes, incl. Sep 30, 2026 | To fetch | Effective dates; what BEA extrapolates at first print |
| BLS PCE–CPI concordance | To fetch | Now a tiebreaker only |
| CPI relative importance, Dec 2025 | In hand (`bls_cpi_relative_importance_2025`) | Confirm it is the Dec 2025 table |
| CPI stratum series, SA and NSA | Partly in hand: 323 series, through Oct 2026 | Check against the new mapping |
| ALFRED: `PCEPILFE`, `PCEPI` | To fetch; coverage confirmed | Backtest target |
| ALFRED: PPI inputs, CPI SA components | To fetch; coverage confirmed for a sample | Three old financial codes end Jan 2023 |
| BEA U20404/U20405, current vintage | In hand; September is the latest month [O] | — |
| October 2025 core PCE index | In hand: 127.165 [O] | Matches the brief |
| CES employment and hours, portfolio-management industry | To fetch | Not usable as an October price input (failure mode 4) |
| October PPI | Nov 13 | — |
| Public professional translations | Unknown | Record what's public; note paywalls |

---

## 8. Proposed agent split

Four agents. The first three run in parallel; the fourth waits for the mapping and data.

| Agent | Model | Answers |
|---|---|---|
| **A. Source mapping** | Opus 5.5 | For every Dallas leaf, and every sub-line inside the 14 parent leaves: BEA's source text → BLS series IDs, source tag, tier, seasonal status, blend weights, flags. Conflicts with the Handbook and concordance listed. Output: `component_mapping.csv`, manual-review list |
| **B. Verification and documents** | Sonnet 5.5 | BEA release notes and effective dates (portfolio management, legal services); earlier versions of the source table; what BEA extrapolates at first print; PPI date from BLS directly; public professional translations |
| **C. Data pulls** | Sonnet 5.5 | Save raw: source table, concordance, ALFRED first prints, Cleveland archive now; CPI/PPI series histories (SA and NSA, plus first-release PPI) once A's series list exists |
| **D. Methods and backtest** | Opus 5.5 | Identity test; seasonal treatment; carry-forward rule and bands; backtest with the §6 choices; the September dry run. All scripted in `code/` |

**Brief outlines** (full briefs written from the skill template after Checkpoint A):
- **A:** inputs are the source table, `dallas_component_mapping.csv`, `bls_cu_item`/`bls_cu_series`, PPI series lists. Rules: never force a match; name-to-series matches must be verified against the series list; tier `proxied` only where BEA's method is quoted.
- **B:** five numbered questions, each answered with a quote and URL, or "not found (unconfirmed)".
- **C:** a fixed list of series and files, dated raw saves, the BLS partial-failure warning, no edits to pipeline raw files.
- **D:** locked decisions 5–10 as amended at Checkpoint A, the §6 table verbatim, output file specs from brief §9.

**What I verify myself:** the identity test, ten mapping rows against the source table, the first-print targets against ALFRED, and the backtest summary metrics recomputed from `backtest_results.csv`.

**Codex read of the plan:** not requested. The changes in §5 follow from a newly found primary source and aren't contested method points.

---

## Checkpoint A outcome (Eli, 2026-11-11)

- **§5 changes to locked decisions 2, 3, 8, 9 and 10: accepted.** These amend the brief.
- **§6 specification choices: locked as written**, with the near-threshold row replaced by the measured-SE rule (proposed in a side chat, confirmed by Eli).
- **Cut order:** not decided; Eli says time isn't a constraint for now. Nothing is cut.
- **Agent split (§8): approved.** A, B and C launch now; D after the mapping and data.
- **Codex read of the plan:** skipped.

---

## Checkpoint B outcome (Eli, 2026-11-11)

- **Mapping approved** (`outputs/component_mapping.csv`).
- **Seven defaults accepted:** tenant rent sub-lines 100% CPI rent; unstated blend weights from CPI relative importance, else fitted on BEA history, else equal; portfolio management assumed in October with the old PPI as a sensitivity only; the uncovered 0.30% left out and weights rescaled; "data available at the time" = everything published by the day after that month's PPI release; old sources for Dec 2025 – Jul 2026 and current sources for Aug – Sep 2026, reported separately; the observed share always reported with its three-way split.
- **Core-flag error in the existing pipeline:** separate task, brief at `02_Research/Subtasks/05_fix_core_flag/brief.md`.

---

## Checkpoint C outcome (Eli, 2026-11-12)

- **Decision rule, main run:** core MAE 0.0405, SE 0.0086, n = 10 (range 0.0318–0.0491); core-CPI-only benchmark 0.0874. Both legs pass under the locked rule.
- **How it is recorded:** "pass under the locked rule, margin within implementation noise." Slide placement is decided at Checkpoint D, with the October number and band in view.
- **Portfolio-management PPIs:** try to recover first-release values from archived BLS reports, time-boxed.
- **Net travel lines:** the locked exclusion stays for the decision rule; the 0.010 pp mean identity residual is disclosed.
- **Rate-change check on the bank-services lines (255, 256):** coordinator pulls the dates and runs it; it can only widen a band.

---

## Decision-rule basis (Eli, 2026-11-13)

- **The decision rule rests on the first-release variant** (portfolio-management PPIs at first release; `outputs/D2_backtest_variant_first_release_pm.csv`): core MAE 0.0423, SE 0.0081, n = 10, MAE ± 1 SE = 0.0342–0.0505. Threshold leg: **inconclusive at this sample size**. Benchmark leg: beats core CPI alone (0.0874).
- Under the locked rule the default placement is therefore a **cross-check next to the Cleveland Fed nowcast**. Eli can override at Checkpoint D.
- **Band (Eli, Nov 13):** set from the variant's backtest RMSE, ±0.0489 pp on core m/m and ±0.0452 on headline (wider than the bottom-up band), plus 0.008 pp for portfolio management. `code/D_build.py` reads it from `outputs/D2_backtest_variant_first_release_pm.csv`.
- Chosen after results were seen (Nov 12 – 13), on the grounds that the variant better follows the locked information-set rule ("PPI inputs at first release where available").

---

## 9. Sources opened in Step 0

- BEA FAQ 521 and Table 2.4.4U-D (Sep 30, 2026) [O]. https://www.bea.gov/help/faq/521
- Cleveland Fed inflation nowcasting page and its monthly chart file [O]. https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting
- FRED/ALFRED vintage-date queries for 19 series [O].
- BLS PPI schedule [S]: the page blocked my request. https://www.bls.gov/schedule/news_release/ppi.htm
- Local: `dallas_component_mapping.csv`, `components.csv`, `requested_component_tags.csv`, `pce_ppi_priced_components.csv`, U20404/U20405 (Nov 10 vintage), CPI and PPI pipeline raw files.
