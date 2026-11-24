"""P6: Oct 2026 UMD estimates for core goods (BEA L375) and transportation services (L190), from the
audited October build lines, plus a one-month accuracy check using the September build vs BEA actual.

Method (same as the Logan-measure Oct est. in 11_slide3a_research C_q6): subgroup m/m = core-weighted
average of leaf m/m (pi, %) over the build lines in the subgroup; Oct index = Sep BEA index x (1 + m/m);
12m vs Oct 2025 BEA index (vintage LastRevised 2026-10-29).
Core goods = build lines < 150 with core weight > 0. Transportation services = build lines 190-208.
Check: same calculation on D_build_2026-09_lines.csv vs BEA actual Sep m/m.
Inputs: 04_oct_pce_build/outputs/D_build_2026-10_lines.csv, D_build_2026-09_lines.csv;
        03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json
Run from project root: python3 -I "02_Research/Subtasks/13_persistence_angle/code/P6_oct_est_subgroups.py"
"""
import csv, json, os
ROOT = os.getcwd()
B = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs')
d = json.load(open(os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes', 'PCE', 'raw', 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')))['BEAAPI']['Results']['Data']
P = {}
for r in d:
    P.setdefault(int(r['LineNumber']), {})[r['TimePeriod'].replace('M', '-')] = float(r['DataValue'].replace(',', ''))
GROUPS = {'Core goods (L375)': (375, lambda ln: ln < 150), 'Transportation services (L190)': (190, lambda ln: 190 <= ln <= 208)}


def sub_mm(path, test):
    num = den = 0.0; n = 0
    for r in csv.DictReader(open(path)):
        ln, w = int(r['line']), float(r['w_c'] or 0)
        if test(ln) and w > 0 and r['pi'] != '':
            num += w * float(r['pi']); den += w; n += 1
    return num / den, n


out = []
for name, (bea, test) in GROUPS.items():
    mm_s, n_s = sub_mm(os.path.join(B, 'D_build_2026-09_lines.csv'), test)
    act_s = (P[bea]['2026-09'] / P[bea]['2026-08'] - 1) * 100
    mm_o, n_o = sub_mm(os.path.join(B, 'D_build_2026-10_lines.csv'), test)
    idx_o = P[bea]['2026-09'] * (1 + mm_o / 100)
    r12_o = (idx_o / P[bea]['2025-10'] - 1) * 100
    r12_s = (P[bea]['2026-09'] / P[bea]['2025-09'] - 1) * 100
    hist = [(P[bea][f'2026-{m:02d}'] / P[bea][f'2026-{m-1:02d}'] - 1) * 100 for m in range(2, 10)]
    out.append(dict(group=name, lines_oct=n_o, oct_est_mm=round(mm_o, 3), sep_actual_12m=round(r12_s, 2), oct_est_12m=round(r12_o, 2),
                    sep_build_mm=round(mm_s, 3), sep_bea_mm=round(act_s, 3), sep_check_error=round(mm_s - act_s, 3),
                    feb_sep_2026_mm_range=f'{min(hist):.2f} to {max(hist):.2f}'))
p = os.path.join(ROOT, '02_Research', 'Subtasks', '13_persistence_angle', 'outputs', 'P6_oct_est_subgroups.csv')
with open(p, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o)
