"""Replace selected sheets of the user's workbook with freshly built ones, keeping all other sheets
(and any hand edits on them) untouched. Usage: python replace_sheets.py <target.xlsx> <new_build.xlsx> <sheet1> <sheet2> ..."""
import sys
from copy import copy

import openpyxl

target, source, names = sys.argv[1], sys.argv[2], sys.argv[3:]
T, S = openpyxl.load_workbook(target), openpyxl.load_workbook(source)
order = T.sheetnames[:]
for name in names:
    src = S[name]
    idx = order.index(name) if name in order else len(T.sheetnames)
    if name in T.sheetnames:
        del T[name]
    dst = T.create_sheet(name, idx)
    for row in src.iter_rows():
        for c in row:
            d = dst.cell(row=c.row, column=c.column, value=c.value)
            if c.has_style:
                d.font, d.fill, d.border = copy(c.font), copy(c.fill), copy(c.border)
                d.alignment, d.number_format = copy(c.alignment), c.number_format
    for rng in src.merged_cells.ranges:
        dst.merge_cells(str(rng))
    for k, dim in src.column_dimensions.items():
        dst.column_dimensions[k].width = dim.width
    for k, dim in src.row_dimensions.items():
        if dim.height:
            dst.row_dimensions[k].height = dim.height
    dst.freeze_panes = src.freeze_panes
    if src.auto_filter.ref:
        dst.auto_filter.ref = src.auto_filter.ref
assert T.sheetnames == order + [n for n in names if n not in order], (T.sheetnames, order)  # existing order kept; new sheets appended (2026-11-10)
T.save(target)
print("replaced:", names, "| kept:", [n for n in order if n not in names])
