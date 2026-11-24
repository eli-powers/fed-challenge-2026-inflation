"""PPI October 2026 view: pull October PPI through the pipeline's own retrieve_ppi(), write it to SEPARATE files, and
build a one-sheet workbook "PPI Oct 2026 views" in the style of the "CPI Oct 2026 views" tab.

Run from the project root:
    python3 "03_Data/pipelines/Price indexes/code/ppi_oct_2026_view.py"

Why separate files: the existing "PPI" tab and PPI/processed/components.csv stay at their current vintage (Eli, Nov 13:
new tab only). This script calls retrieve_bls_baskets.retrieve_ppi() unchanged, with PPI_LATEST = "2026-10" and its
three output writes redirected:
    PPI/processed/components.csv      -> PPI/processed/components_2026-10.csv
    PPI/processed/reconciliation.csv  -> PPI/processed/reconciliation_2026-10.csv
    PPI/processed/named_series.csv    -> PPI/processed/named_series_2026-10.csv
    PPI/processed/REPORT.md           -> PPI/processed/REPORT_2026-10.md
New raw BLS files are saved with today's date in PPI/raw/; existing raw files are never edited.
Then it computes movers and breadth and writes Price_Basket_Findings_build_ppi_oct_2026-11-13.xlsx (one sheet).
The hand-edited workbook is changed only by replace_sheets.py.
"""
import re
import sys
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

CODE = Path(__file__).resolve().parent
ROOT = CODE.parent
sys.path.insert(0, str(CODE))
sys.dont_write_bytecode = True
import retrieve_bls_baskets as rbb  # noqa: E402  (main() is guarded; importing runs nothing)

P = ROOT / "PPI" / "processed"
REDIRECT = {"components.csv": "components_2026-10.csv", "reconciliation.csv": "reconciliation_2026-10.csv",
            "named_series.csv": "named_series_2026-10.csv", "REPORT.md": "REPORT_2026-10.md"}
_orig_write, _orig_report = rbb.write_csv, rbb.report


def _redir(path):
    path = Path(path)
    if path.parent.resolve() == P.resolve() and path.name in REDIRECT:
        return path.with_name(REDIRECT[path.name])
    raise RuntimeError(f"unexpected write outside the redirected PPI files: {path}")


rbb.write_csv = lambda path, rows, columns=None: _orig_write(_redir(path), rows, columns)
rbb.report = lambda path, title, lines: _orig_report(_redir(path), title + " (October 2026 view)",
                                                     [l for l in lines if not l.startswith("Reconciliation gaps above")]
                                                     + ["Reconciliation gaps: see reconciliation_2026-10.csv (the September REPORT.md "
                                                        "sentence on gaps is September-specific and omitted here)."])
rbb.PPI_LATEST = "2026-10"
# Relative-importance tables: the pipeline's PPI_RI_YEAR tables (2026 tables = December 2025 weights since Nov 14, 2026;
# were the 2025 tables / December 2024). BLS sometimes blocks script downloads of these workbooks, so if no copy dated today
# exists, use the most recent saved copy of the same table year (same file, only the retrieval date differs).
_orig_raw_path = rbb.raw_path


def _raw_path(folder, filename):
    tag = f"_relative_importance_{rbb.PPI_RI_YEAR}_"
    p = _orig_raw_path(folder, filename)
    if tag in filename and filename.endswith(f"_{rbb.TODAY}.xlsx") and not p.exists():
        saved = sorted(p.parent.glob(filename.replace(f"_{rbb.TODAY}.xlsx", "_*.xlsx")))
        if saved:
            return saved[-1]
    return p


rbb.raw_path = _raw_path
before = {p.name: p.stat().st_mtime for p in P.glob("*")}
rbb.retrieve_ppi()
for name, mt in before.items():
    if name not in REDIRECT.values():
        assert (P / name).stat().st_mtime == mt, f"{name} was modified"

# ------------------------------------------------------------------------------------------------ analysis
TAGS = [  # verbatim from analyze_baskets.py
    ("Energy", r"\bfuels?\b|lubricants|gasoline|motor fuel|fuel oil|electricity|natural gas|utility gas|propane|energy|diesel|jet fuel|electric power|household fuels"),
    ("Energy spillover", r"air transport|airline|freight|delivery|postage|postal|moving|truck transportation|intercity|railway|water transportation|"
                         r"road transportation|public transportation|courier|motor vehicle rental|car and truck rental|transportation of|warehousing"),
    ("AI", r"software|computer|electronic components|semiconductor|data processing|hosting|information processing|telephone hardware|"
           r"telephone and related communication|video equipment|smart home"),
    ("Asset-price", r"portfolio|financial service charges|securities|commissions|investment advice|trust, fiduciary"),
]


def tag(name):
    n = re.sub(r"\b(less|excluding|except)\b.*$", "", str(name).lower())
    return ", ".join(t for t, pat in TAGS if re.search(pat, n)) or ""


def direction(a, b):  # analyze_baskets.direction
    if pd.isna(a) or pd.isna(b):
        return "n/a"
    return "Accelerating" if a > b + 1 else "Easing" if a < b - 1 else "Steady"


def clean_name(s):  # BLS catalog titles start "PPI Commodity data for ..."; drop the prefix and suffixes for display
    s = re.sub(r"^PPI Commodity data for ", "", str(s))
    s = re.sub(r"^(Final demand|Intermediate demand by commodity type)-", "", s)
    return re.sub(r", (seasonally adjusted|not seasonally adjusted)$", "", s)


num = ["weight_latest", "weight_base_12m", "weight_base_3m", "weight_base_1m", "pct_1m_calc", "pct_3m_ann_calc", "pct_12m_calc",
       "contrib_1m_calc", "contrib_3m_ann_calc", "contrib_12m_calc", "avg_pct_12m_2018_19_calc"]
oc = pd.read_csv(P / "components_2026-10.csv")
sp = pd.read_csv(P / "components.csv")          # September 2026 (unchanged pipeline file)
for d in (oc, sp):
    for c in num:
        d[c] = pd.to_numeric(d[c], errors="coerce")
oc["name"] = oc.component_name.map(clean_name)
oc["flag"] = oc.component_name.map(tag)
oc["direction"] = [direction(a, b) for a, b in zip(oc.pct_3m_ann_calc, oc.pct_12m_calc)]
oc.to_csv(P / "ppi_oct_2026_view_components.csv", index=False)
rec = pd.read_csv(P / "reconciliation_2026-10.csv")
for c in ("published_change", "component_contributions_calc", "gap_pp_calc"):
    rec[c] = pd.to_numeric(rec[c], errors="coerce")

SHORT = {"PPI Final Demand": "Final demand (FD4)", "PPI Intermediate Demand ID61": "ID61 processed",
         "PPI Intermediate Demand ID62": "ID62 unprocessed", "PPI Intermediate Demand ID63": "ID63 services"}
LBL = {"PPI Final Demand": "PPI final demand", "PPI Intermediate Demand ID61": "PPI intermediate: processed goods",
       "PPI Intermediate Demand ID62": "PPI intermediate: unprocessed goods", "PPI Intermediate Demand ID63": "PPI intermediate: services"}

# ------------------------------------------------------------------------------------------------ sheet (helpers copied from build_basket_workbook.py)
NAVY, GREY = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
wb = Workbook()
ws = wb.active
ws.title = "PPI Oct 2026 views"


def title(ws, text, size=14):
    ws.append([text]); ws.cell(ws.max_row, 1).font = Font(bold=True, size=size)


def section(ws, text, ncol):
    ws.append([text]); r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).font, ws.cell(r, 1).fill = Font(bold=True), GREY


def table(ws, header, rows):
    ws.append(header)
    for c in ws[ws.max_row]:
        c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), NAVY, Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in r])
        for c in ws[ws.max_row]:
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            if isinstance(c.value, float):
                c.number_format = "0.00"
    ws.append([])


def widths(ws, w):
    for i, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(i)].width = x


def para(ws, text, ncol, height=30):
    ws.append([text]); r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = height


NC = 10
title(ws, "PPI October 2026 — published data (BLS release Nov 13, 2026)")
para(ws, "Published BLS PPI data. Unlike CPI, BLS collected October 2025 PPI, so 12-month changes are published, not approximated. "
         "Components are the terminal codes of BLS's final-demand (FD4) and intermediate-demand (ID61 processed goods, ID62 unprocessed goods, "
         "ID63 services) systems. Weights are BLS's " + rbb._mlabel(rbb.PPI_RI_BASE) + " relative importances (" + rbb.PPI_RI_YEAR + " tables, posted 06/11/2026), repriced to each date by component vs aggregate NSA "
         "relatives and normalized within each basket at the start of each horizon (same method as the PPI tab, which still uses the December 2024 base). 1m and 3m use SA series where "
         "BLS publishes them, otherwise NSA; 12m uses NSA. Contributions = start-of-horizon weight x component change; summing annualized "
         "component rates overstates the annualized aggregate when components swing (see the gaps). Trade services measure retailer and "
         "wholesaler margins, not prices of goods. Flags are name-based screening tags (Energy spillover = transport/delivery categories potentially exposed to fuel costs), not a causal attribution. The PPI tab elsewhere in this workbook is unchanged and still shows August 2026.", NC, 105)

section(ws, "Published aggregates, Oct 2026 (index calc from BLS API; 1m/3m SA, 12m NSA)", NC)
table(ws, ["Aggregate", "Horizon", "Rate %", "Sum of component contributions (pp)", "Gap (pp)", "Basis"],
      [[SHORT[r.aggregate], r.horizon, r.published_change, r.component_contributions_calc, r.gap_pp_calc, "published indexes"]
       for r in rec.itertuples()])

HDR = ["Rank", "Component", "Flag", "Weight now %", "Weight at start of 1m %", "1m %", "1m contribution (pp)", "3m ann. %",
       "3m ann. contribution (pp)", "Source ID"]


def row1(lab, r):
    return [lab, r.name, r.flag, r.weight_latest, r.weight_base_1m, r.pct_1m_calc, r.contrib_1m_calc, r.pct_3m_ann_calc,
            r.contrib_3m_ann_calc, r.component_id]


fd = oc[oc.index_name == "PPI Final Demand"].dropna(subset=["contrib_1m_calc"])
section(ws, "PPI final demand: top movers by 1m contribution, Oct 2026 (published data) — the largest drivers of the October m/m change", NC)
table(ws, HDR, [row1(f"Up #{k}", r) for k, r in enumerate(fd.sort_values("contrib_1m_calc", ascending=False).head(5).itertuples(), 1)]
      + [row1(f"Down #{k}" if r.contrib_1m_calc < 0 else f"Bottom #{k} (positive)", r)
         for k, r in enumerate(fd.sort_values("contrib_1m_calc").head(5).itertuples(), 1)])

for idx in ("PPI Intermediate Demand ID61", "PPI Intermediate Demand ID62", "PPI Intermediate Demand ID63"):
    g = oc[oc.index_name == idx].dropna(subset=["contrib_1m_calc"]).sort_values("contrib_1m_calc", ascending=False)
    section(ws, f"{LBL[idx]}: all components ranked by 1m contribution, Oct 2026 (published data)", NC)
    table(ws, HDR, [row1(f"#{k}", r) for k, r in enumerate(g.itertuples(), 1)])

H12 = ["Rank", "Component", "Flag", "Weight now %", "Weight at start of 12m %", "12m %", "12m contribution (pp)", "3m ann. %",
       "3-mo direction", "Source ID"]
fd12 = oc[oc.index_name == "PPI Final Demand"].dropna(subset=["contrib_12m_calc"])
section(ws, "PPI final demand: top movers by 12m contribution, Oct 2026 (published data)", NC)
def lab_of(side, k, c):  # R1-F01: an ascending-tail row is "Down" only if its contribution is negative
    return f"Up #{k}" if side == "Up" else (f"Down #{k}" if c < 0 else f"Bottom #{k} (positive)")


table(ws, H12, [[lab_of(side, k, r.contrib_12m_calc), r.name, r.flag, r.weight_latest, r.weight_base_12m, r.pct_12m_calc, r.contrib_12m_calc,
                 r.pct_3m_ann_calc, r.direction, r.component_id]
                for side, sub in (("Up", fd12.sort_values("contrib_12m_calc", ascending=False).head(5)), ("Down", fd12.sort_values("contrib_12m_calc").head(5)))
                for k, r in enumerate(sub.itertuples(), 1)])


def br(d, idx, rate, wcol, thr=3.0, vs_avg=False):
    g = d[(d.index_name == idx) & d[rate].notna() & d[wcol].notna()]
    if vs_avg:
        g = g[g.avg_pct_12m_2018_19_calc.notna()]
        return 100 * g.loc[g[rate] > g.avg_pct_12m_2018_19_calc, wcol].sum() / g[wcol].sum()
    return 100 * g.loc[g[rate] > thr, wcol].sum() / g[wcol].sum()


section(ws, "Breadth, Oct 2026: share of weight with price growth above thresholds (calculated, published data)", NC)
table(ws, ["Index", "% of weight >3% 3m ann. (12m-base weights)", "% >3% 3m ann. (3m-base weights)", "% of weight >3% y/y (12m-base weights)",
           "% above own 2018-19 avg y/y (12m-base weights)"],
      [[SHORT[i], br(oc, i, "pct_3m_ann_calc", "weight_base_12m"), br(oc, i, "pct_3m_ann_calc", "weight_base_3m"),
        br(oc, i, "pct_12m_calc", "weight_base_12m"), br(oc, i, "pct_12m_calc", "weight_base_12m", vs_avg=True)] for i in LBL])
section(ws, "3m breadth, Sep vs Oct 2026: % of weight >3% 3m ann., 3m-base weights in each column (calculated). September keeps the December 2024 RI base; October uses December 2025, so the change mixes prices and a weight-base switch (the switch alone moves October by -0.14 to +0.63 pp)", NC)
table(ws, ["Index", "Sep 2026 (published; pipeline PPI file refreshed Nov 10; Dec 2024 RI)", "Oct 2026 (published; Dec 2025 RI)"],
      [[SHORT[i], br(sp, i, "pct_3m_ann_calc", "weight_base_3m"), br(oc, i, "pct_3m_ann_calc", "weight_base_3m")] for i in LBL])
widths(ws, [16, 52, 16, 12, 14, 10, 14, 10, 14, 30])
for row in ws.iter_rows(min_row=3):  # wrap component names and labels (R1-F02)
    for c in row[:2]:
        if isinstance(c.value, str) and c.coordinate not in ws.merged_cells:
            c.alignment = Alignment(wrap_text=True, vertical="top")

out = ROOT / "Price_Basket_Findings_build_ppi_oct_2026-11-13.xlsx"
wb.save(out)
print("saved", out)
print(rec[["aggregate", "horizon", "published_change", "component_contributions_calc", "gap_pp_calc"]].to_string(index=False))
