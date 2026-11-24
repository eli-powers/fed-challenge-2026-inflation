"""Shared parsers for slide 3B research (Agent A).

Reusable by the forecast pipeline. Rerun scripts from the project root with
`python3 -I <script>`. No network access in this module.

SPF (Philadelphia Fed Survey of Professional Forecasters) core PCE variable names:
  COREPCE1  quarter BEFORE the survey quarter (forecasters already know it: BEA advance estimate)
  COREPCE2  survey (current) quarter
  COREPCE3..6  the next four quarters (so the survey gives 2026Q2..2027Q3 in the 2026Q3 survey)
  COREPCEA/B/C  Q4/Q4 core PCE inflation for survey year, +1, +2
Units: percent change, annual rate, SA. Quarterly = annualized q/q change of the quarterly average
price index; annual = Q4/Q4 (documentation, "COREPCE" entry).
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
TASK = ROOT / "02_Research/Subtasks/12_slide3b_research"
RAW = ROOT / "03_Data/Raw"
OUT = TASK / "outputs"

SPF_Q_VARS = ["COREPCE1", "COREPCE2", "COREPCE3", "COREPCE4", "COREPCE5", "COREPCE6"]
SPF_A_VARS = ["COREPCEA", "COREPCEB", "COREPCEC"]


# ----------------------------------------------------------------------------- quarters
def qidx(year: int, q: int) -> int:
    return year * 4 + (q - 1)


def qlabel(idx: int) -> str:
    return f"{idx // 4}Q{idx % 4 + 1}"


def horizon_map(year: int, q: int) -> dict:
    """variable -> (target_period, horizon_type) for a survey taken in (year, q)."""
    s = qidx(year, q)
    m = {}
    for k, v in enumerate(SPF_Q_VARS, start=1):
        m[v] = (qlabel(s + k - 2), "qq_ann")
    for j, v in enumerate(SPF_A_VARS):
        m[v] = (f"{year + j}Q4/{year + j - 1}Q4", "q4q4")
    return m


# ----------------------------------------------------------------------------- SPF files
def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def read_spf_median(path, var="COREPCE") -> pd.DataFrame:
    """Median forecasts (medianLevel.xlsx sheet <var>, or the single-sheet per-variable file)."""
    xl = pd.ExcelFile(path)
    sheet = var if var in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].map(_num)
    return df


def detect_survey(df: pd.DataFrame, probe="COREPCE2") -> tuple[int, int]:
    """Latest survey (year, quarter) with a non-missing current-quarter forecast."""
    ok = df.dropna(subset=[probe])
    r = ok.iloc[-1]
    return int(r["YEAR"]), int(r["QUARTER"])


def previous_survey(year: int, q: int) -> tuple[int, int]:
    return (year, q - 1) if q > 1 else (year - 1, 4)


def median_row(df: pd.DataFrame, year: int, q: int) -> pd.Series:
    r = df[(df["YEAR"] == year) & (df["QUARTER"] == q)]
    if r.empty:
        raise ValueError(f"survey {year}Q{q} not in median file")
    return r.iloc[0]


def read_dispersion_d1(path, var="COREPCE") -> dict:
    """Dispersion_1.xlsx (D1 = P75-P25 of forecasts for levels; for core PCE the 'level' is the
    annualized inflation rate). Returns {'2026Q3': {offset k (0..4): (p25, p75, d1)}}.
    Offset 0 = survey quarter (COREPCE2) ... 4 = COREPCE6. No annual horizons in this file."""
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


def read_spf_micro(path, var="COREPCE", year=None, q=None) -> pd.DataFrame:
    """Individual responses (SPFmicrodata.xlsx sheet <var>) for one survey."""
    df = pd.read_excel(path, sheet_name=var)
    df.columns = [str(c).strip() for c in df.columns]
    for c in df.columns:
        df[c] = df[c].map(_num)
    if year is not None:
        df = df[(df["YEAR"] == year) & (df["QUARTER"] == q)]
    return df


def hazen(x, p):
    """Percentile with Hazen plotting positions (i-0.5)/n. This reproduces the Philadelphia Fed's
    published Dispersion_1 25th/75th percentiles for core PCE (verified for 2026Q3, all 5 horizons)."""
    x = np.asarray([v for v in x if not np.isnan(v)], float)
    return float(np.percentile(x, p, method="hazen")) if len(x) else np.nan


def parse_release_dates(path, year: int, q: int):
    """(deadline, release, quote) for survey year/q from spf-release-dates.txt; None if absent."""
    txt = Path(path).read_text(errors="replace").splitlines()
    cur_year = None
    for line in txt:
        m = re.match(r"^\s*(\d{4})\s+Q([1-4])\s+(\S+)\s+(\S+)", line)
        if m:
            cur_year = int(m.group(1))
            qq = int(m.group(2))
            rest = (m.group(3), m.group(4))
        else:
            m = re.match(r"^\s+Q([1-4])\s+(\S+)\s+(\S+)", line)
            if not m or cur_year is None:
                continue
            qq = int(m.group(1))
            rest = (m.group(2), m.group(3))
        if cur_year == year and qq == q:
            return rest[0], rest[1], line.strip(), cur_year
    return None


# ----------------------------------------------------------------------------- derivations
def derive_q4_from_annual(q1, q2, q3, q4q4_pct):
    """q4 (annualized %) such that Q4/Q4 = prod_{i=1..4}(1+q_i/100)^(1/4) - 1.
    q_i are annualized q/q rates (percent). Solved: 1+q4/100 = (1+Q4Q4/100)^4 / prod_{i=1..3}(1+q_i/100)."""
    prod = np.prod([1 + v / 100 for v in (q1, q2, q3)])
    return 100 * ((1 + q4q4_pct / 100) ** 4 / prod - 1)


def q4q4_from_quarters(qs):
    return 100 * (np.prod([(1 + v / 100) ** 0.25 for v in qs]) - 1)


# ----------------------------------------------------------------------------- FRED / price data
def load_fred_obs(path) -> pd.Series:
    d = json.load(open(path))
    s = pd.Series({pd.Timestamp(o["date"]): _num(o["value"]) for o in d["observations"]}).dropna()
    return s.sort_index()


def load_alfred_vintage(path, asof: str) -> pd.Series:
    """Series as known on date `asof` from an ALFRED all-vintages JSON."""
    d = json.load(open(path))
    t = pd.Timestamp(asof)
    s = {}
    for o in d["observations"]:
        rs, re_ = pd.Timestamp(o["realtime_start"]), pd.Timestamp(o["realtime_end"])
        if rs <= t <= re_:
            s[pd.Timestamp(o["date"])] = _num(o["value"])
    return pd.Series(s).dropna().sort_index()


def quarterly_avg(monthly: pd.Series, complete_only=True) -> pd.Series:
    """Quarterly average of a monthly series, indexed by 'YYYYQn' labels."""
    q = monthly.groupby(monthly.index.to_period("Q"))
    avg, cnt = q.mean(), q.count()
    if complete_only:
        avg = avg[cnt == 3]
    avg.index = [f"{p.year}Q{p.quarter}" for p in avg.index]
    return avg


def qq_annualized(qavg: pd.Series) -> pd.Series:
    return ((qavg / qavg.shift(1)) ** 4 - 1) * 100


def q4q4_series(qavg: pd.Series) -> pd.Series:
    return (qavg / qavg.shift(4) - 1) * 100


# ----------------------------------------------------------------------------- STEO
def read_steo_series(path, series_id="BREPUUS", sheet="2tab") -> pd.Series:
    """Monthly series from a STEO archive workbook (MMMYY_base.xlsx), e.g. BREPUUS = Brent spot average."""
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    years = raw.iloc[2, 2:].ffill()
    months = raw.iloc[3, 2:]
    row = raw[raw[0] == series_id]
    if row.empty:
        raise ValueError(f"{series_id} not in {sheet}")
    vals = row.iloc[0, 2:]
    mnum = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
    idx = [pd.Timestamp(int(y), mnum[m], 1) for y, m in zip(years, months)]
    return pd.Series([_num(v) for v in vals], index=idx)


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
    """Simple average of the three monthly values (EIA quarterly = average of months)."""
    return quarterly_avg(monthly.dropna(), complete_only=True)


def today_iso():
    return dt.date.today().isoformat()
