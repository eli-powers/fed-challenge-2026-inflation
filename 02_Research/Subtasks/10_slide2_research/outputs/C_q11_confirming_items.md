# Q11. Confirming items for indirect energy effects in Oct 2026 data

Data tables: `C_q11_confirming_items.csv` (Feb 2026 = 100 paths, peaks, Sep/Oct readings), `C_q11_series.csv` (monthly 2018-01 to 2026-10, mm / 3m annualized / y/y), `C_q11_lag_stats.csv` and `C_q11_lag_stats_2022on.csv` (lag correlations). Script `code/C_q11_build.py`; raw in `03_Data/Raw/BLS_CPI_PPI_q11_2026-11-15/` and `03_Data/Raw/EIA_fuel_spot_2026-11-15/`; PCE air transportation from pipeline raw `Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json` (BEA Table 2.4.4U line 207, last revised Oct 29, 2026; ends Sep 2026).
Vintage: BLS API pulled 2026-11-15 (Oct CPI, released Nov 10 per STATE.md; Oct PPI, released Nov 13; Jul-Oct PPI preliminary). All [O]. Horizons: mm = 1 month; 3m ann = (I_t/I_{t-3})^4 - 1; y/y. SA where stated; PPI commodity fuel and trucking series are NSA only.
**Gap:** BLS did not publish Oct 2025 CPI, so CPI y/y for Oct 2026 and CPI 3m rates ending Oct-Dec 2025 do not exist; the lag statistics drop Oct and Nov 2025 for CPI series. Oct PCE is not yet published (BEA); the PCE air series ends Sep 2026.

## Item 1: Airfares (CPI airline fares vs jet fuel)
| Series (ID) | Sep 2026 mm / 3m ann / y/y | Oct 2026 mm / 3m ann / y/y | Feb 2026 = 100 in Oct |
|---|---|---|---|
| CPI airline fares, SA (CUSR0000SETG01) | +1.2 / +27.1 / +22.4 | **+0.4 / +18.3 / n.a.** | 115.8 |
| PCE air transportation, SA (U20404 line 207) | +4.4 / +30.0 / +20.5 | not published | 114.1 (Sep) |
| PPI airline passenger services, SA (WPS3022) | +4.8 / +17.7 / +16.4 | -1.2 / +27.0 / +15.0 | 108.6 |
| PPI jet fuel, NSA (WPU057203) | +13.8 / +173.9 / +96.1 | **+7.0 / +421.7 / +106.5** | 197.0 |
| EIA US Gulf Coast jet fuel spot, monthly avg, $/gal | +17.8 / +332.9 / +110.1 | +2.2 / +201.2 / +108.1 | 198.2 ($2.26 to $4.48) |

**Evidence for fuel pass-through**
- Co-movement in the shock: fares rose through Mar-May 2026 (CPI 102.7, 105.6, 108.4; Feb = 100) as PPI jet fuel jumped (141, 178, 173).
- Monthly changes correlate with jet fuel: CPI fares vs PPI jet fuel r = 0.42 same month and 0.39 one month later; vs EIA jet r = 0.43 at a one-month lag (2018-01 to 2026-10, n = 104; 2022 on: 0.39-0.40, n = 56). Beyond two months the correlation is about zero.
- Level of the readings: CPI fares +22.4% y/y in Sep and PCE air +20.5% y/y, against an average y/y of -1.8% (CPI) and +2.7% (PCE) in 2018-19.
- Oct: jet fuel +7.0% m/m (a new high, 197 vs Feb) and CPI fares still +0.4%, 3m ann +18.3%: no reversal.

**Evidence against (or complicating)**
- Fares were rising before the oil spike: CPI fares Dec 2025 to Feb 2026 +8.0% (262.6 to 283.5) while PPI jet fuel rose only 9.5% (225.5 to 247.0) before the March jump; so some of the 2026 rise is not fuel.
- Weak scale and fit: CPI fares are +15.8% since Feb against jet fuel +97%, a ratio of about 0.16, and the monthly correlation of 0.4 explains about 16% of the variance. PPI airline services correlate only 0.2-0.3 with jet fuel (best lag 0 to 2 months) and its Oct move was down.
- Asymmetry: when jet fuel fell Jun-Jul (143 and 130, Feb = 100) CPI fares kept rising (108.6 to 111.0): fares did not retrace, consistent with sticky pricing or demand/capacity, not with a mechanical cost pass-through.
- Seasonal adjustment matters for the PPI airline series: Oct is -1.2% SA but +4.3% NSA (WPU3022); the SA/NSA gap is about 5.5 pp in one month. BLS release text lists airline passenger services among Oct decliners in final-demand services.
- Demand evidence not assembled (no passenger-volume series pulled); "demand vs cost" cannot be separated from price data alone.
- Concept: airfares embed fuel as a direct cost for airlines, so they are an energy-intensive item rather than clean second-round evidence. The FEDS note itself does not separate indirect from second-round effects (fn 11).

## Item 2: Freight and delivery costs (truck transportation vs diesel), with food away from home as the downstream test
| Series (ID) | Sep 2026 mm / 3m ann / y/y | Oct 2026 mm / 3m ann / y/y | Feb 2026 = 100 in Oct |
|---|---|---|---|
| PPI truck transportation of freight, NSA (WPU3012) | +3.8 / +27.5 / +19.8 | **+3.9 / +51.7 / +24.6** | 122.4 |
| PPI No. 2 diesel, SA (WPS057303) | +19.9 / +306.6 / +114.9 | **-7.9 / +256.5 / +115.2** | 194.6 |
| EIA US Gulf Coast ULSD spot, monthly avg, $/gal | +16.1 / +348.8 / +114.8 | -2.2 / +132.0 / +116.4 | 207.6 |
| PPI final demand transportation and warehousing, SA (WPSFD422) | +3.4 / +20.5 / +16.2 | +2.0 / +36.3 / +18.5 | 115.4 |
| CPI food away from home, SA (CUSR0000SEFV) | +0.2 / +3.2 / +3.5 | **+0.5 / +4.1 / n.a.** | 102.3 |
| CPI full service meals, SA (CUSR0000SEFV01) | +0.3 / +3.8 / +3.8 | +0.7 / +5.6 / n.a. | 102.7 |

**Evidence for**
- Freight prices keep rising after diesel peaks: trucking +3.9% in Oct while diesel fell 7.9% (SA; BLS release: "diesel fuel prices fell 7.9 percent"). Monthly trucking changes correlate with diesel at 0.55 (same month) and with EIA ULSD at 0.66 one month earlier (2018-2026; 0.67 on 2022+): a fuel-surcharge-type lag.
- BLS release: "Over 80 percent of the October increase in the index for final demand services is attributable to prices for truck transportation of freight, which rose 3.9 percent"; stage 1 and stage 3 text names truck transportation of freight among Oct advances. Trucking y/y 24.6% vs a 2018-19 average of 4.5%.

**Evidence against**
- Weak downstream pass-through so far: CPI food away from home is only +2.3% since Feb (102.3), Oct 3m ann 4.1%, Sep y/y 3.5% vs 2.9% average in 2018-19. Freight is +22% over the same period (ratio about 0.1).
- Lag correlation truck freight -> food away from home peaks at 6 months (0.33; 0.34 on 2022+), the edge of the window tested, with n = 104; diesel -> food away from home is about 0 (max 0.11-0.21). That is thin evidence of any link, and it cannot be tested yet for the energy shock that started in March (Oct is month 7 of the shock, 3-4 months after the trucking surge).
- Trucking prices rose 3.9% in both Sep and Oct: a catch-up with diesel is as consistent with surcharge timing as with spreading; the Oct diesel drop (and the early-Nov oil drop) has not yet reached trucking.

## What Oct 2026 shows (summary, data only)
- Airfares: no reversal in CPI (+0.4% m/m, 3m ann +18.3%); PPI airline services -1.2% SA; jet fuel +7.0%.
- Freight: trucking +3.9% m/m with diesel -7.9%; food away from home +0.5% m/m, still modest on a 3m basis (4.1%).
- Cross-check (`Fed_officials_2026-11/summary.md`): Paulson (Nov 10) points to knock-on effects in airfares and fertilizer, and Jefferson (Nov 13) says energy "shows up indirectly in airfares and transport"; this agrees with items 1 and 2 upstream and in CPI airfares, and is not borne out yet in food away from home.
