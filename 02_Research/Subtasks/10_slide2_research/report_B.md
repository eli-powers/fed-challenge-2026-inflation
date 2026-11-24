Status: Audited — converged R3 (Codex, Nov 15, 2026)

# Agent B report: breadth measures (Q4–Q7), Nov 15, 2026
Agent: Opus 5.5, brief `brief_B.md`. Outputs `outputs/B_*`, scripts `code/B_*.py`, `notes_B.md`, `sources_B.md`. Method: share of spending weight with rate > 3%, start-of-window weights, 149 core leaves; Oct 2026 = UMD est.; BEA vintage 2026-11-10, SA.

## Findings

### Q4. Breadth by measure (`B_q4_breadth_by_measure.csv`, `B_q4_breadth_ts.csv`, `B_q4_breadth_summary.csv`, `B_q4_hospital_attribution.csv`, `B_q4_checks.csv`)
All 40 reproduction checks pass (core leaf 12m 60.626 / 54.038, 3m 44.814 / 45.467 within 0.01; every slide 1 C_breadth primary/robustness row within 0.0006; slide 1 core monthly series within 0.001).

| Measure | Horizon | Sep | Oct est. | 2018–19 avg | Post-2018 peak | Sub-line Sep → Oct |
|---|---|---|---|---|---|---|
| Core | 12m | 60.63 | 54.04 | 35.2 | 79.7 (2022-08) | 57.71 → 51.13 |
| Core | 3m ann. | 44.81 | 45.47 | 39.2 | 78.0 (2022-02) | 43.67 → 43.75 |
| Supercore | 12m | 68.98 | 54.48 | 25.9 | 75.2 (2022-11) | 63.95 → 49.45 |
| Supercore | 3m ann. | 39.80 | 38.69 | 29.6 | 86.0 (2024-11) | 37.82 → 35.75 |
| Core goods | 12m | 29.05 | 36.36 | 12.4 | 78.6 (2022-08) | 29.02 → 36.32 |
| Core goods | 3m ann. | 33.57 | 38.81 | 26.5 | 86.1 (2022-01) | 33.57 → 38.78 |
| Core services | 12m | 70.82 | 59.74 | 42.6 | 81.0 (2022-11) | 66.97 → 55.90 |
| Core services | 3m ann. | 48.46 | 47.61 | 43.3 | 89.3 (2024-11) | 46.94 → 45.35 |
| Headline (backup) | 12m | 59.80 | 53.99 | 32.9 | 81.1 (2022-08) | — |
| Headline (backup) | 3m ann. | 43.72 | 46.26 | 38.1 | 79.3 (2022-02) | — |

- Supercore 12m re-derived: 68.98 → 54.48 (confirms the earlier figure).
- 12m drops vs hospital leaves 184–186:

| Measure (12m) | Total change | Hospital contribution change | Change in breadth recomputed without hospitals* |
|---|---|---|---|
| Core | −6.59 | −8.72 | +2.38 |
| Supercore | −14.51 | −15.12 | +0.79 |
| Core services | −11.08 | −11.54 | +0.58 |

\*Coordinator label fix: this column is breadth renormalized over non-hospital leaves (core 56.86 → 59.24), not "total minus hospital" (which is +2.13 for core, the slide 1 E5 figure).
- Hospitals have no effect on 3m measures (their 3m rates are below 3% in both months).

### Q5. Sticky vs flexible (exploratory) (`B_q5_mapping.csv`, `B_q5_sticky_flexible.csv`, `B_q5_sticky_flexible_ts.csv`, `B_q5_atlanta_basket.csv`, `B_q5_coverage.csv`)
- Classification: the saved Atlanta Fed xlsx has aggregates only; the explainer shows the component table as an image. Used Bryan & Meyer (2010), Cleveland Fed Economic Commentary 2010-02, Table 1 (45 CPI groups; sticky if prices change less often than every 4.3 months). Saved in `03_Data/Raw/AtlantaFed_sticky_classification_2026-11-15/`. That the current Atlanta Fed basket uses exactly this grouping is unverified.
- Mapping: approach (a) via the BLS concordance; PPI/non-CPI-priced leaves left out. Primary rule: mixed-class leaves left out; alternative: majority by count. Three mixed leaves (luggage 70, shoes 112, amusement parks 212).
- Coverage of core weight: primary sticky 94 leaves 52.1%, flexible 17 leaves 9.1%, unclassified 38 leaves 38.7%; alternative 52.6 / 10.1 / 37.3%. Unclassified mostly PPI-priced health care, NPISH, finance, insurance, air travel, software.
- PCE breadth (primary), Sep → Oct est.: sticky 12m 60.28 → 62.75, 3m 61.29 → 66.69; flexible 12m 35.22 → 35.73, 3m 48.65 → 37.01. Flexible is 9% of weight and goods-heavy, so noisy. Both sets exclude hospitals (why sticky rises in Oct).
- Atlanta-style CPI basket (CPI relative importance, start of window), Sep → Oct: sticky 12m 66.10 → 67.91 (Oct approx.), 3m 59.55 → 62.63; flexible 12m 51.25 → 54.11, 3m 44.91 → 48.60; core sticky 12m 63.19 → 65.01; core flexible 30.58 → 29.25. Oct 12m uses the pipeline's interpolated base `components_2026-10_approx_interp_oct2025_base.csv` (Oct 2025 = √(Sep × Nov 2025), NSA): "approx."
- Sanity vs Atlanta Fed published aggregates, Sep: sticky 12m mean rate 2.68 vs 2.82; core flexible 1.42 vs 1.48.
- Verdict: coverage fair (61% of core weight); flexible thin and noisy; 3m sticky swings ~40 pp month to month because OER sits on the 3% line.

### Q6. Waller comparison (`B_q6_waller.csv`)
All variants pulled from `C_waller_variants.csv` (Oct est. already present, confirmed) and recomputed through the engine (match within 0.0006).

| Core services 12m | Sep | Oct est. |
|---|---|---|
| Count, leaf | 63.10 (53 of 84) | 60.71 |
| Count, sub-line | 58.62 | 56.90 |
| **Weighted leaf, start-of-window (Eli's preferred)** | **70.815** | **59.74** |
| Weighted leaf, Sep 2026 shares | 71.08 | 59.82 |
| Weighted sub-line | 66.97 | 55.90 |
| Count, ex housing (leaf / sub-line) | 64.10 / 59.09 | 61.54 / 57.27 (coordinator, from C_waller_variants.csv) |

Only weighted-leaf variants exceed 70% in September. Waller's own basis is not stated.

### Q7. Hospital base effect (`B_q7_hospital.csv`, `B_q7_hospital_octobers.csv`, `B_q7_hospital.md`)
**Answer: the Oct 2025 jump is a real measured price move, not a fill. The "base effect" line can be said.**
- BLS collected Oct 2025 PPI late and published it with November on Jan 14, 2026 (BLS revised release dates page [O]).
- Nov 2025 PPI Detailed Report: response rates "within the normal range, and no modifications to PPI methodology or procedures were necessary" (saved PDF p. 6 [O]).
- ALFRED: first-release vintage 2026-01-14, Oct 2025 = 248.009 (+1.42% m/m NSA); current +1.410%. No footnote/status code in the BLS API.
- BEA's shutdown note covers only the missing CPIs (geometric mean of Sep and Nov); the hospital leaves are PPI-priced.
- Not two months in one: Sep (−0.15%) and Nov (+0.22%) published separately.

| Series (Oct 2025 m/m) | Value | z vs 2018–25 | Percentile | Rank of 96 | z vs Octobers only |
|---|---|---|---|---|---|
| BEA leaf 184, SA | +0.893% | 2.73 | 96th | 4th | 1.40 |
| PPI hospitals PCU622---622---, NSA | +1.410% | 3.29 | — | 2nd | — |

- Leaf 184 averaged 0.218% Nov 2025–Sep 2026.
- Driver: October Medicare inpatient reset — WPU5121010111 +5.96% in Oct 2025, largest October since 2014 (earlier Octobers +0.8% to +4.3%; Oct 2026 prelim. +2.09%).

## Slide-worthiness (agent)
- Breadth by measure 4/5: clean, reproducible, 2018–19 baseline; supercore and core goods carry the story; the Oct drop needs the hospital caveat on screen.
- Sticky/flexible 2/5: 39% of core unclassifiable, flexible 9% of weight, 3m dominated by OER at 3%. Q&A backup line at most.

## Worth a look (agent)
1. 3m breadth swings are threshold artefacts: core 3m 66.5 (May 2026) → 32.8 (Aug) → 44.8 (Sep); OER (13% of core) 3m rate 2.80–3.43; rent 3m below 3% since Aug (2.34–2.74).
2. Supercore 12m jumped 54.0 (Feb 2026) → 69.9 (Mar) in one month; not decomposed.
3. Supercore and core services 3m peaked 2024-11 (86%, 89%), above 2022. Unverified; decompose before citing a "peak".
4. Medicare inpatient PPI +6.0% Oct 2025 vs a 2.6% FY2026 payment update [S, unverified].
5. BEA SA hospital series still shows an October bump in 2017, 2019, 2023, 2025 (0.72–0.89%): part calendar regularity.
6. Motor vehicle insurance (CPI RI ~2.5) has no Oct 12m in the CPI approx. file, so missing from the Oct sticky basket.
7. Concordance quirk: HM090 mapped to tenant housing (DTSPRC); kept as published.
8. No previous finalist used inflation breadth or sticky/flexible breadth (md files and 2023–25 transcripts searched).

## Spot-checks (agent)
1. `B_q4_breadth_by_measure.csv` row 13 supercore 12m leaf Sep 68.984; row 33 Oct 54.477.
2. `B_q4_breadth_ts.csv` 2026-08 core_3m_ann_leaf 32.771 (OER leaf 162 3m 2.80, 13% weight).
3. ALFRED PCU622622, date 2025-10-01, realtime_start 2026-01-14, 248.009.
4. `BLS_PPI_detailed_report_2025-11_retrieved_2026-11-12.pdf` p. 6 shutdown box; Medicare inpatient row 51 21010111 Sep→Oct 6.0.
5. Bryan–Meyer EC 2010-02 Table 1; leaf 250 hotels classified flexible (`B_q5_mapping.csv` row 111).

## What to verify (agent)
Current Atlanta basket = Bryan–Meyer Table 1?; reason for +6.0% Medicare inpatient vs 2.6% update (CMS rule, BLS staff); CPI-only source rule for blended lines; four CPI-priced leaves with no concordance link; Daly's quote is Kitco only; Oct 2026 PPI hospitals prelim (+0.677% NSA); Oct 12m breadth rests on UMD's 0.305% SA for hospitals (0.564% needed to stay above 3%).

## Coordinator review
**Verified (independent run through `C_common`):**
- Supercore 12m 68.98 → 54.48, 3m 39.80 → 38.69; core goods 12m 29.05 → 36.36, 3m 33.57 → 38.81; core services 12m 70.81 → 59.74, 3m 48.46 → 47.61. All match.
- Hospital contribution change: supercore −15.12, core services −11.54; zero at 3m. Match.
- ALFRED: Oct 2025 obs first appears with realtime_start 2026-01-14 at 248.009; Sep 2025 at that vintage 244.536 → +1.42% m/m NSA. Match.
- BLS Nov 2025 PPI Detailed Report quote ("within the normal range, and no modifications to PPI methodology or procedures were necessary") found verbatim in the saved PDF.
- Core leaf 2018–19 averages from slide 1's own `C_breadth_ts.csv`: 3m 39.20, 12m 35.25; peak 79.68 (2022-08). B matches.
**Corrected:** relabelled the "change excluding hospitals" column (renormalized breadth, not total minus hospital). Added the Oct ex-housing count from `C_waller_variants.csv`.
**Flag for slide 1 (Worth a look, coordinator):** slide 1 FINAL.md §2 R6 "History" line ("2018–19 average 3m 39.7, 12m 35.7; peak 78.8 Aug 2022") gives the **sub-line** figures, while leaf is now central. Leaf equivalents: 39.2 / 35.2 / 79.7. Check the slide 1 workbook/verbal cues before reuse.
**Could not check:** Bryan–Meyer table vs current Atlanta basket; Medicare payment-rule figure.
**Interpretive notes:** "breadth by measure" is the strongest exhibit; core goods breadth rising (29 → 36 at 12m, 34 → 39 at 3m) while services fall on the hospital base effect is the cleanest goods-vs-services contrast. The Oct 2025 jump being a regular Medicare October reset makes the "base effect" line defensible but invites "then why doesn't seasonal adjustment remove it?" (point 5) — for D.
