"""Compute V/U = JOLTS openings (JTSJOL, thousands, SA) / unemployed level (UNEMPLOY, thousands, SA), monthly,
2018-01 to latest, plus UNRATE. Cross-checks FRED against BLS API. Run from project root with python3 -I."""
import json, csv
from pathlib import Path
ROOT = Path.cwd()
RAW = ROOT / "03_Data/Raw/S3A_A_vu_2026-11-15"
OUT = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs"
def fred(sid):
    d = json.loads((RAW / f"FRED_{sid}_observations_2026-11-15.json").read_text())
    return {o["date"][:7]: (float(o["value"]) if o["value"] not in (".", "") else None) for o in d["observations"]}
J, U, R = fred("JTSJOL"), fred("UNEMPLOY"), fred("UNRATE")
b = json.loads((RAW / "BLS_API_JOL_LNS13000000_LNS14000000_2018_2026_2026-11-15.json").read_text())
bls = {}
for s in b["Results"]["series"]:
    bls[s["seriesID"]] = {f'{x["year"]}-{x["period"][1:]}': (float(x["value"]) if x["value"].replace(".", "").isdigit() else None) for x in s["data"]}
months = sorted(m for m in set(J) | set(U) | set(R) if m >= "2018-01")
rows, mism = [], []
for m in months:
    j, u, r = J.get(m), U.get(m), R.get(m)
    for sid, fv, bid in [("JTSJOL", j, "JTS000000000000000JOL"), ("UNEMPLOY", u, "LNS13000000"), ("UNRATE", r, "LNS14000000")]:
        bv = bls[bid].get(m)
        if fv != bv: mism.append((m, sid, fv, bv))
    vu = round(j / u, 4) if (j is not None and u is not None) else None
    rows.append({"month": m, "openings_thous_JTSJOL": j, "unemployed_thous_UNEMPLOY": u, "vu": vu, "unrate_pct_UNRATE": r,
                 "note": "" if vu is not None else "missing input (see notes)"})
with open(OUT / "A_q1_vu.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
valid = [r for r in rows if r["vu"] is not None]
w2123 = [r for r in valid if "2021-01" <= r["month"] <= "2023-12"]
pk = max(w2123, key=lambda r: r["vu"])
pre = [r["vu"] for r in valid if "2018-01" <= r["month"] <= "2019-12"]
pre_u = [r["unrate_pct_UNRATE"] for r in rows if "2018-01" <= r["month"] <= "2019-12"]
last = valid[-1]
q4_2019 = [r["vu"] for r in valid if r["month"] in ("2019-10", "2019-11", "2019-12")]
# 2021-22 trough of UNRATE, 2023 low
u2123 = [r for r in rows if "2021-01" <= r["month"] <= "2023-12" and r["unrate_pct_UNRATE"] is not None]
umin = min(u2123, key=lambda r: (r["unrate_pct_UNRATE"], r["month"]))
last12 = [r for r in valid][-12:]
summ = {
 "vu_peak_2021_23": (pk["month"], pk["vu"]),
 "vu_avg_2018_19": round(sum(pre) / len(pre), 4),
 "vu_avg_2019Q4": round(sum(q4_2019) / 3, 4),
 "vu_latest": (last["month"], last["vu"]),
 "vu_3m_avg_latest": round(sum(r["vu"] for r in valid[-3:]) / 3, 4),
 "vu_min_last_12m": min((r["vu"], r["month"]) for r in last12),
 "vu_max_last_12m": max((r["vu"], r["month"]) for r in last12),
 "unrate_latest": (rows[-1]["month"], rows[-1]["unrate_pct_UNRATE"]),
 "unrate_avg_2018_19": round(sum(pre_u) / len(pre_u), 3),
 "unrate_min_2021_23": (umin["month"], umin["unrate_pct_UNRATE"]),
 "unrate_at_vu_peak": R.get(pk["month"]),
 "missing_months": [(r["month"], r["openings_thous_JTSJOL"], r["unemployed_thous_UNEMPLOY"], r["unrate_pct_UNRATE"]) for r in rows if None in (r["openings_thous_JTSJOL"], r["unemployed_thous_UNEMPLOY"], r["unrate_pct_UNRATE"])],
 "fred_vs_bls_mismatches": mism,
 "last_12m_vu": [(r["month"], r["vu"]) for r in last12],
}
for k, v in summ.items(): print(k, v)
(OUT / "A_q1_vu_summary.json").write_text(json.dumps(summ, indent=1))
# Quarterly average V/U (BB use quarterly data; their fn 15 range 0.26-1.91 for 2020Q1-2023Q1)
from collections import defaultdict
qd = defaultdict(list)
for r in valid:
    y, mm = r["month"].split("-"); qd[f"{y}Q{(int(mm)-1)//3+1}"].append(r["vu"])
qavg = {q: round(sum(v) / len(v), 4) for q, v in qd.items()}
qn = {q: len(v) for q, v in qd.items()}
bbwin = {q: v for q, v in qavg.items() if "2020Q1" <= q <= "2023Q1"}
print("quarterly 2020Q1-2023Q1 min/max:", min(bbwin.items(), key=lambda x: x[1]), max(bbwin.items(), key=lambda x: x[1]))
print("2019Q4:", qavg["2019Q4"], " 2023Q1:", qavg["2023Q1"], " latest quarters:", [(q, qavg[q], qn[q]) for q in sorted(qavg)[-5:]])
summ["quarterly_vu"] = {q: (qavg[q], qn[q]) for q in sorted(qavg)}
(OUT / "A_q1_vu_summary.json").write_text(json.dumps(summ, indent=1))
