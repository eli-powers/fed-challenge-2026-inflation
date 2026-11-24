"""C_pce_first_prints.py: first-print m/m and y/y for PCEPILFE (core) and PCEPI (headline) from ALFRED vintages,
plus cross-check vs BEA pipeline JSON. Run from project root: python3 02_Research/Subtasks/04_oct_pce_build/code/C_pce_first_prints.py"""
import csv, json, sys
from decimal import Decimal, ROUND_HALF_UP
sys.path.insert(0, "02_Research/Subtasks/04_oct_pce_build/code")
from C_alfred_lib import *
RAW = "03_Data/Raw/ALFRED_{}_all_vintages_2026-11-11.json"
OUT = "02_Research/Subtasks/04_oct_pce_build/outputs/"
months = []
m = "2024-01"
while m <= "2026-09": months.append(m); m = add_months(m, 1)
def r1(x): return float(Decimal(repr(x)).quantize(Decimal("0.1"), ROUND_HALF_UP))
data = {s: load(RAW.format(s)) for s in ("PCEPILFE", "PCEPI")}
rows = []
for sid, name in (("PCEPILFE", "core"), ("PCEPI", "headline")):
    obs = data[sid]
    fr_all = {mm: first_release(obs, mm) for mm in obs}
    for mm in months:
        v = fr_all[mm]
        L, Lp, Ly = (level_asof(obs, x, v) for x in (mm, add_months(mm, -1), add_months(mm, -12)))
        mm_fp = (L/Lp - 1)*100
        cur = level_asof(obs, mm, CURRENT); curp = level_asof(obs, add_months(mm, -1), CURRENT)
        mm_cur = (cur/curp - 1)*100
        yy = (L/Ly - 1)*100
        # delay/combination flags
        flags = []
        nxt = fr_all.get(add_months(mm, 1)); prv = fr_all.get(add_months(mm, -1))
        if nxt == v: flags.append("combined release with next month (%s)" % add_months(mm, 1))
        if prv == v: flags.append("combined release with prior month (%s)" % add_months(mm, -1))
        # lag from month-end to release
        import calendar
        y, mo = int(mm[:4]), int(mm[5:]); me = date(y, mo, calendar.monthrange(y, mo)[1])
        lag = (v - me).days
        if lag > 35: flags.append(f"late release (lag {lag}d from month-end; typical ~26-31d; schedule disrupted by fall-2025 shutdown and catch-up)")
        rows.append(dict(series_id=sid, measure=name, ref_month=mm, first_release_vintage=v.isoformat(),
            level_first_print=L, level_prior_month_same_vintage=Lp, level_year_ago_same_vintage=Ly,
            mm_first_print_pct=f"{mm_fp:.4f}", mm_first_print_1dp=f"{r1(mm_fp):.1f}",
            mm_current_vintage_pct=f"{mm_cur:.4f}", revision_cur_minus_first_pp=f"{mm_cur-mm_fp:+.4f}",
            yy_first_print_pct=f"{yy:.4f}", lag_days_from_month_end=lag, flag="; ".join(flags)))
cols = list(rows[0].keys())
with open(OUT+"pce_first_prints.csv", "w", newline="") as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)
meta = [
 ("series_ids", "PCEPILFE = PCE price index excl. food and energy (core); PCEPI = PCE price index (headline); FRED/ALFRED series of BEA NIPA Table 2.8.7/2.4.4 chain-type price index, 2017=100"),
 ("seasonal_adjustment", "Seasonally adjusted (BEA monthly index)"),
 ("units", "Index level 2017=100; mm/yy columns are percent change, computed as (L_t/L_t-1 - 1)*100 using levels at 3 decimals"),
 ("ref_period", "ref_month 2024-01 .. 2026-09 (monthly, m/m horizon one month; yy = 12-month)"),
 ("first_release_vintage", "Earliest ALFRED realtime_start with a value for that month (ALFRED vintage date; treated as BEA release date; verify against BEA schedule)"),
 ("first_print_calc", "m/m and y/y use ALL levels as they stood in that single first-release vintage (so prior month may already be revised)"),
 ("mm_current_vintage", "Both levels as of the latest vintage (2026-10-29 vintage for Aug-Sep 2026; 2026-09-30 annual update for earlier months). Pulled 2026-11-11"),
 ("1dp_figure", "First-print m/m rounded half-up to 0.1 from our 3-decimal-level calc; BEA's own published rounded figure uses unrounded indexes and can differ by 0.1 occasionally"),
 ("raw_files", "03_Data/Raw/ALFRED_PCEPILFE_all_vintages_2026-11-11.json; 03_Data/Raw/ALFRED_PCEPI_all_vintages_2026-11-11.json; vintage dates: ALFRED_*_vintagedates_2026-11-11.json"),
 ("script", "02_Research/Subtasks/04_oct_pce_build/code/C_pce_first_prints.py (+C_alfred_lib.py)"),
]
with open(OUT+"pce_first_prints_meta.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["field", "description"]); w.writerows(meta)

# ---- cross-check vs BEA pipeline JSON (current vintage) ----
bea = json.load(open("03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json"))["BEAAPI"]["Results"]
if isinstance(bea, list): bea = bea[0]
B = {}
for r in bea["Data"]:
    if r["SeriesCode"] in ("DPCERG", "DPCCRG"):
        B[(r["SeriesCode"], r["TimePeriod"])] = float(r["DataValue"].replace(",", ""))
chk = []; mism = 0
for sid, code in (("PCEPILFE", "DPCCRG"), ("PCEPI", "DPCERG")):
    for mm in sorted(data[sid]):
        a = level_asof(data[sid], mm, CURRENT); b = B.get((code, mm.replace("-", "M")))
        if a is None and b is None: continue
        ok = (a is not None and b is not None and abs(a-b) < 0.0006)
        if not ok: mism += 1
        chk.append((sid, code, mm, a, b, "OK" if ok else "MISMATCH"))
with open(OUT+"C_crosscheck_alfred_vs_bea.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["alfred_series","bea_series","month","alfred_current","bea_pipeline","status"]); w.writerows(chk)
print("crosscheck rows", len(chk), "mismatches", mism)
for t in chk:
    if t[5] != "OK": print(t)
for k in (("DPCCRG","2026M09"),("DPCERG","2026M09"),("DPCCRG","2025M10")): print(k, B.get(k))
# table print
for r in rows:
    if r["measure"]=="core": print(r["ref_month"], r["first_release_vintage"], r["mm_first_print_pct"], r["mm_first_print_1dp"], r["mm_current_vintage_pct"], r["yy_first_print_pct"], r["flag"])
