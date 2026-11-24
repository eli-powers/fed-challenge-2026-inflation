"""E: what drove PPI stage 1 intermediate demand in Oct 2026, with its energy contribution negative? (Eli, Nov 15 follow-up)

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/E_stage1_decomp.py" [--fetch]
Layer 1 (SA, saved data): contributions of the 21 leaf sub-groups of WPSID51 (3 producer types x foods / energy /
  goods ex food & energy / services less TTW / transport & warehousing of goods / passenger transport / trade /
  construction) to stage 1's Oct m/m and Aug->Oct (3m) change.
Layer 2 (NSA, BLS API, --fetch saves raw): the largest commodities inside stage 1 "goods excluding foods and energy"
  (ID51113 + ID51213 + ID51313, ~45% of stage 1), with contributions and a CLASSIFICATION BY COMMODITY GROUP:
  energy-intensive manufacturing (chemicals 06, rubber/plastics 07, paper 09, metals 10, nonmetallic minerals 13 —
  the standard energy-intensive set, e.g. EIA MECS), AI-linked electronics (1178*, 117*), other. This is a heuristic,
  not the I-O energy shares used for the shock tags.
Weights: BLS relative importance Dec 2025 (stage 1 = 100), updated for relative price change to the base month of each
  window: w_i = RI_i x I_i(base)/I_i(Dec 2025). Contribution (pp of stage 1) = w_i/sum(w) x % change_i (sum over all
  leaves in layer 1; layer-2 contributions use the same stage-1 denominator, so they are pp of stage 1 too).
Outputs: outputs/E_stage1_groups.csv, outputs/E_stage1_core_goods_commodities.csv, outputs/E_stage1_summary.csv
"""
import glob
import json
import os
import sys
import urllib.request

import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
STG = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_stages_2026-11-15')
RI = os.path.join(STG, 'bls_ppi_id_production_flow_relative_importance_2026_2026-11-15.xlsx')
RAW2 = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_stage1_commodities_2026-11-15')

# ---------------------------------------------------------------- relative importance (stage 1 block)
rows = [[x for x in r] for r in openpyxl.load_workbook(RI, read_only=True)['idpgrouprel26'].iter_rows(values_only=True)]
groups, comm = {}, {}
cur = None
for r in rows:
    v = [x for x in r if x not in (None, '')]
    if not v:
        continue
    k = str(v[0]).strip()
    if k.startswith('ID5'):
        cur = k
        if k.startswith('ID51') and k != 'ID51':
            groups[k] = (v[1], v[3] if len(v) > 3 and v[3] != '-' else 0.0)
        continue
    if cur in ('ID51113', 'ID51213', 'ID51313') and len(r) >= 6 and r[2] not in (None, ''):
        # commodity rows: col C = code, D = name, F = RI Dec 2025. Col A sometimes holds a stray "#REF!" in the BLS file; ignore it.
        ri = r[5]
        if isinstance(ri, (int, float)):
            comm.setdefault(str(r[2]).strip(), [r[3], 0.0])[1] += ri
# the file ends with a summary hierarchy (ID51, ID511, ...); keep only leaf codes (no listed code extends them)
leaf = {k: v for k, v in groups.items() if v[1] and not any(o != k and o.startswith(k) for o in groups)}
assert abs(sum(w for _, w in leaf.values()) - 100) < 0.5, sum(w for _, w in leaf.values())

# ---------------------------------------------------------------- layer 1: SA leaf sub-groups (saved API files)
idx = {}
for f in glob.glob(os.path.join(STG, 'bls_api_ppi_stages_*.json')):
    for s in json.load(open(f))['Results']['series']:
        for o in s['data']:
            if o['period'] != 'M13':
                idx[(s['seriesID'], f"{o['year']}-{o['period'][1:]}")] = float(o['value'])


def sid(code):
    return 'WPS' + code


def contrib(series_idx, keys, wts, base, end, dec='2025-12'):
    w = {k: wts[k] * series_idx[(k, base)] / series_idx[(k, dec)] for k in keys}
    tot = sum(w.values())
    return {k: (w[k] / tot, 100 * (series_idx[(k, end)] / series_idx[(k, base)] - 1)) for k in keys}, tot


keys = [sid(k) for k in leaf if (sid(k), '2026-10') in idx]
missing = [k for k in leaf if (sid(k), '2026-10') not in idx]
wts = {sid(k): leaf[k][1] for k in leaf}
out = []
for lab, base, end in (('Oct m/m', '2026-09', '2026-10'), ('Aug-Oct 3m (not annualized)', '2026-07', '2026-10')):
    c, _ = contrib(idx, keys, wts, base, end)
    pub = 100 * (idx[('WPSID51', end)] / idx[('WPSID51', base)] - 1)
    for k, (sh, ch) in c.items():
        nm = leaf[k[3:]][0]
        typ = ('energy' if 'energy' in nm and 'excluding' not in nm else 'foods' if nm.endswith('foods') else
               'goods ex food & energy' if 'excluding foods and energy' in nm else
               'transport & warehousing of goods' if 'warehousing of goods' in nm else 'passenger transport' if 'passengers' in nm else
               'trade services' if 'trade services' in nm else 'services less trade/TTW' if 'less trade' in nm else 'other')
        out.append(dict(window=lab, series=k, name=nm, type=typ, weight_share=round(sh, 4), pct_change=round(ch, 3), contribution_pp=round(sh * ch, 4),
                        stage1_published_change=round(pub, 3)))
g = pd.DataFrame(out)
g.to_csv(os.path.join(OUT, 'E_stage1_groups.csv'), index=False)
summ = g.groupby(['window', 'type']).agg(weight_share=('weight_share', 'sum'), contribution_pp=('contribution_pp', 'sum')).reset_index()
tot = g.groupby('window').agg(sum_contrib=('contribution_pp', 'sum'), published=('stage1_published_change', 'first')).reset_index()
print('missing leaf series (weight excluded, shares renormalised):', missing)
print(summ.round(3).to_string(index=False))
print(tot.round(3).to_string(index=False))

# ---------------------------------------------------------------- layer 2: commodities inside stage 1 core goods (NSA)
top = sorted(comm.items(), key=lambda kv: -kv[1][1])[:40]
codes = ['WPU' + k for k, _ in top]
if '--fetch' in sys.argv:
    env = dict(l.strip().replace('export ', '').split('=', 1) for l in open(os.path.expanduser('.env')) if '=' in l)
    os.makedirs(RAW2, exist_ok=True)
    for i in range(0, len(codes), 25):
        body = json.dumps({'seriesid': codes[i:i + 25], 'startyear': '2025', 'endyear': '2026', 'registrationkey': env['BLS_API_KEY'].strip('"\'')}).encode()
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=body,
                                     headers={'Content-Type': 'application/json', 'User-Agent': 'research-script'})
        with urllib.request.urlopen(req, timeout=60) as r:
            open(os.path.join(RAW2, f'bls_api_stage1_core_goods_commodities_batch{i // 25 + 1}_2026-11-15.json'), 'wb').write(r.read())
cidx = {}
for f in glob.glob(os.path.join(RAW2, '*.json')):
    for s in json.load(open(f))['Results']['series']:
        for o in s['data']:
            if o['period'] != 'M13' and o['value'] not in ('-', ''):
                cidx[(s['seriesID'], f"{o['year']}-{o['period'][1:]}")] = float(o['value'])


def cls(code):
    c = code[3:]
    if c.startswith(('1178', '117', '115', '116')):
        return 'AI-linked electronics/computers'
    if c.startswith(('06', '07', '09', '10', '13')):
        return 'energy-intensive manufacturing'
    if c.startswith('05'):
        return 'fuels (should be in energy)'
    return 'other'


# stage-1 denominator for pp: same updated-weight total as layer 1 (all stage 1 leaves)
crow = []
for lab, base, end in (('Oct m/m', '2026-09', '2026-10'), ('Aug-Oct 3m (not annualized)', '2026-07', '2026-10')):
    _, tot_w = contrib(idx, keys, wts, base, end)
    for code, (nm, ri) in [('WPU' + k, v) for k, v in top]:
        if not all((code, m) in cidx for m in ('2025-12', base, end)):
            crow.append(dict(window=lab, series=code, name=nm, ri_dec2025_pct_of_stage1=ri, class_heuristic=cls(code), note='missing data'))
            continue
        w = ri * cidx[(code, base)] / cidx[(code, '2025-12')]
        ch = 100 * (cidx[(code, end)] / cidx[(code, base)] - 1)
        crow.append(dict(window=lab, series=code, name=nm, ri_dec2025_pct_of_stage1=ri, class_heuristic=cls(code), pct_change_nsa=round(ch, 3),
                         contribution_pp_of_stage1=round(w / tot_w * ch, 4), note=''))
c = pd.DataFrame(crow)
c.to_csv(os.path.join(OUT, 'E_stage1_core_goods_commodities.csv'), index=False)
cs = c.groupby(['window', 'class_heuristic']).agg(n=('series', 'count'), ri=('ri_dec2025_pct_of_stage1', 'sum'),
                                                   contribution_pp=('contribution_pp_of_stage1', 'sum')).reset_index()
print(cs.round(3).to_string(index=False))
pd.concat([summ.assign(layer='1 groups (SA)'), cs.rename(columns={'class_heuristic': 'type', 'ri': 'weight_share'}).assign(layer='2 core-goods commodities (NSA, top 40)')]).to_csv(
    os.path.join(OUT, 'E_stage1_summary.csv'), index=False)
print('top-40 coverage of stage 1 core goods RI:', round(sum(v[1] for _, v in top), 2), 'of', round(sum(v[1] for v in comm.values()), 2))
