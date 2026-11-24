# Slide 3B Q&A prep: stress test (Agent D, 2026-11-15)

**Status:** Round 1, not audited. Every answer below is a draft for Eli. Lines that state a landing or a regime judgment are marked **PENDING Eli**.

**Basis for every number:** SPF 2026Q3 median baseline (deadline Aug 11, 2026); oil-assumption proxy Aug-2026 EIA STEO; Brent to Nov 11; core PCE actuals FRED PCEPILFE vintage Oct 29. Core PCE, SA. "Q4/Q4" is the Q4 average over the prior Q4 average. Q4 SPF not out at the time of writing (A checked 17:40 ET Nov 15; D did not recheck). **Nov 16 (coordinator): Q4 SPF released and rerun; #7 and #8 now carry Q4 answers below the Q3 ones. Other answers (#1–6, #10–11) still use Q3-run numbers; #6's oil break-evens ($60 / $70) and the +$10 effect come from `D_q7_checks.py`, which reads only the Q3 run, and were not recomputed for Q4.** Q4 key: **Q4G** = `03_Data/pipelines/forecast_3b/processed/scenario_grid_2026Q4.csv`; **VC** = `processed/vintage_compare.csv`; FINAL §1b.

**Tags:** [O] = opened and read by D. [V] = verified by the coordinator in report_A/B/C and used as-is. [D] = recomputed by D in `code/D_q7_checks.py` → `outputs/D_q7_checks.csv`.

**Citation keys:**
- **GRID** = `report_C.md` Q6 table / `03_Data/pipelines/forecast_3b/processed/scenario_grid_2026Q3.csv`.
- **AX** = `outputs/C_q6_axis_compare.csv`.
- **DEC** = `outputs/C_q6_jumpoff_decomposition.csv`.
- **SENS** = `outputs/C_q6_sensitivity.csv` (line numbers given).
- **JO** = `outputs/C_q6_jumpoff.md`.
- **DQ** = `outputs/D_q7_checks.csv`.
- **NOTE** = the FEDS oil note, De Michelis, Orak, Pradhan & Queralto, Nov 9 2026 (`02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html`) [O].

**Two numbers worth knowing cold** (both [V], 2027 Q4/Q4):
- **Baseline:** 2.40.
- **Six cells:** pre-pandemic 2.40 / 2.48 / 2.42; post-pandemic 2.93 / 3.16 / 2.72 (P1 STEO / P2 $110 / P3 Hormuz+$25) (GRID).

---

## 1. "Your forecast is just the SPF."

**Judge:** "Strip away the grid: isn't this just the SPF with some decoration? What do you actually add?"

**Steelman:**
- Under pre-pandemic dynamics the adjustment to 2027 Q4/Q4 is −0.002 to +0.08 pp, so on half the grid we add nothing (DEC "full" rows: P1 −0.0016, P2 +0.0815, P3 +0.0179) [V].
- The post-pandemic adjustment comes from a five-economy staff note we did not estimate.
- So the value-added is a borrowed coefficient applied to a borrowed baseline.

**Answer (52 words):** "The SPF is our starting point, dated August 11, before the oil spike. What we add is the spike, measured explicitly. Under pre-pandemic pass-through it barely matters: under a tenth for 2027. Under post-pandemic pass-through it adds about 0.3 to 0.8 points, taking 2027 core from 2.4 to between 2.7 and 3.2."
- Sources: post adjustments +0.32 / +0.53 / +0.76 (DEC, P3/P1/P2 post "full"); cells 2.72–3.16 (GRID) [V].

**Do NOT say:**
- "Our forecast is 2.9." There is no single forecast unless Eli sets one.
- "We estimated the pass-through."
- "The SPF already includes oil."

**Real weakness?** **Yes (disclose).** On the pre-pandemic column the adjustment is negligible. Frame that as the finding (the regime is the lever; AX: across regimes 0.30–0.68 pp vs across oil paths 0.08 pre / 0.44 post), not as a gap.

---

## 2. The oil note is a five-economy panel and an upper bound; there's no US number

**Judge:** "That note pools Canada, the euro area, Japan, the UK and the US, and the authors call their projection an upper bound. Where's the US estimate?"

**Steelman:**
- The note reports no country coefficient, interval or figure. The US appears only in footnote 4, which says pass-through "rose significantly in Canada, Japan, and the U.S." [O].
- The authors say the panel "does not allow us to control for some specific factors that have seemingly contributed to persistently elevated inflation in the U.S." [O].
- They "view these paths for core inflation as an upper bound on the likely impact rather than a central prediction" [O].
- The post-pandemic sample is 2021Q1–2026Q2, 22 quarters, which "likely capture[s] more than a pure structural oil-to-core channel" [O].
- So the post column transplants a panel average onto US core PCE.

**Answer (58 words):** "Agreed, and the slide says so. The note has no US-only estimate. Footnote 4 puts the US among the economies where pass-through rose significantly, but gives no number. So we read the post-pandemic column as the authors read their projection: an upper bound; and the pre-pandemic column as the low case. Slide 3A tests where the US sits."

**Do NOT say:**
- "The Fed estimates US pass-through at 0.14."
- "US core rises 0.35% per 10% oil."
- "The note shows firms changed how they set prices." This is barred wording. The note says it "cannot distinguish a structural change … from" more frequent or persistent supply shocks [O].
- "The truth is between the two columns." Nothing establishes that; the US-specific magnitude is unknown.

**Real weakness?** **Yes (disclose, on slide).** It is a locked caveat. The "upper bound" quote attaches to the Fig. 3 projection, which assumes post-pandemic dynamics persist through 2028. Applying it to our post column is our reading and should be said as such.

---

## 3. The baseline's oil assumption is guessed

**Judge:** "The SPF doesn't ask about oil. How do you know what oil price is in the baseline?"

**Steelman:**
- There is no published assumption (A Q2) [V].
- On the deadline day spot Brent was $93.26, above the Aug STEO's 2026Q3 $85.26 and Q4 $78 (`A_q2_proxy_note.md`) [O].
- The 2027 futures curve averaged about $78 vs the STEO's $69.5 (A) [V].
- A lower assumed path inflates every gap. The proxy choice moves P1 × post 2027 Q4/Q4 by about 0.33 pp, which is comparable to the oil axis.

**Answer (60 words):** "We don't know it; nobody publishes it. We use EIA's forecast released on the survey deadline, August 11, and test alternatives. On the baseline oil path with post-pandemic pass-through, 2027 core is 2.83 against the futures curve, 2.93 against August's EIA forecast and 3.16 against July's. The proxy moves us a third of a point; the regime moves us more."
- Sources: SENS line 129 (futures hybrid, 2.8262), GRID P1 × post 2.9273, SENS line 93 (Jul STEO, 3.1564); AX P1 across regimes 0.53 [V].

**Do NOT say:**
- "SPF forecasters assumed $78 oil."
- "Futures prices from CME/ICE." The curve is Yahoo-aggregated NYMEX BZ closes [2], and the futures hybrid uses STEO for 2026.

**Real weakness?** **Yes (disclose).** Keep the three-proxy line in backup. The futures check is secondary-source only.

---

## 4. Why these three oil paths?

**Judge:** "Why these paths? Isn't $110 just a number from a speech, and why would a reopened Hormuz still carry a $25 premium?"

**Steelman:**
- **Bowman's $110 describes history, not a forecast.** Her words: Brent "moved up to and above $110 per barrel in the second half of October before dropping sharply last week" (Bowman, Nov 10, saved RTF) [O]. Daily Brent was at or above $110 on every day from Sep 10 to Oct 31, and October averaged $123.93 (`B_q3_brent_daily.csv`) [D]. So "$110" is below where oil just was.
- **Waller's $20–30 is today's cost of passage, not a post-reopening residual.** His words: "even as there is increased tanker traffic through the Strait of Hormuz, that traffic is moving at great expense … are reportedly boosting oil prices by $20 to $30 a barrel" (Waller, Nov 10, saved PDF) [O]. It is secondhand ("reportedly") and refers to "oil prices", not Brent.
- **The grid is asymmetric.** Even P3 + $25 lies above the Aug assumption, so every central path is inflationary (B Worth a look #5) [V].

**Answer (58 words):** "One path is EIA's current forecast. One is a return to $110, the level Governor Bowman cited for late October. One is Hormuz reopening: EIA's pre-war forecast plus $25, the middle of the $20 to $30 Governor Waller described as today's cost of passage. So that path is generous. With no premium, post-pandemic 2027 core falls to 2.25."
- Source: SENS line 69, P3 + $0 × post 2.2496 [V].

**Do NOT say:**
- "Bowman forecasts $110."
- "Waller expects a $20–30 premium after reopening."
- "$110 is a new spike." It is below the October average.
- Don't call any path "most likely".

**Real weakness?** **Yes (disclose).** The reopening path keeps today's passage cost, which biases the low path upward. Keep the $0-premium variant (2.25 post / 2.34 pre; SENS lines 69, 65) in backup and say "generous" out loud.

---

## 5. Scenarios vs probabilities: "So what's your forecast?"

**Judge:** "Six cells is not a forecast. If you were on the Committee, which one is your modal path?"

**Steelman:**
- A Committee member must submit one SEP number.
- Refusing to weight sounds like evasion, and the fan looks like a confidence band.

**Answer (45 words):** "Our forecast is conditional, and the condition is observable. If pass-through is back to pre-pandemic behaviour, core ends 2027 near 2.4 to 2.5 whatever oil does. If post-pandemic dynamics hold, it's 2.7 to 3.2, depending on oil. Slide 3A is how we judge which: [**PENDING Eli**: the regime reading and the landing number]."
- Sources: pre 2.40–2.48, post 2.72–3.16 (GRID; AX 2027 Q4/Q4 rows) [V].
- If Eli sets `REGIME_WEIGHT_POST`, the weighted path is the landing number. It is Eli's judgment, and it must be presented as a judgment, not a probability.

**Do NOT say:**
- "There's a 60% chance."
- "The fan is a confidence interval." `fan_2026Q3.csv` is labelled "SCENARIO RANGE … NOT a probability fan" (C) [V].
- "Most likely is P1 × post" unless Eli has decided it.

**Real weakness?** **Yes (blocking for the presentation, not for the research).** Without a stated landing, conditional on 3A, the Q&A chain stops at "forecast" and never reaches "policy consequence". Owner: Eli.

---

## 6. What would change the forecast?

**Judge:** "What would make you revise this before December?"

**Steelman:**
- Revision triggers that are vague ("if oil moves") don't earn credit.
- Judges want an observable, a threshold and a direction.

**Answer (56 words):** "Three things. Oil: with post-pandemic pass-through, each sustained $10 on Brent through 2027 moves 2027 core about a tenth; only oil near $60 erases our adjustment. Core prints: the SPF's fourth quarter needs November and December near 0.05% a month after October's 0.3. Repeating 0.3 says the baseline is stale. And the new SPF, November 16."

Sources [D] (DQ unless noted):
- +$10 on P1 in 2027: +0.099 pp post / +0.029 pp pre.
- Flat Brent from Nov 12 that zeroes the 2027 Q4/Q4 adjustment: $60.37 post / $70.73 pre.
- Flat at the Nov 11 spot ($92.14): 2.930 post, about equal to P1.
- 0.053% m/m: JO §1 [V].
- Oct 0.295 m/m: JO / Slide 1 [V].
- Nov 16 Q4 SPF date: roadmap/brief, unverified (A).

**Do NOT say:**
- "October PCE before the finals." Oct PCE is Nov 25, after the Nov 18 cutoff (`03_Data/README.md` line 46) [O, project file]. Present it as a forward trigger only.
- Any other release date not checked (e.g. Nov CPI).

**Real weakness?** **No.** This is a strength if it is on the slide as one line. The break-even ($60 post) is new from D and should go to the audit.

---

## 7. Q3 vs Q4 SPF vintage

**Judge (Q3 still in use):** "Your baseline is from August, before oil went to $130. Why use a stale survey?"
**Judge (after the rerun):** "Your forecast moved when you swapped surveys. Which one do we believe?"

**Steelman:**
- The Q3 survey predates the Sep–Oct spike. Spot averaged $114.16 in September and $123.93 in October vs the Aug STEO's $85 and $80 (`A_q2_proxy_note.md`) [O].
- It also predates the September hike and the ALFRED vintage break, which moved 2026Q1 core from 4.42 to 3.94 (A Worth a look #1) [V].
- After the switch, if the Q4 deadline is on or after Nov 10, the Nov STEO becomes the matched proxy, and **P1's gap is near zero by construction** (pipeline README; C Worth a look #8) [V]. The P1 row then shows almost no regime difference.
- So the slide's message can flip between vintages: the Q3 version says the regime matters even at baseline oil; the Q4 version says the regime matters only if oil departs from November expectations.

**Answer, pre-rerun (49 words):** "Dating it is the point. The August survey is a clean pre-spike baseline, so we can measure the spike explicitly instead of guessing how forecasters priced it. The November survey already prices the spike. On it, our adjustment answers a narrower question: what if oil departs from today's expectations? [**PENDING**: numbers from the Nov 16 rerun.]"

**Do NOT say:**
- "The Q3 SPF accounts for the spike."
- Any Q4 SPF number before the rerun exists. The pipeline was tested only on a synthetic Q4 row (C) [V].

**Real weakness?** **Yes (blocking once Q4 lands).** Eli must decide before the rerun whether the slide shows Q3 (explicit spike), Q4 (spike embedded) or both. The choice changes what the regime axis means.

### 7, after the Q4 rerun (coordinator, Nov 16; not Codex-audited)
**What happened** [O, Q4G / VC]:
- Q4 SPF deadline Nov 11, after the spike. 2027 Q4/Q4 median 2.40 → **2.50**; 2026Q4 2.62 → 3.00; 2027Q4 now published (2.36).
- Matched proxy = Nov STEO = P1, so P1's gap is ~0 from 2027Q1; P1 2027 Q4/Q4 is 2.52 in both regimes.
- 2027 Q4/Q4 cells: post 2.52 / 2.75 / 2.31; pre 2.52 / 2.61 / 2.54 (P1 / P2 / P3). Range 2.31–2.75 (Q3 run: 2.40–3.16).
- Axis: oil path 0.08 (pre) / 0.44 (post); regime 0.01 / 0.15 / 0.23. The Q3 ordering (regime larger) reverses.

**Answer, post-rerun (58 words) [PENDING Eli]:** "We ran both, and the switch is one rerun. The November survey was taken after the spike; forecasters moved 2027 core up a tenth, to 2.5. On it, our baseline oil path barely moves anything, so the question becomes: what if oil departs from November expectations? $110 oil takes 2027 to 2.6–2.75; reopening, 2.3–2.5."
- Sources: VC / Q4G 2027Q4/2026Q4 rows: P2 pre 2.605, post 2.751; P3 post 2.311, pre 2.542 [O].

**Do NOT say:**
- "Forecasters only added a tenth, so pass-through must be weak." That reads a regime off the survey; not established, and the regime call is Eli's.
- "The November survey prices the spike correctly", or any claim about what oil price respondents assumed (still a proxy).
- The Q3-run numbers (2.93, $60 break-even, flat-spot 2.93) against the Q4 baseline.

**Real weakness?** **Yes (disclose).** On Q4, P1 is near-baseline by construction (Judgment_calls item 2 in the workbook): the "central" row is tautological unless Eli adds a non-proxy path. The vintage choice for the slide is still Eli's.

---

## 8. Double counting

**Judge:** "September and October core already reflect the oil spike. Aren't you counting it twice?"

**Steelman:**
- Realized Q3 (2.47) and October (0.295 m/m est.) contain some oil pass-through.
- Under post-pandemic dynamics, the 2026H2 gap steps produce 92–134% of the 2027 Q4/Q4 adjustment (DEC) [V].
- Respondents on Aug 11 saw spot at $93, above our proxy, so part of the "gap" may already be in the baseline.

**Answer (58 words):** "We never adjust published data. Third-quarter core is the actual 2.47, untouched; the adjustment starts in the fourth quarter, on an August survey that didn't contain the spike. The bigger issue runs the other way. Given our October estimate, the SPF's fourth quarter needs November and December core near 0.05% a month. That gap exceeds any oil adjustment."
- Sources: 2026Q3 unadjusted (C method; GRID 2026Q3 rows status=actual); 0.053% (JO §1); cells need 0.061–0.110% (JO table); Oct pace gives 2026Q4 3.61 vs cells 2.65–2.85 (C Worth a look #1) [V].

**Do NOT say:**
- "There's no overlap at all." The proxy-timing overlap is real; see #3.
- "Our 2026 Q4/Q4 forecast is 3.1."

**Real weakness?** **Yes (disclose; affects what goes on the slide).**
- The 2026Q4 cells (2.65–2.85 annualized) and 2026 Q4/Q4 (3.09–3.14) sit below every outside 2026 number: SPF published 3.29, SEP 3.4, Oct-pace 3.33 (A; JO) [V]. Bowman's "likely moved up further to 3.3 percent in October" is a y/y figure, not a forecast [O].
- Lead with 2027. Show 2026 only with the jump-off caveat, or after the Q4 rerun.

### 8, after the Q4 rerun (coordinator, Nov 16; not Codex-audited)
**What changed** [O, Q4G; jump-off recomputed with the builder's live formula]:
- The Q4 survey (deadline Nov 11) postdates the spike, so the oil gap is measured from the Nov STEO; what remains is deviation from November expectations. P1's only gap is 2026Q4 (−0.67 log pts, observed Oct–Nov 11 vs the STEO's quarter), worth −0.001 pp on 2026 Q4/Q4 (post).
- Jump-off: the Q4 SPF's 2026Q4 of 3.00 needs Nov–Dec core of **0.147% m/m** given our Oct 0.295 (Q3 SPF: 0.053%).
- 2026 cells: 2026Q4 2.90–3.03 annualized; 2026 Q4/Q4 3.15–3.19, around the SPF's published 3.18, still below the SEP's 3.4 and the Oct-pace 3.33.

**Answer, post-rerun (55 words) [PENDING Eli]:** "We never adjust published data, and the November survey was taken after the spike, so we only adjust for oil that departs from what forecasters already saw. The open question is the jump-off: the survey's fourth quarter needs November and December core near 0.15% a month, about half October's 0.3."

**Do NOT say:**
- "There's no double counting at all." The proxy is still a proxy; respondents' own oil assumption is unknown.
- "Our 2026 Q4/Q4 forecast is 3.2."

**Real weakness?** **Yes (disclose), smaller than on Q3.** The jump-off gap narrows (0.147% needed vs 0.053%) but does not close.

---

## 9. Linear mapping, the Lucas critique and the policy response

**Judge:** "Those coefficients come from a period when the Fed was behind the curve. Does your adjustment assume the Fed doesn't respond to oil?"

**What the note says** [O]:
- The model is "a backward-looking augmented Phillips curve" in which "inflation expectations depend on past inflation outcomes".
- The Fig. 2 note: "All exogenous variables are held fixed; the response reflects only oil price pass-through and the intrinsic persistence of core inflation." The output gap and the GSCPI are held fixed.
- There is no policy rate in the equation.
- The GEMUS section (structural) uses "an inertial rule similar to that in Taylor (1999)". With higher persistence and pass-through, "Monetary policy is put in the uncomfortable position of having to tighten materially to contain inflation even as the economy weakens", and "the GDP hit is about twice as large".

**Steelman:**
- The mapping is partial-equilibrium: no output-gap response to oil (which would lower core) and no reaction-function change.
- Lucas critique: the 2021–22 sample combined large shocks with a late policy response. A faster-reacting Fed (25 bp hike in September; Waller's 25 bp baseline, 50 bp if Oct core CPI was ~0.3) could lower effective pass-through through expectations. This is D's inference; the note does not say it.
- Linear superposition is exact within the model (B: 0.0001 pp) [V], but large shocks may not be linear in reality.

**Answer (56 words):** "Yes, it's partial. The note's Figure 2 holds the output gap and other inputs fixed, and its equation has no policy rate. So our cells show the inflation pressure before any extra policy response. That's the point: the note's own structural model says that with high pass-through, policy must tighten materially even as the economy weakens."

**Do NOT say:**
- "The note says the Fed should hike."
- "The coefficients are structural."
- "The note holds policy fixed." It holds exogenous variables fixed; policy is simply not in the reduced form.
- Don't quote a GDP number. The note gives none in text (C_q10) [V].

**Real weakness?** **Yes (disclose; label).** Add "before any additional policy response" to the grid caption. It is also the bridge to the policy section.

---

## 10. "The pre-pandemic regime is irrelevant now" vs "the post-pandemic regime is a 22-quarter fluke"

**Judge A:** "The world changed after 2021. Why even show the pre-pandemic column?"
**Judge B:** "Twenty-two quarters of reopening, stimulus and supply chaos. Why should that sample tell us anything about 2027?"

**Steelman A:**
- In the note's horse race, adding post-pandemic pass-through cuts the post-pandemic RMSE from 0.31 to 0.17 (Table 1) [O].
- Persistence roughly doubles (0.35 → 0.65) [O].

**Steelman B:**
- The authors list "reopening demand, fiscal stimulus, labor-market tightness, supply-chain disruptions, and high energy prices".
- They say the interactions "may partly reflect the co-movement of oil prices with broader global demand pressures".
- They say they "cannot say whether this change will endure or reverse" [O].
- The pre-pandemic pass-through CI is −0.002 to 0.004; the post increase CI is 0.004 to 0.021 [O].

**Answer to A (48 words):** "Because the authors themselves don't rule it out. They say the post-pandemic terms may capture demand moving with oil, and in a more normal environment both persistence and pass-through could be weaker. If that unwinds, pre-pandemic is where we land. It's the low case, not a straw man."

**Answer to B (48 words):** "It might be. But the rise isn't one country. It's significant in a five-economy panel, including the US per footnote 4. And allowing it cuts the model's post-pandemic tracking error from 0.31 to 0.17. That's why we don't pick a column mechanically. Slide 3A tests the US-specific evidence."

**Do NOT say:**
- "Price-setting behaviour changed."
- "The post-pandemic regime is the truth."
- Don't quote Table 2's "0.013" as the post-pandemic pass-through. It is the increase; the total is 0.014, i.e. 0.14 pp per 10 pp relative oil inflation (C_q10) [V].

**Real weakness?** **Yes (disclose).** Both columns are live, which is why the grid has two. The deeper fix is 3A's US evidence. Owner: Eli.

---

## 11. Three more a Fed economist would ask

### 11a. "Your post-pandemic 2027Q4 jumps to 3.6% annualized. Why would core spike in late 2027?"

**Steelman:** a quarterly path with a 0.46 pp jump in one quarter (P2 × post 2027Q3 3.14 → Q4 3.60; GRID lines for P2 post) looks like a modelling artefact [V].

**Answer (41 words):** "It's the note's lag shape. Its Figure 2 response dips at one quarter and jumps at four, so the big fourth-quarter-2026 oil step shows up a year later. We don't read quarterly spikes; we lead with Q4-over-Q4, which averages through them."
- Source: R_post k=0 0.0184, k=1 0.0105, k=4 0.1850 (`config/regime_response.csv`) [O].

**Do NOT say:** "core will be 3.6% in Q4 2027."

**Real weakness?** **Yes (non-blocking).** No quarterly-annualized post path should appear on the slide without a label.

### 11b. "Higher persistence applies to every shock, not just oil. Why apply it only to the oil gap?"

**Steelman:**
- In the note, post-pandemic persistence (0.65 vs 0.35) is a property of core inflation itself. Fig. 3 attributes about 0.3 pp at the peak to persistence alone [O].
- Our grid uses the regime only to map the oil gap. The SPF baseline's own disinflation from 3%+ core is left as the forecasters had it.
- So "post" in our grid is not the note's full post-pandemic world.

**Answer (58 words):** "Fair. Our regime axis changes only how the oil gap passes through; the baseline's own persistence is whatever SPF forecasters assumed. If post-pandemic persistence applies to everything, the existing three-percent core would also fade more slowly than the SPF has it. That's a further upside risk our grid doesn't quantify. We'd rather say so than double it in."

**Do NOT say:** "Our post column is the note's full model."

**Real weakness?** **Yes (disclose).** Add one footnote to the grid. Quantifying it would need a new method and is out of scope.

### 11c. "Why the SPF and not the SEP, or Governor Bowman's 'closer to 2 percent next year'?"

**Steelman:**
- The SEP is the Committee's own number: 2027 median 2.5, central tendency 2.3–2.6 (A) [V].
- Bowman said: "my forecast is for core PCE inflation to move closer to 2 percent next year" (saved RTF) [O].
- Every one of our cells is at or above 2.40. Bowman gives a direction, not a number, so whether that is "above her" is interpretation, not a measured disagreement (R1 audit).

**Answer (57 words):** "The SEP gives annual numbers only. We need a quarterly path to apply quarterly oil dynamics, and the SPF publishes one, dated, with a dispersion band. The two agree closely: the SEP's 2027 median is 2.5, the SPF's 2.4. Governor Bowman gave a direction, closer to 2 percent, not a number; our pre-pandemic cells sit near 2.4."
- Sources: SEP 2.5 (A, coordinator-verified); SPF 2.40 (A); post P1/P2 above the SPF 2027 P75 of 2.727 (DQ; IQR from A's microdata, not coordinator-checked) [D].

**Do NOT say:**
- "The Committee's forecast is wrong."
- Don't characterise Bowman beyond her text.

**Real weakness?** **No (prepared answer).** Worth a spoken line: P1 × post (2.93) and P2 × post (3.16) sit above the SPF's 2027 75th percentile, and above the SEP central-tendency top of 2.6 [D].

---

## Three lines to memorize (all **PENDING Eli**)
1. "Under pre-pandemic pass-through, the oil shock barely touches 2027 core. Under post-pandemic, it adds about 0.3 to 0.8 points. The regime, not the oil path, is the bigger lever." (DEC; AX) **PENDING Eli**
2. "Our baseline is the August SPF, dated before the spike. We add the spike explicitly, and we never adjust published data." (C method) **PENDING Eli**
3. "With post-pandemic pass-through, oil would have to fall to about $60 and stay there to bring 2027 core back to 2.4." (DQ flat_breakeven post $60.37) **PENDING Eli** (new D number, not yet audited)

## Verbal-cue candidates (all **PENDING Eli**)
- "Scenarios, not probabilities." **PENDING Eli**
- "The regime is the lever." **PENDING Eli**
- "Dated before the spike." **PENDING Eli**
- "Low case and upper bound": pre-pandemic as the low case, post-pandemic as the authors' upper bound. **PENDING Eli**
- "Before any additional policy response." **PENDING Eli**
- "We don't adjust published data." **PENDING Eli**

## Worth a look
1. **Under post-pandemic dynamics the adjustment is mostly locked in.**
   - Flat Brent at the Nov 11 spot ($92.14) gives 2027 Q4/Q4 2.930, the same as P1 (2.927).
   - Getting back to the SPF's 2.40 needs about $60 flat, below the last pre-war close ($71.32, Feb 27) [D].
   - The oil-path axis under post therefore mostly reflects 2027 levels above about $90 (P2) vs reopening (P3).
2. **The Q4 rerun changes what the P1 row means** (gap ≈ 0 by construction). Decide the framing before Nov 16.
3. **Bowman's $110 sits below recent history.** Brent was ≥$110 every trading day Sep 10–Oct 31; the October mean was $123.93 [D]. "Oil rises again" means relative to $92 on Nov 11, not a new peak.
4. **Every 2026 number in our grid (3.09–3.14 Q4/Q4) is below every outside 2026 number.** SPF published 3.29, SEP 3.4, Oct-pace 3.33.
5. **The pre-pandemic Fig. 2 line can't be rebuilt from Table 2's 0.001 sum** (B Worth a look #1). If a judge has done the arithmetic: "we use the authors' published response table."
