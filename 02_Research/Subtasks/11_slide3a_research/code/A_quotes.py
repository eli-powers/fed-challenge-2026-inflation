"""Verify every verbatim quote used by Agent A against locally extracted text, then write
outputs/A_q1_bb_quotes.md, outputs/A_q7_pace_quotes.csv/.md and outputs/A_quote_check.csv.
Run from project root after A_extract_texts.py, A_html_text.py, A_logan_extract.py: python3 -I <this>."""
import re, csv
from pathlib import Path
ROOT = Path.cwd(); T = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs/text"
OUT = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs"
def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"-\s*\n\s*", "-", s)          # rejoin hyphenated line breaks
    return re.sub(r"\s+", " ", s).strip()
def pages(fn):
    t = (T / fn).read_text()
    parts = re.split(r"=====PAGE (\d+)=====", t)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
BB, PACE = pages("bb2023.txt"), pages("pace_qa.txt")
def bb_find(q, pdfp):
    hay = norm(BB[pdfp] + " " + BB.get(pdfp + 1, ""))  # allow a quote to run onto the next page
    return norm(q) in hay
# (id, pdf page, printed page, figure/table, quote, used_for)
BBQ = [
 ("BB1", 2, "abstract", "—", "We find that, contrary to early concerns that inflation would be spurred by overheated labor markets, most of the inflation surge that began in 2021 was the result of shocks to prices given wages.", "headline finding"),
 ("BB2", 2, "abstract", "—", "However, although tight labor markets have thus far not been the primary driver of inflation, we find that the effects of overheated labor markets on nominal wage growth and inflation are more persistent than the effects of product-market shocks.", "persistence asymmetry"),
 ("BB3", 8, "7", "Eq 3", "We call this term the catch-up term.", "catch-up definition"),
 ("BB4", 9, "8", "Eq 3", "The existence of a catch-up term implies that, in their bargaining with employers, workers seek to be compensated for last period's unexpected inflation.", "catch-up meaning"),
 ("BB5", 10, "9", "Eq 5-6", "The parameters", None),
 ("BB6", 12, "11", "Fig 2", "If the two types of shocks hit the economy simultaneously, the shock to prices will dominate inflation initially. However, as those effects fade, higher underlying inflation emanating from the labor market will become increasingly important.", "two-shock dynamics"),
 ("BB7", 16, "15", "—", "That ratio rose from less than 1.0 in April 2021 (that is, less than one open job per unemployed worker) to a historically high level of about 1.9 (nearly two job openings per unemployed worker) a year later.", "BB's own V/U description"),
 ("BB8", 17, "16", "—", "We conclude that", None),
 ("BB9", 18, "17", "Table 2", "Table 2 suggests that, when", None),
 ("BB10", 19, "18", "Table 2", "There is no evidence of a catch-up effect in Table 2, a result that appears robust.", "catch-up coefficient ~0"),
 ("BB11", 26, "25", "Table 3", "Since wages are controlled for, these findings suggest the presence of some second-round price-price effects of energy and food price shocks on the prices of other goods and services over time.", "second-round price-price effects"),
 ("BB12", 28, "27", "Table 4 / Fig 8", "There is no evidence of de-anchoring, defined here as an increase in the short-run effect of inflation on expected inflation: If estimated over the whole sample, including the covid period, estimated coefficients are very similar.", "short-run expectations anchoring"),
 ("BB13", 29, "28", "Table 5 / Fig 9", "In particular, there is no evidence that long-run expectations became de-anchored during the covid period.", "long-run expectations anchoring"),
 ("BB14", 31, "30", "Fig 10", "Figure 10 is striking, in that the effects of the three price shocks on inflation are quite short-lived, even more so than in the simulation of the analytical model under weak feedback parameters (Figure 1).", "price shocks transitory"),
 ("BB15", 33, "32", "Fig 11", "In this simulation, inflation has risen about 0.7 percent after 6 quarters, 1.0 percent after 12 quarters, and keeps increasing at about 0.15 percent per year from then on.", "V/U IRF magnitudes"),
 ("BB16", 35, "34", "Fig 12", "Energy price shocks in particular account for much of the rise of overall inflation in late 2021 and the first half of 2022, and the for the decline in inflation in the second half of 2022.", "decomposition: energy (sic 'and the for')"),
 ("BB17", 35, "34", "Fig 12", "Second, sectoral shortages were the dominant source of inflation in 2021Q2, and the effects of shortages on inflation, both direct and indirect, remained significant through the end of our sample period.", "decomposition: shortages"),
 ("BB18", 35, "34", "Fig 12", "However, over time, as the labor market has remained tight, the traditional wage Phillips curve effect has begun to assert itself, with the high vacancy-to-unemployment ratio becoming an increasingly important, though by no means dominant, source of inflation.", "decomposition: V/U rising importance"),
 ("BB19", 35, "34", "Fig 13", "Price shocks (energy, food, shortages) contribute less to wage growth than to price inflation, but even at the beginning of 2023 the direct and indirect effects of shocks to prices still explain a greater share than does the vacancy-to-unemployment ratio of the excess of wage growth over that predicted by the initial conditions.", "wage decomposition"),
 ("BB20", 39, "38", "Fig 14", "In contrast, in our projections, reducing the vacancy-to-unemployment ratio to its assumed steady-state level of 1.2 over the next eight quarters brings CPI inflation down to about 2.7 percent, which, adjusting for historical differences between CPI and PCE inflation, is within striking distance of the Fed's target.", "conditional projection"),
 ("BB21", 39, "38", "Fig 14", "All else equal, and not surprisingly, allowing", None),
 ("BB22", 40, "39", "Conclusion", "Our decomposition shows that, as of early 2023, tight labor market conditions still accounted for a minority share of excess inflation. But according to our analysis, if current labor market conditions persist, that share is likely to grow and will not subside on its own.", "conclusion: labor share growing"),
 ("BB23", 41, "40", "Conclusion", "The good news is that, empirically, we find the second-round and indirect effects of product-market shocks to be relatively modest, implying that, as the early critics warned, labor-market balance should ultimately be the primary concern for central banks attempting to maintain price stability.", "policy implication"),
 ("BB24", 37, "36", "Fig 14", "Instead, we interpret the simulations described below as conditional projections, not unconditional forecasts.", "projection caveat"),
 ("BB25", 11, "10", "Fig 1", "With a limited catch-up effect and well-anchored expectations, the conventional wisdom that monetary policymakers can \"look through\" temporary supply shocks is justified.", "look-through condition"),
 ("BB26", 6, "5", "—", "In contrast, we find that a linear relation between labor market tightness and wages, estimated on pre-covid data, fits the covid-era data reasonably well and is adequate to explain the recent behavior of wages.", "nonlinearity citation context"),
 ("BB27", 39, "38", "Fig 14", "If, in the other extreme case, the Beveridge curve were to remain at its position as of early 2023, then the unemployment rate associated with", None),
]
BBQ = [q for q in BBQ if q[5] is not None]
# Pace transcript passages: (id, pdf page start, speaker, section, topic, quote)
PQ = [
 ("P1", 1, "Giancarlo Raspanti", "presentation (output)", "labor slack / Okun's law", "However, at the same time, the unemployment rate has risen above the Fed's estimate of its natural rate. According to Okun's law, unemployment above natural must mean output growth is below potential."),
 ("P2", 4, "Alex Tuosto", "presentation (labor)", "labor slack / V/U", "Additionally, the quits rate and job openings for unemployed persons ratio are steadily declining, indicating future continued deterioration of the labor market."),
 ("P3", 4, "Suraj Sharma", "presentation (labor)", "labor slack / Beveridge curve", "This fall in vacancies and weakening labor demand may indicate an inflection point on the Beveridge curve. Currently, we are descending towards a flatter portion of the curve, meaning we expect any further declines in the job opening rate to now be met with higher rates of unemployment."),
 ("P4", 5, "Suraj Sharma", "presentation (inflation)", "Phillips curve / expectations", "As noted in the Phillips curve relationship, actual inflation depends partly on expected inflation, which guide wage and price setting. Currently, short-term market and survey-based inflation expectations are elevated above target due to tariff uncertainty."),
 ("P5", 5, "Suraj Sharma", "presentation (inflation)", "Phillips curve / expectations", "If these expectations stay above target, actual inflation may rise."),
 ("P6", 6, "Gianna Beck", "presentation (inflation)", "expectations anchoring", "Long-term market and survey-based inflation expectations have remained well anchored throughout recent periods of excess inflation, showing trusted forward guidance and, thereby, enhancing the committee's ability to achieve its dual mandate, even in the face of significantly high inflationary disturbances."),
 ("P7", 6, "Brooklyn Bynum", "presentation (inflation)", "wage-price / productivity", "It is important to note that high wage growth has not yet manifested into higher price inflation due to the growth in productivity. Considering productivity growth is inherently volatile, elevated short-term inflation expectations could soon put upward pressure on wages and, therefore, price inflation."),
 ("P8", 6, "Giancarlo Raspanti", "presentation (inflation risk judgment)", "productivity / risk balance", "With shorter dated annualized measures above target, tariff policy, increasing goods inflation, rising short-term inflation expectations and unreliably volatile productivity growth, we view the balance of risk as tilted towards the upside."),
 ("P9", 8, "Alex Tuosto", "presentation (policy deliberation)", "Phillips curve shift / supply shock", "Tariff policy acting like a supply shock has led to an upward shift in the Phillips curve, where now the same level of unemployment is met with a higher rate of inflation. Perhaps the continued contractionary policy level is appropriate."),
 ("P10", 8, "Suraj Sharma", "presentation (policy deliberation)", "labor slack / supply vs demand", "As both labor supply and demand fall at the same time, any weakening in labor demand is being masked by declining supply."),
 ("P11", 8, "Gianna Beck", "presentation (policy deliberation)", "labor slack / Beveridge curve", "These developments indicate an inflection point on the Beveridge curve, for any further declines in the job openings rate were met with higher rates of unemployment."),
 ("P12", 9, "Brooklyn Bynum", "presentation (forecast)", "slack / forecast", "It is also in line with the unemployment rate returning to natural over the medium term."),
 ("P13", 11, "Alex Tuosto", "Q&A (Common 1, payrolls vs unemployment)", "labor slack / V/U", "Additionally, we have seen labor demand indicators such as the vacancies per unemployed ratio, the quits rate and the hiring rate slowing, declining over this year, signifying, as my colleagues mentioned, that there is a broader labor market cooling and that we are seeing a falling labor demand within the economy."),
 ("P14", 13, "Suraj Sharma", "Q&A (Common 2, financial markets)", "Phillips curve (passing mention)", "Therefore, when we're evaluating the tradeoffs of different implications on financial markets, of course, we look at financial stability, we look at the tradeoff between the dual mandate, which can directly be seen through things like the Phillips curve and indirectly through a variety of indicators, and then we use all the assessments to come to a more holistic and appropriate recommendation for our policy."),
 ("P15", 18, "Giancarlo Raspanti", "Q&A (Lubik, short- vs long-run r-star)", "productivity / AI / r-star", "One of the reasons for this is the growth in productivity we've seen from things such as AI, for example. This has been noted by Governor Cook in one of her more recent speeches."),
 ("P16", 18, "Giancarlo Raspanti", "Q&A (Lubik, short- vs long-run r-star)", "productivity / AI / r-star", "And the breakdown of this is, if AI were to increase productivity gains, you would see a greater return on investments in the United States, which could increase the demand for investment."),
 ("P17", 18, "Giancarlo Raspanti", "Q&A (Pence, what would make inflation the bigger problem)", "expectations / revision trigger", "If we did see that, for example, tariff policies have been placing upward pressure on actual inflation, if we saw a de-anchoring of inflation expectations, this could lead to a response from the Federal Reserve as this could harm their credibility in their ability to achieve their price stability portion of their dual mandate."),
 ("P18", 18, "Giancarlo Raspanti", "Q&A (Pence, what would make inflation the bigger problem)", "expectations / revision trigger", "So, if we saw upward pressure on these longer-term expectations, we might want to consider responding to inflation developments more sharply."),
 ("P19", 3, "Brooklyn Bynum", "presentation (labor)", "labor slack / natural rate", "Over the past year, the U-3 unemployment rate hovered around the SEP's projection for its longer-run natural rate and now slightly exceeds this estimate."),
 ("P20", 4, "Brooklyn Bynum", "presentation (labor risk judgment)", "labor slack / Beveridge curve", "Labor market weakening as evident through slowing payroll growth, falling labor supply and demand, and an inflection point on the Beveridge curve, lead us to view the balance of risks as tilted towards the downside."),
 ("P21", 8, "Brooklyn Bynum", "presentation (policy stance)", "labor slack / policy stance", "This would explain the deterioration of a once tight labor market."),
 ("P22", 10, "Suraj Sharma", "Q&A (Common 1, payrolls vs unemployment)", "labor slack / natural rate", "That's .2 percentage points above what the SEP projects is natural at 4.2."),
 ("P23", 18, "Giancarlo Raspanti", "Q&A (Lubik, short- vs long-run r-star)", "productivity / AI / r-star", "If we see a rightward shift in the investment demand, this will put upward pressure on this real neutral interest rate and this is currently what we're seeing in the economy given those productivity gains."),
]
def strip_headers(s):
    return re.sub(r"TRANSCRIPT COLLEGE FED CHALLENGE NOVEMBER 21, 2025\s*Page \d+ of 19", " ", s)
def pace_find(q, p):
    hay = norm(strip_headers(PACE[p] + " " + PACE.get(p + 1, "")))
    return norm(q) in hay
# Notes files (secondary analysis, not transcripts): (id, file, line, quote)
NOTES_DIR = ROOT / "02_Research/External_views/Previous_Finalists_copy"
NQ = [
 ("N1", "2025 Finals - 1 Presentations.md", "Pace (notes on presentation)", "labor slack / Okun's law (critique)", "Its early Okun's-law inference also illustrates a trap. The unemployment gap at a point in time cannot by itself establish that current GDP growth is below potential growth."),
 ("N2", "2025 Finals - 1 Presentations.md", "Pace (notes, comparison table)", "productivity / wage-price", "Pace relates compensation and productivity to price pressure."),
 ("N3", "2025 Finals - 1 Presentations.md", "Pace (notes, comparison table)", "labor slack / Beveridge curve", "Pace adds the risk that further vacancy declines can carry a larger unemployment cost."),
 ("N4", "2025 Finals - 1 Presentations.md", "Pace (notes, story)", "labor slack", "Explain why slower workforce growth can mask a decline in labor demand, then corroborate with hiring, quits and vacancies per unemployed worker."),
 ("N5", "2025 Finals - 3 Q&A Response Strategies.md", "Pace (notes on Q&A)", "expectations / revision trigger", "In the 30-second question, Pace names longer-run expectations drifting up as evidence that would move inflation ahead of employment risk."),
]
def note_line(fn, q):
    lines = (NOTES_DIR / fn).read_text().splitlines()
    for i, l in enumerate(lines, 1):
        if norm(q) in norm(l): return i
    return None
check = []
for qid, pdfp, prp, fig, q, use in BBQ:
    check.append(("BB w31417", qid, f"pdf p{pdfp} / printed p{prp}", bb_find(q, pdfp)))
for r in PQ: check.append(("Pace transcript", r[0], f"pdf p{r[1]}", pace_find(r[5], r[1])))
nl = {}
for r in NQ:
    nl[r[0]] = note_line(r[1], r[4]); check.append((r[1], r[0], f"line {nl[r[0]]}", nl[r[0]] is not None))
# Q2 quotes (Logan + Dallas + Cleveland), checked against paragraph text files
Q2 = [
 ("L1", "logan_2026-11-10_paragraphs.txt", "My staff's research finds, however, that a change in the mix of price increases and decreases is causing the trimmed mean to drop too many increases right now. This effect likely makes the trimmed mean lower than the true inflation trend."),
 ("D1", "dallasfed_research_economics_2026_0416.txt", "But if the distribution is not negatively skewed, this gives a downwardly biased measure of underlying trend. This likely contributed to the delayed rise of the trimmed mean during the inflation spike of 2021."),
 ("D2", "dallasfed_research_economics_2026_0416.txt", "Percent price changes across 177 PCE categories are sorted each month, changes below the 24th percentile and above the 69th percentile are dropped."),
 ("D3", "dallasfed_research_economics_2026_0416.txt", "In these periods, headline inflation more reliably converges toward core PCE, while the coefficients on trimmed mean are close to zero."),
 ("D4", "dallasfed_research_economics_2026_0416.txt", "This analysis suggests that the currently lower Trimmed Mean PCE inflation rate relative to the core PCE inflation rate may not be strong evidence of disinflation ahead if price changes continue to exhibit a positive skew and the trimmed mean PCE cuts too many of these changes."),
 ("D5", "dallasfed_research_economics_2026_0416.txt", "Over the 12-month period ended in February 2026, there were fewer core goods price declines and more large price increases, accounting for 0.6 percentage points of the 0.7 percentage-point increase in the headline-trimmed mean gap. In contrast, the contribution to the increase in the gap from non-housing core services was minimal."),
 ("D6", "dallasfed_research_economics_2026_0416.txt", "However, the upside contributions from non-housing services have increased somewhat since September. If this trend in positive price changes continues, it could be the beginning of broadening inflationary pressures."),
 ("D7", "dallasfed_research_economics_2026_0416.txt", "The composition of core inflation is still supportive of disinflation, because core goods accounted for more than half of the overshoot through February 2026."),
 ("D8", "dallasfed_research_economics_2026_0813.txt", "The recalibrated alternative trimmed mean currently stands at 2.6 percent for the 12 months ended in June, compared with 2.2 percent for the original trimmed mean."),
 ("D9", "dallasfed_research_economics_2026_0813.txt", "The resulting trims are at the 19th lower percentile (the left tail) and at 20th upper percentile (the right tail), roughly symmetric and lighter than the 24/31 trims used in the original trimmed mean (Chart 1)."),
 ("D10", "dallasfed_research_economics_2026_0813.txt", "While headline and core exceeded 3 percent in April, trimmed mean did not until November (Chart 4)."),
 ("D11", "dallasfed_research_economics_2026_0813.txt", "However, while skewness remains elevated, as it has through June, our analysis suggests that greater weight should be placed on the alternative trimmed mean as a measure of the medium-term trend in inflation (Chart 5)."),
 ("D12", "dallasfed_research_economics_2026_0813.txt", "This evidence doesn't offer a clear-cut conclusion on whether the original trimmed mean is a better measure than the alternate version, just as empirical evidence comparing core and trimmed mean inflation is typically inconclusive."),
 ("D13", "dallasfed_research_economics_2026_0813.txt", "Both trimmed means have had a tighter relationship with economic slack, or the underutilization of economic resources, since the mid-1990s than has core PCE inflation, with the original trimmed mean doing a bit better on this dimension than the alternative over most of that period."),
 ("C1", "clevelandfed_ec202205.txt", "Accounting for the shift from negative to positive skewness, we estimate that recent readings of median PCE inflation and trimmed-mean PCE inflation have been understating the trend in PCE inflation by about 15 basis points and 35 basis points, respectively."),
 ("C2", "clevelandfed_ec202205.txt", "Compared to the median PCE inflation rate, the Dallas Fed's trimmed-mean PCE inflation rate currently suffers from more downward bias owing to its asymmetric trimming."),
 ("C3", "clevelandfed_ec202205.txt", "Dolmas (2009) demonstrates that this degree of asymmetric trimming historically has resulted in an unbiased estimate of headline PCE inflation over longer periods."),
 ("DP1", "dallasfed_research_pce.txt", "The Trimmed Mean PCE inflation rate over the 12 months ending in September was 2.3 percent."),
 ("DO1", "dolmas_wp0506.txt", "In section 3, I make a more rigorous case for trimming, showing that the distributions of individual component price changes that go into the PCE inflation rate are both fat"),
]
for qid, fn, q in Q2:
    check.append((fn, qid, "paragraph search", norm(q) in norm((T / fn).read_text())))
with open(OUT / "A_quote_check.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["source", "quote_id", "location", "found_verbatim"]); w.writerows(check)
bad = [c for c in check if not c[3]]
print(f"{len(check)} quotes checked; not found: {bad}")
# ---- write BB quotes md
L = ["# Bernanke & Blanchard (2023), NBER WP 31417: verbatim quotes used by Agent A", "",
     "Source: `02_Research/External_views/Literature/2023_Bernanke_Blanchard_pandemic_inflation_NBER_w31417.pdf` (June 2023 NBER working paper). Text extracted with pypdf (`code/A_extract_texts.py`); each quote checked verbatim (whitespace-normalized) by `code/A_quotes.py` (`outputs/A_quote_check.csv`). Page = printed page number (PDF page in brackets). Quotes are ≤2 sentences. [O] for all.", "",
     "| ID | Printed p. (PDF p.) | Figure / table / eq. | Used for | Quote |", "|---|---|---|---|---|"]
for qid, pdfp, prp, fig, q, use in BBQ:
    L.append(f"| {qid} | {prp} ({pdfp}) | {fig} | {use} | \"{q}\" |")
(OUT / "A_q1_bb_quotes.md").write_text("\n".join(L) + "\n")
# ---- write Pace csv + md
rows = []
for r in PQ:
    rows.append({"file": "02_Research/External_views/Previous_Finalists_copy/2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf",
                 "location": f"PDF p. {r[1]}" + (" (runs onto next page)" if not norm(r[5]) in norm(strip_headers(PACE[r[1]])) else ""),
                 "section": r[3], "speaker": r[2], "source_type": "official transcript (Federal Reserve)", "quote": r[5], "topic": r[4]})
for r in NQ:
    rows.append({"file": "02_Research/External_views/Previous_Finalists_copy/" + r[1], "location": f"line {nl[r[0]]}",
                 "section": r[2], "speaker": "n/a (analyst notes)", "source_type": "secondary notes (not a transcript)", "quote": r[4], "topic": r[3]})
with open(OUT / "A_q7_pace_quotes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print("wrote", len(BBQ), "BB quotes,", len(rows), "Pace rows")
# ---- Pace md (page order)
def pg(r):
    import re as _r
    m = _r.search(r"(\d+)", r["location"]); return (r["source_type"].startswith("secondary"), int(m.group(1)) if m else 0)
rs = sorted(rows, key=pg)
M = ["# Q7. Pace University (2025 national champion): Phillips-curve, slack, wage-price and productivity wording", "",
     "Status: Round 1, not audited. Verbatim; each passage checked by `code/A_quotes.py` against pypdf text (`outputs/text/pace_qa.txt`) or the notes files (`outputs/A_quote_check.csv`).", "",
     "**Sources.** (1) `2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf`: official Federal Reserve transcript (19 pp.), covering both the presentation (pp. 1–10) and judges' Q&A (pp. 10–19). Speakers named in the transcript. (2) The three `2025 Finals - *.md` files: someone's secondary notes and analysis (they cite the transcript and recordings and include a 2026 snapshot), not transcripts. [O] for all.", "",
     "**Coverage check.** Keyword scan of the transcript (phillips, productiv, wage, slack, beveridge, natural, okun, tight, vacanc, unit labor, labor cost). Every hit about labor slack, inflation, wages or productivity is below; hits about financial conditions or policy tightness (pp. 6, 7, 16) are excluded. No judge asked Pace about the Phillips curve, wages or productivity (question log: 6 prompts, none on these). The words 'unit labor cost', 'NAIRU' and 'wage-price spiral' do not appear.", "",
     "| # | File | Location | Section | Speaker | Topic | Quote |", "|---|---|---|---|---|---|---|"]
for i, r in enumerate(rs, 1):
    M.append(f"| {i} | {'Pace transcript (official)' if r['source_type'].startswith('official') else Path(r['file']).name + ' (notes)'} | {r['location']} | {r['section']} | {r['speaker']} | {r['topic']} | \"{r['quote']}\" |")
(OUT / "A_q7_pace_quotes.md").write_text("\n".join(M) + "\n")
with open(OUT / "A_q7_pace_quotes.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rs[0])); w.writeheader(); w.writerows(rs)
