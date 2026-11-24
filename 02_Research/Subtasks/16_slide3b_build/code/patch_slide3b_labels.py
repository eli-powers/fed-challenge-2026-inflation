"""Patch Eli's hand-edited slide 3B in place (Nov 16): keep the "Quarterly pace" version, delete the other copy,
and add a marker + native data label at each forecast path's 2027Q4 point (option A).

Run from the project root (deck must be closed in PowerPoint):
    python3 -I "02_Research/Subtasks/16_slide3b_build/code/patch_slide3b_labels.py"

Why a patch, not a rebuild: Eli edited the slide by hand after build_inflation_slide3b.py ran (removed the 2027 bracket
and arrow). Rerunning the builder would erase those edits, so this script touches only the keeper slide's chart XML and
removes the superseded copy. Labels are native chart data labels: they show the chart's own cached values (which equal
the Forecast tab of Inflation Slide 3B.xlsx) and stay attached to the points if the chart is resized.
"""
import datetime as dt
import os
import shutil
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.oxml.ns import qn
from pptx.util import Pt

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '15_slide3a_build', 'code'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '14_slide2a_build', 'code'))
import build_inflation_slide3b as b  # noqa: E402

DECK = b.DECK
KEEP_MARK = 'Quarterly pace'
STYLE = {'Oil to $110': (b.RED, XL_LABEL_POSITION.ABOVE), 'SPF median': (b.BLACK, XL_LABEL_POSITION.ABOVE),
         'Hormuz reopens': (b.DNAVY, XL_LABEL_POSITION.BELOW)}
REPORT = os.path.join(HERE, 'patch_labels_report.txt')


def texts(slide):
    return b.b3.title_of(slide)


def label_last_point(series, color, pos):
    i = len(list(series.values)) - 1
    pt = series.points[i]
    pt.marker.style = XL_MARKER_STYLE.CIRCLE
    pt.marker.size = 7
    pt.marker.format.fill.solid()
    pt.marker.format.fill.fore_color.rgb = RGBColor.from_string(color)
    pt.marker.format.line.color.rgb = RGBColor.from_string(color)
    dl = pt.data_label
    dl.position = pos
    dl.show_value = True
    dl.font.name, dl.font.size, dl.font.bold = 'Arial', Pt(12), True
    dl.font.color.rgb = RGBColor.from_string(color)
    d = dl._dLbl
    nf = d.find(qn('c:numFmt'))
    if nf is None:
        nf = etree.Element(qn('c:numFmt'))
        d.find(qn('c:idx')).addnext(nf)
    nf.set('formatCode', '0.0')
    nf.set('sourceLinked', '0')
    for tag in ('c:showLegendKey', 'c:showCatName', 'c:showSerName', 'c:showPercent', 'c:showBubbleSize'):
        el = d.find(qn(tag))
        if el is not None:
            el.set('val', '0')
    return i


def main():
    lock = os.path.join(os.path.dirname(DECK), '~$' + os.path.basename(DECK))
    assert not os.path.exists(lock), 'deck is open in PowerPoint; close it first'
    bk = os.path.join(HERE, '..', 'backup')
    os.makedirs(bk, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y-%m-%dT%H%M')
    shutil.copy2(DECK, os.path.join(bk, f'working_deck_before_label_patch_{stamp}.pptx'))
    before = b.sigs_others(DECK)
    prs = Presentation(DECK)
    lst = prs.slides._sldIdLst
    ours = [(sid, s) for sid, s in zip(list(lst), list(prs.slides)) if b.MARK in texts(s)]
    keep = [(sid, s) for sid, s in ours if KEEP_MARK in texts(s)]
    drop = [(sid, s) for sid, s in ours if KEEP_MARK not in texts(s)]
    assert len(keep) == 1 and len(drop) <= 1, (len(keep), len(drop))
    for sid, _ in drop:
        prs.part.drop_rel(sid.get(qn('r:id')))
        lst.remove(sid)
    slide = keep[0][1]
    ch = [sh.chart for sh in slide.shapes if sh.has_chart][0]
    done = {}
    for se in ch.plots[0].series:
        if se.name in STYLE:
            color, pos = STYLE[se.name]
            i = label_last_point(se, color, pos)
            done[se.name] = (ch.plots[0].categories[i], list(se.values)[i])
    # give the dot labels room: names, divider and column move right (absolute positions, so reruns are idempotent)
    from pptx.util import Inches
    names = {'Oil to $110', 'SPF median', 'Hormuz reopens'}
    for sh in slide.shapes:
        t = sh.text_frame.text if sh.has_text_frame else None
        if t in names:
            sh.left = Inches(9.28)
        elif t is not None and t.startswith('2027 as a whole'):
            sh.left = Inches(11.15)
        elif t is not None and t.endswith('%') and len(t) <= 5:
            sh.left = Inches(11.35)
        elif sh.shape_type == 9:          # the divider line Eli kept
            sh.left = Inches(11.10)
    # Nov 16 (Eli: dots clipped after pasting into the team deck): the 2027Q4 dots sit on the plot's right border and the
    # chart frame ended only ~0.1 in past the plot, so a re-layout in another deck clipped them. Widen the frame to the
    # right to FRAME_RIGHT and rescale the manual plot layout so the plot stays at the same absolute inches.
    FRAME_RIGHT = 9.80
    gf = [sh for sh in slide.shapes if sh.has_chart][0]
    ml = gf.chart._chartSpace.find(qn('c:chart')).find(qn('c:plotArea')).find(qn('c:layout')).find(qn('c:manualLayout'))
    L0, W0 = gf.left / 914400, gf.width / 914400
    xf, wf = float(ml.find(qn('c:x')).get('val')), float(ml.find(qn('c:w')).get('val'))
    # place the plot where it has been rendering (b.RENDER_X), so Eli's shading, names and column stay aligned;
    # with the wider frame PowerPoint honours the manual layout exactly (measured Nov 16)
    # Nov 16, second fix (Eli, PowerPoint for the web): the web app clips markers at the PLOT-AREA edge, and with
    # crossBetween=midCat the first/last points sit on that edge. Switch to crossBetween=between (points at category
    # centres) and widen the plot by half a category on each side, so every point keeps its x position (RENDER_X)
    # while the 2027Q4 dot sits half a category inside the plot. Frame left moves to FRAME_LEFT for the y-axis labels.
    FRAME_LEFT = 0.25
    n_cat = len(list(gf.chart.plots[0].categories))
    step = (b.RENDER_X[1] - b.RENDER_X[0]) / (n_cat - 1)
    px0, pw = b.RENDER_X[0] - step / 2, step * n_cat
    for vax in gf.chart._chartSpace.iter(qn('c:valAx')):
        vax.find(qn('c:crossBetween')).set('val', 'between')
    L1, W1 = FRAME_LEFT, FRAME_RIGHT - FRAME_LEFT
    gf.left, gf.width = Inches(L1), Inches(W1)
    ml.find(qn('c:x')).set('val', repr((px0 - L1) / W1))
    ml.find(qn('c:w')).set('val', repr(pw / W1))
    frame_note = (f'chart frame x {L0:.3f}-{L0 + W0:.3f} -> {L1:.3f}-{FRAME_RIGHT:.3f} in; crossBetween=between; plot area x '
                  f'{px0:.3f}-{px0 + pw:.3f} in, so points run {b.RENDER_X[0]:.3f}-{b.RENDER_X[1]:.3f} in (= RENDER_X), '
                  f'last point {step / 2:.3f} in inside the plot edge')
    prs.save(DECK)
    after = b.sigs_others(DECK)
    sl = list(Presentation(DECK).slides)
    L = [f'Slide 3B label patch, {dt.datetime.now().isoformat(timespec="seconds")}',
         f'deleted superseded copy: {len(drop)}; deck now {len(sl)} slides; 3B at position '
         f'{[i + 1 for i, s in enumerate(sl) if b.MARK in texts(s)]}; other slides unchanged: {after == before}',
         'labels (category, value shown at 0.0): ' + '; '.join(f'{k} {c} {v:.4f} -> {v:.1f}' for k, (c, v) in done.items())]
    L.append(frame_note)
    ok = after == before and len(done) == 3
    L.append(f'RESULT: {"PASS" if ok else "FAIL"}')
    open(REPORT, 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
