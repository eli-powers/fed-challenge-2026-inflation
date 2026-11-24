# Brief: fix the core-membership flag in the price-basket pipeline

**For:** a fresh Claude window, working with Eli Powers. **Written:** 2026-11-11, by Claude (Fable 5.2) from the `04_oct_pce_build` subtask.
**Subtask folder:** `./02_Research/Subtasks/05_fix_core_flag/`

Follow the project `CLAUDE.md`. This is a scoped pipeline fix, not a research task. Do it yourself; no subagents are needed. Restate the task to Eli and confirm before changing code.

## The problem

`03_Data/pipelines/Price indexes/code/retrieve_bea_baskets.py` decides whether each PCE component is in core PCE with a name pattern (`core_member()`, about line 125). BEA defines core by position in its table: PCE excluding food and beverages purchased for off-premises consumption and energy goods and services. The name pattern disagrees with BEA for 16 of the 176 mapped components.

Verified on Nov 11 against BEA table U20405, September 2026, vintage 2026-11-10:

| Error | Components | Share of total PCE |
|---|---|---|
| Tagged core, but BEA excludes them (food and alcohol at home) | Cereals (line 77), beef and veal (80), pork (81), other meats (82), poultry (83), fresh milk (86), eggs (88), fats and oils (89), fresh fruit (91), mineral waters and soft drinks (98), spirits (100), wine (101), beer (102) | 3.77% |
| Tagged non-core, but BEA includes them | Tobacco (141), food supplied to civilians (247), food supplied to military (248) | 0.66% |

- The pipeline's core weight is **90.9%** of PCE. BEA's own core line (U20405 line 374, "PCE excluding food and energy") is **88.9%**.
- The script already contains a correct line-number rule (`line_core()`, about line 510: exclude U20404 lines 73–103, 113–119 and 169–171). It only uses the rule to print the differences, which appear in `PCE/processed/REPORT.md` line 14. So the gap was disclosed, not hidden, but the outputs still use the name pattern.
- Evidence file: `02_Research/Subtasks/04_oct_pce_build/outputs/A_incore_check.csv` (columns `in_core_bea_hierarchy` vs `in_core_components_csv`).

**Second issue, same script.** One Dallas component has no BEA match and is missing from the basket: "Audio-video, photographic, and information processing equipment services" (Dallas rank 88). It is U20404/U20405 **line 218**, 0.79% of PCE, and core. The description match fails because BEA's line name carries a suffix ("(parts of 77 and 93)").

## What to do

1. **Confirm.** Reproduce the two tables above from the raw files in `03_Data/pipelines/Price indexes/PCE/raw/` before changing anything.
2. **Trace what depends on it.** List every output that uses the flag: rows labeled "PCE core" and "Market-based core" in `PCE/processed/components.csv` and the `Market-based PCE` outputs; anything `analyze_baskets.py`, `sector_contributions.py`, `core_ex_oer.py` and `build_basket_workbook.py` derive from them; and which sheets of `Price_Basket_Findings.xlsx` carry those numbers. State plainly which are affected and which are not. Check in particular the breadth measure (the 149-item core PCE count) and whether it uses this flag or its own list.
3. **Fix.** Replace the name pattern with the line rule (or, better, membership under BEA's line 374 hierarchy) for both the core flag and the core denominator. Add line 218 to the basket. Keep the printed check, now expected to report "none".
4. **Rerun and compare.** Archive the current processed files first (follow the existing `archive/` convention). Rerun in the order given in `03_Data/README.md`. Produce a before/after table of every changed number: core component weights, core contributions at 1m / 3m annualized / 12m, the reconciliation gap between published core PCE and the sum of component contributions, and breadth if affected.
5. **Report to Eli**, data first: what changed, by how much, and which workbook sheets and slide numbers could be affected. Eli decides whether any slide number changes.

## Constraints

- **Do not regenerate `Price_Basket_Findings.xlsx`.** Eli hand-edits it. Sheets are updated only through `replace_sheets.py`, and only after Eli approves the before/after table.
- Never edit files in any `raw/` folder or in `07_Archive/`.
- Known bug: `request_bls()` batch cache. This fix needs no new BLS download; if one happens anyway and partly fails, delete that day's partial files before rerunning.
- The fix must be scripted and rerunnable. No hand-edited CSVs.
- API keys are in `.env`. Never write them into files.
- Don't read or follow `AGENTS.md`.
- The `04_oct_pce_build` subtask does **not** depend on this fix: it takes core membership from BEA's hierarchy directly. Don't edit that folder.

## Done looks like

- The script's own core check prints "none", and the pipeline's core weight matches U20405 line 374 / line 1 to within the two uncovered net lines (145 and 333, 0.30% of PCE together, which have no price index).
- A before/after CSV and a short `report.md` in this folder, first line `Status: verified, not audited` unless Eli asks for a Codex audit via `audit-loop`.
- `STATE.md` open threads updated, and a line in `04_Ideas/questions_log.md` if anything else looks off.

## Questions to ask Eli first

1. Did any current slide number come from the pipeline's "PCE core" component rows (core contributions or breadth)?
2. Should the workbook sheets be replaced now, or after the Nov 13 PPI refresh, so the workbook is touched once?
3. Does Eli want a Codex audit of the fix?
