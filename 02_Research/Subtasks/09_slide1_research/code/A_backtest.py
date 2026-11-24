"""A_backtest.csv: Dec 2025 - Sep 2026 (n=10 rule months) first-release-variant backtest, rebuilt from
04_oct_pce_build/outputs/D2_backtest_variant_first_release_pm.csv (our estimate, first print) and backtest_results.csv
(Cleveland nowcast and core-CPI-OLS benchmark). Errors = estimate minus BEA first print (pp, m/m, SA)."""
import sys, math
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *

d2 = [r for r in rd(f'{BUILD}/D2_backtest_variant_first_release_pm.csv') if r['row_type'] == 'month' and r['in_rule'] == 'True']
bt = rd(f'{BUILD}/backtest_results.csv')
bt = [r for r in bt if r['row_type'] == 'month' and r['group'].startswith('rule')]
def pick(meas, method, month):
    x = [r for r in bt if r['measure'] == meas and r['method'] == method and r['month'] == month]
    assert len(x) == 1, (meas, method, month, len(x))
    return x[0]
months = sorted(set(r['month'] for r in d2))
assert len(months) == 10 and months[0] == '2025-12' and months[-1] == '2026-09', months
f = lambda v: float(v)
rows = []
vals = {k: [] for k in ('core_us', 'core_cle', 'core_cpi', 'hl_us', 'hl_cle')}
errs = {k: [] for k in vals}
for m in months:
    c = [r for r in d2 if r['month'] == m and r['measure'] == 'core'][0]
    h = [r for r in d2 if r['month'] == m and r['measure'] == 'headline'][0]
    cle_c, cpi_c, cle_h = pick('core', 'bench3_cleveland', m), pick('core', 'bench2_core_cpi_ols', m), pick('headline', 'bench3_cleveland', m)
    # consistency of first prints between files
    assert abs(f(cle_c['first_print']) - f(c['first_print'])) < 5e-5 and abs(f(cle_h['first_print']) - f(h['first_print'])) < 5e-5
    row = dict(row_type='month', period=m, table_version=c['table_version'],
               core_first_print=c['first_print'], first_print_vintage=c['first_print_vintage'],
               our_core_est=c['est_variant'], our_core_est_main_run=c['est_main'], our_core_err=f'{f(c["est_variant"]) - f(c["first_print"]):.4f}',
               cleveland_core_nowcast=cle_c['estimate'], cleveland_core_err=f'{f(cle_c["estimate"]) - f(c["first_print"]):.4f}', cleveland_timing=cle_c['note'],
               core_cpi_ols_est=cpi_c['estimate'], core_cpi_err=f'{f(cpi_c["estimate"]) - f(c["first_print"]):.4f}', core_cpi_note=cpi_c['note'],
               headline_first_print=h['first_print'],
               our_headline_est=h['est_variant'], our_headline_est_main_run=h['est_main'], our_headline_err=f'{f(h["est_variant"]) - f(h["first_print"]):.4f}',
               cleveland_headline_nowcast=cle_h['estimate'], cleveland_headline_err=f'{f(cle_h["estimate"]) - f(h["first_print"]):.4f}')
    rows.append(row)
    for k, e in (('core_us', row['our_core_err']), ('core_cle', row['cleveland_core_err']), ('core_cpi', row['core_cpi_err']),
                 ('hl_us', row['our_headline_err']), ('hl_cle', row['cleveland_headline_err'])):
        errs[k].append(float(e))
stat = {}
for k, e in errs.items():
    n = len(e)
    stat[k] = dict(n=n, bias=sum(e) / n, mae=sum(abs(x) for x in e) / n, rmse=math.sqrt(sum(x * x for x in e) / n))
colmap = dict(core_us='our_core_err', core_cle='cleveland_core_err', core_cpi='core_cpi_err', hl_us='our_headline_err', hl_cle='cleveland_headline_err')
for s in ('n', 'bias', 'MAE', 'RMSE'):
    key = {'n': 'n', 'bias': 'bias', 'MAE': 'mae', 'RMSE': 'rmse'}[s]
    row = dict(row_type='summary', period='Dec 2025 - Sep 2026 (n=10 rule months)', stat=s)
    for k, col in colmap.items():
        row[col] = f'{stat[k][key]:.4f}' if s != 'n' else stat[k]['n']
    rows.append(row)
for r in rows:
    r.setdefault('stat', '')
    r.update(source='04_oct_pce_build/outputs: D2_backtest_variant_first_release_pm.csv (ours, first print), backtest_results.csv (Cleveland = bench3_cleveland, core CPI = bench2_core_cpi_ols)',
             vintage='BEA first print = ALFRED first-release vintage per month; components/weights current vintage (not real time); variant = first-release PM PPIs',
             basis='m/m % SA, 4 dp, error = estimate minus first print (pp); first-release variant (decision run per Eli Nov 13); core CPI alone = expanding-window OLS of core PCE m/m on core CPI m/m (not raw CPI)')
cols = ['row_type', 'period', 'stat', 'table_version', 'first_print_vintage', 'core_first_print', 'our_core_est', 'our_core_est_main_run', 'our_core_err',
        'cleveland_core_nowcast', 'cleveland_core_err', 'cleveland_timing', 'core_cpi_ols_est', 'core_cpi_err', 'core_cpi_note',
        'headline_first_print', 'our_headline_est', 'our_headline_est_main_run', 'our_headline_err', 'cleveland_headline_nowcast', 'cleveland_headline_err',
        'source', 'vintage', 'basis']
write_csv(f'{OUT}/A_backtest.csv', rows, cols)
print('\nSummary (recomputed from rows):')
for k, v in stat.items(): print(k, {a: round(b, 4) if a != 'n' else b for a, b in v.items()})
print('\nTab claims: core MAE 0.042 / Cleveland 0.068 / CPI 0.087, n=10, bias +0.017')
# also compare to the stored D2/backtest summary rows
d2s = [r for r in rd(f'{BUILD}/D2_backtest_variant_first_release_pm.csv') if r['row_type'] == 'summary' and r['group'].startswith('rule') and r['run'] == 'variant']
for r in d2s: print('D2 stored', r['measure'], 'bias', r['bias'], 'mae', r['mae'], 'rmse', r['rmse'])
