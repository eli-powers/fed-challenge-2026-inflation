"""A_03_sep: Q1.5. Parse FOMC SEP Table 1 (median / central tendency / range) for core and headline PCE.
python3 -I 02_Research/Subtasks/12_slide3b_research/code/A_03_sep.py [path_to_fomcprojtablYYYYMMDD.htm]
Table 1 layout: 3 blocks of 5 cells (y, y+1, y+2, y+3, longer run): median, central tendency, range; blank cell = not published.
Values are Q4/Q4 percent changes (note under the table)."""
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import A_common as C

f = Path(sys.argv[1]) if len(sys.argv) > 1 else C.RAW / "FOMC_SEP_2026-09_2026-11-15/fomcprojtabl20260916.htm"
h = f.read_text()
mdate = re.search(r"fomcprojtabl(\d{8})", f.name).group(1)
title = re.search(r"Table 1\.[^<]*", h).group(0)
years_hdr = None
tab1 = h[h.index("Table 1."):]
tab1 = tab1[: tab1.index("</table>")]
rows = re.findall(r"<tr>(.*?)</tr>", tab1, flags=re.S)
parsed = []
for r in rows:
    th = re.search(r"<th[^>]*>(.*?)</th>", r, flags=re.S)
    if not th:
        continue
    label = re.sub(r"<[^>]+>|\s+", " ", th.group(1)).strip()
    cells = re.findall(r"<td([^>]*)>(.*?)</td>", r, flags=re.S)
    vals = []
    for attrs, txt in cells:
        t = re.sub(r"<[^>]+>|&nbsp;|\s+", "", txt)
        vals.append(None if "emptystub" in attrs or t == "" else t)
    parsed.append((label, vals))

cur = None
recs = []
sy = int(mdate[:4])
yrs = [str(sy), str(sy + 1), str(sy + 2), str(sy + 3), "longer_run"]
for label, vals in parsed:
    if label.startswith("Core PCE"):
        cur, vint = "core_pce", f"{mdate} meeting"
    elif label.startswith("PCE inflation"):
        cur, vint = "headline_pce", f"{mdate} meeting"
    elif label.startswith("June projection") or label.startswith("March projection") or label.endswith("projection"):
        vint = label
        if cur is None:
            continue
    else:
        cur = None
        continue
    if cur is None or len(vals) < 15:
        continue
    blocks = {"median": vals[0:5], "central_tendency": vals[5:10], "range": vals[10:15]}
    for stat, vs in blocks.items():
        for y, v in zip(yrs, vs):
            if v is None:
                continue
            if stat == "median":
                recs.append(dict(meeting=mdate, vintage=vint, variable=cur, target_year=y, stat="median", low=None, high=None, value=float(v)))
            else:
                lo, hi = (v.split("–") + [v])[:2] if "–" in v else (v, v)
                recs.append(dict(meeting=mdate, vintage=vint, variable=cur, target_year=y, stat=stat, low=float(lo), high=float(hi), value=None))
df = pd.DataFrame(recs)
df["horizon_type"] = "q4q4"
df["source_file"] = f"{f.parent.name}/{f.name} (Table 1, {title.strip()})"
df.to_csv(C.OUT / "A_q1_sep.csv", index=False)
print(df[df.variable == "core_pce"].to_string())
