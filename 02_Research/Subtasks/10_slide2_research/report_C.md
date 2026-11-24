Status: Audited — converged R3 (Codex, Nov 15, 2026)

# Agent C report: upstream and external evidence (Q8–Q11), Nov 15, 2026
Agent: Sonnet 5.5, brief `brief_C.md`. Outputs `outputs/C_*`, scripts `code/C_*.py`, `notes_C.md`, `sources_C.md`, `outputs/C_paywalled.csv`. Raw: `03_Data/Raw/BLS_PPI_stages_2026-11-15/`, `EIA_FRED_oil_daily_2026-11-15/`, `EIA_fuel_spot_2026-11-15/`, `BLS_CPI_PPI_q11_2026-11-15/`, `FedBoard_ISM_note_2026-11-15/`. BLS API v2 pulled Nov 15 (Oct PPI released Nov 13); Jul–Oct 2026 PPI preliminary.

## Findings

### Label error (flag first)
- WPSID61–64 are the **by commodity type** series, not stages: ID61 processed goods, **ID62 unprocessed goods**, ID63 services, ID64 construction (for intermediate demand). The **production-flow stages are WPSID51–54** (stage 1–4); sub-series WPSID511–513, 521–523 and WPSID59x1x. Titles: `C_q8_label_check.csv`.
- GO's "unprocessed intermediate (ID62)" is correct; reading ID62 as "stage 2" is wrong.
- The Nov 10 ID62 figure is stale: the Nov 13 release revised Jun–Sep. WPSID62 Sep 299.868 → 293.838 (−2.0%); Sep 3m ann. +41.5% → +31.0%; y/y +21.5% → +19.3% (`C_q8_vintage_revisions.csv`).

### Q8. PPI, Oct 2026, SA (m/m / 3m ann. / y/y)
| Series | m/m | 3m ann. | y/y |
|---|---|---|---|
| Stage 1 (WPSID51) | +0.55 | +18.9 | +14.1 |
| Stage 2 (WPSID52) | −0.21 | +16.4 | +13.2 |
| Stage 3 (WPSID53) | +0.34 | +10.0 | +8.4 |
| Stage 4 (WPSID54) | +0.45 | +8.8 | +8.0 |
| Final demand (WPSFD4) | +0.35 | +9.0 | +6.5 |
| ID62 unprocessed goods | −3.08 | +16.8 | +17.1 |
| ID61 processed goods | +0.36 | +19.6 | +14.5 |

- Sep (revised): stage 1 +2.23 m/m (3m 16.1); stage 2 +3.23 (16.0).
- m/m matches the BLS release text (stage 1 +0.6, stage 2 −0.2, stage 3 +0.3, stage 4 +0.4, FD +0.3, ID62 −3.1). NSA y/y matches the release: 13.9, 13.3, 8.4, 8.0, 6.5, 14.6, 16.9 (`C_q8_nsa_yoy_check.csv`).
- October reverses the ID62 spike (−3.1% after +6.2%; 3m 31.0 → 16.8). Stages mixed: stage 1 extends to a 2018–present record level (172.6); stage 2 slips 0.2% from its Sep peak (first decline since July; 3m still ticks up); stages 3–4 and FD at record levels.
- Ranks, 106 months 2018-01 to 2026-10: y/y stage 1 16th, stage 2 20th (last this high Jun 2022 / Sep 2022, matching BLS text). 3m ann. stage 1 17th (last ≥ Jun 2026), stage 2 26th (last ≥ May 2026).
- Energy within stages: energy goods inputs (ID59115, ID59215) Dec 2025 weights 7.4% (stage 1), 13.5% (stage 2). Energy ≈38% (stage 1) and 47% (stage 2) of the Aug–Oct 3m rise. In Oct, energy contributed −0.25 pp (stage 1) and −0.98 pp (stage 2) (`C_q8_energy_contributions_windows.csv`). Services inputs +0.9% (stage 1), +0.7% (stage 2) m/m; stage 2 goods inputs −1.4%. Stage 1 transport and warehousing for goods producers (ID51122) 3m ann. +39.9%.
- Oil (EIA RBRTE/RWTC daily; FRED mirror identical; last obs Nov 11): Brent peak $135.51 Oct 2; $120.15 Oct 30. Nov 2 −10.6%, Nov 4 −14.2% to $91.84. Oct 30 → Nov 4: Brent −23.6%, WTI −14.7%. Brent $92.14 Nov 11 (−32% from peak).
- Oct PPI predates the drop: BLS prices most items on the Tuesday of the week containing the 13th (Oct 13; Brent $125.78) — BLS Handbook of Methods.
- Outputs: `C_q8_ppi_stages.csv`, `C_q8_ppi_stages_summary.csv`, `C_q8_oil_daily.csv`, `C_q8_oil_drop_summary.csv` (+ revisions, contributions, label check, NSA check).

### Q9. ISM note (`C_q9_ism_note.md`)
- A Board-staff text-mining measure, not an ISM diffusion index: free-text "prices up/down" responses from ISM manufacturing and services surveys, mapped to ~50 PPI-like categories (sentence embeddings, and Claude Sonnet 4.5, preferred). Net mentions = increases − decreases, by sector, monthly, 2024–2026. High-tech variant = memory chips and processors (Fig. 3).
- Not public: no data-availability statement; the note thanks ISM "for access to" the data; ISM site login-gated (`C_paywalled.csv`). No latest reading; sample ends mid-2026.
- Waller goes beyond the note: he cites PPI and "inflation data" (note compares only PPI semiconductors/electronic components), "signal about future PCE inflation" (his inference), and an "October" reading not in the note.

### Q10. FEDS oil note (`C_q10_oil_note_verification.csv`, 43 rows; `C_q10_lit_summary_update.md`)
- Mostly confirmed (Table 2, RMSE horse race, Fig. 2–3 values, fn 4/5/6, Waller's quotes), each quote checked verbatim by script.
- Corrected: (1) the lit summary's "late-Oct spike above $110" — Brent was above $110 every close Sep 10–Oct 30 (Sep avg $114, Oct $124); the early-Aug futures curve ($86–97) is near current Brent. (2) Import prices (fn 3): nothing extra in the panel only; for the US the note cites Peneva et al. that import prices ex energy matter, and omits them from the baseline. (3) 0.14 pp is the post-pandemic total (10 × (0.001 + 0.013)); 0.013 is the increase.
- Country level: no country table; only fn 4 — persistence significant in all five; pass-through rose significantly in Canada, Japan, US; not significant in euro area, UK (attributed to the gas shock). No US coefficient reported.
- GEMUS: a supply reduction in a small oil-producing region calibrated to raise oil prices 10% (Fig. 4 normalises on a 10% oil-price increase; coordinator fix R1-F01); same inertial Taylor-type rule (fn 10) in all cases, not a rule comparison; higher pass-through via higher oil cost share in production (fn 11). "GDP hit about twice as large" has no stated comparator number; the only numeric anchor is "a little over 0.1%" in the base case.

### Q11. Confirming items (`C_q11_confirming_items.md/.csv`)
- **Airfares:** CPI airline fares SA Oct +0.4% m/m, 3m ann. +18.3%, index (Feb 2026 = 100) 115.8; no Oct y/y (no Oct 2025 CPI). PCE air transportation Sep +4.4% m/m, +20.5% y/y. PPI jet fuel Oct +7.0% m/m, +106.5% y/y. PPI airline passenger services Oct −1.2% SA, +4.3% NSA. For pass-through: CPI fares vs jet fuel monthly r ≈ 0.4 at lags 0–1. Against: fares rose 8% Dec–Feb, before the March oil spike; no retrace when jet fuel fell Jun–Jul; cumulative ratio ~0.16; demand evidence not pulled.
- **Freight:** PPI truck freight Oct +3.9% m/m, +24.6% y/y while SA diesel −7.9%; truck vs diesel r 0.55–0.66 at lags 0–1. Downstream, CPI food away from home +0.5% m/m Oct, +2.3% since Feb; truck→food lag correlation peaks at 6 months (0.33, thin).

## Slide-worthiness (agent)
- Upstream panel 4/5: record-level stage 1, energy turning negative in Oct while services inputs and transport still rise; usable for both readings. Caveats: ID62 revision, label correction.
- ISM index 1/5 as data: not public or reproducible; cite as Fed staff note / Waller reference only.
- Confirming items: airfares 3/5 (price moves, weak fuel linkage); freight 3/5 (co-movement consistent with delayed fuel pass-through, but demand, other costs and seasonality not separated; truck freight WPU3012 is NSA, diesel SA; consumer-price pass-through not established — coordinator fix R1-F03).

## Worth a look (agent)
1. ID61–64 label error; Sep ID62 revised −2.0% (Nov 10 "+41.5%" stale).
2. Brent +18% in one day Oct 2 (WTI −1.9%); Brent–WTI spread averaged $21.9 in Oct (max $37.6) vs $3.6 in 2025 and $3.2 Nov 1–11. Cause not investigated.
3. PPI airline services NSA +4.3% vs SA −1.2% in Oct. The pipeline's "WPU3022 −1.24" is actually SA series WPS3022 (label/ID mismatch in `named_series_2026-10.csv`).
4. No Oct 2025 CPI, so no CPI Oct y/y.
5. Stage 2 energy goods inputs −5.7% in Oct after +15.9% in Sep, before the Nov oil drop.

## Spot-checks (agent)
1. `C_q8_ppi_stages.csv` WPSID51 2026-10: 172.613, mm 0.55.
2. WPSID62 2026-09: 293.838 vs old vintage 299.868 in `PPI/raw/bls_api_ppi_baskets_2017_2026_batch1_2026-11-10.json`.
3. `C_q8_oil_daily.csv` 2026-11-04 Brent 91.84.
4. `C_q10_oil_note_verification.csv` fn 4 row.
5. `C_q11_series.csv` WPS3022 2026-10 −1.24%.

## What to verify (agent)
Whether a public ISM text series exists; airline fuel cost share and demand; Eli's acceptance of WPSID51/52 as stages 1–2 (affects roadmap, STATE.md, any ID62-as-stage text); Feb revisions to Jul–Oct PPI; cause of the Oct 2 Brent jump.

## Coordinator review
**Verified:**
- Labels: BLS catalogue `03_Data/Raw/bls_wp_series_2026-11-11.txt` gives WPSID51–54 = "Intermediate demand by production flow-Stage 1…4" and WPSID61–64 = "by commodity type-Processed / Unprocessed goods / Services / Construction". Label correction confirmed.
- Recomputed from the raw BLS JSON (`BLS_PPI_stages_2026-11-15/batch*.json`): WPSID51 Oct 172.613, +0.55 m/m, 3m 18.9, y/y 14.1; WPSID52 154.077, −0.21, 16.4, 13.2; WPSID62 284.779, −3.08, 16.8, 17.1. All match.
- Oil: Brent max since Sep 1 = $135.51 on Oct 2; Nov 4 $91.84 (−14.19% d/d); EIA and FRED columns identical; minimum close Sep 10–Oct 30 $113.96 (so "above $110 every close" holds).
- FEDS note text (saved HTML): fn 4 reads "it rose significantly in Canada, Japan, and the U.S., but was weaker and not statistically significant in the euro area and the U.K., possibly reflecting Europe's natural gas price shock…"; GEMUS: "the GDP hit is about twice as large". Confirmed.
**Corrected:** nothing in the agent's numbers. Note on the "$110" correction: it targets our lit summary's phrase "late-Oct spike above $110". Bowman's own words ("at or above $110 in late October") remain literally true; only "spike" is wrong (prices were above $110 from Sep 10).
**Could not check:** ISM public availability beyond the note; Brent–WTI spread cause.
**Worth a look (coordinator):** The roadmap's upstream panel ("PPI stages 1–2") and the Nov 10 ID62 flag used different series families. If the slide shows "stages", the series are WPSID51/52; ID62 (unprocessed goods) is a separate, more energy-heavy line. Logged for Eli.
**Interpretive notes:** the Oct PPI is the cleanest "first round still lengthening, energy component turning" exhibit; Bowman vs Waller cannot be settled until Nov PPI (Dec), after the oil drop.

## Q11 follow-up (GO revision of Nov 15, 16:25): diesel → food, transportation services, car insurance
Agent C, resumed. Files: `outputs/C_q11b_followup.md`, `C_q11b_food_diesel_series.csv`, `C_q11b_food_diesel_lags.csv`, `C_q11b_transport_services_decomp.csv`, `C_q11b_motor_insurance.csv`; scripts `code/C_q11b_fetch.py`, `code/C_q11b_build.py`; raw `03_Data/Raw/CPI_q11b_2026-11-15b/`. BLS published no Oct 2025 CPI, so no Oct 2026 y/y; Oct–Dec 2025 insurance m/m missing.

**1. Diesel and food (CPI SA).** Food at home Oct +0.44% m/m (largest since April), 3m ann. +1.65%; Sep −0.07%, y/y +1.8%; +1.1% above Feb 2026. Food away from home Oct +0.52%, 3m ann. +4.08%; Sep y/y +3.5% vs 2018–19 avg 2.9%; +2.3% above Feb. EIA retail diesel Oct −0.6% m/m, +68% vs Feb ($3.72 → $6.25), y/y +69.9%; PPI diesel SA −7.9% m/m, +95% vs Feb; PPI truck freight +3.9% m/m (y/y +24.6%), +22% vs Feb. Lag correlations (monthly % changes): retail diesel → food at home ≤0.22 (2018+), 0.30 at lags 1–2 (2022+); diesel → food away ~0 at lags 0–2, 0.31 at lag 7; PPI diesel → food ≤0.17 / 0.23; truck freight → food at home 0.29–0.33 at lags 2–8 (2018+), 0.31–0.49 (2022+, peak lag 8); truck → food away 0.38 lag 7 (2018+), 0.44 (2022+). Peaks at long lags; shock only 7 months old; sample dominated by 2021–22.

**2. Transportation services Oct +0.8% SA** (BLS Table 2 relative importance Sep 2026; components sum to +0.80 pp of the parent's m/m):

| Component | RI % of CPI | Oct m/m | Contribution (pp) |
|---|---|---|---|
| Intracity transportation (NSA; includes mass transit and vehicles for hire, e.g. taxis/rideshares) | 0.366 | +6.6 | +0.39 |
| Motor vehicle insurance | 2.510 | +0.7 | +0.28 |
| Maintenance and repair | 1.065 | +0.6 | +0.10 |
| Airline fares | 1.055 | +0.4 | +0.07 |
| Motor vehicle fees | 0.495 | +0.7 | +0.06 |
| Other intercity | 0.225 | +1.4 | +0.05 |
| Leased cars | 0.382 | 0.0 | 0.00 |
| Car and truck rental | 0.153 | −5.7 | −0.14 |

Intracity transportation + insurance = 0.67 of 0.80. Intracity transportation is NSA (footnote 1) and covers mass transit and vehicles for hire; the small-sample footnote 3 applies to the separate "intracity mass transit" row, whose Oct entry is missing, so the mass-transit/vehicle-for-hire split is unverified. Contributions use rounded published changes (coordinator fix R1-F02). Energy link by the data: airfares (jet fuel direct input) only +0.07 pp; transit fares untested; repair and insurance no direct energy link in BLS definitions.

**3. Motor vehicle insurance (CPI SA).** 2026 m/m: Jan −0.44, Feb −0.33, Mar −0.04, Apr +0.14, May −1.69, Jun −2.01, Jul −0.29, Aug −0.75, Sep +0.06, Oct +0.71. Oct 3m ann. ~+0.1% (Jul −14.9%). y/y Sep −4.98% (peak +22.6% Apr 2024; +3.2% Sep 2025). Oct +0.71 ranks 42nd of 103 months; SA Octobers range −2.17% (2020) to +1.97% (2023). BLS factsheet [O]: model years updated "usually in October or November", which "often results in premium changes"; no energy link. PCE net motor vehicle insurance (U20404 line 279) Sep +0.3% y/y (Jan +3.4%) vs CPI −5.0% (Jan +0.6%): gap −0.6 pp (Mar) → −5.3 pp (Sep). BEA FAQ 83 [O]: insurance excluded from market-based PCE; "premiums minus normal losses" definition [S, unverified].

**Worth a look (agent):** intracity transportation (incl. taxis/rideshares) supplies about half of the 0.8; insurance's Oct rise falls in the model-year update window (Nov will tell); food at home +0.44 with diesel flat and trucking +3.9% (one month); PCE insurance +0.3% vs CPI −5.0% while repair costs +5.8% y/y.

### Coordinator review (follow-up)
**Verified:** BLS `cpi.t02` saved text (`03_Data/Raw/CPI_q11b_2026-11-15b/bls_cpi_news_release_t02_2026-11-15.htm`): "Motor vehicle insurance 2.510 … 0.7", "Intracity transportation 0.366 … 6.6", "Transportation services 6.256 … 0.8". Components' contributions in the CSV sum to 0.80. Contribution arithmetic (2.510 × 0.7 / 6.256 = 0.28) checks.
**Could not check:** food lag correlations (not recomputed); PCE line 279 definition.
**Interpretive note:** none of the three items gives clean evidence of energy pass-through into core services in October; the 0.8 is mostly intracity transportation and insurance.
