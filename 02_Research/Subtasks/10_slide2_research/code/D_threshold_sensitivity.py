"""Brief D, Q12 attack 2 ("why 3%?"): breadth at alternative cutoffs, plus distribution percentiles.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_threshold_sensitivity.py"

Engine: 09_slide1_research/code/C_common.py, imported read-only (unit_table, SCOPES). Same method as the binding
definition (share of start-of-window nominal weight with annualized rate > thr; 3m annualized before the cutoff;
weighted leaf central), with only `thr` varied. Oct 2026 = UMD estimate ("est.").
First reproduces the slide 1 binding numbers (core leaf 12m Sep 60.626 / Oct 54.038; 3m 44.814 / 45.467).

Writes (10_slide2_research/outputs/):
  D_threshold_sensitivity.csv   scope x horizon x month(Sep, Oct est.) x thr, plus 2018-19 average and post-2018 max
  D_threshold_ts.csv            monthly core leaf breadth 2018-01..2026-10 at each thr (12m, 3m)
  D_distribution.csv            weighted percentiles (p10/p25/p50/p75/p90) of core leaf rates, Sep/Oct, and 2018-19 avg
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402  (read-only import of the audited engine)

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
VINTAGE = 'BEA U20404/U20405 vintage 2026-11-10 (data through Sep 2026); Oct 2026 = UMD estimate (04_oct_pce_build)'
THRS = [2.0, 2.5, 3.0, 3.5, 4.0]
SCOPES = {
    'core': set(cc.SCOPES['core']),
    'supercore': set(cc.SCOPES['supercore']),
    'core_goods': set(l for l in cc.SCOPES['core'] if l < 150),
    'core_services': set(cc.SCOPES['core_services']),
    'headline_backup': set(cc.SCOPES['headline']),
}

# ---- reproduction check (binding numbers)
for (back, m), want in {(12, '2026-09'): 60.626, (12, '2026-10'): 54.038, (3, '2026-09'): 44.814, (3, '2026-10'): 45.467}.items():
    got = cc.breadth('leaf', 'core', m, back)[0]
    assert abs(got - want) < 0.01, (back, m, got, want)
print('slide 1 reproduction: pass')

_cache = {}


def tab(end, back):
    k = (str(end), back)
    if k not in _cache:
        _cache[k] = cc.unit_table('leaf', SCOPES['headline_backup'], end, back)
    return _cache[k]


def br(d, leafset, thr):
    s = d[d.leaf.isin(leafset)]
    return 100 * s.w[s.r > thr].sum() / s.w.sum()


def wpct(d, leafset, q):
    s = d[d.leaf.isin(leafset)].sort_values('r')
    cw = s.w.cumsum() / s.w.sum()
    return float(s.r.values[np.searchsorted(cw.values, q)])


months = pd.period_range('2018-01', '2026-10', freq='M')
hist = [m for m in months if m.year in (2018, 2019)]

ts_rows, rows, dist_rows = [], [], []
for back in (12, 3):
    for m in months:
        d = tab(m, back)
        rec = dict(month=str(m), horizon='12m' if back == 12 else '3m_ann', status='UMD est.' if str(m) == '2026-10' else 'BEA published')
        for scope, ls in SCOPES.items():
            for t in THRS:
                rec[f'{scope}_gt{t}'] = round(br(d, ls, t), 3)
        for q in (0.1, 0.25, 0.5, 0.75, 0.9):
            rec[f'core_p{int(q*100)}'] = round(wpct(d, SCOPES['core'], q), 3)
        ts_rows.append(rec)
ts = pd.DataFrame(ts_rows)

for back, hz in ((12, '12m'), (3, '3m_ann')):
    s = ts[ts.horizon == hz].set_index('month')
    h = s.loc[[str(m) for m in hist]]
    for scope in SCOPES:
        for t in THRS:
            c = f'{scope}_gt{t}'
            pk_m = s[c].idxmax()
            rows.append(dict(scope=scope, horizon=hz, threshold_pct=t,
                             sep_2026=s.at['2026-09', c], oct_2026_est=s.at['2026-10', c],
                             change_pp=round(s.at['2026-10', c] - s.at['2026-09', c], 3),
                             avg_2018_19=round(h[c].mean(), 3),
                             sep_minus_2018_19_pp=round(s.at['2026-09', c] - h[c].mean(), 3),
                             post2018_max=s.at[pk_m, c], post2018_max_month=pk_m,
                             vintage=VINTAGE))
    for q in (10, 25, 50, 75, 90):
        c = f'core_p{q}'
        dist_rows.append(dict(horizon=hz, stat=f'weighted p{q} of core leaf rates (%)', sep_2026=s.at['2026-09', c],
                              oct_2026_est=s.at['2026-10', c], avg_2018_19=round(h[c].mean(), 3), vintage=VINTAGE))

res = pd.DataFrame(rows)
# guard: the 3% column must equal the binding numbers
r3 = res[(res.scope == 'core') & (res.threshold_pct == 3.0)].set_index('horizon')
assert abs(r3.at['12m', 'sep_2026'] - 60.626) < 0.01 and abs(r3.at['12m', 'oct_2026_est'] - 54.038) < 0.01
assert abs(r3.at['3m_ann', 'sep_2026'] - 44.814) < 0.01 and abs(r3.at['3m_ann', 'oct_2026_est'] - 45.467) < 0.01

res.to_csv(os.path.join(OUT, 'D_threshold_sensitivity.csv'), index=False)
ts.to_csv(os.path.join(OUT, 'D_threshold_ts.csv'), index=False)
pd.DataFrame(dist_rows).to_csv(os.path.join(OUT, 'D_distribution.csv'), index=False)
print(res[res.scope.isin(['core', 'supercore', 'core_goods'])][['scope', 'horizon', 'threshold_pct', 'sep_2026', 'oct_2026_est', 'avg_2018_19', 'sep_minus_2018_19_pp', 'post2018_max', 'post2018_max_month']].to_string(index=False))
print(pd.DataFrame(dist_rows).to_string(index=False))
