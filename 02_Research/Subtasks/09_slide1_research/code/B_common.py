"""B_common.py: shared engine for brief B (core CPI-PCE gap reconciliation).

Run nothing here directly; B_core_gap.py imports it. Run from the project root:
    python3 -I "02_Research/Subtasks/09_slide1_research/code/B_core_gap.py"

Method (adapted from the structure of BEA Table 9.1U; BEA's own item-level shares are unpublished):
  gap = PCE_pub - CPI_pub
      = formula   [PCE_pub (chained Fisher) - PCE_L (fixed-weight Laspeyres, base-period nominal shares)]
      + scope_P   [sum over PCE-only items k: s_k * (pi_k - Pc)]
      + scope_C   [sum over CPI-only items m: -R_m * (pi_m - Cc)]
      + weight    [sum over matched groups g: (s~_g - R~_g) * (piC_g - Cc)]   (evaluated at CPI prices)
      + price     [sum over matched groups g: s~_g * (piP_g - piC_g)]        (evaluated at PCE weights)
      + chain     [CPI single-base Laspeyres - CPI two-segment (Jan-2026 weight update) aggregate]
      + residual  [our CPI aggregate - published CPI]
  s = PCE nominal share at base month; R = CPI relative importance (RI-updated to base month);
  s~, R~ = shares renormalised within the matched (common-scope) set; Pc, Cc = matched-set means.
  The identity is exact by construction; only the residual row is "unexplained".
"""
import csv, json, math, os, re
import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research')
OUT = os.path.join(SUB, 'outputs')
PI = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes')
PCE_RAW = os.path.join(PI, 'PCE', 'raw')
CPI_RAW = os.path.join(PI, 'CPI', 'raw')
RAW = os.path.join(ROOT, '03_Data', 'Raw')
OCT = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs')

F_U20404 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')
F_U20405 = os.path.join(PCE_RAW, 'BEA_NIUnderlyingDetail_U20405_2026-11-10.json')
F_HIER = os.path.join(OCT, 'A_hierarchy.csv')
F_DLINES = os.path.join(OCT, 'D_build_2026-10_lines.csv')
F_DSUM = os.path.join(OCT, 'D_build_2026-10_summary.csv')
F_U90100 = os.path.join(PI, 'Cross-index analysis', 'raw', 'BEA_NIUnderlyingDetail_U90100_2026-11-10.json')
F_RI = {'old': os.path.join(CPI_RAW, 'bls_cpi_relative_importance_2024_2026-11-10.xlsx'),   # Dec 2024 RI, 2023 weights
        'new': os.path.join(CPI_RAW, 'bls_cpi_relative_importance_2025_2026-11-10.xlsx')}   # Dec 2025 RI, 2024 weights
F_CUITEM = os.path.join(RAW, 'bls_cu_item_2026-11-11.txt')
CPI_JSON = ([os.path.join(CPI_RAW, f'bls_api_cpi_basket_2017_2026_batch{i}_2026-11-10.json') for i in range(1, 8)]
            + [os.path.join(RAW, f'bls_api_components_2015_2026_batch{i}_2026-11-13.json') for i in range(1, 7)])

LINK = '2025M12'   # CPI weight-update link month (2024 weights from Jan 2026)

# ---------------------------------------------------------------- periods
def pkey(p):
    y, m = p.split('M'); return int(y) * 12 + int(m) - 1
def padd(p, k):
    n = pkey(p) + k; return f'{n // 12}M{n % 12 + 1:02d}'

# ---------------------------------------------------------------- PCE
def _bea(path):
    d = json.load(open(path))['BEAAPI']['Results']['Data']
    out = {}
    for x in d:
        v = x['DataValue'].replace(',', '')
        if v in ('', '---', '(NA)'): continue
        out.setdefault(int(x['LineNumber']), {})[x['TimePeriod']] = float(v)
    return out

PCE_IDX = _bea(F_U20404)
PCE_NOM = _bea(F_U20405)
HEADLINE_LINE, CORE_LINE = 1, 374

def load_hierarchy():
    rows = list(csv.DictReader(open(F_HIER)))
    return {int(r['line']): (r['name'], int(float(r['parent'])) if r['parent'] else None, int(r['n_children'])) for r in rows}

HIER = load_hierarchy()
# Net aggregates treated as single atoms (their children contain "Less:" lines that enter negatively)
NET_ATOMS = {146, 149, 156, 272, 334, 338, 342}
# Net foreign travel (333) and net expenditures abroad (145) have no BEA price index; they enter as their
# gross components, with the 'Less:' lines carrying negative nominal weight.
NEG_LINES = {149, 338}
def _under(line, anc):
    p = HIER[line][1]
    while p is not None:
        if p == anc: return True
        p = HIER[p][1]
    return False
def pce_atoms():
    atoms = []
    for ln, (nm, par, nch) in HIER.items():
        if ln in (159, 145, 333): continue                      # addendum line (no parent), duplicates 156
        if ln in NET_ATOMS: atoms.append(ln); continue
        if nch == 0 and not any(_under(ln, a) for a in NET_ATOMS): atoms.append(ln)
    return sorted(atoms)
ATOMS = pce_atoms()
PCE_NONCORE = set(range(73, 104)) | set(range(113, 120)) | set(range(169, 172))   # BEA line rule (pipeline)
def pce_in(agg, ln):
    return True if agg == 'headline' else ln not in PCE_NONCORE

# Oct 2026 estimated atom levels from the 04_oct_pce_build line file (pi = Oct m/m %, SA)
def oct_atom_levels():
    rows = list(csv.DictReader(open(F_DLINES)))
    pi = {int(r['line']): float(r['pi']) for r in rows}
    summ = {r['measure']: r for r in csv.DictReader(open(F_DSUM))}
    core_mm = float(summ['core']['estimate_mm'])
    src = {}
    lv = {}
    for a in ATOMS:
        if a in pi: p, how = pi[a], f'D_build line {a}'
        elif a == 156: p, how = pi[157], 'D_build line 157 (BEA prices 156 on 157)'
        elif a in (10, 11): p, how = pi[9], 'D_build line 9 (parent)'
        elif a == 272: p, how = pi[273], 'D_build line 273 (273 and 274 carry the same pi)'
        elif a in (146, 149, 334, 338): p, how = core_mm, 'net foreign travel / expenditures abroad not estimated in D_build (weights rescaled there): set to core estimate m/m'
        else: raise KeyError(f'no Oct estimate for atom {a}')
        lv[a] = PCE_IDX[a]['2026M09'] * (1 + p / 100); src[a] = how
    agg = {HEADLINE_LINE: float(summ['headline']['index_t']), CORE_LINE: float(summ['core']['index_t'])}
    return lv, agg, src, summ

# ---------------------------------------------------------------- CPI
def _norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
def load_cpi_series():
    lv = {}
    for f in CPI_JSON:
        for s in json.load(open(f))['Results']['series']:
            d = lv.setdefault(s['seriesID'], {})
            for x in s['data']:
                if x['period'] == 'M13': continue
                try: v = float(x['value'])
                except ValueError: continue
                d.setdefault(f"{x['year']}{x['period']}", v)   # first file wins (Nov 10 basket pulls)
    return lv
CPI_LV = load_cpi_series()

def cpi_level(sid, p, interp_oct25=False, gapfill=False):
    d = CPI_LV.get(sid, {})
    if p in d: return d[p]
    if p == '2025M10':
        if interp_oct25 and '2025M09' in d and '2025M11' in d:
            return math.sqrt(d['2025M09'] * d['2025M11'])      # interpolated base (project convention)
        return None
    if gapfill:   # log-linear interpolation of an item's own index across a publication gap of <=3 months each side
        for lo in range(1, 4):
            a = padd(p, -lo)
            if a in d: break
        else: return None
        for hi in range(1, 4):
            b = padd(p, hi)
            if b in d: break
        else: return None
        return d[a] * (d[b] / d[a]) ** (lo / (lo + hi))
    return None

# Codes for RI leaves whose names do not match cu.item exactly
MANUAL_CODES = {'Housing at school, excluding board': 'SEHB01',
                'Technical and business school tuition and fees': 'SEEB04'}
# Household operations: BLS publishes only moving/storage (SEHP03) recently; the parent SEHP and the other
# items are not in our pulls for 2025-26. Moving fell ~7% y/y, a poor proxy for domestic/lawn/repair services,
# so these take core CPI (SA0L1E) as the stated proxy.
PROXY = {'Domestic services': 'SA0L1E', 'Gardening and lawncare services': 'SA0L1E', 'Repair of household items': 'SA0L1E',
         'Unsampled household operations': 'SA0L1E'}
ENERGY_LEAVES = {'Fuel oil', 'Propane, kerosene, and firewood', 'Electricity', 'Utility (piped) gas service',
                 'Gasoline (all types)', 'Other motor fuels'}

def load_ri_tree():
    items = {}
    for r in csv.DictReader(open(F_CUITEM), delimiter='\t'):
        items.setdefault(_norm(r['item_name'].strip()), []).append((r['item_code'].strip(), int(r['display_level'])))
    trees = {}
    for reg, f in F_RI.items():
        ws = openpyxl.load_workbook(f, read_only=True)['Table 1']
        rows = []
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if row[1] == 'Special aggregate indexes': break
            if i >= 9 and row[1] and isinstance(row[0], int):
                rows.append((row[0], row[1].strip(), float(row[2] or 0)))
        trees[reg] = rows
    # structures are identical in both years (checked: 294 rows, 204 leaves); build nodes from 'new'
    nodes = []
    stack = []
    for j, (ind, nm, v) in enumerate(trees['new']):
        oind, onm, ov = trees['old'][j]
        assert (oind, onm) == (ind, nm), (j, nm, onm)
        while stack and stack[-1][0] >= ind: stack.pop()
        parent = stack[-1][1] if stack else None
        nxt = trees['new'][j + 1][0] if j + 1 < len(trees['new']) else -1
        leaf = nxt <= ind
        code = MANUAL_CODES.get(nm)
        if code is None:
            c = items.get(_norm(nm), [])
            code = c[0][0] if c else None
        nodes.append(dict(idx=j, ind=ind, name=nm, ri_new=v, ri_old=ov, parent=parent, leaf=leaf, code=code))
        stack.append((ind, j))
    # food/energy flags
    for n in nodes:
        anc = []; p = n['parent']
        while p is not None: anc.append(nodes[p]['name']); p = nodes[p]['parent']
        n['anc'] = anc
        # RI Table 1 indents 'Alcoholic beverages' (3) under 'Food' (2); in the CPI it is a sibling of Food, inside core
        n['food'] = (('Food' in anc) or n['name'] == 'Food') and not ('Alcoholic beverages' in anc or n['name'] == 'Alcoholic beverages')
        n['energy'] = n['name'] in ENERGY_LEAVES
    return nodes
CPI_NODES = load_ri_tree()
CPI_LEAVES = [n for n in CPI_NODES if n['leaf']]
def cpi_in(agg, n):
    return True if agg == 'headline' else not (n['food'] or n['energy'])

def _rel_series(code, a, b, sa, interp, gapfill):
    if not code: return None
    sids = (['CUSR0000' + code] if sa else []) + ['CUUR0000' + code]
    for sid in sids:
        la, lb = cpi_level(sid, a, interp, gapfill), cpi_level(sid, b, interp, gapfill)
        if la and lb: return lb / la, sid + (' (gap-filled)' if gapfill else '')
    return None

def cpi_leaf_rels(a, b, sa, interp, reg):
    """Price relative b/a for every leaf. Order: (1) own published index; (2) own index, log-linear across a
    publication gap of <=3 months; (proxy) explicit PROXY list; (3) nearest ancestor with its own published index,
    indent >= 2 only (BLS imputes unsampled items from the parent); (4) RI-weighted mean of the nearest ancestor's
    descendants that have their own data."""
    rel, how = {}, {}
    for n in CPI_LEAVES:
        r = _rel_series(n['code'], a, b, sa, interp, False) or _rel_series(n['code'], a, b, sa, interp, True)
        if r: rel[n['idx']] = r[0]; how[n['idx']] = r[1]
    direct = dict(rel)
    for n in CPI_LEAVES:      # explicit proxies (assumption, see notes_B.md)
        if n['idx'] not in rel and n['name'] in PROXY:
            r = _rel_series(PROXY[n['name']], a, b, sa, interp, False)
            if r: rel[n['idx']] = r[0]; how[n['idx']] = f'imputed: proxy {r[1]} (assumption)'
    def node_mean(j):
        num = den = 0.0
        for m in CPI_LEAVES:
            if m['idx'] in direct and (m['parent'] == j or _cpi_desc(m, j)):
                w = m['ri_' + reg]; num += w * direct[m['idx']]; den += w
        return num / den if den else None
    for n in CPI_LEAVES:
        if n['idx'] in rel: continue
        p = n['parent']
        while p is not None:      # (3) nearest ancestor with its own published index (indent >= 2: not 'All items' or a major group)
            node = CPI_NODES[p]
            r = (_rel_series(node['code'], a, b, sa, interp, False) or _rel_series(node['code'], a, b, sa, interp, True)) if node['ind'] >= 2 else None
            if r: rel[n['idx']] = r[0]; how[n['idx']] = f"imputed: ancestor index {r[1]} ('{node['name']}')"; break
            p = node['parent']
        if n['idx'] in rel: continue
        p = n['parent']
        while p is not None:      # (4) RI-weighted mean of the nearest ancestor's descendants that have their own data
            v = node_mean(p)
            if v: rel[n['idx']] = v; how[n['idx']] = f"imputed: mean of sampled descendants of '{CPI_NODES[p]['name']}'"; break
            p = CPI_NODES[p]['parent']
    return rel, how
def _cpi_desc(m, j):
    p = m['parent']
    while p is not None:
        if p == j: return True
        p = CPI_NODES[p]['parent']
    return False

def cpi_weights(a, reg, agg, interp):
    """RI shares at month a under weight regime reg, normalised within agg (BLS: RI_Dec x NSA relative)."""
    dec = '2024M12' if reg == 'old' else '2025M12'
    rel = cpi_leaf_rels(dec, a, False, interp, reg)[0] if a != dec else {n['idx']: 1.0 for n in CPI_LEAVES}
    w = {n['idx']: n['ri_' + reg] * rel[n['idx']] for n in CPI_LEAVES if cpi_in(agg, n)}
    t = sum(w.values())
    return {k: v / t for k, v in w.items()}

def cpi_window(a, b, agg, sa, interp=False):
    """Two-segment (weight-update-aware) Laspeyres contributions of CPI leaves for a->b."""
    if pkey(a) < pkey(LINK) < pkey(b): segs = [(a, LINK, 'old'), (LINK, b, 'new')]
    elif pkey(b) <= pkey(LINK): segs = [(a, b, 'old')]
    else: segs = [(a, b, 'new')]
    contrib = {n['idx']: 0.0 for n in CPI_LEAVES if cpi_in(agg, n)}
    tot_rel = {k: 1.0 for k in contrib}
    L = 1.0; base_w = None; hows = {}
    for (s0, s1, reg) in segs:
        w = cpi_weights(s0, reg, agg, interp)
        rel, how = cpi_leaf_rels(s0, s1, sa, interp, reg)
        if base_w is None: base_w = w
        for k in contrib:
            contrib[k] += L * w[k] * (rel[k] - 1); tot_rel[k] *= rel[k]
            hows.setdefault(k, set()).add(how[k] if k in how else 'missing')
        L *= sum(w[k] * rel[k] for k in contrib)
    return dict(contrib=contrib, R=base_w, pi={k: tot_rel[k] - 1 for k in contrib}, agg=L - 1, segs=segs, how=hows)

def cpi_published(agg, a, b, sa, interp=False):
    sid = ('CUSR0000' if sa else 'CUUR0000') + ('SA0' if agg == 'headline' else 'SA0L1E')
    return cpi_level(sid, b, interp) / cpi_level(sid, a, interp) - 1, sid
