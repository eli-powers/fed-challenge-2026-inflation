"""A Q1.2: independent recomputation of item energy shares from the raw BEA I-O files, compared with 08_shock_tagging/item_exposures_full.csv.

Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/A_q1_energy_spotcheck.py  (project root)

Independent of 08_shock_tagging/code/tag_exposures.py in code and algebra (same inputs and documented design):
  inputs  : BEA 2017 detail commodity-by-commodity total requirements L (CxC_TR, after redefinitions), Make table (commodity output T007),
            PCE bridge 2017 (producers' value, transport, wholesale, retail margins, purchasers' value), all read here with pandas.
  A       = I - L^-1  (direct requirements implied by BEA's published L)
  energy block X = {211000, 212100, 221100, 221200, S00101, S00202, 3241xx}   (as documented in tag_exposures.py)
  exposure e_c for commodity c: energy purchased per $ of c through NON-energy supply chains, counting energy itself as 1.
          Route here: zero the X columns of A (energy industries' own inputs), Leontief inverse L' = (I - A')^-1, e_c = sum_{x in X} L'[x, c]
          (tag_exposures.py instead uses e = 1' A_XN (I - A_NN)^-1; the two are algebraically identical).
  item    : e_item = sum_rows (pv*e[c] + trans*e_T + whole*e_W + retail*e_R) / purchasers' value
          margins: e_T/e_W/e_R = output-weighted mean exposure of transport {482000,483000,484000}, wholesale {42*}, retail {44*,45*,4B0000} excl 447000.
  bridge lines per item taken from item_exposures_full.csv column bridge_lines (the aggregate-line mapping is an input, not re-derived).
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
RAW = os.path.join(ROOT, '03_Data/Raw/BEA_IO_shock_tagging_2026-11-14')
OUT = os.path.join(ROOT, '02_Research/Subtasks/10_slide2_research/outputs')
TAG = os.path.join(ROOT, '02_Research/Subtasks/08_shock_tagging')

tr = pd.read_excel(os.path.join(RAW, 'CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx'), sheet_name='2017', header=None, dtype=object)
codes_col = [str(x).strip() for x in tr.iloc[4, 2:].tolist() if str(x) != 'nan']
body = tr.iloc[5:, :]
body = body[body[0].notna() & ~body[0].astype(str).str.startswith('T')]
rows_codes = [str(x).strip() for x in body[0]]
Lmat = body.iloc[:, 2:2 + len(codes_col)].astype(float).fillna(0.0).values
assert rows_codes == codes_col or set(rows_codes) == set(codes_col)
if rows_codes != codes_col:
    idx = [rows_codes.index(c) for c in codes_col]; Lmat = Lmat[idx, :]
comms = codes_col; ci = {c: i for i, c in enumerate(comms)}; n = len(comms)
print('TR matrix', Lmat.shape)

mk = pd.read_excel(os.path.join(RAW, 'AllTablesIO/IOMake_Before_Redefinitions_2017_Detail.xlsx'), sheet_name='2017', header=None, dtype=object)
hdr = [str(x).strip() for x in mk.iloc[5, :].tolist()]
t007 = mk[mk[0].astype(str).str.strip() == 'T007'].iloc[0]
q = {c: float(t007[hdr.index(c)]) for c in comms if c in hdr}
assert len(q) == n, (n, len(q))

A = np.eye(n) - np.linalg.inv(Lmat)
X = [c for c in comms if c in {'211000', '212100', '221100', '221200', 'S00101', 'S00202'} or c.startswith('3241')]
Xi = [ci[c] for c in X]
print('energy block', X)
Ap = A.copy(); Ap[:, Xi] = 0.0
Lp = np.linalg.inv(np.eye(n) - Ap)
e = Lp[Xi, :].sum(0)
e[Xi] = 1.0


def wmean(codes):
    k = [ci[c] for c in codes if c in ci]
    return float(sum(e[i] * q[comms[i]] for i in k) / sum(q[comms[i]] for i in k))


eT = wmean(['482000', '483000', '484000'])
eW = wmean([c for c in comms if c.startswith('42')])
eR = wmean([c for c in comms if (c[:2] in ('44', '45') or c == '4B0000') and c != '447000'])
print('margin exposures T/W/R', round(eT, 4), round(eW, 4), round(eR, 4))

br = pd.read_excel(os.path.join(RAW, 'PCEBridge_2017_DET_retrieved_2026-11-14.xlsx'), sheet_name='2017', header=None, dtype=object).iloc[5:]
br = br[br[0].notna()].copy()
br[0] = br[0].astype(int)
for j in (4, 5, 6, 7, 8):
    br[j] = pd.to_numeric(br[j], errors='coerce').fillna(0.0)
br[2] = br[2].astype(str).str.strip()

ex = pd.read_csv(os.path.join(TAG, 'item_exposures_full.csv'))
tags = pd.read_csv(os.path.join(TAG, 'proposed_tags.csv'))
ex['leaf'] = ex.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
tags['leaf'] = tags.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
tagmap = tags.set_index('leaf').tag_final.to_dict()
res = []
for _, r in ex.iterrows():
    lines = [int(x) for x in str(r.bridge_lines).split(';')]
    b = br[br[0].isin(lines)]
    pur = b[8].sum()
    val = sum(row[4] * e[ci[row[2]]] + row[5] * eT + row[6] * eW + row[7] * eR for _, row in b.iterrows()) / pur
    top = b.groupby(2)[8].sum().sort_values(ascending=False)
    res.append(dict(leaf=r.leaf, component_name=r.component_name, bridge_lines=r.bridge_lines, weight_latest=r.weight_latest,
                    top_commodity=top.index[0], top_commodity_share_of_purch=round(top.iloc[0] / pur, 3),
                    energy_share_file=r.energy_main, energy_share_recomputed=val))
d = pd.DataFrame(res)
d['abs_diff'] = (d.energy_share_recomputed - d.energy_share_file).abs()
w = d.weight_latest.values; o = np.argsort(d.energy_share_recomputed.values)
cut_re = float(d.energy_share_recomputed.values[o][np.searchsorted(np.cumsum(w[o]), 0.75)])
o2 = np.argsort(d.energy_share_file.values)
cut_file = float(d.energy_share_file.values[o2][np.searchsorted(np.cumsum(w[o2]), 0.75)])
print(f'weighted p75 cutoff: recomputed {cut_re:.5f}, file {cut_file:.5f}')
d['tag_final'] = d.leaf.map(tagmap)
d['file_above_cutoff'] = d.energy_share_file >= cut_file
d['recomputed_above_cutoff'] = d.energy_share_recomputed >= cut_re
print('all-149 max abs diff', d.abs_diff.max(), 'n with >1e-4 diff', int((d.abs_diff > 1e-4).sum()),
      'n where above/below cutoff disagrees', int((d.file_above_cutoff != d.recomputed_above_cutoff).sum()))
d['cutoff_used'] = round(cut_file, 5)
d['dist_to_cutoff_pp'] = ((d.energy_share_file - cut_file) * 100).round(3)

# choose spot-check set
en = d[d.tag_final == 'energy'].sort_values('weight_latest', ascending=False)
top5 = list(en.leaf.head(5))
tagged_en_above = d[(d.tag_final == 'energy')].sort_values('dist_to_cutoff_pp')
above2 = list(tagged_en_above.leaf.head(2))
below = d[(d.energy_share_file < cut_file)].sort_values('dist_to_cutoff_pp', ascending=False)
below2 = list(below.leaf.head(2))
special = {}
for name_part, lab in (('Water supply and sewage', 'water/sewage (named in brief)'), ('Membership clubs', 'membership clubs (named in brief)'),
                       ('Lotteries', 'lotteries (override to untagged)')):
    m = d[d.component_name.str.contains(name_part, case=False, regex=False)]
    for l in m.leaf:
        special[l] = lab
sel = {}
def addrole(l, lab):
    sel[l] = (sel[l] + '; ' + lab) if l in sel else lab
for l in top5: addrole(l, 'top-5 energy-tagged by weight')
for l in above2: addrole(l, 'just above cutoff (energy-tagged)')
for l in below2: addrole(l, 'just below cutoff (not energy-tagged by the rule)')
for l, lab in special.items(): addrole(l, lab)
d['spot_check_role'] = d.leaf.map(sel).fillna('')
d['in_spot_check_set'] = d.leaf.isin(sel)
d['rank_by_energy_share'] = d.energy_share_file.rank(ascending=False).astype(int)
for c in ('energy_share_file', 'energy_share_recomputed', 'abs_diff'):
    d[c] = d[c].round(6)
d['note'] = ''
d.loc[d.leaf == 228, 'note'] = 'Lotteries: overridden to untagged in tag_final (I-O mapping artifact, S00203 per tag_rules.py)'
d = d.sort_values(['in_spot_check_set', 'weight_latest'], ascending=[False, False])
cols = ['in_spot_check_set', 'spot_check_role', 'leaf', 'component_name', 'bridge_lines', 'weight_latest', 'tag_final', 'energy_share_file',
        'energy_share_recomputed', 'abs_diff', 'cutoff_used', 'dist_to_cutoff_pp', 'rank_by_energy_share', 'file_above_cutoff', 'recomputed_above_cutoff',
        'top_commodity', 'top_commodity_share_of_purch', 'note']
d[cols].to_csv(os.path.join(OUT, 'A_q1_energy_spotcheck.csv'), index=False)
print(d[d.in_spot_check_set][cols[:12]].to_string())
