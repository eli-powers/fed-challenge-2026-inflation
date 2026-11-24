"""H: core PCE drivers by BEA major category (excess contribution vs 2018-19), extended to Oct 2026 est. (slide 2A).

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/H_oct_drivers.py"
Method = the round-1 / pipeline method, reused read-only from 03_Data/pipelines/Price indexes/code/sector_contributions.py:
  exact Fisher monthly contributions of the core major categories, chained over 12 months; excess = 12m contribution
  minus the category's average 12m contribution over 2018-19 windows.
October 2026 (est.): one extra month appended to the BEA U20404/U20405 (vintage 2026-11-10) category panel.
  - category price relative r_cat = sum_leaves (Sep nominal share within category) x (1 + leaf Oct m/m est.)   [Laspeyres roll-up,
    leaf m/m = C_common.OCT_LEAF_PI, the audited October build];
  - category Oct nominal = Sep nominal x r_cat (constant real quantities; BEA's Oct nominal is unpublished).
Checks: (1) the Sep window reproduces 03_Data/pipelines/Price indexes/Cross-index analysis/processed/pce_sector_contributions_2026-09.csv;
        (2) Sep category nominal = sum of its core leaves; (3) Oct core m/m implied vs the build's 0.295.
Drill-down: leaf-level excess over own 2018-19 12m rate, s_i x (r_i - rbar_i) (as G, leaf level), within each category.
Writes outputs/H_oct_drivers_categories.csv, outputs/H_oct_drivers_leaves.csv.
"""
import importlib.util
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
PIPE = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

spec = importlib.util.spec_from_file_location('sector_contributions', os.path.join(PIPE, 'code', 'sector_contributions.py'))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

VINT = '2026-11-10'
p, n = sc.load('U20404', VINT), sc.load('U20405', VINT)
CORE = sc.CORE
CATS = sorted(CORE)
SEP, OCT = pd.Period('2026-09', 'M'), pd.Period('2026-10', 'M')

# ---- leaf -> category (core leaves only). Boundaries include the non-core blocks so leaves fall in the right parent.
BOUNDS = sorted(set(CATS) | {73, 113, 152, 169})
def cat_of(leaf):
    c = max(b for b in BOUNDS if b <= leaf)
    return c if c in CORE else None
LEAF_CAT = {l: cat_of(l) for l in cc.LEAVES_CORE}
assert all(v is not None for v in LEAF_CAT.values()), [l for l, v in LEAF_CAT.items() if v is None]
for c in CATS:   # check (2)
    ls = [l for l, v in LEAF_CAT.items() if v == c]
    unpriced = {120: 145, 280: 333}.get(c)            # BEA lines 145 and 333 have no price index (excluded from the 149 leaves)
    gap = abs(sum(n.at[SEP, l] for l in ls) + (n.at[SEP, unpriced] if unpriced else 0) - n.at[SEP, c])
    assert gap < 5, (c, gap)   # BEA nominal is rounded to $ millions; pipeline uses the same tolerance

# ---- append October 2026 (est.)
rel = {}
for c in CATS:
    ls = [l for l, v in LEAF_CAT.items() if v == c]
    w = np.array([n.at[SEP, l] for l in ls])
    rel[c] = float((w / w.sum() * np.array([1 + cc.OCT_LEAF_PI[l] / 100 for l in ls])).sum())
p.loc[OCT] = np.nan
n.loc[OCT] = np.nan
for c in CATS:
    p.at[OCT, c] = p.at[SEP, c] * rel[c]
    n.at[OCT, c] = n.at[SEP, c] * rel[c]
n.at[OCT, 374] = sum(n.at[OCT, c] for c in CATS)

c_m, F = sc.monthly_contrib(p, n, CATS)
oct_mm = (F[OCT] - 1) * 100
build_mm = float(pd.read_csv(cc.OCT_SUMMARY).set_index('measure').at['core', 'estimate_mm'])
print(f'Oct core m/m implied by category roll-up {oct_mm:.3f} vs build {build_mm:.3f}')   # check (3)

base = pd.concat([sc.window(c_m, F, t, 12)[0] for t in pd.period_range('2018-01', '2019-12', freq='M')], axis=1).mean(axis=1)
rows = []
for end in (SEP, OCT):
    c12, S12 = sc.window(c_m, F, end, 12)
    c3, S3 = sc.window(c_m, F, end, 3)
    k = ((1 + S3 / 100) ** 4 - 1) / (S3 / 100)
    for ln in CATS:
        rows.append(dict(period=str(end), status='estimate' if end == OCT else 'BEA published', line=ln, category=CORE[ln],
                         weight_pct=round(100 * n.at[end, ln] / sum(n.at[end, c] for c in CATS), 3),
                         rate_12m=round((p.at[end, ln] / p.at[end - 12, ln] - 1) * 100, 3), contrib_12m=round(c12[ln], 4),
                         contrib_12m_2018_19_avg=round(base[ln], 4), excess_vs_2018_19=round(c12[ln] - base[ln], 4),
                         rate_3m_ann=round(((p.at[end, ln] / p.at[end - 3, ln]) ** 4 - 1) * 100, 3), contrib_3m_ann=round(c3[ln] * k, 4)))
    rows.append(dict(period=str(end), status='estimate' if end == OCT else 'BEA published', line=374, category='TOTAL core (sum)',
                     rate_12m=round(S12, 3), contrib_12m=round(c12.sum(), 4), contrib_12m_2018_19_avg=round(base.sum(), 4),
                     excess_vs_2018_19=round(c12.sum() - base.sum(), 4), rate_3m_ann=round(((1 + S3 / 100) ** 4 - 1) * 100, 3), contrib_3m_ann=round(c3.sum() * k, 4)))
R = pd.DataFrame(rows)

# check (1): Sep reproduces the pipeline file
pipe = pd.read_csv(os.path.join(PIPE, 'Cross-index analysis', 'processed', 'pce_sector_contributions_2026-09.csv'))
pipe = pipe[pipe['index'] == 'Core PCE'].set_index('line')
mine = R[R.period == '2026-09'].set_index('line')
for ln in CATS + [374]:
    for a, b in (('contrib_12m', 'contrib_12m'), ('excess_vs_2018_19', 'excess_vs_2018_19')):
        assert abs(mine.at[ln, a] - pipe.at[ln, b]) < 2e-3, (ln, a, mine.at[ln, a], pipe.at[ln, b])
print('Sep reproduces the pipeline file (contrib_12m and excess, all categories)')
R.to_csv(os.path.join(OUT, 'H_oct_drivers_categories.csv'), index=False)

# ---- drill-down: leaf excess over own 2018-19 12m rate, within categories
t = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
TAG, NAME = dict(zip(t.leaf, t.tag_final)), dict(zip(t.leaf, t.component_name))
CORESET = set(cc.LEAVES_CORE)
bl = {}
for m in pd.period_range('2018-01', '2019-12', freq='M'):
    d = cc.unit_table('leaf', CORESET, str(m), 12)
    for lf, r in zip(d.leaf, d.r):
        bl.setdefault(lf, []).append(r)
bl = {k: sum(v) / len(v) for k, v in bl.items()}
L = []
for per in ('2026-09', '2026-10'):
    d = cc.unit_table('leaf', CORESET, per, 12)
    d['s'] = d.w / d.w.sum()
    for lf, s, r in zip(d.leaf, d.s, d.r):
        L.append(dict(period=per, leaf=lf, name=NAME[lf], category=CORE[LEAF_CAT[lf]], tag=TAG[lf], weight_pct=round(100 * s, 3),
                      rate_12m=round(r, 3), rate_2018_19=round(bl[lf], 3), excess_pp=round(s * (r - bl[lf]), 4)))
LD = pd.DataFrame(L)
LD.to_csv(os.path.join(OUT, 'H_oct_drivers_leaves.csv'), index=False)

pd.set_option('display.width', 220)
v = R.pivot_table(index='category', columns='period', values='excess_vs_2018_19').sort_values('2026-10', ascending=False)
v['rate_12m_oct'] = R[R.period == '2026-10'].set_index('category').rate_12m
v['weight_oct'] = R[R.period == '2026-10'].set_index('category').weight_pct
print(v.round(3).to_string())
for cat in v.index[:6]:
    if cat.startswith('TOTAL'):
        continue
    x = LD[(LD.period == '2026-10') & (LD.category == cat)].sort_values('excess_pp', ascending=False).head(3)
    print('  ', cat, '|', '; '.join(f"{a} [{tg}] {e:+.3f} ({r:.1f}% vs {b:.1f}%)" for a, tg, e, r, b in zip(x.name, x.tag, x.excess_pp, x.rate_12m, x.rate_2018_19)))
