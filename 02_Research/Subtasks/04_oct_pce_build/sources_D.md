# Sources D: every input read by the D_ scripts (all local; nothing downloaded)

| File | Note |
|---|---|
| `02_Research/Subtasks/04_oct_pce_build/outputs/component_mapping.csv` | 224 pricing lines: leaf, sub-line, in_core, BEA seasonal status, series, blend inputs (agent A, approved at Checkpoint B) |
| `.../outputs/component_series_history.csv` | CPI/PPI levels Jan 2015 – Oct 2026 (CPI) / Sep 2026 (PPI), BLS API pulled 2026-11-11, current vintage |
| `.../outputs/ppi_first_release.csv` | First-release m/m for 20 of 28 PPI series, ref months Dec 2024 – Sep 2026 (ALFRED) |
| `.../outputs/pce_first_prints.csv` | Target: BEA first-print core/headline m/m, same-vintage levels, Jan 2024 – Sep 2026 |
| `.../outputs/cleveland_nowcast_history.csv` | Benchmark 3, last nowcast before each PCE release, Jan 2024 – Sep 2026 |
| `.../outputs/C_cleveland_nowcast_long_mm.csv` | Cleveland daily nowcasts back to 2013 (used for Oct 2023) |
| `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` | BEA price indexes, all lines, 2017M01–2026M09, current vintage |
| `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json` | BEA nominal spending, all lines (weights; not real time) |
| `03_Data/Raw/ALFRED_PCEPILFE_all_vintages_2026-11-11.json` | Core PCE all vintages: Oct 2023 first print; base levels and first-print rates for D_build |
| `03_Data/Raw/ALFRED_PCEPI_all_vintages_2026-11-11.json` | Headline PCE all vintages, same uses |
| `03_Data/Raw/ALFRED_CPILFESL_all_vintages_2026-11-11.json` | Core CPI current vintage for benchmark 2 |
| `.../outputs/source_table_changes.csv` and `03_Data/Raw/BEA_Table244UD_*` (read via the change file) | Which lines changed source between table versions (method by month) |
| `03_Data/pipelines/Price indexes/CPI/raw/bls_cpi_relative_importance_2025_2026-11-10.xlsx` | Checked for blend RI: no smartphone RI (line 285 fitted); RI weights for 87/95 already in the mapping |
| `03_Data/pipelines/inflation_data/raw/policy_context/` (listing only) | Confirmed no policy-rate change dates saved (FEDTAR* are SEP projections) |
| `02_Research/Subtasks/04_oct_pce_build/stress_test.md`, `report.md`, `WHERE_WE_ARE.md` | Background and locked decisions |
| `.../outputs/A_hierarchy.csv`, `A_parent_leaves.csv` | Hierarchy (net-travel gross components for the identity diagnostic), sub-line structure |
