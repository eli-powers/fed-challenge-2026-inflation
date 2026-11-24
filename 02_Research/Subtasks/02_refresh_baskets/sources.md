# Sources — 02_refresh_baskets (accessed 2026-11-10)

Tags: [O] opened and read; [S] search snippet only; [2] secondary.

| Source | URL | Tag | Supports |
|---|---|---|---|
| BEA API, NIUnderlyingDetail U20404 / U20405 (monthly, 2017–2026) | https://apps.bea.gov/api/data/ (saved: PCE/raw/BEA_NIUnderlyingDetail_U2040{4,5}_2026-11-10.json) | [O] | PCE component prices and nominal spending through 2026M09; core ex OER; sector contributions |
| BEA API, NIPA T20804 / T20807 | same (PCE/raw/BEA_NIPA_T2080{4,7}_2026-11-10.json) | [O] | Published PCE, core (l.25), supercore (l.28), market-based (l.30/31) rates |
| BEA API, NIUnderlyingDetail U90100 (Table 9.1U) | same (Cross-index analysis/raw/..._U90100_2026-11-10.json) | [O] | CPI–PCE reconciliation, Dec 2025–Sep 2026 |
| BLS Public Data API v2 | https://api.bls.gov/publicAPI/v2/timeseries/data/ (saved: CPI/raw, PPI/raw bls_api_*_2026-11-10.json) | [O] | CPI leaves through Oct 2026 (Oct 2025 = "-"), PPI through Sep 2026; BLS 12m calcs for Sep CPI (3.7, 2.6) |
| BLS CPI relative importance Dec 2024, Dec 2025 | https://www.bls.gov/cpi/tables/relative-importance/2024.xlsx, .../2025.xlsx | [O] | CPI weights |
| BLS CPI news release, October 2026 | https://www.bls.gov/news.release/cpi.nr0.htm | [O] | Oct 1m changes; statement that 12m changes for Oct 2026 cannot be published where Oct 2025 is missing; Table A gasoline 37.4, new vehicles 0.7, used cars −3.3 (12m) |
| BLS CPI factsheet, approximating missing data | https://www.bls.gov/cpi/factsheets/approximating-missing-data.htm | not opened (link cited in the release) | Possible 12m approximation method (unverified) |
| BLS PPI news release, September 2026 | https://www.bls.gov/news.release/ppi.nr0.htm | [O] | FD +1.3% m/m SA (largest since Mar 2022), +6.3% 12m NSA (largest since Dec 2022); Aug revised to +0.5% |
| BLS PPI FD/ID relative importance 2025 | https://www.bls.gov/ppi/tables/final-demand-relative-importance-by-component-series-2025.xlsx; .../intermediate-demand-by-commodity-type-relative-importance-by-component-series-2025.xlsx | [O] (script fetch) | PPI weights |
| FRED PCEPILFE, PCEPI (units pc1) | https://api.stlouisfed.org/fred/series/observations?series_id=PCEPILFE (and PCEPI) | [O] | Spot-check: Sep 2026 12m 3.12116 / 3.64887 |
| Cleveland Fed median CPI files (component table, trim_revised, mcpi_revised, cpi, core, zips) | https://www.clevelandfed.org/-/media/files/webcharts/mediancpi/ | [O] | Oct 2026 tails; trimmed-mean 1m 0.369% (0.4) / 4.5% ann. |
| Atlanta Fed sticky-price CPI page | https://www.atlantafed.org/research-and-data/data/sticky-price-cpi | [O] | New workbook link |
| Atlanta Fed sticky-price workbook (new URL) | https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/sticky-price/sticky-price-data.xlsx | [O] | Sticky/flexible rates through Oct 2026 |
| Atlanta Fed old workbook URL | https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/datafiles/research/inflationproject/stickprice/stickyprice.xlsx | [O] (HTTP 404) | URL moved |
| Dallas Fed trimmed mean PCE page, history workbook, component workbook, tech note | https://www.dallasfed.org/research/pce; .../pce/pcehist; .../pce/detail; .../pce/tech.pdf | [O] (script fetch) | Dallas 1m/6m/12m Sep 2026; trim status |
| BEA FAQ 83 (market-based PCE); NIPA Handbook ch. 5 | https://www.bea.gov/help/faq/83; https://www.bea.gov/sites/default/files/methodologies/nipa-handbook-all-chapters.pdf | [O] (script fetch, not reread) | Market-based membership docs; PPI-source mapping (unchanged) |
| Cleveland Fed median CPI page | https://www.clevelandfed.org/indicators-and-data/median-cpi | [O] | Link to interpolation method PDF and data files |
| Cleveland Fed, "Methodological Approach to Interpolating Missing October 2025 CPI Data" (Dec 2025, 1 p.) | https://www.clevelandfed.org/-/media/project/clevelandfedtenant/clevelandfedsite/indicators-and-data/median-cpi/methodological-approach-interpolating-missing-october-2025-cpi-data.pdf (saved Trimmed mean/raw/clevelandfed_interpolation_method_oct2025_2026-11-10.pdf) | [O] | g_i = (CPI_Nov/CPI_Sep)^(1/2) − 1 used for both Oct and Nov 2025 |
| Cleveland Fed usinflationdata.zip (usinflationdata.csv) | https://www.clevelandfed.org/-/media/files/webcharts/mediancpi/usinflationdata.zip | [O] | Published Oct 2026 12m: median 2.7992, 16% trimmed mean 2.8912 |
| BLS 2025 shutdown CPI FAQ | https://www.bls.gov/cpi/additional-resources/2025-federal-government-shutdown-impact-cpi-faq.htm | not opened (cited by coordinator) | Geometric-mean approximation for seasonal adjustment; unverified by me |
