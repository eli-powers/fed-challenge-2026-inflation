"""Brief C cross-check: which basis reproduces Waller's "more than 70 percent of the components of core PCE service prices saw
12-month increases above 3 percent in September"? Count and weight variants, Sep 2026 and Oct 2026 estimate, 12m rate.
Run from the project root:  python3 -I "02_Research/Subtasks/09_slide1_research/code/C_waller_variants.py"
Writes outputs/C_waller_variants.csv. Core services = services (line>=150) leaves/sub-lines in the core set, incl. housing."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import *  # noqa: E402,F403

rows = []
for period in ('2026-09', '2026-10'):
    for gran in ('leaf', 'sub'):
        for scope in ('core_services', 'supercore'):
            d = unit_table(gran, SCOPES[scope], period, 12)
            above = d.r > 3
            wend = pd.Series([nominal_weight(l, lf, SEP, gran) for l, lf in zip(d.line, d.leaf)], index=d.index)
            variants = {
                'count (unweighted)': 100 * above.mean(),
                'weight: start-of-window (shares 12 months before the end month)': 100 * d.w[above].sum() / d.w.sum(),
                'weight: latest shares (Sep 2026)': 100 * wend[above].sum() / wend.sum(),
            }
            if scope == 'core_services':
                nh = ~d.leaf.between(153, 164)
                variants['count, ex housing leaves (153-164)'] = 100 * above[nh].mean()
                variants['count, ex housing and ex NPISH (342)'] = 100 * above[nh & (d.leaf != 342)].mean()
            for k, v in variants.items():
                rows.append(dict(period=period, status='BEA published' if period == '2026-09' else 'estimate', scope=scope,
                                 method='sub-line' if gran == 'sub' else 'leaf', n_units=len(d), variant=k, value_pct=round(v, 3),
                                 exceeds_70=bool(v > 70)))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(OUTDIR, 'C_waller_variants.csv'), index=False)
pd.set_option('display.width', 200)
print(out.to_string())
