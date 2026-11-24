# notes_C.md (Brief C, data pulls, run 2026-11-11)

Scripts (all in code/, run from project root with `python3 -I`): C_fetch_alfred.py, C_fetch_cleveland_bls.py (fetch); C_alfred_lib.py, C_pce_first_prints.py, C_core_cpi_first_prints.py, C_cleveland_nowcast_history.py, C_crosscheck_cleveland.py, C_parse_bls_concordance.py, C_series_list_freshness.py (compute).
Raw (03_Data/Raw, dated 2026-11-11): ALFRED_{PCEPILFE,PCEPI,CPILFESL}_all_vintages (output_type=1: one row per obs per realtime interval), *_vintagedates, FRED_*_seriesinfo; ClevelandFed_nowcast_{month,year,quarter}; BLS_pce_cpi_code_mapping (.html raw, .csv derived); bls_{cu_item,cu_series,pc_series,wp_series}; BLS_cpi_news_release_cpi_htm.

## Method
- First-release vintage of month m = earliest realtime_start with a non-missing value. Levels "within vintage" = value whose realtime interval contains that date.
- m/m = (L_m / L_m-1 - 1)*100 using 3-decimal levels; y/y = same vs m-12 within the same vintage. 1dp rounded half-up.
- ALFRED vintage date is treated as the agency release date. Cross-checked indirectly: Cleveland's own release dates for PCE match ALFRED's first-release vintage in all 33 months (Jan 2024-Sep 2026) and for CPI in all months where both exist (no mismatches; C_crosscheck_cleveland.py). Not independently checked against BEA/BLS release calendars.

## Task 1 PCE first prints
- 33 ref months Jan 2024-Sep 2026, core (PCEPILFE) and headline (PCEPI), SA, 2017=100.
- Release delays/combination flagged in `flag` column: Sep 2025 (released 2025-12-05, lag 66d), Oct and Nov 2025 (both first released together 2026-01-22), Dec 2025 (2026-02-20), Jan 2026 (2026-03-13), Feb 2026 (2026-04-09). Mar 2026 released 2026-04-30 (normal lag 30d). Normal lags 20-31d.
- Revision from first print to current vintage, abs mean (m/m, pp): core 0.039, headline 0.038; max core 0.188 (Apr 2025: 0.1159 -> 0.3037), headline 0.133 (Apr 2025). Core Jul 2026 first 0.2455 -> now 0.1377 (-0.108, revised within the 2026-09-30 vintage, seen only 2 months after). Some revision comes from BEA's annual update (the 2026-09-30 vintage revised earlier levels; e.g. Oct 2025 core 127.243 -> 127.165; extent of back-revision not mapped).
- The 2026-09-30 vintage (Aug 2026 release) coincided with the annual update.
## Task 2 cross-check
- All 90 month x series levels (Jan 2023-Sep 2026 core and headline) in ALFRED current vintage equal BEA pipeline file U20404 (DPCCRG/DPCERG) within 0.0006: 0 mismatches. Sep 2026 core 130.902, headline 132.257; Oct 2025 core 127.165 confirmed. File: outputs/C_crosscheck_alfred_vs_bea.csv.
## Task 3 core CPI (CPILFESL)
- Oct 2025: no value ever published. ALFRED shows '.' (missing) from vintage 2025-12-18 to present; no earlier vintage had Oct. Nov 2025: first print 331.068 (vintage 2025-12-18), revised to 331.043 on 2026-02-13 (annual SA revision). Sep 2025 level 330.542 at first print, 330.418 current.
- Nov 2025 first-print m/m not computable (Oct missing). Sep->Nov 2025 two-month change at first print: 0.1591% (330.542 -> 331.068, vintage 2025-12-18); y/y at first print 2.6189. Dec 2025 first-print m/m 0.2392 (vintage 2026-01-13) is computed vs Nov.
- BLS release page confirms (opened): "BLS did not collect survey data for October 2025 because of a lapse in appropriations", and BLS cannot publish 12-month changes for October 2026 where Oct 2025 is unavailable (all items and core show "-").
- Oct 2026 core CPI first print: vintage 2026-11-10, level 339.900, m/m 0.2963 (BLS table rounds to 0.3). y/y not computable.
- Core CPI first-print revisions are small: mean abs 0.0135 pp (n=32, 2024+), max 0.038. Part of the difference is the annual SA revision each February, not data revision.
## Task 4 Cleveland nowcast
- month/year JSON: list of 161 charts (target months 2013-07..2026-11), quarter 54. `_comment` = "2026-11-10 00:00" in all (the "updated" stamp). Per chart: categories = dates MM/DD (no year; inferred) plus vertical-line event markers (e.g. "CPI Oct"); datasets: nowcasts (CPI, Core CPI, PCE, Core PCE) and "Actual ..." series, the actual placed on release day, where the nowcast series goes blank.
- Cleveland's "actual" m/m equals my ALFRED first-print m/m for core and headline PCE in all 33 months, and core CPI actuals match.
- Nowcast errors, last nowcast before PCE release minus actual (pp), Jan 2024-Sep 2026, n=33: core PCE mean -0.015, MAE 0.065, range -0.191 (Jun 2024) to +0.148 (Nov 2024); headline mean -0.007, MAE 0.057, range -0.143 (Feb 2025) to +0.143 (Nov 2024).
- Core PCE nowcast changed little between day after CPI and the pre-release day in most months (the nowcast moves mostly on CPI day itself). Day-after-CPI core PCE MAE 0.067. In many months day-after value equals the pre-PCE value (no further update after PPI/CPI).
- Current (chart updated 2026-11-10; dates are nowcast dates):
  Oct 2026 m/m: CPI 0.2421 and core CPI 0.2114 (last nowcast 11/09, then replaced by actuals 0.3503 / 0.2963 on 11/10); PCE 0.3051, core PCE 0.2669 (nowcast dated 11/10).
  Oct 2026 y/y: PCE 3.8114, core PCE 3.2134 (11/10); CPI nowcast 3.7418, core CPI 2.4828 (11/09), actual shown by Cleveland 3.8479 / 2.5767.
  Nov 2026 m/m: CPI 0.1351, core CPI 0.2111, PCE 0.2129, core PCE 0.2640; y/y: CPI 3.9354, core CPI 2.8733, PCE 3.8252, core PCE 3.3250 (11/10).
## Task 5 BLS concordance
- Page fetched OK (HTTP 200) with the contact UA. 15 HTML tables, 404 data rows (ELI, ELI description, PCE series code, PCE description); 315 unique ELIs, 167 unique PCE codes; some ELIs appear on multiple rows (mapped to more than one PCE code, e.g. AA022, AB013, ED011). Page "Last Modified Date: April 5, 2024". Built for the 2011 Blair et al. NBER/CRIW concordance. CSV: 03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv (derived from the saved HTML).
## Task 6 series lists (2026-11-11 vs 2026-09-27)
- cu.item: byte-identical (400 items). cu.series 8104 -> 8104, pc.series 4510 -> 4510, wp.series 5312 -> 5312: zero series added, zero dropped. Only end_year/end_period (and one wp series_title) fields changed: cu end period mostly M08 -> M10 (3019 series), pc/wp M08 -> M09 (PPI Sep is latest in file).
- Odd: wp WPU14440101 end moved back 2026M08 -> 2022M05; pc PCU3365103365106 end 2026M08 -> 2019M07; wp WPU02890149 title text changed (dropped "including tortillas"). New copies saved to 03_Data/Raw; pipeline copies untouched.

## Worth a look
1. Cleveland shows Oct 2026 y/y "actual" core CPI 2.5767 and CPI 3.8479, but BLS did not publish Oct 2026 12-month changes (Oct 2025 missing). Cleveland's figure is their own approximation, not a BLS number.
2. Core PCE nowcast misses (nowcast minus actual, pp): Jun 2024 -0.19 (nowcast -0.009 vs actual 0.182), Feb 2025 -0.17, Nov 2024 +0.148, Feb 2026 -0.135, Dec 2025 -0.122. Dec 2025-Mar 2026 misses were all negative (-0.122, -0.093, -0.135, -0.063).
3. Apr 2025 core PCE first print 0.1159 later revised to 0.3037, the largest first-print revision in the window.
4. Mar 2026 headline PCE first print 0.6642 m/m and Jun 2026 -0.1087 (energy swings; not examined).
