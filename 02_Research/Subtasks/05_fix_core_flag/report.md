Status: verified and audited (Codex converged R2)

# Core-flag fix, price-basket pipeline: report (2026-11-14)

**Data:** BEA vintage 2026-11-10, Sep 2026 data. Both runs read the same saved raw files, so every difference below comes from the code change, not from a data revision. Sep is the last PCE release before the finals (Oct PCE comes out Nov 25).

## What changed in code
- `retrieve_bea_baskets.py`:
  - The core flag and the core denominator now use `line_core()`, BEA's line rule: exclude U20404 lines 73–103, 113–119 and 169–171. The old name rule `core_member()` is kept only so the printed check can compare against it.
  - The `normalize()` regex now also strips "(parts of …)", which recovers line 218 (audio-video, photographic and information processing equipment services).
  - New `REPLAY_DATE=YYYY-MM-DD` option: reads that date's saved raw files instead of calling BEA or Dallas, and needs no API key.
  - One report sentence is now conditional, because it claimed line 218 was unmatched.
- `rebuild_market_based.py`:
  - The leaf-count assert goes from 176 to 177.
  - The "gap explained by line 218" closure row is skipped once 218 is a leaf, so it isn't counted twice.
  - Its core rule was already the line rule (`is_core`), so market-based core membership was never wrong. Only line 218 is new there.
- Not rerun: `core_ex_oer.py` and `sector_contributions.py`. Both read raw U20404/U20405 directly and never use the flag.

## Checks
- Printed core check: **"none"** (`PCE/processed/REPORT.md` line 14).
- Mapped Dallas components: 176 → 177. Line 218 is the only mapping change; every other match is identical.
- Core leaves: 158 → **149**. This now matches the "149-item core PCE" breadth count in `03_Data/README.md`.
- Core weight: **88.58%** of PCE vs BEA line 374/line 1 at **88.88%**. The 0.30 pp gap equals lines 145 and 333 exactly (0.302%), the two net lines with no price index. This meets the brief's done criterion.

## Two stages: read this first

The pipeline sets core membership at two points, and only one of them was wrong.

- **Retrieval stage** (`PCE/processed/components.csv` and `reconciliation.csv`): this is where the name-rule bug lived. It had 158 core leaves, 16 of them misclassified.
- **Downstream analysis** (`analyze_baskets.py` `rebuild_core()`, in place since 2026-09-27): this stage rebuilds core from the headline rows with the BEA line rule. It feeds the breadth figures and every workbook sheet. It already had **148 correctly classified leaves** before this fix.

So **the workbook, breadth and any slide numbers taken from them were never affected by the 16 mislabels.** Their before/after change comes entirely from adding line 218. (Caught by the Codex audit, R1-F01.)

## Before / after (Sep 2026; full table in `before_after.csv`)

**What the workbook and slides use (downstream):**

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Core leaves | 148 | 149 | +1 (line 218) |
| Core: sum of contributions, 12m (pp) | 3.148 | 3.184 | +0.036 |
| Core: published (3.121) less sum, 12m | −0.026 | −0.063 | −0.036 |
| Core: sum of contributions, 3m ann. (pp) | 3.056 | 3.032 | −0.024 |
| Core: published (2.903) less sum, 3m ann. | −0.154 | −0.130 | +0.024 |
| **Breadth, PCE core: % of weight with 12m > 3%** | **60.26** | **60.63** | +0.36 |
| **Breadth, PCE core: % of weight with 3m ann. > 3%** | **45.23** | **44.82** | −0.41 |
| Breadth, PCE core: % of weight with 12m > 2018–19 avg | 61.91 | 62.26 | +0.35 |
| Breadth, PCE headline: 12m > 3% | 59.47 | 59.80 | +0.33 |
| Breadth, PCE headline: 3m ann. > 3% | 43.91 | 43.55 | −0.36 |
| Market-based core: sum of contributions 12m / 3m (pp) | 3.107 / 3.009 | 3.150 / 2.981 | +0.043 / −0.028 |
| CPI breadth | — | — | unchanged |

**Retrieval stage only** (`components.csv`; diagnostics, not used by the workbook):

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Core weight, % of PCE (BEA 88.88) | 90.89 | 88.58 | −2.31 |
| Core leaves | 158 | 149 | −9 |
| Core: sum of contributions, 1m / 3m ann. / 12m (pp) | 0.313 / 3.090 / 3.044 | 0.326 / 3.171 / 3.184 | +0.012 / +0.081 / +0.140 |
| Core: published less sum, 3m ann. / 12m | −0.187 / +0.077 | −0.268 / −0.063 | −0.081 / −0.140 |
| Headline: published less sum, 12m | −0.029 | −0.087 | −0.058 |

The retrieval and downstream 3m sums differ (3.171 vs 3.032) because downstream rescales 3m contributions to aggregate annualization (`fix_3m`).

**Core membership changes** (detail in `core_membership_changes.csv`):
- Out: 13 food and alcohol lines.
- In:
  - tobacco: 12m 6.4%, 3m 7.7%
  - line 218: 12m 7.1%, 3m 0.5%; 0.9% of core
  - food supplied to civilians and military: 3.8%

**The ">50% of the basket above 3%" figure** (PCE core):
- 12m: 60.6% (was 60.3%).
- 3m annualized: 44.8% (was 45.2%).
- Both runs put 12m above 50% and 3m below 50%.

## Affected outputs
- Processed files that changed:
  - PCE: `components.csv`, `reconciliation.csv`, `dallas_component_mapping.csv`, `REPORT.md`
  - Market-based PCE: `components.csv`, `reconciliation.csv`, `pce_market_membership.csv`, `REPORT.md`
  - Cross-index analysis: `breadth.csv`, `movers_top5.csv`, `flagged_items.csv`, `hypothesis_baskets.csv`, `index_coverage.csv`
- Unchanged: published PCE and market-based rates (taken from BEA directly), harmonized PCE (core ex OER), sector contributions, all CPI/PPI outputs, and Trimmed mean.
- Workbook sheets whose values differ (comparing `Price_Basket_Findings_build_corefix_2026-11-14.xlsx` with today's earlier build):
  - Summary (8 cells: mover weight labels)
  - PCE
  - PCE supercore (component rows only; its rates come from BEA directly)
  - Market-based PCE
  - Hypothesis analysis (breadth table, baskets)
  - Sources (leaf count/closure)
- **The live `Price_Basket_Findings.xlsx` has not been touched.** Replace sheets via `replace_sheets.py` only after Eli approves this table.
- Slide numbers: a slide 2 figure taken from the workbook or breadth changes only by the line 218 effect, at most about 0.4 pp. Check it against the downstream "After" column. Retrieval-stage numbers were never in the workbook.

## Flags
- **Reconciliation gap, by stage.**
  - Downstream (what the workbook uses): the 12m gap widens slightly, from −0.026 to −0.063 pp. The 3m gap narrows, from −0.154 to −0.130 pp. There is no sign flip.
  - Retrieval stage: the 12m gap flips sign, from +0.077 to −0.063 pp. Codex decomposed the +0.140 pp change:
    - removing food: −0.051
    - adding tobacco, line 218 and employee food: +0.107
    - rescaling the denominator: +0.084
    
    That is mechanical, not a bug.
- Today's earlier build file `Price_Basket_Findings_build_2026-11-14.xlsx` belongs to another session's run. It was left in place byte-for-byte. The new build is saved under `_corefix_` instead.
- Archive (pre-fix processed files, both scripts, live workbook, earlier build): `03_Data/pipelines/Price indexes/archive/pre_corefix_2026-11-14/`.

## Reproduce
```
cd "03_Data/pipelines/Price indexes"
REPLAY_DATE=2026-11-10 python3 code/retrieve_bea_baskets.py
python3 code/rebuild_market_based.py && python3 code/analyze_baskets.py && python3 code/build_basket_workbook.py
python3 ../../../02_Research/Subtasks/05_fix_core_flag/code/before_after.py
```

## Workbook update (2026-11-14, approved by Eli)
- **Replaced** via `replace_sheets.py`: Summary, PCE, PCE supercore and Market-based PCE. Each matched the earlier build exactly beforehand, so no hand edits were lost. After the replace they match `Price_Basket_Findings_build_corefix_2026-11-14.xlsx`, and the other 9 sheets are unchanged.
- **Held:** Hypothesis analysis and Sources. The live versions are an older layout holding **Aug 2026 data**, not Sep:
  - live breadth for PCE core is 61.43% at 12m and 33.48% at 3m;
  - live Sources has PCE core at 148 leaves with published 12m 3.008.
  
  A replace would move them to Sep and change their notes layout, which goes beyond this fix. Waiting on Eli.
- **Update, same day:** Eli approved, and Hypothesis analysis and Sources were replaced, so all six sheets now carry Sep 2026 data and the fix. The pre-replace copy is at `archive/pre_corefix_2026-11-14/Price_Basket_Findings_after4sheets.xlsx`. The remaining "Aug 2026" text in sheets is the build's archived "Notes as of Aug 2026 data (Oct 2 workbook)" column, not data.
