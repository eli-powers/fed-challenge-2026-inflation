"""K: share of core spending (ex hospitals 184-186) by 12m inflation band, 2018-19 avg vs Mar 2025 (core PCE low) vs Feb 2026 vs Oct 2026 est.
Run from the project root: python3 -I "02_Research/Subtasks/10_slide2_research/code/K_rate_bands.py". Engine: C_common (read-only). Not audited.
Writes outputs/K_rate_bands.csv."""
import os, sys
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402
for (m, b), want in {('2026-09', 12): 60.626, ('2026-10', 12): 54.038}.items():
    assert abs(cc.breadth('leaf', 'core', m, b)[0] - want) < 0.01
LS = set(cc.LEAVES_CORE) - {184, 185, 186}
BANDS = [('below 2%', -99, 2), ('2-3%', 2, 3), ('3-4%', 3, 4), ('4-6%', 4, 6), ('6% or more', 6, 999)]
def bands(m):
    d = cc.unit_table('leaf', LS, m, 12); w = d.w / d.w.sum()
    return {nm: 100 * w[(d.r > lo) & (d.r <= hi)].sum() for nm, lo, hi in BANDS}
pre = [bands(f'{y}-{mo:02d}') for y in (2018, 2019) for mo in range(1, 13)]
rows = {'2018-19 avg': {k: sum(p[k] for p in pre) / len(pre) for k in pre[0]}}
for m, lab in (('2025-03', 'Mar 2025 (core PCE low)'), ('2026-02', 'Feb 2026 (pre-oil)'), ('2026-10', 'Oct 2026 est.')):
    rows[lab] = bands(m)
R = pd.DataFrame(rows).T.round(1)
R['above 3% (breadth)'] = R[['3-4%', '4-6%', '6% or more']].sum(axis=1).round(1)
R['above 4%'] = R[['4-6%', '6% or more']].sum(axis=1).round(1)
R.to_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs', 'K_rate_bands.csv'))
print(R.to_string())
