"""Agent D (slide 3B stress test): independent checks and threshold numbers for Q&A.

Standalone: does NOT import the pipeline. Re-implements the mapping from the pipeline README:
  g_s = 100*ln(Brent_s / Assumed_s), s = 2026Q3..2027Q4 (g before 2026Q3 = 0)
  L_t = sum_{s<=t} R_{t-s} * (g_s - g_{s-1}) / 10
  scenario q/q ann: (1+s/100) = (1+b/100)*exp(4*(L_t - L_{t-1})/100), forecast quarters only (2026Q4..2027Q4)
  2027 Q4/Q4 = prod_{2027Q1..Q4}(1+x/100)^(1/4) - 1

Inputs (read only):
  03_Data/pipelines/forecast_3b/config/regime_response.csv   (FEDS note Fig. 2 table)
  03_Data/pipelines/forecast_3b/processed/oil_paths_2026Q3.csv
  03_Data/pipelines/forecast_3b/processed/oil_assumption_2026Q3.csv
  03_Data/pipelines/forecast_3b/processed/scenario_grid_2026Q3.csv (baseline path, and pipeline values to check against)
  outputs/A_q1_spf_baseline.csv is NOT read; SPF 2027 Q4/Q4 IQR (2.25/2.727) and SEP (2.5; CT 2.3-2.6) are typed from
  report_A.md (coordinator-verified SEP; IQR from A's microdata, not coordinator-checked).

Run from anywhere:  python3 -I ".../12_slide3b_research/code/D_q7_checks.py"
Writes: outputs/D_q7_checks.csv
"""
import csv
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TASK)))
PIPE = os.path.join(ROOT, "03_Data", "pipelines", "forecast_3b")
OUT = os.path.join(TASK, "outputs", "D_q7_checks.csv")

Q = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]
REMAIN_W = 34 / 64  # remaining-weekday weight in the 2026Q4 splice (README / B_q3_path_definitions.md)


def read_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


R = {}
for r in read_csv(os.path.join(PIPE, "config", "regime_response.csv")):
    R.setdefault(r["regime"], {})[int(r["k"])] = float(r["level_response_pct_per_10pct"])

paths = {}
for r in read_csv(os.path.join(PIPE, "processed", "oil_paths_2026Q3.csv")):
    paths.setdefault(r["oil_variant"], {})[r["quarter"]] = float(r["brent_usd"])

assumed = {r["quarter"]: float(r["assumed_brent_usd"])
           for r in read_csv(os.path.join(PIPE, "processed", "oil_assumption_2026Q3.csv"))
           if r["proxy"] == "steo_matched"}

grid = read_csv(os.path.join(PIPE, "processed", "scenario_grid_2026Q3.csv"))
base = {}
pipe_q4q4 = {}
for r in grid:
    if r["is_central"] != "True":
        continue
    if r["horizon"] == "qq_ann" and r["oil_variant"] == "P1_steo_latest" and r["regime"] == "pre":
        base[r["quarter"]] = float(r["baseline_qq_ann"])
    if r["horizon"] == "q4q4" and r["quarter"].startswith("2027Q4"):
        pipe_q4q4[(r["oil_variant"], r["regime"])] = float(r["scenario_qq_ann"])


def run(brent, regime):
    g = [100 * math.log(brent[q] / assumed[q]) for q in Q]
    dg = [g[0]] + [g[i] - g[i - 1] for i in range(1, len(g))]
    L = []
    for t in range(len(Q)):
        L.append(sum(R[regime][min(t - s, 12)] * dg[s] / 10 for s in range(t + 1)))
    out = {}
    for t in range(1, len(Q)):  # 2026Q4 onward are forecast quarters
        b = base[Q[t]]
        out[Q[t]] = ((1 + b / 100) * math.exp(4 * (L[t] - L[t - 1]) / 100) - 1) * 100
    q4q4_27 = (math.prod((1 + out[q] / 100) ** 0.25 for q in Q[2:]) - 1) * 100
    return out, q4q4_27


def base_q4q4_27():
    return (math.prod((1 + base[q] / 100) ** 0.25 for q in Q[2:]) - 1) * 100


rows = []
B27 = base_q4q4_27()
rows.append(["baseline", "2027 Q4/Q4", "baseline (SPF 2026Q3 path, 2027Q4 derived)", round(B27, 4), "check vs 2.4004"])

# 1. Replicate the six central cells (2027 Q4/Q4) and compare to the pipeline
for v in ["P1_steo_latest", "P2_110_flat", "P3_feb26steo_plus25"]:
    for reg in ["pre", "post"]:
        _, y = run(paths[v], reg)
        rows.append(["replicate", "2027 Q4/Q4", f"{v} x {reg}", round(y, 4),
                     f"pipeline {pipe_q4q4[(v, reg)]:.4f}; diff {y - pipe_q4q4[(v, reg)]:+.6f}"])

# 2. Cells vs SPF 2027 Q4/Q4 IQR (A: microdata, 2.25 / 2.727) and Sep SEP 2027 median 2.5 (CT 2.3-2.6)
SPF_P25, SPF_P75, SEP_MED, SEP_CT_HI = 2.25, 2.727, 2.5, 2.6
for v in ["P1_steo_latest", "P2_110_flat", "P3_feb26steo_plus25"]:
    for reg in ["pre", "post"]:
        y = pipe_q4q4[(v, reg)]
        rows.append(["vs_SPF_IQR_SEP", "2027 Q4/Q4", f"{v} x {reg}", round(y, 4),
                     f"above SPF P75 {SPF_P75}: {y > SPF_P75}; above SEP median {SEP_MED}: {y > SEP_MED}; "
                     f"above SEP CT top {SEP_CT_HI}: {y > SEP_CT_HI}"])

# 3. Sensitivity: +$10/bbl on P1 in every 2027 quarter (2026 unchanged)
for reg in ["pre", "post"]:
    p = dict(paths["P1_steo_latest"])
    _, y0 = run(p, reg)
    for qq in Q[2:]:
        p[qq] += 10
    _, y1 = run(p, reg)
    rows.append(["sens_plus10_2027", "2027 Q4/Q4", f"P1 +$10 in 2027Q1-Q4, {reg}", round(y1 - y0, 4),
                 "pp change in 2027 Q4/Q4 core PCE"])

# 4. Flat-Brent break-even from 2026-11-12 (same splice as P2): flat level X such that the
#    2027 Q4/Q4 adjustment equals a target (0 = baseline 2.40; also +0.25 pp)
obs_part = paths["P2_110_flat"]["2026Q4"] - REMAIN_W * 110.0  # weighted observed Oct 1-Nov 11 part


def flat_path(X):
    p = {"2026Q3": paths["P2_110_flat"]["2026Q3"], "2026Q4": obs_part + REMAIN_W * X}
    for qq in Q[2:]:
        p[qq] = X
    return p


def solve(reg, target):
    lo, hi = 20.0, 200.0
    for _ in range(100):
        mid = (lo + hi) / 2
        _, y = run(flat_path(mid), reg)
        if y - B27 < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


_, chk = run(flat_path(110.0), "post")
rows.append(["flat_check", "2027 Q4/Q4", "flat $110 rebuilt (should equal P2 x post)", round(chk, 4),
             f"pipeline {pipe_q4q4[('P2_110_flat', 'post')]:.4f}"])
for reg in ["pre", "post"]:
    for tgt in [0.0, 0.25, 0.5]:
        X = solve(reg, tgt)
        val = "not reached below $200" if X > 199.99 else round(X, 2)
        rows.append(["flat_breakeven", "2027 Q4/Q4", f"{reg}: flat Brent from Nov 12 giving adj {tgt:+.2f} pp",
                     val, "$/bbl, flat 2026-11-12..2027Q4; 2026Q3 actual and Oct1-Nov11 observed kept"])

# 5. Flat at the last observed spot ($92.14, 2026-11-11)
for reg in ["pre", "post"]:
    _, y = run(flat_path(92.14), reg)
    rows.append(["flat_spot", "2027 Q4/Q4", f"flat $92.14 (EIA spot 2026-11-11), {reg}", round(y, 4),
                 f"adj {y - B27:+.4f} pp vs baseline"])

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["check", "measure", "case", "value", "note"])
    w.writerows(rows)
for r in rows:
    print(r)
