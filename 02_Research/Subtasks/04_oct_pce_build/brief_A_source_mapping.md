# Brief A: source mapping (Opus 5.5)

You are a research collaborator for an undergraduate economics student preparing UMD's College Fed Challenge national-finals presentation (an FOMC policy simulation; live Q&A with Fed judges; data cutoff Nov 18, 2026). Explain technical concepts plainly. Today is 2026-11-11. Prefer primary sources: official data releases, methodology pages, Fed publications, papers.

Project root: `./` (paths below are relative to it; some contain spaces, e.g. `03_Data/pipelines/Price indexes/`).

## Project context
October 2026 PCE is released Nov 25, after the cutoff. We are building our own October core and headline PCE estimate bottom-up: price each PCE component from the October CPI or PPI series BEA itself uses, carry forward what can't be observed, and aggregate with September spending shares. Your job is the map from PCE components to source series. Others pull the data and run the backtest. The reporting unit is the Dallas Fed trimmed-mean leaf list. The source **authority** is BEA's Table 2.4.4U-D (dated Sep 30, 2026), which lists a price source and seasonal status for each of 356 BEA lines, on the same line numbers as BEA tables U20404/U20405.

## Inputs (all local; read them, don't re-download)
- Authority: `03_Data/Raw/BEA_Table244UD_PCE_price_source_data_2026-11-11.xlsx` (columns: Item = BEA line, PCE Component, Series Code, Price index source data, Seasonal Status; footnotes at the bottom).
- Leaves: `03_Data/pipelines/Price indexes/PCE/processed/dallas_component_mapping.csv` (177 rows; 176 matched to BEA lines; rank 88 unmatched and corresponds to BEA line 218).
- Weights: `03_Data/pipelines/Price indexes/PCE/processed/components.csv` (`in_core`, `weight_latest`) and `PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json` (nominal spending, every line) and `..._U20404_...json` (price indexes).
- CPI series lists: `03_Data/pipelines/Price indexes/CPI/raw/bls_cu_item_2026-09-27.txt`, `bls_cu_series_2026-09-27.txt`.
- PPI series lists: `03_Data/pipelines/Price indexes/PPI/raw/bls_pc_series_2026-09-27.txt` (industry, `PCU…`), `bls_wp_series_2026-09-27.txt` (commodity, `WPU…`).
- CPI relative importance: `CPI/raw/bls_cpi_relative_importance_2025_2026-11-10.xlsx` (confirm it is the December 2025 table).
- Secondary only: BEA NIPA Handbook `Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf` (whole handbook; Table 5.A PDF pp. 105–111, 5.B pp. 112–130; Dec 2021 vintage; multi-column, text extraction runs columns together) and the BLS PCE–CPI concordance (https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm; if BLS blocks the request, say so and skip it).

## Your task
1. **Coverage.** Build the pricing universe: every matched Dallas leaf, plus line 218. Compute September 2026 nominal shares from U20405 and find why the leaves sum to about 98.9% of total PCE (line 218 is about 0.79%; about 0.3% is unexplained). Deliverable: a short table of what is missing and its weight.
2. **Parent leaves.** Fourteen leaves have no source on their own row in the BEA table because the sources sit on their sub-lines (e.g. lines 13, 17, 156, 176, 187, 194, 241, 258, 272, 275, 279, 281, 317, 342; verify the list yourself). For each, list the sub-lines that carry sources, with their September 2026 shares within the leaf. These sub-lines are priced individually and rolled up to the leaf.
3. **Series IDs.** For every pricing line (leaf or sub-line), turn BEA's source text into BLS series IDs:
   - CPI: match the item name to an item code in `bls_cu_item`, then to U.S. city average series `CUSR0000<item>` (SA) and `CUUR0000<item>` (NSA). Verify each ID exists in `bls_cu_series` and record whether an SA series exists.
   - PPI: match the wording to a `PCU…` or `WPU…` series in the PPI lists. Record whether an SA version exists.
   - Composites and blends: list every input series and BEA's stated weighting ("fixed-weighted"); where BEA gives no weights, say so and propose a weight source (e.g. CPI relative importance), flagged as our assumption.
   - Never force a match. Anything not matched exactly on name goes to the manual-review list with your best candidates and why.
4. **Two tags per pricing line.**
   - *Price source:* CPI, PPI, blend, or imputed (implicit/quantity extrapolation, input-cost indexes, judgmental).
   - *Tier:* **observed** (an October CPI or PPI series BEA names, published monthly), **proxied** (a released October driver, *only if* BEA's table states that method, with the quote), or **assumed** (no replicable October input; carried forward). Portfolio management (line 268) is assumed: BEA's text says out months use market indicators and judgmental trend.
5. **Seasonal status.** Record BEA's Seasonal Status value verbatim per line, and which series we would therefore use: `SA` → BLS SA series; `NSA` → BLS NSA series as is; `SA by BEA` → NSA source, flagged as needing an estimated seasonal adjustment. Flag any line where BEA says SA but BLS publishes no SA series, or the reverse.
6. **Conflicts.** Where the Handbook (Tables 5.A/5.B) or the BLS concordance disagrees with the BEA table for a line you can check, list the conflict. The BEA table wins. Don't parse the whole Handbook; check the PPI-sourced, composite and imputed lines.
7. **Shares.** Report observed / proxied / assumed shares of headline and core weight, and the share by BEA seasonal status.

## Rules
- Verify every claim against a source you opened. Tag each one: [O] opened, [S] search snippet only, [2] secondary. Mark anything unconfirmed "unverified". Never invent numbers, series IDs or citations.
- Compute every number with a saved script in `02_Research/Subtasks/04_oct_pce_build/code/` (prefix `A_`), rerunnable from the project root with `python3`. No hand calculations. Hand-made judgment calls (name matches) go in a small committed CSV the script reads (`code/A_manual_matches.csv`), each with a reason.
- Don't fetch data series; another agent does that from your mapping. Don't edit anything under `03_Data/` or `07_Archive/`. Don't read `AGENTS.md`. Don't edit any workbook.
- Report data, not policy interpretation.
- If a source is paywalled or blocked, say so. Don't reason from guesses about its contents. A "not found" means unconfirmed, not absent.
- Keep an eye out for irregularities (a source that looks wrong for its component, a heavy line with no replicable input). Log them under "Worth a look". Finding nothing is fine.
- Search extracted PDF text with Python (pypdf), not grep.

## Output
Save to `./02_Research/Subtasks/04_oct_pce_build/`:
- `outputs/component_mapping.csv`: one row per pricing line. Columns: dallas_rank, dallas_component, leaf_bea_line, pricing_bea_line, pricing_line_name, is_subline, share_of_headline_sep2026, share_within_leaf, in_core, bea_source_text, bea_seasonal_status, source_tag, tier, series_id_sa, series_id_nsa, series_to_use, blend_inputs (semicolon list of id:weight), needs_bea_sa_estimate (Y/N), match_method (exact/manual/unmatched), flags.
- `outputs/weight_shares.csv`: shares by tier, source tag and seasonal status, for headline and core.
- `outputs/manual_review_list.csv`: unmatched or doubtful lines with candidates.
- `outputs/series_to_fetch.csv`: every distinct BLS series ID needed (CPI SA, CPI NSA, PPI), one per row, with which lines use it.
- `notes_A.md` (raw notes as you go) and `sources_A.md` (every source, URL or path, [O]/[S]/[2], one line on what it supports).
Do NOT write report.md. Return the report as your final message: Findings · Worth a look (only if something stood out) · Spot-check examples (5, with exact file and row) · What to verify. Concise, as a professional economist.
