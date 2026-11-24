"""Compare inflation_data processed/ before vs after the 2026-11-10 refresh.
Run from project root: python3 -I 02_Research/Subtasks/01_refresh_inflation/code/refresh_check.py
Writes tables under 02_Research/Subtasks/01_refresh_inflation/code/out/.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT = Path("03_Data/pipelines/inflation_data")
OLD = ROOT / "archive/pre_refresh_2026-11-10/processed"
NEW = ROOT / "processed"
OUT = Path("02_Research/Subtasks/01_refresh_inflation/code/out")
OUT.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 250, "display.max_rows", 2000, "display.max_colwidth", 60)

def load(base, g, f):
    return pd.read_csv(base / g / f, dtype=str)

def valid(o):
    o = o.copy()
    o["v"] = pd.to_numeric(o["value"], errors="coerce")
    return o[o.v.notna()]

summary, latest_rows, revisions, problems = [], [], [], []
for g in ["bls", "bea", "fed_expectations"]:
    on, nn = valid(load(OLD, g, "observations.csv")), valid(load(NEW, g, "observations.csv"))
    om, nm = load(OLD, g, "series_metadata.csv"), load(NEW, g, "series_metadata.csv")
    rd = load(NEW, g, "release_dates.csv")
    for key in sorted(set(nn.series_key)):
        o_k, n_k = on[on.series_key == key], nn[nn.series_key == key]
        # old/new latest per (value_type,horizon,publisher id)
        ol, nl = o_k.date.max() if len(o_k) else "", n_k.date.max()
        mrow = nm[nm.series_key == key]
        m_latest = mrow.latest_obs.iloc[0] if len(mrow) else ""
        m_rel = mrow.latest_release_date.iloc[0] if len(mrow) else ""
        m_ret = mrow.retrieval_date.iloc[0] if len(mrow) else ""
        m_raw = mrow.raw_files.iloc[0] if len(mrow) else ""
        # consistency: metadata latest_obs vs observations max (compare YYYY-MM)
        if str(m_latest)[:7] != nl[:7] and not (g == "fed_expectations" and key.startswith(("spf", "umich")) and str(m_latest)[:7] == nl[:7]):
            problems.append(f"{g}/{key}: metadata latest_obs={m_latest} but observations max={nl}")
        if m_ret != "2026-11-10":
            problems.append(f"{g}/{key}: retrieval_date={m_ret}")
        rr = rd[rd.series_key == key]
        rr_latest = rr[rr.date.fillna("").str[:7] == nl[:7]]
        rel = rr_latest.first_release_date.iloc[0] if len(rr_latest) else ""
        summary.append(dict(group=g, series_key=key, old_latest=ol[:7], new_latest=nl[:7], meta_latest_obs=str(m_latest)[:10],
                            meta_latest_release=m_rel, release_dates_csv=rel, retrieval_date=m_ret))
        # latest values by horizon
        for (vt, hz), s in n_k.groupby(["value_type", "horizon"]):
            last = s.sort_values("date").iloc[-1]
            latest_rows.append(dict(group=g, series_key=key, value_type=vt, horizon=hz[:60], date=last.date[:10], value=last.v,
                                    sa=last.seasonal_adjustment, series_id=last.publisher_series_id[:50]))
        # revisions: overlapping dates, same value_type/horizon/id
        k = ["date", "value_type", "horizon", "publisher_series_id"]
        mg = o_k[k + ["v"]].merge(n_k[k + ["v"]], on=k, suffixes=("_old", "_new"))
        mg["diff"] = mg.v_new - mg.v_old
        mg = mg[mg["diff"].abs() > 1e-6]
        mg = mg[mg.date >= "2025-09-01"]
        for _, r in mg.iterrows():
            revisions.append(dict(group=g, series_key=key, date=r.date[:10], value_type=r.value_type, horizon=r.horizon[:40], old=r.v_old, new=r.v_new, diff=r["diff"]))
    # raw file existence
    for _, r in nm.iterrows():
        for p in str(r.raw_files).replace(";", ";").split(";"):
            p = p.strip()
            if p and p != "nan" and not (ROOT.parent / p).exists():
                problems.append(f"{g}/{r.series_key}: raw file missing: {p}")
    no = valid(load(NEW, g, "observations.csv"))
    for p in no.raw_file.dropna().unique():
        if not (ROOT.parent / p).exists():
            problems.append(f"{g}: observations raw_file missing: {p}")

S = pd.DataFrame(summary); L = pd.DataFrame(latest_rows); R = pd.DataFrame(revisions)
S.to_csv(OUT / "latest_obs_summary.csv", index=False)
L.to_csv(OUT / "latest_values_by_horizon.csv", index=False)
R.to_csv(OUT / "revisions_since_2025-09.csv", index=False)
print("== LATEST OBS old -> new ==")
print(S.to_string())
print("\n== PROBLEMS ==")
print("\n".join(problems[:60]) or "none"); print(len(problems), "problems")
print("\n== REVISIONS (n=%d) ==" % len(R))
if len(R): print(R.groupby(["group", "series_key", "value_type", "horizon"]).agg(n=("diff", "size"), maxabs=("diff", lambda x: x.abs().max())).to_string())
# release_dates coverage
for g in ["bls", "bea", "fed_expectations"]:
    rd = load(NEW, g, "release_dates.csv")
    rd = rd[rd.date.notna() & (rd.date != "")]
    print(f"\nrelease_dates {g}: max date per series")
    print(rd.groupby("series_key").agg(max_date=("date", "max"), blank_release=("first_release_date", lambda x: x.isna().sum())).to_string())
