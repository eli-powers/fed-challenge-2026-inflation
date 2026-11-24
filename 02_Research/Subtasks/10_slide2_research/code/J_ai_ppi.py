"""J: AI-related upstream PPI basket (Richmond Fed Macro Minute, O'Trakoun, Jun 30 2026, "AI's Imprint on Prices and Inflation",
plus Eli's list). Producer prices, NOT addable to the PCE AI basket (no consumer weights): upstream evidence only.

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/J_ai_ppi.py" [--fetch]
--fetch pulls BLS API v2 (key from .env) into 03_Data/Raw/BLS_PPI_ai_basket_2026-11-16/.
All series NSA (BLS publishes these industry indexes NSA), so y/y is the headline measure; m/m shown for reference.
Writes outputs/J_ai_ppi_summary.csv and outputs/J_ai_ppi_monthly.csv.
"""
import glob
import json
import os
import sys
import urllib.request

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RAW = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_ai_basket_2026-11-16')
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
SERIES = [
    ('PCU33441-33441-', 'Semiconductor and other electronic component mfg', 'Richmond Fig.1; Eli'),
    ('PCU334413334413', 'Semiconductor and related device mfg (narrower chip measure)', 'Eli'),
    ('PCU3341--3341--', 'Computer and peripheral equipment mfg', 'Richmond Fig.1; Eli'),
    ('PCU334112334112', 'Computer storage device mfg', 'Eli'),
    ('PCU334418334418', 'Printed circuit assembly mfg', 'Eli'),
    ('PCU335313335313', 'Switchgear and switchboard apparatus mfg', 'Richmond Fig.2; Eli'),
    ('PCU3336--3336--', 'Turbine and power transmission equipment mfg', 'Richmond Fig.2 (engine, turbine, power transmission)'),
    ('PCU51321051321050502', 'Application software publishing', 'Richmond Fig.3; Eli'),
    ('PCU5182105182105', 'Hosting, ASP and other IT infrastructure provisioning', 'Eli'),
    ('PCU541330541330202', 'Municipal utility and power generation/distribution engineering', 'Richmond Fig.3 (grid engineering)'),
]


def fetch():
    key = None
    for line in open(os.path.expanduser('.env')):
        if line.strip().startswith('BLS'):
            key = line.split('=', 1)[1].strip().strip('"\'')
            break
    os.makedirs(RAW, exist_ok=True)
    for i, (y0, y1) in enumerate(((2006, 2015), (2016, 2025), (2026, 2026))):
        body = {'seriesid': [s for s, _, _ in SERIES], 'startyear': str(y0), 'endyear': str(y1)}
        if key:
            body['registrationkey'] = key
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=json.dumps(body).encode(),
                                     headers={'Content-type': 'application/json'})
        d = json.load(urllib.request.urlopen(req, timeout=120))
        assert d['status'] == 'REQUEST_SUCCEEDED', d.get('message')
        json.dump(d, open(os.path.join(RAW, f'bls_api_ai_ppi_{y0}_{y1}_2026-11-16.json'), 'w'))


if '--fetch' in sys.argv:
    fetch()
rows = []
for f in sorted(glob.glob(os.path.join(RAW, '*.json'))):
    for s in json.load(open(f))['Results']['series']:
        for o in s['data']:
            if o['period'].startswith('M') and o['period'] != 'M13' and o['value'] not in ('-', ''):
                rows.append((s['seriesID'], pd.Period(f"{o['year']}-{o['period'][1:]}", 'M'), float(o['value']),
                             ';'.join(x['code'] for x in o.get('footnotes', []) if x and x.get('code'))))
D = pd.DataFrame(rows, columns=['series_id', 'month', 'index', 'footnote']).drop_duplicates(['series_id', 'month'])
out, mon = [], []
for sid, name, src in SERIES:
    x = D[D.series_id == sid].set_index('month').sort_index()
    if x.empty:
        out.append(dict(series_id=sid, name=name, source=src, note='NO DATA'))
        continue
    idx = x['index']
    yoy = (idx / idx.shift(12, freq='M').reindex(idx.index) - 1) * 100
    mm = (idx / idx.shift(1, freq='M').reindex(idx.index) - 1) * 100
    last = idx.index.max()
    y = yoy.dropna()
    pre = y[(y.index >= pd.Period('2018-01', 'M')) & (y.index <= pd.Period('2019-12', 'M'))]
    rank = int((y >= y[last]).sum()) if last in y.index else None
    prev_ge = y[(y.index < last) & (y >= y.get(last, float('nan')))]
    out.append(dict(series_id=sid, name=name, source=src, last_month=str(last), status=x.at[last, 'footnote'] or 'final',
                    yoy_last=round(y.get(last, float('nan')), 2), yoy_sep=round(y.get(last - 1, float('nan')), 2),
                    yoy_peak=round(y.max(), 2), yoy_peak_month=str(y.idxmax()), yoy_rank_since_start=rank, n_months=len(y),
                    first_month=str(y.index.min()), yoy_last_time_ge=str(prev_ge.index.max()) if len(prev_ge) else 'never (record)',
                    yoy_avg_2018_19=round(pre.mean(), 2) if len(pre) else None, mm_last=round(mm.get(last, float('nan')), 2)))
    for m in y.index[y.index >= pd.Period('2018-01', 'M')]:
        mon.append(dict(series_id=sid, name=name, month=str(m), index=idx[m], yoy=round(y[m], 3), mm=round(mm[m], 3)))
S = pd.DataFrame(out)
S.to_csv(os.path.join(OUT, 'J_ai_ppi_summary.csv'), index=False)
pd.DataFrame(mon).to_csv(os.path.join(OUT, 'J_ai_ppi_monthly.csv'), index=False)
pd.set_option('display.width', 250)
print(S[['series_id', 'name', 'last_month', 'status', 'yoy_last', 'yoy_sep', 'yoy_avg_2018_19', 'yoy_peak', 'yoy_peak_month', 'yoy_last_time_ge', 'first_month', 'mm_last']].to_string(index=False))
