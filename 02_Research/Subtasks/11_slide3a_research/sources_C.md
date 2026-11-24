# sources_C (Agent C). [O] = opened and read/parsed this run; [S] = search snippet only; [2] = secondary. No [S] items used.

## Raw folders
- 03_Data/Raw/S3A_expectations_underlying_2026-11-15/ (fetch_log.csv lists every URL and status)
- 03_Data/Raw/S3A_fomc_statements_2026-11-15/ (fetch_log.csv)

## Expectations
- [O] NY Fed SCE chart data xlsx, https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-data.xlsx (sheet "Inflation expectations"; Oct 2026 = 3.914/3.288 median 1y/3y). Identical to pipeline copy dated 2026-11-10.
- [O] NY Fed SCE Oct 2026 press release, https://www.newyorkfed.org/newsevents/news/research/2026/20261109 (dated Nov 09, 2026; 3.9/3.3/3.0). Release date 2026-11-09.
- [O] Michigan Surveys of Consumers via pipeline: 03_Data/pipelines/inflation_data/processed/fed_expectations/observations.csv (raw: umich_sca_tbmpx1px5_2026-11-10.csv and umich_sca_tbcpx1px5_current_2026-11-10.csv; header of the current table opened). Nov 2026 PRELIMINARY, release 2026-11-06 (pipeline release_dates, publisher calendar). Cross-check FRED MICH (fetched; ends Sep) equal. Not re-downloaded.
- [O] Philadelphia Fed SPF median files via pipeline raw (philadelphiafed_spf_median_*_2026-11-10.xlsx); SPF documentation pdf (pipeline raw 2026-09-26) for variable definitions. Q3 2026 release 2026-08-14 (pipeline release_dates).
- [O] Philadelphia Fed SPF landing page, https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters (Q3 2026 latest as of 2026-11-15 17:49 EST); probe URL .../spf-q4-2026 returned a 404 page.
- [O] FRED T5YIE, T10YIE, T5YIFR (API, through 2026-11-13); GASREGW (EIA weekly regular retail gasoline, through 2026-11-09); MICH. https://fred.stlouisfed.org/series/<ID>
- [O] 03_Data/pipelines/inflation_data/Inflation_Expectations.xlsx (13-measure aggregate, built 2026-11-14) and Logan speech https://www.dallasfed.org/news/speeches/logan/2026/lkl261110 (saved html 2026-11-10_Logan_economic_monetary_policy_outlook.html).

## Underlying trend
- [O] NY Fed MCT data, https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/mct/mct-chart-data.csv and mct-chart-meta-content.json; page https://www.newyorkfed.org/research/policy/mct (data "available for download"; release 10:00 ET 2026-10-30).
- [O] Dallas Fed trimmed mean PCE via FRED PCETRIM1M158SFRBDAL, PCETRIM6M680SFRBDAL, PCETRIM12M159SFRBDAL (Dallas-originated) and the pipeline copy. Publisher page https://www.dallasfed.org/research/pce opened (Sep 12m 2.3; 6m 2.4; 1m ann 2.8; latest update Oct. 29). The pipeline dallasfed xlsx is a distribution chart only.
- [O] Cleveland Fed median PCE, https://www.clevelandfed.org/indicators-and-data/median-pce-inflation ; file https://www.clevelandfed.org/-/media/files/webcharts/medianpce/median-pce-full-history.csv (+ current-components.csv). Updated 2026-10-29; next 2026-11-25.
- [O] Cleveland Fed median CPI / trimmed-mean CPI, https://www.clevelandfed.org/indicators-and-data/median-cpi ; files mcpi_revised.csv, trim_revised.csv, core.csv, cpi.csv (…/files/webcharts/mediancpi/), pipeline chartdata csv 2026-11-10; FRED MEDCPIM159SFRBCLE/TRMMEANCPIM159SFRBCLE. Updated 2026-11-10.
- [O] BEA price indexes via pipeline: 03_Data/pipelines/inflation_data/processed/bea/observations.csv (T20804 L1, L25, L28, L31; vintage 2026-11-10, LastRevised 2026-10-29).
- [O] BEA NIUnderlyingDetail U20404 (Fisher price indexes) and U20405 (nominal $), pipeline raw 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U2040{4,5}_2026-11-10.json; components.csv (leaf rates, validation).
- [O] 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv and D_build_2026-10_summary.csv (audited Oct estimate; every Oct value labelled est.).
- [O] 03_Data/pipelines/Price indexes/code/core_ex_oer.py (method reused for removal of a component from a chained Fisher aggregate).

## Time above target and policy
- [O] FRED PCEPI, PCEPILFE (latest vintage, ALFRED snapshots as of 2021-05-01, 2021-06-01, 2026-09-29), CPIAUCNS, CPILFENS. BLS CPI Oct 2025 gap confirmed in pipeline bls observations (footnote X).
- [O] Board of Governors, Open Market Operations page (target range table), https://www.federalreserve.gov/monetarypolicy/openmarket.htm (saved; "Last Update: September 16, 2026").
- [O] FOMC calendars page, https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm and 59 FOMC statements https://www.federalreserve.gov/newsevents/pressreleases/monetaryYYYYMMDDa.htm, Mar 3 2020 to Oct 28 2026; Plans for Reducing the Size of the Federal Reserve's Balance Sheet https://www.federalreserve.gov/newsevents/pressreleases/monetary20220504b.htm
- [O] FRED DFEDTARU / DFEDTARL (cross-check; all 20 changes match).
