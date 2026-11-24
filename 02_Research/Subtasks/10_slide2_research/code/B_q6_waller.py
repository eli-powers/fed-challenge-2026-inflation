"""Brief B, Q6: Waller (Nov 10) comparison. Pulls every core-services 12m variant from slide 1 outputs
(09_slide1_research/outputs/C_waller_variants.csv); recomputes the count and weighted variants through the audited engine
(C_common.count_share / unit_table) and asserts they match. Marks the weighted leaf share as Eli's preferred basis.

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/B_q6_waller.py"
Writes outputs/B_q6_waller.csv
"""
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
SRC = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'outputs', 'C_waller_variants.csv')
QUOTE = ('Waller, Nov 10 2026: "More than 70 percent of the components of core PCE service prices saw 12-month increases '
         'above 3 percent in September."')

w = pd.read_csv(SRC)
w = w[w.scope.isin(['core_services', 'supercore'])].copy()
periods = sorted(w.period.unique())
assert periods == ['2026-09', '2026-10'], periods       # Oct est. already present in the slide 1 file: confirmed

# recompute count and start-of-window weighted variants through the same engine
for _, r in w.iterrows():
    g = 'leaf' if r.method == 'leaf' else 'sub'
    d = cc.unit_table(g, cc.SCOPES[r.scope], r.period, 12)
    above = d.r > 3
    if r.variant == 'count (unweighted)':
        v = 100 * above.mean()
    elif r.variant.startswith('weight: start'):
        v = 100 * d.w[above].sum() / d.w.sum()
    elif r.variant.startswith('count, ex housing leaves'):
        v = 100 * above[~d.leaf.between(153, 164)].mean()
    elif r.variant.startswith('count, ex housing and ex NPISH'):
        nh = ~d.leaf.between(153, 164)
        v = 100 * above[nh & (d.leaf != 342)].mean()
    elif r.variant.startswith('weight: latest'):
        wend = pd.Series([cc.nominal_weight(l, lf, cc.SEP, g) for l, lf in zip(d.line, d.leaf)], index=d.index)
        v = 100 * wend[above].sum() / wend.sum()
    assert abs(v - r.value_pct) < 0.0006, (r.variant, r.period, r.method, v, r.value_pct)
    w.loc[_, 'n_above'] = int(above.sum()) if r.variant.startswith('count (') else None

w['preferred_basis'] = (w.scope.eq('core_services') & w.method.eq('leaf') & w.variant.str.startswith('weight: start'))
w['preferred_label'] = w.preferred_basis.map({True: "Eli's preferred basis (weighted leaf, start-of-window)", False: ''})
w['source_file'] = '09_slide1_research/outputs/C_waller_variants.csv (pulled; recomputed via C_common and matched to 0.0006)'
w['horizon'] = '12m'
w['vintage'] = 'BEA U20404/U20405 vintage 2026-11-10; 2026-10 = est. (UMD October build)'
w['waller_quote'] = QUOTE
w = w[['period', 'status', 'scope', 'method', 'horizon', 'n_units', 'variant', 'value_pct', 'n_above', 'exceeds_70', 'preferred_basis',
       'preferred_label', 'source_file', 'vintage', 'waller_quote']]
w.to_csv(os.path.join(OUT, 'B_q6_waller.csv'), index=False)
pd.set_option('display.width', 250)
print(w.drop(columns=['source_file', 'vintage', 'waller_quote']).to_string())
