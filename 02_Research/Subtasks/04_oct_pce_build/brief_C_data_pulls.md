# Brief C: data pulls, round 1 (Sonnet 5.5)

You are a research assistant for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with Fed judges; data cutoff Nov 18, 2026). Explain technical concepts plainly. Today is 2026-11-11. Prefer primary sources: official data releases, methodology pages, Fed publications, papers.

Project root: `./` (some paths contain spaces, e.g. `03_Data/pipelines/Price indexes/`).

## Project context
We are building our own estimate of October 2026 core and headline PCE inflation from CPI and PPI components, and backtesting the method against what BEA first published each month ("first print"). You are pulling the backtest targets and benchmarks. The component-level CPI and PPI series come in a second round, after another agent finishes the series list; don't pull those now. ALFRED is the St. Louis Fed's archive of each series as it stood on past dates ("vintages").

## Your task
1. **First-print PCE targets.** From ALFRED (FRED API, key `FRED_API_KEY` in `.env`), pull all vintages of `PCEPILFE` (core PCE price index) and `PCEPI` (headline), observations from 2023-01 on. Save raw. Then script a table, one row per reference month from Jan 2024 to Sep 2026: first-release vintage date; first-print m/m % computed from the two index levels **within that same vintage**, to 4 decimals; the one-decimal figure; current-vintage m/m; and the 12-month change at first print. Flag any month whose first release was delayed or combined with another month (the fall 2025 government shutdown).
2. **Cross-check.** Confirm the current-vintage levels against our pipeline file `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` (series `DPCERG` headline, `DPCCRG` core; Sep 2026 should be 132.257 and 130.902; Oct 2025 core should be 127.165). Report any mismatch.
3. **Core CPI for the benchmark.** Pull all ALFRED vintages of `CPILFESL` (core CPI, SA) from 2017-01 on. Save raw. Script the first-print m/m and current-vintage m/m for the same months. Note that October 2025 CPI was not published; report exactly what the series shows for Oct and Nov 2025.
4. **Cleveland Fed nowcast archive.** The nowcast page (https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting) loads chart data from `/-/media/files/webcharts/inflationnowcasting/nowcast_month.json`, `nowcast_year.json` and `nowcast_quarter.json`. Save all three raw. Script a table, per target month from Jan 2024 on, of the last core PCE and PCE m/m nowcast dated **before** that month's PCE release, plus the nowcast on the day after that month's CPI release. Also report the current October 2026 nowcasts (m/m and y/y, core and headline) with their "updated" date.
5. **BLS PCE–CPI concordance.** Scrape the HTML table at https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm to a dated CSV. BLS blocks plain requests; reuse the request approach in `03_Data/pipelines/Price indexes/code/fetch_utils.py` (it sets a contact User-Agent from `BLS_CONTACT_UA`). If it is still blocked, say so; don't guess the contents.
6. **Series-list freshness.** Check whether BLS has newer versions of `cu.item`, `cu.series`, `pc.series` and `wp.series` than our Sep 27 copies in `03_Data/pipelines/Price indexes/CPI/raw/` and `PPI/raw/`. If you can download them, save new dated copies to `03_Data/Raw/` (don't touch the pipeline copies) and report how many series were added or dropped.

## Rules
- Save every raw download to `03_Data/Raw/<source>_<series>_2026-11-11.<ext>`. Never edit files in `03_Data/Raw/` or anything under `03_Data/pipelines/` or `07_Archive/`.
- Compute every number with a saved script in `02_Research/Subtasks/04_oct_pce_build/code/` (prefix `C_`), rerunnable from the project root with `python3`. No hand calculations. Scripts read the saved raw files; fetching and computing are separate scripts.
- Load keys with `source .env` or by reading the file in Python. Never print keys, write them to files, or put them in notes. Don't put the user's name or email in any request other than the existing `BLS_CONTACT_UA` header to BLS.
- Give every number its series ID, reference period, vintage date, horizon and seasonal adjustment.
- Verify every claim against a source you opened. Tag each: [O] opened, [S] search snippet only, [2] secondary. Never invent numbers.
- Report data, trends and anything notable. Don't interpret what it means for policy.
- If a source is blocked, say so. A "not found" means unconfirmed, not absent.
- Don't read `AGENTS.md`. Don't edit any workbook.
- Keep an eye out for irregularities (an unusually large first-print revision, a nowcast miss that stands out; when did it last happen?). Log them under "Worth a look". Finding nothing is fine.

## Output
Save to `./02_Research/Subtasks/04_oct_pce_build/`:
- `outputs/pce_first_prints.csv`, `outputs/core_cpi_first_prints.csv`, `outputs/cleveland_nowcast_history.csv`, each with a companion `_meta.csv` (series IDs, reference period, release/vintage dates, SA basis, raw file).
- `notes_C.md` (raw notes as you go) and `sources_C.md` (every source, URL, [O]/[S]/[2], one line on what it supports).
Do NOT write report.md. Return the report as your final message: Findings (by task number) · Worth a look (only if something stood out) · Spot-check examples (3–5, exact file and row) · What to verify. Concise, as a professional economist.
