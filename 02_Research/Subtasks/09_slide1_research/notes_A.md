# Agent A notes: existing data into tidy CSVs (Slide 1)

Run date 2026-11-14. All scripts: `code/A_*.py`, run from the project root as `python3 -I <script>`. Tags: [O] opened, [2] secondary.
Run order: A_ts_pce_rates, A_headline, A_backtest, A_outside_existing, A_r4_sep_check, A_r5_cleveland, A_worth_a_look (the last reads A_ts_pce_rates.csv).
Nothing was downloaded; no web access. `03_Data/Raw` and `07_Archive` untouched.

## Conservative choices (no one to ask)
- **Rate source for A_headline:** recomputed Oct level = BEA Sep published level (T20804, Nov 10 file) x (1 + `estimate_mm`/100), then 3m/6m/12m from T20804 levels. The build itself used ALFRED vintage-2026-10-29 levels. Results differ from the build/tab by at most 1.6e-5 pp (3-decimal level rounding). `estimate_mm` is the build's stored 5-dp value; the sum of the line contributions in `D_build_2026-10_lines.csv` is 0.295077 core / 0.317874 headline (6-dp rounding of lines; difference <= 6e-6).
- **Bands:** `band_reported` from the build summary (core 0.0489, headline 0.0452 pp m/m = first-release-variant backtest RMSE), times 1 (1m, 12m), 4 (3m ann.), 2 (6m ann.). Same as the tab; band diff vs tab = 0.
- **Sep published values** in A_headline are computed from T20804 levels, to 5 dp (BEA's own rounded text values 0.3/0.5 m/m are two extra rows).
- **Backtest:** rule months Dec 2025 - Sep 2026 only (n=10); Nov 2025 and the Oct 2023/2024 seasonal-check months excluded, as in the tab. "Our estimate" = first-release variant (`est_variant`, D2), with the main-run estimate kept in a separate column. Cleveland = `bench3_cleveland` (last nowcast before the PCE release); "core CPI alone" = `bench2_core_cpi_ols` (expanding-window regression of core PCE m/m on core CPI m/m, current vintage), not raw core CPI. No CPI benchmark exists for headline in the build.
- **Tiers (A_outside_existing):** UMD and Cleveland = "model"; Goldman, BofA, Capital Economics, Reuters, SocGen, Pantheon = "press-reported"; Bowman = "primary". pre_or_post_PPI taken from the source file's `timing` column. Cleveland labelled "model nowcast, no PPI"; its pre/post field says the model does not use PPI.
- **Bowman URL** (federalreserve.gov/.../bowman20261110a.htm) comes from the footnote hyperlinks inside the saved RTF and from summary.md; I did not re-fetch the page.
- **Paulson core:** no core PCE figure appears in the saved speech, so the core row is blank (not inferred).
- **Cleveland r5:** daily path for the Oct 2026 target (Oct 1 - Nov 13) from `R_cleveland_oct2026_2026-11-14.csv`, long format, latest row flagged; every row labelled "carried forward: Nov 14 pull; re-pull Nov 18". Latest values cross-checked to the raw JSONs in 03_Data/Raw (match).

## Results
### Check values (A_ts_pce_rates)
Sep 2026 12m: headline 3.64887 -> 3.649, core 3.12116 -> 3.121. Both pass.

### A_headline: Oct 2026 estimate vs tab
| Measure | 1m SA | 3m ann. | 6m ann. | 12m | Band (1m / 3m / 6m / 12m) |
|---|---|---|---|---|---|
| Core | 0.29507 | 3.55080 | 2.94772 | 3.24244 | 0.0489 / 0.1956 / 0.0978 / 0.0489 |
| Headline | 0.31788 | 4.62244 | 3.09295 | 3.82457 | 0.0452 / 0.1808 / 0.0904 / 0.0452 |
| Sep core (published) | 0.31650 | 2.90252 | 2.92270 | 3.12116 | |
| Sep headline (published) | 0.49084 | 3.55818 | 3.33546 | 3.64887 | |

Differences from the tab: none above 1.6e-5 pp (core 3m -0.000016, 6m -0.000007, 12m -0.000007; headline 3m +0.000011, 6m +0.000006). Cause: BEA levels at 3 decimals (T20804 vs ALFRED). All tab cells C5:C12, F5:F12 agree to rounding.

### A_backtest (first-release variant, n=10, error = estimate minus BEA first print, pp)
| | Bias | MAE | RMSE |
|---|---|---|---|
| Our core | +0.0169 | 0.0423 | 0.0489 |
| Cleveland core | -0.0398 | 0.0677 | 0.0783 |
| Core CPI OLS | -0.0706 | 0.0874 | 0.0995 |
| Our headline | +0.0179 | 0.0401 | 0.0452 |
| Cleveland headline | -0.0366 | 0.0614 | 0.0726 |

The tab's statements (core MAE 0.042 / Cleveland 0.068 / CPI 0.087, n=10, bias +0.017) are reproduced exactly at the rounding shown. Main run (not the variant): core MAE 0.0399, bias +0.0193, RMSE 0.0465.
Caveats from the build's own metadata: components and weights are current vintage (not real time); only Aug-Sep 2026 used BEA's current method table; portfolio management PPIs in the variant use first-release values for 2 lines.

### A_outside_existing
9 rows, none dropped. Bowman sentence [O] (saved RTF, Council on Foreign Relations, Nov 10): "Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3.3 percent in October, as upward pressures from higher energy prices and AI-related demand continue to flow through to core goods and services prices." The earlier row's quote (StockTitan) was a paraphrase; the speech has no m/m and no headline figure.

### A_r4_sep_check
| Source | Headline y/y | Core y/y |
|---|---|---|
| (a) index levels | 3.649 | 3.121 |
| (b) BEA release text (Oct 29 release) | 3.6 | 3.1 |
| (c) Waller (PDF p.3) | **3.7** | 3.1 |
| (c) Logan | 3.6 | 3.1 |
| (c) Paulson | 3.6 | not stated |
| (c) Jefferson | 3.6 | 3.1 |

Only Waller's headline differs from BEA (3.7 vs 3.6; (a) rounds to 3.6). I found no vintage in the saved data that gives 3.7: the build's first-print Sep headline 12m is 3.64887. Cause unknown; unverified. Waller also states m/m 0.5 and 0.3, matching BEA.

### Cross-check against officials' Oct figures (summary.md and speeches)
- Bowman (core 12m Oct, 3.3, pre-PPI, built off Oct CPI) vs ours 3.24: 0.06 pp higher than our estimate; Cleveland 3.21; Goldman 3.24; BofA, Capital Economics, Reuters 3.2; Pantheon 3.3 (pre-PPI). Her 3.3 is consistent with the pre-PPI cluster (Pantheon) and ~0.06-0.09 above the post-PPI cluster. No official gave an October headline figure.
- Logan: "higher than expected" Oct CPI, worried PCE could rise; Jefferson: Oct data "consistent with well above-target inflation". Qualitative, no conflict with our direction.
- Sep figures: all officials match BEA except Waller's headline (above).

### Cross-check against 2025 finalists (momentum framing)
Pace's Q&A transcript (PDF, 2025-11-21, text just before the "Page 5 of 19" footer) [O]: "three-month core PCE has increased above its six-month measure, indicating inflation has recently accelerated", and calls shorter annualized measures better for "recent underlying trend". Our framing agrees: we report the same 3m and 6m annualized core PCE. Our Oct estimate passes Pace's test (core 3m 3.55 > 6m 2.95; headline 4.62 > 3.09). Differences: (1) Pace's wording is about 3m vs 6m, with 12m "stalled"; here 12m (3.24) sits between 3m and 6m. (2) Ours for Oct are estimates with bands (3m +/-0.20 core, which is a larger share of the 3m-6m gap of 0.60 than a point estimate suggests). (3) Pace's Q&A text shows no band or estimated month (slides not seen). The saved "2025 Finals - 1 Presentations.md" is Eli's own prior note listing "Pace compares 3- and 6-month annualized core PCE" [2].

## Worth a look (also in A_worth_a_look.csv)
1. **Ordering core 3m (3.55) > 12m (3.24) > 6m (2.95):** occurred in 12 months of Jan 2018 - Oct 2026 (est.): 2019-12, 2020-07, 2020-08, 2022-01, 2022-07, 2022-08, 2024-10, and 2026-10 est. Last before now: **Oct 2024**. Headline same ordering (4.62 > 3.82 > 3.09): 13 months; last before now **Oct 2025**.
2. **The ordering comes from a trough, not a spike:** core 1m was 0.133 (Jun) and 0.138 (Jul 2026), which holds the 6m below the 12m; the 6m window for Oct (May-Oct) still contains both. Core 1m prints are 0.262, 0.317, 0.295 for Aug-Oct.
3. **3m ann. core 3.55 is not extreme:** last month with 3m >= 3.551 was Apr 2026. The 12m core est. 3.242 is the highest since Nov 2023; headline 12m 3.825 highest since May 2023.
4. **Pace test over the last 12 months:** core 3m > 6m in 6 of 12 months (Dec 2025 - Apr 2026, then Oct est.); it was false May - Sep 2026. So the Oct "acceleration" signal is new, and depends on the estimate. Headline: 7 of 12.
5. **Our estimate vs Cleveland bias:** backtest bias +0.017 (ours) vs -0.040 (Cleveland). Oct gap: ours 0.295 vs Cleveland 0.267 for core 1m; the sign of the gap is consistent with the historical biases of both, so part of the 0.03 pp gap may be method bias.
6. **Waller's 3.7 vs BEA 3.6** (above).
7. **Oct 2025 base month:** BLS did not publish most Oct 2025 CPI data (summary of 2025-finals note; not checked by me). The Oct 2026 12m rates use BEA's Oct 2025 PCE level (core 127.165; 1m 0.177) as the base. I did not investigate how BEA built it.
8. **Backtest first-print vintages are delayed** (Jan 2026 first print vintage 2026-03-13, Feb 2026-04-09): release timing differed from the usual month-end schedule in this data. Not investigated.

## What to verify
- Whether Waller's 3.7 appears on the Fed's HTML version of the speech (only the PDF is saved).
- BEA's Oct 2025 base-month treatment (item 7).
- Bowman URL against the live page.
- Cleveland: re-pull Nov 18 (all r5 rows are labelled carried forward).
