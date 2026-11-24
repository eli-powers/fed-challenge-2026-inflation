"""Build the Inflation Slide 1 data workbook and slide 1 in our working deck, from one set of computed values.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide1_build/code/build_inflation_slide1.py"            # build
    python3 -I "02_Research/Subtasks/10_slide1_build/code/build_inflation_slide1.py" --verify   # build + checks

Outputs
  01_Finals/Slide data/Inflation Slide 1.xlsx       every number on the slide, with source (chart tabs in the style-guide format)
  01_Finals/slides/Inflation Slides (working).pptx  team deck copy: Inflation section slide + slide 1 (two-chart)

Inputs (all saved locally)
  BEA NIPA T20804 (Oct 29, 2026 release, saved Nov 10): 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json
  UMD October estimate (m/m):                         02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv
  Team deck (template):                               01_Finals/slides/Finals/Slides.pptx
  Style guide:                                        01_Finals/Slide instructions/Fed_Challlenge_Style_Guide.md
Cross-check: 02_Research/Subtasks/09_slide1_research/outputs/A_ts_pce_rates.csv (the Slide1_Inflation_Data.xlsx series).

Decisions (Eli, Nov 15): two-chart slide; left = core and headline PCE 12m; right = core 3m and 6m annualized;
both panels Oct 2023 - Oct 2026; Oct 2026 = UMD estimate, marked by a small "est." in the end labels (said verbally);
title "Inflation: Firming Again After a Summer Lull"; takeaway = placeholder; source line "through Oct 2026 (Oct = UMD
estimate built from BLS CPI/PPI)"; style-guide defaults otherwise (y from 0, 0.00 format).
"""
import copy
import csv
import datetime as dt
import json
import math
import os
import subprocess
import sys

from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
T20804 = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw', 'BEA_NIPA_T20804_2026-11-10.json')
OCT_SUM = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'D_build_2026-10_summary.csv')
XCHECK = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'outputs', 'A_ts_pce_rates.csv')
TEAM_DECK = os.path.join(ROOT, '01_Finals', 'slides', 'Finals', 'Slides.pptx')
OUT_XLSX = os.environ.get('SLIDE1B_XLSX') or os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 1.xlsx')
OUT_PPTX = os.environ.get('SLIDE1B_PPTX') or os.path.join(ROOT, '01_Finals', 'slides', 'Inflation Slides (working).pptx')
SCRATCH = os.environ.get('SLIDE1B_SCRATCH', '/tmp')
REPORT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide1_build', 'code', 'verify_report.txt')
REL = lambda p: os.path.relpath(p, ROOT)

WIN0, WIN1 = (2023, 10), (2026, 10)     # plotted window, both panels
EST_MONTH = '2026-10'

# ---------------------------------------------------------------- style guide constants
NAVY, WHITE, GOLD, LIGHT = '1B2A4A', 'FFFFFF', 'F2CC6B', 'F2F2F2'
RED, DNAVY, BLACK = 'C0282D', '1B2A61', '000000'
AXIS_GRAY, LABEL_GRAY, SOURCE_GRAY = '7F7F7F', '595959', '6B6B6B'
TITLE = ('Inflation', 'Firming Again After a Summer Lull')
HEADING = 'PCE Inflation: 12-Month Rates and Recent Core Momentum'          # drafted by Claude; Eli to confirm
PANEL_L, PANEL_R = 'PCE, 12-Month % Change', 'Core PCE, Annualized % Change'
SOURCE = ('Source: BEA (PCE and core PCE price indexes, NIPA Table 2.8.4). Percent change: 12-month (left), '
          '3- and 6-month annualized (right); monthly, through Oct 2026*. Dashed line: 2% target. '
          '*Oct 2026 = UMD estimate built from BLS CPI/PPI.')
EST_MARK = '*'          # Eli, Nov 15: asterisk on the Oct values instead of "est."; footnoted in the source line
TAKEAWAY = '[Takeaway: one sentence the team writes]'
# Two versions of slide 1 (Eli, Nov 15): the style guide's s.5 layout, then a wider version right after it.
LAYOUTS = [
    # name,   left plot x,   right plot x,   left-label limit, right-label limit
    ('guide', (1.27, 5.13), (7.40, 11.27), 6.50, 12.70),          # s.5: left-chart labels end before x 6.53
    ('wide',  (0.95, 5.40), (7.26, 11.71), 7.26 - 0.65, 11.71 + 1.40),   # +15% plot width (deviation from s.5)
]
PLOT_Y = (2.16, 5.60)                    # no note line
YMIN, YMAX, YSTEP = 0, None, 1           # YMAX from data (next whole number >= max incl. reference)
REFERENCE = 2.0


def months(a, b):
    y, m = a
    while (y, m) <= b:
        yield f'{y}-{m:02d}'
        m += 1
        if m == 13:
            y, m = y + 1, 1


def mdate(m):
    return dt.datetime(int(m[:4]), int(m[5:7]), 1)


def rgb(h):
    return RGBColor.from_string(h)


# ---------------------------------------------------------------- data
def load_data():
    d = json.load(open(T20804))['BEAAPI']['Results']['Data']
    lv = {}
    for r in d:
        if r['LineNumber'] in ('1', '25'):
            lv[(r['LineNumber'], r['TimePeriod'])] = float(r['DataValue'].replace(',', ''))
    summ = {r['measure']: r for r in csv.DictReader(open(OCT_SUM))}
    est = {'core': float(summ['core']['estimate_mm']), 'headline': float(summ['headline']['estimate_mm'])}
    band = {'core': float(summ['core']['band_reported']), 'headline': float(summ['headline']['band_reported'])}
    allm = list(months((2022, 10), WIN1))
    L = {}
    for m in allm:
        if m == EST_MONTH:
            L[m] = {k: L['2026-09'][k] * (1 + est[k] / 100) for k in ('core', 'headline')}
        else:
            L[m] = {'core': lv[('25', m.replace('-', 'M'))], 'headline': lv[('1', m.replace('-', 'M'))]}
    win = list(months(WIN0, WIN1))
    i = {m: allm.index(m) for m in allm}
    rates = {}
    for m in win:
        k = i[m]
        rates[m] = {
            'core12': (L[m]['core'] / L[allm[k - 12]]['core'] - 1) * 100,
            'head12': (L[m]['headline'] / L[allm[k - 12]]['headline'] - 1) * 100,
            'core3': ((L[m]['core'] / L[allm[k - 3]]['core']) ** 4 - 1) * 100,
            'core6': ((L[m]['core'] / L[allm[k - 6]]['core']) ** 2 - 1) * 100,
        }
    return allm, win, L, rates, est, band


# ---------------------------------------------------------------- workbook
EXPECT = {}


def build_workbook(allm, win, L, rates, est, band, ymax):
    wb = Workbook()
    hdr_font = Font(bold=True)
    note_fill = PatternFill('solid', fgColor='FFF2CC')

    # Raw_PCE: BEA levels + Oct estimate level (formula)
    raw = wb.active
    raw.title = 'Raw_PCE'
    raw.append(['Date', 'Core PCE index (T20804 line 25, DPCCRG)', 'Headline PCE index (T20804 line 1, DPCERG)', 'Status'])
    RR = {}
    for j, m in enumerate(allm):
        r = j + 2
        RR[m] = r
        raw.cell(r, 1, mdate(m)).number_format = 'yyyy-mm'
        if m == EST_MONTH:
            raw.cell(r, 2, f"=B{RR['2026-09']}*(1+Oct_est!B2/100)")
            raw.cell(r, 3, f"=C{RR['2026-09']}*(1+Oct_est!B3/100)")
            raw.cell(r, 4, 'UMD estimate (Oct 2026)')
            EXPECT[('Raw_PCE', f'B{r}')] = L[m]['core']
            EXPECT[('Raw_PCE', f'C{r}')] = L[m]['headline']
            for c in (1, 2, 3, 4):
                raw.cell(r, c).fill = note_fill
        else:
            raw.cell(r, 2, L[m]['core'])
            raw.cell(r, 3, L[m]['headline'])
            raw.cell(r, 4, 'BEA published')
        raw.cell(r, 2).number_format = raw.cell(r, 3).number_format = '0.000'

    # Oct_est
    oe = wb.create_sheet('Oct_est')
    oe.append(['Measure', 'Oct 2026 m/m % (UMD estimate)', 'Backtest band +/- (pp m/m)', 'Source'])
    for k in ('core', 'headline'):
        oe.append([k, est[k], band[k], f'{REL(OCT_SUM)} (estimate_mm, band_reported); built 2026-11-13 after the Oct PPI'])

    # chart tabs (style guide section 6): A = real dates, one column per line, header = line name, Reference column
    def chart_tab(name, cols):
        ws = wb.create_sheet(name)
        ws.append(['Date'] + [c[0] for c in cols] + ['Reference'])
        for j, m in enumerate(win):
            r = j + 2
            ws.cell(r, 1, mdate(m)).number_format = 'yyyy-mm'
            for k, (_, key, ftmpl) in enumerate(cols):
                rr, back = RR[m], None
                f = ftmpl(rr)
                ws.cell(r, 2 + k, f).number_format = '0.00'
                EXPECT[(name, ws.cell(r, 2 + k).coordinate)] = rates[m][key]
            ws.cell(r, 2 + len(cols), REFERENCE).number_format = '0.00'
        return ws

    t12 = chart_tab('12m', [
        ('Core', 'core12', lambda r: f'=(Raw_PCE!B{r}/Raw_PCE!B{r - 12}-1)*100'),
        ('Headline', 'head12', lambda r: f'=(Raw_PCE!C{r}/Raw_PCE!C{r - 12}-1)*100')])
    tm = chart_tab('Momentum', [
        ('3-month', 'core3', lambda r: f'=((Raw_PCE!B{r}/Raw_PCE!B{r - 3})^4-1)*100'),
        ('6-month', 'core6', lambda r: f'=((Raw_PCE!B{r}/Raw_PCE!B{r - 6})^2-1)*100')])

    # Notes: every number and text on the slide, with its source
    nt = wb.create_sheet('Notes')
    last = len(win) + 1
    nt.append(['Slide element', 'Value', 'Where it comes from'])
    rows = [
        ('Title', f'{TITLE[0]}: {TITLE[1]}', 'Eli, Nov 15'),
        ('Chart heading', HEADING, 'drafted by Claude; Eli to confirm'),
        ('Left panel title', PANEL_L, ''),
        ('Right panel title', PANEL_R, ''),
        ('End label: Core (left, red), last value %', f"='12m'!B{last}", "12m tab, last row (Oct 2026 = UMD estimate)", rates[win[-1]]['core12']),
        ('End label: Headline (left, dark navy), last value %', f"='12m'!C{last}", "12m tab, last row (Oct 2026 = UMD estimate)", rates[win[-1]]['head12']),
        ('End label: 3-month (right, red), last value %', f'=Momentum!B{last}', 'Momentum tab, last row (Oct 2026 = UMD estimate)', rates[win[-1]]['core3']),
        ('End label: 6-month (right, dark navy), last value %', f'=Momentum!C{last}', 'Momentum tab, last row (Oct 2026 = UMD estimate)', rates[win[-1]]['core6']),
        ('Estimate marker', 'asterisk after each end-label value (e.g. 3.24%*), footnoted in the source line', 'Oct 2026 is the UMD bottom-up estimate; BEA publishes Oct PCE on Nov 25 (Eli, Nov 15: asterisk instead of "est."; said verbally)'),
        ('Reference line (dashed)', REFERENCE, "Reference column of 12m and Momentum tabs: FOMC 2% target"),
        ('Y-axis range (both panels)', f'{YMIN} to {ymax}, steps of {YSTEP}, format 0.00', 'Style guide s.3: from 0 to next whole number >= max (incl. reference); same range for both panels (same units)'),
        ('Plotted window (both panels)', f'{win[0]} to {win[-1]} ({len(win)} months)', 'Eli, Nov 15: start Oct 2023 (verbal cue: highest since Nov 2023); same window both panels'),
        ('X-axis labels', 'YYYY-MM every January and July', 'Style guide s.3. Embedded chart data uses a text label column (blank except Jan/Jul) so labels land on Jan/Jul with a window starting in October; the date order is identical to column A of the chart tabs'),
        ('Source line', SOURCE, 'Style guide s.2 format; Eli approved the "(Oct = UMD estimate ...)" wording Nov 15'),
        ('Takeaway', TAKEAWAY, 'Style guide: placeholder unless Eli gives the sentence'),
        ('Data vintage', 'BEA NIPA T20804, Oct 29, 2026 release (data through Sep 2026), saved Nov 10', REL(T20804)),
        ('Build', 'python3 -I "02_Research/Subtasks/10_slide1_build/code/build_inflation_slide1.py" --verify', 'Rebuilds this workbook and the slide; checks every chart point against this workbook'),
    ]
    for row in rows:
        nt.append(list(row[:3]))
        if len(row) == 4:
            r = nt.max_row
            nt.cell(r, 2).number_format = '0.00'
            EXPECT[('Notes', f'B{r}')] = row[3]
    nt.cell(nt.max_row + 2, 1, 'Cross-check vs Slide1_Inflation_Data.xlsx (A_ts_pce_rates.csv), max abs difference (pp):').font = hdr_font
    for ws in (raw, oe, t12, tm, nt):
        for c in ws[1]:
            c.font = hdr_font
        ws.freeze_panes = 'A2'
    for ws, widths in ((raw, [11, 18, 18, 22]), (oe, [11, 16, 16, 90]), (t12, [11, 10, 10, 10]), (tm, [11, 10, 10, 10]), (nt, [44, 60, 90])):
        for k, w in enumerate(widths):
            ws.column_dimensions[chr(65 + k)].width = w
    for r in nt.iter_rows(min_row=2):
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    # tab order: chart tabs first
    wb._sheets = [t12, tm, raw, oe, nt]
    return wb, nt


# ---------------------------------------------------------------- pptx helpers
def text_box(slide, x, y, w, h, runs, size, font, align=PP_ALIGN.CENTER, bold=False, italic=False, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = runs if isinstance(runs[0], list) else [runs]
    for li, line in enumerate(lines):
        p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
        p.alignment = align
        for text, color in line:
            r = p.add_run()
            r.text = text
            r.font.name, r.font.size, r.font.bold, r.font.italic = font, Pt(size), bold, italic
            r.font.color.rgb = rgb(color)
    return tb


def axis_labels(win):
    return [m if m[5:] in ('01', '07') else ' ' for m in win]     # ' ' not '': python-pptx writes '' as the text "None"


def build_chart(slide, win, series, plot_x, ymax):
    """series: [(name, values, color)] + reference. Plot area placed exactly at plot_x x PLOT_Y via manual layout."""
    fx0, fx1 = plot_x[0] - 0.70, plot_x[1] + 0.08
    fy0, fy1 = PLOT_Y[0] - 0.08, PLOT_Y[1] + 0.36   # room below the plot for one line of date labels; frame ends 5.96 < source line 6.00
    cd = CategoryChartData()
    cd.categories = axis_labels(win)
    for name, vals, _ in series:
        cd.add_series(name, vals)
    cd.add_series('Reference', [REFERENCE] * len(win))
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(fx0), Inches(fy0), Inches(fx1 - fx0), Inches(fy1 - fy0), cd)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = False
    for s, (_, _, color) in zip(ch.plots[0].series, series):
        s.format.line.color.rgb = rgb(color)
        s.format.line.width = Pt(3)
        s.marker.style = XL_MARKER_STYLE.NONE
        s.smooth = False
    ref = ch.plots[0].series[len(series)]
    ref.format.line.color.rgb = rgb(BLACK)
    ref.format.line.width = Pt(2.25)
    ref.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ref.marker.style = XL_MARKER_STYLE.NONE
    ref.smooth = False
    va = ch.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = YMIN, ymax, YSTEP
    va.has_major_gridlines = False
    va.has_minor_gridlines = False
    va.tick_labels.number_format = '0.00'
    va.tick_labels.number_format_is_linked = False
    va.tick_labels.font.name, va.tick_labels.font.size = 'Arial', Pt(12)
    va.tick_labels.font.color.rgb = rgb(LABEL_GRAY)
    va.format.line.fill.background()
    va.major_tick_mark = XL_TICK_MARK.NONE
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.tick_labels.font.name, ca.tick_labels.font.size = 'Arial', Pt(11)
    ca.tick_labels.font.color.rgb = rgb(LABEL_GRAY)
    ca.format.line.color.rgb = rgb(AXIS_GRAY)
    ca.format.line.width = Pt(1)
    ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    cs = ch._chartSpace
    C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
    # first and last points on the plot edges
    for vax in cs.iter(qn('c:valAx')):
        cb = vax.find(qn('c:crossBetween'))
        if cb is None:
            cb = etree.SubElement(vax, qn('c:crossBetween'))
        cb.set('val', 'midCat')
    # every category label shown (blank strings except Jan/Jul), unrotated
    cax = next(cs.iter(qn('c:catAx')))
    for tag in ('c:tickLblSkip', 'c:tickMarkSkip', 'c:noMultiLvlLbl'):     # re-add in schema order (before any extLst)
        el = cax.find(qn(tag))
        if el is not None:
            cax.remove(el)
    ext = cax.find(qn('c:extLst'))
    for tag in ('c:tickLblSkip', 'c:tickMarkSkip', 'c:noMultiLvlLbl'):
        el = etree.Element(qn(tag))
        el.set('val', '1')
        if ext is not None:
            ext.addprevious(el)
        else:
            cax.append(el)
    txpr = cax.find(qn('c:txPr'))
    if txpr is not None:
        bp = txpr.find(qn('a:bodyPr'))
        bp.set('rot', '0')
        bp.set('vert', 'horz')
        bp.set('wrap', 'none')          # keep "2024-01" on one line (PowerPoint otherwise breaks at the hyphen)
    # no chart fill / border, no plot fill
    chart_el = cs.find(qn('c:chart'))
    for parent in (cs, chart_el.find(qn('c:plotArea'))):
        sp = parent.find(qn('c:spPr'))
        if sp is None:
            sp = etree.SubElement(parent, qn('c:spPr'))
            if parent is cs:
                # spPr must precede txPr/externalData in chartSpace
                cs.remove(sp)
                chart_el.addnext(sp)
        for child in list(sp):
            sp.remove(child)
        etree.SubElement(sp, qn('a:noFill'))
        ln = etree.SubElement(sp, qn('a:ln'))
        etree.SubElement(ln, qn('a:noFill'))
    # exact plot area (inner) in slide inches
    pa = chart_el.find(qn('c:plotArea'))
    lay = pa.find(qn('c:layout'))
    if lay is None:
        lay = etree.Element(qn('c:layout'))
        pa.insert(0, lay)
    for child in list(lay):
        lay.remove(child)
    ml = etree.SubElement(lay, qn('c:manualLayout'))
    W, H = fx1 - fx0, fy1 - fy0
    for tag, val in (('c:layoutTarget', 'inner'), ('c:xMode', 'edge'), ('c:yMode', 'edge'),
                     ('c:x', (plot_x[0] - fx0) / W), ('c:y', (PLOT_Y[0] - fy0) / H),
                     ('c:w', (plot_x[1] - plot_x[0]) / W), ('c:h', (PLOT_Y[1] - PLOT_Y[0]) / H)):
        etree.SubElement(ml, qn(tag)).set('val', str(val))
    atd = chart_el.find(qn('c:autoTitleDeleted'))
    if atd is None:
        atd = etree.Element(qn('c:autoTitleDeleted'))
        chart_el.insert(0, atd)
    atd.set('val', '1')
    return gf


def end_labels(slide, plot_x, labels, ymax, right_limit):
    """labels: [(name, value, color)]; two lines: name / 'x.xx%*' (asterisk = Oct estimate); nudged apart if they would touch."""
    h, gap = 0.44, 0.02
    ys = [PLOT_Y[1] - (v - YMIN) / (ymax - YMIN) * (PLOT_Y[1] - PLOT_Y[0]) for _, v, _ in labels]
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    cy = list(ys)
    for a, b in zip(order, order[1:]):
        need = h + gap - (cy[b] - cy[a])
        if need > 0:
            cy[a] -= need / 2
            cy[b] += need / 2
    x = plot_x[1] + 0.16
    w = right_limit - x
    out = []
    for (name, v, color), y in zip(labels, cy):
        text_box(slide, x, y - h / 2, w, h, [[(name, color)], [(f'{v:.2f}%{EST_MARK}', color)]], 13, 'Arial',
                 align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        out.append((name, round(v, 2), round(y, 3), round(y - h / 2, 3)))
    return out


def build_pptx(win, rates, ymax):
    prs = Presentation(TEAM_DECK)
    assert (round(prs.slide_width / 914400, 2), round(prs.slide_height / 914400, 2)) == (13.33, 7.5), 'deck is not 13.33 x 7.5'
    # keep only the Inflation section slide (unchanged), drop the rest
    sldIdLst = prs.slides._sldIdLst
    keep = None
    for sid, slide in zip(list(sldIdLst), list(prs.slides)):
        texts = [sh.text_frame.text for sh in slide.shapes if sh.has_text_frame]
        if 'Inflation' in texts and 'SECTION 1' in texts:
            keep = sid
    assert keep is not None, 'Inflation section slide not found'
    for sid in list(sldIdLst):
        if sid is not keep:
            prs.part.drop_rel(sid.get(qn('r:id')))
            sldIdLst.remove(sid)
    # python-pptx names a new slide slide<N+1>.xml; renumber the kept slide first or the two collide in the zip
    from pptx.opc.packuri import PackURI
    prs.slides[0].part.partname = PackURI('/ppt/slides/slide1.xml')
    blank = [l for l in prs.slide_layouts if l.name == 'Blank'][0]
    labels = {}
    for name, plot_l, plot_r, lim_l, lim_r in LAYOUTS:
        s = prs.slides.add_slide(blank)
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = rgb(LIGHT)
        # title band + title (white label, white colon, gold story)
        band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.01))
        band.fill.solid()
        band.fill.fore_color.rgb = rgb(NAVY)
        band.line.fill.background()
        band.shadow.inherit = False
        tf = band.text_frame
        tf.margin_left = tf.margin_right = Inches(0.2)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        for text, color in ((TITLE[0], WHITE), (':', WHITE), (' ' + TITLE[1], GOLD)):
            r = p.add_run()
            r.text = text
            r.font.name, r.font.size, r.font.bold = 'Georgia', Pt(32), False
            r.font.color.rgb = rgb(color)
        text_box(s, 0.67, 1.09, 12.00, 0.61, [(HEADING, NAVY)], 21, 'Georgia', bold=True, anchor=MSO_ANCHOR.MIDDLE)
        for (x0, x1), t in ((plot_l, PANEL_L), (plot_r, PANEL_R)):
            text_box(s, x0, 1.80, x1 - x0, 0.30, [(t, NAVY)], 13, 'Arial', bold=True)
        last = win[-1]
        L = [('Core', [rates[m]['core12'] for m in win], RED), ('Headline', [rates[m]['head12'] for m in win], DNAVY)]
        R = [('3-month', [rates[m]['core3'] for m in win], RED), ('6-month', [rates[m]['core6'] for m in win], DNAVY)]
        build_chart(s, win, L, plot_l, ymax)
        build_chart(s, win, R, plot_r, ymax)
        lab_l = end_labels(s, plot_l, [(n, v[-1], c) for n, v, c in L], ymax, right_limit=lim_l)
        lab_r = end_labels(s, plot_r, [(n, v[-1], c) for n, v, c in R], ymax, right_limit=lim_r)
        text_box(s, 0.73, 6.00, 12.00, 0.47, [(SOURCE, SOURCE_GRAY)], 13, 'Arial', align=PP_ALIGN.LEFT)
        text_box(s, 0.67, 6.53, 12.00, 0.73, [(TAKEAWAY, NAVY)], 24, 'Georgia', bold=True, italic=True, anchor=MSO_ANCHOR.MIDDLE)
        labels[name] = lab_l + lab_r
    os.makedirs(os.path.dirname(OUT_PPTX), exist_ok=True)
    prs.save(OUT_PPTX)
    return labels


# ---------------------------------------------------------------- verification
def verify(win, rates, ymax, labels):
    lines = [f'Inflation Slide 1 build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    # 1. workbook formulas recalculated by LibreOffice == script values
    os.makedirs(SCRATCH, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', SCRATCH, OUT_XLSX], check=True, capture_output=True, timeout=300)
    rec = load_workbook(os.path.join(SCRATCH, os.path.basename(OUT_XLSX)), data_only=True)
    bad = [(k, v, rec[k[0]][k[1]].value) for k, v in EXPECT.items()
           if not isinstance(rec[k[0]][k[1]].value, (int, float)) or abs(rec[k[0]][k[1]].value - v) > 1e-9]
    lines.append(f'1. workbook formula cells: {len(EXPECT)} checked after LibreOffice recalc; mismatches > 1e-9: {len(bad)}')
    ok &= not bad
    # 2. every chart point in the pptx == the workbook chart tab (same row order)
    prs = Presentation(OUT_PPTX)
    tabs = [('12m', ['Core', 'Headline']), ('Momentum', ['3-month', '6-month'])]
    n_pts, worst = 0, 0.0
    for slide in list(prs.slides)[1:]:
        charts = [sh.chart for sh in slide.shapes if sh.has_chart]
        assert len(charts) == 2
        for ch, (tab, names) in zip(charts, tabs):
            ws = rec[tab]
            hdr = [c.value for c in ws[1]]
            for s in ch.plots[0].series:
                col = hdr.index(s.name) + 1
                wb_vals = [ws.cell(r, col).value for r in range(2, len(win) + 2)]
                for a, b in zip(s.values, wb_vals):
                    worst = max(worst, abs(a - b))
                    n_pts += 1
                assert len(s.values) == len(wb_vals)
            cats = list(ch.plots[0].categories)
            dates = [ws.cell(r, 1).value for r in range(2, len(win) + 2)]
            exp = [d.strftime('%Y-%m') if d.month in (1, 7) else ' ' for d in dates]
            assert cats == exp, f'{tab}: category labels do not follow the tab dates'
    lines.append(f'2. chart points (incl. Reference), both slide versions, vs workbook chart tabs: {n_pts} points; max abs diff {worst:.2e}; category labels match tab dates (Jan/Jul)')
    ok &= worst < 1e-9
    # 3. script values vs the audited Slide 1 research series (A_ts_pce_rates.csv, 5 dp)
    x = {(r['month'], r['measure']): r for r in csv.DictReader(open(XCHECK))}
    diffs = []
    for m in win:
        for key, meas, col in (('core12', 'core', 'rate_12m_pct'), ('head12', 'headline', 'rate_12m_pct'),
                               ('core3', 'core', 'rate_3m_ann_pct'), ('core6', 'core', 'rate_6m_ann_pct')):
            diffs.append(abs(rates[m][key] - float(x[(m, meas)][col])))
    lines.append(f'3. vs Slide1_Inflation_Data series (A_ts_pce_rates.csv): {len(diffs)} values; max abs diff {max(diffs):.2e} pp (csv rounded to 5 dp)')
    ok &= max(diffs) < 1e-4
    # 4. end labels == last workbook values; layout rules
    want = [round(rates[win[-1]][k], 2) for k in ('core12', 'head12', 'core3', 'core6')]
    lab_ok = True
    for lay, labs in labels.items():
        for name, v, yc, ytop in labs:
            lines.append(f'   [{lay}] end label {name}: {v:.2f}%{EST_MARK} at y={yc:.3f} in (box top {ytop:.3f})')
        lab_ok &= [l[1] for l in labs] == want
    ok &= lab_ok
    allv = [rates[m][k] for m in win for k in ('core12', 'head12', 'core3', 'core6')] + [REFERENCE]
    lines.append(f'4. y-axis {YMIN}-{ymax} step {YSTEP} (data max {max(allv):.3f}, min {min(allv):.3f}); window {win[0]}..{win[-1]}; end labels = last values (both versions): {lab_ok}')
    import zipfile
    names = zipfile.ZipFile(OUT_PPTX).namelist()
    dup = sorted({n for n in names if names.count(n) > 1})
    sec = [sh.text_frame.text for sh in prs.slides[0].shapes if sh.has_text_frame]
    lines.append(f'5. deck: {len(prs.slides)} slides (section, slide 1 guide layout, slide 1 wide); section texts {sec}; duplicate zip entries: {dup or "none"}')
    ok &= (not dup) and sec == ['Inflation', 'SECTION 1'] and len(prs.slides) == 1 + len(LAYOUTS)
    lines.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    if not ok:
        sys.exit(1)


def main(do_verify):
    allm, win, L, rates, est, band = load_data()
    allv = [rates[m][k] for m in win for k in ('core12', 'head12', 'core3', 'core6')] + [REFERENCE]
    ymax = math.ceil(max(allv))
    assert min(allv) >= 0, 'data go negative: style guide floor rule needed'
    steps = (ymax - YMIN) / YSTEP
    assert steps <= 10
    wb, nt = build_workbook(allm, win, L, rates, est, band, ymax)
    os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)
    wb.save(OUT_XLSX)
    labels = build_pptx(win, rates, ymax)
    # cross-check summary into Notes
    x = {(r['month'], r['measure']): r for r in csv.DictReader(open(XCHECK))}
    md = max(abs(rates[m][k] - float(x[(m, meas)][c])) for m in win for k, meas, c in
             (('core12', 'core', 'rate_12m_pct'), ('head12', 'headline', 'rate_12m_pct'), ('core3', 'core', 'rate_3m_ann_pct'), ('core6', 'core', 'rate_6m_ann_pct')))
    wb2 = load_workbook(OUT_XLSX)
    n2 = wb2['Notes']
    n2.cell(n2.max_row, 2, round(md, 8))
    wb2.calculation.fullCalcOnLoad = True     # no cached results from openpyxl: make Excel compute every formula on open
    wb2.save(OUT_XLSX)
    print(f'wrote {REL(OUT_XLSX)} and {REL(OUT_PPTX)}; y-axis 0-{ymax}; last date {win[-1]}')
    if do_verify:
        verify(win, rates, ymax, labels)


if __name__ == '__main__':
    main('--verify' in sys.argv)
