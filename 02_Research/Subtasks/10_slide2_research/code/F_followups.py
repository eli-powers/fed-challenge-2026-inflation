"""F: coordinator follow-ups to Eli's Nov 15 notes on S2-E1..E9 (one-off; not audited).

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/F_followups.py"
Engine: 09_slide1_research/code/C_common.py (read-only); tags: 08_shock_tagging/proposed_tags.csv (tag_final).
Writes outputs/F_attrib_top_leaves.csv, F_group_rates_ts.csv, F_ex_hospital_breadth.csv, F_ex_hospital_ts.csv.
Definitions as Agent A (A_q2_attribution.py): s_i start-of-window weight share; r_i annualized leaf rate;
above-target (method a) = s_i * (r_i - 2). Breadth = share of weight with r > 3.
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
NAME = dict(zip(t.leaf, t.component_name))
HOSP = {184, 185, 186}
CORE = set(cc.LEAVES_CORE)
SUPER = cc.SCOPES['supercore']


def table(m, back, leaves=CORE):
    d = cc.unit_table('leaf', leaves, m, back)
    d['s'] = d.w / d.w.sum()
    d['tag'] = d.leaf.map(TAG)
    d['name'] = d.leaf.map(NAME)
    d['above_a'] = d.s * (d.r - 2)
    return d


# ---- 1. attribution: top leaves within each group (method a), 12m Sep/Oct and 3m Oct
rows = []
for m, back in (('2026-09', 12), ('2026-10', 12), ('2026-10', 3)):
    d = table(m, back)
    tot = d.above_a.sum()
    for g in ('energy', 'tariff', 'AI', 'untagged'):
        x = d[d.tag == g].sort_values('above_a', ascending=False)
        for rank, (_, r) in enumerate(x.iterrows(), 1):
            if rank <= 8 or rank > len(x) - 3:
                rows.append(dict(period=m, horizon=f'{back}m', group=g, rank=rank, leaf=r.leaf, name=r['name'], weight_pct=round(100 * r.s, 3),
                                 rate_pct=round(r.r, 2), above_target_a_pp=round(r.above_a, 4), share_of_total_above_pct=round(100 * r.above_a / tot, 2),
                                 group_total_share_pct=round(100 * x.above_a.sum() / tot, 2)))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'F_attrib_top_leaves.csv'), index=False)

# ---- 2. group weighted-mean rates over time (12m), and 3m
rows = []
months = [f'{y}-{mo:02d}' for y in range(2018, 2027) for mo in range(1, 13) if f'{y}-{mo:02d}' <= '2026-10']
for m in months:
    for back in (12, 3):
        d = table(m, back)
        rec = dict(month=m, horizon=f'{back}m')
        for g in ('energy', 'tariff', 'AI', 'untagged'):
            x = d[d.tag == g]
            rec[f'{g}_mean_rate'] = round((x.w * x.r).sum() / x.w.sum(), 3)
        x = d[(d.tag == 'untagged') & ~d.leaf.isin(HOSP)]
        rec['untagged_ex_hosp_mean_rate'] = round((x.w * x.r).sum() / x.w.sum(), 3)
        rec['core_leafsum_rate'] = round((d.s * d.r).sum(), 3)
        rows.append(rec)
G = pd.DataFrame(rows)
G.to_csv(os.path.join(OUT, 'F_group_rates_ts.csv'), index=False)

# ---- 3. breadth ex hospitals: core and supercore, 12m and 3m, monthly, with 2018-19 averages
rows = []
for m in months:
    for back in (12, 3):
        rec = dict(month=m, horizon=f'{back}m')
        for nm, ls in (('core', CORE), ('core_ex_hosp', CORE - HOSP), ('supercore', SUPER), ('supercore_ex_hosp', SUPER - HOSP)):
            d = cc.unit_table('leaf', ls, m, back)
            rec[nm] = round(100 * d.w[d.r > 3].sum() / d.w.sum(), 3)
        rows.append(rec)
X = pd.DataFrame(rows)
X.to_csv(os.path.join(OUT, 'F_ex_hospital_ts.csv'), index=False)
summ = []
for back in ('12m', '3m'):
    x = X[X.horizon == back].set_index('month')
    pre = x[x.index < '2020-01']
    for c in ('core', 'core_ex_hosp', 'supercore', 'supercore_ex_hosp'):
        summ.append(dict(measure=c, horizon=back, avg_2018_19=round(pre[c].mean(), 2), sep_2025=x.at['2025-09', c], feb_2026=x.at['2026-02', c],
                         sep_2026=x.at['2026-09', c], oct_2026_est=x.at['2026-10', c], peak=x[c].max(), peak_month=x[c].idxmax()))
pd.DataFrame(summ).to_csv(os.path.join(OUT, 'F_ex_hospital_breadth.csv'), index=False)
print(pd.DataFrame(summ).to_string(index=False))
print(G[G.month.isin(['2025-09', '2026-02', '2026-09', '2026-10']) & (G.horizon == '12m')].to_string(index=False))
print(G[G.month.isin(['2026-07', '2026-08', '2026-09', '2026-10']) & (G.horizon == '3m')].to_string(index=False))

# ---- 4. counterfactual-style rates: core leaf-sum excluding groups (12m and 3m), Sep 2025 .. Oct 2026
rows = []
for m in ('2025-09', '2026-02', '2026-06', '2026-09', '2026-10'):
    for back in (12, 3):
        d = table(m, back)
        rec = dict(month=m, horizon=f'{back}m', core_leafsum=round((d.s * d.r).sum(), 3))
        for nm, mask in (('ex_energy', d.tag != 'energy'), ('ex_energy_AI', ~d.tag.isin(['energy', 'AI'])),
                         ('ex_energy_AI_tariff', d.tag == 'untagged'), ('ex_hosp', ~d.leaf.isin(HOSP)),
                         ('ex_newspapers_143', d.leaf != 143)):
            x = d[mask]
            rec[nm] = round((x.w * x.r).sum() / x.w.sum(), 3)
        rows.append(rec)
C4 = pd.DataFrame(rows)
C4.to_csv(os.path.join(OUT, 'F_core_ex_groups.csv'), index=False)
print(C4.to_string(index=False))
