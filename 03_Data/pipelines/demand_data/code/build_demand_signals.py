"""Build demand_signals.xlsx from demand_data/processed/.

Change measures (computed here from saved publisher levels unless noted):
  YoY           (x_t / x_t-12m - 1) x 100 for flows/levels; for quarterly series t-4q.
  3m/3m ann.    ((avg of latest 3 months / avg of prior 3 months)^4 - 1) x 100 — monthly flows.
  MoM ann.      ((x_t / x_t-1)^12 - 1) x 100 — monthly flows (shown for completeness; noisy).
  Q/Q SAAR      BEA-published percent change from preceding quarter at annual rate (not recomputed).
  Rates/indexes (saving rate, sentiment, spending share, net-worth ratio): changes in percentage points / index points.

Usage: python3 build_demand_signals.py [OUT_DIR]   (default: demand_data/, i.e. overwrite the live workbook and processed table)
The TLDR sheet is Eli's own interpretation and is never generated: if the existing demand_signals.xlsx has a TLDR sheet it is carried
forward verbatim (with an "As of ..." banner as the first line); otherwise no TLDR sheet is written.
"""
import re
import sys
from copy import copy
from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
OUT_DIR.mkdir(parents=True, exist_ok=True)
LIVE_XLSX = ROOT / "demand_signals.xlsx"
PREV_TLDR = None  # existing TLDR sheet, read before anything is overwritten
if LIVE_XLSX.exists():
    _wb = load_workbook(LIVE_XLSX)
    if "TLDR" in _wb.sheetnames:
        PREV_TLDR = _wb["TLDR"]
obs = pd.concat([pd.read_csv(p, dtype=str) for p in (ROOT / "processed").glob("*/observations.csv")], ignore_index=True)
obs["v"] = pd.to_numeric(obs["value"], errors="coerce")
obs["d"] = pd.to_datetime(obs["date"])


def s(key):
    x = obs[obs.series_key == key].dropna(subset=["v"]).set_index("d")["v"].sort_index()
    if x.empty:
        raise KeyError(key)
    return x


def pct(a, b):
    return None if b is None or pd.isna(b) or b == 0 or pd.isna(a) else (a / b - 1) * 100


def at(x, d):
    return x.get(d, float("nan"))


def monthly_flow(x):
    t = x.index[-1]
    yoy = pct(x.iloc[-1], at(x, t - pd.DateOffset(years=1)))
    last3, prev3 = x.iloc[-3:], x.iloc[-6:-3]
    three = ((last3.mean() / prev3.mean()) ** 4 - 1) * 100 if len(prev3) == 3 and (x.index[-6] == t - pd.DateOffset(months=5)) else None
    mom = ((x.iloc[-1] / x.iloc[-2]) ** 12 - 1) * 100 if x.index[-2] == t - pd.DateOffset(months=1) else None
    return t, x.iloc[-1], yoy, three, mom


def base_yoy(x, months=12):
    """Average YoY over 2015-2019 (pre-pandemic baseline for the same measure)."""
    y = (x / x.shift(freq=pd.DateOffset(months=months)) - 1) * 100
    y = y[(y.index >= "2016-01-01") & (y.index <= "2019-12-31")].dropna()
    return y.mean() if len(y) else None


rows = []  # (channel, indicator, source, freq, period, latest, units, yoy, short, short_label, mom, chg_units, baseline)


def add(channel, indicator, source, freq, period, latest, units, yoy, short, short_label, mom, chg_units, baseline):
    rows.append(dict(channel=channel, indicator=indicator, source=source, freq=freq, period=period, latest=latest, units=units,
                     yoy=yoy, short=short, short_label=short_label, mom=mom, chg_units=chg_units, baseline=baseline))


def label_m(t):
    return t.strftime("%b %Y")


def label_q(t):
    return f"{t.year} Q{(t.month - 1) // 3 + 1}"


def flow_row(channel, indicator, source, key, units, series=None, scale=1.0):
    x = series if series is not None else s(key)
    t, last, yoy, three, mom = monthly_flow(x)
    add(channel, indicator, source, "Monthly", label_m(t), round(last * scale, 1), units, yoy, three, "3m/3m ann.", mom, "%", base_yoy(x))


def bea_quarterly(indicator, key):
    lv, qq = s(key), s(key + "_pct_qq_saar")
    t = lv.index[-1]
    add("AI buildout", indicator, "BEA NIPA 5.3.6 / 5.3.1", "Quarterly", label_q(t), round(lv.iloc[-1] / 1000, 1), "Bil. chained 2017 $, SAAR",
        pct(lv.iloc[-1], at(lv, t - pd.DateOffset(years=1))), qq.iloc[-1], "Q/Q SAAR (BEA)", None, "%", base_yoy(lv))


# ------------------------------------------------------------ AI buildout
A = "AI buildout"
bea_quarterly("Real investment: information processing equipment", "ai_investment_info_processing_equipment")
bea_quarterly("Real investment: software", "ai_investment_software")
bea_quarterly("Real investment: equipment (total)", "ai_investment_equipment_total")
bea_quarterly("Real investment: intellectual property products (total)", "ai_investment_ip_products_total")
bea_quarterly("Real nonresidential fixed investment (total)", "ai_investment_nonresidential_total")

dc, nr = s("construction_private_data_center"), s("private_nonresidential_construction")
t = dc.index[-1]
dc3 = dc.rolling(3).mean()
add(A, "Data center construction spending (nominal)", "Census C30", "Monthly", label_m(t), round(dc.iloc[-1] / 1000, 1), "Bil. $, SAAR",
    pct(dc3.iloc[-1], at(dc3, t - pd.DateOffset(years=1))), monthly_flow(dc)[3], "3m/3m ann.", monthly_flow(dc)[4], "%", base_yoy(dc3))
share = dc / nr * 100
add(A, "Data centers as share of private nonresidential construction", "Census C30", "Monthly", label_m(t), round(share.iloc[-1], 1), "% of total",
    share.iloc[-1] - at(share, t - pd.DateOffset(years=1)), share.iloc[-1] - at(share, t - pd.DateOffset(months=3)), "3-mo change", None, "pp", None)
flow_row(A, "Core capital goods orders (nondefense ex aircraft)", "Census M3", "manufacturers_new_orders_nondefense_capital_goods_excluding_aircraft", "Bil. $, SA", scale=1e-3)
flow_row(A, "Core capital goods shipments (nondefense ex aircraft)", "Census M3", "manufacturers_shipments_nondefense_capital_goods_excluding_aircraft", "Bil. $, SA", scale=1e-3)
flow_row(A, "Computer & electronic products: new orders", "Census M3", "manufacturers_new_orders_computers_and_electronic_products", "Bil. $, SA", scale=1e-3)
flow_row(A, "Computer & electronic products: shipments", "Census M3", "manufacturers_shipments_computers_and_electronic_products", "Bil. $, SA", scale=1e-3)
flow_row(A, "Industrial production: semiconductors & electronic components", "Fed G.17", "industrial_production_semiconductors_and_other_electronic_components", "Index 2017=100")

capex_keys = [k for k in ["capex_microsoft", "capex_alphabet", "capex_amazon", "capex_meta"] if k in set(obs.series_key)]
if capex_keys:
    cap = pd.concat([s(k) for k in capex_keys], axis=1).dropna()
    tot = cap.sum(axis=1)
    t = tot.index[-1]
    ttm = tot.rolling(4).sum()
    add(A, "Hyperscaler cash capex (MSFT+GOOGL+AMZN+META)", "SEC filings (10-Q/10-K)", "Quarterly", label_q(t), round(tot.iloc[-1] / 1000, 1),
        "Bil. $, quarterly, NSA", pct(tot.iloc[-1], at(tot, t - pd.DateOffset(years=1))), pct(ttm.iloc[-1], at(ttm, t - pd.DateOffset(years=1))),
        "Trailing-4Q sum YoY", None, "%", None)
    for k, name in zip(capex_keys, ["Microsoft", "Alphabet", "Amazon", "Meta"]):
        x = s(k)
        tk = x.index[-1]
        add(A, f"   {name} cash capex", "SEC filings", "Quarterly", label_q(tk), round(x.iloc[-1] / 1000, 1), "Bil. $, quarterly, NSA",
            pct(x.iloc[-1], at(x, tk - pd.DateOffset(years=1))), None, "", None, "%", None)

# --------------------------------------------------------------- Consumer
C = "Consumer"
flow_row(C, "Real consumer spending (PCE), total", "BEA", "pce_real_total", "Tril. chained 2017 $, SAAR", scale=1e-6)
flow_row(C, "Real PCE: goods", "BEA", "pce_real_goods", "Tril. chained 2017 $, SAAR", scale=1e-6)
flow_row(C, "Real PCE: services", "BEA", "pce_real_services", "Tril. chained 2017 $, SAAR", scale=1e-6)
flow_row(C, "Real disposable personal income", "BEA", "real_disposable_personal_income", "Tril. chained 2017 $, SAAR", scale=1e-3)
sr = s("personal_saving_rate")
t = sr.index[-1]
add(C, "Personal saving rate", "BEA", "Monthly", label_m(t), sr.iloc[-1], "% of disposable income", sr.iloc[-1] - at(sr, t - pd.DateOffset(years=1)),
    sr.iloc[-1] - at(sr, t - pd.DateOffset(months=3)), "3-mo change", sr.iloc[-1] - sr.iloc[-2], "pp", sr["2016":"2019"].mean())
gas = s("pce_nominal_gasoline_energy_goods") / s("pce_nominal_total") * 100
t = gas.index[-1]
add(C, "Gasoline & other energy goods, share of spending", "BEA (computed share)", "Monthly", label_m(t), round(gas.iloc[-1], 2), "% of nominal PCE",
    gas.iloc[-1] - at(gas, t - pd.DateOffset(years=1)), gas.iloc[-1] - at(gas, t - pd.DateOffset(months=3)), "3-mo change", gas.iloc[-1] - gas.iloc[-2], "pp",
    gas["2016":"2019"].mean())
flow_row(C, "Retail & food services sales (nominal)", "Census", "retail_and_food_services_total", "Bil. $, SA", scale=1e-3)
ctrl = s("retail_trade_excluding_food_services") - s("motor_vehicle_and_parts_dealers") - s("gasoline_stations") - s("building_materials_garden_equipment_and_supplies_dealers")
flow_row(C, "Retail control group (nominal)", "Census (computed)", None, "Bil. $, SA", series=ctrl.dropna(), scale=1e-3)
flow_row(C, "Gasoline station sales (nominal)", "Census", "gasoline_stations", "Bil. $, SA", scale=1e-3)
flow_row(C, "Revolving consumer credit outstanding", "Fed G.19", "revolving_consumer_credit_outstanding", "Tril. $, SA", scale=1e-6)
nw = s("household_and_nonprofit_net_worth_as_percent_of_disposable_personal_income")
t = nw.index[-1]
add(C, "Household net worth / disposable income", "Fed Z.1", "Quarterly", label_q(t), round(nw.iloc[-1], 0), "% of disposable income",
    nw.iloc[-1] - at(nw, t - pd.DateOffset(years=1)), nw.iloc[-1] - nw.iloc[-2], "Q/Q change", None, "pp", nw["2016":"2019"].mean())

# Michigan: full history from raw publisher files for percentile
raw_mich = {"ICS_ALL": "Michigan_tbmics_*.csv", "ICC": "Michigan_tbmiccice_*.csv", "ICE": "Michigan_tbmiccice_*.csv"}  # newest-dated file is used
for key, col, name in [("umich_index_of_consumer_sentiment", "ICS_ALL", "Michigan consumer sentiment"),
                       ("umich_index_of_current_economic_conditions", "ICC", "Michigan: current conditions"),
                       ("umich_index_of_consumer_expectations", "ICE", "Michigan: expectations")]:
    x = s(key)
    t = x.index[-1]
    hist = pd.read_csv(sorted((ROOT / "raw" / "official").glob(raw_mich[col]))[-1])  # ISO date in name: sorted() = newest last
    full = pd.to_numeric(hist[col], errors="coerce").dropna()
    rank = int((full < x.iloc[-1]).sum()) + 1
    _n = obs.loc[(obs.series_key == key) & (pd.to_datetime(obs.date) == t), "note"].fillna("")
    prelim = bool(_n.str.contains("PRELIMINARY").any())  # latest month from the publisher's current table, flagged (P)
    add(C, f"{name}{' [latest month PRELIMINARY]' if prelim else ''} (rank: #{rank} lowest since {int(hist['YYYY'].min())}; ranked against final readings)",
        "Univ. of Michigan", "Monthly", label_m(t),
        x.iloc[-1], "Index (1966Q1=100)", x.iloc[-1] - at(x, t - pd.DateOffset(years=1)), x.iloc[-1] - at(x, t - pd.DateOffset(months=3)), "3-mo change",
        x.iloc[-1] - x.iloc[-2], "index pts", x["2016":"2019"].mean())
cb_keys = [k for k in set(obs.series_key) if k.startswith("conference_board")]
for k in sorted(cb_keys):
    x = s(k)
    t = x.index[-1]
    add(C, "Conference Board " + k.replace("conference_board_", "").replace("_", " "), "The Conference Board (press releases)", "Monthly", label_m(t),
        x.iloc[-1], "Index (1985=100)", x.iloc[-1] - at(x, t - pd.DateOffset(years=1)), x.iloc[-1] - at(x, t - pd.DateOffset(months=3)), "3-mo change",
        x.iloc[-1] - at(x, t - pd.DateOffset(months=1)), "index pts", None)

df = pd.DataFrame(rows)
df.to_csv((ROOT / "processed" if len(sys.argv) == 1 else OUT_DIR) / "demand_signals_table.csv", index=False)
print(df[["channel", "indicator", "period", "latest", "yoy", "short", "short_label", "mom", "chg_units", "baseline"]].round(2).to_string())

# ------------------------------------------------------------------ workbook
COLS = ["Indicator", "Source", "Frequency", "Latest period", "Latest value", "Units", "YoY", "3-mo change", "3-mo measure", "1-mo change", "Change units", "2016-19 norm"]
wb = Workbook()
ws = wb.active
ws.title = "Demand Signals"
NAVY, GREY = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
ws.append([None])  # row 1 blank so the table header is row 2, as in the live workbook
hdr = ws.max_row + 1
ws.append(COLS)
for c in ws[hdr]:
    c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), NAVY, Alignment(wrap_text=True, horizontal="center")
for ch in ["AI buildout", "Consumer"]:
    ws.append([f"Channel: {ch}"])
    r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(COLS))
    ws.cell(r, 1).font, ws.cell(r, 1).fill = Font(bold=True), GREY
    for _, x in df[df.channel == ch].iterrows():
        rnd = lambda v, n=1: None if v is None or pd.isna(v) else round(float(v), n)
        ws.append([x.indicator, x.source, x.freq, x.period, x.latest, x.units, rnd(x.yoy), rnd(x.short), x.short_label or None,
                   rnd(x.mom), x.chg_units, rnd(x.baseline)])
for row in ws.iter_rows(min_row=hdr, max_row=ws.max_row):
    for c in row:
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if c.column >= 5 and isinstance(c.value, (int, float)):
            c.number_format = "0.0"
for i, w in enumerate([58, 26, 11, 12, 12, 26, 9, 11, 20, 11, 10, 11], 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = f"B{hdr + 1}"


# ---- values computed from the processed data for the Notes & Caveats sheet (no hand-typed numbers)
R = {r["indicator"]: r for r in rows}


def full_month(label):  # "Aug 2026" -> "August"
    return datetime.strptime(label, "%b %Y").strftime("%B")


def per(ind):  # latest-period label of a table row; quarters -> "Q2"
    p_ = R[ind]["period"]
    return p_.split()[1] if " Q" in p_ else full_month(p_)


def sgn(v, unit):
    return f"{v:+.1f}{unit}"


goods = R["Real PCE: goods"]
pce_example = f"{sgn(goods['mom'], '%')} MoM ann. vs {sgn(goods['short'], '%')} 3m/3m ann."
sr_chg = sgn(R["Personal saving rate"]["yoy"], " pp")
gas_chg = sgn(R["Gasoline & other energy goods, share of spending"]["yoy"], " pp")
mich_p, cb_p = per([k for k in R if k.startswith("Michigan consumer sentiment")][0]), per("Conference Board confidence")
mich_cb = f"Michigan and Conference Board {mich_p}" if mich_p == cb_p else f"Michigan {mich_p}, Conference Board {cb_p}"
latest_months = (f"Latest months differ by source (BEA {per('Real consumer spending (PCE), total')}, quarterly investment "
                 f"{per('Real investment: information processing equipment')}; Census {per('Retail & food services sales (nominal)')}; "
                 f"Fed G.17 {per('Industrial production: semiconductors & electronic components')}, G.19 {per('Revolving consumer credit outstanding')}, "
                 f"Z.1 {per('Household net worth / disposable income')}; {mich_cb}). Map to prices at matching dates in step 5.")
# Conference Board: every transcribed month since Aug 2025, newest first, each at the latest vintage recorded in processed/research
cbo = obs[obs.series_key.str.startswith("conference_board") & (obs.d >= "2025-08-01")]
cb_items = []
for d_ in sorted(set(cbo.d), reverse=True):
    g = cbo[cbo.d == d_].set_index("series_key")
    nt = g.loc["conference_board_confidence", "note"].replace("Manager transcription: ", "").rstrip(".")
    cb_items.append(f"{d_.strftime('%b %Y')} ({g.loc['conference_board_confidence','v']:.1f} / {g.loc['conference_board_present_situation','v']:.1f} / "
                    f"{g.loc['conference_board_expectations','v']:.1f}; {nt})")
cb_note = ("Proprietary; values transcribed from official press releases, each month at the latest vintage recorded "
           "(order: confidence / present situation / expectations): " + "; ".join(cb_items) +
           ". Expectations below 80 is the Conference Board's recession-signal threshold.")
bea_dates = sorted({m.group(1) for f in obs[obs.source_id.str.startswith(("T", "A", "DSPIC", "PSAVERT", "U")) & obs.raw_file.str.startswith("BEA_")].raw_file
                    for m in [re.search(r"(\d{4}-\d{2}-\d{2})", f)] if m})
fmt_d = lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%b %-d, %Y")
bea_ret = fmt_d(bea_dates[0]) if len(bea_dates) == 1 else f"{fmt_d(bea_dates[0])} to {fmt_d(bea_dates[-1])}"
bea_note = (f"Post-annual-update vintage (BEA files retrieved {bea_ret}): BEA revised Jan 2021 onward on Sept 30. "
            f"PCE, income, saving: latest = {full_month(R['Real consumer spending (PCE), total']['period'])} 2026; "
            f"fixed investment: latest = {R['Real investment: information processing equipment']['period']}. "
            "Oct 2 refresh (hand-recorded history): Census retail sales (Sept 28 benchmark revision back to 2015, incl. 2016-19 norms), the retail revision lowers levels "
            "progressively from 2023 (Aug 2026 -4.7% vs the Sept 27 vintage), consistent with benchmarking to the annual retail survey, not a definition change), "
            "construction spending (August, Oct 1; July revised 75.2 -> 79.0), M3 (Oct 2 full report; small 1-month revisions), Conference Board (September). "
            "Pre-revision data archived in demand_data/archive/vintage_2026-09-27_pre_annual_update/; Nov 10 pre-refresh files in demand_data/archive/pre_refresh_2026-11-10/.")

_g = s("gasoline_stations"); _gt = _g.index[-1]
GAS_YOY = f"{pct(_g.iloc[-1], at(_g, _gt - pd.DateOffset(years=1))):+.0f}% y/y in {label_m(_gt)}"
NOTES = [
    ("How to read the table", ""),
    ("YoY", "Change vs. same period a year earlier (%), or change in percentage points / index points for rates and indexes (see 'Change units'). Data-center construction YoY uses 3-month averages to damp noise."),
    ("3-mo change", "Monthly flows: 3m/3m annualized = (average of latest 3 months / average of prior 3 months)^4 - 1. Used instead of your default MoM annualized because annualizing one month multiplies noise ~12x (e.g., real PCE goods: " + pce_example + "). Quarterly BEA series: BEA-published Q/Q % change at a seasonally adjusted annual rate. Hyperscaler capex: trailing-4-quarter sum y/y (company capex is not seasonally adjusted and lumpy)."),
    ("1-mo change", "Your default MoM annualized ((x_t/x_t-1)^12 - 1) for monthly flows, kept for reference; for rates/indexes, 1-month change in pp or points."),
    ("2016-19 norm", "Pre-pandemic benchmark: for growth rows, average YoY over 2016-2019; for rates/indexes, average level over 2016-2019. Blank where history is too short (capex, Conference Board)."),
    ("Units", "Nominal vs. real matters: BEA investment and PCE are real (chained 2017 $); construction, M3 orders/shipments, retail sales, capex, and credit are nominal and include price increases."),
    ("Data caveats", ""),
    ("BEA vintage", bea_note),
    ("Chained dollars", "Real components (e.g., info-processing equipment vs. equipment total) are not additive; compare growth rates, not levels."),
    ("Imports", "Much AI hardware (servers, chips) is imported; imports subtract from GDP, so investment growth overstates the net domestic demand impulse."),
    ("Data centers", "Census C30 'Office: data center' private construction, SAAR, nominal (includes construction-cost inflation). Share = data center / total private nonresidential construction."),
    ("Core capital goods", "Census M3 nondefense capital goods excluding aircraft (FRED NEWORDER, ANXAVS), nominal, SA. Shipments feed BEA equipment investment; orders lead it."),
    ("Hyperscaler capex", "Cash 'purchases of / additions to property and equipment' from SEC 10-Q/10-K XBRL (Amazon gross purchases). Quarterly values after Q1 are derived from year-to-date cash-flow totals. Calendar-quarter mapping; Microsoft FY ends June."),
    ("Microsoft break", "Microsoft cash capex jumps from $19.4B to $29.9B in calendar Q4 2025 while its separately reported finance-lease additions fall (9.1 -> 6.3 -> 4.0 -> 5.1B); consistent with a lease reclassification. Microsoft y/y growth (+110%) is overstated relative to capex including leases. Finance leases are excluded from the table total."),
    ("Capex guidance (2026, company statements)", "As of the Q2 2026 earnings statements (not updated for Q3): Microsoft ~$175B; Alphabet $195-205B; Amazon ~$220B; Meta $130-145B (incl. finance-lease principal). Sources in demand_data/processed/research/REPORT.md."),
    ("Retail control group", "Computed: retail trade ex food services (RSXFS) minus motor vehicles & parts, gasoline stations, building materials & garden. Nominal; gasoline-station sales " + GAS_YOY + " (the Oct 2 note judged the gasoline rise to be mostly price; not re-verified for the Nov refresh)."),
    ("Gasoline share", "Computed: BEA nominal PCE on gasoline & other energy goods / total nominal PCE. Direct test of the 'saving drawn down to pay for gas' idea: " + gas_chg + " of spending vs. " + sr_chg + " saving rate."),
    ("Wealth", "Fed Z.1 household & nonprofit net worth as % of disposable income (FRED HNONWPDPI), quarterly through 2026 Q2. Correlation with spending does not prove a causal wealth effect; net worth is concentrated among high-income households."),
    ("Michigan", "Index of Consumer Sentiment and components (publisher CSVs). Interviewing moved to web in 2024, a series break that may bias levels down vs. history. Record low 44.8 (May 2026). September 2026 = final reading."),
    ("Conference Board", cb_note),
    ("Revisions/timing", latest_months),
    ("Files", "Raw publisher files: demand_data/raw/; normalized series: demand_data/processed/; code: demand_data/code/ (retrieve_official.py, retrieve_research.py, supplement_research.py, build_demand_signals.py)."),
]
BANNER = "As of Oct 2, 2026 (written before the Nov refresh; not updated by the build)"
if PREV_TLDR is not None:
    t = wb.create_sheet("TLDR", 0)
    off = 0 if str(PREV_TLDR["A1"].value or "").startswith(BANNER[:30]) else 1
    if off:
        t.append([BANNER])
        t["A1"].font = Font(bold=True, size=13)
        t.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLS))
        t.row_dimensions[1].height = 20
    for row in PREV_TLDR.iter_rows():
        for c in row:
            if c.value is None and not c.has_style:
                continue
            n_ = t.cell(c.row + off, c.column, c.value)
            if c.has_style:
                n_.font, n_.fill, n_.alignment, n_.border = copy(c.font), copy(c.fill), copy(c.alignment), copy(c.border)
    for rng in PREV_TLDR.merged_cells.ranges:
        t.merge_cells(start_row=rng.min_row + off, start_column=rng.min_col, end_row=rng.max_row + off, end_column=rng.max_col)
    for r_, dim in PREV_TLDR.row_dimensions.items():
        if dim.height:
            t.row_dimensions[r_ + off].height = dim.height
    for k_, dim in PREV_TLDR.column_dimensions.items():
        if dim.width:
            t.column_dimensions[k_].width = dim.width
n = wb.create_sheet("Notes & Caveats")
n.append(["Topic", "Note"])
for c in n[1]:
    c.font, c.fill = Font(bold=True, color="FFFFFF"), NAVY
for t, v in NOTES:
    n.append([t, v])
    if not v:
        n.cell(n.max_row, 1).font, n.cell(n.max_row, 1).fill = Font(bold=True), GREY
    n.cell(n.max_row, 2).alignment = Alignment(wrap_text=True, vertical="top")
n.column_dimensions["A"].width, n.column_dimensions["B"].width = 30, 140
wb.save(OUT_DIR / "demand_signals.xlsx")
print("saved", OUT_DIR / "demand_signals.xlsx")
