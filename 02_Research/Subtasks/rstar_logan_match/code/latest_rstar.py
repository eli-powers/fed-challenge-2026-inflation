"""Latest published U.S. real r* by model, from raw files in 03_Data/Raw/rstar_2026-11-16/.
Purpose: reconstruct the 'eight published models' behind Logan's Nov 10, 2026 range (1 to 1.85%).
Run: python3 -I latest_rstar.py <raw_dir>"""
import sys, csv, openpyxl
d = sys.argv[1]
def rows(f, sheet):
    ws = openpyxl.load_workbook(f"{d}/{f}", read_only=True, data_only=True)[sheet]
    return [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]
out = []
r = rows("Holston_Laubach_Williams_current_estimates.xlsx", "HLW Estimates"); out.append(("HLW (2023), NY Fed, one-sided", r[-1][0].date(), r[-1][10]))
r = rows("Laubach_Williams_current_estimates.xlsx", "data"); out.append(("Laubach-Williams (2003), NY Fed, one-sided", r[-1][0].date(), r[-1][2]))
r = rows("lubik_matthes_natural_rate_interest.xlsx", "LM_RealRate"); out.append(("Lubik-Matthes, Richmond Fed, median", r[-1][0].date(), r[-1][2]))
r = rows("zaman_stars_2026Q3.xlsx", "Stars_Smoothed")
hdr = r[0]; c = [i for i, v in enumerate(hdr) if isinstance(v, str) and v.lower().startswith("rstar")][0]
for row in r[-2:]: out.append((f"Zaman (Cleveland Fed), mean", row[c], row[c + 3]))
r = rows("el2026-22-figure-data.xlsx", "Figure 1"); row = [x for x in r if x[0] == "2026q3"][0]; out.append(("Curdia medium-run, SF Fed EL 2026-22 (Fig. 1)", "2026q3 (projected)", float(row[1])))
kc = list(csv.reader(open(f"{d}/kc_rstar.csv"))); out.append(("Glover-Oliyide, KC Fed", kc[-1][0], float(kc[-1][1])))
fr = list(csv.DictReader(open(f"{d}/ferreira_rstar_values_feds_note.csv"))); out.append(("Ferreira-Lott-Richards, Fed Board (US col)", fr[-1]["date_h"], float(fr[-1]["US"])))
for name, date, v in out: print(f"{name:48s} {str(date):14s} {v:.3f}")
