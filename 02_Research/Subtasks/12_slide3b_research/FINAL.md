# Slide 3B research: FINAL

## 1. Status
**Status: Audited — converged R2 (Codex, Nov 15).** R1 found 1 Blocking item (the workbook builder could not run on the Q4 SPF) and 2 non-blocking; all fixed, plus a saved synthetic-Q4 regression test. R2 converged; its 3 non-blocking items were fixed. No factual, source or arithmetic item is open. Agents A–D ran (Sonnet A; Opus B, C, D), and the coordinator verified each load-bearing number independently. The Q4 2026 SPF was **not released** at build time (404 at ~17:40 ET Nov 15). **Update Nov 16: the Q4 SPF was released and the pipeline and workbook were rerun on it; see §1b.** §§2–9 below describe the **Q3 2026 SPF** run unless marked; the audit (R1–R2) covered the Q3 run only.

Deliverables:
- **Workbook:** `01_Finals/data/Slide3B_Inflation_Data.xlsx`, now built on the **Q4 SPF** (`--spf=2026Q4 --verify`: 431 live formulas, 0 mismatches, 0 errors, 67 checks against the pipeline). The Q3 version (464 formulas, 72 checks; 6 charts rendered and inspected Nov 15) is saved as `outputs/Slide3B_Inflation_Data_Q3SPF_2026-11-15.xlsx` and rebuilds with `--spf=2026Q3`.
- **Pipeline:** `03_Data/pipelines/forecast_3b/` (README, zero-gap test).
- **Reports:** `report_A.md` … `report_D.md`.
- **Q&A prep:** `outputs/D_qa_prep.md`.

## 1b. Q4 SPF rerun (Nov 16; not audited by Codex)
**Run.** `fetch_inputs.py` → raw `03_Data/pipelines/forecast_3b/raw/2026-11-16/`; `forecast.py --spf 2026Q4`; `--spf 2026Q3 --compare` (`processed/vintage_compare.csv`); zero-gap test on Q4: all pass; workbook rebuilt and verified (above). The Q3 grid reproduces unchanged on the new raw folder. Synthetic-Q4 regression test still passes after the text-tab changes.

**Inputs.** Q4 SPF deadline **Nov 11**, released Nov 16. Matched oil proxy: **Nov STEO** (released Nov 10), which is also Path 1, so P1's gap is ~0 from 2027Q1 (premise 3, §2, now realised). The Q4 survey publishes 2027Q4 directly (no derived quarter). Dispersion_1 Q4 row present (2027Q4 IQR 2.20–2.51). Brent to Nov 11 ($92.14); core PCE through Sep (FRED vintage Oct 29).

**SPF median core PCE, Q3 → Q4 survey** (q/q ann.): 2026Q3 2.70 → 2.50 (actual 2.47); 2026Q4 2.62 → **3.00**; 2027Q1 2.58 → 2.71; 2027Q2 2.43 → 2.60; 2027Q3 2.33 → 2.41; 2027Q4 2.27 (derived) → **2.36** (published). Q4/Q4: 2026 3.29 → 3.18; **2027 2.40 → 2.50**; 2028 2.16 → 2.20.

**Grid, 2027 Q4/Q4** (baseline built from the quarterly path: 2.52; published median 2.50):

| Oil path | Post-pandemic | Pre-pandemic | Q3-run post / pre |
|---|---|---|---|
| P1 Nov STEO | 2.52 | 2.52 | 2.93 / 2.40 |
| P2 $110 flat | 2.75 | 2.61 | 3.16 / 2.48 |
| P3 Feb STEO + $25 | 2.31 | 2.54 | 2.72 / 2.42 |

- Range across the six cells: **2.31–2.75** (Q3 run: 2.40–3.16). 2026 Q4/Q4: 3.15–3.19. 2026Q4 q/q ann.: 2.90–3.03.
- **Axis comparison flips.** Oil path moves 2027 Q4/Q4 by 0.08 (pre) and **0.44** (post); regime moves it 0.01 (P1), 0.15 (P2), 0.23 (P3). In the Q3 run the regime axis was the larger (0.30–0.68).
- **P3 is now below baseline under post** (2.31), because the Nov STEO the baseline is taken to assume sits above P3's path.
- **Sensitivities (2027 Q4/Q4, post):** Oct STEO as proxy, P1 2.57 (+0.05); P2 at the Oct-average flat 2.91; P3 +$0 1.84, +$20 2.23, +$30 2.39. No futures-curve proxy for Q4 (no Nov 11 curve saved).
- **Jump-off:** the Q4 SPF's 2026Q4 of 3.00 needs Nov–Dec core m/m of **0.147%** given our Oct 0.295 (Q3 SPF: 0.053%, reproduced).
- **Vintage gap, stated without reading:** the SPF moved its 2027 Q4/Q4 median up 0.10 between surveys; the Q3-run P1 × post cell sat 0.53 above the Q3 baseline.
- **Not recomputed for Q4:** the Q3 run's "flat Nov 11 spot → 2.93" and "$60 break-even" (§3). Those are Q3-baseline numbers; do not quote them against the Q4 baseline.

**Text updated for Q4:** workbook Slide_worthiness, Judgment_calls (new item 2: P1 near-baseline by construction), READING_GUIDE, README, SEP note, Baseline notes; D's Q&A #7–8. Still Eli's: which vintage leads (§7 item on Q4 SPF), and the new P1 item.

## 2. Premise disagreements (flagged; I did the conservative version, which is the locked design)
1. **Waller's $20–30 is not a "residual premium after reopening."** His speech gives it as the cost of passage *now*, while traffic is increasing ("even as there is increased tanker traffic through the Strait of Hormuz, that traffic is moving at great expense … reportedly boosting oil prices by $20 to $30 a barrel"). Carrying it past a reopening is our extrapolation.
   - Kept: +$25 as the locked central value. Shown alongside: +$0, +$20 and +$30.
   - +$0 is the only disinflationary cell: 2027 Q4/Q4 is 2.25 post and 2.34 pre.
2. **The baseline's problem in 2026 is bigger than oil.**
   - Given our October estimate (0.295 m/m), the SPF's 2026Q4 (2.62% annualized) needs Nov–Dec core of only **0.053% m/m**.
   - The oil adjustment cannot fix that. Every 2026 number in the grid (3.09–3.14 Q4/Q4) sits below the SPF's own 3.29, the SEP's 3.4 and Oct-pace 3.33.
   - Kept: the pure SPF baseline, unadjusted for this (locked), with the gap disclosed. The workbook leads with 2027.
3. **On the Q4 SPF, the "baseline oil" path stops being a scenario.** The proxy rule picks the latest STEO before the Q4 deadline (the Nov STEO), so Path 1's gap is about 0 by construction. The message then moves from "the regime matters even at today's expected oil" to "the regime matters only if oil departs from November expectations." Same method, different story; Eli picks the lead vintage (§7).
4. **The regime axis only touches the oil gap.**
   - The note's higher persistence (sum of the two core lags rising from 0.35 to about 0.65) would also slow the baseline's own disinflation. The grid leaves that path as the SPF had it.
   - It also applies a five-economy average response to US core PCE.
   - Disclosed; not changed.

## 3. Bottom line (data only)
- **Baseline.** The Q3 SPF (deadline Aug 11, before the Sep–Oct spike) has core PCE at **2.40% Q4/Q4 in 2027**. Its 2027Q4 is derived.
- **Oil gap.** Measured against the oil it likely assumed (the Aug STEO, falling to $65 by 2027Q4), all three oil paths sit above that assumption through 2027.
- **2027 Q4/Q4 range.** Mapped through the FEDS note's response table, the six scenarios run from **2.40** (P1 × pre) to **3.16** (P2 × post).
- **Which axis moves 2027 more.** The regime moves it **0.30–0.68 pp**. The oil path moves it **0.08 pp** under pre-pandemic dynamics and **0.44 pp** under post-pandemic ones.
- **Most of the 2027 adjustment is already in.** Under post-pandemic dynamics it comes mostly from oil moves that have already happened: flat Brent at the Nov 11 spot gives 2.93. Brent would need about **$60** flat to return to 2.40.

## 4. Slide-worthiness ranking
1. 3×2 grid, Q4/Q4 columns (`Scenario_grid!D8:G13`): 5/5, on the slide.
2. SPF baseline path, dated (`Baseline`): 4/5, the slide's spine.
3. Oil-path chart (`Oil_paths`): 4/5, on the slide or backup.
4. Axis comparison (`Scenario_grid!E17:G21`): 4/5, a spoken line or inset.
5. Response-function chart (`Pass_through`): 4/5, backup or spoken.
6. Scenario-range chart (`Fan_chart`): 3/5, backup. Its quarters are lumpy.
7. SEP comparison (`SEP_compare`): 3/5, a spoken line.

From D, these belong on the slide as captions:
- "SPF, Aug 11, before the spike";
- "scenarios, not probabilities";
- "post-pandemic = five-economy panel; the authors view their projections as an upper bound";
- "before any additional policy response".

## 5. Answers by question
**Q1. Baseline** (`Baseline`; raw `raw_SPF`, `raw_PCE`)
- **Q3 2026 SPF median core PCE**, q/q annualized, SA. Deadline Aug 11, release Aug 14.
  - 2026Q3 to 2027Q3: 2.70, 2.62, 2.58, 2.43, 2.33.
  - **2027Q4 is derived at 2.27** (`Baseline!D14`, yellow). It is not published; we solved it from the 2027 Q4/Q4 median of 2.40.
- **Q4/Q4 medians:** 2026 3.29, 2027 2.40, 2028 2.16.
- **Dispersion (P25 to P75):** 2026Q4 2.48–2.90, 2027Q3 2.20–2.50 (`Baseline!E:F`).
- **Actual quarters:** 2026Q1 3.94, Q2 3.31, **Q3 2.47**. The SPF expected 2.70 for Q3. Source: FRED vintage Oct 29.
- **Baseline used:** 2026Q4 is **2.62** (`Baseline!G10`). The 2026 Q4/Q4 built from actual quarters plus the SPF is **3.08**, against the SPF's own 3.29 (`Baseline!B18:C18`). The gap is the BEA revision plus the Q3 miss.
- **Jump-off vs slide 1's 3.24%** (`Baseline!B24:B28`):
  - SPF 2026Q4 needs Nov–Dec m/m of 0.053%.
  - If Nov–Dec run at the Oct pace, 2026 Q4/Q4 is 3.33.
- **Sep SEP median core PCE:** 3.4 / 2.5 / 2.2 for 2026 / 2027 / 2028 (`SEP_compare!B6:B8`). The SEP doesn't publish a longer-run core PCE projection.
- **Q4 SPF:** not out (§1).

**Q2. The baseline's oil assumption** (`Oil_paths!D21:D26`; `raw_STEO`)
- Proxy: the **Aug 2026 EIA STEO** (released Aug 11, the SPF deadline day). Brent $85.26 / 78 / 74 / 71 / 68 / **65** for 2026Q3–2027Q4.
- Weaknesses:
  - Nothing says the forecasters used it.
  - It is a model forecast, not a market price.
  - It ran about $8 below the futures that day.
  - Exchange futures data is paywalled.
- Sensitivity: Jul STEO and the Aug 11 futures. Moving between proxies shifts P1 × post 2027 by about 0.33 pp (2.83 to 3.16).

**Q3. Oil paths** (`Oil_paths`; Brent spot FOB, quarterly mean; daily data to Nov 11)
- **P1, baseline oil (Nov 2026 STEO):** 2026Q4 $108.2 (splice), then 2027 at $95 / 89 / 83 / 77.
- **P2, oil rises again:** $110 flat from Nov 12. Bowman: Brent "moved up to and above $110 per barrel in the second half of October."
- **P3, Hormuz reopens:** the pre-war trend (Feb 2026 STEO, the last before the **Feb 28** onset per the Mar STEO, p.5) plus $25. That gives **$78 flat in 2027**. Waller: "$20 to $30 a barrel."
- **Gaps in 2027Q4** (`Oil_paths!H26:J26`, log points): P1 +16.9, P2 +52.6, P3 +18.2.
- The 2026Q3 gap is already +12.2, driven by September.

**Q4. Pass-through mapping** (`Pass_through`; raw `raw_response`)
- **Source:** the note's **own Figure 2 data table** from its accessible version, quarter by quarter, k=0–12 (provenance = table, not interpolated).
- **After 12 quarters, per 10% oil rise:** 0.044% pre-pandemic vs 0.360% post-pandemic (`Pass_through!B18`, `D18`). The text rounds these to "0.05" and "0.35".
- **Math:**
  - Level effect: L_t = Σ_s R_{t−s}·Δgap_s/10.
  - Scenario q/q = baseline + (100+baseline)·(e^{4(L_t−L_{t−1})/100} − 1).
  - Actual quarters are not adjusted.
- **Flag:** the pre-pandemic line cannot be rebuilt from Table 2's pass-through sum (0.001); the post line can. We use the published table.
- The headline mapping (optional) was not done.

**Q5. Script** (`03_Data/pipelines/forecast_3b/`)
- `forecast.py --spf <vintage>` produces the grid, fan, metadata (sha256) and the `REGIME_WEIGHT_POST = None` hook.
- The zero-gap test passes: the baseline comes back exactly in 30/30 rows. The +10% step reproduces the response, and linearity holds.
- The Q4 rerun is 4 commands, in the README. It was dry-run on synthetic data only.

**Q6. Scenario results** (`Scenario_grid!D7:H14`)

| | 2026Q4 q/q ann. | 2027Q4 q/q ann. | 2026 Q4/Q4 | 2027 Q4/Q4 |
|---|---|---|---|---|
| Baseline | 2.62 | 2.27 | 3.08 | 2.40 |
| P1 × pre / post | 2.81 / 2.73 | 2.35 / 3.14 | 3.13 / 3.11 | 2.40 / 2.93 |
| P2 × pre / post | 2.85 / 2.77 | 2.42 / 3.60 | 3.14 / 3.12 | 2.48 / 3.16 |
| P3 × pre / post | 2.72 / 2.65 | 2.42 / 2.78 | 3.11 / 3.09 | 2.42 / 2.72 |
| Spread | 0.20 | 1.25 | 0.05 | 0.76 |

- **Axis comparison for 2027 Q4/Q4** (`Scenario_grid!E17:G21`):
  - Across oil paths: 0.08 with the pre regime held, 0.44 with post held.
  - Across regimes: P1 0.53, P2 0.68, P3 0.30.
- **No weighting.** The hook is `Scenario_grid!D23`, left blank.

**Q7. Stress test** (`outputs/D_qa_prep.md`, `D_issues.csv`)
- Ten attacks are covered, with ≤60-word answers and "do NOT say" lists.
- The top exposures:
  1. the stale 2026 starting point;
  2. the Q4 rerun changing what the grid means;
  3. no stated landing;
  4. partial equilibrium. Fig. 2 holds all exogenous variables fixed, so the scenarios are "before any additional policy response";
  5. proxy and regime scope.

## 6. Flags
- **Already locked in.** Under post-pandemic dynamics, the 2026H2 oil steps that have already happened account for 92–134% of the 2027 adjustment. Brent at today's spot gives the same answer as P1.
- **P1 and P3 converge by 2027Q4** ($77 vs $78), although their earlier 2027 paths and inflation effects differ (post 2027 Q4/Q4 2.93 vs 2.72).
- **Post-regime cells sit above the outside ranges.** Post P1 and P2 (2.93, 3.16) are above the SPF 2027 P75 (2.73) and the SEP central-tendency top (2.6).
- **Lumpy quarters.** The note's post response dips at k=1 and jumps at k=4, so 2027Q4 spikes to 3.60 (P2 × post). Lead with Q4/Q4.
- **Bowman's $110 sits below the October average** ($123.93). Brent was ≥$110 on every trading day from Sep 10 to Oct 31. P2 is a return to $110, not a new peak.
- **BEA revision.** The vintage break (Sep 30) cut 2026Q1 from 4.42 to 3.94. The SPF and the SEP were formed on the old vintage.
- **Unverified:**
  - whether the Fig. 2 shock is 10% or 10 log points (×1.049 if simple);
  - the Yahoo futures values (secondary);
  - the Q4 SPF date.

## 7. Judgment calls for Eli (ordered by how much each blocks the slide)
1. **Regime weighting, which waits on slide 3A.**
   - A: weight toward post-pandemic if 3A finds second-round channels live.
   - B: keep both regimes unweighted as bookends.
   - Default: no weighting (hook blank).
   - This is also where the "so what's your forecast?" landing comes from (D3).
2. **Which SPF vintage leads after Nov 16.**
   - A: Q4 leads and Q3 goes to backup. The story becomes "the regime matters if oil departs from November expectations."
   - B: Q3 leads, because its pre-spike date makes the oil adjustment meaningful, with Q4 shown alongside.
   - GO says show both.
3. **Baseline staleness in 2026.**
   - A: keep the pure SPF and disclose the 0.053% m/m gap (default).
   - B: re-anchor 2026Q4 on the October estimate. This is outside the locked method and risks double-counting October's pass-through.
4. **Hormuz premium.**
   - A: +$25 central (locked).
   - B: +$0 central, or shown alongside, since Waller's figure is today's passage cost.
5. **Oil-assumption proxy.**
   - A: Aug STEO (default).
   - B: Aug 11 futures, which are market prices but a secondary source (−0.10 pp on P1 × post).
6. **Lead metric.**
   - A: Q4/Q4 (default).
   - B: quarterly annualized, which shows timing but is lumpy.
7. **Wording of "upper bound."** The note attaches it to its projection paths (Fig. 3), not to the Fig. 2 response.
   - A: "the authors view their projections as an upper bound."
   - B: drop the phrase on the slide and keep it spoken.
8. **Verbal-cue candidates** (D) were added to the tracker, PENDING Eli.

## 8. Questions you'll probably have
- **How do I rerun on the Q4 SPF?** From the project root, run:
  - `python3 -I 03_Data/pipelines/forecast_3b/code/fetch_inputs.py`
  - `python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q4`
  - `python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q3 --compare`
  - `python3 -I 03_Data/pipelines/forecast_3b/tests/test_zero_gap.py --spf 2026Q4`
  - then `python3 -I "02_Research/Subtasks/12_slide3b_research/code/build_slide3b_workbook.py" --spf=2026Q4 --verify`.
  - The builder handles the Q4 layout (gap starts 2026Q4, 2026Q4 adjusted); regression test `code/test_builder_q4_synthetic.py` passes on a synthetic Q4 file. The jump-off rows are live formulas off the baseline, so they refresh automatically. After the real Q4 rerun, refresh only the Slide_worthiness/Judgment_calls text (README "Vintage note"); `code/A_04_jumpoff.py` is a Q3-only subtask script.
- **Why these three oil paths?**
  - P1 is the market-and-agency view today.
  - P2 is "oil rises again", anchored on Bowman's late-October level.
  - P3 is the de-escalation case, anchored on Waller's passage cost.
  - Each has a dated, quoted source. The alternatives are in `C_q6_sensitivity.csv`.
- **How does this connect to slide 1's 3.24?**
  - 3.24% is October y/y. The grid starts from the SPF's 2026Q4, which is consistent with October only if Nov–Dec core runs at about 0.05% m/m.
  - That's why 2026 numbers stay backup and 2027 is the headline.
- **Why does the regime matter more than oil?** Under pre-pandemic dynamics even a 50-log-point oil gap moves core by under 0.1 pp. Under post-pandemic dynamics the same gaps move it 0.3–0.8 pp. 3A's evidence decides which regime to emphasize.
- **Isn't this just the SPF?** For 2027, the adjustment is 0 to +0.76 pp on top of the SPF. Every cell traces to sources in the workbook.
- **Do the scenarios assume the Fed does nothing?** Yes. Fig. 2 holds exogenous variables fixed and the equation has no policy rate. The cells are "before any additional policy response." That is the bridge to the policy section, and the GEMUS model in the same note shows policy must tighten "materially" under high pass-through.
- **Where do I look first?** `READING_GUIDE` → `Scenario_grid!D7:G14` → `Oil_paths` chart → `Pass_through` chart.

## 9. Paywalled or unavailable (logged; not used)
- ICE Brent futures (licensed): https://www.ice.com/products/219/Brent-Crude-Futures/data
- CME Brent settlements (HTTP 403): https://www.cmegroup.com/markets/energy/crude-oil/brent-crude-oil.settlements.html
- Bloomberg Brent curve (terminal), which the FEDS note's Fig. 3 used.
- EIA NYMEX futures RCLC1–4, discontinued after 2024-04-05: https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm
- SPF Q4 2026 page (404 at Nov 15 build; released Nov 16 and used): https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026

## 10. Nov 18 re-pull checklist
- [x] **Q4 SPF** (released Nov 16): §8 commands run; deadline Nov 11, Dispersion_1 Q4 row and matched STEO (Nov) checked; workbook rebuilt with `--spf=2026Q4`; D's #7–8 updated (§1b).
- [ ] **Brent to the cutoff:** EIA's next daily release is **Nov 18**. Rerun `fetch_inputs.py`, `forecast.py --spf 2026Q4` and the builder with `--spf=2026Q4 --verify`; this changes the 2026Q4 splice.
- [ ] **Nov STEO** (Nov 10) is current. The Dec STEO is after the cutoff.
- [ ] **Oct PCE** comes Nov 25, after the cutoff. The 3.24% estimate stays labelled "est."
- [ ] **Rerun the zero-gap test** after any change.
