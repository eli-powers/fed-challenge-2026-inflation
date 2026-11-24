# Audit R1 — slide3b_build — 2026-11-16
VERDICT: CONVERGED

## Blocking findings
None.

## Non-blocking findings
### R1-F01 · Style · slide 12, line-name end labels
- Claim as written: “Oil to $110”, “SPF median”, “Hormuz reopens”.
- Evidence: `ppt/slides/slide400.xml` in the copied working deck sets all three names to Arial 14 bold (`a:rPr sz="1400"`). The style guide §4 specifies Arial 16 bold. The report’s listed deviations do not explicitly cover this reduction.
- Why it matters: Small, readable guide deviation; no effect on the data or takeaway.
- Suggested fix: Use 16 pt if it fits, or explicitly record the 14 pt deviation. No further audit round needed for this alone.

## Judgment calls for Eli
None newly raised. The draft heading and placeholder takeaway remain Eli’s decisions. The selected post-pandemic regime and dropped P1 path are accepted as instructed.

## Worth a look
None.

## Checked and confirmed
- Reproducibility: fresh copies, claim map, independent script and results are in `99_Codex/slide3b_build/R1/`. `audit_check.py` imports no pipeline code; it reads the raw inputs directly. Numerical outputs are preserved in `audit_results.json`.
- Actuals: quarterly-average PCEPILFE ratios produce **2.49062946, 3.93655920, 3.31397224, 2.46778073%** for 2025Q4–2026Q3. Workbook quarter references and all three `=B5` forecast joins are correct. Raw monthly workbook inputs match the copied FRED JSON.
- Vintage and definition: [FRED](https://fred.stlouisfed.org/series/PCEPILFE) confirms BEA source, monthly SA index, September 130.902, October 29 update and November 25 next release. No newer PCE release is scheduled before the November 18 cutoff.
- SPF: direct extraction of `medianLevel.xlsx`, COREPCE2–6, 2026Q4 row, gives **3.0000, 2.7106, 2.6000, 2.4141, 2.3610%**. These agree with the [Q4 release](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026) at its displayed precision; 2027Q4 is published, not derived.
- Timing: official [SPF dates](https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/spf-release-dates.txt) confirm November 11 deadline and November 16 release. [EIA](https://www.eia.gov/outlooks/steo/outlook.php) confirms November 10 STEO release and November 5 forecast completion. November STEO is correctly selected under the stated latest-release-before-deadline proxy rule; the SPF’s actual oil assumption remains unpublished.
- Oil inputs: independently parsed daily Brent ends November 11 at **$92.14**; Q4 splice uses 30 observations totaling **3501.78**, plus 34 remaining weekdays. November STEO quarterly assumptions are **108.976667, 95, 89, 83, 77** dollars/bbl.
- Both scenario paths reconstructed end-to-end. For $110, gaps are **3.760544, 14.660347, 21.184400, 28.163976, 35.667494** log points; 2027Q3/Q4 level adjustments **0.123555972/0.230350460%** imply 2027Q4 **2.799198901%** annualized. Hormuz path independently gives **1.991973109%**. Every forecast cell agrees with workbook and pipeline within **0.0000006 pp**.
- Response attribution: the post coefficients used match the [FEDS accessible Figure 2 table](https://www.federalreserve.gov/econres/notes/feds-notes/the-effect-of-oil-prices-on-core-inflation-recent-evidence-from-the-advanced-economies-accessible-20261109.htm). The source’s five-economy scope and upper-bound caveat are retained in workbook notes. Slide wording makes no claim about changed price-setting behavior and assigns no scenario probabilities.
- Q4/Q4: independently compounded 2027 quarterly paths give **2.750657720, 2.521328430, 2.310652483%** ($110, SPF, reopens). The formulas correctly use rows 7–10, excluding 2026Q4. The separately published SPF annual median is **2.50%**; workbook A7 explains the different question. Both SPF measures display **2.5%**, so the slide does not introduce a reported-number discrepancy.
- Formula tracing: all 25 numerical formula cells in the slide workbook were evaluated independently. The supporting derivation workbook’s 2027Q4 scenario rows 53/65 use the correct lag order, post-response column, and prior-quarter level; Oil_paths row 26 and Baseline row 14 refer to the proper Q4 inputs.
- Native chart: read `chart21.xml` and its embedded workbook directly. All **22** nonblank chart points, the Q3 join, and blank positions agree with evaluated workbook formulas; no missing values become zero. Axis is **0–4**, step **1**, format **0.00**, through **2027Q4**.
- Render: independently rendered page 12 of the 12-page PowerPoint PDF with PDFKit. At 1536×864, shade spans **x=488–1032**, versus calibrated fork/right edge **487.642/1031.962** pixels. `RENDER_X=(1.398,8.958)` is supported for this export. Labels align with their lines; dates, source and takeaway clear one another. Title, heading, source and takeaway sizes/positions match the guide, apart from declared deviations and R1-F01.
- Prior-slide integrity: compared with the final slide3a R3 deck. Slides 1–8 and renamed parts 300→9, 301→10, 302→11, including relationships, are byte-identical. All old chart, embedded-workbook, master and layout parts are unchanged. Slide 12 (`slide400.xml`) is the only added slide.

## Not checked
- Did not rerun the production builder or pipeline, which would write outside the audit boundary. Independently reproduced their relevant calculations instead.
- Did not reopen the decks in the PowerPoint UI or test a different machine/export. The calibration is confirmed for the supplied Microsoft PowerPoint PDF, not guaranteed after a layout change.
- Did not repeat the converged Q3 research audit, re-estimate the FEDS model, or audit unrelated backup tabs/alternative regimes. Supporting workbook inspection was limited to inputs/formulas feeding this slide.
- The delivered slide workbook has uncached formula results. Its formulas were evaluated independently; the coordinator’s separate LibreOffice recalculation was not rerun. Excel recalculation on opening remains necessary for readers that depend on cached values.
- Future releases, including the planned November 18 Brent refresh, cannot be cleared by this round.
