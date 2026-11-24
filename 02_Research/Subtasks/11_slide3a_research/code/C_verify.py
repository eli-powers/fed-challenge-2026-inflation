"""Independent cross-checks of Agent C numbers. Run from project root with python3 -I. Output: outputs/C_verification_checks.csv"""
import importlib.util, json, re, html, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("C_common", Path.cwd() / "02_Research/Subtasks/11_slide3a_research/code/C_common.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
P = lambda s: pd.Period(s, "M")
rows = []
def chk(name, a, b, tol, note, src):
    rows.append(dict(check=name, value_a=a, value_b=b, abs_diff=round(abs(a - b), 5) if a is not None and b is not None else None, tolerance=tol, passed=(abs(a - b) <= tol) if a is not None and b is not None else None, note=note, source=src))

# 1 Dallas: FRED fresh vs pipeline obs (Dallas xlsx-sourced FRED fallback)
for sid, key in [("PCETRIM12M159SFRBDAL", "dallas_trimmed_mean_pce_12m"), ("PCETRIM1M158SFRBDAL", "dallas_trimmed_mean_pce_1m_ann"), ("PCETRIM6M680SFRBDAL", "dallas_trimmed_mean_pce_6m_ann")]:
    f = C.monthly_period(C.fred(sid)); o = C.pipeline_obs("fed_expectations", key); ps = pd.Series(o.value.values, index=o.date.dt.to_period("M"))
    chk(f"Dallas {sid} Sep 2026 fresh FRED vs pipeline", float(f[P("2026-09")]), float(ps[P("2026-09")]), 0.0005, "same vintage expected", C.rel(C.RAWC / f"FRED_{sid}_2026-11-15.json"))
# Dallas publisher xlsx
try:
    x = pd.read_excel(C.PIPE / "raw/fed_expectations/dallasfed_trimmed_mean_pce_2026-11-10.xlsx", sheet_name=None, header=None)
    for sh, d in x.items():
        txt = d.astype(str)
        hit = d[d.apply(lambda r: r.astype(str).str.contains("2026").any(), axis=1)].tail(2)
        rows.append(dict(check=f"Dallas publisher xlsx sheet '{sh}' last 2026 rows", value_a=None, value_b=None, abs_diff=None, tolerance=None, passed=None, note=hit.to_string()[:300].replace("\n", " | "), source="03_Data/pipelines/inflation_data/raw/fed_expectations/dallasfed_trimmed_mean_pce_2026-11-10.xlsx"))
except Exception as e:
    rows.append(dict(check="Dallas publisher xlsx read", note=str(e)))

# 2 MCT latest vs page text
meta = open(C.RAWC / "NYFed_MCT_meta_content_2026-11-15.json").read()
mm = re.search(r"was ([\d.]+) percent in September, an increase from ([\d.]+) percent", meta)
mct = pd.read_csv(C.RAWC / "NYFed_MCT_chart_data_2026-11-15.csv", skiprows=4, header=None, encoding="utf-8-sig"); mct["p"] = pd.to_datetime(mct[1]).dt.to_period("M"); mct = mct.set_index("p")
chk("MCT Sep 2026: csv (rounded 1dp) vs page text", round(float(mct.loc[P("2026-09"), 3]), 1), float(mm.group(1)), 0.0, "page text 'MCT was 2.8 percent in September'", "NYFed_MCT_meta_content_2026-11-15.json")
chk("MCT Aug 2026 revised: csv (1dp) vs page text", round(float(mct.loc[P("2026-08"), 3]), 1), float(mm.group(2)), 0.0, "page text 'from 2.6 percent (an upward revision) in August'", "NYFed_MCT_meta_content_2026-11-15.json")
chk("MCT band: csv lower/upper (1dp) vs page '(2.5, 3.2)'", round(float(mct.loc[P("2026-09"), 2]), 1) + round(float(mct.loc[P("2026-09"), 4]), 1), 2.5 + 3.2, 0.0, "68 percent band", "NYFed_MCT_meta_content_2026-11-15.json")
sec = float(mct.loc[P("2026-09"), 8]) + float(mct.loc[P("2026-09"), 9]) + float(mct.loc[P("2026-09"), 10])
chk("MCT Sep sector contributions sum vs 4th MCT column (MCT minus 2017-19 avg)", sec, float(mct.loc[P("2026-09"), 5]), 0.03, "sum of goods + services ex housing + housing vs col 5; supports label inference", "NYFed_MCT_chart_data_2026-11-15.csv")

# 3 SCE: fresh vs press release text 3.9/3.3/3.0
pr = open(C.RAWC / "NYFed_SCE_press_release_20261109_2026-11-15.html", errors="ignore").read(); pr = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", pr); pr = html.unescape(re.sub(r"\s+", " ", pr))
m = re.search(r"at ([\d.]+)%, ([\d.]+)%, and ([\d.]+)%, respectively", pr)
d = pd.read_excel(C.RAWC / "NYFed_SCE_chart_data_2026-11-15.xlsx", sheet_name="Inflation expectations", header=None)
last = d[d[0].astype(str).str.fullmatch(r"\d{6}")].iloc[-1]
chk("SCE Oct 2026 1y median: xlsx (1dp) vs press release", round(float(last[1]), 1), float(m.group(1)), 0.0, "press release Nov 9 2026", "NYFed_SCE_press_release_20261109_2026-11-15.html")
chk("SCE Oct 2026 3y median: xlsx (1dp) vs press release", round(float(last[2]), 1), float(m.group(2)), 0.0, "", "NYFed_SCE_press_release_20261109_2026-11-15.html")
sce5 = C.pipeline_obs("fed_expectations", "nyfed_sce_5y_inflation_expectation").iloc[-1]
chk("SCE Oct 2026 5y median: pipeline (1dp) vs press release", round(float(sce5.value), 1), float(m.group(3)), 0.0, "", "NYFed_SCE_press_release_20261109_2026-11-15.html")

# 4 Michigan: FRED MICH vs pipeline publisher CSV (through Sep)
f = C.monthly_period(C.fred("MICH")); o = C.pipeline_obs("fed_expectations", "umich_1y_expected_price_change_median"); ps = pd.Series(o.value.values, index=o.date.dt.to_period("M"))
j = pd.concat([f, ps], axis=1, join="inner").dropna(); j = j[j.index >= P("2018-01")]
chk("Michigan 1y median: FRED MICH vs publisher CSV, max abs diff 2018-01..latest FRED", float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()), 0.0, 0.05, f"n={len(j)}; FRED last {j.index[-1]}", "FRED_MICH_2026-11-15.json vs umich_sca_tbmpx1px5_2026-11-10.csv")

# 5 breakevens: pipeline (2026-11-10 pull) vs fresh overlap
for sid, key in [("T5YIE", "fred_t5yie"), ("T5YIFR", "fred_t5yifr")]:
    f = C.fred(sid).dropna(); o = C.pipeline_obs("fed_expectations", key); ps = pd.Series(o.value.values, index=pd.to_datetime(o.date))
    j = pd.concat([f, ps], axis=1, join="inner").dropna()
    chk(f"{sid}: fresh FRED vs pipeline pull, max abs diff over overlap", float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()), 0.0, 0.0001, f"n={len(j)}", C.rel(C.RAWC / f"FRED_{sid}_2026-11-15.json"))

# 6 Supercore / Logan: leaf-aggregation 12m cross-check from components.csv (Dallas 178 leaves; Laspeyres, base-12m weights)
cc = pd.read_csv(C.ROOT / "03_Data/pipelines/Price indexes/PCE/processed/components.csv"); cc = cc[(cc.index_name == "PCE core") & (cc.in_core == "Y")].copy()
cc["line"] = cc.component_id.str.extract(r"U20404 line (\d+)").astype(int); cs = cc[cc.line >= 150]
hs = cs.line.between(154, 164); tr = cs.line.between(190, 208)
def leaf12(mask):
    d_ = cs[mask]; return float((d_.weight_base_12m * d_.pct_12m_calc).sum() / d_.weight_base_12m.sum())
lm = pd.read_csv(C.OUTD / "C_q6_logan_measure.csv").set_index("month")
chk("Logan measure Sep 2026 12m: exact derived vs leaf-Laspeyres (components.csv)", float(lm.loc["2026-09", "12m_pct"]), leaf12(~hs & ~tr), 0.15, "approximation check only (Laspeyres leaf aggregation vs chained Fisher)", "03_Data/pipelines/Price indexes/PCE/processed/components.csv")
sup_pub = C.pipeline_obs("bea", "pce_services_ex_energy_housing_price"); sup_pub = pd.Series(sup_pub[sup_pub.horizon == "level"].value.astype(float).values, index=sup_pub[sup_pub.horizon == "level"].date.dt.to_period("M"))
chk("Supercore Sep 2026 12m: BEA published (T20804 L28) vs leaf-Laspeyres", float((sup_pub.iloc[-1] / sup_pub.iloc[-13] - 1) * 100), leaf12(~hs), 0.15, "approximation check only", "components.csv + pipeline BEA obs")
# 7 core PCE 12m: pipeline BEA vs FRED PCEPILFE
f = C.monthly_period(C.fred("PCEPILFE")); chk("Core PCE Sep 2026 12m: FRED PCEPILFE vs pipeline BEA T20804 L25", float(C.pct(f, 12)[P("2026-09")]), 3.121, 0.002, "REPORT.md states 3.121", "FRED_PCEPILFE_2026-11-15.json; PCE/processed/REPORT.md")
# 8 Oct est core: D_build summary vs C_q8
est = pd.read_csv(C.ROOT / "02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv")
q8 = pd.read_csv(C.OUTD / "C_q8_time_above_target.csv").set_index("month")
chk("Core PCE Oct 2026 est 12m: D_build vs C_q8 file", float(est[est.measure == "core"].rate_12m.iloc[0]), float(q8.loc["2026-10", "core_12m"]), 1e-4, "est.", "04_oct_pce_build/outputs/D_build_2026-10_summary.csv")
# 9 Logan aggregate 3.38
x = pd.read_csv(C.OUTD / "C_q4_logan_aggregate.csv"); chk("Logan 13-survey aggregate: our workbook vs her ~3.1", float(x[x.measure == "Simple average of 13"].value.iloc[0]), 3.1, 0.05, "does NOT reproduce if passed=False", "03_Data/pipelines/inflation_data/Inflation_Expectations.xlsx")
pd.DataFrame(rows).to_csv(C.OUTD / "C_verification_checks.csv", index=False)
print(pd.DataFrame(rows)[["check", "value_a", "value_b", "abs_diff", "passed"]].to_string())
