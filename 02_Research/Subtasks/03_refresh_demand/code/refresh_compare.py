"""Compare pre-refresh (archive) vs refreshed demand_data: latest-observation table and revisions. Run from project root."""
import pandas as pd
D = "03_Data/pipelines/demand_data/"
A = D + "archive/pre_refresh_2026-11-10/processed/"
old, new = pd.read_csv(A + "demand_signals_table.csv"), pd.read_csv(D + "processed/demand_signals_table.csv")
m = old.merge(new, on="indicator", how="outer", suffixes=("_old", "_new"))
cols = ["indicator", "period_old", "latest_old", "period_new", "latest_new", "units_new", "yoy_new", "short_new", "short_label_new", "mom_new", "chg_units_new"]
print(m[cols].round(2).to_string(index=False))
print("\nSeries with unchanged latest period:", list(m[m.period_old == m.period_new].indicator))
def obs(base):
    return pd.concat([pd.read_csv(base + f"{g}/observations.csv", dtype=str) for g in ("official", "research")])
o, n = obs(A), obs(D + "processed/")
o["v"], n["v"] = pd.to_numeric(o.value, errors="coerce"), pd.to_numeric(n.value, errors="coerce")
j = o.merge(n, on=["series_key", "date"], suffixes=("_o", "_n"))
j["abs"] = j.v_n - j.v_o
j["rel"] = (j.v_n / j.v_o - 1) * 100
print("\nOverlapping obs:", len(j), "| new-only obs:", len(n.merge(o, on=["series_key", "date"], how="left", indicator=True).query("_merge=='left_only'")))
rev = j[(j["abs"].abs() > 1e-9)]
print("Revised observations (value changed):", len(rev), "of", len(j))
print("\nRevisions since 2025-01 (> 0.3% relative or > 0.1 abs for rates/indexes):")
r = rev[(rev.date >= "2025-01-01") & ((rev.rel.abs() > 0.3) | (rev.series_key.str.contains("saving|umich|conference|pct_qq")& (rev["abs"].abs() > 0.1)))]
print(r.sort_values(["series_key", "date"])[["series_key", "date", "v_o", "v_n", "abs", "rel"]].round(3).to_string(index=False))
print("\nQ2 2026 (2026-04-01) BEA investment components:")
q = j[j.date.eq("2026-04-01") & j.series_key.str.startswith("ai_investment")]
print(q[["series_key", "v_o", "v_n", "abs", "rel"]].round(3).to_string(index=False))
