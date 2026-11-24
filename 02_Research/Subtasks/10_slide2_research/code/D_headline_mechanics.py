"""Brief D, Q12 attack 8 (headline mechanics): decompose headline breadth into core, food and energy leaves.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_headline_mechanics.py"

Engine: 09_slide1_research/code/C_common.py (read-only). Headline = 177 leaves; core = 149; non-core leaves split into
energy (gasoline/fuels 115-119, electricity and natural gas 170-171) and food (the rest of the non-core leaves).
Reports, per window, each block's share of headline weight, the share of that block above 3%, and its contribution
(pp) to headline breadth. Oct 2026 = UMD est.
Writes: outputs/D_headline_mechanics.csv, outputs/D_noncore_leaf_rates.csv
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
for (back, m), want in {(12, '2026-09'): 60.626, (12, '2026-10'): 54.038, (3, '2026-09'): 44.814, (3, '2026-10'): 45.467}.items():
    assert abs(cc.breadth('leaf', 'core', m, back)[0] - want) < 0.01
CORE = set(cc.SCOPES['core'])
NONCORE = [l for l in cc.LEAVES_ALL if l not in CORE]
ENERGY = {115, 116, 118, 119, 170, 171}
assert ENERGY <= set(NONCORE)
names = cc.eng.names


def block(l):
    return 'core' if l in CORE else ('energy' if l in ENERGY else 'food')


rows, lr = [], []
for m in ('2026-09', '2026-10'):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = cc.unit_table('leaf', set(cc.LEAVES_ALL), m, back)
        d['ws'] = d.w / d.w.sum()
        d['blk'] = d.leaf.map(block)
        hb = 100 * d.ws[d.r > 3].sum()
        for b, s in d.groupby('blk'):
            rows.append(dict(month=m, status='UMD est.' if m == '2026-10' else 'BEA published', horizon=hz, block=b,
                             share_of_headline_weight_pct=round(100 * s.ws.sum(), 3),
                             share_of_block_above3_pct=round(100 * s.ws[s.r > 3].sum() / s.ws.sum(), 3),
                             contribution_to_headline_breadth_pp=round(100 * s.ws[s.r > 3].sum(), 3),
                             headline_breadth_pct=round(hb, 3)))
        for _, r in d[d.blk != 'core'].iterrows():
            lr.append(dict(month=m, horizon=hz, leaf=int(r.leaf), name=names[int(r.leaf)], block=r.blk, rate_pct=round(r.r, 3),
                           headline_weight_share_pct=round(100 * r.ws, 3)))
res = pd.DataFrame(rows)
res.to_csv(os.path.join(OUT, 'D_headline_mechanics.csv'), index=False)
pd.DataFrame(lr).to_csv(os.path.join(OUT, 'D_noncore_leaf_rates.csv'), index=False)
print(res.to_string(index=False))
