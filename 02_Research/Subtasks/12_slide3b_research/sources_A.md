# Sources, Agent A (slide 3B). All pulled 2026-11-15. Tags: [O] opened/parsed locally, [S] snippet only, [2] secondary.

| Item | Source | Local file | Tag |
|---|---|---|---|
| SPF median core PCE (COREPCE1-6, A-C), history to 2026Q3 | Philadelphia Fed SPF, "Median Forecast Data for Levels" (medianLevel.xlsx), sheet COREPCE, row 233 = 2026Q3 | 03_Data/Raw/PhilFed_SPF_2026Q3_2026-11-15/medianLevel.xlsx | [O] |
| SPF dispersion D1 (P25/P75/IQR, quarterly T..T+4 only) | Dispersion_1.xlsx sheet COREPCE row 242 = 2026Q3 | .../Dispersion_1.xlsx (also Dispersion_2.xlsx saved; not used) | [O] |
| SPF individual responses (30 respondents, 2026Q3) | SPFmicrodata.xlsx sheet COREPCE | .../SPFmicrodata.xlsx | [O] |
| Variable/horizon definitions | SPF Documentation PDF (File Structure; COREPCE entry) | .../spf-documentation.pdf | [O] |
| Q3 survey text and Table 3 (cross-check of medians) | SPF Q3 2026 PDF, release date Aug 14, 2026 | .../spfQ326.pdf | [O] |
| Deadline / release dates | spf-release-dates.txt: "2026 Q3 8/11/26 8/14/26" | .../spf-release-dates.txt | [O] |
| Q4 2026 SPF status | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026 returned HTTP 404 at about 17:40 EST 2026-11-15; main SPF page lists Q3 2026 as the latest survey | .../page_spf_main.html | [O] |
| Sep 2026 SEP Table 1 | federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm (+ PDF) | 03_Data/Raw/FOMC_SEP_2026-09_2026-11-15/ | [O] |
| Core PCE index, monthly SA, latest vintage (realtime 2026-10-29) | FRED PCEPILFE, API observations | 03_Data/Raw/FRED_PCEPILFE_latest_2026-11-15/ | [O] |
| Core PCE as known on Aug 11 (vintage) | ALFRED PCEPILFE all vintages (existing project file, read only) | 03_Data/Raw/ALFRED_PCEPILFE_all_vintages_2026-11-11.json | [O] |
| Oct 2026 core estimate m/m 0.295, y/y 3.24 | project workbook Slide1_Inflation_Data.xlsx (Headline!C6, C10; cached values empty, formulas only) and brief; y/y re-derived from FRED (3.2424) | 01_Finals/data/Slide1_Inflation_Data.xlsx | [O] formulas; values from brief |
| EIA STEO Jul/Aug/Sep/Oct/Nov 2026 (Brent BREPUUS, table 2tab; Dates sheet) | eia.gov/outlooks/steo/archives/{jul26..nov26}_base.xlsx and .pdf; release dates from eia.gov/outlooks/steo/outlook.php | 03_Data/Raw/EIA_STEO_2026-11-15/ | [O] |
| EIA spot Brent/WTI daily to 2026-11-11 | Existing file from subtask 10 (EIA RBRTE/RWTC) | 02_Research/Subtasks/10_slide2_research/outputs/C_q8_oil_daily.csv | [O] |
| EIA NYMEX WTI futures RCLC1-4 | eia.gov/dnav/pet/hist_xls/RCLC{1-4}d.xls: data end 2024-04-05 | 03_Data/Raw/EIA_NYMEX_WTI_futures_RCLC_2026-11-15/ | [O] unusable for 2026 |
| Brent futures curve (BZ contract months), Aug 2026 | Yahoo Finance chart API, daily close, unexpired contracts only | 03_Data/Raw/Yahoo_BZ_futures_curve_2026-11-15/ | [2] |
| ICE / CME Brent futures | not retrievable (CME HTTP 403; ICE licensed) | n/a (A_paywalled.csv) | unverified |
| SPF Q4 2026 scheduled date (Nov 16) | stated in brief only; Philadelphia Fed calendar page is client-rendered; web search found no confirmation | n/a | unverified |
