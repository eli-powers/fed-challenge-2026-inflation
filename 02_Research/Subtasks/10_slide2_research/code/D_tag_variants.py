"""Brief D, Q12 attack 1 ("tags are arbitrary"): energy-group breadth and mean rate under leave-one-out variants.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_tag_variants.py"

Variants of the energy group (tag_final, Eli Nov 14): final; ex restaurants (241, 31% of the group); ex nursing homes
(187, +0.001 pp over the cutoff); ex both; strict 5% cutoff (A_common.tag_scheme(energy_cut=0.05)). Also untagged and
untagged ex hospitals (184-186). Months: Feb 2026 (pre-shock), Sep 2026, Oct 2026 est.; 12m and 3m ann.
Writes: outputs/D_tag_variants.csv
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'code'))
import A_common as a  # noqa: E402

a.check_mapping()
a.slide1_checks()
strict = a.tag_scheme(energy_cut=0.05)[0]
rows = []
for m in ('2026-02', '2026-09', '2026-10'):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = a.leaf_table(m, back)
        E = set(d[d.tag == 'energy'].leaf)
        U = set(d[d.tag == 'untagged'].leaf)
        var = {'energy final': E, 'energy ex 241 restaurants': E - {241}, 'energy ex 187 nursing homes': E - {187},
               'energy ex 241 and 187': E - {241, 187}, 'energy strict 5%': {l for l, t in strict.items() if t == 'energy'},
               'untagged': U, 'untagged ex hospitals 184-186': U - {184, 185, 186}}
        for k, ls in var.items():
            s = d[d.leaf.isin(ls)]
            rows.append(dict(month=m, status='UMD est.' if m == '2026-10' else 'BEA published', horizon=hz, variant=k, n_leaves=len(s),
                             weight_share_of_core_pct=round(100 * s.ws.sum(), 3),
                             breadth_within_gt3_pct=round(100 * s.w[s.r > 3].sum() / s.w.sum(), 3),
                             wmean_rate_pct=round((s.r * s.w).sum() / s.w.sum(), 3)))
res = pd.DataFrame(rows)
chk = res[(res.month == '2026-09') & (res.horizon == '12m') & (res.variant == 'energy final')].iloc[0]
assert abs(chk.breadth_within_gt3_pct - 66.962) < 0.01
res.to_csv(os.path.join(a.OUT, 'D_tag_variants.csv'), index=False)
print(res.pivot_table(index=['horizon', 'variant'], columns='month', values=['breadth_within_gt3_pct', 'wmean_rate_pct']).round(2).to_string())
