"""B_q3.py - Q3 wages and costs: ECI, AHE, Atlanta Fed WGT, nonfarm business ULC/OPH/hourly comp,
summary and trend-productivity benchmark tables.
Run from project root:  python3 -I 02_Research/Subtasks/11_slide3a_research/code/B_q3.py
Outputs: outputs/B_q3_wages_ulc.csv, B_q3_summary.csv, B_q3_benchmark.csv
"""
import json, pathlib
import pandas as pd, numpy as np, openpyxl

ROOT = pathlib.Path('.')
OUT = ROOT/'02_Research/Subtasks/11_slide3a_research/outputs'; OUT.mkdir(exist_ok=True)
RAW = ROOT/'03_Data/Raw/S3A_B_labor_costs_2026-11-15'
PIPE = ROOT/'03_Data/pipelines/inflation_data'
START = pd.Timestamp('2018-01-01')

rows = []
def add(series_id, title, df, freq, sa, source_file, vintage, ppy, has_ann3m=False, level_is_rate=False):
    """df: DataFrame index=Timestamp (period start), col 'v' = level (index/level) ."""
    d = df.sort_index().copy()
    v = d['v']
    if level_is_rate:   # series is already a rate (WGT, published y/y): no transformations
        d['qq'] = np.nan; d['a3'] = np.nan; d['yoy'] = np.nan; d['a8'] = np.nan
    else:
        d['qq'] = ((v / v.shift(1)) ** ppy - 1) * 100
        d['a3'] = ((v / v.shift(3)) ** 4 - 1) * 100 if has_ann3m else np.nan
        d['yoy'] = (v / v.shift(ppy) - 1) * 100
        d['a8'] = ((v / v.shift(8)) ** (ppy / 8) - 1) * 100 if freq == 'Q' else np.nan
    for t, r in d[d.index >= START].iterrows():
        if freq == 'Q':
            per = f'{t.year}Q{(t.month-1)//3+1}'
        else:
            per = t.strftime('%Y-%m')
        win = pd.Timestamp('2021-01-01') <= t <= pd.Timestamp('2023-12-31')
        rows.append(dict(series_id=series_id, title=title, period=per, freq=freq,
                         value_level=r['v'], mm_or_qq_ann=r['qq'], ann3m=r['a3'], yoy=r['yoy'], ann8q=r['a8'],
                         sa=sa, window_2021_23=int(win), source_file=source_file, vintage=vintage))

# ---------- ECI (pipeline processed file; raw API pull 2026-11-10) ----------
obs = pd.read_csv(PIPE/'processed/bls/observations.csv', parse_dates=['date'])
def pipe(sid, vt='index_level'):
    s = obs[(obs.publisher_series_id == sid) & (obs.value_type == vt)].set_index('date')
    return pd.DataFrame({'v': s['value'].astype(float)}), s['raw_file'].iloc[0]
ECI_VINT = 'BLS API pull 2026-11-10 (pipeline); ECI 2026Q3 released 2026-10-30'
for sid, title in [('CIS2020000000000I', 'ECI wages and salaries, private industry, SA index (Dec 2005=100)'),
                   ('CIS2010000000000I', 'ECI total compensation, private industry, SA index (Dec 2005=100)'),
                   ('CIU2020000000000I', 'ECI wages and salaries, private industry, NSA index (Dec 2005=100)')]:
    df, f = pipe(sid)
    add(sid, title, df, 'Q', 'SA' if sid.startswith('CIS') else 'NSA', 'inflation_data/'+f, ECI_VINT, 4)
for sid, title in [('CIU2020000000000A', 'ECI wages and salaries, private industry, published 12-month % change, NSA'),
                   ('CIU2010000000000A', 'ECI total compensation, private industry, published 12-month % change, NSA')]:
    df, f = pipe(sid, 'published_rate')
    add(sid, title, df, 'Q', 'NSA', 'inflation_data/'+f, ECI_VINT, 4, level_is_rate=True)

# ---------- Productivity & Costs (fresh pull 2026-11-15, current vintage after Nov 5 release) ----------
pc = json.load(open(RAW/'bls_api_productivity_costs_2008-2026_2026-11-15.json'))
PCF = '03_Data/Raw/S3A_B_labor_costs_2026-11-15/bls_api_productivity_costs_2008-2026_2026-11-15.json'
def bls_series(js, sid):
    s = [x for x in js['Results']['series'] if x['seriesID'] == sid][0]
    recs = {}
    for x in s['data']:
        if x['period'].startswith('Q'):
            t = pd.Timestamp(int(x['year']), (int(x['period'][1:]) - 1) * 3 + 1, 1)
        else:
            t = pd.Timestamp(int(x['year']), int(x['period'][1:]), 1)
        recs[t] = float(x['value'])
    return pd.DataFrame({'v': pd.Series(recs)}).sort_index()
PC_V = 'BLS Productivity & Costs 2026Q3 preliminary, released 2026-11-05; API pull 2026-11-15; history revised back to 2021Q1 (BEA annual update)'
pcd = {}
for sid, title in [('PRS85006113', 'Nonfarm business unit labor costs, index 2017=100'),
                   ('PRS85006093', 'Nonfarm business output per hour (labor productivity), index 2017=100'),
                   ('PRS85006103', 'Nonfarm business hourly compensation, index 2017=100'),
                   ('PRS85006173', 'Nonfarm business labor share, index 2017=100'),
                   ('PRS85006174', 'Nonfarm business labor share, level (percent of nominal output)')]:
    df = bls_series(pc, sid); pcd[sid] = df
    add(sid, title, df, 'Q', 'SA', PCF, PC_V, 4)

# ---------- AHE ----------
ces = json.load(open(RAW/'bls_api_ces_ahe_2016-2026_2026-11-15.json'))
CESF = '03_Data/Raw/S3A_B_labor_costs_2026-11-15/bls_api_ces_ahe_2016-2026_2026-11-15.json'
CES_V = 'CES Oct 2026 (preliminary), Employment Situation released 2026-11-06; API pull 2026-11-15'
for sid, title in [('CES0500000003', 'Average hourly earnings, all employees, total private ($/hr)'),
                   ('CES0500000008', 'Average hourly earnings, production & nonsupervisory, total private ($/hr)')]:
    add(sid, title, bls_series(ces, sid), 'M', 'SA', CESF, CES_V, 12, has_ann3m=True)

# ---------- Atlanta Fed Wage Growth Tracker ----------
wb = openpyxl.load_workbook(RAW/'atlantafed_wage-growth-data_2026-11-15.xlsx', data_only=True)
ws = wb['data_overall']
hdr = [c.value for c in ws[2]]
ix = {h: i for i, h in enumerate(hdr) if h}
wgt = []
for r in ws.iter_rows(min_row=3, values_only=True):
    if r[0] is None or r[ix['Overall']] in (None, '.'): continue
    wgt.append({'date': pd.Timestamp(r[0]), 'Overall': r[ix['Overall']], 'Job Stayer': r[ix['Job Stayer']], 'Job Switcher': r[ix['Job Switcher']]})
wgt = pd.DataFrame(wgt).set_index('date')
WGTF = '03_Data/Raw/S3A_B_labor_costs_2026-11-15/atlantafed_wage-growth-data_2026-11-15.xlsx (sheet data_overall)'
WGT_V = 'Atlanta Fed page "Updated: October 08, 2026" (data through 2026-09; Oct CPS month not yet published); downloaded 2026-11-15'
for col, sid in [('Overall', 'WGT_overall_3mma'), ('Job Stayer', 'WGT_stayer_3mma'), ('Job Switcher', 'WGT_switcher_3mma')]:
    add(sid, f'Atlanta Fed Wage Growth Tracker, {col}, 3-month moving average of median y/y hourly wage growth (%)',
        pd.DataFrame({'v': wgt[col].astype(float)}), 'M', 'NSA (CPS-based, no SA)', WGTF, WGT_V, 12, level_is_rate=True)

long = pd.DataFrame(rows)
long.to_csv(OUT/'B_q3_wages_ulc.csv', index=False, float_format='%.4f')

# ---------- Summary ----------
def pstart(per):  # period label -> Timestamp
    if 'Q' in per: return pd.Timestamp(int(per[:4]), (int(per[-1]) - 1) * 3 + 1, 1)
    return pd.Timestamp(per + '-01')
long['t'] = long.period.map(pstart)
srows = []
for sid, g in long.groupby('series_id', sort=False):
    g = g.sort_values('t')
    for col, lab in [('value_level', 'level'), ('mm_or_qq_ann', '1-period annualised (m/m or q/q ann.)'), ('ann3m', '3m annualised'),
                     ('yoy', 'y/y'), ('ann8q', '8q annualised')]:
        s = g.dropna(subset=[col])
        if s.empty: continue
        if col == 'value_level' and not (sid.startswith('WGT') or sid.endswith('A') or sid in ('PRS85006174',)):
            pass  # keep level for all (index/$ levels)
        last = s.iloc[-1]
        base = s[(s.t >= '2018-01-01') & (s.t <= '2019-12-31')][col]
        win = s[(s.t >= '2021-01-01') & (s.t <= '2023-12-31')]
        pk = win.loc[win[col].idxmax()] if len(win) else None
        srows.append(dict(series_id=sid, title=g.title.iloc[0], measure=lab, latest_period=last.period, latest=last[col],
                          avg_2018_19=base.mean() if len(base) else np.nan,
                          peak_2021_23=pk[col] if pk is not None else np.nan, peak_period=pk.period if pk is not None else '',
                          sa=last.sa, vintage=last.vintage))
pd.DataFrame(srows).to_csv(OUT/'B_q3_summary.csv', index=False, float_format='%.3f')

# ---------- Trend productivity benchmark ----------
fo = json.load(open(RAW/'fred_OPHNFB_full_2026-11-15.json'))['observations']
oph = pd.Series({pd.Timestamp(x['date']): float(x['value']) for x in fo if x['value'] != '.'}).sort_index()
def cagr(a, b):  # growth from end of quarter a to end of quarter b, annualised
    ta, tb = pstart(a), pstart(b)
    n = (tb.year - ta.year) * 4 + (tb.month - ta.month) // 3
    return ((oph[tb] / oph[ta]) ** (4 / n) - 1) * 100
cands = [
    ('OPH 2010Q1-2019Q4 avg annualised (2009Q4->2019Q4)', '2010Q1-2019Q4', cagr('2009Q4', '2019Q4'), 'computed', 'FRED OPHNFB (=PRS85006093), current vintage; pre-pandemic full expansion; matches Jefferson prior-cycle 1.5%'),
    ('OPH 2007Q4-2019Q4 avg annualised (previous full cycle, NBER peak to peak)', '2007Q4-2019Q4', cagr('2007Q4', '2019Q4'), 'computed', 'FRED OPHNFB; closest computed match to Jefferson "previous business cycle" 1.5%; matches CBO 1.5% claim'),
    ('OPH 2000Q1-2019Q4 avg annualised (1999Q4->2019Q4)', '2000Q1-2019Q4', cagr('1999Q4', '2019Q4'), 'computed', 'FRED OPHNFB; includes the 2000s boom'),
    ('OPH 2015Q1-2019Q4 avg annualised (2014Q4->2019Q4)', '2015Q1-2019Q4', cagr('2014Q4', '2019Q4'), 'computed', 'FRED OPHNFB; late-cycle, low-productivity stretch'),
    ('OPH 2020Q1-2025Q4 avg annualised (2019Q4->2025Q4)', '2020Q1-2025Q4', cagr('2019Q4', '2025Q4'), 'computed', 'FRED OPHNFB current vintage; compare Jefferson 2.2% (his construction not stated)'),
    ('OPH 2019Q4-2026Q3 avg annualised (2019Q4->2026Q3)', '2019Q4-2026Q3', cagr('2019Q4', '2026Q3'), 'computed', 'FRED OPHNFB; whole post-pandemic span'),
    ('OPH 8-quarter annualised to 2026Q3 (2024Q3->2026Q3)', '2024Q3-2026Q3', cagr('2024Q3', '2026Q3'), 'computed', 'actual, not a trend estimate; recent momentum'),
    ('OPH 4-quarter (y/y) to 2026Q3', '2025Q3-2026Q3', cagr('2025Q3', '2026Q3'), 'computed', 'actual; volatile'),
    ('OPH 1947Q1-2026Q3 avg annualised', '1947Q1-2026Q3', cagr('1947Q1', '2026Q3'), 'computed', 'long-run reference'),
    ('Jefferson speech: labor productivity 2020-2025 average', '2020-2025', 2.2, 'cited', '[O] Jefferson, 2026-11-13, saved speech text; underlying series not stated'),
    ('Jefferson speech: previous business cycle average', 'previous cycle', 1.5, 'cited', '[O] Jefferson, 2026-11-13; cycle dates not stated'),
    ('CBO potential labor force productivity 2026-2036 (Feb 2026 Outlook)', '2026-2036', 1.5, 'cited', '[S] search snippet only; cbo.gov returned 403 to fetch, UNVERIFIED'),
]
bench = pd.DataFrame([dict(candidate_trend=c[0], period=c[1], value_pct=round(c[2], 2), implied_wage_growth_2pct_inflation=round(2 + c[2], 2),
                           kind=c[3], central_benchmark='YES' if c[0].startswith('OPH 2007Q4') else '', note=c[4]) for c in cands])
bench.to_csv(OUT/'B_q3_benchmark.csv', index=False)
print(bench[['candidate_trend', 'value_pct', 'implied_wage_growth_2pct_inflation']].to_string())
print(pd.DataFrame(srows).drop(columns=['title', 'vintage']).to_string())
