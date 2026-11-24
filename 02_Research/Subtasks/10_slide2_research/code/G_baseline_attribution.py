"""G: attribution of core PCE inflation by shock group, measured against each group's OWN pre-shock baseline (method d).

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/G_baseline_attribution.py"
Origin: Eli's side chat (Nov 15), an inline calc, scripted here with sensitivities. Not audited.

Definitions (149 core leaves; start-of-window weights; annualized k-month leaf rates; tags = tag_final):
  group level  excess_g = s_g x (R_g(t) - B_g),  R_g = weighted-mean group rate now, s_g = group weight share now,
               B_g = mean over the baseline window's months of the group's weighted-mean rate (same horizon k).
  leaf level   excess_g = sum_{i in g} s_i x (r_i(t) - b_i),  b_i = leaf i's mean rate over the baseline window.
  shares = excess_g / sum_g excess_g.  Total = core leaf-sum now minus the baseline-implied core rate (NOT core minus 2%).
Also reports method a (2% yardstick) for comparison: s_g x (R_g - 2).
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

for (m, b), want in {('2026-09', 12): 60.626, ('2026-10', 12): 54.038, ('2026-09', 3): 44.814, ('2026-10', 3): 45.467}.items():
    assert abs(cc.breadth('leaf', 'core', m, b)[0] - want) < 0.01

t = pd.read_csv(os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv'))
t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
TAG = dict(zip(t.leaf, t.tag_final))
G = ['energy', 'tariff', 'AI', 'untagged']
CORE = set(cc.LEAVES_CORE)
first_month = str(cc.bp.index.min())
print('BEA leaf data start:', first_month)


def table(m, back):
    d = cc.unit_table('leaf', CORE, m, back)
    d['s'] = d.w / d.w.sum()
    d['tag'] = d.leaf.map(TAG)
    return d


def months(a, b):
    out, (y, mo), (y2, mo2) = [], map(int, a.split('-')), map(int, b.split('-'))
    while (y, mo) <= (y2, mo2):
        out.append(f'{y}-{mo:02d}')
        mo += 1
        if mo == 13:
            y, mo = y + 1, 1
    return out


CACHE = {}


def tab(m, back):
    if (m, back) not in CACHE:
        CACHE[(m, back)] = table(m, back)
    return CACHE[(m, back)]


WINDOWS = {'2018-19': ('2018-01', '2019-12'), '2018 only': ('2018-01', '2018-12'), '2019 only': ('2019-01', '2019-12'), '2017-19': ('2017-01', '2019-12'), '2015-19': ('2015-01', '2019-12'),
           '2016-19': ('2016-01', '2019-12'), 'pre-shock Sep 2025 (single month)': ('2025-09', '2025-09'),
           'pre-shock Feb 2026 (single month)': ('2026-02', '2026-02')}
rows = []
for per in ('2026-09', '2026-10'):
    for back in (12, 3):
        d = tab(per, back)
        S = (d.s * d.r).sum()
        # method a for reference
        a = {g: (d.s * (d.r - 2))[d.tag == g].sum() for g in G}
        ta = sum(a.values())
        for g in G:
            rows.append(dict(period=per, horizon=f'{back}m', method='a: 2% yardstick', baseline='2.0 (target)', level='group', group=g,
                             weight_share=round(d.s[d.tag == g].sum(), 4), rate_now=round((d.s * d.r)[d.tag == g].sum() / d.s[d.tag == g].sum(), 3),
                             baseline_rate=2.0, excess_pp=round(a[g], 4), share_pct=round(100 * a[g] / ta, 1), total_pp=round(ta, 4), core_leafsum=round(S, 3)))
        for wn, (w0, w1) in WINDOWS.items():
            ms = months(w0, w1)
            if ms[0] < first_month[:7] or any(cc.P(m) - back < cc.bp.index.min() for m in ms):
                continue
            # group-level baselines
            B = {g: [] for g in G}
            leafb = {}
            for m in ms:
                x = tab(m, back)
                for g in G:
                    y = x[x.tag == g]
                    B[g].append((y.w * y.r).sum() / y.w.sum())
                for lf, r in zip(x.leaf, x.r):
                    leafb.setdefault(lf, []).append(r)
            Bg = {g: sum(v) / len(v) for g, v in B.items()}
            bi = {lf: sum(v) / len(v) for lf, v in leafb.items()}
            for level in ('group', 'leaf'):
                ex = {}
                for g in G:
                    y = d[d.tag == g]
                    if level == 'group':
                        ex[g] = y.s.sum() * ((y.s * y.r).sum() / y.s.sum() - Bg[g])
                    else:
                        ex[g] = (y.s * (y.r - y.leaf.map(bi))).sum()
                tot = sum(ex.values())
                for g in G:
                    y = d[d.tag == g]
                    eff = Bg[g] if level == 'group' else (y.s * y.leaf.map(bi)).sum() / y.s.sum()   # leaf: current-weighted mean of leaf baselines (Codex R1-F04)
                    rows.append(dict(period=per, horizon=f'{back}m', method='d: excess over own baseline', baseline=wn, level=level, group=g,
                                     weight_share=round(y.s.sum(), 4), rate_now=round((y.s * y.r).sum() / y.s.sum(), 3),
                                     baseline_rate=round(eff, 3), group_baseline_rate=round(Bg[g], 3), excess_pp=round(ex[g], 4), share_pct=round(100 * ex[g] / tot, 1),
                                     total_pp=round(tot, 4), core_leafsum=round(S, 3)))
# tag sensitivity: strict 5% energy cutoff (energy_main >= 0.05), other tags unchanged; 12m, 2018-19 baseline, group level
TAG5 = {lf: ('energy' if (TAG[lf] == 'energy' and e >= 0.05) else ('untagged' if TAG[lf] == 'energy' else TAG[lf]))
        for lf, e in zip(t.leaf, t.energy_main)}
for per in ('2026-09', '2026-10'):
    d = tab(per, 12).copy()
    d['tag'] = d.leaf.map(TAG5)
    B = {g: [] for g in G}
    for m in months('2018-01', '2019-12'):
        x = tab(m, 12).copy()
        x['tag'] = x.leaf.map(TAG5)
        for g in G:
            y = x[x.tag == g]
            B[g].append((y.w * y.r).sum() / y.w.sum())
    ex = {g: d.s[d.tag == g].sum() * ((d.s * d.r)[d.tag == g].sum() / d.s[d.tag == g].sum() - sum(B[g]) / len(B[g])) for g in G}
    tot = sum(ex.values())
    for g in G:
        rows.append(dict(period=per, horizon='12m', method='d: excess over own baseline [tags: strict 5% energy]', baseline='2018-19', level='group', group=g,
                         weight_share=round(d.s[d.tag == g].sum(), 4), rate_now=None, baseline_rate=round(sum(B[g]) / len(B[g]), 3),
                         excess_pp=round(ex[g], 4), share_pct=round(100 * ex[g] / tot, 1), total_pp=round(tot, 4), core_leafsum=None))
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, 'G_baseline_attribution.csv'), index=False)
pv = R.pivot_table(index=['period', 'horizon', 'method', 'baseline', 'level'], columns='group', values='share_pct').reindex(columns=G)
tot = R.groupby(['period', 'horizon', 'method', 'baseline', 'level']).total_pp.first()
pv['total_pp'] = tot
pv.to_csv(os.path.join(OUT, 'G_baseline_attribution_summary.csv'))
pd.set_option('display.width', 200)
print(pv.to_string())
print(R[(R.method.str.startswith('d')) & (R.baseline == '2018-19') & (R.level == 'group') & (R.horizon == '12m')][['period', 'group', 'weight_share', 'rate_now', 'baseline_rate', 'excess_pp']].to_string(index=False))

# ---- path: each group's excess over its own 2018-19 12m rate (pp of core), at pre-shock and current months
B12 = {g: [] for g in G}
for m in months('2018-01', '2019-12'):
    x = tab(m, 12)
    for g in G:
        y = x[x.tag == g]
        B12[g].append((y.w * y.r).sum() / y.w.sum())
B12 = {g: sum(v) / len(v) for g, v in B12.items()}
path = []
for m in ('2025-03', '2025-09', '2026-02', '2026-06', '2026-09', '2026-10'):
    d = tab(m, 12)
    rec = dict(month=m, status='estimate' if m == '2026-10' else 'BEA published')
    for g in G:
        y = d[d.tag == g]
        rec[f'{g}_rate'] = round((y.s * y.r).sum() / y.s.sum(), 3)
        rec[f'{g}_excess_pp'] = round(y.s.sum() * ((y.s * y.r).sum() / y.s.sum() - B12[g]), 4)
    rec['total_excess_pp'] = round(sum(rec[f'{g}_excess_pp'] for g in G), 4)
    path.append(rec)
P_ = pd.DataFrame(path)
P_.to_csv(os.path.join(OUT, 'G_excess_path.csv'), index=False)
print({g: round(v, 3) for g, v in B12.items()})
print(P_[['month'] + [f'{g}_excess_pp' for g in G] + ['total_excess_pp']].to_string(index=False))
