"""B_labor_share.py - verify Barr's 'record low 52.8% in 2026Q2'. Writes outputs/B_q3_labor_share.md.
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/B_labor_share.py"""
import json, pathlib
import pandas as pd
ROOT = pathlib.Path('.')
RAW = ROOT/'03_Data/Raw/S3A_B_labor_costs_2026-11-15'
OUT = ROOT/'02_Research/Subtasks/11_slide3a_research/outputs'
def fred(f):
    return pd.Series({pd.Timestamp(x['date']): float(x['value']) for x in json.load(open(RAW/f))['observations'] if x['value'] != '.'}).sort_index()
def q(t): return f'{t.year}Q{(t.month-1)//3+1}'
idx = fred('fred_PRS85006173_full_2026-11-15.json')
bidx = fred('fred_PRS84006173_2026-11-15.json')
pc = json.load(open(RAW/'bls_api_productivity_costs_2008-2026_2026-11-15.json'))
def bls(sid):
    s = [x for x in pc['Results']['series'] if x['seriesID'] == sid][0]
    return pd.Series({pd.Timestamp(int(x['year']), (int(x['period'][1:]) - 1) * 3 + 1, 1): float(x['value']) for x in s['data']}).sort_index()
lvl = bls('PRS85006174'); comp = bls('PRS85006064'); outp = bls('PRS85006054')
calc = comp / outp * 100
fac = lvl['2017-01-01':'2017-12-01'].mean() / 100   # level per index point (2017=100 base)
# ALFRED vintages of the index
al = json.load(open(RAW/'alfred_PRS85006173_vintages_2026-11-15.json'))['observations']
vint = {}
for r in al:
    for k, v in r.items():
        if k.startswith('PRS85006173_'):
            vint.setdefault(k[-8:], {})[pd.Timestamp(r['date'])] = float(v)
vdates = {'20260507': 'May 7 2026 (2026Q1 prelim)', '20260806': 'Aug 6 2026 (2026Q2 prelim)', '20260903': 'Sep 3 2026 (2026Q2 revised)', '20261105': 'Nov 5 2026 (2026Q3 prelim; BEA annual-update revisions)'}
L = []
L.append('# Labor share check: Barr "record low of 52.8 percent in the second quarter of 2026"\n')
L.append('Script: `code/B_labor_share.py`. Raw: BLS API `bls_api_productivity_costs_2008-2026_2026-11-15.json` (series PRS85006174, 064, 054); FRED/ALFRED JSON `fred_PRS85006173_full_2026-11-15.json`, `alfred_PRS85006173_vintages_2026-11-15.json` in `03_Data/Raw/S3A_B_labor_costs_2026-11-15/`. Tags: [O] opened.\n')
L.append('## Series identified')
L.append('- Barr (speech 2026-11-12, saved text) says "labor share of national income" and gives no source; footnote 15 cites NY Fed Liberty Street (Audoly et al., 2026) for the post-COVID decline. The percent-level series matching 52.8 is the **BLS nonfarm business sector labor share, level (percentage), PRS85006174** (labor compensation / nominal value-added output of the nonfarm business sector, SA). BLS also publishes it as an index, PRS85006173 (2017=100; FRED PRS85006173). [O: API, FRED]')
L.append(f'- Check: 2026Q3 PRS85006064/PRS85006054 = {comp.iloc[-1]:,.1f} / {outp.iloc[-1]:,.1f} = {calc.iloc[-1]:.2f}% vs published level {lvl.iloc[-1]:.1f}. Index-to-level factor (2017 average level / 100) = {fac:.4f}.')
L.append('- It is a share of nonfarm business output, **not** "national income". A BEA national-income measure does not give 52.8 (below).\n')
L.append('## Current vintage (Productivity & Costs, 2026Q3 prelim, released 2026-11-05)')
L.append('| Quarter | PRS85006174 level (%) | PRS85006173 index (2017=100) |\n|---|---|---|')
for t in lvl.index[-8:]:
    L.append(f'| {q(t)} | {lvl[t]:.1f} | {idx[t]:.3f} |')
L.append(f'\n**2026Q2 = {lvl["2026-04-01"]:.1f}%; 2026Q3 = {lvl["2026-07-01"]:.1f}%.** Neither is 52.8 in the current vintage.\n')
L.append('## Vintage reconstruction (index from ALFRED x factor; derived, not published levels)')
L.append('| Vintage | 2026Q1 | 2026Q2 | 2026Q3 |\n|---|---|---|---|')
for k, lab in vdates.items():
    v = vint.get(k, {})
    cells = [f'{v[pd.Timestamp(d)]*fac:.2f} (idx {v[pd.Timestamp(d)]:.3f})' if pd.Timestamp(d) in v else 'n/a' for d in ['2026-01-01', '2026-04-01', '2026-07-01']]
    L.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
L.append('\nThe Sep 3 vintage of 2026Q2 (idx 93.446) converts to ~52.8; the Aug 6 vintage (93.547) to ~52.9. **52.8 therefore matches the pre-Nov-5 vintage of the BLS nonfarm business labor share, 2026Q2** (inference from index x factor; BLS published levels for old vintages not retrieved). The Nov 5 release (BEA annual-update revisions back to 2021Q1) revised 2026Q2 UP to 53.3. Barr spoke Nov 12, after that release.\n')
rec = idx.sort_values()
L.append('## Record-low status (index, 1947Q1-2026Q3, current vintage)')
L.append(f'- Lowest in published history: **2026Q3 ({idx.iloc[-1]:.3f})**; second lowest 2026Q2 ({idx["2026-04-01"]:.3f}). Third {q(rec.index[2])} ({rec.iloc[2]:.3f}).')
prior = idx[idx.index < '2025-07-01']
L.append(f'- Lowest reading before 2025Q3: {q(prior.idxmin())} ({prior.min():.3f}); 2025Q3 ({idx["2025-07-01"]:.3f}) was the first quarter below it, i.e. the index has been at or near record lows since 2025Q3.')
run_low = [q(t) for t in idx.index if idx[t] <= idx[:t].min() and t >= pd.Timestamp('2000-01-01')]
L.append('- Quarters since 2000 that set a new low (current vintage): ' + ', '.join(run_low))
L.append(f'- Level path (BLS level series, 2008+): 2008Q4 {lvl["2008-10-01"]:.1f}; 2017 avg {lvl["2017-01-01":"2017-12-01"].mean():.1f}; 2019 avg {lvl["2019-01-01":"2019-12-01"].mean():.1f}; 2021Q3 {lvl["2021-07-01"]:.1f}; 2023 avg {lvl["2023-01-01":"2023-12-01"].mean():.1f}; 2025 avg {lvl["2025-01-01":"2025-12-01"].mean():.1f}; 2026Q3 {lvl.iloc[-1]:.1f}.')
pre21 = idx[idx.index < '2021-01-01']
L.append(f'- Was 2026Q2 a record low when Barr likely read it (Sep 3 vintage idx 93.446)? Yes: BLS revisions in the Nov 5 release reach back only to 2021Q1, so pre-2021 history is unchanged, and its minimum is {pre21.min():.3f} ({q(pre21.idxmin())}); the lowest earlier 2021+ quarter in the Sep 3 vintage was {min(v for d,v in vint["20260903"].items() if d < pd.Timestamp("2026-04-01")):.3f} (2018+ window shown). 93.446 is below all of them. In the current vintage 2026Q2 (94.362) is no longer the lowest, because 2026Q3 (93.729) is lower.\n')
L.append('## Other "labor share" measures (BEA, FRED; not matching 52.8)')
coe = fred('fred_COE_2026-11-15.json'); ni = fred('fred_NICUR_2026-11-15.json'); gdi = fred('fred_GDI_2026-11-15.json')
L.append('| Quarter | Compensation of employees / National income (%) | Compensation / GDI (%) |\n|---|---|---|')
for t in coe.index[-4:]:
    L.append(f'| {q(t)} | {coe[t]/ni[t]*100:.1f} | {coe[t]/gdi[t]*100:.1f} |' if t in ni.index and t in gdi.index else f'| {q(t)} | n/a (2026Q3 NI/GDI not yet published) | n/a |')
L.append('\nSources: FRED COE, NICUR, GDI (BEA; pulled 2026-11-15). Neither BEA ratio is 52.8 for 2026Q2 (about 59.7 and 49.9). Business-sector (PRS84006173) index moves with nonfarm business (93.745 in 2026Q3).\n')
L.append('## Did the Q3 release revise it?')
L.append(f'Yes. 2026Q2: 93.446 (Sep 3) -> 94.362 (Nov 5) = level ~52.8 -> 53.3 (+0.5 pt); 2026Q1: 94.843 -> 95.518 (~53.6 -> 54.0); 2025Q3: 95.999 -> 95.254. 2026Q3 prelim 53.0 (idx 93.729), -0.3 pt vs revised 2026Q2. Direction of the post-2025 decline is unchanged; the ~52.8 level is gone.')
L.append('\n## Caveats')
L.append('- Barr describes it as a share of "national income"; the BLS series is a share of nonfarm business output (excludes government, nonprofits, households incl. owner-occupied housing). Barr does not name the series; the match to PRS85006174 (pre-revision) is inferred from the number, not confirmed with the Board. UNVERIFIED as his source.')
L.append('- 2020Q2 spike (58.9%) is a pandemic composition effect.')
(OUT/'B_q3_labor_share.md').write_text('\n'.join(L))
print('\n'.join(L))
