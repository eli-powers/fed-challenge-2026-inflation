"""Q11b build. (1) Diesel -> food (CPI food at home / away from home vs EIA retail diesel, PPI diesel, PPI truck freight), lag correlations;
(2) CPI transportation services Oct 2026 decomposition with Sep-2026 relative importance (BLS release Table 2) ; (3) CPI motor vehicle insurance history and CPI-PCE gap.
Inputs (read only): 03_Data/Raw/CPI_q11b_2026-11-15b/ (BLS API json, CPI release tables, EIA retail diesel xls, BLS insurance factsheet),
03_Data/Raw/BLS_CPI_PPI_q11_2026-11-15/ (PPI diesel, truck freight; fetched earlier today), pipeline raw BEA U20404 (PCE line 279).
Outputs: outputs/C_q11b_food_diesel_series.csv, C_q11b_food_diesel_lags.csv, C_q11b_transport_services_decomp.csv, C_q11b_motor_insurance.csv, C_q11b_checks.csv
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q11b_build.py (project root)."""
import sys, glob, json, re, html
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
import pandas as pd, numpy as np

D = RAW / "CPI_q11b_2026-11-15b"
grid = pd.period_range("2017-01", "2026-10", freq="M")


def load(pattern):
    out = {}
    for f in sorted(glob.glob(str(pattern))):
        for s in json.load(open(f))["Results"]["series"]:
            out[s["seriesID"]] = pd.Series({pd.Period(f"{o['year']}-{o['period'][1:]}", "M"): (float(o["value"]) if o["value"] not in ("-", "") else np.nan)
                                            for o in s["data"] if o["period"].startswith("M") and o["period"] != "M13"}).reindex(grid)
    return out


ser = load(D / "bls_api_cpi_q11b_batch*.json")
ser.update(load(RAW / "BLS_CPI_PPI_q11_2026-11-15/bls_api_q11_2017_2026_batch*.json"))
d = pd.read_excel(D / "eia_retail_diesel_monthly.xls", sheet_name="Data 1", header=None, skiprows=3)
d.columns = ["date", "v"]; d["date"] = pd.to_datetime(d["date"]).dt.to_period("M")
ser["EIA_RETAIL_DIESEL"] = d.set_index("date")["v"].reindex(grid)
j = json.load(open(ROOT / "03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json"))
ser["PCE_MV_INS_U20404_L279"] = pd.Series({pd.Period(r["TimePeriod"].replace("M", "-"), "M"): float(r["DataValue"]) for r in j["BEAAPI"]["Results"]["Data"] if r["LineNumber"] == "279"}).reindex(grid)


def stats(s):
    return pd.DataFrame({"idx": s, "mm": (s / s.shift(1) - 1) * 100, "ann3m": ((s / s.shift(3)) ** 4 - 1) * 100, "yoy": (s / s.shift(12) - 1) * 100})


C = {k: stats(v.astype(float)) for k, v in ser.items()}
checks = []

# ================= Item 1 =================
titles = {"CUSR0000SAF11": "CPI food at home (SA)", "CUSR0000SEFV": "CPI food away from home (SA)", "CUSR0000SAF1": "CPI food (SA)",
          "EIA_RETAIL_DIESEL": "EIA US retail on-highway diesel, monthly avg $/gal (NSA)", "WPS057303": "PPI No. 2 diesel (SA)", "WPU057303": "PPI No. 2 diesel (NSA)",
          "WPU3012": "PPI truck transportation of freight (NSA)"}
rows = []
for k, t in titles.items():
    x = C[k].reset_index().rename(columns={"index": "month"}); x.insert(0, "series_id", k); x.insert(1, "title", t)
    rows.append(x[x.month >= pd.Period("2018-01", "M")])
pd.concat(rows).assign(month=lambda x: x.month.astype(str)).round(4).to_csv(OUT / "C_q11b_food_diesel_series.csv", index=False)


def lagrows(xk, yk, start, maxlag=9):
    r = []
    for L in range(maxlag + 1):
        z = pd.concat([C[xk]["mm"].shift(L).rename("x"), C[yk]["mm"].rename("y")], axis=1).loc[start:"2026-10"].dropna()
        r.append({"x_series": xk, "y_series": yk, "lag_x_leads_months": L, "corr_mm": z.x.corr(z.y), "n": len(z), "window": f"{start}..2026-10"})
    return r


L = []
for xk in ["EIA_RETAIL_DIESEL", "WPS057303", "WPU3012"]:
    for yk in ["CUSR0000SAF11", "CUSR0000SEFV"]:
        for st in ["2018-01", "2022-01"]:
            L += lagrows(xk, yk, st)
lag = pd.DataFrame(L); lag.round(3).to_csv(OUT / "C_q11b_food_diesel_lags.csv", index=False)
print(lag.pivot_table(index=["window", "x_series", "y_series"], columns="lag_x_leads_months", values="corr_mm").round(2).to_string())
# diagnostics: Oct 2026 and Feb=100
for k in titles:
    s = C[k]
    print(k, "Sep mm/ann3m/yoy", s.loc["2026-09", ["mm", "ann3m", "yoy"]].round(2).tolist(), "Oct", s.loc["2026-10", ["mm", "ann3m", "yoy"]].round(2).tolist(),
          "Feb=100 Oct", round(s.loc["2026-10", "idx"] / s.loc["2026-02", "idx"] * 100, 1), "avg yoy 18-19", round(s.loc["2018-01":"2019-12", "yoy"].mean(), 2))
print("food at home mm 2026:", C["CUSR0000SAF11"].loc["2026-01":, "mm"].round(2).tolist())
print("FAFH mm 2026:", C["CUSR0000SEFV"].loc["2026-01":, "mm"].round(2).tolist())
print("retail diesel $/gal 2026:", C["EIA_RETAIL_DIESEL"].loc["2026-01":, "idx"].round(2).tolist())

# ================= Item 2 =================
t = open(D / "bls_cpi_news_release_t02_2026-11-15.htm", encoding="utf8", errors="ignore").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S); t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
names = ["Transportation services", "Leased cars and trucks", "Car and truck rental", "Motor vehicle maintenance and repair", "Motor vehicle insurance", "Motor vehicle fees",
         "Public transportation", "Airline fares", "Other intercity transportation", "Intracity transportation", "Food at home", "Food away from home"]
tab = {}
for n in names:
    # row pattern: name [ (n) footnotes ] RI(Sep26) 12m(-) unadj_oct SA_aug SA_sep SA_oct
    m = re.search(re.escape(n) + r"(?:\s*\( \d+ \))* ([\d.]+|-) (-|-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)", t)
    # take the occurrence that matches the transportation block (first with a numeric RI after the Food rows for food items)
    if n in ("Food at home", "Food away from home"):
        m = re.search(re.escape(n) + r"(?:\s*\( \d+ \))* ([\d.]+) (-|-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) (-?[\d.]+)", t)
    tab[n] = [m.group(i) for i in range(1, 7)] if m else None
    print(n, tab[n])
parent_w = float(tab["Transportation services"][0])
comp = ["Leased cars and trucks", "Car and truck rental", "Motor vehicle maintenance and repair", "Motor vehicle insurance", "Motor vehicle fees", "Airline fares",
        "Other intercity transportation", "Intracity transportation"]
api = {"Leased cars and trucks": "CUSR0000SETA03", "Car and truck rental": "CUSR0000SETA04", "Motor vehicle maintenance and repair": "CUSR0000SETD",
       "Motor vehicle insurance": "CUSR0000SETE", "Airline fares": "CUSR0000SETG01", "Other intercity transportation": "CUSR0000SETG02"}
dec = []
for n in comp:
    w = float(tab[n][0]); sa_aug, sa_sep, sa_oct = [float(x) for x in tab[n][3:6]]
    r = {"component": n, "relative_importance_Sep2026_pct_of_CPI": w, "share_of_transportation_services_pct": 100 * w / parent_w,
         "pub_SA_Aug_mm": sa_aug, "pub_SA_Sep_mm": sa_sep, "pub_SA_Oct_mm": sa_oct, "pub_unadjusted_Oct_mm": float(tab[n][2]),
         "contribution_Oct_pp_published_rounded": w / parent_w * sa_oct, "contribution_Sep_pp_published_rounded": w / parent_w * sa_sep}
    if n in api:
        a = C[api[n]]
        r["api_series"] = api[n]; r["api_SA_Oct_mm_unrounded"] = a.loc["2026-10", "mm"]; r["api_SA_Sep_mm"] = a.loc["2026-09", "mm"]; r["api_ann3m_Oct"] = a.loc["2026-10", "ann3m"]
        r["contribution_Oct_pp_api"] = w / parent_w * a.loc["2026-10", "mm"]
    else:
        r["api_series"] = "n/a (published series is NSA only; table footnote 1)"
    dec.append(r)
dec = pd.DataFrame(dec)
tot = {"component": "SUM of listed components", "relative_importance_Sep2026_pct_of_CPI": dec.relative_importance_Sep2026_pct_of_CPI.sum(),
       "share_of_transportation_services_pct": dec.share_of_transportation_services_pct.sum(),
       "contribution_Oct_pp_published_rounded": dec.contribution_Oct_pp_published_rounded.sum(), "contribution_Sep_pp_published_rounded": dec.contribution_Sep_pp_published_rounded.sum(),
       "contribution_Oct_pp_api": dec.contribution_Oct_pp_api.sum()}
par = {"component": "Transportation services (parent, published SA)", "relative_importance_Sep2026_pct_of_CPI": parent_w, "share_of_transportation_services_pct": 100.0,
       "pub_SA_Aug_mm": float(tab["Transportation services"][3]), "pub_SA_Sep_mm": float(tab["Transportation services"][4]), "pub_SA_Oct_mm": float(tab["Transportation services"][5]),
       "pub_unadjusted_Oct_mm": float(tab["Transportation services"][2]), "api_series": "CUSR0000SAS4",
       "api_SA_Oct_mm_unrounded": C["CUSR0000SAS4"].loc["2026-10", "mm"], "api_SA_Sep_mm": C["CUSR0000SAS4"].loc["2026-09", "mm"], "api_ann3m_Oct": C["CUSR0000SAS4"].loc["2026-10", "ann3m"]}
dec = pd.concat([dec, pd.DataFrame([tot, par])], ignore_index=True)
dec["contribution_share_of_parent_Oct_pct"] = dec["contribution_Oct_pp_published_rounded"] / par["api_SA_Oct_mm_unrounded"] * 100
dec["note"] = ("Weights: BLS CPI Table 2 relative importance Sep 2026 (start-of-month weights for Oct). Contribution = weight/parent weight x component m/m. "
               "Components whose SA series do not exist (fees, intracity, leased cars in release) use the table's value, which footnote 1 marks NSA. Rounded published m/m (1 decimal) so contributions are approximate.")
dec.round(4).to_csv(OUT / "C_q11b_transport_services_decomp.csv", index=False)
pd.set_option("display.width", 250, "display.max_columns", 30)
print(dec[["component", "relative_importance_Sep2026_pct_of_CPI", "share_of_transportation_services_pct", "pub_SA_Oct_mm", "contribution_Oct_pp_published_rounded", "api_SA_Oct_mm_unrounded", "contribution_Oct_pp_api"]].round(3).to_string())
print("transp services SA mm Aug-Oct 2026 (api):", C["CUSR0000SAS4"].loc["2026-05":, "mm"].round(2).tolist())

# ================= Item 3 =================
ins = C["CUSR0000SETE"].copy(); insn = C["CUUR0000SETE"]
out = ins.rename(columns={"idx": "cpi_mv_insurance_SA_index"}).join(insn["yoy"].rename("cpi_mv_insurance_NSA_yoy")).join(insn["mm"].rename("cpi_mv_insurance_NSA_mm"))
pce = C["PCE_MV_INS_U20404_L279"]
out = out.join(pce["idx"].rename("pce_net_mv_and_other_transport_insurance_index")).join(pce["mm"].rename("pce_mm")).join(pce["ann3m"].rename("pce_ann3m")).join(pce["yoy"].rename("pce_yoy"))
for k, n in [("CUSR0000SETD", "cpi_mv_maint_repair"), ("CUSR0000SETA01", "cpi_new_vehicles"), ("CUSR0000SETA02", "cpi_used_vehicles")]:
    out = out.join(C[k]["yoy"].rename(n + "_SA_yoy")).join(C[k]["ann3m"].rename(n + "_SA_ann3m"))
out = out.loc["2018-01":].reset_index().rename(columns={"index": "month"}); out["month"] = out["month"].astype(str)
out.round(3).to_csv(OUT / "C_q11b_motor_insurance.csv", index=False)
o = out.set_index("month")
print(o.loc["2026-03":, ["mm", "ann3m", "yoy", "cpi_mv_insurance_NSA_yoy", "pce_yoy", "pce_mm", "cpi_mv_maint_repair_SA_yoy", "cpi_new_vehicles_SA_yoy", "cpi_used_vehicles_SA_yoy"]].round(2).to_string())
s = ins["mm"].dropna(); s = s.loc["2018-01":]
print("insurance mm Oct 2026 rank among", len(s), ":", int((s > s.loc["2026-10"]).sum() + 1), "| Sep:", int((s > s.loc["2026-09"]).sum() + 1))
print("insurance mm each Oct/Nov (SA):", {str(p): round(v, 2) for p, v in s.items() if p.month in (10, 11)})
print("insurance NSA mm each Oct/Nov:", {str(p): round(v, 2) for p, v in insn["mm"].dropna().loc["2018-01":].items() if p.month in (10, 11)})
print("insurance yoy peak", ins["yoy"].loc["2018-01":].idxmax(), round(ins["yoy"].loc["2018-01":].max(), 1), "| 2018-19 avg yoy", round(ins["yoy"].loc["2018-01":"2019-12"].mean(), 2), "| min yoy since 2024", ins["yoy"].loc["2024-01":].idxmin(), round(ins["yoy"].loc["2024-01":].min(), 1))
print("mm 2025-2026:", {str(p): round(v, 2) for p, v in ins["mm"].loc["2025-01":].items()})
print("PCE ins yoy Sep26:", round(pce["yoy"].loc["2026-09"], 2), " CPI SA yoy Sep26:", round(ins["yoy"].loc["2026-09"], 2), " NSA yoy Sep26:", round(insn["yoy"].loc["2026-09"], 2))
