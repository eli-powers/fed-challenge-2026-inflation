Status: Audited — converged R3 (Codex, Nov 15; fixes from R1-F01/F02/F04–F07 applied, see 06_Audits/slide3a_research/R1_claude.md)

# Agent C report: expectations and underlying trend (Q4, Q6, Q8) (Sonnet 5.5)

Outputs in `outputs/`, scripts `code/C_*.py` (rerun from the project root with `python3 -I`); `notes_C.md`, `sources_C.md`. Raw downloads: `03_Data/Raw/S3A_expectations_underlying_2026-11-15/` and `03_Data/Raw/S3A_fomc_statements_2026-11-15/`. Every Oct 2026 PCE-based value is "est." (audited `04_oct_pce_build` lines). Nothing paywalled; `C_paywalled.csv` records the Q4 SPF 404.

## Q4. Expectations (`C_q4_expectations.csv`, `C_q4_summary.csv`, `C_q4_gas_comovement.csv`, `C_q4_gas_latest_change.csv`, `C_q4_logan_aggregate.csv`)

| Series | Latest (release) | 2021–23 peak | 2018–19 avg |
|---|---|---|---|
| Michigan 1y median | **4.3, Nov PRELIMINARY** (Nov 6; final Nov 20, after cutoff) | 5.4 (2022-03) | 2.71 |
| Michigan 5–10y median | **3.4, Nov PRELIMINARY** (Oct 3.5) | 3.2 (2023-11) | 2.47 |
| SCE 1y median | 3.91, Oct (released **Nov 9**) | 6.78 (2022-06) | 2.76 |
| SCE 3y median | 3.29, Oct | 4.21 (2021-10) | 2.78 |
| SCE 5y median | 3.00, Oct | 3.02 (2022-03); series starts 2022 | n/a |
| 5y breakeven (T5YIE) | 2.30 daily (Nov 13); Oct avg 2.40 | 3.41 monthly / 3.59 daily (2022-03) | 1.79 |
| 10y breakeven (T10YIE) | 2.24 daily; Oct avg 2.35 | 2.88 monthly / 3.02 daily (2022-04) | 1.91 |
| 5y5y forward (T5YIFR) | 2.18 daily; Oct avg 2.30 | 2.46 monthly (2023-10) / 2.67 daily (2022-04) | 2.03 |

- **SPF Q3 2026 medians** (released Aug 14): headline PCE current year 3.61, next year 2.30, 5y 2.50, 10y 2.20 (2018–19 avg 1.85 / 1.99 / 1.99 / 2.00). Core PCE 3.29 / 2.40. Headline CPI 3.56 / 2.33, 5y 2.60, 10y 2.30. Core CPI 2.78 / 2.56.
- **Q4 2026 SPF: not released as of 2026-11-15 17:49 EST** (Q4 URL 404; `C_q4_spf_q4_check.csv`). Rerun `code/C_q4_spf_check.py` after Nov 16.
- **Gas (FRED GASREGW, weekly):** Oct average $4.309 vs $3.060 a year earlier (+$1.25, +40.8%). Nov average (two weeks) $4.074. Latest weekly $3.995 (Nov 9), down from $4.354 (Oct 5).
- **Latest 12m change, Oct:** Michigan 1y +0.1 pp (4.7 vs 4.6); SCE 1y +0.68 pp. Nov (prelim, partial): Michigan 1y −0.2 pp; gas +$1.02 (+33.6%).
- **Correlations** (descriptive; 12m-change correlation, level correlation in brackets; windows end Oct 2026):

| Pair | 2018-01–2026-10 | 2021–23 | 2024–26 |
|---|---|---|---|
| Michigan 1y | 0.37 (0.66) | 0.89 (0.59) | −0.37 (0.15) |
| SCE 1y | 0.70 (0.65) | 0.91 (0.64) | 0.40 (0.69) |
| Michigan 5–10y | −0.06 (0.52) | 0.58 | −0.63 |
| SCE 3y | 0.47 (0.44) | 0.67 | 0.21 |
| 5y5y | 0.61 (0.72) | 0.55 | 0.36 |

n = 94 / 36 / 34; autocorrelated. The long-run contrast is **not clean**: SCE 3y and 5y5y still co-move with gas; only Michigan 5–10y is near zero on the full-window change.
- **Logan's 13 surveys:** `Inflation_Expectations.xlsx` simple average **3.38** (median 3.30); **does not reproduce her ~3.1**. Groups: household 4.67, business 3.57, professional 2.26, market 3.04. Dropping the Conference Board (5.8, a mean) gives 3.18. Her 13 are unpublished.

## Q6. Underlying trend (`C_q6_underlying.csv`, `C_q6_summary.csv`, `C_q6_logan_measure.csv`, `C_q6_roadmap_check.csv`)

| Measure (Sep 2026 unless noted) | Latest | 2018–19 avg | 2021–23 peak |
|---|---|---|---|
| NY Fed MCT | 2.84 (band 2.49–3.21; Aug revised to 2.56) | 1.87 | 5.66 (2022-06) |
| Dallas trimmed mean 12m / 6m ann / 1m ann | 2.26 / 2.42 / 2.84 | 1.94 / 1.97 / 1.95 | 4.85 (2022-08) / 5.28 / 7.43 |
| Cleveland median PCE 12m | 2.67; 1m 0.247, 3m ann 2.75, 6m ann 2.76 | 2.34 | 5.90 (2022-09) |
| Cleveland median CPI, Oct, 12m | 2.80 (1m ann 3.7) | 2.70 | 6.92 (2023-02) |
| Cleveland trimmed-mean CPI, Oct, 12m | 2.89 (1m ann 4.5) | 2.21 | 7.17 (2022-09) |
| BEA market-based core PCE 12m / 3m / 6m ann | 3.12 / 2.94 / 2.85 | 1.57 | 5.45 (2022-09) |
| Core PCE 12m / 3m / 6m ann (reference) | 3.12 / 2.90 / 2.92 | 1.77 | 5.64 |
| Supercore 12m / 3m / 6m ann, Sep | 3.60 / 3.37 / 3.43 | 2.25 | 5.33 (2022-10) |
| Supercore, Oct **est.** | 3.60 / 4.11 / 3.47 | | |
| **Logan measure** 12m / 3m / 6m ann, Sep | **3.21** / 2.61 / 2.91 | 2.27 | 4.82 (2022-01) |
| Logan measure, Oct **est.** | 3.24 / 3.46 / 3.01 (1m +0.29) | | |

- **MCT sectors:** contributions to the MCT's gap from its 2017–19 average (pp), not sector rates. Sep: goods 0.54, services ex housing 0.45, housing 0.04.
- **Logan measure:** BEA U20404/U20405 (vintage 2026-11-10); exact two-part Fisher removal (as in `core_ex_oer.py`): L376 (services ex energy) less L153 (housing), then less L190 (transportation services). Joint removal differs by < 0.002 pp. Validation: derived supercore matches BEA's published supercore (T20804 L28) within 0.007 pp over 2018–26 (Sep 3.595 vs 3.596).
- **Oct est. method:** audited build lines (98 lines, 54% of core), leaf-aggregated; overstates the exact Sep m/m by ~0.009 pp (not adjusted); no subgroup uncertainty band.
- **Roadmap check:** MCT 2.8 → 2.84 match; Dallas 2.3 → 2.26 match; Logan 3.2 → 3.207 match; core PCE 3.1 → 3.121; headline 3.6 → 3.649. `Fed_officials_2026-11/summary.md` quotes Waller's 3.7 headline (already known; slide 1 E7 uses BEA 3.6).
- **"Eight tenths above target-consistent pace"** implies 2.4 (3.2 − 0.8); the speech gives no source. Our measure's 2018–19 average is 2.27.

## Q8. Time above target (`C_q8_time_above_target.csv`, `C_q8_time_above_summary.csv`, `C_q8_policy_timeline.csv`, `C_q8_vintage_check.csv`, `C_q8_fomc_meetings_all.csv`)

| Measure (12m, current vintage) | First month above 2.0 | Last month ≤ 2.0 | Run through Sep | Through Oct | Six years reached |
|---|---|---|---|---|---|
| Headline PCE | Mar 2021 (2.64) | Feb 2021 (1.79) | 67 months = 5.58 yrs | 68 = 5.67 (est.) | Mar 2027 |
| Core PCE | Mar 2021 (2.13) | Feb 2021 (1.65) | 67 = 5.58 | 68 = 5.67 (est.) | Mar 2027 |
| Headline CPI (NSA) | Mar 2021 | Feb 2021 (1.68) | 67 = 5.58 | n/a | Mar 2027 |
| Core CPI (NSA) | Apr 2021 | Mar 2021 (1.65) | 66 = 5.50 | n/a | Apr 2027 |

- No month at or below 2.0 since the run began on any measure. Closest approach in the run: headline PCE 2.255 (Mar 2025), core PCE 2.134 (Mar 2021), core CPI 2.446 (Aug 2026).
- **"Nearly six years" rounds up:** 5.6 years through Sep, 5.7 with Oct est.; six years completes in Mar 2027.
- CPI: BLS did not collect Oct 2025 CPI (lapse in appropriations), so CPI y/y is missing for Oct 2025 and Oct 2026; treated as neither above nor below.
- **Policy timeline (20 target-range changes, Mar 2020–Oct 2026):**
  - Mar 3, 2020 −50 to 1.00–1.25; Mar 15, 2020 −100 to 0–0.25.
  - 2022: +425 bp over 7 hikes (Mar 16 +25; May 4 +50; Jun 15, Jul 27, Sep 21, Nov 2 +75 each; Dec 14 +50) to 4.25–4.50.
  - 2023: +100 (Feb 1, Mar 22, May 3, Jul 26) to 5.25–5.50.
  - 2024: −50 Sep 18; −25 Nov 7 and Dec 18 to 4.25–4.50.
  - 2025: −25 Sep 17, Oct 29, Dec 10 to 3.50–3.75.
  - Sep 16, 2026: +25 to 3.75–4.00 (12–0). Oct 28, 2026: hold (10–2).
  - All 20 match FRED DFEDTARU/DFEDTARL and the Board's Open Market Operations table (effective dates = statement date + 1).
  - Balance sheet: QE restarted Mar 15, 2020, uncapped Mar 23, 2020; taper announced Nov 3, 2021, doubled Dec 15, 2021; net purchases to end "early March" 2022 (Jan 26, 2022 statement; actual end date unconfirmed); QT announced May 4, 2022, started Jun 1, 2022 (caps $30bn/$17.5bn rising to $60bn/$35bn); slowed from Apr 1, 2025 (Treasury cap $25bn → $5bn); ended Dec 1, 2025 (Oct 29, 2025 statement); Dec 10, 2025: reserve-management purchases of shorter-term Treasuries as needed.

## Slide-worthiness (agent)
- Expectations, short vs long: **4.** Short-run far above 2018–19 (Michigan 4.3 vs 2.7; SCE 3.9 vs 2.8). Market/professional long-run ~2.2–2.5. Household long-run 3.3–3.4 (Michigan 5–10y above its 2021–23 peak). Michigan Nov prelim; SPF Q4 pending.
- Gas co-movement: **3.** Strong in 2021–23 (0.89/0.91), weak or negative for Michigan in 2024–26 (−0.37). Gas +41% y/y vs Michigan 1y +0.1 pp. Descriptive; small n; long-run contrast mixed.
- Underlying-trend panel: **4.** Clear range: trimmed 2.26, median PCE 2.67, MCT 2.84, core 3.12, Logan measure 3.21, supercore 3.60. Caveat: the Logan measure is a plateau (3.15 Sep 2025 → 3.21), not a rise; its 3m ann. is 2.61 (Sep), 3.46 (Oct est.).
- Time above target: **3.** Clean, but 5.6–5.7 years, and the start depends on vintage.
- Policy timeline: **2.** Context only.

## Worth a look
1. 13-survey aggregate 3.38 vs Logan's ~3.1; moves 0.2 with or without the Conference Board mean.
2. Logan's long-run "near 2 percent" holds for markets and SPF, not for Michigan 5–10y (3.4) or SCE 3y (3.29).
3. Michigan 5–10y now exceeds its 2021–23 peak; the current table labels the column "next 5 years" (horizon unconfirmed).
4. Vintage: core PCE Mar 2021 was 1.83 as first published, 2.20 on Sep 29, 2026, 2.13 now. On the original vintage the core run starts Apr 2021.
5. Logan's "eight tenths" implies 2.4, unsourced.
6. Hawkish dissents: Jul 29 (9–3: Hammack, Kashkari, Logan); Oct 28 (10–2: Cook, Hammack); Apr 2026 dissents over the easing bias.
7. Gas fell $4.35 (Oct 5) → $3.995 (Nov 9) while Oct supercore est. m/m softened (+0.27 from +0.37). Descriptive.

## Spot checks
1. `C_q6_logan_measure.csv` 2026-09: 12m 3.207; `C_q6_supercore_validation.csv` 2026-09: 3.595 vs 3.596.
2. `C_q4_summary.csv` "SCE 1y median": 3.914 (2026-10), release 2026-11-09; peak 6.776 (2022-06).
3. `C_q8_time_above_summary.csv` core PCE: run start 2021-03, 67 months; `C_q8_vintage_check.csv`.
4. `C_q6_roadmap_check.csv` MCT: 2.84.
5. `C_q8_policy_timeline.csv` 2026-09-16 and 2026-10-28.

`C_verification_checks.csv`: 19 cross-checks, 18 pass (the failure is the 3.38 vs 3.1 aggregate).

## What to verify (agent)
- SPF Q4 after Nov 16; Michigan final (Nov 20, after cutoff); Oct PCE actuals Nov 25.
- Michigan Nov prelim and 5–10y label from the pipeline copy (raw 2026-11-10); release date Nov 6 not independently confirmed.
- MCT column labels inferred from page text.
- Pre-Q3 2026 SPF release dates blank.
- Oct est. for supercore/Logan measure has no uncertainty band; market-based core has no Oct est.
- Board open-market page "Last Update: September 16, 2026".

## Coordinator review
**Verified:**
- Time above target, recomputed from the inflation pipeline's BEA index levels: headline and core PCE last ≤ 2.0 in Feb 2021; 67 consecutive months above 2.0 through Sep 2026; minimum within the run 2.255 (headline) and 2.134 (core); Sep 12m 3.649 / 3.121. ✔
- Logan measure, independent Törnqvist removal of L153 and L190 from L376 (U20404/U20405 2026-11-10): Sep 2026 12m **3.207**, Sep 2025 3.146 — identical to the agent's Fisher result. ✔
- NY Fed MCT chart-data file, 2026-09 row: 2.49 / **2.84** / 3.21, gap vs 2017–19 1.01; sector columns 0.54 / 0.45 / 0.04. Column headers in the file confirm: "Goods", "Services ex. housing", "Housing" under "decompositions#sector-aggregates". ✔ Also: MCT path 3.45 (Apr 2026) → 2.55 (Jul) → 2.56 (Aug) → 2.84 (Sep).
- SCE press release (Nov 9) text: "unchanged at the one-year, three-year, and five-year-ahead horizons at 3.9%, 3.3%, and 3.0%". ✔
- Board open-market table: 2026 "September 17 | 25 | 0 | 3.75-4.00"; 2025 Dec 11, Oct 30, Sep 18 cuts of 25 to 3.50–3.75. ✔ (effective dates)
- Michigan 5–10y Nov 2026 3.4 PRELIMINARY, Oct 3.5, pipeline note on the "next 5 years" label. ✔

**Corrected:**
- **Michigan 5–10y "above its 2021–23 peak" (Worth a look 3; slide-worthiness):** Agent D found, and I verified in UMich's own web-series note (`03_Data/Raw/S3A_D_michigan_mode_2026-11-15/umich_px5web202506.pdf`), that Michigan switched from phone to web interviewing in 2024 and that the web-only Jun 2025 median (4.0) "matches the peak reading from mid-2022". The 3.4 vs 3.2 comparison straddles a survey-mode break and must not be stated as a new high. The workbook carries the caveat.
- the agent's "summary.md 3.7 does not match" is not an error in summary.md: the 3.7 is Waller's own figure (summary notes Logan/Paulson/Jefferson give 3.6), already settled by slide 1 E7. Logged, not a new flag.

**Could not check:** gas correlations (not recomputed); SPF Q3 values (not recomputed); Cleveland median PCE values.

**Worth a look (coordinator):**
- MCT fell from 3.45 (Apr 2026) to 2.55 (Jul) and rebounded to 2.84 (Sep): the Sep reading is a rise of 0.28 in one month (Aug revised).
- The Logan measure's 12m is flat (3.15 → 3.21 over a year), but Oct est. 3m ann. jumps to 3.46 from 2.61. That is the "recent momentum has picked up" pattern, and it rests on the estimate.

**Interpretive notes:** expectations split cleanly by respondent type rather than by horizon: households are high at both horizons; markets and professionals are near target at long horizons. That weakens the "short-run expectations just track gas" defense (household long-run is also up) and also weakens "unanchoring" claims (markets anchored). D should press both directions.
