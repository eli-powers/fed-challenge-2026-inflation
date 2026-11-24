"""C_crosscheck_cleveland.py: compare Cleveland nowcast table (release dates, 'actual' m/m) with ALFRED first prints; list largest nowcast errors.
Run: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_crosscheck_cleveland.py"""
import csv
O = "02_Research/Subtasks/04_oct_pce_build/outputs/"
cl = {r["target_month"]: r for r in csv.DictReader(open(O+"cleveland_nowcast_history.csv"))}
pce = {(r["measure"], r["ref_month"]): r for r in csv.DictReader(open(O+"pce_first_prints.csv"))}
cpi = {r["ref_month"]: r for r in csv.DictReader(open(O+"core_cpi_first_prints.csv"))}
nd = dn = 0; bad = []
for t, r in cl.items():
    if r["pce_release_date"] and t <= "2026-09":
        p = pce[("core", t)]; h = pce[("headline", t)]
        if r["pce_release_date"] != p["first_release_vintage"]: dn += 1; bad.append(("pce date", t, r["pce_release_date"], p["first_release_vintage"]))
        if abs(float(r["actual_core_pce_mm_cleveland"]) - float(p["mm_first_print_pct"])) > 0.0006: nd += 1; bad.append(("core pce val", t, r["actual_core_pce_mm_cleveland"], p["mm_first_print_pct"]))
        if abs(float(r["actual_pce_mm_cleveland"]) - float(h["mm_first_print_pct"])) > 0.0006: nd += 1; bad.append(("pce val", t, r["actual_pce_mm_cleveland"], h["mm_first_print_pct"]))
    c = cpi.get(t)
    if r["cpi_release_date"] and c and c["first_release_vintage"] and r["cpi_release_date"] != c["first_release_vintage"]: bad.append(("cpi date", t, r["cpi_release_date"], c["first_release_vintage"]))
    if r["actual_core_cpi_mm_cleveland"] and c and c["mm_first_print_pct"] and abs(float(r["actual_core_cpi_mm_cleveland"]) - float(c["mm_first_print_pct"])) > 0.0006:
        bad.append(("core cpi val", t, r["actual_core_cpi_mm_cleveland"], c["mm_first_print_pct"]))
print("mismatches:", len(bad))
for b in bad: print(b)
errs = sorted([(float(r["core_pce_err_nowcast_minus_actual"]), t) for t, r in cl.items() if r["core_pce_err_nowcast_minus_actual"]])
import statistics as st
e = [x[0] for x in errs]
print("core PCE pre-release nowcast error: n", len(e), "mean", round(st.mean(e), 4), "MAE", round(st.mean(abs(x) for x in e), 4), "min", errs[0], "max", errs[-1])
e2 = sorted([(float(r["pce_err_nowcast_minus_actual"]), t) for t, r in cl.items() if r["pce_err_nowcast_minus_actual"]])
x2 = [x[0] for x in e2]
print("PCE pre-release error: n", len(x2), "mean", round(st.mean(x2), 4), "MAE", round(st.mean(abs(x) for x in x2), 4), "min", e2[0], "max", e2[-1])
print("largest |core err|:", sorted(errs, key=lambda x: -abs(x[0]))[:6])
print("largest |pce err|:", sorted(e2, key=lambda x: -abs(x[0]))[:6])
# day-after-CPI error for core pce
da = [(float(r["core_pce_nowcast_day_after_cpi"]) - float(r["actual_core_pce_mm_cleveland"]), t) for t, r in cl.items() if r["core_pce_nowcast_day_after_cpi"] and r["actual_core_pce_mm_cleveland"]]
print("core PCE day-after-CPI err: n", len(da), "MAE", round(st.mean(abs(x[0]) for x in da), 4))
