"""Preview what replace_sheets.py would change for chosen sheets, without running it.

Run from the project root:
  python3 -I "02_Research/Subtasks/02_refresh_baskets/code/replace_preview.py" <build.xlsx> Summary CPI PCE "PCE supercore" "Market-based PCE"
replace_sheets.py deletes each named sheet in the live workbook and recreates it from the build, copying cell values,
font/fill/border/alignment/number format, merged ranges, column widths, row heights, freeze panes and autofilter.
Anything else on the live sheet is lost (comments, hyperlinks, data validation, conditional formatting, images, tab color,
print settings). This script lists, per sheet: those at-risk features present on the live sheet; cell value changes
(counts by kind, plus every changed text cell); merged-range and dimension changes. Full cell diff -> CSV next to this
script's subtask folder (replace_preview_<sheet>.csv). Read-only for both workbooks.
"""
import csv
import sys
from pathlib import Path

import openpyxl

LIVE = Path("03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx")
BUILD = Path(sys.argv[1])
SHEETS = sys.argv[2:]
OUTDIR = Path("02_Research/Subtasks/02_refresh_baskets/replace_preview")
OUTDIR.mkdir(exist_ok=True)
L, B = openpyxl.load_workbook(LIVE), openpyxl.load_workbook(BUILD)


def vals(ws):
    return {(c.row, c.column): c.value for row in ws.iter_rows() for c in row if c.value not in (None, "")}


for name in SHEETS:
    lw, bw = L[name], B[name]
    print(f"\n=== {name}: live {lw.dimensions} -> build {bw.dimensions}")
    risk = {
        "comments": sum(1 for r in lw.iter_rows() for c in r if c.comment),
        "hyperlinks": sum(1 for r in lw.iter_rows() for c in r if c.hyperlink),
        "data_validations": len(lw.data_validations.dataValidation),
        "conditional_formats": len(list(lw.conditional_formatting)),
        "images": len(getattr(lw, "_images", [])),
        "charts": len(getattr(lw, "_charts", [])),
        "tab_color": bool(lw.sheet_properties.tabColor),
    }
    print("   live features replace_sheets would drop:", {k: v for k, v in risk.items() if v} or "none")
    a, b = vals(lw), vals(bw)
    rows = []
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        if x != y:
            kind = "added" if x is None else "removed" if y is None else ("number" if isinstance(x, (int, float)) and isinstance(y, (int, float)) else "text")
            rows.append(dict(cell=openpyxl.utils.get_column_letter(k[1]) + str(k[0]), kind=kind, live=x, build=y))
    with open(OUTDIR / f"replace_preview_{name.replace(' ', '_')}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["cell", "kind", "live", "build"])
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    print("   cell changes:", dict(Counter(r["kind"] for r in rows)), "of", len(set(a) | set(b)), "non-empty cells")
    ml, mb = {str(r) for r in lw.merged_cells.ranges}, {str(r) for r in bw.merged_cells.ranges}
    print(f"   merged ranges: live {len(ml)}, build {len(mb)}; removed {sorted(ml - mb)[:12]}; added {sorted(mb - ml)[:12]}")
    cw = {k: (lw.column_dimensions[k].width, bw.column_dimensions[k].width) for k in set(lw.column_dimensions) | set(bw.column_dimensions)
          if lw.column_dimensions[k].width != bw.column_dimensions[k].width}
    print("   column width changes:", dict(sorted(cw.items())) or "none", "| freeze:", lw.freeze_panes, "->", bw.freeze_panes)
    for r in rows:
        if r["kind"] in ("text", "added", "removed") and (isinstance(r["live"], str) or isinstance(r["build"], str)):
            print(f"   {r['cell']:>5} {r['kind']:7} | live: {str(r['live'])[:110]!r} | build: {str(r['build'])[:110]!r}")
