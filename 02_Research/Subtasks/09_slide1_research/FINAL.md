# Slide 1 research: final report (R1–R6)

**Status: Audited — converged R2** (Codex, Nov 14). Two Blocking workbook bugs found in R1 (R6 leaf robustness cells took the wrong CSV rows; an average row was plotted as a month) were fixed and closed in R2. No factual, source or arithmetic item is open. Eight judgment calls (E1–E8) are Eli's; see section 5.

**Workbook:** [`01_Finals/data/Slide1_Inflation_Data.xlsx`](../../../01_Finals/data/Slide1_Inflation_Data.xlsx). It has 11 research tabs and 9 grey `raw_` tabs. Research tabs use live formulas back to the raw tabs: 5,400 formula cells, each matching the script's own value after a LibreOffice recalculation (0 mismatches, 0 errors). Every build also re-checks the 24 hardcoded breadth cells against their source CSV.
**Rebuild:** `python3 -I "02_Research/Subtasks/09_slide1_research/code/build_slide1_workbook.py" --verify` (fix the inputs in `outputs/`, not the xlsx).
**Reports:** `report_A.md` … `report_D.md` (each with a coordinator review). Audit trail: `06_Audits/slide1_research/`.

---

## 1. Headline numbers for slide 1 (Oct 2026 = UMD estimate, "est.")

| Figure | Value | Cell |
|---|---|---|
| Core PCE 12m, Oct est. (band ±0.05) | **3.24%** (Sep 3.12) | `Headline!C10` |
| Headline PCE 12m, Oct est. (band ±0.05) | **3.82%** (Sep 3.65) | `Headline!C15` |
| Core 6m ann. / 3m ann., Oct est. | 2.95% / **3.55%** (Sep 2.92 / 2.90) | `Headline!C9`, `C8` |
| Headline 6m ann. / 3m ann., Oct est. | 3.09% / 4.62% (Sep 3.34 / 3.56) | `Headline!C14`, `C13` |
| Core m/m, Sep → Oct est. | 0.317 → **0.295** | `Headline!B19:C19` |
| Headline m/m, Sep → Oct est. | 0.491 → 0.318 | `Headline!B20:C20` |
| Outside median core m/m (n=4 named, post-PPI) | 0.295; range 0.29–0.30; UMD distance 0.0 bp | `R2_outside_estimates!D21:D25` |
| Same, two-decimal figures only (n=3, excludes Morgan Stanley's 0.3) | 0.290 | `R2_outside_estimates!D27` |

The bands are the backtest root-mean-square error (RMSE; the typical size of the estimate's miss) against BEA's first print, scaled to each horizon: core ±0.049 pp m/m, ±0.20 on 3m annualized, ±0.10 on 6m annualized.

## 2. R1–R6: answers (data only)

**R1. Backtest** (`R1_backtest`). Errors are measured on m/m against BEA's first print, using the first-release variant, Dec 2025 – Sep 2026, n = 10.

| Measure | Bias | MAE |
|---|---|---|
| Our core | +0.017 | 0.042 |
| Cleveland core | −0.040 | 0.068 |
| Core-CPI regression benchmark | −0.071 | 0.087 |
| Our headline | +0.018 | 0.040 |

- MAE is the mean absolute error, the average size of a miss ignoring sign. Bias is the average signed miss.
- **Label fix:** the roadmap's "core CPI alone" is an OLS regression of core PCE on core CPI (a statistical fit), not raw core CPI. The tab now says so.

**R2. Outside October estimates** (`R2_outside_estimates`)
- Four named estimates were published after the PPI:
  - Goldman: 0.30 m/m, 3.24 y/y
  - BofA: 0.29, 3.2
  - Capital Economics: 0.29, 3.2
  - Morgan Stanley: 0.3 (one decimal), 3.2
- **Sources:**
  - Capital Economics is now **primary**. The public intro of its Nov 13 note gives 0.29% and "3.2%, from 3.1%".
  - The other three are press reports [2].
- **Excluded from the count:**
  - Reuters' unnamed-economist consensus (~0.3 / 3.2);
  - Cleveland (a model; 0.267);
  - pre-PPI items: Pantheon 0.35–0.40, Sharif ~0.34, SocGen 0.30, and Bowman's 3.3% y/y.
- **Count:** only 4 independent post-PPI estimates exist on the open web, against Eli's target of ~10. The rest are paywalled (section 6).

**R3. Core CPI–PCE gap** (`R3_core_gap`)
- **The gap itself:**
  - Sep 12m: core PCE 3.121 − core CPI 2.564 = **+0.557 pp**.
  - Oct approx. 12m: 3.242 − 2.815 = **+0.428**. The CPI's Oct 2025 base is interpolated.
  - Oct 3m annualized: 3.551 − 3.746 = **−0.196**.
- **Decomposition, Sep.** These are UMD estimates. Effects (pp) under two conventions:

| Effect | BEA-style | Centred |
|---|---|---|
| Weight | −0.28 | +0.90 |
| PCE-only scope | +0.94 | −0.30 |
| Price | +0.05 | +0.08 |
| Formula | −0.03 | −0.03 |
| Residual | −0.10 | −0.10 |

- **Shelter weight** is −0.80 BEA-style and −0.10 centred.
  - **CPI's heavier shelter weight lowers PCE relative to CPI under both conventions.** It does not explain why PCE is higher.
- **What pushes PCE above CPI** (BEA-style / centred):
  - software, +0.21 / +0.29;
  - motor vehicle insurance, +0.18 / +0.24: CPI −5.0% y/y vs PCE +0.3%;
  - health insurance, +0.18 / +0.21: CPI −9.0% vs PCE +7.0%;
  - PCE-only items: third-party-paid medical +0.36 / −0.26, financial services +0.30 / +0.09, restaurant meals (in core PCE, not core CPI) +0.21 / 0.00.
- **Caveat:** how the gap splits across effects depends on an assumed medical split. Without it, BEA-style weight is +0.28 and PCE-only scope +0.58; the total is unchanged.
- **Spoken-line candidates** are in `report_B.md` §4 (a, b, c).

**R4. Sep PCE y/y** (`R4_sep_pce_check`)
- **Headline:** index levels give 3.649; BEA's release text says 3.6. Logan, Paulson and Jefferson say 3.6. **Waller says 3.7**, and it is in his live speech. No saved vintage gives 3.7.
- **Core:** 3.121 from levels and 3.1 in the text. Waller, Logan and Jefferson all say 3.1.

**R5. Cleveland nowcast** (`R5_cleveland`). This is the Nov 13 nowcast, **carried forward from the Nov 14 pull; re-pull Nov 18**.

| Measure | m/m | y/y | UMD minus Cleveland |
|---|---|---|---|
| Core | 0.267 | 3.21 | +2.8 bp m/m |
| Headline | 0.305 | 3.81 | +1.3 bp m/m |

**R6. Breadth.** This is the share of core spending weight whose inflation is above 3%, using start-of-window weights (`R6_breadth`).

| Method | Horizon | Sep | Oct est. |
|---|---|---|---|
| **Leaf (central, Eli Nov 15)** | 12m | **60.6** | **54.0** |
| **Leaf (central, Eli Nov 15)** | 3m annualized | **44.8** | **45.5** |
| Sub-line (robustness) | 12m | 57.7 | 51.1 |
| Sub-line (robustness) | 3m annualized | 43.7 | 43.8 |

- **History:** the 2018–19 average is 3m 39.7 and 12m 35.7. The peak was 78.8 (12m, Aug 2022). **Correction (Nov 15, from slide 2 research):** these are the **sub-line** figures. On the central weighted-leaf basis: 3m 39.2, 12m 35.2, peak 79.7 (Aug 2022), per `C_breadth_ts.csv` leaf columns.
- **What drives the Oct 12m drop:** more than all of it is three hospital lines, 8.8% of core weight, all priced off one PPI series. They are at 3.34% Sep and 2.73% Oct est. If they had stayed above 3%, Oct would be 59.9. The carried-forward lines contribute −0.003 pp.
  - **This corrects report 07,** which put about 1.8 pp of the drop in the carried-forward lines. Codex confirmed the correction.
- **Component-sum gap:** the earlier "0.130" (Sep) and "~0.23" (Oct) figures are on **different bases**.
  - Sep 3m ann. gap 0.296 = (a) convexity 0.167 + (b) fixed-share vs Fisher 0.033 + (c) residual 0.096.
  - Oct: (a) 0.191, (b) 0.033, (c) 0.005.
  - Convexity is the gap from annualizing each component before weighting instead of after. Fisher is the chained index formula BEA uses.
- **Waller's ">70% of core services components above 3%":** a count gives 63.1%. Only a **weighted** share reproduces it, at 70.8%.

## 3. Flags

**Couldn't verify:**
- the Goldman, BofA and Morgan Stanley original notes;
- the timezone of the Reuters/KELO timestamp;
- why Waller said 3.7;
- BEA documentation of the 9.1U convention (it was inferred);
- the medical third-party split (it was assumed);
- how BEA built the Oct 2025 PCE base month;
- native Excel rendering. Charts were checked in a LibreOffice render.

**Worth a look:**
1. Core 3m > 12m > 6m has occurred in only 12 months since 2018. The last was Oct 2024. The core 3m > 6m ordering was false May–Sep 2026 and turns on only with the Oct estimate (A).
2. Core 12m at 3.24 would be the highest since Nov 2023, and headline 3.82 the highest since May 2023 (A).
3. Sep headline 3.649 sits 0.001 below the 3.65 rounding boundary. That is a plausible but unverified reason for Waller's 3.7 (coordinator).
4. CPI health insurance is −9.0% y/y vs PCE +7.0%, and CPI car insurance −5.0% vs +0.3% (B).
5. The 3m breadth series is very noisy: 62.7 (May), then 36.5 (Aug), then 43.7 (Sep) (C).
6. Supercore 12m breadth falls 14.5 pp Sep→Oct, vs −6.6 for all core (C).
7. Our backtest bias and Cleveland's have opposite signs (+0.017 vs −0.040), and the Oct UMD−Cleveland gap has the same sign (A).
8. Post-PPI estimates cluster within 1 bp. Pre-PPI estimates sat 5–10 bp higher (D). Codex adds that the forecasters share the same CPI and PPI inputs, so the four are not four independent measurements.
9. A blog attributes "about 0.34%" to Waller. It is unsourced and was left out (D).

## 4. Disagreements with the brief premise

- **The roadmap lists shelter weight as a candidate driver of the gap.** It is a large effect, but its sign is opposite: it narrows the gap. The run continued. R3 reports both conventions, and the slide line must not say shelter explains PCE > CPI.
- **R2's goal of ~10 independent estimates isn't reachable from the open web** (n = 4).

## 5. Judgment calls for Eli (both positions)
Full text is in the workbook tab `Judgment_calls_and_paywalled` and in `outputs/Z_judgment_calls.csv`.

| # | Decision | Claude | Codex |
|---|---|---|---|
| E1 | R3 attribution convention for the spoken line | Either is defensible. A convention-neutral line avoids choosing: insurance, software and PCE-only medical/financial services outweigh CPI's heavier shelter weight. | BEA-style resembles the 9.1U comparisons. Centred separates relative from common inflation. Both depend on the medical split. |
| E2 | Oct gap horizon | Approx. 12m (+0.43) for comparability, with the base caveat visible. | Same trade-off. The 3m figure (−0.20) avoids the missing base but is noisier. |
| E3 | Corroboration line | "Median 0.295, range 0.29–0.30, n=4", plus a footnote. | The median is 0.290 on two-decimal figures; MS rounding allows 0.290–0.295. Could say "about 0.3" instead. |
| E4 | Bowman 3.3% | Dated (pre-PPI) context only. | Agrees. |
| E5 | Oct 12m breadth decline | Show it only with the hospital caveat; 3m is flat. | Valid statistic. Present it cautiously, or prominently with the concentration explicit. |
| E7 | Waller 3.7 | Use BEA's 3.6 and name the source. | Agrees. Cause unknown. |
| E8 | "Accelerating" | Core 3m ann. 3.55 > 12m 3.24 > 6m 2.95. The 3m > 6m signal is new in Oct and rests on the estimate. Core m/m eased. | Supports a recent-momentum description, not a uniform increase. m/m eases and 3m breadth is flat. |

E6 (report 07's 1.8 pp) is closed as factual.

### Eli's decisions (Nov 15)
| # | Decision | Status |
|---|---|---|
| E1 | Verbal only, either/or: PCE puts more weight on fast-inflating spending. Depending on the method, that shows up as a weight effect (centred, +0.90) or a scope effect (BEA-style, +0.94). Both methods are valid; never present both as adding at once. | Locked (Nov 15) |
| E2 | Quote the Oct gap on the approx. 12m basis. | Locked |
| E3 | Verbal cue only: "about 0.3, in line with other forecasters using a similar methodological approach." | Locked |
| E4 | Bowman 3.3% is context only. | Locked |
| E5 | Weighted leaf (149) is the central breadth figure, replacing sub-line. The Oct 12m drop is flagged verbally as hospital-driven. | **Method locked.** Wording pending: base effect; "hospital" not "health care"; justify leaf on its own merits. Stress-test at slide 2. |
| E7 | Use BEA's 3.6. | Locked |
| E8 | "Recent momentum has picked up," not "accelerating." | Locked |

**E5 check (Nov 15, leaf basis):**
- The three hospital leaves (184–186) contribute −8.72 pp, against the total change of −6.59 pp. All other leaves net +2.13.
- **It is a base effect.** Hospital prices rose 0.893% m/m in Oct 2025, the month now leaving the 12-month window. Their Nov 2025–Sep 2026 average was 0.218%, and the Oct 2026 estimate is 0.305%.
- **Workbook follow-up: done (Nov 15).** R6 now leads with weighted leaf as the live-formula central figure (`R6_breadth!D6:E7`, over a 149-leaf block that draws on the new grey tab `raw_PCE_leaves`); sub-line is robustness (`D8:E9`). The hospital base effect is in live formulas at `R6_breadth!D66:G68`.

## 6. Paywalled links (Eli to fetch; workbook tab `Judgment_calls_and_paywalled`)

| URL | What it would add | Tab |
|---|---|---|
| Reuters original, Mutikani Nov 13 PPI story | Verbatim consensus wording; maybe named forecasters | R2 |
| Bloomberg survey / Bloomberg Economics Oct PCE | Strongest named consensus | R2 |
| MNI post-PPI PCE estimates (Nov 13) | Many sell-side estimates at two decimals | R2 |
| Newsquawk post-PPI sell-side commentary (Nov 13) | Two-decimal figures for MS, Pantheon, Oxford, Barclays | R2 |
| employamerica.org/core-cast | Independent non-bank nowcast | R2 |
| pantheonmacro.com post-PPI update | Replaces the pre-PPI 0.35–0.40 | R2 |
| Capital Economics full note | Already primary via its public intro; the full note adds detail only | R2 |
| kalshi.com KXPCECORE-26OCT | Market-implied distribution (the fetch was rate-limited, not paywalled) | R2 |

When Eli sends any of these, check each one against `R2_outside_estimates`. Add the row to `outputs/Z_outside_updates.csv` (or a new D row) and rebuild, or note it as already covered.

## 7. Re-pull checklist for Nov 18 (data cutoff)
- [ ] **R5 Cleveland nowcast.** Re-pull the month and year JSON into a new `03_Data/Raw/ClevelandFed_nowcast_*_2026-11-18.json`. Update `A_r5_cleveland.py`'s input and rerun it, then rebuild. Drop the "carried forward" label once it is refreshed.
- [ ] **New outside estimates** (Nov 14–18), including any post-PPI Pantheon or Employ America update, any Fed speech that cites October PCE, and any of the paywalled sources Eli fetches.
- [ ] **New data in the window:** if any October PCE input is revised, rerun `04_oct_pce_build` and then this pipeline.
- [ ] Rebuild with `--verify`. Confirm 0 mismatches and that the semantic check passes.

**Proposal (Eli decides):** the Cleveland re-pull and the PCE rates/breadth build will recur with each release. They could be promoted into `03_Data/pipelines/` after the finals.
