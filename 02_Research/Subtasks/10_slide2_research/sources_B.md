# Sources: Agent B (Q4–Q7), 2026-11-15

**Tags:** [O] opened, [S] search snippet only, [2] secondary.

## Existing project files used (cited, not re-downloaded)

**BEA**
- `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` [O]: prices. Data to Sep 2026, SA.
- `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json` [O]: nominal spending.
- `03_Data/Raw/BEA_PIO_october-and-november-2025_page_retrieved_2026-11-11.html` [O]: BEA's note on imputing the missing October 2025 CPIs (CPIs only).
- `03_Data/Raw/BEA_PIO_additional_information_retrieved_2026-11-11.html` [O]: definitions only; no imputation text.

**BLS**
- `03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv` [O]: BLS concordance from CPI item code (ELI) to PCE series code, 404 rows.
- `03_Data/Raw/BLS_PPI_detailed_report_2025-11_retrieved_2026-11-12.pdf` [O]: shutdown box, p. 6. Oct 2025 hospital and Medicare inpatient tables.

**ALFRED**
- `03_Data/Raw/ALFRED_PCU622622_all_vintages_from2024-11_2026-11-11.json` [O]: Oct 2025 first-release vintage is 2026-01-14.

**Atlanta Fed**
- `03_Data/pipelines/Price indexes/Sticky CPI/raw/atlantafed_sticky_price_cpi_2026-11-10.xlsx` [O]: aggregate indexes only, no component classification.

**CPI component pipeline**
- `03_Data/pipelines/Price indexes/CPI/processed/components.csv` [O]: Sep 2026, published.
- `components_2026-10_approx_interp_oct2025_base.csv` [O]: Oct 2026 12m is approximate; the Oct 2025 base is the square root of Sep 2025 × Nov 2025 CPI, NSA.
- `components_2026-10_short_horizon.csv` [O]: Oct 2026 3m, published. Matches the approximate file's 3m column exactly; the script asserts this.

**Audited engine and outputs**
- `02_Research/Subtasks/09_slide1_research/code/C_common.py` [O]: imported read-only.
- `09_slide1_research/outputs/C_breadth.csv`, `C_breadth_ts.csv`, `C_waller_variants.csv`, `C_hospital_lines.csv` [O].
- `02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv`, `component_mapping.csv`, `A_hierarchy.csv` [O].
- `01_Finals/data/Slide1_Inflation_Data.xlsx`, tab R6_breadth, rows 60–68 [O]: formula cells have no cached values; labels read.

**Cross-checks**
- `02_Research/External_views/Fed_officials_2026-11/summary.md` [O]: Waller quote; Daly reported via Kitco [2].
- `02_Research/External_views/Previous_Finalists_copy/` [O]: md files and PDF transcripts searched with Python.

## New downloads (2026-11-15)

**`03_Data/Raw/BLS_PPI_hospitals_2026-11-15/`**
- Files: `bls_api_ppi_hospitals_2006_2015.json` and `bls_api_ppi_hospitals_2016_2026.json`.
- Source: BLS API v2 with catalog [O].
- Series: PCU622---622---, PCU6221--6221--, WPU5121010111, WPU51210101, WPU511104. All NSA. Oct 2026 values are preliminary (code P).

**`03_Data/Raw/AtlantaFed_sticky_classification_2026-11-15/`**
- `ClevelandFed_EC201002_page_retrieved_2026-11-15.html` [O]: Bryan & Meyer (2010), "Are Some Prices in the CPI More Forward Looking Than Others? We Think So," Economic Commentary 2010-02, Table 1 (45 groups). From https://www.clevelandfed.org/publications/economic-commentary/2010/ec-201002-are-some-prices-in-the-cpi-more-forward-looking-than-others-we-think-so
- `ClevelandFed_EC201002_Bryan_Meyer_2010.pdf` [O]: PDF of the same commentary. Saved; the table was taken from the HTML text.

**`03_Data/Raw/BLS_shutdown_notices_2026-11-15/`**: empty. curl got 403; see `outputs/B_paywalled.csv`.

## Web pages read

- https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm [O, via WebFetch]: the Oct 2025 PPI news release was canceled and the October data were published with November on Jan 14, 2026. Also says October 2025 CPI could not be collected.
- https://www.atlantafed.org/research-and-data/data/sticky-price-cpi/explainer [O, via WebFetch]: the classification follows Bryan & Meyer (2010) and the table is an image.
- FY2026 Medicare inpatient payment rule (IPPS): 2.6% update (3.3% market basket minus 0.7 productivity), effective Oct 1, 2025 [S]. Snippets from beckershospitalreview.com/finance/cms-finalizes-2-6-pay-bump-for-hospitals-in-2026-8-things-to-know/ and aamc.org; not opened. Unverified at primary source (CMS final rule).
