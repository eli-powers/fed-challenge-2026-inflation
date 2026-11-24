"""C2_compute_first_release_revisions.py: reads saved ALFRED raw JSON (03_Data/Raw/ALFRED_*_all_vintages_from2024-11_2026-11-11.json) and
outputs/C2_alfred_id_resolution.csv. Writes outputs/ppi_first_release.csv(+_meta), outputs/C2_cpi_sa_revisions_by_month.csv,
outputs/C2_cpi_sa_revisions_summary.csv(+_meta). Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C2_compute_first_release_revisions.py
First release = earliest ALFRED realtime_start at which the reference month has a non-missing value. 'Prior month in same vintage' = level of
month-1 as it stood on that same vintage date. m/m % = 100*(level/prior-1). Current = vintage of 2026-11-11 (realtime_end 9999-12-31)."""
import json, csv
from datetime import date
from pathlib import Path
RAW = Path("03_Data/Raw"); OUT = Path("02_Research/Subtasks/04_oct_pce_build/outputs"); DATE = "2026-11-11"
def load(fid):
    obs = {}
    for r in json.load(open(RAW/f"ALFRED_{fid}_all_vintages_from2024-11_{DATE}.json"))["observations"]:
        v = None if r["value"] == "." else float(r["value"])
        obs.setdefault(r["date"][:7], []).append((date.fromisoformat(r["realtime_start"]), date.fromisoformat(r["realtime_end"]), v))
    return obs
def asof(obs, m, vd):
    for rs, re_, v in obs.get(m, []):
        if rs <= vd <= re_: return v
def first(obs, m):
    c = [rs for rs, re_, v in obs.get(m, []) if v is not None]
    return min(c) if c else None
def prev(m): y, mo = int(m[:4]), int(m[5:]); t = y*12+mo-2; return f"{t//12}-{t%12+1:02d}"
def months(a, b):
    y, mo = int(a[:4]), int(a[5:]); out = []
    while f"{y}-{mo:02d}" <= b:
        out.append(f"{y}-{mo:02d}"); mo += 1
        if mo == 13: y += 1; mo = 1
    return out
CUR = date(9999, 12, 31)
res = list(csv.DictReader(open(OUT/"C2_alfred_id_resolution.csv")))
# ---- PPI first release
rows = []
for r in res:
    if not r["bls_series_id"].startswith(("PCU", "WPU")) or r["status"] != "OK": continue
    obs = load(r["fred_series_id"]); fid = r["fred_series_id"]
    for m in months("2024-12", "2026-12"):
        fv = first(obs, m)
        if fv is None: continue
        lv = asof(obs, m, fv); pv = asof(obs, prev(m), fv)
        cl = asof(obs, m, CUR); cp = asof(obs, prev(m), CUR)
        mm1 = round(100*(lv/pv-1), 4) if lv and pv else ""
        mmc = round(100*(cl/cp-1), 4) if cl and cp else ""
        rows.append([r["bls_series_id"], fid, m, fv.isoformat(), lv, pv if pv is not None else "", mm1, cl if cl is not None else "", cp if cp is not None else "", mmc,
                     round(mmc-mm1, 4) if mm1 != "" and mmc != "" else "", "NSA", f"ALFRED_{fid}_all_vintages_from2024-11_{DATE}.json"])
hdr = ["bls_series_id", "fred_series_id", "reference_month", "first_release_vintage_date", "first_release_level", "prior_month_level_same_vintage",
       "first_print_mm_pct", "current_level_2026-11-11", "current_prior_month_level", "current_mm_pct", "mm_revision_pp", "seasonal", "raw_file"]
with open(OUT/"ppi_first_release.csv", "w", newline="") as fh: w = csv.writer(fh); w.writerow(hdr); w.writerows(rows)
# ---- CPI SA revisions
by_month, summ = [], []
for r in res:
    if not r["bls_series_id"].startswith("CUSR") or r["status"] != "OK": continue
    obs = load(r["fred_series_id"]); sid = r["bls_series_id"]; revs = []; lvl_rev = []
    for m in months("2024-12", "2026-09"):
        fv = first(obs, m)
        if fv is None: by_month.append([sid, m, "", "", "", "", "", "", "no first-release value (e.g. 2025-10, not collected)"]); continue
        lv = asof(obs, m, fv); pv = asof(obs, prev(m), fv); cl = asof(obs, m, CUR); cp = asof(obs, prev(m), CUR)
        mm1 = 100*(lv/pv-1) if lv and pv else None; mmc = 100*(cl/cp-1) if cl and cp else None
        rev = (mmc-mm1) if mm1 is not None and mmc is not None else None
        if rev is not None: revs.append(abs(rev))
        changed = "Y" if lv != cl else "N"
        if lv is not None and cl is not None: lvl_rev.append(m) if changed == "Y" else None
        by_month.append([sid, m, fv.isoformat(), lv, cl, round(mm1, 4) if mm1 is not None else "", round(mmc, 4) if mmc is not None else "",
                         round(rev, 4) if rev is not None else "", f"level_revised={changed}"])
    summ.append([sid, r["fred_series_id"], len(revs), round(sum(revs)/len(revs), 4) if revs else "", round(max(revs), 4) if revs else "",
                 len(lvl_rev), ";".join(lvl_rev)])
with open(OUT/"C2_cpi_sa_revisions_by_month.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["series_id", "reference_month", "first_release_vintage_date", "first_release_level_SA", "current_level_SA", "first_print_mm_pct", "current_mm_pct", "mm_revision_pp", "note"]); w.writerows(by_month)
with open(OUT/"C2_cpi_sa_revisions_summary.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["series_id", "fred_series_id", "n_months_compared", "mean_abs_mm_revision_pp", "max_abs_mm_revision_pp", "n_months_level_revised", "months_level_revised"]); w.writerows(summ)
for name, n, desc in (("ppi_first_release", len(rows), "PPI (NSA) first-release vs current. Reference months Dec 2024 on. First release = earliest ALFRED realtime_start with a value. Dates are ALFRED vintage dates, which can lag BLS release day by a few days. Series not in ALFRED listed in C2_alfred_id_resolution.csv (status NOT FOUND)."),
                      ("C2_cpi_sa_revisions_summary", len(summ), "Ten largest-share CPI SA series carried by ALFRED, ref months 2024-12..2026-09; level revised = SA level differs between first release and 2026-11-11 vintage.")):
    with open(OUT/f"{name}_meta.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["field", "value"])
        for k, v in (("file", name+".csv"), ("rows", n), ("source", "ALFRED (FRED API series/observations, output_type=1, realtime 1776-07-04..9999-12-31)"), ("retrieved", DATE), ("script", "code/C2_compute_first_release_revisions.py"), ("description", desc)): w.writerow([k, v])
print(len(rows), len(by_month))
