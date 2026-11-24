# Agent E: first-release values for the portfolio-management PPIs (Sonnet 5.5, returned 2026-11-12)

Held outside `report.md` while Codex Audit 1 round 1 runs (audited files are frozen). To be merged into `report.md` after the round.

## Findings
- **Recovered for all nine reference months, Nov 2025 – Jul 2026.** BLS's archived PPI Detailed Reports (https://www.bls.gov/ppi/detailed-report/) carry both series in Table 11, NAICS 523940: row 523940-1 portfolio management (`PCU5239405239401`), row 523940-2 investment advice (`PCU5239405239402`). Each report shows five monthly levels; the last is the reference month (preliminary) and the fourth is the prior month as shown in that same report.
- Oct 2025 has no report (shutdown). Nov 2025 data was released Jan 14, 2026; Dec 2025 on Jan 30, 2026.
- Extraction was clean; no value was read by eye. Table: `outputs/E_pm_ppi_first_release.csv`. Script: `code/E_pm_ppi_first_release.py`. PDFs: `03_Data/Raw/BLS_PPI_detailed_report_<YYYY-MM>_retrieved_2026-11-12.pdf`.

| Ref month | Series | First-print m/m % (same report) | Current m/m % | Revision pp |
|---|---|---|---|---|
| 2025-11 | PM | 1.441 | 1.352 | −0.089 |
| 2025-11 | IA | 0.450 | 0.722 | +0.272 |
| 2025-12 | PM | 2.011 | 0.637 | −1.373 |
| 2025-12 | IA | 0.335 | 0.133 | −0.202 |
| 2026-01 | PM | 1.480 | 2.711 | +1.231 |
| 2026-01 | IA | 0.079 | 0.624 | +0.545 |
| 2026-02 | PM | 0.972 | 1.075 | +0.102 |
| 2026-02 | IA | 0.241 | 0.448 | +0.207 |
| 2026-03 | PM | 0.991 | 1.046 | +0.055 |
| 2026-03 | IA | 0.150 | 0.138 | −0.012 |
| 2026-04 | PM | −2.352 | −1.799 | +0.553 |
| 2026-04 | IA | −2.888 | 0.904 | +3.792 |
| 2026-05 | PM | 4.842 | 5.182 | +0.340 |
| 2026-05 | IA | 5.384 | 3.117 | −2.268 |
| 2026-06 | PM | 0.514 | 0.531 | +0.017 |
| 2026-06 | IA | 1.434 | 1.577 | +0.143 |
| 2026-07 | PM | 6.458 | 6.669 | +0.211 |
| 2026-07 | IA | 0.175 | −0.063 | −0.238 |

PM = portfolio management; IA = investment advice. NSA.

## Worth a look (agent)
- The prior month shown in a report often differs from that month's own first print (e.g. Dec 2025 PM: 439.001 first printed, 438.267 in the next report, 431.923 now).
- Largest revisions: IA Apr 2026 (first −2.89%, now +0.90%; the sign flipped) and IA May 2026 (−2.27 pp); PM Dec 2025 (−1.37 pp) and Jan 2026 (+1.23 pp).
- PM rose 6.5% in Jul 2026 and 4.8% in May 2026. Not investigated.

## What to verify (agent)
- PDFs came through a fetch tool, not a manual download. Release dates come from the schedule table in the Jul 2026 report.
- The row-to-series mapping rests on code suffixes and level agreement with settled history.

## Coordinator review (Agent E)
**Verified, and how.** I opened the April, May and July 2026 PDFs with pypdf and read the six rows directly. All six first-release and prior-month levels match the CSV (e.g. April 2026 PM "431.923 443.630 448.403 453.120 442.464"; IA "297.246 299.100 300.483 301.056 292.360").

**Not checked.** The other six reports; the release dates; a manual re-download from bls.gov.

**Coordinator note.** For the backtest the right real-time monthly change is the one computed within a single report (reference month over the prior month as shown in that report), since that is what a user of the data had on that day. The table's `first_print_mm_pct` is on that basis.
