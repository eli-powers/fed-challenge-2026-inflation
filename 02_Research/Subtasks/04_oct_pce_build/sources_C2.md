# sources_C2

All retrieved 2026-11-11. Tags: [O] opened (API response read by script and inspected), [S] search snippet, [2] secondary.

- [O] BLS Public Data API v2, https://api.bls.gov/publicAPI/v2/timeseries/data/ (POST; 6 batches). Raw: `03_Data/Raw/bls_api_components_2015_2026_batch1..6_2026-11-11.json`.
- [O] BLS series lists (already in project): `03_Data/Raw/bls_cu_series_2026-11-11.txt`, `bls_pc_series_2026-11-11.txt`, `bls_wp_series_2026-11-11.txt`, `bls_cu_item_2026-11-11.txt` (used to identify old-source series).
- [O] FRED API series metadata and ALFRED all-vintage observations (output_type=1, observation_start 2024-11-01): https://api.stlouisfed.org/fred/series, /fred/series/observations, /fred/series/search. Raw: `03_Data/Raw/ALFRED_<id>_all_vintages_from2024-11_2026-11-11.json` (30 series), `FRED_<id>_seriesinfo_2026-11-11.json`.
- [O] Project files: `outputs/series_to_fetch.csv`, `source_table_changes.csv`, `component_mapping.csv`.
- No web pages were opened for this subtask. Keys were read from .env by scripts and not printed or saved.
