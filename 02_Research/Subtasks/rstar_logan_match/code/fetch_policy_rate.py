"""Fetch fed funds and market expectations series from FRED; save raw JSON (key stripped) to 03_Data/Raw/.
Run from project root: python3 -I 02_Research/Subtasks/rstar_logan_match/code/fetch_policy_rate.py"""
import json, os, urllib.request, urllib.parse, datetime
key = [l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser(".env")) if "FRED_API_KEY" in l][0]
today = datetime.date.today().isoformat()
for sid, start in [("EFFR","2026-09-01"),("DFEDTARU","2026-09-01"),("DFEDTARL","2026-09-01"),("EXPINF1YR","2025-01-01"),("EXPINF2YR","2025-01-01"),("T5YIE","2026-09-01")]:
    q = urllib.parse.urlencode({"series_id":sid,"api_key":key,"file_type":"json","observation_start":start})
    d = json.load(urllib.request.urlopen(f"https://api.stlouisfed.org/fred/series/observations?{q}", timeout=30))
    d.pop("api_key", None)
    json.dump(d, open(f"03_Data/Raw/fred_{sid}_{today}.json","w"))
    obs = [o for o in d["observations"] if o["value"] != "."]
    print(sid, [(o["date"], o["value"]) for o in obs[-3:]])
