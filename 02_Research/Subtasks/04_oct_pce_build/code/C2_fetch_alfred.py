"""C2_fetch_alfred.py: ALFRED all-vintage pulls (output_type=1) for (a) the 28 PPI series in series_to_fetch.csv + 2 extra portfolio-management PPIs,
(b) ten large CPI SA series. Observations from 2024-11-01. Saves raw JSON to 03_Data/Raw/ and an ID-resolution log to outputs/C2_alfred_id_resolution.csv.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C2_fetch_alfred.py
Key read from .env; never printed or saved (asserted absent from every saved body)."""
import json, re, csv, time, urllib.request, urllib.parse, urllib.error
from pathlib import Path
DATE = "2026-11-11"; RAW = Path("03_Data/Raw"); OUT = Path("02_Research/Subtasks/04_oct_pce_build/outputs")
K = next(re.match(r"\s*(?:export\s+)?FRED_API_KEY=(.*)", l).group(1).strip().strip("'\"") for l in open(Path(".env")) if re.match(r"\s*(?:export\s+)?FRED_API_KEY=", l))
def call(path, **p):
    p.update(api_key=K, file_type="json")
    try:
        with urllib.request.urlopen(urllib.request.Request("https://api.stlouisfed.org/fred/" + path + "?" + urllib.parse.urlencode(p), headers={"User-Agent": "research-script"}), timeout=120) as r:
            body = r.read().decode(); assert K not in body; return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    finally: time.sleep(0.25)
ppi = [r["series_id"] for r in csv.DictReader(open(OUT/"series_to_fetch.csv")) if r["kind"] == "PPI"] + ["PCU5239405239401", "PCU5239405239402"]
cpi = ["CUSR0000SEHC01", "CUSR0000SEMF01", "CUSR0000SEFV01", "CUSR0000SETB", "CUSR0000SEMC04", "CUSR0000SS45021", "CUSR0000SETD", "CUSR0000SEHF01", "CUSR0000SAA2", "CUSR0000SETA02",
       "CUSR0000SEFX", "CUSR0000SAA1", "CUSR0000SERE01"]  # last three: next-largest weights, substituting for SEMF01, SEFV01, SS45021 (not carried by FRED)
log = []
for sid in ppi + cpi:
    cands = [sid] + ([sid.replace("-", "")] if "-" in sid else [])
    found = None; tried = []
    for c in cands:
        st, body = call("series", series_id=c); tried.append(f"{c}:{st}")
        if st == 200: found = c; (RAW/f"FRED_{c}_seriesinfo_{DATE}.json").write_text(body); break
    if not found: log.append([sid, "", "NOT FOUND", ";".join(tried), 0]); continue
    st, body = call("series/observations", series_id=found, realtime_start="1776-07-04", realtime_end="9999-12-31", observation_start="2024-11-01", output_type=1, limit=100000)
    assert st == 200, (sid, st)
    (RAW/f"ALFRED_{found}_all_vintages_from2024-11_{DATE}.json").write_text(body)
    log.append([sid, found, "OK", ";".join(tried), json.loads(body)["count"]])
    print(sid, found, json.loads(body)["count"])
with open(OUT/"C2_alfred_id_resolution.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["bls_series_id", "fred_series_id", "status", "ids_tried", "n_observation_rows"]); w.writerows(log)
