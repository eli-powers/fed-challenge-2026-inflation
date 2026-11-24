"""A_ts_pce_rates.csv: monthly PCE rates from BEA T20804 index levels (line 1 headline, line 25 core), Jan 2018 - Sep 2026,
plus Oct 2026 estimate from the build (flagged est.)."""
import sys
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *

lv = load_levels()
summ = {r['measure']: r for r in rd(f'{BUILD}/D_build_2026-10_summary.csv')}
rows = []
meta = {'headline': ('DPCERG', 1, 'Personal consumption expenditures (PCE)'),
        'core': ('DPCCRG', 25, 'PCE excluding food and energy')}
months = [(y, m) for y in range(2018, 2027) for m in range(1, 13) if (y, m) <= (2026, 9)]
for meas in ('core', 'headline'):
    sc, ln, desc = meta[meas]
    L = lv[meas]
    for ym in months:
        r = rates(L, ym)
        rows.append(dict(month=ymstr(ym), measure=meas, series_code=sc, nipa_table='T20804', line=ln, line_desc=desc,
                         index_level=f'{L[ym]:.3f}', rate_1m_pct=f'{r["r1m"]:.5f}', rate_3m_ann_pct=f'{r["r3m_ann"]:.5f}',
                         rate_6m_ann_pct=f'{r["r6m_ann"]:.5f}', rate_12m_pct=f'{r["r12m"]:.5f}',
                         status='published', source='BEA NIPA Table 2.8.4 (T20804), 2017=100, SA, Fisher price index',
                         vintage=T20804_VINTAGE, basis='computed from index levels: 1m=(L/L-1 -1)*100; 3m ann=((L/L-3)^4-1)*100; 6m ann=((L/L-6)^2-1)*100; 12m=(L/L-12 -1)*100'))
    # Oct 2026 estimate: extend Sep published level by build's m/m
    s = summ[meas]
    est = float(s['estimate_mm'])
    it = L[(2026, 9)] * (1 + est / 100)
    r = rates(L, (2026, 10), level_t=it)
    rows.append(dict(month='2026-10', measure=meas, series_code=sc, nipa_table='T20804', line=ln, line_desc=desc,
                     index_level=f'{it:.3f}', rate_1m_pct=f'{r["r1m"]:.5f}', rate_3m_ann_pct=f'{r["r3m_ann"]:.5f}',
                     rate_6m_ann_pct=f'{r["r6m_ann"]:.5f}', rate_12m_pct=f'{r["r12m"]:.5f}',
                     status='est.', source='UMD bottom-up Oct 2026 estimate (04_oct_pce_build/outputs/D_build_2026-10_summary.csv, estimate_mm) applied to BEA Sep 2026 published level',
                     vintage=f'estimate built Nov 13 2026 (first-release variant); Sep base level from {T20804_VINTAGE}',
                     basis='level = Sep level*(1+estimate_mm/100); rates as above from levels. Not BEA data; BEA publishes Oct on Nov 25, 2026'))
cols = ['month', 'measure', 'series_code', 'nipa_table', 'line', 'line_desc', 'index_level', 'rate_1m_pct', 'rate_3m_ann_pct',
        'rate_6m_ann_pct', 'rate_12m_pct', 'status', 'source', 'vintage', 'basis']
write_csv(f'{OUT}/A_ts_pce_rates.csv', rows, cols)

# checks
bad = False
for meas, want in (('headline', 3.649), ('core', 3.121)):
    got = rates(lv[meas], (2026, 9))['r12m']
    ok = abs(round(got, 3) - want) < 1e-9
    print(f'CHECK Sep 2026 12m {meas}: {got:.5f} -> {round(got,3)} (want {want}) {"OK" if ok else "FAIL"}')
    bad |= not ok
# any missing months in the pull?
for meas in lv:
    assert all(shift(ym, -12) in lv[meas] for ym in months), 'missing base months'
sys.exit(1 if bad else 0)
