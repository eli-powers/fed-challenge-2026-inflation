# Notes, Agent A (baseline and oil assumption), 2026-11-15

Scripts (rerun from project root with `python3 -I`): `code/A_01_pull.py` (downloads), `A_02_spf.py`, `A_03_sep.py`, `A_04_jumpoff.py`, `A_05_oil.py`; parsers in `A_common.py`. `A_02_spf.py [raw_dir]` autodetects the survey from the latest non-empty row of medianLevel.xlsx, so a Q4 folder works unedited: pull with `A_01_pull.py spf 2026Q4 <date>`, then `A_02_spf.py <that folder>` and `A_04_jumpoff.py <that folder>`. (Not tested on a Q4 file because none exists; tested only on 2026Q3 and by construction on the 2026Q2 row.)

## Q1.1 SPF Q3 2026 median core PCE (SA, percent, annualized q/q unless stated)
Variable meaning (documentation, "File Structure"): COREPCE1 = quarter before the survey (forecasters know BEA's advance estimate), COREPCE2 = survey quarter, COREPCE3-6 = next four quarters; COREPCEA/B/C = Q4/Q4 for the survey year and the next two. Quarterly = annualized q/q change of the quarterly average of monthly index; annual = Q4/Q4.

| Variable | Period | Median | P25 | P75 | IQR |
|---|---|---|---|---|---|
| COREPCE1 | 2026Q2 (jump-off, effectively actual) | 3.40 | 3.40 | 3.40 | 0.00 |
| COREPCE2 | 2026Q3 | 2.70 | 2.60 | 3.20 | 0.60 |
| COREPCE3 | 2026Q4 | 2.6158 | 2.477 | 2.90 | 0.423 |
| COREPCE4 | 2027Q1 | 2.5766 | 2.40 | 2.90 | 0.50 |
| COREPCE5 | 2027Q2 | 2.4313 | 2.30 | 2.70 | 0.40 |
| COREPCE6 | 2027Q3 | 2.3261 | 2.20 | 2.50 | 0.30 |
| COREPCEA | 2026 Q4/Q4 | 3.2876 | 3.2002 | 3.473 | 0.273 |
| COREPCEB | 2027 Q4/Q4 | 2.4004 | 2.2499 | 2.7274 | 0.4775 |
| COREPCEC | 2028 Q4/Q4 | 2.1586 | 2.0436 | 2.40 | 0.3564 (26 respondents) |

- **Quarters given: 2026Q2 (jump-off) through 2027Q3. There is no published 2027Q4 quarterly figure.** Published medians (rounded) agree with the survey PDF Table 3 (3.4, 2.7, 2.6, 2.6, 2.4, 2.3; 3.3, 2.4, 2.2). 30 respondents.
- **Derived 2027Q4 q/q annualized = 2.268** (not published). Formula: 1 + q4/100 = (1 + B/100)^4 / [(1+q1/100)(1+q2/100)(1+q3/100)], with q1..q3 = 2.5766, 2.4313, 2.3261 and B = 2.4004 (inverts Q4/Q4 = prod (1+q_i/100)^(1/4) - 1; round trip checked in code). Approximate because the quarterly medians and the annual median each come from different respondents' middle values (the median of a sum is not the sum of medians), and because respondents give quarterly and annual numbers separately. Sensitivity: B +/- 0.05 moves it to 2.468 / 2.068 (x4). Cross-check: repeating the 2027Q3 pace in Q4 gives 2027 Q4/Q4 = 2.415 vs published 2.400, so the quarterly path and annual median are close but not identical.

## Q1.2 Dispersion
- Dispersion_1.xlsx publishes P25, P75 and D1 = P75 - P25 for the five quarterly horizons T..T+4 (COREPCE2..6). **No annual (A/B/C) and no COREPCE1 dispersion is published**, so those P25/P75 are computed from SPFmicrodata.xlsx with Hazen percentiles (position (i-0.5)/n); this method reproduces all 10 published quarterly percentiles exactly (checked in code). Labeled "derived" in the CSV.
- Respondent range 2026Q3: min 1.74 / max 4.50; 2026Q4: 1.11 / 4.40; 2027Q3: 0.75 / 3.60; 2026 Q4/Q4: 2.66 / 4.19. Individual-response file is a single xlsx download (24.6 MB); respondent IDs are anonymized.

## Q1.3 Survey dates
Q3 2026: deadline **8/11/26**, news release **8/14/26** (spf-release-dates.txt: "2026 Q3 8/11/26 8/14/26"; header "True Deadline Date / News Release Date"). Survey PDF says "Release Date: August 14, 2026". Q2: 5/12/26 and 5/15/26. Documentation: questionnaires go out after BEA's advance GDP report (Jul 30 2026; the date itself is not in the file), so forecasters knew advance 2026Q2 core PCE.

## Q1.4 Q4 2026 SPF
Not released. Survey page spf-q4-2026 returned 404 at ~17:40 EST Nov 15; the SPF main page lists Q3 2026 as latest; spf-release-dates.txt has no Q4 2026 row. Scheduled date of Mon Nov 16 is from the brief only and is **unverified** (the Philadelphia Fed release calendar renders client-side; web search did not confirm). Last year's Q4 2025 release was Nov 17 2025 (shutdown-delayed), so mid-November is typical. Code is ready (see top).

## Q1.5 Sep 2026 SEP (Q4/Q4, percent; meeting Sep 15-16, 2026)
Core PCE: median 2026 3.4, 2027 2.5, 2028 2.2, 2029 2.0; central tendency 3.3-3.4, 2.3-2.6, 2.0-2.2, 2.0; range 2.8-3.5, 2.1-2.7, 2.0-2.3, 2.0-2.1. No longer-run value for core PCE (blank cell in table). June: 3.3, 2.5, 2.1 (2029 not published in June). Headline PCE median 3.7, 2.3, 2.1, 2.0, LR 2.0. Table in `outputs/A_q1_sep.csv`.

## Q1.6 Jump-off (calculations, not forecasts; FRED PCEPILFE latest vintage, realtime 2026-10-29)
Actual core PCE, q/q annualized from quarterly averages: 2025Q4 2.49, 2026Q1 3.94, 2026Q2 3.31, 2026Q3 **2.47**. Q4/Q4: 2025 2.77. y/y (quarterly avg): 2026Q3 3.05.
- **2026Q3 forecast error:** SPF median 2.70 vs actual 2.47 = -0.23 pp (actual 2.47 is 0.13 pp below the P25 of 2.60 and 0.73 pp below the P75 of 3.20).
- 2026Q2: SPF jump-off 3.40 vs actual 3.31 (latest vintage) = -0.09; vs the Aug-11 vintage 3.42.
- **Vintage break:** the data vintage changed between the Aug 26 and Sep 30 ALFRED vintages (consistent with the BEA annual update; not confirmed against a BEA date here). 2026Q1 q/q was 4.42 (Aug vintage) vs 3.94 now; 2026Q2 3.42 vs 3.31; 2025 Q4/Q4 2.85 vs 2.77. SPF Q3 and the Sep SEP were formed on the old vintage.
- SPF consistency: actual Q1, Q2 (latest) + SPF Q3, Q4 medians give 2026 Q4/Q4 = 3.14 vs the published COREPCEA 3.29. If 2026Q4 = SPF 2.6158 given actual Q1-Q3, Q4/Q4 = 3.08. Q4 q/q needed to reach the published 3.29 = 3.44.
- **Oct estimate:** Oct level from Sep x 1.00295 gives y/y 3.2424 (matches stated 3.24). (i) Nov, Dec m/m = 0.295: 2026Q4 q/q ann. 3.61, 2026 Q4/Q4 **3.33**, Dec y/y 3.36. (ii-a) Nov, Dec m/m = monthly equivalent of SPF's 2.6158 (0.2154/month): Q4 q/q 3.28, Q4/Q4 **3.25**, Dec y/y 3.20. (ii-b) Nov, Dec m/m solved so that Q4 q/q = SPF 2.6158 given our Oct estimate: 0.053/month, Q4/Q4 **3.08**, Dec y/y 2.87.
- Our Oct estimate is a bottom-up estimate with a band (Headline sheet); the workbook cell values are not cached, so 0.295 comes from the brief.

## Q2 Oil assumption (details: outputs/A_q2_proxy_note.md)
Proxy: Aug 2026 STEO (released 8/11/26; modeling completed 8/6/26; last historical month Jul 2026). Brent quarterly (mean of monthly): 2026Q3 85.26, Q4 78.00, 2027Q1 74.00, Q2 71.00, Q3 68.00, Q4 65.00. July STEO is $8-11 lower in 2026Q3-Q4. Brent futures on 2026-08-11 (Yahoo, secondary; 2027 contract months only): 2027Q1 81.48 ... 2027Q4 75.76. EIA spot Brent on 8/11: $93.26; prior 20 trading days mean $90.19; WTI $84.77, spread $8.49.

## Worth a look
1. **Vintage break between the SPF baseline and today's data** (annual update): see above. The Q3 SPF's 3.29 for 2026 Q4/Q4 is about 0.15 pp above what SPF's own quarterly medians give on current history.
2. **Oil has reverted:** EIA spot Brent monthly mean $123.93 in Oct, but $92.14 on Nov 11 (Nov mean to Nov 11 $96.92); Brent-WTI spread $8.49 on Aug 11 vs $2.52 on Nov 11. The Q3 SPF baseline predates both the Sep-Oct spike and the retracement.
3. **STEO vs futures disagree by about $8/bbl in 2027** (Aug STEO 2027 mean 69.5 vs futures 78.2) and the Aug STEO's 2026Q3 forecast (85.26) undershot actual (96.30) by $11.
4. 2026Q3 actual core PCE (2.47) came in below the Q3 SPF median (2.70) and below its P25 (2.60) while the Q2 survey had 2.94 for Q3: the panel revised Q3 down by 0.24 even before the print.
5. Dispersion is not unusual: IQR for the survey quarter is 0.60 (68th percentile since 2007, median 0.45; max 1.32 in 2022Q1); T+4 0.30 is low (15th percentile). A few respondents are far outside the pack (IDs with 3.6-4.5 flat paths; one at 0.75 in 2027Q3).
6. COREPCE1 (2026Q2) is not a pure actual: two respondents entered 3.4155/3.4187.
7. Survey quote note: the SPF Q4 2025 survey lacked jump-off values (shutdown); not relevant to Q3 2026.

## What to verify
- Q4 2026 SPF release date and contents (Nov 16 per brief).
- Annual-update date vs the vintage break.
- Whether Yahoo BZ contract-month closes match ICE/CME settlements.
- That respondents condition on something like STEO (unknowable; the SPF special surveys do not ask).
