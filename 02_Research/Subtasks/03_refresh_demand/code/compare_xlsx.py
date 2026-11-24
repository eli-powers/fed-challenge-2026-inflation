"""Cell-by-cell comparison of two xlsx workbooks. Usage: python3 compare_xlsx.py A.xlsx B.xlsx"""
import sys
from openpyxl import load_workbook
a, b = load_workbook(sys.argv[1]), load_workbook(sys.argv[2])
print("sheets:", a.sheetnames, b.sheetnames)
diffs = 0
for name in sorted(set(a.sheetnames) | set(b.sheetnames)):
    if name not in a.sheetnames or name not in b.sheetnames:
        print("sheet missing in one:", name); diffs += 1; continue
    x, y = a[name], b[name]
    print(name, "dims", x.dimensions, y.dimensions, "merged equal:", sorted(map(str, x.merged_cells.ranges)) == sorted(map(str, y.merged_cells.ranges)))
    for r in range(1, max(x.max_row, y.max_row) + 1):
        for c in range(1, max(x.max_column, y.max_column) + 1):
            u, v = x.cell(r, c).value, y.cell(r, c).value
            if u != v:
                diffs += 1; print(f"DIFF {name}!{x.cell(r,c).coordinate}: {u!r} | {v!r}")
print("total cell diffs:", diffs)
