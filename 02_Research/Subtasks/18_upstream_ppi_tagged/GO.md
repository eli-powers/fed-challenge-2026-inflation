# GO: Producer-price inflation by shock group (Method A, tagged PPI stage commodities)

**For:** slide 2B right chart (candidate to mirror the left chart with PPI). Eli, Nov 17, 2026. Method C (`17_upstream_io_costs/`) was tried; Eli disliked its coverage gaps. All judgment calls below were decided by Eli in advance. Do not reopen them; if a rule cannot be applied as written, apply the stated fallback and log it.

**Run:** `coordinate` skill, then `audit-loop` (Codex, max 3 rounds). **Sonnet 5.5** coordinator and subagents (Opus only if a step fails twice). Keep usage low: no literature review, no analyses beyond this brief. Run to completion without stopping for input; put anything needing Eli in `report.md` → "Judgment calls for Eli".

## Question
Splitting a PPI stage aggregate into the left chart's four groups (energy, tariff, AI, everything else), how many points of that stage's 12-month inflation does each group add **above its own 2018–19 pace**, in **Mar 2025 vs Oct 2026**?

## Method (fixed)
1. **Aggregates:** **stage 4 intermediate demand (WPUID54) = central; stage 1 (WPUID51) = sensitivity.** Both computed in full. Units = the commodity-level components BLS lists under each stage in the relative-importance file `03_Data/Raw/BLS_PPI_stages_2026-11-15/bls_ppi_id_production_flow_relative_importance_2026_2026-11-15.xlsx` (see how `10_slide2_research/code/E_stage1_decomp.py` parses it; note the stray `#REF!` cells). Use the finest level that has both a weight and a priced index; services lines (trade, transportation and warehousing, other services) are units too.
2. **Weights:** BLS relative importance, **Dec 2025**, updated for relative price change to the start of each 12-month window: w_i = RI_i × I_i(base)/I_i(Dec 2025) (same as E). Check: weighted 12m change of the units reproduces published WPUID54/WPUID51 12m change within 0.3 pp in Mar 2025 and Oct 2026; report the gap. **Sensitivity:** each year's own December weights (fetch earlier RI files only if quick; else log as not done).
3. **Prices:** BLS commodity indexes (WPU…), **NSA**, 12-month % change. Fetch via BLS API v2 (key from `.env`; never write keys to files); reuse saved raw in `03_Data/Raw/BLS_PPI_*` where IDs overlap.
4. **Tags (exclusive; priority AI > energy > tariff > other):**
   - **Energy:** BLS's own energy commodity definition only (fuels, electricity, natural gas, i.e. the commodities BLS puts in its "energy" aggregates; group 05 and the energy lines in each stage). No energy-intensive goods.
   - **AI (central):** the producer commodities matching the four consumer AI items (PCE lines 49, 50, 51, 71: computers, software, phones/communication equipment, other information equipment): **electronic components and accessories (incl. semiconductors), computers and peripherals, communications equipment, and software publishing.** List the WPU codes used.
   - **AI sensitivity ("AI buildout", same AI bar, wider list):** add the commodity matches for the remaining industries in the AI producer-price basket (`10_slide2_research/code/J_ai_ppi.py`): data processing/hosting services, switchgear, turbines and power transmission equipment, and utility/power engineering services. Match each industry (PCU) to its commodity code(s) (WPU) via NAICS and list the matches. These items move into the AI bar from wherever they would otherwise sit.
   - **Tariff:** a goods commodity whose **imports are ≥ 15% of total U.S. supply**, from the BEA 2017 detailed import matrix / use table (same threshold as the consumer tags in `08_shock_tagging/decisions.md`). Map commodity → BEA commodity via NAICS; fallback: next broader NAICS level; log unmatched items as "other" and report their weight.
   - **Other:** everything else, including all services lines except AI services. **Sensitivity:** freight transportation counted as energy.
   - Output a tag table: every unit, code, name, weight, tag, the rule that fired, and the import share.
5. **Formula (mirrors the left chart, `10_slide2_research/code/G_baseline_attribution.py` group level):** excess_g = s_g × (R_g(t) − B_g), s_g = group weight share now, R_g = weighted group 12m rate, B_g = mean of the group's monthly 12m rates over 2018-01..2019-12. Total = sum of groups.
6. **Comparison months:** **Mar 2025 vs Oct 2026** (Oct preliminary; flag it), same as the left chart. Also report Feb 2026.

## Outputs (stage 4 central; stage 1 and each sensitivity alongside)
- Excess by group (pp of the stage's 12m inflation): Mar 2025, Feb 2026, Oct 2026, with total.
- Group table: weight share, 12m rate, 2018–19 baseline rate.
- Top 10 contributors to each group's Oct 2026 excess.
- Monthly path Jan 2018 – Oct 2026 of each group's excess (central).
- Diagnostics: weights sum to 100; reproduction gap vs published stage index; share of weight unpriced or unmatched (flag if > 10%); 3 index values spot-checked against raw.

## Files
- Folder: `02_Research/Subtasks/18_upstream_ppi_tagged/` (`brief_*.md`, `notes_*.md`, `report.md`, `code/`, `outputs/`).
- Raw: new folders `03_Data/Raw/BLS_PPI_stage_commodities_<date>/` and, if needed, `03_Data/Raw/BEA_IO_import_shares_<date>/`. Reuse BEA tables already saved by subtask 17 if present (read-only). Never edit existing raw files.
- Main script `code/ppi_tagged_excess.py` (`--fetch` downloads; otherwise reads raw), run with `python3 -I`, rules copied into its header.
- `report.md`: status line, method as run, the tables, deviations/fallbacks, caveats (PPI prices domestic producers only, so tariffs show indirectly; "tariff" = import-exposed, not verified as actually tariffed; Oct preliminary), and **Judgment calls for Eli**. Data first; no slide recommendations beyond flagging which stage/version is most stable across sensitivities.

## Subagents (suggested; coordinator may merge)
- **S1 (Sonnet):** parse stage 4 and stage 1 units and RI weights; fetch commodity indexes; reproduction check.
- **S2 (Sonnet):** tagging: energy list, AI PCU→WPU match, BEA import shares and the ≥ 15% rule; tag table.
- **Coordinator:** combine, compute, verify (reproduce 3 numbers by hand from saved intermediates), report, then `audit-loop`. Don't touch the deck, slide workbooks, `AGENTS.md`, `07_Archive`, or existing `03_Data/Raw` files.

## Done when
`report.md` holds every output above with sources, the script reruns cleanly from raw, the Codex audit has converged (or hit 3 rounds with open items listed), and STATE.md gets a one-line pointer (do not change Eli's views).
