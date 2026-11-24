"""Q11 build: confirming items for indirect (second-round) energy effects, Oct 2026.
 (a) Airfares: CPI airline fares (CUSR0000SETG01 SA), PCE air transportation price index (BEA U20404 line 207, SA), PPI airline
     passenger services (WPU3022 NSA), vs jet fuel (PPI WPU057203 NSA; EIA US Gulf Coast kerosene-type jet fuel spot, monthly).
 (b) Freight/delivery: PPI truck transportation of freight (WPU3012 NSA) vs diesel (PPI WPU057303 NSA; EIA NY Harbor? no: US Gulf Coast
     ULSD spot as saved), downstream CPI food away from home (CUSR0000SEFV SA).
Inputs: 03_Data/Raw/BLS_CPI_PPI_q11_2026-11-15/, 03_Data/Raw/EIA_fuel_spot_2026-11-15/, pipeline raw BEA U20404 (2026-11-10 vintage).
Outputs: outputs/C_q11_series.csv (long monthly), outputs/C_q11_lag_stats.csv, outputs/C_q11_confirming_items.csv
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q11_build.py
Note: BLS did not publish Oct 2025 CPI (lapse in appropriations), so CPI Oct 2025 is missing; mm for Nov 2025, 3m ann for Oct-Dec 2025
and yoy for Oct 2026 are NaN for CPI series (gap-safe calculation on a regular monthly grid).
"""
import sys, glob, json
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
import pandas as pd, numpy as np

S = RAW / "BLS_CPI_PPI_q11_2026-11-15"
grid = pd.period_range("2017-01", "2026-10", freq="M")
ser = {}
for f in sorted(glob.glob(str(S / "bls_api_q11_2017_2026_batch*.json"))):
    for s in json.load(open(f))["Results"]["series"]:
        d = {pd.Period(f"{o['year']}-{o['period'][1:]}", "M"): (float(o["value"]) if o["value"] not in ("-", "") else np.nan)
             for o in s["data"] if o["period"].startswith("M") and o["period"] != "M13"}
        ser[s["seriesID"]] = pd.Series(d).reindex(grid)
        ser[s["seriesID"]].attrs["bls"] = True

# BEA PCE air transportation (pipeline raw, 2026-11-10 vintage; last revised 2026-10-29)
j = json.load(open(ROOT / "03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json"))
rows = [r for r in j["BEAAPI"]["Results"]["Data"] if r["LineNumber"] == "207"]
ser["PCE_AIR_U20404_L207"] = pd.Series({pd.Period(r["TimePeriod"].replace("M", "-"), "M"): float(r["DataValue"]) for r in rows}).reindex(grid)


def eia(path, col):
    d = pd.read_excel(path, sheet_name="Data 1", header=None, skiprows=3)
    d.columns = ["date", col]
    d["date"] = pd.to_datetime(d["date"]).dt.to_period("M")
    return d.set_index("date")[col].reindex(grid)


E = RAW / "EIA_fuel_spot_2026-11-15"
ser["EIA_JET_USGC_m"] = eia(E / "EIA_EER_EPJK_PF4_RGC_DPGm.xls", "jet")
ser["EIA_ULSD_USGC_m"] = eia(E / "EIA_EER_EPD2DXL0_PF4_RGC_DPGm.xls", "ulsd")

meta = {
    "CUSR0000SETG01": ("CPI airline fares", "SA", "BLS CPI-U"),
    "CUUR0000SETG01": ("CPI airline fares", "NSA", "BLS CPI-U"),
    "CUSR0000SEFV": ("CPI food away from home", "SA", "BLS CPI-U"),
    "CUSR0000SEFV01": ("CPI full service meals and snacks", "SA", "BLS CPI-U"),
    "CUSR0000SAS": ("CPI services (all)", "SA", "BLS CPI-U"),
    "CUSR0000SETG": ("CPI public transportation", "SA", "BLS CPI-U"),
    "PCE_AIR_U20404_L207": ("PCE price index: air transportation (Fisher, 2017=100)", "SA", "BEA Table 2.4.4U line 207 (pipeline raw 2026-11-10; to Sep 2026)"),
    "WPU3022": ("PPI airline passenger services (commodity)", "NSA", "BLS PPI"),
    "WPS3022": ("PPI airline passenger services (commodity)", "SA", "BLS PPI"),
    "WPU057203": ("PPI jet fuel", "NSA", "BLS PPI"),
    "WPU057303": ("PPI No. 2 diesel fuel", "NSA", "BLS PPI"),
    "WPS057303": ("PPI No. 2 diesel fuel", "SA", "BLS PPI"),
    "WPU3012": ("PPI truck transportation of freight (commodity)", "NSA", "BLS PPI"),
    "WPSFD422": ("PPI final demand transportation and warehousing", "SA", "BLS PPI"),
    "EIA_JET_USGC_m": ("EIA US Gulf Coast kerosene-type jet fuel spot, monthly avg, $/gal", "NSA", "EIA EER_EPJK_PF4_RGC_DPG"),
    "EIA_ULSD_USGC_m": ("EIA US Gulf Coast ULSD (No. 2 diesel) spot, monthly avg, $/gal", "NSA", "EIA EER_EPD2DXL0_PF4_RGC_DPG"),
}
frames = []
calc = {}
for sid, (title, sa, src) in meta.items():
    s = ser[sid].astype(float)
    mm = (s / s.shift(1) - 1) * 100
    a3 = ((s / s.shift(3)) ** 4 - 1) * 100
    yy = (s / s.shift(12) - 1) * 100
    calc[sid] = pd.DataFrame({"mm": mm, "ann3m": a3, "yoy": yy, "idx": s})
    d = calc[sid].reset_index().rename(columns={"index": "month"})
    d.insert(0, "series_id", sid); d.insert(1, "title", title); d["seasonal"] = sa; d["source"] = src
    frames.append(d[d.month >= pd.Period("2018-01", "M")])
long = pd.concat(frames)
long["month"] = long["month"].astype(str)
long.round(4).to_csv(OUT / "C_q11_series.csv", index=False)

# ---------- lag statistics: monthly log changes, 2018-01..2026-09/10, excluding the missing Oct/Nov 2025 CPI months ----------
def lagcorr(x_id, y_id, maxlag=6, start="2018-01", end="2026-10", exclude=("2025-10", "2025-11")):
    x = calc[x_id]["mm"]; y = calc[y_id]["mm"]
    rows = []
    for L in range(0, maxlag + 1):
        d = pd.concat([x.shift(L).rename("x"), y.rename("y")], axis=1).loc[start:end]
        d = d[~d.index.astype(str).isin(exclude)].dropna()
        # also drop months whose lagged x falls in the gap
        rows.append({"x_series": x_id, "y_series": y_id, "lag_months_x_leads": L, "corr_mm": d["x"].corr(d["y"]), "n": len(d)})
    return rows


pairs = [("WPU057203", "CUSR0000SETG01"), ("EIA_JET_USGC_m", "CUSR0000SETG01"), ("WPU057203", "PCE_AIR_U20404_L207"), ("WPU057203", "WPS3022"),
         ("EIA_JET_USGC_m", "WPS3022"), ("WPU057303", "WPU3012"), ("EIA_ULSD_USGC_m", "WPU3012"), ("WPU057303", "CUSR0000SEFV"), ("WPU3012", "CUSR0000SEFV")]
lag = pd.DataFrame([r for p in pairs for r in lagcorr(*p)])
lag["window"] = "2018-01..2026-10 monthly % changes (ex 2025-10/11 for CPI gaps)"
lag.round(3).to_csv(OUT / "C_q11_lag_stats.csv", index=False)
best = lag.loc[lag.groupby(["x_series", "y_series"])["corr_mm"].apply(lambda s: s.abs().idxmax())]
print(best[["x_series", "y_series", "lag_months_x_leads", "corr_mm", "n"]].round(3).to_string())
# same on 2022-01 onward to avoid pandemic-era distortions
lag2 = pd.DataFrame([dict(r, window="2022-01..2026-10") for p in pairs for r in lagcorr(*p, start="2022-01")])
lag2.round(3).to_csv(OUT / "C_q11_lag_stats_2022on.csv", index=False)
print(lag2.loc[lag2.groupby(["x_series", "y_series"])["corr_mm"].apply(lambda s: s.abs().idxmax())][["x_series", "y_series", "lag_months_x_leads", "corr_mm", "n"]].round(3).to_string())

# ---------- episode tables: Feb 2026 = 100 (pre-shock), peak, latest ----------
base = pd.Period("2026-02", "M")
ep = []
for sid in ["WPU057203", "EIA_JET_USGC_m", "CUSR0000SETG01", "PCE_AIR_U20404_L207", "WPU3022", "WPS3022", "WPU057303", "WPS057303", "EIA_ULSD_USGC_m", "WPU3012", "CUSR0000SEFV", "CUSR0000SEFV01", "WPSFD422"]:
    s = calc[sid]["idx"]; b = s.loc[base]
    r = s.loc["2026-02":] / b * 100
    ep.append({"series_id": sid, "title": meta[sid][0], "Feb26=100_Mar": r.get(pd.Period("2026-03", "M")), "Apr": r.get(pd.Period("2026-04", "M")), "May": r.get(pd.Period("2026-05", "M")),
               "Jun": r.get(pd.Period("2026-06", "M")), "Jul": r.get(pd.Period("2026-07", "M")), "Aug": r.get(pd.Period("2026-08", "M")),
               "Sep": r.get(pd.Period("2026-09", "M")), "Oct": r.get(pd.Period("2026-10", "M")),
               "peak_level": r.max(), "peak_month": str(r.idxmax()),
               "mm_Sep26": calc[sid]["mm"].loc["2026-09"], "mm_Oct26": calc[sid]["mm"].loc["2026-10"],
               "ann3m_Sep26": calc[sid]["ann3m"].loc["2026-09"], "ann3m_Oct26": calc[sid]["ann3m"].loc["2026-10"],
               "yoy_Sep26": calc[sid]["yoy"].loc["2026-09"], "yoy_Oct26": calc[sid]["yoy"].loc["2026-10"]})
ep = pd.DataFrame(ep)
ep.round(2).to_csv(OUT / "C_q11_confirming_items.csv", index=False)
pd.set_option("display.width", 300, "display.max_columns", 40)
print(ep.round(1).to_string())
# 2018-19 average y/y for context
for sid in ["CUSR0000SETG01", "PCE_AIR_U20404_L207", "WPU3022", "WPS3022", "WPU3012", "CUSR0000SEFV"]:
    print(sid, "avg yoy 2018-19:", calc[sid]["yoy"].loc["2018-01":"2019-12"].mean().round(2))
# airline fare CPI full recent path
print(pd.concat([calc[k]["idx"].loc["2025-09":].rename(k) for k in ["CUSR0000SETG01", "WPU3022", "WPS3022", "WPU057203", "EIA_JET_USGC_m"]], axis=1).round(2).to_string())
