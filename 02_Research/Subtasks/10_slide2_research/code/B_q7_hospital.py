"""Brief B, Q7: the hospital base effect. Oct 2025 m/m of PPI hospitals (PCU622---622---, NSA) and of BEA PCE leaves
184-186 (SA, BEA U20404 vintage 2026-11-10), vs Jul 2025-Jan 2026 and the 2018-2025 distribution; first-release vintage
of the Oct 2025 PPI observation from ALFRED; BLS footnote codes; Medicare inpatient sub-index.

Run from the project root:  python3 -I "02_Research/Subtasks/10_slide2_research/code/B_q7_hospital.py"
Inputs: 03_Data/Raw/BLS_PPI_hospitals_2026-11-15/*.json (B_q7_fetch_bls.py), 03_Data/Raw/ALFRED_PCU622622_all_vintages_from2024-11_2026-11-11.json,
        BEA U20404 via the audited engine (C_common -> D_common, read-only).
Writes outputs/B_q7_hospital.csv, outputs/B_q7_hospital_octobers.csv
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402

OUT = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research', 'outputs')
RAW = os.path.join(ROOT, '03_Data', 'Raw')

# ---- BLS series (NSA), with footnotes
lv, foot, titles = {}, {}, {}
for f in ('bls_api_ppi_hospitals_2006_2015.json', 'bls_api_ppi_hospitals_2016_2026.json'):
    d = json.load(open(os.path.join(RAW, 'BLS_PPI_hospitals_2026-11-15', f)))
    for s in d['Results']['series']:
        titles[s['seriesID']] = s.get('catalog', {}).get('series_title', '')
        for o in s['data']:
            if not o['period'].startswith('M') or o['period'] == 'M13':
                continue
            m = pd.Period(f"{o['year']}-{o['period'][1:]}", 'M')
            lv.setdefault(s['seriesID'], {})[m] = float(o['value'])
            foot.setdefault(s['seriesID'], {})[m] = ';'.join(x.get('code', '') + ':' + x.get('text', '') for x in o['footnotes'] if x)
L = pd.DataFrame(lv).sort_index()
MM = 100 * (L / L.shift(1) - 1)
PPI = 'PCU622---622---'
MED = 'WPU5121010111'

# ---- BEA leaves 184-186 (SA price index, U20404 vintage 2026-11-10)
bea = cc.bp[[184, 185, 186]]
bea_mm = 100 * (bea / bea.shift(1) - 1)

# ---- ALFRED: vintages of the Oct 2025 observation (FRED id PCU622622)
al = json.load(open(os.path.join(RAW, 'ALFRED_PCU622622_all_vintages_from2024-11_2026-11-11.json')))['observations']
al = pd.DataFrame(al)
al_oct = al[al.date == '2025-10-01'].sort_values('realtime_start')
al_sep = al[al.date == '2025-09-01'].sort_values('realtime_start')
first_oct = al_oct.iloc[0]
sep_at_first = al_sep[(al_sep.realtime_start <= first_oct.realtime_start)].iloc[-1]
fr_mm = 100 * (float(first_oct.value) / float(sep_at_first.value) - 1)

rows = []
O = pd.Period('2025-10', 'M')
win = pd.period_range('2025-07', '2026-01', freq='M')


def stats(series, m, lo='2018-01', hi='2025-12', label=''):
    s = series.loc[pd.Period(lo, 'M'):pd.Period(hi, 'M')].dropna()
    v = series[m]
    octs = s[[p.month == 10 for p in s.index]]
    nonoct = s[[p.month != 10 for p in s.index]]
    return dict(value_mm_pct=round(v, 4), dist_window=f'{lo}..{hi}', n=len(s), mean=round(s.mean(), 4), sd=round(s.std(), 4),
                z=round((v - s.mean()) / s.std(), 2), pctile=round(100 * (s < v).mean() + 50 * (s == v).mean(), 1),
                rank_desc=int((s > v).sum() + 1), max_month=str(s.idxmax()), max_value=round(s.max(), 4),
                oct_mean=round(octs.mean(), 4), oct_n=len(octs), z_vs_nonoct=round((v - nonoct.mean()) / nonoct.std(), 2),
                z_vs_octobers=round((v - octs.mean()) / octs.std(), 2) if len(octs) > 2 else None)


for sid, name, ser, sa in ((PPI, 'PPI hospitals (industry 622)', MM[PPI], 'NSA'),
                           ('PCU6221--6221--', 'PPI general medical & surgical hospitals', MM['PCU6221--6221--'], 'NSA'),
                           (MED, 'PPI Medicare patients: hospital inpatient care (commodity)', MM[MED], 'NSA'),
                           ('BEA_184', 'BEA PCE leaf 184 nonprofit hospitals (price index)', bea_mm[184], 'SA (BEA)'),
                           ('BEA_185', 'BEA PCE leaf 185 proprietary hospitals', bea_mm[185], 'SA (BEA)'),
                           ('BEA_186', 'BEA PCE leaf 186 government hospitals', bea_mm[186], 'SA (BEA)')):
    st = stats(ser, O)
    rec = dict(series_id=sid, name=name, seasonal=sa, ref_month='2025-10', **st)
    for m in list(win) + [pd.Period('2026-09', 'M'), pd.Period('2026-10', 'M')]:
        rec[f'mm_{m}'] = round(ser.get(m, np.nan), 4)
    if not sid.startswith('BEA'):
        rec['nsa_12m_2026-09'] = round(100 * (L[sid][pd.Period('2026-09', 'M')] / L[sid][pd.Period('2025-09', 'M')] - 1), 4)
        rec['nsa_12m_2026-10_prelim'] = round(100 * (L[sid][pd.Period('2026-10', 'M')] / L[sid][pd.Period('2025-10', 'M')] - 1), 4)
        rec['bls_footnotes_2026-10'] = foot.get(sid, {}).get(pd.Period('2026-10', 'M'), '')[:12]
    rec['avg_mm_2025-11_to_2026-09'] = round(ser.loc[pd.Period('2025-11', 'M'):pd.Period('2026-09', 'M')].mean(), 4)
    rec['bls_footnotes_2025-10'] = foot.get(sid, {}).get(O, 'n/a (BEA)') or 'none'
    rec['source'] = ('BLS API v2, 03_Data/Raw/BLS_PPI_hospitals_2026-11-15/ (retrieved 2026-11-15)' if not sid.startswith('BEA')
                     else 'BEA NIPA U20404 vintage 2026-11-10 (pipelines/Price indexes/PCE/raw)')
    rows.append(rec)
R = pd.DataFrame(rows)
R['alfred_oct2025_first_release_vintage'] = ''
R.loc[R.series_id == PPI, 'alfred_oct2025_first_release_vintage'] = (
    f'{first_oct.realtime_start} value {first_oct.value}; Sep 2025 in that vintage {sep_at_first.value}; first-release m/m {fr_mm:.4f}%; '
    f'later vintages: ' + '; '.join(f"{r.realtime_start}={r.value}" for r in al_oct.itertuples()))
R.to_csv(os.path.join(OUT, 'B_q7_hospital.csv'), index=False)

# ---- every October: NSA PPI 622, Medicare inpatient, BEA leaf 184 SA
oc = []
for y in range(2006, 2027):
    m = pd.Period(f'{y}-10', 'M')
    oc.append(dict(year=y, ppi622_oct_mm_nsa=round(MM[PPI].get(m, np.nan), 4), medicare_inpatient_oct_mm_nsa=round(MM[MED].get(m, np.nan), 4),
                   bea184_oct_mm_sa=round(bea_mm[184].get(m, np.nan), 4) if m in bea_mm.index else np.nan,
                   bea184_avg_other_months_sa=round(bea_mm[184][[p.year == y and p.month != 10 for p in bea_mm.index]].mean(), 4) if y >= 2018 else np.nan,
                   ppi622_avg_other_months_nsa=round(MM[PPI][[p.year == y and p.month != 10 for p in MM.index]].mean(), 4)))
OC = pd.DataFrame(oc)
OC['implied_seasonal_gap_pp(nsa_ppi_minus_bea_sa)'] = (OC.ppi622_oct_mm_nsa - OC.bea184_oct_mm_sa).round(4)
OC.to_csv(os.path.join(OUT, 'B_q7_hospital_octobers.csv'), index=False)

pd.set_option('display.width', 250)
print(R.drop(columns=['source', 'alfred_oct2025_first_release_vintage']).T.to_string())
print(R.alfred_oct2025_first_release_vintage[R.series_id == PPI].iloc[0])
print(OC.to_string())
print({k: titles[k] for k in titles})
