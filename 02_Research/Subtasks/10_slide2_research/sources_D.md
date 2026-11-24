# Sources, Agent D (Nov 15, 2026)

No web access was used; no new raw downloads. All tags are [O] (opened in this run) unless stated otherwise.

## Primary texts opened
- **Waller, Nov 10:** `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Waller_economic_outlook.pdf` [O]. Read with pypdf. Quote: "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September."
- **Bowman, Nov 10:** `.../speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` [O]. Read with textutil. Paragraphs 3, 11–13: "roughly one-fourth"; "may be broadening"; "3.3 percent in October"; "relative price shocks in specific sectors".
- **Logan, Nov 10:** `.../speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html` [O]. Quote: the trimmed mean "drop[s] too many increases right now"; "concentrated in narrow categories".
- **Dallas Fed technical note (2009 revision):** `03_Data/pipelines/Price indexes/PCE/raw/Dallas_trimmed_mean_tech_2026-11-10.pdf` [O]. Source for the 24%/31% trims and the 178 components.
- **Dallas component table, Sep 2026:** `03_Data/pipelines/Price indexes/PCE/raw/Dallas_trimmed_mean_components_2026-11-10.xlsx` [O]. Used for the weight-timing check.
- **Dallas published rates:** `03_Data/pipelines/Price indexes/Trimmed mean/processed/dallas_trimmed_mean_rates.csv` [O]. A pipeline-processed copy of the official workbook: 1m 2.84, 6m 2.42, 12m 2.26 (Sep 2026).

## Data (via the audited engine)
- BEA U20404/U20405, vintage 2026-11-10, read through `09_slide1_research/code/C_common.py` [O].
- UMD Oct build: `04_oct_pce_build/outputs/D_build_2026-10_lines.csv` [O], hospital rows: pi 0.3047, adj_b −0.3723.
- ALFRED hospital PPI revisions: `04_oct_pce_build/outputs/ppi_first_release.csv` [O]. Rows for PCU622---622---.
- `09_slide1_research/outputs/C_flip_distance_oct.csv` [O]. Line 184 needed m/m 0.5639.
- Tag rules and energy block: `08_shock_tagging/decisions.md` and `code/tag_exposures.py` (line 75) [O].

## Agent outputs relied on (coordinator-verified reports)
- Agent A: `A_q2_attribution.csv`, `A_q3_*`, `A_q1_*` and `A_q1_tariff_exemption.md`, via `report_A.md` [A]. I opened `A_q3_tagged_breadth_ts.csv`, `A_q1_tag_robustness.csv` and `A_q3_sensitivity.csv` directly [O].
- Agent B: `B_q4_*`, `B_q6_waller.csv`, `B_q7_hospital.md` and `B_q7_hospital_octobers.csv` [O, opened]; the remaining B outputs via `report_B.md` [B].
- Agent C: `C_q11_confirming_items.md` and `C_q10_lit_summary_update.md` [O, opened]; PPI stage figures via `report_C.md` [C]. `C_q8_oil_daily.csv` [O].
- The 2025 finals Q&A log and response strategies (`02_Research/External_views/Previous_Finalists_copy/`) [O]. Used for how judges phrase questions.
- STATE.md [O]: Oct PCE release Nov 25; the Goldman cross-check [2] (secondary as recorded there).

## Not accessed
- Bowman's attribution method (unpublished).
- Waller's breadth basis (not stated).
- Passenger-volume data.
- Dallas staff trimmed-mean bias research (referenced by Logan; not saved).
