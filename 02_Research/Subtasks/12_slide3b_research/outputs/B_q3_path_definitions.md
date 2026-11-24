# Slide 3B oil paths: definitions (Agent B, 2026-11-15)

All prices are Brent spot FOB, $/bbl, not seasonally adjusted, quarterly averages. Script: `code/B_q3_build.py`. Data: `B_q3_oil_paths.csv`.
Tags: [O] = opened and read by me; [S] = search snippet only; [2] = secondary source.

## Common conventions
- **History (kind=actual):** EIA RBRTE daily spot, release 2026-11-12, last observation **2026-11-11 ($92.14)** [O]. FRED DCOILBRENTEU matches EIA on every date since 2024-01-01 (0 mismatches; FRED last updated 2026-11-12) [O]. Next EIA release is 2026-11-18, the data cutoff day, so a rerun on Nov 18 should add Nov 12–17.
- **Quarterly average** = the simple mean of trading-day observations. STEO quarterly numbers are means of monthly averages. The two conventions differ by ≤$0.65 in complete quarters (2026Q2: 102.63 vs 103.28).
- **2026Q3 is complete:** $96.30, 65 days. **2026Q4 is partial:** 30 days observed (Oct 1–Nov 11), mean $116.73.
- **2026Q4 splice (kind=splice):** Q4 = (sum of the 30 observed days + the rule or forecast price × the 34 remaining weekdays) / 64. The remaining weekdays are 12 in Nov and 22 in Dec. Nov 26 and Dec 25 are excluded as likely EIA gaps, which is an approximation. Weights: **observed 0.469, rule/forecast 0.531**. For Path 1 the remaining days use the STEO monthly forecast for their month (Nov $104, Dec $99).
- **Rules start on 2026-11-12**, the first day after the last observation, and run through 2027Q4.

## Path 1: baseline (central)
- **Rule:** the EIA **November 2026 STEO** Brent forecast (series BREPUUS, table 2tab). The model run was completed **2026-11-05** and the report released **2026-11-10** [O] (`steo_home.htm`: "Release Date: November 10, 2026 | Forecast Completed: November 5, 2026").
- **Quarterly path:** 2026Q4 $108.2 (splice; the STEO's own Q4 is $108.98), 2027Q1 $95, Q2 $89, Q3 $83, Q4 $77.
- **Futures check: not available from a free primary source.**
  - EIA's NYMEX futures series RCLC1–4 end on **2024-04-05**. The EIA page states "Futures prices after April 5, 2024, are not available" [O].
  - CME and ICE pages returned HTTP 403 (logged in `B_paywalled.csv`).
  - Search snippets [S] give the Brent front-month settlements as $92.57 on Nov 9 and about $92.7 on Nov 11. That is close to spot ($91.03 and $92.14). These snippets give no term structure, so they can't be used as a curve.
- **Market check found later in the run** (`code/B_q3_fetch_futures.py`, `B_q3_futures_curve.csv`). Source: NYMEX Brent Last-Day (BZ) contract closes on **2026-11-13**, via the Yahoo Finance chart API [2]. This is the same route Agent A used for Aug 11.
  - Front month (Jan-27 contract): $95.84. Nov 12 close $95.82, vs EIA spot $92.14 on Nov 11.
  - Quarterly mean of contract months: **2027Q1 $93.2, Q2 $87.5, Q3 $83.8, Q4 $80.8**. The Nov STEO has $95, $89, $83, $77, so the two agree within −$1.8 to +$3.8. The curve is flatter at the back.
  - Contract month is treated as delivery month (approximate).
  - Saved as variant **`P1_futures_2026-11-13` (alt)**: 2026Q4 splice uses the front contract for the remaining days, giving $105.6.
- **Brent–WTI spot spread:** $2.52 on Nov 11; the Nov 1–11 mean is $3.24 (EIA) [O].
- **Why the STEO as central:** it is the only dated, public, **primary** quarterly forecast through 2027Q4. The futures curve is available only through a secondary aggregator. It is the same family of source as the baseline-assumption proxy (Aug 2026 STEO), so the gap compares like with like.
- **Caveat:** it was completed Nov 5, before the Nov 9–11 lows. Its Nov–Dec forecasts ($104, $99) sit about $7–12 above recent spot (~$90–92).

## Path 2: "oil rises again"
- **Quote, Bowman, Nov 10 2026** [O] (`2026-11-10_Bowman_US_economy_monetary_policy.rtf`): "As tensions rose, Brent oil prices moved up to and above $110 per barrel in the second half of October before dropping sharply last week on optimism that an agreement between the U.S. and Iran could be reached following the midterm elections."
  - Check: EIA daily Brent over Oct 15–31 ran from $115.22 to $128.30, mean $121.39. That is consistent with "above $110" [O].
- **Central rule:** Brent at **$110 flat from 2026-11-12 through 2027Q4**. 2026Q4 splice = $113.2.
  - One-line justification: $110 is the threshold Bowman names. It is a round, quotable level, and a return to it reverses last week's drop without assuming a new peak.
- **Alternative rule:** Brent at the **Oct 2026 monthly average, $123.93, flat** from 2026-11-12. 2026Q4 = $120.6.
  - One-line justification: it is the realized level of the most recent month of the disruption, which the Nov STEO calls "the highest price since July 2022 when prices averaged $127/b adjusted for inflation" [O]. So it is a "back to where we just were" stress case rather than an invented peak.

## Path 3: "Hormuz reopens" (pre-war trend plus a residual premium)
**(a) Pre-war date.** The conflict began on **2026-02-28**.
- Source: EIA STEO March 2026, p. 5 [O]: "The Brent crude oil spot price rose from an average of $71 per barrel (b) on February 27 to $104/b on March 9 following the onset of military action in the Middle East that began on February 28." The March 2026 STEO adds that the Strait of Hormuz "was effectively closed to most shipping traffic" as of March 9.
- The Nov 2026 STEO [O] confirms it: "Since the U.S.-Iran conflict began on February 28…".
- In the Brent series, the last pre-war observation is **2026-02-27, $71.32**. The first observation after the onset is 2026-03-02, $77.24.
- **Pre-war window:** through 2026-02-27.

**(b) Pre-war trend: the last pre-war STEO vintage = Feb 2026 STEO** (completed 2026-02-05, released 2026-02-10, per the March STEO's "previous forecast: February 10, 2026") [O].
- Its quarterly Brent: 2026Q3 $55.3, Q4 $54.0, then **$53.0 in every quarter of 2027**.
- **Alternative trend:** the Jan 2–Feb 27 2026 spot average, **$68.69**, flat.

**(c) Premium:** **$25 central**, with $20 and $30 as alternatives, added to the trend from 2026-11-12.
- Central path: 2026Q4 $96.7 (splice), **2027Q1–Q4 $78.0**. The $20 alternative gives $73.0; the $30 alternative gives $83.0.
- Alternative trend + $25 = $93.7.
- Quote, **Waller, Nov 10 2026** [O] (`2026-11-10_Waller_economic_outlook.pdf`): "First, even as there is increased tanker traffic through the Strait of Hormuz, that traffic is moving at great expense. The insurance now needed for ships making this passing, and the ship-to-ship transfer of oil necessary to guard against Iranian attacks, are reportedly boosting oil prices by $20 to $30 a barrel."

**(d) Premise check (flag; the locked design is not changed).**
- Waller's $20–30 is the cost of passage **in the current state**: traffic is increasing, but it needs insurance and ship-to-ship transfers to guard against attacks. The figure is "reportedly", so even Waller presents it secondhand.
- A "residual premium after reopening" is therefore **an extrapolation, not the same thing**. A full reopening would remove at least part of the need for ship-to-ship transfers and war-risk insurance, so the measured premium is better read as an upper end for a post-reopening residual.
- Waller says it boosts "oil prices", not specifically Brent. Brent is a North Sea FOB benchmark. Gulf freight and insurance costs reach Brent only indirectly, through competition among delivered crudes. Bowman says freight and insurance are "raising the cost of delivered oil".
- **$0-premium variant** (`P3_feb26steo_plus0`): the pre-war trend itself, 2026Q4 $83.4 (splice) and then **$53 flat in 2027**, below the Aug-2026 STEO assumption (a gap of −20 to −33 log points).
- Second premise issue: the Feb-2026 STEO "trend" was already a forecast of falling prices. Its 2026Q3 value of $55 was about $14 below the Jan–Feb spot average ($68.7). "Pre-war trend" therefore means "the pre-war forecast", not "the pre-war price level". The Jan–Feb average variant covers the second reading.

## Gaps vs the baseline assumption (provisional)
- `A_q2_oil_assumption.csv` did not exist when this ran, so gaps are **provisional vs the Aug-2026 STEO**: completed 2026-08-06, quarterly mean of monthly BREPUUS (Q3 $85.26, Q4 $78.0, then 2027 $74, $71, $68, $65).
- Gaps are reported both as 100·ln(P/P_assumed) (log points) and as a simple % change.
- The Aug STEO's 2026Q3 already contains realized July ($83.77).
- The gap starts in 2026Q3, the first quarter where it is nonzero: 2026Q3 actual $96.30 vs $85.26 = **+12.2 log points**, driven by September. No gap is assumed before 2026Q3. The final gaps belong to the forecast script, using A's file.
- The FEDS note's own Fig. 3 projection used "the Brent futures curve (as of early August 2026)" [O]. That is the same timing as this proxy, but on futures, not the STEO.

Provisional gap, log points ×100:

| variant | 26Q3 | 26Q4 | 27Q1 | 27Q2 | 27Q3 | 27Q4 |
|---|---|---|---|---|---|---|
| P1 Nov STEO | 12.2 | 32.8 | 25.0 | 22.6 | 19.9 | 16.9 |
| P2 $110 | 12.2 | 37.2 | 39.6 | 43.8 | 48.1 | 52.6 |
| P2 alt Oct avg | 12.2 | 43.5 | 51.6 | 55.7 | 60.0 | 64.5 |
| P3 +$25 | 12.2 | 21.5 | 5.3 | 9.4 | 13.7 | 18.2 |
| P3 +$20 / +$30 | 12.2 | 18.7 / 24.2 | −1.4 / 11.5 | 2.8 / 15.6 | 7.1 / 19.9 | 11.6 / 24.4 |
| P3 +$0 | 12.2 | 6.7 | −33.4 | −29.2 | −24.9 | −20.4 |
| P3 alt Jan–Feb avg +$25 | 12.2 | 29.2 | 23.6 | 27.7 | 32.1 | 36.6 |

**Sensitivity to the assumption proxy** (`code/B_q3_gap_sensitivity.py`, `B_q3_gap_sensitivity.csv`). Agent A's file also holds a NYMEX BZ futures curve as of **2026-08-11**: 2027 quarters $81.5, $78.7, $77.0, $75.8. Measured against it, 2027 gaps are **8–15 log points smaller** than against the Aug STEO:
- P1 Nov STEO: 15.4 → 1.6 (vs 25.0 → 16.9).
- P2 $110: 30.0 → 37.3.
- **P3 +$25: −4.4 → +2.9** (vs +5.3 → +18.2). Path 3 is roughly neutral against futures but inflationary against the STEO.

Which proxy is final is A's or the forecast script's call. It matters for every scenario.
