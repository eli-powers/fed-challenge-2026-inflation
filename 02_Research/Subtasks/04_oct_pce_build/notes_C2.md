# notes_C2: component data pulls, round 2 (retrieved 2026-11-11)

Scripts (run from project root, `python3 -I`): `code/C2_fetch_bls.py` -> `C2_build_history_coverage.py` -> `C2_fetch_alfred.py` -> `C2_compute_first_release_revisions.py`.

## Task 1: BLS history
- 284 series (277 in series_to_fetch + 7 extras) in 6 API v2 batches, Jan 2015-Dec 2026 request window; raw at `03_Data/Raw/bls_api_components_2015_2026_batch1..6_2026-11-11.json`. All batches REQUEST_SUCCEEDED and returned every requested series. Only "No Data Available" messages (genuine series gaps, below) were present, so batches were saved as returned.
- Extras: PCU5239405239401, PCU5239405239402 (named in brief); CPI Legal services NSA/SA CUUR/CUSR0000SEGD01 (old source E1GAL1/E1AXS1); CPI Hospital and related services NSA/SA CUUR/CUSR0000SEMD (E1MEF1); CUSR0000SEEE02 (does not exist; BLS says "Series does not exist"; old source for E1CPS1 is NSA, CUUR0000SEEE02 already in the fetch list).
- Old-source identification: E1CPS1 -> CUUR0000SEEE02 (in list); E1OMS1/E1OMO1 -> CUUR0000SEMC04 (in list); E1PMI1 -> PCU5239405239401/02 (extras); E1GAL1/E1AXS1 -> CUUR0000SEGD01; E1MEF1 -> CUSR0000SEMD; E1FIS1 -> CUSR0000SEFG; E1DEN1 -> CUSR0000SEMC02; E1SPE1 -> CUUR0000SS62032; E1NSC1/E1CHC1 -> CUUR0000SEEB03; E1TAP1 -> CUSR0000SS68023 (all in list). E1MDF1 "Club dues and fees for participant sports and group exercises": no BLS item with that exact name; closest is SERF01 "Club membership ... or participant sports fees" (CUUR0000SERF01, in list), match is judgment, unconfirmed. E1IMC1 is an implicit BEA/BLS banking-output extrapolation, not a CPI/PPI series: not pulled.
- Footnote codes seen: X (2025 lapse in appropriations; Oct 2025 CPI, value "-" stored blank), P (preliminary). No discontinued flags are returned by the API; discontinuation inferred from coverage.
- Values are as published 2026-11-11 (CPI Oct 2026 released Nov 10; PPI through Sep 2026).

## Task 2: coverage (`component_series_coverage.csv`)
- CPI present for Oct 2026: 246 of 256 CPI series. Without Oct 2026 (10): CUSR0000SEEE02 (nonexistent), CUSR0000SEGD01 and CUUR0000SEGD01 (last value 2024-09; extras), CUUR0000SEHP (last 2024-10), CUUR0000SEHP01 (2024-11), CUUR0000SEHP04 (2024-07), CUUR0000SS45031 (no data at all; BLS list end 2000M05), CUUR0000SS61021 (2016-10), CUUR0000SS62051 (2020-11), CUUR0000SS62052 (2020-12). Seven of the ten are in series_to_fetch (SEHP, SEHP01, SEHP04, SS45031, SS61021, SS62051, SS62052).
- PPI: all 28 (26 + 2 extras) last = Sep 2026; Oct 2026 absent (expected, PPI due Nov 13). Oct 2025 PPI has values for all 28.
- Oct 2025 CPI: blank with footnote X in 240 series-rows; numeric in 11 (SA: SEEC01, SETA02, SETA03, SS45011, SS45021; NSA: SEEC01, SEED03, SETA02, SETA03, SS45011, SS45021). Oct 2025 numeric values for these are what BLS published; not investigated further.
- Series with extra gaps since 2017: SEMC04 (SA and NSA, 12; values only in 2026-04, -06, -08, -10 and a subset of 2025-11..2026-09), SETA03 (38, 2020-04..2025-03), SEEA (8), SS62032 (8), SS68023 (11), SSEE041 smartphones (starts 2019-12), SEEC02, SEFV03, SS47021 (1 extra month each). `missing_detail` column has the months.

## Task 3: PPI first release (`ppi_first_release.csv`)
- FRED ID resolution in `outputs/C2_alfred_id_resolution.csv`. IDs differing from BLS: PCU6211--6211-- = PCU62116211; PCU622---622--- = PCU622622. All other found PPIs use the BLS ID.
- NOT in ALFRED (HTTP 400 on series lookup; "not found" = unconfirmed, series-search also returned nothing): PCU5132105132107, PCU5231505231501011, PCU5231505231501012, PCU523150523150102, PCU5231505231502011, PCU5231505231502012, PCU5239405239401, PCU5239405239402. 20 of 28 carried. FRED has older NAICS-based portfolio management IDs (e.g. PCU523920523920P) but not these.
- 440 rows (20 series x 22 reference months, Dec 2024-Sep 2026), NSA. Vintage dates are ALFRED realtime_start. Shutdown-delayed releases appear as batched first-release dates (e.g. PCU622622: Sep 2025 first on 2025-11-25; Oct and Nov 2025 both on 2026-01-14).
- All 440 rows: mean |current m/m - first-print m/m| = 0.256 pp; 61% of rows differ by more than 0.005 pp; 36 rows differ by more than 1 pp. By series (mean abs, max): PCU5182105182105 1.03/4.58; PCU5613805613802 0.80/2.56; PCU621512621512 0.47/3.99; PCU524114524114 0.38/4.22; PCU4811114811111 0.38/1.13; ... PCU6211--6211-- 0.05/0.31 (full list reproducible from file).

## Task 4: CPI SA revisions (`C2_cpi_sa_revisions_summary.csv`, `C2_cpi_sa_revisions_by_month.csv`)
- Sample: ten largest `share_of_headline_sep2026` SA series (summed over component_mapping rows by series_id_sa; headline SA0 excluded). FRED does not carry CUSR0000SEMF01, SEFV01, SS45021 (shares 2.76%, 2.72%, 1.68%); replaced by next-largest carried: SEFX, SAA1, SERE01. Sample: SEHC01, SETB, SEMC04, SETD, SEHF01, SAA2, SETA02, SEFX, SAA1, SERE01.
- The SA level for reference months 2024-12 to 2025-12 was revised on the 2026-02-13 vintage (the February seasonal-factor revision) in 7 of 10 series: SEHC01, SETB, SEHF01, SAA2, SETA02, SAA1, SERE01; Oct 2025 is revised only where a value exists (SETA02). No revision to any month from 2026-01 on. SETD and SEFX: no revisions in any month; SEMC04: no revision among the 7 months compared (sparse data).
- Mean abs m/m revision (pp), n months: SEHC01 0.008 (20); SETB 0.452 (20; max 2.48); SEMC04 0.000 (7); SETD 0.000 (20); SEHF01 0.089 (20); SAA2 0.158 (20); SETA02 0.099 (22); SEFX 0.000 (20); SAA1 0.129 (20); SERE01 0.159 (20).

## Worth a look
1. CPI household operations (SEHP, SEHP01, SEHP04), Legal services (SEGD01), and several Photo series have no October 2026 value; SEHP* last values 2024-07..2024-11 and sparse since 2024 (values only for some months). BEA maps lines 328, 330-332 to these (component_mapping).
2. CPI SEMC04 (services by other medical professionals; BEA lines 176, 180, 181; share 1.9%) has values only in some months since mid-2025.
3. Oct 2025 CPI numeric (not X) for 11 series, including SA SETA02 and SETA03 (leased cars).
4. PPI Oct 2025 first release came on 2026-01-14 (ALFRED vintage dates) for all 20 series carried.
5. SETB (gasoline SA) 2025-03 level 277.740 first release vs 283.182 current, a 1.96% level change from the Feb 2026 SA revision.

## Limits
- ALFRED ref month with no ALFRED row for 2025-10 CPI SA appears as "." in the vintage (value missing). Months with first release missing are skipped in the by-month table.
- ALFRED realtime dates can differ by a day from BLS release dates; not checked against BLS calendars.
- Mean abs revision for SEMC04 is based on only 7 months with values in both vintages.
