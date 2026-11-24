"""Task 1 (gate): aggregation identity test.
Feed BEA's own current-vintage component m/m (U20404, vintage 2026-11-10) through the locked aggregation
(previous-month nominal shares from U20405; 177 covered leaves; lines 145 and 333 left out and weights rescaled)
and compare with BEA's published current-vintage headline (line 1) and core (line 374) m/m.
Variants:
  A  leaf level, locked formula (sum of w_{t-1} * pi_leaf)
  B  pricing-line level: parent leaves rolled up from their sub-lines with previous-month within-leaf shares
     (tenant rent 156 = 100% CPI rent; NPISH 342 at leaf level), locked formula
  F  diagnostic only: Fisher formula on the same leaves (geometric mean of Laspeyres with t-1 shares and
     Paasche with t shares), to separate formula error from weight/coverage error.
  C  diagnostic only: locked formula, full coverage: the two excluded net lines (145, 333) entered through their
     gross components with signed weights (+146, -149, +334, -338), shares over BEA's own line-1 / line-374 totals.
  CF diagnostic only: Fisher formula with that full coverage.
Output: outputs/identity_test.csv (+ _meta.csv)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import Engine, P, OUT, RULE_MONTHS, EXTRA_MONTHS, HEADLINE_LINE, CORE_LINE, table_version


def fisher(eng, t, leaves):
    t = P(t)
    rel = (eng.bea_p.loc[t, leaves] / eng.bea_p.loc[t - 1, leaves])
    s0 = eng.bea_n.loc[t - 1, leaves]; s0 = s0 / s0.sum()
    s1 = eng.bea_n.loc[t, leaves]; s1 = s1 / s1.sum()
    las = (s0 * rel).sum()
    paa = 1.0 / (s1 / rel).sum()
    return 100 * (np.sqrt(las * paa) - 1), 100 * (las - 1)


GROSS = {146: 1, 149: -1, 334: 1, 338: -1}


def full_cov(eng, t, core):
    t = P(t)
    base = [l for l in eng.leaves if (eng.leaf_core[l] or not core)]
    tot_line = CORE_LINE if core else HEADLINE_LINE
    lines = base + list(GROSS)
    sg = pd.Series({l: GROSS.get(l, 1) for l in lines})
    n0 = eng.bea_n.loc[t - 1, lines] * sg / eng.bea_n.at[t - 1, tot_line]
    n1 = eng.bea_n.loc[t, lines] * sg / eng.bea_n.at[t, tot_line]
    rel = eng.bea_p.loc[t, lines] / eng.bea_p.loc[t - 1, lines]
    las = (n0 * rel).sum() / n0.sum()
    paa = n1.sum() / (n1 / rel).sum()
    return 100 * (las - 1), 100 * (np.sqrt(las * paa) - 1), n0.sum()


def main():
    eng = Engine()
    months = sorted(set(RULE_MONTHS + EXTRA_MONTHS + [str(p) for p in pd.period_range('2024-01', '2026-09', freq='M')]))
    rows = []
    for m in months:
        t = P(m)
        wh, wc = eng.leaf_weights(t)
        pi_leaf = eng.bea_mm.loc[t, eng.leaves]
        A_h, A_c = (wh * pi_leaf).sum(), (wc * pi_leaf).sum()
        _, df = eng.estimate(t, k=6, version=table_version(t))
        B_h, B_c = df.contrib_h_bea.sum(), df.contrib_c_bea.sum()
        core_leaves = [l for l in eng.leaves if eng.leaf_core[l]]
        F_h, L_h = fisher(eng, t, eng.leaves)
        F_c, L_c = fisher(eng, t, core_leaves)
        pub_h, pub_c = eng.bea_mm.at[t, HEADLINE_LINE], eng.bea_mm.at[t, CORE_LINE]
        C_h, CF_h, cov_h = full_cov(eng, t, False)
        C_c, CF_c, cov_c = full_cov(eng, t, True)
        rows.append(dict(month=m, in_rule=m in RULE_MONTHS, published_headline=pub_h, published_core=pub_c,
                         A_leaf_headline=A_h, A_leaf_core=A_c, gapA_headline=A_h - pub_h, gapA_core=A_c - pub_c,
                         B_subline_headline=B_h, B_subline_core=B_c, gapB_headline=B_h - pub_h, gapB_core=B_c - pub_c,
                         F_fisher_headline=F_h, F_fisher_core=F_c, gapF_headline=F_h - pub_h, gapF_core=F_c - pub_c,
                         C_full_headline=C_h, C_full_core=C_c, gapC_headline=C_h - pub_h, gapC_core=C_c - pub_c,
                         gapCF_headline=CF_h - pub_h, gapCF_core=CF_c - pub_c, fullcov_share_h=cov_h, fullcov_share_c=cov_c,
                         excluded_share_prev_month=(eng.bea_n.at[t - 1, 145] + eng.bea_n.at[t - 1, 333]) / eng.bea_n.at[t - 1, HEADLINE_LINE]))
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(OUT, 'identity_test.csv'), index=False, float_format='%.5f')
    meta = pd.DataFrame([
        ('file', 'identity_test.csv'), ('script', 'code/D_identity_test.py'),
        ('inputs', 'U20404 and U20405, vintage 2026-11-10 (current); component_mapping.csv'),
        ('units', 'percent m/m, SA (BEA Fisher indexes); gaps in pp = aggregate minus published'),
        ('variants', 'A leaf-level locked formula; B sub-line roll-up locked formula (as used by the build); F Fisher diagnostic; C locked formula with the excluded net lines entered via gross components (+146 -149 +334 -338); CF Fisher with that coverage'),
        ('coverage', '177 leaves (99.70% of PCE); lines 145 and 333 (0.30%) excluded and weights rescaled'),
        ('caveat', 'current vintage only; not a real-time test')], columns=['field', 'value'])
    meta.to_csv(os.path.join(OUT, 'identity_test_meta.csv'), index=False)
    for col in ['gapA_headline', 'gapA_core', 'gapB_headline', 'gapB_core', 'gapF_headline', 'gapF_core', 'gapC_headline', 'gapC_core',
                'gapCF_headline', 'gapCF_core']:
        x = r[col]; xr = r.loc[r.in_rule, col]
        print(f'{col:15s} all: max|gap| {x.abs().max():.4f} ({r.loc[x.abs().idxmax(), "month"]}) mean {x.mean():+.4f} | '
              f'rule months: max|gap| {xr.abs().max():.4f} mean {xr.mean():+.4f}')


if __name__ == '__main__':
    main()
