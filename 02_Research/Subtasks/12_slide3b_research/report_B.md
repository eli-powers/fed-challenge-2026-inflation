Status: Audited — converged R2 (Codex, Nov 15)

# Agent B report: oil paths and pass-through mapping (Opus 5.5, 2026-11-15)

## Findings
### Q3 Oil paths (Brent spot FOB, $/bbl, NSA, quarterly mean of trading days)
- Daily: last EIA RBRTE 2026-11-11 $92.14 (EIA release Nov 12; next Nov 18 = cutoff). FRED DCOILBRENTEU matches EIA on all dates since 2024. 2026Q3 complete $96.30 (65 days); 2026Q4 partial (Oct 1–Nov 11, 30 days) mean $116.73.
- **P1 central, EIA Nov-2026 STEO** (completed Nov 5, released Nov 10) [O]: 2026Q4 $108.2 (splice: observed w=0.469 + remaining weekdays w=0.531 at STEO Nov $104, Dec $99); 2027Q1–Q4 $95, $89, $83, $77. Market check (alt): NYMEX BZ closes Nov 13 via Yahoo [2]: front $95.84; 2027Q1–Q4 $93.2, $87.5, $83.8, $80.8. EIA RCLC1–4 end 2024-04-05; CME/ICE 403; Bloomberg paywalled. Brent–WTI $2.52 (Nov 11).
- **P2 central, $110 flat from Nov 12** (2026Q4 $113.2; 2027 $110). Alt: Oct-2026 avg $123.93 flat (2026Q4 $120.6). Bowman [O]: "As tensions rose, Brent oil prices moved up to and above $110 per barrel in the second half of October before dropping sharply last week…"
- **P3 central, Hormuz reopens:** onset 2026-02-28 (EIA Mar-2026 STEO p.5 [O]: "military action in the Middle East that began on February 28"); last pre-war Brent Feb 27 $71.32. Pre-war trend = Feb-2026 STEO (completed Feb 5) → $53/qtr in 2027. Central = +$25 → 2026Q4 $96.7, 2027 $78 flat. Alts: +$20, +$30, +$0 ($53), Jan–Feb spot avg $68.69 + $25. Waller [O]: "…reportedly boosting oil prices by $20 to $30 a barrel."
- **Premise check:** Waller's $20–30 is the cost of *current* passage (insurance, ship-to-ship transfers) as traffic rises, reported secondhand; "residual premium after reopening" is an extrapolation, so $20–30 reads as an upper end. He does not say it is in Brent (North Sea FOB). $0 variant provided; locked design unchanged.
- **Gaps, provisional vs Aug-2026 STEO** (85.26, 78, 74, 71, 68, 65): start 2026Q3 at +12.2 log pts (September). 2027Q4: P1 +16.9, P2 +52.6, P3 +18.2, P3 $0 −20.4.

### Q4 Pass-through mapping
- Equation (MathJax): π_t = α_i + (γ1+η1·D)π_{t−1} + (γ2+η2·D)π_{t−2} + λx_t + βs_t + Σ_{j=0..4}(δ_j+ζ_j·D)o_{t−j} + ε_t; o = quarterly Brent inflation in local currency relative to core; D from 2021Q1. Units (annualized?) not stated (unverified); level mapping unaffected. Individual lags not reported.
- **Fig. 2 data table (accessible version), k=0–12, provenance = table.** k=4: 0.032 / 0.057 / 0.185; k=8: 0.041 / 0.080 / 0.318; k=12: 0.044 / 0.088 / 0.360 (pre / persistence only / post; % core level per permanent 10% oil rise; five-economy average).
- Mapping: L_t = Σ_s R_{t−s}·Δg_s/10; q/q ann. adj. a_t ≈ 4ΔL (exact compounding ≤0.008 pp); Q4/Q4 2027 adj = L_27Q4 − L_26Q4. 2027Q4 = k=5 from 2026Q3 start, no extrapolation. Superposition matches direct simulation within 0.0001 pp; relative-to-core feedback ≤0.004 pp, embedded in table. If "10%" = 9.53 log pts, scale ×1.049 (unverified). `map_gap_to_core` in `code/B_common.py`.
- **Worked 2027 Q4/Q4 adj. (pp), pre / persistence only / post:** P1 −0.00 / +0.07 / +0.51; P2 +0.08 / +0.18 / +0.74; P3 +0.02 / +0.05 / +0.31. 2026 Q4/Q4 adj. 0.03–0.08.
- Optional headline mapping: not done.

## Slide-worthiness
- Oil-path chart 4/5: dated, sourced paths plus the assumption line; P3 central converges to P1 by 2027Q4.
- Response-function chart 4/5: note's own data; pre/post 0.04 vs 0.36; k=1 dip / k=4 jump need a line.

## Worth a look
1. Fig. 2 pre and persistence-only lines can't be reproduced from Table 2's pass-through sum 0.001 (−66 to −69% at k=12 under every lag split); need ≈0.0025 / 0.0032 (inside the pre CI). Post line reproduces within +1.5 to +5%. Possibly separately estimated restricted specs (unverified). Q&A trap.
2. Text rounds the figure: 0.044 / 0.088 / 0.360 vs "0.05" / "just under 0.1" / "0.35".
3. Post response is lumpy (k=1 dip, k=4 jump): quarterly annualized adjustments uneven (P1 post 2027Q4 +0.85 pp ann.); Q4/Q4 more robust.
4. Assumption proxy moves 2027 gaps 8–15 log pts (vs Aug-11 futures, P3 central → −4 to +3) (`B_q3_gap_sensitivity.csv`).
5. Even "Hormuz + $25" is above the Aug-STEO assumption; only the $0 variant is disinflationary.
6. Pre-war "trend" (Feb STEO $53–55) was a forecast of falling prices, ~$14 below Jan–Feb spot.
7. Nov STEO stale at front (Nov–Dec $104/$99 vs spot ~$92, front future $95.8).
8. The note's Fig. 3 also used Brent futures "as of early August 2026" — same timing as our proxy.

## Spot-check examples
1. `03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/DeMichelis_oil_core_accessible_20261109.htm`, Fig. 2 table k=12. 2. `03_Data/Raw/EIA_STEO_Nov2026_2026-11-15/nov26_base.xlsx` 2tab BREPUUS Oct–Dec 2027 = 79/77/75. 3. `03_Data/Raw/EIA_STEO_Mar2026_report_2026-11-15/mar26.pdf` p.5. 4. `03_Data/Raw/EIA_Brent_daily_2026-11-15/EIA_RBRTEd.xls` last row 92.14. 5. `outputs/B_q4_worked_example.csv` P2_110_flat / post / Q4/Q4 2027 = 0.7418.

## What to verify
Quotes; whether Fig. 2 pre/persistence-only come from restricted specs; 10% vs 10 log pts; Yahoo futures [2]; 2026Q4 remaining-day count (Nov 26, Dec 25 dropped). Rerun B_q3 scripts after EIA's Nov 18 release (rename raw folder first; scripts never overwrite).

Files: `notes_B.md`, `sources_B.md`, `outputs/B_*`, `code/B_*`. Raw: `03_Data/Raw/{EIA_Brent_daily, EIA_NYMEX_futures, Yahoo_BZ_futures_current, EIA_STEO_Nov2026, EIA_STEO_Aug2026, EIA_STEO_prewar_Jan-Feb2026, EIA_STEO_Mar2026_report, FEDS_oil_note_accessible}_2026-11-15/`.

## Coordinator review
**Verified (independent scripts):**
- Fig. 2 accessible-version table k=0–12, all three lines — read directly from the saved HTML; matches B_q4_response.csv k=12.
- Nov STEO 2027 quarterly Brent 95 / 89 / 83 / 77; Nov $104, Dec $99 — match.
- Mar STEO p.5 onset sentence ("military action in the Middle East that began on February 28") — match.
- Bowman and Waller quotes — checked against saved RTF/PDF earlier this session — match.
- Own convolution (L_t = Σ R_{t−s}Δg_s/10, log gaps ×100 vs Aug STEO) → 2027 Q4/Q4 adj pre/post: P1 −0.001/+0.513; P2 +0.080/+0.742; P3 +0.017/+0.313; 2026 Q4/Q4 adj 0.03–0.08 — match B.
**Corrections:** none.
**Not checked:** Yahoo futures [2]; B's reconstruction tests (Worth a look #1) — logged as a flag, not load-bearing (we use the table).
**Coordinator notes for C (binding on design):**
- Use Fig. 2 table responses (provenance = table); regimes on the grid = "pre-pandemic" and "post-pandemic (stronger persistence and pass-through)". Persistence-only = backup row only.
- Central paths: P1 Nov STEO, P2 $110 flat, P3 Feb-STEO + $25. Alts are sensitivity.
- Lead with Q4/Q4; quarterly annualized adjustments are lumpy (Fig. 2 shape).
**Worth a look (coordinator):** the oil axis matters mainly in the post regime: under pre-pandemic dynamics every central path adds ≤0.08 pp to 2027 Q4/Q4.
