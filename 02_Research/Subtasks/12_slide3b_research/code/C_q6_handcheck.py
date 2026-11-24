"""C_q6_handcheck: independent recomputation of one non-trivial cell, post-pandemic x P2 ($110 flat), SPF 2026Q3.
Does NOT import the forecast_3b pipeline (or its parsers/config). Reads raw files directly:
  pipeline raw/2026-11-15/: medianLevel.xlsx (SPF), PCEPILFE_observations.json (FRED), EIA_RBRTEd.xls, aug26_base.xlsx
  outputs/B_q4_response.csv (Agent B's Fig. 2 table; not the pipeline's config copy)
then compares with processed/scenario_grid_2026Q3.csv.
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/C_q6_handcheck.py
"""
import csv
import json
import math
from datetime import date, timedelta
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(".")
RAW = ROOT / "03_Data/pipelines/forecast_3b/raw/2026-11-15"
OUT = ROOT / "02_Research/Subtasks/12_slide3b_research/outputs"

# 1. SPF 2026Q3 medians (sheet COREPCE, row YEAR=2026 QUARTER=3)
ws = openpyxl.load_workbook(RAW / "medianLevel.xlsx", read_only=True, data_only=True)["COREPCE"]
hdr, spf = None, None
for row in ws.iter_rows(values_only=True):
    if hdr is None:
        hdr = list(row); continue
    if row[0] == 2026 and row[1] == 3:
        spf = dict(zip(hdr, row))
q26_4, q27_1, q27_2, q27_3, a27 = (float(spf[k]) for k in ("COREPCE3", "COREPCE4", "COREPCE5", "COREPCE6", "COREPCEB"))
q27_4 = 100 * ((1 + a27 / 100) ** 4 / ((1 + q27_1 / 100) * (1 + q27_2 / 100) * (1 + q27_3 / 100)) - 1)

# 2. Assumed Brent: Aug-2026 STEO BREPUUS (sheet 2tab), quarterly mean of months
ws = openpyxl.load_workbook(RAW / "aug26_base.xlsx", read_only=True, data_only=True)["2tab"]
rows = list(ws.iter_rows(values_only=True))
yrs, mos = list(rows[2]), list(rows[3])
br = [r for r in rows if r[0] == "BREPUUS"][0]
cur, monthly = None, {}
for j in range(2, len(br)):
    cur = yrs[j] if yrs[j] is not None else cur
    if br[j] is not None and mos[j] is not None:
        monthly[(int(cur), mos[j])] = float(br[j])
qm = {"2026Q3": ("Jul", "Aug", "Sep"), "2026Q4": ("Oct", "Nov", "Dec"), "2027Q1": ("Jan", "Feb", "Mar"),
      "2027Q2": ("Apr", "May", "Jun"), "2027Q3": ("Jul", "Aug", "Sep"), "2027Q4": ("Oct", "Nov", "Dec")}
assumed = {q: sum(monthly[(int(q[:4]), m)] for m in ms) / 3 for q, ms in qm.items()}

# 3. Scenario Brent, P2 $110 flat: 2026Q3 actual mean; 2026Q4 = observed days + remaining weekdays at $110
d = pd.read_excel(RAW / "EIA_RBRTEd.xls", sheet_name="Data 1", skiprows=2)
d.columns = ["date", "p"]
d = d.dropna()
d["date"] = pd.to_datetime(d["date"])
q3 = d[(d.date >= "2026-07-01") & (d.date <= "2026-09-30")].p
q4obs = d[(d.date >= "2026-10-01")].p
last = d.date.max().date()
rem, t = 0, last + timedelta(days=1)
while t <= date(2026, 12, 31):
    if t.weekday() < 5 and t not in (date(2026, 11, 26), date(2026, 12, 25)):
        rem += 1
    t += timedelta(days=1)
scen = {"2026Q3": q3.mean(), "2026Q4": (q4obs.sum() + 110 * rem) / (len(q4obs) + rem)}
scen.update({q: 110.0 for q in ("2027Q1", "2027Q2", "2027Q3", "2027Q4")})
Q = list(qm)
g = [100 * math.log(scen[q] / assumed[q]) for q in Q]

# 4. Response (post) from B's CSV, provenance=table
R = {}
with open(OUT / "B_q4_response.csv") as f:
    for r in csv.DictReader(f):
        if r["regime"] == "post" and r["provenance"] == "table":
            R[int(r["k"])] = float(r["level_response_pct_per_10pct"])
L = []
for t in range(len(Q)):
    tot = 0.0
    for s in range(t + 1):
        step = g[s] - (g[s - 1] if s else 0.0)
        tot += R[t - s] * step / 10
    L.append(tot)
Ld = dict(zip(Q, L))

# 5. Apply to forecast quarters (2026Q3 is actual -> not adjusted)
base = {"2026Q4": q26_4, "2027Q1": q27_1, "2027Q2": q27_2, "2027Q3": q27_3, "2027Q4": q27_4}
out = {}
for i, q in enumerate(Q[1:], start=1):
    dL = Ld[q] - Ld[Q[i - 1]]
    out[q] = 100 * ((1 + base[q] / 100) * math.exp(4 * dL / 100) - 1)
q4q4_27 = 100 * (math.prod((1 + out[q] / 100) ** 0.25 for q in ("2027Q1", "2027Q2", "2027Q3", "2027Q4")) - 1)
# 2026 Q4/Q4 from the actual index
obs = json.loads((RAW / "PCEPILFE_observations.json").read_text())["observations"]
idx = {o["date"][:7]: float(o["value"]) for o in obs}
qa = lambda y, ms: sum(idx[f"{y}-{m:02d}"] for m in ms) / 3
lvl25q4, lvl26q3 = qa(2025, (10, 11, 12)), qa(2026, (7, 8, 9))
q4q4_26 = 100 * (lvl26q3 / lvl25q4 * (1 + out["2026Q4"] / 100) ** 0.25 - 1)

# 6. Compare with the pipeline
G = pd.read_csv(ROOT / "03_Data/pipelines/forecast_3b/processed/scenario_grid_2026Q3.csv")
c = G[(G.oil_variant == "P2_110_flat") & (G.regime == "post")].set_index("quarter").scenario_qq_ann
lines = ["Hand-check: post-pandemic x P2 ($110 flat), SPF 2026Q3 baseline, Aug-2026 STEO assumption",
         f"  last Brent obs {last}; 2026Q4 splice = {len(q4obs)} observed + {rem} remaining weekdays",
         f"  gaps (log pts x100): " + ", ".join(f"{q} {x:.3f}" for q, x in zip(Q, g)),
         f"  L (core level adj, %): " + ", ".join(f"{q} {x:.4f}" for q, x in zip(Q, L)),
         f"{'item':16s} {'handcheck':>10s} {'pipeline':>10s} {'diff':>10s}"]
ok = True
for name, mine, theirs in [("2026Q4 q/q ann", out["2026Q4"], c["2026Q4"]), ("2027Q1 q/q ann", out["2027Q1"], c["2027Q1"]),
                           ("2027Q4 q/q ann", out["2027Q4"], c["2027Q4"]), ("2026 Q4/Q4", q4q4_26, c["2026Q4/2025Q4"]),
                           ("2027 Q4/Q4", q4q4_27, c["2027Q4/2026Q4"])]:
    diff = mine - theirs
    ok &= abs(diff) < 1e-5
    lines.append(f"{name:16s} {mine:10.6f} {theirs:10.6f} {diff:10.2e}")
lines.append("MATCH (|diff| < 1e-5 pp; pipeline CSV stores 6 decimals)" if ok else "MISMATCH")
print("\n".join(lines))
(OUT / "C_q6_handcheck_output.txt").write_text("\n".join(lines) + "\n")
assert ok
