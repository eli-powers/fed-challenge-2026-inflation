"""P2: core PCE by source (core goods / housing / core services ex housing), contributions to 12m,
and the m/m profile of the base months Oct 2025 - Mar 2026 (shutdown check).

Contribution approximation: c_i = w_i(t-12) * r_i(12m), with w_i = component nominal spending share of
core (U20405) in month t-12. Exact Fisher contributions differ slightly; residual reported.
Services ex energy & housing is built as a Fisher two-part removal of housing (L153) from L376, matching
the method in 11_slide3a_research C_q6 (reproduces BEA published supercore).

Inputs: 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json (prices)
        03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json (nominal)
        (BEA vintage LastRevised 2026-10-29; data through 2026M09)
Run from project root: python3 -I "02_Research/Subtasks/13_persistence_angle/code/P2_core_decomposition.py"
"""
import csv, json, os

ROOT = os.getcwd()
RAW = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw')
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs')
os.makedirs(OUT, exist_ok=True)


def load(tab):
    d = json.load(open(os.path.join(RAW, f'BEA_NIUnderlyingDetail_{tab}_2026-11-10.json')))['BEAAPI']['Results']['Data']
    out = {}
    for r in d:
        ln = int(r['LineNumber']); t = r['TimePeriod'].replace('M', '-')
        out.setdefault(ln, {})[t] = float(r['DataValue'].replace(',', ''))
    return out


P, N = load('U20404'), load('U20405')
CORE, GOODS, SVX, HSG = 374, 375, 376, 153
months = sorted(P[CORE])


def prev(t, k=1):
    y, m = map(int, t.split('-')); m -= k
    while m <= 0: y, m = y - 1, m + 12
    return f'{y:04d}-{m:02d}'


# Fisher removal of housing from services ex energy -> supercore index (chain-linked)
sc = {months[0]: 100.0}
for t in months[1:]:
    s = prev(t)
    if s not in sc: continue
    rel_a, rel_h = P[SVX][t] / P[SVX][s], P[HSG][t] / P[HSG][s]
    na0, nh0 = N[SVX][s], N[HSG][s]; na1, nh1 = N[SVX][t], N[HSG][t]
    # quantity-weight shares using nominal: Laspeyres and Paasche price relatives of the residual
    w0 = (na0 - nh0); las = (na0 * rel_a - nh0 * rel_h) / w0
    pas_inv = ((na1 / rel_a) - (nh1 / rel_h)) / (na1 - nh1)
    sc[t] = sc[s] * (las / pas_inv) ** 0.5
P['SC'] = sc
N['SC'] = {t: N[SVX][t] - N[HSG][t] for t in months}

comps = [('Core goods', GOODS), ('Housing', HSG), ('Core services ex housing (supercore)', 'SC')]


def r12(ln, t): return (P[ln][t] / P[ln][prev(t, 12)] - 1) * 100
def r1(ln, t): return (P[ln][t] / P[ln][prev(t)] - 1) * 100


rows = []
for t in months:
    if prev(t, 12) not in P[CORE] or t < '2018-01': continue
    b = prev(t, 12)
    rec = dict(month=t, core_12m=round(r12(CORE, t), 4), core_1m=round(r1(CORE, t), 4))
    tot = 0
    for name, ln in comps:
        w = N[ln][b] / N[CORE][b]
        c = w * r12(ln, t); tot += c
        rec[f'{name} | w(t-12)'] = round(w, 4); rec[f'{name} | 12m'] = round(r12(ln, t), 4)
        rec[f'{name} | contrib_pp'] = round(c, 4); rec[f'{name} | 1m'] = round(r1(ln, t), 4)
    rec['residual_pp'] = round(rec['core_12m'] - tot, 4)
    rows.append(rec)

with open(os.path.join(OUT, 'P2_core_decomposition.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

R = {r['month']: r for r in rows}
def avg(key, a, b): xs = [r[key] for r in rows if a <= r['month'] <= b]; return sum(xs) / len(xs)
peak = max((r for r in rows if '2021-01' <= r['month'] <= '2023-12'), key=lambda r: r['core_12m'])
summ = []
for label, get in [('2018-19 avg', lambda k: avg(k, '2018-01', '2019-12')),
                   (f'2021-23 core peak ({peak["month"]})', lambda k: peak[k]),
                   ('Sep 2025', lambda k: R['2025-09'][k]), ('Feb 2026', lambda k: R['2026-02'][k]),
                   ('Sep 2026', lambda k: R['2026-09'][k])]:
    rec = dict(period=label, core_12m=round(get('core_12m'), 3))
    for name, _ in comps:
        rec[f'{name} 12m'] = round(get(f'{name} | 12m'), 3); rec[f'{name} contrib'] = round(get(f'{name} | contrib_pp'), 3)
    rec['residual'] = round(get('residual_pp'), 3)
    summ.append(rec)
base = summ[0]
for rec in summ[1:]:
    for name, _ in comps:
        rec[f'{name} contrib vs 2018-19'] = round(rec[f'{name} contrib'] - base[f'{name} contrib'], 3)
with open(os.path.join(OUT, 'P2_core_decomposition_summary.csv'), 'w', newline='') as f:
    keys = list(summ[-1].keys()); w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(summ)
for s in summ: print(s)
print('\nBase-month m/m profile (core, goods, housing, supercore):')
for t in ['2025-07', '2025-08', '2025-09', '2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-07', '2026-08', '2026-09']:
    r = R[t]; print(t, r['core_1m'], r['Core goods | 1m'], r['Housing | 1m'], r['Core services ex housing (supercore) | 1m'])
print('\nHousing 1m, 2024-01..2026-09 mean:', round(avg('Housing | 1m', '2024-01', '2026-09'), 4))
