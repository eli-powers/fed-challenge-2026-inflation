"""Fetch BLS PPI commodity indexes (NSA, WPU...) for every stage-4 and stage-1 unit, their 4- and 3-character parents
(fallback when a unit is unpriced), and the published stage aggregates WPUID54 / WPUID51 (NSA), 2016-2026.
BLS API v2, key from .env (never written to files). Raw JSON saved unedited to
03_Data/Raw/BLS_PPI_stage_commodities_2026-11-17/. Called by ppi_tagged_excess.py --fetch.
"""
import json
import os
import time
import urllib.request
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import units

RAW = os.path.join(units.ROOT, '03_Data', 'Raw', 'BLS_PPI_stage_commodities_2026-11-17')


def key():
    for line in open(os.path.expanduser('.env')):
        line = line.strip().replace('export ', '')
        if line.startswith('BLS'):
            return line.split('=', 1)[1].strip().strip('"\'')


def series_list(col=5):
    codes = set()
    for s in ('54', '51'):
        for c in units.stage_units(s, col):
            codes |= {c, c[:4], c[:3]}
    return sorted({'WPU' + c for c in codes}) + ['WPUID54', 'WPUID51', 'WPSID54', 'WPSID51']


def fetch_dec2024_extra():
    """Audit R1-F02: series for units that exist only in the Dec 2024 RI universe (saved as extra batches)."""
    ids = sorted(set(series_list(4)) - set(series_list(5)))
    return fetch(ids, prefix='dec2024extra_')


def fetch(ids=None, prefix=''):
    os.makedirs(RAW, exist_ok=True)
    ids = ids or series_list()
    k = key()
    for i in range(0, len(ids), 50):
        body = json.dumps({'seriesid': ids[i:i + 50], 'startyear': '2016', 'endyear': '2026', 'registrationkey': k}).encode()
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=body,
                                     headers={'Content-Type': 'application/json', 'User-Agent': 'research-script'})
        raw = urllib.request.urlopen(req, timeout=120).read()
        d = json.loads(raw)
        assert d['status'] == 'REQUEST_SUCCEEDED', d.get('message')
        open(os.path.join(RAW, f'bls_api_stage_commodities_{prefix}2016_2026_batch{i // 50 + 1:02d}_2026-11-17.json'), 'wb').write(raw)
        time.sleep(0.5)
    return len(ids)


if __name__ == '__main__':
    print(fetch_dec2024_extra() if '--dec2024-extra' in sys.argv else fetch())
