"""B_fetch_bls.py - download BLS Productivity & Costs (nonfarm business) incl. labor share level,
and CES average hourly earnings, into a new raw folder. Run from project root: python3 -I code path.
Keys read from .env (never written to files)."""
import os, json, urllib.request, pathlib, re
ROOT = pathlib.Path('.')
OUT = ROOT/'03_Data/Raw/S3A_B_labor_costs_2026-11-15'; OUT.mkdir(parents=True, exist_ok=True)
for line in open(os.path.expanduser('.env')):
    m = re.match(r'export (\w+)=(.*)', line.strip())
    if m: os.environ[m.group(1)] = m.group(2).strip('"\'')
prod = [f'PRS85006{n}' for n in ['054','064','091','092','093','101','102','103','111','112','113','171','172','173','174','141','142','143','051','061']]
ces = ['CES0500000003','CES0500000008','CES0500000002']
def pull(ids, y0, y1, tag):
    req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/',
        data=json.dumps({'seriesid': ids,'startyear': str(y0),'endyear': str(y1),'catalog': True,'registrationkey': os.environ['BLS_API_KEY']}).encode(),
        headers={'Content-type':'application/json'})
    d = json.load(urllib.request.urlopen(req))
    d.get('Results',{}).pop('registrationkey',None)
    f = OUT/f'bls_api_{tag}_{y0}-{y1}_2026-11-15.json'
    f.write_text(json.dumps(d, indent=1)); print(f.name, d['status'], d.get('message'))
pull(prod, 2008, 2026, 'productivity_costs')
pull(ces, 2016, 2026, 'ces_ahe')
