"""Subtask 18 (Method A): producer-price inflation by shock group, tagged PPI stage commodities.

Run from anywhere:  python3 -I "02_Research/Subtasks/18_upstream_ppi_tagged/code/ppi_tagged_excess.py" [--fetch]
  --fetch  re-downloads BLS commodity indexes (fetch_prices.py) into 03_Data/Raw/BLS_PPI_stage_commodities_2026-11-17/.
  Without it, reads saved raw only.

RULES (fixed by Eli, GO.md, Nov 17 2026)
1 Aggregates: stage 4 intermediate demand (WPUID54) = central; stage 1 (WPUID51) = sensitivity. Units = commodity
  codes BLS lists under each stage in the Dec 2025 RI file (units.py); goods AND services lines are units.
  Finest level with a weight and a priced index: the unit's own WPU index; months it is unpublished are filled with
  its parent group's movement (4-char, then 3-char parent), chain-linked at the nearest common month. Units with no
  price at any level are dropped (weights renormalised) and reported.
2 Weights: w_i = RI_i(Dec 2025) x I_i(t-12)/I_i(Dec 2025) (relative-price update to the start of each 12m window).
  Check: weighted 12m change of units vs published WPUID54/WPUID51 12m change, target |gap| <= 0.3 pp (Mar 2025,
  Oct 2026). Sensitivity "w_dec2024": RI Dec 2024 (same file, col E), its own unit universe, updated with I(Dec 2024);
  goods units present only in Dec 2024 have no S2 NAICS mapping -> other (weight logged). Each year's own Dec
  weights: NOT DONE (earlier BLS RI files returned HTTP 403 to scripted fetch; logged).
3 Prices: BLS commodity indexes WPU..., NSA, 12-month % change.
4 Tags (exclusive; priority AI > energy > tariff > other):
  energy  = BLS energy: commodity group 05 (identical to the units in each stage's energy blocks; checked in code).
  AI      = central: electronic components incl. semiconductors, computers & peripherals, communications equipment,
            software publishing (outputs/ai_match.csv, ai_list=central).
            buildout sensitivity: + commodity matches for data processing/hosting, switchgear, turbines & power
            transmission equipment, utility/power engineering (ai_list=buildout).
  tariff  = goods commodity (codes 01-15, not energy/AI) with imports >= 15% of total U.S. supply, BEA 2017 detail
            use table (bea_imports.py); commodity -> NAICS (outputs/goods_naics_map.csv) -> BEA; fallback broader
            NAICS; unmatched -> other, weight reported. Scrap/recyclables (no NAICS industry) are unmatched -> other;
            sensitivity "scrap_bea" tags them with BEA's Scrap commodity S00401 (imports 6.7bn / supply 17.5bn = 0.384,
            an I-O artifact: BEA's domestic scrap output covers secondary sales only).
  other   = everything else incl. all services except AI services. Sensitivity "freight_energy": freight
            transportation (codes 301*: rail, truck, water, air freight, postal/courier, pipeline) counted as energy.
  Unpriced weight varies by window (more units lack prices early in the baseline); reported as max over the path.
5 Formula (group level, mirrors 10_slide2_research/code/G_baseline_attribution.py):
  excess_g(t) = s_g(t) x (R_g(t) - B_g); s_g = group weight share at t (start-of-window weights), R_g = weighted
  group 12m rate, B_g = mean of R_g over 2018-01..2019-12. Total = sum of groups.
  Item contribution to group excess (top-10 tables): s_i x (r_i - B_g), sums exactly to the group excess.
6 Months: Mar 2025, Feb 2026, Oct 2026 (Oct 2026 preliminary, footnote P).
"""
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd  # noqa: E402

import bea_imports  # noqa: E402
import units  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'outputs')
RAW = os.path.join(units.ROOT, '03_Data', 'Raw', 'BLS_PPI_stage_commodities_2026-11-17')
MONTHS = ('2025-03', '2026-02', '2026-10')
BASE = [f'{y}-{m:02d}' for y in (2018, 2019) for m in range(1, 13)]
PATH = [f'{y}-{m:02d}' for y in range(2018, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
GROUPS = ['energy', 'tariff', 'AI', 'other']
THRESH = 0.15

if '--fetch' in sys.argv:
    import fetch_prices
    fetch_prices.fetch()
    fetch_prices.fetch_dec2024_extra()
LOG = []


def log(s):
    LOG.append(s)
    print(s)


# ------------------------------------------------------------------ prices
IDX, FOOT = {}, {}
for f in sorted(glob.glob(os.path.join(RAW, '*.json'))):
    for s in json.load(open(f))['Results']['series']:
        d = IDX.setdefault(s['seriesID'], {})
        for o in s['data']:
            if o['period'].startswith('M') and o['period'] != 'M13' and o['value'] not in ('-', ''):
                m = f"{o['year']}-{o['period'][1:]}"
                d[m] = float(o['value'])
                FOOT[(s['seriesID'], m)] = ';'.join(x['code'] for x in o.get('footnotes', []) if x and x.get('code'))
ALLM = [f'{y}-{m:02d}' for y in range(2016, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]


def unit_path(code):
    """own index, gaps filled by parent movement (chain-linked). Returns (dict month->value, source label, filled months)."""
    own = dict(IDX.get('WPU' + code, {}))
    src = 'own'
    for par in (code[:4], code[:3]):
        p = IDX.get('WPU' + par, {})
        if not p or par == code:
            continue
        if not own:
            own, src = dict(p), f'parent WPU{par}'
            continue
        miss = [m for m in ALLM if m not in own and m in p]
        if not miss:
            continue
        common = [m for m in ALLM if m in own and m in p]
        if not common:
            continue
        for m in miss:
            link = min(common, key=lambda c: abs(ALLM.index(c) - ALLM.index(m)))
            own[m] = own[link] * p[m] / p[link]
        src += f'+fill WPU{par}'
    filled = [m for m in ALLM if m in own and ('WPU' + code not in IDX or m not in IDX['WPU' + code])]
    return own, src, filled


# ------------------------------------------------------------------ tags
DRY = '--dry-no-tags' in sys.argv   # development only: runs the engine with no S2 tag files (outputs not valid)
GMAP = {} if DRY else {r['code']: r for r in csv.DictReader(open(os.path.join(OUT, 'goods_naics_map.csv')))}
AI = {}
for r in ([] if DRY else csv.DictReader(open(os.path.join(OUT, 'ai_match.csv')))):
    AI.setdefault(next(v for k, v in r.items() if k.startswith('ai_list')).strip(), set()).add(r['code'].strip())
if DRY:
    OUT = os.path.join(OUT, '_dry')
    os.makedirs(OUT, exist_ok=True)
# Audit R1 corrections applied over S2's map (S2 file left as delivered). Sources in 06_Audits/18_upstream_ppi_tagged/R1_claude.md.
NAICS_FIX = {
    '061401': '325110;324110',          # R1-F01: published children = aromatics (325110/324110) + liquid refinery gases (324110)
    '108905': '336370;332721;332999',   # R1-F01: children incl. automotive job stampings (336370), precision turned (332721)
    '017108': '112310',                 # R1-N03: BLS places breaker stock under chicken eggs
    '102102': '212230', '102114': '212230',   # R1-N03: valid NAICS 2017 code
    '123201': '326199',                 # R1-N03: resilient floor coverings
    '159F31': '316998',                 # R1-N03: purchased-leather residual
}
for c, n in NAICS_FIX.items():
    if c in GMAP:
        GMAP[c] = dict(GMAP[c], naics_2017=n)
# R1-F03: BLS lists three 518210 product lines; the NAICS-based match (GO rule) takes all three, incl. 381102 BPM
AI.setdefault('buildout', set()).add('381102')
IMP = {}
for c, r in GMAP.items():
    ns = [x.strip() for x in str(r['naics_2017']).split(';') if x.strip()]
    IMP[c] = bea_imports.share_for_naics(ns) if ns else (None, [], '', 'no NAICS')


def tag(code, version):
    ai = AI.get('central', set()) | (AI.get('buildout', set()) if version == 'ai_buildout' else set())
    if code in ai:
        return 'AI', 'AI list' + (' (buildout)' if code not in AI.get('central', set()) else ''), None
    if code.startswith('05'):
        return 'energy', 'BLS energy (group 05)', None
    if version == 'freight_energy' and code.startswith('301'):
        return 'energy', 'freight transportation (sensitivity)', None
    if code[:2] <= '15':
        sh, bea, _, note = IMP.get(code, (None, [], '', 'not in map'))
        if bea == ['S00401'] and version != 'scrap_bea':
            return 'other', 'goods, scrap: no NAICS industry -> unmatched (GO fallback); BEA S00401 share would be ' + f'{sh:.3f}', None
        if sh is None:
            return 'other', f'goods, import share unmatched ({note})', None
        if sh >= THRESH:
            return 'tariff', f'goods, import share {sh:.3f} >= 0.15 (BEA {",".join(bea[:4])})', sh
        return 'other', f'goods, import share {sh:.3f} < 0.15', sh
    return 'other', 'services (non-AI)', None


# ------------------------------------------------------------------ engine
def run(stage, version):
    # R1-F02: Dec 2024 sensitivity uses the Dec 2024 column's OWN unit universe
    U = units.stage_units(stage, 4 if version == 'w_dec2024' else 5)
    dec = '2024-12' if version == 'w_dec2024' else '2025-12'
    P, meta = {}, []
    for c, u in U.items():
        ri = u['ri']
        path, src, filled = unit_path(c)
        t, rule, sh = tag(c, version)
        P[c] = path
        meta.append(dict(code=c, series='WPU' + c, name=u['name'], ri=ri, tag=t, rule=rule, import_share=sh,
                         naics_2017=GMAP.get(c, {}).get('naics_2017', ''), bea_match=';'.join(IMP.get(c, (None, []))[1]),
                         price_source=src if path else 'UNPRICED', n_filled_months=len(filled),
                         priced=bool(path) and dec in path))
    M = pd.DataFrame(meta).set_index('code')
    rows, items = [], []
    for t in sorted(set(PATH) | set(MONTHS)):
        y, m = map(int, t.split('-'))
        b = f'{y - 1}-{m:02d}'
        ok = [c for c in M.index if M.at[c, 'ri'] > 0 and all(k in P[c] for k in (t, b, dec))]
        w = pd.Series({c: M.at[c, 'ri'] * P[c][b] / P[c][dec] for c in ok})
        r = pd.Series({c: 100 * (P[c][t] / P[c][b] - 1) for c in ok})
        tw = w.sum()
        miss_w = M.ri[M.ri > 0].sum() - M.loc[ok, 'ri'].sum()
        for g in GROUPS:
            gi = [c for c in ok if M.at[c, 'tag'] == g]
            sg = w[gi].sum() / tw if gi else 0.0
            Rg = (w[gi] * r[gi]).sum() / w[gi].sum() if gi else 0.0
            rows.append(dict(month=t, group=g, s=sg, R=Rg, n=len(gi)))
        rows.append(dict(month=t, group='_total', s=1.0, R=(w * r).sum() / tw, n=len(ok), unpriced_ri=miss_w))
        if t in MONTHS:
            items.append(pd.DataFrame(dict(month=t, code=ok, s_i=(w / tw).values, r_i=r.values)))
    D = pd.DataFrame(rows)
    B = D[D.month.isin(BASE)].groupby('group').R.mean()
    D['B'] = D.group.map(B)
    D['excess'] = D.s * (D.R - D.B)
    D.loc[D.group == '_total', 'excess'] = D[D.group != '_total'].groupby('month').excess.sum().reindex(D.loc[D.group == '_total', 'month']).values
    pub = IDX['WPUID' + stage]
    D['published_12m'] = D.month.map(lambda t: 100 * (pub[t] / pub[f'{int(t[:4]) - 1}{t[4:]}'] - 1))
    I = pd.concat(items)
    I['tag'] = I.code.map(M.tag)
    I['name'] = I.code.map(M.name)
    I['B_g'] = I.tag.map(B)
    I['contrib_to_group_excess'] = I.s_i * (I.r_i - I.B_g)
    return D, M, I



VERSIONS = ['central', 'w_dec2024', 'ai_buildout', 'freight_energy', 'scrap_bea']
summ, paths, tags_out, top_out, groups_out = [], [], [], [], []
for st in ('54', '51'):
    for v in VERSIONS:
        D, M, I = run(st, v)
        lab = f'stage{st[1]}'
        D.insert(0, 'version', v)
        D.insert(0, 'stage', lab)
        paths.append(D)
        if v == 'central':
            tags_out.append(M.reset_index().assign(stage=lab))
        if v == 'w_dec2024':
            un = M[M.rule.str.contains('not in map')]
            log(f'{lab} w_dec2024: units {len(M)}, RI {M.ri.sum():.3f}; goods absent from the S2 map (tagged other) {len(un)} units, '
                f'RI {un.ri.sum():.3f}; unpriced at Dec 2024 {int((~M.priced).sum())} units, RI {M[~M.priced].ri.sum():.3f}')
        for t in MONTHS:
            d = D[D.month == t].set_index('group')
            tot = d.loc['_total']
            summ.append(dict(stage=lab, version=v, month=t, **{f'excess_{g}': d.at[g, 'excess'] for g in GROUPS},
                             excess_total=tot.excess, units_12m=tot.R, published_12m=tot.published_12m,
                             repro_gap_pp=tot.R - tot.published_12m, unpriced_ri=tot.unpriced_ri))
            for g in GROUPS:
                groups_out.append(dict(stage=lab, version=v, month=t, group=g, weight_share=d.at[g, 's'],
                                       rate_12m=d.at[g, 'R'], baseline_2018_19=d.at[g, 'B'], excess_pp=d.at[g, 'excess'], n_units=d.at[g, 'n']))
        T = I[I.month == '2026-10']
        for g in GROUPS:
            tg = T[T.tag == g].sort_values('contrib_to_group_excess', key=abs, ascending=False).head(10)
            top_out.append(tg.assign(stage=lab, version=v, group=g))

S = pd.DataFrame(summ)
pd.concat(paths).to_csv(os.path.join(OUT, 'group_monthly_all_versions.csv'), index=False)
S.to_csv(os.path.join(OUT, 'summary_excess.csv'), index=False)
pd.DataFrame(groups_out).to_csv(os.path.join(OUT, 'group_table.csv'), index=False)
pd.concat(top_out).to_csv(os.path.join(OUT, 'top10_oct2026.csv'), index=False)
TG = pd.concat(tags_out)
TG.to_csv(os.path.join(OUT, 'tag_table.csv'), index=False)

# ------------------------------------------------------------------ diagnostics
for st in ('stage4', 'stage1'):
    t = TG[TG.stage == st]
    ri = t.ri.sum()
    unm = t[t.rule.str.contains('unmatched')].ri.sum()
    unp = t[~t.priced].ri.sum()
    log(f'{st}: units {len(t)}, RI sum {ri:.3f}; unpriced RI {unp:.3f}; goods with unmatched import share RI {unm:.3f} '
        f'({100 * unm / ri:.2f}%); own-index units {int((t.price_source == "own").sum())}, parent-based/filled '
        f'{int((t.price_source != "own").sum())} (RI {t[t.price_source != "own"].ri.sum():.3f})')
    sc = t[t.rule.str.contains('scrap')]
    log(f'{st}: scrap units (other by fallback) {len(sc)}, RI {sc.ri.sum():.3f}')
    log(f'{st}: Dec 2025 RI by tag ' + ', '.join(f'{g} {t[t.tag == g].ri.sum():.2f}' for g in GROUPS))
PA = pd.concat(paths)
for st in ('stage4', 'stage1'):
    x = PA[(PA.stage == st) & (PA.version == 'central') & (PA.group == '_total')]
    log(f'{st} central: max unpriced RI over Jan 2018-Oct 2026 {x.unpriced_ri.max():.3f} ({x.loc[x.unpriced_ri.idxmax(), "month"]}); '
        f'in Mar 2025/Feb 2026/Oct 2026: {", ".join(f"{v:.3f}" for v in x[x.month.isin(MONTHS)].unpriced_ri)}')
pre = {(s, m): FOOT.get(('WPUID' + s, m), '') for s in ('54', '51') for m in MONTHS}
log(f'published aggregate footnotes (P = preliminary): {pre}')
for st in ('54', '51'):
    U = units.stage_units(st)
    eb = {c for c, u in U.items() if any(len(b) == 7 and b.endswith('12') for b in u['blocks'])}
    g5 = {c for c in U if c.startswith('05')}
    log(f'energy check stage{st[1]}: energy-block units {len(eb)}, group-05 units {len(g5)}, identical: {eb == g5}')
open(os.path.join(OUT, 'run_log.txt'), 'w').write('\n'.join(LOG) + '\n')
pd.set_option('display.width', 220)
print(S.round(3).to_string(index=False))
