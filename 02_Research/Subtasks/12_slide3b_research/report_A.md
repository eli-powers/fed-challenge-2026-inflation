Status: Audited — converged R2 (Codex, Nov 15)

# Agent A report: baseline and implied oil assumption (Sonnet 5.5, 2026-11-15)

## Findings
**Q1.1 Q3 2026 SPF median core PCE** (SA; quarterly = q/q annualized; annual = Q4/Q4; 30 respondents; `03_Data/Raw/PhilFed_SPF_2026Q3_2026-11-15/medianLevel.xlsx`, sheet COREPCE, row 233) [O]
- COREPCE1 (2026Q2, quarter before survey) 3.40; COREPCE2–6 = 2026Q3–2027Q3: 2.70, 2.6158, 2.5766, 2.4313, 2.3261.
- COREPCEA/B/C (Q4/Q4 2026/2027/2028): 3.2876, 2.4004, 2.1586.
- No published 2027Q4 quarterly. **Derived 2027Q4 = 2.268** from (1+B/100) = Π_{2027Q1..Q4}(1+q/100)^(1/4). Approximate (medians from different respondents); B ±0.05 → 2.07 / 2.47.

**Q1.2 Dispersion** (P25/P75). Published (`Dispersion_1.xlsx`) for COREPCE2–6 only: 2026Q3 2.60/3.20; 2026Q4 2.477/2.90; 2027Q1 2.40/2.90; 2027Q2 2.30/2.70; 2027Q3 2.20/2.50. Annual horizons derived from `SPFmicrodata.xlsx` (Hazen percentiles; method reproduces all 10 published quarterly percentiles): 2026 3.20/3.473; 2027 2.25/2.727; 2028 2.04/2.40 (26 resp.).

**Q1.3 Survey dates.** Q3 deadline Aug 11, 2026; release Aug 14, 2026 (`spf-release-dates.txt`; `spfQ326.pdf`) [O].

**Q1.4 Q4 SPF.** Not released at ~17:40 ET Nov 15 (`spf-q4-2026` 404; not in release-dates file) [O]. Nov 16 date unverified (from brief). Parser autodetects the survey from the latest row; untested on a real Q4 file.

**Q1.5 Sep 2026 SEP core PCE (Q4/Q4)** (`03_Data/Raw/FOMC_SEP_2026-09_2026-11-15/fomcprojtabl20260916.htm`) [O]: median 2026 3.4, 2027 2.5, 2028 2.2, 2029 2.0; central tendency 3.3–3.4 / 2.3–2.6 / 2.0–2.2 / 2.0; range 2.8–3.5 / 2.1–2.7 / 2.0–2.3 / 2.0–2.1. June medians 3.3 / 2.5 / 2.1.

**Q1.6 Jump-off** (FRED PCEPILFE, vintage 2026-10-29; calculations, not forecasts)
- Actual q/q ann.: 2026Q1 3.94, Q2 3.31, **Q3 2.47**; 2025 Q4/Q4 2.77.
- SPF 2026Q3 forecast error: 2.70 vs 2.47 = −0.23 pp (below SPF P25).
- Oct est. check: Sep index × 1.00295 → 3.242% y/y (matches 3.24).
- 2026 Q4/Q4 if Nov–Dec m/m = (i) 0.295 → 3.33; (ii-a) 0.215 (monthly equivalent of SPF 2026Q4 pace) → 3.25; (ii-b) m/m that makes Q4 = SPF 2.6158 given our Oct → 0.053 → 3.08. SPF published 2026 Q4/Q4 3.2876.

**Q2 Implied oil assumption.** No published SPF oil assumption. Primary proxy: **Aug 2026 STEO** (released Aug 11 = SPF deadline day; modeling Aug 6) [O]. Quarterly Brent (mean of monthly): 2026Q3 85.26, Q4 78.00, 2027Q1 74.00, Q2 71.00, Q3 68.00, Q4 65.00. Alt: Jul STEO 74.00 / 70.00 / 67.67 / 65.67 / 64.00 / 62.00. Futures [2, Yahoo BZ, 2027 months only, Aug 11]: 2027Q1 81.48, Q2 78.72, Q3 76.99, Q4 75.76. EIA spot Brent Aug 11 $93.26; prior-20-day mean $90.19; Brent–WTI $8.49. EIA RCLC1–4 files end 2024-04-05 (unusable); ICE licensed; CME 403.

## Slide-worthiness
- SPF baseline path as spine: 4/5 — published, quarterly, IQR band; must be dated (pre-spike, pre-revision).
- SEP as spoken line: 3/5 — 3.4 / 2.5 / 2.2 vs SPF 3.29 / 2.40 / 2.16; Q4/Q4 only.

## Worth a look
1. Vintage break between Aug 26 and Sep 30 ALFRED vintages: 2026Q1 4.42 → 3.94; Q2 3.42 → 3.31; 2025 Q4/Q4 2.85 → 2.77. SPF quarterly medians + revised H1 actuals give 2026 Q4/Q4 3.14 vs published 3.29.
2. Brent retraced: Oct avg $123.93 → $92.14 Nov 11; Brent–WTI $8.49 (Aug 11) → $2.52 (Nov 11).
3. STEO vs futures ~$8/bbl apart in 2027 (69.5 vs ~78.2). Aug STEO 2026Q3 85.26 undershot actual 96.30.
4. SPF cut 2026Q3 from 2.94 (Q2 survey) to 2.70; actual 2.47.
5. Dispersion unremarkable (survey-quarter IQR 0.60, 68th pct since 2007).
6. Slide1 workbook Headline has no cached values; 0.295 came from the brief.

## Spot-check examples
1. `medianLevel.xlsx` COREPCE row 233. 2. `Dispersion_1.xlsx` COREPCE row 242. 3. `outputs/A_q1_spf_baseline.csv` DERIVED 2027Q4 2.2679. 4. `aug26_base.xlsx` 2tab BREPUUS Aug 2026 = 87, Sep 85, Oct 80. 5. `outputs/A_q1_jumpoff.csv` (ii-b) 3.0819.

## What to verify
Q4 SPF on Nov 16; BEA annual-update date vs the vintage break; Yahoo BZ vs exchange settlements; Jul vs Aug STEO as primary proxy.

Files: `notes_A.md`, `sources_A.md`, `code/A_common.py`, `code/A_01_pull.py`–`A_05_oil.py`, `outputs/A_*`. Raw: `03_Data/Raw/{PhilFed_SPF_2026Q3, FOMC_SEP_2026-09, FRED_PCEPILFE_latest, EIA_STEO, EIA_NYMEX_WTI_futures_RCLC, Yahoo_BZ_futures_curve}_2026-11-15/`.

## Coordinator review
**Verified (independent scripts, raw files):**
- SPF row 233 values and derived 2027Q4 = 2.2679 (own formula) — match.
- PCEPILFE (vintage 2026-10-29) quarterly averages: 2026Q1 3.937, Q2 3.314, Q3 2.468 ann. — match.
- Oct est.: Sep 130.902 × 1.00295 / Oct 2025 127.165 → 3.242% — match.
- Aug STEO `2tab` BREPUUS monthly (Jul 83.77 actual, Aug 87, Sep 85 … Dec 2027 64) → quarterly 85.26 / 78.00 / 74.00 / 71.00 / 68.00 / 65.00 — match.
- SEP table core PCE row (median 3.4 / 2.5 / 2.2 / 2.0, CT, range, June) — match.
**Corrections:** none.
**Not checked:** dispersion microdata percentiles (trusting the published-file reproduction test A reports); Yahoo futures [2].
**Coordinator notes for C (binding on design):**
- 2026Q3 is now actual (2.47). Forecast quarters are 2026Q4–2027Q4. Show actual 2026Q1–Q3 + SPF path, and the SPF-as-published 2026Q3 as a reference. Build Q4/Q4 2026 from actual Q1–Q3 + scenario Q4; also show the SPF's published annual medians.
- Aug STEO = central proxy (dated to the deadline); Jul STEO and Yahoo futures = sensitivity rows.
- The Aug STEO sits $8–10 below realized/futures: a lower assumed path makes every scenario's gap larger. Disclose.
**Worth a look (coordinator):** Aug STEO assumed Brent falling to $65 by 2027Q4; the Nov 11 spot ($92) is already ~$14 above the Aug STEO's 2026Q4 ($78). So even the "baseline" oil path implies a positive gap.
