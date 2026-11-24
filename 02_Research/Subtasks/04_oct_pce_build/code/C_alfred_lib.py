"""Shared helpers: load ALFRED output_type=1 JSON and build within-vintage level lookups."""
import json
from datetime import date
def d(s): return date.fromisoformat(s)
def load(path):
    rows = json.load(open(path))["observations"]
    out = {}  # obs month -> list of (rs, re, value|None)
    for r in rows:
        v = None if r["value"] == "." else float(r["value"])
        out.setdefault(r["date"][:7], []).append((d(r["realtime_start"]), d(r["realtime_end"]), v))
    for k in out: out[k].sort()
    return out
def level_asof(obs, month, vint):
    """Level of `month` as published in vintage `vint` (a date); None if missing/'.' or not yet published."""
    for rs, re_, v in obs.get(month, []):
        if rs <= vint <= re_: return v
    return None
def first_release(obs, month):
    """Earliest realtime_start with a non-missing value."""
    c = [rs for rs, re_, v in obs.get(month, []) if v is not None]
    return min(c) if c else None
def add_months(m, n):
    y, mo = int(m[:4]), int(m[5:7]); t = y*12 + mo-1 + n
    return f"{t//12:04d}-{t%12+1:02d}"
CURRENT = date(9999, 12, 31)
