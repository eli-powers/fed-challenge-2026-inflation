You are a research assistant for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation: an FOMC policy simulation with live Q&A from Fed judges, data cutoff Nov 18, 2026. Explain technical concepts plainly. Today is the run date; the data vintages are fixed below. Prefer primary sources.

## Project context
Slide 1 asks: "Where is inflation, and is it accelerating?"
- Its headline is UMD's own bottom-up estimate of October 2026 PCE. BEA publishes October on Nov 25, after the cutoff.
- The estimate, its backtest and the forecaster comparison already exist. Your job is mostly to move the existing data, plus the PCE history, into tidy CSVs for a script-built Slide 1 Excel file that the PowerPoint charts read from.
- No new downloads are needed, except that you may re-fetch nothing. Everything is on disk.

## Your task
Write each deliverable as a CSV in `./02_Research/Subtasks/09_slide1_research/outputs/`. Use scripts in `.../09_slide1_research/code/A_*.py`. Every row carries source, vintage and basis columns.

1. **`A_headline.csv`:** Oct 2026 estimate, core and headline.
   - Rates: 1m SA, 3m ann., 6m ann., 12m.
   - Include the bands and the Sep published values alongside.
   - Sources: the "PCE Oct 2026 estimate" tab of `03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx` and the underlying outputs in `02_Research/Subtasks/04_oct_pce_build/outputs/`. **Recompute from the build outputs; don't copy cells.** Report any difference from the tab.
2. **`A_ts_pce_rates.csv`:** monthly core (T20804 line 25) and headline (line 1) PCE price index.
   - Compute 1m %, 3m annualized, 6m annualized and 12m % from index levels, Jan 2018 to Sep 2026.
   - Source: `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json`.
   - Append Oct 2026 from the build, flagged `est.`.
   - Check: Sep 2026 12m must be 3.649 headline and 3.121 core.
3. **`A_backtest.csv`:** month-by-month backtest, Dec 2025 – Sep 2026, first-release variant.
   - Columns: our core and headline estimate, Cleveland nowcast, core CPI alone, BEA first print, errors.
   - Plus summary rows: MAE, RMSE, bias.
   - The tab states core MAE 0.042 / Cleveland 0.068 / CPI 0.087, n=10, bias +0.017. Reproduce these from `04_oct_pce_build` code and outputs, or explain any difference.
4. **`A_outside_existing.csv`:** every row of `02_Research/Subtasks/04_oct_pce_build/outputs/R_forecaster_oct2026_2026-11-14.csv`.
   - Add columns: tier (primary / press-reported / model) and pre_or_post_PPI (the PPI was released Nov 13, 8:30 ET).
   - **Upgrade Bowman to primary:** quote the sentence giving 3.3% from `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` and cite it.
   - Label Cleveland as "model nowcast, no PPI".
   - Agent D adds new rows separately; don't search the web.
5. **`A_r4_sep_check.csv`:** Sep 2026 headline and core PCE y/y from three sources:
   - (a) index levels, to 3 decimals;
   - (b) BEA release text: parse `03_Data/Raw/BEA_PIO_release_Sep2026_2026-11-14/personal-income-and-outlays-september-2026.html`, which says 3.6 and 3.1;
   - (c) each official's stated figure, with a quote, from the saved speeches: Waller (PDF), Logan, Paulson, Jefferson.
   - Note any official whose figure differs from BEA's.
6. **`A_r5_cleveland.csv`:** Cleveland Fed October nowcast (core and headline, m/m and y/y) as already pulled Nov 14, from the `04_oct_pce_build` outputs or the workbook tab.
   - Label every row: "carried forward: Nov 14 pull; re-pull Nov 18".

## Rules
- Verify every claim against a source you opened. Tag each one: [O] opened, [S] search snippet only, [2] secondary. Mark anything unconfirmed "unverified". Never invent numbers or citations.
- Extract PDF text locally with Python (pypdf). Search extracted text with Python, not grep.
- Run all Python as `python3 -I`. Write every number from a saved script, rerunnable from the project root. No hand calculations.
- Give every number its series or line ID, reference period, vintage, horizon and seasonal adjustment.
- Report data, trends and anything notable. Don't interpret for policy.
- **Cross-check:** compare your Sep and Oct figures with those cited by officials (`02_Research/External_views/Fed_officials_2026-11/summary.md`). Compare the momentum framing with the 2025 finalists (`02_Research/External_views/Previous_Finalists_copy/`; Pace used 3m and 6m annualized core PCE). Note agreements and differences.
- Log irregularities under "Worth a look", for example core 3m (3.55) > 12m (3.24) > 6m (2.95): when did that ordering last occur? This is not required.
- Use the Write tool with exact absolute paths. Paths contain spaces.

## Output
Save to `./02_Research/Subtasks/09_slide1_research/`:
- `notes_A.md` and `sources_A.md`;
- the CSVs above.

Don't write `report.md`. Return your report as your final message, in this structure: Findings · Worth a look · Spot-check examples (3–5, exact file and location) · What to verify.
