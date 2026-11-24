"""Coordinator extras for GO items added on Nov 15 (after the briefs were written).

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/Z_coordinator_extras.py"
Writes outputs/Z_q4b_ex_oer_breadth.csv  (Q4b optional: breadth on core ex OER, Eli's "harmonized PCE" scope)
       outputs/Z_q5_atlanta_panel.csv     (Q5 reference panel: Atlanta Fed sticky/flexible CPI, published rates, 2025-01 .. 2026-10)
Engine: 09_slide1_research/code/C_common.py (read-only). Reproduction checks asserted first.
"""
import os
import sys

import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

for (m, b), want in {('2026-09', 12): 60.626, ('2026-10', 12): 54.038, ('2026-09', 3): 44.814, ('2026-10', 3): 45.467}.items():
    assert abs(cc.breadth('leaf', 'core', m, b)[0] - want) < 0.01

# ---- Q4b optional: core ex OER (leaf whose BEA name is owner-occupied imputed rent)
names = {}
for r in cc.dc.json.load(open(os.path.join(ROOT, cc.U20404_REL)))['BEAAPI']['Results']['Data'] if hasattr(cc.dc, 'json') else []:
    names.setdefault(int(r['LineNumber']), r['LineDescription'])
if not names:
    import json
    for r in json.load(open(os.path.join(ROOT, cc.U20404_REL)))['BEAAPI']['Results']['Data']:
        names.setdefault(int(r['LineNumber']), r['LineDescription'])
oer = [l for l in cc.LEAVES_CORE if 'owner-occupied' in names.get(l, '').lower()]
assert len(oer) >= 1, 'OER leaf not found'
rows = []
for scope_name, leaves in (('core', set(cc.LEAVES_CORE)), ('core ex OER (harmonized)', set(cc.LEAVES_CORE) - set(oer)),
                           ('core ex OER ex hospitals 184-186', set(cc.LEAVES_CORE) - set(oer) - {184, 185, 186})):
    for m in ('2025-09', '2026-02', '2026-09', '2026-10'):
        for back, hz in ((12, '12m'), (3, '3m_ann')):
            d = cc.unit_table('leaf', leaves, m, back)
            rows.append(dict(scope=scope_name, period=m, status='estimate' if m == '2026-10' else 'BEA published', horizon=hz,
                             breadth_pct=round(100 * d.w[d.r > 3].sum() / d.w.sum(), 3), n_leaves=len(d),
                             oer_leaves=';'.join(f'{l} {names[l]}' for l in oer), vintage='BEA U20404/U20405 2026-11-10; 2026-10 = UMD est.'))
    pre = []
    for y in (2018, 2019):
        for mo in range(1, 13):
            d = cc.unit_table('leaf', leaves, f'{y}-{mo:02d}', 12)
            pre.append(100 * d.w[d.r > 3].sum() / d.w.sum())
    rows.append(dict(scope=scope_name, period='avg 2018-19', status='BEA published', horizon='12m', breadth_pct=round(sum(pre) / len(pre), 3),
                     n_leaves=len(leaves), oer_leaves=';'.join(str(l) for l in oer), vintage='BEA U20404/U20405 2026-11-10'))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'Z_q4b_ex_oer_breadth.csv'), index=False)

# ---- Q5 reference panel: Atlanta Fed published sticky/flexible rates
RAW = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'Sticky CPI', 'raw', 'atlantafed_sticky_price_cpi_2026-11-10.xlsx')
ws = openpyxl.load_workbook(RAW, read_only=True, data_only=True)['Data']
it = ws.iter_rows(values_only=True)
hdr = next(it)
series = {'Flexible CPI': 1, 'Core Flexible CPI': 5, 'Sticky CPI': 9, 'Core Sticky CPI': 13}
out = []
for r in it:
    if r[0] is None or not hasattr(r[0], 'year'):
        continue
    ym = f'{r[0].year}-{r[0].month:02d}'
    if ym < '2025-01':
        continue
    for name, c in series.items():
        out.append(dict(month=ym, series=name, mm_1m_ann_pct=r[c + 1], ann3m_pct=r[c + 2], yoy_12m_pct=r[c + 3],
                        source=f'{os.path.relpath(RAW, ROOT)}, sheet Data, columns "{hdr[c]}" +1..+3 (publisher-reported rates)'))
p = pd.DataFrame(out)
p.to_csv(os.path.join(OUT, 'Z_q5_atlanta_panel.csv'), index=False)
f = p[(p.series == 'Flexible CPI') & p.month.isin(['2026-08', '2026-09', '2026-10'])]
print(f[['month', 'mm_1m_ann_pct']].to_string(index=False))
print(pd.DataFrame(rows)[lambda x: x.period.isin(['2026-09', '2026-10', 'avg 2018-19'])].to_string(index=False))
