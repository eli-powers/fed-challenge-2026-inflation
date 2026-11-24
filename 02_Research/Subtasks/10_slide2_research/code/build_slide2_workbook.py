"""Build 01_Finals/data/Slide2_Inflation_Data.xlsx from the slide2_research outputs and their raw files.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/build_slide2_workbook.py"            # build
    python3 -I "02_Research/Subtasks/10_slide2_research/code/build_slide2_workbook.py" --verify   # build + LibreOffice recalc check

Design (GO.md): same two-layer design as slide 1. Research tabs first, grey raw_ tabs last. Research tabs use live
formulas back to the raw tabs wherever practical (leaf breadth, tagged breadth, attribution, breadth by measure, sticky/
flexible PCE breadth, Waller weighted/count, hospital m/m, PPI stage rates, oil); script-computed values from the agents'
outputs carry a cell note naming the CSV. Every formula cell has an expected value computed here (EXPECT), checked after a
LibreOffice recalculation (--verify). semantic_check() compares the live-formula values with the agents' CSVs.
Chart and verify helpers are reused from the slide 1 builder (rich_title, style_chart, line_style, finalize_chart,
add_chart, the put() overwrite guard). Fix inputs (outputs/*.csv, raw files), then rebuild. Do not hand-edit the xlsx
unless Eli has started doing so (then patch in place).
"""
import csv
import datetime as dt
import json
import os
import re
import statistics
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research')
OUT = os.path.join(SUB, 'outputs')
S1CODE = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code')
XLSX = os.environ.get('SLIDE2_OUT') or os.path.join(ROOT, '01_Finals', 'data', 'Slide2_Inflation_Data.xlsx')
SCRIPT = '10_slide2_research/code/build_slide2_workbook.py'
BUILD_DATE = dt.date.today().isoformat()
REL = lambda p: os.path.relpath(p, ROOT)

sys.path.insert(0, S1CODE)
import build_slide1_workbook as b1          # noqa: E402  (helpers only; b1.main() is never called)
import C_common as cc                      # noqa: E402  (audited breadth engine, read-only)
from openpyxl import Workbook, load_workbook   # noqa: E402
from openpyxl.chart import BarChart, LineChart, Reference, Series   # noqa: E402
from openpyxl.comments import Comment      # noqa: E402
from openpyxl.styles import Alignment, Font   # noqa: E402
from openpyxl.utils import get_column_letter   # noqa: E402

put, hdr_row, section, band, header, raw_meta = b1.put, b1.hdr_row, b1.section, b1.band, b1.header, b1.raw_meta
style_chart, line_style, add_chart = b1.style_chart, b1.line_style, b1.add_chart
FILL_EST, FILL_CF, FILL_KEY, F_BOLD = b1.FILL_EST, b1.FILL_CF, b1.FILL_KEY, b1.F_BOLD
FMT_RATE, FMT_BR = b1.FMT_RATE, b1.FMT_BR
EXPECT = b1.EXPECT
b1.TAB_COLORS.update({'README': '1F3864', 'Attribution': 'C00000', 'Tagged_breadth': 'C00000', 'Breadth_measures': 'BF8F00',
                      'Sticky_flexible': 'BF8F00', 'Waller': 'BF8F00', 'Hospital_base_effect': '7030A0', 'PPI_stages': '2F5597',
                      'External': '2F5597', 'Slide_worthiness': '548235', 'Sources': '1F3864', 'Judgment_calls_and_paywalled': 'FF0000'})
SEMANTIC = []   # (sheet, coord, expected_from_csv, label)


def note(cell, text):
    cell.comment = Comment(text, 'build_slide2_workbook.py', width=340, height=120)


def rd(name):
    p = name if os.path.isabs(name) else os.path.join(OUT, name)
    with open(p, newline='') as f:
        return list(csv.DictReader(f))


num = b1.num
GROUPS = ['energy', 'tariff', 'AI', 'untagged']
LPM = ['2025-09', '2025-10', '2026-06', '2026-07', '2026-09', '2026-10']
WM = ['2025-09', '2025-10', '2026-06', '2026-07']
# (period, horizon) -> (rate key, weight key)
WIN = {('2026-09', '12m'): ('r12s', 'w12s'), ('2026-09', '3m'): ('r3s', 'w3s'),
       ('2026-10', '12m'): ('r12o', 'w12o'), ('2026-10', '3m'): ('r3o', 'w3o')}


def months(a, b):
    return list(b1.months(a, b))


# ============================================================================ raw tabs
def build_raw_leaves(ws):
    tags = rd(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
    tag = {int(re.search(r'line (\d+)', x['component_id']).group(1)): x['tag_final'] for x in tags}
    sticky = {int(x['leaf']): (x['class_primary_leave_out_mixed'] or 'unclassified') for x in rd('B_q5_mapping.csv')}
    assert set(tag) == set(cc.LEAVES_CORE) == set(sticky), 'leaf sets differ'
    raw_meta(ws, 'BEA PCE detail: the 149 core leaves with shock tags, scope flags and sticky/flexible class', [
        ('Source files', f'{cc.U20404_REL}; {cc.U20405_REL}; Oct 2026 est. from 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv; '
                         'tags: 02_Research/Subtasks/08_shock_tagging/proposed_tags.csv (tag_final); sticky class: outputs/B_q5_mapping.csv (class_primary_leave_out_mixed)'),
        ('URL', 'https://apps.bea.gov/api/data (NIUnderlyingDetail U20404 / U20405, monthly)'),
        ('Vintage', 'BEA Oct 29, 2026 release (data through Sep 2026), files saved 2026-11-10; Oct 2026 = UMD est. (built 2026-11-13)'),
        ('Notes', 'P_* = U20404 index (2017=100, SA). W_* = leaf nominal $ (millions, SAAR) at the base month of each window. P_2026-10 est. via '
                  'C_common.index_level(leaf, "2026-10", "leaf"). Scope: goods = line < 150, services = line >= 150; supercore = services ex housing 153-164 '
                  '(C_common.is_supercore_leaf). Sticky class: Bryan-Meyer (2010) groups via the BLS PCE-CPI concordance; "unclassified" = PPI/non-CPI priced or mixed.')])
    leaf_desc = {}
    for r_ in b1.bea(os.path.join(ROOT, cc.U20404_REL))[0]:
        leaf_desc.setdefault(int(r_['LineNumber']), r_['LineDescription'])
    cols = ['leaf', 'name', 'tag_final', 'scope', 'supercore'] + ['sticky_class'] + [f'P_{m}' + (' est.' if m == '2026-10' else '') for m in LPM] + [f'W_{m}' for m in WM]
    hdr_row(ws, 6, 1, cols, [7, 40, 10, 9, 9, 12] + [11] * 6 + [13] * 4)
    ROW, V = {}, {}
    for i, lf in enumerate(cc.LEAVES_CORE):
        lf = int(lf)
        rr = 7 + i
        vals = [lf, leaf_desc.get(lf, ''), tag[lf], 'services' if lf >= 150 else 'goods', 1 if cc.is_supercore_leaf(lf) else 0, sticky[lf]] + \
               [float(cc.index_level(lf, m, 'leaf')) for m in LPM] + [float(cc.nominal_weight(lf, lf, m, 'leaf')) for m in WM]
        for j, v in enumerate(vals):
            put(ws, rr, 1 + j, v, b1.FMT_LVL if 6 <= j < 12 else ('#,##0' if j >= 12 else None), fill=FILL_EST if j == 11 else None)
        ROW[lf] = rr
        V[lf] = dict(zip(['leaf', 'name', 'tag', 'scope', 'supercore', 'sticky'] + [f'P_{m}' for m in LPM] + [f'W_{m}' for m in WM], vals))
    ws.freeze_panes = 'C7'
    return ROW, V


def bls_series(paths, ids):
    out = {}
    for p in paths:
        j = json.load(open(p))
        for s in j['Results']['series']:
            if s['seriesID'] in ids:
                for o in s['data']:
                    if o['period'].startswith('M') and o['period'] != 'M13':
                        out[(s['seriesID'], f"{o['year']}-{o['period'][1:]}")] = (float(o['value']), ';'.join(f['code'] for f in o.get('footnotes', []) if f and f.get('code')))
    return out


PPI_IDS = [('WPSFD4', 'Final demand'), ('WPSFD49116', 'Final demand less foods, energy and trade services (core FD; S2-E10)'), ('WPSID51', 'Stage 1 intermediate demand (production flow)'), ('WPSID52', 'Stage 2 intermediate demand (production flow)'),
           ('WPSID53', 'Stage 3 intermediate demand'), ('WPSID54', 'Stage 4 intermediate demand'),
           ('WPSID61', 'Processed goods for intermediate demand (commodity type)'), ('WPSID62', 'Unprocessed goods for intermediate demand (commodity type)')]
PPI_DIR = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_stages_2026-11-15')


def build_raw_ppi(ws):
    paths = sorted(os.path.join(PPI_DIR, f) for f in os.listdir(PPI_DIR) if f.startswith('bls_api_ppi_stages') and f.endswith('.json'))
    d = bls_series(paths, {i for i, _ in PPI_IDS})
    raw_meta(ws, 'BLS PPI: final demand, intermediate demand by production flow (stages 1-4) and by commodity type (ID61, ID62), SA monthly index', [
        ('Source files', '; '.join(REL(p) for p in paths)),
        ('URL', 'https://api.bls.gov/publicAPI/v2/timeseries/data/ (series WPSFD4, WPSID51-54, WPSID61, WPSID62)'),
        ('Vintage', 'pulled 2026-11-15 (Oct 2026 PPI released 2026-11-13); Jul-Oct 2026 preliminary (BLS footnote P)'),
        ('Notes', 'Label check (Agent C): WPSID51-54 are the production-flow STAGES; WPSID61-64 are by COMMODITY TYPE (ID62 = unprocessed goods), not stages.')])
    ms = months((2017, 1), (2026, 10))
    hdr_row(ws, 6, 1, ['Month'] + [f'{i} {t}' for i, t in PPI_IDS] + ['footnote (WPSID51)'], [10] + [16] * len(PPI_IDS) + [12])
    ROW, V = {}, {}
    for k, m in enumerate(ms):
        rr = 7 + k
        put(ws, rr, 1, m)
        for j, (sid, _) in enumerate(PPI_IDS):
            v = d[(sid, m)][0]
            put(ws, rr, 2 + j, v, '0.000')
            V[(sid, m)] = v
        put(ws, rr, 2 + len(PPI_IDS), d[('WPSID51', m)][1])
        ROW[m] = rr
    ws.freeze_panes = 'B7'
    return ROW, V, ms


def build_raw_oil(ws):
    rows = {}
    for sid, key in (('DCOILBRENTEU', 'brent'), ('DCOILWTICO', 'wti')):
        p = os.path.join(ROOT, '03_Data', 'Raw', 'EIA_FRED_oil_daily_2026-11-15', f'FRED_{sid}_obs_2026-11-15.json')
        for o in json.load(open(p))['observations']:
            if '2026-09-01' <= o['date'] <= '2026-11-30' and o['value'] not in ('.', ''):
                rows.setdefault(o['date'], {})[key] = float(o['value'])
    rows = {k: v for k, v in rows.items() if 'brent' in v and 'wti' in v}   # trading days with both quotes
    raw_meta(ws, 'Daily oil spot prices, Brent and WTI ($/bbl), Sep 1 - Nov 11, 2026', [
        ('Source files', '03_Data/Raw/EIA_FRED_oil_daily_2026-11-15/FRED_DCOILBRENTEU_obs_2026-11-15.json; FRED_DCOILWTICO_obs_2026-11-15.json (EIA RBRTE/RWTC xls in the same folder are identical)'),
        ('URL', 'https://fred.stlouisfed.org/series/DCOILBRENTEU ; https://fred.stlouisfed.org/series/DCOILWTICO (source: EIA)'),
        ('Vintage', 'retrieved 2026-11-15; last observation 2026-11-11'),
        ('Notes', 'Oct PPI pricing date: Tuesday of the week containing the 13th (Oct 13, 2026), per BLS Handbook of Methods (Agent C).')])
    hdr_row(ws, 6, 1, ['Date', 'Brent', 'WTI'], [12, 10, 10])
    ROW, V = {}, {}
    for k, dte in enumerate(sorted(rows)):
        rr = 7 + k
        put(ws, rr, 1, dte)
        put(ws, rr, 2, rows[dte].get('brent'), '0.00')
        put(ws, rr, 3, rows[dte].get('wti'), '0.00')
        ROW[dte] = rr
        V[dte] = rows[dte]
    return ROW, V


def build_raw_hospital(ws):
    p = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_hospitals_2026-11-15', 'bls_api_ppi_hospitals_2016_2026.json')
    d = bls_series([p], {'PCU622---622---', 'WPU5121010111'})
    raw_meta(ws, 'Hospital prices: BLS PPI hospitals (NSA) and Medicare inpatient sub-index; BEA PCE leaf 184 index (SA)', [
        ('Source files', f'{REL(p)}; {cc.U20404_REL} (leaf 184, nonprofit hospitals; 185-186 share the same PPI source); Oct 2026 leaf = UMD est.'),
        ('URL', 'https://api.bls.gov/publicAPI/v2/timeseries/data/PCU622---622--- ; https://apps.bea.gov/api/data (U20404)'),
        ('Vintage', 'BLS pulled 2026-11-15 (Oct 2026 preliminary); BEA Oct 29, 2026 release; ALFRED first-release vintage of the Oct 2025 PPI value = 2026-01-14 (248.009)'),
        ('Notes', 'October 2025 PPI was collected late (shutdown) and published with November on Jan 14, 2026; BLS: response rates "within the normal range" (Agent B, Q7).')])
    ms = months((2017, 12), (2026, 10))
    hdr_row(ws, 6, 1, ['Month', 'PPI hospitals PCU622---622--- (NSA)', 'PPI Medicare inpatient WPU5121010111 (NSA)', 'BEA leaf 184 index (SA)'], [10, 18, 18, 16])
    ROW, V = {}, {}
    for k, m in enumerate(ms):
        rr = 7 + k
        lv = float(cc.index_level(184, m, 'leaf'))
        vals = [m, d[('PCU622---622---', m)][0], d.get(('WPU5121010111', m), (None,))[0], lv]
        for j, v in enumerate(vals):
            put(ws, rr, 1 + j, v, '0.000' if j else None, fill=FILL_EST if (m == '2026-10' and j == 3) else None)
        ROW[m] = rr
        V[m] = dict(ppi=vals[1], med=vals[2], leaf=lv)
    return ROW, V, ms


def build_raw_ts(ws):
    bts = [x for x in rd('B_q4_breadth_ts.csv') if re.fullmatch(r'\d{4}-\d{2}', x['month'])]
    ats = [x for x in rd('A_q3_tagged_breadth_ts.csv') if re.fullmatch(r'\d{4}-\d{2}', x['month'])]
    assert [x['month'] for x in bts] == [x['month'] for x in ats] and bts[-1]['month'] == '2026-10'
    raw_meta(ws, 'Breadth time series (script outputs): by measure (Agent B) and by shock tag (Agent A), weighted leaf, monthly 2018-01 to 2026-10', [
        ('Source files', '02_Research/Subtasks/10_slide2_research/outputs/B_q4_breadth_ts.csv; outputs/A_q3_tagged_breadth_ts.csv'),
        ('URL', 'n/a (computed by code/B_q4_*.py and code/A_q3_*.py from BEA U20404/U20405 through C_common.py)'),
        ('Vintage', 'BEA Oct 29, 2026 release; 2026-10 = UMD est.'),
        ('Notes', 'Share of weight with rate > 3%; start-of-window weights (t-3 for 3m ann., t-12 for 12m). Within-group = % of the group\'s own weight.')])
    bcols = ['core_12m_leaf', 'supercore_12m_leaf', 'core_goods_12m_leaf', 'core_services_12m_leaf', 'headline_backup_12m_leaf',
             'core_3m_ann_leaf', 'supercore_3m_ann_leaf', 'core_goods_3m_ann_leaf', 'core_services_3m_ann_leaf', 'headline_backup_3m_ann_leaf']
    acols = [f'{g}_within_12m' for g in GROUPS] + [f'{g}_within_3m_ann' for g in GROUPS]
    hdr_row(ws, 6, 1, ['Month', 'Status'] + bcols + acols, [10, 12] + [12] * (len(bcols) + len(acols)))
    COL = {c: 3 + j for j, c in enumerate(bcols + acols)}
    ROW = {}
    for k, (x, y) in enumerate(zip(bts, ats)):
        rr = 7 + k
        est = x['month'] == '2026-10'
        put(ws, rr, 1, x['month'] + (' est.' if est else ''), fill=FILL_EST if est else None)
        put(ws, rr, 2, x['status'])
        for c in bcols:
            put(ws, rr, COL[c], num(x[c]), FMT_BR, fill=FILL_EST if est else None)
        for c in acols:
            put(ws, rr, COL[c], num(y[c]), FMT_BR, fill=FILL_EST if est else None)
        ROW[x['month']] = rr
    return ROW, COL, {x['month']: x for x in bts}, {y['month']: y for y in ats}


# ============================================================================ leaf calc block (Tagged_breadth, below the tables)
def build_leaf_calc(ws, LROW, LV, L0):
    """One row per core leaf: live rates and start-of-window weights over raw_PCE_leaves. Returns ranges and Python values."""
    R = 'raw_PCE_leaves!'
    first = L0 + 1
    calc = {}
    section(ws, L0 - 1, f'Leaf-level calculation: 149 core leaves (rows {first}-{first + len(LROW) - 1}); live formulas over raw_PCE_leaves. Oct = UMD est.')
    hdr_row(ws, L0, 1, ['Leaf', 'Tag', 'Scope', 'Supercore', 'Sticky class', 'Sep 12m %', 'Sep 3m ann. %', 'Oct 12m % (est.)', 'Oct 3m ann. % (est.)',
                        'W Sep 2025', 'W Jun 2026', 'W Oct 2025', 'W Jul 2026'])
    for i, lf in enumerate(LROW):
        rr = first + i
        p, pr = LV[lf], LROW[lf]
        c = dict(r12s=(p['P_2026-09'] / p['P_2025-09'] - 1) * 100, r3s=((p['P_2026-09'] / p['P_2026-06']) ** 4 - 1) * 100,
                 r12o=(p['P_2026-10'] / p['P_2025-10'] - 1) * 100, r3o=((p['P_2026-10'] / p['P_2026-07']) ** 4 - 1) * 100,
                 w12s=p['W_2025-09'], w3s=p['W_2026-06'], w12o=p['W_2025-10'], w3o=p['W_2026-07'],
                 tag=p['tag'], scope=p['scope'], sc=p['supercore'], st=p['sticky'], row=rr)
        calc[lf] = c
        put(ws, rr, 1, f'={R}A{pr}', expect=lf)
        put(ws, rr, 2, f'={R}C{pr}', expect=c['tag'])
        put(ws, rr, 3, f'={R}D{pr}', expect=c['scope'])
        put(ws, rr, 4, f'={R}E{pr}', expect=c['sc'])
        put(ws, rr, 5, f'={R}F{pr}', expect=c['st'])
        put(ws, rr, 6, f'=({R}K{pr}/{R}G{pr}-1)*100', FMT_RATE, expect=c['r12s'])
        put(ws, rr, 7, f'=(({R}K{pr}/{R}I{pr})^4-1)*100', FMT_RATE, expect=c['r3s'])
        put(ws, rr, 8, f'=({R}L{pr}/{R}H{pr}-1)*100', FMT_RATE, expect=c['r12o'], fill=FILL_EST)
        put(ws, rr, 9, f'=(({R}L{pr}/{R}J{pr})^4-1)*100', FMT_RATE, expect=c['r3o'], fill=FILL_EST)
        put(ws, rr, 10, f'={R}M{pr}', '#,##0', expect=c['w12s'])
        put(ws, rr, 11, f'={R}O{pr}', '#,##0', expect=c['w3s'])
        put(ws, rr, 12, f'={R}N{pr}', '#,##0', expect=c['w12o'])
        put(ws, rr, 13, f'={R}P{pr}', '#,##0', expect=c['w3o'])
    last = first + len(LROW) - 1
    rng = lambda col: f"Tagged_breadth!${col}${first}:${col}${last}"
    RNG = dict(tag=rng('B'), scope=rng('C'), sc=rng('D'), st=rng('E'), r12s=rng('F'), r3s=rng('G'), r12o=rng('H'), r3o=rng('I'),
               w12s=rng('J'), w3s=rng('K'), w12o=rng('L'), w3o=rng('M'))
    return calc, RNG, last


def py_share(calc, rk, wk, sel=lambda c: True, thr=3.0, denom_all=False):
    den = sum(c[wk] for c in calc.values() if (True if denom_all else sel(c)))
    return 100 * sum(c[wk] for c in calc.values() if sel(c) and c[rk] > thr) / den


# ============================================================================ research tabs
def build_tagged(ws, LROW, LV):
    header(ws, 'Tagged breadth: share of each shock group\'s spending with inflation above 3%',
           'Weighted-leaf breadth inside each tag group (energy, tariff, AI, untagged) and each group\'s contribution to all-core breadth; Sep 2026 vs Oct 2026 est.; '
           'decomposition of the Oct 12m change by tag; sensitivities; monthly series. Data only.',
           'Units: % of group weight (within) or pp of core weight (contribution). Start-of-window weights. BEA U20404/U20405 Oct 29, 2026 release; Oct = UMD est. '
           'Draws on raw_PCE_leaves (leaf block below, live) and raw_breadth_ts (series).')
    L0 = 120
    calc, RNG, last = build_leaf_calc(ws, LROW, LV, L0)
    A3 = {(x['period'], 'm3' if x['horizon'] == '3m_ann' else '12m', x['group']): x for x in rd('A_q3_tagged_breadth.csv')}
    hdr_row(ws, 5, 1, ['Group', 'n leaves', 'Weight share % (Sep 12m window)', 'Within 12m Sep', 'Within 12m Oct est.', 'Within 3m Sep', 'Within 3m Oct est.',
                       'Contrib 12m Sep (pp)', 'Contrib 12m Oct est. (pp)', 'Contrib 3m Sep (pp)', 'Contrib 3m Oct est. (pp)'],
            [26, 9, 13, 11, 11, 11, 11, 12, 12, 12, 12])
    rr = 6
    for g in GROUPS + ['ALL CORE']:
        sel = (lambda c, g=g: c['tag'] == g) if g != 'ALL CORE' else (lambda c: True)
        cond = f'({RNG["tag"]}="{g}")*' if g != 'ALL CORE' else ''
        put(ws, rr, 1, g, bold=g == 'ALL CORE')
        put(ws, rr, 2, f'=COUNTIF({RNG["tag"]},"{g}")' if g != 'ALL CORE' else f'=COUNT({RNG["r12s"]})', expect=sum(1 for c in calc.values() if sel(c)))
        put(ws, rr, 3, f'=SUMPRODUCT({cond}{RNG["w12s"]})/SUM({RNG["w12s"]})*100', FMT_BR, expect=100 * sum(c['w12s'] for c in calc.values() if sel(c)) / sum(c['w12s'] for c in calc.values()))
        for j, (per, hz) in enumerate([('2026-09', '12m'), ('2026-10', '12m'), ('2026-09', '3m'), ('2026-10', '3m')]):
            rk, wk = WIN[(per, hz)]
            v = py_share(calc, rk, wk, sel)
            put(ws, rr, 4 + j, f'=SUMPRODUCT({cond}({RNG[rk]}>3)*{RNG[wk]})/SUMPRODUCT({cond}{RNG[wk]})*100' if cond else
                f'=SUMPRODUCT(({RNG[rk]}>3)*{RNG[wk]})/SUM({RNG[wk]})*100', FMT_BR, expect=v,
                fill=FILL_EST if per == '2026-10' else (FILL_KEY if g == 'ALL CORE' else None))
            vc = py_share(calc, rk, wk, sel, denom_all=True)
            put(ws, rr, 8 + j, f'=SUMPRODUCT({cond}({RNG[rk]}>3)*{RNG[wk]})/SUM({RNG[wk]})*100', FMT_RATE, expect=vc, fill=FILL_EST if per == '2026-10' else None)
            if g != 'ALL CORE':
                a = A3[(per, 'm3' if hz == '3m' else '12m', g)]
                SEMANTIC.append(('Tagged_breadth', f'{get_column_letter(4 + j)}{rr}', num(a['breadth_within_group_pct']), f'A_q3 within {g} {per} {hz}'))
                SEMANTIC.append(('Tagged_breadth', f'{get_column_letter(8 + j)}{rr}', num(a['contribution_to_core_breadth_pp']), f'A_q3 contrib {g} {per} {hz}'))
        rr += 1
    cr = rr - 1
    for col, want in ((4, 60.626), (5, 54.038), (6, 44.814), (7, 45.467)):
        SEMANTIC.append(('Tagged_breadth', f'{get_column_letter(col)}{cr}', want, 'slide 1 reproduction check'))
    # untagged ex hospitals
    selx = lambda c: c['tag'] == 'untagged' and c['row'] not in [calc[h]['row'] for h in (184, 185, 186)]
    hrows = [calc[h]['row'] for h in (184, 185, 186)]
    assert all(calc[h]['tag'] == 'untagged' for h in (184, 185, 186))
    put(ws, rr, 1, 'untagged ex hospital leaves 184-186')
    for j, (per, hz) in enumerate([('2026-09', '12m'), ('2026-10', '12m'), ('2026-09', '3m'), ('2026-10', '3m')]):
        rk, wk = WIN[(per, hz)]
        rc, wc = RNG[rk].split('!')[1].replace('$', '').split(':')[0][0], RNG[wk].split('!')[1].replace('$', '').split(':')[0][0]
        sub_n = '-'.join(f'({rc}{h}>3)*{wc}{h}' for h in hrows)
        sub_d = '-'.join(f'{wc}{h}' for h in hrows)
        put(ws, rr, 4 + j, f'=(SUMPRODUCT(({RNG["tag"]}="untagged")*({RNG[rk]}>3)*{RNG[wk]})-{sub_n})/(SUMPRODUCT(({RNG["tag"]}="untagged")*{RNG[wk]})-{sub_d})*100',
            FMT_BR, expect=py_share(calc, rk, wk, selx), fill=FILL_EST if per == '2026-10' else None)
    rr += 1
    band(ws, 6, rr - 1, 1, 11)
    put(ws, rr, 1, 'Tags: 08_shock_tagging/proposed_tags.csv tag_final (Eli, Nov 14): energy = top quartile of core weight by I-O energy share (E >= 3.47%); tariff = goods with direct import share >= 15%; AI = leaves 49, 50, 51, 71. One tag per leaf.')
    # ---- Oct 12m change by tag (live)
    rr += 2
    section(ws, rr, 'Oct 12m breadth change (Sep -> Oct est.) by tag group, pp of core weight; sums to the all-core change')
    rr += 1
    hdr_row(ws, rr, 1, ['Group', 'Change (pp)', 'Agent A CSV'])
    D = {x['group']: x for x in rd('A_q3_oct12m_drop_by_tag.csv')}
    tw_s, tw_o = sum(c['w12s'] for c in calc.values()), sum(c['w12o'] for c in calc.values())

    def chg(sel):
        return sum(100 * (c['w12o'] * (c['r12o'] > 3) / tw_o - c['w12s'] * (c['r12s'] > 3) / tw_s) for c in calc.values() if sel(c))
    d0 = rr + 1
    for g in GROUPS:
        rr += 1
        put(ws, rr, 1, g)
        put(ws, rr, 2, f'=(SUMPRODUCT(({RNG["tag"]}="{g}")*({RNG["r12o"]}>3)*{RNG["w12o"]})/SUM({RNG["w12o"]})-SUMPRODUCT(({RNG["tag"]}="{g}")*({RNG["r12s"]}>3)*{RNG["w12s"]})/SUM({RNG["w12s"]}))*100',
            FMT_RATE, expect=chg(lambda c, g=g: c['tag'] == g), fill=FILL_KEY if g == 'untagged' else None)
        put(ws, rr, 3, num(D[g]['change_pp']), FMT_RATE)
        SEMANTIC.append(('Tagged_breadth', f'B{rr}', num(D[g]['change_pp']), f'A_q3 drop {g}'))
    rr += 1
    put(ws, rr, 1, 'of which hospital leaves 184-186 (untagged)')
    terms = '+'.join(f'(H{h}>3)*L{h}/SUM({RNG["w12o"]})-(F{h}>3)*J{h}/SUM({RNG["w12s"]})' for h in hrows)
    put(ws, rr, 2, f'=({terms})*100', FMT_RATE, expect=chg(lambda c: c['row'] in hrows), fill=FILL_KEY)
    hk = [k for k in D if k.startswith('hospital')][0]
    put(ws, rr, 3, num(D[hk]['change_pp']), FMT_RATE)
    rr += 1
    put(ws, rr, 1, 'Total (all core)', bold=True)
    put(ws, rr, 2, f'=SUM(B{d0}:B{d0 + 3})', FMT_RATE, expect=chg(lambda c: True))
    # ---- sensitivities (script values)
    rr += 2
    section(ws, rr, 'Sensitivities (Agent A, A_q3_sensitivity.csv): energy group under alternative rules, 12m Sep 2026 (script values)')
    rr += 1
    hdr_row(ws, rr, 1, ['Scheme', 'Group', 'n leaves', 'Weight share %', 'Within-group breadth', 'Contribution (pp)', 'Share of above-target (method a)'])
    for x in rd('A_q3_sensitivity.csv'):
        if x['period'] == '2026-09' and x['horizon'] == '12m' and x['group'] == 'energy':
            rr += 1
            put(ws, rr, 1, x['scheme'])
            put(ws, rr, 2, x['group'])
            put(ws, rr, 3, num(x['n_leaves']))
            put(ws, rr, 4, num(x['weight_share_pct']), FMT_BR)
            put(ws, rr, 5, num(x['breadth_within_group_pct']), FMT_BR)
            put(ws, rr, 6, num(x['contribution_to_core_breadth_pp']), FMT_RATE)
            c = put(ws, rr, 7, num(x['share_of_above_target_a']), '0.0%')
            note(c, 'Value from outputs/A_q3_sensitivity.csv (code/A_q3_*.py).')
    # ---- time series (formulas to raw_breadth_ts) and chart
    return calc, RNG, rr


def ts_block(ws, T0, TROW, TCOL, cols, labels, title, avg=True):
    """copy monthly series from raw_breadth_ts with live formulas; optional 2018-19 averages. Returns (first,last) rows."""
    hdr_row(ws, T0, 1, ['Month'] + labels + ([f'2018-19 avg: {labels[0]}'] if avg else []))
    ms = list(TROW)
    first = T0 + 1
    pre = [m for m in ms if m < '2020-01']
    for k, m in enumerate(ms):
        rr = first + k
        put(ws, rr, 1, f'=raw_breadth_ts!A{TROW[m]}', expect=m + (' est.' if m == '2026-10' else ''), fill=FILL_EST if m == '2026-10' else None)
        for j, c in enumerate(cols):
            put(ws, rr, 2 + j, f'=raw_breadth_ts!{get_column_letter(TCOL[c])}{TROW[m]}', FMT_BR, expect=TV[(m, c)], fill=FILL_EST if m == '2026-10' else None)
        if avg:
            put(ws, rr, 2 + len(cols), f'=AVERAGE(raw_breadth_ts!{get_column_letter(TCOL[cols[0]])}{TROW[pre[0]]}:{get_column_letter(TCOL[cols[0]])}{TROW[pre[-1]]})', FMT_BR,
                expect=statistics.mean(TV[(m, cols[0])] for m in pre))
    section(ws, T0 - 1, title)
    return first, first + len(ms) - 1


TV = {}


def line_chart(ws, first, last, cols, colors, title, ytitle, source, anchor, dashes=None, skip=12, w=24, h=11):
    ch = LineChart()
    style_chart(ch, title, ytitle, 'Month', source, w=w, h=h, yfmt='0')
    for k, (col, color) in enumerate(zip(cols, colors)):
        s = Series(Reference(ws, min_col=col, min_row=first, max_row=last), title=ws.cell(row=first - 1, column=col).value)
        line_style(s, color, dash=(dashes or {}).get(col), width_pt=2.0 if k == 0 else 1.5)
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=first, max_row=last))
    ch.x_axis.tickLblSkip = skip
    add_chart(ws, ch, anchor)


def bar_chart(ws, r0, r1, cats_col, cols, colors, title, ytitle, xtitle, source, anchor, w=18, h=10, yfmt='0'):
    bc = BarChart()
    bc.type = 'col'
    style_chart(bc, title, ytitle, xtitle, source, w=w, h=h, yfmt=yfmt)
    for col in cols:
        bc.add_data(Reference(ws, min_col=col, min_row=r0 - 1, max_row=r1), titles_from_data=True)
    for s_, color in zip(bc.series, colors):
        s_.graphicalProperties.solidFill = color
        s_.graphicalProperties.line.solidFill = color
    bc.set_categories(Reference(ws, min_col=cats_col, min_row=r0, max_row=r1))
    add_chart(ws, bc, anchor)


def build_attribution(ws, calc, RNG):
    header(ws, 'Attribution: shares of above-target core PCE (core minus 2%) by shock group, compared with Bowman',
           'Group contribution C_g = sum over the group\'s leaves of (start-of-window weight share x leaf rate), no cutoff. Three ways to allocate the 2% target; Sep 2026 published vs Oct 2026 est.; 12m and 3m ann. Data only.',
           'Units: pp (contributions) and % of total above-target. Live formulas over the Tagged_breadth leaf block (raw_PCE_leaves). Methods: '
           '(a) C_g - 2 x weight share (central); (b) only leaves above 2% count, sum of share x (rate - 2); (c) whole 2% charged to untagged.')
    A = {(x['period'], x['horizon'], x['method'], x['group']): x for x in rd('A_q2_attribution.csv')}
    hdr_row(ws, 5, 1, ['Period', 'Horizon', 'Group', 'Weight share', 'Contribution C_g (pp)', 'Group rate %', '(a) above-target pp', '(a) share %',
                       '(b) above-target pp', '(b) share %', '(c) above-target pp', '(c) share %'], [12, 9, 12, 10, 12, 10, 12, 10, 12, 10, 12, 10])
    rr = 6
    KEY = {}
    for per in ('2026-09', '2026-10'):
        for hz, hk in (('12m', '12m'), ('3m', '3m_ann')):
            rk, wk = WIN[(per, hz)]
            tw = sum(c[wk] for c in calc.values())
            py = {}
            for g in GROUPS:
                s = sum(c[wk] for c in calc.values() if c['tag'] == g) / tw
                C = sum(c[wk] * c[rk] for c in calc.values() if c['tag'] == g) / tw
                b = sum(c[wk] * (c[rk] - 2) for c in calc.values() if c['tag'] == g and c[rk] > 2) / tw
                py[g] = dict(s=s, C=C, a=C - 2 * s, b=b, c=C - 2 if g == 'untagged' else C)
            tot = {k: sum(py[g][k] for g in GROUPS) for k in ('a', 'b', 'c')}
            r0 = rr
            for g in GROUPS:
                est = per == '2026-10'
                put(ws, rr, 1, per + (' est.' if est else ''), fill=FILL_EST if est else None)
                put(ws, rr, 2, hz + (' ann.' if hz == '3m' else ''))
                put(ws, rr, 3, g)
                cond = f'({RNG["tag"]}="{g}")'
                put(ws, rr, 4, f'=SUMPRODUCT({cond}*{RNG[wk]})/SUM({RNG[wk]})', '0.0000', expect=py[g]['s'])
                put(ws, rr, 5, f'=SUMPRODUCT({cond}*{RNG[wk]}*{RNG[rk]})/SUM({RNG[wk]})', '0.000', expect=py[g]['C'])
                put(ws, rr, 6, f'=E{rr}/D{rr}', FMT_RATE, expect=py[g]['C'] / py[g]['s'])
                put(ws, rr, 7, f'=E{rr}-2*D{rr}', '0.000', expect=py[g]['a'])
                put(ws, rr, 8, f'=G{rr}/SUM(G${r0}:G${r0 + 3})*100', FMT_BR, expect=100 * py[g]['a'] / tot['a'], fill=FILL_KEY if hz == '12m' else None)
                put(ws, rr, 9, f'=SUMPRODUCT({cond}*({RNG[rk]}>2)*{RNG[wk]}*({RNG[rk]}-2))/SUM({RNG[wk]})', '0.000', expect=py[g]['b'])
                put(ws, rr, 10, f'=I{rr}/SUM(I${r0}:I${r0 + 3})*100', FMT_BR, expect=100 * py[g]['b'] / tot['b'])
                put(ws, rr, 11, f'=E{rr}-2' if g == 'untagged' else f'=E{rr}', '0.000', expect=py[g]['c'])
                put(ws, rr, 12, f'=K{rr}/SUM(K${r0}:K${r0 + 3})*100', FMT_BR, expect=100 * py[g]['c'] / tot['c'])
                for col, m in ((8, 'a'), (10, 'b'), (12, 'c')):
                    SEMANTIC.append(('Attribution', f'{get_column_letter(col)}{rr}', 100 * num(A[(per, hk, m, g)]['share_of_above_target']), f'A_q2 {per} {hz} {m} {g}'))
                KEY[(per, hz, g)] = rr
                rr += 1
            put(ws, rr, 3, 'Total / leaf-sum S', bold=True)
            put(ws, rr, 5, f'=SUM(E{r0}:E{rr - 1})', '0.000', expect=sum(py[g]['C'] for g in GROUPS))
            put(ws, rr, 7, f'=SUM(G{r0}:G{rr - 1})', '0.000', expect=tot['a'])
            put(ws, rr, 9, f'=SUM(I{r0}:I{rr - 1})', '0.000', expect=tot['b'])
            put(ws, rr, 11, f'=SUM(K{r0}:K{rr - 1})', '0.000', expect=tot['c'])
            x = A[(per, hk, 'a', 'energy')]
            put(ws, rr, 2, f'published/est. core {num(x["published_or_est_core_rate_R"]):.3f}; residual R-S {num(x["residual_R_minus_S"]):.3f} (not allocated)')
            rr += 2
    band(ws, 6, rr - 1, 1, 12)
    rr += 1
    section(ws, rr, 'Bowman (Nov 10, 2026, Council on Foreign Relations), exact words from the saved speech')
    rr += 1
    put(ws, rr, 1, '"Tariffs, energy, and AI-related price pressures each accounted for roughly one-fourth of above-target core PCE inflation over the 12 months ending in September. '
                   'The remaining one-fourth likely reflects persistent effects from the inflationary shocks in recent years."')
    rr += 1
    put(ws, rr, 1, 'Source: 02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf ("Inflation", 2nd paragraph); '
                   'https://www.federalreserve.gov/newsevents/speech/bowman20261110a.htm. Her method is not disclosed (no footnote gives one). Her fourth piece is a cause, not a set of items.')
    # chart data: Sep 12m shares by method
    cd = rr + 3
    section(ws, cd - 2, 'Chart data: share of above-target core PCE, 12m Sep 2026, by allocation method (%), vs Bowman\'s one-fourth each')
    hdr_row(ws, cd - 1, 1, ['Group', '(a) own-weight', '(b) excess over 2%', '(c) 2% on untagged', 'Bowman'])
    for k, g in enumerate(GROUPS):
        r = cd + k
        put(ws, r, 1, g)
        src = KEY[('2026-09', '12m', g)]
        for j, col in enumerate(('H', 'J', 'L')):
            put(ws, r, 2 + j, f'={col}{src}', FMT_BR, expect=EXPECT[('Attribution', f'{col}{src}')])
        put(ws, r, 5, 25 if g != 'untagged' else 25)
    put(ws, cd + 4, 1, 'Bowman column: her "roughly one-fourth" each for tariffs, energy, AI; the untagged row shows her remaining fourth ("persistent effects"), which is a cause, not an item set.')
    bar_chart(ws, cd, cd + 3, 1, [2, 3, 4, 5], ['C00000', 'ED7D31', 'FFC000', '7F7F7F'],
              'Share of above-target core PCE by shock group, 12m to Sep 2026: three ways to allocate the 2% target vs Bowman', 'Percent of above-target core PCE', 'Shock group',
              'Source: BEA U20404/U20405 (Oct 29, 2026); UMD tags; Bowman (Nov 10, 2026)', 'N5', w=22, h=11)
    ws.freeze_panes = 'A6'


def build_measures(ws, calc, RNG, TROW, TCOL):
    header(ws, 'Breadth by measure: core, supercore, core goods, core services (headline backup only)',
           'Share of each measure\'s spending weight with inflation above 3%; weighted leaf (central) with sub-line robustness; Sep 2026 vs Oct 2026 est.; 2018-19 averages, post-2018 peak; '
           'hospital-leaf share of the 12m change; monthly series. Data only.',
           'Units: % of the measure\'s weight. Start-of-window weights. Core/supercore/goods/services leaf figures are live formulas over the Tagged_breadth leaf block (raw_PCE_leaves); '
           'sub-line, headline and averages/peaks from Agent B (outputs/B_q4_*.csv, cell notes). Series draw on raw_breadth_ts.')
    B = {(x['period'], x['measure'], x['horizon'], x['method'].split(' ')[0]): num(x['value']) for x in rd('B_q4_breadth_by_measure.csv')}
    S = {(x['measure'], x['horizon']): x for x in rd('B_q4_breadth_summary.csv')} if os.path.exists(os.path.join(OUT, 'B_q4_breadth_summary.csv')) else {}
    hdr_row(ws, 5, 1, ['Measure', 'Horizon', 'Sep 2026 (leaf)', 'Oct 2026 est. (leaf)', 'Change (pp)', 'Sub-line Sep', 'Sub-line Oct est.', '2018-19 avg (leaf)', 'Note'],
            [18, 9, 12, 12, 10, 11, 11, 12, 70])
    SEL = {'core': (lambda c: True, ''), 'supercore': (lambda c: c['sc'] == 1, f'({RNG["sc"]}=1)*'),
           'core_goods': (lambda c: c['scope'] == 'goods', f'({RNG["scope"]}="goods")*'), 'core_services': (lambda c: c['scope'] == 'services', f'({RNG["scope"]}="services")*')}
    avgcol = {'core': ('core_12m_leaf', 'core_3m_ann_leaf'), 'supercore': ('supercore_12m_leaf', 'supercore_3m_ann_leaf'),
              'core_goods': ('core_goods_12m_leaf', 'core_goods_3m_ann_leaf'), 'core_services': ('core_services_12m_leaf', 'core_services_3m_ann_leaf'),
              'headline_backup': ('headline_backup_12m_leaf', 'headline_backup_3m_ann_leaf')}
    pre = [m for m in TROW if m < '2020-01']
    rr = 6
    CH = {}
    for meas in ('core', 'supercore', 'core_goods', 'core_services', 'headline_backup'):
        for hz, hk in (('12m', '12m'), ('3m', '3m_ann')):
            put(ws, rr, 1, meas.replace('_backup', ' (backup; includes food and direct energy)'), bold=meas == 'core')
            put(ws, rr, 2, hz + (' ann.' if hz == '3m' else ''))
            for j, per in enumerate(('2026-09', '2026-10')):
                rk, wk = WIN[(per, hz)]
                if meas in SEL:
                    sel, cond = SEL[meas]
                    v = py_share(calc, rk, wk, sel)
                    put(ws, rr, 3 + j, (f'=SUMPRODUCT({cond}({RNG[rk]}>3)*{RNG[wk]})/SUMPRODUCT({cond}{RNG[wk]})*100' if cond else
                                        f'=SUMPRODUCT(({RNG[rk]}>3)*{RNG[wk]})/SUM({RNG[wk]})*100'), FMT_BR, expect=v,
                        fill=FILL_EST if per == '2026-10' else FILL_KEY)
                    SEMANTIC.append(('Breadth_measures', f'{get_column_letter(3 + j)}{rr}', B[(per, meas, hk, 'leaf')], f'B_q4 {meas} {hz} {per}'))
                else:
                    c = put(ws, rr, 3 + j, B[(per, meas, hk, 'leaf')], FMT_BR, fill=FILL_EST if per == '2026-10' else None)
                    note(c, 'Value from outputs/B_q4_breadth_by_measure.csv (code/B_q4_*.py; headline = 177 leaves incl. energy, not in raw_PCE_leaves).')
                    v = B[(per, meas, hk, 'leaf')]
                CH[(meas, hz, per)] = v
            put(ws, rr, 5, f'=D{rr}-C{rr}', FMT_BR, expect=CH[(meas, hz, '2026-10')] - CH[(meas, hz, '2026-09')])
            for j, per in enumerate(('2026-09', '2026-10')):
                c = put(ws, rr, 6 + j, B[(per, meas, hk, 'sub-line')], FMT_BR, fill=FILL_EST if per == '2026-10' else None)
                if j == 0:
                    note(c, 'Sub-line robustness (184 core pricing lines), from outputs/B_q4_breadth_by_measure.csv.')
            col = avgcol[meas][0 if hz == '12m' else 1]
            L = get_column_letter(TCOL[col])
            put(ws, rr, 8, f'=AVERAGE(raw_breadth_ts!{L}{TROW[pre[0]]}:{L}{TROW[pre[-1]]})', FMT_BR, expect=statistics.mean(TV[(m, col)] for m in pre))
            ts = {m: TV[(m, col)] for m in TROW}
            pk = max(ts, key=ts.get)
            put(ws, rr, 9, f'post-2018 peak {ts[pk]:.1f} ({pk}); from raw_breadth_ts')
            rr += 1
    band(ws, 6, rr - 1, 1, 9)
    for col, want in ((3, 60.626), (4, 54.038)):
        SEMANTIC.append(('Breadth_measures', f'{get_column_letter(col)}6', want, 'slide 1 reproduction core 12m'))
    for col, want in ((3, 44.814), (4, 45.467)):
        SEMANTIC.append(('Breadth_measures', f'{get_column_letter(col)}7', want, 'slide 1 reproduction core 3m'))
    # hospital share of the 12m change (script values)
    rr += 1
    section(ws, rr, 'Oct 12m change and the three hospital leaves 184-186 (Agent B, B_q4_hospital_attribution.csv; pp)')
    rr += 1
    hdr_row(ws, rr, 1, ['Measure', 'Total change', 'Hospital contribution change', 'Breadth without hospitals: Sep', 'Oct est.', 'Change without hospitals', 'Note'])
    for x in rd('B_q4_hospital_attribution.csv'):
        if x['horizon'] == '12m' and x['method'] == 'leaf':
            rr += 1
            put(ws, rr, 1, x['measure'])
            for j, k in enumerate(('change_pp', 'hosp_contrib_change_pp', 'sep_breadth_ex_hosp', 'oct_est_breadth_ex_hosp', 'change_ex_hosp_pp')):
                c = put(ws, rr, 2 + j, num(x[k]), FMT_RATE, fill=FILL_EST if k.startswith('oct') else None)
            put(ws, rr, 7, '"without hospitals" = breadth recomputed over the remaining leaves (renormalized), not total minus hospital contribution. 3m: hospital rates < 3% in both months (no effect).')
    # threshold sensitivity (Agent D)
    rr += 2
    section(ws, rr, 'Cutoff sensitivity, 12m (Agent D, D_threshold_sensitivity.csv): breadth at 2.0-4.0% cutoffs; level vs 2018-19 holds at every cutoff, the Sep->Oct change does not')
    rr += 1
    hdr_row(ws, rr, 1, ['Measure', 'Cutoff %', 'Sep 2026', 'Oct 2026 est.', 'Change (pp)', '2018-19 avg', 'Sep minus 2018-19 (pp)'])
    for x in rd('D_threshold_sensitivity.csv'):
        if x['horizon'] != '12m':
            continue
        rr += 1
        for j, k in enumerate(('scope', 'threshold_pct', 'sep_2026', 'oct_2026_est', 'change_pp', 'avg_2018_19', 'sep_minus_2018_19_pp')):
            v = num(x[k])
            put(ws, rr, 1 + j, v if v is not None else x[k], FMT_BR if j >= 2 else ('0.0' if j == 1 else None),
                fill=FILL_EST if k == 'oct_2026_est' else (FILL_KEY if k == 'threshold_pct' and v == 3.0 else None))
    # Q4b: trimmed mean reconciliation (Agent D) and ex-OER breadth (coordinator)
    rr += 2
    section(ws, rr, 'Q4b. Breadth vs the Dallas trimmed mean (Agent D, D_trimmed_reconcile.csv): monthly trimming vs 12m component rates')
    rr += 1
    hdr_row(ws, rr, 1, ['Period', 'Measure', 'Value %', 'Dallas published %'])
    for x in rd('D_trimmed_reconcile.csv'):
        rr += 1
        est = x['month'] == '2026-10'
        put(ws, rr, 1, x['month'] + (' est.' if est else ''), fill=FILL_EST if est else None)
        put(ws, rr, 2, x['measure'])
        put(ws, rr, 3, num(x['value']), FMT_RATE, fill=FILL_EST if est else None)
        put(ws, rr, 4, num(x['dallas_published']), FMT_RATE)
    rr += 1
    put(ws, rr, 1, 'Q&A data (Agent D): the trimmed mean cuts the top 31% of MONTHLY changes; items above 3% at 12m lose 33% of their weighted months from the top, and their kept months average 2.65% vs 4.80% over all months. '
                   'Trimming the 12m rates once instead gives 2.98% (core). Dallas 12m fell 2.76 (Sep 2025) -> 2.27 (Sep 2026) while 12m breadth rose 58.8 -> 60.6.')
    rr += 2
    section(ws, rr, 'Q4b optional: breadth on core ex OER (Eli\'s "harmonized PCE" scope; OER = leaves 161-162, BEA line 160), coordinator, Z_q4b_ex_oer_breadth.csv')
    rr += 1
    hdr_row(ws, rr, 1, ['Scope', 'Period', 'Horizon', 'Breadth %', 'n leaves'])
    for x in rd('Z_q4b_ex_oer_breadth.csv'):
        rr += 1
        est = x['period'] == '2026-10'
        put(ws, rr, 1, x['scope'])
        put(ws, rr, 2, x['period'] + (' est.' if est else ''), fill=FILL_EST if est else None)
        put(ws, rr, 3, x['horizon'])
        c = put(ws, rr, 4, num(x['breadth_pct']), FMT_BR, fill=FILL_EST if est else None)
        put(ws, rr, 5, num(x['n_leaves']))
        note(c, 'Value from code/Z_coordinator_extras.py (C_common engine; start-of-window weights; >3%).')
    # series + chart
    T0 = rr + 4
    cols = ['core_12m_leaf', 'supercore_12m_leaf', 'core_goods_12m_leaf', 'core_services_12m_leaf']
    f1, l1 = ts_block(ws, T0, TROW, TCOL, cols, ['Core 12m', 'Supercore 12m', 'Core goods 12m', 'Core services 12m'],
                      'Monthly series, 12m (weighted leaf), with 2018-19 core average; from raw_breadth_ts (Agent B); Oct 2026 = est.')
    line_chart(ws, f1, l1, [2, 3, 4, 5, 6], ['C00000', '7030A0', '2F5597', 'BF8F00', '7F7F7F'],
               'Breadth by measure, 12m: share of weight with inflation above 3% (weighted leaf), 2018 to Oct 2026 est.', 'Percent of the measure\'s spending weight',
               'Source: BEA U20404/U20405 (Oct 29, 2026); UMD calculations; Oct 2026 = est.', 'K5', dashes={6: 'dash'})
    T1 = l1 + 4
    cols3 = ['core_3m_ann_leaf', 'supercore_3m_ann_leaf', 'core_goods_3m_ann_leaf', 'core_services_3m_ann_leaf']
    f2, l2 = ts_block(ws, T1, TROW, TCOL, cols3, ['Core 3m ann.', 'Supercore 3m ann.', 'Core goods 3m ann.', 'Core services 3m ann.'],
                      'Monthly series, 3m annualized (weighted leaf), with 2018-19 core average; Oct 2026 = est.')
    line_chart(ws, f2, l2, [2, 3, 4, 5, 6], ['C00000', '7030A0', '2F5597', 'BF8F00', '7F7F7F'],
               'Breadth by measure, 3m annualized: share of weight with inflation above 3% (weighted leaf), 2018 to Oct 2026 est.', 'Percent of the measure\'s spending weight',
               'Source: BEA U20404/U20405 (Oct 29, 2026); UMD calculations; Oct 2026 = est. 3m series are noisy (OER sits near the 3% line).', 'K30', dashes={6: 'dash'})
    # Sep vs Oct bar
    cd = 5
    hdr_row(ws, cd, 26, ['Chart data: measure, horizon', 'Sep 2026', 'Oct 2026 est.'], [26, 10, 12])
    k = 0
    for r in range(6, 14):
        k += 1
        put(ws, cd + k, 26, f'=A{r}&", "&B{r}', expect=f'{ws.cell(row=r, column=1).value}, {ws.cell(row=r, column=2).value}')
        put(ws, cd + k, 27, f'=C{r}', FMT_BR, expect=EXPECT[('Breadth_measures', f'C{r}')])
        put(ws, cd + k, 28, f'=D{r}', FMT_BR, expect=EXPECT[('Breadth_measures', f'D{r}')], fill=FILL_EST)
    bar_chart(ws, cd + 1, cd + k, 26, [27, 28], ['8EA9DB', 'C00000'], 'Breadth by measure, Sep 2026 vs Oct 2026 est. (weighted leaf)',
              'Percent of the measure\'s spending weight', 'Measure, horizon', 'Source: BEA U20404/U20405; UMD Oct build. Oct 12m declines are driven by three hospital leaves (base effect).', 'K55', w=24, h=11)
    ws.freeze_panes = 'A6'
    # tagged series chart lives on Tagged_breadth (built after)


def build_tagged_series(ws, TROW, TCOL, start_row):
    T0 = start_row + 4
    cols = [f'{g}_within_12m' for g in GROUPS]
    f1, l1 = ts_block(ws, T0, TROW, TCOL, cols, ['Energy 12m (within)', 'Tariff 12m (within)', 'AI 12m (within)', 'Untagged 12m (within)'],
                      'Monthly within-group breadth, 12m (weighted leaf); from raw_breadth_ts (Agent A); Oct 2026 = est.', avg=False)
    line_chart(ws, f1, l1, [2, 3, 5], ['C00000', '2F5597', '7F7F7F'],
               'Within-group breadth, 12m: share of each group\'s weight with inflation above 3% (energy, tariff, untagged), 2018 to Oct 2026 est.',
               'Percent of the group\'s spending weight', 'Source: BEA U20404/U20405; UMD tags (Nov 14); Oct 2026 = est. AI group omitted (4 leaves, 2% of core).', 'N5', w=24, h=11)
    # Sep vs Oct bar (within, 12m and 3m)
    cd = 5
    hdr_row(ws, cd, 30, ['Chart data: group', 'Within 12m Sep', 'Within 12m Oct est.', 'Within 3m Sep', 'Within 3m Oct est.'])
    for k in range(5):
        r = 6 + k
        put(ws, cd + 1 + k, 30, f'=A{r}', expect=ws.cell(row=r, column=1).value)
        for j in range(4):
            col = get_column_letter(4 + j)
            put(ws, cd + 1 + k, 31 + j, f'={col}{r}', FMT_BR, expect=EXPECT[('Tagged_breadth', f'{col}{r}')], fill=FILL_EST if j % 2 else None)
    bar_chart(ws, cd + 1, cd + 5, 30, [31, 32, 33, 34], ['F4B183', 'C00000', '9DC3E6', '2F5597'], 'Within-group breadth by shock tag, Sep 2026 vs Oct 2026 est.',
              'Percent of the group\'s spending weight', 'Shock group', 'Source: BEA U20404/U20405; UMD tags; Oct 2026 = est. Untagged Oct 12m fall = hospital leaves (base effect).', 'N30', w=24, h=11)


def build_sticky(ws, calc, RNG):
    header(ws, 'Sticky vs flexible (exploratory): breadth of sticky-price and flexible-price spending',
           'PCE leaves classed sticky/flexible via the BLS PCE-CPI concordance and Bryan-Meyer (2010) CPI groups (PPI/non-CPI priced and mixed leaves left out); cross-check on an Atlanta Fed-style CPI basket. Data only.',
           'Units: % of the class\'s weight above 3%. PCE side: live formulas over the Tagged_breadth leaf block (raw_PCE_leaves, sticky_class). CPI basket: Agent B script values (B_q5_atlanta_basket.csv); '
           'Oct CPI 12m uses an interpolated Oct 2025 base (approx.). Coverage is ~61% of core weight; Eli: "fine if it shows nothing".')
    SF = {(x['period'], x['cls'], x['horizon']): num(x['value']) for x in rd('B_q5_sticky_flexible.csv') if x['rule'] == 'primary' and x['side'].startswith('PCE')}
    hdr_row(ws, 5, 1, ['Class (PCE leaves)', 'n leaves', 'Share of core weight % (Sep 12m window)', '12m Sep', '12m Oct est.', '3m Sep', '3m Oct est.'], [26, 9, 14, 10, 10, 10, 10])
    rr = 6
    for cls in ('sticky', 'flexible', 'unclassified'):
        sel = lambda c, cls=cls: c['st'] == cls
        cond = f'({RNG["st"]}="{cls}")*'
        put(ws, rr, 1, cls)
        put(ws, rr, 2, f'=COUNTIF({RNG["st"]},"{cls}")', expect=sum(1 for c in calc.values() if sel(c)))
        put(ws, rr, 3, f'=SUMPRODUCT({cond}{RNG["w12s"]})/SUM({RNG["w12s"]})*100', FMT_BR, expect=100 * sum(c['w12s'] for c in calc.values() if sel(c)) / sum(c['w12s'] for c in calc.values()))
        for j, (per, hz) in enumerate([('2026-09', '12m'), ('2026-10', '12m'), ('2026-09', '3m'), ('2026-10', '3m')]):
            rk, wk = WIN[(per, hz)]
            put(ws, rr, 4 + j, f'=SUMPRODUCT({cond}({RNG[rk]}>3)*{RNG[wk]})/SUMPRODUCT({cond}{RNG[wk]})*100', FMT_BR, expect=py_share(calc, rk, wk, sel),
                fill=FILL_EST if per == '2026-10' else None)
            if cls != 'unclassified':
                SEMANTIC.append(('Sticky_flexible', f'{get_column_letter(4 + j)}{rr}', SF[(per, cls, '12m' if hz == '12m' else '3m_ann')], f'B_q5 {cls} {per} {hz}'))
        rr += 1
    rr += 1
    section(ws, rr, 'Cross-check: Atlanta Fed-style CPI basket (CPI items weighted by relative importance at the start of the window), Agent B script values')
    rr += 1
    hdr_row(ws, rr, 1, ['Scope', 'Class', 'Period', 'Horizon', 'Breadth %', 'n items', 'Weighted mean rate %', 'Atlanta Fed published 12m'])
    for x in rd('B_q5_atlanta_basket.csv'):
        rr += 1
        est = x['period'] == '2026-10'
        for j, v in enumerate([x['scope'], x['cls'], x['period'] + (' (approx. 12m)' if est and x['horizon'] == '12m' else ''), x['horizon'], num(x['value']), num(x['n_items']),
                               num(x['weighted_mean_rate']), num(x.get('atlanta_published_12m'))]):
            put(ws, rr, 1 + j, v, FMT_BR if j in (4,) else (FMT_RATE if j in (6, 7) else None), fill=FILL_EST if est and j == 4 else None)
    rr += 2
    put(ws, rr, 1, 'Caveats (Agent B): classification from Bryan & Meyer (2010) Table 1 (45 CPI groups); that the current Atlanta Fed basket uses exactly this grouping is unverified. '
                   'Flexible set is ~9% of core weight and goods-heavy; 3m sticky series swings ~40 pp month to month because OER sits on the 3% line. Mapping: outputs/B_q5_mapping.csv.')
    rr += 2
    section(ws, rr, 'Reference panel: Atlanta Fed sticky-price and flexible-price CPI, publisher-reported rates (%), Jan 2025 - Oct 2026 (Z_q5_atlanta_panel.csv)')
    rr += 1
    P = rd('Z_q5_atlanta_panel.csv')
    sers = ['Flexible CPI', 'Core Flexible CPI', 'Sticky CPI', 'Core Sticky CPI']
    hdr_row(ws, rr, 1, ['Month'] + [f'{s} 1m ann.' for s in sers] + [f'{s} 12m' for s in sers])
    by = {}
    for x in P:
        by.setdefault(x['month'], {})[x['series']] = x
    p0 = rr + 1
    for m in sorted(by):
        rr += 1
        put(ws, rr, 1, m, fill=FILL_KEY if m in ('2026-08', '2026-09', '2026-10') else None)
        for j, s in enumerate(sers):
            put(ws, rr, 2 + j, num(by[m][s]['mm_1m_ann_pct']), FMT_BR)
            put(ws, rr, 6 + j, num(by[m][s]['yoy_12m_pct']), FMT_BR)
    note(ws.cell(row=p0 - 1, column=2), 'Source: 03_Data/pipelines/Price indexes/Sticky CPI/raw/atlantafed_sticky_price_cpi_2026-11-10.xlsx (sheet Data), via code/Z_coordinator_extras.py. Rates as published.')
    line_chart(ws, p0, rr, [6, 7, 8, 9], ['ED7D31', 'F4B183', '2F5597', '9DC3E6'],
               'Atlanta Fed sticky vs flexible CPI, 12m %, Jan 2025 - Oct 2026', 'Percent change, 12m',
               'Source: Federal Reserve Bank of Atlanta, Sticky-Price CPI (retrieved Nov 10, 2026).', 'K5', skip=3, w=20, h=10)
    ws.freeze_panes = 'A6'


def build_waller(ws, calc, RNG):
    header(ws, 'Waller comparison: ">70 percent of the components of core PCE service prices" above 3% at 12m (September)',
           'Every variant on core services 12m: count vs weighted, leaf vs sub-line, Sep 2026 and Oct 2026 est. Weighted leaf (start-of-window) is Eli\'s preferred basis (it reproduces >70%). Data only.',
           'Units: % of items (count) or % of core-services weight. Weighted and count leaf figures are live formulas over the Tagged_breadth leaf block; other variants pulled from '
           '09_slide1_research/outputs/C_waller_variants.csv via outputs/B_q6_waller.csv.')
    sel = lambda c: c['scope'] == 'services'
    cond = f'({RNG["scope"]}="services")*'
    hdr_row(ws, 5, 1, ['Variant (core services, 12m)', 'Sep 2026', 'Oct 2026 est.', 'Exceeds 70% in Sep?', 'Note'], [52, 11, 12, 12, 60])
    put(ws, 6, 1, 'Weighted leaf, start-of-window weights (PREFERRED, Eli)', bold=True)
    put(ws, 7, 1, 'Count, leaf (84 core services leaves)')
    for j, per in enumerate(('2026-09', '2026-10')):
        rk, wk = WIN[(per, '12m')]
        put(ws, 6, 2 + j, f'=SUMPRODUCT({cond}({RNG[rk]}>3)*{RNG[wk]})/SUMPRODUCT({cond}{RNG[wk]})*100', FMT_BR, expect=py_share(calc, rk, wk, sel),
            fill=FILL_EST if j else FILL_KEY)
        n = sum(1 for c in calc.values() if sel(c))
        put(ws, 7, 2 + j, f'=SUMPRODUCT({cond}({RNG[rk]}>3))/COUNTIF({RNG["scope"]},"services")*100', FMT_BR,
            expect=100 * sum(1 for c in calc.values() if sel(c) and c[rk] > 3) / n, fill=FILL_EST if j else None)
    put(ws, 6, 4, '=IF(B6>70,"yes","no")', expect='yes' if py_share(calc, 'r12s', 'w12s', sel) > 70 else 'no')
    put(ws, 7, 4, '=IF(B7>70,"yes","no")', expect='yes' if 100 * sum(1 for c in calc.values() if sel(c) and c['r12s'] > 3) / sum(1 for c in calc.values() if sel(c)) > 70 else 'no')
    W = rd('B_q6_waller.csv')
    wv = {(x['period'], x['method'], x['variant']): num(x['value_pct']) for x in W if x['scope'] == 'core_services'}
    SEMANTIC.append(('Waller', 'B6', wv[('2026-09', 'leaf', 'weight: start-of-window (shares 12 months before the end month)')], 'B_q6 weighted leaf Sep'))
    SEMANTIC.append(('Waller', 'C6', wv[('2026-10', 'leaf', 'weight: start-of-window (shares 12 months before the end month)')], 'B_q6 weighted leaf Oct'))
    SEMANTIC.append(('Waller', 'B7', wv[('2026-09', 'leaf', 'count (unweighted)')], 'B_q6 count leaf Sep'))
    SEMANTIC.append(('Waller', 'C7', wv[('2026-10', 'leaf', 'count (unweighted)')], 'B_q6 count leaf Oct'))
    rr = 8
    for (meth, var) in sorted({(k[1], k[2]) for k in wv}):
        if meth == 'leaf' and var in ('count (unweighted)', 'weight: start-of-window (shares 12 months before the end month)'):
            continue
        put(ws, rr, 1, f'{var} [{meth}]')
        c = put(ws, rr, 2, wv.get(('2026-09', meth, var)), FMT_BR)
        put(ws, rr, 3, wv.get(('2026-10', meth, var)), FMT_BR, fill=FILL_EST)
        put(ws, rr, 4, 'yes' if (wv.get(('2026-09', meth, var)) or 0) > 70 else 'no')
        note(c, 'Pulled from 09_slide1_research/outputs/C_waller_variants.csv (via outputs/B_q6_waller.csv).')
        rr += 1
    band(ws, 6, rr - 1, 1, 5)
    rr += 1
    put(ws, rr, 1, 'Waller (Nov 10, BoE Watchers): "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September." His basis is not stated. '
                   'Source: 02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Waller_economic_outlook.pdf')
    ws.freeze_panes = 'A6'


def build_hospital(ws, HROW, HV, hms):
    header(ws, 'Hospital base effect: was the Oct 2025 hospital price jump real, and how unusual was it?',
           'Monthly m/m for PPI hospitals (NSA), the Medicare inpatient sub-index (NSA) and BEA leaf 184 (SA; leaves 185-186 share the PPI source), Jan 2018 - Oct 2026 (Oct 2026 leaf = est.); '
           'Oct 2025 vs the 2018-25 distribution. Data only.',
           'Units: % m/m. Live formulas over raw_hospital. Answer (Agent B, Q7, verified): the Oct 2025 value is a measured price (published Jan 14, 2026, response rates normal), not a fill.')
    hdr_row(ws, 5, 1, ['Month', 'PPI hospitals m/m % (NSA)', 'PPI Medicare inpatient m/m % (NSA)', 'BEA leaf 184 m/m % (SA)'], [10, 14, 14, 14])
    ms = [m for m in hms if m >= '2018-01']
    first = 6
    MM = {}
    for k, m in enumerate(ms):
        rr = first + k
        pm = hms[hms.index(m) - 1]
        est = m == '2026-10'
        put(ws, rr, 1, f'=raw_hospital!A{HROW[m]}', expect=m, fill=FILL_EST if est else (FILL_KEY if m == '2025-10' else None))
        v1 = (HV[m]['ppi'] / HV[pm]['ppi'] - 1) * 100
        v3 = (HV[m]['leaf'] / HV[pm]['leaf'] - 1) * 100
        put(ws, rr, 2, f'=(raw_hospital!B{HROW[m]}/raw_hospital!B{HROW[pm]}-1)*100', '0.000', expect=v1)
        if HV[m]['med'] is not None and HV[pm]['med'] is not None:
            put(ws, rr, 3, f'=(raw_hospital!C{HROW[m]}/raw_hospital!C{HROW[pm]}-1)*100', '0.000', expect=(HV[m]['med'] / HV[pm]['med'] - 1) * 100)
        put(ws, rr, 4, f'=(raw_hospital!D{HROW[m]}/raw_hospital!D{HROW[pm]}-1)*100', '0.000', expect=v3, fill=FILL_EST if est else None)
        MM[m] = (rr, v1, v3)
    last = first + len(ms) - 1
    r25 = [MM[m][0] for m in ms if m <= '2025-12']
    a, b = min(r25), max(r25)
    oc = MM['2025-10'][0]
    # stats block
    S0, SC = 5, 7
    hdr_row(ws, S0, SC, ['Statistic', 'PPI hospitals (NSA)', 'BEA leaf 184 (SA)', 'Note'], [36, 14, 14, 60])
    l184 = [MM[m][2] for m in ms if m <= '2025-12']
    p622 = [MM[m][1] for m in ms if m <= '2025-12']
    rows = [('Oct 2025 m/m %', f'=B{oc}', f'=D{oc}', MM['2025-10'][1], MM['2025-10'][2], 'month now leaving the 12m window'),
            ('Mean m/m, 2018-01 to 2025-12', f'=AVERAGE(B{a}:B{b})', f'=AVERAGE(D{a}:D{b})', statistics.mean(p622), statistics.mean(l184), ''),
            ('SD m/m, 2018-01 to 2025-12 (sample)', f'=STDEV(B{a}:B{b})', f'=STDEV(D{a}:D{b})', statistics.stdev(p622), statistics.stdev(l184), ''),
            ('z-score of Oct 2025', f'=(H6-H7)/H8', f'=(I6-I7)/I8', (MM['2025-10'][1] - statistics.mean(p622)) / statistics.stdev(p622),
             (MM['2025-10'][2] - statistics.mean(l184)) / statistics.stdev(l184), 'Agent B reports z 3.29 (PPI) and 2.73 (leaf 184)'),
            ('Rank of Oct 2025 among 2018-25 months (1 = highest)', f'=RANK(B{oc},B{a}:B{b})', f'=RANK(D{oc},D{a}:D{b})',
             1 + sum(1 for x in p622 if x > MM['2025-10'][1]), 1 + sum(1 for x in l184 if x > MM['2025-10'][2]), 'Agent B: 2nd (PPI), 4th (leaf 184) of 96'),
            ('Average m/m Nov 2025 - Sep 2026', f'=AVERAGE(B{MM["2025-11"][0]}:B{MM["2026-09"][0]})', f'=AVERAGE(D{MM["2025-11"][0]}:D{MM["2026-09"][0]})',
             statistics.mean(MM[m][1] for m in ms if '2025-11' <= m <= '2026-09'), statistics.mean(MM[m][2] for m in ms if '2025-11' <= m <= '2026-09'), 'slide 1 R6 row 66-68: 0.218 (leaf 184)'),
            ('Oct 2026 m/m % (PPI prelim.; leaf est.)', f'=B{MM["2026-10"][0]}', f'=D{MM["2026-10"][0]}', MM['2026-10'][1], MM['2026-10'][2], 'leaf = UMD est. 0.305; 0.564 needed to keep 12m above 3%')]
    for k, (lbl, f1, f2, e1, e2, nt) in enumerate(rows):
        r = S0 + 1 + k
        put(ws, r, SC, lbl, bold=k == 0)
        put(ws, r, SC + 1, f1, '0.000', expect=e1, fill=FILL_KEY if k in (0, 3) else None)
        put(ws, r, SC + 2, f2, '0.000', expect=e2, fill=FILL_EST if k == 6 else (FILL_KEY if k in (0, 3) else None))
        put(ws, r, SC + 3, nt)
    SEMANTIC.append(('Hospital_base_effect', 'I6', 0.893, 'slide 1 hospital Oct 2025 m/m'))
    SEMANTIC.append(('Hospital_base_effect', 'I11', 0.218, 'slide 1 hospital avg Nov25-Sep26'))
    SEMANTIC.append(('Hospital_base_effect', 'H9', 3.29, 'B_q7 z PPI'))
    SEMANTIC.append(('Hospital_base_effect', 'I9', 2.73, 'B_q7 z leaf'))
    r = S0 + len(rows) + 3
    section_c = ws.cell(row=r, column=SC, value='Was it a fill? Evidence (Agent B, verified by coordinator)')
    section_c.font = Font(bold=True, size=12, color=b1.NAVY)
    ev = ['BLS collected the Oct 2025 PPI late and published it with November on Jan 14, 2026 (BLS revised release dates page).',
          'BLS Nov 2025 PPI Detailed Report, p. 6: response rates "within the normal range, and no modifications to PPI methodology or procedures were necessary" '
          '(03_Data/Raw/BLS_PPI_detailed_report_2025-11_retrieved_2026-11-12.pdf).',
          'ALFRED PCU622622: Oct 2025 first appears in the 2026-01-14 vintage at 248.009 (Sep 2025: 244.536), +1.42% NSA; no BLS footnote on the value.',
          'BEA\'s shutdown treatment (geometric mean of Sep and Nov) applies to the missing CPIs; the hospital leaves are PPI-priced.',
          'Sep 2025 (-0.15%) and Nov 2025 (+0.22%) were published separately, so Oct is not two months booked in one.',
          'Driver: the October Medicare inpatient reset (WPU5121010111 +5.96% in Oct 2025, largest October since 2014). BEA\'s SA leaf still shows October bumps in 2017, 2019, 2023, 2025 (0.72-0.89%).']
    for k, t in enumerate(ev):
        ws.cell(row=r + 1 + k, column=SC, value=f'{k + 1}. {t}')
    # chart: leaf 184 and PPI m/m since 2023
    c0 = MM['2023-01'][0]
    ch = BarChart()
    ch.type = 'col'
    style_chart(ch, 'Hospital prices, m/m %: BEA leaf 184 (SA) and PPI hospitals (NSA), Jan 2023 - Oct 2026 (Oct 2026 leaf = est.)', 'Percent change, m/m', 'Month',
                'Source: BLS PPI PCU622---622--- (pulled Nov 15, 2026); BEA U20404 (Oct 29, 2026); Oct 2025 = month leaving the 12m window', w=26, h=11, yfmt='0.0')
    for col, color in ((4, 'C00000'), (2, '8EA9DB')):
        s = Series(Reference(ws, min_col=col, min_row=c0, max_row=last), title=ws.cell(row=5, column=col).value)
        s.graphicalProperties.solidFill = color
        s.graphicalProperties.line.solidFill = color
        ch.series.append(s)
    ch.set_categories(Reference(ws, min_col=1, min_row=c0, max_row=last))
    ch.x_axis.tickLblSkip = 3
    add_chart(ws, ch, 'G25')
    ws.freeze_panes = 'A6'


def build_ppi(ws, PROW, PV, pms, OROW, OV):
    header(ws, 'PPI upstream panel: intermediate demand by production flow (stages 1-4), commodity-type ID61/ID62, final demand',
           'Monthly SA index, m/m, 3m annualized and y/y, Jan 2018 - Oct 2026 (Jul-Oct preliminary); Oct 2026 vs Sep; energy\'s share of the stage 1-2 rise; daily oil around the early-Nov drop. Data only.',
           'Units: % (m/m, 3m ann., y/y on the SA index). Live formulas over raw_PPI_stages and raw_oil. LABEL: stages = WPSID51-54; ID61/ID62 are by commodity type (ID62 = unprocessed goods), NOT stages. '
           'BLS y/y headlines are NSA (Agent C check: match).')
    S = {x['series_id']: x for x in rd('C_q8_ppi_stages_summary.csv')}
    hdr_row(ws, 5, 1, ['Series', 'Title', 'Sep m/m', 'Oct m/m', 'Sep 3m ann.', 'Oct 3m ann.', 'Sep y/y (SA)', 'Oct y/y (SA)', 'Oct index'], [10, 46, 9, 9, 10, 10, 10, 10, 10])
    R = 'raw_PPI_stages!'
    for k, (sid, t) in enumerate(PPI_IDS):
        rr = 6 + k
        col = get_column_letter(2 + k)
        put(ws, rr, 1, sid, bold=sid in ('WPSID51', 'WPSID52'))
        put(ws, rr, 2, t)
        for j, m in enumerate(('2026-09', '2026-10')):
            i0, i1, i3, i12 = PV[(sid, m)], PV[(sid, pms[pms.index(m) - 1])], PV[(sid, pms[pms.index(m) - 3])], PV[(sid, pms[pms.index(m) - 12])]
            r0, r1, r3, r12 = PROW[m], PROW[pms[pms.index(m) - 1]], PROW[pms[pms.index(m) - 3]], PROW[pms[pms.index(m) - 12]]
            put(ws, rr, 3 + j, f'=({R}{col}{r0}/{R}{col}{r1}-1)*100', FMT_RATE, expect=(i0 / i1 - 1) * 100, fill=FILL_KEY if j and sid in ('WPSID51', 'WPSID52') else None)
            put(ws, rr, 5 + j, f'=(({R}{col}{r0}/{R}{col}{r3})^4-1)*100', FMT_BR, expect=((i0 / i3) ** 4 - 1) * 100)
            put(ws, rr, 7 + j, f'=({R}{col}{r0}/{R}{col}{r12}-1)*100', FMT_BR, expect=(i0 / i12 - 1) * 100)
            if m == '2026-10':
                SEMANTIC.append(('PPI_stages', f'D{rr}', num(S[sid]['mm_Oct26']), f'C_q8 {sid} mm Oct'))
                SEMANTIC.append(('PPI_stages', f'F{rr}', num(S[sid]['ann3m_Oct26']), f'C_q8 {sid} 3m Oct'))
        put(ws, rr, 9, f'={R}{col}{PROW["2026-10"]}', '0.000', expect=PV[(sid, '2026-10')])
    band(ws, 6, 5 + len(PPI_IDS), 1, 9)
    rr = 7 + len(PPI_IDS)
    put(ws, rr, 1, 'Revision note: the Nov 13 release revised Jun-Sep. WPSID62 Sep 299.868 -> 293.838 (-2.0%); Sep 3m ann. +41.5% -> +31.0%; y/y +21.5% -> +19.3% (C_q8_vintage_revisions.csv). The Nov 10 "+41.5%" is superseded.')
    # energy contributions (script values)
    rr += 2
    section(ws, rr, 'Energy within stages 1-2 (Agent C, C_q8_energy_contributions_windows.csv; pp of the stage index change)')
    rr += 1
    E = rd('C_q8_energy_contributions_windows.csv')
    cols = list(E[0].keys())
    hdr_row(ws, rr, 1, cols[:10])
    for x in E:
        rr += 1
        for j, k in enumerate(cols[:10]):
            v = num(x[k])
            put(ws, rr, 1 + j, v if v is not None else x[k], '0.00' if v is not None else None)
    # series: stage 1, stage 2, ID62 3m ann. and y/y since 2018 (live)
    T0 = rr + 4
    section(ws, T0 - 1, 'Monthly series (live over raw_PPI_stages): y/y and 3m ann. for stage 1, stage 2, ID62 unprocessed goods, final demand')
    lab = ['Stage 1 y/y', 'Stage 2 y/y', 'ID62 unprocessed y/y', 'Final demand y/y', 'Stage 1 3m ann.', 'Stage 2 3m ann.']
    hdr_row(ws, T0, 1, ['Month'] + lab)
    ser = [('WPSID51', 12), ('WPSID52', 12), ('WPSID62', 12), ('WPSFD4', 12), ('WPSID51', 3), ('WPSID52', 3)]
    colof = {sid: get_column_letter(2 + k) for k, (sid, _) in enumerate(PPI_IDS)}
    ms = [m for m in pms if m >= '2018-01']
    f1 = T0 + 1
    for k, m in enumerate(ms):
        r = f1 + k
        put(ws, r, 1, f'={R}A{PROW[m]}', expect=m)
        for j, (sid, back) in enumerate(ser):
            pm = pms[pms.index(m) - back]
            c = colof[sid]
            v = ((PV[(sid, m)] / PV[(sid, pm)]) ** (12 / back) - 1) * 100
            put(ws, r, 2 + j, f'=(({R}{c}{PROW[m]}/{R}{c}{PROW[pm]})^{12 // back}-1)*100' if back == 3 else f'=({R}{c}{PROW[m]}/{R}{c}{PROW[pm]}-1)*100', FMT_BR, expect=v)
    l1 = f1 + len(ms) - 1
    line_chart(ws, f1, l1, [2, 3, 4, 5], ['C00000', 'ED7D31', '7F7F7F', '2F5597'],
               'PPI upstream: stage 1 and stage 2 intermediate demand, ID62 unprocessed goods, final demand, y/y %, 2018 to Oct 2026', 'Percent change, y/y (SA index)',
               'Source: BLS PPI (pulled Nov 15, 2026; Jul-Oct 2026 preliminary). Stages = WPSID51/52; ID62 = unprocessed goods by commodity type.', 'K5', dashes={4: 'dash'})
    # oil block (live)
    O0 = 5
    OC = 30
    hdr_row(ws, O0, OC, ['Oil: date', 'Brent $/bbl', 'WTI $/bbl', 'Brent d/d %'], [12, 10, 10, 10])
    ds = sorted(OROW)
    for k, dte in enumerate(ds):
        r = O0 + 1 + k
        put(ws, r, OC, f'=raw_oil!A{OROW[dte]}', expect=dte)
        put(ws, r, OC + 1, f'=raw_oil!B{OROW[dte]}', '0.00', expect=OV[dte].get('brent'))
        put(ws, r, OC + 2, f'=raw_oil!C{OROW[dte]}', '0.00', expect=OV[dte].get('wti'))
        if k:
            pd_ = ds[k - 1]
            put(ws, r, OC + 3, f'=(raw_oil!B{OROW[dte]}/raw_oil!B{OROW[pd_]}-1)*100', '0.0', expect=(OV[dte]['brent'] / OV[pd_]['brent'] - 1) * 100)
    ol = O0 + len(ds)
    line_chart(ws, O0 + 1, ol, [OC + 1, OC + 2], ['C00000', '2F5597'],
               'Daily oil spot, Sep 1 - Nov 11, 2026: Brent peaked $135.51 (Oct 2); fell to $91.84 on Nov 4', 'Dollars per barrel',
               'Source: EIA via FRED (DCOILBRENTEU, DCOILWTICO), retrieved Nov 15, 2026. Oct PPI priced around Oct 13 (Brent $125.78), before the drop.', 'K30', skip=10, w=22, h=10)
    # reorder: line_chart uses column A as categories; override for oil
    ws._charts[-1].set_categories(Reference(ws, min_col=OC, min_row=O0 + 1, max_row=ol))
    ws._charts[-1].x_axis.title = b1.rich_title([('Date (trading days)', 9, True, '404040')])
    ws.freeze_panes = 'A6'


def build_external(ws):
    header(ws, 'External evidence: ISM pricing-sentiment note, FEDS oil note (second half), US confirming items',
           'Agent C findings (Q9-Q11), each with its source. Data and verified quotes only; no interpretation.',
           'Sources: 02_Research/External_views/Fed_officials_2026-11/staff_notes/ (saved full texts); outputs/C_q9_ism_note.md, C_q10_oil_note_verification.csv, C_q11_confirming_items.csv.')
    hdr_row(ws, 5, 1, ['Item', 'Finding', 'Source / location'], [30, 110, 60])
    rows = [
        ('Q9 ISM index: what it is', 'Board-staff text-mining measure (Cajner, Crane, Kurz, Soto & Vrankovich, FEDS Note Oct 1, 2026): free-text "prices up/down" responses in ISM manufacturing and services surveys mapped to ~50 PPI-like categories (sentence embeddings; Claude Sonnet 4.5 preferred); net mentions = increases - decreases, monthly, 2024-2026. High-tech variant = memory chips and processors (Fig. 3).', 'staff_notes/2026-10-01_Cajner_pricing_sentiment_ISM.html; outputs/C_q9_ism_note.md'),
        ('Q9 ISM index: public?', 'No public series found. No data-availability statement; the note thanks ISM "for access to" the data; ISM site login-gated. No latest reading (sample ends mid-2026). Waller cites an "October" reading not in the note.', 'outputs/C_q9_ism_note.md; C_paywalled.csv'),
        ('Q10 oil note: country level', 'No country table. Footnote 4 only: persistence rise significant in all five economies; oil pass-through "rose significantly in Canada, Japan, and the U.S., but was weaker and not statistically significant in the euro area and the U.K., possibly reflecting Europe\'s natural gas price shock". No US coefficient reported.', 'staff_notes/2026-11-09_DeMichelis_oil_core_inflation.html, fn 4'),
        ('Q10 oil note: pass-through size', '0.14 pp per 10 pp relative oil inflation is the post-pandemic total (10 x (0.001 + 0.013)); 0.013 is the post-pandemic increase.', 'Table 2; C_q10_oil_note_verification.csv'),
        ('Q10 oil note: GEMUS', 'Supply reduction in a small oil-producing region calibrated to raise oil prices 10% (Fig. 4); same inertial Taylor-type rule in all cases (fn 10), not a rule comparison; higher pass-through via a higher oil cost share (fn 11). "the GDP hit is about twice as large": no comparator number; base case GDP hit "a little over 0.1%".', 'GEMUS section, fn 10-11'),
        ('Q10 oil note: correction to our summary', 'Our lit summary\'s "late-Oct spike above $110" is wrong: Brent closed above $110 every day Sep 10 - Oct 30 (Sep avg $114, Oct $124). Bowman\'s "at or above $110 in late October" is literally true.', 'C_q8_oil_daily.csv; C_q10_lit_summary_update.md'),
        ('Q11 airfares', 'CPI airline fares SA Oct +0.4% m/m, 3m ann. +18.3% (no Oct y/y: no Oct 2025 CPI). PCE air transportation Sep +4.4% m/m, +20.5% y/y. PPI jet fuel Oct +7.0% m/m, +106.5% y/y. For pass-through: fares vs jet fuel r ~0.4 at lags 0-1. Against: fares rose 8% Dec-Feb before the March oil spike; no retrace when jet fuel fell Jun-Jul; cumulative ratio ~0.16; demand data not pulled.', 'C_q11_confirming_items.md/.csv'),
        ('Q11 freight', 'PPI truck freight Oct +3.9% m/m, +24.6% y/y while SA diesel -7.9%; truck vs diesel r 0.55-0.66 at lags 0-1. CPI food away from home +0.5% m/m Oct, +2.3% since Feb; truck-to-food lag correlation peaks at 6 months (0.33, thin).', 'C_q11_confirming_items.md/.csv'),
        ('Q11b diesel -> food', 'CPI food at home Oct +0.44% m/m SA (largest since Apr), 3m ann. +1.65%; food away +0.52%, 3m ann. +4.08%. Retail diesel Oct -0.6% m/m (+68% vs Feb); PPI truck freight +3.9% m/m. Lag correlations: diesel -> food at home <= 0.30; truck freight -> food 0.29-0.49 peaking at lags 7-8 (long lags; shock 7 months old).', 'outputs/C_q11b_followup.md; C_q11b_food_diesel_lags.csv'),
        ('Q11b transportation services +0.8%', 'Contributions (pp of the +0.8): intracity transportation +0.39 (+6.6%, NSA; mass transit plus taxis/rideshares; split unverified), motor vehicle insurance +0.28, maintenance/repair +0.10, airfares +0.07, fees +0.06, other intercity +0.05, rental -0.14. Energy-linked by the data: airfares only (+0.07). Contributions use rounded published changes.', 'C_q11b_transport_services_decomp.csv; BLS cpi.t02 (Oct 2026)'),
        ('Q11b motor vehicle insurance +0.7%', 'Oct +0.71% m/m after a year of declines (May -1.69, Jun -2.01); ranks 42nd of 103 months; y/y Sep -4.98%. BLS factsheet: model-year updates "usually in October or November" often change premiums; no energy link. PCE net insurance +0.3% y/y vs CPI -5.0% (Sep).', 'C_q11b_motor_insurance.csv; BLS CPI motor vehicle insurance factsheet'),
    ]
    for k, row in enumerate(rows):
        for j, v in enumerate(row):
            c = put(ws, 6 + k, 1 + j, v)
            c.alignment = Alignment(wrap_text=True, vertical='top')
    rr = 6 + len(rows) + 1
    section(ws, rr, 'Q11 series table (Agent C, C_q11_confirming_items.csv; Feb 2026 = 100 levels and rates)')
    rr += 1
    X = rd('C_q11_confirming_items.csv')
    cols = list(X[0].keys())
    hdr_row(ws, rr, 1, cols)
    for x in X:
        rr += 1
        for j, k in enumerate(cols):
            v = num(x[k])
            put(ws, rr, 1 + j, v if v is not None else x[k], '0.0' if v is not None else None)
    ws.freeze_panes = 'A6'


def build_worthiness(ws):
    header(ws, 'Slide-worthiness: how strong a slide story each candidate exhibit makes (agents\' ratings and the coordinator\'s, side by side)',
           'Ratings 1-5 (5 = strongest slide story). Data plus a rating; not a slide design. Eli decides what goes on the slide.',
           'Source: report_A.md ... report_D.md "Slide-worthiness" sections; coordinator column from FINAL.md section 2. File: outputs/Z_slide_worthiness.csv.')
    X = rd('Z_slide_worthiness.csv')
    cols = list(X[0].keys())
    hdr_row(ws, 5, 1, cols, [30, 12, 14, 12, 60, 60])
    for k, x in enumerate(X):
        for j, c in enumerate(cols):
            v = num(x[c]) if c in ('agent_rating', 'stress_test_rating', 'coordinator_rating') else None
            cell = put(ws, 6 + k, 1 + j, v if v is not None else x[c])
            cell.alignment = Alignment(wrap_text=True, vertical='top')


SOURCES = [
    ('Tagged_breadth, Attribution, Breadth_measures, Sticky_flexible, Waller', 'raw_PCE_leaves', f'{cc.U20404_REL}; {cc.U20405_REL}; 02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_lines.csv; 02_Research/Subtasks/08_shock_tagging/proposed_tags.csv; outputs/B_q5_mapping.csv', 'https://apps.bea.gov/api/data (NIUnderlyingDetail U20404/U20405)', 'BEA Oct 29, 2026 release (saved 2026-11-10); Oct = UMD est. (2026-11-13)'),
    ('Breadth_measures, Tagged_breadth', 'raw_breadth_ts', 'outputs/B_q4_breadth_ts.csv; outputs/A_q3_tagged_breadth_ts.csv', 'n/a (computed through C_common.py)', 'run 2026-11-15'),
    ('Hospital_base_effect', 'raw_hospital', '03_Data/Raw/BLS_PPI_hospitals_2026-11-15/bls_api_ppi_hospitals_2016_2026.json; 03_Data/Raw/ALFRED_PCU622622_all_vintages_from2024-11_2026-11-11.json; 03_Data/Raw/BLS_PPI_detailed_report_2025-11_retrieved_2026-11-12.pdf', 'https://api.bls.gov/publicAPI/v2/timeseries/data/PCU622---622---', 'BLS pulled 2026-11-15; ALFRED 2026-11-11'),
    ('PPI_stages', 'raw_PPI_stages', '03_Data/Raw/BLS_PPI_stages_2026-11-15/bls_api_ppi_stages_2017_2026_batch1-5_2026-11-15.json; bls_ppi_news_release_*.htm', 'https://api.bls.gov/publicAPI/v2/timeseries/data/ ; https://www.bls.gov/news.release/ppi.nr0.htm', 'pulled 2026-11-15 (Oct PPI released 2026-11-13)'),
    ('PPI_stages', 'raw_oil', '03_Data/Raw/EIA_FRED_oil_daily_2026-11-15/', 'https://fred.stlouisfed.org/series/DCOILBRENTEU ; https://www.eia.gov/dnav/pet/hist/RBRTED.htm', 'retrieved 2026-11-15; last obs 2026-11-11'),
    ('Attribution', '(quote)', '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf', 'https://www.federalreserve.gov/newsevents/speech/bowman20261110a.htm', 'Nov 10, 2026'),
    ('Waller', '(quote)', '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Waller_economic_outlook.pdf', 'https://www.federalreserve.gov/newsevents/speech/waller20261110a.htm', 'Nov 10, 2026'),
    ('External', '(texts)', '02_Research/External_views/Fed_officials_2026-11/staff_notes/2026-10-01_Cajner_pricing_sentiment_ISM.html; 2026-11-09_DeMichelis_oil_core_inflation.html', 'https://www.federalreserve.gov/econres/notes/feds-notes/', 'Oct 1 and Nov 9, 2026'),
    ('Sticky_flexible', '(script values)', 'outputs/B_q5_*.csv; 03_Data/Raw/AtlantaFed_sticky_classification_2026-11-15/; 03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv', 'https://www.clevelandfed.org/publications/economic-commentary/2010/ec-201002-are-some-prices-in-the-cpi-more-forward-looking-than-others-we-think-so', 'Bryan & Meyer (2010)'),
    ('Breadth_measures (Q4b)', '(script values)', 'outputs/D_trimmed_reconcile.csv; outputs/Z_q4b_ex_oer_breadth.csv; 03_Data/pipelines/Price indexes/Trimmed mean/processed/dallas_trimmed_mean_rates.csv', 'https://www.dallasfed.org/research/pce', 'Dallas retrieved 2026-11-10'),
    ('Sticky_flexible (panel)', '(publisher rates)', '03_Data/pipelines/Price indexes/Sticky CPI/raw/atlantafed_sticky_price_cpi_2026-11-10.xlsx; outputs/Z_q5_atlanta_panel.csv', 'https://www.atlantafed.org/research-and-data/data/sticky-price-cpi', 'retrieved 2026-11-10'),
    ('Q1 (tags; report_A.md)', '(documents)', '03_Data/Raw/tariff_exemption_2026-11-15/ (DCPD-202500470.pdf; FR_2026-03824; FR_2026-15181; SCOTUS_learning_resources_v_trump.pdf)', 'https://www.govinfo.gov ; https://www.federalregister.gov ; https://www.supremecourt.gov', 'Apr 11, 2025 - Jul 28, 2026'),
]


def build_sources(ws):
    header(ws, 'Sources: every raw file and URL behind each tab', 'One row per raw input. Paths relative to the project root; outputs/ = 02_Research/Subtasks/10_slide2_research/outputs/.',
           'All files are saved locally; nothing in this workbook depends on a live link. Per-agent source lists: sources_A.md ... sources_D.md.')
    hdr_row(ws, 5, 1, ['Research tab(s)', 'Raw tab', 'File(s)', 'URL', 'Vintage'], [30, 18, 90, 60, 30])
    for i, row in enumerate(SOURCES):
        for j, v in enumerate(row):
            c = put(ws, 6 + i, 1 + j, v)
            c.alignment = Alignment(wrap_text=True, vertical='top')
    ws.freeze_panes = 'A6'


def build_needs(ws):
    header(ws, 'Judgment calls for Eli and scope/deliverable deviations (both positions), and paywalled links',
           'Items for Eli to decide or fetch. Copied from 06_Audits/slide2_research/STATUS.md (Judgment calls for Eli) via outputs/Z_judgment_calls.csv.', 'Paywalled lists: outputs/A_paywalled.csv, B_paywalled.csv, C_paywalled.csv.')
    hdr_row(ws, 5, 1, ['#', 'Item', 'Claude', 'Codex / other position', 'Affects tab', 'Status'], [5, 50, 55, 55, 22, 30])
    rr = 6
    for x in rd('Z_judgment_calls.csv'):
        for j, k in enumerate(['id', 'item', 'position_a', 'position_b', 'tab', 'status']):
            c = put(ws, rr, 1 + j, x[k])
            c.alignment = Alignment(wrap_text=True, vertical='top')
        rr += 1
    rr += 1
    section(ws, rr, 'Paywalled or blocked links (not accessed)')
    rr += 1
    hdr_row(ws, rr, 1, ['#', 'URL', 'Agent', 'What it would add'])
    k = 0
    for fname in ('A_paywalled.csv', 'B_paywalled.csv', 'C_paywalled.csv'):
        p = os.path.join(OUT, fname)
        if not os.path.exists(p):
            continue
        for x in rd(fname):
            k += 1
            rr += 1
            url = x.get('url', x.get('URL', ''))
            what = x.get('what_it_would_add', x.get('what', x.get('what it would add', '; '.join(f'{a}: {b}' for a, b in x.items() if a not in ('url', 'URL')))))
            for j, v in enumerate([k, url, fname[0], what]):
                c = put(ws, rr, 1 + j, v)
                c.alignment = Alignment(wrap_text=True, vertical='top')


DESCR = {
    'Attribution': 'Bowman-style shares of above-target core PCE by shock group (energy, tariff, AI, untagged), three allocation methods, Sep vs Oct est., 12m and 3m; her quote; chart.',
    'Tagged_breadth': 'Breadth within each tag group and its contribution to core breadth; Oct 12m change by tag (hospitals); sensitivities; monthly series; 149-leaf live calculation block.',
    'Breadth_measures': 'Breadth for core, supercore, core goods, core services (headline backup), Sep vs Oct est., 3m and 12m; 2018-19 averages; hospital effect; monthly charts.',
    'Sticky_flexible': 'Exploratory: sticky vs flexible PCE breadth via the BLS concordance (61% coverage) and an Atlanta Fed-style CPI basket.',
    'Waller': 'Waller\'s ">70%" on core services: count vs weighted, leaf vs sub-line, Sep and Oct est.',
    'Hospital_base_effect': 'Hospital m/m history; Oct 2025 jump vs its distribution; evidence it was measured, not filled.',
    'PPI_stages': 'PPI stages 1-4 (WPSID51-54), ID61/ID62, final demand: Oct vs Sep, series chart; energy within stages; daily oil and the early-Nov drop.',
    'External': 'ISM pricing-sentiment note (not public), FEDS oil note second half, airfares and freight confirming items.',
    'Slide_worthiness': 'Each agent\'s and the coordinator\'s rating of each candidate exhibit, side by side.',
    'Sources': 'Every raw file and URL behind each tab.',
    'Judgment_calls_and_paywalled': 'Judgment calls and scope deviations for Eli (both positions); paywalled links.',
}


def build_readme(ws, research, raws):
    header(ws, 'Slide 2 data workbook: "How widely has the energy shock spread, and at what scale?"',
           'Research data for Slide 2 of the UMD finals inflation section. One tab per research question that produced data; grey raw_ tabs at the end hold every series behind each number.',
           f'Built {BUILD_DATE} by {SCRIPT}. Vintages: BEA PCE Oct 29, 2026 release (through Sep 2026); Oct 2026 = UMD estimate (Nov 13, after PPI); BLS PPI pulled Nov 15 (Oct release Nov 13). Data cutoff: Nov 18, 2026.')
    rr = 5
    section(ws, rr, 'How to rebuild')
    rr += 1
    ws.cell(row=rr, column=1, value=f'From the project root:  python3 -I "02_Research/Subtasks/{SCRIPT}" --verify   (fix inputs in 10_slide2_research/outputs/ or raw files, never this xlsx, until Eli hand-edits it)')
    rr += 2
    section(ws, rr, 'Label key')
    for lbl, fill, txt in (('est.', FILL_EST, 'our estimate (UMD bottom-up October build); BEA publishes October PCE on Nov 25'),
                           ('carried forward', FILL_CF, 'value pulled earlier and not yet refreshed (none on this workbook\'s research tabs; Oct build "assumed" tier in slide 1)'),
                           ('key figure', FILL_KEY, 'figure most likely to be cited')):
        rr += 1
        c = ws.cell(row=rr, column=1, value=lbl)
        c.fill = fill
        c.font = F_BOLD
        ws.cell(row=rr, column=2, value=txt)
    rr += 2
    section(ws, rr, 'Contents (click to jump)')
    rr += 1
    hdr_row(ws, rr, 1, ['Tab', 'What it shows'], [28, 130])
    for n in research[1:] + raws:
        rr += 1
        c = ws.cell(row=rr, column=1, value=n)
        c.hyperlink = f"#'{n}'!A1"
        c.font = Font(color='0563C1', underline='single')
        ws.cell(row=rr, column=2, value=DESCR.get(n, 'raw data (grey tab): source file path, URL, vintage and notes in rows 2-5'))
    rr += 2
    section(ws, rr, 'Conventions')
    for t in ('Breadth = share of spending weight with inflation > 3%; 3m rates annualized before the cutoff; start-of-window weights; weighted leaf (149 core leaves) central, sub-line robustness (Eli).',
              'Live formulas wherever practical: click a cell to trace it to a raw tab. Script values carry a cell note naming the CSV. Every build checks the live values against the agents\' CSVs (semantic check).',
              'Status and audit trail: 02_Research/Subtasks/10_slide2_research/FINAL.md, report_A.md ... report_D.md, 06_Audits/slide2_research/.'):
        rr += 1
        ws.cell(row=rr, column=1, value=t)


# ============================================================================ main / verify
def main(verify=False):
    wb = Workbook()
    wb.remove(wb.active)
    research = ['README', 'Attribution', 'Tagged_breadth', 'Breadth_measures', 'Sticky_flexible', 'Waller', 'Hospital_base_effect', 'PPI_stages', 'External',
                'Slide_worthiness', 'Sources', 'Judgment_calls_and_paywalled']
    raws = ['raw_PCE_leaves', 'raw_breadth_ts', 'raw_hospital', 'raw_PPI_stages', 'raw_oil']
    S = {n: wb.create_sheet(n) for n in research + raws}
    LROW, LV = build_raw_leaves(S['raw_PCE_leaves'])
    TROW, TCOL, BTS, ATS = build_raw_ts(S['raw_breadth_ts'])
    for m in TROW:
        for c, col in TCOL.items():
            src = BTS[m] if c in BTS[m] else ATS[m]
            TV[(m, c)] = num(src[c])
    HROW, HV, hms = build_raw_hospital(S['raw_hospital'])
    PROW, PV, pms = build_raw_ppi(S['raw_PPI_stages'])
    OROW, OV = build_raw_oil(S['raw_oil'])
    calc, RNG, last_row = build_tagged(S['Tagged_breadth'], LROW, LV)
    build_tagged_series(S['Tagged_breadth'], TROW, TCOL, 120 + len(LROW) + 2)
    build_attribution(S['Attribution'], calc, RNG)
    build_measures(S['Breadth_measures'], calc, RNG, TROW, TCOL)
    build_sticky(S['Sticky_flexible'], calc, RNG)
    build_waller(S['Waller'], calc, RNG)
    build_hospital(S['Hospital_base_effect'], HROW, HV, hms)
    build_ppi(S['PPI_stages'], PROW, PV, pms, OROW, OV)
    build_external(S['External'])
    build_worthiness(S['Slide_worthiness'])
    build_sources(S['Sources'])
    build_needs(S['Judgment_calls_and_paywalled'])
    build_readme(S['README'], research, raws)
    semantic_check()
    os.makedirs(os.path.dirname(XLSX), exist_ok=True)
    wb.save(XLSX)
    print(f'saved {REL(XLSX)}: {len(EXPECT)} formula cells, {len(SEMANTIC)} semantic checks passed')
    chart_xml_check()
    if verify:
        run_verify()


def semantic_check():
    bad = []
    for sh, coord, want, lbl in SEMANTIC:
        got = EXPECT[(sh, coord)]
        tol = 0.051 if lbl.startswith(('B_q7', 'slide 1 hospital')) else (0.006 if 'reproduction' in lbl else 0.006 if lbl.startswith('A_q2') else 0.0015)
        if lbl.startswith(('A_q3 within', 'A_q3 contrib', 'A_q3 drop', 'B_q4', 'B_q5', 'B_q6', 'C_q8')):
            tol = 0.0015
        if abs(got - want) > max(tol, 1e-9) + (0.0006 if lbl.startswith(('B_q', 'A_q3')) else 0):
            bad.append((sh, coord, lbl, got, want))
    for b in bad:
        print('SEMANTIC MISMATCH', b)
    assert not bad, f'{len(bad)} semantic mismatches'


def chart_xml_check():
    import zipfile
    z = zipfile.ZipFile(XLSX)
    n_line = n_bar = 0
    for f in z.namelist():
        if f.startswith('xl/charts/chart'):
            x = re.sub(r'<(/?)c:', r'<\1', z.read(f).decode())   # openpyxl writes the chart namespace as default (no c: prefix)
            ns = x.count('<ser>')
            assert ns > 0, f'{f}: no series'
            if '<lineChart>' in x:
                assert x.count('<smooth val="0"/>') >= ns, f'{f}: missing smooth=0'
                n_line += 1
            if '<barChart>' in x:
                assert x.count('<invertIfNegative val="0"/>') >= ns, f'{f}: missing invertIfNegative=0'
                n_bar += 1
    assert n_line + n_bar == 10, f'expected 10 charts, found {n_line + n_bar}'
    print(f'chart XML check: {n_line} line charts with smooth val="0", {n_bar} bar charts with invertIfNegative val="0"')


def run_verify():
    scratch = os.environ.get('SLIDE2_SCRATCH', '/tmp')
    os.makedirs(scratch, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', scratch, XLSX], check=True, capture_output=True, timeout=600)
    rec = os.path.join(scratch, os.path.basename(XLSX))
    wb = load_workbook(rec, data_only=True)
    bad, errs = [], []
    for (sh, coord), exp in EXPECT.items():
        v = wb[sh][coord].value
        if isinstance(v, str) and v.startswith('#'):
            errs.append((sh, coord, v))
            continue
        if isinstance(exp, str):
            if str(v) != exp:
                bad.append((sh, coord, exp, v))
            continue
        if not isinstance(v, (int, float)) or abs(v - exp) > 1e-6 * max(1, abs(exp)):
            bad.append((sh, coord, exp, v))
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('#') and c.value[1:4] in ('REF', 'DIV', 'VAL', 'N/A', 'NAM', 'NUM', 'NUL'):
                    errs.append((ws.title, c.coordinate, c.value))
    rep = os.path.join(SUB, 'code', 'build_verify_report.txt')
    with open(rep, 'w') as f:
        f.write(f'LibreOffice recalculation check, {dt.datetime.now().isoformat(timespec="seconds")}\n')
        f.write(f'formula cells checked: {len(EXPECT)}; mismatches: {len(bad)}; error values: {len(errs)}; semantic checks vs agent CSVs: {len(SEMANTIC)} passed\n')
        for b in bad[:200]:
            f.write(f'MISMATCH {b}\n')
        for e in errs[:200]:
            f.write(f'ERROR {e}\n')
    print(open(rep).read()[:3000])
    if bad or errs:
        sys.exit(1)


if __name__ == '__main__':
    main(verify='--verify' in sys.argv)
