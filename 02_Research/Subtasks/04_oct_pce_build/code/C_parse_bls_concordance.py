"""C_parse_bls_concordance.py: parse all HTML tables of the saved BLS PCE-CPI code-mapping page to CSV.
Run: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_parse_bls_concordance.py"""
import csv, re
from html.parser import HTMLParser
SRC = "03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.html"
OUT = "03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv"   # derived from raw HTML; raw HTML itself untouched
class P(HTMLParser):
    def __init__(s): super().__init__(); s.tables=[]; s.t=None; s.row=None; s.cell=None; s.text=[]; s.intext=False; s.skip=0; s.lm=None
    def handle_starttag(s, tag, a):
        if tag=="table": s.t=[]; s.tables.append(s.t)
        elif tag=="tr" and s.t is not None: s.row=[]; s.t.append(s.row)
        elif tag in("td","th") and s.row is not None: s.cell=[]
        elif tag in("p","br") and s.cell is not None: s.cell.append(" ")
        elif tag in ("script","style"): s.skip+=1
    def handle_endtag(s, tag):
        if tag in("td","th") and s.cell is not None: s.row.append(re.sub(r"\s+"," ","".join(s.cell)).strip()); s.cell=None
        elif tag=="tr": s.row=None
        elif tag=="table": s.t=None
        elif tag in ("script","style"): s.skip-=1
    def handle_data(s, d):
        if s.skip: return
        if s.cell is not None: s.cell.append(d)
h = open(SRC, encoding="utf-8", errors="replace").read()
p = P(); p.feed(h)
print("tables:", len(p.tables))
n = 0
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["table_no","table_title","ELI","ELI_description","PCE_series_code","PCE_description"])
    for i, t in enumerate(p.tables, 1):
        title = t[0][0] if t and t[0] else ""
        hdr = t[1] if len(t) > 1 else []
        print(i, "title:", title, "| header:", hdr, "| rows:", len(t)-2)
        for r in t[2:]:
            if len(r) == 4: w.writerow([i, title]+r); n += 1
            elif r: print("  odd row", i, r)
print("data rows written:", n)
m = re.search(r"Last Modified Date:[^<]*(?:<[^>]*>\s*)*([A-Za-z]+ \d+, \d{4})?", h); print("last modified:", m.group(0)[:150] if m else None)
