"""Agent D (slide 3A stress test): settle disputed points from existing, coordinator-verified outputs.

Run from the project root:
    python3 -I "02_Research/Subtasks/11_slide3a_research/code/D_q9_checks.py"

Inputs: only files already in 11_slide3a_research/outputs/ (A_, B_, C_ prefixes). No new downloads.
Output: outputs/D_q9_checks.csv (check, item, value, unit, period, input_file, note).
"""
import csv
import math
import os
import statistics as st

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "02_Research/Subtasks/11_slide3a_research/outputs")
rows = []


def add(check, item, value, unit, period, src, note=""):
    if isinstance(value, float):
        value = round(value, 3)
    rows.append(dict(check=check, item=item, value=value, unit=unit, period=period, input_file=src, note=note))


def read(name):
    with open(os.path.join(OUT, name), newline="") as f:
        return list(csv.DictReader(f))


# 1. Logan measure: is the Oct est. 3m annualised rate unusual?
f = "C_q6_logan_measure.csv"
lm = read(f)
ann3 = {r["month"]: float(r["3m_ann_pct"]) for r in lm if r["3m_ann_pct"]}
m12 = {r["month"]: float(r["12m_pct"]) for r in lm if r["12m_pct"]}
oct_est = ann3["2026-10"]
last12 = [m for m in sorted(ann3) if "2025-10" <= m <= "2026-09"]
add("logan_3m", "Oct 2026 est. 3m ann.", oct_est, "% ann.", "2026-10", f, "est.")
add("logan_3m", "Sep 2026 3m ann.", ann3["2026-09"], "% ann.", "2026-09", f)
add("logan_3m", "months in Oct25-Sep26 with 3m ann >= Oct est.", sum(ann3[m] >= oct_est for m in last12), "count of 12", "2025-10..2026-09", f)
mx = max(last12, key=lambda m: ann3[m])
add("logan_3m", "max 3m ann. Oct25-Sep26", ann3[mx], "% ann.", mx, f)
add("logan_3m", "mean 3m ann. Oct25-Sep26", st.mean(ann3[m] for m in last12), "% ann.", "2025-10..2026-09", f)
b = [m for m in sorted(ann3) if "2018-01" <= m <= "2019-12"]
add("logan_3m", "2018-19 mean 3m ann.", st.mean(ann3[m] for m in b), "% ann.", "2018-01..2019-12", f)
add("logan_3m", "2018-19 max 3m ann.", max(ann3[m] for m in b), "% ann.", "2018-01..2019-12", f)
ks = sorted(ann3)
d = {ks[i]: ann3[ks[i]] - ann3[ks[i - 1]] for i in range(1, len(ks))}
add("logan_3m", "Sep->Oct est. change in 3m ann.", d["2026-10"], "pp", "2026-10", f)
dd = [abs(d[m]) for m in d if "2024-01" <= m <= "2026-09"]
add("logan_3m", "months 2024-01..2026-09 with |monthly change in 3m ann| >= Sep->Oct change",
    sum(x >= abs(d["2026-10"]) for x in dd), f"count of {len(dd)}", "2024-01..2026-09", f)
add("logan_3m", "SD of monthly change in 3m ann., 2024-01..2026-09", st.pstdev([d[m] for m in d if "2024-01" <= m <= "2026-09"]), "pp", "2024-01..2026-09", f)
add("logan_12m", "12m Sep 2025", m12["2025-09"], "%", "2025-09", f)
add("logan_12m", "12m max Oct25-Sep26", max(m12[m] for m in last12), "%", max(last12, key=lambda m: m12[m]), f)

# 2. Expectations: pre-oil (Feb 2026) vs latest, and the 2025 tariff episode
f = "C_q4_expectations.csv"
ex = read(f)
ser = {}
for r in ex:
    try:
        ser.setdefault(r["series_id"], {})[r["period"]] = float(r["value"])
    except ValueError:
        pass
labels = {
    "PX_MD": "Michigan 1y median",
    "PX5_MD": "Michigan 5-10y median",
    "Median one-year ahead expected inflation rate": "SCE 1y median",
    "Median three-year ahead expected inflation rate": "SCE 3y median",
    "T5YIFR": "5y5y forward (monthly avg)",
    "T5YIE": "5y breakeven (monthly avg)",
    "GASREGW": "Gas regular (monthly avg of weekly)",
}
for sid, lab in labels.items():
    s = ser.get(sid, {})
    months = sorted(k for k in s if len(k) == 7)
    if not months:
        continue
    latest = months[-1]
    if "2026-02" in s:
        add("expect_preoil", f"{lab}: Feb 2026 (pre-oil-jump)", s["2026-02"], "% or $", "2026-02", f)
        add("expect_preoil", f"{lab}: latest", s[latest], "% or $", latest, f, "Michigan Nov = preliminary" if "Michigan" in lab and latest == "2026-11" else "")
        add("expect_preoil", f"{lab}: latest minus Feb 2026", s[latest] - s["2026-02"], "pp or $", f"2026-02..{latest}", f)
    y25 = [m for m in months if m.startswith("2025")]
    if y25 and sid in ("PX_MD", "PX5_MD"):
        mm = max(y25, key=lambda m: s[m])
        add("expect_2025", f"{lab}: 2025 max (tariff episode, pre-oil)", s[mm], "%", mm, f)

# 3. ULC noise
f = "B_q3_wages_ulc.csv"
w = read(f)
ulc = {r["period"]: r for r in w if r["series_id"] == "PRS85006113"}
qq = {p: float(r["mm_or_qq_ann"]) for p, r in ulc.items() if r["mm_or_qq_ann"]}
for lo, hi, lab in [("2018Q1", "2019Q4", "2018-19"), ("2024Q1", "2026Q3", "2024Q1-2026Q3")]:
    v = [qq[p] for p in sorted(qq) if lo <= p <= hi]
    add("ulc_noise", f"SD of q/q ann. ULC, {lab}", st.pstdev(v), "pp", f"{lo}..{hi}", f, f"n={len(v)}")
    add("ulc_noise", f"range of q/q ann. ULC, {lab}", f"{min(v):.2f} to {max(v):.2f}", "% ann.", f"{lo}..{hi}", f)
v8 = {p: float(r["ann8q"]) for p, r in ulc.items() if r["ann8q"]}
v4 = {p: float(r["yoy"]) for p, r in ulc.items() if r["yoy"]}
for p in ["2025Q3", "2025Q4", "2026Q1", "2026Q2", "2026Q3"]:
    add("ulc_path", f"ULC y/y / 8q ann. {p}", f"{v4[p]:.2f} / {v8[p]:.2f}", "%", p, f)

# 4. Implied nonfarm business output deflator from the identity labor share = ULC / P
ls = {r["period"]: float(r["value_level"]) for r in w if r["series_id"] == "PRS85006173" and r["value_level"]}
ul = {p: float(r["value_level"]) for p, r in ulc.items() if r["value_level"]}
for p0, p1 in [("2025Q3", "2026Q3"), ("2024Q3", "2026Q3")]:
    yrs = 1 if p0 == "2025Q3" else 2
    g_ulc = ((ul[p1] / ul[p0]) ** (1 / yrs) - 1) * 100
    g_ls = ((ls[p1] / ls[p0]) ** (1 / yrs) - 1) * 100
    g_p = (((ul[p1] / ls[p1]) / (ul[p0] / ls[p0])) ** (1 / yrs) - 1) * 100
    add("labor_share_identity", f"ULC growth {p0}->{p1}", g_ulc, "% ann.", f"{p0}..{p1}", f, "PRS85006113")
    add("labor_share_identity", f"labor share index growth {p0}->{p1}", g_ls, "% ann.", f"{p0}..{p1}", f, "PRS85006173")
    add("labor_share_identity", f"implied output deflator growth (ULC/LS) {p0}->{p1}", g_p, "% ann.", f"{p0}..{p1}", f,
        "derived from identity, not the published BLS IPD (PRS85006143 not pulled); nonfarm business incl. oil and gas extraction")

# 5. Wage measure minus benchmark matrix
f = "B_q3_summary.csv"
s = read(f)
def pick(sid, measure_exact):
    for r in s:
        if r["series_id"] == sid and r["measure"] == measure_exact:
            return float(r["latest"]), r["latest_period"]
    raise KeyError((sid, measure_sub))
measures = {
    "ECI W&S private y/y (SA idx)": ("CIS2020000000000I", "y/y"),
    "ECI W&S private 8q ann.": ("CIS2020000000000I", "8q annualised"),
    "ECI total comp private y/y": ("CIS2010000000000I", "y/y"),
    "AHE all private y/y": ("CES0500000003", "y/y"),
    "AHE all private 3m ann.": ("CES0500000003", "3m annualised"),
    "WGT overall 3mma": ("WGT_overall_3mma", "level"),
    "Hourly comp NFB y/y": ("PRS85006103", "y/y"),
    "Hourly comp NFB 8q ann.": ("PRS85006103", "8q annualised"),
}
benches = {"2010-19 trend (3.16)": 3.16, "2007Q4-19Q4 central (3.52)": 3.52, "2020-25 trend (4.21)": 4.21}
for lab, (sid, sub) in measures.items():
    try:
        val, per = pick(sid, sub)
    except KeyError:
        add("wage_vs_bench", lab, "not found", "", "", f, f"measure substring '{sub}' not matched")
        continue
    add("wage_vs_bench", lab, val, "%", per, f)
    for bl, bv in benches.items():
        add("wage_vs_bench", f"{lab} minus {bl}", val - bv, "pp", per, f + " ; B_q3_benchmark.csv")

# 6. Real wage: ECI W&S 12m vs headline PCE 12m, Sep 2026 / Q3
eci, _ = pick("CIS2020000000000I", "y/y")
# headline PCE Sep 12m is not a column; take it from C_q8_time_above_target.csv
tat = read("C_q8_time_above_target.csv")
pce_sep = {r["month"]: float(r["pce_12m"]) for r in tat if r["pce_12m"]}.get("2026-09")
add("real_wage", "headline PCE 12m Sep 2026", pce_sep, "%", "2026-09", "C_q8_time_above_target.csv")
if pce_sep is not None:
    add("real_wage", "ECI W&S y/y minus headline PCE 12m (Sep)", eci - pce_sep, "pp", "2026Q3 vs 2026-09", "B_q3_summary.csv ; C_q8_time_above_target.csv")
else:
    add("real_wage", "headline PCE Sep 12m", "not parsed", "", "", "C_q8_time_above_target.csv", "see columns")

# 7. V/U direction
f = "A_q1_vu.csv"
vu = {r["month"]: float(r["vu"]) for r in read(f) if r["vu"]}
add("vu", "V/U Dec 2025", vu["2025-12"], "ratio", "2025-12", f)
add("vu", "V/U Sep 2026", vu["2026-09"], "ratio", "2026-09", f)
add("vu", "change Dec 2025 -> Sep 2026", vu["2026-09"] - vu["2025-12"], "ratio", "2025-12..2026-09", f)
add("vu", "2018-19 mean", st.mean(v for m, v in vu.items() if "2018" <= m[:4] <= "2019"), "ratio", "2018-01..2019-12", f)

with open(os.path.join(OUT, "D_q9_checks.csv"), "w", newline="") as fo:
    wr = csv.DictWriter(fo, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)
print(f"wrote {len(rows)} rows")
for r in rows:
    print(r["check"], "|", r["item"], "|", r["value"], "|", r["period"])
