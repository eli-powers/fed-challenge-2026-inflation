"""Agent C fetch (Q8): FOMC statements Mar 2020-Oct 2026 + CPI NSA from FRED. Run from project root with python3 -I."""
import re, time, urllib.request, urllib.parse
from pathlib import Path
ROOT = Path.cwd()
OUT = ROOT / "03_Data/Raw/S3A_fomc_statements_2026-11-15"; OUT.mkdir(parents=True, exist_ok=True)
RAW1 = ROOT / "03_Data/Raw/S3A_expectations_underlying_2026-11-15"
UA = "Mozilla/5.0 (UMD College Fed Challenge research; S3A fetch)"
keys = {}
for line in open(Path(".env")):
    m = re.match(r"\s*(?:export\s+)?(\w+)=(.*)", line)
    if m: keys[m.group(1)] = m.group(2).strip().strip("'\"")
FRED = keys["FRED_API_KEY"]
def get(url, dest):
    for a in range(3):
        try:
            d = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90).read(); break
        except Exception as e:
            err = str(e); time.sleep(2)
    else:
        return "FAILED " + err
    dest.write_bytes(d.replace(FRED.encode(), b"REDACTED")); return f"ok {len(d)}"
log = []
for sid in ["CPIAUCNS", "CPILFENS"]:
    u = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode({"series_id": sid, "api_key": FRED, "file_type": "json"})
    log.append((f"FRED_{sid}_2026-11-15.json", re.sub(FRED, "REDACTED", u), get(u, RAW1 / f"FRED_{sid}_2026-11-15.json")))
for sid in ["PCEPI", "PCEPILFE"]:
    for rt in ["2021-05-01", "2021-06-01", "2026-09-29"]:   # vintages after the Mar 2021 / Apr 2021 releases; and just before the 2026-09-30 annual update
        u = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode({"series_id": sid, "api_key": FRED, "file_type": "json", "realtime_start": rt, "realtime_end": rt, "observation_start": "2019-01-01"})
        log.append((f"ALFRED_{sid}_asof_{rt}.json", re.sub(FRED, "REDACTED", u), get(u, RAW1 / f"ALFRED_{sid}_asof_{rt}.json")))
cal = (RAW1 / "FRB_fomccalendars_2026-11-15.htm").read_text(errors="ignore")
dates = set(re.findall(r"monetary(\d{8})a\.htm", cal))
dates |= {"20200303", "20200315", "20200323", "20200429", "20200610", "20200729", "20200916", "20201105", "20201216"}
for d in sorted(dates):
    if d < "20200301": continue
    u = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{d}a.htm"
    log.append((f"FOMC_statement_{d}.htm", u, get(u, OUT / f"FOMC_statement_{d}.htm"))); time.sleep(0.3)
with open(OUT / "fetch_log.csv", "w") as f:
    f.write("file,url,status\n")
    for n, u, s in log: f.write(f'"{n}","{u}","{s}"\n')
print(sum(1 for x in log if x[2].startswith("FAIL")), "failed of", len(log))
for x in log:
    if x[2].startswith("FAIL"): print(x)
