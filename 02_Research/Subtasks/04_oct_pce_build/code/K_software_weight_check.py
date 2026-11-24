"""Coordinator check (2026-11-13): how the software composite's blend weights (BEA line 50) are estimated,
three ways, for target month 2026-09 (fit sample 2022-01 .. 2026-08, 12-month log changes, percent).
Run from the project root: python3 "02_Research/Subtasks/04_oct_pce_build/code/K_software_weight_check.py"
Inputs: 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json (line 50, SA index)
        02_Research/Subtasks/04_oct_pce_build/outputs/component_series_history.csv (CUUR0000SEEE02, PCU5132105132107,
        PCU5182105182105; NSA; Oct 2025 CPI filled with the geometric mean of Sep and Nov, as in D_common)
Output: 02_Research/Subtasks/04_oct_pce_build/outputs/K_software_weight_check.csv
"""
import json, numpy as np, pandas as pd
from scipy.optimize import nnls
SUB = "02_Research/Subtasks/04_oct_pce_build/"
def find(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "Data" and isinstance(v, list): return v
            r = find(v)
            if r is not None: return r
    elif isinstance(x, list):
        for v in x:
            r = find(v)
            if r is not None: return r
u = pd.DataFrame(find(json.load(open("03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json"))))
b = u[u.LineNumber == "50"].copy(); b.index = pd.PeriodIndex(b.TimePeriod.str.replace("M", "-"), freq="M")
y = np.log(b.DataValue.astype(float)).diff(12) * 100
h = pd.read_csv(SUB + "outputs/component_series_history.csv", comment="#")
h["m"] = pd.PeriodIndex(h.year.astype(str) + "-" + h.period.str[1:], freq="M")
ids = ["CUUR0000SEEE02", "PCU5132105132107", "PCU5182105182105"]
lv = h[h.series_id.isin(ids)].pivot_table(index="m", columns="series_id", values="value", aggfunc="first").sort_index()
o = pd.Period("2025-10", "M")
if pd.isna(lv.at[o, ids[0]]): lv.at[o, ids[0]] = np.sqrt(lv.at[o - 1, ids[0]] * lv.at[o + 1, ids[0]])
X = np.log(lv[ids]).diff(12) * 100
d = pd.concat([y.rename("y"), X], axis=1).loc["2022-01":"2026-08"].dropna()
A, yy = d[ids].values, d.y.values
w_ols = np.linalg.lstsq(A, yy, rcond=None)[0]
Z = np.column_stack([A[:, 0] - A[:, 2], A[:, 1] - A[:, 2]]); g = np.linalg.lstsq(Z, yy - A[:, 2], rcond=None)[0]
w_sub = np.array([g[0], g[1], 1 - g.sum()])
M = 1e4; w_n, _ = nnls(np.vstack([A, M * np.ones((1, 3))]), np.concatenate([yy, [M]])); w_n = w_n / w_n.sum()
rows = []
for name, w in [("unconstrained OLS, no intercept", w_ols), ("sum-to-one by substitution (OLS)", w_sub),
                ("NNLS with sum-to-one (as in D_common)", w_n), ("equal weights", np.ones(3) / 3), ("CPI only", np.array([1.0, 0, 0]))]:
    r = yy - A @ w
    rows.append(dict(spec=name, w_cpi_software=round(w[0], 4), w_ppi_game_software=round(w[1], 4), w_ppi_hosting=round(w[2], 4),
                     sum_w=round(w.sum(), 4), rmse_pp=round(float(np.sqrt((r ** 2).mean())), 4),
                     r2=round(float(1 - (r ** 2).sum() / ((yy - yy.mean()) ** 2).sum()), 4), n=len(d), sample="2022-01..2026-08"))
out = pd.DataFrame(rows); out.to_csv(SUB + "outputs/K_software_weight_check.csv", index=False); print(out.to_string())
