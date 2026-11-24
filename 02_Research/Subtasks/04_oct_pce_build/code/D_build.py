"""Single entry point for the bottom-up PCE estimate of one month (task 6).

Usage (from the project root):
    python3 "02_Research/Subtasks/04_oct_pce_build/code/D_build.py" --month 2026-10
    python3 "02_Research/Subtasks/04_oct_pce_build/code/D_build.py" --month 2026-09     # dry run, Sep 2026
Options: --window N (carry-forward months; default = the window chosen in outputs/backtest_window_choice.csv).

Uses only saved inputs: component_series_history.csv (CPI/PPI, current vintage), ppi_first_release.csv,
BEA U20404/U20405 (2026-11-10), component_mapping.csv, ALFRED PCEPI/PCEPILFE (index levels for the rates).
Information rule: BEA component history, blend-weight fits, method-B factors and carry-forward averages use months
before the target month only. Rates extend BEA's published SA index from the vintage before the target month's
release. The build FAILS (exit code 2, nothing written) if any PPI input of an observed line has no value for the
target month, and lists those inputs.
Outputs: outputs/D_build_<month>_summary.csv and outputs/D_build_<month>_lines.csv."""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import (Engine, P, OUT, PM_LINE, table_version, bottom_up_band, rates, base_vintage_levels, alfred_obs,
                      alfred_first_print)


def missing_ppi(eng, specs, t):
    miss = []
    for ln, s in specs.items():
        if s['tier'] == 'assumed':
            continue
        for sid, _ in s['inputs']:
            if sid.startswith(('PCU', 'WPU')):
                v, prov = eng.series_mm(sid, t, True)
                if pd.isna(v):
                    miss.append((sid, ln, s['name']))
    return miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--month', required=True)
    ap.add_argument('--window', type=int, default=None)
    a = ap.parse_args()
    t = P(a.month)
    wcf = os.path.join(OUT, 'backtest_window_choice.csv')
    if a.window is None:
        if os.path.exists(wcf):
            wc = pd.read_csv(wcf)
            K = int(wc[wc.chosen & (wc.measure == 'core')].window.iloc[0])
        else:
            K = 6
            print('WARNING: backtest_window_choice.csv not found; using the 6-month prior')
    else:
        K = a.window
    eng = Engine()
    version = table_version(t)
    specs = eng.specs(version)

    # ---- input checks
    if (t - 1) not in eng.bea_n.index:
        sys.exit(f'FAIL: BEA spending shares for {t - 1} are not in U20405 (need the previous month).')
    miss = missing_ppi(eng, specs, t)
    if miss:
        print(f'FAIL: {len(miss)} PPI input(s) have no value for {t} in component_series_history.csv or ppi_first_release.csv:')
        for sid, ln, name in sorted(set(miss)):
            print(f'  {sid:22s} BEA line {ln:4d}  {name}')
        print('Nothing was written. After the PPI release: rerun the data pulls listed in code/README.md, then this script.')
        sys.exit(2)
    cpi_obs = [s for s in specs.values() if s['tier'] != 'assumed' and any(x.startswith('CU') for x, _ in s['inputs'])]
    n_cpi_ok = sum(1 for s in cpi_obs if all(pd.notna(eng.series_mm(x, t)[0]) for x, _ in s['inputs']))
    if n_cpi_ok == 0:
        sys.exit(f'FAIL: no CPI inputs for {t}.')

    # ---- estimate
    summ, df = eng.estimate(t, k=K, version=version, first_release=True)
    band, items = bottom_up_band(eng, df, t)
    # Band (b) = backtest RMSE of the run the decision rule rests on. Eli, Nov 13, 2026: the first-release variant
    # (D2_backtest_variant_first_release_pm.csv). Falls back to the main run if that file is absent.
    f_var = os.path.join(OUT, 'D2_backtest_variant_first_release_pm.csv')
    if os.path.exists(f_var):
        vv = pd.read_csv(f_var)
        rr = vv[(vv.row_type == 'summary') & (vv.group == 'rule (Dec 2025-Sep 2026)') & (vv.run == 'variant')]
        rmse_src = 'first-release variant (D2)'
    else:
        bt = pd.read_csv(os.path.join(OUT, 'backtest_results.csv'))
        rr = bt[(bt.row_type == 'summary') & (bt.group == 'rule (Dec 2025-Sep 2026)') & (bt.method == 'build') & (bt.target == 'first print')]
        rmse_src = 'main run (backtest_results.csv)'
        print('WARNING: D2 variant file not found; band uses the main run RMSE')
    rmse = {m: float(rr[rr.measure == m].rmse.iloc[0]) for m in ('core', 'headline')}

    rows = []
    for meas, sid, ba, pm in (('core', 'PCEPILFE', band['band_a_c'], band['pm_allow_c']),
                              ('headline', 'PCEPI', band['band_a_h'], band['pm_allow_h'])):
        est = summ[meas]
        vint, lv = base_vintage_levels(sid, t)
        r = rates(lv, t, est)
        b = max(ba, rmse[meas])
        row = dict(month=str(t), measure=meas, table_version=version, window=K, estimate_mm=est,
                   band_a_bottom_up=ba, band_b_backtest_rmse=rmse[meas], band_b_source=rmse_src, band_reported=b, pm_allowance=pm,
                   base_vintage=vint, base_index_tm1=r['I_tm1'], index_t=r['I_t'],
                   rate_1m_pct=r['r1m'], rate_1m_ann=r['r1m_ann'], band_1m_ann=12 * b,
                   rate_3m_ann=r['r3m_ann'], band_3m_ann=4 * b, rate_6m_ann=r['r6m_ann'], band_6m_ann=2 * b,
                   rate_12m=r['r12m'], band_12m=b)
        # first print comparison when the month has been released (dry run)
        df_a = alfred_obs(sid)
        v1, lv1 = alfred_first_print(df_a, str(t))
        if v1 is not None:
            row.update(fp_vintage=v1, fp_1m=100 * (lv1[t] / lv1[t - 1] - 1), fp_3m_ann=100 * ((lv1[t] / lv1[t - 3]) ** 4 - 1),
                       fp_6m_ann=100 * ((lv1[t] / lv1[t - 6]) ** 2 - 1), fp_12m=100 * (lv1[t] / lv1[t - 12] - 1))
            row['miss_1m'] = est - row['fp_1m']
        col_w = 'w_c' if meas == 'core' else 'w_h'
        for c in ('observed_published', 'observed_needs_seasonal', 'blend', 'proxied', 'assumed'):
            row[f'share_{c}'] = df.loc[df.cat == c, col_w].sum()
            row[f'contrib_{c}'] = df.loc[df.cat == c, 'contrib_c' if meas == 'core' else 'contrib_h'].sum()
        rows.append(row)
    out = pd.DataFrame(rows)

    # PM sensitivity (current table only): old PPI blend instead of carry-forward
    if version == '2026-09-30':
        alt = eng.price_line(eng.specs('2026-02-20')[PM_LINE], t, K, True)
        r = df[df.line == PM_LINE].iloc[0]
        out['pm_carry_forward_mm'] = r.pi
        out['pm_old_ppi_mm'] = alt['pi'] if alt['tier_used'] != 'assumed' else np.nan
        out['pm_sensitivity_effect'] = [r.w_c * (alt['pi'] - r.pi), r.w_h * (alt['pi'] - r.pi)] if alt['tier_used'] != 'assumed' else np.nan
    out.to_csv(os.path.join(OUT, f'D_build_{t}_summary.csv'), index=False, float_format='%.5f')
    keep = ['line', 'leaf', 'name', 'cat', 'tier_used', 'seasonal', 'inputs', 'weights', 'weight_source', 'adj_b', 'adj_b_years',
            'pi', 'w_leaf_h', 'w_leaf_c', 'sub_share', 'w_h', 'w_c', 'contrib_h', 'contrib_c', 'provenance', 'note']
    df[keep].sort_values('contrib_c', key=abs, ascending=False).to_csv(os.path.join(OUT, f'D_build_{t}_lines.csv'), index=False, float_format='%.6f')
    pd.set_option('display.width', 250)
    print(out.T.to_string())
    print(f'Wrote outputs/D_build_{t}_summary.csv and outputs/D_build_{t}_lines.csv')


if __name__ == '__main__':
    main()
