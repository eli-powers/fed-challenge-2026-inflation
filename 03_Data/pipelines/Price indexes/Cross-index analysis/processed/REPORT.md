# BEA CPI/PCE reconciliation and source mapping | report

Retrieval date: 2026-11-10; source vintage is the latest available at retrieval (2026M09).
Table 9.1U (U90100) latest monthly period in API response: 2026M09; 2026M09 is published.
Raw sources: BEA API U90100 (Price indexes/Cross-index analysis/raw/BEA_NIUnderlyingDetail_U90100_2026-11-10.json); NIPA Handbook Chapter 5 (Price indexes/Cross-index analysis/raw/BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf).
cpi_pce_reconciliation.csv retains BEA Table 9.1U values and row labels as returned by the publisher API, covering monthly and quarterly where available.
pce_ppi_priced_components.csv captures 17 Chapter 5 source-table lines mentioning CPI/PPI/producer price indexes.
NIPA Handbook Tables 5.A-5.B give component-group sources/methods at broader product-category scope; no one-to-one PPI series mapping is published for every Dallas leaf in that table.
Rows therefore preserve exact handbook source text and mark component-level PPI assignments N/A where the handbook does not specify a leaf mapping.
Formula/weight/scope reconciliation is published in Table 9.1U; see raw API payload and processed CSV for exact row definitions/values.
