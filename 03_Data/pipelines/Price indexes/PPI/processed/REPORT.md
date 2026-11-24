# PPI basket retrieval

- Question: Can BLS FD-ID final-demand and intermediate-demand component contributions be reproduced through Sep 2026?
- Sources: BLS PPI relative-importance workbooks (Dec 2024), wp.series/pc.series lists, BLS API v2; archive: https://www.bls.gov/ppi/tables/final-demand-intermediate-demand-special-requests.htm
- FD terminal RI rows=33 (sum 100.000%); ID terminal RI rows=27; parent sums: ID61=99.998%; ID62=99.999%; ID63=99.999%.
- Weights use December 2024 RI repriced by component/aggregate NSA relatives; weights are normalized within each basket for the start of each horizon.
- Rates: 1m and 3m annualized use SA where available, otherwise NSA; 12m uses NSA. Contributions equal start-period weight times component rate.
- Reconciliation gaps above 0.15 pp: annualized 3m FD4=+0.204 pp, ID61=+0.292 pp, ID62=+2.760 pp. The required linear weighted-contribution formula annualizes each component before summing; this diverges most for volatile ID62 commodity movements because annualization is nonlinear. 12m/1m FD4 gaps are within 0.02 pp.
- named_series.csv verifies each exact WPU commodity or PCU industry ID against official series lists; hospital inpatient and outpatient are separate rows.
- Uncertainty: any missing observations or codes stay blank and can widen reconciliation gaps; no neighboring series is substituted.
