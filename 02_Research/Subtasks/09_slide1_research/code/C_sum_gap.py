"""Brief C item 4: split the gap between the component-contribution sum and the published core PCE rate.

Run from the project root:  python3 -I "02_Research/Subtasks/09_slide1_research/code/C_sum_gap.py"
Writes outputs/C_sum_gap.csv (and prints a reconciliation to the workbook numbers).

Notation (core set C; weights rescaled to sum to one over C; window = k months from t0 to t1; k = 3 or 12)
  p_i(t)       BEA price index of unit i (October 2026 = estimate: Sep index x (1 + build m/m))
  s_i(t)       nominal spending share of unit i in month t over C   (U20405)
  w_i          = s_i(t0)  start-of-window weights
  g_i          = p_i(t1)/p_i(t0) - 1                         window growth of unit i
  pi_i(t)      = p_i(t)/p_i(t-1) - 1                         monthly growth of unit i
  ann(x)       = (1 + x)^(12/k) - 1
  R_pub        published (Sep) or estimated (Oct) core PCE rate, annualized k-month rate of the aggregate index

  S_ann   = sum_i w_i * ann(g_i)                      the workbook's "sum of component contributions" (each rate annualized, then weighted)
  A_fix   = ann( sum_i w_i * g_i )                    fixed start-of-window shares, aggregate annualized
  A_chain = ann( prod_t (1 + L_t) - 1 ),  L_t = sum_i s_i(t-1) * pi_i(t)       monthly-updated shares (chained Laspeyres)
  A_fish  = ann( prod_t F_t - 1 ),  F_t = sqrt( (1 + L_t) * (1 + Pa_t) ),
            1 + Pa_t = 1 / sum_i s_i(t) / (1 + pi_i(t))   Fisher = geometric mean of Laspeyres and Paasche, chained monthly
            (October 2026: no October shares exist, so F_Oct = 1 + L_Oct; the Paasche step is not measurable)

  Gap  G = S_ann - R_pub  =  (a) + (b) + (c)
  (a) annualization convexity      = S_ann   - A_fix
  (b) fixed-share vs chained index = A_fix   - A_fish        = (b1) A_fix - A_chain   [weights frozen at t0 vs updated monthly]
                                                              + (b2) A_chain - A_fish  [Laspeyres vs Fisher within each month]
  (c) residual                     = A_fish  - R_pub         [covered set (BEA lines 145 and 333, 0.3% of PCE, are not priced and
                                                              are rescaled out), BEA's actual aggregation details, rounding]
All in percentage points. At k = 12, ann(x) = x so (a) = 0 by construction.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import *  # noqa: E402,F403

summ = pd.read_csv(OCT_SUMMARY).set_index('measure')
core = summ.loc['core']


def published(period, back):
    """Sep: BEA core PCE (U20404 line 374) annualized k-month rate. Oct: BEA Sep index extended by the build's October core m/m."""
    t = P(period)
    if t <= SEP:
        return 100 * ((bp.at[t, 374] / bp.at[t - back, 374]) ** (12 / back) - 1)
    i_oct = bp.at[SEP, 374] * (1 + core.estimate_mm / 100)
    return 100 * ((i_oct / bp.at[t - back, 374]) ** (12 / back) - 1)


def decompose(gran, period, back):
    t1 = P(period)
    t0 = t1 - back
    u = units(gran, SCOPES['core'])

    def shares(m):
        v = np.array([nominal_weight(l, lf, m, gran) for l, lf in u], dtype=float)
        return v / v.sum()

    def lvl(m):
        return np.array([index_level(l, m, gran) for l, lf in u], dtype=float)

    w0 = shares(t0)
    g = lvl(t1) / lvl(t0) - 1
    ann = lambda x: (1 + x) ** (12 / back) - 1
    S = (w0 * ann(g)).sum()
    A_fix = ann((w0 * g).sum())
    chain = 1.0
    fish = 1.0
    for m in range(1, back + 1):
        t = t0 + m
        pi = lvl(t) / lvl(t - 1) - 1
        L = (shares(t - 1) * pi).sum()
        chain *= 1 + L
        if t <= SEP:
            pa = 1 / (shares(t) / (1 + pi)).sum() - 1
            fish *= np.sqrt((1 + L) * (1 + pa))
        else:
            fish *= 1 + L
    A_chain = chain ** (12 / back) - 1
    A_fish = fish ** (12 / back) - 1
    R = published(period, back) / 100
    out = dict(S_ann=S, A_fix=A_fix, A_chain=A_chain, A_fish=A_fish, R_pub=R)
    return {k: 100 * v for k, v in out.items()}, len(u)


rows = []
for period in ('2026-09', '2026-10'):
    for back, hz in ((3, '3m_ann'), (12, '12m')):
        for gran in ('sub', 'leaf'):
            r, n = decompose(gran, period, back)
            G = r['S_ann'] - r['R_pub']
            a = r['S_ann'] - r['A_fix']
            b1 = r['A_fix'] - r['A_chain']
            b2 = r['A_chain'] - r['A_fish']
            c = r['A_fish'] - r['R_pub']
            assert abs(G - (a + b1 + b2 + c)) < 1e-9
            rows.append(dict(period=period, status='BEA published' if period == '2026-09' else 'estimate', horizon=hz,
                             method='sub-line' if gran == 'sub' else 'leaf', role='primary' if gran == 'sub' else 'robustness', n_units=n,
                             published_or_est_rate=r['R_pub'], sum_of_contributions_S_ann=r['S_ann'], gap_total_G=G,
                             a_annualization_convexity=a, b_fixed_share_vs_chained_fisher=b1 + b2, b1_weights_frozen_vs_monthly_updated=b1,
                             b2_laspeyres_vs_fisher_monthly=b2, c_residual=c,
                             A_fixed_share_aggregate=r['A_fix'], A_chained_laspeyres=r['A_chain'], A_chained_fisher=r['A_fish']))
D = pd.DataFrame(rows)
D['gap_if_aggregate_annualized_pipeline_fix3m_basis'] = D.b_fixed_share_vs_chained_fisher + D.c_residual
D['weight_basis'] = 'start-of-window nominal shares (U20405) of the base month, rescaled over the covered core set'
D['vintage'] = 'BEA U20404/U20405 2026-11-10 (data through Sep 2026); October = estimate (audited build, 04_oct_pce_build)'
D['formula_note'] = 'see docstring of C_sum_gap.py and notes_C.md; Oct Fisher Paasche step not measurable (no Oct shares): F_Oct = Laspeyres'

# ---- reconcile to the numbers already in the workbook
W = pd.read_csv(W_FILE)
g = W[W.w_c != 0]
oct3, oct12 = g.c3_c.sum(), g.c12_c.sum()
got = D[(D.period == '2026-10') & (D.method == 'sub-line')].set_index('horizon')
print('Oct W-file sums: 3m', round(oct3, 4), '12m', round(oct12, 4), '| mine S_ann', round(got.at['3m_ann', 'sum_of_contributions_S_ann'], 4), round(got.at['12m', 'sum_of_contributions_S_ann'], 4))
print('Oct published/estimated (summary): 3m', core.rate_3m_ann, '12m', core.rate_12m, '| mine', round(got.at['3m_ann', 'published_or_est_rate'], 4), round(got.at['12m', 'published_or_est_rate'], 4))
comp = pd.read_csv(os.path.join(ROOT, '03_Data/pipelines/Price indexes/PCE/processed/components.csv'))
pc = comp[comp.index_name == 'PCE core']
print('pipeline PCE core rows', len(pc), 'sum contrib_3m_ann_calc (fix_3m, workbook Sep basis)', round(pc.contrib_3m_ann_calc.sum(), 4),
      '12m', round(pc.contrib_12m_calc.sum(), 4))
sp = D[(D.period == '2026-09') & (D.method == 'leaf')].set_index('horizon')
print('Sep leaf: mine A_fix 3m', round(sp.at['3m_ann', 'A_fixed_share_aggregate'], 4), 'S_ann 3m', round(sp.at['3m_ann', 'sum_of_contributions_S_ann'], 4),
      '12m S', round(sp.at['12m', 'sum_of_contributions_S_ann'], 4))

# basis rows: which of the two sums is the "0.130" and the "0.23"
basis = [dict(period='2026-09', basis='pipeline workbook Sep sum (components.csv contrib_3m_ann_calc after fix_3m; 149 leaves)', horizon='3m_ann',
              sum_value=pc.contrib_3m_ann_calc.sum(), published=published('2026-09', 3)),
         dict(period='2026-09', basis='pipeline workbook Sep sum (components.csv contrib_12m_calc; 149 leaves)', horizon='12m',
              sum_value=pc.contrib_12m_calc.sum(), published=published('2026-09', 12)),
         dict(period='2026-10', basis='October tab sum (W_pce_oct_tab_lines.csv c3_c, individually annualized; 184 sub-lines)', horizon='3m_ann',
              sum_value=oct3, published=core.rate_3m_ann),
         dict(period='2026-10', basis='October tab sum (W_pce_oct_tab_lines.csv c12_c; 184 sub-lines)', horizon='12m', sum_value=oct12, published=core.rate_12m)]
B = pd.DataFrame(basis)
B['gap_pp'] = B.sum_value - B.published
print(B.round(4).to_string())
B.round(4).to_csv(os.path.join(OUTDIR, 'C_sum_gap_basis_reconciliation.csv'), index=False)
num = [c for c in D.columns if D[c].dtype == float]
D[num] = D[num].round(4)
D.to_csv(os.path.join(OUTDIR, 'C_sum_gap.csv'), index=False)
pd.set_option('display.width', 250)
print(D[['period', 'horizon', 'method', 'published_or_est_rate', 'sum_of_contributions_S_ann', 'gap_total_G', 'a_annualization_convexity',
         'b_fixed_share_vs_chained_fisher', 'b1_weights_frozen_vs_monthly_updated', 'b2_laspeyres_vs_fisher_monthly', 'c_residual']].to_string())

# ---- monthly residual: chained Fisher over the covered core set vs BEA's published core m/m (is the Sep residual typical?)
u = units('sub', SCOPES['core'])
mrows = []
for t in pd.period_range('2023-10', '2026-09', freq='M'):
    def sh(m):
        v = np.array([nominal_weight(l, lf, m, 'sub') for l, lf in u], dtype=float)
        return v / v.sum()
    lv = lambda m: np.array([index_level(l, m, 'sub') for l, lf in u], dtype=float)
    pi = lv(t) / lv(t - 1) - 1
    Lt = (sh(t - 1) * pi).sum()
    Pa = 1 / (sh(t) / (1 + pi)).sum() - 1
    F = np.sqrt((1 + Lt) * (1 + Pa)) - 1
    pub = bp.at[t, 374] / bp.at[t - 1, 374] - 1
    mrows.append(dict(month=str(t), laspeyres_mm_pct=100 * Lt, fisher_covered_mm_pct=100 * F, published_core_mm_pct=100 * pub,
                      fisher_minus_published_pp=100 * (F - pub), laspeyres_minus_fisher_pp=100 * (Lt - F)))
M = pd.DataFrame(mrows)
print('monthly residual (Fisher covered - published), pp m/m, Oct 2023-Sep 2026: mean', round(M.fisher_minus_published_pp.mean(), 4),
      'sd', round(M.fisher_minus_published_pp.std(), 4), 'mean Lasp-Fisher', round(M.laspeyres_minus_fisher_pp.mean(), 4),
      'last 3', M.fisher_minus_published_pp.tail(3).round(4).tolist())
M.round(5).to_csv(os.path.join(OUTDIR, 'C_sum_gap_monthly_residual.csv'), index=False)
