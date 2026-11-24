"""R3 (core CPI-PCE gap), raw_CPI and raw_BEA_9_1U tabs for the Slide 1 workbook.

Called from build_slide1_workbook.py. Effect values come from Agent B's scripts (code/B_core_gap.py ->
outputs/B_core_gap_sep.csv, B_core_gap_oct.csv, B_theme_summary.csv, B_headline_check.csv); the published
PCE and CPI rates and the gaps are live formulas over raw_CPI and TS_PCE_rates.
"""
import json
import math
import os

from openpyxl.chart import BarChart, Reference, Series
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

CPI_MONTHS = ['2025-06', '2025-07', '2025-09', '2025-11', '2026-06', '2026-07', '2026-09', '2026-10']


def _cpi_series(root):
    raw = os.path.join(root, '03_Data', 'pipelines', 'Price indexes', 'CPI', 'raw')
    files = [os.path.join(raw, f'bls_api_cpi_basket_2017_2026_batch{i}_2026-11-10.json') for i in range(1, 8)]
    out = {}
    for f in files:
        for s in json.load(open(f))['Results']['series']:
            out[s['seriesID']] = {f"{x['year']}-{x['period'][1:]}": float(x['value']) for x in s['data']
                                  if x['period'].startswith('M') and x['period'] != 'M13' and x['value'] not in ('-', '')}
    return out, files


SHORT = {
    'Shelter (OER, rent, hotels, housing at school)': 'Shelter',
    'Health care: third-party-paid medical (PCE-only scope)': 'Medical, 3rd-party paid (PCE-only)',
    'Health insurance (weight and price)': 'Health insurance',
    'Software (weight and price)': 'Software',
    'Motor vehicle insurance (weight and price)': 'Motor vehicle insurance',
    'Airfares (weight and price)': 'Airfares',
    'Core definition: restaurant meals in core PCE only': 'Restaurant meals (core PCE only)',
    'Core definition: alcohol at home in core CPI only': 'Alcohol at home (core CPI only)',
    'CPI-only items (vehicle fees, lawn care)': 'CPI-only items',
    'Formula (Fisher vs fixed weight)': 'Formula (Fisher vs fixed)',
    'CPI Jan-2026 weight update': 'CPI Jan-2026 reweight',
    'Residual (CPI replication)': 'Residual',
    'All other matched items (weight and price)': 'All other matched items',
}


def short_label(t):
    if t in SHORT:
        return SHORT[t]
    if t.startswith('Health care: in-scope'):
        return 'Medical, in-scope'
    if t.startswith('Financial:'):
        return 'Financial services (PCE-only)'
    if t.startswith('NPISH'):
        return 'NPISH, travel, other PCE-only'
    return t[:30]


def build(S, EXPECT, h):
    put, hdr_row, header, raw_meta, section, note = h['put'], h['hdr_row'], h['header'], h['raw_meta'], h['section'], h['note']
    rd, num, OUT, ROOT = h['rd'], h['num'], h['OUT'], h['ROOT']
    TS_ROW, TSV, FILL_EST, FILL_KEY = h['TS_ROW'], h['TSV'], h['FILL_EST'], h['FILL_KEY']

    # ------------------------------------------------------------------ raw_CPI
    ws = S['raw_CPI']
    ser, files = _cpi_series(ROOT)
    groups = rd(os.path.join(OUT, 'B_mapping_groups.csv'))
    codes = ['CUUR0000SA0L1E', 'CUSR0000SA0L1E', 'CUUR0000SA0', 'CUSR0000SA0']
    for g in groups:
        for part in g['cpi_items'].split(';'):
            c = part.strip().split('=')[0].strip()
            if c and c != 'no code' and not c.startswith('no ') and c.isalnum():
                sid = 'CUUR0000' + c
                if sid in ser and sid not in codes:
                    codes.append(sid)
    raw_meta(ws, 'BLS CPI-U index levels used in R3 (core and headline aggregates, plus the item indexes mapped to PCE groups)', [
        ('Source files', '03_Data/pipelines/Price indexes/CPI/raw/bls_api_cpi_basket_2017_2026_batch1-7_2026-11-10.json (B also uses 03_Data/Raw/bls_api_components_2015_2026_batch1-6_2026-11-13.json and the relative-importance xlsx files for weights)'),
        ('URL', 'https://api.bls.gov/publicAPI/v2/timeseries/data/ (CPI-U, U.S. city average); item list: https://www.bls.gov/cpi/'),
        ('Vintage', 'BLS Oct 2026 CPI release (Nov 10, 2026); BLS published no Oct 2025 CPI (shutdown), so Oct 2025 is blank'),
        ('Retrieved', '2026-11-10. CUUR = NSA, CUSR = SA; index base 1982-84=100 unless noted')])
    hdr_row(ws, 6, 1, ['Series ID', 'SA?'] + CPI_MONTHS, [18, 6] + [11] * len(CPI_MONTHS))
    CROW = {}
    for i, sid in enumerate(codes):
        r = 7 + i
        put(ws, r, 1, sid)
        put(ws, r, 2, 'SA' if sid.startswith('CUSR') else 'NSA')
        for j, m in enumerate(CPI_MONTHS):
            v = ser[sid].get(m)
            put(ws, r, 3 + j, v, '0.000')
        CROW[sid] = r
    ws.freeze_panes = 'C7'
    col = {m: get_column_letter(3 + j) for j, m in enumerate(CPI_MONTHS)}

    # ------------------------------------------------------------------ raw_BEA_9_1U
    ws = S['raw_BEA_9_1U']
    p = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'Cross-index analysis', 'raw', 'BEA_NIUnderlyingDetail_U90100_2026-11-10.json')
    data = json.load(open(p))['BEAAPI']['Results']['Data']
    raw_meta(ws, 'BEA Table 9.1U: Reconciliation of percent change in the CPI with percent change in the PCE price index (monthly, SA, pp)', [
        ('Source file', os.path.relpath(p, ROOT)),
        ('URL', 'https://apps.bea.gov/api/data (DataSetName=NIUnderlyingDetail, TableName=U90100, Frequency=M)'),
        ('Vintage', 'LastRevised Oct 29, 2026 (through Sep 2026); 2025M10 and 2025M11 absent (no CPI)'),
        ('Retrieved', '2026-11-10. Values are BEA\'s, rounded (0.1 for lines 1 and 39; 0.01 for effect lines)')])
    mths = sorted(set(r['TimePeriod'] for r in data if r['TimePeriod'] >= '2025M01'))
    lines = {}
    for r in data:
        lines.setdefault(int(r['LineNumber']), r['LineDescription'])
    vals = {(int(r['LineNumber']), r['TimePeriod']): num(r['DataValue']) for r in data}
    hdr_row(ws, 6, 1, ['Line', 'Description'] + mths + ['Sum Dec 2025 - Sep 2026'], [6, 60] + [9] * len(mths) + [14])
    sm = [m for m in mths if '2025M12' <= m <= '2026M09']
    c_a = get_column_letter(3 + mths.index(sm[0]))
    c_b = get_column_letter(3 + mths.index(sm[-1]))
    U_ROW = {}
    for i, ln in enumerate(sorted(lines)):
        r = 7 + i
        put(ws, r, 1, ln)
        put(ws, r, 2, lines[ln])
        for j, m in enumerate(mths):
            put(ws, r, 3 + j, vals.get((ln, m)), '0.00')
        s = sum(vals.get((ln, m)) or 0 for m in sm)
        put(ws, r, 3 + len(mths), f'=SUM({c_a}{r}:{c_b}{r})', '0.00', expect=s)
        U_ROW[ln] = (r, s)
    ws.freeze_panes = 'C7'
    sum_col = get_column_letter(3 + len(mths))

    # ------------------------------------------------------------------ R3_core_gap
    ws = S['R3_core_gap']
    header(ws, 'R3: Why does core PCE run above core CPI? Decomposing the gap, Sep 2026 (published) and Oct 2026 (est.)',
           'Core PCE minus core CPI, split into formula, weight, price, scope (items in only one index) and residual. UMD decomposition in two attribution conventions: BEA-style (inferred from Table 9.1U; not BEA\'s published core attribution) and centred on the matched-set mean. Data only.',
           'Units: percentage points. Sep: 12m, PCE SA vs CPI NSA (as published). Oct: approx. 12m (CPI Oct 2025 base interpolated as sqrt(Sep 2025 x Nov 2025); PCE = UMD est.) and 3m ann. SA. Rates draw on raw_CPI and TS_PCE_rates; effects from B_core_gap.py (cell notes).')
    hdr_row(ws, 5, 1, ['Comparison', 'Core PCE %', 'Core CPI %', 'Gap (PCE - CPI), pp'], [44, 13, 13, 13])
    hdr_row(ws, 5, 8, ['Basis'], [90])
    for _c in 'EFG':
        ws.column_dimensions[_c].width = 13
    cu, cs = CROW['CUUR0000SA0L1E'], CROW['CUSR0000SA0L1E']
    lv = lambda sid, m: ser[sid][m]
    cmp_rows = {}
    # Sep 12m
    cpi_sep = (lv('CUUR0000SA0L1E', '2026-09') / lv('CUUR0000SA0L1E', '2025-09') - 1) * 100
    cpi_oct12 = (lv('CUUR0000SA0L1E', '2026-10') / math.sqrt(lv('CUUR0000SA0L1E', '2025-09') * lv('CUUR0000SA0L1E', '2025-11')) - 1) * 100
    cpi_oct3 = ((lv('CUSR0000SA0L1E', '2026-10') / lv('CUSR0000SA0L1E', '2026-07')) ** 4 - 1) * 100
    spec = [
        ('Sep 2026, 12m (published)', f"=TS_PCE_rates!H{TS_ROW['2026-09']}", TSV[('2026-09', 'core')]['12m'],
         f"=(raw_CPI!{col['2026-09']}{cu}/raw_CPI!{col['2025-09']}{cu}-1)*100", cpi_sep, 'PCE U20404 line 374 = T20804 line 25 (SA); CPI CUUR0000SA0L1E (NSA)', None),
        ('Oct 2026, approx. 12m (PRIMARY for Oct; est.)', f"=TS_PCE_rates!H{TS_ROW['2026-10']}", TSV[('2026-10', 'core')]['12m'],
         f"=(raw_CPI!{col['2026-10']}{cu}/SQRT(raw_CPI!{col['2025-09']}{cu}*raw_CPI!{col['2025-11']}{cu})-1)*100", cpi_oct12,
         'CPI Oct 2025 base = sqrt(Sep 2025 x Nov 2025) (BLS published no Oct 2025 CPI); error of this base is not bounded', FILL_EST),
        ('Oct 2026, 3m annualized (alternate; est.)', f"=TS_PCE_rates!F{TS_ROW['2026-10']}", TSV[('2026-10', 'core')]['3m'],
         f"=((raw_CPI!{col['2026-10']}{cs}/raw_CPI!{col['2026-07']}{cs})^4-1)*100", cpi_oct3, 'Jul -> Oct 2026, both SA; CPI fully published, noisier horizon', FILL_EST),
    ]
    r = 6
    for lbl, fp, vp, fc, vc, basis, fill in spec:
        put(ws, r, 1, lbl, bold=True, fill=fill)
        put(ws, r, 2, fp, h['FMT_RATE'], expect=vp, fill=fill)
        put(ws, r, 3, fc, h['FMT_RATE'], expect=vc)
        put(ws, r, 4, f'=B{r}-C{r}', '0.000', expect=vp - vc, fill=FILL_KEY)
        put(ws, r, 8, basis)
        cmp_rows[lbl] = (r, vp - vc)
        r += 1
    # effect subtotals
    sep = rd(os.path.join(OUT, 'B_core_gap_sep.csv'))
    octr = rd(os.path.join(OUT, 'B_core_gap_oct.csv'))
    sub = {}
    for x in sep:
        if x['effect'] == 'subtotal':
            sub[('sep', x['item'])] = (num(x['pp']), num(x['pp_centered_alt']))
    for x in octr:
        if x['effect'] == 'subtotal':
            sub[(x['comparison'], x['item'])] = (num(x['pp']), num(x['pp_centered_alt']))
    r += 1
    section(ws, r, 'Gap by effect (pp). Each column sums to the gap above (check row). BEA-style = UMD decomposition using a convention inferred from Table 9.1U; Centred = vs matched-set mean')
    r += 1
    comps = [('sep', 'Sep 12m'), ('approx_12m', 'Oct approx. 12m (est.)'), ('3m_annualized', 'Oct 3m ann. (est.)')]
    hdr = ['Effect']
    for _, lbl in comps:
        hdr += [f'{lbl}: BEA-style', f'{lbl}: Centred']
    hdr_row(ws, r, 1, hdr)
    EFF = [('formula', 'Formula (chained Fisher vs fixed weight)'), ('weight', 'Weight (same item, different share)'),
           ('price', 'Price (same item, different price measure)'), ('scope_PCE_only', 'Scope: items only in core PCE'),
           ('scope_CPI_only', 'Scope: items only in core CPI'), ('other', 'Other (CPI Jan-2026 weight update)'),
           ('residual', 'Residual (CPI replication error)')]
    e0 = r + 1
    for k, lbl in EFF:
        r += 1
        put(ws, r, 1, lbl)
        for j, (ck, _) in enumerate(comps):
            b, c = sub[(ck, k)]
            c1 = put(ws, r, 2 + 2 * j, b, '0.000')
            put(ws, r, 3 + 2 * j, c, '0.000')
            if j == 0 and k == 'formula':
                note(c1, 'Effect values from 09_slide1_research/code/B_core_gap.py (outputs/B_core_gap_*.csv, subtotal rows). Item-level detail in those CSVs.')
    e1 = r
    r += 1
    put(ws, r, 1, 'Sum of effects', bold=True)
    gaps = [cmp_rows[s[0]][1] for s in spec]
    for j, (ck, _) in enumerate(comps):
        for k2 in (0, 1):
            cc = get_column_letter(2 + 2 * j + k2)
            put(ws, r, 2 + 2 * j + k2, f'=SUM({cc}{e0}:{cc}{e1})', '0.000', expect=sum(sub[(ck, k)][k2] for k, _ in EFF))
    r += 1
    put(ws, r, 1, 'Check: sum minus gap (should be ~0)', bold=True)
    for j in range(3):
        gr = cmp_rows[spec[j][0]][0]
        for k2 in (0, 1):
            cc = get_column_letter(2 + 2 * j + k2)
            put(ws, r, 2 + 2 * j + k2, f'={cc}{r - 1}-$D${gr}', '0.000',
                expect=sum(sub[(comps[j][0], k)][k2] for k, _ in EFF) - gaps[j])
    # R1-F03: visible caveat beside the principal decomposition
    sens = [x for x in rd(os.path.join(OUT, 'B_sensitivity_sep.csv')) if x['run'] == 'no_medical_split']
    sv = {x['effect']: num(x['pp_bea_convention']) for x in sens}
    r += 1
    put(ws, r, 1, 'CAVEAT: the allocation across weight / price / scope is a UMD estimate. It assumes the in-scope (household-paid) share of PCE medical '
        f'items = 0.648 x the CPI share. Without that split (Sep, BEA-style): weight {sv["weight"]:+.3f}, price {sv["price"]:+.3f}, PCE-only scope '
        f'{sv["scope_PCE_only"]:+.3f}; the total gap is unchanged. The headline run matches several 9.1U lines (shelter, imputed financial services, NPISH, airfares) '
        'but not gasoline, foreign travel or CPI-only scope: a partial cross-check, not validation of every allocation (B_sensitivity_sep.csv; report_B.md).')
    note(ws.cell(row=r, column=1), 'Added after Codex audit R1-F03.')
    # themes
    th = rd(os.path.join(OUT, 'B_theme_summary.csv'))
    runs = []
    for x in th:
        if x['run'] not in runs:
            runs.append(x['run'])
    r += 2
    section(ws, r, 'Gap by theme (pp): the items behind the spoken line. Sum = gap')
    r += 1
    th_hdr = ['Theme']
    RUN_LBL = {'core_sep_12m': 'Sep 12m', 'core_oct_12m_approx': 'Oct approx. 12m (est.)', 'core_oct_3m_ann': 'Oct 3m ann. (est.)'}
    for rn in runs:
        th_hdr += [f'{RUN_LBL.get(rn, rn)}: BEA-style', f'{RUN_LBL.get(rn, rn)}: Centred']
    hdr_row(ws, r, 1, th_hdr)
    themes = [x['theme'] for x in th if x['run'] == runs[0] and not x['theme'].startswith('TOTAL')]
    t0 = r + 1
    TH = {}
    for t in themes:
        r += 1
        put(ws, r, 1, t)
        for j, rn in enumerate(runs):
            x = [y for y in th if y['run'] == rn and y['theme'] == t]
            if x:
                put(ws, r, 2 + 2 * j, num(x[0]['pp_bea_convention']), '0.000')
                put(ws, r, 3 + 2 * j, num(x[0]['pp_centered_alt']), '0.000')
                TH[(rn, t)] = (num(x[0]['pp_bea_convention']), num(x[0]['pp_centered_alt']), r)
    t1 = r
    r += 1
    put(ws, r, 1, 'TOTAL (sum of themes) = gap', bold=True)
    for j, rn in enumerate(runs):
        for k2 in (0, 1):
            cc = get_column_letter(2 + 2 * j + k2)
            put(ws, r, 2 + 2 * j + k2, f'=SUM({cc}{t0}:{cc}{t1})', '0.000',
                expect=sum(TH[(rn, t)][k2] for t in themes if (rn, t) in TH), fill=FILL_KEY)
    note(ws.cell(row=t0, column=2), 'Values from B_core_gap.py (outputs/B_theme_summary.csv).')
    # waterfall data (Sep 12m), both conventions
    r += 2
    section(ws, r, 'Waterfall chart data, Sep 2026 12m: from core CPI to core PCE by theme (base = invisible offset)')
    sep_gr = cmp_rows[spec[0][0]][0]
    charts_at = ['I12', 'I40']
    for conv_i, conv in enumerate(('BEA-style convention, UMD decomposition', 'Centred, UMD decomposition')):
        r += 1
        hdr_row(ws, r, 1, [f'Step ({conv})', 'Base (hidden)', 'Up', 'Down', 'Level (core CPI / core PCE)'])
        w0 = r + 1
        r += 1
        put(ws, r, 1, 'Core CPI, 12m')
        put(ws, r, 7, 'Core CPI, 12m')
        put(ws, r, 2, 0, '0.000')
        put(ws, r, 3, 0, '0.000')
        put(ws, r, 4, 0, '0.000')
        put(ws, r, 5, f'=C{sep_gr}', '0.000', expect=cpi_sep)
        cum = cpi_sep
        lows = [cpi_sep]
        prev_cum_cell = f'E{r}'
        steps = sorted([(t, TH[(runs[0], t)]) for t in themes if (runs[0], t) in TH], key=lambda z: -abs(z[1][conv_i]))
        for t, (vb, vc_, trow) in steps:
            r += 1
            v = (vb, vc_)[conv_i]
            src = f'{get_column_letter(2 + conv_i)}{trow}'
            put(ws, r, 1, t[:48])
            put(ws, r, 7, short_label(t))
            before, after = cum, cum + v
            put(ws, r, 2, f'=MIN({prev_cum_cell},{prev_cum_cell}+{src})', '0.000', expect=min(before, after))
            put(ws, r, 3, f'=MAX({src},0)', '0.000', expect=max(v, 0))
            put(ws, r, 4, f'=MAX(-{src},0)', '0.000', expect=max(-v, 0))
            put(ws, r, 5, 0, '0.000')
            # running total kept in column F (helper)
            put(ws, r, 6, f'={prev_cum_cell}+{src}', '0.000', expect=after)
            prev_cum_cell = f'F{r}'
            cum = after
            lows.append(after)
        r += 1
        put(ws, r, 1, 'Core PCE, 12m')
        put(ws, r, 7, 'Core PCE, 12m')
        put(ws, r, 2, 0, '0.000')
        put(ws, r, 3, 0, '0.000')
        put(ws, r, 4, 0, '0.000')
        put(ws, r, 5, f'=B{sep_gr}', '0.000', expect=TSV[('2026-09', 'core')]['12m'])
        w1 = r
        hdr_row(ws, w0 - 1, 6, ['Running total', 'Chart label'])
        bc = BarChart()
        bc.type = 'col'
        bc.grouping = 'stacked'
        bc.overlap = 100
        floor = math.floor((min(lows) - 0.15) * 5) / 5     # axis floor below the lowest running total, so no step is clipped
        h['style_chart'](bc, f'Core CPI to core PCE, Sep 2026 12m, by theme ({conv})', f'Percent, 12m (axis starts at {floor:.1f})', 'Theme (largest step first)',
                         'Source: BLS CPI-U; BEA PCE U20404/U20405; UMD decomposition (B_core_gap.py), convention inferred from BEA Table 9.1U', w=30, h=14, yfmt='0.0')
        for cidx, color in ((2, None), (3, '70AD47'), (4, 'C00000'), (5, '2F5597')):
            s = Series(Reference(ws, min_col=cidx, min_row=w0, max_row=w1), title=ws.cell(row=w0 - 1, column=cidx).value)
            if color is None:
                s.graphicalProperties.noFill = True
                s.graphicalProperties.line.noFill = True
            else:
                s.graphicalProperties.solidFill = color
            bc.series.append(s)
        bc.set_categories(Reference(ws, min_col=7, min_row=w0, max_row=w1))
        bc.y_axis.scaling.min = floor
        bc.gapWidth = 40
        bc.legend.legendEntry = [h['LegendEntry'](idx=0, delete=True)]   # hide the invisible base series from the legend
        h['add_chart'](ws, bc, charts_at[conv_i])
        r += 1
    # headline check
    hc = rd(os.path.join(OUT, 'B_headline_check.csv'))
    r += 1
    section(ws, r, 'Method check on headline: our decomposition vs BEA Table 9.1U, summed Dec 2025 - Sep 2026 (pp; Oct/Nov 2025 absent)')
    r += 1
    hdr_row(ws, r, 1, ['Item', 'BEA 9.1U', 'Ours', 'Ours minus BEA'])
    hdr_row(ws, r, 8, ['Note'])
    for x in hc:
        if x['block'] != 'monthly_sum_Dec25_Sep26':
            continue
        r += 1
        b, o = num(x['bea_9_1U_pp']), num(x['ours_pp'])
        put(ws, r, 1, x['item'])
        c = put(ws, r, 2, b, '0.00')
        put(ws, r, 3, o, '0.000')
        if b is not None and o is not None:
            put(ws, r, 4, f'=C{r}-B{r}', '0.000', expect=o - b)
        put(ws, r, 8, x['note'])
    note(ws.cell(row=r, column=2), f'BEA values: sums of raw_BEA_9_1U rows over Dec 2025 - Sep 2026 (column {sum_col}); ours from B_core_gap.py (outputs/B_headline_check.csv).')
    r += 1
    put(ws, r, 1, f'BEA monthly sums are in raw_BEA_9_1U column {sum_col} (live SUM formulas). Line 14 (rent of shelter) = {U_ROW.get(14, (0, 0))[1]:.2f}.')
    ws.freeze_panes = 'B6'
