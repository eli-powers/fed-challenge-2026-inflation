# S2 notes: goods NAICS concordance and AI match

## Method
- Input: outputs/units_all_for_mapping.csv, 695 rows; 551 goods rows (codes 01-15) mapped, 144 services rows (30-80) left to the AI-match step.
- Mapping done from item names plus the coordinator-supplied brief rules, drawing on NAICS 2017 structure knowledge [2: my recall, no BLS commodity-to-NAICS file opened].
- Validity check [O]: every mapped NAICS code (non-SCRAP) is covered by (prefix of / prefixed by) a code in col G of the 'NAICS Codes' sheet of CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx. This confirms BEA-grouping coverage, not that a specific 6-digit code exists in NAICS 2017.
- Corrections made after that check: 2017 merged codes (335220 major appliances, 333517 machine tools, 333318 service machinery, 332999 enameled sanitary ware).
- Script: scratchpad build.py (mapping text m1.txt/m2.txt); outputs are deterministic from those.
- Attempted BLS factsheet fetch (bls.gov/ppi/factsheets/...data-processing...) [O]: page had no commodity-to-NAICS mapping. AI-match rows therefore rest on [2] item-name reasoning; unverified.

## Conventions
- Multiple codes mean ambiguous producer industry; level column shows the coarsest digits among them.
- SCRAP: 091201/091203/091207 (recyclable paper), 101211-101215, 102301-102303, 131702 (glass), 072C01 (plastics).
- 053101/053201 mapped to 211130 (production), not 2212, since these are production indexes, not distribution (brief gave 054*/055* only).
- 102301 etc. nonferrous scrap flagged SCRAP; secondary smelted metals (1024xx) mapped to 3314 industries.

## Worth a look
- 108905 "Other metal products" (stage4 weight 1.633) is a residual mixed bag; low-confidence 332999;332919.
- 141205 "Motor vehicles parts" (3.783 stage4) mapped at 4-digit 3363; BEA import share for the whole parts sector will be an average over very different parts.
- 139902 clay and stone mining spans several 2123 industries.
- 119408/119413 engines: PPI engine items may be produced by vehicle makers (336310), not only 333618.
- 117821 relays sits in BLS group 1178 (electronic components) but is NAICS 335314, outside 3344.
- 453201 Engineering services is a single broad item; no municipal-utility line exists in the CSV. 
- No software publishing (5112/513210) items in the CSV. Services 381xx are the only data/hosting items; 381102 Business process management excluded as not 518210 primary.
- 336101 Directory/mailing list compilations publishing (stage1 0.494) is publishing (5111/519130), not software.
