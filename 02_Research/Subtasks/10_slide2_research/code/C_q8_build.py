"""Q8 build: PPI intermediate-demand stages, commodity-type series and final demand.
Inputs (read only): 03_Data/Raw/BLS_PPI_stages_2026-11-15/ (BLS API v2 JSON, wp series list, relative-importance xlsx),
                    03_Data/Raw/EIA_FRED_oil_daily_2026-11-15/, pipeline Nov-10 vintage raw JSON (revision check).
Outputs: outputs/C_q8_ppi_stages.csv, C_q8_ppi_stages_summary.csv, C_q8_oil_daily.csv, C_q8_oil_drop_summary.csv,
         C_q8_energy_contributions.csv, C_q8_vintage_revisions.csv, C_q8_label_check.csv, C_q8_nsa_yoy_check.csv
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q8_build.py   (from the project root)
Definitions: mm = 100*(I_t/I_{t-1}-1); ann3m = 100*((I_t/I_{t-3})^4-1); yoy = 100*(I_t/I_{t-12}-1) on the SA index.
"""
import sys, glob, json, re
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
import pandas as pd, numpy as np, openpyxl

OUT.mkdir(exist_ok=True, parents=True)
SRC = RAW / "BLS_PPI_stages_2026-11-15"
START = "2018-01"

# ---------- titles ----------
wp = [[x.strip() for x in l.split("\t")] for l in (SRC / "bls_wp_series_2026-09-27_copy.txt").read_text().splitlines()]
title_full = {r[0]: r[5] for r in wp[1:]}


def clean(t):
    t = t.replace("PPI Commodity data for ", "").replace(", seasonally adjusted", "").replace(", not seasonally adjusted", "")
    return t


def family(sid):
    if sid.startswith(("WPSID5", "WPUID5")):
        return "intermediate_demand_by_production_flow"
    if sid.startswith(("WPSID6", "WPUID6")):
        return "intermediate_demand_by_commodity_type"
    return "final_demand"


# ---------- load raw ----------
def load_json(pattern):
    d = {}
    for f in sorted(glob.glob(str(pattern))):
        j = json.load(open(f))
        for s in j["Results"]["series"]:
            d[s["seriesID"]] = {(int(o["year"]), int(o["period"][1:])): (float(o["value"]), ",".join(x.get("code", "") for x in o.get("footnotes", []) if x))
                                for o in s["data"] if o["period"].startswith("M") and o["period"] != "M13" and o["value"] not in ("-", "")}
    return d


sa = load_json(SRC / "bls_api_ppi_stages_2017_2026_batch*_2026-11-15.json")
nsa = load_json(SRC / "bls_api_ppi_nsa_check_2017_2026_batch*_2026-11-15.json")


def frame(d):
    rows = []
    for sid, m in d.items():
        for (y, mo), (v, fn) in m.items():
            rows.append((sid, pd.Period(f"{y}-{mo:02d}", "M"), v, fn))
    return pd.DataFrame(rows, columns=["series_id", "month", "index", "fn"]).sort_values(["series_id", "month"])


df = frame(sa)
g = df.groupby("series_id")["index"]
df["mm"] = (df["index"] / g.shift(1) - 1) * 100
df["ann3m"] = ((df["index"] / g.shift(3)) ** 4 - 1) * 100
df["yoy"] = (df["index"] / g.shift(12) - 1) * 100
# month continuity check (shift assumes no gaps)
gaps = df.groupby("series_id")["month"].apply(lambda s: (s.diff().dropna().map(lambda x: x.n) != 1).sum())
assert gaps.sum() == 0, gaps[gaps > 0]
df["status"] = np.where(df["fn"].str.contains("P"), "preliminary (P)", "final")
df["title"] = df["series_id"].map(lambda s: clean(title_full[s]))
df["family"] = df["series_id"].map(family)
df["seasonal"] = "SA"
long = df[df["month"] >= pd.Period(START, "M")].copy()
long["month"] = long["month"].astype(str)
long[["series_id", "title", "month", "index", "mm", "ann3m", "yoy", "status", "family", "seasonal"]].round(4).to_csv(OUT / "C_q8_ppi_stages.csv", index=False)

# ---------- label check ----------
focus = ["WPSID51", "WPSID52", "WPSID53", "WPSID54", "WPSFD4", "WPSID61", "WPSID62", "WPSID63", "WPSID64",
         "WPSID511", "WPSID512", "WPSID513", "WPSID521", "WPSID522",
         "WPSID59115", "WPSID59215", "WPSID59315", "WPSID59415", "WPSID59111", "WPSID59112", "WPSID59211", "WPSID59212",
         "WPSID6222", "WPSID622", "WPSID69113", "WPSID69212", "WPSID613"]
lab = pd.DataFrame({"series_id": focus, "bls_title_full": [title_full[s] for s in focus]})
lab["family"] = lab.series_id.map(family)
lab["note"] = lab.series_id.map(lambda s: {
    "WPSID51": "STAGE 1 (production flow)", "WPSID52": "STAGE 2 (production flow)", "WPSID53": "STAGE 3 (production flow)", "WPSID54": "STAGE 4 (production flow)",
    "WPSID61": "COMMODITY-TYPE: processed goods for intermediate demand (NOT stage 1)",
    "WPSID62": "COMMODITY-TYPE: UNPROCESSED goods for intermediate demand (NOT stage 2; not 'processed')",
    "WPSID63": "COMMODITY-TYPE: services for intermediate demand (NOT stage 3)",
    "WPSID64": "COMMODITY-TYPE: construction for intermediate demand (NOT stage 4)"}.get(s, ""))
lab.to_csv(OUT / "C_q8_label_check.csv", index=False)

# ---------- summary: latest readings, ranks, last-time-this-high ----------
win = df[df["month"] >= pd.Period(START, "M")]
LAST, PREV = pd.Period("2026-10", "M"), pd.Period("2026-09", "M")
rows = []
for sid, sub in win.groupby("series_id"):
    sub = sub.set_index("month")
    if LAST not in sub.index or PREV not in sub.index:
        continue
    r = {"series_id": sid, "title": clean(title_full[sid]), "family": family(sid), "focus": 0, "index_Oct26": sub.loc[LAST, "index"], "index_Sep26": sub.loc[PREV, "index"], "index_Aug26": sub.loc[LAST - 2, "index"],
         "vintage": "BLS API v2 pulled 2026-11-15 (Oct 2026 PPI release of 2026-11-13); SA; Jul-Oct 2026 preliminary"}
    for met in ["mm", "ann3m", "yoy"]:
        s = sub[met].dropna()
        for lab_, p in [("Oct26", LAST), ("Sep26", PREV)]:
            v = s.loc[p]
            r[f"{met}_{lab_}"] = v
        v = s.loc[LAST]
        r[f"{met}_Oct26_rank_desc"] = int((s > v).sum() + 1)
        r[f"{met}_n_months"] = len(s)
        prior = s[(s.index < LAST) & (s >= v)]
        r[f"{met}_Oct26_last_time_ge"] = str(prior.index.max()) if len(prior) else "never since 2018-01"
        v2 = s.loc[PREV]
        r[f"{met}_Sep26_rank_desc"] = int((s > v2).sum() + 1)
        prior2 = s[(s.index < PREV) & (s >= v2)]
        r[f"{met}_Sep26_last_time_ge"] = str(prior2.index.max()) if len(prior2) else "never since 2018-01"
        r[f"{met}_peak"] = s.max(); r[f"{met}_peak_month"] = str(s.idxmax())
    r["mm_Oct_minus_Sep"] = r["mm_Oct26"] - r["mm_Sep26"]
    r["ann3m_Oct_minus_Sep"] = r["ann3m_Oct26"] - r["ann3m_Sep26"]
    rows.append(r)
summ = pd.DataFrame(rows)
summ["focus"] = summ["series_id"].isin(focus).astype(int)
summ = summ.sort_values(["focus", "family", "series_id"], ascending=[False, True, True])
summ.round(4).to_csv(OUT / "C_q8_ppi_stages_summary.csv", index=False)

# ---------- NSA y/y check vs BLS release ----------
nd = frame(nsa)
nd["yoy_nsa"] = (nd["index"] / nd.groupby("series_id")["index"].shift(12) - 1) * 100
chk = nd[nd.month == LAST][["series_id", "index", "yoy_nsa"]].copy()
chk["sa_series"] = chk.series_id.str.replace("WPU", "WPS")
chk["yoy_sa_calc"] = chk.sa_series.map(lambda s: summ.set_index("series_id").loc[s, "yoy_Oct26"])
pub = {"WPUID51": 13.9, "WPUID52": 13.3, "WPUID53": 8.4, "WPUID54": 8.0, "WPUFD4": 6.5, "WPUID61": 14.6, "WPUID62": 16.9}
chk["bls_release_12m_pct_Oct26"] = chk.series_id.map(pub)
chk["source_of_published"] = "BLS PPI news release USDL 26-1687 (2026-11-13), text and Table B/D paragraphs: https://www.bls.gov/news.release/ppi.nr0.htm"
chk.round(3).to_csv(OUT / "C_q8_nsa_yoy_check.csv", index=False)

# ---------- vintage comparison: Nov 10 (Sep release, first print) vs Nov 15 ----------
old = load_json(ROOT / "03_Data/pipelines/Price indexes/PPI/raw/bls_api_ppi_baskets_2017_2026_batch*_2026-11-10.json")
rev = []
for sid, m in old.items():
    if sid in sa:
        for k in [(2026, 6), (2026, 7), (2026, 8), (2026, 9)]:
            if k in m and k in sa[sid]:
                o, n = m[k][0], sa[sid][k][0]
                rev.append({"series_id": sid, "title": clean(title_full[sid]), "month": f"{k[0]}-{k[1]:02d}", "index_vintage_2026-11-10": o,
                            "index_vintage_2026-11-15": n, "revision_pct": (n / o - 1) * 100})
rev = pd.DataFrame(rev)
rev["abs_rev"] = rev.revision_pct.abs()
rev = rev.sort_values("abs_rev", ascending=False).drop(columns="abs_rev")
rev["note"] = ("Nov-10 vintage = pipeline raw (BLS API retrieved 2026-11-10 after the Sep release); Nov-15 vintage = this pull. "
               "BLS release footnote: data for June through September revised for late reports and corrections by respondents.")
rev.round(4).to_csv(OUT / "C_q8_vintage_revisions.csv", index=False)

# ---------- energy contributions to stage 1-4 (relative importance, chain-updated shares) ----------
ri_path = SRC / "bls_ppi_id_production_flow_relative_importance_2026_2026-11-15.xlsx"
ws = openpyxl.load_workbook(ri_path, read_only=True).active
ri = {}
for r in list(ws.iter_rows(values_only=True))[4900:]:
    if r[1] and str(r[1]).strip().startswith("ID59"):
        ri[str(r[1]).strip()] = (r[4], r[5])
comp_suffix = {"goods": "1", "services": "2", "foods": "4", "energy": "5", "goods_ex_food_energy": "6", "construction": "7"}
# RI Dec 2024 weights apply to 2025 data, Dec 2025 weights to 2026 data (BLS: reflects sample revisions effective Jan of the following year)
idx = df.pivot(index="month", columns="series_id", values="index")
contrib_rows = []
for stage in [1, 2, 3, 4]:
    stage_id = f"WPSID5{stage}"
    parts = {k: f"WPSID59{stage}1{v}" for k, v in comp_suffix.items() if k not in ("goods",)}
    for k, sid in list(parts.items()):
        if f"ID59{stage}1{comp_suffix[k]}" not in ri:
            parts.pop(k)
    for per in pd.period_range("2025-02", "2026-10", freq="M"):
        w_col = 0 if per.year == 2025 else 1
        base = pd.Period(f"{per.year - 1}-12", "M")
        tot = 0.0
        row = {"stage": stage, "month": str(per), "weights_used": "Dec 2024 RI" if w_col == 0 else "Dec 2025 RI"}
        stage_mm = (idx.loc[per, stage_id] / idx.loc[per - 1, stage_id] - 1) * 100
        for k, sid in parts.items():
            w = float(ri[sid.replace("WPS", "")][w_col])
            # share at t-1 = RI(Dec base) * (comp_{t-1}/comp_base) / (stage_{t-1}/stage_base)
            share = w * (idx.loc[per - 1, sid] / idx.loc[base, sid]) / (idx.loc[per - 1, stage_id] / idx.loc[base, stage_id]) / 100
            cm = (idx.loc[per, sid] / idx.loc[per - 1, sid] - 1) * 100
            row[f"contrib_{k}_pp"] = share * cm
            row[f"share_{k}_pct"] = share * 100
            tot += share * cm
        row["stage_mm_pct"] = stage_mm
        row["sum_of_contribs_pp"] = tot
        row["residual_pp"] = stage_mm - tot
        contrib_rows.append(row)
ec = pd.DataFrame(contrib_rows)
ec.round(4).to_csv(OUT / "C_q8_energy_contributions.csv", index=False)

# cumulative sums for the key windows
def window_sum(stage, start, end):
    s = ec[(ec.stage == stage) & (ec.month >= start) & (ec.month <= end)]
    cols = [c for c in s.columns if c.startswith("contrib_") or c in ("stage_mm_pct", "sum_of_contribs_pp", "residual_pp")]
    return s[cols].sum()


wins = {"Aug-Oct 2026 (3m)": ("2026-08", "2026-10"), "Jul-Sep 2026 (3m)": ("2026-07", "2026-09"), "Nov25-Oct26 (12m)": ("2025-11", "2026-10"), "Sep 2026": ("2026-09", "2026-09"), "Oct 2026": ("2026-10", "2026-10")}
wrows = []
for stage in [1, 2, 3, 4]:
    for wn, (a, b) in wins.items():
        s = window_sum(stage, a, b)
        d = {"stage": stage, "window": wn, "note": "sum of monthly contributions (pp), simple not compounded; weights chain-updated from BLS Dec RI"}
        d.update(s.round(3).to_dict())
        e = s.get("contrib_energy_pp", np.nan); t = s["sum_of_contribs_pp"]
        d["energy_share_of_stage_change_pct"] = round(100 * e / t, 1) if abs(t) > 1e-9 else np.nan
        wrows.append(d)
pd.DataFrame(wrows).to_csv(OUT / "C_q8_energy_contributions_windows.csv", index=False)

# ---------- oil ----------
O = RAW / "EIA_FRED_oil_daily_2026-11-15"


def eia(f, name):
    d = pd.read_excel(O / f, sheet_name="Data 1", header=None, skiprows=3)
    d.columns = ["date", name]
    d["date"] = pd.to_datetime(d["date"]); return d.set_index("date")[name]


def fred(f, name):
    j = json.load(open(O / f))
    return pd.Series({pd.Timestamp(o["date"]): (float(o["value"]) if o["value"] != "." else np.nan) for o in j["observations"]}, name=name)


br_e, wt_e = eia("EIA_RBRTEd_2026-11-15.xls", "brent_eia"), eia("EIA_RWTCd_2026-11-15.xls", "wti_eia")
br_f, wt_f = fred("FRED_DCOILBRENTEU_obs_2026-11-15.json", "brent_fred"), fred("FRED_DCOILWTICO_obs_2026-11-15.json", "wti_fred")
oil = pd.concat([br_e, wt_e, br_f, wt_f], axis=1)
oil = oil[oil.index >= "2018-01-01"]
oil["brent_usd_bbl"] = oil["brent_eia"]; oil["wti_usd_bbl"] = oil["wti_eia"]
oil["brent_eia_minus_fred"] = oil["brent_eia"] - oil["brent_fred"]; oil["wti_eia_minus_fred"] = oil["wti_eia"] - oil["wti_fred"]
oil["brent_dod_pct"] = oil["brent_usd_bbl"].pct_change() * 100
oil["wti_dod_pct"] = oil["wti_usd_bbl"].pct_change() * 100
oil["brent_minus_wti"] = oil["brent_usd_bbl"] - oil["wti_usd_bbl"]
oil["source"] = "EIA spot prices RBRTE / RWTC (daily, FOB); FRED mirrors DCOILBRENTEU / DCOILWTICO; EIA last data 2026-11-11"
oil.index.name = "date"
oil.round(3).to_csv(OUT / "C_q8_oil_daily.csv")
print("oil EIA vs FRED max abs diff:", oil[["brent_eia_minus_fred", "wti_eia_minus_fred"]].abs().max().to_dict())

o = oil[oil.index >= "2026-09-01"]
ev = []
for name, col in [("Brent", "brent_usd_bbl"), ("WTI", "wti_usd_bbl")]:
    s = oil[col].dropna()
    s26 = s[s.index >= "2026-01-01"]
    pk = s26.loc["2026-09-01":"2026-11-11"]
    peak_d = pk.idxmax(); peak = pk.max()
    after = s.loc[peak_d:]
    low_d = after.idxmin(); low = after.min()
    dod = s.pct_change() * 100
    big = dod.loc["2026-10-20":].nsmallest(3)
    ev.append({"series": name, "peak_date_since_Sep1": str(peak_d.date()), "peak_usd": peak, "trough_date_to_Nov11": str(low_d.date()), "trough_usd": low,
               "peak_to_trough_pct": (low / peak - 1) * 100,
               "last_obs_date": str(s.index[-1].date()), "last_usd": s.iloc[-1],
               "last_vs_peak_pct": (s.iloc[-1] / peak - 1) * 100,
               "close_Oct13": s.loc["2026-10-13"], "close_Oct30": s.loc["2026-10-30"], "close_Nov02": s.loc["2026-11-02"], "close_Nov03": s.loc["2026-11-03"], "close_Nov04": s.loc["2026-11-04"],
               "Nov03_to_Nov04_pct": (s.loc["2026-11-04"] / s.loc["2026-11-03"] - 1) * 100,
               "Oct30_to_Nov04_pct": (s.loc["2026-11-04"] / s.loc["2026-10-30"] - 1) * 100,
               "Oct13_to_Nov04_pct": (s.loc["2026-11-04"] / s.loc["2026-10-13"] - 1) * 100,
               "Oct13_to_last_pct": (s.iloc[-1] / s.loc["2026-10-13"] - 1) * 100,
               "largest_1day_drops_since_Oct20": "; ".join(f"{d.date()}: {v:.1f}%" for d, v in big.items()),
               "monthly_avg_Sep26": s.loc["2026-09"].mean(), "monthly_avg_Oct26": s.loc["2026-10"].mean(), "avg_Nov1_to_Nov11": s.loc["2026-11-01":"2026-11-11"].mean(),
               "source": "EIA RBRTE/RWTC daily spot; FRED DCOILBRENTEU/DCOILWTICO"})
pd.DataFrame(ev).round(3).to_csv(OUT / "C_q8_oil_drop_summary.csv", index=False)
# also the full Oct-Nov window print
print(oil.loc["2026-10-01":, ["brent_usd_bbl", "wti_usd_bbl", "brent_dod_pct", "wti_dod_pct"]].round(2).to_string())
print(pd.DataFrame(ev).T.to_string())
print("wrote outputs; series in long:", long.series_id.nunique(), "rows", len(long))
