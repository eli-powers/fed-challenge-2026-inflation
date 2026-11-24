# Proposed replacement: lit summary, De Michelis, Orak, Pradhan & Queralto (2026)

**Status:** proposal from Agent C (Nov 15). The original `lit_summary_DeMichelis_oil.md` is untouched. Every claim below was checked against the saved note (`staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html`); see `C_q10_oil_note_verification.csv` (43 rows; script confirms each quoted string verbatim). Changes from the original are marked **[changed]** or **[added]**.

"The Effect of Oil Prices on Core Inflation: Recent Evidence from the Advanced Economies." FEDS Notes, Nov 9, 2026. https://doi.org/10.17016/2380-7172.4190. A staff note giving the authors' own views; not an official forecast ("do not represent any official forecasts").

## What it does
- **Model.** Backward-looking Phillips curve for core inflation, panel of five economies (US, Canada, euro area, Japan, UK), 2000:Q1-2026:Q2, country fixed effects. Core = core PCE (US) and core CPI (others).
  - Regressors: two lags of core inflation, output gap, NY Fed GSCPI, and the current value plus four lags of quarterly Brent inflation (local currency) measured relative to core. A post-pandemic dummy (2021:Q1 on) is interacted with the persistence terms and the oil terms.
- **Horse race (Table 1, RMSE).** Post-pandemic: 0.37 (no dummies) -> 0.31 (persistence) -> 0.17 (persistence + pass-through). Full sample 2016:Q1-2026:Q2: 0.31 -> 0.24 -> 0.14. The pass-through interaction gives the single largest improvement.
- **Projection.** From Brent futures (early Aug 2026), GSCPI at 1.63 SD in June decaying 0.8 per quarter (fn 8), and 2026:Q1-Q2 core as the starting point.
- **Structural simulation.** A 10% oil price rise in GEMUS (Board staff's open-economy model; see below).

## Key numbers (Table 2 unless noted)
| | Pre-pandemic | Post-pandemic increase | Post-pandemic level |
|---|---|---|---|
| Persistence (sum of two core lags) | 0.347*** [0.225, 0.470] | +0.298*** [0.202, 0.395] | about 0.65 |
| Pass-through (sum of oil coefficients) | 0.001 [-0.002, 0.004], not significant | +0.013** [0.004, 0.021] | 0.014 |
| Effect on core of a 10 pp rise in relative oil inflation | about 0.01 pp (not significant) | | **[changed]** 0.14 pp (= 10 x 0.014; the 0.013 in the table is the increase, the 0.14 is the total) |

- **Permanent 10% oil rise, effect on the core price level after 12 quarters (Fig. 2, average of the five economies):** 0.05% under pre-pandemic dynamics; just under 0.1% with higher persistence only; 0.35% with both. Most of the effect builds within about 8 quarters.
- **Projection, average advanced-economy core inflation (Fig. 3):** pre-pandemic dynamics peak near 2.2%; persistence only plateaus around 2.5%; full model nearly 2.8% around mid-2027, about 0.6 pp above the pre-pandemic path (0.3 pp from persistence, a further 0.3-0.35 pp from pass-through), then about 2.2% by end-2028. The pass-through part fades as the oil impulse in the futures curve normalizes; the persistence part keeps core above the no-persistence path "well into 2028".

## Country-level and US-specific results **[added; original had only fn 4 in one line]**
- **The note reports no country-level table or figure.** The only country evidence is footnote 4 (country-specific OLS, no coefficients shown): persistence rise "broad-based and significant across all five economies"; pass-through "rose significantly in Canada, Japan, and the U.S., but was weaker and not statistically significant in the euro area and the U.K., possibly reflecting Europe's natural gas price shock following Russia's invasion of Ukraine."
- **US-specific:** no US coefficient, interval or figure appears anywhere. The US is "significant" only through fn 4. The authors warn the panel "does not allow us to control for some specific factors that have seemingly contributed to persistently elevated inflation in the U.S."
- Fn 3: for the US, Peneva et al. (2025) show import prices excluding energy matter; the authors could not build a consistent cross-country measure, so import prices are not in the baseline. **[changed]** The original said "adding import prices adds nothing"; the note says that only of the panel regression and flags the US as a case where the control matters.

## Robustness and footnotes (all 11 checked)
- Fn 1: authors' views only. Fn 2: actual oil price changes, not isolated supply shocks (Kilian 2009); the output gap control is argued to help isolate the cost-push component **[added]**. Fn 3: import prices (above). Fn 4: country level (above). Fn 5: energy CPI instead of oil gives "similar, indeed somewhat larger" pass-through; dropping contemporaneous oil gives similar results. Fn 6: V/U in place of the output gap gives +0.292 persistence, +0.010 pass-through, still significant (Canada excluded: vacancy data start 2015) **[added]**. Fn 7: Alp et al. (2023) found a permanent 10% oil rise raises core CPI about 0.1% over roughly eight quarters, close to this note's pre-pass-through-change result **[added]**. Fn 8: GSCPI decay. Fn 9: GEMUS = Global Economy Model for U.S. Policy Analysis, an extension of Cuba-Borda et al. (2025). Fn 10: policy rule. Fn 11: oil cost share as proxy (below).

## GEMUS policy simulation (Figure 4) **[changed: original said only "a Taylor-type policy rule"]**
- **What it is.** A structural open-economy model with the US and a foreign block that contains a small oil-producing region. The 10% oil price rise comes from cutting that region's oil supply. Trade in consumption goods, intermediate inputs and capital goods; nominal and real rigidities; financial frictions.
- **The policy rule** (fn 10): "an inertial rule similar to that in Taylor (1999), with the policy rate responding to core inflation and the output gap." The same rule is used in all three cases. **It is not an experiment comparing different rules**; what varies is the calibration of the inflation process.
- **Three calibrations.** Black: pre-pandemic (low persistence, low pass-through): activity falls "a little over 0.1 percent", headline inflation rises "noticeably but briefly", core only modestly, policy tightens slightly. Red: higher persistence: larger, longer-lasting core response, somewhat more severe contraction, "the differences are not large", policy still responds modestly. Blue: higher persistence plus higher pass-through.
- **How higher pass-through is built.** A "higher cost share of oil in production", calibrated "to match the rise in pass-through estimated in our regressions" (fn 11: a proxy for "larger indirect effects on wages or on the prices of other inputs"; raising price-adjustment frequency instead gives similar near-term results for activity and the policy rate).
- **Result (blue).** Headline and core inflation "much larger and more persistent, and the GDP hit is about twice as large." Policy must "tighten materially to contain inflation even as the economy weakens." Output falls from both supply-side (costs) and demand-side (oil prices, tighter policy) forces.
- **Limits.** The text gives no figure for the blue-line GDP loss; "twice as large" has no stated comparator (read as versus the earlier cases) and Figure 4 values are not in the text. Do not quote a GDP number.

## What it does NOT say (corrections marked)
1. It does not say second-round effects are happening: "second-round effects have not yet materialized; however, risks are mounting."
2. It does not separate indirect from second-round effects; pass-through is one reduced-form coefficient. Fn 11's "indirect effects on wages or on the prices of other inputs" is the justification for the simulation's proxy, not an estimated finding **[changed wording]**.
3. It does not separate oil supply from oil demand shocks; the post-pandemic terms "may partly reflect the co-movement of oil prices with broader global demand pressures."
4. It is not a central forecast; the authors call the paths "an upper bound on the likely impact rather than a central prediction."
5. It cannot separate a structural change from more frequent or more persistent supply shocks, or say whether the change will "endure or reverse."
6. No US-only model; US result in fn 4 only (see above).
7. It does not recommend a policy; it says oil shocks "may now pose greater challenges to monetary policy."
8. **[changed]** Its projection inputs are dated: Brent futures as of early August 2026. The original added "before the late-Oct spike above $110"; that is wrong. EIA daily Brent (`C_q8_oil_daily.csv`) was $86-97 in August, averaged $114 in September (peak $130.8) and $124 in October (peak $135.51 on Oct 2). Every daily close from Sep 10 through Oct 30 was at or above $110, fell to $91.84 on Nov 4 and was $92.14 on Nov 11, back near the August level the futures curve was built from.
9. Short, unusual sample: 2021:Q1-2026:Q2 is 22 quarters, which includes reopening demand, fiscal stimulus, labor-market tightness and supply disruptions (the note cites Bernanke and Blanchard 2024).

## Waller's use of it (Nov 10 speech, checked against the saved PDF)
- His words: core inflation "may be more responsive to energy shocks"; "in a more sustained way than in the past"; "cautions against taking too much comfort in this view"; "especially if oil prices were to remain elevated, these pressures could be larger than previously though[t] and persist well into 2027" (the speech text reads "though").
- Faithful on the conditional (oil staying elevated). He omits "upper bound" (zero hits for "upper bound" and zero for "second-round" in the speech). "Well into 2027" is his paraphrase: in the note the pass-through path peaks mid-2027 and the persistence path stays elevated "well into 2028".
- Framing for Q&A: Bowman, look through and contain second-round effects if they appear; Waller, the first round (direct plus indirect) is larger and longer-lasting than assumed.

## How it can be used (unchanged in substance)
Slide 2: pass-through 0.01 -> 0.14 pp per 10 pp relative oil inflation; US in the "significant" group per fn 4, with the confirming-item test (airfares, freight; see `C_q11_confirming_items.md`). Slide 3: persistence 0.35 -> 0.65. Slide 4: the 0.6 pp as the staff note's upper bound, conditional on oil staying elevated, with the dated-input caveat above. Policy framing: GEMUS shows a larger activity cost alongside a harder inflation problem; it supports the policy-lag argument and the warning about tightening into weakness. Q&A: volunteer the caveats.
