# Slide 3A research: final report (Q1–Q9)

**Status: Audited — converged R3** (Codex, Nov 15). R1 found 4 Blocking items: BB's 1.2 V/U presented as a threshold rather than an assumed benchmark; the labor-share identity presented as profit-margin expansion; the NFIB "plans" chart plotting a realized series; and a wrong job-switcher premium peak (2.4 → 2.7 pp). Plus 3 Non-blocking (PPI "by construction"; Michigan baseline-bias direction; MCT horizon label). All fixed; R2 caught one unpropagated "margins" sentence, closed in R3. No factual, source or arithmetic item is open. One judgment call (N14) is logged for Eli.

**Workbook:** [`01_Finals/data/Slide3A_Inflation_Data.xlsx`](../../../01_Finals/data/Slide3A_Inflation_Data.xlsx). Tabs: `READING_GUIDE` (start here), `README`, 6 research tabs, `Slide_worthiness`, `Sources`, `Judgment_calls_and_paywalled`, 4 grey `raw_` tabs. 5,714 live formula cells; LibreOffice recalculation gives 0 mismatches and 0 errors; 38 checks against the agents' CSVs pass. All 13 charts were rendered and inspected; the chart XML has `smooth val="0"` / `invertIfNegative val="0"`.
**Rebuild:** `python3 -I "02_Research/Subtasks/11_slide3a_research/code/build_slide3a_workbook.py" --verify`. Fix the inputs in `outputs/`, not the xlsx.
**Reports:** `report_A.md` … `report_D.md` (each with a coordinator review). Audit trail: `06_Audits/slide3a_research/`.

---

## 1. Disagreements with the premise (read first)
1. **The roadmap's Bernanke–Blanchard citations don't exist in the paper.** R1 asks us to verify "Reis (2021) and the state-dependent-pricing cite" in BB. The paper cites neither (0 hits in text and references; checked by Agent A and by me). Reis (2021), "Losing the Inflation Anchor", BPEA, does exist. Where the cite came from is unknown (N6).
2. **Read literally, the lead exhibit's own framework points away from a labor-driven second round.** BB find no catch-up effect in wages (Table 2: −0.024, p=0.765), and their key channel, V/U, is 1.06 now against the 1.2 steady-state value they assumed (its 2019Q4 level; not tightly estimated, p.36) and 2.04 at the 2022 peak. Their wage equation is continuous: 1.2 is a benchmark, not an on/off line. Unit labor costs over 8 quarters are 1.92%, the same as 2018–19 (1.90). What has moved is short-run expectations (SCE 1y 3.0 → 3.9 since Feb) and firms' price plans (NFIB net 37%, highest since Jul 2022). The conservative version run here keeps the BB table as scoped, with every channel shown, including the ones that cut against a second round. Whether it still leads is Eli's call (N1).
3. **A rival reading the roadmap doesn't list: the nonlabor share, not wages.** The roadmap reads wages and catch-up "through ULC and the labor share". The labor share is at a record low (53.0%, 2026Q3) and falling, which by identity means output prices (+4.05% y/y, nonfarm business) are rising faster than unit labor costs (+2.39%), so the nonlabor share rose. Nonlabor payments include profits but also depreciation, taxes, net interest and rents; wider profit margins or oil rents are possible explanations that need separate evidence (not decomposed; Codex R1-F02) (N4).
4. **"Nearly six years above target" rounds up.** It is 67 months (5.6 years) through Sep 2026, 68 with the Oct estimate. Six years arrives in Mar 2027 (N3).
5. **Household long-run expectations: the 2021–23 comparison breaks.** Michigan moved from phone to web interviewing in 2024; on UMich's own web series, Jun 2025 (4.0) "matches the peak reading from mid-2022". Michigan 5–10y now (3.4) is therefore not "above its 2021–23 peak". Use SCE 3y and 5y5y for then-vs-now (N2).

## 2. Bottom line (data only)
Labor-cost measures look like 2018–19, not 2021–23: V/U 1.06 (peak 2.04), ULC 1.9% over two years (2018–19: 1.9%), ECI wages 3.1% y/y (2018–19: 3.0%; 2021–23 peak 5.6%). Long-run market and professional expectations are near pre-shock levels (5y5y 2.30 Oct avg; SPF 10y PCE 2.2), while household expectations are elevated at both horizons (Michigan 1y 4.3, SCE 1y 3.9, SCE 3y 3.3) and short-run household expectations are up about 0.9 pp since February. Underlying inflation measures range from 2.26 (Dallas trimmed mean) to 3.60 (supercore), all above 2%; Logan's core services ex housing and transport is 3.21% (2018–19: 2.27%). Firms' stated plans are elevated (NFIB net 37% plan price increases, net 24% plan compensation increases), and nonfarm business output prices are rising faster than unit labor costs (4.05% vs 2.39%). Headline and core PCE have been above 2.0% for 67 consecutive months.

## 3. Slide-worthiness ranking (data and ratings only; Eli decides)
Workbook tab `Slide_worthiness`. Ratings 1–5. D = how well it survives hostile Q&A.

| Exhibit | Agent | D | Coordinator | Basis |
|---|---|---|---|---|
| Underlying-trend panel | 4 (C) | 4 | **4** | Full range 2.26–3.60, all above 2; every roadmap number reproduces. Oct momentum rests on the estimate. |
| V/U then vs now | 4 (A) | 4 | **4** | Like-for-like: 2.04 → 1.06 vs 1.2. Cuts toward "no labor second round". |
| ULC 4q/8q | 3 (B) | 4 | **4** | 8q 1.92 vs 2018–19 1.90; nets out productivity. |
| Expectations short vs long | 4 (C) | 3 | **4** | Split by respondent type is robust; Michigan long-run comparison must stay within the web era. |
| Time above target | 3 (C) | 4 | **4** | 67 months, exact. |
| BB channel table | 4 (A) | 3 | **3** | Leads only with V/U, ULC and short-run expectations side by side. |
| Labor share | 3 (B) | 3 | **3** | 53.0 now (not 52.8); opens a nonlabor-share reading (profits not established). |
| Trimmed-mean bias | 3 (A) | 3 | **3** | Verified quote and Dallas data; Dallas calls the evidence "not clear-cut". Q&A backup. |
| Wages vs benchmark | 4 (B) | 2 | **2** | Sign flips with the wage measure and trend. |
| Catch-up surveys | 3 (B) | 2 | **2** | Plans only; NFIB price plans are the loudest reading. |
| Gas co-movement | 3 (C) | 2 | **2** | Descriptive, small n, mode break. |
| Policy timeline | 2 (C) | 2 | **2** | Context only. |

## 4. Per question (data only; tab and cell)

**Q1. Bernanke–Blanchard channels, 2021–23 vs now** (`BB_channels!A5:I14`; V/U chart at `S5`; report_A)
- Model: wage equation with V/U and a catch-up term; price equation (wages read as ULC, plus energy, food, shortages); short- and long-run expectations equations (Eqs 1–6, pp.6–9).
- Estimates: V/U lag sum 0.693 (p=0.030); catch-up −0.024 (p=0.765) (Table 2, p.17). Energy 0.066 in the price equation, "some second-round price-price effects" (Table 3, pp.24–25). Short-run expectations respond 0.124 per point of inflation (Table 4); long-run 0.025 (Table 5).
- 2021–23: energy drove "much of the rise" in late 2021–H1 2022; shortages dominated 2021Q2; V/U became "an increasingly important, though by no means dominant, source of inflation" (Fig 12, p.34). Conclusion: "labor-market balance should ultimately be the primary concern" (p.40). Expectations "feed fairly quickly into wages, although … react slowly to actual" inflation (p.18; quote both halves).
- Then / 2018–19 / now: V/U 2.04 (Mar 2022) / 1.16 / **1.06** (Sep 2026) (`BB_channels!L9:Q9`); Michigan 1y 5.4 / 2.71 / 4.3 (Nov prelim); SCE 1y 6.78 / 2.76 / 3.91; Michigan 5–10y 3.2 / 2.47 / 3.4 (mode break, not comparable); 5y5y 2.46 / 2.03 / 2.30; ECI W&S y/y 5.62 / 3.00 / 3.12; ULC y/y 6.13 / 1.77 / 2.39; ULC 8q 5.63 / 1.90 / 1.92; NFIB planned comp 32 / 21.5 / 24.
- Energy/food relative prices and shortages: "now" not computed on BB's construction (N11).

**Q2. Trimmed-mean bias** (report_A; `outputs/A_q2_trimmed_bias.md`)
- Logan, exact: "My staff's research finds, however, that a change in the mix of price increases and decreases is causing the trimmed mean to drop too many increases right now. This effect likely makes the trimmed mean lower than the true inflation trend." It links Dallas Fed posts of Apr 16 and Aug 13, 2026.
- Apr 16: positive skew makes the 24/31 trim "downwardly biased". Aug 13: alternative 19/20 trim 2.571 vs 2.223 (12m to Jun 2026); evidence "doesn't offer a clear-cut conclusion".
- Dallas skewness (12m avg): +0.09 Jun 2026 vs −0.14 1977–2019 mean (positive in 13% of months then).
- Slide 2 Q4b (cited): kept months of >3% items average 2.65% vs 4.80% for all months; monthly trim 2.27 vs 2.98 trimming 12m rates once. Consistent in direction.

**Q3. Wages and costs** (`Wages_ULC`: summary `A77:F91`; benchmark `A60:E72`; charts `AE5`, `AE29`, `AE53`; report_B)
- 2026Q3: ECI W&S y/y **3.12** (8q 3.35); ECI total comp 3.34; ULC y/y **2.39**, 8q **1.92**, q/q ann. −0.66; hourly comp 4.49; output per hour y/y 2.06, 8q 2.36. AHE Oct y/y 3.12, 3m ann. 3.88 (prelim). WGT Sep 3.9.
- Benchmark 2% + trend: central trend 1.52 (OPH 2007Q4–2019Q4) → **3.52%**; 2020–25 trend 2.21 → 4.21%.
- Labor share (PRS85006174): **53.0** (2026Q3, record low on the index), 53.3 (Q2). Barr's 52.8 = the pre-revision Sep 3 vintage of Q2 (reconstructed). He calls it a share of "national income"; it matches the nonfarm business series.
- ULC was revised up with the Nov 5 release (2026Q2 y/y 1.4 → 2.6).

**Q4. Expectations** (`Expectations`: summary `A117:F125`; SPF `A129`; gas correlations `A144`; Logan aggregate `A153`; charts `L5`, `L29`, `L55`, `L82`; report_C)
- Households: Michigan 1y 4.3, 5–10y 3.4 (Nov prelim); SCE 1y 3.91, 3y 3.29 (Oct; Nov 9).
- Professionals: SPF Q3 2026 headline PCE current year 3.61, next year 2.30, 10y 2.20. Q4 SPF not out at build (due Nov 16).
- Markets: 5y BE 2.40, 10y 2.35, 5y5y 2.30 (Oct averages); latest daily Nov 13: 2.30 / 2.24 / 2.18.
- Gas: Oct avg $4.31 vs $3.06 a year earlier (+41%); $4.00 Nov 9. Correlation of 12m changes with gas: Michigan 1y 0.89 (2021–23) but −0.37 (2024–26); SCE 1y 0.91 / 0.40; 5y5y 0.55 / 0.36.
- Logan's "13 surveys ≈ 3.1" is not reproducible; our pipeline aggregate is 3.38 (N8).

**Q5. Catch-up evidence (surveys)** (`Catch_up`: summary `A116:F124`; other surveys `A128`; charts `K5`, `K29`; report_B)
- NFIB Oct 2026 (net %, SA): plan to raise compensation **24** (highest since Dec 2025; 2018–19 21.5; peak 32); plan to raise prices **37** (highest since Jul 2022; 2018–19 23.1; peak 54); raised prices 33; raised comp 29.
- Atlanta Fed BIE: unit costs vs a year ago 2.52; year ahead 2.30 (2018–19 ~2.0).
- Richmond Fed wage diffusion (Oct): mfg 20, services 16, both below 2018–19 (26.6, 30.4).
- Richmond CFO survey Q3: expected 2026 wage growth 4.3% mean (3.8% median); price 5.3%.
- Beige Book Oct 14: "inflation has spawned additional wage pressure in the form of higher cost-of-living demands"; "Higher oil prices permeated all District reports."
- Eli's podcast figures: "24%" matches NFIB planned compensation (Oct); "34%" does not match Oct planned prices (37).

**Q6. Underlying trend** (`Underlying_trend`: summary `A116:F130`; roadmap check `A134`; charts `O5`, `O29`; report_C)
- Sep 2026: Dallas trimmed mean 2.26; Cleveland median PCE 2.67; NY Fed MCT 2.84; core PCE 3.12; market-based core 3.12; **Logan measure 3.21**; supercore 3.60. All 2018–19 averages 1.6–2.3.
- Oct est.: Logan measure 12m 3.24, 3m ann. 3.46 (Sep 2.61); supercore 12m 3.60, 3m 4.11.
- Roadmap check: 2.8 (MCT 2.84), 2.3 (2.26) and 3.2 (3.207) all reproduce. Logan's "eight tenths above target-consistent pace" implies 2.4%, unsourced.

**Q7. Pace 2025 wording** (report_A; `outputs/A_q7_pace_quotes.md`)
- Phillips curve: Sharma (transcript p.5), "actual inflation depends partly on expected inflation, which guide wage and price setting"; Tuosto (p.8), tariffs "led to an upward shift in the Phillips curve".
- Productivity: Bynum (p.6), "high wage growth has not yet manifested into higher price inflation due to the growth in productivity"; Raspanti (p.6), "unreliably volatile productivity growth"; Q&A p.18, AI productivity and r-star.
- None of Pace's six judge questions was on the Phillips curve, wages or productivity.

**Q8. Time above target and policy timeline** (`Time_above_target`: summary `K6:M13`; policy table below; chart `R5`; report_C)
- Headline and core PCE: last month ≤ 2.0% was Feb 2021; **67** consecutive months above through Sep 2026 (5.58 years); 68 with Oct est. Lowest inside the run: headline 2.255 (Mar 2025), core 2.134 (Mar 2021). CPI: headline 67, core 66 months.
- Policy: 20 target-range changes Mar 2020–Sep 2026; Sep 16, 2026 +25 bp to 3.75–4.00 (12–0); Oct 28 hold (10–2). QT ended Dec 1, 2025.

**Q9. Stress test** (`outputs/D_qa_prep.md`, 17 attacks; `D_bridge_line_check.md`; `D_verbal_cues.md`; report_D)
- Highest-damage attacks: BB read literally (#8); the Logan measure's rise sits in the Oct estimate (#13); the wage-benchmark sign depends on measure and trend (#12); the Michigan mode break (#15).
- **Bridge line** (support only; wording is Eli's): "doesn't show second-round effects" supported (upstream PPI can't distinguish first- from second-round mechanisms on its own; absence comes from 3A's labor data); "lengthens the first round" supported but weakened (data fit "bigger" as well as "longer"); "raises their risk" supported conceptually, empirically weak.

## 5. Flags
**Couldn't verify:**
- CBO 1.5%: located by Codex in CBO's 2026–36 Outlook as *potential labor force productivity* (potential GDP / potential labor force), not nonfarm business output per hour. Use only as an illustration.
- Barr's exact source for 52.8 (inferred to be the pre-revision BLS vintage).
- Size of Michigan's web-mode effect.
- Richmond CFO values (hand-transcribed by Agent B from the saved HTML).
- NFIB 2018–20 values via an archived report (seasonal factors may differ at the join).
- The Jan 2026 V/U level shift (population controls?).
- Where the Reis / state-dependent-pricing cite came from.

**Worth a look:**
1. The NY Fed MCT fell from 3.45 (Apr 2026) to 2.55 (Jul) and rebounded to 2.84 (Sep), with Aug revised up.
2. Hourly compensation (4.5%) runs far above ECI wages (3.1%). Job-switcher wage premium 1.3 pp (WGT 4.7 vs 3.4) vs a 2.7 pp peak (Nov 2022).
3. Labor share at a record low while ULC is 2.4%: implied output prices +4.05%, above core PCE (3.12). Nonlabor payments (profits, depreciation, taxes, interest, rents) and the oil share are not decomposed.
4. The Logan measure's 3m rate was higher in Jan–Feb 2026 (4.25, 4.07) than in Oct est. (3.46); possibly residual seasonality.
5. NFIB planned price increases at a 4-year high while hard wage measures show no pickup.
6. Slide 2's "upstream pressure at a record" refers to the PPI stage 1 index level; on y/y rates it ranks 16th of 106 months.
7. Dallas's alternative trim (+0.35 pp) is about half the MCT–trimmed gap; they are different adjustments.
8. Core PCE Mar 2021 was 1.83 as first published (2.13 now): on the original vintage the run starts Apr 2021.

**Codex (R1):**
- CBO's 1.5% is confirmed in its 2026–36 Outlook, but as potential labor force productivity, not nonfarm business output per hour; keep that distinction if the 3.5% illustration is used.
- Michigan's experimental web-basis 2018–19 average (2.47) equals the phone-era average, so the elevation of household long-run expectations vs 2018–19 holds; only the 2021–23 peak comparison breaks.
- Not verified by anyone: the Jan 2026 V/U population-control effect, a numerical Michigan mode effect, and any decomposition of nonlabor payments into profits/oil rents.

## 6. Judgment calls for Eli (ordered by how much each blocks the slide; both positions)
Full text: workbook tab `Judgment_calls_and_paywalled`; `outputs/Z_judgment_calls.csv`.

| # | Item | Claude | Other position |
|---|---|---|---|
| N1 | Does the BB table lead, given its labor leg argues against a second round? | Lead only with V/U, ULC 8q and short-run expectations together; quote BB p.18 in full. | D: 3/5 as lead. A: 4/5. |
| N2 | Michigan long-run vs 2021–23 crosses the 2024 phone-to-web break. | Don't say "above its 2021–23 peak"; use SCE 3y and 5y5y. | D: same. C originally said "above". |
| N3 | "Nearly six years above target" = 67 months. | Say "67 months" or "five and a half years". | C, D: same. |
| N4 | Barr's 52.8 is superseded (53.0 now); the nonlabor share rose (prices +4.05% vs ULC +2.39%). | Cite 53.0. Say "nonlabor share", not "margins", unless profits are decomposed. Where the point goes (3A, 3B or decision) is yours. | D: margins reading largely right. Codex: identity shows nonlabor share, not profit margins. |
| N5 | Wage benchmark trend (3.52 vs 4.21) and wage measure. | Lead with ULC; benchmark as backup with both lines. | B: central 3.52, show both. D: 2/5. |
| N6 | Roadmap's Reis / state-dependent-pricing cite isn't in BB. | Drop it or tell us its source. | A: same. |
| N7 | Logan quote wording ("right now"; "likely" in sentence 2; implied 2.4% unsourced). | Use the exact two sentences. | A, C: same. |
| N8 | Logan's 13-survey 3.1 doesn't reproduce (ours 3.38). | Quote hers as hers. | C, D: same. |
| N9 | Bridge line support (clause by clause). | Supported with caveats; wording yours. | D: same. |
| N10 | "Recent momentum has picked up" on the Logan measure rests on Oct est. | Label est.; lead with the level. | D: high-damage attack. |
| N11 | BB energy/food/shortage channels have no "now" value. | Leave to slide 2 unless you want them. | A flagged. |
| N12 | Optional new computation: trimmed-mean month test for 2018–19. | Not done; low priority. | A suggested. |
| N14 | D's numeric revision triggers (e.g. 5y5y > 2.46 "de-anchoring") are proposed watch points, not estimated tests. | Keep as optional watch points; not in spoken answers. | Codex: keep or omit. |

**Codex judgment call (R1):** N14 above (revision thresholds are watch points, not tests). No other judgment calls; nothing Codex raised is open.

## 7. Questions you'll probably have
- **How does this relate to slide 2's finding?** Slide 2 found breadth was already high before the oil shock and the exposed items got hotter ("a bigger, longer first round"). 3A asks whether that is spilling into wages and expectations. On the labor side, not yet (V/U, ULC, ECI look like 2018–19). On expectations, short-run household measures are up and long-run market measures are not. Firms' price plans are elevated, and the nonlabor share has risen (profits or oil rents would need separate evidence). The bridge line is supported with caveats (N9).
- **Which numbers are estimates?** Anything labelled "est." for October 2026 PCE (core PCE 12m, supercore, the Logan measure) comes from our audited October build; BEA publishes on Nov 25, after the finals. Michigan Nov is preliminary (final Nov 20). AHE Oct is preliminary.
- **Why does the labor share differ from Barr's?** BLS revised it on Nov 5; he spoke Nov 12 using the earlier vintage. Same series, newer vintage.
- **Why is "2021–23 peak" sometimes different from what papers quote?** We use today's data vintage throughout (e.g. BB's "about 1.9" V/U peak is 2.04 monthly now).
- **What's the Logan measure?** PCE core services excluding housing and transportation services, built from BEA lines 376 − 153 − 190. Our Sep value (3.207) reproduces her 3.2, and two methods (Fisher, Törnqvist) agree.
- **Is the trimmed mean wrong?** Not wrong; designed to drop extremes. Dallas staff find that when large increases dominate (positive skew), it drops too many increases. Their alternative trim is 0.35 pp higher. The evidence is "not clear-cut" in their words.
- **Is the policy timeline relevant here?** Context only; the slide defers policy.

## 8. Paywalled links
Workbook tab `Judgment_calls_and_paywalled`; files `outputs/A_paywalled.csv` … `D_paywalled.csv`. None affects a reported number. Main ones: CBO productivity slides (403; the 1.5% is unverified); NFIB historical data (subscription); Conference Board salary survey and CEO confidence (members only); two papers linked from the Dallas Aug blog (ScienceDirect, SSRN; 403).

## 9. Re-pull checklist for Nov 18
- [ ] **Q4 SPF (Nov 16):** rerun `code/C_q4_spf_check.py`; if out, add to `C_q4_summary.csv` and rebuild.
- [ ] **Breakevens and gas:** extend FRED T5YIE/T10YIE/T5YIFR and GASREGW to Nov 17 (rerun `code/C_00_fetch.py` into a new dated folder, update paths, rerun `C_q4_expectations.py`).
- [ ] **Fed speeches Nov 16–18** (Warsh, Hammack, Kashkari, Musalem): anything on second-round effects, wages or expectations goes in `External_views`.
- [ ] **Oct 27–28 FOMC minutes** (expected Nov 16–20): check for second-round language.
- [ ] **NY Fed MCT:** next update after Oct PCE (Nov 25+), after the cutoff.
- [ ] **No change expected before Nov 18:** JOLTS (Oct due early Dec), ECI (Jan 30), productivity (Dec revision), NFIB Nov (Dec), Michigan final (Nov 20), Oct PCE (Nov 25).
- [ ] After any input change: rebuild with `--verify` (must show 0 mismatches, 0 errors).
