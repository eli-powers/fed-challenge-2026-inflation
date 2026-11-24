"""Build 01_Finals/data/Slide3B_Inflation_Data.xlsx (slide 3B: forecast and scenarios).

Run from the project root:
    python3 -I "02_Research/Subtasks/12_slide3b_research/code/build_slide3b_workbook.py"            # build
    python3 -I "02_Research/Subtasks/12_slide3b_research/code/build_slide3b_workbook.py" --verify   # build + LibreOffice recalc

Design (GO.md): same two-layer design as slides 1 and 2. READING_GUIDE first, README, research tabs, then grey raw_ tabs.
The scenario grid is LIVE FORMULAS: SPF baseline (raw_SPF) + oil gap (raw_Brent_daily, raw_STEO) mapped through the
FEDS note's Figure 2 response (raw_response). Every formula cell has an expected value computed here (EXPECT), checked
after a LibreOffice recalculation (--verify). semantic_check() compares the live-formula values with the pipeline's
processed/scenario_grid_<spf>.csv (03_Data/pipelines/forecast_3b). Chart and verify helpers are reused from the slide 1
builder. Fix inputs (pipeline raw/config, agent outputs), then rebuild; do not hand-edit the xlsx unless Eli has started to.
Inputs are read from the pipeline's raw folder (default: latest raw/<date>/), and SPF vintage from --spf (default 2026Q3).
"""
import csv
import datetime as dt
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '12_slide3b_research')
OUT = os.path.join(SUB, 'outputs')
PIPE = os.environ.get('SLIDE3B_PIPE') or os.path.join(ROOT, '03_Data', 'pipelines', 'forecast_3b')   # SLIDE3B_PIPE: test against a scratch pipeline copy
S1CODE = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code')
XLSX = os.environ.get('SLIDE3B_OUT') or os.path.join(ROOT, '01_Finals', 'data', 'Slide3B_Inflation_Data.xlsx')
SCRIPT = '12_slide3b_research/code/build_slide3b_workbook.py'
BUILD_DATE = dt.date.today().isoformat()
REL = lambda p: os.path.relpath(p, ROOT)
SPF = next((a.split('=')[1] for a in sys.argv if a.startswith('--spf=')), '2026Q3')

sys.path.insert(0, S1CODE)
sys.path.insert(0, os.path.join(PIPE, 'code'))
import build_slide1_workbook as b1           # noqa: E402  (helpers only)
import parsers as P                         # noqa: E402  (pipeline parsers, read-only)
import pandas as pd                         # noqa: E402
from openpyxl import Workbook, load_workbook   # noqa: E402
from openpyxl.chart import BarChart, LineChart, Reference, Series   # noqa: E402
from openpyxl.comments import Comment       # noqa: E402
from openpyxl.styles import Alignment, Font   # noqa: E402
from openpyxl.utils import get_column_letter as CL   # noqa: E402

put, hdr_row, section, header, raw_meta = b1.put, b1.hdr_row, b1.section, b1.header, b1.raw_meta
style_chart, line_style, add_chart = b1.style_chart, b1.line_style, b1.add_chart
FILL_EST, FILL_KEY, F_BOLD = b1.FILL_EST, b1.FILL_KEY, b1.F_BOLD
EXPECT = b1.EXPECT
b1.TAB_COLORS.update({'READING_GUIDE': 'FF0000', 'README': '1F3864', 'Baseline': 'C00000', 'Oil_paths': 'BF8F00',
                      'Pass_through': 'BF8F00', 'Scenario_grid': 'C00000', 'Fan_chart': '2F5597', 'SEP_compare': '2F5597',
                      'Slide_worthiness': '548235', 'Sources': '1F3864', 'Judgment_calls_and_paywalled': 'FF0000'})
SEMANTIC = []   # (sheet, coord, expected_from_pipeline_csv, label)
KEY = {}        # name -> 'Sheet!A1' for the reading guide
F2, F3, F4 = '0.00', '0.000', '0.0000'


def note(cell, text):
    cell.comment = Comment(text, 'build_slide3b_workbook.py', width=360, height=130)


def rd(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def latest_raw():
    base = os.path.join(PIPE, 'raw')
    ds = sorted(d for d in os.listdir(base) if re.match(r'\d{4}-\d{2}-\d{2}', d))
    return os.path.join(base, ds[-1])


RAW = latest_raw()
RF = lambda n: os.path.join(RAW, n)
QS = P.qrange('2026Q1', '2027Q4')          # shown quarters
HQ = P.qrange('2025Q1', '2027Q4')          # oil chart quarters
CENTRAL = [('P1', 'P1 Baseline oil (latest STEO)'), ('P2', 'P2 Oil rises again ($110 flat)'),
           ('P3', 'P3 Hormuz reopens (pre-war trend + $25)')]
REG = [('pre', 'Pre-pandemic dynamics'), ('post', 'Post-pandemic dynamics (stronger persistence and pass-through)')]
RCOL = {'pre': 2, 'persistence_only': 3, 'post': 4}   # raw_response / Pass_through columns


# ============================================================================ load inputs (pipeline raw)
med = P.read_spf_median(RF('medianLevel.xlsx'))
mrow = P.median_row(med, SPF)
hm = P.horizon_map(SPF)
SPFROW_G = {str(v) for k, v in hm.items() if k in P.SPF_Q_VARS}   # quarters the survey publishes (text tabs)
SPFQ4Q4 = {2026: float(mrow['COREPCEA']), 2027: float(mrow['COREPCEB'])}
disp = P.read_dispersion_d1(RF('Dispersion_1.xlsx')).get(SPF, {})
deadline, release, _ = P.parse_release_dates(RF('spf-release-dates.txt'), SPF)
core = P.load_fred_obs(RF('PCEPILFE_observations.json'))
brent = P.read_eia_daily(RF('EIA_RBRTEd.xls'))
steo_rel = P.parse_steo_release_dates(RF('page_steo_outlook.html'))
ASSUME_V = P.steo_vintage_for(str(deadline)[:10], steo_rel)[0]
LATEST_V = P.latest_steo(steo_rel)
STEO = {v: P.read_steo_series(RF(f'{v}_base.xlsx')) for v in dict.fromkeys((ASSUME_V, LATEST_V, 'feb26'))}
GQ = P.qrange(str(hm['COREPCE2']), '2027Q4')   # gap quarters start at the survey quarter (pipeline rule)
LAST_ACT = P.quarter_of(core.index[-1])       # last actual core PCE quarter
CENTRAL[0] = ('P1', f'P1 Baseline oil ({LATEST_V} STEO)')
RESP = {}
for r in rd(os.path.join(PIPE, 'config', 'regime_response.csv')):
    RESP.setdefault(r['regime'], []).append(float(r['level_response_pct_per_10pct']))
GRID = rd(os.path.join(PIPE, 'processed', f'scenario_grid_{SPF}.csv'))
FAN = rd(os.path.join(PIPE, 'processed', f'fan_{SPF}.csv'))
SEP = rd(os.path.join(OUT, 'A_q1_sep.csv'))


def gcell(path, regime, quarter, col='scenario_qq_ann'):
    for r in GRID:
        if r['is_central'] == 'True' and r['oil_path'] == path and r['regime'] == regime and r['quarter'] == quarter:
            return float(r[col])
    raise KeyError((path, regime, quarter))


# ============================================================================ raw tabs
def build_raw_pce(ws):
    raw_meta(ws, 'raw_PCE: core PCE price index (PCEPILFE), monthly, SA, 2017=100',
             [('Source', 'BEA via FRED PCEPILFE (observations JSON)'), ('File', REL(RF('PCEPILFE_observations.json'))),
              ('Vintage', 'FRED realtime ' + str(core.attrs.get('realtime', '2026-10-29 (BEA Sep 2026 release)'))),
              ('Note', 'Quarterly average of the monthly index (col C label) feeds the Baseline tab actual quarters.')])
    hdr_row(ws, 6, 1, ['Month', 'Index (SA)', 'Quarter'], [12, 12, 10])
    rows = {}
    r = 7
    for d, v in core.items():
        if d < pd.Timestamp('2025-01-01'):
            continue
        put(ws, r, 1, d.strftime('%Y-%m'))
        put(ws, r, 2, float(v), F3)
        put(ws, r, 3, P.quarter_of(d))
        rows[d.strftime('%Y-%m')] = r
        r += 1
    return rows, r - 1


def build_raw_brent(ws):
    raw_meta(ws, 'raw_Brent_daily: Brent spot FOB, $/bbl, daily (EIA RBRTE)',
             [('Source', 'EIA, Europe Brent Spot Price FOB (RBRTE), daily; FRED DCOILBRENTEU matches (Agent B)'),
              ('File', REL(RF('EIA_RBRTEd.xls'))), ('Last observation', str(brent.index[-1].date())),
              ('Note', 'NSA. Quarter label in col C drives AVERAGEIFS/SUMIFS/COUNTIFS on Oil_paths.')])
    hdr_row(ws, 6, 1, ['Date', 'Brent $/bbl', 'Quarter', 'Month'], [12, 12, 10, 10])
    r = 7
    for d, v in brent.items():
        if d < pd.Timestamp('2025-01-01'):
            continue
        put(ws, r, 1, d.strftime('%Y-%m-%d'))
        put(ws, r, 2, float(v), F2)
        put(ws, r, 3, P.quarter_of(d))
        put(ws, r, 4, d.strftime('%Y-%m'))
        r += 1
    return 7, r - 1


def build_raw_steo(ws):
    raw_meta(ws, 'raw_STEO: EIA Short-Term Energy Outlook, Brent spot (BREPUUS), monthly $/bbl, by vintage',
             [('Source', 'EIA STEO archive <vintage>_base.xlsx, sheet 2tab, series BREPUUS'),
              ('Files', '; '.join(REL(RF(f'{v}_base.xlsx')) for v in STEO)),
              ('Roles', f'{ASSUME_V} = oil the SPF baseline assumed (proxy: latest STEO released on/before the SPF deadline {str(deadline)[:10]}); '
                        f'{LATEST_V} = Path 1; feb26 = last pre-war vintage (Path 3 trend)'),
              ('Release dates', '; '.join(f'{v} {steo_rel.get(v)}' for v in STEO))])
    vs = list(STEO)
    hdr_row(ws, 6, 1, ['Month', 'Quarter'] + [f'{v} BREPUUS' for v in vs], [10, 10, 14, 14, 14])
    rows = {}
    r = 7
    for mth in pd.period_range('2026-01', '2027-12', freq='M'):
        ts = mth.to_timestamp()
        put(ws, r, 1, str(mth))
        put(ws, r, 2, P.quarter_of(ts))
        for j, v in enumerate(vs):
            put(ws, r, 3 + j, float(STEO[v][ts]), F2)
        rows[str(mth)] = r
        r += 1
    return rows, {v: 3 + j for j, v in enumerate(vs)}, r - 1


def build_raw_spf(ws):
    raw_meta(ws, f'raw_SPF: Philadelphia Fed SPF, core PCE, survey {SPF}',
             [('Source', 'Philadelphia Fed Survey of Professional Forecasters, medianLevel.xlsx sheet COREPCE; Dispersion_1.xlsx sheet COREPCE'),
              ('Files', REL(RF('medianLevel.xlsx')) + '; ' + REL(RF('Dispersion_1.xlsx'))),
              ('Survey dates', f'deadline {str(deadline)[:10]}, release {str(release)[:10]} (spf-release-dates.txt)'),
              ('Units', 'COREPCE1-6: q/q annualized % (SA), quarters t-1..t+4; COREPCEA/B/C: Q4/Q4 % for the survey year and the next two')])
    hdr_row(ws, 6, 1, ['Variable', 'Target period', 'Horizon', 'Median', 'P25 (published)', 'P75 (published)'], [12, 14, 10, 10, 14, 14])
    rows = {}
    r = 7
    for k, v in enumerate(P.SPF_Q_VARS + P.SPF_A_VARS):
        put(ws, r, 1, v)
        put(ws, r, 2, str(hm[v]))
        put(ws, r, 3, 'qq_ann' if v in P.SPF_Q_VARS else 'Q4/Q4')
        put(ws, r, 4, float(mrow[v]), F4)
        if v in P.SPF_Q_VARS and (k - 1) in disp:
            put(ws, r, 5, disp[k - 1][0], F3)
            put(ws, r, 6, disp[k - 1][1], F3)
        rows[str(hm[v]) if v in P.SPF_Q_VARS else f'A{hm[v]}'] = r
        r += 1
    return rows


def build_raw_response(ws):
    raw_meta(ws, 'raw_response: FEDS Note Figure 2 data, core price level response (%) to a permanent 10% oil price rise',
             [('Source', 'De Michelis, Orak, Pradhan & Queralto, FEDS Notes Nov 9 2026, accessible version, Figure 2 data table'),
              ('Files', 'config: ' + REL(os.path.join(PIPE, 'config', 'regime_response.csv')) + '; raw: 03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/'),
              ('Scope', 'Average of five advanced economies (Canada, euro area, Japan, UK, US), NOT US-only. Authors: an upper bound.'),
              ('Note', 'k = quarters after the rise (k=0 = quarter of the rise). Cumulative level effect, % per 10% oil rise.')])
    hdr_row(ws, 6, 1, ['k', 'Pre-pandemic', 'Stronger persistence only', 'Stronger persistence and pass-through (post)'], [6, 16, 18, 22])
    for k in range(13):
        put(ws, 7 + k, 1, k)
        for reg, c in RCOL.items():
            put(ws, 7 + k, c, RESP[reg][k], '0.000000')


def build_raw_sep(ws):
    raw_meta(ws, 'raw_SEP: FOMC Summary of Economic Projections, Sep 16 2026, core PCE inflation (Q4/Q4 %)',
             [('Source', 'federalreserve.gov fomcprojtabl20260916 (Table 1)'), ('File', '03_Data/Raw/FOMC_SEP_2026-09_2026-11-15/fomcprojtabl20260916.htm'),
              ('Parsed by', 'Agent A, outputs/A_q1_sep.csv (coordinator-verified against the htm)'), ('Note', 'No longer-run projection for core PCE.')])
    hdr_row(ws, 6, 1, ['Year', 'Median', 'Central tendency low', 'Central tendency high', 'Range low', 'Range high'], [8, 10, 12, 12, 10, 10])
    out = {}
    for i, y in enumerate((2026, 2027, 2028, 2029)):
        r = 7 + i
        put(ws, r, 1, y)
        for row in SEP:
            if row['variable'] == 'core_pce' and int(row['target_year']) == y and row['vintage'].startswith('20260916'):
                if row['stat'] == 'median':
                    put(ws, r, 2, float(row['value']), '0.0')
                elif row['stat'] == 'central_tendency':
                    put(ws, r, 3, float(row['low']), '0.0')
                    put(ws, r, 4, float(row['high']), '0.0')
                elif row['stat'] == 'range':
                    put(ws, r, 5, float(row['low']), '0.0')
                    put(ws, r, 6, float(row['high']), '0.0')
        out[y] = r
    return out


# ============================================================================ research tabs
def build_baseline(ws, PCEROW, SPFROW):
    header(ws, f'Baseline: SPF median core PCE path (survey {SPF}) with actual quarters',
           'Question: what does the outside forecast say, before any oil adjustment, and how does it compare with the data since?',
           f'Core PCE, SA. q/q annualized % unless marked Q4/Q4. SPF deadline {str(deadline)[:10]} (' + ('before' if str(deadline)[:10] < '2026-09-01' else 'after') + ' the Sep-Oct oil spike). Actual = FRED PCEPILFE quarterly average.')
    hdr_row(ws, 5, 1, ['Quarter', 'Actual index (qtr avg)', 'Actual q/q ann.', 'SPF median q/q ann.', 'SPF P25', 'SPF P75', 'Baseline used', 'Status'],
            [10, 14, 12, 14, 10, 10, 13, 46])
    rows = {}
    qlist = P.qrange('2025Q4', '2027Q4')
    last_act = P.quarter_of(core.index[-1])
    idx = {q: core[[P.quarter_of(d) == q for d in core.index]] for q in qlist}
    act_v = {}
    for i, q in enumerate(qlist):
        r = 6 + i
        rows[q] = r
        put(ws, r, 1, q)
        if P.qidx(q) <= P.qidx(last_act):
            av = float(idx[q].mean())
            put(ws, r, 2, f'=AVERAGEIFS(raw_PCE!$B:$B,raw_PCE!$C:$C,A{r})', F3, expect=av)
            act_v[q] = av
            if i > 0:
                pq = qlist[i - 1]
                e = ((av / act_v[pq]) ** 4 - 1) * 100
                put(ws, r, 3, f'=((B{r}/B{r-1})^4-1)*100', F2, expect=e)
                act_v[q + 'rate'] = e
        if q in SPFROW:
            sr = SPFROW[q]
            put(ws, r, 4, f'=raw_SPF!D{sr}', F2, expect=float(mrow[[k for k, v in hm.items() if str(v) == q and k in P.SPF_Q_VARS][0]]))
            k = [kk for kk in P.SPF_Q_VARS if str(hm[kk]) == q][0]
            j = P.SPF_Q_VARS.index(k) - 1
            if j in disp:
                put(ws, r, 5, f'=raw_SPF!E{sr}', F2, expect=disp[j][0])
                put(ws, r, 6, f'=raw_SPF!F{sr}', F2, expect=disp[j][1])
    # derived last quarter (2027Q4) from the annual Q4/Q4 median
    y = 2027
    q4 = f'{y}Q4'
    base = {}
    if q4 not in SPFROW:
        a = float(mrow['COREPCEB'])
        q1, q2, q3 = (float(mrow[[k for k in P.SPF_Q_VARS if str(hm[k]) == f'{y}Q{n}'][0]]) for n in (1, 2, 3))
        e = P.derive_q4_from_annual(q1, q2, q3, a)
        r = rows[q4]
        c = put(ws, r, 4, f'=((1+raw_SPF!D{SPFROW["A2027"]}/100)^4/((1+D{rows["2027Q1"]}/100)*(1+D{rows["2027Q2"]}/100)*(1+D{rows["2027Q3"]}/100))-1)*100',
                F2, expect=e, fill=FILL_EST)
        note(c, 'DERIVED, not published: the SPF gives no 2027Q4 quarterly figure. Solved so that 2027Q1-Q4 compound to the SPF 2027 Q4/Q4 median '
                '(COREPCEB). Approximate: quarterly and annual medians come from different respondents (Agent A: B +/-0.05 -> 2.07/2.47).')
    for q in qlist:
        r = rows[q]
        if q == '2025Q4':
            continue
        if P.qidx(q) <= P.qidx(last_act):
            put(ws, r, 7, f'=C{r}', F2, expect=act_v[q + 'rate'])
            base[q] = act_v[q + 'rate']
            put(ws, r, 8, 'actual (FRED PCEPILFE, vintage of the Sep 2026 PCE release)')
        else:
            v = EXPECT[(ws.title, f'D{r}')]
            put(ws, r, 7, f'=D{r}', F2, expect=v, fill=FILL_KEY if q in ('2026Q4', '2027Q4') else None)
            base[q] = v
            put(ws, r, 8, 'SPF median, published' if q in SPFROW else 'SPF, DERIVED from the 2027 Q4/Q4 median (yellow)')
    # Q4/Q4 block
    r0 = rows['2027Q4'] + 2
    section(ws, r0, 'Q4/Q4 (from the quarterly path) vs the SPF published annual median')
    hdr_row(ws, r0 + 1, 1, ['Year', 'Baseline Q4/Q4 (actual + SPF quarters)', 'SPF published Q4/Q4 median', 'Difference', 'Note'], None)
    q4q4 = {}
    for i, yy in enumerate((2026, 2027)):
        r = r0 + 2 + i
        qs = [f'{yy}Q{n}' for n in (1, 2, 3, 4)]
        e = (math.prod((1 + base[q] / 100) ** 0.25 for q in qs) - 1) * 100
        q4q4[yy] = e
        put(ws, r, 1, yy)
        put(ws, r, 2, '=(' + '*'.join(f'(1+G{rows[q]}/100)^0.25' for q in qs) + '-1)*100', F2, expect=e, fill=FILL_KEY)
        pub = float(mrow['COREPCEA' if yy == 2026 else 'COREPCEB'])
        put(ws, r, 3, f'=raw_SPF!D{SPFROW["A" + str(yy)]}', F2, expect=pub)
        put(ws, r, 4, f'=B{r}-C{r}', F2, expect=e - pub)
        if yy == 2026:
            k3 = [kk for kk in P.SPF_Q_VARS if str(hm[kk]) == '2026Q3']
            s3 = f'SPF 2026Q3 {float(mrow[k3[0]]):.2f}' if k3 else 'SPF 2026Q3'
            put(ws, r, 5, f'Built with actual 2026Q1-Q3 (revised data; {s3} vs actual {act_v["2026Q3rate"]:.2f})')
        else:
            put(ws, r, 5, 'Equal by construction: 2027Q4 is derived from this median' if '2027Q4' not in SPFROW else
                'Published 2027Q4 used; the gap is a median-of-annual vs product-of-quarterly-medians difference (different respondents)')
    KEY['base_2026q4'] = f"Baseline!G{rows['2026Q4']}"
    KEY['base_2027q4'] = f"Baseline!G{rows['2027Q4']}"
    KEY['base_q4q4_2026'] = f'Baseline!B{r0 + 2}'
    KEY['base_q4q4_2027'] = f'Baseline!B{r0 + 3}'
    # jump-off
    r = r0 + 6
    section(ws, r, 'Jump-off: the October estimate vs the baseline (calculations, not forecasts; Agent A outputs/A_q1_jumpoff.csv)')
    hdr_row(ws, r + 1, 1, ['Item', 'Value', 'Source'], None)
    J = {x['item']: x for x in rd(os.path.join(OUT, 'A_q1_jumpoff.csv'))} if os.path.exists(os.path.join(OUT, 'A_q1_jumpoff.csv')) else {}
    # live jump-off (vintage-proof): Oct index = Sep index x (1 + Oct m/m est.); Nov-Dec equal m/m
    sep_m = core.index[-1].strftime('%Y-%m')
    sep_i = float(core.iloc[-1])
    q3r, q25r = rows[LAST_ACT], rows['2025Q4']
    q3avg, q25avg = act_v[LAST_ACT], act_v['2025Q4']
    b4 = base['2026Q4']
    yoy, mm = 3.24, 0.295
    octi = sep_i * (1 + mm / 100)
    g = 1 + mm / 100
    e_q4q4_oct = (octi * (1 + g + g * g) / 3 / q25avg - 1) * 100
    T = 3 * q3avg * (1 + b4 / 100) ** 0.25 / octi
    e_mm_need = ((-1 + math.sqrt(4 * T - 3)) / 2 - 1) * 100
    e_q4q4_b = (q3avg * (1 + b4 / 100) ** 0.25 / q25avg - 1) * 100
    R0 = r + 2
    lines = [('Oct 2026 core PCE y/y, UMD estimate (est.)', yoy, None, 'Slide1_Inflation_Data.xlsx Headline!C10 (est.; BEA Oct PCE out Nov 25)'),
             ('Oct 2026 core PCE m/m, UMD estimate (est.)', mm, None, 'slide 1 / 04_oct_pce_build (est.); input'),
             (f'Oct 2026 core PCE index (est.) = {sep_m} index x (1 + m/m)', f'=raw_PCE!B{PCEROW[sep_m]}*(1+B{R0 + 1}/100)', octi, 'live formula'),
             ('2026 Q4/Q4 if Nov-Dec m/m = Oct pace', f'=(B{R0 + 2}*(1+(1+B{R0 + 1}/100)+(1+B{R0 + 1}/100)^2)/3/B{q25r}-1)*100', e_q4q4_oct, 'live formula (A_q1_jumpoff.csv (i): 3.33)'),
             (f'Nov-Dec m/m needed for 2026Q4 = baseline {b4:.4f} (given Oct est.)', f'=((-1+SQRT(4*(3*B{q3r}*(1+G{rows["2026Q4"]}/100)^0.25/B{R0 + 2})-3))/2-1)*100', e_mm_need, 'live formula (A_q1_jumpoff.csv (ii-b): 0.053 on the Q3 SPF)'),
             ('2026 Q4/Q4 if 2026Q4 = baseline pace', f'=(B{q3r}*(1+G{rows["2026Q4"]}/100)^0.25/B{q25r}-1)*100', e_q4q4_b, 'live formula (A_q1_jumpoff.csv (ii-b): 3.08 on the Q3 SPF)')]
    for i, (lbl, v, e, src) in enumerate(lines):
        put(ws, R0 + i, 1, lbl)
        if e is None:
            c = put(ws, R0 + i, 2, v, '0.000', fill=FILL_EST)
            note(c, 'Input (our estimate, not a live formula): ' + src)
        else:
            put(ws, R0 + i, 2, v, '0.000', expect=e, fill=FILL_EST)
        put(ws, R0 + i, 3, src)
    r = R0 - 2
    KEY['jump_oct'] = f'Baseline!B{R0 + 1}'      # Oct m/m 0.295 (R1-F02: was the y/y row)
    KEY['jump_mm'] = f'Baseline!B{R0 + 4}'
    # chart
    ch = LineChart()
    style_chart(ch, f'Core PCE: actual and SPF {SPF} median path', '% q/q annualized', 'Quarter',
                f'Source: BEA via FRED PCEPILFE; Philadelphia Fed SPF {SPF} (deadline {str(deadline)[:10]})' + ('; 2027Q4 derived' if '2027Q4' not in SPFROW else ''), w=22, h=11, yfmt='0.0')
    first, last = rows['2026Q1'], rows['2027Q4']
    for col, color, dash, nm in ((7, 'C00000', None, None), (4, '1F3864', 'dash', None), (5, 'A6A6A6', 'sysDot', None), (6, 'A6A6A6', 'sysDot', None)):
        s = Series(Reference(ws, min_col=col, min_row=first, max_row=last), title=ws.cell(row=5, column=col).value)
        line_style(s, color, dash=dash, width_pt=2.25 if col == 7 else 1.5)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
    add_chart(ws, ch, 'J5')
    return rows, base, q4q4


def build_oil(ws, STROW, STCOL, BR0, BR1):
    header(ws, 'Oil_paths: three Brent paths vs the oil price the baseline assumed',
           'Question: how far does each oil scenario sit from the oil price the SPF forecasters likely assumed, quarter by quarter?',
           'Brent spot FOB $/bbl, NSA, quarterly mean. Gap = 100 x ln(path / assumed), log points (~%). Gap starts ' + GQ[0] + ' (the survey quarter); actual quarters are history.')
    last = brent.index[-1]
    lastq = P.quarter_of(last)
    qend = pd.Period(lastq, 'Q').end_time.normalize()
    rem = [d for d in pd.bdate_range(last + pd.Timedelta(days=1), qend)
           if not ((d.month, d.day) in ((12, 25), (1, 1)) or (d.month == 11 and d.weekday() == 3 and 22 <= d.day <= 28))]
    remm = {}
    for d in rem:
        remm[d.strftime('%Y-%m')] = remm.get(d.strftime('%Y-%m'), 0) + 1
    # splice parameters
    section(ws, 5, f'Splice parameters for {lastq} (observed days + remaining weekdays at each path\'s rule; Thanksgiving and Dec 25 dropped)')
    hdr_row(ws, 6, 1, ['Parameter', 'Value', 'Note'], [44, 12, 60])
    ms = sorted(remm)
    put(ws, 7, 1, 'Last EIA Brent observation')
    put(ws, 7, 2, str(last.date()))
    put(ws, 7, 3, 'raw_Brent_daily; next EIA release Nov 18 (rerun)')
    put(ws, 8, 1, f'Observed days in {lastq}')
    nobs = int(sum(1 for d in brent.index if P.quarter_of(d) == lastq))
    put(ws, 8, 2, f'=COUNTIFS(raw_Brent_daily!$C:$C,"{lastq}")', '0', expect=nobs)
    PR = {}
    for i, m in enumerate(ms):
        put(ws, 9 + i, 1, f'Remaining weekdays in {m}')
        put(ws, 9 + i, 2, remm[m], '0')
        put(ws, 9 + i, 3, 'computed by this script from the calendar (pipeline rule)')
        PR[m] = 9 + i
    sumobs = float(brent[[P.quarter_of(d) == lastq for d in brent.index]].sum())
    rs = 9 + len(ms)
    put(ws, rs, 1, f'Sum of observed Brent in {lastq}')
    put(ws, rs, 2, f'=SUMIFS(raw_Brent_daily!$B:$B,raw_Brent_daily!$C:$C,"{lastq}")', F2, expect=sumobs)
    nrem = sum(remm.values())
    # quarterly table
    T0 = rs + 3
    section(ws, T0 - 1, 'Quarterly paths ($/bbl) and gaps vs the assumption (log points x100)')
    hdr_row(ws, T0, 1, ['Quarter', 'Actual Brent (qtr mean)', 'Days observed', f'Assumed by baseline ({ASSUME_V} STEO)',
                        f'P1 Baseline oil ({LATEST_V} STEO)', 'P2 Oil rises again ($110)', 'P3 Hormuz reopens (+$25)',
                        'Gap P1', 'Gap P2', 'Gap P3'], [10, 14, 10, 16, 14, 14, 14, 10, 10, 10])
    ROW, GAP = {}, {}
    av = brent.groupby([P.quarter_of(d) for d in brent.index]).mean()
    acol = STCOL[ASSUME_V]
    lcol = STCOL[LATEST_V]
    fcol = STCOL['feb26']
    vals = {}
    for i, q in enumerate(HQ):
        r = T0 + 1 + i
        ROW[q] = r
        put(ws, r, 1, q)
        if P.qidx(q) <= P.qidx(lastq):
            put(ws, r, 2, f'=AVERAGEIFS(raw_Brent_daily!$B:$B,raw_Brent_daily!$C:$C,A{r})', F2, expect=float(av[q]),
                fill=FILL_EST if q == lastq else None)
            put(ws, r, 3, f'=COUNTIFS(raw_Brent_daily!$C:$C,A{r})', '0', expect=int(sum(1 for d in brent.index if P.quarter_of(d) == q)))
        if q in GQ:
            mrows = [STROW[m] for m in STROW if P.quarter_of(pd.Timestamp(m + '-01')) == q]
            ea = sum(float(STEO[ASSUME_V][pd.Timestamp(m + '-01')]) for m in STROW if P.quarter_of(pd.Timestamp(m + '-01')) == q) / 3
            put(ws, r, 4, f'=AVERAGE(raw_STEO!{CL(acol)}{mrows[0]}:{CL(acol)}{mrows[-1]})', F2, expect=ea)
            vals[(q, 'A')] = ea
        for j, (pid, rule) in enumerate((('P1', 'steo'), ('P2', 'flat'), ('P3', 'feb'))):
            c = 5 + j
            if P.qidx(q) < P.qidx(lastq):
                put(ws, r, c, f'=B{r}', F2, expect=float(av[q]))
                vals[(q, pid)] = float(av[q])
            elif q == lastq:
                if rule == 'flat':
                    f = f'=($B${rs}+{nrem}*110)/($B$8+{nrem})'
                    e = (sumobs + nrem * 110) / (nobs + nrem)
                else:
                    sc = lcol if rule == 'steo' else fcol
                    add = '' if rule == 'steo' else '+25'
                    terms = '+'.join(f'$B${PR[m]}*(raw_STEO!{CL(sc)}{STROW[m]}{add})' for m in ms)
                    f = f'=($B${rs}+{terms})/($B$8+' + '+'.join(f'$B${PR[m]}' for m in ms) + ')'
                    v = STEO[LATEST_V if rule == 'steo' else 'feb26']
                    e = (sumobs + sum(remm[m] * (float(v[pd.Timestamp(m + '-01')]) + (0 if rule == 'steo' else 25)) for m in ms)) / (nobs + nrem)
                put(ws, r, c, f, F2, expect=e, fill=FILL_EST)
                vals[(q, pid)] = e
            else:
                mrows = [STROW[m] for m in STROW if P.quarter_of(pd.Timestamp(m + '-01')) == q]
                if rule == 'flat':
                    put(ws, r, c, 110, F2)
                    vals[(q, pid)] = 110.0
                else:
                    sc = lcol if rule == 'steo' else fcol
                    v = STEO[LATEST_V if rule == 'steo' else 'feb26']
                    e = sum(float(v[pd.Timestamp(m + '-01')]) for m in STROW if P.quarter_of(pd.Timestamp(m + '-01')) == q) / 3 + (0 if rule == 'steo' else 25)
                    put(ws, r, c, f'=AVERAGE(raw_STEO!{CL(sc)}{mrows[0]}:{CL(sc)}{mrows[-1]})' + ('' if rule == 'steo' else '+25'), F2, expect=e)
                    vals[(q, pid)] = e
            if q in GQ:
                g = 100 * math.log(vals[(q, pid)] / vals[(q, 'A')])
                put(ws, r, 8 + j, f'=100*LN({CL(c)}{r}/$D{r})', F2, expect=g, fill=FILL_KEY if q == '2027Q4' else None)
                GAP[(pid, q)] = (r, 8 + j, g)
                SEMANTIC.append((ws.title, f'{CL(8 + j)}{r}', float([x for x in GRID if x['is_central'] == 'True' and x['oil_path'] == pid and x['regime'] == 'post' and x['quarter'] == q][0]['oil_gap_pct']), f'gap {pid} {q}'))
    KEY['oil_gap_2027'] = f"Oil_paths!H{ROW['2027Q4']}:J{ROW['2027Q4']}"
    KEY['oil_assumed_2027'] = f"Oil_paths!D{ROW['2027Q4']}"
    KEY['oil_assumed_val'] = vals[('2027Q4', 'A')]
    ch = LineChart()
    style_chart(ch, 'Brent: scenario paths vs the oil price the baseline assumed', '$/bbl', 'Quarter',
                f'Source: EIA RBRTE daily (to {last.date()}); EIA STEO {ASSUME_V}, {LATEST_V}, feb26; rules per Bowman/Waller (Nov 10)', w=22, h=11, yfmt='0')
    first, lastr = ROW[HQ[0]], ROW[HQ[-1]]
    for col, color, dash in ((4, '000000', 'dash'), (5, '1F3864', None), (6, 'C00000', None), (7, '548235', None)):
        s = Series(Reference(ws, min_col=col, min_row=first, max_row=lastr), title=ws.cell(row=T0, column=col).value)
        line_style(s, color, dash=dash, width_pt=2.0)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=lastr))
    add_chart(ws, ch, 'L5')
    return GAP, vals


def build_pass(ws):
    header(ws, 'Pass_through: how a permanent 10% oil rise moves the core price level, by regime',
           'Question: what are the two pass-through regimes, quarter by quarter? (FEDS Note Fig. 2 data, the note\'s own numbers)',
           '% change in the core price LEVEL, k quarters after a permanent 10% rise in oil. Five-economy average (not US-only); authors call their projection an upper bound.')
    hdr_row(ws, 5, 1, ['k (quarters after)', 'Pre-pandemic', 'Stronger persistence only (backup)', 'Post-pandemic: stronger persistence and pass-through'], [16, 14, 20, 26])
    for k in range(13):
        r = 6 + k
        put(ws, r, 1, k)
        for reg, c in RCOL.items():
            put(ws, r, c, f'=raw_response!{CL(c)}{7 + k}', '0.000', expect=RESP[reg][k], fill=FILL_KEY if k == 12 and reg != 'persistence_only' else None)
    put(ws, 20, 1, 'Ratio post / pre at k=12')
    put(ws, 20, 4, '=D18/B18', '0.0', expect=RESP['post'][12] / RESP['pre'][12])
    put(ws, 22, 1, 'Text of the note rounds these: "0.05 percent after three years" (pre), "just under 0.1" (persistence only), "0.35 percent after 12 quarters" (post).')
    put(ws, 23, 1, 'Flag (Agent B): the pre and persistence-only lines cannot be reproduced from Table 2\'s pass-through sum (0.001); the post line can (within 1.5-5%). Use the figure data, not "0.001".')
    KEY['pt_k12'] = 'Pass_through!B18 (pre) and D18 (post)'
    ch = LineChart()
    style_chart(ch, 'Core price level after a permanent 10% oil rise', '% of core price level', 'Quarters after the rise',
                'Source: De Michelis et al., FEDS Notes Nov 9 2026, Fig. 2 data (five-economy average)', w=20, h=11, yfmt='0.00')
    for col, color, dash in ((2, '1F3864', None), (3, 'A6A6A6', 'dash'), (4, 'C00000', None)):
        s = Series(Reference(ws, min_col=col, min_row=6, max_row=18), title=ws.cell(row=5, column=col).value)
        line_style(s, color, dash=dash, width_pt=2.0)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=18))
    add_chart(ws, ch, 'F5')


def build_grid(ws, BROW, base, GAP):
    header(ws, 'Scenario_grid: SPF baseline + oil gap mapped to core, 3 oil paths x 2 regimes (live formulas)',
           'Question: where does core PCE end up in 2026 and 2027 under each oil path and each pass-through regime? Scenarios, NOT probabilities; no weighting.',
           'Core PCE, SA. q/q annualized % and Q4/Q4 %. Level effect L_t = sum_s R(t-s) x change in gap_s / 10; scenario q/q = baseline + (100+baseline) x (exp(4 x (L_t - L_t-1)/100) - 1). Actual quarters are not adjusted.')
    # summary table first (rows 6-14), detail below (row 20+)
    D0 = 30
    section(ws, D0 - 1, 'Detail: one block per cell. Gap from Oil_paths; R from Pass_through; baseline from Baseline. Click any cell to trace it.')
    hdr_row(ws, D0, 1, ['Cell', 'Oil path', 'Regime', 'Quarter', 'Baseline q/q ann.', 'Oil gap (log pts)', 'Change in gap', 'Level effect L (%)',
                        'Adjustment (pp, q/q ann.)', 'Scenario q/q ann.'], [24, 8, 10, 10, 12, 12, 12, 12, 14, 13])
    r = D0 + 1
    CELLS = {}
    for pid, plab in CENTRAL:
        for reg, rlab in REG:
            rows = {}
            Lv, gv = [], []
            for t, q in enumerate(GQ):
                put(ws, r, 1, f'{pid} x {reg}')
                put(ws, r, 2, pid)
                put(ws, r, 3, reg)
                put(ws, r, 4, q)
                put(ws, r, 5, f'=Baseline!G{BROW[q]}', F3, expect=base[q])
                gr, gc, g = GAP[(pid, q)]
                gv.append(g)
                put(ws, r, 6, f'=Oil_paths!{CL(gc)}{gr}', F3, expect=g)
                dg = g if t == 0 else g - gv[t - 1]
                put(ws, r, 7, f'=F{r}' if t == 0 else f'=F{r}-F{r-1}', F3, expect=dg)
                # L_t = sum_{s<=t} R_{t-s} * dg_s / 10
                rc = CL(RCOL[reg])
                terms = '+'.join(f'Pass_through!${rc}${6 + (t - s)}*G{r - t + s}' for s in range(t + 1))
                dgs = [gv[0]] + [gv[s] - gv[s - 1] for s in range(1, t + 1)]
                L = sum(RESP[reg][t - s] * dgs[s] / 10 for s in range(t + 1))
                Lv.append(L)
                put(ws, r, 8, f'=({terms})/10', '0.0000', expect=L)
                if P.qidx(q) <= P.qidx(LAST_ACT):
                    put(ws, r, 9, 0, F3)
                    put(ws, r, 10, f'=E{r}', F3, expect=base[q])
                    sc = base[q]
                    put(ws, r, 11, 'actual quarter: not adjusted (level effect carried into the next quarter\'s change)')
                else:
                    Lprev = Lv[t - 1] if t > 0 else 0.0     # first gap quarter is a forecast: preceding level effect = 0
                    adj = (100 + base[q]) * (math.exp(4 * (L - Lprev) / 100) - 1)
                    put(ws, r, 9, f'=(100+E{r})*(EXP(4*(H{r}-H{r-1})/100)-1)' if t > 0 else f'=(100+E{r})*(EXP(4*(H{r}-0)/100)-1)', F3, expect=adj)
                    sc = base[q] + adj
                    put(ws, r, 10, f'=E{r}+I{r}', F3, expect=sc)
                    SEMANTIC.append((ws.title, f'J{r}', gcell(pid, reg, q), f'scenario {pid} {reg} {q}'))
                rows[q] = (r, sc)
                r += 1
            CELLS[(pid, reg)] = rows
            r += 1
    # summary
    section(ws, 5, 'Summary: the 3 x 2 grid (key figures). Baseline = SPF path with no oil adjustment.')
    hdr_row(ws, 6, 1, ['Cell', 'Oil path', 'Regime', '2026Q4 q/q ann.', '2027Q4 q/q ann.', '2026 Q4/Q4', '2027 Q4/Q4', 'vs baseline 2027 Q4/Q4 (pp)'], None)
    sr = 7
    put(ws, sr, 1, 'Baseline (SPF, no oil adjustment)')
    put(ws, sr, 4, f'=Baseline!G{BROW["2026Q4"]}', F2, expect=base['2026Q4'])
    put(ws, sr, 5, f'=Baseline!G{BROW["2027Q4"]}', F2, expect=base['2027Q4'])
    bq = {}
    for yy, col in ((2026, 6), (2027, 7)):
        qs = [f'{yy}Q{n}' for n in (1, 2, 3, 4)]
        e = (math.prod((1 + base[q] / 100) ** 0.25 for q in qs) - 1) * 100
        bq[yy] = e
        put(ws, sr, col, '=(' + '*'.join(f'(1+Baseline!G{BROW[q]}/100)^0.25' for q in qs) + '-1)*100', F2, expect=e)
    SUMROW = {}
    res = {}
    for i, ((pid, reg), rows) in enumerate(CELLS.items()):
        rr = sr + 1 + i
        SUMROW[(pid, reg)] = rr
        put(ws, rr, 1, f'{pid} x {reg}')
        put(ws, rr, 2, dict(CENTRAL)[pid])
        put(ws, rr, 3, dict(REG)[reg])
        put(ws, rr, 4, f'=J{rows["2026Q4"][0]}', F2, expect=rows['2026Q4'][1], fill=FILL_KEY)
        put(ws, rr, 5, f'=J{rows["2027Q4"][0]}', F2, expect=rows['2027Q4'][1], fill=FILL_KEY)
        for yy, col in ((2026, 6), (2027, 7)):
            qs = [f'{yy}Q{n}' for n in (1, 2, 3, 4)]
            parts, e = [], 1.0
            for q in qs:
                if q in rows:
                    parts.append(f'(1+J{rows[q][0]}/100)^0.25')
                    e *= (1 + rows[q][1] / 100) ** 0.25
                else:
                    parts.append(f'(1+Baseline!G{BROW[q]}/100)^0.25')
                    e *= (1 + base[q] / 100) ** 0.25
            e = (e - 1) * 100
            res[(pid, reg, yy)] = e
            put(ws, rr, col, '=(' + '*'.join(parts) + '-1)*100', F2, expect=e, fill=FILL_KEY)
            SEMANTIC.append((ws.title, f'{CL(col)}{rr}', gcell(pid, reg, f'{yy}Q4/{yy - 1}Q4'), f'Q4/Q4 {pid} {reg} {yy}'))
        put(ws, rr, 8, f'=G{rr}-$G${sr}', F2, expect=res[(pid, reg, 2027)] - bq[2027])
    rr = sr + 7
    put(ws, rr, 1, 'Spread across the 6 cells (max - min)')
    for col in (4, 5, 6, 7):
        vals = [EXPECT[(ws.title, f'{CL(col)}{sr + 1 + i}')] for i in range(6)]
        put(ws, rr, col, f'=MAX({CL(col)}{sr + 1}:{CL(col)}{sr + 6})-MIN({CL(col)}{sr + 1}:{CL(col)}{sr + 6})', F2, expect=max(vals) - min(vals), bold=True)
    KEY['grid'] = f'Scenario_grid!D{sr + 1}:G{sr + 6}'
    KEY['grid_spread'] = f'Scenario_grid!G{rr}'
    # axis comparison (2027 Q4/Q4 and 2027Q4)
    ar = rr + 2
    put(ws, ar, 1, 'Which axis moves 2027 more? (range, pp)')
    put(ws, ar, 4, '2027Q4 q/q ann.')
    put(ws, ar, 7, '2027 Q4/Q4')
    lines = [('Across oil paths, pre-pandemic regime held', [('P1', 'pre'), ('P2', 'pre'), ('P3', 'pre')]),
             ('Across oil paths, post-pandemic regime held', [('P1', 'post'), ('P2', 'post'), ('P3', 'post')])]
    AX = {}
    for i, (lbl, cs) in enumerate(lines):
        r2 = ar + 1 + i
        put(ws, r2, 1, lbl)
        for col in (5, 7):
            refs = ','.join(f'{CL(col)}{SUMROW[c]}' for c in cs)
            vals = [EXPECT[(ws.title, f'{CL(col)}{SUMROW[c]}')] for c in cs]
            put(ws, r2, col, f'=MAX({refs})-MIN({refs})', F2, expect=max(vals) - min(vals), fill=FILL_KEY)
        AX[lbl] = r2
    for i, (pid, _) in enumerate(CENTRAL):
        r2 = ar + 3 + i
        put(ws, r2, 1, f'Across regimes, {pid} held (post - pre)')
        for col in (5, 7):
            put(ws, r2, col, f'={CL(col)}{SUMROW[(pid, "post")]}-{CL(col)}{SUMROW[(pid, "pre")]}', F2,
                expect=EXPECT[(ws.title, f'{CL(col)}{SUMROW[(pid, "post")]}')] - EXPECT[(ws.title, f'{CL(col)}{SUMROW[(pid, "pre")]}')], fill=FILL_KEY)
    KEY['axis'] = f'Scenario_grid!E{ar + 1}:G{ar + 5}'
    # regime-weight hook (Eli input)
    hr = ar + 7
    put(ws, hr, 1, 'REGIME WEIGHT HOOK (Eli\'s input after slide 3A): post-pandemic weight')
    c = put(ws, hr, 4, None, fill=FILL_EST)
    note(c, 'Blank on purpose. Eli decides after 3A whether to weight the regimes. These are scenarios, not probabilities. '
            'Pipeline equivalent: REGIME_WEIGHT_POST = None in 03_Data/pipelines/forecast_3b/code/forecast.py.')
    put(ws, hr, 5, 'Blank = no weighting (default). Nothing on this workbook uses it yet.')
    KEY['hook'] = f'Scenario_grid!D{hr}'
    # bar chart of 2027 Q4/Q4
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, '2027 core PCE (Q4/Q4) by scenario: baseline and 3 oil paths x 2 regimes', '% Q4/Q4', 'Scenario',
                f'Source: SPF {SPF} median; EIA; FEDS Note Fig. 2; UMD calculations. Scenarios, not probabilities.', w=22, h=11, yfmt='0.0')
    bc.add_data(Reference(ws, min_col=7, min_row=6, max_row=sr + 6), titles_from_data=True)
    bc.set_categories(Reference(ws, min_col=1, min_row=sr, max_row=sr + 6))
    bc.series[0].graphicalProperties.solidFill = 'C00000'
    bc.series[0].graphicalProperties.line.solidFill = 'C00000'
    bc.y_axis.scaling.min = 0
    bc.legend = None
    add_chart(ws, bc, 'M5')
    return CELLS, SUMROW, res, bq


def build_fan(ws, BROW, base, CELLS):
    header(ws, 'Fan_chart: scenario range (min/max of the 6 cells) around the SPF baseline',
           'Question: how wide is the range of scenario outcomes each quarter, and how does it compare with forecasters\' own disagreement?',
           'Core PCE, q/q annualized %. SCENARIO RANGE across the 6 cells, NOT a probability fan. SPF P25/P75 = interquartile range of forecasters (published horizons only).')
    hdr_row(ws, 5, 1, ['Quarter', 'Baseline (SPF)', 'Scenario min', 'Scenario max', 'SPF P25', 'SPF P75'], [10, 14, 12, 12, 10, 10])
    FR = {}
    for i, q in enumerate(QS):
        r = 6 + i
        FR[q] = r
        put(ws, r, 1, q)
        put(ws, r, 2, f'=Baseline!G{BROW[q]}', F2, expect=base[q])
        if q in GQ:
            refs = ','.join(f'Scenario_grid!J{rows[q][0]}' for rows in CELLS.values())
            vals = [rows[q][1] for rows in CELLS.values()]
            put(ws, r, 3, f'=MIN({refs})', F2, expect=min(vals))
            put(ws, r, 4, f'=MAX({refs})', F2, expect=max(vals))
            fr = [x for x in FAN if x['quarter'] == q and x['horizon'] == 'qq_ann'][0]
            SEMANTIC.append((ws.title, f'C{r}', float(fr['scenario_range_min']), f'fan min {q}'))
            SEMANTIC.append((ws.title, f'D{r}', float(fr['scenario_range_max']), f'fan max {q}'))
        else:
            put(ws, r, 3, f'=B{r}', F2, expect=base[q])
            put(ws, r, 4, f'=B{r}', F2, expect=base[q])
        if EXPECT.get(('Baseline', f'E{BROW[q]}')) is not None and P.qidx(q) > P.qidx(LAST_ACT):
            put(ws, r, 5, f'=Baseline!E{BROW[q]}', F2, expect=EXPECT[('Baseline', f'E{BROW[q]}')])
            put(ws, r, 6, f'=Baseline!F{BROW[q]}', F2, expect=EXPECT[('Baseline', f'F{BROW[q]}')])
    put(ws, 16, 1, 'Reading note: the quarterly range is lumpy because the note\'s post-pandemic response dips at k=1 and jumps at k=4; Q4/Q4 (Scenario_grid) is the steadier read.')
    KEY['fan'] = 'Fan_chart!C13:D13 (2027Q4 range)'
    ch = LineChart()
    style_chart(ch, 'Core PCE scenario range vs SPF baseline and forecaster IQR', '% q/q annualized', 'Quarter',
                f'Source: SPF {SPF}; UMD scenario grid. Range = min/max of 6 scenarios, NOT a probability fan.', w=22, h=11, yfmt='0.0')
    for col, color, dash in ((2, '000000', None), (3, '548235', 'dash'), (4, 'C00000', 'dash'), (5, 'A6A6A6', 'sysDot'), (6, 'A6A6A6', 'sysDot')):
        s = Series(Reference(ws, min_col=col, min_row=6, max_row=6 + len(QS) - 1), title=ws.cell(row=5, column=col).value)
        line_style(s, color, dash=dash, width_pt=2.0 if col == 2 else 1.5)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=6 + len(QS) - 1))
    add_chart(ws, ch, 'H5')


def build_sep(ws, SEPROW, SPFROW, SUMROW, q4base):
    header(ws, 'SEP_compare: FOMC September SEP vs SPF vs our scenario range (Q4/Q4)',
           'Question: how do the Fed\'s own September projections compare with the outside baseline and our scenarios? (spoken line / backup)',
           'Core PCE, Q4/Q4 %. SEP = Sep 16 2026 median, central tendency and range. SPF = published annual median. Scenario min/max = Scenario_grid.')
    hdr_row(ws, 5, 1, ['Year', 'SEP median', 'SEP central tendency low', 'SEP central tendency high', 'SPF published median', 'Baseline from quarterly path',
                       'Scenario min', 'Scenario max'], [8, 11, 14, 14, 14, 14, 12, 12])
    for i, y in enumerate((2026, 2027, 2028)):
        r = 6 + i
        sr = SEPROW[y]
        put(ws, r, 1, y)
        for c, src in ((2, 'B'), (3, 'C'), (4, 'D')):
            v = [float(x['value'] if src == 'B' else (x['low'] if src == 'C' else x['high'])) for x in SEP
                 if x['variable'] == 'core_pce' and int(x['target_year']) == y and x['vintage'].startswith('20260916')
                 and x['stat'] == ('median' if src == 'B' else 'central_tendency')][0]
            put(ws, r, c, f'=raw_SEP!{src}{sr}', '0.0', expect=v)
        var = {2026: 'COREPCEA', 2027: 'COREPCEB', 2028: 'COREPCEC'}[y]
        put(ws, r, 5, f'=raw_SPF!D{SPFROW["A" + str(y)]}', F2, expect=float(mrow[var]))
        if y in (2026, 2027):
            col = 'F' if y == 2026 else 'G'
            put(ws, r, 6, f'=Scenario_grid!{col}7', F2, expect=q4base[y])
            refs = ','.join(f'Scenario_grid!{col}{rr}' for rr in SUMROW.values())
            vals = [EXPECT[('Scenario_grid', f'{col}{rr}')] for rr in SUMROW.values()]
            put(ws, r, 7, f'=MIN({refs})', F2, expect=min(vals))
            put(ws, r, 8, f'=MAX({refs})', F2, expect=max(vals))
    put(ws, 10, 1, 'Note: the SEP and the SPF were both formed before the Sep 30 BEA revision (2026Q1 4.42 -> 3.94) and before the Sep-Oct oil spike; the SEP is conditioned on each participant\'s own appropriate policy.' if SPF == '2026Q3' else
        f'Note: the SEP (Sep 16) predates the Sep 30 BEA revision (2026Q1 4.42 -> 3.94) and the Sep-Oct oil spike; the SPF {SPF} (deadline {str(deadline)[:10]}) postdates both. The SEP is conditioned on each participant\'s own appropriate policy.')
    KEY['sep'] = 'SEP_compare!B6:E7'
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, 'Core PCE Q4/Q4: SEP median, SPF median, scenario min and max', '% Q4/Q4', 'Year',
                'Source: FOMC SEP Sep 16 2026; Philadelphia Fed SPF; UMD scenario grid', w=20, h=10, yfmt='0.0')
    for col in (2, 5, 7, 8):
        bc.add_data(Reference(ws, min_col=col, min_row=5, max_row=7), titles_from_data=True)
    for s_, color in zip(bc.series, ('1F3864', 'A6A6A6', '548235', 'C00000')):
        s_.graphicalProperties.solidFill = color
        s_.graphicalProperties.line.solidFill = color
    bc.set_categories(Reference(ws, min_col=1, min_row=6, max_row=7))
    bc.y_axis.scaling.min = 0
    add_chart(ws, bc, 'J5')


# ============================================================================ text tabs
def text_rows(ws, rows, widths, start=5):
    hdr_row(ws, start, 1, rows[0], widths)
    for i, row in enumerate(rows[1:]):
        for j, v in enumerate(row):
            c = ws.cell(row=start + 1 + i, column=1 + j, value=v)
            c.alignment = Alignment(wrap_text=True, vertical='top')


SW = [['Item', 'Rating (1-5)', 'Use', 'Reason (agents A-D, coordinator)'],
      ['3x2 scenario grid, Q4/Q4 columns (Scenario_grid)', 5, 'ON the slide', 'The slide\'s core: transparent, every cell traces to sources (Agent C)'],
      ['SPF baseline path, dated (Baseline)', 4, 'ON the slide (as the spine)', 'Published, quarterly, IQR band; must be dated Aug 11, pre-spike (Agent A)'],
      ['Oil-path chart (Oil_paths)', 4, 'ON the slide or backup', 'Dated, sourced paths plus the assumption line; P3 converges to P1 by 2027 (Agent B)'],
      ['Response-function chart (Pass_through)', 4, 'Backup / spoken', 'The note\'s own data; 0.04 vs 0.36 contrast is immediate (Agent B)'],
      ['Axis comparison (Scenario_grid)', 4, 'Spoken line or inset', 'Oil path matters little under pre (0.08), more under post (0.44); regime moves 0.30-0.68 (Agent C)'],
      ['Scenario-range chart (Fan_chart)', 3, 'Backup', 'Quarterly range is lumpy (Fig. 2 shape); label as range, not probability (Agent C)'],
      ['SEP comparison (SEP_compare)', 3, 'Spoken line', 'SEP 3.4 / 2.5 / 2.2 next to SPF 3.29 / 2.40 / 2.16; Q4/Q4 only (Agent A)']]

SW_Q4 = [['Item', 'Rating (1-5)', 'Use', 'Reason (agents A-D; rows marked Q4 rerun = coordinator, Nov 16, PENDING Eli)'],
      ['3x2 scenario grid, Q4/Q4 columns (Scenario_grid)', 5, 'ON the slide', 'The slide\'s core: transparent, every cell traces to sources (Agent C)'],
      ['SPF baseline path, dated (Baseline)', 4, 'ON the slide (as the spine)', 'Q4 rerun: dated Nov 11, after the spike; 2027Q4 now published (no derived quarter). Q3 (Aug 11) path in backup'],
      ['Oil-path chart (Oil_paths)', 4, 'ON the slide or backup', 'Q4 rerun: P1 (Nov STEO) is also the assumption line, so P1\'s gap is ~0 from 2027Q1; P2 sits above it, P3 below'],
      ['Response-function chart (Pass_through)', 4, 'Backup / spoken', 'The note\'s own data; 0.04 vs 0.36 contrast is immediate (Agent B)'],
      ['Axis comparison (Scenario_grid)', 4, 'Spoken line or inset', 'Q4 rerun: oil path moves 2027 Q4/Q4 0.08 (pre) and 0.44 (post); regime moves it 0.01 (P1), 0.15 (P2), 0.23 (P3). In the Q3 run the regime axis was larger (0.30-0.68)'],
      ['Q3 vs Q4 vintage comparison (processed/vintage_compare.csv)', 3, 'Backup / spoken', 'Q4 rerun: SPF 2027 Q4/Q4 median 2.40 -> 2.50; Q3-run P1 post cell was 2.93. Coordinator rating, PENDING Eli'],
      ['Scenario-range chart (Fan_chart)', 3, 'Backup', 'Quarterly range is lumpy (Fig. 2 shape); label as range, not probability (Agent C)'],
      ['SEP comparison (SEP_compare)', 3, 'Spoken line', 'Q4 rerun: SEP 3.4 / 2.5 / 2.2 next to SPF 3.18 / 2.50 / 2.20; Q4/Q4 only']]

SOURCES = [['Source', 'What it supports', 'File / URL', 'Tag'],
           [f'Philadelphia Fed SPF, {SPF} (medianLevel, Dispersion_1)', f'Baseline path, IQR, deadline {str(deadline)[:10]}', 'raw_SPF; https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters', '[O]'],
           ['FRED PCEPILFE (BEA), vintage of the Sep 2026 PCE release', 'Actual core PCE quarters', 'raw_PCE; https://fred.stlouisfed.org/series/PCEPILFE', '[O]'],
           ['EIA Brent spot RBRTE daily', 'Actual Brent; 2026Q4 splice', 'raw_Brent_daily; https://www.eia.gov/dnav/pet/hist/RBRTED.htm', '[O]'],
           [f'EIA STEO {ASSUME_V} / {LATEST_V} / feb26 (2tab BREPUUS)', 'Assumed oil (proxy); Path 1; Path 3 pre-war trend' if ASSUME_V != LATEST_V else 'Assumed oil (proxy) AND Path 1 (same vintage); Path 3 pre-war trend', 'raw_STEO; https://www.eia.gov/outlooks/steo/', '[O]'],
           ['EIA STEO Mar 2026 report p.5', 'War onset Feb 28 2026 ("military action in the Middle East that began on February 28")', '03_Data/Raw/EIA_STEO_Mar2026_report_2026-11-15/mar26.pdf', '[O]'],
           ['De Michelis, Orak, Pradhan & Queralto, FEDS Notes Nov 9 2026 (accessible version, Fig. 2 data)', 'Pass-through regimes (response by quarter)', 'raw_response; https://www.federalreserve.gov/econres/notes/feds-notes/the-effect-of-oil-prices-on-core-inflation-recent-evidence-from-the-advanced-economies-20261109.html', '[O]'],
           ['Bowman, Nov 10 2026, CFR', 'P2: "moved up to and above $110 per barrel in the second half of October"', '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf', '[O]'],
           ['Waller, Nov 10 2026, BoE Watchers', 'P3 premium: "reportedly boosting oil prices by $20 to $30 a barrel" (cost of current passage)', '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Waller_economic_outlook.pdf', '[O]'],
           ['FOMC SEP, Sep 16 2026', 'SEP_compare', 'raw_SEP; https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm', '[O]'],
           ['NYMEX BZ futures closes via Yahoo Finance chart API', 'Sensitivity only (Aug 11 and Nov 13 curves)', '03_Data/Raw/Yahoo_BZ_futures_*_2026-11-15/', '[2]'],
           ['UMD Oct 2026 core PCE estimate', 'Jump-off (3.24% y/y est.)', '01_Finals/data/Slide1_Inflation_Data.xlsx Headline!C10', 'est.']]


def build_needs(ws, items):
    text_rows(ws, items, [6, 34, 58, 58, 34])


def build_reading_guide(ws, names):
    header(ws, 'READING GUIDE: Slide 3B data workbook ("Forecast and scenarios")',
           'Start here. For each tab: the question it answers, every column in plain language, how to read the chart, and the 2-3 numbers to know (with cells).',
           f'Built {BUILD_DATE} by {SCRIPT}. Baseline: SPF {SPF} (deadline {str(deadline)[:10]}). Oil to {brent.index[-1].date()}. Scenarios, NOT probabilities.')
    G = [
        ('THE ONE-PARAGRAPH VERSION', None, None, None),
        ('', f'We take the professional forecasters\' core PCE path (SPF {SPF}, survey deadline {str(deadline)[:10]}), measure how far each oil scenario sits above the oil price they likely assumed, '
             f'and push that gap through the Fed staff note\'s estimate of how oil moves core prices. Two pass-through regimes (pre- vs post-pandemic) x three oil paths = six scenarios. '
             + ('The regime axis moves 2027 more than the oil axis does. ' if SPF == '2026Q3' else
                'Here the baseline oil path (P1) is also the forecasters\' likely assumption, so P1 barely moves; under post-pandemic dynamics the oil path moves 2027 more than the regime does. ')
             + f'Key cells: {KEY["grid"]} (the grid), {KEY["axis"]} (which axis matters).', None, None),
        ('Baseline', 'What does the outside forecast say before any oil adjustment, and how does it compare with the data since?',
         'Quarter; Actual index (qtr avg) = average of the 3 monthly core PCE index values; Actual q/q ann. = quarter-over-quarter change, annualized (x4 compounding) - the "pace" in that quarter; '
         'SPF median q/q ann. = middle forecast of ~30 professional forecasters; SPF P25/P75 = 25th and 75th percentile forecasters (their disagreement); Baseline used = actual where we have data, SPF after; '
         + ('yellow = 2027Q4 is DERIVED (the SPF does not publish it). ' if '2027Q4' not in SPFROW_G else '2027Q4 is published in this survey. ') + 'Lower block: Q4/Q4 = growth from Q4 of one year to Q4 of the next (the SEP\'s horizon). Jump-off block: our October estimate vs the baseline.',
         f'Line chart: red = baseline used; dashed navy = SPF median as published; grey dots = forecasters\' P25/P75. Key: {KEY["base_2026q4"]} 2026Q4 baseline; {KEY["base_q4q4_2027"]} 2027 Q4/Q4 baseline; '
         + f'{KEY["jump_mm"]}: Nov-Dec core m/m needed for the baseline 2026Q4, vs our Oct 0.295 ({KEY["jump_oct"]}).'),
        ('Oil_paths', 'How far is each oil scenario from the oil price the SPF forecasters likely assumed?',
         'Splice parameters: the current quarter mixes observed days with each path\'s assumption for the rest. Actual Brent = quarterly average of daily spot; Assumed by baseline = EIA STEO forecast issued on the SPF deadline (a PROXY: '
         'forecasters don\'t publish an oil assumption); P1/P2/P3 = the three paths; Gap = 100 x ln(path/assumed), in log points (about %). A "futures curve" = market prices today for oil delivered on future dates (here only a sensitivity; exchange data is paywalled).',
         f'Line chart: black dashed = assumed; navy P1, red P2, green P3. Key: {KEY["oil_gap_2027"]} 2027Q4 gaps; {KEY["oil_assumed_2027"]} assumed ${KEY["oil_assumed_val"]:.0f} by 2027Q4.'),
        ('Pass_through', 'How much does a permanent 10% oil rise move the core price LEVEL, quarter by quarter, in each regime?',
         'k = quarters after the rise; columns = the note\'s three lines. "Pass-through regime" = which set of estimated dynamics we use: pre-pandemic (2000-2020 behaviour) or post-pandemic (stronger persistence and pass-through since 2021). '
         '"Persistence" = how much this quarter\'s core inflation carries into the next. Five-economy average, not US-only; the authors call the projection an upper bound.',
         f'Line chart: red = post, navy = pre, grey dashed = persistence only (backup). Key: {KEY["pt_k12"]}: 0.044% vs 0.360% after 12 quarters (about 8x).'),
        ('Scenario_grid', 'Where does core PCE end up in 2026 and 2027 under each oil path x regime?',
         'Summary (top): one row per scenario; 2026Q4/2027Q4 q/q ann.; 2026/2027 Q4/Q4; vs baseline. Spread = max - min. Axis comparison: range across oil paths (regime fixed) vs regime difference (path fixed). '
         'Hook cell: blank on purpose (Eli\'s regime weighting after slide 3A). Detail (row 30+): baseline, gap, change in gap, level effect L (cumulative % effect on the core price level), adjustment, scenario. Every number is a live formula.',
         f'Bar chart: 2027 Q4/Q4 for baseline and the six cells. Key: {KEY["grid"]}; {KEY["grid_spread"]} spread; {KEY["axis"]}; hook {KEY["hook"]}.'),
        ('Fan_chart', 'How wide is the range of scenario outcomes each quarter?',
         'Baseline; Scenario min/max = lowest/highest of the 6 cells (a RANGE of scenarios, not a probability fan); SPF P25/P75 = forecasters\' disagreement for comparison.',
         f'Line chart: black = baseline; green/red dashed = scenario min/max; grey dots = SPF IQR. Lumpy quarters come from the note\'s response shape. Key: {KEY["fan"]}.'),
        ('SEP_compare', 'How do the Fed\'s September projections compare with the SPF and our scenarios?',
         'SEP = FOMC Summary of Economic Projections (each participant\'s forecast under their own appropriate policy): median and central tendency (drops the 3 highest and 3 lowest). SPF median; our baseline and scenario min/max (Q4/Q4).',
         f'Bar chart by year. Key: {KEY["sep"]}: SEP 3.4 / 2.5 vs SPF {SPFQ4Q4[2026]:.2f} / {SPFQ4Q4[2027]:.2f} for 2026 / 2027.'),
        ('Slide_worthiness', 'What should go on the slide vs spoken vs backup?', 'Item, rating 1-5, use, reason.', 'No chart.'),
        ('Sources', 'Where each input comes from.', 'Source, what it supports, file/URL, tag ([O] opened primary, [2] secondary, est. our estimate).', 'No chart.'),
        ('Judgment_calls_and_paywalled', 'Decisions that are Eli\'s, ordered by how much they block the slide, and sources we could not access.', 'Item, decision, position A, position B, default used.', 'No chart.'),
        ('raw_ tabs (grey)', 'The source data behind every formula.', 'Rows 1-5 give source, file path, vintage and notes; data from row 7.', 'No charts.'),
        ('GLOSSARY', None, None, None),
        ('q/q annualized', 'Change from one quarter to the next, scaled up to an annual rate ((1+q)^4 - 1).', None, None),
        ('Q4/Q4', 'Change from the 4th quarter of one year to the 4th quarter of the next (averages over the year; the SEP\'s horizon).', None, None),
        ('y/y', 'Change from the same month a year earlier (our 3.24% October estimate).', None, None),
        ('SPF', 'Philadelphia Fed Survey of Professional Forecasters: ~30 private forecasters, quarterly.', None, None),
        ('Pass-through regime', 'Which estimated dynamics turn oil moves into core inflation: pre-pandemic (weak) or post-pandemic (stronger).', None, None),
        ('Oil gap', 'How far a scenario\'s oil price sits above the price the baseline assumed, in log points (~%).', None, None),
        ('Futures curve', 'Today\'s market prices for oil delivered on future dates; a market-based forecast.', None, None),
        ('STEO', 'EIA Short-Term Energy Outlook: the government energy agency\'s monthly forecast.', None, None),
        ('Level effect L', 'The cumulative % by which oil pushes the core price level above the baseline path.', None, None),
        ('Scenario vs probability', 'A scenario says "if oil does X and pass-through is Y, core is Z". It does not say how likely X or Y is.', None, None),
        ('SEP central tendency', 'The range of FOMC projections after dropping the 3 highest and 3 lowest.', None, None),
        ('est.', 'Our estimate (yellow fill), not an official number.', None, None),
    ]
    hdr_row(ws, 5, 1, ['Tab / term', 'Question it answers / meaning', 'Columns, in plain language', 'How to read the chart; key numbers (cells)'], [22, 48, 90, 80])
    for i, row in enumerate(G):
        r = 6 + i
        for j, v in enumerate(row):
            if v is None:
                continue
            c = ws.cell(row=r, column=1 + j, value=v)
            c.alignment = Alignment(wrap_text=True, vertical='top')
            if j == 0:
                c.font = F_BOLD
        if row[0] in names:
            ws.cell(row=r, column=1).hyperlink = f"#'{row[0]}'!A1"
            ws.cell(row=r, column=1).font = Font(bold=True, color='0563C1', underline='single')


def build_readme(ws, research, raws):
    header(ws, 'Slide 3B data workbook: "Forecast and scenarios"',
           'Core PCE through 2027Q4: SPF baseline adjusted for oil gaps through the FEDS oil note\'s dynamics, 3 oil paths x 2 pass-through regimes. Scenarios, not probabilities.',
           f'Built {BUILD_DATE} by {SCRIPT}. SPF {SPF} (deadline {str(deadline)[:10]}); PCE through Sep 2026; Brent to {brent.index[-1].date()}; STEO {LATEST_V}. Data cutoff Nov 18 2026.')
    lines = [
        ('How to rebuild', f'From the project root: python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf {SPF}  then  python3 -I "02_Research/Subtasks/{SCRIPT}" --verify'),
        ('Q4 SPF (one rerun)', 'fetch_inputs.py -> forecast.py --spf 2026Q4 -> this builder with --spf=2026Q4 --verify (see 03_Data/pipelines/forecast_3b/README.md)'),
        ('Inputs', f'Pipeline raw folder {REL(RAW)}; config/regime_response.csv; agent outputs A_q1_sep.csv, A_q1_jumpoff.csv'),
        ('Checks', 'Live formulas recomputed by LibreOffice (0 mismatches required); semantic check vs processed/scenario_grid CSV; chart XML smooth/invertIfNegative flags.'),
        ('Caveats', 'Oil note = five-economy panel average and an upper bound; baseline oil assumption is a proxy (STEO on the SPF deadline); scenarios not probabilities; never describe the note as evidence of changed price-setting behaviour.'),
        ('Vintage note', f'Text tabs describe this ({SPF} SPF) run.' + ('' if SPF == '2026Q3' else ' Q3 2026 SPF version: 02_Research/Subtasks/12_slide3b_research/outputs/Slide3B_Inflation_Data_Q3SPF_2026-11-15.xlsx, or rebuild with --spf=2026Q3.')),
        ('Audit trail', '02_Research/Subtasks/12_slide3b_research/FINAL.md, report_A..D.md, 06_Audits/slide3b_research/'),
    ]
    for i, (k, v) in enumerate(lines):
        ws.cell(row=5 + i, column=1, value=k).font = F_BOLD
        ws.cell(row=5 + i, column=2, value=v)
    r = 13
    section(ws, r, 'Contents (click to jump)')
    for i, n in enumerate(research + raws):
        c = ws.cell(row=r + 1 + i, column=1, value=n)
        c.hyperlink = f"#'{n}'!A1"
        c.font = Font(color='0563C1', underline='single')
    ws.column_dimensions['A'].width = 26
    ws.column_dimensions['B'].width = 150


NEEDS = [['#', 'Item (ordered by how much it blocks the slide)', 'Position A', 'Position B', 'Default used here'],
         [1, 'Regime weighting (waits on slide 3A)', 'Weight toward post-pandemic if 3A finds second-round channels live (labour tightness, expectations, catch-up)',
          'Keep both regimes unweighted as bookends; let judges see the range', 'No weighting (hook blank)'],
         [2, 'Baseline staleness: SPF 2026Q4 2.62 needs Nov-Dec core m/m ~0.05% vs our Oct 0.295', 'Keep pure SPF + oil adjustment (locked method); disclose the jump-off gap in a spoken line',
          'Re-anchor 2026Q4 on the Oct estimate (risks double-counting October\'s oil pass-through; outside the locked method)', 'Pure SPF; jump-off shown on Baseline'],
         [3, 'Oil-assumption proxy', 'Aug STEO (dated to the SPF deadline; public)', 'Aug 11 futures (market; secondary source) or Jul STEO; moves P1 x post 2027 Q4/Q4 by ~0.33 pp', 'Aug STEO; others as sensitivity'],
         [4, 'Hormuz premium: Waller\'s $20-30 is the cost of CURRENT passage, not a post-reopening residual', 'Keep +$25 central (locked); say "premium persists at Waller\'s estimate"', 'Make +$0 central or show it alongside (only disinflationary cell)', '+$25 central; +$0/+$20/+$30 sensitivity'],
         [5, 'Lead metric', 'Q4/Q4 (steady; matches SEP)', 'Quarterly annualized (shows timing but lumpy from the note\'s response shape)', 'Q4/Q4 leads'],
         [6, 'Q4 SPF (Nov 16): rerun and show both', 'Show Q4 as baseline, Q3 in backup', 'Show both side by side', 'Not yet released at build time'],
         [7, 'Wording of the pre-pandemic regime number', 'Quote the figure data (0.044% after 12 q)', 'Quote the text ("0.05 percent")', 'Figure data in the workbook'],
         ['', 'PAYWALLED / UNAVAILABLE (logged, not used)', '', '', ''],
         ['', 'ICE Brent futures (licensed); CME settlements (HTTP 403); Bloomberg (terminal)', 'https://www.ice.com/products/219/Brent-Crude-Futures/data', 'https://www.cmegroup.com/markets/energy/crude-oil/brent-crude-oil.settlements.html', 'Yahoo BZ closes [2] used as sensitivity only'],
         ['', 'EIA NYMEX futures RCLC1-4 discontinued after 2024-04-05', 'https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm', '', ''],
         ['', 'SPF Q4 2026 page (404 at build time)', 'https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026', '', '']]


NEEDS_Q4 = [['#', 'Item (ordered by how much it blocks the slide; Q4 rerun Nov 16)', 'Position A', 'Position B', 'Default used here'],
         [1, 'Regime weighting (waits on slide 3A). Q4 rerun: matters little for P1 (0.01 pp), 0.15 (P2) and 0.23 (P3) for 2027 Q4/Q4', 'Weight toward post-pandemic if 3A finds second-round channels live (labour tightness, expectations, catch-up)',
          'Keep both regimes unweighted as bookends; let judges see the range', 'No weighting (hook blank)'],
         [2, 'P1 is near-baseline by construction: the Q4 SPF\'s proxy assumption and P1 are both the Nov STEO', 'Keep P1 = latest STEO (locked rule); say "the central oil path is the one forecasters already saw"',
          'Add or substitute a path that is not the proxy (e.g. Brent flat at the latest spot) so the central row is not tautological (outside the locked method)', 'P1 = Nov STEO (locked)'],
         [3, 'Baseline staleness: SPF 2026Q4 3.00 needs Nov-Dec core m/m ~0.15% vs our Oct 0.295', 'Keep pure SPF + oil adjustment (locked method); disclose the jump-off gap in a spoken line',
          'Re-anchor 2026Q4 on the Oct estimate (risks double-counting October\'s oil pass-through; outside the locked method)', 'Pure SPF; jump-off shown on Baseline'],
         [4, 'Oil-assumption proxy', 'Nov STEO (released Nov 10, the latest before the Nov 11 deadline; public)', 'Oct STEO (one vintage earlier) moves P1 x post 2027 Q4/Q4 by +0.05 pp; no futures proxy saved for Nov 11', 'Nov STEO; Oct STEO as sensitivity'],
         [5, 'Hormuz premium: Waller\'s $20-30 is the cost of CURRENT passage, not a post-reopening residual', 'Keep +$25 central (locked); say "premium persists at Waller\'s estimate"', 'Make +$0 central or show it alongside (post 2027 Q4/Q4 1.84)', '+$25 central; +$0/+$20/+$30 sensitivity'],
         [6, 'Lead metric', 'Q4/Q4 (steady; matches SEP)', 'Quarterly annualized (shows timing but lumpy from the note\'s response shape)', 'Q4/Q4 leads'],
         [7, 'Q4 vs Q3 SPF on the slide', 'Show Q4 as baseline, Q3 in backup', 'Show both side by side', 'Workbook on Q4; Q3 workbook copy in 12_slide3b_research/outputs/'],
         [8, 'Wording of the pre-pandemic regime number', 'Quote the figure data (0.044% after 12 q)', 'Quote the text ("0.05 percent")', 'Figure data in the workbook'],
         ['', 'PAYWALLED / UNAVAILABLE (logged, not used)', '', '', ''],
         ['', 'ICE Brent futures (licensed); CME settlements (HTTP 403); Bloomberg (terminal)', 'https://www.ice.com/products/219/Brent-Crude-Futures/data', 'https://www.cmegroup.com/markets/energy/crude-oil/brent-crude-oil.settlements.html', 'Yahoo BZ closes [2] used as sensitivity only'],
         ['', 'EIA NYMEX futures RCLC1-4 discontinued after 2024-04-05', 'https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm', '', '']]


# ============================================================================ main / verify
def main(verify=False):
    wb = Workbook()
    wb.remove(wb.active)
    research = ['READING_GUIDE', 'README', 'Baseline', 'Oil_paths', 'Pass_through', 'Scenario_grid', 'Fan_chart', 'SEP_compare',
                'Slide_worthiness', 'Sources', 'Judgment_calls_and_paywalled']
    raws = ['raw_SPF', 'raw_PCE', 'raw_Brent_daily', 'raw_STEO', 'raw_response', 'raw_SEP']
    S = {n: wb.create_sheet(n) for n in research + raws}
    PCEROW, _ = build_raw_pce(S['raw_PCE'])
    BR0, BR1 = build_raw_brent(S['raw_Brent_daily'])
    STROW, STCOL, _ = build_raw_steo(S['raw_STEO'])
    SPFROW = build_raw_spf(S['raw_SPF'])
    build_raw_response(S['raw_response'])
    SEPROW = build_raw_sep(S['raw_SEP'])
    BROW, base, q4b = build_baseline(S['Baseline'], PCEROW, SPFROW)
    GAP, _ = build_oil(S['Oil_paths'], STROW, STCOL, BR0, BR1)
    build_pass(S['Pass_through'])
    CELLS, SUMROW, res, bq = build_grid(S['Scenario_grid'], BROW, base, GAP)
    build_fan(S['Fan_chart'], BROW, base, CELLS)
    build_sep(S['SEP_compare'], SEPROW, SPFROW, SUMROW, bq)
    header(S['Slide_worthiness'], 'Slide_worthiness', 'What goes on the slide, what is spoken, what is backup', 'Ratings from agents A-C reports; coordinator-reviewed' + ('' if SPF == '2026Q3' else f'; text updated for SPF {SPF}'))
    text_rows(S['Slide_worthiness'], SW if SPF == '2026Q3' else SW_Q4, [44, 12, 24, 90])
    header(S['Sources'], 'Sources', 'Every input, with tag', '[O] opened primary; [2] secondary; est. = our estimate')
    text_rows(S['Sources'], SOURCES, [52, 56, 90, 8])
    header(S['Judgment_calls_and_paywalled'], 'Judgment calls for Eli (ordered by how much each blocks the slide) and paywalled sources', 'Both positions given; default = what this workbook uses', 'See FINAL.md section 7')
    build_needs(S['Judgment_calls_and_paywalled'], NEEDS if SPF == '2026Q3' else NEEDS_Q4)
    build_reading_guide(S['READING_GUIDE'], research + raws)
    build_readme(S['README'], research, raws)
    semantic_check()
    os.makedirs(os.path.dirname(XLSX), exist_ok=True)
    wb.save(XLSX)
    print(f'saved {REL(XLSX)}: {len(EXPECT)} formula cells, {len(SEMANTIC)} semantic checks passed')
    chart_xml_check()
    if verify:
        run_verify()


def semantic_check():
    bad = [(sh, c, lbl, EXPECT[(sh, c)], w) for sh, c, w, lbl in SEMANTIC if abs(EXPECT[(sh, c)] - w) > 1e-5]
    for b in bad:
        print('SEMANTIC MISMATCH', b)
    assert not bad, f'{len(bad)} semantic mismatches'


def chart_xml_check():
    import zipfile
    z = zipfile.ZipFile(XLSX)
    n_line = n_bar = 0
    for f in z.namelist():
        if f.startswith('xl/charts/chart'):
            x = re.sub(r'\s+/>', '/>', re.sub(r'<(/?)c:', r'<\1', z.read(f).decode()))   # R2-F02: serializer-independent
            ns = x.count('<ser>')
            assert ns > 0, f'{f}: no series'
            if '<lineChart>' in x:
                assert x.count('<smooth val="0"/>') >= ns, f'{f}: missing smooth=0'
                n_line += 1
            if '<barChart>' in x:
                assert x.count('<invertIfNegative val="0"/>') >= ns, f'{f}: missing invertIfNegative=0'
                n_bar += 1
    assert n_line + n_bar == 6, f'expected 6 charts, found {n_line + n_bar}'
    print(f'chart XML check: {n_line} line charts with smooth val="0", {n_bar} bar charts with invertIfNegative val="0"')


def run_verify():
    scratch = os.environ.get('SLIDE3B_SCRATCH', '/tmp')
    os.makedirs(scratch, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', scratch, XLSX], check=True, capture_output=True, timeout=600)
    rec = os.path.join(scratch, os.path.basename(XLSX))
    wb = load_workbook(rec, data_only=True)
    bad, errs = [], []
    for (sh, coord), exp in EXPECT.items():
        v = wb[sh][coord].value
        if isinstance(v, str) and v.startswith('#'):
            errs.append((sh, coord, v))
            continue
        if not isinstance(v, (int, float)) or abs(v - exp) > 1e-6 * max(1, abs(exp)):
            bad.append((sh, coord, exp, v))
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('#') and c.value[1:4] in ('REF', 'DIV', 'VAL', 'N/A', 'NAM', 'NUM', 'NUL'):
                    errs.append((ws.title, c.coordinate, c.value))
    rep = os.path.join(SUB, 'code', 'build_verify_report.txt')
    with open(rep, 'w') as f:
        f.write(f'LibreOffice recalculation check, {dt.datetime.now().isoformat(timespec="seconds")}\n')
        f.write(f'formula cells checked: {len(EXPECT)}; mismatches: {len(bad)}; error values: {len(errs)}; semantic checks vs pipeline CSV: {len(SEMANTIC)} passed\n')
        for b in bad[:200]:
            f.write(f'MISMATCH {b}\n')
        for e in errs[:200]:
            f.write(f'ERROR {e}\n')
    print(open(rep).read()[:3000])
    if bad or errs:
        sys.exit(1)


if __name__ == '__main__':
    main(verify='--verify' in sys.argv)
