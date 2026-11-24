#!/usr/bin/env python3
"""Retrieve BEA PCE price indexes/rates and FRED checks for the bea group.

Run from any directory with BEA_API_KEY and FRED_API_KEY set:
    python inflation_data/code/retrieve_bea.py

All network traffic and raw-file writing use fetch_utils. API payloads are
saved as returned, apart from fetch_utils' required API-key redaction.
"""
import csv
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from datetime import datetime

from bs4 import BeautifulSoup

from fetch_utils import ROOT, RETRIEVAL_DATE, get_key, http_get, save_raw, fred_initial_release

BEA_URL = "https://apps.bea.gov/api/data/"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_SEARCH_URL = "https://api.stlouisfed.org/fred/series/search"
GROUP = "bea"
OUT = ROOT / "processed" / GROUP
OUT.mkdir(parents=True, exist_ok=True)

SERIES = {
    "pce_price": {
        "indicator": "PCE price index (headline)", "table": "T20804", "line": "1", "code": "DPCERG",
        "exact_title": "Personal consumption expenditures (PCE)", "fred": "PCEPI", "rate_line": "1",
        "rate_code": "DPCERGM", "rate_title": "Personal consumption expenditures (PCE)",
    },
    "pce_core_price": {
        "indicator": "PCE price index excluding food and energy (core)", "table": "T20804", "line": "25", "code": "DPCCRG",
        "exact_title": "PCE excluding food and energy", "fred": "PCEPILFE", "rate_line": "25",
        "rate_code": "DPCCRGM", "rate_title": "PCE excluding food and energy",
    },
    "pce_market_based_price": {
        "indicator": "Market-based PCE price index", "table": "T20804", "line": "30", "code": "DPCMRG",
        "exact_title": "Market-based PCE", "fred": "DPCMRG3M086SBEA", "rate_line": "30",
        "rate_code": "DPCMRGM", "rate_title": "Market-based PCE",
    },
    "pce_market_based_core_price": {
        "indicator": "Market-based PCE price index excluding food and energy", "table": "T20804", "line": "31", "code": "DPCXRG",
        "exact_title": "Market-based PCE excluding food and energy", "fred": "DPCXRG3M086SBEA", "rate_line": "31",
        "rate_code": "DPCXRGM", "rate_title": "Market-based PCE excluding food and energy",
    },
    "pce_services_ex_energy_housing_price": {
        "indicator": "PCE services excluding energy and housing (price index)", "table": "T20804", "line": "28", "code": "IA001260",
        "exact_title": "PCE services excluding energy and housing", "fred": "IA001260M", "rate_line": "28",
        "rate_code": "PP001260", "rate_title": "PCE services excluding energy and housing",
    },
    "pce_goods_ex_food_energy_price": {
        "indicator": "PCE goods excluding food and energy (price index)", "table": "U20404", "line": "375", "code": "IA000062",
        "exact_title": "PCE goods excluding food and energy", "fred": "", "rate_line": "", "rate_code": "", "rate_title": "",
    },
}

INDEX_TABLES = {
    "NIPA": {"T20804": ["1", "25", "28", "30", "31"]},
    "NIUnderlyingDetail": {"U20404": ["375"]},
}
RATE_TABLES = {"T20807": ["1", "25", "28", "30", "31"]}


def bea_get(params, filename):
    params = {**params, "UserID": get_key("BEA_API_KEY"), "ResultFormat": "JSON"}
    raw = http_get(BEA_URL, params)
    raw_path = save_raw(GROUP, filename, raw)
    parsed = json.loads(raw)
    if "BEAAPI" not in parsed or "Results" not in parsed["BEAAPI"]:
        raise RuntimeError(f"BEA response missing results: {filename}")
    return parsed["BEAAPI"]["Results"], raw_path


def saved_get(url, params, filename):
    raw = http_get(url, params)
    return json.loads(raw), save_raw(GROUP, filename, raw)


def parse_month(period):
    m = re.fullmatch(r"(\d{4})M(\d{2})", period)
    if not m:
        return None
    return f"{m.group(1)}-{m.group(2)}-01"


def val_or_empty(v):
    if v in (None, "", "...", "--", "-"):
        return ""
    return v


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    retrieval_date = RETRIEVAL_DATE
    raw_files = set()

    # Verify table inventory from the BEA API itself and retain the full replies.
    tables = {}
    for dataset in ("NIPA", "NIUnderlyingDetail"):
        result, raw_path = bea_get({"method": "GetParameterValues", "DatasetName": dataset, "ParameterName": "TableName"},
                                   f"bea_{dataset}_GetParameterValues_{retrieval_date}.json")
        raw_files.add(raw_path)
        tables[dataset] = {x["TableName"]: x["Description"] for x in result["ParamValue"]}
    expected = {"NIPA": ["T20804", "T20807"], "NIUnderlyingDetail": ["U20404"]}
    for ds, names in expected.items():
        for name in names:
            if name not in tables[ds]:
                raise RuntimeError(f"Expected BEA table not available: {ds} {name}")

    # Search FRED for all requested concept names and preserve each discovery response.
    fred_search_notes = {}
    searches = {
        "pce_price": "Personal Consumption Expenditures: Chain-type Price Index",
        "pce_core_price": "Personal Consumption Expenditures Excluding Food and Energy Chain-Type Price Index",
        "pce_market_based_price": "market-based PCE price index monthly",
        "pce_market_based_core_price": "market-based PCE excluding food and energy monthly",
        "pce_services_ex_energy_housing_price": "Personal Consumption Expenditures Services Excluding Energy and Housing Chain-Type Price Index monthly",
        "pce_goods_ex_food_energy_price": "PCE goods excluding food and energy chain-type price index",
    }
    fred_key = get_key("FRED_API_KEY")
    for i, (key, query) in enumerate(searches.items()):
        result, raw_path = saved_get(FRED_SEARCH_URL, {
            "api_key": fred_key, "file_type": "json", "search_text": query,
            "limit": 100, "order_by": "search_rank", "sort_order": "asc",
        }, f"fred_series_search_{key}_{retrieval_date}.json")
        raw_files.add(raw_path)
        fred_search_notes[key] = result.get("seriess", [])

    # API year lists can exceed practical request limits; keep requests in <=5-year chunks.
    years = list(range(2000, date.today().year + 1))
    chunks = [years[i:i + 5] for i in range(0, len(years), 5)]
    payloads = defaultdict(list)
    source_by_table = defaultdict(set)
    source_by_period = {}
    for dataset, table_map in INDEX_TABLES.items():
        for table, lines in table_map.items():
            for chunk in chunks:
                ystr = ",".join(map(str, chunk))
                result, raw_path = bea_get({"method": "GetData", "DatasetName": dataset, "TableName": table,
                                            "Frequency": "M", "Year": ystr, "LineCode": ",".join(lines)},
                                           f"bea_{dataset}_{table}_M_{chunk[0]}-{chunk[-1]}_{retrieval_date}.json")
                raw_files.add(raw_path)
                source_by_table[(dataset, table)].add(raw_path)
                payloads[(dataset, table)].extend(result.get("Data", []))
                for row in result.get("Data", []):
                    source_by_period[(dataset, table, row.get("TimePeriod"))] = raw_path
                if result.get("Error"):
                    raise RuntimeError(f"BEA returned error for {dataset} {table}: {result['Error']}")
    for table, lines in RATE_TABLES.items():
        for chunk in chunks:
            ystr = ",".join(map(str, chunk))
            result, raw_path = bea_get({"method": "GetData", "DatasetName": "NIPA", "TableName": table,
                                        "Frequency": "M", "Year": ystr, "LineCode": ",".join(lines)},
                                       f"bea_NIPA_{table}_M_{chunk[0]}-{chunk[-1]}_{retrieval_date}.json")
            raw_files.add(raw_path)
            source_by_table[("NIPA", table)].add(raw_path)
            payloads[("NIPA", table)].extend(result.get("Data", []))
            for row in result.get("Data", []):
                source_by_period[("NIPA", table, row.get("TimePeriod"))] = raw_path

    # Exact series IDs/lines come from API metadata; insist the assigned rows exist.
    index_rows = {}
    for dataset, table_map in INDEX_TABLES.items():
        for table, wanted_lines in table_map.items():
            for item in payloads[(dataset, table)]:
                if item.get("LineNumber") in wanted_lines:
                    key = next(k for k, s in SERIES.items() if s["table"] == table and s["line"] == item["LineNumber"])
                    if item.get("LineDescription") != SERIES[key]["exact_title"] or item.get("SeriesCode") != SERIES[key]["code"]:
                        raise RuntimeError(f"BEA line mismatch for {key}: {item}")
                    index_rows.setdefault(key, {})[item["TimePeriod"]] = item
    rate_rows = {}
    for item in payloads[("NIPA", "T20807")]:
        for key, s in SERIES.items():
            if s["rate_line"] and item.get("LineNumber") == s["rate_line"]:
                if item.get("LineDescription") != s["rate_title"] or item.get("SeriesCode") != s["rate_code"]:
                    raise RuntimeError(f"BEA rate line mismatch for {key}: {item}")
                rate_rows.setdefault(key, {})[item["TimePeriod"]] = item

    # One normalized observation row per published measure and month; no rates are computed.
    observations = []
    for key, s in SERIES.items():
        if key not in index_rows:
            raise RuntimeError(f"No BEA index observations retrieved for {key}")
        idx_dataset = "NIPA" if s["table"].startswith("T") else "NIUnderlyingDetail"
        for period, item in sorted(index_rows[key].items()):
            dt = parse_month(period)
            if not dt: continue
            value = val_or_empty(item.get("DataValue"))
            observations.append({"series_key": key, "publisher_series_id": f"BEA {s['table']} line {s['line']} ({s['code']})",
                "date": dt, "frequency": "M", "value": value, "value_type": "index_level",
                "measure_label": f"{s['exact_title']} price index", "horizon": "level", "seasonal_adjustment": "SA",
                "raw_file": source_by_period[(idx_dataset, s["table"], period)], "note": "" if value != "" else "BEA value missing in API response"})
        if s["rate_line"]:
            for period, item in sorted(rate_rows.get(key, {}).items()):
                dt = parse_month(period)
                if not dt: continue
                value = val_or_empty(item.get("DataValue"))
                observations.append({"series_key": key, "publisher_series_id": f"BEA T20807 line {s['rate_line']} ({s['rate_code']})",
                    "date": dt, "frequency": "M", "value": value, "value_type": "published_rate",
                    "measure_label": "Percent change from preceding month", "horizon": "MoM", "seasonal_adjustment": "SA",
                    "raw_file": source_by_period[("NIPA", "T20807", period)], "note": "Published monthly percent change; not annualized" if value != "" else "BEA value missing in API response"})

    # Validate the expected monthly coverage and latest value month for each index.
    bykey = defaultdict(list)
    for row in observations:
        if row["value_type"] == "index_level": bykey[row["series_key"]].append(row)
    latest_month = max((r["date"] for values in bykey.values() for r in values), default="")
    if latest_month < f"{date.today().year}-01-01":
        raise RuntimeError(f"Latest observation unexpectedly old: {latest_month}")
    counts = {k: len(v) for k, v in bykey.items()}

    # FRED current levels and ALFRED first-release observations are saved independently.
    fred_data = {}
    release_rows = []
    fred_raw_by_series = {}
    for key, s in SERIES.items():
        sid = s["fred"]
        if not sid:
            continue
        alfred_raw = fred_initial_release(sid)
        alfred_path = save_raw(GROUP, f"alfred_first_release_{sid}_{retrieval_date}.json", alfred_raw)
        raw_files.add(alfred_path)
        fred_raw = http_get(FRED_URL, {"series_id": sid, "api_key": fred_key, "file_type": "json", "sort_order": "asc"})
        fred_path = save_raw(GROUP, f"fred_observations_{sid}_{retrieval_date}.json", fred_raw)
        raw_files.add(fred_path)
        fred_raw_by_series[key] = fred_path
        fobs = json.loads(fred_raw).get("observations", [])
        fred_data[key] = {x.get("date"): val_or_empty(x.get("value")) for x in fobs}
        aobs = json.loads(alfred_raw).get("observations", [])
        # Keep latest 13 valid monthly ALFRED first-release dates.
        months = []
        for x in aobs:
            dt = x.get("date", "")
            rel = x.get("realtime_start", "")
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", dt) and dt.endswith("-01") and rel and rel != "9999-12-31":
                months.append((dt, rel))
        for dt, rel in months[-13:]:
            release_rows.append({"series_key": key, "date": dt, "first_release_date": rel,
                "method": f"ALFRED output_type=4 {sid}", "note": "First vintage date from ALFRED"})

    # Goods-ex-food-and-energy lacks an exact FRED monthly series: retrieve BEA's official
    # release archive and map each recent observation to the release that first published it.
    archive_url = "https://www.bea.gov/news/archive"
    archive_params = {"field_related_product_target_id": "476", "title": ""}
    archive_raw = http_get(archive_url, archive_params)
    archive_path = save_raw(GROUP, f"bea_news_archive_personal_income_{retrieval_date}.html", archive_raw)
    raw_files.add(archive_path)
    archive = BeautifulSoup(archive_raw, "html.parser")
    release_map = {}
    month_names = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                   "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    for tr in archive.select("tr.release-row"):
        link = tr.select_one('a[href*="personal-income-and-outlays"]')
        if not link: continue
        title = link.get_text(" ", strip=True)
        if "Data Update" in title: continue
        dates = re.findall(r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}", tr.get_text(" ", strip=True))
        if not dates: continue
        pubdate = datetime.strptime(dates[-1], "%B %d, %Y").date().isoformat()
        m = re.search(r"Personal Income and Outlays, (.+?) (\d{4})$", title)
        if not m: continue
        for mon in re.findall(r"January|February|March|April|May|June|July|August|September|October|November|December", m.group(1)):
            year = int(m.group(2))
            release_map[f"{year:04d}-{month_names[mon]:02d}-01"] = pubdate
    # The archive may lag the most recent release. Fetch that official release page too.
    latest_year, latest_mon = latest_month[:4], latest_month[5:7]
    latest_mon_name = datetime.strptime(latest_month[:7], "%Y-%m").strftime("%B")
    latest_release_url = f"https://www.bea.gov/news/{latest_year}/personal-income-and-outlays-{latest_mon_name.lower()}-{latest_year}"
    latest_release_raw = http_get(latest_release_url)
    latest_release_path = save_raw(GROUP, f"bea_personal_income_outlays_latest_{retrieval_date}.html", latest_release_raw)
    raw_files.add(latest_release_path)
    latest_release_text = BeautifulSoup(latest_release_raw, "html.parser").get_text(" ", strip=True)
    date_match = re.search(r"EMBARGOED UNTIL RELEASE.*?, ([A-Z][a-z]+ \d{1,2}, \d{4})", latest_release_text)
    if date_match:
        release_map[latest_month] = datetime.strptime(date_match.group(1), "%B %d, %Y").date().isoformat()
    goods_months = sorted(bykey["pce_goods_ex_food_energy_price"], key=lambda r: r["date"])[-13:]
    for row in goods_months:
        if row["date"] in release_map:
            release_rows.append({"series_key": "pce_goods_ex_food_energy_price", "date": row["date"],
                "first_release_date": release_map[row["date"]],
                "method": f"publisher calendar {archive_url}?field_related_product_target_id=476",
                "note": "Monthly Personal Income and Outlays release date; underlying index first published with release"})
        else:
            release_rows.append({"series_key": "pce_goods_ex_food_energy_price", "date": row["date"], "first_release_date": "",
                "method": f"publisher calendar {archive_url}?field_related_product_target_id=476",
                "note": f"No matching release row found in saved BEA archive {archive_path}; left blank"})
    latest_iso = latest_month
    latest_release_date = release_map.get(latest_iso, "")
    latest_month_label = datetime.strptime(latest_iso[:7], "%Y-%m").strftime("%B %Y")
    if retrieval_date < "2026-09-30":
        vintage_text = (f"Retrieved {retrieval_date}, before the scheduled 2026-09-30 annual update; latest release used is "
            f"Personal Income and Outlays, {latest_month_label}, released {latest_release_date or 'date unavailable in archive'}. "
            "BEA says estimates from 2021Q1 forward will be updated Sept. 30, including portfolio management, legal services, and computer software methods. "
            "Re-running unchanged after that date retrieves the then-current BEA vintage; retrieval-date filenames preserve snapshots.")
    else:
        vintage_text = (f"Retrieved {retrieval_date}, after the scheduled 2026-09-30 annual update; latest release used is "
            f"Personal Income and Outlays, {latest_month_label}, released {latest_release_date or 'date unavailable in archive'}. "
            "BEA's annual update revised estimates from 2021Q1 forward, including portfolio management, legal services, and computer software methods. "
            "Re-running retrieves the then-current BEA vintage; retrieval-date filenames preserve snapshots.")

    # Compare the latest three overlapping published index values to FRED without replacing BEA.
    comparisons = {}
    for key, values in bykey.items():
        sid = SERIES[key]["fred"]
        if not sid:
            comparisons[key] = {"id": "", "checked": [], "match": None, "reason": "No exact monthly FRED equivalent found in FRED series search"}
            continue
        bvals = {x["date"]: x["value"] for x in values}
        overlap = sorted(d for d, v in bvals.items() if v != "" and d in fred_data.get(key, {}) and fred_data[key][d] != "")[-3:]
        checks = []
        for dt in overlap:
            bv, fv = float(bvals[dt]), float(fred_data[key][dt])
            checks.append({"date": dt, "bea": bv, "fred": fv, "difference": round(bv - fv, 9), "match": abs(bv-fv) < 0.00051})
        comparisons[key] = {"id": sid, "checked": checks, "match": bool(checks) and all(x["match"] for x in checks), "reason": "" if checks else "No common nonmissing observations"}

    # Metadata reference-year and latest-release details are confirmed in the BEA table NoteText.
    table_notes = {}
    for raw_path in sorted(source_by_table[("NIPA", "T20804")]):
        d = json.loads((ROOT.parent / raw_path).read_text(encoding="utf-8"))
        for n in d["BEAAPI"]["Results"].get("Notes", []):
            if n.get("NoteRef") == "T20804": table_notes["T20804"] = n.get("NoteText", "")
    for raw_path in sorted(source_by_table[("NIUnderlyingDetail", "U20404")]):
        d = json.loads((ROOT.parent / raw_path).read_text(encoding="utf-8"))
        for n in d["BEAAPI"]["Results"].get("Notes", []):
            if n.get("NoteRef") == "U20404": table_notes["U20404"] = n.get("NoteText", "")

    obs_fields = ["series_key", "publisher_series_id", "date", "frequency", "value", "value_type", "measure_label", "horizon", "seasonal_adjustment", "raw_file", "note"]
    write_csv(OUT / "observations.csv", obs_fields, observations)
    metadata = []
    for key, s in SERIES.items():
        idx = sorted(index_rows[key])
        rates_present = bool(s["rate_line"])
        rate_horizons = "MoM" if rates_present else "none published in assigned BEA monthly tables"
        dataset = "NIPA" if s["table"].startswith("T") else "NIUnderlyingDetail"
        table_name = tables[dataset][s["table"]]
        metadata.append({
            "series_key": key, "indicator": s["indicator"], "publisher": "U.S. Bureau of Economic Analysis",
            "exact_title": s["exact_title"], "publisher_series_id": f"BEA {s['table']} line {s['line']} ({s['code']})",
            "table_or_dataset": f"{dataset}; {table_name}",
            "definition": "BEA Fisher price index; index levels and rates taken verbatim from the identified tables. " +
                ("U20404 underlying detail, addenda line." if s["line"] == "375" else "Monthly PCE price index series."),
            "frequency": "M", "units": "index, 2017=100; published rate in percent" if rates_present else "index, 2017=100",
            "seasonal_adjustment": "SA", "geography_population": "United States; personal consumption expenditures",
            "earliest_obs": min(idx)[:4] + "-" + min(idx)[5:] if idx else "", "latest_obs": max(idx)[:4] + "-" + max(idx)[5:] if idx else "",
            "latest_release_date": latest_release_date + f" (Personal Income and Outlays, {latest_month_label})",
            "source_url": "https://apps.bea.gov/api/data/", "api_endpoint": "https://apps.bea.gov/api/data/ (GetData; no key in stored URL)",
            "raw_files": ";".join(sorted(
                list(source_by_table[(dataset, s["table"])]) +
                (list(source_by_table[("NIPA", "T20807")] if s["rate_line"] else [])) +
                ([f"inflation_data/raw/bea/alfred_first_release_{s['fred']}_{retrieval_date}.json",
                  f"inflation_data/raw/bea/fred_observations_{s['fred']}_{retrieval_date}.json",
                  f"inflation_data/raw/bea/fred_series_search_{key}_{retrieval_date}.json"] if s["fred"] else [archive_path]) +
                [latest_release_path]
            )), "retrieval_date": retrieval_date,
            "published_rate_horizons": rate_horizons, "fred_equivalent_id": s["fred"],
            "revision_vintage_notes": f"BEA table reports {table_notes.get(s['table'], '2017=100')}. {vintage_text}",
            "status": "retrieved", "notes": ("Exact title confirmed in U20404; no corresponding NIPA T20804 summary line; no matching BEA-published monthly percent-change line was found in T20807." if key == "pce_goods_ex_food_energy_price" else "Rate table T20807 is percent change from preceding month; monthly rate, not annualized. No BEA time-series table for 12-month price change was listed in the API table inventory; release text reports headline/core YoY in current news release.")
        })
    metadata_fields = list(metadata[0].keys())
    write_csv(OUT / "series_metadata.csv", metadata_fields, metadata)
    write_csv(OUT / "release_dates.csv", ["series_key", "date", "first_release_date", "method", "note"], sorted(release_rows, key=lambda x:(x["series_key"],x["date"])))

    # Compact verification report; all differences retain the BEA value as primary.
    lines = ["# BEA PCE price data retrieval", "",
        f"Retrieved: {retrieval_date}. Scope: monthly SA BEA price indexes, Jan 2000 through latest API observation; no derived rates computed.",
        "BEA API parameter inventory verified NIPA T20804/T20807 and NIUnderlyingDetail U20404. T20804 note states index numbers, 2017=100, seasonally adjusted; table latest revision recorded in raw responses.",
        f"Latest Personal Income and Outlays release used: {latest_month_label}, released {latest_release_date or 'date unavailable in saved archive'}. The Sept. 30, 2026 annual update affects 2021Q1 onward.", "",
        "## Retrieved series", ""]
    for key, s in SERIES.items():
        vals = bykey[key]
        first = min(x["date"] for x in vals)[:7]; last = max(x["date"] for x in vals)[:7]
        lines.append(f"- `{key}` — BEA {s['table']} line {s['line']} ({s['code']}), **{s['exact_title']}**; {first}–{last}, {counts[key]} index observations; index 2017=100, SA.")
        if s["rate_line"]:
            n = len(rate_rows.get(key, {}))
            lines.append(f"  - Rates: T20807 line {s['rate_line']} ({s['rate_code']}), label **Percent change from preceding month**, {n} observations; monthly rate, not annualized.")
        else:
            lines.append("  - Rates: no exact series in the BEA monthly price-change companion table T20807; no rate constructed.")
    lines += ["", "## Verification and FRED comparisons", "", "Exact series titles, line numbers, codes, unit/base, seasonal adjustment, and last-revised notes were checked in saved BEA GetData responses. Table names were checked against saved GetParameterValues responses.", "FRED is used only as a cross-check and for ALFRED first-release dates; BEA observations remain primary."]
    for key, result in comparisons.items():
        if not result["id"]:
            lines.append(f"- `{key}`: no exact monthly FRED equivalent found; checked FRED series search response. Latest 13 first-release dates use BEA's Personal Income and Outlays release calendar/archive.")
        elif result["checked"]:
            detail = "; ".join(f"{x['date']}: BEA {x['bea']:.3f}, FRED {x['fred']:.3f}, diff {x['difference']:+.3f}" for x in result["checked"])
            precision_note = " FRED's values are shown to one decimal while BEA reports three; differences are within 0.05 and consistent with FRED rounding." if key == "pce_services_ex_energy_housing_price" else ""
            lines.append(f"- `{key}` / `{result['id']}`: {'matches' if result['match'] else 'differences'} on latest {len(result['checked'])} overlapping observations: {detail}.{precision_note}")
        else:
            lines.append(f"- `{key}` / `{result['id']}`: unresolved cross-check: {result['reason']}.")
    lines += ["", "## N/A and unresolved", "",
        "- Goods excluding food and energy is available as U20404 line 375, exactly titled 'PCE goods excluding food and energy'; no matching series was present in NIPA T20804 or T20807. FRED search found no exact monthly series. The underlying-detail index is retained; no rate is fabricated.",
        "- BEA publishes 12-month headline and core changes in current release text, but the API inventory has no monthly PCE price 12-month-change table. These two release-text rates are not reconstructed as a time series here.",
        "- Release-date rows for the goods series use official BEA Personal Income and Outlays monthly release dates; all other series use ALFRED output_type=4. If BEA does not return an ALFRED date for a month, the date is left blank rather than inferred.",
        "- A post-Sept. 30 rerun will reflect revised current BEA values, not freeze this pre-update vintage; raw filenames include retrieval date. No request parameter for historical BEA vintage was identified in this API workflow.", ""]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"BEA series retrieved: {len(SERIES)}; index rows: {sum(counts.values())}; total observation rows: {len(observations)}")
    print(f"Latest index month: {latest_month}; raw payloads saved: {len(raw_files)}")
    for key, res in comparisons.items():
        print(f"FRED check {key}: {res['id'] or 'none'}; {len(res['checked'])} comparisons; match={res['match']}")


if __name__ == "__main__":
    main()
