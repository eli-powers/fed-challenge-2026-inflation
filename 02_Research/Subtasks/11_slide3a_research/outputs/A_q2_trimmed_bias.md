# Q2. Dallas Fed staff research on trimmed-mean bias (Agent A, Nov 15, 2026)

Status: Round 1, not audited. Data only, no policy reading.
Quotes are checked verbatim by `code/A_quotes.py`; results are in `outputs/A_quote_check.csv`, IDs L1, D1–D13, C1–C3, DP1. Chart-data numbers come from `code/A_q2_dallas_data.py`, which writes `outputs/A_q2_dallas_data_extract.json`. Raw files are in `03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/`.

**Term.** *Skewness* is whether the extreme price changes in a month sit mostly in the upper tail (positive skew: more large increases) or the lower tail (negative skew: more large declines). The Dallas trimmed mean drops the bottom 24% and the top 31% of each month's spending-weighted price changes. That asymmetry was designed for the usual negative skew.

## Sources

| # | Source | Date | URL | Tag | What it says (≤2 sentences, quoted) |
|---|---|---|---|---|---|
| S1 | Atkinson, Dolmas, Zarutskie, "Skewness warrants caution as Trimmed Mean PCE inflation eases," *Dallas Fed Economics* | Apr 16, 2026 | https://www.dallasfed.org/research/economics/2026/0416 | [O] | "But if the distribution is not negatively skewed, this gives a downwardly biased measure of underlying trend. This likely contributed to the delayed rise of the trimmed mean during the inflation spike of 2021." (D1) |
| S1 | same | | | [O] | Method: "Percent price changes across 177 PCE categories are sorted each month, changes below the 24th percentile and above the 69th percentile are dropped." (D2) |
| S1 | same | | | [O] | When skewness is positive, "headline inflation more reliably converges toward core PCE, while the coefficients on trimmed mean are close to zero." (D3, Chart 4, sample from 1960) |
| S1 | same | | | [O] | Attribution: "Over the 12-month period ended in February 2026, there were fewer core goods price declines and more large price increases, accounting for 0.6 percentage points of the 0.7 percentage-point increase in the headline-trimmed mean gap. In contrast, the contribution to the increase in the gap from non-housing core services was minimal." (D5) |
| S1 | same | | | [O] | "However, the upside contributions from non-housing services have increased somewhat since September. If this trend in positive price changes continues, it could be the beginning of broadening inflationary pressures." (D6) |
| S1 | same | | | [O] | Counterweight: "The composition of core inflation is still supportive of disinflation, because core goods accounted for more than half of the overshoot through February 2026." (D7) |
| S2 | Atkinson, Dolmas, Zarutskie, "Alternative Trimmed Mean PCE inflation measure better tracked price surge," *Dallas Fed Economics* | Aug 13, 2026 | https://www.dallasfed.org/research/economics/2026/0813 | [O] | Recalibrated on 1967–2009: "The resulting trims are at the 19th lower percentile (the left tail) and at 20th upper percentile (the right tail), roughly symmetric and lighter than the 24/31 trims used in the original trimmed mean (Chart 1)." (D9) |
| S2 | same | | | [O] | "The recalibrated alternative trimmed mean currently stands at 2.6 percent for the 12 months ended in June, compared with 2.2 percent for the original trimmed mean." (D8) |
| S2 | same | | | [O] | 2021: "While headline and core exceeded 3 percent in April, trimmed mean did not until November (Chart 4)." (D10) |
| S2 | same | | | [O] | "However, while skewness remains elevated, as it has through June, our analysis suggests that greater weight should be placed on the alternative trimmed mean as a measure of the medium-term trend in inflation (Chart 5)." (D11) |
| S2 | same | | | [O] | Authors' own caveat: "This evidence doesn't offer a clear-cut conclusion on whether the original trimmed mean is a better measure than the alternate version, just as empirical evidence comparing core and trimmed mean inflation is typically inconclusive." (D12) |
| S2 | same | | | [O] | Both trimmed means have a tighter link to slack than core since the mid-1990s, "with the original trimmed mean doing a bit better on this dimension than the alternative over most of that period." (D13) |
| S3 | Rich, Verbrugge, Zaman, "Adjusting Median and Trimmed-Mean Inflation Rates for Bias Based on Skewness," Cleveland Fed *Economic Commentary* 2022-05 | 2022 (exact day not parsed from page) | https://www.clevelandfed.org/publications/economic-commentary/2022/ec-202205-adjusting-median-and-trimmed-mean-inflation-rates-for-bias-based-on-skewness | [O] | Cleveland Fed, not Dallas. S1 links it as "research has shown". "Compared to the median PCE inflation rate, the Dallas Fed's trimmed-mean PCE inflation rate currently suffers from more downward bias owing to its asymmetric trimming." (C2) Estimated bias in 2021: median about 15bp and trimmed mean about 35bp (C1). |
| S3 | same | | | [O] | Long-run unbiasedness: "Dolmas (2009) demonstrates that this degree of asymmetric trimming historically has resulted in an unbiased estimate of headline PCE inflation over longer periods." (C3) |
| S4 | Dolmas, "Trimmed Mean PCE Inflation," Dallas Fed WP 0506 | Jul 25, 2005 | https://www.dallasfed.org/-/media/documents/research/papers/2005/wp0506.pdf | [O] | The original methodology. Component price-change distributions are "both fat-tailed and left-skewed" (p.3, DO1), and robust measures show negative skew 58% of months over 1977–2004 (p.9). That is the reason for the asymmetric trim. |
| S5 | Dallas Fed, Trimmed Mean PCE Inflation Rate page | updated Oct 29, 2026; next Nov 25 | https://www.dallasfed.org/research/pce | [O] | "The Trimmed Mean PCE inflation rate over the 12 months ending in September was 2.3 percent." (DP1) The same page gives headline 3.6% and core 3.1% (12m, Sep 2026). Sep 1m annualized: TM 2.8, core 3.9. Sep 6m annualized: TM 2.4, core 2.9. |
| S6 | Logan, speech, Nov 10, 2026 | Nov 10, 2026 | https://www.dallasfed.org/news/speeches/logan/2026/lkl261110 (saved HTML) | [O] | Paragraph 162; see Q2.2 below. |
| — | Dolmas & Koenig 2019 (WP 1903; *Dallas Fed Economics* May 2019); FEDS Note Aug 2, 2019 "Comparing two measures of core inflation" | 2019 | listed on the S5 page and linked from S2 | [S] / not read | Related comparisons of trimmed mean and core. FEDS Note HTML saved but not read for this question. |

**Chart-data numbers** (from the Dallas `0416data.xlsx` and `0813data.xlsx`, via `A_q2_dallas_data.py`). The Kelly skewness measure is a 12-month average of monthly readings across PCE components.
- Kelly skewness (12m average) by month:
  - 2024-12: −0.188
  - 2025-09: −0.100
  - 2026-02: +0.011 (S1 vintage)
  - 2026-06: +0.092 (S2 vintage, latest published)
- Kelly skewness benchmarks:
  - 1977–2019 mean: −0.141
  - Share of 1977–2019 months with positive 12m skew: 13%
  - 2021 peak: +0.331 (Dec 2021)
- Latest one-month Kelly reading (Jun 2026): −0.468, a single-month swing negative.
- S2 Chart 5, 12m rates, Jun 2026, Jul 30 2026 vintage:

  | Measure | Jun 2026 12m |
  |---|---|
  | Core PCE | 3.29 |
  | Headline PCE | 3.67 |
  | Trimmed mean (24,31), original | 2.22 |
  | Trimmed mean (19,20), alternative | 2.57 |

  Gap, alternative minus original: 0.35pp.
- S1 Chart 5, change in the headline-minus-trimmed gap over the 12m ended Feb 2026, by category (pp):

  | Category | Contribution |
  |---|---|
  | Core goods | +0.637 |
  | Food and energy | +0.160 |
  | Non-housing core services | +0.033 |
  | Housing | −0.141 |
  | **Total** | **+0.690** |

## Q2.2 Logan's sentence: verified, with one wording difference

Exact text, paragraph 162 of the saved HTML. Extraction is in `outputs/text/logan_2026-11-10_paragraphs.txt`.

> "The New York Fed's multivariate core trend inflation index registered 2.8 percent in September. The Dallas Fed's trimmed mean PCE price index has been lower, 2.3 percent on a 12-month basis through September. My staff's research finds, however, that a change in the mix of price increases and decreases is causing the trimmed mean to drop too many increases right now. This effect likely makes the trimmed mean lower than the true inflation trend."

- **The roadmap quote matches, but truncated.** The speech adds "right now" at the end of the sentence and opens with "My staff's research finds, however,".
- **She does cite staff research.** In the HTML, "research" links to S1 (`/research/economics/2026/0416`) and "finds" links to S2 (`/research/economics/2026/0813`).
- **No footnote.**
- **"Likely".** The word is in the next sentence, in "likely makes the trimmed mean lower than the true inflation trend". It is not in "drop too many increases".
- **Context.** The paragraph sits in her "dashboard" of trend measures, between core PCE 3.1% (paragraph 161) and the breadth discussion. The breadth discussion includes non-housing, non-transportation core services at 3.2% (paragraph 165).

## Q2.3 Consistency with slide 2 Q4b (cited, not recomputed)

Slide 2 files:
- `10_slide2_research/report_D.md` item 11;
- `outputs/D_trimmed_reconcile.csv`, `D_trimmed_above3_fate.csv`;
- `Slide2_Inflation_Data.xlsx` `Breadth_measures` rows 52–68.

| Item | Slide 2 number | Source row |
|---|---|---|
| UMD replication of Dallas TM, Sep 2026, 1m / 6m / 12m | 2.848 / 2.427 / 2.265 (published 2.84 / 2.42 / 2.26) | D_trimmed_reconcile rows 1–3 |
| 24/31 trim applied once to 12m leaf rates, Sep | 2.981 (149 core leaves); 2.946 (177 headline leaves) | rows 4, 6 |
| Core leaves with 12m >3%: share of weighted leaf-months cut from top / bottom | 32.8% / 11.9% (included 49.5%, boundary 5.8%) | D_trimmed_above3_fate |
| Core leaves with 12m ≤3%: cut from top / bottom | 21.5% / 34.9% | same |
| >3% leaves: avg m/m ×12, all months vs kept months | 4.80% vs 2.65% | same |
| Dallas 12m, Sep 2025 → Sep 2026 vs 12m breadth | 2.76 → 2.27 vs 58.8 → 60.6 | report_D item 11 |

**Consistency (data only).**
- **Direction is consistent.** Slide 2 shows that months of high-inflation items are removed from the top far more often than from the bottom (32.8% vs 11.9%). The monthly-trim result (2.27) sits about 0.7pp below a one-time trim of 12m rates (2.98). This matches the S1/S2 mechanism: an asymmetric top-heavy trim drops many increases when large increases are common.
- **Magnitudes are not like-for-like.**
  - Dallas's own correction (the 19/20 alternative) is +0.35pp (Jun 2026).
  - Cleveland's 2021 skew adjustment was about +35bp.
  - The slide 2 0.7pp gap compares monthly trimming with 12m trimming, which is a different construct. Part of that gap would exist in any month, because trimming monthly changes removes lumpy one-month jumps even when the distribution is symmetric.
- **Neither slide 2 nor this task computes skewness on our leaf data.** The Dallas Kelly series is the only skewness evidence here, through Jun 2026.

## Worth a look (Q2)
1. **Unconditional benchmark.** 32.8% of >3% items' months are cut from the top, only slightly above the 31% of weight the method removes from the top every month. The large effect is in *which* months are kept: 2.65% vs 4.80%. That points to lumpy increases concentrated in a few months, which is related to the skew mechanism but not the same thing. An unconditional benchmark would separate them, for example the same "fate" calculation for 2018–19, or the 12m-trim vs monthly-trim gap for 2018–19. This is a coordinator or Eli decision; it would be a new computation, not a redo.
2. **Logan's research is two Dallas Fed Economics blog posts**, not refereed work. The authors say the evidence is not clear-cut (D12). The original 24/31 trim keeps a slightly tighter relationship with slack (D13).
3. **The latest public skew reading is June 2026.** Whether skew stayed positive through Sep is not published in these files. The Jun one-month reading swung to −0.47.
4. **The S2 text says core "has accelerated to mid-3 percent".** The current Dallas page shows core 3.1% for Sep (12m). The gap reflects later months and revisions, so don't quote S2's "mid-3" as current.
