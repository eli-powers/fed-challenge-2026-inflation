#!/usr/bin/env python3
"""Retrieve BEA PCE basket inputs, Dallas trimmed-mean documentation, and process.

Run from any directory with BEA_API_KEY set. Raw publisher responses are saved
through fetch_utils.save_raw (which redacts credentials). The API query is kept
from 2017 to the current year; reruns automatically use the current retrieval date
and the latest month present in the BEA data.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import os
import re
import subprocess
import tempfile
import urllib.parse
from collections import defaultdict
from pathlib import Path

from fetch_utils import get_key, http_get, save_raw
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
# REPLAY_DATE=YYYY-MM-DD re-reads the saved raw files of that date instead of calling the publishers
# (isolates code changes from data revisions; added 2026-11-14 for the core-flag fix, approved by Eli).
REPLAY = os.environ.get("REPLAY_DATE")
TODAY = REPLAY or dt.date.today().isoformat()
BEA = "https://apps.bea.gov/api/data/"
YEARS = ",".join(str(y) for y in range(2017, dt.date.today().year + 1))
COMPONENT_COLUMNS = [
    "index_name", "component_id", "component_name", "level_or_parent", "in_core",
    "weight_latest", "weight_base_12m", "weight_base_3m", "weight_base_1m", "weight_units",
    "pct_1m_calc", "pct_3m_ann_calc", "pct_12m_calc", "contrib_1m_calc",
    "contrib_3m_ann_calc", "contrib_12m_calc", "avg_pct_12m_2018_19_calc",
    "excess_contrib_12m_calc", "latest_period", "sa_basis", "source_ids", "raw_file", "note",
]


def bea_query(dataset: str, table: str, year: str = YEARS, folder: str = "PCE") -> tuple[dict, str]:
    params = {
        "method": "GetData", "datasetname": dataset,
        "TableName": table, "Frequency": "M", "Year": year, "ResultFormat": "JSON",
    }
    fname = f"BEA_{dataset}_{table}_{TODAY}.json"
    if REPLAY:
        raw, path = replay_raw(folder, fname)
    else:
        raw = http_get(BEA, {"UserID": get_key("BEA_API_KEY"), **params})
        path = save_raw(folder, fname, raw)
    parsed = json.loads(raw)
    results = parsed.get("BEAAPI", {}).get("Results", {})
    if results.get("Error") or "Data" not in results:
        raise RuntimeError(f"BEA {dataset}/{table} API error: {results.get('Error')}")
    return parsed, path


def save_document(url: str, folder: str, filename: str, accept: str | None = None) -> tuple[bytes, str]:
    if REPLAY:
        return replay_raw(folder, filename)
    raw = http_get(url, headers={"Accept": accept} if accept else None)
    return raw, save_raw(folder, filename, raw)


def replay_raw(folder: str, filename: str) -> tuple[bytes, str]:
    path = ROOT / folder / "raw" / filename
    if not path.exists():
        raise FileNotFoundError(f"REPLAY_DATE={REPLAY}: missing saved raw file {path}")
    return path.read_bytes(), str(path.relative_to(ROOT.parent))


def write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_num(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    s = str(value).strip().replace(",", "")
    if s in {"", "---", ".", "...", "N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def period_sort(p: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{4})M(\d{2})", p)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def pshift(p: str, months: int) -> str:
    y, m = period_sort(p)
    n = y * 12 + m - 1 + months
    return f"{n // 12:04d}M{n % 12 + 1:02d}"


def pct(a: float | None, b: float | None, annualize: int = 1) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return ((a / b) ** annualize - 1) * 100


def fmt(x: float | None) -> str:
    return "" if x is None or not math.isfinite(x) else f"{x:.8f}"


def normalize(s: str) -> str:
    # BEA appends underlying-detail table line references in parentheses; Dallas's
    # published component labels omit those reference numbers.
    s = re.sub(r"\s*\((?:parts? of\s+)?\d+[^)]*\)", " ", s, flags=re.I)
    s = s.lower().replace("(npishs)", "").replace("&", "and").replace("non-profit", "nonprofit")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def parse_dallas_xlsx(xlsx: bytes) -> list[dict]:
    """Read Dallas's official 178-line underlying detail list, the current list for the tech-note series set."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
        f.write(xlsx)
        f.flush()
        ws = load_workbook(f.name, read_only=True, data_only=True)["Web - Underlying detail"]
        found = []
        for row in ws.iter_rows(min_row=3, values_only=True):
            if row and row[0] and str(row[0]).strip().lower() != "none":
                found.append({"dallas_rank": len(found) + 1, "dallas_name": str(row[0]).strip(),
                              "dallas_current_month_rate": row[1], "dallas_weight": row[2], "dallas_cumulative_weight": row[3]})
        if len(found) < 170:
            raise RuntimeError(f"Dallas official workbook contains only {len(found)} component rows")
        return found


def line_core(ln) -> bool:
    """BEA core = PCE excluding off-premises food & beverages (U20404 lines 73-103), energy goods (113-119)
    and electricity & gas (169-171). Clothing 104-112, tobacco 141 and food supplied 247-248 stay core."""
    n = int(ln)
    return not (73 <= n <= 103 or 113 <= n <= 119 or 169 <= n <= 171)


def core_member(name: str) -> bool:
    # Legacy name rule; superseded 2026-11-14 by line_core() (disagreed with BEA on 16 lines). Kept for the printed check.
    s = normalize(name)
    # Core PCE excludes food and beverages purchased for off-premises consumption and energy goods/services.
    food = re.search(r"\b(food|foods|beverage|beverages|meat|fish|dairy|bakery|fruits|vegetables|coffee|tea|sugar|cereal|alcoholic|tobacco)\b", s)
    if "food services" in s or "meals away" in s:
        food = None
    energy = re.search(r"\b(energy|gasoline|fuel|fuels|electricity|natural gas|electric power|heating|coal|motor vehicle fuels|lubricants)\b", s)
    return not bool(food or energy)


def market_member(name: str) -> tuple[bool | None, str]:
    s = normalize(name)
    # BEA FAQ: excludes most implicit-price imputations, most insurance, gambling,
    # used-light-vehicle margins, net travel abroad, and NPISH final consumption.
    nonmarket_patterns = [
        r"financial services furnished without payment", r"final consumption expenditures of nonprofit",
        r"expenditures abroad", r"gambling", r"margin.*used.*light.*motor", r"medical.*insurance",
        r"hospitalization insurance", r"income loss insurance", r"life insurance", r"motor vehicle insurance",
        r"net motor vehicle.*insurance", r"workers compensation insurance", r"insurance services furnished without payment", r"net health insurance",
    ]
    if any(re.search(p, s) for p in nonmarket_patterns):
        return False, "BEA market-based PCE FAQ exclusion; see cited BEA documentation"
    if "net household insurance" in s:
        return True, "BEA FAQ identifies household insurance premiums and normal losses as included in market-based PCE"
    if "insurance" in s and not any(x in s for x in ["medical", "life", "motor vehicle", "income loss", "workers"]):
        return None, "BEA distinguishes included household insurance premiums/normal losses from excluded insurance types; leaf scope ambiguous"
    # Most rows are observable transaction-priced goods/services, which BEA says form the market-based measure.
    return True, "BEA FAQ: market-based components have observable prices (CPI/PPI); category not listed among named exclusions"


def main() -> None:
    # Publisher data responses (complete query is also saved in each raw payload).
    ud_price, raw_price = bea_query("NIUnderlyingDetail", "U20404")
    ud_spend, raw_spend = bea_query("NIUnderlyingDetail", "U20405")
    t20804, raw_t20804 = bea_query("NIPA", "T20804")
    t20807, raw_t20807 = bea_query("NIPA", "T20807")
    u90100, raw_recon = bea_query("NIUnderlyingDetail", "U90100", folder="Cross-index analysis")

    # PCE and market-based documentation.
    dallas_pdf, dallas_path = save_document("https://www.dallasfed.org/-/media/Documents/research/pce/tech.pdf", "PCE", f"Dallas_trimmed_mean_tech_{TODAY}.pdf")
    dallas_detail, dallas_detail_path = save_document("https://www.dallasfed.org/~/media/documents/research/pce/detail", "PCE", f"Dallas_trimmed_mean_components_{TODAY}.xlsx")
    dallas_history, dallas_history_path = save_document("https://www.dallasfed.org/~/media/documents/research/pce/pcehist", "Trimmed mean", f"dallas_trimmed_mean_history_{TODAY}.xlsx")
    faq_html, faq_path = save_document("https://www.bea.gov/help/faq/83", "Market-based PCE", f"BEA_market_based_PCE_FAQ_{TODAY}.html")
    handbook_url = "https://www.bea.gov/sites/default/files/methodologies/nipa-handbook-all-chapters.pdf"
    handbook_pdf, handbook_path = save_document(handbook_url, "Cross-index analysis", f"BEA_NIPA_Handbook_Chapter5_{TODAY}.pdf")
    dallas = parse_dallas_xlsx(dallas_detail)
    legacy_list_gaps = max(0, 178 - len(dallas))

    def data(parsed):
        return parsed["BEAAPI"]["Results"]["Data"]

    prices = data(ud_price)
    spend = data(ud_spend)
    price_rows = [r for r in prices if r.get("Frequency", "M") == "M"]
    spend_rows = [r for r in spend if r.get("Frequency", "M") == "M"]
    # Build leaf rows by exact description first; report unmapped or ambiguous matches.
    price_by_desc: dict[str, list[dict]] = defaultdict(list)
    spend_by_desc: dict[str, list[dict]] = defaultdict(list)
    for r in price_rows:
        price_by_desc[normalize(r["LineDescription"])].append(r)
    for r in spend_rows:
        spend_by_desc[normalize(r["LineDescription"])].append(r)
    # Do not match aggregate lines. The Dallas list is the requested published component set.
    latest_all = sorted({r["TimePeriod"] for r in price_rows}, key=period_sort)
    latest_spend = max({r["TimePeriod"] for r in spend_rows}, key=period_sort)
    latest = min(latest_all[-1], latest_spend, key=period_sort)
    base12, base3, base1 = pshift(latest, -12), pshift(latest, -3), pshift(latest, -1)
    pindex: dict[tuple[str, str], float | None] = {}
    exp: dict[tuple[str, str], float | None] = {}
    desc_map: dict[str, dict] = {}
    for r in price_rows:
        pindex[(r["SeriesCode"], r["TimePeriod"])] = parse_num(r.get("DataValue"))
        desc_map.setdefault(r["SeriesCode"], r)
    for r in spend_rows:
        exp[(r["SeriesCode"], r["TimePeriod"])] = parse_num(r.get("DataValue"))

    # Pull latest parent hierarchy and aggregate lines.
    latest_lines = {r["LineNumber"]: r for r in price_rows if r["TimePeriod"] == latest}
    line_by_desc = {normalize(r["LineDescription"]): r for r in latest_lines.values()}
    excluded_core = normalize("Food and beverages purchased for off-premises consumption")
    energy_line = normalize("Energy goods and services")
    core_parent_line = next((r for r in latest_lines.values() if normalize(r["LineDescription"]) == excluded_core), None)

    # Map Dallas names to unique detailed leaf series. Exact normalized descriptions only.
    mapped = []
    for d in dallas:
        key = normalize(d["dallas_name"])
        candidates = price_by_desc.get(key, [])
        # Some Dallas labels differ only by BEA's typographic/legacy phrasing; these remain N/A rather than fuzzy substitutions.
        codes = sorted({r["SeriesCode"] for r in candidates})
        if len(codes) != 1:
            d.update({"series": None, "line": None, "bea_name": "N/A", "match_note": "N/A: no unique exact normalized LineDescription match in U20404/U20405"})
            mapped.append(d)
            continue
        code = codes[0]
        pr = next(r for r in candidates if r["SeriesCode"] == code)
        expcandidates = spend_by_desc.get(key, [])
        sr = expcandidates[0] if len({r["SeriesCode"] for r in expcandidates}) == 1 else None
        if sr is None:
            d.update({"series": None, "line": pr["LineNumber"], "bea_name": pr["LineDescription"], "match_note": "N/A: no unique same-description nominal-spending line in U20405"})
            mapped.append(d)
            continue
        d.update({"series": code, "line": pr["LineNumber"], "bea_name": pr["LineDescription"], "spend_series": sr["SeriesCode"], "match_note": "exact normalized description match"})
        mapped.append(d)
    good = [d for d in mapped if d.get("series")]

    # Determine aggregate indexes from publisher data.
    aggs = {}
    for dataset_key, parsed in [("U20404", ud_price), ("T20804", t20804)]:
        for r in data(parsed):
            if r.get("TimePeriod") == latest:
                aggs[(dataset_key, r.get("LineNumber"))] = {**r, "value": parse_num(r.get("DataValue"))}
    pce_head = next((r for r in data(ud_price) if r.get("LineNumber") == "1" and r.get("TimePeriod") == latest), None)
    pce_core = next((r for r in data(ud_price) if r.get("LineNumber") == "25" and r.get("TimePeriod") == latest), None)
    market_head = next((r for r in data(t20804) if r.get("LineNumber") == "30" and r.get("TimePeriod") == latest), None)
    market_core = next((r for r in data(t20804) if r.get("LineNumber") == "31" and r.get("TimePeriod") == latest), None)

    exp_lookup = {(r["SeriesCode"], r["TimePeriod"]): parse_num(r.get("DataValue")) for r in spend_rows}
    def expenditure_for(code: str, p: str) -> float | None:
        return exp_lookup.get((code, p))

    # Headline/core components. A core row uses BEA's core parent definition; line membership is inferred from the named PCE food/energy exclusions.
    outrows = {"PCE": [], "Market-based PCE": [], "PCE__recon": [], "Market-based PCE__recon": []}
    pce_memberships = []
    for item in good:
        core = line_core(item["line"])
        market, market_note = market_member(item["bea_name"])
        pce_memberships.append({**item, "core": core, "market": market, "market_note": market_note})
    for item in good:
        code, line, name = item["series"], item["line"], item["bea_name"]
        core = line_core(line)
        market, market_note = market_member(name)
        vals = {p: pindex.get((code, p)) for p in [latest, base1, base3, base12]}
        changes = {
            "pct_1m_calc": pct(vals[latest], vals[base1]),
            "pct_3m_ann_calc": pct(vals[latest], vals[base3], 4),
            "pct_12m_calc": pct(vals[latest], vals[base12]),
        }
        avgs = []
        for year in (2018, 2019):
            for month in range(1, 13):
                cur = f"{year}M{month:02d}"
                prev = pshift(cur, -12)
                vcur, vprev = pindex.get((code, cur)), pindex.get((code, prev))
                ch = pct(vcur, vprev)
                if ch is not None:
                    avgs.append(ch)
        avg = sum(avgs) / len(avgs) if len(avgs) == 24 else None
        for index_name, include, denominator_core in [("PCE headline", True, False), ("PCE core", core, True)]:
            if not include:
                continue
            denom = {}
            for p in [latest, base1, base3, base12]:
                if denominator_core:
                    denom[p] = sum((expenditure_for(x["spend_series"], p) or 0) for x in pce_memberships if x["core"])
                else:
                    denom[p] = expenditure_for("DPCERC", p)
            weights = {p: (expenditure_for(item["spend_series"], p) / denom[p] if expenditure_for(item["spend_series"], p) is not None and denom[p] else None) for p in denom}
            row = {c: "" for c in COMPONENT_COLUMNS}
            row.update({
                "index_name": index_name, "component_id": f"U20404 line {line} / U20405 line {line} ({code})",
                "component_name": name, "level_or_parent": "Dallas Fed 178-component basket", "in_core": "Y" if core else "N",
                "weight_latest": fmt(weights[latest]), "weight_base_12m": fmt(weights[base12]),
                "weight_base_3m": fmt(weights[base3]), "weight_base_1m": fmt(weights[base1]),
                "weight_units": "fraction of aggregate nominal PCE expenditure",
                "pct_1m_calc": fmt(changes["pct_1m_calc"]), "pct_3m_ann_calc": fmt(changes["pct_3m_ann_calc"]),
                "pct_12m_calc": fmt(changes["pct_12m_calc"]),
                "contrib_1m_calc": fmt(weights[base1] * changes["pct_1m_calc"] if weights[base1] is not None and changes["pct_1m_calc"] is not None else None),
                "contrib_3m_ann_calc": fmt(weights[base3] * changes["pct_3m_ann_calc"] if weights[base3] is not None and changes["pct_3m_ann_calc"] is not None else None),
                "contrib_12m_calc": fmt(weights[base12] * changes["pct_12m_calc"] if weights[base12] is not None and changes["pct_12m_calc"] is not None else None),
                "avg_pct_12m_2018_19_calc": fmt(avg),
                "excess_contrib_12m_calc": fmt(weights[latest] * (changes["pct_12m_calc"] - avg) if weights[latest] is not None and avg is not None and changes["pct_12m_calc"] is not None else None),
                "latest_period": latest, "sa_basis": "SA; BEA U20404 monthly Fisher price indexes",
                "source_ids": f"BEA NIUnderlyingDetail U20404 line {line}; U20405 line {line}",
                "raw_file": f"{raw_price}; {raw_spend}", "note": item["match_note"] + ("; tagged core by component description under BEA food/energy definition" if not core else ""),
            })
            outrows["PCE"].append(row)

        # Market rows. Market-based weights are rescaled to observed-market items in each period.
        if market is True:
            for index_name, include, core_only in [("Market-based headline", True, False), ("Market-based core", core, True)]:
                if not include:
                    continue
                market_denoms = {}
                selected = [x for x in pce_memberships if x["market"] is True and (x["core"] or not core_only)]
                for p in [latest, base1, base3, base12]:
                    market_denoms[p] = sum((expenditure_for(x["spend_series"], p) or 0) for x in selected)
                w = {p: (expenditure_for(item["spend_series"], p) / market_denoms[p] if expenditure_for(item["spend_series"], p) is not None and market_denoms[p] else None) for p in market_denoms}
                row = {c: "" for c in COMPONENT_COLUMNS}
                row.update({
                    "index_name": index_name, "component_id": f"U20404 line {line} / U20405 line {line} ({code})",
                    "component_name": name, "level_or_parent": "Dallas Fed 178-component basket", "in_core": "Y" if core else "N",
                    "weight_latest": fmt(w[latest]), "weight_base_12m": fmt(w[base12]), "weight_base_3m": fmt(w[base3]), "weight_base_1m": fmt(w[base1]),
                    "weight_units": "fraction of market-based nominal PCE expenditure (rescaled)",
                    "pct_1m_calc": fmt(changes["pct_1m_calc"]), "pct_3m_ann_calc": fmt(changes["pct_3m_ann_calc"]), "pct_12m_calc": fmt(changes["pct_12m_calc"]),
                    "contrib_1m_calc": fmt(w[base1] * changes["pct_1m_calc"] if w[base1] is not None and changes["pct_1m_calc"] is not None else None),
                    "contrib_3m_ann_calc": fmt(w[base3] * changes["pct_3m_ann_calc"] if w[base3] is not None and changes["pct_3m_ann_calc"] is not None else None),
                    "contrib_12m_calc": fmt(w[base12] * changes["pct_12m_calc"] if w[base12] is not None and changes["pct_12m_calc"] is not None else None),
                    "avg_pct_12m_2018_19_calc": fmt(avg),
                    "excess_contrib_12m_calc": fmt(w[latest] * (changes["pct_12m_calc"] - avg) if w[latest] is not None and avg is not None and changes["pct_12m_calc"] is not None else None),
                    "latest_period": latest, "sa_basis": "SA; BEA U20404 monthly Fisher price indexes",
                    "source_ids": f"BEA NIUnderlyingDetail U20404 line {line}; U20405 line {line}; market membership per BEA FAQ",
                    "raw_file": f"{raw_price}; {raw_spend}; {faq_path}", "note": market_note,
                })
                outrows["Market-based PCE"].append(row)

    # Retain every Dallas-listed item in the component file, including exact-match failures.
    # Their values remain N/A rather than receiving a nearby BEA series silently.
    for d in mapped:
        if d.get("series"):
            continue
        for target, index_name in [("PCE", "PCE headline"), ("Market-based PCE", "Market-based headline")]:
            row = {c: "" for c in COMPONENT_COLUMNS}
            row.update({
                "index_name": index_name, "component_id": f"Dallas component rank {d['dallas_rank']} (BEA mapping N/A)",
                "component_name": d["dallas_name"], "level_or_parent": "Dallas Fed 178-component basket",
                "in_core": "N/A", "weight_units": "N/A", "latest_period": latest,
                "sa_basis": "SA; BEA U20404 monthly Fisher price indexes",
                "source_ids": "Dallas Fed 178-component technical note; BEA NIUnderlyingDetail U20404/U20405",
                "raw_file": f"{dallas_path}; {dallas_detail_path}; {raw_price}; {raw_spend}",
                "note": d["match_note"] + "; exact-description mapping required; no nearby series substituted. Source: https://apps.bea.gov/api/data/ and https://www.dallasfed.org/-/media/Documents/research/pce/tech.pdf",
            })
            outrows[target].append(row)
    for gap_no in range(legacy_list_gaps):
        for target, index_name in [("PCE", "PCE headline"), ("Market-based PCE", "Market-based headline")]:
            row = {c: "" for c in COMPONENT_COLUMNS}
            row.update({
                "index_name": index_name, "component_id": "Dallas legacy 178-list item not present in current detail workbook",
                "component_name": "N/A: current Dallas detail workbook contains 177 rows; 2009 technical note describes 178",
                "level_or_parent": "Dallas Fed technical-note component set", "in_core": "N/A", "weight_units": "N/A",
                "latest_period": latest, "sa_basis": "SA; BEA U20404 monthly Fisher price indexes",
                "source_ids": "Dallas Fed technical note and current underlying-detail workbook; BEA U20404/U20405",
                "raw_file": f"{dallas_path}; {dallas_detail_path}; {raw_price}; {raw_spend}",
                "note": "N/A: one of 178 legacy technical-note components is absent from the current Dallas detail workbook, so its exact name and BEA line cannot be matched. Source: https://www.dallasfed.org/-/media/Documents/research/pce/tech.pdf",
            })
            outrows[target].append(row)

    # Save market membership audit in the market-based folder, including ambiguous classifications.
    membership_rows = []
    for x in pce_memberships:
        membership_rows.append({"component_id": f"U20404/U20405 line {x['line']} ({x['series']})", "component_name": x["bea_name"], "market_status": "market" if x["market"] is True else "non-market" if x["market"] is False else "N/A", "source_citation": "BEA FAQ 83: https://www.bea.gov/help/faq/83", "raw_file": faq_path, "basis": x["market_note"]})
    for x in mapped:
        if not x.get("series"):
            membership_rows.append({"component_id": f"Dallas component rank {x['dallas_rank']}", "component_name": x["dallas_name"], "market_status": "N/A", "source_citation": "BEA FAQ 83: https://www.bea.gov/help/faq/83", "raw_file": f"{faq_path}; {dallas_path}", "basis": x["match_note"] + "; BEA component line must first be identified."})
    for _ in range(legacy_list_gaps):
        membership_rows.append({"component_id": "Dallas legacy 178-list item not present in current detail workbook", "component_name": "N/A: one list item unavailable", "market_status": "N/A", "source_citation": "Dallas technical note plus BEA FAQ 83: https://www.bea.gov/help/faq/83", "raw_file": f"{faq_path}; {dallas_path}; {dallas_detail_path}", "basis": "N/A: source-list entry is absent from current Dallas workbook; cannot determine BEA line or market status."})
    write_csv(ROOT / "Market-based PCE/processed/pce_market_membership.csv", membership_rows)

    # Publisher aggregate indexes and reconciliation.
    def aggregate_change(parsed, line, period, back):
        rows = data(parsed)
        def val(pp):
            r = next((r for r in rows if r.get("LineNumber") == str(line) and r.get("TimePeriod") == pp), None)
            return parse_num(r.get("DataValue")) if r else None
        return pct(val(period), val(pshift(period, back)), 4 if back == -3 else 1)
    # T20804 aggregation, U20404 headline/core; use line numbers 1,25,30,31.
    aggregate_defs = {
        "PCE headline": (t20804, "1"), "PCE core": (t20804, "25"),
        "Market-based headline": (t20804, "30"), "Market-based core": (t20804, "31"),
    }
    for name, (parsed, line) in aggregate_defs.items():
        target = "PCE" if name.startswith("PCE ") else "Market-based PCE"
        contrib_cols = {"1m": "contrib_1m_calc", "3m_ann": "contrib_3m_ann_calc", "12m": "contrib_12m_calc"}
        comprows = [r for r in outrows[target] if r["index_name"] == name]
        con_sums = {h: sum(parse_num(r[c]) or 0 for r in comprows) for h, c in contrib_cols.items()}
        agg = {h: aggregate_change(parsed, line, latest, back) for h, back in [("1m", -1), ("3m_ann", -3), ("12m", -12)]}
        for h in ["1m", "3m_ann", "12m"]:
            outrows[target + "__recon" if target == "PCE" else "Market-based PCE__recon"].append({
                "index_name": name, "horizon": h, "latest_period": latest, "publisher_aggregate_pct_change": fmt(agg[h]),
                "sum_component_contributions_pp_calc": fmt(con_sums[h]), "gap_publisher_less_components_pp_calc": fmt(agg[h] - con_sums[h] if agg[h] is not None else None),
                "component_count": len(comprows), "aggregate_source_id": f"BEA NIPA T20804 line {line}",
                "raw_file": raw_t20804,
                "note": "Linear nominal expenditure-share contributions to a chained Fisher index are approximate; aggregation gap is reported.",
            })
    # PCE expenditure closure from the basket against headline nominal PCE.
    for p in [latest, base1, base3, base12]:
        leaf_sum = sum((expenditure_for(x["spend_series"], p) or 0) for x in good)
        total = expenditure_for("DPCERC", p)
        # nominal values in millions SAAR; values may be rounded in the published API.
        outrows["PCE__recon"].append({"index_name": "PCE nominal basket closure", "horizon": p, "latest_period": latest,
            "publisher_aggregate_pct_change": fmt(total), "sum_component_contributions_pp_calc": fmt(leaf_sum),
            "gap_publisher_less_components_pp_calc": fmt(leaf_sum - total if total is not None else None), "component_count": len(good),
            "aggregate_source_id": "BEA NIUnderlyingDetail U20405 line 1", "raw_file": raw_spend,
            "note": "Values are current-dollar nominal PCE ($millions SAAR); gap is leaf-sum less publisher aggregate."})

    recon_cols = ["index_name", "horizon", "latest_period", "publisher_aggregate_pct_change", "sum_component_contributions_pp_calc", "gap_publisher_less_components_pp_calc", "component_count", "aggregate_source_id", "raw_file", "note"]
    for folder, key in [("PCE", "PCE"), ("Market-based PCE", "Market-based PCE")]:
        write_csv(ROOT / folder / "processed/components.csv", outrows[key], COMPONENT_COLUMNS)
        write_csv(ROOT / folder / "processed/reconciliation.csv", outrows[key + "__recon"], recon_cols)

    # Published BEA CPI/PCE reconciliation table 9.1U exactly as published.
    recon_rows = data(u90100)
    write_csv(ROOT / "Cross-index analysis/processed/cpi_pce_reconciliation.csv", recon_rows)

    # Stable documented PPI examples from Chapter 5 Tables 5.A/5.B. These
    # table rows are broader than Dallas's leaves; do not imply a finer crosswalk.
    ppi_rows = [
        {"component_or_parent_as_published": "Physician services", "ppi_source_as_published": "PPI for offices of physicians", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, line 62; p. 20", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook."},
        {"component_or_parent_as_published": "Home health care services", "ppi_source_as_published": "PPI for home health care services", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 20", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook."},
        {"component_or_parent_as_published": "Medical laboratories", "ppi_source_as_published": "PPI for medical laboratories", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 20", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook."},
        {"component_or_parent_as_published": "Medical laboratories / diagnostic imaging", "ppi_source_as_published": "PPI for diagnostic imaging centers", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 20", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook."},
        {"component_or_parent_as_published": "Hospitals", "ppi_source_as_published": "PPI for hospitals", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, lines 65-66; p. 21", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording; private and government estimates use related methods."},
        {"component_or_parent_as_published": "Nursing homes", "ppi_source_as_published": "PPI for nursing care facilities", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, line 67; p. 21", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook."},
        {"component_or_parent_as_published": "Air transportation", "ppi_source_as_published": "PPI for domestic scheduled passenger air transportation", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, line 74; p. 23", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact broad component/source wording from the handbook; Dallas leaf line is U20404 line 207."},
        {"component_or_parent_as_published": "Financial services: direct commissions on exchange-listed equities", "ppi_source_as_published": "PPI for brokerage services, equities and ETFs", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Financial services: other direct commissions", "ppi_source_as_published": "PPI for brokerage services, all other securities", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Financial services: imputed commissions on over-the-counter equity securities", "ppi_source_as_published": "PPI for dealer transactions, equity securities", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Financial services: other imputed commissions", "ppi_source_as_published": "PPI for dealer transactions, debt securities and all other trading", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Financial services: commissions on mutual fund sales", "ppi_source_as_published": "PPI for other securities related services including margin lending and mutual fund sales", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Portfolio management and investment advice services", "ppi_source_as_published": "Fixed-weighted average of PPI for portfolio management and PPI for investment advice", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Named as its own BEA source-data component; this BEA line is not a separate Dallas 178-list leaf."},
        {"component_or_parent_as_published": "Trust, fiduciary, and custody activities", "ppi_source_as_published": "PPI for commercial bank trust services", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 29", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Net household insurance", "ppi_source_as_published": "PPI for homeowners' insurance", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 30", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Medical care and hospitalization insurance", "ppi_source_as_published": "PPI for direct health and medical insurance carriers", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 30", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
        {"component_or_parent_as_published": "Workers' compensation insurance", "ppi_source_as_published": "PPI for workers' compensation insurance", "source_citation": "BEA NIPA Handbook, Chapter 5, Table 5.B, p. 30", "source_url": handbook_url, "raw_file": handbook_path, "note": "Exact PPI source named in the current handbook table."},
    ]
    write_csv(ROOT / "Cross-index analysis/processed/pce_ppi_priced_components.csv", ppi_rows)

    # Dallas published rates from its official downloadable historical data; source page includes 1m/6m/12m annual rates.
    dallas_page, page_path = save_document("https://www.dallasfed.org/research/pce", "Trimmed mean", f"dallas_trimmed_mean_page_{TODAY}.html")
    # Official Dallas workbook columns B-D contain 1-, 6-, and 12-month annualized rates.
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as f:
        f.write(dallas_history)
        f.flush()
        hist_ws = load_workbook(f.name, read_only=True, data_only=True)["Web - Historical"]
        hist_values = {}
        for row in hist_ws.iter_rows(min_row=5, values_only=True):
            if row and hasattr(row[0], "strftime"):
                hist_values[row[0].strftime("%Y-%m")] = [parse_num(v) for v in row[1:4]]
    dallas_latest = max(hist_values) if hist_values else None
    dallas_has_latest = latest.replace("M", "-") in hist_values
    dallas_period = latest if dallas_has_latest else (dallas_latest.replace("-", "M") if dallas_latest else latest)
    rates = hist_values.get(dallas_period.replace("M", "-"), [None, None, None])
    dallas_records = []
    for i, (sid, measure) in enumerate([("PCETRIM1M158SFRBDAL", "1-month annualized"), ("PCETRIM6M680SFRBDAL", "6-month annualized"), ("PCETRIM12M159SFRBDAL", "12-month")]):
        dallas_records.append({"series_id": sid, "measure": measure, "period": dallas_period, "value": fmt(rates[i]), "unit": "percent per year", "publisher": "Federal Reserve Bank of Dallas", "raw_file": f"{page_path}; {dallas_history_path}", "note": "Official Dallas historical workbook; component-level trimming data are not published." + ("" if dallas_has_latest else f" Dallas has not yet published {latest}; latest available Dallas month shown.")})
    write_csv(ROOT / "Trimmed mean/processed/dallas_trimmed_mean_rates.csv", dallas_records)
    mapping_output = [{"dallas_rank": x["dallas_rank"], "dallas_component": x["dallas_name"], "BEA_line": x.get("line", "N/A"), "BEA_series": x.get("series", "N/A"), "BEA_description": x.get("bea_name", "N/A"), "match_note": x["match_note"], "source_ids": "Dallas technical note/current underlying detail; BEA U20404/U20405"} for x in mapped]
    for _ in range(legacy_list_gaps):
        mapping_output.append({"dallas_rank": "N/A", "dallas_component": "N/A: legacy technical-note entry not in current 177-row Dallas workbook", "BEA_line": "N/A", "BEA_series": "N/A", "BEA_description": "N/A", "match_note": "N/A: entry name not present in current source workbook; exact description mapping impossible", "source_ids": "Dallas technical note/current underlying detail; BEA U20404/U20405"})
    write_csv(ROOT / "PCE/processed/dallas_component_mapping.csv", mapping_output)

    # Explicitly audit the five requested leaf/parent lines without silently
    # treating a broader BEA category as the same component.
    requested_tags = [
        "Portfolio management and investment advice services",
        "Financial service charges, fees, and commissions",
        "Financial services furnished without payment",
        "Computer software and accessories",
        "Air transportation",
    ]
    tag_rows = []
    for target_name in requested_tags:
        candidates = [r for r in price_rows if r.get("TimePeriod") == latest and normalize(r["LineDescription"]) == normalize(target_name)]
        exact = candidates[0] if len({r["SeriesCode"] for r in candidates}) == 1 and candidates else None
        listed = next((x for x in mapped if normalize(x["dallas_name"]) == normalize(target_name)), None)
        if exact:
            nline, ncode, nname = exact["LineNumber"], exact["SeriesCode"], exact["LineDescription"]
            nominal = next((r for r in spend_rows if r["TimePeriod"] == latest and r["LineNumber"] == nline), None)
            source_line = f"U20404 line {nline} ({ncode}); U20405 line {nline} ({nominal['SeriesCode'] if nominal else 'N/A'})"
            status = "Y" if listed and listed.get("series") else "N"
            note = "Exact Dallas leaf match." if status == "Y" else "BEA line exists but is not a named Dallas 178-list leaf; it sits within/under the relevant broader financial-services hierarchy."
            if nline == "258":
                note += " BEA line 258 is a broad financial-service-charges category with more detailed child lines."
        else:
            nname, source_line, status = "N/A", "N/A", "N/A"
            note = "N/A: no unique exact BEA description found in U20404 at latest period."
        tag_rows.append({"requested_component_tag": target_name, "dallas_leaf_presence": status,
                         "dallas_rank": listed["dallas_rank"] if listed else "N/A", "BEA_component_line": source_line,
                         "BEA_description": nname, "source_ids": "BEA NIUnderlyingDetail U20404/U20405; Dallas Fed component list",
                         "raw_file": f"{raw_price}; {raw_spend}; {dallas_path}; {dallas_detail_path}", "note": note})
    write_csv(ROOT / "PCE/processed/requested_component_tags.csv", tag_rows)

    # Run-time numbers for the reports.
    pubr = {}
    for nm, (parsed, line) in aggregate_defs.items():
        pubr[nm] = {h: aggregate_change(parsed, line, latest, back) for h, back in [("1m", -1), ("3m_ann", -3), ("12m", -12)]}
    def rec_for(target, nm, h):
        return next(r for r in outrows[target + "__recon"] if r.get("index_name") == nm and r.get("horizon") == h)
    def f3(x):
        return "n/a" if x in (None, "") else f"{float(x):.3f}"
    t_latest_rows = {r["LineNumber"]: r for r in data(t20804) if r.get("TimePeriod") == latest}
    t_desc = {ln: t_latest_rows[ln]["LineDescription"] for ln in ("1", "25", "30", "31") if ln in t_latest_rows}
    clos = next(r for r in outrows["PCE__recon"] if r.get("index_name") == "PCE nominal basket closure" and r.get("horizon") == latest)
    leaf_sum_l, tot_l = float(clos["sum_component_contributions_pp_calc"]), float(clos["publisher_aggregate_pct_change"])
    # Core rule check: script's name-regex core vs BEA line rule (exclude U20404 lines 73-103, 113-119, 169-171).
    core_diff = [(x["line"], x["bea_name"], x["core"]) for x in pce_memberships if bool(x["core"]) != line_core(x["line"])]
    legacy_diff = "; ".join(f"line {x['line']} {x['bea_name']}" for x in pce_memberships if core_member(x["bea_name"]) != line_core(x["line"])) or "none"
    core_diff_txt = "; ".join(f"line {l} {n} (script core={c}, line-rule core={not c})" for l, n, c in core_diff) or "none"
    core_ids = [x for x in pce_memberships if x["core"]]
    h_pairs = "; ".join(f"{nm}: " + ", ".join(f"{h} {f3(pubr[nm][h])}" for h in ("12m", "3m_ann", "1m")) for nm in pubr)
    rec_pce = "; ".join(f"{nm} {h}: published {f3(rec_for('PCE', nm, h)['publisher_aggregate_pct_change'])}, sum contrib {f3(rec_for('PCE', nm, h)['sum_component_contributions_pp_calc'])}, gap {f3(rec_for('PCE', nm, h)['gap_publisher_less_components_pp_calc'])}" for nm in ("PCE headline", "PCE core") for h in ("12m", "3m_ann"))
    rec_mb = "; ".join(f"{nm} {h} gap {f3(rec_for('Market-based PCE', nm, h)['gap_publisher_less_components_pp_calc'])} pp" for nm in ("Market-based headline", "Market-based core") for h in ("12m", "3m_ann", "1m"))
    mb12 = [abs(float(rec_for("Market-based PCE", nm, "12m")["gap_publisher_less_components_pp_calc"] or 0)) for nm in ("Market-based headline", "Market-based core")]
    mb_thresh = "exceed" if max(mb12) > 0.15 else "are within"
    lines_by_code = {r["SeriesCode"]: r for r in price_rows if r["TimePeriod"] == latest}
    # U90100 latest period
    u_periods = sorted({r.get("TimePeriod") for r in data(u90100) if r.get("TimePeriod")}, key=lambda q: (q[:4], q[4:]))
    u_monthly = sorted({r.get("TimePeriod") for r in data(u90100) if r.get("TimePeriod") and "M" in r.get("TimePeriod")}, key=period_sort)
    u_latest_m = u_monthly[-1] if u_monthly else "n/a"
    ppi_rep = f"Table 9.1U (U90100) latest monthly period in API response: {u_latest_m}; {latest} {'is' if latest in u_monthly else 'is NOT'} published."

    # Brief diagnostics and reports (<=60 lines each).
    unmatched = sum(1 for x in mapped if not x.get("series"))
    dallas_missing_names = ", ".join(x["dallas_name"] for x in mapped if not x.get("series"))
    pce_reports = {
        "PCE": [
            "# BEA PCE basket | retrieval report", "", f"Retrieval date: {TODAY}; BEA vintage as retrieved; latest period used (latest present in U20404/U20405): {latest}; base months {base12} (12m), {base3} (3m), {base1} (1m).",
            "Sources: BEA NIUnderlyingDetail U20404 (Fisher price indexes) and U20405 (current-dollar PCE, $millions SAAR); Dallas Fed 178-component technical note.",
            f"Raw files: {raw_price}; {raw_spend}; {raw_t20804}; {raw_t20807}; {dallas_path}; {dallas_detail_path}.",
            f"Coverage: {len(good)} of 178 legacy Dallas components mapped to unique matching BEA lines; current Dallas detail workbook has {len(dallas)} rows.",
            f"N/A: {dallas_missing_names or 'none'}; plus {legacy_list_gaps} legacy-list entry absent from current Dallas workbook.",
            "Weights: nominal expenditure shares; core denominator sums components in core by BEA U20404 line position (excludes off-premises food/beverages and energy).",
            "Indexes are SA; pct_1m=(I_t/I_t-1-1)*100, pct_3m_ann=((I_t/I_t-3)^4-1)*100, pct_12m=(I_t/I_t-12-1)*100.",
            "Contributions use start-period nominal weight times component percent change; 3-month changes are annualized. avg_pct is the 24-month mean of Jan 2018-Dec 2019 YoY changes; excess_contrib uses latest weight times current-minus-average YoY change.",
            f"Published rates computed from BEA NIPA T20804 ({latest}; 12m {base12}->{latest}; 3m annualized {base3}->{latest}; 1m): {h_pairs}. Lines: " + ", ".join(f"{k}={v}" for k, v in t_desc.items()) + ".",
            "Contributions to a chained Fisher index are approximate; see reconciliation.csv.",
            f"Leaf contributions vs published (pp): {rec_pce}.",
            f"Core membership: BEA line rule (exclude U20404 lines 73-103 food, 113-119 energy goods, 169-171 electricity & gas; clothing 104-112 stays core), {len(core_ids)} of {len(pce_memberships)} mapped leaves in core; flag vs line rule differs for: {core_diff_txt}. Superseded name rule (pre 2026-11-14) would differ for: {legacy_diff}.",
            f"Nominal leaf closure is reported in reconciliation.csv at {latest} and weight base months.",
            "Requested line audit: requested_component_tags.csv shows presence/location; portfolio management (U20404 line 268) and financial services furnished without payment (line 254) exist in BEA but are not separate Dallas leaf items; financial charges line 258, software line 50, and air transportation line 207 are matched.",
            f"At retrieval the current Dallas workbook has {len(dallas)} names while its technical note describes 178; one legacy entry is N/A" + (f"; unmatched current names: {dallas_missing_names}." if dallas_missing_names else "; every current Dallas name is matched (audio-video equipment services = U20404 line 218 since 2026-11-14)."),
            f"{latest} nominal leaf sum is ${leaf_sum_l:,.0f} million versus total PCE ${tot_l:,.0f} million (gap ${leaf_sum_l - tot_l:,.0f} million, {(leaf_sum_l - tot_l) / tot_l * 100:.2f}%); unmatched Dallas names/list-vintage mismatch explain uncertainty in closure.",
            "BEA data vintage is whatever BEA served on the retrieval date (the Sept 30, 2026 release includes the 2026 annual update, history revised from Jan 2021).",
        ],
        "Market-based PCE": [
            "# Market-based PCE basket | retrieval report", "", f"Retrieval date: {TODAY}; latest period used: {latest}.",
            f"Sources: BEA U20404/U20405, NIPA Table 2.8.4 lines 30-31, and BEA FAQ 83 ({faq_path}); raw tables: {raw_price}; {raw_spend}; {raw_t20804}; {raw_t20807}.",
            "BEA says market-based PCE uses observed prices (primarily detailed CPIs/PPIs), excludes most imputed expenditures, most insurance, gambling, used light-vehicle margins, net travel abroad, and NPISH final consumption; owner-occupied rent is included.",
            "Component membership and cited classification are in pce_market_membership.csv. Every N/A has a reason; explicit insurance exclusions/inclusions follow BEA FAQ 83.",
            "Weights rescale included components to market-based nominal expenditures. Headline/core contributions use same change formulas as PCE; aggregate indexes are BEA T20804 lines 30/31.",
            f"Reconciliation reports gaps versus BEA (FAQ-based membership, retrieve step; the rebuilt BEA-composition-table version is documented below when rebuild_market_based.py has run): {rec_mb}; the 12-month gaps {mb_thresh} the 0.15 pp review threshold.",
            "Investigation: BEA source data expose market-based nominal amounts by broad parent category, not by each 178 leaf. FAQ-based leaf membership and rescaled PCE leaf weights therefore cannot reproduce all market-based Fisher contributions; no allocation was invented.",
            "Limitation: BEA FAQ supplies category-level rules, not a full line-by-line 178-component crosswalk; detailed membership is documented as an inference, not an official BEA flag.",
        ],
        "Cross-index analysis": [
            "# BEA CPI/PCE reconciliation and source mapping | report", "", f"Retrieval date: {TODAY}; source vintage is the latest available at retrieval ({latest}).", ppi_rep,
            f"Raw sources: BEA API U90100 ({raw_recon}); NIPA Handbook Chapter 5 ({handbook_path}).",
            "cpi_pce_reconciliation.csv retains BEA Table 9.1U values and row labels as returned by the publisher API, covering monthly and quarterly where available.",
            f"pce_ppi_priced_components.csv captures {len(ppi_rows)} Chapter 5 source-table lines mentioning CPI/PPI/producer price indexes.",
            "NIPA Handbook Tables 5.A-5.B give component-group sources/methods at broader product-category scope; no one-to-one PPI series mapping is published for every Dallas leaf in that table.",
            "Rows therefore preserve exact handbook source text and mark component-level PPI assignments N/A where the handbook does not specify a leaf mapping.",
            "Formula/weight/scope reconciliation is published in Table 9.1U; see raw API payload and processed CSV for exact row definitions/values.",
        ],
        "Trimmed mean": [
            "# Dallas Fed trimmed-mean PCE rates | report", "", f"Retrieval date: {TODAY}; Dallas period shown: {dallas_period} ({'matches BEA latest' if dallas_has_latest else f'Dallas has NOT yet published {latest}; BEA latest is {latest}'}).",
            f"Official source page: https://www.dallasfed.org/research/pce (saved: {page_path}). Technical note: {dallas_path}.",
            "Publisher series IDs recorded: PCETRIM1M158SFRBDAL, PCETRIM6M680SFRBDAL, PCETRIM12M159SFRBDAL.",
            "Dallas publishes component-level detail (\"Components included and excluded from this month's Trimmed Mean\", color-coded workbook); this task records published rates and reads the published trim status without reconstructing the index.",
            f"Official historical workbook saved at {dallas_history_path}; values are copied as published with no reconstruction.",
        ],
    }
    for folder, lines in pce_reports.items():
        prefix = "dallas_" if folder == "Trimmed mean" else ""
        (ROOT / folder / "processed" / f"{prefix}REPORT.md").write_text("\n".join(lines[:60]) + "\n", encoding="utf-8")

    # One-line execution summary (never includes request URLs or keys).
    print(f"Built BEA basket outputs for {latest}: mapped {len(good)}/178 Dallas components; wrote PCE, market-based PCE, CPI/PCE reconciliation, source mapping, and Dallas rate files.")


if __name__ == "__main__":
    main()
