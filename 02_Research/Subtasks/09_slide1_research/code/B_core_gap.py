"""B_core_gap.py: core (and headline) CPI-PCE gap reconciliation, Sep 2026 and Oct 2026, plus a headline
cross-check against BEA Table 9.1U.

Run from the project root:
    python3 -I "02_Research/Subtasks/09_slide1_research/code/B_core_gap.py"
Writes (02_Research/Subtasks/09_slide1_research/outputs/):
    B_core_gap_sep.csv, B_core_gap_oct.csv, B_headline_check.csv, B_mapping_groups.csv, B_group_detail_<run>.csv
Reads only saved local files (see B_common.py); nothing is downloaded; nothing under 03_Data is modified.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import B_common as C
from B_mapping import GROUPS, PCE_ONLY, CPI_ONLY

PCE_VINT = 'BEA U20404/U20405 vintage Oct 29 2026 (retrieved Nov 10 2026)'
CPI_VINT = 'BLS CPI-U item indexes retrieved Nov 10 2026 (Oct 2026 CPI release) + Nov 13 2026 component pull; RI Dec 2024 and Dec 2025'

# ---------------------------------------------------------------- assign items to groups
def build_assignment():
    pce_g, cpi_g = {}, {}
    for gid, label, kind, lines, cpis, note in GROUPS:
        for ln in lines: pce_g[ln] = gid
        for c in cpis:
            if c == '__FOOD_AT_HOME__':
                for n in C.CPI_LEAVES:
                    if 'Food at home' in n['anc']: cpi_g[n['idx']] = gid
                continue
            hit = [n for n in C.CPI_LEAVES if n['code'] == c or n['name'] == c]
            assert len(hit) == 1, (gid, c, len(hit))
            cpi_g[hit[0]['idx']] = gid
    for ln in PCE_ONLY: pce_g[ln] = 'PONLY:' + PCE_ONLY[ln][0]
    for c, (lab, note) in CPI_ONLY.items():
        hit = [n for n in C.CPI_LEAVES if n['code'] == c or n['name'] == c]
        assert len(hit) == 1, c
        cpi_g[hit[0]['idx']] = 'CONLY:' + lab
    miss_p = [a for a in C.ATOMS if a not in pce_g]
    miss_c = [n['name'] for n in C.CPI_LEAVES if n['idx'] not in cpi_g]
    assert not miss_p, f'PCE atoms unassigned: {miss_p}'
    assert not miss_c, f'CPI leaves unassigned: {miss_c}'
    extra = [ln for ln in pce_g if ln not in C.ATOMS]
    assert not extra, f'mapped lines that are not atoms: {extra}'
    return pce_g, cpi_g
PCE_G, CPI_G = build_assignment()
KIND = {g[0]: g[2] for g in GROUPS}
LABEL = {g[0]: g[1] for g in GROUPS}

# ---------------------------------------------------------------- one decomposition
def pce_side(agg, a, b, levels_b=None, agg_b=None):
    atoms = [x for x in C.ATOMS if C.pce_in(agg, x)]
    nom = {x: (-1 if x in C.NEG_LINES else 1) * C.PCE_NOM[x][a] for x in atoms}
    tot = sum(nom.values())
    pub_line = C.HEADLINE_LINE if agg == 'headline' else C.CORE_LINE
    closure = tot / C.PCE_NOM[pub_line][a] - 1
    def lv(x, p):
        if p == b and levels_b is not None: return levels_b[x]
        return C.PCE_IDX[x][p]
    s = {x: nom[x] / tot for x in atoms}
    pi = {x: lv(x, b) / lv(x, a) - 1 for x in atoms}
    L = sum(s[x] * pi[x] for x in atoms)
    pb = agg_b[pub_line] if (agg_b is not None) else C.PCE_IDX[pub_line][b]
    pub = pb / C.PCE_IDX[pub_line][a] - 1
    return dict(s=s, pi=pi, L=L, pub=pub, closure=closure)

def decompose(agg, a, b, sa, interp=False, levels_b=None, agg_b=None, cpi_pub_override=None, split_partial=True):
    P = pce_side(agg, a, b, levels_b, agg_b)
    Cw = C.cpi_window(a, b, agg, sa, interp)
    cpub, cpub_sid = C.cpi_published(agg, a, b, sa, interp)
    if cpi_pub_override is not None: cpub = cpi_pub_override
    # group aggregates
    gp, gc = {}, {}
    for x, sx in P['s'].items():
        g = PCE_G[x]; d = gp.setdefault(g, [0.0, 0.0]); d[0] += sx; d[1] += sx * P['pi'][x]
    for k, Rk in Cw['R'].items():
        g = CPI_G[k]; d = gc.setdefault(g, [0.0, 0.0]); d[0] += Rk; d[1] += Rk * Cw['pi'][k]
    groups = sorted(set(gp) | set(gc))
    matched = [g for g in groups if g in gp and g in gc and not g.startswith(('PONLY', 'CONLY'))]
    ponly = [g for g in groups if g in gp and g not in matched]
    conly = [g for g in groups if g in gc and g not in matched]
    sP = {g: gp[g][0] for g in gp}; pP = {g: gp[g][1] / gp[g][0] if gp[g][0] else 0.0 for g in gp}
    sC = {g: gc[g][0] for g in gc}; pC = {g: gc[g][1] / gc[g][0] if gc[g][0] else 0.0 for g in gc}
    full = [g for g in matched if KIND[g] == 'common']
    k = sum(sP[g] for g in full) / sum(sC[g] for g in full)
    s_in, s_out = {}, {}
    for g in matched:
        if KIND[g] == 'partial' and split_partial:
            s_in[g] = min(sP[g], k * sC[g]); s_out[g] = sP[g] - s_in[g]
        else:
            s_in[g] = sP[g]; s_out[g] = 0.0
    S_C = sum(s_in.values()); R_C = sum(sC[g] for g in matched)
    Pc = sum(s_in[g] * pP[g] for g in matched) / S_C
    Cc = sum(sC[g] * pC[g] for g in matched) / R_C
    rows = []
    def add(effect, item, val, valc, method, src):
        rows.append(dict(effect=effect, item=item, pp=val * 100, pp_centered=valc * 100, method=method, source=src))
    # formula
    fml = P['pub'] - P['L']
    add('formula', 'Chained Fisher vs fixed-weight Laspeyres (all PCE items, not allocated)', fml, fml,
        'published PCE change minus Laspeyres on base-month nominal shares of BEA atoms', PCE_VINT)
    # pp = BEA Table 9.1U convention (raw shares of the full index, item change not centred);
    # pp_centered = alternate attribution relative to the matched-set mean (shares renormalised within the matched set)
    for g in matched:
        st, rt = s_in[g] / S_C, sC[g] / R_C
        add('weight', LABEL[g], (s_in[g] - sC[g]) * pC[g], (st - rt) * (pC[g] - Cc),
            f'BEA convention: (PCE in-scope share {s_in[g]*100:.2f}% - CPI share {sC[g]*100:.2f}%) x CPI group change {pC[g]*100:.2f}%. '
            f'Centred: (renormalised {st*100:.2f}% - {rt*100:.2f}%) x (change - matched CPI mean {Cc*100:.2f}%)'
            + ('. Partial-scope group: in-scope PCE share = k x CPI share' if KIND[g] == 'partial' else ''),
            f'{PCE_VINT}; {CPI_VINT}')
    for g in matched:
        st = s_in[g] / S_C
        add('price', LABEL[g], s_in[g] * (pP[g] - pC[g]), st * (pP[g] - pC[g]),
            f'PCE in-scope share {s_in[g]*100:.2f}% (renormalised {st*100:.2f}%) x (PCE group change {pP[g]*100:.2f}% - CPI group change {pC[g]*100:.2f}%)',
            f'{PCE_VINT}; {CPI_VINT}')
    # scope: PCE-only
    for g in ponly:
        lab = g.split(':', 1)[1] if ':' in g else LABEL.get(g, g)
        tag = ' [core-definition: in core PCE, excluded from core CPI]' if not g.startswith('PONLY') else ''
        add('scope_PCE_only', lab + tag, sP[g] * pP[g], sP[g] * (pP[g] - Pc),
            f'PCE share {sP[g]*100:.2f}% x item change {pP[g]*100:.2f}% (centred: minus matched PCE mean {Pc*100:.2f}%)', PCE_VINT)
    for g in matched:
        if s_out[g] > 0:
            add('scope_PCE_only', LABEL[g] + ' [third-party-paid portion, out of CPI scope]', s_out[g] * pP[g], s_out[g] * (pP[g] - Pc),
                f'out-of-scope PCE share {s_out[g]*100:.2f}% (= PCE share {sP[g]*100:.2f}% - k x CPI share {sC[g]*100:.2f}%; k={k:.3f}) x change {pP[g]*100:.2f}% (centred: minus {Pc*100:.2f}%)',
                PCE_VINT)
    for g in conly:
        lab = g.split(':', 1)[1] if ':' in g else LABEL.get(g, g)
        tag = ' [core-definition: in core CPI, excluded from core PCE]' if not g.startswith('CONLY') else ''
        add('scope_CPI_only', lab + tag, -sC[g] * pC[g], -sC[g] * (pC[g] - Cc),
            f'-(CPI share {sC[g]*100:.2f}% x item change {pC[g]*100:.2f}%) (centred: change minus matched CPI mean {Cc*100:.2f}%)', CPI_VINT)
    # CPI chain link and residual
    L1 = sum(Cw['R'][k2] * Cw['pi'][k2] for k2 in Cw['R'])
    add('other', 'CPI weight update in Jan 2026 (two-segment chain vs single base)', L1 - Cw['agg'], L1 - Cw['agg'],
        'single-base CPI Laspeyres minus two-segment (old weights to Dec 2025, new weights after) aggregate', CPI_VINT)
    add('residual', 'CPI aggregation residual (our leaf aggregate vs published index)', Cw['agg'] - cpub, Cw['agg'] - cpub,
        f'our CPI aggregate {Cw["agg"]*100:.3f}% minus published {cpub*100:.3f}% ({cpub_sid})', CPI_VINT)
    gap = (P['pub'] - cpub) * 100
    for key in ('pp', 'pp_centered'):
        total = sum(r[key] for r in rows)
        assert abs(total - gap) < 1e-9, (key, total, gap)
    meta = dict(pce_pub=P['pub'] * 100, pce_L=P['L'] * 100, cpi_pub=cpub * 100, cpi_ours=Cw['agg'] * 100, cpi_L1=L1 * 100,
                gap=gap, k=k, S_C=S_C, R_C=R_C, Pc=Pc * 100, Cc=Cc * 100, pce_closure=P['closure'] * 100,
                segs=Cw['segs'], cpub_sid=cpub_sid)
    detail = []
    for g in groups:
        detail.append(dict(group=g, label=LABEL.get(g, g.split(':', 1)[-1]), kind=KIND.get(g, 'pce_only' if g in ponly else 'cpi_only'),
                           pce_share=sP.get(g, 0) * 100, pce_share_in_scope=s_in.get(g, 0) * 100, cpi_share=sC.get(g, 0) * 100,
                           pce_change=pP.get(g, float('nan')) * 100 if g in pP else '', cpi_change=pC[g] * 100 if g in pC else ''))
    imputed = sorted({C.CPI_NODES[k2]['name'] for k2, hs in Cw['how'].items() if any(str(h).startswith('imputed') for h in hs)})
    meta['cpi_imputed_leaves'] = imputed
    meta['cpi_imputed_share'] = sum(Cw['R'][k2] for k2, hs in Cw['how'].items() if any(str(h).startswith('imputed') for h in hs)) * 100
    return rows, meta, detail

def summarize(rows, key='pp'):
    out = {}
    for r in rows: out[r['effect']] = out.get(r['effect'], 0) + r[key]
    return out

def write_csv(path, rows, header_rows, basis):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['effect', 'item', 'pp', 'method', 'source', 'pp_centered_alt', 'basis'])
        for hr in header_rows: w.writerow(list(hr) + [hr[2], basis])
        for r in rows: w.writerow([r['effect'], r['item'], f"{r['pp']:.4f}", r['method'], r['source'], f"{r['pp_centered']:.4f}", basis])
        tot = summarize(rows); totc = summarize(rows, 'pp_centered')
        for e, v in tot.items(): w.writerow(['subtotal', e, f'{v:.4f}', 'sum of rows with this effect', '', f'{totc[e]:.4f}', basis])
        w.writerow(['check', 'sum of all effect rows incl. residual', f"{sum(r['pp'] for r in rows):.4f}", 'equals published gap by construction', '', f"{sum(r['pp_centered'] for r in rows):.4f}", basis])

def write_detail(path, detail, meta):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['group', 'label', 'kind', 'pce_share_pct', 'pce_share_in_cpi_scope_pct', 'cpi_share_pct', 'pce_change_pct', 'cpi_change_pct'])
        for d in detail:
            w.writerow([d['group'], d['label'], d['kind'], f"{d['pce_share']:.4f}", f"{d['pce_share_in_scope']:.4f}", f"{d['cpi_share']:.4f}",
                        f"{d['pce_change']:.4f}" if d['pce_change'] != '' else '', f"{d['cpi_change']:.4f}" if d['cpi_change'] != '' else ''])
        for kk in ('pce_pub', 'pce_L', 'cpi_pub', 'cpi_ours', 'cpi_L1', 'gap', 'k', 'S_C', 'R_C', 'Pc', 'Cc', 'pce_closure', 'cpi_imputed_share'):
            w.writerow(['meta', kk, meta[kk]])
        w.writerow(['meta', 'cpi_segments', meta['segs']])
        w.writerow(['meta', 'cpi_imputed_leaves', '; '.join(meta['cpi_imputed_leaves'])])

def published_rows(meta, plabel, clabel):
    return [('published', plabel, f"{meta['pce_pub']:.4f}", 'PCE change, %', PCE_VINT),
            ('published', clabel, f"{meta['cpi_pub']:.4f}", 'CPI change, %', CPI_VINT + f" ({meta['cpub_sid']})"),
            ('published', 'gap = PCE minus CPI', f"{meta['gap']:.4f}", 'pp; the effect rows below sum to this', '')]

# ---------------------------------------------------------------- runs
def main():
    os.makedirs(C.OUT, exist_ok=True)
    # mapping file
    with open(os.path.join(C.OUT, 'B_mapping_groups.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['group', 'label', 'kind', 'pce_lines', 'pce_line_names', 'cpi_items', 'note'])
        for gid, label, kind, lines, cpis, note in GROUPS:
            cl = [n for n in C.CPI_LEAVES if CPI_G.get(n['idx']) == gid]
            w.writerow([gid, label, kind, ' '.join(map(str, lines)), '; '.join(C.HIER[l][0] for l in lines),
                        '; '.join(f"{n['code'] or 'no code'}={n['name']}" for n in cl), note])
        labs = {}
        for ln, (lab, note) in PCE_ONLY.items(): labs.setdefault(lab, []).append(ln)
        for lab, lns in labs.items():
            w.writerow(['PCE-only', lab, 'pce_only', ' '.join(map(str, sorted(lns))), '; '.join(C.HIER[l][0] for l in sorted(lns)), '',
                        next(PCE_ONLY[l][1] for l in sorted(lns) if PCE_ONLY[l][1]) if any(PCE_ONLY[l][1] for l in lns) else ''])
        for c, (lab, note) in CPI_ONLY.items():
            w.writerow(['CPI-only', lab, 'cpi_only', '', '', c, note])
    results = {}
    # 1) Sep 2026 core 12m (NSA CPI, as published y/y)
    rows, meta, det = decompose('core', '2025M09', '2026M09', sa=False)
    basis = 'Sep 2025 -> Sep 2026, 12-month change; PCE SA, CPI NSA (as published y/y)'
    write_csv(os.path.join(C.OUT, 'B_core_gap_sep.csv'), rows,
              published_rows(meta, 'Core PCE (U20404 line 374), 12m %', 'Core CPI-U (CUUR0000SA0L1E), 12m %'), basis)
    write_detail(os.path.join(C.OUT, 'B_group_detail_core_sep12m.csv'), det, meta)
    results['core_sep_12m'] = (rows, meta)
    # sensitivity: SA CPI components
    rows_sa, meta_sa, det_sa = decompose('core', '2025M09', '2026M09', sa=True)
    results['core_sep_12m_SA'] = (rows_sa, meta_sa)
    rows_ns, meta_ns, _ = decompose('core', '2025M09', '2026M09', sa=False, split_partial=False)
    results['core_sep_12m_nosplit'] = (rows_ns, meta_ns)
    with open(os.path.join(C.OUT, 'B_sensitivity_sep.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['run', 'effect', 'pp_bea_convention', 'pp_centered_alt', 'note'])
        for lab, rr, note in (('main', rows, 'CPI NSA; medical third-party portion split out as PCE-only scope'),
                              ('cpi_sa_components', rows_sa, 'CPI SA item indexes, published SA core CPI 12m'),
                              ('no_medical_split', rows_ns, 'medical groups treated as fully in CPI scope (all PCE weight in weight effect)')):
            t1, t2 = summarize(rr), summarize(rr, 'pp_centered')
            for e in t1: w.writerow([lab, e, f'{t1[e]:.4f}', f'{t2[e]:.4f}', note])
            for r in rr:
                if ('shelter' in r['item'].lower() or "Owners'" in r['item'] or 'Rent of primary' in r['item']) and r['effect'] == 'weight':
                    w.writerow([lab, 'weight: ' + r['item'], f"{r['pp']:.4f}", f"{r['pp_centered']:.4f}", note])
    # 2) Oct 2026 core: approx 12m (interpolated Oct 2025 CPI base) and 3m annualized (Jul -> Oct, SA)
    lv_oct, agg_oct, src_oct, summ = C.oct_atom_levels()
    rows_o, meta_o, det_o = decompose('core', '2025M10', '2026M10', sa=False, interp=True, levels_b=lv_oct, agg_b=agg_oct)
    rows_3, meta_3, det_3 = decompose('core', '2026M07', '2026M10', sa=True, levels_b=lv_oct, agg_b=agg_oct)
    # annualize the 3m decomposition: scale every row by f so rows sum to the annualized gap
    pa = ((1 + meta_3['pce_pub'] / 100) ** 4 - 1) * 100; ca = ((1 + meta_3['cpi_pub'] / 100) ** 4 - 1) * 100
    f3 = (pa - ca) / meta_3['gap']
    rows_3a = [dict(r, pp=r['pp'] * f3, pp_centered=r['pp_centered'] * f3, method=r['method'] + f'; raw 3-month pp scaled by f={f3:.4f} so rows sum to the annualized gap') for r in rows_3]
    with open(os.path.join(C.OUT, 'B_core_gap_oct.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['comparison', 'effect', 'item', 'pp', 'method', 'source', 'pp_centered_alt', 'basis'])
        b1 = ('PRIMARY: approx. 12m, Oct 2025 -> Oct 2026. PCE Oct 2026 = our estimate (04_oct_pce_build, first-release variant, band +/-0.05pp on 12m); '
              'CPI NSA with every Oct 2025 level interpolated as sqrt(Sep 2025 x Nov 2025) (BLS published no Oct 2025 CPI)')
        b2 = ('ALTERNATE: 3m annualized, Jul 2026 -> Oct 2026, SA both sides. CPI fully published; PCE Oct = our estimate (band +/-0.20pp on 3m ann.)')
        for lab, rr, mm, bb in (('approx_12m', rows_o, meta_o, b1), ('3m_annualized', rows_3a, dict(meta_3, pce_pub=pa, cpi_pub=ca, gap=pa - ca), b2)):
            for hr in published_rows(mm, 'Core PCE Oct 2026 (estimate)', 'Core CPI-U Oct 2026'):
                w.writerow([lab] + list(hr) + [hr[2], bb])
            for r in rr: w.writerow([lab, r['effect'], r['item'], f"{r['pp']:.4f}", r['method'], r['source'] + '; Oct PCE: 04_oct_pce_build D_build_2026-10', f"{r['pp_centered']:.4f}", bb])
            tc = summarize(rr, 'pp_centered')
            for e, v in summarize(rr).items(): w.writerow([lab, 'subtotal', e, f'{v:.4f}', 'sum of rows with this effect', '', f'{tc[e]:.4f}', bb])
            w.writerow([lab, 'check', 'sum of all effect rows incl. residual', f"{sum(r['pp'] for r in rr):.4f}", 'equals gap', '', f"{sum(r['pp_centered'] for r in rr):.4f}", bb])
    write_detail(os.path.join(C.OUT, 'B_group_detail_core_oct12m_approx.csv'), det_o, meta_o)
    write_detail(os.path.join(C.OUT, 'B_group_detail_core_oct3m.csv'), det_3, meta_3)
    results['core_oct_12m'] = (rows_o, meta_o); results['core_oct_3m_ann'] = (rows_3a, dict(meta_3, pce_pub=pa, cpi_pub=ca, gap=pa - ca, f3=f3))
    # 3) Headline cross-check vs BEA Table 9.1U
    months = [C.padd('2025M12', i) for i in range(10)]          # Dec 2025 .. Sep 2026
    monthly = {}
    for m in months:
        r_m, meta_m, _ = decompose('headline', C.padd(m, -1), m, sa=True)
        monthly[m] = (summarize(r_m), meta_m, r_m)
    rows_h10, meta_h10, det_h10 = decompose('headline', '2025M11', '2026M09', sa=True)
    rows_h12, meta_h12, det_h12 = decompose('headline', '2025M09', '2026M09', sa=False)
    write_detail(os.path.join(C.OUT, 'B_group_detail_headline_sep12m.csv'), det_h12, meta_h12)
    # BEA lines
    bea = {}
    for x in json.load(open(C.F_U90100))['BEAAPI']['Results']['Data']:
        try: bea.setdefault(int(x['LineNumber']), {})[x['TimePeriod']] = float(x['DataValue'])
        except ValueError: pass
    def bsum(ln): return sum(bea[ln][m] for m in months)
    def item_sum(rowsets, effect, keys):
        tot = 0.0
        for rs in rowsets:
            for r in rs:
                if r['effect'] == effect and any(k in r['item'] for k in keys): tot += r['pp']
        return tot
    msets = [monthly[m][2] for m in months]
    ours = {e: sum(monthly[m][0].get(e, 0) for m in months) for e in ('formula', 'weight', 'scope_PCE_only', 'scope_CPI_only', 'price', 'other', 'residual')}
    comp = [
        ('PCE price index, sum of monthly % changes', bsum(1), sum(monthly[m][1]['pce_pub'] for m in months), 'BEA line 1 (rounded to 0.1 each month) vs exact from U20404 line 1'),
        ('CPI, sum of monthly % changes', bsum(39), sum(monthly[m][1]['cpi_pub'] for m in months), 'BEA line 39 (rounded to 0.1) vs exact from CUSR0000SA0'),
        ('Gap PCE minus CPI', bsum(1) - bsum(39), sum(monthly[m][1]['gap'] for m in months), ''),
        ('Gap implied by BEA effect lines (2 + 13 + 21 - 28 + 32)', bsum(2) + bsum(13) + bsum(21) - bsum(28) + bsum(32), sum(monthly[m][1]['gap'] for m in months), 'BEA effect lines are rounded to 0.01 each month, so this is a better BEA gap than lines 1 and 39'),
        ('Formula effect', bsum(2), ours['formula'], 'BEA line 2'),
        ('Weight effect, total', bsum(13), ours['weight'], 'BEA line 13'),
        ('Weight effect: rent of shelter (OER + rent + hotels/lodging)', bsum(14), item_sum(msets, 'weight', ["Owners' equivalent", 'Rent of primary', 'Hotels', 'Housing at school']), 'BEA line 14; ours = OER, rent, hotels, housing at school'),
        ('Weight effect: owner-occupied housing', bsum(15), item_sum(msets, 'weight', ["Owners' equivalent"]), 'BEA line 15'),
        ('Weight effect: tenant rent', bsum(16), item_sum(msets, 'weight', ['Rent of primary']), 'BEA line 16'),
        ('Weight effect: hotels and motels', bsum(17), item_sum(msets, 'weight', ['Hotels']), 'BEA line 17'),
        ('Weight effect: gasoline', bsum(18), item_sum(msets, 'weight', ['Motor fuel']), 'BEA line 18'),
        ('Weight effect: household energy', bsum(19), item_sum(msets, 'weight', ['Electricity', 'Utility gas', 'Fuel oil']), 'BEA line 19'),
        ('Weight effect: other', bsum(20), ours['weight'] - item_sum(msets, 'weight', ["Owners' equivalent", 'Rent of primary', 'Hotels', 'Housing at school', 'Motor fuel', 'Electricity', 'Utility gas', 'Fuel oil']), 'BEA line 20'),
        ('Scope: PCE items out of CPI scope, total', bsum(21), ours['scope_PCE_only'], 'BEA line 21'),
        ('Scope PCE-only: physician services', bsum(22), item_sum(msets, 'scope_PCE_only', ['Physician']), 'BEA line 22; ours = third-party portion'),
        ('Scope PCE-only: hospital and nursing home', bsum(23), item_sum(msets, 'scope_PCE_only', ['Hospital', 'Nursing']), 'BEA line 23; ours = third-party portion'),
        ('Scope PCE-only: financial services furnished without payment', bsum(24), item_sum(msets, 'scope_PCE_only', ['furnished without payment']), 'BEA line 24'),
        ('Scope PCE-only: foreign travel', bsum(25), item_sum(msets, 'scope_PCE_only', ['Net foreign travel']), 'BEA line 25 (foreign travel by U.S. residents); ours = net foreign travel atom'),
        ('Scope PCE-only: NPISH', bsum(26), item_sum(msets, 'scope_PCE_only', ['NPISH']), 'BEA line 26'),
        ('Scope PCE-only: other', bsum(27), ours['scope_PCE_only'] - item_sum(msets, 'scope_PCE_only', ['Physician', 'Hospital', 'Nursing', 'furnished without payment', 'Net foreign travel', 'NPISH']), 'BEA line 27'),
        ('Scope: CPI items out of PCE scope (gap terms = minus BEA line 28)', -bsum(28), ours['scope_CPI_only'], 'BEA line 28 enters the gap with a minus sign'),
        ('Other effects total (BEA: seasonal + price + other)', bsum(32), ours['price'] + ours['other'], 'BEA line 32; ours = price + CPI weight-update'),
        ('Other effects: air transportation price', bsum(36), item_sum(msets, 'price', ['Airline']), 'BEA line 36'),
        ('Residual (ours only: CPI replication error)', 0.0, ours['residual'], 'BEA lines sum to published CPI; ours = our CPI aggregate minus published'),
    ]
    with open(os.path.join(C.OUT, 'B_headline_check.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['block', 'item', 'bea_9_1U_pp', 'ours_pp', 'ours_minus_bea_pp', 'note', 'basis'])
        bb = ('Sum of monthly effects, Dec 2025 - Sep 2026 (10 months; Oct and Nov 2025 monthly CPI changes do not exist). '
              'BEA U90100 LastRevised Oct 29 2026 (retrieved Nov 10 2026), monthly values rounded to 0.01pp. Ours: same months, SA CPI and PCE, previous-month weights.')
        for it, bv, ov, note in comp:
            w.writerow(['monthly_sum_Dec25_Sep26', it, f'{bv:.4f}', f'{ov:.4f}', f'{ov - bv:.4f}', note, bb])
        for m in months:
            sm, mt, _ = monthly[m]
            w.writerow(['by_month_gap', m, f"{bea[1][m] - bea[39][m]:.4f}", f"{mt['gap']:.4f}", f"{mt['gap'] - (bea[1][m] - bea[39][m]):.4f}",
                        f"BEA formula {bea[2][m]:+.2f} weight {bea[13][m]:+.2f} scopeP {bea[21][m]:+.2f} scopeC {-bea[28][m]:+.2f} other {bea[32][m]:+.2f} | ours formula {sm['formula']:+.3f} weight {sm['weight']:+.3f} scopeP {sm['scope_PCE_only']:+.3f} scopeC {sm['scope_CPI_only']:+.3f} price+other {sm['price']+sm['other']:+.3f} resid {sm['residual']:+.3f}",
                        'one month, SA; BEA PCE and CPI lines rounded to 0.1'])
        for lab, rr, mm, bb2 in (('cumulative_Nov25_Sep26', rows_h10, meta_h10, 'Single window Nov 2025 -> Sep 2026 (same 10 months, one base), SA CPI; the method used for core'),
                                 ('headline_12m_Sep26', rows_h12, meta_h12, 'Sep 2025 -> Sep 2026, 12m, CPI NSA (no BEA comparator for 12m)')):
            sm = summarize(rr)
            w.writerow([lab, 'published PCE %', '', f"{mm['pce_pub']:.4f}", '', '', bb2])
            w.writerow([lab, 'published CPI %', '', f"{mm['cpi_pub']:.4f}", '', mm['cpub_sid'], bb2])
            w.writerow([lab, 'gap', '', f"{mm['gap']:.4f}", '', '', bb2])
            for e in ('formula', 'weight', 'scope_PCE_only', 'scope_CPI_only', 'price', 'other', 'residual'):
                w.writerow([lab, e, f'{bsum({"formula":2,"weight":13,"scope_PCE_only":21}[e]) if (lab.startswith("cumul") and e in ("formula","weight","scope_PCE_only")) else (-bsum(28) if (lab.startswith("cumul") and e=="scope_CPI_only") else "")}',
                            f'{sm.get(e, 0):.4f}', '', 'BEA column = monthly sum, for rough comparison only' if lab.startswith('cumul') else '', bb2])
            for r in rr:
                if abs(r['pp']) >= 0.02: w.writerow([lab + '_items', f"{r['effect']}: {r['item']}", '', f"{r['pp']:.4f}", '', r['method'], bb2])
    results['headline_monthly'] = monthly; results['headline_cum'] = (rows_h10, meta_h10); results['headline_12m'] = (rows_h12, meta_h12)
    # theme summary (for spoken-line candidates): combines rows across effects by item theme
    THEMES = [
        ('Shelter (OER, rent, hotels, housing at school)', lambda r: r['effect'] in ('weight', 'price') and any(k in r['item'] for k in ("Owners' equivalent", 'Rent of primary', 'Hotels', 'Housing at school'))),
        ('Health care: third-party-paid medical (PCE-only scope)', lambda r: 'third-party-paid' in r['item']),
        ('Health care: in-scope medical weight and price (incl. Rx, physicians, hospitals)', lambda r: r['effect'] in ('weight', 'price') and any(k in r['item'] for k in ('Prescription', 'Physician', 'Dental', 'Other professional medical', 'Hospital services', 'Nursing homes', 'Individual and family', 'Nonprescription'))),
        ('Health insurance (weight and price)', lambda r: r['effect'] in ('weight', 'price') and r['item'] == 'Health insurance'),
        ('Financial: portfolio mgmt, imputed bank services, commissions, life insurance (PCE-only)', lambda r: r['effect'] == 'scope_PCE_only' and any(k in r['item'] for k in ('Portfolio', 'furnished without payment', 'Securities commissions', 'Life insurance'))),
        ('Software (weight and price)', lambda r: r['effect'] in ('weight', 'price') and 'software' in r['item']),
        ('Motor vehicle insurance (weight and price)', lambda r: r['effect'] in ('weight', 'price') and r['item'] == 'Motor vehicle insurance'),
        ('Airfares (weight and price)', lambda r: r['effect'] in ('weight', 'price') and 'Airline' in r['item']),
        ('Core definition: restaurant meals in core PCE only', lambda r: 'Food away from home' in r['item']),
        ('Core definition: alcohol at home in core CPI only', lambda r: 'Alcohol at home' in r['item']),
        ('NPISH, foreign travel, social services, gambling, other PCE-only', lambda r: r['effect'] == 'scope_PCE_only' and any(k in r['item'] for k in ('NPISH', 'foreign travel', 'expenditures abroad', 'Social services', 'Gambling', 'Employment agency', 'Income-loss', 'farm dwellings'))),
        ('CPI-only items (vehicle fees, lawn care)', lambda r: r['effect'] == 'scope_CPI_only' and 'Alcohol at home' not in r['item']),
        ('Formula (Fisher vs fixed weight)', lambda r: r['effect'] == 'formula'),
        ('CPI Jan-2026 weight update', lambda r: r['effect'] == 'other'),
        ('Residual (CPI replication)', lambda r: r['effect'] == 'residual'),
    ]
    with open(os.path.join(C.OUT, 'B_theme_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['run', 'theme', 'pp_bea_convention', 'pp_centered_alt', 'basis'])
        for lab, rr, bb in (('core_sep_12m', rows, basis), ('core_oct_12m_approx', rows_o, 'Oct 2025 -> Oct 2026 approx. 12m (interpolated CPI base; PCE Oct = estimate)'),
                            ('core_oct_3m_ann', rows_3a, 'Jul -> Oct 2026, 3m annualized, SA')):
            used = set()
            for th, fn in THEMES:
                sel = [i for i, r in enumerate(rr) if fn(r) and i not in used]; used |= set(sel)
                w.writerow([lab, th, f"{sum(rr[i]['pp'] for i in sel):.4f}", f"{sum(rr[i]['pp_centered'] for i in sel):.4f}", bb])
            rest = [i for i in range(len(rr)) if i not in used]
            w.writerow([lab, 'All other matched items (weight and price)', f"{sum(rr[i]['pp'] for i in rest):.4f}", f"{sum(rr[i]['pp_centered'] for i in rest):.4f}", bb])
            w.writerow([lab, 'TOTAL = gap', f"{sum(r['pp'] for r in rr):.4f}", f"{sum(r['pp_centered'] for r in rr):.4f}", bb])
    # console summary
    for key in ('core_sep_12m', 'core_sep_12m_SA', 'core_sep_12m_nosplit', 'core_oct_12m', 'core_oct_3m_ann', 'headline_cum', 'headline_12m'):
        rr, mm = results[key]
        print(f"\n== {key}: PCE {mm['pce_pub']:.3f}  CPI {mm['cpi_pub']:.3f}  gap {mm['gap']:.3f}  | PCE_L {mm['pce_L']:.3f} CPI_ours {mm['cpi_ours']:.3f} k={mm['k']:.3f} PCEclosure {mm['pce_closure']:.4f}% imputedCPI {mm['cpi_imputed_share']:.2f}%")
        for e, v in summarize(rr).items(): print(f'   {e:16s} {v:+.3f}')
        for r in sorted(rr, key=lambda r: -abs(r['pp']))[:14]: print(f"     {r['effect']:15s} {r['pp']:+.3f}  {r['item'][:80]}")
    print('\nOct atom sources not taken directly from D_build lines:', {a: s for a, s in src_oct.items() if not s.startswith('D_build line ' + str(a))})
    print('headline monthly-sum comparison:'); [print(f'   {it[:70]:70s} BEA {bv:+.3f} ours {ov:+.3f}') for it, bv, ov, note in comp]

if __name__ == '__main__':
    main()
