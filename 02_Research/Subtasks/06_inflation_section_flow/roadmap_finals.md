# Inflation section roadmap for the finals (structure only)

**Started:** 2026-11-14. This builds on `slide_structure.md` (Nov 13). Each slide is locked with Eli one at a time; we expect to iterate further during development.
**Inputs:** Fed officials' views (`02_Research/External_views/Fed_officials_2026-11/summary.md`), 2025 finalist transcripts, Eli's views.

## Slide 1: Where is inflation, and is it accelerating? (LOCKED Nov 14)

**On the slide**
1. Headline figure: October core and headline PCE at 12 months. This is UMD's own estimate, marked "est." on the slide. It is the main inflation figure for the whole presentation, so every speaker uses the same number.
2. Momentum: 12-month, 6-month annualized and 3-month annualized rates through the October estimate, plus the Sep→Oct m/m change. The direction comes from the data, not from an assumption.
3. Corroboration line (small): the median and range of outside October estimates, and where UMD's estimate sits relative to them. **Changed Nov 15 (Eli): moved off the slide; it is now a verbal cue only ("about 0.3, in line with other forecasters using a similar methodological approach").**

**Spoken only**
- Method, one sentence: built from CPI and PPI components, seasonally adjusted, and in line with outside estimates and nowcasts.
- PCE is the Fed's target measure, which is why it is the headline.
- The CPI–PCE gap and its main driver, one line. Right now core PCE (3.1%) runs above core CPI (2.6%); headline PCE and CPI are about equal (Sep, y/y). **Changed Nov 15 (Eli): quote only the Oct 12m gap (+0.43 pp, approx.), with the either/or weight/scope line (E1). Script: `01_Finals/speaker_notes/verbal_cues_and_script_notes.md`.**

**Backup**
- The method and its backtest error (the backtest is done).
- Table of outside estimates.
- CPI–PCE reconciliation.

**Dropped**
- The two-model panel. Harvard's "two nowcasts" in 2025 were GDP figures, spoken at about 1:34. They were not inflation estimates and may never have been on a slide.

**Research**
- R1. Oct estimate: backtest done; cross-check done (Goldman within 2–3bp or identical on headline/core, m/m and y/y). Remaining: save the comparison as a sourced table if it isn't already, and pull the backtest error for backup.
- R2. Outside October PCE estimates released after the Nov 13 PPI. Compare on core m/m to two decimals; report the median and range, and our distance in bp. Label Cleveland as a model nowcast (it uses no PPI). Bowman's 3.3% counts as one source. **Paywalled sources go to Eli to check.**
- R3. Decompose the current core CPI–PCE gap. Candidates: shelter weight (CPI is about 2× PCE), PCE-only imputed financial services, third-party-paid health care, airfares taken from PPI, and the weighting formula.
- R4. Resolve September headline PCE y/y: Waller says 3.7%, while Logan, Paulson and Jefferson say 3.6%.
- R5. Cleveland nowcast as of the Nov 18 cutoff.
- R6. Reconciliation (Eli, Nov 14): pick the breadth method (leaf, 149 items, vs. sub-line, 184) and apply it to both months; explain the ~0.13 pp gap between published core and our 3m component sum. See `07_breadth_reconciliation/report.md`.

## Slide 2: How widely has the energy shock spread, and at what scale? (LOCKED Nov 14)

**Opener (spoken or subtitle):** broad isn't the same as persistent. A one-time repricing can spread widely and still fade. This slide measures how far it has spread; slide 3A asks whether it lasts.

**On the slide**
1. **Lead exhibit:** one set of tags (energy-exposed, tariff-exposed, AI-related, untagged; one tag per core item) feeds two views:
   - (a) a Bowman-style attribution of above-target core PCE: Sep vs. her roughly 1/4 each, then Oct;
   - (b) breadth for tagged vs. untagged items at 3m and 12m.
   - Concentrated in tagged items fits Bowman (repricing). Rising in untagged items fits Waller and Daly (spreading), which leads into 3A. **Correction (Nov 15, slide 2 research):** Bowman herself says pressures "may be broadening"; the real difference is whether broadening persists (slide 3A). Framing now set by S2-E1 (see `10_slide2_research/FINAL.md` §7).
2. **Breadth for core and supercore:** spending-weighted; 3m rates annualized before the 3% cutoff; one method (leaf or sub-line) used for both months and labeled.
3. **Upstream panel:** PPI stages 1–2 (production flow: **WPSID51/52**; ID61–64 are by commodity type, and ID62 = unprocessed goods is not a stage), the true leading signal (stage 3 partly feeds PCE directly), plus the ISM price-pressure index if it is public. Still building fits Waller; flattening since the early-November oil drop fits Bowman.

**Spoken only:** indirect effects are inferred, not observed directly. The FEDS oil-note pass-through estimate, plus 1–2 US confirming items. The comparison to Waller's ">70%" (core services). **Correction (Nov 15):** only the spending-weighted measure reproduces >70% (70.8); a count gives 63.1. Per S2-E7, Waller is not named; we quote our own supercore ex-hospitals figure.

**Backup:** tagging rules and the alternative-threshold run; headline and core-goods breadth (**correction Nov 15:** headline 12m breadth is *below* core in Sep, 59.8 vs 60.6, because food offsets energy; do not say "rises mechanically"); group contributions; labels for carried-forward Oct items.

**Research**
- R1. Tagging rules: DONE, approved Nov 14 (`08_shock_tagging/decisions.md`). Final: AI 2.0%, tariff 11.1%, energy 18.3% (top quartile), untagged 68.6% of core weight. Open item: verify the computer/smartphone tariff exemption.
- R2. Attribution and tagged breadth: Sep vs. Bowman, then Oct.
- R3. Breadth by basket (headline, core, supercore, core goods), plus a one-off count-based core-services run to compare with Waller.
- R4. PPI stages 1–2 (WPSID51/52), October.
- R5. ISM note (Cajner et al.): read it and check whether the index is public.
- R6. Second half of the oil note, including the US-specific results.
- R7. 1–2 US confirming items (e.g. airfares).
- R8. Decompose the 12m Oct breadth drop (~6.6 pp): by group, and carried-forward vs. measured items. **Update Nov 15:** the "~1.8 pp in carried-forward items" is superseded (slide 1 R6, Codex-confirmed): carried-forward lines contribute −0.003 pp. Three hospital leaves contribute −8.7 pp, a base effect from the Oct 2025 hospital jump (+0.89% m/m) leaving the window. Central method is now **weighted leaf** (Eli, Nov 15; E5).
- R9. **(Eli, Nov 15)** Breadth across measures, emphasising supercore and other persistence-adjacent measures. Candidates to scope with Eli: supercore (core services ex housing); core services ex housing ex transport (Logan's measure); trimmed-mean and median-style components; and services vs goods. Same weighted-leaf method, 3m and 12m, Sep vs Oct.

**Stress-test answers to prepare:** tags are arbitrary; the 12m breadth drop; Bowman as a black box; Oct too early for indirect effects; airfares as demand vs. pass-through; AI/energy overlap (electricity is outside core); why 3%; headline mechanics.

## Slide order (not locked)
Working order: 1 level, 2 breadth, 3A persistence, 3B forecast, then AI. Eli is considering moving AI to second place, since AI is the presentation's unique lens. We'll stress-test the order once the slides are developed.

## Slide 3A: Is the first round turning into a second round? (LOCKED Nov 14)

**Bridge from slide 2 (spoken):** "Upstream pressure doesn't show second-round effects, but it lengthens the first round, which raises their risk."

**On the slide**
1. **Lead exhibit:** Bernanke–Blanchard (2023) channels, 2021–23 vs. now:
   - labor tightness;
   - expectations: short vs. long; households, professionals and markets;
   - wages and catch-up, read through unit labor costs (ULC) and the labor share.
2. **Underlying trend:**
   - NY Fed multivariate core trend 2.8% vs. Dallas trimmed mean 2.3%.
   - Logan's reason for the gap: "a change in the mix of price increases and decreases is causing the trimmed mean to drop too many increases", so it is "likely" below the true trend.
   - Plus supercore or market-based services. Candidate: Logan's core services ex housing and ex transportation, 3.2%.

**Spoken**
- Nearly six years above target (verify), with stacked shocks.
- The oil note's higher post-pandemic pass-through. The authors can't tell whether the inflation process changed or shocks became more frequent; either way, pass-through is higher now. Do NOT claim a change in price-setting behavior.
- Productivity vs. wages: ULC strips out productivity. Benchmark: wage growth consistent with 2% inflation is about 2% plus trend productivity. Barr puts the labor share at a record low 52.8%.

**Policy hand-off (decision section, not this slide)**
- "Little evidence second-round effects have emerged yet. But holding isn't the default: policy is still accommodative (Logan: real rate 78bp, a quarter point below the lowest neutral estimate); AI is demand-side and policy can act on it; and nearly six years above target strains the anchor → 25bp."
- 3A ends on the evidence alone.

**Backup:** full expectations dashboard; trimmed-mean mechanics; shelter, new-lease vs. measured rents; 2020–24 policy timeline (once verified).

**Research**
- R1. Bernanke–Blanchard model and decomposition sections. Verify Reis (2021) and the state-dependent-pricing cite.
- R2. Dallas Fed staff research on trimmed-mean bias.
- R3. Wages, ULC (4q and 8q), labor share, productivity.
- R4. Expectations dashboard, including Q4 SPF.
- R5. Catch-up evidence: Atlanta Fed BIE, NFIB compensation plans, Conference Board.
- R6. Verify time above target and the policy timeline.
- R7. Pace's exact Phillips-curve and productivity wording.
- R8. Refresh the underlying measures.

**Stress test**
- Anchored expectations, so why not hold?
- Cherry-picking the 2.8% over the 2.3%.
- The oil note is a panel and an upper bound.
- Short-run expectations just track gas prices.
- The catch-up evidence is anecdotal.
- Wage growth is just productivity.
- ULC is noisy.

**Also for slide 2:** Logan's breadth framing ("concentrated in narrow categories… may cool" vs. "widespread… underlying trend") is a citable opener.

## Slide 3B: Forecast and scenarios (LOCKED Nov 14)

**Decisions (Eli):**
- Core PCE only.
- Horizon through 2027Q4, i.e. 8 quarters.
- Baseline is the **Q3 SPF** for now. The **Q4 SPF comes out Mon Nov 16**, before the cutoff. The script must update the slide on the new SPF with one rerun, so it belongs in `03_Data/pipelines/` because it recurs.
- Flag: the Q3 SPF predates the late-October oil spike. The oil-gap adjustment is how we account for that, so state the baseline date on the slide.
- Team: Eli coordinates with the other lenses. Inflation is probably the only section with a forecast.

**Agreed so far**
- There is always a forecast, whatever slide 2 finds.
- Method: outside forecasts, adjusted by us and labelled.
- Two axes: oil path × pass-through regime. The regimes are the oil note's post- and pre-pandemic estimates. 3A's evidence decides which regime is more likely.
- Oil paths:
  - baseline;
  - oil rises again;
  - Hormuz opens: pre-war trend plus a residual premium. Waller's $20–30 is the anchor for the premium.

**How the adjustment works**
1. Start from an outside baseline core PCE path, e.g. the Q4 SPF quarterly path or the Sep SEP.
2. Measure each scenario's oil path against the oil price the baseline assumed. Proxy: futures as of the forecast date.
3. Map the oil gap to core using the oil note's dynamics. Post-pandemic, a permanent 10% rise lifts the core price level by about 0.35% after 12 quarters; pre-pandemic, about 0.05%. If the note's table gives enough detail, apply its coefficients quarter by quarter.
4. Optional: headline adds the direct energy effect through energy's share of PCE.
5. Do it in one small reproducible script, Pace-style.

**Research**
- R1. Baseline: Q3 SPF quarterly core PCE path, swapped to Q4 SPF on Nov 16. The Sep SEP median goes in a spoken line or backup.
- R2. Oil paths: Brent futures or EIA STEO (Nov) for the baseline; an upside path (e.g. back to late-Oct ≥$110, per Bowman); the pre-war Brent level plus premium.
- R3. The oil note's coefficients and dynamic path, from the saved full text.
- R4. Rule for mapping to headline (optional).
- R5. The script and a labelled fan of scenarios.
- R6. A balance-of-risks close that ties 3A's regime evidence to the scenario weights.

**Caveats to state**
- The oil note is a five-economy panel and an upper bound.
- The baseline's own oil assumption isn't published; we use the proxy above.
- These are scenarios, not probabilities.

## Slide 4: AI (PLACEHOLDER, deliberately unfinished)
- Contents stay as in the Nov 13 `slide_structure.md` slide 4 for now.
- Role and placement are undecided; one option is moving it to second.
- Iterate during slide development (flagged in STATE.md).

## Build format
PowerPoint, with charts built from Excel so figures are verifiable and consistent (David's method). David's slide prompt will come at build time.

## Build order and status
1. **Slide 1** (tonight): research R1–R6 so tomorrow's build only needs Eli's go-ahead. The first decision is the breadth method (leaf vs. sub-line); see slide 1 R6.
2. Slide 2 → 3A → 3B → AI (the AI slide's setup is still owed; see STATE.md).
3. Mon Nov 16: Q4 SPF lands; rerun the 3B pipeline.
4. Nov 18: data cutoff. Refresh the Cleveland nowcast, any new speeches (Warsh Nov 16, Hammack and Kashkari Nov 17, Musalem Nov 18) and the Oct FOMC minutes.
5. Audits (Codex) on each slide's numbers before they're final.
