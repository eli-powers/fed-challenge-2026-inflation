# Q7. The hospital base effect (Agent B, 2026-11-15)

**Question.** Is the +0.89% Oct 2025 m/m in the hospital PCE leaves (184–186) a real measured price move, or a fill or imputation? This decides whether the "base effect" line can be said.

**Answer: real and measured.** The October 2025 PPI for hospitals (PCU622---622---) was collected and published by BLS. It was not imputed. BEA's documented shutdown imputation covers CPI only, and these leaves are priced from the PPI. The October jump comes from a once-a-year Medicare inpatient price reset that happens every October. The 2025 reset was unusually large. Data: `B_q7_hospital.csv`, `B_q7_hospital_octobers.csv`. Script: `code/B_q7_hospital.py`, with raw data fetched by `code/B_q7_fetch_bls.py`.

## Evidence

**1. BLS published Oct 2025 PPI, late, with November.**
- BLS's revised release-date page says it would not publish a separate October news release but was "collecting October reference period data on a delay." It planned to "publish October data with the November 2025 PPI news release on January 14, 2026." [O] https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm (read with WebFetch; direct download returned 403).
- The same page says CPI is different: BLS "could not collect October 2025 reference period survey data … is unable to retroactively collect these data." [O]
- The PPI Detailed Report for November 2025 (saved: `03_Data/Raw/BLS_PPI_detailed_report_2025-11_retrieved_2026-11-12.pdf`, p. 6) has a box headed "Effect of Federal Government Shutdown on PPI Data" [O]:
  - October price-update requests, "asking for information as of the October 14 pricing date, were sent to PPI survey respondents on November 19."
  - "The response rates for the October and November data reflected in this report are within the normal range, and no modifications to PPI methodology or procedures were necessary."
- **ALFRED first-release vintage** (FRED id PCU622622; `03_Data/Raw/ALFRED_PCU622622_all_vintages_from2024-11_2026-11-11.json`) [O]:
  - The Oct 2025 value first appears on **2026-01-14** at 248.009, against Sep 2025 at 244.536 in that vintage: **+1.420% NSA** at first release.
  - It was revised to 247.988 on 2026-01-30 and to 247.985 from 2026-02-27, giving **+1.410%** on the current vintage.
- **BLS API, retrieved 2026-11-15** (`03_Data/Raw/BLS_PPI_hospitals_2026-11-15/`) [O]: the Oct 2025 observation carries **no footnote code**. Oct 2026 carries "P" (preliminary), so the API does flag status where it applies.
- The detailed report's table shows the hospitals industry index (622) values. Sep→Oct 2025: 244.536 → 248.009. Oct→Nov: 248.522. 1-month changes: −0.1 (Aug–Sep), +1.4 (Sep–Oct), +0.2 (Oct–Nov). [O]

**2. BEA did not impute the hospital leaves.**
- The BEA PIO release for Oct and Nov 2025 (released Jan 22, 2026; saved `03_Data/Raw/BEA_PIO_october-and-november-2025_page_retrieved_2026-11-11.html`), Technical Notes, "October Prices" [O]: *"To replace the missing CPIs, BEA derived seasonally adjusted price indexes for October using the geometric mean of the September and November CPIs."* Non-seasonally adjusted (NSA) values were rebuilt from the imputed SA values using October 2024 seasonal factors. The note names CPIs only and says nothing about PPIs.
- The "Additional information" page (`BEA_PIO_additional_information_retrieved_2026-11-11.html`) has no shutdown or imputation text. [O]
- BEA's source for leaves 184–186 is PPI hospitals (`04_oct_pce_build/outputs/component_mapping.csv`, tier `observed_needs_seasonal`). PPIs had a published Oct 2025 value, so the CPI geometric-mean fill does not apply. This is an inference from BEA's note covering only CPIs, not an explicit BEA statement about PPIs.

**3. What drove the move: the October Medicare reset.**
- PPI commodity "Medicare patients: hospital inpatient care, general medical and surgical hospitals" (WPU5121010111, NSA) [O]:
  - Flat Jul–Sep 2025 at 125.099.
  - **+5.96%** in Oct 2025.
  - Flat again in Nov.
- The detailed report agrees: Sep→Oct +6.0. Hospital inpatient care overall (general medical and surgical) was +2.2. Hospital outpatient care was +0.1 NSA; API WPU511104 gives 159.974 → 160.056. [O]
- Medicare inpatient rises every October, the start of the federal fiscal year (`B_q7_hospital_octobers.csv`, 2014–2026):
  - 2016–2024 Octobers ran +0.8% to +4.3%.
  - Oct 2025 (+5.96%) is the largest in the series.
  - Oct 2026 (prelim) is +2.09%.
- The FY2026 Medicare inpatient payment rule (IPPS) set a **2.6%** rate update effective Oct 1, 2025 [S] (Becker's / AAMC search snippets, not opened). The PPI Medicare component rose much more than that headline update. **Unverified why.** Candidates include DSH/uncompensated-care changes and DRG-weight effects. Not settled.

## Numbers (m/m %, Oct 2025 vs neighbours and history)

| Series | SA | Jul 25 | Aug | Sep | **Oct 25** | Nov | Dec | Jan 26 | Avg Nov 25–Sep 26 | 2018–25 mean / SD | z | pctile (2018–25, n=96) | Oct-only mean 2018–25 | z vs Octobers |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PPI hospitals PCU622---622--- | NSA | 0.087 | 0.414 | −0.148 | **1.410** | 0.221 | −0.403 | 0.645 | 0.168 | 0.236 / 0.357 | 3.29 | 98.4 (rank 2; max Jan 2022 1.432) | 0.715 | 1.56 |
| BEA leaf 184 (185, 186 identical to 0.001) | SA (BEA) | 0.064 | 0.407 | 0.082 | **0.893** | 0.464 | −0.134 | 0.096 | 0.218 | 0.239 / 0.239 | 2.73 | 96.4 (rank 4; max Jan 2022 1.063) | 0.353 | 1.40 |
| PPI Medicare inpatient WPU5121010111 | NSA | 0.0 | 0.0 | 0.0 | **5.961** | 0.0 | 0.054 | 0.0 | 0.005 | 0.266 / 1.013 | 5.62 | 99.5 (max) | 3.219 | 1.91 |

- BEA leaf 184 October m/m, SA (vintage 2026-11-10), by year:
  - 2017: 0.881
  - 2018: 0.224
  - 2019: 0.718
  - 2020: 0.184
  - 2021: −0.144
  - 2022: 0.008
  - 2023: 0.769
  - 2024: 0.171
  - 2025: **0.893**
- BEA's seasonally adjusted series still shows a large October move in 2017, 2019, 2023 and 2025. Oct 2025 is the largest October in the BEA series since at least 2017, but about the same as 2017.
- PPI 622, NSA 12m: Sep 2026 **3.290%**; Oct 2026 **2.543%** (Oct 2026 PPI is preliminary, released 2026-11-13).
- UMD's October build uses an SA m/m of 0.305% for these leaves. A 12m rate above 3% would have needed 0.564% (`09_slide1_research/outputs/C_hospital_lines.csv`).

## Answers

- **Measured, not filled.**
  - BLS collected Oct 2025 PPI late but normally: the Oct 14 pricing date was kept, response rates were normal, and no method change was made.
  - BLS published it on Jan 14, 2026, with no status code.
  - BEA's shutdown fill applies to CPIs, not to this PPI.
  - It is **not** a two-month change booked in one month: Sep (−0.15%) and Nov (+0.22%) were each published separately.
- **The "base effect" line can be said.** The precise version: "the October 2025 hospital price jump, mainly the annual Medicare inpatient reset, drops out of the 12-month window."
- **Caveat for Q&A.** October hospital jumps recur every year, so this is partly a calendar pattern, not a one-off. What was unusual in 2025 was the size: the Medicare component rose +6.0% against a typical 2–4%. The Oct 2026 reset is smaller (+2.1% prelim).
- **What would settle the remaining question** (why +6.0% against a 2.6% rate update):
  - BLS PPI health-care staff, or the PPI hospital methodology / FAQ page.
  - The detailed DRG-level Medicare inpatient indexes for Oct 2025.
