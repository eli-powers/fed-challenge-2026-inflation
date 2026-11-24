"""Inflation slide 1, alternate version: 12-month and 3-month annualized on BOTH panels (headline left, core right).

Professor's comment on team deck slide 4 (Nov 18): show headline and core separately, each with 12m and 3m
(or 6m and 3m). Eli, Nov 18: build the 12m + 3m version; keep the current slide.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide1_build/code/build_slide1_alt_12m3m.py"

What it does (backs up both files to 01_Finals/slides/archive/ first):
  1. Inflation Slide 1.xlsx: adds tabs Alt_Headline and Alt_Core (formulas over Raw_PCE, same window as 12m/Momentum)
     and appends rows to Notes. Existing tabs untouched.
  2. Team_Working_Deck.pptx: copies current slide 4 (inflation slide 1, with Eli's formatting) and inserts the copy
     right after it. On the copy: charts re-fed (3-month red, 12-month navy, 2% dashed), y-axis 0 to 7 on both
     panels, panel titles, chart heading, end labels (text and height) and source line. Title and takeaway kept.
Same data as build_inflation_slide1.py (BEA T20804 Oct 29 release + UMD Oct estimate); it imports load_data() from there.
"""
import copy
import datetime as dt
import math
import os
import shutil
import sys

from lxml import etree
from openpyxl import load_workbook
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.parts.chart import ChartPart

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_inflation_slide1 as base  # noqa: E402

ROOT = base.ROOT
XLSX = os.path.join(ROOT, '01_Finals', 'Slide data', 'Inflation Slide 1.xlsx')
DECK = os.path.join(ROOT, '01_Finals', 'slides', 'Team_Working_Deck.pptx')
ARCH = os.path.join(ROOT, '01_Finals', 'slides', 'archive')
SRC_TITLE = 'Inflation: Firming Again After a Summer Lull'
HEADING = 'PCE Inflation: 12-Month Rates and 3-Month Momentum'          # drafted by Claude; Eli to confirm
PANEL_L, PANEL_R = 'Headline PCE, % Change', 'Core PCE, % Change'
SOURCE = ('Source: BEA (PCE and core PCE price indexes, NIPA Table 2.8.4). Percent change: 12-month and 3-month '
          'annualized; monthly, through Oct 2026*. Dashed line: 2% target. *Oct 2026 = UMD estimate built from BLS CPI/PPI.')
ALT_MARK = 'ALT 12m/3m'   # written to the slide's notes so a rerun finds and replaces the copy instead of adding another


def rates_alt():
    allm, win, L, rates, est, band = base.load_data()
    i = {m: allm.index(m) for m in allm}
    out = {}
    for m in win:
        k = i[m]
        out[m] = {
            'head12': rates[m]['head12'], 'core12': rates[m]['core12'], 'core3': rates[m]['core3'],
            'head3': ((L[m]['headline'] / L[allm[k - 3]]['headline']) ** 4 - 1) * 100,
        }
    return allm, win, out


# ---------------------------------------------------------------- workbook (patched in place)
def patch_workbook(allm, win, R):
    wb = load_workbook(XLSX)
    for n in ('Alt_Headline', 'Alt_Core'):
        if n in wb.sheetnames:
            del wb[n]
    raw_row = {m: j + 2 for j, m in enumerate(allm)}
    assert wb['Raw_PCE'].cell(raw_row[win[-1]], 1).value == base.mdate(win[-1]), 'Raw_PCE row layout changed'
    for name, col, k12, k3 in (('Alt_Headline', 'C', 'head12', 'head3'), ('Alt_Core', 'B', 'core12', 'core3')):
        ws = wb.create_sheet(name, index=wb.sheetnames.index('Raw_PCE'))
        ws.append(['Date', '3-month', '12-month', 'Reference'])
        for j, m in enumerate(win):
            r, rr = j + 2, raw_row[m]
            ws.cell(r, 1, base.mdate(m)).number_format = 'yyyy-mm'
            ws.cell(r, 2, f'=((Raw_PCE!{col}{rr}/Raw_PCE!{col}{rr - 3})^4-1)*100').number_format = '0.00'
            ws.cell(r, 3, f'=(Raw_PCE!{col}{rr}/Raw_PCE!{col}{rr - 12}-1)*100').number_format = '0.00'
            ws.cell(r, 4, base.REFERENCE).number_format = '0.00'
        for c in ws[1]:
            c.font = copy.copy(wb['12m']['A1'].font)
        ws.freeze_panes = 'A2'
        for k, w in enumerate([11, 10, 10, 10]):
            ws.column_dimensions[chr(65 + k)].width = w
    nt = wb['Notes']
    tag = 'ALT VERSION (team deck slide 5): 12-month + 3-month annualized on both panels'
    start = next((r for r in range(1, nt.max_row + 1) if nt.cell(r, 1).value == tag), None)
    if start:
        nt.delete_rows(start - 1, nt.max_row - start + 2)
    last = len(win) + 1
    nt.append([])
    nt.append([tag, '', 'Professor comment on slide 4; Eli, Nov 18: build it, keep the current slide'])
    for row in (
        ('Chart heading', HEADING, 'drafted by Claude; Eli to confirm'),
        ('Left panel title', PANEL_L, 'Alt_Headline tab'),
        ('Right panel title', PANEL_R, 'Alt_Core tab'),
        ('End label: 3-month (left, red)', f'=Alt_Headline!B{last}', 'Oct 2026 = UMD estimate'),
        ('End label: 12-month (left, dark navy)', f'=Alt_Headline!C{last}', 'Oct 2026 = UMD estimate'),
        ('End label: 3-month (right, red)', f'=Alt_Core!B{last}', 'Oct 2026 = UMD estimate'),
        ('End label: 12-month (right, dark navy)', f'=Alt_Core!C{last}', 'Oct 2026 = UMD estimate'),
        ('Y-axis range (both panels)', '0 to 7, steps of 1, format 0.00', 'Headline 3m ann. peaks at 6.16% (May 2026); same range both panels'),
        ('Source line', SOURCE, 'Same wording as the original, with the horizons changed'),
        ('Build', 'python3 -I "02_Research/Subtasks/10_slide1_build/code/build_slide1_alt_12m3m.py"', ''),
    ):
        nt.append(list(row))
        if row[1].startswith('='):
            nt.cell(nt.max_row, 2).number_format = '0.00'
    wb.calculation.fullCalcOnLoad = True
    wb.save(XLSX)


# ---------------------------------------------------------------- deck
def find_slide(prs, title, alt):
    for idx, s in enumerate(prs.slides):
        texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
        is_alt = s.has_notes_slide and ALT_MARK in s.notes_slide.notes_text_frame.text
        if title in texts and is_alt == alt:
            return idx, s
    return None, None


def delete_slide(prs, idx):
    sid = prs.slides._sldIdLst[idx]
    prs.part.drop_rel(sid.get(qn('r:id')))
    prs.slides._sldIdLst.remove(sid)


def duplicate_slide(prs, src_idx):
    src = prs.slides[src_idx]
    new = prs.slides.add_slide(src.slide_layout)
    for sh in list(new.shapes):
        sh._element.getparent().remove(sh._element)
    bg = src._element.cSld.bg
    if bg is not None:
        new._element.cSld.insert(0, copy.deepcopy(bg))
    pkg = prs.part.package
    for sh in src.shapes:
        el = copy.deepcopy(sh._element)
        new.shapes._spTree.append(el)
        if sh.has_chart:
            op = sh.chart_part
            cp = ChartPart.load(pkg.next_partname(ChartPart.partname_template), op.content_type, pkg, op.blob)
            ext = cp._element.find(qn('c:externalData'))
            if ext is not None:
                cp._element.remove(ext)
            cp.chart_workbook.update_from_xlsx_blob(op.chart_workbook.xlsx_part.blob)
            rid = new.part.relate_to(cp, RT.CHART)
            el.find('.//' + qn('c:chart')).set(qn('r:id'), rid)
    # move the new slide to sit right after the source
    lst = prs.slides._sldIdLst
    sid = lst[-1]
    lst.remove(sid)
    lst.insert(src_idx + 1, sid)
    return prs.slides[src_idx + 1]


def set_text(shape, lines):
    """Replace text paragraph by paragraph, keeping the first run's formatting in each paragraph."""
    paras = shape.text_frame.paragraphs
    assert len(paras) == len(lines), (shape.name, len(paras), lines)
    for p, t in zip(paras, lines):
        runs = p.runs
        runs[0].text = t
        for r in runs[1:]:
            r._r.getparent().remove(r._r)


def plot_y_range(gf):
    """Inner plot area top/bottom in EMU, from the chart frame and its manual layout."""
    ml = gf.chart._chartSpace.find('.//' + qn('c:plotArea') + '/' + qn('c:layout') + '/' + qn('c:manualLayout'))
    y = float(ml.find(qn('c:y')).get('val'))
    h = float(ml.find(qn('c:h')).get('val'))
    return gf.top + y * gf.height, gf.top + (y + h) * gf.height


def place_labels(boxes_vals, y0, y1, ymax):
    """boxes_vals: [(shape, value)]; centre each label on its line end, nudged apart if they would overlap."""
    h = boxes_vals[0][0].height
    gap = int(0.02 * 914400)
    ys = [y1 - v / ymax * (y1 - y0) for _, v in boxes_vals]
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    for a, b in zip(order, order[1:]):
        need = h + gap - (ys[b] - ys[a])
        if need > 0:
            ys[a] -= need / 2
            ys[b] += need / 2
    for (shape, _), y in zip(boxes_vals, ys):
        shape.top = int(y - h / 2)


def build_deck(win, R, ymax):
    prs = Presentation(DECK)
    old_idx, _ = find_slide(prs, SRC_TITLE, alt=True)
    if old_idx is not None:
        delete_slide(prs, old_idx)
    src_idx, src = find_slide(prs, SRC_TITLE, alt=False)
    assert src is not None, 'slide 1 (inflation) not found in team deck'
    s = duplicate_slide(prs, src_idx)
    s.notes_slide.notes_text_frame.text = (f'{ALT_MARK}: alternate of the previous slide (headline left, core right; '
                                           '12-month and 3-month annualized). Built by build_slide1_alt_12m3m.py.')
    by = {sh.name: sh for sh in s.shapes}
    by_text = {sh.text_frame.text: sh for sh in s.shapes if sh.has_text_frame}
    set_text(by_text['PCE Inflation: 12-Month Rates and Recent Core Momentum'], [HEADING])
    set_text(by_text['PCE, 12-Month % Change'], [PANEL_L])
    set_text(by_text['Core PCE, Annualized % Change'], [PANEL_R])
    set_text(next(sh for t, sh in by_text.items() if t.startswith('Source: BEA')), [SOURCE])
    charts = sorted([sh for sh in s.shapes if sh.has_chart], key=lambda g: g.left)
    assert len(charts) == 2
    last = win[-1]
    panels = [(charts[0], 'head3', 'head12'), (charts[1], 'core3', 'core12')]
    label_sets = [  # (box for 3-month, box for 12-month) per panel: the original red/navy label boxes
        (by_text[next(t for t in by_text if t.startswith('Core\n'))], by_text[next(t for t in by_text if t.startswith('Headline\n'))]),
        (by_text[next(t for t in by_text if t.startswith('3-month\n'))], by_text[next(t for t in by_text if t.startswith('6-month\n'))]),
    ]
    for (gf, k3, k12), (box3, box12) in zip(panels, label_sets):
        names = [se.name for se in gf.chart.plots[0].series]
        assert len(names) == 3 and names[2] == 'Reference', names   # index 0 = red line, 1 = navy, 2 = dashed 2%
        cd = CategoryChartData()
        cd.categories = base.axis_labels(win)
        cd.add_series('3-month', [R[m][k3] for m in win])
        cd.add_series('12-month', [R[m][k12] for m in win])
        cd.add_series('Reference', [base.REFERENCE] * len(win))
        gf.chart.replace_data(cd)
        for se in gf.chart.plots[0].series:
            se.smooth = False
        va = gf.chart.value_axis
        va.minimum_scale, va.maximum_scale, va.major_unit = 0, ymax, 1
        set_text(box3, ['3-month', f'{R[last][k3]:.2f}%*'])
        set_text(box12, ['12-month', f'{R[last][k12]:.2f}%*'])
        y0, y1 = plot_y_range(gf)
        place_labels([(box3, R[last][k3]), (box12, R[last][k12])], y0, y1, ymax)
    prs.save(DECK)
    return src_idx + 2   # 1-based number of the new slide


def main():
    allm, win, R = rates_alt()
    allv = [R[m][k] for m in win for k in R[win[0]]] + [base.REFERENCE]
    assert min(allv) >= 0
    ymax = math.ceil(max(allv))
    stamp = dt.datetime.now().strftime('%Y-%m-%d_%H%M')
    os.makedirs(ARCH, exist_ok=True)
    shutil.copy2(DECK, os.path.join(ARCH, f'Team_Working_Deck_pre-alt12m3m_{stamp}.pptx'))
    shutil.copy2(XLSX, os.path.join(ARCH, f'Inflation Slide 1_pre-alt12m3m_{stamp}.xlsx'))
    patch_workbook(allm, win, R)
    n = build_deck(win, R, ymax)
    print(f'y-axis 0-{ymax}; new slide = deck slide {n}; last values (Oct 2026*): '
          + ', '.join(f'{k} {R[win[-1]][k]:.2f}' for k in ('head3', 'head12', 'core3', 'core12')))


if __name__ == '__main__':
    main()
