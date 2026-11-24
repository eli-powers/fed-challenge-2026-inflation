# Breadth reconciliation: pipeline (P) vs October-build tab (O)

**Date:** 2026-11-14. Opus subagent, read-only on the project. Claude reran `code/recon.py` and `code/oct_leaf.py`, and both reproduce the numbers below. **Not Codex-audited.**
**Breadth:** share of core PCE spending weight with inflation strictly above 3%.

## Answer
The gap comes from **granularity**:
- P uses the 149 core leaves of the Dallas/BEA basket.
- O uses 184 core pricing lines: 13 leaves split into 48 BEA sub-lines.

Everything else is identical or negligible: core set, index vintage (U20404, Nov 10), rate formulas, threshold, and weights (≤0.07 pp).

## Sep 2026, decomposition P → O
| Step | 12m | 3m |
|---|---:|---:|
| P (reproduced) | 60.63 | 44.82 |
| Core set, index, formula, threshold | 0 | 0 |
| Weights (t−12 → start of window) | 0 | −0.003 |
| Granularity (leaves → sub-lines) | −2.91 → **57.71** | −1.15 → **43.67** |

The order of steps barely matters: the interaction is under 0.07 pp.

## Same-method Sep → Oct pairs
| Method | 12m | 3m |
|---|---|---|
| O, sub-lines | 57.7 → 51.1 | 43.7 → 43.8 |
| Leaf level, start-of-window weights | 60.6 → ~54.0 | 44.8 → ~45.5 |

The leaf-level October figures are approximate: a fixed-share roll-up of sub-line estimates.

The tables below show weight and 12m rate; for the 3m flips, see the subagent output. The main ones are line 242 (limited-service meals, 2.95% weight, 3m 2.35%) and line 180 (specialty outpatient, 1.55%, 3.11%).

## Largest 12m flips (sub-line below 3% while its parent leaf is above)
| Sub-line (line) | Weight | 12m rate |
|---|---:|---:|
| Home health care (177) | 1.18% | 1.60% |
| Financial service charges and fees (259) | 0.79% | 1.00% |
| Medical laboratories (178) | 0.29% | 1.18% |
| Homes for the elderly (318) | 0.22% | 1.04% |

## Judgment (subagent's; Claude agrees)
- Neither method is wrong. The error is pairing P's September with O's October. That exaggerates the 12m drop by about 2.9 pp and shows a 3m fall that isn't there.
- Pick one method for both months and say which.
- Under either method, 12m breadth falls about 6.6 pp from Sep to Oct, and 3m breadth is flat to slightly up.

## Flags
- About 1.8 of the 6.6 pp October 12m drop sits in the roughly 11% of core that the October build carries forward (assumed). That is a soft spot.
- The October tab labels mix weight bases: 43.83 on 12m-base weights vs 43.75 on 3m-base weights. Both round to 43.8.
- `04_oct_pce_build/report.md` attributes the tab's core-weight difference to the name-based core flag. That is stale: the core sets are identical.
- Leaves 272 and 13 are net lines, so their sub-line weights look odd. Both are small.

## Code
Run from the project root with `python3 -I`:
- `code/recon.py`: reproduces both methods and runs the switch grid.
- `code/misclass.py`: lists sub-line flips. Pass the scratch or data folder as the first argument.
- `code/oct_leaf.py`: approximate October breadth at leaf level. Same argument.

These read inputs under the project and the session scratchpad.
