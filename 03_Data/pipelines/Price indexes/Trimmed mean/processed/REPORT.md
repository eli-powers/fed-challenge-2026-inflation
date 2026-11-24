# Cleveland Fed median and trimmed-mean CPI

- Sources: Cleveland Fed median CPI page and its published CSV/XLSX/ZIP component files; all seven page-listed files saved to raw/.
- Component table columns are preserved: 1-month annualized percent change, normalized relative importance, cumulative relative importance.
- Latest period identified from the publisher's Median CPI page: Oct 2026. Component values/weights are not reconstructed.
- Cleveland Fed defines the 16% trimmed mean by excluding component-weight shares below the 8th and above the 92nd percentiles.
- trimmed_tails.csv lists published component rows that overlap those tails, including boundary components, with full published weights and cumulative weights.
- Tail assignment uses the published cumulative weight to identify which published rows cross 8% and 92%; no trimmed mean is recalculated.
- All raw payloads and the component-table source path are recorded in the processed files.
