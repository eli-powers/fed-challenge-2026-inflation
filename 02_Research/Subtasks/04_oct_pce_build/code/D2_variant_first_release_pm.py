"""Brief D2: labeled backtest VARIANT "first-release portfolio-management PPIs". Not the decision run.

Identical to the main run in D_backtest.py (same months, same carry-forward window read from
outputs/backtest_window_choice.csv with no re-selection, same weights, seasonal treatment, fitted old-268 blend weights,
same first-print targets) except: in months priced with an old BEA table (Nov 2025; Dec 2025 - Jul 2026) the two
portfolio-management PPIs feeding line 268 (PCU5239405239401, PCU5239405239402) use the first-release m/m computed
within a single BLS PPI Detailed Report (outputs/E_pm_ppi_first_release.csv, column first_print_mm_pct) instead of
today's revised values. Existing D_ modules are imported unchanged; the swap is an in-memory subclass of Engine.

Step 1 (gate): with the swap OFF, the harness must reproduce the main run's monthly core estimates in
outputs/backtest_results.csv to 4 decimals; otherwise the script stops (exit 3) before writing anything.

Run from the project root:
    python3 "02_Research/Subtasks/04_oct_pce_build/code/D2_variant_first_release_pm.py"
Writes (new files only): outputs/D2_backtest_variant_first_release_pm.csv (+ _meta.csv),
                         outputs/D2_remaining_revised_ppi.csv (+ _meta.csv).
October 2026 is never estimated here."""
import os, sys
sys.dont_write_bytecode = True  # do not touch code/__pycache__ (frozen folder during audit)
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import Engine, P, OUT, RULE_MONTHS, table_version, first_prints, round1, PM_LINE

PM_SERIES = ('PCU5239405239401', 'PCU5239405239402')
E_FILE = os.path.join(OUT, 'E_pm_ppi_first_release.csv')
SWAP_MONTHS = ['2025-11'] + [str(p) for p in pd.period_range('2025-12', '2026-07', freq='M')]  # old-table months
MONTHS = RULE_MONTHS + ['2025-11']
F_MAIN = os.path.join(OUT, 'D2_backtest_variant_first_release_pm.csv')
F_REM = os.path.join(OUT, 'D2_remaining_revised_ppi.csv')


class PMSwapEngine(Engine):
    """Engine whose series_mm returns the first-release (same-report) m/m for the two PM PPIs in SWAP_MONTHS
    when swap=True. With swap=False it is the unmodified Engine."""

    def __init__(self, swap):
        super().__init__()
        self.swap = swap
        e = pd.read_csv(E_FILE, dtype={'reference_month': str})
        self.pm_fr = {(r.series_id, r.reference_month): float(r.first_print_mm_pct) for r in e.itertuples()}

    def series_mm(self, sid, t, first_release=True):
        if self.swap and first_release and sid in PM_SERIES and str(P(t)) in SWAP_MONTHS:
            k = (sid, str(P(t)))
            if k not in self.pm_fr:
                raise KeyError(f'first-release PM value missing for {k}')
            return self.pm_fr[k], 'PPI first release (BLS Detailed Report, same-report m/m; D2 swap)'
        return super().series_mm(sid, t, first_release)


def metrics(est, fp, fp1):
    e, a, f1 = (pd.Series(x, dtype=float) for x in (est, fp, fp1))
    m = e - a
    n = len(m)
    mae = m.abs().mean()
    se = m.abs().std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
    i = m.abs().idxmax()
    return dict(n=n, bias=m.mean(), mae=mae, se_mae=se, mae_lo=mae - se, mae_hi=mae + se, rmse=np.sqrt((m ** 2).mean()),
                largest_miss=m[i], largest_miss_month=i, hit_rate_1dp=float((round1(e) == f1.round(1)).mean()))


def threshold_leg(lo, hi, thr=0.05):
    if hi < thr:
        return 'pass'
    if lo > thr:
        return 'fail'
    return 'inconclusive'


def main():
    wc = pd.read_csv(os.path.join(OUT, 'backtest_window_choice.csv'))
    K = int(wc[wc.chosen & (wc.measure == 'core')].window.iloc[0])
    fps = first_prints()
    main_res = pd.read_csv(os.path.join(OUT, 'backtest_results.csv'))
    mb = main_res[(main_res.row_type == 'month') & (main_res.method == 'build')]

    base, var = PMSwapEngine(swap=False), PMSwapEngine(swap=True)

    # ---- step 1: reproduction gate (swap off) against the saved main run
    est0, lines0 = {}, {}
    rep = []
    for m in MONTHS:
        s, df = base.estimate(m, k=K, version=table_version(m), first_release=True)
        est0[m], lines0[m] = s, df
        for meas in ('core', 'headline'):
            saved = float(mb[(mb.month == m) & (mb.measure == meas)].estimate.iloc[0])
            rep.append(dict(month=m, measure=meas, harness=s[meas], saved=saved, diff=s[meas] - saved,
                            match_4dp=round(s[meas], 4) == round(saved, 4)))
    rep = pd.DataFrame(rep)
    print('Reproduction check (swap off vs outputs/backtest_results.csv, build, window', K, ')')
    print(rep.to_string())
    rc = rep[rep.measure == 'core']
    print(f'max |diff| core = {rc["diff"].abs().max():.2e}; headline = {rep[rep.measure == "headline"]["diff"].abs().max():.2e}')
    if not rc.match_4dp.all():
        print('REPRODUCTION FAILED: core estimates do not match to 4 decimals. Stopping; nothing written.')
        sys.exit(3)

    # ---- step 2: variant
    rows = []
    rem = []
    for m in MONTHS:
        s1, df1 = var.estimate(m, k=K, version=table_version(m), first_release=True)
        s0, df0 = est0[m], lines0[m]
        pm1 = df1[df1.line == PM_LINE].iloc[0]; pm0 = df0[df0.line == PM_LINE].iloc[0]
        for meas in ('core', 'headline'):
            fp = fps[(meas, m)]
            rows.append(dict(row_type='month', month=m, in_rule=m in RULE_MONTHS, table_version=table_version(m),
                             pm_swapped=m in SWAP_MONTHS, measure=meas, window=K,
                             est_main=s0[meas], est_variant=s1[meas], variant_minus_main=s1[meas] - s0[meas],
                             first_print=fp['mm'], first_print_1dp=fp['mm1'], first_print_vintage=fp['vintage'],
                             miss_main=s0[meas] - fp['mm'], miss_variant=s1[meas] - fp['mm'],
                             est_main_1dp=float(round1(s0[meas])), est_variant_1dp=float(round1(s1[meas])),
                             hit_main=float(round1(s0[meas])) == round(fp['mm1'], 1),
                             hit_variant=float(round1(s1[meas])) == round(fp['mm1'], 1),
                             pm_pi_main=pm0.pi, pm_pi_variant=pm1.pi, pm_weights=pm1.weights,
                             pm_w=pm1.w_c if meas == 'core' else pm1.w_h, pm_provenance_variant=pm1.provenance))
        # remaining revised PPIs in the variant
        for r in df1.itertuples():
            for q in str(r.provenance).split(' | '):
                if 'PPI revised' in q:
                    rem.append(dict(month=m, in_rule=m in RULE_MONTHS, series_id=q.split(':')[0], line=int(r.line),
                                    leaf=int(r.leaf), line_name=r.name, w_c=r.w_c, w_h=r.w_h))
    res = pd.DataFrame(rows)

    # ---- summary block
    summ = []
    for gname, gm in (('rule (Dec 2025-Sep 2026)', RULE_MONTHS), ('Nov 2025 (excluded)', ['2025-11'])):
        for meas in ('core', 'headline'):
            x = res[(res.month.isin(gm)) & (res.measure == meas)].set_index('month')
            for run, col in (('main', 'est_main'), ('variant', 'est_variant')):
                mt = metrics(x[col], x.first_print, x.first_print_1dp)
                mt['threshold_leg_core_rule'] = threshold_leg(mt['mae_lo'], mt['mae_hi']) if (meas == 'core' and gm is RULE_MONTHS) else ''
                summ.append(dict(row_type='summary', group=gname, measure=meas, run=run, **mt))
            if len(gm) > 1:
                d = (x.miss_variant.abs().mean() - x.miss_main.abs().mean())
                summ.append(dict(row_type='summary', group=gname, measure=meas, run='variant minus main', mae=d, n=len(x)))
    summ = pd.DataFrame(summ)
    out = pd.concat([res, summ], ignore_index=True)
    out.to_csv(F_MAIN, index=False, float_format='%.4f')

    rem = pd.DataFrame(rem)
    rem.to_csv(F_REM, index=False, float_format='%.6f')
    rr = rem[rem.in_rule]
    rem_s = rr.groupby('series_id').agg(rule_months_affected=('month', 'nunique'), lines=('line', lambda s: ';'.join(map(str, sorted(set(s))))),
                                        w_c_mean=('w_c', 'mean'), w_h_mean=('w_h', 'mean')).reset_index()

    for f, desc in ((F_MAIN, 'D2 variant: line 268 in old-table months (Nov 2025, Dec 2025-Jul 2026) priced from first-release '
                             'same-report m/m of PCU5239405239401/02 (E_pm_ppi_first_release.csv); everything else = main run. '
                             'row_type=month: core/headline estimate main vs variant, first print, misses, 1dp hits, PM line detail; '
                             'row_type=summary: n, bias, MAE, SE of MAE (SD |miss| / sqrt n, ddof=1), MAE +/- 1 SE, RMSE, largest miss, '
                             '1dp hit rate, threshold leg (core, rule months; MAE+/-1SE vs 0.05), and variant-minus-main MAE'),
                    (F_REM, 'PPI inputs still priced from revised (current) data in the variant, by month, line, and line weight '
                            '(w_c core-share, w_h headline-share of the pricing line)')):
        base_name = os.path.basename(f)[:-4]
        pd.DataFrame([('file', base_name + '.csv'), ('script', 'code/D2_variant_first_release_pm.py'), ('content', desc),
                      ('units', 'percent m/m (pp for misses), SA; weights are shares'), ('window', f'carry-forward window = {K} months (from backtest_window_choice.csv, not re-selected)'),
                      ('reproduction', f'swap off reproduces backtest_results.csv build estimates; max |diff| core {rc["diff"].abs().max():.2e}'),
                      ('vintages', 'targets: ALFRED first-print vintages; components and weights: current vintage (not real time); PM PPIs: BLS Detailed Reports, first-release'),
                      ('status', 'labeled variant; NOT the decision run; no Oct 2026 estimate')],
                     columns=['field', 'value']).to_csv(os.path.join(OUT, base_name + '_meta.csv'), index=False)

    pd.set_option('display.width', 250)
    print(res[['month', 'measure', 'est_main', 'est_variant', 'variant_minus_main', 'first_print', 'miss_main', 'miss_variant',
               'hit_main', 'hit_variant', 'pm_pi_main', 'pm_pi_variant', 'pm_w']].to_string())
    print(summ.to_string())
    print(rem_s.to_string())
    print(rr.groupby(['series_id', 'line']).month.apply(lambda s: ','.join(sorted(s))).to_string())


if __name__ == '__main__':
    main()
