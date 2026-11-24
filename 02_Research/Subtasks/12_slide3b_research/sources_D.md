# Sources: Agent D (slide 3B stress test), 2026-11-15

**Tags:**
- [O] = opened and read by D.
- [V] = number taken from report_A/B/C as verified by the coordinator, used as-is.
- [D] = recomputed by D.
- [2] = secondary.

## Primary texts opened
- [O] FEDS Note, De Michelis, Orak, Pradhan & Queralto, "The Effect of Oil Prices on Core Inflation: Recent Evidence from the Advanced Economies," Nov 9 2026.
  - File: `02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html`. Full text extracted.
  - Passages used:
    - the backward-looking reduced form and "inflation expectations depend on past inflation outcomes";
    - the Fig. 2 note "All exogenous variables are held fixed";
    - "upper bound … rather than a central prediction";
    - Table 1 RMSE;
    - Table 2;
    - fn 4 (country results);
    - the US control caveat;
    - "endure or reverse";
    - GEMUS: "tighten materially to contain inflation even as the economy weakens".
- [O] Accessible version, Fig. 2 data table: `03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/DeMichelis_oil_core_accessible_20261109.htm`.
- [O] Bowman, Nov 10 2026: `…/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf`. Converted with textutil.
  - Quotes: $110 sentence; "look through temporary energy-driven inflation, when possible"; "likely moved up further to 3.3 percent in October"; "closer to 2 percent next year"; "cannot offset the direct effects … second-round effects".
- [O] Waller, Nov 10 2026: `…/speeches/2026-11-10_Waller_economic_outlook.pdf`. Read with pypdf.
  - Quotes: "$20 to $30 a barrel" passage; "taking too much comfort"; "persist well into 2027"; the 50 bp conditional.
- [O] Logan, Nov 10 2026: `…/speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html`.
  - Quotes: "That effect will fade as higher energy prices become the new baseline"; "must not be too eager to call shocks temporary". Not used in answers; available as a contrary line.

## Project files opened
- [O] `GO.md`, `brief_D.md`, `report_A.md`, `report_B.md`, `report_C.md`, each with its coordinator review.
- [O] `03_Data/pipelines/forecast_3b/README.md`.
- [O] `03_Data/pipelines/forecast_3b/config/regime_response.csv`.
- [O] `03_Data/pipelines/forecast_3b/processed/{scenario_grid,oil_paths,oil_assumption}_2026Q3.csv`.
- [O] `outputs/C_q6_jumpoff.md`, `C_q6_jumpoff_decomposition.csv`, `C_q6_axis_compare.csv`, `C_q6_sensitivity.csv`.
- [O] `outputs/B_q3_path_definitions.md`, `B_q4_mapping_math.md`, `B_q3_brent_daily.csv`, `A_q2_proxy_note.md`.
- [O] `02_Research/Subtasks/10_slide2_research/outputs/C_q10_lit_summary_update.md`.
- [O] `02_Research/External_views/Fed_officials_2026-11/summary.md`.
- [O] `02_Research/External_views/Previous_Finalists_copy/2025 Finals - 2 Q&A Question Log.md` and `… 3 Q&A Response Strategies.md`.
- [O] `02_Research/Subtasks/06_inflation_section_flow/roadmap_finals.md` (slide 3B section).
- [O] `03_Data/README.md` line 46: Oct PCE Nov 25 and Michigan final Nov 20, both after the cutoff. This is a project file, not a BEA schedule, so treat it as [2].

## Not opened / not verified by D
- Philadelphia Fed SPF page: Q4 2026 release status not rechecked. A found a 404 at 17:40 ET on Nov 15.
- The SPF 2027 Q4/Q4 P25/P75 (2.25/2.727) is from A's microdata computation, which the coordinator did not check.
- Yahoo NYMEX BZ futures [2], as in A and B.
- Dec 8–9 FOMC date: news coverage only, per the officials summary. Not used in answers.
