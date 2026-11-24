"""Shared helpers for Agent C scripts (load with importlib by path; scripts run as python3 -I from project root)."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
SUB = ROOT / "02_Research/Subtasks/11_slide3a_research"
OUTD = SUB / "outputs"
RAWC = ROOT / "03_Data/Raw/S3A_expectations_underlying_2026-11-15"
PIPE = ROOT / "03_Data/pipelines/inflation_data"
PCE_RAW = ROOT / "03_Data/pipelines/Price indexes/PCE/raw"
OUTD.mkdir(parents=True, exist_ok=True)


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT.resolve()))
    except Exception:
        return str(p)


def fred(sid, tag="", start=None):
    f = RAWC / f"FRED_{sid}{tag}_2026-11-15.json"
    d = json.load(open(f))
    s = pd.Series({pd.Timestamp(o["date"]): (float(o["value"]) if o["value"] not in (".", "") else float("nan"))
                   for o in d["observations"]}).sort_index()
    s.attrs["file"] = rel(f)
    s.attrs["realtime"] = d.get("realtime_start")
    if start:
        s = s[s.index >= start]
    return s


def monthly_period(s):
    s = s.copy(); s.index = s.index.to_period("M"); return s


def pipeline_obs(group, key):
    o = pd.read_csv(PIPE / "processed" / group / "observations.csv")
    o = o[o.series_key == key].copy()
    o["date"] = pd.to_datetime(o["date"])
    return o.sort_values("date")


def ann(idx, k):
    """k-month annualized % change of an index Series (PeriodIndex monthly)."""
    return ((idx / idx.shift(k)) ** (12 / k) - 1) * 100


def pct(idx, k):
    return (idx / idx.shift(k) - 1) * 100
