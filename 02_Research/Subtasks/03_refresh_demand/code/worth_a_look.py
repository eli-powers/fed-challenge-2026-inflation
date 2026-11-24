"""Context checks for unusual readings in the refreshed data (from processed observations; run from project root)."""
import pandas as pd
D = "03_Data/pipelines/demand_data/processed/"
o = pd.concat([pd.read_csv(D + g + "/observations.csv", dtype=str) for g in ("official", "research")])
o["v"] = pd.to_numeric(o.value, errors="coerce"); o["d"] = pd.to_datetime(o.date)
s = lambda k: o[o.series_key == k].dropna(subset=["v"]).set_index("d").v.sort_index()
sr = s("personal_saving_rate"); print("saving rate:", sr.iloc[-1], "; last month at or below (since 2015):", sr[sr <= sr.iloc[-1]].index[-2].strftime("%Y-%m"), "; min since 2015", sr.min(), sr.idxmin().strftime("%Y-%m"))
g = s("pce_real_goods"); print("real PCE goods last 4 (bil):", (g.iloc[-4:] / 1000).round(1).tolist())
gs = s("gasoline_stations"); print("gasoline stations sales Aug->Sep:", gs.iloc[-2], gs.iloc[-1])
dc = s("construction_private_data_center"); print("data center Aug,Sep rev:", dc.iloc[-2:].tolist(), "mom%", round((dc.iloc[-1] / dc.iloc[-2] - 1) * 100, 1))
for k in ("umich_index_of_consumer_sentiment",):
    m = s(k); print(k, m.iloc[-3:].tolist(), "lowest-ever rank file:", "see workbook")
ip = s("ai_investment_info_processing_equipment_pct_qq_saar"); print("info-proc Q/Q SAAR last 6:", ip.iloc[-6:].tolist())
cap = pd.concat([s("capex_" + c) for c in ("microsoft", "alphabet", "amazon", "meta")], axis=1).dropna().sum(axis=1)
print("hyperscaler capex last 5 (bil):", (cap.iloc[-5:] / 1000).round(1).tolist())
rc = s("revolving_consumer_credit_outstanding"); print("revolving credit last 3:", rc.iloc[-3:].tolist())
for k in ("conference_board_confidence", "conference_board_expectations"):
    x = s(k); print(k, x.iloc[-4:].tolist())
