"""Read the Dallas Fed chart-data workbooks (Economics blog 2026-04-16 and 2026-08-13) saved in
03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/ and print/save the numbers cited in A_q2_trimmed_bias.md.
Run from project root: python3 -I <this>."""
import openpyxl, json, datetime as dt
from pathlib import Path
ROOT = Path.cwd(); D = ROOT / "03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15"
OUT = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs"
def rows(f, sh):
    return list(openpyxl.load_workbook(D / f, data_only=True, read_only=True)[sh].iter_rows(values_only=True))
num = lambda v: v if isinstance(v, (int, float)) else None
res = {}
# Kelly skewness (Chart 3 of 0416; 0813 data5 is a later vintage through Jun 2026)
for f, sh in [("dallasfed_0416data.xlsx", "data3"), ("dallasfed_0813data.xlsx", "data5")]:
    r = [(x[0], num(x[1]), num(x[2])) for x in rows(f, sh)[1:] if isinstance(x[0], dt.datetime)]
    s12 = [(d, v) for d, v, _ in r if v is not None]
    pre = [v for d, v in s12 if 1977 <= d.year <= 2019]
    res[f + ":kelly12m"] = {
        "latest": (s12[-1][0].strftime("%Y-%m"), round(s12[-1][1], 4)),
        "last6": [(d.strftime("%Y-%m"), round(v, 4)) for d, v in s12[-6:]],
        "mean_1977_2019": round(sum(pre) / len(pre), 4),
        "share_positive_1977_2019": round(sum(v > 0 for v in pre) / len(pre), 3),
        "max_2021": max(((d.strftime("%Y-%m"), round(v, 4)) for d, v in s12 if d.year == 2021), key=lambda x: x[1]),
        "dec2024": [(d.strftime("%Y-%m"), round(v, 4)) for d, v in s12 if d.year == 2024 and d.month == 12],
        "sep2025": [(d.strftime("%Y-%m"), round(v, 4)) for d, v in s12 if d.year == 2025 and d.month == 9],
        "latest_1m": (r[-1][0].strftime("%Y-%m"), r[-1][2]),
    }
# 0813 data4: core, headline, TM(24,31), TM(19,20) 12m rates (Chart 5)
r = rows("dallasfed_0813data.xlsx", "data4")
hdr = r[2]
vals = [(x[1], num(x[2]), num(x[3]), num(x[4]), num(x[5])) for x in r[3:] if isinstance(x[1], dt.datetime)]
vals = [v for v in vals if v[3] is not None]
res["0813_chart5_12m_rates_last"] = [dict(month=v[0].strftime("%Y-%m"), core=v[1], headline=v[2], tm_24_31=v[3], tm_19_20=v[4]) for v in vals[-3:]]
# 0416 data5: contribution to change in headline-trimmed gap by category (Chart 5)
r = rows("dallasfed_0416data.xlsx", "data5")
res["0416_chart5_last_row"] = dict(zip(r[0][1:], r[-1][1:]))
res["0416_chart5_last_dated_row"] = [ (x[0].strftime("%Y-%m"),) + tuple(x[1:]) for x in r if isinstance(x[0], dt.datetime) and all(num(y) is not None for y in x[1:])][-1]
# 0813 chart1 trims table? data2 is Chart 2 (RMSE rolling?); data3 slack coefficient — report latest
for sh in ("data2", "data3"):
    r = rows("dallasfed_0813data.xlsx", sh)
    last = [x for x in r if isinstance(x[1], dt.datetime) and any(num(y) is not None for y in x[2:])][-1]
    res[f"0813_{sh}_header"] = r[2]; res[f"0813_{sh}_last"] = (last[1].strftime("%Y-%m"),) + tuple(round(y, 4) if num(y) is not None else y for y in last[2:])
for k, v in res.items(): print(k, v)
(OUT / "A_q2_dallas_data_extract.json").write_text(json.dumps(res, indent=1, default=str))
