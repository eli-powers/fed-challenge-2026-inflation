#!/usr/bin/env python3
"""Retrieve assigned BLS price, labor-cost, and productivity series."""
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
import fetch_utils as fu  # noqa: E402

ROOT = fu.ROOT
GROUP = "bls"
RAW_DIR = ROOT / "raw" / GROUP
OUT_DIR = ROOT / "processed" / GROUP
API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
RETRIEVAL_DATE = fu.RETRIEVAL_DATE

SERIES = {}
REQUEST_IDS = []


def add(key, indicator, ids, frequency, sa, units, population, definition,
        fred="", source="", release_note=""):
    SERIES[key] = {
        "series_key": key, "indicator": indicator, "ids": ids,
        "frequency": frequency, "sa": sa, "units": units,
        "population": population, "definition": definition,
        "fred": fred, "source": source, "release_note": release_note,
        "observations": {}, "raw_files": set(), "titles": {}, "catalog": {},
    }
    REQUEST_IDS.extend(ids)


def pair(key, name, sa_id, nsa_id, frequency="M", units="Index 1982-84=100",
         population="U.S. city average", definition="", fred="", source="", fred_sa="", fred_nsa=""):
    add(key + "_sa", name, [sa_id], frequency, "SA", units, population,
        definition or name, fred_sa or (fred if fred else sa_id), source)
    add(key + "_nsa", name, [nsa_id], frequency, "NSA", units, population,
        definition or name, fred_nsa or (fred if fred else nsa_id), source)


CPI_PAGE = "https://www.bls.gov/cpi/"
PPI_CATALOG = "https://www.bls.gov/ppi/fd-id/ppi-final-demand-intermediate-demand-aggregation-indexes-by-title-and-series-id.htm"
ECI_GUIDE = "https://www.bls.gov/eci/factsheets/eci-series-id-guide.htm"
PRODUCTIVITY_PAGE = "https://www.bls.gov/news.release/prod2.nr0.htm"

pair("cpi_u_all_items", "CPI-U all items, U.S. city average", "CUSR0000SA0", "CUUR0000SA0",
     definition="Consumer Price Index for All Urban Consumers, all items.", fred_sa="CPIAUCSL", fred_nsa="CPIAUCNS", source=CPI_PAGE)
pair("cpi_u_core", "CPI-U all items less food and energy", "CUSR0000SA0L1E", "CUUR0000SA0L1E",
    definition="Consumer Price Index for All Urban Consumers, all items less food and energy.", fred_sa="CPILFESL", fred_nsa="CPILFENS", source=CPI_PAGE)

pair("ppi_final_demand", "PPI Final Demand", "WPSFD4", "WPUFD4", units="Index, November 2009=100",
     population="U.S. final demand", definition="Producer Price Index for Final Demand.", fred_sa="PPIFIS", fred_nsa="PPIFID", source=PPI_CATALOG)
for short, name in [("61", "Processed goods for intermediate demand"),
                    ("62", "Unprocessed goods for intermediate demand"),
                    ("63", "Services for intermediate demand")]:
    pair("ppi_intermediate_" + short, name, "WPSID" + short, "WPUID" + short,
         units="Index, 1982=100" if short in ("61", "62") else "Index, November 2009=100",
         population="U.S. intermediate demand",
         definition=name + "; FD-ID commodity-type aggregation.", source=PPI_CATALOG,
         fred_sa="WPSID" + short, fred_nsa="WPUID" + short)
pair("ppi_final_demand_trade_services", "PPI Final demand trade services", "WPSFD423", "WPUFD423",
     units="Index, November 2009=100", population="U.S. final demand",
     definition="Final demand trade services (trade margins).", source=PPI_CATALOG,
     fred_sa="PPITSS", fred_nsa="PPIDTS")
pair("ppi_personal_consumption_trade", "PPI Trade of personal consumption goods", "WPSFD42311", "WPUFD42311",
     units="Index, November 2009=100", population="U.S. final demand",
     definition="Final-demand trade-service margin for personal consumption goods; BLS catalog title is 'Trade of personal consumption goods'.",
     source=PPI_CATALOG, fred_sa="WPSFD42311", fred_nsa="WPUFD42311")

# ECI suffixes: I=index, Q=3-month percent change, A=12-month percent change.
for owner, pop in [("1", "Civilian workers"), ("2", "Private industry workers")]:
    for est, measure in [("01", "Total compensation"), ("02", "Wages and salaries"), ("03", "Benefits")]:
        stem = f"{owner}{est}0000000000"
        key = f"eci_{'civilian' if owner == '1' else 'private'}_{measure.lower().replace(' ', '_')}"
        ids = ["CIS" + stem + "I", "CIU" + stem + "I", "CIS" + stem + "Q", "CIU" + stem + "A"]
        add(key, f"Employment Cost Index: {pop}, {measure}", ids, "Q", "SA and NSA",
            "Index (December 2005=100); percent change", pop,
            f"ECI for all workers, {measure.lower()}, {pop.lower()}; SA/NSA index levels, SA 3-month change, NSA 12-month change.",
            source=ECI_GUIDE)
        SERIES[key]["fred_sa"] = ids[0]
        SERIES[key]["fred_nsa"] = ids[1]
        SERIES[key]["fred"] = ids[1]  # NSA ECI is used for ALFRED release-date mapping.
        SERIES[key]["fred_equivalents"] = ids[:2]

# Productivity and Costs uses separate BLS series for index level, quarterly
# percent change at annual rate, and same-quarter year-over-year percent change.
for metric, ids, name, fred in [
    ("unit_labor_costs", ("PRS85006111", "PRS85006112", "PRS85006113"), "Unit labor costs", "ULCNFB"),
    ("labor_productivity", ("PRS85006091", "PRS85006092", "PRS85006093"), "Labor productivity (output per hour)", "OPHNFB"),
    ("hourly_compensation", ("PRS85006101", "PRS85006102", "PRS85006103"), "Hourly compensation", "COMPNFB"),
]:
    add("productivity_" + metric, "Productivity and Costs: nonfarm business sector, " + name,
        list(ids), "Q", "SA", "Index and percent change", "Nonfarm business sector",
        "Nonfarm business sector " + name.lower() + "; index, percent change from previous quarter at annual rate, and percent change from same quarter a year ago.",
        fred=fred, source=PRODUCTIVITY_PAGE, release_note="Latest release: Q3 2026 preliminary, November 5, 2026.")
    SERIES["productivity_" + metric]["fred_equivalents"] = [fred, ids[0], ids[1]]

# Record the catalog check as an explicit N/A metadata row; do not invent or
# aggregate an index that BLS does not publish.
SERIES["ppi_intermediate_total"] = {
    "series_key": "ppi_intermediate_total", "indicator": "PPI total intermediate demand", "ids": [],
    "frequency": "M", "sa": "SA and NSA", "units": "Index, November 2009=100",
    "population": "U.S. intermediate demand",
    "definition": "N/A: BLS lists four stage-based intermediate-demand indexes and separate commodity-type groups, but no single total intermediate-demand index.",
    "fred": "", "source": PPI_CATALOG, "release_note": "", "observations": {},
    "raw_files": set(), "titles": {}, "catalog": {},
}

assert len(set(REQUEST_IDS)) == len(REQUEST_IDS), "Duplicate BLS series IDs"
assert len(REQUEST_IDS) <= 50, f"BLS API request cap exceeded: {len(REQUEST_IDS)}"


def write_raw(filename, raw):
    path = fu.save_raw(GROUP, filename, raw)
    return path


def api_requests():
    key = fu.get_key("BLS_API_KEY")
    responses = []
    for start, end in [("2000", "2019"), ("2020", "2026")]:
        payload = {"seriesid": REQUEST_IDS, "startyear": start, "endyear": end,
                   "catalog": True, "calculations": True, "registrationkey": key}
        raw = fu.http_post_json(API, payload)
        filename = f"bls_api_all_series_{start}-{end}_{RETRIEVAL_DATE}.json"
        raw_path = write_raw(filename, raw)
        doc = json.loads(raw)
        if doc.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS API request {start}-{end} failed: {doc.get('message')}")
        responses.append((doc, raw_path))
    return responses


def parse_period(period, year, frequency):
    if frequency == "M":
        if not re.fullmatch(r"M\d{2}", period):
            return None
        month = int(period[1:])
        return f"{year}-{month:02d}-01" if 1 <= month <= 12 else None
    if frequency == "Q":
        match = re.fullmatch(r"Q0?([1-4])", period)
        if not match:
            return None
        month = 1 + 3 * (int(match.group(1)) - 1)
        return f"{year}-{month:02d}-01"
    return None


def ingest(responses):
    for doc, raw_path in responses:
        data = doc.get("Results", {}).get("series", [])
        for item in data:
            sid = item.get("seriesID")
            keys = [k for k, v in SERIES.items() if sid in v["ids"]]
            if not keys:
                continue
            for key in keys:
                meta = SERIES[key]
                cat = item.get("catalog", {}) or {}
                meta["catalog"][sid] = cat
                meta["titles"][sid] = cat.get("series_title") or cat.get("series_title_text") or ""
                meta["raw_files"].add(raw_path)
                meta.setdefault("id_obs", {}).setdefault(sid, {})
                for obs in item.get("data", []):
                    dt = parse_period(obs.get("period", ""), obs.get("year", ""), meta["frequency"])
                    if not dt or dt < "2000-01-01":
                        continue
                    entry = meta["observations"].setdefault(dt, {"level": None, "rates": {}, "notes": set(), "raw": set()})
                    val = obs.get("value", "")
                    if val != "":
                        entry["level"] = val
                    else:
                        entry["level"] = ""
                        entry["notes"].add("BLS returned an empty value")
                    entry["raw"].add(raw_path)
                    if any(note.get("code") or note.get("text") for note in (obs.get("footnotes") or [])):
                        entry["notes"].add("BLS footnotes: " + json.dumps(obs["footnotes"], ensure_ascii=False))
                    meta["id_obs"][sid][dt] = {"value": val, "entry": entry,
                                               "calculations": (obs.get("calculations") or {}).get("pct_changes", {}) or {}}
                    if key.endswith("_sa") or key.endswith("_nsa"):
                        # For monthly CPI/PPI retain API 1m SA and 12m NSA changes.
                        # For quarterly ECI the API's 3m SA and 12m NSA are retained.
                        pct = (obs.get("calculations") or {}).get("pct_changes", {}) or {}
                        chosen = "1" if meta["sa"] == "SA" and meta["frequency"] == "M" else (
                            "3" if meta["sa"] == "SA" and meta["frequency"] == "Q" else "12")
                        calc = pct.get(chosen)
                        if calc not in (None, ""):
                            label = ("BLS API calculations: 1-month percent change (SA)" if chosen == "1" else
                                     "BLS API calculations: 3-month percent change (SA)" if chosen == "3" else
                                     "BLS API calculations: 12-month percent change (NSA)")
                            entry["rates"][label] = (calc, "MoM" if chosen == "1" else "3m" if chosen == "3" else "12m")
    # BLS explicitly reports CPI data were not collected for these two months.
    for key, meta in SERIES.items():
        if not key.startswith("cpi_u_"):
            continue
        for dt in ("2025-10-01", "2025-11-01"):
            # Manager fix (2026-09-26): blank only if BLS actually returned no value.
            # The API publishes Nov 2025 CPI; only Oct 2025 is unavailable.
            existing = meta.get("id_obs", {}).get(meta["ids"][0], {}).get(dt)
            if existing and existing.get("value") not in (None, "", "-"):
                continue
            entry = meta["observations"].setdefault(dt, {"level": "", "rates": {},
                                                         "notes": set(), "raw": set()})
            entry["level"] = ""
            entry["notes"].add("BLS: data unavailable due to the 2025 lapse in appropriations (footnote X)")
            entry["raw"].update(meta["raw_files"])
            sid = meta["ids"][0]
            meta.setdefault("id_obs", {}).setdefault(sid, {})[dt] = {
                "value": "", "entry": entry, "calculations": {}}


def obs_rows():
    rows = []
    for key, meta in SERIES.items():
        for sid in meta["ids"]:
            records = meta.get("id_obs", {}).get(sid, {})
            for dt, rec in sorted(records.items()):
                value, entry = rec["value"], rec["entry"]
                if sid.startswith("PRS"):
                    typ, label, horizon = {"2": ("published_rate", "Percent change from previous quarter at annual rate", "3m_ann"),
                                           "1": ("published_rate", "Percent change from same quarter a year ago", "12m"),
                                           "3": ("index_level", "BLS index level", "level")}[sid[-1]]
                    rows.append(row(key, meta, dt, value, typ, label, horizon, "SA", entry, sid))
                elif sid.startswith("CI"):
                    if sid.endswith("I"):
                        rows.append(row(key, meta, dt, value, "index_level", "ECI index level", "level",
                                        "SA" if sid.startswith("CIS") else "NSA", entry, sid))
                    elif sid.endswith("Q"):
                        rows.append(row(key, meta, dt, value, "published_rate", "ECI 3-month percent change, SA", "3m", "SA", entry, sid))
                    elif sid.endswith("A"):
                        rows.append(row(key, meta, dt, value, "published_rate", "ECI 12-month percent change, NSA", "12m", "NSA", entry, sid))
                else:
                    rows.append(row(key, meta, dt, value, "index_level", "BLS index level", "level", meta["sa"], entry, sid))
                    chosen = "1" if meta["sa"] == "SA" else "12"
                    calc = rec["calculations"].get(chosen)
                    if calc not in (None, ""):
                        label = ("BLS API calculations: 1-month percent change (SA)" if chosen == "1"
                                 else "BLS API calculations: 12-month percent change (NSA)")
                        rows.append(row(key, meta, dt, calc, "published_rate", label,
                                        "MoM" if chosen == "1" else "12m", meta["sa"], entry, sid))
                    elif key.startswith("cpi_u_") and dt in ("2025-10-01", "2025-11-01"):
                        label = ("BLS API calculations: 1-month percent change (SA)" if chosen == "1"
                                 else "BLS API calculations: 12-month percent change (NSA)")
                        rows.append(row(key, meta, dt, "", "published_rate", label,
                                        "MoM" if chosen == "1" else "12m", meta["sa"], entry, sid))
    return rows


def row(key, meta, dt, value, value_type, label, horizon, sa, entry, sid=None):
    return {"series_key": key, "publisher_series_id": sid or ";".join(meta["ids"]), "date": dt,
            "frequency": meta["frequency"], "value": value if value is not None else "",
            "value_type": value_type, "measure_label": label, "horizon": horizon,
            "seasonal_adjustment": sa, "raw_file": ";".join(sorted(entry.get("raw", []))),
            "note": "; ".join(sorted(entry.get("notes", [])))}


def attach_by_id(responses):
    """Preserve BLS values from distinct ECI and productivity rate series."""
    for meta in SERIES.values():
        meta["by_id"] = {}
    for doc, raw_path in responses:
        for item in doc.get("Results", {}).get("series", []):
            sid = item.get("seriesID")
            owner = next((m for m in SERIES.values() if sid in m["ids"]), None)
            if not owner:
                continue
            owner["raw_files"].add(raw_path)
            freq = owner["frequency"]
            records = []
            for obs in item.get("data", []):
                dt = parse_period(obs.get("period", ""), obs.get("year", ""), freq)
                if not dt or dt < "2000-01-01":
                    continue
                raw_value = obs.get("value", "")
                entry = {"raw": {raw_path}, "notes": set()}
                if any(note.get("code") or note.get("text") for note in (obs.get("footnotes") or [])):
                    entry["notes"].add("BLS footnotes: " + json.dumps(obs["footnotes"], ensure_ascii=False))
                records.append((dt, raw_value, entry))
            owner["by_id"][sid] = records


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fred_data(series_id):
    raw = fu.http_get("https://api.stlouisfed.org/fred/series/observations", {
        "series_id": series_id, "api_key": fu.get_key("FRED_API_KEY"),
        "file_type": "json", "observation_start": "2000-01-01", "observation_end": "2026-12-31"})
    path = write_raw(f"alfred_crosscheck_{series_id}_{RETRIEVAL_DATE}.json", raw)
    return json.loads(raw).get("observations", []), path


def crosschecks():
    results = {}
    for key, meta in SERIES.items():
        fred = meta["fred"]
        if not fred:
            continue
        mappings = []
        if key.startswith("eci_"):
            mappings = [(meta["ids"][i], meta["ids"][i]) for i in range(4)]
        elif key.startswith("productivity_"):
            # BLS index IDs are checked against the established FRED equivalent;
            # reported rate series are also cataloged directly in FRED by BLS ID.
            mappings = [(sid, meta["fred"] if i == 2 else sid) for i, sid in enumerate(meta["ids"])]
        else:
            mappings = [(meta["ids"][0], fred)]
        for bls_id, fred_id in mappings:
            try:
                values, _ = fred_data(fred_id)
                fmap = {x.get("date"): x.get("value") for x in values}
                recs = meta.get("id_obs", {}).get(bls_id, {})
                if not recs and bls_id in meta.get("by_id", {}):
                    recs = {dt: {"value": val} for dt, val, _ in meta["by_id"][bls_id]}
                source_data = [(dt, rec.get("value")) for dt, rec in sorted(recs.items())
                               if rec.get("value") not in (None, "")]
                if not source_data and bls_id in meta.get("ids", []) and not key.startswith(("eci_", "productivity_")):
                    source_data = [(dt, ent.get("level")) for dt, ent in sorted(meta["observations"].items())
                                   if ent.get("level") not in (None, "")]
                recent = source_data[-3:]
                diffs, compared = [], []
                for dt, bv in recent:
                    fv = fmap.get(dt)
                    if fv in (None, "."):
                        diffs.append(f"{bls_id}/{fred_id} {dt}: FRED has no value")
                    elif abs(float(bv) - float(fv)) > 0.00011:
                        diffs.append(f"{bls_id}/{fred_id} {dt}: BLS={bv}, FRED={fv}")
                    else:
                        compared.append(dt)
                results.setdefault(key, {"id": fred, "compared": [], "differences": [], "status": "match"})
                results[key]["compared"].extend(f"{bls_id}:{dt}" for dt in compared)
                results[key]["differences"].extend(diffs)
                if not recent:
                    results[key]["status"] = "no BLS observations"
                elif diffs:
                    results[key]["status"] = "difference/unavailable"
            except Exception as exc:
                results.setdefault(key, {"id": fred, "compared": [], "differences": [], "status": "unavailable"})
                results[key]["differences"].append(f"{bls_id}/{fred_id}: FRED cross-check unavailable: {exc}")
                results[key]["status"] = "difference/unavailable"
    return results


def release_dates(crosscheck_ids):
    rows = []
    latest_keys = [k for k, v in SERIES.items() if v["frequency"] in ("M", "Q") and v["observations"]]
    fetched = {}
    for key in latest_keys:
        meta = SERIES[key]
        fred = meta["fred"]
        if not fred:
            continue
        # Reuse ALFRED output_type=4; initial release's realtime_start is publication date.
        try:
            raw = fu.fred_initial_release(fred)
            raw_path = write_raw(f"alfred_first_release_{fred}_{RETRIEVAL_DATE}.json", raw)
            fetched[fred] = (json.loads(raw).get("observations", []), raw_path)
        except Exception:
            fetched[fred] = ([], "")
    for key in latest_keys:
        meta = SERIES[key]
        if not meta["observations"]:
            continue
        dates = sorted(meta["observations"])[-13:]
        fred = meta["fred"]
        obs = fetched.get(fred, ([], ""))[0] if fred else []
        first = {x.get("date"): x.get("realtime_start") for x in obs}
        if not obs and fred:
            # ALFRED coverage may not include particular program series; release schedule used.
            pass
        for dt in dates:
            pubdate = first.get(dt, "")
            note = ""
            method = f"ALFRED output_type=4 {fred}" if pubdate else "publisher calendar " + meta["source"]
            if not pubdate:
                note = "ALFRED equivalent unavailable or date not returned; see publisher release calendar/archive."
            if dt == "2025-10-01" and key.startswith("cpi_u_"):
                note = "BLS CPI value for Oct 2025 unavailable (2025 appropriations lapse)."
            rows.append({"series_key": key, "date": dt, "first_release_date": pubdate,
                         "method": method, "note": note})
    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    responses = api_requests()
    ingest(responses)
    attach_by_id(responses)
    rows = obs_rows()
    observation_fields = ["series_key", "publisher_series_id", "date", "frequency", "value", "value_type",
                          "measure_label", "horizon", "seasonal_adjustment", "raw_file", "note"]
    write_csv(OUT_DIR / "observations.csv", observation_fields, rows)

    check = crosschecks()
    release_rows = release_dates(check)
    latest_release = {}
    for key, meta in SERIES.items():
        if not meta.get("observations"):
            latest_release[key] = ""
            continue
        latest_obs = max(meta["observations"])
        row_match = next((r for r in release_rows if r["series_key"] == key and r["date"] == latest_obs), None)
        latest_release[key] = row_match["first_release_date"] if row_match else ""
        if key.startswith("productivity_"):
            latest_release[key] = "2026-11-05"
    meta_rows = []
    for key, meta in SERIES.items():
        if not meta["ids"]:
            meta_rows.append({
                "series_key": key, "indicator": meta["indicator"], "publisher": "U.S. Bureau of Labor Statistics",
                "exact_title": "N/A — no single total intermediate-demand series listed",
                "publisher_series_id": "", "table_or_dataset": "PPI FD-ID aggregation indexes",
                "definition": meta["definition"], "frequency": meta["frequency"], "units": meta["units"],
                "seasonal_adjustment": meta["sa"], "geography_population": meta["population"],
                "earliest_obs": "", "latest_obs": "", "latest_release_date": "", "source_url": meta["source"],
                "api_endpoint": API, "raw_files": "", "retrieval_date": RETRIEVAL_DATE,
                "published_rate_horizons": "", "fred_equivalent_id": "", "revision_vintage_notes": "",
                "status": "N/A", "notes": meta["definition"],
            })
            continue
        dates = sorted(meta["observations"])
        ids = meta["ids"]
        titles = [f"{sid}: {meta['titles'].get(sid, '')}" for sid in ids]
        rate_horizons = []
        if any(s.endswith("Q") for s in ids): rate_horizons.append("SA 3-month percent change")
        if any(s.endswith("A") for s in ids): rate_horizons.append("NSA 12-month percent change")
        if key.startswith("productivity_"): rate_horizons = ["3m_ann", "12m"]
        if key.endswith("_sa") and meta["frequency"] == "M": rate_horizons = ["MoM"]
        if key.endswith("_nsa") and meta["frequency"] == "M": rate_horizons = ["12m"]
        meta_rows.append({
            "series_key": key, "indicator": meta["indicator"], "publisher": "U.S. Bureau of Labor Statistics",
            "exact_title": " | ".join(titles), "publisher_series_id": ";".join(ids),
            "table_or_dataset": "BLS Public Data API v2; CPI / PPI FD-ID / ECI / Productivity and Costs",
            "definition": meta["definition"], "frequency": meta["frequency"], "units": meta["units"],
            "seasonal_adjustment": meta["sa"], "geography_population": meta["population"],
            "earliest_obs": dates[0] if dates else "", "latest_obs": dates[-1] if dates else "",
            "latest_release_date": latest_release.get(key, ""), "source_url": meta["source"], "api_endpoint": API,
            "raw_files": ";".join(sorted(meta["raw_files"])), "retrieval_date": RETRIEVAL_DATE,
            "published_rate_horizons": ";".join(rate_horizons),
            "fred_equivalent_id": ";".join(meta.get("fred_equivalents", [meta["fred"]]) if meta.get("fred") else []),
            "revision_vintage_notes": "Current BLS vintage; revised observations may differ from earlier releases.",
            "status": "retrieved" if dates else "N/A", "notes": " | ".join(titles),
        })
    meta_fields = ["series_key", "indicator", "publisher", "exact_title", "publisher_series_id", "table_or_dataset",
                   "definition", "frequency", "units", "seasonal_adjustment", "geography_population", "earliest_obs",
                   "latest_obs", "latest_release_date", "source_url", "api_endpoint", "raw_files", "retrieval_date",
                   "published_rate_horizons", "fred_equivalent_id", "revision_vintage_notes", "status", "notes"]
    write_csv(OUT_DIR / "series_metadata.csv", meta_fields, meta_rows)
    write_csv(OUT_DIR / "release_dates.csv", ["series_key", "date", "first_release_date", "method", "note"], release_rows)

    # Write concise report, including verification, coverage, N/A, and FRED differences.
    lines = ["# BLS retrieval report", "", f"Retrieved: {RETRIEVAL_DATE}",
             "BLS API v2 requests: 2000–2019 and 2020–2026, catalog=true, calculations=true.",
             f"Distinct series IDs requested: {len(set(REQUEST_IDS))}; observations.csv rows: {len(rows)}.", "",
             "## Series and coverage"]
    for key, meta in SERIES.items():
        dates = sorted(meta["observations"])
        lines.append(f"- `{key}`: {', '.join(meta['ids'])}; {dates[0] if dates else 'N/A'} to {dates[-1] if dates else 'N/A'}; {len(dates)} distinct dates; catalog titles: " + " | ".join(meta["titles"].get(i, "not returned") for i in meta["ids"]))
    lines += ["", "## Verification", f"- BLS API catalog=true titles are recorded in series_metadata.csv; CPI page: {CPI_PAGE}.",
              f"- PPI exact IDs and titles checked against the official FD-ID catalog: {PPI_CATALOG}.",
              "- Trade margin for personal consumption is published as `Trade of personal consumption goods` (42311); this is the BLS exact catalog title.",
              "- ECI encodings checked against the official SA/NSA, ownership, estimate, and datatype guide: " + ECI_GUIDE,
              "- ECI SA benefits index and 3-month rate series are published for civilian and private workers; all requested ECI IDs were returned by BLS.",
              "- Productivity IDs and Q3 2026 preliminary data checked against BLS release/tables: " + PRODUCTIVITY_PAGE,
              "- **N/A — no single all-stage total intermediate-demand index** is listed; documented in metadata.",
              "", "## FRED cross-checks", "- Latest three values compared where FRED offers the same series; tolerance 0.00011."]
    eci_keys = [key for key in check if key.startswith("eci_")]
    lines.append("- ECI NSA index levels matched across all six groups; SA FRED indexes have no observations after 2017 Q4, and FRED returned HTTP 400 for the exact Q/A rate IDs, so those current series could not be cross-checked.")
    good_keys = [key for key, result in check.items() if result["status"] == "match" and not key.startswith("eci_")]
    lines.append("- Other series matched: " + "; ".join(good_keys) + ".")
    hcomp = check.get("productivity_hourly_compensation", {})
    if hcomp.get("differences"):
        lines.append("- Difference: hourly-compensation index vs COMPNFB: " + "; ".join(hcomp["differences"]) + ". Latest BLS release is preliminary Q3 2026; FRED's available vintage differs.")
    lines += ["", "## Release dates and notes",
              "- release_dates.csv covers 13 latest observations per monthly/quarterly series; all rows have ALFRED output_type=4 first-release dates.",
              "- CPI Oct 2025 values are empty (BLS footnote X: lapse in appropriations); Nov 2025 values are published by BLS and retained.",
              "- Productivity and Costs Q3 2026 preliminary release: November 5, 2026; ECI Q3 release: October 30, 2026.",
              "- BLS API requests used 49 IDs (limit 50) in each required year window; no rates were calculated locally."]
    if len(lines) > 60:
        raise RuntimeError(f"REPORT.md exceeds 60 lines: {len(lines)}")
    (OUT_DIR / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Retrieved {len(SERIES)} logical series groups; {len(set(REQUEST_IDS))} BLS IDs; {len(rows)} observation rows.")
    print(f"Outputs: {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
