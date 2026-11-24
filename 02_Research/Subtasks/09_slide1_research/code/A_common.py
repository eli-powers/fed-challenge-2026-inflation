"""Shared helpers for Agent A (Slide 1 existing-data CSVs). Run scripts from the project root with `python3 -I`."""
import csv, json, os, re, sys

ROOT = '.'
BUILD = f'{ROOT}/02_Research/Subtasks/04_oct_pce_build/outputs'
OUT = f'{ROOT}/02_Research/Subtasks/09_slide1_research/outputs'
T20804 = f'{ROOT}/03_Data/pipelines/Price indexes/PCE/raw/BEA_NIPA_T20804_2026-11-10.json'
WORKBOOK = f'{ROOT}/03_Data/pipelines/Price indexes/Price_Basket_Findings.xlsx'
SPEECHES = f'{ROOT}/02_Research/External_views/Fed_officials_2026-11/speeches'
BEA_REL = f'{ROOT}/03_Data/Raw/BEA_PIO_release_Sep2026_2026-11-14/personal-income-and-outlays-september-2026.html'
T20804_VINTAGE = 'BEA NIPA T20804 saved 2026-11-10 (table LastRevised Oct 29, 2026; contains Sep 2026)'


def load_levels():
    """Return {'headline': {(y,m): level}, 'core': {...}} from T20804 line 1 (DPCERG) and line 25 (DPCCRG)."""
    d = json.load(open(T20804))
    data = d['BEAAPI']['Results']['Data']
    out = {'headline': {}, 'core': {}}
    for x in data:
        key = {'1': 'headline', '25': 'core'}.get(x['LineNumber'])
        if key is None:
            continue
        tp = x['TimePeriod']  # e.g. 2026M09
        y, m = int(tp[:4]), int(tp[5:])
        out[key][(y, m)] = float(x['DataValue'].replace(',', ''))
    return out


def shift(ym, k):
    y, m = ym
    n = y * 12 + (m - 1) + k
    return (n // 12, n % 12 + 1)


def rates(lv, ym, level_t=None):
    """1m %, 3m ann., 6m ann., 12m % from index levels. level_t overrides level at ym (for estimates)."""
    it = level_t if level_t is not None else lv[ym]
    g = lambda k: lv[shift(ym, -k)]
    return dict(r1m=100 * (it / g(1) - 1), r3m_ann=100 * ((it / g(3)) ** 4 - 1),
                r6m_ann=100 * ((it / g(6)) ** 2 - 1), r12m=100 * (it / g(12) - 1))


def ymstr(ym):
    return f'{ym[0]}-{ym[1]:02d}'


def write_csv(path, rows, cols):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='raise')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})
    print('wrote', path, len(rows), 'rows')


def rd(path):
    return list(csv.DictReader(open(path)))
