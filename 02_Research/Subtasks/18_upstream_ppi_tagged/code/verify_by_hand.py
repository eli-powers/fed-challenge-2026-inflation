"""Coordinator verification: recompute 3 reported numbers from saved intermediates, spot-check 3 index values against
raw files saved by OTHER subtasks (independent downloads), and print tag diagnostics. Reads outputs/ only + raw."""
import glob
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
O = os.path.join(HERE, 'outputs')
G = pd.read_csv(os.path.join(O, 'group_monthly_all_versions.csv'))
c = G[(G.stage == 'stage4') & (G.version == 'central')]
out = []
# 1-2: group excess = s x (R - mean of R over 2018-19), energy and tariff, Oct 2026
for g in ('energy', 'tariff'):
    x = c[c.group == g]
    B = x[x.month.str[:4].isin(['2018', '2019'])].R.mean()
    n = x[x.month == '2026-10'].iloc[0]
    out.append(f'stage4 central {g} Oct 2026: s={n.s:.4f} R={n.R:.3f} B(24 months)={B:.3f} -> excess {n.s * (n.R - B):.3f} (script {n.excess:.3f})')
# 3: item-level contributions sum to the AI group excess; total = sum of groups
T = pd.read_csv(os.path.join(O, 'top10_oct2026.csv'))
t = T[(T.stage == 'stage4') & (T.version == 'central') & (T.group == 'AI')]
out.append(f'stage4 central AI Oct 2026: sum of item contribs (top {len(t)} AI items) = {t.contrib_to_group_excess.sum():.3f}; '
           f'group excess {c[(c.group == "AI") & (c.month == "2026-10")].excess.iloc[0]:.3f}')
tot = c[(c.month == '2026-10') & (c.group != '_total')].excess.sum()
out.append(f'stage4 central total Oct 2026 = sum of groups {tot:.3f}; shares sum {c[(c.month == "2026-10") & (c.group != "_total")].s.sum():.4f}')


# spot checks vs independently saved raw
def val(pattern, sid, m):
    for f in glob.glob(pattern):
        for s in json.load(open(f))['Results']['series']:
            if s['seriesID'] == sid:
                for o in s['data']:
                    if f"{o['year']}-{o['period'][1:]}" == m:
                        return float(o['value']), os.path.basename(f)
    return None, None


new = os.path.join(ROOT, '03_Data/Raw/BLS_PPI_stage_commodities_2026-11-17/*.json')
for sid, m, old in (('WPUID54', '2026-10', '03_Data/Raw/BLS_PPI_stages_2026-11-15/*.json'),
                    ('WPUID51', '2025-03', '03_Data/Raw/BLS_PPI_stages_2026-11-15/*.json'),
                    ('WPU141205', '2025-12', '03_Data/Raw/BLS_PPI_stage1_commodities_2026-11-15/*.json'),
                    ('WPU102302', '2026-10', '03_Data/Raw/BLS_PPI_stage1_commodities_2026-11-15/*.json')):
    a, fa = val(new, sid, m)
    b, fb = val(os.path.join(ROOT, old), sid, m)
    out.append(f'spot {sid} {m}: new raw {a} ({fa}) vs earlier raw {b} ({fb})')
TG = pd.read_csv(os.path.join(O, 'tag_table.csv'))
for st in ('stage4', 'stage1'):
    t = TG[(TG.stage == st) & TG.import_share.notna()]
    near = t[(t.import_share - 0.15).abs() < 0.03]
    out.append(f'{st}: goods with import share within 3 pp of 15%: {len(near)} units, RI {near.ri.sum():.2f}')
print('\n'.join(out))
open(os.path.join(O, 'verify_by_hand.txt'), 'w').write('\n'.join(out) + '\n')
