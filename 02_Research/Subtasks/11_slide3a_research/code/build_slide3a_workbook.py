"""Build 01_Finals/data/Slide3A_Inflation_Data.xlsx from the slide3a_research outputs and their raw files.

Run from the project root:
    python3 -I "02_Research/Subtasks/11_slide3a_research/code/build_slide3a_workbook.py"            # build
    python3 -I "02_Research/Subtasks/11_slide3a_research/code/build_slide3a_workbook.py" --verify   # build + LibreOffice recalc check

Design (GO.md): same two-layer design as slides 1 and 2. READING_GUIDE first, README, research tabs, then Slide_worthiness,
Sources, Judgment_calls_and_paywalled, then grey raw_ tabs. Research tabs use live formulas back to the raw tabs; rates are
computed in-sheet from index levels where the levels are on a raw tab (V/U, AHE, ECI, ULC, productivity, hourly comp,
PCE 12m and the time-above-target run). Published or agent-derived rates (surveys, MCT, Dallas, Cleveland, supercore,
Logan measure) are copied onto raw tabs from the agents' CSVs and referenced. Every formula cell has an expected value
computed here (EXPECT) and checked after a LibreOffice recalculation (--verify). semantic_check() compares live values
with the agents' summary CSVs. Chart and verify helpers are reused from the slide 1 builder. Fix inputs, then rebuild.
"""
import csv
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '11_slide3a_research')
OUT = os.path.join(SUB, 'outputs')
S1CODE = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code')
XLSX = os.environ.get('SLIDE3A_OUT') or os.path.join(ROOT, '01_Finals', 'data', 'Slide3A_Inflation_Data.xlsx')
SCRIPT = '11_slide3a_research/code/build_slide3a_workbook.py'
BUILD_DATE = dt.date.today().isoformat()
REL = lambda p: os.path.relpath(p, ROOT)
RAWB = os.path.join(ROOT, '03_Data', 'Raw', 'S3A_B_labor_costs_2026-11-15')
RAWC = os.path.join(ROOT, '03_Data', 'Raw', 'S3A_expectations_underlying_2026-11-15')
RAWA = os.path.join(ROOT, '03_Data', 'Raw', 'S3A_A_vu_2026-11-15')
PIPE_BLS = os.path.join(ROOT, '03_Data', 'pipelines', 'inflation_data', 'processed', 'bls', 'observations.csv')
OCT_SUM = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'D_build_2026-10_summary.csv')

sys.path.insert(0, S1CODE)
import build_slide1_workbook as b1          # noqa: E402  (helpers only; b1.main() is never called)
from openpyxl import Workbook, load_workbook   # noqa: E402
from openpyxl.chart import BarChart, LineChart, Reference, Series   # noqa: E402
from openpyxl.comments import Comment      # noqa: E402
from openpyxl.styles import Alignment, Font   # noqa: E402
from openpyxl.utils import get_column_letter as CL   # noqa: E402

put, hdr_row, section, header, raw_meta = b1.put, b1.hdr_row, b1.section, b1.header, b1.raw_meta
style_chart, line_style, add_chart = b1.style_chart, b1.line_style, b1.add_chart
FILL_EST, FILL_KEY, F_BOLD = b1.FILL_EST, b1.FILL_KEY, b1.F_BOLD
EXPECT = b1.EXPECT
num = b1.num
F2, F1, F3 = '0.00', '0.0', '0.000'
b1.TAB_COLORS.update({'READING_GUIDE': '000000', 'README': '1F3864', 'BB_channels': 'C00000', 'Wages_ULC': 'BF8F00', 'Catch_up': 'BF8F00',
                      'Expectations': '2F5597', 'Underlying_trend': '7030A0', 'Time_above_target': '548235', 'Slide_worthiness': '548235',
                      'Sources': '1F3864', 'Judgment_calls_and_paywalled': 'FF0000'})
CONST = {}           # (sheet, coord) -> value of constant cells linked from other tabs
SEMANTIC = []        # (sheet, coord, expected_from_csv, tol, label)
KEYCELLS = {}        # name -> 'Sheet!A1' (used by READING_GUIDE and BB_channels)
WRAP = Alignment(wrap_text=True, vertical='top')
BLUE, RED, GREEN, ORANGE, PURPLE, GREY, TEAL, BLACK = '2F5597', 'C00000', '548235', 'ED7D31', '7030A0', '7F7F7F', '00B0F0', '1F1F1F'


def note(cell, text):
    cell.comment = Comment(text, 'build_slide3a_workbook.py', width=340, height=120)


def rd(name):
    p = name if os.path.isabs(name) else os.path.join(OUT, name)
    with open(p, newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def months(a, b):
    y, m = int(a[:4]), int(a[5:])
    out = []
    while f'{y}-{m:02d}' <= b:
        out.append(f'{y}-{m:02d}')
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def quarters(a, b):
    y, q = int(a[:4]), int(a[-1])
    out = []
    while f'{y}Q{q}' <= b:
        out.append(f'{y}Q{q}')
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def shift(m, k):
    y, mm = int(m[:4]), int(m[5:7])
    t = y * 12 + mm - 1 - k
    return f'{t // 12}-{t % 12 + 1:02d}'


def qshift(q, k):
    y, n = int(q[:4]), int(q[-1])
    t = y * 4 + n - 1 - k
    return f'{t // 4}Q{t % 4 + 1}'


def in_1819(p):
    return p[:4] in ('2018', '2019')


def in_2123(p):
    return p[:4] in ('2021', '2022', '2023')


def text_cell(ws, r, c, v, width=None, bold=False):
    cell = put(ws, r, c, v, bold=bold)
    cell.alignment = WRAP
    if width:
        ws.column_dimensions[CL(c)].width = width
    return cell


# ============================================================================ data loading
def load_monthly():
    """dict key -> {month: value}; plus status dict for est./prelim."""
    S, ST, SRC = {}, {}, {}

    def add(key, m, v, status='', src=''):
        if v is None:
            return
        S.setdefault(key, {})[m] = v
        if status:
            ST[(key, m)] = status
        if src:
            SRC.setdefault(key, src)
    for r in rd('A_q1_vu.csv'):
        add('openings', r['month'], num(r['openings_thous_JTSJOL']), src='outputs/A_q1_vu.csv <- 03_Data/Raw/S3A_A_vu_2026-11-15/FRED_JTSJOL_observations_2026-11-15.json')
        add('unemployed', r['month'], num(r['unemployed_thous_UNEMPLOY']), src='outputs/A_q1_vu.csv <- FRED_UNEMPLOY_observations_2026-11-15.json')
        add('unrate', r['month'], num(r['unrate_pct_UNRATE']), src='outputs/A_q1_vu.csv <- FRED_UNRATE_observations_2026-11-15.json')
    ahe = json.load(open(os.path.join(RAWB, 'bls_api_ces_ahe_2016-2026_2026-11-15.json')))
    for s in ahe['Results']['series']:
        k = {'CES0500000003': 'ahe', 'CES0500000008': 'ahe_pns'}.get(s['seriesID'])
        if not k:
            continue
        for x in s['data']:
            if x['period'].startswith('M') and x['period'] != 'M13':
                m = f"{x['year']}-{x['period'][1:]}"
                add(k, m, num(x['value']), status='prelim' if m == '2026-10' else '', src=f'{REL(RAWB)}/bls_api_ces_ahe_2016-2026_2026-11-15.json ({s["seriesID"]}, SA)')
    for r in rd('B_q3_wages_ulc.csv'):
        k = {'WGT_overall_3mma': 'wgt', 'WGT_stayer_3mma': 'wgt_stay', 'WGT_switcher_3mma': 'wgt_switch'}.get(r['series_id'])
        if k:
            add(k, r['period'], num(r['value_level']), src='outputs/B_q3_wages_ulc.csv <- ' + r['source_file'])
    for r in rd('C_q4_expectations.csv'):
        sid, hz = r['series_id'], r['horizon']
        k = None
        if sid == 'PX_MD':
            k = 'mich1'
        elif sid == 'PX5_MD':
            k = 'mich510'
        elif sid.startswith('Median one-year'):
            k = 'sce1'
        elif sid.startswith('Median three-year'):
            k = 'sce3'
        elif sid in ('T5YIE', 'T10YIE', 'T5YIFR') and 'monthly average' in hz:
            k = {'T5YIE': 'be5', 'T10YIE': 'be10', 'T5YIFR': 'fwd55'}[sid]
        elif sid == 'GASREGW' and 'monthly average' in hz:
            k = 'gas'
        if k:
            st = 'prelim' if 'PRELIM' in r['status'].upper() else ('partial month' if k in ('gas', 'be5', 'be10', 'fwd55') and r['period'] == '2026-11' else '')
            add(k, r['period'], num(r['value']), status=st, src='outputs/C_q4_expectations.csv <- ' + r['source_file'])
    U = {('NY Fed MCT (central estimate)', 'annualized trend estimate'): 'mct', ('NY Fed MCT lower 68% band', '%'): 'mct_lo', ('NY Fed MCT upper 68% band', '%'): 'mct_hi',
         ('Dallas Fed trimmed-mean PCE, 12m (y/y)', '12m (y/y)'): 'dal12', ('Dallas Fed trimmed-mean PCE, 6m annualized', '6m annualized'): 'dal6',
         ('Cleveland Fed median PCE, 12m % change (published)', '12m (% y/y)'): 'medpce',
         ('Market-based core PCE (BEA)', '12m (% y/y)'): 'mbcore',
         ('Supercore: PCE services ex energy and housing (BEA published through Sep; Oct est.)', '12m (% y/y)'): 'super12',
         ('Supercore: PCE services ex energy and housing (BEA published through Sep; Oct est.)', '3m ann (annualized %)'): 'super3',
         ('Logan measure: PCE services ex energy, housing and transportation (derived; Oct est.)', '12m (% y/y)'): 'logan12',
         ('Logan measure: PCE services ex energy, housing and transportation (derived; Oct est.)', '3m ann (annualized %)'): 'logan3',
         ('Cleveland Fed median CPI, 12m', '12m (% y/y)'): 'medcpi', ('Cleveland Fed 16% trimmed-mean CPI, 12m', '12m (% y/y)'): 'trimcpi'}
    for r in rd('C_q6_underlying.csv'):
        k = U.get((r['series'], r['horizon']))
        if k:
            add(k, r['period'], num(r['value']), status='est.' if r['status'].startswith('est') else '', src='outputs/C_q6_underlying.csv <- ' + r['source_file'])
    N = {'NFIB net % raised compensation, last 3 months': 'nfib_comp', 'NFIB net % planning to raise compensation, next 3 months': 'nfib_comp_plan',
         'NFIB net % raised average selling prices, last 3 months': 'nfib_px', 'NFIB net % planning to raise prices, next 3 months': 'nfib_px_plan',
         'BIE unit costs vs a year ago, mean (Q3)': 'bie_uc', 'BIE year-ahead unit cost expectation, mean (Q4)': 'bie_uc_ahead',
         'Richmond Fed mfg survey: wages, current (diffusion)': 'rich_mfg_w', 'Richmond Fed services survey: avg wages, current (diffusion)': 'rich_svc_w'}
    for r in rd('B_q5_catchup.csv'):
        k = N.get(r['series'])
        if k and re.fullmatch(r'\d{4}-\d{2}', r['period']):
            add(k, r['period'], num(r['value']), src='outputs/B_q5_catchup.csv <- ' + r['source_file'])
    return S, ST, SRC


def load_quarterly():
    S = {}
    o = rd(PIPE_BLS)
    for r in o:
        if r['publisher_series_id'] in ('CIS2020000000000I', 'CIS2010000000000I') and r['value_type'] == 'index_level':
            q = f"{r['date'][:4]}Q{(int(r['date'][5:7]) - 1) // 3 + 1}"
            S.setdefault(r['publisher_series_id'], {})[q] = num(r['value'])
    d = json.load(open(os.path.join(RAWB, 'bls_api_productivity_costs_2008-2026_2026-11-15.json')))
    for blk in (d if isinstance(d, list) else [d]):
        for s in blk['Results']['series']:
            if s['seriesID'] in ('PRS85006093', 'PRS85006103', 'PRS85006113', 'PRS85006173', 'PRS85006174'):
                for x in s['data']:
                    if x['period'].startswith('Q') and x['value'] not in ('-', ''):
                        S.setdefault(s['seriesID'], {})[f"{x['year']}Q{int(x['period'][1:])}"] = num(x['value'])
    return S


def load_pce():
    S = {}
    for f, k in (('FRED_PCEPI_2026-11-15.json', 'pce'), ('FRED_PCEPILFE_2026-11-15.json', 'core')):
        for x in json.load(open(os.path.join(RAWC, f)))['observations']:
            if x['value'] != '.' and x['date'] >= '2016-01-01':
                S.setdefault(k, {})[x['date'][:7]] = float(x['value'])
    for r in rd(OCT_SUM):
        S['pce' if r['measure'] == 'headline' else 'core']['2026-10'] = float(r['index_t'])
    for f, k in (('FRED_DFEDTARU_2026-11-15.json', 'ffu'), ('FRED_DFEDTARL_2026-11-15.json', 'ffl')):
        obs = {x['date']: float(x['value']) for x in json.load(open(os.path.join(RAWC, f)))['observations'] if x['value'] != '.'}
        for m in months('2019-01', '2026-11'):
            ds = [d for d in obs if d[:7] == m]
            if ds:
                S.setdefault(k, {})[m] = obs[max(ds)]    # month-end (last available day) value
    return S


# ============================================================================ raw tabs
MCOLS = [('openings', 'JOLTS job openings, thous. (JTSJOL, SA)'), ('unemployed', 'Unemployed, thous. (UNEMPLOY, SA)'), ('unrate', 'Unemployment rate % (UNRATE, SA)'),
         ('ahe', 'AHE all private $/hr (CES0500000003, SA)'), ('ahe_pns', 'AHE prod. & nonsup. $/hr (CES0500000008, SA)'),
         ('wgt', 'Atlanta Fed WGT overall, 3mma %'), ('wgt_stay', 'WGT job stayer, 3mma %'), ('wgt_switch', 'WGT job switcher, 3mma %'),
         ('mich1', 'Michigan 1y median %'), ('mich510', 'Michigan 5-10y median %'), ('sce1', 'NY Fed SCE 1y median %'), ('sce3', 'NY Fed SCE 3y median %'),
         ('be5', '5y breakeven % (T5YIE, monthly avg)'), ('be10', '10y breakeven % (T10YIE, monthly avg)'), ('fwd55', '5y5y forward % (T5YIFR, monthly avg)'),
         ('gas', 'Regular gasoline $/gal (GASREGW, monthly avg, NSA)'),
         ('mct', 'NY Fed MCT central %'), ('mct_lo', 'MCT lower 68% band'), ('mct_hi', 'MCT upper 68% band'),
         ('dal12', 'Dallas trimmed mean PCE 12m %'), ('dal6', 'Dallas trimmed mean PCE 6m ann. %'), ('medpce', 'Cleveland median PCE 12m %'),
         ('medcpi', 'Cleveland median CPI 12m %'), ('trimcpi', 'Cleveland trimmed-mean CPI 12m %'), ('mbcore', 'BEA market-based core PCE 12m %'),
         ('super12', 'Supercore PCE 12m % (Oct est.)'), ('super3', 'Supercore PCE 3m ann. % (Oct est.)'),
         ('logan12', 'Logan measure 12m % (core svcs ex housing & transport; Oct est.)'), ('logan3', 'Logan measure 3m ann. % (Oct est.)'),
         ('nfib_comp', 'NFIB net % raised compensation'), ('nfib_comp_plan', 'NFIB net % planning to raise compensation'),
         ('nfib_px', 'NFIB net % raised selling prices'), ('nfib_px_plan', 'NFIB net % planning to raise prices'),
         ('bie_uc', 'Atlanta Fed BIE unit costs vs year ago, mean %'), ('bie_uc_ahead', 'BIE year-ahead unit cost exp., mean %'),
         ('rich_mfg_w', 'Richmond Fed mfg wages, current (diffusion)'), ('rich_svc_w', 'Richmond Fed services wages, current (diffusion)')]
MONTHS = months('2017-01', '2026-11')
QS = quarters('2016Q1', '2026Q3')
PMONTHS = months('2016-01', '2026-11')


def build_raw_monthly(ws, S, ST, SRC):
    raw_meta(ws, 'raw_monthly: monthly series behind BB_channels, Wages_ULC, Expectations, Underlying_trend, Catch_up', [
        ('Source', 'Agents\' CSVs in 02_Research/Subtasks/11_slide3a_research/outputs/ (A_q1_vu, B_q3_wages_ulc, B_q5_catchup, C_q4_expectations, C_q6_underlying) and the raw files they cite; AHE straight from the BLS API file. Row 5 below gives each column\'s file.'),
        ('Vintage', 'Pulled 2026-11-15 (pipeline files 2026-11-10/14). BEA PCE through Sep 2026 (Oct 29 release); Oct 2026 PCE-based values = UMD estimate ("est.", yellow).'),
        ('Flags', 'Yellow = est. (Oct PCE build) or PRELIMINARY (Michigan Nov; AHE Oct) or partial month (Nov gas/breakevens). Cell notes say which.'),
    ])
    hdr_row(ws, 6, 1, ['Month'] + [lbl for _, lbl in MCOLS], [10] + [14] * len(MCOLS))
    for j, (k, _) in enumerate(MCOLS):
        c = ws.cell(row=5, column=2 + j, value=SRC.get(k, ''))
        c.font = Font(size=7, color='7F7F7F')
    ROW, COL = {}, {}
    for i, m in enumerate(MONTHS):
        r = 7 + i
        ROW[m] = r
        put(ws, r, 1, m)
        for j, (k, _) in enumerate(MCOLS):
            COL[k] = 2 + j
            v = S.get(k, {}).get(m)
            if v is not None:
                st = ST.get((k, m))
                c = put(ws, r, 2 + j, v, fill=FILL_EST if st else None)
                if st:
                    note(c, st)
    ws.freeze_panes = 'B7'
    return ROW, COL


QCOLS = [('CIS2020000000000I', 'ECI wages & salaries, private, SA index (Dec 2005=100)'), ('CIS2010000000000I', 'ECI total compensation, private, SA index'),
         ('PRS85006093', 'Nonfarm business output per hour, index 2017=100'), ('PRS85006103', 'Nonfarm business hourly compensation, index 2017=100'),
         ('PRS85006113', 'Nonfarm business unit labor costs, index 2017=100'), ('PRS85006173', 'Nonfarm business labor share, index 2017=100'),
         ('PRS85006174', 'Nonfarm business labor share, level % of output')]


def build_raw_quarterly(ws, Q):
    raw_meta(ws, 'raw_quarterly: ECI and nonfarm business productivity and costs (index levels)', [
        ('Source', f'ECI: 03_Data/pipelines/inflation_data/processed/bls/observations.csv (raw: inflation_data/raw/bls/bls_api_all_series_*_2026-11-10.json). Productivity & costs: {REL(RAWB)}/bls_api_productivity_costs_2008-2026_2026-11-15.json'),
        ('Vintage', 'ECI 2026Q3 released 2026-10-30. Productivity & Costs 2026Q3 preliminary released 2026-11-05 (history revised back to 2021Q1 after BEA annual update).'),
        ('URL', 'https://api.bls.gov/publicAPI/v2/timeseries/data/ ; https://www.bls.gov/lpc/ ; https://www.bls.gov/eci/'),
    ])
    hdr_row(ws, 6, 1, ['Quarter'] + [f'{sid}: {lbl}' for sid, lbl in QCOLS], [10] + [18] * len(QCOLS))
    ROW, COL = {}, {}
    for i, q in enumerate(QS):
        r = 7 + i
        ROW[q] = r
        put(ws, r, 1, q)
        for j, (sid, _) in enumerate(QCOLS):
            COL[sid] = 2 + j
            v = Q.get(sid, {}).get(q)
            if v is not None:
                put(ws, r, 2 + j, v)
    ws.freeze_panes = 'B7'
    return ROW, COL


def build_raw_pce(ws, P):
    raw_meta(ws, 'raw_PCE_index: PCE and core PCE price index levels; fed funds target range (month-end)', [
        ('Source', f'{REL(RAWC)}/FRED_PCEPI_2026-11-15.json, FRED_PCEPILFE_2026-11-15.json (BEA vintage 2026-10-29); Oct 2026 = UMD estimate index_t from 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv; FRED_DFEDTARU/DFEDTARL_2026-11-15.json'),
        ('Units', 'PCEPI, PCEPILFE: index 2017=100, SA. Fed funds target range upper/lower bound, %, last daily value in the month.'),
        ('URL', 'https://fred.stlouisfed.org/series/PCEPI ; PCEPILFE ; DFEDTARU ; DFEDTARL'),
    ])
    hdr_row(ws, 6, 1, ['Month', 'PCEPI (headline)', 'PCEPILFE (core)', 'Fed funds target upper %', 'Fed funds target lower %'], [10, 14, 14, 14, 14])
    ROW = {}
    for i, m in enumerate(PMONTHS):
        r = 7 + i
        ROW[m] = r
        put(ws, r, 1, m + (' est.' if m == '2026-10' else ''), fill=FILL_EST if m == '2026-10' else None)
        for j, k in enumerate(('pce', 'core', 'ffu', 'ffl')):
            v = P.get(k, {}).get(m)
            if v is not None:
                put(ws, r, 2 + j, v, fill=FILL_EST if (m == '2026-10' and j < 2) else None)
    ws.freeze_panes = 'B7'
    return ROW


def build_raw_policy(ws):
    raw_meta(ws, 'raw_policy: FOMC target-range changes, Mar 2020 - Oct 2026 (plus the Oct 28, 2026 hold)', [
        ('Source', 'outputs/C_q8_policy_timeline.csv <- FOMC statements (federalreserve.gov press releases), cross-checked to FRED DFEDTARU/DFEDTARL and the Board\'s Open Market Operations table (03_Data/Raw/S3A_expectations_underlying_2026-11-15/FRB_openmarket_2026-11-15.htm).'),
        ('Note', 'date = statement date; effective_date = statement date + 1 (Board table convention).'),
    ])
    X = rd('C_q8_policy_timeline.csv')
    cols = ['date', 'effective_date', 'action', 'change_bp', 'lower', 'upper', 'vote', 'source_url']
    hdr_row(ws, 6, 1, cols, [12, 12, 40, 10, 8, 8, 12, 70])
    for i, x in enumerate(X):
        for j, c in enumerate(cols):
            v = num(x[c]) if c in ('change_bp', 'lower', 'upper') else x[c]
            put(ws, 7 + i, 1 + j, v)
    return X


# ============================================================================ generic blocks
def latest_row(S, key, ms):
    have = [m for m in ms if S.get(key, {}).get(m) is not None]
    return have[-1] if have else None


def stat_block(ws, r0, c0, first, last, specs, title, label_rows=None):
    """Summary rows: for each spec (label, col_letter_on_this_sheet, values{period: v}, latest_period) write latest, 2018-19 avg,
    2021-23 peak (max) with live formulas over this sheet's own block. Returns {label: (row)}."""
    sect(ws, r0 - 1, c0, title)
    hdr_row(ws, r0, c0, ['Measure', 'Latest', 'Latest period', '2018-19 avg', '2021-23 peak', '2021-23 peak period'], [44, 10, 12, 10, 10, 12])
    out = {}
    for i, (lbl, col, vals, rows_by_p, lp) in enumerate(specs):
        r = r0 + 1 + i
        text_cell(ws, r, c0, lbl)
        lr = rows_by_p[lp]
        put(ws, r, c0 + 1, f'={col}{lr}', F2, expect=vals[lp], fill=FILL_KEY)
        put(ws, r, c0 + 2, lp + (' est.' if lp == '2026-10' and 'est' in lbl else ''))
        p1819 = [p for p in rows_by_p if in_1819(p) and vals.get(p) is not None]
        p2123 = [p for p in rows_by_p if in_2123(p) and vals.get(p) is not None]
        if p1819:
            put(ws, r, c0 + 3, f'=AVERAGE({col}{rows_by_p[p1819[0]]}:{col}{rows_by_p[p1819[-1]]})', F2, expect=statistics.mean(vals[p] for p in p1819))
        if p2123:
            pk = max(p2123, key=lambda p: vals[p])
            put(ws, r, c0 + 4, f'=MAX({col}{rows_by_p[p2123[0]]}:{col}{rows_by_p[p2123[-1]]})', F2, expect=max(vals[p] for p in p2123))
            put(ws, r, c0 + 5, pk)
        out[lbl] = r
    return out


def sect(ws, row, col, text):
    if col == 1:
        section(ws, row, text)
    else:
        b1.WRITTEN.add((ws.title, row, col))
        ws.cell(row=row, column=col, value=text).font = Font(bold=True, size=12, color=b1.NAVY)


def line_chart(ws, first, last, cols, colors, title, ytitle, source, anchor, dashes=None, skip=12, w=24, h=11, cat_col=1, yfmt='0.0', xtitle='Month'):
    ch = LineChart()
    style_chart(ch, title, ytitle, xtitle, source, w=w, h=h, yfmt=yfmt)
    for k, (col, color) in enumerate(zip(cols, colors)):
        s = Series(Reference(ws, min_col=col, min_row=first, max_row=last), title=ws.cell(row=first - 1, column=col).value)
        line_style(s, color, dash=(dashes or {}).get(col), width_pt=2.0 if k == 0 else 1.5)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=cat_col, min_row=first, max_row=last))
    ch.x_axis.tickLblSkip = skip
    add_chart(ws, ch, anchor)


def bar_chart(ws, r0, r1, cats_col, cols, colors, title, ytitle, xtitle, source, anchor, w=18, h=10, yfmt='0.0'):
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, title, ytitle, xtitle, source, w=w, h=h, yfmt=yfmt)
    for col in cols:
        bc.add_data(Reference(ws, min_col=col, min_row=r0 - 1, max_row=r1), titles_from_data=True)
    for s_, color in zip(bc.series, colors):
        s_.graphicalProperties.solidFill = color
        s_.graphicalProperties.line.solidFill = color
    bc.set_categories(Reference(ws, min_col=cats_col, min_row=r0, max_row=r1))
    bc.y_axis.scaling.min = None
    add_chart(ws, bc, anchor)
    return bc


def monthly_block(ws, r0, c0, keys, labels, S, ST, MROW, MCOL, ms, title, extra=None):
    """Copy monthly series from raw_monthly via live references. extra: list of (label, fn(m) -> (formula, expect) or None).
    Returns (first_row, last_row, {key: col_letter}, {period: row}, vals{key:{m:v}})."""
    sect(ws, r0 - 1, c0, title)
    names = ['Month'] + labels + [e[0] for e in (extra or [])]
    hdr_row(ws, r0, c0, names, [10] + [12] * (len(names) - 1))
    rows, cols, vals = {}, {}, {}
    for i, m in enumerate(ms):
        r = r0 + 1 + i
        rows[m] = r
        is_est = any(ST.get((k, m)) == 'est.' for k in keys)
        put(ws, r, c0, m + (' est.' if is_est else ''), fill=FILL_EST if is_est else None)
        for j, k in enumerate(keys):
            col = c0 + 1 + j
            cols[k] = CL(col)
            v = S.get(k, {}).get(m)
            if v is not None:
                st = ST.get((k, m))
                put(ws, r, col, f'=raw_monthly!{CL(MCOL[k])}{MROW[m]}', F2, expect=v, fill=FILL_EST if st else None)
                vals.setdefault(k, {})[m] = v
        for j, (lbl, fn) in enumerate(extra or []):
            col = c0 + 1 + len(keys) + j
            cols[lbl] = CL(col)
            res = fn(m, r)
            if res is not None:
                f, e = res
                put(ws, r, col, f, F2, expect=e)
                vals.setdefault(lbl, {})[m] = e
    return r0 + 1, r0 + len(ms), cols, rows, vals


# ============================================================================ research tabs
def build_wages(ws, Q, QROW, QCOL, S, ST, MROW, MCOL):
    header(ws, 'Wages_ULC: are wages and unit labor costs running faster than 2% inflation allows? (Q3)',
           'Data only. Wage growth vs the 2%-consistent benchmark (2% + trend productivity); unit labor costs (ULC) 4q and 8q; labor share; productivity. 2021-23 window marked.',
           'Units: % change. Quarterly rates computed here from raw_quarterly index levels (y/y = 4-quarter change; 8q ann. = 8-quarter change annualized; q/q ann.). Monthly AHE from raw_monthly levels. SA except WGT (CPS-based). Vintage: ECI Oct 30; P&C Nov 5 (2026Q3 prelim); AHE Oct (Nov 6, prelim).')
    # ---- quarterly block
    r0 = 6
    section(ws, r0 - 1, 'A. Quarterly (live formulas over raw_quarterly)')
    names = ['Quarter', 'ECI W&S y/y', 'ECI W&S 8q ann.', 'ECI total comp y/y', 'ULC y/y (4q)', 'ULC 8q ann.', 'ULC q/q ann.', 'Hourly comp y/y',
             'Output per hour y/y', 'Output per hour 8q ann.', 'Labor share level %', 'Labor share index (2017=100)', '2021-23 window', '2%-consistent ULC']
    hdr_row(ws, r0, 1, names, [10] + [11] * (len(names) - 1))
    qs = quarters('2018Q1', '2026Q3')
    QR, QV = {}, {}

    def g(sid, q):
        return Q.get(sid, {}).get(q)

    def rc(sid, q):
        return f'raw_quarterly!{CL(QCOL[sid])}{QROW[q]}'
    specs = [('eci_yoy', 'CIS2020000000000I', 'yoy'), ('eci_8q', 'CIS2020000000000I', '8q'), ('ecitc_yoy', 'CIS2010000000000I', 'yoy'),
             ('ulc_yoy', 'PRS85006113', 'yoy'), ('ulc_8q', 'PRS85006113', '8q'), ('ulc_qq', 'PRS85006113', 'qq'), ('hc_yoy', 'PRS85006103', 'yoy'),
             ('oph_yoy', 'PRS85006093', 'yoy'), ('oph_8q', 'PRS85006093', '8q'), ('ls_lvl', 'PRS85006174', 'lvl'), ('ls_idx', 'PRS85006173', 'lvl')]
    for i, q in enumerate(qs):
        r = r0 + 1 + i
        QR[q] = r
        put(ws, r, 1, q)
        for j, (k, sid, kind) in enumerate(specs):
            col = 2 + j
            if kind == 'lvl':
                v = g(sid, q)
                f = f'={rc(sid, q)}'
            elif kind == 'yoy':
                a, b_ = g(sid, q), g(sid, qshift(q, 4))
                v = (a / b_ - 1) * 100
                f = f'=({rc(sid, q)}/{rc(sid, qshift(q, 4))}-1)*100'
            elif kind == '8q':
                a, b_ = g(sid, q), g(sid, qshift(q, 8))
                v = ((a / b_) ** 0.5 - 1) * 100
                f = f'=(({rc(sid, q)}/{rc(sid, qshift(q, 8))})^0.5-1)*100'
            else:
                a, b_ = g(sid, q), g(sid, qshift(q, 1))
                v = ((a / b_) ** 4 - 1) * 100
                f = f'=(({rc(sid, q)}/{rc(sid, qshift(q, 1))})^4-1)*100'
            put(ws, r, col, f, F2 if kind != 'lvl' else F1, expect=v)
            QV.setdefault(k, {})[q] = v
        put(ws, r, 13, 1 if in_2123(q) else 0)
        put(ws, r, 14, 2)
    QC = {k: CL(2 + j) for j, (k, _, _) in enumerate(specs)}
    qlast = r0 + len(qs)
    # ---- monthly block (AHE, WGT) at column P
    c0 = 16
    ms = months('2018-01', '2026-10')

    def ahe_yoy(m, r):
        a, b_ = S['ahe'].get(m), S['ahe'].get(shift(m, 12))
        if a is None or b_ is None:
            return None
        return (f'=(raw_monthly!{CL(MCOL["ahe"])}{MROW[m]}/raw_monthly!{CL(MCOL["ahe"])}{MROW[shift(m, 12)]}-1)*100', (a / b_ - 1) * 100)

    def ahe_3m(m, r):
        a, b_ = S['ahe'].get(m), S['ahe'].get(shift(m, 3))
        if a is None or b_ is None:
            return None
        return (f'=((raw_monthly!{CL(MCOL["ahe"])}{MROW[m]}/raw_monthly!{CL(MCOL["ahe"])}{MROW[shift(m, 3)]})^4-1)*100', ((a / b_) ** 4 - 1) * 100)

    def pns_yoy(m, r):
        a, b_ = S['ahe_pns'].get(m), S['ahe_pns'].get(shift(m, 12))
        if a is None or b_ is None:
            return None
        return (f'=(raw_monthly!{CL(MCOL["ahe_pns"])}{MROW[m]}/raw_monthly!{CL(MCOL["ahe_pns"])}{MROW[shift(m, 12)]}-1)*100', (a / b_ - 1) * 100)
    BENCH = [x for x in rd('B_q3_benchmark.csv') if x['central_benchmark'] == 'YES'][0]
    bench_v = num(BENCH['implied_wage_growth_2pct_inflation'])
    CONST[('Wages_ULC', 'C61')] = bench_v
    BROW = 60   # benchmark block row (column A), formulas reference it
    BCELL = f'$C${BROW + 1}'

    def bench(m, r):
        return (f'={BCELL}', bench_v)
    mf, ml, mcols, mrows, mvals = monthly_block(ws, r0, c0, ['wgt'], ['Atlanta Fed WGT overall (3mma)'], S, ST, MROW, MCOL, ms,
                                                'B. Monthly wages (live formulas over raw_monthly)',
                                                extra=[('AHE all private y/y', ahe_yoy), ('AHE all private 3m ann.', ahe_3m), ('AHE prod. & nonsup. y/y', pns_yoy),
                                                       ('2%-consistent wage growth (central)', bench)])
    # ---- benchmark block
    section(ws, BROW - 1, 'C. Benchmark: wage growth consistent with 2% inflation = 2% + trend productivity (outputs/B_q3_benchmark.csv; script values)')
    hdr_row(ws, BROW, 1, ['Trend candidate', 'Trend productivity %', 'Implied 2%-consistent wage growth %', 'Central?', 'Note'])
    X = rd('B_q3_benchmark.csv')
    X.sort(key=lambda x: 0 if x['central_benchmark'] == 'YES' else 1)
    for i, x in enumerate(X):
        r = BROW + 1 + i
        text_cell(ws, r, 1, x['candidate_trend'])
        c = put(ws, r, 2, num(x['value_pct']), F2, fill=FILL_KEY if i == 0 else None)
        note(c, 'outputs/B_q3_benchmark.csv')
        put(ws, r, 3, num(x['implied_wage_growth_2pct_inflation']), F2, fill=FILL_KEY if i == 0 else None)
        put(ws, r, 4, 'central' if x['central_benchmark'] == 'YES' else '')
        text_cell(ws, r, 5, x['note'])
    # ---- summary block
    sr = BROW + len(X) + 4
    spec = [('ECI wages & salaries, private, y/y (CIS2020000000000I, SA)', QC['eci_yoy'], QV['eci_yoy'], QR, '2026Q3'),
            ('ECI W&S 8q annualized', QC['eci_8q'], QV['eci_8q'], QR, '2026Q3'),
            ('ECI total compensation, private, y/y', QC['ecitc_yoy'], QV['ecitc_yoy'], QR, '2026Q3'),
            ('ULC y/y (PRS85006113)', QC['ulc_yoy'], QV['ulc_yoy'], QR, '2026Q3'),
            ('ULC 8q annualized', QC['ulc_8q'], QV['ulc_8q'], QR, '2026Q3'),
            ('ULC q/q annualized', QC['ulc_qq'], QV['ulc_qq'], QR, '2026Q3'),
            ('Hourly compensation y/y (PRS85006103)', QC['hc_yoy'], QV['hc_yoy'], QR, '2026Q3'),
            ('Output per hour y/y (PRS85006093)', QC['oph_yoy'], QV['oph_yoy'], QR, '2026Q3'),
            ('Output per hour 8q annualized', QC['oph_8q'], QV['oph_8q'], QR, '2026Q3'),
            ('Labor share level % (PRS85006174)', QC['ls_lvl'], QV['ls_lvl'], QR, '2026Q3'),
            ('AHE all private y/y (Oct prelim)', mcols['AHE all private y/y'], mvals['AHE all private y/y'], mrows, '2026-10'),
            ('AHE all private 3m ann. (Oct prelim)', mcols['AHE all private 3m ann.'], mvals['AHE all private 3m ann.'], mrows, '2026-10'),
            ('AHE prod. & nonsup. y/y (Oct prelim)', mcols['AHE prod. & nonsup. y/y'], mvals['AHE prod. & nonsup. y/y'], mrows, '2026-10'),
            ('Atlanta Fed WGT overall 3mma', mcols['wgt'], mvals['wgt'], mrows, '2026-09')]
    SR = stat_block(ws, sr + 1, 1, None, None, spec, 'D. Summary: latest vs 2018-19 average vs 2021-23 peak (live formulas over blocks A and B)')
    # labor share: 2021-23 peak is not informative; add record-low check
    r = sr + 2 + len(spec) + 1
    text_cell(ws, r, 1, 'Labor share index: record low in the 2008-2026Q3 index history? (MIN over raw_quarterly)')
    ls_all = [v for q, v in Q['PRS85006173'].items()]
    put(ws, r, 2, f'=MIN(raw_quarterly!{CL(QCOL["PRS85006173"])}7:{CL(QCOL["PRS85006173"])}{6 + len(QS)})', F3, expect=min(v for q, v in Q['PRS85006173'].items() if q in QROW))
    put(ws, r, 3, f'=raw_quarterly!{CL(QCOL["PRS85006173"])}{QROW["2026Q3"]}', F3, expect=Q['PRS85006173']['2026Q3'])
    text_cell(ws, r, 4, '<- B = minimum since 2016Q1 on this tab; C = 2026Q3. Full-history check (from 1947, current vintage): outputs/B_q3_labor_share.md.')
    # semantic checks vs B_q3_summary
    BS = {(x['series_id'], x['measure']): x for x in rd('B_q3_summary.csv')}

    def sem(label, sid, meas, col_off=1):
        x = BS.get((sid, meas))
        if x:
            SEMANTIC.append(('Wages_ULC', f'{CL(1 + col_off)}{SR[label]}', num(x['latest']), 0.006, f'B_q3_summary {sid} {meas}'))
    for label, sid in (('ECI wages & salaries, private, y/y (CIS2020000000000I, SA)', 'CIS2020000000000I'), ('ULC y/y (PRS85006113)', 'PRS85006113'),
                       ('Hourly compensation y/y (PRS85006103)', 'PRS85006103'), ('Output per hour y/y (PRS85006093)', 'PRS85006093')):
        sem(label, sid, 'y/y')
    for label, sid in (('ULC 8q annualized', 'PRS85006113'), ('Output per hour 8q annualized', 'PRS85006093'), ('ECI W&S 8q annualized', 'CIS2020000000000I')):
        sem(label, sid, '8q annualised')
    for label, sid in (('AHE all private y/y (Oct prelim)', 'CES0500000003'), ('AHE prod. & nonsup. y/y (Oct prelim)', 'CES0500000008')):
        sem(label, sid, 'y/y')
    sem('AHE all private 3m ann. (Oct prelim)', 'CES0500000003', '3m annualised')
    KEYCELLS.update({'eci_yoy': f'Wages_ULC!B{SR["ECI wages & salaries, private, y/y (CIS2020000000000I, SA)"]}', 'ulc_yoy': f'Wages_ULC!B{SR["ULC y/y (PRS85006113)"]}',
                     'ulc_8q': f'Wages_ULC!B{SR["ULC 8q annualized"]}', 'ls_lvl': f'Wages_ULC!B{SR["Labor share level % (PRS85006174)"]}',
                     'ahe_yoy': f'Wages_ULC!B{SR["AHE all private y/y (Oct prelim)"]}', 'wgt': f'Wages_ULC!B{SR["Atlanta Fed WGT overall 3mma"]}',
                     'bench': f'Wages_ULC!C{BROW + 1}', 'eci_yoy_1819': f'Wages_ULC!D{SR["ECI wages & salaries, private, y/y (CIS2020000000000I, SA)"]}',
                     'eci_yoy_peak': f'Wages_ULC!E{SR["ECI wages & salaries, private, y/y (CIS2020000000000I, SA)"]}',
                     'ulc_yoy_1819': f'Wages_ULC!D{SR["ULC y/y (PRS85006113)"]}', 'ulc_yoy_peak': f'Wages_ULC!E{SR["ULC y/y (PRS85006113)"]}',
                     'ulc_8q_1819': f'Wages_ULC!D{SR["ULC 8q annualized"]}', 'ulc_8q_peak': f'Wages_ULC!E{SR["ULC 8q annualized"]}'})
    WG = {'SR': SR, 'QV': QV, 'mvals': mvals, 'bench': bench_v}
    # charts
    line_chart(ws, mf, ml, [c0 + 2, c0 + 1, c0 + 5], [BLUE, ORANGE, GREY], 'Wage growth vs the 2%-consistent benchmark (2% + 1.5% trend productivity)',
               '% change', 'Source: BLS CES (AHE y/y, SA; Oct prelim); Atlanta Fed Wage Growth Tracker (3mma, through Sep). Dashed = 3.52% benchmark (B_q3_benchmark.csv).',
               'AE5', dashes={c0 + 5: 'dash'}, cat_col=c0)
    line_chart(ws, r0 + 1, qlast, [5, 6, 14], [RED, BLUE, GREY], 'Unit labor costs, nonfarm business: 4-quarter and 8-quarter (annualized) change',
               '% change', 'Source: BLS Productivity & Costs (PRS85006113), 2026Q3 prelim, Nov 5. Dashed = 2% (ULC pace consistent with 2% if margins are stable).',
               'AE29', dashes={14: 'dash'}, skip=4, xtitle='Quarter')
    line_chart(ws, r0 + 1, qlast, [11], [PURPLE], 'Labor share, nonfarm business (% of output)', '% of output',
               'Source: BLS PRS85006174, current vintage (Nov 5). Q2 2026 = 53.3 now; 52.8 (Barr) was the pre-revision vintage.',
               'AE53', skip=4, xtitle='Quarter', yfmt='0.0')
    return WG


def build_expectations(ws, S, ST, MROW, MCOL):
    header(ws, 'Expectations: short- vs long-run inflation expectations for households, professionals and markets; co-movement with gas (Q4)',
           'Data only. Latest vs 2018-19 average and 2021-23 peak; monthly charts; SPF (quarterly); correlation of 12m changes with gasoline prices (descriptive, not causal).',
           'Units: % (expected inflation) and $/gal (gas). Michigan Nov 2026 = PRELIMINARY (final Nov 20, after cutoff). SCE Oct survey released Nov 9. Breakevens and gas: monthly averages; Nov = partial month (yellow). SPF Q4 2026 not released as of Nov 15.')
    keys = ['mich1', 'sce1', 'be5', 'mich510', 'sce3', 'fwd55', 'be10', 'gas']
    labels = ['Michigan 1y', 'SCE 1y', '5y breakeven', 'Michigan 5-10y', 'SCE 3y', '5y5y forward', '10y breakeven', 'Gasoline $/gal']
    ms = months('2018-01', '2026-11')
    first, last, cols, rows, vals = monthly_block(ws, 6, 1, keys, labels, S, ST, MROW, MCOL, ms, 'A. Monthly (live references to raw_monthly)',
                                                  extra=[('2% line', lambda m, r: ('=2', 2.0))])
    sr = last + 4
    spec = []
    for k, lbl in zip(keys, labels):
        lp = latest_row(S, k, ms)
        if k in ('gas', 'be5', 'be10', 'fwd55'):
            lp = '2026-10'    # latest full month
        spec.append((f'{lbl} ({"latest full month" if lp == "2026-10" and k in ("gas","be5","be10","fwd55") else "latest"})', cols[k], vals[k], rows, lp))
    SR = stat_block(ws, sr, 1, None, None, spec, 'B. Summary: latest vs 2018-19 average vs 2021-23 peak (live formulas over block A)')
    mlbl = spec[3][0]
    note(ws.cell(row=SR[mlbl], column=5), 'CAUTION: survey-mode break. Michigan moved from phone to web interviews in 2024. UMich\'s web-only series puts Jun 2025 (4.0) at the mid-2022 peak (03_Data/Raw/S3A_D_michigan_mode_2026-11-15/umich_px5web202506.pdf). Do not compare the current reading with this 2021-23 peak; compare within the web era only.')
    rr = SR[spec[-1][0]] + 1
    text_cell(ws, rr, 1, 'CAUTION (Michigan rows): Michigan switched from phone to web interviewing in 2024. UMich\'s web-only series says Jun 2025\'s 5-10y median of 4.0 "matches the peak reading from mid-2022". So Michigan "now vs 2021-23 peak" and "now vs 2018-19" straddle a mode break. Within the web era: 5-10y 4.4 (Apr 2025) -> 3.3 (Feb 2026) -> 3.4 (Nov 2026 prelim). Source: report_D.md, D_q9_checks.csv rows 18-21.')
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=6)
    ws.row_dimensions[rr].height = 60
    CS = {x['series']: x for x in rd('C_q4_summary.csv')}
    for (lbl, *_), csvname in zip(spec, ['Michigan 1y median', 'SCE 1y median', None, 'Michigan 5-10y median', 'SCE 3y median', None, None, None]):
        if csvname and csvname in CS:
            SEMANTIC.append(('Expectations', f'B{SR[lbl]}', num(CS[csvname]['latest_value']), 0.006, f'C_q4_summary {csvname} latest'))
            SEMANTIC.append(('Expectations', f'D{SR[lbl]}', num(CS[csvname]['avg_2018_19']), 0.006, f'C_q4_summary {csvname} 2018-19'))
            SEMANTIC.append(('Expectations', f'E{SR[lbl]}', num(CS[csvname]['peak_2021_23_value']), 0.006, f'C_q4_summary {csvname} peak'))
    KEYCELLS.update({'mich1': f'Expectations!B{SR[spec[0][0]]}', 'sce1': f'Expectations!B{SR[spec[1][0]]}', 'mich510': f'Expectations!B{SR[spec[3][0]]}',
                     'sce3': f'Expectations!B{SR[spec[4][0]]}', 'fwd55': f'Expectations!B{SR[spec[5][0]]}',
                     'mich1_1819': f'Expectations!D{SR[spec[0][0]]}', 'mich1_peak': f'Expectations!E{SR[spec[0][0]]}',
                     'sce1_1819': f'Expectations!D{SR[spec[1][0]]}', 'sce1_peak': f'Expectations!E{SR[spec[1][0]]}',
                     'mich510_1819': f'Expectations!D{SR[spec[3][0]]}', 'mich510_peak': f'Expectations!E{SR[spec[3][0]]}',
                     'fwd55_1819': f'Expectations!D{SR[spec[5][0]]}', 'fwd55_peak': f'Expectations!E{SR[spec[5][0]]}'})
    # SPF block (script values)
    r = sr + len(spec) + 3
    section(ws, r, 'C. SPF medians, Q3 2026 survey (released Aug 14, 2026; script values from outputs/C_q4_summary.csv). Q4 2026 due Nov 16: not yet released at build.')
    hdr_row(ws, r + 1, 1, ['Series', 'Latest', 'Survey', '2018-19 avg', '2021-23 peak', 'Peak survey'])
    spf = [x for x in rd('C_q4_summary.csv') if x['group'] == 'Professionals']
    for i, x in enumerate(spf):
        rr = r + 2 + i
        text_cell(ws, rr, 1, f"{x['series']} ({x['horizon']})")
        c = put(ws, rr, 2, num(x['latest_value']), F2)
        note(c, 'outputs/C_q4_summary.csv')
        put(ws, rr, 3, x['latest_period'])
        put(ws, rr, 4, num(x['avg_2018_19']), F2)
        put(ws, rr, 5, num(x['peak_2021_23_value']), F2)
        put(ws, rr, 6, x['peak_2021_23_period'])
    # gas co-movement block
    r = r + 3 + len(spf)
    section(ws, r, 'D. Co-movement with gasoline: correlation of 12-month changes (outputs/C_q4_gas_comovement.csv; descriptive, autocorrelated, small n)')
    G = rd('C_q4_gas_comovement.csv')
    pairs = ['Michigan 1y median', 'SCE 1y median', 'Michigan 5-10y median', 'SCE 3y median', '5y5y forward breakeven (monthly avg)']
    wins = {}
    for x in G:
        if not x['transform'].startswith('12m change (gas %'):
            continue
        for p in pairs:
            if x['series_pair'] == 'Gas (GASREGW monthly avg) vs ' + p:
                wins[(p, x['window'])] = (num(x['corr']), x['n'])
    wl = sorted({w for (_, w) in wins}, key=lambda w: (w[:4] != '2018', w))
    hdr_row(ws, r + 1, 1, ['Expectation series (12m change vs gas 12m % change)'] + [f'{w}' for w in wl])
    for i, p in enumerate(pairs):
        rr = r + 2 + i
        text_cell(ws, rr, 1, p)
        for j, w in enumerate(wl):
            if (p, w) in wins:
                c = put(ws, rr, 2 + j, wins[(p, w)][0], F2)
                note(c, f'n = {wins[(p, w)][1]}; outputs/C_q4_gas_comovement.csv')
    assert all((p, w) in wins for p in pairs for w in wl), 'gas correlation table has gaps'
    gr0, gr1 = r + 2, r + 1 + len(pairs)
    bar_chart(ws, gr0, gr1, 1, [2 + j for j in range(len(wl))], [GREY, RED, BLUE, GREEN][:len(wl)],
              'Correlation of 12-month changes with gasoline prices, by window', 'Correlation', 'Expectation series',
              'Source: C_q4_gas_comovement.csv (Michigan, NY Fed SCE, FRED T5YIFR, GASREGW). Descriptive; not causal.', 'L82', w=20, h=10, yfmt='0.0')
    # Logan aggregate
    r = gr1 + 3
    section(ws, r, 'E. Logan\'s "13 surveys" one-year aggregate: our reconstruction (outputs/C_q4_logan_aggregate.csv; pipeline Inflation_Expectations.xlsx, Nov 14)')
    LA = rd('C_q4_logan_aggregate.csv')
    hdr_row(ws, r + 1, 1, ['Row', 'Group', 'Measure', 'Value', 'Observation'])
    for i, x in enumerate(LA):
        for j, k in enumerate(['row_type', 'group', 'measure', 'value', 'observation']):
            v = num(x[k]) if k == 'value' else x[k]
            put(ws, r + 2 + i, 1 + j, v, F2 if k == 'value' else None)
    # charts
    line_chart(ws, first, last, [2, 3, 4, 10], [RED, ORANGE, BLUE, GREY], 'Short-run inflation expectations: households vs markets', '%',
               'Source: U. Michigan (Nov prelim), NY Fed SCE (Oct), FRED T5YIE (monthly avg). Dashed = 2%.', 'L5', dashes={10: 'dash'})
    line_chart(ws, first, last, [5, 6, 7, 10], [RED, ORANGE, BLUE, GREY], 'Longer-run inflation expectations: households vs markets', '%',
               'Source: U. Michigan 5-10y (Nov prelim), NY Fed SCE 3y (Oct), FRED T5YIFR 5y5y (monthly avg). Dashed = 2%.', 'L29', dashes={10: 'dash'})
    line_chart(ws, first, last, [9], [BLACK], 'Regular gasoline price, monthly average', '$ per gallon',
               'Source: EIA via FRED GASREGW (weekly, NSA), monthly average; Nov = partial month.', 'L55', yfmt='0.00')
    return SR


def build_underlying(ws, S, ST, MROW, MCOL, PROW, P):
    header(ws, 'Underlying_trend: where is underlying inflation? MCT vs trimmed mean vs median vs Logan\'s measure vs supercore (Q6)',
           'Data only. Refreshed underlying-trend measures, monthly from 2018; latest vs 2018-19 average and 2021-23 peak; check of every number the roadmap quotes. Rates, not breadth (slide 2 has breadth).',
           'Units: %, 12-month change unless stated (MCT = trend estimate, annualized). Sep 2026 = latest BEA data (Oct 29 release); Oct 2026 = UMD estimate ("est.") for supercore, Logan measure and core PCE. Cleveland CPI measures through Oct.')
    keys = ['mct', 'dal12', 'medpce', 'mbcore', 'super12', 'logan12', 'mct_lo', 'mct_hi', 'dal6', 'super3', 'logan3']
    labels = ['NY Fed MCT', 'Dallas trimmed mean 12m', 'Cleveland median PCE 12m', 'Market-based core 12m', 'Supercore 12m', 'Logan measure 12m',
              'MCT lower band', 'MCT upper band', 'Dallas trimmed mean 6m ann.', 'Supercore 3m ann.', 'Logan measure 3m ann.']
    ms = months('2018-01', '2026-10')

    def core12(m, r):
        a, b_ = P['core'].get(m), P['core'].get(shift(m, 12))
        return (f'=(raw_PCE_index!C{PROW[m]}/raw_PCE_index!C{PROW[shift(m, 12)]}-1)*100', (a / b_ - 1) * 100)
    first, last, cols, rows, vals = monthly_block(ws, 6, 1, keys, labels, S, ST, MROW, MCOL, ms, 'A. Monthly (live references to raw_monthly; core PCE 12m computed from raw_PCE_index)',
                                                  extra=[('Core PCE 12m', core12), ('2% line', lambda m, r: ('=2', 2.0))])
    sr = last + 4
    spec = []
    for k, lbl in [('dal12', 'Dallas trimmed mean PCE 12m (Sep)'), ('medpce', 'Cleveland median PCE 12m (Sep)'), ('mct', 'NY Fed MCT (Sep)'),
                   ('Core PCE 12m', 'Core PCE 12m (Sep)'), ('mbcore', 'Market-based core PCE 12m (Sep)'), ('logan12', 'Logan measure 12m (Sep)'), ('super12', 'Supercore 12m (Sep)')]:
        spec.append((lbl, cols[k], vals[k], rows, '2026-09'))
    for k, lbl in [('logan12', 'Logan measure 12m, Oct est.'), ('super12', 'Supercore 12m, Oct est.'), ('Core PCE 12m', 'Core PCE 12m, Oct est.'),
                   ('logan3', 'Logan measure 3m ann. (Sep)'), ('super3', 'Supercore 3m ann. (Sep)')]:
        spec.append((lbl, cols[k], vals[k], rows, '2026-10' if 'Oct' in lbl else '2026-09'))
    spec.append(('Logan measure 3m ann., Oct est.', cols['logan3'], vals['logan3'], rows, '2026-10'))
    spec.append(('Supercore 3m ann., Oct est.', cols['super3'], vals['super3'], rows, '2026-10'))
    SR = stat_block(ws, sr, 1, None, None, spec, 'B. Summary: latest vs 2018-19 average vs 2021-23 peak (live formulas over block A); rows 1-7 sorted low to high = chart order')
    CS = {(x['group'], x['series'], x['horizon']): x for x in rd('C_q6_summary.csv')}

    def csv_val(series_sub, horizon_sub, period):
        for (g_, s_, h_), x in CS.items():
            if series_sub in s_ and horizon_sub in h_ and x['latest_period'] == period:
                return num(x['latest_value'])
    for lbl, ss, hs, per in [('NY Fed MCT (Sep)', 'MCT central', '', '2026-09'), ('Dallas trimmed mean PCE 12m (Sep)', 'trimmed-mean PCE', '12m', '2026-09'),
                             ('Logan measure 12m, Oct est.', 'Logan', '12m', '2026-10')]:
        v = csv_val(ss, hs, per)
        if v is not None:
            SEMANTIC.append(('Underlying_trend', f'B{SR[lbl]}', v, 0.006, f'C_q6_summary {ss} {per}'))
    lm = {x['month']: x for x in rd('C_q6_logan_measure.csv')}
    SEMANTIC.append(('Underlying_trend', f'B{SR["Logan measure 12m (Sep)"]}', num(lm['2026-09']['12m_pct']), 0.0006, 'C_q6_logan_measure 2026-09 12m'))
    SEMANTIC.append(('Underlying_trend', f'B{SR["Core PCE 12m (Sep)"]}', 3.121, 0.0006, 'core PCE 12m Sep (C_q6_roadmap_check 3.121)'))
    KEYCELLS.update({'mct': f'Underlying_trend!B{SR["NY Fed MCT (Sep)"]}', 'dal12': f'Underlying_trend!B{SR["Dallas trimmed mean PCE 12m (Sep)"]}',
                     'logan12': f'Underlying_trend!B{SR["Logan measure 12m (Sep)"]}', 'logan12_oct': f'Underlying_trend!B{SR["Logan measure 12m, Oct est."]}',
                     'logan3': f'Underlying_trend!B{SR["Logan measure 3m ann. (Sep)"]}', 'logan3_oct': f'Underlying_trend!B{SR["Logan measure 3m ann., Oct est."]}',
                     'super12': f'Underlying_trend!B{SR["Supercore 12m (Sep)"]}', 'medpce': f'Underlying_trend!B{SR["Cleveland median PCE 12m (Sep)"]}'})
    # roadmap check
    r = sr + len(spec) + 3
    section(ws, r, 'C. Roadmap number check (outputs/C_q6_roadmap_check.csv; script values)')
    RC = rd('C_q6_roadmap_check.csv')
    hdr_row(ws, r + 1, 1, ['Claim', 'Roadmap/speech value', 'Publisher value', 'Diff', 'Verdict', 'Vintage'])
    for i, x in enumerate(RC):
        for j, k in enumerate(['claim', 'roadmap_or_speech_value', 'publisher_value', 'diff', 'verdict', 'vintage']):
            v = num(x[k]) if k in ('roadmap_or_speech_value', 'publisher_value', 'diff') else x[k]
            c = put(ws, r + 2 + i, 1 + j, v, F3 if isinstance(v, float) else None)
            if not isinstance(v, float):
                c.alignment = WRAP
    # bar chart of latest (rows 1-7 of summary)
    b0 = SR['Dallas trimmed mean PCE 12m (Sep)']
    bar_chart(ws, b0, b0 + 6, 1, [2], [PURPLE], 'Underlying inflation measures, September 2026 (12-month % change; MCT = trend estimate)', '%', 'Measure',
              'Source: Dallas Fed, Cleveland Fed, NY Fed MCT, BEA (Oct 29 release); Logan measure derived from BEA U20404/U20405 (C_q6_logan_measure.csv).', 'O5', w=22, h=11)
    line_chart(ws, first, last, [2, 3, 4, 7, 13, 14], [PURPLE, GREEN, ORANGE, RED, BLACK, GREY],
               'Underlying inflation measures, 2018 to Oct 2026 (Oct = est. for Logan measure and core PCE)', '%',
               'Source: NY Fed MCT; Dallas Fed trimmed mean PCE; Cleveland Fed median PCE; Logan measure (BEA, derived); core PCE (BEA; Oct UMD est.). Dashed = 2%.',
               'O29', dashes={14: 'dash'})
    return SR


def build_catchup(ws, S, ST, MROW, MCOL):
    header(ws, 'Catch_up: are firms planning to catch wages and prices up? Survey and anecdotal evidence (Q5)',
           'Data only. All series here are SURVEYS (not hard data). NFIB = net % of small-business owners (raise minus lower), SA. Atlanta Fed BIE = mean % unit-cost change. Richmond Fed = diffusion indexes (% up minus % down).',
           'Latest: NFIB Oct 2026 report; BIE Oct 2026; Richmond Oct 2026. Sources: outputs/B_q5_catchup.csv, B_q5_summary.csv. Eli\'s podcast figures (34% prices / 24% comp) checked in section C.')
    keys = ['nfib_comp_plan', 'nfib_px_plan', 'nfib_comp', 'nfib_px', 'bie_uc', 'bie_uc_ahead', 'rich_mfg_w', 'rich_svc_w']
    labels = ['NFIB plan to raise comp.', 'NFIB plan to raise prices', 'NFIB raised comp.', 'NFIB raised prices', 'BIE unit costs vs yr ago', 'BIE year-ahead unit cost',
              'Richmond mfg wages (current)', 'Richmond services wages (current)']
    ms = months('2018-01', '2026-10')
    first, last, cols, rows, vals = monthly_block(ws, 6, 1, keys, labels, S, ST, MROW, MCOL, ms, 'A. Monthly (live references to raw_monthly)')
    sr = last + 4
    spec = [(lbl, cols[k], vals[k], rows, latest_row(S, k, ms)) for k, lbl in zip(keys, labels)]
    SR = stat_block(ws, sr, 1, None, None, spec, 'B. Summary: latest vs 2018-19 average vs 2021-23 peak (live formulas over block A)')
    BS = {x['series']: x for x in rd('B_q5_summary.csv')}
    for lbl, s_ in [('NFIB plan to raise comp.', 'NFIB net % planning to raise compensation, next 3 months'), ('NFIB plan to raise prices', 'NFIB net % planning to raise prices, next 3 months')]:
        SEMANTIC.append(('Catch_up', f'B{SR[lbl]}', num(BS[s_]['latest']), 0.006, f'B_q5_summary {s_}'))
        SEMANTIC.append(('Catch_up', f'D{SR[lbl]}', num(BS[s_]['avg_2018_19']), 0.006, f'B_q5_summary {s_} 1819'))
        SEMANTIC.append(('Catch_up', f'E{SR[lbl]}', num(BS[s_]['peak_2021_23']), 0.006, f'B_q5_summary {s_} peak'))
    KEYCELLS.update({'nfib_comp_plan': f'Catch_up!B{SR["NFIB plan to raise comp."]}', 'nfib_px_plan': f'Catch_up!B{SR["NFIB plan to raise prices"]}',
                     'nfib_comp_plan_1819': f'Catch_up!D{SR["NFIB plan to raise comp."]}', 'nfib_comp_plan_peak': f'Catch_up!E{SR["NFIB plan to raise comp."]}',
                     'bie_uc_ahead': f'Catch_up!B{SR["BIE year-ahead unit cost"]}'})
    r = sr + len(spec) + 3
    section(ws, r, 'C. Other surveys and anecdotes (script values; outputs/B_q5_catchup.csv, report_B.md)')
    hdr_row(ws, r + 1, 1, ['Source', 'Series', 'Period', 'Value', 'Units / note'], [30, 60, 22, 10, 60])
    other = [x for x in rd('B_q5_catchup.csv') if not re.fullmatch(r'\d{4}-\d{2}', x['period']) or x['series'] in (
        'NFIB % citing labor costs as single most important problem', 'NFIB % citing labor quality/availability as single most important problem', 'NFIB % with unfilled job openings',
        'CCI: consumers average 12-month inflation expectations')]
    for i, x in enumerate(other):
        rr = r + 2 + i
        text_cell(ws, rr, 1, x['source'])
        text_cell(ws, rr, 2, x['series'])
        put(ws, rr, 3, x['period'])
        put(ws, rr, 4, num(x['value']), F1)
        text_cell(ws, rr, 5, f"{x['units']}; {x['survey_or_hard']}")
    rr = r + 3 + len(other)
    for t in ('Eli\'s podcast figures: "24%" = NFIB net % planning to raise compensation, Oct 2026 (matches). "34%" does NOT match Oct 2026 planned prices (net 37); it matches Nov 2025 net % that actually raised prices. These are net balances, not shares of firms.',
              'Beige Book, Oct 14, 2026 (information through Oct 5): "Several Districts noted that inflation has spawned additional wage pressure in the form of higher cost-of-living demands from individuals as well as challenges from rising benefit costs." "Higher oil prices permeated all District reports."',
              'Logan (Nov 10): a CEO planning larger 2027 raises to offset 2026 inflation (anecdote). Paulson (Nov 10): isolated reports of bigger raises; "nothing in the data" shows it is widespread (as summarized in Fed_officials_2026-11/summary.md).'):
        text_cell(ws, rr, 1, t)
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=5)
        ws.row_dimensions[rr].height = 45
        rr += 1
    line_chart(ws, first, last, [3, 2], [RED, BLUE], 'NFIB small-business plans: net % planning to raise prices and compensation (next 3 months)', 'Net % of owners',
               'Source: NFIB Small Business Economic Trends (Oct 2026 report; 2018-20 from Dec 2020 report), SA net balances. Survey data.', 'K5', yfmt='0')
    line_chart(ws, first, last, [6, 7], [PURPLE, GREY], 'Atlanta Fed BIE: unit costs vs a year ago and expected year ahead (mean %)', '%',
               'Source: Atlanta Fed Business Inflation Expectations (pipeline file, Nov 14). Survey data.', 'K29', dashes={7: 'dash'})
    return SR


def build_bb(ws, S, ST, MROW, MCOL):
    header(ws, 'BB_channels: Bernanke-Blanchard (2023) channels, 2021-23 vs now (Q1) - lead-exhibit candidate',
           'Data only. Each row is one channel of the Bernanke-Blanchard model. "Then" = 2021-23 peak (current data vintage); "Now" = latest reading, linked live to the research tab that computes it. Paper references give figure/table/page.',
           'Paper: Bernanke & Blanchard, "What Caused the U.S. Pandemic-Era Inflation?", NBER WP 31417 (June 2023), saved PDF in 02_Research/External_views/Literature/. Channels text: outputs/A_q1_bb_channels.csv; quotes: A_q1_bb_quotes.md.')
    # V/U block first (col L onwards) so we can link
    ms = months('2018-01', '2026-09')

    def vu(m, r):
        a, b_ = S['openings'].get(m), S['unemployed'].get(m)
        if a is None or b_ is None:
            return None
        return (f'=raw_monthly!{CL(MCOL["openings"])}{MROW[m]}/raw_monthly!{CL(MCOL["unemployed"])}{MROW[m]}', a / b_)
    c0 = 12
    first, last, cols, rows, vals = monthly_block(ws, 30, c0, ['openings', 'unemployed', 'unrate'], ['Job openings (thous.)', 'Unemployed (thous.)', 'Unemployment rate %'],
                                                  S, ST, MROW, MCOL, ms, 'V/U monthly (live formulas over raw_monthly)',
                                                  extra=[('V/U', vu), ('BB assumed benchmark 1.2', lambda m, r: ('=1.2', 1.2))])
    vspec = [('V/U (JTSJOL / UNEMPLOY)', cols['V/U'], vals['V/U'], rows, '2026-09'), ('Unemployment rate %', cols['unrate'], vals['unrate'], rows, '2026-09')]
    VS = stat_block(ws, 8, c0, None, None, vspec, 'V/U summary (live formulas over the monthly block below)')
    A = json.load(open(os.path.join(OUT, 'A_q1_vu_summary.json')))
    KEYCELLS.update({'vu': f'BB_channels!{CL(c0 + 1)}{VS["V/U (JTSJOL / UNEMPLOY)"]}', 'vu_1819': f'BB_channels!{CL(c0 + 3)}{VS["V/U (JTSJOL / UNEMPLOY)"]}',
                     'vu_peak': f'BB_channels!{CL(c0 + 4)}{VS["V/U (JTSJOL / UNEMPLOY)"]}'})
    SEMANTIC.append(('BB_channels', KEYCELLS['vu'].split('!')[1], 1.0582, 0.0006, 'A_q1_vu Sep 2026 1.06'))
    SEMANTIC.append(('BB_channels', KEYCELLS['vu_peak'].split('!')[1], 2.0390, 0.0006, 'A_q1_vu peak 2022-03 2.04'))
    # channel table
    hdr_row(ws, 5, 1, ['Channel', 'What it means (plain language)', 'Bernanke-Blanchard evidence for 2021-23 (fig/table/page)', 'Measure used here', 'Then: 2021-23 peak',
                       '2018-19 avg', 'Now', 'Now period', 'Where it is computed'], [26, 40, 55, 30, 10, 10, 10, 12, 24])
    BBR = {x['channel']: x for x in rd('A_q1_bb_channels.csv')}
    rowsdef = [
        ('Labor-market tightness (V/U)', 'More job openings per unemployed worker -> faster wage growth (wage Phillips curve).',
         BBR['Labor-market tightness (V/U)']['bb_role_in_2021_23'], 'V/U = JTSJOL / UNEMPLOY (monthly SA)', 'vu'),
        ('Short-run expectations: households', 'What people expect inflation to be over the next year; in BB it moves with recent inflation.',
         BBR['Short-run inflation expectations']['bb_role_in_2021_23'], 'Michigan 1y median', 'mich1'),
        ('Short-run expectations: households (NY Fed)', 'Same concept, different survey.', 'BB use the Cleveland Fed model 1y series; NY Fed SCE shown as the household survey.', 'NY Fed SCE 1y median', 'sce1'),
        ('Long-run expectations: households', 'Expected inflation 5-10 years ahead; in BB it barely moves with recent inflation (anchored).',
         BBR['Long-run inflation expectations']['bb_role_in_2021_23'], 'Michigan 5-10y median. CAUTION: Michigan moved phone -> web in 2024; then-vs-now straddles the mode break (web-era Jun 2025 = 4.0 matched the mid-2022 peak). Not comparable.', 'mich510'),
        ('Long-run expectations: markets', 'Inflation compensation priced in Treasury markets for years 6-10.', 'Not in BB (they use Cleveland 10y); market lens added here.', '5y5y forward (T5YIFR, monthly avg)', 'fwd55'),
        ('Wages (nominal wage growth)', 'How fast pay is rising; feeds prices via unit labor costs.', BBR['Nominal wage growth (endogenous)']['bb_role_in_2021_23'],
         'ECI wages & salaries, private, y/y', 'eci_yoy'),
        ('Wage-to-price pass-through: unit labor costs', 'Wage cost per unit of output (wages adjusted for productivity).',
         BBR['Productivity trend / unit labor costs (wage-to-price pass-through)']['bb_role_in_2021_23'], 'Nonfarm business ULC y/y', 'ulc_yoy'),
        ('Wage-to-price pass-through: ULC 8q', 'Same, smoothed over two years.', 'BB use 8-quarter productivity smoothing (p.12).', 'Nonfarm business ULC 8q ann.', 'ulc_8q'),
        ('Catch-up (wages catching up to past inflation)', 'Workers recouping real-wage losses from inflation that surprised them.',
         BBR['Catch-up (wage response to past unexpected inflation)']['bb_role_in_2021_23'], 'Proxy: NFIB net % planning to raise compensation (survey)', 'nfib_comp_plan'),
    ]
    for i, (ch, plain, ev, meas, key) in enumerate(rowsdef):
        r = 6 + i
        text_cell(ws, r, 1, ch, bold=True)
        text_cell(ws, r, 2, plain)
        text_cell(ws, r, 3, ev)
        text_cell(ws, r, 4, meas)
        sheet, cell = KEYCELLS[key].split('!')
        for col, suf in ((5, '_peak'), (6, '_1819'), (7, '')):
            kk = key + suf
            if kk in KEYCELLS:
                sh, cc = KEYCELLS[kk].split('!')
                put(ws, r, col, f'={sh}!{cc}', F2, expect=CELLVAL.get((sh, cc), CONST.get((sh, cc))), fill=FILL_KEY if col == 7 else None)
        per = {'vu': 'Sep 2026', 'mich1': 'Nov 2026 prelim', 'sce1': 'Oct 2026', 'mich510': 'Nov 2026 prelim', 'fwd55': 'Oct 2026 avg', 'eci_yoy': '2026Q3',
               'ulc_yoy': '2026Q3', 'ulc_8q': '2026Q3', 'nfib_comp_plan': 'Oct 2026'}[key]
        put(ws, r, 8, per)
        put(ws, r, 9, f'{sheet}!{cell}')
        ws.row_dimensions[r].height = 75
    r = 6 + len(rowsdef)
    for ch, txt in (('Energy and food relative-price shocks', BBR['Energy relative price shock']['value_2021_23'] + ' "Now": not recomputed on the BB construction in this run; slide 2 (PPI_stages, Attribution) covers the 2026 energy shock.'),
                    ('Sectoral shortages', BBR['Sectoral shortages']['value_2021_23'] + ' "Now": not pulled (outside the agents\' briefs).'),
                    ('BB conditional projections', 'V/U held near 1.8 -> inflation slowly rising; V/U 1.2 -> CPI about 2.7%; V/U 0.8 -> about 2% (Fig 14, p.38). "conditional projections, not unconditional forecasts" (p.36). CPI-based.')):
        text_cell(ws, r, 1, ch, bold=True)
        text_cell(ws, r, 2, txt)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=9)
        ws.row_dimensions[r].height = 45
        r += 1
    text_cell(ws, r, 1, 'Key BB estimates', bold=True)
    text_cell(ws, r, 2, 'Wage equation (Table 2, p.17): V/U lag sum 0.693 (p=0.030); catch-up -0.024 (p=0.765), i.e. no catch-up effect in 1990-2019 data. Price equation (Table 3, p.24): energy 0.066, "some second-round price-price effects" (p.25). Short-run expectations (Table 4): inflation coefficient 0.124 pre-covid / 0.133 full. Long-run (Table 5): 0.025 / 0.031. Conclusion (p.40): "labor-market balance should ultimately be the primary concern". No citation of Reis (2021) or state-dependent pricing anywhere in the paper.')
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=9)
    ws.row_dimensions[r].height = 75
    line_chart(ws, first, last, [c0 + 4, c0 + 5], [RED, GREY], 'Labor-market tightness: job openings per unemployed worker (V/U)', 'Ratio',
               'Source: BLS JOLTS (JTSJOL) / CPS (UNEMPLOY) via FRED, SA; Sep 2026 latest (Oct 2025 CPS missing: shutdown). Dashed = 1.2, BB\'s ASSUMED steady-state benchmark (its 2019Q4 value; not tightly estimated, BB p.36).',
               'S5', dashes={c0 + 5: 'dash'}, yfmt='0.0', cat_col=c0)


def build_time(ws, P, PROW, POL):
    header(ws, 'Time_above_target: how long has inflation been above 2%? And the 2020-26 policy timeline (Q8)',
           'Data only. Headline and core PCE 12-month inflation computed live from index levels; flag = 1 when above 2.0%; run = consecutive months above 2.0%. Policy: every FOMC target-range change Mar 2020 - Oct 2026.',
           'Units: % (12m change of PCEPI/PCEPILFE, SA, BEA vintage Oct 29, 2026; Oct 2026 = UMD estimate, yellow). Fed funds upper bound: month-end (FRED DFEDTARU). CPI cross-check in outputs/C_q8_time_above_summary.csv.')
    ms = months('2019-01', '2026-10')
    r0 = 6
    section(ws, r0 - 1, 'A. Monthly (live formulas over raw_PCE_index)')
    hdr_row(ws, r0, 1, ['Month', 'Headline PCE 12m %', 'Core PCE 12m %', 'Headline > 2.0 (1/0)', 'Core > 2.0 (1/0)', 'Headline run (months)', 'Core run (months)', 'Fed funds upper bound %', '2% line'],
            [12, 12, 12, 11, 11, 12, 12, 12, 8])
    runs = {'h': 0, 'c': 0}
    R = {}
    for i, m in enumerate(ms):
        r = r0 + 1 + i
        R[m] = r
        est = m == '2026-10'
        put(ws, r, 1, m + (' est.' if est else ''), fill=FILL_EST if est else None)
        h = (P['pce'][m] / P['pce'][shift(m, 12)] - 1) * 100
        c = (P['core'][m] / P['core'][shift(m, 12)] - 1) * 100
        put(ws, r, 2, f'=(raw_PCE_index!B{PROW[m]}/raw_PCE_index!B{PROW[shift(m, 12)]}-1)*100', F2, expect=h, fill=FILL_EST if est else None)
        put(ws, r, 3, f'=(raw_PCE_index!C{PROW[m]}/raw_PCE_index!C{PROW[shift(m, 12)]}-1)*100', F2, expect=c, fill=FILL_EST if est else None)
        put(ws, r, 4, f'=IF(B{r}>2,1,0)', expect=1 if h > 2 else 0)
        put(ws, r, 5, f'=IF(C{r}>2,1,0)', expect=1 if c > 2 else 0)
        runs['h'] = runs['h'] + 1 if h > 2 else 0
        runs['c'] = runs['c'] + 1 if c > 2 else 0
        if i == 0:
            put(ws, r, 6, f'=D{r}', expect=runs['h'])
            put(ws, r, 7, f'=E{r}', expect=runs['c'])
        else:
            put(ws, r, 6, f'=IF(D{r}=1,F{r - 1}+1,0)', expect=runs['h'])
            put(ws, r, 7, f'=IF(E{r}=1,G{r - 1}+1,0)', expect=runs['c'])
        if P['ffu'].get(m) is not None:
            put(ws, r, 8, f'=raw_PCE_index!D{PROW[m]}', F2, expect=P['ffu'][m])
        put(ws, r, 9, '=2', expect=2.0)
    last = r0 + len(ms)
    # summary at K
    k0 = 11
    ws.cell(row=5, column=k0, value='B. Summary (live formulas over block A)').font = Font(bold=True, size=12, color=b1.NAVY)
    hdr_row(ws, 6, k0, ['Item', 'Headline PCE', 'Core PCE'], [52, 14, 14])
    rs, ro = R['2026-09'], R['2026-10']
    hv = {m: (P['pce'][m] / P['pce'][shift(m, 12)] - 1) * 100 for m in ms}
    cv = {m: (P['core'][m] / P['core'][shift(m, 12)] - 1) * 100 for m in ms}

    def run_at(v, m):
        n = 0
        for x in ms[:ms.index(m) + 1]:
            n = n + 1 if v[x] > 2 else 0
        return n
    items = [('Consecutive months above 2.0% through Sep 2026', f'=F{rs}', f'=G{rs}', run_at(hv, '2026-09'), run_at(cv, '2026-09'), '0'),
             ('Years above 2.0% through Sep 2026', f'=F{rs}/12', f'=G{rs}/12', run_at(hv, '2026-09') / 12, run_at(cv, '2026-09') / 12, '0.00'),
             ('Consecutive months above 2.0% through Oct 2026 (est.)', f'=F{ro}', f'=G{ro}', run_at(hv, '2026-10'), run_at(cv, '2026-10'), '0'),
             ('Years above 2.0% through Oct 2026 (est.)', f'=F{ro}/12', f'=G{ro}/12', run_at(hv, '2026-10') / 12, run_at(cv, '2026-10') / 12, '0.00'),
             ('Lowest 12m reading inside the current run (since Mar 2021)', f'=MIN(B{R["2021-03"]}:B{rs})', f'=MIN(C{R["2021-03"]}:C{rs})',
              min(hv[m] for m in ms if '2021-03' <= m <= '2026-09'), min(cv[m] for m in ms if '2021-03' <= m <= '2026-09'), F3),
             ('Feb 2021 12m (last month at or below 2.0%)', f'=B{R["2021-02"]}', f'=C{R["2021-02"]}', hv['2021-02'], cv['2021-02'], F3),
             ('Sep 2026 12m', f'=B{rs}', f'=C{rs}', hv['2026-09'], cv['2026-09'], F3)]
    TS = {}
    for i, (lbl, fh, fc, eh, ec, fmt) in enumerate(items):
        r = 7 + i
        text_cell(ws, r, k0, lbl)
        put(ws, r, k0 + 1, fh, fmt, expect=eh, fill=FILL_KEY if i < 2 else None)
        put(ws, r, k0 + 2, fc, fmt, expect=ec, fill=FILL_KEY if i < 2 else None)
        TS[lbl] = r
    KEYCELLS.update({'run_months': f'Time_above_target!M{TS["Consecutive months above 2.0% through Sep 2026"]}', 'run_years': f'Time_above_target!M{TS["Years above 2.0% through Sep 2026"]}'})
    SEMANTIC.append(('Time_above_target', f'L{TS["Consecutive months above 2.0% through Sep 2026"]}', 67, 0.0, 'C_q8 headline run 67'))
    SEMANTIC.append(('Time_above_target', f'M{TS["Consecutive months above 2.0% through Sep 2026"]}', 67, 0.0, 'C_q8 core run 67'))
    SEMANTIC.append(('Time_above_target', f'M{TS["Consecutive months above 2.0% through Oct 2026 (est.)"]}', 68, 0.0, 'C_q8 core run Oct est 68'))
    r = 7 + len(items) + 1
    text_cell(ws, r, k0, 'Six years would be reached in Mar 2027 (both measures). CPI: headline run 67 months, core CPI 66 (outputs/C_q8_time_above_summary.csv). Vintage: core PCE Mar 2021 was 1.83 as first published (run would start Apr 2021 on that vintage).')
    ws.merge_cells(start_row=r, start_column=k0, end_row=r, end_column=k0 + 2)
    ws.row_dimensions[r].height = 60
    # policy table at K
    p0 = r + 3
    ws.cell(row=p0 - 1, column=k0, value='C. FOMC target-range changes, Mar 2020 - Oct 2026 (live references to raw_policy)').font = Font(bold=True, size=12, color=b1.NAVY)
    hdr_row(ws, p0, k0, ['Statement date', 'Action', 'Change (bp)', 'Lower %', 'Upper %', 'Vote'], [52, 14, 14, 10, 10, 10])
    for i, x in enumerate(POL):
        r = p0 + 1 + i
        rr = 7 + i
        put(ws, r, k0, f'=raw_policy!A{rr}', expect=x['date'])
        put(ws, r, k0 + 1, f'=raw_policy!C{rr}', expect=x['action'])
        if num(x['change_bp']) is not None:
            put(ws, r, k0 + 2, f'=raw_policy!D{rr}', '0', expect=num(x['change_bp']))
            put(ws, r, k0 + 3, f'=raw_policy!E{rr}', F2, expect=num(x['lower']))
            put(ws, r, k0 + 4, f'=raw_policy!F{rr}', F2, expect=num(x['upper']))
        if x['vote']:
            put(ws, r, k0 + 5, f'=raw_policy!G{rr}', expect=x['vote'])
    line_chart(ws, r0 + 1, last, [2, 3, 8, 9], [RED, BLUE, GREY, BLACK], 'PCE inflation (12-month) and the fed funds target, 2019 to Oct 2026 est.', '%',
               'Source: BEA PCEPI/PCEPILFE (Oct 29 release; Oct = UMD est.); FRED DFEDTARU (month-end upper bound). Dashed = 2% target.',
               'R5', dashes={9: 'dash', 8: 'sysDot'})


def build_worthiness(ws):
    header(ws, 'Slide_worthiness: how strong a slide story each candidate exhibit makes (agents\', stress test and coordinator ratings side by side)',
           'Ratings 1-5 (5 = strongest). Data plus a rating; not a slide design. Eli decides what goes on the slide.',
           'Source: report_A.md ... report_D.md "Slide-worthiness" sections; coordinator column from FINAL.md section 3. File: outputs/Z_slide_worthiness.csv.')
    X = rd('Z_slide_worthiness.csv')
    cols = list(X[0].keys())
    hdr_row(ws, 5, 1, cols, [34, 10, 12, 14, 14, 80])
    for k, x in enumerate(X):
        for j, c in enumerate(cols):
            v = num(x[c]) if c.endswith('rating') else None
            cell = put(ws, 6 + k, 1 + j, v if v is not None else x[c])
            cell.alignment = WRAP


SOURCES = [
    ('BB_channels', 'raw_monthly', '03_Data/Raw/S3A_A_vu_2026-11-15/FRED_JTSJOL_observations_2026-11-15.json; FRED_UNEMPLOY_observations_2026-11-15.json; FRED_UNRATE_observations_2026-11-15.json; outputs/A_q1_vu.csv; outputs/A_q1_bb_channels.csv; 02_Research/External_views/Literature/2023_Bernanke_Blanchard_pandemic_inflation_NBER_w31417.pdf',
     'https://fred.stlouisfed.org/series/JTSJOL ; https://www.nber.org/papers/w31417', 'JOLTS Sep 2026 (Nov 3); CPS Oct 2026 (Nov 6)'),
    ('Wages_ULC', 'raw_quarterly, raw_monthly', '03_Data/pipelines/inflation_data/raw/bls/bls_api_all_series_*_2026-11-10.json (ECI); 03_Data/Raw/S3A_B_labor_costs_2026-11-15/bls_api_productivity_costs_2008-2026_2026-11-15.json; bls_api_ces_ahe_2016-2026_2026-11-15.json; atlantafed_wage-growth-data_2026-11-15.xlsx; outputs/B_q3_*.csv',
     'https://api.bls.gov/publicAPI/v2/timeseries/data/ ; https://www.atlantafed.org/chcs/wage-growth-tracker', 'ECI Oct 30; P&C Nov 5; AHE Nov 6; WGT Oct 8'),
    ('Wages_ULC (labor share vintages)', '(script values)', '03_Data/Raw/S3A_B_labor_costs_2026-11-15/alfred_PRS85006173_vintages_2026-11-15.json; outputs/B_q3_labor_share.md', 'https://alfred.stlouisfed.org/series?seid=PRS85006173', 'ALFRED pulled 2026-11-15'),
    ('Expectations', 'raw_monthly', '03_Data/pipelines/inflation_data/raw/fed_expectations/umich_* (2026-11-10); 03_Data/Raw/S3A_expectations_underlying_2026-11-15/NYFed_SCE_chart_data_2026-11-15.xlsx; FRED_T5YIE/T10YIE/T5YIFR/GASREGW_2026-11-15.json; outputs/C_q4_*.csv',
     'https://www.sca.isr.umich.edu ; https://www.newyorkfed.org/microeconomics/sce ; https://fred.stlouisfed.org', 'Michigan Nov prelim (Nov 6); SCE Oct (Nov 9); FRED to Nov 13'),
    ('Expectations (SPF)', '(script values)', '03_Data/pipelines/inflation_data/raw/fed_expectations/ (SPF median files); outputs/C_q4_summary.csv; PhillyFed_SPF_landing_recheck_2026-11-15.html (Q4 not out)', 'https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters', 'Q3 2026 (Aug 14)'),
    ('Expectations (Logan aggregate)', '(script values)', '03_Data/pipelines/inflation_data/Inflation_Expectations.xlsx (raw/expectations_aggregate/, Nov 14); outputs/C_q4_logan_aggregate.csv', 'n/a', 'build 2026-11-14'),
    ('Underlying_trend', 'raw_monthly, raw_PCE_index', '03_Data/Raw/S3A_expectations_underlying_2026-11-15/NYFed_MCT_chart_data_2026-11-15.csv; FRED_PCETRIM*_2026-11-15.json; ClevelandFed_median_PCE_full_history_2026-11-15.csv; ClevelandFed_mediancpi_*.csv; 03_Data/pipelines/inflation_data/processed/bea/observations.csv; 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404/U20405_2026-11-10.json; 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv; outputs/C_q6_*.csv',
     'https://www.newyorkfed.org/research/policy/mct ; https://www.dallasfed.org/research/pce ; https://www.clevelandfed.org/indicators-and-data/median-pce-inflation ; https://apps.bea.gov/api', 'MCT Oct 30; BEA Oct 29; Oct = UMD est. (Nov 13)'),
    ('Underlying_trend (Logan quote)', '(quote)', '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Logan_economic_monetary_policy_outlook.html', 'https://www.dallasfed.org/news/speeches/logan/2026/lkl261110', 'Nov 10, 2026'),
    ('Catch_up', 'raw_monthly', '03_Data/Raw/S3A_B_labor_costs_2026-11-15/nfib_SBET-Report-October-2026_2026-11-15.pdf; nfib_SBET-Dec-2020_via-wayback_2026-11-15.pdf; 03_Data/pipelines/inflation_data/raw/expectations_aggregate/atlantafed_bie-data_2026-11-14.xlsx; richmondfed_*_2026-11-14.*; fed_beigebook202610_2026-11-15.html; outputs/B_q5_*.csv',
     'https://www.nfib.com/sbet/ ; https://www.atlantafed.org/research/inflationproject/bie ; https://www.richmondfed.org/research/regional_economy/surveys_of_business_conditions', 'NFIB Oct 2026; BIE Oct; Richmond Oct; Beige Book Oct 14'),
    ('Time_above_target', 'raw_PCE_index, raw_policy', '03_Data/Raw/S3A_expectations_underlying_2026-11-15/FRED_PCEPI/PCEPILFE/DFEDTARU/DFEDTARL_2026-11-15.json; FRB_openmarket_2026-11-15.htm; 03_Data/Raw/S3A_fomc_statements_2026-11-15/; outputs/C_q8_*.csv',
     'https://fred.stlouisfed.org/series/PCEPI ; https://www.federalreserve.gov/monetarypolicy/openmarket.htm', 'BEA Oct 29; FRED Nov 15'),
    ('Trimmed-mean bias (Q2; FINAL.md)', '(texts)', '03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/; outputs/A_q2_trimmed_bias.md; 02_Research/Subtasks/10_slide2_research/outputs/D_trimmed_*.csv', 'https://www.dallasfed.org/research/economics/2026/0416 ; https://www.dallasfed.org/research/economics/2026/0813', 'Apr 16 and Aug 13, 2026'),
    ('Pace wording (Q7; FINAL.md)', '(texts)', '02_Research/External_views/Previous_Finalists_copy/2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf; outputs/A_q7_pace_quotes.md', 'n/a', 'Nov 21, 2025 transcript'),
    ('Stress test (Q9; FINAL.md)', '(text)', 'outputs/D_qa_prep.md; D_bridge_line_check.md; D_verbal_cues.md', 'n/a', 'Nov 15, 2026'),
]


def build_sources(ws):
    header(ws, 'Sources: every raw file and URL behind each tab', 'One row per raw input. Paths relative to the project root; outputs/ = 02_Research/Subtasks/11_slide3a_research/outputs/.',
           'All files are saved locally; nothing in this workbook depends on a live link. Per-agent source lists: sources_A.md ... sources_D.md.')
    hdr_row(ws, 5, 1, ['Research tab(s)', 'Raw tab', 'File(s)', 'URL', 'Vintage'], [30, 22, 100, 60, 30])
    for i, row in enumerate(SOURCES):
        for j, v in enumerate(row):
            text_cell(ws, 6 + i, 1 + j, v)
    ws.freeze_panes = 'A6'


def build_needs(ws):
    header(ws, 'Judgment calls for Eli and scope/deliverable deviations (both positions), and paywalled links',
           'Items for Eli to decide or fetch, ordered by how much each blocks the slide. Copied from FINAL.md section 6 via outputs/Z_judgment_calls.csv.', 'Paywalled lists: outputs/A_paywalled.csv, B_paywalled.csv, C_paywalled.csv, D_paywalled.csv.')
    hdr_row(ws, 5, 1, ['#', 'Item', 'Claude', 'Other position (agent / Codex)', 'Affects tab', 'Status'], [5, 50, 55, 55, 22, 30])
    rr = 6
    for x in rd('Z_judgment_calls.csv'):
        for j, k in enumerate(['id', 'item', 'position_a', 'position_b', 'tab', 'status']):
            text_cell(ws, rr, 1 + j, x[k])
        rr += 1
    rr += 1
    section(ws, rr, 'Paywalled or blocked links (not accessed)')
    rr += 1
    hdr_row(ws, rr, 1, ['#', 'URL', 'Agent', 'What it would add / status'])
    k = 0
    for fname in ('A_paywalled.csv', 'B_paywalled.csv', 'C_paywalled.csv', 'D_paywalled.csv'):
        p = os.path.join(OUT, fname)
        if not os.path.exists(p):
            continue
        for x in rd(fname):
            k += 1
            rr += 1
            url = x.get('url', x.get('URL', ''))
            what = '; '.join(f'{a}: {b}' for a, b in x.items() if a not in ('url', 'URL') and b)
            for j, v in enumerate([k, url, fname[0], what]):
                text_cell(ws, rr, 1 + j, v)


DESCR = {
    'READING_GUIDE': 'Start here: what each tab answers, how to read each column and chart, the numbers to look at first, and a glossary.',
    'BB_channels': 'Lead-exhibit candidate: Bernanke-Blanchard channels, 2021-23 peak vs 2018-19 vs now, each linked to the tab that computes it; V/U chart.',
    'Wages_ULC': 'Wages (ECI, AHE, Atlanta tracker) vs the 2%-consistent benchmark; ULC 4q/8q; labor share; productivity; 3 charts.',
    'Expectations': 'Short- vs long-run expectations (households, professionals, markets); gas co-movement; SPF; Logan aggregate; 4 charts.',
    'Underlying_trend': 'MCT, trimmed mean, median PCE, market-based core, Logan measure, supercore; roadmap number check; 2 charts.',
    'Catch_up': 'Survey evidence of catch-up: NFIB, Atlanta Fed BIE, Richmond Fed, CFO survey, Conference Board, Beige Book; 2 charts.',
    'Time_above_target': 'Months above 2% (headline and core PCE), live run counter; 2020-26 FOMC rate changes; 1 chart.',
    'Slide_worthiness': 'Agent, stress-test and coordinator ratings of each candidate exhibit.',
    'Sources': 'Every raw file and URL behind each tab.',
    'Judgment_calls_and_paywalled': 'Judgment calls for Eli (both positions), ordered by how much they block the slide; paywalled links.',
}


def build_readme(ws, order, raws):
    header(ws, 'Slide 3A data workbook: "Is the first round turning into a second round?"',
           'Research data for slide 3A of the UMD finals inflation section. Evidence only; no policy recommendation (that belongs to the decision section).',
           f'Built {BUILD_DATE} by {SCRIPT}. Vintages: BEA PCE Oct 29 (through Sep 2026); Oct 2026 PCE = UMD estimate (Nov 13); BLS P&C Nov 5; ECI Oct 30; JOLTS Nov 3; Michigan Nov prelim; SCE Nov 9. Data cutoff Nov 18, 2026.')
    rr = 5
    section(ws, rr, 'How to rebuild')
    rr += 1
    ws.cell(row=rr, column=1, value=f'From the project root:  python3 -I "02_Research/Subtasks/{SCRIPT}" --verify   (fix inputs in 11_slide3a_research/outputs/ or raw files, never this xlsx, until Eli hand-edits it)')
    rr += 2
    section(ws, rr, 'Label key')
    for lbl, fill, txt in (('est. / prelim', FILL_EST, 'UMD estimate (October PCE build; BEA publishes Oct PCE Nov 25) or a preliminary/partial reading (Michigan Nov prelim; AHE Oct prelim; Nov gas/breakevens partial month). Cell notes say which.'),
                           ('key figure', FILL_KEY, 'figure most likely to be cited')):
        rr += 1
        c = ws.cell(row=rr, column=1, value=lbl)
        c.fill = fill
        c.font = F_BOLD
        ws.cell(row=rr, column=2, value=txt)
    rr += 2
    section(ws, rr, 'Contents (click to jump)')
    rr += 1
    hdr_row(ws, rr, 1, ['Tab', 'What it shows'], [28, 130])
    for n in order + raws:
        if n == 'README':
            continue
        rr += 1
        c = ws.cell(row=rr, column=1, value=n)
        c.hyperlink = f"#'{n}'!A1"
        c.font = Font(color='0563C1', underline='single')
        ws.cell(row=rr, column=2, value=DESCR.get(n, 'raw data (grey tab): source file path, URL, vintage and notes in rows 2-5'))
    rr += 2
    section(ws, rr, 'Conventions')
    for t in ('Live formulas wherever practical: click a cell to trace it to a raw tab. Rates are computed in-sheet from index levels where the levels are on a raw tab (V/U, AHE, ECI, ULC, productivity, hourly comp, PCE 12m, the time-above-target run). Published or agent-derived rates are referenced from raw_monthly.',
              'Every build checks the live values against the agents\' CSVs (semantic check) and, with --verify, recalculates in LibreOffice (0 mismatches, 0 errors required).',
              '"2021-23 peak" = maximum over Jan 2021 - Dec 2023 (2021Q1-2023Q4) in the CURRENT data vintage. "2018-19 avg" = simple average over 2018-2019.',
              'Wording (Eli, binding): "recent momentum has picked up", not "accelerating". Do not claim a change in price-setting behaviour from the FEDS oil note.',
              'Status and audit trail: 02_Research/Subtasks/11_slide3a_research/FINAL.md, report_A.md ... report_D.md, 06_Audits/slide3a_research/.'):
        rr += 1
        c = ws.cell(row=rr, column=1, value=t)
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=2)


# ---------------------------------------------------------------------------- reading guide
def build_guide(ws):
    header(ws, 'READING_GUIDE: how to read this workbook (start here)',
           'For each tab: the question it answers, what the columns mean, how to read the charts, and the 2-3 numbers to look at first (with cells). Glossary at the bottom.',
           'All numbers on this tab are live links to the cells named, so they update on rebuild. Evidence only; no policy recommendation.')
    ws.column_dimensions['A'].width = 24
    ws.column_dimensions['B'].width = 120
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 28
    r = 5

    def para(label, text, bold=False, h=None):
        nonlocal r
        c1 = ws.cell(row=r, column=1, value=label)
        c1.font = F_BOLD if bold or label else c1.font
        c1.alignment = WRAP
        c2 = ws.cell(row=r, column=2, value=text)
        c2.alignment = WRAP
        if h:
            ws.row_dimensions[r].height = h
        r += 1

    def look(label, key):
        nonlocal r
        sh, cc = KEYCELLS[key].split('!')
        ws.cell(row=r, column=1, value='  look at').font = Font(italic=True, color='595959')
        ws.cell(row=r, column=2, value=label).alignment = WRAP
        put(ws, r, 3, f'={sh}!{cc}', F2, expect=CELLVAL.get((sh, cc), CONST.get((sh, cc))), fill=FILL_KEY)
        c = ws.cell(row=r, column=4, value=f'{sh}!{cc}')
        c.hyperlink = f"#'{sh}'!{cc}"
        c.font = Font(color='0563C1', underline='single')
        r += 1

    def tab(name, q, cols, charts, looks):
        nonlocal r
        c = ws.cell(row=r, column=1, value=name)
        c.font = Font(bold=True, size=12, color=b1.NAVY)
        c.hyperlink = f"#'{name}'!A1"
        r += 1
        para('Question', q, h=30)
        para('Columns', cols, h=max(30, 15 * (len(cols) // 110 + 1)))
        para('Charts', charts, h=max(30, 15 * (len(charts) // 110 + 1)))
        for lbl, k in looks:
            look(lbl, k)
        r += 1
    section(ws, r, 'Reading order (suggested): BB_channels -> Underlying_trend -> Expectations -> Wages_ULC. Catch_up and Time_above_target are backup.')
    r += 2
    tab('BB_channels', 'Do the channels that drove 2021-23 inflation in Bernanke-Blanchard (BB) look like they did then? (BB = the 2023 paper that split pandemic inflation into its causes.)',
        'Rows 6-14: one BB channel each. "Then" = the 2021-23 peak of the same series in today\'s data; "2018-19 avg" = the pre-pandemic normal; "Now" = latest reading, a live link to the tab named in column I. '
        'V/U = job openings divided by unemployed workers (labor-market tightness; above 1 means more openings than job seekers). Catch-up = wages rising to recover purchasing power lost to past inflation.',
        'V/U chart (anchored at S5): x = month, y = openings per unemployed worker; up = tighter labor market; dashed line = 1.2, the steady-state V/U that BB ASSUMED for their projections (its 2019Q4 value; they say it is not tightly estimated, and their wage equation has no threshold). Below 1.2 is not "off" and above is not "on".',
        [('V/U now (Sep 2026)', 'vu'), ('V/U 2021-23 peak (Mar 2022)', 'vu_peak'), ('V/U 2018-19 average', 'vu_1819')])
    tab('Underlying_trend', 'Where is underlying (trend) inflation once noisy prices are filtered out, and do the measures agree?',
        'Block A: monthly values of each measure. MCT = NY Fed multivariate core trend (a statistical estimate of trend inflation). Trimmed mean = average after dropping the most extreme price changes each month. '
        'Median PCE = the middle price change. Market-based = excludes prices BEA imputes. Supercore = core services excluding housing. Logan measure = core services excluding housing AND transportation. '
        'Block B: latest, 2018-19 average and 2021-23 peak. Block C: check of each roadmap number against the publisher.',
        'Bar chart (O5): September 2026 readings, low to high; taller bar = higher underlying inflation. Line chart (O29): x = month, y = % 12-month change (MCT = trend); dashed = 2% target; Oct values are UMD estimates for the Logan measure and core PCE.',
        [('Dallas trimmed mean, Sep', 'dal12'), ('NY Fed MCT, Sep', 'mct'), ('Logan measure 12m, Sep', 'logan12'), ('Logan measure 3m ann., Oct est.', 'logan3_oct')])
    tab('Expectations', 'Are inflation expectations rising, and is it only short-run household expectations following gas prices?',
        'Block A: monthly. Michigan and NY Fed SCE are household surveys (median expected inflation). Breakevens = inflation compensation priced in Treasury bonds (includes risk premia). '
        '5y5y forward = expected average inflation 5-10 years ahead from market prices. Block B: latest vs 2018-19 and 2021-23. Block C: SPF (professional forecasters). '
        'Block D: correlation of 12-month changes in each series with 12-month % changes in gasoline prices (+1 = move together, 0 = unrelated; descriptive only).',
        'Short-run chart (L5) and long-run chart (L29): x = month, y = expected inflation %; up = higher expected inflation; dashed = 2%. Gas chart (L55): $/gallon. Correlation bar chart (L82): one bar per window; taller = closer co-movement with gas.',
        [('Michigan 1y, Nov prelim', 'mich1'), ('Michigan 5-10y, Nov prelim (do not compare with 2021-23: 2024 phone-to-web mode break)', 'mich510'), ('5y5y forward, Oct avg', 'fwd55')])
    tab('Wages_ULC', 'Are labor costs growing faster than 2% inflation allows?',
        'Block A (quarterly): ECI = Employment Cost Index (pay per hour for a fixed mix of jobs); ULC = unit labor costs (hourly compensation divided by output per hour, i.e. wages net of productivity); '
        '8q ann. = two-year change, annualized (smoother); labor share = workers\' share of business output. Block B (monthly): AHE = average hourly earnings; WGT = Atlanta Fed wage growth tracker (median wage growth of the same people a year apart). '
        'Block C: benchmark = 2% + trend productivity growth (wage growth that is consistent with 2% inflation if margins are stable). Block D: latest vs 2018-19 vs 2021-23.',
        'Wage chart (AE5): x = month, y = % wage growth; dashed = 3.52% benchmark; above the line = faster than 2%-consistent. ULC chart (AE29): x = quarter; dashed = 2%. Labor-share chart (AE53): % of output; down = workers\' share falling.',
        [('ECI wages & salaries y/y, 2026Q3', 'eci_yoy'), ('2%-consistent wage benchmark', 'bench'), ('ULC 8q annualized, 2026Q3', 'ulc_8q'), ('Labor share level %, 2026Q3', 'ls_lvl')])
    tab('Catch_up', 'Do firms report plans to catch wages and prices up? (survey and anecdotal evidence only)',
        'Block A: monthly survey series. NFIB = National Federation of Independent Business; "net %" = share of owners raising minus share lowering. BIE = Atlanta Fed Business Inflation Expectations (mean % unit-cost change). '
        'Richmond = Richmond Fed diffusion index (% reporting higher wages minus % lower). Block C: CFO survey, Conference Board, Beige Book, and the check of Eli\'s podcast figures.',
        'NFIB chart (K5): planned increases only (next 3 months): x = month, y = net % of owners; up = more firms planning increases. Realized (last 3 months) series are in block A columns D-E, not charted. BIE chart (K29): %; dashed = expected year ahead.',
        [('NFIB net % planning to raise compensation, Oct', 'nfib_comp_plan'), ('NFIB net % planning to raise prices, Oct', 'nfib_px_plan')])
    tab('Time_above_target', 'Is "nearly six years above 2%" accurate, and what has policy done since 2020?',
        'Block A: 12-month headline and core PCE inflation computed from index levels; flag = 1 if above 2.0%; run = consecutive months above 2.0% (resets to 0 when a month is at or below 2.0%). Block B: run length and the lowest reading inside the run. Block C: every FOMC target-range change.',
        'Chart (R5): x = month; red/blue = headline/core PCE 12m %; grey dotted = fed funds target upper bound; dashed = 2%.',
        [('Core PCE: consecutive months above 2% through Sep 2026', 'run_months'), ('... in years', 'run_years')])
    para('Slide_worthiness', 'Ratings 1-5 from each agent, the stress test (D) and the coordinator. Data plus a rating; Eli decides.', bold=True)
    para('Sources', 'Every raw file and URL behind each tab.', bold=True)
    para('Judgment_calls_and_paywalled', 'Judgment calls for Eli with both positions, ordered by how much they block the slide.', bold=True)
    para('raw_ tabs (grey)', 'raw_monthly, raw_quarterly, raw_PCE_index, raw_policy: the series behind every formula. Rows 2-5 give source file, vintage and URL.', bold=True)
    r += 1
    section(ws, r, 'Glossary (every term and abbreviation used)')
    r += 1
    for term, d in GLOSSARY:
        ws.cell(row=r, column=1, value=term).font = F_BOLD
        c = ws.cell(row=r, column=2, value=d)
        c.alignment = WRAP
        r += 1


GLOSSARY = [
    ('First round / second round', 'First round: the direct and indirect price effects of a shock (e.g. oil feeding into fuel, then airfares). Second round: those price increases feeding into wages, expectations and price-setting, so inflation persists after the shock fades.'),
    ('BB', 'Bernanke & Blanchard (2023), NBER WP 31417: model splitting 2021-23 US inflation into energy, food, shortages, labor-market tightness and expectations.'),
    ('V/U', 'Job openings (JOLTS) divided by unemployed workers (CPS). Measures labor-market tightness. BB ASSUME 1.2 (its 2019Q4 value) as the steady-state level in their projections; it is not tightly estimated (p.36, fn 16), and the effect of V/U on wages is continuous, not a threshold.'),
    ('JOLTS / CPS', 'Job Openings and Labor Turnover Survey (BLS) / Current Population Survey (household survey behind the unemployment rate).'),
    ('Catch-up', 'Wage growth that responds to past inflation that was higher than expected, as workers try to restore real wages. BB estimate it at about zero before 2020.'),
    ('ECI', 'Employment Cost Index (BLS): cost of labor per hour for a fixed mix of jobs, so not distorted by shifts in who is employed. W&S = wages and salaries; total comp adds benefits.'),
    ('AHE', 'Average hourly earnings (BLS payroll survey). Affected by changes in the mix of jobs.'),
    ('WGT', 'Atlanta Fed Wage Growth Tracker: median 12-month wage growth of the same individuals; 3mma = 3-month moving average. Job switchers vs stayers shown separately.'),
    ('ULC', 'Unit labor costs = hourly compensation / output per hour. Labor cost per unit of output; strips productivity out of wage growth.'),
    ('Labor share', 'Share of nonfarm business output paid to workers (compensation / nominal output). BLS PRS85006174 (level, %) and PRS85006173 (index).'),
    ('Trend productivity', 'Average growth of output per hour over a long period (here 2007Q4-2019Q4, 1.52%/yr). Benchmark wage growth = 2% + trend productivity.'),
    ('y/y, 12m', 'Change over the past 12 months (4 quarters).'),
    ('3m ann., 6m ann.', 'Change over 3 or 6 months, converted to an annual rate (compounded).'),
    ('8q ann.', 'Change over 8 quarters (2 years), annualized.'),
    ('q/q ann.', 'Change from the previous quarter, annualized.'),
    ('SA / NSA', 'Seasonally adjusted / not seasonally adjusted.'),
    ('PCE, core PCE', 'Personal consumption expenditures price index (BEA), the Fed\'s target measure; core excludes food and energy.'),
    ('Supercore', 'PCE services excluding energy and housing.'),
    ('Logan measure', 'PCE core services excluding housing and transportation services (cited by Dallas Fed President Logan, Nov 10). Derived here from BEA lines 376 less 153 less 190.'),
    ('Market-based PCE', 'PCE excluding prices BEA imputes (no observed market transaction), e.g. some financial services.'),
    ('MCT', 'NY Fed Multivariate Core Trend: a statistical model\'s estimate of the current persistent (trend) component of inflation, annualized, from 17 PCE sectors; band = 68% uncertainty range. Not a 12-month-ahead forecast.'),
    ('Trimmed mean (Dallas)', 'Average monthly PCE inflation after dropping the 24% of spending with the lowest and 31% with the highest price changes each month.'),
    ('Median PCE / CPI (Cleveland)', 'The price change at the middle of the spending-weighted distribution each month.'),
    ('Skewness', 'Asymmetry of the distribution of price changes; positive = more large increases than large decreases. Dallas staff find positive skew biases the trimmed mean down.'),
    ('Michigan, SCE', 'University of Michigan Surveys of Consumers; NY Fed Survey of Consumer Expectations. Both report median expected inflation.'),
    ('SPF', 'Philadelphia Fed Survey of Professional Forecasters (quarterly). Q4 2026 due Nov 16.'),
    ('Breakeven', 'Nominal Treasury yield minus TIPS yield at the same maturity: inflation compensation, including risk and liquidity premia.'),
    ('5y5y forward', 'Expected average inflation over the five years starting five years from now, from breakevens (FRED T5YIFR).'),
    ('NFIB', 'National Federation of Independent Business small-business survey. "Net %" = % raising minus % lowering (SA).'),
    ('BIE', 'Atlanta Fed Business Inflation Expectations survey (firms\' unit-cost changes, mean %).'),
    ('Diffusion index', '% of firms reporting an increase minus % reporting a decrease.'),
    ('Beige Book', 'Fed summary of anecdotal reports from the 12 districts (Oct 14, 2026 edition here).'),
    ('est.', 'UMD estimate of October 2026 PCE (audited bottom-up build from CPI and PPI); BEA publishes Oct PCE on Nov 25.'),
    ('prelim', 'Preliminary reading, subject to revision (Michigan Nov final Nov 20; AHE Oct revised with the Nov jobs report).'),
    ('Vintage', 'The release a number comes from. Revised series (e.g. ULC, labor share) change across vintages.'),
    ('FOMC, target range', 'Federal Open Market Committee; the fed funds target range (lower-upper bound). Change in bp = basis points (100 bp = 1 percentage point).'),
    ('QE / QT', 'Quantitative easing (Fed asset purchases) / quantitative tightening (balance-sheet runoff).'),
    ('Pass-through', 'How much a cost change (e.g. oil) shows up in other prices.'),
    ('FEDS oil note', 'De Michelis, Orak, Pradhan & Queralto, FEDS Note, Nov 9, 2026: post-pandemic oil pass-through to core inflation is higher in a 5-economy panel; authors call their projection an upper bound.'),
]


# ============================================================================ main / verify
CELLVAL = EXPECT    # expected values of formula cells, used for cross-tab links


def collect_vals():
    pass


def main(verify=False):
    S, ST, SRC = load_monthly()
    Q = load_quarterly()
    P = load_pce()
    wb = Workbook()
    wb.remove(wb.active)
    order = ['READING_GUIDE', 'README', 'BB_channels', 'Wages_ULC', 'Expectations', 'Underlying_trend', 'Catch_up', 'Time_above_target',
             'Slide_worthiness', 'Sources', 'Judgment_calls_and_paywalled']
    raws = ['raw_monthly', 'raw_quarterly', 'raw_PCE_index', 'raw_policy']
    W = {n: wb.create_sheet(n) for n in order + raws}
    MROW, MCOL = build_raw_monthly(W['raw_monthly'], S, ST, SRC)
    QROW, QCOL = build_raw_quarterly(W['raw_quarterly'], Q)
    PROW = build_raw_pce(W['raw_PCE_index'], P)
    POL = build_raw_policy(W['raw_policy'])
    build_wages(W['Wages_ULC'], Q, QROW, QCOL, S, ST, MROW, MCOL)
    build_expectations(W['Expectations'], S, ST, MROW, MCOL)
    build_underlying(W['Underlying_trend'], S, ST, MROW, MCOL, PROW, P)
    build_catchup(W['Catch_up'], S, ST, MROW, MCOL)
    build_time(W['Time_above_target'], P, PROW, POL)
    collect_vals()
    build_bb(W['BB_channels'], S, ST, MROW, MCOL)
    collect_vals()
    build_worthiness(W['Slide_worthiness'])
    build_sources(W['Sources'])
    build_needs(W['Judgment_calls_and_paywalled'])
    build_readme(W['README'], order, raws)
    build_guide(W['READING_GUIDE'])
    semantic_check()
    os.makedirs(os.path.dirname(XLSX), exist_ok=True)
    wb.save(XLSX)
    print(f'saved {REL(XLSX)}: {len(EXPECT)} formula cells, {len(SEMANTIC)} semantic checks passed')
    chart_xml_check()
    if verify:
        run_verify()


def semantic_check():
    bad = []
    for sh, coord, want, tol, lbl in SEMANTIC:
        got = EXPECT[(sh, coord)]
        if abs(got - want) > max(tol, 1e-9):
            bad.append((sh, coord, lbl, got, want))
    for b in bad:
        print('SEMANTIC MISMATCH', b)
    assert not bad, f'{len(bad)} semantic mismatches'


N_CHARTS = 13


def chart_xml_check():
    import zipfile
    z = zipfile.ZipFile(XLSX)
    n_line = n_bar = 0
    for f in z.namelist():
        if f.startswith('xl/charts/chart'):
            x = re.sub(r'<(/?)c:', r'<\1', z.read(f).decode())
            x = re.sub(r'\s*/>', '/>', x)
            ns = x.count('<ser>')
            assert ns > 0, f'{f}: no series'
            if '<lineChart>' in x:
                assert x.count('<smooth val="0"/>') >= ns, f'{f}: missing smooth=0'
                n_line += 1
            if '<barChart>' in x:
                assert x.count('<invertIfNegative val="0"/>') >= ns, f'{f}: missing invertIfNegative=0'
                n_bar += 1
    assert n_line + n_bar == N_CHARTS, f'expected {N_CHARTS} charts, found {n_line + n_bar}'
    print(f'chart XML check: {n_line} line charts with smooth val="0", {n_bar} bar charts with invertIfNegative val="0"')


def run_verify():
    scratch = os.environ.get('SLIDE3A_SCRATCH', '/tmp')
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
        if isinstance(exp, str):
            if str(v) != exp:
                bad.append((sh, coord, exp, v))
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
        f.write(f'formula cells checked: {len(EXPECT)}; mismatches: {len(bad)}; error values: {len(errs)}; semantic checks vs agent CSVs: {len(SEMANTIC)} passed\n')
        for b in bad[:200]:
            f.write(f'MISMATCH {b}\n')
        for e in errs[:200]:
            f.write(f'ERROR {e}\n')
    print(open(rep).read()[:3000])
    if bad or errs:
        sys.exit(1)


if __name__ == '__main__':
    main(verify='--verify' in sys.argv)
