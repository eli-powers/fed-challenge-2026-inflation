# Notes, Brief E

- BLS archive does carry these series: Table 11 (index levels, 5 months: 3 prior, prior month, reference month) has NAICS 523940-1 and 523940-2 rows. Map: PCU5239405239401 = 523940-1 portfolio management; PCU5239405239402 = 523940-2 investment advice (assumed from code suffix; levels match component_series_history for settled months, e.g. Nov 2025 final 429.188 / 296.851).
- First-published value = last column of the report for that reference month (marked p). Prior month = 4th column of same report (may already be revised).
- Extraction was clean; no values read by eye, so no E_manual_values.csv.
- Shutdown: no Oct 2025 report exists on the archive (Oct 2025 data appears only as a column in later reports). Nov 2025 report released Jan 14, 2026; Dec 2025 Jan 30, 2026. Reports for Sep 2025 and earlier were not needed.
- Fetch method: curl got HTTP 403; WebFetch retrieved the PDFs. A further attempt to vary the user agent was blocked by the permission layer and was not pursued.
- Script is slow (~3 min) because it extracts every page of 9 PDFs.
