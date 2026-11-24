Status: Audit 1 (mapping and backtest) converged R2, 2026-11-12. Audit 2 (October build) converged R1, 2026-11-13. Decision basis and band: first-release variant (Eli, Nov 13). Checkpoint D pending.

# October 2026 PCE build: reports

Sections appear in the order agents returned: C, B, A, C2, D, a coordinator addendum, then post-audit corrections and additions. Agent E's full report is in `E_report_pending.md`.

---

# Agent C: backtest targets and benchmarks (Sonnet 5.5, returned 2026-11-11)

All six tasks completed; BLS did not block the requests. Every number is computed by a saved script in `code/` (prefix `C_`). Raw files are in `03_Data/Raw/`, dated 2026-11-11.

Method note: the first-release vintage is the earliest ALFRED vintage carrying a value. The first-print m/m uses both index levels as they stood in that single vintage. Release dates are ALFRED vintage dates, not checked against the BEA or BLS calendars; they match Cleveland's release dates in every month.

## Findings

**1. First-print PCE** (`PCEPILFE` core, `PCEPI` headline; SA, 2017=100; Jan 2024 – Sep 2026, 33 months). Table: `outputs/pce_first_prints.csv`.
- Delayed or combined releases (flagged in the file): Sep 2025 released 2025-12-05; Oct and Nov 2025 released together 2026-01-22; Dec 2025 on 2026-02-20; Jan 2026 on 2026-03-13; Feb 2026 on 2026-04-09. Mar 2026 (2026-04-30) is back to a normal lag of 20–31 days.
- Mean absolute revision, first print to current vintage, m/m: core 0.039 pp, headline 0.038 pp.
- Largest revisions: Apr 2025 core 0.1159 → 0.3037 (+0.188 pp), headline 0.1002 → 0.2336. Jul 2026 core 0.2455 → 0.1377 (−0.108 pp).
- Latest core first print, Sep 2026: 0.3165 m/m, 3.1212% y/y, vintage 2026-10-29.

**2. Cross-check.** All 90 month-and-series levels match the pipeline `U20404` file within 0.0006. Sep 2026: 130.902 core, 132.257 headline. Oct 2025 core: 127.165. Detail: `outputs/C_crosscheck_alfred_vs_bea.csv`.

**3. Core CPI** (`CPILFESL`, SA, 1982–84=100). Table: `outputs/core_cpi_first_prints.csv`, Feb 2017 – Oct 2026.
- Oct 2025 was never published; ALFRED shows missing from vintage 2025-12-18 on. BLS [O]: "BLS did not collect survey data for October 2025 because of a lapse in appropriations."
- Nov 2025: first print 331.068 (vintage 2025-12-18), revised to 331.043. Its m/m isn't computable. Sep→Nov 2025 two-month change at first print: 0.1591%.
- Dec 2025 first-print m/m: 0.2392. Oct 2026 first print: level 339.900, m/m 0.2963 (vintage 2026-11-10); y/y not computable.
- Mean absolute revision, first print to current, 2024 on: 0.0135 pp (n=32), max 0.038. Part of it is the annual February seasonal-factor revision.

**4. Cleveland Fed nowcast archive.** Raw month, year and quarter JSONs saved. Table: `outputs/cleveland_nowcast_history.csv`; long form in `outputs/C_cleveland_nowcast_long_mm.csv`.
- The chart files carry dates as MM/DD with no year; the year is inferred from the target month and date order.
- Cleveland's "actual" core and headline PCE m/m equal our first prints in all 33 months, and PCE release dates match in all 33.
- Nowcast error, last nowcast before the PCE release minus actual, 33 months:

| | Mean | MAE | Min | Max |
|---|---|---|---|---|
| Core PCE | −0.015 | 0.065 | −0.191 (Jun 2024) | +0.148 (Nov 2024) |
| Headline PCE | −0.007 | 0.057 | −0.143 (Feb 2025) | +0.143 (Nov 2024) |

- Core PCE nowcast MAE using the day-after-CPI value: 0.067 pp.
- Current nowcasts (chart stamp 2026-11-10): Oct 2026 core PCE 0.2669 m/m, 3.2134 y/y; PCE 0.3051 m/m, 3.8114 y/y. Nov 2026 core PCE 0.2640 m/m; PCE 0.2129 m/m.

**5. BLS PCE–CPI concordance.** Fetched (HTTP 200) with the contact User-Agent. 15 HTML tables, 404 data rows, 315 unique ELIs, 167 unique PCE codes. "Last Modified Date: April 5, 2024". CSV: `03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv`.

**6. Series-list freshness.** No series added or dropped against the Sep 27 copies (cu.item 400, cu.series 8104, pc.series 4510, wp.series 5312). New dated copies in `03_Data/Raw/`.

## Worth a look (agent)
1. Cleveland shows Oct 2026 y/y "actuals" for CPI (3.8479%) and core CPI (2.5767%). BLS publishes no Oct 2026 12-month change because Oct 2025 is missing.
2. Largest core PCE nowcast misses: Jun 2024 (−0.19), Feb 2025 (−0.17), Nov 2024 (+0.148), Feb 2026 (−0.135). All four months Dec 2025 – Mar 2026 were negative (−0.122, −0.093, −0.135, −0.063).
3. Apr 2025 core PCE first print 0.1159, later 0.3037: the largest revision in the window.
4. Headline PCE: Mar 2026 first print 0.6642 m/m; Jun 2026 −0.1087. Not investigated.
5. Two BLS series end dates moved backward in the latest lists (`WPU14440101`, `PCU3365103365106`). Cause unknown.

## What to verify (agent)
- Release dates rest on ALFRED vintage dates.
- The one-decimal figure is rounded from 3-decimal index levels; BEA's published rounded figure can differ by 0.1 occasionally.
- The Cleveland year inference is in `C_cleveland_nowcast_history.py`. The nowcast on CPI day appears to already include that day's CPI.
- How far back the 2026-09-30 annual update revised levels was not mapped (e.g. Oct 2025 core 127.243 → 127.165).
- One extra raw file was saved: the BLS CPI release page.

## Coordinator review (Agent C)

**Verified, and how.**
- First prints: I re-queried ALFRED myself for six vintage/month pairs and recomputed m/m. All match the agent's table: core Sep 2026 0.3165 (vintage 2026-10-29), Jan 2024 0.4156 (2024-02-29), Oct 2025 0.2079 and Nov 2025 0.1604 (both 2026-01-22), Apr 2025 0.1159 (2025-05-30); headline Mar 2026 0.6642 (2026-04-30); core CPI Oct 2026 0.2963 (2026-11-10).
- Cleveland error statistics: recomputed from `cleveland_nowcast_history.csv`. Core PCE, 33 months: mean −0.0145, MAE 0.0648, min −0.1906, max +0.1478. Matches.
- Cross-check file: 90 rows, all status OK.
- Current Oct 2026 nowcasts match what I read on the Cleveland page on Nov 11 (0.27 / 3.21 core; 0.31 / 3.81 headline).

**Added by me (not in the agent's report).** Cleveland core PCE nowcast over the decision-rule window, Dec 2025 – Sep 2026 (n=10), last value before the PCE release, against first print: bias −0.040, MAE 0.068, SE of MAE 0.013, largest absolute miss 0.135 (Feb 2026).

**Corrected.** Nothing.

**Not checked.** The Cleveland year-inference logic line by line; the concordance CSV against the HTML; release dates against agency calendars.

**Worth a look (coordinator).**
- Core PCE y/y at first print fell from 3.34% (Jul 2026) to 3.01% (Aug 2026) while the first-print m/m was 0.25 in both months. The Aug release was the Sep 30 annual update, so the drop is revision to history, not the monthly change.
- In Dec 2025 – Feb 2026, PCE releases ran 40–51 days after month-end. In those months the next month's CPI was already out before the PCE release. "Data available at the time" needs a fixed definition for the backtest: I propose information as of the day after that month's PPI release.

---

# Agent B: verification and documents (Sonnet 5.5, returned 2026-11-11)

Files: `notes_B.md`, `sources_B.md`, `outputs/source_table_changes.csv`, `code/B_*.py`. Raw pages and files are in `03_Data/Raw/`. Tags: [O] opened, [S] snippet only, [2] secondary. Fuller quotes are in `notes_B.md`.

## Findings

**Q1. Portfolio management method change [O].**
- BEA's statement: Mataloni, "The 2026 Annual Update of the National Economic Accounts," *Survey of Current Business*, Sep 30, 2026. https://apps.bea.gov/scb/issues/2026/09-september/0926-nea-annual-update.htm
  - "BEA improved the deflation methodology for consumer spending on portfolio management and investment advice services... The quantity of portfolio management services will be derived using a BLS Current Employment Statistics (CES)-based quantity extrapolator..."
  - "A BLS producer price index (PPI)... was used for deflation." Under the new method "the price index will be derived implicitly."
- Effective with the annual update released Sep 30, 2026. The Aug 2026 release says: "The revisions for estimates of personal income and outlays begin with January 2021."
- BEA doesn't say month by month that the new method applies to Apr–Aug 2026; the agent infers it from that sentence.
- For the backtest: first prints for Dec 2025 – Jul 2026 were built under the old PPI method. The Aug 2026 print (Sep 30) and Sep 2026 print (Oct 29) were built under the new method.
- Table 2.4.4U-D row 268 changed from "PPI Portfolio Management and Investment advice | NSA" (Feb 20, 2026 version) to the implicit quantity extrapolation, "SA by BEA" (Sep 30, 2026 version).

**Q2. Legal services [O]. BEA's account differs from Employ America's.**
- BEA FAQ 1486: "In January 2026 the unpublished CPI showed an unprecedented increase that could not be substantiated by any other data. As a result, BEA made a downward adjustment to the PCE price index using changes in the BLS producer price index (PPI) for legal services to inform the adjustment." The legal-services CPI "is no longer published by BLS. However, BLS continues to provide BEA with the unpublished CPI." https://www.bea.gov/help/faq/1486
- Monthly technical notes: the Mar 2026 release says the index was "adjusted for the months of January and March. No adjustment was made for February." The Apr and May releases add no adjustment for those months. The Jan, Jun, Jul, Aug and Sep releases have no legal-services note.
- Permanent change, Sep 30, 2026: "BEA replaced the consumer price index (CPI) for legal services with an improved composite price index based on PPIs for legal services." The CPI "was last published for the month of September 2024."
- Professional association dues follow the legal-services deflator. The same update replaced the computer software and accessories deflator with a composite of the CPI and two PPIs.
- Missing Oct 2025 CPI (BEA's Oct+Nov 2025 release, Jan 22, 2026): "BEA derived seasonally adjusted price indexes for October using the geometric mean of the September and November CPIs."
- A BLS primary statement on the legal-services CPI: not found (unconfirmed).

**Q3. Earlier versions of Table 2.4.4U-D [O].**

| Table date | URL | Notes |
|---|---|---|
| 2025-02-28 | https://www.bea.gov/sites/default/files/2023-06/faq521.xlsx | Still live; identical Wayback copies |
| 2026-02-20 | https://www.bea.gov/sites/default/files/2026-02/FAQ521-Feb26-update.xlsx | Retrieved from the Internet Archive (snapshot 20260503063910). The live URL now serves a Sep 30 file |
| 2026-09-30 | https://www.bea.gov/sites/default/files/2026-10/FAQ521-Sep26-update.xlsx | Current |

- Changed lines, Feb 20 → Sep 30 (9 lines; `outputs/source_table_changes.csv`): 50 computer software (CPI NSA → composite, SA by BEA); 180 and 181 (wording only); 211 membership clubs (different CPI item, NSA → SA); 255 commercial banks (wording only); 268 portfolio management; 299 legal services; 305 professional association dues; 340 medical expenditures of foreigners (SA → NSA).
- 2025-02-28 → 2026-02-20 (6 lines): fish and seafood SA → NSA; dental SA → NSA; spectator sports and tax preparation add "& judgmental trend"; day care and child care NSA → SA.
- Not found: the date of the Feb 2025 → Feb 2026 file swap.

**Q4. What BEA sets by judgment at first print.** A "key source data and assumptions" file for Personal Income and Outlays: not found (unconfirmed). Checked the Jan–Sep 2026 release pages and the May–Sep release PDFs.
- The legal-services notes are the only documented first-print price adjustments in the 2026 releases.
- Table lines that name judgment or implicit extrapolation: farm dwellings rental value (out months on CPI owners' equivalent rent); spectator sports; commercial banks; other depository institutions and regulated investment companies; portfolio management; tax preparation.

**Q5. Newer method documentation [O].** "Updated Summary of NIPA Methodologies," *Survey of Current Business*, Sep 30, 2026. https://apps.bea.gov/scb/issues/2026/09-september/0926-nipa-methodologies.htm
- BEA's current Handbook Chapter 5 is headed "(Updated: December 2024)", not December 2021.
- Portfolio management and legal services passages match the table changes above. Other PCE price passages were not compared.

**Q6. October PPI release [O].** BLS schedule page: "October 2026 Nov. 13, 2026 08:30 AM". The row prints no time zone. https://www.bls.gov/schedule/news_release/ppi.htm

**Q7. Public translations.**
- **Employ America Core-Cast** [O]: m/m, y/y and component detail around each CPI, PPI and PCE release. The October 2026 posts (Nov 5 and Nov 10) are subscriber-only. Post-PCE posts are public: Aug 2026 core +25 bp vs a 28 bp nowcast; Sep 2026 core +32 bp vs a 34 bp nowcast.
- **Chicago Fed Letter 529, "Flash PCE"** (Sep 2026) [O, page only]: headline, core and three core subcomponents; stated RMSE about 0.59 pp annualized. No data download found. PDF and appendix not opened.
- **Cleveland Fed nowcast** [O]: a model nowcast, not a translation.
- **Oxford Economics** [O, one article]: Jun 2026 summary public; no October article found.

## Worth a look (agent)
- BEA adjusted legal services in both Jan and Mar 2026, not January alone as Employ America wrote.
- BEA overwrote the file at the Feb 2026 URL in place.
- Row 211 (membership clubs) changed CPI item between Feb and Sep 2026 without a mention in the BEA articles the agent read.
- Several lines rely on judgmental trend in out months.

## What to verify (agent)
- Whether the new portfolio method applies to Apr–Aug 2026 monthly data (inferred).
- Which table version was in force for the Dec 2025 print.
- The Chicago Fed PDF and appendix; FAQ 521 files older than June 2023.

## Coordinator review (Agent B)

**Verified, and how.** I fetched the live pages myself and searched the text.
- Portfolio management and legal-services passages in the SCB annual-update article: both quotes present as given.
- FAQ 1486, "In January 2026 the unpublished CPI showed an unprecedented increase...": present as quoted.
- March 2026 release technical note, "adjusted for the months of January and March. No adjustment was made for February.": present.
- August 2026 release, "revisions... begin with January 2021": present.
- PPI schedule (agent's saved page): "October 2026 Nov. 13, 2026 08:30 AM".
- Table versions: I read rows 50, 211, 268 and 299 in all three saved files. The 2025-02-28 and 2026-02-20 versions show CPI NSA for software and legal services and PPI NSA for portfolio management; the current file shows the new sources. Matches.
- Handbook vintage: the BEA chapter file the agent retrieved is headed "(Updated: December 2024)". Our pipeline copy (the whole handbook) has Chapter 5 headed "(Updated: December 2021)". Both statements are true of their own file; the pipeline copy is the older one.

**Corrected.** Nothing.

**Not checked.** The table-date cell in each version; the Internet Archive provenance of the Feb 20 file; the Employ America figures; the Apr and May release notes.

**Resolved from other work.** The agent couldn't tell which Cleveland October value is core PCE. Agent C's archive file settles it: core PCE 0.2669 m/m, headline 0.3051.

**Worth a look (coordinator).**
- **Only two backtest months were built under BEA's current methods** (Aug and Sep 2026). In Dec 2025 – Jul 2026, portfolio management was PPI-priced, legal services used an unpublished CPI (adjusted by BEA in Jan and Mar), and computer software used its CPI alone.
- **Legal services was unobservable before Sep 30, 2026**: the CPI BEA used has been unpublished since Sep 2024. In backtest months it belongs in the assumed tier. From October it is an observed PPI composite.
- **BEA's own fill for Oct 2025** was the geometric mean of the Sep and Nov CPIs. That fixes how to treat October 2025 in the seasonal estimates.

---

# Agent A: source mapping (Opus 5.5, returned 2026-11-11)

Scripts, run from the project root in this order: `code/A_build_mapping.py`, then `code/A_handbook_conflicts.py`. Shares are September 2026 nominal spending shares (U20405, vintage 2026-11-10). The authority is BEA Table 2.4.4U-D ("T244"), dated Sep 30, 2026.

## Findings

**1. Coverage.** The 176 matched leaves sum to 98.906% of PCE. Adding line 218 (0.792%) gives 99.698%. The remaining 0.302% is two net lines with no price index in U20404: line 145, net expenditures abroad by U.S. residents (0.058%), and line 333, net foreign travel (0.244%). Both are core, so covered core is 99.66% of BEA's core line (374).

**2. Parent leaves.** 14 leaves have no source on their own row: 13, 17, 156, 176, 187, 194, 218, 241, 258, 272, 275, 281, 317, 342. (Against the coordinator's draft list: adds 218, drops 279, which is priced as one line.)
- Lines 157 and 158 (sub-lines of 156, tenant rent) are not published in U20405, so their within-leaf weights are unknown. Proposed default: 157 = 1.00, 158 = 0.00, flagged as our assumption. Basis: line 159, priced by CPI rent alone, has the same value as 156.
- Sub-line shares: `outputs/A_parent_leaves.csv`. Portfolio management (268) is 63% of leaf 258. In NPISH (342), gross output is +372% of the leaf and sales receipts −277%.

**3. Series IDs.** 224 pricing lines: 163 leaves priced on their own row plus 61 sub-lines.
- Match method: 151 exact, 46 manual, 27 with no series. Every PPI match counts as manual because BLS titles use an "Industry-Product" form.
- 8 blends. BEA states weights for none of them. Proposed: CPI relative importance (Dec 2025) for lines 87 and 95; equal weights or a regression on history for lines 285, 328, 50, 178, 299 and 305 (our assumption).
- 277 distinct series to fetch: 110 CPI SA, 141 CPI NSA, 26 PPI. No PPI has a current SA version.

**4. Tiers, share of total PCE** (covered total 99.70%).
- With NPISH netted as assumed: observed 89.4%, assumed 10.1%, proxied 0.14% (line 163, farm dwellings, whose out months use CPI owners' equivalent rent).
- Share of covered core: observed 88.4%, assumed 11.4%, proxied 0.15%.
- By source: CPI 67.9%, PPI 17.5%, blend 4.7%, imputed 9.7%.
- Largest assumed lines: NPISH net (2.96%), portfolio management (1.69%), commercial banks (1.25%), other depository institutions and regulated investment companies (1.19%), social assistance (1.15%), life insurance (0.59%).

**5. Seasonal status (BEA's labels), share of PCE.** SA 39.6%, NSA 30.2%, "SA by BEA" 22.9%, mixed or other 7.1%.
- 17 lines (18.7%) need our own seasonal-adjustment estimate. Hospital PPIs are 7.85%, physicians 3.97%.
- 52 lines (19.3%) use the NSA CPI as BEA directs even though BLS publishes an SA series.

**6. Conflicts with the Handbook** (`outputs/A_conflicts.csv`; 10 lines, 4.7% of PCE; T244 wins): portfolio management; used vehicle margins (lines 15, 19: Handbook PPI, T244 CPI used cars and trucks); software; legal services and professional dues; video streaming (renamed CPI item); school lunches and employee food (lines 240, 247, 248: T244 says CPI full service meals).

## Worth a look (agent)
- **`components.csv` mislabels core for 17 leaves.** Its core weight is 0.9089 against BEA's 0.8888. Details: `outputs/A_incore_check.csv`. Not edited.
- **Some CPIs BEA names are no longer published** (0.55% of PCE): new motorcycles (ended 2000), film and photographic supplies (2016), photographer fees and photo processing (2020), and household operations items whose last real values are 2024. Tagged assumed. BEA may use unpublished BLS detail; unverified. Details: `outputs/A_stale_series.csv`.
- **Line 268 has live PPIs** (`PCU5239405239401`, `PCU5239405239402`), which the old method used. A candidate proxy, but T244 doesn't support it.
- **NPISH leverage.** An error in the gross-output price is amplified about 3.7 times in the NPISH net price.

## What to verify (agent)
- "Land-line telephone services" → `SEED04` (lines 283, 284); "Technical and business school" → `SEEB04` (line 297).
- The NAICS level BEA uses for the physicians, home health and nursing PPIs.
- Blend weights, the 157/158 split, and the mapping of NPISH receipt lines to household-spending lines (agent's judgment).

## Coordinator review (Agent A)

**Verified, and how.**
- Coverage: I recomputed shares from U20405. Line 145 = 0.058%, line 333 = 0.244%, line 218 = 0.792%, BEA core line 374 = 88.88% of PCE. Matches.
- Tier and source shares: recomputed from `component_mapping.csv`. They match once leaf 156 (3.53%) is added back; its two sub-lines carry blank weights in the file because U20405 doesn't publish them.
- Source text and seasonal status: I compared 20 mapping rows (10 random, 10 chosen heavy or unusual lines) with the BEA table. 19 match exactly. The one difference is line 356 (NPISH receipts), where the table has no seasonal status and the file has a blank.
- Core mislabel in the existing pipeline: confirmed. `retrieve_bea_baskets.py` assigns core by a name rule. Against BEA's hierarchy it tags 13 food and alcohol leaves (3.77% of PCE) as core, and tobacco and two food-supplied lines (0.66%) as non-core. Line 218 is missing altogether. The script has its own line-rule check for this (around line 510).

**Corrected.** Nothing in the agent's files.

**Not checked.** The 46 manual name matches one by one; the Handbook conflict list; the NPISH receipts mapping.

**Added by me: the observed tier, split by how much estimation it needs** (share of total PCE; covered core in parentheses).

| Group | Headline | Core |
|---|---|---|
| Observed, BLS series used as published | 68.2% | 66.1% |
| Observed, but needs our seasonal-adjustment estimate | 18.7% | 21.1% |
| Observed blend with weights BEA doesn't state | 2.6% | 1.2% |
| Proxied | 0.1% | 0.2% |
| Assumed | 10.1% | 11.4% |

**Worth a look (coordinator).**
- The existing pipeline's core flag is wrong for 16 leaves. Anything built from `components.csv` rows labeled "PCE core" inherits it. This build takes core membership from BEA's hierarchy instead.
- "Observed" at 89% overstates how much is read straight off BLS data: about a fifth of weight depends on a seasonal adjustment BEA doesn't publish.

---

# Agent C2: component data pulls, round 2 (Sonnet 5.5, returned 2026-11-11)

Scripts: `code/C2_*.py`. Raw: `03_Data/Raw/bls_api_components_2015_2026_batch1..6_2026-11-11.json` and ALFRED files.

## Findings

**1. BLS history.** 284 series requested (277 from `series_to_fetch.csv` plus 7 used under BEA's older methods), Jan 2015 – Oct 2026. `outputs/component_series_history.csv`, 39,318 rows. Blank means BLS returned "-". Footnotes seen: X (2025 funding lapse), P (preliminary).
- Extras: portfolio-management PPIs `PCU5239405239401` and `PCU5239405239402`; CPI legal services `SEGD01` (SA, NSA); CPI hospital and related services `SEMD` (SA, NSA); `CUSR0000SEEE02`, which does not exist.
- Old source not identified cleanly: line 211's former item ("Club dues and fees for participant sports and group exercises"); closest is `CUUR0000SERF01`, the agent's judgment.

**2. Coverage** (`outputs/component_series_coverage.csv`, `outputs/C2_no_oct2026.csv`).
- October 2026 present for 246 of 256 CPI series. Missing: household operations `SEHP` (last value 2024-10), `SEHP01` (2024-11), `SEHP04` (2024-07); new motorcycles `SS45031` (no data); film `SS61021` (2016-10); photographer fees `SS62051` (2020-11); photo processing `SS62052` (2020-12); legal services `SEGD01` SA and NSA (2024-09); `CUSR0000SEEE02` (doesn't exist).
- All 28 PPI series end Sep 2026.
- October 2025: 240 CPI series-rows blank with footnote X; 11 have values (`SEEC01`, `SETA02`, `SETA03`, `SS45011`, `SS45021` in SA and NSA, plus `SEED03` NSA). All PPI series have an October 2025 value.
- Other gaps since 2017: `SEMC04` (services by other medical professionals; values only in some months since mid-2025), `SETA03` (38 months, 2020-04 to 2025-03), `SS68023` (11), `SEEA` (8), `SS62032` (8); smartphones `SSEE041` starts 2019-12.

**3. PPI as first released** (`outputs/ppi_first_release.csv`, 440 rows). ALFRED carries 20 of the 28 PPI series. Not found (unconfirmed absence): `PCU5132105132107`, five `PCU523150…` brokerage and dealer series, and both portfolio-management PPIs.
- Mean absolute gap between first-print and current m/m across all rows: 0.256 pp. Largest by series (mean / max): `PCU5182105182105` 1.03 / 4.58; `PCU5613805613802` 0.80 / 2.56; `PCU621512621512` 0.47 / 3.99; `PCU524114524114` 0.38 / 4.22; `PCU4811114811111` 0.38 / 1.13. Smallest: physicians 0.05 / 0.31.

**4. CPI SA revisions** (`outputs/C2_cpi_sa_revisions_summary.csv`). In a sample of ten large SA series, seven had reference months 2024-12 through 2025-12 revised in the 2026-02-13 vintage; no month from 2026-01 on was revised. Mean absolute m/m revision: OER 0.008 pp; gasoline 0.452 (max 2.48); others 0.09–0.16.

## Worth a look (agent)
- Household-operations CPIs have been sparse since 2024 (BEA lines 328, 330–332).
- `SEMC04` (BEA lines 176, 180, 181; about 1.9% of headline) has values only in some months since mid-2025.
- Eleven CPI series-rows have October 2025 values despite the non-collection.

## Coordinator review (Agent C2)

**Verified, and how.**
- History file against an independent pull: the pipeline's own Nov 10 BLS downloads overlap on 172 series and 20,010 observations. Zero mismatches.
- PPI first release: I queried ALFRED for hospitals (`PCU622622`) at vintage 2026-09-10. July 251.94, August 253.51, first-print m/m +0.62%, as in the agent's table. The current m/m is +0.22%.

**Not checked.** A fresh BLS API pull (the API returned HTTP 503 on three tries on Nov 12); the ALFRED ID search for the 8 missing PPIs; the SA-revision table.

**Worth a look (coordinator).**
- **Hospital PPI revisions are large relative to our target.** Hospitals are 7.85% of PCE. A 0.40 pp revision to the August m/m is worth about 0.03 pp on headline PCE. BEA's first print used the first-release PPI, so the backtest must too.
- **BLS API availability is a build-day risk.** It returned 503 on the morning of Nov 12.
- `SEMC04` moves from "observed" toward "assumed" in months where BLS publishes no value; the backtest should apply that month by month.

---

# Agent D: methods and backtest (Opus 5.5, returned 2026-11-12)

> **Superseded in part (2026-11-12, after Codex audit round 1).** The numbers in this section are the agent's original run. A correction to the legal-services history changed them slightly. The current numbers are in "Post-audit corrections and additions" at the end of this file. Original outputs are kept in `outputs/archive_pre_R1_fix/`.

Scripts: `code/D_*.py`; run order in `code/README.md`. Notes: `notes_D.md`, `sources_D.md`. All "first print" targets are BEA first-release m/m from ALFRED, computed within one vintage. Rule months: Dec 2025 – Sep 2026 (n = 10).

## Decision-rule outcome (agent)
- **Threshold leg: pass, by 0.0009 pp.** Core MAE 0.0405, SE 0.0086, n = 10. MAE ± 1 SE = 0.0318–0.0491, wholly below 0.05.
- **Benchmark leg: beats.** Core-CPI-only OLS has MAE 0.0874 (SE 0.0159, n = 10). Difference −0.047 pp.
- The threshold outcome depends on implementation details at this margin: an intermediate run with a failed weight fit gave 0.0413 ± 0.0087 (top end 0.05002, which reads inconclusive); a 6-month carry-forward window gives 0.0415 ± 0.0081; a 3-month window 0.0483 ± 0.0073.

## Findings

**1. Identity test: the gate failed; cause found; locked method kept.** (`outputs/identity_test.csv`)
- Largest gap in rule months: 0.024 pp (core, Jul 2026). Largest overall: 0.045 pp (core, Apr 2025). 19 of 34 months exceed 0.01.
- Cause: the two excluded net lines (145 and 333, 0.30% of PCE) are small nets of large gross flows (line 334 is 1.18% of PCE, line 338 0.94%) whose prices diverge.
- Adding them back through their gross components cuts the largest gap to 0.011 headline and 0.005 core; with the Fisher formula as well, 0.004 and 0.0014.

**2. Mapping validation.** (`outputs/mapping_validation.csv`) Nearly all CPI lines reproduce BEA's monthly change (correlation ≈ 1.000, gap below 0.001 pp/month). Flagged, with no mapping changes made: legal services 299/305 composite (correlation 0.33, mean gap +0.32 pp/month); air transportation 207 (mean absolute gap 1.26 pp/month on 1.06% of PCE); software 50 (mean gap +0.17); tax preparation 301 and spectator sports 216 (noisy); leasing 195/196 (−0.12); farm dwellings 163 (correlation −0.07); educational books 69 (−0.05).

**3. Seasonal tests.** (`outputs/seasonal_tests.csv`) 35 of 97 input series show seasonality at 5%, including all hospital, home-health, nursing, health-insurance, legal and air PPIs. October adjustments for Oct 2026, method B (used) / method A (cross-check), in pp: hospitals −0.372 / −0.508; nursing homes −0.672 / −0.591; home health −0.307 / −0.493; health insurance +0.212 / +0.237; physicians +0.015 / −0.014; legal services −0.393 / −0.421; air transportation −5.96 / −5.32. Method B uses Octobers 2017–2025 (2021–2025 for lines 50, 299, 305 in this original run; corrected below to 2024–2025 for legal services and dues). CPI inputs missing in Oct 2025 are filled with the geometric mean of September and November and kept out of the October factor; that is BEA's stated procedure for seasonally adjusted prices only, and our approximation for unadjusted series (see corrections). The no-look-ahead condition is only partly met, because BEA re-estimates factors each annual update.

**4. Backtest.** (`outputs/backtest_results.csv`, `backtest_attribution.csv`, `backtest_lines.csv`)
- Carry-forward window chosen: 12 months (assumed-tier core contribution MAE 0.0190, vs 0.0213 for 6 and 0.0250 for 3). Selection and test use the same months.

| Measure | Bias | MAE (SE, n) | RMSE | Largest miss | 1-decimal hit rate | 12-month error MAE |
|---|---|---|---|---|---|---|
| Core | +0.020 (7 of 10 positive) | 0.0405 (0.0086, 10) | 0.048 | +0.093 (Sep 2026) | 0.4 | 0.042 |
| Headline | — | 0.0386 (0.0073, 10) | 0.044 | — | 0.5 | — |

| Core, by group | MAE (n) |
|---|---|
| Old-table months, Dec 2025 – Jul 2026 | 0.0327 (8) |
| Current-table months, Aug – Sep 2026 | 0.0714 (2); misses +0.050, +0.093 |

| Core benchmark, rule months | MAE (SE) |
|---|---|
| No change | 0.0788 (0.0221) |
| Core-CPI OLS | 0.0874 (0.0159); bias −0.071 |
| Cleveland nowcast | 0.0677 (0.0131) |

- Excluded months, core misses: Nov 2025 +0.031; Oct 2023 +0.086; Oct 2024 +0.060.
- With revised PPI in place of first release, core MAE would be 0.031 (sensitivity).
- Bands (`outputs/backtest_bands.csv`): bottom-up 0.025–0.031 pp core; backtest RMSE 0.048 core, 0.044 headline (the wider, so the reported band); portfolio-management allowance 0.008 pp on core.
- Event check on lines 255/256: not done; no policy-rate change dates are saved locally.
- Portfolio management on the old PPI blend instead of carry-forward: −0.040 pp on core in Aug 2026, −0.002 in Sep 2026.

**6. Build script.** `code/D_build.py --month YYYY-MM`.
- Dry run for 2026-09: core 0.409 vs first print 0.317 (miss +0.093); headline 0.576 vs 0.491. Core 3m annualized 3.18 vs 2.90; 6m 3.06 vs 2.92; 12m 3.19 vs 3.12.
- 2026-10: exits cleanly, listing 35 missing PPI input rows (27 series). No October estimate reported.
- Tomorrow: set the date to 2026-11-13 in `C2_fetch_bls.py` and in the file pattern of `C2_build_history_coverage.py`, run both, then `D_build.py --month 2026-10`. Do not rerun `D_backtest.py` for the decision.

**7. Q&A facts.** Mean absolute contribution to the core miss, rule months, by source (diagnostic, against revised data): blends 0.032; revision (current minus first print) 0.032; PPI lines needing our seasonal estimate 0.024; assumed 0.019; observed as published 0.019; identity residual 0.010. Lines recurring in the top misses: 207 (air), 268 (portfolio management), 50 (software), 301 (tax preparation), 342 (NPISH), 180 (other medical professionals).

## Sensitivity: PPIs without first-release history
(`outputs/backtest_sensitivity_no_first_release_ppi.csv`) The 8 series treated as missing, so their lines fall to assumed. Same window, same months.

| | Main MAE (SE, n) | Sensitivity MAE (SE, n) | Difference |
|---|---|---|---|
| Core | 0.0405 (0.0086, 10) | 0.0597 (0.0145, 10) | +0.019 |
| Headline | 0.0386 (0.0073, 10) | 0.0546 (0.0124, 10) | +0.016 |

Most of the difference comes from portfolio management in the old-table months.

## Deviations and judgment calls (agent)
- **Blend-weight fit bug, fixed after seeing results.** The optimizer stalled at equal weights for line 178; a first fix made the Aug 2026 legal-services fit fail, giving the "inconclusive" 0.0413 ± 0.0087. The final run uses exact non-negative least squares with weights summing to one. The rule is unchanged.
- Identity gate exceeded; locked exclusion of lines 145 and 333 kept.
- Nov 2025, Oct 2023 and Oct 2024 use the 2025-02-28 source table.
- Blend weights fitted on 12-month log changes through the month before target; old line 268 fitted on 2017–2020.
- `SEMC04` (lines 180/181): where the target month exists and the previous month is missing, the 2-month geometric change is used; so observed in Jun, Aug and Oct 2026, assumed otherwise.
- Weights and CPI are current vintage. Seven PPIs lacked first release in rule months and were priced from revised data, flagged.

## Worth a look (agent)
- Both October checks miss high: core +0.086 (2023), +0.060 (2024).
- The two months built with BEA's current methods show the largest rule-month misses (+0.050, +0.093).
- Air transportation: BEA's October adjustment averages −5.96 pp; in Sep 2026 the line alone added +0.028 pp to the core miss.
- Legal-services composite fits BEA's revised history poorly (Jan 2026: BEA +1.33, composite +4.88).

## Coordinator review (Agent D)

**Verified, and how.**
- Targets: the ten core first prints in `backtest_results.csv` equal my ALFRED-verified first prints exactly.
- Core metrics recomputed from the monthly rows: MAE 0.0405, SE 0.0086, range 0.0318–0.0491, bias +0.0199, RMSE 0.048, largest miss +0.0929 (Sep 2026). Matches.
- Benchmark (2) rebuilt independently from the BEA core index and core CPI: for Dec 2025, a = 0.0535, b = 0.6827, n = 104, prediction 0.2125; rule-window MAE 0.0874, SE 0.0159. Identical.
- Benchmark (3): 0.0677 / 0.0131 equals what I computed from the Cleveland file on Nov 11.
- Identity test: largest gaps in the file match the report (locked formula 0.042 core overall; full coverage 0.005; full coverage with Fisher 0.0014).
- Window choice file and the sensitivity file match the report.
- The blend-weight fix: I read `D_common.blend_weights`. It is non-negative least squares with a sum-to-one constraint, on data up to the month before target. That is a faithful implementation of the locked rule, not a change to it.

**Corrected.** Nothing.

**Not checked.** Method B line by line; the old-table switching logic; the attribution; the 2026-09 dry run beyond matching the backtest row.

**Worth a look (coordinator).**
- **The pass is not a clean pre-registered pass.** A bug was fixed after results were visible, and the outcome moved from inconclusive (top of range 0.05002) to pass (0.0491). The fix is correct, but the margin (0.0009 pp) is smaller than the effect of any single implementation choice reported.
- **The sensitivity exceeded the 0.005 pp trigger** agreed in the side chat (+0.019 on core MAE). Under it, MAE ± 1 SE is 0.045–0.074, which reads inconclusive. The main run prices seven PPIs from revised data in the old-table months, which is not real time; the revised-PPI sensitivity (0.031) shows revised data flatters the result.
- **Misses lean positive where it matters for October:** bias +0.020; both months under BEA's current methods missed high; both past Octobers missed high.
- **The identity gate failed** on a decision locked at Checkpoint B (leaving out the two net travel lines). Mean absolute identity residual in rule months: 0.010 pp.

---

# Coordinator addendum: rate-change check on the bank-services lines (2026-11-12)

Checkpoint C item 4. Script: `code/K_event_check_rates.py`. Output: `outputs/K_event_check_rates.csv`. Inputs: BEA U20404 lines 255 and 256 (SA price index, m/m %, vintage 2026-11-10); FRED `DFEDTARU` (federal funds target, upper limit; `03_Data/Raw/FRED_DFEDTARU_2026-11-12.json`). Window: Jan 2017 – Sep 2026.

| Line | Months of or after a target change (n = 49): SD of m/m | All other months (n = 68): SD of m/m | Correlation of m/m with the size of the change, same month |
|---|---|---|---|
| 255 Commercial banks | 1.31 | 0.92 | 0.52 |
| 256 Other depository institutions and regulated investment companies | 0.48 | 0.51 | 0.62 |

- The target was raised on 2026-09-17, so October 2026 is a "month after a change".
- Line 255 is more variable around rate changes; line 256 is not. Both move in the direction of the change in the same month.
- Effect on the band: line 255 is 1.25% of PCE (about 1.4% of core). Using its event-month SD (1.31) in place of the 36-month SD used in the bottom-up band (0.97) adds about 0.005 pp to that item's term before quadrature. The reported band is the backtest RMSE (0.048 pp core), which is wider than the bottom-up band either way, so the reported band does not change.
- Per the locked rule, this is recorded as a band note and not modeled.

---

# Post-audit corrections and additions (coordinator, 2026-11-12)

Made after Codex audit round 1 (`06_Audits/04_oct_pce_build/R1_codex.md`) and therefore **after backtest results had been seen**. Pre-correction outputs and code: `outputs/archive_pre_R1_fix/`.

## 1. Correction: legal services and professional dues history (Codex R1-F01, accepted)

- **The error.** The backtest engine treated BEA's new legal-services composite (lines 299 and 305) as starting in January 2021. BEA's preview article says the composite "will replace the consumer price index (CPI) for legal services beginning in 2024" (Mataloni, *Survey of Current Business*, Jun 24, 2026; saved as `03_Data/Raw/BEA_SCB_2026-06_annual_update_preview_retrieved_2026-11-11.html`). Agent B's notes had this; it was dropped in the synthesis.
- **The fix** (`code/D_common.py`, `NEW_METHOD_START`): lines 299 and 305 start 2024-01. Two sample boundaries now follow from the start date, for all three new-method lines: monthly-change samples (seasonal methods A and B) begin one month after it, and 12-month-change samples (blend-weight fits) begin twelve months after it, so no observation straddles the method change. Line 50 (software) keeps 2021-01, which is the start of the revision window; BEA states no start date for that composite (unverified).
- **Consequences, applied literally under the locked rules:**
  - Legal-services blend weights: fewer than 24 usable observations exist (19–21), so the locked fallback applies: **equal weights** across the five PPIs.
  - Legal-services seasonal factor (method B): Octobers 2024 and 2025 only. October 2026 adjustment **−0.035 pp** (was −0.393).
  - Software: fit sample now starts 2022-01; October adjustment −0.044 pp.
- Rerun: `D_seasonal_tests.py`, `D_mapping_validation.py`, `D_backtest.py`, `D_sensitivity_no_fr_ppi.py`, `D_build.py --month 2026-09`, `D2_variant_first_release_pm.py`.

## 2. Current backtest numbers (replace those in the Agent D section)

Core, against BEA first print, rule months Dec 2025 – Sep 2026 (n = 10):

| Run | Bias | MAE | SE | MAE ± 1 SE | RMSE | Largest miss | Threshold leg |
|---|---|---|---|---|---|---|---|
| Main run (as specified in the brief) | +0.019 | 0.0399 | 0.0080 | 0.0319–0.0478 | 0.0465 | +0.081 (Sep 2026) | pass |
| Variant: first-release portfolio-management PPIs | +0.017 | 0.0423 | 0.0081 | 0.0342–0.0505 | 0.0489 | −0.083 (Jan 2026) | inconclusive |
| Sensitivity: 8 PPIs without first release treated as assumed | +0.007 | 0.0590 | 0.0142 | 0.0448–0.0732 | 0.0727 | — | inconclusive |
| Before the correction, main run | +0.020 | 0.0405 | 0.0086 | 0.0318–0.0491 | 0.0480 | +0.093 (Sep 2026) | pass |

- Benchmarks are unchanged: core-CPI-only OLS 0.0874 (SE 0.0159); Cleveland nowcast 0.0677 (SE 0.0131); no change 0.0788 (SE 0.0221). The benchmark leg is met in every run.
- Headline, main run: MAE 0.0381, SE 0.0066, RMSE 0.0430. Variant: 0.0401, SE 0.0070.
- By group, main run, core: old-table months MAE 0.0327 (n = 8); current-table months 0.0684 (n = 2; misses +0.056 in Aug 2026 and +0.081 in Sep 2026).
- Excluded months, core misses: Nov 2025 +0.031; Oct 2023 +0.086; Oct 2024 +0.060.
- One-decimal hit rate, core: 0.4. 12-month error MAE: 0.041.
- Carry-forward window: 12 months, unchanged (assumed-tier core contribution MAE 0.0190, vs 0.0213 for 6 months and 0.0250 for 3). With a 6-month window the core MAE is 0.0409 (SE 0.0075); with 3 months 0.0477 (SE 0.0068). With revised PPIs throughout: 0.0308.
- **Reported band:** ±0.0465 pp on core m/m and ±0.0430 on headline (backtest RMSE of the main run; bottom-up band 0.027–0.031 core). Portfolio-management allowance 0.008 pp on core.
- **September 2026 dry run:** core 0.397 vs first print 0.317 (miss +0.081); headline 0.565 vs 0.491. Core 3m annualized 3.13 vs 2.90; 6m 3.03 vs 2.92; 12m 3.18 vs 3.12.

## 3. Addition: first-release portfolio-management PPIs (agents E and D2)

- **Agent E** recovered first-release values of `PCU5239405239401` and `PCU5239405239402` for Nov 2025 – Jul 2026 from BLS's archived PPI Detailed Reports (Table 11, NAICS 523940). Table: `outputs/E_pm_ppi_first_release.csv`. Full report and my review: `E_report_pending.md`. I read six rows in three of the PDFs myself; all match.
- **Agent D2** ran the backtest with those values in place of today's revised ones for line 268 in the old-table months, changing nothing else (`code/D2_variant_first_release_pm.py`, `outputs/D2_backtest_variant_first_release_pm.csv`, `notes_D2.md`). With the swap off, its harness reproduces the main run to 4 decimals.
- Result (after the correction above): core MAE 0.0423, SE 0.0081, range 0.0342–0.0505, which **includes 0.05**. Under the locked rule that reads "inconclusive at this sample size". Aug and Sep 2026 are identical in both runs, because line 268 is carried forward there.
- Still priced from revised data in the variant: the five `PCU523150…` brokerage and dealer PPIs (lines 262–267, about 0.21% of core, all ten months) and `PCU5132105132107` (one input to software, Aug and Sep 2026).
- **Which run the decision rule rests on is Eli's call.** The brief's information-set rule is "PPI inputs at first release where available", and the variant is closer to that than the main run. The main run is the one specified and applied before the first-release values were recovered.

## 4. Smaller corrections (Codex R1-F02 and R1-F03, accepted)

- **October 2025 fill.** We fill missing October 2025 CPI values with the geometric mean of September and November for both adjusted and unadjusted series. BEA's stated procedure is that for seasonally adjusted prices; for unadjusted prices BEA rebuilt October from October 2024 seasonal factors. For unadjusted series ours is an approximation, now labeled as such in the code and above. Codex's check: no rule-month estimate changes; excluded November 2025 core moves by +0.0008 pp.
- **Discontinued CPI series in the past-October checks.** The engine treats the stale-series lines as assumed in every month, including Oct 2023 and Oct 2024, when some of those series still had values. That departs from the month-by-month tier rule and was recorded only in `notes_D.md`. Codex's check with month-specific eligibility: Oct 2023 core miss +0.0872 (reported +0.0860); Oct 2024 +0.0585 (reported +0.0604). Rule months are unaffected. Not recoded; disclosed here.

## 5. Worth a look (from Codex round 1)

- FRED may carry some of the brokerage and dealer PPIs under older IDs (`PCU523120523120101`, `PCU523120523120102`, `PCU5231205231204`, `PCU523110523110201`) and a game-software commodity index (`WPU342104`). A lead for recovering more first-release history; not verified.
- Past October gaps for air transportation between BEA's adjusted series and the PPI range from about −4.4 to −8.2 pp, which supports the scale of the −5.96 pp adjustment but not its accuracy for any one October.

---

# October 2026 build (coordinator, 2026-11-13) — Audit 2 converged R1

**Status:** run after the October PPI release (Nov 13, 8:30 AM ET). Codex Audit 2 converged in round 1 (`06_Audits/04_oct_pce_build/A2_R1_codex.md`): no blocking findings; one README fix applied. Checkpoint D (Eli's review and placement decision) is still to come.

**Data.** `C2_fetch_bls.py` pulled all 284 component series into new raw files (`03_Data/Raw/bls_api_components_2015_2026_batch*_2026-11-13.json`); all six batches succeeded. `C2_build_history_coverage.py` rebuilt `outputs/component_series_history.csv`. All 28 PPI series now end in October 2026. Against the Nov 11 pull: 28 new observations (October PPI), no CPI changes, and 69 revised PPI values in Jun – Sep 2026. The audited Nov 11 history is kept as `outputs/component_series_history_2026-11-11.csv` (the backtest stays on it).

**Decision basis.** Eli chose the first-release variant on Nov 13: threshold leg inconclusive, so the default placement is a cross-check next to the Cleveland nowcast.

**Result** (`outputs/D_build_2026-10_summary.csv`, `D_build_2026-10_lines.csv`; carry-forward window 12 months; current BEA source table):

| | Core | Headline |
|---|---|---|
| October m/m % | 0.295 | 0.318 |
| 1-month annualized | 3.60 | 3.88 |
| 3-month annualized | 3.55 | 4.62 |
| 6-month annualized | 2.95 | 3.09 |
| 12-month | 3.24 | 3.82 |
| Band on m/m (first-release variant's backtest RMSE; Eli, Nov 13) | ±0.0489 | ±0.0452 |
| For reference: main-run RMSE | ±0.0465 | ±0.0430 |
| Cleveland Fed nowcast, Nov 10 | 0.267 m/m, 3.21 y/y | 0.305 m/m, 3.81 y/y |

- Bands scale about 12× on the annualized 1-month rate, 4× on the 3-month, 2× on the 6-month, 1× on the 12-month. Portfolio-management allowance: 0.008 pp on core.
- Rates extend BEA's SA September index (ALFRED vintage 2026-10-29): core 130.902 → 131.288; headline 132.257 → 132.677. Oct 2025 core base 127.165.

**Component map for October** (share of covered spending; 212 pricing lines, NPISH priced as one leaf):

| Type | Lines | Headline | Core |
|---|---|---|---|
| CPI direct, used as published | 155 | 67.4% | 65.0% |
| PPI direct, used as published | 10 | 1.0% | 1.1% |
| CPI direct, needs our seasonal adjustment | 3 | 0.3% | 0.3% |
| PPI direct, needs our seasonal adjustment | 11 | 16.5% | 18.6% |
| Composite, CPI relative-importance weights | 2 | 1.5% | 0.0% |
| Composite, equal weights (fallback) | 2 | 0.8% | 0.9% |
| Composite, weights fitted on BEA history | 3 | 2.2% | 2.4% |
| Proxied | 1 | 0.1% | 0.2% |
| Carried forward | 25 | 10.2% | 11.4% |

**Largest contributions to core (pp):** owners' equivalent rent +0.040; air transportation −0.028; newspapers and periodicals +0.023; computer software −0.021; nonprofit hospitals +0.018; meals at other eating places +0.018; taxicabs and ride sharing +0.016.

**Worth a look.**
- **Air transportation (line 207):** the PPI rose 3.6% unadjusted; our October seasonal adjustment is −5.96 pp, giving −2.34%. BEA's own October changes for this line in 2017–2025 ranged from −1.80% to +1.20%, so −2.34% would be the lowest October in that period. Air was also a large source of backtest error.
- **Computer software (line 50):** −1.69% (game-software PPI −3.7%, software CPI −1.5%). BEA's own Octobers ranged from −1.10% to +1.86%.
- Those two lines together take about 0.05 pp off core.
- Provenance labels in the lines file say "PPI revised (no first release)" for October PPI. On release day the October value in the history file *is* the first release; the label comes from `ppi_first_release.csv` not yet having October. Values are correct; the label is misleading.

**Walkthrough notebook.** `oct2026_pce_walkthrough.ipynb` (generated by `code/N_make_walkthrough_notebook.py`) reruns the map, the October build, the regressions, the identity test and the full backtest live from the same engine. Executed end to end on Nov 13: every check matches the audited files (October core 0.2951 and headline 0.3179; main-run core MAE 0.0399; variant 0.0423; hospital PPI F-statistic 11.520; carry-forward window 12). It writes nothing to `outputs/`.

---

# Workbook tab "PCE Oct 2026 estimate" (coordinator, 2026-11-13) — Audit 3 converged R2

**Request (Eli, Nov 13):** add one tab to `03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx` presenting the October estimate the way the workbook presents October CPI ("CPI Oct 2026 views") and September PCE ("PCE"), showing the main drivers of core and headline. This overrides the brief's "no workbook edits" rule for this one tab.

**How it was built**
- `code/W_build_pce_oct_tab.py` reads the audited October build (`outputs/D_build_2026-10_lines.csv`, `_summary.csv`) and writes a one-sheet build workbook, `Price indexes/Price_Basket_Findings_build_pce_oct_2026-11-13.xlsx`, plus `outputs/W_pce_oct_tab_lines.csv` (every line's numbers).
- Inserted with the pipeline's `replace_sheets.py`. The pre-edit workbook is archived at `Price indexes/archive/pre_replace_2026-11-13/`. A cell-by-cell fingerprint of all 11 existing tabs (values, formats, fills, merges, widths) is identical before and after; the new tab is appended last.
- Styling helpers and the Energy / Energy spillover / AI / Asset-price tags are copied from the pipeline's own `build_basket_workbook.py` and `analyze_baskets.py`.
- Component 3-month and 12-month rates extend BEA's published index for each line (U20404, vintage 2026-11-10) by our October change. Weights at the start of each window are BEA spending shares from the audited engine. Core membership is BEA's hierarchy, so core weights differ slightly from the existing "PCE" tab, which uses the pipeline's name-based core flag (see `02_Research/Subtasks/05_fix_core_flag/brief.md`).

**Layout** (matches "CPI Oct 2026 views": same widths for columns A–J, section and header styles, Up/Down #1–5 ranking)
1. Note on method, band, backtest and placement.
2. Estimated aggregates: headline and core at 1m, 3m ann., 6m ann., 12m, with sum of component contributions, gap, band, basis.
3. Top 5 up / down movers by **1m contribution** (the October m/m drivers), headline and core.
4. Top 5 up / down movers by 12m contribution (estimate), headline and core.
5. Breadth: share of weight above 3% (3m ann., y/y) and above own 2018–19 average.
6. 3m breadth, September (BEA published) vs October (estimate).
7. Comparison with the Cleveland Fed nowcast (Nov 10 vintage).

Two columns beyond the CPI tab: "Band ± (pp)" in the aggregates table, and "How priced" in the movers tables.

**What it shows (October 2026, estimate)**
- Core 0.30 m/m (±0.05), 3.55% 3m ann., 2.95% 6m ann., 3.24% 12m. Headline 0.32 (±0.05), 4.62%, 3.09%, 3.82%.
- Core m/m drivers, up: owners' equivalent rent +0.040 pp; newspapers and periodicals +0.023; nonprofit hospitals +0.018; meals at other eating places +0.018; taxicabs and ride sharing +0.016. Down: air transportation −0.028; computer software −0.021; motor vehicle rental −0.010; women's and girls' clothing −0.009; used trucks −0.008.
- Headline adds gasoline (+0.016) among the top up movers.
- Core 12m drivers, up: owners' equivalent rent +0.45 pp; software +0.20; air transportation +0.18; nonprofit hospitals +0.16; portfolio management +0.14 (carried forward). Down: prescription drugs −0.13.
- Breadth: 43.8% of core weight above 3% at a 3m annualized rate (September, BEA published: 43.7%); 51.1% above 3% y/y; 71.7% above its own 2018–19 average.
- **The 3m gap is large for headline (+0.55 pp; core +0.23).** Most of it is convexity: summing weight × each component's annualized 3m rate overstates the annualized aggregate when some components move a lot (gasoline +72% annualized). Codex measured 0.50 of the 0.55 pp headline gap and 0.19 of the 0.23 core gap as convexity; the rest is fixed-share aggregation against BEA's chained index. The CPI tab shows the same effect on a smaller scale. The aggregate rates come from the index, not the sum.
- Audit 3 R1 (Codex): fixed the Basis labels for the 3m and 6m rows (2 and 5 published months, not 11), added a note that weights are rescaled over the 99.7% of PCE covered, and corrected the gap explanation above.

---

# Corroboration for Checkpoint D (coordinator, 2026-11-14)

**Cleveland refresh.** `code/R_cleveland_refresh.py` re-pulled the nowcast (raw: `03_Data/Raw/ClevelandFed_nowcast_{month,year}_2026-11-14.json`; chart updated Nov 13). The October nowcast has been unchanged since the Nov 10 CPI release: core 0.267 m/m, 3.21% y/y; headline 0.305, 3.81%. The tab's Nov 10 row stays correct. Rerun on Nov 18 (`python3 -I code/R_cleveland_refresh.py 2026-11-18`).

**Other forecasters.** `outputs/R_forecaster_oct2026_2026-11-14.csv` (URLs, dates, quotes). All bank figures are press reports of client notes; the notes themselves were not accessible. Post-PPI:

| | Core m/m | Core y/y | Headline m/m | Headline y/y |
|---|---|---|---|---|
| Ours | 0.295 | 3.24 | 0.318 | 3.82 |
| Goldman Sachs (from 0.35) | 0.30 | 3.24 | 0.32 | 3.83 |
| Bank of America (from 0.32) | 0.29 | 3.2 | 0.30 | 3.8 |
| Capital Economics | 0.29 | 3.2 | — | — |
| Reuters, unnamed economists (from ~0.35) | ~0.3 | 3.2 | — | — |
| Cleveland nowcast | 0.267 | 3.21 | 0.305 | 3.81 |

Pre-PPI estimates (Pantheon 0.35–0.40, Reuters 0.4, SocGen 0.30 central) are in the CSV for the record. No page snapshots were saved; the CSV quotes are the record.

**Tab update (Eli, Nov 14).** "PCE Oct 2026 estimate" rebuilt with `code/W_build_pce_oct_tab.py` and reinserted with `replace_sheets.py` (pre-edit workbook: `Price indexes/archive/pre_pce_tab_forecasters_2026-11-14/`). Changes: the note's placement sentence now states Checkpoint D; the Cleveland section title says unchanged through Nov 13; a new last section lists the post-PPI forecasters above (marked not audited). Fingerprints of the other 12 tabs are identical before and after; October numbers unchanged (core 0.2951, headline 0.3179).
