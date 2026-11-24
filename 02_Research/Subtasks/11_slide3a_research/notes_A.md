# Agent A raw notes (Nov 15, 2026)

## Rerun order (from the project root, `python3 -I`)
1. `code/A_download_vu.py` downloads the V/U data. Raw files go to `03_Data/Raw/S3A_A_vu_2026-11-15/`. On a new vintage, change the date folder.
2. `code/A_vu.py` writes `outputs/A_q1_vu.csv` and `A_q1_vu_summary.json`.
3. `code/A_q1_channels.py` writes `outputs/A_q1_bb_channels.csv`.
4. `code/A_extract_texts.py` extracts the PDFs: BB, the Pace transcript and Dolmas 2005.
5. `code/A_html_text.py <html…>` converts the HTML files to text. The Dallas and Cleveland files were downloaded with curl into `03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/`; that curl step was not scripted.
6. `code/A_logan_extract.py` extracts the speech paragraphs.
7. `code/A_q2_dallas_data.py` reads the Dallas chart data.
8. `code/A_quotes.py` runs the verbatim checks (69/69 found) and writes the quote md/csv files.

## Q1: Bernanke–Blanchard (BB) w31417
Page numbers below are printed page numbers. The PDF page is printed + 1.

**Equations:**
- **Eq 1, p.6: wage level.** w = pᵉ + ω^A + βx. The nominal wage follows expected prices, an aspiration real wage and labor-market tightness x.
- **Eq 2, p.7: aspiration real wage.** ω^A = αω^A(−1) + (1−α)(w(−1)−p(−1)) + z_ω. This is a weighted average of the past aspiration and the past realized real wage. It is the device for catch-up.
- **Eq 3, p.7: wage growth.** Δw = (pᵉ−p(−1)) + α(p(−1)−pᵉ(−1)) + β(x−αx(−1)) + z_w. Wage growth equals expected inflation, plus the catch-up term (last period's inflation surprise), plus tightness in level and change.
- **Eq 4, p.8: price equation.** Δp = Δw + Δz_p. Prices follow wages (unit labor costs, in the empirical version) plus non-labor price shocks: energy, food and shortages.
- **Eq 5, p.8: short-run expectations.** pᵉ−p(−1) = δπ* + (1−δ)(past inflation). δ measures short-run anchoring.
- **Eq 6, p.9: long-run expectations.** π* = γπ*(−1) + (1−γ)(past inflation). γ measures long-run anchoring.
- **Calibrations, Figs 1–2, pp.10–11.**
  - Weak feedback, α=0.2, δ=0.9, γ=0.95: a permanent level shock leaves inflation +0.06 higher permanently.
  - Strong feedback, α=0.6, δ=0.7, γ=0.9: +0.34.

**Estimation:**
- Quarterly data, 1990Q1–2019Q4. The price equation runs to 2023Q1, because the shortage term needs covid variation.
- Four lags of each variable, with homogeneity imposed.
- Variable list: Table 1, pp.13–14.

**Tables:**

| Table (page) | Equation | Key coefficient sums |
|---|---|---|
| 2 (p.17) | Wage | gw 0.460, v/u 0.693 (p=0.030), catch-up −0.024 (p=0.765), cf1 0.540, gpty 0.031 |
| 3 (p.24) | Price | gp 0.335, gw 0.665, grpe 0.066, grpf 0.126 (p=0.050), shortage 0.018 (sum p=0.281; joint p=0.000), gpty −0.143 |
| 4 (p.27) | Short-run expectations (cf1) | cf1 0.369, cf10 0.506, gp 0.124 |
| 5 (p.29) | Long-run expectations (cf10) | cf10 0.975, gp 0.025 |

- The Table 5 note says the sample is 1990Q1–2019Q1. The text says pre-covid 2019Q4, so the note is probably a typo.

**Robustness (appendix):**
- PCE in place of CPI, Table A2, p.42: v/u sum 0.774; price-equation gw 0.499.
- SPF expectations, Table A3, p.43: v/u 1.154; catch-up 0.087, not significant.

**Figures:**

| Figure | Page | Shows | Text detail |
|---|---|---|---|
| 1, 2 | 10–11 | Analytical impulse responses | — |
| 3 | 19 | Wage fit | — |
| 4, 5 | 20–21 | CRB principal component vs energy and food | First PC explains 66.0% of variance |
| 6 | 23 | Autos | — |
| 7 | 26 | Price fit | — |
| 8, 9 | 28–29 | Expectations fit | — |
| 10 | 31 | Price-shock impulse responses | Text p.30 |
| 11 | 32 | v/u impulse response | +0.7 at 6q, +1.0 at 12q, then +0.15/yr |
| 12 | 33 | Inflation decomposition | Text p.34 |
| 13 | 35 | Wage decomposition | Text p.34 |
| 14 | 37 | Projections | Text p.38 |

- **Shock standard deviations** (fn 15, p.30), measured over 2020Q1–2023Q1:

  | Shock | SD | Range |
  |---|---|---|
  | Energy relative price | 32% | +45 to −52 |
  | Food relative price | 3.2% | +8.9 to −1.3 |
  | Shortage index | 11.6 | 10 to 48 |
  | v/u | 0.5 | 0.26 to 1.91 |

- **Bar values are not in the text.** The paper's replication files (nber.org/data-appendix/w31417) could give them, but were not opened.

**Projections (pp.36–38):**
- v/u lowered to 1.8 / 1.2 / 0.8 over 8 quarters from 2023Q2.
- Resulting CPI path: rising / ~2.7% / ~2%.
- Implied natural rate of unemployment: 3.6% if the Beveridge curve returns to its pre-pandemic position, ~4.3% if it stays at its early-2023 position. Footnote 18 uses u ∝ (v/u)^−0.6.

**Citation check:**
- Python searches of the full text and reference list for "Reis", "state-dependent" and "state dependent" found **0 hits**.
- The only Phillips-curve nonlinearity citations (p.5) are Cecchetti et al. (2023), Benigno & Eggertsson (2023, NBER WP 31197) and Gagnon & Sarsenbayev (2022). BB contrast them with their own linear fit.
- The roadmap's "Reis (2021) and the state-dependent-pricing cite" are not in this paper. No other project file contains either string except the roadmap; the slide 3B folder was not searched, per the rules. The origin is unknown.
- Reis (2021) itself exists: Brookings summary page [O]. Title "Losing the Inflation Anchor", BPEA Fall 2021, pp. 307–361. The paper is about expectations de-anchoring across episodes.

**V/U data** (`A_q1_vu.csv`, current vintage):
- Monthly peak 2.039 (Mar 2022). Quarterly peak 1.932 (2022Q2). BB's 1.91 matches the quarterly figure.
- 2018–19 average 1.160. 2019Q4 1.187; BB used 1.2.
- Latest 1.058 (Sep 2026). Jul–Sep average 1.047.
- Last-12m low 0.873 (Dec 2025). V/U crossed 1.0 in Apr 2026 (1.029).
- UNRATE: Oct 2026 4.1; 2018–19 average 3.78; 2021–23 low 3.4 (Apr 2023).
- Gaps: Oct 2025 CPS missing (shutdown), so V/U and UNRATE are missing for that month. Oct 2026 JOLTS is not yet out, so the Oct 2026 V/U is missing.
- BB's 2023Q1 "approximately 1.8" is 1.694 in the current vintage. JOLTS revisions since June 2023 lowered openings.
- Jan 2026 jump, 0.873 → 0.983. This may reflect January CPS population controls and the JOLTS annual revision; not checked.

## Q2: see `outputs/A_q2_trimmed_bias.md`

## Q7: see `outputs/A_q7_pace_quotes.md`
- The md files are in `Previous_Finalists_copy/`, not inside `2025 /`.
- "compensation" never appears in the Pace transcript. The notes' "Pace relates compensation and productivity to price pressure" maps to Bynum p.6 ("high wage growth … productivity").
