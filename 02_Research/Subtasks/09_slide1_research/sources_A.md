# Sources, Agent A (all [O] = opened by script or tool this run)

| Use | File | Tag | Notes |
|---|---|---|---|
| PCE index levels | `03_Data/pipelines/Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json` | [O] | Table 2.8.4, 2017=100, SA; line 1 DPCERG, line 25 DPCCRG; LastRevised Oct 29, 2026 |
| Oct 2026 estimate | `02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv`, `D_build_2026-10_lines.csv` | [O] | built Nov 13 |
| Workbook tab compared | `03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx`, tab "PCE Oct 2026 estimate", C5:C12, F5:F12 | [O] | cached values (data_only) |
| Backtest | `.../04_oct_pce_build/outputs/D2_backtest_variant_first_release_pm.csv`, `backtest_results.csv`, `D2_..._meta.csv` | [O] | |
| Forecasters | `.../04_oct_pce_build/outputs/R_forecaster_oct2026_2026-11-14.csv` | [O] | press rows are [2]; not re-checked, no web access |
| Bowman | `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` | [O] | textutil text conversion |
| Waller | `.../speeches/2026-11-10_Waller_economic_outlook.pdf` | [O] | pypdf; quote on pypdf page 3 |
| Logan, Paulson, Jefferson | `.../speeches/2026-11-10_Logan_..html`, `2026-11-10_Paulson_..html`, `2026-11-13_Jefferson_..html` | [O] | saved HTML, BeautifulSoup text |
| BEA release | `03_Data/Raw/BEA_PIO_release_Sep2026_2026-11-14/personal-income-and-outlays-september-2026.html` | [O] | embargo 8:30 a.m. EDT Oct 29, 2026 |
| Cleveland Oct path | `.../04_oct_pce_build/outputs/R_cleveland_oct2026_2026-11-14.csv`; raw `03_Data/Raw/ClevelandFed_nowcast_{month,year}_2026-11-14.json` | [O] | |
| Officials summary | `02_Research/External_views/Fed_officials_2026-11/summary.md` | [O] | [2] for anything not re-verified in the speech |
| 2025 finalists | `02_Research/External_views/Previous_Finalists_copy/2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf`; `2025 Finals - 1 Presentations.md` | [O] PDF; md is [2] | |

Scripts (all `python3 -I`, from project root): `code/A_common.py`, `A_ts_pce_rates.py`, `A_headline.py`, `A_backtest.py`, `A_outside_existing.py`, `A_r4_sep_check.py`, `A_r5_cleveland.py`, `A_worth_a_look.py`.
Dependencies: openpyxl, pypdf, bs4, macOS `textutil` (A_outside_existing.py only).
