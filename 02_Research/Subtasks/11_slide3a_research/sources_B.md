# Sources, Agent B (Q3 wages/costs, Q5 catch-up). Tags: [O] opened, [S] search snippet only, [2] secondary/summary tool.
| Source | URL / file | Tag | Note |
|---|---|---|---|
| ECI (CIS/CIU 2010, 2020) | pipeline `03_Data/pipelines/inflation_data/processed/bls/observations.csv` (raw `raw/bls/bls_api_all_series_2020-2026_2026-11-10.json`) | [O] | BLS API pull 2026-11-10; 2026Q3 ECI released Oct 30 (per Subtask 01 report) |
| Productivity & Costs PRS85006xxx incl. 054/064/174 | `03_Data/Raw/S3A_B_labor_costs_2026-11-15/bls_api_productivity_costs_2008-2026_2026-11-15.json` | [O] | BLS API v2 pull 2026-11-15; Q3 prelim released Nov 5; all 315 overlapping obs match pipeline 11-10 pull (B_crosscheck.py) |
| FRED OPHNFB, PRS85006173 full, PRS84006173, COE, NICUR, GDI, GDP, A576RC1 | `.../fred_*_2026-11-15.json` | [O] | FRED API; OPHNFB = PRS85006093 |
| ALFRED vintages PRS85006173 | `.../alfred_PRS85006173_vintages_2026-11-15.json` | [O] | vintage dates 2026-05-07 to 11-05 |
| CES AHE CES0500000003/08/02 | `.../bls_api_ces_ahe_2016-2026_2026-11-15.json` | [O] | Oct 2026 prelim (footnote P); Sep revised 37.86 |
| BLS Employment Situation Oct 2026 | https://www.bls.gov/news.release/empsit.nr0.htm | [2] | WebFetch summary: released Fri Nov 6 2026 8:30 ET; AHE +14c (0.4%) to $38.00, 3.1% y/y; prod & nonsup $32.75 (+12c). curl 403 |
| Atlanta Fed Wage Growth Tracker | https://www.atlantafed.org/research-and-data/data/wage-growth-tracker ; file `.../wage-growth-data.xlsx` saved as `atlantafed_wage-growth-data_2026-11-15.xlsx` (+ page html) | [O] | page "Updated: October 08, 2026"; data through Sep 2026; Oct not yet |
| NFIB SBET Oct 2026 | https://www.nfib.com/wp-content/uploads/2026/11/SBET-Report-October-2026.pdf (saved) | [O] | pypdf; tables p.16-17 (PDF pp.18-19), prices p.14; commentary pp.3 |
| NFIB SBET Sep 2026 | https://www.nfib.com/wp-content/uploads/2026/10/NFIB-SBET-Report-September-2026.pdf (saved) | [O] saved, not parsed | |
| NFIB SBET Dec 2020 | https://web.archive.org/web/2021/https://assets.nfib.com/nfibcom/SBET-Dec-2020.pdf (saved) | [O] | 2018-2020 history; seasonal factors as of Dec 2020, not re-estimated |
| Atlanta Fed BIE | `pipeline raw/expectations_aggregate/atlantafed_bie-data_2026-11-14.xlsx` | [O] | latest column date 2026-10-17 (Oct 2026 survey); labor-cost question ended Nov 2023 |
| Richmond Fed mfg / services historical | pipeline `richmondfed_mfg_historicaldata_2026-11-14.xlsx`, `richmondfed_nmf_...` | [O] | SA wage diffusion indexes to Oct 2026 |
| Richmond Fed CFO Survey Q3 2026 | pipeline `richmondfed_cfo_survey_2026Q3_results_2026-11-14.html` | [O] | fielded Aug 17-Sep 4 2026 |
| Conference Board CCI Oct 2026 | pipeline `conferenceboard_CCI_Oct2026_press_2026-11-14.html` | [O] | 12-month inflation expectation 5.8% |
| Conference Board Salary Budget 2026-27 | https://www.conference-board.org/publications/us-salary-increase-budgets-2026-2027 | [2] | WebFetch: 3.5% median for 2027, merit 3.1%, release Sep 3 2026; members-only |
| Beige Book Oct 2026 | https://www.federalreserve.gov/monetarypolicy/beigebook202610-summary.htm (saved) | [O] | Last Update Oct 14 2026; info through Oct 5 |
| Barr speech Nov 12 2026 | `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-12_Barr_inequality_AI.html` | [O] | 52.8% sentence and fn 15; no source named for the number |
| Jefferson speech Nov 13 2026 | same folder `2026-11-13_Jefferson_productivity_puzzles.html` | [O] | 2.2% (2020-25) vs 1.5% previous cycle |
| CBO potential labor force productivity 1.5% | cbo.gov slides/Outlook | [S] | UNVERIFIED; fetch blocked |
