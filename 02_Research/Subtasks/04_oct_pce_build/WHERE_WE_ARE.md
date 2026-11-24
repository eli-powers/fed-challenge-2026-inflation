# Where we are: October 2026 PCE build

**As of:** 2026-11-11, late evening. **Next hard date:** October PPI, Fri Nov 13, 8:30 AM. Cutoff Nov 18.

**Update, 2026-11-14. Checkpoint D decided (Eli):** our October estimate is the presentation default, always shown corroborated against the Cleveland Fed nowcast and other forecasters. Build closed.

**Update, 2026-11-13, 1:45 PM.**

- **Decision basis:** first-release variant (Eli, Nov 13). Threshold leg inconclusive, so the default placement is a cross-check next to Cleveland.
- **October build done** (not audited): core 0.295 m/m, 3.24% y/y; headline 0.318 m/m, 3.82% y/y. Details in `report.md`, last section.
- **Walkthrough notebook** for the 4:45 meeting with Professor Aruba: `oct2026_pce_walkthrough.ipynb`. Open in VS Code, pick the `/opt/anaconda3` kernel, Run All.
- **Band:** variant RMSE, core ±0.0489, headline ±0.0452 (Eli, Nov 13).
- **Audit 2 (October build) converged R1** (Nov 13): no blocking findings.
- **Open:** Checkpoint D (placement).

**Update, 2026-11-12 evening. Read this first; it supersedes the afternoon update below where they differ.**

- **Audit 1 converged in round 2.** One blocking finding (legal services starts in 2024, not 2021) was fixed and everything rerun.
- **Backtest now, core vs first print, n = 10:** main run MAE 0.0399, SE 0.0080, range 0.0319–0.0478 (pass). Variant with first-release portfolio-management PPIs: 0.0423, SE 0.0081, range 0.0342–0.0505 (inconclusive). Benchmarks: core CPI alone 0.0874; Cleveland 0.0677.
- **Reported band:** ±0.0465 pp on core m/m, plus 0.008 pp for portfolio management.
- **Open with you:** which run the decision rule rests on. My recommendation is the variant. It doesn't block the build.
- **Friday steps are unchanged** (see below). The build script still exits cleanly on 2026-10 until October PPI is in.

**Update, 2026-11-12 afternoon.** This section replaces the Nov 11 status below where they differ.

- **Checkpoint C done.** Backtest, rule months Dec 2025 – Sep 2026 (n = 10), core vs BEA first print: build MAE 0.0405, SE 0.0086 (range 0.0318–0.0491); core CPI alone 0.0874; Cleveland nowcast 0.0677. Both legs of the decision rule pass, the threshold by 0.0009 pp. Recorded as "pass under the locked rule, margin within implementation noise." Slide placement is decided at Checkpoint D.
- **Reported band:** ±0.048 pp on core m/m, plus 0.008 pp for portfolio management.
- **Sensitivity** (8 PPIs without first-release history treated as assumed): core MAE 0.0597, SE 0.0145.
- **Rate-change check** on the bank-services lines: done; the reported band doesn't change (`outputs/K_event_check_rates.csv`).
- **Running:** Codex Audit 1, round 1 (`06_Audits/04_oct_pce_build/`), and agent E (first-release values for the two portfolio-management PPIs from archived BLS reports, time-boxed).
- **Frozen while Codex runs:** every file in this folder except those prefixed `E_`.
- **Friday Nov 13, after 8:30 AM:** in `code/C2_fetch_bls.py` and the file pattern in `code/C2_build_history_coverage.py`, set the date to 2026-11-13; run both; then `python3 code/D_build.py --month 2026-10` from the project root (full steps in `code/README.md`). Do **not** rerun `D_backtest.py`. BLS's API returned HTTP 503 on the morning of Nov 12, so allow for retries.
- **Then:** Checkpoint D (you review the October number), Audit 2.

## Done

- **Step 0 stress test** and **Checkpoint A**: `stress_test.md` (your decisions are in its "Checkpoint A outcome" section).
- **Mapping** and **Checkpoint B (approved Nov 11)**: `outputs/component_mapping.csv`. 224 pricing lines, 99.7% of PCE.
- **Backtest targets and benchmarks**: first-print core and headline PCE, core CPI first prints, the Cleveland Fed nowcast archive (all in `outputs/`).
- **BEA method facts**: portfolio management, legal services and software all changed on Sep 30, 2026. Earlier versions of BEA's source table are saved.
- All three agent reports, with my verification, are in `report.md` (status: Round 1, not audited).

## Numbers to remember

| Item | Value |
|---|---|
| Observed, BLS series as published | 68.2% of headline, 66.1% of core |
| Observed, needs our seasonal estimate | 18.7%, 21.1% |
| Observed blend, weights not stated by BEA | 2.6%, 1.2% |
| Assumed | 10.1%, 11.4% |
| Cleveland Fed October nowcast (Nov 10) | core PCE 0.27 m/m, 3.21 y/y; headline 0.31, 3.81 |
| Cleveland core nowcast error, Dec 2025 – Sep 2026 | MAE 0.068 pp, bias −0.040 |
| Latest core PCE first print (Sep 2026) | 0.3165 m/m, 3.12% y/y |

## Your Checkpoint B decisions (all seven defaults accepted)

1. Tenant rent sub-lines: 100% CPI rent, flagged as our assumption.
2. Unstated blend weights: CPI relative importance where it exists; otherwise fitted on BEA's component history, equal weights as fallback.
3. Portfolio management in October: assumed (carried forward). The old PPI is a sensitivity only.
4. The uncovered 0.30% (two net travel lines): left out, weights rescaled.
5. "Data available at the time": everything published by the day after that month's PPI release.
6. Backtest methods by month: old sources for Dec 2025 – Jul 2026, current sources for Aug – Sep 2026, reported separately.
7. The observed share is always reported with the three-way split, not as a single 89%.

## In flight

- **Round-2 data pull (agent C2)** was launched Nov 11: the 277 component series, PPI as first released, and seasonal-revision sizes. Its outputs land in `outputs/component_series_*.csv` and `outputs/ppi_first_release.csv`. **Not yet verified by me.** Brief: `brief_C2_component_data.md`.

## Not started

- **Agent D (methods and backtest, Opus 5.5)**: not briefed or launched. I held it because your usage ran out. It is the next step and the largest one.
- Checkpoint C (backtest vs. the decision rule), Audit 1 (Codex), the Nov 13 build, Checkpoint D, Audit 2.

## Tomorrow, in order

1. Verify the round-2 data pull.
2. Write agent D's brief from `stress_test.md` §5–6 plus the seven decisions above, and launch it.
3. Checkpoint C when the backtest returns, then Audit 1.
4. Timing is tight: the brief wanted the backtest and Audit 1 finished before Friday 8:30 AM. If Audit 1 hasn't converged, the build runs anyway and nothing is called slide-ready until both audits converge.

## Flags still open

- **Core flag error in the existing price-basket pipeline** (16 components mislabeled; pipeline core weight 90.9% vs BEA's 88.9%). Separate task; brief at `02_Research/Subtasks/05_fix_core_flag/brief.md`. This build is not affected.
- **Only two backtest months (Aug, Sep 2026) used BEA's current methods.**
- **Portfolio management (1.69% of PCE) can't be tested**; its October value is carried forward.
- **Cut order** if time runs short is still undecided (headline vs. the Oct 2023–24 seasonal check).
- The Worth a look items in `report.md` have not yet been copied to `04_Ideas/questions_log.md`.

## To resume

Open a window in this project and say: "Read `02_Research/Subtasks/04_oct_pce_build/WHERE_WE_ARE.md` and continue from 'Tomorrow, in order'."
