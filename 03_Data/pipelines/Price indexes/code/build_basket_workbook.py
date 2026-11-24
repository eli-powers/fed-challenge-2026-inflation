"""Build Price indexes/Price_Basket_Findings.xlsx from processed outputs (run analyze_baskets.py first)."""
import json
import re
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / "Cross-index analysis" / "processed"
FINDINGS = json.loads((ROOT / "code" / "findings_text.json").read_text())
movers = pd.read_csv(X / "movers_top5.csv")
flagged = pd.read_csv(X / "flagged_items.csv")
baskets = pd.read_csv(X / "hypothesis_baskets.csv")
drill = pd.read_csv(X / "pce_drilldown.csv")
breadth = pd.read_csv(X / "breadth.csv")
wedge = pd.read_csv(X / "cpi_pce_wedge_bea_9_1U.csv")
named = pd.read_csv(X / "ppi_named_series_tagged.csv")
cov = pd.read_csv(X / "index_coverage.csv")
tails = pd.read_csv(ROOT / "Trimmed mean" / "processed" / "trimmed_tails.csv")
dallas = pd.read_csv(ROOT / "Trimmed mean" / "processed" / "dallas_trimmed_mean_rates.csv")
sticky = pd.read_csv(ROOT / "Sticky CPI" / "processed" / "sticky_cpi_rates.csv")


def rec(folder, name, horizon):
    r = pd.read_csv(ROOT / folder / "processed" / "reconciliation.csv")
    r = r[(r.iloc[:, 0] == name) & (r.iloc[:, 2 if folder in ("CPI", "PPI") else 1].astype(str).str.contains(horizon, regex=False))]
    col = "published_change" if "published_change" in r else "publisher_aggregate_pct_change"
    return float(r[col].iloc[0]) if len(r) else None


CPI_LBL, PPI_LBL, CLE_ATL_LBL = "Sep 2026", "Sep 2026", "Oct 2026"  # refresh 2026-11-10 (was "Aug 2026" literals)
HEAD = {  # published aggregate rates (from each folder's reconciliation.csv, i.e., publisher index data)
    "CPI headline": ("CPI", "CPI-U headline", CPI_LBL), "CPI core": ("CPI", "CPI-U core", CPI_LBL),
    "PPI final demand": ("PPI", "PPI Final Demand", PPI_LBL), "PPI intermediate: processed goods": ("PPI", "PPI Intermediate Demand ID61", PPI_LBL),
    "PPI intermediate: unprocessed goods": ("PPI", "PPI Intermediate Demand ID62", PPI_LBL), "PPI intermediate: services": ("PPI", "PPI Intermediate Demand ID63", PPI_LBL),
}
rates = {k: (rec(f, n, "12m"), rec(f, n, "3m"), p) for k, (f, n, p) in HEAD.items()}
# Supercore: BEA NIPA T20804 line 28 (PCE services excluding energy and housing), computed from the saved BEA index
_t20804 = sorted((ROOT / "PCE" / "raw").glob("BEA_NIPA_T20804_*.json"), key=lambda f: re.findall(r"\d{4}-\d{2}-\d{2}", f.name)[-1])[-1]
_d = json.load(open(_t20804))["BEAAPI"]["Results"]["Data"]
_px = {r["TimePeriod"]: float(r["DataValue"].replace(",", "")) for r in _d if r["LineNumber"] == "28"}
_t = max(_px)
_y, _m = int(_t[:4]), int(_t[5:])
_lag = lambda k: f"{_y - (1 if _m - k <= 0 else 0)}M{(_m - k - 1) % 12 + 1:02d}"
# Market-based PCE rates straight from BEA T20804 lines 30 (headline) and 31 (core)
_MON = __import__("calendar").month_abbr
PCE_LABEL = f"{_MON[int(_t[5:])]} {_t[:4]}"
for _lab, _line in (("PCE headline", "1"), ("PCE core", "25"), ("Market-based PCE headline", "30"), ("Market-based PCE core", "31")):
    _q = {r["TimePeriod"]: float(r["DataValue"].replace(",", "")) for r in _d if r["LineNumber"] == _line}
    rates[_lab] = ((_q[_t] / _q[_lag(12)] - 1) * 100, ((_q[_t] / _q[_lag(3)]) ** 4 - 1) * 100, PCE_LABEL)
rates["PCE supercore (services ex energy & housing)"] = ((_px[_t] / _px[_lag(12)] - 1) * 100, ((_px[_t] / _px[_lag(3)]) ** 4 - 1) * 100, PCE_LABEL)
_ORDER = ["CPI headline", "CPI core", "PCE headline", "PCE core", "PCE supercore (services ex energy & housing)", "Market-based PCE headline",
          "Market-based PCE core", "PPI final demand", "PPI intermediate: processed goods", "PPI intermediate: unprocessed goods", "PPI intermediate: services"]
rates = {k: rates[k] for k in _ORDER}

NAVY, GREY, YEL = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="D9E1F2"), PatternFill("solid", fgColor="FFF2CC")
thin = Side(style="thin", color="BFBFBF")
wb = Workbook()


def title(ws, text, size=14):
    ws.append([text])
    ws.cell(ws.max_row, 1).font = Font(bold=True, size=size)


def section(ws, text, ncol):
    ws.append([text])
    r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).font, ws.cell(r, 1).fill = Font(bold=True), GREY


def table(ws, header, rows, hl_col=None):
    ws.append(header)
    for c in ws[ws.max_row]:
        c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), NAVY, Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in r])
        for c in ws[ws.max_row]:
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            if isinstance(c.value, float):
                c.number_format = "0.00"
        if hl_col is not None and r[hl_col]:
            for c in ws[ws.max_row]:
                c.fill = YEL
    ws.append([])


def widths(ws, w):
    for i, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(i)].width = x


def para(ws, text, ncol, height=30):
    ws.append([text])
    r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = height


NOTES_HDR, CUR_HDR = "Notes as of Aug 2026 data (Oct 2 workbook)", "Current notes"


def notes_block(ws, notes, ncol, height=30, prefix=""):
    """findings_text.json notes, verbatim, under NOTES_HDR, with an empty CUR_HDR column right of them for Eli (added 2026-11-10)."""
    ws.append([NOTES_HDR])
    r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).font, ws.cell(r, 1).fill = Font(bold=True), GREY
    ws.cell(r, ncol + 1, CUR_HDR).font, ws.cell(r, ncol + 1).fill = Font(bold=True), GREY
    ws.column_dimensions[get_column_letter(ncol + 1)].width = 60
    for n in notes:
        para(ws, prefix + n, ncol, height)
        ws.cell(ws.max_row, ncol + 1).alignment = Alignment(wrap_text=True, vertical="top")


MOVER_HDR = ["Rank", "Component", "Flag", "Weight now (% of index)", "Weight at start of 12m (%)", "12m %", "12m contribution (pp)", "3m ann. %", "3m ann. contribution (pp)",
             "3-mo direction", "Excess vs 2018-19 (pp)", "Source ID"]


def mover_rows(idx):
    g = movers[movers["index"] == idx]
    out = []
    for side in ["Top 5 upward", "Top 5 downward"]:
        if g[g.side == side].empty:
            out.append([side, f"None: no component had a {'positive' if 'up' in side else 'negative'} 12-month contribution"] + [None] * 10)
        for r in g[g.side == side].itertuples():
            out.append([f"{'Up' if 'up' in side else 'Down'} #{r.rank}", r.component_name, r.tag if isinstance(r.tag, str) else "", r.weight_pct, r.weight_base_pct, r.pct_12m_calc, r.contrib_12m_calc,
                        r.pct_3m_ann_calc, r.contrib_3m_ann_calc, r.direction, r.excess_contrib_12m_calc, r.component_id])
    return out


def flag_rows(idx):
    return [["", r.component_name, r.tag, r.weight_pct, r.weight_base_pct, r.pct_12m_calc, r.contrib_12m_calc, r.pct_3m_ann_calc, r.contrib_3m_ann_calc, r.direction,
             r.excess_contrib_12m_calc, r.component_id] for r in flagged[flagged["index"] == idx].itertuples()]


# ------------------------------------------------------------------ Summary
ws = wb.active
ws.title = "Summary"
title(ws, f"What's driving U.S. price indexes — basket movers (CPI {CPI_LBL}; PPI {PPI_LBL}; PCE {PCE_LABEL}, post-Sept 30 2026 annual-update vintage)")
section(ws, "Key findings", 9)
notes_block(ws, FINDINGS["key"], 9, 48, prefix="• ")
ws.append([])
section(ws, "By index: published rate and biggest movers (12-month contribution, pp; weight = % of index)", 9)
table(ws, ["Index", "Latest", "12m %", "3m ann. %", "Top upward movers", "Top downward movers", NOTES_HDR, CUR_HDR],
      [[k, v[2], v[0], v[1],
        "; ".join(f"{r.component_name} ({r.weight_pct:.2f}% wt, {r.contrib_12m_calc:+.2f})" for r in movers[(movers["index"] == k) & (movers.side == "Top 5 upward")].head(3).itertuples()),
        "; ".join(f"{r.component_name} ({r.weight_pct:.2f}% wt, {r.contrib_12m_calc:+.2f})" for r in movers[(movers["index"] == k) & (movers.side == "Top 5 downward")].head(3).itertuples()),
        FINDINGS["index"].get(k, ""), None] for k, v in rates.items()])
for row in ws.iter_rows(min_row=ws.max_row - len(rates), max_row=ws.max_row):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
widths(ws, [30, 10, 8, 10, 60, 60, 70, 60, 10])
para(ws, "Flags: Energy = direct energy items; Energy spillover = transport/delivery services exposed to fuel costs; AI = computers, software, electronics, "
         "chips, hosting, capital equipment; Asset-price = financial services priced off asset values. Contributions = weight x component change (calculated; "
         "see Sources for reconciliation to published totals).", 9, 45)

# ------------------------------------------------------------- index sheets
def index_sheet(name, idxs, notes):
    ws = wb.create_sheet(name)
    title(ws, name + " — top movers and flagged items")
    notes_block(ws, notes, 12, 32)
    for idx in idxs:
        r = rates[idx]
        section(ws, f"{idx}: {r[0]:.2f}% 12m, {r[1]:.2f}% 3m ann. ({r[2]})", 12)
        table(ws, MOVER_HDR, mover_rows(idx))
        fr = flag_rows(idx)
        if fr:
            ws.append([f"Flagged AI / Energy / Asset-price items not in the top 5 ({idx})"])
            ws.cell(ws.max_row, 1).font = Font(italic=True, bold=True)
            table(ws, MOVER_HDR, fr)
    widths(ws, [13, 52, 16, 11, 11, 9, 13, 10, 13, 13, 12, 34])
    return ws


index_sheet("CPI", ["CPI headline", "CPI core"], FINDINGS["sheet"]["CPI"])
ws = index_sheet("PPI", ["PPI final demand", "PPI intermediate: processed goods", "PPI intermediate: unprocessed goods", "PPI intermediate: services"],
                 FINDINGS["sheet"]["PPI"])
section(ws, "Named PPI series tied to the hypotheses (calculated from BLS indexes; NSA)", 11)
table(ws, ["Series", "BLS ID", "Flag", "1m %", "3m ann. %", "12m %", "Latest"],
      [[r.requested_name, r.component_id, r.tag, r.pct_1m_calc, r.pct_3m_ann_calc, r.pct_12m_calc, r.latest_period] for r in named.itertuples()])
ws = index_sheet("PCE", ["PCE headline", "PCE core"], FINDINGS["sheet"]["PCE"])
section(ws, "Drill-down: lines inside the movers (BEA underlying detail; calculated)", 11)
table(ws, ["BEA line", "Component", "Flag", "Weight % of PCE", "Weight % of core", "12m %", "3m ann. %", "Contribution to PCE 12m (pp)", "Contribution to core 12m (pp)", "Source"],
      [[r.line, r.component, r.tag if isinstance(r.tag, str) else "", r.weight_pce_pct, r.weight_core_pct, r.pct_12m, r.pct_3m_ann, r.contrib_pce_12m, r.contrib_core_12m, r.source]
       for r in drill.itertuples()])
# ------------------------------------------------------------- PCE supercore
SC = "PCE supercore (services ex energy & housing)"
ws = index_sheet("PCE supercore", [SC], FINDINGS["sheet"]["PCE supercore"])
section(ws, "Supercore excluding asset-price-linked and airfare items (12m, weight-averaged component rates; calculated)", 12)
table(ws, [f"Measure ({NOTES_HDR}; values are Aug 2026)", "12m %", "Weight removed (% of supercore)", CUR_HDR], [list(x) + [None] for x in FINDINGS["supercore_ex"]])
wb.move_sheet("PCE supercore", offset=-(len(wb.sheetnames) - 1 - wb.sheetnames.index("PCE") - 1))

index_sheet("Market-based PCE", ["Market-based PCE headline", "Market-based PCE core"], FINDINGS["sheet"]["Market-based PCE"])

# ------------------------------------------------ trimmed mean & sticky (published only)
ws = wb.create_sheet("Trimmed & Sticky")
title(ws, "Trimmed mean and sticky CPI — published data only (no reconstruction)")
notes_block(ws, FINDINGS["sheet"]["Trimmed & Sticky"], 8, 32)
section(ws, f"Cleveland Fed 16% trimmed-mean CPI: components in the trimmed tails, {CLE_ATL_LBL} (published 1-month annualized changes)", 8)
table(ws, ["Component", "Tail", "1m ann. % (published)", "Weight % (published)", "Cumulative weight %", "Source"],
      [[r.component, r.tail, r.published_1m_annualized_pct, r.published_weight_normalized_pct, r.published_cumulative_weight_pct, r.source_ids] for r in tails.itertuples()])
section(ws, "Dallas Fed trimmed mean PCE (published rates)", 8)
table(ws, ["Series", "Measure", "Period", "Value %", "Publisher"], [[r.series_id, r.measure, r.period, r.value, r.publisher] for r in dallas.itertuples()])
_dt = pd.read_csv(ROOT / "Trimmed mean" / "processed" / "dallas_trimmed_components_published.csv")
section(ws, "Dallas Fed trimmed mean PCE: components cut and kept this month (published; trim status as color-coded by Dallas)", 8)
table(ws, ["Publisher status", "Components", "Total weight %"],
      [[k, len(g), round(g.published_weight_pct.sum(), 2)] for k, g in _dt.groupby("publisher_status", sort=False)])
for _st in ["Cut from top", "Cut from bottom"]:
    _g = _dt[_dt.publisher_status == _st].nlargest(10, "published_weight_pct")
    ws.append([f"{_st}: 10 largest-weight components (published 1-month annualized change)"])
    ws.cell(ws.max_row, 1).font = Font(italic=True, bold=True)
    table(ws, ["Component", "1m ann. % (published)", "Weight % (published)", "Cumulative weight %", "Source"],
          [[r.component, r.published_1m_annualized_pct, r.published_weight_pct, r.published_cumulative_weight_pct, r.raw_file] for r in _g.itertuples()])
section(ws, f"Atlanta Fed sticky/flexible CPI (published rates, {CLE_ATL_LBL})", 8)
table(ws, ["Series", "1m ann. %", "3m ann. %", "12m %", "Source"],
      [[r.series, r._3, r._4, r._5, r.source_ids] for r in sticky.itertuples()])
widths(ws, [34, 12, 14, 14, 14, 40, 10, 10])

# ------------------------------------------------------ hypothesis analysis
ws = wb.create_sheet("Hypothesis analysis")
title(ws, "Hypothesis analysis — energy spillover, AI, asset-price measurement, CPI-PCE gap, breadth")
notes_block(ws, FINDINGS["sheet"]["Hypothesis analysis"], 10, 40)
section(ws, "Baskets within core (weight-averaged component rates; calculated). Control = rest of core.", 10)
table(ws, ["Index", "Basket", "Weight % of core", "12m %", "3m ann. %", "12m contribution (pp)", "3m ann. contribution (pp)", "Control 12m %", "Control 3m ann. %", "Items"],
      [[r.index, r.basket, r.weight_share_pct, r.pct_12m, r.pct_3m_ann, r.contrib_12m, r.contrib_3m_ann, r.control_pct_12m, r.control_pct_3m_ann, r.items] for r in baskets.itertuples()])
section(ws, f"CPI vs PCE: BEA's published reconciliation (Table 9.1U, headline), summed {wedge.period.iloc[0]} (Oct/Nov 2025 CPI not published)", 10)
table(ws, ["Line", "Item", "Sum, pp"], [[r.LineNumber, r.LineDescription, r.sum_pp] for r in wedge.itertuples()])
section(ws, "Breadth: share of basket weight with price growth above thresholds (calculated)", 10)
table(ws, ["Index", "% of weight >3% y/y", "% of weight >3% 3m ann.", "% of weight above own 2018-19 avg"],
      [[r.index, r.share_weight_12m_above_3, r.share_weight_3m_ann_above_3, r.share_weight_12m_above_2018_19_avg] for r in breadth.itertuples()])
widths(ws, [14, 60, 14, 10, 10, 14, 14, 12, 12, 80])

# -------------------------------------------------------------- Sources
ws = wb.create_sheet("Sources")
title(ws, "Sources, methods, and reconciliation")
notes_block(ws, FINDINGS["sources"], 6, 45)
section(ws, "Coverage and reconciliation (sum of component contributions vs published change)", 6)
table(ws, ["Index", "Components with data", "Weight covered %", "Sum of 12m contributions (pp)", "Published 12m %", "Gap (pp)"],
      [[r.index, r.n_components, r.weight_covered_pct, r.sum_contrib_12m, rates[r.index][0], rates[r.index][0] - r.sum_contrib_12m] for r in cov.itertuples()])
widths(ws, [34, 14, 14, 18, 14, 10])
# ------------------------------------------- CPI Oct 2026 views (added 2026-11-10; new sheet, others unchanged)
_cp = ROOT / "CPI" / "processed"
if (X / "cpi_movers_2026-10_short_horizon.csv").exists():
    APPROX = "approx., interpolated Oct 2025 base"
    ws = wb.create_sheet("CPI Oct 2026 views")
    title(ws, "CPI October 2026 — short-horizon view (published data) and approximate 12m (" + APPROX + ")")
    para(ws, "BLS did not collect October 2025 CPI, so BLS publishes no Oct 2026 12-month changes for most series. Short-horizon figures use "
             "published BLS indexes only. Approx. 12m figures use Oct 2025 = sqrt(Sep 2025 x Nov 2025) on NSA indexes (the geometric-mean "
             "approximation BLS describes for seasonal adjustment); 11- and 13-month changes on the published Nov 2025 and Sep 2025 bases are shown as endpoint sensitivity comparisons, not bounds (October NSA levels often lie outside the Sep-Nov range). "
             "The official CPI basket elsewhere in this workbook stays at Sep 2026.", 10, 60)
    _rs = pd.read_csv(_cp / "reconciliation_2026-10_short_horizon.csv")
    _ra = pd.read_csv(_cp / "reconciliation_2026-10_approx_interp_oct2025_base.csv")
    section(ws, "Published aggregates, Oct 2026 (index calc from BLS API; 1m/3m SA, 12m NSA)", 10)
    table(ws, ["Aggregate", "Horizon", "Rate %", "Sum of component contributions (pp)", "Gap (pp)", "Basis"],
          [[r.aggregate, r.horizon, r.published_change, r.component_contributions_calc, r.gap_pp_calc, "published indexes"] for r in _rs[~_rs.horizon.str.startswith("12m")].itertuples()]
          + [[r.aggregate, r.horizon, r.published_change, r.component_contributions_calc, r.gap_pp_calc,
              APPROX if r.horizon.startswith("12m") else "published NSA endpoints (sensitivity comparison, not a bound)"]
             for r in _ra[_ra.horizon.str.match(r"(?:12m|(?:11|13)-month change)")].itertuples()])
    _ms = pd.read_csv(X / "cpi_movers_2026-10_short_horizon.csv")
    for idx in ["CPI headline", "CPI core"]:
        section(ws, f"{idx}: top movers by 3m annualized contribution, Oct 2026 (published data)", 10)
        table(ws, ["Rank", "Component", "Flag", "Weight now %", "Weight at start of 3m %", "1m %", "1m contribution (pp)", "3m ann. %", "3m ann. contribution (pp)", "Source ID"],
              [[f"{'Up' if 'up' in r.side else 'Down'} #{r.rank}", r.component_name, r.tag if isinstance(r.tag, str) else "", r.weight_pct, r.weight_base_3m_pct, r.pct_1m_calc,
                r.contrib_1m_calc, r.pct_3m_ann_calc, r.contrib_3m_ann_calc, r.component_id] for r in _ms[_ms["index"] == idx].itertuples()])
    _ma = pd.read_csv(X / "cpi_movers_2026-10_approx_interp_oct2025_base.csv")
    for idx in ["CPI headline", "CPI core"]:
        section(ws, f"{idx}: top movers by 12m contribution, Oct 2026 ({APPROX})", 10)
        table(ws, ["Rank", "Component", "Flag", "Weight now %", "Weight at start of 12m %", "12m % (approx.)", "12m contribution (pp, approx.)", "3m ann. %", "3-mo direction", "Source ID"],
              [[f"{'Up' if 'up' in r.side else 'Down'} #{r.rank}", r.component_name, r.tag if isinstance(r.tag, str) else "", r.weight_pct, r.weight_base_pct, r.pct_12m_calc,
                r.contrib_12m_calc, r.pct_3m_ann_calc, r.direction, r.component_id] for r in _ma[_ma["index"] == idx].itertuples()])
    _bs = pd.read_csv(X / "cpi_breadth_2026-10_short_horizon.csv")
    _ba = pd.read_csv(X / "cpi_breadth_2026-10_approx_interp_oct2025_base.csv")
    section(ws, "Breadth, Oct 2026: share of weight with price growth above thresholds (calculated)", 10)
    table(ws, ["Index", "% of weight >3% 3m ann. (12m-base weights, " + APPROX + ")", "% >3% 3m ann. (3m-base weights, published)",
               "% of weight >3% y/y (" + APPROX + ")", "% above own 2018-19 avg (" + APPROX + ")"],
          [[r.index, r.share_weight_3m_ann_above_3, r.share_weight_3m_ann_above_3_w3mbase,
            _ba.set_index("index").loc[r.index, "share_weight_12m_above_3"], _ba.set_index("index").loc[r.index, "share_weight_12m_above_2018_19_avg"]] for r in _bs.itertuples()])
    _b9 = pd.read_csv(X / "cpi_breadth_2026-09_w3mbase.csv").set_index("index")
    section(ws, "3m breadth, Sep vs Oct 2026: % of weight >3% 3m ann., same weighting in each column (calculated)", 10)
    table(ws, ["Index", "Sep 2026, 3m-base weights (published)", "Oct 2026, 3m-base weights (published)",
               "Sep 2026, 12m-base weights (official breadth)", "Oct 2026, 12m-base weights (" + APPROX + ")"],
          [[r.index, _b9.loc[r.index, "share_weight_3m_ann_above_3_w3mbase"], r.share_weight_3m_ann_above_3_w3mbase,
            _b9.loc[r.index, "share_weight_3m_ann_above_3_w12mbase_official"], r.share_weight_3m_ann_above_3] for r in _bs.itertuples()])
    widths(ws, [16, 52, 16, 12, 14, 10, 14, 10, 14, 30])

# Never overwrite the hand-edited Price_Basket_Findings.xlsx: build to a separate file; replace_sheets.py moves chosen sheets.
_OUTFILE = ROOT / f"Price_Basket_Findings_build_{__import__('datetime').date.today().isoformat()}.xlsx"
wb.save(_OUTFILE)
print("saved", _OUTFILE)
