"""Task 4-5 and 7: backtest under the locked specification, decision rule, attribution, bands, event check.

Months in the decision rule: Dec 2025 - Sep 2026 (10). Also run, excluded from the rule: Nov 2025, Oct 2023, Oct 2024.
Target: BEA first print m/m (same ALFRED vintage); secondary: current vintage (U20404 2026-11-10).
Information set: PPI at first release where ppi_first_release.csv has it (else revised, flagged); CPI current vintage
(flag: SA values revised Feb 2026 for ref months through Dec 2025); seasonal factors, blend weights and carry-forward
averages use months before the target month only (but current-vintage BEA history: not real time).
Methods by month: 2026-02-20 table for Dec 2025 - Jul 2026; 2026-09-30 table for Aug - Sep 2026;
2025-02-28 table for Nov 2025, Oct 2023, Oct 2024 (judgment).
Carry-forward window chosen among 3/6/12 by lowest MAE of the assumed tier's total CORE contribution vs BEA's
current-vintage assumed-tier contribution over the rule months (same months as the test: disclosed).
Outputs: outputs/backtest_results.csv, backtest_attribution.csv, backtest_lines.csv, backtest_window_choice.csv,
         backtest_bands.csv, backtest_event_check.csv (+ _meta.csv)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import (Engine, P, OUT, RULE_MONTHS, OLD_GROUP, NEW_GROUP, EXTRA_MONTHS, HEADLINE_LINE, CORE_LINE, PM_LINE,
                      table_version, first_prints, alfred_obs, alfred_asof, bottom_up_band, round1, CPI_SA_REVISED_FEB2026,
                      CLEV_HIST, CLEV_LONG, build_specs)

MONTHS = RULE_MONTHS + EXTRA_MONTHS
WINDOWS = (3, 6, 12)


def core_cpi_current():
    df = alfred_obs('CPILFESL')
    lv = alfred_asof(df, df.realtime_start.max())
    full = pd.period_range(lv.index.min(), lv.index.max(), freq='M')
    lv = lv.reindex(full)
    filled = lv.copy()
    o = P('2025-10')
    if pd.isna(filled[o]):
        filled[o] = np.sqrt(filled[o - 1] * filled[o + 1])
    return 100 * (lv / lv.shift(1) - 1), 100 * (filled / filled.shift(1) - 1)


def bench_core_cpi_ols(eng, t, cpi_mm, cpi_mm_filled):
    """OLS of core PCE m/m (U20404 line 374, current vintage) on core CPI m/m (CPILFESL, current ALFRED vintage),
    expanding window from Feb 2017 through t-1; prediction uses core CPI m/m for t (current vintage)."""
    t = P(t)
    y = eng.bea_mm[CORE_LINE]
    d = pd.concat([y.rename('y'), cpi_mm.rename('x')], axis=1).loc[P('2017-02'):t - 1].dropna()
    X = np.column_stack([np.ones(len(d)), d.x.values])
    b = np.linalg.lstsq(X, d.y.values, rcond=None)[0]
    x_t = cpi_mm.get(t, np.nan)
    note = ''
    if pd.isna(x_t):
        x_t = cpi_mm_filled.get(t, np.nan)
        note = 'core CPI m/m from Oct 2025 geometric fill'
    return b[0] + b[1] * x_t, b, len(d), note


def cleveland(t, fp_vintage):
    h = pd.read_csv(CLEV_HIST)
    r = h[h.target_month == t]
    if len(r):
        r = r.iloc[0]
        return r.core_pce_nowcast_mm, r.pce_nowcast_mm, f'last pre-release {r.last_pre_pce_date}'
    lg = pd.read_csv(CLEV_LONG)
    lg = lg[(lg.target_month == t) & (lg.nowcast_date < fp_vintage)]
    if not len(lg):
        return np.nan, np.nan, 'not available'
    c = lg[lg.series == 'core_pce'].sort_values('nowcast_date')
    hd = lg[lg.series == 'pce'].sort_values('nowcast_date')
    return c.value_pct_mm.iloc[-1], hd.value_pct_mm.iloc[-1], f'last pre-release {c.nowcast_date.iloc[-1]} (long file)'


def metrics(est, fp, est12=None, fp12=None, fp1=None):
    e = pd.Series(est, dtype=float); a = pd.Series(fp, dtype=float)
    m = e - a
    ok = m.notna()
    m = m[ok]
    n = len(m)
    if n == 0:
        return dict(n=0)
    out = dict(n=n, bias=m.mean(), mae=m.abs().mean(), se_mae=(m.abs().std(ddof=1) / np.sqrt(n)) if n > 1 else np.nan,
               rmse=np.sqrt((m ** 2).mean()), largest_miss=m.loc[m.abs().idxmax()], largest_miss_month=m.abs().idxmax())
    if fp1 is not None:
        f1 = pd.Series(fp1, dtype=float)[ok]
        out['hit_rate_1dp'] = float((round1(e[ok]) == f1.round(1)).mean())
    if est12 is not None:
        e12 = pd.Series(est12, dtype=float) - pd.Series(fp12, dtype=float)
        e12 = e12.dropna()
        out['err12_mean'] = e12.mean() if len(e12) else np.nan
        out['err12_mae'] = e12.abs().mean() if len(e12) else np.nan
        out['err12_n'] = len(e12)
    return out


def main():
    eng = Engine()
    fps = first_prints()
    cpi_mm, cpi_mm_f = core_cpi_current()

    # ---- run all windows
    lines_all, summ = [], {}
    for k in WINDOWS:
        for m in MONTHS:
            s, df = eng.estimate(m, k=k, version=table_version(m), first_release=True)
            summ[(k, m)] = s
            lines_all.append(df)
    lines = pd.concat(lines_all, ignore_index=True)

    # ---- window choice: assumed-tier total core contribution vs BEA's, rule months
    wc_rows = []
    for k in WINDOWS:
        for meas, col, colb in (('core', 'contrib_c', 'contrib_c_bea'), ('headline', 'contrib_h', 'contrib_h_bea')):
            errs = []
            for m in RULE_MONTHS:
                x = lines[(lines.window == k) & (lines.month == m) & (lines.cat == 'assumed')]
                errs.append(x[col].sum() - x[colb].sum())
            errs = np.array(errs)
            wc_rows.append(dict(window=k, measure=meas, mae_assumed_contrib_pp=np.abs(errs).mean(), bias=errs.mean(),
                                n=len(errs), months='Dec 2025 - Sep 2026'))
    wc = pd.DataFrame(wc_rows)
    wcc = wc[wc.measure == 'core'].sort_values('mae_assumed_contrib_pp')
    K = int(wcc.window.iloc[0])
    wc['chosen'] = wc.window == K
    wc['note'] = 'chosen on core; selection and test use the same months (disclosed)'
    wc.to_csv(os.path.join(OUT, 'backtest_window_choice.csv'), index=False, float_format='%.5f')

    L = lines[lines.window == K].copy()
    L.to_csv(os.path.join(OUT, 'backtest_lines.csv'), index=False, float_format='%.6f')

    # ---- per-month results
    rows = []
    for m in MONTHS:
        t = P(m)
        grp = 'rule:old-table' if m in OLD_GROUP else ('rule:current-table' if m in NEW_GROUP else 'excluded')
        x = L[L.month == m]
        parts = [q for pv in x.provenance.fillna('') for q in pv.split(' | ')]
        ppi_rev = sorted(set(q.split(':')[0] for q in parts if 'PPI revised' in q))
        flags = []
        if ppi_rev:
            flags.append('PPI revised (no first release): ' + ','.join(ppi_rev))
        if CPI_SA_REVISED_FEB2026(m):
            flags.append('CPI SA values revised Feb 2026 (current vintage used)')
        if m in ('2025-10', '2025-11'):
            flags.append('CPI Oct 2025 missing; BEA geometric fill used')
        # benchmarks
        b2, coef, nobs, b2note = bench_core_cpi_ols(eng, t, cpi_mm, cpi_mm_f)
        for meas, line in (('core', CORE_LINE), ('headline', HEADLINE_LINE)):
            fp = fps.get((meas, m))
            est = summ[(K, m)][meas]
            cur = eng.bea_mm.at[t, line]
            prev_fp = fps.get((meas, str(t - 1)))
            if prev_fp is None and m == '2023-10':
                v, lv = None, None
                df_ = alfred_obs('PCEPILFE' if meas == 'core' else 'PCEPI')
                vv = df_[df_.month == t - 1].realtime_start.min()
                lv = alfred_asof(df_, vv)
                nochange = 100 * (lv[t - 1] / lv[t - 2] - 1)
            else:
                nochange = prev_fp['mm'] if prev_fp else np.nan
            clev_c, clev_h, clev_note = cleveland(m, fp['vintage'])
            methods = {'build': est, 'bench1_no_change': nochange,
                       'bench2_core_cpi_ols': b2 if meas == 'core' else np.nan,
                       'bench3_cleveland': clev_c if meas == 'core' else clev_h}
            for meth, val in methods.items():
                est12 = 100 * (fp['L_prev'] * (1 + val / 100) / fp['L_yago'] - 1) if pd.notna(val) and pd.notna(fp['L_yago']) else np.nan
                rows.append(dict(month=m, group=grp, in_rule=m in RULE_MONTHS, measure=meas, method=meth, window=K if meth == 'build' else np.nan,
                                 table_version=table_version(m), estimate=val, first_print=fp['mm'], first_print_1dp=fp['mm1'],
                                 first_print_vintage=fp['vintage'], current_vintage=cur, miss_vs_first=val - fp['mm'],
                                 miss_vs_current=val - cur, est_1dp=float(round1(val)) if pd.notna(val) else np.nan,
                                 hit_1dp=(float(round1(val)) == round(fp['mm1'], 1)) if pd.notna(val) else np.nan,
                                 est_12m=est12, first_print_12m=fp['yy'], err_12m=est12 - fp['yy'] if pd.notna(est12) else np.nan,
                                 note=(f'OLS a={coef[0]:.4f} b={coef[1]:.4f} n={nobs} {b2note}' if meth == 'bench2_core_cpi_ols' and meas == 'core'
                                       else clev_note if meth == 'bench3_cleveland' else ''),
                                 flags='; '.join(flags) if meth == 'build' else ''))
    res = pd.DataFrame(rows)

    # ---- summary block
    groups = {'rule (Dec 2025-Sep 2026)': RULE_MONTHS, 'old table (Dec 2025-Jul 2026)': OLD_GROUP,
              'current table (Aug-Sep 2026)': NEW_GROUP, 'Nov 2025 (excluded)': ['2025-11'],
              'Oct 2023 (excluded)': ['2023-10'], 'Oct 2024 (excluded)': ['2024-10']}
    srows = []
    for gname, gm in groups.items():
        for meas in ('core', 'headline'):
            for meth in ('build', 'bench1_no_change', 'bench2_core_cpi_ols', 'bench3_cleveland'):
                x = res[(res.month.isin(gm)) & (res.measure == meas) & (res.method == meth)].set_index('month')
                if x.estimate.isna().all():
                    continue
                mt = metrics(x.estimate, x.first_print, x.est_12m, x.first_print_12m, x.first_print_1dp)
                mtc = metrics(x.estimate, x.current_vintage)
                srows.append(dict(group=gname, measure=meas, method=meth, target='first print', **mt))
                srows.append(dict(group=gname, measure=meas, method=meth, target='current vintage',
                                  **{k: v for k, v in mtc.items()}))
    summary = pd.DataFrame(srows)

    # sensitivity: all PPI revised instead of first release, rule months, chosen window
    sens = []
    for m in RULE_MONTHS:
        s, _ = eng.estimate(m, k=K, version=table_version(m), first_release=False)
        for meas in ('core', 'headline'):
            sens.append(dict(month=m, measure=meas, estimate=s[meas], first_print=fps[(meas, m)]['mm']))
    sens = pd.DataFrame(sens)
    for meas in ('core', 'headline'):
        x = sens[sens.measure == meas].set_index('month')
        mt = metrics(x.estimate, x.first_print)
        summary = pd.concat([summary, pd.DataFrame([dict(group='rule (Dec 2025-Sep 2026)', measure=meas,
                                                         method='sensitivity: build with revised PPI', target='first print', **mt)])])

    # sensitivity: other carry-forward windows (not used for the decision; window chosen by the locked rule)
    for k in WINDOWS:
        if k == K:
            continue
        for meas in ('core', 'headline'):
            e_ = pd.Series({m: summ[(k, m)][meas] for m in RULE_MONTHS})
            a_ = pd.Series({m: fps[(meas, m)]['mm'] for m in RULE_MONTHS})
            mt = metrics(e_, a_)
            summary = pd.concat([summary, pd.DataFrame([dict(group='rule (Dec 2025-Sep 2026)', measure=meas,
                                                             method=f'sensitivity: build with {k}-month carry-forward', target='first print', **mt)])])

    res['row_type'] = 'month'
    summary['row_type'] = 'summary'
    out = pd.concat([res, summary], ignore_index=True)
    out.to_csv(os.path.join(OUT, 'backtest_results.csv'), index=False, float_format='%.4f')

    # ---- attribution (diagnostic, revised): core and headline
    arows = []
    cats = ['observed_published', 'observed_needs_seasonal', 'blend', 'proxied', 'assumed']
    for m in MONTHS:
        t = P(m)
        x = L[L.month == m]
        for meas, col, colb, line in (('core', 'contrib_c', 'contrib_c_bea', CORE_LINE), ('headline', 'contrib_h', 'contrib_h_bea', HEADLINE_LINE)):
            r = dict(month=m, in_rule=m in RULE_MONTHS, measure=meas)
            for c in cats:
                xc = x[x.cat == c]
                r[f'{c}_diff'] = xc[col].sum() - xc[colb].sum()
                r[f'{c}_weight'] = xc['w_c' if meas == 'core' else 'w_h'].sum()
            r['identity_residual'] = x[colb].sum() - eng.bea_mm.at[t, line]
            fp = fps[(meas, m)]['mm']
            r['revision_current_minus_first'] = eng.bea_mm.at[t, line] - fp
            r['total_miss_vs_first'] = x[col].sum() - fp
            r['check_sum'] = sum(r[f'{c}_diff'] for c in cats) + r['identity_residual'] + r['revision_current_minus_first']
            # top 5 line-level contributors to the miss
            d = (x[col] - x[colb]).rename('d')
            top = x.assign(d=d).reindex(d.abs().sort_values(ascending=False).index).head(5)
            r['top5_lines'] = '; '.join(f"{int(a.line)}({a.cat}):{a.d:+.4f}" for a in top.itertuples())
            arows.append(r)
    att = pd.DataFrame(arows)
    att.to_csv(os.path.join(OUT, 'backtest_attribution.csv'), index=False, float_format='%.5f')

    # ---- bands
    brow = []
    rm = summary[(summary.group == 'rule (Dec 2025-Sep 2026)') & (summary.method == 'build') & (summary.target == 'first print')]
    rmse_c = float(rm[rm.measure == 'core'].rmse.iloc[0]); rmse_h = float(rm[rm.measure == 'headline'].rmse.iloc[0])
    for m in MONTHS:
        b, items = bottom_up_band(eng, L[L.month == m], m)
        brow.append(dict(month=m, band_a_core=b['band_a_c'], band_a_headline=b['band_a_h'], band_b_rmse_core=rmse_c,
                         band_b_rmse_headline=rmse_h, reported_core=max(b['band_a_c'], rmse_c), reported_headline=max(b['band_a_h'], rmse_h),
                         pm_allowance_core=b['pm_allow_c'], pm_allowance_headline=b['pm_allow_h']))
    bands = pd.DataFrame(brow)
    bands.to_csv(os.path.join(OUT, 'backtest_bands.csv'), index=False, float_format='%.5f')

    # ---- event check (lines 255, 256): data only
    ev = []
    for ln in (255, 256):
        s = eng.bea_mm[ln]
        for m in pd.period_range('2026-01', '2026-09', freq='M'):
            ev.append(dict(line=ln, name=eng.names[ln], month=str(m), mm_current_vintage=s[m],
                           sd_mm_36m_before_2026=s.loc[P('2023-01'):P('2025-12')].std(), mean_mm_36m_before_2026=s.loc[P('2023-01'):P('2025-12')].mean()))
    ev = pd.DataFrame(ev)
    ev['note'] = ('Event study against past policy-rate changes NOT done: no policy-rate change dates (e.g. FRED DFEDTARU/DFEDTARL) '
                  'are saved locally; the only local rate files are SEP projections (FEDTAR*). Data shown for reference only.')
    ev.to_csv(os.path.join(OUT, 'backtest_event_check.csv'), index=False, float_format='%.4f')

    # ---- PM sensitivity in the current-table months: old PPI-based PM instead of carry-forward
    pm = []
    for m in NEW_GROUP:
        s_new, df_new = eng.estimate(m, k=K, version='2026-09-30')
        spec_old = eng.specs('2026-02-20')[PM_LINE]
        alt = eng.price_line(spec_old, m, K, True)
        r = df_new[df_new.line == PM_LINE].iloc[0]
        pm.append(dict(month=m, pm_carry_forward=r.pi, pm_old_ppi=alt['pi'], pm_bea_current=r.pi_bea, w_c=r.w_c, w_h=r.w_h,
                       core_effect_if_old_ppi=r.w_c * (alt['pi'] - r.pi), headline_effect_if_old_ppi=r.w_h * (alt['pi'] - r.pi)))
    pd.DataFrame(pm).to_csv(os.path.join(OUT, 'backtest_pm_sensitivity.csv'), index=False, float_format='%.5f')

    for f, desc in (('backtest_results', 'per month x measure x method: estimate, first print, current vintage, misses, 1dp hit, 12m error; then summary rows (row_type=summary) with n, bias, MAE, SE of MAE, RMSE, largest miss, hit rate, 12m error by group of months and target'),
                    ('backtest_attribution', 'diagnostic and REVISED: miss vs first print split into tier differences (our contribution minus BEA current-vintage contribution), identity residual (BEA components through our aggregation minus BEA published current), and revision (current minus first print). check_sum = total miss'),
                    ('backtest_lines', 'pricing-line detail for the chosen window: pi (ours), pi_bea (current vintage), weights, contributions, provenance'),
                    ('backtest_window_choice', 'MAE of assumed-tier contribution error by window; chosen on core'),
                    ('backtest_bands', 'band (a) bottom-up quadrature per month; band (b) rule-month RMSE vs first print; reported = wider; PM allowance separate'),
                    ('backtest_event_check', 'lines 255/256 m/m; event study not possible locally'),
                    ('backtest_pm_sensitivity', 'Aug-Sep 2026: portfolio management carry-forward vs old PPI blend')):
        pd.DataFrame([('file', f + '.csv'), ('script', 'code/D_backtest.py'), ('content', desc),
                      ('units', 'percent m/m (pp for misses/contributions), SA'), ('window', f'carry-forward window chosen = {K} months'),
                      ('vintages', 'targets: ALFRED first-print vintages; current: U20404 2026-11-10; components and weights: current vintage (not real time)')],
                     columns=['field', 'value']).to_csv(os.path.join(OUT, f + '_meta.csv'), index=False)

    # ---- print
    pd.set_option('display.width', 250)
    print(wc.to_string())
    print(res[(res.method == 'build')][['month', 'measure', 'estimate', 'first_print', 'current_vintage', 'miss_vs_first', 'hit_1dp', 'err_12m']].to_string())
    print(summary[summary.target == 'first print'][['group', 'measure', 'method', 'n', 'bias', 'mae', 'se_mae', 'rmse', 'largest_miss', 'largest_miss_month', 'hit_rate_1dp', 'err12_mae']].to_string())
    print(att[att.measure == 'core'].drop(columns=[c for c in att.columns if c.endswith('_weight')]).to_string())
    print(bands.to_string())
    print(pd.DataFrame(pm).to_string())


if __name__ == '__main__':
    main()
