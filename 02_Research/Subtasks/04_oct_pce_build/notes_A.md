# Notes A: source mapping (raw working notes, 2026-11-11)

Scripts (run from the project root, in order):
1. `python3 02_Research/Subtasks/04_oct_pce_build/code/A_build_mapping.py`. Writes component_mapping, weight_shares, manual_review_list, series_to_fetch, A_coverage_gap, A_parent_leaves, A_hierarchy, A_incore_check and A_stale_series.
2. `python3 02_Research/Subtasks/04_oct_pce_build/code/A_handbook_conflicts.py`. Writes A_conflicts.csv. It reads component_mapping.csv for the weights.

Shared loaders are in `code/A_common.py`. Name judgments are in `code/A_manual_matches.csv`, one reason per row.

## Inputs checked
- T244 (Table 2.4.4U-D) has 356 numbered lines, dated 2026-09-30 (cell D1). Unnumbered sub-rows sit under line 95 (six CPIs) and lines 276–279 (premiums / "Less:" benefits or losses). [O]
- U20405 (vintage 2026-11-10, LastRevised Oct 29, 2026) has lines 1–402. Lines 157 and 158 are **not published**. U20404 is also missing 145 and 333, which are net lines with no price index. [O]
- T244 and U20405 names agree on all lines except 17, and those 17 differ only cosmetically (BEA cross-reference parentheses, "acitivities" typo, "supplied civilians" vs "supplied to civilians", etc.). This confirms the line numbering is the same. [O]
- CPI relative importance file: the Table 1 title reads "(2024 Weights) ... December 2025". Confirmed. [O]

## Hierarchy
- The parent/child structure is inferred by additivity across 24 months (2024M10–2026M09). "Less:" lines count as negatives, with a tolerance of $1m + $0.6m per term. All 120 parents add up exactly in Sep 2026.
- Line 159 ("Tenant-occupied, including landlord durables") equals line 156 in nominal value but has a slightly different price (146.179 vs 146.183, Sep 2026). It is an alternative presentation, not an additive child, so it is excluded from the parse. Lines 157–158 are attached to 156 by hand.

## Coverage
- The 176 matched leaves sum to 98.906% of September PCE; adding line 218 (0.792%) gives 99.698%.
- The remaining gap is 0.302%. It is exactly line 145, net expenditures abroad by U.S. residents (0.058%), plus line 333, net foreign travel (0.244%). Neither has a price index in U20404, which is consistent with Dallas leaving them out. Both are classed as core under BEA's definition, so core coverage is 99.66% of line 374.

## Parent leaves
- 14 leaves have no source on their own row: 13, 17, 156, 176, 187, 194, 218, 241, 258, 272, 275, 281, 317, 342.
- This list differs from the brief's: it **includes 218** and **excludes 279**. Line 279's source sits on two unnumbered sub-rows that carry the same PPI, so 279 is priced as one line. The same holds for 276–278 inside 275.
- Sub-line shares are in outputs/A_parent_leaves.csv.

## Matching
- CPI "exact" means the names are equal after normalizing case, punctuation, "&" and whitespace, with no word changes. 151 lines are exact matches.
- Every PPI match is counted as manual: BLS titles use the "Industry-Product" form, so no PPI name can match exactly.
- 20 CPI wording differences were handled by hand. Low or medium confidence cases go to manual_review_list.

## Findings logged while working
- **Stale BEA-named CPIs.** These CPIs are not published for the U.S. city average in the BLS series list of 2026-09-27 [O]:
  - SS45031 New motorcycles, ended 2000M05
  - SS61021 Film and photographic supplies, ended 2016
  - SS62051 Photographer fees and SS62052 Photo processing, ended 2020
  - SEHP, SEHP01 and SEHP04, listed through 2025M10. The local Nov-10 API pull shows the last valid observations as 2024M11 for SEHP01 and 2024M07 for SEHP04, with '-' in later periods.
  
  BEA may use unpublished BLS detail; that is unverified. These lines are tiered "assumed".
- **components.csv in_core is wrong for 17 leaves.**
  - Off-premises foods and alcohol (fresh milk, eggs, meats, cereals, beverages, beer, wine, spirits, and others) are tagged core.
  - Tobacco and food furnished to employees (lines 247–248) are tagged non-core.
  - BEA's definition (U20404/U20405 note 3, and the energy footnote) gives core = PCE excluding lines 73, 113 and 169.
  - As a result, the components.csv core weight is 0.9089 against a true line 374 / line 1 of 0.8888. This affects the existing PCE pipeline; nothing was edited.
- **Seasonal status.** Lines where BEA uses the NSA CPI although BLS publishes an SA series: 52 pricing lines, 19.3% of PCE (e.g. prescription drugs, furniture, dental). This is consistent with BEA's footnote: "seasonally adjusted data where necessary". No line has BEA saying SA while BLS publishes no current SA series. Note: the CUSR0000SS45031 SA series ended in 2000.
- **NPISH (line 342).** Gross output (lines 345–355, 11.01% of PCE) comes from BEA input-cost indexes with unpublished weights. Receipts (line 356, −8.19%) are priced at HCE prices, per the T244 text "Details for these categories can be found in the relevant section of the Household consumption expenditures". The net is 2.96%. The leverage is large: a 1% error in the gross-output price moves the NPISH price by about 3.7%.
- **Line 268 portfolio management.** T244 says implicit/judgmental. Handbook 5.B (2021) says "Fixed-weighted average of PPI for Portfolio management and PPI for investment advice". The current PPIs PCU5239405239401 and PCU5239405239402 exist. T244 wins, so 268 is assumed.
- **Line 156 sub-lines.** 157 and 158 are unpublished, so their within-leaf weights are unknown. The proposed default is 157 = 1.00 and 158 = 0.00 (our assumption). Basis: line 159, which BEA prices with CPI rent alone, has the same nominal value as 156.

## BLS concordance
- I fetched https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm through WebFetch. It was not blocked, but it returned a model summary rather than raw HTML. The page was last modified 2024-04-05 and rests on 2011 work.
- It maps CPI ELIs to PCE codes for weights, not price sources. Its CPI mappings for PPI-priced PCE lines are therefore scope crosswalks, not price-source conflicts: physicians MC011, hospitals MD011, air TG011, legal GD011.
- Useful support it gave for name matches: HB011 LODGING WHILE AT SCHOOL → Housing at schools; EB041 TECHNICAL AND BUSINESS SCHOOL TUITION AND FIXED FEES → Commercial and vocational schools; ED041 TELEPHONE SERVICES, LAND-LINE → land-line lines.
- The rows were relayed by a summarizer, so treat them as [O] but re-check them verbatim before quoting.
