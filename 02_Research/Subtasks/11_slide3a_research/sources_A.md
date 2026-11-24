# Sources: Agent A (Q1, Q2, Q7), Nov 15, 2026

Tags: [O] opened and read, [S] saved or seen but not read for the claim, [2] secondary, "unverified" = could not open.

| # | Source | URL / local file | Tag | Note |
|---|---|---|---|---|
| 1 | Bernanke & Blanchard (2023), "What Caused the US Pandemic-Era Inflation?", NBER WP 31417, June 2023 | `02_Research/External_views/Literature/2023_Bernanke_Blanchard_pandemic_inflation_NBER_w31417.pdf`; http://www.nber.org/papers/w31417 | [O] | Full text extracted with pypdf (50 pp.). Figures are images, so bar values are not in the text. |
| 2 | NBER w31417 landing page | https://www.nber.org/papers/w31417 → `03_Data/Raw/S3A_A_reis_2026-11-15/nber_w31417_page.html` | [S] | Saved. It did not show published-version details, so the published AEJ version was not checked. |
| 3 | Reis (2021), "Losing the Inflation Anchor," BPEA Fall 2021, 307–361 (Brookings summary page) | https://www.brookings.edu/articles/losing-the-inflation-anchor/ → `03_Data/Raw/S3A_A_reis_2026-11-15/brookings_reis_losing_inflation_anchor.html` | [O] (summary page); full PDF not opened | Confirms title, year and venue. **BB w31417 does not cite Reis.** |
| 4 | FRED JTSJOL, UNEMPLOY, UNRATE (observations + series info, API, retrieved 2026-11-15) | `03_Data/Raw/S3A_A_vu_2026-11-15/FRED_*_2026-11-15.json` | [O] | JTSJOL last updated 2026-11-03 (Sep 2026, preliminary). UNEMPLOY and UNRATE last updated 2026-11-06 (Oct 2026). |
| 5 | BLS API v2: JTS000000000000000JOL, LNS13000000, LNS14000000, 2018–2026 | `03_Data/Raw/S3A_A_vu_2026-11-15/BLS_API_JOL_LNS13000000_LNS14000000_2018_2026_2026-11-15.json` | [O] | Cross-check: 0 mismatches with FRED. |
| 6 | Logan, speech, Nov 10, 2026 | `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html` (og:url https://www.dallasfed.org/news/speeches/logan/2026/lkl261110) | [O] | Paragraph 162. Links to sources 7 and 8. |
| 7 | Atkinson, Dolmas, Zarutskie, Dallas Fed Economics, Apr 16, 2026 (+ chart data xlsx) | https://www.dallasfed.org/research/economics/2026/0416 → `03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/` | [O] | Skewness and trimmed-mean bias. |
| 8 | Atkinson, Dolmas, Zarutskie, Dallas Fed Economics, Aug 13, 2026 (+ chart data xlsx) | https://www.dallasfed.org/research/economics/2026/0813 → same folder | [O] | 19/20 alternative trim. |
| 9 | Rich, Verbrugge, Zaman, Cleveland Fed EC 2022-05 | https://www.clevelandfed.org/publications/economic-commentary/2022/ec-202205-adjusting-median-and-trimmed-mean-inflation-rates-for-bias-based-on-skewness → same folder | [O] | Skew-based bias adjustment. |
| 10 | Dolmas (2005), Dallas Fed WP 0506 | https://www.dallasfed.org/-/media/documents/research/papers/2005/wp0506.pdf → same folder | [O] | Method; left skew in 1977–2004. |
| 11 | Dallas Fed Trimmed Mean PCE page | https://www.dallasfed.org/research/pce → same folder | [O] | Sep 2026 TM 2.3, headline 3.6, core 3.1. Updated Oct 29. |
| 12 | FEDS Notes, Aug 2, 2019; Dolmas–Koenig, Dallas Fed Economics, May 30, 2019 | saved in the same folder | [S] | Saved, not read. |
| 13 | ScienceDirect pii S016920702300047X; SSRN 5254123 | see `outputs/A_paywalled.csv` | unverified | HTTP 403. |
| 14 | Pace University, official finals transcript, Nov 21, 2025 | `02_Research/External_views/Previous_Finalists_copy/2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf` (Fed: https://www.federalreserve.gov/mediacenter/files/fed-challenge-winner-qa-transcript-20251121.pdf) | [O] | Presentation pp. 1–10, Q&A pp. 10–19. |
| 15 | `2025 Finals - 1 Presentations.md`, `- 2 Q&A Question Log.md`, `- 3 Q&A Response Strategies.md` | `02_Research/External_views/Previous_Finalists_copy/` (parent folder, not inside `2025 /`) | [O] [2] | Secondary analyst notes. |
| 16 | Slide 2 audited outputs (cited, not recomputed) | `02_Research/Subtasks/10_slide2_research/report_D.md` item 11; `outputs/D_trimmed_reconcile.csv`, `D_trimmed_above3_fate.csv`; `01_Finals/data/Slide2_Inflation_Data.xlsx` `Breadth_measures` rows 52–68 | [O] | Binding inputs. |
