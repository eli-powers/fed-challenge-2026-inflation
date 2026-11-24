"""Task 2: mapping validation.
For each pricing line with a source series: correlation and gap between the source m/m (treated per BEA's
seasonal status; SA by BEA -> NSA + method-B factor from prior years only) and BEA's own component m/m
(U20404, current vintage 2026-11-10), Jan 2024 - Sep 2026. Revised (current-vintage) source data throughout.
Current table (2026-09-30) specs for all lines; old-table specs added for the lines that changed (50, 211, 268, 299, 305).
Flag rule (set before results): corr < 0.5, or |mean gap| > 0.05 pp/month, or MAE gap > 0.5 pp/month.
The mapping is NOT changed; proposed changes are listed in notes_D.md.
Output: outputs/mapping_validation.csv (+ _meta.csv)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import pandas as pd
from D_common import Engine, P, OUT

MONTHS = pd.period_range('2024-01', '2026-09', freq='M')


def validate(eng, spec, label):
    ln = spec['line']
    bl = 156 if ln == 157 else ln
    src, bea = [], []
    for t in MONTHS:
        s = eng.source_treated(spec, t, first_release=False)
        src.append(s['value']); bea.append(eng.bea_mm.at[t, bl])
    d = pd.DataFrame({'src': src, 'bea': bea}, index=MONTHS).dropna()
    n = len(d)
    r = dict(pricing_bea_line=ln, leaf_bea_line=spec['leaf'], name=spec['name'], spec=label, tier=spec['tier'],
             seasonal_treatment=spec['seasonal'], inputs=';'.join(s for s, _ in spec['inputs']), n_months=n)
    if n >= 6:
        g = d.src - d.bea
        r.update(corr=d.src.corr(d.bea), mean_gap_pp=g.mean(), mae_gap_pp=g.abs().mean(), rmse_gap_pp=np.sqrt((g ** 2).mean()),
                 sd_bea=d.bea.std(), sd_src=d.src.std(), largest_gap_pp=g.loc[g.abs().idxmax()], largest_gap_month=str(g.abs().idxmax()))
        fl = []
        if not (r['corr'] >= 0.5):
            fl.append('corr<0.5')
        if abs(r['mean_gap_pp']) > 0.05:
            fl.append('|mean gap|>0.05')
        if r['mae_gap_pp'] > 0.5:
            fl.append('MAE gap>0.5')
        r['flag'] = ';'.join(fl)
    else:
        r['flag'] = 'too few months with source data'
    return r


def main():
    eng = Engine()
    wsep = eng.bea_n.loc[P('2026-09')] / eng.bea_n.at[P('2026-09'), 1]
    rows = []
    cur = eng.specs('2026-09-30')
    for ln, s in cur.items():
        if not s['inputs']:
            continue
        rows.append(validate(eng, s, 'current table 2026-09-30'))
    old = eng.specs('2026-02-20')
    for ln in (50, 211, 268, 299, 305):
        rows.append(validate(eng, old[ln], 'old table 2026-02-20'))
    r = pd.DataFrame(rows)
    r['share_of_pce_sep2026'] = [wsep.get(156 if l == 157 else l, np.nan) for l in r.pricing_bea_line]
    r = r.sort_values(['flag', 'share_of_pce_sep2026'], ascending=[False, False])
    r.to_csv(os.path.join(OUT, 'mapping_validation.csv'), index=False, float_format='%.4f')
    pd.DataFrame([
        ('file', 'mapping_validation.csv'), ('script', 'code/D_mapping_validation.py'),
        ('window', 'Jan 2024 - Sep 2026 (months with both values)'),
        ('source', 'component_series_history.csv (current vintage, Oct 2025 CPI geometric fill), BEA U20404 2026-11-10'),
        ('units', 'percent m/m; gaps = source minus BEA, pp'),
        ('seasonal', 'SA -> BLS SA; NSA -> unadjusted; SA by BEA -> NSA + method B (prior years only)'),
        ('flag_rule', 'corr<0.5 or |mean gap|>0.05 or MAE gap>0.5 (set before results)'),
        ('share', 'nominal share of total PCE, Sep 2026 (line 157 shown with leaf 156)')], columns=['field', 'value']).to_csv(
        os.path.join(OUT, 'mapping_validation_meta.csv'), index=False)
    print(r[['pricing_bea_line', 'name', 'spec', 'n_months', 'corr', 'mean_gap_pp', 'mae_gap_pp', 'share_of_pce_sep2026', 'flag']]
          .to_string(max_colwidth=40))


if __name__ == '__main__':
    main()
