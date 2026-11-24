"""Task 3: seasonal tests.
(1) For every NSA input series and every input of a 'SA by BEA' line (current table, plus old-table inputs):
    OLS of the series' m/m on 12 calendar-month dummies, F-test that all month means are equal.
    Sample: all months Feb 2015 - Sep 2026 in component_series_history.csv (current vintage); Oct and Nov 2025
    dropped for CPI series whose Oct 2025 value was missing (BLS did not collect). Check only: the estimate uses
    NSA series as BEA directs regardless of the result.
(2) For every 'SA by BEA' pricing line (current table): method B implied October adjustment for target Oct 2026
    (mean over prior Octobers of BEA SA m/m minus source NSA m/m; years listed), and method A (own month-dummy
    factor: minus (mean Oct NSA m/m - mean of all months)) as a cross-check. Method B is the one used.
Output: outputs/seasonal_tests.csv (+ _meta.csv)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from scipy import stats
from D_common import Engine, P, OUT


def ftest(y):
    y = y.dropna()
    if len(y) < 36:
        return np.nan, np.nan, len(y)
    groups = [y[y.index.month == m].values for m in range(1, 13)]
    groups = [g for g in groups if len(g) > 1]
    f, p = stats.f_oneway(*groups)
    return f, p, len(y)


def main():
    eng = Engine()
    target = P('2026-10')
    rows = []
    seen = {}
    for version in ('2026-09-30', '2026-02-20'):
        for ln, s in eng.specs(version).items():
            if not s['inputs']:
                continue
            for sid, _ in s['inputs']:
                is_nsa = sid.startswith(('CUUR', 'PCU', 'WPU'))
                if not (is_nsa or s['seasonal'] == 'SAbyBEA'):
                    continue
                key = sid
                if key in seen:
                    seen[key]['used_by_lines'] += f';{ln}' if str(ln) not in seen[key]['used_by_lines'].split(';') else ''
                    continue
                y = eng.hist_mm(sid).loc[:P('2026-09')]
                if sid in eng.oct25_filled:
                    y = y.drop([P('2025-10'), P('2025-11')], errors='ignore')
                f, p, n = ftest(y)
                r = dict(kind='input series F-test', series_id=sid, used_by_lines=str(ln), table=version,
                         bea_seasonal_status_of_line=s['seasonal'], n_months=n, F_stat=f, p_value=p,
                         seasonal_at_5pct=('yes' if p < 0.05 else 'no') if pd.notna(p) else 'n/a')
                seen[key] = r
                rows.append(r)
    for ln, s in eng.specs('2026-09-30').items():
        if s['seasonal'] != 'SAbyBEA' or not s['inputs']:
            continue
        b, yrs = eng.method_b(s, target)
        a = eng.method_a(s, target)
        w, wsrc = eng.blend_weights(s, target)
        src = eng.nsa_source_hist(s, target)
        f, p, n = ftest(src.loc[:P('2026-09')])
        is_ppi = all(sid.startswith(('PCU', 'WPU')) for sid, _ in s['inputs'])
        rows.append(dict(kind='SA by BEA line: October factor', series_id=';'.join(x for x, _ in s['inputs']), used_by_lines=str(ln),
                         table='2026-09-30', bea_seasonal_status_of_line='SA by BEA', n_months=n, F_stat=f, p_value=p,
                         seasonal_at_5pct=('yes' if p < 0.05 else 'no') if pd.notna(p) else 'n/a',
                         line_name=s['name'], weights=';'.join(f'{x:.4f}' for x in w), weight_source=wsrc,
                         methodB_oct_adj_pp=b, methodB_years=yrs, methodA_oct_adj_pp=a if is_ppi else np.nan,
                         methodA_oct_adj_pp_crosscheck_cpi=a if not is_ppi else np.nan, A_minus_B_pp=(a - b) if pd.notna(a) else np.nan))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, 'seasonal_tests.csv'), index=False, float_format='%.4f')
    pd.DataFrame([
        ('file', 'seasonal_tests.csv'), ('script', 'code/D_seasonal_tests.py'),
        ('F-test', 'one-way ANOVA of m/m by calendar month (= F-test on 12 month dummies), Feb 2015 - Sep 2026, current vintage'),
        ('method B', 'BEA implied adjustment for October = mean over prior Octobers of (BEA SA m/m - source NSA m/m), pp; '
                     'BEA U20404 starts 2017, so Octobers 2017-2025; line 50 uses Feb 2021+ and lines 299/305 use Feb 2024+ (new source start per BEA; see D_common.NEW_METHOD_START)'),
        ('method A', 'own month-dummy factor on the NSA source: -(mean October m/m - mean of all months), pp, years before Oct 2026; cross-check only'),
        ('Oct 2025', 'PPIs have Oct 2025 values and are used; CPI inputs missing in Oct 2025 are filled with BEA geometric mean for m/m, '
                     'and Oct 2025 is kept out of the October factor; Oct/Nov 2025 dropped from F-tests for those CPI series'),
        ('look-ahead', 'BEA re-estimates seasonal factors each annual update; current-vintage BEA history embeds later information')],
        columns=['field', 'value']).to_csv(os.path.join(OUT, 'seasonal_tests_meta.csv'), index=False)
    pd.set_option('display.width', 250)
    print(out[out.kind.str.startswith('SA by')][['used_by_lines', 'series_id', 'p_value', 'methodB_oct_adj_pp', 'methodB_years',
                                                  'methodA_oct_adj_pp', 'methodA_oct_adj_pp_crosscheck_cpi']].to_string())
    x = out[out.kind == 'input series F-test']
    print('input series tested', len(x), 'seasonal at 5%:', (x.seasonal_at_5pct == 'yes').sum())


if __name__ == '__main__':
    main()
