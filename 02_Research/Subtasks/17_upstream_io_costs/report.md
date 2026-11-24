Status: verified, not audited (no Codex audit this run, per GO.md). Coordinator checks below. Nov 17, 2026.

# 17: Upstream purchased-input cost pressure by shock group (Method C, input-output)

**Question (GO.md):** for each 2B left-chart shock group, how fast are the purchased input costs of the industries that produce it rising, relative to their own 2018–19 pace, in Mar 2025, Feb 2026 and Oct 2026?

**Script:** `code/io_input_costs.py` (`--fetch` downloads; otherwise reads raw only). Tables: `code/report_tables.py` → `outputs/report_tables.md`. Hand check: `code/verify_by_hand.py`. All three run with `python3 -I` from the project root.

**Data:** BEA 2017 detailed benchmark use, make and import matrices and the 2017 PCE bridge (all before redefinitions, producers' prices; retrieved Nov 14, reused from `03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/`). BEA summary use and make for 2023 (same zip) plus the summary import matrix 1997–2023 (`03_Data/Raw/BEA_IO_summary_2026-11-17/`). BLS PPI industry indexes (PCU, NSA), 290 series: 287 fetched Nov 17 into `03_Data/Raw/BLS_PPI_io_inputs_2026-11-17/`, plus 3 reused from `BLS_PPI_hospitals_2026-11-15` and `BLS_PPI_ai_basket_2026-11-16`. Data run 2017-01 to 2026-10. **Jul–Oct 2026 PPI values are preliminary**, and BLS revises them 4 months after release. Leaf weights and tags come from C_common/G. The group PCE shares match G exactly (Oct 2026: energy 0.1809, tariff 0.1107, AI 0.0196, else 0.6888).

## Method as run
1. **Leaves:** 149 core PCE leaves with `tag_final`. Leaf weights are start-of-window nominal PCE weights (t−12), the same as G. Each leaf maps to its 2017 bridge line(s) through `bridge_lines` in `proposed_tags.csv`.
2. **Leaf → inputs:** from the 2017 bridge, each leaf's input vector x_i = Σ_c PV_ic · M[:, c], plus the leaf's wholesale, retail and transport margins as three separate inputs (D4).
   - **Central:** M = L_d − I, the domestic commodity-by-commodity total requirements excluding the unit of own output.
   - **Direct:** M = A_d.
   - **Summary:** M = L_d − I built from the 2023 summary tables (73 commodities), with the 2017 bridge aggregated to summary codes.
   - Tables are commodity-by-commodity under the industry-technology assumption: A = (U/g)(V/q), A_d = (max(U − M_imp, 0)/g)(V/q).
3. **Pricing:** each input gets one PCU industry index under rule 4 (`outputs/ppi_concordance.csv`). Unpriced inputs are dropped and shares renormalised within each leaf. Margins use PCUAWHLTRAWHLTR (wholesale), PCUARETTRARETTR (retail) and PCUATRNWRATRNWR (transportation & warehousing).
4. **Group rate:** R_g(t) = Σ_{i∈g} w_i(t−12) · Σ_j s_ij · PPI12m_j(t) / Σ w_i. Baseline = mean of R_g over 2018-01..2019-12. Excess = R_g − baseline.
5. **Contributions:**
   - (a) plain: s_g · excess.
   - (b) scaled: s_g · θ_g · excess. Here s_g is the group's share of core PCE (start-of-window weights) and θ_g is the leaf-weighted purchased-input share of purchasers' value: domestic direct inputs plus margins, from the 2017 use table (2023 for the summary run). An incl.-imports θ is in `summary_table.csv`.

## Results

### Central (2017 detail, domestic total requirements): 12m purchased-input cost inflation (%), and excess over the group's own 2018–19 average (pp)

| Group | 2018-19 avg | Mar 2025 | Feb 2026 | Oct 2026 | Excess Mar 25 | Excess Feb 26 | Excess Oct 26 | Input share θ | Dropped wt |
|---|---|---|---|---|---|---|---|---|---|
| Energy-exposed | 2.28 | 2.90 | 4.15 | 9.65 | 0.63 | 1.87 | 7.37 | 0.51 | 36% ⚑ |
| Tariff-exposed | 2.25 | 2.67 | 5.31 | 7.43 | 0.41 | 3.06 | 5.17 | 0.78 | 8% |
| AI-related | 2.04 | 3.75 | 5.18 | 6.58 | 1.71 | 3.14 | 4.54 | 0.59 | 17% ⚑ |
| Everything else | 2.35 | 3.25 | 4.19 | 7.69 | 0.91 | 1.84 | 5.34 | 0.33 | 47% ⚑ |

⚑ = dropped weight above 15% (rule 4 flag). Dropped weight is the share of the group's purchased inputs with no PPI, Oct 2026 weights.

Contributions, pp:

| Group | PCE share Oct 26 | (a) plain Mar 25 | (a) Feb 26 | (a) Oct 26 | (b) scaled Mar 25 | (b) Feb 26 | (b) Oct 26 |
|---|---|---|---|---|---|---|---|
| Energy-exposed | 0.181 | 0.12 | 0.34 | 1.33 | 0.06 | 0.17 | 0.69 |
| Tariff-exposed | 0.111 | 0.05 | 0.34 | 0.57 | 0.04 | 0.26 | 0.45 |
| AI-related | 0.020 | 0.03 | 0.06 | 0.09 | 0.02 | 0.04 | 0.05 |
| Everything else | 0.689 | 0.62 | 1.27 | 3.68 | 0.21 | 0.42 | 1.23 |
| **Total** | 1.000 | 0.82 | 2.01 | 5.67 | 0.32 | 0.90 | 2.42 |

### Sensitivity 1: direct requirements (first-tier suppliers only)

| Group | 2018-19 avg | Mar 2025 | Feb 2026 | Oct 2026 | Excess Mar 25 | Excess Feb 26 | Excess Oct 26 | θ | Dropped wt |
|---|---|---|---|---|---|---|---|---|---|
| Energy-exposed | 2.27 | 2.79 | 3.99 | 9.16 | 0.52 | 1.71 | 6.89 | 0.51 | 36% ⚑ |
| Tariff-exposed | 2.22 | 2.59 | 5.25 | 6.72 | 0.37 | 3.03 | 4.50 | 0.78 | 3% |
| AI-related | 2.04 | 3.85 | 5.29 | 6.30 | 1.81 | 3.25 | 4.26 | 0.59 | 12% |
| Everything else | 2.34 | 3.34 | 4.32 | 6.29 | 1.00 | 1.98 | 3.95 | 0.33 | 53% ⚑ |

| Group | (a) Mar 25 | (a) Feb 26 | (a) Oct 26 | (b) Mar 25 | (b) Feb 26 | (b) Oct 26 |
|---|---|---|---|---|---|---|
| Energy-exposed | 0.10 | 0.31 | 1.25 | 0.05 | 0.16 | 0.64 |
| Tariff-exposed | 0.04 | 0.34 | 0.50 | 0.03 | 0.26 | 0.39 |
| AI-related | 0.04 | 0.06 | 0.08 | 0.02 | 0.04 | 0.05 |
| Everything else | 0.68 | 1.36 | 2.72 | 0.23 | 0.45 | 0.91 |
| **Total** | 0.86 | 2.07 | 4.55 | 0.33 | 0.91 | 1.99 |

### Sensitivity 2: summary annual tables (2023, 73 commodities)

| Group | 2018-19 avg | Mar 2025 | Feb 2026 | Oct 2026 | Excess Mar 25 | Excess Feb 26 | Excess Oct 26 | θ | Dropped wt |
|---|---|---|---|---|---|---|---|---|---|
| Energy-exposed | 2.61 | 2.73 | 4.80 | 11.32 | 0.12 | 2.20 | 8.71 | 0.51 | 44% ⚑ |
| Tariff-exposed | 2.37 | 2.82 | 5.48 | 7.68 | 0.45 | 3.11 | 5.31 | 0.78 | 11% |
| AI-related | 2.26 | 3.68 | 5.49 | 7.25 | 1.42 | 3.22 | 4.99 | 0.55 | 21% ⚑ |
| Everything else | 2.70 | 3.71 | 4.93 | 9.32 | 1.01 | 2.24 | 6.62 | 0.34 | 57% ⚑ |

| Group | (a) Mar 25 | (a) Feb 26 | (a) Oct 26 | (b) Mar 25 | (b) Feb 26 | (b) Oct 26 |
|---|---|---|---|---|---|---|
| Energy-exposed | 0.02 | 0.40 | 1.58 | 0.01 | 0.20 | 0.81 |
| Tariff-exposed | 0.05 | 0.35 | 0.59 | 0.04 | 0.27 | 0.46 |
| AI-related | 0.03 | 0.06 | 0.10 | 0.02 | 0.04 | 0.05 |
| Everything else | 0.69 | 1.54 | 4.56 | 0.24 | 0.53 | 1.57 |
| **Total** | 0.79 | 2.35 | 6.82 | 0.31 | 1.04 | 2.90 |

### Stability across sensitivities, Oct 2026: each group's share of the total contribution (%)

| Version | Measure | Energy | Tariff | AI | Else | Total pp |
|---|---|---|---|---|---|---|
| central | (a) plain | 24 | 10 | 2 | 65 | 5.67 |
| direct | (a) plain | 27 | 11 | 2 | 60 | 4.55 |
| summary | (a) plain | 23 | 9 | 1 | 67 | 6.82 |
| central | (b) scaled | 28 | 18 | 2 | 51 | 2.42 |
| direct | (b) scaled | 32 | 19 | 2 | 46 | 1.99 |
| summary | (b) scaled | 28 | 16 | 2 | 54 | 2.90 |

**Which version is most stable (flag only, no recommendation):**
- *Group excess rates.* Across the three sensitivities, Oct 2026 excess varies least for tariff (4.50–5.31) and AI (4.26–4.99). It varies most for everything else (3.95–6.62) and energy (6.89–8.71), the two groups with the most dropped weight.
- *Totals.* (a) runs 4.55–6.82 pp and (b) runs 1.99–2.90 pp. Both span about ±20% of central.
- *Group shares of the total.* (a) and (b) move by similar amounts (4–8 points per group).
- *Rank order.* Energy has the largest excess in every version. The order of the other three changes: in direct, untagged falls to last.

### Top 10 inputs by contribution to each group's Oct 2026 excess (central)
contribution_j = share_j(Oct 26) × r_j(Oct 26) − mean over 2018–19 of share_j(t) × r_j(t). The contributions sum exactly to the group excess (asserted in the script). The columns below are the input's share, its 12m %, its 2018–19 average 12m %, and its contribution in pp of the group's input-cost excess.

**Energy-exposed** (excess 7.37)
| Input | PPI | Share | 12m Oct 26 | 18-19 avg | Contrib |
|---|---|---|---|---|---|
| 324110 refineries | PCU32411-32411- | 0.034 | 88.0 | 6.6 | 2.75 |
| 211000 oil & gas extraction | PCU211---211--- | 0.014 | 45.2 | −1.3 | 0.65 |
| Retail margin | PCUARETTRARETTR | 0.134 | 5.5 | 2.0 | 0.47 |
| 484000 truck transport | PCU484---484--- | 0.020 | 20.0 | 4.5 | 0.30 |
| 48A000 other transport (3-digit→sector) | PCUATRNWRATRNWR | 0.027 | 14.0 | 3.8 | 0.29 |
| 221100 electric power | PCU2211--2211-- | 0.048 | 6.5 | 2.4 | 0.20 |
| Wholesale margin | PCUAWHLTRAWHLTR | 0.029 | 8.9 | 2.8 | 0.18 |
| 424A00 nondurable wholesalers | PCU424---424--- | 0.032 | 7.5 | 2.4 | 0.17 |
| 424700 petroleum wholesalers | PCU4247--4247-- | 0.011 | 9.7 | −3.3 | 0.14 |
| 325110 petrochemicals | PCU32511-32511- | 0.004 | 31.9 | −0.3 | 0.14 |

**Tariff-exposed** (excess 5.17)
| Input | PPI | Share | 12m Oct 26 | 18-19 avg | Contrib |
|---|---|---|---|---|---|
| Retail margin | PCUARETTRARETTR | 0.487 | 5.5 | 2.0 | 1.69 |
| Wholesale margin | PCUAWHLTRAWHLTR | 0.152 | 8.9 | 2.8 | 0.93 |
| Transport margin | PCUATRNWRATRNWR | 0.032 | 14.0 | 3.8 | 0.34 |
| 331110 iron & steel mills | PCU3311--3311-- | 0.010 | 33.7 | 4.9 | 0.29 |
| 324110 refineries | PCU32411-32411- | 0.003 | 88.0 | 6.6 | 0.24 |
| 334418 printed circuit assembly | PCU334418334418 | 0.001 | 150.6 | −0.6 | 0.21 |
| 484000 truck transport | PCU484---484--- | 0.009 | 20.0 | 4.5 | 0.14 |
| 423A00 durable wholesalers | PCU423---423--- | 0.013 | 10.3 | 3.2 | 0.10 |
| 325110 petrochemicals | PCU32511-32511- | 0.003 | 31.9 | −0.3 | 0.09 |
| 211000 oil & gas extraction | PCU211---211--- | 0.002 | 45.2 | −1.3 | 0.09 |

**AI-related** (excess 4.54)
| Input | PPI | Share | 12m Oct 26 | 18-19 avg | Contrib |
|---|---|---|---|---|---|
| Wholesale margin | PCUAWHLTRAWHLTR | 0.269 | 8.9 | 2.8 | 1.63 |
| Retail margin | PCUARETTRARETTR | 0.354 | 5.5 | 2.0 | 1.22 |
| 334418 printed circuit assembly | PCU334418334418 | 0.005 | 150.6 | −0.6 | 0.74 |
| 511200 software publishers | PCU51321-51321- | 0.072 | −5.6 | −0.5 | −0.37 |
| 324110 refineries | PCU32411-32411- | 0.003 | 88.0 | 6.6 | 0.25 |
| 33441A semiconductors & components | PCU33441-33441- | 0.004 | 30.6 | −1.3 | 0.14 |
| 561300 employment services | PCU5613--5613-- | 0.045 | 3.8 | 1.3 | 0.12 |
| 423400 prof./comm. equip. wholesalers | PCU4234--4234-- | 0.022 | −2.1 | 2.9 | −0.10 |
| 541100 legal services | PCU5411--5411-- | 0.030 | 6.3 | 3.1 | 0.10 |
| Transport margin | PCUATRNWRATRNWR | 0.009 | 14.0 | 3.8 | 0.09 |

**Everything else** (excess 5.34)
| Input | PPI | Share | 12m Oct 26 | 18-19 avg | Contrib |
|---|---|---|---|---|---|
| 324110 refineries | PCU32411-32411- | 0.019 | 88.0 | 6.6 | 1.53 |
| 211000 oil & gas extraction | PCU211---211--- | 0.009 | 45.2 | −1.3 | 0.40 |
| 444000 building material retailers | PCU444---444--- | 0.017 | 23.8 | 3.2 | 0.36 |
| 484000 truck transport | PCU484---484--- | 0.013 | 20.0 | 4.5 | 0.20 |
| Retail margin | PCUARETTRARETTR | 0.058 | 5.5 | 2.0 | 0.20 |
| 523900 other financial investment | PCU523---523--- | 0.028 | 12.1 | 5.5 | 0.19 |
| 561300 employment services | PCU5613--5613-- | 0.057 | 3.8 | 1.3 | 0.14 |
| 523A00 securities/commodity contracts | PCU523---523--- | 0.019 | 12.1 | 5.5 | 0.13 |
| Wholesale margin | PCUAWHLTRAWHLTR | 0.021 | 8.9 | 2.8 | 0.13 |
| 481000 air transport | PCU481---481--- | 0.011 | 14.9 | 3.2 | 0.12 |

Top 10 lists for the two sensitivities are in `outputs/top10_inputs_oct2026.csv`.

### Monthly path, central (12m %, quarter-end months; full Jan 2018 – Oct 2026 in `outputs/group_monthly_path_central.csv`, including excess and contributions)

| Month | Energy | Tariff | AI | Else |
|---|---|---|---|---|
| 2018-06 | 3.83 | 2.85 | 2.22 | 3.59 |
| 2018-12 | 3.00 | 3.20 | 2.31 | 2.79 |
| 2019-06 | 0.85 | 1.83 | 1.92 | 1.19 |
| 2019-12 | 0.70 | 1.00 | 1.86 | 1.16 |
| 2020-06 | −1.38 | 0.79 | 1.23 | −0.80 |
| 2021-06 | 13.89 | 12.79 | 9.61 | 12.40 |
| 2022-03 | 15.29 | 16.63 | 13.82 | 11.75 |
| 2022-12 | 8.36 | 6.04 | 5.88 | 6.35 |
| 2023-06 | −2.41 | −0.57 | 0.83 | 0.28 |
| 2024-06 | 2.12 | 0.75 | 2.15 | 2.58 |
| 2024-12 | 2.43 | 1.42 | 2.47 | 2.91 |
| 2025-03 | 2.90 | 2.67 | 3.75 | 3.25 |
| 2025-09 | 3.41 | 4.13 | 3.98 | 3.22 |
| 2025-12 | 3.44 | 4.75 | 4.42 | 3.66 |
| 2026-03 | 4.85 | 5.38 | 4.89 | 4.65 |
| 2026-06 | 7.08 | 5.89 | 6.28 | 6.53 |
| 2026-09 | 8.90 | 6.70 | 6.51 | 7.46 |
| 2026-10 | 9.65 | 7.43 | 6.58 | 7.69 |

## Diagnostics
- **Shares sum to 1:** asserted for every leaf after renormalising, and for every group over all inputs and over priced inputs, at each key month.
- **Contributions add up:** the top-input contributions sum to the group excess (asserted).
- **BEA table build checked against BEA:** BEA's published 2017 CxC total-requirements table was compared with my build from use/make. The median column-sum gap is 0.035 against my total (incl. imports) inverse and 0.253 against the domestic inverse. Mean column sums: BEA 2.098, built total 2.063, built domestic 1.815. So BEA's published TR includes imported inputs, which is why the domestic L is built here.
- **Concordance, detail level** (402 commodities + 3 margins), by count: 225 exact; 7 exact via the NAICS-2022 crosswalk; 28 / 16 / 14 at the 5- / 4- / 3-digit level; 15 sector aggregate; 97 dropped (84 with no PPI, 13 with no NAICS: government, scrap, used goods, noncomparable imports, rest-of-world adjustment).
- **Concordance, summary level** (73 + 3): 12 exact; 1 via crosswalk; 21 broader; 12 sector aggregate; 27 dropped.
- **Weight by match level** (Oct 2026, central, share of all purchased inputs):

  | Match | Energy | Tariff | AI | Else |
  |---|---|---|---|---|
  | exact | 34.3% | 23.2% | 20.0% | 30.3% |
  | crosswalk | 0.9% | 0.1% | 6.5% | 1.0% |
  | broader | 10.0% | 5.9% | 2.9% | 12.2% |
  | sector aggregate | 3.1% | 0.7% | 0.7% | 1.9% |
  | margin index | 15.5% | 62.1% | 52.5% | 7.5% |
  | **dropped** | 36.2% | 8.0% | 17.5% | 47.1% |

  Other versions: `outputs/report_tables.md`.
- **Largest dropped inputs** (central, Oct 2026; share of the group's purchased inputs; `outputs/diag_top_dropped_inputs_oct2026.csv`):
  - Energy: 531ORE other real estate 9.0%, 550000 management of companies 5.2%, 541800 advertising 2.5%, 52A000 banking 1.9%.
  - Else: 531ORE 9.1%, 522A00 non-bank credit 6.2%, 230302 repair construction 4.5%, 52A000 4.4%, 550000 3.5%.
  - AI: 531ORE 4.2%, 541800 2.5%, 550000 2.1%.
  - Why they drop: there is no PCU industry index at any NAICS level for these codes, or their NAICS codes share only a 2-digit prefix (e.g. 52A000 = 521 + 5221).
- **Series dropped for incomplete data** (not complete 2017-01..2026-10), so the rule walked up a level: PCU33141-33141-, PCU331410331410, PCU332114332114.
- **PPI spot checks against the raw JSON** (`outputs/diag_ppi_spot_checks.csv`), all exact:
  - PCUAWHLTRAWHLTR Oct 2026: 223.337
  - PCU32411-32411- Oct 2025: 288.364
  - PCU33331-33331- Jun 2019: 125.8
- **Rerun:** the run from raw without `--fetch` reproduces byte-identical `summary_table.csv`, `group_monthly_all_versions.csv` and `top10_inputs_oct2026.csv`.

## Deviations and fallbacks (logged per GO.md)
1. **Before redefinitions, not after.** BEA's import matrices exist only before redefinitions, and BEA's published TR includes imports (see Diagnostics). The domestic tables are therefore built from the before-redefinitions use, make and import matrices. Producers' prices as specified.
2. **Domestic use clipped at 0.** 85 detail cells of U − M_imp are negative: imports exceed use for 325414 biological products in a few industries, plus BEA's negative used-goods entries. Those cells are set to 0. Their summed coefficient is about 0.1 (summed over 402 columns).
3. **Rule 4, "next broader level", applied repeatedly.** The rule walks 6 → 5 → 4 → 3 digits, then uses the BLS sector aggregate where one exists (42, 44–45, 48–49, 51, 21, 31–33). Multi-NAICS BEA codes start from the common prefix of their NAICS codes.
   - A NAICS 2017→2022 prefix crosswalk handles codes BLS has renamed (retail 446/447/448/451/452/453/442/443; information 5111/5112/5151/5152/5173/5191/51913).
   - A series qualifies only with complete data for 2017-01..2026-10.
   - Applied literally (one step only), the rule would drop much more weight.
4. **Raw reuse.** No new `BEA_IO_2017_detail_<date>/` folder was made: the identical 2017 detail files already sit in `03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/` (read-only). The latest summary tables available were the 2023 tables in BEA's AllTablesIO zip (retrieved Nov 14). I could not find a 2024+ summary file at BEA's URL patterns: the zip URL now serves an HTML page.
5. **Summary bridge.** BEA's summary PCE bridge was not available, so the summary run aggregates the 2017 detail bridge to summary codes. Only the IO structure changes in sensitivity 2.
6. **θ for version (b).** Domestic direct inputs plus margins, i.e. what is priced. The incl.-imports θ is reported in `summary_table.csv`. It is 0.02–0.05 higher by group (central: energy 0.55, tariff 0.82, AI 0.60, else 0.36).
7. **Execution.** The coordinator (Opus) did the S1/S2 work inline, with no subagents, to keep usage low.
   - The first BLS fetch ran unregistered because of a key-parsing bug (`export` prefix), so BLS returned only 25 series and 10 years. Those files were deleted and the full refetch is the only BLS raw in the folder.

## Caveats
- **2017 weights.** The IO structure (2017; 2023 in the summary run) predates 2025–26. Input mixes and import shares have shifted since, especially for tariff-exposed goods.
- **Imports excluded.** PPI prices domestic producers only, and BLS import price indexes exclude tariffs. Tariff costs reach these numbers only through domestic prices and trade margins.
- **Labour and value added excluded.** Purchased inputs only, so service groups understate cost pressure: θ is 0.33 for everything else vs 0.78 for tariff.
- **Owners' equivalent rent.** OER and rent leaves are priced through the inputs to housing (repairs, insurance, real-estate services, mostly dropped), a weak proxy for rents.
- **Dropped weight is large where flagged.** Renormalising assumes the unpriced inputs (real estate, management of companies, finance, construction, advertising) move like the priced ones. In an energy-led episode, the priced set tilts toward energy and goods.
- **Trade margins dominate two groups.** They are 62% of tariff-group inputs and 52% of AI-group inputs (central). The trade PPIs measure margins (selling price minus acquisition cost), not purchased-input prices in the usual sense.
- **PPI vintage.** Jul–Oct 2026 PPI are preliminary.

## Coordinator review
- **Hand check** (`code/verify_by_hand.py`): plain-loop recomputation from the saved intermediates (leaf shares, concordance, PPI 12m rates, leaf weights, tags, θ) matches the script to 1e-6 on four numbers:
  - central energy Oct 2026 rate 9.65176
  - AI 2018–19 baseline 2.04140
  - everything-else plain contribution Feb 2026 1.26762
  - everything-else scaled contribution Feb 2026 0.42353
- **Cross-checks against earlier project pulls:**
  - PCU33441-33441- Oct 2026 12m is 30.64%, matching `10_slide2_research/outputs/M_upstream_by_shock.csv`.
  - The large energy PPIs are consistent with M's final-demand energy +37.0% y/y and processed fuels +43.1%.
  - Group PCE shares match G.
- **Not checked:** PPI values against the BLS website, beyond the raw JSON; whether BLS revised history when it re-coded the NAICS-2022 series.

### Worth a look
- **PCU334418 printed circuit assembly:** +150.6% y/y in Oct 2026, peak 164.8% in Jun 2026, 2018–19 average −0.6%. It is the AI group's largest non-margin contributor (0.74 pp at a 0.5% share). Worth confirming what BLS prices there (possibly memory-module assemblies) before citing it.
- **Trade-margin PPIs:** wholesale 8.9% y/y and retail 5.5% (2018–19 averages 2.8% and 2.0%). Both are the highest since Nov 2022. They drive most of the tariff and AI bars.
- **Refinery PPI:** +88.0% y/y, highest since Nov 2021.
- **AI group in Mar 2025:** input-cost excess was already 1.7 pp, the largest of the four groups at that date (direct 1.8; summary 1.4).
- **Subtask 08's energy exposure:** it used A = I − TR⁻¹ from BEA's published TR, which includes imported inputs. That suits an all-origin energy cost share, but it is not domestic. Noted for consistency, not as an error.

## Judgment calls for Eli
1. **Dropped-weight flags.** Energy (36%), AI (17%) and everything else (47%) are above the 15% threshold in the central run. The same holds for energy and else in the direct run (AI 12%), and for energy, AI and else in the summary run. Accept as is with the caveat, or allow a narrow fix? For example, price multi-NAICS codes with their largest component's PPI (52A000 → 5221 banking). That fix is outside rule 4 as written.
2. **What the AI and tariff bars measure.** Most of both is trade-margin PPI, not chip, metal or other goods input prices. Does that fit the 2B right chart's purpose?
3. **θ basis for version (b).** Domestic (used) or incl. imports (reported)?
4. **Summary vintage.** The latest summary tables I could reach are 2023. Acceptable, or should I look further for a 2024 release?
