# Data

Two kinds of data live here:

- **`pipelines/`**: **recurring** data that gets rerun on each release. Each pipeline is self-contained: `code/` (scripts), `raw/` (publisher files, never edited), `processed/` (normalized CSVs plus metadata), `archive/` (older vintages), and an output workbook.
- **`Raw/`**: **one-off** raw series behind numbers in a research subtask (`02_Research/Subtasks/`). Named `<source>_<series>_<YYYY-MM-DD>.csv`. Never edited.

**Rule:** a new release means rerunning the pipeline script, not rebuilding by hand. A one-off analysis that turns out to need rerunning gets promoted into a pipeline.

Run scripts from the project root, e.g. `python3 "03_Data/pipelines/inflation_data/code/retrieve_bls.py"`. API keys load from `.env`. Never commit keys.

## Pipelines

Folder names are kept from Round 1 because the scripts store raw-file paths that include them. Renaming is planned for the post-challenge GitHub cleanup.

| Folder | What it is | Output |
|---|---|---|
| `inflation_data/` | Inflation indicators and expectations: CPI, PCE, PPI, sticky and trimmed measures, ECI, productivity/ULC, survey and market expectations (BLS, BEA, regional Feds, Michigan, FRED/ALFRED) | `inflation_indicators.xlsx` |
| `Price indexes/` | Component-level price baskets: CPI/PCE/PPI components, breadth (149-item core PCE), sector contributions, CPI–PCE reconciliation, market-based PCE, harmonized PCE (core ex OER) | `Price_Basket_Findings.xlsx` (Eli hand-edits it; update sheets via `replace_sheets.py`, never regenerate it whole) |
| `demand_data/` | 34 demand and AI-investment indicators: real consumption, income, saving, sentiment, investment, data-center construction, hyperscaler capex (SEC filings) | `demand_signals.xlsx` |
| `forecast_3b/` | Slide 3B core PCE scenario forecast: SPF median baseline + oil-gap adjustment through the FEDS oil note's Fig. 2 response, 3 oil paths x 2 regimes, through 2027Q4 (added Nov 15) | `processed/scenario_grid_<spf>.csv` (+ fan, metadata); workbook `01_Finals/data/Slide3B_Inflation_Data.xlsx` via `02_Research/Subtasks/12_slide3b_research/code/build_slide3b_workbook.py` |

## Release → what to run

This map is from the scripts' own docstrings. It has not been run end to end since the Nov 8 move. Confirm on first use.

| Release | Pipeline: scripts, in order |
|---|---|
| CPI, PPI, ECI, productivity (BLS) | `inflation_data`: `retrieve_bls.py` → `build_workbook.py` → `audit_workbook.py`. `Price indexes`: `retrieve_bls_baskets.py` → `analyze_baskets.py` → `build_basket_workbook.py` → `replace_sheets.py` |
| PCE / personal income (BEA) | `inflation_data`: `retrieve_bea.py` → `build_workbook.py` → `audit_workbook.py`. `Price indexes`: `retrieve_bea_baskets.py`, `rebuild_market_based.py`, `core_ex_oer.py` (harmonized PCE), `sector_contributions.py` → `analyze_baskets.py` → `build_basket_workbook.py` → `replace_sheets.py`. `demand_data`: `retrieve_official.py` → `build_demand_signals.py` |
| Fed measures, expectations (Cleveland/Atlanta/Dallas/NY Fed, Michigan, breakevens) | `inflation_data`: `retrieve_fed_expectations.py` → `supplement_fed_expectations.py` → `build_workbook.py` → `audit_workbook.py` |
| Expectations aggregate (13 one-year measures, Logan-style) | `inflation_data`: re-download changed files into `raw/expectations_aggregate/` (bump `RAW_DATE`), then `build_expectations_aggregate.py` → `Inflation_Expectations.xlsx`. Rerun on Q4 SPF and the Oct NY Fed SME |
| SPF (quarterly), EIA STEO (monthly), EIA Brent daily | `forecast_3b`: `fetch_inputs.py` → `forecast.py --spf <YYYYQn>` (add `--compare` once two surveys are present) → `tests/test_zero_gap.py --spf <YYYYQn>`; then `02_Research/Subtasks/12_slide3b_research/code/build_slide3b_workbook.py --spf=<YYYYQn> --verify`. Rerun on Q4 SPF and on Nov 18 (EIA Brent). See `forecast_3b/README.md` |
| Census retail sales, construction; Conference Board; company capex | `demand_data`: `retrieve_official.py` / `retrieve_research.py` → `supplement_research.py` → `build_demand_signals.py` |

## Known state (Nov 8, 2026)
- All raw-file references resolve after the move: inflation 166,645, price baskets 12,706, demand 237. Twelve Oct 2 Conference Board rows in `demand_data` store paths relative to the pipeline folder, not its parent. The files exist; the convention is just inconsistent.
- **Reconciled Nov 10:** `audit_workbook.py` reports 0 mismatches. The Oct 1–2 hand edits now come from the scripts: the Dallas revision note, the harmonized-PCE (core ex OER) row (read from `Price indexes/.../core_pce_ex_oer_<date>.csv`, 2017 = 100), and the release-date rule. The rebuild changed no numbers. The breakeven daily rows for Sep 28–Oct 1 drop out until the next `retrieve_fed_expectations.py` run. Pre-reconcile workbook, processed files and code: `inflation_data/archive/pre_reconcile_2026-11-10/`.
- **Release-date rule:** for revised series, "Release date" is the release the shown vintage comes from. The first-release date is added to Notes when it differs. Surveys (SPF, NY Fed SCE, Michigan) and daily breakevens keep their own release date.
- Order matters on a BEA release: run `Price indexes/code/core_ex_oer.py` on the new vintage **before** `build_workbook.py`. The build flags a mismatch if the derived series ends in a different month than core PCE.

- **Refreshed Nov 10 (all three pipelines; Codex-audited).** Archives: each pipeline's `archive/pre_refresh_2026-11-10/`.
- **Michigan preliminary months:** both pipelines append the latest "(P)" month from the publisher's current tables. It is flagged PRELIMINARY in its notes and replaced by the final reading on the next run after the final release.
- **Oct CPI:** BLS publishes no Oct 2026 12m change. `Price indexes` writes separate files: `*_2026-10_short_horizon*` (1m/3m) and `*_2026-10_approx_interp_oct2025_base*` (approx. 12m, Oct 2025 = √(Sep × Nov 2025), NSA). The official CPI basket stays at Sep. 11/13-month changes are sensitivity comparisons, not bounds.
- **Baskets workbook:** update it via `replace_sheets.py` only. The script now also appends new sheets. The build writes `Price_Basket_Findings_build_<date>.xlsx`, never the live file.

## Release calendar to Nov 18
Known: Oct CPI Nov 10 (in). Oct PPI Nov 13. Q4 SPF mid-Nov. Michigan Nov final Nov 20 and Oct PCE Nov 25 (both after the cutoff).
