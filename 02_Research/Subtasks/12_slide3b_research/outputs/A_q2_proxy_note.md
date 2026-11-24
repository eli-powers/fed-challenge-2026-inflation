# Q2 proxy note: what oil path did the Q3 2026 SPF baseline condition on?

**Short answer.** SPF respondents report no oil assumption, so none is observable. Best public proxy: the **August 2026 EIA STEO** (released 2026-08-11, modeling completed 2026-08-06, last historical month July 2026). The SPF deadline was also 2026-08-11. Two other benchmarks are shown for bracketing: the July 2026 STEO (released 2026-07-07) and NYMEX Brent futures for 2027 contract months on 2026-08-11 (secondary source).

All numbers: `A_q2_oil_assumption.csv`. Quarterly STEO = simple mean of the three monthly Brent spot values (BREPUUS, sheet 2tab); EIA's own quarterly column is not in the archive workbook, so this is derived.

| Quarter | Aug STEO (proxy) | Jul STEO | Brent futures, Aug 11 (mean of 3 contract months) | Actual EIA spot (daily mean) |
|---|---|---|---|---|
| 2026Q3 | 85.26 | 74.00 | n/a (expired) | 96.30 |
| 2026Q4 | 78.00 | 70.00 | n/a (expired) | 116.73 (partial, to Nov 11) |
| 2027Q1 | 74.00 | 67.67 | 81.48 | not yet |
| 2027Q2 | 71.00 | 65.67 | 78.72 | |
| 2027Q3 | 68.00 | 64.00 | 76.99 | |
| 2027Q4 | 65.00 | 62.00 | 75.76 | |

Spot at the deadline (EIA RBRTE, 2026-08-11): **$93.26**; mean of the 20 trading days before it (2026-07-14 to 2026-08-10): **$90.19** (incl. deadline day $90.67). WTI spot that day $84.77, so Brent minus WTI = **$8.49** (wide; in the Nov 10-11 data it is $0.5-2.5).

## Weaknesses (plain language)
- **SPF forecasters do not report an oil assumption, and nothing says they use STEO.** Many use their own models, bank house views or the futures strip. STEO is one reasonable stand-in, not a measurement of what they assumed.
- **STEO is a model forecast, not a market price.** It sits well below the futures curve: Aug STEO 2027 mean $69.5 vs. futures about $78.2 for 2027 (contract months). The two proxies disagree by roughly $8/bbl in 2027, so the "implied oil path" is a range, not a point.
- **Timing.** Aug STEO was published on the SPF deadline day (Aug 11). Respondents answering earlier saw the July STEO ($11/bbl lower in 2026Q3), and their own spot view (Jul 31 spot $96.95, Aug 6 $89.65).
- **Futures proxy is partial.** Only contract months Jan 2027 and later are retrievable (Yahoo Finance, secondary [2]); 2026 contracts have expired and are not archived. EIA's NYMEX WTI futures files (RCLC1-4) end in April 2024, so they cannot proxy the Aug 2026 curve. ICE and CME are not reachable (see `A_paywalled.csv`). A BZ contract month is the price of that month's futures contract, not the expected monthly average spot.
- **Quarter averages are our arithmetic** (mean of three monthly values), not EIA-published quarterly figures.
- The Q3 SPF (deadline Aug 11) predates the Sep-Oct spike: actual EIA spot averaged $114.16 in Sep and $123.93 in Oct, vs. the Aug STEO's Sep forecast of $85 and Oct forecast of $80 (monthly rows in the CSV). Spot had fallen back to about $92 by Nov 10-11 (Nov mean to date $96.92).
