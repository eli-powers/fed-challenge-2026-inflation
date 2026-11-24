# Slide 2 research: final report (Q1–Q12)

**Status: Audited — converged R3** (Codex, Nov 15). R1 found 3 Blocking items (GEMUS shock normalisation; intracity transportation mislabelled as mass transit; freight/airfare correlations stated as causal) and 1 Non-blocking (headline label). All were fixed. R2 caught a CSV-quoting regression in the R1 fix, closed in R3. No factual, source or arithmetic item is open. Codex also audited the tagging files (`08_shock_tagging/`) for the first time: the exposure builder reproduces byte-for-byte, and electricity is in the energy block. The judgment calls in section 4 are Eli's.**

**Workbook:** [`01_Finals/data/Slide2_Inflation_Data.xlsx`](../../../01_Finals/data/Slide2_Inflation_Data.xlsx). It has 11 research tabs and 5 grey `raw_` tabs. There are 5,512 live formula cells. A LibreOffice recalculation gives 0 mismatches and 0 errors, and 138 checks against the agents' CSVs pass, including the four slide 1 reproduction numbers. All 10 charts were rendered and inspected; the chart XML has `smooth val="0"` / `invertIfNegative val="0"`.
**Rebuild:** `python3 -I "02_Research/Subtasks/10_slide2_research/code/build_slide2_workbook.py" --verify`. Fix the inputs in `outputs/`, not the xlsx.
**Reports:** `report_A.md` … `report_D.md` (each with a coordinator review). Audit trail: `06_Audits/slide2_research/`.

---

## 0. Disagreements with the premise (read first)
1. **"Spread" vs "scale."** The slide asks how widely the energy shock has spread. On our measure, breadth was already high before the oil shock:
   - Core 12m breadth: 58.8 in Sep 2025 and 52.9 in Feb 2026, the last month before Brent jumped. It was 60.6 in Sep and is 54.0 in Oct est.
   - Energy-tagged 12m breadth: 71.3 (Feb) → 67.0 (Sep) → 73.3 (Oct est.).
   - Untagged, excluding hospitals: 57.9 → 57.9 → 57.8.
   - What did rise is the energy group's average 12m rate: 3.14 → 3.92 → 4.30%.

   Source: `outputs/D_preshock.csv`, re-derived by the coordinator and Codex. Codex notes that "did not widen" is too strong: energy-tagged is slightly above Feb in Oct est. (71.3 → 73.3) and core 52.9 → 54.0. "Already broad, with hotter exposed items" is the defensible reading. The data fit "the first round got bigger and longer" better than "it spread". Reframing is Eli's call (Judgment calls for Eli N6). Per the GO's override, the research ran the conservative version, which is the slide as scoped.
2. **"Concentrated fits Bowman" misstates her.** In the same speech she says pressures "may be broadening" (verbatim, saved RTF). The real Bowman–Waller difference is whether broadening persists, which is slide 3A's question.
3. **The 3% cutoff is a knife-edge for month-to-month changes.** 35.4% of core weight sits between 3.0 and 3.5% (OER, hospitals, restaurants). The Sep → Oct change in 12m breadth is −6.6 pp at a 3% cutoff, +5.8 at 3.5% and +2.0 at 2%. The **level relative to 2018–19 holds at every cutoff from 2 to 4%** (+11 to +25 pp).

## 1. Slide-worthiness ranking (data and ratings only; the decision is Eli's)
Workbook tab `Slide_worthiness`. Ratings run from 1 to 5.

| Exhibit | Agent | Stress test (D) | Coordinator | Basis |
|---|---|---|---|---|
| Upstream panel (PPI stages 1–2, oil) | 4 (C) | 4 | **4** | Stage 1 is at a 2018–present record level. Energy's contribution turned negative in Oct (−0.25 pp stage 1, −0.98 pp stage 2) while services inputs rose. Needs the WPSID51/52 labels. |
| Breadth by measure | 4 (B) | 3 | **4** | The level vs 2018–19 holds at every cutoff and exclusion (ex OER, ex hospitals). The Sep → Oct change is fragile. |
| Tagged breadth | 3 (A) | 2 as breadth / 4 as rates | **3** | Within-group breadth hasn't risen since Feb. Group average rates separate cleanly under every tag variant. |
| Bowman-style attribution | 3 (A) | 2 | **2** | It depends on how the 2% is allocated (energy 23–60%). No method reproduces her quarter each. |
| Sticky/flexible | 2 (B) | 2 | **2** | Covers 61% of core weight. The flexible set is 9% of weight and noisy. |

**2a/2b split:** the strongest two exhibits (upstream, which is about the first round lengthening, and breadth level vs baseline) answer different questions. On the evidence they do not need to share one slide. That is all the data says; the decision is Eli's.

## 2. Per question (data only)

**Q1. Tags** (`report_A.md`; `outputs/A_q1_*`)
- **Tariff exemption.**
  - The Apr 11, 2025 presidential memorandum (DCPD202500470) defines "semiconductors" in E.O. 14257 to include HTS 8471, 8517.13, 8542 and others. Effective Apr 5, 2025.
  - The Supreme Court ended the IEEPA reciprocal tariffs on Feb 20, 2026 (*Learning Resources v. Trump*).
  - The successors were Section 122 (10%, Feb 24–Jul 24, 2026) and Section 301 forced-labor tariffs (from Jul 24). Both exempt 8471, 8517.13.00 and 8542.
  - Section 232 semiconductors (Jan 14, 2026) covers a "very narrow category". Phase two is unconfirmed.
- **Energy spot-check.** Recomputing from the I-O tables matches `item_exposures_full.csv` (max diff 4.9e-06; cutoff 0.03468). No leaf changes side.
- **One proposed change:** leaf 187, nursing homes, energy → untagged (N2).

**Q2. Attribution** (`Attribution!A6:L32`; chart at `Attribution!N5`). Shares of above-target core PCE, 12m (energy / tariff / AI / untagged).

| Method | Sep | Oct est. |
|---|---|---|
| (a) own-weight | 29.2 / −0.1 / 18.0 / 52.9 | 31.9 / 5.1 / 15.1 / 47.8 |
| (b) excess over 2% | 23.0 / 7.9 / 13.0 / 56.1 | 24.2 / 9.8 / 11.9 / 54.1 |
| (c) 2% on untagged | 59.8 / 18.6 / 21.3 / 0.4 | 59.7 / 22.1 / 18.1 / 0.1 |

- Group 12m rates (Sep): energy 3.92%, tariff 1.99%, AI ~12.5%.
- Bowman: "Tariffs, energy, and AI-related price pressures each accounted for roughly one-fourth of above-target core PCE inflation over the 12 months ending in September." Her method is not disclosed.

**Q3. Tagged breadth** (`Tagged_breadth!A5:K11`; Oct change `B16:B21`). Within-group breadth.

| Group | 12m Sep → Oct est. | 3m Sep → Oct est. |
|---|---|---|
| Energy | 67.0 → 73.3 | 61.9 → 69.0 |
| Tariff | 29.1 → 38.5 | 31.3 → 42.3 |
| AI | 90.0 → 90.0 | 28.4 → 28.4 |
| Untagged | 63.2 → 50.5 | 43.0 → 40.3 |
| Untagged ex hospitals | 57.9 → 57.8 | |

- **Oct 12m change, −6.588 pp in total:** untagged −8.801 (of which hospitals −8.721), energy +1.163, tariff +1.044, AI +0.006.
- **Sensitivities:** `Tagged_breadth!A25:G29`. Under the strict 5% cutoff, energy has 16 leaves, 3.5% of weight, and 59.2% breadth.

**Q4. Breadth by measure** (`Breadth_measures!C6:H15`; charts at `K5`, `K30`, `K55`)

| Measure | 12m Sep → Oct est. | 3m Sep → Oct est. | 2018–19 avg (12m / 3m) |
|---|---|---|---|
| Core | 60.6 → 54.0 | 44.8 → 45.5 | 35.2 / 39.2 |
| Supercore | 69.0 → 54.5 | 39.8 → 38.7 | 25.9 / 29.6 |
| Core goods | 29.1 → 36.4 | 33.6 → 38.8 | 12.4 / 26.5 |
| Core services | 70.8 → 59.7 | 48.5 → 47.6 | 42.6 / 43.3 |

- **Hospital contributions to the 12m change:** core −8.72, supercore −15.12, core services −11.54. Zero at 3m.
- **Headline is backup:** 12m 59.8 → 54.0, 3m 43.7 → 46.3. Headline 12m is **below** core in Sep, so "rises mechanically" is not true at 12m.
- **Cutoff sensitivity:** `Breadth_measures` row 24 onward.

**Q4b. Breadth vs the trimmed mean** (`Breadth_measures` row 52 onward)
- Our Dallas-method replication gives 2.848 / 2.427 / 2.265 (1m / 6m / 12m, Sep) against the published 2.84 / 2.42 / 2.26.
- The Dallas measure trims the top 31% of *monthly* changes. Items above 3% at 12m lose 33% of their weighted months from the top, and their kept months average 2.65% vs 4.80% over all months.
- Trimming the 12m rates once instead gives 2.98% for core.
- The Dallas 12m fell 2.76 → 2.27 (Sep 2025 → Sep 2026) while 12m breadth rose 58.8 → 60.6.
- **Ex OER ("harmonized" scope):** 12m 54.4 → 46.8 against a 2018–19 average of 25.6. Excluding both OER and hospitals: 49.3 → 52.1 against 28.4.

**Q5. Sticky vs flexible** (`Sticky_flexible!A5:G8`; Atlanta Fed panel and chart below)
- Coverage is 61% of core weight: sticky 52.1%, flexible 9.1%.
- Sticky 12m 60.3 → 62.8; flexible 12m 35.2 → 35.7.
- Atlanta Fed-style CPI basket: sticky 12m 66.1 → 67.9 (approx.).
- Atlanta Fed flexible CPI, 1m annualized: 10.2 (Aug), 22.2 (Sep), 3.0 (Oct).
- Noisy, with poor flexible coverage.

**Q6. Waller** (`Waller!B6:C7` plus variants below)
- Core services 12m, weighted leaf: **70.8** (Sep) → 59.7 (Oct est.).
- Count: 63.1 → 60.7.
- Only the weighted variants exceed 70%.

**Q7. Hospital base effect** (`Hospital_base_effect!G5:J12`; evidence list below; chart at `G25`)
- The Oct 2025 jump (+0.893% leaf 184 SA; +1.410% PPI NSA; z 2.73 / 3.29) is a **measured price, not a fill**. The Oct 2025 PPI was published Jan 14, 2026, with response rates "within the normal range". The driver is the October Medicare inpatient reset (+5.96%).
- **The base-effect line can be said.**
- **Revision risk:** Aug 2026 printed +0.62% first and is +0.22% now (ALFRED). To keep the 12m above 3%, Oct 2026 would need a +0.26 pp upward revision to the NSA PPI. Only 1 of 22 recent revisions was that large (D).

**Q8. PPI upstream** (`PPI_stages!A6:I12`; charts at `K5` and `K30`; oil at `AD5`)

| Series | Oct m/m | 3m ann. | y/y |
|---|---|---|---|
| Stage 1 (WPSID51) | +0.55 | 18.9 | 14.1 |
| Stage 2 (WPSID52) | −0.21 | 16.4 | 13.2 |
| ID62 (unprocessed goods) | −3.08 | 16.8 | 17.1 |

- ID62's Sep 3m annualized rate was revised from 41.5 to 31.0.
- **Oil:** Brent peaked at $135.51 on Oct 2, fell 14.2% on Nov 4 to $91.84, and was $92.14 on Nov 11. Oct PPI was priced around Oct 13 (Brent $125.78).

**Q9. ISM note** (`External`)
- It is a Board-staff text-mining index built from ISM free-text responses. It is not public, and there is no latest reading.

**Q10. FEDS oil note** (`External`; `outputs/C_q10_*`)
- 43 claims checked.
- Country detail exists only in footnote 4: pass-through is significant in the US, Canada and Japan, not in the euro area or UK. No US coefficient is reported.
- GEMUS: the "GDP hit about twice as large" has no comparator number.
- Our summary's "late-Oct spike above $110" is wrong: Brent was above $110 from Sep 10.

**Q11. Confirming items** (`External`)
- **Airfares:** weak fuel linkage (+8% Dec–Feb, before the spike).
- **Freight:** PPI truck freight (NSA) +3.9% in Oct while SA diesel fell 7.9%. Consistent with delayed fuel pass-through, but demand and other costs are not separated; correlations are not causal estimates.
- **Food:** at home +0.44%, away from home +0.52% in Oct. Truck-to-food correlations peak at 7–8-month lags.
- **Transportation services +0.8%:** intracity transportation (+0.39 pp; NSA; mass transit plus taxis/rideshares, split unverified) plus insurance (+0.28 pp) make up 0.67 of it. Airfares contribute +0.07.
- **Motor vehicle insurance +0.7%:** an ordinary size (rank 42 of 103 months), in the model-year update window. BLS lists no energy link.

**Q12. Stress test:** `outputs/D_qa_prep.md` (16 attacks) and `outputs/D_verbal_cues.md`. See section 0 and `report_D.md`.

## 3. Flags
**Couldn't verify:**
- Section 232 phase two;
- whether the Bryan–Meyer 2010 grouping still matches the current Atlanta Fed basket;
- the Medicare payment-rule figure;
- the revision counts in `D_hospital_flip.csv`;
- the electricity share of the energy-tag I-O block;
- the definition of PCE line 279;
- ISM availability beyond the note;
- the cause of the Oct 2 Brent jump;
- the food lag correlations (not recomputed).

**Worth a look:**
1. The PPI stage labels were wrong in earlier notes (ID61–64 are by commodity type; the stages are ID51–54), and ID62's Sep value was revised down 2.0%.
2. The Feb → Sep rise in core 12m breadth (+7.7 pp) is mostly hospitals re-entering above 3%, the mirror image of the Oct drop.
3. Supercore and core services 3m breadth peaked in Nov 2024 (86%, 89%), above 2022. Not decomposed.
4. Leaves 51 and 71 (calculators, phones) have identical rates.
5. CPI car insurance is −5.0% y/y vs PCE +0.3% (Sep), while repair costs are +5.8% y/y.
6. Slide 1 FINAL's history line (35.7 / 39.7 / 78.8) uses sub-line figures. The leaf figures are 35.2 / 39.2 / 79.7.
7. The tariff group runs at 1.99% 12m, yet Bowman gives tariffs a quarter.
8. Intracity transportation +6.6% (NSA; includes taxis/rideshares) supplies half of transportation services' +0.8.
9. The Atlanta Fed flexible CPI swung 10.2 → 22.2 → 3.0 (1m annualized, Aug–Oct).

**Codex:** the Atlanta Fed explainer points to the Bryan–Meyer 2010 table, which supports the sticky/flexible classification's provenance but does not verify every detailed mapping. Exposure-group contributions describe where price increases occur, not which shock caused them.

## 4. Judgment calls for Eli (both positions)
Full text is on the workbook tab `Judgment_calls_and_paywalled` and in `06_Audits/slide2_research/STATUS.md`.

| # | Item | Claude | Other |
|---|---|---|---|
| N1 | Logan measure and trimmed components (roadmap R9) not added | Covered only via Q4b | — |
| N2 | Leaf 187 nursing homes: energy → untagged | Keep `tag_final`; show as a sensitivity | A: change it |
| N3 | Whether and how to show the Bowman attribution | Backup only; method-dependent | A 3/5, D 2/5 |
| N4 | PPI stage labels (WPSID51/52; ID62 is not a stage) | Fix the roadmap and STATE wording | C: same |
| N5 | Slide 1 history line is sub-line, not leaf | Check the slide 1 workbook and cues | — |
| N6 | **Premise: "spread" vs "scale"** | Data favour "bigger and longer first round"; Eli decides the framing | D: reframe |
| N7 | 3% knife-edge | Quote levels vs 2018–19, not monthly changes | D: add a distribution view |
| N8 | Roadmap wording: "headline mechanical", "Waller count", "concentrated fits Bowman" | Fix all three | D: same |
| N9 | GO revised mid-run (16:25) | All added items covered; process note | — |

**Codex positions (R1):** N6, "already broad, with hotter exposed items" is defensible, while "did not widen" is too strong. N3, keep the attribution as explicitly descriptive backup with the method range, or omit it. N2, the borderline tags are sensitivity choices, not errors.

## 5. Paywalled links
Listed on the workbook tab `Judgment_calls_and_paywalled`, from `outputs/A_paywalled.csv`, `B_paywalled.csv` and `C_paywalled.csv`. They include the ISM survey site (login-gated). None of them affects a reported number.

## 6. Re-pull checklist for Nov 18
- [ ] **PPI:** no new release before Nov 18 (Nov PPI is in Dec). Recheck the Oct values only if BLS posts a correction.
- [ ] **Oil:** extend the daily Brent/WTI series to Nov 17–18 (rerun `code/C_q8_fetch.py` into a new `_2026-11-18` folder; update `build_raw_oil`'s path).
- [ ] **Atlanta Fed sticky CPI:** no change until the Nov CPI (Dec).
- [ ] **Oct PCE inputs:** if any October build input is revised, rerun `04_oct_pce_build`, then slide 1 `C_breadth.py`, then `B_q4`, `A_q2`/`A_q3`, `D_*`, `Z_coordinator_extras.py`, then rebuild with `--verify`.
- [ ] **Hospital PPI:** check for any revision to the Oct 2026 preliminary value (+0.677% NSA) before the cutoff.
- [ ] **Fed speeches Nov 14–18:** any official citing breadth, trimmed mean or attribution goes in `External_views`.

## 7. Eli's decisions (Nov 15, main window; side-chat inputs folded in)
Analyses E (stage 1 decomposition, side chat), F (attribution drivers, ex-hospital series, group rates) and G (own-baseline attribution and excess path) came after the R3 audit. **Audited: converged R1 in a separate audit, `06_Audits/slide2_followups/` (Nov 15).** All numbers reproduce byte for byte. Four style/metadata fixes were applied. One judgment call is with Eli: whether the S2-E1 line carries a qualifier.

| # | Decision | Status |
|---|---|---|
| S2-E1 | **Framing:** breadth was already high before the oil shock; what changed is the intensity and its source. Excess over each group's own 2018–19 pace (`G_excess_path.csv`, pp of core, 12m) went from 0.84 (Mar 2025) to 1.50 (Oct est.). The untagged background fell 0.76 → 0.35 while energy, tariffs and AI each built to ~0.35–0.41. Tariffs were mostly in place by Feb 2026; since the oil shock, energy and AI each added ~0.2. **Line:** "Inflation was already broad before the oil shock, from leftover pressure across the basket. Over the past year and a half that leftover has roughly halved, while tariffs, energy and AI have each built up to about four-tenths of a point on top." Energy's 12m rate (3.14 → 3.92 → 4.30%) is the verbal example. | Locked (line wording to be finalised in the script) |
| S2-E2 | Quote breadth **levels vs 2018–19**, not Sep→Oct changes (3% knife-edge). | Locked |
| S2-E3 | Say the hospital **base-effect** line, then use breadth **excluding hospitals** throughout. Disclose it up front, justify it on measurement grounds (one PPI series; Medicare's administrative October reset) and apply it to the whole history. Core ex hospitals 12m: 38.6 (2018–19) → 57.9 (Feb) → 56.9 (Sep) → 59.2 (Oct est.). | Locked |
| S2-E4 | Attribution: carry forward **method d** (excess over each group's own 2018–19 pace; about a quarter each at 12m, close to Bowman). No shares on the slide. Caveats: 12m only; sensitive to baseline year and energy cutoff; energy's piece is mostly travel services; AI's is mostly software, whose 3m annualized rate is now −9.1% (AI group as a whole about +1.0%). | Locked; audit pending |
| S2-E5 | One on the slide, the other verbal: group **inflation rates** on the slide; within-group breadth as a verbal cue. | Locked (which one goes where is confirmed at structure stage) |
| S2-E6 | Stage 1 m/m cooled (2.23 → 0.55) mostly because of energy (~83% of the slowdown); core goods inputs accelerated. Use **y/y 14.1% (SA; BLS headline NSA 13.9%), highest since Jun 2022**, not "record level". Energy pass-through is partial (side-chat analysis E, unverified: about half plausibly energy-linked, with petrochemicals close to direct energy). November PPI is the test. | Locked; E pending verification |
| S2-E7 | Don't name Waller; quote our own **supercore ex hospitals**: 30.5 (2018–19) → 63.6 (Feb) → 63.5 (Sep) → 64.2 (Oct est.). Be ready for "Waller said 70%": he measured a different set of items. | Locked |
| S2-E8 | Keep leaf 187 (nursing homes) as energy; show the alternative as a sensitivity. | Locked |
| S2-E9 | Supercore (ex hospitals) is the main breadth measure. **Trimmed mean = Q&A backup on 2B** (Oct est. 2.38%; one-shot 12m trim 2.95%). **NY Fed MCT → slide 3A.** | Locked (Nov 15) |
| S2-E10 | Add PPI core final demand (WPSFD49116) to the PPI tab as data (backup, not on the slide). | Locked; done in workbook |
| J01 | S2-E1 line carries the qualifier: "...each built up to about four-tenths of a point **above its pre-pandemic pace**." Never call method d a replication of Bowman. | Locked (Nov 15) |
| Structure | Slide 2 splits into **2A (drivers)** and **2B (breadth)**, two quick slides (`slide2_inventory.md`). | Locked (Nov 15) |
| Housekeeping | Roadmap wording (Bowman framing, Waller basis, headline), PPI stage labels in the roadmap, and the slide 1 history line (now leaf 35.2 / 39.2 / 79.7). | Done Nov 15 |
