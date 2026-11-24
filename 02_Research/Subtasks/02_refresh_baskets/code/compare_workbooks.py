"""Compare the hand-edited Price_Basket_Findings.xlsx with the new script build, sheet by sheet.

Run from the project root:
  python3 -I "02_Research/Subtasks/02_refresh_baskets/code/compare_workbooks.py" [build.xlsx]
For each sheet: present in which file, used range, and cell-level differences against
(a) the new build and (b) a rebuild of the Oct 2 pipeline state if available. A sheet whose text
cells differ from what build_basket_workbook.py writes (beyond numbers/period labels) is flagged as
possibly hand-edited. Read-only.
"""
import sys
from pathlib import Path
import openpyxl

PI = Path("03_Data/pipelines/Price indexes")
CUR = PI / "Price_Basket_Findings.xlsx"
NEW = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(PI.glob("Price_Basket_Findings_build_*.xlsx"))[-1]


def cells(ws):
    return {(c.row, c.column): c.value for row in ws.iter_rows() for c in row if c.value not in (None, "")}


cur, new = openpyxl.load_workbook(CUR), openpyxl.load_workbook(NEW)
print("current:", CUR, cur.sheetnames)
print("build:  ", NEW, new.sheetnames)
for name in dict.fromkeys(cur.sheetnames + new.sheetnames):
    a = cells(cur[name]) if name in cur.sheetnames else None
    b = cells(new[name]) if name in new.sheetnames else None
    if a is None or b is None:
        print(f"\n[{name}] only in {'build' if a is None else 'current'}; "
              f"{'' if a is None else f'current dims {cur[name].dimensions}, {len(a)} non-empty cells'}")
        if a is not None:
            for k, v in list(a.items())[:40]:
                print("   ", k, str(v)[:150])
        continue
    diff = [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
    txt = [(k, x, y) for k, x, y in diff if isinstance(x, str) or isinstance(y, str)]
    num = len(diff) - len(txt)
    print(f"\n[{name}] current {cur[name].dimensions} ({len(a)} cells) | build {new[name].dimensions} ({len(b)} cells) | "
          f"diffs: {len(diff)} ({num} numeric-only, {len(txt)} involving text)")
    # text cells present in current but absent from build: candidates for hand edits
    only_cur_text = [(k, x) for k, x, y in txt if x is not None and y is None]
    for k, x in only_cur_text[:15]:
        print(f"    current-only text {k}: {str(x)[:160]}")
    fills = {(c.row, c.column) for row in cur[name].iter_rows() for c in row if c.comment}
    if fills:
        print("    cells with comments in current:", sorted(fills)[:10])
