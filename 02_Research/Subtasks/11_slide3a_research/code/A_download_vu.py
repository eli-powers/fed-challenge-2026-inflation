"""Download JOLTS openings, unemployed level and unemployment rate (FRED API + BLS API cross-check).
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/A_download_vu.py
Writes raw files (never edited afterward) to 03_Data/Raw/S3A_A_vu_2026-11-15/. Keys loaded from .env."""
import json, os, urllib.request, urllib.parse
from pathlib import Path
ROOT = Path.cwd()
RAW = ROOT / "03_Data/Raw/S3A_A_vu_2026-11-15"
RAW.mkdir(parents=True, exist_ok=True)
keys = {}
for line in open(os.path.expanduser(".env")):
    line = line.strip().replace("export ", "")
    if "=" in line:
        k, v = line.split("=", 1); keys[k] = v.strip().strip('"').strip("'")
UA = keys.get("BLS_CONTACT_UA", "research-script")
def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()
for sid in ["JTSJOL", "UNEMPLOY", "UNRATE"]:
    base = "https://api.stlouisfed.org/fred/"
    q = urllib.parse.urlencode({"series_id": sid, "api_key": keys["FRED_API_KEY"], "file_type": "json", "observation_start": "2000-12-01"})
    obs = json.loads(get(base + "series/observations?" + q))
    info = json.loads(get(base + "series?" + q.replace("&observation_start=2000-12-01", "")))
    for d in (obs, info):  # strip nothing secret: FRED responses don't echo the key
        pass
    (RAW / f"FRED_{sid}_observations_2026-11-15.json").write_text(json.dumps(obs, indent=1))
    (RAW / f"FRED_{sid}_seriesinfo_2026-11-15.json").write_text(json.dumps(info, indent=1))
    print(sid, obs["observations"][-1], info["seriess"][0]["last_updated"])
payload = json.dumps({"seriesid": ["JTS000000000000000JOL", "LNS13000000", "LNS14000000"],
                      "startyear": "2018", "endyear": "2026", "registrationkey": keys["BLS_API_KEY"]}).encode()
b = json.loads(get("https://api.bls.gov/publicAPI/v2/timeseries/data/", payload, {"Content-type": "application/json"}))
(RAW / "BLS_API_JOL_LNS13000000_LNS14000000_2018_2026_2026-11-15.json").write_text(json.dumps(b, indent=1))
print(b.get("status"), b.get("message"))
for s in b["Results"]["series"]:
    print(s["seriesID"], s["data"][0])
