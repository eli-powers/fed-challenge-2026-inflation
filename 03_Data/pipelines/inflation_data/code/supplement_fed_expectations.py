"""Manager supplement to retrieve_fed_expectations.py (run after it).

Fills gaps left by the subagent run and corrects labels:
- Dallas Fed Trimmed Mean PCE: the Dallas Fed site offers no historical rate file
  (pcedata.xlsx is a current-distribution chart table), so the Dallas-originated
  series are taken from FRED with Dallas Fed attribution (spec rule 2 fallback).
- Cleveland Fed 16% trimmed-mean CPI 12-month rate: publisher chart-data CSV
  (mediancpi_chartdata.csv, column trimmedmeancpi, begins 2017-01).
- Cleveland annualized monthly change relabeled as other:1-month annualized.
- Atlanta Fed sticky CPI monthly (non-annualized) change columns added as MoM.
- University of Michigan: publisher CSV tbmpx1px5.csv (PX_MD, PX5_MD medians).
- SPF horizon labels per SPF documentation (Philadelphia Fed).
- ALFRED first-release dates and latest-3 FRED cross-checks.
No rates are computed here; all values are publisher-reported.
"""
import csv
import io
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_utils import RETRIEVAL_DATE, ROOT, fred_initial_release, get_key, http_get, save_raw  # noqa: E402

G = "fed_expectations"
PROC = ROOT / "processed" / G
RAW = ROOT / "raw" / G
REL = lambda p: str(Path(p).relative_to(ROOT.parent)) if Path(p).is_absolute() else p  # noqa: E731

obs = pd.read_csv(PROC / "observations.csv", dtype=str)
meta = pd.read_csv(PROC / "series_metadata.csv", dtype=str)
rel = pd.read_csv(PROC / "release_dates.csv", dtype=str)
new_obs, new_meta, new_rel, checks = [], [], [], []


def fred_json(endpoint, **params):
    params.update(api_key=get_key("FRED_API_KEY"), file_type="json")
    return http_get(f"https://api.stlouisfed.org/fred/{endpoint}", params)


def fred_obs(series_id, save_name):
    raw = fred_json("series/observations", series_id=series_id, observation_start="2000-01-01")
    path = save_raw(G, save_name, raw)
    data = json.loads(raw)
    return path, [(o["date"], o["value"]) for o in data["observations"]]


def fred_meta(series_id):
    raw = fred_json("series", series_id=series_id)
    save_raw(G, f"stlouisfed_fred_{series_id}_metadata_{RETRIEVAL_DATE}.json", raw)
    return json.loads(raw)["seriess"][0]


def meta_row(**kw):
    base = {c: "" for c in meta.columns}
    base.update(retrieval_date=RETRIEVAL_DATE, status="retrieved")
    base.update(kw)
    return base


def obs_row(**kw):
    base = {c: "" for c in obs.columns}
    base.update(kw)
    return base


# ---------------------------------------------------------------- Dallas Fed
dallas = {
    "dallas_trimmed_mean_pce_1m_ann": ("PCETRIM1M158SFRBDAL", "other:1-month annualized", "1-month annualized trimmed mean PCE inflation rate"),
    "dallas_trimmed_mean_pce_6m_ann": ("PCETRIM6M680SFRBDAL", "6m_ann", "6-month annualized trimmed mean PCE inflation rate"),
    "dallas_trimmed_mean_pce_12m": ("PCETRIM12M159SFRBDAL", "12m", "12-month trimmed mean PCE inflation rate"),
}
for key, (fid, horizon, label) in dallas.items():
    m = fred_meta(fid)
    path, rows = fred_obs(fid, f"stlouisfed_fred_{fid}_dallasfed-originated_{RETRIEVAL_DATE}.json")
    for d, v in rows:
        new_obs.append(obs_row(series_key=key, publisher_series_id=f"Dallas Fed trimmed mean PCE (FRED {fid})", date=d,
                               frequency="M", value="" if v == "." else v, value_type="published_rate",
                               measure_label=label, horizon=horizon, seasonal_adjustment="SA",
                               raw_file=path, note="" if v != "." else "missing in source"))
    new_meta.append(meta_row(
        series_key=key, indicator="Dallas Fed Trimmed Mean PCE", publisher="Federal Reserve Bank of Dallas (distributed via FRED, St. Louis Fed)",
        exact_title=f"{m['title']} ({m['units']})", publisher_series_id=fid, table_or_dataset="Dallas Fed Trimmed Mean PCE Inflation Rate",
        definition="Trims 24% (lower tail) and 31% (upper tail) of the weighted distribution of monthly price changes across 178 PCE components (Dallas Fed).",
        frequency="M", units=m["units"], seasonal_adjustment=m["seasonal_adjustment"], geography_population="United States",
        earliest_obs=rows[0][0], latest_obs=rows[-1][0], latest_release_date=m["last_updated"][:10],
        source_url="https://www.dallasfed.org/research/pce",
        api_endpoint=f"https://api.stlouisfed.org/fred/series/observations?series_id={fid}", raw_files=path,
        published_rate_horizons=horizon, fred_equivalent_id=fid,
        revision_vintage_notes=("Dallas recomputes its full history from the current BEA vintage, so every BEA revision "
                                "(including the Sept 30, 2026 annual update, which revised Jan 2021 onward) revises this series. "
                                f"Latest = {rows[-1][0][:7]}. FRED last_updated " + m["last_updated"]),
        notes="Dallas Fed website has no historical time-series download (pcedata.xlsx is a current-distribution chart table; pcehistprior2009.xls covers pre-2009 history only). FRED used as fallback with Dallas attribution. Download range begins 2000-01."))

# --------------------------------------------------------------- Cleveland Fed
clev_url = "https://www.clevelandfed.org/-/media/files/webcharts/mediancpi/mediancpi_chartdata.csv"
raw = http_get(clev_url)
clev_path = save_raw(G, f"clevelandfed_mediancpi_chartdata_{RETRIEVAL_DATE}.csv", raw)
cdf = pd.read_csv(io.BytesIO(raw))
for _, r in cdf.iterrows():
    new_obs.append(obs_row(series_key="cleveland_trimmed_mean_cpi_12m", publisher_series_id="mediancpi_chartdata.csv: trimmedmeancpi",
                           date=r["date"], frequency="M", value="" if pd.isna(r["trimmedmeancpi"]) else f"{r['trimmedmeancpi']}",
                           value_type="published_rate", measure_label="16% trimmed-mean CPI, 12-month percent change (Cleveland Fed chart data)",
                           horizon="12m", seasonal_adjustment="SA", raw_file=clev_path, note=""))
new_meta.append(meta_row(
    series_key="cleveland_trimmed_mean_cpi_12m", indicator="Cleveland Fed 16% Trimmed Mean CPI", publisher="Federal Reserve Bank of Cleveland",
    exact_title="16% trimmed-mean CPI, 12-month percent change", publisher_series_id="mediancpi_chartdata.csv column trimmedmeancpi",
    table_or_dataset="Cleveland Fed Median CPI chart data", definition="Weighted mean of CPI component price changes after trimming 8% from each tail of the distribution.",
    frequency="M", units="Percent change from 12 months earlier", seasonal_adjustment="SA", geography_population="U.S. city average, all urban consumers",
    earliest_obs=str(cdf["date"].iloc[0]), latest_obs=str(cdf["date"].iloc[-1]), source_url="https://www.clevelandfed.org/indicators-and-data/median-cpi",
    api_endpoint=clev_url, raw_files=clev_path, published_rate_horizons="12m", fred_equivalent_id="TRMMEANCPIM159SFRBCLE",
    notes="Publisher's own download begins 2017-01; earlier 12-month history is not in the publisher files (FRED TRMMEANCPIM159SFRBCLE carries it and is saved for cross-check only). Cleveland interpolated Oct/Nov 2025 after the shutdown."))
# relabel annualized monthly change (subagent mapped it to MoM)
mask = obs.series_key == "cleveland_trimmed_mean_cpi_trim_ann_monthly_chg"
obs.loc[mask, "horizon"] = "other:1-month annualized"
obs.loc[mask, "measure_label"] = "trim_ann_monthly_chg: 1-month percent change, annualized"
obs.loc[mask, "seasonal_adjustment"] = "SA"
mask = obs.series_key == "cleveland_trimmed_mean_cpi_trim_monthly_chg"
obs.loc[mask, "horizon"] = "MoM"
obs.loc[mask, "measure_label"] = "trim_monthly_chg: 1-month change, expressed as a decimal fraction (0.0022 = 0.22%)"
obs.loc[mask, "seasonal_adjustment"] = "SA"
meta.loc[meta.series_key.str.startswith("cleveland_trimmed_mean_cpi_trim"), "published_rate_horizons"] = meta.loc[
    meta.series_key.str.startswith("cleveland_trimmed_mean_cpi_trim"), "series_key"].map(
    {"cleveland_trimmed_mean_cpi_trim_monthly_chg": "MoM (decimal fraction)", "cleveland_trimmed_mean_cpi_trim_ann_monthly_chg": "other:1-month annualized"})

# ---------------------------------------------------------------- Atlanta Fed
atl_file = RAW / f"atlantafed_sticky_price_cpi_{RETRIEVAL_DATE}.xlsx"
if not atl_file.exists():
    atl_file = sorted(RAW.glob("atlantafed_sticky_price_cpi_*.xlsx"))[-1]
atl = pd.read_excel(atl_file, sheet_name="Data")
atl_map = {"sticky_price_cpi_headline_mom": "Sticky CPI (monthly)", "sticky_price_cpi_core_mom": "Core Sticky CPI (monthly)",
           "sticky_price_cpi_less_shelter_mom": "Sticky CPI EX_shelter"}
for key, col in atl_map.items():
    for _, r in atl.iterrows():
        v = r[col]
        missing = isinstance(v, str) or pd.isna(v)
        new_obs.append(obs_row(series_key=key, publisher_series_id=f"Atlanta Fed sticky-price CPI workbook, column '{col}'",
                               date=pd.Timestamp(r["Date"]).strftime("%Y-%m-%d"), frequency="M", value="" if missing else f"{v}",
                               value_type="published_rate", measure_label=f"{col}: 1-month change, decimal fraction (0.003 = 0.3%)",
                               horizon="MoM", seasonal_adjustment="SA", raw_file=REL(atl_file), note="publisher 'na'" if missing else ""))
    new_meta.append(meta_row(
        series_key=key, indicator="Atlanta Fed Sticky CPI", publisher="Federal Reserve Bank of Atlanta", exact_title=f"{col} — 1-month change",
        publisher_series_id=f"workbook column '{col}'", table_or_dataset="Atlanta Fed Sticky-Price CPI data workbook",
        definition="Monthly change of the sticky-price CPI aggregate (components that change price relatively infrequently).", frequency="M",
        units="Decimal fraction (0.003 = 0.3%)", seasonal_adjustment="SA", geography_population="U.S. city average, all urban consumers",
        earliest_obs="1967-02-01", latest_obs=pd.Timestamp(atl["Date"].iloc[-1]).strftime("%Y-%m-%d"),
        source_url="https://www.atlantafed.org/research-and-data/data/sticky-price-cpi", raw_files=REL(atl_file), published_rate_horizons="MoM"))

# ------------------------------------------------------------------ Michigan
mich_url = "https://www.sca.isr.umich.edu/files/tbmpx1px5.csv"
raw = http_get(mich_url)
mich_path = save_raw(G, f"umich_sca_tbmpx1px5_{RETRIEVAL_DATE}.csv", raw)
mdf = pd.read_csv(io.BytesIO(raw))
mdf["date"] = pd.to_datetime(mdf["Month"] + " " + mdf["YYYY"].astype(str), format="%B %Y").dt.strftime("%Y-%m-%d")
mdf["status"] = "final"
# The historical file (tbmpx1px5) holds final readings only. The publisher's current-table CSV (tbcpx1px5)
# also carries the latest preliminary month, flagged "(P)". Append any month newer than the historical file.
cur_url = "https://www.sca.isr.umich.edu/files/tbcpx1px5.csv"
cur_raw = http_get(cur_url)
cur_path = save_raw(G, f"umich_sca_tbcpx1px5_current_{RETRIEVAL_DATE}.csv", cur_raw)
_cur = []
for row in csv.reader(io.StringIO(cur_raw.decode("utf-8", "replace"))):
    if len(row) > 5 and row[1].strip().isdigit() and row[3].strip():
        mon = row[0].replace("(P)", "").strip()
        _cur.append({"date": pd.to_datetime(f"{mon} {row[1].strip()}", format="%B %Y").strftime("%Y-%m-%d"),
                     "PX_MD": float(row[3]), "PX5_MD": float(row[5]) if row[5].strip() else None,
                     "status": "preliminary" if "(P)" in row[0] else "final"})
_newer = [r for r in _cur if r["date"] > mdf["date"].max()]
if _newer:
    mdf = pd.concat([mdf, pd.DataFrame(_newer)], ignore_index=True)
for key, col, label, hz in [
    ("umich_1y_expected_price_change_median", "PX_MD", "Median expected change in prices during the next 12 months (PX_MD)", "next 12 months"),
    ("umich_5to10y_expected_price_change_median", "PX5_MD", "Median expected change in prices during the next 5 to 10 years (PX5_MD)", "next 5 to 10 years"),
]:
    for _, r in mdf.iterrows():
        v = r[col]
        prelim = r["status"] == "preliminary"
        new_obs.append(obs_row(series_key=key, publisher_series_id=f"SCA {'tbcpx1px5.csv (current table)' if prelim else 'tbmpx1px5.csv'} {col}",
                               date=r["date"], frequency="M",
                               value="" if pd.isna(v) else f"{v}", value_type="expectation", measure_label=label, horizon=hz,
                               seasonal_adjustment="NSA", raw_file=cur_path if prelim else mich_path,
                               note=("PRELIMINARY (flagged '(P)' in the publisher's current table); replaced by the final reading on the next run after "
                                     "the final release. Current table labels the long-run column 'next 5 years'." if prelim else "")))
    new_meta.append(meta_row(
        series_key=key, indicator="University of Michigan inflation expectations", publisher="University of Michigan, Surveys of Consumers",
        exact_title=label, publisher_series_id=col, table_or_dataset="SCA table: Expected Changes in Inflation Rates (tbmpx1px5)",
        definition="Median of household responses on expected percent change in prices; the SCA tables also publish means (not retrieved here).",
        frequency="M", units="Percent", seasonal_adjustment="NSA", geography_population="U.S. households (adults)",
        earliest_obs=mdf.loc[mdf[col].notna(), "date"].iloc[0], latest_obs=mdf["date"].iloc[-1], source_url="https://www.sca.isr.umich.edu/tables.html",
        api_endpoint=f"{mich_url}; {cur_url}", raw_files=f"{mich_path}; {cur_path}", fred_equivalent_id="MICH" if col == "PX_MD" else "",
        revision_vintage_notes=("Monthly preliminary then final estimate. Final months from tbmpx1px5.csv; "
                                + (f"latest month ({mdf['date'].iloc[-1][:7]}) is PRELIMINARY, from the current table tbcpx1px5.csv."
                                   if mdf["status"].iloc[-1] == "preliminary" else "latest month is final.")),
        notes="Series break: interviewing moved from phone to mixed phone/web in April 2024 and to web-only by July 2024; the SCA cautions comparisons across the transition. File begins 1978; PX5_MD has gaps before 1990."))
meta = meta[~meta.series_key.isin(["umich_expected_prices_table_32", "umich_expected_prices_table_33"])]

# ---------------------------------------------------------------------- SPF
def spf_label(code):
    var, h = code.rstrip("ABC123456").upper(), code[-1].upper()
    if code.upper() in ("CPI5YR", "CPI10", "PCE5YR", "PCE10"):
        return {"CPI5YR": "annual-average headline CPI inflation over the next 5 years (Q4/Q4 basis)",
                "CPI10": "annual-average headline CPI inflation over the next 10 years (Q4/Q4 basis)",
                "PCE5YR": "annual-average headline PCE inflation over the next 5 years (Q4/Q4 basis)",
                "PCE10": "annual-average headline PCE inflation over the next 10 years (Q4/Q4 basis)"}[code.upper()]
    if h == "1":
        return f"{var}1: real-time historical value for the quarter before the survey quarter (annualized Q/Q %), not a forecast"
    if h in "23456":
        n = int(h) - 2
        return f"{var}{h}: forecast, annualized Q/Q % change, " + ("current (survey) quarter" if n == 0 else f"{n} quarter(s) after survey quarter")
    return f"{var}{h}: forecast, Q4/Q4 % change for " + {"A": "survey year", "B": "year after survey year", "C": "two years after survey year"}[h]

spf_mask = obs.series_key.str.startswith("spf_")
obs.loc[spf_mask, "horizon"] = obs.loc[spf_mask, "series_key"].str.split("_").str[-1].map(spf_label)
meta_spf = meta.series_key.str.startswith("spf_")
meta.loc[meta_spf, "definition"] = meta.loc[meta_spf, "series_key"].str.split("_").str[-1].map(spf_label) + \
    " Source: SPF Documentation (philadelphiafed.org), saved as raw/fed_expectations/philadelphiafed_spf_documentation_2026-09-26.pdf."

# ------------------------------------------------- release dates (ALFRED)
alfred = {
    "dallas_trimmed_mean_pce_12m": "PCETRIM12M159SFRBDAL", "dallas_trimmed_mean_pce_6m_ann": "PCETRIM6M680SFRBDAL",
    "dallas_trimmed_mean_pce_1m_ann": "PCETRIM1M158SFRBDAL", "cleveland_trimmed_mean_cpi_12m": "TRMMEANCPIM159SFRBCLE",
    "cleveland_trimmed_mean_cpi_trim_ann_monthly_chg": "TRMMEANCPIM158SFRBCLE", "cleveland_trimmed_mean_cpi_trim_monthly_chg": "TRMMEANCPIM158SFRBCLE",
    "sticky_price_cpi_headline_12m": "STICKCPIM159SFRBATL", "sticky_price_cpi_headline_3m_ann": "STICKCPIM679SFRBATL",
    "sticky_price_cpi_headline_other:1-month annualized": "STICKCPIM158SFRBATL", "sticky_price_cpi_headline_mom": "STICKCPIM157SFRBATL",
    "sticky_price_cpi_core_12m": "CORESTICKM159SFRBATL", "sticky_price_cpi_core_3m_ann": "CORESTICKM679SFRBATL",
    "sticky_price_cpi_core_other:1-month annualized": "CORESTICKM158SFRBATL", "sticky_price_cpi_core_mom": "CORESTICKM157SFRBATL",
    "sticky_price_cpi_less_shelter_12m": "STICKCPIXSHLTRM159SFRBATL", "sticky_price_cpi_less_shelter_3m_ann": "STICKCPIXSHLTRM679SFRBATL",
    "sticky_price_cpi_less_shelter_other:1-month annualized": "STICKCPIXSHLTRM158SFRBATL", "sticky_price_cpi_less_shelter_mom": "STICKCPIXSHLTRM157SFRBATL",
    "umich_1y_expected_price_change_median": "MICH",
}
alfred_cache = {}
for key, fid in alfred.items():
    if fid not in alfred_cache:
        raw = fred_initial_release(fid)
        save_raw(G, f"stlouisfed_alfred_initial_release_{fid}_{RETRIEVAL_DATE}.json", raw)
        alfred_cache[fid] = {o["date"]: o["realtime_start"] for o in json.loads(raw)["observations"]}
    first = alfred_cache[fid]
    all_obs = pd.concat([obs, pd.DataFrame(new_obs)]) if new_obs else obs
    dates = sorted(all_obs.loc[all_obs.series_key == key, "date"].unique())[-13:]
    for d in dates:
        d10 = str(d)[:10]
        new_rel.append({"series_key": key, "date": d10, "first_release_date": first.get(d10, ""),
                        "method": f"ALFRED output_type=4 {fid}", "note": "" if d10 in first else "not in ALFRED (FRED lags or observation newer than FRED)"})
# Michigan preliminary release dates, transcribed from the SCA 2026 release calendar (ALFRED has no preliminary dates).
UMICH_PRELIM_RELEASES = {"2026-11-01": ("2026-11-06", "https://data.sca.isr.umich.edu/fetchdoc.php?docid=79628")}
_mlast = mdf.iloc[-1]
if _mlast["status"] == "preliminary" and _mlast["date"] in UMICH_PRELIM_RELEASES:
    _rd, _src = UMICH_PRELIM_RELEASES[_mlast["date"]]
    new_rel = [r for r in new_rel if not (r["series_key"].startswith("umich_") and r["date"] == _mlast["date"])]
    for _k in ("umich_1y_expected_price_change_median", "umich_5to10y_expected_price_change_median"):
        new_rel.append({"series_key": _k, "date": _mlast["date"], "first_release_date": _rd,
                        "method": f"publisher release calendar {_src}", "note": "Preliminary release; final scheduled per the same calendar."})
# SCE is not on ALFRED. Release dates transcribed from dated NY Fed press releases (one entry per verified release).
SCE_RELEASES = {"2026-10-01": ("2026-11-09", "https://www.newyorkfed.org/newsevents/news/research/2026/20261109")}
for key in ["nyfed_sce_1y_inflation_expectation", "nyfed_sce_3y_inflation_expectation", "nyfed_sce_5y_inflation_expectation"]:
    for d, (rd, src) in SCE_RELEASES.items():
        new_rel.append({"series_key": key, "date": d, "first_release_date": rd, "method": f"publisher press release {src}", "note": ""})
    new_rel.append({"series_key": key, "date": "", "first_release_date": "", "method": "publisher calendar https://www.newyorkfed.org/microeconomics/sce",
                    "note": "Months not listed in SCE_RELEASES: release dates not retrieved (SCE is not on FRED/ALFRED)."})
new_rel.append({"series_key": "umich_5to10y_expected_price_change_median", "date": "", "first_release_date": "", "method": "publisher calendar https://www.sca.isr.umich.edu/",
                "note": "N/A: no ALFRED series for the 5-10 year median; preliminary mid-month, final late-month."})
for key in meta.loc[meta_spf, "series_key"]:
    new_rel.append({"series_key": key, "date": "2026-07-01", "first_release_date": "2026-08-14", "method": "publisher (SPF Q3 2026 release)",
                    "note": "Earlier survey release dates not retrieved; see https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters"})

# -------------------------------------------------------- FRED cross-checks
xcheck = {"cleveland_trimmed_mean_cpi_12m": "TRMMEANCPIM159SFRBCLE", "sticky_price_cpi_headline_12m": "STICKCPIM159SFRBATL",
          "sticky_price_cpi_core_12m": "CORESTICKM159SFRBATL", "sticky_price_cpi_less_shelter_12m": "STICKCPIXSHLTRM159SFRBATL",
          "sticky_price_cpi_core_3m_ann": "CORESTICKM679SFRBATL", "umich_1y_expected_price_change_median": "MICH"}
all_obs = pd.concat([obs, pd.DataFrame(new_obs)])
for key, fid in xcheck.items():
    _, rows = fred_obs(fid, f"stlouisfed_fred_{fid}_crosscheck_{RETRIEVAL_DATE}.json")
    fred = dict(rows)
    ours = all_obs[(all_obs.series_key == key) & (all_obs.value != "")].sort_values("date").tail(3)
    for _, r in ours.iterrows():
        f = fred.get(str(r["date"])[:10])
        diff = "" if f in (None, ".") else f"{float(r['value']) - float(f):+.3f}"
        checks.append(f"{key} {str(r['date'])[:10]}: publisher {float(r['value']):.3f} | FRED {fid} {f} | diff {diff or 'n/a'}")

# ------------------------------------------------------------------- write
replaced = set(pd.DataFrame(new_obs).series_key)
obs = pd.concat([obs[~obs.series_key.isin(replaced)], pd.DataFrame(new_obs)], ignore_index=True)
meta = pd.concat([meta[~meta.series_key.isin(set(pd.DataFrame(new_meta).series_key))], pd.DataFrame(new_meta)], ignore_index=True)
rel = pd.concat([rel[~rel.series_key.isin(set(pd.DataFrame(new_rel).series_key))], pd.DataFrame(new_rel)], ignore_index=True)
obs.to_csv(PROC / "observations.csv", index=False, quoting=csv.QUOTE_MINIMAL)
meta.to_csv(PROC / "series_metadata.csv", index=False)
rel.to_csv(PROC / "release_dates.csv", index=False)
with open(PROC / "REPORT.md", "a", encoding="utf-8") as fh:
    fh.write("\n## Manager supplement (supplement_fed_expectations.py)\n")
    fh.write("- Dallas trimmed mean: FRED fallback with Dallas attribution (no publisher historical file). Michigan: publisher CSV tbmpx1px5 (medians). "
             "Cleveland 12-month: publisher chart-data CSV from 2017-01. Atlanta MoM (decimal) columns added. SPF horizons relabeled per SPF documentation. "
             "Cleveland annualized monthly change relabeled from MoM to other:1-month annualized.\n")
    fh.write("- FRED cross-checks (latest 3):\n")
    for c in checks:
        fh.write(f"  - {c}\n")
print("\n".join(checks))
print(f"obs rows {len(obs)}, meta rows {len(meta)}, release rows {len(rel)}")
