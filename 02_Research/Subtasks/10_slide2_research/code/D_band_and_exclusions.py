"""Brief D, Q12 (attacks 2, 3, 9): how much core weight sits just above/below the 3% line, and breadth
excluding OER (leaf 162) and/or the hospital leaves (184-186).

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_band_and_exclusions.py"

Engine: 09_slide1_research/code/C_common.py via A_common.py (both read-only). Weighted leaf, start-of-window weights.
Writes: outputs/D_band_leaves.csv (core leaves with rate in (2.5, 3.5], Sep and Oct est., 12m and 3m),
        outputs/D_band_summary.csv (weight share by band), outputs/D_exclusions.csv (breadth ex OER / ex hospitals).
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'code'))
import A_common as a  # noqa: E402

OUT = a.OUT
a.check_mapping()
a.slide1_checks()
NAMES = a.cc.eng.names
BANDS = [(-1e9, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 3.5), (3.5, 4.0), (4.0, 1e9)]
EXCL = {'none': set(), 'ex_OER_162': {162}, 'ex_hospitals_184_186': {184, 185, 186},
        'ex_OER_and_hospitals': {162, 184, 185, 186}}

leaf_rows, band_rows, ex_rows = [], [], []
for m in ('2026-09', '2026-10'):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = a.leaf_table(m, back)
        status = 'UMD est.' if m == '2026-10' else 'BEA published'
        for lo, hi in BANDS:
            s = d[(d.r > lo) & (d.r <= hi)]
            band_rows.append(dict(month=m, status=status, horizon=hz, band=f'({lo if lo > -1e8 else "-inf"}, {hi if hi < 1e8 else "inf"}]',
                                  n_leaves=len(s), weight_share_pct=round(100 * s.ws.sum(), 3)))
        s = d[(d.r > 2.5) & (d.r <= 3.5)].sort_values('ws', ascending=False)
        for _, r in s.iterrows():
            leaf_rows.append(dict(month=m, status=status, horizon=hz, leaf=int(r.leaf), name=NAMES[int(r.leaf)], tag=r.tag,
                                  rate_pct=round(r.r, 3), weight_share_pct=round(100 * r.ws, 3), above3=bool(r.r > 3)))
        for k, ex in EXCL.items():
            s = d[~d.leaf.isin(ex)]
            ex_rows.append(dict(month=m, status=status, horizon=hz, exclusion=k,
                                breadth_gt3_pct=round(100 * s.w[s.r > 3].sum() / s.w.sum(), 3),
                                excluded_weight_share_pct=round(100 * d[d.leaf.isin(ex)].ws.sum(), 3)))

pd.DataFrame(leaf_rows).to_csv(os.path.join(OUT, 'D_band_leaves.csv'), index=False)
bs = pd.DataFrame(band_rows)
bs.to_csv(os.path.join(OUT, 'D_band_summary.csv'), index=False)
exd = pd.DataFrame(ex_rows)
exd.to_csv(os.path.join(OUT, 'D_exclusions.csv'), index=False)
print(bs.to_string(index=False))
print(exd.to_string(index=False))
