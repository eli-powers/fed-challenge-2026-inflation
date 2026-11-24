"""Brief B, Q4: weighted breadth by measure (core, supercore, core goods, core services; headline as backup).

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/B_q4_breadth_by_measure.py"

Engine: 09_slide1_research/code/C_common.py, imported read-only (unit_table, SCOPES, is_supercore_leaf, breadth).
New scope: core_goods = core leaves with line < 150 (built from SCOPES['core'], no new rate/weight logic).
Method (Eli, binding): share of start-of-window nominal spending weight whose annualized rate is > 3%;
weighted leaf (149 core leaves) central, sub-line (184 core pricing lines) robustness.
October 2026 = UMD estimate (BEA Sep index extended by the audited 04_oct_pce_build October m/m), labelled est.

Writes (10_slide2_research/outputs/): B_q4_breadth_by_measure.csv, B_q4_breadth_ts.csv, B_q4_checks.csv
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402  (read-only import of the audited engine)

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
S1 = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'outputs')
VINTAGE = 'BEA NIPA U20404 (prices) / U20405 (nominal) vintage 2026-11-10, data through Sep 2026; SA'

MEASURES = {
    'core': set(cc.SCOPES['core']),
    'supercore': set(cc.SCOPES['supercore']),
    'core_goods': set(l for l in cc.SCOPES['core'] if l < 150),
    'core_services': set(cc.SCOPES['core_services']),
    'headline_backup': set(cc.SCOPES['headline']),
}
assert MEASURES['core_goods'] | MEASURES['core_services'] == MEASURES['core']
assert not (MEASURES['core_goods'] & MEASURES['core_services'])


def table(gran, end, back):
    """unit table over all headline leaves once; measures subset it (same engine, same rows)."""
    return cc.unit_table(gran, MEASURES['headline_backup'], end, back)


def br(d, leafset):
    s = d[d.leaf.isin(leafset)]
    return 100 * s.w[s.r > 3].sum() / s.w.sum(), len(s)


# ------------------------------------------------------------------ checks: reproduce slide 1 numbers
checks = []


def chk(name, got, want, src, tol=0.01):
    ok = abs(got - want) < tol
    checks.append(dict(check=name, reproduced=round(got, 3), source_value=want, abs_diff=round(abs(got - want), 4), tol=tol, pass_=ok, source=src))
    assert ok, (name, got, want)


for (g, back, m), want in {('leaf', 12, '2026-09'): 60.626, ('leaf', 12, '2026-10'): 54.038,
                           ('leaf', 3, '2026-09'): 44.814, ('leaf', 3, '2026-10'): 45.467}.items():
    d = table(g, m, back)
    chk(f'core {g} {back}m {m} (brief binding value)', br(d, MEASURES['core'])[0], want, 'brief_B.md / C_breadth.csv')

c1 = pd.read_csv(os.path.join(S1, 'C_breadth.csv'))
prim = c1[c1.role.isin(['primary', 'robustness'])]
for _, r in prim.iterrows():
    g = 'leaf' if r.method == 'leaf' else 'sub'
    back = 12 if r.horizon == '12m' else 3
    meas = 'headline_backup' if r.scope == 'headline' else r.scope
    d = table(g, r.period, back)
    v, n = br(d, MEASURES[meas])
    assert n == r.n_units, (r.scope, g, n, r.n_units)
    chk(f'{r.scope} {r.method} {r.horizon} {r.period}', v, r.value_pct, 'C_breadth.csv (09_slide1_research/outputs)', tol=0.0006)
wv = pd.read_csv(os.path.join(S1, 'C_waller_variants.csv'))
for _, r in wv[wv.variant.str.startswith('weight: start')].iterrows():
    g = 'leaf' if r.method == 'leaf' else 'sub'
    d = table(g, r.period, 12)
    chk(f'{r.scope} {r.method} 12m {r.period} (Waller weighted)', br(d, MEASURES[r.scope])[0], r.value_pct, 'C_waller_variants.csv', tol=0.0006)

# ------------------------------------------------------------------ point table, Sep vs Oct est.
rows = []
for period in ('2026-09', '2026-10'):
    for back, hz in ((3, '3m_ann'), (12, '12m')):
        for g, meth in (('leaf', 'leaf (central)'), ('sub', 'sub-line (robustness)')):
            d = table(g, period, back)
            for meas, ls in MEASURES.items():
                v, n = br(d, ls)
                rows.append(dict(period=period, measure=meas, horizon=hz, method=meth, value=round(v, 3), n_units=n,
                                 status='BEA published' if period == '2026-09' else 'est. (UMD October build)',
                                 weight_basis=f'start-of-window nominal shares of {cc.P(period) - back}',
                                 block='backup (rises mechanically in an energy shock)' if meas == 'headline_backup' else 'main',
                                 vintage=VINTAGE))

# ------------------------------------------------------------------ monthly series 2018-01 .. 2026-10
months = [str(p) for p in pd.period_range('2018-01', '2026-10', freq='M')]
ts = []
for m in months:
    rec = dict(month=m, status='BEA published' if m <= '2026-09' else 'est.')
    for g, tag in (('leaf', 'leaf'), ('sub', 'subline')):
        for back, hz in ((3, '3m_ann'), (12, '12m')):
            d = table(g, m, back)
            for meas, ls in MEASURES.items():
                rec[f'{meas}_{hz}_{tag}'] = round(br(d, ls)[0], 3)
    ts.append(rec)
ts = pd.DataFrame(ts)

# check: core series identical to slide 1 C_breadth_ts.csv
old = pd.read_csv(os.path.join(S1, 'C_breadth_ts.csv'))
old = old[old.month.str.match(r'^\d{4}-\d{2}$')].set_index('month')
new = ts.set_index('month')
for hz in ('3m_ann', '12m'):
    for tag in ('leaf', 'subline'):
        diff = (new[f'core_{hz}_{tag}'] - old[f'core_breadth_{hz}_{tag}']).abs().max()
        chk(f'core {tag} {hz} monthly series 2018-01..2026-10, max abs diff', diff, 0.0, 'C_breadth_ts.csv', tol=0.0011)

# reference rows: 2018-19 average, post-2018 peak, trough (published months only for peak/trough, plus Oct est. shown separately)
cols = [c for c in ts.columns if c not in ('month', 'status')]
pub = ts[ts.month <= '2026-09'].set_index('month')
avg = pub.loc['2018-01':'2019-12', cols].mean()
summ = []
for c in cols:
    s = pub[c]
    meas, rest = c.split('_3m_ann_') if '_3m_ann_' in c else c.split('_12m_')
    hz = '3m_ann' if '_3m_ann_' in c else '12m'
    summ.append(dict(series=c, measure=meas, horizon=hz, method='leaf' if rest == 'leaf' else 'sub-line',
                     avg_2018_2019=round(avg[c], 3), peak_month_2018_2026Sep=s.idxmax(), peak_value=round(s.max(), 3),
                     trough_month=s.idxmin(), trough_value=round(s.min(), 3), sep_2026=s['2026-09'],
                     oct_2026_est=float(new.at['2026-10', c]),
                     sep_minus_avg=round(s['2026-09'] - avg[c], 3), oct_est_minus_avg=round(new.at['2026-10', c] - avg[c], 3),
                     sep_pctile_in_2018_2026=round(100 * (s <= s['2026-09']).mean(), 1),
                     last_month_at_or_above_sep_before_sep=(s[s.index < '2026-09'][s[s.index < '2026-09'] >= s['2026-09']].index.max()
                                                            if (s[s.index < '2026-09'] >= s['2026-09']).any() else 'none')))
summ = pd.DataFrame(summ)
summ.to_csv(os.path.join(OUT, 'B_q4_breadth_summary.csv'), index=False)

ref = dict(month='avg_2018_2019', status='reference: mean of 24 monthly values Jan 2018-Dec 2019')
ref.update({c: round(avg[c], 3) for c in cols})
pk = dict(month='peak_value_2018-01_to_2026-09', status='reference: max over published months')
pk.update({c: round(pub[c].max(), 3) for c in cols})
pkm = dict(month='peak_month', status='reference: month of max')
pkm.update({c: pub[c].idxmax() for c in cols})
ts_out = pd.concat([ts, pd.DataFrame([ref, pk, pkm])], ignore_index=True)
ts_out['weight_basis'] = 'start-of-window nominal shares (t-3 for 3m ann., t-12 for 12m); rate > 3%'
ts_out['vintage'] = VINTAGE + '; 2026-10 = est.'
ts_out.to_csv(os.path.join(OUT, 'B_q4_breadth_ts.csv'), index=False)

# add avg / peak rows to the long table too
for _, s in summ.iterrows():
    for lab, val, extra in (('avg_2018_2019', s.avg_2018_2019, ''), (f'peak {s.peak_month_2018_2026Sep}', s.peak_value, 'post-2018 peak over published months')):
        rows.append(dict(period=lab, measure=s.measure, horizon=s.horizon,
                         method='leaf (central)' if s.method == 'leaf' else 'sub-line (robustness)', value=val,
                         n_units=len(MEASURES[s.measure]) if s.method == 'leaf' else None,
                         status='reference', weight_basis='start-of-window', block='backup' if s.measure == 'headline_backup' else 'main',
                         vintage=VINTAGE))
out = pd.DataFrame(rows)
# n_units for sub-line reference rows
nsub = {meas: br(table('sub', '2026-09', 12), ls)[1] for meas, ls in MEASURES.items()}
out.loc[out.n_units.isna(), 'n_units'] = out.loc[out.n_units.isna(), 'measure'].map(nsub)
out['n_units'] = out.n_units.astype(int)
out.to_csv(os.path.join(OUT, 'B_q4_breadth_by_measure.csv'), index=False)
pd.DataFrame(checks).rename(columns={'pass_': 'pass'}).to_csv(os.path.join(OUT, 'B_q4_checks.csv'), index=False)

pd.set_option('display.width', 250)
print(out[out.period.isin(['2026-09', '2026-10'])].pivot_table(index=['measure', 'horizon', 'method'], columns='period', values='value'))
print(summ.drop(columns=['series']).to_string())
print('checks passed:', len(checks))

# ------------------------------------------------------------------ hospital attribution per measure (leaves 184-186)
HOSP = {184, 185, 186}
att = []
for g in ('leaf', 'sub'):
    for back, hz in ((12, '12m'), (3, '3m_ann')):
        dS, dO = table(g, '2026-09', back), table(g, '2026-10', back)
        for meas, ls in MEASURES.items():
            if not (ls & HOSP):
                continue
            rec = dict(measure=meas, horizon=hz, method='leaf' if g == 'leaf' else 'sub-line')
            for tag, d in (('sep', dS), ('oct_est', dO)):
                s = d[d.leaf.isin(ls)]
                W = s.w.sum()
                h = s[s.leaf.isin(HOSP)]
                rec[f'{tag}_breadth'] = round(100 * s.w[s.r > 3].sum() / W, 3)
                rec[f'{tag}_hosp_weight_pct'] = round(100 * h.w.sum() / W, 3)
                rec[f'{tag}_hosp_contrib_pp'] = round(100 * h.w[h.r > 3].sum() / W, 3)
                rec[f'{tag}_hosp_rates'] = ';'.join(f'{x:.3f}' for x in h.r)
                xs = s[~s.leaf.isin(HOSP)]
                rec[f'{tag}_breadth_ex_hosp'] = round(100 * xs.w[xs.r > 3].sum() / xs.w.sum(), 3)
            rec['change_pp'] = round(rec['oct_est_breadth'] - rec['sep_breadth'], 3)
            rec['hosp_contrib_change_pp'] = round(rec['oct_est_hosp_contrib_pp'] - rec['sep_hosp_contrib_pp'], 3)
            rec['change_ex_hosp_pp'] = round(rec['oct_est_breadth_ex_hosp'] - rec['sep_breadth_ex_hosp'], 3)
            att.append(rec)
att = pd.DataFrame(att)
att['note'] = 'hospital leaves 184-186 priced off PPI hospitals PCU622---622---; ex_hosp = breadth renormalised without them'
att.to_csv(os.path.join(OUT, 'B_q4_hospital_attribution.csv'), index=False)
print(att.drop(columns=['note', 'sep_hosp_rates', 'oct_est_hosp_rates']).to_string())
