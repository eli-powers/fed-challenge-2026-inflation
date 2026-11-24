Status: Audited — converged R2

# Report B: core CPI–PCE gap decomposition (R3)

## Findings
**Headline result: CPI's heavier shelter weight does not explain why core PCE runs above core CPI; it pushes the other way.** Two attribution conventions with the same total: **BEA-style convention** (UMD decomposition; convention inferred from Table 9.1U values and partially cross-checked on headline; `pp`) and **centred** (each item measured against the matched-set mean; `pp_centered_alt`).

**1. Sep 2026 core, 12m (`outputs/B_core_gap_sep.csv`)**: core PCE 3.1212% (U20404 line 374, SA) − core CPI 2.5644% (CUUR0000SA0L1E, NSA) = **+0.557 pp**.

| Effect | BEA convention | Centred |
|---|---|---|
| Formula (chained Fisher vs fixed weight) | −0.030 | −0.030 |
| Weight | −0.283 | +0.903 |
| Price | +0.049 | +0.077 |
| Scope, PCE-only | +0.942 | −0.304 |
| Scope, CPI-only | −0.023 | +0.009 |
| CPI Jan-2026 reweighting | −0.001 | −0.001 |
| Residual (CPI replication) | −0.096 | −0.096 |

Largest items (BEA / centred): shelter weight −0.797 / −0.105 (OER −0.628 / −0.095; CPI share 32.8% vs PCE 13.5%); software +0.21 / +0.29 (PCE share 1.20% vs CPI 0.03%; CPI +28.4% vs PCE +18.5%); motor vehicle insurance +0.18 / +0.24 (CPI −4.98% vs PCE +0.30%); health insurance price +0.21 / +0.33, weight+price +0.18 / +0.21 (CPI −8.99% vs PCE +6.98%); PCE-only: hospital third-party +0.24 / −0.01, restaurant meals (core PCE only) +0.21 / 0.00, portfolio management +0.15 / +0.08, imputed financial services +0.09 / −0.02, Rx third-party −0.11 / −0.20.

**2. Oct 2026 core (`B_core_gap_oct.csv`)**: primary = approx. 12m, our core PCE est. 3.2425% − core CPI 2.8149% (Oct 2025 CPI base interpolated √(Sep×Nov), matches workbook) = **+0.428**; weight −0.302 / +1.016; PCE-only +0.946 / −0.372; shelter −0.837 / −0.082; residual −0.116. Chosen for same horizon as Sep and the slide; weakness = unpublished CPI base. Alternate 3m ann. SA Jul→Oct: 3.551 vs 3.746 = **−0.196**.

**3. Headline check vs Table 9.1U (`B_headline_check.csv`)**: 9.1U lacks Oct/Nov 2025, so method run monthly Dec 2025–Sep 2026 (SA, prior-month weights), effects summed. BEA vs ours: shelter weight −0.52 / −0.526; OER −0.40 / −0.405; tenant rent −0.11 / −0.104; total weight −0.48 / −0.508; imputed fin. services +0.08 / +0.077; NPISH +0.04 / +0.048; other PCE-only +0.21 / +0.214; airfares price −0.07 / −0.078; formula −0.08 / −0.056; total PCE-only scope +0.63 / +0.518; gasoline weight −0.35 / −0.425; foreign travel +0.06 / −0.007; CPI-only scope −0.13 / −0.021. Gap implied by BEA effect lines −0.14 vs our exact −0.166.

**4. Spoken-line candidates (data only; `B_theme_summary.csv`)**
- A (centred): "Core PCE runs about half a point above core CPI. Shelter's heavier CPI weight actually pulls the other way, by about 0.1 point. The gap comes from software, which PCE weights about 40 times more (+0.3); car insurance, whose CPI price fell about 5% (+0.25); and health insurance, which CPI measures falling 9% (+0.2)."
- B (BEA convention): "Shelter's double weight in CPI subtracts about 0.8 point… PCE also covers things CPI doesn't: third-party-paid medical care (+0.36), financial services like portfolio management (+0.30), and restaurant meals that core CPI leaves out (+0.21). Together those PCE-only items add about 0.9 point."
- C (short): "On a BEA-style reconciliation (our decomposition), the half-point gap is roughly +0.9 from items only PCE covers, minus 0.8 from CPI's heavier shelter weight, with insurance and software pricing netting most of the rest."

## Worth a look (agent)
1. Shelter has the wrong sign to explain the gap (negative in both conventions).
2. The two conventions tell different stories (BEA's embeds a normalisation: PCE-only items ≈ 36% of core PCE).
3. Insurance measurement gaps are large (CPI health insurance −9.0% vs PCE +7.0%; car insurance −5.0% vs +0.3%).
4. Oct gap flips sign by horizon (+0.43 approx. 12m; −0.20 3m ann.).
5. Residual ≈ 17% of Sep gap (−0.096); 5.8% of core CPI weight imputed.
6. 9.1U rounded line totals (−0.40) shouldn't be quoted as the gap.
7. BEA's CPI-only physician/hospital split and scope shares unpublished; medical third-party split assumed (PCE in-scope share = 0.648 × CPI share); no-split sensitivity: weight +0.28, price −0.16, PCE-only +0.58.
8. No official discusses the gap; no 2025 finalist reconciles CPI and PCE.

## Spot-check examples (agent)
1. Core CPI 330.804 → 339.287 = 2.564%. 2. OER CPI 431.246 → 445.310 and PCE line 162 141.309 → 145.917, both +3.261%; (13.54% − 32.80%) × 3.26 = −0.628. 3. Health insurance CPI SEME 149.597 → 136.151 (−8.99%), PCE line 276 130.045 → 139.124 (+6.98%). 4. Software CPI SEEE02 21.991 → 28.234 (+28.39%), PCE line 50 71.974 → 85.277 (+18.48%). 5. 9.1U line 14 Dec 2025–Sep 2026 sum −0.52.

## What to verify (agent)
BEA convention inferred from 9.1U values (no BEA doc); mapping judgments in `code/B_mapping.py` (medical factor 0.648; vehicle fees and lawn care CPI-only; core CPI as proxy for unpublished household-operations items); Oct interpolated CPI base; foreign travel set to core m/m in Oct; gasoline (−0.425 vs −0.35) and foreign-travel (−0.007 vs +0.06) differences vs BEA.

## Coordinator review
**Verified independently** (`scratchpad/verify_B.py`, straight from BLS API JSON batch1–7 Nov 10 and BEA U20404/U90100 JSON):
- Core CPI CUUR0000SA0L1E 330.804 → 339.287 = 2.564% ✓; core PCE line 374 126.940 → 130.902 = 3.121% ✓; gap 0.557 ✓.
- OER CPI SEHC01 431.246 → 445.310 = 3.261% ✓; PCE line 162 141.309 → 145.917 = 3.261% ✓.
- Health insurance CPI SEME −8.988% ✓; PCE line 276 ("Medical care and hospitalization" = health insurance) +6.981% ✓.
- Software CPI SEEE02 +28.389% ✓; PCE line 50 +18.483% ✓. Motor vehicle insurance CPI SETE −4.983% ✓.
- 9.1U line 14 ("Rent of shelter"): 10 monthly values Dec 2025–Sep 2026 sum to −0.52 ✓.
- `B_core_gap_sep.csv` check row: sum of all effect rows incl. residual = 0.5568 = gap ✓.

**Corrected**: none. Clarification: the agent's "+0.21 / +0.33" for health insurance is the *price* effect alone; the theme file gives health insurance *weight and price* +0.181 / +0.208. The workbook uses the theme file and labels it "weight and price".

**Premise note (recorded per GO "Disagreements")**: the roadmap and STATE.md frame shelter weight as a candidate driver of the *gap*. The data say shelter weight lowers PCE relative to CPI. Not a disagreement with the brief (which only listed candidates), but the spoken line must not say shelter explains PCE > CPI.

**Judgment for Eli**: which convention (BEA vs centred) the spoken line uses; they rank drivers differently. Logged in Judgment calls for Eli.

**Could not check**: the 9.1U convention against BEA documentation (none found by the agent); mapping judgments (Codex ask).

**Coordinator Worth a look**: our headline method misses BEA on gasoline weight by −0.07 and CPI-only scope by +0.11; the core version excludes energy, but CPI-only scope matters for core too, so the core CPI-only line (−0.023) may be understated.

**Interpretive notes (not shared unless asked)**: the most defensible one-liner is convention-neutral: the gap is "items and prices PCE measures differently (insurance, software, PCE-only medical and financial services) outweighing CPI's heavier shelter weight".

**Post-audit (Codex R1-F03, accepted):** "validated vs BEA" overstated it. The convention is inferred from 9.1U values; the headline run matches shelter, imputed financial services, NPISH and airfares but not gasoline, foreign travel or CPI-only scope. The weight/price/scope allocation depends on the assumed medical split (0.648); without it, Sep BEA-style weight +0.280, price −0.156, PCE-only +0.584 (total unchanged). Option C reworded.
