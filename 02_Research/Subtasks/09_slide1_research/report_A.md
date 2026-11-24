Status: Audited — converged R2

# Report A: existing Slide 1 data into tidy CSVs (Headline, TS, R1, R2-existing, R4, R5)

## Findings
**Oct 2026 estimate (`outputs/A_headline.csv`)**, recomputed from build `estimate_mm` + T20804 (Nov 10 vintage); max diff vs workbook tab 1.6e-5 pp; bands match tab.

| | 1m | 3m ann. | 6m ann. | 12m |
|---|---|---|---|---|
| Core est. (band ±) | 0.29507 (0.0489) | 3.5508 (0.1956) | 2.9477 (0.0978) | 3.2424 (0.0489) |
| Headline est. (band ±) | 0.31788 (0.0452) | 4.6224 (0.1808) | 3.0930 (0.0904) | 3.8246 (0.0452) |
| Sep core, published | 0.3165 | 2.9025 | 2.9227 | 3.1212 |
| Sep headline, published | 0.4908 | 3.5582 | 3.3355 | 3.6489 |

**Time series (`A_ts_pce_rates.csv`)**: 212 rows, Jan 2018–Sep 2026 published + Oct 2026 `est.`; Sep 12m checks pass (3.649 / 3.121).

**Backtest (`A_backtest.csv`)**, first-release variant, n=10 (Dec 2025–Sep 2026), error = estimate − BEA first print (pp):

| | Bias | MAE | RMSE |
|---|---|---|---|
| Our core | +0.0169 | 0.0423 | 0.0489 |
| Cleveland core | −0.0398 | 0.0677 | 0.0783 |
| Core-CPI benchmark | −0.0706 | 0.0874 | 0.0995 |
| Our headline | +0.0179 | 0.0401 | 0.0452 |
| Cleveland headline | −0.0366 | 0.0614 | 0.0726 |

"Core CPI alone" = build's `bench2_core_cpi_ols` (expanding-window OLS of core PCE m/m on core CPI m/m), not raw core CPI. No headline CPI benchmark.

**Outside, existing (`A_outside_existing.csv`)**: 9 rows, tier + pre/post-PPI added. Bowman upgraded to primary [O] from the saved RTF: "Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3.3 percent in October…" (12m core only; pre-PPI, Nov 10). Prior StockTitan wording was a paraphrase. Cleveland labelled "model nowcast, no PPI".

**R4 Sep check (`A_r4_sep_check.csv`)**: index levels 3.649 / 3.121; BEA text 3.6 / 3.1; Waller 3.7 / 3.1; Logan 3.6 / 3.1; Paulson 3.6 / not stated; Jefferson 3.6 / 3.1. Only Waller's headline differs; his m/m figures (0.5, 0.3) match BEA. No vintage found that gives 3.7.

**R5 Cleveland (`A_r5_cleveland.csv`)**: 60 daily rows, all "carried forward: Nov 14 pull; re-pull Nov 18". Latest: core 0.2669 m/m / 3.2134 y/y; headline 0.3051 / 3.8114.

**Cross-checks**: Bowman 3.3 vs ours 3.24 (+0.06; sits with pre-PPI cluster). No official gave an Oct headline figure. Pace 2025 used "three-month core PCE has increased above its six-month measure"; our Oct est. satisfies it (3.55 > 2.95).

## Worth a look (agent)
1. Core 3m > 12m > 6m ordering: 12 months since Jan 2018; last before Oct 2026 est. was Oct 2024. Headline: 13 months, last Oct 2025.
2. Ordering driven by low Jun/Jul 2026 core m/m (0.133, 0.138) inside the 6m window.
3. Core 12m 3.242 highest since Nov 2023; headline 3.825 highest since May 2023; core 3m 3.55 last matched Apr 2026.
4. Core 3m > 6m was false May–Sep 2026; the Oct "acceleration" signal is new and rests on our estimate.
5. Waller 3.7 vs BEA 3.6 unexplained (only PDF saved).
6. Opposite backtest biases (ours +0.017, Cleveland −0.040); Oct gap ours−Cleveland +0.028 has the same sign.
7. Backtest caveats: current-vintage components/weights; only Aug–Sep 2026 on current method table; Jan/Feb 2026 first prints delayed.
8. Oct 2025 base level (core 127.165) built by BEA without most Oct 2025 CPI; treatment not investigated.

## Spot-check examples (agent)
1. `A_headline.csv` core 3m: 3.55080 vs tab C10 3.55082.
2. `A_ts_pce_rates.csv` 2026-09 core/headline 12m: 3.12116 / 3.64887.
3. `A_backtest.csv` summary rows vs `04_oct_pce_build/outputs/D2_backtest_variant_first_release_pm.csv`.
4. `A_r4_sep_check.csv` Waller headline 3.7 (PDF p.3).
5. `A_outside_existing.csv` Bowman row (RTF, Inflation section).

## What to verify (agent)
Waller 3.7 on Fed HTML; Bowman live URL; Oct 2025 base; press rows not re-checked; Cleveland re-pull Nov 18; `A_outside_existing.py` needs macOS `textutil`.

## Coordinator review
**Verified independently** (own script, `scratchpad/verify_A.py`, from T20804 Nov 10 JSON, build summary and D2 backtest file):
- Sep 12m: core 3.1212, headline 3.6489 ✓.
- Oct est. from estimate_mm × Sep level: core 12m 3.2424, 3m 3.5508, 6m 2.9477 ✓; headline 12m 3.8246, 3m 4.6224, 6m 3.0929 (agent 3.0930; rounding) ✓.
- Backtest from D2 month rows (`in_rule=True`, `miss_variant`): core n=10, MAE 0.0423, bias +0.0169; headline MAE 0.0401, bias +0.0179 ✓.
- Waller PDF text: "rose at a monthly rate of 0.5 percent in September and 3.7 percent over the previous 12 months" ✓ (quote confirmed).
- Bowman RTF via textutil: "Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3.…" ✓.
- Ordering count: re-ran on `A_ts_pce_rates.csv`; core matches 12 months (2018-11 … 2024-10, 2026-10) ✓; agent's parenthetical list omitted 2018-11/12, 2019-01, 2019-06 but the count and "last Oct 2024" are right. Headline 13, last 2025-10 ✓.

**Corrected**: none in files. Label fix for the workbook: "core CPI alone" → "core-CPI regression benchmark" (Eli's roadmap wording would mislead).

**Could not check**: Fed HTML of Waller; Oct 2025 base construction.

**Coordinator Worth a look**: Sep 12m headline 3.649 rounds to 3.6 but is 0.001 from the 3.65 rounding boundary — a vintage revision of +0.001 would make it 3.7 at 1dp under round-half-up. That is the most likely innocent explanation for Waller's 3.7 (unverified).

**Interpretive notes (not shared unless asked)**: the "accelerating" read rests on 3m > 6m, which flips only with the October estimate; the band on core 3m (±0.20) does not overturn it (3.35 > 2.95+0.10).
