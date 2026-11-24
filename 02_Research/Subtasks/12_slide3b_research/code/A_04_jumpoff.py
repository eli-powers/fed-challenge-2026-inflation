"""A_04_jumpoff: Q1.6. Actual core PCE (PCEPILFE) quarterly data vs SPF jump-off; calculations (not forecasts).
python3 -I 02_Research/Subtasks/12_slide3b_research/code/A_04_jumpoff.py [spf_raw_dir]
Quarterly = average of three monthly index levels (same construction as SPF documentation). q/q annualized =
((Q_t/Q_{t-1})^4-1)*100; Q4/Q4 = Q4_t/Q4_{t-1}-1."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import A_common as C

OCT_MM = 0.295  # project Oct 2026 core m/m estimate (%), Slide1_Inflation_Data.xlsx Headline!C6 (brief: 0.295)
OCT_YY_STATED = 3.24  # Slide1_Inflation_Data.xlsx Headline!C10 (brief)
raw = Path(sys.argv[1]) if len(sys.argv) > 1 else C.RAW / "PhilFed_SPF_2026Q3_2026-11-15"
fred = C.RAW / "FRED_PCEPILFE_latest_2026-11-15/PCEPILFE_observations.json"
alf = C.RAW / "ALFRED_PCEPILFE_all_vintages_2026-11-11.json"  # existing project file, read-only

med = C.read_spf_median(raw / "medianLevel.xlsx")
Y, Q = C.detect_survey(med)
row = C.median_row(med, Y, Q)
hm = C.horizon_map(Y, Q)
spf = {hm[v][0]: row[v] for v in C.SPF_Q_VARS}  # target quarter -> annualized q/q
annA = row["COREPCEA"]
surv = f"{Y}Q{Q}"
dl = C.parse_release_dates(raw / "spf-release-dates.txt", Y, Q)
deadline = pd.to_datetime(dl[0], format="%m/%d/%y").date().isoformat() if dl else None

m = C.load_fred_obs(fred)
vint_fred = "FRED PCEPILFE, realtime 2026-10-29 (BEA release of Sep 2026 PCE)"
qa = C.quarterly_avg(m)
qq = C.qq_annualized(qa)
yy = C.q4q4_series(qa)
rec = []


def add(section, item, value, unit, note, source):
    rec.append(dict(section=section, item=item, value=None if value is None or pd.isna(value) else round(float(value), 4),
                    unit=unit, note=note, source=source))


for lab in qa.index[-9:]:
    add("actual_quarterly_latest_vintage", f"{lab} avg index (2017=100)", qa[lab], "index", "quarterly avg of monthly SA index", vint_fred)
    add("actual_quarterly_latest_vintage", f"{lab} q/q annualized", qq[lab], "% ann., SA", "calc from quarterly averages", vint_fred)
    if lab.endswith("Q4"):
        add("actual_quarterly_latest_vintage", f"{lab} Q4/Q4", yy[lab], "%", "calc", vint_fred)
for lab in ["2025Q4", "2026Q1", "2026Q2", "2026Q3"]:
    add("actual_quarterly_latest_vintage", f"{lab} y/y (quarterly avg)", yy[lab], "%", "calc, quarterly avg over same quarter a year earlier", vint_fred)

# as known on SPF deadline (ALFRED vintage)
if deadline:
    mv = C.load_alfred_vintage(alf, deadline)
    qv = C.quarterly_avg(mv)
    qqv, yyv = C.qq_annualized(qv), C.q4q4_series(qv)
    src_v = f"ALFRED PCEPILFE vintage in force on {deadline} (file ALFRED_PCEPILFE_all_vintages_2026-11-11.json)"
    for lab in qv.index[-6:]:
        add("actual_quarterly_as_of_spf_deadline", f"{lab} q/q annualized", qqv[lab], "% ann., SA", "calc; vintage known to forecasters", src_v)
    add("actual_quarterly_as_of_spf_deadline", "2025Q4 Q4/Q4", yyv["2025Q4"], "%", "calc; SPF PDF shows 2.9 'actual' for 2025", src_v)
    # revision of 2026Q2 q/q between vintages
    add("actual_quarterly_vintage_revision", "2026Q2 q/q ann.: latest minus as-of-deadline", qq["2026Q2"] - qqv["2026Q2"], "pp", "calc", "both vintages above")
    add("actual_quarterly_vintage_revision", "2026Q1 q/q ann.: latest minus as-of-deadline", qq["2026Q1"] - qqv["2026Q1"], "pp", "calc", "both vintages above")
    add("actual_quarterly_vintage_revision", "2025Q4 Q4/Q4: latest minus as-of-deadline", yy["2025Q4"] - yyv["2025Q4"], "pp", "calc", "both vintages above")

# forecast errors vs SPF
src_s = f"SPF {surv} median (COREPCE1..6, COREPCEA) vs latest vintage"
add("spf_vs_actual", f"2026Q2 SPF COREPCE1 (jump-off, {surv} survey)", spf["2026Q2"], "% ann.", "published", src_s)
add("spf_vs_actual", "2026Q2 actual q/q ann. (latest vintage)", qq["2026Q2"], "% ann.", "calc", vint_fred)
add("spf_vs_actual", "2026Q2 actual minus SPF jump-off", qq["2026Q2"] - spf["2026Q2"], "pp", "calc", src_s)
add("spf_vs_actual", "2026Q3 SPF COREPCE2 forecast", spf["2026Q3"], "% ann.", "published (survey deadline Aug 11, before Q3 data)", src_s)
add("spf_vs_actual", "2026Q3 actual q/q ann. (latest vintage; BEA first print, Oct 29 vintage)", qq["2026Q3"], "% ann.", "calc", vint_fred)
add("spf_vs_actual", "2026Q3 forecast error (actual minus SPF median)", qq["2026Q3"] - spf["2026Q3"], "pp", "calc", src_s)
add("spf_vs_actual", "2026Q3 actual minus SPF p75 (3.2)", qq["2026Q3"] - 3.2, "pp", "calc; p75 from Dispersion_1 offset T", "A_q1_spf_baseline.csv")
add("spf_vs_actual", "2026Q4 SPF COREPCE3 forecast", spf["2026Q4"], "% ann.", "published", src_s)
add("spf_vs_actual", "2026 Q4/Q4 SPF COREPCEA (median)", annA, "%", "published", src_s)

# SPF-consistency: quarterlies vs annual
q1, q2, q3a = qq["2026Q1"], qq["2026Q2"], qq["2026Q3"]
a_mix = C.q4q4_from_quarters([q1, q2, spf["2026Q3"], spf["2026Q4"]])
add("consistency", "2026 Q4/Q4 from actual Q1,Q2 + SPF Q3,Q4 medians", a_mix, "%", "calc: prod of (1+q/100)^(1/4); compare with published COREPCEA", src_s)
add("consistency", "Published COREPCEA minus that calc", annA - a_mix, "pp", "calc; gap = medians of different respondents / vintage", src_s)
need_q4 = C.derive_q4_from_annual(q1, q2, q3a, annA)
add("consistency", "2026Q4 q/q ann. needed for 2026 Q4/Q4 = SPF COREPCEA, given actual Q1-Q3 (latest vintage)", need_q4, "% ann.", "calc, not a forecast", src_s)
add("consistency", "2026 Q4/Q4 if 2026Q4 = SPF COREPCE3, given actual Q1-Q3 (latest vintage)", C.q4q4_from_quarters([q1, q2, q3a, spf["2026Q4"]]), "%", "calc, not a forecast", src_s)
nxt = C.q4q4_from_quarters([spf[f"{Y+1}Q1"], spf[f"{Y+1}Q2"], spf[f"{Y+1}Q3"], spf[f"{Y+1}Q3"]])
add("consistency", f"{Y+1} Q4/Q4 if Q4 simply repeats Q3 SPF pace ({spf[f'{Y+1}Q3']:.4f})", nxt, "%", "calc; vs published COREPCEB", src_s)
add("consistency", f"Published COREPCEB {Y+1}", row["COREPCEB"], "%", "published", src_s)

# Oct estimate and Nov/Dec calculations
sep, oct25 = m["2026-09-01"], m["2025-10-01"]
octl = sep * (1 + OCT_MM / 100)
add("oct_estimate", "Sep 2026 index (published)", sep, "index", "FRED", vint_fred)
add("oct_estimate", "Oct 2026 index implied by m/m 0.295", octl, "index", "calc: Sep*(1+0.00295)", "Slide1_Inflation_Data.xlsx Headline!C6 (m/m input, from brief)")
add("oct_estimate", "Oct 2026 y/y implied by that index vs Oct 2025", (octl / oct25 - 1) * 100, "%", f"calc; project stated {OCT_YY_STATED}% (Headline!C10)", "FRED Oct 2025 index")
q3avg, q4_25 = qa["2026Q3"], qa["2025Q4"]
target_g = (1 + spf["2026Q4"] / 100) ** (1 / 12) - 1


def scen(g):
    nov = octl * (1 + g)
    dec = nov * (1 + g)
    q4avg = (octl + nov + dec) / 3
    return dict(dec_yy=(dec / m["2025-12-01"] - 1) * 100, q4_qq=((q4avg / q3avg) ** 4 - 1) * 100, q4q4=(q4avg / q4_25 - 1) * 100)


# (ii-b): solve g so that Q4 q/q annualized = SPF 2026Q4 median
lo, hi = -0.02, 0.02
for _ in range(100):
    mid = (lo + hi) / 2
    if scen(mid)["q4_qq"] > spf["2026Q4"]:
        hi = mid
    else:
        lo = mid
g_solve = (lo + hi) / 2
for tag, g, desc in [("i", OCT_MM / 100, "Nov and Dec core m/m = 0.295 (Oct est.)"),
                     ("ii-a", target_g, f"Nov and Dec m/m = monthly equivalent of SPF 2026Q4 pace ({spf['2026Q4']:.4f}% ann. -> {target_g*100:.4f}%/mo)"),
                     ("ii-b", g_solve, "Nov and Dec m/m solved so 2026Q4 q/q annualized equals SPF median (given our Oct est.)")]:
    s = scen(g)
    add("calc_2026Q4_scenarios", f"({tag}) m/m for Nov, Dec", g * 100, "%", desc, "calc; not a forecast")
    add("calc_2026Q4_scenarios", f"({tag}) Dec 2026 y/y", s["dec_yy"], "%", desc, "calc; not a forecast")
    add("calc_2026Q4_scenarios", f"({tag}) 2026Q4 q/q annualized", s["q4_qq"], "% ann.", desc, "calc; not a forecast")
    add("calc_2026Q4_scenarios", f"({tag}) 2026 Q4/Q4", s["q4q4"], "%", desc, "calc; not a forecast")
add("calc_2026Q4_scenarios", "SPF 2026 Q4/Q4 median (for comparison)", annA, "%", "published", src_s)
add("calc_2026Q4_scenarios", "SPF 2026Q4 q/q ann. median (for comparison)", spf["2026Q4"], "% ann.", "published", src_s)

df = pd.DataFrame(rec)
df.to_csv(C.OUT / "A_q1_jumpoff.csv", index=False)
pd.set_option("display.width", 250, "display.max_colwidth", 80)
print(df[["section", "item", "value", "unit"]].to_string())
