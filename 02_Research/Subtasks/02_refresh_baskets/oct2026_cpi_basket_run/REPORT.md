# CPI-U basket retrieval

- Question: Can BLS CPI-U U.S. city-average basket contributions be reproduced through Oct 2026?
- Sources: BLS API v2 for aggregate index observations; BLS annual RI page: https://www.bls.gov/cpi/tables/relative-importance/
- IDs: CUSR0000SA0 / CUUR0000SA0 (all items); CUSR0000SA0L1E / CUUR0000SA0L1E (less food and energy).
- Coverage requested: 2017–2026; latest month Oct 2026. API responses are batch-cached in raw/.
- Inputs: BLS CPI flat files cu.item/cu.series; Table 1 Dec 2024 and Dec 2025; 204 hierarchy leaves retained (unmatched leaf series remain explicit N/A).
- Dec 2025 leaf RI sum=100.001%; core leaf sum=79.917% versus published core RI 79.919%.
- Core excludes food, nonalcoholic beverage leaves, and the six energy leaves; alcoholic beverages remain in core. The Dec 2025 core leaf RI sum is checked against the published core RI. Weights update from matching December RI by component/all-item NSA price relatives; core rows are separately rescaled to 100.
- Formulae: pct_1m=(I_t/I_t-1-1)*100; pct_3m_ann=((I_t/I_t-3)^4-1)*100; pct_12m=(I_t/I_t-12-1)*100. Contributions=starting RI share x rate; excess contribution=current 12m starting weight x (component 12m minus its 2018–19 mean).
- Sources: BLS API v2; BLS CPI relative importance: https://www.bls.gov/cpi/tables/relative-importance/
- CPI October 2025 observations are N/A because BLS did not collect October CPI (footnote X); November 2025 remains published.
- Investigation: headline 12m gap is -0.295 pp (>0.15); RI update has weight coverage 94.607% at Aug 2025 and 95.684% at Aug 2026, with 33–34 leaves lacking required item-series observations or a catalog series. This coverage shortfall is the leading explanation; the residual cannot be allocated to missing leaves.
- Headline and core contributions and gaps are in reconciliation.csv; gaps above 0.15 pp require review of unavailable leaf series and weight dating.
