"""Brief A: map PCE pricing lines (Dallas leaves + line 218, and their sub-lines) to BLS series.

Authority: BEA Table 2.4.4U-D (Sep 30, 2026). Weights: U20405 (Sep 2026 nominal, vintage 2026-11-10).
Run from project root:  python3 02_Research/Subtasks/04_oct_pce_build/code/A_build_mapping.py
Writes outputs/component_mapping.csv, weight_shares.csv, manual_review_list.csv, series_to_fetch.csv,
plus A_coverage_gap.csv, A_parent_leaves.csv, A_hierarchy.csv, A_incore_check.csv.
"""
import os, re, sys, math
import pandas as pd
import openpyxl
sys.path.insert(0, os.path.dirname(__file__))
from A_common import *

os.makedirs(OUT, exist_ok=True)
sys.setrecursionlimit(5000)

# ---------------------------------------------------------------- inputs
t244 = load_t244()
num = {r['line']: r for r in t244 if r['line'] is not None}
subrows = {}
for r in t244:
    if r['line'] is None:
        subrows.setdefault(r['parent_line'], []).append(r)
assert len(num) == 356, len(num)

months = [f'{y}M{m:02d}' for y in (2024, 2025, 2026) for m in range(1, 13)]
months = [p for p in months if p <= PERIOD][-24:]
val, u_names = load_bea(U20405, set(months))
lines_with_data = sorted({l for (l, p) in val if l <= 356})
missing_in_u20405 = [l for l in range(1, 357) if l not in lines_with_data]

# name consistency T244 vs U20405 (strip BEA cross-reference parentheses)
name_mismatch = []
for l in lines_with_data:
    a = norm(re.sub(r'\s*\((?:\d+|parts? of[^)]*)\)\s*$', '', u_names[l]))
    b = norm(num[l]['name'])
    if a != b:
        name_mismatch.append((l, num[l]['name'], u_names[l]))


def sign(l):
    return -1.0 if num[l]['name'].lower().startswith('less') else 1.0


def v(l, p=PERIOD):
    return val[(l, p)]

# ---------------------------------------------------------------- hierarchy by additivity
# Line 159 'Tenant-occupied, including landlord durables' equals line 156 in value (alternative
# presentation; its U20404 price differs slightly). It is not additive at the 154 level, so it is
# excluded from the parse. Lines 157-158 are not published in U20405 and are attached to 156 below.
EXCLUDE = {159}
order = [l for l in lines_with_data if l not in EXCLUDE]
pos = {l: i for i, l in enumerate(order)}
end_memo, children = {}, {}


def close(acc, target, nterms):
    tol = 1.0 + 0.6 * nterms  # $ millions rounding
    return all(abs(acc[k] - target[k]) <= tol for k in range(len(months)))


def subtree_end(i):
    if i in end_memo:
        return end_memo[i]
    end_memo[i] = i + 1  # provisional (guards recursion)
    l = order[i]
    target = [v(l, p) for p in months]
    acc = [0.0] * len(months)
    j, kids = i + 1, []
    while j < len(order) and len(kids) < 60:
        c = order[j]
        acc = [acc[k] + sign(c) * v(c, months[k]) for k in range(len(months))]
        kids.append(c)
        j = subtree_end(j)
        if close(acc, target, len(kids)) and len(kids) >= 1:
            # single-child match is only accepted if values are identical (true duplicate)
            if len(kids) == 1 and not all(v(kids[0], p) == v(l, p) for p in months):
                pass
            else:
                children[l] = kids
                end_memo[i] = j
                return j
        if max(abs(a) for a in acc) > 6 * max(abs(t) for t in target) + 10:
            break
    children[l] = []
    end_memo[i] = i + 1
    return i + 1


assert subtree_end(0) == len(order), 'line 1 subtree does not cover the table'
children[156] = [157, 158]
children[157] = children[158] = []
parent = {c: p for p, ks in children.items() for c in ks}


def descendants(l):
    out = []
    for c in children.get(l, []):
        out.append(c)
        out += descendants(c)
    return out


def bottoms(l):
    ks = children.get(l, [])
    return [l] if not ks else [b for c in ks for b in bottoms(c)]


def path_sign(l, top):
    """Net sign of line l inside aggregate top (product of 'Less:' signs on the path)."""
    s, x = 1.0, l
    while x != top:
        s *= sign(x)
        x = parent[x]
    return s

# verify additivity of every parent for Sep 2026
add_check = []
for p, ks in children.items():
    if ks and p not in (156,):
        diff = v(p) - sum(sign(c) * v(c) for c in ks)
        add_check.append((p, len(ks), diff))
hier = pd.DataFrame([dict(line=l, name=num[l]['name'], parent=parent.get(l), n_children=len(children.get(l, [])),
                          sep2026_musd=val.get((l, PERIOD))) for l in range(1, 357)])
hier.to_csv(os.path.join(OUT, 'A_hierarchy.csv'), index=False)

TOTAL = v(1)
CORE_TOTAL_374 = load_bea(U20405, {PERIOD})[0][(374, PERIOD)]
food_energy_roots = [73, 113, 169]   # off-premises food & bev; gasoline & other energy goods; electricity & gas
fe_set = set(food_energy_roots) | {d for r in food_energy_roots for d in descendants(r)}

# ---------------------------------------------------------------- leaves and coverage
dal = pd.read_csv(DALLAS)
dal = dal[pd.to_numeric(dal.dallas_rank, errors='coerce').notna()].copy()
dal['dallas_rank'] = dal.dallas_rank.astype(float).astype(int)
dal['BEA_line'] = pd.to_numeric(dal.BEA_line, errors='coerce')
dal.loc[dal.dallas_rank == 88, 'BEA_line'] = 218   # per brief: rank 88 corresponds to BEA line 218
assert norm(num[218]['name']) == norm(dal.loc[dal.dallas_rank == 88, 'dallas_component'].iloc[0]), 'rank 88 name check'
dal['BEA_line'] = dal.BEA_line.astype(int)
leaves = dict(zip(dal.BEA_line, zip(dal.dallas_rank, dal.dallas_component)))
assert len(leaves) == 177

covered = set()
for l in leaves:
    covered |= set(bottoms(l))
# overlap check: no leaf is an ancestor of another
anc_overlap = [(a, b) for a in leaves for b in leaves if a != b and b in descendants(a)]
all_bottoms = bottoms(1)
uncovered = [b for b in all_bottoms if b not in covered]
leaf_share_sum = sum(v(l) for l in leaves) / TOTAL


def top_uncovered(b):
    """highest ancestor of b whose bottoms are all uncovered"""
    x = b
    while parent.get(x) and all(bb not in covered for bb in bottoms(parent[x])):
        x = parent[x]
    return x

gap_tops = sorted({top_uncovered(b) for b in uncovered})
u20404_val, u20404_names = load_bea(U20404, {PERIOD})
gap_rows = []
for g in gap_tops:
    gap_rows.append(dict(bea_line=g, name=num[g]['name'], sep2026_musd=v(g), net_sign=path_sign(g, 1),
                         share_of_headline=path_sign(g, 1) * v(g) / TOTAL,
                         price_index_in_U20404=(g, PERIOD) in u20404_val,
                         bea_source_text=num[g]['source'] or '(on sub-lines)'))
gap = pd.DataFrame(gap_rows)
resid = 1 - leaf_share_sum
gap.loc[len(gap)] = dict(bea_line='', name='TOTAL gap (1 - sum of 177 leaves incl. 218)', sep2026_musd=TOTAL - sum(v(l) for l in leaves),
                         net_sign='', share_of_headline=resid, price_index_in_U20404='', bea_source_text='')
gap.loc[len(gap)] = dict(bea_line=218, name='memo: line 218 share (rank 88, included above)', sep2026_musd=v(218), net_sign='',
                         share_of_headline=v(218) / TOTAL, price_index_in_U20404=True, bea_source_text='')
gap.to_csv(os.path.join(OUT, 'A_coverage_gap.csv'), index=False)

# ---------------------------------------------------------------- pricing lines


def has_source(l):
    r = num[l]
    if r['source']:
        return True
    return bool(subrows.get(l))


def pricing_lines(leaf):
    if has_source(leaf):
        return [leaf]
    out = []
    for c in children.get(leaf, []):
        out += pricing_lines(c) if not has_source(c) else [c]
    return out

# ---------------------------------------------------------------- BLS lists
items = load_bls_list(CU_ITEM)
item_by_norm = {norm(n): c for n, c in zip(items.item_name, items.item_code)}
item_name = dict(zip(items.item_code, items.item_name))
cus = load_bls_list(CU_SERIES)
cus_ids = dict(zip(cus.series_id, cus.end_year + cus.end_period))
ppi = pd.concat([load_bls_list(PC_SERIES)[['series_id', 'seasonal', 'series_title', 'end_year', 'end_period']],
                 load_bls_list(WP_SERIES)[['series_id', 'seasonal', 'series_title', 'end_year', 'end_period']]])
ppi_ids = dict(zip(ppi.series_id, ppi.end_year + ppi.end_period))
ppi_title = dict(zip(ppi.series_id, ppi.series_title))

man = pd.read_csv(os.path.join(CODE, 'A_manual_matches.csv'), dtype=str).fillna('')
man['pricing_bea_line'] = man.pricing_bea_line.astype(int)

# CPI relative importance, Dec 2025 (Table 1, CPI-U)
wb = openpyxl.load_workbook(CPI_RI, read_only=True)
ws = wb['Table 1']
ri_title = [r for r in ws.iter_rows(min_row=1, max_row=1, values_only=True)][0][1]
assert 'December 2025' in ri_title, ri_title
ri = {}
for r in ws.iter_rows(values_only=True):
    if r[1] and isinstance(r[2], (int, float)):
        ri.setdefault(norm(r[1]), r[2])


def cpi_info(code):
    sa, nsa = f'CUSR0000{code}', f'CUUR0000{code}'
    # an SA series counts as available only if it is still current in the BLS list
    return dict(sa=sa if cus_ids.get(sa, '') >= CURRENT else '', nsa=nsa if nsa in cus_ids else '',
                sa_end=cus_ids.get(sa, ''), nsa_end=cus_ids.get(nsa, ''))


def ppi_info(sid):
    sa = ('WPS' + sid[3:]) if sid.startswith('WPU') else ''
    sa = sa if sa in ppi_ids and ppi_ids[sa].startswith('2026') else ''
    return dict(sa=sa, nsa=sid if sid in ppi_ids else '', sa_end=ppi_ids.get(sa, ''), nsa_end=ppi_ids.get(sid, ''))


CURRENT = '2026M08'   # last period in the 2026-09-27 BLS series lists
STALE_CANDIDATES = {
    'SS45031': 'SETA01 (New vehicles) or SERC (Sporting goods) as proxy - our assumption',
    'SS61021': 'SERD01 (Photographic equipment and supplies) - our assumption',
    'SS62051': 'SERD02 (Photographers and photo processing) - our assumption',
    'SS62052': 'SERD02 (Photographers and photo processing) - our assumption',
    'SEHP01': 'no close current CPI; carry forward or SEHP02 (Gardening and lawncare services) - weak',
    'SEHP04': 'SAH3 (Household furnishings and operations) - weak',
    'SEHP': 'SAH3 (Household furnishings and operations) - weak',
}


def stale(sid):
    end = cus_ids.get(sid) or ppi_ids.get(sid) or ''
    return bool(sid) and end < CURRENT, end


def pick(seas, info):
    """series to use given BEA seasonal status for one input"""
    s = (seas or '').strip()
    if s == 'SA':
        return (info['sa'], 'N', '' if info['sa'] else 'BEA says SA but no current BLS SA series; NSA would need SA estimate')
    if s == 'NSA':
        return (info['nsa'], 'N', '')
    if s == 'SA by BEA':
        return (info['nsa'], 'Y', '')
    return (info['nsa'] or info['sa'], '', f'seasonal status not single-valued: {s}')


def resolve_input(line, frag, kind, code, seas):
    if kind == 'CPI':
        info = cpi_info(code)
        exact = norm(re.sub(r'^CPI (for )?', '', frag)) == norm(item_name.get(code, '#'))
    elif kind == 'PPI':
        info = ppi_info(code)
        exact = False
    else:
        return None
    sid, est, fl = pick(seas, info)
    return dict(code=code, kind=kind, info=info, use=sid, est=est, flag=fl, exact=exact)

# ---------------------------------------------------------------- classify each pricing line
JUDG = '& judgmental trend'
records, review = [], []
NPISH_RECEIPTS_QUOTE = num[356]['source']

for leaf, (rank, dname) in sorted(leaves.items(), key=lambda x: x[1][0]):
    pls = pricing_lines(leaf)
    leaf_in_core = 'N' if leaf in fe_set else 'Y'
    for pl in pls:
        r = num[pl]
        src, seas = r['source'], r['seasonal']
        subs = subrows.get(pl, [])
        flags = []
        if src is None and subs:
            srcs = {s['source'] for s in subs}
            seass = {s['seasonal'] for s in subs}
            if len(srcs) == 1:
                src, seas = srcs.pop(), seass.pop() if len(seass) == 1 else '; '.join(sorted(seass))
                flags.append('source on unnumbered sub-rows (' + ' / '.join(s['name'] for s in subs) + '); same series both')
        share = path_sign(pl, 1) * v(pl) / TOTAL if (pl, PERIOD) in val else math.nan
        within = (path_sign(pl, leaf) * v(pl) / v(leaf)) if ((pl, PERIOD) in val and pl != leaf) else (1.0 if pl == leaf else math.nan)
        rec = dict(dallas_rank=rank, dallas_component=dname, leaf_bea_line=leaf, pricing_bea_line=pl,
                   pricing_line_name=r['name'], is_subline='Y' if pl != leaf else 'N',
                   share_of_headline_sep2026=share, share_within_leaf=within, in_core=leaf_in_core,
                   bea_source_text=src if not (pl == 95) else (r['source'] + ' ' + '; '.join(f"{s['source']} [{s['seasonal']}]" for s in subs)),
                   bea_seasonal_status=seas if pl != 95 else '; '.join(f"{s['seasonal']}" for s in subs),
                   source_tag='', tier='', series_id_sa='', series_id_nsa='', series_to_use='', blend_inputs='',
                   needs_bea_sa_estimate='N', match_method='unmatched', flags='')
        if pl in (157, 158):
            flags.append('line not published in U20405: within-leaf weight unknown; proposed default 157=1.00, 158=0.00 '
                         '(line 159, priced by CPI rent alone, has the same Sep-2026 value as 156) - our assumption; estimate in backtest')
        mrows = man[man.pricing_bea_line == pl]
        low = src.lower() if src else ''
        is_blend = len(mrows[mrows.kind.isin(['CPI', 'PPI'])]) > 1 or pl == 95
        if pl == 356:
            # NPISH receipts priced at HCE prices of same services
            parts = []
            for m in mrows.itertuples():
                w = v(int(m.subrow)) / v(356)
                parts.append(f'BEA_L{m.code}(via U20405 L{m.subrow}):{w:.4f}')
            rec.update(source_tag='imputed', tier='proxied', blend_inputs=';'.join(parts), match_method='manual',
                       series_to_use='(HCE line prices, see blend_inputs)')
            flags.append(f'proxied: BEA text "{NPISH_RECEIPTS_QUOTE}"; HCE line mapping is our judgment (see A_manual_matches.csv)')
            review.append(dict(pricing_bea_line=pl, name=r['name'], issue='NPISH receipts priced at HCE prices; line mapping 358-368 -> HCE lines is judgment',
                               candidates='; '.join(f'L{m.subrow}->L{m.code} ({m.confidence})' for m in mrows.itertuples()), why=NPISH_RECEIPTS_QUOTE))
        elif is_blend:
            ins = []
            kinds = set()
            for m in mrows.itertuples():
                if m.kind not in ('CPI', 'PPI'):
                    continue
                s_in = m.bea_input_seasonal or seas
                ri_ = resolve_input(pl, m.source_fragment, m.kind, m.code, s_in)
                ins.append((m, ri_))
                kinds.add(m.kind)
            # proposed weights
            ws_ = []
            if all(m.weight_basis == 'cpi_ri' for m, _ in ins):
                raw = [ri.get(norm(item_name[m.code])) for m, _ in ins]
                if all(x is not None for x in raw):
                    ws_ = [x / sum(raw) for x in raw]
                    flags.append('blend weights = CPI-U relative importance Dec 2025 (our assumption; BEA weights not published)')
            if not ws_:
                ws_ = [None] * len(ins)
                flags.append('BEA blend weights not stated; proposal: ' +
                             ('CPI-U Dec-2025 relative importance where available, else estimate by regressing BEA line index on inputs (backtest)'
                              if kinds == {'CPI'} else 'equal weights or regression of BEA line index on inputs (backtest) - our assumption'))
            parts = [f"{x.get('use') or x['info']['nsa']}:{'NA' if w is None else f'{w:.4f}'}" for (m, x), w in zip(ins, ws_)]
            rec['blend_inputs'] = ';'.join(parts)
            rec['source_tag'] = 'blend' if len(kinds) > 1 or True else ''
            st = [(m.code, stale(x['use'])[1]) for m, x in ins if stale(x['use'])[0]]
            rec['tier'] = 'observed' if not st else 'assumed'
            for code_, end_ in st:
                flags.append(f'blend input {code_} not current in BLS list (last {end_}); blend treated as assumed; candidate: {STALE_CANDIDATES.get(code_, "none")}')
                review.append(dict(pricing_bea_line=pl, name=r['name'], issue=f'BEA-named CPI {code_} not published (last {end_})',
                                   candidates=STALE_CANDIDATES.get(code_, ''), why='BLS series list 2026-09-27 end period'))
            rec['needs_bea_sa_estimate'] = 'Y' if any(x['est'] == 'Y' for _, x in ins) else 'N'
            rec['match_method'] = 'exact' if all(x['exact'] for _, x in ins) else 'manual'
            rec['series_to_use'] = '(blend, see blend_inputs)'
            for (m, x) in ins:
                if x['flag']:
                    flags.append(f"{m.code}: {x['flag']}")
                if not x['use']:
                    flags.append(f'{m.code}: series ID not found in BLS list')
                if m.confidence != 'high':
                    review.append(dict(pricing_bea_line=pl, name=r['name'], issue=f'blend input match {m.confidence}',
                                       candidates=f'{m.code}; alt: {m.alternatives}', why=m.reason))
            if any(m.weight_basis == 'unstated' for m, _ in ins):
                review.append(dict(pricing_bea_line=pl, name=r['name'], issue='blend weights not stated by BEA',
                                   candidates=rec['blend_inputs'], why=src))
        elif low.startswith('cpi ') or low.startswith('ppi '):
            kind = src[:3].upper()
            frag = src.replace(JUDG, '').strip()
            if JUDG in src:
                flags.append('BEA adds judgmental trend: not replicable; CPI used alone')
                review.append(dict(pricing_bea_line=pl, name=r['name'], issue='judgmental component in BEA source',
                                   candidates='CPI part only', why=src))
            code, method, conf, alts, reason = None, 'unmatched', '', '', ''
            if kind == 'CPI' and norm(frag[4:]) in item_by_norm:
                code, method = item_by_norm[norm(frag[4:])], 'exact'
            elif len(mrows):
                m = mrows.iloc[0]
                code, method, conf, alts, reason = m.code, 'manual', m.confidence, m.alternatives, m.reason
            if code is None:
                rec.update(source_tag=kind, tier='assumed', match_method='unmatched')
                flags.append('no series match')
                review.append(dict(pricing_bea_line=pl, name=r['name'], issue='unmatched', candidates='', why=src))
            else:
                x = resolve_input(pl, frag, kind, code, seas)
                info = x['info']
                rec.update(source_tag=kind, tier='observed', series_id_sa=info['sa'], series_id_nsa=info['nsa'],
                           series_to_use=x['use'], needs_bea_sa_estimate=x['est'] or 'N', match_method=method)
                if x['flag']:
                    flags.append(x['flag'])
                if not x['use']:
                    flags.append('series ID not found in BLS list')
                is_st, end_ = stale(x['use'])
                if is_st:
                    rec['tier'] = 'assumed'
                    flags.append(f'BEA-named series {x["use"]} not current in BLS list (last {end_}): no October observation; '
                                 f'candidate: {STALE_CANDIDATES.get(code, "none")}; BEA may use unpublished BLS detail (unverified)')
                    review.append(dict(pricing_bea_line=pl, name=r['name'], issue=f'BEA-named series {x["use"]} not published (last {end_})',
                                       candidates=STALE_CANDIDATES.get(code, ''), why='BLS series list 2026-09-27 end period'))
                if (seas or '').strip() == 'NSA' and info['sa']:
                    flags.append('BEA uses NSA although BLS publishes SA')
                if method == 'manual' and conf != 'high':
                    review.append(dict(pricing_bea_line=pl, name=r['name'], issue=f'{kind} name match {conf}',
                                       candidates=f'{code}; alt: {alts}', why=reason))
                if kind == 'PPI':
                    flags.append(f'PPI title: {ppi_title.get(code, "?")}')
        else:
            # imputed: implicit, input-cost, USDA, foreign CPIs, BEA indexes
            rec.update(source_tag='imputed', tier='assumed', match_method='unmatched')
            if 'out months' in low and 'owners equivalent rent' in low:
                m = mrows.iloc[0]
                x = resolve_input(pl, m.source_fragment, 'CPI', m.code, seas)
                rec.update(tier='proxied', series_id_sa=x['info']['sa'], series_id_nsa=x['info']['nsa'],
                           series_to_use=x['use'], match_method='manual')
                q = re.search(r'"Out months"[^.]*\.', src)
                flags.append('proxied: BEA text ' + (q.group(0) if q else src))
            elif 'input cost' in low:
                flags.append('BEA input cost index (CES/ECI, PPIs, CPIs; weights unpublished): carried forward')
            elif 'usda' in low:
                flags.append('USDA prices received composite; not a BLS series; weights unpublished: carried forward')
            elif 'judgmental' in low or 'market indicators' in low:
                q = re.search(r'"?Out months[^.]*\.?', src)
                flags.append('out months judgmental: ' + (q.group(0) if q else ''))
            if rec['tier'] == 'assumed':
                review.append(dict(pricing_bea_line=pl, name=r['name'], issue='no replicable October input (assumed)',
                                   candidates='carry forward', why=src))
        rec['flags'] = ' | '.join(flags)
        records.append(rec)

cm = pd.DataFrame(records)
cols = ['dallas_rank', 'dallas_component', 'leaf_bea_line', 'pricing_bea_line', 'pricing_line_name', 'is_subline',
        'share_of_headline_sep2026', 'share_within_leaf', 'in_core', 'bea_source_text', 'bea_seasonal_status',
        'source_tag', 'tier', 'series_id_sa', 'series_id_nsa', 'series_to_use', 'blend_inputs',
        'needs_bea_sa_estimate', 'match_method', 'flags']
cm = cm[cols]
cm.to_csv(os.path.join(OUT, 'component_mapping.csv'), index=False)

# ---------------------------------------------------------------- parent leaves table
par = cm[cm.is_subline == 'Y'][['leaf_bea_line', 'dallas_component', 'pricing_bea_line', 'pricing_line_name',
                                 'share_within_leaf', 'share_of_headline_sep2026', 'tier']]
par.to_csv(os.path.join(OUT, 'A_parent_leaves.csv'), index=False)

# ---------------------------------------------------------------- in_core check vs components.csv
comp = pd.read_csv(COMPONENTS)
comp = comp[comp.index_name == 'PCE headline'].copy()
comp['line'] = comp.component_id.str.extract(r'U20405 line (\d+)').astype(float)
chk = []
for leaf in leaves:
    ours = 'N' if leaf in fe_set else 'Y'
    theirs = comp.loc[comp.line == leaf, 'in_core']
    theirs = theirs.iloc[0] if len(theirs) else 'missing'
    if ours != theirs:
        chk.append(dict(bea_line=leaf, name=num[leaf]['name'], in_core_bea_hierarchy=ours, in_core_components_csv=theirs,
                        share_of_headline=v(leaf) / TOTAL))
pd.DataFrame(chk).to_csv(os.path.join(OUT, 'A_incore_check.csv'), index=False)

# ---------------------------------------------------------------- weight shares
cm2 = cm.copy()
# lines 157/158: unpublished; allocate leaf 156 share to 157 (default) for share accounting
s156 = v(156) / TOTAL
cm2.loc[cm2.pricing_bea_line == 157, 'share_of_headline_sep2026'] = s156
cm2.loc[cm2.pricing_bea_line == 158, 'share_of_headline_sep2026'] = 0.0
core_cov = cm2.loc[cm2.in_core == 'Y', 'share_of_headline_sep2026'].sum()
rows = []
seas_group = cm2.bea_seasonal_status.fillna('none').map(lambda s: s if s in ('SA', 'NSA', 'SA by BEA') else ('none' if s == 'none' else 'mixed/other'))
for view in ('pricing_line_signed', 'leaf_net_npish_as_assumed'):
    d = cm2.copy()
    d['seas'] = seas_group
    if view == 'leaf_net_npish_as_assumed':
        npish = d[d.leaf_bea_line == 342]
        d = d[d.leaf_bea_line != 342]
        d = pd.concat([d, pd.DataFrame([dict(tier='assumed', source_tag='imputed', seas='mixed/other', in_core='Y',
                                             share_of_headline_sep2026=v(342) / TOTAL)])])
    for dim, col in (('tier', 'tier'), ('source_tag', 'source_tag'), ('bea_seasonal_status', 'seas')):
        for k, g in d.groupby(col):
            h = g.share_of_headline_sep2026.sum()
            c = g.loc[g.in_core == 'Y', 'share_of_headline_sep2026'].sum()
            rows.append(dict(view=view, dimension=dim, category=k, share_of_total_pce=h,
                             share_of_covered_pce=h / leaf_share_sum, share_of_core_line374=c * TOTAL / CORE_TOTAL_374,
                             share_of_covered_core=c / core_cov, n_pricing_lines=len(g)))
wsdf = pd.DataFrame(rows)
wsdf.loc[len(wsdf)] = dict(view='memo', dimension='denominators', category='covered PCE share; covered core / line 374',
                           share_of_total_pce=leaf_share_sum, share_of_covered_pce=1.0,
                           share_of_core_line374=core_cov * TOTAL / CORE_TOTAL_374, share_of_covered_core=1.0, n_pricing_lines=len(cm))
wsdf.to_csv(os.path.join(OUT, 'weight_shares.csv'), index=False)

# ---------------------------------------------------------------- series to fetch
need = {}


def add(sid, kind, line, role):
    if sid:
        need.setdefault(sid, dict(series_id=sid, kind=kind, lines=set(), roles=set()))
        need[sid]['lines'].add(int(line))
        need[sid]['roles'].add(role)

for r in cm.itertuples():
    if r.blend_inputs and r.pricing_bea_line != 356:
        for p in r.blend_inputs.split(';'):
            sid = p.split(':')[0]
            add(sid, 'CPI' if sid.startswith('CU') else 'PPI', r.pricing_bea_line, 'blend input (series_to_use)')
    if r.series_to_use and not str(r.series_to_use).startswith('('):
        add(r.series_to_use, 'CPI' if r.series_to_use.startswith('CU') else 'PPI', r.pricing_bea_line, 'series_to_use')
    # always fetch both SA and NSA for CPI single-series lines (diagnostics / SA estimates)
    for sid in (r.series_id_sa, r.series_id_nsa):
        if isinstance(sid, str) and sid:
            add(sid, 'CPI' if sid.startswith('CU') else 'PPI', r.pricing_bea_line, 'companion SA/NSA')
# blend inputs: also companion SA/NSA
for m in man.itertuples():
    if m.kind == 'CPI':
        i = cpi_info(m.code)
        for sid in (i['sa'], i['nsa']):
            if sid and m.pricing_bea_line in set(cm.pricing_bea_line):
                add(sid, 'CPI', m.pricing_bea_line, 'companion SA/NSA')
stf = pd.DataFrame([dict(series_id=k, kind=x['kind'],
                         seasonal='SA' if k.startswith(('CUSR', 'WPS')) else 'NSA',
                         end_in_bls_list=cus_ids.get(k) or ppi_ids.get(k, ''),
                         used_as_series_to_use='Y' if any('series_to_use' in s for s in x['roles']) else 'N',
                         bea_lines=';'.join(str(l) for l in sorted(x['lines'])))
                    for k, x in sorted(need.items())])
stf.to_csv(os.path.join(OUT, 'series_to_fetch.csv'), index=False)

rv = pd.DataFrame(review).drop_duplicates()
rv = rv.merge(cm[['pricing_bea_line', 'share_of_headline_sep2026']], on='pricing_bea_line', how='left')
rv.to_csv(os.path.join(OUT, 'manual_review_list.csv'), index=False)

# ---------------------------------------------------------------- stale-series evidence in local Nov-10 API pulls
import glob, json as _json
ev = []
stale_ids = sorted({x for x in stf.series_id if stale(x)[0]})
for f in sorted(glob.glob(os.path.join(PI, 'CPI', 'raw', 'bls_api_cpi_basket_*_2026-11-10.json'))):
    for srs in _json.load(open(f))['Results']['series']:
        if srs['seriesID'] in stale_ids:
            good = [d for d in srs['data'] if d['value'] not in ('-', '')]
            ev.append(dict(series_id=srs['seriesID'], file=os.path.basename(f),
                           latest_period_in_file=srs['data'][0]['year'] + srs['data'][0]['period'] if srs['data'] else '',
                           latest_valid_obs=(good[0]['year'] + good[0]['period']) if good else 'none'))
pd.DataFrame([dict(series_id=x, end_in_series_list=cus_ids.get(x) or ppi_ids.get(x)) for x in stale_ids]).merge(
    pd.DataFrame(ev, columns=['series_id', 'file', 'latest_period_in_file', 'latest_valid_obs']), on='series_id', how='left'
).to_csv(os.path.join(OUT, 'A_stale_series.csv'), index=False)

# ---------------------------------------------------------------- console summary
print('T244 numbered lines:', len(num), '| lines missing in U20405:', missing_in_u20405)
print('name mismatches T244 vs U20405:', len(name_mismatch))
for x in name_mismatch:
    print('   ', x)
bad = [x for x in add_check if abs(x[2]) > 1 + 0.6 * x[1]]
print('parents:', len(add_check), '| additivity failures Sep2026:', bad)
print('leaf overlaps:', anc_overlap)
print(f'leaf share sum {leaf_share_sum:.6f}; gap {resid:.6f}; 218 share {v(218)/TOTAL:.6f}')
print(gap.to_string())
print('parent leaves (no own source):', [l for l in leaves if not has_source(l)])
print('pricing lines:', len(cm), '| sublines:', (cm.is_subline == 'Y').sum())
print(cm.groupby(['tier'])['share_of_headline_sep2026'].sum())
print('match methods:', cm.match_method.value_counts().to_dict())
print('core covered (share of total PCE):', core_cov, ' line374/line1:', CORE_TOTAL_374 / TOTAL)
print('in_core disagreements vs components.csv:', len(chk))
print('series to fetch:', len(stf), stf.kind.value_counts().to_dict())
print('review items:', len(rv))
print(pd.read_csv(os.path.join(OUT, 'A_stale_series.csv')).to_string())
cc = comp.drop_duplicates('line')
print('components.csv in_core=Y weight sum:', cc.loc[cc.in_core == 'Y', 'weight_latest'].sum(), '| line374/line1:', CORE_TOTAL_374 / TOTAL)
