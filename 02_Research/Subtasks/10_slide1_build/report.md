Status: Audited — converged R1

# Slide 1 build: Inflation Slide 1 workbook and slide 1 (two-chart)

**Built:** 2026-11-15 by Claude (Opus 5.5), with no subagents, from Eli's Nov 15 instructions and David's style guide (`01_Finals/Slide instructions/Fed_Challlenge_Style_Guide.md`). Eli's rules override the guide where they conflict.

## Outputs
- `01_Finals/Slide data/Inflation Slide 1.xlsx`. It holds every number on the slide:
  - `12m` and `Momentum`: chart tabs in the guide's s.6 format (real dates in column A, header = line name, a Reference column of 2.00). Values are live formulas over `Raw_PCE`.
  - `Raw_PCE`: BEA T20804 index levels for Oct 2022–Sep 2026, plus the Oct 2026 level, computed by formula from `Oct_est`.
  - `Oct_est`: the UMD October m/m estimate and its backtest band.
  - `Notes`: every slide element (title, heading, panel titles, end-label values, axis range, window, source line, takeaway) with where it comes from.
- `01_Finals/slides/Inflation Slides (working).pptx`: a copy of the team deck. It keeps only the Inflation section slide (unchanged) and adds slide 1.
- Build script: `code/build_inflation_slide1.py`, which also writes `code/verify_report.txt`.
- PowerPoint-rendered reference: `render/slide1_powerpoint_render.pdf`.

## Slide content (Eli's decisions, Nov 15)
- **Title:** "Inflation: Firming Again After a Summer Lull".
- **Chart heading:** drafted by Claude: "PCE Inflation: 12-Month Rates and Recent Core Momentum". Eli to confirm.
- **Takeaway:** the placeholder.
- **Left panel:** core (red) and headline (dark navy) PCE, 12-month % change.
- **Right panel:** core PCE 3-month (red) and 6-month (dark navy) annualized.
- **Window:** Oct 2023 to Oct 2026 on both panels.
- **Dashed 2% target** on both panels.
- **End labels:** name, then value with "est.":

| Line | Panel | Oct 2026 |
|---|---|---|
| Core | left | 3.24% est. |
| Headline | left | 3.82% est. |
| 3-month | right | 3.55% est. |
| 6-month | right | 2.95% est. |

- **Y-axis:** 0–5, step 1, format 0.00, the same on both panels (guide s.3 and s.5).
- **Source line:** "...through Oct 2026 (Oct = UMD estimate built from BLS CPI/PPI). Dashed line: 2% target." Eli approved this wording.

## Deviations from the guide
1. **Category labels.** The chart's embedded data uses text category labels: "YYYY-MM" for January and July, a single space otherwise. With a window starting in October, a native category or date axis can't put labels on January and July only.
   - The workbook's chart tabs keep real dates in column A, as the guide requires.
   - Row order is identical, and the build verifies the labels against the tab dates.
2. **The "est." marking** is not in the guide. Eli chose a small label in the end labels.
3. **Rendering settings.** Date labels are set not to wrap (`wrap="none"`), because PowerPoint split "2024-" / "01". The chart frame ends at 5.96 in, so one line of date labels clears the source line at 6.00.

## Verification (verify_report.txt, PASS)
1. Workbook: 154 formula cells recalculated in LibreOffice equal the script's values (tolerance 1e-9).
2. Pptx: all 222 embedded chart points, including Reference, equal the workbook chart-tab values (max diff 5e-15). The category labels follow the tab dates.
3. The plotted series equal the audited Slide 1 research series (`09_slide1_research/outputs/A_ts_pce_rates.csv`): 148 values, max diff 5e-6 pp, due to the CSV's 5-dp rounding.
4. End-label values equal the last workbook values. Y-axis 0–5 (data max 4.454, core 3m in Mar 2024). Window 2023-10 to 2026-10.
5. Deck: 2 slides; the section slide's XML is canonically identical to the team original; there are no duplicate zip entries. The team deck's hash is unchanged (it matches the archived original).
6. Rendered in Microsoft PowerPoint (AppleScript export to PDF) and inspected against the guide's s.8 checks:
   - the plot spans x 1.27–5.13 and 7.40–11.27 in, and y 2.16–5.60 in;
   - the end labels sit level with their line ends;
   - the dashed line is at 2.00;
   - the Mar 2024 peak (4.45) reads correctly against the axis;
   - no gridlines, legend or chart box;
   - the date labels clear the source line, and the source line (2 lines) clears the takeaway.

## Not checked
- Excel itself was not used to render.
- Copy-pasting into the team deck was not tested. Native charts carry their own embedded data, so pasting keeps it.

## Update (Nov 15, after the audit): wide version added
- **What was added:** at Eli's request the deck now has 3 slides: the Inflation section slide, slide 1 in the guide's s.5 layout, then slide 1 in a **wide layout**.
- **Wide layout:** plots at x 0.95–5.40 and 7.26–11.71 in, 4.45 in wide each (about 15% wider than the guide's). This deviates from s.5. Everything else is identical.
- **Not re-audited (Eli's instruction).** Only the layout changed; no numbers changed or were added.
- **Build checks (verify_report.txt): PASS.**
  - 444 chart points across both versions equal the workbook.
  - End labels in both versions equal the last workbook values.
  - The section slide is unchanged; no duplicate zip entries.
- **Render:** `render/slide1_powerpoint_render.pdf` is re-exported from PowerPoint with all 3 slides.

## Update (Nov 15): estimate marker
- **Change:** at Eli's request, the "est." text in the end labels is replaced by an asterisk on each October value, e.g. "3.24%*".
- **Footnote:** the source line now reads "...through Oct 2026*. Dashed line: 2% target. *Oct 2026 = UMD estimate built from BLS CPI/PPI."
- **Scope:** applied to both versions. The Notes tab is updated. Layout and text only; no numbers changed.
- **Checks:** build checks PASS; re-rendered in PowerPoint.
