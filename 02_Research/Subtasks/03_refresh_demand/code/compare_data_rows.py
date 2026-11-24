"""Compare the data-table rows (matched by indicator name) of the live workbook vs the temp rebuild,
and dump the live workbook's TLDR sheet. Run from project root."""
from openpyxl import load_workbook
P = "03_Data/pipelines/demand_data/demand_signals.xlsx"
Q = "02_Research/Subtasks/03_refresh_demand/tmp/demand_signals_rebuild_check.xlsx"
def rows(path):
    ws = load_workbook(path)["Demand Signals"]
    out, hdr = {}, False
    for r in ws.iter_rows(values_only=True):
        if r[0] == "Indicator": hdr = True; continue
        if hdr and r[1] is not None: out[r[0]] = r
    return out
a, b = rows(P), rows(Q)
print("indicators live/rebuild:", len(a), len(b), "| only in one:", set(a) ^ set(b))
d = [(k, a[k], b[k]) for k in a if k in b and a[k] != b[k]]
print("data rows differing:", len(d))
for x in d: print(x)
print("--- live TLDR sheet ---")
for r in load_workbook(P)["TLDR"].iter_rows(values_only=True): print(r)
