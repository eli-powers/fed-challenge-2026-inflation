Status: Audited — converged R3 (Codex, Nov 15, 2026)

# Agent A report: tags and attribution (Q1–Q3), Nov 15, 2026
Agent: Sonnet 5.5, brief `brief_A.md`. Outputs `outputs/A_*`, scripts `code/A_*.py`, notes `notes_A.md`, sources `sources_A.md`, paywalled `outputs/A_paywalled.csv`.

**Pre-checks passed:** slide 1 reproduction (core leaf 12m 60.626 / 54.038; 3m 44.814 / 45.467); 149 core leaves map one-to-one to `proposed_tags.csv`; counts and weights reproduce `tag_summary.csv` (4/30/42/73; AI 2.04%, tariff 11.11%, energy 18.26%, untagged 68.60%); re-applying `tag_rules.py` reproduces `tag_final` with zero differences.

## Findings

### Q1. Tags
**1. Tariff exemption** (`outputs/A_q1_tariff_exemption.md`; sources in `03_Data/Raw/tariff_exemption_2026-11-15/`).
- Presidential memorandum, Apr 11, 2025 (DCPD202500470) [O]: the term "semiconductors" in E.O. 14257 "includes the products classified in the following headings": 8471, 847330, 8486, 85171300, 85176200, 85235100, 8524, 85285200, 8541.x, 8542. Effective Apr 5, 2025, with refunds. The memo does not say "computers" or "smartphones"; the HTS headings do (8471 data-processing machines; 8517.13 smartphones).
- Supreme Court, Feb 20, 2026, *Learning Resources v. Trump* (No. 24-1287): "IEEPA does not authorize the President to impose tariffs" [O syllabus]. The reciprocal tariffs no longer exist.
  - Successor 1: Section 122 surcharge, 10%, Feb 24–Jul 24, 2026 (Proclamation 11012); exemption list (9903.03.03) includes 8471.xx, 8517.13.00, 8542 [O, FR public-inspection PDF 2026-03824].
  - Successor 2: Section 301 "forced-labor" tariffs, 10% or 12.5%, from Jul 24, 2026 (FR 2026-15181, published Jul 28); exemption list (9903.05.86) includes 8471.30.01–8471.90.00, 8517.13.00, 8542.31–8542.90 [O].
- Section 232 semiconductors (Proclamation 11002, Jan 14, 2026): 25% on a "very narrow category"; carves out "non-data center consumer applications". Phase two only recommended; not confirmed imposed as of Nov 15 [S, unverified].
- Latest date confirmed: Section 301 notice in force from Jul 24, 2026; later amendments not checked.
- Consequence: PCs and phones (import shares 57%, 37%) were never charged the reciprocal duty. The AI+tariff overlap flag on leaves 49, 51, 71 reflects import share, not an applied tariff. AI-before-tariff priority is consistent.

**2. Energy spot-check** (`outputs/A_q1_energy_spotcheck.csv`). Energy shares recomputed for all 149 leaves (11 flagged) with different algebra but the same documented design (bridge mapping, margins, energy block). Max abs. difference 4.9e-06; weighted p75 cutoff 0.03468 in both; no leaf changes side. Verifies arithmetic and data handling, not the design.

| Leaf | Item | Energy share | Note |
|---|---|---|---|
| 241 | Other purchased meals | 0.0453 | largest by weight, 5.74% of core |
| 187 | Nursing homes | 0.03469 | +0.001 pp over cutoff |
| 207 | Air transportation | 0.1127 | |
| 245 | Alcohol in meals | 0.0385 | |
| 250 | Hotels | 0.0468 | |
| 167 | Water/sewage | 0.0606 | |
| 211 | Membership clubs | 0.0569 | |
| 26 | Lighting | 0.0353 | just above |
| 309 | Hairdressing | 0.0338 | just below |
| 125 | Other medical products | 0.0339 | just below |
| 228 | Lotteries | 0.0609 | untagged by override |

**3. Proposals** (`outputs/A_q1_tag_proposals.csv`, support `A_q1_tag_robustness.csv`; `tag_final` unchanged).
- One proposal: leaf 187 nursing homes (1.46% of core) energy → untagged: +0.001 pp over the cutoff, and the only energy leaf that drops out under the before-redefinitions measure (41 of 42 stay).
- Flags, no change: restaurants (241) is 31% of the energy group (group 12.5% of core without it); software (50) is 88% of the AI group's 12m contribution; drugs untagged per Eli; autos' Section 232 not verified; lotteries override "mapping artifact" claim not verified.

### Q2. Bowman-style attribution (`outputs/A_q2_attribution.csv`, `A_q2_leaf_contrib.csv`, `A_q2_bowman_quote.md`)
- C_g = Σ_g (start-of-window weight share × leaf annualized rate), no cutoff. Method (a) above-target = C_g − share_g × 2.
- Reconciliation, leaf-sum S vs published/est. R: 12m Sep 3.184 vs 3.121 (−0.063); 12m Oct 3.304 vs 3.242 (−0.061); 3m Sep 3.171 vs 2.903 (−0.268); 3m Oct 3.749 vs 3.551 (−0.198). 3m residual mostly annualization convexity (`C_sum_gap`). An `a_scaled` method spreads the residual pro rata.
- Shares of above-target, 12m (energy / tariff / AI / untagged; Sep weights 18.1 / 11.1 / 2.0 / 68.9%):

| Method | Sep | Oct est. |
|---|---|---|
| a, central | 29.2 / −0.1 / 18.0 / 52.9 | 31.9 / 5.1 / 15.1 / 47.8 |
| b, excess over 2% only | 23.0 / 7.9 / 13.0 / 56.1 | 24.2 / 9.8 / 11.9 / 54.1 |
| c, 2% charged to untagged | 59.8 / 18.6 / 21.3 / 0.4 | 59.7 / 22.1 / 18.1 / 0.1 |

  Total above-target: (a),(c) 1.184 Sep / 1.304 Oct; (b) 1.851 / 1.893.
- 3m ann., method a: Sep 40.5 / −10.1 / 15.7 / 53.9; Oct est. 46.8 / 2.2 / −1.2 / 52.1.
- Group 12m rates, Sep: energy 3.92%, tariff 1.99%, AI ~12.5%.
- Bowman (Nov 10 CFR speech, "Inflation", 2nd paragraph): "Tariffs, energy, and AI-related price pressures each accounted for roughly one-fourth of above-target core PCE inflation over the 12 months ending in September. The remaining one-fourth likely reflects persistent effects from the inflationary shocks in recent years." Five footnotes; none gives a method. Her fourth piece is a cause, not a set of items; untagged is only the nearest analogue (an assumption). Untagged carries ~50% under (a) and (b) vs her 25%.

### Q3. Tagged vs untagged breadth (`outputs/A_q3_*`)
Within-group breadth (% of group weight >3%), contribution to all-core breadth (pp) in brackets:

| Group | 12m Sep | 12m Oct est. | 3m Sep | 3m Oct est. |
|---|---|---|---|---|
| Energy | 67.0 (12.1) | 73.3 (13.3) | 61.9 (11.2) | 69.0 (12.5) |
| Tariff | 29.1 (3.2) | 38.5 (4.3) | 31.3 (3.5) | 42.3 (4.7) |
| AI | 90.0 (1.8) | 90.0 (1.8) | 28.4 (0.6) | 28.4 (0.6) |
| Untagged | 63.2 (43.6) | 50.5 (34.8) | 43.0 (29.6) | 40.3 (27.7) |
| All core | 60.6 | 54.0 | 44.8 | 45.5 |

- Untagged ex hospital leaves, 12m: 57.9 Sep, 57.8 Oct est.
- Time series 2018-01 to 2026-10 (`A_q3_tagged_breadth_ts.csv`); core matches `C_breadth_ts.csv`. 2018–19 averages, within-group 12m: core 35.2, energy 33.7, tariff 6.2, AI 0.0, untagged 41.1; 3m: 39.2, 38.2, 22.7, 9.5, 42.8.
- Sensitivities (`A_q3_sensitivity.csv`, 12m Sep): strict 5%: 16 energy leaves, 3.5% weight, breadth 59.2%; transport, same top-quartile rule on transport-inclusive measure: 35 leaves, 15.1%, 69.7%; transport flag replacing the energy rule: 19, 4.4%, 47.5%; flag unioned with final: identical to final. Method-a energy share of above-target (12m Sep): 15.7% (strict 5%), 28.8% (transport quartile).
- Oct 12m breadth change −6.588 pp (`A_q3_oct12m_drop_by_tag.csv`): untagged −8.801, energy +1.163, tariff +1.044, AI +0.006. Rate crossings −6.705, weight shift +0.117. Hospital leaves 184–186 (untagged, asserted) −8.721 (flip −8.780, weight +0.059). Untagged ex hospitals −0.080. Crossings: 5 leaves down, 8 up.

## Slide-worthiness (agent)
| Exhibit | Rating | Why |
|---|---|---|
| Bowman-style attribution | 3/5 | Answers a Governor's framing, but method choice moves energy from 23% to 60%; her method undisclosed; tariff ~0 under (a); untagged ~50% not 25%; 3m residual large. Robust only as "untagged is the largest share under (a) and (b)". |
| Tagged vs untagged breadth | 3/5 | Oct 12m drop entirely untagged via hospitals; ex hospitals untagged flat (57.9→57.8) while energy rises 67→73 and tariff 29→39. But energy vs untagged-ex-hospital gap only 9–15 pp; tagged breadth already high pre-2026; AI is effectively one leaf. |

## Worth a look (agent)
1. Tariff group's 12m rate is 1.99% (Sep), not above target. New light trucks (1.9% weight) at 0.5%; ex that leaf 2.32%. Bowman gives tariffs a quarter.
2. AI group ≈ software (leaf 50): 12m 18.5% Sep / 16.1% Oct est., but 3m ann. +0.4% Sep / −9.1% Oct est. Phones −12.7% 12m. How BEA prices software is worth checking.
3. Untagged 12m breadth 63–64% and energy 72% already in Sep 2025; energy-tagged >63% every month Feb–Oct 2026.
4. Reciprocal tariffs struck down Feb 20, 2026; replaced by Section 122 then Section 301. The tariff tag is by import share, not applied tariff. Possible Q&A line.
5. Bowman's 3.3% Oct core vs our 3.24%.
6. Cross-checks: consistent in direction with Waller's ">70%" and Daly's "spread into services". Goolsbee's "services not oil-driven" is reported, not primary. 2025 finalists have no attribution-by-shock exhibit (keyword search only).

## Spot-check examples (agent)
1. `A_q2_attribution.csv`: `2026-09, 12m, a, energy` share 0.2924; `tariff` −0.0008.
2. `A_q3_oct12m_drop_by_tag.csv`: `hospital leaves 184-186 (sum)` −8.721; `untagged` −8.801.
3. `A_q1_energy_spotcheck.csv`: leaf 187 0.03469 vs 0.034689.
4. `DCPD-202500470.pdf` pp. 1–2 HTS list; `FR_2026-15181_public_inspection.pdf` p. 84.
5. `A_q3_sensitivity.csv`: strict 5% rows.

## What to verify (agent)
Energy design not re-argued; Section 232 phase two, pharma schedule and CBP CSMS 64724565 not opened [S]; post-Jul 28 Section 301 amendments not checked; SCOTUS vote count secondary; Section 122 15% increase announced but no proclamation found; leaves 49/71 → HTS mapping from descriptions, not a concordance; 3m method-a shares rest on S exceeding published by 0.2–0.27 pp.

## Coordinator review
**Verified (independent script, scratchpad `vA.py`, through `C_common` + `proposed_tags.csv`):**
- Leaf mapping (all 149 core leaves) and the four reproduction checks.
- Within-group breadth, all 16 cells of the Q3 table: match to 0.1 (Oct 12m untagged 50.4 in my run vs 50.5 reported: rounding at 50.45; not material).
- Method-a attribution shares, 12m and 3m, Sep and Oct: all match to 0.1. Leaf-sums S 3.184 / 3.303(4) / 3.171 / 3.749 match.
- Oct 12m drop by tag: untagged −8.801, energy +1.163; hospital −8.721 and all three hospital leaves tagged untagged.
- Bowman quote: exact, from `textutil` extraction of the saved RTF.
- Tariff sources: opened the saved PDFs with pypdf. DCPD-202500470 contains "That term's meaning includes the products classified in the following headings… 8471 • 847330 • 8486 • 85171300…"; FR 2026-03824 and 2026-15181 both list 8471.30.01 and 8517.13.00; the SCOTUS PDF contains "alleging that IEEPA does not authorize the reciprocal… tariffs" (syllabus holding text located by agent; I confirmed the file is the opinion).
**Corrected:** nothing.
**Could not check:** Section 232 phase two status; CBP CSMS; the I-O design itself.
**Worth a look (coordinator):** Method (c) puts ~0% on untagged, (a) ~50%: the "Bowman quarter-each" comparison is essentially an artefact of how the 2% is allocated. No method reproduces a quarter each. Tariff group 12m rate 1.99% means under (a) tariffs contribute nothing above target in Sep, which conflicts with Bowman's quarter.
**Interpretive notes (not for Eli unless asked):** the cleanest slide statement from A is the tag decomposition of the Oct 12m drop (all of it untagged hospitals; ex hospitals untagged flat). The attribution is fragile and better as Q&A backup.
