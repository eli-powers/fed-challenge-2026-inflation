"""Builds outputs/report_tables.md from io_input_costs.py outputs (every number in report.md comes from here).
Run from project root: python3 -I 02_Research/Subtasks/17_upstream_io_costs/code/report_tables.py"""
import os
import pandas as pd
O = os.path.join(os.path.dirname(__file__), '..', 'outputs')
S = pd.read_csv(os.path.join(O, 'summary_table.csv'))
A = pd.read_csv(os.path.join(O, 'group_monthly_all_versions.csv'))
T = pd.read_csv(os.path.join(O, 'top10_inputs_oct2026.csv'))
L = pd.read_csv(os.path.join(O, 'diag_match_level_weights_oct2026.csv'))
R = pd.read_csv(os.path.join(O, 'ppi_12m_rates.csv'), index_col=0)
GL = {'energy': 'Energy-exposed', 'tariff': 'Tariff-exposed', 'AI': 'AI-related', 'untagged': 'Everything else', 'TOTAL': 'Total'}
KM = ['2025-03', '2026-02', '2026-10']
out = []
f = lambda x, d=2: '' if pd.isna(x) else f'{x:.{d}f}'  # noqa: E731
for v in ('central', 'direct', 'summary'):
    d = S[S.version == v]
    out.append(f'\n### {v}: 12m purchased-input cost inflation (%), excess over own 2018-19 avg (pp)\n')
    out.append('| Group | 2018-19 avg | Mar 2025 | Feb 2026 | Oct 2026 | Excess Mar 25 | Excess Feb 26 | Excess Oct 26 | Input share θ | Dropped wt |')
    out.append('|---|---|---|---|---|---|---|---|---|---|')
    for _, r in d[d.group != 'TOTAL'].iterrows():
        out.append(f"| {GL[r.group]} | {f(r.baseline_2018_19)} | " + ' | '.join(f(r[f'rate_{m}']) for m in KM) + ' | ' +
                   ' | '.join(f(r[f'excess_{m}']) for m in KM) + f" | {f(r.theta_domestic_oct26)} | {100*r.dropped_share_oct26:.0f}%{' ⚑' if r.dropped_flag else ''} |")
    out.append(f'\n{v}: contributions, pp (PCE share = group share of core PCE, start-of-window weights)\n')
    out.append('| Group | PCE share Oct 26 | (a) plain Mar 25 | (a) Feb 26 | (a) Oct 26 | (b) scaled Mar 25 | (b) Feb 26 | (b) Oct 26 |')
    out.append('|---|---|---|---|---|---|---|---|')
    for _, r in d.iterrows():
        out.append(f"| {GL[r.group]} | {f(r['pce_share_2026-10'], 3)} | " + ' | '.join(f(r[f'contrib_plain_{m}']) for m in KM) + ' | ' +
                   ' | '.join(f(r[f'contrib_scaled_{m}']) for m in KM) + ' |')
# stability: group shares of total contribution, Oct 2026
out.append('\n### Stability across versions, Oct 2026: each group\'s share of the total contribution (%)\n')
out.append('| Version | Measure | Energy | Tariff | AI | Else | Total pp |')
out.append('|---|---|---|---|---|---|---|')
for meas in ('plain', 'scaled'):
    for v in ('central', 'direct', 'summary'):
        d = S[(S.version == v)].set_index('group')[f'contrib_{meas}_2026-10']
        out.append(f'| {v} | ({"a" if meas == "plain" else "b"}) {meas} | ' + ' | '.join(f'{100*d[g]/d["TOTAL"]:.0f}' for g in ('energy', 'tariff', 'AI', 'untagged')) + f' | {d["TOTAL"]:.2f} |')
out.append('\n### Top 10 inputs by contribution to each group\'s Oct 2026 excess (central)\n')
for g in ('energy', 'tariff', 'AI', 'untagged'):
    out.append(f'\n**{GL[g]}**\n\n| Input (BEA code) | PPI series | Share | 12m Oct 26 | 2018-19 avg | Contrib to excess (pp) |\n|---|---|---|---|---|---|')
    for _, r in T[(T.version == 'central') & (T.group == g)].iterrows():
        title = str(r.ppi_title).replace('PPI industry data for ', '').replace('PPI industry group data for ', '').replace('PPI industry sub-sector data for ', '').replace(', not seasonally adjusted', '')
        out.append(f'| {r.input} | {r.ppi_series} ({title}) | {r.share_oct26:.3f} | {r.r12_oct26:.1f} | {r.r12_base_avg:.1f} | {r.contrib_to_excess_pp:.2f} |')
out.append('\n### Match level of input weight, Oct 2026 (share of all purchased inputs)\n')
pv = L.pivot_table(index=['version', 'match'], columns='group', values='weight').reindex(columns=['energy', 'tariff', 'AI', 'untagged'])
out.append(pv.map(lambda x: f'{100*x:.1f}%' if pd.notna(x) else '').to_markdown())
# path, central, quarterly snapshot
c = A[A.version == 'central'].pivot(index='month', columns='group', values='rate')[['energy', 'tariff', 'AI', 'untagged']]
out.append('\n### Monthly path (central), 12m %, selected months (full path in group_monthly_path_central.csv)\n')
out.append(c[c.index.str.endswith(('-03', '-06', '-09', '-12')) | (c.index == '2026-10')].round(2).to_markdown())
# worth a look helpers
for s in ('PCUAWHLTRAWHLTR', 'PCUARETTRARETTR', 'PCU334418334418', 'PCU32411-32411-'):
    x = R[s]
    prev = x[(x >= x.iloc[-1]) & (x.index < '2026-10')]
    out.append(f'\n{s}: Oct 2026 12m {x.iloc[-1]:.1f}%; 2018-19 avg {x.loc["2018-01":"2019-12"].mean():.1f}%; '
               f'last month at or above: {prev.index.max() if len(prev) else "none since 2018-01"}; max since 2018 {x.max():.1f}% ({x.idxmax()})')
open(os.path.join(O, 'report_tables.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
