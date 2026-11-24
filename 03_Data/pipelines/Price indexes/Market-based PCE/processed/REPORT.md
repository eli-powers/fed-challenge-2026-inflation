# Market-based PCE basket | retrieval report

Retrieval date: 2026-11-10; latest period used: 2026M09.
Sources: BEA U20404/U20405, NIPA Table 2.8.4 lines 30-31, and BEA FAQ 83 (Price indexes/Market-based PCE/raw/BEA_market_based_PCE_FAQ_2026-11-10.html); raw tables: Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json; Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json; Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json; Price indexes/PCE/raw/BEA_NIPA_T20807_2026-11-10.json.
BEA says market-based PCE uses observed prices (primarily detailed CPIs/PPIs), excludes most imputed expenditures, most insurance, gambling, used light-vehicle margins, net travel abroad, and NPISH final consumption; owner-occupied rent is included.
Component membership and cited classification are in pce_market_membership.csv. Every N/A has a reason; explicit insurance exclusions/inclusions follow BEA FAQ 83.
Weights rescale included components to market-based nominal expenditures. Headline/core contributions use same change formulas as PCE; aggregate indexes are BEA T20804 lines 30/31.
Reconciliation reports gaps versus BEA (FAQ-based membership, retrieve step; the rebuilt BEA-composition-table version is documented below when rebuild_market_based.py has run): Market-based headline 12m gap -0.102 pp; Market-based headline 3m_ann gap -0.404 pp; Market-based headline 1m gap 0.012 pp; Market-based core 12m gap -0.121 pp; Market-based core 3m_ann gap -0.293 pp; Market-based core 1m gap -0.003 pp; the 12-month gaps are within the 0.15 pp review threshold.
Investigation: BEA source data expose market-based nominal amounts by broad parent category, not by each 178 leaf. FAQ-based leaf membership and rescaled PCE leaf weights therefore cannot reproduce all market-based Fisher contributions; no allocation was invented.
Limitation: BEA FAQ supplies category-level rules, not a full line-by-line 178-component crosswalk; detailed membership is documented as an inference, not an official BEA flag.

<!-- rebuild_market_based.py section -->
## Rebuilt market-based basket (BEA 2009 composition tables), run-time results
Latest 2026M09; bases 12m 2025M09, 3m 2026M06, 1m 2026M08. Inputs: BEA_NIUnderlyingDetail_U20404_2026-11-10.json; BEA_NIUnderlyingDetail_U20405_2026-11-10.json.
T20804 published (BEA_NIPA_T20804_2026-11-10.json): line 1: 12m 3.649, 3m ann 3.558, 1m 0.491; line 25: 12m 3.121, 3m ann 2.903, 1m 0.317; line 30: 12m 3.731, 3m ann 3.692, 1m 0.538; line 31: 12m 3.118, 3m ann 2.936, 1m 0.339
U20404 lines 377/402 vs T20804 lines 30/31 (12m): 3.731/3.118 vs 3.731/3.118.
Core rule: exclude U20404 lines 73-103, 113-119, 169-171 (clothing 104-112 stays core); category core substitutes line 166 for 386.
Rate reconciliation (sum of contributions vs BEA U20404 line 377/402 index ratio):
- leaf | sum contributions, headline vs line 377: 12m pct (2025M09->2026M09): computed 3.803 vs BEA 3.731, gap 0.072 pp
- leaf | sum contributions, headline vs line 377: 3m annualized pct (2026M06->2026M09): computed 3.742 vs BEA 3.692, gap 0.050 pp
- leaf | sum contributions, headline vs line 377: 1m pct (2026M08->2026M09): computed 0.542 vs BEA 0.538, gap 0.004 pp
- leaf | sum contributions, core vs line 402: 12m pct (2025M09->2026M09): computed 3.150 vs BEA 3.118, gap 0.032 pp
- leaf | sum contributions, core vs line 402: 3m annualized pct (2026M06->2026M09): computed 2.981 vs BEA 2.936, gap 0.046 pp
- leaf | sum contributions, core vs line 402: 1m pct (2026M08->2026M09): computed 0.344 vs BEA 0.339, gap 0.005 pp
- category | sum contributions, headline vs line 377: 12m pct (2025M09->2026M09): computed 3.764 vs BEA 3.731, gap 0.033 pp
- category | sum contributions, headline vs line 377: 3m annualized pct (2026M06->2026M09): computed 3.698 vs BEA 3.692, gap 0.006 pp
- category | sum contributions, headline vs line 377: 1m pct (2026M08->2026M09): computed 0.538 vs BEA 0.538, gap -0.000 pp
- category | sum contributions, core vs line 402: 12m pct (2025M09->2026M09): computed 3.124 vs BEA 3.118, gap 0.005 pp
- category | sum contributions, core vs line 402: 3m annualized pct (2026M06->2026M09): computed 2.936 vs BEA 2.936, gap 0.001 pp
- category | sum contributions, core vs line 402: 1m pct (2026M08->2026M09): computed 0.339 vs BEA 0.339, gap 0.000 pp
Nominal reconciliation (2026M09):
- leaf | sum market leaves vs line 377 Market-based PCE: computed 19394236 vs BEA 19391362, gap 2874 (0.01%)
- leaf | sum market core leaves vs line 402 MB core: computed 16898821 vs BEA 16895944, gap 2877 (0.02%)
- leaf | domestic services in-kind (approx 7% of line 328; non-market, included in leaf sum): computed 2730 vs BEA 0, gap 2730 (nan%)
- leaf | implied in-kind domestic service in line 328 (leaf sum line 398 minus BEA line 398) as % of line 328: computed 7 vs BEA 7, gap 0 (5.40%)
- category | sum of non-overlapping lines 378-383,385-391,393-398 vs line 377: computed 19391357 vs BEA 19391362, gap -5 (-0.00%)
- category | sum of core category set (386 replaced by line 166) vs line 402: computed 16895939 vs BEA 16895944, gap -5 (-0.00%)
Category-level nominal gaps, max abs: $2878 mn (leaves mapped to line 384 Market-based PCE services)
Composition codes with no current line: [('market', 'TSP', 'Tenant-occupied stationary homes'), ('market', 'TLD', 'Tenant landlord durables'), ('non-market', 'OMB', 'PCE Other-than-Market-based'), ('non-market', 'GDN', 'Goods Other-than-Market-based'), ('non-market', 'NFR', 'Net expenditures abroad by U.S. residents'), ('non-market', 'SEN', 'Services Other-than-Market-based'), ('non-market', 'DMI', 'Domestic services, in kind (unpublished)'), ('non-market', 'FOR', 'Net foreign travel')]
