# Notes: Agent B (Q4–Q7), 2026-11-15

**Standing conventions**
- Breadth = share of start-of-window nominal weight whose annualized rate is > 3%, using the weighted leaf method (149 core leaves).
- Engine: `09_slide1_research/code/C_common.py`, imported read-only.
- Oct 2026 = UMD estimate ("est."). BEA U20404/U20405 vintage 2026-11-10, SA.
- All scripts run from the project root with `python3 -I`, in this order:
  1. `B_q4_breadth_by_measure.py`
  2. `B_q6_waller.py`
  3. `B_q7_fetch_bls.py` (network)
  4. `B_q7_hospital.py`
  5. `B_q5_sticky_flexible.py`

## Q4: breadth by measure
- **New scope:** core_goods = core leaves with line < 150 (65 leaves). It is built from `SCOPES['core']`; no new rate or weight code.
- **Checks:** 40 of 40 pass (`outputs/B_q4_checks.csv`).
  - The four binding numbers match to within 0.01.
  - Every C_breadth primary and robustness row matches to within 0.0006.
  - The Waller weighted rows match.
  - The core monthly series (leaf and sub-line, 3m and 12m) matches C_breadth_ts to within 0.001.
- **Supercore 12m leaf, re-derived:** 68.984 → 54.477. Confirmed.
- **Hospital attribution** (`B_q4_hospital_attribution.csv`): the leaves 184–186 drop more than fully explains each 12m fall.

  | Measure | Change | Hospitals | Ex-hospital change |
  |---|---|---|---|
  | Core | −6.59 | −8.72 | +2.38 |
  | Supercore | −14.51 | −15.12 | +0.79 |
  | Core services | −11.08 | −11.54 | +0.58 |

  The 3m changes are unaffected: the hospital 3m rate was below 3% in both months.
- **3m series are noisy.**
  - Core 3m leaf runs 66.5 (May 26), 56.1, 61.4, 32.8 (Aug), 44.8, 45.5 est.
  - The cause is OER (leaf 162, about 13% of core weight) sitting at the 3% line: its 3m rate went 4.51, 4.34, 3.22, 2.80, 3.22, 3.43.
  - Rent (156) fell below 3% on a 3m basis from Aug 2026: 2.34, 2.74, 2.52.

## Q5: sticky vs flexible
- **Classification file:** the Atlanta Fed xlsx has no component list.
  - Used Bryan & Meyer (2010) Table 1 (45 groups; sticky = price changes less often than every 4.3 months).
  - Assumption: today's Atlanta Fed basket uses this same grouping. **Unverified.** The Atlanta page shows the table only as an image.
- **Stratum → group mapping:** done by ELI code prefix; it is in the code dictionary `BM`.
  - TA090 ("unsampled new and used motor vehicles") has no single group and is excluded from class votes.
  - Lodging away from home (HB, which includes housing at school) is flexible, as in Table 1.
- **PCE mapping chain:**
  - Concordance PCE code DxxxRC → U20404 code DxxxRG → BEA line.
  - DTSPRC is set by hand to line 156.
  - Codes that point to an aggregate line are expanded to that line's leaf descendants, but only for leaves with no direct ELI link.
  - Concordance quirk: HM090 "unsampled tools, hardware…" maps to DTSPRC, tenant-occupied homes. It is kept as BLS published it; both are sticky, so the class is unchanged.
- **CPI-only source rule:**
  - A leaf is CPI-priced if every pricing line has source_tag CPI, or is a blend whose BEA text names only CPIs.
  - CPI-only blends: lines 87, 95, 285 cellular, 328 domestic services.
  - Leaves 50, 176, 258, 275 have mixed CPI and PPI sources and are left out.
- **Coverage of core weight** (Sep 2025 shares):

  | Rule | Sticky | Flexible | Unclassified |
  |---|---|---|---|
  | Primary (mixed leaves left out) | 94 leaves, 52.12% | 17 leaves, 9.14% | 38 leaves, 38.74% |
  | Alternative (majority by ELI count) | 95 leaves, 52.61% | 19 leaves, 10.06% | 35 leaves, 37.32% |

  - 3 leaves are mixed: 70 luggage (3 sticky / 4 flexible ELIs), 112 shoes (1/4), 212 amusement parks (2/1). The majority rule decides all three.
  - The 35 leaves left out by source are mostly health care (hospitals, physicians, paramedical, nursing homes), NPISH, financial services, insurance, air transport and software.
  - 4 CPI-priced leaves have no concordance ELI: casino gambling, child care, lotteries, food supplied to civilians.
- **Flexible set is small and goods-heavy:** 17 leaves (new and used vehicles, parts, apparel, jewelry, tobacco, vehicle leasing and rental, hotels, housing at school). 3m results are noisy (48.65 → 37.01).
- **Atlanta-style CPI basket check:**
  - My RI-weighted mean rates are close to the Atlanta Fed published aggregates for Sep:
    - sticky 12m 2.68 vs 2.82
    - core flexible 12m 1.42 vs 1.48
    - sticky 3m 3.39 vs 3.33
  - Oct 12m is only approximate (interpolated base). Sticky 3.38 vs Atlanta 3.09: the approximation, or the 4 sticky items missing in the Oct file, shifts it.
  - The Oct file has fewer sticky items (87 vs 91; RI covered 66.5 vs 69.5). Five items have a Sep 12m rate but an N/A Oct 12m rate; the pipeline notes a missing index observation or RI update:
    - **Motor vehicle insurance (SETE, RI about 2.5)**
    - gardening and lawncare
    - motor vehicle body work
    - photographers
    - fees for lessons
  - Oct 12m sticky basket breadth therefore excludes motor vehicle insurance.

## Q6: Waller
- Oct est. rows are already in `C_waller_variants.csv`: confirmed.
- All rows recompute through the engine to within 0.0006.
- Only the weighted core-services variants exceed 70 in Sep: leaf start-of-window 70.815 and leaf latest-share 71.075.
- **Label caveat:** for October, slide 1's "latest shares (Sep 2026)" variant uses Sep 2026 shares, not Oct.

## Q7: hospital
- See `outputs/B_q7_hospital.md`. Measured, not imputed.
- Oct 2025 PPI first released 2026-01-14 (+1.42% NSA first print; +1.41% current vintage).
- The Medicare inpatient component rose +5.96% in Oct 2025.

## Cross-checks
- **Waller, Nov 10:** "more than 70 percent … in September" matches only our weighted core-services leaf basis (70.8 start-of-window, 71.1 Sep shares). Count bases give 58.6–64.9.
  - On our Oct est., the weighted leaf share falls to 59.7. That fall comes entirely from the hospitals base effect.
  - Waller's actual basis is not stated.
- **Daly (reported via Kitco [2], no primary text):** services ex-housing "not moving in the correct direction."
  - Supercore 12m breadth is 68.98 in Sep, 43 pp above its 2018–19 average (25.9).
  - Supercore 3m was 39.8 Sep and 38.7 Oct est., below most of 2026 (peak 69.5 in May).
  - Supercore ex-hospitals 12m rises +0.79 Sep → Oct est.
  - The 12m level agrees with Daly; the 3m direction is mixed.
- **Previous finalists** (md and PDF transcripts 2023–25): no inflation breadth or sticky/flexible breadth found. Only supercore levels (2024 winner) and payroll diffusion (2025 UCLA).
