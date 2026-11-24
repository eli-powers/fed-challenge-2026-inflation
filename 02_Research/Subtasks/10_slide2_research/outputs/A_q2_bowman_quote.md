# Bowman's decomposition: exact words and comparison

**Source (opened, local primary copy):** `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` (Vice Chair for Supervision Michelle W. Bowman, "The U.S. Economy and Considerations for Monetary Policy", Council on Foreign Relations, Nov 10, 2026; original https://www.federalreserve.gov/newsevents/speech/bowman20261110a.htm). Text extracted with `textutil` and searched in Python (`code/A_q2_bowman.py`). [O: local copy; the federalreserve.gov original was not re-fetched by this agent]

## The paragraph (section "Inflation", 2nd paragraph of that section)

> Lack of progress on lowering inflation largely reflects a confluence of shocks unrelated to conditions in the labor market. Tariffs, energy, and AI-related price pressures each accounted for roughly one-fourth of above-target core PCE inflation over the 12 months ending in September. The remaining one-fourth likely reflects persistent effects from the inflationary shocks in recent years. Price pressures had been concentrated in a few categories, but the latest data suggest that these pressures may be broadening.

Preceding paragraph (context): "Inflation Progress on lowering inflation has stalled over the past two years or so. Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3.3 percent in October, as upward pressures from higher energy prices and AI-related demand continue to flow through to core goods and services prices."

Following paragraph: "It is important to ensure that those inflationary pressures do not intensify, further broaden, or become embedded in consumer and business expectations. But today's consumer price index data suggest that inflation pressures may persist for longer. Tariff effects should further wane going forward. Energy-related price pressures should unwind when the Middle East conflict resolves. And inflation pressures related to the AI buildout seem to persist despite some early signs of slowing. I mostly view these pressures as reflecting relative price shocks in specific sectors of the economy. For example, the AI buildout has quickly shifted investment demand toward specific types of high-tech capital, putting upward pressure on prices due to relatively inelastic supply in the near term. As these shocks wane or unwind and with no inflationary pressures emerging in the labor market, my forecast is for core PCE inflation to move closer to 2 percent next year."

**Footnotes in the speech:** 5 footnotes (1-5). None gives a method, data source or breakdown for the one-fourth split. Footnote-search hits for tariff/decompos/attribut/energy: none. So the method behind the split is not disclosed in the speech. The speech also says 12m core PCE "likely moved up further to 3.3 percent in October" (our Oct estimate: 3.24%).

## What Bowman says vs our tag-scheme shares (12m, share of above-target core PCE)

Bowman, 12 months to September: tariffs ~25%, energy ~25%, AI ~25%, "persistent effects from the inflationary shocks in recent years" ~25%.

**Method a (central): each group owes 2% on its own weight** (above-target = contribution - weight share x 2)
| Period | Energy | Tariff | AI | Untagged | Total above-target (pp) |
|---|---|---|---|---|---|
| 2026-09 | 29.2% | -0.1% | 18.0% | 52.9% | 1.184 |
| 2026-10 (est.) | 31.9% | 5.1% | 15.1% | 47.8% | 1.304 |

**Method b: excess over 2% only (leaves running above 2%; below-target leaves do not offset)**
| Period | Energy | Tariff | AI | Untagged | Total above-target (pp) |
|---|---|---|---|---|---|
| 2026-09 | 23.0% | 7.9% | 13.0% | 56.1% | 1.851 |
| 2026-10 (est.) | 24.2% | 9.8% | 11.9% | 54.1% | 1.893 |

**Method c: the whole 2% charged to the untagged group**
| Period | Energy | Tariff | AI | Untagged | Total above-target (pp) |
|---|---|---|---|---|---|
| 2026-09 | 59.8% | 18.6% | 21.3% | 0.4% | 1.184 |
| 2026-10 (est.) | 59.7% | 22.1% | 18.1% | 0.1% | 1.304 |

Weights (core, start of Sep-2026 12m window): energy 18.1%, tariff 11.1%, AI 2.0%, untagged 68.9%.

## Her fourth piece vs the tag scheme
- Bowman's fourth piece ("persistent effects from the inflationary shocks in recent years") is a **cause**, not a group of items. A tag scheme assigns each leaf to one group; it has no residual cause. The nearest analogue in our scheme is **untagged** (items with no energy, tariff or AI link), but untagged items can also carry second-round effects of the three shocks and effects of the earlier shocks (2021-22). Whether untagged = her fourth is a mapping assumption, not something the speech supports. [interpretation flag, not a finding]
- Her split is by cause (each of the 3 shocks ~25% of above-target), ours is by item exposure; an AI-demand shock can lift untagged services (e.g. via wages or rents), and an energy shock lifts non-energy items through costs. Item tags can't see this.
- Our untagged group is 69% of core weight and carries 53% of above-target core PCE under method a, about double her 25% for the fourth piece.
