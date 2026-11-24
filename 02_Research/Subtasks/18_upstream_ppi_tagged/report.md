Status: Audited — converged R3 (Codex, Nov 17 2026)

# Subtask 18: Producer-price inflation by shock group (Method A, tagged PPI stage commodities)

For slide 2B right chart (Eli, Nov 17 2026; rules fixed in `GO.md`). Data: BLS PPI commodity indexes, NSA, via BLS API v2, retrieved 2026-11-17 (raw: `03_Data/Raw/BLS_PPI_stage_commodities_2026-11-17/`. The original pull was 26 JSON batches, 1,265 series requested and 1,248 with data. The Dec 2024 sensitivity added 3 batches, 103 series requested and 39 with data. In total: 29 batches, 1,368 requested, 1,287 with data). Weights: BLS relative importance, Dec 2025, ID production flow file (posted 06/11/2026). Import shares: BEA 2017 detail use table (before redefinitions, producers' value). **Oct 2026 values are preliminary (BLS footnote P on the stage aggregates and on 1,178 commodity series in the original pull; 1,214 including the Dec 2024 extra batches). BLS makes interim revisions and finalizes NSA PPIs four months after first publication.**

Rerun: `python3 -I "02_Research/Subtasks/18_upstream_ppi_tagged/code/ppi_tagged_excess.py"` (add `--fetch` to re-download), then `code/report_tables.py` and `code/verify_by_hand.py`. Runtime about 30 s. All outputs in `outputs/`.

## Answer (stage 4 central, pp of stage 4's 12-month inflation above each group's own 2018–19 pace)

| | energy | tariff | AI | other | **total** | stage 4 12m (units / published) |
|---|---|---|---|---|---|---|
| Mar 2025 | −0.22 | −0.15 | +0.02 | +0.57 | **+0.22** | 2.55 / 2.56 |
| Feb 2026 | +0.14 | +0.50 | +0.13 | +1.42 | **+2.19** | 4.52 / 4.43 |
| Oct 2026 (P) | +1.07 | +0.85 | +0.27 | +3.30 | **+5.49** | 7.82 / 7.98 |

Stage 1 central, same months: total +0.39, +3.03, +12.50 (energy −1.15 / −0.14 / +4.11; tariff +0.07 / +1.13 / +1.55; AI +0.02 / +0.05 / +0.07; other +1.45 / +2.00 / +6.77). Full tables, all sensitivities, below.

**Stability across sensitivities (flag only, not a recommendation):** stage 4 is the more stable stage. Oct 2026 total ranges +5.11 to +5.49. Tariff stays at +0.84–0.85 in every version and AI at +0.19–0.30. The largest swing is freight-as-energy, which moves 0.39 pp from other to energy. Commodity→NAICS mapping uncertainty is not captured by these variants: one remap in audit R1 (061401) moved stage 1 tariff by about 1 pp. Stage 1 is not stable. Oct 2026 tariff is +1.19 with Dec 2024 weights, +1.55 central and +3.32 with BEA scrap tagging; the total runs from +9.75 to +12.52. Stage 1's Dec 2024 → Dec 2025 BLS reweighting is large (stage 1 goods-producers' core goods RI 16.7 → 27.5), and its reproduction gap exceeds the 0.3 pp check in Mar 2025 and Oct 2026.

## Method as run
1. **Units.** Commodity codes listed under each stage in the RI file. A commodity that appears in several producer-type blocks is one unit, with its RI summed. Stage 4 has 655 units (RI sum 99.980) and stage 1 has 557 (99.991); the gap from 100 is rounding in the BLS file. Services lines are units.
2. **Prices.** Each unit uses its own WPU index (NSA). Months where that index is unpublished are filled from the parent group's movement (4-character, then 3-character), chain-linked at the nearest common month. That covers 108 stage-4 units (RI 2.78) and 91 stage-1 units (RI 3.29). The remaining units (547 and 466) use their own index throughout. Units without the prices a window needs are dropped for that window, with weights renormalised. In the three focal windows that excludes RI 0 (stage 4) and 0.054 (stage 1). The maximum over the path is 0.892 / 2.382, in Jan 2018.
3. **Weights.** w_i = RI_i(Dec 2025) × I_i(t−12)/I_i(Dec 2025).
4. **Tags** (exclusive; priority AI > energy > tariff > other):
   - **Energy** = BLS group 05. The code checks that this set is identical to the units in each stage's energy blocks (20 in stage 4, 24 in stage 1).
   - **AI central** = 18 codes: 11 in BLS group 1178 (electronic components incl. semiconductors), 4 in 115* (computers/peripherals), and 3 communications-equipment codes (1176*). **No software-publishing unit exists in either stage**, so software is absent.
   - **AI buildout** adds 381101, 381102 and 381103 (all three BLS product lines of data processing/hosting, 518210, matched via NAICS per GO; 381102 added after audit R1), 117522 (switchgear), 119701, 119801, 114501 and 114502 (turbines and power transmission, 3336), and 453201 (engineering services). The last one is only a broad proxy for the 541330 utility-engineering line.
   - **Tariff** = goods (codes 01–15) whose BEA 2017 import share ≥ 0.15. The route is commodity → NAICS 2017 (`outputs/goods_naics_map.csv`, assigned by subagent S2 from item names; 7 codes corrected after audit R1 via `NAICS_FIX` in the script) → BEA detail (prefix match, pooled, broadened if needed).
   - **Other** = the rest, including all non-AI services.
   - Full tag table: `outputs/tag_table.csv` (code, name, RI, tag, rule fired, import share, NAICS, BEA match, price source).
5. **Formula.** excess_g = s_g × (R_g(t) − B_g), with B_g = mean of R_g over 2018-01..2019-12. Total = sum of the groups. In the top-10 tables, an item's contribution = s_i × (r_i − B_g), which sums exactly to the group excess.

**Dec 2025 RI by tag:** stage 4 energy 6.23, tariff 20.70, AI 0.53, other 72.52. Stage 1 energy 7.38, tariff 20.37, AI 0.67, other 71.57.

### Excess by group (pp of the stage's 12m inflation above each group's 2018-19 pace)

| stage | version | month | energy | tariff | AI | other | **total** | units 12m | published 12m | gap |
|---|---|---|---|---|---|---|---|---|---|---|
| stage4 | central | 2025-03 | -0.22 | -0.15 | +0.02 | +0.57 | **+0.22** | 2.55 | 2.56 | -0.01 |
| stage4 | central | 2026-02 | +0.14 | +0.50 | +0.13 | +1.42 | **+2.19** | 4.52 | 4.43 | +0.09 |
| stage4 | central | 2026-10 | +1.07 | +0.85 | +0.27 | +3.30 | **+5.49** | 7.82 | 7.98 | -0.16 |
| stage4 | w_dec2024 | 2025-03 | -0.25 | -0.07 | +0.01 | +0.40 | **+0.10** | 2.51 | 2.56 | -0.05 |
| stage4 | w_dec2024 | 2026-02 | +0.04 | +0.55 | +0.10 | +1.27 | **+1.96** | 4.37 | 4.43 | -0.06 |
| stage4 | w_dec2024 | 2026-10 | +1.01 | +0.85 | +0.19 | +3.06 | **+5.11** | 7.52 | 7.98 | -0.46 |
| stage4 | ai_buildout | 2025-03 | -0.22 | -0.15 | +0.04 | +0.55 | **+0.22** | 2.55 | 2.56 | -0.01 |
| stage4 | ai_buildout | 2026-02 | +0.14 | +0.48 | +0.15 | +1.42 | **+2.19** | 4.52 | 4.43 | +0.09 |
| stage4 | ai_buildout | 2026-10 | +1.07 | +0.84 | +0.30 | +3.28 | **+5.49** | 7.82 | 7.98 | -0.16 |
| stage4 | freight_energy | 2025-03 | -0.25 | -0.15 | +0.02 | +0.60 | **+0.22** | 2.55 | 2.56 | -0.01 |
| stage4 | freight_energy | 2026-02 | +0.16 | +0.50 | +0.13 | +1.40 | **+2.20** | 4.52 | 4.43 | +0.09 |
| stage4 | freight_energy | 2026-10 | +1.46 | +0.85 | +0.27 | +2.91 | **+5.49** | 7.82 | 7.98 | -0.16 |
| stage4 | scrap_bea | 2025-03 | -0.22 | -0.15 | +0.02 | +0.57 | **+0.22** | 2.55 | 2.56 | -0.01 |
| stage4 | scrap_bea | 2026-02 | +0.14 | +0.50 | +0.13 | +1.42 | **+2.19** | 4.52 | 4.43 | +0.09 |
| stage4 | scrap_bea | 2026-10 | +1.07 | +0.85 | +0.27 | +3.30 | **+5.49** | 7.82 | 7.98 | -0.16 |
| stage1 | central | 2025-03 | -1.15 | +0.07 | +0.02 | +1.45 | **+0.39** | 2.27 | 1.94 | +0.33 |
| stage1 | central | 2026-02 | -0.14 | +1.13 | +0.05 | +2.00 | **+3.03** | 4.89 | 5.05 | -0.16 |
| stage1 | central | 2026-10 | +4.11 | +1.55 | +0.07 | +6.77 | **+12.50** | 14.34 | 13.91 | +0.43 |
| stage1 | w_dec2024 | 2025-03 | -1.01 | -0.31 | +0.02 | +0.54 | **-0.76** | 1.77 | 1.94 | -0.17 |
| stage1 | w_dec2024 | 2026-02 | +0.00 | +0.80 | +0.10 | +1.11 | **+2.01** | 4.53 | 5.05 | -0.52 |
| stage1 | w_dec2024 | 2026-10 | +3.75 | +1.19 | +0.22 | +4.58 | **+9.75** | 12.26 | 13.91 | -1.65 |
| stage1 | ai_buildout | 2025-03 | -1.15 | +0.06 | +0.09 | +1.38 | **+0.38** | 2.27 | 1.94 | +0.33 |
| stage1 | ai_buildout | 2026-02 | -0.14 | +1.09 | +0.07 | +2.00 | **+3.03** | 4.89 | 5.05 | -0.16 |
| stage1 | ai_buildout | 2026-10 | +4.11 | +1.52 | +0.15 | +6.72 | **+12.49** | 14.34 | 13.91 | +0.43 |
| stage1 | freight_energy | 2025-03 | -1.23 | +0.07 | +0.02 | +1.56 | **+0.41** | 2.27 | 1.94 | +0.33 |
| stage1 | freight_energy | 2026-02 | -0.16 | +1.13 | +0.05 | +2.04 | **+3.05** | 4.89 | 5.05 | -0.16 |
| stage1 | freight_energy | 2026-10 | +4.80 | +1.55 | +0.07 | +6.09 | **+12.52** | 14.34 | 13.91 | +0.43 |
| stage1 | scrap_bea | 2025-03 | -1.15 | +1.06 | +0.02 | +0.43 | **+0.37** | 2.27 | 1.94 | +0.33 |
| stage1 | scrap_bea | 2026-02 | -0.14 | +2.82 | +0.05 | +0.28 | **+3.01** | 4.89 | 5.05 | -0.16 |
| stage1 | scrap_bea | 2026-10 | +4.11 | +3.32 | +0.07 | +4.99 | **+12.49** | 14.34 | 13.91 | +0.43 |

### Group table, central (weight share, 12m rate %, 2018-19 baseline %, excess pp)

| stage | month | group | weight share | 12m rate | baseline | excess |
|---|---|---|---|---|---|---|
| stage4 | 2025-03 | energy | 6.7% | -1.89 | 1.37 | -0.22 |
| stage4 | 2025-03 | tariff | 20.9% | 1.23 | 1.95 | -0.15 |
| stage4 | 2025-03 | AI | 0.5% | 3.06 | -0.68 | +0.02 |
| stage4 | 2025-03 | other | 71.9% | 3.34 | 2.55 | +0.57 |
| stage4 | 2026-02 | energy | 6.4% | 3.57 | 1.37 | +0.14 |
| stage4 | 2026-02 | tariff | 20.7% | 4.36 | 1.95 | +0.50 |
| stage4 | 2026-02 | AI | 0.5% | 26.33 | -0.68 | +0.13 |
| stage4 | 2026-02 | other | 72.4% | 4.51 | 2.55 | +1.42 |
| stage4 | 2026-10 | energy | 6.4% | 18.02 | 1.37 | +1.07 |
| stage4 | 2026-10 | tariff | 20.7% | 6.05 | 1.95 | +0.85 |
| stage4 | 2026-10 | AI | 0.5% | 51.69 | -0.68 | +0.27 |
| stage4 | 2026-10 | other | 72.3% | 7.11 | 2.55 | +3.30 |
| stage1 | 2025-03 | energy | 8.7% | -8.15 | 5.03 | -1.15 |
| stage1 | 2025-03 | tariff | 19.6% | 2.28 | 1.94 | +0.07 |
| stage1 | 2025-03 | AI | 0.7% | 2.12 | -0.19 | +0.02 |
| stage1 | 2025-03 | other | 71.0% | 3.54 | 1.50 | +1.45 |
| stage1 | 2026-02 | energy | 8.1% | 3.32 | 5.03 | -0.14 |
| stage1 | 2026-02 | tariff | 19.6% | 7.71 | 1.94 | +1.13 |
| stage1 | 2026-02 | AI | 0.7% | 6.89 | -0.19 | +0.05 |
| stage1 | 2026-02 | other | 71.7% | 4.28 | 1.50 | +2.00 |
| stage1 | 2026-10 | energy | 7.7% | 58.48 | 5.03 | +4.11 |
| stage1 | 2026-10 | tariff | 20.4% | 9.54 | 1.94 | +1.55 |
| stage1 | 2026-10 | AI | 0.7% | 10.69 | -0.19 | +0.07 |
| stage1 | 2026-10 | other | 71.3% | 10.99 | 1.50 | +6.77 |

### Top 10 contributors to each group's Oct 2026 excess, stage4 central (pp; item share x (item 12m rate - group baseline))

| group | code | item | share | 12m rate | contribution |
|---|---|---|---|---|---|
| energy | 057303 | No. 2 diesel fuel | 0.42% | 115.2 | +0.48 |
| energy | 057104 | Unleaded regular gasoline | 0.42% | 78.5 | +0.33 |
| energy | 057103 | Unleaded premium gasoline | 0.12% | 67.2 | +0.08 |
| energy | 058103 | Other petroleum and coal products, including coke oven produ | 0.22% | 31.6 | +0.07 |
| energy | 054321 | Industrial electric power | 1.56% | -2.0 | -0.05 |
| energy | 057801 | Lubricating oil base stocks | 0.04% | 118.2 | +0.05 |
| energy | 055421 | Natural gas to electric power | 0.29% | 16.9 | +0.04 |
| energy | 057604 | Lubricating and similar oils | 0.11% | 21.8 | +0.02 |
| energy | 054221 | Commercial electric power | 2.95% | 0.6 | -0.02 |
| energy | 057407 | Residual fuels (heavy fuel oils, incl. #5, #6, & other resid | 0.06% | 35.6 | +0.02 |
| tariff | 108905 | Other metal products | 1.64% | 8.8 | +0.11 |
| tariff | 101703 | Hot rolled steel sheet and strip, including tin mill product | 0.29% | 32.9 | +0.09 |
| tariff | 102501 | Aluminum mill shapes | 0.29% | 23.3 | +0.06 |
| tariff | 141205 | Motor vehicles parts | 3.80% | 3.1 | +0.05 |
| tariff | 027A01 | Other oilseed processing | 0.14% | 32.2 | +0.04 |
| tariff | 101707 | Cold rolled steel sheet and strip | 0.10% | 40.1 | +0.04 |
| tariff | 102603 | Nonferrous wire and cable | 0.19% | 19.6 | +0.03 |
| tariff | 022306 | Prepared fresh and frozen seafood | 0.18% | 18.8 | +0.03 |
| tariff | 025401 | Confectionery materials | 0.18% | -13.2 | -0.03 |
| tariff | 072106 | Plastics construction products | 0.75% | 5.7 | +0.03 |
| AI | 117861 | Printed circuit assemblies, loaded boards, modules and consu | 0.16% | 155.7 | +0.24 |
| AI | 115201 | Computer storage devices (except parts, attachments and acce | 0.01% | 80.4 | +0.01 |
| AI | 117849 | Bare printed circuit boards | 0.02% | 46.4 | +0.01 |
| AI | 117603 | Other communications and related equipment, including broadc | 0.11% | 2.3 | +0.00 |
| AI | 117856 | Microwave components, electron tubes, and other electronic c | 0.05% | 5.5 | +0.00 |
| AI | 117847 | Other semiconductor devices, incl. transistors, diodes, and  | 0.04% | -7.9 | -0.00 |
| AI | 117824 | Connectors for electronic circuitry | 0.03% | 5.0 | +0.00 |
| AI | 117853 | Electronic coils, transformers, and other inductors | 0.01% | 7.1 | +0.00 |
| AI | 117839 | Integrated circuit packages, including microprocessors | 0.05% | 0.8 | +0.00 |
| AI | 117822 | Switches, mechanical, for electronic circuitry | 0.00% | 14.8 | +0.00 |
| other | 574101 | Metals, minerals, and ores wholesaling | 0.74% | 92.6 | +0.66 |
| other | 402101 | Portfolio management | 3.33% | 18.5 | +0.53 |
| other | 571102 | Parts and supplies for machinery and equipment wholesaling | 3.51% | 12.4 | +0.34 |
| other | 301202 | Long-distance motor carrying | 1.08% | 28.8 | +0.28 |
| other | 401101 | Securities brokerage, dealing, and investment advice | 1.94% | 9.0 | +0.13 |
| other | 579101 | Other commodities wholesaling | 1.70% | 9.9 | +0.12 |
| other | 578101 | Food wholesaling | 1.76% | 9.6 | +0.12 |
| other | 575101 | Chemicals and allied products wholesaling | 1.35% | 11.4 | +0.12 |
| other | 391101 | Business loans (partial) | 1.00% | -8.4 | -0.11 |
| other | 451101 | Legal services | 2.58% | 6.3 | +0.10 |

### Top 10 contributors to each group's Oct 2026 excess, stage1 central (pp; item share x (item 12m rate - group baseline))

| group | code | item | share | 12m rate | contribution |
|---|---|---|---|---|---|
| energy | 057303 | No. 2 diesel fuel | 1.86% | 115.2 | +2.05 |
| energy | 057104 | Unleaded regular gasoline | 0.86% | 78.5 | +0.64 |
| energy | 057203 | Jet fuel | 0.36% | 106.5 | +0.37 |
| energy | 058103 | Other petroleum and coal products, including coke oven produ | 0.75% | 31.6 | +0.20 |
| energy | 057801 | Lubricating oil base stocks | 0.17% | 118.2 | +0.19 |
| energy | 056101 | Crude petroleum (domestic production) | 0.36% | 52.0 | +0.17 |
| energy | 057103 | Unleaded premium gasoline | 0.24% | 67.2 | +0.15 |
| energy | 057407 | Residual fuels (heavy fuel oils, incl. #5, #6, & other resid | 0.24% | 35.6 | +0.07 |
| energy | 055421 | Natural gas to electric power | 0.62% | 16.9 | +0.07 |
| energy | 057302 | Home heating oil and distillates | 0.06% | 118.5 | +0.06 |
| tariff | 102201 | Primary nonferrous metals | 0.94% | 42.7 | +0.38 |
| tariff | 061403 | Other basic organics | 4.13% | 9.7 | +0.32 |
| tariff | 101703 | Hot rolled steel sheet and strip, including tin mill product | 0.40% | 32.9 | +0.12 |
| tariff | 101707 | Cold rolled steel sheet and strip | 0.25% | 40.1 | +0.10 |
| tariff | 101706 | Steel pipe and tube | 0.27% | 21.7 | +0.05 |
| tariff | 027A01 | Other oilseed processing | 0.17% | 32.2 | +0.05 |
| tariff | 102501 | Aluminum mill shapes | 0.18% | 23.3 | +0.04 |
| tariff | 061302 | Inorganic chemicals, other than alkalies and chlorine | 0.43% | 9.2 | +0.03 |
| tariff | 072106 | Plastics construction products | 0.78% | 5.7 | +0.03 |
| tariff | 117522 | Switchgear and switchboard apparatus | 0.22% | 14.0 | +0.03 |
| AI | 117861 | Printed circuit assemblies, loaded boards, modules and consu | 0.02% | 155.7 | +0.04 |
| AI | 117849 | Bare printed circuit boards | 0.03% | 46.4 | +0.01 |
| AI | 117856 | Microwave components, electron tubes, and other electronic c | 0.08% | 5.5 | +0.00 |
| AI | 115201 | Computer storage devices (except parts, attachments and acce | 0.01% | 80.4 | +0.00 |
| AI | 117603 | Other communications and related equipment, including broadc | 0.14% | 2.3 | +0.00 |
| AI | 115405 | Parts, attachments, and accessories for computer terminals a | 0.11% | 2.3 | +0.00 |
| AI | 117824 | Connectors for electronic circuitry | 0.05% | 5.0 | +0.00 |
| AI | 117847 | Other semiconductor devices, incl. transistors, diodes, and  | 0.03% | -7.9 | -0.00 |
| AI | 117605 | Electronic systems and equipment, n.e.c. | 0.05% | 3.6 | +0.00 |
| AI | 117853 | Electronic coils, transformers, and other inductors | 0.02% | 7.1 | +0.00 |
| other | 574101 | Metals, minerals, and ores wholesaling | 1.13% | 92.6 | +1.03 |
| other | 061401 | Primary basic organic chemicals | 2.22% | 41.6 | +0.89 |
| other | 301202 | Long-distance motor carrying | 2.00% | 28.8 | +0.55 |
| other | 102301 | Copper base scrap | 1.24% | 38.9 | +0.46 |
| other | 101211 | Carbon steel scrap | 2.86% | 14.2 | +0.37 |
| other | 402101 | Portfolio management | 1.40% | 18.5 | +0.24 |
| other | 102302 | Aluminum base scrap | 1.52% | 15.3 | +0.21 |
| other | 302201 | Airline passenger services | 1.28% | 15.0 | +0.17 |
| other | 579101 | Other commodities wholesaling | 2.04% | 9.9 | +0.17 |
| other | 575101 | Chemicals and allied products wholesaling | 1.67% | 11.4 | +0.17 |

### Monthly path of excess, stage 4 central (selected months; full Jan 2018 - Oct 2026 in outputs/group_monthly_path_central_stage4.csv)

| month | energy | tariff | AI | other | total |
|---|---|---|---|---|---|
| 2018-03 | +0.29 | +0.18 | -0.00 | +0.13 | +0.59 |
| 2018-06 | +0.46 | +0.41 | -0.00 | -0.12 | +0.75 |
| 2018-09 | +0.26 | +0.28 | +0.00 | +0.26 | +0.80 |
| 2018-12 | -0.05 | +0.27 | -0.00 | +0.45 | +0.68 |
| 2019-03 | -0.08 | -0.06 | -0.00 | -0.09 | -0.23 |
| 2019-06 | -0.37 | -0.36 | -0.00 | +0.13 | -0.60 |
| 2019-09 | -0.40 | -0.40 | +0.01 | +0.10 | -0.70 |
| 2019-12 | -0.26 | -0.43 | +0.01 | -0.86 | -1.54 |
| 2020-03 | -0.62 | -0.40 | +0.01 | -0.94 | -1.96 |
| 2020-06 | -0.64 | -0.36 | +0.00 | -2.31 | -3.31 |
| 2020-09 | -0.31 | +0.14 | +0.00 | -1.29 | -1.47 |
| 2020-12 | -0.06 | +0.21 | -0.00 | -0.08 | +0.07 |
| 2021-03 | +0.93 | +1.03 | +0.00 | +1.84 | +3.80 |
| 2021-06 | +1.14 | +2.39 | +0.01 | +5.64 | +9.19 |
| 2021-09 | +1.08 | +2.01 | +0.01 | +5.72 | +8.82 |
| 2021-12 | +1.16 | +2.73 | +0.02 | +5.89 | +9.81 |
| 2022-03 | +1.30 | +2.73 | +0.03 | +6.07 | +10.13 |
| 2022-06 | +2.18 | +1.52 | +0.03 | +4.44 | +8.17 |
| 2022-09 | +1.42 | +1.37 | +0.02 | +3.63 | +6.44 |
| 2022-12 | +0.64 | +0.47 | +0.02 | +2.69 | +3.81 |
| 2023-03 | +0.08 | -0.26 | -0.00 | +0.96 | +0.77 |
| 2023-06 | -1.07 | -0.37 | -0.01 | +0.05 | -1.40 |
| 2023-09 | -0.18 | -0.36 | -0.01 | +0.01 | -0.54 |
| 2023-12 | -0.27 | -0.31 | -0.01 | +0.00 | -0.58 |
| 2024-03 | -0.16 | -0.33 | +0.00 | +0.35 | -0.13 |
| 2024-06 | -0.04 | -0.27 | +0.01 | +0.53 | +0.23 |
| 2024-09 | -0.57 | -0.29 | +0.01 | +0.37 | -0.47 |
| 2024-12 | -0.16 | -0.13 | +0.03 | +0.65 | +0.39 |
| 2025-03 | -0.22 | -0.15 | +0.02 | +0.57 | +0.22 |
| 2025-06 | -0.11 | -0.01 | +0.01 | +0.11 | -0.00 |
| 2025-09 | +0.13 | +0.22 | +0.04 | +0.66 | +1.05 |
| 2025-12 | +0.17 | +0.28 | +0.04 | +1.05 | +1.56 |
| 2026-03 | +0.49 | +0.49 | +0.15 | +1.20 | +2.33 |
| 2026-06 | +0.84 | +0.73 | +0.24 | +2.68 | +4.48 |
| 2026-09 | +1.23 | +0.80 | +0.23 | +3.07 | +5.33 |
| 2026-10 | +1.07 | +0.85 | +0.27 | +3.30 | +5.49 |

## Diagnostics
- **Weights.** RI sums are 99.980 (stage 4) and 99.991 (stage 1). Group shares sum to 1.0000 each month.
- **Reproduction gap** (units 12m − published WPUID 12m; target ≤ 0.3 pp):
  - Stage 4: −0.01 (Mar 2025), +0.09 (Feb 2026), −0.16 (Oct 2026). Passes.
  - Stage 1: **+0.33 (Mar 2025)**, −0.16 (Feb 2026), **+0.43 (Oct 2026)**. Fails in Mar 2025 and Oct 2026.
  - Dec 2024 weights (own Dec 2024 unit universe): stage 4 −0.05 / −0.06 / **−0.46**; stage 1 −0.17 / **−0.52** / **−1.65**.
  - A plausible cause: the published index uses the weights in force at each date, and BLS revised the FD–ID allocations effective with January 2026 data (BLS notice), while we apply one weight vintage to every window. Not tested.
- **Unpriced / unmatched weight.** Unpriced in the three focal windows: 0 in stage 4, 0.054 in stage 1. The maximum over Jan 2018–Oct 2026 is 0.892 / 2.382 (Jan 2018), so baseline months have slightly thinner price coverage. Goods with no import-share match: 0 in stage 4, **8.26% of stage 1**, all of it scrap/recyclables (12 units). That is below the 10% flag but close.
- **Near the 15% threshold.** Goods with an import share within 3 pp of 15%: 68 units / RI 5.45 in stage 4, 53 units / RI 3.48 in stage 1. The largest is 108905 Other metal products (stage 4 RI 1.63, import share 0.164). Codex's illustrative test moves it to other, which lowers the stage 4 Oct tariff bar from +0.85 to +0.75 (audit R2).
- **Spot checks.** New raw vs independently saved earlier raw, all identical (`outputs/verify_by_hand.txt`):
  - WPUID54 Oct 2026 169.645
  - WPUID51 Mar 2025 148.872
  - WPU141205 Dec 2025 130.773
  - WPU102302 Oct 2026 436.849
- **Hand recomputation from saved intermediates** (stage 4, Oct 2026):
  - energy 0.0642 × (18.016 − 1.369) = 1.069
  - tariff 0.2075 × (6.046 − 1.947) = 0.850
  - the top-10 AI items sum to 0.270 of the 0.272 group excess
  - all match the script

## Deviations and fallbacks
1. **Coordinator model.** GO asked for a Sonnet coordinator. This session ran on Opus and coordinated directly. To keep usage low, S1 (parsing, fetch, reproduction) was done by the coordinator. Only S2 (NAICS concordance and AI match) went to a Sonnet subagent (`brief_S2_mapping.md`, `notes_S2.md`).
2. **Own-year December weights: not done.** Earlier BLS RI files returned HTTP 403 to scripted download. As a substitute, the `w_dec2024` sensitivity uses the Dec 2024 RI column printed in the same file, with that column's own unit universe: 696 / 576 units, RI 99.950 / 99.979. The audit R1-F02 fix fetched prices for the extra units. 45 / 32 goods units that exist only in Dec 2024 have no NAICS mapping and are tagged other (RI 0.329 / 0.593); 7 / 3 units are unpriced at Dec 2024 (RI 0.099 / 0.155).
3. **Scrap.** S2 mapped 12 scrap/recyclable codes to BEA's "Scrap" commodity S00401. Its import share, 6.7bn / 17.5bn = 0.384, rests on BEA booking only secondary scrap sales as domestic output, which looks like an I-O artifact. Scrap has no NAICS industry, so the GO fallback applies: unmatched → other, weight reported (8.26% of stage 1, 0 in stage 4). `scrap_bea` shows the alternative. See Judgment calls for Eli.
4. **BLS concordance not used.** BLS lists an Industry–Commodity Concordance workbook (bls.gov/ppi/tables/, per audit R1). Neither S2 nor Codex could retrieve it, and scripted bls.gov downloads return 403. S2 assigned NAICS from item names: 409 high, 110 medium and 32 low confidence. Audit R1 corrected 7 codes from the BLS published children and the Census 2017 manual. 061401 Primary basic organic chemicals → 325110;324110 (import share 0.098, now other; stage 1 Oct tariff −1.06 pp). 108905 Other metal products → 336370;332721;332999 (0.164, still tariff but near the threshold). The rest were invalid-code corrections that change no tag.
5. **Freight sensitivity** = codes 301* (rail, truck, water, air freight, postal/courier, pipeline). Arrangement, warehousing and cargo handling stay in other.
6. **NAICS level.** 141205 Motor vehicle parts (stage 4 RI 3.78, the largest goods unit) is matched at 4-digit 3363 (import share 0.299).

## Caveats
- PPI prices domestic producers only. Tariffs show up indirectly, through import-competing domestic prices and imported inputs.
- "Tariff" means import-exposed (BEA 2017 shares). Whether each item was actually tariffed is not verified.
- Oct 2026 is preliminary.
- Trade-services units (wholesale margins) are "other". 574101 Metals, minerals and ores wholesaling (+92.6% y/y) is the largest single contributor to stage 4 "other" in Oct 2026 (+0.66 pp), even though its price is metal-linked.
- AI is about 0.5% of stage 4 weight, so its bar is small even with large rates.

## Worth a look
- WPU117861 Printed circuit assemblies is up 155.7% y/y in Oct 2026 (index 104.6 → 267.4). It supplies 89.9% of the stage-4 AI excess (+0.24 of +0.27). The full BLS group 1178, including 117861, is up 31.7% (WPU1178 71.05 → 93.61). A real price surge vs. a sample or quality change is unverified. Check whether this is a real price surge or a sample/quality issue.
- Diesel (+115% y/y), jet fuel (+107%) and gasoline (+79%) drive the stage-1 energy excess of +4.11.
- 574101 Metals, minerals and ores wholesaling margins nearly doubled (index 251.6 → 484.5, Oct 2025 → Oct 2026), with +25% from Aug to Oct 2026 alone (388.0 → 484.5).
- 402101 Portfolio management (+18.5% y/y, stage 4 share 3.3%) is the second-largest "other" contributor. The index measures management fees, which often move with the value of assets under management.
- The stage-4 monthly path peaks at +10.26 pp (Jan 2022), versus +5.49 now.

## Judgment calls for Eli
1. **Scrap tagging (stage 1 only).** Central treats scrap as other (GO fallback). BEA's scrap commodity would make it tariff and raise stage 1's Oct 2026 tariff bar by +1.77 pp (+1.55 → +3.32). Stage 4 is unaffected.
2. **Stage 1 reproduction gap** is +0.43 pp in Oct 2026, above the 0.3 pp check. Accept it, or treat stage 1 as indicative only.
3. **No software in either stage**, so AI central covers hardware only. AI is 0.5–0.7% of the weight.
4. **Engineering services (453201)** enters "AI buildout" as a whole, although only the utility/power-engineering line is AI-linked. Across the three focal months the buildout version changes AI by at most +0.08 pp (stage 1 Oct: +0.07 → +0.15); over the full monthly path the maximum is +0.20 pp (stage 1, Jul 2025).

## Coordinator review
- **Verified:** the reproduction check, 3 hand recomputations and 4 raw spot checks (see Diagnostics). I also checked the top-18 goods units by weight in each stage for NAICS and import share plausibility (e.g. 331110 steel 0.249, 336111 autos 0.671, 334413 semiconductors 0.375). And I checked the energy-block = group-05 identity.
- **Corrected:** the S2 output column header `ai_list(central/buildout)` was read by prefix. Scrap was moved from tariff to other per the GO fallback (deviation 3). Audit R1: 7 NAICS corrections, 381102 added to buildout, Dec 2024 universe fixed, and two Worth-a-look figures and counts fixed (see `06_Audits/18_upstream_ppi_tagged/R1_claude.md`).
- **Not checked:** the 6-digit NAICS 2017 validity of S2's codes, and the med/low-confidence rows individually.
