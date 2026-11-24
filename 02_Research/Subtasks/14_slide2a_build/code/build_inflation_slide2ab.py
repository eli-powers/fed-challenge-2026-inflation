"""Build Inflation slides 2A (breadth) and 2B (drivers), their data workbooks, into our working deck.

Run from the project root:
    python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2ab.py"            # build
    python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2ab.py" --verify   # build + checks

Supersedes build_inflation_slide2a.py (the Nov 15 drivers-only 2A). Eli, Nov 16: slide 2 = 2A breadth, 2B drivers, 2C AI
(teammate slide, later). Design answers ("run it" = all recommendations, Nov 16):
  both:  value labels with * on Oct; units in panel titles, no axis titles; hospitals disclosed in the source line;
         no note line on 2A, one on 2B; order: slide 1, 2A, 2B, then the teammate AI slides (untouched).
  2A:    title "Inflation: Broad Since the Low, Hotter at the Top"; heading "Share of Core Spending With Prices Rising
         Faster Than 3%"; left = core (red) and supercore (dark navy) 12m breadth ex hospitals, Oct 2023-Oct 2026,
         dashed core 2018-19 average, marker at the Mar 2025 core PCE low; right = 3 rate bands, Mar 2025 (navy) vs Oct 2026* (red).
  2B:    title "Inflation: Three Shocks Now Drive the Excess"; heading "How Far Inflation Runs Above Its Pre-Pandemic
         Pace, and What's Feeding It"; left = shock groups (plain labels) Mar 2025 vs Oct 2026*, total 0.84 -> 1.50;
         right = stage 1 PPI Oct m/m contributions, horizontal bars, negative bars (energy, food) in dark navy (Eli Nov 17).
Outputs
  01_Finals/Slide data/Inflation Slide 2A.xlsx (breadth), Inflation Slide 2B.xlsx (drivers)
  01_Finals/slides/Inflation Slides (working).pptx  (2A, 2B inserted after slide 1's two versions; other slides unchanged)
"""
import datetime as dt
import hashlib
import os
import subprocess
import sys
import zipfile

import pandas as pd
from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_MARKER_STYLE, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RES = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
TAGS = os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv')
DECK = os.path.join(ROOT, '01_Finals', 'slides', 'Inflation Slides (working).pptx')
OUT_PPTX = os.environ.get('SLIDE2_PPTX') or DECK
XLSX_A = os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 2A.xlsx')
XLSX_B = os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 2B.xlsx')
SCRATCH = os.environ.get('SLIDE2_SCRATCH', '/tmp')
REPORT = os.path.join(ROOT, '02_Research', 'Subtasks', '14_slide2a_build', 'code', 'verify_report_2ab.txt')
REL = lambda p: os.path.relpath(p, ROOT)
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

NAVY, WHITE, GOLD, LIGHT = '1B2A4A', 'FFFFFF', 'F2CC6B', 'F2F2F2'
RED, DNAVY, BLACK = 'C0282D', '1B2A61', '000000'
AXIS_GRAY, LABEL_GRAY, SOURCE_GRAY = '7F7F7F', '595959', '6B6B6B'
TAKEAWAY = '[Takeaway: one sentence the team writes]'
EST = '*'

A = dict(title=('Inflation', 'Broad Since the Low, Hotter at the Top'),
         heading='Share of Core Spending With Prices Rising Faster Than 3%',
         panel_l='Spending rising faster than 3%, 12-month (%)',
         panel_r='Spending by 12-month inflation rate (%)',
         source=('Source: BEA (PCE price indexes and spending, Tables 2.4.4U/2.4.5U); UMD calculations. Share of core PCE '
                 'spending, excluding hospitals, monthly through Oct 2026*. Dashed line: core 2018–19 average '
                 '(supercore: 30.5%). *Oct 2026 = UMD estimate built from BLS CPI/PPI.'))
B = dict(title=('Inflation', 'Three Shocks Now Drive the Excess'),
         heading='How Far Inflation Runs Above Its Pre-Pandemic Pace, and What’s Feeding It',
         note='Bars: points each group adds to core inflation beyond its 2018–19 pace · *Oct 2026 = UMD estimate',
         panel_l='Excess over pre-pandemic pace, by exposure (pp)',
         panel_r='Stage 1 producer input prices, Oct: +{pub:.2f}% m/m',
         source=('Source: BEA (Tables 2.4.4U/2.4.5U); BLS PPI (stage 1 intermediate demand, WPSID51 and components, SA, prelim.); '
                 'UMD calculations and shock tags. Left: pp of core PCE 12-month inflation above each group’s 2018–19 pace. '
                 'Right: contributions to the Oct m/m change. *Oct 2026 = UMD estimate.'))
MARKS = (A['title'][1], B['title'][1])

WIN0, WIN1 = '2023-10', '2026-10'
LOW = '2025-03'                        # core PCE 12m low since 2022 (2.56%, current vintage)
HOSP = {184, 185, 186}
LS = sorted(set(cc.LEAVES_CORE) - HOSP)
BANDS = [('Below 3%', None, 3), ('3–6%', 3, 6), ('6% or more', 6, None)]
BANDS_ALT = [('Above 3%', 3, None), ('6% or more', 6, None)]   # Eli Nov 16: option 1, built as an alternate 2A for comparison
GROUPS = [('energy', 'Energy-exposed'), ('tariff', 'Tariff-exposed goods'), ('AI', 'AI-related goods'), ('untagged', 'Everything else')]
GMONTHS = [('2025-03', 'Mar 2025'), ('2026-10', 'Oct 2026')]
STAGE = [('Goods inputs (ex food & energy)', ['goods ex food & energy']), ('Trade margins', ['trade services']),
         ('Freight & warehousing', ['transport & warehousing of goods']), ('Other services', ['services less trade/TTW', 'passenger transport']),
         ('Food', ['foods']), ('Energy', ['energy'])]
PLOT_Y = (2.16, 5.60)       # 2A: no note line
PLOT_Y_B = (2.40, 5.60)     # 2B: note line
YMIN_BL = -0.10             # 2B left axis floor (Eli Nov 16): native ticks at 0.10 steps, the negative tick hidden by number format


def months(a, b):
    y, m = int(a[:4]), int(a[5:])
    out = []
    while (y, m) <= (int(b[:4]), int(b[5:])):
        out.append(f'{y}-{m:02d}')
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def mdate(m):
    return dt.datetime(int(m[:4]), int(m[5:7]), 1)


def rgb(h):
    return RGBColor.from_string(h)


# ================================================================ data
def load():
    win = months(WIN0, WIN1)
    need = sorted(set(win) | {LOW})
    sup = {l: 1 if cc.is_supercore_leaf(l) else 0 for l in LS}
    R, W = {}, {}
    for m in need:
        d = cc.unit_table('leaf', set(LS), m, 12).set_index('leaf')
        assert set(d.index) == set(LS), m
        for l in LS:
            R[(l, m)], W[(l, m)] = float(d.at[l, 'r']), float(d.at[l, 'w'])

    def share(m, pred):
        num = sum(W[(l, m)] for l in LS if pred(l, R[(l, m)]))
        return num

    breadth = {}
    for m in win:
        tw = sum(W[(l, m)] for l in LS)
        sw = sum(W[(l, m)] for l in LS if sup[l])
        breadth[m] = (100 * share(m, lambda l, r: r > 3) / tw, 100 * share(m, lambda l, r: r > 3 and sup[l]) / sw)
    bands = {}
    for m in (LOW, WIN1):
        tw = sum(W[(l, m)] for l in LS)
        bands[m] = [100 * share(m, lambda l, r, lo=lo, hi=hi: (lo is None or r > lo) and (hi is None or r <= hi)) / tw for _, lo, hi in BANDS]
        bands[('alt', m)] = [100 * share(m, lambda l, r, lo=lo, hi=hi: (lo is None or r > lo) and (hi is None or r <= hi)) / tw for _, lo, hi in BANDS_ALT]
    # cross-checks vs audited/related outputs
    F = pd.read_csv(os.path.join(RES, 'F_ex_hospital_ts.csv'))
    F = F[F.horizon == '12m'].set_index('month')
    fmax = max(max(abs(breadth[m][0] - F.at[m, 'core_ex_hosp']), abs(breadth[m][1] - F.at[m, 'supercore_ex_hosp'])) for m in win)
    assert fmax < 6e-4, fmax
    K = pd.read_csv(os.path.join(RES, 'K_rate_bands.csv'), index_col=0)
    kk = {LOW: K.loc['Mar 2025 (core PCE low)'], WIN1: K.loc['Oct 2026 est.']}
    kmax = 0
    for m in (LOW, WIN1):
        k3 = [kk[m]['below 2%'] + kk[m]['2-3%'], kk[m]['3-4%'] + kk[m]['4-6%'], kk[m]['6% or more']]
        kmax = max(kmax, max(abs(a - b) for a, b in zip(bands[m], k3)))
    assert kmax < 0.11, kmax          # K csv is rounded to 1 dp per band (sum of two rounded bands)
    # 2018-19 core average (reference line), from F (audited)
    pre = F[(F.index >= '2018-01') & (F.index <= '2019-12')]
    ref = float(pre.core_ex_hosp.mean())
    sref = float(pre.supercore_ex_hosp.mean())
    # shock groups (as the Nov 15 build)
    t = pd.read_csv(TAGS)
    t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
    tag = dict(zip(t.leaf, t.tag_final))
    core = set(cc.LEAVES_CORE)

    def grp(month):
        d = cc.unit_table('leaf', core, month, 12)
        d['tag'] = d.leaf.map(tag)
        return {gk: (d.w[d.tag == gk].sum() / d.w.sum(), (d.w * d.r)[d.tag == gk].sum() / d.w[d.tag == gk].sum()) for gk, _ in GROUPS}
    base = {gk: 0.0 for gk, _ in GROUPS}
    for y in (2018, 2019):
        for mo in range(1, 13):
            o = grp(f'{y}-{mo:02d}')
            for gk in base:
                base[gk] += o[gk][1] / 24
    G = {m: grp(m) for m, _ in GMONTHS}
    gaud = pd.read_csv(os.path.join(RES, 'G_excess_path.csv')).set_index('month')
    gmax = max(abs(G[m][gk][0] * (G[m][gk][1] - base[gk]) - gaud.at[m, f'{gk}_excess_pp']) for m, _ in GMONTHS for gk, _ in GROUPS)
    assert gmax < 6e-5, gmax
    # stage 1 (analysis E, audited in slide2_followups R1)
    E = pd.read_csv(os.path.join(RES, 'E_stage1_groups.csv'))
    E = E[E.window == 'Oct m/m'].reset_index(drop=True)
    emax = float((E.weight_share * E['pct_change'] - E.contribution_pp).abs().max())
    assert emax < 1e-3, emax
    stage = {lab: float((E.weight_share * E['pct_change'])[E.type.isin(types)].sum()) for lab, types in STAGE}
    S = pd.read_csv(os.path.join(RES, 'C_q8_ppi_stages_summary.csv')).set_index('series_id')
    pub = float(S.at['WPSID51', 'mm_Oct26'])
    return dict(win=win, R=R, W=W, sup=sup, breadth=breadth, bands=bands, ref=ref, sref=sref, G=G, base=base, E=E, stage=stage,
                pub=pub, checks=dict(F=fmax, K=kmax, G=gmax, E=emax))


# ================================================================ workbooks
EXPECT = {}     # (file, sheet, coord) -> value


def fmt_hdr(ws, widths):
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'B2'
    for k, w in enumerate(widths):
        ws.column_dimensions[get_column_letter(k + 1)].width = w


def notes_tab(wb, rows):
    nt = wb.create_sheet('Notes')
    nt.append(['Slide element', 'Value', 'Where it comes from'])
    for r in rows:
        nt.append(list(r))
    fmt_hdr(nt, [36, 80, 90])
    for r in nt.iter_rows(min_row=2):
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    return nt


def build_wb_a(D):
    wb = Workbook()
    win = D['win']
    cols = sorted(set(win) | {LOW})
    # raw tabs: 12m leaf rates and start-of-window weights (C_common), one column per month
    rr = wb.active
    rr.title = 'Raw_rates'
    rw = wb.create_sheet('Raw_weights')
    for ws, key in ((rr, 'R'), (rw, 'W')):
        ws.append(['Leaf (BEA line)', 'Supercore (1/0)'] + [mdate(m) for m in cols])
        for c in ws[1][2:]:
            c.number_format = 'yyyy-mm'
        for l in LS:
            ws.append([l, D['sup'][l]] + [D[key][(l, m)] for m in cols])
        fmt_hdr(ws, [9, 9] + [10] * len(cols))
    first, last = 2, 1 + len(LS)
    col = {m: get_column_letter(3 + j) for j, m in enumerate(cols)}
    rng = lambda tab, m: f'{tab}!${col[m]}${first}:${col[m]}${last}'
    flag = f'Raw_rates!$B${first}:$B${last}'
    # chart tab: Breadth (s.6: dates, one column per line, Reference)
    tb = wb.create_sheet('Breadth')
    tb.append(['Date', 'Core', 'Supercore', 'Reference'])
    for m in win:
        r = tb.max_row + 1
        tb.cell(r, 1, mdate(m)).number_format = 'yyyy-mm'
        tb.cell(r, 2, f"=SUMPRODUCT(({rng('Raw_rates', m)}>3)*{rng('Raw_weights', m)})/SUM({rng('Raw_weights', m)})*100").number_format = '0.0'
        tb.cell(r, 3, f"=SUMPRODUCT(({rng('Raw_rates', m)}>3)*{rng('Raw_weights', m)}*{flag})/SUMPRODUCT({rng('Raw_weights', m)}*{flag})*100").number_format = '0.0'
        tb.cell(r, 4, round(D['ref'], 4)).number_format = '0.0'
        EXPECT[('A', 'Breadth', f'B{r}')] = D['breadth'][m][0]
        EXPECT[('A', 'Breadth', f'C{r}')] = D['breadth'][m][1]
    fmt_hdr(tb, [10, 9, 10, 10])
    # chart tab: Bands
    def band_tab(name, bands, key_):
      tn = wb.create_sheet(name)
      tn.append(['Band', 'Mar 2025', 'Oct 2026'])
      for i, (lab, lo, hi) in enumerate(bands):
        r = tn.max_row + 1
        tn.cell(r, 1, lab)
        for j, m in enumerate((LOW, WIN1)):
            cond = []
            if lo is not None:
                cond.append(f"({rng('Raw_rates', m)}>{lo})")
            if hi is not None:
                cond.append(f"({rng('Raw_rates', m)}<={hi})")
            tn.cell(r, 2 + j, f"=SUMPRODUCT({'*'.join(cond)}*{rng('Raw_weights', m)})/SUM({rng('Raw_weights', m)})*100").number_format = '0.0'
            EXPECT[('A', name, tn.cell(r, 2 + j).coordinate)] = D['bands'][key_(m)][i]
      fmt_hdr(tn, [14, 10, 10])
      return tn
    tn = band_tab('Bands', BANDS, lambda m: m)
    tn2 = band_tab('Bands_alt', BANDS_ALT, lambda m: ('alt', m))
    notes_tab(wb, [
        ('Title', f"{A['title'][0]}: {A['title'][1]}", 'Claude draft, approved by Eli Nov 16 ("run it")'),
        ('Chart heading', A['heading'], 'Claude draft, approved Nov 16'),
        ('Left panel', A['panel_l'] + '; core (red) and supercore (dark navy), Oct 2023-Oct 2026', 'Breadth tab (formulas over Raw_rates/Raw_weights)'),
        ('Reference line (dashed)', f"core 2018-19 average {D['ref']:.2f}% (supercore {D['sref']:.2f}%, in the source line)",
         '10_slide2_research/outputs/F_ex_hospital_ts.csv (audited), mean of 2018-01..2019-12'),
        ('Low marker', f'Mar 2025 = core PCE 12m low since 2022 (2.56%, BEA vintage Nov 10)', '09_slide1_research/outputs/A_ts_pce_rates.csv'),
        ('Right panel', A['panel_r'] + '; Above 3% and 6% or more, Mar 2025 (dark navy) vs Oct 2026* (red); the 3-band version (Bands tab) was not chosen (Eli Nov 16)', 'Bands_alt tab'),
        ('Basket', '146 core PCE leaves (149 minus hospitals 184-186); 12m rates; start-of-window nominal weights; breadth = share of weight with rate > 3%',
         'C_common.py (09_slide1_research/code); Eli S2-E3 (hospitals excluded throughout)'),
        ('Y-axis (both panels)', '0 to 80, step 20, format 0 (deviation: guide 0.00 and step 1 are for inflation rates)', 'same units both panels (guide s.5)'),
        ('Guide deviations', '(1) right panel is a bar chart with a manual series key (guide: lines, end labels, no legend); (2) Bands tab has band names in column A, not dates (s.6); (3) y-axis in % of spending, 0-80 step 20, format 0 (s.3 whole-number/0.00 rule written for inflation rates); (4) panel titles widened 0.3 in each side to fit; (5) Low marker (dashed gray vertical + label) is an added annotation', 'Codex slide2ab_build R1-F01'),
        ('Source line', A['source'], 'approved Nov 16'),
        ('Takeaway', TAKEAWAY, 'placeholder'),
        ('Cross-checks', f"F_ex_hospital_ts max diff {D['checks']['F']:.1e}; K_rate_bands (1 dp) max diff {D['checks']['K']:.2f}", 'build script'),
        ('Build', 'python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2ab.py" --verify', ''),
    ])
    wb._sheets = [tb, tn, tn2, rr, rw, wb['Notes']]
    wb.calculation.fullCalcOnLoad = True
    return wb


def build_wb_b(D):
    wb = Workbook()
    rg = wb.active
    rg.title = 'Raw_groups'
    rg.append(['Month', 'Group (tag_final)', 'Label', 'Share of core weight (start of window)', 'Group 12m rate (%)', 'Group 2018-19 average 12m rate (%)'])
    GROW = {}
    for m, _ in GMONTHS:
        for gk, gl in GROUPS:
            s, r = D['G'][m][gk]
            rg.append([mdate(m), gk, gl, s, r, D['base'][gk]])
            rg.cell(rg.max_row, 1).number_format = 'yyyy-mm'
            GROW[(m, gk)] = rg.max_row
    fmt_hdr(rg, [10, 12, 22, 16, 14, 16])
    re_ = wb.create_sheet('Raw_stage1')
    re_.append(['Series', 'Name', 'Type', 'Weight share in stage 1', 'Oct 2026 m/m % (SA, prelim.)', 'Contribution (pp)'])
    for _, x in D['E'].iterrows():
        r = re_.max_row + 1
        re_.append([x.series, x['name'], x.type, float(x.weight_share), float(x['pct_change']), f'=D{r}*E{r}'])
        EXPECT[('B', 'Raw_stage1', f'F{r}')] = float(x.weight_share * x['pct_change'])
    fmt_hdr(re_, [14, 60, 26, 14, 14, 14])
    n = re_.max_row
    tg = wb.create_sheet('Shock_groups')
    tg.append(['Group'] + [ml for _, ml in GMONTHS])
    for gk, gl in GROUPS:
        r = tg.max_row + 1
        tg.cell(r, 1, gl)
        for j, (m, _) in enumerate(GMONTHS):
            q = GROW[(m, gk)]
            tg.cell(r, 2 + j, f'=Raw_groups!D{q}*(Raw_groups!E{q}-Raw_groups!F{q})').number_format = '0.00'
            s, rt = D['G'][m][gk]
            EXPECT[('B', 'Shock_groups', tg.cell(r, 2 + j).coordinate)] = s * (rt - D['base'][gk])
    r = tg.max_row + 1
    tg.cell(r, 1, 'Total (shown as text on the slide)')
    for j in range(2):
        L = get_column_letter(2 + j)
        tg.cell(r, 2 + j, f'=SUM({L}2:{L}{r - 1})').number_format = '0.00'
        m = GMONTHS[j][0]
        EXPECT[('B', 'Shock_groups', f'{L}{r}')] = sum(D['G'][m][gk][0] * (D['G'][m][gk][1] - D['base'][gk]) for gk, _ in GROUPS)
    fmt_hdr(tg, [34, 11, 11])
    ts = wb.create_sheet('Stage1')
    ts.append(['Component', 'Oct 2026'])
    for lab, types in STAGE:
        r = ts.max_row + 1
        ts.cell(r, 1, lab)
        ts.cell(r, 2, '=' + '+'.join(f'SUMIF(Raw_stage1!$C$2:$C${n},"{t_}",Raw_stage1!$F$2:$F${n})' for t_ in types)).number_format = '+0.00;-0.00'
        EXPECT[('B', 'Stage1', f'B{r}')] = D['stage'][lab]
    r = ts.max_row + 1
    ts.cell(r, 1, 'Sum of components')
    ts.cell(r, 2, f'=SUM(B2:B{r - 1})').number_format = '+0.00'
    EXPECT[('B', 'Stage1', f'B{r}')] = sum(D['stage'].values())
    ts.cell(r + 1, 1, 'Published stage 1 m/m (WPSID51, SA)')
    ts.cell(r + 1, 2, D['pub']).number_format = '+0.00'
    fmt_hdr(ts, [34, 11])
    notes_tab(wb, [
        ('Title', f"{B['title'][0]}: {B['title'][1]}", 'Eli (kept Nov 16; qualifier spoken, J01)'),
        ('Chart heading', B['heading'], 'Claude draft, approved Nov 16'),
        ('Note line', B['note'], 'approved Nov 16'),
        ('Left panel', B['panel_l'] + '; Mar 2025 (dark navy) vs Oct 2026* (red); total 0.84 -> 1.50 as text', 'Shock_groups tab; method = 10_slide2_research/code/G_baseline_attribution.py (group level), audited'),
        ('Right panel', B['panel_r'].format(pub=D['pub']) + '; horizontal bars; negative bars (energy, food) dark navy, positive red (Eli Nov 17); sum vs published', 'Stage1 tab over Raw_stage1 (10_slide2_research/outputs/E_stage1_groups.csv; BLS Dec 2025 RI updated; audited slide2_followups R1)'),
        ('Other services', 'services less trade/transport/warehousing + passenger transport', 'grouping for readability'),
        ('Y-axes', 'left -0.10 to 0.80 pp, step 0.10, negative tick label hidden (format 0.00;;0.00) so the axis reads 0.00-0.80 (Eli Nov 16: no negative range; small dip below zero labelled); right -0.40 to 0.60 pp step 0.20; format 0.00 (different units: left pp of core PCE, right pp of stage 1 PPI m/m)', ''),
        ('Guide deviations', '(1) both panels are bar charts with value labels; left uses a manual series key (guide: lines, end labels, no legend); (2) chart tabs have group/component names in column A, not dates (s.6); (3) right plot at x 8.95-11.27 instead of 7.40-11.27 (s.5) to make room for category names, so the two plots differ in width; (4) axes in pp with 0.20 steps (left -0.20 to 0.80, right -0.40 to 0.60), different units per panel; (5) negative bars (energy, food) drawn as an overlaid second series (dark navy) so colour marks sign (Eli Nov 17); (6) right panel total in the panel title; (7) left axis step 0.10 with the -0.10 tick label hidden; (8) left total shown as an end label right of the plot (navy Mar 2025, red Oct 2026*)', 'Codex slide2ab_build R1-F01'),
        ('Source line', B['source'], 'approved Nov 16'),
        ('Takeaway', TAKEAWAY, 'placeholder'),
        ('Cross-checks', f"G_excess_path (4 dp) max diff {D['checks']['G']:.1e}; E contributions max diff {D['checks']['E']:.1e}", 'build script'),
        ('Build', 'python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2ab.py" --verify', ''),
    ])
    wb._sheets = [tg, ts, rg, re_, wb['Notes']]
    wb.calculation.fullCalcOnLoad = True
    return wb


# ================================================================ pptx helpers
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


def frame_fix(ch, plot_x, plot_y, frame):
    cs = ch._chartSpace
    chart_el = cs.find(qn('c:chart'))
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
                     ('c:x', (plot_x[0] - fx0) / W), ('c:y', (plot_y[0] - fy0) / H),
                     ('c:w', (plot_x[1] - plot_x[0]) / W), ('c:h', (plot_y[1] - plot_y[0]) / H)):
        etree.SubElement(ml, qn(tag)).set('val', str(val))
    atd = chart_el.find(qn('c:autoTitleDeleted'))
    if atd is None:
        atd = etree.Element(qn('c:autoTitleDeleted'))
        chart_el.insert(0, atd)
    atd.set('val', '1')
    cax = next(cs.iter(qn('c:catAx')))
    txpr = cax.find(qn('c:txPr'))
    if txpr is not None:
        bp = txpr.find(qn('a:bodyPr'))
        bp.set('rot', '0')
        bp.set('vert', 'horz')
        bp.set('wrap', 'none' if ch.chart_type == XL_CHART_TYPE.LINE else 'square')
    return cs


def axes(ch, ymin, ymax, step, fmt, cat_size=11):
    va = ch.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = ymin, ymax, step
    va.has_major_gridlines = va.has_minor_gridlines = False
    va.tick_labels.number_format = fmt
    va.tick_labels.number_format_is_linked = False
    va.tick_labels.font.name, va.tick_labels.font.size = 'Arial', Pt(12)
    va.tick_labels.font.color.rgb = rgb(LABEL_GRAY)
    va.format.line.fill.background()
    va.major_tick_mark = XL_TICK_MARK.NONE
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.tick_labels.font.name, ca.tick_labels.font.size = 'Arial', Pt(cat_size)
    ca.tick_labels.font.color.rgb = rgb(LABEL_GRAY)
    ca.format.line.color.rgb = rgb(AXIS_GRAY)
    ca.format.line.width = Pt(1)
    ca.major_tick_mark = XL_TICK_MARK.NONE
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW


def bar_chart(slide, kind, cats, series, plot_x, plot_y, frame, ymin, ymax, step, fmt, label_fmts, colors, gap=70, point_colors=None):
    cd = CategoryChartData()
    cd.categories = cats
    for name, vals in series:
        cd.add_series(name, vals)
    fx0, fy0, fx1, fy1 = frame
    gf = slide.shapes.add_chart(kind, Inches(fx0), Inches(fy0), Inches(fx1 - fx0), Inches(fy1 - fy0), cd)
    ch = gf.chart
    ch.has_title = False
    ch.has_legend = False
    pl = ch.plots[0]
    pl.gap_width, pl.overlap = gap, 0
    for k, (s, color, lf) in enumerate(zip(pl.series, colors, label_fmts)):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = rgb(color)
        s.format.line.fill.background()
        s.invert_if_negative = False
        dl = s.data_labels
        dl.show_value = True
        dl.number_format, dl.number_format_is_linked = lf, False
        dl.position = XL_LABEL_POSITION.OUTSIDE_END
        dl.font.name, dl.font.size, dl.font.bold = 'Arial', Pt(11), True
        dl.font.color.rgb = rgb(color)
        if point_colors and k == 0:
            for i, pc in point_colors.items():
                pt = s.points[i]
                pt.format.fill.solid()
                pt.format.fill.fore_color.rgb = rgb(pc)
                pt.data_label.font.name, pt.data_label.font.size, pt.data_label.font.bold = 'Arial', Pt(11), True
                pt.data_label.font.color.rgb = rgb(pc)
                pt.data_label.number_format, pt.data_label.number_format_is_linked = lf, False
                pt.data_label.position = XL_LABEL_POSITION.OUTSIDE_END
    axes(ch, ymin, ymax, step, fmt)
    frame_fix(ch, plot_x, plot_y, frame)
    return gf


def key(slide, x, y, items, size=12):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(3.4), Inches(0.26))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    for k, (text, color) in enumerate(items):
        for t_ in (('    ' if k else '') + '■ ', text):
            r = p.add_run()
            r.text = t_
            r.font.name, r.font.size, r.font.bold = 'Arial', Pt(size), True
            r.font.color.rgb = rgb(color)


def base_slide(prs, spec, note=None):
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
    for text, color in ((spec['title'][0], WHITE), (':', WHITE), (' ' + spec['title'][1], GOLD)):
        r = p.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.bold = 'Georgia', Pt(32), False
        r.font.color.rgb = rgb(color)
    text_box(s, 0.67, 1.09, 12.00, 0.61, [(spec['heading'], NAVY)], 21, 'Georgia', bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if note:
        text_box(s, 0.67, 1.63, 12.00, 0.30, [(note, NAVY)], 13, 'Arial')
    text_box(s, 0.73, 6.00, 12.00, 0.47, [(spec['source'], SOURCE_GRAY)], 12, 'Arial', align=PP_ALIGN.LEFT)
    text_box(s, 0.67, 6.62, 12.00, 0.68, [(TAKEAWAY, NAVY)], 24, 'Georgia', bold=True, italic=True, anchor=MSO_ANCHOR.MIDDLE)
    return s


def slide_2a(prs, D, variant='bands'):
    s = base_slide(prs, A)
    PL, PR = (1.27, 5.13), (7.40, 11.27)
    for (x0, x1), t in ((PL, A['panel_l']), (PR, A['panel_r'])):
        text_box(s, x0 - 0.3, 1.80, x1 - x0 + 0.6, 0.30, [(t, NAVY)], 13, 'Arial', bold=True)
    win = D['win']
    YMAX = 80
    # left: lines
    cd = CategoryChartData()
    cd.categories = [m if m[5:] in ('01', '07') else ' ' for m in win]
    cd.add_series('Core', [D['breadth'][m][0] for m in win])
    cd.add_series('Supercore', [D['breadth'][m][1] for m in win])
    cd.add_series('Reference', [round(D['ref'], 4)] * len(win))
    fr = (PL[0] - 0.62, PLOT_Y[0] - 0.08, PL[1] + 0.08, PLOT_Y[1] + 0.36)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(fr[0]), Inches(fr[1]), Inches(fr[2] - fr[0]), Inches(fr[3] - fr[1]), cd)
    ch = gf.chart
    ch.has_title = ch.has_legend = False
    for se, color, w_, dash in zip(ch.plots[0].series, (RED, DNAVY, BLACK), (3, 3, 2.25), (None, None, MSO_LINE_DASH_STYLE.DASH)):
        se.format.line.color.rgb = rgb(color)
        se.format.line.width = Pt(w_)
        if dash:
            se.format.line.dash_style = dash
        se.marker.style = XL_MARKER_STYLE.NONE
        se.smooth = False
    axes(ch, 0, YMAX, 20, '0')
    cs = frame_fix(ch, PL, PLOT_Y, fr)
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
    # end labels
    yof = lambda v: PLOT_Y[1] - v / YMAX * (PLOT_Y[1] - PLOT_Y[0])
    labs = [('Core', D['breadth'][win[-1]][0], RED), ('Supercore', D['breadth'][win[-1]][1], DNAVY)]
    ys = [yof(v) for _, v, _ in labs]
    h = 0.44
    if abs(ys[0] - ys[1]) < h + 0.02:
        mid = (ys[0] + ys[1]) / 2
        hi_first = ys[0] > ys[1]       # larger y = lower on the slide
        ys = [mid + (h + 0.02) / 2, mid - (h + 0.02) / 2] if hi_first else [mid - (h + 0.02) / 2, mid + (h + 0.02) / 2]
    for (n_, v, c), y in zip(labs, ys):
        text_box(s, PL[1] + 0.16, y - h / 2, 1.20, h, [[(n_, c)], [(f'{v:.1f}%{EST}', c)]], 13, 'Arial', align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    # low marker: thin dashed vertical at Mar 2025 + small label at the top of the plot
    i = win.index(LOW)
    x = PL[0] + i / (len(win) - 1) * (PL[1] - PL[0])
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(PLOT_Y[0] + 0.30), Inches(x), Inches(PLOT_Y[1]))
    ln.line.color.rgb = rgb(AXIS_GRAY)
    ln.line.width = Pt(1)
    ln.line.dash_style = MSO_LINE_DASH_STYLE.SQUARE_DOT
    text_box(s, x - 0.9, PLOT_Y[0] + 0.02, 1.8, 0.26, [('Core PCE low, Mar 2025', LABEL_GRAY)], 10, 'Arial')
    # right: bands
    frR = (PR[0] - 0.62, PLOT_Y[0] - 0.08, PR[1] + 0.10, PLOT_Y[1] + 0.36)
    bands, k = (BANDS, lambda m: m) if variant == 'bands' else (BANDS_ALT, lambda m: ('alt', m))
    bar_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [b[0] for b in bands],
              [('Mar 2025', D['bands'][k(LOW)]), ('Oct 2026', D['bands'][k(WIN1)])], PR, PLOT_Y, frR, 0, YMAX, 20, '0',
              ['0.0', '0.0"*"'], [DNAVY, RED], gap=90 if variant == 'alt' else 70)
    # Eli Nov 16: option 1 (Above 3% / 6% or more) chosen; the three-band version is no longer built
    key(s, PR[0] + 1.30, PLOT_Y[0] + 0.02, [('Mar 2025', DNAVY), ('Oct 2026*', RED)])
    return s


def slide_2b(prs, D):
    s = base_slide(prs, B, note=B['note'])
    PL, PR = (1.27, 5.13), (8.95, 11.27)
    text_box(s, PL[0] - 0.3, 2.07, PL[1] - PL[0] + 0.6, 0.30, [(B['panel_l'], NAVY)], 13, 'Arial', bold=True)
    text_box(s, 7.10, 2.07, 11.27 - 7.10, 0.30, [(B['panel_r'].format(pub=D['pub']), NAVY)], 13, 'Arial', bold=True)
    vals = {m: [D['G'][m][gk][0] * (D['G'][m][gk][1] - D['base'][gk]) for gk, _ in GROUPS] for m, _ in GMONTHS}
    frL = (PL[0] - 0.70, PLOT_Y_B[0] - 0.08, PL[1] + 0.10, PLOT_Y_B[1] + 0.40)
    gfL = bar_chart(s, XL_CHART_TYPE.COLUMN_CLUSTERED, [gl for _, gl in GROUPS], [(ml, vals[m]) for m, ml in GMONTHS],
              PL, PLOT_Y_B, frL, YMIN_BL, 0.80, 0.10, '0.00;;0.00', ['0.00;-0.00', '0.00"*";-0.00"*"'], [DNAVY, RED])
    # Eli Nov 16: no negative axis range; a small dip below zero is fine. Native ticks would start at the axis minimum
    # (-0.08, 0.12, ...), so the value-axis labels are hidden and drawn as text at 0.00..0.80 in the guide's axis style.
    yb = lambda v: PLOT_Y_B[1] - (v - YMIN_BL) / (0.80 - YMIN_BL) * (PLOT_Y_B[1] - PLOT_Y_B[0])
    cax = next(gfL.chart._chartSpace.iter(qn('c:catAx')))
    for tg_ in ('c:tickLblSkip',):
        el = cax.find(qn(tg_))
        if el is not None:
            cax.remove(el)
        el = etree.Element(qn(tg_))
        el.set('val', '1')
        ext = cax.find(qn('c:extLst'))
        (ext.addprevious(el) if ext is not None else cax.append(el))
    key(s, PL[0] + 0.12, PLOT_Y_B[0] + 0.02, [('Mar 2025', DNAVY), ('Oct 2026*', RED)])
    t0, t1 = sum(vals['2025-03']), sum(vals['2026-10'])
    # total as an end label right of the plot, beside the "Everything else" bars (Eli Nov 16)
    text_box(s, PL[1] + 0.16, yb(0.30) - 0.25, 1.70, 0.50, [[('Total', NAVY)], [(f'{t0:.2f}', DNAVY), (' → ', NAVY), (f'{t1:.2f}{EST}', RED)]],
             13, 'Arial', align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    # right: stage 1 horizontal bars (first category at the bottom -> feed reversed)
    labs = [lab for lab, _ in STAGE]
    order = list(reversed(labs))
    frR = (7.05, PLOT_Y_B[0] - 0.08, PR[1] + 0.55, PLOT_Y_B[1] + 0.36)
    gf = bar_chart(s, XL_CHART_TYPE.BAR_CLUSTERED, order,
                   [('Oct 2026', [D['stage'][l] if D['stage'][l] >= 0 else None for l in order]),
                    ('Negative', [D['stage'][l] if D['stage'][l] < 0 else None for l in order])],
                   PR, PLOT_Y_B, frR, -0.40, 0.60, 0.20, '0.00', ['+0.00;-0.00', '+0.00;-0.00'], [RED, DNAVY], gap=55)
    gf.chart.plots[0].overlap = 100       # negative bars drawn as their own series in the same slot, so they can be dark navy
    return s, (t0, t1)


def part_hashes(path):
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        data = z.read(n)
        if n.endswith('.xml') or n.endswith('.rels'):
            data = etree.tostring(etree.fromstring(data, etree.XMLParser(remove_blank_text=True)), method='c14n')
        out[n] = hashlib.sha256(data).hexdigest()
    return out


def slide_sigs(path):
    """content signature of every slide that is not 2A/2B, in deck order: C14N hash of the slide XML and of each chart part
    and embedded workbook it uses. Independent of part names (python-pptx renumbers slide parts whenever prs.slides is read)."""
    prs = Presentation(path)
    c14 = lambda b: hashlib.sha256(etree.tostring(etree.fromstring(b, etree.XMLParser(remove_blank_text=True)), method='c14n')).hexdigest()
    out = []
    for slide in prs.slides:
        if is_ours(slide):
            continue
        sig = [c14(etree.tostring(slide._element))]
        for rel in sorted(slide.part.rels.values(), key=lambda r: r.rId):
            if 'chart' in rel.reltype:
                sig.append(c14(rel.target_part.blob))
                for r2 in rel.target_part.rels.values():
                    sig.append(hashlib.sha256(r2.target_part.blob).hexdigest())
        out.append(tuple(sig))
    return out


def is_ours(slide):
    texts = ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame)
    return any(m in texts for m in MARKS)


def keep_part_names(prs):
    keep = set()
    for slide in prs.slides:
        if is_ours(slide):
            continue
        keep.add(str(slide.part.partname).lstrip('/'))
        for rel in slide.part.rels.values():
            if 'chart' in rel.reltype or 'image' in rel.reltype:
                keep.add(str(rel.target_part.partname).lstrip('/'))
                for r2 in rel.target_part.rels.values():
                    keep.add(str(r2.target_part.partname).lstrip('/'))
    return keep


def build_pptx(D):
    prs = Presentation(DECK)
    lst = prs.slides._sldIdLst
    for sid, slide in zip(list(lst), list(prs.slides)):
        if is_ours(slide):
            prs.part.drop_rel(sid.get(qn('r:id')))
            lst.remove(sid)
    # position: after the last slide-1 version ("Firming Again")
    titles = [' '.join(sh.text_frame.text for sh in sl.shapes if sh.has_text_frame) for sl in prs.slides]
    pos = max(i for i, t in enumerate(titles) if 'Firming Again After a Summer Lull' in t) + 1
    others = [str(sl.part.partname) for sl in prs.slides]
    from pptx.opc.packuri import PackURI
    used = {str(pt.partname) for pt in prs.part.package.iter_parts()}

    def unique_name(slide):        # python-pptx names a new slide slide<len+1>.xml, which can collide with a kept slide
        k = 100
        while f'/ppt/slides/slide{k}.xml' in used:
            k += 1
        slide.part.partname = PackURI(f'/ppt/slides/slide{k}.xml')
        used.add(f'/ppt/slides/slide{k}.xml')
    unique_name(slide_2a(prs, D, variant='alt'))
    sb, totals = slide_2b(prs, D)
    unique_name(sb)
    ids = list(lst)
    new = ids[-2:]
    for el in new:
        lst.remove(el)
    for k, el in enumerate(new):
        lst.insert(pos + k, el)
    prs.save(OUT_PPTX)
    return pos, others, totals


# ================================================================ verify
def recalc(path):
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', SCRATCH, path], check=True, capture_output=True, timeout=300)
    return load_workbook(os.path.join(SCRATCH, os.path.basename(path)), data_only=True)


def verify(D, before, pos, totals):
    L = [f'Inflation slides 2A/2B build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    os.makedirs(SCRATCH, exist_ok=True)
    rec = {'A': recalc(XLSX_A), 'B': recalc(XLSX_B)}
    bad = [(k, v, rec[k[0]][k[1]][k[2]].value) for k, v in EXPECT.items()
           if not isinstance(rec[k[0]][k[1]][k[2]].value, (int, float)) or abs(rec[k[0]][k[1]][k[2]].value - v) > 1e-9]
    L.append(f'1. workbook formula cells (2A + 2B): {len(EXPECT)} checked after LibreOffice recalc; mismatches: {len(bad)} {bad[:3]}')
    ok &= not bad
    c = D['checks']
    L.append(f'2. cross-checks: breadth vs F_ex_hospital_ts (audited) {c["F"]:.1e}; bands vs K_rate_bands (1 dp) {c["K"]:.2f}; '
             f'groups vs G_excess_path (4 dp) {c["G"]:.1e}; stage 1 weight x pct vs E csv {c["E"]:.1e}')
    prs = Presentation(OUT_PPTX)
    sl = list(prs.slides)
    sa, sb = sl[pos], sl[pos + 1]
    assert A['title'][1] in ' '.join(sh.text_frame.text for sh in sa.shapes if sh.has_text_frame)
    assert B['title'][1] in ' '.join(sh.text_frame.text for sh in sb.shapes if sh.has_text_frame)
    worst, n = 0.0, 0
    # 2A left vs Breadth tab
    chA = [sh.chart for sh in sa.shapes if sh.has_chart]
    wsb = rec['A']['Breadth']
    hdr = [x.value for x in wsb[1]]
    for se in chA[0].plots[0].series:
        colv = [wsb.cell(r, hdr.index(se.name) + 1).value for r in range(2, wsb.max_row + 1)]
        for a, b in zip(se.values, colv):
            worst, n = max(worst, abs(a - b)), n + 1
    cats = list(chA[0].plots[0].categories)
    dates = [wsb.cell(r, 1).value.strftime('%Y-%m') for r in range(2, wsb.max_row + 1)]
    assert cats == [d if d[5:] in ('01', '07') else ' ' for d in dates]
    wsa = rec['A']['Bands_alt']
    for j, se in enumerate(chA[1].plots[0].series):
        for i, v in enumerate(se.values):
            worst, n = max(worst, abs(v - wsa.cell(2 + i, 2 + j).value)), n + 1
    assert abs(D['bands'][('alt', WIN1)][0] - D['breadth'][WIN1][0]) < 1e-9, 'Above 3% (Oct) must equal the left-chart core endpoint'
    chB = [sh.chart for sh in sb.shapes if sh.has_chart]
    wsg = rec['B']['Shock_groups']
    for j, se in enumerate(chB[0].plots[0].series):
        for i, v in enumerate(se.values):
            worst, n = max(worst, abs(v - wsg.cell(2 + i, 2 + j).value)), n + 1
    wss = rec['B']['Stage1']
    tab = {wss.cell(r, 1).value: wss.cell(r, 2).value for r in range(2, 2 + len(STAGE))}
    sers = chB[1].plots[0].series
    for k_, name in enumerate(chB[1].plots[0].categories):
        v = sers[0].values[k_] if sers[0].values[k_] is not None else sers[1].values[k_]
        assert (sers[0].values[k_] is None) != (sers[1].values[k_] is None)
        worst, n = max(worst, abs(v - tab[name])), n + 1
    L.append(f'3. chart points vs workbook chart tabs: {n} points; max abs diff {worst:.1e}')
    ok &= worst < 1e-9 and n == 37 * 3 + 4 + 8 + 6
    allA = [v for m in D['win'] for v in D['breadth'][m]] + [v for m in (LOW, WIN1) for v in D['bands'][('alt', m)]]
    gv = [v for se in chB[0].plots[0].series for v in se.values]
    sv = list(D['stage'].values())
    rng = (0 <= min(allA) and max(allA) <= 80, YMIN_BL < min(gv) and max(gv) <= 0.80, -0.40 < min(sv) and max(sv) <= 0.60)
    L.append(f'4. axis ranges fit: 2A 0-80 (data {min(allA):.1f}-{max(allA):.1f}) {rng[0]}; 2B left {YMIN_BL:.2f}..0.80 (labels 0.00-0.80) ({min(gv):.3f}..{max(gv):.3f}) {rng[1]}; '
             f'2B right -0.40..0.60 ({min(sv):.3f}..{max(sv):.3f}) {rng[2]}; totals {totals[0]:.2f} -> {totals[1]:.2f}; stage sum {sum(sv):.3f} vs published {D["pub"]:.3f}')
    ok &= all(rng) and abs(sum(sv) - D['pub']) < 0.02
    xml = [etree.tostring(cc_._chartSpace).decode() for cc_ in chA + chB]
    nbar = sum(x.count('<c:ser>') for x in xml[1:])   # 2 + 2 + 2 bar series
    ninv = sum(x.count('<c:invertIfNegative val="0"/>') for x in xml[1:])
    smooth = xml[0].count('<c:smooth val="0"/>') >= 3
    L.append(f'5. chart XML: line smooth=0 on all 3 series: {smooth}; bar invertIfNegative=0 on {ninv}/{nbar} bar series')
    ok &= smooth and ninv >= nbar
    after = slide_sigs(OUT_PPTX)
    changed = [] if after == before else [f'{len(before)} slides before vs {len(after)} after; first differing index {next((i for i, (x, y) in enumerate(zip(before, after)) if x != y), None)}']
    missing = []
    names = zipfile.ZipFile(OUT_PPTX).namelist()
    dup = sorted({x for x in names if names.count(x) > 1})
    order = [' '.join(sh.text_frame.text for sh in s_.shapes if sh.has_text_frame)[:45] for s_ in sl]
    L.append(f'6. deck: {len(sl)} slides; order: {order}; other slides (content signature, C14N, incl. charts) changed: {changed or "none"}; duplicate zip entries: {dup or "none"}')
    ok &= not changed and not missing and not dup
    L.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    if not ok:
        sys.exit(1)


def main(do_verify):
    D = load()
    for path, wb in ((XLSX_A, build_wb_a(D)), (XLSX_B, build_wb_b(D))):
        wb.save(path)
    before = slide_sigs(DECK)
    pos, others, totals = build_pptx(D)
    print(f'wrote {REL(XLSX_A)}, {REL(XLSX_B)}, {REL(OUT_PPTX)} (2A at position {pos + 1})')
    if do_verify:
        verify(D, before, pos, totals)


if __name__ == '__main__':
    main('--verify' in sys.argv)
