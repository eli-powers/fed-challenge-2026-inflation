Status: Audited — converged R2

# Report D: outside October 2026 PCE estimates (R2 novel pull)

## Findings
- One new post-PPI named estimate: **Morgan Stanley, core ~0.3% m/m (rounded), 3.2% y/y** (brewmarkets.com, Judy Dutton, Nov 13, no time) [2]. "0.3%" in that article hyperlinks to thehill.com (not fetched).
- No open-web estimates found for JPMorgan, Wells Fargo, Citi, Barclays, Deutsche, UBS, Nomura, Jefferies, BNP, TD, Oxford, Pantheon post-PPI, Employ America, Bloomberg Economics. No Fed-official estimate dated Nov 14–18.
- **Independent named post-PPI estimates (existing file + new): 4** — Goldman 0.30, BofA 0.29, Capital Economics 0.29, Morgan Stanley ~0.30 (1 decimal). Median 0.295, range 0.29–0.30.
- Unnamed Reuters economists ~0.3 / 3.2 = consensus line, not an independent forecaster. UMD and Cleveland excluded from the count.
- Pre-PPI items listed, not counted: Inflation Insights (Sharif) ~0.34 (secondary blog, Nov 11); Pantheon 0.35–0.40 / 3.3 (Nov 10 note, repeated in Newsquawk weekly).
- Target of ~10 not reachable on the open web; likely sources (MNI, Newsquawk, Bloomberg, Reuters originals, Capital Economics, Employ America, Kalshi) in `outputs/D_paywalled.csv`.

## Worth a look (agent)
- Blog claim that Waller said core PCE was "on track for about a 0.34% gain in October": no outlet, date or transcript; not in Nov 10 speech. Unverified, excluded.
- Bowman 3.3% y/y is pre-PPI (Nov 10 speech), above the post-PPI 3.2–3.24 cluster.
- Post-PPI estimates cluster tightly (0.29–0.30); pre-PPI group sat 0.05–0.10 higher.
- WebFetch returns a model summary, not raw HTML; quotes saved as extracts in `03_Data/Raw/outside_oct_pce_estimates_2026-11-14/extracts.txt`.

## Spot-check examples (agent)
1. https://www.brewmarkets.com/stories/these-prices-could-torch-your-thanksgiving
2. https://www.wichitaliberty.org/economics/october-2026-cpi-report-inflation/
3. https://kelo.com/2026/11/13/us-producer-prices-rise-further-in-october/
4. Newsquawk week-in-focus 16–20 Nov (Pantheon)
5. https://pro.thestreet.com/market-commentary/headline-producer-prices-cool-but-core-hits-highest-annual-rate-since-2022

## Coordinator review
**Verified (independent fetch of live pages, Nov 14):**
- Morgan Stanley: page loads; text reads "Morgan Stanley economists are now expecting core PCE to rise by 0.3%" … "for October, with the annual inflation rate edging up to 3.2% from 3.1%." Author Judy Dutton, Nov 13, no time. Confirmed. The 0.3% links to The Hill, so the underlying press source is likely The Hill; not fetched.
- Reuters via KELO: "economists estimated that core PCE inflation rose 0.3% in October…"; "they forecast core PCE inflation advancing 3.2%". Confirmed. Page stamp "Nov 13, 2026 | 7:46 AM" has no timezone; KELO is a Sioux Falls (Central) station, and the story reports the PPI as released, so it is post-PPI (likely 8:46 ET). Flag: timezone inferred.
- Capital Economics via ASTIG: "he estimated core PCE will have risen 0.29 percent in October, lifting the annual rate to 3.2 percent". Confirmed; page shows only "1 day ago" — date inferred, secondary Philippine aggregator.
- Recomputed the median/range of the 4 named post-PPI core m/m (0.30, 0.29, 0.29, 0.30 treating MS as 0.30): median 0.295, range 0.29–0.30. UMD 0.295 → 0.0 bp from median. Note MS's 0.3 is 1-decimal; treating it as 0.30 is an assumption (it could be 0.25–0.34).

**Could not check:** Goldman/BofA original notes (TheStreet Pro is a press report); Sharif original; Waller 0.34 claim; Kalshi (429).

**Coordinator Worth a look:** every corroborating estimate is press-reported [2]; none is a primary note. The "corroboration line" rests on 4 secondary-sourced numbers, 1 of which is 1-decimal.

**Interpretive notes (not shared unless asked):** with n=4 and a 1bp range, "median and range" is thin; a footnote "n=4 named, post-PPI, press-reported" is the honest label.

**Post-audit (Codex R1 Worth a look, accepted):** Capital Economics upgraded to **primary**: its Nov 13 note's public intro (Thomas Ryan) reads "lowering our estimate for the monthly rise in the core deflator to 0.29% m/m" and "core PCE inflation is still likely to rise to 3.2%, from 3.1%". Re-fetched by coordinator; extract in `03_Data/Raw/capital_economics_ppi_note_2026-11-14/extract.md`; applied via `outputs/Z_outside_updates.csv`. Two-decimal-only median (excl. Morgan Stanley) = 0.290, n=3.
