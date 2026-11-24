# sources_C: files opened for brief C (all read locally; nothing downloaded)

Paths relative to `./`.

## Data (primary)
- `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json`: BEA underlying detail Table 2.4.4U price indexes by line, monthly, Jan 2017-Sep 2026 (vintage retrieved 2026-11-10). Loaded via `D_common.load_bea_frame`; also parsed independently with `json` for spot checks (lines 184, 186, 129).
- `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json`: BEA Table 2.4.5U nominal spending by line, same vintage (weights).
- `03_Data/pipelines/Price indexes/PCE/processed/components.csv`: pipeline Dallas/BEA component rates and contributions (used only to reconcile the workbook's Sep sums: 149 core rows, `contrib_3m_ann_calc`, `contrib_12m_calc`).
- `02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv` and `D_build_2026-10_summary.csv`: audited October build (Codex audit converged R1, Nov 13), October m/m by pricing line, tier, within-leaf shares, core estimate 0.29507 and 3m/12m rates.
- `02_Research/Subtasks/04_oct_pce_build/outputs/W_pce_oct_tab_lines.csv`: October tab lines (used to check my sums and breadth).
- `02_Research/Subtasks/04_oct_pce_build/outputs/component_mapping.csv` (via `D_common.Engine`), `component_series_history.csv` (loaded by the engine; not used for any reported number).
- `02_Research/Subtasks/04_oct_pce_build/code/D_common.py`, `W_build_pce_oct_tab.py`: engine and tab construction (read, not edited).

## Prior work (read)
- `02_Research/Subtasks/07_breadth_reconciliation/report.md` and `code/recon.py`, `oct_leaf.py`, `misclass.py` (recon.py and oct_leaf.py rerun unchanged; they reproduce 60.626/44.817 etc.).
- `02_Research/Subtasks/05_fix_core_flag/report.md`: core flag (149 leaves, BEA line rule), Sep sums 3.032 / 3.171 and gaps.
- `03_Data/pipelines/Price indexes/code/analyze_baskets.py`: `fix_3m`, `rebuild_core`, `supercore` rules.
- `02_Research/Subtasks/09_slide1_research/brief_C_breadth.md`, `GO.md`.

## External views (cross-check)
- `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Waller_economic_outlook.pdf` (text extracted with pypdf; quote located in the opening passage on September PCE): "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September." Public source: https://www.federalreserve.gov/newsevents/speech/waller20261110a.htm (as listed in `summary.md`; not fetched).
- `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html`: breadth framing paragraph; 3.2% non-housing non-transportation core services 12m through Sep.
- `02_Research/External_views/Fed_officials_2026-11/summary.md`.
- `02_Research/External_views/Previous_Finalists_copy/` (Davidson, Harvard, PACE, UCLA 2025; 2023 and 2024 winner PDFs; the three 2025 Finals summary .md files): searched for breadth, diffusion, broad-based, share of components.

## Not accessed
- BEA's methodology documentation for the monthly Fisher aggregation (no web access used); the (b)/(c) split is therefore against a monthly chained Fisher approximation on the covered set.
- Any October PCE release (due Nov 25, 2026).
