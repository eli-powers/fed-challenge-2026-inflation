"""Checks for the Oct 2026 interpolated-base 12m CPI (approx., interpolated Oct 2025 base).

Run from the project root:  python3 -I "02_Research/Subtasks/02_refresh_baskets/code/oct2026_interp_checks.py"
Read-only; inputs are pipeline raw files saved 2026-11-10.
 1. BLS headline/core NSA: 12m on interpolated base sqrt(Sep25*Nov25), plus 11-month (Nov 2025 base) and
    13-month (Sep 2025 base) bounds. Raw changes over 11 / 13 months, not annualized.
 2. Cleveland Fed: Oct/Nov 2025 monthly changes in mcpi_revised / trim_revised; 12m chained from monthly changes
    vs Cleveland's published 12m (usinflationdata.zip); index-level check of I_Oct25 vs sqrt(I_Sep25*I_Nov25).
 3. Atlanta Fed sticky-price CPI: Oct vs Nov 2025 monthly relatives; 12m chained from monthly changes vs published
    12mo column; same index-level check.
"""
import io
import json
import zipfile
from pathlib import Path

import pandas as pd

PI = Path("03_Data/pipelines/Price indexes")
D = "2026-11-10"

# ---------------------------------------------------------------- 1. BLS bounds
lev = {}
for f in sorted((PI / "CPI" / "raw").glob(f"bls_api_cpi_basket_2017_2026_batch*_{D}.json")):
    for s in json.loads(f.read_bytes())["Results"]["series"]:
        if s["seriesID"] in ("CUUR0000SA0", "CUUR0000SA0L1E"):
            lev[s["seriesID"]] = {f"{x['year']}-{x['period'][1:]}": float(x["value"]) for x in s["data"]
                                  if x["period"].startswith("M") and x["value"] not in ("-", "")}
print("1. BLS CPI-U NSA, Oct 2026 vs Oct 2025 (approx., interpolated Oct 2025 base)")
for sid, lab in (("CUUR0000SA0", "headline"), ("CUUR0000SA0L1E", "core")):
    L = lev[sid]
    assert "2025-10" not in L
    base = (L["2025-09"] * L["2025-11"]) ** 0.5
    o = L["2026-10"]
    print(f"   {lab} {sid}: Sep25 {L['2025-09']}, Nov25 {L['2025-11']}, interp Oct25 {base:.3f}, Oct26 {o}")
    print(f"     12m approx {(o / base - 1) * 100:.3f}%   11-month (Nov 2025 base) {(o / L['2025-11'] - 1) * 100:.3f}%   "
          f"13-month (Sep 2025 base) {(o / L['2025-09'] - 1) * 100:.3f}%")

# ---------------------------------------------------------------- 2. Cleveland
TM = PI / "Trimmed mean" / "raw"
z = zipfile.ZipFile(TM / f"clevelandfed_usinflationdata_{D}.zip")
u = pd.read_csv(io.BytesIO(z.read("usinflationdata.csv")), skiprows=[1])
u["Date"] = pd.to_datetime(u["Date"])
u = u.set_index("Date")
print("\n2. Cleveland Fed")
for key, col_m, idx_col, yoy_col in (
        ("mcpi_revised", "mcpi_monthly_chg", "Revised FRB Cleveland Median CPI SA, (Dec-82=100)", "Revised FRB Cleveland Median CPI SA, (Dec-82=100) % Change - Year to Year"),
        ("trim_revised", "trim_monthly_chg", "Revised 16% trimmed mean SA, (Dec-82=100)", "Revised 16% trimmed mean SA, (Dec-82=100) % Change - Year to Year")):
    m = pd.read_csv(TM / f"clevelandfed_{key}_{D}.csv")
    m.columns = [c.strip() for c in m.columns]
    m["date"] = pd.to_datetime(m["date"])
    m = m.set_index("date")[col_m]
    g10, g11 = m["2025-10-01"], m["2025-11-01"]
    chain = ((1 + m["2025-11-01":"2026-10-01"]).prod() - 1) * 100
    I = pd.to_numeric(u[idx_col], errors="coerce")
    pub = pd.to_numeric(u[yoy_col], errors="coerce")["2026-10-01"]
    geo = (I["2025-09-01"] * I["2025-11-01"]) ** 0.5
    print(f"   {key}: Oct25 m/m {g10:.6%}, Nov25 m/m {g11:.6%} (equal: {abs(g10 - g11) < 1e-12}); diff {g10 - g11:.2e}")
    print(f"     12m Oct 2026: published {pub:.4f}; chained from monthly file {chain:.4f}; from index ratio {(I['2026-10-01'] / I['2025-10-01'] - 1) * 100:.4f}")
    print(f"     index: I_Oct25 {I['2025-10-01']:.4f} vs sqrt(I_Sep25*I_Nov25) {geo:.4f}; 12m on geometric base {(I['2026-10-01'] / geo - 1) * 100:.4f}; "
          f"11-month {(I['2026-10-01'] / I['2025-11-01'] - 1) * 100:.4f}; 13-month {(I['2026-10-01'] / I['2025-09-01'] - 1) * 100:.4f}")

# ---------------------------------------------------------------- 3. Atlanta
a = pd.read_excel(PI / "Sticky CPI" / "raw" / f"atlantafed_sticky_price_cpi_{D}.xlsx", sheet_name="Data", header=None)
hdr = a.iloc[0].tolist()
a = a.iloc[1:].copy()
a[0] = pd.to_datetime(a[0])
a = a.set_index(0)
print("\n3. Atlanta Fed sticky-price CPI (monthly column = monthly change, fraction)")
for name, (mc, yc) in {"Flexible CPI": (1, 4), "Core Flexible CPI": (5, 8), "Sticky CPI": (9, 12), "Core Sticky CPI": (13, 16), "Sticky CPI ex-shelter": (17, 20)}.items():
    m = pd.to_numeric(a[mc], errors="coerce")
    g10, g11 = m["2025-10-01"], m["2025-11-01"]
    chain = ((1 + m["2025-11-01":"2026-10-01"]).prod() - 1) * 100
    I = (1 + m.fillna(0)).cumprod()
    geo = (I["2025-09-01"] * I["2025-11-01"]) ** 0.5
    pub = pd.to_numeric(a[yc], errors="coerce")["2026-10-01"]
    print(f"   {name} [{hdr[mc]}]: Oct25 {g10:.6f} Nov25 {g11:.6f} equal={abs(g10 - g11) < 1e-9}; 12m Oct26 published {pub:.4f}, "
          f"chained {chain:.4f}, on geometric base {(I['2026-10-01'] / geo - 1) * 100:.4f}")
