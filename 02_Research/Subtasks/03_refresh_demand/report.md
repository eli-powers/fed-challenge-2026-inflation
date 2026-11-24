Status: Audited — converged R3 (Codex, 2026-11-10)

# 03 Refresh demand pipeline (Nov 10, 2026)

## Agent report (Sonnet 5.5)

### Findings
The fix plan and the Nov 10 refresh are both done. The live `demand_signals.xlsx` and `processed/` are rebuilt. 33 of 34 table rows moved to a new latest period (corrected after audit R1-F02). The exception is household net worth / disposable income (Fed Z.1, HNONWPDPI), which stays at Q2 2026 because no new release is out (Q3 due Dec, unverified). Archive: `demand_data/archive/pre_refresh_2026-11-10/`.

| Series (ID) | Old → new | New value | YoY | Short measure |
|---|---|---|---|---|
| Real info-processing equipment investment (BEA Y034RX, SAAR) | Q2 → Q3 adv. | 854.9 bil. ch.2017$ | +29.1% | Q/Q SAAR +37.4% |
| Real software (B985RX) | Q2 → Q3 | 985.7 | +12.8% | +9.6% |
| Real equipment total (Y033RX) | Q2 → Q3 | 1,675.9 | +14.1% | +20.9% |
| Real IP products total (Y001RX) | Q2 → Q3 | 1,796.4 | +9.3% | +8.4% |
| Real nonres. fixed investment (A008RX) | Q2 → Q3 | 4,106.9 | +8.4% | +12.7% |
| Data-center construction (Census C30, SAAR) | Aug → Sep | $96.5B | +80.3% (3m-avg) | 3m/3m ann +211.4%; 1-mo ann +169.4% |
| Data-center share of private nonres. construction | Aug → Sep | 12.2% | +5.6 pp | 3-mo +2.6 pp |
| Core capital goods orders (NEWORDER) | Aug → Sep | $88.2B | +13.7% | 3m +15.4% |
| Core capital goods shipments (ANXAVS) | Aug → Sep | $86.1B | +11.6% | 3m +16.7% |
| Computer & electronic orders / shipments (A34SNO / A34SVS) | Aug → Sep | 31.3 / 34.7 | +16.7% / +9.7% | 3m +9.7% / +4.4% |
| IP semiconductors (IPG3344S) | Aug → Sep | 198.6 | +19.9% | 3m +28.4% |
| Hyperscaler cash capex, sum of 4 (SEC XBRL, NSA) | Q2 → Q3 | $201.9B | +107.6% | trailing-4Q YoY +86.6% |
| Microsoft / Alphabet / Amazon / Meta | Q2 → Q3 | 39.4 / 51.4 / 77.3 / 33.9 | +103.0 / +114.4 / +120.1 / +80.3% | — |
| Real PCE total / goods / services (BEA T20806) | Aug → Sep | 17.0T / 5.8T / 11.2T | +2.5% each | 3m +3.8 / +3.0 / +4.1%; 1-mo ann +0.2 / −3.5 / +1.9% |
| Real disposable income (DSPIC96) | Aug → Sep | 18.4T | +1.0% | 3m +2.3%; 1-mo ann −3.2% |
| Personal saving rate (PSAVERT) | Aug 4.1 → Sep 3.8 | 3.8% | −1.3 pp | 3-mo −0.6 pp |
| Gasoline & energy goods share of PCE | Aug → Sep | 2.44% | +0.43 pp | 3-mo +0.20 pp |
| Retail & food services (RSAFS) | Aug → Sep | $745.0B | +6.3% | 3m +4.8% |
| Retail control group (computed) | Aug → Sep | $400.2B | +4.6% | 3m +4.3% |
| Gasoline stations (RSGASS) | Aug → Sep | $68.0B | +28.1% | 1-mo ann +109.7% |
| Revolving consumer credit (REVOLSL) | Jul → Sep | $1.37T | +4.25% | 3m +2.5% |
| Net worth / disposable income (HNONWPDPI) | Q2 → Q2 | 828% | +59.4 pp | Q/Q +47.1 pp |
| Michigan sentiment / current / expectations (ICS/ICC/ICE) | Sep → **Nov (preliminary)**; Oct final | Nov (P) 51.0 / 51.0 / 50.9; Oct final 48.0 / 46.7 / 48.8 | Nov y/y 0.0 / −0.1 / −0.1 | Nov 1-mo +3.0 / +4.3 / +2.1 |
| Conference Board confidence / present / expectations | Sep → Oct | 91.7 / 120.4 / 72.6 | n/a (no Oct 2025 row) | 1-mo +7.5 / +8.6 / +6.9 |

Raw files created: 55, all dated 2026-11-10 (list in `tmp/raw_files_created.txt`). No series failed. Revisions: 109 of 4,262 overlapping observations changed. Q2 2026 BEA investment components are unchanged. Census data-center construction Jul +2.2%, Aug +4.5%. Saving rate Jul 4.6 → 4.5, Aug 4.1 → 4.0. IP semis Aug 190.1 → 194.5. Conference Board Sep 81.9 → 84.2.

### Script edits (before → after in notes.md)
- `supplement_research.py`: all hand-entered Conference Board months are now in one transcription dict (Aug 2025, Sep 2025, May–Jul 2026, Aug 2026 revised, Sep 2026, Oct 2026). A reproduction check on the pre-refresh file reproduced all 24 existing CB rows. The 12 relative `raw_file` paths are normalized.
- `build_demand_signals.py`:
  - output-directory argument added;
  - the Sept 27 TLDR block removed from "Demand Signals", so the header is now row 2;
  - the existing TLDR sheet is carried forward verbatim, with the banner "As of Oct 2, 2026 (written before the Nov refresh; not updated by the build)";
  - freeze pane moved to B3;
  - the Michigan file is picked by newest date;
  - five Notes cells are computed at build time.
- Not changed in the initial refresh: `retrieve_official.py`, `retrieve_research.py`, `fetch_utils.py`. After audit R1: `retrieve_official.py` gained `michigan_current()` (Michigan preliminary month), and `supplement_research.py` syncs CB metadata (see Coordinator review).
- Still hand-typed and partly stale: the Michigan note (record low / "September final"), the Microsoft-break numbers, the capex-guidance note, and the Wealth note. The `GUIDANCE` URLs in `retrieve_research.py` still point to Q2 pages.

### Fix verification (gate before pulling)
The agent rebuilt on the unchanged processed data and diffed against the live workbook:
- **"Demand Signals":** 0 value differences, and the table CSV is byte-identical.
- **TLDR:** the banner row is the only change.
- **Notes:** B4, B18 and B22 are identical. B9 (BEA vintage) and B21 (CB months) differ in wording only; all their numbers match live.
- **Formatting:** the live file's header styling had been displaced by the hand deletion. The rebuild restores the script styling.

### Worth a look (agent)
- Hyperscaler capex Q3 $201.9B (Q2 $165.0B; +107.6% y/y). Real IPE grew 37.4% Q/Q SAAR after 7.6% in Q2; the last six quarters were 20.1, 15.3, 35.4, 38.8, 7.6, 37.4. The Q2 dip does not appear in capex.
- Conference Board expectations 72.6 in Oct, up from 65.7 (derived Sep revised). The threshold cited in the note is 80.
- Saving rate 3.8%, the lowest since Oct 2022. The post-2015 low is 2.4 (Jun 2022).
- Real PCE goods Sep 1-month annualized −3.5% against 3m +3.0%.
- Gasoline station sales +6.4% in one month (Aug → Sep).
- Data-center construction +8.6% m/m to $96.5B SAAR; Aug revised up 4.5%.
- In Oct, Michigan was flat (48.0) while the Conference Board rose 7.5.
- The Conference Board page scrape in `retrieve_research.py` failed again; the supplement covers it.

### Spot-checks (agent)
PSAVERT Sep 3.8 (FRED). RSAFS Sep 745,021 (FRED). Alphabet Q3 capex 51,355 from the 10-Q 9-month cash flow minus Q1 and Q2. Conference Board Oct release on PR Newswire, Oct 27: 91.7 / 120.4 / 72.6, and Sep revised 84.2.

### What to verify (agent)
- Sep Conference Board sub-index levels 111.8 / 65.7 are derived (level minus stated change); the release gives no revised sub-index levels.
- Michigan Oct final and Nov preliminary status.
- Microsoft, Amazon and Meta capex against their filings.
- BEA Q3 and Sep values against the BEA release pages.
- IP and consumer credit release dates.
- The stale hand-typed Notes lines and the `GUIDANCE` URLs: an owner decision.

## Coordinator review

**Verified:**
- **FRED, pulled Nov 10, vs `processed/`:** exact match for PSAVERT Sep 3.8 (Jul 4.5, Aug 4.0); RSAFS 745,021; DSPIC96 18,366.1; real PCE 16,977.6 (PCEC96 = DPCERX); IPG3344S 198.6335; NEWORDER 88,185; ANXAVS 86,125; REVOLSL 1,368,452.96; real equipment Y033RX Q3 1,675.883; HNONWPDPI Q2 828.48 (latest on FRED). FRED UMCSENT still ends at Sep 48.1, consistent with the old value. Oct 48.0 comes from the Michigan CSV and could not be cross-checked on FRED.
- **SEC capex,** from the saved companyfacts JSONs (10-Q facts):
  - Amazon Q3 77,259 (3-month fact, 10-Q filed Oct 30);
  - Meta 83,055 − 49,113 = 33,942 (10-Q filed Oct 22);
  - Microsoft Jul–Sep 39,367 (10-Q filed Oct 28);
  - Alphabet 131,953 − 80,598 = 51,355 (form 10-Q, filed Oct 29). This resolves the agent's open question on the Alphabet form type.
  - The sum, 201,923, matches.
- **Conference Board Oct,** from the saved release page text: 91.7 (+7.5 from Sep revised 84.2); Present Situation 120.4 (+8.6); Expectations 72.6 (+6.9).

**Corrected after Codex R1:** Michigan Nov preliminary ingested from the publisher's current tables, flagged in the table label (F01). Row count 33 of 34, software +12.8%, Aug data-center revision +4.5% (F02). Conference Board metadata now synced by `supplement_research.py` (latest Oct 2026, release 2026-10-27, SA on all rows); gasoline note computed (+28% y/y, Sep); capex guidance note dated "as of Q2 2026 statements" (Meta's Q3 guidance is $135–145B per Codex; left for Eli) (F03).

**Could not check:** the Census C30 data-center values (no FRED series; the agent's processed value comes from the saved xlsx). BEA IPE (Y034RX), software and IPP levels against BEA. The Michigan Oct indices against the publisher page.

**Coordinator worth a look:**
- The Conference Board calls the Sep revision 81.9 → 84.2 "a slight upward revision". 2.3 points is not slight by the usual standard. Our 81.9 Sep first print was hand-transcribed on Oct 2. Check it against the Sep 30 press release, or confirm the revision really was this large.
- The derived Sep sub-index levels (111.8 / 65.7) follow the existing pipeline convention but are not published numbers. Label them accordingly wherever they appear.
- The TLDR sheet is kept verbatim from Oct 2 and is now stale against the Nov data (banner added). Eli should decide whether to rewrite it.

**Interpretive notes (not shared unless asked):** capex and real IPE disagree on timing (the Q2 IPE dip has no counterpart in capex). That is plausible, given cash timing versus deliveries and imports, but it is a likely judge question.
