"""Manager consolidation: permitted rate calculations, validation, and the Excel workbook.

Permitted calculations (monthly price-index series only, and only when the
publisher does not report the rate):
  MoM      = (I_t / I_{t-1} - 1) * 100                 SA index
  3m_ann   = ((I_t / I_{t-3}) ** 4 - 1) * 100          SA index (compounded, annualized)
  6m_ann   = ((I_t / I_{t-6}) ** 2 - 1) * 100          SA index (compounded, annualized)
  12m      = (I_t / I_{t-12} - 1) * 100                NSA index; SA index only where the
                                                       publisher issues no NSA index (BEA PCE)
Any missing input -> N/A with reason. Rate-only publishers (Dallas, Cleveland,
Atlanta), expectations, breakevens, SPF, ECI and ULC are never calculated.
"""
import sys
from datetime import date
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "processed"
GROUPS = ["bls", "bea", "fed_expectations"]
TODAY = date.today().isoformat()

obs = pd.concat([pd.read_csv(PROC / g / "observations.csv", dtype=str).assign(group=g) for g in GROUPS], ignore_index=True)
meta = pd.concat([pd.read_csv(PROC / g / "series_metadata.csv", dtype=str).assign(group=g) for g in GROUPS], ignore_index=True)
rel = pd.concat([pd.read_csv(PROC / g / "release_dates.csv", dtype=str) for g in GROUPS], ignore_index=True)
obs["date"] = pd.to_datetime(obs["date"]).dt.strftime("%Y-%m-%d")
obs["value_num"] = pd.to_numeric(obs["value"], errors="coerce")
REL = {(r.series_key, r.date): r.first_release_date for r in rel.itertuples() if isinstance(r.date, str) and isinstance(r.first_release_date, str)}

# ------------------------------------------- derived series: core PCE ex OER
# Not a BEA series. Built by "Price indexes/code/core_ex_oer.py"; the latest vintage file is read here.
DERIVED_KEY = "pce_core_ex_oer_derived"
DERIVED_IND = "PCE excluding food, energy, and owner-occupied housing (core ex OER; derived)"
XDIR = ROOT.parent / "Price indexes" / "Cross-index analysis" / "processed"
_dfiles = sorted(p for p in XDIR.glob("core_pce_ex_oer_????-??-??.csv"))
if not _dfiles:
    sys.exit(f"No core_pce_ex_oer_<date>.csv in {XDIR}; run Price indexes/code/core_ex_oer.py first.")
DERIVED_FILE = _dfiles[-1]
DERIVED_VINTAGE = DERIVED_FILE.stem.rsplit("_", 1)[-1]
_dh = pd.read_csv(DERIVED_FILE).dropna(subset=["core_ex_oer_index"])
# core_ex_oer.py chains from Jan 2017 = 100; rebase to BEA's convention (2017 annual average = 100). Rates are unaffected.
_dh["core_ex_oer_index"] = _dh.core_ex_oer_index / _dh.loc[_dh.t.str.startswith("2017"), "core_ex_oer_index"].mean() * 100
_ds = pd.read_csv(XDIR / f"core_pce_ex_oer_summary_{DERIVED_VINTAGE}.csv").set_index("series")
_val_d, _val_p = _ds.loc["VALIDATION derived: 376 minus 153"], _ds.loc["VALIDATION published supercore (T20804 line 28)"]
_last = _dh.iloc[-1]
_pce_vintage = str(meta.loc[meta.series_key == "pce_core_price", "latest_release_date"].iloc[0])
DERIVED_NOTE = (
    "Not published by BEA. Derived by removing 'Imputed rental of owner-occupied nonfarm housing' (U20404/U20405 line 160; "
    f"OER equivalent, {_last.oer_share_of_core:.1f}% of core nominal spending in {pd.Period(_last.t, 'M').strftime('%b %Y')}) "
    "from published core PCE (line 374) inside BEA's monthly Fisher chain: each month solve F^2 = L x P for the remainder's "
    "price relative, using published price relatives and nominal shares; then chain. Method check: the same procedure applied "
    "to line 376 minus line 153 reproduces BEA's published PCE services ex energy and housing "
    f"({pd.Period(_last.t, 'M').strftime('%b')} 12m {_val_d['12m']:.3f} vs {_val_p['12m']:.3f}; 3m {_val_d['3m_ann']:.3f} vs {_val_p['3m_ann']:.3f}). "
    f"Code: Price indexes/code/core_ex_oer.py (vintage file {DERIVED_FILE.name}). All horizons calculated from the derived SA index.")
obs = pd.concat([obs, pd.DataFrame({
    "series_key": DERIVED_KEY, "publisher_series_id": "Derived: BEA U20404/U20405 line 374 minus line 160",
    "date": pd.to_datetime(_dh.t).dt.strftime("%Y-%m-%d"), "frequency": "M", "value": _dh.core_ex_oer_index.astype(str),
    "value_type": "index_level", "measure_label": "Derived index level", "horizon": "level", "seasonal_adjustment": "SA",
    "raw_file": f"Price indexes/Cross-index analysis/processed/{DERIVED_FILE.name}", "note": DERIVED_NOTE,
    "group": "derived", "value_num": _dh.core_ex_oer_index.astype(float)})], ignore_index=True)
_raw_u = [f"Price indexes/PCE/raw/BEA_NIUnderlyingDetail_{t}_{DERIVED_VINTAGE}.json" for t in ("U20404", "U20405")]
DERIVED_META = {
    "series_key": DERIVED_KEY, "indicator": DERIVED_IND, "publisher": "Derived from U.S. Bureau of Economic Analysis data",
    "exact_title": "Not a BEA series (derived)", "publisher_series_id": "Derived: BEA U20404/U20405 line 374 minus line 160",
    "table_or_dataset": "NIUnderlyingDetail; Tables 2.4.4U (price indexes) and 2.4.5U (nominal expenditures)",
    "definition": "Core PCE price index with owner-occupied housing (imputed rent of owner-occupied nonfarm housing) removed; Fisher chain removal of one component.",
    "frequency": "M", "units": "derived; 2017=100", "seasonal_adjustment": "SA",
    "geography_population": "United States; personal consumption expenditures",
    "earliest_obs": str(_dh.t.iloc[1]), "latest_obs": str(_last.t), "latest_release_date": _pce_vintage,
    "source_url": "https://apps.bea.gov/iTable/?reqid=1180",
    "api_endpoint": "https://apps.bea.gov/api/data/ (NIUnderlyingDetail U20404, U20405)",
    "raw_files": "; ".join(_raw_u + [f"output Price indexes/Cross-index analysis/processed/{DERIVED_FILE.name}"]),
    "retrieval_date": DERIVED_VINTAGE,
    "revision_vintage_notes": f"Current BEA vintage ({_pce_vintage}); recompute with core_ex_oer.py after each BEA release.",
    "status": "derived", "notes": DERIVED_NOTE, "group": "derived"}
meta = pd.concat([meta, pd.DataFrame([DERIVED_META])], ignore_index=True)
META = meta.set_index("series_key")

# ------------------------------------------------------- release-date rule
# "Release date" = the release whose data vintage the shown value comes from.
# Revised series: the series' latest release at retrieval (metadata latest_release_date, else the newest
# first-release date on file); the observation's own first-release date is added to Notes when it differs.
# Never-revised series (surveys, daily market rates) keep the observation's own release date.
UNREVISED_PREFIXES = ("spf_", "nyfed_", "umich_", "fred_")


def _date10(x):
    x = "" if x is None or pd.isna(x) else str(x)[:10]
    return x if len(x) == 10 and x[4] == "-" and x[7] == "-" else ""


VINTAGE = {}
for k in meta.series_key:
    v = _date10(META.loc[k, "latest_release_date"] if not isinstance(META.loc[k, "latest_release_date"], pd.Series)
                else META.loc[k, "latest_release_date"].iloc[0])
    VINTAGE[k] = v or max([d for (kk, _), d in REL.items() if kk == k], default="")


def series(key, horizon):
    s = obs[(obs.series_key == key) & (obs.horizon == horizon)]
    return dict(zip(s.date, s.value_num))


def shift(d, months):
    return (pd.Timestamp(d) + pd.DateOffset(months=months)).strftime("%Y-%m-%d")


def fmt(v, nd=2):
    return None if v is None or pd.isna(v) else round(float(v), nd)


# --------------------------------------------------------------- indicators
# Monthly price indexes: (indicator, SA level key, NSA level key or None, publisher-rate keys)
PRICE_INDEXES = [
    ("CPI-U all items (headline)", "cpi_u_all_items_sa", "cpi_u_all_items_nsa"),
    ("CPI-U all items less food and energy (core)", "cpi_u_core_sa", "cpi_u_core_nsa"),
    ("PCE price index (headline)", "pce_price", None),
    ("PCE price index excluding food and energy (core)", "pce_core_price", None),
    ("Market-based PCE price index", "pce_market_based_price", None),
    ("Market-based PCE excluding food and energy", "pce_market_based_core_price", None),
    ("PCE services excluding energy and housing", "pce_services_ex_energy_housing_price", None),
    ("PCE goods excluding food and energy", "pce_goods_ex_food_energy_price", None),
    (DERIVED_IND, DERIVED_KEY, None),
    ("PPI Final Demand", "ppi_final_demand_sa", "ppi_final_demand_nsa"),
    ("PPI Processed goods for intermediate demand", "ppi_intermediate_61_sa", "ppi_intermediate_61_nsa"),
    ("PPI Unprocessed goods for intermediate demand", "ppi_intermediate_62_sa", "ppi_intermediate_62_nsa"),
    ("PPI Services for intermediate demand", "ppi_intermediate_63_sa", "ppi_intermediate_63_nsa"),
    ("PPI Final demand trade services", "ppi_final_demand_trade_services_sa", "ppi_final_demand_trade_services_nsa"),
    ("PPI Final demand trade of personal consumption (trade services for personal consumption)",
     "ppi_personal_consumption_trade_sa", "ppi_personal_consumption_trade_nsa"),
]
# Rate-only publishers: indicator -> {field: (key, horizon, label)}
RATE_ONLY = [
    ("Dallas Fed Trimmed Mean PCE", {
        "6m": ("dallas_trimmed_mean_pce_6m_ann", "6m_ann"), "12m": ("dallas_trimmed_mean_pce_12m", "12m"),
        "other": ("dallas_trimmed_mean_pce_1m_ann", "other:1-month annualized")}),
    ("Cleveland Fed 16% Trimmed-Mean CPI", {
        "mom": ("cleveland_trimmed_mean_cpi_trim_monthly_chg", "MoM"), "12m": ("cleveland_trimmed_mean_cpi_12m", "12m"),
        "other": ("cleveland_trimmed_mean_cpi_trim_ann_monthly_chg", "other:1-month annualized")}),
    ("Atlanta Fed Sticky-Price CPI (headline)", {
        "mom": ("sticky_price_cpi_headline_mom", "MoM"), "3m": ("sticky_price_cpi_headline_3m_ann", "3m_ann"),
        "12m": ("sticky_price_cpi_headline_12m", "12m"), "other": ("sticky_price_cpi_headline_other:1-month annualized", "other:1-month annualized")}),
    ("Atlanta Fed Core Sticky-Price CPI (less food and energy)", {
        "mom": ("sticky_price_cpi_core_mom", "MoM"), "3m": ("sticky_price_cpi_core_3m_ann", "3m_ann"),
        "12m": ("sticky_price_cpi_core_12m", "12m"), "other": ("sticky_price_cpi_core_other:1-month annualized", "other:1-month annualized")}),
    ("Atlanta Fed Sticky-Price CPI less shelter", {
        "mom": ("sticky_price_cpi_less_shelter_mom", "MoM"), "3m": ("sticky_price_cpi_less_shelter_3m_ann", "3m_ann"),
        "12m": ("sticky_price_cpi_less_shelter_12m", "12m"), "other": ("sticky_price_cpi_less_shelter_other:1-month annualized", "other:1-month annualized")}),
]
RATE_ONLY_NA = {"mom": "Publisher reports no non-annualized 1-month change; not calculated (rate-only publisher).",
                "3m": "Publisher does not report a 3-month annualized rate; not calculated (rate-only publisher).",
                "6m": "Publisher does not report a 6-month annualized rate; not calculated (rate-only publisher).",
                "12m": "Publisher does not report a 12-month rate."}
LEVEL_ONLY = [  # (category, indicator, key, horizon filter)
    ("Expectations — household", "NY Fed SCE: median 1-year-ahead expected inflation", "nyfed_sce_1y_inflation_expectation"),
    ("Expectations — household", "NY Fed SCE: median 3-year-ahead expected inflation", "nyfed_sce_3y_inflation_expectation"),
    ("Expectations — household", "NY Fed SCE: median 5-year-ahead expected inflation", "nyfed_sce_5y_inflation_expectation"),
    ("Expectations — household", "Michigan: median expected price change, next 12 months", "umich_1y_expected_price_change_median"),
    ("Expectations — household", "Michigan: median expected price change, next 5-10 years", "umich_5to10y_expected_price_change_median"),
    ("Expectations — market", "5-year breakeven inflation rate (T5YIE)", "fred_t5yie"),
    ("Expectations — market", "10-year breakeven inflation rate (T10YIE)", "fred_t10yie"),
    ("Expectations — market", "5-year, 5-year forward inflation expectation rate (T5YIFR)", "fred_t5yifr"),
]
SPF_KEYS = sorted(k for k in obs.series_key.unique() if k.startswith("spf_"))
LABOR = [
    ("ECI civilian workers: total compensation", "eci_civilian_total_compensation"),
    ("ECI civilian workers: wages and salaries", "eci_civilian_wages_and_salaries"),
    ("ECI civilian workers: benefits", "eci_civilian_benefits"),
    ("ECI private industry: total compensation", "eci_private_total_compensation"),
    ("ECI private industry: wages and salaries", "eci_private_wages_and_salaries"),
    ("ECI private industry: benefits", "eci_private_benefits"),
    ("Nonfarm business: unit labor costs", "productivity_unit_labor_costs"),
    ("Nonfarm business: labor productivity (output per hour)", "productivity_labor_productivity"),
    ("Nonfarm business: hourly compensation", "productivity_hourly_compensation"),
]
NA_NONMONTHLY = "N/A: not a monthly price-index series; no MoM/3m/6m changes derived (per spec)."


def m(key, col):
    try:
        v = META.loc[key, col]
        return v.iloc[0] if isinstance(v, pd.Series) else v
    except KeyError:
        return None


# --------------------------------------------------------- price-index calc
calc_rows = []  # full history, machine-readable


def price_index_rates(ind, sa, nsa):
    lv_sa, lv_nsa = series(sa, "level"), series(nsa, "level") if nsa else {}
    pub_mom, pub_12 = series(sa, "MoM"), series(nsa, "12m") if nsa else {}
    out = {}
    for d in sorted(lv_sa):
        r = {}
        # MoM
        if d in pub_mom and not pd.isna(pub_mom[d]):
            r["mom"] = (pub_mom[d], "N", f"Publisher-reported ({m(sa, 'publisher')}): {'BLS API 1-month % change, SA' if nsa else 'BEA Table 2.8.7 percent change from preceding month (monthly rate)'}.")
        else:
            a, b = lv_sa.get(d), lv_sa.get(shift(d, -1))
            r["mom"] = ((a / b - 1) * 100, "Y", "Calculated: (SA index_t / SA index_t-1 - 1) x 100.") if pd.notna(a) and pd.notna(b) and b else \
                (None, "N/A", "N/A: SA index missing for t or t-1 (e.g., BLS Oct/Nov 2025 CPI not collected) or series start.")
        for f, k, p in (("3m", 3, 4), ("6m", 6, 2)):
            a, b = lv_sa.get(d), lv_sa.get(shift(d, -k))
            r[f] = (((a / b) ** p - 1) * 100, "Y", f"Calculated: ((SA index_t / SA index_t-{k})^{p} - 1) x 100, compounded annual rate.") \
                if pd.notna(a) and pd.notna(b) and b else (None, "N/A", f"N/A: SA index missing for t or t-{k} (data gap or series start); not interpolated.")
        # 12m
        if nsa and d in pub_12 and not pd.isna(pub_12[d]):
            r["12m"] = (pub_12[d], "N", "Publisher-reported: BLS API 12-month % change, NSA.")
        elif nsa:
            a, b = lv_nsa.get(d), lv_nsa.get(shift(d, -12))
            r["12m"] = ((a / b - 1) * 100, "Y", "Calculated: (NSA index_t / NSA index_t-12 - 1) x 100.") if pd.notna(a) and pd.notna(b) and b else \
                (None, "N/A", "N/A: NSA index missing for t or t-12; not interpolated.")
        else:
            a, b = lv_sa.get(d), lv_sa.get(shift(d, -12))
            r["12m"] = ((a / b - 1) * 100, "Y", "Calculated: (SA index_t / SA index_t-12 - 1) x 100. BEA publishes PCE price indexes SA only and no monthly 12-month-change table in its API; BEA's own release uses the same SA basis.") \
                if pd.notna(a) and pd.notna(b) and b else (None, "N/A", "N/A: index missing for t-12 (series start).")
        out[d] = r
        for f, (v, flag, note) in r.items():
            calc_rows.append({"indicator": ind, "sa_key": sa, "nsa_key": nsa or "", "date": d, "horizon": {"mom": "MoM", "3m": "3m_ann", "6m": "6m_ann", "12m": "12m"}[f],
                              "value": v, "calculation_required": flag, "note": note})
    return lv_sa, out


# ---------------------------------------------------------------- rows
SNAP_COLS = ["Category", "Indicator", "Publisher", "Series ID(s)", "Frequency", "Observation date", "Release date",
             "Publisher-reported value", "Value measure / units", "YoY (12m)", "YoY calc required", "6m annualized", "6m calc required",
             "3m annualized", "3m calc required", "MoM", "MoM calc required", "Other (publisher-reported)", "Other: what it is", "Notes"]
snapshot, recent = [], []


def rel(keys, d):
    """Release-date field (see release-date rule above) plus the first-release date for Notes."""
    keys = [k for k in keys if k]
    first = next((REL[(k, d)] for k in keys if (k, d) in REL), "")
    if keys and keys[0] == DERIVED_KEY:
        return {"Release date": f"{_date10(_pce_vintage)} (current BEA vintage; derived {DERIVED_VINTAGE})"}
    if any(k.startswith(UNREVISED_PREFIXES) for k in keys):
        return {"Release date": first or "N/A"}
    vintage = next((VINTAGE[k] for k in keys if VINTAGE.get(k)), "")
    out = {"Release date": vintage or first or "N/A"}
    if first and vintage and first != vintage:
        out["_first"] = first
    return out


def window(dates, freq):
    last = pd.Timestamp(max(dates))
    return [d for d in sorted(dates) if pd.Timestamp(d) > last - pd.DateOffset(months=12)]


def add(rowset, **kw):
    first = kw.pop("_first", None)
    row = {c: None for c in SNAP_COLS}
    row.update(kw)
    if first:
        row["Notes"] = f"First released {first}; value shown is from the {row['Release date']} vintage." + (
            f" | {row['Notes']}" if row["Notes"] else "")
    rowset.append(row)


for ind, sa, nsa in PRICE_INDEXES:
    cat = "Prices — " + ("CPI" if sa.startswith("cpi") else "PCE" if sa.startswith("pce") else "PPI")
    ids = m(sa, "publisher_series_id") + (f" (SA); {m(nsa, 'publisher_series_id')} (NSA)" if nsa else " (SA only)")
    lv, rates = price_index_rates(ind, sa, nsa)
    dates = window(list(lv), "M")
    for i, d in enumerate(dates):
        r = rates[d]
        notes = " | ".join(f"{lab}: {r[f][2]}" for f, lab in (("12m", "YoY"), ("6m", "6m"), ("3m", "3m"), ("mom", "MoM")))
        o = obs[(obs.series_key == sa) & (obs.date == d) & (obs.horizon == "level")]
        extra = o.note.dropna().iloc[0] if not o.note.dropna().empty else ""
        kw = dict(Category=cat, Indicator=ind, Publisher=m(sa, "publisher"), **{"Series ID(s)": ids}, Frequency="Monthly",
                  **{"Observation date": d, **rel([sa, nsa], d), "Publisher-reported value": fmt(lv[d], 3),
                     "Value measure / units": f"Index level, SA ({m(sa, 'units')})", "YoY (12m)": fmt(r["12m"][0]), "YoY calc required": r["12m"][1],
                     "6m annualized": fmt(r["6m"][0]), "6m calc required": r["6m"][1], "3m annualized": fmt(r["3m"][0]), "3m calc required": r["3m"][1],
                     "MoM": fmt(r["mom"][0]), "MoM calc required": r["mom"][1], "Other (publisher-reported)": None, "Other: what it is": "N/A",
                     "Notes": (extra + " | " if extra else "") + notes})
        if pd.isna(lv[d]):
            kw["Publisher-reported value"] = "N/A"
        add(recent, **kw)
    add(snapshot, **{k: v for k, v in recent[-1].items()})

for ind, spec in RATE_ONLY:
    keys = [k for k, _ in spec.values()]
    ser = {f: series(k, h) for f, (k, h) in spec.items()}
    alld = sorted(set().union(*[set(d for d, v in s.items() if pd.notna(v)) for s in ser.values()]))
    dates = window(alld, "M")
    first_key = keys[0]
    for d in dates:
        kw = {"Category": "Prices — Fed Bank measures", "Indicator": ind, "Publisher": m(first_key, "publisher"),
              "Series ID(s)": "; ".join(f"{m(k, 'publisher_series_id')}" for k in keys), "Frequency": "Monthly",
              "Observation date": d, **rel(keys, d), "Publisher-reported value": "see rate fields",
              "Value measure / units": "Publisher reports rates only (no index level used)"}
        notes = []
        for f, col, flag in (("12m", "YoY (12m)", "YoY calc required"), ("6m", "6m annualized", "6m calc required"),
                             ("3m", "3m annualized", "3m calc required"), ("mom", "MoM", "MoM calc required")):
            if f in ser:
                v = ser[f].get(d)
                kw[col], kw[flag] = (fmt(v, 4 if f == "mom" else 2), "N") if pd.notna(v) else ("N/A", "N/A")
                if f == "mom":
                    notes.append("MoM is published as a decimal fraction (0.003 = 0.3%), shown verbatim.")
                if pd.isna(v):
                    notes.append(f"{col}: publisher value missing for this date.")
            else:
                kw[col], kw[flag] = "N/A", "N/A"
                notes.append(RATE_ONLY_NA[f])
        v = ser["other"].get(d)
        kw["Other (publisher-reported)"] = fmt(v) if pd.notna(v) else "N/A"
        kw["Other: what it is"] = "1-month % change, annualized (publisher-reported)"
        kw["Notes"] = " ".join(notes)
        add(recent, **kw)
    add(snapshot, **recent[-1])

for cat, ind, key in LEVEL_ONLY:
    s = obs[(obs.series_key == key) & obs.value_num.notna()]
    freq = {"D": "Daily", "M": "Monthly", "Q": "Quarterly"}[s.frequency.iloc[0]]
    for d in window(list(obs[obs.series_key == key].date), freq):
        o = obs[(obs.series_key == key) & (obs.date == d)].iloc[0]
        add(recent, Category=cat, Indicator=ind, Publisher=m(key, "publisher"), **{"Series ID(s)": m(key, "publisher_series_id"), "Frequency": freq,
            "Observation date": d, **(rel([key], d) if freq != "Daily" else {"Release date": "Same/next business day (daily series)"}),
            "Publisher-reported value": fmt(o.value_num) if pd.notna(o.value_num) else "N/A",
            "Value measure / units": f"{o.measure_label} ({m(key, 'units')})", "YoY (12m)": "N/A", "YoY calc required": "N/A",
            "6m annualized": "N/A", "6m calc required": "N/A", "3m annualized": "N/A", "3m calc required": "N/A", "MoM": "N/A",
            "MoM calc required": "N/A", "Other: what it is": "N/A",
            "Notes": "Expectation/breakeven level; price-change fields not applicable (per spec)." + (f" {o.note}" if isinstance(o.note, str) else "")})
    # Expectations stay out of the Current Snapshot (established layout since Sept 2026); full rows are in Recent 12 Months.

for key in SPF_KEYS:
    s = obs[obs.series_key == key]
    if s.value_num.notna().sum() == 0:
        continue
    code = key.split("_")[-1].upper()
    for d in window(list(s.date), "Q"):
        o = s[s.date == d].iloc[0]
        add(recent, Category="Expectations — professional (SPF)", Indicator=f"SPF median {code}", Publisher=m(key, "publisher"),
            **{"Series ID(s)": code, "Frequency": "Quarterly (survey)", "Observation date": d,
               **rel([key], d), "Publisher-reported value": fmt(o.value_num) if pd.notna(o.value_num) else "N/A",
               "Value measure / units": o.horizon, "YoY (12m)": "N/A", "YoY calc required": "N/A", "6m annualized": "N/A", "6m calc required": "N/A",
               "3m annualized": "N/A", "3m calc required": "N/A", "MoM": "N/A", "MoM calc required": "N/A", "Other: what it is": "N/A",
               "Notes": "Survey date = quarter start of survey quarter. Median across forecasters; price-change fields not applicable."})

for ind, key in LABOR:
    lv, r12 = series(key, "level"), series(key, "12m")
    other_h = "3m" if key.startswith("eci") else "3m_ann"
    oth = series(key, other_h)
    lvl_rows = obs[(obs.series_key == key) & (obs.horizon == "level")]
    sa_rows = lvl_rows[lvl_rows.seasonal_adjustment == "SA"] if (lvl_rows.seasonal_adjustment == "SA").any() else lvl_rows
    lv = dict(zip(sa_rows.date, sa_rows.value_num))
    for d in window(list(lv), "Q"):
        add(recent, Category="Labor costs", Indicator=ind, Publisher=m(key, "publisher"), **{"Series ID(s)": m(key, "publisher_series_id"),
            "Frequency": "Quarterly", "Observation date": d, **rel([key], d), "Publisher-reported value": fmt(lv.get(d), 3),
            "Value measure / units": f"Index level ({sa_rows.seasonal_adjustment.iloc[0]}); {m(key, 'units')}",
            "YoY (12m)": fmt(r12.get(d)) if pd.notna(r12.get(d)) else "N/A", "YoY calc required": "N" if pd.notna(r12.get(d)) else "N/A",
            "6m annualized": "N/A", "6m calc required": "N/A", "3m annualized": "N/A", "3m calc required": "N/A", "MoM": "N/A", "MoM calc required": "N/A",
            "Other (publisher-reported)": fmt(oth.get(d)) if pd.notna(oth.get(d)) else "N/A",
            "Other: what it is": "3-month % change, SA (not annualized)" if key.startswith("eci") else "% change from previous quarter at annual rate, SA",
            "Notes": "YoY = publisher-reported 12-month (same quarter a year ago) % change. " + NA_NONMONTHLY})
    add(snapshot, **[r for r in recent if r["Indicator"] == ind][-1])

# ------------------------------------------------------ Sources & Methods
SRC_COLS = ["series_key", "indicator", "publisher", "exact_title", "publisher_series_id", "table_or_dataset", "definition", "frequency", "units",
            "seasonal_adjustment", "geography_population", "earliest_obs", "latest_obs", "latest_release_date", "source_url", "api_endpoint",
            "raw_files", "retrieval_date", "revision_vintage_notes", "status", "notes"]
used_keys = set(obs.series_key)
_order = {g: i for i, g in enumerate(["bls", "bea", "derived", "fed_expectations"])}
src = meta.assign(_o=meta.group.map(_order)).sort_values("_o", kind="stable")[SRC_COLS].copy()
src["calculation_notes"] = src.series_key.map(lambda k: (
    "All horizons calculated (Y) from the derived SA index; method validated against BEA published supercore." if k == DERIVED_KEY else
    "MoM publisher-reported; 3m/6m annualized calculated from SA index; 12m publisher-reported (NSA)." if k.endswith("_sa") or k.endswith("_nsa") and k.startswith(("cpi", "ppi")) else
    "MoM publisher-reported (BEA 2.8.7); 3m/6m/12m calculated from SA index." if k.startswith("pce_") and k != "pce_goods_ex_food_energy_price" else
    "No BEA-published rate: MoM, 3m/6m annualized and 12m calculated from SA index." if k == "pce_goods_ex_food_energy_price" else
    "Rates used verbatim; none calculated." if k.startswith(("dallas", "cleveland", "sticky")) else
    "Published values only; no changes derived."))
src.loc[src.series_key.isin(["ppi_final_demand_sa", "ppi_final_demand_nsa"]), "notes"] = src.loc[
    src.series_key.isin(["ppi_final_demand_sa", "ppi_final_demand_nsa"]), "notes"].fillna("") + " FD-ID aggregation begins Nov 2009 (index Nov 2009=100); earlier history does not exist."

# --------------------------------------------------------------- validate
problems = []
for rowset, name in ((snapshot, "snapshot"), (recent, "recent")):
    for r in rowset:
        for f in ("YoY", "6m", "3m", "MoM"):
            flag = r[f"{f} calc required" if f != "YoY" else "YoY calc required"]
            if flag not in ("Y", "N", "N/A"):
                problems.append(f"{name} {r['Indicator']} {r['Observation date']} bad flag {f}={flag}")
if str(_last.t) != str(m("pce_core_price", "latest_obs"))[:7]:
    problems.append(f"Derived core ex OER ends {_last.t} but BEA core PCE ends {m('pce_core_price', 'latest_obs')}: rerun core_ex_oer.py on the current BEA vintage")
# native-frequency check: no duplicated (indicator, date) and monthly/quarterly spacing
rec = pd.DataFrame(recent)
dups = rec.duplicated(["Indicator", "Observation date"]).sum()
if dups:
    problems.append(f"{dups} duplicate indicator/date rows in Recent 12 Months")
for ind, g in rec.groupby("Indicator"):
    f = g.Frequency.iloc[0]
    ds = pd.to_datetime(g["Observation date"])
    if f.startswith("Quarterly") and not all(ds.dt.month.isin([1, 4, 7, 10])):
        problems.append(f"{ind}: quarterly dates not on quarter starts")
    if f == "Monthly" and not all(ds.dt.day == 1):
        problems.append(f"{ind}: monthly dates not month-start")
    if f == "Monthly" and len(g) > 12:
        problems.append(f"{ind}: more than 12 monthly rows")
    if f.startswith("Quarterly") and len(g) > 4:
        problems.append(f"{ind}: more than 4 quarterly rows")

# ------------------------------------------------------------------ write
calc = pd.DataFrame(calc_rows)
calc.to_csv(PROC / "calculated_rates.csv", index=False)
wb = Workbook()
HDR = PatternFill("solid", fgColor="1F3864")


def sheet(ws, cols, rows):
    ws.append(cols)
    for c in ws[1]:
        c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), HDR, Alignment(wrap_text=True, vertical="top")
    for r in rows:
        ws.append([r.get(c) if isinstance(r, dict) else r[c] for c in cols])
    ws.freeze_panes = "C2"
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = {"Notes": 90, "Indicator": 42, "Value measure / units": 40, "notes": 70,
                                                            "definition": 60, "revision_vintage_notes": 50, "calculation_notes": 50}.get(c, 16)
    ws.auto_filter.ref = ws.dimensions


ws = wb.active
ws.title = "Current Snapshot"
sheet(ws, SNAP_COLS, snapshot)
sheet(wb.create_sheet("Recent 12 Months"), SNAP_COLS, recent)
sheet(wb.create_sheet("Sources & Methods"), SRC_COLS + ["calculation_notes"], src.fillna("").to_dict("records"))
info = wb.create_sheet("Read Me")
for line in [
    f"Built {TODAY} by inflation_data/code/build_workbook.py from inflation_data/processed/.",
    "Calc required: N = publisher-reported value used verbatim; Y = calculated by build_workbook.py from saved publisher index levels; N/A = not applicable or not computable (see Notes).",
    "Calculations permitted only for monthly price indexes: MoM and 3m/6m annualized (compounded) from SA index; 12m from NSA index (SA only where publisher has no NSA index: BEA PCE).",
    "Rate-only publishers (Dallas, Cleveland, Atlanta) are shown verbatim; horizons they do not publish are N/A. Non-preferred published horizons are in 'Other'.",
    "Cleveland and Atlanta MoM values are published as decimal fractions (0.003 = 0.3%) and are shown verbatim.",
    f"PCE vintage: latest = {str(m('pce_core_price', 'latest_obs'))[:7]}, released {_pce_vintage}. BEA's Sept 30, 2026 annual update revised Jan 2021 onward and changed methods for portfolio management, software and legal services; the pre-update version is archived in inflation_data/archive/vintage_2026-09-27_pre_annual_update/.",
    "Release date = the release whose data vintage the shown value comes from (for revised series, the latest release at retrieval; the observation's first-release date is in Notes when different). Surveys (SPF, NY Fed SCE, Michigan) and daily breakevens are not revised and show their own release date; Michigan shows the preliminary release date.",
    "Full histories: inflation_data/processed/<group>/observations.csv and processed/calculated_rates.csv; raw publisher files in inflation_data/raw/.",
    f"Derived row: core PCE excluding owner-occupied housing (core ex OER) is not published by BEA; it is derived from BEA aggregates by Price indexes/code/core_ex_oer.py (file {DERIVED_FILE.name}; see its Notes and Sources & Methods). It is the only non-published index in the workbook.",
]:
    info.append([line])
info.column_dimensions["A"].width = 160
wb.move_sheet("Read Me", offset=-3)
wb.save(ROOT / "inflation_indicators.xlsx")
print(f"snapshot rows {len(snapshot)}, recent rows {len(recent)}, sources rows {len(src)}, calc rows {len(calc)}")
print("VALIDATION:", "OK" if not problems else "\n".join(problems))
