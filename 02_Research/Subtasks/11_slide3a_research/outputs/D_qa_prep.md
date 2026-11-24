# Slide 3A hostile-judge Q&A prep (Agent D, Nov 15, 2026)

Status: Round 1, NOT AUDITED. Evidence only; no policy recommendation. Every spoken answer is a **draft, PENDING Eli**.

**Conventions.** Oct 2026 PCE-based values are the audited UMD estimate ("est."); official Oct PCE is out Nov 25, after the finals. Michigan Nov 2026 is PRELIMINARY (final Nov 20). Q4 SPF due Nov 16 (not out at writing). "Recent momentum has picked up", never "accelerating". No claim of changed price-setting behaviour from the oil note.

**Tags.** [O] opened or computed by me in this run. [A]/[B]/[C] taken from that agent's coordinator-verified report or output (series ID, period, SA and vintage are in the cited file row). File paths are in `11_slide3a_research/outputs/` unless given. "row N" = line N of the CSV, header = line 1.

**New D computation.** `code/D_q9_checks.py` → `outputs/D_q9_checks.csv` (88 rows). It reads only existing A/B/C outputs; no new downloads were needed for numbers. One new raw file: `03_Data/Raw/S3A_D_michigan_mode_2026-11-15/umich_px5web202506.pdf` (UMich, Hsu, Jun 27, 2025; SHA-256 b773dedb…b698) for the survey-mode point.

---

## Read this first: four findings that change what we can say

1. **Michigan 5–10y "above its 2021–23 peak" is a survey-mode artifact (attack 9b, 15).** Michigan moved from phone to web interviewing in 2024. UMich's own web-only parallel series says June 2025's median (4.0) "matches the peak reading from mid-2022" [O, raw PDF above]. So on a like-for-like web basis, the 2022 peak was about 4.0, not the 3.2 in the spliced series (`C_q4_summary.csv` row 3). The current 3.4 is **below** the web-basis 2022 peak. The 2018–19 phone-era average (2.47) is the same as UMich's experimental web-basis 2018–19 average (2.47; Oct 2024 parallel-web report, appendix p.4, per Codex R1-F06), so the elevation vs 2018–19 holds. Drop "above its 2021–23 peak".
2. **The Logan measure's Oct est. 3m rate is high relative to Jul–Sep, not to the past year (attack 13).** 3.46 (Oct est.) vs 2.61 (Sep), but four of the previous 12 months were at or above 3.46 (max 4.25, Jan 2026); the 12-month mean of the 3m rate is 3.18 (`D_q9_checks.csv` rows 2–6). A 0.86 pp one-month jump has happened 5 times since Jan 2024 (row 10). "Recent momentum has picked up" survives only as "since the summer".
3. **Bernanke–Blanchard's own second-round channel is short-run expectations, not catch-up (attack 8).** BB: "short-run inflation expectations feed fairly quickly into wages", though they "react slowly to actual price inflation" (printed p.18) [O, `outputs/text/bb2023.txt`]; catch-up ≈ 0 (Table 2) [A]. So read literally, BB say the risk route now is short-run expectations (SCE 1y +0.91 pp since Feb 2026) plus V/U, not catch-up. And BB p.9: "the longer the episode … the stronger the effect on steady-state inflation" [O]. This is the strongest literature support for the bridge line's "lengthens … raises their risk".
4. **The labor-share fall is arithmetically a price-over-cost gap (attack 11).** Labor share = ULC / output price. ULC +2.39% y/y and labor share −1.60% imply the nonfarm business output price +4.05% y/y (2025Q3→2026Q3; `D_q9_checks.csv` rows 46–48). Prices, not wages, are leading. But nonfarm business includes oil and gas extraction, so part of this is the oil windfall itself (first round), not broad "greedflation" (not decomposed; flagged).

---

## Damage ranking

| Rank | # | Attack | Damage | Why |
|---|---|---|---|---|
| 1 | 8 | BB read literally: no catch-up, V/U 1.06 < 1.2 | **High** | Uses our own lead exhibit against us. Answerable via BB's expectations channel, but only if Eli knows p.18. |
| 2 | 13 | Logan measure's rise is all in the Oct est. | **High** | True on 3m; 12m flat; Oct 3m is not unusual vs the past year. |
| 3 | 12 | Wage-benchmark sign depends on measure and trend | **High** | Sign flips across 8 measures × 3 trends (`D_q9_checks.csv` rows 52–83). |
| 4 | 15 (new) | Michigan long-run comparison is a mode break | **High** | A judge who knows the 2024 web switch catches a factual error. |
| 5 | 2 | Cherry-picking MCT 2.8 over trimmed 2.3 | **Medium-high** | Defensible with Dallas's own alt-trim 2.57, but the two corrections differ in size. |
| 6 | 9 | Logan's 3.1 doesn't reproduce; "near 2%" fails for households | **Medium** | We don't rely on her 3.1; long-run split by respondent type is our point. |
| 7 | 11 | Labor share vintage; margins not wages | **Medium** | Vintage fix is easy; the nonlabor share has risen, but profits are not established (nonlabor payments not decomposed; Codex R1-F02). |
| 8 | 1 | Expectations anchored, so why not hold? | **Medium** | Evidence answer is clean (long-run market anchored, short-run up). Policy part belongs elsewhere. |
| 9 | 4 | Short-run expectations just track gas | **Medium** | 2021–23 correlation 0.89–0.91 supports the judge; 2025 tariff spike and 2024–26 Michigan −0.37 cut against. |
| 10 | 3 | Oil note is a panel and an upper bound | **Medium** | All true; we must volunteer it. |
| 11 | 14 | NFIB price plans are a first-round echo | **Medium** | Plans can't distinguish cost pass-through from second round. Concede. |
| 12 | 16 (new) | ULC is benign; that is the real answer | **Medium** | ULC 8q 1.92 ≈ 2018–19 1.90; strongest "no second round" fact. |
| 13 | 6 | Wage growth is just productivity | **Low-medium** | ULC answers it; BB find trend productivity insignificant in wages. |
| 14 | 7 | ULC is noisy | **Low-medium** | q/q SD 3.0 pp even in 2018–19; we use 4q/8q. |
| 15 | 5 | Catch-up evidence is anecdotal | **Low-medium** | Mostly true; we say so. Real wages −0.53 pp gives the motive. |
| 16 | 10 | "Nearly six years" is 5.6–5.7 | **Low** | Logan's own phrase; say "5.6 years, 67 months". |
| 17 | 17 (new) | V/U is rising, so the labor channel is turning on | **Low-medium** | Flip-side of 8: V/U +0.19 since Dec 2025. |

---

## 1. "Expectations are anchored, so why not hold?"

**(a) Judge.** "Your long-run expectations are at 2.2. Breakevens fell in November. If the anchor holds, isn't the textbook answer to look through an oil shock?"

**(b) Strongest contrary reading.** Market and professional long-run measures are at or near pre-pandemic levels: 5y5y 2.19 (Nov avg) vs 2.15 in Feb 2026 and 2.03 in 2018–19; SPF 10y PCE 2.20. BB found no de-anchoring even in 2021–23 (Table 5) and say look-through is justified "with a limited catch-up effect and well-anchored expectations" (p.10). On BB's terms both conditions hold.

**(c) Data.**
- 5y5y: Feb 2026 2.15 → Nov 2.19 (+0.04); 5y breakeven 2.45 → 2.30 (−0.15) (`D_q9_checks.csv` rows 28–33) [O].
- SPF Q3 2026 median: PCE 10y 2.20, 5y 2.50 (`C_q4_summary.csv`) [C].
- Short-run, Feb 2026 → latest: SCE 1y 3.00 → 3.91 (+0.91, Oct); Michigan 1y 3.4 → 4.3 (+0.9, Nov prelim) (rows 14–16, 22–24) [O].
- Medium-run household: SCE 3y 3.00 → 3.29 (+0.29) (rows 25–27) [O].
- BB's channel: short-run expectations "feed fairly quickly into wages" (BB printed p.18) [O].

**(d) Weak spot.** Anchoring is a long-run concept, and the long-run market data support the judge. Our case rests on short-run and household measures, which BB's own estimates say react slowly to inflation (0.124 per point, Table 4) [A]. The Q4 SPF (Nov 16) could move the professional numbers.

**(e) Revision trigger.** We would call the expectations channel quiet if SCE 1y falls back below 3.4 (its Mar 2026 level) and SCE 3y below 3.0 while 5y5y stays ≤ 2.3. We would call it de-anchoring if 5y5y monthly average exceeds 2.46 (its 2021–23 monthly peak, `C_q4_summary.csv` row 23) or the Q4 SPF 10y PCE rises above 2.3.

**(f) Spoken (draft).** "Long-run market expectations are anchored: the 5-year, 5-year forward is 2.2, about where it was in February. What has moved is short-run expectations, up almost a point since February, and in Bernanke–Blanchard those feed into wages quickly."

---

## 2. "You cherry-picked the MCT's 2.8 over the trimmed mean's 2.3."

**(a) Judge.** "The Dallas trimmed mean was built to strip out exactly this kind of shock, and it says 2.3. Why lead with the bigger number?"

**(b) Strongest contrary reading.** The trimmed mean is the measure designed to remove relative-price shocks; the MCT includes sector trends that oil can contaminate (goods contributed 0.54 pp of its gap, `C_q6_summary.csv`). The MCT is volatile: 3.45 (Apr) → 2.55 (Jul) → 2.84 (Sep), Aug revised [C]. Picking whichever is higher is cherry-picking.

**(c) Data.**
- Panel, Sep 2026: trimmed 2.26, median PCE 2.67, MCT 2.84 (band 2.49–3.21), core 3.12, Logan measure 3.21, supercore 3.60 (`C_q6_summary.csv`) [C].
- Dallas's own alternative trim (19/20): 2.57 vs 2.22 original, Jun 2026 (`A_q2_dallas_data_extract.json`; raw `S3A_A_dallas_trimmed_2026-11-15/dallasfed_0813data.xlsx`, sheet data4) [A].
- Skewness (Dallas Kelly, 12m avg) +0.09 Jun 2026 vs 1977–2019 mean −0.14; positive in only 13% of 1977–2019 months [A].
- Slide 2: trimming 12m rates once gives 2.98 vs 2.27 monthly trim (slide 2 `D_trimmed_reconcile.csv`) [slide 2 D, audited].

**(d) Weak spot.** Dallas's own Aug 13 post says the evidence "doesn't offer a clear-cut conclusion" [A]. The alt-trim correction (+0.35 pp) is about half the MCT–trimmed gap (0.58); they are different adjustments [A coordinator]. Skewness data end in June.

**(e) Revision trigger.** If the trimmed mean's 6m annualised rate (2.42 Sep) and median PCE 6m (2.76) both fall below 2.3 by the Oct release (Nov 25), the "true trend above 2.5" reading weakens. If Dallas skewness turns ≤ 0, Logan's bias argument loses its mechanism.

**(f) Spoken (draft).** "We show the whole range, 2.3 to 3.6, not one number. Even Dallas's own alternative trim gives 2.6, and every measure in the range is above 2."

---

## 3. "The oil note is a five-country panel and an upper bound."

**(a) Judge.** "Your pass-through number comes from a panel of five economies, has no US coefficient, and the authors call it an upper bound. Why should it carry weight for US core PCE?"

**(b) Strongest contrary reading.** Correct on every point. No US coefficient is reported; the US is "significant" only in footnote 4. The sample after 2021Q1 is 22 quarters dominated by reopening and fiscal shocks. The authors "cannot distinguish a structural change … from the possibility that global supply shocks have become more frequent, more persistent, or both" (`10_slide2_research/outputs/C_q10_oil_note_verification.csv` row 25). The pass-through term "may partly reflect the co-movement of oil prices with broader global demand pressures" (row 43). Projections are "an upper bound … rather than a central prediction" (row 15).

**(c) Data.**
- Pass-through 0.001 pre → 0.014 post per pp relative oil inflation; persistence 0.35 → 0.65 (Table 2; `C_q10_lit_summary_update.md`) [slide 2 C, audited].
- Robust to V/U instead of output gap: +0.292 / +0.010, still significant (fn 6; verification row 20).
- Note's own conclusion: "second-round effects have not yet materialized; however, risks are mounting" (row 17).
- Projection inputs dated: Brent futures early Aug 2026; Brent then above $110 Sep 10–Oct 30, $92 on Nov 11 (`10_slide2_research/outputs/C_q8_oil_daily.csv`) [slide 2 C].

**(d) Weak spot.** Everything in (b). We cannot show the US coefficient. We use the note for direction (pass-through higher post-2021), not size.

**(e) Revision trigger.** If US energy-intensive core items (slide 2 confirming items: truck freight, food away from home) decelerate to pre-shock rates within two months of Brent at ~$92, the "higher pass-through" reading weakens for the US.

**(f) Spoken (draft).** "It's a panel and the authors call it an upper bound, so we use it for direction, not size. Its own conclusion is ours: second-round effects haven't materialised, but the risks are mounting."

---

## 4. "Short-run expectations just track gas prices."

**(a) Judge.** "Household one-year expectations are a gas-price thermometer. They'll fall as gas falls. Why read them as second-round risk?"

**(b) Strongest contrary reading.** In 2021–23 the 12m-change correlation with gas was 0.89 (Michigan) and 0.91 (SCE) (`C_q4_gas_comovement.csv` rows 6, 15) [C]. Gas is up $1.17 since Feb 2026 (`D_q9_checks.csv` rows 34–36); short-run expectations rose about 0.9 pp in the same window. Gas has fallen from $4.35 (Oct 5) to $4.00 (Nov 9) and Michigan 1y fell 4.7 → 4.3 in Nov prelim [C].

**(c) Data.**
- 2024–26 correlations: Michigan 1y −0.37, SCE 1y 0.40 (rows 9, 18) [C].
- Michigan 1y peaked at 6.6 in May 2025, with gas low, during the tariff episode (`D_q9_checks.csv` row 17) [O]: the series responds to salient price news generally, not gas alone.
- Medium-run moved too: SCE 3y +0.29 pp since Feb (row 27); SCE 3y still correlates with gas (0.47 full window, `C_q4_summary`/report C) [C].
- Oct 12m change: gas +41%, Michigan 1y +0.1 pp, SCE 1y +0.68 (`C_q4_gas_latest_change.csv` row 2) [C].

**(d) Weak spot.** The correlations are descriptive, small-n and autocorrelated [C]. The Michigan 2024–26 window straddles the 2024 phone-to-web switch (finding 1), which may distort its correlations. Concede that gas is part of it.

**(e) Revision trigger.** If gas holds near $4.00 or falls and SCE 1y returns to ≤ 3.4 (its Mar 2026 level) by the Dec SCE release, the "gas thermometer" reading wins for short-run expectations.

**(f) Spoken (draft).** "Gas is part of it, but not all: Michigan one-year expectations hit 6.6 in May 2025, when gas was cheap, on tariffs. And the three-year SCE measure is up too."

---

## 5. "Your catch-up evidence is anecdotal."

**(a) Judge.** "A CEO story, a Beige Book sentence and a small-business survey. Where is catch-up in the hard data?"

**(b) Strongest contrary reading.** It is not in the hard data. ECI W&S 3.12 y/y, AHE 3.12, ULC 8q 1.92 ≈ 2018–19 1.90 [B]. Richmond Fed wage diffusion indexes are below 2018–19 (mfg 20 vs 26.6; services 16 vs 30.4) [B]. BB find no catch-up effect (Table 2, p=0.765) [A].

**(c) Data.**
- Motive exists: ECI W&S y/y 3.12 minus headline PCE 12m 3.65 = −0.53 pp real (`D_q9_checks.csv` rows 84–85) [O].
- Plans: NFIB net 24% plan to raise compensation (highest since Dec 2025); Richmond CFO expected 2026 wage 4.3% mean (3.8 median), up from 4.0 (3.1) (`B_q5_summary.csv`) [B].
- Beige Book Oct 14: "inflation has spawned additional wage pressure in the form of higher cost-of-living demands" [B, verbatim].
- AHE 3m annualised 3.88 (Oct prelim) vs 2.90 Sep [B]; weak Aug base.

**(d) Weak spot.** All of it. Survey plans are not settlements; the CFO numbers were hand-transcribed (B flag). No hard-data series shows catch-up yet.

**(e) Revision trigger.** Catch-up is showing in hard data if ECI W&S q/q annualised exceeds 4.0 in 2026Q4 (Jan 30 release, after finals) or AHE 3m stays above 3.8 in the Nov jobs report.

**(f) Spoken (draft).** "Agreed, it's not in the hard data yet: wages are 3.1% and real wages are still about half a point negative. That gap is the motive, and the surveys say plans are rising; we're watching whether settlements follow."

---

## 6. "Wage growth is just productivity."

**(a) Judge.** "Productivity is growing 2% plus; AI may be lifting it. Wage growth of 3–4% is consistent with 2% inflation."

**(b) Strongest contrary reading.** Output per hour +2.06 y/y, 2.36 8q annualised, 2020–25 trend 2.21 [B]. With a 2.2 trend the benchmark is 4.2%, and only hourly comp (4.49) exceeds it (`D_q9_checks.csv` rows 52–83) [O]. ULC 8q 1.92 confirms wage growth is productivity-covered.

**(c) Data.** ULC already nets out productivity: 2.39 y/y, 1.92 8q (rows 45) [B/O]. BB: trend productivity "has no statistically significant effect on wage growth" in their estimates (printed p.18) [O].

**(d) Weak spot.** This attack is largely right on the hard data. Our concern cannot be wages-now; it is expectations and prices over cost.

**(e) Revision trigger.** If ULC 8q rises above 2.5 (2026Q4 release, early Feb), productivity no longer covers wages.

**(f) Spoken (draft).** "That's exactly why we look at unit labor costs, which net out productivity: 1.9% over two years, about where they were in 2018–19. On wages alone, we don't see a second round."

---

## 7. "Unit labor costs are noisy."

**(a) Judge.** "ULC fell 0.7% annualised last quarter and gets revised by a point. You can't hang anything on it."

**(b) Strongest contrary reading.** q/q annualised SD was 3.04 pp in 2018–19 (range −4.2 to +6.2) and 2.10 in 2024Q1–2026Q3 (`D_q9_checks.csv` rows 37–40) [O]. The Nov 5 revision moved 2026Q1/Q2 y/y from 0.4/1.4 to 1.8/2.6 [B].

**(c) Data.** 4q and 8q are steadier: y/y 1.46 → 2.18 → 1.82 → 2.57 → 2.39 and 8q 1.57 → 2.06 → 1.99 → 2.13 → 1.92, 2025Q3–2026Q3 (rows 41–45) [O]. Hourly comp 4.49 vs ECI 3.12 shows measure dependence [B].

**(d) Weak spot.** Revisions of ~1.4 pp to y/y are as large as any signal. ULC covers nonfarm business only and includes benefits; its relevant price is the business deflator, not PCE [B].

**(e) Revision trigger.** Two consecutive y/y readings above 3.0 would turn the ULC exhibit from "benign" to "pressure".

**(f) Spoken (draft).** "Quarterly ULC is noisy, so we use four- and eight-quarter rates: 2.4 and 1.9. Both are near 2018–19 levels, and the November revision moved them up, not down."

---

## 8. "Bernanke–Blanchard, read literally, say no labor-driven second round."

**(a) Judge.** "Your lead exhibit is BB. They find no catch-up effect, and their steady-state V/U is 1.2. You're at 1.06. Their framework says the second round isn't coming from labor."

**(b) Strongest contrary reading.** Fair. Catch-up −0.024, p=0.765 (Table 2) [A]. V/U 1.06 (Sep) vs BB's assumed steady-state benchmark 1.2 (its 2019Q4 value; BB say it is not tightly estimated, p.36 and fn 16; their wage equation is continuous, not a threshold) and the 2.04 peak (`A_q1_vu.csv` row 106) [A]. BB: "the second-round and indirect effects of product-market shocks [are] relatively modest" (p.40) [A]. Price-shock effects are "quite short-lived" (p.30) [A].

**(c) Data (BB's own other channels).**
- BB's wage equation runs price shocks into wages via short-run expectations, which "feed fairly quickly into wages" (printed p.18) [O]. SCE 1y +0.91 pp since Feb 2026 (`D_q9_checks.csv` row 24) [O].
- BB p.9: "the longer the episode, or the lower γ, the stronger the effect on steady-state inflation" [O]. Inflation above 2 for 67 months (`C_q8_time_above_summary.csv` row 2) [C].
- BB Table 3: energy has "some second-round price-price effects" (p.25), a non-labor route [A].
- V/U direction: 0.87 (Dec 2025) → 1.06 (Sep 2026), +0.19 (`D_q9_checks.csv` rows 86–88) [O]; BB's wage equation includes the change in V/U [A].
- BB used Cleveland Fed model expectations, not surveys; projections are CPI [A].

**(d) Weak spot.** The labor-tightness leg of BB genuinely points away from a second round. BB estimate short-run expectations respond slowly (0.124). Our expectations data are survey-based, not BB's measure.

**(e) Revision trigger.** If V/U rises above BB's assumed 1.2 benchmark (Oct JOLTS, early Dec) while SCE 1y stays ≥ 3.9, both BB channels would be pushing wages up more than at the 2019 benchmark (a watch point, not a BB threshold). If short-run expectations retrace to Feb 2026 levels, BB's framework says little second-round risk remains.

**(f) Spoken (draft).** "You're right that labor tightness is below the 1.2 benchmark they assumed for steady inflation, and their catch-up term is zero. But in their model the faster route is short-run expectations into wages, and those are up almost a point since February."

---

## 9. "Logan's 13 surveys don't reproduce, and her 'long-run near 2%' fails for households."

**(a) Judge.** "Your own reconstruction of Logan's survey average is 3.4, not 3.1. And Michigan long-run is 3.4. Which is it?"

**(b) Strongest contrary reading.** Our 13-survey simple average 3.38 (median 3.30); dropping the Conference Board mean gives 3.18 (`C_q4_logan_aggregate.csv` rows 2–3, 24) [C]. Household long-run: Michigan 5–10y 3.4 (Nov prelim), SCE 3y 3.29 [C]. So either expectations are higher than Logan says or our numbers are wrong.

**(c) Data.**
- Logan's text says respondents "expect **PCE** inflation to run around 3.1 percent" and names "households, businesses and market participants" [O, `outputs/text/logan_2026-11-10_paragraphs.txt` para 169]. Her figure is PCE-converted and her list is unpublished; ours mixes CPI-based and PCE-based answers and includes 4 professional surveys. Non-reproduction is expected, not an error in either.
- Long-run by respondent type: 5y5y 2.19, SPF 10y PCE 2.20 vs Michigan 5–10y 3.4, SCE 3y 3.29 [C/O].
- Michigan mode break: web-basis 2022 peak ≈ 4.0 (finding 1) [O].

**(d) Weak spot.** We cannot reproduce her number and should not quote 3.1 as ours. Michigan's household long-run level is inflated by the web switch by an unknown amount.

**(e) Revision trigger.** If the Q4 SPF 10y PCE and 5y5y both stay ≤ 2.3, "market and professional long-run near 2" stands; if Michigan 5–10y (final Nov 20) rises above 3.9 (its Oct 2025 level), household long-run is drifting.

**(f) Spoken (draft).** "Logan converted to a PCE basis with her own list; we can't replicate it, so we don't use her 3.1. Our point is the split: markets and forecasters near 2.2 long-run, households well above."

---

## 10. "'Nearly six years above target' is 5.6 years."

**(a) Judge.** "Five and a half years isn't nearly six."

**(b) Strongest contrary reading.** 67 months through Sep = 5.58 years; 68 with Oct est. = 5.67; six years completes Mar 2027 (`C_q8_time_above_summary.csv` row 2) [C]. On the originally published vintage core PCE starts Apr 2021 [C].

**(c) Data.** No month at or below 2.0 on headline or core PCE since Feb 2021; closest approach headline 2.255 (Mar 2025) [C]. "Nearly six years" is Logan's phrase (para 142, 156) [O].

**(d) Weak spot.** Rounding up; vintage-dependent start.

**(e) Revision trigger.** None needed; state the exact number.

**(f) Spoken (draft).** "Sixty-seven straight months above 2% through September, five and a half years, and no single month back at 2 since February 2021."

---

## 11. "Barr's 52.8% is a stale vintage, and a falling labor share means margins, not wages."

**(a) Judge.** "That number was revised to 53.3. And if labor's share is falling, wages aren't the problem: profits are. That's greedflation, not a second round."

**(b) Strongest contrary reading.** Correct on the vintage: 52.8 matches the Sep 3 vintage of PRS85006174 2026Q2 (reconstructed from the index); current is 53.3 Q2, 53.0 Q3 (`B_q3_labor_share.md`) [B]. Labor share = ULC / output price; ULC +2.39% and labor share −1.60% imply output price +4.05% y/y (`D_q9_checks.csv` rows 46–48) [O]. Prices outrunning unit labor costs means the nonlabor share rose. Unit nonlabor payments include profits but also depreciation, production taxes less subsidies, net interest and rental income (BLS calculation methods), so this alone does not establish wider profit margins; higher margins or oil rents are possible explanations that need separate evidence.

**(c) Data.**
- Over two years: ULC 1.92% ann., implied deflator 3.37% ann. (rows 49–51) [O].
- Record low on the index in current vintage: 2026Q3 93.729 (1947–2026) [B].
- Nonlabor payments +8.4% y/y vs labor compensation +4.7% (Q3) [B].

**(d) Weak spot.** The judge's reading is largely the data's reading. Not decomposed: nonfarm business includes oil and gas extraction, so part of the nonlabor-share rise may be the oil windfall (first round) rather than broad pricing power; nonlabor payments are not decomposed (profits vs depreciation, taxes, interest, rents). Implied deflator is derived from the identity, not the published BLS IPD (PRS85006143 not pulled). Barr says "national income"; the series is nonfarm business output [B].

**(e) Revision trigger.** If the labor share stabilises while ULC rises above 3% y/y, the pressure is shifting from the nonlabor share to wages.

**(f) Spoken (draft).** "The current BLS number is 53.0% in the third quarter, a record low. It tells us prices have outrun unit labor costs, about 4% versus 2.4%, so the nonlabor share, not wages, has risen so far."

---

## 12. "Your wage benchmark's sign depends on the measure and the trend."

**(a) Judge.** "ECI and average hourly earnings are below your 3.5 benchmark; the Atlanta tracker and hourly compensation are above it. With a 2.2 trend, the benchmark is 4.2 and almost everything is below. Which is it?"

**(b) Strongest contrary reading.** Correct. Gap to 3.52: ECI W&S −0.40, ECI total comp −0.18, AHE y/y −0.40, AHE 3m +0.36, WGT +0.38, hourly comp +0.97. Gap to 4.21: all negative except hourly comp (+0.28 y/y, +0.12 8q) (`D_q9_checks.csv` rows 52–83) [O]. The trend choice moves the benchmark ~0.7 pp, as large as the gap [B].

**(c) Data.** ULC sidesteps the trend choice: 2.39 y/y, 1.92 8q [B]. Measure gaps: hourly comp includes benefits and is revised heavily; ECI W&S excludes benefits [B].

**(d) Weak spot.** No measure-robust conclusion that wages exceed a 2%-consistent pace. The honest summary is "near the benchmark, sign uncertain".

**(e) Revision trigger.** Wage pressure is clear only when ECI W&S y/y exceeds 4.2 (the high benchmark); it is clearly absent if hourly comp 8q falls below 3.5.

**(f) Spoken (draft).** "Depending on the measure and the productivity trend, wages are a few tenths either side of a 2%-consistent pace. That's why we lean on unit labor costs, which are near 2."

---

## 13. "The Logan measure's rise is all in your October estimate."

**(a) Judge.** "Twelve-month non-housing, non-transport services is 3.2, the same as a year ago. Your 'momentum' is one estimated month."

**(b) Strongest contrary reading.** 12m: 3.15 (Sep 2025) → 3.21 (Sep 2026) → 3.24 (Oct est.) (`D_q9_checks.csv` row 12; `C_q6_logan_measure.csv` rows 95, 107–108) [O/C]. 3m: 2.61 → 3.46 (Oct est.) rests on an estimate covering 54% of core with no uncertainty band [C]. And 3.46 is not unusual: 4 of the prior 12 months were at or above it; max 4.25 Jan 2026; 12-month mean of the 3m rate 3.18 (rows 2–6) [O]. A move of ≥ 0.86 pp in one month occurred 5 times since Jan 2024 (SD 0.63) (rows 9–11) [O].

**(c) Data.** The level is the point, not the change: 12m 3.21 vs 2018–19 avg 2.27 [C]; the 3m rate's 2018–19 mean 2.22 and max 3.35 (rows 7–8) [O]. Six of the 13 3m readings from Oct 2025 to Oct 2026 est. (Dec, Jan, Feb, Mar, May, Oct est.) exceed the 2018–19 max of 3.35 (`C_q6_logan_measure.csv`) [O].

**(d) Weak spot.** "Momentum picked up" is true only against Jul–Sep 2026. It should not be the headline. The estimate overstates the exact Sep m/m by ~0.009 pp [C].

**(e) Revision trigger.** Official Oct PCE (Nov 25): if the 3m annualised rate prints below 3.0, drop "momentum picked up". If 12m exceeds 3.39 (its Jan 2026 high), the plateau is breaking upward.

**(f) Spoken (draft).** "The story is the level: about 3.2% for a year, a full point above 2018–19. October's estimate picks up from a soft summer, but it's back to where it was earlier this year, not a breakout."

---

## 14. "NFIB price plans at a four-year high are a first-round echo, not a second round."

**(a) Judge.** "Small firms planning price hikes after an oil and tariff cost shock is the first round, by definition."

**(b) Strongest contrary reading.** Correct in principle: price plans can't distinguish passing on input costs from responding to wages or expectations. PPI stage 1 is up 14.1% y/y (slide 2 `C_q8_ppi_stages_summary.csv` row 12) [slide 2 C]. NFIB net 37% plan to raise prices, highest since Jul 2022 [B]; net 33% actually raised (hist. avg 14) [B].

**(c) Data.** NFIB labor costs as most important problem: 7%; compensation plans 24 vs 2018–19 21.5 [B]. Labor is not the cited driver.

**(d) Weak spot.** Concede. NFIB is a symptom of a long first round; that is the bridge line's point, not evidence of a second round.

**(e) Revision trigger.** If price plans stay ≥ 35 after Brent stays near $92 for two months (Dec NFIB, released Jan), the persistence is no longer tied to input costs.

**(f) Spoken (draft).** "Agreed, on its own that's the first round being passed on. We show it because a longer first round is what gives second-round effects time to form."

---

## 15. (new) "Michigan's long-run expectations are above their 2022 peak? That's the web switch."

**(a) Judge.** "Michigan moved to web interviews in 2024, and web respondents report higher inflation. Comparing 3.4 to a phone-era peak is apples to oranges."

**(b) Strongest contrary reading.** Correct. UMich's web-only series puts June 2025 (4.0) equal to "the peak reading from mid-2022" [O, UMich Jun 27, 2025 update]. So the web-basis 2022 peak was about 4.0; current 3.4 is below it. A secondary account says web respondents are "more willing to express high inflation expectations" [2, unverified].

**(c) Data.** Michigan 5–10y path: 4.4 (Apr 2025) → 3.3 (Feb 2026) → 3.4 (Nov prelim) (`D_q9_checks.csv` rows 18–21) [O]; essentially flat through the oil shock (+0.1 since Feb).

**(d) Weak spot.** Our C summary's 2018–19 average (2.47) and 2021–23 peak (3.2) are phone-era. The size of the mode shift for inflation expectations is not quantified in what I opened.

**(e) Revision trigger.** Use only within-web comparisons (2024+) for Michigan long-run.

**(f) Spoken (draft).** "Right, Michigan switched to web in 2024, so we compare it only with itself since then: long-run expectations are 3.4, down from 4.4 in April 2025 and flat since the oil shock."

---

## 16. (new) "Unit labor costs are at 2018–19 rates. Isn't that the end of the second-round question?"

**(a) Judge.** "Your best cost measure is benign. What's left?"

**(b) Strongest contrary reading.** ULC 8q 1.92 vs 2018–19 1.90 [B]; ECI W&S 8q 3.35 [B]. The labor-cost channel is quiet.

**(c) Data.** What's left is the non-labor route: price over cost (implied deflator 4.05 vs ULC 2.39, rows 46–48) [O]; BB's price-price effects (p.25) [A]; services ex housing ex transport 3.21 [C]; short-run expectations +0.9 pp [O].

**(d) Weak spot.** These are not second-round effects in BB's wage sense. They are persistence of the first round plus expectation risk.

**(e) Revision trigger.** As in attack 7.

**(f) Spoken (draft).** "On labor costs, yes, there's no second round yet. What we can't rule out is the other route: prices running ahead of costs and short-run expectations rising."

---

## 17. (new) "V/U is rising. Isn't the labor channel turning on?" (the opposite attack)

**(a) Judge.** "V/U is up from 0.87 to 1.06 in nine months and unemployment fell to 4.1. Aren't you understating the labor risk?"

**(b) Strongest contrary reading.** V/U +0.19 since Dec 2025; above 1.0 since Apr 2026 (`D_q9_checks.csv` rows 86–88; `A_q1_vu.csv`) [O/A]. UNRATE 4.5 (Nov 2025) → 4.1 (Oct 2026) [A].

**(c) Data.** Still below 2018–19 (1.16) and BB's assumed 1.2 benchmark (2019Q4 value; not tightly estimated, p.36) [A]. The Dec→Jan jump (0.87 → 0.98) may reflect population controls and the JOLTS annual revision (unchecked) [A].

**(d) Weak spot.** Part of the rise may be a level shift, not tightening. Oct JOLTS is not out before Nov 18.

**(e) Revision trigger.** V/U above 1.2 (BB's assumed benchmark; a watch point, not an estimated threshold) on the Oct or Nov JOLTS.

**(f) Spoken (draft).** "It has risen, to about 1.06, but it's still below 2018–19 and below the 1.2 that Bernanke–Blanchard assumed for steady inflation. In their model, tightness pushes wages continuously, so we watch the level, not a line."

---

## Worth a look
1. **Michigan mode break** (finding 1): affects `C_q4_summary.csv` row 3 peak comparison and the C report's "above its 2021–23 peak". Also possibly the Michigan 2024–26 gas correlations.
2. **Logan 3m rate**: Jan 2026 (4.25) and Feb (4.07) were higher than Oct est. The Jan spike is a January-effect candidate (residual seasonality in services, common in PCE); not tested.
3. **Implied output deflator 4.05% y/y** vs core PCE 3.12: the gap likely reflects energy in nonfarm business output. Pull PRS85006143 (IPD) and the BEA nonfinancial corporate unit-profit table to separate oil rents and other nonlabor payments from profit margins.
4. **"Upstream pressure at a record"** (slide 2 bridge) is a record **index level**; stage 1 y/y 14.1 ranks 16th of 106 months (peak 22.4, May 2021) (`10_slide2_research/outputs/C_q8_ppi_stages_summary.csv` row 12). One stage-1 sub-index is a record on rates: services inputs to stage-1 goods producers (WPSID5112), 3m ann. 35.5, y/y 19.2, both rank 1 since 2018 (row 86).
5. Real ECI wages −0.53 pp: a catch-up motive that BB's framework (catch-up ≈ 0 pre-2020) says historically doesn't translate. Logan's CEO anecdote is precisely this case.
