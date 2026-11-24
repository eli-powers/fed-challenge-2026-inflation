"""Q10: verify lit_summary_DeMichelis_oil.md and STATE.md first-half summary against the saved FEDS Note text.
Extracts text from the saved HTML (read only), checks that every quoted string occurs verbatim in the note (or Waller speech PDF), and writes
outputs/C_q10_oil_note_verification.csv.
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q10_verify.py   (from project root)
Source files: 02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html ;
              .../speeches/2026-11-10_Waller_economic_outlook.pdf (pypdf)."""
import re, html, csv, sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import ROOT, OUT

EV = ROOT / "02_Research/External_views/Fed_officials_2026-11"


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"\s+", " ", s).strip()


raw = (EV / "staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html").read_text(encoding="utf8", errors="ignore")
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
t = html.unescape(re.sub(r"<[^>]+>", " ", t))
NOTE = norm(t)
try:
    import pypdf
    W = norm("\n".join(p.extract_text() for p in pypdf.PdfReader(str(EV / "speeches/2026-11-10_Waller_economic_outlook.pdf")).pages))
except Exception as e:  # pragma: no cover
    W = ""
    print("pypdf unavailable", e)

# (id, where_claimed, claim, source_location_in_note, status, exact_quote, doc, comment)
C = []


def add(src, claim, loc, status, quote, comment="", doc="note"):
    C.append((src, claim, loc, status, quote, comment, doc))


L = "lit_summary"; S = "STATE.md"
add(L, "Panel of five economies (US, Canada, euro area, Japan, UK), 2000:Q1-2026:Q2", "Empirical framework, para 3", "confirmed",
    "Canada, the euro area, Japan, the United Kingdom, and the United States")
add(L, "Sample 2000:Q1-2026:Q2, post-pandemic dummy from 2021:Q1", "Empirical framework, para 3", "confirmed", "The sample period spans from 2000:Q1 through 2026:Q2, with the post-pandemic period starting in 2021:Q1")
add(L, "Core inflation = core PCE for US, core CPI for the other four", "Empirical framework, para 3", "confirmed", "Core inflation is measured using core PCE prices for the U.S. and core CPI prices for the other economies")
add(L, "Regressors: two core lags, output gap, GSCPI, current + four lags of Brent oil inflation relative to core", "Equation 1 and para after it", "confirmed",
    "The specification includes four lags of oil-price inflation", "Sum over j=0..4 in the displayed equation = current + 4 lags (five quarterly terms). Oil is quarterly Brent in local currency, relative to core inflation.")
add(S, "'five quarters of Brent oil inflation measured relative to core'", "Equation; Empirical framework para 3", "confirmed", "oil inflation is measured from quarterly Brent prices in local currency and enters the model relative to core inflation")
add(L, "Horse race RMSE post-pandemic 0.37 -> 0.31 -> 0.17; largest single gain from pass-through", "Table 1 and para before it", "confirmed",
    "moving from constant coefficients to stronger persistence and pass-through lowers the RMSE from 0.37 to 0.17, with the single largest improvement in fit coming from the pass-through interaction",
    "Table 1 full-sample RMSE 0.31 / 0.24 / 0.14; post-pandemic 0.37 / 0.31 / 0.17.")
add(L, "Pre-pandemic persistence 0.347*** (95% CI 0.23-0.47); post-pandemic increase +0.298*** -> about 0.65", "Table 2; text under Table 2", "confirmed",
    "persistence roughly doubles to about 0.65 from 2021:Q1 onward", "Table 2: 0.347*** [0.225, 0.470]; +0.298*** [0.202, 0.395].")
add(L, "Pass-through pre-pandemic 0.001 (n.s.); post-pandemic increase +0.013** (CI 0.004-0.021)", "Table 2", "confirmed",
    "Post-pandemic increase in pass-through", "Table 2 row: 0.013** [0.004, 0.021]; pre-pandemic 0.001 [-0.002, 0.004]. Note text: pre-pandemic effect 'statistically insignificant'. (Quote is the row label; numbers are in the table.)")
add(L, "10 pp rise in relative oil inflation -> ~0.01 pp pre, ~0.14 pp post", "Text under Table 2", "confirmed",
    "a 10-percentage point increase in relative oil-price inflation raised core inflation by only about a statistically insignificant 0.01 percentage point. After the pandemic, the pass-through rises to a statistically significant 0.14 percentage point",
    "0.14 = 10 x (0.001 + 0.013) = TOTAL post-pandemic pass-through; the 0.013 in Table 2 is the INCREASE. Lit summary's table lists '+0.013' and '~0.14' side by side: clarify that 0.14 is the total (pre + increase). Units: 'for one-unit changes' (Table 2 text).")
add(L, "Permanent 10% oil rise: core price level +0.05% (pre) / just under 0.1% (persistence only) / 0.35% (both) after 12 quarters; most builds within ~8 quarters", "Figure 2 and text", "confirmed",
    "raising the core price level by only 0.05 percent after three years", "Also: 'to 0.35 percent after 12 quarters, with most of the effect building over roughly eight quarters.' Average across five economies (Fig. 2 note), not US.")
add(L, "Projection inputs: Brent futures early Aug 2026, GSCPI 1.63 SD in June, decay 0.8/quarter", "Section 'What does the model imply...'; fn 8", "confirmed",
    "the Brent futures curve (as of early August 2026) for the path of oil prices from 2026:Q3 onward; and the reading of the GSCPI through June 2026, at 1.63 standard deviations above its historical mean and projected forward at an estimated quarterly decay rate of 0.8",
    "fn 8: decay from regressing GSCPI on one lag over 2020:Q1-2024:Q4, slope ~0.8; half-life ~3 quarters.")
add(L, "Projection (Fig. 3): pre-pandemic peaks near 2.2%; persistence only plateau ~2.5%; full model nearly 2.8% mid-2027, ~0.6 pp above pre-pandemic path, ~2.2% by end-2028", "Text under Figure 3", "confirmed",
    "core inflation climbs to nearly 2.8 percent around mid-2027, roughly 0.6 percentage point above the path implied by pre-pandemic dynamics, before receding toward about 2.2 percent by the end of 2028")
add(L, "Pass-through part fades as oil normalizes; persistence part lasts into 2028", "Text under Figure 3", "confirmed",
    "the higher pass-through dominates the near-term peak but fades as the oil impulse in the futures curve normalizes")
add(L, "Authors call projection an upper bound, not a central prediction", "Text under Figure 3", "confirmed",
    "We therefore view these paths for core inflation as an upper bound on the likely impact rather than a central prediction")
add(S, "Authors 'read the results as an upside inflation risk'", "Intro para 3", "confirmed", "we view our results as suggestive of an upside risk to inflation")
add(L, "'second-round effects have not yet materialized; however, risks are mounting'", "Text after Figure 3", "confirmed",
    "second-round effects have not yet materialized; however, risks are mounting")
add(L, "Footnote 4 (country level): persistence significant in all five economies", "Footnote 4", "confirmed",
    "the rise in core inflation persistence post-pandemic broad-based and significant across all five economies",
    "fn 4 refers to country-specific OLS estimates; no coefficients, standard errors or table are shown for any single country.")
add(L, "Footnote 4: pass-through significant in US, Canada, Japan; not in euro area or UK", "Footnote 4", "confirmed",
    "it rose significantly in Canada, Japan, and the U.S., but was weaker and not statistically significant in the euro area and the U.K., possibly reflecting Europe's natural gas price shock following Russia's invasion of Ukraine",
    "Add: the authors' own explanation for Europe (gas shock). US magnitude is NOT reported anywhere in the note (no US coefficient, CI or figure). Significance level not stated.")
add(L, "Footnote 6: V/U replaces output gap -> +0.292 persistence, +0.010 pass-through, still significant", "Footnote 6", "confirmed",
    "The estimated post-pandemic increases in persistence and pass-through are 0.292 and 0.010, respectively, close to the baseline estimates of 0.298 and 0.013, and remain statistically significant",
    "Add: Canada excluded from this robustness check (vacancy series starts 2015).")
add(L, "Footnote 5: energy CPI instead of oil gives similar or larger pass-through", "Footnote 5", "confirmed",
    "Using energy CPI in place of oil prices delivers similar, indeed somewhat larger, estimates of the post-pandemic increase in pass-through")
add(L, "Footnote 3: adding import prices adds nothing", "Footnote 3", "corrected",
    "found no evidence of additional explanatory power for core inflation in the panel regression",
    "Panel result only. Same fn: 'Peneva et al. (2025) showed that for the U.S. it is important to control for import prices excluding oil and other energy products' but no consistent cross-country measure, and no tariff-inclusive import prices for the foreign economies, so import prices are NOT in the baseline. Do not say 'import prices add nothing' for the US.")
add(L, "Footnote 11: higher pass-through could reflect larger indirect effects on wages or on prices of other inputs", "Footnote 11", "confirmed (nuance)",
    "like larger indirect effects on wages or on the prices of other inputs",
    "In context this is the justification for how the GEMUS simulation proxies higher pass-through (higher oil cost share in production), not an empirical finding. 'Proxies for the underlying reasons why oil pass-through could be stronger'.")
add(L, "Reduced form: does not separate oil supply from demand shocks (fn 2, Kilian)", "Footnote 2; text after Fig. 3", "confirmed (nuance)",
    "This specification uses actual oil-price changes rather than attempting to isolate oil supply shocks using structural decomposition methods",
    "Authors add the counterpoint: 'our inclusion of the output gap controls for the state of economic activity, helping to isolate the cost-push component.' Demand co-movement caveat is in the main text: 'may partly reflect the co-movement of oil prices with broader global demand pressures'.")
add(L, "Cannot tell structural change from more frequent/persistent shocks; cannot say if change will endure or reverse", "Intro para 3", "confirmed",
    "cannot distinguish a structural change in the underlying inflation process from the possibility that global supply shocks have become more frequent, more persistent, or both")
add(L, "No US-specific model: US-specific drivers cannot be controlled for", "Intro para 3 (+ fn 4)", "confirmed (nuance)",
    "it does not allow us to control for some specific factors that have seemingly contributed to persistently elevated inflation in the U.S. because of the lack of comparable data in other countries",
    "Correct that there is no US-only model/table in the note; fn 4 gives country-specific OLS significance for the US without numbers.")
add(L, "GEMUS: 10% oil shock under a Taylor-type policy rule", "GEMUS section; fn 9, fn 10", "confirmed (detail added)",
    "Monetary policy in the model follows an inertial rule similar to that in Taylor (1999), with the policy rate responding to core inflation and the output gap",
    "Fn 10 (policy rule). Shock is generated 'through a reduction in that region's supply of oil to global markets' (a supply shock in a small oil-producing region of the foreign block). Same rule across all three calibrations; it is not a rule-comparison experiment. GEMUS = Global Economy Model for U.S. Policy Analysis (fn 9), extension of Cuba-Borda et al. (2025).")
add(L, "GEMUS scenarios: black = pre-pandemic (low persistence, low pass-through); red = higher persistence; blue = higher persistence + higher pass-through", "GEMUS section, Figure 4", "confirmed",
    "The red lines show the effects of the same shock under the higher inflation persistence indicated by our post-pandemic estimates")
add(L, "Higher pass-through engineered by raising oil cost share in production, calibrated to the regression estimate", "GEMUS section para 3; fn 11", "not in lit summary (added)",
    "we assume that firms' marginal costs respond more strongly to an increase in oil prices—engineered through a higher cost share of oil in production—and calibrate this increase to match the rise in pass-through estimated in our regressions",
    "Fn 11: also tried raising the frequency of price adjustment; 'similar implications for the near-term effects on activity and the policy rate'.")
add(L, "GEMUS: activity declines a little over 0.1% in the pre-pandemic (black) case", "GEMUS section para 2", "not in lit summary (added)",
    "activity declines a little over 0.1 percent", "Only numeric GEMUS anchor in the text; Figure 4 values are not in text/alt text.")
add(L, "'GDP hit about twice as large' with higher pass-through", "GEMUS section para 3", "confirmed (comparator unstated)",
    "The increases in both headline and core inflation are now much larger and more persistent, and the GDP hit is about twice as large",
    "The comparison base is not stated explicitly (presumably vs the earlier black/red cases). Text gives no figure for the blue-line GDP loss; 'twice' x 'a little over 0.1%' implies ~0.2-0.3% is the READER's inference, not in the note.")
add(L, "Policy has to 'tighten materially to contain inflation even as the economy weakens'", "GEMUS section para 3", "confirmed",
    "Monetary policy is put in the uncomfortable position of having to tighten materially to contain inflation even as the economy weakens")
add(L, "Decline in activity reflects both supply-side and demand-side forces", "GEMUS section para 3", "not in lit summary (added)",
    "The decline in activity reflects both supply-side forces, as firms face higher costs, and demand-side forces, as higher oil prices and tighter monetary policy restrain spending")
add(L, "Note does not recommend a policy", "Conclusion", "confirmed",
    "oil-price shocks may now pose greater challenges to monetary policy")
add(L, "Short, unusual sample (about 22 quarters; reopening demand, fiscal stimulus, tight labor market, supply chains, Bernanke-Blanchard)", "Text after Fig. 3; Conclusion", "confirmed",
    "the post-pandemic interactions are estimated from a short and unusual period",
    "22 quarters = 2021:Q1-2026:Q2 inclusive (arithmetic, not stated in the note).")
add(L, "Forecast inputs dated: Brent futures early Aug 2026, 'before the late-Oct spike above $110 and the subsequent drop'", "Text before Fig. 3", "corrected",
    "the Brent futures curve (as of early August 2026)",
    "The Aug date is confirmed. The 'late-Oct spike above $110' is WRONG: EIA daily Brent (outputs/C_q8_oil_daily.csv) was $86-97 in August, averaged $114 in September (peak $130.8) and $124 in October (peak $135.51 on Oct 2); it fell to $91.84 on Nov 4 and $92.14 on Nov 11. Bowman's 'at or above $110 in late October' is consistent with this.")
add(L, "Waller: core 'may be more responsive to energy shocks'", "Waller speech, p.2-3", "confirmed", "core inflation may be more responsive to energy shocks", doc="waller")
add(L, "Waller: 'in a more sustained way than in the past'", "Waller speech", "confirmed", "may pass through to goods and services in a more sustained way than in the past", doc="waller")
add(L, "Waller: 'cautions against taking too much comfort in this view'", "Waller speech", "confirmed", "this new work cautions against taking too much comfort in this view", doc="waller")
add(L, "Waller: 'larger than previously thought and persist well into 2027', 'especially if oil prices were to remain elevated'", "Waller speech", "confirmed (typo)",
    "especially if oil prices were to remain elevated, these pressures could be larger than previously though and persist well into 2027",
    "Speech text reads 'previously though' (typo for 'thought'). 'Well into 2027' is Waller's paraphrase; the note itself shows a mid-2027 peak for the pass-through path and an elevated persistence path 'well into 2028'.", doc="waller")
add(L, "Waller leaves out that authors call projection an upper bound", "Waller speech vs note", "confirmed",
    "Their analysis suggests that, especially if oil prices were to remain elevated", "No mention of 'upper bound' anywhere in the Waller paragraph (checked by text search).", doc="waller")
add(L, "Neither Waller nor the note says 'a second round could come' in second-round terms", "Waller speech; note", "confirmed",
    "second-round effects have not yet materialized; however, risks are mounting", "Waller's paragraph contains no 'second-round' wording (text search).")
add(S, "'Reads flagged' bullet: 'oil may be standing in for broader demand pressure'", "Text after Fig. 3", "confirmed",
    "may partly reflect the co-movement of oil prices with broader global demand pressures")
add(S, "'no US-only estimates in the main text'", "Intro para 3; fn 4", "confirmed", "it does not allow us to control for some specific factors that have seemingly contributed to persistently elevated inflation in the U.S.")

# ---- programmatic quote check and notes ----
rows = []
for src, claim, loc, status, quote, comment, doc in C:
    hay = NOTE if doc == "note" else W
    found = norm(quote) in hay
    if not found:  # allow Waller line-break hyphenation artefacts
        found = norm(quote).replace(" ", "") in hay.replace(" ", "")
    rows.append({"claim_source": src, "claim": claim, "source_location": loc, "status": status, "quote_verbatim_found_by_script": found,
                 "exact_quote": quote, "comment": comment,
                 "document": "FEDS Note, De Michelis et al., Nov 9 2026 (saved HTML)" if doc == "note" else "Waller speech Nov 10 2026 (saved PDF)"})
# negative text searches
neg = [("'second-round' occurrences in Waller speech", len(re.findall("second-round|second round", W, flags=re.I))),
       ("'upper bound' occurrences in Waller speech", len(re.findall("upper bound", W, flags=re.I))),
       ("'upper bound' occurrences in note", len(re.findall("upper bound", NOTE, flags=re.I))),
       ("footnotes in note (numbered 1-11)", len(re.findall(r"\b(1[01]|[1-9])\. (?:The note|This specification|We also|Country-specific|Using energy|As a robustness|These estimates|The decay|GEMUS|Monetary policy in|The assumption)", NOTE)))]
print(neg)
with open(OUT / "C_q10_oil_note_verification.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
bad = [r for r in rows if not r["quote_verbatim_found_by_script"]]
print(len(rows), "rows;", len(bad), "quotes not found verbatim:")
for r in bad:
    print("  -", r["claim"][:80], "|", r["exact_quote"][:90])
