# Slide 2 hostile-judge Q&A prep (Agent D, Nov 15, 2026)

Status: Round 1, NOT AUDITED. Data only; no policy recommendation. Every spoken answer is a **draft, PENDING Eli**.

**Conventions.** Breadth = share of start-of-window spending weight with annualized rate > 3%, weighted leaf (149 core leaves). Sep 2026 = BEA published (vintage 2026-11-10). Oct 2026 = UMD estimate ("est."). Official Oct PCE comes out Nov 25, after the finals (STATE.md), so the estimate is what we defend on Nov 20.

**Tags.** [O] = opened by me in this run (file or script output). [A]/[B]/[C] = taken from that agent's coordinator-verified report or output. Where I cite a file, it is in `10_slide2_research/outputs/` unless a path is given.

**New D computations** (scripts in `code/`, all rerun from the project root with `python3 -I`, each asserting the slide 1 reproduction: core leaf 12m 60.626 / 54.038, 3m 44.814 / 45.467):

| Script | Output | Content |
|---|---|---|
| `D_threshold_sensitivity.py` | `D_threshold_sensitivity.csv`, `D_threshold_ts.csv`, `D_distribution.csv` | Breadth at cutoffs of 2, 2.5, 3, 3.5 and 4%; weighted percentiles |
| `D_band_and_exclusions.py` | `D_band_summary.csv`, `D_band_leaves.csv`, `D_exclusions.csv` | Weight near the 3% line; breadth ex OER / ex hospitals |
| `D_trimmed_reconcile.py` | `D_trimmed_reconcile.csv`, `D_trimmed_monthly.csv`, `D_trimmed_above3_fate.csv` | Dallas trimmed mean replication and reconciliation |
| `D_preshock.py` | `D_preshock.csv` | Sep 2025 and Feb 2026 (pre-shock) baselines by tag group |
| `D_tag_variants.py` | `D_tag_variants.csv` | Energy group leave-one-out variants |
| `D_hospital_ts.py` | `D_hospital_oer_ts.csv`, `D_hospital_oer_summary.csv` | Monthly hospital and OER contributions, 2018 to Oct 2026 |
| `D_hospital_flip.py` | `D_hospital_flip.csv` | What it would take for the hospitals to stay above 3% |
| `D_headline_mechanics.py` | `D_headline_mechanics.csv`, `D_noncore_leaf_rates.csv` | Headline breadth split into core, food and energy |

---

## Read this first: three attacks that the current slide framing does not survive as written

1. **Breadth did not widen after the oil shock started (attack 10).** Core 12m breadth was 58.8% in Sep 2025 and 52.9% in Feb 2026, the last month before Brent jumped ($70.9 → $103.1, monthly average). Within the energy-tagged group, 12m breadth was 71.3% in Feb, 67.0% in Sep and 73.3% in Oct est. Untagged ex hospitals was 57.9 → 57.9 → 57.8. What did change is **intensity**: the energy group's mean 12m rate went 3.14 → 3.92 → 4.30%. `D_preshock.csv`, `D_tag_variants.csv` [O]
2. **Core 12m breadth is a knife-edge at 3% (attack 2).** In Sep, 35.4% of core weight had 12m rates between 3.0 and 3.5%. OER alone is 13.1%, and the hospitals are another 8.7%. At a 3.5% cutoff, Sep breadth is 25.2%, not 60.6%. The Sep → Oct change is −6.6 pp at 3%, but **+5.8 pp at 3.5% and +2.0 pp at 2%**. `D_band_summary.csv`, `D_threshold_sensitivity.csv` [O]
3. **Bowman herself says pressures "may be broadening"** (Nov 10 speech, para 4 [O]). A slide that sets "concentrated fits Bowman" against "spreading fits Waller/Daly" misstates her. She says pressures *had been* concentrated and may now be broadening, while still expecting them to fade (attack 15).

---

## 1. "Your tags are arbitrary."

**Judge:** "You've labelled 18% of core 'energy-exposed' with a top-quartile cutoff. Restaurants are almost a third of that group, and nursing homes sit right on the line. Why should I believe the split isn't just a choice?"

**Strongest contrary reading.** The cutoff is a choice: decisions.md itself says "results are sensitive to the cutoff because many items bunch between 4% and 5%". The group is dominated by one leaf. Restaurants are 5.74% of core weight, 31% of the group [A]. Nursing homes are +0.001 pp over the cutoff [A]. Tariff exposure is measured by import share, although the reciprocal tariffs were struck down on Feb 20, 2026 [A, SCOTUS syllabus opened by A]. So "energy-exposed" may just mean "labour-intensive services with some energy input".

**Data.**
- Leave-one-out, 12m within-group breadth Feb 2026 / Sep / Oct est. (`D_tag_variants.csv` [O]):

  | Energy group variant | Feb 2026 | Sep 2026 | Oct est. | Mean 12m rate, Feb → Oct est. |
  |---|---|---|---|---|
  | Final | 71.3 | 67.0 | 73.3 | 3.14 → 4.30 |
  | Ex restaurants (241) | 58.3 | 51.7 | 61.1 | 2.82 → 4.54 |
  | Ex nursing homes (187) | 68.9 | 64.1 | 71.0 | |
  | Ex both | 52.9 | 45.3 | 56.0 | |
  | Strict 5% (16 leaves, 3.5% of core) | 59.5 | 59.2 | 59.5 | 3.30 → 7.70 |

- Under every variant, the energy group's **mean rate** rises from Feb to Oct, while its breadth does not rise consistently.
- Energy share of above-target core (method a, 12m Sep): 29.2% final, 15.7% strict 5%, 28.8% transport quartile (`A_q3_sensitivity.csv`, `A_q2_attribution.csv`) [A].
- The I-O recomputation reproduces all 149 energy shares to 5e-6, and no leaf changes side [A]. This verifies the arithmetic, not the design.
- Tariffs (from A's primary-source review): IEEPA reciprocal tariffs were struck down Feb 20, 2026; Section 122 at 10% ran Feb 24–Jul 24; Section 301 at 10–12.5% from Jul 24 (FR 2026-15181). PCs and phones are exempt under all three [A]. Import share therefore remains an exposure proxy for tariffs that still apply, under different authorities.

**What would change our view.** If the energy-minus-untagged gap in **mean rate** vanished under the strict 5% tag, the tag story would be fragile. It does not: strict-5% energy 12m mean is 7.25% in Sep, against 2.91% for untagged under the final scheme [O]. Untagged under the strict scheme was not computed.

**Spoken (draft).** "The tags are an exposure measure from the BEA input-output tables, not a claim about cause. We show the strict 5% cutoff alongside the top quartile. Under both, energy-exposed items are running hotter, about 4 to 7% over 12 months against under 3% for everything else. Neither version shows the share above 3% climbing much since February."

---

## 2. "Why 3%?"

**Judge:** "Why is 3% the line? Why not 2%, the target? And how much does your story depend on it?"

**Strongest contrary reading.** 3% is the cutoff that **maximises the gap to 2018–19** for core 12m: +25.4 pp, against +15.7 at 2%, +23.0 at 2.5%, +11.0 at 3.5% and +11.2 at 4% (`D_threshold_sensitivity.csv` [O]). It also sits where a third of core weight bunches. The sign of the Sep → Oct change flips with the cutoff.

**Data** (core, weighted leaf; Sep / Oct est. / 2018–19 average; `D_threshold_sensitivity.csv` [O]):

| Cutoff | 12m Sep | 12m Oct est. | 12m 2018–19 | 3m Sep | 3m Oct est. | 3m 2018–19 |
|---|---|---|---|---|---|---|
| 2.0% | 71.9 | 73.9 | 56.1 | 72.1 | 68.3 | 57.1 |
| 2.5% | 70.0 | 69.5 | 47.0 | 54.4 | 68.2 | 47.9 |
| **3.0%** | **60.6** | **54.0** | **35.2** | **44.8** | **45.5** | **39.2** |
| 3.5% | 25.2 | 31.0 | 14.2 | 24.8 | 31.8 | 24.3 |
| 4.0% | 19.3 | 21.8 | 8.1 | 21.4 | 30.9 | 16.3 |

- Bunching, Sep 12m: 35.4% of core weight sits in (3.0, 3.5]. That is 19 leaves: OER 13.1% at 3.26%, the three hospital leaves 8.7% at 3.34%, restaurants 5.7% at 3.47%, paramedical 3.6% at 3.35%. In Oct est. the band holds 23.0% (`D_band_summary.csv`, `D_band_leaves.csv` [O]).
- Distribution measure (weighted percentiles of 12m core leaf rates, `D_distribution.csv` [O]):

  | Percentile | Sep | Oct est. | 2018–19 |
  |---|---|---|---|
  | Median | 3.26 | 3.26 | 2.33 |
  | p75 | 3.72 | 3.78 | 3.31 |
  | p90 | 6.43 | 6.51 | 3.87 |

- At 12m the elevation against 2018–19 holds at **every** cutoff from 2 to 4%: +11 to +25 pp.
- Why 3% (provenance): it is Waller's line ("12-month increases above 3 percent", speech [O]), so our number is comparable to his. Eli fixed it as a binding method decision before this run (GO.md).

**What would change our view.** If the 2018–19 gap shrank toward zero at higher cutoffs, the "elevated breadth" claim would only be a 3% artefact. It doesn't: +11 pp at 4%. The Sep → Oct *direction* is not robust, so we should not claim narrowing or widening from it.

**Spoken (draft).** "3% is Waller's line, so we can compare with him. The level result doesn't depend on it: at any cutoff from 2 to 4%, breadth is 11 to 25 points above 2018–19, and the weighted median item is running 3.3% against 2.3% then. The month-to-month change does depend on it, because a third of core spending sits between 3 and 3.5%. So we don't read anything into one month's move."

---

## 3. "Breadth fell 6.6 points in October. Isn't that disinflation?"

**Judge:** "Your own number says the share above 3% dropped from 61 to 54. Isn't inflation narrowing? And isn't 'base effect' an excuse? Seasonal adjustment should remove an October pattern."

**Strongest contrary reading.**
- The October hospital jump recurs every year, so it is partly calendar regularity. BEA's SA series still shows October bumps in 2017, 2019, 2023 and 2025 (0.72–0.89%) [B].
- The Oct 2026 hospital figure is a UMD estimate, built from a preliminary PPI that we seasonally adjust ourselves.
- And maybe it is real narrowing: hospital inflation genuinely slowed.

**Data.**
- −6.59 pp total. The hospital leaves 184–186 contribute −8.72; untagged ex hospitals −0.08; energy +1.16; tariff +1.04 (`A_q3_oct12m_drop_by_tag.csv`) [A].
- Ex hospitals, core 12m breadth rises 56.86 → 59.24 [B]. Ex hospitals and OER: 49.65 → 52.43 (`D_exclusions.csv`, `D_hospital_oer_summary.csv` [O]).
- Measured, not filled: PPI hospitals Oct 2025 +1.42% NSA at first release (Jan 14, 2026), with normal response rates. The driver was the Medicare inpatient reset, +5.96%, the largest October in the series (2016–24 Octobers +0.8 to +4.3%) [B].
- Why SA doesn't remove it: SA removes the *average* October reset. The implied October seasonal gap (NSA PPI minus BEA SA) averaged 0.37 pp over 2017–25. The 2025 excess (+1.41% NSA vs a 0.72% October mean) stays in the SA series as 0.89% (`B_q7_hospital_octobers.csv` [B]; `D_hospital_flip.csv` [O]). A larger-than-usual reset is an irregular, not a seasonal.
- Hospitals sit on the line: their 12m rate was 2.95% in Feb, 3.1–3.4% in Mar–Sep and 2.74% in Oct est. They add or remove 8.7 pp each time they cross (`D_hospital_oer_ts.csv` [O]).
- **Estimate risk** (`D_hospital_flip.csv` [O]):
  - UMD used an SA m/m of 0.305%, from the PPI prelim of +0.677% NSA less a 0.372 seasonal adjustment.
  - Staying above 3% needs 0.564% SA, which is 0.936% NSA at our adjustment, an upward revision of +0.26 pp.
  - In 22 months of PCU622622 first-print revisions (Dec 2024–Sep 2026), 1 was that large (+0.44, Mar 2025). Mean absolute revision is 0.09 pp; the largest downward revision was −0.40.
  - At current NSA, a flip also needs a seasonal gap ≤ 0.113 pp; the smallest in 2017–25 was 0.241. **0 of 9 Octobers** would flip it.

**What would change our view.** A revised Oct 2026 PPI hospitals ≥ ~0.94% NSA, or BEA applying an October seasonal factor under ~0.11 pp. Either would restore ~8.8 pp and turn the "drop" into a rise. Next check: the Nov PPI release (revises Oct) and BEA's Oct PCE on Nov 25.

**Spoken (draft).** "All of the drop, and more, is three hospital lines. Hospital prices jumped in October 2025 on an unusually large Medicare reset, and that month just left the 12-month window. Take those lines out and breadth rose slightly. Seasonal adjustment only removes a normal October; last year's reset was double the usual size."

---

## 4. "Bowman says a quarter each. How do you get her number?"

**Judge:** "Governor Bowman attributes roughly a quarter each to tariffs, energy, AI and persistence. Does your decomposition agree, and if not, who's right?"

**Strongest contrary reading.** Our attribution is a black box of our own. How the 2% target is allocated moves energy's share from 23% to 60% (12m Sep), and no method reproduces a quarter each [A]. Bowman's method is undisclosed; her five footnotes give none [A]. Her fourth quarter is a *cause* (persistence), not a set of items.

**Data.**
- Shares of above-target core, 12m Sep (energy / tariff / AI / untagged; `A_q2_attribution.csv`) [A]:

  | Method | Energy | Tariff | AI | Untagged |
  |---|---|---|---|---|
  | (a) own-weight 2% | 29.2 | −0.1 | 18.0 | 52.9 |
  | (b) excess over 2% only | 23.0 | 7.9 | 13.0 | 56.1 |
  | (c) 2% charged to untagged | 59.8 | 18.6 | 21.3 | 0.4 |

- Tariff group 12m rate is 1.99% in Sep, below target. It was 2.86% in Feb (`D_preshock.csv` [O]). New light trucks (1.9% of core) ran at 0.5% [A].
- The AI group is 2.0% of core weight; software (leaf 50) is 88% of its contribution [A].
- 3m leaf-sum residual is 0.2–0.27 pp, mostly annualization convexity [A].
- Bowman's exact words [O, saved RTF]: "Tariffs, energy, and AI-related price pressures each accounted for roughly one-fourth of above-target core PCE inflation over the 12 months ending in September."

**What would change our view.** Publication of her method or staff memo. Within our data, a tariff group rate well above 2% would be needed for tariffs to carry a quarter under (a) or (b).

**Spoken (draft).** "We can't reproduce a quarter each, and we say so. Her method isn't published, and ours swings with how you assign the 2% target. One thing holds under every allocation: the tariff-exposed items we can identify are running at about 2% over 12 months, so they aren't carrying a quarter of the overshoot in our data."

---

## 5. "October is too early to see indirect effects."

**Judge:** "The shock hit in March. The literature says pass-through takes quarters. Why read anything from October? And oil just fell 30%."

**Strongest contrary reading.**
- The FEDS note's core effect builds over about 8 quarters [C]. October is month 7 of the shock (Brent monthly average $70.9 Feb → $103.1 Mar; `C_q8_oil_daily.csv`).
- Oct PPI was priced on Oct 13 (Brent $125.78), before the Nov 4 drop to $91.84 [C]. So October can't show the reversal, and it can't show the full indirect effect either.
- Breadth figures may be catching the first round only.

**Data.**
- Upstream, Oct m/m SA (`C_q8_ppi_stages_summary.csv`) [C]:
  - Stage 1 (WPSID51): +0.55; 3m annualized +18.9; y/y +14.1; record level.
  - Stage 2 (WPSID52): −0.21; 3m +16.4.
- Energy contribution in Oct: −0.25 pp (stage 1), −0.98 pp (stage 2). Services inputs rose +0.9% and +0.7%. Stage 1 transport and warehousing for goods producers: 3m annualized +39.9% [C].
- Oil note: pass-through 0.001 → 0.014 (sum of oil coefficients); a permanent 10% rise lifts the core level 0.35% after 12 quarters post-pandemic vs 0.05% pre-pandemic. The paths are "an upper bound", and US results appear only in fn 4 [C].

**What would change our view.** Nov PPI stages 1–2 (December release, the first one priced after the oil drop):
- energy contributions stay negative and services and transport inputs also roll over: reads as first round fading;
- services and transport inputs keep rising with energy down: reads as indirect effects building.

**Spoken (draft).** "Agreed, October can't settle it, and we don't claim it does. What it shows is the first round still lengthening: stage 1 producer prices are at a record, and the energy part turned negative in October while transport and services inputs kept rising. November PPI, the first priced after the oil drop, is the test."

---

## 6. "Airfares are demand, not pass-through."

**Judge:** "Airfares are up 20% because people are flying, not because of jet fuel. Why count them as energy spread?"

**Strongest contrary reading** (C's own evidence against, `C_q11_confirming_items.md`) [C]:
- Fares rose 8.0% Dec 2025–Feb 2026, before the March oil spike.
- The cumulative ratio of fares to jet fuel since Feb is about 0.16 (+15.8% vs +97%).
- Fares didn't retrace when jet fuel fell in Jun–Jul.
- PPI airline services fell 1.2% SA in Oct (+4.3% NSA).
- No passenger-demand series was pulled.

**Data** [C]:
- CPI airline fares: Oct SA +0.4% m/m, 3m annualized +18.3%; Sep y/y +22.4%.
- PCE air transportation: Sep +20.5% y/y; 12m Sep 20.5%, Oct est. 16.8% (engine, [O]).
- CPI fares vs PPI jet fuel monthly r = 0.42 at lag 0 and 0.39 at lag 1, about 16% of variance.
- Air transportation is 1.2% of core and energy-tagged (energy share 11.3%) [A].

**What would change our view.** A passenger-volume or load-factor series rising strongly through 2026 would support demand. Fares falling with jet fuel after the Nov drop would support pass-through.

**Spoken (draft).** "We treat airfares as an energy-intensive item, not as clean second-round evidence. The fuel link is real but weak, about a 0.4 correlation, and fares were rising before the spike, and other explanations, including demand, remain untested. Trucking is consistent with delayed fuel pass-through (truck freight, NSA, +3.9% in October while SA diesel fell 7.9%), but demand and other costs have not been separated."

---

## 7. "Isn't the AI story just the energy story? Data centers burn electricity."

**Judge:** "Data-center power demand is raising electricity prices. Electricity is excluded from core. So how do you separate AI from energy?"

**Strongest contrary reading.** Our tags can't separate them.
- The energy tag's I-O energy block includes electric power (221100) and the federal and state/local electric utilities (S00101, S00202) as well as oil and gas (`08_shock_tagging/code/tag_exposures.py` line 75 [O]). Any AI-driven rise in electricity costs that feeds core items is booked as **energy**.
- The AI tag is four goods leaves, and software is 88% of its contribution [A]. It misses AI's indirect cost effects entirely.

**Data** (engine [O]):
- PCE electricity (line 170, outside core): 12m 4.37% Sep, 4.16% Oct est.; 3m 0.67% Sep, 3.97% Oct est.
- For comparison, gasoline: 12m 34.96% Sep, 37.75% Oct est.
- AI leaves, 12m Sep: PCs 9.70% (3m 40.5%); software 18.48% (3m 0.39%, Oct est. 3m −9.14%); leaves 51 and 71 both −12.67%.
- AI group: 2.0% of weight; 12m within-breadth 90%, 3m 28% [A].

**What would change our view.** An I-O split of the energy share into electricity vs petroleum for the energy-tagged leaves. Not computed; it needs `tag_exposures.py` rerun by commodity. If electricity is a large part of the restaurant/hotel energy share, part of "energy" is AI-adjacent.

**Spoken (draft).** "The tags measure direct exposure, so AI's effect through electricity shows up under energy, and we flag that. But electricity is up about 4% over the year against 35% for gasoline. The energy-exposed signal is mostly oil, and the AI group is essentially computers and software."

---

## 8. "Headline breadth must be higher in an energy shock. Why show core?"

**Judge:** "Of course breadth rises when oil goes up; every energy item is above 3%. Isn't that mechanical?"

**Strongest contrary reading** (against our own backup line): the "headline rises mechanically" claim is **not borne out**. Headline 12m breadth is *below* core in Sep (59.8 vs 60.6) and about equal in Oct est. (54.0 vs 54.0) [B]. Food items, mostly below 3%, offset energy.

**Data** (`D_headline_mechanics.csv` [O]):
- Sep 12m: energy leaves are 3.6% of headline weight, 99% of them above 3%, contributing +3.6 pp. Food is 7.3% of weight, 30% above 3%, contributing +2.2 pp. Core contributes 54.0 pp.
- 3m Oct est.: energy 3.9% of weight, 91% above 3%; headline 46.3 vs core 45.5.

**What would change our view.** n/a (a measurement fact). The reason to show core is the usual one: it is the persistence-relevant set. It is not that headline is inflated.

**Spoken (draft).** "Energy items are only about 4% of spending, and food mostly runs below 3%, so headline and core breadth are almost identical. We show core because it's the set that tells us about persistence."

**Flag for the coordinator:** the roadmap/backup wording "headline breadth rises mechanically in an energy shock" should be softened. In our data the mechanical lift is about +3.6 pp from energy, offset by food.

---

## 9. "Your 3-month breadth is just OER bouncing around 3%."

**Judge:** "Core 3-month breadth went from 66% in May to 33% in August to 45% in September. That's noise. Which reading do you believe?"

**Strongest contrary reading.** Correct: OER is about 13% of core and its 3m rate sits at the line. It ran 4.51 → 4.34 → 3.22 → 2.80 → 3.22 → 3.43, May–Oct est. [B]. In Aug OER fell below 3% and removed 13 pp; in Sep it added 12.9 pp back (`D_hospital_oer_ts.csv` [O]).

**Data.** Core 3m ex hospitals and OER (renormalised): Feb 55.6, Sep 40.8, Oct est. 41.6; 2018–19 average 34.6 (`D_hospital_oer_summary.csv` [O]). Ex OER alone, 3m: 36.6 Sep, 37.4 Oct est. (`D_exclusions.csv` [O]).

**What would change our view.** 3m breadth ex OER and hospitals rising above ~50 would be a genuine broadening signal, independent of the two threshold-sitters.

**Spoken (draft).** "Yes, the 3-month number is noisy because owners' equivalent rent sits right at 3%. Excluding it and hospitals, 3-month breadth is about 41%, against 35% in 2018–19. That's elevated, but not rising."

---

## 10. "Breadth was already this high before the war." (likely; not in the brief's list)

**Judge:** "Sixty percent above 3% sounds alarming, but what was it a year ago, before oil spiked? If it was the same, what does this have to do with the energy shock?"

**Strongest contrary reading.** Breadth reflects the inflation regime already in place in 2025, not the energy shock. Energy-exposed items were already broad before March.

**Data** (`D_preshock.csv`, `D_hospital_oer_summary.csv`, `D_tag_variants.csv` [O]):

| 12m breadth > 3% | Sep 2025 | Feb 2026 (pre-shock) | Sep 2026 | Oct 2026 est. |
|---|---|---|---|---|
| Core | 58.8 | 52.9 | 60.6 | 54.0 |
| Core ex hospitals & OER (renormalised) | 47.5 | 50.8 | 49.7 | 52.4 |
| Energy-tagged | 72.3 | 71.3 | 67.0 | 73.3 |
| Untagged ex hospitals | n/a | 57.9 | 57.9 | 57.8 |
| Core goods | 22.5 | 32.7 | 29.1 | 36.4 |
| Supercore | 61.6 | 54.0 | 69.0 | 54.5 |

| 12m weighted mean rate | Sep 2025 | Feb 2026 | Sep 2026 | Oct 2026 est. |
|---|---|---|---|---|
| Energy-tagged | 3.23 | 3.14 | 3.92 | 4.30 |
| Untagged | 3.26 | 3.00 | 2.91 | 2.90 |
| Core (weighted mean of leaf rates, not chained) | 2.86 | 2.98 | 3.18 | 3.30 |

- Against 2018–19, everything is elevated: core 35.2, ex hospitals & OER 28.9.

**What would change our view.** Untagged ex-hospital 12m breadth rising clearly above its flat ~58% would be spread. It has been flat since Feb.

**Spoken (draft).** "Breadth was already high before the shock; that's the 2025 inflation we inherited. What the energy shock changed is how hot the exposed items run: their average 12-month rate went from about 3.1 to 4.3%, while everything else stayed under 3%. So far it's a bigger first round, not a wider one."

---

## 11. "Sixty percent above 3%, but the trimmed mean is 2.3%. Which is right?" (GO Q4b; not answered in B's report)

**Judge:** "The Dallas trimmed mean is 2.3%. You say 60% of core is above 3%. Those can't both describe the same economy."

**Strongest contrary reading.** The trimmed mean is designed to strip out exactly the items breadth counts, so 2.3% is the truer trend and breadth overstates.

**Data** (`D_trimmed_reconcile.csv`, `D_trimmed_above3_fate.csv` [O]):
- UMD replication of the Dallas method (177 headline leaves, monthly 24%/31% trim, previous-month weights) reproduces the published Sep 2026 figures:

  | Horizon | UMD replication | Dallas published |
  |---|---|---|
  | 1m annualized | 2.848 | 2.84 |
  | 6m | 2.427 | 2.42 |
  | 12m | 2.265 | 2.26 |

  Oct est. 12m: 2.38.
- Trimming the **12m** leaf rates once (same 24/31) gives 2.95% (headline) and 2.98% (core) in Sep. So about 0.7 pp of the gap comes from trimming **monthly** changes, not from breadth vs centre.
- Mechanism: for core leaves above 3% at 12m, 33% of their weighted leaf-months were cut from the top, against 12% from the bottom. Their average m/m annualized is 4.80% over all months but 2.65% over the months the trim kept.
- Supports Logan [O, saved speech]: the change in the mix of increases and decreases "is causing the trimmed mean to drop too many increases right now."
- Trend: Dallas-method 12m fell 2.76 (Sep 2025) → 2.27 (Sep 2026), while core 12m breadth rose 58.8 → 60.6 (`D_trimmed_monthly.csv` [O]).

**What would change our view.** If the 12m-rate trim also came out near 2.3%, the two would genuinely disagree. It comes out near 3%.

**Spoken (draft).** "They measure different things. The trimmed mean drops the top 31% of *monthly* changes. Items running above 3% get their big months cut a third of the time, so over the months it keeps they look like 2.6%, not 4.8%. Trim the 12-month rates instead and you get about 3%. That's the bias Logan's staff point to."

---

## 12. "Waller said 70% of components. You get 63% on a count."

**Judge:** "Waller says 'more than 70 percent of the components'. Components sounds like a count. Your count is 63%."

**Strongest contrary reading.** Our ">70%" match uses a weighted basis Waller didn't state. Our count basis (63.1 leaf, 58.6 sub-line) doesn't reproduce him. Roadmap text says "on his basis (core services, count of items)", which contradicts the result.

**Data** (`B_q6_waller.csv`) [B]:
- Core services 12m, Sep: weighted leaf 70.8; weighted Sep-2026 shares 71.1; count leaf 63.1 (53 of 84); count sub-line 58.6.
- Oct est.: weighted 59.7, the fall coming from hospitals.
- Quote [O]: "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September."

**What would change our view.** If his staff's basis turned out to be a finer count (e.g. Dallas-style ~178 components, services subset), our comparison would need that basis. Unverified.

**Spoken (draft).** "We reproduce his 70% only on a spending-weighted basis, 70.8%. A simple count gives 63%. His basis isn't stated, so we show ours and label it."

---

## 13. "Sticky vs flexible: what does it show?"

**Judge:** "If this is spreading, it should show up in sticky prices. Does it?"

**Strongest contrary reading.** Our mapping covers 61% of core. Flexible is 9% of weight. The classification is Bryan–Meyer (2010), not confirmed to be the current Atlanta basket [B].

**Data** [B]:
- PCE sticky 12m: 60.3 → 62.8 Sep → Oct est. (it excludes the hospitals, which is why it rises).
- Atlanta-style CPI basket sticky 12m: 66.1 → 67.9 (Oct approx.).
- 3m sticky swings ~40 pp month to month (OER).

**What would change our view.** n/a. B rates it 2/5 and it is backup only.

**Spoken (draft).** "On the sticky-price basket, about two-thirds of spending is above 3% and it ticked up in October. But our mapping covers only 60% of core, so we treat it as a cross-check."

---

## 14. "Which PPI series is 'stage 2'?" (label trap)

**Judge:** "You cite unprocessed intermediate goods up 40% annualized. Is that stage 2?"

**Strongest contrary reading.** Our earlier notes read ID62 as stage 2. It is "unprocessed goods by commodity type". The stages are WPSID51–54 [C, verified against the BLS catalogue]. The Nov 10 "+41.5%" is stale: revised to +31.0% (Sep 3m), and Oct reversed −3.1% m/m [C].

**Data.** WPSID52 stage 2: Oct −0.21% m/m, 3m +16.4%, y/y +13.2%. ID62: Oct −3.08% m/m, 3m +16.8% [C].

**Spoken (draft).** "Stage 2 is WPSID52, up 16% annualized over three months and slightly down in October. The unprocessed-goods series is separate and more energy-heavy; it spiked in September and fell 3% in October."

---

## 15. "Bowman says broadening too. Isn't your Bowman-vs-Waller framing a straw man?"

**Judge:** "You set Bowman up as 'it's concentrated'. She said pressures 'may be broadening'."

**Strongest contrary reading.** The disagreement isn't concentrated vs broad; it's whether broadening persists. Bowman [O]: "Price pressures had been concentrated in a few categories, but the latest data suggest that these pressures may be broadening." She still forecasts core "closer to 2 percent next year" as shocks "wane or unwind."

**Data.** Use #10. Breadth is flat since Feb at 12m; intensity is up in exposed items. That fits "relative price shocks in specific sectors" (her words [O]) at least as well as spread.

**Spoken (draft).** "Fair: both governors see some broadening. Where they differ is whether it lasts, which is slide 3A's question. Our breadth data say the shock has made exposed items hotter but hasn't yet widened the share above 3%."

---

## 16. "How did you get October?" (Pace-style provenance question)

**Judge:** "October PCE isn't out. Where do your October numbers come from, and how wrong could they be?"

**Data.**
- UMD October build: BEA's Sep index extended by line-level October m/m from the Oct CPI and the Oct PPI (released Nov 13).
- 17 lines (18.7% of PCE) need our own seasonal adjustment; hospitals are 7.85% (`04_oct_pce_build/report.md`) [2, coordinator report].
- Core 0.295 m/m, 3.24% y/y, against Bowman's 3.3% [O speech] and Goldman within 2–3bp (STATE.md [2]).
- Carried-forward lines contribute −0.003 pp to the breadth drop (slide 1 R6) [2].
- The hospitals decide the 12m breadth result; see attack 3 for the flip test.

**Spoken (draft).** "We built October line by line from the October CPI and PPI, the way BEA does, and labelled it as an estimate. Our core is 3.24% y/y, close to Governor Bowman's 3.3% and to bank estimates. The one line that matters for breadth is hospitals: it would take a revision more than twice the usual size to change the result."

---

## Ranking of attack severity (D's judgment, for coordinator)
- **Most damaging:** #10 (pre-shock baseline), #2 (knife-edge), #15 (Bowman framing).
- **Well defended:** #3, #11 and #8, now that the data are in hand.
- **Fragile:** #4 (Bowman attribution) and #12 (Waller basis).


> Coordinator note (Codex R1-F03): spoken answer on airfares/freight qualified; correlations are not causal estimates.
