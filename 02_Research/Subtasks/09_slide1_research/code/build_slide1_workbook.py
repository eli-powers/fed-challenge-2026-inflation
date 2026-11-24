"""Build 01_Finals/data/Slide1_Inflation_Data.xlsx from the slide1_research outputs and their raw files.

Run from the project root:
    python3 -I "02_Research/Subtasks/09_slide1_research/code/build_slide1_workbook.py"            # build
    python3 -I "02_Research/Subtasks/09_slide1_research/code/build_slide1_workbook.py" --verify   # build + LibreOffice recalc check

Design (GO.md, Eli's binding requirements):
  * research tabs first (one per item), raw_ tabs last (grey);
  * research tabs draw on raw tabs with live formulas where practical; script-computed values carry a cell
    note naming the script and function;
  * native openpyxl charts built from the workbook's own cells;
  * every formula cell's expected value is computed here in Python (EXPECT) and checked after a LibreOffice
    recalculation (--verify).
Fix inputs (outputs/*.csv, raw files), then rebuild. Do not hand-edit the xlsx unless Eli has started doing so.
"""
import csv
import datetime as dt
import re
import json
import math
import os
import statistics
import subprocess
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, LineChart, Reference, Series
from openpyxl.chart.data_source import NumDataSource, NumRef
from openpyxl.chart.error_bar import ErrorBars
from openpyxl.chart.legend import LegendEntry
from openpyxl.chart.marker import DataPoint, Marker
from openpyxl.chart.text import RichText, Text
from openpyxl.chart.title import Title
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, RegularTextRun, RichTextProperties
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink  # noqa: F401  (hyperlinks set via cell.hyperlink)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research')
OUT = os.path.join(SUB, 'outputs')
BUILD = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs')
PCE_RAW = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw')
XLSX = os.environ.get('SLIDE1_OUT') or os.path.join(ROOT, '01_Finals', 'data', 'Slide1_Inflation_Data.xlsx')   # SLIDE1_OUT: build elsewhere (e.g. to diff against a hand-edited copy)
SCRIPT = '09_slide1_research/code/build_slide1_workbook.py'
BUILD_DATE = dt.date.today().isoformat()

sys.path.insert(0, os.path.join(SUB, 'code'))

T20804 = os.path.join(PCE_RAW, 'BEA_NIPA_T20804_2026-11-10.json')
U20404 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')
U20405 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20405_2026-11-10.json')
OCT_SUM = os.path.join(BUILD, 'D_build_2026-10_summary.csv')
OCT_LINES = os.path.join(BUILD, 'D_build_2026-10_lines.csv')
REL = lambda p: os.path.relpath(p, ROOT)

# ----------------------------------------------------------------------------- styles
NAVY = '1F3864'
F_TITLE = Font(bold=True, size=14, color=NAVY)
F_SUB = Font(italic=True, size=10, color='404040')
F_HDR = Font(bold=True, color='FFFFFF')
F_BOLD = Font(bold=True)
FILL_HDR = PatternFill('solid', fgColor=NAVY)
FILL_BAND = PatternFill('solid', fgColor='F2F2F2')
FILL_EST = PatternFill('solid', fgColor='FFF2CC')      # est. (our estimate)
FILL_CF = PatternFill('solid', fgColor='FCE4D6')       # carried forward
FILL_PRESS = PatternFill('solid', fgColor='DDEBF7')    # press-reported
FILL_KEY = PatternFill('solid', fgColor='E2EFDA')      # key figure
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
TAB_COLORS = {'README': '1F3864', 'Headline': 'C00000', 'TS_PCE_rates': '2F5597', 'R1_backtest': '548235',
              'R2_outside_estimates': '548235', 'R3_core_gap': '7030A0', 'R4_sep_pce_check': '7030A0',
              'R5_cleveland': 'ED7D31', 'R6_breadth': 'BF8F00', 'Sources': '1F3864',
              'Judgment_calls_and_paywalled': 'FF0000'}
FMT_RATE = '0.00'
FMT_RATE3 = '0.000'
FMT_BR = '0.0'
FMT_LVL = '0.000'

EXPECT = {}   # (sheet, coordinate) -> expected numeric value for formula cells
R6_EXPECTED_HARDCODED = {}   # (period, scope, horizon, method) -> C_breadth.csv primary/robustness value (semantic check)


def rd(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(str(x).replace(',', ''))
    except (TypeError, ValueError):
        return None


def note(cell, text):
    cell.comment = Comment(text, 'build_slide1_workbook.py', width=320, height=110)


def header(ws, title, what, units):
    ws['A1'] = title
    ws['A1'].font = F_TITLE
    ws['A2'] = what
    ws['A2'].font = F_SUB
    ws['A3'] = units
    ws['A3'].font = F_SUB
    ws.sheet_properties.tabColor = TAB_COLORS.get(ws.title, '808080')


def hdr_row(ws, row, col, names, widths=None):
    for j, n in enumerate(names):
        c = ws.cell(row=row, column=col + j, value=n)
        c.font = F_HDR
        c.fill = FILL_HDR
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
        c.border = BOX
    ws.row_dimensions[row].height = 32
    if widths:
        for j, w in enumerate(widths):
            ws.column_dimensions[get_column_letter(col + j)].width = w


WRITTEN = set()   # (sheet, row, col): guard against one block silently overwriting another


def put(ws, row, col, value, fmt=None, expect=None, fill=None, bold=False):
    key = (ws.title, row, col)
    if key in WRITTEN:
        raise ValueError(f'cell written twice (block overlap): {ws.title}!{get_column_letter(col)}{row}')
    WRITTEN.add(key)
    c = ws.cell(row=row, column=col, value=value)
    if fmt:
        c.number_format = fmt
    if fill is not None:
        c.fill = fill
    if bold:
        c.font = F_BOLD
    c.border = BOX
    if isinstance(value, str) and value.startswith('='):
        if expect is None:
            raise ValueError(f'formula without expected value: {ws.title}!{c.coordinate} {value}')
        EXPECT[(ws.title, c.coordinate)] = expect
    return c


def band(ws, r0, r1, c0, c1):
    for r in range(r0, r1 + 1):
        if (r - r0) % 2 == 1:
            for cc in range(c0, c1 + 1):
                cell = ws.cell(row=r, column=cc)
                if cell.fill is None or cell.fill.fgColor.rgb in (None, '00000000'):
                    cell.fill = FILL_BAND


def section(ws, row, text):
    if (ws.title, row, 1) in WRITTEN:
        raise ValueError(f'section label overwrites data: {ws.title}!A{row}')
    WRITTEN.add((ws.title, row, 1))
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(bold=True, size=12, color=NAVY)


def ref(sheet, coord):
    return f"'{sheet}'!{coord}" if not sheet.isidentifier() else f'{sheet}!{coord}'


def rich_title(lines):
    """Chart/axis title as rich text that does NOT overlay the plot. lines = [(text, size_pt, bold, hex colour)]."""
    paras = []
    for text, sz, bold, col in lines:
        cp = CharacterProperties(sz=int(sz * 100), b=bold, solidFill=col)
        paras.append(Paragraph(pPr=ParagraphProperties(defRPr=cp), r=[RegularTextRun(rPr=cp, t=text)]))
    return Title(tx=Text(rich=RichText(bodyPr=RichTextProperties(), p=paras)), overlay=False)


def style_chart(ch, title, ytitle, xtitle, source, w=24, h=11, yfmt=None):
    """Title (bold) with a small grey source line; axis titles; legend at bottom; category labels at the bottom edge."""
    ch.title = rich_title([(title, 12, True, '1F1F1F'), (source, 8, False, '595959')])
    ch.y_axis.title = rich_title([(ytitle, 9, True, '404040')])
    ch.x_axis.title = rich_title([(xtitle, 9, True, '404040')])
    ch.width, ch.height = w, h
    ch.legend.position = 'b'
    ch.legend.overlay = False
    # openpyxl >= 3.1 hides axes unless delete is set False explicitly
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.tickLblPos = 'low'      # keep category labels at the bottom even when values go negative
    if yfmt:
        ch.y_axis.number_format = yfmt
        ch.y_axis.numFmt.sourceLinked = False


def line_style(s, color, dash=None, width_pt=2.0):
    s.graphicalProperties.line.solidFill = color
    s.graphicalProperties.line.width = int(width_pt * 12700)
    if dash:
        s.graphicalProperties.line.dashStyle = dash
    s.marker.symbol = 'none'
    s.smooth = False


def finalize_chart(ch):
    """Excel defaults that openpyxl leaves unset and that render wrongly in Excel:
    - line series: <c:smooth> absent -> Excel draws SMOOTHED curves; force straight segments;
    - bar series: <c:invertIfNegative> absent -> Excel fills negative bars WHITE (look empty); force off."""
    for sub in ch._charts:
        for s in sub.series:
            if isinstance(sub, LineChart):
                s.smooth = False
            if isinstance(sub, BarChart):
                s.invertIfNegative = False


def add_chart(ws, ch, anchor):
    finalize_chart(ch)
    ws.add_chart(ch, anchor)


def raw_meta(ws, title, rows):
    """raw tab header: rows 1..4, data header at row 6"""
    ws['A1'] = title
    ws['A1'].font = F_TITLE
    for i, (k, v) in enumerate(rows):
        ws.cell(row=2 + i, column=1, value=k).font = F_BOLD
        ws.cell(row=2 + i, column=2, value=v).font = F_SUB
    ws.sheet_properties.tabColor = '808080'


# ----------------------------------------------------------------------------- load raw data
def bea(path):
    d = json.load(open(path))['BEAAPI']['Results']
    return d['Data'], d


def bea_levels(path, lines):
    data, _ = bea(path)
    out = {}
    for r in data:
        if r['LineNumber'] in lines:
            out[(r['LineNumber'], r['TimePeriod'])] = num(r['DataValue'])
    return out


def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield f'{y}-{m:02d}'
        m += 1
        if m == 13:
            y, m = y + 1, 1


def bea_p(m):
    return m.replace('-', 'M')


def main(verify=False):
    wb = Workbook()
    wb.remove(wb.active)
    research = ['README', 'Headline', 'TS_PCE_rates', 'R1_backtest', 'R2_outside_estimates', 'R3_core_gap',
                'R4_sep_pce_check', 'R5_cleveland', 'R6_breadth', 'Sources', 'Judgment_calls_and_paywalled']
    raws = ['raw_PCE_T20804', 'raw_PCE_components', 'raw_PCE_leaves', 'raw_Oct_build', 'raw_CPI', 'raw_BEA_9_1U', 'raw_backtest',
            'raw_outside_estimates', 'raw_Cleveland', 'raw_BEA_release_text']
    S = {n: wb.create_sheet(n) for n in research + raws}

    # ======================================================================= raw_PCE_T20804
    ws = S['raw_PCE_T20804']
    lv = bea_levels(T20804, {'1', '25'})
    _, t_meta = bea(T20804)
    raw_meta(ws, 'BEA NIPA Table 2.8.4: PCE price indexes, monthly (2017=100, SA, Fisher)', [
        ('Source file', REL(T20804)),
        ('URL', 'https://apps.bea.gov/api/data (DataSetName=NIPA, TableName=T20804, Frequency=M); table view: https://apps.bea.gov/iTable/?reqid=19&step=2&isuri=1&categories=survey'),
        ('Vintage', 'Oct 29, 2026 release (data through Sep 2026); file saved 2026-11-10'),
        ('Retrieved', '2026-11-10 (03_Data/pipelines/Price indexes/PCE pipeline)')])
    hdr_row(ws, 6, 1, ['Month', 'Core PCE index (line 25, DPCCRG)', 'Headline PCE index (line 1, DPCERG)'], [10, 22, 22])
    T_ROW = {}
    T_LV = {}
    r = 7
    for m in months((2017, 1), (2026, 9)):
        core, head = lv[('25', bea_p(m))], lv[('1', bea_p(m))]
        put(ws, r, 1, m)
        put(ws, r, 2, core, FMT_LVL)
        put(ws, r, 3, head, FMT_LVL)
        T_ROW[m] = r
        T_LV[m] = {'core': core, 'headline': head}
        r += 1
    ws.freeze_panes = 'A7'

    # ======================================================================= raw_Oct_build
    ws = S['raw_Oct_build']
    raw_meta(ws, 'UMD bottom-up October 2026 PCE estimate: summary and component (pricing-line) table', [
        ('Source files', f'{REL(OCT_SUM)}; {REL(OCT_LINES)}'),
        ('URL', 'n/a (our build, 02_Research/Subtasks/04_oct_pce_build; inputs = BLS CPI and PPI Oct 2026 releases)'),
        ('Vintage', 'built 2026-11-13 after the Oct PPI (Nov 13, 8:30 ET); base = BEA Sep 2026 (Oct 29 release)'),
        ('Retrieved', 'n/a (computed); audited in 06_Audits/04_oct_pce_build')])
    summ = {x['measure']: x for x in rd(OCT_SUM)}
    cols = ['measure', 'estimate_mm', 'band_reported', 'band_1m_ann', 'band_3m_ann', 'band_6m_ann', 'band_12m',
            'rate_1m_ann', 'rate_3m_ann', 'rate_6m_ann', 'rate_12m', 'share_assumed']
    hdr_row(ws, 6, 1, cols, [12] + [13] * (len(cols) - 1))
    OB = {}
    for i, mname in enumerate(['core', 'headline']):
        rr = 7 + i
        for j, cname in enumerate(cols):
            v = summ[mname][cname]
            put(ws, rr, 1 + j, v if j == 0 else num(v), None if j == 0 else '0.00000', fill=FILL_EST if j else None)
            OB[(mname, cname)] = f'raw_Oct_build!${get_column_letter(1 + j)}${rr}'
    OBV = {(m, c): num(summ[m][c]) for m in ('core', 'headline') for c in cols[1:]}
    ws.cell(row=10, column=1, value='Component (pricing-line) table: pi = line m/m % (Oct 2026 est.); w_c / w_h = Sep 2026 shares in core / headline; tier = build source tier ("assumed" = carried forward)').font = F_BOLD
    lines = rd(OCT_LINES)
    lcols = ['line', 'leaf', 'name', 'cat', 'tier_used', 'seasonal', 'inputs', 'pi', 'w_c', 'w_h', 'contrib_c', 'contrib_h', 'provenance']
    hdr_row(ws, 11, 1, lcols, [7, 7, 40, 22, 14, 10, 28, 10, 10, 10, 10, 10, 60])
    OL_ROW = {}
    for i, x in enumerate(lines):
        rr = 12 + i
        for j, cname in enumerate(lcols):
            v = x[cname]
            nv = num(v) if cname in ('line', 'leaf', 'pi', 'w_c', 'w_h', 'contrib_c', 'contrib_h') else None
            c = put(ws, rr, 1 + j, nv if nv is not None else v, '0.00000' if cname in ('pi', 'w_c', 'w_h', 'contrib_c', 'contrib_h') else None)
            if cname == 'cat' and v == 'assumed':
                c.fill = FILL_CF
        OL_ROW[int(x['line'])] = rr
    OCT_PI = {int(x['line']): num(x['pi']) for x in lines}
    OCT_CAT = {int(x['line']): x['cat'] for x in lines}
    ws.freeze_panes = 'A12'

    # ======================================================================= raw_PCE_components
    import C_common as cc   # unit list and start-of-window sub-line nominal weights (Agent C, audited code path)
    ws = S['raw_PCE_components']
    raw_meta(ws, 'BEA PCE detail (U20404 price indexes, U20405 nominal spending): the 184 core pricing lines used for breadth and the sum gap', [
        ('Source files', f'{REL(U20404)}; {REL(U20405)}'),
        ('URL', 'https://apps.bea.gov/api/data (DataSetName=NIUnderlyingDetail, TableName=U20404 / U20405, Frequency=M)'),
        ('Vintage', 'Oct 29, 2026 release (data through Sep 2026); files saved 2026-11-10'),
        ('Retrieved', '2026-11-10. Weights W_* are start-of-window nominal $ (millions, SAAR) per sub-line: leaf nominal x sub-line share of the leaf (C_common.nominal_weight). Line 157 (CPI rent sub-line) is priced on the leaf-156 index.')])
    units = cc.units('sub', cc.SCOPES['core'])
    PM = ['2025-09', '2025-10', '2026-06', '2026-07', '2026-09']
    WM = ['2025-09', '2025-10', '2026-06', '2026-07']
    pcols = ['line', 'leaf', 'name', 'price line used'] + [f'P_{m}' for m in PM] + [f'W_{m}' for m in WM]
    hdr_row(ws, 6, 1, pcols, [7, 7, 44, 9] + [11] * 5 + [13] * 4)
    names = {int(x['line']): x['name'] for x in lines}
    PC_ROW, PCV = {}, {}
    for i, (ln, lf) in enumerate(units):
        rr = 7 + i
        pl = cc.bl(ln)
        vals = [ln, lf, names.get(ln, ''), pl] + [float(cc.index_level(ln, m, 'sub')) for m in PM] + \
               [float(cc.nominal_weight(ln, lf, m, 'sub')) for m in WM]
        for j, v in enumerate(vals):
            put(ws, rr, 1 + j, v, FMT_LVL if 4 <= j < 9 else ('#,##0' if j >= 9 else None))
        PC_ROW[ln] = rr
        PCV[ln] = dict(zip(pcols, vals))
    note(ws['E6'], 'Price index levels from U20404 (2017=100). For line 157 the leaf-156 (tenant rent) index is used, as in C_common.bl().')
    note(ws['J6'], 'Nominal weights computed by C_common.nominal_weight() from U20405: leaf nominal $ x (sub-line nominal / sum of the leaf\'s sub-lines).')
    ws.freeze_panes = 'E7'

    # ======================================================================= raw_PCE_leaves (central breadth method, Eli E5 Nov 15)
    ws = S['raw_PCE_leaves']
    raw_meta(ws, 'BEA PCE detail (U20404 price indexes, U20405 nominal spending): the 149 core leaves used for the central (weighted-leaf) breadth figure', [
        ('Source files', f'{REL(U20404)}; {REL(U20405)}; Oct 2026 leaf estimate from {REL(OCT_LINES)}'),
        ('URL', 'https://apps.bea.gov/api/data (DataSetName=NIUnderlyingDetail, TableName=U20404 / U20405, Frequency=M)'),
        ('Vintage', 'Oct 29, 2026 release (data through Sep 2026); files saved 2026-11-10. Oct 2026 = UMD est. (built 2026-11-13)'),
        ('Retrieved', '2026-11-10. W_* = leaf nominal $ (millions, SAAR) at the base month of each window (start-of-window weights). P_2026-10 est. = Sep level x (1 + fixed-share roll-up of the leaf\'s sub-line m/m), C_common.index_level(leaf, "2026-10", "leaf").')])
    leaf_desc = {}
    for r_ in bea(U20404)[0]:
        leaf_desc.setdefault(int(r_['LineNumber']), r_['LineDescription'])
    LPM = ['2025-09', '2025-10', '2026-06', '2026-07', '2026-09', '2026-10']
    lcols2 = ['leaf', 'name'] + [f'P_{m}' + (' est.' if m == '2026-10' else '') for m in LPM] + [f'W_{m}' for m in WM]
    hdr_row(ws, 6, 1, lcols2, [7, 44] + [11] * 6 + [13] * 4)
    LF_ROW, LFV = {}, {}
    for i, lf in enumerate(int(x) for x in cc.LEAVES_CORE):
        rr = 7 + i
        vals = [lf, leaf_desc.get(lf, '')] + [float(cc.index_level(lf, m, 'leaf')) for m in LPM] + \
               [float(cc.nominal_weight(lf, lf, m, 'leaf')) for m in WM]
        for j, v in enumerate(vals):
            put(ws, rr, 1 + j, v, FMT_LVL if 2 <= j < 8 else ('#,##0' if j >= 8 else None), fill=FILL_EST if j == 7 else None)
        LF_ROW[lf] = rr
        LFV[lf] = dict(zip(['leaf', 'name'] + [f'P_{m}' for m in LPM] + [f'W_{m}' for m in WM], vals))
    note(ws['H6'], 'Oct 2026 estimate: Sep 2026 leaf level x (1 + fixed-share (Sep within-leaf shares) roll-up of the build\'s sub-line m/m), computed by C_common.index_level(leaf, "2026-10", "leaf") (09_slide1_research/code/C_common.py). Unsplit leaves = the build\'s line m/m.')
    note(ws['I6'], 'Leaf nominal spending from U20405 (C_common.nominal_weight(leaf, leaf, month, "leaf")).')
    ws.freeze_panes = 'C7'

    # ======================================================================= raw_backtest
    ws = S['raw_backtest']
    bt = rd(os.path.join(OUT, 'A_backtest.csv'))
    raw_meta(ws, 'Backtest inputs: UMD estimate, Cleveland nowcast and core-CPI benchmark vs BEA first print (m/m %, SA)', [
        ('Source files', '02_Research/Subtasks/04_oct_pce_build/outputs/D2_backtest_variant_first_release_pm.csv; backtest_results.csv (via 09_slide1_research/outputs/A_backtest.csv)'),
        ('URL', 'BEA first prints from ALFRED vintages (https://alfred.stlouisfed.org, PCEPI / PCEPILFE); Cleveland: https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting'),
        ('Vintage', 'first-release variant; Dec 2025 - Sep 2026 (n=10)'),
        ('Retrieved', 'build 2026-11-13/14; Cleveland = last nowcast before each BEA release')])
    bcols = ['period', 'first_print_vintage', 'core_first_print', 'our_core_est', 'cleveland_core_nowcast', 'core_cpi_ols_est',
             'headline_first_print', 'our_headline_est', 'cleveland_headline_nowcast', 'cleveland_timing', 'core_cpi_note']
    hdr_row(ws, 6, 1, bcols, [10, 12, 12, 12, 12, 12, 12, 12, 12, 26, 30])
    BT = [x for x in bt if x['row_type'] == 'month']
    for i, x in enumerate(BT):
        for j, cname in enumerate(bcols):
            v = x[cname]
            nv = num(v) if j >= 2 and j <= 8 else None
            put(ws, 7 + i, 1 + j, nv if nv is not None else v, '0.0000' if nv is not None else None)
    ws.freeze_panes = 'A7'

    # ======================================================================= raw_outside_estimates
    ws = S['raw_outside_estimates']
    ox = rd(os.path.join(OUT, 'A_outside_existing.csv'))
    dx = rd(os.path.join(OUT, 'D_outside_new.csv'))
    raw_meta(ws, 'Outside estimates of October 2026 PCE, as collected (text as found)', [
        ('Source files', '09_slide1_research/outputs/A_outside_existing.csv (from 04_oct_pce_build/outputs/R_forecaster_oct2026_2026-11-14.csv); outputs/D_outside_new.csv; page extracts in 03_Data/Raw/outside_oct_pce_estimates_2026-11-14/'),
        ('URL', 'per row (column K)'),
        ('Vintage', 'collected 2026-11-14; PPI released 2026-11-13 08:30 ET'),
        ('Retrieved', '2026-11-14; press-reported rows are secondary [2] unless tier says primary')])
    ocols = ['file', 'forecaster', 'tier', 'pre_or_post_PPI', 'core_mm', 'core_yy', 'headline_mm', 'headline_yy',
             'published', 'revised_from', 'URL', 'quote']
    hdr_row(ws, 6, 1, ocols, [8, 30, 26, 22, 10, 9, 10, 10, 28, 18, 50, 70])
    RAWO = []
    rr = 7
    for x in ox:
        vals = ['A', x['forecaster'], x['tier'], x['pre_or_post_PPI'], x['core_mm'], x['core_yy'], x['headline_mm'],
                x['headline_yy'], x['outlet_and_date'], x['revised_from'], x['url'], x['quote_or_note']]
        RAWO.append((rr, vals))
        rr += 1
    zx = rd(os.path.join(OUT, 'Z_outside_updates.csv')) if os.path.exists(os.path.join(OUT, 'Z_outside_updates.csv')) else []
    ZTIER = {z['forecaster']: z for z in zx}
    for x in dx:
        vals = ['D', x['forecaster'], x['tier'], x['pre_or_post_PPI'], x['core_mm'], x['core_yy'], x['headline_mm'],
                x['headline_yy'], x['published'], x['revised_from'], x['URL'], x['exact quote']]
        RAWO.append((rr, vals))
        rr += 1
    for z in zx:
        vals = ['Z', z['forecaster'] + ' [coordinator update]', z['tier'], z['pre_or_post_PPI'], z['core_mm'], z['core_yy'], z['headline_mm'],
                z['headline_yy'], z['published'], '', z['URL'], z['quote'] + ' (raw: ' + z['raw_file'] + ')']
        RAWO.append((rr, vals))
        rr += 1
    for rr, vals in RAWO:
        for j, v in enumerate(vals):
            nv = num(v) if 4 <= j <= 7 else None
            c = put(ws, rr, 1 + j, nv if nv is not None else v, '0.00' if nv is not None else None)
            if 'press' in vals[2] or 'secondary' in vals[2] or 'consensus' in vals[2]:
                if j == 2:
                    c.fill = FILL_PRESS
    ws.freeze_panes = 'C7'

    # ======================================================================= raw_Cleveland
    ws = S['raw_Cleveland']
    cl = rd(os.path.join(OUT, 'A_r5_cleveland.csv'))
    raw_meta(ws, 'Cleveland Fed inflation nowcast for October 2026 PCE: daily path (carried forward: Nov 14 pull; re-pull Nov 18)', [
        ('Source files', '03_Data/Raw/ClevelandFed_nowcast_month_2026-11-14.json; ClevelandFed_nowcast_year_2026-11-14.json (via 04_oct_pce_build/outputs/R_cleveland_oct2026_2026-11-14.csv and 09_slide1_research/outputs/A_r5_cleveland.csv)'),
        ('URL', 'https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting'),
        ('Vintage', 'chart updated 2026-11-13 (unchanged since the 2026-11-10 update that followed Oct CPI); model uses no PPI'),
        ('Retrieved', '2026-11-14. CARRIED FORWARD: re-pull Nov 18 before the data cutoff')])
    ccols = ['nowcast_date', 'target_month', 'measure', 'mm_pct', 'yy_pct', 'is_latest', 'label']
    hdr_row(ws, 6, 1, ccols, [12, 12, 10, 10, 10, 9, 36])
    CL_ROW = {}
    for i, x in enumerate(cl):
        for j, cname in enumerate(ccols):
            v = x[cname]
            nv = num(v) if cname in ('mm_pct', 'yy_pct') else None
            put(ws, 7 + i, 1 + j, nv if nv is not None else v, '0.0000' if nv is not None else None, fill=FILL_CF)
        CL_ROW[(x['nowcast_date'], x['measure'])] = 7 + i
    ws.freeze_panes = 'A7'

    # ======================================================================= raw_BEA_release_text
    ws = S['raw_BEA_release_text']
    r4 = rd(os.path.join(OUT, 'A_r4_sep_check.csv'))
    raw_meta(ws, 'Quoted sentences: BEA September 2026 Personal Income and Outlays release and Fed officials (R4)', [
        ('Source files', '03_Data/Raw/BEA_PIO_release_Sep2026_2026-11-14/personal-income-and-outlays-september-2026.html; 02_Research/External_views/Fed_officials_2026-11/speeches/ (per row)'),
        ('URL', 'https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026 (release Oct 29, 2026); speeches: federalreserve.gov / regional Fed sites'),
        ('Vintage', 'BEA release Oct 29, 2026; speeches Nov 10-13, 2026'),
        ('Retrieved', '2026-11-14 (BEA html); speeches saved Nov 2026')])
    tcols = ['item', 'source', 'measure', 'metric', 'stated value (%)', 'quote', 'location', 'source file']
    hdr_row(ws, 6, 1, tcols, [6, 26, 10, 22, 12, 90, 40, 60])
    TX_ROW = {}
    rr = 7
    for x in r4:
        if x['item'] == 'a':
            continue
        vals = [x['item'], x['source'], x['measure'], x['metric'], num(x['value']), x['quote'], x['location'], x['source_file']]
        for j, v in enumerate(vals):
            c = put(ws, rr, 1 + j, v, '0.0' if j == 4 and v is not None else None)
            if j == 5:
                c.alignment = Alignment(wrap_text=True, vertical='top')
        TX_ROW[(x['source'], x['measure'], x['metric'])] = rr
        rr += 1
    ws.freeze_panes = 'A7'

    # ======================================================================= TS_PCE_rates
    ws = S['TS_PCE_rates']
    header(ws, 'PCE inflation rates, monthly, Jan 2018 - Oct 2026 (Oct = UMD estimate)',
           'Core and headline PCE price index: 1-month %, 3-month and 6-month annualized %, 12-month %. Data only.',
           'Units: percent; SA; Fisher index 2017=100. Vintage: BEA Oct 29, 2026 release (saved Nov 10). Draws on raw_PCE_T20804 (levels) and raw_Oct_build (Oct m/m est.). Oct row = est. (amber).')
    hdr_row(ws, 5, 1, ['Month', 'Core index', 'Headline index', 'Status', 'Core 1m %', 'Core 3m ann. %', 'Core 6m ann. %',
                       'Core 12m %', 'Headline 1m %', 'Headline 3m ann. %', 'Headline 6m ann. %', 'Headline 12m %', '2% target'],
            [14, 11, 11, 10, 10, 11, 11, 11, 11, 12, 12, 12, 9])
    TS_ROW = {}
    LV = {m: dict(T_LV[m]) for m in T_LV}
    LV['2026-10'] = {k: T_LV['2026-09'][k] * (1 + OBV[(k, 'estimate_mm')] / 100) for k in ('core', 'headline')}
    allm = list(months((2017, 1), (2026, 10)))
    ts_months = [m for m in allm if m >= '2018-01']
    TSV = {}

    def lref(meas, m):
        col = 'B' if meas == 'core' else 'C'
        if m == '2026-10':
            return f'${col}${TS_ROW["2026-10"]}'
        return f'raw_PCE_T20804!${col}${T_ROW[m]}'

    for i, m in enumerate(ts_months):
        TS_ROW[m] = 6 + i
    for m in ts_months:
        rr = TS_ROW[m]
        est = m == '2026-10'
        fill = FILL_EST if est else None
        put(ws, rr, 1, m + (' est.' if est else ''), fill=fill)
        for meas, col in (('core', 2), ('headline', 3)):
            if est:
                f = f'={lref(meas, "2026-09")}*(1+{OB[(meas, "estimate_mm")]}/100)'
            else:
                f = f'={lref(meas, m)}'
            put(ws, rr, col, f, FMT_LVL, expect=LV[m][meas], fill=fill)
        put(ws, rr, 4, 'est.' if est else 'published', fill=fill)
        k = allm.index(m)
        for meas, c0 in (('core', 5), ('headline', 9)):
            lags = {'1m': (1, 1), '3m': (3, 4), '6m': (6, 2), '12m': (12, 1)}
            vals = {}
            for j, (h, (back, pw)) in enumerate(lags.items()):
                mb = allm[k - back]
                v = ((LV[m][meas] / LV[mb][meas]) ** pw - 1) * 100
                vals[h] = v
                f = f'=({lref(meas, m)}/{lref(meas, mb)}-1)*100' if pw == 1 else f'=(({lref(meas, m)}/{lref(meas, mb)})^{pw}-1)*100'
                put(ws, rr, c0 + j, f, FMT_RATE, expect=v, fill=fill)
            TSV[(m, meas)] = vals
        put(ws, rr, 13, 2.0, FMT_RATE)
    last = TS_ROW['2026-10']
    band(ws, 6, last, 1, 13)
    ws.freeze_panes = 'B6'
    # long layout
    lc = 15
    ws.cell(row=4, column=lc, value='Long layout (one row per month x measure; formulas point at the wide block)').font = F_BOLD
    hdr_row(ws, 5, lc, ['Month', 'Measure', 'Status', '1m %', '3m ann. %', '6m ann. %', '12m %'], [14, 10, 10, 9, 10, 10, 9])
    rr = 6
    for m in ts_months:
        for meas, c0 in (('core', 5), ('headline', 9)):
            est = m == '2026-10'
            fill = FILL_EST if est else None
            put(ws, rr, lc, m, fill=fill)
            put(ws, rr, lc + 1, meas, fill=fill)
            put(ws, rr, lc + 2, 'est.' if est else 'published', fill=fill)
            for j, h in enumerate(['1m', '3m', '6m', '12m']):
                put(ws, rr, lc + 3 + j, f'={get_column_letter(c0 + j)}{TS_ROW[m]}', FMT_RATE, expect=TSV[(m, meas)][h], fill=fill)
            rr += 1
    # charts
    ch = LineChart()
    style_chart(ch, 'Core and headline PCE inflation, 12-month % (Oct 2026 = UMD est.)', 'Percent, 12-month change', 'Month',
                'Source: BEA NIPA T2.8.4 (Oct 29, 2026 release); Oct 2026 UMD bottom-up estimate', w=26, h=12, yfmt='0.0')
    for col in (8, 12, 13):
        ch.add_data(Reference(ws, min_col=col, min_row=5, max_row=last), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=last))
    line_style(ch.series[0], '2F5597')
    line_style(ch.series[1], 'C00000')
    line_style(ch.series[2], '7F7F7F', dash='dash', width_pt=1.25)
    ch.x_axis.tickLblSkip = 12
    add_chart(ws, ch, 'X5')
    ch2 = LineChart()
    first24 = TS_ROW['2024-11']
    style_chart(ch2, 'Core PCE momentum, last 24 months: 3m ann. vs 6m ann. vs 12m (Oct 2026 = est.)', 'Percent', 'Month',
                'Source: BEA NIPA T2.8.4; Oct 2026 UMD estimate (last point)', w=26, h=12, yfmt='0.0')
    for col, color in ((6, 'C00000'), (7, 'ED7D31'), (8, '2F5597')):
        s = Series(Reference(ws, min_col=col, min_row=first24, max_row=last), title=ws.cell(row=5, column=col).value)
        line_style(s, color)
        ch2.series.append(s)
    s = Series(Reference(ws, min_col=13, min_row=first24, max_row=last), title='2% target')
    line_style(s, '7F7F7F', dash='dash', width_pt=1.25)
    ch2.series.append(s)
    ch2.set_categories(Reference(ws, min_col=1, min_row=first24, max_row=last))
    add_chart(ws, ch2, 'X30')

    # ======================================================================= Headline
    ws = S['Headline']
    header(ws, 'Slide 1 headline: October 2026 PCE inflation, UMD estimate (est.)',
           'October 2026 core and headline PCE at 1m, 1m annualized, 3m ann., 6m ann. and 12m, with backtest bands; September published alongside. Data only.',
           'Units: percent, SA. Est. = UMD bottom-up build (Nov 13, after PPI). Band = backtest RMSE vs BEA first print (first-release variant, Dec 2025-Sep 2026, n=10), scaled to horizon. Draws on TS_PCE_rates and raw_Oct_build.')
    hdr_row(ws, 5, 1, ['Measure', 'Horizon', 'Oct 2026 est.', 'Band (+/-)', 'Low', 'High', 'Sep 2026 published', 'Change, Oct est. minus Sep (pp)'],
            [16, 22, 13, 11, 10, 10, 15, 18])
    HL = {}
    rr = 6
    horizons = [('1m (m/m, not annualized)', 0, 'band_reported', None),
                ('1m annualized', None, 'band_1m_ann', 'rate_1m_ann'),
                ('3m annualized', 1, 'band_3m_ann', None),
                ('6m annualized', 2, 'band_6m_ann', None),
                ('12m', 3, 'band_12m', None)]
    for meas, c0 in (('core', 5), ('headline', 9)):
        for hname, j, bcol, _ in horizons:
            if j is None:
                c1m = f'TS_PCE_rates!{get_column_letter(c0)}'
                f_est = f'=((1+{c1m}{TS_ROW["2026-10"]}/100)^12-1)*100'
                f_sep = f'=((1+{c1m}{TS_ROW["2026-09"]}/100)^12-1)*100'
                e = ((1 + TSV[('2026-10', meas)]['1m'] / 100) ** 12 - 1) * 100
                sp = ((1 + TSV[('2026-09', meas)]['1m'] / 100) ** 12 - 1) * 100
            else:
                h = ['1m', '3m', '6m', '12m'][j]
                col = get_column_letter(c0 + j)
                f_est = f'=TS_PCE_rates!{col}{TS_ROW["2026-10"]}'
                f_sep = f'=TS_PCE_rates!{col}{TS_ROW["2026-09"]}'
                e = TSV[('2026-10', meas)][h]
                sp = TSV[('2026-09', meas)][h]
            b = OBV[(meas, bcol)]
            put(ws, rr, 1, meas, bold=True)
            put(ws, rr, 2, hname)
            put(ws, rr, 3, f_est, FMT_RATE, expect=e, fill=FILL_EST, bold=(j == 3))
            put(ws, rr, 4, f'={OB[(meas, bcol)]}', FMT_RATE, expect=b)
            put(ws, rr, 5, f'=C{rr}-D{rr}', FMT_RATE, expect=e - b)
            put(ws, rr, 6, f'=C{rr}+D{rr}', FMT_RATE, expect=e + b)
            put(ws, rr, 7, f_sep, FMT_RATE, expect=sp)
            put(ws, rr, 8, f'=C{rr}-G{rr}', FMT_RATE, expect=e - sp)
            HL[(meas, hname)] = (rr, e)
            rr += 1
    note(ws['D5'], 'Band source: raw_Oct_build (D_build_2026-10_summary.csv band_* columns): first-release backtest RMSE (core 0.0489, headline 0.0452 pp m/m), x4 for 3m ann., x2 for 6m ann., x1 for 12m, x12 for 1m ann.')
    for (meas, h), (r_, _) in HL.items():
        if h == '12m':
            ws.cell(row=r_, column=3).fill = FILL_KEY
    band(ws, 6, rr - 1, 1, 8)
    ws.freeze_panes = 'A6'
    rr += 1
    section(ws, rr, 'Sep -> Oct m/m (1-month, not annualized)')
    rr += 1
    hdr_row(ws, rr, 1, ['Measure', 'Sep 2026 m/m (BEA)', 'Oct 2026 m/m (est.)', 'Change (pp)'])
    for meas, c0 in (('core', 5), ('headline', 9)):
        rr += 1
        col = get_column_letter(c0)
        put(ws, rr, 1, meas, bold=True)
        put(ws, rr, 2, f'=TS_PCE_rates!{col}{TS_ROW["2026-09"]}', '0.000', expect=TSV[('2026-09', meas)]['1m'])
        put(ws, rr, 3, f'=TS_PCE_rates!{col}{TS_ROW["2026-10"]}', '0.000', expect=TSV[('2026-10', meas)]['1m'], fill=FILL_EST)
        put(ws, rr, 4, f'=C{rr}-B{rr}', '0.000', expect=TSV[('2026-10', meas)]['1m'] - TSV[('2026-09', meas)]['1m'])
    # chart data (core): 1m ann, 3m, 6m, 12m
    rr += 2
    section(ws, rr, 'Chart data: core PCE, Oct 2026 est. vs Sep 2026 published (annualized horizons)')
    rr += 1
    hdr_row(ws, rr, 1, ['Horizon', 'Oct 2026 est.', 'Sep 2026 published', 'Band (+/-)', '2% target'])
    cd0 = rr + 1
    for hname in ['1m annualized', '3m annualized', '6m annualized', '12m']:
        rr += 1
        src, e = HL[('core', hname)]
        put(ws, rr, 1, hname)
        put(ws, rr, 2, f'=C{src}', FMT_RATE, expect=e, fill=FILL_EST)
        put(ws, rr, 3, f'=G{src}', FMT_RATE, expect=EXPECT[('Headline', f'G{src}')])
        put(ws, rr, 4, f'=D{src}', FMT_RATE, expect=EXPECT[('Headline', f'D{src}')])
        put(ws, rr, 5, 2.0, FMT_RATE)
    cd1 = rr
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, 'Core PCE inflation by horizon: Oct 2026 est. (with backtest band) vs Sep 2026', 'Percent (annualized; 12m = y/y)', 'Horizon',
                'Source: BEA NIPA T2.8.4; UMD bottom-up Oct estimate; band = backtest RMSE', w=20, h=11, yfmt='0.0')
    s_est = Series(Reference(ws, min_col=2, min_row=cd0, max_row=cd1), title='Oct 2026 est.')
    s_est.graphicalProperties.solidFill = 'C00000'
    s_est.errBars = ErrorBars(errDir='y', errBarType='both', errValType='cust', noEndCap=False,
                              plus=NumDataSource(numRef=NumRef(f=f"Headline!$D${cd0}:$D${cd1}")),
                              minus=NumDataSource(numRef=NumRef(f=f"Headline!$D${cd0}:$D${cd1}")))
    s_sep = Series(Reference(ws, min_col=3, min_row=cd0, max_row=cd1), title='Sep 2026 published')
    s_sep.graphicalProperties.solidFill = '8EA9DB'
    bc.series += [s_est, s_sep]
    bc.set_categories(Reference(ws, min_col=1, min_row=cd0, max_row=cd1))
    lc2 = LineChart()
    s2 = Series(Reference(ws, min_col=5, min_row=cd0, max_row=cd1), title='2% target')
    line_style(s2, '7F7F7F', dash='dash', width_pt=1.25)
    lc2.series.append(s2)
    bc += lc2
    add_chart(ws, bc, 'J5')

    # ======================================================================= R1_backtest
    ws = S['R1_backtest']
    header(ws, 'R1: How accurate is the October method? Backtest vs BEA first print, Dec 2025 - Sep 2026',
           'Month-by-month m/m estimates (ours, Cleveland nowcast, core-CPI regression benchmark) vs BEA first print, errors, and summary MAE / RMSE / bias. Data only.',
           'Units: percent m/m, SA; error = estimate minus BEA first print (pp). First-release variant, n=10. Draws on raw_backtest. "Core CPI alone" = expanding-window OLS of core PCE m/m on core CPI m/m (bench2_core_cpi_ols), not raw core CPI.')
    hdr_row(ws, 5, 1, ['Month', 'Core: BEA first print', 'Core: ours', 'Core: Cleveland', 'Core: CPI benchmark',
                       'Core err: ours', 'Core err: Cleveland', 'Core err: CPI bench',
                       'Headline: BEA first print', 'Headline: ours', 'Headline: Cleveland', 'Headline err: ours', 'Headline err: Cleveland'],
            [10] + [12] * 12)
    R1E = {k: [] for k in ('co', 'cc', 'cb', 'ho', 'hc')}
    for i, x in enumerate(BT):
        rr = 6 + i
        rw = 7 + i
        put(ws, rr, 1, x['period'])
        vals = {}
        for col, rcol, key in ((2, 'C', 'core_first_print'), (3, 'D', 'our_core_est'), (4, 'E', 'cleveland_core_nowcast'),
                               (5, 'F', 'core_cpi_ols_est'), (9, 'G', 'headline_first_print'), (10, 'H', 'our_headline_est'),
                               (11, 'I', 'cleveland_headline_nowcast')):
            v = num(x[key])
            vals[key] = v
            put(ws, rr, col, f'=raw_backtest!{rcol}{rw}', '0.000', expect=v)
        for col, a, b, k in ((6, 'C', 'B', 'co'), (7, 'D', 'B', 'cc'), (8, 'E', 'B', 'cb'), (12, 'J', 'I', 'ho'), (13, 'K', 'I', 'hc')):
            ka = {'C': 'our_core_est', 'D': 'cleveland_core_nowcast', 'E': 'core_cpi_ols_est', 'J': 'our_headline_est', 'K': 'cleveland_headline_nowcast'}[a]
            kb = {'B': 'core_first_print', 'I': 'headline_first_print'}[b]
            e = vals[ka] - vals[kb]
            R1E[k].append(e)
            put(ws, rr, col, f'={a}{rr}-{b}{rr}', '0.000', expect=e)
    r_last = 6 + len(BT) - 1
    band(ws, 6, r_last, 1, 13)
    rr = r_last + 2
    section(ws, rr, 'Summary (pp, m/m)')
    rr += 1
    hdr_row(ws, rr, 1, ['Statistic', '', '', '', '', 'Core: ours', 'Core: Cleveland', 'Core: CPI bench', '', '', '', 'Headline: ours', 'Headline: Cleveland'])
    stats = [('n', lambda L: len(L), lambda c: f'=COUNT({c}6:{c}{r_last})'),
             ('Bias (mean error)', lambda L: sum(L) / len(L), lambda c: f'=AVERAGE({c}6:{c}{r_last})'),
             ('MAE', lambda L: sum(abs(v) for v in L) / len(L), lambda c: f'=SUMPRODUCT(ABS({c}6:{c}{r_last}))/COUNT({c}6:{c}{r_last})'),
             ('RMSE', lambda L: math.sqrt(sum(v * v for v in L) / len(L)), lambda c: f'=SQRT(SUMSQ({c}6:{c}{r_last})/COUNT({c}6:{c}{r_last}))')]
    R1S = {}
    for sname, fn, ff in stats:
        rr += 1
        put(ws, rr, 1, sname, bold=True)
        for col, k in ((6, 'co'), (7, 'cc'), (8, 'cb'), (12, 'ho'), (13, 'hc')):
            c = get_column_letter(col)
            v = fn(R1E[k])
            put(ws, rr, col, ff(c), '0' if sname == 'n' else '0.0000', expect=v, fill=FILL_KEY if sname == 'MAE' else None)
            R1S[(sname, k)] = v
    ws.freeze_panes = 'B6'
    ch = BarChart()
    ch.type = 'col'
    style_chart(ch, 'Core PCE m/m error vs BEA first print: ours vs Cleveland vs core-CPI benchmark', 'Error, pp (estimate minus first print)', 'Month',
                'Source: 04_oct_pce_build backtest (first-release variant); BEA first prints via ALFRED; Cleveland Fed nowcast', w=24, h=11, yfmt='0.00')
    for col in (6, 7, 8):
        ch.add_data(Reference(ws, min_col=col, min_row=5, max_row=r_last), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=6, max_row=r_last))
    for s_, color in zip(ch.series, ('C00000', '8EA9DB', 'A5A5A5')):
        s_.graphicalProperties.solidFill = color
        s_.graphicalProperties.line.solidFill = color
    add_chart(ws, ch, 'O5')

    # ======================================================================= R2_outside_estimates
    ws = S['R2_outside_estimates']
    header(ws, 'R2: Outside estimates of October 2026 PCE vs UMD',
           'Every outside October estimate found, with tier and timing; median and range of the named, independent, post-PPI estimates and UMD\'s distance in bp. Data only.',
           'Units: core/headline m/m % and y/y %. Counted set = named forecasters, published after the Nov 13 8:30 ET PPI, one row each (consensus lines, models, officials and pre-PPI notes excluded). Draws on raw_outside_estimates. Blue = press-reported.')
    rcols = ['Forecaster', 'Tier', 'Pre/post PPI', 'Core m/m %', 'Core y/y %', 'Headline m/m %', 'Headline y/y %',
             'Published / outlet', 'Counted in median?', 'Why / why not', 'Core m/m if counted', 'raw_outside_estimates row', 'URL',
             'Two-decimal figure?', 'Core m/m if counted and two-decimal']
    hdr_row(ws, 5, 1, rcols, [30, 26, 16, 10, 10, 11, 11, 32, 10, 38, 11, 10, 50, 10, 12])
    COUNT_RULE = {
        'Goldman Sachs': ('Y', 'named, post-PPI'),
        'Bank of America': ('Y', 'named, post-PPI'),
        'Capital Economics (Thomas Ryan)': ('Y', 'named, post-PPI'),
        'Morgan Stanley': ('Y', 'named, post-PPI; 1-decimal (0.3) treated as 0.30'),
    }
    rows_r2 = []
    for rr_raw, vals in RAWO:
        fc = vals[1]
        if fc.startswith('Pantheon Macroeconomics (repeat') or vals[0] == 'Z':
            continue    # duplicate rows: Pantheon repeat (same Nov 10 note); coordinator updates are applied to the original row below
        rule = COUNT_RULE.get(fc)
        if rule is None:
            why = ('our estimate' if fc.startswith('UMD') else 'model nowcast, no PPI' if fc.startswith('Cleveland')
                   else 'consensus line, not an independent forecaster' if ('Consensus' in fc or 'unnamed' in fc)
                   else 'official; 12m core only; pre-PPI' if 'Bowman' in fc else 'pre-PPI (superseded or not updated)')
            rule = ('N', why)
        rows_r2.append((rr_raw, vals, rule))
    R2V = []
    for i, (rr_raw, vals, rule) in enumerate(rows_r2):
        rr = 6 + i
        press = any(t in vals[2] for t in ('press', 'secondary', 'consensus'))
        put(ws, rr, 1, vals[1], bold=vals[1].startswith('UMD'), fill=FILL_EST if vals[1].startswith('UMD') else None)
        if vals[1] in ZTIER:
            z = ZTIER[vals[1]]
            c = put(ws, rr, 2, z['tier'])
            zrow = [r_ for r_, v_ in RAWO if v_[0] == 'Z' and v_[1].startswith(vals[1])][0]
            note(c, f"Upgraded from '{vals[2]}' (raw_outside_estimates row {rr_raw}) to primary: {z['note']} Source: {z['URL']}; extract {z['raw_file']} (raw_outside_estimates row {zrow}). Numbers unchanged.")
            vals = list(vals)
            vals[10] = z['URL']
        else:
            put(ws, rr, 2, vals[2], fill=FILL_PRESS if press else None)
        put(ws, rr, 3, vals[3])
        core_val = None
        for j, rc in ((4, 'E'), (5, 'F'), (6, 'G'), (7, 'H')):
            v = num(vals[j])
            if v is not None:
                put(ws, rr, j, f'=raw_outside_estimates!{rc}{rr_raw}', '0.00' if j in (4, 6) else '0.00', expect=v)
            elif vals[j]:
                if j == 4 and vals[1] == 'Morgan Stanley':
                    v = 0.30
                    c = put(ws, rr, j, v, '0.00')
                    note(c, f'raw text: "{vals[j]}". Press report gives 0.3% (one decimal); entered as 0.30 for the median. True value could be 0.25-0.34.')
                else:
                    c = put(ws, rr, j, vals[j])
            if j == 4:
                core_val = v
        put(ws, rr, 8, vals[8])
        put(ws, rr, 9, rule[0], bold=rule[0] == 'Y', fill=FILL_KEY if rule[0] == 'Y' else None)
        put(ws, rr, 10, rule[1])
        put(ws, rr, 11, f'=IF(I{rr}="Y",D{rr},"")', '0.00', expect=core_val if rule[0] == 'Y' else '')
        put(ws, rr, 12, rr_raw)
        put(ws, rr, 13, vals[10])
        twodp = 'N' if vals[1] == 'Morgan Stanley' else 'Y'
        put(ws, rr, 14, twodp)
        put(ws, rr, 15, f'=IF(AND(I{rr}="Y",N{rr}="Y"),D{rr},"")', '0.00', expect=core_val if (rule[0] == 'Y' and twodp == 'Y') else '')
        R2V.append((vals[1], rule[0], core_val, rr, twodp))
    r_last = 6 + len(rows_r2) - 1
    band(ws, 6, r_last, 1, 15)
    counted = [v for _, f, v, _, _ in R2V if f == 'Y']
    counted2 = [v for _, f, v, _, t in R2V if f == 'Y' and t == 'Y']
    umd_row = [r for n, _, _, r, _ in R2V if n.startswith('UMD')][0]
    umd = [v for n, _, v, _, _ in R2V if n.startswith('UMD')][0]
    cle_row = [r for n, _, _, r, _ in R2V if n.startswith('Cleveland')][0]
    cle = [v for n, _, v, _, _ in R2V if n.startswith('Cleveland')][0]
    rr = r_last + 2
    section(ws, rr, 'Corroboration line (core m/m, counted set)')
    rng = f'K6:K{r_last}'
    med = statistics.median(counted)
    summ_rows = [('n counted', f'=COUNT({rng})', len(counted), '0'),
                 ('Median core m/m %', f'=MEDIAN({rng})', med, '0.000'),
                 ('Min', f'=MIN({rng})', min(counted), '0.00'),
                 ('Max', f'=MAX({rng})', max(counted), '0.00'),
                 ('UMD core m/m %', f'=D{umd_row}', umd, '0.000'),
                 ('UMD minus median (bp)', f'=(D{umd_row}-MEDIAN({rng}))*100', (umd - med) * 100, '0.0'),
                 ('Cleveland minus median (bp)', f'=(D{cle_row}-MEDIAN({rng}))*100', (cle - med) * 100, '0.0'),
                 ('Median, two-decimal figures only (excl. Morgan Stanley 0.3)', f'=MEDIAN(O6:O{r_last})', statistics.median(counted2), '0.000'),
                 ('n, two-decimal figures only', f'=COUNT(O6:O{r_last})', len(counted2), '0')]
    R2S = {}
    for lbl, f, v, fmt in summ_rows:
        rr += 1
        put(ws, rr, 1, lbl, bold=True)
        put(ws, rr, 4, f, fmt, expect=v, fill=FILL_KEY)
        R2S[lbl] = v
    rr += 1
    put(ws, rr, 1, 'Goldman, BofA and Morgan Stanley are press-reported [2]; Capital Economics is primary (public intro of its Nov 13 note). Morgan Stanley is reported only to one decimal (0.3), so the coded median assumes 0.30; with an MS value anywhere that rounds to 0.3, the median lies in 0.290-0.295. Forecasters share the same CPI/PPI inputs, so agreement is not four independent measurements.')
    # chart data
    rr += 2
    section(ws, rr, 'Chart data: core m/m by source (post-PPI named + UMD + Cleveland)')
    rr += 1
    # one series per group (counted outside estimates / UMD / Cleveland) so colours and markers render in every app
    hdr_row(ws, rr, 1, ['Source', 'Counted outside estimate', 'Median of counted', 'UMD (est.)', 'Cleveland (model, not counted)'])
    c0 = rr + 1
    chart_src = [(n, r) for n, f, v, r, _ in R2V if f == 'Y'] + [('UMD (est.)', umd_row), ('Cleveland (model)', cle_row)]
    for n, r in chart_src:
        rr += 1
        put(ws, rr, 1, n)
        v = [vv for nn, _, vv, r2, _ in R2V if r2 == r][0]
        col = 4 if n.startswith('UMD') else 5 if n.startswith('Cleveland') else 2
        put(ws, rr, col, f'=D{r}', '0.00', expect=v, fill=FILL_EST if col == 4 else None)
        put(ws, rr, 3, f'=MEDIAN({rng})', '0.000', expect=med)
    c1 = rr
    # Dot chart (not bars): the estimates differ by 1-3 bp, so a bar axis that does not start at zero would exaggerate them.
    dc = LineChart()
    style_chart(dc, 'October 2026 core PCE m/m: outside estimates vs UMD and median of counted', 'Percent m/m', 'Source',
                'Source: Goldman, BofA, Morgan Stanley via press reports; Capital Economics note (Nov 13); UMD build; Cleveland Fed nowcast (model, not counted)',
                w=22, h=11, yfmt='0.00')
    for col, sym, size, color in ((2, 'circle', 10, '2F5597'), (4, 'diamond', 13, 'C00000'), (5, 'circle', 10, 'A5A5A5')):
        s = Series(Reference(ws, min_col=col, min_row=c0 - 1, max_row=c1), title_from_data=True)
        s.graphicalProperties.line.noFill = True
        s.smooth = False
        s.marker = Marker(symbol=sym, size=size)
        s.marker.graphicalProperties = GraphicalProperties(solidFill=color)
        s.marker.graphicalProperties.line.solidFill = color
        dc.series.append(s)
    s3 = Series(Reference(ws, min_col=3, min_row=c0 - 1, max_row=c1), title_from_data=True)
    line_style(s3, '000000', dash='dash', width_pt=1.25)
    dc.series.append(s3)
    dc.set_categories(Reference(ws, min_col=1, min_row=c0, max_row=c1))
    dc.y_axis.scaling.min = 0.25
    dc.y_axis.scaling.max = 0.32
    dc.y_axis.majorUnit = 0.01
    add_chart(ws, dc, 'O5')
    ws.freeze_panes = 'B6'

    # ======================================================================= R4_sep_pce_check
    ws = S['R4_sep_pce_check']
    header(ws, 'R4: What was September 2026 PCE inflation? Index levels vs BEA release text vs Fed officials',
           'September 2026 headline and core PCE y/y: computed from index levels (3 decimals), as stated by BEA, and as stated by each official. Data only.',
           'Units: percent y/y, SA. Vintage: BEA Oct 29, 2026 release. Draws on raw_PCE_T20804 (levels) and raw_BEA_release_text (quotes).')
    hdr_row(ws, 5, 1, ['Source', 'Measure', 'Sep 2026 y/y %', 'Difference vs BEA text (pp)', 'Quote location / note'], [30, 10, 14, 16, 70])
    rr = 6
    R4 = {}
    for meas, col in (('headline', 'C'), ('core', 'B')):
        v = (T_LV['2026-09'][meas] / T_LV['2025-09'][meas] - 1) * 100
        put(ws, rr, 1, 'BEA index levels (T20804), 3 dp', bold=True)
        put(ws, rr, 2, meas)
        put(ws, rr, 3, f'=(raw_PCE_T20804!{col}{T_ROW["2026-09"]}/raw_PCE_T20804!{col}{T_ROW["2025-09"]}-1)*100', FMT_RATE3, expect=v, fill=FILL_KEY)
        put(ws, rr, 5, f'levels {T_LV["2026-09"][meas]} / {T_LV["2025-09"][meas]}')
        R4[('levels', meas)] = (rr, v)
        rr += 1
    for meas in ('headline', 'core'):
        rr0, v = R4[('levels', meas)]
        put(ws, rr, 1, 'Index levels rounded to 1 dp')
        put(ws, rr, 2, meas)
        put(ws, rr, 3, f'=ROUND(C{rr0},1)', '0.0', expect=round(v, 1))
        rr += 1
    bea_rows = {}
    for (src, meas, metric), trow in TX_ROW.items():
        if 'y/y' not in metric and '12' not in metric and 'year' not in metric.lower():
            continue
        val = [num(x['value']) for x in r4 if x['source'] == src and x['measure'] == meas and x['metric'] == metric][0]
        put(ws, rr, 1, src, bold=src.startswith('BEA'))
        put(ws, rr, 2, meas)
        if val is not None:
            put(ws, rr, 3, f'=raw_BEA_release_text!E{trow}', '0.0', expect=val)
        else:
            put(ws, rr, 3, 'not stated')
        loc = [x['location'] for x in r4 if x['source'] == src and x['measure'] == meas and x['metric'] == metric][0]
        put(ws, rr, 5, f'raw_BEA_release_text row {trow}: {loc}')
        if src.startswith('BEA'):
            bea_rows[meas] = (rr, val)
        R4[(src, meas)] = (rr, val)
        rr += 1
    for (src, meas), (r_, val) in list(R4.items()):
        if src == 'levels':
            continue
        if meas in bea_rows and val is not None:
            put(ws, r_, 4, f'=C{r_}-C{bea_rows[meas][0]}', '0.0', expect=val - bea_rows[meas][1],
                fill=FILL_EST if abs(val - bea_rows[meas][1]) > 1e-9 else None)
    for meas in ('headline', 'core'):
        r_, v = R4[('levels', meas)]
        put(ws, r_, 4, f'=C{r_}-C{bea_rows[meas][0]}', FMT_RATE3, expect=v - bea_rows[meas][1])
    rr += 1
    put(ws, rr, 1, 'Note: headline 3.649 is 0.001 below the 3.65 rounding boundary; Waller\'s 3.7 is not reproduced by any saved vintage (cause unverified).')
    ws.column_dimensions['A'].width = 34
    ws.freeze_panes = 'A6'

    # ======================================================================= R5_cleveland
    ws = S['R5_cleveland']
    header(ws, 'R5: Cleveland Fed nowcast of October 2026 PCE (carried forward: Nov 14 pull; re-pull Nov 18)',
           'Latest Cleveland Fed nowcast of October core and headline PCE (m/m and y/y), its daily path, and its distance from UMD. Data only.',
           'Units: percent. Model nowcast; uses no PPI. Pulled Nov 14 (chart updated Nov 13). CARRIED FORWARD - re-pull Nov 18. Draws on raw_Cleveland and TS_PCE_rates.')
    hdr_row(ws, 5, 1, ['Measure', 'Cleveland m/m %', 'Cleveland y/y %', 'UMD m/m % (est.)', 'UMD y/y % (est.)', 'UMD minus Cleveland m/m (bp)', 'UMD minus Cleveland y/y (bp)', 'Status'],
            [11, 13, 13, 13, 13, 16, 16, 36])
    latest = [x for x in cl if x['is_latest'] == 'yes']
    rr = 6
    R5 = {}
    for meas, c0 in (('core', 5), ('headline', 9)):
        x = [y for y in latest if y['measure'] == meas][0]
        crow = CL_ROW[(x['nowcast_date'], meas)]
        mm, yy = num(x['mm_pct']), num(x['yy_pct'])
        um, uy = TSV[('2026-10', meas)]['1m'], TSV[('2026-10', meas)]['12m']
        put(ws, rr, 1, meas, bold=True)
        put(ws, rr, 2, f'=raw_Cleveland!D{crow}', '0.000', expect=mm, fill=FILL_CF)
        put(ws, rr, 3, f'=raw_Cleveland!E{crow}', FMT_RATE, expect=yy, fill=FILL_CF)
        put(ws, rr, 4, f'=TS_PCE_rates!{get_column_letter(c0)}{TS_ROW["2026-10"]}', '0.000', expect=um, fill=FILL_EST)
        put(ws, rr, 5, f'=TS_PCE_rates!{get_column_letter(c0 + 3)}{TS_ROW["2026-10"]}', FMT_RATE, expect=uy, fill=FILL_EST)
        put(ws, rr, 6, f'=(D{rr}-B{rr})*100', '0.0', expect=(um - mm) * 100)
        put(ws, rr, 7, f'=(E{rr}-C{rr})*100', '0.0', expect=(uy - yy) * 100)
        put(ws, rr, 8, f'carried forward: Nov 14 pull; re-pull Nov 18 (nowcast date {x["nowcast_date"]})', fill=FILL_CF)
        R5[meas] = (mm, yy)
        rr += 1
    rr += 1
    section(ws, rr, 'Daily nowcast path for October (y/y %)')
    rr += 1
    hdr_row(ws, rr, 1, ['Nowcast date', 'Core y/y %', 'Headline y/y %', 'Core m/m %', 'Headline m/m %'])
    p0 = rr + 1
    dates = sorted(set(x['nowcast_date'] for x in cl))
    for d in dates:
        rr += 1
        put(ws, rr, 1, d, fill=FILL_CF)
        for j, (meas, k, colr) in enumerate((('core', 'yy_pct', 'E'), ('headline', 'yy_pct', 'E'), ('core', 'mm_pct', 'D'), ('headline', 'mm_pct', 'D'))):
            crow = CL_ROW.get((d, meas))
            if crow:
                v = num([x for x in cl if x['nowcast_date'] == d and x['measure'] == meas][0][k])
                put(ws, rr, 2 + j, f'=raw_Cleveland!{colr}{crow}', FMT_RATE if k == 'yy_pct' else '0.000', expect=v, fill=FILL_CF)
    p1 = rr
    ch = LineChart()
    style_chart(ch, 'Cleveland Fed nowcast of October 2026 PCE y/y, by nowcast date (carried forward, Nov 14 pull)', 'Percent, y/y', 'Nowcast date',
                'Source: Federal Reserve Bank of Cleveland, Inflation Nowcasting (pulled 2026-11-14)', w=22, h=11, yfmt='0.0')
    for col, color in ((2, '2F5597'), (3, 'C00000')):
        s_ = Series(Reference(ws, min_col=col, min_row=p0, max_row=p1), title=ws.cell(row=p0 - 1, column=col).value)
        line_style(s_, color)
        ch.series.append(s_)
    ch.set_categories(Reference(ws, min_col=1, min_row=p0, max_row=p1))
    ch.y_axis.scaling.min = 2.5
    ch.y_axis.scaling.max = 4.5
    ch.x_axis.tickLblSkip = 5
    add_chart(ws, ch, 'J5')
    ws.freeze_panes = 'A6'

    # ======================================================================= R6_breadth
    build_r6(S['R6_breadth'], PCV, PC_ROW, OCT_PI, OCT_CAT, OL_ROW, names, LFV, LF_ROW)

    # ======================================================================= R3 / raw_CPI / raw_BEA_9_1U
    import build_slide1_r3 as r3mod
    r3mod.build(S, EXPECT, dict(add_chart=add_chart, LegendEntry=LegendEntry, put=put, hdr_row=hdr_row, header=header, raw_meta=raw_meta, section=section, note=note,
                                band=band, style_chart=style_chart, rd=rd, num=num, FILL_EST=FILL_EST, FILL_KEY=FILL_KEY,
                                FILL_PRESS=FILL_PRESS, FMT_RATE=FMT_RATE, OUT=OUT, ROOT=ROOT, TS_ROW=TS_ROW, TSV=TSV))

    # ======================================================================= Sources, Judgment_calls, README
    build_sources(S['Sources'])
    build_needs(S['Judgment_calls_and_paywalled'])
    build_readme(S['README'], research, raws)

    for n in raws:
        S[n].sheet_properties.tabColor = '808080'
    os.makedirs(os.path.dirname(XLSX), exist_ok=True)
    wb.save(XLSX)
    with open(os.path.join(SUB, 'code', 'build_expected_values.json'), 'w') as f:
        json.dump({f'{k[0]}!{k[1]}': v for k, v in EXPECT.items()}, f, indent=0)
    print(f'wrote {REL(XLSX)}; {len(EXPECT)} formula cells with expected values')
    semantic_check()
    if verify:
        run_verify()


def semantic_check():
    """Hardcoded (non-formula) R6 summary cells must equal the intended C_breadth.csv rows (R1-F01)."""
    wb = load_workbook(XLSX)
    ws = wb['R6_breadth']
    n = 0
    for r in range(6, 30):
        scope, meth, hz = ws.cell(row=r, column=1).value, ws.cell(row=r, column=2).value, ws.cell(row=r, column=3).value
        if scope not in ('core', 'headline', 'supercore') or not meth:
            continue
        method = 'sub-line' if str(meth).startswith('sub-line') else 'leaf'
        hk = '3m_ann' if hz == '3m ann.' else '12m'
        for col, per in ((4, '2026-09'), (5, '2026-10')):
            v = ws.cell(row=r, column=col).value
            want = R6_EXPECTED_HARDCODED[(per, scope, hk, method)]
            got = EXPECT.get(('R6_breadth', ws.cell(row=r, column=col).coordinate), v) if isinstance(v, str) else v
            assert abs(got - want) < 5e-4, f'R6 {scope}/{method}/{hk}/{per}: workbook {got} vs C_breadth.csv {want}'
            n += 1
    print(f'semantic check: {n} R6 summary cells match C_breadth.csv primary/robustness rows')


# ----------------------------------------------------------------------------- R6
def build_r6(ws, PCV, PC_ROW, OCT_PI, OCT_CAT, OL_ROW, names, LFV, LF_ROW):
    header(ws, 'R6: How broad is core PCE inflation? Share of core spending with inflation above 3%',
           'Breadth = share of core PCE spending weight whose 3m-annualized or 12m inflation is above 3%. Sep 2026 published and Oct 2026 est.; weighted leaf (149 BEA components) CENTRAL (Eli, Nov 15), sub-line (184 pricing lines) robustness; component-sum gap split. Data only.',
           'Units: percent of core weight; start-of-window nominal weights. Vintage: BEA U20404/U20405 Oct 29, 2026 release; Oct = UMD est. Core leaf (central) and core sub-line (robustness) figures are live formulas over the calculation blocks below (raw_PCE_leaves, raw_PCE_components, raw_Oct_build); other figures from Agent C scripts (cell notes).')
    br = rd(os.path.join(OUT, 'C_breadth.csv'))
    # ---- line-level calc block (rows placed lower; summary formulas reference it)
    units = list(PC_ROW.keys())
    L0 = 90          # header row of line block (summary blocks above must end before row L0-2; asserted below)
    n = len(units)
    first, lastr = L0 + 1, L0 + n
    calc = {}
    for i, ln in enumerate(units):
        rr = first + i
        p = PCV[ln]
        pr = PC_ROW[ln]
        o_lv = p['P_2026-09'] * (1 + OCT_PI[ln] / 100)
        r12s = (p['P_2026-09'] / p['P_2025-09'] - 1) * 100
        r3s = ((p['P_2026-09'] / p['P_2026-06']) ** 4 - 1) * 100
        r12o = (o_lv / p['P_2025-10'] - 1) * 100
        r3o = ((o_lv / p['P_2026-07']) ** 4 - 1) * 100
        calc[ln] = dict(r12s=r12s, r3s=r3s, r12o=r12o, r3o=r3o, w12s=p['W_2025-09'], w3s=p['W_2026-06'], w12o=p['W_2025-10'], w3o=p['W_2026-07'])
        R = f'raw_PCE_components!'
        put(ws, rr, 1, f'={R}A{pr}', expect=ln)
        put(ws, rr, 2, names.get(ln, ''))
        c = put(ws, rr, 3, OCT_CAT[ln], fill=FILL_CF if OCT_CAT[ln] == 'assumed' else None)
        put(ws, rr, 4, f'={R}I{pr}*(1+raw_Oct_build!H{OL_ROW[ln]}/100)', FMT_LVL, expect=o_lv, fill=FILL_EST)
        put(ws, rr, 5, f'=({R}I{pr}/{R}E{pr}-1)*100', FMT_RATE, expect=r12s)
        put(ws, rr, 6, f'=IF(E{rr}>3,1,0)', '0', expect=1 if r12s > 3 else 0)
        put(ws, rr, 7, f'={R}J{pr}', '#,##0', expect=p['W_2025-09'])
        put(ws, rr, 8, f'=(({R}I{pr}/{R}G{pr})^4-1)*100', FMT_RATE, expect=r3s)
        put(ws, rr, 9, f'=IF(H{rr}>3,1,0)', '0', expect=1 if r3s > 3 else 0)
        put(ws, rr, 10, f'={R}L{pr}', '#,##0', expect=p['W_2026-06'])
        put(ws, rr, 11, f'=(D{rr}/{R}F{pr}-1)*100', FMT_RATE, expect=r12o, fill=FILL_EST)
        put(ws, rr, 12, f'=IF(K{rr}>3,1,0)', '0', expect=1 if r12o > 3 else 0, fill=FILL_EST)
        put(ws, rr, 13, f'={R}K{pr}', '#,##0', expect=p['W_2025-10'])
        put(ws, rr, 14, f'=((D{rr}/{R}H{pr})^4-1)*100', FMT_RATE, expect=r3o, fill=FILL_EST)
        put(ws, rr, 15, f'=IF(N{rr}>3,1,0)', '0', expect=1 if r3o > 3 else 0, fill=FILL_EST)
        put(ws, rr, 16, f'={R}M{pr}', '#,##0', expect=p['W_2026-07'])
    section(ws, L0 - 1, f'Line-level calculation: 184 core pricing lines (rows {first}-{lastr}); weights = start-of-window nominal $ (raw_PCE_components); Oct level = Sep level x (1 + line m/m est./100)')
    hdr_row(ws, L0, 1, ['Line', 'Name', 'Oct build tier', 'Oct 2026 level (est.)', 'Sep 12m %', 'Sep 12m >3%', 'Weight Sep 2025',
                        'Sep 3m ann. %', 'Sep 3m >3%', 'Weight Jun 2026', 'Oct 12m % (est.)', 'Oct 12m >3%', 'Weight Oct 2025',
                        'Oct 3m ann. % (est.)', 'Oct 3m >3%', 'Weight Jul 2026'])

    def bshare(rk, wk):
        num_ = sum(calc[l][wk] for l in units if calc[l][rk] > 3)
        return 100 * num_ / sum(calc[l][wk] for l in units)

    BRF = {('2026-09', '12m'): ('F', 'G', bshare('r12s', 'w12s')), ('2026-09', '3m_ann'): ('I', 'J', bshare('r3s', 'w3s')),
           ('2026-10', '12m'): ('L', 'M', bshare('r12o', 'w12o')), ('2026-10', '3m_ann'): ('O', 'P', bshare('r3o', 'w3o'))}

    # ---- leaf-level calc block (central method): 149 core leaves, all live formulas over raw_PCE_leaves
    leaves = list(LF_ROW.keys())
    LL0 = lastr + 4                  # header row of the leaf block
    lfirst, llast = LL0 + 1, LL0 + len(leaves)
    lcalc = {}
    RL = 'raw_PCE_leaves!'
    for i, lf in enumerate(leaves):
        rr = lfirst + i
        p = LFV[lf]
        pr = LF_ROW[lf]
        r12s = (p['P_2026-09'] / p['P_2025-09'] - 1) * 100
        r3s = ((p['P_2026-09'] / p['P_2026-06']) ** 4 - 1) * 100
        r12o = (p['P_2026-10'] / p['P_2025-10'] - 1) * 100
        r3o = ((p['P_2026-10'] / p['P_2026-07']) ** 4 - 1) * 100
        lcalc[lf] = dict(r12s=r12s, r3s=r3s, r12o=r12o, r3o=r3o, w12s=p['W_2025-09'], w3s=p['W_2026-06'], w12o=p['W_2025-10'], w3o=p['W_2026-07'], row=rr)
        put(ws, rr, 1, f'={RL}A{pr}', expect=lf)
        put(ws, rr, 2, p['name'])
        put(ws, rr, 3, 'hospital' if lf in (184, 185, 186) else '')
        put(ws, rr, 4, f'={RL}H{pr}', FMT_LVL, expect=p['P_2026-10'], fill=FILL_EST)
        put(ws, rr, 5, f'=({RL}G{pr}/{RL}C{pr}-1)*100', FMT_RATE, expect=r12s)
        put(ws, rr, 6, f'=IF(E{rr}>3,1,0)', '0', expect=1 if r12s > 3 else 0)
        put(ws, rr, 7, f'={RL}I{pr}', '#,##0', expect=p['W_2025-09'])
        put(ws, rr, 8, f'=(({RL}G{pr}/{RL}E{pr})^4-1)*100', FMT_RATE, expect=r3s)
        put(ws, rr, 9, f'=IF(H{rr}>3,1,0)', '0', expect=1 if r3s > 3 else 0)
        put(ws, rr, 10, f'={RL}K{pr}', '#,##0', expect=p['W_2026-06'])
        put(ws, rr, 11, f'=(D{rr}/{RL}D{pr}-1)*100', FMT_RATE, expect=r12o, fill=FILL_EST)
        put(ws, rr, 12, f'=IF(K{rr}>3,1,0)', '0', expect=1 if r12o > 3 else 0, fill=FILL_EST)
        put(ws, rr, 13, f'={RL}J{pr}', '#,##0', expect=p['W_2025-10'])
        put(ws, rr, 14, f'=((D{rr}/{RL}F{pr})^4-1)*100', FMT_RATE, expect=r3o, fill=FILL_EST)
        put(ws, rr, 15, f'=IF(N{rr}>3,1,0)', '0', expect=1 if r3o > 3 else 0, fill=FILL_EST)
        put(ws, rr, 16, f'={RL}L{pr}', '#,##0', expect=p['W_2026-07'])
    section(ws, LL0 - 1, f'Leaf-level calculation (CENTRAL): 149 core leaves (rows {lfirst}-{llast}); weights = start-of-window leaf nominal $ (raw_PCE_leaves); Oct level = UMD est. (fixed-share roll-up of the build)')
    hdr_row(ws, LL0, 1, ['Leaf', 'Name', 'Flag', 'Oct 2026 level (est.)', 'Sep 12m %', 'Sep 12m >3%', 'Weight Sep 2025',
                         'Sep 3m ann. %', 'Sep 3m >3%', 'Weight Jun 2026', 'Oct 12m % (est.)', 'Oct 12m >3%', 'Weight Oct 2025',
                         'Oct 3m ann. % (est.)', 'Oct 3m >3%', 'Weight Jul 2026'])

    def lshare(rk, wk, subset=None):
        tot = sum(lcalc[l][wk] for l in leaves)
        return 100 * sum(lcalc[l][wk] for l in (subset or leaves) if lcalc[l][rk] > 3) / tot

    BRF_LEAF = {('2026-09', '12m'): ('F', 'G', lshare('r12s', 'w12s')), ('2026-09', '3m_ann'): ('I', 'J', lshare('r3s', 'w3s')),
                ('2026-10', '12m'): ('L', 'M', lshare('r12o', 'w12o')), ('2026-10', '3m_ann'): ('O', 'P', lshare('r3o', 'w3o'))}

    # ---- summary block
    hdr_row(ws, 5, 1, ['Scope', 'Method', 'Horizon', 'Sep 2026 (published)', 'Oct 2026 (est.)', 'Change (pp)', 'Units', 'Role / note'],
            [24, 16, 10, 14, 14, 11, 9, 60])
    for c_, w in zip('IJKLMNOP', [12, 14, 12, 10, 12, 14, 10, 12]):
        ws.column_dimensions[c_].width = w
    ws.column_dimensions['B'].width = 30
    rr = 6
    # R1-F01 fix: C_breadth.csv also holds sensitivity, count-comparison and Waller rows with the same
    # period/scope/horizon/method; select only the primary (sub-line) and robustness (leaf) rows, one per key.
    bv = {}
    for x in br:
        if x['role'] not in ('primary', 'robustness'):
            continue
        k = (x['period'], x['scope'], x['horizon'], x['method'])
        assert k not in bv, f'duplicate primary/robustness row in C_breadth.csv: {k}'
        # C_breadth.csv (Agent C) labels sub-line 'primary' / leaf 'robustness' (pre-Nov 15 choice); the builder maps roles itself:
        # central = leaf (Eli, E5, Nov 15), robustness = sub-line.
        assert (x['method'] == 'sub-line') == (x['role'] == 'primary'), f'unexpected role for {k}: {x["role"]}'
        bv[k] = num(x['value_pct'])
    R6_EXPECTED_HARDCODED.update(bv)
    R6V = {}
    for scope in ('core', 'headline', 'supercore'):
        for method in ('leaf', 'sub-line'):
            for hz in ('3m_ann', '12m'):
                s_ = bv.get(('2026-09', scope, hz, method))
                o_ = bv.get(('2026-10', scope, hz, method))
                if s_ is None:
                    continue
                put(ws, rr, 1, scope, bold=scope == 'core')
                put(ws, rr, 2, method + (' (central)' if method == 'leaf' else ' (robustness)'), bold=method == 'leaf')
                put(ws, rr, 3, '3m ann.' if hz == '3m_ann' else '12m')
                if scope == 'core':
                    brf, f0, f1 = (BRF_LEAF, lfirst, llast) if method == 'leaf' else (BRF, first, lastr)
                    for col, per in ((4, '2026-09'), (5, '2026-10')):
                        fc, wc, v = brf[(per, hz)]
                        put(ws, rr, col, f'=SUMPRODUCT({fc}{f0}:{fc}{f1},{wc}{f0}:{wc}{f1})/SUM({wc}{f0}:{wc}{f1})*100',
                            FMT_BR, expect=v, fill=FILL_EST if per == '2026-10' else (FILL_KEY if method == 'leaf' else None))
                        R6V[(method, per, hz)] = v
                    put(ws, rr, 6, f'=E{rr}-D{rr}', FMT_BR, expect=R6V[(method, '2026-10', hz)] - R6V[(method, '2026-09', hz)])
                    put(ws, rr, 8, ('CENTRAL (Eli, Nov 15); live formula over the leaf block' if method == 'leaf' else 'robustness; live formula over the sub-line block')
                        + f' (rows {f0}-{f1}). Matches C_breadth.csv: {s_:.3f} / {o_:.3f}')
                else:
                    c1 = put(ws, rr, 4, s_, FMT_BR)
                    c2 = put(ws, rr, 5, o_, FMT_BR, fill=FILL_EST)
                    note(c1, 'Value from 09_slide1_research/code/C_breadth.py (outputs/C_breadth.csv).')
                    put(ws, rr, 6, f'=E{rr}-D{rr}', FMT_BR, expect=o_ - s_)
                    put(ws, rr, 8, ('central method; ' if method == 'leaf' else 'robustness; ') + 'value from C_breadth.py' + ('; Oct leaf = fixed-share roll-up of sub-line m/m (effectively exact at the 3% cutoff)' if method == 'leaf' else ''))
                put(ws, rr, 7, '% of weight')
                rr += 1
    band(ws, 6, rr - 1, 1, 8)
    # Waller comparison
    wv = rd(os.path.join(OUT, 'C_waller_variants.csv'))
    rr += 1
    section(ws, rr, 'Comparison: Waller (Nov 10) ">70 percent of the components of core PCE service prices" above 3% at 12m')
    rr += 1
    hdr_row(ws, rr, 1, ['Period', 'Method', 'Variant', 'Value %', 'Exceeds 70?'])
    for x in wv:
        if x['scope'] != 'core_services':
            continue
        rr += 1
        put(ws, rr, 1, x['period'], fill=FILL_EST if x['period'] == '2026-10' else None)
        put(ws, rr, 2, x['method'])
        put(ws, rr, 3, x['variant'])
        c = put(ws, rr, 4, num(x['value_pct']), FMT_BR)
        note(c, 'Value from C_waller_variants.py (outputs/C_waller_variants.csv).')
        put(ws, rr, 5, x['exceeds_70'])
    # sum gap
    sg = rd(os.path.join(OUT, 'C_sum_gap.csv'))
    rr += 2
    section(ws, rr, 'Component-sum gap: sum of component contributions minus published (or est.) core rate, split (pp). Exact additive: gap = (a) + (b) + (c)')
    rr += 1
    hdr_row(ws, rr, 1, ['Period', 'Horizon', 'Method', 'Sum of contributions', 'Published / est.', 'Gap', '(a) annualization convexity',
                        '(b) fixed-share vs chained Fisher', '(c) residual', 'Gap on aggregate-annualized basis (pipeline fix_3m)'])
    for x in sg:
        if x['method'] != 'sub-line' and x['role'] != 'primary':
            pass
        rr += 1
        est = x['period'] == '2026-10'
        put(ws, rr, 1, x['period'], fill=FILL_EST if est else None)
        put(ws, rr, 2, x['horizon'])
        put(ws, rr, 3, x['method'])
        vals = [num(x[k]) for k in ('sum_of_contributions_S_ann', 'published_or_est_rate', 'gap_total_G', 'a_annualization_convexity',
                                    'b_fixed_share_vs_chained_fisher', 'c_residual', 'gap_if_aggregate_annualized_pipeline_fix3m_basis')]
        for j, v in enumerate(vals):
            if j == 2:
                put(ws, rr, 4 + j, f'=D{rr}-E{rr}', FMT_RATE3, expect=vals[0] - vals[1])
            elif j == 5:
                put(ws, rr, 4 + j, f'=F{rr}-G{rr}-H{rr}', FMT_RATE3, expect=vals[0] - vals[1] - vals[3] - vals[4])
            else:
                c = put(ws, rr, 4 + j, v, FMT_RATE3)
                if j in (0, 3, 4):
                    note(c, 'Value from 09_slide1_research/code/C_sum_gap.py (formulas in notes_C.md). (c) here = gap - (a) - (b).')
    rr += 1
    put(ws, rr, 1, 'Note: the workbook\'s earlier "0.130" (Sep) gap is on the aggregate-annualized basis (last column) and the "~0.23" (Oct) on the individually annualized basis (Gap column); they are not like for like.')
    # carried-forward / hospitals
    cf = rd(os.path.join(OUT, 'C_carried_forward.csv'))
    hosp = rd(os.path.join(OUT, 'C_hospital_lines.csv'))[0]
    rr += 2
    section(ws, rr, 'What drives the Oct 12m breadth change (sub-line robustness basis, by Oct build tier; pp of core weight)')
    rr += 1
    hdr_row(ws, rr, 1, ['Tier / block', 'n lines', 'Core weight %', 'Sep contribution', 'Oct contribution', 'Change (pp)', 'Lines crossing 3%', 'Note'])
    for x in cf:
        rr += 1
        put(ws, rr, 1, x['tier'], fill=FILL_CF if x['tier'] == 'assumed' else None)
        put(ws, rr, 2, num(x['n_lines']))
        put(ws, rr, 3, num(x['core_weight_share_oct_window_pct']), FMT_BR)
        put(ws, rr, 4, num(x['breadth_sep_contribution_pp']), FMT_RATE)
        put(ws, rr, 5, num(x['breadth_oct_contribution_pp']), FMT_RATE)
        put(ws, rr, 6, num(x['change_total_pp']), FMT_RATE3)
        put(ws, rr, 7, num(x['n_lines_crossing_3pct']))
        put(ws, rr, 8, ('"assumed" = carried forward in the Oct build. ' if x['tier'] == 'assumed' else '') + x['note'])
    rr += 1
    put(ws, rr, 1, 'Hospital lines 184-186', bold=True)
    put(ws, rr, 2, 3)
    put(ws, rr, 3, num(hosp['core_weight_pct_oct_12m_window']), FMT_BR)
    put(ws, rr, 8, f"12m {hosp['sep_12m_rate_pct']}% -> {hosp['oct_12m_rate_est_pct']}% (est.); Oct m/m used {hosp['oct_mm_used_pct']}%, needed {hosp['oct_mm_needed_to_stay_above_3pct_12m']}% to stay >3% (36m SD {hosp['mm_sd_36m']}); "
        f"Oct 12m breadth {hosp['oct_12m_breadth_base']} vs {hosp['oct_12m_breadth_if_hospitals_just_above_3pct']} if they stayed above 3%. {hosp['tier']}")
    # leaf basis (central): hospital leaves 184-186 and the Oct 2025 base effect, live formulas over the leaf block
    rr += 2
    section(ws, rr, 'Oct 12m breadth change on the CENTRAL (weighted-leaf) basis: hospital leaves vs everything else (pp of core weight)')
    rr += 1
    hdr_row(ws, rr, 1, ['Block', 'n leaves', 'Oct core weight %', 'Change in 12m breadth (pp)', 'Oct 2025 m/m %', 'Avg m/m Nov 2025-Sep 2026 %',
                        'Oct 2026 m/m % (est.)', 'Note'])
    hosp_l = [l for l in (184, 185, 186) if l in lcalc]
    tw_s = sum(lcalc[l]['w12s'] for l in leaves)
    tw_o = sum(lcalc[l]['w12o'] for l in leaves)
    def dchg(ls):
        return sum(100 * (lcalc[l]['w12o'] * (lcalc[l]['r12o'] > 3) / tw_o - lcalc[l]['w12s'] * (lcalc[l]['r12s'] > 3) / tw_s) for l in ls)
    def dform(ls):
        terms = '+'.join(f'L{lcalc[l]["row"]}*M{lcalc[l]["row"]}/SUM($M${lfirst}:$M${llast})-F{lcalc[l]["row"]}*G{lcalc[l]["row"]}/SUM($G${lfirst}:$G${llast})' for l in ls)
        return f'=({terms})*100'
    h_ch, all_ch = dchg(hosp_l), dchg(leaves)
    rr += 1
    hr = rr
    put(ws, rr, 1, 'Hospital leaves 184-186', bold=True)
    put(ws, rr, 2, len(hosp_l))
    w_h = 100 * sum(lcalc[l]['w12o'] for l in hosp_l) / tw_o
    put(ws, rr, 3, '=(' + '+'.join(f'M{lcalc[l]["row"]}' for l in hosp_l) + f')/SUM(M{lfirst}:M{llast})*100', FMT_BR, expect=w_h)
    put(ws, rr, 4, dform(hosp_l), FMT_RATE, expect=h_ch, fill=FILL_KEY)
    l0 = hosp_l[0]
    pr0 = LF_ROW[l0]
    p0 = LFV[l0]
    put(ws, rr, 5, f'=(raw_PCE_leaves!D{pr0}/raw_PCE_leaves!C{pr0}-1)*100', '0.000', expect=(p0['P_2025-10'] / p0['P_2025-09'] - 1) * 100)
    put(ws, rr, 6, f'=((raw_PCE_leaves!G{pr0}/raw_PCE_leaves!D{pr0})^(1/11)-1)*100', '0.000', expect=((p0['P_2026-09'] / p0['P_2025-10']) ** (1 / 11) - 1) * 100)
    put(ws, rr, 7, f'=(raw_PCE_leaves!H{pr0}/raw_PCE_leaves!G{pr0}-1)*100', '0.000', expect=(p0['P_2026-10'] / p0['P_2026-09'] - 1) * 100, fill=FILL_EST)
    put(ws, rr, 8, 'Base effect: the Oct 2025 hospital jump leaves the 12m window. The three leaves share one price source (PPI hospitals), so they move together; m/m shown for leaf 184 (identical for 185, 186).')
    rr += 1
    put(ws, rr, 1, 'All other core leaves')
    put(ws, rr, 2, len(leaves) - len(hosp_l))
    put(ws, rr, 4, f'=D{rr + 1}-D{hr}', FMT_RATE, expect=all_ch - h_ch)
    rr += 1
    put(ws, rr, 1, 'Total (central leaf, Sep -> Oct)', bold=True)
    put(ws, rr, 2, len(leaves))
    put(ws, rr, 4, f'=(SUMPRODUCT(L{lfirst}:L{llast},M{lfirst}:M{llast})/SUM(M{lfirst}:M{llast})-SUMPRODUCT(F{lfirst}:F{llast},G{lfirst}:G{llast})/SUM(G{lfirst}:G{llast}))*100',
        FMT_RATE, expect=all_ch)
    assert rr < L0 - 2, f'R6 summary blocks overrun the line block (row {rr} >= {L0 - 2})'
    # time series
    # R1-F02 fix: C_breadth_ts.csv appends a reference row (avg_2018_2019); keep only YYYY-MM monthly rows
    ts = [x for x in rd(os.path.join(OUT, 'C_breadth_ts.csv')) if re.fullmatch(r'\d{4}-\d{2}', x['month'])]
    assert ts[-1]['month'] == '2026-10', ts[-1]['month']
    T0 = llast + 4
    section(ws, T0 - 1, 'Breadth time series, leaf (central) and sub-line (robustness) (values from C_breadth.py; Oct 2026 = est.)')
    hdr_row(ws, T0, 1, ['Month', 'Status', 'Core 3m ann. (sub-line)', 'Core 12m (sub-line)', 'Core 3m ann. (leaf)', 'Core 12m (leaf)',
                        '2018-19 avg, 3m (leaf)', '2018-19 avg, 12m (leaf)'])
    t1 = T0 + 1
    t_last = T0 + len(ts)
    r18 = [T0 + 1 + i for i, x in enumerate(ts) if x['month'] < '2020-01']
    a3 = statistics.mean(num(x['core_breadth_3m_ann_leaf']) for x in ts if x['month'] < '2020-01')
    a12 = statistics.mean(num(x['core_breadth_12m_leaf']) for x in ts if x['month'] < '2020-01')
    for i, x in enumerate(ts):
        rr = t1 + i
        est = x['month'] == '2026-10'
        put(ws, rr, 1, x['month'] + (' est.' if est else ''), fill=FILL_EST if est else None)
        put(ws, rr, 2, x['status'], fill=FILL_EST if est else None)
        for j, k in enumerate(('core_breadth_3m_ann_subline', 'core_breadth_12m_subline', 'core_breadth_3m_ann_leaf', 'core_breadth_12m_leaf')):
            put(ws, rr, 3 + j, num(x[k]), FMT_BR, fill=FILL_EST if est else None)
        put(ws, rr, 7, f'=AVERAGE($E${min(r18)}:$E${max(r18)})', FMT_BR, expect=a3)
        put(ws, rr, 8, f'=AVERAGE($F${min(r18)}:$F${max(r18)})', FMT_BR, expect=a12)
    note(ws.cell(row=T0, column=3), 'Values from 09_slide1_research/code/C_breadth.py (outputs/C_breadth_ts.csv); start-of-window weights; current 184-line set applied to all history.')
    ch = LineChart()
    style_chart(ch, 'Core PCE breadth: share of core weight with inflation above 3% (weighted leaf, 149 components), with 2018-19 averages', 'Percent of core spending weight', 'Month',
                'Source: BEA U20404/U20405 (Oct 29, 2026 release); UMD calculations; Oct 2026 = est.', w=26, h=12, yfmt='0')
    for col, color, dash, wpt in ((5, '8EA9DB', None, 1.25), (6, 'C00000', None, 2.0), (7, '2F5597', 'dash', 1.5), (8, 'C00000', 'dash', 1.5)):
        s = Series(Reference(ws, min_col=col, min_row=t1, max_row=t_last), title=ws.cell(row=T0, column=col).value)
        line_style(s, color, dash=dash, width_pt=wpt)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=t1, max_row=t_last))
    ch.x_axis.tickLblSkip = 12
    add_chart(ws, ch, 'L5')
    # Sep vs Oct by method chart (core): data block in columns R-T, clear of every table on this tab
    cd = 5
    hdr_row(ws, cd, 26, ['Chart data: method / horizon', 'Sep 2026', 'Oct 2026 est.'], [26, 10, 12])
    k = 0
    for method in ('leaf', 'sub-line'):
        for hz in ('3m_ann', '12m'):
            k += 1
            rr = cd + k
            src = [r for r in range(6, 30) if ws.cell(row=r, column=1).value == 'core' and str(ws.cell(row=r, column=2).value).startswith(method)
                   and ws.cell(row=r, column=3).value == ('3m ann.' if hz == '3m_ann' else '12m')][0]
            put(ws, rr, 26, f'{method}{" (central)" if method == "leaf" else ""}, {"3m ann." if hz == "3m_ann" else "12m"}')
            sv = EXPECT.get(('R6_breadth', f'D{src}'), ws.cell(row=src, column=4).value)
            ov = EXPECT.get(('R6_breadth', f'E{src}'), ws.cell(row=src, column=5).value)
            put(ws, rr, 27, f'=D{src}', FMT_BR, expect=sv)
            put(ws, rr, 28, f'=E{src}', FMT_BR, expect=ov, fill=FILL_EST)
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, 'Core breadth, Sep 2026 vs Oct 2026 est., by method and horizon', 'Percent of core spending weight', 'Method, horizon',
                'Source: BEA U20404/U20405; UMD Oct build; weighted leaf = central, sub-line = robustness', w=20, h=10, yfmt='0')
    for col in (27, 28):
        bc.add_data(Reference(ws, min_col=col, min_row=cd, max_row=cd + k), titles_from_data=True)
    for s_, color in zip(bc.series, ('8EA9DB', 'C00000')):
        s_.graphicalProperties.solidFill = color
        s_.graphicalProperties.line.solidFill = color
    bc.set_categories(Reference(ws, min_col=26, min_row=cd + 1, max_row=cd + k))
    add_chart(ws, bc, 'L32')
    ws.freeze_panes = 'A4'


# ----------------------------------------------------------------------------- Sources / Needs / README
SOURCES = [
    ('Headline, TS_PCE_rates, R4', 'raw_PCE_T20804', '03_Data/pipelines/Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json', 'https://apps.bea.gov/api/data (NIPA T20804)', 'BEA Oct 29, 2026 release; saved 2026-11-10'),
    ('Headline, TS_PCE_rates, R6', 'raw_Oct_build', '02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv; D_build_2026-10_lines.csv', 'n/a (UMD build from BLS CPI/PPI Oct 2026)', 'built 2026-11-13 after PPI'),
    ('R6', 'raw_PCE_components', '03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json; ..._U20405_2026-11-10.json', 'https://apps.bea.gov/api/data (NIUnderlyingDetail U20404/U20405)', 'BEA Oct 29, 2026 release; saved 2026-11-10'),
    ('R6', 'raw_PCE_leaves', '03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json; ..._U20405_2026-11-10.json; Oct est. from 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv (fixed-share roll-up, C_common.py)', 'https://apps.bea.gov/api/data (NIUnderlyingDetail U20404/U20405)', 'BEA Oct 29, 2026 release; saved 2026-11-10; Oct = UMD est.'),
    ('R6', '(script values)', '09_slide1_research/outputs/C_breadth.csv, C_breadth_ts.csv, C_sum_gap.csv, C_carried_forward.csv, C_hospital_lines.csv, C_waller_variants.csv', 'n/a (computed by code/C_*.py)', 'run 2026-11-14'),
    ('R1_backtest', 'raw_backtest', '02_Research/Subtasks/04_oct_pce_build/outputs/D2_backtest_variant_first_release_pm.csv; backtest_results.csv (via outputs/A_backtest.csv)', 'https://alfred.stlouisfed.org (first prints); https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting', 'Dec 2025 - Sep 2026'),
    ('R2_outside_estimates', 'raw_outside_estimates', 'outputs/A_outside_existing.csv; outputs/D_outside_new.csv; 03_Data/Raw/outside_oct_pce_estimates_2026-11-14/', 'per row', 'collected 2026-11-14'),
    ('R4_sep_pce_check', 'raw_BEA_release_text', '03_Data/Raw/BEA_PIO_release_Sep2026_2026-11-14/personal-income-and-outlays-september-2026.html; 02_Research/External_views/Fed_officials_2026-11/speeches/', 'https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026', 'release Oct 29, 2026; speeches Nov 10-13'),
    ('R5_cleveland', 'raw_Cleveland', '03_Data/Raw/ClevelandFed_nowcast_month_2026-11-14.json; ClevelandFed_nowcast_year_2026-11-14.json', 'https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting', 'pulled 2026-11-14 (carried forward)'),
]


def build_sources(ws):
    header(ws, 'Sources: every raw file and URL behind each tab', 'One row per raw input. Paths are relative to the project root.', 'All files are saved locally; nothing in this workbook depends on a live link.')
    hdr_row(ws, 5, 1, ['Research tab(s)', 'Raw tab', 'File(s)', 'URL', 'Vintage'], [26, 22, 80, 60, 30])
    extra = []
    p = os.path.join(OUT, 'B_sources_for_workbook.csv')
    if os.path.exists(p):
        extra = [(x['tabs'], x['raw_tab'], x['files'], x['url'], x['vintage']) for x in rd(p)]
    for i, row in enumerate(SOURCES + extra):
        for j, v in enumerate(row):
            c = put(ws, 6 + i, 1 + j, v)
            c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A6'


def build_needs(ws):
    header(ws, 'Judgment calls for Eli, and paywalled links', 'Items for Eli to decide or fetch. Both positions are given where Codex and Claude differ.', 'Source: 06_Audits/slide1_research/STATUS.md (Judgment calls for Eli) and outputs/D_paywalled.csv (+ other agents\' paywalled lists).')
    hdr_row(ws, 5, 1, ['#', 'Item', 'Position A', 'Position B', 'Affects tab', 'Status / decision (Eli, Nov 15)'], [5, 50, 50, 50, 22, 60])
    rr = 6
    p = os.path.join(OUT, 'Z_judgment_calls.csv')
    if os.path.exists(p):
        for x in rd(p):
            for j, k in enumerate(['id', 'item', 'position_a', 'position_b', 'tab', 'status']):
                c = put(ws, rr, 1 + j, x[k])
                c.alignment = Alignment(wrap_text=True, vertical='top')
            rr += 1
    rr += 1
    section(ws, rr, 'Paywalled or blocked links (not accessed; Eli to fetch)')
    rr += 1
    hdr_row(ws, rr, 1, ['#', 'URL', 'Publisher', 'What it would add', 'Affects tab', 'Why it matters'])
    k = 0
    for fname, tab in (('D_paywalled.csv', 'R2_outside_estimates'), ('B_paywalled.csv', 'R3_core_gap')):
        p = os.path.join(OUT, fname)
        if not os.path.exists(p):
            continue
        for x in rd(p):
            k += 1
            rr += 1
            vals = [k, x.get('URL', x.get('url', '')), x.get('publisher', ''), x.get('what it likely contains', x.get('what', '')), tab, x.get('why it matters', x.get('why', ''))]
            for j, v in enumerate(vals):
                c = put(ws, rr, 1 + j, v)
                c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A6'


DESCR = {
    'Headline': 'Oct 2026 core and headline PCE (est.): 1m, 1m ann., 3m, 6m, 12m with backtest bands; Sep published; Sep->Oct m/m.',
    'TS_PCE_rates': 'Monthly core and headline PCE rates, Jan 2018 - Oct 2026 (Oct est.), wide and long layouts; 12m and momentum charts.',
    'R1_backtest': 'Backtest of the Oct method vs BEA first print, ours vs Cleveland vs core-CPI benchmark; MAE, RMSE, bias.',
    'R2_outside_estimates': 'Outside Oct estimates with tier and timing; median, range, UMD distance in bp.',
    'R3_core_gap': 'Core PCE minus core CPI gap decomposition, Sep (published) and Oct (est.); headline check vs BEA Table 9.1U.',
    'R4_sep_pce_check': 'Sep 2026 PCE y/y: index levels vs BEA text vs Fed officials (Waller 3.7 vs 3.6).',
    'R5_cleveland': 'Cleveland Fed Oct nowcast (carried forward: Nov 14 pull; re-pull Nov 18) and its path.',
    'R6_breadth': 'Breadth above 3%, Sep and Oct: weighted leaf (149 components) central, sub-line robustness; time series; hospital base effect; sum-gap split.',
    'Sources': 'Every raw file and URL behind each tab.',
    'Judgment_calls_and_paywalled': 'Judgment calls for Eli (both positions) and paywalled links to fetch.',
}


def build_readme(ws, research, raws):
    header(ws, 'Slide 1 data workbook: "Where is inflation, and is it accelerating?"',
           'Chart-ready data for Slide 1 of the UMD finals inflation section. One tab per research item; raw tabs (grey) at the end hold every series behind each number.',
           f'Built {BUILD_DATE} by {SCRIPT}. Vintages: BEA PCE Oct 29, 2026 release (through Sep 2026); Oct 2026 = UMD estimate (Nov 13, after PPI). Data cutoff for finals: Nov 18, 2026.')
    rr = 5
    section(ws, rr, 'How to rebuild')
    rr += 1
    ws.cell(row=rr, column=1, value=f'From the project root:  python3 -I "02_Research/Subtasks/{SCRIPT}" --verify   (fix inputs in 09_slide1_research/outputs/ or raw files, never this xlsx, until Eli hand-edits it)')
    rr += 2
    section(ws, rr, 'Label key')
    for lbl, fill, txt in (('est.', FILL_EST, 'our estimate (UMD bottom-up October build); BEA publishes October PCE on Nov 25'),
                           ('carried forward', FILL_CF, 'value pulled earlier and not yet refreshed (Cleveland: Nov 14 pull, re-pull Nov 18); also the Oct build\'s "assumed" tier'),
                           ('press-reported', FILL_PRESS, 'number taken from a press report of a bank note, not the original note [2]'),
                           ('key figure', FILL_KEY, 'figure used on the slide or in the corroboration line')):
        rr += 1
        c = ws.cell(row=rr, column=1, value=lbl)
        c.fill = fill
        c.font = F_BOLD
        c.border = BOX
        ws.cell(row=rr, column=2, value=txt)
    rr += 2
    section(ws, rr, 'Contents (click to jump)')
    rr += 1
    hdr_row(ws, rr, 1, ['Tab', 'What it shows'], [28, 120])
    for n in research[1:]:
        rr += 1
        c = ws.cell(row=rr, column=1, value=n)
        c.hyperlink = f"#'{n}'!A1"
        c.font = Font(color='0563C1', underline='single')
        ws.cell(row=rr, column=2, value=DESCR.get(n, ''))
    rr += 1
    for n in raws:
        rr += 1
        c = ws.cell(row=rr, column=1, value=n)
        c.hyperlink = f"#'{n}'!A1"
        c.font = Font(color='0563C1', underline='single')
        ws.cell(row=rr, column=2, value='raw data (grey tab): source file path, URL, vintage and retrieval date in rows 2-5')
    rr += 2
    section(ws, rr, 'Conventions')
    for t in ('Rates in percent, 2 decimals; breadth in percent of core weight, 1 decimal. 3m and 6m rates are annualized; 1m is m/m unless labelled annualized.',
              'Black numbers in research tabs are live formulas wherever practical: click a cell to trace it to a raw tab. Script-computed values carry a cell note naming the script.',
              'Status lines and audit trail: 02_Research/Subtasks/09_slide1_research/FINAL.md and 06_Audits/slide1_research/.'):
        rr += 1
        ws.cell(row=rr, column=1, value=t)


# ----------------------------------------------------------------------------- verify
def run_verify():
    scratch = os.environ.get('SLIDE1_SCRATCH', '/tmp')
    os.makedirs(scratch, exist_ok=True)
    cmd = ['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', scratch, XLSX]
    subprocess.run(cmd, check=True, capture_output=True, timeout=300)
    rec = os.path.join(scratch, os.path.basename(XLSX))
    wb = load_workbook(rec, data_only=True)
    bad, errs, n = [], [], 0
    for (sh, coord), exp in EXPECT.items():
        v = wb[sh][coord].value
        n += 1
        if isinstance(v, str) and v.startswith('#'):
            errs.append((sh, coord, v))
            continue
        if exp == '' or exp is None:
            if v not in (None, ''):
                bad.append((sh, coord, exp, v))
            continue
        if not isinstance(v, (int, float)) or abs(v - exp) > 1e-6:
            bad.append((sh, coord, exp, v))
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('#') and c.value[1:4] in ('REF', 'DIV', 'VAL', 'N/A', 'NAM', 'NUM', 'NUL'):
                    errs.append((ws.title, c.coordinate, c.value))
    rep = os.path.join(SUB, 'code', 'build_verify_report.txt')
    with open(rep, 'w') as f:
        f.write(f'LibreOffice recalculation check, {dt.datetime.now().isoformat(timespec="seconds")}\n')
        f.write(f'formula cells checked: {n}; mismatches > 1e-6: {len(bad)}; error values: {len(errs)}\n')
        for b in bad[:200]:
            f.write(f'MISMATCH {b}\n')
        for e in errs[:200]:
            f.write(f'ERROR {e}\n')
    print(open(rep).read()[:3000])
    if bad or errs:
        sys.exit(1)


if __name__ == '__main__':
    main(verify='--verify' in sys.argv)
