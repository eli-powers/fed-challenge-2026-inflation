"""Build the Inflation Slide 2A data workbook and slide 2A ("what's driving it") in our working deck.

Run from the project root:
    python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2a.py"            # build
    python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2a.py" --verify   # build + checks

Outputs
  01_Finals/Slide data/Inflation Slide 2A.xlsx      every number on the slide, with source
  01_Finals/slides/Inflation Slides (working).pptx  slide 2A appended after the existing slides (section, slide 1 x2), which are not changed

Inputs (all saved locally)
  BEA U20404/U20405 (Oct 29, 2026 release, saved Nov 10): 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U2040{4,5}_2026-11-10.json
  UMD October estimate (leaf m/m): 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv (via C_common.py)
  Shock tags: 02_Research/Subtasks/08_shock_tagging/proposed_tags.csv (tag_final)
Recomputed here from the raw files (fresh run of 10_slide2_research/code/H_oct_drivers.py for categories; group excess
recomputed directly through C_common) and cross-checked against the audited outputs H_oct_drivers_categories.csv and
G_excess_path.csv (slide2_followups audit).

Decisions (Eli, Nov 15; slide build prompt Step 0 answers): two-chart slide 2A. Left = excess contribution vs 2018-19 by BEA
category, Oct 2026* only, top six categories + housing, horizontal bars, BEA names (spoken script maps to shocks). Right =
excess by shock group, grouped bars Mar 2025 (dark navy) vs Oct 2026* (red). Same y-range both panels (-0.20 to 0.80 pp,
step 0.20, format 0.00); value labels with an asterisk on Oct values; note line defining the measure; title "Inflation:
Three Shocks Now Drive the Excess"; heading and panel titles drafted by Claude (Eli to confirm); source line as proposed
plus "shock tags: UMD"; takeaway = placeholder; guide layout only.
"""
import datetime as dt
import hashlib
import math
import os
import runpy
import subprocess
import sys
import zipfile

import pandas as pd
from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RES = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research')
H_SCRIPT = os.path.join(RES, 'code', 'H_oct_drivers.py')
H_CSV = os.path.join(RES, 'outputs', 'H_oct_drivers_categories.csv')
G_CSV = os.path.join(RES, 'outputs', 'G_excess_path.csv')
TAGS = os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv')
OUT_XLSX = os.environ.get('SLIDE2A_XLSX') or os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 2A.xlsx')
DECK = os.path.join(ROOT, '01_Finals', 'slides', 'Inflation Slides (working).pptx')
OUT_PPTX = os.environ.get('SLIDE2A_PPTX') or DECK
SCRATCH = os.environ.get('SLIDE2A_SCRATCH', '/tmp')
REPORT = os.path.join(ROOT, '02_Research', 'Subtasks', '14_slide2a_build', 'code', 'verify_report.txt')
REL = lambda p: os.path.relpath(p, ROOT)
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

# ---------------------------------------------------------------- style guide constants and slide text
NAVY, WHITE, GOLD, LIGHT = '1B2A4A', 'FFFFFF', 'F2CC6B', 'F2F2F2'
RED, DNAVY = 'C0282D', '1B2A61'
AXIS_GRAY, LABEL_GRAY, SOURCE_GRAY = '7F7F7F', '595959', '6B6B6B'
TITLE = ('Inflation', 'Three Shocks Now Drive the Excess')
HEADING = 'Core PCE Inflation Above Its Pre-Pandemic Pace: Where It Comes From'      # DRAFT (Claude); Eli to confirm
PANEL_L = 'By spending category, Oct 2026*'                                            # DRAFT
PANEL_R = 'By shock exposure, Mar 2025 vs Oct 2026*'                                   # DRAFT
NOTE = 'Excess = contribution to core PCE 12-month inflation above its 2018–19 average · *Oct 2026 = UMD estimate'
SOURCE = ('Source: BEA (PCE price indexes and spending, Tables 2.4.4U/2.4.5U); UMD calculations; shock tags: UMD. '
          'Percentage points of core PCE 12-month inflation above the 2018–19 average, monthly data through Oct 2026*. '
          '*Oct 2026 = UMD estimate built from BLS CPI/PPI.')
TAKEAWAY = '[Takeaway: one sentence the team writes]'
SLIDE_MARK = 'Three Shocks Now Drive the Excess'        # identifies an existing 2A slide on rebuild

PLOT_L = (2.60, 5.13)          # deviation from s.5 (1.27-5.13): BEA category names need ~2.2 in left of a horizontal bar plot
PLOT_R = (7.40, 11.27)         # s.5
PLOT_Y = (2.40, 5.60)          # s.5 with a note line
PANEL_TOP = 2.07
YMIN, YMAX, YSTEP = -0.20, 0.80, 0.20
TOP_CATS = [38, 190, 172, 280, 104, 234]   # six largest Oct excesses (asserted below), then housing
HOUSING = 153
GROUPS = [('energy', 'Energy'), ('tariff', 'Tariffs'), ('AI', 'AI'), ('untagged', 'All other')]
MONTHS = [('2025-03', 'Mar 2025'), ('2026-10', 'Oct 2026')]


def rgb(h):
    return RGBColor.from_string(h)


# ---------------------------------------------------------------- data (recomputed from raw)
def load_data():
    # categories: fresh run of the audited H script (rewrites its CSVs with identical content), compared to the audited CSV
    audited = pd.read_csv(H_CSV)          # read the audited snapshot BEFORE H rewrites it (Codex slide2a_build R1-F01)
    g = runpy.run_path(H_SCRIPT, run_name='h_rerun')
    R = g['R']
    m = R.merge(audited, on=['period', 'line'], suffixes=('', '_aud'))
    dmax = max((m[c] - m[c + '_aud']).abs().max() for c in ('contrib_12m', 'contrib_12m_2018_19_avg', 'excess_vs_2018_19'))
    assert dmax < 1e-9, f'category recompute differs from audited H csv by {dmax}'
    cats = R[R.period == '2026-10'].set_index('line')
    sep = R[R.period == '2026-09'].set_index('line')
    ranked = cats.drop(index=374).sort_values('excess_vs_2018_19', ascending=False).index.tolist()
    assert ranked[:6] == TOP_CATS, f'top six categories changed: {ranked[:6]}'
    # groups: excess over own 2018-19 12m pace, recomputed through C_common
    t = pd.read_csv(TAGS)
    t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
    tag = dict(zip(t.leaf, t.tag_final))
    core = set(cc.LEAVES_CORE)

    def grp(month):
        d = cc.unit_table('leaf', core, month, 12)
        d['tag'] = d.leaf.map(tag)
        out = {}
        for gk, _ in GROUPS:
            y = d[d.tag == gk]
            out[gk] = (y.w.sum() / d.w.sum(), (y.w * y.r).sum() / y.w.sum())
        return out
    base = {gk: 0.0 for gk, _ in GROUPS}
    pre = [f'{y}-{mo:02d}' for y in (2018, 2019) for mo in range(1, 13)]
    for mth in pre:
        o = grp(mth)
        for gk in base:
            base[gk] += o[gk][1] / len(pre)
    G = {mth: grp(mth) for mth, _ in MONTHS}
    gaud = pd.read_csv(G_CSV).set_index('month')
    gmax = 0.0
    for mth, _ in MONTHS:
        for gk, _ in GROUPS:
            s, r = G[mth][gk]
            gmax = max(gmax, abs(s * (r - base[gk]) - gaud.at[mth, f'{gk}_excess_pp']))
    assert gmax < 6e-5, f'group recompute differs from audited G csv by {gmax}'
    return R, cats, sep, G, base, dmax, gmax


# ---------------------------------------------------------------- workbook
EXPECT = {}


def build_workbook(R, cats, sep, G, base):
    wb = Workbook()
    hb = Font(bold=True)
    # Raw_categories: all 15 core BEA categories, Sep and Oct, from the H recompute
    rc = wb.active
    rc.title = 'Raw_categories'
    rc.append(['BEA line', 'Category (BEA name)', 'Weight in core, Oct 2026* (%)', '12m rate, Oct 2026* (%)',
               '12m contribution, Sep 2026 (pp)', '12m contribution, Oct 2026* (pp)', 'Average 12m contribution 2018-19 (pp)',
               'Source'])
    RROW = {}
    lines = [ln for ln in cats.index if ln != 374]
    for ln in lines:
        rc.append([int(ln), cats.at[ln, 'category'], cats.at[ln, 'weight_pct'], cats.at[ln, 'rate_12m'], sep.at[ln, 'contrib_12m'],
                   cats.at[ln, 'contrib_12m'], cats.at[ln, 'contrib_12m_2018_19_avg'],
                   'exact Fisher contribution (03_Data/pipelines/Price indexes/code/sector_contributions.py), recomputed by '
                   '10_slide2_research/code/H_oct_drivers.py from BEA U20404/U20405 (saved 2026-11-10) + UMD Oct leaf estimate'])
        RROW[ln] = rc.max_row
    rc.append(['374', 'TOTAL core (sum)', None, cats.at[374, 'rate_12m'], sep.at[374, 'contrib_12m'], cats.at[374, 'contrib_12m'],
               cats.at[374, 'contrib_12m_2018_19_avg'], 'sum of categories; core 12m rate shown in column D'])
    tot_row = rc.max_row
    # Raw_groups
    rg = wb.create_sheet('Raw_groups')
    rg.append(['Month', 'Group (tag_final)', 'Label on slide', 'Share of core weight (start of 12m window)', 'Group 12m rate (%)',
               'Group baseline: average 12m rate 2018-19 (%)', 'Source'])
    GROW = {}
    for mth, ml in MONTHS:
        for gk, gl in GROUPS:
            s, r = G[mth][gk]
            rg.append([dt.datetime(int(mth[:4]), int(mth[5:]), 1), gk, gl, s, r, base[gk],
                       'C_common.unit_table (BEA U20404/U20405; Oct 2026 = UMD estimate); tags 08_shock_tagging/proposed_tags.csv; '
                       'method = 10_slide2_research/code/G_baseline_attribution.py (group level)'])
            rg.cell(rg.max_row, 1).number_format = 'yyyy-mm'
            GROW[(mth, gk)] = rg.max_row
    # chart tab: Categories (s.6 adapted: column A = category, not dates)
    tc = wb.create_sheet('Categories')
    tc.append(['Category', 'Oct 2026'])
    CROW = {}
    for ln in TOP_CATS + [HOUSING]:
        r = RROW[ln]
        tc.append([f'=Raw_categories!B{r}', f'=Raw_categories!F{r}-Raw_categories!G{r}'])
        rr = tc.max_row
        EXPECT[('Categories', f'A{rr}')] = cats.at[ln, 'category']
        EXPECT[('Categories', f'B{rr}')] = cats.at[ln, 'contrib_12m'] - cats.at[ln, 'contrib_12m_2018_19_avg']
        tc.cell(rr, 2).number_format = '0.00'
        CROW[ln] = rr
    # chart tab: Shock_groups
    tg = wb.create_sheet('Shock_groups')
    tg.append(['Group'] + [ml for _, ml in MONTHS])
    SROW = {}
    for gk, gl in GROUPS:
        rr = tg.max_row + 1
        tg.cell(rr, 1, gl)
        for j, (mth, _) in enumerate(MONTHS):
            r = GROW[(mth, gk)]
            tg.cell(rr, 2 + j, f'=Raw_groups!D{r}*(Raw_groups!E{r}-Raw_groups!F{r})').number_format = '0.00'
            s, rate = G[mth][gk]
            EXPECT[('Shock_groups', tg.cell(rr, 2 + j).coordinate)] = s * (rate - base[gk])
        SROW[gk] = rr
    # Notes
    nt = wb.create_sheet('Notes')
    nt.append(['Slide element', 'Value', 'Where it comes from'])
    rows = [
        ('Title', f'{TITLE[0]}: {TITLE[1]}', 'Eli, Nov 15 (structure-stage option 1)'),
        ('Chart heading', HEADING, 'DRAFT by Claude; Eli to confirm'),
        ('Note line', NOTE, 'Eli, Nov 15 (Step 0 answer 7)'),
        ('Left panel title', PANEL_L, 'DRAFT by Claude; Eli to confirm'),
        ('Right panel title', PANEL_R, 'DRAFT by Claude; Eli to confirm'),
        ('Left chart', 'horizontal bars, red, Oct 2026* excess by BEA category: six largest + housing; BEA names',
         'Categories tab (formulas over Raw_categories). Eli: Oct only; BEA names, spoken script maps to shocks'),
        ('Right chart', 'grouped bars by shock group: Mar 2025 (dark navy) vs Oct 2026* (red); key above the plot',
         'Shock_groups tab (formulas over Raw_groups). Eli: grouped bars'),
        ('Value labels', 'Arial 11 at each bar end, 2 dp; Oct 2026 values carry an asterisk', 'Eli, Nov 15 (Step 0 answer 6)'),
        ('Y-axis (both panels)', f'{YMIN:.2f} to {YMAX:.2f} pp, step {YSTEP:.2f}, format 0.00',
         'Eli: same range both panels (pp). Floor below 0 because energy Mar 2025 = -0.01 (guide s.3 floor rule, scaled to 0.20 steps)'),
        ('Total excess Oct 2026* (spoken, not on chart)', f'=Raw_categories!F{tot_row}-Raw_categories!G{tot_row}', 'Raw_categories total row'),
        ('Source line', SOURCE, 'Eli, Nov 15 (Step 0 answer 10)'),
        ('Takeaway', TAKEAWAY, 'placeholder (guide; Eli)'),
        ('Data vintage', 'BEA U20404/U20405 Oct 29, 2026 release (through Sep 2026), saved Nov 10; Oct 2026 = UMD estimate built Nov 13 after the Oct PPI',
         '03_Data/pipelines/Price indexes/PCE/raw/; 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv'),
        ('Audit trail', 'research: 06_Audits/slide2_followups (H, G); build: 06_Audits/slide2a_build', ''),
        ('Build', 'python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2a.py" --verify', 'Rebuilds this workbook and slide 2A'),
    ]
    for row in rows:
        nt.append(list(row))
        if isinstance(row[1], str) and row[1].startswith('='):
            EXPECT[('Notes', f'B{nt.max_row}')] = cats.at[374, 'contrib_12m'] - cats.at[374, 'contrib_12m_2018_19_avg']
            nt.cell(nt.max_row, 2).number_format = '0.00'
    for ws, widths in ((tc, [34, 11]), (tg, [12, 11, 11]), (rc, [9, 40, 14, 12, 14, 14, 16, 90]), (rg, [10, 10, 12, 16, 12, 16, 90]), (nt, [40, 70, 90])):
        for c in ws[1]:
            c.font = hb
            c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.freeze_panes = 'A2'
        for k, w in enumerate(widths):
            ws.column_dimensions[chr(65 + k)].width = w
    for r in nt.iter_rows(min_row=2):
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    wb._sheets = [tc, tg, rc, rg, nt]
    wb.calculation.fullCalcOnLoad = True
    return wb


# ---------------------------------------------------------------- pptx helpers
def text_box(slide, x, y, w, h, runs, size, font, align=PP_ALIGN.CENTER, bold=False, italic=False, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    for text, color in runs:
        r = p.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.bold, r.font.italic = font, Pt(size), bold, italic
        r.font.color.rgb = rgb(color)
    return tb


def style_chart(gf, plot_x, frame, fmt_by_series, horizontal):
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = False
    plot = ch.plots[0]
    plot.gap_width = 60 if horizontal else 70
    plot.overlap = 0
    for s, (color, numfmt) in zip(plot.series, fmt_by_series):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = rgb(color)
        s.format.line.fill.background()
        s.invert_if_negative = False
        dl = s.data_labels
        dl.show_value = True
        dl.number_format = numfmt
        dl.number_format_is_linked = False
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        dl.font.name, dl.font.size, dl.font.bold = 'Arial', Pt(11), True
        dl.font.color.rgb = rgb(color)
    va = ch.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = YMIN, YMAX, YSTEP
    va.has_major_gridlines = va.has_minor_gridlines = False
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
    chart_el = cs.find(qn('c:chart'))
    cax = next(cs.iter(qn('c:catAx')))
    txpr = cax.find(qn('c:txPr'))
    if txpr is not None:
        bp = txpr.find(qn('a:bodyPr'))
        bp.set('rot', '0')
        bp.set('vert', 'horz')
    for parent in (cs, chart_el.find(qn('c:plotArea'))):
        sp = parent.find(qn('c:spPr'))
        if sp is None:
            sp = etree.SubElement(parent, qn('c:spPr'))
            if parent is cs:
                cs.remove(sp)
                chart_el.addnext(sp)
        for child in list(sp):
            sp.remove(child)
        etree.SubElement(sp, qn('a:noFill'))
        ln = etree.SubElement(sp, qn('a:ln'))
        etree.SubElement(ln, qn('a:noFill'))
    pa = chart_el.find(qn('c:plotArea'))
    lay = pa.find(qn('c:layout'))
    if lay is None:
        lay = etree.Element(qn('c:layout'))
        pa.insert(0, lay)
    for child in list(lay):
        lay.remove(child)
    ml = etree.SubElement(lay, qn('c:manualLayout'))
    fx0, fy0, fx1, fy1 = frame
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


def part_hashes(path):
    """canonical (C14N) hash for XML parts, so python-pptx re-serialization (declaration/whitespace) is not a change; raw hash otherwise"""
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        data = z.read(n)
        if n.endswith('.xml') or n.endswith('.rels'):
            data = etree.tostring(etree.fromstring(data, etree.XMLParser(remove_blank_text=True)), method='c14n')
        out[n] = hashlib.sha256(data).hexdigest()
    return out


def build_pptx(cats, G, base):
    prs = Presentation(DECK)
    assert (round(prs.slide_width / 914400, 2), round(prs.slide_height / 914400, 2)) == (13.33, 7.5)
    sldIdLst = prs.slides._sldIdLst
    # drop an existing 2A slide (rebuild); keep every other slide unchanged
    for sid, slide in zip(list(sldIdLst), list(prs.slides)):
        texts = ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        if SLIDE_MARK in texts:
            prs.part.drop_rel(sid.get(qn('r:id')))
            sldIdLst.remove(sid)
    n_before = len(prs.slides)
    blank = [l for l in prs.slide_layouts if l.name == 'Blank'][0]
    s = prs.slides.add_slide(blank)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(LIGHT)
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
    text_box(s, 0.67, 1.63, 12.00, 0.30, [(NOTE, NAVY)], 13, 'Arial')
    text_box(s, 1.27, PANEL_TOP, 5.13 - 1.27, 0.30, [(PANEL_L, NAVY)], 13, 'Arial', bold=True)      # centred over the s.5 left slot
    text_box(s, PLOT_R[0], PANEL_TOP, PLOT_R[1] - PLOT_R[0], 0.30, [(PANEL_R, NAVY)], 13, 'Arial', bold=True)
    # left: horizontal bars (first category plotted at the bottom, so feed housing first and the largest last)
    order = list(reversed(TOP_CATS + [HOUSING]))
    cd = CategoryChartData()
    cd.categories = [cats.at[ln, 'category'] for ln in order]
    cd.add_series('Oct 2026', [cats.at[ln, 'contrib_12m'] - cats.at[ln, 'contrib_12m_2018_19_avg'] for ln in order])
    fL = (0.30, PLOT_Y[0] - 0.08, PLOT_L[1] + 0.55, PLOT_Y[1] + 0.36)
    gL = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(fL[0]), Inches(fL[1]), Inches(fL[2] - fL[0]), Inches(fL[3] - fL[1]), cd)
    style_chart(gL, PLOT_L, fL, [(RED, '0.00"*";-0.00"*"')], horizontal=True)
    # right: grouped columns, Mar 2025 (dark navy) then Oct 2026* (red)
    cd = CategoryChartData()
    cd.categories = [gl for _, gl in GROUPS]
    for mth, ml in MONTHS:
        cd.add_series(ml, [G[mth][gk][0] * (G[mth][gk][1] - base[gk]) for gk, _ in GROUPS])
    fR = (PLOT_R[0] - 0.70, PLOT_Y[0] - 0.08, PLOT_R[1] + 0.10, PLOT_Y[1] + 0.36)
    gR = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(fR[0]), Inches(fR[1]), Inches(fR[2] - fR[0]), Inches(fR[3] - fR[1]), cd)
    style_chart(gR, PLOT_R, fR, [(DNAVY, '0.00;-0.00'), (RED, '0.00"*";-0.00"*"')], horizontal=False)
    # series key for the right chart (bars have no end labels): top-left inside the plot, where the bars are short
    tb = s.shapes.add_textbox(Inches(PLOT_R[0] + 0.10), Inches(PLOT_Y[0] + 0.02), Inches(2.6), Inches(0.26))
    tfk = tb.text_frame
    tfk.margin_left = tfk.margin_right = tfk.margin_top = tfk.margin_bottom = 0
    pk = tfk.paragraphs[0]
    for text, color in (('■ ', DNAVY), ('Mar 2025', DNAVY), ('    ■ ', RED), ('Oct 2026*', RED)):
        r = pk.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.bold = 'Arial', Pt(13), True
        r.font.color.rgb = rgb(color)
    text_box(s, 0.73, 6.00, 12.00, 0.47, [(SOURCE, SOURCE_GRAY)], 13, 'Arial', align=PP_ALIGN.LEFT)
    text_box(s, 0.67, 6.53, 12.00, 0.73, [(TAKEAWAY, NAVY)], 24, 'Georgia', bold=True, italic=True, anchor=MSO_ANCHOR.MIDDLE)
    prs.save(OUT_PPTX)
    return n_before


# ---------------------------------------------------------------- verification
def verify(cats, G, base, dmax, gmax, before_hashes, n_before):
    lines = [f'Inflation Slide 2A build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    os.makedirs(SCRATCH, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', SCRATCH, OUT_XLSX], check=True, capture_output=True, timeout=300)
    rec = load_workbook(os.path.join(SCRATCH, os.path.basename(OUT_XLSX)), data_only=True)
    bad = []
    for (sh, coord), v in EXPECT.items():
        got = rec[sh][coord].value
        if isinstance(v, str):
            if got != v:
                bad.append((sh, coord, v, got))
        elif not isinstance(got, (int, float)) or abs(got - v) > 1e-9:
            bad.append((sh, coord, v, got))
    lines.append(f'1. workbook formula cells: {len(EXPECT)} checked after LibreOffice recalc; mismatches: {len(bad)} {bad[:3]}')
    ok &= not bad
    lines.append(f'2. recompute vs audited research outputs: categories (H_oct_drivers_categories.csv) max diff {dmax:.1e}; '
                 f'shock groups (G_excess_path.csv, 4 dp) max diff {gmax:.1e}')
    prs = Presentation(OUT_PPTX)
    s = list(prs.slides)[-1]
    charts = [sh.chart for sh in s.shapes if sh.has_chart]
    assert len(charts) == 2
    # left chart vs Categories tab
    ws = rec['Categories']
    tab = {ws.cell(r, 1).value: ws.cell(r, 2).value for r in range(2, ws.max_row + 1)}
    pl = charts[0].plots[0]
    worst, n = 0.0, 0
    for name, v in zip(pl.categories, pl.series[0].values):
        worst = max(worst, abs(v - tab[name]))
        n += 1
    ws = rec['Shock_groups']
    hdr = [c.value for c in ws[1]]
    tabg = {ws.cell(r, 1).value: [ws.cell(r, c).value for c in range(2, ws.max_column + 1)] for r in range(2, ws.max_row + 1)}
    pr = charts[1].plots[0]
    for j, ser in enumerate(pr.series):
        assert ser.name == hdr[1 + j]
        for name, v in zip(pr.categories, ser.values):
            worst = max(worst, abs(v - tabg[name][j]))
            n += 1
    lines.append(f'3. chart points vs workbook chart tabs: {n} points; max abs diff {worst:.1e}; series order {[x.name for x in pr.series]}')
    ok &= worst < 1e-9 and n == 7 + 8
    allv = list(pl.series[0].values) + [v for ser in pr.series for v in ser.values]
    rng_ok = YMIN <= min(allv) and max(allv) <= YMAX and min(allv) > YMIN + 0.05
    lines.append(f'4. y-axis {YMIN:.2f} to {YMAX:.2f} step {YSTEP:.2f}; data min {min(allv):.4f}, max {max(allv):.4f}; fits: {rng_ok}')
    ok &= rng_ok
    xml = [etree.tostring(c._chartSpace).decode() for c in charts]
    n_ser = sum(x.count('<c:ser>') for x in xml)
    n_inv = sum(x.count('<c:invertIfNegative val="0"/>') for x in xml)
    star = all(('0.00&quot;*&quot;' in x) or ('0.00"*"' in x) for x in xml)
    flags = n_inv >= n_ser == 3 and star
    lines.append(f'5. chart XML: invertIfNegative=0 on all bar series and asterisk number format present: {flags}')
    ok &= bool(flags)
    after = part_hashes(OUT_PPTX)
    old_slides = [n_ for n_ in before_hashes if n_.startswith('ppt/slides/slide') or n_.startswith('ppt/charts/') or n_.startswith('ppt/embeddings/')]
    changed = [n_ for n_ in old_slides if n_ in after and after[n_] != before_hashes[n_]]
    missing = [n_ for n_ in old_slides if n_ not in after]
    names = zipfile.ZipFile(OUT_PPTX).namelist()
    dup = sorted({x for x in names if names.count(x) > 1})
    lines.append(f'6. deck: {len(prs.slides)} slides ({n_before} kept + 2A); earlier slide/chart/embedding parts changed: {changed or "none"}; '
                 f'missing: {missing or "none"}; duplicate zip entries: {dup or "none"}')
    ok &= not changed and not missing and not dup and len(prs.slides) == n_before + 1
    lines.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    if not ok:
        sys.exit(1)


def main(do_verify):
    R, cats, sep, G, base, dmax, gmax = load_data()
    wb = build_workbook(R, cats, sep, G, base)
    os.makedirs(os.path.dirname(OUT_XLSX), exist_ok=True)
    wb.save(OUT_XLSX)
    before = part_hashes(DECK)
    # earlier slides: remember hashes of the parts that exist before (excluding any old 2A slide, which is replaced)
    prs0 = Presentation(DECK)
    keep_parts = set()
    for slide in prs0.slides:
        texts = ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
        if SLIDE_MARK in texts:
            continue
        keep_parts.add(str(slide.part.partname).lstrip('/'))
        for rel in slide.part.rels.values():
            if 'chart' in rel.reltype:
                keep_parts.add(str(rel.target_part.partname).lstrip('/'))
                for r2 in rel.target_part.rels.values():
                    keep_parts.add(str(r2.target_part.partname).lstrip('/'))
    before = {k: v for k, v in before.items() if k in keep_parts}
    n_before = build_pptx(cats, G, base)
    print(f'wrote {REL(OUT_XLSX)} and {REL(OUT_PPTX)}')
    if do_verify:
        verify(cats, G, base, dmax, gmax, before, n_before)


if __name__ == '__main__':
    main('--verify' in sys.argv)
