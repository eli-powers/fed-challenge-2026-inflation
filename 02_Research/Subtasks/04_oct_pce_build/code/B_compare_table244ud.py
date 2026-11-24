"""Row-by-row comparison of BEA Table 2.4.4U-D versions (source text + seasonal status).
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/B_compare_table244ud.py
Writes outputs/source_table_changes.csv (prior 2026-02-20 -> current 2026-09-30) plus extra pairs."""
import openpyxl, csv
R="03_Data/Raw/BEA_Table244UD_PCE_price_source_data_"
V={"2025-02-28":R+"2025-02-28_retrieved_2026-11-11.xlsx",
   "2026-02-20":R+"2026-02-20_retrieved_2026-11-11.xlsx",
   "2026-09-30_feb26url":R+"2026-09-30_via_Feb26_url_retrieved_2026-11-11.xlsx",
   "2026-09-30":R+"2026-11-11.xlsx"}
def load(k):
    ws=openpyxl.load_workbook(V[k],read_only=True).worksheets[0]
    d={}
    for r in ws.iter_rows(min_row=5,values_only=True):
        if r[2]: d[r[2]]=(r[0],(r[1] or "").strip(),(r[3] or "").strip() if r[3] else "",(r[4] or "").strip() if r[4] else "")
    return d
pairs=[("2026-02-20","2026-09-30"),("2025-02-28","2026-02-20"),("2026-09-30_feb26url","2026-09-30")]
rows=[]
for a,b in pairs:
    A,B=load(a),load(b)
    for code in sorted(set(A)|set(B), key=lambda c:(B.get(c) or A.get(c))[0]):
        x,y=A.get(code),B.get(code)
        if x is None or y is None:
            rows.append([a,b,code,(y or x)[0],(y or x)[1],"line added" if x is None else "line removed",x[2] if x else "",x[3] if x else "",y[2] if y else "",y[3] if y else ""]); continue
        ch=[n for n,i in (("name",1),("source",2),("seasonal",3)) if x[i]!=y[i]]
        if ch: rows.append([a,b,code,y[0],y[1],"+".join(ch),x[2],x[3],y[2],y[3]])
with open("02_Research/Subtasks/04_oct_pce_build/outputs/source_table_changes.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["old_version","new_version","series_code","item","component","what_changed","old_source","old_seasonal","new_source","new_seasonal"]); w.writerows(rows)
for r in rows: print(r[0],"->",r[1],r[2],r[3],r[4][:40],r[5])
print(len(rows),"changed lines")
