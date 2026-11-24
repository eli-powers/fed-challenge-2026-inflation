"""Scan saved BEA Personal Income & Outlays release pages for method/judgment language. Run from project root."""
import re,html,glob
KW=r'legal|portfolio|judgment|imput|extrapolat|assum|methodolog|price index for|PPI|producer price|CPI'
for f in sorted(glob.glob("03_Data/Raw/BEA_PIO_*2026_page_retrieved_2026-11-11.html")):
    t=open(f,errors="ignore").read()
    t=re.sub(r'(?s)<(script|style|nav|header|footer).*?</\1>','',t)
    t=html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',t)))
    i=t.find('Technical Notes'); j=t.find('Related Data Tables') if 'Related Data Tables' in t else len(t)
    tn=t[i:j] if i>=0 else ""
    print("=====",f.split('/')[-1],"| technical-notes chars:",len(tn))
    for s in re.split(r'(?<=[.!?]) ',tn):
        if re.search(KW,s,re.I): print("  -",s[:400])
