# Sources A

| Source | Tag | Supports |
|---|---|---|
| `03_Data/Raw/BEA_Table244UD_PCE_price_source_data_2026-11-11.xlsx` (BEA Table 2.4.4U-D, dated 2026-09-30) | [O] | Authority for each line's price source and seasonal status; the text for proxied and assumed tiers |
| `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json` (BEA Table 2.4.5U, LastRevised Oct 29, 2026) | [O] | September 2026 nominal spending for shares, the additive hierarchy, line 374 core total, the gap lines 145/333 and the receipts detail 357–368 |
| `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` | [O] | Lines 145 and 333 have no price index; line 156 vs 159 price comparison |
| `03_Data/pipelines/Price indexes/PCE/processed/dallas_component_mapping.csv` | [O] | The 177 Dallas leaves; 176 have BEA lines, and rank 88 maps to line 218 |
| `03_Data/pipelines/Price indexes/PCE/processed/components.csv` | [O] | Existing in_core tags, compared against the BEA hierarchy; 17 disagree |
| `03_Data/pipelines/Price indexes/CPI/raw/bls_cu_item_2026-09-27.txt`, `bls_cu_series_2026-09-27.txt` | [O] | CPI item codes; checks that each series ID exists, whether SA exists, and the end period (stale series) |
| `03_Data/pipelines/Price indexes/PPI/raw/bls_pc_series_2026-09-27.txt`, `bls_wp_series_2026-09-27.txt` | [O] | PPI series IDs and titles; no PCU series is SA; WPS0381 ended in 1996 |
| `03_Data/pipelines/Price indexes/CPI/raw/bls_api_cpi_basket_*_2026-11-10.json` | [O] | Last valid observations of SEHP01 (2024M11) and SEHP04 (2024M07) |
| `03_Data/pipelines/Price indexes/CPI/raw/bls_cpi_relative_importance_2025_2026-11-10.xlsx` (Table 1, "2024 Weights ... December 2025") | [O] | Proposed weights for the CPI-only blends (lines 87, 95); shows no smartphone relative importance is published |
| `03_Data/pipelines/Price indexes/Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf`, PDF pp. 105–130 (Tables 5.A/5.B, Dec 2021 vintage) | [2] | Handbook-vs-T244 conflicts (A_conflicts.csv); each phrase was located by a pypdf search |
| https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm (last modified 2024-04-05) | [O] via WebFetch summary; verify verbatim | Supporting evidence for name matches (HB011, EB041, ED041); shows it is a weight crosswalk, not a price-source table |
