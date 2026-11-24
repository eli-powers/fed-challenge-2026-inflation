# Research demand data retrieval report

Retrieved 2026-11-10. SEC facts are automated; Conference Board values are limited to official public releases.

## Series retrieved
- `capex_microsoft` (PaymentsToAcquirePropertyPlantAndEquipment): 2023-10-01 to 2026-07-01; latest $39,367m; latest filing https://www.sec.gov/Archives/edgar/data/789019/000119312526436133/
- `capex_alphabet` (PaymentsToAcquirePropertyPlantAndEquipment): 2023-10-01 to 2026-07-01; latest $51,355m; latest filing https://www.sec.gov/Archives/edgar/data/1652044/000165204426000084/
- `capex_amazon` (PaymentsToAcquireProductiveAssets): 2023-10-01 to 2026-07-01; latest $77,259m; latest filing https://www.sec.gov/Archives/edgar/data/1018724/000101872426000040/
- `capex_meta` (PaymentsToAcquirePropertyPlantAndEquipment): 2023-10-01 to 2026-07-01; latest $33,942m; latest filing https://www.sec.gov/Archives/edgar/data/1326801/000162828026066773/
- `capex_microsoft_finance_lease_additions` (RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability): 2023-10-01 to 2026-07-01; latest $5,192m; reported separately and not added to cash capex.
- Conference Board (three indices): 2026-08 only; headline 89.4, Present Situation 121.2, Expectations 68.2; release 2026-08-25. Older values not recovered.
- Conference Board (three indices): September 2024 original release also recovered (98.7, 124.3, 81.7; release 2024-09-24); subsequent revisions unverified.

## N/A coverage
- Conference Board: 22 monthly observations between Sep 2024 and Aug 2026 are N/A because dated public releases were not recoverable; remaining history is proprietary. Revisions are unverified.

## Latest full-year capex guidance (report only)
- Microsoft: approximately $175B calendar 2026 after lease classification change; [FY26 Q4 call](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4).
- Alphabet: $195B–$205B calendar 2026; [Q2 2026 earnings call](https://abc.xyz/investor/events/event-details/2026/2026-Q2-Earnings-Call-2026-GgTAq7Is0z/default.aspx).
- Amazon: approximately $220B cash capex in 2026 per CEO Q2 call; [official Q2 call page](https://ir.aboutamazon.com/events/event-details/2026/Q2-2026-Amazoncom-Inc-Earnings-Conference-Call/default.aspx). Q2 10-Q says cash capex should increase but does not quantify annual guidance.
- Meta: $130B–$145B calendar 2026, including principal payments on finance leases; [Q2 2026 results](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/).

## Verification and caveats
- SEC companyfacts concept labels and filing line titles were checked; SEC filing accession links and raw companyfacts JSON are preserved.
- Quarterly cash capex is in millions of USD, NSA. Q1 equals reported YTD; Q2, Q3, and Q4 are differences of consecutive YTD totals within each fiscal year. Microsoft dates follow fiscal period ends and include period end in each note.
- Amazon uses gross purchases, not net of proceeds or incentives. Microsoft's cash line excludes finance leases; supplemental noncash finance-lease additions are separate and not added.
- Conference Board values are proprietary. September 2024 original and August 2026 latest published levels are included; September 2024 vintage may have been revised. September 2026 release was scheduled after retrieval date.
