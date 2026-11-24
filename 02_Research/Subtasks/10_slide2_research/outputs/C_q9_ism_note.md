# Q9. ISM pricing-sentiment note (Cajner, Crane, Kurz, Soto & Vrankovich, FEDS Notes, Oct 1, 2026)

Source read in full: `02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-10-01_Cajner_pricing_sentiment_ISM.html` [O]; the Fed's "accessible version" page of the figures [O], saved in `03_Data/Raw/FedBoard_ISM_note_2026-11-15/`. DOI https://doi.org/10.17016/2380-7172.4191. Tags: [O] opened, [S] snippet only, [2] secondary.

## 1. What the index is [O]
**It is not a headline ISM diffusion index.** It is a Board-staff text-analysis construction from the free-text boxes of the ISM surveys. The note's own words: "a timely, granular measure of input cost pressures using text from Institute for Supply Management's (ISM) monthly surveys of manufacturing and services firms."
- **Data source.** ISM's monthly surveys of purchasing managers at manufacturing and services firms. The relevant fields are two free-text boxes, "prices going up" and "prices going down", accompanying the prices-paid question. Respondents can skip them; "text is provided in roughly a quarter to a third of responses." The authors thank ISM "for access to and help with the manufacturing and services survey data that underlie the work."
- **Construction.**
  1. Split each firm-month text into items on commas and semicolons.
  2. Map each item to one of "roughly fifty" PPI-like categories (energy, food and beverages, chemicals and materials, metals, housing and construction, high-tech products such as memory chips and processors, and others). Two methods: (1) unsupervised sentence embeddings (all-MiniLM-L6-v2) matched by cosine similarity to seed terms per category; (2) Claude Sonnet 4.5 reads each firm-month cell and assigns items via in-context learning. The note says the two give broadly similar results; its "preferred approach" is the generative-AI one.
  3. Count each firm-category pair as one mention. Net_{s,c,t} = Increases - Decreases, by sector s (manufacturing or services), category c, month t.
- **Coverage and frequency.** Monthly; the series "cover 2024-2026"; two sectors; about 50 categories plus an aggregate (all categories).
- **Timing.** "The manufacturing (services) report is released on the first (third) business day of the month... roughly two weeks before official price indices such as the Producer Price Index."
- **Units.** Net count of mentions (orange bars, right axis in the figures), not a percent or an index level. PPI comparisons are year-over-year percent changes.
- **Validation in the note (qualitative).** Figures 1-4 are charts only: oil (net mentions spike March 2026, ease by June, PPI petroleum turns down in June); ferrous metals (steady rise from early 2025, tracks the iron and steel PPI "less tightly"); high-tech; aggregate (peaks April 2026, declines in June; "tracks the year-over-year change in the final demand PPI closely"; the accessible text says the manufacturing index is highly correlated with PPI and "the services relationship is somewhat weaker"). No correlation coefficients, regressions or lead-lag statistics are reported. "Sometimes lead" is the note's own hedge: "the timing of the ISM price pressures sometimes lead the PPI data."

## 2. The "high-tech" variant Waller cites [O]
- The category is "high-tech products, predominantly memory chips and processors" (taxonomy); Figure 3 is labelled "Memory Chips (Manufacturing)" and "Memory Chips (Services)", generative-AI classification, compared with the y/y PPI for "semiconductors and other electronic components."
- Reading from the note's text: manufacturing index "rose in December 2025 and grew sharply in January 2026, remaining elevated through the present"; the PPI series "only rose in February 2026"; services shows "a similar pattern". Explanation offered: rising memory prices amid the AI buildout (high-bandwidth memory demand pulling capacity away from conventional DRAM and NAND).
- No monthly values are printed (the accessible version only describes the charts). Any number would have to be read off the chart image, which is not saved as data.

## 3. Is it publicly published? Not found; treat as unavailable
- **The note contains no data availability statement.** Text searches of the note body (Introduction through References) for "avail", "request", "replicat", "public", "download", "appendix", "upon", "posted" returned zero hits; links in the saved HTML to `/data.htm` and `/datadownload` are Fed site navigation, not note-specific. The Fed's accessible version describes charts in words and provides no table. **Status: no public series found; unconfirmed that none exists.**
- What the note does say about data: "PPI data was obtained via Haver Analytics" (fn 4, proprietary) and the ISM thanks above, which implies ISM supplied the underlying text to the Board. The ISM text boxes themselves are not shown to be public.
- **The ISM headline reports.** ISM publishes its Manufacturing and Services Reports on Business monthly. When I tried to read the ISM report page, the server redirected to a login page (`ecommerce.ismworld.org/SSO/Login.aspx`) and the public pages returned no readable content; logged in `C_paywalled.csv`. Whether the commodity-up/commodity-down lists are in the public part of each report is unverified.
- **Latest reading:** none available. The note's sample ends mid-2026 (Fig. 4 shows the decline "in June 2026"; the note is dated Oct 1). Waller's only statement on October is qualitative, below.

## 4. Waller's exact sentences (Nov 10, 2026, BoE Watchers speech; saved PDF, extracted with pypdf) [O]
> "In one exercise, researchers tried to capture imminent price pressures with a textual analysis of the well-known surveys of purchasing managers conducted by the Institute for Supply Management (ISM). ISM surveys ask purchasing managers to list specific commodities, materials, and services whose prices rose or fell that month. Staff used these responses to construct monthly price pressure indexes that correspond with actual categories of the producer price index (PPI). They found these indexes provide information about future changes in producer prices and, as a result, should have some signal about future PCE inflation. For example, the index for high-tech products rose in December 2025 and jumped further in January 2026, ahead of an escalation in those goods prices that eventually showed up in the February PPI and inflation data. The most recent ISM data, for October, point to the possibility of more price increases ahead."
- Earlier in the speech: "whether high-tech goods prices related to the AI buildout continue to rise at the very high rate of recent months."

**Gaps between Waller and the note.**
1. "inflation data": the note compares only with the PPI (semiconductors and other electronic components); it makes no comparison with PCE or CPI.
2. "should have some signal about future PCE inflation" is Waller's inference; the note says its series "support the use of the ISM price data not only as a signal for nowcasting, but also as a leading indicator of the direction and magnitude of price pressures" (of PPI).
3. "The most recent ISM data, for October": the note's sample ends before October; Waller is speaking from staff's updated reading, not from anything in the published note. Not verifiable from public sources. Timing: per the note, the October manufacturing report came out on the first business day of November and the services report on the third, i.e. before his Nov 10 speech.
4. Neither the note nor Waller gives a number for any ISM-based reading.

## 5. Usability for slide 2 (data, not a design)
- A cited external signal only; there is no data we can chart or reproduce. The note itself calls the series "sometimes" leading. It is public as a Fed Note (cite Waller and the note), not as a downloadable index.
- Use as context for "what staff and Waller are watching"; do not display numbers.
