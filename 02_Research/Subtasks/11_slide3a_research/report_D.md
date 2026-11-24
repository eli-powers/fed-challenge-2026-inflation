Status: Audited — converged R3 (Codex, Nov 15; fixes from R1-F01/F02/F04–F07 applied, see 06_Audits/slide3a_research/R1_claude.md)

# Agent D report: hostile-judge stress test (Q9) (Opus 5.5)

Evidence only; no policy recommendation. All spoken lines are PENDING Eli. Paths relative to `11_slide3a_research/`.

**Deliverables:** `outputs/D_qa_prep.md` (17 attacks, sections a–f, ranked by damage); `outputs/D_bridge_line_check.md`; `outputs/D_verbal_cues.md` (10 lines plus 4 "do not use"); `outputs/D_slide_worthiness.csv`; `outputs/D_paywalled.csv`; `notes_D.md`, `sources_D.md`. Script `code/D_q9_checks.py` writes `outputs/D_q9_checks.csv` (88 rows) from A/B/C outputs only; rerun reproduces it (same md5). New raw folder `03_Data/Raw/S3A_D_michigan_mode_2026-11-15/umich_px5web202506.pdf`.

## Findings: top attacks by damage
1. **High. #8, BB read literally** (no catch-up effect, −0.024, p=0.765; V/U 1.06 < 1.2). Answer from BB: short-run expectations "feed fairly quickly into wages" (printed p.18). SCE 1y 3.00 (Feb 2026) → 3.91 (Oct), +0.91 pp (`D_q9_checks.csv` rows 22–24). BB p.9: "the longer the episode… the stronger the effect on steady-state inflation."
2. **High. #13, the Logan measure's rise is all in the Oct estimate.** Mostly right: Oct est. 3m 3.46 is not unusual (4 of the prior 12 months at or above it; high 4.25 Jan 2026; 12-month mean of the 3m rate 3.18; rows 2–6). A one-month jump ≥ 0.86 pp happened 5 times since Jan 2024 (row 10). Lead with the level: 12m 3.21 vs 2018–19 2.27.
3. **High. #12, wage-benchmark sign depends on measure and trend.** Against 3.52: ECI W&S −0.40, WGT +0.38, hourly comp +0.97. Against 4.21: all below except hourly comp (+0.28) (rows 52–83). ULC avoids the trend choice: 1.92 over 8 quarters.
4. **High (new). #15, Michigan's long-run comparison breaks at a survey-mode change.** Michigan moved from phone to web interviews in 2024. UMich's own web-only series says June 2025's 4.0 "matches the peak reading from mid-2022". So 3.4 now is below the like-for-like 2022 peak; C's "above its 2021–23 peak (3.2)" is a mode artifact. Web era: 4.4 (Apr 2025) → 3.3 (Feb 2026) → 3.4 (Nov prelim) (rows 18–21).
5. **Medium-high. #2, cherry-picking MCT 2.8 over trimmed 2.3.** Show the range 2.26–3.60, all above 2. Dallas's alternative trim 2.57 vs 2.22 (Jun 2026). Concede Dallas calls the evidence "not clear-cut".
6. **Medium. #11, labor share and margins.** Use 53.0 (Q3, current vintage), not 52.8. Identity labor share = ULC ÷ output price gives implied output price +4.05% y/y vs ULC +2.39% (rows 46–48): output prices outpaced ULC and the nonlabor share rose. Nonlabor payments include profits, depreciation, taxes, interest and rents, so wider profit margins or oil rents are possible explanations needing separate evidence (Codex R1-F02); not decomposed.
7. **Medium. Other briefed attacks:** #9 Logan's 3.1 is converted to a PCE basis from an unpublished list (para 169), so non-reproduction is expected. #1 anchored: 5y5y 2.15 → 2.19 since Feb. #4 gas: Michigan 1y peaked at 6.6 in May 2025 when gas was cheap (tariffs). #3 oil note: concede every caveat. #14 NFIB: concede first-round echo.
8. **Low–medium. #6 productivity, #7 ULC noise, #5 anecdotal catch-up, #10 six years, #17 V/U rising.** ULC quarterly sd 3.0 pp even in 2018–19, but 4q/8q steady at 2.39/1.92. Real ECI wages −0.53 pp vs headline PCE (motive for catch-up, not evidence). Time above target: 67 months through Sep. V/U 0.87 → 1.06 since Dec 2025.

## Bridge-line verdict (support only; not rewritten)
- **"Doesn't show second-round effects": supported, with a logical caveat.** Upstream PPI cannot distinguish first- from second-round mechanisms on its own (Codex R1-F05: PPI prices can embed wages and expectations); absence must come from 3A's wages, ULC and expectations. Services inputs to stage-1 producers (WPSID5112) at their highest since 2018 (3m ann. 35.5, y/y 19.2).
- **"Lengthens the first round": supported but weakened.** For: stage 1 +14.1% y/y; freight and food lags; oil note effects build within ~8 quarters. Against: Brent ~$92 since Nov 4; Oct stage 2 −0.21% m/m; energy's contribution to stage 1 negative. Fits "bigger" as well as "longer".
- **"Raises their risk": supported conceptually** (BB p.9, p.18; oil note "risks are mounting"; short-run expectations +0.9 pp since Feb). Empirically weak: BB catch-up ≈ 0; short-run expectations respond slowly (0.124); no de-anchoring 2021–23; V/U < 1.2.

## Slide-worthiness (stress-test rating, 1–5)
| Exhibit | Rating | Reason |
|---|---|---|
| BB channel table | 3 | Labor leg argues against us unless the p.18 expectations channel sits beside it. |
| V/U then vs now | 4 | Like-for-like; hard to attack. |
| Wages vs benchmark | 2 | Sign flips across measures and trends. |
| ULC 4q/8q | 4 | Nets out productivity; strongest "no wage second round" fact. |
| Labor share | 3 | Record low holds on new vintage; opens a nonlabor-share (possibly margins) reading. |
| Catch-up surveys | 2 | Plans and anecdotes only. |
| Expectations short vs long | 3 | Split by respondent type survives; Michigan long-run comparison does not. |
| Gas co-movement | 2 | Descriptive, small sample, straddles the Michigan mode break. |
| Underlying-trend panel | 4 | Full range pre-empts cherry-picking. |
| Trimmed-mean bias | 3 | Good Q&A backup; "not clear-cut"; skewness ends June. |
| Time above target | 4 | Exact; say "67 months". |
| Policy timeline | 2 | Context; invites policy questions this slide defers. |

## Worth a look
1. Michigan mode break affects `C_q4_summary.csv` row 3, C's report and possibly the 2024–26 Michigan gas correlations. The 2018–19 baseline 2.47 is phone era.
2. The Logan measure's 3m rate was higher in Jan–Feb 2026 (4.25, 4.07) than in Oct est.; January may be residual seasonality (not tested).
3. Slide 2's "upstream pressure at a record" refers to the stage 1 index level. On rates, stage 1 y/y 14.1 ranks 16th of 106 months; peak 22.4 May 2021 (`10_slide2_research/outputs/C_q8_ppi_stages_summary.csv` row 12).
4. Implied nonfarm business output price (+4.05%) well above core PCE (3.12). Separating oil rents and other nonlabor payments from profit margins needs PRS85006143 or BEA profits by industry.

## Spot checks
1. `D_q9_checks.csv` row 48: implied output price +4.052% (2025Q3→2026Q3).
2. `D_q9_checks.csv` row 4: 4 months Oct 2025–Sep 2026 with 3m ≥ 3.461.
3. `outputs/text/bb2023.txt` PDF p.19 (printed 18): "short-run inflation expectations feed fairly quickly into wages".
4. `umich_px5web202506.pdf` p.1: "June's median now matches the peak reading from mid-2022".
5. `outputs/text/logan_2026-11-10_paragraphs.txt` para 169: "expect PCE inflation to run around 3.1 percent".

## What to verify (agent)
- Size of the Michigan web-mode effect (higher web expectations: secondary source, unverified; Oct 2024 UMich report not located).
- Q4 SPF (Nov 16), Michigan final (Nov 20), official Oct PCE (Nov 25) feed revision triggers.
- Implied deflator from the identity, not the published series.
- Richmond CFO values (B's hand transcription) not re-checked.
- BB page cites from A not re-verified except printed pp.9 and 18.

## Coordinator review
**Verified:**
- UMich web-series PDF text: "After four months of sharp increases to start 2025, long-run expectations fell in May and June. June's median now matches the peak reading from mid-2022, but the three-month-moving average remains above mid-2022." ✔ The mode-break point stands; C's Michigan 5–10y "above its 2021–23 peak" must carry this caveat (amended in report_C and on the workbook).
- BB printed p.9: "the longer the episode, or the lower γ, the stronger the effect on steady-state inflation." ✔
- BB printed p.18: "short-run inflation expectations feed fairly quickly into wages" ✔ — **but the sentence continues "although, as we shall see below, short-run inflation expectations react slowly to actual" inflation.** Any spoken use of the first clause must carry the second; otherwise it is selective quoting. Flagged in FINAL.
- Implied output price: (ULC index ratio 2026Q3/2025Q3) ÷ (labor share index ratio) − 1 = **4.052%**. ✔
- SCE 1y: 3.00 (Feb 2026) → 3.914 (Oct 2026). ✔

**Corrected:** none in D's files.

**Could not check:** the WPSID5112 ranking (slide 2 data, not recomputed); Michigan 1y 6.6 May 2025 (not recomputed); size of the mode effect.

**Interpretive notes:** D's ranking makes the case thinner than the roadmap assumed: the hard labor-cost data (ULC 8q 1.9, V/U 1.06) are the "no second round yet" evidence, while the "risk" rests on short-run expectations and firm price plans. The labor share/implied deflator point (prices running ahead of unit labor costs) is the most important new fact for 3B and the decision section.
