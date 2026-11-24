"""Brief C items 1-3: breadth tables, time series, carried-forward attribution, leaf roll-up check.

Run from the project root:  python3 -I "02_Research/Subtasks/09_slide1_research/code/C_breadth.py"
Writes (in 09_slide1_research/outputs/): C_breadth.csv, C_breadth_ts.csv, C_carried_forward.csv,
C_carried_forward_lines.csv, C_leaf_rollup_check.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from C_common import *  # noqa: E402,F403
from C_common import _SUBS_BY_LEAF  # noqa: E402

VINTAGE = 'BEA U20404/U20405 vintage 2026-11-10 (data through Sep 2026)'
OCT_NOTE = ('estimate: BEA Sep index extended by the audited October build m/m (D_build_2026-10_lines.csv); '
            'BEA publishes October PCE on Nov 25')

# ---------------------------------------------------------------- 0. reproduce report 07 numbers (checks)
EXPECT = {('sub', 12, '2026-09'): 57.71, ('sub', 12, '2026-10'): 51.1, ('sub', 3, '2026-09'): 43.67, ('sub', 3, '2026-10'): 43.8,
          ('leaf', 12, '2026-09'): 60.63, ('leaf', 12, '2026-10'): 54.0, ('leaf', 3, '2026-09'): 44.81, ('leaf', 3, '2026-10'): 45.5}
for (g, back, m), want in EXPECT.items():
    got = breadth(g, 'core', m, back)[0]
    assert abs(got - want) < 0.06, (g, back, m, got, want)
print('report 07 numbers reproduced (sub-line and leaf, 3m and 12m, Sep and Oct)')

# ---------------------------------------------------------------- 1. C_breadth.csv
rows = []


def add(period, scope, horizon, method, role, basis, n, val, wbasis, note='', extra=None):
    rows.append(dict(period=period, status='BEA published' if period == '2026-09' else 'estimate',
                     scope=scope, horizon=horizon, method=method, role=role, metric=basis, n_units=n,
                     value_pct=round(float(val), 3), weight_basis=wbasis,
                     vintage=VINTAGE, note=(note + ('; ' + OCT_NOTE if period == '2026-10' else '')).strip('; ')))


NUNIT = {}
for period in ('2026-09', '2026-10'):
    for scope in ('core', 'headline', 'supercore'):
        for back, hz in ((3, '3m_ann'), (12, '12m')):
            for gran, role in (('sub', 'primary'), ('leaf', 'robustness')):
                b, n = breadth(gran, scope, period, back)
                wb = f'start-of-window weights: nominal shares of {P(period) - back} (base month of the {back}m window)'
                note = ''
                if period == '2026-10' and gran == 'leaf':
                    note = ('leaf October rates use a fixed-share (Sep within-leaf shares) roll-up of sub-line m/m for the 13 split '
                            'leaves; approximate, error bound in C_leaf_rollup_check.csv')
                if scope == 'supercore':
                    note = (note + '; supercore = services ex energy and housing, within core; units: leaves with line>=150 excl 153-164, 169-171').strip('; ')
                if scope == 'headline':
                    note = (note + '; headline units = all 177 BEA leaves in the Dallas/BEA basket (lines 145 and 333 excluded) or their sub-lines').strip('; ')
                add(period, scope, hz, 'sub-line' if gran == 'sub' else 'leaf', role, 'share of spending weight with rate > 3%', n, b, wb, note)
    # sensitivity: 3m breadth on 12m-ago weights (the October tab's other label)
    for gran in ('sub', 'leaf'):
        d = unit_table(gran, SCOPES['core'], period, 3)
        d['w12'] = [nominal_weight(l, lf, P(period) - 12, gran) for l, lf in zip(d.line, d.leaf)]
        v = 100 * d.w12[d.r > 3].sum() / d.w12.sum()
        add(period, 'core', '3m_ann', 'sub-line' if gran == 'sub' else 'leaf', 'sensitivity', 'share of spending weight with rate > 3%', len(d), v,
            f'sensitivity: 12m-ago weights (shares of {P(period) - 12}) applied to the 3m rate',
            'the October tab shows both labels (43.83 vs 43.75); primary is start-of-window weights')

# Waller cross-check: COUNT of core services items with 12m rate above 3% (not weight). Same cutoff, 12m, Sep and Oct.
WALLER = ('Waller (Nov 10): "More than 70 percent of the components of core PCE service prices saw 12-month increases above 3 percent in September." '
          'Count basis; core services = services leaves (line>=150) inside our core set (energy services 169-171 are not core), incl. housing')
for period in ('2026-09', '2026-10'):
    for gran in ('leaf', 'sub'):
        c, k, n = count_share(gran, 'core_services', period, 12)
        add(period, 'core_services', '12m', 'sub-line' if gran == 'sub' else 'leaf', 'Waller cross-check', f'share of items (count) with rate > 3% [{k} of {n}]', n, c,
            'none (item count, unweighted)', WALLER)
        b, n = breadth(gran, 'core_services', period, 12)
        add(period, 'core_services', '12m', 'sub-line' if gran == 'sub' else 'leaf', 'Waller cross-check', 'share of spending weight with rate > 3%', n, b,
            f'start-of-window weights: nominal shares of {P(period) - 12}', 'same set, weighted, for comparison with the count')
    # count variants: ex housing leaves, and market-based-ish exclusion of the largest imputed lines is NOT attempted (no flag in the data)
    c, k, n = count_share('leaf', 'supercore', period, 12)
    add(period, 'supercore', '12m', 'leaf', 'Waller cross-check', f'share of items (count) with rate > 3% [{k} of {n}]', n, c, 'none (item count, unweighted)',
        'services ex energy and housing, count basis')
    for gran in ('leaf', 'sub'):
        c, k, n = count_share(gran, 'core', period, 12)
        add(period, 'core', '12m', 'sub-line' if gran == 'sub' else 'leaf', 'count comparison', f'share of items (count) with rate > 3% [{k} of {n}]', n, c,
            'none (item count, unweighted)', 'all core items, count basis (goods + services)')

out = pd.DataFrame(rows)
out.to_csv(os.path.join(OUTDIR, 'C_breadth.csv'), index=False)
print(out[out.role.isin(['primary', 'robustness'])].pivot_table(index=['scope', 'horizon', 'method'], columns='period', values='value_pct'))
print(out[out.role.isin(['Waller cross-check', 'count comparison'])][['period', 'scope', 'method', 'metric', 'value_pct']].to_string())

# ---------------------------------------------------------------- 2. time series
months = [str(p) for p in pd.period_range('2018-01', '2026-09', freq='M')] + ['2026-10']
ts = []
for m in months:
    r = dict(month=m, status='BEA published' if m <= '2026-09' else 'estimate')
    for gran, tag in (('sub', 'subline'), ('leaf', 'leaf')):
        for back, hz in ((3, '3m_ann'), (12, '12m')):
            r[f'core_breadth_{hz}_{tag}'] = round(breadth(gran, 'core', m, back)[0], 3)
    ts.append(r)
ts = pd.DataFrame(ts)
hist = ts[(ts.month >= '2018-01') & (ts.month <= '2019-12')]
ref = {'month': 'avg_2018_2019', 'status': 'reference: simple average of the 24 monthly values Jan 2018 - Dec 2019'}
for c in ts.columns[2:]:
    ref[c] = round(hist[c].mean(), 3)
ts = pd.concat([ts, pd.DataFrame([ref])], ignore_index=True)
ts['weight_basis'] = 'start-of-window weights (shares of month t-3 for 3m, t-12 for 12m)'
ts['note'] = 'sub-line = 184 core pricing lines, current BEA (Sep 30, 2026) source table applied to all history; leaf = 149 core leaves'
ts.to_csv(os.path.join(OUTDIR, 'C_breadth_ts.csv'), index=False)
pub = ts[ts.month.str.match(r'^\d{4}-\d{2}$') & (ts.month <= '2026-09')]
for c in ('core_breadth_3m_ann_subline', 'core_breadth_12m_subline'):
    s = pub.set_index('month')[c]
    print(c, 'avg 18-19', ref[c], 'max', s.idxmax(), s.max(), 'min', s.idxmin(), s.min(), 'Sep26', s['2026-09'], 'last 6', s.tail(6).round(1).to_dict())

# ---------------------------------------------------------------- 3. carried-forward attribution (sub-line, core, 12m)
dS = unit_table('sub', SCOPES['core'], '2026-09', 12)
dO = unit_table('sub', SCOPES['core'], '2026-10', 12)
m = dS.merge(dO, on=['line', 'leaf'], suffixes=('_S', '_O'))
assert len(m) == len(dS) == len(dO) == 184
m['tier'] = m.line.map(OCT_TIER)
m['name'] = m.line.map(lambda l: eng.names[bl(l)] if l == 157 else eng.names[l])
WS, WO = m.w_S.sum(), m.w_O.sum()
m['aS'] = m.w_S / WS * 100 * (m.r_S > 3)          # contribution to Sep breadth (pp)
m['aO'] = m.w_O / WO * 100 * (m.r_O > 3)          # contribution to Oct breadth (pp)
m['d_total'] = m.aO - m.aS
m['d_flip'] = m.w_O / WO * 100 * ((m.r_O > 3).astype(int) - (m.r_S > 3).astype(int))      # rate crossings, Oct weights
m['d_weight'] = (m.w_O / WO - m.w_S / WS) * 100 * (m.r_S > 3)                               # weight shift, Sep status
assert abs(m.d_total.sum() - (m.d_flip.sum() + m.d_weight.sum())) < 1e-9
tot = m.d_total.sum()
print('Sep', m.aS.sum(), 'Oct', m.aO.sum(), 'change', tot)
rows = []
for tier, g in list(m.groupby('tier')) + [('ALL', m)]:
    rows.append(dict(tier=tier, n_lines=len(g), core_weight_share_oct_window_pct=round(100 * g.w_O.sum() / WO, 2),
                     core_weight_share_sep_window_pct=round(100 * g.w_S.sum() / WS, 2),
                     breadth_sep_contribution_pp=round(g.aS.sum(), 3), breadth_oct_contribution_pp=round(g.aO.sum(), 3),
                     change_total_pp=round(g.d_total.sum(), 3), of_which_rate_crossings_pp=round(g.d_flip.sum(), 3),
                     of_which_weight_shift_pp=round(g.d_weight.sum(), 3),
                     n_lines_crossing_3pct=int(((g.r_S > 3) != (g.r_O > 3)).sum()),
                     n_down_crossings=int(((g.r_S > 3) & (g.r_O <= 3)).sum()), n_up_crossings=int(((g.r_S <= 3) & (g.r_O > 3)).sum())))
cf = pd.DataFrame(rows)
cf['share_of_total_change_pct'] = (100 * cf.change_total_pp / round(tot, 3)).round(1)
# counterfactuals for the assumed tier
asm = m.tier == 'assumed'
b_oct_all = m.aO.sum()
b_if_assumed_kept_sep_status = m.aO[~asm].sum() + (m.w_O / WO * 100 * (m.r_S > 3))[asm].sum()
w_na_S, w_na_O = m.w_S[~asm].sum(), m.w_O[~asm].sum()
b_ex_S = 100 * m.w_S[~asm][m.r_S > 3].sum() / w_na_S
b_ex_O = 100 * m.w_O[~asm][m.r_O > 3].sum() / w_na_O
cf['note'] = ''
cf.loc[cf.tier == 'ALL', 'note'] = (f'Sep 12m {m.aS.sum():.3f} -> Oct 12m {m.aO.sum():.3f} (sub-line, core, start-of-window weights: Sep 2025 shares for Sep, Oct 2025 shares for Oct). '
                                    f'Oct breadth if the assumed lines had kept their Sep side of 3% (at Oct weights): {b_if_assumed_kept_sep_status:.3f}. '
                                    f'Ex-assumed breadth (renormalised): Sep {b_ex_S:.3f}, Oct {b_ex_O:.3f}, change {b_ex_O - b_ex_S:.3f}')
cf['vintage'] = VINTAGE + '; October = estimate'
cf.to_csv(os.path.join(OUTDIR, 'C_carried_forward.csv'), index=False)
print(cf.to_string())
print('counterfactual Oct if assumed kept Sep status', b_if_assumed_kept_sep_status, '| ex-assumed Sep', b_ex_S, 'Oct', b_ex_O)

lines_out = m[(m.r_S > 3) != (m.r_O > 3)].copy()
lines_out['direction'] = np.where(lines_out.r_O > 3, 'up through 3%', 'down through 3%')
lines_out = lines_out.assign(weight_oct_window_pct=(100 * lines_out.w_O / WO).round(3), weight_sep_window_pct=(100 * lines_out.w_S / WS).round(3),
                             r12_sep=lines_out.r_S.round(3), r12_oct_est=lines_out.r_O.round(3), change_pp=lines_out.d_total.round(3))
lines_out = lines_out.sort_values('d_total')[['line', 'name', 'leaf', 'tier', 'weight_sep_window_pct', 'weight_oct_window_pct',
                                               'r12_sep', 'r12_oct_est', 'direction', 'change_pp']]
lines_out.to_csv(os.path.join(OUTDIR, 'C_carried_forward_lines.csv'), index=False)
print(lines_out.to_string())

# ---------------------------------------------------------------- 4. leaf roll-up approximation check
# How well does a fixed-share (previous-month within-leaf shares) roll-up of BEA sub-line m/m reproduce BEA's own leaf m/m?
split_leaves = sorted(lf for lf in LEAVES_CORE if len([1 for l, s in specs.items() if s['leaf'] == lf]) > 1 and lf not in (TENANT, NPISH))
errs = []
win = [p for p in pd.period_range('2023-10', '2026-09', freq='M')]
for lf in split_leaves:
    subs = _SUBS_BY_LEAF[lf]
    for t in win:
        sh = np.array([bn.at[t - 1, l] for l in subs]); sh = sh / sh.sum()
        pis = np.array([100 * (bp.at[t, l] / bp.at[t - 1, l] - 1) for l in subs])
        roll = float((sh * pis).sum())
        bea = 100 * (bp.at[t, lf] / bp.at[t - 1, lf] - 1)
        errs.append((lf, eng.names[lf], str(t), roll, bea, roll - bea))
E = pd.DataFrame(errs, columns=['leaf', 'name', 'month', 'rollup_mm', 'bea_leaf_mm', 'error_pp'])
by = E.groupby(['leaf', 'name']).error_pp.agg(mean='mean', mean_abs=lambda x: x.abs().mean(), max_abs=lambda x: x.abs().max(), n='size').reset_index()
all_row = pd.DataFrame([dict(leaf='ALL', name=f'all {len(split_leaves)} split leaves, Oct 2023 - Sep 2026', mean=E.error_pp.mean(), mean_abs=E.error_pp.abs().mean(),
                             max_abs=E.error_pp.abs().max(), n=len(E))])
by = pd.concat([by, all_row], ignore_index=True)
print(by.round(4).to_string())
# sensitivity of Oct leaf breadth to the roll-up error: shift every split leaf's October m/m by +/- its own max_abs and by +/- overall p95
p95 = E.error_pp.abs().quantile(0.95)
ma = by.set_index('leaf').max_abs.to_dict()
res = []
base = {}
for back in (12, 3):
    base[back] = breadth('leaf', 'core', '2026-10', back)[0]
    lo = hi = base[back]
    for sign in (-1, 1):
        saved = dict(OCT_LEAF_PI)
        for lf in split_leaves:
            OCT_LEAF_PI[lf] = saved[lf] + sign * ma[lf]
        v = breadth('leaf', 'core', '2026-10', back)[0]
        OCT_LEAF_PI.update(saved)
        lo, hi = min(lo, v), max(hi, v)
    # weight of split leaves whose Oct rate is within the shift of 3%
    d = unit_table('leaf', SCOPES['core'], '2026-10', back)
    d['sh'] = d.leaf.map(lambda l: ma.get(l, 0))
    near = d[(d.r - 3).abs() <= d.sh * (1 if back == 12 else 4)]
    res.append(dict(horizon=f'{back}m' + ('_ann' if back == 3 else ''), oct_leaf_breadth_point=round(base[back], 3), band_low=round(lo, 3), band_high=round(hi, 3),
                    n_split_leaves=len(split_leaves),
                    near_threshold_leaves=len(near), near_threshold_weight_pct=round(100 * near.w.sum() / d.w.sum(), 3)))
R = pd.DataFrame(res)
R['note'] = (f'band: every split leaf Oct m/m shifted by +/- its own maximum historical roll-up error (Oct 2023-Sep 2026); overall mean abs error '
             f'{E.error_pp.abs().mean():.4f} pp, p95 {p95:.4f} pp, max {E.error_pp.abs().max():.4f} pp')
print(R.to_string())
by['section'] = 'roll-up error by leaf (pp m/m, fixed prior-month within-leaf shares vs BEA leaf m/m)'
R['section'] = 'effect on October leaf breadth'
pd.concat([by, R], ignore_index=True).round(4).to_csv(os.path.join(OUTDIR, 'C_leaf_rollup_check.csv'), index=False)

# ---------------------------------------------------------------- 5. flip distance and carried-forward stress (sub-line, core, Oct estimate)
# For each core pricing line: the October m/m (%) that would put its Oct rate exactly on 3%, vs the m/m used. Exact formulas:
#   12m: I_Oct* = 1.03 * I_Oct2025 ;  3m ann.: I_Oct* = 1.03**(1/4) * I_Jul2026 ;  pi* = 100*(I_Oct*/I_Sep - 1)
# SD = standard deviation of the line's BEA m/m over the 36 months to Sep 2026 (BEA current vintage).
rows = []
for line, leaf in units('sub', SCOPES['core']):
    b = bl(line)
    i_sep = bp.at[SEP, b]
    pi_used = OCT_PI[line]
    sd = float(eng.bea_mm[b].loc[SEP - 35:SEP].std())
    w12 = nominal_weight(line, leaf, OCT - 12, 'sub')
    w3 = nominal_weight(line, leaf, OCT - 3, 'sub')
    star12 = 100 * (1.03 * bp.at[OCT - 12, b] / i_sep - 1)
    star3 = 100 * (1.03 ** 0.25 * bp.at[OCT - 3, b] / i_sep - 1)
    rows.append(dict(line=line, name=eng.names[b], leaf=leaf, tier=OCT_TIER[line], w12_pct=w12, w3_pct=w3, oct_mm_used=pi_used,
                     mm_needed_for_12m_eq_3pct=star12, mm_needed_for_3m_eq_3pct=star3, mm_sd_36m=sd,
                     r12_oct=rate(line, OCT, 12, 'sub'), r3_oct=rate(line, OCT, 3, 'sub')))
fd = pd.DataFrame(rows)
fd['w12_pct'] = 100 * fd.w12_pct / fd.w12_pct.sum()
fd['w3_pct'] = 100 * fd.w3_pct / fd.w3_pct.sum()
fd['gap12_pp'] = fd.oct_mm_used - fd.mm_needed_for_12m_eq_3pct          # + means the used m/m is above the flip point
fd['gap3_pp'] = fd.oct_mm_used - fd.mm_needed_for_3m_eq_3pct
fd['above3_12m'] = fd.r12_oct > 3
fd['flip12_within_1sd'] = fd.gap12_pp.abs() <= fd.mm_sd_36m
fd['flip3_within_1sd'] = fd.gap3_pp.abs() <= fd.mm_sd_36m
assert (fd.above3_12m == (fd.gap12_pp > 0)).all()
fd.round(4).sort_values('w12_pct', ascending=False).to_csv(os.path.join(OUTDIR, 'C_flip_distance_oct.csv'), index=False)

# stress: every line in a tier moves its October m/m by +/- 1 SD simultaneously (an extreme, not a probability)
st = []
saved = dict(OCT_PI)
for tier in ('assumed', 'observed_needs_seasonal', 'observed_published', 'blend'):
    sds = fd.set_index('line').mm_sd_36m
    res = {}
    for sign in (-1, 1):
        for ln in fd.line[fd.tier == tier]:
            OCT_PI[ln] = saved[ln] + sign * sds[ln]
        res[sign] = (breadth('sub', 'core', '2026-10', 12)[0], breadth('sub', 'core', '2026-10', 3)[0])
        OCT_PI.update(saved)
    gt = fd[fd.tier == tier]
    st.append(dict(tier=tier, n_lines=len(gt), weight_pct_12m_base=round(gt.w12_pct.sum(), 2),
                   weight_pct_within_1sd_of_flip_12m=round(gt.w12_pct[gt.flip12_within_1sd].sum(), 2),
                   weight_pct_within_1sd_of_flip_3m=round(gt.w3_pct[gt.flip3_within_1sd].sum(), 2),
                   oct_12m_breadth_if_all_minus1sd=round(res[-1][0], 3), oct_12m_breadth_if_all_plus1sd=round(res[1][0], 3),
                   oct_3m_breadth_if_all_minus1sd=round(res[-1][1], 3), oct_3m_breadth_if_all_plus1sd=round(res[1][1], 3),
                   base_12m=round(breadth('sub', 'core', '2026-10', 12)[0], 3), base_3m=round(breadth('sub', 'core', '2026-10', 3)[0], 3)))
st = pd.DataFrame(st)
st['note'] = ('stress = every line of the tier shifted by -1 SD / +1 SD of its own 36-month m/m SD at once (extreme case, not a forecast interval); '
              'within_1sd = weight of lines whose Oct m/m is within 1 SD of the value that puts the rate exactly on 3%')
st.to_csv(os.path.join(OUTDIR, 'C_carried_forward_stress.csv'), index=False)
print(st.drop(columns='note').to_string())

# ---------------------------------------------------------------- 6. the three hospital lines (184, 185, 186): the largest single driver of the Oct 12m drop
need = fd.set_index('line').mm_needed_for_12m_eq_3pct
saved = dict(OCT_PI)
for ln in (184, 185, 186):
    OCT_PI[ln] = need[ln] + 1e-6
b12_hosp_above = breadth('sub', 'core', '2026-10', 12)[0]
b3_hosp_above = breadth('sub', 'core', '2026-10', 3)[0]
OCT_PI.update(saved)
hosp = fd[fd.line.isin([184, 185, 186])]
H = pd.DataFrame([dict(item='hospital lines 184+185+186 (nonprofit, proprietary, government hospitals)', core_weight_pct_oct_12m_window=hosp.w12_pct.sum(),
                       sep_12m_rate_pct=float(m.set_index('line').loc[184, 'r_S']), oct_12m_rate_est_pct=float(hosp.r12_oct.mean()), oct_mm_used_pct=float(hosp.oct_mm_used.mean()),
                       oct_mm_needed_to_stay_above_3pct_12m=float(hosp.mm_needed_for_12m_eq_3pct.mean()), mm_sd_36m=float(hosp.mm_sd_36m.mean()),
                       oct_12m_breadth_base=breadth('sub', 'core', '2026-10', 12)[0], oct_12m_breadth_if_hospitals_just_above_3pct=b12_hosp_above,
                       oct_3m_breadth_base=breadth('sub', 'core', '2026-10', 3)[0], oct_3m_breadth_if_hospitals_just_above_3pct=b3_hosp_above,
                       tier='observed_needs_seasonal: PPI hospitals PCU622---622--- (no first release) with our method-B seasonal adjustment',
                       note='all three lines use the same PPI series, so they move together')]).round(3)
H.to_csv(os.path.join(OUTDIR, 'C_hospital_lines.csv'), index=False)
print(H.T.to_string())
