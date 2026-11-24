"""Append the r* policy-stance slides (A, B, B-alt) to the working deck, drawn from native PowerPoint shapes
(one coordinate mapping for dots, bands, lines, shading and axis, so they align in PowerPoint, Keynote and LibreOffice).

Patches the hand-edited deck in place: backs it up, removes any earlier copies of these slides
(shape named RSTAR_SLIDE_TAG), then appends three slides at the end. All numbers and text come
from 01_Finals/data/SlideRstar_Policy_Data.xlsx (built by build_rstar_slide.py).

Run from project root:
    python3 -I 02_Research/Subtasks/rstar_logan_match/code/add_rstar_slides_to_deck.py
"""
import copy, datetime, shutil
from pathlib import Path
import openpyxl
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt, Emu

ROOT = Path.cwd()
DECK = ROOT / "01_Finals/slides/Inflation Slides (working).pptx"
WB = ROOT / "01_Finals/data/SlideRstar_Policy_Data.xlsx"
ARCH = ROOT / "01_Finals/slides/archive"
TAG = "RSTAR_SLIDE_TAG"

NAVY, WHITE, GOLD, BG = "1B2A4A", "FFFFFF", "F2CC6B", "F2F2F2"
RED, DNAVY, AXIS, LABEL, SRC = "C0282D", "1B2A61", "7F7F7F", "595959", "6B6B6B"
# plot area (inches): rows, axis, labels
PX0, PX1, PY0, PY1 = 4.05, 10.55, 2.95, 5.55


def blend(h, a, bg=BG):
    c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]; b = [int(bg[i:i + 2], 16) for i in (0, 2, 4)]
    return "".join(f"{round(a * x + (1 - a) * y):02X}" for x, y in zip(c, b))


def rgb(h):
    return RGBColor.from_string(h)


def tb(slide, l, t, w, h, text, size, color, font="Arial", bold=False, italic=False, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.MIDDLE, wrap=True):
    s = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = s.text_frame; tf.word_wrap = wrap; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    runs = text if isinstance(text, list) else [(text, color)]
    p = tf.paragraphs[0]; p.alignment = align
    for txt, col in runs:
        r = p.add_run(); r.text = txt
        f = r.font; f.size = Pt(size); f.name = font; f.bold = bold; f.italic = italic; f.color.rgb = rgb(col)
    return s


def read_wb():
    wb = openpyxl.load_workbook(WB, data_only=True)
    r = [x for x in wb["rstar"].iter_rows(values_only=True)][1:]
    est = [dict(model=x[0], value=x[1], lo=x[2], hi=x[3], band=x[4], short="short-run" in x[0]) for x in r if x[0]]
    rr = {(x[0], x[1]): x for x in list(wb["real_rates"].iter_rows(values_only=True))[1:] if x[0]}
    txt = {}
    for v, f, t in list(wb["slide_text"].iter_rows(values_only=True))[1:]:
        txt[(v, f)] = t
    return est, rr, txt


def add_slide(prs, est, lines, bands, xmin, xmax, unit, source, note_line, heading):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(BG)
    band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.01))
    band.fill.solid(); band.fill.fore_color.rgb = rgb(NAVY); band.line.fill.background(); band.name = TAG
    tf = band.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    for t, col in (("Policy stance:", WHITE), (" [story the team writes]", GOLD)):
        r = p.add_run(); r.text = t; r.font.size = Pt(32); r.font.name = "Georgia"; r.font.color.rgb = rgb(col)
    tb(s, 0.67, 1.09, 12.00, 0.61, heading, 21, NAVY, font="Georgia", bold=True, align=PP_ALIGN.CENTER)
    tb(s, 0.67, 1.63, 12.00, 0.30, note_line, 13, NAVY, align=PP_ALIGN.CENTER)

    order = sorted(est, key=lambda e: (e["short"], e["value"]))
    n = len(order)
    # data y: row i at y = n-1-i; axis from -0.5 to n-0.5
    def y_in(i):  # inches from top for row i
        return PY0 + (i + 0.5) / n * (PY1 - PY0)
    def x_in(v):
        return PX0 + (v - xmin) / (xmax - xmin) * (PX1 - PX0)

    # neutral zone shading (behind chart)
    trend = [e["value"] for e in est if not e["short"]]
    lo_z, hi_z = min(trend), max(trend)
    zone_top = 2.20
    z = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x_in(lo_z)), Inches(zone_top), Inches(x_in(hi_z) - x_in(lo_z)), Inches(PY1 - zone_top))
    z.fill.solid(); z.fill.fore_color.rgb = rgb(DNAVY); z.line.fill.background()
    sf = z.fill._xPr.find(qn("a:solidFill")); etree.SubElement(sf[0], qn("a:alpha"), val="9000")

    # uncertainty bands: native line shapes on the chart's coordinate mapping (behind the chart's dots)
    if bands:
        for i, e in enumerate(order):
            if e["lo"] is None:
                continue
            c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x_in(e["lo"])), Inches(y_in(i)), Inches(x_in(e["hi"])), Inches(y_in(i)))
            c.line.width = Pt(7)
            c.line.color.rgb = rgb(blend(GOLD, 0.45) if e["short"] else blend(DNAVY, 0.33))
            c.line._get_or_add_ln().set("cap", "flat")
            c.name = f"band {e['model']}"

    # policy-rate lines, dots and x-axis: native shapes on the same coordinate mapping
    def seg(x0, y0, x1, y1, color, width, dash=None, name=None):
        c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0), Inches(x1), Inches(y1))
        c.line.width = Pt(width); c.line.color.rgb = rgb(color)
        if dash:
            c.line.dash_style = MSO_LINE.DASH
        if name:
            c.name = name
        return c
    seg(PX0, PY1, PX1, PY1, AXIS, 1, name="x-axis")
    t = xmin
    while t <= xmax + 1e-9:
        tb(s, x_in(t) - 0.4, PY1 + 0.06, 0.8, 0.25, f"{t:.1f}%".replace("-", "−"), 12, LABEL, align=PP_ALIGN.CENTER)
        t += unit
    for lab, val, dash in lines:
        seg(x_in(val), PY0 - 0.08, x_in(val), PY1, RED, 3, dash, name=f"policy line {lab}")
    d = 0.17
    for i, e in enumerate(order):
        o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x_in(e["value"]) - d / 2), Inches(y_in(i) - d / 2), Inches(d), Inches(d))
        o.fill.solid(); o.fill.fore_color.rgb = rgb(GOLD if e["short"] else DNAVY)
        o.line.color.rgb = rgb(DNAVY); o.line.width = Pt(1.5); o.name = f"dot {e['model']}"
        o.shadow.inherit = False

    # zone + direction labels
    tb(s, x_in(lo_z) - 0.6, zone_top + 0.02, x_in(hi_z) - x_in(lo_z) + 1.2, 0.28, f"Neutral zone {lo_z:.2f}–{hi_z:.2f}%", 12, DNAVY,
       bold=True, align=PP_ALIGN.CENTER)
    tb(s, PX0, zone_top + 0.02, 2.2, 0.28, "← Accommodative", 12, LABEL)
    tb(s, PX1 - 2.2, zone_top + 0.02, 2.2, 0.28, "Restrictive →", 12, LABEL, align=PP_ALIGN.RIGHT)
    # policy-line labels
    ly = PY0 - 0.42
    for j, (lab, val, dash) in enumerate(lines):
        if len(lines) == 1:
            tb(s, x_in(val) - 2.5, ly, 5.0, 0.28, f"{lab}: {val:.2f}%", 12.5, RED, bold=True, align=PP_ALIGN.CENTER)
        elif j == 0:
            tb(s, x_in(val) - 4.06, ly, 4.0, 0.28, f"{lab}: {val:.2f}%", 12.5, RED, bold=True, align=PP_ALIGN.RIGHT)
        else:
            tb(s, x_in(val) + 0.06, ly, 4.0, 0.28, f"{lab}: {val:.2f}%", 12.5, RED, bold=True)
    # row labels + values
    for i, e in enumerate(order):
        yc = y_in(i)
        name = e["model"].replace(" (short-run r*)", "") + (" (short-run r*)" if e["short"] else "")
        tb(s, 0.30, yc - 0.17, PX0 - 0.42, 0.34, name, 13, NAVY, bold=e["short"], align=PP_ALIGN.RIGHT)
        if bands:
            bt = "no band published" if e["lo"] is None else (f"{e['lo']:.2f} to {e['hi']:.2f}".replace("-", "−") + ("*" if str(e["band"]).startswith("≈68%") else ""))
            tb(s, PX1 + 0.12, yc - 0.15, 2.6, 0.30, f"{e['value']:.2f}   [{bt}]", 11.5, LABEL)
        else:
            tb(s, x_in(e["value"]) + 0.16, yc - 0.15, 0.6, 0.30, f"{e['value']:.2f}", 11.5, LABEL)
    tb(s, 0.73, 6.02, 12.00, 0.50, source, 10, SRC, anchor=MSO_ANCHOR.TOP)
    tb(s, 0.67, 6.62, 12.00, 0.68, "[Takeaway: one sentence the team writes]", 24, NAVY, font="Georgia", bold=True, italic=True,
       align=PP_ALIGN.CENTER)
    return s


def main():
    est, rr, txt = read_wb()
    ARCH.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    prs = Presentation(DECK)
    if not any(sh.name == TAG for sl in prs.slides for sh in sl.shapes):  # back up only the true pre-r* deck
        shutil.copy2(DECK, ARCH / f"Inflation Slides (working)_pre-rstar_{stamp}.pptx")
    # drop earlier copies of these slides
    sldIdLst = prs.slides._sldIdLst
    for sld_id, slide in list(zip(list(sldIdLst), list(prs.slides))):
        if any(sh.name == TAG for sh in slide.shapes):
            prs.part.drop_rel(sld_id.rId); sldIdLst.remove(sld_id)
    heading, note, source = txt[("all", "heading")], txt[("all", "note_line")], txt[("all", "source")]
    cle = rr[("Cleveland Fed 1-yr expected inflation (headline CPI)", "next 12 months")][6]
    def r(var, win):
        return rr[(f"SPF Q4 2026 median, {var}", win)][6]
    # A
    add_slide(prs, est, [("Headline CPI (Cleveland Fed)", cle, None), ("Headline PCE (SPF)", r("headline PCE", "26Q4-27Q3"), True)],
              False, 0, 2.5, 0.5, source + " " + txt[("A: CPI vs PCE (no bands)", "source_tail")], note, heading)
    # B, B-alt
    for win, key in (("26Q4-27Q3", "B: headline vs core PCE, 2026Q4-27Q3"), ("27Q1-27Q4", "B-alt: headline vs core PCE, 2027Q1-Q4")):
        h, c = r("headline PCE", win), r("core PCE", win)
        if abs(h - c) < 0.005:
            lines = [("Headline = core PCE (SPF)", h, None)]
        else:
            lines = sorted([("Headline PCE (SPF)", h, None), ("Core PCE (SPF)", c, True)], key=lambda t: t[1])
        add_slide(prs, est, lines, True, -1, 3.5, 1, source + " " + txt[(key, "source_tail")], note, heading)
    prs.save(DECK)
    print("saved", DECK, "slides:", len(prs.slides))


if __name__ == "__main__":
    main()
