# Slide 2 (2A + 2B): inventory of slide-worthy material (v2, Nov 15, 2026)

Everything strong and relevant enough to appear on slides 2A/2B or in their verbal script/Q&A. Inclusion here is not a decision; Eli chooses at the structure stage.

**Structure (Eli, Nov 15):** 2A = what's driving inflation (October category drivers plus the own-baseline attribution); 2B = breadth. Two quick, condensed slides.

**Audit status:** `slide2_research` converged R3. `slide2_followups` (analyses E, F, G, H, I) ran three Codex rounds (`06_Audits/slide2_followups/`). The two R3 Blocking items (dates and baskets mixed in the transfer to this inventory) were fixed after the round cap. The fixed figures come from `code/I_exhosp_distribution.py` and match Codex's independent calculation exactly; there was no fourth Codex round. **Backup figures marked "including hospitals" are September values, an exception to the convention.**

**Conventions:** Oct 2026 = UMD estimate ("est."). "Excess" = contribution above each category's or group's own 2018–19 pace, measured relative to normal, **not** core minus 2%. Breadth = share of spending weight with inflation > 3%, weighted leaf, start-of-window weights, **hospitals excluded** (S2-E3). Locked decisions: `FINAL.md` §7.

---

## 2A. What's driving it

### 2A-1. Core drivers by BEA category, Oct 2026 est. (the round-1 exhibit, updated)
Excess contribution vs 2018–19, pp of core 12m inflation (`outputs/H_oct_drivers_categories.csv`). Core 12m 3.24% (est.); **total excess 1.47 pp** (Sep 1.35).

| Category (share of core) | 12m rate Oct est. | Excess Sep | **Excess Oct est.** | Main drivers inside (leaf excess; shock tag) |
|---|---|---|---|---|
| Recreational goods & vehicles (3.8%) | 8.2 | 0.44 | **0.43** | software +0.26, PCs +0.09 (AI) |
| Transportation services (3.9%) | 8.8 | 0.27 | **0.25** | airfares +0.15, taxis +0.04 (energy); auto repair +0.05 |
| Health care (19.4%) | 2.7 | 0.23 | **0.18** | paramedical +0.08, dental +0.04. Hospitals (all 3) fell 0.096 → 0.044, the base effect |
| Other services (9.2%) | 3.0 | 0.14 | **0.14** | communication +0.05, personal care +0.03 |
| Clothing & footwear (3.0%) | 3.0 | 0.10 | **0.11** | women's clothing, shoes, men's clothing (all tariff-tagged) |
| Food services & accommodation (8.1%) | 3.9 | 0.08 | **0.11** | restaurants +0.05, hotels +0.03 (energy-tagged) |
| Other nondurables (9.2%) | 1.4 | 0.01 | 0.09 | games/toys +0.13 (tariff), newspapers +0.08: two small leaves |
| **Housing (17.6%)** | 3.3 | −0.02 | **0.00** | essentially no excess vs 2018–19, though it is ~18% of core inflation (+0.58 pp) |

- Checks: September reproduces the pipeline file exactly. The October roll-up gives core m/m 0.295, the same as the build.
- Leaf amounts are diagnostics; they don't sum exactly to the Fisher category totals. Other durables (jewelry) and furnishings (dishes) are also single-small-leaf categories.
- Mapping categories to shocks: recreational goods → **AI**; transportation services and food services/accommodation → **energy-intensive travel**; clothing (and toys) → **tariffs**; health care, other services → **non-shock background**.

### 2A-2. Excess by shock group: the Bowman-type split (own-baseline attribution, method d)
Each group's 12m inflation vs its own 2018–19 pace × its spending share (`outputs/G_excess_path.csv`, `G_baseline_attribution_summary.csv`).

| pp of core | Energy | Tariff | AI | Untagged | Total |
|---|---|---|---|---|---|
| Mar 2025 | −0.01 | 0.03 | 0.06 | 0.76 | 0.84 |
| Sep 2025 | 0.20 | 0.23 | 0.04 | 0.59 | 1.06 |
| Feb 2026 (pre-oil) | 0.18 | 0.44 | 0.14 | 0.42 | 1.18 |
| Sep 2026 | 0.32 | 0.35 | 0.36 | 0.35 | 1.38 |
| **Oct 2026 est.** | **0.39** | **0.41** | **0.35** | **0.35** | **1.50** |

- **Shares, Oct est.:** energy 26 / tariff 28 / AI 23 / untagged 23. Sep: 23 / 25 / 26 / 25. Roughly a quarter each, close to Bowman's "roughly one-fourth each". It is **not a replication of her (undisclosed) method**.
- **Fragility:**
  - It holds at 12m only; at 3m in Oct, energy is 40% and AI 8%.
  - The baseline year matters: with 2018 or 2019 alone as the baseline, untagged runs 13–34%.
  - Under the strict 5% energy cutoff, energy falls to 12.5% (Oct est.).
- **Group rates vs their own norms (12m, Oct est.):** energy 4.30 vs 2.14; tariff 2.61 vs −1.14; AI 12.0 vs −5.8; untagged 2.91 vs 2.40. On 3m, energy is 6.5%.
- **Core excluding all shock-exposed items:** 2.91% (12m), 3.32% (3m), against 3.26% in Sep 2025.
- **Cross-check:** the category total (1.47) and the shock-group total (1.50) agree. The 0.03 gap is a method difference.
- **Locked line (S2-E1)** fits here: "...that leftover has roughly halved, while tariffs, energy and AI have each built up to about four-tenths of a point on top." Qualifier pending (J01).

### 2A-3. Upstream pipeline (2A or 2B; S2-E6)
- **Stage 1 producer input prices +14.1% y/y (SA; BLS NSA 13.9%), the highest since Jun 2022.** Stage 2 +13.2%; final demand +6.5%.
- **Momentum cooled because of energy:** stage 1 m/m went +2.23 → +0.55. Energy's contribution went +1.15 → −0.25 pp, about 83% of the slowdown. Core goods inputs went the other way: +0.20 → +0.53.
- **What kept stage 1 rising in Oct:**
  - petrochemicals +0.27 (oil/gas feedstock);
  - trade margins +0.21;
  - freight +0.13;
  - scrap metals +0.12.

  About half is plausibly energy-linked. This is a heuristic split, not an estimate. The broader computer, industrial-machinery and electrical-equipment groups (115–117) are only 1.4% of stage 1's Dec 2025 weight, so AI-linked inputs are not material there. This is a weight-based exposure check, not a measured AI contribution.
- **Timing:** Brent peaked at $135.51 (Oct 2) and fell to $91.84 (Nov 4). The Oct PPI was priced around Oct 13 ($125.78), before the drop. Nov PPI comes Dec 15, after the finals.

---

## 2B. How wide it is (breadth)

### 2B-1. Breadth levels vs 2018–19, excluding hospitals (S2-E2, E3, E7)

| 12m breadth, % of spending > 3% | 2018–19 | Sep 2025 | Feb 2026 | Sep 2026 | **Oct 2026 est.** | Post-2018 peak |
|---|---|---|---|---|---|---|
| **Core** | 38.6 | 55.0 | 57.9 | 56.9 | **59.2** | 77.7 (Aug 2022) |
| **Supercore** | 30.5 | 54.9 | 63.6 | 63.5 | **64.2** | 70.8 (Nov 2022) |
| Core goods | 12.4 | | | 29.1 | 36.4 | 78.6 (Aug 2022) |

- **3m annualized, Oct est.:** core 49.9 (2018–19: 41.8); supercore 45.7 (32.6).
- **Robust at any cutoff:** at the five tested cutoffs from 2% to 4%, Oct est. core breadth (excluding hospitals) is 15–21 pp above 2018–19. The weighted median item runs 3.32% vs 2.40% (`I_exhosp_distribution.csv`).
- **Chart-ready:** monthly 2018–Oct 2026 in `F_ex_hospital_ts.csv`.

### 2B-2. Hospital base effect (the line that justifies excluding hospitals)
- Hospitals (8.8% of core) account for −8.7 pp of the −6.6 pp Oct drop in 12m core breadth. The cause is October 2025's Medicare inpatient reset: +5.96%, the largest October since 2014. It was **measured, not filled** (published Jan 14, 2026; response rates "within the normal range").
- The same base effect lowers health care's 2A driver: all three hospital leaves together fell 0.096 → 0.044 pp.
- To change the breadth result, Oct 2026 would need a +0.26 pp hospital revision. The mean absolute revision is 0.09; 1 of 22 recent revisions was that large.

### 2B-3. Breadth inside the shock groups (verbal, S2-E5)
- Within-group 12m breadth: energy-exposed 71.3 (Feb) → 73.3 (Oct est.); untagged excluding hospitals flat at 57.9 → 57.8.
- This is the "same width, more heat" point: breadth is roughly flat since Feb while excess rose 1.18 → 1.50 pp.

---

## Verbal or backup (both slides)
- **Confirming items** (correlations, not causal estimates):
  - truck freight (NSA) +3.9% in Oct while diesel (SA) fell 7.9%;
  - CPI transportation services +0.8%, mostly intracity transport and car insurance (airfares only +0.07);
  - food at home +0.44%.
- **Trimmed mean:** our Dallas-method estimate for Oct is 12m 2.38% (Sep 2.26 published, matched to the hundredth). Trimming October's 12m rates once instead gives 2.95% (headline basket, as Dallas) or 2.96% (core). It reads lower than breadth because it cuts the top 31% of *monthly* changes. In Sep, hot core items lost about a third of their months to the top trim.
- **NY Fed Multivariate Core Trend** 2.84 (Sep; cited by Logan). No Oct value before the cutoff. Likely slide 3A.
- **Waller's ">70%":** reproduced only by spending-weighted core services (70.8, Sep, *including* hospitals); a count gives 63.1. Not named (S2-E7).
- **Headline:** 12m breadth 59.8 is below core's 60.6 (Sep, both *including* hospitals), because food offsets energy.
- **3% knife-edge:** 25% of core weight (Oct est., excluding hospitals) sits between 3.0 and 3.5%; 35% in Sep including hospitals. Quote levels, not monthly changes.
- **Sticky/flexible:** backup only (61% coverage).
- **Tags:** the reciprocal tariffs were struck down Feb 20, 2026; the tariff tag is by import share. Nursing homes sit on the energy cutoff (kept).
- **FEDS oil note:** post-pandemic pass-through is significant in the US, Canada and Japan (fn 4).
- **ISM pricing sentiment:** not public; cite only as Waller's reference.

## Open (all settled Nov 15: J01 qualifier added; trimmed mean = 2B Q&A backup; MCT → slide 3A; core final demand added to the PPI tab)
- **J01:** a qualifier on the S2-E1 line, e.g. "...about four-tenths of a point **above its pre-pandemic pace**".
- **S2-E9:** trimmed mean and MCT placement.
- **S2-E10:** add PPI core final demand to the PPI tab.
- **Workbook:** analyses E, F, G and H are not yet in `Slide2_Inflation_Data.xlsx`. That happens at the build stage.
