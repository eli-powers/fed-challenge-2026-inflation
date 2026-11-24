#!/usr/bin/env python3
"""Retrieve official demand indicators for the College Fed Challenge."""
import csv
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import fetch_utils as fu

GROUP = "official"
TODAY = fu.RETRIEVAL_DATE
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw" / GROUP
OUT = ROOT / "processed" / GROUP
START = "2015-01-01"
FRED = "https://api.stlouisfed.org/fred"
BEA = "https://apps.bea.gov/api/data"
BEA_URL = "https://apps.bea.gov/api/"
records, observations, rawfiles = [], [], {}
BEA_PARAM_CACHE = {}


def save(publisher, dataset, content, ext="json"):
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", dataset).strip("_")[:90]
    fn = f"{publisher}_{safe}_{TODAY}.{ext}"
    rel = fu.save_raw(GROUP, fn, content)
    rawfiles.setdefault(dataset, []).append(fn)
    return fn


def jbytes(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2).encode()


def record_meta(key, channel, indicator, publisher, sid, title, freq, units, sa,
                earliest, latest, release, url, raw_names, status="retrieved", notes=""):
    records.append({"series_key": key, "channel": channel, "indicator": indicator,
                    "publisher": publisher, "source_id": sid, "exact_title": title,
                    "frequency": freq, "units": units, "seasonal_adjustment": sa,
                    "earliest_obs": earliest, "latest_obs": latest,
                    "latest_release_date": release, "source_url": url,
                    "raw_files": ";".join(raw_names), "retrieval_date": TODAY,
                    "status": status, "notes": notes})


def add_observations(key, rows, freq, units, sa, sid, rawname, note=""):
    for row in rows:
        dt = row["date"]
        if dt < START:
            continue
        val = row["value"]
        if val in (None, "", "."):
            continue
        if freq == "Q":
            m = re.match(r"(\d{4})-?Q([1-4])", dt)
            if m:
                dt = f"{m.group(1)}-{(int(m.group(2))-1)*3+1:02d}-01"
        elif len(dt) == 7:
            dt += "-01"
        observations.append({"series_key": key, "date": dt, "frequency": freq,
                             "value": val, "units": units,
                             "seasonal_adjustment": sa, "source_id": sid,
                             "raw_file": rawname, "note": note})


def fred_series(sid, key, channel, indicator, expected=None, note=""):
    """Fetch metadata and observations from FRED; originating publisher is retained."""
    meta_b = fu.http_get(FRED + "/series", {"series_id": sid,
          "api_key": fu.get_key("FRED_API_KEY"), "file_type": "json"})
    meta_fn = save("FRED", f"{sid}_metadata", meta_b)
    meta = json.loads(meta_b).get("seriess", [{}])[0]
    if not meta:
        raise ValueError(f"FRED metadata not found for {sid}")
    title = meta.get("title", "")
    if expected and not any(s.lower() in title.lower() for s in expected):
        # Preserve the actual metadata and make the mismatch visible in notes.
        note = (note + "; " if note else "") + f"ID title differs from requested wording: {title}"
    obs_b = fu.http_get(FRED + "/series/observations", {"series_id": sid,
          "api_key": fu.get_key("FRED_API_KEY"), "file_type": "json",
          "observation_start": START, "observation_end": date.today().isoformat()})
    obs_fn = save("FRED", f"{sid}_observations", obs_b)
    payload = json.loads(obs_b)
    rows = [{"date": o["date"], "value": o.get("value")} for o in payload.get("observations", [])]
    units = meta.get("units", "")
    freq = "Q" if meta.get("frequency_short") in ("Q", "Quarterly") else "M"
    sa = meta.get("seasonal_adjustment", "")
    add_observations(key, rows, freq, units, sa, sid, obs_fn, note)
    vals = [r for r in rows if r["value"] not in (None, ".", "")]
    origin = meta.get("notes") or ""
    publisher = "BEA" if "Bureau of Economic Analysis" in origin or sid in BEA_FRED else (
                "U.S. Census Bureau" if sid in CENSUS_FRED else "Federal Reserve Board")
    release = (meta.get("last_updated", "") or "")[:10]
    record_meta(key, channel, indicator, publisher, sid, title, freq, units, sa,
                vals[0]["date"] if vals else "", vals[-1]["date"] if vals else "",
                release, f"https://fred.stlouisfed.org/series/{sid}", [meta_fn, obs_fn],
                notes=note)
    return vals, meta, obs_fn


BEA_FRED = {"PCEC96", "PCEDG", "PCESV", "DSPIC96", "PSAVERT"}
CENSUS_FRED = {"RSAFS", "RSFSXMV", "RSXFS", "NEWORDER", "ANXAVS", "A34SNO",
               "A34SVS", "RSMVPD", "RSGASS", "RSBMGESD", "RSFSDP"}


def bea_call(params, tag):
    safe=re.sub(r"[^A-Za-z0-9_-]+","_",tag).strip("_")[:90]
    cached=RAW / f"BEA_{safe}_{TODAY}.json"
    if cached.exists():
        return json.loads(cached.read_bytes()),cached.name
    q = {**params, "UserID": fu.get_key("BEA_API_KEY"), "ResultFormat": "JSON"}
    b = fu.http_get(BEA, q)
    fn = save("BEA", tag, b)
    obj = json.loads(b)
    if "BEAAPI" in obj and "Error" in obj["BEAAPI"]:
        raise RuntimeError(str(obj["BEAAPI"]["Error"]))
    return obj, fn


def bea_tables(dataset):
    """Fetch or reuse today's saved official table-name response."""
    if dataset in BEA_PARAM_CACHE:
        return BEA_PARAM_CACHE[dataset]
    tag=f"{dataset}_table_names"
    existing=RAW / f"BEA_{tag}_{TODAY}.json"
    if existing.exists():
        payload=json.loads(existing.read_bytes())
        fn=existing.name
    else:
        payload,fn=bea_call({"method":"GetParameterValues","datasetname":dataset,
                             "ParameterName":"TableName"},tag)
    BEA_PARAM_CACHE[dataset]=(payload,fn)
    return payload,fn


def bea_series(table, channel, chosen, suffix="", freq="M", start_year=2015, dataset="NIPA"):
    # Verify the requested table exists and save publisher parameter metadata.
    param, pfn = bea_tables(dataset)
    valid_tables=param.get("BEAAPI",{}).get("Results",{}).get("ParamValue",[])
    if not any(v.get("TableName")==table for v in valid_tables):
        raise RuntimeError(f"BEA GetParameterValues did not verify table {table}")
    years=",".join(str(y) for y in range(start_year,date.today().year+1))
    data_tag=f"{dataset}_{table}_{freq}"
    cached_data=RAW / f"BEA_{data_tag}_{TODAY}.json"
    if not cached_data.exists() and dataset=="NIUnderlyingDetail" and table=="U20405":
        cached_data=RAW / f"BEA_test_U20405_{freq}_{TODAY}.json"
    if cached_data.exists():
        data=json.loads(cached_data.read_bytes()); dfn=cached_data.name
    else:
        data, dfn = bea_call({"method": "GetData", "datasetname": dataset,
                              "TableName": table, "Frequency": freq,
                              "Year": years}, data_tag)
    results = data.get("BEAAPI", {}).get("Results", {})
    rows = results.get("Data", [])
    if not rows:
        raise RuntimeError(f"No data returned for BEA {table}")
    found = {}
    for name, matcher, key, units, note in chosen:
        candidates = [r for r in rows if matcher(r.get("LineDescription", ""))]
        # Manager fix (2026-09-27): a description can repeat within a table (e.g. T50306 line 9
        # "Equipment" = nonresidential, line 26 "Equipment" = residential). Keep the first line only.
        if candidates:
            first_line = min(int(r.get("LineNumber", 10**6)) for r in candidates)
            candidates = [r for r in candidates if int(r.get("LineNumber", 10**6)) == first_line]
        if not candidates:
            record_meta(key, channel, name, "BEA", table, name, freq, units, "SAAR",
                        "", "", "", BEA_URL, [pfn, dfn], status="N/A",
                        notes="Requested exact line not present in BEA table response; no substitution.")
            continue
        # Prefer exact descriptions or the most concise match when table labels
        # include a parenthetical qualifier.
        row = sorted(candidates, key=lambda x: len(x.get("LineDescription", "")))[0]
        desc = row.get("LineDescription", "")
        vals = []
        for r in candidates:
            if r.get("LineDescription") != desc:
                continue
            tp = r.get("TimePeriod", "")
            if freq == "Q":
                m = re.match(r"(\d{4})Q([1-4])", tp)
                if not m or int(m.group(1)) < start_year: continue
                dt = f"{m.group(1)}Q{m.group(2)}"
            else:
                m = re.match(r"(\d{4})M(\d{1,2})", tp)
                if not m or int(m.group(1)) < start_year: continue
                dt = f"{m.group(1)}-{int(m.group(2)):02d}"
            val = r.get("DataValue", "")
            val = val.replace(",", "") if isinstance(val, str) else val
            vals.append({"date": dt, "value": val})
        series_code = row.get("SeriesCode") or table
        add_observations(key, vals, freq, units, "SAAR", series_code, dfn, note)
        release_time = ""
        record_meta(key, channel, name, "BEA", series_code, desc, freq, units, "SAAR",
                    vals[0]["date"] if vals else "", vals[-1]["date"] if vals else "",
                    release_time, BEA_URL, [pfn, dfn], notes=note)
        found[key] = vals
    return found


def csv_direct(url, name, publisher="Michigan", full=False, note=""):
    b = fu.http_get(url)
    fn = save(publisher, name, b, "csv")
    text = b.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise RuntimeError(f"No CSV rows from {url}")
    # Michigan CSV headers vary across vintage releases; identify date and
    # requested index columns by exact header fragments and preserve publisher names.
    headers = reader.fieldnames or []
    month_col = next((h for h in headers if h.lower()=="month"), None)
    year_col = next((h for h in headers if h.lower() in ("yyyy","year")), None)
    date_col = next((h for h in headers if "date" in h.lower()), headers[0])
    targets = [h for h in headers if h not in (month_col, year_col)] if month_col and year_col else [h for h in headers if h != date_col]
    code_names={"ICS_ALL":"Index of Consumer Sentiment","ICC":"Index of Current Economic Conditions","ICE":"Index of Consumer Expectations"}
    for col in targets:
        key = "umich_" + re.sub(r"[^a-z0-9]+", "_", code_names.get(col,col).lower()).strip("_")
        vals=[]
        for r in rows:
            rawdate = (r.get(date_col) or "").strip()
            if month_col and year_col:
                mon=(r.get(month_col) or "").strip(); yr=(r.get(year_col) or "").strip()
                month_num={x.lower():i for i,x in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"],1)}.get(mon.lower())
                if not month_num or not yr: continue
                dt=f"{int(yr):04d}-{month_num:02d}"
            else:
                m = re.search(r"(\d{4})[-/](\d{1,2})", rawdate)
                if not m: continue
                dt=f"{m.group(1)}-{int(m.group(2)):02d}"
            value=(r.get(col) or "").strip()
            if not value: continue
            vals.append({"date":dt,"value":value})
        if not full:
            vals=[r for r in vals if r["date"] >= START[:7]]
        add_observations(key, vals, "M", "Index", "NSA", col, fn,
                         (note + "; full history retained" if full else note))
        record_meta(key, "Consumer", code_names.get(col,col), "University of Michigan", col, code_names.get(col,col), "M", "Index", "NSA",
                    vals[0]["date"] if vals else "", vals[-1]["date"] if vals else "",
                    "", url, [fn], notes=note + (" Full history retained for percentile calculations." if full else ""))


def michigan_current():
    """Append the latest PRELIMINARY month, flagged "(P)" in the publisher's current tables (tbcics, tbciccice).
    The historical files (tbmics, tbmiccice) carry final readings only. Final values replace this on a later run."""
    months = {x.lower(): i for i, x in enumerate(["January","February","March","April","May","June","July","August",
                                                   "September","October","November","December"], 1)}
    for url, name, cols in [("https://www.sca.isr.umich.edu/files/tbcics.csv", "tbcics_current", {4: "umich_index_of_consumer_sentiment"}),
                            ("https://www.sca.isr.umich.edu/files/tbciccice.csv", "tbciccice_current",
                             {3: "umich_index_of_current_economic_conditions", 5: "umich_index_of_consumer_expectations"})]:
        try:
            b = fu.http_get(url)
        except Exception as e:
            print(f"Michigan current table {name} not retrieved: {type(e).__name__}: {e}")
            continue
        fn = save("Michigan", name, b, "csv")
        for row in csv.reader(io.StringIO(b.decode("utf-8-sig", errors="replace"))):
            if len(row) < 6 or "(P)" not in row[0] or not row[1].strip().isdigit():
                continue
            mon = months.get(row[0].replace("(P)", "").strip().lower())
            dt = f"{int(row[1]):04d}-{mon:02d}-01"
            for idx, key in cols.items():
                latest = max((o["date"] for o in observations if o["series_key"] == key), default="")
                if not row[idx].strip() or dt <= latest:
                    continue
                add_observations(key, [{"date": dt, "value": row[idx].strip()}], "M", "Index", "NSA",
                                 {"umich_index_of_consumer_sentiment": "ICS_ALL", "umich_index_of_current_economic_conditions": "ICC",
                                  "umich_index_of_consumer_expectations": "ICE"}[key], fn,
                                 "PRELIMINARY (flagged '(P)' in the publisher's current table); final reading replaces it on a later run.")
                for m in records:
                    if m["series_key"] == key:
                        m["latest_obs"] = dt
                        m["raw_files"] = (m["raw_files"] + ";" if m["raw_files"] else "") + fn
                        m["notes"] = (m["notes"] + " " if m["notes"] else "") + f"Latest month {dt[:7]} is PRELIMINARY (current table {name})."


def census_construction():
    url = "https://www.census.gov/construction/c30/xlsx/privsatime.xlsx"
    b = fu.http_get(url)
    fn = save("Census", "C30_private_SA_historical", b, "xlsx")
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(b), data_only=True, read_only=True)
        all_rows=[]
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                all_rows.append([str(x).strip() if x is not None else "" for x in row])
        header_idx=next(i for i,r in enumerate(all_rows) if any(c.strip().lower()=="data center" for c in r))
        header=all_rows[header_idx]
        center_col=next(j for j,c in enumerate(header) if c.strip().lower()=="data center")
        nonres_col=next(j for j,c in enumerate(header) if c.strip().lower()=="nonresidential")
        def numeric(s):
            try: return float(str(s).replace(",", "").replace("$", ""))
            except Exception: return None
        def parse_month(s):
            m=re.match(r"([A-Za-z]{3})-(\d{2})",s)
            if not m:return ""
            mm={x.lower():i for i,x in enumerate(["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"],1)}.get(m.group(1).lower())
            yy=int(m.group(2)); yyyy=2000+yy if yy<80 else 1900+yy
            return f"{yyyy:04d}-{mm:02d}" if mm else ""
        specs=[("construction_private_data_center","Private nonresidential data center construction spending",center_col,"C30 private office: data center","Value Put in Place: Data Center"),
               ("private_nonresidential_construction","Total private nonresidential construction spending",nonres_col,"C30 private construction: nonresidential","Value of Private Construction Put in Place: Nonresidential")]
        for key,title,col,sid,exact in specs:
            vals=[]
            for r in all_rows[header_idx+1:]:
                if col>=len(r) or not r[0]:continue
                dt=parse_month(r[0]); v=numeric(r[col])
                if dt and v is not None and dt>=START[:7]: vals.append({"date":dt,"value":v})
            if vals:
                vals.sort(key=lambda x:x["date"])
                add_observations(key,vals,"M","Millions of dollars, SAAR","SA",sid,fn,"Census C30 Value Put in Place")
                record_meta(key,"AI buildout",title,"U.S. Census Bureau",sid,exact,"M","Millions of dollars, SAAR","SA",
                            vals[0]["date"],vals[-1]["date"],"",url,[fn],notes="Census C30 historical monthly seasonally adjusted annual rate series.")
            else:
                record_meta(key,"AI buildout",title,"U.S. Census Bureau",sid,exact,"M","Millions of dollars, SAAR","SA",
                            "","","",url,[fn],status="N/A",notes="Official private SA workbook contains no observations from January 2015 for this category.")
    except Exception as e:
        record_meta("construction_private_data_center","AI buildout","Private nonresidential data center construction spending","U.S. Census Bureau",
                    "C30 private office: data center","Value Put in Place: Data Center","M","Millions of dollars, SAAR","SA",
                    "","","",url,[fn],status="N/A",notes=f"Workbook downloaded but could not be parsed ({type(e).__name__}); inspect workbook.")


def write_outputs():
    OUT.mkdir(parents=True, exist_ok=True)
    obs_cols=["series_key","date","frequency","value","units","seasonal_adjustment","source_id","raw_file","note"]
    meta_cols=["series_key","channel","indicator","publisher","source_id","exact_title","frequency","units","seasonal_adjustment","earliest_obs","latest_obs","latest_release_date","source_url","raw_files","retrieval_date","status","notes"]
    for path, rows, cols in [(OUT/"observations.csv",observations,obs_cols),(OUT/"series_metadata.csv",records,meta_cols)]:
        if path.name=="observations.csv": rows.sort(key=lambda x:(x["series_key"],x["date"]))
        with path.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    # Concise report with latest available observation per series.
    bykey={}
    for o in observations: bykey.setdefault(o["series_key"],[]).append(o)
    items=[]
    for m in records:
        if m["status"]!="retrieved": continue
        vals=bykey.get(m["series_key"],[])
        latest=max(vals,key=lambda x:x["date"]) if vals else None
        items.append(f"`{m['series_key']}` ({m['source_id']}) {m['earliest_obs']}–{m['latest_obs']}; latest {latest['date']}={latest['value']} {m['units']}" if latest else f"`{m['series_key']}` ({m['source_id']}): no observations")
    lines=["# Official demand indicators retrieval", "", f"Retrieved {TODAY}.", "",
           "## Retrieved series (key, ID, range, latest)"]
    for i in range(0,len(items),3): lines.append("- " + " | ".join(items[i:i+3]))
    lines += ["", "## N/A"]
    na=[m for m in records if m["status"]=="N/A"]
    lines += [f"- `{m['series_key']}`: {m['notes']} Source: {m['source_url']}" for m in na] or ["- None"]
    lines += ["", "## Verification and caveats",
              "- FRED series IDs/titles were checked against FRED metadata; FRED-sourced series retain their originating publisher in metadata.",
              "- BEA table IDs and line descriptions were checked through BEA GetParameterValues/GetData; Census construction was sourced from the official C30 historical workbook.",
              "- Observations are native frequency and untransformed; no interpolation, carry-forward, or derived rates were applied.",
              "- Census data-center spending is a dedicated monthly category from the private SA workbook; Michigan publisher CSVs retain full histories and exact index columns. Web interviewing began in 2024 (series break).",
              "- BEA's 2026 annual update scheduled for September 30, 2026 will revise PCE, income, saving, and investment data from Q1 2021 onward; this retrieval is the pre-update vintage.",
              "- FRED last-updated dates are retained as update dates; BEA and Census release dates are blank when not included with their data responses."]
    (OUT/"REPORT.md").write_text("\n".join(lines[:40])+"\n",encoding="utf-8")


def main():
    # BEA fixed investment, quarterly; publisher-reported percent changes kept separate.
    inv_lines=[
        ("Information processing equipment",lambda s:"information processing equipment" in s.lower(),"ai_investment_info_processing_equipment","Millions of chained 2017 dollars, SAAR",""),
        ("Software",lambda s:s.strip().lower()=="software","ai_investment_software","Millions of chained 2017 dollars, SAAR",""),
        ("Equipment total",lambda s:s.strip().lower()=="equipment","ai_investment_equipment_total","Millions of chained 2017 dollars, SAAR",""),
        ("Intellectual property products total",lambda s:s.strip().lower()=="intellectual property products","ai_investment_ip_products_total","Millions of chained 2017 dollars, SAAR",""),
        ("Nonresidential private fixed investment total",lambda s:s.strip().lower()=="nonresidential","ai_investment_nonresidential_total","Millions of chained 2017 dollars, SAAR","")]
    bea_series("T50306","AI buildout",[(a,b,k,"Millions of chained 2017 dollars, SAAR",n) for a,b,k,_,n in inv_lines],freq="Q")
    bea_series("T50301","AI buildout",[(a,b,k+"_pct_qq_saar","Percent change, SAAR",n) for a,b,k,_,n in inv_lines],freq="Q")
    # Monthly PCE levels, BEA NIPA tables. Rows are matched by BEA line descriptions.
    bea_series("T20806","Consumer",[
      ("Real PCE total",lambda s:s.strip().lower().startswith("personal consumption expenditures"),"pce_real_total","Millions of chained 2017 dollars, SAAR",""),
      ("Real PCE goods",lambda s:s.strip().lower()=="goods","pce_real_goods","Millions of chained 2017 dollars, SAAR",""),
      ("Real PCE services",lambda s:s.strip().lower()=="services","pce_real_services","Millions of chained 2017 dollars, SAAR","")],freq="M")
    bea_series("U20405","Consumer",[
      ("Nominal PCE total",lambda s:s.strip().lower()=="personal consumption expenditures","pce_nominal_total","Millions of dollars, SAAR",""),
      ("Gasoline and other energy goods",lambda s:"gasoline and other energy goods" in s.lower(),"pce_nominal_gasoline_energy_goods","Millions of dollars, SAAR","")],freq="M",dataset="NIUnderlyingDetail")
    # FRED identifiers are verified by retrieving source metadata and observations.
    # This list is deliberately checked on FRED before output; unsupported IDs become N/A.
    series=[
      ("DSPIC96","Consumer","Real disposable personal income",["Real Disposable Personal Income"]),
      ("PSAVERT","Consumer","Personal saving rate",["Personal Saving Rate"]),
      ("NEWORDER","AI buildout","Manufacturers' new orders: nondefense capital goods excluding aircraft",["New Orders: Nondefense Capital Goods Excluding Aircraft"]),
      ("ANXAVS","AI buildout","Manufacturers' shipments: nondefense capital goods excluding aircraft",["Shipments: Nondefense Capital Goods Excluding Aircraft"]),
      ("A34SNO","AI buildout","Manufacturers' new orders: computers and electronic products",["New Orders: Computers and Electronic Products"]),
      ("A34SVS","AI buildout","Manufacturers' shipments: computers and electronic products",["Shipments: Computers and Electronic Products"]),
      ("IPG3344S","AI buildout","Industrial production: semiconductors and other electronic components",["NAICS = 3344"]),
      ("RSAFS","Consumer","Retail and food services total",["Advance Retail Sales: Retail Trade and Food Services"]),
      ("RSFSXMV","Consumer","Retail and food services excluding motor vehicle and parts dealers",["Excluding Motor Vehicle and Parts Dealers"]),
      ("RSXFS","Consumer","Retail trade excluding food services",["Advance Retail Sales: Retail Trade"]),
      ("RSMVPD","Consumer","Motor vehicle and parts dealers",["Motor Vehicle and Parts Dealers"]),
      ("RSGASS","Consumer","Gasoline stations",["Gasoline Stations"]),
      ("RSBMGESD","Consumer","Building materials, garden equipment and supplies dealers",["Building Materials, Garden Equipment and Supplies Dealers"]),
      ("RSFSDP","Consumer","Food services and drinking places",["Food Services and Drinking Places"]),
      ("HNONWPDPI","Consumer","Household and nonprofit net worth as percent of disposable personal income",["Households and Nonprofit Organizations; Net Worth as a Percentage of Disposable Personal Income"]),
      ("TNWBSHNO","Consumer","Household and nonprofit net worth level",["Households and Nonprofit Organizations; Net Worth"]),
      ("REVOLSL","Consumer","Revolving consumer credit outstanding",["Revolving Consumer Credit"]),
      ("TOTALSL","Consumer","Total consumer credit outstanding",["Total Consumer Credit"]),
    ]
    for sid,ch,ind,expected in series:
      key=re.sub(r"[^a-z0-9]+","_",ind.lower()).strip("_")
      try: fred_series(sid,key,ch,ind,expected)
      except Exception as e:
        # Save no fabricated observation; record ID failure and reason.
        record_meta(key,ch,ind,"FRED",sid,ind,"M","","", "","","",
                    f"https://fred.stlouisfed.org/series/{sid}",[],status="N/A",
                    notes=f"Publisher/FRED verification or retrieval failed: {type(e).__name__}: {e}")
    # Retail total and selected series titles sometimes differ; the title is retained verbatim.
    # Quarterly Z.1 series are native Q and are handled in FRED metadata.
    # Michigan publisher CSVs: retain complete histories from original source files.
    for url,name in [("https://www.sca.isr.umich.edu/files/tbmics.csv","tbmics"),
                     ("https://www.sca.isr.umich.edu/files/tbmiccice.csv","tbmiccice")]:
      try: csv_direct(url,name,full=True,note="Publisher-reported index; interview mode moved to web in 2024 (series break).")
      except Exception as e:
        record_meta("umich_"+name,"Consumer","University of Michigan consumer sentiment series","University of Michigan",name,name,"M","Index","NSA","","","",url,[],status="N/A",notes=f"Publisher CSV retrieval/parsing failed: {type(e).__name__}: {e}")
    michigan_current()
    census_construction()
    write_outputs()
    print(f"Wrote {len(observations)} observations across {len(records)} metadata rows to {OUT}")


if __name__ == "__main__":
    main()
