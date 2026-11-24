# Q11b follow-up: food vs diesel, transportation services decomposition, motor vehicle insurance

Scripts `code/C_q11b_fetch.py`, `code/C_q11b_build.py` (`python3 -I`, project root). Raw: `03_Data/Raw/CPI_q11b_2026-11-15b/` (BLS API json, CPI release `cpi.nr0` and Table 2 `cpi.t02`, BLS motor-vehicle-insurance factsheet, EIA retail diesel monthly xls). PPI diesel/truck and PCE line 279 are read from files cited in `C_q11_*` / the pipeline (`PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json`). Tags: [O] opened. Data only; no policy reading. Vintage: BLS API pulled 2026-11-15, Oct 2026 CPI (release page last modified Nov 13). BLS did not publish Oct 2025 CPI (release text: "BLS did not collect survey data for October 2025 because of a lapse in appropriations"), so CPI y/y for Oct 2026 does not exist for these series and m/m for Oct-Dec 2025 is missing for insurance; lag correlations drop those months.
Outputs: `C_q11b_food_diesel_series.csv`, `C_q11b_food_diesel_lags.csv`, `C_q11b_transport_services_decomp.csv`, `C_q11b_motor_insurance.csv`.

## 1. Diesel and food (CPI SA m/m, 3m annualized; food is outside core)
| Series | Sep m/m / 3m ann / y/y | Oct m/m / 3m ann | Feb 2026 = 100 in Oct |
|---|---|---|---|
| CPI food at home, SA (SAF11) | -0.07 / -0.42 / +1.8 | **+0.44 / +1.65** | 101.1 |
| CPI food away from home, SA (SEFV) | +0.23 / +3.22 / +3.5 | **+0.52 / +4.08** | 102.3 |
| EIA retail on-highway diesel, $/gal (3.72 Feb, 6.29 Sep, 6.25 Oct) | +15.2 / +145.9 / +67.9 | -0.6 / +153.5 (y/y +69.9) | 168.0 |
| PPI diesel, SA (WPS057303) | +19.9 / +306.6 / +114.9 | -7.9 / +256.5 | 194.6 |
| PPI truck freight, NSA (WPU3012) | +3.8 / +27.5 / +19.8 | +3.9 / +51.7 (y/y +24.6) | 122.4 |
- 2018-19 average y/y: food at home +0.7%, food away +2.9%, truck freight +4.5%. The BLS release table agrees on Oct m/m (food at home +0.4, away +0.5).
- 2026 food at home m/m, Jan-Oct: +0.19, +0.44, -0.16, +0.68, +0.06, +0.19, -0.07, +0.04, -0.07, +0.44 (the Oct reading is the largest since April). Food away: +0.15 to +0.32 each month, +0.52 in Oct.
- **Lag correlations of monthly % changes** (x leads y by L months; full table in `C_q11b_food_diesel_lags.csv`; n about 100 for 2018+, 56 for 2022+):
  - Retail diesel -> food at home: 2018+ about 0.0-0.2 at lags 0-2, maximum 0.22 (lag 7); 2022+ 0.30 at lags 1-2, then 0.1-0.26.
  - Retail diesel -> food away: about 0 at lags 0-2 (-0.21 at lag 0 for 2022+), 0.20-0.25 at lags 3-4, maximum 0.31 at lag 7 (both windows).
  - PPI diesel (SA) -> food: at most 0.17 (2018+) and 0.23 (2022+, lag 1).
  - Truck freight -> food at home: 0.29-0.33 at lags 2-8 (2018+), 0.31-0.49 (2022+, peak 0.49 at lag 8); truck freight -> food away: 0.38 at lag 7 (2018+), 0.44 at lag 7 (2022+).
- What Oct shows: diesel is 68% above Feb at retail and flat m/m; truck freight keeps rising (+3.9%); food at home and away both stepped up (+0.44, +0.52), but cumulative since Feb food at home is +1.1% and food away +2.3%. The Oct 2026 y/y does not exist.
- Caveat in the data: the correlations are of noisy monthly changes, share the 2021-22 episode, and peak at long lags (7-8 months) that are only 3-4 months old in this shock (diesel jumped in March; Oct is month 7).

## 2. CPI transportation services, Oct +0.8% SA: decomposition
Weights: BLS CPI Table 2, relative importance Sep 2026 [O]. Contribution = (component weight / 6.256) x component m/m. Published SA m/m (rounded to 0.1) used; where an SA series exists the unrounded API value agrees.
| Component | Weight (% of CPI) | Share of transp. services | Oct m/m | Contribution (pp) |
|---|---|---|---|---|
| Intracity transportation (mass transit, SS53031) | 0.366 | 5.9% | +6.6 | **+0.39** |
| Motor vehicle insurance | 2.510 | 40.1% | +0.7 | **+0.28** |
| Motor vehicle maintenance and repair | 1.065 | 17.0% | +0.6 | +0.10 |
| Airline fares | 1.055 | 16.9% | +0.4 | +0.07 |
| Motor vehicle fees | 0.495 | 7.9% | +0.7 | +0.06 |
| Other intercity transportation | 0.225 | 3.6% | +1.4 | +0.05 |
| Leased cars and trucks | 0.382 | 6.1% | 0.0 | 0.00 |
| Car and truck rental | 0.153 | 2.4% | -5.7 | -0.14 |
| **Sum of components** | 6.251 | | | **+0.80** (parent published +0.8; API unrounded +0.84) |
- Public transportation total +2.0% (weight 1.651). Parent path SA m/m May-Oct: -0.58, -0.35, +0.28, +0.45, +0.59, +0.84.
- Drivers: intracity mass transit (+0.39 pp, about half of the 0.8) and motor vehicle insurance (+0.28 pp). Mass transit is a very small-weight, "special index based on a substantially smaller sample" (release footnote 3) and its SA m/m equals the NSA (footnote 1).
- Energy-linked candidates, by the data only: airfares (jet fuel is a direct input; +0.07 pp; see `C_q11_confirming_items.md`); intracity transit fares (fuel is a cost but no source tested here: unverified); motor vehicle maintenance and repair (+0.10 pp; parts and labor, no direct fuel input). Car rental fell 5.7% (offsetting after +5.4% in Sep). Insurance has no energy link in the BLS definition (item 3).

## 3. CPI motor vehicle insurance (CUSR0000SETE, SA)
- m/m 2026: Jan -0.44, Feb -0.33, Mar -0.04, Apr +0.14, May -1.69, Jun -2.01, Jul -0.29, Aug -0.75, **Sep +0.06, Oct +0.71** (published: -0.8, +0.1, +0.7). 3m annualized Oct +0.1 (Jun -13.4, Jul -14.9). y/y: Sep -4.98% (NSA same), Aug -5.13% (the low since 2024); y/y was +22.6% at the Apr 2024 peak, +3.2% in Sep 2025 and averaged +4.2% in 2018-19. Oct y/y not published.
- Oct +0.71% ranks 42nd of 103 months (2018-2026 m/m available); Sep ranks 73rd. The Oct move is not unusual in size.
- Oct and Nov history (SA m/m): Oct 2018 +0.60, 2019 +0.16, 2020 -2.17, 2021 -0.71, 2022 +1.61, 2023 +1.97, 2024 -0.02, 2026 +0.71 (2025 not published). NSA Oct: +0.92, +0.50, -1.72, -0.30, +2.01, +2.35, +0.31, +1.00. No consistent October pattern in SA.
- **What drives it per BLS** [O] (factsheet `.../cpi/factsheets/motor-vehicle-insurance.htm`): the index measures premiums for fixed policy/driver/vehicle characteristics (collision, comprehensive, liability and other coverages). "Once a year, usually in October or November, the model year of each vehicle in our sample is updated by 1 year"; this "often results in premium changes", up where newer models mean "higher expenses associated with a newer model such as the cost of repairs", down for safety features. The BLS Oct release gives no cause for the +0.7% beyond listing it among increasing indexes. The factsheet contains no fuel or energy link. Nothing here tests an energy link: unverified.
- Candidate-driver data (SA y/y, Sep 2026): motor vehicle maintenance and repair +5.8%, new vehicles +0.6%, used vehicles -1.5% (Oct: new +0.7%, used -3.3%). Repair costs are rising while premiums fall y/y.
- **CPI-PCE gap:** PCE "Net motor vehicle and other transportation insurance" (BEA U20404 line 279, SA): y/y +3.4% Jan, +1.4% Mar, +1.0% Jun, +0.96% Aug, **+0.3% Sep** (m/m -0.05); CPI -5.0% Sep. The gap widened from about -0.6 pp (Mar) to -5.3 pp (Sep). Concept difference: the PCE line is a net-of-losses measure (line label "Net ..."); BEA FAQ 83 [O] says motor vehicle insurance is excluded from market-based PCE; the "premiums minus normal losses" definition comes from a search snippet [S], not opened: unverified.

## Worth a look
1. Mass transit (+6.6%) supplies about half of the 0.8 on a tiny weight and a small-sample special index.
2. Insurance CPI fell 12 months and then rose 0.7% in Oct at the annual model-year update window; no read on whether it persists (Nov 2026 will show).
3. Food at home Oct +0.44 is the largest since Apr, with diesel flat and trucking +3.9%: one month only.
4. PCE insurance y/y fell from +3.4% (Jan) to +0.3% (Sep) while CPI went from +0.6% to -5.0%.
5. Oct-Dec 2025 insurance m/m missing (lapse in appropriations), so y/y comparisons around Oct 2026 are unavailable.

## Spot-checks
1. `C_q11b_transport_services_decomp.csv`, row "Motor vehicle insurance": weight 2.510, Oct +0.7, contribution 0.281; BLS `cpi.t02` text row "Motor vehicle insurance 2.510 - 1.0 -0.8 0.1 0.7".
2. `C_q11b_motor_insurance.csv` 2026-09: yoy -4.98, pce_yoy 0.30; pipeline `PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` line 279.
3. `C_q11b_food_diesel_series.csv` CUSR0000SAF11 2026-10: mm 0.44; BLS release Table A food at home +0.4.

## What to verify
- BEA's exact PCE motor-vehicle-insurance methodology (opened only as a snippet).
- Whether intracity transit fares carry any fuel component (no source opened).
- Whether Nov 2026 CPI insurance reverses the Oct step.
