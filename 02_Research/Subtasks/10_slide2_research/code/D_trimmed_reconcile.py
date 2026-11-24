"""Brief D, Q12 extra attack ("60% of core is above 3% but the Dallas trimmed mean is 2.3%: which is right?").
GO Q4b; not covered by agent B's report, so answered here with data.

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_trimmed_reconcile.py"

What it does (UMD replication, not the Dallas series):
  1. Monthly trimmed mean over the 177 headline PCE leaves (BEA U20404/U20405, vintage 2026-11-10), Dallas
     proportions (24% lower tail, 31% upper tail, by expenditure weight; Dallas tech note 2009 revision, saved at
     03_Data/pipelines/Price indexes/PCE/raw/Dallas_trimmed_mean_tech_2026-11-10.pdf). Weight = previous-month nominal
     share; the boundary component enters with its fractional weight. 12m = compounded 12 monthly trimmed means.
     Checked against the published Dallas 1m / 6m / 12m for Sep 2026 (dallas_trimmed_mean_rates.csv).
  2. A "12m-rate trimmed mean": the same 24/31 trim applied once to the cross-section of 12m leaf rates.
  3. For the core leaves above 3% at 12m (Sep), how often their monthly changes were trimmed from the top.
Oct 2026 uses the UMD estimate (est.).

Writes: outputs/D_trimmed_reconcile.csv, outputs/D_trimmed_monthly.csv, outputs/D_trimmed_above3_fate.csv
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
DALLAS = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'Trimmed mean', 'processed', 'dallas_trimmed_mean_rates.csv')
LO, HI = 0.24, 0.31
LEAVES = cc.LEAVES_ALL
CORE = set(cc.SCOPES['core'])
assert len(LEAVES) == 177

for (back, m), want in {(12, '2026-09'): 60.626, (12, '2026-10'): 54.038, (3, '2026-09'): 44.814, (3, '2026-10'): 45.467}.items():
    assert abs(cc.breadth('leaf', 'core', m, back)[0] - want) < 0.01


def lvl(l, m):
    return cc.index_level(l, m, 'leaf')


def trim(x, w, lo=LO, hi=HI):
    """weighted trimmed mean with fractional boundary weights; returns (mean, per-item kept fraction, status)."""
    o = np.argsort(x, kind='mergesort')
    xs, ws = x[o], w[o] / w[o].sum()
    cum_hi = np.cumsum(ws)
    cum_lo = cum_hi - ws
    keep = np.clip(np.minimum(cum_hi, 1 - hi) - np.maximum(cum_lo, lo), 0, None) / ws
    mean = (xs * ws * keep).sum() / (ws * keep).sum()
    k = np.empty_like(keep)
    k[o] = keep
    status = np.where(k > 0.999, 'included', np.where(k > 0, 'boundary', ''))
    pos = np.empty_like(cum_lo)
    pos[o] = cum_lo
    status = np.where(status == '', np.where(pos < lo, 'cut_bottom', 'cut_top'), status)
    return mean, k, status


months = pd.period_range('2017-02', '2026-10', freq='M')
mrows, fate = [], []
for m in months:
    prev = m - 1
    x = np.array([100 * (lvl(l, m) / lvl(l, prev) - 1) for l in LEAVES])
    w = np.array([cc.bn.at[prev, l] for l in LEAVES])
    ok = ~np.isnan(x) & ~np.isnan(w)
    tm, k, st = trim(x[ok], w[ok])
    mrows.append(dict(month=str(m), status='UMD est.' if str(m) == '2026-10' else 'BEA published', trimmed_mm_pct=tm, n=int(ok.sum())))
    for l, xi, si in zip(np.array(LEAVES)[ok], x[ok], st):
        fate.append((str(m), l, xi, si))
mt = pd.DataFrame(mrows).set_index('month')
g = 1 + mt.trimmed_mm_pct / 100
mt['ann_1m'] = 100 * (g ** 12 - 1)
mt['ann_6m'] = 100 * (g.rolling(6).apply(np.prod, raw=True) ** 2 - 1)
mt['r12m'] = 100 * (g.rolling(12).apply(np.prod, raw=True) - 1)
mt.reset_index().to_csv(os.path.join(OUT, 'D_trimmed_monthly.csv'), index=False)

dal = pd.read_csv(DALLAS)
dal = dal[dal.period == '2026M09'].set_index('measure').value.to_dict()


def xsec_trim(end, scope_leaves):
    d = cc.unit_table('leaf', set(scope_leaves), end, 12)
    tm, _, _ = trim(d.r.values, d.w.values)
    wm = (d.r * d.w).sum() / d.w.sum()
    return tm, wm


rows = []
for m in ('2026-09', '2026-10'):
    st = 'UMD est.' if m == '2026-10' else 'BEA published'
    rows += [
        dict(month=m, status=st, measure='UMD replication: monthly 24/31 trim, 177 headline leaves, 1m annualized', value=mt.at[m, 'ann_1m'], dallas_published=dal.get('1-month annualized') if m == '2026-09' else None),
        dict(month=m, status=st, measure='UMD replication: same, 6m annualized', value=mt.at[m, 'ann_6m'], dallas_published=dal.get('6-month annualized') if m == '2026-09' else None),
        dict(month=m, status=st, measure='UMD replication: same, 12m', value=mt.at[m, 'r12m'], dallas_published=dal.get('12-month') if m == '2026-09' else None),
    ]
    for lab, ls in (('177 headline leaves', LEAVES), ('149 core leaves', CORE)):
        tm, wm = xsec_trim(m, ls)
        rows.append(dict(month=m, status=st, measure=f'cross-section trim (24/31) of 12m leaf rates, {lab}', value=tm))
        rows.append(dict(month=m, status=st, measure=f'start-of-window-weighted mean of 12m leaf rates, {lab} (not chained; cf. C_sum_gap)', value=wm))
rec = pd.DataFrame(rows)
rec['value'] = rec.value.round(3)
rec['vintage'] = 'BEA U20404/U20405 vintage 2026-11-10; Oct 2026 = UMD est.; Dallas: dallas_trimmed_mean_rates.csv (retrieved 2026-11-10)'
rec.to_csv(os.path.join(OUT, 'D_trimmed_reconcile.csv'), index=False)

# fate of the monthly changes of core leaves that are above 3% at 12m in Sep 2026 (window Oct 2025..Sep 2026)
F = pd.DataFrame(fate, columns=['month', 'leaf', 'mm', 'trim_status'])
d12 = cc.unit_table('leaf', CORE, '2026-09', 12)
d12['ws'] = d12.w / d12.w.sum()
win = [str(p) for p in pd.period_range('2025-10', '2026-09', freq='M')]
fw = F[F.month.isin(win)].merge(d12[['leaf', 'r', 'ws']], on='leaf')
fw['grp'] = np.where(fw.r > 3, 'core leaves >3% at 12m (Sep)', 'core leaves <=3% at 12m (Sep)')
out = (fw.groupby(['grp', 'trim_status']).ws.sum() / fw.groupby('grp').ws.sum()).rename('share_of_leaf_months_weighted').reset_index()
# mean monthly change, annualized, of the >3% group: all months vs months kept by the trim
for grp, s in fw.groupby('grp'):
    allm = (s.mm * s.ws).sum() / s.ws.sum()
    kept = s[s.trim_status.isin(['included', 'boundary'])]
    keptm = (kept.mm * kept.ws).sum() / kept.ws.sum()
    out = pd.concat([out, pd.DataFrame([dict(grp=grp, trim_status='avg m/m all months, annualized x12 (%)', share_of_leaf_months_weighted=12 * allm),
                                        dict(grp=grp, trim_status='avg m/m kept months only, annualized x12 (%)', share_of_leaf_months_weighted=12 * keptm)])])
out['share_of_leaf_months_weighted'] = out.share_of_leaf_months_weighted.round(4)
out.to_csv(os.path.join(OUT, 'D_trimmed_above3_fate.csv'), index=False)
print(rec[['month', 'measure', 'value', 'dallas_published']].to_string(index=False))
print(out.to_string(index=False))
print(mt[['ann_1m', 'ann_6m', 'r12m']].tail(14).round(2).to_string())
