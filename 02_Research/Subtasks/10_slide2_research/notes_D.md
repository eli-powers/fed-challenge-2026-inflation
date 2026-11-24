# Notes, Agent D (Q12 stress test), 2026-11-15

## Run order
From the project root, `python3 -I`. Each script asserts the slide 1 reproduction (core leaf 12m 60.626 / 54.038, 3m 44.814 / 45.467); all pass.
1. `code/D_threshold_sensitivity.py`. It goes first because D_preshock reads its time-series output.
2. `code/D_band_and_exclusions.py`
3. `code/D_trimmed_reconcile.py`
4. `code/D_preshock.py` (reads `D_threshold_ts.csv`, `A_q3_tagged_breadth_ts.csv` and `C_q8_oil_daily.csv`; asserts tag-group breadth equals A's series to 0.01)
5. `code/D_tag_variants.py`
6. `code/D_hospital_ts.py`
7. `code/D_hospital_flip.py`
8. `code/D_headline_mechanics.py`

Engine: `09_slide1_research/code/C_common.py` (directly, or via `A_common.py`), read-only. No downloads; no raw files created.

## Method notes
- **Threshold runs.** Same unit tables as the binding method, with only `thr` changed. Core goods = core leaves with line < 150 (as B). Percentiles are weighted by start-of-window weights, taking the first leaf whose cumulative weight reaches q.
- **Trimmed mean replication.**
  - Universe: 177 headline leaves (Dallas uses 178 components; ours are BEA's current leaves).
  - Monthly m/m changes; weights are previous-month nominal shares. Check: Rx drugs Aug share 2.764% vs Dallas Sep-table weight 2.765%.
  - Trim: 24% lower and 31% upper tail, with a fractional boundary weight. 12m = product of 12 monthly trimmed means.
  - Matches published Sep 2026 to ≤ 0.008 pp at 1m, 6m and 12m. The Oct 2026 version uses UMD est. leaf m/m.
  - The "kept months" comparison uses simple ×12 annualization of the average m/m (labelled as such).
- **Pre-shock month.** Feb 2026 is the last month before monthly-average Brent jumped ($70.9 Feb → $103.1 Mar), from `C_q8_oil_daily.csv`. The 12m window ending Feb 2026 is therefore entirely pre-shock.
- **Hospital flip.**
  - NSA input = pi − adj_b = 0.305 + 0.372 = 0.677, which equals the published Oct 2026 PPI 622 prelim (B).
  - Needed SA 0.5639 comes from `C_flip_distance_oct.csv`.
  - The historical seasonal gap is from B's October table (2017–25, n = 9). Revisions: ALFRED first print vs the 2026-11-11 vintage, n = 22.

## Findings beyond the brief (flag to coordinator)
1. **GO Q4b (breadth vs trimmed mean) was not in brief_B and is not in report_B.** I answered it with data in D_qa_prep #11. It is a scope gap the coordinator should log.
2. Core 12m breadth at 3% is dominated by two near-line blocks: OER (13.1%, 12m 3.06–3.76 since Sep 2025) and hospitals (8.7%, 2.74–3.97).
   - Hospitals crossed 3% at 12m in Feb (out), Mar (in) and Oct est. (out), moving core breadth ±8.7 pp each time (`D_hospital_oer_ts.csv`).
   - Feb → Sep core +7.7 pp is mostly hospitals re-entering, the mirror of the Oct drop.
3. 12m breadth within the energy group has not risen since Feb under any variant; the mean rate has. The breadth exhibit may be the wrong lens for "spread at what scale": the energy shock shows up in rates, not in the count above 3%.
4. Headline vs core: headline is not mechanically higher (food offsets energy). The roadmap backup line should change.
5. Leaves 51 (calculators etc.) and 71 (phones) have identical rates (−12.67% 12m Sep; −7.83% 3m). They are probably priced on the same index. Not checked.
6. 3m breadth at 2.5% jumps 54.4 → 68.2 Sep → Oct est., because ~17.5% of weight (hospitals, rent) moved from (2.0, 2.5] into (2.5, 3.0].
7. The Dallas-method 12m trimmed mean fell 2.76 → 2.27 (Sep 2025 → Sep 2026) while core 12m breadth rose 58.8 → 60.6.
8. Bowman's text says "may be broadening", which contradicts the roadmap's "concentrated fits Bowman".
9. Roadmap: "the comparison to Waller's '>70%', on his basis (core services, count of items)". But count gives 63.1; only weighted reproduces >70 (B). The roadmap wording conflicts with the result.

## Limits
- Not checked: the electricity vs petroleum split of the energy-tag I-O shares (needs a `tag_exposures.py` rerun by commodity).
- Waller's actual basis, Bowman's method, passenger-demand data: unavailable.
- All spoken answers are drafts for Eli. No policy recommendation is made.
