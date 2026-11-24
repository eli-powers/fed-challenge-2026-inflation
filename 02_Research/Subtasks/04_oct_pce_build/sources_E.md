# Sources, Brief E

- [O] BLS PPI Detailed Report archive index, https://www.bls.gov/ppi/detailed-report/ (read via WebFetch 2026-11-12; curl returned HTTP 403). Lists PDFs as `ppi-detailed-report-<month>-<year>.pdf`. 2025: Jan-Sep, Nov, Dec (October 2025 not available); 2026: Jan-Sep.
- [O] Nine PDFs, each fetched from `https://www.bls.gov/ppi/detailed-report/ppi-detailed-report-<month>-<year>.pdf` (Nov 2025, Dec 2025, Jan-Jul 2026), saved to `03_Data/Raw/BLS_PPI_detailed_report_<YYYY-MM>_retrieved_2026-11-12.pdf`. Opened with pypdf; Table 11 ("Producer price indexes for net output of selected industries and their products, not seasonally adjusted"), product codes 523940-1 (portfolio management) and 523940-2 (investment advice).
- [O] Release dates: schedule table on p.3 of the Jul 2026 report.
- [O] Current values: `outputs/component_series_history.csv` (not re-downloaded).
