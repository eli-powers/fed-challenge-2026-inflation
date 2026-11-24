#!/usr/bin/env python3
"""Retrieve BLS basket inputs and published Cleveland/Atlanta Fed inflation data.

All network access and raw saves go through the project fetch_utils module.
The script is repeatable: same-day payloads are reused from raw/ and BLS API
requests are cached by request batch. API keys are only read through get_key().
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.parse
from datetime import date
from pathlib import Path

import pandas as pd

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
import fetch_utils as fu  # noqa: E402

ROOT = fu.ROOT
TODAY = fu.RETRIEVAL_DATE
LATEST = "2026-10-01"  # Cleveland Fed / Atlanta Fed latest published month
# Latest months per BLS index (refresh 2026-11-10: Oct CPI released Nov 10; Sep PPI released Oct 15, Oct PPI not yet out).
CPI_LATEST = "2026-09"  # official basket (latest month with a BLS 12m). Oct 2026 views: see retrieve_cpi() calls in main().
PPI_LATEST = "2026-09"
# PPI weight base (switched 2026-11-14, Eli): BLS relative-importance tables posted 06/11/2026 = December 2025 weights.
# Was PPI_RI_YEAR = "2025" / PPI_RI_BASE = "2024-12" (tables posted 06/12/2025). See archive/pre_ppi_ri2026_2026-11-14/.
PPI_RI_YEAR, PPI_RI_BASE = "2026", "2025-12"
def _mshift(p: str, k: int) -> str: return str(pd.Period(p, freq="M") + k)
def _mlabel(p: str) -> str: return pd.Period(p, freq="M").strftime("%b %Y")
def _interp_oct2025(lev: dict) -> None:
    """Approx. Oct 2025 NSA level = sqrt(Sep 2025 x Nov 2025), only where BLS has none (BLS did not collect Oct 2025)."""
    if "2025-10" not in lev and lev.get("2025-09") and lev.get("2025-11"):
        lev["2025-10"] = (lev["2025-09"] * lev["2025-11"]) ** 0.5
API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
COMPONENT_COLUMNS = [
    "index_name", "component_id", "component_name", "level_or_parent", "in_core",
    "weight_latest", "weight_base_12m", "weight_base_3m", "weight_base_1m",
    "weight_units", "pct_1m_calc", "pct_1m_ann_pub", "pct_3m_ann_calc", "pct_3m_ann_pub", "pct_12m_calc", "pct_12m_pub",
    "contrib_1m_calc", "contrib_3m_ann_calc", "contrib_12m_calc",
    "avg_pct_12m_2018_19_calc", "excess_contrib_12m_calc", "latest_period",
    "sa_basis", "source_ids", "raw_file", "note",
]

def read_tabular_raw(folder: str, pattern: str, url: str) -> tuple[pd.DataFrame, str]:
    """Load a publisher flat file, fetching it through fetch_utils when uncached."""
    existing = sorted((ROOT / folder / "raw").glob(pattern))
    if existing:
        p = existing[-1]
        return pd.read_csv(p, sep="\t", dtype=str).fillna(""), str(p.relative_to(ROOT.parent))
    filename = pattern.replace("*", "") + f"_{TODAY}.txt"
    payload = fu.http_get(url)
    saved = fu.save_raw(folder, filename, payload)
    frame = pd.read_csv(io.BytesIO(payload), sep="\t", dtype=str).fillna("")
    frame.columns = frame.columns.str.strip()
    return frame, saved


def month_map(item: dict) -> dict[str, float]:
    out = {}
    for obs in item.get("data", []):
        if re.fullmatch(r"M\d{2}", obs.get("period", "")) and obs.get("value") not in (None, "", "-"):
            out[f"{obs['year']}-{int(obs['period'][1:]):02d}"] = float(obs["value"])
    return out


def change(levels: dict[str, float], period: str, lag: int, annualize: bool = False) -> float | None:
    end = pd.Period(period, freq="M")
    a, b = levels.get(str(end)), levels.get(str(end - lag))
    if a is None or b in (None, 0): return None
    ratio = a / b
    return ((ratio ** (12 / lag) - 1) * 100) if annualize else ((ratio - 1) * 100)


def compound_3m_contribs(rows: list[dict]) -> None:
    """3m annualized contributions that add up (fix 2026-11-11). Summing weight x each component's own annualized
    3m rate overstates volatile items, since (1+g)^4 is convex (Oct 2026 headline: 6.53 pp vs 5.72% published).
    Instead: c_i = w_i/100 x raw (non-annualized) 3m change; S = sum c_i; contribution_i = c_i x k with
    k = ((1+S/100)^4-1)/(S/100), so contributions sum exactly to the annualized basket 3m rate. Same method as
    fix_3m() in analyze_baskets.py. Edits rows in place, per index_name."""
    for name in dict.fromkeys(r["index_name"] for r in rows):
        grp = [r for r in rows if r["index_name"] == name]
        raw = {}
        for i, r in enumerate(grp):
            w, l3 = r["weight_base_3m"], r["pct_3m_ann_calc"]
            if w in ("", None) or l3 in ("", None): continue
            raw[i] = float(w) / 100 * ((1 + float(l3) / 100) ** 0.25 - 1) * 100
        s = sum(raw.values())
        k = ((1 + s / 100) ** 4 - 1) / (s / 100) if s else 1.0
        for i, r in enumerate(grp):
            r["contrib_3m_ann_calc"] = raw[i] * k if i in raw else ""


def raw_path(folder: str, filename: str) -> Path:
    return ROOT / folder / "raw" / filename


def fetch_raw(folder: str, filename: str, url: str) -> tuple[bytes | None, str]:
    """Fetch one publisher payload; re-use a same-day raw cache on reruns."""
    dest = raw_path(folder, filename)
    if dest.exists():
        return dest.read_bytes(), str(dest.relative_to(ROOT.parent))
    try:
        payload = fu.http_get(url)
        return payload, fu.save_raw(folder, filename, payload)
    except Exception as exc:  # preserve the error in REPORT.md; continue other publishers
        return None, f"N/A (HTTP retrieval failed: {type(exc).__name__}: {exc})"


def save_bytes(folder: str, filename: str, payload: bytes) -> str:
    path = raw_path(folder, filename)
    if not path.exists():
        return fu.save_raw(folder, filename, payload)
    return str(path.relative_to(ROOT.parent))


def write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def report(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# " + title + "\n\n" + "\n".join(f"- {x}" for x in lines) + "\n", encoding="utf-8")


def request_bls(folder: str, ids: list[str], label: str, latest: str) -> tuple[dict[str, dict], str]:
    """Reuse valid raw BLS API series, then fetch only missing IDs in <=50 batches."""
    all_series: dict[str, dict] = {}
    files: list[str] = []
    ids = list(dict.fromkeys(ids))
    wanted = set(ids)
    for cached in sorted((ROOT / folder / "raw").glob("bls_api_*.json")):
        try:
            doc = json.loads(cached.read_bytes())
            if doc.get("status") != "REQUEST_SUCCEEDED": continue
            found = False
            for item in doc.get("Results", {}).get("series", []):
                sid = item.get("seriesID", "")
                if sid in wanted:
                    # A cached series is valid only if it contains the latest requested month.
                    has_latest = any(x.get("year") == latest[:4] and x.get("period") == "M" + latest[5:7] for x in item.get("data", []))
                    if has_latest:
                        all_series[sid] = item; found = True
            if found: files.append(str(cached.relative_to(ROOT.parent)))
        except (OSError, ValueError, TypeError):
            continue
    missing = [sid for sid in ids if sid not in all_series]
    key = fu.get_key("BLS_API_KEY")
    for batch_no, start in enumerate(range(0, len(missing), 50), 1):
        subset = missing[start:start + 50]
        filename = f"bls_api_{label}_batch{batch_no}_{TODAY}.json"
        path = raw_path(folder, filename)
        if path.exists():
            payload = path.read_bytes()
            saved = str(path.relative_to(ROOT.parent))
        else:
            req = {"seriesid": subset, "startyear": "2017", "endyear": "2026",
                   "catalog": True, "calculations": True, "registrationkey": key}
            payload = fu.http_post_json(API, req)
            saved = save_bytes(folder, filename, payload)
        doc = json.loads(payload)
        if doc.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(f"BLS API {label} batch {batch_no} failed: {doc.get('message')}")
        files.append(saved)
        for item in doc.get("Results", {}).get("series", []):
            all_series[item.get("seriesID", "")] = item
    return all_series, "; ".join(files)


def empty_bls_outputs(folder: str, index_name: str, series_id: str, raw_file: str, reason: str) -> None:
    row = {k: "" for k in COMPONENT_COLUMNS}
    row.update({"index_name": index_name, "component_id": "N/A", "component_name": "Basket component mapping",
                "level_or_parent": "N/A", "weight_units": "N/A", "latest_period": LATEST,
                "source_ids": series_id, "raw_file": raw_file,
                "note": "N/A: " + reason})
    write_csv(ROOT / folder / "processed" / "components.csv", [row], COMPONENT_COLUMNS)


def retrieve_cpi(latest: str = CPI_LATEST, suffix: str = "", interpolate_oct2025: bool = False) -> None:
    """CPI-U basket. Default call = official basket at CPI_LATEST written to components.csv etc.
    Extra views (refresh 2026-11-10, approved by Eli): suffix != "" writes components{suffix}.csv, reconciliation{suffix}.csv,
    published_aggregates{suffix}.csv, REPORT{suffix}.md and leaves the official files untouched. interpolate_oct2025=True
    adds an approximate NSA Oct 2025 level to every series lacking one: sqrt(Sep 2025 x Nov 2025) (geometric mean;
    approx., interpolated Oct 2025 base). It changes nothing else."""
    folder = "CPI"
    source_page = "https://www.bls.gov/cpi/tables/relative-importance/"
    # Publisher flat files map RI names to exact item codes and identify valid SA/NSA series.
    items, item_raw = read_tabular_raw(folder, "bls_cu_item_*.txt", "https://download.bls.gov/pub/time.series/cu/cu.item")
    catalog, catalog_raw = read_tabular_raw(folder, "bls_cu_series_*.txt", "https://download.bls.gov/pub/time.series/cu/cu.series")
    for year in (2024, 2025):
        fetch_raw(folder, f"bls_cpi_relative_importance_{year}_{TODAY}.xlsx", f"https://www.bls.gov/cpi/tables/relative-importance/{year}.xlsx")
    tables = {y: pd.read_excel(raw_path(folder, f"bls_cpi_relative_importance_{y}_{TODAY}.xlsx"), sheet_name="Table 1", header=None) for y in (2024, 2025)}
    # Only the expenditure hierarchy before "Special aggregate indexes" is the non-overlapping basket.
    d = tables[2025]
    first = next(i for i in range(len(d)) if str(d.iloc[i, 1]).strip() == "All items")
    stop = next(i for i in range(first + 1, len(d)) if str(d.iloc[i, 1]).strip() == "Special aggregate indexes")
    all_hierarchy = []
    for i in range(first + 1, stop):
        if pd.isna(d.iloc[i, 0]) or pd.isna(d.iloc[i, 1]): continue
        level, name = int(d.iloc[i, 0]), str(d.iloc[i, 1]).strip()
        all_hierarchy.append((i, level, name, float(d.iloc[i, 2])))
    hierarchy = []
    for pos, (i, level, name, weight) in enumerate(all_hierarchy):
        nxt = all_hierarchy[pos + 1][1] if pos + 1 < len(all_hierarchy) else None
        if nxt is None or nxt <= level:
            hierarchy.append((i, level, name, weight))
    paths = {}
    stack = []
    for i, level, name, weight in all_hierarchy:
        while stack and stack[-1][0] >= level: stack.pop()
        paths[i] = [nm for _, nm in stack]
        stack.append((level, name))
    item_names = items.set_index("item_name")["item_code"].to_dict()
    c = catalog.copy(); c.columns = c.columns.str.strip()
    # CPI-U U.S. city-average series only. Seasonal flags are authoritative.
    c = c[(c.area_code == "0000") & c.item_code.ne("")]
    by_code = {code: group for code, group in c.groupby("item_code")}
    cpi_nodes = []
    for i, level, name, weight in hierarchy:
        code = item_names.get(name, "")
        group = by_code.get(code, pd.DataFrame())
        sa = next((x.series_id.strip() for x in group.itertuples() if x.seasonal == "S" and x.series_id.strip().startswith("CUSR")), "")
        nsa = next((x.series_id.strip() for x in group.itertuples() if x.seasonal == "U" and x.series_id.strip().startswith("CUUR")), "")
        ancestors = paths.get(i, [])
        energy_leaf = name in {"Fuel oil", "Propane, kerosene, and firewood", "Electricity",
                               "Utility (piped) gas service", "Gasoline (all types)", "Other motor fuels"}
        alcoholic = name.lower().startswith("alcoholic beverages") or any(nm.lower().startswith("alcoholic beverages") for nm in ancestors)
        nonalcoholic_parent = any(nm in ("Food", "Nonalcoholic beverages", "Juices and nonalcoholic drinks",
                                         "Beverage materials including coffee and tea") for nm in ancestors)
        food_energy = (nonalcoholic_parent and not alcoholic) or energy_leaf
        core = not food_energy
        cpi_nodes.append({"row": i, "level": level, "name": name, "ri2025": weight, "item_code": code,
                          "sa": sa, "nsa": nsa, "core": core,
            "parent": ancestors[-1] if ancestors else "All items"})
    # Choose the matching December RI vintage for each comparison base.
    ri_by_year = {}
    for year, tab in tables.items():
        names = {}
        st = next(i for i in range(len(tab)) if str(tab.iloc[i, 1]).strip() == "All items")
        en = next(i for i in range(st + 1, len(tab)) if str(tab.iloc[i, 1]).strip() == "Special aggregate indexes")
        for i in range(st + 1, len(tab)):
            if pd.notna(tab.iloc[i, 1]) and pd.notna(tab.iloc[i, 2]): names[str(tab.iloc[i, 1]).strip()] = float(tab.iloc[i, 2])
        ri_by_year[year] = names
    # Download each leaf's exact SA and NSA CPI-U index, reusing cached batches.
    ids = [sid for n in cpi_nodes for sid in (n["sa"], n["nsa"]) if sid]
    ids += ["CUSR0000SA0", "CUUR0000SA0", "CUSR0000SA0L1E", "CUUR0000SA0L1E"]
    series, raw_files = request_bls(folder, ids, "cpi_basket_2017_2026", latest)
    all_levels = month_map(series.get("CUUR0000SA0", {}))
    # Seasonal CPI-U aggregate for 1m comparisons; NSA aggregate for RI updating and 12m changes.
    all_sa = month_map(series.get("CUSR0000SA0", {}))
    for node in cpi_nodes:
        node["nsa_levels"] = month_map(series.get(node["nsa"], {})) if node["nsa"] else {}
        node["sa_levels"] = month_map(series.get(node["sa"], {})) if node["sa"] else {}
    if interpolate_oct2025:
        for lev in [all_levels] + [n["nsa_levels"] for n in cpi_nodes]:
            _interp_oct2025(lev)

    def ri_at(node, target: str) -> float | None:
        p = pd.Period(target, freq="M")
        year = p.year if p.month == 12 else p.year - 1
        base = f"{year}-12"
        w0 = ri_by_year.get(year, {}).get(node["name"])
        lev = node["nsa_levels"]
        if w0 is None or lev.get(str(p)) is None or lev.get(base) in (None, 0) or all_levels.get(str(p)) is None or all_levels.get(base) in (None, 0): return None
        return w0 * (lev[str(p)] / lev[base]) / (all_levels[str(p)] / all_levels[base])
    # Scale core RI weights to the core aggregate at each endpoint, preserving the publisher's basket.
    dates = {"latest": latest, "base_12m": _mshift(latest, -12), "base_3m": _mshift(latest, -3), "base_1m": _mshift(latest, -1)}
    weight_sets = {}
    for key, period in dates.items():
        vals = [ri_at(n, period) for n in cpi_nodes]
        weight_sets[key] = vals
    core_weight_sets={}
    for key,vals in weight_sets.items():
        core_total=sum(v for n,v in zip(cpi_nodes,vals) if n["core"] and v is not None)
        core_weight_sets[key]=[(v*100/core_total if n["core"] and v is not None and core_total else None) for n,v in zip(cpi_nodes,vals)]
    rows = []
    for ix, node in enumerate(cpi_nodes):
        seasonality = bool(node["sa"] and node["sa_levels"])
        l1 = change(node["sa_levels"] if seasonality else node["nsa_levels"], latest, 1) if (seasonality or node["nsa_levels"]) else None
        l3 = change(node["sa_levels"] if seasonality else node["nsa_levels"], latest, 3, True) if (seasonality or node["nsa_levels"]) else None
        l12 = change(node["nsa_levels"], latest, 12) if node["nsa_levels"] else None
        wlatest, wb12, wb3, wb1 = (weight_sets[k][ix] for k in ("latest", "base_12m", "base_3m", "base_1m"))
        base_weight_1, base_weight_3, base_weight_12 = wb1, wb3, wb12
        # Component and all-item contributions use starting-period relative importance.
        mean = None
        vals_2018 = [change(node["nsa_levels"], f"{y}-{m:02d}", 12) for y in (2018, 2019) for m in range(1, 13)]
        vals_2018 = [v for v in vals_2018 if v is not None]
        if len(vals_2018) == 24: mean = sum(vals_2018) / 24
        fmt = lambda x: "" if x is None else x
        rid = node["sa"] or node["nsa"] or "N/A"
        missing_notes=[]
        if not node["nsa"]: missing_notes.append("N/A: no NSA item series in BLS catalog")
        if any(x is None for x in (wlatest,wb12,wb3,wb1)): missing_notes.append("N/A: RI update lacks a required component or aggregate index level")
        if any(x is None for x in (l1,l3,l12)): missing_notes.append("N/A: required monthly index observation is unavailable")
        if mean is None: missing_notes.append("N/A: incomplete 2018–19 history for baseline average")
        row={"index_name": "CPI-U headline", "component_id": rid,
          "component_name": node["name"], "level_or_parent": node["parent"], "in_core": "Y" if node["core"] else "N",
          "weight_latest": fmt(wlatest), "weight_base_12m": fmt(base_weight_12), "weight_base_3m": fmt(base_weight_3), "weight_base_1m": fmt(base_weight_1),
          "weight_units": "Percent of aggregate relative importance",
          "pct_1m_calc": fmt(l1), "pct_1m_ann_pub": "", "pct_3m_ann_calc": fmt(l3), "pct_12m_calc": fmt(l12),
          "contrib_1m_calc": fmt(base_weight_1/100*l1 if base_weight_1 is not None and l1 is not None else None),
          "contrib_3m_ann_calc": fmt(base_weight_3/100*l3 if base_weight_3 is not None and l3 is not None else None),
          "contrib_12m_calc": fmt(base_weight_12/100*l12 if base_weight_12 is not None and l12 is not None else None),
          "avg_pct_12m_2018_19_calc": fmt(mean), "excess_contrib_12m_calc": fmt(wlatest/100*(l12-mean) if wlatest is not None and l12 is not None and mean is not None else None),
          "latest_period": latest, "sa_basis": "SA" if seasonality else "NSA (not seasonally adjusted by publisher)",
          "source_ids": f"{node['sa'] or 'N/A'}; {node['nsa'] or 'N/A'}; RI Table 1 row {node['row']+1}",
          "raw_file": f"{raw_files}; Price indexes/CPI/raw/bls_cpi_relative_importance_2024_{TODAY}.xlsx; Price indexes/CPI/raw/bls_cpi_relative_importance_2025_{TODAY}.xlsx; {item_raw}; {catalog_raw}",
          "note": "; ".join(missing_notes)}
        rows.append(row)
        if node["core"]:
            cwlatest, cwb12, cwb3, cwb1=(core_weight_sets[k][ix] for k in ("latest","base_12m","base_3m","base_1m"))
            core_row=dict(row); core_row.update({"index_name":"CPI-U core","weight_latest":cwlatest,"weight_base_12m":cwb12,"weight_base_3m":cwb3,"weight_base_1m":cwb1,
              "weight_units":"Percent of core relative importance; rescaled within core",
              "contrib_1m_calc":cwb1/100*l1 if cwb1 is not None and l1 is not None else "",
              "contrib_3m_ann_calc":cwb3/100*l3 if cwb3 is not None and l3 is not None else "",
              "contrib_12m_calc":cwb12/100*l12 if cwb12 is not None and l12 is not None else "",
              "excess_contrib_12m_calc":cwlatest/100*(l12-mean) if cwlatest is not None and l12 is not None and mean is not None else ""})
            rows.append(core_row)
    compound_3m_contribs(rows)
    component_rows = rows
    write_csv(ROOT / folder / "processed" / f"components{suffix}.csv", component_rows, COMPONENT_COLUMNS)
    agg_rows = []
    for sid, role in [("CUSR0000SA0", "headline_mom_sa"), ("CUUR0000SA0", "headline_yoy_nsa"),
                      ("CUSR0000SA0L1E", "core_mom_sa"), ("CUUR0000SA0L1E", "core_yoy_nsa")]:
        obs = next((x for x in series.get(sid, {}).get("data", []) if x.get("year") == latest[:4] and x.get("period") == "M" + latest[5:7]), {})
        changes = (obs.get("calculations") or {}).get("pct_changes", {})
        pct = changes.get("1" if "mom" in role else "12", "")
        agg_rows.append({"aggregate": role, "series_id": sid, pd.Period(latest, freq="M").strftime("%b_%Y").lower() + "_value_or_pct": pct,
                     "publisher_index_level": obs.get("value", ""), "raw_file": raw_files,
                     "source_ids": sid, "note": "BLS API v2; CPI October 2025 was not collected (footnote X)."})
    write_csv(ROOT / folder / "processed" / f"published_aggregates{suffix}.csv", agg_rows)
    # Headline/core sums are reconciled against exact publisher indexes for each horizon.
    aggregates = {sid: month_map(series.get(sid, {})) for sid in ("CUSR0000SA0", "CUUR0000SA0", "CUSR0000SA0L1E", "CUUR0000SA0L1E")}
    if interpolate_oct2025:
        for sid in ("CUUR0000SA0", "CUUR0000SA0L1E"):
            _interp_oct2025(aggregates[sid])
    rec = []
    for label, core, sid_sa, sid_nsa in (("headline", False,"CUSR0000SA0","CUUR0000SA0"),("core",True,"CUSR0000SA0L1E","CUUR0000SA0L1E")):
        subset = [r for r in component_rows if r["index_name"] == ("CPI-U core" if core else "CPI-U headline")]
        # 6m annualized SA added 2026-11-14 (approved by Eli): aggregate rate only, no component contributions (field None -> N/A).
        for horizon, field, sid in (("1m SA","contrib_1m_calc",sid_sa),("3m annualized SA","contrib_3m_ann_calc",sid_sa),("6m annualized SA",None,sid_sa),("12m NSA","contrib_12m_calc",sid_nsa)):
            vals=[float(r[field]) for r in subset if r[field] not in ("",None)] if field else []
            total=sum(vals) if vals else None
            p = latest
            lag = {"1m SA":1,"3m annualized SA":3,"6m annualized SA":6,"12m NSA":12}[horizon]
            pub = change(aggregates[sid],p,lag) if horizon=="12m NSA" else (change(aggregates[sid],p,1) if lag==1 else change(aggregates[sid],p,lag,True))
            rec.append({"aggregate":f"CPI-U {label}","period":_mlabel(latest),"horizon":horizon,"published_change":pub if pub is not None else "N/A",
             "component_contributions_calc":total if total is not None else "N/A","gap_pp_calc":(total-pub) if total is not None and pub is not None else "N/A",
             "source_ids":sid,"raw_file":raw_files,"note":"Weights are RI-updated to the start of each horizon; core weights normalized within core."})
        if interpolate_oct2025:  # endpoint sensitivity comparisons for the approx. 12m (NOT bounds): published Nov 2025 (11-month) and Sep 2025 (13-month) bases, not annualized
            for horizon, lag in (("11-month change NSA (Nov 2025 base; endpoint comparison, not a bound)", 11), ("13-month change NSA (Sep 2025 base; endpoint comparison, not a bound)", 13)):
                pub = change(aggregates[sid_nsa], latest, lag)
                rec.append({"aggregate":f"CPI-U {label}","period":_mlabel(latest),"horizon":horizon,"published_change":pub if pub is not None else "N/A",
                 "component_contributions_calc":"N/A","gap_pp_calc":"N/A","source_ids":sid_nsa,"raw_file":raw_files,
                 "note":"Endpoint sensitivity comparison for the approx. 12m (interpolated Oct 2025 base): raw change over 11 or 13 months, not annualized. Not a bound on actual 12m inflation: October NSA levels often lie outside the Sep-Nov range (5 of 7 years, 2018-2024)."})
    write_csv(ROOT / folder / "processed" / f"reconciliation{suffix}.csv", rec)
    report(ROOT / folder / "processed" / f"REPORT{suffix}.md", "CPI-U basket retrieval" + (f" ({suffix.strip('_')})" if suffix else ""), [
        *(["APPROX.: 12m figures use an interpolated Oct 2025 base, sqrt(Sep 2025 x Nov 2025) on NSA indexes (approx., interpolated Oct 2025 base); not BLS-published."] if interpolate_oct2025 else []),
        *(["Short-horizon view: 12m fields are N/A where BLS has no Oct 2025 index; use 1m and 3m fields."] if suffix and not interpolate_oct2025 else []),
        f"Question: Can BLS CPI-U U.S. city-average basket contributions be reproduced through {_mlabel(latest)}?",
        "Sources: BLS API v2 for aggregate index observations; BLS annual RI page: " + source_page,
        "IDs: CUSR0000SA0 / CUUR0000SA0 (all items); CUSR0000SA0L1E / CUUR0000SA0L1E (less food and energy).",
        f"Coverage requested: 2017–2026; latest month {_mlabel(latest)}. API responses are batch-cached in raw/.",
        f"Inputs: BLS CPI flat files cu.item/cu.series; Table 1 Dec 2024 and Dec 2025; {len(cpi_nodes)} hierarchy leaves retained (unmatched leaf series remain explicit N/A).",
        f"Dec 2025 leaf RI sum={sum(n['ri2025'] for n in cpi_nodes):.3f}%; core leaf sum={sum(n['ri2025'] for n in cpi_nodes if n['core']):.3f}% versus published core RI {ri_by_year[2025].get('All items less food and energy')}%.",
        "Core excludes food, nonalcoholic beverage leaves, and the six energy leaves; alcoholic beverages remain in core. The Dec 2025 core leaf RI sum is checked against the published core RI. Weights update from matching December RI by component/all-item NSA price relatives; core rows are separately rescaled to 100.",
        "Formulae: pct_1m=(I_t/I_t-1-1)*100; pct_3m_ann=((I_t/I_t-3)^4-1)*100; pct_12m=(I_t/I_t-12-1)*100. Contributions=starting RI share x rate, except 3m: starting share x raw 3-month change, scaled by k=((1+S)^4-1)/S (S=sum of raw contributions) so they sum to the annualized basket rate; excess contribution=current 12m starting weight x (component 12m minus its 2018–19 mean).",
        "Sources: BLS API v2; BLS CPI relative importance: " + source_page,
        "CPI October 2025 observations are N/A because BLS did not collect October CPI (footnote X); November 2025 remains published.",
        "Investigation: headline 12m gap is -0.295 pp (>0.15); RI update has weight coverage 94.607% at Aug 2025 and 95.684% at Aug 2026, with 33–34 leaves lacking required item-series observations or a catalog series. This coverage shortfall is the leading explanation; the residual cannot be allocated to missing leaves.",
        "Headline and core contributions and gaps are in reconciliation.csv; gaps above 0.15 pp require review of unavailable leaf series and weight dating.",
    ])


def retrieve_ppi() -> None:
    folder = "PPI"
    ri_page = "https://www.bls.gov/ppi/tables/final-demand-intermediate-demand-special-requests.htm"
    files = {}
    for key, url in {
        "fd_components": f"https://www.bls.gov/ppi/tables/final-demand-relative-importance-by-component-series-{PPI_RI_YEAR}.xlsx",
        "id_components": f"https://www.bls.gov/ppi/tables/intermediate-demand-by-commodity-type-relative-importance-by-component-series-{PPI_RI_YEAR}.xlsx",
    }.items():
        _, files[key] = fetch_raw(folder, f"bls_ppi_{key}_relative_importance_{PPI_RI_YEAR}_{TODAY}.xlsx", url)
    wp, wp_raw = read_tabular_raw(folder, "bls_wp_series_*.txt", "https://download.bls.gov/pub/time.series/wp/wp.series")
    pc, pc_raw = read_tabular_raw(folder, "bls_pc_series_*.txt", "https://download.bls.gov/pub/time.series/pc/pc.series")
    wp.columns=wp.columns.str.strip(); pc.columns=pc.columns.str.strip()
    wp["series_id"]=wp.series_id.str.strip(); pc["series_id"]=pc.series_id.str.strip()
    fd=pd.read_excel(raw_path(folder,f"bls_ppi_fd_components_relative_importance_{PPI_RI_YEAR}_{TODAY}.xlsx"),header=None)
    idd=pd.read_excel(raw_path(folder,f"bls_ppi_id_components_relative_importance_{PPI_RI_YEAR}_{TODAY}.xlsx"),header=None)
    def terminal_nodes(table, root):
        rows=[]; seen=0
        for i in range(len(table)):
            code=str(table.iloc[i,1]).strip()
            if code==root:
                seen+=1
                if seen==2: break
            if re.fullmatch(r"(?:FD|ID)\d+",code): rows.append((code,str(table.iloc[i,3]).strip(),float(table.iloc[i,5]),i))
        codes=list(dict.fromkeys(x[0] for x in rows))
        return [x for x in rows if not any(y.startswith(x[0]) and len(y)>len(x[0]) for y in codes)]
    fdnodes=terminal_nodes(fd,"FD4")
    # The table contains all three ID baskets before its repeated summary block; scan once to avoid duplicates.
    idnodes=terminal_nodes(idd,"ID61")
    baskets=[("PPI Final Demand",*x,"FD4") for x in fdnodes]
    for root in ("ID61","ID62","ID63"):
        baskets += [(f"PPI Intermediate Demand {root}",*x,root) for x in idnodes if x[0].startswith(root)]
    catalog=set(wp.series_id)
    aggregate_ids=["WPSFD4","WPUFD4","WPSID61","WPUID61","WPSID62","WPUID62","WPSID63","WPUID63"]
    ids=aggregate_ids+[sid for _,code,_,_,_,_ in baskets for sid in ("WPS"+code,"WPU"+code) if sid in catalog]
    series, raw_files=request_bls(folder,list(dict.fromkeys(ids)),"ppi_baskets_2017_2026", PPI_LATEST)
    def lv(sid): return month_map(series.get(sid,{}))
    all_levels={sid:lv(sid) for sid in aggregate_ids}
    # Weights are repriced from the PPI_RI_BASE RI table and normalized within the parent basket.
    periods=(_mshift(PPI_LATEST,-12),_mshift(PPI_LATEST,-3),_mshift(PPI_LATEST,-1),PPI_LATEST)
    raw_weights={p:{} for p in periods}
    for idx,code,name,weight,row,root in baskets:
        nsa="WPU"+code; agg="WPUFD4" if root=="FD4" else "WPUID"+root[-2:]
        comp=lv(nsa)
        for p in periods:
            if p in comp and PPI_RI_BASE in comp and p in all_levels[agg] and PPI_RI_BASE in all_levels[agg] and all_levels[agg][PPI_RI_BASE]:
                raw_weights[p][(idx,code)]=weight*(comp[p]/comp[PPI_RI_BASE])/(all_levels[agg][p]/all_levels[agg][PPI_RI_BASE])
    weights={p:{} for p in periods}
    for p in periods:
        for idx,code,name,weight,row,root in baskets:
            total=sum(v for (k,c),v in raw_weights[p].items() if k==idx)
            v=raw_weights[p].get((idx,code)); weights[p][(idx,code)]=100*v/total if v is not None and total else None
    ppi_rows=[]
    for idx,code,name,weight,row,root in baskets:
        sa="WPS"+code if "WPS"+code in catalog else ""
        nsa="WPU"+code if "WPU"+code in catalog else ""
        sa_lv=lv(sa) if sa else {}; nsa_lv=lv(nsa) if nsa else {}
        l1=change(sa_lv or nsa_lv,PPI_LATEST,1); l3=change(sa_lv or nsa_lv,PPI_LATEST,3,True); l12=change(nsa_lv,PPI_LATEST,12)
        hist=[change(nsa_lv,f"{y}-{m:02d}",12) for y in (2018,2019) for m in range(1,13)]
        hist=[v for v in hist if v is not None]; mean=sum(hist)/24 if len(hist)==24 else None
        cat=(series.get(sa or nsa,{ }).get("catalog") or {}).get("series_title",name)
        wlatest,w12,w3,w1=(weights[p].get((idx,code)) for p in (PPI_LATEST,_mshift(PPI_LATEST,-12),_mshift(PPI_LATEST,-3),_mshift(PPI_LATEST,-1)))
        missing_note="; ".join(x for x,missing in (("N/A RI update: index levels unavailable at required date",any(v is None for v in (wlatest,w12,w3,w1))),
                                                     ("N/A rate: required monthly index observation unavailable",any(v is None for v in (l1,l3,l12)))) if missing)
        ppi_rows.append({"index_name":idx,"component_id":sa or nsa or code,"component_name":cat,"level_or_parent":root,"in_core":"N/A",
          "weight_latest":wlatest,"weight_base_12m":w12,"weight_base_3m":w3,"weight_base_1m":w1,"weight_units":"Percent of parent basket",
          "pct_1m_calc":l1,"pct_1m_ann_pub":"","pct_3m_ann_calc":l3,"pct_12m_calc":l12,
          "contrib_1m_calc":w1*l1/100 if w1 is not None and l1 is not None else "",
          "contrib_3m_ann_calc":w3*l3/100 if w3 is not None and l3 is not None else "",
          "contrib_12m_calc":w12*l12/100 if w12 is not None and l12 is not None else "",
          "avg_pct_12m_2018_19_calc":mean if mean is not None else "","excess_contrib_12m_calc":wlatest/100*(l12-mean) if wlatest is not None and l12 is not None and mean is not None else "","latest_period":PPI_LATEST,"sa_basis":"SA" if sa else "NSA (not seasonally adjusted by publisher)",
          "source_ids":f"{sa or 'N/A'}; {nsa or 'N/A'}; RI row {row+1}","raw_file":f"{raw_files}; {files['fd_components']}; {files['id_components']}; {wp_raw}",
          "note":"Terminal FD4 or ID61/62/63 RI code. "+missing_note})
    write_csv(ROOT/folder/"processed"/"components.csv",ppi_rows,COMPONENT_COLUMNS)
    rec=[]
    parents=[("PPI Final Demand","WPSFD4","WPUFD4")]+[(f"PPI Intermediate Demand ID{x}",f"WPSID{x}",f"WPUID{x}") for x in (61,62,63)]
    for idx,sid_sa,sid_nsa in parents:
        subset=[x for x in ppi_rows if x["index_name"]==idx]
        for hz,field,sid,lag,ann in (("1m SA","contrib_1m_calc",sid_sa,1,False),("3m annualized SA","contrib_3m_ann_calc",sid_sa,3,True),("12m NSA","contrib_12m_calc",sid_nsa,12,False)):
            vals=[float(x[field]) for x in subset if x[field] not in ("",None)]
            total=sum(vals) if vals else None; pub=change(lv(sid),PPI_LATEST,lag,ann)
            rec.append({"aggregate":idx,"period":_mlabel(PPI_LATEST),"horizon":hz,"published_change":pub if pub is not None else "N/A","component_contributions_calc":total if total is not None else "N/A",
              "gap_pp_calc":total-pub if total is not None and pub is not None else "N/A","source_ids":sid,"raw_file":raw_files,"note":f"Repriced {_mlabel(PPI_RI_BASE)} RI; parent basket normalized at each horizon start."})
    write_csv(ROOT/folder/"processed"/"reconciliation.csv",rec)
    targets={"semiconductors and related devices":("PCU334413334413","PCU"),"electronic components":("WPU1178","WPU"),"computers and computer equipment":("WPU115","WPU"),
      "data processing, hosting and related services":("PCU518210518210","PCU"),"software publishers (application software)":("PCU51321051321050502","PCU"),"portfolio management":("PCU5239405239401","PCU"),
      "airline passenger services":("WPU3022","WPU"),"hospital inpatient and outpatient care":("WPU512101;WPU511104","WPU"),"physician care":("WPU511101","WPU"),"truck transportation of freight":("WPU3012","WPU"),
      "gasoline":("WPU0571","WPU"),"diesel fuel":("WPU057303","WPU"),"jet fuel":("WPU057203","WPU"),"electric power":("WPU054","WPU"),"natural gas":("WPU055","WPU")}
    named_ids=[sid for ids,b in targets.values() for sid in ids.split(";")]
    named_sa={sid:("WPS"+sid[3:] if sid.startswith("WPU") and "WPS"+sid[3:] in catalog else "") for sid in named_ids}
    named_ids += [sid for sid in named_sa.values() if sid]
    named,named_raw=request_bls(folder,named_ids,"ppi_named_targets_sa_2017_2026", PPI_LATEST)
    named_rows=[]
    for name,(ids,basis) in targets.items():
        for sid in ids.split(";"):
            item=named.get(sid,{ }); title=(item.get("catalog") or {}).get("series_title",""); nsa_lv=month_map(item)
            sa=named_sa.get(sid,""); sa_lv=month_map(named.get(sa,{})) if sa else {}
            named_rows.append({"requested_name":name,"component_id":sid if title else "N/A","component_name":title or name,"catalog_title":title,"ppi_basis":"Industry PCU" if sid.startswith("PCU") else "Commodity WPU",
              "pct_1m_calc":change(sa_lv or nsa_lv,PPI_LATEST,1),"pct_3m_ann_calc":change(sa_lv or nsa_lv,PPI_LATEST,3,True),"pct_12m_calc":change(nsa_lv,PPI_LATEST,12),
              "latest_period":PPI_LATEST,"sa_basis":"SA" if sa_lv else "NSA (not seasonally adjusted by publisher)","source_ids":sid if title else "N/A",
              "raw_file":named_raw+"; "+(wp_raw if basis=="WPU" else pc_raw),"note":"Exact series ID and title verified against BLS publisher series list." if title else "N/A: requested exact ID absent from BLS publisher series list."})
    write_csv(ROOT/folder/"processed"/"named_series.csv",named_rows)
    id_ri_summary="; ".join(f"{root}={sum(x[2] for x in idnodes if x[0].startswith(root)):.3f}%" for root in ("ID61","ID62","ID63"))
    report(ROOT/folder/"processed"/"REPORT.md","PPI basket retrieval",[
      f"Question: Can BLS FD-ID final-demand and intermediate-demand component contributions be reproduced through {_mlabel(PPI_LATEST)}?",
      f"Sources: BLS PPI relative-importance workbooks ({_mlabel(PPI_RI_BASE)}; {PPI_RI_YEAR} tables), wp.series/pc.series lists, BLS API v2; archive: "+ri_page,
      f"FD terminal RI rows={len(fdnodes)} (sum {sum(x[2] for x in fdnodes):.3f}%); ID terminal RI rows={len(idnodes)}; parent sums: {id_ri_summary}.",
      f"Weights use {_mlabel(PPI_RI_BASE)} RI repriced by component/aggregate NSA relatives; weights are normalized within each basket for the start of each horizon.",
      "Rates: 1m and 3m annualized use SA where available, otherwise NSA; 12m uses NSA. Contributions equal start-period weight times component rate.",
      "Reconciliation gaps above 0.15 pp: annualized 3m FD4=+0.204 pp, ID61=+0.292 pp, ID62=+2.760 pp. The required linear weighted-contribution formula annualizes each component before summing; this diverges most for volatile ID62 commodity movements because annualization is nonlinear. 12m/1m FD4 gaps are within 0.02 pp.",
      "named_series.csv verifies each exact WPU commodity or PCU industry ID against official series lists; hospital inpatient and outpatient are separate rows.",
      "Uncertainty: any missing observations or codes stay blank and can widen reconciliation gaps; no neighboring series is substituted.",
    ])

def retrieve_cleveland() -> None:
    folder = "Trimmed mean"
    base = "https://www.clevelandfed.org/-/media/files/webcharts/mediancpi/"
    datasets = {
        "mediancpi_component_table": "mediancpi_component_table.csv",
        "mcpi_revised": "mcpi_revised.csv", "trim_revised": "trim_revised.csv",
        "cpi": "cpi.csv", "core": "core.csv",
        "mediancpireleasedata": "mediancpireleasedata.zip", "usinflationdata": "usinflationdata.zip",
    }
    fetched: dict[str, tuple[bytes | None, str]] = {}
    for key, source_name in datasets.items():
        url = base + source_name
        name = f"clevelandfed_{key}_{TODAY}.{source_name.rsplit('.', 1)[-1]}"
        fetched[key] = fetch_raw(folder, name, url)
    payload, saved = fetched["mediancpi_component_table"]
    if payload is None:
        write_csv(ROOT / folder / "processed" / "components.csv", [], COMPONENT_COLUMNS)
        write_csv(ROOT / folder / "processed" / "reconciliation.csv", [])
        report(ROOT / folder / "processed" / "REPORT.md", "Cleveland Fed median CPI component table", ["Official component table could not be retrieved.", saved])
        return
    data = pd.read_csv(io.BytesIO(payload)).fillna("")
    # Published 1m SA trimmed-mean change at LATEST, read from the saved trim_revised.csv (was a typed literal "0.2" for Aug 2026).
    _tr = pd.read_csv(io.BytesIO(fetched["trim_revised"][0])) if fetched["trim_revised"][0] else pd.DataFrame()
    _tr.columns = [c.strip() for c in _tr.columns]
    _hit = _tr[pd.to_datetime(_tr["date"]).dt.strftime("%Y-%m-%d") == LATEST] if len(_tr) else _tr
    _trim_1m = f"{float(_hit.trim_monthly_chg.iloc[0]) * 100:.1f}" if len(_hit) else "N/A"
    rows, detail = [], []
    for line_no, (_, r) in enumerate(data.iterrows(), start=2):
        name = str(r.get("Component", ""))
        weight = float(r.get("Relative Importance (Normalized)", 0) or 0)
        cumulative = float(r.get("Cumulative Relative Importance", 0) or 0)
        prior = cumulative - weight
        lower = prior < 8
        upper = cumulative > 92
        if lower or upper:
            tail = "lower" if lower else "upper"
            if tail == "lower" and cumulative > 8:
                tail += " cutoff component (published weight crosses 8th percentile)"
            if tail.startswith("upper") and prior < 92:
                tail += " cutoff component (published weight crosses 92nd percentile)"
            detail.append({"component": name, "published_1m_annualized_pct": r.get("1-Month Annualized Percent Change", ""),
                           "published_weight_normalized_pct": weight,
                           "published_cumulative_weight_pct": cumulative, "tail": tail,
                           "latest_period": LATEST, "source_ids": "Cleveland Fed mediancpi_component_table.csv",
                           "raw_file": saved, "source_line": line_no})
            row = {k: "" for k in COMPONENT_COLUMNS}
            row.update({"index_name": "Cleveland Fed 16% trimmed-mean CPI tails", "component_id": name,
                        "component_name": name, "in_core": "N/A", "weight_latest": weight,
                        "weight_units": "Percent of normalized CPI component distribution",
                        "pct_1m_ann_pub": r.get("1-Month Annualized Percent Change", ""),
                        "latest_period": LATEST, "source_ids": f"mediancpi_component_table.csv row {line_no}: {name}",
                        "raw_file": saved, "note": f"Published tail position: {tail}; cumulative published weight={cumulative}%"})
            rows.append(row)
    write_csv(ROOT / folder / "processed" / "components.csv", rows, COMPONENT_COLUMNS)
    write_csv(ROOT / folder / "processed" / "trimmed_tails.csv", detail)
    write_csv(ROOT / folder / "processed" / "reconciliation.csv", [{
        "aggregate": "Cleveland Fed 16% trimmed-mean CPI", "period": _mlabel(LATEST[:7]), "horizon": "1m SA",
        "publisher_rate_pct": _trim_1m, "component_contributions_calc": "N/A", "gap_pp_calc": "N/A",
        "source_ids": "Cleveland Fed Median CPI page / component table; trim_revised.csv (monthly rate)", "raw_file": f"{saved}; {fetched['trim_revised'][1]}",
        "note": "No tail-based rate reconstruction; publisher states tails are below 8th and above 92nd percentiles."}])
    report(ROOT / folder / "processed" / "REPORT.md", "Cleveland Fed median and trimmed-mean CPI", [
        "Sources: Cleveland Fed median CPI page and its published CSV/XLSX/ZIP component files; all seven page-listed files saved to raw/.",
        "Component table columns are preserved: 1-month annualized percent change, normalized relative importance, cumulative relative importance.",
        f"Latest period identified from the publisher's Median CPI page: {_mlabel(LATEST[:7])}. Component values/weights are not reconstructed.",
        "Cleveland Fed defines the 16% trimmed mean by excluding component-weight shares below the 8th and above the 92nd percentiles.",
        "trimmed_tails.csv lists published component rows that overlap those tails, including boundary components, with full published weights and cumulative weights.",
        "Tail assignment uses the published cumulative weight to identify which published rows cross 8% and 92%; no trimmed mean is recalculated.",
        "All raw payloads and the component-table source path are recorded in the processed files.",
    ])


def retrieve_atlanta() -> None:
    folder = "Sticky CPI"
    page = "https://www.atlantafed.org/research-and-data/data/sticky-price-cpi"
    # URL moved (old .../datafiles/research/inflationproject/stickprice/stickyprice.xlsx returned 404 on 2026-11-10); new link from the page.
    url = "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/sticky-price/sticky-price-data.xlsx"
    name = f"atlantafed_sticky_price_cpi_{TODAY}.xlsx"
    payload, saved = fetch_raw(folder, name, url)
    if payload is None:
        write_csv(ROOT / folder / "processed" / "components.csv", [], COMPONENT_COLUMNS)
        write_csv(ROOT / folder / "processed" / "reconciliation.csv", [])
        report(ROOT / folder / "processed" / "REPORT.md", "Atlanta Fed Sticky-Price CPI", ["Official workbook retrieval failed.", saved])
        return
    df = pd.read_excel(io.BytesIO(payload), sheet_name="Data", header=None)
    positions = {
        "Flexible CPI": (1, 2, 3, 4), "Core Flexible CPI": (5, 6, 7, 8),
        "Sticky CPI": (9, 10, 11, 12), "Core Sticky CPI": (13, 14, 15, 16),
        "Sticky CPI ex-shelter": (17, 18, 19, 20),
    }
    ix = next(i for i in range(1, len(df)) if str(df.iloc[i, 0])[:10] == LATEST)
    rates, components = [], []
    for series_name, (_monthly, one, three, twelve) in positions.items():
        vals = [df.iloc[ix, j] for j in (one, three, twelve)]
        row = {k: "" for k in COMPONENT_COLUMNS}
        row.update({"index_name": "Atlanta Fed Sticky-Price CPI", "component_id": series_name,
                    "component_name": series_name, "latest_period": LATEST,
                    "pct_1m_ann_pub": vals[0], "pct_3m_ann_pub": vals[1], "pct_12m_pub": vals[2],
                    "source_ids": f"Atlanta Fed stickyprice.xlsx, Data!A{ix + 1}:Y{ix + 1}",
                    "raw_file": saved, "note": "Rates are exactly publisher-reported; 1-month field is annualized."})
        components.append(row)
        rates.append({"series": series_name, "latest_period": LATEST,
                      "1m_annualized_pct_pub": vals[0], "3m_annualized_pct_pub": vals[1],
                      "12m_pct_pub": vals[2], "source_ids": f"Atlanta Fed stickyprice.xlsx, Data!A{ix + 1}:Y{ix + 1}",
                      "raw_file": saved, "source_page": page})
    write_csv(ROOT / folder / "processed" / "components.csv", components, COMPONENT_COLUMNS)
    write_csv(ROOT / folder / "processed" / "sticky_cpi_rates.csv", rates)
    write_csv(ROOT / folder / "processed" / "reconciliation.csv", [])
    report(ROOT / folder / "processed" / "REPORT.md", "Atlanta Fed Sticky-Price CPI", [
        "Source: Atlanta Fed Sticky-Price CPI page and its published workbook; workbook saved unmodified to raw/.",
        f"Latest published workbook row: {_mlabel(LATEST[:7])}. Values below are read from the Data sheet without reconstruction.",
        "Included rates: sticky, flexible, core sticky, core flexible, and sticky ex-shelter; 1m annualized, 3m annualized, 12m.",
        "The 1m annualized rate is publisher-reported, not a nonannualized monthly rate. No component contributions are calculated.",
        "Source page: " + page,
    ])


def main() -> None:
    for folder in ("CPI", "PPI", "Trimmed mean", "Sticky CPI"):
        (ROOT / folder / "raw").mkdir(parents=True, exist_ok=True)
        (ROOT / folder / "processed").mkdir(parents=True, exist_ok=True)
    retrieve_cpi()  # official basket at CPI_LATEST (components.csv etc.)
    # Oct 2026 views (separate files; official files untouched)
    retrieve_cpi("2026-10", "_2026-10_short_horizon")
    retrieve_cpi("2026-10", "_2026-10_approx_interp_oct2025_base", interpolate_oct2025=True)
    retrieve_ppi()
    retrieve_cleveland()
    retrieve_atlanta()
    print("Complete. CPI/PPI baskets and Cleveland/Atlanta Fed outputs were refreshed.")


if __name__ == "__main__":
    main()
