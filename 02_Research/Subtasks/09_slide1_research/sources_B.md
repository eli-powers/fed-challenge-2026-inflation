# Agent B sources

Tags: [O] opened and checked by script or read; [S] search snippet only; [2] secondary. This task used no web sources; everything was already on disk.

## Data (raw, never edited)
- [O] BEA NIUnderlyingDetail **U20404** (PCE price indexes, Fisher, 2017=100, SA), LastRevised Oct 29 2026, retrieved Nov 10 2026: `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json`.
- [O] BEA NIUnderlyingDetail **U20405** (PCE current dollars, $mn SAAR), same vintage: `.../PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json`.
- [O] BEA NIUnderlyingDetail **U90100** (Table 9.1U, reconciliation of CPI and PCE percent change, monthly, SA at monthly rates), LastRevised Oct 29 2026, retrieved Nov 10 2026: `.../Cross-index analysis/raw/BEA_NIUnderlyingDetail_U90100_2026-11-10.json`. Its months run to 2026M09. The 2025M10 and 2025M11 cells are absent from the payload.
- [O] BLS CPI-U item indexes (SA CUSR / NSA CUUR), API pulls of Nov 10 2026, which include the Oct 2026 CPI: `.../CPI/raw/bls_api_cpi_basket_2017_2026_batch1-7_2026-11-10.json`.
  - Supplemented, never overriding, by `03_Data/Raw/bls_api_components_2015_2026_batch1-6_2026-11-13.json`. These add parent indexes SAA1, SAA2, SEGD, SEHJ, SEMD, SERA, SERC, SERF, SETD, SEGA and SEAE, plus SEHB01, SEEB04 and others.
  - Oct 2025 values are "-" with footnote X: "Data unavailable due to the 2025 lapse in appropriations" [O].
- [O] BLS CPI relative importance, Table 1: Dec 2024 (2023 weights) `.../CPI/raw/bls_cpi_relative_importance_2024_2026-11-10.xlsx` and Dec 2025 (2024 weights) `..._2025_2026-11-10.xlsx`. Both tables have the same 294 rows and 204 leaves.
- [O] BLS cu.item flat file: `03_Data/Raw/bls_cu_item_2026-11-11.txt`, used to map names to codes.
- [O] BLS PCE–CPI code mapping (ELI → PCE series), "Last Modified Date: April 5, 2024": HTML `03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.html`, parsed CSV `..._2026-11-11.csv`. Source: https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm (saved by `04_oct_pce_build`).
  - Rows used: TF011/TF012 → N/A; HP021 → N/A; HP043 → N/A; ME011–ME041 → DMINRC; HD011 → DFINRC; HB011 → DSCHRC; GD051/GD052 → DFEERC/DTAPRC; MC041 → home health, labs, other professional, specialty outpatient; MD031/GD061 → individual and family services; TG011 → air transportation and foreign passenger fares; FX011 → alcohol in purchased meals.

## Project-derived inputs (read only)
- [O] `02_Research/Subtasks/04_oct_pce_build/outputs/A_hierarchy.csv`: the U20404 line hierarchy (parent, number of children).
- [O] `.../04_oct_pce_build/outputs/D_build_2026-10_lines.csv` and `D_build_2026-10_summary.csv`: Oct 2026 PCE estimate (first-release variant). Core index 131.28826, 12m 3.24245%, 3m ann. 3.55082%, m/m 0.29507%; headline index 132.67741.
- [O] `03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx`:
  - "CPI Oct 2026 views": core 12m NSA approx. 2.8149% on the interpolated base; core 3m ann. SA 3.7464%.
  - "Summary": note on the Sept 30 revision shrinking the gap; PM + software ≈ +0.25 pp.
  - "Hypothesis analysis": 9.1U sums.

## Methodology text
- [O] BEA NIPA Handbook (whole handbook, saved as "Chapter 5"), `.../Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf`, extracted with pypdf:
  - PDF p.56: CPI definition. It covers "out-of-pocket" expenditures and excludes investment items such as stocks, bonds and life insurance.
  - PDF p.96 (ch.5 p.5-2): PCE includes expenditures financed by third-party payers, such as employer-paid health insurance and government programs.
  - PDF p.117 (Table 5.B line 74): air transportation is priced with the "PPI for domestic scheduled passenger air transportation".
  - PDF p.123: portfolio management is priced with a fixed-weighted average of the PPIs for portfolio management and investment advice.
  - The Handbook does **not** describe the Table 9.1U methodology. A search for "formula effect", "weight effect" and "reconcil" found nothing relevant, so BEA's exact item-level shares and scope splits are **unverified**. Our convention was inferred from the 9.1U values themselves (see notes_B.md, Method).

## Cross-check reading
- [O] `02_Research/External_views/Fed_officials_2026-11/summary.md` and `speeches/` (Bowman, Logan, Paulson, Waller and others, Nov 10–14). None discusses the CPI–PCE gap.
- [O] `02_Research/External_views/Previous_Finalists_copy/`: 2025 transcripts (Harvard, Chicago and others), 2023–2025 Fed transcripts (PDF), and the 2025 markdown logs. No CPI–PCE reconciliation in any of them.

## Paywalled
None.
