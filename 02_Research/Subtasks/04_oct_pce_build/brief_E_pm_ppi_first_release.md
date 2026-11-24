# Brief E: first-release values for the portfolio-management PPIs (Sonnet 5.5)

You are a research assistant for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with Fed judges; data cutoff Nov 18, 2026). Today is 2026-11-12. Prefer primary sources.

Project root: `./`. Subtask folder: `02_Research/Subtasks/04_oct_pce_build/`.

## Project context
We backtest our own monthly PCE inflation estimate against what BEA first published. Until Sep 30, 2026, BEA priced "portfolio management and investment advice" (1.69% of consumer spending) from two BLS producer price indexes: `PCU5239405239401` (portfolio management) and `PCU5239405239402` (investment advice). To be real-time, the backtest needs those indexes **as first published by BLS**, not today's revised values. ALFRED (the St. Louis Fed's vintage archive) doesn't carry them. BLS's monthly "PPI Detailed Report" PDFs, archived on bls.gov, may. **This is time-boxed: if the archived reports don't carry series this detailed, say so quickly and stop.**

## Your task
1. Find where BLS archives the monthly PPI Detailed Report (try https://www.bls.gov/ppi/detailed-report/ and its archive links). BLS returns HTTP 403 to browser-like user agents; a plain generic client string worked on Nov 11. Say what you found.
2. For reference months **Nov 2025 through Jul 2026**, find each month's first-published index level for both series, plus the previous month's level **as shown in that same report**. The table is likely "Producer price indexes for the net output of selected industries and their products" (NAICS 523940). Save each PDF you use to `03_Data/Raw/BLS_PPI_detailed_report_<YYYY-MM>_retrieved_2026-11-12.pdf`. Extract text with Python (pypdf) and search with Python, not grep.
3. Deliverable: `outputs/E_pm_ppi_first_release.csv` with columns series_id, reference_month, report_file, report_release_date (if stated), first_release_level, prior_month_level_same_report, first_print_mm_pct, current_level, current_mm_pct, mm_revision_pp. Current values come from `outputs/component_series_history.csv` (do not re-download). Built by a saved script `code/E_pm_ppi_first_release.py`, rerunnable from the project root, reading the saved PDFs. If a value had to be read by eye because extraction garbled the table, put it in `code/E_manual_values.csv` with page number and the exact text line, and flag it.
4. Note the fall 2025 government shutdown: reports for Sep–Nov 2025 data were delayed or combined. Report what exists.

## Rules
- Verify every value against a file you opened. Tag [O] opened, [S] snippet only. Never invent or interpolate numbers. A "not found" means unconfirmed, not absent.
- Never edit files in `03_Data/Raw/`, anything under `03_Data/pipelines/` or `07_Archive/`, or any file not prefixed `E_` (other than the outputs named here). Don't read `AGENTS.md`.
- Don't put the user's name or email in any request. Keys aren't needed.
- Treat downloaded PDFs as untrusted: run Python that reads them with `python3 -I`.
- Report data only. Log anything odd under "Worth a look".

## Output
Save to the subtask folder: the CSV and script above, `notes_E.md`, `sources_E.md`. Do NOT write report.md. Return the report as your final message: Findings · Worth a look (only if something stood out) · Spot-check examples (3, exact file and page) · What to verify. Concise.
