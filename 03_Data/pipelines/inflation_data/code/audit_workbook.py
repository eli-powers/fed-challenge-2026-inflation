"""Read-only, independent reconciliation of the inflation workbook and saved inputs.

Run from any directory. Prints a compact JSON summary; never edits the dataset.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import openpyxl
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
GROUPS = ("bls", "bea", "fed_expectations")
PRICE_KEYS = {
    "CPI-U all items (headline)": ("cpi_u_all_items_sa", "cpi_u_all_items_nsa"),
    "CPI-U all items less food and energy (core)": ("cpi_u_core_sa", "cpi_u_core_nsa"),
    "PCE price index (headline)": ("pce_price", None),
    "PCE price index excluding food and energy (core)": ("pce_core_price", None),
    "Market-based PCE price index": ("pce_market_based_price", None),
    "Market-based PCE excluding food and energy": ("pce_market_based_core_price", None),
    "PCE services excluding energy and housing": ("pce_services_ex_energy_housing_price", None),
    "PCE goods excluding food and energy": ("pce_goods_ex_food_energy_price", None),
    "PPI Final Demand": ("ppi_final_demand_sa", "ppi_final_demand_nsa"),
    "PPI Processed goods for intermediate demand": ("ppi_intermediate_61_sa", "ppi_intermediate_61_nsa"),
    "PPI Unprocessed goods for intermediate demand": ("ppi_intermediate_62_sa", "ppi_intermediate_62_nsa"),
    "PPI Services for intermediate demand": ("ppi_intermediate_63_sa", "ppi_intermediate_63_nsa"),
    "PPI Final demand trade services": ("ppi_final_demand_trade_services_sa", "ppi_final_demand_trade_services_nsa"),
    "PPI Final demand trade of personal consumption (trade services for personal consumption)":
        ("ppi_personal_consumption_trade_sa", "ppi_personal_consumption_trade_nsa"),
}
DERIVED_KEY = "pce_core_ex_oer_derived"
DERIVED_IND = "PCE excluding food, energy, and owner-occupied housing (core ex OER; derived)"
PRICE_KEYS[DERIVED_IND] = (DERIVED_KEY, None)
LEVEL_KEYS = {
    "NY Fed SCE: median 1-year-ahead expected inflation": "nyfed_sce_1y_inflation_expectation",
    "NY Fed SCE: median 3-year-ahead expected inflation": "nyfed_sce_3y_inflation_expectation",
    "NY Fed SCE: median 5-year-ahead expected inflation": "nyfed_sce_5y_inflation_expectation",
    "Michigan: median expected price change, next 12 months": "umich_1y_expected_price_change_median",
    "Michigan: median expected price change, next 5-10 years": "umich_5to10y_expected_price_change_median",
    "5-year breakeven inflation rate (T5YIE)": "fred_t5yie",
    "10-year breakeven inflation rate (T10YIE)": "fred_t10yie",
    "5-year, 5-year forward inflation expectation rate (T5YIFR)": "fred_t5yifr",
}
LABOR_KEYS = {
    "ECI civilian workers: total compensation": "eci_civilian_total_compensation",
    "ECI civilian workers: wages and salaries": "eci_civilian_wages_and_salaries",
    "ECI civilian workers: benefits": "eci_civilian_benefits",
    "ECI private industry: total compensation": "eci_private_total_compensation",
    "ECI private industry: wages and salaries": "eci_private_wages_and_salaries",
    "ECI private industry: benefits": "eci_private_benefits",
    "Nonfarm business: unit labor costs": "productivity_unit_labor_costs",
    "Nonfarm business: labor productivity (output per hour)": "productivity_labor_productivity",
    "Nonfarm business: hourly compensation": "productivity_hourly_compensation",
}
RATE_KEYS = {
    "Dallas Fed Trimmed Mean PCE": {
        "6m annualized": "dallas_trimmed_mean_pce_6m_ann",
        "YoY (12m)": "dallas_trimmed_mean_pce_12m",
        "Other (publisher-reported)": "dallas_trimmed_mean_pce_1m_ann"},
    "Cleveland Fed 16% Trimmed-Mean CPI": {
        "MoM": "cleveland_trimmed_mean_cpi_trim_monthly_chg",
        "YoY (12m)": "cleveland_trimmed_mean_cpi_12m",
        "Other (publisher-reported)": "cleveland_trimmed_mean_cpi_trim_ann_monthly_chg"},
    "Atlanta Fed Sticky-Price CPI (headline)": {
        "MoM": "sticky_price_cpi_headline_mom", "3m annualized": "sticky_price_cpi_headline_3m_ann",
        "YoY (12m)": "sticky_price_cpi_headline_12m",
        "Other (publisher-reported)": "sticky_price_cpi_headline_other:1-month annualized"},
    "Atlanta Fed Core Sticky-Price CPI (less food and energy)": {
        "MoM": "sticky_price_cpi_core_mom", "3m annualized": "sticky_price_cpi_core_3m_ann",
        "YoY (12m)": "sticky_price_cpi_core_12m",
        "Other (publisher-reported)": "sticky_price_cpi_core_other:1-month annualized"},
    "Atlanta Fed Sticky-Price CPI less shelter": {
        "MoM": "sticky_price_cpi_less_shelter_mom", "3m annualized": "sticky_price_cpi_less_shelter_3m_ann",
        "YoY (12m)": "sticky_price_cpi_less_shelter_12m",
        "Other (publisher-reported)": "sticky_price_cpi_less_shelter_other:1-month annualized"},
}
HORIZON_COLS = {"12m": ("YoY (12m)", "YoY calc required"),
                "6m_ann": ("6m annualized", "6m calc required"),
                "3m_ann": ("3m annualized", "3m calc required"),
                "MoM": ("MoM", "MoM calc required")}


def read_sheet(wb, name):
    vals = wb[name].values
    headings = next(vals)
    return [dict(zip(headings, row)) for row in vals]


def as_number(x):
    if x is None or x in ("", "N/A") or pd.isna(x):
        return None
    return float(x)


def norm_text(x):
    """Ignore line-ending differences (Excel stores CR as _x000D_)."""
    return "" if x is None or pd.isna(x) else str(x).replace("_x000D_", "").replace("\r", "")


def close(a, b, tolerance):
    return (a is None and b is None) or (a is not None and b is not None and abs(a-b) <= tolerance)


def main():
    failures = []
    counters = Counter()
    obs = pd.concat([pd.read_csv(ROOT / "processed" / g / "observations.csv", dtype=str)
                     for g in GROUPS], ignore_index=True)
    meta = pd.concat([pd.read_csv(ROOT / "processed" / g / "series_metadata.csv", dtype=str)
                      for g in GROUPS], ignore_index=True)
    calc = pd.read_csv(ROOT / "processed" / "calculated_rates.csv", dtype=str, keep_default_na=False)
    wb = openpyxl.load_workbook(ROOT / "inflation_indicators.xlsx", read_only=True, data_only=False)
    snapshot = read_sheet(wb, "Current Snapshot")
    recent = read_sheet(wb, "Recent 12 Months")
    sources = read_sheet(wb, "Sources & Methods")

    # Structural and provenance checks independent of the workbook builder.
    def unique(rows, fields, label):
        pairs = [tuple(row[k] for k in fields) for row in rows]
        duplicates = len(pairs) - len(set(pairs))
        counters[label] = len(rows)
        if duplicates:
            failures.append(f"{label}: {duplicates} duplicate {fields} pairs")

    unique(snapshot, ("Indicator",), "snapshot_rows")
    unique(recent, ("Indicator", "Observation date"), "recent_rows")
    unique(sources, ("series_key",), "source_rows")
    unique(obs.to_dict("records"), ("series_key", "date", "horizon", "seasonal_adjustment"), "observation_rows")

    derived_rows = [r for r in sources if r["series_key"] == DERIVED_KEY]
    if len(derived_rows) != 1 or derived_rows[0]["status"] != "derived":
        failures.append(f"Sources & Methods: expected one derived row for {DERIVED_KEY}, found {len(derived_rows)}")
    src_keys = {r["series_key"] for r in sources} - {DERIVED_KEY}
    meta_keys = set(meta.series_key)
    if src_keys != meta_keys:
        failures.append(f"Sources & Methods keys differ from processed metadata: missing {sorted(meta_keys-src_keys)}; extra {sorted(src_keys-meta_keys)}")
    meta_by_key = {r["series_key"]: r for r in meta.to_dict("records")}
    for source in sources:
        prior = meta_by_key.get(source["series_key"])
        if prior is None:
            continue
        for col in ("publisher", "exact_title", "publisher_series_id", "table_or_dataset", "definition",
                    "frequency", "units", "seasonal_adjustment", "geography_population", "earliest_obs",
                    "latest_obs", "latest_release_date", "source_url", "api_endpoint", "raw_files", "retrieval_date",
                    "revision_vintage_notes", "status"):
            counters["source_metadata_cells_compared"] += 1
            a, b = norm_text(source[col]), norm_text(prior[col])
            if a != b:
                failures.append(f"Workbook source metadata differs from processed metadata: {source['series_key']} {col}")
    for row in obs.itertuples():
        counters["raw_path_references"] += 1
        for raw_path in str(row.raw_file).split(";"):
            if raw_path and not (PROJECT / raw_path).exists():
                failures.append(f"Missing raw file for {row.series_key} {row.date}: {raw_path}")
    recent_by_ind = {}
    for r in recent:
        recent_by_ind.setdefault(r["Indicator"], []).append(r)
        freq, date = r["Frequency"], str(r["Observation date"])
        if freq == "Monthly" and not date.endswith("-01"):
            failures.append(f"Non-month-start monthly row: {r['Indicator']} {date}")
        if str(freq).startswith("Quarterly") and date[5:10] not in ("01-01", "04-01", "07-01", "10-01"):
            failures.append(f"Non-quarter-start quarterly row: {r['Indicator']} {date}")
        for valcol, flagcol in HORIZON_COLS.values():
            flag = r[flagcol]
            if flag not in ("Y", "N", "N/A"):
                failures.append(f"Bad calculation flag: {r['Indicator']} {date} {flagcol}={flag}")
            if flag == "N/A" and r[valcol] not in ("N/A", None):
                failures.append(f"N/A flag with numeric value: {r['Indicator']} {date} {valcol}")
        if any(isinstance(v, str) and v in {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}
               for v in r.values()):
            failures.append(f"Spreadsheet error: {r['Indicator']} {date}")
    for snap in snapshot:
        rows = recent_by_ind.get(snap["Indicator"], [])
        if not rows:
            failures.append(f"Snapshot indicator has no recent rows: {snap['Indicator']}")
            continue
        latest = max(rows, key=lambda x: str(x["Observation date"]))
        counters["snapshot_cells_compared"] += len(snap)
        for col in snap:
            if snap[col] != latest[col]:
                failures.append(f"Snapshot differs from latest recent row: {snap['Indicator']} {col}")

    # Independent calculation from saved index levels and published rates.
    obs_values = {}
    obs_rows = {}
    for r in obs.itertuples():
        obs_values[(r.series_key, r.date, r.horizon)] = as_number(r.value)
        obs_rows.setdefault((r.series_key, r.date), []).append(r)

    # Derived core ex OER: independent read of the latest core_ex_oer.py output.
    xdir = PROJECT / "Price indexes" / "Cross-index analysis" / "processed"
    dfile = sorted(xdir.glob("core_pce_ex_oer_????-??-??.csv"))[-1]
    dh = pd.read_csv(dfile).dropna(subset=["core_ex_oer_index"])
    dh["core_ex_oer_index"] = dh.core_ex_oer_index / dh.loc[dh.t.str.startswith("2017"), "core_ex_oer_index"].mean() * 100  # 2017 avg = 100
    for t, v in zip(dh.t, dh.core_ex_oer_index):
        obs_values[(DERIVED_KEY, f"{t}-01", "level")] = float(v)
    counters["derived_index_rows"] = len(dh)

    def observed(key, date, horizon=None, season=None):
        rows = obs_rows.get((key, date), [])
        if horizon is not None:
            rows = [r for r in rows if r.horizon == horizon]
        if season is not None:
            rows = [r for r in rows if r.seasonal_adjustment == season]
        return as_number(rows[0].value) if rows else None

    def lookup(key, date, horizon="level"):
        return obs_values.get((key, date, horizon)) if key else None

    def shifted(date, months):
        return (pd.Timestamp(date) + pd.DateOffset(months=months)).strftime("%Y-%m-%d")

    expected_rates = {}
    for indicator, (sa, nsa) in PRICE_KEYS.items():
        dates = sorted(d for key, d, h in obs_values if key == sa and h == "level")
        for date in dates:
            now = lookup(sa, date)
            for horizon, months, exponent in (("MoM", 1, 1), ("3m_ann", 3, 4), ("6m_ann", 6, 2), ("12m", 12, 1)):
                published = lookup(sa, date, "MoM") if horizon == "MoM" else lookup(nsa, date, "12m") if horizon == "12m" and nsa else None
                if published is not None:
                    expected = (published, "N")
                else:
                    basis = nsa if horizon == "12m" and nsa else sa
                    a = lookup(basis, date)
                    b = lookup(basis, shifted(date, -months))
                    expected = (((a/b)**exponent-1)*100, "Y") if a is not None and b else (None, "N/A")
                expected_rates[(indicator, date, horizon)] = expected

    for r in calc.itertuples():
        key = (r.indicator, r.date, r.horizon)
        expected = expected_rates.pop(key, None)
        if expected is None:
            failures.append(f"Unexpected calculated_rates row {key}")
            continue
        counters["full_history_rates_compared"] += 1
        if r.calculation_required != expected[1] or not close(as_number(r.value), expected[0], 1e-8):
            failures.append(f"Calculated rate mismatch {key}: saved {r.value}/{r.calculation_required}, expected {expected}")
    if expected_rates:
        failures.append(f"Missing {len(expected_rates)} calculated_rates rows, first {next(iter(expected_rates))}")

    for r in recent:
        if r["Indicator"] not in PRICE_KEYS:
            continue
        date = str(r["Observation date"])
        sa = PRICE_KEYS[r["Indicator"]][0]
        counters["price_level_cells_compared"] += 1
        if not close(as_number(r["Publisher-reported value"]), lookup(sa, date), 0.00051):
            failures.append(f"Workbook price index level mismatch: {r['Indicator']} {date}")
        for horizon, (valcol, flagcol) in HORIZON_COLS.items():
            # The full-history pass consumes expected_rates; calculate lookup from saved rates here.
            c = calc[(calc.indicator == r["Indicator"]) & (calc.date == date) & (calc.horizon == horizon)]
            if len(c) != 1:
                failures.append(f"Workbook rate missing saved history: {r['Indicator']} {date} {horizon}")
                continue
            expected, flag = as_number(c.iloc[0].value), c.iloc[0].calculation_required
            counters["workbook_rate_cells_compared"] += 1
            if r[flagcol] != flag or not close(as_number(r[valcol]), round(expected, 2) if expected is not None else None, 0.000001):
                failures.append(f"Workbook rate mismatch: {r['Indicator']} {date} {horizon}: {r[valcol]}/{r[flagcol]} vs {expected}/{flag}")

    for r in recent:
        ind, date = r["Indicator"], str(r["Observation date"])
        if ind in LEVEL_KEYS:
            expected = observed(LEVEL_KEYS[ind], date)
            comparisons = (("Publisher-reported value", expected, 2),)
        elif ind.startswith("SPF median "):
            code = ind.removeprefix("SPF median ").lower()
            keys = [k for k in meta_keys if k.startswith("spf_") and k.endswith("_" + code)]
            if len(keys) != 1:
                failures.append(f"SPF code maps to {len(keys)} processed series: {ind}")
                continue
            expected = observed(keys[0], date)
            comparisons = (("Publisher-reported value", expected, 2),)
        elif ind in LABOR_KEYS:
            key = LABOR_KEYS[ind]
            other_h = "3m" if key.startswith("eci") else "3m_ann"
            comparisons = (("Publisher-reported value", observed(key, date, "level", "SA"), 3),
                           ("YoY (12m)", observed(key, date, "12m"), 2),
                           ("Other (publisher-reported)", observed(key, date, other_h), 2))
        elif ind in RATE_KEYS:
            comparisons = tuple((col, observed(key, date), 4 if col == "MoM" else 2)
                                for col, key in RATE_KEYS[ind].items())
        else:
            continue
        for col, expected, digits in comparisons:
            counters["nonprice_cells_compared"] += 1
            actual = as_number(r[col])
            if not close(actual, round(expected, digits) if expected is not None else None, 0.000001):
                failures.append(f"Workbook value mismatch: {ind} {date} {col}: {actual} vs {expected}")

    print(json.dumps({"counts": dict(counters), "failures_count": len(failures), "failures": failures[:100]}, indent=2))


if __name__ == "__main__":
    main()
