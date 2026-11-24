# config/ provenance

These files are fixed inputs that are not re-downloaded on each run. Each is a copy of a
coordinator-verified research output (subtask `02_Research/Subtasks/12_slide3b_research/`, 2026-11-15).
Do not edit them by hand; if a source changes, re-copy and update the checksum here.

| File | Copied from | sha256 of the source file at copy time | What it is |
|---|---|---|---|
| `regime_response.csv` | `outputs/B_q4_response.csv`, rows with `provenance == table` (39 rows) | 9e69aa6728ff36753ef828fcd31b386c9b0c64ba7fa9a6352f84cff5b77acf0a | Cumulative core PCE **price-level** response (%) k = 0..12 quarters after a permanent 10% oil-price rise; regimes `pre`, `post`, `persistence_only`. Read from the Figure 2 data table of the accessible version of De Michelis et al., FEDS Note, 2026-11-09 (raw: `03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/DeMichelis_oil_core_accessible_20261109.htm`). Five-economy panel average, not U.S.-specific. |
| `futures_curve_2026-11-13.csv` | `outputs/B_q3_futures_curve.csv` | 9d6dff03cba60746ee59de4ada2a5a549db95082927b5f7308dd46eae74c198f | NYMEX BZ (Brent Last Day Financial) contract closes on 2026-11-13 via the Yahoo Finance chart API. **Secondary source [2]**; CME/ICE pages are blocked. Used only for the P1 alt sensitivity row. Raw: `03_Data/Raw/Yahoo_BZ_futures_current_2026-11-15/`. |
| `assumption_futures_2026Q3.csv` | `outputs/A_q2_oil_assumption.csv`, rows "NYMEX Brent futures (BZ), quarterly mean of 3 contract months" | 9494f5fdb8825519263257c88871450667c292af57c2c82948b29e89b6aca765 | Brent futures as of the Q3-2026 SPF deadline (2026-08-11), 2027Q1-Q4 only (2026 contracts expired, not archived). **Secondary [2]**. Used only for the assumption-proxy sensitivity; 2026Q3-Q4 fall back to the matched STEO. Raw: `03_Data/Raw/Yahoo_BZ_futures_curve_2026-11-15/`. |
| `oil_path_rules.json` | written from `outputs/B_q3_path_definitions.md` and `code/B_q3_build.py` | n/a | Path rules (P1 latest STEO; P2 $110 flat; P3 Feb-2026 STEO + $25) and the alternates. |

A Q4-SPF run needs no config change. An `assumption_futures_<spf>.csv` for the Q4 survey does not
exist; that sensitivity row is then skipped (the script says so).
