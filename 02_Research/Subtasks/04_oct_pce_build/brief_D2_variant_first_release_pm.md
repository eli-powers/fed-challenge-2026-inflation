# Brief D2: backtest variant with first-release portfolio-management PPIs (Opus 5.5)

You are a research collaborator for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with Fed judges; data cutoff Nov 18, 2026). Today is 2026-11-12.

Project root: `./`. Subtask folder: `02_Research/Subtasks/04_oct_pce_build/` (`SUB/`).

## Project context
We built a bottom-up estimate of monthly core and headline PCE inflation from CPI and PPI components and backtested it against BEA's first-published numbers for Dec 2025 – Sep 2026 under rules locked before results. The backtest code is `SUB/code/D_common.py`, `D_backtest.py` and related `D_` scripts (written by an earlier agent; read `SUB/brief_D_methods_backtest.md`, `SUB/notes_D.md` and `SUB/code/README.md` first). In the months before BEA changed methods (prints for Dec 2025 – Jul 2026), BEA priced portfolio management (BEA line 268, 1.69% of consumer spending) from two producer price indexes. The main run had to use today's revised values of those two indexes because first-release values weren't available. They have now been recovered from BLS's archived reports. Your job is one labeled variant run that swaps them in.

**A Codex audit is running and every existing file in the subtask folder is frozen. Do NOT modify, rewrite, or regenerate ANY existing file** (no edits to `D_common.py`, `D_backtest.py`, `README.md`, `notes_D.md`, or any existing output CSV; do not rerun `D_backtest.py` or any script that writes existing outputs). Create NEW files only, all prefixed `D2_`. If you can't do the task without touching an existing file, stop and say so.

## Input
`SUB/outputs/E_pm_ppi_first_release.csv`: series_id (`PCU5239405239401`, `PCU5239405239402`), reference_month (2025-11 … 2026-07), first_release_level, prior_month_level_same_report, first_print_mm_pct, current values. Use `first_print_mm_pct` (the change computed within a single BLS report) as the real-time monthly change.

## Your task
1. Variant run "first-release portfolio-management PPIs": identical to the main run in every respect (same months, the same 12-month carry-forward window with no re-selection, same weights, seasonal treatment, the same fitted blend weights for old line 268, same benchmarks), except that in the old-table months (Nov 2025, and Dec 2025 – Jul 2026) line 268 is priced from the first-release monthly changes of the two PPIs instead of the revised ones. Implement it in `SUB/code/D2_variant_first_release_pm.py`, importing from the existing `D_` modules without changing them (subclass or patch in memory). First confirm that your harness, with the swap switched off, reproduces the main run's monthly core estimates in `SUB/outputs/backtest_results.csv` to 4 decimals; report the largest difference. If it doesn't reproduce, stop and report.
2. Output `SUB/outputs/D2_backtest_variant_first_release_pm.csv` with a `_meta.csv`: per month, core and headline estimate under the main run and the variant, the first print, both misses; and a summary block with n, bias, MAE, SE of MAE (SD of |miss| / √n), MAE ± 1 SE range, RMSE, largest miss, 1-decimal hit rate for both, plus the MAE difference. Rule months are Dec 2025 – Sep 2026 (n = 10); show Nov 2025 separately.
3. State which PPIs are still priced from revised data in the variant (expected: the five `PCU523150…` series and `PCU5132105132107`) and how many rule months each affects, with the weight of the lines they feed.
4. Notes go in a new `SUB/notes_D2.md`.

## Rules
- No tuning. No change to any locked rule. List every judgment call.
- Every number from the saved script, rerunnable from the project root with `python3`. No downloads.
- Never edit anything under `03_Data/` or `07_Archive/`. Don't read `AGENTS.md`.
- Do not report any October 2026 estimate.

## Output
Return a short report as your final message: reproduction check · summary table · per-month core estimates side by side · the threshold-leg reading of the variant under the locked rule (MAE ± 1 SE entirely below 0.05 = pass; includes 0.05 = inconclusive; entirely above = fail) · remaining revised-data PPIs · judgment calls · 3 spot-check rows.
