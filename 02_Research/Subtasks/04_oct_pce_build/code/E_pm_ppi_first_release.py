"""First-published BLS PPI levels for portfolio management / investment advice.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/E_pm_ppi_first_release.py
Reads saved PDFs in 03_Data/Raw (Table 11, NAICS 523940-1 / 523940-2; last two numeric
columns = prior month, reference month). Release dates come from the schedule table in
the Jul 2026 report. Current values from outputs/component_series_history.csv."""
import csv, re, pypdf
ROOT = "02_Research/Subtasks/04_oct_pce_build/"
RAW = "03_Data/Raw/BLS_PPI_detailed_report_%s_retrieved_2026-11-12.pdf"
MONTHS = ["2025-11","2025-12","2026-01","2026-02","2026-03","2026-04","2026-05","2026-06","2026-07"]
SERIES = {"PCU5239405239401": "523940-1", "PCU5239405239402": "523940-2"}
MN = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# release schedule (Jul 2026 report, p.3)
sched = {}
r = pypdf.PdfReader(RAW % "2026-07")
for l in r.pages[2].extract_text().splitlines():
    m = re.match(r"\s*(\w+) (\d{4}) (\w+)\.? (\d+), (\d{4})", l)
    if m and m.group(1) in MN:
        sched[f"{m.group(2)}-{MN.index(m.group(1))+1:02d}"] = f"{m.group(5)}-{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(m.group(3)[:3])+1:02d}-{int(m.group(4)):02d}"

hist = {}
for row in csv.DictReader(open(ROOT + "outputs/component_series_history.csv")):
    if row["series_id"] in SERIES:
        hist[(row["series_id"], f"{row['year']}-{row['period'][1:]}")] = float(row["value"])

def prev(ym):
    y, m = map(int, ym.split("-")); return f"{y-1}-12" if m == 1 else f"{y}-{m-1:02d}"

out = []
for ym in MONTHS:
    f = RAW % ym
    rd = pypdf.PdfReader(f)
    for sid, code in SERIES.items():
        hits = []
        pat = re.compile(re.escape(code) + r" +06/02( +[\d.]+){5}\s*$")
        for i, p in enumerate(rd.pages):
            for l in (p.extract_text() or "").splitlines():
                if pat.search(l): hits.append((i+1, l))
        assert len(hits) == 1, (ym, sid, hits)
        pg, line = hits[0]
        nums = [float(x) for x in line.split()[-5:]]
        prior, first = nums[3], nums[4]
        cur = hist[(sid, ym)]; curprior = hist[(sid, prev(ym))]
        fp = (first/prior-1)*100; cp = (cur/curprior-1)*100
        out.append(dict(series_id=sid, reference_month=ym, report_file=f.split("/")[-1],
            report_release_date=sched.get(ym, ""), first_release_level=first,
            prior_month_level_same_report=prior, first_print_mm_pct=round(fp, 3),
            current_level=cur, current_mm_pct=round(cp, 3), mm_revision_pp=round(cp-fp, 3)))
with open(ROOT + "outputs/E_pm_ppi_first_release.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o["series_id"][-2:], o["reference_month"], o["report_release_date"], o["prior_month_level_same_report"], o["first_release_level"], o["first_print_mm_pct"], o["current_level"], o["current_mm_pct"], o["mm_revision_pp"])
