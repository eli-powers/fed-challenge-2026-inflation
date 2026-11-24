# code/ — October 2026 PCE bottom-up build

Run every script from the **project root** with `python3` (paths contain spaces; quote them), e.g.
`python3 "02_Research/Subtasks/04_oct_pce_build/code/D_build.py" --month 2026-10`.
Fetch scripts read keys from `.env`; nothing else touches the network.

## Full run order

| Step | Script | Network | Writes |
|---|---|---|---|
| A1 | `A_build_mapping.py` | no | `outputs/component_mapping.csv`, `weight_shares.csv`, `manual_review_list.csv`, `series_to_fetch.csv`, `A_*.csv` |
| A2 | `A_handbook_conflicts.py` | no | `outputs/A_conflicts.csv` |
| B  | `B_compare_table244ud.py`, `B_judgment_lines.py`, `B_scan_pio.py`, `B_vintage_revision_check.py` (any order) | no | `outputs/source_table_changes.csv`; others print |
| C1 | `C_fetch_alfred.py`, `C_fetch_cleveland_bls.py` | yes | raw files in `03_Data/Raw/` dated by their `DATE` constant |
| C2 | `C_pce_first_prints.py`, `C_core_cpi_first_prints.py`, `C_cleveland_nowcast_history.py`, `C_crosscheck_cleveland.py`, `C_parse_bls_concordance.py`, `C_series_list_freshness.py` (`C_alfred_lib.py` is a helper) | no | `outputs/pce_first_prints.csv`, `core_cpi_first_prints.csv`, `cleveland_nowcast_history.csv`, `C_*.csv` |
| C2-1 | `C2_fetch_bls.py` (needs `series_to_fetch.csv`) | yes | `03_Data/Raw/bls_api_components_2015_2026_batch*_<DATE>.json` |
| C2-2 | `C2_fetch_alfred.py` | yes | `03_Data/Raw/ALFRED_*_all_vintages_from2024-11_<DATE>.json` |
| C2-3 | `C2_build_history_coverage.py` | no | `outputs/component_series_history.csv`, `component_series_coverage.csv`, `C2_no_oct2026.csv` |
| C2-4 | `C2_compute_first_release_revisions.py` | no | `outputs/ppi_first_release.csv`, `C2_cpi_sa_revisions_*.csv` |
| D1 | `D_identity_test.py` (gate) | no | `outputs/identity_test.csv` |
| D2 | `D_mapping_validation.py` | no | `outputs/mapping_validation.csv` |
| D3 | `D_seasonal_tests.py` | no | `outputs/seasonal_tests.csv` |
| D4 | `D_backtest.py` | no | `outputs/backtest_results.csv`, `backtest_attribution.csv`, `backtest_lines.csv`, `backtest_window_choice.csv`, `backtest_bands.csv`, `backtest_event_check.csv`, `backtest_pm_sensitivity.csv` |
| D5 | `D_sensitivity_no_fr_ppi.py` (after D4; labeled sensitivity, not in the decision rule) | no | `outputs/backtest_sensitivity_no_first_release_ppi.csv` |
| D6 | `D_build.py --month YYYY-MM` (after D4 and D2: reads the chosen window from D4 and the band RMSE from the D2 first-release variant, Eli's decision basis) | no | `outputs/D_build_<month>_summary.csv`, `D_build_<month>_lines.csv` |

`D_common.py` is the shared engine (loaders, method versions by BEA source table, pricing, method-B seasonal factors,
blend-weight fits, carry-forward, aggregation, bands, rates). All D_ outputs carry a `_meta.csv`.

## On October PPI day (Nov 13, 2026)

`D_build.py --month 2026-10` currently stops with exit code 2 and lists the 35 PPI input rows (27 series) with no
October value. After the 8:30 AM release:

1. **Pull BLS again into new dated raw files (do not overwrite the 2026-11-11 files).** In `C2_fetch_bls.py` set
   `DATE = "2026-11-13"` and run it. If the API returns 503, retry later; it saves a batch only when complete.
2. **Rebuild the history file from the new raw files.** In `C2_build_history_coverage.py` change the glob date
   `..._2026-11-11.json` to `..._2026-11-13.json` and run it. Check `outputs/component_series_coverage.csv`: every
   PCU/WPU series should have `last_month` = 2026-10.
3. **Run the build:** `python3 "02_Research/Subtasks/04_oct_pce_build/code/D_build.py" --month 2026-10`.
   On the release day the history file's October PPI m/m (Oct first print over Sep as revised that day) is the
   first-release m/m, so `ppi_first_release.csv` does not need refreshing. (Optional: `C2_fetch_alfred.py` +
   `C2_compute_first_release_revisions.py` with updated dates, for the record.)
4. **Do not rerun `D_backtest.py` for the decision.** The decision rule was applied to the Nov 12 inputs; rerunning on
   the refreshed history changes the backtest (PPI revisions back four months, any CPI revisions). If it must be
   rerun, keep a copy of the Nov 12 `backtest_*.csv` first; `D_build.py` reads `backtest_window_choice.csv`, and
   takes the band's rule-month RMSE from the first-release variant (`D2_backtest_variant_first_release_pm.csv`; Eli,
   Nov 13), falling back to the main run in `backtest_results.csv` only if that file is absent.

Notes for the October build: `CUUR0000SEMC04` (lines 180, 181) is bimonthly; October has a value, September does not,
so the build uses the 2-month geometric change Aug→Oct (rule in `D_common.series_mm`). Portfolio management (268) is
assumed; the summary file also reports the old two-PPI value as a sensitivity once `PCU52394054…` have October values.

## Dry run (Sep 2026, as if unreleased)

`python3 "02_Research/Subtasks/04_oct_pce_build/code/D_build.py" --month 2026-09` uses BEA history through August,
the September PPI first release, and the ALFRED vintage of 2026-09-30 for the base index levels, and compares with
the 2026-10-29 first print. Its 1-month estimate equals the backtest's September row.

## Walkthrough notebook (Nov 13, 2026)

`N_make_walkthrough_notebook.py` writes `../oct2026_pce_walkthrough.ipynb`. The notebook calls this engine step by step: the component map,
one line of each type priced by hand, the October sum, the regressions, the identity test, the full backtest (on the audited
Nov 11 history, `outputs/component_series_history_2026-11-11.csv`) and the October rates. It reads saved files only and writes nothing.
