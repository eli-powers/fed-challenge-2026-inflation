"""A Q2: Bowman-style attribution of above-target core PCE (core minus 2%) to energy / tariff / AI / untagged groups.

Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/A_q2_attribution.py   (from the project root)

Definitions (149 core leaves i; k = 3 or 12 months; window t0 = t1 - k)
  w_i   = nominal spending (U20405) of leaf i in the BASE month t0 (start-of-window)
  s_i   = w_i / sum_core w                      leaf weight share
  r_i   = 100*((I_i(t1)/I_i(t0))**(12/k) - 1)   annualized k-month leaf rate (%, BEFORE any cutoff), I = BEA leaf index; Oct = estimate
  S     = sum_i s_i r_i                          sum of leaf contributions (pp)
  group g: weight share s_g = sum_{i in g} s_i ; contribution C_g = sum_{i in g} s_i r_i  (pp; sum_g C_g = S)
  Published/estimated core rate R (BEA core PCE line 374; Oct: Sep index x (1 + build m/m)); residual = R - S (not allocated).
Methods for above-target (T = 2.0):
  a  (central)  A_g = C_g - s_g*T                      each group "owes" T on its own weight. sum_g A_g = S - T
  b  (excess)   A_g = sum_{i in g, r_i>T} s_i (r_i - T)  only leaves running above target count (below-target leaves do not offset). Sum = excess total.
  c  (untagged) A_g = C_g for tagged groups; A_untagged = C_untagged - T  (the whole 2% is charged to the untagged group)
  a_scaled      method a with each A_g multiplied by (R - T)/(S - T) so the groups sum to published-minus-2 (puts the residual pro rata)
share_of_above_target = A_g / sum_g A_g (shares can be negative or above 100% when a group's contribution is below its target-owed amount).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *

T = 2.0
check_mapping(); slide1_checks()
summ = pd.read_csv(cc.OCT_SUMMARY).set_index('measure').loc['core']


def published(period, back):
    t = P(period)
    if t <= cc.SEP:
        return 100 * ((bp.at[t, 374] / bp.at[t - back, 374]) ** (12 / back) - 1)
    i_oct = bp.at[cc.SEP, 374] * (1 + summ.estimate_mm / 100)
    return 100 * ((i_oct / bp.at[t - back, 374]) ** (12 / back) - 1)


rows, leafrows = [], []
for period, status in (('2026-09', 'BEA published'), ('2026-10', 'UMD estimate (est.)')):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        d = leaf_table(period, back)
        d['c'] = d.ws * d.r
        d['excess'] = np.where(d.r > T, d.ws * (d.r - T), 0.0)
        R = published(period, back)
        S = d.c.sum()
        assert abs(S - 100 * 0 - S) < 1e-12
        resid = R - S
        # leaf-level
        for _, x in d.iterrows():
            leafrows.append(dict(period=period, horizon=hz, leaf=int(x.leaf), tag=x.tag, weight_share_pct=round(100 * x.ws, 4),
                                 rate_pct=round(x.r, 4), contribution_pp=round(x.c, 5), owed_at_2pct_pp=round(x.ws * T, 5),
                                 above_target_a_pp=round(x.c - x.ws * T, 5), excess_over_target_b_pp=round(x.excess, 5), over_3pct=bool(x.over3)))
        g = d.groupby('tag').agg(s=('ws', 'sum'), C=('c', 'sum'), X=('excess', 'sum'))
        g = g.reindex(GROUPS)
        A = {'a': g.C - g.s * T, 'b': g.X, 'c': g.C.copy()}
        A['c']['untagged'] = g.C['untagged'] - T
        scale = (R - T) / (S - T)
        A['a_scaled'] = A['a'] * scale
        for m, ser in A.items():
            tot = ser.sum()
            for tg in GROUPS:
                rows.append(dict(period=period, status=status, horizon=hz, method=m, group=tg,
                                 weight_share=round(g.s[tg], 5), group_rate_pct=round(g.C[tg] / g.s[tg], 4), contribution_pp=round(g.C[tg], 4),
                                 above_target_pp=round(ser[tg], 4), share_of_above_target=round(ser[tg] / tot, 4),
                                 sum_leaf_contributions_S=round(S, 4), published_or_est_core_rate_R=round(R, 4),
                                 residual_R_minus_S=round(resid, 4), total_above_target_allocated=round(tot, 4),
                                 vintage=VINTAGE))
        print(period, hz, f'S={S:.4f} R={R:.4f} resid={resid:.4f} | weights', {k: round(v, 3) for k, v in g.s.items()})
        for m, ser in A.items():
            print('   ', m, {k: f'{v:.3f} ({100*v/ser.sum():.1f}%)' for k, v in ser.items()}, 'tot', round(ser.sum(), 3))

att = pd.DataFrame(rows)
att.to_csv(os.path.join(OUT, 'A_q2_attribution.csv'), index=False)
pd.DataFrame(leafrows).to_csv(os.path.join(OUT, 'A_q2_leaf_contrib.csv'), index=False)

# reconciliation file check: sum of leaf contributions equals C_sum_gap S_ann (leaf rows)
sg = pd.read_csv(os.path.join(ROOT, '02_Research/Subtasks/09_slide1_research/outputs/C_sum_gap.csv'))
sg = sg[sg.method == 'leaf']
for _, r in sg.iterrows():
    hz = r.horizon
    m = att[(att.period == r.period) & (att.horizon == hz) & (att.method == 'a') & (att.group == 'energy')].iloc[0]
    assert abs(m.sum_leaf_contributions_S - r.sum_of_contributions_S_ann) < 5e-4, (r.period, hz, m.sum_leaf_contributions_S, r.sum_of_contributions_S_ann)
    assert abs(m.published_or_est_core_rate_R - r.published_or_est_rate) < 5e-4, (r.period, hz, m.published_or_est_core_rate_R, r.published_or_est_rate)
print('S and R match 09_slide1 C_sum_gap.csv leaf rows')
