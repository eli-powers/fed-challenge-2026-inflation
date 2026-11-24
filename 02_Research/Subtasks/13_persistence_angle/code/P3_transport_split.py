"""P3: is the post-oil-shock rise in supercore in transportation services (energy-exposed) or in the rest?

Splits services ex energy & housing (supercore) into transportation services (BEA L190) and the
Logan measure (supercore ex transportation), with contributions to the supercore 12m change
Feb 2026 (last month before the Brent jump, per slide 2) -> Sep 2026, and Sep 2025 -> Feb 2026.
Also: Logan measure 12m history, first month above 3.0% in the current run, and its 2025-26 range.

Contribution approx: share of supercore nominal spending at t-12 x component 12m rate.
Inputs: 03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404/U20405_2026-11-10.json;
        02_Research/Subtasks/11_slide3a_research/outputs/C_q6_logan_measure.csv
Run from project root: python3 -I "02_Research/Subtasks/13_persistence_angle/code/P3_transport_split.py"
"""
import csv, json, os

ROOT = os.getcwd()
RAW = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw')
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs')


def load(tab):
    d = json.load(open(os.path.join(RAW, f'BEA_NIUnderlyingDetail_{tab}_2026-11-10.json')))['BEAAPI']['Results']['Data']
    out = {}
    for r in d:
        out.setdefault(int(r['LineNumber']), {})[r['TimePeriod'].replace('M', '-')] = float(r['DataValue'].replace(',', ''))
    return out


P, N = load('U20404'), load('U20405')
SVX, HSG, TRN = 376, 153, 190


def prev(t, k):
    y, m = map(int, t.split('-')); m -= k
    while m <= 0: y, m = y - 1, m + 12
    return f'{y:04d}-{m:02d}'


lm = {r['month']: r for r in csv.DictReader(open(os.path.join(ROOT, '02_Research', 'Subtasks', '11_slide3a_research', 'outputs', 'C_q6_logan_measure.csv')))}
r12 = lambda ln, t: (P[ln][t] / P[ln][prev(t, 12)] - 1) * 100
# supercore 12m from P2 output (Fisher removal; reproduces BEA published 3.596)
p2 = {r['month']: r for r in csv.DictReader(open(os.path.join(OUT, 'P2_core_decomposition.csv')))}
sc12 = lambda t: float(p2[t]['Core services ex housing (supercore) | 12m'])

rows = []
for t in ['2025-09', '2026-02', '2026-09']:
    b = prev(t, 12)
    sc_nom = N[SVX][b] - N[HSG][b]
    w_tr = N[TRN][b] / sc_nom
    rec = dict(month=t, supercore_12m=round(sc12(t), 3), transport_12m=round(r12(TRN, t), 3), transport_share=round(w_tr, 4),
               transport_contrib=round(w_tr * r12(TRN, t), 3), logan_12m=round(float(lm[t]['12m_pct']), 3),
               logan_share=round(1 - w_tr, 4), logan_contrib=round((1 - w_tr) * float(lm[t]['12m_pct']), 3))
    rec['residual'] = round(rec['supercore_12m'] - rec['transport_contrib'] - rec['logan_contrib'], 3)
    rows.append(rec)
for a, b in [(0, 1), (1, 2)]:
    x, y = rows[a], rows[b]
    rows.append(dict(month=f'change {x["month"]} -> {y["month"]}',
                     supercore_12m=round(y['supercore_12m'] - x['supercore_12m'], 3),
                     transport_12m=round(y['transport_12m'] - x['transport_12m'], 3), transport_share='',
                     transport_contrib=round(y['transport_contrib'] - x['transport_contrib'], 3),
                     logan_12m=round(y['logan_12m'] - x['logan_12m'], 3), logan_share='',
                     logan_contrib=round(y['logan_contrib'] - x['logan_contrib'], 3),
                     residual=round(y['residual'] - x['residual'], 3)))
with open(os.path.join(OUT, 'P3_transport_split.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)

# Logan measure history
hist = [(m, float(r['12m_pct'])) for m, r in sorted(lm.items()) if r['12m_pct']]
run_start = None
for m, v in hist:
    if v > 3.0:
        run_start = run_start or m
    else:
        run_start = None
print('\nLogan measure 12m: current run above 3.0% since', run_start)
last13 = [v for m, v in hist if m >= '2025-10']
print('Oct 2025 - Oct 2026 est. range:', min(last13), max(last13))
for lo, hi in [('2018-01', '2019-12'), ('2021-01', '2023-12'), ('2024-01', '2024-12')]:
    xs = [v for m, v in hist if lo <= m <= hi]; print(lo, hi, 'avg', round(sum(xs) / len(xs), 3), 'max', max(xs))
print('Transport services 12m history (selected):', {t: round(r12(TRN, t), 2) for t in ['2025-09', '2025-12', '2026-02', '2026-04', '2026-06', '2026-08', '2026-09']})
