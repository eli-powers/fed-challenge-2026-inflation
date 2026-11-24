"""P1: mechanical base-effect paths for core PCE and underlying measures, Oct 2026 est. -> Mar 2027.

Data only, no forecast model. For each measure, the 12m rate in month t is
prod(1+m/m) over the last 12 months. Future months are filled with a constant
m/m under named scenarios; the months that drop out are the actual
Oct 2025 - Mar 2026 prints (current vintage).

Inputs (all saved project files):
  02_Research/Subtasks/11_slide3a_research/outputs/C_q6_underlying.csv
    (BEA T20804 via inflation_data pipeline, vintage 2026-10-29; Dallas PCETRIM; Cleveland median PCE)
  02_Research/Subtasks/11_slide3a_research/outputs/C_q6_logan_measure.csv
  02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv (core Oct est. m/m)
Run from project root:  python3 -I "02_Research/Subtasks/13_persistence_angle/code/P1_base_effects.py"
"""
import csv, os

ROOT = os.getcwd()
S3A = os.path.join(ROOT, '02_Research', 'Subtasks', '11_slide3a_research', 'outputs')
OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs')
os.makedirs(OUT, exist_ok=True)


def months(a, b):
    y, m = map(int, a.split('-')); out = []
    while True:
        s = f'{y:04d}-{m:02d}'; out.append(s)
        if s == b: return out
        m += 1
        if m > 12: y, m = y + 1, 1


rows = list(csv.DictReader(open(os.path.join(S3A, 'C_q6_underlying.csv'))))


def series(name_start, horizon, transform=None):
    d = {}
    for r in rows:
        if r['series'].startswith(name_start) and r['horizon'] == horizon and r['value']:
            v = float(r['value'])
            d[r['period']] = transform(v) if transform else v
    return d


ann_to_mm = lambda a: ((1 + a / 100) ** (1 / 12) - 1) * 100
MM = {
    'Core PCE': series('Core PCE price index', '1m (% m/m)'),
    'Market-based core PCE': series('Market-based core PCE', '1m (% m/m)'),
    'Supercore (services ex energy & housing)': series('Supercore: PCE services ex energy and housing (BEA published', '1m (% m/m)'),
    'Dallas trimmed mean PCE': series('Dallas Fed trimmed-mean PCE, 1m annualized', '1m annualized', ann_to_mm),
    'Cleveland median PCE': series('Cleveland Fed median PCE, 1m % change', '1m (% m/m)'),
}
lm = {r['month']: float(r['1m_pct']) for r in csv.DictReader(open(os.path.join(S3A, 'C_q6_logan_measure.csv'))) if r['1m_pct']}
MM['Logan measure (core svcs ex housing & transport)'] = lm
octsum = {r['measure']: r for r in csv.DictReader(open(os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'D_build_2026-10_summary.csv')))}
MM['Core PCE']['2026-10'] = float(octsum['core']['estimate_mm'])  # UMD est.

TWO_PCT = ann_to_mm(2.0)


def twelve(d, t):
    ms = months_back(t, 12)
    p = 1.0
    for m in ms: p *= 1 + d[m] / 100
    return (p - 1) * 100


def months_back(t, n):
    y, m = map(int, t.split('-')); out = []
    for _ in range(n):
        out.append(f'{y:04d}-{m:02d}'); m -= 1
        if m == 0: y, m = y - 1, 12
    return out[::-1]


def avg_mm(d, ms):
    p = 1.0
    for m in ms: p *= 1 + d[m] / 100
    return (p ** (1 / len(ms)) - 1) * 100


future = months('2026-10', '2027-03')
long_rows, summ = [], []
for name, d in MM.items():
    last = max(d)
    base = {k: v for k, v in d.items()}
    scen = {
        '2% pace (0.165 m/m)': TWO_PCT,
        '2018-19 avg m/m': avg_mm(d, months('2018-01', '2019-12')),
        'last 6m avg m/m': avg_mm(d, months_back(last, 6)),
        'last 3m avg m/m': avg_mm(d, months_back(last, 3)),
    }
    cur12 = twelve(d, last)
    for sname, mm in scen.items():
        dd = dict(base)
        for m in future:
            if m not in dd: dd[m] = mm
        for m in future:
            drop = months_back(m, 13)[0]
            long_rows.append(dict(measure=name, scenario=sname, assumed_mm=round(mm, 4), month=m,
                                  status='actual/est.' if m in base else 'scenario',
                                  dropping_out_month=drop, dropping_out_mm=round(d[drop], 4),
                                  twelve_m=round(twelve(dd, m), 3)))
        summ.append(dict(measure=name, last_month=last, last_12m=round(cur12, 3), scenario=sname,
                         assumed_mm=round(mm, 4), assumed_ann=round(((1 + mm / 100) ** 12 - 1) * 100, 2),
                         twelve_m_Jan2027=round(twelve({**{m: mm for m in future if m not in base}, **base}, '2027-01'), 3),
                         twelve_m_Mar2027=round(twelve({**{m: mm for m in future if m not in base}, **base}, '2027-03'), 3)))
    # drop-out profile (the m/m each future month must beat to raise the 12m)
    for m in future:
        drop = months_back(m, 13)[0]
        long_rows.append(dict(measure=name, scenario='hold-12m break-even', assumed_mm='', month=m, status='',
                              dropping_out_month=drop, dropping_out_mm=round(d[drop], 4), twelve_m=''))

with open(os.path.join(OUT, 'P1_base_effect_paths.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys())); w.writeheader(); w.writerows(long_rows)
with open(os.path.join(OUT, 'P1_base_effect_summary.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(summ[0].keys())); w.writeheader(); w.writerows(summ)

for s in summ:
    print(f"{s['measure'][:34]:34s} {s['last_month']} 12m {s['last_12m']:5.2f} | {s['scenario']:20s} mm {s['assumed_mm']:.3f} ({s['assumed_ann']:4.2f} ann) -> Jan27 {s['twelve_m_Jan2027']:5.2f}  Mar27 {s['twelve_m_Mar2027']:5.2f}")
print()
for name, d in MM.items():
    print(name[:34], 'drop-outs:', ' '.join(f"{m}:{d[m]:.3f}" for m in months('2025-10', '2026-03')))

# Break-even pace: the average m/m of the months leaving the window (Oct 2025-Mar 2026 for the
# Oct 2026-Mar 2027 prints). A future pace above it raises the Mar 2027 12m vs the latest 12m.
print('\nBreak-even pace over the next six prints (geometric avg of drop-out m/m):')
be_rows = []
for name, d in MM.items():
    last = max(d)
    drops = months('2025-10', '2026-03') if last == '2026-10' else months('2025-10', '2026-03')
    # months still to be replaced after the latest available print
    rem = [m for m in months('2025-10', '2026-03') if f'{int(m[:4]) + 1}{m[4:]}' > last]
    a = avg_mm(d, rem)
    ann = ((1 + a / 100) ** 12 - 1) * 100
    be_rows.append(dict(measure=name, latest=last, months_leaving=f'{rem[0]}..{rem[-1]}', breakeven_mm=round(a, 4), breakeven_ann=round(ann, 2)))
    print(f'  {name[:40]:40s} latest {last}; leaving {rem[0]}..{rem[-1]}: {a:.3f} m/m = {ann:.2f}% ann')
with open(os.path.join(OUT, 'P1_breakeven_pace.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(be_rows[0].keys())); w.writeheader(); w.writerows(be_rows)
