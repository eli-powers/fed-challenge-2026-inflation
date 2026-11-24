Status: Audited — converged R4 (Codex; R4-F01 wording applied verbatim from auditor's suggested fix, 2026-11-10)

# 02 Refresh price-basket pipeline (Nov 10, 2026)

## Agent report (Opus 5.5)

### Findings
**Core ex OER first.** `core_ex_oer.py 2026-11-10` was run on the new BEA vintage (Sep PCE, released Oct 29), producing `Cross-index analysis/processed/core_pce_ex_oer_2026-11-10.csv` and `_summary_2026-11-10.csv`.
- Validation, Sep 2026 (12m / 6m ann / 3m ann / m/m): derived 376−153 is 3.595 / 3.427 / 3.366 / 0.366 vs BEA supercore (T20804 l.28) 3.596 / 3.429 / 3.369 / 0.367. The maximum gap is 0.003 pp (prior vintage 0.002).
- Harmonized PCE (374−160), Sep: 3.100 / 2.791 / 2.854 / 0.313 (Aug, old vintage: 2.999 / 2.604 / 1.930 / 0.256).
- Published core PCE (l.374), Sep: 3.121 / 2.923 / 2.903 / 0.317. The OER share of core nominal spending is 13.34%.
- Revisions to 12m: core PCE Aug 3.008 → 3.034 and Jul +0.012; core ex OER Aug 2.999 → 3.030 and Jul +0.014. Jan–Jun are unchanged.

**Oct CPI stopped as a method issue.** BLS cannot publish Oct 2026 12-month changes because Oct 2025 is missing.
- In an Oct run, only 6 of 204 headline leaves have a 12m change, and `analyze_baskets.py` crashes in `weight_pct()` (IndexError on an empty frame).
- The Oct run is saved in `oct2026_cpi_basket_run/`. The pipeline's CPI basket is left at **Sep 2026**.
- Options: (a) keep Sep; (b) run Oct on 1m/3m only, which needs analyze/build changes; (c) a BLS-style 12m approximation (factsheet not opened).
- Oct aggregates: headline +0.4 / core +0.3 m/m SA; 3m annualized 5.72 / 3.75 (agent calculation from the index).

| Basket | Latest | Rows old → new | Notes |
|---|---|---|---|
| CPI | Aug → **Sep 2026** | 344 → 344 (204 headline / 140 core) | Leaves with a 12m contribution: 170/106 → 171/107. Motor vehicle body work newly has data. |
| PPI | Aug → Sep | 59 → 59 | No composition change. Oct PPI is not out. |
| PCE | M08 → M09 | 336 → 336 (178 / 158) | 176/178 Dallas components mapped. Nothing dropped. |
| Market-based PCE | M08 → M09 | 289 → 289 | Unchanged. |
| Cleveland trimmed tails | Aug → **Oct** | 12 → 13 | Tail membership turned over. |
| Atlanta sticky | Aug → Oct | 5 → 5 | Publisher URL moved (fixed). |
| Dallas trimmed mean PCE | Aug → Sep | 3 rates | 1m ann 2.84, 6m 2.42, 12m 2.26 (Aug 1.92 / 2.35 / 2.19). |
| Cross-index | Sep | — | Breadth, sector contributions and 9.1U wedge (Dec 2025–Sep 2026) rebuilt. |

**Published rates, Sep 2026 (12m / 3m ann):**
- CPI 3.74 / 4.56; core CPI 2.56 / 3.41.
- PCE 3.65 / 3.56; core PCE 3.12 / 2.90; supercore 3.60 / 3.37.
- Market-based PCE 3.73 / 3.69; market-based core 3.12 / 2.94.
- PPI FD 6.34 / 8.14; ID61 14.14 / 16.99; ID62 21.50 / 41.52; ID63 6.32 / 7.45.

**Breadth, Sep** (share of basket weight; 12m > 3% / 3m ann > 3% / 12m above own 2018–19 average; Aug in brackets):

| Basket | 12m > 3% | 3m ann > 3% | Above 2018–19 avg |
|---|---|---|---|
| CPI core | 58.5 [53.6] | 58.3 [17.0] | 37.3 [40.0] |
| PCE core | 60.3 [61.4] | 45.2 [33.5] | 61.9 [63.1] |
| CPI headline | 62.1 [59.5] | 54.6 [19.4] | 47.2 [50.8] |
| PCE headline | 59.5 [60.8] | 43.9 [31.8] | 64.4 [66.0] |

Core PCE has 148 items with data, not the 149 stated in the brief/README.

**Top sector contributions, 12m pp, Sep:**
- Headline: gasoline and other energy goods 0.691, housing and utilities 0.604, health care 0.522, financial services 0.353, transportation services 0.308.
- Core: health care 0.585, housing 0.559, financial services 0.395, transportation services 0.345, recreational goods 0.312.
- Sums vs published: 3.658 vs 3.649; 3.123 vs 3.121.

**Reconciliation:**
- 12m sum gaps are about unchanged: CPI headline −0.295 → −0.306; core −0.136 → −0.124; PPI FD 0.020 → 0.012.
- 3m-annualized gaps in the retrieval reconciliation files widened (CPI 0.08 → 0.28; PPI FD 0.20 → 0.83; ID61 3.12; ID62 3.39). This is the known artifact of linearly summing annualized rates; `analyze_baskets` fix_3m rescales them.
- The hard-coded gap sentences in the REPORT text are stale.

### Script edits (dates, labels, paths only; before → after in notes.md)
- `retrieve_bls_baskets.py`:
  - `LATEST` 2026-08-01 → 2026-10-01. Added `CPI_LATEST` / `PPI_LATEST` = 2026-09 plus helpers, replacing about 30 literal Aug strings.
  - The `request_bls()` cache check was hard-wired to M08, so nothing would have been re-fetched. It is now driven by a `latest` argument.
  - The column `aug_2026_value_or_pct` is renamed by latest month (nothing reads it).
  - Atlanta URL moved (the old one returns 404).
  - **Borderline:** the Cleveland reconciliation's literal "0.2" now reads the same published figure from the saved `trim_revised.csv`. For Aug it reproduces 0.2; for Oct it gives 0.4.
- `build_basket_workbook.py`: Aug labels are now `CPI_LBL` / `PPI_LBL` (Sep) and `CLE_ATL_LBL` (Oct). The output path, which used to **overwrite `Price_Basket_Findings.xlsx`**, now writes `Price_Basket_Findings_build_<date>.xlsx`.
- Not edited: BEA, market-based, `core_ex_oer`, `analyze_baskets`, sector, `replace_sheets`, `findings_text.json`.
- **Latent bug, not fixed:** if `request_bls()` fails partway, the rerun renumbers batches and reuses that day's batch file for different IDs, which then silently come back empty. The agent hit a BLS 503, deleted the day's partial files and reran clean.

### Workbook sheet plan (replace_sheets.py NOT run)
- New build: `Price indexes/Price_Basket_Findings_build_2026-11-10.xlsx`. The live workbook is byte-identical to its archive copy.
- Method: the Oct 2 state was rebuilt from archived code and data, then compared with the live workbook (`code/compare_workbooks.py`).
- **Script-built, no hand edits:** Summary, CPI, PCE, PCE supercore, Market-based PCE.
- **Hand-edited:**
  - PPI: row 22 blank; flagged row "Transportation of government passengers" (WPSFD42212) missing.
  - Trimmed & Sticky: A3 source text; A28 legend wording.
  - Hypothesis analysis: A56 header.
  - Sources: A9 and A11 appended notes; A25 new row.
- **Hand-made:** PCE sector contributions (August values; no build step).
- **Proposal:**
  - Replace CPI, PCE, PCE supercore and Market-based PCE. Caveat: each carries August-tied `findings_text.json` notes, and supercore's "Supercore excluding…" table hard-codes the August numbers.
  - Replace Summary only after the findings text is updated.
  - PPI, Trimmed & Sticky, Hypothesis and Sources: only after their hand edits are carried into the build.
  - Leave PCE sector contributions as is.

### Stale findings text (`findings_text.json`, all tied to August)
- **key[0], gasoline:** the text says pump prices are reversing (~−31% ann.). They are now +47% CPI / +48% PCE 3m ann. Gasoline's 12m contribution is CPI +1.02 / PCE +0.63 pp (text: +0.81 / +0.49).
- **key[1]:** basket contributions and airfare rates.
- **key[2]:** core PCE 3.01 vs CPI 2.45 (now 3.12 vs 2.56); the market-based comparison; the 9.1U sums.
- **key[4]:** Dallas 2.19 (now 2.26); Atlanta core sticky 2.7 (now 3.06 Oct); 3m core PCE 2.05 (now 2.90); breadth 33% / 17% (now 45% / 58%). "Momentum cooled" now conflicts with the data.
- **key[5]:** "~2.0% annualized over 3 months"; "energy shock already reversing".
- **key[3]:** AI/PPI numbers.
- All `index/*` one-liners; `sheet/*` month labels and numbers; `sources[2]`; the `supercore_ex` numbers.
- Also (added after audit R1-F02): `sources[1]` says PPI relative importance is Dec 2025 (files say Dec 2024); `sources[6]` says 3m uses annualized change (analysis weights raw 3m changes, then annualizes); the Dallas rates CSV says component trimming data are unpublished although the component workbook is saved and processed.
- Also stale: the generated REPORT.md sentences and the hand-written `Cross-index analysis/processed/REPORT.md` and `findings_brief*.md`.

### Worth a look (agent)
- PPI FD Sep +1.3% m/m (largest since Mar 2022) and +6.3% y/y (largest since Dec 2022). ID62 3m ann +41.5%, y/y +21.5%.
- Breadth (3m ann, share > 3%) jumped in one month: core CPI 17.0 → 58.3; core PCE 33.5 → 45.2.
- Gasoline went from −31% to +47–48% 3m annualized; Oct CPI gasoline is +37.4% y/y.
- Core PCE 3m annualized 2.05 → 2.90; harmonized PCE 1.93 → 2.85.
- Dallas trimmed mean 2.26 vs core PCE 3.12, a gap of about 0.86 pp. Dallas trim counts changed sharply (upper cut 70 → 85 components).
- Atlanta publishes Oct 12m sticky rates (core sticky 3.06; flexible 6.20) even though BLS publishes no Oct 12m. Atlanta's method is unverified.
- Cleveland Oct tails turned over (energy and insurance out; used cars, rental, apparel, food items in).
- PPI Aug revised: final demand +0.5 (the old pipeline had 0.40).

### Spot-checks (agent)
FRED PCEPILFE pc1 Sep 3.12116 = pipeline 3.121160. BLS PPI release: FD +1.3 / 6.3. BLS CPI Table A, Oct 12m: gasoline 37.4, new vehicles 0.7, used cars −3.3, matching the Oct-run leaves. BLS API CPI Sep 12m 3.7 / 2.6 = 3.738 / 2.564. BEA supercore validation within 0.003.

### What to verify (agent)
Oct CPI horizon decision. Borderline Cleveland edit. PPI missing row. The month of the Dallas component workbook (unlabeled; treated as Sep). Atlanta URL permanence. BLS missing-data factsheet not opened. `request_bls()` cache bug.

## Coordinator review

**Verified:**
- **Core ex OER:** the validation numbers are in `core_ex_oer_DONE.txt` and the summary CSV. The inflation workbook built on this vintage audits to 0 failures (see 01_refresh_inflation): Sep 12m 3.10, m/m 0.31.
- **Breadth:** `Cross-index analysis/processed/breadth.csv` (Sep) and the archived pre-refresh `breadth.csv` (Aug) match the report exactly, including the 3m jump in core CPI 17.04 → 58.31.
- **PPI record:** FRED PPIFIS Sep m/m +1.34%. The last larger reading was Mar 2022 (+1.68), which confirms "largest since March 2022".
- **Gasoline:** FRED CUSR0000SETB01 3m annualized is −31.0 (Aug) and +47.0 (Sep), matching the report. Oct is +72.0 (not reported by the agent; CPI basket held at Sep).
- **Published aggregates:** PCE, core PCE and PPI FD levels and rates verified against FRED in 01_refresh_inflation.
- **Live workbook:** confirmed byte-identical to the archive; `replace_sheets.py` not run.

**Corrected:** nothing.

**Could not check:** sector contribution values beyond the sum check; the Dallas component workbook month; Atlanta's Oct 12m method; Cleveland tail membership.

**Judgment calls for Eli (escalated, not audit items):**
1. Oct CPI basket horizon: options (a), (b) or (c).
2. Which sheets of `Price_Basket_Findings.xlsx` to replace, and in what order relative to rewriting the findings text.
3. `findings_text.json` is Eli's written analysis, now stale against Sep data. Rewrite it, or mark it "as of Aug"?
4. The PPI sheet's missing WPSFD42212 row: intentional deletion?

**Coordinator worth a look:**
- `build_basket_workbook.py` previously wrote over the hand-edited workbook by default. The output-path change prevents that. Keep it.
- *(Corrected after audit R1-F01.)* The core CPI breadth jump (17.0 → 58.3) is dominated by OER crossing 3% annualized (2.80% → 3.22%; about 34% of the breadth denominator). Used cars, hospital services and lodging away from home also cross upward. These calculations do not identify causes; a threshold-share measure can jump on one heavy item.

**Interpretive notes (not shared unless asked):** several of the August findings (gasoline reversing, momentum cooling) are now contradicted by the data. This matters for the finals narrative.

---

# Round 2 additions (Nov 10, approved by Eli): Oct CPI views, interpolated 12m, notes columns

Status: Round 2 additions — under audit

## Agent report (Opus 5.5), summarized

**Official September outputs unchanged.** Every processed file is byte-identical before and after, except `Trimmed mean/processed/reconciliation.csv` (the R1-F03 fix). The reruns reused same-day raw files.

**Oct 2026 short-horizon view** (published BLS indexes, SA):
- Headline 1m 0.350%, 3m annualized 5.72%; core 0.296%, 3.75%. BLS publishes 0.4 / 0.3.
- Top 3m-annualized contributions, headline: gasoline (72.0% ann.) +2.24 pp; OER +0.86; wireless (24.9%) +0.30; lodging (25.5%) +0.28; rent +0.20.
- Top contributions, core: OER +1.15; wireless +0.40; lodging +0.38; rent +0.26; airfares (18.3%) +0.24.
- 3m breadth (share above 3% annualized):
  - Headline 59.8% (12m-base weights, approx.) / 58.7% (3m-base weights, exact).
  - Core 60.7% / 58.8%.
  - Sep official: core 58.3%, headline 54.6%.
- Files: `CPI/processed/*_2026-10_short_horizon*`, `Cross-index analysis/processed/cpi_{movers,breadth}_2026-10_short_horizon.csv`.

**Interpolated Oct 2026 12m** (NSA, "approx., interpolated Oct 2025 base", Oct 2025 = √(Sep 2025 × Nov 2025)):

| | 12m approx. | 11-month change (Nov 2025 base) | 13-month change (Sep 2025 base) |
|---|---|---|---|
| Headline CUUR0000SA0 | 4.022 | 4.131 | 3.913 |
| Core CUUR0000SA0L1E | 2.815 | 2.874 | 2.756 |

- Interpolated Oct 2025 level: headline 324.461, core 330.614.
- Component 12m: 168 headline leaves (Sep: 171).
- Component-sum gap: headline −0.11 (Sep −0.31); core +0.22 (Sep −0.12, sign flip).
- Approx. 12m breadth: core >3% y/y 59.7%, above own 2018–19 average 76.1%; headline 64.1% / 79.5%.
- Top approx. 12m contributions: headline gasoline +1.08, OER +0.86; core OER +1.20, airfares +0.34.
- Files: `*_2026-10_approx_interp_oct2025_base*`.

**Validation against publishers:**
- **Cleveland method** (PDF Dec 2025, saved to `Trimmed mean/raw/clevelandfed_interpolation_method_oct2025_2026-11-10.pdf`): Cleveland assigns each component the same one-month change for October and November 2025, √(Nov/Sep) − 1, then computes the median and trim as usual. It ignores the partial October data BLS published on Dec 18.
- **Cleveland median**, published Oct 2026 12m 2.7992: our geometric base applied to Cleveland's index gives **2.7992**, an exact match.
- **Cleveland 16% trimmed mean**, published 2.8912: ours gives 2.8908 (−0.0004 pp; both round to 2.9). Cleveland's Oct and Nov 2025 trimmed monthly values differ by 8.5e-6, probably from re-weighting (unconfirmed).
- **Limitation:** this checks Cleveland's published index, not an independent component rebuild. The pipeline has no median/trim reconstruction, and the component table covers only the latest month.
- **Atlanta:** Oct and Nov 2025 relatives are equal for sticky, core sticky and sticky ex-shelter, and our base reproduces their Oct 12m exactly (3.0944 / 3.0595 / 2.8977). The relatives are not equal for flexible and core flexible: ours gives 6.218 vs published 6.201 and 1.259 vs 1.222.

**Notes columns** (`build_basket_workbook.py`):
- Every place findings_text.json notes appear now sits under "Notes as of Aug 2026 data (Oct 2 workbook)", verbatim, with an empty "Current notes" column beside it.
- The `supercore_ex` table header says its values are Aug 2026 literals.
- New build sheet: "CPI Oct 2026 views".

**Script edits** (notes.md, "Round 2"):
- `retrieve_bls_baskets.py`: `_interp_oct2025()`, used only where Oct 2025 is missing, NSA only. `retrieve_cpi(latest, suffix, interpolate_oct2025)`; with defaults the output is unchanged. R1-F03 raw_file fix.
- `analyze_baskets.py`: one appended block, which reuses the existing functions.
- `build_basket_workbook.py`: `notes_block()`, header changes, the Oct sheet.

**Sheet replacement preview** (`replace_preview/`):
- Summary, PCE, PCE supercore and Market-based PCE: no value, style, width or height differences from the Oct 2 build, so nothing hand-made is lost.
- **CPI:** formatting differs from the Oct 2 build: column E width 13 vs 11, five row heights set, 50 fill colours stored with alpha FF. This looks like an Excel re-save or minor manual sizing. Replacing CPI would drop the width and row heights.
- PPI shows the same pattern.

**Worth a look (agent):**
- Core breadth above the 2018–19 average jumps to 76.1% on the approx. base. Most of that is OER (35% of weight) moving 3.26% → 3.42% against its 3.32% average, a threshold effect that depends on the interpolated OER base.
- The approx. component-sum gap swings by 0.34 pp for core. Treat component-level approx. 12m with more caution than the aggregates.
- Oct core 3m annualized 3.75% (Sep 3.41%); wireless and lodging enter the top movers.

## Coordinator review (Round 2 additions)

**Verified:**
- **Headline/core interpolated 12m and the 11/13-month comparisons** match my independent FRED calculation (CPIAUCNS / CPILFENS: 4.02 [4.13 / 3.91]; 2.81 [2.87 / 2.76]). *(Corrected after audit R2-F01: the 11- and 13-month changes are endpoint sensitivity comparisons, **not bounds** on actual 12m inflation. They would bound it only if the missing Oct 2025 NSA level lay between Sep and Nov 2025; headline Oct levels fell outside that range in 5 of 7 years, 2018–2024.)*
- **Official Sep outputs:** sha256 of all R1-audited processed CSVs unchanged except `Trimmed mean/processed/reconciliation.csv` (intended).
- **Live workbook:** byte-identical to its archive.
- **Cleveland PDF text** opened and read (pypdf); it confirms the equal-one-month-change method.

**Corrected:** nothing.

**Could not check:** component-level Oct values and breadth; the Atlanta flexible gap; the Cleveland trimmed re-weighting explanation.

**Coordinator worth a look:** the BLS FAQ says BLS's own October 2025 approximation for seasonal adjustment is the geometric mean of Sep and Nov. That is the same base, and Cleveland's method is equivalent for the median. So the interpolated aggregate rests on a method two publishers use, while component-level approximations are weaker.

## Round 3–4 additions (coordinator, Nov 10)

**R3-F01 fix:** `build_basket_workbook.py` selector updated so the "CPI Oct 2026 views" aggregate table again shows all six rows. Endpoint rows' Basis: "published NSA endpoints (sensitivity comparison, not a bound)".

**Sep 3m breadth on 3m-base weights** (approved by Eli; appended block in `analyze_baskets.py` → `Cross-index analysis/processed/cpi_breadth_2026-09_w3mbase.csv`; new Sep-vs-Oct table in "CPI Oct 2026 views"). Share of weight >3% 3m annualized, same weighting in each column:

| | Sep, 3m-base weights (published) | Oct, 3m-base weights (published) | Sep, 12m-base weights (official) | Oct, 12m-base weights (approx.) |
|---|---|---|---|---|
| CPI core | 59.04 | 58.79 | 58.31 | 60.73 |
| CPI headline | 55.48 | 58.75 | 54.61 | 59.76 |

- **Check:** the 12m-base column reproduces the official `breadth.csv` September values exactly (58.3066 / 54.6137). `breadth.csv` is unchanged.
- **Notable:** for core, the weighting choice changes the *direction* Sep → Oct: flat to slightly down on exact 3m weights (−0.25 pp, same 107 items), up on 12m-base weights (+2.4 pp as displayed, of which most is the coverage change; +0.29 pp on the common 103 items). Headline rises under both.
- **Coverage (corrected after audit R4-F01):** 3m-base breadth uses the same 107 core / 171 headline components in September and October. 12m-base breadth uses 107 / 171 in September and 103 / 167 in October because four components lack October 2025 approximate base weights (leased cars and trucks; motor vehicle insurance; photographers and photo processing; fees for lessons or instructions). Thus the displayed 12m-base change also reflects coverage; on the common 103 core rows, breadth falls 0.27 pp with 3m-base weights and rises 0.29 pp with 12m-base weights.
