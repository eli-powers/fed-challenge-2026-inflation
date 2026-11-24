"""C_cleveland_nowcast_history.py: parse Cleveland Fed nowcast chart JSONs (month, year) saved 2026-11-11 into a long table,
then build per-target-month table: last nowcast dated before the PCE release, nowcast on/after the CPI release.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_cleveland_nowcast_history.py"""
import json, csv, sys
from datetime import date, timedelta
sys.path.insert(0, "02_Research/Subtasks/04_oct_pce_build/code")
RAW = "03_Data/Raw/ClevelandFed_nowcast_{}_2026-11-11.json"
OUT = "02_Research/Subtasks/04_oct_pce_build/outputs/"
SER = {"CPI Inflation": "cpi", "Core CPI Inflation": "core_cpi", "PCE Inflation": "pce", "Core PCE Inflation": "core_pce",
       "Actual CPI Inflation": "act_cpi", "Actual Core CPI Inflation": "act_core_cpi", "Actual PCE Inflation": "act_pce", "Actual Core PCE Inflation": "act_core_pce"}
def parse(kind):
    data = json.load(open(RAW.format(kind)))
    out = {}   # (target 'YYYY-MM') -> dict(series -> {date: float}), plus 'updated'
    for e in data:
        y, m = e["chart"]["subcaption"].split("-"); Y, M = int(y), int(m)
        tgt = f"{Y:04d}-{M:02d}"
        dates = []
        for v in e["dataset"][0]["data"]:
            mm, dd = v["tooltext"].split("{br}")[1].split("/")
            dates.append((int(mm), int(dd)))
        # infer years: first date nearest the 15th of the target month, then roll over at month wrap
        mm0, dd0 = dates[0]
        cand = min((date(Y+k, mm0, dd0) for k in (-1, 0, 1)), key=lambda x: abs((x - date(Y, M, 15)).days))
        yr = cand.year; prev = mm0; full = []
        for mm, dd in dates:
            if mm < prev: yr += 1
            prev = mm; full.append(date(yr, mm, dd))
        rec = {"updated": e["chart"]["_comment"]}
        for ds in e["dataset"]:
            key = SER[ds["seriesname"]]; rec[key] = {}
            assert len(ds["data"]) == len(full)
            for dt, v in zip(full, ds["data"]):
                if v["value"] != "": rec[key][dt] = float(v["value"])
        rec["dates"] = full
        out[tgt] = rec
    return out
M = parse("month"); Yr = parse("year")
# long file (all targets, all dates) for auditability
with open(OUT+"C_cleveland_nowcast_long_mm.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["target_month", "nowcast_date", "series", "value_pct_mm"])
    for t, r in M.items():
        for k in SER.values():
            for dt, v in sorted(r[k].items()): w.writerow([t, dt, k, v])
rows = []
for t in sorted(M):
    if not ("2024-01" <= t <= "2026-10"): continue
    r = M[t]
    pce_rel = max(r["act_pce"]) if r["act_pce"] else None
    cpi_rel = max(r["act_cpi"]) if r["act_cpi"] else None
    ccpi_rel = max(r["act_core_cpi"]) if r["act_core_cpi"] else None
    d = dict(target_month=t, chart_updated=r["updated"][:10], pce_release_date=pce_rel or "", cpi_release_date=cpi_rel or "")
    if pce_rel:
        pre = [x for x in r["dates"] if x < pce_rel and x in r["core_pce"]]
        lp = max(pre)
        d.update(last_pre_pce_date=lp, core_pce_nowcast_mm=r["core_pce"][lp], pce_nowcast_mm=r["pce"].get(lp, ""),
                 actual_core_pce_mm_cleveland=r["act_core_pce"][pce_rel], actual_pce_mm_cleveland=r["act_pce"].get(pce_rel, ""),
                 core_pce_err_nowcast_minus_actual=r["core_pce"][lp]-r["act_core_pce"][pce_rel],
                 pce_err_nowcast_minus_actual=(r["pce"][lp]-r["act_pce"][pce_rel]) if (lp in r["pce"] and pce_rel in r["act_pce"]) else "")
    if cpi_rel:
        d["core_pce_nowcast_on_cpi_day"] = r["core_pce"].get(cpi_rel, ""); d["pce_nowcast_on_cpi_day"] = r["pce"].get(cpi_rel, "")
        after = [x for x in r["dates"] if x > cpi_rel and x in r["core_pce"]]
        if after:
            da = min(after)
            d.update(day_after_cpi_date=da, core_pce_nowcast_day_after_cpi=r["core_pce"][da], pce_nowcast_day_after_cpi=r["pce"].get(da, ""))
        pre_c = [x for x in r["dates"] if x < cpi_rel and x in r["core_pce"]]
        if pre_c:
            d["core_pce_nowcast_day_before_cpi"] = r["core_pce"][max(pre_c)]; d["pce_nowcast_day_before_cpi"] = r["pce"].get(max(pre_c), "")
    d["actual_core_cpi_mm_cleveland"] = r["act_core_cpi"].get(ccpi_rel, "") if ccpi_rel else ""
    d["actual_cpi_mm_cleveland"] = r["act_cpi"].get(cpi_rel, "") if cpi_rel else ""
    rows.append(d)
cols = ["target_month","chart_updated","cpi_release_date","pce_release_date","last_pre_pce_date","core_pce_nowcast_mm","pce_nowcast_mm",
        "actual_core_pce_mm_cleveland","actual_pce_mm_cleveland","core_pce_err_nowcast_minus_actual","pce_err_nowcast_minus_actual",
        "core_pce_nowcast_day_before_cpi","pce_nowcast_day_before_cpi","core_pce_nowcast_on_cpi_day","pce_nowcast_on_cpi_day",
        "day_after_cpi_date","core_pce_nowcast_day_after_cpi","pce_nowcast_day_after_cpi","actual_core_cpi_mm_cleveland","actual_cpi_mm_cleveland"]
def fmt(v): return f"{v:.4f}" if isinstance(v, float) else v
with open(OUT+"cleveland_nowcast_history.csv", "w", newline="") as f:
    w = csv.DictWriter(f, cols); w.writeheader()
    for d in rows: w.writerow({c: fmt(d.get(c, "")) for c in cols})
meta = [
 ("source", "Cleveland Fed Inflation Nowcasting chart data: https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json (also nowcast_year.json, nowcast_quarter.json)"),
 ("raw_files", "03_Data/Raw/ClevelandFed_nowcast_month_2026-11-11.json; ..._year_...; ..._quarter_... (downloaded 2026-11-11; file stamp _comment = 2026-11-10 00:00)"),
 ("series", "Nowcasts of CPI, core CPI, PCE (headline) and core PCE price index; units percent change m/m (month file), y/y (year file); no seasonal-adjustment label in file (Cleveland Fed methodology: SA m/m, annualized not applied in month file)"),
 ("target_month", "Month being nowcast (chart subcaption). Rows Jan 2024 .. Oct 2026"),
 ("nowcast_dates", "File gives MM/DD without a year; year inferred from target month and date order (script C_cleveland_nowcast_history.py). Business days only"),
 ("release_dates", "Inferred as the date on which Cleveland's 'Actual ...' series has a value (nowcast series is blank from that day). Cross-checked against ALFRED first-release vintages in notes_C.md"),
 ("last_pre_pce", "Last non-blank nowcast dated strictly before pce_release_date"),
 ("day_after_cpi", "First nowcast date strictly after cpi_release_date. Also given: on cpi day and day before. CPI-day PCE nowcasts appear to already incorporate that day's CPI"),
 ("errors", "err = nowcast minus Cleveland's 'actual' (their first-print m/m, from unrounded BEA/BLS indexes); percentage points"),
 ("script", "02_Research/Subtasks/04_oct_pce_build/code/C_cleveland_nowcast_history.py; long form of all values: outputs/C_cleveland_nowcast_long_mm.csv"),
]
with open(OUT+"cleveland_nowcast_history_meta.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["field", "description"]); w.writerows(meta)
# ---- current October 2026 (m/m and y/y) ----
print("== CURRENT ==")
for t in ("2026-10", "2026-11"):
    for lab, src in (("m/m", M), ("y/y", Yr)):
        r = src[t]
        for k in ("cpi", "core_cpi", "pce", "core_pce"):
            if r[k]:
                dt = max(r[k]); print(t, lab, k, dt, f"{r[k][dt]:.4f}", "chart updated", r["updated"])
        for k in ("act_cpi","act_core_cpi","act_pce","act_core_pce"):
            if r[k]: dt=max(r[k]); print(t, lab, k, dt, f"{r[k][dt]:.4f}")
# last 12 rows
for d in rows[-14:]: print({c: fmt(d.get(c, "")) for c in ("target_month","cpi_release_date","pce_release_date","last_pre_pce_date","core_pce_nowcast_mm","pce_nowcast_mm","actual_core_pce_mm_cleveland","core_pce_err_nowcast_minus_actual","day_after_cpi_date","core_pce_nowcast_day_after_cpi")})
