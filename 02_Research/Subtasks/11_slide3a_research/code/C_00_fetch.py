"""Agent C fetch: download publisher/FRED files to a NEW raw folder (never edits existing raw).
Run from project root:  python3 -I 02_Research/Subtasks/11_slide3a_research/code/C_00_fetch.py
Keys are read from .env and redacted from every saved file.
"""
import json, os, re, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "03_Data/Raw/S3A_expectations_underlying_2026-11-15"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (UMD College Fed Challenge research; S3A fetch)"
keys = {}
for line in open(Path(".env")):
    m = re.match(r"\s*(?:export\s+)?(\w+)=(.*)", line)
    if m:
        keys[m.group(1)] = m.group(2).strip().strip("'\"")
FRED = keys["FRED_API_KEY"]
LOG = []

def get(url, name, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=90).read()
            break
        except Exception as e:
            err = str(e); time.sleep(2)
    else:
        LOG.append((name, url, "FAILED " + err)); print("FAIL", name, err); return None
    data = data.replace(FRED.encode(), b"REDACTED")
    (OUT / name).write_bytes(data)
    LOG.append((name, re.sub(FRED, "REDACTED", url), f"ok {len(data)} bytes"))
    return data

def fred(sid, extra=None, tag=""):
    p = {"series_id": sid, "api_key": FRED, "file_type": "json"}
    if extra: p.update(extra)
    get("https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(p), f"FRED_{sid}{tag}_2026-11-15.json")

for s in ["T5YIE", "T10YIE", "T5YIFR", "GASREGW", "DFEDTARU", "DFEDTARL", "PCEPI", "PCEPILFE", "CPIAUCSL", "CPILFESL",
          "MICH", "PCETRIM1M158SFRBDAL", "PCETRIM6M680SFRBDAL", "PCETRIM12M159SFRBDAL",
          "MEDCPIM158SFRBCLE", "MEDCPIM157SFRBCLE", "TRMMEANCPIM158SFRBCLE", "TRMMEANCPIM159SFRBCLE", "MEDCPIM159SFRBCLE"]:
    fred(s)
# first-release (ALFRED output_type=4) for PCE and CPI
for s in ["PCEPI", "PCEPILFE"]:
    fred(s, {"realtime_start": "1776-07-04", "realtime_end": "9999-12-31", "output_type": 4, "observation_start": "2018-01-01"}, "_firstrelease")
for s in ["MICH"]:
    fred(s, {"realtime_start": "1776-07-04", "realtime_end": "9999-12-31", "output_type": 4, "observation_start": "2025-01-01"}, "_firstrelease")
# release dates
for s in ["PCEPI", "CPIAUCSL", "GASREGW"]:
    get("https://api.stlouisfed.org/fred/series/release/dates?" + urllib.parse.urlencode(
        {"series_id": s, "api_key": FRED, "file_type": "json"}), f"FRED_releasedates_{s}_2026-11-15.json") if False else None
for rid, nm in [(53, "GDP_PCE_PIO"), (10, "CPI"), (9, "Empl")]:
    pass
# publisher files
get("https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/mct/mct-chart-data.csv", "NYFed_MCT_chart_data_2026-11-15.csv")
get("https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/mct/mct-chart-meta-content.json", "NYFed_MCT_meta_content_2026-11-15.json")
get("https://www.newyorkfed.org/research/policy/mct", "NYFed_MCT_page_2026-11-15.html")
get("https://www.clevelandfed.org/-/media/files/webcharts/medianpce/median-pce-full-history.csv", "ClevelandFed_median_PCE_full_history_2026-11-15.csv")
get("https://www.clevelandfed.org/-/media/files/webcharts/medianpce/current-components.csv", "ClevelandFed_median_PCE_current_components_2026-11-15.csv")
get("https://www.clevelandfed.org/indicators-and-data/median-pce-inflation", "ClevelandFed_median_PCE_page_2026-11-15.html")
for f in ["mcpi_revised", "trim_revised", "core", "cpi"]:
    get(f"https://www.clevelandfed.org/-/media/files/webcharts/mediancpi/{f}.csv", f"ClevelandFed_mediancpi_{f}_2026-11-15.csv")
get("https://www.clevelandfed.org/indicators-and-data/median-cpi", "ClevelandFed_median_CPI_page_2026-11-15.html")
get("https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-data.xlsx", "NYFed_SCE_chart_data_2026-11-15.xlsx")
get("https://www.newyorkfed.org/microeconomics/sce", "NYFed_SCE_page_2026-11-15.html")
get("https://www.federalreserve.gov/monetarypolicy/openmarket.htm", "FRB_openmarket_2026-11-15.htm")
get("https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm", "FRB_fomccalendars_2026-11-15.htm")
get("https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026", "PhillyFed_SPF_Q4_2026_probe_2026-11-15.html")
get("https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters", "PhillyFed_SPF_landing_2026-11-15.html")
get("https://www.dallasfed.org/research/pce", "Dallas_trimmed_mean_page_2026-11-15.html")  # added after first run; page confirms 12m 2.3, 6m 2.4, 1m ann 2.8, BEA headline 3.6, core 3.1
with open(OUT / "fetch_log.csv", "w") as f:
    f.write("file,url,status\n")
    for n, u, s in LOG: f.write(f'"{n}","{u}","{s}"\n')
print(len(LOG), "logged;", sum(1 for x in LOG if x[2].startswith("FAIL")), "failed")
