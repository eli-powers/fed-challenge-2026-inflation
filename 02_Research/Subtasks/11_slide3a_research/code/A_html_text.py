"""Convert saved HTML files to paragraph-numbered text in outputs/text/. Usage (project root):
python3 -I 02_Research/Subtasks/11_slide3a_research/code/A_html_text.py <html files...>"""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
OUT = Path.cwd() / "02_Research/Subtasks/11_slide3a_research/outputs/text"
class PP(HTMLParser):
    BLOCK = ("p", "li", "h1", "h2", "h3", "h4", "td", "th", "figcaption", "title")
    def __init__(s): super().__init__(); s.paras = []; s.cur = None; s.skip = 0; s.links = []
    def handle_starttag(s, t, a):
        if t in ("script", "style"): s.skip += 1
        if t in s.BLOCK: s.cur = []
        if t == "a" and s.cur is not None:
            h = dict(a).get("href"); s.cur.append(""); s.links.append((len(s.paras), h))
    def handle_endtag(s, t):
        if t in ("script", "style"): s.skip -= 1
        if t in s.BLOCK and s.cur is not None:
            txt = re.sub(r"\s+", " ", "".join(s.cur)).strip()
            if txt: s.paras.append(f"<{t}> {txt}")
            s.cur = None
    def handle_data(s, d):
        if s.cur is not None and not s.skip: s.cur.append(d)
for fp in sys.argv[1:]:
    p = PP(); p.feed(Path(fp).read_text(errors="ignore"))
    o = OUT / (Path(fp).stem + ".txt")
    with open(o, "w") as f:
        for i, t in enumerate(p.paras): f.write(f"[{i}] {t}\n")
        f.write("\n# LINKS (para index, href)\n")
        for l in p.links:
            if l[1] and not l[1].startswith("#"): f.write(f"{l}\n")
    print(o.name, len(p.paras))
