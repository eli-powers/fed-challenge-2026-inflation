Status: Audited — converged R2

# Report C: breadth (R6) and component-sum gap

Weight basis: start-of-window nominal shares (U20405, base month of the window). BEA vintage 2026-11-10 (through Sep 2026); Oct = audited build estimate.

## Findings
**1. Core breadth, % of core spending weight with rate > 3% (`outputs/C_breadth.csv`)**

| | Sep 3m ann | Oct 3m ann (est) | Sep 12m | Oct 12m (est) |
|---|---:|---:|---:|---:|
| Sub-line (primary, 184) | 43.667 | 43.752 | 57.713 | 51.127 |
| Leaf (robustness, 149) | 44.814 | 45.467 | 60.626 | 54.038 |

- Reproduces report 07's expected figures (asserted in script).
- Oct leaf figures effectively exact: fixed-share roll-up of sub-line m/m vs BEA leaf m/m over 36 months, MAE 0.004 pp, max 0.08 pp; nearest split leaf to the 3% cutoff is 0.14 pp (12m) / 0.07 pp (3m) away.
- Supercore 12m: 63.95 → 49.45 (sub-line), 68.98 → 54.48 (leaf), −14.5 pp.
- Headline sub-line: 12m 57.21 → 51.40; 3m 42.70 → 44.73.

**2. Time series (`C_breadth_ts.csv`)**, Jan 2018–Sep 2026 + Oct est. 2018–19 average (sub-line): 3m 39.73, 12m 35.70 (leaf 39.20 / 35.25). Extremes (sub-line): 12m max 78.8 (Aug 2022), min 26.6 (Nov 2020); 3m max 76.4 (Feb 2022), min 24.2 (Nov 2020). 3m is noisy: 62.7 (May 2026), 57.9 (Jul), 36.5 (Aug), 43.7 (Sep).

**3. Carried-forward share (`C_carried_forward.csv`)**: report 07's "about 1.8 of 6.6 pp" **not reproduced**.
- "Carried forward" = build's `assumed` tier: 24 lines, 11.2% of core weight; none crosses 3%; contribution to −6.586 pp change: −0.003 pp (leaf: −0.016).
- The drop sits in hospital lines 184/185/186 (8.78% of core weight): 12m 3.337% → 2.734%, contribution −8.72 pp (> 100% of net). One PPI series (`PCU622---622---`, revised, no first release) + our seasonal adjustment. Oct m/m 0.305%; would need 0.564% (+0.26 pp, ~1.1 SD) to stay > 3%. If they stayed above 3%, Oct 12m breadth = 59.91.
- Eight lines cross up (+2.36 pp); tax preparation and window coverings cross down.
- Stress (`C_carried_forward_stress.csv`): all 24 assumed lines ±1 SD → 12m 50.88–51.25; 3m 43.0–51.6.

**4. Component-sum gap (`C_sum_gap.csv`)**, exact additive split gap = (a) convexity + (b) fixed-share vs chained Fisher + (c) residual, sub-line, pp:

| | Sum | Published/est. | Gap | (a) | (b) | (c) |
|---|---:|---:|---:|---:|---:|---:|
| Sep 3m ann | 3.199 | 2.903 | 0.296 | 0.167 | 0.033 | 0.096 |
| Sep 12m | 3.186 | 3.121 | 0.065 | 0 | 0.028 | 0.037 |
| Oct 3m ann (est) | 3.780 | 3.551 | 0.229 | 0.191 | 0.033 | 0.005 |
| Oct 12m (est) | 3.306 | 3.242 | 0.063 | 0 | 0.036 | 0.027 |

- **The quoted 0.130 (Sep) and ~0.23 (Oct) are on different bases.** Workbook Sep sum 3.032 annualizes the aggregate (`fix_3m`), so (a)=0 and 0.130 = (b) 0.037 + (c) 0.093 (leaf). Oct tab's 3.78 annualizes each component, so 0.229 includes (a) 0.19. Like for like: Sep individually annualized (leaf) 3.171 − 2.903 = 0.268; Oct on aggregate-annualized basis ≈ 0.038 vs Sep 0.130.
- (c) unexplained; Sep 3m residual ≈ 1.4 monthly SDs. Oct (c) small partly by construction (Oct "published" is the build's fixed-share m/m).

**5. Cross-checks**: Waller's ">70% of components of core PCE service prices" — Sep count basis gives 63.1% (53/84 leaves) and 58.6% (68/116 sub-lines); only a **weighted** leaf share reproduces >70% (70.8% start-of-window, 71.1% latest). Oct est.: count 60.7% leaf / 56.9% sub-line; weighted 59.7% / 55.9% (`C_waller_variants.csv`). Logan: narrow-vs-widespread framing, one stat (non-housing non-transport core services 3.2% 12m), no breadth number. 2025 finalists: no inflation-breadth statistic found.

## Worth a look (agent)
1. Report 07's 1.8 pp carried-forward claim doesn't hold on any basis tried; soft spot is the hospital block, not the assumed tier.
2. 0.130 vs 0.23 gaps mix bases.
3. Waller's figure matches a weighted share, not a count.
4. Three hospital lines drive > 100% of the Oct 12m breadth drop, rest on one revised PPI series, ~1.1 SD from flipping.
5. Supercore 12m breadth −14.5 pp vs all-core −6.6.
6. 3m breadth very noisy.
7. Oct 2025 base month (missing CPI) not tested.
8. Sub-line 16 (net used autos) negative weight, immaterial.

## Spot-check examples (agent)
Line 186 Sep 12m 3.3368%; line 129 flowers 2.769 → 5.228; core line 374 12m 3.1212 / 3m 2.9025; W-file sums 3.7795 / 3.3055; pipeline retrieval-stage 3.1707 = `S_ann`.

## What to verify (agent)
Meaning of report 07's 1.8; Fisher-chain Paasche step; Waller's component list; 184-line set applied to all history; (b)/(c) vs a chained-Fisher approximation, not BEA's exact method.

## Coordinator review
**Verified independently** (`scratchpad/verify_C2.py`: rates and nominal weights read straight from U20404/U20405 JSON and the build's line m/m; C's code used only for the line→leaf list):
- Sub-line core breadth: Sep 12m 57.713, Oct 12m 51.127, Sep 3m 43.667, Oct 3m 43.752 ✓ (all four exact).
- Leaf Sep 12m 60.626 (n=149) ✓.
- Hospital lines 184/185/186: Sep 12m 3.337; Oct 12m 2.735/2.734/2.734; Oct m/m 0.305 each ✓ (one series drives all three).
- Checked C's sub-line weight function for double counting on the tenant (156/157) and NPISH (342) special cases: sub-line weights sum equals leaf weights sum (18,768,853) ✓.
- Report 07 line 47 does say "About 1.8 of the 6.6 pp October 12m drop sits in the roughly 11% of core that the October build carries forward". C's contradiction of it is supported by my recompute direction (hospitals alone > 100%); I did not independently recompute the assumed-tier −0.003.

**Corrected**: none.

**Material flags for FINAL**: (1) report 07's 1.8 pp claim is superseded; (2) the 0.130 and 0.23 "sum gaps" are on different bases and should not be quoted side by side; (3) the Oct 12m breadth drop is one PPI hospital series.

**Could not check**: Fisher-chain implementation in (b) line by line (Codex ask); Waller footnote on Fed site.

**Interpretive notes (not shared unless asked)**: an Oct 12m breadth "decline" headline is fragile — it is one revised PPI series on 8.8% of weight; leaf vs sub-line difference (~3 pp) is larger than the Oct 3m change.
