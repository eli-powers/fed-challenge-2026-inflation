"""Build the r* policy-stance slide: data workbook + slide mockups (PNG) in house style.

Every number is read from saved raw files; nothing is typed in by hand except the
raw-file paths and the SPF window choice below.

Run from project root:
    python3 -I 02_Research/Subtasks/rstar_logan_match/code/build_rstar_slide.py

Outputs
    01_Finals/data/SlideRstar_Policy_Data.xlsx   (tabs: rstar, real_rates, notes)
    02_Research/Subtasks/rstar_logan_match/output/slide_A_cpi_vs_pce.png      (no bands)
    02_Research/Subtasks/rstar_logan_match/output/slide_B_headline_vs_core_pce.png  (bands)
    02_Research/Subtasks/rstar_logan_match/output/slide_B_alt_next4q.png      (B with 2027Q1-Q4 window)
"""
import csv, json, re, html
from math import prod
from pathlib import Path
import openpyxl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path.cwd()
RAW = ROOT / "03_Data/Raw/rstar_2026-11-16"
FRED_DATE = "2026-11-17"
SPF_FILE = ROOT / "03_Data/pipelines/forecast_3b/raw/2026-11-16/medianLevel.xlsx"
OUT = ROOT / "02_Research/Subtasks/rstar_logan_match/output"
WB_OUT = ROOT / "01_Finals/data/SlideRstar_Policy_Data.xlsx"
# SPF window: Eli's choice = survey quarter + next 3 (cols 2-5: 2026Q4-2027Q3).
# Alternative (pipeline convention, next 4 quarters) = cols 3-6: 2027Q1-2027Q4.
SPF_WINDOWS = {"26Q4-27Q3": (2, 5), "27Q1-27Q4": (3, 6)}
MAIN_WINDOW = "26Q4-27Q3"

Z90 = 1.6448536  # standard-normal 95th percentile: 90% two-sided band = ±1.645 s.d.
NAVY, WHITE, GOLD, BG = "#1B2A4A", "#FFFFFF", "#F2CC6B", "#F2F2F2"
RED, DNAVY, AXIS, LABEL, SRC = "#C0282D", "#1B2A61", "#7F7F7F", "#595959", "#6B6B6B"


def sheet_rows(path, sheet):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet]
    return [r for r in ws.iter_rows(values_only=True) if any(c is not None for c in r)]


def param(rows, block, name):
    """Value of `name` in the rows following the header row whose first cell == block."""
    on = False
    for r in rows:
        vals = [c for c in r if c is not None]
        if vals and vals[0] == block:
            on = True
            continue
        if on and vals and vals[0] == name:
            return float(vals[1])
    raise KeyError((block, name))


def load_rstar():
    est = []
    # HLW (NY Fed): one-sided US r*, band = +/-1 S.E. (final obs.) from Parameters sheet
    r = sheet_rows(RAW / "Holston_Laubach_Williams_current_estimates.xlsx", "HLW Estimates")
    v, d = float(r[-1][10]), r[-1][0]
    se = param(sheet_rows(RAW / "Holston_Laubach_Williams_current_estimates.xlsx", "Parameters"), "S.E. (final obs.)", "r*")
    est.append(dict(plabel="2026Q2", model="HLW (NY Fed)", value=v, lo=v - se, hi=v + se, band="±1 S.E. (final obs.)",
                    period=f"{d.year}Q{(d.month - 1) // 3 + 1}", concept="Trend", kind="trend"))
    # LW (NY Fed): one-sided r*, band = +/-1 S.E. (final)
    r = sheet_rows(RAW / "Laubach_Williams_current_estimates.xlsx", "data")
    v, d = float(r[-1][2]), r[-1][0]
    se = param(sheet_rows(RAW / "Laubach_Williams_current_estimates.xlsx", "parameters"), "SE (final)", "r*")
    est.append(dict(plabel="2026Q2", model="Laubach–Williams (NY Fed)", value=v, lo=v - se, hi=v + se, band="±1 S.E. (final)",
                    period=f"{d.year}Q{(d.month - 1) // 3 + 1}", concept="Trend", kind="trend"))
    # Lubik-Matthes (Richmond Fed): median, 16th-84th percentile
    r = sheet_rows(RAW / "lubik_matthes_natural_rate_interest.xlsx", "LM_RealRate")
    d = r[-1][0]
    est.append(dict(plabel="2026Q2", model="Lubik–Matthes (Richmond Fed)", value=float(r[-1][2]), lo=float(r[-1][1]), hi=float(r[-1][3]),
                    band="16th–84th pct.", period=f"{d.year}Q{(d.month - 1) // 3 + 1}", concept="Trend (5-yr-ahead VAR)", kind="trend"))
    # Zaman (Cleveland Fed): mean, 68% band, latest quarter of Nov 6 vintage
    r = sheet_rows(RAW / "zaman_stars_2026Q3.xlsx", "Stars_Smoothed")
    c = [i for i, x in enumerate(r[0]) if isinstance(x, str) and x.lower().startswith("rstar")][0]
    assert r[1][c + 2] == "68L" and r[1][c + 3] == "Mean" and r[1][c + 4] == "68U", r[1][c:c + 6]
    row = r[-1]
    est.append(dict(plabel="2026Q3", model="Zaman (Cleveland Fed)", value=float(row[c + 3]), lo=float(row[c + 2]), hi=float(row[c + 4]),
                    band="68%", period=str(row[c]).replace(".", "Q"), concept="Medium run", kind="trend"))
    # Glover-Oliyide (KC Fed): point, 68%
    kc = list(csv.reader(open(RAW / "kc_rstar.csv")))
    assert kc[1][2] == "Lower (68%)" and kc[1][3] == "Upper (68%)", kc[1]
    est.append(dict(plabel="Sep 2026", model="Glover–Oliyide (KC Fed)", value=float(kc[-1][1]), lo=float(kc[-1][2]), hi=float(kc[-1][3]),
                    band="68%", period=kc[-1][0][:7], concept="Medium run (5-yr-ahead VAR)", kind="trend"))
    # Cúrdia (SF Fed): Figure 1 medium-run median, 90% band; use 2026q3 row (letter text: "approximately 1.5%")
    r = sheet_rows(RAW / "el2026-22-figure-data.xlsx", "Figure 1")
    row = [x for x in r if x[0] == "2026q3"][0]
    # Published band is 90%; convert each side to ~68% assuming normality (68% half-width = 90% half-width / 1.6449).
    # Validated on Zaman, which publishes both: rule gives 0.80-2.16 vs published 68% 0.79-2.14 (2026Q3).
    v, lo90, hi90 = float(row[1]), float(row[2]), float(row[3])
    est.append(dict(plabel="2026Q3, projected; data to 2025Q4", model="Cúrdia (SF Fed)", value=v, lo=v - (v - lo90) / Z90, hi=v + (hi90 - v) / Z90,
                    band=f"≈68% (converted from published 90%: {lo90:.2f} to {hi90:.2f})",
                    period="2026Q3 (projected; data end 2025Q4)", concept="Medium run", kind="trend"))
    # Ferreira-Lott-Richards (Fed Board): US, latest half-year; no published band
    fr = list(csv.DictReader(open(RAW / "ferreira_rstar_values_feds_note.csv")))
    est.append(dict(plabel="2026 H2, in progress", model="Ferreira–Lott–Richards (Board)", value=float(fr[-1]["US"]), lo=None, hi=None, band="none published",
                    period=f"date_h {fr[-1]['date_h']} (2026 H2, in progress)", concept="Longer run", kind="trend"))
    # NY Fed DSGE: short-run r*, 2026 (Q4) mean and 68% band from the Sep 2026 Liberty Street table
    t = html.unescape(re.sub(r"<[^>]+>", " ", open(RAW / "libertystreet_nyfed_dsge_forecast_sep2026.html", errors="ignore").read()))
    m = re.search(r"Real natural rate of interest \(Q4\)\s+([\d.]+)\s+\(([-\d.]+),\s*([-\d.]+)\)", re.sub(r"\s+", " ", t))
    est.append(dict(plabel="short-run concept · 2026Q4, Sep forecast", model="NY Fed DSGE (short-run r*)", value=float(m.group(1)), lo=float(m.group(2)), hi=float(m.group(3)),
                    band="68%", period="2026 (Q4), Sep 2026 forecast", concept="Short run", kind="short"))
    return est


def load_real_rates():
    def fred_last(sid):
        obs = [o for o in json.load(open(ROOT / f"03_Data/Raw/fred_{sid}_{FRED_DATE}.json"))["observations"] if o["value"] != "."]
        return obs[-1]["date"], float(obs[-1]["value"])
    effr_d, effr = fred_last("EFFR")
    cle_d, cle = fred_last("EXPINF1YR")
    rates = [dict(measure="Cleveland Fed 1-yr expected inflation (headline CPI)", window="next 12 months", expinf=cle,
                  asof=cle_d, key="cle_cpi")]
    for var, lab in [("PCE", "headline PCE"), ("COREPCE", "core PCE"), ("CPI", "headline CPI")]:
        r = sheet_rows(SPF_FILE, var)
        last = r[-1]
        assert (int(last[0]), int(last[1])) == (2026, 4), last[:2]
        for w, (a, b) in SPF_WINDOWS.items():
            q = [float(last[1 + i]) for i in range(a, b + 1)]
            e = (prod((1 + x / 100) ** 0.25 for x in q) - 1) * 100
            rates.append(dict(measure=f"SPF Q4 2026 median, {lab}", window=w, expinf=e, asof="2026Q4 survey (Nov 16)",
                              key=f"spf_{var.lower()}_{w}"))
    for x in rates:
        x["effr"], x["effr_date"], x["real"] = effr, effr_d, effr - x["expinf"]
    return {x["key"]: x for x in rates}


def write_workbook(est, rates):
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "rstar"
    ws.append(["Model", "r* (real, %)", "Band low", "Band high", "Band type", "Period", "Concept", "Slide period label"])
    for e in sorted(est, key=lambda e: (e["kind"] == "short", e["value"])):
        ws.append([e["model"], round(e["value"], 3), None if e["lo"] is None else round(e["lo"], 3),
                   None if e["hi"] is None else round(e["hi"], 3), e["band"], e["period"], e["concept"], e["plabel"]])
    ws = wb.create_sheet("real_rates")
    ws.append(["Measure", "Window", "Expected inflation (%)", "As of", "EFFR (%)", "EFFR date", "Real fed funds (%)"])
    for x in rates.values():
        ws.append([x["measure"], x["window"], round(x["expinf"], 3), x["asof"], x["effr"], x["effr_date"], round(x["real"], 3)])
    ws = wb.create_sheet("slide_text")
    ws.append(["Version", "Field", "Text"])
    ws.append(["all", "heading", HEADING]); ws.append(["all", "note_line", NOTE_LINE]); ws.append(["all", "source", SOURCE])
    for k, lab in [("A", "A: CPI vs PCE (no bands)"), ("26Q4-27Q3", "B: headline vs core PCE, 2026Q4-27Q3"), ("27Q1-27Q4", "B-alt: headline vs core PCE, 2027Q1-Q4")]:
        ws.append([lab, "source_tail", TEXT[k]])
    ws = wb.create_sheet("notes")
    for line in [
        "Built by 02_Research/Subtasks/rstar_logan_match/code/build_rstar_slide.py from raw files in 03_Data/Raw/rstar_2026-11-16/, 03_Data/Raw/fred_*_2026-11-17.json and forecast_3b/raw/2026-11-16/medianLevel.xlsx.",
        "Real fed funds = EFFR minus expected inflation. SPF expected inflation = compounded average of quarterly annualized medians over the window.",
        f"Main SPF window: {MAIN_WINDOW} (survey quarter + next 3). Alternative 27Q1-27Q4 shown in real_rates.",
        "Bands: HLW/LW = ±1 S.E. of final obs. (≈68% if normal); LM 16th-84th pct.; Zaman, KC, DSGE 68%; Cúrdia ≈68% converted from its published 90% band (each side / 1.645, normality assumed; rule reproduces Zaman's published 68% from its 90% within 0.02); FLR none published.",
        "Concepts differ: DSGE is short-run r*; others are trend/medium/longer-run. Neutral zone shading = range of the seven non-DSGE point estimates.",
        "Logan (Nov 10) cited eight models, 1 to 1.85. Two endpoints (HLW low, Lubik-Matthes high) match the sources her speech links; five other models are candidates (values inside her range), not confirmed members. Her full eight-model list remains unidentified.",
    ]:
        ws.append([line])
    WB_OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(WB_OUT)


HEADING = "Real fed funds rate vs. published estimates of the neutral real rate (r*)"
NOTE_LINE = "Real fed funds rate = fed funds rate minus expected inflation over the coming year"
SOURCE = ("Source: NY Fed (HLW, Laubach–Williams: 2026Q2; DSGE short-run r* for 2026, Sep 18 forecast); Richmond Fed (Lubik–Matthes, 2026Q2); "
          "Cleveland Fed (Zaman, 2026Q3); KC Fed (Glover–Oliyide, Sep 2026); SF Fed (Cúrdia, 2026Q3 projection); Fed Board FEDS Note "
          "(Ferreira–Lott–Richards, 2026 H2); Philadelphia Fed SPF (Q4 2026 survey); FRED (EFFR, EXPINF1YR).")
TEXT = {}


def slide_texts(rates):
    cle = rates["cle_cpi"]
    out = {"A": (f"Real rate: EFFR {cle['effr']:.2f}% ({cle['effr_date']}) minus Cleveland Fed 1-yr expected CPI inflation "
                 f"{cle['expinf']:.2f}% (Nov) or SPF headline PCE {rates['spf_pce_26Q4-27Q3']['expinf']:.2f}% (2026Q4–2027Q3).")}
    for win, wl in [("26Q4-27Q3", "2026Q4–2027Q3"), ("27Q1-27Q4", "2027Q1–2027Q4")]:
        h, c = rates[f"spf_pce_{win}"], rates[f"spf_corepce_{win}"]
        out[win] = (f"Real rate: EFFR {h['effr']:.2f}% ({h['effr_date']}) minus SPF median expected inflation, {wl}: headline PCE "
                    f"{h['expinf']:.2f}%, core PCE {c['expinf']:.2f}%. Bars: 68% bands (±1 S.E. for HLW, LW); *Cúrdia converted from its published 90% band assuming normality; none published for FLR.")
    return out


def fmt(v):
    return f"{v:.2f}".replace("-", "−")


def draw(est, lines, path, bands, xlim, ticks, heading):
    fig = plt.figure(figsize=(13.33, 7.5), dpi=150)
    fig.patch.set_facecolor(BG)
    inch = fig.dpi_scale_trans
    W, H = 13.33, 7.5
    fig.add_artist(plt.Rectangle((0, 1 - 1.01 / H), 1, 1.01 / H, transform=fig.transFigure, color=NAVY, zorder=0))
    t1 = fig.text(0, H - 0.505, "Policy stance: ", transform=inch, ha="left", va="center", color=WHITE, family="Georgia", size=32)
    t2 = fig.text(0, H - 0.505, "[story the team writes]", transform=inch, ha="left", va="center", color=GOLD, family="Georgia", size=32)
    rend = fig.canvas.get_renderer()
    w1 = t1.get_window_extent(rend).width / fig.dpi
    w2 = t2.get_window_extent(rend).width / fig.dpi
    t1.set_x((W - w1 - w2) / 2); t2.set_x((W - w1 - w2) / 2 + w1)
    fig.text(W / 2, H - 1.40, heading, transform=inch, ha="center", va="center", color=NAVY, family="Georgia", size=21, weight="bold")
    # plot area
    x0, x1, y0, y1 = 4.05, 10.55, 2.05, 5.55
    ax = fig.add_axes([x0 / W, (H - y1) / H, (x1 - x0) / W, (y1 - y0) / H])
    ax.set_facecolor("none")
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS); ax.spines["bottom"].set_linewidth(1)
    ax.set_xlim(*xlim); ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.1f}%".replace("-", "−") for t in ticks], family="Arial", size=12, color=LABEL)
    ax.tick_params(axis="x", length=0, pad=6); ax.set_yticks([])
    order = sorted(est, key=lambda e: (e["kind"] == "short", e["value"]))
    n = len(order)
    ax.set_ylim(n - 0.3, -2.35)
    trend = [e["value"] for e in est if e["kind"] == "trend"]
    lo_z, hi_z = min(trend), max(trend)
    ax.axvspan(lo_z, hi_z, ymin=0, ymax=1, color=DNAVY, alpha=0.09, lw=0, zorder=0)
    ax.text((lo_z + hi_z) / 2, -2.05, f"Neutral zone {lo_z:.2f}–{hi_z:.2f}%", ha="center", va="center", family="Arial", size=12, color=DNAVY, weight="bold")
    ax.text(xlim[0] + 0.03 * (xlim[1] - xlim[0]), -2.05, "← Accommodative", ha="left", va="center", family="Arial", size=12, color=LABEL)
    ax.text(xlim[1] - 0.03 * (xlim[1] - xlim[0]), -2.05, "Restrictive →", ha="right", va="center", family="Arial", size=12, color=LABEL)
    for i, e in enumerate(order):
        short = e["kind"] == "short"
        if bands and e["lo"] is not None:
            ax.plot([e["lo"], e["hi"]], [i, i], color=GOLD if short else DNAVY, alpha=0.45 if short else 0.35, lw=6,
                    solid_capstyle="butt", ls="-", zorder=1)
        ax.scatter([e["value"]], [i], s=120, zorder=3, color=GOLD if short else DNAVY, edgecolor=DNAVY, linewidth=1.6)
        lab = e["model"].replace(" (short-run r*)", "")
        ax.annotate(lab + (" (short-run r*)" if short else ""), xy=(0, i), xycoords=("axes fraction", "data"), xytext=(-12, 0),
                    textcoords="offset points", ha="right", va="center", family="Arial", size=13, color=NAVY,
                    weight="bold" if short else "normal")
        if bands:
            band = "no band published" if e["lo"] is None else f"{fmt(e['lo'])} to {fmt(e['hi'])}" + ("*" if e["band"].startswith("≈68%") else "")
            ax.annotate(f"{e['value']:.2f}   [{band}]", xy=(1, i), xycoords=("axes fraction", "data"), xytext=(10, 0),
                        textcoords="offset points", ha="left", va="center", family="Arial", size=11.5, color=LABEL)
        else:
            ax.annotate(f"{e['value']:.2f}", xy=(e["value"], i), xytext=(10, 0), textcoords="offset points",
                        ha="left", va="center", family="Arial", size=11.5, color=LABEL)
    # policy-rate lines
    for j, (lab, val, style) in enumerate(lines):
        ax.plot([val, val], [n - 0.3, -0.55], color=RED, lw=3, ls=style, zorder=4)
        lab1 = lab.replace("\n", " ")
        ax.annotate(f"{lab1}: {val:.2f}%", xy=(val, -0.75), xytext=(-6 if j == 0 else 6, 0), textcoords="offset points",
                    ha=("right" if j == 0 else "left") if len(lines) > 1 else "center", va="center", family="Arial",
                    size=12.5, color=RED, weight="bold")
    return fig


def main():
    est = load_rstar()
    rates = load_real_rates()
    OUT.mkdir(parents=True, exist_ok=True)
    cle = rates["cle_cpi"]
    w = MAIN_WINDOW
    hp, cp = rates[f"spf_pce_{w}"], rates[f"spf_corepce_{w}"]
    global TEXT
    TEXT = slide_texts(rates)
    src = SOURCE
    take = "[Takeaway: one sentence the team writes]"
    heading = HEADING

    def finish(fig, path, note):
        fig.text(13.33 / 2, 7.5 - 1.78, NOTE_LINE, transform=fig.dpi_scale_trans, ha="center", va="center", family="Arial", size=13, color=NAVY)
        fig.text(0.73, 7.5 - 6.02, src + " " + note, transform=fig.dpi_scale_trans, ha="left", va="top", family="Arial", size=11,
                 color=SRC, wrap=True)
        fig.text(13.33 / 2, 7.5 - 6.95, take, transform=fig.dpi_scale_trans, ha="center", va="center", family="Georgia",
                 size=24, weight="bold", style="italic", color=NAVY)
        fig.savefig(path, facecolor=BG); plt.close(fig)

    # A: headline CPI (Cleveland) vs headline PCE (SPF), no bands
    fig = draw(est, [("Headline CPI\n(Cleveland Fed)", cle["real"], "-"), ("Headline PCE\n(SPF)", hp["real"], (0, (4, 2)))],
               OUT / "slide_A_cpi_vs_pce.png", bands=False, xlim=(0, 2.5), ticks=[0, 0.5, 1, 1.5, 2, 2.5], heading=heading)
    finish(fig, OUT / "slide_A_cpi_vs_pce.png",
           TEXT["A"])

    # B: SPF headline vs core PCE, with bands
    def make_b(win, path):
        h, c = rates[f"spf_pce_{win}"], rates[f"spf_corepce_{win}"]
        if abs(h["real"] - c["real"]) < 0.005:
            lines = [("Headline = core PCE\n(SPF)", h["real"], "-")]
        else:
            lo, hi = sorted([("Headline PCE\n(SPF)", h["real"], "-"), ("Core PCE\n(SPF)", c["real"], (0, (4, 2)))], key=lambda t: t[1])
            lines = [lo, hi]
        fig = draw(est, lines, path, bands=True, xlim=(-1, 3.5), ticks=[-1, 0, 1, 2, 3], heading=heading)
        wl = {"26Q4-27Q3": "2026Q4–27Q3", "27Q1-27Q4": "2027Q1–Q4"}[win]
        finish(fig, path, TEXT[win])
    make_b(MAIN_WINDOW, OUT / "slide_B_headline_vs_core_pce.png")
    make_b("27Q1-27Q4", OUT / "slide_B_alt_next4q.png")
    write_workbook(est, rates)

    for e in sorted(est, key=lambda e: e["value"]):
        print(f"{e['model']:34s} {e['value']:.3f}  [{e['lo'] if e['lo'] is None else round(e['lo'], 3)}, "
              f"{e['hi'] if e['hi'] is None else round(e['hi'], 3)}]  {e['band']:22s} {e['period']}")
    for x in rates.values():
        print(f"{x['measure']:52s} {x['window']:14s} exp {x['expinf']:.3f}  real {x['real']:.3f}")


if __name__ == "__main__":
    main()
