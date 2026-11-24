"""Compare supplement_research.REL against the pre-refresh hand-built CB rows (archive). Run from project root.
Expected: every month matches value/note/source (raw_file path normalized) except 2026-09 (superseded by revised vintage)."""
import sys, pandas as pd
sys.path.insert(0, "03_Data/pipelines/demand_data/code")
import supplement_research as s
o = pd.read_csv("03_Data/pipelines/demand_data/archive/pre_refresh_2026-11-10/processed/research/observations.csv", dtype=str)
o = o[o.series_key.isin(s.KEYS)]
bad = 0
for d, (url, note, vals) in s.REL.items():
    for k, v in zip(s.KEYS, vals):
        r = o[(o.series_key == k) & (o.date == d)]
        if r.empty: print("NEW  ", d, k, v); continue
        r = r.iloc[0]
        rf = r.raw_file; rf = "demand_data/" + rf if rf.startswith("raw/") else rf
        ok = float(r.value) == v and r.note == "Manager transcription: " + note and rf == url
        if not ok: bad += 1; print("DIFF ", d, k, r.value, "->", v, "|", r.note[:60])
print("mismatches:", bad)
