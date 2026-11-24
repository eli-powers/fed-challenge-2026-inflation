"""Build Inflation slide 3B (forecast: SPF median with oil price scenarios) and its workbook.

Run from the project root:
    python3 -I "02_Research/Subtasks/16_slide3b_build/code/build_inflation_slide3b.py" --verify

Eli, Nov 16:
  - one time series, core PCE q/q annualized (SPF basis), 2025Q4-2027Q4; one actual line through 2026Q3 that splits
    into labelled paths from 2026Q4; forecast region shaded;
  - P1 (Nov STEO oil path) dropped: on the Q4 SPF it equals the baseline; pre-pandemic pass-through dropped
    (flagged verbally); paths shown = SPF median, oil to $110, Hormuz reopens (both post-pandemic pass-through);
  - right-hand side: 2027 Q4/Q4 (Q4 2026 to Q4 2027) for each path;
  - title "Inflation Forecast: SPF Median with Oil Price Scenarios"; heading = Claude draft for Eli to confirm;
    takeaway = placeholder.
Inputs: the forecast_3b pipeline (raw/<latest>/PCEPILFE_observations.json; processed/scenario_grid_2026Q4.csv).
Writes 01_Finals/Slide data/Inflation Slide 3B.xlsx; appends the slide after the last slide of the working deck
(replacing an earlier copy of itself). Helpers come from 14_slide2a_build and 15_slide3a_build.
"""
import csv
import datetime as dt
import json
import os
import subprocess
import sys

from openpyxl import Workbook
from openpyxl.styles import PatternFill
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '14_slide2a_build', 'code'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '15_slide3a_build', 'code'))
import build_inflation_slide2ab as b2  # noqa: E402
import build_inflation_slide3a as b3  # noqa: E402

rgb, text_box = b2.rgb, b2.text_box
NAVY, RED, DNAVY, BLACK, LGRAY = b2.NAVY, b2.RED, b2.DNAVY, b2.BLACK, b2.LABEL_GRAY
SHADE = 'E3E3E3'
SPF = '2026Q4'
PIPE = os.path.join(ROOT, '03_Data', 'pipelines', 'forecast_3b')
GRID = os.path.join(PIPE, 'processed', f'scenario_grid_{SPF}.csv')
META = os.path.join(PIPE, 'processed', f'metadata_{SPF}.json')
XLSX = os.environ.get('SLIDE3B_SLIDE_XLSX') or os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 3B.xlsx')
DECK = os.environ.get('SLIDE3B_DECK') or b2.DECK
REPORT = os.path.join(HERE, 'verify_report.txt')
REL = lambda p: os.path.relpath(p, ROOT)

S = dict(title=('Inflation Forecast', 'SPF Median with Oil Price Scenarios'),
         heading='Core PCE Inflation Through 2027 Under Two Oil Paths',
         source=('Source: BEA via FRED (PCEPILFE); Philadelphia Fed SPF, Q4 2026 median; EIA (Brent; STEO); FEDS Notes (Nov 9, 2026), '
                 'post-pandemic pass-through; UMD calc. Core PCE, % q/q annualized, SA, actual through 2026Q3. Dashed line: SPF median.'))
MARK = S['title'][1]
Q = ['2025Q4', '2026Q1', '2026Q2', '2026Q3', '2026Q4', '2027Q1', '2027Q2', '2027Q3', '2027Q4']
LAST_ACT = '2026Q3'
PATHS = [('spf', 'SPF median', BLACK, None), ('p2', 'Oil to $110', RED, 'P2_110_flat'), ('p3', 'Hormuz reopens', DNAVY, 'P3_feb26steo_plus25')]
PLOT_X, PLOT_Y = (1.53, 9.27), (1.80, 5.60)
RENDER_X = (1.398, 8.958)   # where PowerPoint actually draws this plot (measured from the PowerPoint PDF export, Nov 16);
                            # the shaded region and end labels are placed on these, not on PLOT_X
YLO, YHI, YSTEP = 0, 4, 1
EXPECT = {}


def qmonths(q):
    y, n = int(q[:4]), int(q[-1])
    return [f'{y}-{m:02d}' for m in range(3 * n - 2, 3 * n + 1)]


def prevq(q):
    y, n = int(q[:4]), int(q[-1])
    return f'{y - 1}Q4' if n == 1 else f'{y}Q{n - 1}'


# ================================================================ data
def load():
    meta = json.load(open(META))
    raw = os.path.join(ROOT, meta['raw_folder'])
    fred = json.load(open(os.path.join(raw, 'PCEPILFE_observations.json')))['observations']
    idx = {o['date'][:7]: float(o['value']) for o in fred if o['value'] != '.'}
    D = {'meta': meta, 'raw': raw, 'idx': idx, 'months': b2.months('2025-07', '2026-09')}
    qa = lambda q: sum(idx[m] for m in qmonths(q)) / 3
    D['act'] = {q: ((qa(q) / qa(prevq(q))) ** 4 - 1) * 100 for q in Q if q <= LAST_ACT}
    rows = list(csv.DictReader(open(GRID)))
    cen = [r for r in rows if r['is_central'] == 'True' and r['regime'] == 'post']
    get = lambda var, q, col: float([r for r in cen if r['oil_variant'] == var and r['quarter'] == q][0][col])
    fq = [q for q in Q if q > LAST_ACT]
    D['scen'] = {'spf': {q: get('P2_110_flat', q, 'baseline_qq_ann') for q in fq}}
    for k, _, _, var in PATHS[1:]:
        D['scen'][k] = {q: get(var, q, 'scenario_qq_ann') for q in fq}
    D['pipe_q4q4'] = {'spf': get('P2_110_flat', '2027Q4/2026Q4', 'baseline_qq_ann')}
    for k, _, _, var in PATHS[1:]:
        D['pipe_q4q4'][k] = get(var, '2027Q4/2026Q4', 'scenario_qq_ann')
    D['spf_pub_2027'] = meta['spf_published_q4q4']['2027']
    D['q4q4'] = {}
    for k in D['scen']:
        p = 1.0
        for q in ('2027Q1', '2027Q2', '2027Q3', '2027Q4'):
            p *= (1 + D['scen'][k][q] / 100) ** 0.25
        D['q4q4'][k] = (p - 1) * 100
    # cross-checks: actual quarters vs pipeline (status=actual rows), Q4/Q4 vs pipeline rows
    pa = {r['quarter']: float(r['baseline_qq_ann']) for r in cen if r['oil_variant'] == 'P2_110_flat' and r['status'] == 'actual'}
    D['checks'] = {'actual q/q vs pipeline (2026Q1-Q3)': max(abs(D['act'][q] - pa[q]) for q in pa),
                   '2027 Q4/Q4 vs pipeline': max(abs(D['q4q4'][k] - D['pipe_q4q4'][k]) for k in D['q4q4'])}
    assert max(D['checks'].values()) < 1e-6, D['checks']
    assert meta['spf_vintage'] == SPF and meta['last_actual_quarter'] == LAST_ACT, meta
    return D


# ================================================================ workbook
def build_wb(D):
    wb = Workbook()
    grey = PatternFill('solid', fgColor='D9D9D9')
    rp = wb.active
    rp.title = 'Raw_PCE'
    rp.append(['Month', f"PCEPILFE core PCE price index, SA (FRED realtime {D['meta']['core_pce_vintage'][-10:]})"])
    RP = {}
    for m in D['months']:
        rp.append([b2.mdate(m), D['idx'][m]])
        rp.cell(rp.max_row, 1).number_format = 'yyyy-mm'
        RP[m] = rp.max_row
    b2.fmt_hdr(rp, [10, 40])
    rs = wb.create_sheet('Raw_scenarios')
    rs.append(['Quarter', 'SPF Q4 2026 median, q/q ann.', 'Oil to $110 (P2, post-pandemic), q/q ann.', 'Hormuz reopens (P3, post-pandemic), q/q ann.'])
    RS = {}
    for q in Q:
        if q <= LAST_ACT:
            continue
        rs.append([q] + [D['scen'][k][q] for k, _, _, _ in PATHS])
        RS[q] = rs.max_row
    b2.fmt_hdr(rs, [10, 22, 26, 26])
    for ws in (rp, rs):
        ws.sheet_properties.tabColor = '808080'
        for c in ws[1]:
            c.fill = grey

    tf = wb.create_sheet('Forecast')
    tf.append(['Date', 'Actual', 'SPF median', 'Oil to $110', 'Hormuz reopens'])
    TF = {}
    for q in Q:
        r = tf.max_row + 1
        TF[q] = r
        y, n = int(q[:4]), int(q[-1])
        tf.cell(r, 1, dt.datetime(y, 3 * n - 2, 1)).number_format = 'yyyy-mm'
        if q <= LAST_ACT:
            cur = '+'.join(f'Raw_PCE!B{RP[m]}' for m in qmonths(q))
            prv = '+'.join(f'Raw_PCE!B{RP[m]}' for m in qmonths(prevq(q)))
            tf.cell(r, 2, f'=((({cur})/({prv}))^4-1)*100').number_format = '0.00'
            EXPECT[('Forecast', f'B{r}')] = D['act'][q]
            if q == LAST_ACT:                       # paths start at the last actual so the lines join
                for j in range(3):
                    tf.cell(r, 3 + j, f'=B{r}').number_format = '0.00'
                    EXPECT[('Forecast', tf.cell(r, 3 + j).coordinate)] = D['act'][q]
        else:
            for j, (k, _, _, _) in enumerate(PATHS):
                tf.cell(r, 3 + j, f'=Raw_scenarios!{"BCD"[j]}{RS[q]}').number_format = '0.00'
                EXPECT[('Forecast', tf.cell(r, 3 + j).coordinate)] = D['scen'][k][q]
    b2.fmt_hdr(tf, [10, 10, 12, 12, 14])

    tq = wb.create_sheet('Q4Q4_2027')
    tq.append(['Path', '2027 Q4/Q4 % (2027Q4 over 2026Q4)', 'Shown on slide', 'Pipeline value (check)'])
    for j, (k, lab, _, _) in enumerate(PATHS):
        r = tq.max_row + 1
        col = 'CDE'[j]
        terms = '*'.join(f'(1+Forecast!{col}{TF[q]}/100)^0.25' for q in ('2027Q1', '2027Q2', '2027Q3', '2027Q4'))
        tq.cell(r, 1, lab)
        tq.cell(r, 2, f'=({terms}-1)*100').number_format = '0.00'
        tq.cell(r, 3, f'=TEXT(B{r},"0.0")&"%"')
        tq.cell(r, 4, D['pipe_q4q4'][k]).number_format = '0.0000'
        EXPECT[('Q4Q4_2027', f'B{r}')] = D['q4q4'][k]
    r = tq.max_row + 2
    tq.cell(r, 1, 'SPF published 2027 Q4/Q4 median (not plotted)')
    tq.cell(r, 2, D['spf_pub_2027'])
    tq.cell(r + 1, 1, 'The SPF row compounds the median quarterly path; the published annual median comes from the same survey but a '
                      'different question, so the two differ slightly.')
    b2.fmt_hdr(tq, [30, 22, 14, 18])

    ck = '; '.join(f'{k} {v:.2e}' for k, v in D['checks'].items())
    m = D['meta']
    b2.notes_tab(wb, [
        ('Title', f"{S['title'][0]}: {S['title'][1]}", 'Eli, Nov 16 ("something like"); apostrophe in "Scenario\'s" dropped'),
        ('Chart heading', S['heading'], 'DRAFT by Claude, for Eli to confirm'),
        ('Chart', 'Core PCE, % q/q annualized, 2025Q4-2027Q4. Actual (gray) through 2026Q3; from 2026Q4 SPF median (black dashed), '
                  'Oil to $110 (red), Hormuz reopens (dark navy). The three paths start at the 2026Q3 actual so the lines join. Shaded = forecast quarters.',
         f"Forecast tab. Actual = quarterly average of monthly PCEPILFE (Raw_PCE; {REL(os.path.join(D['raw'], 'PCEPILFE_observations.json'))}). "
         f"Paths = Raw_scenarios, copied from {REL(GRID)} (central variants, post-pandemic regime; baseline_qq_ann / scenario_qq_ann). "
         'The live-formula derivation of every scenario cell is in 01_Finals/data/Slide3B_Inflation_Data.xlsx (Scenario_grid).'),
        ('Right-hand panel', '2027 Q4/Q4 per path, one decimal', 'Q4Q4_2027 tab: product of the four 2027 quarters on the Forecast tab'),
        ('Inputs and vintages', f"SPF {m['spf_vintage']} (deadline {m['spf_deadline']}, released {m['spf_release']}); oil assumption proxy: "
         f"{m['assumption_proxies']['steo_matched']}; Brent to {m['oil']['last_brent_date']} (${m['oil']['last_brent_usd']}); core PCE {m['core_pce_vintage']}",
         REL(META)),
        ('Oil paths', 'Oil to $110 = Brent flat at $110 (Bowman, Nov 10: Brent "moved up to and above $110" in late October). '
                      'Hormuz reopens = Feb 2026 STEO (pre-war) + $25 (midpoint of Waller\'s $20-30 cost of current passage, Nov 10).',
         '02_Research/Subtasks/12_slide3b_research/outputs/B_q3_path_definitions.md'),
        ('Pass-through', 'Post-pandemic dynamics of the FEDS oil note (five-economy panel; authors call the projection an upper bound). '
                         'Pre-pandemic results are verbal only (2027 Q4/Q4: $110 2.61, reopens 2.54).', 'Eli, Nov 16: post-pandemic only on the slide'),
        ('Dropped from the slide', 'P1 (Nov STEO path): equals the baseline on the Q4 SPF (2027 Q4/Q4 2.52)', 'Eli, Nov 16'),
        ('Source line', S['source'], ''),
        ('Takeaway', b2.TAKEAWAY, 'placeholder'),
        ('Cross-checks', ck, 'max abs diff vs the pipeline CSV'),
        ('Guide deviations', '(1) four lines (actual gray #595959, SPF dashed black, two paths red / dark navy); the guide allows two plus a reference; '
                             '(2) the dashed line is a forecast path, not a constant reference; (3) shaded forecast region; (4) quarterly labels; '
                             '(5) right-hand value column; (6) end labels one decimal in the right column.', ''),
        ('Build', 'python3 -I "02_Research/Subtasks/16_slide3b_build/code/build_inflation_slide3b.py" --verify', ''),
    ])
    wb._sheets = [tf, tq, rp, rs, wb['Notes']]
    wb.calculation.fullCalcOnLoad = True
    return wb


# ================================================================ slide
def xpos(i):
    return RENDER_X[0] + i / (len(Q) - 1) * (RENDER_X[1] - RENDER_X[0])


def ypos(v, py=PLOT_Y):
    return py[1] - (v - YLO) / (YHI - YLO) * (py[1] - py[0])


PLOT_Y_ALT = (2.16, 5.60)    # alternate: room for a panel title at 1.80 (guide s.5 convention)


def line(s, x1, y1, x2, y2, color, w=1.0, arrow=False):
    from pptx.enum.shapes import MSO_CONNECTOR
    from lxml import etree
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(w)
    if arrow:
        ln = c.line._get_or_add_ln()
        te = etree.SubElement(ln, qn('a:tailEnd'))
        te.set('type', 'triangle'); te.set('w', 'med'); te.set('len', 'med')
    return c


def build_slide(prs, D, alt=False):
    """alt=True (Eli, Nov 16, options 1-3): panel title naming the quarterly unit; a '2027' bracket over 2027Q1-Q4 with an
    arrow to the right-hand column; the column headed '2027 as a whole' and set off by a divider."""
    PLOT_Y = PLOT_Y_ALT if alt else globals()['PLOT_Y']
    ypos_ = lambda v: ypos(v, PLOT_Y)
    s = b2.base_slide(prs, S)
    # shaded forecast region (behind the chart; the chart has no fill)
    x0 = xpos(Q.index(LAST_ACT))
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0), Inches(PLOT_Y[0]), Inches(RENDER_X[1] - x0), Inches(PLOT_Y[1] - PLOT_Y[0]))
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(SHADE)
    sh.line.fill.background()
    sh.shadow.inherit = False
    text_box(s, x0 + 0.08, (PLOT_Y[1] - 0.36) if alt else (PLOT_Y[0] + 0.05), RENDER_X[1] - x0 - 0.16, 0.28,
             [('Forecast: SPF median and oil scenarios', LGRAY)], 12, 'Arial', align=PP_ALIGN.LEFT, bold=True)
    if alt:
        text_box(s, RENDER_X[0] - 0.3, 1.80, RENDER_X[1] - RENDER_X[0] + 0.6, 0.30, [('Quarterly pace, % change at an annual rate', NAVY)], 13, 'Arial', bold=True)
    cd = CategoryChartData()
    cd.categories = Q
    act = [D['act'].get(q) for q in Q]
    ser = {'Actual': act}
    for j, (k, lab, _, _) in enumerate(PATHS):
        ser[lab] = [D['act'][q] if q == LAST_ACT else (D['scen'][k][q] if q > LAST_ACT else None) for q in Q]
    order = ['Actual', 'Oil to $110', 'Hormuz reopens', 'SPF median']
    for n in order:
        cd.add_series(n, ser[n])
    fr = (PLOT_X[0] - 0.62, PLOT_Y[0] - 0.08, PLOT_X[1] + 0.08, PLOT_Y[1] + 0.36)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(fr[0]), Inches(fr[1]), Inches(fr[2] - fr[0]), Inches(fr[3] - fr[1]), cd)
    ch = gf.chart
    ch.has_title = ch.has_legend = False
    sty = {'Actual': (LGRAY, 3, None), 'Oil to $110': (RED, 3, None), 'Hormuz reopens': (DNAVY, 3, None),
           'SPF median': (BLACK, 2.25, MSO_LINE_DASH_STYLE.DASH)}
    for se in ch.plots[0].series:
        c, w, dash = sty[se.name]
        se.format.line.color.rgb = rgb(c)
        se.format.line.width = Pt(w)
        if dash:
            se.format.line.dash_style = dash
        se.marker.style = XL_MARKER_STYLE.NONE
        se.smooth = False
    b2.axes(ch, YLO, YHI, YSTEP, '0.00', cat_size=12)
    cs = b2.frame_fix(ch, PLOT_X, PLOT_Y, fr)
    from lxml import etree
    for vax in cs.iter(qn('c:valAx')):
        cb = vax.find(qn('c:crossBetween'))
        if cb is None:
            cb = etree.SubElement(vax, qn('c:crossBetween'))
        cb.set('val', 'midCat')
    # gaps stay gaps (no zero, no bridging across the empty forecast part of "Actual")
    dbl = cs.find(qn('c:chart')).find(qn('c:dispBlanksAs'))
    if dbl is None:
        dbl = etree.SubElement(cs.find(qn('c:chart')), qn('c:dispBlanksAs'))
    dbl.set('val', 'gap')
    # end labels (names) beside each path's last point; right-hand column = 2027 Q4/Q4
    last = {lab: ser[lab][-1] for _, lab, _, _ in PATHS}
    labs = sorted([(lab, last[lab], col, k) for k, lab, col, _ in PATHS], key=lambda t: -t[1])
    ys = [ypos_(v) for _, v, _, _ in labs]
    h = 0.32
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + h + 0.02)
    if not alt:
        XL, XV, WV = RENDER_X[1] + 0.15, 11.05, 1.25
        text_box(s, XV - 0.35, PLOT_Y[0] + 0.05, 1.95, 0.62, [[('2027, Q4/Q4', NAVY)], [('Q4 2026 to Q4 2027', NAVY)]], 13, 'Arial', bold=True)
    else:
        XL, XV, WV = RENDER_X[1] + 0.08, 11.20, 1.30
        XH0, XH1, XDIV = 11.00, 12.70, 10.95
        yb = PLOT_Y[0] + 0.30                                  # bracket over 2027Q1-2027Q4
        xa, xb = xpos(Q.index('2027Q1')), xpos(Q.index('2027Q4'))
        line(s, xa, yb, xb, yb, NAVY, 1.25)
        line(s, xa, yb, xa, yb + 0.12, NAVY, 1.25)
        line(s, xb, yb, xb, yb + 0.12, NAVY, 1.25)
        text_box(s, xa, yb - 0.27, xb - xa, 0.24, [('2027', NAVY)], 12, 'Arial', bold=True)
        line(s, xb + 0.06, yb, XH0 - 0.04, yb, NAVY, 1.25, arrow=True)
        text_box(s, XH0, yb - 0.26, XH1 - XH0, 0.56, [[('2027 as a whole', NAVY)], [('Q4 2026 to Q4 2027', NAVY)]], 13, 'Arial', bold=True)
        s.shapes[-1].text_frame.paragraphs[1].runs[0].font.size = Pt(11)
        s.shapes[-1].text_frame.paragraphs[1].runs[0].font.bold = False
    for (lab, v, col, k), y in zip(labs, ys):
        text_box(s, XL, y - h / 2, 1.85, h, [(lab, col)], 16, 'Arial', align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text_box(s, XV, y - h / 2, WV, h, [(f"{D['q4q4'][k]:.1f}%", col)], 20, 'Arial', align=PP_ALIGN.CENTER, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if alt:
        line(s, XDIV, yb + 0.40, XDIV, ys[-1] + 0.30, b2.AXIS_GRAY, 1.0)
    D['label_y'] = dict(zip([l for l, _, _, _ in labs], ys))
    return s


def build_pptx(D):
    from pptx.opc.packuri import PackURI
    prs = Presentation(DECK)
    lst = prs.slides._sldIdLst
    for sid, slide in zip(list(lst), list(prs.slides)):
        if MARK in b3.title_of(slide):
            prs.part.drop_rel(sid.get(qn('r:id')))
            lst.remove(sid)
    used = {str(pt.partname) for pt in prs.part.package.iter_parts()}
    k = 400
    for alt in (False, True):            # main version, then the alternate (Eli compares)
        s = b3.guide_fix(build_slide(prs, D, alt=alt))
        while f'/ppt/slides/slide{k}.xml' in used:
            k += 1
        s.part.partname = PackURI(f'/ppt/slides/slide{k}.xml')
        used.add(f'/ppt/slides/slide{k}.xml')
    prs.save(DECK)


def sigs_others(path):
    old = b3.MARKS
    b3.MARKS = (MARK,)
    try:
        return b3.sigs_others(path)
    finally:
        b3.MARKS = old


def verify(D, before):
    import zipfile
    L = [f'Inflation slide 3B build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    rec = b2.recalc(XLSX)
    bad = [(k, v, rec[k[0]][k[1]].value) for k, v in EXPECT.items()
           if not isinstance(rec[k[0]][k[1]].value, (int, float)) or abs(rec[k[0]][k[1]].value - v) > 1e-9]
    L.append(f'1. workbook formula cells: {len(EXPECT)} checked after LibreOffice recalc; mismatches: {len(bad)} {bad[:3]}')
    ok &= not bad
    L.append('2. cross-checks vs pipeline CSV (max abs diff): ' + '; '.join(f'{k} {v:.1e}' for k, v in D['checks'].items()))
    prs = Presentation(DECK)
    sl = list(prs.slides)
    ours = [x for x in sl if MARK in b3.title_of(x)]
    ok &= len(ours) == 2
    ws = rec['Forecast']
    col = {'Actual': 2, 'SPF median': 3, 'Oil to $110': 4, 'Hormuz reopens': 5}
    worst, n = 0.0, 0
    for o in ours:
        ch = [sh.chart for sh in o.shapes if sh.has_chart][0]
        for se in ch.plots[0].series:
            for i, v in enumerate(se.values):
                w = ws.cell(2 + i, col[se.name]).value
                if v is None or w is None:
                    ok &= (v is None and w is None)
                    continue
                worst, n = max(worst, abs(v - w)), n + 1
    L.append(f'3. chart points vs Forecast tab (main + alternate): {n} points (expected {2 * (4 + 3 * 6)}); max abs diff {worst:.1e}; blanks match')
    ok &= worst < 1e-9 and n == 2 * (4 + 3 * 6)
    vals = list(D['act'].values()) + [v for k in D['scen'] for v in D['scen'][k].values()]
    fit = YLO <= min(vals) and max(vals) <= YHI
    L.append(f'4. axis {YLO}..{YHI} step {YSTEP}; data {min(vals):.2f}..{max(vals):.2f}; fit {fit}')
    ok &= fit
    tq = rec['Q4Q4_2027']
    shown = [tq.cell(r, 3).value for r in (2, 3, 4)]
    present = all(sv in b3.title_of(o) for o in ours for sv in shown)
    L.append(f'5. right-hand values {shown} (workbook TEXT cells) present on the slide: {present}; '
             f"2027 Q4/Q4: SPF {D['q4q4']['spf']:.4f}, $110 {D['q4q4']['p2']:.4f}, reopens {D['q4q4']['p3']:.4f}; SPF published {D['spf_pub_2027']}")
    ok &= present
    after = sigs_others(DECK)
    same = after == before
    names = zipfile.ZipFile(DECK).namelist()
    dup = sorted({x for x in names if names.count(x) > 1})
    L.append(f'6. deck: {len(sl)} slides; 3B main / alternate at positions {[sl.index(o) + 1 for o in ours]}; all other slides unchanged: {same}; duplicates: {dup or "none"}')
    L.append('   order: ' + ' | '.join(b3.title_of(x)[:40] for x in sl))
    ok &= same and not dup
    L.append('7. plotted values: ' + '; '.join(f'{q} act {D["act"][q]:.2f}' for q in D['act']) + ' | ' +
             '; '.join(f'{lab} ' + '/'.join(f'{D["scen"][k][q]:.2f}' for q in Q if q > LAST_ACT) for k, lab, _, _ in PATHS))
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
    print(f'wrote {REL(XLSX)}; appended slide 3B to {REL(DECK)}')
    if do_verify:
        verify(D, before)


if __name__ == '__main__':
    main('--verify' in sys.argv)
