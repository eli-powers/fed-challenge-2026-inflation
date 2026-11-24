"""Pull BLS's own published 1-month percent changes for the series used directly (as published) in the
October 2026 build, so the notebook can compare them with the changes we compute from index levels.
Run from the project root:  python3 "02_Research/Subtasks/04_oct_pce_build/code/K_fetch_bls_pct_changes.py"
Input:  outputs/D_build_2026-10_lines.csv (series of the direct lines)
Output: 03_Data/Raw/bls_api_direct_pct_changes_2026-11-13.json (raw API responses, never edited)"""
import json, os, urllib.request
from pathlib import Path
import pandas as pd
SUB = Path("02_Research/Subtasks/04_oct_pce_build")
OUTF = Path("03_Data/Raw/bls_api_direct_pct_changes_2026-11-13.json")
env = {}
for l in open(os.path.expanduser(".env")):
    l = l.strip().replace("export ", "")
    if "=" in l and not l.startswith("#"):
        k, v = l.split("=", 1); env[k] = v.strip().strip('"').strip("'")
lines = pd.read_csv(SUB / "outputs/D_build_2026-10_lines.csv")
ids = sorted(set(lines[lines["cat"].isin(["observed_published", "proxied"])].inputs))
out = []
for i in range(0, len(ids), 50):
    body = json.dumps({"seriesid": ids[i:i + 50], "startyear": "2026", "endyear": "2026", "calculations": True,
                       "registrationkey": env["BLS_API_KEY"]}).encode()
    req = urllib.request.Request("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=body,
                                 headers={"Content-type": "application/json", "User-Agent": env.get("BLS_CONTACT_UA", "research-client")})
    r = json.load(urllib.request.urlopen(req, timeout=90))
    print("batch", i // 50 + 1, r["status"], len(r["Results"]["series"]), "series")
    if r["status"] != "REQUEST_SUCCEEDED":
        raise SystemExit("partial failure; nothing saved")
    out.append(r)
if OUTF.exists():
    raise SystemExit(f"{OUTF} exists; not overwriting")
OUTF.write_text(json.dumps(out))
print("saved", OUTF, len(ids), "series")
