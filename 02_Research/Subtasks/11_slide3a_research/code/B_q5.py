"""B_q5.py - Q5 catch-up evidence (surveys/anecdotal). NFIB (PDF parsed with pypdf), Atlanta Fed BIE, Richmond Fed
survey wage diffusion, Richmond CFO survey, Conference Board (public items only).
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/B_q5.py
Outputs: outputs/B_q5_catchup.csv, outputs/B_q5_summary.csv"""
import re, pathlib
import pandas as pd, numpy as np, openpyxl, pypdf
ROOT = pathlib.Path('.')
OUT = ROOT/'02_Research/Subtasks/11_slide3a_research/outputs'
RAW = ROOT/'03_Data/Raw/S3A_B_labor_costs_2026-11-15'
EXP = ROOT/'03_Data/pipelines/inflation_data/raw/expectations_aggregate'
rows = []
def add(source, series, period, value, units, sa, kind, f):
    if value is None or (isinstance(value, float) and np.isnan(value)): return
    rows.append(dict(source=source, series=series, period=period, value=value, units=units, sa=sa, survey_or_hard=kind, source_file=f))

# ---- NFIB ----
def nfib_tables(pdf, header):
    r = pypdf.PdfReader(str(pdf))
    for p in r.pages:
        t = p.extract_text()
        if t.strip().startswith(header):
            tabs, cur, last = [], {}, 0
            for ln in t.splitlines():
                m = re.match(r'^(20\d\d)((?:\s+-?\d+)+)\s*$', ln.strip())
                if m:
                    y = int(m.group(1))
                    if y < last: tabs.append(cur); cur = {}
                    last = y; cur[y] = [int(x) for x in m.group(2).split()]
            tabs.append(cur)
            return tabs
    raise ValueError(header)
nf = {}
for pdf, yrs in [('nfib_SBET-Dec-2020_via-wayback_2026-11-15.pdf', range(2018, 2021)), ('nfib_SBET-Report-October-2026_2026-11-15.pdf', range(2021, 2027))]:
    for hdr, (a, b) in [('SMALL BUSINESS COMPENSATION (CONTINUED', ('actual_comp', 'plan_comp')), ('SMALL BUSINESS PRICES', ('actual_price', 'plan_price'))]:
        t = nfib_tables(RAW/pdf, hdr)
        assert len(t) == 2, (pdf, hdr, len(t))   # first table = actual last 3 months, second = plans next 3 months
        for name, tab in zip((a, b), t):
            for y in yrs:
                for m, v in enumerate(tab[y], start=1):
                    nf.setdefault(name, {})[f'{y}-{m:02d}'] = (v, pdf)
labels = {'actual_comp': 'NFIB net % raised compensation, last 3 months', 'plan_comp': 'NFIB net % planning to raise compensation, next 3 months',
          'actual_price': 'NFIB net % raised average selling prices, last 3 months', 'plan_price': 'NFIB net % planning to raise prices, next 3 months'}
for k, d in nf.items():
    for per, (v, f) in d.items():
        add('NFIB SBET', labels[k], per, float(v), 'net % of owners (raise minus lower)', 'SA', 'survey', '03_Data/Raw/S3A_B_labor_costs_2026-11-15/'+f)
# single-month text items from Oct 2026 report (opened; page 3 summary)
f = '03_Data/Raw/S3A_B_labor_costs_2026-11-15/nfib_SBET-Report-October-2026_2026-11-15.pdf'
add('NFIB SBET', 'NFIB % citing labor costs as single most important problem', '2026-10', 7.0, '% of owners', 'NSA', 'survey', f)
add('NFIB SBET', 'NFIB % citing labor quality/availability as single most important problem', '2026-10', 25.0, '% of owners', 'NSA', 'survey', f)
add('NFIB SBET', 'NFIB % with unfilled job openings', '2026-10', 36.0, '% of owners', 'SA', 'survey', f)

# ---- Atlanta Fed BIE ----
bf = EXP/'atlantafed_bie-data_2026-11-14.xlsx'; bfr = '03_Data/pipelines/inflation_data/raw/expectations_aggregate/atlantafed_bie-data_2026-11-14.xlsx'
ws = openpyxl.load_workbook(bf, data_only=True)['BIE Survey results']
for r in ws.iter_rows(min_row=4, values_only=True):
    if r[0] is None or not hasattr(r[0], 'year'): continue
    per = f'{r[0].year}-{r[0].month:02d}'
    add('Atlanta Fed BIE', 'BIE unit costs vs a year ago, mean (Q3)', per, r[21]*100 if r[21] is not None else None, '% (mean of firm responses)', 'n/a', 'survey', bfr)
    add('Atlanta Fed BIE', 'BIE year-ahead unit cost expectation, mean (Q4)', per, r[29]*100 if r[29] is not None else None, '% (mean of probability-weighted responses)', 'n/a', 'survey', bfr)
ws = openpyxl.load_workbook(bf, data_only=True)['Quarterly- Price Change']
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[0] is None: continue
    d = pd.to_datetime(r[0], errors='coerce')
    if pd.isna(d): continue
    per = f'{d.year}-{d.month:02d}'
    add('Atlanta Fed BIE', 'BIE own price change, past 12 months, mean', per, float(r[2]), '%', 'n/a', 'survey', bfr)
    add('Atlanta Fed BIE', 'BIE own price change, expected next 12 months, mean', per, float(r[7]), '%', 'n/a', 'survey', bfr)

# ---- Richmond Fed mfg / services wage diffusion ----
for fn, cols in [('richmondfed_mfg_historicaldata_2026-11-14.xlsx', [('sa_mfg_wage_c', 'Richmond Fed mfg survey: wages, current (diffusion)'), ('sa_mfg_wage_e', 'Richmond Fed mfg survey: wages, expected 6m (diffusion)')]),
                 ('richmondfed_nmf_historicaldata_2026-11-14.xlsx', [('sa_svc_ave_wage_c', 'Richmond Fed services survey: avg wages, current (diffusion)'), ('sa_svc_ave_wage_e', 'Richmond Fed services survey: avg wages, expected (diffusion)')])]:
    w = openpyxl.load_workbook(EXP/fn, data_only=True).worksheets[0]
    h = [c.value for c in w[1]]
    for col, lab in cols:
        j = h.index(col)
        for r in w.iter_rows(min_row=2, values_only=True):
            if hasattr(r[0], 'year') and r[0].year >= 2018 and isinstance(r[j], (int, float)):
                add('Richmond Fed', lab, f'{r[0].year}-{r[0].month:02d}', float(r[j]), 'diffusion index (% up minus % down)', 'SA', 'survey', '03_Data/pipelines/inflation_data/raw/expectations_aggregate/'+fn)

# ---- Richmond CFO survey Q3 2026 (html opened; Aug 17-Sep 4 2026) ----
cf = '03_Data/pipelines/inflation_data/raw/expectations_aggregate/richmondfed_cfo_survey_2026Q3_results_2026-11-14.html'
for lab, vals in {'avg wage': {'2026Q2 survey, CY2026': (4.0, 3.1), '2026Q2 survey, CY2027': (3.9, 3.0), '2026Q3 survey, CY2026': (4.3, 3.8), '2026Q3 survey, CY2027': (4.3, 4.0)},
                  'price': {'2026Q2 survey, CY2026': (4.7, 3.0), '2026Q2 survey, CY2027': (4.1, 3.0), '2026Q3 survey, CY2026': (5.3, 4.0), '2026Q3 survey, CY2027': (4.5, 3.0)},
                  'unit cost': {'2026Q2 survey, CY2026': (4.5, 4.0), '2026Q2 survey, CY2027': (4.0, 3.0), '2026Q3 survey, CY2026': (4.8, 4.0), '2026Q3 survey, CY2027': (4.2, 3.0)}}.items():
    for per, (mean, med) in vals.items():
        add('Richmond Fed CFO survey', f'CFO expected y/y change, own firm {lab}, mean', per, mean, '% y/y (employment-weighted; revenue-weighted for price/unit cost)', 'n/a', 'survey', cf)
        add('Richmond Fed CFO survey', f'CFO expected y/y change, own firm {lab}, median', per, med, '% y/y', 'n/a', 'survey', cf)

# ---- Conference Board (public items) ----
cb = '03_Data/pipelines/inflation_data/raw/expectations_aggregate/conferenceboard_CCI_Oct2026_press_2026-11-14.html'
add('Conference Board', 'CCI: consumers average 12-month inflation expectations', '2026-10', 5.8, '%', 'n/a', 'survey', cb)
add('Conference Board', 'Salary Budget Survey: median base-pay increase budget, 2027', '2027 (released 2026-09-03)', 3.5, '% median', 'n/a', 'survey', 'WebFetch conference-board.org/publications/us-salary-increase-budgets-2026-2027 (members-only report; public brief) [2: not saved]')
add('Conference Board', 'Salary Budget Survey: median base-pay increase budget, 2026 (actual/planned)', '2026', 3.5, '% median', 'n/a', 'survey', 'same as above')
add('Conference Board', 'Salary Budget Survey: median base-pay increase budget, 2025', '2025 (released 2025-09-02)', 3.5, '% median', 'n/a', 'survey', 'WebFetch conference-board.org/publications/US-salary-increase-budgets-2025-2026 [2: not saved]')
add('Conference Board', 'Salary Budget Survey: median merit budget, 2027', '2027 (released 2026-09-03)', 3.1, '% median', 'n/a', 'survey', 'same as above')

cat = pd.DataFrame(rows)
cat.to_csv(OUT/'B_q5_catchup.csv', index=False, float_format='%.3f')

# ---- summary ----
def key(p): return p[:7]
srows = []
for (src, ser), g in cat.groupby(['source', 'series'], sort=False):
    g = g.copy()
    g['ym'] = g.period.map(lambda p: p[:7] if re.match(r'^\d{4}-\d{2}$', p) else None)
    last = g.iloc[-1] if len(g) == 1 or g.ym.isna().all() else g.dropna(subset=['ym']).sort_values('ym').iloc[-1]
    ts = g.dropna(subset=['ym'])
    base = ts[(ts.ym >= '2018-01') & (ts.ym <= '2019-12')].value
    win = ts[(ts.ym >= '2021-01') & (ts.ym <= '2023-12')]
    pk = win.loc[win.value.idxmax()] if len(win) else None
    srows.append(dict(source=src, series=ser, latest_period=last.period, latest=last.value, avg_2018_19=base.mean() if len(base) else np.nan,
                      n_2018_19=len(base), peak_2021_23=pk.value if pk is not None else np.nan, peak_period=pk.period if pk is not None else '',
                      units=last.units, sa=last.sa, survey_or_hard='survey', source_file=last.source_file))
sm = pd.DataFrame(srows); sm.to_csv(OUT/'B_q5_summary.csv', index=False, float_format='%.2f')
pd.set_option('display.width', 250, 'display.max_colwidth', 70)
print(sm.drop(columns=['units', 'sa', 'survey_or_hard', 'source_file']).to_string())
