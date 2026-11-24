"""Q6: underlying trend measures (MCT, Dallas trimmed mean, Cleveland median/trimmed, BEA market-based core, supercore,
Logan measure = PCE services ex energy, ex housing, ex transportation) + roadmap check.
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/C_q6_underlying.py
"""
import importlib.util, json, warnings, re
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import brentq
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("C_common", Path.cwd() / "02_Research/Subtasks/11_slide3a_research/code/C_common.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)

P = lambda s: pd.Period(s, "M")
long = []  # series rows


def addser(group, name, sid, horizon, s, status, release, src, start="2018-01"):
    s = s.dropna()
    s = s[s.index >= P(start)]
    for p, v in s.items():
        st = status(p) if callable(status) else status
        long.append(dict(series_group=group, series=name, series_id=sid, horizon=horizon, period=str(p), value=round(float(v), 4),
                         status=st, release_date=release(p) if callable(release) else release, source_file=src))


def rates(idx):
    return {"1m": C.pct(idx, 1), "3m ann": C.ann(idx, 3), "6m ann": C.ann(idx, 6), "12m": C.pct(idx, 12)}


# ---------- BEA indexes from pipeline (T20804) ----------
def bea_idx(key):
    o = C.pipeline_obs("bea", key); o = o[o.horizon == "level"] if "horizon" in o else o
    return pd.Series(o.value.astype(float).values, index=o.date.dt.to_period("M"))

bea_src = "03_Data/pipelines/inflation_data/processed/bea/observations.csv (BEA NIPA T20804, vintage retrieved 2026-11-10, LastRevised 2026-10-29)"
BEA_REL = "2026-10-29"
idx = {k: bea_idx(k) for k in ["pce_price", "pce_core_price", "pce_market_based_core_price", "pce_services_ex_energy_housing_price"]}
labels = {"pce_price": ("Headline PCE price index", "T20804 L1 DPCERG"), "pce_core_price": ("Core PCE price index", "T20804 L25 DPCCRG"),
          "pce_market_based_core_price": ("Market-based core PCE (BEA)", "T20804 L31 DPCXRG"),
          "pce_services_ex_energy_housing_price": ("Supercore: PCE services ex energy and housing (BEA published)", "T20804 L28 IA001260")}
rt = {}
for k, (nm, sid) in labels.items():
    rt[k] = rates(idx[k])
    grp = "Reference" if k in ("pce_price", "pce_core_price") else "BEA derived"
    for h, s in rt[k].items():
        addser(grp, nm, sid, h + (" (% m/m)" if h == "1m" else " (% y/y)" if h == "12m" else " (annualized %)"), s, "actual", BEA_REL, bea_src)

# ---------- NY Fed MCT ----------
mct_f = C.RAWC / "NYFed_MCT_chart_data_2026-11-15.csv"
m = pd.read_csv(mct_f, skiprows=4, header=None, encoding="utf-8-sig")
names = ["blank", "date", "MCT_lower68", "MCT", "MCT_upper68", "MCT_minus_2017_19_avg", "Headline_PCE_12m", "Core_PCE_12m", "contrib_goods",
         "contrib_services_ex_housing", "contrib_housing", "goods_common", "goods_sector_specific", "svcs_exh_common", "svcs_exh_sector_specific", "housing_common", "housing_sector_specific"]
m.columns = names
m = m[m.date.notna()].copy(); m["p"] = pd.to_datetime(m.date).dt.to_period("M"); m = m.set_index("p")
MCT_REL = "2026-10-30"
for col, nm, hz in [("MCT", "NY Fed MCT (central estimate)", "annualized trend estimate"), ("MCT_lower68", "NY Fed MCT lower 68% band", "%"), ("MCT_upper68", "NY Fed MCT upper 68% band", "%"),
                    ("contrib_goods", "MCT sector contribution: core goods (pp vs 2017-19 avg)", "pp"), ("contrib_services_ex_housing", "MCT sector contribution: services ex housing (pp vs 2017-19 avg)", "pp"),
                    ("contrib_housing", "MCT sector contribution: housing (pp vs 2017-19 avg)", "pp"), ("MCT_minus_2017_19_avg", "MCT minus its 2017-19 average (pp; 4th MCT column, inferred label)", "pp")]:
    addser("NY Fed MCT", nm, "MCT/" + col, hz, m[col].astype(float), "actual", MCT_REL, C.rel(mct_f))

# ---------- Dallas trimmed mean PCE (FRED, Dallas-originated) ----------
rdq = pd.read_csv(C.PIPE / "processed/fed_expectations/release_dates.csv")
dal = {}
for sid, hz in [("PCETRIM1M158SFRBDAL", "1m annualized"), ("PCETRIM6M680SFRBDAL", "6m annualized"), ("PCETRIM12M159SFRBDAL", "12m (y/y)")]:
    s = C.fred(sid); s = C.monthly_period(s); dal[hz] = s
    addser("Dallas trimmed mean PCE", "Dallas Fed trimmed-mean PCE, " + hz, sid, hz, s, "actual", "2026-10-29 (BEA PCE release; Dallas posts same day per FRED/ALFRED)", C.rel(C.RAWC / f"FRED_{sid}_2026-11-15.json"))

# ---------- Cleveland median PCE ----------
cm = pd.read_csv(C.RAWC / "ClevelandFed_median_PCE_full_history_2026-11-15.csv")
cm.columns = ["date", "mm", "yy"]
cm["p"] = pd.to_datetime(cm.date, format="%m/%d/%Y").dt.to_period("M"); cm = cm.set_index("p")
cmm = cm.mm.astype(float)  # monthly % change
cmp_f = C.rel(C.RAWC / "ClevelandFed_median_PCE_full_history_2026-11-15.csv")
cidx = (1 + cmm.fillna(0) / 100).cumprod()
cal_rates = {"1m ann": ((1 + cmm / 100) ** 12 - 1) * 100, "3m ann": C.ann(cidx, 3), "6m ann": C.ann(cidx, 6), "12m (computed by compounding)": C.pct(cidx, 12)}
chk12 = (cal_rates["12m (computed by compounding)"] - cm.yy.astype(float)).dropna()
print("Cleveland median PCE compounded 12m vs published yy: max abs diff (2018+)", chk12[chk12.index >= P("2018-01")].abs().max())
CLE_PCE_REL = "2026-10-29"
addser("Cleveland median PCE", "Cleveland Fed median PCE, 1m % change (not annualized)", "median-pce-full-history.csv col2", "1m (% m/m)", cmm, "actual", CLE_PCE_REL, cmp_f)
addser("Cleveland median PCE", "Cleveland Fed median PCE, 12m % change (published)", "median-pce-full-history.csv col3", "12m (% y/y)", cm.yy.astype(float), "actual", CLE_PCE_REL, cmp_f)
for h in ["1m ann", "3m ann", "6m ann"]:
    addser("Cleveland median PCE", "Cleveland Fed median PCE, " + h + " (computed by compounding published monthly)", "computed", h, cal_rates[h], "actual", CLE_PCE_REL, cmp_f)

# ---------- Cleveland median / trimmed-mean CPI ----------
cc = pd.read_csv(C.PIPE / "raw/fed_expectations/clevelandfed_mediancpi_chartdata_2026-11-10.csv"); cc["p"] = pd.to_datetime(cc.date).dt.to_period("M"); cc = cc.set_index("p")
mc = pd.read_csv(C.RAWC / "ClevelandFed_mediancpi_mcpi_revised_2026-11-15.csv"); mc.columns = ["date", "mm", "ann"]; mc["p"] = pd.to_datetime(mc.date).dt.to_period("M"); mc = mc.set_index("p")
tr = pd.read_csv(C.RAWC / "ClevelandFed_mediancpi_trim_revised_2026-11-15.csv"); tr.columns = ["date", "mm", "ann"]; tr["p"] = pd.to_datetime(tr.date).dt.to_period("M"); tr = tr.set_index("p")
CPI_REL = "2026-11-10"
addser("Cleveland CPI", "Cleveland Fed median CPI, 12m", "mediancpi_chartdata col mediancpi (pipeline raw 2026-11-10)", "12m (% y/y)", cc.mediancpi.astype(float), "actual", CPI_REL, "03_Data/pipelines/inflation_data/raw/fed_expectations/clevelandfed_mediancpi_chartdata_2026-11-10.csv")
addser("Cleveland CPI", "Cleveland Fed 16% trimmed-mean CPI, 12m", "mediancpi_chartdata col trimmedmeancpi (pipeline raw 2026-11-10)", "12m (% y/y)", cc.trimmedmeancpi.astype(float), "actual", CPI_REL, "03_Data/pipelines/inflation_data/raw/fed_expectations/clevelandfed_mediancpi_chartdata_2026-11-10.csv")
addser("Cleveland CPI", "Cleveland Fed median CPI, 1m annualized", "mcpi_revised.csv ann_monthly_chg", "1m annualized", mc.ann.astype(float), "actual", CPI_REL, C.rel(C.RAWC / "ClevelandFed_mediancpi_mcpi_revised_2026-11-15.csv"))
addser("Cleveland CPI", "Cleveland Fed 16% trimmed-mean CPI, 1m annualized", "trim_revised.csv ann_monthly_chg", "1m annualized", tr.ann.astype(float), "actual", CPI_REL, C.rel(C.RAWC / "ClevelandFed_mediancpi_trim_revised_2026-11-15.csv"))
# FRED cross-check of 12m
for sid, col in [("MEDCPIM159SFRBCLE", "mediancpi"), ("TRMMEANCPIM159SFRBCLE", "trimmedmeancpi")]:
    f = C.monthly_period(C.fred(sid)); j = pd.concat([f, cc[col].astype(float)], axis=1, join="inner").dropna()
    print("FRED vs Cleveland chartdata", sid, "max abs diff", float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()))

# ---------- Logan measure from BEA U20404/U20405 ----------
def load(table):
    d = json.load(open(C.PCE_RAW / f"BEA_NIUnderlyingDetail_{table}_2026-11-10.json"))["BEAAPI"]["Results"]
    df = pd.DataFrame(d["Data"]); df["v"] = df.DataValue.str.replace(",", "").astype(float)
    df["t"] = pd.PeriodIndex(df.TimePeriod.str.replace("M", "-"), freq="M")
    return df.pivot_table(index="t", columns="LineNumber", values="v")

p, n = load("U20404"), load("U20405")

def remove(pa, na, px, nx):
    """Chain price index of (aggregate A minus component X). Two-part Fisher identity F^2 = L*P (as in 03_Data/pipelines/Price indexes/code/core_ex_oer.py)."""
    idx_ = [100.0]
    for t in range(1, len(pa)):
        F = pa.iloc[t] / pa.iloc[t - 1]; rx = px.iloc[t] / px.iloc[t - 1]
        sx0 = nx.iloc[t - 1] / na.iloc[t - 1]; sr0 = 1 - sx0
        wx1 = nx.iloc[t] / na.iloc[t]; wr1 = 1 - wx1
        f = lambda r: (sr0 * r + sx0 * rx) / (wr1 / r + wx1 / rx) - F * F
        idx_.append(idx_[-1] * brentq(f, 0.5, 1.5))
    return pd.Series(idx_, index=pa.index)

def combine(lines):
    idx_ = [100.0]
    for t in range(1, len(p)):
        r = p[lines].iloc[t] / p[lines].iloc[t - 1]; n0, n1 = n[lines].iloc[t - 1], n[lines].iloc[t]
        L = (n0 * r).sum() / n0.sum(); Pa = n1.sum() / (n1 / r).sum(); idx_.append(idx_[-1] * (L * Pa) ** 0.5)
    return pd.Series(idx_, index=p.index)

s376, s153, s190 = p["376"], p["153"], p["190"]
sup_der = remove(s376, n["376"], s153, n["153"])                     # services ex energy minus housing = supercore (derived)
nsup = n["376"] - n["153"]
logan_A = remove(sup_der, nsup, s190, n["190"])                      # method A: sequential exact removal
x2 = combine(["153", "190"]); logan_B = remove(s376, n["376"], x2, n["153"] + n["190"])  # method B: housing+transport removed jointly
sup_pub = idx["pce_services_ex_energy_housing_price"].reindex(p.index)
val = pd.DataFrame({"derived_12m": C.pct(sup_der, 12), "published_12m": C.pct(sup_pub, 12), "derived_1m": C.pct(sup_der, 1), "published_1m": C.pct(sup_pub, 1),
                    "derived_3m": C.ann(sup_der, 3), "published_3m": C.ann(sup_pub, 3)})
val["d12"] = val.derived_12m - val.published_12m; val["d1"] = val.derived_1m - val.published_1m; val["d3"] = val.derived_3m - val.published_3m
val2 = val[val.index >= P("2018-01")]
print("Supercore derived-vs-published (2018-01..2026-09): max|12m diff| %.4f  max|1m diff| %.4f  max|3m ann diff| %.4f ; Sep-2026 12m derived %.3f published %.3f"
      % (val2.d12.abs().max(), val2.d1.abs().max(), val2.d3.abs().max(), val.derived_12m.iloc[-1], val.published_12m.iloc[-1]))
print("Logan A vs B 12m latest: %.4f vs %.4f ; max abs diff 2018+: %.4f" % (C.pct(logan_A, 12).iloc[-1], C.pct(logan_B, 12).iloc[-1], (C.pct(logan_A, 12) - C.pct(logan_B, 12))[P("2018-01"):].abs().max()))
val.to_csv(C.OUTD / "C_q6_supercore_validation.csv", float_format="%.5f")

# ---------- October estimate from the audited build lines ----------
L = pd.read_csv(C.ROOT / "02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv")
Lc = L[(L.w_c > 0) & (L.line >= 150)].copy()
housing = Lc.line.between(154, 164); transport = Lc.line.between(190, 208)
def grp_mm(mask):
    d = Lc[mask]; return (d.w_c * d.pi).sum() / d.w_c.sum(), d.w_c.sum() / L.w_c.sum(), len(d)
g_sup, sh_sup, n_sup = grp_mm(~housing)
g_log, sh_log, n_log = grp_mm(~housing & ~transport)
g_trn, sh_trn, n_trn = grp_mm(transport)
g_svc, sh_svc, n_svc = grp_mm(pd.Series(True, index=Lc.index))
print("Oct est m/m: services ex energy %.4f (core share %.3f, %d lines); supercore %.4f (%.3f); logan %.4f (%.3f, %d lines); transport %.4f (%.3f)" %
      (g_svc, sh_svc, n_svc, g_sup, sh_sup, g_log, sh_log, n_log, g_trn, sh_trn))

# validate the leaf-Laspeyres approach on Sep 2026 using components.csv (Sep actual leaf m/m and Aug-base weights)
cc_ = pd.read_csv(C.ROOT / "03_Data/pipelines/Price indexes/PCE/processed/components.csv")
cc_ = cc_[(cc_.index_name == "PCE core") & (cc_.in_core == "Y")].copy()
cc_["line"] = cc_.component_id.str.extract(r"U20404 line (\d+)").astype(int)
cs = cc_[cc_.line >= 150]
def sep_mm(mask):
    d = cs[mask]; return (d.weight_base_1m * d.pct_1m_calc).sum() / d.weight_base_1m.sum()
hs = cs.line.between(154, 164); tr_ = cs.line.between(190, 208)
sep_leaf = {"supercore": sep_mm(~hs), "logan": sep_mm(~hs & ~tr_)}
sep_exact = {"supercore": float(C.pct(sup_pub, 1).iloc[-1]), "logan_A": float(C.pct(logan_A, 1).iloc[-1])}
print("Sep-2026 validation of leaf aggregation (m/m %%): supercore leaf %.4f vs exact(published) %.4f ; logan leaf %.4f vs exact(A) %.4f" %
      (sep_leaf["supercore"], sep_exact["supercore"], sep_leaf["logan"], sep_exact["logan_A"]))
# also: leaf aggregation vs exact over several recent months is not available (components.csv has Sep only); record Sep error as the bias estimate
sep_err = {"supercore": sep_leaf["supercore"] - sep_exact["supercore"], "logan": sep_leaf["logan"] - sep_exact["logan_A"]}

OCT = P("2026-10")
def with_oct(sep_idx, mm_oct):
    s = sep_idx.copy(); s = s[s.index <= P("2026-09")]; s.loc[OCT] = s.iloc[-1] * (1 + mm_oct / 100); return s

sup_pub_full = sup_pub.copy()
sup_oct = with_oct(idx["pce_services_ex_energy_housing_price"], g_sup)   # Sep actual (BEA published) chained with Oct est m/m
logan_oct = with_oct(logan_A, g_log)
sup_status = lambda p_: "est." if p_ == OCT else "actual"
for nm, s, sid in [("Supercore: PCE services ex energy and housing (BEA published through Sep; Oct est.)", sup_oct, "T20804 L28 IA001260 + Oct est. from D_build lines"),
                   ("Logan measure: PCE services ex energy, housing and transportation (derived; Oct est.)", logan_oct, "derived U20404/U20405 L376-L153-L190 + Oct est.")]:
    for h, r in rates(s).items():
        addser("Supercore / Logan measure", nm, sid, h + (" (% m/m)" if h == "1m" else " (% y/y)" if h == "12m" else " (annualized %)"), r, sup_status,
               lambda p_: "est. (Oct PCE due 2026-11-25)" if p_ == OCT else BEA_REL, "outputs C_q6_logan_measure.csv; " + bea_src, start="2018-01")

# Logan measure file
lm = pd.DataFrame({"month": [str(x) for x in logan_oct.index if x >= P("2017-01")], })
lo_r = rates(logan_oct)
lm = pd.DataFrame({"month": [str(x) for x in logan_oct.index], "index_2017_01=100": logan_oct.values, "1m_pct": lo_r["1m"].values, "3m_ann_pct": lo_r["3m ann"].values,
                   "6m_ann_pct": lo_r["6m ann"].values, "12m_pct": lo_r["12m"].values,
                   "status": ["est." if x == OCT else "actual" for x in logan_oct.index],
                   "lines_included": "BEA U20404 L376 (PCE services excl. energy) less L153 (Housing) less L190 (Transportation services); Oct est. = leaf-weighted m/m of %d D_build lines (line>=150, ex 154-164 housing, ex 190-208 transport; covers %.1f%% of core)" % (n_log, sh_log * 100)})
lm = lm[lm.month >= "2017-12"]
lm["method_B_12m_pct_(joint_removal)"] = [float(C.pct(logan_B, 12).get(P(x), np.nan)) if x != "2026-10" else np.nan for x in lm.month]
lm.round(4).to_csv(C.OUTD / "C_q6_logan_measure.csv", index=False)

# alt methods series for the long file
addser("Supercore / Logan measure", "Logan measure, method B (housing and transportation removed jointly), 12m", "derived", "12m (% y/y)", C.pct(logan_B, 12), "actual", BEA_REL, "BEA U20404/U20405 vintage 2026-11-10")
addser("Supercore / Logan measure", "Supercore derived from U20404/U20405 (L376 less L153), 12m (validation)", "derived", "12m (% y/y)", C.pct(sup_der, 12), "actual", BEA_REL, "BEA U20404/U20405 vintage 2026-11-10")

# ---------- Summary ----------
long_df = pd.DataFrame(long)
long_df.to_csv(C.OUTD / "C_q6_underlying.csv", index=False)

def summ_rows(group, name, hz, s, status_oct=False, release="", src=""):
    s = s.dropna(); s = s[s.index >= P("2018-01")]
    p18 = s[(s.index >= P("2018-01")) & (s.index <= P("2019-12"))]; p21 = s[(s.index >= P("2021-01")) & (s.index <= P("2023-12"))]
    return dict(group=group, series=name, horizon=hz, latest_period=str(s.index[-1]), latest_value=round(float(s.iloc[-1]), 3),
                latest_status="est." if (status_oct and s.index[-1] == OCT) else "actual", release_date=release,
                avg_2018_19=round(float(p18.mean()), 3), peak_2021_23=round(float(p21.max()), 3), peak_2021_23_period=str(p21.idxmax()), source_file=src)

SM = []
SM.append(summ_rows("NY Fed MCT", "MCT central", "% annualized trend", m.MCT.astype(float), release=MCT_REL, src=C.rel(mct_f)))
SM.append(summ_rows("NY Fed MCT", "MCT lower 68% band", "%", m.MCT_lower68.astype(float), release=MCT_REL, src=C.rel(mct_f)))
SM.append(summ_rows("NY Fed MCT", "MCT upper 68% band", "%", m.MCT_upper68.astype(float), release=MCT_REL, src=C.rel(mct_f)))
for h, s in dal.items():
    SM.append(summ_rows("Dallas trimmed mean PCE", "Dallas trimmed-mean PCE", h, s, release="2026-10-29", src="FRED PCETRIM*SFRBDAL (fetched 2026-11-15)"))
for h in ["1m ann", "3m ann", "6m ann"]:
    SM.append(summ_rows("Cleveland median PCE", "Cleveland median PCE (compounded)", h, cal_rates[h], release=CLE_PCE_REL, src=cmp_f))
SM.append(summ_rows("Cleveland median PCE", "Cleveland median PCE", "12m published", cm.yy.astype(float), release=CLE_PCE_REL, src=cmp_f))
SM.append(summ_rows("Cleveland median PCE", "Cleveland median PCE", "1m % m/m", cmm, release=CLE_PCE_REL, src=cmp_f))
SM.append(summ_rows("Cleveland CPI", "Median CPI", "12m", cc.mediancpi.astype(float), release=CPI_REL, src="pipeline raw clevelandfed_mediancpi_chartdata_2026-11-10.csv"))
SM.append(summ_rows("Cleveland CPI", "16% trimmed-mean CPI", "12m", cc.trimmedmeancpi.astype(float), release=CPI_REL, src="pipeline raw clevelandfed_mediancpi_chartdata_2026-11-10.csv"))
SM.append(summ_rows("Cleveland CPI", "Median CPI", "1m annualized", mc.ann.astype(float), release=CPI_REL, src="ClevelandFed_mediancpi_mcpi_revised_2026-11-15.csv"))
SM.append(summ_rows("Cleveland CPI", "16% trimmed-mean CPI", "1m annualized", tr.ann.astype(float), release=CPI_REL, src="ClevelandFed_mediancpi_trim_revised_2026-11-15.csv"))
for k, nm in [("pce_core_price", "Core PCE"), ("pce_price", "Headline PCE"), ("pce_market_based_core_price", "BEA market-based core PCE")]:
    for h, s in rt[k].items(): SM.append(summ_rows("BEA", nm, h, s, release=BEA_REL, src=bea_src))
for nm, s in [("Supercore (BEA L28; Oct est.)", sup_oct), ("Logan measure (services ex energy, housing, transportation; Oct est.)", logan_oct)]:
    for h, r in rates(s).items():
        row = summ_rows("Supercore / Logan measure", nm, h, r, status_oct=True, release="Sep: 2026-10-29; Oct est.", src="outputs/C_q6_logan_measure.csv")
        SM.append(row)
        # also Sep actual row
        sa = r[r.index <= P("2026-09")]
        row2 = summ_rows("Supercore / Logan measure", nm.replace("; Oct est.", "") + " [Sep actual]", h, sa, release=BEA_REL, src="outputs/C_q6_logan_measure.csv"); SM.append(row2)
pd.DataFrame(SM).to_csv(C.OUTD / "C_q6_summary.csv", index=False)

# ---------- Roadmap check ----------
rc = []
def g(group, series_name, hz, period):
    r = pd.DataFrame(SM); return None
dsep = dal["12m (y/y)"][P("2026-09")]; msep = float(m.MCT.astype(float)[P("2026-09")]); lsep = float(rates(logan_A)["12m"][P("2026-09")])
lsepB = float(rates(logan_B)["12m"][P("2026-09")])
core12 = float(rt["pce_core_price"]["12m"][P("2026-09")]); head12 = float(rt["pce_price"]["12m"][P("2026-09")])
target_pace = round(3.2 - 0.8, 1)
l1819 = float(rates(logan_A)["12m"][P("2018-01"):P("2019-12")].mean())
rc.append(dict(claim="NY Fed MCT 2.8% (Sep 2026)", roadmap_or_speech_value=2.8, publisher_value=round(msep, 3), diff=round(msep - 2.8, 3), verdict="match (rounds to 2.8)", vintage="NY Fed MCT Sep 2026 update, posted 10:00 ET 2026-10-30 (BEA Sep PCE vintage 2026-10-29); Aug revised up to 2.56", source=C.rel(mct_f)))
rc.append(dict(claim="Dallas trimmed-mean PCE 12m 2.3% (Sep 2026)", roadmap_or_speech_value=2.3, publisher_value=round(float(dsep), 3), diff=round(float(dsep) - 2.3, 3), verdict="match (2.26 rounds to 2.3)", vintage="Dallas series as on FRED PCETRIM12M159SFRBDAL fetched 2026-11-15; Sep 2026, BEA 2026-10-29 vintage", source="FRED PCETRIM12M159SFRBDAL; pipeline dallasfed xlsx"))
rc.append(dict(claim="Core services ex housing and transportation 12m 3.2% (Sep 2026) [Logan]", roadmap_or_speech_value=3.2, publisher_value=round(lsep, 3), diff=round(lsep - 3.2, 3), verdict="match (3.207 rounds to 3.2)", vintage="derived from BEA U20404/U20405 vintage 2026-11-10 (LastRevised 2026-10-29); method A sequential removal; method B %.3f" % lsepB, source="outputs/C_q6_logan_measure.csv"))
rc.append(dict(claim="Core PCE 12m 3.1% (Sep 2026) [Logan]", roadmap_or_speech_value=3.1, publisher_value=round(core12, 3), diff=round(core12 - 3.1, 3), verdict="match (3.12 rounds to 3.1)", vintage="BEA T20804 L25, 2026-10-29", source=bea_src))
rc.append(dict(claim="Headline PCE 12m 3.6% (Logan) / 3.7% (roadmap/summary) (Sep 2026)", roadmap_or_speech_value=3.6, publisher_value=round(head12, 3), diff=round(head12 - 3.6, 3), verdict="3.649 rounds to 3.6: Logan 3.6 matches; the 3.7 in 02_Research/External_views/Fed_officials_2026-11/summary.md does NOT match the BEA index (differs by +0.05 after rounding)", vintage="BEA T20804 L1, 2026-10-29", source=bea_src))
rc.append(dict(claim="Logan 'eight tenths above the target-consistent pace' => implied pace", roadmap_or_speech_value=target_pace, publisher_value=round(l1819, 3), diff=round(l1819 - target_pace, 3), verdict="implied pace = 3.2 - 0.8 = 2.4 (speech does not give the number or its source); our measure averaged %.2f over 2018-19 (12m)" % l1819, vintage="speech 2026-11-10; our derived measure", source="outputs/C_q6_logan_measure.csv"))
pd.DataFrame(rc).to_csv(C.OUTD / "C_q6_roadmap_check.csv", index=False)
print(pd.DataFrame(rc)[["claim", "roadmap_or_speech_value", "publisher_value", "diff"]])
print(pd.DataFrame(SM)[["group", "series", "horizon", "latest_period", "latest_value", "latest_status", "avg_2018_19", "peak_2021_23", "peak_2021_23_period"]].to_string())
json.dump(dict(oct_mm=dict(services_ex_energy=g_svc, supercore=g_sup, logan=g_log, transport=g_trn), core_share=dict(supercore=sh_sup, logan=sh_log, transport=sh_trn),
               sep_leaf_vs_exact=dict(leaf=sep_leaf, exact=sep_exact, error=sep_err)), open(C.OUTD / "C_q6_oct_est_diagnostics.json", "w"), indent=1)
