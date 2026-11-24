"""A_r5_cleveland.csv: Cleveland Fed Oct 2026 nowcast path (core and headline PCE; m/m and y/y) as pulled 2026-11-14.
Source: 04_oct_pce_build/outputs/R_cleveland_oct2026_2026-11-14.csv; cross-checked against raw JSON in 03_Data/Raw."""
import sys, json
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *

src = rd(f'{BUILD}/R_cleveland_oct2026_2026-11-14.csv')
LABEL = 'carried forward: Nov 14 pull; re-pull Nov 18'
rows = []
last = src[-1]['nowcast_date']
for r in src:
    for meas, mmc, yyc in (('core', 'core_pce_mm', 'core_pce_yy'), ('headline', 'pce_mm', 'pce_yy')):
        rows.append(dict(nowcast_date=r['nowcast_date'], target_month='2026-10', measure=meas,
                         mm_pct=f'{float(r[mmc]):.4f}', yy_pct=f'{float(r[yyc]):.4f}', is_latest='yes' if r['nowcast_date'] == last else '',
                         label=LABEL, series_name='Cleveland Fed Inflation Nowcasting: ' + ('Core PCE Inflation' if meas == 'core' else 'PCE Inflation'),
                         units_sa='m/m % (monthly rate, not annualized, as in nowcast_month.json) and y/y %; Cleveland does not label SA; no PPI input',
                         vintage='pulled 2026-11-14; chart updated 2026-11-13 (value unchanged since 2026-11-10 update, which followed Oct CPI)',
                         source='02_Research/Subtasks/04_oct_pce_build/outputs/R_cleveland_oct2026_2026-11-14.csv',
                         raw_file='03_Data/Raw/ClevelandFed_nowcast_month_2026-11-14.json; ClevelandFed_nowcast_year_2026-11-14.json',
                         basis='model nowcast, no PPI'))
cols = ['nowcast_date', 'target_month', 'measure', 'mm_pct', 'yy_pct', 'is_latest', 'label', 'series_name', 'units_sa', 'vintage', 'source', 'raw_file', 'basis']
write_csv(f'{OUT}/A_r5_cleveland.csv', rows, cols)
# cross-check latest against raw JSON
def latest(kind):
    d = json.load(open(f'{ROOT}/03_Data/Raw/ClevelandFed_nowcast_{kind}_2026-11-14.json'))
    for e in d:
        y, m = e['chart']['subcaption'].split('-')
        if f'{int(y):04d}-{int(m):02d}' == '2026-10':
            out = {}
            for ds in e['dataset']:
                vals = [(v['tooltext'].split('{br}')[1], float(v['value'])) for v in ds['data'] if v['value'] != '']
                if ds['seriesname'] in ('Core PCE Inflation', 'PCE Inflation'):
                    out[ds['seriesname']] = vals[-1]
            return e['chart'].get('_comment', '')[:40], out
for k in ('month', 'year'):
    print(k, latest(k))
print('csv latest:', {r['measure']: (r['mm_pct'], r['yy_pct']) for r in rows if r['is_latest']})
