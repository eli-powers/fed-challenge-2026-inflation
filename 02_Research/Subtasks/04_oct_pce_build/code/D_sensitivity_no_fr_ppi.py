"""Coordinator-added sensitivity: "no first-release PPI as assumed".
The 8 PPI series ALFRED does not carry at first release are treated as unavailable, so any pricing line using one of
them falls to the assumed tier (carry-forward of BEA's own m/m) for that month. Everything else is identical to the
main run in D_backtest.py: same months, the carry-forward window chosen in the main run (read from
outputs/backtest_window_choice.csv, not re-selected), same weights and seasonal treatment.
Not used for the decision rule. Run D_backtest.py first.
Output: outputs/backtest_sensitivity_no_first_release_ppi.csv (+ _meta.csv)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import Engine, OUT, RULE_MONTHS, table_version, first_prints

NO_FR = ['PCU5239405239401', 'PCU5239405239402', 'PCU5231505231501011', 'PCU5231505231501012', 'PCU523150523150102',
         'PCU5231505231502011', 'PCU5231505231502012', 'PCU5132105132107']


def stats(miss):
    m = pd.Series(miss)
    return dict(n=len(m), mae=m.abs().mean(), se_mae=m.abs().std(ddof=1) / np.sqrt(len(m)), bias=m.mean(), rmse=np.sqrt((m ** 2).mean()))


def main():
    wc = pd.read_csv(os.path.join(OUT, 'backtest_window_choice.csv'))
    K = int(wc[wc.chosen & (wc.measure == 'core')].window.iloc[0])
    fps = first_prints()
    base, sens = Engine(), Engine()
    sens.force_missing = set(NO_FR)
    rows = []
    for m in RULE_MONTHS:
        s0, _ = base.estimate(m, k=K, version=table_version(m))
        s1, d1 = sens.estimate(m, k=K, version=table_version(m))
        lines = sorted(d1[d1.provenance.fillna('').str.contains('sensitivity run')].line.astype(int).tolist())
        for meas in ('core', 'headline'):
            fp = fps[(meas, m)]['mm']
            rows.append(dict(row_type='month', month=m, measure=meas, window=K, est_main=s0[meas], est_sensitivity=s1[meas],
                             diff_sens_minus_main=s1[meas] - s0[meas], first_print=fp, miss_main=s0[meas] - fp,
                             miss_sensitivity=s1[meas] - fp, lines_moved_to_assumed=';'.join(map(str, lines))))
    r = pd.DataFrame(rows)
    summ = []
    for meas in ('core', 'headline'):
        x = r[r.measure == meas]
        a, b = stats(x.miss_main), stats(x.miss_sensitivity)
        summ.append(dict(row_type='summary', month='Dec 2025 - Sep 2026', measure=meas, window=K,
                         n=a['n'], mae_main=a['mae'], se_mae_main=a['se_mae'], bias_main=a['bias'], rmse_main=a['rmse'],
                         mae_sensitivity=b['mae'], se_mae_sensitivity=b['se_mae'], bias_sensitivity=b['bias'], rmse_sensitivity=b['rmse'],
                         mae_diff_sens_minus_main=b['mae'] - a['mae']))
    out = pd.concat([r, pd.DataFrame(summ)], ignore_index=True)
    out.to_csv(os.path.join(OUT, 'backtest_sensitivity_no_first_release_ppi.csv'), index=False, float_format='%.5f')
    pd.DataFrame([('file', 'backtest_sensitivity_no_first_release_ppi.csv'), ('script', 'code/D_sensitivity_no_fr_ppi.py'),
                  ('content', 'main run vs run with the 8 PPIs lacking ALFRED first-release history treated as missing (line -> assumed)'),
                  ('series', ';'.join(NO_FR)), ('window', f'{K} months, from the main run (not re-selected)'),
                  ('months', 'Dec 2025 - Sep 2026 (rule months)'), ('target', 'BEA first print m/m, percent; misses in pp'),
                  ('status', 'labeled sensitivity; NOT used for the decision rule'),
                  ('judgment', 'a blend with one such input (line 50 software, Aug-Sep 2026) moves to assumed as a whole, per the missing-source rule')],
                 columns=['field', 'value']).to_csv(os.path.join(OUT, 'backtest_sensitivity_no_first_release_ppi_meta.csv'), index=False)
    pd.set_option('display.width', 250)
    print(out.to_string())


if __name__ == '__main__':
    main()
