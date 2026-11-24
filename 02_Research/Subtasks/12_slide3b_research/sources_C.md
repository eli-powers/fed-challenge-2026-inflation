# Sources, Agent C (slide 3B pipeline and scenarios), 2026-11-15

Tags: [O] = opened or parsed locally; [2] = secondary source; "copy" = a coordinator-verified file from Agent A or B.

## New raw pull (pipeline folder, never edited)
`03_Data/pipelines/forecast_3b/raw/2026-11-15/`. `manifest.json` gives the URL, bytes and sha256 for each file.

| File | URL | Vintage | Tag |
|---|---|---|---|
| medianLevel.xlsx, Dispersion_1.xlsx, spf-release-dates.txt | philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/{historical-data/medianLevel.xlsx, historical-data/Dispersion_1.xlsx, spf-release-dates.txt} | Latest survey 2026Q3: deadline 8/11/26, release 8/14/26. Byte-identical to `03_Data/Raw/PhilFed_SPF_2026Q3_2026-11-15/` | [O] |
| page_steo_outlook.html | https://www.eia.gov/outlooks/steo/outlook.php | Archive list: nov26 released 11/10/2026, aug26 08/11/2026, jul26 07/07/2026, may26 05/12/2026, apr26 04/07/2026, feb26 02/10/2026 | [O] |
| {nov26, aug26, jul26, may26, apr26, feb26}_base.xlsx | https://www.eia.gov/outlooks/steo/archives/<v>_base.xlsx (sheet 2tab, BREPUUS) | aug26 completed 2026-08-06; nov26 completed 2026-11-05; feb26 completed 2026-02-05. aug26, feb26 and nov26 are identical to A's and B's raw copies | [O] |
| EIA_RBRTEd.xls | https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls | Last observation 2026-11-11, $92.14. Identical to `03_Data/Raw/EIA_Brent_daily_2026-11-15/` | [O] |
| PCEPILFE_observations.json | api.stlouisfed.org/fred/series/observations (key not stored) | Realtime 2026-10-29 (BEA Sep 2026 PCE). Values identical to `03_Data/Raw/FRED_PCEPILFE_latest_2026-11-15/` | [O] |

## Config copies (`03_Data/pipelines/forecast_3b/config/`; checksums in `PROVENANCE.md`)
- `regime_response.csv`: copy of `outputs/B_q4_response.csv`, provenance = table. It is the Fig. 2 data table of De Michelis et al., FEDS Note, 2026-11-09, accessible version (`03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/`). The coordinator verified it against the HTML. [copy]
- `futures_curve_2026-11-13.csv`: copy of `outputs/B_q3_futures_curve.csv` (Yahoo NYMEX BZ closes). [2]
- `assumption_futures_2026Q3.csv`: copy of A's futures rows for Aug 11 (2027Q1–Q4). [2]
- `oil_path_rules.json`: path rules from `B_q3_path_definitions.md` and `B_q3_build.py`. The Bowman and Waller quote fragments are B's quotes, which the coordinator checked against the saved speeches. I did not re-open the speeches. [copy]

## Other project files read (not edited)
- `01_Finals/data/Slide1_Inflation_Data.xlsx`:
  - Headline!C10 is a formula (`=TS_PCE_rates!H111`) with no cached value;
  - raw_Oct_build!B7 = 0.29507 (core Oct m/m est.), the number used;
  - TS_PCE_rates!B111 = Sep index × (1 + B7/100). [O]
- `02_Research/External_views/Previous_Finalists_copy/2025 Finals - 1 Presentations.md`: the Pace section only, for its point on labelling forecast-path provenance and extensions. [O]
- `outputs/A_*`, `outputs/B_*`, `code/A_common.py`, `code/B_common.py`, `code/B_q3_build.py`, and report_A/B including the coordinator reviews. [O]

## Not accessed
- The Q4 2026 SPF: not released at run time (A: page 404 at about 17:40 ET).
- CME/ICE futures: blocked (A_paywalled.csv, B_paywalled.csv).
