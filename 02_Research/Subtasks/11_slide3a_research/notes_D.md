# Agent D notes (slide 3A stress test, Nov 15, 2026)

## Inputs read in full
- `brief_D.md`; `report_A.md`, `report_B.md`, `report_C.md` incl. coordinator reviews.
- Roadmap slide 3A section (`06_inflation_section_flow/roadmap_finals.md`).
- Slide 2: `FINAL.md` (§0–Q11), `outputs/C_q10_lit_summary_update.md`, `C_q10_oil_note_verification.csv` (rows cited), `C_q8_ppi_stages_summary.csv` (rows 12, 86), and the format of `D_qa_prep.md`.
- `External_views/Fed_officials_2026-11/lit_summary_DeMichelis_oil.md`.
- Output CSVs used: A_q1_vu, A_q1_bb_channels, A_q1_bb_quotes.md, B_q3_summary, B_q3_wages_ulc, B_q3_benchmark, B_q3_labor_share.md, B_q5_summary, C_q4_expectations, C_q4_summary, C_q4_gas_comovement, C_q4_gas_latest_change, C_q4_logan_aggregate, C_q6_logan_measure, C_q6_summary, C_q8_time_above_summary, C_q8_time_above_target.
- Primary text opened: `outputs/text/bb2023.txt` (BB 2023 pypdf extract, A's file) for printed p.9 and p.18 passages; `outputs/text/logan_2026-11-10_paragraphs.txt` paras 142, 156, 162, 165, 168–169, 177.

## New computation
- `code/D_q9_checks.py` → `outputs/D_q9_checks.csv` (88 rows). Run: `python3 -I "02_Research/Subtasks/11_slide3a_research/code/D_q9_checks.py"` from the project root. Reads only existing outputs; deterministic.
- Implied output deflator = ULC index / labor share index (identity labor share = ULC / P, BLS nonfarm business, SA, vintage Nov 5 2026). Not the published IPD (PRS85006143, not pulled).
- Logan measure stats use C's monthly series (BEA U20404/U20405 vintage 2026-11-10; Oct = est.).
- Expectations pre-oil baseline = Feb 2026 (last month before the Brent jump, as in slide 2 `D_preshock.csv`).

## New raw data
- `03_Data/Raw/S3A_D_michigan_mode_2026-11-15/umich_px5web202506.pdf`: UMich (J. Hsu), "June 2025 Update: Current versus Pre-Pandemic Long-Run Inflation Expectations", Jun 27, 2025. 1 page. Fetched via WebFetch (binary saved by the harness, copied unchanged). Text extracted with pypdf in-session (not saved as a script: extraction only, no numbers computed). Key text: "June's median now matches the peak reading from mid-2022"; web medians 4.4 Apr 2025, 4.0 Jun 2025.

## Judgments
- Damage ranking is mine; criteria: (i) is the attack factually right, (ii) does it hit a lead exhibit, (iii) can we answer with a number in ≤ 2 sentences.
- I did not rewrite the bridge line; support only.
- Secondary claim that web respondents report higher inflation expectations is [2], from search snippets; unverified.

## Not done
- No decomposition of nonfarm business margins into oil-sector vs other (needs BEA corporate profits by industry or IPD by sector).
- Mode-effect size for Michigan inflation expectations not quantified.
- Q4 SPF not out (due Nov 16); attack 1 and 9 triggers reference it.
