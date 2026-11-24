# BLS retrieval report

Retrieved: 2026-11-10
BLS API v2 requests: 2000–2019 and 2020–2026, catalog=true, calculations=true.
Distinct series IDs requested: 49; observations.csv rows: 11773.

## Series and coverage
- `cpi_u_all_items_sa`: CUSR0000SA0; 2000-01-01 to 2026-10-01; 322 distinct dates; catalog titles: All items in U.S. city average, all urban consumers, seasonally adjusted
- `cpi_u_all_items_nsa`: CUUR0000SA0; 2000-01-01 to 2026-10-01; 322 distinct dates; catalog titles: All items in U.S. city average, all urban consumers, not seasonally adjusted
- `cpi_u_core_sa`: CUSR0000SA0L1E; 2000-01-01 to 2026-10-01; 322 distinct dates; catalog titles: All items less food and energy in U.S. city average, all urban consumers, seasonally adjusted
- `cpi_u_core_nsa`: CUUR0000SA0L1E; 2000-01-01 to 2026-10-01; 322 distinct dates; catalog titles: All items less food and energy in U.S. city average, all urban consumers, not seasonally adjusted
- `ppi_final_demand_sa`: WPSFD4; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand, seasonally adjusted
- `ppi_final_demand_nsa`: WPUFD4; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand, not seasonally adjusted
- `ppi_intermediate_61_sa`: WPSID61; 2000-01-01 to 2026-09-01; 321 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Processed goods for intermediate demand, seasonally adjusted
- `ppi_intermediate_61_nsa`: WPUID61; 2000-01-01 to 2026-09-01; 321 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Processed goods for intermediate demand, not seasonally adjusted
- `ppi_intermediate_62_sa`: WPSID62; 2000-01-01 to 2026-09-01; 321 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Unprocessed goods for intermediate demand, seasonally adjusted
- `ppi_intermediate_62_nsa`: WPUID62; 2000-01-01 to 2026-09-01; 321 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Unprocessed goods for intermediate demand, not seasonally adjusted
- `ppi_intermediate_63_sa`: WPSID63; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Services for intermediate demand, seasonally adjusted
- `ppi_intermediate_63_nsa`: WPUID63; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Intermediate demand by commodity type-Services for intermediate demand, not seasonally adjusted
- `ppi_final_demand_trade_services_sa`: WPSFD423; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand trade services, seasonally adjusted
- `ppi_final_demand_trade_services_nsa`: WPUFD423; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand trade services, not seasonally adjusted
- `ppi_personal_consumption_trade_sa`: WPSFD42311; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand-Trade of personal consumption goods, seasonally adjusted
- `ppi_personal_consumption_trade_nsa`: WPUFD42311; 2009-11-01 to 2026-09-01; 203 distinct dates; catalog titles: PPI Commodity data for Final demand-Trade of personal consumption goods, not seasonally adjusted
- `eci_civilian_total_compensation`: CIS1010000000000I, CIU1010000000000I, CIS1010000000000Q, CIU1010000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Total compensation for all civilian workers, current dollar index | Total compensation for all civilian workers, current dollar index | Total compensation for all civilian workers, 3-month percent change, current dollars | Total compensation for all civilian workers, 12-month percent change, current dollars
- `eci_civilian_wages_and_salaries`: CIS1020000000000I, CIU1020000000000I, CIS1020000000000Q, CIU1020000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Wages and salaries for all civilian workers, current dollar index | Wages and salaries for all civilian workers, current dollar index | Wages and salaries for all civilian workers, 3-month percent change, current dollars | Wages and salaries for all civilian workers, 12-month percent change, current dollars
- `eci_civilian_benefits`: CIS1030000000000I, CIU1030000000000I, CIS1030000000000Q, CIU1030000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Total benefits for all civilian workers, current dollar index | Total benefits for all civilian workers, current dollar index | Total benefits for all civilian workers, 3-month percent change, current dollars | Total benefits for all civilian workers, 12-month percent change, current dollars
- `eci_private_total_compensation`: CIS2010000000000I, CIU2010000000000I, CIS2010000000000Q, CIU2010000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Total compensation for all private industry workers, current dollar index | Total compensation for all private industry workers, current dollar index | Total compensation for all private industry workers, 3-month percent change, current dollars | Total compensation for all private industry workers, 12-month percent change, current dollars
- `eci_private_wages_and_salaries`: CIS2020000000000I, CIU2020000000000I, CIS2020000000000Q, CIU2020000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Wages and salaries for all private industry workers, current dollar index | Wages and salaries for all private industry workers, current dollar index | Wages and salaries for all private industry workers, 3-month percent change, current dollars | Wages and salaries for all private industry workers, 12-month percent change, current dollars
- `eci_private_benefits`: CIS2030000000000I, CIU2030000000000I, CIS2030000000000Q, CIU2030000000000A; 2001-01-01 to 2026-07-01; 103 distinct dates; catalog titles: Total benefits for all private industry workers, current dollar index | Total benefits for all private industry workers, current dollar index | Total benefits for all private industry workers, 3-month percent change, current dollars | Total benefits for all private industry workers, 12-month percent change, current dollars
- `productivity_unit_labor_costs`: PRS85006111, PRS85006112, PRS85006113; 2000-01-01 to 2026-07-01; 107 distinct dates; catalog titles: Unit labor costs for the Nonfarm business sector, % Change same quarter 1 year ago | Unit labor costs for the Nonfarm business sector, % Change from previous quarter | Unit labor costs for the Nonfarm business sector, Index (2017=100)
- `productivity_labor_productivity`: PRS85006091, PRS85006092, PRS85006093; 2000-01-01 to 2026-07-01; 107 distinct dates; catalog titles: Labor productivity for the Nonfarm business sector, % Change same quarter 1 year ago | Labor productivity for the Nonfarm business sector, % Change from previous quarter | Labor productivity for the Nonfarm business sector, Index (2017=100)
- `productivity_hourly_compensation`: PRS85006101, PRS85006102, PRS85006103; 2000-01-01 to 2026-07-01; 107 distinct dates; catalog titles: Hourly compensation for the Nonfarm business sector, % Change same quarter 1 year ago | Hourly compensation for the Nonfarm business sector, % Change from previous quarter | Hourly compensation for the Nonfarm business sector, Index (2017=100)
- `ppi_intermediate_total`: ; N/A to N/A; 0 distinct dates; catalog titles: 

## Verification
- BLS API catalog=true titles are recorded in series_metadata.csv; CPI page: https://www.bls.gov/cpi/.
- PPI exact IDs and titles checked against the official FD-ID catalog: https://www.bls.gov/ppi/fd-id/ppi-final-demand-intermediate-demand-aggregation-indexes-by-title-and-series-id.htm.
- Trade margin for personal consumption is published as `Trade of personal consumption goods` (42311); this is the BLS exact catalog title.
- ECI encodings checked against the official SA/NSA, ownership, estimate, and datatype guide: https://www.bls.gov/eci/factsheets/eci-series-id-guide.htm
- ECI SA benefits index and 3-month rate series are published for civilian and private workers; all requested ECI IDs were returned by BLS.
- Productivity IDs and Q3 2026 preliminary data checked against BLS release/tables: https://www.bls.gov/news.release/prod2.nr0.htm
- **N/A — no single all-stage total intermediate-demand index** is listed; documented in metadata.

## FRED cross-checks
- Latest three values compared where FRED offers the same series; tolerance 0.00011.
- ECI NSA index levels matched across all six groups; SA FRED indexes have no observations after 2017 Q4, and FRED returned HTTP 400 for the exact Q/A rate IDs, so those current series could not be cross-checked.
- Other series matched: cpi_u_all_items_sa; cpi_u_all_items_nsa; cpi_u_core_sa; cpi_u_core_nsa; ppi_final_demand_sa; ppi_final_demand_nsa; ppi_intermediate_61_sa; ppi_intermediate_61_nsa; ppi_intermediate_62_sa; ppi_intermediate_62_nsa; ppi_intermediate_63_sa; ppi_intermediate_63_nsa; ppi_final_demand_trade_services_sa; ppi_final_demand_trade_services_nsa; ppi_personal_consumption_trade_sa; ppi_personal_consumption_trade_nsa; productivity_unit_labor_costs; productivity_labor_productivity; productivity_hourly_compensation.

## Release dates and notes
- release_dates.csv covers 13 latest observations per monthly/quarterly series; all rows have ALFRED output_type=4 first-release dates.
- CPI Oct 2025 values are empty (BLS footnote X: lapse in appropriations); Nov 2025 values are published by BLS and retained.
- Productivity and Costs Q3 2026 preliminary release: November 5, 2026; ECI Q3 release: October 30, 2026.
- BLS API requests used 49 IDs (limit 50) in each required year window; no rates were calculated locally.
