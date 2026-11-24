# Retrieval subagent spec (shared by all source groups)

You are retrieving official U.S. inflation-indicator data for a student research project. The manager (another agent) consolidates your outputs into the final workbook. You retrieve and normalize; you do NOT build the workbook or compute derived rates.

## Hard rules
1. Retrieve only the exact publisher-defined series assigned to you. Never substitute a nearby measure or construct an aggregate. If an exact series is unavailable, record it as N/A in metadata with the best official link and the reason.
2. Use the originating publisher's API or official download. Use FRED only for discovery, cross-checking, and ALFRED first-release dates, unless the originator has no usable access (then record the originator's attribution and link). Exception: St. Louis Fed breakeven series (T5YIE, T10YIE, T5YIFR) are published by the St. Louis Fed, so the FRED API is the originating source.
3. Coverage: January 2000 through the latest observation. If a series begins later, take its earliest date and record that. Keep native frequency (daily, monthly, quarterly). No interpolation, no carry-forward, no frequency conversion.
4. Rates: capture every publisher-reported rate verbatim (e.g., 1-month annualized, 12-month percent change, 3-month percent change at annual rate). Record exactly what the publisher calls it. Do NOT compute any rate yourself. Also capture index levels when published (SA and NSA, where both exist).
5. Missing observations: keep the date with an empty value and a note (e.g., BLS reports that Oct and Nov 2025 CPI were not collected because of the 2025 appropriations lapse). Never fill them.
6. API keys: they are in env vars BEA_API_KEY, BLS_API_KEY, FRED_API_KEY. Never print them, never write them to any file, never hard-code them. Use `inflation_data/code/fetch_utils.py` (`get_key`, `http_get`, `http_post_json`, `save_raw`, `fred_initial_release`). Always save payloads with `save_raw`, which redacts keys.
7. Write ONLY inside `inflation_data/raw/<group>/`, `inflation_data/processed/<group>/`, and your own script `inflation_data/code/retrieve_<group>.py`. Do not edit other files.
8. Check pagination and completeness: compare observation counts with any count the API reports, and confirm the latest observation matches the publisher's latest release.
9. No long narration. No raw data dumps in your final message.

## Raw files
Filenames: `<publisher>_<dataset-or-series>_<YYYY-MM-DD retrieval date>.<ext>` (e.g., `bls_api_CPI_2000-2019_2026-09-26.json`). Save unmodified publisher payloads (except key redaction).

## Processed outputs (exact schema; CSV, UTF-8, header row)

### `processed/<group>/observations.csv` (long format, one row per series per date per measure)
| column | meaning |
|---|---|
| series_key | stable snake_case key you assign, e.g. `cpi_u_core` |
| publisher_series_id | exact ID/line code, e.g. `CUSR0000SA0L1E`, or `BEA U20404 line 25` |
| date | ISO date. Monthly `YYYY-MM-01`; quarterly = first day of quarter; daily = actual date; SPF = survey quarter start date |
| frequency | `D`, `M`, `Q` |
| value | numeric as published; empty if missing |
| value_type | `index_level`, `published_rate`, `expectation`, `forecast`, `breakeven` |
| measure_label | exact publisher label, e.g. `12-month percent change, NSA`, `1-month annualized percent change`, `median 1-year-ahead expected inflation` |
| horizon | for rates: `MoM`, `3m_ann`, `6m_ann`, `12m`, or `other:<exact description>`; for expectations/forecasts: exact horizon text; for index levels: `level` |
| seasonal_adjustment | `SA`, `NSA`, or `not applicable` |
| raw_file | path of the raw file this came from (relative to project root) |
| note | missing-value reason, preliminary flag, break, etc. |

### `processed/<group>/series_metadata.csv` (one row per series_key)
series_key, indicator (the plain name from your assignment), publisher, exact_title, publisher_series_id, table_or_dataset, definition, frequency, units, seasonal_adjustment, geography_population, earliest_obs, latest_obs, latest_release_date, source_url, api_endpoint (without key), raw_files, retrieval_date, published_rate_horizons (list), fred_equivalent_id (for cross-check / ALFRED; blank if none), revision_vintage_notes, status (`retrieved` / `N/A`), notes.

### `processed/<group>/release_dates.csv`
series_key, date, first_release_date, method (`ALFRED output_type=4 <FRED id>` or `publisher calendar <url>`), note. Cover at least the latest 13 observations per monthly/quarterly series. For daily series, write one row per series stating the publication convention instead.

### `processed/<group>/REPORT.md`
Concise: series retrieved (key, ID, date range, count), N/A items with reason and link, verification performed (IDs/titles checked against which publisher page), cross-checks against FRED (latest 3 values match? list differences), unresolved issues. Max ~60 lines.

## Final message
Return a <=15-line summary: counts retrieved, N/A list, any issue the manager must decide. Everything else goes in REPORT.md.
