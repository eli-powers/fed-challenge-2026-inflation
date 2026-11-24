# Sources: Agent B (slide 3B oil paths and pass-through), 2026-11-15

Tags: [O] = opened and parsed locally; [S] = search snippet only; [2] = secondary source.

## Raw files saved (new folders; never edited)

| Folder (03_Data/Raw/) | Files | Source URL | Vintage / release |
|---|---|---|---|
| EIA_Brent_daily_2026-11-15 | EIA_RBRTEd.xls, EIA_RWTCd.xls | https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls (and RWTCd) | EIA release 2026-11-12, last obs 2026-11-11, next release 2026-11-18 [O] |
| same | FRED_DCOILBRENTEU/DCOILWTICO _obs/_seriesinfo.json | api.stlouisfed.org (key redacted) | FRED last updated 2026-11-12, obs to 2026-11-11 [O] |
| EIA_NYMEX_futures_2026-11-15 | EIA_RCLC1–4d.xls, pet_pri_fut_s1_d.htm | https://www.eia.gov/dnav/pet/hist_xls/RCLC1d.xls … | **discontinued: last obs 2024-04-05** [O] |
| Yahoo_BZ_futures_current_2026-11-15 | BZ_F.json, BZ{F..Z}27.NYM.json, BZ{F,G,H}28.NYM.json | https://query1.finance.yahoo.com/v8/finance/chart/<ticker> | daily closes to 2026-11-13 [2]; BZZ26 returned 404 |
| EIA_STEO_Nov2026_2026-11-15 | nov26_base.xlsx (identical to STEO_m_current.xlsx), nov26.pdf, steo_home.htm, steo_report_global_oil.htm | https://www.eia.gov/outlooks/steo/archives/nov26_base.xlsx; /archives/nov26.pdf | released 2026-11-10, modeling completed 2026-11-05 [O] |
| EIA_STEO_Aug2026_2026-11-15 | aug26_base.xlsx | /archives/aug26_base.xlsx | completed 2026-08-06 [O]; released 2026-08-11 per Agent A's file [2 from A] |
| EIA_STEO_prewar_Jan-Feb2026_2026-11-15 | feb26_base.xlsx, jan26_base.xlsx, **mar26_base.xlsx** | /archives/{feb,jan,mar}26_base.xlsx | Feb: completed 2026-02-05, released 2026-02-10 (per Mar STEO text) [O]. Jan: completed 2026-01-08. **Mar (completed 2026-03-09) is post-onset despite the folder name;** used only for comparison |
| EIA_STEO_Mar2026_report_2026-11-15 | mar26.pdf | /archives/mar26.pdf | conflict onset date (Feb 28) quoted from p. 5 [O] |
| FEDS_oil_note_accessible_2026-11-15 | DeMichelis_oil_core_accessible_20261109.htm | https://www.federalreserve.gov/econres/notes/feds-notes/the-effect-of-oil-prices-on-core-inflation-recent-evidence-from-the-advanced-economies-accessible-20261109.htm | Fig. 1–4 data tables; last update 2026-11-09 [O] |

## Existing project files read (not edited)
- `02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html`: equation (MathJax), Table 2, text, footnotes [O].
- `.../speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` [O] and `.../2026-11-10_Waller_economic_outlook.pdf` [O]: exact quotes in `outputs/B_q3_path_definitions.md`.
- `10_slide2_research/outputs/C_q8_oil_daily.csv` (slide 2 Brent, to Nov 11): matches this pull.
- `12_slide3b_research/outputs/A_q2_oil_assumption.csv` (Agent A; read only): the Aug STEO path matches mine exactly; A's Aug-11 futures curve is used in the sensitivity check.

## Search snippets [S] (not used for numbers in outputs)
- Brent front-month settlement $92.57 on 2026-11-09: nationthailand.com, "Brent losses top US$7 a barrel after November 9 settlement" (https://www.nationthailand.com/news/world/40073309).
- About $92.7 on 2026-11-11: tradingeconomics.com, "Brent Settles Above $92 Amid US-Iran Tensions" (https://tradingeconomics.com/commodity/brent-crude-oil/news/600509).

## Blocked or paywalled
See `outputs/B_paywalled.csv` (CME, ICE, Bloomberg, EIA futures discontinued).
