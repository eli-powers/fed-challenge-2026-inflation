"""P5: which untagged core leaves (ex hospitals) make up the 6%+ band in P4, and how fragile is it?

Same engine and weights as P4 / slide 2 K_rate_bands (weighted leaf, 12m, start-of-window weights,
tag_final from 08_shock_tagging/proposed_tags.csv). Lists every untagged leaf above 6% in Feb 2026,
Sep 2026 and Oct 2026 est., with its share of untagged spending and 12m rate, and the 6%+ share
excluding the largest leaf and the largest two.
Run from project root: python3 -I "02_Research/Subtasks/13_persistence_angle/code/P5_untagged_hot_tail.py"
"""
import os, sys
import pandas as pd
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402
tags = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
tags['leaf'] = tags.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
TAG = tags.set_index('leaf').tag_final.to_dict()
NAME = tags.set_index('leaf').component_name.to_dict()
ALL = set(cc.LEAVES_CORE) - {184, 185, 186}
UNT = {l for l in ALL if str(TAG.get(l)).lower() in ('untagged', 'none', 'nan', '')}
rows, summ = [], []
for m in ('2025-03', '2026-02', '2026-09', '2026-10'):
    d = cc.unit_table('leaf', UNT, m, 12)
    d['share'] = 100 * d.w / d.w.sum()
    hot = d[d.r > 6].sort_values('share', ascending=False)
    for _, x in hot.iterrows():
        rows.append(dict(month=m, leaf=int(x.leaf), name=NAME.get(int(x.leaf), ''), share_of_untagged=round(x.share, 2), r12=round(x.r, 2)))
    tot = hot.share.sum()
    summ.append(dict(month=m, n_leaves=len(hot), share_6plus=round(tot, 2),
                     ex_top1=round(tot - hot.share.iloc[:1].sum(), 2), ex_top2=round(tot - hot.share.iloc[:2].sum(), 2),
                     top1=NAME.get(int(hot.leaf.iloc[0]), '') if len(hot) else ''))
out = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs')
pd.DataFrame(rows).to_csv(os.path.join(out, 'P5_untagged_hot_tail_leaves.csv'), index=False)
pd.DataFrame(summ).to_csv(os.path.join(out, 'P5_untagged_hot_tail_summary.csv'), index=False)
print(pd.DataFrame(summ).to_string())
print(pd.DataFrame(rows).to_string())
