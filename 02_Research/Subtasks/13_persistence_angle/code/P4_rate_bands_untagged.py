"""P4: K_rate_bands (slide 2) rerun on UNTAGGED core leaves ex hospitals (184-186), plus the tagged complement.
Same engine (09_slide1_research C_common, weighted leaf, 12m, start-of-window weights) and same bands/months as
10_slide2_research/code/K_rate_bands.py. Tags: 08_shock_tagging/proposed_tags.csv, column tag_final (Eli, Nov 14).
Reproduction check: union of the two groups equals K_rate_bands.csv (all core ex hospitals).
Run from project root: python3 -I "02_Research/Subtasks/13_persistence_angle/code/P4_rate_bands_untagged.py"
"""
import os, sys
import pandas as pd
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402
tags = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
tags['leaf'] = tags.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
TAG = tags.set_index('leaf').tag_final.to_dict()
ALL = set(cc.LEAVES_CORE) - {184, 185, 186}
print('tag_final values:', sorted(set(str(TAG.get(l)) for l in ALL)))
UNT = {l for l in ALL if str(TAG.get(l)).lower() in ('untagged', 'none', 'nan', '')}
BANDS = [('below 2%', -99, 2), ('2-3%', 2, 3), ('3-4%', 3, 4), ('4-6%', 4, 6), ('6% or more', 6, 999)]
def bands(LS, m):
    d = cc.unit_table('leaf', LS, m, 12); w = d.w / d.w.sum()
    return {nm: 100 * w[(d.r > lo) & (d.r <= hi)].sum() for nm, lo, hi in BANDS}
out = []
for grp, LS in (('untagged ex hospitals', UNT), ('tagged (energy/tariff/AI)', ALL - UNT), ('all core ex hospitals', ALL)):
    pre = [bands(LS, f'{y}-{mo:02d}') for y in (2018, 2019) for mo in range(1, 13)]
    rows = {'2018-19 avg': {k: sum(p[k] for p in pre) / len(pre) for k in pre[0]}}
    for m, lab in (('2025-03', 'Mar 2025 (core PCE low)'), ('2026-02', 'Feb 2026 (pre-oil)'), ('2026-09', 'Sep 2026'), ('2026-10', 'Oct 2026 est.')):
        rows[lab] = bands(LS, m)
    R = pd.DataFrame(rows).T
    R['above 3%'] = R[['3-4%', '4-6%', '6% or more']].sum(axis=1)
    R['above 4%'] = R[['4-6%', '6% or more']].sum(axis=1)
    R.insert(0, 'group', grp); R.index.name = 'period'
    out.append(R.round(1))
O = pd.concat(out)
K = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs', 'K_rate_bands.csv'), index_col=0)
chk = O[O.group == 'all core ex hospitals'].drop(columns='group')
for p in K.index:
    assert abs(chk.loc[p, '6% or more'] - K.loc[p, '6% or more']) < 0.11 and abs(chk.loc[p, 'above 3%'] - K.loc[p, 'above 3% (breadth)']) < 0.11, p
print('reproduces K_rate_bands.csv: OK; untagged leaves', len(UNT), 'of', len(ALL))
O.to_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs', 'P4_rate_bands_untagged.csv'))
print(O.to_string())
