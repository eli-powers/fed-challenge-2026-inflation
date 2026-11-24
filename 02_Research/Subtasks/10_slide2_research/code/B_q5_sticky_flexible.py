"""Brief B, Q5 (exploratory): sticky vs flexible breadth.

Classification: Bryan & Meyer (2010), Cleveland Fed Economic Commentary 2010-02, Table 1 (the basis of the Atlanta Fed
sticky-price CPI): 45 CPI expenditure groups, sticky if prices change less often than every 4.3 months.
Saved: 03_Data/Raw/AtlantaFed_sticky_classification_2026-11-15/ (page HTML + PDF). The Atlanta Fed's xlsx
(03_Data/pipelines/Price indexes/Sticky CPI/raw/atlantafed_sticky_price_cpi_2026-11-10.xlsx) has only aggregate indexes,
no component list (checked).

Part A, PCE side (approach a): CPI ELI -> PCE series code (BLS concordance 03_Data/Raw/BLS_pce_cpi_code_mapping_2026-11-11.csv)
-> BEA U20404 line (series code DxxxRC -> DxxxRG; DTSPRC -> line 156) -> core leaf. Each ELI's class = class of its CPI
group (ELI first two letters / item stratum -> Bryan-Meyer group). A leaf is classified only if (1) every BEA pricing line
of the leaf is priced from CPIs (component_mapping.csv source_tag CPI, or a CPI-only blend), and (2) its ELIs give one class.
Mixed leaves: primary rule = leave out; alternative = majority by ELI count (ties left out). Both reported.
Breadth = audited engine (C_common.unit_table, leaf, start-of-window weights, rate > 3%).

Part B, CPI side cross-check: the 204 CPI-U leaf items in 03_Data/pipelines/Price indexes/CPI/processed/components.csv
(Sep 2026) and components_2026-10_approx_interp_oct2025_base.csv (Oct 2026; Oct 2025 base = sqrt(Sep x Nov 2025), NSA:
12m is approx.), weighted by start-of-window relative importance (weight_base_12m / weight_base_3m), rate > 3%.

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/B_q5_sticky_flexible.py"
Writes outputs/B_q5_mapping.csv, B_q5_sticky_flexible.csv, B_q5_sticky_flexible_ts.csv, B_q5_atlanta_basket.csv
"""
import json
import os
import sys

import numpy as np
import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
CONC = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_pce_cpi_code_mapping_2026-11-11.csv')
U20404 = os.path.join(ROOT, cc.U20404_REL)
CMAP = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'component_mapping.csv')
HIER = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'A_hierarchy.csv')
CPI_SEP = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'CPI', 'processed', 'components.csv')
CPI_OCT = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'CPI', 'processed', 'components_2026-10_approx_interp_oct2025_base.csv')
CPI_OCT_SH = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'CPI', 'processed', 'components_2026-10_short_horizon.csv')
ATL = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'Sticky CPI', 'raw', 'atlantafed_sticky_price_cpi_2026-11-10.xlsx')

# ---------------------------------------------------------------- Bryan-Meyer (2010) Table 1 groups, keyed by CPI stratum code
F, S = 'flexible', 'sticky'
BM = {  # stratum prefix (ELI first 2 letters, or 4 chars where a group is one stratum) -> (Bryan-Meyer group, class, freq months)
    'TB': ('Motor fuel', F, 0.7), 'TA04': ('Car and truck rental', F, 1.2), 'FK': ('Fresh fruits and vegetables', F, 1.3),
    'FL': ('Fresh fruits and vegetables', F, 1.3), 'HE': ('Fuel oil and other fuels', F, 1.5), 'HF': ('Gas (piped) and electricity', F, 1.6),
    'FC': ('Meats, poultry, fish, and eggs', F, 1.9), 'FD': ('Meats, poultry, fish, and eggs', F, 1.9), 'FE': ('Meats, poultry, fish, and eggs', F, 1.9),
    'FF': ('Meats, poultry, fish, and eggs', F, 1.9), 'FG': ('Meats, poultry, fish, and eggs', F, 1.9), 'FH': ('Meats, poultry, fish, and eggs', F, 1.9),
    'TA02': ('Used cars and trucks', F, 2.0), 'TA03': ('Leased cars and trucks', F, 2.0), 'TA01': ('New vehicles', F, 2.0),
    'AC': ("Women's and girls' apparel", F, 2.3), 'AD': ("Women's and girls' apparel", F, 2.3), 'FJ': ('Dairy and related products', F, 2.6),
    'FN': ('Nonalcoholic beverages, beverage materials', F, 2.7), 'FP': ('Nonalcoholic beverages, beverage materials', F, 2.7),
    'HB': ('Lodging away from home', F, 3.1), 'FM': ('Processed fruits and vegetables', F, 3.2), 'AA': ("Men's and boys' apparel", F, 3.2),
    'AB': ("Men's and boys' apparel", F, 3.2), 'FA': ('Cereals and bakery products', F, 3.3), 'FB': ('Cereals and bakery products', F, 3.3),
    'AE': ('Footwear', F, 3.4), 'FR': ('Other food at home', F, 3.6), 'FS': ('Other food at home', F, 3.6), 'FT': ('Other food at home', F, 3.6),
    'AG': ('Jewelry and watches', F, 3.9), 'TC': ('Motor vehicle parts and equipment', F, 4.1), 'GA': ('Tobacco and smoking products', F, 4.2),
    'AF': ("Infants' and toddlers' apparel", S, 5.3),
    'HH': ('Household furnishings and operations', S, 5.3), 'HJ': ('Household furnishings and operations', S, 5.3),
    'HK': ('Household furnishings and operations', S, 5.3), 'HL': ('Household furnishings and operations', S, 5.3),
    'HM': ('Household furnishings and operations', S, 5.3), 'HN': ('Household furnishings and operations', S, 5.3),
    'HP': ('Household furnishings and operations', S, 5.3), 'TD': ('Motor vehicle maintenance and repair', S, 5.8),
    'TE': ('Motor vehicle insurance', S, 5.9), 'MA': ('Medical care commodities', S, 6.2), 'MB': ('Medical care commodities', S, 6.2),
    'MF': ('Medical care commodities', S, 6.2), 'MG': ('Medical care commodities', S, 6.2), 'GB': ('Personal care products', S, 6.7),
    'FW': ('Alcoholic beverages', S, 7.3), 'FX': ('Alcoholic beverages', S, 7.3),
    'RA': ('Recreation', S, 7.9), 'RB': ('Recreation', S, 7.9), 'RC': ('Recreation', S, 7.9), 'RD': ('Recreation', S, 7.9),
    'RE': ('Recreation', S, 7.9), 'RF': ('Recreation', S, 7.9), 'RG': ('Recreation', S, 7.9),
    'GE': ('Miscellaneous personal goods', S, 8.1), 'EC': ('Communication', S, 8.4), 'ED': ('Communication', S, 8.4), 'EE': ('Communication', S, 8.4),
    'TG': ('Public transportation', S, 9.4), 'HD': ("Tenants' and household insurance", S, 10.1), 'FV': ('Food away from home', S, 10.7),
    'HA': ('Rent of primary residence', S, 11.0), 'HC': ("Owners' equivalent rent", S, 11.0), 'EA': ('Education', S, 11.1), 'EB': ('Education', S, 11.1),
    'MC': ('Medical care services', S, 14.0), 'MD': ('Medical care services', S, 14.0), 'ME': ('Medical care services', S, 14.0),
    'HG': ('Water, sewer, trash collection services', S, 14.3), 'TF': ('Motor vehicle fees', S, 16.4), 'GC': ('Personal care services', S, 23.7),
    'GD': ('Miscellaneous personal services', S, 25.9),
}


def bm_of(code):
    """code = ELI (e.g. 'FA011') or CPI item stratum without 'SE' (e.g. 'FA01', 'TA02')."""
    for k in (code[:4], code[:2]):
        if k in BM:
            return BM[k]
    return (None, None, None)


# ---------------------------------------------------------------- Part A: PCE leaves
conc = pd.read_csv(CONC)
d = json.load(open(U20404))['BEAAPI']['Results']['Data']
code2line = {}
for r in d:
    code2line.setdefault(r['SeriesCode'], int(r['LineNumber']))
conc['rg'] = conc.PCE_series_code.str[:-2] + 'RG'
conc['bea_line'] = conc.rg.map(code2line)
conc.loc[conc.PCE_series_code == 'DTSPRC', 'bea_line'] = 156   # tenant-occupied stationary homes (U20404 code IA000629)
conc[['bm_group', 'bm_class', 'bm_freq_months']] = conc.ELI.apply(lambda e: pd.Series(bm_of(e)))
UNCLASSIFIED_ELI = conc[conc.bm_class.isna()].copy()   # e.g. TA090 unsampled new and used motor vehicles: no single Bryan-Meyer group
print('ELIs with no Bryan-Meyer group (excluded from class votes):', UNCLASSIFIED_ELI.ELI.tolist())
conc = conc[conc.bm_class.notna()].copy()

# leaf descendants (for concordance codes that hit an aggregate line)
H = pd.read_csv(HIER)
children = H.groupby('parent').line.apply(list).to_dict()
specs = cc.specs
line2leaf = {ln: s['leaf'] for ln, s in specs.items()}
LEAVES = set(cc.LEAVES_ALL)


def leaf_targets(line):
    if pd.isna(line):
        return []
    line = int(line)
    if line in LEAVES:
        return [line]
    if line in line2leaf:
        return [line2leaf[line]]
    out, stack = [], [line]
    while stack:
        x = stack.pop()
        for c in children.get(x, []):
            if c in LEAVES:
                out.append(c)
            elif c in line2leaf:
                out.append(line2leaf[c])
            else:
                stack.append(c)
    return sorted(set(out))


conc['leaf_targets'] = conc.bea_line.apply(leaf_targets)
conc['via'] = conc.bea_line.apply(lambda l: 'none' if pd.isna(l) else ('leaf/sub-line' if (int(l) in LEAVES or int(l) in line2leaf) else 'aggregate->leaf descendants'))
direct = conc[conc.via == 'leaf/sub-line'].explode('leaf_targets')
agg = conc[conc.via == 'aggregate->leaf descendants'].explode('leaf_targets')
# descendants of an aggregate code count only for leaves with no direct ELI link
agg = agg[~agg.leaf_targets.isin(set(direct.leaf_targets))]
links = pd.concat([direct, agg]).dropna(subset=['leaf_targets'])
links['leaf'] = links.leaf_targets.astype(int)

# source of each leaf: all pricing lines CPI-based?
cm = pd.read_csv(CMAP)
cm = cm[cm.pricing_bea_line.isin(specs.keys())]


def cpi_line(r):
    if r.source_tag == 'CPI':
        return True
    if r.source_tag == 'blend':
        t = str(r.bea_source_text)
        return ('PPI' not in t) and ('CES' not in t) and ('ECI' not in t) and ('CPI' in t)
    return False


cm['cpi_sourced'] = cm.apply(cpi_line, axis=1)
leaf_src = cm.groupby('leaf_bea_line').agg(cpi_all=('cpi_sourced', 'all'), tags=('source_tag', lambda x: '|'.join(sorted(set(x)))),
                                          src=('bea_source_text', lambda x: ' || '.join(str(v)[:80] for v in x)))

rows = []
w_sep = cc.bn.loc[cc.P('2025-09')]   # 12m start-of-window weights for Sep 2026 (used only for the coverage share)
core = sorted(cc.SCOPES['core'])
for lf in core:
    L = links[links.leaf == lf]
    classes = L.bm_class.value_counts().to_dict()
    nS, nF = classes.get(S, 0), classes.get(F, 0)
    cpi_all = bool(leaf_src.cpi_all.get(lf, False))
    if not cpi_all:
        cls_strict, cls_major, reason = None, None, 'left out: priced (at least partly) from PPI / BEA input-cost / other non-CPI source'
    elif nS + nF == 0:
        cls_strict, cls_major, reason = None, None, 'left out: CPI-priced but no ELI in the BLS concordance points to this leaf'
    elif nS and nF:
        cls_strict = None
        cls_major = S if nS > nF else (F if nF > nS else None)
        reason = f'mixed ({nS} sticky ELIs, {nF} flexible ELIs): left out under primary rule'
    else:
        cls_strict = cls_major = S if nS else F
        reason = 'one consistent class'
    rows.append(dict(leaf=lf, name=cc.eng.names[lf], line_ge_150=lf >= 150, core_weight_sep2025_pct=100 * w_sep[lf] / w_sep[core].sum(),
                     pricing_source_tags=leaf_src.tags.get(lf, ''), all_lines_cpi_priced=cpi_all, n_eli=len(L), n_eli_sticky=nS, n_eli_flexible=nF,
                     eli_list=';'.join(L.ELI), bm_groups=';'.join(sorted(set(L.bm_group))), class_primary_leave_out_mixed=cls_strict,
                     class_alt_majority=cls_major, reason=reason, bea_source_text=leaf_src.src.get(lf, '')))
MAP = pd.DataFrame(rows)
MAP.to_csv(os.path.join(OUT, 'B_q5_mapping.csv'), index=False)

summ = []
for rule, col in (('primary: leave out mixed', 'class_primary_leave_out_mixed'), ('alt: majority by ELI count', 'class_alt_majority')):
    for cl in (S, F, None):
        g = MAP[MAP[col].isna()] if cl is None else MAP[MAP[col] == cl]
        summ.append(dict(rule=rule, cls=cl or 'unclassified', n_leaves=len(g), core_weight_pct=round(g.core_weight_sep2025_pct.sum(), 2)))
SUMM = pd.DataFrame(summ)
print(SUMM.to_string())
print(MAP.reason.str.split(':').str[0].value_counts())
print('mixed leaves:', MAP[MAP.reason.str.startswith('mixed')][['leaf', 'name', 'n_eli_sticky', 'n_eli_flexible', 'core_weight_sep2025_pct']].to_string())

# ---------------------------------------------------------------- PCE sticky/flexible breadth through the audited engine
res = []
sets = {}
for rule, col in (('primary', 'class_primary_leave_out_mixed'), ('alt_majority', 'class_alt_majority')):
    for cl in (S, F):
        sets[(rule, cl)] = set(MAP.leaf[MAP[col] == cl])
sets[('ref', 'core_all')] = set(core)
sets[('ref', 'covered_core')] = sets[('primary', S)] | sets[('primary', F)]


def br(leafset, end, back):
    t = cc.unit_table('leaf', leafset, end, back)
    return 100 * t.w[t.r > 3].sum() / t.w.sum(), len(t), t


for period in ('2026-09', '2026-10'):
    for back, hz in ((3, '3m_ann'), (12, '12m')):
        coreW = cc.unit_table('leaf', sets[('ref', 'core_all')], period, back).w.sum()
        for (rule, cl), ls in sets.items():
            v, n, t = br(ls, period, back)
            res.append(dict(side='PCE (BEA leaves, engine)', period=period, status='BEA published' if period == '2026-09' else 'est. (UMD October build)',
                            rule=rule, cls=cl, horizon=hz, method='leaf', value=round(v, 3), n_units=n,
                            share_of_core_weight_pct=round(100 * t.w.sum() / coreW, 2),
                            weight_basis=f'start-of-window nominal shares of {cc.P(period) - back}',
                            vintage='BEA U20404/U20405 vintage 2026-11-10'))
assert abs([r for r in res if r['cls'] == 'core_all' and r['period'] == '2026-09' and r['horizon'] == '12m'][0]['value'] - 60.626) < 0.01

# monthly series (primary rule)
ts = []
for m in [str(p) for p in pd.period_range('2018-01', '2026-10', freq='M')]:
    rec = dict(month=m, status='BEA published' if m <= '2026-09' else 'est.')
    for back, hz in ((3, '3m_ann'), (12, '12m')):
        for cl in (S, F):
            rec[f'{cl}_{hz}_leaf'] = round(br(sets[('primary', cl)], m, back)[0], 3)
        rec[f'covered_core_{hz}_leaf'] = round(br(sets[('ref', 'covered_core')], m, back)[0], 3)
    ts.append(rec)
TS = pd.DataFrame(ts)
pub = TS[TS.month <= '2026-09'].set_index('month')
avg = pub.loc['2018-01':'2019-12'].drop(columns='status').mean()
extra = [dict(month='avg_2018_2019', status='reference', **{c: round(avg[c], 3) for c in avg.index}),
         dict(month='peak_value', status='reference: max 2018-01..2026-09', **{c: pub[c].max() for c in avg.index}),
         dict(month='peak_month', status='reference', **{c: pub[c].idxmax() for c in avg.index})]
TS = pd.concat([TS, pd.DataFrame(extra)], ignore_index=True)
TS['note'] = 'primary rule (mixed leaves left out); weighted leaf, start-of-window weights, rate > 3%'
TS.to_csv(os.path.join(OUT, 'B_q5_sticky_flexible_ts.csv'), index=False)

# ---------------------------------------------------------------- Part B: Atlanta-Fed-style basket on CPI items
def cpi_frame(path):
    c = pd.read_csv(path)
    c = c[c.index_name == 'CPI-U headline'].copy()
    c['stratum'] = c.component_id.fillna('').str.replace(r'^CU[SU]R0000SE', '', regex=True).where(c.component_id.fillna('').str.match(r'^CU[SU]R0000SE'), '')
    c[['bm_group', 'bm_class', 'bm_freq']] = c.stratum.apply(lambda s: pd.Series(bm_of(s) if s else (None, None, None)))
    return c


cs, co, csh = cpi_frame(CPI_SEP), cpi_frame(CPI_OCT), cpi_frame(CPI_OCT_SH)
basket = []
unc = cs[cs.bm_class.isna()]
print('CPI items without stratum code/class:', len(unc), 'RI', unc.weight_latest.sum())
for period, c, src12 in (('2026-09', cs, 'components.csv (published 12m)'),
                         ('2026-10', co, 'components_2026-10_approx_interp_oct2025_base.csv (approx.: Oct 2025 = sqrt(Sep x Nov 2025), NSA)')):
    for hz, rcol, wcol in (('12m', 'pct_12m_calc', 'weight_base_12m'), ('3m_ann', 'pct_3m_ann_calc', 'weight_base_3m')):
        for scope in ('all items', 'core (ex food & energy)'):
            for cl in (S, F):
                g = c[(c.bm_class == cl)]
                if scope.startswith('core'):
                    g = g[g.in_core == 'Y']
                g = g.dropna(subset=[rcol, wcol])
                v = 100 * g[wcol][g[rcol] > 3].sum() / g[wcol].sum()
                # weighted mean rate as a sanity check vs the Atlanta Fed aggregate (not identical: aggregation differs)
                mr = (g[wcol] * g[rcol]).sum() / g[wcol].sum()
                status = 'BLS published' if period == '2026-09' else ('approx. (interpolated Oct 2025 base)' if hz == '12m' else 'BLS published (short horizon)')
                basket.append(dict(side='CPI items (Atlanta Fed-style basket)', period=period, status=status, scope=scope, cls=cl, horizon=hz,
                                   value=round(v, 3), n_items=len(g), ri_weight_covered=round(g[wcol].sum(), 3),
                                   weighted_mean_rate=round(mr, 3), weight_basis=f'{wcol} (start-of-window relative importance)',
                                   source=src12 if hz == '12m' else ('components.csv' if period == '2026-09' else 'components_2026-10_approx... (3m col)')))
B = pd.DataFrame(basket)
# Oct 3m in the approx file must equal the short-horizon file (same published indexes)
for cl in (S, F):
    a = co[co.bm_class == cl].set_index('component_id').pct_3m_ann_calc
    b = csh[csh.bm_class == cl].set_index('component_id').pct_3m_ann_calc
    j = pd.concat([a, b], axis=1).dropna()
    assert (j.iloc[:, 0] - j.iloc[:, 1]).abs().max() < 1e-9

# Atlanta Fed published aggregates, Sep and Oct 2026 (sanity comparison for weighted_mean_rate)
wb = openpyxl.load_workbook(ATL, read_only=True)
rows_ = [r for r in wb['Data'].iter_rows(values_only=True)]
hdr = rows_[0]
AT = pd.DataFrame([r for r in rows_[1:] if r[0] is not None], columns=hdr)
AT['month'] = pd.to_datetime(AT.Date).dt.to_period('M').astype(str)
cols = list(hdr)
atl = {}
for name, start in (('flexible all items', 1), ('flexible core', 5), ('sticky all items', 9), ('sticky core', 13)):
    for m in ('2026-09', '2026-10'):
        r = AT[AT.month == m]
        if len(r):
            atl[(name, m)] = (r.iloc[0, start + 2], r.iloc[0, start + 3])   # 3-mo a.r., 12mo
print('Atlanta Fed published (3m a.r., 12m):', atl)
B['atlanta_published_3m_ar'] = None
B['atlanta_published_12m'] = None
for i, r in B.iterrows():
    key = (f"{r.cls} {'all items' if r.scope == 'all items' else 'core'}", r.period)
    if key in atl:
        B.at[i, 'atlanta_published_3m_ar'] = atl[key][0]
        B.at[i, 'atlanta_published_12m'] = atl[key][1]
B.to_csv(os.path.join(OUT, 'B_q5_atlanta_basket.csv'), index=False)

OUTSF = pd.DataFrame(res)
OUTSF.to_csv(os.path.join(OUT, 'B_q5_sticky_flexible.csv'), index=False)
SUMM.to_csv(os.path.join(OUT, 'B_q5_coverage.csv'), index=False)
pd.set_option('display.width', 250)
print(OUTSF.pivot_table(index=['rule', 'cls', 'horizon'], columns='period', values=['value', 'share_of_core_weight_pct']))
print(B.drop(columns=['source', 'weight_basis', 'side']).to_string())
print(TS.tail(4).to_string())
