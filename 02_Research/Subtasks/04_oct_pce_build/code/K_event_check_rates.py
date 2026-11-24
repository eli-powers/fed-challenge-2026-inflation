"""Coordinator script (Checkpoint C item 4). Event check: do the two 'financial services furnished
without payment' leaves (BEA lines 255 commercial banks, 256 other depository institutions and regulated
investment companies) move differently in months around a federal funds target change?
Run from the project root: python3 "02_Research/Subtasks/04_oct_pce_build/code/K_event_check_rates.py"
Inputs (saved, never edited):
  03_Data/Raw/FRED_DFEDTARU_2026-11-12.json  (fed funds target range, upper limit, daily)
  03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json (SA price indexes)
Output: 02_Research/Subtasks/04_oct_pce_build/outputs/K_event_check_rates.csv (+ _meta.csv)
Window: Jan 2017 - Sep 2026, current vintage. Event month = month of a target change; also month + 1.
"""
import json, pandas as pd, numpy as np
SUB = "02_Research/Subtasks/04_oct_pce_build/"
o = [x for x in json.load(open("03_Data/Raw/FRED_DFEDTARU_2026-11-12.json"))["observations"] if x["value"] != "."]
d = pd.Series({x["date"]: float(x["value"]) for x in o}); ch = d.diff().dropna(); ch = ch[ch != 0]
ev = pd.DataFrame({"date": ch.index, "chg": ch.values}); ev["ym"] = ev.date.str[:7]
evm = ev.groupby("ym").chg.sum()

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
rows = []
for line, name in [("255", "Commercial banks"), ("256", "Other depository institutions and regulated investment companies")]:
    s = u[u.LineNumber == line].copy(); s["ym"] = s.TimePeriod.str.replace("M", "-")
    p = s.set_index("ym").DataValue.astype(float).sort_index(); mm = (p / p.shift(1) - 1) * 100
    mm = mm[(mm.index >= "2017-01") & (mm.index <= "2026-09")]
    idx = list(mm.index)
    e0 = [m for m in idx if m in evm.index]
    e1 = [idx[i + 1] for i, m in enumerate(idx[:-1]) if m in evm.index]
    for label, months in [("month of a target change", e0), ("month after a target change", e1),
                          ("month of or after a change", sorted(set(e0) | set(e1))),
                          ("all other months", [m for m in idx if m not in set(e0) | set(e1)]), ("all months", idx)]:
        x = mm[months]
        rows.append(dict(line=line, name=name, group=label, n=len(x), mean_mm=round(x.mean(), 4), sd_mm=round(x.std(ddof=1), 4),
                         mean_abs_mm=round(x.abs().mean(), 4), min_mm=round(x.min(), 4), max_mm=round(x.max(), 4)))
    # signed response: correlation of m/m with the size of the change in event months and the month after
    for lag, months in [(0, e0), (1, e1)]:
        chg = [evm[idx[idx.index(m) - lag]] for m in months]
        rows.append(dict(line=line, name=name, group=f"corr(m/m, rate change in pp), lag {lag}", n=len(months),
                         mean_mm=round(float(np.corrcoef(chg, mm[months])[0, 1]), 4)))
    for m in ["2026-08", "2026-09"]:
        rows.append(dict(line=line, name=name, group=f"m/m in {m} (target raised 2026-09-17)", n=1, mean_mm=round(mm[m], 4)))
out = pd.DataFrame(rows); out.to_csv(SUB + "outputs/K_event_check_rates.csv", index=False)
pd.DataFrame([["file", "K_event_check_rates.csv"], ["script", "code/K_event_check_rates.py"],
              ["series", "BEA U20404 lines 255, 256 (SA price index, m/m %); FRED DFEDTARU"],
              ["window", "2017-01 to 2026-09"], ["vintage", "U20404 2026-11-10; DFEDTARU retrieved 2026-11-12"],
              ["event months", ";".join(evm[evm.index >= "2017-01"].index)]], columns=["field", "value"]).to_csv(SUB + "outputs/K_event_check_rates_meta.csv", index=False)
pd.set_option("display.width", 220); print(out.to_string())
