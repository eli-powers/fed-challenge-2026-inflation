# Handoff: slide3b_build, Round 1

**Written:** 2026-11-16 by Claude (Opus 5.5). **Context:** finals data cutoff Nov 18; Eli pastes slides into the team deck by hand. Prioritize (A) and (D).

## What this is
One native one-chart PowerPoint slide, "Inflation Forecast: SPF Median with Oil Price Scenarios" (working deck slide 12), plus its workbook. Eli's spec (Nov 16): core PCE % q/q annualized (SPF basis), 2025Q4–2027Q4; one actual line through 2026Q3 forking into SPF median / Oil to $110 / Hormuz reopens from 2026Q4; shaded forecast region; right-hand column = 2027 Q4/Q4 per path. **Post-pandemic pass-through only** (Eli's decision; pre-pandemic is verbal). **P1 (Nov STEO path) dropped** (Eli; it equals the baseline on the Q4 SPF). Do not re-litigate these decisions as findings; flag premise problems as Judgment.

The numbers come from the forecast_3b pipeline run on the Q4 2026 SPF (Nov 16). The research and pipeline were audited as `06_Audits/slide3b_research` (converged R2) **on the Q3 SPF run only**; the Q4 rerun (same code; builder text changes) has **not** been audited. Spot-checking the Q4 pipeline inputs that feed this slide is in scope.

## Scope
- **(A) Facts, vintages, arithmetic:** every plotted number and the three right-hand values trace to `Inflation Slide 3B.xlsx`, then to the pipeline CSV / raw files.
- **(B) Reasoning:** does any element (title, heading, labels, shading label, source line) misstate what the data show? Wording rules: never present scenarios as probabilities; never call the FEDS oil note evidence of changed price-setting behaviour.
- **(C) Writing:** brief.
- **(D) Style guide:** `01_Finals/Slide instructions/Fed_Challlenge_Style_Guide.md`. Eli's decisions and the deviations listed in the report override it.

## Files
- `02_Research/Subtasks/16_slide3b_build/report.md`, `code/build_inflation_slide3b.py`, `code/verify_report.txt`.
- `01_Finals/Slide data/Inflation Slide 3B.xlsx`.
- `01_Finals/slides/Inflation Slides (working).pptx`: slide 12 is 3B; slides 1–11 must be unchanged.
- `02_Research/Subtasks/16_slide3b_build/render/deck_3b.pdf` (Microsoft PowerPoint export), `render/s3b.png`.
- Inputs: `03_Data/pipelines/forecast_3b/processed/scenario_grid_2026Q4.csv`, `processed/metadata_2026Q4.json`, `raw/2026-11-16/` (`PCEPILFE_observations.json`, `medianLevel.xlsx`, `nov26_base.xlsx`, `feb26_base.xlsx`, `EIA_RBRTEd.xls`, `spf-release-dates.txt`), `config/regime_response.csv`.
- Context: `02_Research/Subtasks/12_slide3b_research/FINAL.md` §1b (Q4 rerun summary), `03_Data/pipelines/forecast_3b/README.md`, `01_Finals/data/Slide3B_Inflation_Data.xlsx` (live-formula derivation of every scenario cell).

## Load-bearing claims
1. Actual core PCE q/q ann. (quarterly avg of PCEPILFE, FRED realtime 2026-10-29): 2025Q4 2.49, 2026Q1 3.94, Q2 3.31, Q3 2.47.
2. SPF Q4 2026 median core PCE (q/q ann.) 2026Q4–2027Q4: 3.00, 2.71, 2.60, 2.41, 2.36 (deadline Nov 11).
3. Oil to $110 (post): 3.03, 2.78, 2.70, 2.73, 2.80. Hormuz reopens (post): 2.91, 2.69, 2.41, 2.15, 1.99.
4. Right column, 2027 Q4/Q4: $110 2.8% (2.7507), SPF median 2.5% (2.5213; published annual median 2.50), reopens 2.3% (2.3107).
5. Oil-assumption proxy for the Q4 SPF = Nov 2026 STEO (released Nov 10, before the Nov 11 deadline).
6. Source line attributions.

## Explicit asks
1. Recompute independently: the four actual quarters from raw FRED; the SPF quarterly medians from `medianLevel.xlsx`; at least one scenario path end-to-end (gap → response → q/q) for 2027Q4, without importing the pipeline; the three Q4/Q4 values. Read chart data from the pptx XML/embedded workbook, not via my script.
2. Check workbook formulas reference the right rows (quarter averages, the 2026Q3 join, the Q4/Q4 product).
3. Check the render: shading starts at the 2026Q3 fork and ends at the plot's right edge; labels sit beside their lines; nothing overlaps; source line clears the takeaway.
4. Check slides 1–11 are unchanged versus `06_Audits/slide3a_build`'s final state if feasible (or at least that slide 12 is the only new slide).
5. Check whether the SPF row's 2.52 (compounded quarterly path) vs the published 2.50 is presented correctly.
6. Check what I said I could not verify: the RENDER_X calibration (measured from one PowerPoint export).

## Materiality rule
Blocking only if it would change a takeaway, a reported number, a source attribution, or a recommendation. Everything else is Non-blocking or Note.
