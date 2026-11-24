"""Brief B, Q7: fetch PPI hospital series (with catalog and footnotes) from the BLS API v2; save the raw JSON.
Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/B_q7_fetch_bls.py"
Saves 03_Data/Raw/BLS_PPI_hospitals_2026-11-15/bls_api_ppi_hospitals_<span>.json (key loaded from .env, never saved)."""
import json
import os
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
RAW = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_hospitals_2026-11-15')
env = {}
for line in open(os.path.expanduser('.env')):
    line = line.strip().replace('export ', '')
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v.strip().strip('"').strip("'")
SERIES = ['PCU622---622---',      # PPI industry: hospitals (NSA) -- BEA source for PCE lines 184-186
          'PCU6221--6221--',      # general medical and surgical hospitals
          'WPU5121010111',        # commodity: Medicare patients, hospital inpatient care, general med & surg hospitals
          'WPU51210101',          # commodity: hospital inpatient care
          'WPU511104',            # commodity: hospital outpatient care
          ]
for y0, y1 in ((2006, 2015), (2016, 2026)):
    body = dict(seriesid=SERIES, startyear=str(y0), endyear=str(y1), catalog=True, registrationkey=env['BLS_API_KEY'])
    req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=json.dumps(body).encode(),
                                 headers={'Content-type': 'application/json', 'User-Agent': 'research-client'})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    print(y0, y1, d.get('status'), d.get('message'))
    json.dump(d, open(os.path.join(RAW, f'bls_api_ppi_hospitals_{y0}_{y1}.json'), 'w'), indent=1)
