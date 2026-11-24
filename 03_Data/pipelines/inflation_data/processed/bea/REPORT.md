# BEA PCE price data retrieval

Retrieved: 2026-11-10. Scope: monthly SA BEA price indexes, Jan 2000 through latest API observation; no derived rates computed.
BEA API parameter inventory verified NIPA T20804/T20807 and NIUnderlyingDetail U20404. T20804 note states index numbers, 2017=100, seasonally adjusted; table latest revision recorded in raw responses.
Latest Personal Income and Outlays release used: September 2026, released 2026-10-29. The Sept. 30, 2026 annual update affects 2021Q1 onward.

## Retrieved series

- `pce_price` — BEA T20804 line 1 (DPCERG), **Personal consumption expenditures (PCE)**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: T20807 line 1 (DPCERGM), label **Percent change from preceding month**, 321 observations; monthly rate, not annualized.
- `pce_core_price` — BEA T20804 line 25 (DPCCRG), **PCE excluding food and energy**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: T20807 line 25 (DPCCRGM), label **Percent change from preceding month**, 321 observations; monthly rate, not annualized.
- `pce_market_based_price` — BEA T20804 line 30 (DPCMRG), **Market-based PCE**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: T20807 line 30 (DPCMRGM), label **Percent change from preceding month**, 321 observations; monthly rate, not annualized.
- `pce_market_based_core_price` — BEA T20804 line 31 (DPCXRG), **Market-based PCE excluding food and energy**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: T20807 line 31 (DPCXRGM), label **Percent change from preceding month**, 321 observations; monthly rate, not annualized.
- `pce_services_ex_energy_housing_price` — BEA T20804 line 28 (IA001260), **PCE services excluding energy and housing**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: T20807 line 28 (PP001260), label **Percent change from preceding month**, 321 observations; monthly rate, not annualized.
- `pce_goods_ex_food_energy_price` — BEA U20404 line 375 (IA000062), **PCE goods excluding food and energy**; 2000-01–2026-09, 321 index observations; index 2017=100, SA.
  - Rates: no exact series in the BEA monthly price-change companion table T20807; no rate constructed.

## Verification and FRED comparisons

Exact series titles, line numbers, codes, unit/base, seasonal adjustment, and last-revised notes were checked in saved BEA GetData responses. Table names were checked against saved GetParameterValues responses.
FRED is used only as a cross-check and for ALFRED first-release dates; BEA observations remain primary.
- `pce_price` / `PCEPI`: matches on latest 3 overlapping observations: 2026-07-01: BEA 131.187, FRED 131.187, diff +0.000; 2026-08-01: BEA 131.611, FRED 131.611, diff +0.000; 2026-09-01: BEA 132.257, FRED 132.257, diff +0.000.
- `pce_core_price` / `PCEPILFE`: matches on latest 3 overlapping observations: 2026-07-01: BEA 130.148, FRED 130.148, diff +0.000; 2026-08-01: BEA 130.489, FRED 130.489, diff +0.000; 2026-09-01: BEA 130.902, FRED 130.902, diff +0.000.
- `pce_market_based_price` / `DPCMRG3M086SBEA`: matches on latest 3 overlapping observations: 2026-07-01: BEA 128.998, FRED 128.998, diff +0.000; 2026-08-01: BEA 129.407, FRED 129.407, diff +0.000; 2026-09-01: BEA 130.103, FRED 130.103, diff +0.000.
- `pce_market_based_core_price` / `DPCXRG3M086SBEA`: matches on latest 3 overlapping observations: 2026-07-01: BEA 127.463, FRED 127.463, diff +0.000; 2026-08-01: BEA 127.773, FRED 127.773, diff +0.000; 2026-09-01: BEA 128.206, FRED 128.206, diff +0.000.
- `pce_services_ex_energy_housing_price` / `IA001260M`: differences on latest 3 overlapping observations: 2026-07-01: BEA 134.279, FRED 134.300, diff -0.021; 2026-08-01: BEA 134.780, FRED 134.800, diff -0.020; 2026-09-01: BEA 135.274, FRED 135.300, diff -0.026. FRED's values are shown to one decimal while BEA reports three; differences are within 0.05 and consistent with FRED rounding.
- `pce_goods_ex_food_energy_price`: no exact monthly FRED equivalent found; checked FRED series search response. Latest 13 first-release dates use BEA's Personal Income and Outlays release calendar/archive.

## N/A and unresolved

- Goods excluding food and energy is available as U20404 line 375, exactly titled 'PCE goods excluding food and energy'; no matching series was present in NIPA T20804 or T20807. FRED search found no exact monthly series. The underlying-detail index is retained; no rate is fabricated.
- BEA publishes 12-month headline and core changes in current release text, but the API inventory has no monthly PCE price 12-month-change table. These two release-text rates are not reconstructed as a time series here.
- Release-date rows for the goods series use official BEA Personal Income and Outlays monthly release dates; all other series use ALFRED output_type=4. If BEA does not return an ALFRED date for a month, the date is left blank rather than inferred.
- A post-Sept. 30 rerun will reflect revised current BEA values, not freeze this pre-update vintage; raw filenames include retrieval date. No request parameter for historical BEA vintage was identified in this API workflow.
