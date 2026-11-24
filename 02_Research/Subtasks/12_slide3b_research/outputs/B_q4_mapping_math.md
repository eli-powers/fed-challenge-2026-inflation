# Oil gap to core PCE: equation, response function, mapping (Agent B, 2026-11-15)

Scripts: `code/B_q4_response.py`, `code/B_q4_identification.py`, function `map_gap_to_core` in `code/B_common.py`.
Source: De Michelis, Orak, Pradhan & Queralto, "The Effect of Oil Prices on Core Inflation: Recent Evidence from the Advanced Economies," FEDS Notes, 2026-11-09 (doi 10.17016/2380-7172.4190). I read both the main HTML [O] and the accessible version saved 2026-11-15 [O].

## 1. The estimated equation (extracted from the MathJax in the main HTML) [O]
Full specification:

π_{i,t} = α_i + γ1 π_{i,t−1} + γ2 π_{i,t−2} + η1 π_{i,t−1} D_t^post + η2 π_{i,t−2} D_t^post + λ x_{i,t} + β s_t + Σ_{j=0}^{4} δ_j o_{i,t−j} + Σ_{j=0}^{4} ζ_j o_{i,t−j} D_t^post + ε_{i,t}

Definitions, quoted from the note:
- π_{i,t}: "core inflation in economy i in quarter t".
- x: "the output gap".
- s: "a measure of supply-chain disruptions" (the GSCPI).
- o: "relative oil-price inflation".
- D^post: "equals one from 2021:Q1 onward".

Units and measurement:
- Quote: "oil inflation is measured from quarterly Brent prices in local currency and enters the model relative to core inflation." So o_t = oil inflation_t − π_t.
- Core is "core PCE prices for the U.S. and core CPI prices for the other economies". The sample is 2000:Q1–2026:Q2, a panel of five economies with country fixed effects.
- **Not stated in the note (unverified):** whether inflation is annualized and whether it is a log difference.
  - Annualization doesn't matter for the mapping. π and o enter in the same units, so γ, η, δ, ζ are invariant to a common ×4 rescaling. The level response per 10% oil rise is the same either way.
  - The level response in Fig. 2 is reported in % of the core price level.
- Coefficient units: the note says the "point estimates in Table 2 … are for one-unit changes". It also says "a 10-percentage point increase in relative oil-price inflation raised core inflation by only about … 0.01 percentage point" (pre) and by "0.14 percentage point" (post).

Table 2 [O], already verified in slide 2's `C_q10_oil_note_verification.csv`:

| term | value |
|---|---|
| persistence, pre | 0.347 |
| increase in persistence, post | +0.298 (total ≈ 0.645) |
| pass-through, pre | 0.001, CI −0.002 to 0.004 |
| increase in pass-through, post | +0.013 (total 0.014) |

- **Individual lag coefficients are not reported** (only sums).

## 2. Response function R_k: from the note's own data table
- The accessible version's **Figure 2 table** gives the cumulative core price-level response, in %, to a permanent 10% oil rise for k = 0…12 quarters, for all three lines.
- Provenance: **table**, from the note's figure data.
- Saved to `B_q4_response.csv` (provenance=table), with the column headings quoted exactly.

| k | pre | persistence only | post (full) |
|---|---|---|---|
| 0 | 0.0196 | 0.0188 | 0.0184 |
| 1 | 0.0257 | 0.0265 | 0.0105 |
| 2 | 0.0301 | 0.0376 | 0.0644 |
| 3 | 0.0226 | 0.0388 | 0.0896 |
| 4 | 0.0323 | 0.0566 | 0.1850 |
| 5 | 0.0339 | 0.0634 | 0.2269 |
| 6 | 0.0374 | 0.0712 | 0.2690 |
| 8 | 0.0409 | 0.0801 | 0.3179 |
| 12 | 0.0444 | 0.0884 | 0.3604 |

Notes:
- The text's "0.05", "just under 0.1" and "0.35" are rounded. The post line reads 0.354 at k=11 and 0.360 at k=12, so "12 quarters" may count the impact quarter as quarter 1. The difference is small.
- **The paths are not monotone.**
  - Post falls at k=1 (0.018 → 0.011). The implied lag-1 coefficient is negative.
  - Pre falls at k=3.
  - The post response is **back-loaded**: k=0–3 adds only 0.09, while k=4 jumps by +0.095 (a large implied lag-4 coefficient).
- The note's footnote on Fig. 2: "All exogenous variables are held fixed; the response reflects only oil price pass-through and the intrinsic persistence of core inflation." So the relative-to-core feedback is inside the line.

### 2b. Reconstruction test from the Table 2 sums (provenance=reconstruction; for comparison only)
- Method: simulate π_k = γ1π_{k−1} + γ2π_{k−2} + Σ δ_j(o_{k−j} − π_{k−j}) for a 10-log-point oil step at k=0, under 9 splits (3 γ splits × 3 δ splits). Results: `B_q4_reconstruction_tests.csv`.
- **Post:** reproduces the table well. R12 = 0.366–0.378 vs 0.360, an error of **+1.5% to +5.0%**. The best split, equal γ and equal δ, has an RMSE of 0.036 over k=0–12. Because no split reproduces the k=1 dip, the reconstruction **cannot** stand in for the table's quarter-by-quarter shape.
- **Pre and persistence-only: they do NOT reproduce the table.**
  - The Table-2 sums imply a long-run level effect of 0.015 (pre) and 0.028 (persistence-only), against the table's 0.044 and 0.088. That is about **−66% to −69% at k=12 under every split**.
  - Identification check (`B_q4_identification.csv`): fix γ1+γ2 at the Table-2 value and fit δ freely. The published lines then need a pass-through sum of about **0.0025 (pre)** and **0.0032 (persistence-only)**, against the 0.001 in Table 2. The fit RMSE is 0.003 and 0.0005.
  - The post line needs 0.0135, close to Table 2's 0.014.
  - The unconstrained 7-coefficient fit is ill-conditioned (condition number 160–1000), so I don't report its individual lags as estimates.
  - One possible explanation, my inference and **unverified**: the black and red lines come from the restricted specifications (1) and (2), estimated separately, rather than from the full model's pre-pandemic coefficients.
- **Decision:** use the **table** R_k. The forecast script should cite it as "FEDS note Fig. 2 data". No interpolation was needed.

## 3. Mapping a gap path to core
- Let g_s be the oil gap in quarter s, in log points ×100 (100·ln P_scen/P_assumed), with g = 0 before 2026Q3. Let Δg_s = g_s − g_{s−1}.
- The model is linear, so any path is a sum of permanent steps:

  **L_t = Σ_{s≤t} R_{t−s} · Δg_s / 10**  (core price-level adjustment, % / log points)

- Adjustment to quarterly annualized core inflation:
  - approximate: **a_t ≈ 4·(L_t − L_{t−1})** (pp);
  - exact compounding: a_t = 100·[exp((L_t − L_{t−1})/100)^4 − 1].
- Q4/Q4 adjustment ≈ **L_{2027Q4} − L_{2026Q4}** for 2027, and L_{2026Q4} for 2026.
- **Horizon:** the gap starts at 2026Q3, so 2027Q4 is k=5, inside the published range (k≤12). No extrapolation is needed. Beyond k=12, `map_gap_to_core` holds R flat, which is an assumption.
- **Exact vs approximate:** at most 0.008 pp apart, in P2 post 2027Q4 (1.301 vs 1.293). Negligible.
- **Check against a direct simulation** (`B_q4_mapping_checks.csv`). Using the 7 coefficients fitted to each table line:
  - superposition and direct simulation agree to machine precision;
  - superposition on the table R_k vs the direct simulation differs by at most 0.00008 pp of level.
- **Relative-to-core feedback:** a higher core path lowers o, which is negative feedback. Removing it changes L by at most 0.0036 pp (P2, post) because δ sums to ≤0.014. **It doesn't matter for the mapping**, and it is already embedded in the table R_k.
- **Shock size convention:** if the "10 percent" in Fig. 2 is a simple 10% rise (9.53 log points) rather than 10 log points, all mapped effects scale up by **×1.049**. The note doesn't say which (unverified).

## 4. Worked example (`B_q4_worked_example.csv`; gaps provisional vs the Aug-2026 STEO)

**P2 ($110 flat)**
- Gap: 12.2, 37.2, 39.6, 43.8, 48.1, 52.6 log points (2026Q3–2027Q4). Δg = 12.2, 25.0, 2.4, 4.1, 4.3, 4.5.
- 2027Q4, post: L = (R5·12.18 + R4·25.02 + R3·2.44 + R2·4.14 + R1·4.32 + R0·4.51)/10 = (0.2269·12.18 + 0.1850·25.02 + 0.0896·2.44 + 0.0644·4.14 + 0.0105·4.32 + 0.0184·4.51)/10 = **0.801**.

| regime | L 2026Q4 | L 2027Q4 | Q4/Q4 2027 adj. | qa adj. 2027Q1..Q4 (pp) |
|---|---|---|---|---|
| pre | 0.080 | 0.160 | **+0.08 pp** | 0.10, 0.05, 0.02, 0.15 |
| persistence only | 0.079 | 0.264 | +0.18 pp | 0.15, 0.16, 0.16, 0.28 |
| post | 0.059 | 0.801 | **+0.74 pp** | 0.20, 0.69, 0.79, 1.30 |

**Other paths, Q4/Q4 2027 adjustment (pre / persistence only / post), pp:**
- P1 Nov STEO: **−0.00 / +0.07 / +0.51**
- P3 +$25: **+0.02 / +0.05 / +0.31**
- 2026 Q4/Q4 adjustments are small in every case: 0.03–0.08 pp.

**Caution on quarterly profiles.** The large implied lag-4 coefficient makes the quarterly annualized adjustments lumpy. For example, P1 post 2027Q4 is +0.85 pp because 2027Q4 is four quarters after the 2026Q4 gap jump. Q4/Q4 numbers are more robust to that lag-shape detail.

## 5. Caveats that apply (from the note)
- A five-economy panel average (Canada, euro area, Japan, U.K., U.S.), **not the US**.
- Footnote 4: the pass-through rise is significant in Canada, Japan and the U.S., not significant in the euro area or U.K.
- The authors "view these paths … as an upper bound on the likely impact rather than a central prediction".
- **Reduced form:** "cannot distinguish a structural change in the underlying inflation process from the possibility that global supply shocks have become more frequent, more persistent, or both". It uses actual oil-price changes, not identified supply shocks (fn. 2), and the post-pandemic terms "may partly reflect the co-movement of oil prices with broader global demand pressures".
- **Short post-pandemic sample:** 2021Q1–2026Q2 = 22 quarters.
- "even if our results stem from a structural change … we cannot say whether this change will endure or reverse."
- Don't describe the note as evidence of changed price-setting behaviour.
- "do not represent any official forecasts".
