"""C2_build_history_coverage.py: reads saved BLS raw JSON (03_Data/Raw/bls_api_components_2015_2026_batch*_2026-11-13.json) and writes
outputs/component_series_history.csv(+_meta), outputs/component_series_coverage.csv(+_meta), outputs/C2_no_oct2026.csv.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C2_build_history_coverage.py"""
import json, glob, csv
from pathlib import Path
OUT = Path("02_Research/Subtasks/04_oct_pce_build/outputs")
fetch = {r["series_id"]: r for r in csv.DictReader(open(OUT/"series_to_fetch.csv"))}
hist, cov, nodata_msgs = [], [], {}
def mi(y, m): return int(y)*12 + int(m)-1
files = sorted(glob.glob("03_Data/Raw/bls_api_components_2015_2026_batch*_2026-11-13.json"))
for f in files:
    d = json.load(open(f))
    for m in d["message"]:
        if "net change" not in m:
            sid = m.split("Series ")[1].split(" Year")[0] if "Series " in m else m
            nodata_msgs.setdefault(sid, []).append(m.split(" Year: ")[-1] if "Year:" in m else m)
    for s in d["Results"]["series"]:
        sid = s["seriesID"]; rows = {}
        for r in s["data"]:
            if not r["period"].startswith("M") or r["period"] == "M13": continue
            codes = ";".join(x["code"] for x in r["footnotes"] if x.get("code"))
            v = "" if r["value"] == "-" else r["value"]
            hist.append([sid, r["year"], r["period"], v, codes, Path(f).name])
            rows[mi(r["year"], r["period"][1:])] = (v, codes)
        kind = fetch[sid]["kind"] if sid in fetch else ("PPI" if sid[:2] in ("PC", "WP") else "CPI")
        seas = fetch[sid]["seasonal"] if sid in fetch else ("SA" if sid[2] == "S" else "NSA")
        valid = sorted(k for k, (v, c) in rows.items() if v != "")
        if valid:
            first, last = valid[0], valid[-1]
            ym = lambda k: f"{k//12}-{k%12+1:02d}"
            miss = [k for k in range(mi(2017, 1), last+1) if k not in valid]
            o25 = rows.get(mi(2025, 10)); o26 = rows.get(mi(2026, 10))
            rec = [k for k in range(mi(2025, 11), mi(2026, 10)+1) if k not in valid]
            cov.append([sid, kind, seas, "Y" if sid in fetch else "N (extra)", ym(first), ym(last), "Y" if o26 and o26[0] != "" else "N",
                        len(miss), ";".join(ym(k) for k in miss) if len(miss) <= 6 else f"{len(miss)} months, first {ym(miss[0])}, last {ym(miss[-1])}",
                        ("blank, footnote " + o25[1]) if o25 and o25[0] == "" else (f"value {o25[0]}" if o25 else "absent from response"),
                        ";".join(sorted(set(nodata_msgs.get(sid, []))))[:120], len(rec), ";".join(ym(k) for k in rec)])
        else:
            cov.append([sid, kind, seas, "Y" if sid in fetch else "N (extra)", "", "", "N", "", "", "", "NO DATA", "", ""])
hist.sort(key=lambda r: (r[0], r[1], r[2]))
with open(OUT/"component_series_history.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["series_id", "year", "period", "value", "footnote_codes", "raw_file"]); w.writerows(hist)
cov.sort()
with open(OUT/"component_series_coverage.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["series_id", "kind", "seasonal", "in_series_to_fetch", "first_month", "last_month", "oct2026_present", "missing_months_since_2017-01", "missing_detail", "oct2025_appearance", "bls_api_message_years_without_data", "n_missing_2025-11_to_2026-10", "missing_2025-11_to_2026-10"]); w.writerows(cov)
with open(OUT/"C2_no_oct2026.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["series_id", "kind", "seasonal", "last_month"])
    for c in cov:
        if c[6] == "N": w.writerow([c[0], c[1], c[2], c[5]])
for name, rows, desc in (("component_series_history", len(hist), "Tidy long monthly values from BLS API v2 (blank value = BLS '-' i.e. not available; footnote X = 2025 lapse in appropriations; P = preliminary). Monthly M01-M12 only. Values as published by BLS API on 2026-11-13 (current vintage)."),
                         ("component_series_coverage", len(cov), "One row per series; missing count is months from 2017-01 through each series' last valid month with no value.")):
    with open(OUT/f"{name}_meta.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["field", "value"])
        for k, v in (("file", f"{name}.csv"), ("rows", rows), ("source", "BLS Public Data API v2, api.bls.gov/publicAPI/v2/timeseries/data/"), ("retrieved", "2026-11-13"), ("raw_files", ";".join(Path(f).name for f in files)), ("script", "code/C2_build_history_coverage.py"), ("description", desc)):
            w.writerow([k, v])
print(len(hist), len(cov))
