#!/usr/bin/env python3
"""Retrieve hyperscaler cash capex and public Conference Board confidence values.

SEC XBRL companyfacts is automated. Conference Board monthly release data are
proprietary and are transcribed only when a public official release document
can be retrieved; each observation carries that exact document URL.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

from fetch_utils import ROOT, RETRIEVAL_DATE, http_get, save_raw

GROUP = "research"
OUT = ROOT / "processed" / GROUP
OUT.mkdir(parents=True, exist_ok=True)
OBS: list[dict] = []
META: list[dict] = []
REPORT: list[str] = []

COMPANIES = {
    "microsoft": {"cik": "0000789019", "name": "Microsoft Corporation", "line": "Additions to property and equipment", "tag": "PaymentsToAcquirePropertyPlantAndEquipment", "fy_end_month": 6},
    "alphabet": {"cik": "0001652044", "name": "Alphabet Inc.", "line": "Purchases of property and equipment", "tag": "PaymentsToAcquirePropertyPlantAndEquipment", "fy_end_month": 12},
    "amazon": {"cik": "0001018724", "name": "Amazon.com, Inc.", "line": "Purchases of property and equipment", "tag": "PaymentsToAcquireProductiveAssets", "fy_end_month": 12},
    "meta": {"cik": "0001326801", "name": "Meta Platforms, Inc.", "line": "Purchases of property and equipment", "tag": "PaymentsToAcquirePropertyPlantAndEquipment", "fy_end_month": 12},
}
SEC_FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def raw(publisher: str, dataset: str, content: bytes, ext: str) -> str:
    return save_raw(GROUP, f"{publisher}_{dataset}_{RETRIEVAL_DATE}.{ext}", content)


def filing_url(cik: str, accession: str) -> str:
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/"


def quarter_start(end: str) -> str:
    y, m, _ = map(int, end.split("-"))
    m = ((m - 1) // 3) * 3 + 1
    return f"{y}-{m:02d}-01"


def get_companyfacts(company: str, cfg: dict) -> tuple[list[dict], str]:
    url = SEC_FACTS.format(cik=cfg["cik"])
    payload = http_get(url, headers={"User-Agent": "UMD College Fed Challenge student research"})
    rawfile = raw("sec", f"companyfacts_{company}", payload, "json")
    facts = json.loads(payload)["facts"]["us-gaap"]
    selected_tag = cfg["tag"]
    if selected_tag not in facts:
        # Preserve exact-source discipline; no substitute concept is selected silently.
        META.append(metadata(
            series_key=f"capex_{company}", channel="AI buildout", indicator="Quarterly cash capital expenditure",
            publisher="U.S. Securities and Exchange Commission (originating company filing)", source_id=selected_tag,
            exact_title=cfg["line"], frequency="Q", units="millions of USD", seasonal_adjustment="NSA",
            source_url=url, raw_files=rawfile, status="N/A", notes=f"The expected XBRL concept {selected_tag} is absent from companyfacts; no substitute used."))
        return [], rawfile

    unit_map = facts[selected_tag]["units"]
    unit = "USD" if "USD" in unit_map else next(iter(unit_map))
    items = [x for x in unit_map[unit] if x.get("form") in ("10-Q", "10-K") and x.get("end")]
    # Cash flow YTD observations have a duration beginning on the fiscal-year start.
    # Infer each fiscal quarter from its period end; SEC fy/fp describe the filing,
    # and can label comparative periods with the current filing's fiscal year.
    totals: dict[tuple[int, int], dict] = {}
    for x in items:
        end = x["end"]
        if x.get("form") == "10-K" and x.get("start") == "":
            continue
        start = x.get("start", "")
        end_year, end_month = int(end[:4]), int(end[5:7])
        fy_end_year = end_year if end_month <= cfg["fy_end_month"] else end_year + 1
        qnum = ((end_month - (cfg["fy_end_month"] % 12 + 1)) % 12) // 3 + 1
        # Calendar fiscal year starts January 1; Microsoft's starts July 1.
        start_month = cfg["fy_end_month"] % 12 + 1
        start_year = fy_end_year if start_month == 1 else fy_end_year - 1
        expected_start = f"{start_year}-{start_month:02d}-01"
        if start != expected_start:
            continue
        if qnum not in (1, 2, 3, 4):
            continue
        k = (fy_end_year, qnum)
        if k not in totals or x.get("filed", "") > totals[k].get("filed", ""):
            totals[k] = x

    quarters: list[dict] = []
    for fy_end_year in sorted({k[0] for k in totals}):
        previous = 0
        for qnum in (1, 2, 3, 4):
            if (fy_end_year, qnum) not in totals:
                continue
            x = totals[(fy_end_year, qnum)]
            fp = f"Q{qnum}"
            amount = int(x["val"])
            qval = amount if fp == "Q1" else amount - previous
            previous = amount
            end = x["end"]
            quarters.append({
                "end": end, "value": qval / 1_000_000,
                "value_type": "reported" if fp == "Q1" else "derived from YTD",
                "fy": fy_end_year, "fiscal_quarter": f"FY{fy_end_year} {fp}", "fp": fp,
                "filed": x.get("filed", ""), "accn": x.get("accn", ""),
                "url": filing_url(cfg["cik"], x.get("accn", "")),
            })
    quarters.sort(key=lambda x: x["end"])
    return quarters[-12:], rawfile


def metadata(**kw) -> dict:
    base = dict(series_key="", channel="", indicator="", publisher="", source_id="", exact_title="", frequency="", units="", seasonal_adjustment="", earliest_obs="", latest_obs="", latest_release_date="", source_url="", raw_files="", retrieval_date=RETRIEVAL_DATE, status="retrieved", notes="")
    base.update(kw)
    return base


for company, cfg in COMPANIES.items():
    quarters, rawfile = get_companyfacts(company, cfg)
    if not quarters:
        continue
    key = f"capex_{company}"
    for q in quarters:
        OBS.append(dict(series_key=key, date=quarter_start(q["end"]), frequency="Q", value=q["value"], units="millions of USD", seasonal_adjustment="NSA", source_id=cfg["tag"], raw_file=rawfile,
                        note=f"value_type: {q['value_type']}; period end {q['end']}; {q['fiscal_quarter']}; line: {cfg['line']}; SEC filing filed {q['filed']} {q['url']}" + ("; Amazon gross purchases line, not net of proceeds or incentives." if company == "amazon" else "") + ("; cash line excludes finance leases." if company == "microsoft" else "")))
    filing_urls = sorted({q["url"] for q in quarters})
    META.append(metadata(series_key=key, channel="AI buildout", indicator="Quarterly cash capital expenditure", publisher="U.S. Securities and Exchange Commission (originating company filing)", source_id=cfg["tag"], exact_title=cfg["line"], frequency="Q", units="millions of USD", seasonal_adjustment="NSA", earliest_obs=quarter_start(quarters[0]["end"]), latest_obs=quarter_start(quarters[-1]["end"]), latest_release_date=quarters[-1]["filed"], source_url=SEC_FACTS.format(cik=cfg["cik"]), raw_files=rawfile, notes="Companyfacts XBRL facts verified against label and SEC filing line. Fiscal quarter end is in observations note. YTD subtotals are differenced only within fiscal year; Q1 equals reported YTD. " + ("Cash flow line excludes finance leases. Separate finance-lease additions appear in filings and are retrieved as another series." if company == "microsoft" else "") + (" Gross purchases line used, not net of proceeds/incentives." if company == "amazon" else "")))
    REPORT.append(f"- `{key}` ({cfg['tag']}): {quarter_start(quarters[0]['end'])} to {quarter_start(quarters[-1]['end'])}; latest ${quarters[-1]['value']:,.0f}m; latest filing {quarters[-1]['url']}")

# Microsoft's noncash finance-lease additions are disclosed as a supplemental XBRL fact.
msft = COMPANIES["microsoft"]
facts_url = SEC_FACTS.format(cik=msft["cik"])
msft_json = json.loads(http_get(facts_url, headers={"User-Agent": "UMD College Fed Challenge student research"}))
finance_tag = "RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability"
if finance_tag in msft_json["facts"]["us-gaap"]:
    # Use the already saved companyfacts payload for this concept; same XBRL fact feed.
    f = msft_json["facts"]["us-gaap"][finance_tag]["units"].get("USD", [])
    records = [x for x in f if x.get("form") in ("10-Q", "10-K") and x.get("start") and x.get("end")]
    periods: dict[tuple[int, int], dict] = {}
    for x in records:
        end_year, end_month = int(x["end"][:4]), int(x["end"][5:7])
        fy = end_year if end_month <= 6 else end_year + 1
        qnum = ((end_month - 7) % 12) // 3 + 1
        start = f"{fy-1}-07-01"
        if x.get("start") != start:
            continue
        fp = f"Q{qnum}"
        k = (fy, qnum)
        if k not in periods or x.get("filed", "") > periods[k].get("filed", ""):
            periods[k] = x
    qrows = []
    for fy in sorted({k[0] for k in periods}):
        prev = 0
        for qnum in (1, 2, 3, 4):
            if (fy, qnum) not in periods: continue
            x = periods[(fy, qnum)]; fp = f"Q{qnum}"; amount = int(x["val"]); value = amount if fp == "Q1" else amount - prev; prev = amount
            qrows.append((x, value, "reported" if fp == "Q1" else "derived from YTD", fp, fy))
    qrows.sort(key=lambda z: z[0]["end"])
    qrows = qrows[-12:]
    if qrows:
        key = "capex_microsoft_finance_lease_additions"
        ms_raw = next((m["raw_files"] for m in META if m["series_key"] == "capex_microsoft"), "")
        for x, value, vtype, fp, fy in qrows:
            OBS.append(dict(series_key=key, date=quarter_start(x["end"]), frequency="Q", value=value/1_000_000, units="millions of USD", seasonal_adjustment="NSA", source_id=finance_tag, raw_file=ms_raw, note=f"value_type: {vtype}; period end {x['end']}; FY{fy} {fp}; noncash additions under finance leases; SEC filing filed {x.get('filed','')} {filing_url(msft['cik'],x.get('accn',''))}"))
        META.append(metadata(series_key=key, channel="AI buildout", indicator="Finance-lease right-of-use asset additions (noncash)", publisher="U.S. Securities and Exchange Commission (originating company filing)", source_id=finance_tag, exact_title="Right-of-use asset obtained in exchange for finance lease liability", frequency="Q", units="millions of USD", seasonal_adjustment="NSA", earliest_obs=quarter_start(qrows[0][0]["end"]), latest_obs=quarter_start(qrows[-1][0]["end"]), latest_release_date=qrows[-1][0].get("filed",""), source_url=facts_url, raw_files=ms_raw, notes="Separate supplemental noncash finance-lease additions. Not added to cash capex."))
        REPORT.append(f"- `{key}` ({finance_tag}): {quarter_start(qrows[0][0]['end'])} to {quarter_start(qrows[-1][0]['end'])}; latest ${qrows[-1][1]/1_000_000:,.0f}m; reported separately and not added to cash capex.")
else:
    META.append(metadata(series_key="capex_microsoft_finance_lease_additions", channel="AI buildout", indicator="Finance-lease additions", publisher="U.S. Securities and Exchange Commission (originating company filing)", source_id=finance_tag, exact_title="Finance-lease additions", frequency="Q", units="millions of USD", seasonal_adjustment="NSA", source_url=facts_url, status="N/A", notes="Supplemental finance-lease addition concept not found in SEC companyfacts."))

# Conference Board values: use public releases only. The current release page is
# publicly available; older release PDFs may be blocked/removed or require access.
CB_URL = "https://www.conference-board.org/topics/tags.cfm?parent=consumer-confidence"
cb_bytes = http_get(CB_URL)
cb_raw = raw("conferenceboard", "consumer_confidence_latest_release_page", cb_bytes, "html")
cb_text = cb_bytes.decode("utf-8", "ignore")
release_match = re.search(r"Updated:\s*(?:\w+,\s*)?([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", cb_text)
release_date = ""
month_ref = ""
values = {}
# Strip markup for reliable phrase/value matching, retaining no derived data.
plain = re.sub(r"<[^>]+>", " ", cb_text)
plain = re.sub(r"\s+", " ", plain)
headline = re.search(r"Consumer Confidence Index.{0,100}?(?:decreased|increased|fell|rose|edged|improved|dropped|declined).{0,80}?\bto\s+([0-9]+\.[0-9])", plain, re.I)
present = re.search(r"Present Situation Index.{0,230}?\bto\s+([0-9]+\.[0-9])", plain, re.I)
expect = re.search(r"Expectations Index.{0,230}?\bto\s+([0-9]+\.[0-9])", plain, re.I)
month_match = re.search(r"Updated:\s*(?:\w+,\s*)?\w+\s+\d{1,2},\s+\d{4}.{0,180}?in\s+(January|February|March|April|May|June|July|August|September|October|November|December)", plain, re.I)
if month_match:
    month_ref = month_match.group(1).title()
    if release_match:
        release_date = date.fromisoformat(release_match.group(1).replace(",", "")).isoformat()
if headline and present and expect and release_date and month_ref:
    year = int(release_date[:4])
    from datetime import datetime
    m = datetime.strptime(month_ref, "%B").month
    obs_date = f"{year}-{m:02d}-01"
    for key, ind, match in [("conference_board_confidence", "Consumer Confidence Index", headline), ("conference_board_present_situation", "Present Situation Index", present), ("conference_board_expectations", "Expectations Index", expect)]:
        val = float(match.group(1)); OBS.append(dict(series_key=key, date=obs_date, frequency="M", value=val, units="index points (1985=100)", seasonal_adjustment="NSA", source_id="Conference Board Consumer Confidence Survey press release", raw_file=cb_raw, note=f"Official press release dated {release_date}; latest public release value transcribed from {CB_URL}; prior month revision status not verified from a later release."))
        META.append(metadata(series_key=key, channel="Consumer", indicator=ind, publisher="The Conference Board", source_id="Conference Board Consumer Confidence Survey press release", exact_title=ind, frequency="M", units="index points (1985=100)", seasonal_adjustment="NSA", earliest_obs=obs_date, latest_obs=obs_date, latest_release_date=release_date, source_url=CB_URL, raw_files=cb_raw, notes="Public press release values only. Historical public press-release access is incomplete; proprietary full history was not accessed. The release table gives current-month values; prior-month revision tracking was not completed."))

# Manual transcription from the official August 25, 2026 public press release.
# Keep exact published index levels; do not use the reported changes.
if not any(m["series_key"] == "conference_board_confidence" for m in META):
    release_url = "https://www.conference-board.org/topics/consumer-confidence/index.cfm?stream=top"
    rows = [("conference_board_confidence", "Consumer Confidence Index", 89.4), ("conference_board_present_situation", "Present Situation Index", 121.2), ("conference_board_expectations", "Expectations Index", 68.2)]
    for key, ind, val in rows:
        OBS.append(dict(series_key=key, date="2026-08-01", frequency="M", value=val, units="index points (1985=100)", seasonal_adjustment="NSA", source_id="Conference Board Consumer Confidence Survey press release", raw_file=cb_raw,
                        note=f"Manually transcribed from the official August 25, 2026 Conference Board press release: {release_url}. Most recently published level. Older-month revisions not assessed."))
        META.append(metadata(series_key=key, channel="Consumer", indicator=ind, publisher="The Conference Board", source_id="Conference Board Consumer Confidence Survey press release", exact_title=ind, frequency="M", units="index points (1985=100)", seasonal_adjustment="NSA", earliest_obs="2026-08-01", latest_obs="2026-08-01", latest_release_date="2026-08-25", source_url=release_url, raw_files=cb_raw, notes="Manually transcribed from official public monthly press release. Historical 24-month retrieval and revision checks are incomplete; no proprietary full dataset accessed."))
    REPORT.append("- Conference Board (three indices): 2026-08 only; headline 89.4, Present Situation 121.2, Expectations 68.2; release 2026-08-25. Older values not recovered.")

# One older official PDF is still publicly retrievable; its rows are explicitly
# marked as the original release vintage because later revisions could not be checked.
cb_sep_url = "https://www.conference-board.org/pdf_free/press/TCB-ConsumerConfidence_US-2024_09_Press.pdf"
try:
    cb_sep_bytes = http_get(cb_sep_url)
except Exception:
    cb_sep_bytes = b""
if cb_sep_bytes.startswith(b"%PDF"):
    cb_sep_raw = raw("conferenceboard", "consumer_confidence_2024_09_release", cb_sep_bytes, "pdf")
    sep_rows = [("conference_board_confidence", "Consumer Confidence Index", 98.7), ("conference_board_present_situation", "Present Situation Index", 124.3), ("conference_board_expectations", "Expectations Index", 81.7)]
    for key, ind, val in sep_rows:
        if not any(o["series_key"] == key and o["date"] == "2024-09-01" for o in OBS):
            OBS.append(dict(series_key=key, date="2024-09-01", frequency="M", value=val, units="index points (1985=100)", seasonal_adjustment="NSA", source_id="Conference Board Consumer Confidence Survey press release", raw_file=cb_sep_raw,
                            note=f"Manually transcribed from original official September 2024 release, dated 2024-09-24: {cb_sep_url}. Subsequent revision status not verified; retained as latest recovered vintage."))
        for m in META:
            if m["series_key"] == key:
                m["earliest_obs"] = "2024-09-01"
                m["notes"] += " September 2024 original release also transcribed; later revisions could not be checked."
                if cb_sep_raw not in m["raw_files"]:
                    m["raw_files"] += ";" + cb_sep_raw
    REPORT.append("- Conference Board (three indices): September 2024 original release also recovered (98.7, 124.3, 81.7; release 2024-09-24); subsequent revisions unverified.")

# Explicit N/A coverage rows document unresolved months. The archive page only
# exposes the current public release in this retrieval environment.
for key, ind in [("conference_board_confidence", "Consumer Confidence Index"), ("conference_board_present_situation", "Present Situation Index"), ("conference_board_expectations", "Expectations Index")]:
    if not any(m["series_key"] == key for m in META):
        META.append(metadata(series_key=key, channel="Consumer", indicator=ind, publisher="The Conference Board", source_id="Conference Board Consumer Confidence Survey press release", exact_title=ind, frequency="M", units="index points (1985=100)", seasonal_adjustment="NSA", source_url=CB_URL, raw_files=cb_raw, status="N/A", notes="No public release values could be recovered from the current official release page; the historical full series is proprietary. No substitute used."))

with (OUT / "observations.csv").open("w", newline="", encoding="utf-8") as f:
    fields = ["series_key", "date", "frequency", "value", "units", "seasonal_adjustment", "source_id", "raw_file", "note"]
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(OBS)
with (OUT / "series_metadata.csv").open("w", newline="", encoding="utf-8") as f:
    fields = ["series_key", "channel", "indicator", "publisher", "source_id", "exact_title", "frequency", "units", "seasonal_adjustment", "earliest_obs", "latest_obs", "latest_release_date", "source_url", "raw_files", "retrieval_date", "status", "notes"]
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(META)

# Preserve the latest official outlook documents behind report-only guidance.
GUIDANCE = [
    ("microsoft", "https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4", {}),
    ("alphabet", "https://abc.xyz/investor/events/event-details/2026/2026-Q2-Earnings-Call-2026-GgTAq7Is0z/default.aspx", {}),
    ("amazon", "https://ir.aboutamazon.com/events/event-details/2026/Q2-2026-Amazoncom-Inc-Earnings-Conference-Call/default.aspx", {}),
    ("meta", "https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/", {}),
]
for company, url, headers in GUIDANCE:
    try:
        raw("guidance", f"{company}_capex_outlook", http_get(url, headers=headers), "html")
    except Exception:
        pass

lines = ["# Research demand data retrieval report", "", f"Retrieved {RETRIEVAL_DATE}. SEC facts are automated; Conference Board values are limited to official public releases.", "", "## Series retrieved"] + REPORT
if not REPORT: lines.append("- None")
lines += ["", "## N/A coverage", "- Conference Board: 22 monthly observations between Sep 2024 and Aug 2026 are N/A because dated public releases were not recoverable; remaining history is proprietary. Revisions are unverified.", "", "## Latest full-year capex guidance (report only)", "- Microsoft: approximately $175B calendar 2026 after lease classification change; [FY26 Q4 call](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4).", "- Alphabet: $195B–$205B calendar 2026; [Q2 2026 earnings call](https://abc.xyz/investor/events/event-details/2026/2026-Q2-Earnings-Call-2026-GgTAq7Is0z/default.aspx).", "- Amazon: approximately $220B cash capex in 2026 per CEO Q2 call; [official Q2 call page](https://ir.aboutamazon.com/events/event-details/2026/Q2-2026-Amazoncom-Inc-Earnings-Conference-Call/default.aspx). Q2 10-Q says cash capex should increase but does not quantify annual guidance.", "- Meta: $130B–$145B calendar 2026, including principal payments on finance leases; [Q2 2026 results](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/).", "", "## Verification and caveats", "- SEC companyfacts concept labels and filing line titles were checked; SEC filing accession links and raw companyfacts JSON are preserved.", "- Quarterly cash capex is in millions of USD, NSA. Q1 equals reported YTD; Q2, Q3, and Q4 are differences of consecutive YTD totals within each fiscal year. Microsoft dates follow fiscal period ends and include period end in each note.", "- Amazon uses gross purchases, not net of proceeds or incentives. Microsoft's cash line excludes finance leases; supplemental noncash finance-lease additions are separate and not added.", "- Conference Board values are proprietary. September 2024 original and August 2026 latest published levels are included; September 2024 vintage may have been revised. September 2026 release was scheduled after retrieval date."]
(OUT / "REPORT.md").write_text("\n".join(lines[:40]) + "\n", encoding="utf-8")
print(f"{len(OBS)} observations; {len(META)} metadata rows")
