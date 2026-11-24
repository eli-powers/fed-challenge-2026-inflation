"""Brief D, Q12 attacks 3 and 9: monthly contribution of the hospital leaves (184-186) and OER (162) to core 12m and
3m breadth, and core breadth excluding them, 2018-01 - Oct 2026 (Oct = UMD est.); plus 2018-19 averages.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_hospital_ts.py"
Engine: C_common via A_common (read-only). Writes: outputs/D_hospital_oer_ts.csv, outputs/D_hospital_oer_summary.csv
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'code'))
import A_common as a  # noqa: E402

a.slide1_checks()
H = {184, 185, 186}
rows = []
for m in pd.period_range('2018-01', '2026-10', freq='M'):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = a.leaf_table(m, back)
        h = d[d.leaf.isin(H)]
        o = d[d.leaf == 162]
        rest = d[~d.leaf.isin(H | {162})]
        rows.append(dict(month=str(m), status='UMD est.' if str(m) == '2026-10' else 'BEA published', horizon=hz,
                         core_breadth=round(100 * d.ws[d.over3].sum(), 3),
                         hospital_rate_184=round(float(d[d.leaf == 184].r.iloc[0]), 3),
                         hospital_contrib_pp=round(100 * h.ws[h.over3].sum(), 3),
                         oer_rate_162=round(float(o.r.iloc[0]), 3),
                         oer_contrib_pp=round(100 * o.ws[o.over3].sum(), 3),
                         rest_contrib_pp=round(100 * rest.ws[rest.over3].sum(), 3),
                         breadth_ex_hosp_oer_renorm=round(100 * rest.w[rest.r > 3].sum() / rest.w.sum(), 3)))
res = pd.DataFrame(rows)
res.to_csv(os.path.join(a.OUT, 'D_hospital_oer_ts.csv'), index=False)
h = res[res.month.str[:4].isin(['2018', '2019'])]
summ = []
for hz in ('12m', '3m_ann'):
    for c in ('core_breadth', 'breadth_ex_hosp_oer_renorm'):
        s_ = res[res.horizon == hz].set_index('month')[c]
        summ.append(dict(horizon=hz, measure=c, avg_2018_19=round(h[h.horizon == hz][c].mean(), 3), sep_2025=s_['2025-09'],
                         feb_2026=s_['2026-02'], sep_2026=s_['2026-09'], oct_2026_est=s_['2026-10']))
summ = pd.DataFrame(summ)
summ.to_csv(os.path.join(a.OUT, 'D_hospital_oer_summary.csv'), index=False)
print(summ.to_string(index=False))
