"""M: upstream producer prices grouped by the three shocks (energy / tariff / AI), 12-month % change (NSA),
Mar 2025 and Oct 2026 vs the 2018-19 average of 12-month rates. Eli Nov 17 (option 3 for the 2B right chart). Not audited.

Run from project root: python3 -I 02_Research/Subtasks/10_slide2_research/code/M_upstream_by_shock.py [--fetch]
--fetch pulls BLS API v2 (key from .env) into 03_Data/Raw/BLS_PPI_shock_upstream_2026-11-17/.
Also reads the AI basket raw (03_Data/Raw/BLS_PPI_ai_basket_2026-11-16/).
Caveat: PPI prices domestic producers only; imports and tariffs are not priced directly, so 'tariff' series are indirect proxies.
"""
import glob, json, os, sys, urllib.request
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RAW = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_shock_upstream_2026-11-17')
RAW_AI = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_ai_basket_2026-11-16')
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')

SERIES = [  # (id, label, group)
    ('WPUID51', 'Stage 1 intermediate demand', 'stage'),
    ('WPUID52', 'Stage 2 intermediate demand', 'stage'),
    ('WPUID53', 'Stage 3 intermediate demand', 'stage'),
    ('WPUID54', 'Stage 4 intermediate demand', 'stage'),
    ('WPUFD4', 'Final demand', 'stage'),
    ('WPUID51113', 'Stage 1: goods ex F&E, to goods producers', 'stage_core'),
    ('WPUID52113', 'Stage 2: goods ex F&E, to goods producers', 'stage_core'),
    ('WPUID53113', 'Stage 3: goods ex F&E, to goods producers', 'stage_core'),
    ('WPUID54113', 'Stage 4: goods ex F&E, to goods producers', 'stage_core'),
    ('WPUID54213', 'Stage 4: goods ex F&E, to services producers', 'stage_core'),
    ('WPUID54212', 'Stage 4: energy, to services producers', 'energy'),
    ('WPUID613', 'Processed fuels & lubricants (intermediate)', 'energy'),
    ('WPUFD412', 'Final demand energy', 'energy'),
    ('WPUFD41311', 'Finished consumer goods ex food & energy', 'tariff'),
    ('WPUFD413112', 'Durable consumer goods', 'tariff'),
    ('WPUFD413111', 'Nondurable consumer goods ex food & energy', 'tariff'),
    ('WPUID61113', 'Materials for durable manufacturing', 'tariff'),
    ('WPUID6112', 'Components for manufacturing', 'tariff'),
    ('WPU1017', 'Steel mill products', 'tariff'),
    ('WPU1025', 'Nonferrous mill shapes (incl. aluminum)', 'tariff'),
    ('WPU1178', 'Electronic components & accessories', 'AI'),
]
AI_EXTRA = [('PCU33441-33441-', 'Electronic components (incl. chips), industry', 'AI'),
            ('PCU334413334413', 'Semiconductors & related devices', 'AI'),
            ('PCU3341--3341--', 'Computers & peripherals', 'AI')]


def fetch():
    key = None
    for line in open(os.path.expanduser('.env')):
        if line.strip().startswith('BLS'):
            key = line.split('=', 1)[1].strip().strip('"\'')
            break
    os.makedirs(RAW, exist_ok=True)
    for y0, y1 in ((2016, 2025), (2026, 2026)):
        body = {'seriesid': [s for s, _, _ in SERIES], 'startyear': str(y0), 'endyear': str(y1)}
        if key:
            body['registrationkey'] = key
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=json.dumps(body).encode(),
                                     headers={'Content-type': 'application/json'})
        d = json.load(urllib.request.urlopen(req, timeout=120))
        assert d['status'] == 'REQUEST_SUCCEEDED', d.get('message')
        json.dump(d, open(os.path.join(RAW, f'bls_api_shock_upstream_{y0}_{y1}_2026-11-17.json'), 'w'))


if '--fetch' in sys.argv:
    fetch()
rows = []
for f in sorted(glob.glob(os.path.join(RAW, '*.json')) + glob.glob(os.path.join(RAW_AI, '*.json'))):
    for s in json.load(open(f))['Results']['series']:
        for o in s['data']:
            if o['period'].startswith('M') and o['period'] != 'M13' and o['value'] not in ('-', ''):
                rows.append((s['seriesID'], pd.Period(f"{o['year']}-{o['period'][1:]}", 'M'), float(o['value']),
                             ';'.join(x['code'] for x in o.get('footnotes', []) if x and x.get('code'))))
D = pd.DataFrame(rows, columns=['series_id', 'month', 'index', 'fn']).drop_duplicates(['series_id', 'month'])
out = []
for sid, lab, g in SERIES + AI_EXTRA:
    x = D[D.series_id == sid].set_index('month').sort_index()['index']
    if x.empty:
        out.append(dict(series_id=sid, label=lab, group=g, note='NO DATA')); continue
    yoy = (x / x.shift(12, freq='M').reindex(x.index) - 1) * 100
    base = yoy[(yoy.index >= pd.Period('2018-01', 'M')) & (yoy.index <= pd.Period('2019-12', 'M'))]
    last = yoy.dropna().index.max()
    g_ = lambda m: round(yoy.get(pd.Period(m, 'M'), float('nan')), 2)
    out.append(dict(series_id=sid, label=lab, group=g, base_2018_19=round(base.mean(), 2), n_base=len(base.dropna()),
                    mar_2025=g_('2025-03'), feb_2026=g_('2026-02'), oct_2026=g_('2026-10'), last=str(last),
                    excess_oct=round(g_('2026-10') - base.mean(), 2), excess_mar25=round(g_('2025-03') - base.mean(), 2)))
R = pd.DataFrame(out)
R.to_csv(os.path.join(OUT, 'M_upstream_by_shock.csv'), index=False)
pd.set_option('display.width', 220)
print(R.drop(columns=['series_id']).to_string(index=False))
