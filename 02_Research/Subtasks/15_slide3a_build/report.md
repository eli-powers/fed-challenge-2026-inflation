Status: Audited — converged R3

# Slide 3A build: slides 3a.1 and 3a.2 and the Inflation Slide 3A workbook

**Built:** 2026-11-16 by Claude (Opus 5.5), with no subagents. The design is Eli's "defaults" to the Nov 16 design list. Two later instructions from Eli apply: September actuals only on 3a.1, and don't name the Logan measure; call it "services ex. housing & transportation".

## Outputs
- **Workbook:** `01_Finals/Slide data/Inflation Slide 3A.xlsx`.
  - Chart tabs: `Exposure_bars`, `Labor_costs`, `Expectations`, `NFIB_plans`.
  - Grey raw tabs: `Raw_BEA`, `Raw_12m`, `Raw_labor`, `Raw_survey`.
  - `Notes`: every slide element mapped to its source.
  - 544 live formula cells.
- **Deck:** `01_Finals/slides/Inflation Slides (working).pptx`. 3a.1 and 3a.2 were appended as slides 9 and 10, after the teammate's AI Buildout slides. All other slides are unchanged (canonical XML and chart signatures).
- **Script:** `code/build_inflation_slide3a.py` (reuses the slide 2 helpers). It writes `code/verify_report.txt`.
- **PowerPoint render:** `render/deck_3a.pdf`; PNGs `render/s3a_1.png` and `render/s3a_2.png`.

## Slide content
**3a.1, "Inflation: A First Round, Not a Spiral"** (two-chart, with a note line)
- **Heading** (draft, accepted): "The Shock Shows Up in Exposed Prices, Not in Labor Costs".
- **Note line:** "Top two items are directly exposed to oil and tariffs · Job openings per unemployed worker: 1.06 (Sep 2026) vs 1.16 (2018–19 avg.)".
- **Left panel:** horizontal bars, 12-month %, 2018–19 average (gray) / Feb 2026 (dark navy) / Sep 2026 (red).

| Item | 2018–19 | Feb 2026 | Sep 2026 |
|---|---|---|---|
| Transportation services | 2.05 | 4.30 | 9.21 |
| Core goods | −0.48 | 2.04 | 1.98 |
| Services ex. housing & transportation | 2.26 | 3.24 | 3.21 |
| Trimmed mean PCE | 1.94 | 2.38 | 2.26 |
| Median PCE | 2.34 | 2.91 | 2.67 |

  Axis −2 to 10, step 2.
- **Right panel:** unit labor costs, y/y (red, 2.39 in 2026Q3), and ECI private wages and salaries, SA y/y (dark navy, 3.12), 2018Q1–2026Q3. Dashed line at ULC's 2018–19 y/y average (1.77). Axis 0–7. (Originally 8-quarter annualized, 1.92 vs 1.90; switched Nov 16, see update below.)

**3a.2, "Inflation: Early Signs of Persistence"** (two-chart, no note line; window Jan 2018 – Oct 2026 on both panels)
- **Heading** (draft, accepted): "Households Expect More Inflation, and Small Firms Plan to Raise Prices".
- **Left panel:** NY Fed SCE median 1-year (red, 3.91 Oct) against 5y5y breakeven, monthly average (dark navy, 2.30 Oct). Dashed 2%. Axis 0–7 (Codex R1-F02).
- **Right panel:** NFIB net % planning to raise prices (red, 37) and compensation (dark navy, 24). Axis −10 to 60; the baseline is at the bottom.
- **Takeaways:** the placeholder on both slides.

## Verification (verify_report.txt: PASS)
1. **Workbook:** all 544 formula cells, recalculated in LibreOffice, equal the script's values. 0 mismatches.
2. **Cross-checks against earlier outputs** (max abs diff 0.0004 pp):
   - transportation and core goods against the P2/P3 scripts;
   - the 2018–19 averages for services ex. housing & transportation, the trimmed mean and the median against `C_q6_summary.csv`;
   - ULC y/y and ECI y/y against `B_q3_wages_ulc.csv`.

   P2 and P3 have not been audited; the rest are audited outputs.
3. **Chart points:** all 770 (including the vertical alternate) equal the workbook tabs.
4. **Axes:** every axis range contains its data.
5. **Deck:** 11 slides (3a.1 horizontal = 9, 3a.1 vertical = 10, 3a.2 = 11); slides 1–8 are unchanged; no duplicate zip entries.
6. **Render:** PowerPoint, inspected. No overlap; labels sit level with their line ends; dashed lines sit at 1.77 and 2.00; source lines (two lines, Arial 13) clear the takeaway (6.53/0.73).

## Deviations from the guide
1. 3a.1 left uses three bar series and a key; the third color is gray #7F7F7F.
2. 3a.1 left axis runs from −2 to 10.
3. Date labels:
   - 3a.1 right is quarterly, labelled on Q1 of even years;
   - 3a.2 is labelled on January of even years. Jan/Jul labels would overlap over nine years.
4. The 3a.2 right axis runs from −10 to 60 (NFIB price plans hit −3 in 2020).
5. End labels use one decimal; NFIB uses integers.

## Caveats and re-pull
- **No estimates on either slide.**
- **NFIB 2018–20:** comes from an archived report; seasonal factors may differ at the join.
- **5y5y:** October is a monthly average; the Nov 13 daily was 2.18.
- **Before the Nov 18 cutoff, nothing on these slides changes**, except possibly the October 5y5y average if FRED revises it. SCE November data arrives in December, NFIB November on about Dec 8, and productivity is revised Dec 8.
- **To rebuild:**
  ```bash
  python3 -I "02_Research/Subtasks/15_slide3a_build/code/build_inflation_slide3a.py" --verify
  ```

## Update (Nov 16, during Codex R1): alternate 3a.1 with vertical bars
- Eli asked for a vertical-bar version of the 3a.1 left chart, keeping the horizontal one for comparison. It is slide 10; 3a.2 moves to slide 11 (deck now 11 slides). Same data, same right panel; the note line says "The first two items" instead of "Top two items".
- Left plot widened to x 1.27–6.20 (guide 1.27–5.13) so the five category names fit; plot bottom 5.20 to leave room for wrapped category labels. Key at the top right of the plot.
- Verify: PASS (770 chart points = workbook; slides 1–8 unchanged). Rendered in PowerPoint: `render/s3a_1_vertical.png`.
- Audit note: the deck and build script changed after the R1 checksums were taken (addition of the alternate slide only; slides 9 and 11 rebuilt from identical data). Codex R1 audits the pre-alternate copy; the alternate shares every number with slide 9.

## Audit (Codex)
- R1: 2 Blocking (FRED 5y5y publisher = St. Louis Fed; source 13 pt / takeaway 6.53–0.73 / expectations axis 0–7), 1 Non-blocking (Dec 8). All accepted and fixed.
- R2: CONVERGED. Vertical alternate cleared. R2-F01 (stale report lines) fixed here.
- Open for Eli: horizontal vs vertical 3a.1; takeaways; slides 2A–2C still use 12 pt source / 6.62 takeaway (outside this task).

## Update (Nov 16, after R2): unit labor costs switched to year-over-year
- Eli: use the standard y/y unit, matching ECI and the teammate's employment slide (ULC y/y 2.4%). 3a.1 right panel (both versions) now plots PRS85006113 y/y (2026Q3 2.39; 2018–19 avg 1.77, dashed; 2021–23 peak 6.13). Panel title "Labor costs, % change from a year earlier"; axis 0–7 (max 6.13); source line "nonfarm unit labor costs, y/y".
- Cross-check vs audited `B_q3_wages_ulc.csv` yoy column; verify PASS (770 points). Rendered in PowerPoint.
- Message shift: ULC is now slightly above 2018–19 (2.4 vs 1.8) rather than equal (8q 1.92 vs 1.90). Cues 2 and 13 updated; 8q kept as Q&A backup.
- Needs Codex R3 (a plotted number changed).

- R3 (ULC y/y switch): CONVERGED. R3-F01 (stale report lines) fixed. Judgment for Eli: heading "Not in Labor Costs" vs ULC y/y 2.39 (0.62 pp above 2018–19 avg 1.77; far below 6.13 peak).
