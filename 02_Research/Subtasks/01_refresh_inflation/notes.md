# Notes: inflation_data refresh, 2026-11-10

## Steps
1. Archive: copied raw/, processed/, code/ to `03_Data/pipelines/inflation_data/archive/pre_refresh_2026-11-10/` (originals left in place).
2. Ran from project root with keys sourced from .env: retrieve_bls.py (first attempt HTTP 503 from BLS API, rerun succeeded), retrieve_bea.py, retrieve_fed_expectations.py (needed 2 fixes below), supplement_fed_expectations.py.
3. Did NOT run build_workbook.py / audit_workbook.py. `processed/calculated_rates.csv` and the workbook are therefore still at the Aug vintage until the coordinator builds.
4. Check script: `code/refresh_check.py` (outputs in `code/out/`): old vs new latest obs, metadata consistency, raw-file existence (0 problems), revisions since 2025-09.

## Script edits (all in 03_Data/pipelines/inflation_data/code/)
| File | Line | Before -> After | Why |
|---|---|---|---|
| retrieve_bls.py | 99 | release_note "Latest release: Q2 2026 revised, September 3, 2026." -> "Q3 2026 preliminary, November 5, 2026." | label date |
| retrieve_bls.py | 414 | `latest_release[key] = "2026-09-03"` -> `"2026-11-05"` | hard-coded productivity release date (verified on BLS prod2 release page) |
| retrieve_bls.py | 473, 482, 486 | REPORT.md text strings Q2 2026 revised / Sept 3 / ECI Q2 July 31 -> Q3 2026 preliminary / Nov 5 / ECI Q3 Oct 30 | report text only |
| retrieve_fed_expectations.py | 71 | `'stickyprice.xlsx' in x.lower()` -> `any(n in x.lower() for n in ('sticky-price-data.xlsx','stickyprice.xlsx'))` | Atlanta Fed renamed the download link (new: .../sticky-price/sticky-price-data.xlsx). New file has same 'Data' sheet and 25 identical column headers as the Sep 26 file (checked), so the column-index logic is unchanged |
| retrieve_fed_expectations.py | ~85 | SCE sheet list `[('Inflation expectations',('1','3')),('Five-year ahead Infl Exp',('5',))]` -> `[('Inflation expectations',('1','3','5'))]` | NY Fed removed the 'Five-year ahead Infl Exp' sheet; the column "Median five-year ahead expected inflation rate" is now in 'Inflation expectations' (col K). Same statistic, found by the same header-phrase match. Layout change, not a method change; flagged for verification (see report) |
| supplement_fed_expectations.py | ~166 | Michigan note keyed to 2026-09-01 "September 2026 = final" -> keyed to 2026-10-01 "October 2026 = final (SCA home page shows 'Preliminary Results for November 2026')" | latest month moved |
| supplement_fed_expectations.py | ~174 | revision_vintage_notes "latest (Sept 2026) is final." -> "latest (Oct 2026) is final; Nov 2026 preliminary on SCA home page but not yet in tbmpx1px5.csv." | same |

Not edited (stale text, overwritten or still true): retrieve_fed_expectations.py Dallas addmeta rows (latest_obs 2026-07-01 / release 2026-08-26) are replaced by supplement's Dallas rows; SPF latest_release_date '2026-08-14' and supplement SPF rows (2026-07-01 / 2026-08-14) remain correct because Q4 2026 SPF is not yet out (Philadelphia Fed files end 2026 Q3). Michigan table PDF `&y=2026` fine. retrieve_bea.py needed no edits (year range uses date.today(); vintage text branch already post-Sept 30). Year-range literals in retrieve_bls.py ("2020","2026") and observation_end 2026-12-31 still cover 2026.

## Results
- All series reach latest release (see report). release_dates.csv (BEA) now covers Aug (2026-09-30) and Sep (2026-10-29) for all 6 series; ALFRED had them (the earlier stop at July was FRED lag at the Sept 26 pull).
- BLS CPI Oct 2026: no 12-month rate published (Oct 2025 missing); latest 12m published rate is Sep 2026 (headline NSA 3.7, core NSA 2.6). BLS says so on the release page.
- umich_1y release_dates row: ALFRED MICH has no Oct 2026 yet, first_release_date blank (script note "not in ALFRED"); FRED cross-check for Oct is n/a.
- Michigan Nov 2026 preliminary exists on SCA home page but the pipeline's CSV (tbmpx1px5.csv) ends at Oct. Not in processed. The home-page snippet shows index values only; inflation-expectation medians for Nov prelim not retrieved (unverified).
- SPF Q4 2026 not out; processed SPF still Q3 2026 (released 2026-08-14).
- Breakevens daily to 2026-11-10: T5YIE 2.25, T10YIE 2.20, T5YIFR 2.15 (FRED). Sep 28 - Oct 1 gap noted in README is now filled.
- BEA services-ex-energy-housing FRED comparison shows "differences" of about 0.02 (FRED rounds to 1 decimal); pre-existing, same as before.
- Revisions since 2025-09 (see code/out/revisions_since_2025-09.csv, 123 rows). Notable: PPI intermediate unprocessed (62, SA) Jul index revised 277.050 -> 274.341, MoM 0.7 -> -0.2; Aug MoM 1.1 -> 0.9. Productivity Q3 release revised hourly comp and ULC back to 2025Q4 (e.g. ULC 2026Q1 12m 0.4 -> 1.8; hourly comp 2026Q1 3m_ann 2.1 -> 5.1). PCE Aug core MoM 0.2 -> 0.3 (index 130.455 -> 130.489).
