# October 2026 PCE estimate: what drove headline and core (interpretation draft)

**Date:** 2026-11-13. **Source:** the "PCE Oct 2026 estimate" tab in `Price_Basket_Findings.xlsx` (Eli's bottom-up build, audited by Codex Nov 13) and its line file, `04_oct_pce_build/outputs/W_pce_oct_tab_lines.csv`.

**What I added:** a grouping of the ~212 component lines into BEA categories, plus an "excess over 2018–19" split. Script: `code/oct_pce_drivers_by_group.py`. Outputs: `outputs/oct_pce_drivers_by_group.csv` and `outputs/oct_pce_drivers_by_flag.csv`. This grouping is **not audited**.

**Caveats:**
- These are estimates. Bands are about ±0.05 pp on m/m and about ±0.2 pp on 3m annualized.
- The tab says component sums overshoot the aggregates (3m headline by +0.55 pp, mostly annualization convexity), so read group shares as approximate.
- "Excess" = weight × (12m rate − that component's own 2018–19 average y/y). It's a rough measure of what's running above normal, not a model.

## Aggregates (estimate)

| | 1m | 3m ann. | 6m ann. | 12m |
|---|---|---|---|---|
| Headline PCE | 0.32 | 4.6 | 3.1 | 3.8 |
| Core PCE | 0.30 | 3.6 | 2.9 | 3.2 |

The pattern is 3m > 12m > 6m for both: a soft middle of the year, then a reacceleration over Aug–Oct. Core 1m of 0.30 is about 3.6% annualized.

## Headline: energy, plainly

| Group | Weight % | 12m contrib. (pp) | 3m ann. contrib. (pp) |
|---|---|---|---|
| Energy goods + energy services | 4.1 | 0.81 | 1.69 |
| Everything else | 95.9 | ~3.1 | ~3.5 |

- About a fifth of 12m headline and about a third of 3m headline come from 4% of the basket.
- Gasoline is +38% y/y and +73% 3m annualized. Fuel oil is +75% y/y.
- Electricity is +4.2% y/y, with a small contribution (0.05 pp).
- Food at home is minor: 0.14 pp of 12m.

## Core: no single driver, and the composition is changing

**Level (12m contributions, pp of about 3.3 summed):** housing 0.59, health care 0.53, financial services 0.39, transportation services 0.34, recreational goods 0.32, food services 0.31, other services 0.30.

**What's running above normal (excess vs. 2018–19, about 1.5 pp of core in total):**

| Bucket | Excess (pp) |
|---|---|
| Core goods (recreational goods 0.45, of which software 0.26 and computers 0.09; clothing 0.11; other nondurables 0.11) | ~0.74 |
| Services ex housing (transportation 0.26, mostly airfares; health care 0.18; other services 0.13; food services 0.10) | ~0.75 |
| Housing | ~0.0 (−0.02) |

**Momentum (3m annualized contributions):** the mix has moved away from goods and toward services ex housing.
- Services ex housing ≈ 2.5 pp of the 3.8 summed.
- Housing 0.57: steady at about 3.4%, near its 2018–19 pace.
- Core goods ≈ 0.7. Software has turned negative (−9% 3m ann.), while PCs/tablets are +25% 3m ann.

Largest single 3m core contributors:
- OER 0.44
- **Newspapers and periodicals 0.31** (0.5% weight; +60% 3m ann.)
- Hotels 0.21
- Airfares 0.19
- Hospitals 0.18
- Cell phone service 0.17
- Vehicle repair 0.15
- Restaurants 0.15
- PCs 0.14
- Portfolio management 0.13 (carried forward, i.e. assumed)
- Toys and games 0.12
- Taxis and ride-sharing 0.11 (+45% 3m ann.)

**The tab's flagged themes, core:**

| Flag | 12m (pp) | 3m (pp) |
|---|---|---|
| Energy spillover | 0.19 | 0.24 |
| AI | 0.25 | 0.03 |
| Asset-price | 0.19 | 0.26 |

**Breadth:** core 3m share above 3% is flat (43.7% Sep → 43.8% Oct). The 12m share above 3% is 51%; 72% of weight is above its own 2018–19 average.

## Interpretation (mine; Eli forms his own read)

1. **Headline is an energy story, and that's safe to say.** The open question for policy is core.
2. **Core's acceleration is intensifying, not broadening.** Momentum rose while 3m breadth stayed flat, so the same ~44% of the basket is running hotter. On its own, that argues against "inflation is spreading everywhere" and is evidence for 25 over 50. Slide 2's question ("is it spreading?") has a tentative answer: not wider, hotter.
3. **The core momentum leans toward energy-sensitive services** (airfares, taxis/ride-sharing, vehicle repair, restaurants, hotels). That's consistent with pass-through, but the lines the tab itself flags as energy spillover are only about 6% of core 3m. Taxis and restaurants aren't flagged. Whether they belong in a spillover bucket is a research choice to make deliberately, not after seeing the answer.
4. **Housing isn't the excess.** It's a big contributor but running near its pre-pandemic pace. So shelter disinflation isn't a coming relief valve, and "it's just lagged shelter" isn't the right story. That supports dropping shelter from Slide 3 if space is tight.
5. **AI in consumer prices is a 12m story fading in the 3m, with a twist.** Software drove the 12m excess and is now falling, while computer hardware is accelerating. If memory or chip costs are the reason, that would support the AI-inputs hypothesis for Slide 4. That's untested. The PPI-input work should check it rather than assume it.
6. **Two Q&A soft spots sit inside core momentum.**
   - Newspapers and periodicals alone is about a tenth of summed 3m core.
   - Portfolio management is assumed (carried forward) and tied to equities, which have fallen.
   A judge who asks "what's in that 3.6%?" should get these from us first.

## Flags
- The new build's 12m core breadth (51% above 3%) is not comparable to the old pipeline's Sep figure (60%). The old pipeline had the core-flag error, and the two builds differ. Don't present the change as a trend until it's reconciled.
- This grouping is my analysis on audited inputs. The grouping itself isn't audited.
