# Market-based PCE basket | retrieval report

Retrieval date: 2026-09-27; latest period used: 2026M07.
Sources: BEA U20404/U20405, NIPA Table 2.8.4 lines 30-31, and BEA FAQ 83 (Price indexes/Market-based PCE/raw/BEA_market_based_PCE_FAQ_2026-09-27.html); raw tables: Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-09-27.json; Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-09-27.json; Price indexes/PCE/raw/BEA_NIPA_T20804_2026-09-27.json; Price indexes/PCE/raw/BEA_NIPA_T20807_2026-09-27.json.
BEA says market-based PCE uses observed prices (primarily detailed CPIs/PPIs), excludes most imputed expenditures, most insurance, gambling, used light-vehicle margins, net travel abroad, and NPISH final consumption; owner-occupied rent is included.
Component membership and cited classification are in pce_market_membership.csv. Every N/A has a reason; explicit insurance exclusions/inclusions follow BEA FAQ 83.
Weights rescale included components to market-based nominal expenditures. Headline/core contributions use same change formulas as PCE; aggregate indexes are BEA T20804 lines 30/31.
Reconciliation reports gaps versus BEA; July 2026 market-based 12-month gaps are -0.354 pp headline and -0.340 pp core, exceeding the 0.15 pp review threshold.
Investigation: BEA source data expose market-based nominal amounts by broad parent category, not by each 178 leaf. FAQ-based leaf membership and rescaled PCE leaf weights therefore cannot reproduce all market-based Fisher contributions; no allocation was invented.
Limitation: BEA FAQ supplies category-level rules, not a full line-by-line 178-component crosswalk; detailed membership is documented as an inference, not an official BEA flag.
