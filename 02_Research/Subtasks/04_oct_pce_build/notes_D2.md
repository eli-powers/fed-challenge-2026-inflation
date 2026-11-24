# Notes D2: backtest variant with first-release portfolio-management PPIs (Opus 5.5, 2026-11-12)

Labeled **variant**, not the decision run. Script: `code/D2_variant_first_release_pm.py` (run from project root with `python3`).
Outputs: `outputs/D2_backtest_variant_first_release_pm.csv` (+ `_meta.csv`), `outputs/D2_remaining_revised_ppi.csv` (+ `_meta.csv`).
No existing file was modified; the existing D_ modules are imported unchanged and the swap is an in-memory subclass of
`Engine` (`PMSwapEngine.series_mm`). Bytecode writing is switched off so `code/__pycache__` is not touched. No Oct 2026 estimate.

## What changes
Line 268 (portfolio management) in old-table months (Nov 2025; Dec 2025 – Jul 2026) is priced from the same-report
first-release m/m of `PCU5239405239401` and `PCU5239405239402` (`outputs/E_pm_ppi_first_release.csv`, `first_print_mm_pct`)
instead of today's revised values. Blend weights unchanged (0.8465 / 0.1535, fitted 2017–2020). Aug–Sep 2026 use the current
table, where 268 is assumed (12-month carry-forward), so they are identical to the main run.

## Reproduction gate (swap off)
All 22 month × measure build estimates (rule months + Nov 2025) round to the saved 4-decimal values in
`outputs/backtest_results.csv`. Max |harness − saved|: core 4.5e-05, headline 4.3e-05 (rounding of the saved file only).

## Results (rule months Dec 2025 – Sep 2026, n = 10; vs BEA first print)
| | bias | MAE | SE | MAE ± 1 SE | RMSE | largest miss | 1dp hits |
|---|---|---|---|---|---|---|---|
| core main | +0.0199 | 0.0405 | 0.0086 | 0.0318 – 0.0491 | 0.0480 | +0.0929 (Sep 26) | 0.4 |
| core variant | +0.0175 | 0.0429 | 0.0088 | 0.0342 – 0.0517 | 0.0504 | +0.0929 (Sep 26) | 0.4 |
| headline main | +0.0205 | 0.0386 | 0.0073 | 0.0313 – 0.0459 | 0.0444 | +0.0856 (Sep 26) | 0.5 |
| headline variant | +0.0184 | 0.0407 | 0.0076 | 0.0331 – 0.0482 | 0.0466 | +0.0856 (Sep 26) | 0.5 |

MAE variant − main: core +0.0025, headline +0.0021. Threshold leg (core): main **pass** (upper 0.0491 < 0.05); variant
**inconclusive** (upper 0.0517 includes 0.05). Nov 2025 (excluded): core miss +0.0315 → +0.0321; headline −0.0099 → −0.0093.

Largest month effects (core, variant − main): Dec 2025 +0.0218 (PM first release +2.01% vs revised +0.64%),
Jan 2026 −0.0207 (PM +1.48% vs +2.71%; IA +0.08% vs +0.62%), Apr 2026 −0.0194 (IA −2.89% vs +0.90%). Others < 0.003.
Per-month 1-decimal hit/miss is unchanged in every month for both measures.

## Remaining revised-data PPIs in the variant (rule months)
| series | line | rule months | mean line weight core / headline |
|---|---|---|---|
| PCU5231505231501011 | 262 | 10 | 0.050% / 0.045% |
| PCU5231505231501012 | 263 | 10 | 0.024% / 0.021% |
| PCU5231505231502011 | 265 | 10 | 0.034% / 0.030% |
| PCU5231505231502012 | 266 | 10 | 0.054% / 0.048% |
| PCU523150523150102 | 267 | 10 | 0.057% / 0.050% |
| PCU5132105132107 | 50 (blend input, fitted share ~0.15) | 2 (Aug, Sep 2026) | 1.25% / 1.12% (whole line) |
Lines 262–267 together ≈ 0.21% of core. Matches the brief's expectation. Nov 2025 also uses the five `PCU523150…` revised.

## Judgment calls
1. Swap months = Nov 2025 + Dec 2025 – Jul 2026 (the months priced with an old table, where 268 uses the two PPIs).
2. Real-time change = `first_print_mm_pct` (reference month over prior month within one BLS report), per brief. Check:
   every PCE first-print vintage falls after that report and before the next PPI report (e.g. Dec 2025: PPI Jan 30,
   PCE Feb 20, next PPI Feb 27), so the same-report change is the latest PPI information BEA could have had.
3. Old-268 blend weights kept as in the main run (fit on revised history 2017–2020); not refitted.
4. Window K = 12 read from `backtest_window_choice.csv`; not re-selected.
5. Reproduction criterion: `round(harness, 4) == saved` for every core row (saved file is 4-dp).
6. Metrics as in the main run: SE of MAE uses SD with ddof = 1; 1dp hit uses round-half-up of the estimate vs the
   first print's 1dp value; threshold leg evaluated on unrounded MAE ± SE.
7. "MAE difference" = variant MAE − main MAE.

## Worth a look
- The main run's threshold-leg pass was already marginal (upper end 0.0491; notes_D log item 4 shows it flipping on a
  numerical fix). Switching to the more faithful real-time PM inputs pushes it to inconclusive (0.0517). The revised
  PM PPIs happened to track BEA's first print better than the first-release ones did.
- The Dec 2025 and Jan 2026 PM first releases largely offset each other (+0.022, −0.021 core), consistent with BLS
  revising Dec down and Jan up; the Apr 2026 IA sign flip moves core −0.019 and *improves* that month's miss.
