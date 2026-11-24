"""Build demand_signals.xlsx from demand_data/processed/.

Change measures (computed here from saved publisher levels unless noted):
  YoY           (x_t / x_t-12m - 1) x 100 for flows/levels; for quarterly series t-4q.
  3m/3m ann.    ((avg of latest 3 months / avg of prior 3 months)^4 - 1) x 100 — monthly flows.
  MoM ann.      ((x_t / x_t-1)^12 - 1) x 100 — monthly flows (shown for completeness; noisy).
  Q/Q SAAR      BEA-published percent change from preceding quarter at annual rate (not recomputed).
  Rates/indexes (saving rate, sentiment, spending share, net-worth ratio): changes in percentage points / index points.
"""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path("./03_Data/pipelines/demand_data")
TMP = Path("./02_Research/Subtasks/03_refresh_demand/tmp")
PROJECT = ROOT.parent
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
raw_mich = {"ICS_ALL": "Michigan_tbmics_2026-09-27.csv", "ICC": "Michigan_tbmiccice_2026-09-27.csv", "ICE": "Michigan_tbmiccice_2026-09-27.csv"}
for key, col, name in [("umich_index_of_consumer_sentiment", "ICS_ALL", "Michigan consumer sentiment"),
                       ("umich_index_of_current_economic_conditions", "ICC", "Michigan: current conditions"),
                       ("umich_index_of_consumer_expectations", "ICE", "Michigan: expectations")]:
    x = s(key)
    t = x.index[-1]
    hist = pd.read_csv(sorted((ROOT / "raw" / "official").glob(raw_mich[col].replace("2026-09-27", "*")))[-1])
    full = pd.to_numeric(hist[col], errors="coerce").dropna()
    rank = int((full < x.iloc[-1]).sum()) + 1
    add(C, f"{name} (rank: #{rank} lowest since {int(hist['YYYY'].min())})", "Univ. of Michigan", "Monthly", label_m(t),
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
df.to_csv(TMP / "demand_signals_table.csv", index=False)
print(df[["channel", "indicator", "period", "latest", "yoy", "short", "short_label", "mom", "chg_units", "baseline"]].round(2).to_string())

# ------------------------------------------------------------------ workbook
TLDR = [
    "TLDR — demand signals as of Sept 27, 2026 (BEA data are pre-Sept 30 revision vintage)",
    "AI buildout is the strongest demand impulse in the data: hyperscaler cash capex $165B in Q2 (+87% y/y); data-center construction +57% y/y to a $75B annual rate (10% of private nonresidential building); "
    "real info-processing equipment investment +22% y/y; core capital goods orders +14% y/y; semiconductor output +12% y/y (27% annualized over 3 months).",
    "But the AI impulse slowed in Q2 national accounts: info-processing equipment grew 6.9% annualized vs. 37-40% in the two prior quarters, and much of that equipment is imported (dampens domestic demand pressure).",
    "Consumers: real spending +2.1% y/y (below its 2016-19 norm of 2.5%) but re-accelerating to 3.6% annualized over 3 months, led by services (4.1%). Real disposable income is nearly flat (+0.5% y/y).",
    "Puzzle resolved in the accounting: spending outpaces income because saving fell — saving rate 3.0% (down 1.5 pp in a year; 2016-19 avg 6.2%). "
    "Household net worth jumped to 828% of income (+59 pp y/y), consistent with a wealth effect. Gasoline's share of spending rose only 0.3 pp y/y — too small to explain the saving drawdown by itself. Revolving credit growth (3.6% y/y) is below normal, so this is not credit-fueled.",
    "Sentiment is at record-low territory (Michigan 48.1, 2nd-lowest since 1952; Conference Board expectations 68.2) while spending holds up — sentiment is a weak guide to spending here.",
    "Countercase: consumer spending is only moderate on a y/y basis; saving and income data will be revised Sept 30; AI capex is nominal and includes price effects (chips, construction costs).",
]
COLS = ["Indicator", "Source", "Frequency", "Latest period", "Latest value", "Units", "YoY", "3-mo change", "3-mo measure", "1-mo change", "Change units", "2016-19 norm"]
wb = Workbook()
ws = wb.active
ws.title = "Demand Signals"
NAVY, GREY = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
ws.append([TLDR[0]])
ws["A1"].font = Font(bold=True, size=13)
for i, line in enumerate(TLDR[1:], start=2):
    ws.append(["• " + line])
    ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=len(COLS))
    ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[i].height = 46
ws.append([])
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
ws.freeze_panes = ws.cell(hdr + 1, 2)

NOTES = [
    ("How to read the table", ""),
    ("YoY", "Change vs. same period a year earlier (%), or change in percentage points / index points for rates and indexes (see 'Change units'). Data-center construction YoY uses 3-month averages to damp noise."),
    ("3-mo change", "Monthly flows: 3m/3m annualized = (average of latest 3 months / average of prior 3 months)^4 - 1. Used instead of your default MoM annualized because annualizing one month multiplies noise ~12x (e.g., real PCE goods: -7.1% MoM ann. vs +2.5% 3m/3m ann.). Quarterly BEA series: BEA-published Q/Q % change at a seasonally adjusted annual rate. Hyperscaler capex: trailing-4-quarter sum y/y (company capex is not seasonally adjusted and lumpy)."),
    ("1-mo change", "Your default MoM annualized ((x_t/x_t-1)^12 - 1) for monthly flows, kept for reference; for rates/indexes, 1-month change in pp or points."),
    ("2016-19 norm", "Pre-pandemic benchmark: for growth rows, average YoY over 2016-2019; for rates/indexes, average level over 2016-2019. Blank where history is too short (capex, Conference Board)."),
    ("Units", "Nominal vs. real matters: BEA investment and PCE are real (chained 2017 $); construction, M3 orders/shipments, retail sales, capex, and credit are nominal and include price increases."),
    ("Data caveats", ""),
    ("BEA vintage", "PCE, income, saving, and fixed investment are the pre-annual-update vintage (latest monthly = July 2026; latest quarter = 2026 Q2). BEA revises Q1 2021 onward on Sept 30, 2026 — refresh then. The saving rate is often revised substantially."),
    ("Chained dollars", "Real components (e.g., info-processing equipment vs. equipment total) are not additive; compare growth rates, not levels."),
    ("Imports", "Much AI hardware (servers, chips) is imported; imports subtract from GDP, so investment growth overstates the net domestic demand impulse."),
    ("Data centers", "Census C30 'Office: data center' private construction, SAAR, nominal (includes construction-cost inflation). Share = data center / total private nonresidential construction."),
    ("Core capital goods", "Census M3 nondefense capital goods excluding aircraft (FRED NEWORDER, ANXAVS), nominal, SA. Shipments feed BEA equipment investment; orders lead it."),
    ("Hyperscaler capex", "Cash 'purchases of / additions to property and equipment' from SEC 10-Q/10-K XBRL (Amazon gross purchases). Quarterly values after Q1 are derived from year-to-date cash-flow totals. Calendar-quarter mapping; Microsoft FY ends June."),
    ("Microsoft break", "Microsoft cash capex jumps from $19.4B to $29.9B in calendar Q4 2025 while its separately reported finance-lease additions fall (9.1 -> 6.3 -> 4.0 -> 5.1B); consistent with a lease reclassification. Microsoft y/y growth (+110%) is overstated relative to capex including leases. Finance leases are excluded from the table total."),
    ("Capex guidance (2026, company statements)", "Microsoft ~$175B; Alphabet $195-205B; Amazon ~$220B; Meta $130-145B (incl. finance-lease principal). Sources in demand_data/processed/research/REPORT.md."),
    ("Retail control group", "Computed: retail trade ex food services (RSXFS) minus motor vehicles & parts, gasoline stations, building materials & garden. Nominal; gasoline-station sales +21% y/y are mostly price."),
    ("Gasoline share", "Computed: BEA nominal PCE on gasoline & other energy goods / total nominal PCE. Direct test of the 'saving drawn down to pay for gas' idea: +0.3 pp of spending vs. -1.5 pp saving rate."),
    ("Wealth", "Fed Z.1 household & nonprofit net worth as % of disposable income (FRED HNONWPDPI), quarterly through 2026 Q2. Correlation with spending does not prove a causal wealth effect; net worth is concentrated among high-income households."),
    ("Michigan", "Index of Consumer Sentiment and components (publisher CSVs). Interviewing moved to web in 2024, a series break that may bias levels down vs. history. Record low 44.8 (May 2026). September 2026 = final reading."),
    ("Conference Board", "Proprietary; values transcribed from official press releases: Aug 2026 (89.4 / 121.2 / 68.2), July 2026 as revised in the Aug release, May 2026 and Aug 2025 original releases (later revisions not verified). Expectations below 80 is the Conference Board's recession-signal threshold. September release due Sept 29."),
    ("Revisions/timing", "Latest months differ by source (BEA July; Census/Fed August; Michigan September). Map to prices at matching dates in step 5."),
    ("Files", "Raw publisher files: demand_data/raw/; normalized series: demand_data/processed/; code: demand_data/code/ (retrieve_official.py, retrieve_research.py, supplement_research.py, build_demand_signals.py)."),
]
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
wb.save(TMP / "demand_signals_rebuild_check.xlsx")
print("saved")
