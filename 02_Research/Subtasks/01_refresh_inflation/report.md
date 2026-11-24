Status: Audited — converged R3 (Codex, 2026-11-10)

# 01 Refresh inflation pipeline (Nov 10, 2026)

## Agent report (Sonnet 5.5)

### Findings
The refresh is complete, and every series reaches its latest release. Archive: `03_Data/pipelines/inflation_data/archive/pre_refresh_2026-11-10/` (raw/, processed/, code/ copied). The BLS API returned HTTP 503 on the first run; the rerun succeeded. The agent's consistency check found 0 problems: metadata `latest_obs` matches the observations, `retrieval_date` is 2026-11-10 throughout, and no referenced raw file is missing. BEA `release_dates.csv` now covers Aug (2026-09-30) and Sep (2026-10-29) for all 6 series (from ALFRED).

| Group (series IDs) | Old → new latest | Release | Latest stored values |
|---|---|---|---|
| CPI-U all items (CUSR0000SA0 / CUUR0000SA0) | Aug → Oct 2026 | 2026-11-10 | SA m/m +0.4 (Oct); NSA 12m 3.7 (Sep); Oct SA index 337.476 |
| CPI-U core (CUSR0000SA0L1E / CUUR0000SA0L1E) | Aug → Oct | 2026-11-10 | SA m/m +0.3 (Oct); NSA 12m 2.6 (Sep); Oct SA index 339.900 |
| PPI final demand (WPSFD4 / WPUFD4) | Aug → Sep | 2026-10-15 | SA m/m +1.3; NSA 12m 6.3 |
| PPI trade services (WPSFD423) | Aug → Sep | 2026-10-15 | SA m/m +1.4; NSA 12m 4.7 |
| PPI personal-consumption trade (WPSFD42311) | Aug → Sep | 2026-10-15 | SA m/m +0.9; NSA 12m 4.5 |
| PPI intermediate processed (WPSID61) | Aug → Sep | 2026-10-15 | SA m/m +2.5; NSA 12m 14.1 |
| PPI intermediate unprocessed (WPSID62) | Aug → Sep | 2026-10-15 | SA m/m +8.4; NSA 12m 21.5 |
| PPI intermediate services (WPSID63) | Aug → Sep | 2026-10-15 | SA m/m +0.9; NSA 12m 6.3 |
| ECI civilian (CIS/CIU 1010/1020/1030) | Q2 → Q3 2026 | 2026-10-30 | Total comp: 3m SA 0.8, 12m NSA 3.4; wages 0.7 / 3.1; benefits 0.9 / 3.9 |
| ECI private (CIS/CIU 2010/2020/2030) | Q2 → Q3 | 2026-10-30 | Total comp 0.8 / 3.4; wages 0.8 / 3.1; benefits 0.9 / 3.9 |
| Productivity (PRS85006091-93) | Q2 → Q3 | 2026-11-05 (preliminary) | q/q annualized 3.6; y/y 2.1 |
| Unit labor costs (PRS85006111-13) | Q2 → Q3 | 2026-11-05 | q/q annualized −0.7; y/y 2.4 |
| Hourly compensation (PRS85006101-03) | Q2 → Q3 | 2026-11-05 | q/q annualized 2.9; y/y 4.5 |
| PCE (T20804 line 1) | Aug → Sep | 2026-10-29 | SA m/m +0.5; index 132.257 |
| Core PCE (line 25) | Aug → Sep | 2026-10-29 | SA m/m +0.3; index 130.902 |
| Market-based PCE / core (lines 30/31) | Aug → Sep | 2026-10-29 | m/m +0.5 / +0.3 |
| PCE services ex energy & housing (line 28) | Aug → Sep | 2026-10-29 | m/m +0.4 |
| PCE goods ex food & energy (U20404 l.375) | Aug → Sep | 2026-10-29 | index 112.310 (no published rate) |
| Dallas trimmed-mean PCE (FRED) | Aug → Sep | 2026-10-29 | 1m ann 2.84; 6m ann 2.42; 12m 2.26 |
| Cleveland trimmed-mean CPI | Aug → Oct | 2026-11-10 (ALFRED) | 12m 2.891; m/m 0.00369 (decimal); 1m ann 4.5 |
| Atlanta sticky CPI headline / core / ex shelter | Aug → Oct | 2026-11-10 | 12m 3.094 / 3.059 / 2.898; 3m ann 3.743 / 3.755 / 4.188 |
| NY Fed SCE median 1y / 3y / 5y | Aug → Oct | 2026-11-09 (NY Fed press release) | 3.914 / 3.288 / 3.000 |
| Michigan 12m / 5–10y medians | Sep → **Nov (preliminary)**; Oct final | Nov prelim released 2026-11-06 (SCA 2026 release calendar); final due Nov 20 | Nov (P) 4.3 / 3.4; Oct final 4.7 / 3.5 |
| Breakevens T5YIE / T10YIE / T5YIFR | Sep 25 → Nov 10 | daily | 2.25 / 2.20 / 2.15 |
| SPF | Q3 → Q3 | 2026-08-14 | Not updated: Q4 not yet released |

Gaps: SPF Q4 not out. *(Corrected after audit R1-F01: Michigan Nov preliminary is now ingested from the publisher's current table `tbcpx1px5.csv`, flagged preliminary.)* No Oct 2026 CPI 12-month rate, because Oct 2025 was never collected, so the latest y/y is Sep. Oct PPI not out.

### Script edits (logged before → after in notes.md)
- `retrieve_bls.py` l.414: productivity `latest_release` "2026-09-03" → "2026-11-05"; ll.99/473/482/486: Q2/Sept 3/ECI Jul 31 label strings → Q3/Nov 5/Oct 30.
- `retrieve_fed_expectations.py` l.71: the Atlanta link match also accepts `sticky-price-data.xlsx` (publisher renamed the file; same sheet and 25 headers). ~l.85: the SCE sheet list is now `[('Inflation expectations',('1','3','5'))]`, because the NY Fed folded the 5-year sheet into "Inflation expectations". Same statistic, same header match; no revisions to prior 5-year months.
- `supplement_fed_expectations.py` ~ll.166/174: Michigan "final"/vintage notes Sep → Oct.
- No edits to `retrieve_bea.py` or `fetch_utils.py`.

### Worth a look (agent)
- PPI unprocessed intermediate (WPSID62) Sep: +8.4 m/m SA, 21.5 y/y NSA; processed +2.5 / 14.1; final demand +1.3 / 6.3. Jul WPSID62 was revised 277.050 → 274.341.
- The Q3 productivity release revised history back to **2021Q1**, following BEA's Sept 30 annual NIPA update (BLS release, Revised measures; corrected after audit R1-F04). ULC 2026Q1 y/y 0.4 → 1.8; Q2 1.4 → 2.6; hourly comp 2026Q1 3m ann 2.1 → 5.1.
- Aug core PCE revised from +0.2 to +0.3 m/m (index 130.455 → 130.489).
- CPI headline m/m +0.6 Sep, +0.4 Oct; core 0.3 in Aug, Sep and Oct.
- Atlanta flexible-price CPI 1m annualized: 10.2 (Aug), 22.2 (Sep). Not investigated.

### Spot-checks (agent)
1. BLS CPI release (bls.gov/news.release/cpi.nr0.htm, Table A): Oct +0.4 / core +0.3; BLS cannot publish Oct 12-month changes.
2. BLS productivity release (prod2.nr0.htm): Q3 prelim Nov 5; 3.6 (2.1), ULC −0.7 (2.4), hourly comp 2.9 (4.5).
3. BEA PIO Sep 2026 release, Oct 29: PCE +0.5 / core +0.3 m/m.
4. FRED PCEPILFE: Sep 130.902, Aug 130.489.
5. UMich SCA: Nov preliminary posted; `tbmpx1px5.csv` ends Oct (4.7, 3.5).

### What to verify (agent)
Run core_ex_oer.py before the build. SCE 5-year column location stability. Whether to pull Michigan Nov preliminary. Michigan Oct release date blank until FRED loads it. Rerun before Nov 18 for the Q4 SPF and Oct PPI (due Nov 13). **Oct PCE is scheduled for Nov 25, after the Nov 18 cutoff** (BEA; corrected after audit R1-F05). SPF `latest_release_date` strings are hard-coded to Q3/2026-08-14. `inflation_data/README.txt` still describes the Sept–Oct pull.

Agent files: `notes.md`, `sources.md`, `code/refresh_check.py`, `code/out/` (latest_obs_summary, latest_values_by_horizon, revisions_since_2025-09).

## Coordinator review

**Verified (FRED API, pulled Nov 10, compared with `processed/`):**
- Latest index levels match exactly: CPIAUCSL Oct 337.476; CPILFESL Oct 339.900; PCEPI Sep 132.257; PCEPILFE Sep 130.902; PPIFIS Sep 159.780; WPSID62 Sep 299.868; OPHNFB Q3 121.922; ULCNFB Q3 124.393.
- Implied changes are consistent with the stored publisher rates: CPI +0.35 → published 0.4; core +0.30; PCE +0.49; core PCE +0.32; PPI FD +1.34; WPSID62 +8.37; productivity +3.55 annualized; ULC −0.66.
- ECIALLCIV Q3 y/y 3.37, consistent with the stored 3.4 (NSA CIU).
- Breakevens Nov 10: 2.25 / 2.20 / 2.15 match.
- The agent's "unverified" ULC revision claim is confirmed: current-vintage 2026Q1 y/y 1.82, Q2 2.57.

**Build and audit (run by coordinator):** `core_ex_oer.py` was run on the 2026-11-10 BEA vintage by the baskets agent. Validation: derived 376−153 vs published supercore, 12m 3.595 vs 3.596, 3m 3.366 vs 3.369. Then `build_workbook.py` (VALIDATION OK) → `audit_workbook.py`: **0 failures**. 16,564 full-history rates, 720 workbook rate cells and 1,327 non-price cells compared. The Snapshot now shows Oct CPI, Sep PCE/PPI, Q3 ECI/productivity, Oct Fed measures, and core ex OER Sep 12m 3.10 / m/m 0.31.

**Corrected after Codex R1:** Michigan Nov preliminary ingested (F01); SCE 5-year coverage now starts 2022-01 and Oct SCE release date 2026-11-09 recorded (F02); productivity revision reach and cause (F04); Oct PCE timing (F05). Rebuild + audit: 0 failures.

**Audit-script coverage (R1-F03):** `audit_workbook.py` independently checks arithmetic (rates, levels, derived index) but does not check release dates or the vintage/first-release rule against release evidence, and it compares Sources & Methods only to processed metadata. The 0-failure result clears the numbers, not the date labels.

**Could not check:** NY Fed SCE and Michigan values against the publisher pages (I relied on the agent's FRED cross-check, which has no Michigan Oct value yet). Atlanta flexible CPI readings. The cause of the productivity revision.

**Coordinator worth a look:**
- Snapshot CPI rows have a blank y/y for Oct (correct: no Oct 2025 collection). Anyone reading the Snapshot needs to know the latest CPI y/y is Sep (3.7 headline, 2.6 core).
- Two script edits follow publisher layout changes (Atlanta file name; NY Fed SCE sheet). These are not methodology changes, but they are the most likely place for a silent error. The auditor should confirm the 5-year SCE series is the same statistic.

**Interpretive notes (not shared unless asked):** the PPI pipeline readings (unprocessed +8.4 m/m) are the kind of upstream move that motivated the Sept energy-spillover question. Worth tying to the oil work and the FEDS oil note when Eli turns there.
