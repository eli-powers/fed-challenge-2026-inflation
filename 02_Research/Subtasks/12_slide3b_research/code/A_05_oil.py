"""A_05_oil: Q2. Oil path the SPF baseline plausibly conditioned on (proxies), as of the Q3 SPF deadline.
python3 -I 02_Research/Subtasks/12_slide3b_research/code/A_05_oil.py [deadline YYYY-MM-DD]
Proxies: (1) EIA STEO vintages (Brent spot, monthly -> simple quarterly mean); (2) NYMEX Brent Last-Day Financial
futures (BZ) per contract month from Yahoo Finance chart API (secondary), (3) EIA spot RBRTE/RWTC actuals."""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import A_common as C

deadline = sys.argv[1] if len(sys.argv) > 1 else "2026-08-11"
E = C.RAW / "EIA_STEO_2026-11-15"
daily = pd.read_csv(C.ROOT / "02_Research/Subtasks/10_slide2_research/outputs/C_q8_oil_daily.csv", parse_dates=["date"]).set_index("date")
SPOT_SRC = "02_Research/Subtasks/10_slide2_research/outputs/C_q8_oil_daily.csv (EIA RBRTE/RWTC daily, to 2026-11-11)"
rows = []


def add(proxy, vintage, quarter, usd, src, note=""):
    rows.append(dict(proxy=proxy, vintage=vintage, quarter=quarter, brent_usd=None if usd is None or pd.isna(usd) else round(float(usd), 2),
                     source_file=src, note=note))


# STEO release dates from the EIA outlook page (saved)
html = (E / "page_steo_outlook.html").read_text()
rel = {}
for mon, d, f in re.findall(r"(\w+ 2026)\s+(\d\d/\d\d/2026)\s+(\w+)\.pdf", re.sub(r"<[^>]+>", " ", html)):
    rel[f] = d
quarters = [f"{y}Q{q}" for y in (2026, 2027) for q in (1, 2, 3, 4)]
steo_q = {}
for f in ["jul26", "aug26", "sep26", "oct26", "nov26"]:
    p = E / f"{f}_base.xlsx"
    mser = C.read_steo_series(p, "BREPUUS")
    meta = C.read_steo_meta(p)
    qa = C.steo_quarterly(mser)
    steo_q[f] = qa
    for q in quarters:
        add("EIA STEO Brent spot (BREPUUS), quarterly mean of monthly", f"{f} (released {rel.get(f)}, modeling completed {meta.get('completed')}, last hist. month {meta.get('last_historical_month')})",
            q, qa.get(q), f"EIA_STEO_2026-11-15/{f}_base.xlsx sheet 2tab row BREPUUS", "published monthly; quarter = simple mean of 3 months (derived)")
    for mth in pd.date_range("2026-07-01", "2027-12-01", freq="MS"):
        add("EIA STEO Brent spot (BREPUUS), monthly", f, mth.strftime("%Y-%m"), mser.get(mth), f"EIA_STEO_2026-11-15/{f}_base.xlsx sheet 2tab row BREPUUS", "published")

# actuals from EIA daily spot
b = daily["brent_usd_bbl"].dropna()
mq = b.groupby(b.index.to_period("Q")).mean()
for per, v in mq.items():
    lab = f"{per.year}Q{per.quarter}"
    if lab in quarters:
        add("Actual EIA spot RBRTE, quarterly mean of daily", "to 2026-11-11", lab, v, SPOT_SRC, "2026Q4 is partial (Oct 1 - Nov 11)" if lab == "2026Q4" else "")
mm = b.groupby(b.index.to_period("M")).mean()
for per, v in mm.items():
    if per >= pd.Period("2026-01"):
        add("Actual EIA spot RBRTE, monthly mean of daily", "to 2026-11-11", str(per), v, SPOT_SRC)

# spot at deadline
dts = pd.Timestamp(deadline)
bd = b[b.index <= dts]
spot = bd.iloc[-1]
spot_date = bd.index[-1]
prior20 = bd.iloc[-21:-1]  # 20 trading days before the deadline day
incl20 = bd.iloc[-20:]
w = daily["wti_usd_bbl"].dropna()
wspot = w[w.index <= dts].iloc[-1]
add("EIA spot Brent RBRTE on deadline", deadline, "deadline day", spot, SPOT_SRC, f"date used {spot_date.date()}")
add("EIA spot Brent 20 trading-day mean BEFORE deadline day", f"{prior20.index[0].date()} to {prior20.index[-1].date()}", "20d avg", prior20.mean(), SPOT_SRC, "excludes deadline day")
add("EIA spot Brent 20 trading-day mean INCLUDING deadline day", f"{incl20.index[0].date()} to {incl20.index[-1].date()}", "20d avg", incl20.mean(), SPOT_SRC, "")
add("EIA spot WTI RWTC on deadline", deadline, "deadline day", wspot, SPOT_SRC, "WTI, for spread")
add("EIA Brent minus WTI spot on deadline", deadline, "deadline day", spot - wspot, SPOT_SRC, "USD/bbl")
for d_ in ["2026-07-31", "2026-08-06"]:
    add("EIA spot Brent RBRTE", d_, "day", b[b.index <= d_].iloc[-1], SPOT_SRC, "STEO Aug data cutoff = Aug 6; SPF questionnaire sent ~after Jul 30 GDP advance (documentation)")

# futures curve snapshot (Yahoo BZ contracts)
Y = C.RAW / "Yahoo_BZ_futures_curve_2026-11-15"
mcode = {c: i + 1 for i, c in enumerate("FGHJKMNQUVXZ")}
curve = {}
for f in sorted(Y.glob("BZ[FGHJKMNQUVXZ]??.NYM.json")):
    j = json.load(open(f))
    try:
        r = j["chart"]["result"][0]
    except Exception:
        continue
    ser = pd.Series(r["indicators"]["quote"][0]["close"], index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    c, yy = f.name[2], int(f.name[3:5])
    curve[pd.Timestamp(2000 + yy, mcode[c], 1)] = ser.dropna()
cdf = pd.DataFrame(curve).sort_index(axis=1)
src_y = "Yahoo_BZ_futures_curve_2026-11-15/BZ<m><yy>.NYM.json (Yahoo Finance chart API, daily close; secondary [2])"
for d_ in [pd.Timestamp(deadline) - pd.Timedelta(days=1), pd.Timestamp(deadline)]:
    sn = cdf.loc[cdf.index <= d_].iloc[-1] if (cdf.index <= d_).any() else None
    if sn is None:
        continue
    snd = cdf.index[cdf.index <= d_][-1]
    for mth, v in sn.dropna().items():
        add("NYMEX Brent Last-Day futures (BZ) by contract month", str(snd.date()), mth.strftime("%Y-%m"), v, src_y, "contract month price, not average spot for the month")
snd = cdf.index[cdf.index <= pd.Timestamp(deadline)][-1]
sn = cdf.loc[snd].dropna()
for q in ["2027Q1", "2027Q2", "2027Q3", "2027Q4"]:
    per = pd.Period(q)
    ms = [m_ for m_ in sn.index if pd.Period(m_, "Q") == per]
    if len(ms) == 3:
        add("NYMEX Brent futures (BZ), quarterly mean of 3 contract months", str(snd.date()), q, sn[ms].mean(), src_y, "derived: simple mean of monthly contracts; 2026 contracts unavailable (expired)")
# front month (Yahoo continuous)
fm = json.load(open(Y / "BZ_F.json"))["chart"]["result"][0]
fms = pd.Series(fm["indicators"]["quote"][0]["close"], index=pd.to_datetime(fm["timestamp"], unit="s").normalize())
add("Yahoo BZ=F continuous front-month close", str(snd.date()), "front", fms.get(snd), src_y.replace("BZ<m><yy>.NYM", "BZ_F"), "roll convention unverified; compare EIA spot same day")
add("Yahoo BZ=F minus EIA spot Brent same day", str(snd.date()), "front", fms.get(snd) - b.get(snd, np.nan), src_y, "")

df = pd.DataFrame(rows)
df.to_csv(C.OUT / "A_q2_oil_assumption.csv", index=False)

# unavailable / paywalled log
pw = pd.DataFrame([
    dict(item="ICE Brent futures curve (deadline snapshot)", url="https://www.ice.com/products/219/Brent-Crude-Futures/data", status="not retrievable without licence (page loads, data is JS/licensed); not used", checked="2026-11-15"),
    dict(item="CME Brent Last Day Financial futures settlements", url="https://www.cmegroup.com/markets/energy/crude-oil/brent-crude-oil.settlements.html", status="HTTP 403 to automated fetch", checked="2026-11-15"),
    dict(item="EIA NYMEX WTI futures contracts 1-4 (RCLC1-RCLC4), deadline date", url="https://www.eia.gov/dnav/pet/hist_xls/RCLC1d.xls", status="downloaded, but series ends 2024-04-05 (no 2026 data); cannot be used for Aug 2026", checked="2026-11-15"),
    dict(item="Brent futures contracts expiring in 2026 (Sep-Dec 2026) as of Aug 2026", url="https://query1.finance.yahoo.com/v8/finance/chart/BZV26.NYM", status="Yahoo returns no data for expired contracts; only Jan-2027 and later contracts retrievable", checked="2026-11-15"),
    dict(item="SPF Q4 2026 release (survey page)", url="https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026", status="HTTP 404 (not yet published) at check time", checked="2026-11-15 ~17:40 EST"),
    dict(item="Philadelphia Fed Economic Release Calendar (SPF Q4 date)", url="https://www.philadelphiafed.org/calendar-of-events?release=survey-of-professional-forecasters", status="calendar renders client-side; no SPF date in fetched HTML; scheduled date unverified", checked="2026-11-15"),
])
pw.to_csv(C.OUT / "A_paywalled.csv", index=False)

pd.set_option("display.width", 250, "display.max_colwidth", 90)
print("deadline spot", spot_date.date(), spot, "20d before", round(prior20.mean(), 2), "incl", round(incl20.mean(), 2), "WTI", wspot, "spread", round(spot - wspot, 2))
t = df[df.proxy.str.contains("quarterly")].pivot_table(index="quarter", columns="vintage", values="brent_usd", aggfunc="first")
print(t.to_string())
print(df[df.proxy.str.contains("by contract month")].pivot_table(index="quarter", columns="vintage", values="brent_usd").to_string())
