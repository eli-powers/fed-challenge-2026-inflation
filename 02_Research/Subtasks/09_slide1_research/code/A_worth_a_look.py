"""Irregularity checks on A_ts_pce_rates.csv (Jan 2018 - Oct 2026 est.). Prints findings and writes outputs/A_worth_a_look.csv."""
import sys
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *

ts = rd(f'{OUT}/A_ts_pce_rates.csv')
S = {}
for r in ts:
    S.setdefault(r['measure'], {})[r['month']] = {k: float(r[k]) for k in ('rate_1m_pct', 'rate_3m_ann_pct', 'rate_6m_ann_pct', 'rate_12m_pct')}
    S[r['measure']][r['month']]['status'] = r['status']
out = []
def rec(measure, q, ans):
    out.append(dict(measure=measure, question=q, answer=ans, source='A_ts_pce_rates.csv (BEA T20804 levels; Oct 2026 = est.)', basis='computed in A_worth_a_look.py'))
    print(measure, '|', q, '|', ans)
for meas in ('core', 'headline'):
    d = S[meas]
    ms = sorted(d)
    o = d['2026-10']
    # ordering 3m > 12m > 6m
    pat = [m for m in ms if d[m]['rate_3m_ann_pct'] > d[m]['rate_12m_pct'] > d[m]['rate_6m_ann_pct']]
    prev = [m for m in pat if m != '2026-10']
    rec(meas, 'months with 3m ann > 12m > 6m ann (Jan 2018 - Oct 2026)', f'{len(pat)} months; last 8: {pat[-8:]}')
    rec(meas, 'Most recent month BEFORE Oct 2026 with 3m>12m>6m', prev[-1] if prev else 'none')
    # 3m > 6m
    gt = [m for m in ms if d[m]['rate_3m_ann_pct'] > d[m]['rate_6m_ann_pct']]
    last12 = [m for m in ms[-12:] if d[m]['rate_3m_ann_pct'] > d[m]['rate_6m_ann_pct']]
    rec(meas, 'Pace test (3m ann > 6m ann): months true among last 12 (Nov 2025 - Oct 2026 est.)', f'{len(last12)} of 12: {last12}')
    # gap size
    gap = {m: d[m]['rate_3m_ann_pct'] - d[m]['rate_6m_ann_pct'] for m in ms}
    top = sorted(gap, key=gap.get, reverse=True)[:5]
    rec(meas, 'largest 3m-minus-6m gaps (pp) in sample', '; '.join(f'{m}: {gap[m]:+.2f}' for m in top) + f'; Oct 2026 est. {gap["2026-10"]:+.2f}')
    for key, lab in (('rate_12m_pct', '12m'), ('rate_3m_ann_pct', '3m ann'), ('rate_6m_ann_pct', '6m ann'), ('rate_1m_pct', '1m')):
        v = o[key]
        prior = [m for m in ms if m != '2026-10' and d[m][key] >= v]
        rec(meas, f'last month before Oct 2026 with {lab} >= Oct est. ({v:.3f})', prior[-1] if prior else 'none since Jan 2018 (first month 2018-01; 12m/3m/6m start 2018-01 using 2017 levels)')
    rec(meas, 'Sep 2026 (published) vs Oct 2026 (est.): 3m ann / 6m ann / 12m', f'{d["2026-09"]["rate_3m_ann_pct"]:.2f}/{d["2026-09"]["rate_6m_ann_pct"]:.2f}/{d["2026-09"]["rate_12m_pct"]:.2f} -> {o["rate_3m_ann_pct"]:.2f}/{o["rate_6m_ann_pct"]:.2f}/{o["rate_12m_pct"]:.2f}')
    rec(meas, 'last 10 months of 1m % (Jan-Oct 2026)', ', '.join(f'{m}:{d[m]["rate_1m_pct"]:.3f}' for m in ms[-10:]))
write_csv(f'{OUT}/A_worth_a_look.csv', out, ['measure', 'question', 'answer', 'source', 'basis'])
