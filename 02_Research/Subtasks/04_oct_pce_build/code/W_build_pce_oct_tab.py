"""Build the "PCE Oct 2026 estimate" tab for Price_Basket_Findings.xlsx, in the style of the "CPI Oct 2026 views" tab.

Run from the project root:
    python3 "02_Research/Subtasks/04_oct_pce_build/code/W_build_pce_oct_tab.py"
Writes ONLY a separate build workbook:
    03_Data/pipelines/Price indexes/Price_Basket_Findings_build_pce_oct_2026-11-13.xlsx  (one sheet)
plus outputs/W_pce_oct_tab_lines.csv (every line's numbers, for audit). The hand-edited workbook is changed only by
replace_sheets.py (see code/README.md), never by this script.

Data: the audited October build (outputs/D_build_2026-10_lines.csv and _summary.csv; Audit 2 converged R1, Nov 13).
Component 3-month and 12-month rates extend BEA's own published index for each line (U20404, vintage 2026-11-10,
data through Sep 2026) by our October change. Weights at the start of each window are BEA nominal spending shares
(U20405) for the month before the window starts, computed by the audited engine (D_common.Engine.estimate).
Styling and flags (Energy / Energy spillover / AI / Asset-price) copy the pipeline's own helpers and tag rules.
"""
import os, re, sys
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build')
OUT = os.path.join(SUB, 'outputs')
PIPE = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes')
BUILD = os.path.join(PIPE, 'Price_Basket_Findings_build_pce_oct_2026-11-13.xlsx')
SHEET = 'PCE Oct 2026 estimate'
sys.path.insert(0, os.path.join(SUB, 'code'))
sys.dont_write_bytecode = True
import D_common as dc

# ---- pipeline tag rules, copied verbatim from Price indexes/code/analyze_baskets.py (TAGS, tag)
TAGS = [
    ("Energy", r"\bfuels?\b|lubricants|gasoline|motor fuel|fuel oil|electricity|natural gas|utility gas|propane|energy|diesel|jet fuel|electric power|household fuels"),
    ("Energy spillover", r"air transport|airline|freight|delivery|postage|postal|moving|truck transportation|intercity|railway|water transportation|"
                         r"road transportation|public transportation|courier|motor vehicle rental|car and truck rental|transportation of|warehousing"),
    ("AI", r"software|computer|electronic components|semiconductor|data processing|hosting|information processing|telephone hardware|"
           r"telephone and related communication|video equipment|smart home"),
    ("Asset-price", r"portfolio|financial service charges|securities|commissions|investment advice|trust, fiduciary"),
]


def tag(name):
    n = str(name).lower()
    n = re.sub(r"\b(less|excluding|except)\b.*$", "", n)
    return ", ".join(t for t, pat in TAGS if re.search(pat, n)) or ""


def direction(a, b):  # pipeline rule (analyze_baskets.direction): 3m ann. vs 12m, +/- 1 pp
    if pd.isna(a) or pd.isna(b):
        return "n/a"
    return "Accelerating" if a > b + 1 else "Easing" if a < b - 1 else "Steady"


HOW = {'observed_published': 'Direct (BLS series as published)', 'observed_needs_seasonal': 'Our seasonal adjustment',
       'blend': 'Composite', 'proxied': 'Proxied', 'assumed': 'Carried forward (12-mo avg)'}


def how_priced(r):
    if r['cat'] == 'blend' and r['seasonal'] == 'SAbyBEA':
        return 'Composite + our seasonal adjustment'
    return HOW[r['cat']]


# ---- data
T = dc.P('2026-10')
lines = pd.read_csv(os.path.join(OUT, 'D_build_2026-10_lines.csv'))
summ = pd.read_csv(os.path.join(OUT, 'D_build_2026-10_summary.csv')).set_index('measure')
eng = dc.Engine()                                   # Nov 13 history (default HISTORY)
w3 = eng.estimate('2026-08', k=12, version='2026-09-30')[1].set_index('line')    # shares of Jul 2026 = start of 3m window
w12 = eng.estimate('2025-11', k=12, version='2026-09-30')[1].set_index('line')   # shares of Oct 2025 = start of 12m window
chk = eng.estimate(T, k=int(summ.loc['core', 'window']), version='2026-09-30')[0]
assert abs(chk['core'] - summ.loc['core', 'estimate_mm']) < 5e-6 and abs(chk['headline'] - summ.loc['headline', 'estimate_mm']) < 5e-6

rows = []
for r in lines.itertuples():
    r = r._asdict()
    bl = 156 if r['line'] == 157 else r['line']
    p = eng.bea_p[bl]
    i_sep = p.get(dc.P('2026-09'))
    i_oct = i_sep * (1 + r['pi'] / 100)
    p3 = 100 * ((i_oct / p.get(dc.P('2026-07'))) ** 4 - 1)
    p12 = 100 * (i_oct / p.get(dc.P('2025-10')) - 1)
    yy = 100 * (p / p.shift(12) - 1)
    avg1819 = yy[(yy.index >= dc.P('2018-01')) & (yy.index <= dc.P('2019-12'))].mean()
    rows.append(dict(line=r['line'], name=r['name'], flag=tag(r['name']), how=how_priced(r), in_core=r['w_c'] != 0,
                     w_h=100 * r['w_h'], w_c=100 * r['w_c'], w3_h=100 * w3.at[r['line'], 'w_h'], w3_c=100 * w3.at[r['line'], 'w_c'],
                     w12_h=100 * w12.at[r['line'], 'w_h'], w12_c=100 * w12.at[r['line'], 'w_c'],
                     pct_1m=r['pi'], pct_3m_ann=p3, pct_12m=p12, avg_12m_2018_19=avg1819,
                     source=f"BEA line {r['line']}; " + (str(r['inputs']).replace(';', ', ') if isinstance(r['inputs'], str) and r['inputs'] else
                                                         f"carry-forward of BEA line {bl}")))
d = pd.DataFrame(rows)
for m in ('h', 'c'):
    d[f'c1_{m}'] = d[f'w_{m}'] / 100 * d.pct_1m
    d[f'c3_{m}'] = d[f'w3_{m}'] / 100 * d.pct_3m_ann
    d[f'c12_{m}'] = d[f'w12_{m}'] / 100 * d.pct_12m
d['direction'] = [direction(a, b) for a, b in zip(d.pct_3m_ann, d.pct_12m)]
assert abs(d.c1_c.sum() - summ.loc['core', 'estimate_mm']) < 5e-6 and abs(d.c1_h.sum() - summ.loc['headline', 'estimate_mm']) < 5e-6
d.to_csv(os.path.join(OUT, 'W_pce_oct_tab_lines.csv'), index=False, float_format='%.6f')

# ---- styling helpers: copied from Price indexes/code/build_basket_workbook.py
NAVY, GREY = PatternFill("solid", fgColor="1F3864"), PatternFill("solid", fgColor="D9E1F2")
thin = Side(style="thin", color="BFBFBF")
wb = Workbook()
ws = wb.active
ws.title = SHEET


def title(ws, text, size=14):
    ws.append([text]); ws.cell(ws.max_row, 1).font = Font(bold=True, size=size)


def section(ws, text, ncol):
    ws.append([text]); r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).font, ws.cell(r, 1).fill = Font(bold=True), GREY


def table(ws, header, rows):
    ws.append(header)
    for c in ws[ws.max_row]:
        c.font, c.fill, c.alignment = Font(bold=True, color="FFFFFF"), NAVY, Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in r])
        for c in ws[ws.max_row]:
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            if isinstance(c.value, float):
                c.number_format = "0.00"
    ws.append([])


def widths(ws, w):
    for i, x in enumerate(w, 1):
        ws.column_dimensions[get_column_letter(i)].width = x


def para(ws, text, ncol, height=30):
    ws.append([text]); r = ws.max_row
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncol)
    ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[r].height = height


NC = 11
EST = "estimate: 11 months published BEA + our October"            # 12m (Oct 2025 base)
EST_H = {'3m annualized SA': 'estimate: 2 months published BEA (Aug, Sep) + our October',
         '6m annualized SA': 'estimate: 5 months published BEA (May-Sep) + our October', '12m SA': EST}   # A3_R1-F01
title(ws, "PCE October 2026 — our bottom-up estimate (BEA publishes October PCE on Nov 25, after the Nov 18 cutoff)")
para(ws, "Estimate, not published data. Each PCE component is priced from the October CPI or PPI series BEA itself names "
         "(BEA Table 2.4.4U-D, Sep 30, 2026), weighted by September 2026 spending shares: 66% of core straight from published BLS data, "
         "21% with our estimate of BEA's own seasonal adjustment, 1% other composites with derived weights, 11% carried forward at the "
         "12-month average. Rates extend BEA's published SA September index (vintage Oct 29, 2026). Band = the build's backtest error "
         "(RMSE vs BEA first print, Dec 2025 - Sep 2026, first-release variant), scaled 4x for 3m ann., 2x for 6m ann., 1x for 12m. "
         "Backtest: our core MAE 0.042 pp vs Cleveland nowcast 0.068 and core CPI alone 0.087 (n = 10); errors leaned high (bias +0.017). "
         "Under the pre-set decision rule the threshold test is inconclusive; placement (Eli, Nov 14): our estimate is the presentation default, always shown next to the Cleveland nowcast and other forecasters (last section). "
         "Weights: nominal spending shares rescaled over the components we cover (99.7% of headline PCE; core within covered core); \"now\" = September 2026, the latest spending month. The 3m contribution gap is mostly annualization convexity (e.g. gasoline +72% ann.), with a smaller fixed-share aggregation residual; the 12m gap reflects fixed-share aggregation vs BEA's chained index. Audited (Codex, Nov 13); the forecaster comparison (added Nov 14) is press-reported and not audited. Source: 02_Research/Subtasks/04_oct_pce_build/.", NC, 135)

section(ws, "Estimated aggregates, Oct 2026 (component contributions from this build; 1m SA)", NC)
agg = []
for meas, label in (('headline', 'PCE headline'), ('core', 'PCE core')):
    s = summ.loc[meas]
    m = 'h' if meas == 'headline' else 'c'
    agg += [[label, '1m SA', s.rate_1m_pct, d[f'c1_{m}'].sum(), d[f'c1_{m}'].sum() - s.rate_1m_pct, s.band_reported, 'estimate (our October change)'],
            [label, '3m annualized SA', s.rate_3m_ann, d[f'c3_{m}'].sum(), d[f'c3_{m}'].sum() - s.rate_3m_ann, s.band_3m_ann, EST_H['3m annualized SA']],
            [label, '6m annualized SA', s.rate_6m_ann, None, None, s.band_6m_ann, EST_H['6m annualized SA']],
            [label, '12m SA', s.rate_12m, d[f'c12_{m}'].sum(), d[f'c12_{m}'].sum() - s.rate_12m, s.band_12m, EST_H['12m SA']]]
table(ws, ["Aggregate", "Horizon", "Rate %", "Sum of component contributions (pp)", "Gap (pp)", "Band ± (pp)", "Basis"], agg)

MOV_HDR = ["Rank", "Component", "Flag", "Weight now % (Sep 2026)", "Weight at start of 3m %", "1m %", "1m contribution (pp)",
           "3m ann. %", "3m ann. contribution (pp)", "How priced", "Source ID"]


def movers(m, col_rank, n=5):
    g = d[d[f'w_{m}'] != 0]
    up = g.sort_values(f'{col_rank}_{m}', ascending=False).head(n)
    dn = g.sort_values(f'{col_rank}_{m}').head(n)
    out = []
    for lab, sub in (('Up', up), ('Down', dn)):
        for k, r in enumerate(sub.itertuples(), 1):
            out.append([f'{lab} #{k}', r.name, r.flag, getattr(r, f'w_{m}'), getattr(r, f'w3_{m}'), r.pct_1m, getattr(r, f'c1_{m}'),
                        r.pct_3m_ann, getattr(r, f'c3_{m}'), r.how, r.source])
    return out


for m, label in (('h', 'PCE headline'), ('c', 'PCE core')):
    section(ws, f"{label}: top movers by 1m contribution, Oct 2026 (estimate) — the largest drivers of the October m/m change", NC)
    table(ws, MOV_HDR, movers(m, 'c1'))

H12 = ["Rank", "Component", "Flag", "Weight now % (Sep 2026)", "Weight at start of 12m %", "12m % (estimate)", "12m contribution (pp, estimate)",
       "3m ann. %", "3-mo direction", "How priced", "Source ID"]
for m, label in (('h', 'PCE headline'), ('c', 'PCE core')):
    section(ws, f"{label}: top movers by 12m contribution, Oct 2026 ({EST})", NC)
    g = d[d[f'w_{m}'] != 0]
    out = []
    for lab, sub in (('Up', g.sort_values(f'c12_{m}', ascending=False).head(5)), ('Down', g.sort_values(f'c12_{m}').head(5))):
        for k, r in enumerate(sub.itertuples(), 1):
            out.append([f'{lab} #{k}', r.name, r.flag, getattr(r, f'w_{m}'), getattr(r, f'w12_{m}'), r.pct_12m, getattr(r, f'c12_{m}'),
                        r.pct_3m_ann, r.direction, r.how, r.source])
    table(ws, H12, out)


def breadth(m, pct, w_col, thr=None, vs_avg=False):
    g = d[(d[w_col] != 0) & d[pct].notna()]
    if vs_avg:
        g = g[g.avg_12m_2018_19.notna()]
        return 100 * g.loc[g[pct] > g.avg_12m_2018_19, w_col].sum() / g[w_col].sum()
    return 100 * g.loc[g[pct] > thr, w_col].sum() / g[w_col].sum()


section(ws, "Breadth, Oct 2026: share of weight with price growth above thresholds (calculated, estimate)", NC)
table(ws, ["Index", "% of weight >3% 3m ann. (12m-base weights)", "% >3% 3m ann. (3m-base weights)", "% of weight >3% y/y (12m-base weights)",
           "% above own 2018-19 avg y/y (12m-base weights)"],
      [[lab, breadth(m, 'pct_3m_ann', f'w12_{m}', 3), breadth(m, 'pct_3m_ann', f'w3_{m}', 3), breadth(m, 'pct_12m', f'w12_{m}', 3),
        breadth(m, 'pct_12m', f'w12_{m}', vs_avg=True)] for m, lab in (('h', 'PCE headline'), ('c', 'PCE core'))])

# Sep 2026 3m breadth from BEA's published component indexes, same lines and the same 3m-base weighting
sep_rows = []
for m, lab in (('h', 'PCE headline'), ('c', 'PCE core')):
    wsep = eng.estimate('2026-07', k=12, version='2026-09-30')[1].set_index('line')   # shares of Jun 2026 = start of Sep's 3m window
    v = []
    for r in d.itertuples():
        bl = 156 if r.line == 157 else r.line
        p = eng.bea_p[bl]
        x = 100 * ((p.get(dc.P('2026-09')) / p.get(dc.P('2026-06'))) ** 4 - 1)
        v.append((100 * wsep.at[r.line, f'w_{m}'], x))
    v = pd.DataFrame(v, columns=['w', 'x']); v = v[(v.w != 0) & v.x.notna()]
    sep_rows.append([lab, 100 * v.loc[v.x > 3, 'w'].sum() / v.w.sum(), breadth(m, 'pct_3m_ann', f'w3_{m}', 3)])
section(ws, "3m breadth, Sep vs Oct 2026: % of weight >3% 3m ann., 3m-base weights in each column (calculated)", NC)
table(ws, ["Index", "Sep 2026 (BEA published)", "Oct 2026 (estimate)"], sep_rows)

clev = pd.read_csv(os.path.join(OUT, 'cleveland_nowcast_history.csv')).query("target_month == '2026-10'").iloc[0]
import json
_yr = json.load(open(os.path.join(ROOT, '03_Data', 'Raw', 'ClevelandFed_nowcast_year_2026-11-11.json')))
_yr = [e for e in _yr if e['chart'].get('subcaption') == '2026-10'][0]
clev_yy = {s_['seriesname']: float(s_['data'][-1]['value']) for s_ in _yr['dataset'] if s_['data'] and s_['data'][-1].get('value')}
section(ws, "For comparison: Cleveland Fed nowcast for October 2026 (as of Nov 10; unchanged through the Nov 13 update, re-pulled Nov 14)", NC)
table(ws, ["Index", "Our estimate, 1m %", "Cleveland nowcast, 1m %", "Our estimate, 12m %", "Cleveland nowcast, 12m %"],
      [['PCE headline', summ.loc['headline', 'rate_1m_pct'], float(clev.pce_nowcast_on_cpi_day), summ.loc['headline', 'rate_12m'], clev_yy['PCE Inflation']],
       ['PCE core', summ.loc['core', 'rate_1m_pct'], float(clev.core_pce_nowcast_on_cpi_day), summ.loc['core', 'rate_12m'], clev_yy['Core PCE Inflation']]])
# ---- other forecasters (added Nov 14; Checkpoint D): post-PPI estimates, press reports of client notes
fc = pd.read_csv(os.path.join(OUT, 'R_forecaster_oct2026_2026-11-14.csv'), dtype=str).fillna('')
fc = fc[fc.timing.str.startswith('after PPI') & ~fc.forecaster.str.startswith('UMD')]
num = lambda x: float(x) if re.fullmatch(r'-?\d+(\.\d+)?', x) else (x or None)
section(ws, "For comparison: other forecasters' October 2026 estimates after the Nov 13 PPI release (press reports of client notes; not audited)", NC)
table(ws, ["Forecaster", "Core 1m %", "Core 12m %", "Headline 1m %", "Headline 12m %", "Revised from (1m)", "Source"],
      [['Our estimate', summ.loc['core', 'rate_1m_pct'], summ.loc['core', 'rate_12m'], summ.loc['headline', 'rate_1m_pct'], summ.loc['headline', 'rate_12m'], None, 'this build']] +
      [[r.forecaster, num(r.core_mm), num(r.core_yy), num(r.headline_mm), num(r.headline_yy), r.revised_from or None, r.outlet_and_date] for r in fc.itertuples()])
para(ws, "Sources and quotes: 02_Research/Subtasks/04_oct_pce_build/outputs/R_forecaster_oct2026_2026-11-14.csv. Bank notes themselves were not accessed. "
         "Pre-PPI estimates (Pantheon 0.35-0.40, Reuters-polled economists 0.4, SocGen 0.30 central) are in that file, not shown here.", NC, 30)
widths(ws, [16, 52, 16, 12, 14, 10, 14, 10, 14, 30, 44])
wb.save(BUILD)
print('saved', BUILD)
print(f"core 1m {d.c1_c.sum():.4f} | headline 1m {d.c1_h.sum():.4f}")
