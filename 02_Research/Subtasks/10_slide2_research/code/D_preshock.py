"""Brief D, Q12 extra attack ("breadth was already this high before the oil shock"): pre-shock baselines.

Run from the project root (after D_threshold_sensitivity.py and agent A's A_q3_breadth.py):
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_preshock.py"

Pre-shock reference months: Sep 2025 (one year earlier) and Feb 2026 (last month before Brent's March 2026 jump:
monthly-average Brent $70.9 Feb -> $103.1 Mar, from outputs/C_q8_oil_daily.csv).
For each tag group (tag_final) and for core: within-group breadth (>3%), weighted mean rate and weighted median rate,
12m and 3m annualized, start-of-window weights, weighted leaf. Breadth for core/supercore/core goods is read from
D_threshold_ts.csv; tag-group breadth is recomputed and checked against A_q3_tagged_breadth_ts.csv.
Writes: outputs/D_preshock.csv
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'code'))
import A_common as a  # noqa: E402

OUT = a.OUT
a.check_mapping()
a.slide1_checks()
MONTHS = ['2025-09', '2026-02', '2026-09', '2026-10']
oil = pd.read_csv(os.path.join(OUT, 'C_q8_oil_daily.csv'))
oil['m'] = oil.date.astype(str).str[:7]
brent = oil.groupby('m').brent_usd_bbl.mean()
ats = pd.read_csv(os.path.join(OUT, 'A_q3_tagged_breadth_ts.csv')).set_index('month')
tts = pd.read_csv(os.path.join(OUT, 'D_threshold_ts.csv'))


def wmed(s):
    s = s.sort_values('r')
    cw = (s.w.cumsum() / s.w.sum()).values
    return float(s.r.values[np.searchsorted(cw, 0.5)])


rows = []
for m in MONTHS:
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = a.leaf_table(m, back)
        for g in ['core'] + a.GROUPS:
            s = d if g == 'core' else d[d.tag == g]
            b = 100 * s.w[s.r > 3].sum() / s.w.sum()
            if g != 'core':
                assert abs(b - ats.at[m, f'{g}_within_{hz}']) < 0.01, (m, g, hz)
            rows.append(dict(month=m, status='UMD est.' if m == '2026-10' else 'BEA published', horizon=hz, group=g,
                             breadth_gt3_pct=round(b, 3), wmean_rate_pct=round((s.r * s.w).sum() / s.w.sum(), 3),
                             wmedian_rate_pct=round(wmed(s), 3), weight_share_pct=round(100 * s.ws.sum(), 3),
                             brent_month_avg_usd=round(brent.get(m, np.nan), 1)))
        t = tts[(tts.month == m) & (tts.horizon == hz)].iloc[0]
        for sc in ('supercore', 'core_goods', 'core_services'):
            rows.append(dict(month=m, status='UMD est.' if m == '2026-10' else 'BEA published', horizon=hz, group=sc,
                             breadth_gt3_pct=t[f'{sc}_gt3.0'], brent_month_avg_usd=round(brent.get(m, np.nan), 1)))
res = pd.DataFrame(rows)
res.to_csv(os.path.join(OUT, 'D_preshock.csv'), index=False)
print(res.pivot_table(index=['horizon', 'group'], columns='month', values=['breadth_gt3_pct', 'wmean_rate_pct', 'wmedian_rate_pct']).round(2).to_string())
