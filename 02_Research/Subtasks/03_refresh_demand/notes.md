# 03_refresh_demand: notes (2026-11-10)

STATUS: first run stopped at step 2 (hand edits found). Eli then approved a fix plan (coordinator message); fixes made, gate passed with 2 flagged Notes cells, refresh run Nov 10.

## Step 1: archive (done)
Copied raw/, processed/, code/ (minus __pycache__), demand_signals.xlsx to
`03_Data/pipelines/demand_data/archive/pre_refresh_2026-11-10/`. 189 files; originals left in place.

## Step 2: hand-edit check (FAILED, stopped)
- Made `code/build_check_copy.py` (copy of build_demand_signals.py; ROOT hard-set to the pipeline folder, outputs redirected to `tmp/`).
  Diffs vs. original: 3 lines only (ROOT; two output paths). Pipeline script not edited.
- Ran on the current processed files -> `tmp/demand_signals_rebuild_check.xlsx`, `tmp/demand_signals_table.csv`.
  `tmp/demand_signals_table.csv` is byte-identical to `processed/demand_signals_table.csv`.
- `code/compare_xlsx.py` (cell by cell): 476 cell diffs; mostly row shift from the missing sheet. `code/compare_data_rows.py` (matched by indicator): all 34 data rows identical.
- Real differences (hand edits in live workbook, not producible by build script):
  1. Sheet `TLDR` exists in live workbook (6 bullets, dated Oct 2, 2026); script has no such sheet, and its
     TLDR list is hard-coded Sept 27 text placed in the top rows of "Demand Signals".
  2. Live `Demand Signals` has the table starting at row 2 (header) vs row 9 in rebuild (no TLDR text block).
  3. `Notes & Caveats` B4 (real PCE goods example: +17.2% MoM ann. / +3.6% 3m/3m vs script -7.1% / +2.5%),
     B9 (BEA vintage: rewritten as post-annual-update, Oct 2 refresh details; script says pre-update vintage),
     B18 (gasoline: "-1.1 pp saving rate" vs script "-1.5 pp"),
     B21 (Conference Board: Sept 2026 / Aug revised / June revised / Sept 2025 rows; script lists Aug 2026, Jul, May, Aug 2025),
     B22 (latest months by source; script has older text).
- Merged-cell ranges on Demand Signals also differ (consequence of 1-2).

## Additional pipeline findings (read, not run)
- `processed/research/observations.csv` holds Conference Board rows (Sep 2025, Jun 2026, Aug 2026 revised, Sep 2026) that NO script
  produces. `retrieve_research.py` rewrites that file from scratch (only Sep 2024 PDF + whichever current-page parse succeeds + Aug 2026 fallback);
  `supplement_research.py` re-adds only Aug 2025, May 2026, Jul 2026. Running them would delete the Oct 2 rows
  (Sep 2025, Jun 2026, Aug 2026 revised, Sep 2026). Also hard-coded Aug 25 release text in the fallback; latest-page regex
  needs "Updated:" and a month phrase. Method-level issue: not changed.
- Twelve Oct 2 CB rows store raw_file relative to the pipeline folder ("raw/research/...") instead of "demand_data/raw/...". Not normalized.
- build_demand_signals.py hard-codes: Michigan raw file date "2026-09-27" (raw_mich dict), TLDR text, NOTES text; no script writes the
  TLDR sheet. `retrieve_official.py` has no hard-coded dates for retrieval but BEA call caches by TODAY filename, FRED observation_end=today.
- `retrieve_research.py` hard-codes: Microsoft FY-end/quarters logic fine; GUIDANCE URLs are Q2 2026 pages (will need Q3 call pages);
  report text strings dated. Company quarters: `quarters[-12:]`.
- Workbook currently has 34 indicators (brief says 46 series; 34 table rows, README also says 34).

## Script edits
None. (No pipeline script modified; only new files in this subtask's code/ and tmp/.)

## Files created
- demand_data/archive/pre_refresh_2026-11-10/ (copy)
- code/build_check_copy.py, code/compare_xlsx.py, code/compare_data_rows.py
- tmp/build_check_stdout.txt, tmp/demand_signals_rebuild_check.xlsx, tmp/demand_signals_table.csv


## Approved fix plan: script edits (before -> after, why)
All in 03_Data/pipelines/demand_data/code/. Original build script saved at tmp/build_demand_signals.ORIG.py.
1. supplement_research.py (rewritten, same convention): REL dict now holds Aug 2025, Sep 2025, May 2026, Jun 2026, Jul 2026, Aug 2026 (revised),
   Sep 2026, Oct 2026; row builder unchanged (headline values; URL or demand_data/raw path in raw_file; "Manager transcription:" note). Wrapped in
   `if __name__ == "__main__"`; added KEYS list. Before: 3 months hard-coded; Sep 2025/Jun 2026/Aug 2026/Sep 2026 existed only as hand edits in
   processed CSV (lost if retrieve_research ran). Aug/Sep 2026 raw_file "raw/research/..." -> "demand_data/raw/research/..." (12 rows normalized).
   Check: code/check_cb_reproduction.py + full old-vs-new comparison: all 24 prior CB rows reproduced (values, notes, sources); only intended differences:
   Sep 2026 (revised, below), Sep 2024 PDF raw_file re-dated 2026-09-27 -> 2026-11-10 (retrieve_research re-saves the PDF).
   Added Oct 2026 (91.7 / 120.4 / 72.6) and Sep 2026 revision (84.2 headline; PS 111.8 = 120.4-8.6; Exp 65.7 = 72.6-6.9; first print 81.9 / 109.3 / 63.6 kept in note)
   from the Oct 27, 2026 release. The release gives no revised Sep sub-index levels; derived as in the existing Aug/Jun 2026 rows. A month cannot have two rows in the build, so the first print
   is replaced by the revised value (as was done for Aug 2026).
2. build_demand_signals.py:
   - docstring: usage + TLDR policy. imports: re, sys, copy, datetime, load_workbook.
   - new OUT_DIR = argv[1] or ROOT (path only); table csv: processed/ by default, OUT_DIR if arg given; wb.save(ROOT/"demand_signals.xlsx") -> OUT_DIR/"demand_signals.xlsx".
   - TLDR: hard-coded Sept 27 TLDR list and its writing into the top of "Demand Signals" removed; ws.append([]) + hdr -> ws.append([None]) so header is row 2 (as live).
     Existing TLDR sheet from the current demand_signals.xlsx is copied verbatim (values, styles, merges, widths) to the first sheet, with banner row "As of Oct 2, 2026 (written before the Nov refresh; not updated by the build)" inserted as row 1 (not re-added if already present). No sheet -> none written.
   - freeze panes: ws.freeze_panes = ws.cell(hdr+1,2) -> f"B{hdr+1}" (cell is a MergedCell once the header moves to row 2; same pane).
   - Michigan: raw_mich dict "Michigan_tbmics_2026-09-27.csv" etc. -> "Michigan_tbmics_*.csv"; glob(raw_mich[col].replace("2026-09-27","*")) -> glob(raw_mich[col]) (sorted()[-1] = newest ISO date; the original already globbed newest, now no hard-coded date).
   - Notes & Caveats computed at build time: "3-mo change" PCE goods example (pce_example); "Gasoline share" (gas_chg, sr_chg); "BEA vintage" (bea_note: retrieval dates from BEA raw_file names, latest months from table; Oct 2 history kept as labeled static text); "Conference Board" (cb_note: every month from Aug 2025 at latest recorded vintage, notes included); "Revisions/timing" (latest_months). Not touched (still hand-typed, now partly stale): Michigan ("Record low 44.8 (May 2026). September 2026 = final reading."), Microsoft break numbers, capex guidance, Wealth ("through 2026 Q2").
3. No edits to retrieve_official.py, retrieve_research.py, fetch_utils.py. Not edited: GUIDANCE URLs in retrieve_research.py (Q2/FY26 Q4 pages) and REPORT.md strings are stale (flagged).

## Step 5 gate (rebuild current processed data -> tmp/gate/, diff vs live)
Run: python3 -I build_demand_signals.py <abs>/tmp/gate ; code/compare_xlsx.py live tmp/gate. 10 cell diffs:
- Demand Signals: 0 value diffs; same dims row 2 onward; merged ranges equal. processed table csv identical.
- TLDR: only the inserted banner (all other text identical, shifted down 1 row).
- Notes B4, B18, B22: identical to live.
- Notes B9 and B21 differ in wording (numbers identical): B9 says "BEA files retrieved Oct 2, 2026" (live "retrieved Sept 30-Oct 2"), drops "(revised)" and the hand sentence "Fed, Michigan and capex rows unchanged (already latest)", adds Nov 10 archive pointer. B21 lists seven months (Aug 2025, Sep 2025, May-Sep 2026) with source notes, live listed four selected months in prose.
- Not value-compared: cell formatting. Live has header-row styling displaced by hand row deletion (A1 navy fill, row 2 unstyled), freeze pane D14, col widths A=48.5; rebuild has navy header on row 2, freeze B3, script widths.
Proceeded with the refresh (data and structure match; the two note cells are the expected result of computing them).

## Refresh run (2026-11-10)
retrieve_official.py (45 raw files, 4,221 obs, 38 metadata rows, 0 N/A), retrieve_research.py (10 raw files; CB page scrape failed again and fell back to Aug 2026 first print; Sep 2024 PDF re-fetched OK), supplement_research.py (24 rows), build_demand_signals.py (live workbook + processed/demand_signals_table.csv rewritten).
Raw files created: tmp/raw_files_created.txt. Comparison output: tmp/refresh_compare_out.txt (code/refresh_compare.py); context: code/worth_a_look.py.
Keys sourced from .env, not printed or written.
Revisions: 109 of 4,262 overlapping observations changed value; Q2 2026 BEA investment components (levels and Q/Q SAAR): zero change after Q3 advance.
