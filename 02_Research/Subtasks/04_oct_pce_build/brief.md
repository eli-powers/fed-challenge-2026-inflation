# Master brief: October 2026 PCE build (core and headline)

**For:** Fable 5.2, coordinator. **Written:** 2026-11-11, by Claude (Opus 5.5) with Eli Powers.
**Subtask folder:** `./02_Research/Subtasks/04_oct_pce_build/`

You are coordinating a research subtask for an undergraduate economics student, Eli Powers. Eli is preparing UMD's College Fed Challenge national-finals presentation: an FOMC policy simulation with live Q&A from Fed judges, on **Nov 20, 2026**. The slide and data cutoff is **Nov 18, 2026**. Eli owns inflation for the team.

Run this with the project's `coordinate` skill (`.claude/skills/coordinate/SKILL.md`), with one change: **you (Fable 5.2) are the coordinator** in place of Opus 5.5. Use Opus 5.5 and Sonnet 5.5 subagents for the bulk work, per the skill's model defaults. Also follow the project `CLAUDE.md` (evidence standard, data before interpretation, reproducibility). Eli directs; you run the work and verify it before it reaches Eli.

This is a **master plan**. You write the subagent briefs yourself, using the skill's template, and you decide the split. Eli has **locked** the decisions marked LOCKED. Raise disagreement with them at Checkpoint A. Don't change them on your own.

---

## 1. Why this exists

October 2026 PCE is released **Nov 25**, after the cutoff. Latest data in hand: September PCE, October CPI (released Nov 10). October PPI is released **Nov 13**. Eli wants October core and headline PCE estimates for the deck. They should be built by us from October CPI and PPI and checked against outside nowcasts. They must show **component contributions**, which outside estimates don't publish.

Context from the Nov 11 planning session (pipeline data, Nov 10 vintage):
- Core PCE 12m in Sep 2026: **3.12%**. Core CPI 12m: **2.57%**. CPI − PCE gap: **−0.56 pp**. The gap has been negative since Nov 2025. Its 2000–19 average was +0.26 pp. Gaps this negative appeared only in 2003–04 and 2010 since 2000.
- Core CPI alone is a weak proxy for core PCE's monthly change. Regressing core PCE m/m on core CPI m/m over 2024–26 gives a correlation of about 0.62 and a residual SD of about 0.064 pp/month. The CPI+PPI translation is the standard method.
- The October 2025 core PCE index exists in the current vintage (127.165, 2017=100), so the October 2026 12m change has a real base. October 2025 CPI does not exist (government shutdown).

These figures came from a quick in-session calculation, not a saved script. Recompute any you report.

---

## 2. Locked decisions (Eli)

1. **Hybrid approach (LOCKED).** Build our own October core and headline PCE from CPI and PPI components. Benchmark against outside estimates (Cleveland Fed nowcast, professional translations).
2. **Component universe (LOCKED).** The **178** Dallas Fed trimmed-mean leaf components in `PCE/processed/dallas_component_mapping.csv`, matched to BEA lines and series codes.
3. **Order of tagging (LOCKED).**
   - The BEA NIPA Handbook, Chapter 5, **Table 5.A (goods) and Table 5.B (services)**, is the starting **authority** for each component's price source. Newer BEA method documents override it where they differ (see §6a).
   - The BLS PCE–CPI concordance is used **second**, only for CPI-tagged components, to choose which CPI index. Where the two conflict, the Handbook wins and the conflict is flagged.
4. **Two tags per component (LOCKED).**
   - *Price source:* CPI, PPI, **blend** (several CPI and/or PPI inputs, or a CPI input with different scope), or imputed.
   - *Tier:* **observed** (October CPI or PPI), **proxied** (a released October driver, used *only if* BEA's method is verified), or **assumed** (carried forward).
5. **Aggregation (LOCKED).** m/m ≈ Σ wᵢπᵢ, with **September 2026 nominal expenditure shares** at leaf level. Do headline first, then core using BEA's core flag (`in_core` in `PCE/processed/components.csv`), with shares rescaled within core.
6. **Rates (LOCKED).**
   - Extend BEA's published **SA September index** by our October estimate. Compute 1m, 3m annualized, 6m annualized and 12m from index ratios: 3m = (I_Oct/I_Jul)⁴ − 1, 6m = (I_Oct/I_Apr)² − 1, 12m = I_Oct/I_Oct2025 − 1.
   - Show bands. The 3m annualized rate magnifies an October error about 4×, 6m about 2×, 12m about 1×.
7. **Contributions (LOCKED).** Report wᵢπᵢ for every component, labeled observed, proxied or assumed. Assumed contributions can't be called "movers."
8. **Seasonal adjustment (LOCKED approach).** For every source series published only unadjusted (NSA):
   - **Test C first.** Run an F-test on month dummies for a seasonal pattern. If there's no meaningful seasonality, use the NSA change as is.
   - **Then B for items that pass.** Estimate BEA's implied October adjustment for that item as the average, over past Octobers, of BEA's SA component m/m minus the source's NSA m/m. Use **prior years only** for any backtest month (no look-ahead).
   - **A (own X-13 or dummy regression) is an optional cross-check only.**
   - Note: the 12m rate barely depends on seasonal adjustment. The 1m, 3m and 6m rates do.
9. **Assumed-item rule (LOCKED approach).**
   - Carry forward each assumed item at its recent average m/m. The window (3, 6 or 12 months) is chosen by the backtest, by **lowest mean absolute error vs. BEA first print**. Set the criterion **before** looking at results. Eli's prior is 6 months.
   - Band: per item, weight × historical SD of its m/m, combined in quadrature across items, plus proxy error where available.
10. **Backtest decision rule (LOCKED, set before results).** If backtest MAE on monthly core is **≤ 0.05 pp** *and* our build beats the core-CPI-only benchmark, our estimate goes on the slide as our number, with a band. Otherwise it becomes a cross-check next to the consensus, and the component breakdown is still used.
11. **Deliverable (LOCKED).** A report plus CSVs. **No workbook edits** (don't touch `Price_Basket_Findings.xlsx` or run `replace_sheets.py`). **No charts or slides.** Everything saved to its proper location, scripted, verifiable and reproducible.

---

## 3. Existing assets (use these; don't rebuild)

Root: `./`. Paths below are relative to `03_Data/pipelines/Price indexes/` unless noted. The folder name contains a space.

| Asset | Path | Notes |
|---|---|---|
| 178 leaf components ↔ BEA lines/series | `PCE/processed/dallas_component_mapping.csv` | BEA codes end in `G` (price index), e.g. `DLINRG` |
| PCE component weights and changes | `PCE/processed/components.csv` | Has `in_core`, `weight_latest`, `weight_base_1m`, etc. 336 rows (includes parents) |
| Requested financial-services tags | `PCE/processed/requested_component_tags.csv` | Portfolio mgmt (line 268), financial service charges (258), financial services furnished without payment (254) |
| PPI-priced components (Handbook) | `Cross-index analysis/processed/pce_ppi_priced_components.csv` | 17 rows. **Not build-ready** (see §5) |
| BEA NIPA Handbook (PDF) | `Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf` | Despite the filename, this is the **whole handbook** (453 pages). Ch. 5 is "Updated: December 2021." Table 5.A (goods) is PDF pp. 105–111, Table 5.B (services) pp. 112–130. See §6a for its limits |
| BEA CPI–PCE reconciliation (U90100) | `Cross-index analysis/processed/cpi_pce_reconciliation.csv` | Weight, scope and formula effects; use as a sanity check |
| CPI item and series lists | `CPI/raw/bls_cu_item_2026-09-27.txt`, `CPI/raw/bls_cu_series_2026-09-27.txt` | Validate series IDs; SA availability (`seasonal` = S/U). Refresh if stale |
| PPI series lists | `PPI/raw/bls_pc_series_2026-09-27.txt`, `PPI/raw/bls_wp_series_2026-09-27.txt` | Map PPI source wording to series IDs and SA status |
| Aggregate CPI/PCE index levels | `03_Data/pipelines/inflation_data/processed/bls/observations.csv`, `.../bea/observations.csv` | Nov 10 vintage |
| Existing fetch code | `Price indexes/code/` (`retrieve_bls_baskets.py`, `retrieve_bea_baskets.py`, `fetch_utils.py`) | Reuse. **Known bug:** `request_bls()` batch cache. On a partial BLS failure, delete that day's partial files before rerunning |

**Unrelated file:** `Cross-index analysis/processed/ppi_named_series_tagged.csv` is an AI-related PPI list, **not** PCE sources. Don't use it as a PCE source map.

API keys: `.env`. Never write keys into files.

---

## 4. How CPI-tagged components get series IDs (agreed approach)

Concordance source: BLS, "PCE–CPI code mapping," https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm. A subagent read it Nov 11 [O]. Key facts:
- It's an inline HTML table, no downloadable file. Last modified Apr 5, 2024. The content comes from Blair et al. (2011), built to make PCE-weighted CPI aggregates.
- It maps CPI ELIs (entry-level items, e.g. `AA011`) to BEA PCE codes ending in `C` (current dollars, e.g. `DMBCRC`). It's **many-to-many** both ways, and 4 ELIs map to N/A.
- It does **not** say it reflects BEA's price-source data, and it doesn't mention PPI. That's why the Handbook is the authority.

Steps:
1. Scrape the table to `03_Data/Raw/` (dated). Script it.
2. **Strip the last letter** of BEA codes on both sides and join on the stem (`DLINRG` → `DLINR`, `DLINRC` → `DLINR`). Spot-check known pairs (electricity, gasoline, men's clothing) to confirm the convention.
3. **ELI → item stratum** = first four characters (`AA011` → `AA01`). Verify every stratum exists in `bls_cu_item`.
4. **Stratum → series ID:** SA = `CUSR0000SE` + stratum. NSA = `CUUR0000SE` + stratum. Verify each against `bls_cu_series`, and record whether an SA series exists. A quick Nov 11 count found about 166 active U.S. strata, 135 with SA and 31 NSA only. That was an approximate pattern filter; recompute.
5. **Patches:**
   - Vintage mismatch: the concordance is from 2011, and the CPI structure was revised (notably 2018). Rows that don't join go to a **manual-review list**. Don't force them.
   - Several strata per PCE component → tag **blend**. Combine with CPI relative-importance weights (Dec 2025).
   - Dedupe ELIs that roll up to the same stratum.
   - Unsampled ELIs (`xx090`) roll up like the others.
6. **Validation:** for each CPI-mapped component, compare the m/m of our chosen CPI series with BEA's published component m/m over 2024–26. Report correlation and mean gap. Flag poor fits as a wrong stratum, a missed blend or a wrong source tag.

---

## 5. PPI-tagged components: what's still needed

`pce_ppi_priced_components.csv` is a start, not a build input:
- **No PPI series IDs.** It holds Handbook wording ("PPI for offices of physicians"). Match each to IDs in the PPI series lists.
- **Parent-level and badly parsed rows.** The financial-services and trust rows are split across lines. Clean them and map them down to the 178 leaves.
- **Completeness unverified.** Re-check against Tables 5.A and 5.B and the newer method documents in §6a. For example, a reported Jan 2026 translation miss involved a legal-services PPI that isn't on our list [S, Employ America]. Add any missing PPI-sourced items.
- **Seasonal status:** record whether each PPI series has an SA version.
- **Portfolio management:** see §6, item 1.

---

## 6. Verify before building (Phase 0)

These are **unverified** and affect the build:
1. **BEA's reported Sep 30, 2026 change** that replaced the PPI deflator for portfolio management and investment advice with an extrapolator based on CES employment data [S, RBC]. Confirm from BEA's own release or technical note.
   - If true, decide whether the October input is observable (October payroll employment for that industry) and whether that's tier proxied or assumed.
   - The backtest **cannot** test the new method. Its band must come from elsewhere.
2. **How BEA treats NSA CPI and PPI inputs:** does it use them as is or seasonally adjust them itself? Check the Handbook and BEA methodology pages.
3. **ALFRED first-release coverage** for each PPI series that feeds PCE, plus CPI SA components if that's cheap. Also aggregate core and headline PCE first prints (`PCEPILFE`, `PCEPI`).
4. **Cleveland Fed nowcast:** which measures it publishes (core PCE m/m and y/y?), and whether past nowcasts are archived for benchmarking.
5. **BEA "source data and key assumptions"** for recent PCE releases: whether BEA itself extrapolates items at first print. That tells us whether our carry-forward approach mirrors BEA's.
6. **October PPI release date and time** (expected Nov 13, 8:30 ET). Confirm on the BLS schedule.

---

## 6a. Known gaps: inputs we don't have yet

**We do not have everything we need.** The list below is what Claude and Eli identified on Nov 11. It is **not complete**: Fable is expected to find more (see Step 0).

**Limits of the source authority we do have (Tables 5.A/5.B):**
- **Old vintage.** Chapter 5 was last updated **December 2021**. That predates BEA's 2023 comprehensive update, the 2024–2026 annual updates, the reported Jan 2026 legal-services change and the reported Sep 30, 2026 portfolio-management change. Treat it as a starting point that newer documents can override.
- **Too coarse.** Rows are at NIPA Table 2.4 line-group level, not at the level of the 178 leaves. Several leaves share one row's source description.
- **Hard to parse.** It's a multi-column PDF table, and text extraction runs columns together (checked Nov 11). Plan for careful parsing plus a manual read of the price column. Don't trust a naive text scrape.

**Sources to acquire (save to `03_Data/Raw/` or the subtask folder, dated):**

| Need | Why | Status |
|---|---|---|
| Newer BEA method documentation (e.g., an updated summary of NIPA methodologies in the *Survey of Current Business*, and the 2023 comprehensive and 2024–26 annual-update articles) | Overrides the 2021 Handbook where methods changed | Not in hand. Find the latest; confirm the titles exist |
| Whether BEA publishes a **leaf-level** price-source list or concordance for PCE | Would replace inference from group-level tables | Unknown. Check; don't assume it exists |
| BEA release notes and technical notes for recent PCE releases (incl. Sep 30, 2026; "key source data and assumptions") | Method changes; what BEA extrapolates at first print | Not in hand |
| BLS PCE–CPI concordance table | CPI crosswalk (§4) | Read Nov 11, not saved. Scrape and save |
| CPI relative importance, Dec 2025 | Blend weights | Not confirmed in hand |
| CPI stratum-level SA/NSA series for every mapped stratum (history + Oct 2026) | Observed inputs | Partly in the `Price indexes` CPI pipeline; check coverage against the mapping |
| PPI series for every PPI-sourced item (history + Oct 2026, released Nov 13) | Observed inputs | Series IDs not yet mapped (§5) |
| ALFRED vintages: PPI inputs, CPI SA components, `PCEPILFE`, `PCEPI` | Real-time backtest | Coverage unchecked (§6 item 3) |
| BEA component price indexes (U20404) and nominal spending (U20405), current vintage | Weights, validation, seasonal method B | In hand (Nov 10). Confirm Sep is the latest month |
| CES employment for the portfolio-management industry, Oct 2026 | Possible proxy, if §6 item 1 is confirmed | Not in hand |
| Cleveland Fed nowcast (current values + any archive) | Benchmark and corroboration | Not in hand |
| Public professional core PCE translations for October (and past months, for the backtest) | Benchmark | Not in hand. Record what's public; note paywalls |

Rules: if a source is paywalled or blocked, say so and ask Eli. Don't reason from guesses about its contents. A "not found" is unconfirmed, not absent.

---

## 7. Phases, checkpoints and audits

### Step 0: Stress test (you, before anything else) → CHECKPOINT A
Stress-test this brief and plan **before** launching any build agents. Save the result as `stress_test.md` in the subtask folder. Cover:
- premise errors, or a rival approach that would change the task;
- feasibility against the timeline (§8), and what to cut first if time runs short;
- failure modes the plan misses, and whether the mitigations are adequate;
- an **inputs inventory**: every input the build needs, marked *in hand* / *to fetch* / *unknown if it exists*. Start from §6a and **add any source you judge necessary that §6a misses**, with why it's needed. Flag new additions so Eli can see them;
- any locked decision you think is wrong, with your reasoning (Eli decides);
- your proposed agent split (agents, model each, what each answers) and subagent brief outlines.

**Stop. Eli reviews at Checkpoint A** before any agent launches.

### Phase 1: Mapping (Nov 11–12)
Run §6 verifications, then §4 and §5.
Output: the full 178-row mapping table with source tag, tier, series IDs, SA status, blend weights and flags. Also a manual-review list and the mapping validation from §4.6. Report the **observed / proxied / assumed shares of core and headline weight**.
**→ CHECKPOINT B: Eli reviews the mapping and the shares.**

### Phase 2: Methods and backtest (Nov 11–12; must finish before Nov 13)
- **Seasonal treatment** per §2 item 8, for every NSA input.
- **Assumed-item rule and band** per §2 item 9. Also an event check: did financial services furnished without payment shift after past policy-rate changes? The September 2026 hike matters here. If it shifted, widen that item's band; don't model it.
- **Backtest:**
  - *Window:* Dec 2025 – Sep 2026. Run Nov 2025 but flag it: its CPI was affected by the shutdown, so don't let it drive choices. Exclude Oct 2025 (no CPI). If ALFRED inputs allow, add **Oct 2023 and Oct 2024** as an October-specific seasonal check. If they don't, say it couldn't be tested.
  - *Target:* BEA **first-print** core and headline m/m (ALFRED), computed from index levels within the same vintage, to 2 decimals. Secondary target: current vintage.
  - *Real-time inputs:*
    - PPI: first-release from ALFRED where available; otherwise use revised data and flag the component.
    - CPI: current vintage is fine except across February SA revisions; flag affected months.
    - Seasonal factors and carry-forward averages: only data available at the time.
    - Weights: current-vintage previous-month shares (flagged).
    - BEA methods: as in force that month (e.g. portfolio management priced from PPI before Sep 30).
  - *Benchmarks:* last month's core PCE (no change in trend); core CPI alone (regression); Cleveland nowcast if its history is available; public professional translations, informally.
  - *Metrics:* bias, MAE, RMSE, max miss, **rounding hit rate** (does our estimate round to BEA's one-decimal print?), 12m error.
  - *Miss attribution:* split each month's miss by tier, comparing our component contributions with BEA's current-vintage ones (diagnostic only).
  - *Caveats to state:* the sample is small (~10 months), so present ranges, not precise rankings. BEA's Sep 2026 annual update changed history.
  - Apply the §2 item 10 decision rule and report the result plainly.
- **→ CHECKPOINT C: Eli reviews the backtest result against the decision rule.**
- **→ AUDIT 1 (Codex):** mapping plus backtest, via `audit-loop`, **before Nov 13**. Fix converged findings before the build.

### Phase 3: Build (Nov 13, PPI day)
- Pull October PPI (and confirm the October CPI vintage). Price every component and compute headline and core m/m, 1m/3m/6m/12m with bands, and contributions with tier labels.
- Compare with the Cleveland nowcast and any public professional estimates (corroboration, not inputs).
- **→ CHECKPOINT D: Eli reviews the build before anything is called slide-ready.**
- **→ AUDIT 2 (Codex):** the build, starting Nov 13. Aim to converge by Nov 15–16, leaving margin before Nov 18.

### Also prepare (in the final report)
Q&A-ready facts, as data, not interpretation:
- the observed share of weight;
- the main sources of backtest error by tier;
- the September-revision footnote: BEA revises Jul–Sep with the October release, so our 3m and 6m rates can move for reasons unrelated to our estimate.

---

## 8. Timeline (hard)

| Date | What |
|---|---|
| Nov 11 | Stress test → **A**. Start Phase 0/1 |
| Nov 12 | Finish mapping → **B**. Seasonal, carry-forward, backtest → **C**. **Audit 1** |
| Nov 13 | October PPI. Build → **D**. **Audit 2** starts |
| Nov 14–16 | Audit 2 converges. Final report |
| Nov 18 | Slide and data cutoff (hard) |

If time runs short, keep the core estimate, contributions and band, and the backtest on the core window. Drop first, in this order:
1. the optional seasonal cross-check (method A);
2. the Oct 2023–24 seasonal check;
3. the headline estimate (headline is mostly CPI food and energy and is lower risk).

Tell Eli at the next checkpoint what was dropped.

---

## 9. Outputs and file locations

All under `02_Research/Subtasks/04_oct_pce_build/` unless noted:
- `brief.md` (this file). `stress_test.md` (Step 0). Subagent briefs as `brief_<agent>.md`.
- `notes.md`, `sources.md` (per the skill; each source tagged [O]/[S]/[2]).
- `code/`: every script, rerunnable from the project root, run in order. Include a `code/README.md` with the run order and inputs/outputs.
- `outputs/` (CSV; include a header comment or a companion `_meta.csv` with series IDs, reference period, release date, vintage, SA basis):
  - `component_mapping.csv`: 178 rows, with source tag, tier, series ID(s), SA status, blend weights, flags, manual-review status.
  - `mapping_validation.csv`: per-component fit against BEA history.
  - `seasonal_tests.csv`: per NSA input, F-test result and implied October adjustment.
  - `backtest_results.csv`: per month and method, estimate vs. first print vs. current vintage, plus the summary metrics.
  - `oct2026_estimate.csv`: headline and core, 1m/3m/6m/12m, point estimates and bands.
  - `oct2026_contributions.csv`: per component wᵢ, πᵢ, wᵢπᵢ, tier, source.
  - `weight_shares.csv`: observed/proxied/assumed shares of core and headline.
- Raw downloads: `03_Data/Raw/<source>_<series>_<YYYY-MM-DD>.csv`, never edited. Cite existing pipeline raw files where they already hold the data.
- `report.md` per the skill (`Status: Round 1 — NOT AUDITED` first line, then the reports and a coordinator review).
- Audit files: `06_Audits/04_oct_pce_build/` per `audit-loop`.
- Worth a look items: append to `04_Ideas/questions_log.md` at the end.

**Don't:** edit `03_Data/Raw/` or any pipeline raw files; edit `Price_Basket_Findings.xlsx`; touch `07_Archive/`; read or follow `AGENTS.md`.

---

## 10. Reporting to Eli

- **Data before interpretation.** Give numbers, trends and anything notable. Don't say what it means for policy unless Eli asks.
- At each checkpoint: what was done, the data, flags (subagent issues, what couldn't be verified, irregularities). Questions go **last**.
- Separate facts, assumptions and uncertainty. Never invent sources, numbers or consensus. If something can't be accessed, say so.
- Explain new technical terms in one plain line the first time they appear (Eli knows seasonal adjustment only from class).
- Flag irregularities as **Worth a look**: for example, a component whose CPI/PPI source diverges sharply from BEA's history, or an October reading that's unusual (when did it last happen?). Finding nothing is fine.

---

## 11. Sources referenced in planning (to verify, not to cite as is)

- Knotek & Zaman, "Nowcasting U.S. Headline and Core Inflation," Cleveland Fed WP 14-03R / JMCB 2017. Core nowcast accuracy is roughly equal to SPF and the Greenbook [S]. https://www.clevelandfed.org/center-for-inflation-research/inflation-working-papers/wp-1403r-nowcasting-us-headline-and-core-inflation
- Chicago Fed Letter No. 529 (2026), Flash PCE, reported RMSE ~0.6 pp annualized [S]. https://www.chicagofed.org/publications/chicago-fed-letter/2026/529
- Oxford Economics PCE nowcast, claimed average absolute error of 2 bp [S, vendor claim]. https://www.oxfordeconomics.com/resource/us-pce-nowcast-rise-in-core-inflation-isnt-a-signal-for-2026/
- Employ America, Core Cast posts; Jan 2026 miss of 8–9 bp attributed to seasonal factors and a legal-services PPI change [S]. https://www.employamerica.org/inflation-analysis/january-2026-core-cast-post-pce/
- RBC, "PCE deflator update: a retroactive revision, not a disinflationary signal" (portfolio-management method change) [S]. https://www.rbc.com/en/economics/us-analysis/us-featured-analysis/pce-deflator-update-a-retroactive-revision-not-a-disinflationary-signal/
- BLS PCE–CPI code mapping [O, Nov 11]. https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm
- Do **not** use: a search summary claiming Aug 2026 core PCE "fell short of 0.3%/3.3% forecasts." It conflicts with our data (Aug 12m = 3.03%).
