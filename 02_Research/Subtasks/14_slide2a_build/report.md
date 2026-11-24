Status: Audited — converged R1 (Codex, Nov 15); F01 fixed; F02 and J01 with Eli

# Slide 2A build: Inflation Slide 2A workbook and slide 2A (two-chart)

**Built:** 2026-11-15 by Claude (Opus 5.5), no subagents. Inputs: the slide build prompt (`01_Finals/Slide instructions/slide_build_prompt.md`, first draft, used as written per Eli), Eli's Step 0 answers (Nov 15), and David's style guide (`Fed_Challlenge_Style_Guide.md`). Eli's rules override the guide where they conflict.

## Outputs
- **`01_Finals/Slide data/Inflation Slide 2A.xlsx`**, holding every number on the slide:
  - `Categories` (left chart): live formulas, excess = `Raw_categories` Oct contribution minus the 2018–19 average.
  - `Shock_groups` (right chart): live formulas, excess = share × (rate − 2018–19 rate) over `Raw_groups`.
  - `Raw_categories`: all 15 core BEA categories, Sep and Oct.
  - `Raw_groups`: group shares, rates and baselines for Mar 2025 and Oct 2026.
  - `Notes`: every slide element and where it comes from.
  - `fullCalcOnLoad` is on.
- **`01_Finals/slides/Inflation Slides (working).pptx`**: slide 2A appended as slide 4, after the section slide and slide 1 (guide and wide versions). The earlier slides are canonically unchanged. Backup of the pre-2A deck: scratchpad `working_deck_backup_pre2A.pptx`.
- **Build script:** `code/build_inflation_slide2a.py` (writes `code/verify_report.txt`).
- **PowerPoint render:** `render/slide2a_powerpoint_render.pdf` (full deck: `render/working_deck_powerpoint_render.pdf`).

## Slide content
- **Title:** "Inflation: Three Shocks Now Drive the Excess" (Eli).
- **Chart heading (DRAFT, Claude; Eli to confirm):** "Core PCE Inflation Above Its Pre-Pandemic Pace: Where It Comes From".
- **Note line:** "Excess = contribution to core PCE 12-month inflation above its 2018–19 average · *Oct 2026 = UMD estimate".
- **Left panel ("By spending category, Oct 2026*", DRAFT):** horizontal red bars, Oct 2026* excess (pp), six largest categories plus housing, with BEA names.

  | Category | Oct 2026* |
  |---|---|
  | Recreational goods and vehicles | 0.43 |
  | Transportation services | 0.25 |
  | Health care | 0.18 |
  | Other services | 0.14 |
  | Clothing and footwear | 0.11 |
  | Food services and accommodations | 0.11 |
  | Housing | 0.00 |

- **Right panel ("By shock exposure, Mar 2025 vs Oct 2026*", DRAFT):** grouped bars, Mar 2025 (dark navy) vs Oct 2026* (red).

  | Group | Mar 2025 | Oct 2026* |
  |---|---|---|
  | Energy | −0.01 | 0.39 |
  | Tariffs | 0.03 | 0.41 |
  | AI | 0.06 | 0.35 |
  | All other | 0.76 | 0.35 |

- **Y-axis:** −0.20 to 0.80 pp, step 0.20, format 0.00, the same on both panels. Data min −0.0084 (energy, Mar 2025); max 0.7627.
- **Value labels:** Arial 11 bold at each bar end, in the series colour. Oct values carry "*".
- **Source line:** "Source: BEA (PCE price indexes and spending, Tables 2.4.4U/2.4.5U); UMD calculations; shock tags: UMD. Percentage points of core PCE 12-month inflation above the 2018–19 average, monthly data through Oct 2026*. *Oct 2026 = UMD estimate built from BLS CPI/PPI."
- **Takeaway:** the placeholder.
- **Last date plotted:** Oct 2026 (UMD estimate). The left chart also compares to the 2018–19 average; the right chart compares Mar 2025 with Oct 2026.

## Deviations from the guide (all flagged)
1. **Bar charts throughout.** The guide is written for line charts with dates.
   - Chart tabs have category or group names in column A, not dates (s.6).
   - There are no end labels; value labels sit at the bar ends instead of above bars (s.3, adapted for horizontal bars).
2. **Left plot position:** x 2.60–5.13 instead of 1.27–5.13 (s.5), so the BEA category names fit to the left of a horizontal bar plot. The two plots are therefore not the same size.
   - PowerPoint renders the left plot about 0.3 in wider than set (≈2.67–5.43 in); the right plot sits exactly at 7.40–11.27 in.
   - The left panel title is centred over the s.5 left slot (1.27–5.13).
3. **Right-chart key** ("■ Mar 2025 ■ Oct 2026*", Arial 13 bold in the series colours), inside the top-left of the plot. Bars have no end labels to identify the series, and the guide allows no legend.
4. **Y-axis in pp:** −0.20 to 0.80 in steps of 0.20, not whole-number steps (Eli). The floor is below 0 because energy is −0.01 in Mar 2025 (the s.3 floor rule, scaled to 0.20 steps).
5. **Colours:** Oct 2026 is red, the first colour, as the emphasis series. Mar 2025 is dark navy. On the right chart Mar 2025 is the first series in data order, but it takes the second colour.
6. **Note line and source line** both carry the "*Oct 2026 = UMD estimate" footnote (Eli approved both).

## Verification (`code/verify_report.txt`, PASS)
1. **Workbook:** 23 formula cells recalculated in LibreOffice equal the script's values (tolerance 1e-9).
2. **Recompute from raw vs the audited research outputs:**
   - categories: a fresh run of `H_oct_drivers.py` equals `H_oct_drivers_categories.csv` (max diff 0);
   - shock groups: recomputed through `C_common` vs `G_excess_path.csv` (rounded to 4 dp), max diff 4.9e-5.
3. **Chart points:** all 15 embedded chart points equal the workbook chart-tab values (max diff 9e-16). The series order is Mar 2025, Oct 2026.
4. **Y-axis range** covers the data (−0.0084 to 0.7627).
5. **Chart XML:** `invertIfNegative val="0"` on all 3 bar series; the asterisk number format is on the Oct labels.
6. **Deck:** 4 slides. The section slide, both slide 1 versions, and their chart and embedding parts are canonically (C14N) identical to the pre-2A deck; python-pptx only re-serializes bytes. No duplicate zip entries.
7. **Rendered in Microsoft PowerPoint** (AppleScript export to PDF) and inspected against s.8:
   - no gridlines, legend or chart box;
   - title inside the band;
   - value labels beside their bars, none touching;
   - the −0.01 label sits below the baseline;
   - category names fit (one wraps to two lines);
   - the source line (2 lines) clears the takeaway.

## Notes for Eli
- **Copying into the team deck:** the charts are native and embedded, not linked, so pasting keeps their data. The slide uses the team deck's Blank layout.
- **Re-running the slide 1 builder recreates the working deck from the team deck, which would remove slide 2A.** Re-run this script afterwards.
- **Data cutoff (Nov 18):** nothing here changes before the cutoff unless an October build input is revised. In that case:
  1. rerun `04_oct_pce_build`;
  2. rerun `10_slide2_research/code/H_oct_drivers.py` and `G_baseline_attribution.py`;
  3. rerun this script with `--verify`.
- **Script consistency:** spoken figures in the tracker (S2-E1 line: "about four-tenths each", "roughly halved") match the right chart (0.39 / 0.41 / 0.35; All other 0.76 → 0.35). There is no `script_final.md` yet.
- **Drafts to confirm:** the chart heading, both panel titles, and the label "All other" for the untagged group.

## Not checked
- Excel itself was not used to render; PowerPoint and LibreOffice were.
- Pasting into the team deck was not tested.
