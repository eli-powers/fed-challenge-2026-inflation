# GO: Upstream input-cost pressure by shock group (Method C, input-output)

**For:** slide 2B right chart (candidate replacement for the stage 1 PPI chart). Eli, Nov 17, 2026. All judgment calls below were decided by Eli in advance ("all rec"). Do not reopen them; if a rule cannot be applied as written, apply the stated fallback and log it.

**Run:** `coordinate` skill. **Sonnet 5.5** coordinator and subagents (Opus only if a step fails twice). **No Codex audit** this run. Keep usage low: no literature review, no extra analyses beyond this brief. Run to completion without stopping for input; put anything needing Eli in `report.md` → "Judgment calls for Eli".

## Question
For each consumer shock group on the 2B left chart (energy-exposed, tariff-exposed, AI-related, everything else), how fast are the **purchased input costs** of the industries that produce it rising, relative to their own 2018–19 pace, in **Mar 2025 vs Oct 2026**?

## Method (fixed)
1. **Consumer items and tags:** exactly the left chart's: 149 core PCE leaves, `tag_final` from `02_Research/Subtasks/08_shock_tagging/proposed_tags.csv`, the same leaf set and weights as `10_slide2_research/code/G_baseline_attribution.py` (via `09_slide1_research/code/C_common.py`). Read-only; never edit those files.
2. **Consumer item → producing industries:** BEA **PCE bridge table** (2017 benchmark, detailed), producers' value plus wholesale/retail/transport margins as separate "inputs" (D4).
3. **Industry → inputs:** BEA **2017 detailed benchmark** input-output tables (after redefinitions, purchasers' or producers' prices: use producers' prices, consistent with PPI).
   - **Central:** total requirements (domestic, commodity-by-commodity or industry-by-commodity; document which), i.e. the whole supply chain.
   - **Sensitivity 1:** direct requirements (first-tier suppliers only).
   - **Sensitivity 2:** the latest BEA **summary annual** tables (~71 industries) instead of the 2017 detail.
4. **Inputs → prices:** BLS **PPI industry indexes (PCU, NSA)** matched by NAICS. Rule: exact NAICS match; else the next broader NAICS level; else drop the input and renormalise. Report the dropped weight share per group (flag if > 15%). Trade and transport margins are priced with the PPI trade (wholesale/retail) and transportation/warehousing service indexes. Energy inputs use the matching energy PPIs (no special treatment).
5. **Imports:** excluded (domestic requirements only). State this in the report: PPI excludes imports, and BLS import price indexes exclude tariffs.
6. **Labour / value added:** excluded (purchased inputs only). Also compute each group's **purchased-input share of output** from the same use table.
7. **Index:** for group g, input-cost 12m inflation = Σ_j share_jg × PPI 12m %Δ_j, shares from step 3 combined with the consumer leaf weights within the group (start-of-window PCE weights, as in G). Baseline = mean of the monthly 12m rates over 2018-01..2019-12.

## Outputs (for each group, central + both sensitivities)
- 12m input-cost inflation: 2018–19 avg, Mar 2025, Feb 2026, Oct 2026; excess = rate − baseline.
- **Contribution versions** (pp, mirroring the left chart): (a) plain: group PCE share × excess; (b) input-share scaled: group PCE share × purchased-input share × excess. Totals across groups.
- Top 10 inputs by contribution to each group's Oct 2026 excess (shows what drives each bar).
- Monthly path Jan 2018 – Oct 2026 for each group (central), for a possible line chart.
- Diagnostics: weights sum to 1 per group; dropped-weight share; PPI coverage; spot checks of 3 PPI values against raw.

## Files
- Folder: `02_Research/Subtasks/17_upstream_io_costs/` (`brief_*.md`, `notes_*.md`, `report.md`, `code/`, `outputs/`).
- Raw downloads: new folders `03_Data/Raw/BEA_IO_2017_detail_<date>/`, `03_Data/Raw/BEA_IO_summary_<date>/`, `03_Data/Raw/BLS_PPI_io_inputs_<date>/`. Never edit raw files.
- One main script `code/io_input_costs.py` (`--fetch` downloads; otherwise reads raw), run with `python3 -I`. Rules above copied into its header. BLS key from `.env` (never write keys to files). Reuse PPI raw already in `03_Data/Raw/BLS_PPI_*` where IDs overlap.
- `report.md`: status line, method as run, the tables above, deviations/fallbacks, caveats (2017 weights predate 2025–26; imports excluded; labour excluded so services groups understate cost pressure; owners' equivalent rent's inputs are a weak proxy for rents), and **Judgment calls for Eli**. Data first; no slide recommendations beyond flagging which version is most stable across sensitivities.

## Subagents (suggested split; coordinator may merge)
- **S1 (Sonnet):** download BEA 2017 detail use/total-requirements + bridge tables and the summary annual tables; build the leaf → industry → input weight matrices; checks that shares sum to 1.
- **S2 (Sonnet):** build the BEA-commodity → NAICS → PPI (PCU) concordance under rule 4; fetch PPI series; report coverage and dropped weight.
- **Coordinator:** combine, compute, verify (reproduce 3 group numbers by hand from saved intermediates), write report. Don't touch the deck, slide workbooks, `AGENTS.md`, `07_Archive`, or `03_Data/Raw` files that already exist.

## Done when
`report.md` holds every output above with sources, the script reruns cleanly from raw, and STATE.md gets a one-line pointer (do not change Eli's views).
