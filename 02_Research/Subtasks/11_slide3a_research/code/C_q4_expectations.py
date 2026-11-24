"""Q4: expectations dashboard + gas co-movement + Logan 13-survey aggregate check.
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/C_q4_expectations.py
Outputs: outputs/C_q4_expectations.csv, C_q4_summary.csv, C_q4_gas_comovement.csv, C_q4_gas_latest_change.csv, C_q4_logan_aggregate.csv
"""
import importlib.util, warnings
from pathlib import Path
import numpy as np, pandas as pd, openpyxl
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("C_common", Path.cwd() / "02_Research/Subtasks/11_slide3a_research/code/C_common.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)

START = pd.Period("2018-01", "M")
rows = []  # long output


def add(group, source, sid, horizon, period, value, release, status, src):
    rows.append(dict(group=group, source=source, series_id=sid, horizon=horizon, period=str(period), value=value,
                     release_date=release, status=status, source_file=src))


# ---------- Households: Michigan (pipeline; publisher CSV) ----------
rd = pd.read_csv(C.PIPE / "processed/fed_expectations/release_dates.csv")
def rdate(key, date):
    m = rd[(rd.series_key == key) & (rd.date == date)]
    return m.first_release_date.iloc[0] if len(m) and isinstance(m.first_release_date.iloc[0], str) else ""

monthly = {}  # key -> Series (PeriodIndex) for summary and correlations
for key, name, hz in [("umich_1y_expected_price_change_median", "Michigan 1y median", "next 12 months"),
                      ("umich_5to10y_expected_price_change_median", "Michigan 5-10y median (current table labels 'next 5 years')", "5-10 years ahead")]:
    o = C.pipeline_obs("fed_expectations", key)
    o = o[o.date >= "2018-01-01"]
    s = pd.Series(o.value.values, index=o.date.dt.to_period("M"))
    monthly[name] = s
    for r in o.itertuples():
        pr = "PRELIMINARY" if isinstance(r.note, str) and "PRELIMINARY" in r.note else "final"
        add("Households", "University of Michigan Surveys of Consumers", "PX_MD" if "1y" in name else "PX5_MD", hz,
            r.date.to_period("M"), r.value, rdate(key, r.date.strftime("%Y-%m-%d")), pr, r.raw_file)

# ---------- Households: NY Fed SCE (fresh 2026-11-15 download; cross-checked to pipeline) ----------
sce_f = C.RAWC / "NYFed_SCE_chart_data_2026-11-15.xlsx"
d = pd.read_excel(sce_f, sheet_name="Inflation expectations", header=None)
hdr = d.iloc[3].tolist(); body = d.iloc[4:].copy(); body.columns = hdr
body = body[body.iloc[:, 0].astype(str).str.fullmatch(r"\d{6}")]
body["p"] = pd.PeriodIndex(body.iloc[:, 0].astype(str).str[:4] + "-" + body.iloc[:, 0].astype(str).str[4:], freq="M")
print([h for h in hdr[:8]])
cols = {"SCE 1y median": [h for h in hdr if isinstance(h, str) and h.lower().startswith("median one-year")][0],
        "SCE 3y median": [h for h in hdr if isinstance(h, str) and h.lower().startswith("median three-year")][0]}
for h in hdr:
    if isinstance(h, str) and h.lower().startswith("median five-year"): cols["SCE 5y median"] = h
SCE_REL = "2026-11-09"  # NY Fed press release, Oct 2026 survey (saved NYFed_SCE_press_release_20261109_2026-11-15.html)
for name, col in cols.items():
    s = pd.Series(body[col].astype(float).values, index=body.p.values)
    s = s[~s.isna()]
    monthly[name] = s[s.index >= START]
    hz = {"1y": "1 year ahead", "3y": "3 years ahead", "5y": "5 years ahead"}[name.split()[1]]
    for p, v in s[s.index >= START].items():
        add("Households", "NY Fed Survey of Consumer Expectations", col, hz, p, v, SCE_REL if p == s.index[-1] else "", "final", C.rel(sce_f))
# cross-check to pipeline copy
chk = []
for key, name in [("nyfed_sce_1y_inflation_expectation", "SCE 1y median"), ("nyfed_sce_3y_inflation_expectation", "SCE 3y median")]:
    o = C.pipeline_obs("fed_expectations", key); ps = pd.Series(o.value.values, index=o.date.dt.to_period("M"))
    j = pd.concat([ps, monthly[name]], axis=1, join="inner").dropna(); chk.append((name, float((j.iloc[:, 0] - j.iloc[:, 1]).abs().max()), len(j)))
print("SCE fresh vs pipeline max abs diff:", chk)

# ---------- Professionals: SPF (pipeline raw median files) ----------
spf = [("PCE", "spf_pce_pcea", "headline PCE", "current year Q4/Q4"), ("PCE", "spf_pce_pceb", "headline PCE", "next year Q4/Q4"),
       ("PCE5YR", "spf_pce5yr_pce5yr", "headline PCE", "next 5 yrs avg annual"), ("PCE10", "spf_pce10_pce10", "headline PCE", "next 10 yrs avg annual"),
       ("COREPCE", "spf_corepce_corepcea", "core PCE", "current year Q4/Q4"), ("COREPCE", "spf_corepce_corepceb", "core PCE", "next year Q4/Q4"),
       ("CPI", "spf_cpi_cpia", "headline CPI", "current year Q4/Q4"), ("CPI", "spf_cpi_cpib", "headline CPI", "next year Q4/Q4"),
       ("CPI5YR", "spf_cpi5yr_cpi5yr", "headline CPI", "next 5 yrs avg annual"), ("CPI10", "spf_cpi10_cpi10", "headline CPI", "next 10 yrs avg annual"),
       ("CORECPI", "spf_corecpi_corecpia", "core CPI", "current year Q4/Q4"), ("CORECPI", "spf_corecpi_corecpib", "core CPI", "next year Q4/Q4")]
spf_q = {}
for sid, key, nm, hz in spf:
    o = C.pipeline_obs("fed_expectations", key); o = o[o.date >= "2018-01-01"]
    label = f"SPF {nm}, {hz}"
    spf_q[label] = pd.Series(o.value.values, index=o.date.dt.to_period("Q"))
    for r in o.itertuples():
        q = r.date.to_period("Q")
        add("Professionals", "Philadelphia Fed Survey of Professional Forecasters (median)", key.split("_", 2)[-1].upper() if False else sid + {"current year Q4/Q4": "A", "next year Q4/Q4": "B"}.get(hz, ""),
            f"{nm}; {hz}", q, r.value, rdate(key, r.date.strftime("%Y-%m-%d")) if str(q) == "2026Q3" else "", "final", r.raw_file)
# Q4 2026 SPF check recorded by C_q4_spf_check.py (run at end)

# ---------- Markets: breakevens (fresh FRED, daily -> monthly mean) ----------
daily = {}
for sid, nm, hz in [("T5YIE", "5y breakeven", "5y"), ("T10YIE", "10y breakeven", "10y"), ("T5YIFR", "5y5y forward breakeven", "5y5y")]:
    s = C.fred(sid).dropna(); daily[nm] = s
    m = s[s.index >= "2018-01-01"].groupby(s[s.index >= "2018-01-01"].index.to_period("M")).mean()
    cnt = s[s.index >= "2018-01-01"].groupby(s[s.index >= "2018-01-01"].index.to_period("M")).count()
    monthly[nm + " (monthly avg)"] = m
    for p, v in m.items():
        add("Markets", "FRED (Fed Board/Treasury) " + sid, sid, hz + " monthly average of daily", p, round(v, 4), "", "partial month (%d obs)" % cnt[p] if p == m.index[-1] else "full month", s.attrs["file"])
    add("Markets", "FRED " + sid, sid, hz + " latest daily", s.index[-1].strftime("%Y-%m-%d"), s.iloc[-1], "next business day after observation (FRED daily)", "daily latest", s.attrs["file"])

# ---------- Gas ----------
g = C.fred("GASREGW").dropna()
gm = g.groupby(g.index.to_period("M")).mean(); gcnt = g.groupby(g.index.to_period("M")).count()
monthly["Gas $/gal (monthly avg of weekly)"] = gm[gm.index >= START]
for p, v in gm[gm.index >= START].items():
    add("Gas", "EIA via FRED GASREGW (US regular all formulations retail, weekly, $/gal, NSA)", "GASREGW", "monthly average of weekly (Mondays)", p, round(v, 4), "", "partial month (%d weeks)" % gcnt[p] if p == gm.index[-1] else "full month", g.attrs["file"])
add("Gas", "EIA via FRED GASREGW", "GASREGW", "latest weekly", g.index[-1].strftime("%Y-%m-%d"), g.iloc[-1], "weekly (Mon); FRED updated 2026-11-15 fetch", "weekly latest", g.attrs["file"])

out = pd.DataFrame(rows)
out.to_csv(C.OUTD / "C_q4_expectations.csv", index=False)

# ---------- Summary ----------
def summ(group, source, name, s, hz, freq, latest_release, status_latest, src):
    s = s.dropna()
    if freq == "M":
        p21 = s[(s.index >= pd.Period("2021-01", "M")) & (s.index <= pd.Period("2023-12", "M"))]
        p18 = s[(s.index >= pd.Period("2018-01", "M")) & (s.index <= pd.Period("2019-12", "M"))]
    else:
        p21 = s[(s.index >= pd.Period("2021Q1", "Q")) & (s.index <= pd.Period("2023Q4", "Q"))]
        p18 = s[(s.index >= pd.Period("2018Q1", "Q")) & (s.index <= pd.Period("2019Q4", "Q"))]
    return dict(group=group, source=source, series=name, horizon=hz, frequency=freq,
                latest_period=str(s.index[-1]), latest_value=round(float(s.iloc[-1]), 3), latest_release_date=latest_release, latest_status=status_latest,
                peak_2021_23_period=str(p21.idxmax()) if len(p21) else "n/a", peak_2021_23_value=round(float(p21.max()), 3) if len(p21) else np.nan,
                avg_2018_19=round(float(p18.mean()), 3) if len(p18) else np.nan, n_2018_19=len(p18), source_file=src)

S = []
S.append(summ("Households", "Michigan", "Michigan 1y median", monthly["Michigan 1y median"], "next 12m", "M", "2026-11-06", "PRELIMINARY (final due 2026-11-20)", "03_Data/pipelines/inflation_data/raw/fed_expectations/umich_sca_tbcpx1px5_current_2026-11-10.csv"))
S.append(summ("Households", "Michigan", "Michigan 5-10y median", monthly["Michigan 5-10y median (current table labels 'next 5 years')"], "5-10y", "M", "2026-11-06", "PRELIMINARY (final due 2026-11-20)", "03_Data/pipelines/inflation_data/raw/fed_expectations/umich_sca_tbcpx1px5_current_2026-11-10.csv"))
S.append(summ("Households", "NY Fed SCE", "SCE 1y median", monthly["SCE 1y median"], "1y", "M", SCE_REL, "final", C.rel(sce_f)))
S.append(summ("Households", "NY Fed SCE", "SCE 3y median", monthly["SCE 3y median"], "3y", "M", SCE_REL, "final", C.rel(sce_f)))
S.append(summ("Households", "NY Fed SCE", "SCE 5y median (series starts 2022-01; no 2018-19 base)", monthly["SCE 5y median"], "5y", "M", SCE_REL, "final", C.rel(sce_f)))
for label, s in spf_q.items():
    S.append(summ("Professionals", "SPF median", label, s, label.split(", ", 1)[1], "Q", "2026-08-14 (Q3 survey)", "final; Q4 2026 survey: see C_q4_spf_q4_check.csv", "03_Data/pipelines/inflation_data/raw/fed_expectations/philadelphiafed_spf_median_*_2026-11-10.xlsx"))
for nm in ["5y breakeven", "10y breakeven", "5y5y forward breakeven"]:
    sm = monthly[nm + " (monthly avg)"]
    full = sm.iloc[:-1]  # drop partial Nov
    r = summ("Markets", "FRED", nm + " monthly avg (latest = last full month Oct 2026)", full, nm, "M", "FRED daily", "full month; Nov partial in C_q4_expectations.csv", daily[nm].attrs["file"])
    S.append(r)
    dv = daily[nm]
    S.append(dict(group="Markets", source="FRED", series=nm + " latest daily", horizon=nm, frequency="D", latest_period=dv.index[-1].strftime("%Y-%m-%d"), latest_value=float(dv.iloc[-1]),
                  latest_release_date="FRED daily", latest_status="daily", peak_2021_23_period=str(dv["2021":"2023"].idxmax().date()), peak_2021_23_value=float(dv["2021":"2023"].max()),
                  avg_2018_19=round(float(dv["2018":"2019"].mean()), 3), n_2018_19=len(dv["2018":"2019"]), source_file=dv.attrs["file"]))
gfull = monthly["Gas $/gal (monthly avg of weekly)"].iloc[:-1]
S.append(summ("Gas", "EIA/FRED", "Regular gasoline $/gal monthly avg (latest = last full month)", gfull, "$/gal", "M", "weekly", "full month", g.attrs["file"]))
pd.DataFrame(S).to_csv(C.OUTD / "C_q4_summary.csv", index=False)

# ---------- Gas co-movement ----------
X = {k: monthly[k] for k in ["Michigan 1y median", "SCE 1y median",
                              "Michigan 5-10y median (current table labels 'next 5 years')", "SCE 3y median", "5y5y forward breakeven (monthly avg)", "5y breakeven (monthly avg)"]}
gas = monthly["Gas $/gal (monthly avg of weekly)"]
gas_all = gm  # full history for 12m changes
END = pd.Period("2026-10", "M")  # last complete month common to gas, Michigan(final) and SCE
wins = {"2018-01..2026-10": (pd.Period("2018-01", "M"), END), "2021-01..2023-12": (pd.Period("2021-01", "M"), pd.Period("2023-12", "M")),
        "2024-01..2026-10": (pd.Period("2024-01", "M"), END)}
cm = []
for xn, xs in X.items():
    xfull = xs  # starts 2018-01 so 12m change starts 2019-01
    g12p = (gas_all / gas_all.shift(12) - 1) * 100
    g12d = gas_all - gas_all.shift(12)
    x12 = xfull - xfull.shift(12)
    for wn, (a, b) in wins.items():
        for tname, gx, xx in [("level (gas $/gal vs expectation %)", gas_all, xfull),
                              ("12m change (gas % change vs expectation pp change)", g12p, x12),
                              ("12m change (gas $ change vs expectation pp change)", g12d, x12)]:
            j = pd.concat([gx, xx], axis=1, join="inner").dropna(); j = j[(j.index >= a) & (j.index <= b)]
            if len(j) >= 8:
                cm.append(dict(series_pair=f"Gas (GASREGW monthly avg) vs {xn.replace(' (current table labels \'next 5 years\')', '')}", window=wn, transform=tname,
                               corr=round(float(j.iloc[:, 0].corr(j.iloc[:, 1])), 3), n=len(j), sample_start=str(j.index[0]), sample_end=str(j.index[-1])))
pd.DataFrame(cm).to_csv(C.OUTD / "C_q4_gas_comovement.csv", index=False)

# latest 12m change comparison
lat = []
for p in [pd.Period("2026-10", "M"), pd.Period("2026-11", "M")]:
    row = dict(period=str(p), gas_level=round(float(gas_all[p]), 3), gas_level_12m_ago=round(float(gas_all[p - 12]), 3),
               gas_12m_change_dollars=round(float(gas_all[p] - gas_all[p - 12]), 3), gas_12m_change_pct=round(float((gas_all[p] / gas_all[p - 12] - 1) * 100), 2),
               gas_note="partial month (weeks of Nov 2 and Nov 9)" if p.month == 11 else "full month")
    for nm, s in [("Michigan_1y", monthly["Michigan 1y median"]), ("SCE_1y", monthly["SCE 1y median"]),
                  ("Michigan_5_10y", monthly["Michigan 5-10y median (current table labels 'next 5 years')"]), ("SCE_3y", monthly["SCE 3y median"])]:
        if p in s.index and (p - 12) in s.index:
            row[nm + "_level"] = round(float(s[p]), 3); row[nm + "_12m_change_pp"] = round(float(s[p] - s[p - 12]), 3)
        else:
            row[nm + "_level"] = np.nan; row[nm + "_12m_change_pp"] = np.nan
    lat.append(row)
pd.DataFrame(lat).to_csv(C.OUTD / "C_q4_gas_latest_change.csv", index=False)

# ---------- Logan 13-survey aggregate ----------
wb = openpyxl.load_workbook(C.PIPE / "Inflation_Expectations.xlsx", data_only=True)
ws = wb["Measures"]
meas = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] and r[1] != "Simple average" and r[5] is not None]
mdf = pd.DataFrame(meas, columns=["group", "measure", "publisher", "concept", "horizon", "value", "observation", "source", "note"])
tot = mdf.value.mean()
lo = []
for i, r in mdf.iterrows():
    lo.append(dict(row_type="leave_one_out", group=r.group, measure=r.measure, value=r.value, observation=r.observation, average_without_this=round((mdf.value.sum() - r.value) / (len(mdf) - 1), 3)))
comp = [dict(row_type="component", group=r.group, measure=r.measure, value=r.value, observation=r.observation, average_without_this=np.nan) for r in mdf.itertuples()]
summ_rows = [dict(row_type="aggregate", group="all", measure="Simple average of 13", value=round(tot, 3), observation="2026-11-14 build", average_without_this=np.nan),
             dict(row_type="aggregate", group="all", measure="Median of 13", value=float(mdf.value.median()), observation="", average_without_this=np.nan),
             dict(row_type="aggregate", group="reference", measure="Logan quoted (Nov 10; staff, PCE-based)", value=3.1, observation="2026-11-10", average_without_this=np.nan)]
for gname, gg in mdf.groupby("group"):
    summ_rows.append(dict(row_type="group_average", group=gname, measure=f"{gname} (n={len(gg)})", value=round(gg.value.mean(), 3), observation="", average_without_this=np.nan))
# CPI-based vs not (descriptive)
pd.DataFrame(summ_rows + comp + lo).to_csv(C.OUTD / "C_q4_logan_aggregate.csv", index=False)
print("avg", tot, "n", len(mdf)); print(out.shape)
