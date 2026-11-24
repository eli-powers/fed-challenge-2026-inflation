"""List Table 2.4.4U-D lines whose source text mentions judgment/trend/implicit/extrapolation, per version.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/B_judgment_lines.py"""
import openpyxl,re
R="03_Data/Raw/BEA_Table244UD_PCE_price_source_data_"
for lab,f in [("2026-09-30 (current)",R+"2026-11-11.xlsx"),("2026-02-20",R+"2026-02-20_retrieved_2026-11-11.xlsx")]:
    print("=====",lab)
    ws=openpyxl.load_workbook(f,read_only=True).worksheets[0]
    for r in ws.iter_rows(min_row=5,values_only=True):
        s=str(r[3] or "")
        if re.search(r'(?i)judg|trend|implicit|extrapol|imput|assum|market indicator',s):
            print(r[0],r[2],r[1].strip(),'|',s[:260],'|',r[4])
