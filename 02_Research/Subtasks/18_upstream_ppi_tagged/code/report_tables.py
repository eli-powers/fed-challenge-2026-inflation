"""Build markdown tables for report.md from outputs/ (no computation beyond formatting and selection)."""
import os

import pandas as pd

O = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs')
S = pd.read_csv(os.path.join(O, 'summary_excess.csv'))
G = pd.read_csv(os.path.join(O, 'group_table.csv'))
T = pd.read_csv(os.path.join(O, 'top10_oct2026.csv'), dtype={'code': str})
P = pd.read_csv(os.path.join(O, 'group_monthly_all_versions.csv'))
L = []
f = lambda x: f'{x:+.2f}'  # noqa: E731
L.append('### Excess by group (pp of the stage\'s 12m inflation above each group\'s 2018-19 pace)\n')
L.append('| stage | version | month | energy | tariff | AI | other | **total** | units 12m | published 12m | gap |')
L.append('|---|---|---|---|---|---|---|---|---|---|---|')
for _, r in S.iterrows():
    L.append(f'| {r.stage} | {r.version} | {r.month} | {f(r.excess_energy)} | {f(r.excess_tariff)} | {f(r.excess_AI)} | {f(r.excess_other)} | '
             f'**{f(r.excess_total)}** | {r.units_12m:.2f} | {r.published_12m:.2f} | {f(r.repro_gap_pp)} |')
L.append('\n### Group table, central (weight share, 12m rate %, 2018-19 baseline %, excess pp)\n')
L.append('| stage | month | group | weight share | 12m rate | baseline | excess |')
L.append('|---|---|---|---|---|---|---|')
for _, r in G[G.version == 'central'].iterrows():
    L.append(f'| {r.stage} | {r.month} | {r.group} | {100 * r.weight_share:.1f}% | {r.rate_12m:.2f} | {r.baseline_2018_19:.2f} | {f(r.excess_pp)} |')
for st in ('stage4', 'stage1'):
    L.append(f'\n### Top 10 contributors to each group\'s Oct 2026 excess, {st} central (pp; item share x (item 12m rate - group baseline))\n')
    L.append('| group | code | item | share | 12m rate | contribution |')
    L.append('|---|---|---|---|---|---|')
    for _, r in T[(T.stage == st) & (T.version == 'central')].iterrows():
        L.append(f'| {r.group} | {r.code} | {str(r["name"])[:60]} | {100 * r.s_i:.2f}% | {r.r_i:.1f} | {f(r.contrib_to_group_excess)} |')
c = P[(P.version == 'central') & (P.group != '_total')].pivot_table(index=['stage', 'month'], columns='group', values='excess').reset_index()
c['total'] = c[['energy', 'tariff', 'AI', 'other']].sum(axis=1)
c[c.stage == 'stage4'].to_csv(os.path.join(O, 'group_monthly_path_central_stage4.csv'), index=False)
c[c.stage == 'stage1'].to_csv(os.path.join(O, 'group_monthly_path_central_stage1.csv'), index=False)
L.append('\n### Monthly path of excess, stage 4 central (selected months; full Jan 2018 - Oct 2026 in outputs/group_monthly_path_central_stage4.csv)\n')
L.append('| month | energy | tariff | AI | other | total |')
L.append('|---|---|---|---|---|---|')
for _, r in c[(c.stage == 'stage4') & (c.month.str[5:].isin(['03', '06', '09', '12']) | (c.month == '2026-10'))].iterrows():
    L.append(f'| {r.month} | {f(r.energy)} | {f(r.tariff)} | {f(r.AI)} | {f(r.other)} | {f(r.total)} |')
open(os.path.join(O, 'report_tables.md'), 'w').write('\n'.join(L) + '\n')
print(len(L), 'lines')
