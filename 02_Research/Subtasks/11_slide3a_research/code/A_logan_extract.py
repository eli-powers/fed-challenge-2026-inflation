"""Extract paragraphs from the saved Logan Nov 10 2026 speech HTML and print those about trimmed mean / trend.
Run from project root: python3 -I <this>."""
import re, html
from html.parser import HTMLParser
from pathlib import Path
ROOT = Path.cwd()
P = ROOT / "02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html"
class PP(HTMLParser):
    def __init__(s): super().__init__(); s.paras=[]; s.cur=None; s.links=[]
    def handle_starttag(s,t,a):
        if t in ("p","li","h1","h2","h3","sup"): 
            if t!="sup": s.cur=[]
        if t=="a" and s.cur is not None:
            s.links.append((len(s.paras), dict(a).get("href")))
    def handle_endtag(s,t):
        if t in ("p","li","h1","h2","h3") and s.cur is not None:
            txt=re.sub(r"\s+"," ","".join(s.cur)).strip()
            if txt: s.paras.append(txt)
            s.cur=None
    def handle_data(s,d):
        if s.cur is not None: s.cur.append(d)
p=PP(); p.feed(P.read_text(errors="ignore"))
out = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs/text/logan_2026-11-10_paragraphs.txt"
with open(out,"w") as f:
    for i,t in enumerate(p.paras): f.write(f"[{i}] {t}\n")
kw = ["trimmed","mix of price","multivariate","trend","3.2","2.3","2.8","staff","research","footnote"]
for i,t in enumerate(p.paras):
    if any(k in t.lower() for k in kw): print(f"[{i}] {t}\n")
print("LINKS near:", [l for l in p.links if l[1] and ("dallasfed" in l[1] or "newyorkfed" in l[1])][:40])
