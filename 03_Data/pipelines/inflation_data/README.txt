INFLATION INDICATOR DATASET — README
Retrieved: 2026-09-26 (all sources); PCE refreshed 2026-09-30, Dallas 2026-10-01, breakevens 2026-10-02. Built for Eli Powers's College Fed Challenge inflation assessment.

FOLDER CONTENTS
  inflation_indicators.xlsx   Final workbook (sheets described below). Latest-12-month view only; no full histories.
  raw/bls/                    Unmodified BLS Public Data API v2 responses (2000-2019 and 2020-2026 windows, catalog + calculations) and ALFRED/FRED check files.
  raw/bea/                    Unmodified BEA API responses (NIPA T20804, T20807; NIUnderlyingDetail U20404), parameter inventories, ALFRED/FRED check files.
  raw/fed_expectations/       Publisher downloads: Cleveland Fed trimmed-mean CSVs; Atlanta Fed sticky-price CPI workbook; NY Fed SCE chart-data workbook + questionnaire;
                              Michigan SCA tbmpx1px5.csv (+ table PDFs); Philadelphia Fed SPF median files + SPF documentation PDF; St. Louis Fed FRED JSON
                              (breakevens; Dallas Fed trimmed mean fallback; cross-checks; ALFRED release dates).
                              umich_probe_* files are unused format probes from the retrieval run (kept for provenance).
  processed/<group>/observations.csv    Normalized long-format series, full native-frequency history (Jan 2000 or series start onward; some publisher files start earlier).
  processed/<group>/series_metadata.csv Per-series metadata (IDs, titles, definitions, units, SA status, coverage, URLs, raw paths, vintage notes).
  processed/<group>/release_dates.csv   First-release dates (ALFRED output_type=4 where available; publisher calendars otherwise).
  processed/<group>/REPORT.md           Retrieval and verification report for each source group (includes manager addenda).
  processed/calculated_rates.csv        Full history of every permitted calculated/assembled rate for the monthly price indexes, with Y/N/N/A flag and method note.
  code/fetch_utils.py                   Shared HTTP/saving helpers; API keys read from environment variables and redacted from every saved file.
  code/retrieve_bls.py, retrieve_bea.py, retrieve_fed_expectations.py   Group retrieval scripts (written by Codex subagents, reviewed/patched by the manager).
  code/supplement_fed_expectations.py   Manager supplement; run after retrieve_fed_expectations.py.
  code/build_workbook.py                Manager calculations, validation, and workbook build.
  code/subagent_spec.md                 Shared retrieval spec given to the subagents.

SOURCES (originating publishers)
  BLS: CPI-U (CUSR0000SA0, CUUR0000SA0, CUSR0000SA0L1E, CUUR0000SA0L1E); PPI FD-ID (WPSFD4/WPUFD4, WPSID61-63/WPUID61-63, WPSFD423/WPUFD423, WPSFD42311/WPUFD42311);
       ECI (CIS/CIU 1010, 1020, 1030, 2010, 2020, 2030 — I, Q, A series); Productivity and Costs nonfarm business (PRS85006091-93, -101-103, -111-113).
  BEA: PCE, core PCE, market-based PCE, market-based core, PCE services ex energy and housing (NIPA T20804/T20807); PCE goods ex food and energy (U20404 line 375).
  Federal Reserve Bank of Dallas: Trimmed Mean PCE (1-month annualized, 6-month annualized, 12-month) via FRED (PCETRIM1M158SFRBDAL, PCETRIM6M680SFRBDAL, PCETRIM12M159SFRBDAL),
       because the Dallas Fed site offers no historical time-series download.
  Federal Reserve Bank of Cleveland: 16% trimmed-mean CPI (monthly change, annualized monthly change, 12-month change; 12-month from chart data beginning 2017-01).
  Federal Reserve Bank of Atlanta: Sticky-price CPI, core sticky-price CPI, sticky-price CPI less shelter (monthly, 1-month annualized, 3-month annualized, 12-month).
  Federal Reserve Bank of New York: SCE median 1-, 3-, 5-year-ahead expected inflation (5-year begins 2022-01).
  University of Michigan Surveys of Consumers: median expected price change next 12 months (PX_MD) and next 5-10 years (PX5_MD).
  Federal Reserve Bank of St. Louis: T5YIE, T10YIE, T5YIFR (daily, from 2003-01-02; derived by the St. Louis Fed from Board H.15 yields).
  Federal Reserve Bank of Philadelphia: SPF median CPI, CORECPI, PCE, COREPCE (horizons 1-6, A, B, C), CPI5YR, CPI10, PCE5YR, PCE10.

CALCULATION APPROACH
  Only for monthly price-index series, only when the publisher does not report the rate:
    MoM    = (I_t / I_t-1 - 1) x 100                (SA index)
    3m ann = ((I_t / I_t-3)^4 - 1) x 100            (SA index; compounded annual rate, not a moving average)
    6m ann = ((I_t / I_t-6)^2 - 1) x 100            (SA index)
    12m    = (I_t / I_t-12 - 1) x 100               (NSA index; SA index only for BEA PCE series, which BEA publishes SA only)
  Publisher-reported rates are used verbatim (flag N): BLS API 1-month (SA) and 12-month (NSA) changes; BEA Table 2.8.7 percent change from preceding month;
  all Dallas/Cleveland/Atlanta rates; ECI 3-month/12-month and Productivity & Costs quarterly/annual changes.
  Rate-only publishers are never calculated; unpublished horizons are N/A; non-preferred published horizons go in "Other".
  Missing inputs produce N/A (no interpolation, no carry-forward). Expectations, breakevens, SPF, ECI and ULC get no derived changes.

WORKBOOK SHEETS
  Read Me            Legend for flags and conventions.
  Current Snapshot   One row per requested series/measure at its latest observation: value and measure label, YoY / 6m ann / 3m ann / MoM with
                     calc-required flags (Y/N/N/A), "Other" publisher-reported horizon, notes.
  Recent 12 Months   Same columns, one row per series per observation date within the latest 12 months, at native frequency (12 monthly, 4 quarterly, ~250 daily rows).
  Sources & Methods  Publisher, exact title, IDs/tables, definition, frequency, units, SA status, population, coverage, latest release, URLs/endpoints,
                     raw-file paths, retrieval date, revision/vintage notes, calculation notes.

VINTAGES, BREAKS, AND KNOWN LIMITS
  - BEA PCE: post-annual-update vintage (retrieved 2026-09-30; latest = August 2026, released Sept 30). BEA revised Jan 2021-Jul 2026 and changed methods for portfolio management, software and legal services. PCE rows in the workbook were updated in place; pre-update data are in archive/vintage_2026-09-27_pre_annual_update/. FRED/ALFRED had not yet loaded the revision on Sept 30 (cross-checks show vintage mismatches, expected). Dallas trimmed mean updated Oct 1 to August 2026 on Dallas's revised (post-update) history.
  - BLS CPI October 2025 is unavailable (BLS footnote X, 2025 appropriations lapse). November 2025 is published. Rates needing October 2025 are N/A.
  - PPI final-demand and services-for-intermediate-demand indexes begin Nov 2009 (FD-ID system start).
  - BLS publishes no single total "intermediate demand" index; the three commodity-type indexes are provided (Eli's choice).
  - "Trade services for personal consumption" = BLS catalog title "Final demand - Trade of personal consumption goods" (WPSFD42311/WPUFD42311).
  - Cleveland 12-month trimmed-mean history from the publisher's own files begins 2017-01. Cleveland and Atlanta monthly changes are decimal fractions (0.003 = 0.3%).
  - Michigan moved from phone to web interviewing during 2024 (series break). September 2026 is the final reading.
  - SCE and pre-latest SPF release dates are not machine-retrievable (N/A with calendar links).
  - The BEA API echoes the API key in responses; it has been replaced with "REDACTED" in saved raw files. That is the only modification to raw files.
