"""C_fetch_alfred.py: download all ALFRED vintages (output_type=1: value per obs per realtime interval).
Run from project root: python3 02_Research/Subtasks/04_oct_pce_build/code/C_fetch_alfred.py
Key is read from .env and never written (response bodies don't contain it)."""
import json, re, urllib.request, urllib.parse
from pathlib import Path
DATE = "2026-11-11"
RAW = Path("03_Data/Raw")
def key():
    for l in open(Path(".env")):
        m = re.match(r"\s*(?:export\s+)?FRED_API_KEY=(.*)", l)
        if m: return m.group(1).strip().strip("'\"")
    raise SystemExit("no key")
K = key()
JOBS = {"PCEPILFE": "2023-01-01", "PCEPI": "2023-01-01", "CPILFESL": "2017-01-01"}
for sid, start in JOBS.items():
    p = {"series_id": sid, "api_key": K, "file_type": "json", "realtime_start": "1776-07-04",
         "realtime_end": "9999-12-31", "observation_start": start, "output_type": 1, "limit": 100000}
    url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(p)
    body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=120).read().decode()
    assert K not in body
    out = RAW / f"ALFRED_{sid}_all_vintages_{DATE}.json"
    out.write_text(body)
    d = json.loads(body)
    print(sid, d.get("count"), len(d["observations"]), out)
    # series metadata
    p2 = {"series_id": sid, "api_key": K, "file_type": "json"}
    u2 = "https://api.stlouisfed.org/fred/series?" + urllib.parse.urlencode(p2)
    b2 = urllib.request.urlopen(urllib.request.Request(u2, headers={"User-Agent": "research-script"}), timeout=60).read().decode()
    (RAW / f"FRED_{sid}_seriesinfo_{DATE}.json").write_text(b2)
    # vintage dates
    p3 = {"series_id": sid, "api_key": K, "file_type": "json", "realtime_start": "1776-07-04", "realtime_end": "9999-12-31", "limit": 10000}
    u3 = "https://api.stlouisfed.org/fred/series/vintagedates?" + urllib.parse.urlencode(p3)
    b3 = urllib.request.urlopen(urllib.request.Request(u3, headers={"User-Agent": "research-script"}), timeout=60).read().decode()
    (RAW / f"ALFRED_{sid}_vintagedates_{DATE}.json").write_text(b3)
