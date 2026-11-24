"""Build Inflation_Expectations.xlsx: an unweighted average of 13 one-year-ahead
inflation expectation measures (households, businesses, professional forecasters,
markets), modeled on Dallas Fed President Logan's Nov 10, 2026 "baker's dozen".

Run from the project root:
    python3 "03_Data/pipelines/inflation_data/code/build_expectations_aggregate.py"

Inputs
- processed/fed_expectations/observations.csv (pipeline: Michigan, NY Fed SCE, SPF)
- raw/expectations_aggregate/*_<RAW_DATE>.* (publisher downloads, never edited)

Method: simple average of each measure's latest reading, with no weights. Measures mix
CPI, PCE and own-firm price/cost concepts and survey dates; see the "Measures" sheet.
"""
import json
import re
import html
from pathlib import Path

import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]          # .../inflation_data
RAW = ROOT / "raw" / "expectations_aggregate"
PROC = ROOT / "processed" / "fed_expectations" / "observations.csv"
OUT = ROOT / "Inflation_Expectations.xlsx"
RAW_DATE = "2026-11-14"


def raw(name):
    return RAW / f"{name}_{RAW_DATE}{'' if '.' in name else ''}"


def html_text(path):
    t = path.read_text(errors="ignore")
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t))


def find(pattern, text, label):
    m = re.search(pattern, text)
    if not m:
        raise ValueError(f"{label}: pattern not found")
    return m


obs = pd.read_csv(PROC)


def pipeline_latest(key):
    s = obs[obs.series_key == key].sort_values("date").iloc[-1]
    return float(s.value), s.date, s.raw_file


rows = []


def add(group, name, publisher, concept, horizon, value, obs_date, source, note=""):
    rows.append(dict(Group=group, Measure=name, Publisher=publisher, Concept=concept,
                     Horizon=horizon, Value=round(value, 2), Observation=obs_date,
                     Source=str(source), Note=note))


# ---------------- Households ----------------
v, d, f = pipeline_latest("umich_1y_expected_price_change_median")
add("Household", "Michigan Surveys of Consumers, 1-yr expected price change (median)",
    "University of Michigan", "General prices", "Next 12 months", v, d, f,
    "Nov 2026 is PRELIMINARY; final Nov 20 (after cutoff).")

v, d, f = pipeline_latest("nyfed_sce_1y_inflation_expectation")
add("Household", "NY Fed Survey of Consumer Expectations, 1-yr inflation (median)",
    "Federal Reserve Bank of New York", "Inflation rate", "1 year ahead", v, d, f)

p = RAW / f"conferenceboard_CCI_Oct2026_press_{RAW_DATE}.html"
m = find(r"average 12-month inflation expectations[^.]*?at ([0-9.]+)%", html_text(p), "Conference Board")
add("Household", "Conference Board Consumer Confidence, 12-month inflation expectations (average)",
    "The Conference Board", "Inflation rate", "Next 12 months", float(m.group(1)), "2026-10", p.name,
    "From the Oct press release text; the series itself is paywalled. Mean, not median (runs high).")

# ---------------- Businesses ----------------
p = RAW / f"atlantafed_bie-data_{RAW_DATE}.xlsx"
ws = openpyxl.load_workbook(p, data_only=True)["BIE Survey results"]
r = list(ws.iter_rows(values_only=True))
hdr2 = r[2]
q4 = [i for i, h in enumerate(r[1]) if h and str(h).startswith("Question 4")][0]
mean_col = [i for i in range(q4, len(hdr2)) if hdr2[i] == "Mean"][0]
last = r[-1]
add("Business", "Atlanta Fed Business Inflation Expectations, year-ahead unit costs (mean)",
    "Federal Reserve Bank of Atlanta", "Own-firm unit costs", "Next 12 months",
    last[mean_col] * 100, last[0].date().isoformat(), p.name)

p = RAW / f"clevelandfed_sofie_statistics_{RAW_DATE}.xlsx"
r = [x for x in openpyxl.load_workbook(p, data_only=True)["Question_1"].iter_rows(values_only=True)
     if x[0] and re.match(r"^\d{4}\.\d$", str(x[0]))]
add("Business", "Cleveland Fed Survey of Firms' Inflation Expectations, 12-month CPI (mean)",
    "Federal Reserve Bank of Cleveland", "CPI", "Next 12 months", r[-1][1], r[-1][0], p.name,
    "Quarterly; latest posted wave is 2026.3.")

for fname, col, label in [
    ("richmondfed_mfg_historicaldata", "nsa_mfg_pct_chg_prcs_recd_e", "manufacturing"),
    ("richmondfed_nmf_historicaldata", "nsa_svc_prcs_recd_e", "non-manufacturing (services)"),
]:
    p = RAW / f"{fname}_{RAW_DATE}.xlsx"
    r = list(openpyxl.load_workbook(p, data_only=True).active.iter_rows(values_only=True))
    i = r[0].index(col)
    lastrow = [x for x in r[1:] if isinstance(x[i], (int, float))][-1]
    add("Business", f"Richmond Fed {label} survey, expected prices received next 12 months",
        "Federal Reserve Bank of Richmond", "Own-firm prices received", "Next 12 months",
        lastrow[i], lastrow[0].date().isoformat(), p.name,
        f"Column {col}. Fifth District firms only (UMD's district).")

p = RAW / f"richmondfed_cfo_survey_2026Q3_results_{RAW_DATE}.html"
m = find(r"Price ([0-9.]+)% \([0-9.]+%\) ([0-9.]+)% \([0-9.]+%\)", html_text(p), "CFO Survey")
add("Business", "CFO Survey (Richmond/Atlanta Feds, Duke), own-firm price growth for 2027 (mean)",
    "FRB Richmond / FRB Atlanta / Duke", "Own-firm prices", "Calendar 2027 y/y", float(m.group(2)),
    "2026Q3 (fielded Aug 17-Sep 4)", p.name,
    "Revenue-weighted mean; median 3.0%. Calendar-2027 horizon is the closest to 1 year ahead.")

# ---------------- Professional forecasters ----------------
def spf_next4(prefix):
    vals, d = [], None
    for h in (3, 4, 5, 6):
        v, d, _ = pipeline_latest(f"spf_{prefix}_{prefix}{h}")
        vals.append(v)
    g = 1.0
    for v in vals:
        g *= (1 + v / 100) ** 0.25
    return (g - 1) * 100, d, vals

v, d, parts = spf_next4("pce")
add("Professional", "Survey of Professional Forecasters, headline PCE, next 4 quarters (median)",
    "Federal Reserve Bank of Philadelphia", "PCE", "4 quarters after survey quarter", v,
    "2026Q3 survey (Aug)", "processed/fed_expectations/observations.csv (spf_pce_pce3..6)",
    f"Compounded from quarterly annualized medians {', '.join(f'{x:.2f}' for x in parts)}. "
    "Q4 SPF not yet released as of Nov 14; rerun when it is.")

p = RAW / f"philadelphiafed_livingston_jun26_{RAW_DATE}.pdf"
t = " ".join(pg.extract_text() for pg in PdfReader(p).pages)
m = find(r"Consumer Price Index \(CPI-U\)\s+\d+\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)", t, "Livingston")
jun26, jun27 = float(m.group(2)), float(m.group(4))
add("Professional", "Livingston Survey, CPI-U Jun 2026 to Jun 2027 (median)",
    "Federal Reserve Bank of Philadelphia", "CPI", "Jun 2026-Jun 2027",
    (jun27 / jun26 - 1) * 100, "2026-06 (forecasts due Jun 3)", p.name,
    f"From forecast index levels {jun26} to {jun27}. Semiannual; STALE (pre-dates the late-2026 energy run-up).")

p = RAW / f"philadelphiafed_ATSIX_Vintages_{RAW_DATE}.xlsx"
r = list(openpyxl.load_workbook(p, data_only=True, read_only=True)["InfExp"].iter_rows(values_only=True))
c = r[0].index("infexp12")
add("Professional", "Aruoba Term Structure of Inflation Expectations, 12 months ahead",
    "Federal Reserve Bank of Philadelphia", "CPI", "12 months ahead", r[-1][c],
    r[-1][0].date().isoformat(), p.name,
    "Model curve fitted to SPF and Blue Chip forecasts, so it partly overlaps SPF.")

p = RAW / f"nyfed_sme_sep-2026-data_{RAW_DATE}.xlsx"
sme = pd.read_excel(p)
sel = sme[(sme.value_tag == "econoutlook_pathofmodes_headlinepce_2027") & (sme.aggregation == "pctl50")
          & (sme.panel_type == "Combined")]
assert len(sel) == 1, len(sel)
add("Professional", "NY Fed Survey of Market Expectations (market participants), headline PCE 2027 Q4/Q4 (median)",
    "Federal Reserve Bank of New York", "PCE", "2027 Q4/Q4", float(sel.aggregation_value.iloc[0]) * 100,
    "2026-09 survey (due Sep 8)", p.name,
    "October survey results not yet posted. A survey of dealers and buy-side firms, not a market price.")

# ---------------- Markets ----------------
p = RAW / f"fred_EXPINF1YR_{RAW_DATE}.json"
o = json.loads(p.read_text())["observations"][-1]
add("Market", "Cleveland Fed 1-year expected inflation",
    "Federal Reserve Bank of Cleveland (via FRED EXPINF1YR)", "CPI", "Next 12 months",
    float(o["value"]), o["date"], p.name,
    "Model blending Treasury yields, inflation swaps and survey forecasts. "
    "Free 1-yr swaps/breakevens unavailable; Minneapolis Fed 1-yr options series ended 2018.")

df = pd.DataFrame(rows)
assert len(df) == 13, len(df)
avg = df.Value.mean()
grp = df.groupby("Group", sort=False).Value.agg(["count", "mean"]).round(2)

# Memo items (not in the average)
memo = []
v, d, f = pipeline_latest("spf_cpi_cpi3")
cpi_v, cpi_d, cpi_parts = spf_next4("cpi")
memo.append(("SPF headline CPI, next 4 quarters (same panel as SPF PCE)", round(cpi_v, 2), "2026Q3 survey"))
v, d, f = pipeline_latest("umich_5to10y_expected_price_change_median"); memo.append(("Michigan 5-10 yr (median)", v, d))
v, d, f = pipeline_latest("nyfed_sce_3y_inflation_expectation"); memo.append(("NY Fed SCE 3 yr (median)", round(v, 2), d))
v, d, f = pipeline_latest("fred_t5yifr"); memo.append(("5y5y forward breakeven (FRED T5YIFR)", v, d))
v, d, f = pipeline_latest("spf_pce10_pce10"); memo.append(("SPF 10-yr PCE (median)", v, "2026Q3 survey"))

wb = openpyxl.Workbook()
ws = wb.active; ws.title = "Summary"
bold = Font(bold=True)
ws.append(["Inflation expectations: unweighted average of 13 one-year-ahead measures"]); ws["A1"].font = Font(bold=True, size=13)
ws.append([f"Built {RAW_DATE} by code/build_expectations_aggregate.py. Modeled on Logan (Dallas Fed), Nov 10, 2026: 13 surveys of households, businesses and market participants."])
ws.append([])
ws.append(["Simple average (13 measures, %)", round(avg, 2)]); ws["A4"].font = bold; ws["B4"].font = bold
ws.append(["For reference: Logan's figure (her staff, PCE-based, Nov 10)", 3.1])
ws.append(["Median of the 13 (%)", round(df.Value.median(), 2)])
ws.append(["Min / max (%)", f"{df.Value.min():.2f} / {df.Value.max():.2f}"])
ws.append([])
ws.append(["Group", "Count", "Average (%)"]);
for c in ws[ws.max_row]: c.font = bold
for g, r_ in grp.iterrows():
    ws.append([g, int(r_["count"]), r_["mean"]])
ws.append([])
ws.append(["Caveats"]); ws.cell(ws.max_row, 1).font = bold
for line in [
    "Not like-for-like: the measures mix CPI, PCE, and own-firm prices or costs; medians and means; survey dates from Jun to Nov 2026.",
    "CPI-based measures typically run a few tenths above PCE, so the simple average sits above a pure PCE-equivalent figure.",
    "Logan's 13 are not published. Our set is a reconstruction, not her list.",
    "Unweighted, so the group mix drives the result (3 household, 5 business, 4 professional, 1 market).",
    "Stale readings: Livingston (Jun), SPF and NY Fed SME (Aug-Sep), CFO and SoFIE (Q3). Rerun when Q4 SPF and the Oct SME post.",
]:
    ws.append(["- " + line])
ws.column_dimensions["A"].width = 95; ws.column_dimensions["B"].width = 14; ws.column_dimensions["C"].width = 14

ws2 = wb.create_sheet("Measures")
cols = list(df.columns)
ws2.append(cols)
for c in ws2[1]:
    c.font = bold; c.fill = PatternFill("solid", fgColor="DDDDDD")
for _, r_ in df.iterrows():
    ws2.append([r_[c] for c in cols])
ws2.append([]); ws2.append(["", "Simple average", "", "", "", round(avg, 2)])
for c, w in zip("ABCDEFGHI", [13, 70, 34, 24, 26, 8, 26, 55, 80]):
    ws2.column_dimensions[c].width = w
for row in ws2.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")

ws3 = wb.create_sheet("Memo (not averaged)")
ws3.append(["Measure", "Value (%)", "As of"])
for c in ws3[1]: c.font = bold
for m_ in memo:
    ws3.append(list(m_))
ws3.column_dimensions["A"].width = 60

wb.save(OUT)
print(df[["Group", "Measure", "Value", "Observation"]].to_string())
print("\nAVERAGE", round(avg, 3)); print(grp)
