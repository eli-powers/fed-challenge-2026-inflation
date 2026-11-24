Status: Audited — converged R1 (Codex)

# Slide 3B build: "Inflation Forecast: SPF Median with Oil Price Scenarios"

**Built:** 2026-11-16 by Claude (Opus 5.5), no subagents, to Eli's Nov 16 spec: one quarterly time series; post-pandemic pass-through only; P1 dropped.

## Outputs
- **Workbook:** `01_Finals/Slide data/Inflation Slide 3B.xlsx`.
  - `Forecast`: the chart tab.
  - `Q4Q4_2027`: the right-hand values.
  - Grey raw tabs: `Raw_PCE`, `Raw_scenarios`.
  - `Notes`: every element mapped to its source.
  - 25 live formula cells.
- **Deck:** `01_Finals/slides/Inflation Slides (working).pptx`. Slide 12 is appended after 3a.2; slides 1–11 are unchanged (signature check). A pre-build copy of the deck is in the session scratchpad.
- **Script:** `code/build_inflation_slide3b.py`. It reuses the 2A/3A helpers and writes `code/verify_report.txt`.
- **PowerPoint render:** `render/deck_3b.pdf`; slide PNG `render/s3b.png`.

## Slide content
- **Title (Eli):** "Inflation Forecast: SPF Median with Oil Price Scenarios". The apostrophe in "Scenario's" was dropped.
- **Heading (Claude draft, to confirm):** "Core PCE Inflation Through 2027 Under Two Oil Paths".
- **Chart:** core PCE, % q/q annualized, 2025Q4–2027Q4. Axis 0–4, step 1.
  - **Actual (gray)** through 2026Q3: 2.49, 3.94, 3.31, 2.47.
  - **From 2026Q4**, each path starts at the 2026Q3 actual, so the lines join. The forecast region is shaded from the fork.

| Path | 2026Q4 | 2027Q1 | 2027Q2 | 2027Q3 | 2027Q4 |
|---|---|---|---|---|---|
| SPF median (black dashed) | 3.00 | 2.71 | 2.60 | 2.41 | 2.36 |
| Oil to $110 (red) | 3.03 | 2.78 | 2.70 | 2.73 | 2.80 |
| Hormuz reopens (dark navy) | 2.91 | 2.69 | 2.41 | 2.15 | 1.99 |

- **Right-hand column, 2027 Q4/Q4 (Q4 2026 to Q4 2027):**
  - Oil to $110: 2.8% (2.7507).
  - SPF median: 2.5% (2.5213, the quarterly path compounded; the published annual median is 2.50).
  - Hormuz reopens: 2.3% (2.3107).
- **Source line:** BEA via FRED (PCEPILFE); Philadelphia Fed SPF, Q4 2026 median; EIA (Brent; STEO); FEDS Notes (Nov 9, 2026), post-pandemic pass-through; UMD calc. It also gives the units, the last actual quarter, and "Dashed line: SPF median".
- **Takeaway:** placeholder.

## Verification (verify_report.txt: PASS)
1. **Workbook:** all 25 formula cells equal the script after LibreOffice recalculation.
2. **Against the pipeline CSV** (`processed/scenario_grid_2026Q4.csv`): actual q/q differs by at most 3e-7; 2027 Q4/Q4 by at most 4e-7.
3. **Chart:** all 22 points equal the `Forecast` tab, and the blanks match.
4. **Axis and deck:** the 0–4 axis contains the data (1.99–3.94). Slides 1–11 are unchanged, with no duplicate zip parts.
5. **Render:** inspected in PowerPoint.
   - PowerPoint draws the plot at x 1.40–8.96 in, not the 1.53–9.27 in that was set (measured from the PDF).
   - The shading and labels are placed on the measured edges (`RENDER_X`).
   - The source line runs two lines and clears the takeaway.

## Deviations from the guide
1. **Four lines.** Actual gray #595959, SPF dashed black, and two paths in red and dark navy. The guide allows two lines plus a reference.
2. **The dashed line is a forecast path,** not a constant reference.
3. **Shaded forecast region** (#E3E3E3), with a gray label.
4. **Quarterly category labels.**
5. **Right-hand value column,** Arial 20 bold in the line colors, with a two-line header.
6. **Y-axis number format 0.00,** per the guide; the values are at one decimal.

## Open for Eli
- Confirm or replace the heading.
- Write the takeaway.
- Script lines:
  - the post-pandemic flag (the authors call it an upper bound; pre-pandemic gives $110 2.61 / reopens 2.54);
  - why P1 is gone (it equals the SPF on the Q4 survey);
  - the jump-off (Nov–Dec core needs about 0.15% m/m).

## Re-pull
- After the Nov 18 EIA Brent update, rerun in order:
  - `fetch_inputs.py`
  - `forecast.py --spf 2026Q4`
  - this script with `--verify`
  - the PowerPoint render
- The 2026Q4 splice moves the paths slightly.
- If the plot frame changes, re-measure `RENDER_X`.

## Audit (Codex)
- R1 CONVERGED. Codex recomputed independently from raw files: the actuals, the SPF medians, both scenario paths end-to-end (gap -> response -> q/q), the three Q4/Q4 values, all 22 chart points from the pptx XML, and the render calibration; slides 1-11 byte-identical to the slide3a R3 deck.
- R1-F01 (Non-blocking): end labels raised to Arial 16 bold per guide s.4; rebuilt (PASS) and re-rendered after a PowerPoint restart (PowerPoint had served a cached copy).
- Not covered: the Q4 pipeline rerun as a whole (only the inputs feeding this slide), and renders on other machines or after manual resizing.


## Update (Nov 16, after R1): alternate 3B for comparison (slide 13)
- Eli: make the q/q-annualized chart and the year-over-year column harder to confuse; build options 1-3 alongside the current slide.
- Slide 13 (`build_slide(..., alt=True)`), same data and chart: (1) panel title "Quarterly pace, % change at an annual rate" (plot top moved to 2.16 in); (2) a "2027" bracket over 2027Q1-2027Q4 with an arrow to the column; (3) column headed "2027 as a whole / Q4 2026 to Q4 2027", set off by a gray divider; shading label moved to the bottom of the shaded area.
- Verify PASS (44 chart points = workbook; slides 1-11 unchanged). Fresh PowerPoint render `render/s3b_alt.png`; plot edges unchanged, so `RENDER_X` holds.
- Not audited: layout-only change on audited data. Slide 12 is unchanged in content.

## Update (Nov 16, late): Eli's keeper + end-point labels
- **Keeper = the alternate** ("Quarterly pace" version), hand-edited by Eli: the 2027 bracket and arrow removed; the panel title, column header and divider kept. The superseded copy was deleted; the deck is 12 slides with 3B at slide 12.
- **Option A labels** (Eli): marker plus native data label at each path's 2027Q4 point, Arial 12 bold, line color, one decimal, no % sign: $110 2.8 (above), SPF 2.4 (above), reopens 2.0 (below). They are the chart's own values (2.7992 / 2.3610 / 1.9920), so they always match the `Forecast` tab. Names moved to x 9.28, divider to 11.10, header to 11.15, values to 11.35 so the dots don't touch the names.
- Done by `code/patch_slide3b_labels.py`, an in-place patch. It refuses to run while the deck is open, backs the deck up to `backup/` first, touches only slide 3B, and checks that slides 1–11 are unchanged (PASS; `code/patch_labels_report.txt`). Fresh PowerPoint render: `render/s3b.png`.
- **Do not rerun `build_inflation_slide3b.py` against the deck.** It would erase Eli's hand edits and re-add two copies. For the Nov 18 Brent refresh, update the chart data in place: rerun the pipeline, then patch the chart's series values and the three column values. Rebuilding the workbook alone is safe.
- Not re-audited: layout and labels only, on audited data.

## Update (Nov 16, late): clipped dots after pasting into the team deck
- **Symptom (Eli):** the 2027Q4 dots were cut off after copy-paste into the team deck; they looked fine in the working deck.
- **Cause:** the dots sit on the plot's right border, and the chart frame ended only 0.08 in past the plot's set edge (9.27 → 9.35 in). In the working deck PowerPoint squeezed the plot to 1.40–8.96 in, which left room. Widening the frame showed that the squeeze came from the tight frame itself: with room, PowerPoint draws the plot exactly where the manual layout puts it. A deck that lays the plot out as set puts the dots on the frame edge and clips them.
- **Fix** (`patch_slide3b_labels.py`, in place): the chart frame right edge goes from 9.35 to 9.80 in, and the plot's manual layout is set explicitly to 1.398–8.958 in (`RENDER_X`), so the shading, names and column stay aligned. The fresh PowerPoint render measures 1.398–8.949 and looks identical. The dots now have about 0.85 in of clearance inside the frame. Slides 1–11 are unchanged (PASS).
- Not verified in the team deck (no access). Paste with Keep Source Formatting, and check that the team deck's slide size is 13.33 × 7.5 in.
- **Second fix (still clipped in PowerPoint for the web):** the web app clips markers at the plot-area edge, not the frame. With crossBetween=midCat the first and last points sat on that edge. The patch now sets crossBetween=between and widens the plot area by half a category on each side (0.925–9.431 in), so the points stay at 1.398–8.958 in and the 2027Q4 dots sit 0.47 in inside the plot. The chart frame is now x 0.25–9.80 in. Fresh desktop render: points unchanged (gray starts 1.38, red dot ends 9.05), and the baseline runs 0.92–9.43 in. Slides 1–11 are unchanged (PASS). Web rendering is not verified by me.
