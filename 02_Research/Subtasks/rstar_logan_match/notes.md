# Matching Logan's "eight published models" (r*, 1–1.85%)

**Question (Eli, Nov 16):** identify the r* estimates behind the neutral-rate range. Eli attributed it to Bowman. It is from **Logan (Dallas), Nov 10, 2026**: "Across eight published models, estimates of the neutral real interest rate currently range from 1 to 1.85 percent." The "13" is her separate "baker's dozen" of inflation-expectations surveys. Bowman's Nov 10 speech gives no r* range.

The speech names no models and has no footnotes. Her earlier speeches (Nov 2024, Sep 2025, Feb 2026) also name none; each links the low end to the NY Fed r* page and the high end to the Richmond Fed page.

## Reconstruction (script: `code/latest_rstar.py`; raw: `03_Data/Raw/rstar_2026-11-16/`)

| Model | Value (real %) | Vintage | Status |
|---|---|---|---|
| Holston–Laubach–Williams (2023), NY Fed, one-sided | 1.009 | 2026Q2 (Aug 28 release) | **Confirmed low end** (linked in speech, matches "1") |
| Lubik–Matthes, Richmond Fed, median | 1.850 | 2026Q2 (updated Sep 23) | **Confirmed high end** (linked in speech, matches "1.85") |
| Laubach–Williams (2003), NY Fed, one-sided | 1.652 | 2026Q2 | Probable (same NY Fed page) |
| Ferreira–Lott–Richards, Fed Board FEDS Note | 1.731 | date code 2026.5 = 2026 H2 (inferred; file updated Nov 5) | Probable |
| Cúrdia medium-run, SF Fed EL 2026-22 | 1.50 (Fig. 1, 2026q3; text "approximately 1.5%") | as of Aug 2026 | Probable |
| Glover–Oliyide, KC Fed | 1.460 | Sep 2026 | Probable |
| Zaman, Cleveland Fed | 1.452 (Q2) / 1.456 (Q3, posted Nov 6) | 2026Q2/Q3 | Probable |
| 8th model | — | — | **Not identified** |

Candidates checked and excluded or unavailable: NY Fed DSGE short-run r* 1.9 for 2026 (Sep 18) is outside the range, so likely excluded; DGGT, Davis et al., Johannsen–Mertens, Lewis–Vazquez-Grande, Kiley: no 2026 U.S. update found. Unchecked leads for the 8th: D'Amico–Kim–Wei (DKW), Christensen–Rudebusch (FRBSF WP 2026-19), St. Louis Fed Kliesen post (May 4, 2026).

Selection basis for the "probable" rows (candidates, not confirmed members of Logan's eight): PIMCO's nine-measure consolidation (Sep 23, 2026) lists all of them, and each current value sits inside 1–1.85%. This is inference, not confirmation.

## Caveats
- Concepts differ: HLW/LW/LM are trend r*; Cúrdia is a medium-run rate (model data end 2025Q4); the DSGE value is short-run.
- One-sided HLW was 1.09 in 2026Q1, so the low end depends on vintage. Next NY Fed release Nov 27 (after finals).
- Cúrdia, KC, FLR, Zaman values were later verified against source pages by a subagent (see Update below); page/URL provenance is the subagent's.

## Update (Nov 16, later): verification, 8th model, real policy rate
- Verified by subagent against source pages/files: Cúrdia ~1.5 ("approximately 1.5%"; Figure 1 medium-run 2026q3 = 1.503; quarters after 2025q4 look projected. The 1.51 used earlier is a Figure 2 policy-rule statistic, not r*, so use 1.50). KC Glover–Oliyide Sep 2026 = 1.460 real (page shows no update date). FLR US 2026.5 = 2026:H2, inferred from the semiannual sequence (file starts 1960 = 1960:H1, steps 0.5); the data-definitions PDF only says date_h is "Half-yearly date corresponding to the estimate period" (`03_Data/Raw/rstar_2026-11-16/FRB_FerreiraLottRichards_rstar_data_description_dl2026-11-16.pdf`), real, updated Nov 5; current half-year partly projected. Zaman 2026Q3 = 1.456 real (updated Nov 6); the Q2-data vintage gave 2026Q2 = 1.365 (checked by me).
- 8th model: still unidentified. PIMCO's nine = Davis-Mills, LW, HLW, LM, HZ/ZH, FEDS Notes (FLR), DGGT, Cúrdia, GO. DGGT is ~0.5 (Liberty Street, Feb 25, 2026), outside range; Davis-Mills value not found at primary source; DKW has no public current series. No press coverage names the eight.
- Real policy rate (FRED raw, `code/fetch_policy_rate.py`): EFFR 3.88 (Nov 13); Cleveland Fed 1-yr expected inflation 3.04 (Nov) → 0.84 real. Alternatives: Logan 3.1 → 0.78; our 13-measure average 3.38 → 0.50; SPF headline PCE next 4q 2.41 (Q3 survey, stale; Q4 not posted Nov 16) → 1.47.
- Correction (Nov 16): Q4 SPF IS posted (released Nov 16; spf-q4-2026 HTML page, read by subagent, PDF not parsed). Headline PCE quarterly medians 2026Q4–2027Q3: 3.5, 2.6, 2.3, 2.3 → compounded next-4-quarter ≈ 2.67 → real fed funds ≈ 1.21. Core PCE: 3.0, 2.7, 2.6, 2.4. Headline PCE Q4/Q4: 2026 3.7, 2027 2.4. Rerun the 13-measure expectations aggregate (it still uses Q3 SPF 2.41).

## Slide build (Nov 17)
Eli asked for two versions: (A) real rate deflated by headline CPI (Cleveland Fed 1-yr) vs headline PCE (SPF), no bands; (B) SPF headline vs core PCE with published r* bands. Short-run DSGE dot recolored gold (house gold #F2CC6B), not gray.
- Script: `code/build_rstar_slide.py` → `01_Finals/data/SlideRstar_Policy_Data.xlsx` and `output/slide_A_cpi_vs_pce.png`, `output/slide_B_headline_vs_core_pce.png`, `output/slide_B_alt_next4q.png`.
- SPF Q4 2026 (released Nov 16) from `forecast_3b/raw/2026-11-16/medianLevel.xlsx` (unrounded medians). Main window = Eli's 2026Q4–2027Q3 (cols 2–5). Real rates: Cleveland CPI 0.84; SPF headline PCE 1.20; SPF core PCE 1.20 (identical in this window); alt window 2027Q1–Q4: headline PCE 1.52, core PCE 1.36. Eli's 1.21 used rounded page medians.
- Published bands: HLW ±1 S.E. final obs (1.525); LW ±1 S.E. final (1.685); LM 16th–84th; Zaman 68%; KC 68%; Cúrdia 90%; DSGE 68% (Liberty Street table, Sep 18); FLR none.
- Deliberate style-guide deviation: dot/scatter chart (guide covers line/bar only).
- Nov 17 (Eli): Cúrdia band converted from published 90% (−0.37 to 3.30) to ≈68% (0.37 to 2.60): each side divided by 1.645, normality assumed. Check: the same rule applied to Zaman's published 90% band gives 0.80–2.16 vs its published 68% band 0.79–2.14. Marked with * on the slides; source line discloses. Deck slides 14–15 updated.
