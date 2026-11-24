"""Coordinator check: recompute 3 group numbers from the saved intermediates with plain loops (no shared code).
Run from project root: python3 -I 02_Research/Subtasks/17_upstream_io_costs/code/verify_by_hand.py
Reads outputs/ written by io_input_costs.py: leaf_input_shares_central.csv, ppi_concordance.csv, ppi_12m_rates.csv,
leaf_pce_weights_start_of_window.csv, leaf_tags.csv, leaf_theta_central.csv, group_monthly_all_versions.csv.
Also lists the largest dropped (unpriced) inputs per group (central, Oct 2026) for the report."""
import csv, os
O = os.path.join(os.path.dirname(__file__), '..', 'outputs')
rd = lambda f: list(csv.DictReader(open(os.path.join(O, f))))  # noqa: E731
sh = {r['']: {k: float(v) for k, v in r.items() if k != ''} for r in rd('leaf_input_shares_central.csv')}
con = {r['bea_code']: r['ppi_series'] for r in rd('ppi_concordance.csv') if r['level'] == 'detail'}
rates = {r['']: {k: float(v) for k, v in r.items() if k != ''} for r in rd('ppi_12m_rates.csv')}
w = {r['']: {k: float(v) for k, v in r.items() if k != ''} for r in rd('leaf_pce_weights_start_of_window.csv')}
tag = {r['']: r['tag_final'] for r in rd('leaf_tags.csv')}
th = {r['leaf']: float(r['theta_domestic']) for r in rd('leaf_theta_central.csv')}
script = {(r['version'], r['group'], r['month']): r for r in rd('group_monthly_all_versions.csv')}


def grate(g, m):
    L = [l for l in tag if tag[l] == g]
    tot = sum(w[l][m] for l in L)
    return sum(w[l][m] / tot * sum(s * rates[m][con[c]] for c, s in sh[l].items() if s) for l in L)


def base(g):
    ms = [f'{y}-{mo:02d}' for y in (2018, 2019) for mo in range(1, 13)]
    return sum(grate(g, m) for m in ms) / len(ms)


chk = []
r1 = grate('energy', '2026-10'); chk.append(('energy rate Oct 2026', r1, float(script[('central', 'energy', '2026-10')]['rate'])))
b = base('AI'); chk.append(('AI baseline 2018-19', b, float(script[('central', 'AI', '2026-10')]['baseline'])))
m = '2026-02'; g = 'untagged'
L = [l for l in tag if tag[l] == g]; allw = sum(w[l][m] for l in w); sg = sum(w[l][m] for l in L) / allw
ex = grate(g, m) - base(g); thg = sum(w[l][m] * th[l] for l in L) / sum(w[l][m] for l in L)
chk.append(('untagged contrib plain Feb 2026', sg * ex, float(script[('central', g, m)]['contrib_plain_pp'])))
chk.append(('untagged contrib scaled Feb 2026', sg * thg * ex, float(script[('central', g, m)]['contrib_scaled_pp'])))
for n, a, s in chk:
    print(f'{n:35s} hand {a:9.5f}  script {s:9.5f}  diff {a - s:+.2e}')
    assert abs(a - s) < 1e-6
print('all hand checks match')
