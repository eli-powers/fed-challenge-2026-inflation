"""I: October 2026 est. breadth distribution EXCLUDING hospitals (184-186), for the slide 2B inventory (Codex slide2_followups R3-F01).

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/I_exhosp_distribution.py"
Engine: 09_slide1_research/code/C_common.py (read-only). Core leaves minus 184-186; start-of-window weights; 12m rates.
Outputs outputs/I_exhosp_distribution.csv:
  - breadth at cutoffs 2.0/2.5/3.0/3.5/4.0, Oct 2026 est. vs the 2018-19 monthly average (same basket);
  - weighted median 12m leaf rate, Oct 2026 est. vs the 2018-19 average of monthly weighted medians;
  - share of weight with 12m rate in (3.0, 3.5], Oct 2026 est.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

for (m, b), want in {('2026-09', 12): 60.626, ('2026-10', 12): 54.038, ('2026-09', 3): 44.814, ('2026-10', 3): 45.467}.items():
    assert abs(cc.breadth('leaf', 'core', m, b)[0] - want) < 0.01
LS = set(cc.LEAVES_CORE) - {184, 185, 186}
THR = (2.0, 2.5, 3.0, 3.5, 4.0)


def stats(m):
    d = cc.unit_table('leaf', LS, m, 12).sort_values('r')
    w = d.w / d.w.sum()
    out = {t: 100 * w[d.r > t].sum() for t in THR}
    cw = np.cumsum(w.values)
    out['median'] = float(d.r.values[np.searchsorted(cw, 0.5)])
    out['band'] = 100 * w[(d.r > 3.0) & (d.r <= 3.5)].sum()
    return out


pre = [stats(f'{y}-{mo:02d}') for y in (2018, 2019) for mo in range(1, 13)]
avg = {k: float(np.mean([p[k] for p in pre])) for k in pre[0]}
now = stats('2026-10')
rows = [dict(item=f'breadth >{t}% (12m)', oct_2026_est=round(now[t], 3), avg_2018_19=round(avg[t], 3), gap_pp=round(now[t] - avg[t], 3)) for t in THR]
rows.append(dict(item='weighted median 12m leaf rate (%)', oct_2026_est=round(now['median'], 3), avg_2018_19=round(avg['median'], 3), gap_pp=round(now['median'] - avg['median'], 3)))
rows.append(dict(item='share of weight with 12m rate in (3.0, 3.5] (%)', oct_2026_est=round(now['band'], 3), avg_2018_19=round(avg['band'], 3), gap_pp=None))
R = pd.DataFrame(rows)
R['basket'] = 'core leaves excl. hospitals 184-186; start-of-window weights; Oct 2026 = UMD est.'
R.to_csv(os.path.join(OUT, 'I_exhosp_distribution.csv'), index=False)
print(R.to_string(index=False))
