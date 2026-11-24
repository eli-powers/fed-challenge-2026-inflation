# 02_refresh_baskets — raw notes (2026-11-10)

All paths relative to project root unless absolute. PI = `03_Data/pipelines/Price indexes/`.

## Run log (order actually run)
1. Archive: copied every `*/raw/`, `*/processed/`, `code/` (minus `__pycache__`) and `Price_Basket_Findings.xlsx` to `PI/archive/pre_refresh_2026-11-10/` (151 files = 150 + workbook; 77 MB). Originals left in place.
2. `retrieve_bea_baskets.py` (no edits needed; dates are derived from the data). Run with plain `python3` (not `-I`): it imports `fetch_utils` from its own folder, which `-I` removes from `sys.path`. Same for `retrieve_bls_baskets.py`. All other scripts run with `python3 -I`.
   - Output: "Built BEA basket outputs for 2026M09: mapped 176/178 Dallas components".
   - New raw: `PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json`, `..._U20405_2026-11-10.json`, `BEA_NIPA_T20804_2026-11-10.json`, `BEA_NIPA_T20807_2026-11-10.json`, `Cross-index analysis/raw/BEA_NIUnderlyingDetail_U90100_2026-11-10.json`, Dallas tech PDF / components xlsx / history xlsx / page html, BEA FAQ 83 html, NIPA handbook PDF (all `_2026-11-10`).
3. `core_ex_oer.py 2026-11-10` (priority) → `Cross-index analysis/processed/core_pce_ex_oer_2026-11-10.csv` and `core_pce_ex_oer_summary_2026-11-10.csv`. `core_ex_oer_DONE.txt` written immediately after.
   - Validation, Sep 2026 (12m / 6m ann / 3m ann / m/m): derived 376−153 = 3.595 / 3.427 / 3.366 / 0.366; published T20804 l.28 = 3.596 / 3.429 / 3.369 / 0.367. Max abs gap 0.003 pp (old vintage, Aug: max 0.002 pp).
   - `inflation_data/code/build_workbook.py` picks the newest `core_pce_ex_oer_????-??-??.csv`, so it will read the 2026-11-10 file automatically.
4. `retrieve_bls_baskets.py` (edited; see below). First attempt: BLS API HTTP 503 on CPI batch 8 after batches 1–7 were saved. Found a latent cache bug (below), so deleted only the same-day (`_2026-11-10`) `bls_api_*` partial files in CPI/raw and PPI/raw and reran from clean; second attempt succeeded.
   - First successful run used CPI_LATEST = 2026-10. Outputs copied to `02_Research/Subtasks/02_refresh_baskets/oct2026_cpi_basket_run/` (components, reconciliation, published_aggregates, REPORT).
5. `rebuild_market_based.py` (no edits) → 289 rows, 2026M09.
6. `sector_contributions.py 2026-11-10 2026-09` (args passed; defaults in the script still say 2026-10-01 / 2026-08, not edited) → `Cross-index analysis/processed/pce_sector_contributions_2026-09.csv`.
7. `analyze_baskets.py` with Oct CPI: **crashed** (`weight_pct()` IndexError: CPI rows have no 12m contribution, so the filtered frame is empty). This is the Oct-2025 CPI gap, a method item (see below). Stopped on that item.
8. Set CPI_LATEST = 2026-09 and reran `retrieve_bls_baskets.py` (reused the same-day raw files; no new API calls). Then `analyze_baskets.py` OK, `build_basket_workbook.py` OK → `PI/Price_Basket_Findings_build_2026-11-10.xlsx`. `Price_Basket_Findings.xlsx` byte-identical to archive copy (cmp) — untouched.
9. `replace_sheets.py` NOT run.

## Script edits (file, line, before → after, why)
### code/retrieve_bls_baskets.py
- L27: `LATEST = "2026-08-01"` → `LATEST = "2026-10-01"` (Cleveland/Atlanta latest month; both publish Oct 2026). Added L28–32: `CPI_LATEST`, `PPI_LATEST`, helpers `_mshift()` (month shift) and `_mlabel()` ("Sep 2026"). Why: the CPI/PPI sections had ~30 literal "2026-08"/"Aug 2026"/"M08" strings; now derived from two constants. Final values: `CPI_LATEST = "2026-09"` (see method item), `PPI_LATEST = "2026-09"`.
- `request_bls()` signature: added `latest` argument; cache check `x.get("year") == "2026" and x.get("period") == "M08"` → compares to `latest`. Why: otherwise every cached Aug file counts as current and nothing is re-fetched. Callers pass CPI_LATEST / PPI_LATEST.
- CPI: `dates = {"latest": "2026-08", "base_12m": "2025-08", "base_3m": "2026-05", "base_1m": "2026-07"}` → derived from CPI_LATEST; `change(..., "2026-08", k)` → `CPI_LATEST` (l1, l3, l12); `latest_period` "2026-08" → CPI_LATEST; published-aggregate lookup year/period "2026"/"M08" → from CPI_LATEST; column name `aug_2026_value_or_pct` → `<mon>_<yyyy>_value_or_pct` (now `sep_2026_value_or_pct`; no script reads this column — grep checked); reconciliation `p = "2026-08"` → CPI_LATEST, `"period":"Aug 2026"` → `_mlabel(CPI_LATEST)`; two REPORT.md strings "August 2026"/"Aug 2026" → f-strings.
- PPI: `periods=("2025-08","2026-05","2026-07","2026-08")` → derived from PPI_LATEST; l1/l3/l12 `"2026-08"` → PPI_LATEST; weight tuple `("2026-08","2025-08","2026-05","2026-07")` → derived; `latest_period` (components and named_series) → PPI_LATEST; reconciliation `pub=change(lv(sid),"2026-08",...)` and `"period":"Aug 2026"` → PPI_LATEST / label; named-series l1/l3/l12 → PPI_LATEST; REPORT question string → f-string.
- Cleveland: reconciliation `"period": "Aug 2026"` → `_mlabel(LATEST[:7])`; REPORT "Latest period ... Aug 2026" → f-string. **Borderline edit:** `"publisher_rate_pct": "0.2"` (a typed Aug 2026 value) → `_trim_1m`, read from the saved `clevelandfed_trim_revised_<date>.csv` (`trim_monthly_chg` × 100, 1 decimal, row = LATEST). Same published figure, now traceable to a raw file; Aug check: 0.0021995 × 100 = 0.2, matches the old literal. Oct 2026 value: 0.4. Coordinator may prefer to revert.
- Atlanta: URL `.../Documents/datafiles/research/inflationproject/stickprice/stickyprice.xlsx` (HTTP 404 on 2026-11-10, redirects to /error) → `.../Documents/research-and-data/data/sticky-price/sticky-price-data.xlsx` (link taken from https://www.atlantafed.org/research-and-data/data/sticky-price-cpi). Same sheet "Data", same 25 columns and header text as the Sep 27 file; latest row 2026-10-01. REPORT "Latest published workbook row: Aug 2026" → f-string.
- Not edited (stale text, left as-is): CPI REPORT "Investigation: headline 12m gap is -0.295 pp ... 94.607% at Aug 2025 and 95.684% at Aug 2026" (now −0.306 pp at Sep 2026); PPI REPORT "Reconciliation gaps above 0.15 pp: annualized 3m FD4=+0.204 pp, ID61=+0.292 pp, ID62=+2.760 pp" (now +0.834 / +3.119 / +3.393).

### code/build_basket_workbook.py
- New line before HEAD: `CPI_LBL, PPI_LBL, CLE_ATL_LBL = "Sep 2026", "Sep 2026", "Oct 2026"`.
- HEAD dict: six `"Aug 2026"` → CPI_LBL / PPI_LBL.
- L128 title: "CPI/PPI Aug 2026; PCE {PCE_LABEL}" → "CPI {CPI_LBL}; PPI {PPI_LBL}; PCE {PCE_LABEL}".
- L191 Cleveland tails section "Aug 2026" → CLE_ATL_LBL; L206 Atlanta section "Aug 2026" → CLE_ATL_LBL.
- **Output path:** `wb.save(ROOT / "Price_Basket_Findings.xlsx")` → `wb.save(ROOT / f"Price_Basket_Findings_build_{date.today()}.xlsx")`. Why: the script overwrote Eli's hand-edited workbook directly; brief says build to a separate file.

### Not edited
- `retrieve_bea_baskets.py`, `rebuild_market_based.py`, `core_ex_oer.py`, `analyze_baskets.py`, `sector_contributions.py`, `replace_sheets.py`, `findings_text.json`.
- `core_ex_oer.py` default vintage (2026-10-01) and `sector_contributions.py` defaults (2026-10-01, 2026-08) left; passed as arguments.

## Method items (stopped, not changed)
1. **October 2026 CPI basket: no 12-month horizon.** BLS did not collect Oct 2025 CPI; the Oct 2026 release says BLS "cannot publish 12-month percent changes for October 2026 for indexes where October 2025 data are unavailable" [O, cpi.nr0.htm]. In the Oct run, 12m is available for only 6 of 204 headline leaves (new vehicles, used cars, leased cars, gasoline, postage, wireless). The pipeline's CPI 12m weights (RI updated to Oct 2025) and 12m contributions are all N/A, and `analyze_baskets.py` crashes (movers, breadth, coverage all rank/weight on 12m contribution). Options need a method decision: (a) keep CPI basket at Sep 2026 (current state); (b) Oct basket on 1m/3m only, with analyze/build changed to skip 12m for CPI; (c) a 12m approximation per BLS's "approximating missing data" factsheet. Current pipeline state = (a).
2. **PCE sector contributions sheet** in the workbook is hand-made (no script writes it). New source CSV exists (`pce_sector_contributions_2026-09.csv`) but updating the sheet needs either a hand edit or a new build step.
3. `request_bls()` same-day cache bug (robustness, not method): after a partial failure, the rerun renumbers the missing IDs from batch 1, finds today's `batch1` file on disk and reuses it for a different ID subset, so those IDs come back empty without error. Avoided here by deleting the partial same-day files. Suggest a fix (e.g., include the first series ID or a hash in the file name, or verify IDs on reuse).

## Data notes
- CPI Oct 2026 (Oct run): headline 1m SA 0.350% (index calc; BLS rounds to 0.4), core 1m SA 0.296% (0.3); 3m ann SA headline 5.72%, core 3.75%; component 3m-sum gap headline +0.81 pp, core +0.33 pp (linear sum of annualized rates; analyze_baskets' fix_3m rescales). 12m N/A.
- CPI Sep 2026 basket (pipeline state): 344 rows (204 headline, 140 core); 171 headline / 107 core leaves with a 12m contribution (was 170/106: Motor vehicle body work CUUR0000SETD01 gained data).
- PPI Sep 2026: 59 rows, unchanged composition.
- PCE Sep 2026: 336 rows (178 headline, 158 core in the BEA script; analyze_baskets rebuilds core to 148 with data). Dallas list: 176/178 mapped (same as before); current Dallas workbook has 177 rows. Unmapped "Audio-video, photographic, and information processing equipment services" moved from Dallas rank 34 to 88 (a component_id label change, not a basket change).
- Market-based PCE: 289 rows (158 headline, 131 core), unchanged.
- Cleveland tails: 12 → 13 rows (tail membership changes month to month; list in report).
- Atlanta sticky: 5 series, Oct 2026.
- Dallas trimmed mean: Sep 2026 1m ann 2.84, 6m ann 2.42, 12m 2.26 (Aug: 1.92 / 2.35 / 2.19). Dallas component workbook has no month label in rows 1–2; its contents differ from the Oct 1 copy (status counts top/bottom/included 85/47/43 vs 70/57/48), so treated as Sep; month itself unverified from file.
- Revisions (new vintage minus old, 12m): core PCE Jul +0.012, Aug +0.027 (3.008 → 3.034); core ex OER Jul +0.014, Aug +0.031 (2.999 → 3.030). Jan–Jun 2026 unchanged.
- PPI Aug FD 1m revised: release says +0.5% in Aug (old pipeline Aug 1m SA 0.40%).

## Spot-checks
- FRED PCEPILFE pc1 (API, realtime 2026-11-10): Sep 2026 3.12116 vs pipeline 3.121160 (BEA T20804 l.25). Match.
- FRED PCEPI pc1: Sep 2026 3.64887 vs pipeline 3.648874. Match.
- BLS PPI release (ppi.nr0.htm, Sep 2026): FD +1.3% m/m SA, +6.3% 12m NSA vs pipeline 1.343 / 6.338. Match.
- BLS CPI release (cpi.nr0.htm, Oct 2026) Table A: gasoline 12m 37.4, new vehicles 0.7, used cars −3.3; Oct run leaves 37.358 / 0.736 / −3.313. Match. Headline/core 1m 0.4/0.3 vs published_aggregates (API) 0.4/0.3.
- BLS API calculations (pct_changes '12'): CUUR0000SA0 Sep 2026 3.7, CUUR0000SA0L1E 2.6 vs pipeline 3.738 / 2.564.

## Workbook comparison method
- `code/compare_workbooks.py <file>` compares the current workbook with (a) the new build and (b) a rebuild of the Oct 2 state made by running the archived code on the archived data in a temporary scratch folder. Differences in (b) = hand edits since the last build.
- `code/compare_vintages.py` prints row counts, dropped/added components, reconciliation old vs new, and revisions.

---
# Round 2 (coordinator message, approved by Eli), 2026-11-10 ~22:55–23:10 EST

## Run log
1. Snapshot of CPI, PPI, Trimmed mean, Sticky CPI, Cross-index processed files to the scratchpad before any change (`.../scratchpad/snap_before_task2/`).
2. Edited `retrieve_bls_baskets.py`, `analyze_baskets.py`, `build_basket_workbook.py` (below). Reran retrieve_bls_baskets (same-day raw cache reused; still 9 CPI raw files dated 2026-11-10, so no new API pulls), analyze_baskets, build_basket_workbook.
3. Verified with `cmp`: every pre-existing processed file is byte-identical to the snapshot **except** `Trimmed mean/processed/reconciliation.csv` (intended R1-F03 change).
4. Downloaded Cleveland's method PDF to `Trimmed mean/raw/clevelandfed_interpolation_method_oct2025_2026-11-10.pdf` (publisher file, pipeline raw path).
5. New check scripts (subtask code/): `oct2026_interp_checks.py` (BLS bounds, Cleveland, Atlanta), `replace_preview.py` (what replace_sheets would do; CSVs in `replace_preview/`).
6. replace_sheets.py NOT run. Live workbook unchanged.

## Script edits (before → after)
### retrieve_bls_baskets.py
- New helper after `_mlabel`: `_interp_oct2025(lev)` sets `lev["2025-10"] = sqrt(lev["2025-09"] * lev["2025-11"])` only if Oct 2025 is missing.
- `def retrieve_cpi() -> None:` → `def retrieve_cpi(latest=CPI_LATEST, suffix="", interpolate_oct2025=False)`, with docstring. Inside the function every `CPI_LATEST` → `latest` (16 places, including the request_bls cache check). With defaults the function is identical to before (verified: official outputs byte-identical).
- After the node level loop: `if interpolate_oct2025:` apply `_interp_oct2025` to `all_levels` (CUUR0000SA0) and every node's NSA levels. After `aggregates = {...}`: same for CUUR0000SA0 and CUUR0000SA0L1E. SA levels are not touched (1m/3m don't use Oct 2025).
- Output names: `components.csv` → `components{suffix}.csv`; same for `published_aggregates`, `reconciliation`, `REPORT`. REPORT gets a leading "APPROX." or "Short-horizon view" line when suffix is set.
- In the reconciliation loop, when interpolating: two extra rows per aggregate, "11m NSA (Nov 2025 base; upper/lower bound)" and "13m NSA (Sep 2025 base; upper/lower bound)" = change(levels, latest, 11/13), not annualized.
- `main()`: `retrieve_cpi()` → `retrieve_cpi()` + `retrieve_cpi("2026-10", "_2026-10_short_horizon")` + `retrieve_cpi("2026-10", "_2026-10_approx_interp_oct2025_base", interpolate_oct2025=True)`.
- R1-F03: Cleveland reconciliation row `"source_ids": "Cleveland Fed Median CPI page / component table", "raw_file": saved` → `"source_ids": "... ; trim_revised.csv (monthly rate)", "raw_file": f"{saved}; {fetched['trim_revised'][1]}"`. Tails files keep the component-table path.
- Comment on `CPI_LATEST` line updated (no value change).
### analyze_baskets.py
- Appended block at end of file (nothing above changed): `_cpi_view()` loads a CPI component file with the existing `clean`/`tag`/`fix_3m`; `_ranked()` = existing sign rule (top 5 positive / top 5 negative).
  - Short horizon: movers ranked by 3m ann. contribution → `cpi_movers_2026-10_short_horizon.csv`; 3m breadth (>3% 3m ann.) with 12m-base weights taken from the approx. file (only source of Oct 2025 weights), aligned by row (component_id is not unique), plus a variant with exact 3m-base weights → `cpi_breadth_2026-10_short_horizon.csv`.
  - Approx. 12m: movers and the three breadth measures by the existing rules → `cpi_movers_2026-10_approx_interp_oct2025_base.csv`, `cpi_breadth_2026-10_approx_interp_oct2025_base.csv`. All labelled "approx., interpolated Oct 2025 base".
  - Fix during run: first version used `set_index("component_id").reindex` (duplicate-label error), then a non-NaN-safe assert; final version aligns by row with a NaN-safe name/id assert.
### build_basket_workbook.py
- New `NOTES_HDR = "Notes as of Aug 2026 data (Oct 2 workbook)"`, `CUR_HDR = "Current notes"` and `notes_block(ws, notes, ncol, height, prefix)`: header row (notes header merged over 1..ncol, "Current notes" in column ncol+1, width 60), then each note verbatim via `para`, the Current-notes cell left empty.
- Summary key findings: `for f in FINDINGS["key"]: para(ws, "• " + f, 9, 48)` → `notes_block(ws, FINDINGS["key"], 9, 48, prefix="• ")`.
- Summary by-index table: header "One-line finding" → NOTES_HDR, plus a new last column CUR_HDR (empty); widths `[30,10,8,10,60,60,70,10,10]` → `[30,10,8,10,60,60,70,60,10]`.
- `index_sheet`: `for n in notes: para(ws, n, 12, 32)` → `notes_block(ws, notes, 12, 32)` (CPI, PPI, PCE, PCE supercore, Market-based PCE).
- PCE supercore `supercore_ex` table: header "Measure" → "Measure (Notes as of Aug 2026 data (Oct 2 workbook); values are Aug 2026)", plus empty "Current notes" column.
- Trimmed & Sticky, Hypothesis analysis, Sources: `for n in ...: para(...)` → `notes_block(...)` with the same widths/heights.
- New sheet "CPI Oct 2026 views" (added before save, only if the Oct files exist): Oct aggregates (1m/3m published; approx. 12m with 11m/13m bounds), short-horizon movers, approx. 12m movers, breadth. Existing sheets unaffected by it.

## Results
- Interpolated 12m (NSA, approx., interpolated Oct 2025 base): headline 4.022 (11m 4.131 / 13m 3.913), core 2.815 (2.874 / 2.756). Matches coordinator's FRED check 4.02 (4.13/3.91), 2.81 (2.87/2.76).
- Component-sum vs aggregate (approx.): headline 3.911 vs 4.022 (gap −0.112; Sep official −0.306); core 3.035 vs 2.815 (gap +0.220; Sep −0.124). Coverage 168 headline leaves with 12m (Sep: 171).
- Cleveland PDF (Dec 2025): for overall CPI and each component, g_i = (CPI_Nov/CPI_Sep)^(1/2) − 1, used as the one-month change for both Oct and Nov; median and 16% trimmed mean then computed as usual; Oct component data BLS did publish on Dec 18 are ignored. PDF does not state SA vs NSA.
- Cleveland files: median Oct25 = Nov25 m/m exactly (0.116279%); trimmed Oct25 0.148178% vs Nov25 0.149027% (differ by 8.5e-6). Published Oct 2026 12m (usinflationdata.csv): median 2.7992, trimmed 2.8912; chaining the monthly files reproduces both exactly; geometric base on Cleveland's own index: median 2.7992 (exact), trimmed 2.8908 (−0.0004). Pipeline has no median/trimmed reconstruction logic, so a component-level recompute was not possible (component table covers only the latest month).
- Atlanta: Oct25 = Nov25 monthly relatives for Sticky, Core sticky, Sticky ex-shelter; NOT equal for Flexible (0.001744 vs 0.001424) and Core flexible (0.000631 vs −0.000090). Chaining monthly reproduces all five published Oct 12m; geometric base on Atlanta's chained index reproduces sticky series exactly, but gives flexible 6.218 vs 6.201 and core flexible 1.259 vs 1.222.
- Breadth jump in approx. 12m "above own 2018–19 avg" (CPI core 37.3% Sep → 76.1% Oct): mostly OER (35% weight) moving from 3.26% to 3.42% vs its 3.32% 2018–19 average.
- Workbook formatting: earlier comparison was values only. CPI and PPI sheets in the live workbook also differ from the Oct 2 rebuild in formatting: CPI column E width 13 vs 11, row heights set on rows 1/5/18/29/42, 50 cells with fill alpha FF vs 00 (typical of an Excel re-save); PPI 89 style diffs and 8 row heights. Summary, PCE, PCE supercore, Market-based PCE: no value, style, width or height differences from the Oct 2 rebuild.

- 2026-11-11 fix (3m contribution gap): `retrieve_bls_baskets.py` now compounds 3m contributions the same way as `analyze_baskets.fix_3m` (new `compound_3m_contribs()`), so `components*.csv` and `reconciliation*.csv` agree with the movers files. CPI step rerun on the cached 2026-11-10 raw vintage (no new downloads). Only `contrib_3m_ann_calc` changed. New 3m sum gaps: Oct headline +0.11 pp (was +0.81), core +0.17 (was +0.33); Sep headline −0.14 (was +0.28), core −0.03 (was +0.13). Workbook "CPI Oct 2026 views" D6:E6 and D8:E8 patched in place; backup at `Price indexes/archive/Price_Basket_Findings_pre_3mfix_2026-11-11.xlsx`. Movers rankings unchanged (they already used fix_3m).
