"""L: what is inside 'Everything else' (untagged) on slide 2B left chart. Eli Nov 17. Not audited.

Leaf-level split of the untagged group's excess: s_i x (r_i - b_i), b_i = leaf's mean 12m rate over 2018-19
(G_baseline_attribution 'leaf' level). Leaf sum differs slightly from the group-level number on the slide (mix term).
Run from project root: python3 -I 02_Research/Subtasks/10_slide2_research/code/L_untagged_composition.py
"""
import os, sys
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

t = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
TAG = dict(zip(t.leaf, t.tag_final))
NAME = dict(zip(t.leaf, t[[c for c in t.columns if 'name' in c.lower() or 'label' in c.lower()][0]]))
CORE = set(cc.LEAVES_CORE)

def tab(m):
    d = cc.unit_table('leaf', CORE, m, 12); d['s'] = d.w / d.w.sum(); d['tag'] = d.leaf.map(TAG); return d

base = {}
for y in (2018, 2019):
    for mo in range(1, 13):
        x = tab(f'{y}-{mo:02d}')
        for lf, r in zip(x.leaf, x.r):
            base.setdefault(lf, []).append(r)
b = {k: sum(v) / len(v) for k, v in base.items()}
rows = []
for m in ('2025-03', '2026-10'):
    d = tab(m)
    d = d[d.tag == 'untagged'].copy()
    d['excess'] = d.s * (d.r - d.leaf.map(b))
    for _, r in d.iterrows():
        rows.append(dict(month=m, leaf=r.leaf, name=NAME.get(r.leaf), share=r.s, rate=r.r, base=b[r.leaf], excess_pp=r.excess))
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, 'L_untagged_composition.csv'), index=False)
for m in ('2025-03', '2026-10'):
    x = R[R.month == m].sort_values('excess_pp', ascending=False)
    print(m, 'leaf-sum', round(x.excess_pp.sum(), 3), 'share', round(x.share.sum(), 3))
    print(x.head(12)[['leaf', 'name', 'share', 'rate', 'base', 'excess_pp']].round(3).to_string(index=False))
    print(x.tail(4)[['leaf', 'name', 'share', 'rate', 'base', 'excess_pp']].round(3).to_string(index=False))
