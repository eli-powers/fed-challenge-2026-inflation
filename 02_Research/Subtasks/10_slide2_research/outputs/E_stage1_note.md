# E. What drove PPI stage 1 in Oct 2026, with energy negative? (Eli follow-up, Nov 15)
Status: coordinator one-off, **not audited**. Script: `code/E_stage1_decomp.py` (`--fetch` pulls the commodity PPIs). Raw: `03_Data/Raw/BLS_PPI_stages_2026-11-15/` (sub-groups, SA, and Dec 2025 relative importance) and new `03_Data/Raw/BLS_PPI_stage1_commodities_2026-11-15/` (commodities, NSA). Outputs: `E_stage1_groups.csv`, `E_stage1_core_goods_commodities.csv`, `E_stage1_summary.csv`.

**Method.** Contributions in pp of stage 1. Weights are Dec 2025 relative importance updated for relative prices to the window's base month. Layer 1 (21 leaf sub-groups, SA) sums to 0.56 vs published 0.551 (Oct m/m), and 4.37 vs 4.42 (Jul → Oct level change).

**Layer 1, Oct m/m (stage 1 +0.55%).**

| Sub-group | Weight | Contribution (pp) |
|---|---|---|
| Goods ex food & energy | 44% | +0.53 |
| Trade services (margins) | 11% | +0.21 |
| Transport & warehousing of goods | 5% | +0.13 |
| Services less trade/transport | 26% | +0.07 |
| Passenger transport | 1% | −0.02 |
| Foods | 2% | −0.12 |
| Energy | 11% | −0.25 |

Aug → Oct (3 months, not annualized; +4.42% in total): energy +1.65, goods ex food & energy +1.08, trade +0.84, freight +0.38, services +0.19, foods +0.15.

**Layer 2, inside goods ex food & energy, Oct m/m (NSA; top 40 commodities = 29.2 of 45.3 points of weight).**
- Primary basic organic chemicals (WPU061401) +7.8%: **+0.20 pp**. Other basic organics (WPU061403) +1.7%: +0.07. These are petrochemicals made from oil/gas feedstock.
- Carbon steel scrap (WPU101211) +3.4%: +0.10. Copper scrap +1.8%: +0.03. Nonferrous and aluminum scrap −0.04.
- Steel pipe, structural metal and other metal products: about +0.04.
- **No computer or electronic component (BLS groups 115–117) is among the 40 largest stage 1 core-goods inputs.**

**Reading (data only).**
- About +0.40 pp of the non-energy rise is plausibly energy-linked: petrochemicals +0.27 and freight +0.13.
- About +0.33 pp has no obvious energy link: scrap metals and trade margins.
- AI-linked electronics are not a material stage 1 input on these weights.

**Caveats.**
- Layer 2 is NSA while layer 1 is SA.
- My energy-intensive/other heuristic in the CSV is too broad (it counts printing as energy-intensive); use the named commodities, not the class totals.
- Hot-rolled steel sheet (WPU101703) has no Oct value.
- Oct 2026 PPI is preliminary.
- It's one month.
- BLS's weights file has stray `#REF!` cells in column A of some commodity rows. The script ignores that column; an earlier run that didn't was discarded.
