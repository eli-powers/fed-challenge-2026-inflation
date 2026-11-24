"""B_crosscheck.py - compare fresh 2026-11-15 BLS pull with pipeline 2026-11-10 pull and printed published rates.
Run: python3 -I 02_Research/Subtasks/11_slide3a_research/code/B_crosscheck.py"""
import json, pathlib, pandas as pd
ROOT = pathlib.Path('.')
o = pd.read_csv(ROOT/'03_Data/pipelines/inflation_data/processed/bls/observations.csv', parse_dates=['date'])
pc = json.load(open(ROOT/'03_Data/Raw/S3A_B_labor_costs_2026-11-15/bls_api_productivity_costs_2008-2026_2026-11-15.json'))
bad = 0; n = 0
for sid in ['PRS85006113', 'PRS85006093', 'PRS85006103', 'PRS85006111', 'PRS85006112', 'PRS85006091', 'PRS85006092', 'PRS85006101', 'PRS85006102']:
    s = [x for x in pc['Results']['series'] if x['seriesID'] == sid][0]
    new = {pd.Timestamp(int(x['year']), (int(x['period'][1:]) - 1) * 3 + 1, 1): float(x['value']) for x in s['data']}
    old = o[o.publisher_series_id == sid].set_index('date')['value']
    for d, v in old.items():
        if d in new and d >= pd.Timestamp('2018-01-01'):
            n += 1
            if abs(new[d] - v) > 1e-6: bad += 1; print('DIFF', sid, d.date(), v, new[d])
print('compared', n, 'mismatches', bad)
# published q/q and y/y vs my computation, latest
q = o[(o.publisher_series_id == 'PRS85006112')].set_index('date')['value']; i = o[o.publisher_series_id == 'PRS85006113'].set_index('date')['value']
print('ULC 2026Q3 published q/q ann', q.iloc[-1], 'computed', round(((i.iloc[-1] / i.iloc[-2]) ** 4 - 1) * 100, 2))
y = o[(o.publisher_series_id == 'PRS85006111')].set_index('date')['value']
print('ULC 2026Q3 published y/y', y.iloc[-1], 'computed', round((i.iloc[-1] / i.iloc[-5] - 1) * 100, 2))
e = o[(o.publisher_series_id == 'CIU2020000000000A')].set_index('date')['value']; es = o[(o.publisher_series_id == 'CIS2020000000000I')].set_index('date')['value']
print('ECI W&S pub NSA y/y 2026Q3', e.iloc[-1], 'SA-index y/y', round((es.iloc[-1] / es.iloc[-5] - 1) * 100, 2))
