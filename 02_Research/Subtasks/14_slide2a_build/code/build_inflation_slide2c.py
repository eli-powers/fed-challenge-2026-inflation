"""Build Inflation slide 2C (AI: upstream producer prices and consumer tech prices) and its data workbook.

Run from the project root:
    python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2c.py" --verify

Eli, Nov 16: flow 2A breadth -> 2B intensity + stage 1 PPI -> 2C AI (tight: AI prices only), built on the teammate's
"AI Buildout: Tech Costs Are Rising" slide plus the audited AI PPI basket (analysis J, 06_Audits/slide2_ai_ppi, converged R1).
The teammate's slides stay in the deck untouched for comparison.
Left  = AI-related upstream PPIs (BLS industry indexes, NSA), 12-month % change, Oct 2026 (prelim.) vs each series' 2018-19
        average; storage devices (+80%) and printed circuit assemblies (+151%, lumpy) are left off the chart for scale (verbal).
Right = PCE prices for software (BEA line 50) and personal computers (line 49), 12-month %, Oct 2023 - Oct 2026 (same window
        as slides 1 and 2A); Oct 2026 = UMD estimate. Teammate's chart concept, with the Oct estimate and the 0% reference.
Writes 01_Finals/Slide data/Inflation Slide 2C.xlsx; inserts slide 2C after slide 2B in the working deck.
"""
import datetime as dt
import glob
import json
import math
import os
import sys

import pandas as pd
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
sys.path.insert(0, HERE)
import build_inflation_slide2ab as b2  # noqa: E402  (helpers, constants, C_common)

ROOT, cc, rgb, text_box = b2.ROOT, b2.cc, b2.rgb, b2.text_box
NAVY, RED, DNAVY, BLACK, LABEL_GRAY = b2.NAVY, b2.RED, b2.DNAVY, b2.BLACK, b2.LABEL_GRAY
RAW = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_ai_basket_2026-11-16')
JSUM = os.path.join(b2.RES, 'J_ai_ppi_summary.csv')
XLSX_C = os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 2C.xlsx')
DECK = b2.DECK
REPORT = os.path.join(HERE, 'verify_report_2c.txt')

C = dict(title=('Inflation', 'Tech Prices During the AI Buildout'),                         # Eli, hand-edited in the deck Nov 16 09:23
         heading='Prices Tied to the AI Buildout: Producer Inputs and Consumer Tech',      # DRAFT
         note='Left: producer prices, 12-month change · Right: consumer prices, 12-month change · *Oct 2026 = UMD estimate',
         panel_l='AI-related producer prices, Oct 2026 vs 2018–19 (%)',
         panel_r='Consumer software and computer prices (%)',
         source=('Source: BLS PPI industry indexes (NSA; Oct 2026 preliminary); BEA PCE price indexes (Table 2.4.4U, lines 49–50); '
                 'UMD calculations. 12-month % change; left bars: Oct 2026 vs 2018–19 average. Dashed line: 0%. '
                 '*Oct 2026 = UMD estimate built from BLS CPI/PPI.'))
MARK = C['title'][1]
OLD_MARKS = ('AI Is Lifting Tech Prices',)   # earlier draft title
PPI = [('PCU33441-33441-', 'Electronic components (incl. chips)'), ('PCU3341--3341--', 'Computers & peripherals'),
       ('PCU335313335313', 'Switchgear (power equipment)'), ('PCU541330541330202', 'Grid engineering services'),
       ('PCU51321051321050502', 'Application software publishing'), ('PCU334413334413', 'Semiconductors & related devices')]
LEAVES = [(50, 'Software'), (49, 'Computers')]
WIN = b2.months('2023-10', '2026-10')
PLOT_Y = (2.40, 5.60)


def load():
    v = {}
    for f in glob.glob(os.path.join(RAW, '*.json')):
        for s in json.load(open(f))['Results']['series']:
            for o in s['data']:
                if o['period'].startswith('M') and o['period'] != 'M13':
                    v[(s['seriesID'], f"{o['year']}-{o['period'][1:]}")] = float(o['value'])
    ppm = b2.months('2017-01', '2026-10')
    yoy = lambda sid, m: (v[(sid, m)] / v[(sid, ppm[ppm.index(m) - 12])] - 1) * 100
    pre = [m for m in ppm if '2018-01' <= m <= '2019-12']
    bars = {sid: (sum(yoy(sid, m) for m in pre) / len(pre), yoy(sid, '2026-10')) for sid, _ in PPI}
    J = pd.read_csv(JSUM).set_index('series_id')
    jmax = max(max(abs(bars[sid][0] - J.at[sid, 'yoy_avg_2018_19']), abs(bars[sid][1] - J.at[sid, 'yoy_last'])) for sid, _ in PPI)
    assert jmax < 0.006, jmax          # J summary is rounded to 2 dp
    allm = b2.months('2022-10', '2026-10')
    lv = {(l, m): float(cc.index_level(l, m, 'leaf')) for l, _ in LEAVES for m in allm}
    r12 = {(l, m): (lv[(l, m)] / lv[(l, allm[allm.index(m) - 12])] - 1) * 100 for l, _ in LEAVES for m in WIN}
    F = pd.read_csv(os.path.join(b2.RES, 'F_attrib_top_leaves.csv'))
    fx = F[(F.horizon == '12m') & F.leaf.isin([49, 50])].set_index(['period', 'leaf']).rate_pct
    fmax = max(abs(r12[(l, p)] - fx.loc[(p, l)]) for l, _ in LEAVES for p in ('2026-09', '2026-10'))
    assert fmax < 0.006, fmax
    return dict(v=v, ppm=ppm, bars=bars, lv=lv, allm=allm, r12=r12, checks=dict(J=jmax, F=fmax))


EXPECT = {}


def build_wb(D):
    wb = Workbook()
    rp = wb.active
    rp.title = 'Raw_PPI'
    rp.append(['Month'] + [sid for sid, _ in PPI])
    PR = {}
    for m in D['ppm']:
        rp.append([b2.mdate(m)] + [D['v'][(sid, m)] for sid, _ in PPI])
        rp.cell(rp.max_row, 1).number_format = 'yyyy-mm'
        PR[m] = rp.max_row
    b2.fmt_hdr(rp, [10] + [16] * len(PPI))
    rl = wb.create_sheet('Raw_PCE')
    rl.append(['Month'] + [f'BEA line {l} ({n}) index, 2017=100' for l, n in LEAVES] + ['Status'])
    LR = {}
    for m in D['allm']:
        rl.append([b2.mdate(m)] + [D['lv'][(l, m)] for l, _ in LEAVES] + ['UMD estimate' if m == '2026-10' else 'BEA published'])
        rl.cell(rl.max_row, 1).number_format = 'yyyy-mm'
        LR[m] = rl.max_row
    b2.fmt_hdr(rl, [10, 22, 22, 14])
    tb = wb.create_sheet('PPI_bars')
    tb.append(['Item', '2018–19 average', 'Oct 2026'])
    pre = [m for m in D['ppm'] if '2018-01' <= m <= '2019-12']
    for j, (sid, lab) in enumerate(PPI):
        col = get_column_letter(2 + j)
        r = tb.max_row + 1
        tb.cell(r, 1, lab)
        terms = ','.join(f'Raw_PPI!{col}{PR[m]}/Raw_PPI!{col}{PR[m] - 12}' for m in pre)
        tb.cell(r, 2, f'=(AVERAGE({terms})-1)*100').number_format = '0.0'
        tb.cell(r, 3, f"=(Raw_PPI!{col}{PR['2026-10']}/Raw_PPI!{col}{PR['2026-10'] - 12}-1)*100").number_format = '0.0'
        EXPECT[('PPI_bars', f'B{r}')] = D['bars'][sid][0]
        EXPECT[('PPI_bars', f'C{r}')] = D['bars'][sid][1]
    b2.fmt_hdr(tb, [36, 14, 12])
    tc = wb.create_sheet('Consumer_tech')
    tc.append(['Date'] + [n for _, n in LEAVES] + ['Reference'])
    for m in WIN:
        r = tc.max_row + 1
        tc.cell(r, 1, b2.mdate(m)).number_format = 'yyyy-mm'
        for j, (l, _) in enumerate(LEAVES):
            col = get_column_letter(2 + j)
            tc.cell(r, 2 + j, f'=(Raw_PCE!{col}{LR[m]}/Raw_PCE!{col}{LR[m] - 12}-1)*100').number_format = '0.0'
            EXPECT[('Consumer_tech', tc.cell(r, 2 + j).coordinate)] = D['r12'][(l, m)]
        tc.cell(r, 4, 0)
    b2.fmt_hdr(tc, [10, 10, 11, 10])
    b2.notes_tab(wb, [
        ('Title', f"{C['title'][0]}: {C['title'][1]}", 'DRAFT by Claude; Eli to confirm (teammate title: "AI Buildout: Tech Costs Are Rising")'),
        ('Chart heading', C['heading'], 'DRAFT'),
        ('Note line', C['note'], ''),
        ('Left panel', C['panel_l'] + '; horizontal bars, 2018-19 average (dark navy) vs Oct 2026 (red)',
         'PPI_bars over Raw_PPI (03_Data/Raw/BLS_PPI_ai_basket_2026-11-16/; audited 06_Audits/slide2_ai_ppi). Note the 2018-19 average of 12m changes is computed as AVERAGE(index ratio)-1 (= average of the 24 y/y rates)'),
        ('Left panel exclusions', 'storage devices (PCU334112334112) +80.3% and printed circuit assemblies (PCU334418334418) +150.6% left off the chart for scale; PCB index jumps in steps', 'verbal only'),
        ('Labels', '"Electronic components (incl. chips)" = BLS 3344 semiconductor and other electronic components; "Semiconductors & related devices" = 334413 (integrated circuits plus diodes, transistors, wafers; not chips only); "Application software publishing" = 51321050502 (the broader software publishing industry 513210 was -5.6% in Oct, BLS table 12)', 'Codex slide2c_build R1-F01/F02; avoids the teammate slide\'s "Chips" label for the broad series'),
        ('Right panel', C['panel_r'] + '; software (red), computers (dark navy), Oct 2023-Oct 2026, dashed 0%', 'Consumer_tech over Raw_PCE (BEA U20404 lines 49-50 via C_common; Oct 2026 = UMD estimate)'),
        ('Source line', C['source'], ''),
        ('Takeaway', b2.TAKEAWAY, 'placeholder'),
        ('Cross-checks', f"PPI vs J_ai_ppi_summary (2 dp) max diff {D['checks']['J']:.4f}; PCE 12m vs F_attrib_top_leaves (2 dp) max diff {D['checks']['F']:.4f}", ''),
        ('Guide deviations', '(1) left = horizontal bar chart with a series key; categories in column A; (2) left axis -10 to 40 step 10, format 0; (3) left plot x 3.30-5.13 for category names; (4) right y-axis -10 to 25 step 5 (guide floor rule: next whole number below the minimum, scaled to steps of 5)', ''),
        ('Build', 'python3 -I "02_Research/Subtasks/14_slide2a_build/code/build_inflation_slide2c.py" --verify', ''),
    ])
    wb._sheets = [tb, tc, rp, rl, wb['Notes']]
    wb.calculation.fullCalcOnLoad = True
    return wb


def slide_2c(prs, D):
    s = b2.base_slide(prs, C, note=C['note'])
    PL, PR_ = (3.30, 5.13), (7.40, 11.27)
    text_box(s, 0.60, 2.07, 5.13 - 0.60, 0.30, [(C['panel_l'], NAVY)], 13, 'Arial', bold=True)
    text_box(s, PR_[0] - 0.3, 2.07, PR_[1] - PR_[0] + 0.6, 0.30, [(C['panel_r'], NAVY)], 13, 'Arial', bold=True)
    order = list(reversed(PPI))
    frL = (0.45, PLOT_Y[0] - 0.08, PL[1] + 0.55, PLOT_Y[1] + 0.36)
    b2.bar_chart(s, XL_CHART_TYPE.BAR_CLUSTERED, [lab for _, lab in order],
                 [('2018–19 average', [D['bars'][sid][0] for sid, _ in order]), ('Oct 2026', [D['bars'][sid][1] for sid, _ in order])],
                 PL, PLOT_Y, frL, -10, 40, 10, '0', ['0.0;-0.0', '0.0;-0.0'], [DNAVY, RED], gap=50)
    b2.key(s, PL[0] + 0.55, PLOT_Y[1] - 0.30, [('2018–19 avg.', DNAVY), ('Oct 2026', RED)], size=11)
    # right: lines (software red, computers dark navy) + dashed 0%
    vals = [[D['r12'][(l, m)] for m in WIN] for l, _ in LEAVES]
    lo = math.floor(min(min(x) for x in vals) / 5) * 5
    hi = math.ceil(max(max(x) for x in vals) / 5) * 5
    cd = CategoryChartData()
    cd.categories = [m if m[5:] in ('01', '07') else ' ' for m in WIN]
    for (l, n), vv in zip(LEAVES, vals):
        cd.add_series(n, vv)
    cd.add_series('Reference', [0] * len(WIN))
    fr = (PR_[0] - 0.62, PLOT_Y[0] - 0.08, PR_[1] + 0.08, PLOT_Y[1] + 0.36)
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
    b2.axes(ch, lo, hi, 5, '0')
    cs = b2.frame_fix(ch, PR_, PLOT_Y, fr)
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
    yof = lambda v: PLOT_Y[1] - (v - lo) / (hi - lo) * (PLOT_Y[1] - PLOT_Y[0])
    labs = [(n, vv[-1], c) for (l, n), vv, c in zip(LEAVES, vals, (RED, DNAVY))]
    ys = [yof(v) for _, v, _ in labs]
    h = 0.44
    if abs(ys[0] - ys[1]) < h + 0.02:
        mid = (ys[0] + ys[1]) / 2
        ys = [mid - (h + 0.02) / 2, mid + (h + 0.02) / 2] if ys[0] < ys[1] else [mid + (h + 0.02) / 2, mid - (h + 0.02) / 2]
    for (n, v, c), y in zip(labs, ys):
        text_box(s, PR_[1] + 0.16, y - h / 2, 1.30, h, [[(n, c)], [(f'{v:.1f}%*', c)]], 13, 'Arial', align=PP_ALIGN.LEFT, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    return s, (lo, hi)


def build_pptx(D):
    prs = Presentation(DECK)
    lst = prs.slides._sldIdLst
    for sid, slide in zip(list(lst), list(prs.slides)):
        if any(mk in ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame) for mk in (MARK,) + OLD_MARKS):
            prs.part.drop_rel(sid.get(qn('r:id')))
            lst.remove(sid)
    titles = [' '.join(sh.text_frame.text for sh in sl.shapes if sh.has_text_frame) for sl in prs.slides]
    pos = max(i for i, t in enumerate(titles) if b2.B['title'][1] in t) + 1
    from pptx.opc.packuri import PackURI
    used = {str(pt.partname) for pt in prs.part.package.iter_parts()}
    s, rng = slide_2c(prs, D)
    k = 200
    while f'/ppt/slides/slide{k}.xml' in used:
        k += 1
    s.part.partname = PackURI(f'/ppt/slides/slide{k}.xml')
    el = list(lst)[-1]
    lst.remove(el)
    lst.insert(pos, el)
    prs.save(DECK)
    return pos, rng


def sigs_except_2c(path):
    # all slides except 2C: reuse the 2A/2B content signature, but also include 2A/2B (they must not change here)
    import hashlib
    prs = Presentation(path)
    c14 = lambda b: hashlib.sha256(etree.tostring(etree.fromstring(b, etree.XMLParser(remove_blank_text=True)), method='c14n')).hexdigest()
    out = []
    for slide in prs.slides:
        if MARK in ' '.join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame):
            continue
        sig = [c14(etree.tostring(slide._element))]
        for rel in sorted(slide.part.rels.values(), key=lambda r: r.rId):
            if 'chart' in rel.reltype:
                sig.append(c14(rel.target_part.blob))
        out.append(tuple(sig))
    return out


def verify(D, before, pos, rng):
    L = [f'Inflation slide 2C build check, {dt.datetime.now().isoformat(timespec="seconds")}']
    ok = True
    rec = b2.recalc(XLSX_C)
    bad = [(k, v, rec[k[0]][k[1]].value) for k, v in EXPECT.items()
           if not isinstance(rec[k[0]][k[1]].value, (int, float)) or abs(rec[k[0]][k[1]].value - v) > 1e-9]
    L.append(f'1. workbook formula cells: {len(EXPECT)} checked after LibreOffice recalc; mismatches: {len(bad)} {bad[:3]}')
    ok &= not bad
    L.append(f"2. cross-checks: PPI vs J_ai_ppi_summary (audited, 2 dp) {D['checks']['J']:.4f}; PCE 12m vs F_attrib_top_leaves (audited, 2 dp) {D['checks']['F']:.4f}")
    prs = Presentation(DECK)
    sl = list(prs.slides)
    s = sl[pos]
    assert MARK in ' '.join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
    ch = [sh.chart for sh in s.shapes if sh.has_chart]
    worst, n = 0.0, 0
    wb_ = rec['PPI_bars']
    tab = {wb_.cell(r, 1).value: (wb_.cell(r, 2).value, wb_.cell(r, 3).value) for r in range(2, 2 + len(PPI))}
    for j, se in enumerate(ch[0].plots[0].series):
        for name, v in zip(ch[0].plots[0].categories, se.values):
            worst, n = max(worst, abs(v - tab[name][j])), n + 1
    wc = rec['Consumer_tech']
    for j, se in enumerate(list(ch[1].plots[0].series)[:2]):
        for i, v in enumerate(se.values):
            worst, n = max(worst, abs(v - wc.cell(2 + i, 2 + j).value)), n + 1
    L.append(f'3. chart points vs workbook tabs: {n} points; max abs diff {worst:.1e}')
    ok &= worst < 1e-9 and n == 12 + 2 * len(WIN)
    bv = [x for p in D['bars'].values() for x in p]
    lv = [D['r12'][k] for k in D['r12']]
    fit = -10 <= min(bv) and max(bv) <= 40 and rng[0] <= min(lv) and max(lv) <= rng[1]
    L.append(f'4. axes: left -10..40 (data {min(bv):.1f}..{max(bv):.1f}); right {rng[0]}..{rng[1]} (data {min(lv):.1f}..{max(lv):.1f}); fit {fit}')
    ok &= fit
    after = sigs_except_2c(DECK)
    same = after == before
    import zipfile
    names = zipfile.ZipFile(DECK).namelist()
    dup = sorted({x for x in names if names.count(x) > 1})
    order = [' '.join(sh.text_frame.text for sh in x.shapes if sh.has_text_frame)[:40] for x in sl]
    L.append(f'5. deck: {len(sl)} slides, 2C at position {pos + 1}; all other slides (incl. 2A/2B) unchanged in content: {same}; duplicates: {dup or "none"}; order {order}')
    ok &= same and not dup
    L.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    if not ok:
        sys.exit(1)


def main(do_verify):
    D = load()
    build_wb(D).save(XLSX_C)
    before = sigs_except_2c(DECK)
    pos, rng = build_pptx(D)
    print(f'wrote {os.path.relpath(XLSX_C, ROOT)}; 2C at slide {pos + 1}')
    if do_verify:
        verify(D, before, pos, rng)


if __name__ == '__main__':
    main('--verify' in sys.argv)
