"""A_headline.csv: Oct 2026 estimate (core, headline) recomputed from 04_oct_pce_build outputs + BEA T20804 levels,
with bands, Sep published values, and difference vs the 'PCE Oct 2026 estimate' tab of Price_Basket_Findings.xlsx."""
import sys
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *
import openpyxl

lv = load_levels()
summ = {r['measure']: r for r in rd(f'{BUILD}/D_build_2026-10_summary.csv')}
lines = rd(f'{BUILD}/D_build_2026-10_lines.csv')
wb = openpyxl.load_workbook(WORKBOOK, data_only=True)
ws = wb['PCE Oct 2026 estimate']
# tab cells: rows 5-12; C=Rate, F=Band, rows by (aggregate, horizon)
tab = {}
for r in range(5, 13):
    agg, hor = ws.cell(r, 1).value, ws.cell(r, 2).value
    tab[(('headline' if 'headline' in agg else 'core'), hor)] = (ws.cell(r, 3).value, ws.cell(r, 6).value, f'C{r}', f'F{r}')
HZ = [('1m SA', 'r1m', '1m SA (m/m, %)', 1), ('3m annualized SA', 'r3m_ann', '3m annualized SA (%)', 4),
      ('6m annualized SA', 'r6m_ann', '6m annualized SA (%)', 2), ('12m SA', 'r12m', '12m % (y/y)', 1)]
rows, diffs = [], []
for meas, col in (('core', 'contrib_c'), ('headline', 'contrib_h')):
    s = summ[meas]
    L = lv[meas]
    est_mm = float(s['estimate_mm'])
    line_sum = sum(float(x[col]) for x in lines)
    # recompute: Oct level from Sep published level and the estimated m/m
    it = L[(2026, 9)] * (1 + est_mm / 100)
    r_oct = rates(L, (2026, 10), level_t=it)
    r_sep = rates(L, (2026, 9))
    b = float(s['band_reported'])
    # the build's own stored values (for the diff report only)
    stored = {'r1m': float(s['rate_1m_pct']), 'r3m_ann': float(s['rate_3m_ann']), 'r6m_ann': float(s['rate_6m_ann']), 'r12m': float(s['rate_12m'])}
    for hz_tab, key, hz_lab, mult in HZ:
        tv, tb, c1, c2 = tab[(meas, hz_tab)]
        val = r_oct[key]
        rows.append(dict(
            month='2026-10', measure=meas, series='PCEPILFE / T20804 line 25' if meas == 'core' else 'PCEPI / T20804 line 1',
            horizon=hz_lab, status='est.', estimate=f'{val:.5f}', band_pm=f'{mult*b:.5f}',
            band_basis=f'build backtest RMSE vs BEA first print, first-release variant (Dec 2025-Sep 2026, n=10) = {b:.4f} pp m/m, x{mult} for this horizon',
            sep_published=f'{r_sep[key]:.5f}', sep_basis='BEA published Sep 2026, from T20804 index levels (vintage Oct 29 release)',
            build_stored_value=f'{stored[key]:.5f}', tab_value=tv, tab_cell=c1, diff_vs_tab=f'{val - tv:.5f}',
            tab_band=tb, band_diff_vs_tab=f'{mult*b - tb:.5f}',
            m_m_line_sum_check=f'{line_sum:.6f}' if key == 'r1m' else '',
            sa='SA', ref_period='Oct 2026', vintage='estimate built 2026-11-13; Sep base level BEA T20804 saved 2026-11-10 (Oct 29 vintage)',
            source='02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv (estimate_mm, band_reported) + D_build_2026-10_lines.csv; levels: BEA NIPA T20804',
            basis='recomputed: Oct level = Sep published level x (1+estimate_mm/100); rates from levels'))
        diffs.append((meas, hz_tab, val, stored[key], tv))
# BEA published Sep m/m rounded text values, for reference
rel = [dict(month='2026-09', measure='core', series='BEA release text', horizon='1m SA (m/m, %), rounded', status='published', estimate='0.3', sep_published='0.3', basis='BEA PIO Sep 2026 text, 1 dp', source='BEA_PIO_release_Sep2026 html', sa='SA', ref_period='Sep 2026', vintage='released 2026-10-29'),
       dict(month='2026-09', measure='headline', series='BEA release text', horizon='1m SA (m/m, %), rounded', status='published', estimate='0.5', sep_published='0.5', basis='BEA PIO Sep 2026 text, 1 dp', source='BEA_PIO_release_Sep2026 html', sa='SA', ref_period='Sep 2026', vintage='released 2026-10-29')]
cols = ['month', 'measure', 'series', 'horizon', 'status', 'estimate', 'band_pm', 'band_basis', 'sep_published', 'sep_basis',
        'build_stored_value', 'tab_value', 'tab_cell', 'diff_vs_tab', 'tab_band', 'band_diff_vs_tab', 'm_m_line_sum_check',
        'sa', 'ref_period', 'vintage', 'source', 'basis']
write_csv(f'{OUT}/A_headline.csv', rows + rel, cols)
print('\nmeasure horizon recomputed | build stored | tab | recomputed-tab')
for m, h, v, st, tv in diffs:
    print(f'{m:9s} {h:18s} {v:.5f} | {st:.5f} | {tv:.5f} | {v-tv:+.6f}')
for meas, col in (('core', 'contrib_c'), ('headline', 'contrib_h')):
    print(meas, 'sum of line contributions', f'{sum(float(x[col]) for x in lines):.6f}', 'vs estimate_mm', summ[meas]['estimate_mm'])
