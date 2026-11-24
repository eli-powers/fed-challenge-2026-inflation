"""Q3 build: extended Brent daily, quarterly averages, STEO vintages, the three oil paths, and provisional gaps.
Inputs (raw, read only): 03_Data/Raw/EIA_Brent_daily_2026-11-15/, EIA_STEO_{Nov2026,Aug2026,prewar_Jan-Feb2026}_2026-11-15/,
EIA_NYMEX_futures_2026-11-15/.
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q3_build.py"""
import sys, json, math
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *
import pandas as pd
import numpy as np
import openpyxl

D = RAW / "EIA_Brent_daily_2026-11-15"


def eia_daily(fn):
    x = pd.read_excel(D / fn, sheet_name="Data 1", header=None, skiprows=3)
    x.columns = ["date", "v"]
    x["date"] = pd.to_datetime(x["date"]).dt.strftime("%Y-%m-%d")
    return x.dropna().set_index("date")["v"].astype(float)


def fred(fn):
    j = json.loads((D / fn).read_text())
    return pd.Series({o["date"]: float(o["value"]) for o in j["observations"] if o["value"] not in (".", "")})


b_eia, w_eia = eia_daily("EIA_RBRTEd.xls"), eia_daily("EIA_RWTCd.xls")
b_fr, w_fr = fred("FRED_DCOILBRENTEU_obs.json"), fred("FRED_DCOILWTICO_obs.json")
df = pd.DataFrame({"brent_eia": b_eia, "wti_eia": w_eia}).loc["2024-01-01":]
df = df.join(pd.DataFrame({"brent_fred": b_fr, "wti_fred": w_fr}), how="outer")
df["brent_eia_minus_fred"] = (df.brent_eia - df.brent_fred).round(4)
df["brent_minus_wti_eia"] = (df.brent_eia - df.wti_eia).round(2)
df.index.name = "date"
df["source"] = "EIA RBRTE/RWTC daily spot FOB (release 2026-11-12, xls); FRED DCOILBRENTEU/DCOILWTICO (last updated 2026-11-12); $/bbl NSA"
df.to_csv(OUT / "B_q3_brent_daily.csv")
last = df.brent_eia.dropna().index.max()
mism = df[(df.brent_eia_minus_fred.abs() > 0.001)].shape[0]
print("last EIA Brent date", last, "value", df.brent_eia[last], "| EIA vs FRED mismatches since 2024:", mism,
      "| FRED-only dates:", df[df.brent_eia.isna() & df.brent_fred.notna()].index.tolist())
print("Brent-WTI spread, last:", df.brent_minus_wti_eia.dropna().iloc[-1], "; Nov 1-11 mean:",
      round(df.loc["2026-11-01":, "brent_minus_wti_eia"].mean(), 2))

# --- quarterly actual averages (simple mean of daily observations) and monthly
s = df.brent_eia.dropna()
qa = s.groupby([quarter_of(d) for d in s.index]).agg(["mean", "count"])
qa = qa.loc["2025Q1":]
mon = s.groupby([d[:7] for d in s.index]).agg(["mean", "count"]).loc["2025-01":]
print(mon.round(2).to_string())
# monthly-average-of-months quarterly (STEO convention) for comparison
mq = mon["mean"].groupby([quarter_of(m + "-01") for m in mon.index]).mean()
rows = []
for q, r in qa.iterrows():
    rows.append({"quarter": q, "brent_usd_daily_mean": round(r["mean"], 3), "brent_usd_mean_of_monthly": round(mq[q], 3),
                 "days_observed": int(r["count"]), "complete": q != "2026Q4",
                 "first_date": min(d for d in s.index if quarter_of(d) == q),
                 "last_date": max(d for d in s.index if quarter_of(d) == q),
                 "source": "EIA RBRTE daily spot FOB, $/bbl NSA, release 2026-11-12; quarterly = simple mean of trading-day observations"})
qdf = pd.DataFrame(rows)
qdf.to_csv(OUT / "B_q3_brent_quarterly.csv", index=False)
print(qdf.to_string())

# --- futures check (EIA RCLC1-4)
F = RAW / "EIA_NYMEX_futures_2026-11-15"
fut = {}
for c in range(1, 5):
    x = pd.read_excel(F / f"EIA_RCLC{c}d.xls", sheet_name="Data 1", header=None, skiprows=3).dropna()
    fut[c] = (pd.to_datetime(x.iloc[-1, 0]).strftime("%Y-%m-%d"), float(x.iloc[-1, 1]))
print("EIA RCLC last obs:", fut)


# --- STEO vintages: monthly Brent spot (BREPUUS) from 2tab
def steo(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["2tab"].iter_rows(values_only=True))
    dates = list(wb["Dates"].iter_rows(values_only=True))
    vint, completed = dates[0][3], dates[1][3]
    r = [r for r in rows if r[0] == "BREPUUS"][0]
    vals = [v for v in r[2:2 + 72]]
    months = [f"{2022 + i // 12}-{i % 12 + 1:02d}" for i in range(72)]
    m = pd.Series(vals, index=months, dtype=float)
    q = m.groupby([quarter_of(k + "-01") for k in m.index]).mean()
    return vint, str(completed)[:10], m, q


V = {}
for key, p in [("nov26", RAW / "EIA_STEO_Nov2026_2026-11-15/nov26_base.xlsx"),
               ("aug26", RAW / "EIA_STEO_Aug2026_2026-11-15/aug26_base.xlsx"),
               ("feb26", RAW / "EIA_STEO_prewar_Jan-Feb2026_2026-11-15/feb26_base.xlsx"),
               ("jan26", RAW / "EIA_STEO_prewar_Jan-Feb2026_2026-11-15/jan26_base.xlsx"),
               ("mar26", RAW / "EIA_STEO_prewar_Jan-Feb2026_2026-11-15/mar26_base.xlsx")]:
    V[key] = steo(p)
    print(key, V[key][0], "completed", V[key][1])
Q = quarters("2025Q1", "2027Q4")
steo_tab = pd.DataFrame({k: V[k][3].reindex(Q) for k in V}).round(2)
steo_tab["actual_daily_mean"] = qdf.set_index("quarter")["brent_usd_daily_mean"].reindex(Q).round(2)
steo_tab.index.name = "quarter"
steo_tab.to_csv(OUT / "B_q3_steo_vintages_quarterly.csv")
print(steo_tab.to_string())
steo_m = pd.DataFrame({k: V[k][2].loc["2025-01":"2027-12"] for k in V}).round(2)
steo_m["actual"] = mon["mean"].round(2)
steo_m.index.name = "month"
steo_m.to_csv(OUT / "B_q3_steo_vintages_monthly.csv")

# --- splice rule for 2026Q4: observed trading days + rule/forecast for the remaining weekdays of the quarter
obs4 = s.loc["2026-10-01":"2026-12-31"]
rem = pd.bdate_range(pd.Timestamp(last) + pd.Timedelta(days=1), "2026-12-31")
# EIA's Brent series has no observations on some holidays; we count weekdays and drop Thanksgiving (Nov 26) and Dec 25,
# the two US holidays in the window on which EIA's Brent series has historically had gaps (approximation; stated).
rem = [d for d in rem if d.strftime("%m-%d") not in ("11-26", "12-25")]
n_obs, n_rem = len(obs4), len(rem)
rem_months = pd.Series([d.strftime("%Y-%m") for d in rem]).value_counts().to_dict()
w_obs = n_obs / (n_obs + n_rem)
print(f"2026Q4 splice: {n_obs} observed days (Oct 1-{last}), {n_rem} remaining weekdays {rem_months}; weight observed={w_obs:.3f}")


def splice_q4(rule_by_month):
    tot = obs4.sum() + sum(rule_by_month[m] * n for m, n in rem_months.items())
    return tot / (n_obs + n_rem)


nov_m, aug_q = V["nov26"][2], V["aug26"][3]
feb_q = V["feb26"][3]
janfeb = s.loc["2026-01-01":"2026-02-27"].mean()
prewar_cut = "2026-02-27"
rows = []


def add(pid, label, variant, vid, q, val, kind, src):
    rows.append({"path_id": pid, "path_label": label, "variant": variant, "variant_id": vid, "quarter": q,
                 "brent_usd": round(float(val), 3), "kind": kind, "source": src})


HIST = [q for q in Q if q <= "2026Q3"]
FQ = quarters("2027Q1", "2027Q4")
A_SRC = "EIA RBRTE daily, quarterly mean of trading days"
paths = []
# Path 1
paths.append(("P1", "Baseline: EIA Nov-2026 STEO (completed 2026-11-05, released 2026-11-10)", "central", "P1_steo_nov26",
              {m: nov_m[m] for m in rem_months}, {q: V["nov26"][3][q] for q in FQ},
              "EIA STEO Nov 2026 2tab BREPUUS, quarterly = mean of monthly forecasts"))
# Path 1 alternative: NYMEX BZ futures curve as of the latest close (secondary [2], from B_q3_fetch_futures.py)
fc_file = OUT / "B_q3_futures_curve.csv"
if fc_file.exists():
    fc = pd.read_csv(fc_file).dropna(subset=["contract_month"])
    fdate = fc.date.iloc[0]
    fq = fc.assign(q=fc.contract_month.map(lambda m: quarter_of(m + "-01"))).groupby("q").close.mean()
    front = float(fc.sort_values("contract_month").close.iloc[0])
    paths.append(("P1", f"Baseline (market check): NYMEX Brent futures curve, closes of {fdate}", "alt", "P1_futures_" + fdate,
                  {m: front for m in rem_months}, {q: fq[q] for q in FQ},
                  f"NYMEX BZ contract closes {fdate} via Yahoo Finance [2]; quarter = mean of 3 contract months; rest of 2026Q4 at front (Jan-27) contract"))
# Path 2
paths.append(("P2", "Oil rises again: Brent $110 flat from 2026-11-12", "central", "P2_110_flat",
              {m: 110.0 for m in rem_months}, {q: 110.0 for q in FQ}, "rule: $110/bbl (Bowman, Nov 10 2026: 'up to and above $110' late Oct)"))
paths.append(("P2", "Oil rises again (harsher): Brent at Oct-2026 average flat from 2026-11-12", "alt", "P2_octavg_flat",
              {m: mon.loc["2026-10", "mean"] for m in rem_months}, {q: mon.loc["2026-10", "mean"] for q in FQ},
              f"rule: Oct 2026 EIA Brent monthly mean ${mon.loc['2026-10', 'mean']:.2f}"))
# Path 3: Feb-2026 STEO (last pre-war vintage) + premium
for prem, var in [(25, "central"), (20, "alt"), (30, "alt"), (0, "alt")]:
    paths.append(("P3", f"Hormuz reopens: pre-war trend (Feb-2026 STEO) + ${prem} premium, from 2026-11-12", var, f"P3_feb26steo_plus{prem}",
                  {m: V["feb26"][2][m] + prem for m in rem_months}, {q: feb_q[q] + prem for q in FQ},
                  f"rule: EIA STEO Feb 2026 (completed 2026-02-05) BREPUUS + ${prem}; premium per Waller Nov 10 2026 ($20-30)"))
paths.append(("P3", "Hormuz reopens (alt trend): Jan 1-Feb 27 2026 Brent average + $25, from 2026-11-12", "alt", "P3_janfebavg_plus25",
              {m: janfeb + 25 for m in rem_months}, {q: janfeb + 25 for q in FQ},
              f"rule: EIA Brent mean 2026-01-02..2026-02-27 = ${janfeb:.2f} + $25"))

for pid, label, var, vid, remrule, fq, src in paths:
    for q in HIST:
        add(pid, label, var, vid, q, qdf.set_index("quarter").loc[q, "brent_usd_daily_mean"], "actual", A_SRC)
    add(pid, label, var, vid, "2026Q4", splice_q4(remrule), "splice",
        f"{n_obs} observed days (w={w_obs:.3f}) + {n_rem} remaining weekdays (w={1 - w_obs:.3f}) at: {src}")
    for q in FQ:
        add(pid, label, var, vid, q, fq[q], "forecast" if pid == "P1" else "rule", src)
paths_df = pd.DataFrame(rows)

# --- provisional gaps vs Aug-2026 STEO quarterly path (Agent A's assumption file absent at run time)
a_file = OUT / "A_q2_oil_assumption.csv"
gap_basis = "provisional vs Aug-2026 STEO (completed 2026-08-06), quarterly mean of monthly BREPUUS"
paths_df["assumption_usd"] = np.nan
paths_df["gap_logpts_x100"] = np.nan
paths_df["gap_simple_pct"] = np.nan
for i, r in paths_df.iterrows():
    if r.quarter >= "2026Q3":
        a = aug_q[r.quarter]
        paths_df.loc[i, "assumption_usd"] = round(a, 3)
        paths_df.loc[i, "gap_logpts_x100"] = round(100 * math.log(r.brent_usd / a), 3)
        paths_df.loc[i, "gap_simple_pct"] = round(100 * (r.brent_usd / a - 1), 3)
paths_df["gap_basis"] = np.where(paths_df.quarter >= "2026Q3", gap_basis, "")
paths_df.to_csv(OUT / "B_q3_oil_paths.csv", index=False)
print("A assumption file present:", a_file.exists())
piv = paths_df[paths_df.quarter >= "2026Q3"].pivot(index="variant_id", columns="quarter", values="brent_usd").round(1)
print(piv.to_string())
print(paths_df[paths_df.quarter >= "2026Q3"].pivot(index="variant_id", columns="quarter", values="gap_logpts_x100").round(1).to_string())
print("Aug-26 STEO quarterly:", {q: round(aug_q[q], 2) for q in quarters("2026Q3", "2027Q4")})
print("Jan-Feb 2026 pre-war Brent mean:", round(janfeb, 2), "through", prewar_cut)
meta = {"last_eia_brent_date": last, "n_obs_q4": n_obs, "n_rem_q4": n_rem, "rem_months": rem_months, "w_obs": w_obs,
        "janfeb_mean": janfeb, "eia_rclc_last": fut, "steo_vintages": {k: (V[k][0], V[k][1]) for k in V}}
(OUT / "B_q3_meta.json").write_text(json.dumps(meta, indent=1, default=str))
