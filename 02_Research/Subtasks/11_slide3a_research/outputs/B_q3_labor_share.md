# Labor share check: Barr "record low of 52.8 percent in the second quarter of 2026"

Script: `code/B_labor_share.py`. Raw: BLS API `bls_api_productivity_costs_2008-2026_2026-11-15.json` (series PRS85006174, 064, 054); FRED/ALFRED JSON `fred_PRS85006173_full_2026-11-15.json`, `alfred_PRS85006173_vintages_2026-11-15.json` in `03_Data/Raw/S3A_B_labor_costs_2026-11-15/`. Tags: [O] opened.

## Series identified
- Barr (speech 2026-11-12, saved text) says "labor share of national income" and gives no source; footnote 15 cites NY Fed Liberty Street (Audoly et al., 2026) for the post-COVID decline. The percent-level series matching 52.8 is the **BLS nonfarm business sector labor share, level (percentage), PRS85006174** (labor compensation / nominal value-added output of the nonfarm business sector, SA). BLS also publishes it as an index, PRS85006173 (2017=100; FRED PRS85006173). [O: API, FRED]
- Check: 2026Q3 PRS85006064/PRS85006054 = 13,436.4 / 25,370.2 = 52.96% vs published level 53.0. Index-to-level factor (2017 average level / 100) = 0.5650.
- It is a share of nonfarm business output, **not** "national income". A BEA national-income measure does not give 52.8 (below).

## Current vintage (Productivity & Costs, 2026Q3 prelim, released 2026-11-05)
| Quarter | PRS85006174 level (%) | PRS85006173 index (2017=100) |
|---|---|---|
| 2024Q4 | 54.4 | 96.350 |
| 2025Q1 | 54.7 | 96.861 |
| 2025Q2 | 54.3 | 96.113 |
| 2025Q3 | 53.8 | 95.254 |
| 2025Q4 | 54.0 | 95.643 |
| 2026Q1 | 54.0 | 95.518 |
| 2026Q2 | 53.3 | 94.362 |
| 2026Q3 | 53.0 | 93.729 |

**2026Q2 = 53.3%; 2026Q3 = 53.0%.** Neither is 52.8 in the current vintage.

## Vintage reconstruction (index from ALFRED x factor; derived, not published levels)
| Vintage | 2026Q1 | 2026Q2 | 2026Q3 |
|---|---|---|---|
| May 7 2026 (2026Q1 prelim) | 54.07 (idx 95.707) | n/a | n/a |
| Aug 6 2026 (2026Q2 prelim) | 53.59 (idx 94.843) | 52.85 (idx 93.547) | n/a |
| Sep 3 2026 (2026Q2 revised) | 53.59 (idx 94.843) | 52.80 (idx 93.446) | n/a |
| Nov 5 2026 (2026Q3 prelim; BEA annual-update revisions) | 53.97 (idx 95.518) | 53.31 (idx 94.362) | 52.96 (idx 93.729) |

The Sep 3 vintage of 2026Q2 (idx 93.446) converts to ~52.8; the Aug 6 vintage (93.547) to ~52.9. **52.8 therefore matches the pre-Nov-5 vintage of the BLS nonfarm business labor share, 2026Q2** (inference from index x factor; BLS published levels for old vintages not retrieved). The Nov 5 release (BEA annual-update revisions back to 2021Q1) revised 2026Q2 UP to 53.3. Barr spoke Nov 12, after that release.

## Record-low status (index, 1947Q1-2026Q3, current vintage)
- Lowest in published history: **2026Q3 (93.729)**; second lowest 2026Q2 (94.362). Third 2025Q3 (95.254).
- Lowest reading before 2025Q3: 2025Q2 (96.113); 2025Q3 (95.254) was the first quarter below it, i.e. the index has been at or near record lows since 2025Q3.
- Quarters since 2000 that set a new low (current vintage): 2003Q3, 2004Q1, 2005Q1, 2005Q2, 2005Q3, 2005Q4, 2006Q2, 2006Q3, 2009Q1, 2009Q3, 2009Q4, 2010Q1, 2010Q4, 2011Q4, 2013Q4, 2022Q2, 2022Q4, 2023Q1, 2023Q3, 2023Q4, 2025Q2, 2025Q3, 2026Q2, 2026Q3
- Level path (BLS level series, 2008+): 2008Q4 60.0; 2017 avg 56.5; 2019 avg 56.5; 2021Q3 56.9; 2023 avg 54.6; 2025 avg 54.2; 2026Q3 53.0.
- Was 2026Q2 a record low when Barr likely read it (Sep 3 vintage idx 93.446)? Yes: BLS revisions in the Nov 5 release reach back only to 2021Q1, so pre-2021 history is unchanged, and its minimum is 97.562 (2013Q4); the lowest earlier 2021+ quarter in the Sep 3 vintage was 94.843 (2018+ window shown). 93.446 is below all of them. In the current vintage 2026Q2 (94.362) is no longer the lowest, because 2026Q3 (93.729) is lower.

## Other "labor share" measures (BEA, FRED; not matching 52.8)
| Quarter | Compensation of employees / National income (%) | Compensation / GDI (%) |
|---|---|---|
| 2025Q4 | 60.3 | 50.4 |
| 2026Q1 | 60.4 | 50.4 |
| 2026Q2 | 59.7 | 49.9 |
| 2026Q3 | n/a (2026Q3 NI/GDI not yet published) | n/a |

Sources: FRED COE, NICUR, GDI (BEA; pulled 2026-11-15). Neither BEA ratio is 52.8 for 2026Q2 (about 59.7 and 49.9). Business-sector (PRS84006173) index moves with nonfarm business (93.745 in 2026Q3).

## Did the Q3 release revise it?
Yes. 2026Q2: 93.446 (Sep 3) -> 94.362 (Nov 5) = level ~52.8 -> 53.3 (+0.5 pt); 2026Q1: 94.843 -> 95.518 (~53.6 -> 54.0); 2025Q3: 95.999 -> 95.254. 2026Q3 prelim 53.0 (idx 93.729), -0.3 pt vs revised 2026Q2. Direction of the post-2025 decline is unchanged; the ~52.8 level is gone.

## Caveats
- Barr describes it as a share of "national income"; the BLS series is a share of nonfarm business output (excludes government, nonprofits, households incl. owner-occupied housing). Barr does not name the series; the match to PRS85006174 (pre-revision) is inferred from the number, not confirmed with the Board. UNVERIFIED as his source.
- 2020Q2 spike (58.9%) is a pandemic composition effect.