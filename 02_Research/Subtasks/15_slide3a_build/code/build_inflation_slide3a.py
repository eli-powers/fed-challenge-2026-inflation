"""Build Inflation slides 3a.1 (first round, not a spiral) and 3a.2 (early signs of persistence) and their workbook.

Run from the project root:
    python3 -I "02_Research/Subtasks/15_slide3a_build/code/build_inflation_slide3a.py" --verify

Eli, Nov 16 ("defaults" to the design list, plus: don't call it the Logan measure; Sep actuals only on 3a.1):
  3a.1  two-chart, note line (V/U). Left = horizontal bars, 12m % change, 2018-19 avg / Feb 2026 (pre-oil) / Sep 2026 for
        transportation services, core goods (shock-exposed) and services ex housing & transportation, Dallas trimmed mean,
        Cleveland median PCE. Right = nonfarm business unit labor costs (y/y, red; Eli Nov 16: switched from 8-quarter annualized) and ECI private wages
        and salaries (SA, y/y, dark navy), 2018Q1-2026Q3, dashed at the ULC 2018-19 average.
  3a.2  two-chart, no note line, same monthly window Jan 2018 - Oct 2026 on both panels. Left = NY Fed SCE median 1-year
        expectation (red) vs 5y5y breakeven (T5YIFR monthly avg, dark navy), dashed 2%. Right = NFIB net % planning to raise
        prices (red) vs planning to raise compensation (dark navy).
  Takeaways stay the placeholder. Titles and headings are Claude drafts accepted with "defaults".
Writes 01_Finals/Slide data/Inflation Slide 3A.xlsx; appends 3a.1 and 3a.2 after the last slide of the working deck.
Helpers (layout, colors, chart fixes) come from 14_slide2a_build/code/build_inflation_slide2ab.py.
"""
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import zipfile

from lxml import etree
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '14_slide2a_build', 'code'))
import build_inflation_slide2ab as b2  # noqa: E402

rgb, text_box = b2.rgb, b2.text_box
NAVY, RED, DNAVY, BLACK, GRAY = b2.NAVY, b2.RED, b2.DNAVY, b2.BLACK, '7F7F7F'
S3A = os.path.join(ROOT, '02_Research', 'Subtasks', '11_slide3a_research', 'outputs')
P13 = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs')
BEA = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw', 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')
PRODJ = os.path.join(ROOT, '03_Data', 'Raw', 'S3A_B_labor_costs_2026-11-15', 'bls_api_productivity_costs_2008-2026_2026-11-15.json')
ECIF = os.path.join(ROOT, '03_Data', 'pipelines', 'inflation_data', 'processed', 'bls', 'observations.csv')
XLSX = os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 3A.xlsx')
DECK = b2.DECK
REPORT = os.path.join(HERE, 'verify_report.txt')
REL = lambda p: os.path.relpath(p, ROOT)

S1 = dict(title=('Inflation', 'A First Round, Not a Spiral'),
          heading='The Shock Shows Up in Exposed Prices, Not in Labor Costs',
          note='Top two items are directly exposed to oil and tariffs · Job openings per unemployed worker: 1.06 (Sep 2026) vs 1.16 (2018–19 avg.)',
          panel_l='Prices by exposure to the shock, 12-month % change',
          panel_r='Labor costs, % change from a year earlier',
          source=('Source: BEA (Table 2.4.4U; services ex. housing & transportation: UMD calc.); Dallas Fed; Cleveland Fed; BLS (nonfarm '
                  'unit labor costs, y/y; ECI private wages & salaries, SA, y/y; JOLTS/CPS). Left: Sep 2026; right: through 2026Q3. '
                  'Dashed line: unit labor costs, 2018–19 avg.'))
S2 = dict(title=('Inflation', 'Early Signs of Persistence'),
          heading='Households Expect More Inflation, and Small Firms Plan to Raise Prices',
          panel_l='Inflation expectations (%)',
          panel_r='Small firms’ plans, next 3 months (net % of firms)',
          source=('Source: NY Fed Survey of Consumer Expectations (median 1-yr-ahead); St. Louis Fed via FRED (5-yr, 5-yr forward '
                  'breakeven, T5YIFR, monthly avg. of daily); NFIB (net % planning to raise prices / compensation, SA). Monthly, '
                  'Jan 2018–Oct 2026. Dashed line: 2% target.'))
MARKS = (S1['title'][1], S2['title'][1])
ITEMS = [('trans', 'Transportation services'), ('goods', 'Core goods'), ('svx', 'Services ex. housing & transportation'),
         ('trim', 'Trimmed mean PCE (Dallas Fed)'), ('med', 'Median PCE (Cleveland Fed)')]
COLS = [('2018–19 avg.', GRAY), ('Feb 2026 (pre-oil)', DNAVY), ('Sep 2026', RED)]
QWIN = [f'{y}Q{q}' for y in range(2018, 2027) for q in range(1, 5)][:35]          # 2018Q1-2026Q3
MWIN = b2.months('2018-01', '2026-10')
PLOT_NOTE, PLOT_NONOTE = (2.40, 5.60), (2.16, 5.60)
PL, PR = (1.27, 5.13), (7.40, 11.27)
EXPECT = {}


# ================================================================ data
def load():
    D = {}
    bea = json.load(open(BEA))['BEAAPI']['Results']['Data']
    idx = {}
    for r in bea:
        if r['LineNumber'] in ('190', '375'):
            idx[(int(r['LineNumber']), r['TimePeriod'].replace('M', '-'))] = float(r['DataValue'].replace(',', ''))
    D['bea_m'] = b2.months('2017-01', '2026-09')
    D['bea'] = idx
    r12 = lambda ln, m: (idx[(ln, m)] / idx[(ln, D['bea_m'][D['bea_m'].index(m) - 12])] - 1) * 100
    pre = b2.months('2018-01', '2019-12')
    avg = lambda f: sum(f(m) for m in pre) / len(pre)
    bars = {'trans': [avg(lambda m: r12(190, m)), r12(190, '2026-02'), r12(190, '2026-09')],
            'goods': [avg(lambda m: r12(375, m)), r12(375, '2026-02'), r12(375, '2026-09')]}
    # published / audited 12m series
    lm = {r['month']: float(r['12m_pct']) for r in csv.DictReader(open(os.path.join(S3A, 'C_q6_logan_measure.csv'))) if r['12m_pct']}
    und = list(csv.DictReader(open(os.path.join(S3A, 'C_q6_underlying.csv'))))
    ser = lambda start, hz: {r['period']: float(r['value']) for r in und if r['series'].startswith(start) and r['horizon'] == hz and r['value']}
    trim, med = ser('Dallas Fed trimmed-mean PCE, 12m', '12m (y/y)'), ser('Cleveland Fed median PCE, 12m % change (published)', '12m (% y/y)')
    D['m12'] = {'svx': lm, 'trim': trim, 'med': med}
    for k, s in D['m12'].items():
        bars[k] = [avg(lambda m: s[m]), s['2026-02'], s['2026-09']]
    D['bars'] = bars
    # cross-checks against audited outputs
    p3 = {r['month']: r for r in csv.DictReader(open(os.path.join(P13, 'P3_transport_split.csv')))}
    p2 = {r['month']: r for r in csv.DictReader(open(os.path.join(P13, 'P2_core_decomposition.csv')))}
    p2s = {r['period']: r for r in csv.DictReader(open(os.path.join(P13, 'P2_core_decomposition_summary.csv')))}
    q6s = {(r['group'], r['series'], r['horizon']): r for r in csv.DictReader(open(os.path.join(S3A, 'C_q6_summary.csv')))}
    ck = {
        'trans Feb/Sep vs P3': max(abs(bars['trans'][1] - float(p3['2026-02']['transport_12m'])), abs(bars['trans'][2] - float(p3['2026-09']['transport_12m']))),
        'goods Feb/Sep vs P2': max(abs(bars['goods'][1] - float(p2['2026-02']['Core goods | 12m'])), abs(bars['goods'][2] - float(p2['2026-09']['Core goods | 12m']))),
        'goods 2018-19 vs P2 summary': abs(bars['goods'][0] - float(p2s['2018-19 avg']['Core goods 12m'])),
        'svx 2018-19 vs C_q6_summary': abs(bars['svx'][0] - float([v for k, v in q6s.items() if k[0] == 'Supercore / Logan measure' and '[Sep actual]' in k[1] and 'Logan' in k[1] and k[2] == '12m'][0]['avg_2018_19'])),
        'trim 2018-19 vs C_q6_summary': abs(bars['trim'][0] - float(q6s[('Dallas trimmed mean PCE', 'Dallas trimmed-mean PCE', '12m (y/y)')]['avg_2018_19'])),
        'med 2018-19 vs C_q6_summary': abs(bars['med'][0] - float(q6s[('Cleveland median PCE', 'Cleveland median PCE', '12m published')]['avg_2018_19'])),
    }
    # labor costs
    pj = json.load(open(PRODJ))['Results']['series']
    ulc = {f"{o['year']}Q{o['period'][-1]}": float(o['value']) for s in pj if s['seriesID'] == 'PRS85006113' for o in s['data'] if o['period'].startswith('Q')}
    eci = {}
    for r in csv.DictReader(open(ECIF)):
        if r['publisher_series_id'] == 'CIS2020000000000I' and r['value_type'] == 'index_level':
            y, mo = int(r['date'][:4]), int(r['date'][5:7])
            eci[f'{y}Q{(mo - 1) // 3 + 1}'] = float(r['value'])
    allq = [f'{y}Q{q}' for y in range(2016, 2027) for q in range(1, 5)][:43]
    D['ulc'], D['eci'], D['allq'] = ulc, eci, allq
    sh = lambda q, k: allq[allq.index(q) - k]
    D['ulc4'] = {q: (ulc[q] / ulc[sh(q, 4)] - 1) * 100 for q in QWIN}
    D['eci4'] = {q: (eci[q] / eci[sh(q, 4)] - 1) * 100 for q in QWIN}
    D['ulc_ref'] = sum(D['ulc4'][q] for q in QWIN if q < '2020') / 8
    bq = list(csv.DictReader(open(os.path.join(S3A, 'B_q3_wages_ulc.csv'))))
    b8 = {r['period']: float(r['yoy']) for r in bq if r['series_id'] == 'PRS85006113' and r['yoy']}
    by = {r['period']: float(r['yoy']) for r in bq if r['series_id'] == 'CIS2020000000000I' and r['yoy']}
    ck['ULC y/y vs B_q3'] = max(abs(D['ulc4'][q] - b8[q]) for q in QWIN)
    ck['ECI y/y vs B_q3'] = max(abs(D['eci4'][q] - by[q]) for q in QWIN)
    vu = json.load(open(os.path.join(S3A, 'A_q1_vu_summary.json')))
    D['vu'] = (vu['vu_latest'][1], vu['vu_avg_2018_19'])
    # expectations and NFIB
    ex = list(csv.DictReader(open(os.path.join(S3A, 'C_q4_expectations.csv'))))
    D['sce'] = {r['period']: float(r['value']) for r in ex if r['series_id'] == 'Median one-year ahead expected inflation rate'}
    D['fwd'] = {r['period']: float(r['value']) for r in ex if r['series_id'] == 'T5YIFR' and r['horizon'].startswith('5y5y monthly')}
    nf = list(csv.DictReader(open(os.path.join(S3A, 'B_q5_catchup.csv'))))
    D['nfp'] = {r['period']: float(r['value']) for r in nf if r['series'] == 'NFIB net % planning to raise prices, next 3 months'}
    D['nfc'] = {r['period']: float(r['value']) for r in nf if r['series'] == 'NFIB net % planning to raise compensation, next 3 months'}
    D['src'] = {'sce': [r for r in ex if r['series_id'] == 'Median one-year ahead expected inflation rate'][0]['source_file'],
                'fwd': [r for r in ex if r['series_id'] == 'T5YIFR'][0]['source_file'],
                'nfib': 'NFIB SBET PDFs in 03_Data/Raw/S3A_B_labor_costs_2026-11-15/ (via B_q5_catchup.csv)'}
    for k in ('sce', 'fwd', 'nfp', 'nfc'):
        miss = [m for m in MWIN if m not in D[k]]
        assert not miss, (k, miss)
    D['checks'] = ck
    assert max(ck.values()) < 0.006, ck
    return D


# ================================================================ workbook
def build_wb(D):
    wb = Workbook()
    rb = wb.active
    rb.title = 'Raw_BEA'
    rb.append(['Month', 'BEA U20404 line 190 Transportation services (index)', 'BEA U20404 line 375 PCE goods ex food & energy (index)'])
    RB = {}
    for m in D['bea_m']:
        rb.append([b2.mdate(m), D['bea'][(190, m)], D['bea'][(375, m)]])
        rb.cell(rb.max_row, 1).number_format = 'yyyy-mm'
        RB[m] = rb.max_row
    b2.fmt_hdr(rb, [10, 26, 26])
    r12 = wb.create_sheet('Raw_12m')
    r12.append(['Month', 'Services ex. housing & transportation, 12m % (UMD, C_q6_logan_measure.csv)',
                'Dallas Fed trimmed mean PCE, 12m % (PCETRIM12M159SFRBDAL)', 'Cleveland Fed median PCE, 12m % (published)'])
    R12 = {}
    for m in b2.months('2018-01', '2026-09'):
        r12.append([b2.mdate(m), D['m12']['svx'][m], D['m12']['trim'][m], D['m12']['med'][m]])
        r12.cell(r12.max_row, 1).number_format = 'yyyy-mm'
        R12[m] = r12.max_row
    b2.fmt_hdr(r12, [10, 24, 24, 24])
    rq = wb.create_sheet('Raw_labor')
    rq.append(['Quarter', 'PRS85006113 nonfarm business unit labor costs (index 2017=100)', 'CIS2020000000000I ECI private wages & salaries, SA (index)'])
    RQ = {}
    for q in D['allq']:
        rq.append([q, D['ulc'][q], D['eci'][q]])
        RQ[q] = rq.max_row
    b2.fmt_hdr(rq, [10, 26, 26])
    rs = wb.create_sheet('Raw_survey')
    rs.append(['Month', 'NY Fed SCE median 1-yr expected inflation (%)', 'T5YIFR 5y5y breakeven, monthly avg of daily (%)',
               'NFIB net % planning to raise prices', 'NFIB net % planning to raise compensation'])
    RS = {}
    for m in MWIN:
        rs.append([b2.mdate(m), D['sce'][m], D['fwd'][m], D['nfp'][m], D['nfc'][m]])
        rs.cell(rs.max_row, 1).number_format = 'yyyy-mm'
        RS[m] = rs.max_row
    b2.fmt_hdr(rs, [10, 20, 20, 20, 20])

    # ---- chart tab: Exposure bars
    tb = wb.create_sheet('Exposure_bars')
    tb.append(['Item'] + [c for c, _ in COLS])
    pre = b2.months('2018-01', '2019-12')
    for key_, lab in ITEMS:
        r = tb.max_row + 1
        tb.cell(r, 1, lab)
        if key_ in ('trans', 'goods'):
            col = 'B' if key_ == 'trans' else 'C'
            terms = ','.join(f'Raw_BEA!{col}{RB[m]}/Raw_BEA!{col}{RB[m] - 12}' for m in pre)
            tb.cell(r, 2, f'=(AVERAGE({terms})-1)*100')
            for j, mm in ((3, '2026-02'), (4, '2026-09')):
                tb.cell(r, j, f'=(Raw_BEA!{col}{RB[mm]}/Raw_BEA!{col}{RB[mm] - 12}-1)*100')
        else:
            col = {'svx': 'B', 'trim': 'C', 'med': 'D'}[key_]
            tb.cell(r, 2, f'=AVERAGE(Raw_12m!{col}{R12["2018-01"]}:{col}{R12["2019-12"]})')
            tb.cell(r, 3, f'=Raw_12m!{col}{R12["2026-02"]}')
            tb.cell(r, 4, f'=Raw_12m!{col}{R12["2026-09"]}')
        for j in range(3):
            tb.cell(r, 2 + j).number_format = '0.00'
            EXPECT[('Exposure_bars', tb.cell(r, 2 + j).coordinate)] = D['bars'][key_][j]
    b2.fmt_hdr(tb, [38, 14, 18, 12])

    # ---- chart tab: Labor costs (quarterly; column A = quarter-start dates)
    tl = wb.create_sheet('Labor_costs')
    tl.append(['Date', 'Unit labor costs (y/y)', 'ECI wages (y/y)', 'Reference'])
    first = tl.max_row + 1
    for q in QWIN:
        r = tl.max_row + 1
        y, qq = int(q[:4]), int(q[-1])
        tl.cell(r, 1, dt.datetime(y, 3 * qq - 2, 1)).number_format = 'yyyy-mm'
        tl.cell(r, 2, f'=(Raw_labor!B{RQ[q]}/Raw_labor!B{RQ[q] - 4}-1)*100').number_format = '0.00'
        tl.cell(r, 3, f'=(Raw_labor!C{RQ[q]}/Raw_labor!C{RQ[q] - 4}-1)*100').number_format = '0.00'
        tl.cell(r, 4, f'=AVERAGE($B${first}:$B${first + 7})').number_format = '0.00'
        EXPECT[('Labor_costs', f'B{r}')] = D['ulc4'][q]
        EXPECT[('Labor_costs', f'C{r}')] = D['eci4'][q]
        EXPECT[('Labor_costs', f'D{r}')] = D['ulc_ref']
    b2.fmt_hdr(tl, [10, 16, 14, 10])

    # ---- chart tabs: Expectations, NFIB_plans
    te = wb.create_sheet('Expectations')
    te.append(['Date', 'Households, 1-yr (SCE)', 'Markets, 5y5y', 'Reference'])
    tn = wb.create_sheet('NFIB_plans')
    tn.append(['Date', 'Price plans', 'Pay plans'])
    for m in MWIN:
        r = te.max_row + 1
        te.cell(r, 1, b2.mdate(m)).number_format = 'yyyy-mm'
        te.cell(r, 2, f'=Raw_survey!B{RS[m]}').number_format = '0.00'
        te.cell(r, 3, f'=Raw_survey!C{RS[m]}').number_format = '0.00'
        te.cell(r, 4, 2)
        tn.cell(r, 1, b2.mdate(m)).number_format = 'yyyy-mm'
        tn.cell(r, 2, f'=Raw_survey!D{RS[m]}')
        tn.cell(r, 3, f'=Raw_survey!E{RS[m]}')
        EXPECT[('Expectations', f'B{r}')] = D['sce'][m]
        EXPECT[('Expectations', f'C{r}')] = D['fwd'][m]
        EXPECT[('NFIB_plans', f'B{r}')] = D['nfp'][m]
        EXPECT[('NFIB_plans', f'C{r}')] = D['nfc'][m]
    b2.fmt_hdr(te, [10, 18, 14, 10])
    b2.fmt_hdr(tn, [10, 12, 12])

    ck = '; '.join(f'{k} {v:.4f}' for k, v in D['checks'].items())
    b2.notes_tab(wb, [
        ('3a.1 title', f"{S1['title'][0]}: {S1['title'][1]}", 'DRAFT by Claude, accepted by Eli ("defaults", Nov 16)'),
        ('3a.1 chart heading', S1['heading'], 'DRAFT by Claude, accepted by Eli ("defaults")'),
        ('3a.1 note line', S1['note'], f"V/U = JOLTS openings / CPS unemployed: {D['vu'][0]:.4f} (Sep 2026) vs {D['vu'][1]:.4f} (2018-19 avg); "
         '11_slide3a_research/outputs/A_q1_vu_summary.json (audited, converged R3; raw 03_Data/Raw/S3A_A_vu_2026-11-15/)'),
        ('3a.1 left panel', S1['panel_l'] + '; horizontal bars: 2018-19 avg (gray), Feb 2026 (dark navy), Sep 2026 (red); Sep actuals only (Eli: no estimates)',
         'Exposure_bars. Transportation services = BEA U20404 line 190; core goods = line 375 (PCE goods ex food & energy), both from Raw_BEA '
         f'({REL(BEA)}, BEA vintage 2026-10-29). Services ex. housing & transportation = UMD Fisher removal of lines 153 and 190 from line 376 '
         '(11_slide3a_research/outputs/C_q6_logan_measure.csv, audited; Dallas Fed President Logan cites this measure; not named on the slide per Eli). '
         'Trimmed mean and median from C_q6_underlying.csv (FRED PCETRIM12M159SFRBDAL; Cleveland Fed median PCE file). 2018-19 avg = average of the 24 monthly 12m rates.'),
        ('3a.1 right panel', S1['panel_r'] + '; unit labor costs y/y (red), ECI private wages & salaries SA y/y (dark navy), 2018Q1-2026Q3; dashed = ULC 2018-19 avg',
         f'Labor_costs over Raw_labor: PRS85006113 from {REL(PRODJ)} (2026Q3 preliminary, released Nov 5; history revised to 2021Q1); '
         f'CIS2020000000000I from {REL(ECIF)} (2026Q3 released Oct 30). ULC 2018-19 average of y/y = {D["ulc_ref"]:.4f}'),
        ('3a.2 title', f"{S2['title'][0]}: {S2['title'][1]}", 'DRAFT by Claude, accepted by Eli ("defaults")'),
        ('3a.2 chart heading', S2['heading'], 'DRAFT by Claude, accepted by Eli ("defaults")'),
        ('3a.2 left panel', S2['panel_l'] + '; SCE 1-yr median (red), 5y5y breakeven monthly avg (dark navy), dashed 2%, Jan 2018-Oct 2026',
         f"Expectations over Raw_survey; SCE: {D['src']['sce']}; 5y5y: {D['src']['fwd']} (via C_q4_expectations.csv, audited). "
         'Michigan omitted (2024 phone-to-web mode break); SPF quarterly (verbal).'),
        ('3a.2 right panel', S2['panel_r'] + '; NFIB net % planning to raise prices (red) and compensation (dark navy), SA, Jan 2018-Oct 2026',
         f"NFIB_plans over Raw_survey; {D['src']['nfib']}. 2018-20 values from an archived report (seasonal factors may differ at the join)."),
        ('Source lines', S1['source'] + ' || ' + S2['source'], ''),
        ('Takeaways', b2.TAKEAWAY, 'placeholder on both slides'),
        ('Verbal only (Eli)', 'Non-wage share (output prices +4.05% vs ULC +2.39%; labor share 53.0, record low); FEDS oil note bridge ("upper bound"); Oct estimates', 'cue tracker, PENDING Eli'),
        ('Cross-checks vs audited outputs', ck, 'max abs diff (pp)'),
        ('Guide deviations', '(1) 3a.1 left = horizontal bars with three series and a key; third series in gray #7F7F7F (guide has two series colors); '
         '(2) 3a.1 left axis -2 to 10 step 2; (3) 3a.1 right is quarterly, labels on Q1 of even years; (4) 3a.2 monthly 2018-2026, labels on January of even years '
         '(Jan/Jul labels would overlap over nine years); (5) 3a.2 right axis -10 to 60 step 10 (NFIB price plans -3 in 2020); (6) end-label values to one decimal (NFIB integers).', ''),
        ('Build', 'python3 -I "02_Research/Subtasks/15_slide3a_build/code/build_inflation_slide3a.py" --verify', ''),
    ])
    wb._sheets = [tb, tl, te, tn, rb, r12, rq, rs, wb['Notes']]
    wb.calculation.fullCalcOnLoad = True
    return wb


# ================================================================ slides
def line_chart(s, cats, series, plot_x, plot_y, lo, hi, step, fmt, ref=None):
    cd = CategoryChartData()
    cd.categories = cats
    for n, vv in series:
        cd.add_series(n, vv)
    if ref is not None:
        cd.add_series('Reference', [ref] * len(cats))
    fr = (plot_x[0] - 0.62, plot_y[0] - 0.08, plot_x[1] + 0.08, plot_y[1] + 0.36)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(fr[0]), Inches(fr[1]), Inches(fr[2] - fr[0]), Inches(fr[3] - fr[1]), cd)
    ch = gf.chart
    ch.has_title = ch.has_legend = False
    sty = [(RED, 3, None), (DNAVY, 3, None), (BLACK, 2.25, MSO_LINE_DASH_STYLE.DASH)]
    for se, (color, w_, dash) in zip(ch.plots[0].series, sty):
        se.format.line.color.rgb = rgb(color)
        se.format.line.width = Pt(w_)
        if dash:
            se.format.line.dash_style = dash
        se.marker.style = XL_MARKER_STYLE.NONE
        se.smooth = False
    b2.axes(ch, lo, hi, step, fmt)
    cs = b2.frame_fix(ch, plot_x, plot_y, fr)
    for vax in cs.iter(qn('c:valAx')):
        cb = vax.find(qn('c:crossBetween'))
        if cb is None:
            cb = etree.SubElement(vax, qn('c:crossBetween'))
        cb.set('val', 'midCat')
    cax = next(cs.iter(qn('c:catAx')))
    for tg_ in ('c:tickLblSkip', 'c:tickMarkSkip', 'c:noMultiLvlLbl'):
        el = cax.find(qn(tg_))
        if el is not None:
            cax.remove(el)
    ext = cax.find(qn('c:extLst'))
    for tg_ in ('c:tickLblSkip', 'c:tickMarkSkip', 'c:noMultiLvlLbl'):
        el = etree.Element(qn(tg_))
        el.set('val', '1')
        (ext.addprevious(el) if ext is not None else cax.append(el))
    cr = cax.find(qn('c:crosses'))
    if cr is not None:
        cr.set('val', 'min')          # guide s.3: baseline stays at the bottom when values go negative
    return ch


def end_labels(s, plot_x, plot_y, lo, hi, labs, width=1.20):
    yof = lambda v: plot_y[1] - (v - lo) / (hi - lo) * (plot_y[1] - plot_y[0])
    ys = [yof(v) for _, _, v, _ in labs]
    h = 0.44
    if abs(ys[0] - ys[1]) < h + 0.02:
        mid = (ys[0] + ys[1]) / 2
        ys = [mid - (h + 0.02) / 2, mid + (h + 0.02) / 2] if ys[0] <= ys[1] else [mid + (h + 0.02) / 2, mid - (h + 0.02) / 2]
    for (n, txt, v, c), y in zip(labs, ys):
        text_box(s, plot_x[1] + 0.16, y - h / 2, width, h, [[(n, c)], [(txt, c)]], 13, 'Arial', align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)


def guide_fix(s):
    """Codex slide3a_build R1-F02: source line Arial 13 and takeaway box 6.53/0.73 per guide s.2 (the shared helper uses 12 / 6.62 / 0.68)."""
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text
        if t.startswith('Source:'):
            for p_ in sh.text_frame.paragraphs:
                for r in p_.runs:
                    r.font.size = Pt(13)
        elif t == b2.TAKEAWAY:
            sh.top, sh.height = Inches(6.53), Inches(0.73)
    return s


def slide_31(prs, D):
    s = b2.base_slide(prs, S1, note=S1['note'])
    PY = PLOT_NOTE
    plx = (3.55, 5.70)
    text_box(s, 0.45, 2.07, 5.70 - 0.45, 0.30, [(S1['panel_l'], NAVY)], 13, 'Arial', bold=True)
    text_box(s, PR[0] - 0.3, 2.07, PR[1] - PR[0] + 0.6, 0.30, [(S1['panel_r'], NAVY)], 13, 'Arial', bold=True)
    order = list(reversed(ITEMS))
    series = [(COLS[j][0], [D['bars'][k][j] for k, _ in order]) for j in (2, 1, 0)]   # Sep bottom ... 2018-19 top within each group
    fr = (0.30, PY[0] - 0.08, plx[1] + 0.45, PY[1] + 0.36)
    b2.bar_chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [lab for _, lab in order], series, plx, PY, fr, -2, 10, 2, '0',
                 ['0.0;-0.0'] * 3, [COLS[2][1], COLS[1][1], COLS[0][1]], gap=45)
    text_box(s, 4.85, 4.55, 1.40, 0.75, [[('■ ' + c, col)] for c, col in COLS], 10, 'Arial', align=PP_ALIGN.LEFT, bold=True)
    cats = [q if (q.endswith('Q1') and int(q[:4]) % 2 == 0) else ' ' for q in QWIN]
    u, e = [D['ulc4'][q] for q in QWIN], [D['eci4'][q] for q in QWIN]
    line_chart(s, cats, [('Unit labor costs (y/y)', u), ('ECI wages (y/y)', e)], PR, PY, 0, 7, 1, '0.00', ref=D['ulc_ref'])
    end_labels(s, PR, PY, 0, 7, [('Unit labor costs', f'{u[-1]:.1f}%', u[-1], RED), ('ECI wages', f'{e[-1]:.1f}%', e[-1], DNAVY)], width=1.55)
    return s


VSHORT = {'trans': 'Transportation services', 'goods': 'Core goods', 'svx': 'Services ex. housing & transport',
          'trim': 'Trimmed mean PCE', 'med': 'Median PCE'}


def slide_31v(prs, D):
    """Alternate 3a.1 (Eli, Nov 16): same content, left chart as vertical columns, for comparison."""
    s = b2.base_slide(prs, S1, note=S1['note'].replace('Top two items', 'The first two items'))
    PY = PLOT_NOTE
    pyv = (PY[0], 5.20)
    plx = (1.27, 6.20)
    text_box(s, 0.45, 2.07, plx[1] - 0.45 + 0.2, 0.30, [(S1['panel_l'], NAVY)], 13, 'Arial', bold=True)
    text_box(s, PR[0] - 0.3, 2.07, PR[1] - PR[0] + 0.6, 0.30, [(S1['panel_r'], NAVY)], 13, 'Arial', bold=True)
    series = [(COLS[j][0], [D['bars'][k][j] for k, _ in ITEMS]) for j in (0, 1, 2)]
    fr = (0.62, pyv[0] - 0.08, plx[1] + 0.10, 5.95)
    gf = b2.bar_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [VSHORT[k] for k, _ in ITEMS], series, plx, pyv, fr, -2, 10, 2, '0',
                      ['0.0;-0.0'] * 3, [c for _, c in COLS], gap=60)
    gf.chart.category_axis.tick_labels.font.size = Pt(10)
    b2.key(s, 2.95, pyv[0] + 0.02, [(c, col) for c, col in COLS], size=10)
    cats = [q if (q.endswith('Q1') and int(q[:4]) % 2 == 0) else ' ' for q in QWIN]
    u, e = [D['ulc4'][q] for q in QWIN], [D['eci4'][q] for q in QWIN]
    line_chart(s, cats, [('Unit labor costs (y/y)', u), ('ECI wages (y/y)', e)], PR, PY, 0, 7, 1, '0.00', ref=D['ulc_ref'])
    end_labels(s, PR, PY, 0, 7, [('Unit labor costs', f'{u[-1]:.1f}%', u[-1], RED), ('ECI wages', f'{e[-1]:.1f}%', e[-1], DNAVY)], width=1.55)
    return s


def slide_32(prs, D):
    s = b2.base_slide(prs, S2)
    PY = PLOT_NONOTE
    for (x0, x1), t in ((PL, S2['panel_l']), (PR, S2['panel_r'])):
        text_box(s, x0 - 0.3, 1.80, x1 - x0 + 0.6, 0.30, [(t, NAVY)], 13, 'Arial', bold=True)
    cats = [m if (m.endswith('-01') and int(m[:4]) % 2 == 0) else ' ' for m in MWIN]
    sce, fwd = [D['sce'][m] for m in MWIN], [D['fwd'][m] for m in MWIN]
    line_chart(s, cats, [('Households, 1-yr (SCE)', sce), ('Markets, 5y5y', fwd)], PL, PY, 0, 7, 1, '0.00', ref=2)
    end_labels(s, PL, PY, 0, 7, [('Households', f'{sce[-1]:.1f}% (1-yr)', sce[-1], RED), ('Markets', f'{fwd[-1]:.1f}% (5y5y)', fwd[-1], DNAVY)], width=1.22)
    nfp, nfc = [D['nfp'][m] for m in MWIN], [D['nfc'][m] for m in MWIN]
    line_chart(s, cats, [('Price plans', nfp), ('Pay plans', nfc)], PR, PY, -10, 60, 10, '0')
    end_labels(s, PR, PY, -10, 60, [('Price plans', f'{nfp[-1]:.0f}', nfp[-1], RED), ('Pay plans', f'{nfc[-1]:.0f}', nfc[-1], DNAVY)])
    return s


def title_of(slide):
    return ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)


def sigs_others(path):
    prs = Presentation(path)
    c14 = lambda b: hashlib.sha256(etree.tostring(etree.fromstring(b, etree.XMLParser(remove_blank_text=True)), method='c14n')).hexdigest()
    out = []
    for slide in prs.slides:
        if any(mk in title_of(slide) for mk in MARKS):
            continue
        sig = [c14(etree.tostring(slide._element))]
        for rel in sorted(slide.part.rels.values(), key=lambda r: r.rId):
            if 'chart' in rel.reltype:
                sig.append(c14(rel.target_part.blob))
        out.append(tuple(sig))
    return out


def build_pptx(D):
    from pptx.opc.packuri import PackURI
    prs = Presentation(DECK)
    lst = prs.slides._sldIdLst
    for sid, slide in zip(list(lst), list(prs.slides)):
        if any(mk in title_of(slide) for mk in MARKS):
            prs.part.drop_rel(sid.get(qn('r:id')))
            lst.remove(sid)
    used = {str(pt.partname) for pt in prs.part.package.iter_parts()}
    k = 300
    for fn in (slide_31, slide_31v, slide_32):
        s = guide_fix(fn(prs, D))
        while f'/ppt/slides/slide{k}.xml' in used:
            k += 1
        s.part.partname = PackURI(f'/ppt/slides/slide{k}.xml')
        used.add(f'/ppt/slides/slide{k}.xml')
    prs.save(DECK)


def verify(D, before):
    L = [f'Inflation slides 3a.1/3a.2 build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    rec = b2.recalc(XLSX)
    bad = [(k, v, rec[k[0]][k[1]].value) for k, v in EXPECT.items()
           if not isinstance(rec[k[0]][k[1]].value, (int, float)) or abs(rec[k[0]][k[1]].value - v) > 1e-9]
    L.append(f'1. workbook formula cells: {len(EXPECT)} checked after LibreOffice recalc; mismatches: {len(bad)} {bad[:3]}')
    ok &= not bad
    L.append('2. cross-checks vs audited outputs (max abs diff, pp): ' + '; '.join(f'{k} {v:.5f}' for k, v in D['checks'].items()))
    prs = Presentation(DECK)
    sl = list(prs.slides)
    ours = [x for x in sl if any(mk in title_of(x) for mk in MARKS)]
    ok &= len(ours) == 3
    worst, n = 0.0, 0
    # 3a.1 bars
    ch = [sh.chart for sh in ours[0].shapes if sh.has_chart]
    tb = rec['Exposure_bars']
    tab = {tb.cell(r, 1).value: [tb.cell(r, c).value for c in (2, 3, 4)] for r in range(2, 2 + len(ITEMS))}
    for se in ch[0].plots[0].series:
        j = [c for c, _ in COLS].index(se.name)
        for name, v in zip(ch[0].plots[0].categories, se.values):
            worst, n = max(worst, abs(v - tab[name][j])), n + 1
    def lines(chart, ws, ncol):
        nonlocal worst, n
        for j, se in enumerate(list(chart.plots[0].series)[:ncol]):
            for i, v in enumerate(se.values):
                worst, n = max(worst, abs(v - ws.cell(2 + i, 2 + j).value)), n + 1
    lines(ch[1], rec['Labor_costs'], 3)
    chv = [sh.chart for sh in ours[1].shapes if sh.has_chart]          # alternate 3a.1, vertical columns
    rows_ = [tab[lab] for _, lab in ITEMS]
    for se in chv[0].plots[0].series:
        j = [c for c, _ in COLS].index(se.name)
        for i, v in enumerate(se.values):
            worst, n = max(worst, abs(v - rows_[i][j])), n + 1
    lines(chv[1], rec['Labor_costs'], 3)
    ch2 = [sh.chart for sh in ours[2].shapes if sh.has_chart]
    lines(ch2[0], rec['Expectations'], 3)
    lines(ch2[1], rec['NFIB_plans'], 2)
    exp_n = 2 * (15 + 3 * len(QWIN)) + 3 * len(MWIN) + 2 * len(MWIN)
    L.append(f'3. chart points vs workbook tabs: {n} points (expected {exp_n}); max abs diff {worst:.1e}')
    ok &= worst < 1e-9 and n == exp_n
    bv = [x for v in D['bars'].values() for x in v]
    rngs = [('3a.1 left', -2, 10, bv), ('3a.1 right', 0, 7, list(D['ulc4'].values()) + list(D['eci4'].values())),
            ('3a.2 left', 0, 7, list(D['sce'].values()) + list(D['fwd'].values())), ('3a.2 right', -10, 60, list(D['nfp'].values()) + list(D['nfc'].values()))]
    for nm, lo, hi, vals in rngs:
        vals = [v for v in vals]
        fit = lo <= min(vals) and max(vals) <= hi
        L.append(f'4. axis {nm}: {lo}..{hi}; data {min(vals):.2f}..{max(vals):.2f}; fit {fit}')
        ok &= fit
    after = sigs_others(DECK)
    same = after == before
    names = zipfile.ZipFile(DECK).namelist()
    dup = sorted({x for x in names if names.count(x) > 1})
    order = [title_of(x)[:45] for x in sl]
    L.append(f'5. deck: {len(sl)} slides; 3a.1 / 3a.1 alt (vertical) / 3a.2 at positions {[sl.index(x) + 1 for x in ours]}; all other slides unchanged: {same}; duplicates: {dup or "none"}')
    L.append('   order: ' + ' | '.join(order))
    ok &= same and not dup
    L.append(f"6. end-label values: ULC y/y {D['ulc4']['2026Q3']:.2f}, ECI {D['eci4']['2026Q3']:.2f}, ref {D['ulc_ref']:.2f}; SCE {D['sce']['2026-10']:.2f}, "
             f"5y5y {D['fwd']['2026-10']:.2f}; NFIB prices {D['nfp']['2026-10']:.0f}, pay {D['nfc']['2026-10']:.0f}; V/U {D['vu'][0]:.2f} vs {D['vu'][1]:.2f}")
    L.append('   bars (2018-19 / Feb 2026 / Sep 2026): ' + '; '.join(f"{lab}: " + ' / '.join(f'{x:.2f}' for x in D['bars'][k]) for k, lab in ITEMS))
    L.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    if not ok:
        sys.exit(1)


def main(do_verify):
    D = load()
    build_wb(D).save(XLSX)
    before = sigs_others(DECK)
    build_pptx(D)
    print(f'wrote {REL(XLSX)}; appended 3a.1, 3a.2 to {REL(DECK)}')
    if do_verify:
        verify(D, before)


if __name__ == '__main__':
    main('--verify' in sys.argv)
