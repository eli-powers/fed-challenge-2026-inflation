"""Parsers for the forecast_3b pipeline. No network access in this module.

Provenance: the SPF/STEO/FRED parsers below are copied (verbatim logic, lightly trimmed) from
02_Research/Subtasks/12_slide3b_research/code/A_common.py (Agent A, coordinator-verified 2026-11-15),
so the pipeline does not depend on a research-subtask folder. Changes vs A_common:
  * parse_release_dates strips the '*' footnote markers the Philadelphia Fed adds to delayed surveys;
  * parse_steo_release_dates is generalized from A_05_oil.py (any year, not only 2026);
  * read_eia_daily is from B_q3_build.py (Agent B).

SPF core PCE variables (SPF documentation, "COREPCE"): COREPCE1 = quarter before the survey quarter
(BEA advance estimate known to forecasters), COREPCE2 = survey quarter, COREPCE3..6 = next four quarters;
COREPCEA/B/C = Q4/Q4 for the survey year, +1, +2. Units: percent, annual rate, SA. Quarterly =
annualized q/q change of the quarterly-average index.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

SPF_Q_VARS = ["COREPCE1", "COREPCE2", "COREPCE3", "COREPCE4", "COREPCE5", "COREPCE6"]
SPF_A_VARS = ["COREPCEA", "COREPCEB", "COREPCEC"]
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


# ----------------------------------------------------------------------------- quarters
def qidx(label: str) -> int:
    return int(label[:4]) * 4 + int(label[-1]) - 1


def qlabel(idx: int) -> str:
    return f"{idx // 4}Q{idx % 4 + 1}"


def qrange(start: str, end: str) -> list[str]:
    return [qlabel(i) for i in range(qidx(start), qidx(end) + 1)]


def quarter_of(date) -> str:
    d = pd.Timestamp(date)
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


# ----------------------------------------------------------------------------- SPF
def read_spf_median(path, var="COREPCE") -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    sheet = var if var in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].map(_num)
    return df


def surveys_present(df: pd.DataFrame, probe="COREPCE2") -> list[str]:
    ok = df.dropna(subset=[probe])
    return [f"{int(r.YEAR)}Q{int(r.QUARTER)}" for r in ok.itertuples()]


def median_row(df: pd.DataFrame, survey: str) -> pd.Series:
    y, q = int(survey[:4]), int(survey[-1])
    r = df[(df["YEAR"] == y) & (df["QUARTER"] == q)]
    if r.empty:
        raise ValueError(f"survey {survey} not in SPF median file")
    return r.iloc[0]


def horizon_map(survey: str) -> dict:
    """variable -> target quarter (quarterly vars) or target year (annual vars)."""
    s = qidx(survey)
    m = {v: qlabel(s + k - 2) for k, v in enumerate(SPF_Q_VARS, start=1)}
    y = int(survey[:4])
    m.update({v: y + j for j, v in enumerate(SPF_A_VARS)})
    return m


def read_dispersion_d1(path, var="COREPCE") -> dict:
    """Dispersion_1.xlsx: {'2026Q3': {offset k (0..4): (p25, p75, d1)}}; offset 0 = survey quarter (COREPCE2).
    Published for quarterly horizons T..T+4 only (no annual horizons in this file)."""
    raw = pd.read_excel(path, sheet_name=var, header=None)
    hdr_i = raw.index[raw[0].astype(str).str.startswith("Survey_Date")][0]
    out = {}
    for _, r in raw.iloc[hdr_i + 1:].iterrows():
        lab = str(r[0]).strip()
        if not re.fullmatch(r"\d{4}Q\d", lab):
            continue
        d = {}
        for k in range(5):
            p25, p75, d1 = (_num(r[1 + 3 * k + j]) for j in range(3))
            if not np.isnan(p25):
                d[k] = (p25, p75, d1)
        out[lab] = d
    return out


def parse_release_dates(path, survey: str):
    """(deadline ISO, release ISO, raw line) for a survey from spf-release-dates.txt; None if absent."""
    year, q = int(survey[:4]), int(survey[-1])
    cur_year = None
    for line in Path(path).read_text(errors="replace").splitlines():
        m = re.match(r"^\s*(\d{4})\s+Q([1-4])\s+(\S+)\s+(\S+)", line)
        if m:
            cur_year, qq, a, b = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4)
        else:
            m = re.match(r"^\s+Q([1-4])\s+(\S+)\s+(\S+)", line)
            if not m or cur_year is None:
                continue
            qq, a, b = int(m.group(1)), m.group(2), m.group(3)
        if cur_year == year and qq == q:
            f = lambda s: dt.datetime.strptime(s.strip("*"), "%m/%d/%y").date().isoformat()
            return f(a), f(b), line.strip()
    return None


# ----------------------------------------------------------------------------- derivations
def derive_q4_from_annual(q1, q2, q3, q4q4_pct):
    """q4 (annualized %) such that Q4/Q4 = prod_{i=1..4}(1+q_i/100)^(1/4) - 1."""
    prod = np.prod([1 + v / 100 for v in (q1, q2, q3)])
    return 100 * ((1 + q4q4_pct / 100) ** 4 / prod - 1)


# ----------------------------------------------------------------------------- FRED / core PCE
def load_fred_obs(path) -> pd.Series:
    d = json.load(open(path))
    s = pd.Series({pd.Timestamp(o["date"]): _num(o["value"]) for o in d["observations"]}).dropna()
    return s.sort_index()


def quarterly_avg(monthly: pd.Series) -> pd.Series:
    """Quarterly average of a monthly series (complete quarters only), indexed 'YYYYQn'."""
    g = monthly.groupby(monthly.index.to_period("Q"))
    avg, cnt = g.mean(), g.count()
    avg = avg[cnt == 3]
    avg.index = [f"{p.year}Q{p.quarter}" for p in avg.index]
    return avg


# ----------------------------------------------------------------------------- STEO
def read_steo_series(path, series_id="BREPUUS", sheet="2tab") -> pd.Series:
    """Monthly series from a STEO archive workbook (<mon><yy>_base.xlsx). BREPUUS = Brent spot, $/bbl."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    years = raw.iloc[2, 2:].ffill()
    months = raw.iloc[3, 2:]
    row = raw[raw[0] == series_id]
    if row.empty:
        raise ValueError(f"{series_id} not in {sheet} of {path}")
    vals = row.iloc[0, 2:]
    mnum = {m: i + 1 for i, m in enumerate(MONTHS)}
    idx = [pd.Timestamp(int(y), mnum[m], 1) for y, m in zip(years, months)]
    return pd.Series([_num(v) for v in vals], index=idx).dropna()


def read_steo_meta(path) -> dict:
    raw = pd.read_excel(path, sheet_name="Dates", header=None)
    d = {}
    for _, r in raw.iterrows():
        k = str(r[0]).strip()
        if k.startswith("Forecast Month"):
            d["forecast_month"] = str(r[3])
        elif k.startswith("Modeling and analysis completion"):
            d["completed"] = pd.Timestamp(r[3]).date().isoformat()
        elif k.startswith("Last Historical Month"):
            d["last_historical_month"] = str(int(r[3]))
    return d


def steo_quarterly(monthly: pd.Series) -> pd.Series:
    """Quarter = simple mean of the three monthly values (our arithmetic; EIA's archive has no quarterly column)."""
    g = monthly.groupby(monthly.index.to_period("Q"))
    avg = g.mean()[g.count() == 3]
    avg.index = [f"{p.year}Q{p.quarter}" for p in avg.index]
    return avg


def parse_steo_release_dates(html_path) -> dict:
    """{'aug26': '2026-08-11', ...} from the saved EIA STEO outlook page (archive list)."""
    t = re.sub(r"<[^>]+>", " ", Path(html_path).read_text(errors="replace"))
    out = {}
    for _mon, d, f in re.findall(r"(\w+ \d{4})\s+(\d\d/\d\d/\d{4})\s+(\w+)\.pdf", t):
        out.setdefault(f, dt.datetime.strptime(d, "%m/%d/%Y").date().isoformat())
    return out


def steo_vintage_for(deadline_iso: str, release_dates: dict) -> tuple[str, str | None]:
    """(matched, previous): matched = latest STEO released on or before the SPF deadline."""
    ok = sorted(((d, v) for v, d in release_dates.items() if d <= deadline_iso), reverse=True)
    if not ok:
        raise ValueError(f"no STEO vintage released on/before {deadline_iso}")
    return ok[0][1], (ok[1][1] if len(ok) > 1 else None)


def latest_steo(release_dates: dict) -> str:
    return max(release_dates.items(), key=lambda kv: kv[1])[0]


# ----------------------------------------------------------------------------- EIA daily spot
def read_eia_daily(path) -> pd.Series:
    """EIA hist_xls daily file (e.g. RBRTEd.xls), sheet 'Data 1'. Returns $/bbl indexed by Timestamp."""
    x = pd.read_excel(path, sheet_name="Data 1", header=None, skiprows=3)
    x.columns = ["date", "v"]
    x = x.dropna()
    x["date"] = pd.to_datetime(x["date"])
    return x.set_index("date")["v"].astype(float).sort_index()
