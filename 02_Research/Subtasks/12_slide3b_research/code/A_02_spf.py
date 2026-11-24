"""A_02_spf: Q1.1-1.4. SPF core PCE baseline (median + dispersion), survey dates, Q4 check.
Run from project root:  python3 -I 02_Research/Subtasks/12_slide3b_research/code/A_02_spf.py [raw_dir]
raw_dir defaults to 03_Data/Raw/PhilFed_SPF_2026Q3_2026-11-15. A new SPF (e.g. 2026Q4) dropped in a new
raw folder with the same file names parses with no edits: the survey year/quarter is detected from the
latest non-missing row of medianLevel.xlsx. Output rows for that survey replace any earlier rows of the
same survey in outputs/A_q1_spf_baseline.csv and A_q1_survey_dates.csv (other surveys are kept)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import A_common as C  # noqa: E402

raw = Path(sys.argv[1]) if len(sys.argv) > 1 else C.RAW / "PhilFed_SPF_2026Q3_2026-11-15"
med_f, d1_f, mic_f, rel_f = raw / "medianLevel.xlsx", raw / "Dispersion_1.xlsx", raw / "SPFmicrodata.xlsx", raw / "spf-release-dates.txt"
rel_pull = raw.name

med = C.read_spf_median(med_f, "COREPCE")
Y, Q = C.detect_survey(med)
survey = f"{Y}Q{Q}"
py, pq = C.previous_survey(Y, Q)
hmap = C.horizon_map(Y, Q)
row = C.median_row(med, Y, Q)
prow = C.median_row(med, py, pq)

disp = C.read_dispersion_d1(d1_f, "COREPCE")
mic = C.read_spf_micro(mic_f, "COREPCE", Y, Q)

recs = []


def add(sv, var, stat, val, pod, src, hm):
    tp, ht = hm[var]
    recs.append(dict(survey=sv, variable=var, target_period=tp, horizon_type=ht, stat=stat,
                     value=None if pd.isna(val) else round(float(val), 4),
                     published_or_derived=pod, source_file=src))


MED = f"{rel_pull}/medianLevel.xlsx (sheet COREPCE, row {survey})"
for v in C.SPF_Q_VARS + C.SPF_A_VARS:
    add(survey, v, "median", row[v], "published", MED, hmap)
# previous survey medians (context for revisions)
phm = C.horizon_map(py, pq)
for v in C.SPF_Q_VARS + C.SPF_A_VARS:
    add(f"{py}Q{pq}", v, "median", prow[v], "published",
        f"{rel_pull}/medianLevel.xlsx (sheet COREPCE, row {py}Q{pq})", phm)

# percentiles: quarterly COREPCE2..6 from published Dispersion_1; everything else from micro (Hazen)
checks = []
for i, v in enumerate(C.SPF_Q_VARS):
    k = i - 1  # COREPCE2 -> offset 0
    x = mic[v].dropna()
    n = len(x)
    if k >= 0 and k in disp.get(survey, {}):
        p25, p75, dd = disp[survey][k]
        src = f"{rel_pull}/Dispersion_1.xlsx (sheet COREPCE, row {survey}, offset T+{k})"
        pod = "published"
        checks.append((v, p25, C.hazen(x, 25), p75, C.hazen(x, 75)))
    else:
        p25, p75 = C.hazen(x, 25), C.hazen(x, 75)
        dd = p75 - p25
        src = f"{rel_pull}/SPFmicrodata.xlsx (sheet COREPCE; Hazen percentile, computed)"
        pod = "derived"
    for stat, val in (("p25", p25), ("p75", p75), ("iqr", dd), ("n_respondents", n),
                      ("min", x.min()), ("max", x.max()), ("mean", x.mean())):
        add(survey, v, stat, val, pod if stat in ("p25", "p75", "iqr") else "derived",
            src if stat in ("p25", "p75", "iqr") else f"{rel_pull}/SPFmicrodata.xlsx (sheet COREPCE; computed)", hmap)
for v in C.SPF_A_VARS:
    x = mic[v].dropna()
    p25, p75 = C.hazen(x, 25), C.hazen(x, 75)
    src = f"{rel_pull}/SPFmicrodata.xlsx (sheet COREPCE; Hazen percentile, computed; Dispersion_1 has no annual horizons)"
    for stat, val in (("p25", p25), ("p75", p75), ("iqr", p75 - p25), ("n_respondents", len(x)),
                      ("min", x.min()), ("max", x.max()), ("mean", x.mean())):
        add(survey, v, stat, val, "derived", src, hmap)

# micro-vs-median consistency
for v in C.SPF_Q_VARS + C.SPF_A_VARS:
    mm = mic[v].dropna().median()
    assert abs(mm - row[v]) < 5e-4, (v, mm, row[v])

# derived 2027Q4 (or generally: the 4th quarter of survey_year+1) if the quarterly horizon stops at Q3
q_targets = {hmap[v][0]: row[v] for v in C.SPF_Q_VARS}
nxt = f"{Y + 1}Q4"
if nxt not in q_targets:
    qs = [q_targets.get(f"{Y + 1}Q{j}") for j in (1, 2, 3)]
    if all(x is not None and not np.isnan(x) for x in qs):
        ann = row["COREPCEB"]
        q4 = C.derive_q4_from_annual(*qs, ann)
        recs.append(dict(survey=survey, variable="DERIVED_from_COREPCE3-6_and_COREPCEB", target_period=nxt,
                         horizon_type="qq_ann", stat="median", value=round(float(q4), 4),
                         published_or_derived="derived",
                         source_file=f"derived: 1+q4/100=(1+B/100)^4/prod(1+q_i/100), q1..q3={qs}, B={ann}"))
        # check: round trip
        rt = C.q4q4_from_quarters(qs + [q4])
        assert abs(rt - ann) < 1e-9
        # sensitivity: rounding of published annual median (e.g. +-0.05) moves q4 by ~4x
        for dlt in (-0.05, 0.05):
            recs.append(dict(survey=survey, variable="DERIVED_sensitivity", target_period=nxt, horizon_type="qq_ann",
                             stat=f"median_if_COREPCEB_{dlt:+.2f}", value=round(float(C.derive_q4_from_annual(*qs, ann + dlt)), 4),
                             published_or_derived="derived", source_file="derived: same formula, annual median shifted"))

df = pd.DataFrame(recs)
outf = C.OUT / "A_q1_spf_baseline.csv"
if outf.exists():
    old = pd.read_csv(outf)
    old = old[~old["survey"].isin(df["survey"].unique())]
    df = pd.concat([old, df], ignore_index=True)
df.to_csv(outf, index=False)

# survey dates
rd = C.parse_release_dates(rel_f, Y, Q)
dates = []
if rd:
    dates.append(dict(survey=survey, deadline=rd[0], release_date=rd[1], quote=f"{rd[3]} " + rd[2] + "  [file header: 'True Deadline Date  News Release Date']",
                      source=f"{rel_pull}/spf-release-dates.txt"))
else:
    dates.append(dict(survey=survey, deadline="not listed", release_date="not listed", quote="no row for this survey in spf-release-dates.txt",
                      source=f"{rel_pull}/spf-release-dates.txt"))
rdp = C.parse_release_dates(rel_f, py, pq)
if rdp:
    dates.append(dict(survey=f"{py}Q{pq}", deadline=rdp[0], release_date=rdp[1], quote=f"{rdp[3]} " + rdp[2], source=f"{rel_pull}/spf-release-dates.txt"))
dd_ = pd.DataFrame(dates)
of = C.OUT / "A_q1_survey_dates.csv"
if of.exists():
    old = pd.read_csv(of, dtype=str)
    old = old[~old["survey"].isin(dd_["survey"])]
    dd_ = pd.concat([old, dd_], ignore_index=True)
dd_.to_csv(of, index=False)

print(f"survey detected: {survey} (previous {py}Q{pq}); respondents with core PCE answers: {mic['COREPCE2'].notna().sum()}")
print("median:", {v: row[v] for v in C.SPF_Q_VARS + C.SPF_A_VARS})
print("Dispersion_1 vs micro-Hazen check (var, p25 pub, p25 hazen, p75 pub, p75 hazen):")
for c in checks:
    print("  ", c, "OK" if abs(c[1] - c[2]) < 5e-4 and abs(c[3] - c[4]) < 5e-4 else "MISMATCH")
print(df[df.survey == survey].query("stat in ['median','p25','p75','iqr']").pivot_table(
    index=["variable", "target_period"], columns="stat", values="value", aggfunc="first").to_string())
print(df[df.variable.str.startswith("DERIVED")].to_string())
print(dd_.to_string())
