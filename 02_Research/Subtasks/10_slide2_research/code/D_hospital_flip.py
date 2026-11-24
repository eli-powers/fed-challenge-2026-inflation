"""Brief D, Q12 attack 3 (estimate risk on the Oct 12m breadth drop): what would it take for the hospital leaves
(184-186, 8.8% of core weight) to stay above 3% at 12m in Oct 2026?

Run from the project root:
    python3 -I "02_Research/Subtasks/10_slide2_research/code/D_hospital_flip.py"

Inputs (all saved, read-only):
  - 04_oct_pce_build/outputs/D_build_2026-10_lines.csv: UMD Oct 2026 SA m/m (pi) and the BEA-style seasonal
    adjustment applied to the NSA PPI (adj_b), leaves 184-186.
  - 09_slide1_research/outputs/C_flip_distance_oct.csv: SA m/m needed for the 12m rate to equal 3% (0.564).
  - 10_slide2_research/outputs/B_q7_hospital_octobers.csv: implied October seasonal gap (NSA PPI m/m minus BEA SA
    leaf m/m), 2017-2025.
  - 04_oct_pce_build/outputs/ppi_first_release.csv: PCU622622 first-print vs current m/m (ALFRED), Dec 2024-Sep 2026.
Writes: outputs/D_hospital_flip.csv
"""
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks')
OUT = os.path.join(SUB, '10_slide2_research', 'outputs')
L = pd.read_csv(os.path.join(SUB, '04_oct_pce_build', 'outputs', 'D_build_2026-10_lines.csv')).set_index('line')
F = pd.read_csv(os.path.join(SUB, '09_slide1_research', 'outputs', 'C_flip_distance_oct.csv')).set_index('line')
O = pd.read_csv(os.path.join(OUT, 'B_q7_hospital_octobers.csv'))
R = pd.read_csv(os.path.join(SUB, '04_oct_pce_build', 'outputs', 'ppi_first_release.csv'))
R = R[R.bls_series_id == 'PCU622---622---']

sa_used = L.at[184, 'pi']
adj = L.at[184, 'adj_b']
nsa_in = sa_used - adj
need_sa = F.at[184, 'mm_needed_for_12m_eq_3pct']
gaps = O.dropna(subset=['implied_seasonal_gap_pp(nsa_ppi_minus_bea_sa)'])
gcol = 'implied_seasonal_gap_pp(nsa_ppi_minus_bea_sa)'
rows = [
    dict(item='UMD Oct 2026 SA m/m used, leaf 184 (%)', value=sa_used),
    dict(item='UMD seasonal adjustment applied, adj_b (pp)', value=adj),
    dict(item='implied NSA PPI 622 Oct 2026 m/m input (%) = pi - adj_b', value=nsa_in),
    dict(item='published PPI 622 Oct 2026 prelim NSA m/m (%), B_q7_hospital_octobers.csv', value=float(O[O.year == 2026].ppi622_oct_mm_nsa.iloc[0])),
    dict(item='SA m/m needed for 12m >= 3% (%)', value=need_sa),
    dict(item='NSA m/m needed at UMD adj_b (%)', value=need_sa - adj),
    dict(item='upward NSA revision needed at UMD adj_b (pp)', value=need_sa - adj - nsa_in),
    dict(item='max seasonal gap that still flips at current NSA (pp) = NSA - needed SA', value=nsa_in - need_sa),
    dict(item='historical October seasonal gap 2017-2025: min (pp)', value=gaps[gcol].min()),
    dict(item='historical October seasonal gap 2017-2025: mean (pp)', value=gaps[gcol].mean()),
    dict(item='historical October seasonal gap 2017-2025: max (pp)', value=gaps[gcol].max()),
    dict(item='Octobers 2017-2025 whose gap would flip the result at current NSA (count)', value=int((gaps[gcol] <= nsa_in - need_sa).sum())),
    dict(item='NSA m/m needed at the smallest historical gap (%)', value=need_sa + gaps[gcol].min()),
    dict(item='PCU622622 first-print revisions Dec 2024-Sep 2026: n', value=len(R)),
    dict(item='  mean abs revision (pp)', value=R.mm_revision_pp.abs().mean()),
    dict(item='  max upward revision (pp)', value=R.mm_revision_pp.max()),
    dict(item='  min (largest downward) revision (pp)', value=R.mm_revision_pp.min()),
    dict(item='  count of upward revisions >= needed at UMD adj_b', value=int((R.mm_revision_pp >= need_sa - adj - nsa_in).sum())),
]
res = pd.DataFrame(rows)
res['value'] = res.value.astype(float).round(4)
res['note'] = 'Oct 2026 = UMD est.; revisions = ALFRED current (2026-11-11) minus first print; seasonal gap from BEA SA leaf 184 vs NSA PPI'
res.to_csv(os.path.join(OUT, 'D_hospital_flip.csv'), index=False)
print(res[['item', 'value']].to_string(index=False))
