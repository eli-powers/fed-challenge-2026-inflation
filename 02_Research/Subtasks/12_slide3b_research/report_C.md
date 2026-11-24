Status: Audited — converged R2 (Codex, Nov 15)

# Agent C report: forecast pipeline and scenario results (Opus 5.5, 2026-11-15)

Q4 SPF not out at run time; all results use the **Q3 SPF**.

## Findings
**Q5 Pipeline `03_Data/pipelines/forecast_3b/`** (code/, config/, raw/, processed/, archive/, tests/, README.md)
- `code/fetch_inputs.py`: new `raw/<date>/` (never overwrites; `_2`, `_3`); SPF medianLevel, Dispersion_1, release dates; STEO outlook page + latest vintage + vintage matching the SPF deadline + one before + feb26; EIA daily Brent; FRED PCEPILFE. Staged, validated, renamed; on failure exits 1 and names the previous folder (tested with a bad URL). Today's pull byte-identical to A/B raw copies (6 files, sha256). No key in any file.
- `code/forecast.py`: `--spf`, `--raw`, `--compare`; `REGIME_WEIGHT_POST = None  # Eli's input after slide 3A; None = no weighting`. Outputs `processed/scenario_grid_<spf>.csv` (`is_central` marks the 6 cells), `fan_<spf>.csv` ("SCENARIO RANGE ... NOT a probability fan"; SPF P25/P75 where published), `sensitivity_proxy_`, `oil_paths_`, `oil_assumption_`, `metadata_<spf>.json` (sha256, vintages, params). `--compare` → `vintage_compare.csv` once Q3 and Q4 both present.
- Method: baseline = actual 2026Q1–Q3 (Q3 2.468) then SPF medians (2027Q4 = 2.2679 derived). Gap = 100·ln(scenario Brent / Aug-STEO assumption) from 2026Q3; proxy rule = latest STEO released on/before the SPF deadline. L_t = Σ R_{t−s}Δg_s/10 with exact compounding. **Actual quarters not adjusted**; first applied change 4·(L_26Q4 − L_26Q3). Q4/Q4 from the quarterly path incl. actuals; SPF published annual median alongside.
- Cross-checks vs B: paths within 0.0005 $/bbl; gaps within 0.0008 log pts; 2027 Q4/Q4 adjustments match after compounding (P1 post B 0.513 → 0.527 here).
- Q4 readiness: exact commands in README; synthetic-Q4 dry run (scratch only) works end to end (2027Q4 becomes published, gap starts 2026Q4, proxy → nov26, compare runs). Not tested on a real Q4 file.
- Tests (`tests/test_zero_gap.py`, all pass): zero gap == baseline exactly (30/30 rows); constant +10% gap → L_k == R_k k=0..12, all regimes, matches B's `map_gap_to_core`; linearity exact for L and 4ΔL (exact-compounded quarterly ratio 2.001–2.013, second order).

**Q6 Results** (SPF 2026Q3 baseline; Aug-STEO proxy; Brent to Nov 11; PCEPILFE vintage Oct 29; core PCE, SA, %)

| Cell | 2026Q4 q/q ann. | 2027Q4 q/q ann. | 2026 Q4/Q4 | 2027 Q4/Q4 |
|---|---|---|---|---|
| Baseline | 2.616 | 2.268 | 3.082 | 2.400 |
| P1 STEO × pre / post | 2.812 / 2.732 | 2.346 / 3.137 | 3.131 / 3.111 | 2.399 / 2.927 |
| P2 $110 × pre / post | 2.848 / 2.765 | 2.422 / 3.598 | 3.140 / 3.119 | 2.482 / 3.163 |
| P3 Hormuz+$25 × pre / post | 2.721 / 2.647 | 2.417 / 2.785 | 3.108 / 3.090 | 2.418 / 2.721 |
| Spread (max − min) | 0.202 | 1.252 | 0.051 | 0.764 |

SPF published Q4/Q4: 2026 3.2876, 2027 2.4004 (2027 baseline = 2.4004 by construction).
- Axis comparison (range, pp): 2027Q4 q/q ann.: across oil paths pre 0.08, post 0.81; across regimes P1/P2/P3 0.79/1.18/0.37. 2027 Q4/Q4: across oil paths pre 0.08, post 0.44; across regimes 0.53/0.68/0.30.
- Sensitivity, 2027 Q4/Q4 pre/post (`C_q6_sensitivity.csv`, non-central): P1 futures 2.41/2.90; P2 Oct avg 2.50/3.32; P3 +$20 2.41/2.64; +$30 2.43/2.80; +$0 2.34/2.25; Jan–Feb spot+$25 2.45/2.95. Proxy (post, P1/P2/P3): Jul STEO 3.16/3.39/2.95; futures hybrid 2.83/3.06/2.62.
- Jump-off (`C_q6_jumpoff.md`): Oct est. m/m 0.29507 → 3.242% y/y. Given Oct, SPF 2026Q4 2.6158 needs Nov–Dec m/m 0.053% each; the six cells need 0.061–0.110%. Oct pace repeated → 2026Q4 3.61, 2026 Q4/Q4 3.33.
- Double counting: 2026Q3 actual, not adjusted. 2026Q4 adjustment (+0.03 to +0.23 pp) is added to an SPF path that predates the Sep–Oct spike (respondents' own oil assumptions are unpublished, and Aug 11 spot was already $93.26, so some overlap with the proxy timing can't be ruled out; R1 audit wording): not a double count of the spike; would be one only if re-anchored on Oct data and then adjusted. Larger exposure: in the post regime the 2026Q3–Q4 gap steps account for 92–134% of the 2027 Q4/Q4 adjustment (realized 2026Q3 step alone 35–84%). Pre regime: 2026H2 part ≤ +0.04 pp. Flag only.
- Hand-check (`code/C_q6_handcheck.py`, no pipeline import): post × P2 matches at 2026Q4, 2027Q1, 2027Q4 and both Q4/Q4, max |diff| 4e-7 pp.

## Slide-worthiness
- 3×2 grid table 5/5 — the slide's core; lead with Q4/Q4; date the baseline (Aug 11).
- Scenario-range chart 3/5 — quarterly range lumpy (2027Q4 post 3.60); use Q4/Q4 bars or label strongly.
- Axis comparison 4/5 — oil paths 0.08 (pre) vs 0.44 (post) against regimes 0.30–0.68 (2027 Q4/Q4).

## Worth a look
1. Jump-off gap ≈1 pp: Oct-pace 2026Q4 3.61 vs cells 2.65–2.85; bigger than any oil adjustment for 2026Q4.
2. 2027 adjustments come mostly from oil moves already realized (2026H2 steps).
3. 2026Q4 is higher under pre than post in every path (post response dips at k=1, 0.0184 → 0.0105).
4. 2027Q4 quarterly spikes under post (P2 3.60, P1 3.14) from the k=4 jump hitting the large 2026Q4 gap step.
5. Proxy choice moves P1 post 2027 Q4/Q4 by 0.33 pp (Jul STEO 3.16 / Aug 2.93 / futures 2.83), comparable to the oil-path axis.
6. P3 +$0 × post is the only cell below baseline (2027 Q4/Q4 2.25).
7. P1 × pre 2027 Q4/Q4 −0.002 pp vs baseline.
8. On the Q4 SPF, P1's gap ≈ 0 by construction (latest STEO = matched proxy); grid shifts between vintages partly via proxy change (synthetic dry run only).
9. SPF 2026Q3 miss (2.70 vs 2.47) not explained by oil here (modelled 2026Q3 impact +0.09 pp ann.).

## Spot-check examples
1. `processed/scenario_grid_2026Q3.csv` line 79 (P2 × post, 2027Q4): gap 52.609, L 0.8006, adj 1.3305, scenario 3.598351. 2. line 21 (P1 × post, 2027 Q4/Q4) 2.927278. 3. `processed/fan_2026Q3.csv` line 11: 2.3988–3.1629. 4. `outputs/C_q6_sensitivity.csv` line 69: 2.2496. 5. `outputs/C_q6_jumpoff.md` §1: 0.053%.

## What to verify
Real Q4 SPF rerun (deadline; Dispersion_1 Q4 row); leaving actual 2026Q3 unadjusted; 10% vs 10 log pts (×1.049); Q4 splice holiday gaps; Yahoo futures [2]; Nov 18 rerun after EIA Brent update.

## Coordinator review
**Verified:**
- Reran `tests/test_zero_gap.py` myself: ALL TESTS PASSED (zero-gap exact, +10% step reproduces R_k, linearity).
- Reran `forecast.py --spf 2026Q3`: outputs regenerate; 2027Q4 central cells 2.346/3.137, 2.422/3.598, 2.417/2.785 — match the table.
- Independent hand calc (own script, no pipeline import; Fig. 2 post table, Aug STEO, P1 path): P1 × post 2027 Q4/Q4 2.9256 vs pipeline 2.9273; 2027Q4 q/q 3.1334 vs 3.1373. Differences ≤0.004 pp from my rounded inputs (85.26 vs 85.257 etc.) — accept.
- README has exact Q4 rerun commands; no key strings in pipeline files.
**Corrections:** none.
**Not checked:** fetch failure path (agent-reported test); synthetic Q4 dry run (scratch, not saved).
**Interpretive notes (kept here):** the oil axis only matters under the post regime; the regime axis is the bigger lever. The 2026Q4 jump-off gap (Oct pace) dwarfs the oil adjustment — this is the strongest "your baseline is stale" attack and needs a disclosed answer.
