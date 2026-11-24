"""R_cleveland_refresh.py: re-pull the Cleveland Fed inflation nowcast and list every daily October 2026 value
(month-over-month and year-over-year) so the "PCE Oct 2026 estimate" comparison row can be checked against the
latest vintage before the Nov 18 cutoff.

Run from project root:
    python3 -I 02_Research/Subtasks/04_oct_pce_build/code/R_cleveland_refresh.py [YYYY-MM-DD]
The optional date (default: today) names the raw files. If raw files for that date already exist they are reused,
not re-downloaded. Raw JSONs go to 03_Data/Raw/ClevelandFed_nowcast_{month,year}_<date>.json (never edited).
Output: outputs/R_cleveland_oct2026_<date>.csv (one row per nowcast date for target month 2026-10).
"""
import csv, json, sys, urllib.request
from datetime import date
from pathlib import Path

DATE = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
RAW = Path("03_Data/Raw")
OUT = Path("02_Research/Subtasks/04_oct_pce_build/outputs")
BASE = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/"
UA = "Mozilla/5.0 (UMD College Fed Challenge research; inflation_data retrieval)"  # same generic UA as C_fetch_cleveland_bls.py
TARGET = "2026-10"
SER = {"CPI Inflation": "cpi", "Core CPI Inflation": "core_cpi", "PCE Inflation": "pce", "Core PCE Inflation": "core_pce"}


def fetch(kind):
    p = RAW / f"ClevelandFed_nowcast_{kind}_{DATE}.json"
    if not p.exists():
        req = urllib.request.Request(BASE + f"nowcast_{kind}.json", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            p.write_bytes(r.read())
        print("saved", p)
    else:
        print("reusing", p)
    return json.load(open(p))


def october(data):
    """Return (chart_updated_comment, {(mm, dd): {series: value}}) for the 2026-10 target entry."""
    for e in data:
        y, m = e["chart"]["subcaption"].split("-")
        if f"{int(y):04d}-{int(m):02d}" != TARGET:
            continue
        rows = {}
        for ds in e["dataset"]:
            key = SER.get(ds["seriesname"])
            if key is None:
                continue
            for v in ds["data"]:
                mm, dd = v["tooltext"].split("{br}")[1].split("/")
                if v["value"] != "":
                    rows.setdefault((int(mm), int(dd)), {})[key] = float(v["value"])
        return e["chart"].get("_comment", ""), rows
    raise SystemExit(f"target {TARGET} not found")


upd_m, mm = october(fetch("month"))
upd_y, yy = october(fetch("year"))
print("chart updated (month):", upd_m[:40], "| (year):", upd_y[:40])
# Nowcast dates for an October target run from early October into late November; all fall in 2026.
keys = sorted(set(mm) | set(yy))
OUT.mkdir(exist_ok=True)
fn = OUT / f"R_cleveland_oct2026_{DATE}.csv"
with open(fn, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["nowcast_date", "core_pce_mm", "pce_mm", "core_cpi_mm", "cpi_mm", "core_pce_yy", "pce_yy"])
    for k in keys:
        a, b = mm.get(k, {}), yy.get(k, {})
        w.writerow([f"2026-{k[0]:02d}-{k[1]:02d}", a.get("core_pce", ""), a.get("pce", ""), a.get("core_cpi", ""),
                    a.get("cpi", ""), b.get("core_pce", ""), b.get("pce", "")])
print("wrote", fn)
for k in keys[-8:]:
    print(f"2026-{k[0]:02d}-{k[1]:02d}", mm.get(k, {}), {s: yy.get(k, {}).get(s) for s in ("core_pce", "pce")})
