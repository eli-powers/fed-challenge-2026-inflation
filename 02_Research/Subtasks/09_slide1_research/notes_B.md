# Agent B notes: core CPI–PCE gap reconciliation (Sep and Oct 2026)

Run: `python3 -I "02_Research/Subtasks/09_slide1_research/code/B_core_gap.py"` from the project root (about 2 s; reads only saved files, writes only to `09_slide1_research/outputs/`). Code: `code/B_common.py` (engine), `code/B_mapping.py` (all mapping assumptions), `code/B_core_gap.py` (runs and CSVs).

Tags: [O] opened and checked, [S] search snippet only, [2] secondary. Every number below comes from the CSVs, the script, or a raw file named in `sources_B.md`.

## Outputs
| File | What it holds |
|---|---|
| `outputs/B_core_gap_sep.csv` | Sep 2026 core, 12m. Columns: effect, item, pp (BEA 9.1U convention), method, source, pp_centered_alt, basis. Includes published rows, subtotals and a check row. |
| `outputs/B_core_gap_oct.csv` | Oct 2026 core. Two blocks: `approx_12m` (PRIMARY) and `3m_annualized` (ALTERNATE). |
| `outputs/B_headline_check.csv` | Headline, our method vs BEA Table 9.1U: summed monthly effects for Dec 2025–Sep 2026, a by-month gap, a single-window Nov 2025→Sep 2026 run, and a headline 12m run. |
| `outputs/B_theme_summary.csv` | Rows grouped by theme (shelter, health care, financial, software and so on), both conventions. This feeds the spoken-line candidates. |
| `outputs/B_sensitivity_sep.csv` | Sep core: main run vs CPI SA components vs no medical third-party split. |
| `outputs/B_mapping_groups.csv` | Every matched group, with its PCE lines and CPI items, plus the PCE-only and CPI-only lists. |
| `outputs/B_group_detail_*.csv` | For each group: PCE and CPI shares, in-scope shares and changes, plus metadata (k, matched means, imputed CPI leaves). |

## Method (how each effect is defined)
The gap is published PCE minus published CPI, in pp. The identity is exact by construction, and the check row in each CSV confirms it.
- **Formula** = the published PCE change (chained Fisher, U20404 line 374 or 1) minus a fixed-weight Laspeyres built from BEA "atoms" at base-month nominal shares (U20405).
  - Atoms are the leaves of BEA's U20404 hierarchy (`04_oct_pce_build/outputs/A_hierarchy.csv`). Net items enter as gross components with "Less:" lines at negative weight: 146 less 149, 334 less 338, plus 156, 272 and 342 as single atoms. BEA publishes no price index for lines 145 and 333.
  - Atom nominal shares close to the published aggregate within 0.0000% in every run.
- **Weight** (matched groups): (PCE in-scope share − CPI share) × CPI group change.
- **Price** (matched groups): PCE in-scope share × (PCE group change − CPI group change). Airfares fall here, because PCE prices them with a PPI.
- **Scope, PCE-only**: PCE share × item change. This covers third-party-paid medical, imputed financial services, portfolio management, NPISH and the rest.
- **Scope, CPI-only**: −(CPI share × item change).
- **Other**: the CPI's January 2026 weight update. Our CPI aggregate chains two segments (2023 weights through Dec 2025, 2024 weights after). The row is the single-base Laspeyres minus that chained aggregate.
- **Residual**: our CPI leaf aggregate minus the published CPI. It is the only unexplained row; the PCE side has none, because the formula row absorbs it exactly.
- **Two attributions of the same identity.**
  - `pp` follows BEA's Table 9.1U convention: raw shares of the full index, with item changes not centred. This is the convention validated against 9.1U below.
  - `pp_centered_alt` renormalises shares within the matched set and measures each item's change relative to the matched-set mean. Both sum to the same gap, but they **split it very differently** between weight and scope (see Worth a look #1).
  - BEA convention confirmed by the 9.1U match: our shelter weight effect is −0.526 against BEA's −0.52, and FSWP scope is 0.077 against 0.08. A centred version gave +0.07 for shelter, which is clearly not BEA's convention [O, B_headline_check.csv].

## Mapping assumptions (full list in `code/B_mapping.py` and `outputs/B_mapping_groups.csv`)
- **Matching.** 63 groups (7 of them partial-scope medical; in core runs the food/energy groups drop out or become core-definition scope) at roughly the published CPI-stratum level. The basis is the BLS PCE–CPI ELI concordance [O] `03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv` (last modified Apr 5 2024), aggregated, plus judgment where the concordance is ELI-level or silent. Each group's note says which applies.
- **Core definitions**, which differ between the two indexes:
  - Core PCE excludes U20404 lines 73–103 (off-premises food and beverages, including alcohol), 113–119 and 169–171. This is the pipeline's BEA line rule.
  - Core CPI excludes the "Food" subtree and six energy leaves, so alcoholic beverages stay in core CPI.
  - As a result, restaurant meals (FAFH group) are in core PCE only and alcohol at home is in core CPI only. Both are reported as scope rows tagged "[core-definition]".
  - RI Table 1 indents "Alcoholic beverages" under "Food". The script overrides that so alcohol stays in core: the core RI leaf sum is 79.917 against BLS's published 79.919 (Dec 2025).
- **Partial-scope medical.** This covers Rx, physicians, dental, other professional/home health/labs, hospitals, nursing homes, and individual & family services.
  - PCE includes payments by employers, insurers and government [O, NIPA Handbook ch.5 p.5-2 (PDF p.96)]. The CPI covers out-of-pocket spending [O, Handbook PDF p.56].
  - Assumption: in-scope PCE share = k × CPI share, where k is PCE share per CPI RI point over the fully matched groups (k = 0.648 for core Sep, 0.738 for headline). The remainder is reported as PCE-only scope, "[third-party-paid portion]".
  - BEA's own split is unpublished. Sensitivity with no split (`B_sensitivity_sep.csv`): weight +0.280, price −0.156 and PCE-only scope +0.584, against main-run values of −0.283, +0.049 and +0.942.
- **Health insurance** is matched as one group (CPI SEME ↔ PCE line 276), treating both as net or retained-earnings concepts. Concordance ME011–ME041 → DMINRC.
- **CPI-only items**: vehicle registration and license fees (SETF01; concordance TF011/TF012 → N/A) and gardening/lawncare (SEHP02; concordance HP021 → N/A).
  - BEA's 9.1U also reports CPI-only physician and hospital items (lines 29–30). We cannot reproduce them, and we have no basis for that split.
- **PCE-only items**:
  - imputed financial services (255–257), portfolio management (268), securities commissions/trust (262–269), life insurance (271), income-loss and workers' comp insurance (277–278);
  - NPISH (342), net foreign travel (334−338) and net expenditures abroad (146−149);
  - farm dwellings (163), food on farms (103), gambling (227–229), social and religious services (318–326 excl. 320), and employment-agency and union/professional dues (302, 304, 305).
- **CPI leaves without their own published data** at the needed months (5.8% of core CPI weight, Sep 12m run) are imputed in this order:
  1. their own index, log-linear across a gap of 3 months or less;
  2. an explicit proxy;
  3. the nearest ancestor index at indent ≥ 2;
  4. the RI-weighted mean of the ancestor's sampled descendants.
  - Explicit proxy (assumption): domestic services, gardening, repair of household items and unsampled household operations take core CPI (SA0L1E). Their parent SEHP has no 2025–26 data in our pulls, and the only published sibling (moving, SEHP03) fell about 7% y/y.
  - The imputed list is in `B_group_detail_*.csv` meta rows.
- **CPI weights.** BLS relative importance: Dec 2024 (2023 weights) and Dec 2025 (2024 weights), updated to the base month by NSA price relatives and normalised within the aggregate. The link month is Dec 2025.
- **Seasonal basis.**
  - 12m runs use NSA CPI, matching the published y/y. PCE is SA only.
  - Sensitivity with SA CPI components against published SA core CPI 12m (2.566): every effect changes by 0.01 pp or less (other +0.006), and the residual becomes −0.105.
  - Monthly headline-check runs and the 3m-ann run use SA CPI.

## Task 1: Sep 2026 core, 12m (Sep 2025 → Sep 2026; PCE vintage Oct 29 2026, retrieved Nov 10; CPI retrieved Nov 10)
Published core PCE is 3.1212% and core CPI-U NSA is 2.5644%, a gap of **+0.557 pp** [O, U20404 line 374: 126.940 → 130.902; CUUR0000SA0L1E: 330.804 → 339.287].

| Effect | BEA convention | Centred alt. |
|---|---|---|
| Formula | −0.030 | −0.030 |
| Weight | −0.283 | +0.903 |
| Price | +0.049 | +0.077 |
| Scope, PCE-only | +0.942 | −0.304 |
| Scope, CPI-only | −0.023 | +0.009 |
| Other (CPI Jan-2026 reweight) | −0.001 | −0.001 |
| Residual (CPI replication) | **−0.096** | −0.096 |

Largest items, BEA convention (centred value in brackets):
- OER weight −0.628 (−0.095); rent weight −0.144 (−0.009); shelter theme −0.797 (−0.105).
- Software weight +0.332 (+0.478) and price −0.119 (−0.186).
  - PCE share 1.20% vs CPI 0.03%; CPI software +28.4% y/y vs PCE +18.5% [O, CUUR0000SEEE02 21.991 → 28.234; U20404 line 50 71.974 → 85.277].
- Motor vehicle insurance weight +0.144 (+0.194).
  - CPI share 3.49% vs PCE 0.60%; CPI MV insurance −4.98% y/y vs PCE +0.30% [O, CUUR0000SETE 890.473 → 846.102; U20404 line 279].
- Health insurance price +0.208 (+0.326).
  - CPI −8.99% y/y vs PCE +6.98% [O, CUUR0000SEME 149.597 → 136.151; U20404 line 276 130.045 → 139.124].
- PCE-only items:
  - hospitals third-party +0.237 (−0.009); restaurant meals (core definition) +0.210 (+0.002); portfolio management +0.146 (+0.084);
  - Rx third-party −0.112 (−0.198); other professional medical third-party +0.104 (−0.003); imputed financial services +0.088 (−0.021); NPISH +0.028 (−0.084).
- Airfares: weight −0.014 (+0.101), price −0.020 (−0.031). CPI airline +22.4% vs PCE (PPI-based) +20.5%.

## Task 2: Oct 2026 core
**Choice of comparison.** The CSV carries both.
- **PRIMARY: approximate 12m** (Oct 2025 → Oct 2026). It uses the same horizon as Sep and the slide.
  - It follows the project's convention, Eli's slide choice and the Cleveland/Atlanta approach: every CPI Oct 2025 level is interpolated as √(Sep 2025 × Nov 2025), NSA.
  - This reproduces the workbook's "CPI Oct 2026 views" core 12m of 2.8149% exactly [O, Price_Basket_Findings.xlsx].
  - Weakness: the CPI base is not published. The interpolation error is unknown and not bounded here.
- **ALTERNATE: 3m annualized** (Jul → Oct 2026, SA). The CPI side is fully published, but it is noisier and not comparable with the y/y figures.
- **PCE Oct 2026** is our estimate (`04_oct_pce_build`, D_build first-release variant): core index 131.28826, 12m 3.2425% (band ±0.049 pp), 3m ann. 3.5508% (band ±0.196).
  - Atom levels = Sep 2026 published × (1 + D_build line m/m).
  - Lines 146, 149, 334 and 338 (net foreign travel and expenditures abroad, which D_build leaves out) are set to the core estimate's m/m (0.29507%). Lines 10 and 11 use line 9, 156 uses 157, and 272 uses 273.

Results, BEA convention (centred value in brackets):
- **Approx. 12m:** PCE 3.2425 − CPI 2.8149 = **+0.428**.
  - Formula −0.040; weight −0.302 (+1.016); price −0.065 (−0.101); scope PCE-only +0.946 (−0.372); scope CPI-only −0.017 (+0.019); other +0.021; residual −0.116.
  - Shelter theme −0.837 (−0.082).
- **3m ann.:** PCE 3.5508 − CPI 3.7464 = **−0.196**. The sign is reversed.
  - Formula −0.037; weight −1.321 (+0.103); price +0.214 (+0.335); scope PCE-only +0.815 (−0.782); scope CPI-only +0.033 (+0.086); residual +0.100.
  - Rows are scaled by f so that they sum to the annualized gap (f is in the method text).

## Task 3: Headline cross-check vs BEA Table 9.1U (U90100, LastRevised Oct 29 2026, retrieved Nov 10 2026)
- **Missing months.** 9.1U has no entries for Oct and Nov 2025 [O, raw JSON: the 2025M10 and 2025M11 cells are absent].
  - Monthly CPI changes for those months do not exist: there is no Oct 2025 CPI, so neither Sep→Oct nor Oct→Nov can be computed.
  - We therefore compare **sums of monthly effects over the ten months Dec 2025–Sep 2026**. We ran our method month by month (SA, previous-month weights) and summed.
  - We also report a single-window Nov 2025 → Sep 2026 run, which is the same 10 months as the core method uses, and a headline 12m run with no BEA comparator.
  - The summed BEA monthly values are rounded to 0.01 pp per month (to 0.1 for lines 1 and 39).

Summed effects, Dec 2025–Sep 2026 (BEA vs ours, pp):
- Formula: −0.08 vs −0.056.
- Weight, total: −0.48 vs −0.508.
  - Shelter −0.52 vs −0.526 (OER −0.40 vs −0.405; tenant rent −0.11 vs −0.104; hotels −0.02 vs −0.016).
  - Gasoline −0.35 vs −0.425; household energy −0.02 vs −0.053; other +0.42 vs +0.496.
- Scope, PCE-only: +0.63 vs +0.518.
  - Physicians +0.05 vs +0.032; hospital and nursing +0.18 vs +0.154; FSWP +0.08 vs +0.077.
  - Foreign travel +0.06 vs −0.007; NPISH +0.04 vs +0.048; other +0.21 vs +0.214.
- Scope, CPI-only (in gap terms): −0.13 vs −0.021. BEA's CPI-only physician and hospital items are not replicated.
- Other effects: −0.08 vs −0.053; air transportation −0.07 vs −0.078.
- Our CPI residual: −0.045.
- **Gap.** The BEA effect lines imply −0.14 against our exact −0.166. BEA's rounded lines 1 and 39 sum to 3.1 − 3.5 = −0.40, which is a rounding artefact: the exact sums are 3.244 and 3.409.
- By month (`by_month_gap` rows), our gap tracks BEA's within 0.08 pp in every month. The largest differences are Feb (+0.08) and Mar/May (+0.06), and BEA's lines are rounded to 0.1.
- **Reading of the check.**
  - Shelter, FSWP, NPISH, airfares, "other" scope and the totals line up within about 0.03 pp.
  - Gasoline weight (−0.075 off) and foreign-travel scope (−0.07 off) are the weakest matches, along with BEA's CPI-only medical, which we can't reproduce (−0.11 off). These fall mostly outside core, except foreign travel and the medical scope split.

## Cross-checks with officials and 2025 finalists
- **Fed officials** (`02_Research/External_views/Fed_officials_2026-11/summary.md` and speeches, Nov 10–14) [O]:
  - None discusses the CPI–PCE gap or a reconciliation.
  - Bowman converts Oct CPI into an Oct core PCE estimate of 3.3% [O, speech text]. Logan and Paulson cite PCE and mention the Oct CPI release.
- **2025 finalists** (`Previous_Finalists_copy/`, transcripts and markdown) [O]:
  - No finalist reconciles CPI and PCE.
  - Harvard cited the Dallas Fed core services PCE excluding imputed non-market prices "such as portfolio management" [O, Harvard transcript ~2:40].
  - Harvard (2025) quoted Aug 2025 core PCE at 2.9% and Sep 2025 core CPI at 3.0%, so the gap was near zero then [O, transcript ~1:47–2:00].

## Prior-work consistency
- Workbook Summary note [O, Price_Basket_Findings.xlsx]: BEA's Sept 30 revision shrank the core gap (July 0.87 → 0.51 pp), and portfolio management (~0.10) plus software (~0.15) add about +0.25 pp, measured as excess over core.
  - Our centred Sep values: PM +0.084; software weight + price +0.29. Same order of magnitude; the definitions differ.
- Not rechecked here: the pre-revision July 0.87 figure. It comes from the earlier pipeline vintage.

## Conservative choices made (nobody to ask)
- Primary CSV column = BEA convention, because the brief asks for 9.1U categories and validation against 9.1U. The centred attribution is kept as `pp_centered_alt` and not hidden.
- Medical third-party split by k-scaling. This is our assumption, BEA's being unpublished, and a sensitivity is given.
- Household-operations proxy = core CPI. Without it, moving's −7% would be imputed to 0.8% of core CPI weight, and the residual would grow to about −0.2.
- The residual is not forced to zero or allocated to items.
- Nothing was downloaded, so there are no new raw files. Every input was already on disk.

## Paywalled
None encountered. No web sources were used.

## Worth a look
1. **The shelter-weight explanation has the wrong sign for this gap.** CPI's larger shelter weight lowers PCE relative to CPI in both conventions: −0.80 pp (BEA convention) and −0.10 (centred) in the Sep core.
   - So shelter cannot explain why core PCE is *above* core CPI. It explains why the gap is not bigger.
   - The PIMCO "about 34% vs about 16%" point in STATE.md is about weights, and it is correct; but here it works against the gap.
2. **The two attributions tell different stories** with the same total.
   - On BEA's convention, PCE-only items carry the gap (+0.94) and the weight effect is negative (−0.28).
   - Centred on the matched-set mean, the weight effect is positive (+0.90: software +0.48, MV insurance +0.19, airfares +0.10) and PCE-only scope is negative (−0.30: Rx third-party −0.20, NPISH −0.08, physicians −0.07).
   - The BEA convention's item rows include a normalisation component: PCE-only items take about 36% of core PCE, so every matched PCE share is smaller.
   - Judges who know 9.1U will expect BEA's convention. A one-line "why" reads more naturally from the centred version. Pick one and label it.
3. **Insurance measurement divergences are large** (Sep 2026 y/y):
   - CPI health insurance −8.99% vs PCE +6.98%, giving a price effect of +0.21 (+0.33 centred);
   - CPI motor vehicle insurance −4.98% vs PCE +0.30%.
   - Not checked: when CPI health insurance was last this negative. It deserves a look before Q&A.
4. **Software:** CPI +28.4% y/y vs PCE +18.5%, with PCE share 1.20% vs CPI 0.03%. The net contribution is +0.21 (BEA convention) or +0.29 (centred).
5. **The gap's sign depends on the horizon in Oct.** Approx. 12m is +0.43, but 3m annualized is −0.20 (CPI 3.75 vs PCE est. 3.55).
6. **CPI replication residual** of −0.096 pp (Sep core 12m), about 17% of the gap.
   - About −0.04 arises in Sep→Dec 2025 (shutdown months) and about −0.06 in Dec 2025→Sep 2026.
   - 5.8% of core CPI weight has no own published index at the needed dates and is imputed.
   - Apparel parents (SAA1/SAA2) do not aggregate exactly from their published leaves: +0.6 to +1.5 pp gaps at group level over Dec→Sep. That is consistent with BLS aggregating from area-level cells, so a residual is expected.
7. **BEA 9.1U line-total rounding.** Summing the rounded lines 1 and 39 gives PCE − CPI = −0.40 for Dec–Sep (`cpi_pce_wedge_bea_9_1U.csv`: 3.1 vs 3.5; the Hypothesis tab's Dec–Aug version is 2.60 vs 2.90). The effect lines imply −0.14, and the exact figure is −0.17. Don't quote the rounded line totals as the gap.
8. **BEA's CPI-only physician and hospital scope** (+0.14 over 10 months on the CPI side) cannot be reproduced from public data. Its counterpart is that our PCE-only medical scope is smaller than BEA's (0.19 vs 0.23).
