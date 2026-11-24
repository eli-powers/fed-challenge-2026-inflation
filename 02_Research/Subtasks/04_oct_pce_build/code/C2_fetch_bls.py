"""C2_fetch_bls.py: pull 277 series_to_fetch.csv series + extras from BLS API v2, Jan 2015 - latest. Saves raw JSON to 03_Data/Raw/.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C2_fetch_bls.py
Keys read from .env; never printed or saved. A batch is saved only if status is REQUEST_SUCCEEDED
and every requested series is returned with no error message; otherwise nothing is saved and it is retried."""
import re, csv, json, time, urllib.request
from pathlib import Path
DATE = "2026-11-13"; RAW = Path("03_Data/Raw"); OUT = Path("02_Research/Subtasks/04_oct_pce_build/outputs")
env = {}
for l in open(Path(".env")):
    m = re.match(r"\s*(?:export\s+)?(\w+)=(.*)", l)
    if m: env[m.group(1)] = m.group(2).strip().strip("'\"")
EXTRA = ["PCU5239405239401", "PCU5239405239402",           # old-method portfolio mgmt PPIs (brief)
         "CUUR0000SEGD01", "CUSR0000SEGD01",               # CPI Legal services (old source E1GAL1/E1AXS1)
         "CUUR0000SEMD", "CUSR0000SEMD",                   # CPI Hospital and related services (old source E1MEF1)
         "CUSR0000SEEE02"]                                 # CPI Computer software SA (old source NSA only; harmless extra)
ids = [r["series_id"] for r in csv.DictReader(open(OUT/"series_to_fetch.csv"))]
ids += [s for s in EXTRA if s not in ids]
print(len(ids), "series")
def post(batch):
    body = json.dumps({"seriesid": batch, "startyear": "2015", "endyear": "2026", "registrationkey": env["BLS_API_KEY"]}).encode()
    req = urllib.request.Request("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=body,
        headers={"Content-Type": "application/json", "User-Agent": env.get("BLS_CONTACT_UA", "research")})
    with urllib.request.urlopen(req, timeout=180) as r: return json.loads(r.read())
for i in range(0, len(ids), 50):
    batch = ids[i:i+50]; n = i//50 + 1
    for attempt in range(3):
        try:
            d = post(batch)
        except Exception as e:
            print("batch", n, "attempt", attempt, type(e).__name__); time.sleep(5); continue
        got = {s["seriesID"] for s in d.get("Results", {}).get("series", [])}
        msgs = [m for m in d.get("message", []) if "net change" not in m]
        ok = d.get("status") == "REQUEST_SUCCEEDED" and got == set(batch) and not msgs
        print("batch", n, d.get("status"), len(got), "of", len(batch), "msgs:", msgs[:5])
        if ok or attempt == 2:
            # save even if some series are empty-but-returned; refuse only when status failed or series missing
            if d.get("status") == "REQUEST_SUCCEEDED" and got == set(batch):
                (RAW/f"bls_api_components_2015_2026_batch{n}_{DATE}.json").write_text(json.dumps(d))
                print("  saved")
            break
        time.sleep(5)
