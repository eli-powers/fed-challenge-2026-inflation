# Notes: Agent B (oil paths and pass-through mapping), 2026-11-15

## Run order (from the project root, python3 -I)
1. `code/B_q3_fetch.py`: EIA/FRED daily, EIA futures (discontinued), STEO vintages, FEDS accessible version.
2. `code/B_q3_fetch_futures.py`: NYMEX BZ closes via Yahoo [2]. Raw files are cached; delete the folder to refetch.
3. `code/B_q3_build.py`: daily/quarterly Brent, STEO vintage tables, oil paths, provisional gaps.
4. `code/B_q3_gap_sensitivity.py`: gaps vs A's Aug-11 futures.
5. `code/B_q4_response.py`: Fig. 2 table, reconstruction tests, implied coefficients, mapping checks, worked example.
6. `code/B_q4_identification.py`: constrained-persistence fit of the Fig. 2 lines.

For the forecast script: `from B_common import map_gap_to_core`; R_k is `outputs/B_q4_response.csv` with provenance=="table".

## Decisions taken
- **Path 1 central:** Nov-2026 STEO, a primary source. The futures curve (Nov 13, secondary) is the alternative.
- **2026Q4 splice:** day-weighted, observed 0.469 / rule 0.531.
- **Rules start 2026-11-12.**
- **Path 2:** $110 flat is the central case; the Oct average, $123.93, is the alternative.
- **Path 3:** Feb-2026 STEO + $25 is the central case. Alternatives: +$20, +$30, +$0, and the Jan–Feb spot average + $25.
- **Pre-war:** through 2026-02-27; onset 2026-02-28 per EIA STEO Mar 2026.
- **Gaps:** in log points, starting 2026Q3. They are provisional vs the Aug-2026 STEO, and A's file agrees on those numbers.
- **Response:** uses the note's Fig. 2 table (provenance=table). Reconstruction is reported only as a test. No interpolation.

## Not done
- Optional headline mapping via energy's PCE share and a crude-to-gasoline rule: skipped for time.

## Irregularities (also in the final report)
- **Fig. 2's pre and persistence-only lines don't match Table 2's pass-through sum.**
  - They need a pass-through sum of about 0.0025–0.003, not 0.001. Reconstruction errs by −66% to −69% at k=12.
  - The post line reproduces within +1.5% to +5%.
- **Fig. 2 values vs text:** 0.044, 0.088 and 0.360 at k=12, against the text's "0.05", "just under 0.1" and "0.35".
- **The post response is non-monotone and back-loaded:** it dips at k=1 and jumps at k=4.
- **Every path except P3 +$0 sits above the Aug-STEO assumption.** P3 +$25 converges to the Nov STEO by 2027Q4 ($78 vs $77).
- **The pre-war "trend" is low:** the Feb STEO's $53–55 was about $14 below the Jan–Feb spot average.
- **The proxy choice matters a lot:** Aug STEO vs Aug-11 futures moves 2027 gaps by 8–15 log points.
- **The Nov STEO is stale at the front:** its Nov–Dec forecasts ($104, $99) are above spot (~$92) and the front future ($95.8).
- **EIA's NYMEX futures series were discontinued in Apr 2024.**
