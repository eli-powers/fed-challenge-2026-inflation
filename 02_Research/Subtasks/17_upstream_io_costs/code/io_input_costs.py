"""17: upstream purchased-input cost pressure by consumer shock group (Method C, input-output). Not audited.

Run from the project root:
    python3 -I "02_Research/Subtasks/17_upstream_io_costs/code/io_input_costs.py" [--fetch]
--fetch downloads (BEA summary import matrix; BLS PPI PCU series not already in 03_Data/Raw/BLS_PPI_*);
without it the script reads only saved raw files. BLS key from .env (never written).

RULES (copied from GO.md, Eli Nov 17 2026; decided in advance, not reopened)
 1. Consumer items/tags: the 2B left chart's 149 core PCE leaves, tag_final from 08_shock_tagging/proposed_tags.csv,
    same leaf set and weights as 10_slide2_research/code/G_baseline_attribution.py via 09_slide1_research/code/C_common.py
    (read-only).
 2. Consumer item -> producing industries: BEA PCE bridge table (2017 benchmark, detailed); producers' value, plus
    wholesale / retail / transport margins as separate "inputs" (D4).
 3. Industry -> inputs: BEA 2017 detailed benchmark IO tables, producers' prices.
      Central: total requirements (domestic, commodity-by-commodity), whole supply chain = L_d - I.
      Sensitivity 1: direct requirements (first-tier suppliers only), A_d.
      Sensitivity 2: latest BEA summary annual tables (~71 industries) instead of the 2017 detail.
 4. Inputs -> prices: BLS PPI industry indexes (PCU, NSA) matched by NAICS. Exact NAICS match; else the next broader
    NAICS level; else drop the input and renormalise. Report dropped weight share per group (flag if > 15%).
    Trade and transport margins priced with the PPI wholesale trade, retail trade and transportation & warehousing
    industry indexes. Energy inputs use the matching energy PPIs (no special treatment).
 5. Imports excluded (domestic requirements only). PPI excludes imports; BLS import price indexes exclude tariffs.
 6. Labour / value added excluded (purchased inputs only). Also compute each group's purchased-input share of output.
 7. Index: group input-cost 12m inflation = sum_j share_jg x PPI 12m %ch_j; shares from step 3 combined with the
    consumer-leaf weights within the group (start-of-window PCE weights, as in G). Baseline = mean of monthly 12m rates
    over 2018-01..2019-12.

AS IMPLEMENTED (deviations / fallbacks are logged in report.md):
  * BEA's published 2017 detail CxC total-requirements table includes imported inputs (its column sums match
    (I-A_total)^-1, not the domestic inverse), and BEA's import matrices exist only BEFORE redefinitions. So the domestic
    tables are built here from the before-redefinitions use, make and import matrices: commodity-by-commodity, industry
    technology, A = (U/g) (V/q); A_d = ((U - M)/g) (V/q); L_d = (I - A_d)^-1.
  * Rule 4 "next broader level" is applied repeatedly (6->5->4->3 digits), then the BLS sector aggregate where one
    exists (42 wholesale, 44-45 retail, 48-49 transportation & warehousing, 51 information, 21 mining, 31-33 mfg).
    NAICS 2017 codes renamed in NAICS 2022 (PPI now uses 2022 codes) are matched through a small crosswalk (XWALK).
    A PPI series qualifies only with complete monthly data 2017-01..2026-10.
  * Domestic use = max(U - M, 0) cell by cell: 85 detail cells would otherwise be negative (imports > use for 325414
    biological products in a few industries; BEA's negative used-goods S00402 entries). Their total is ~0.1 of A_d.
  * Leaf input vector: x_i = sum_c PV_ic * M[:, c] + (wholesale, retail, transport margins of i as three inputs),
    M = L_d - I (central) or A_d (direct). Shares s_ij = x_ij / sum over priced inputs.
  * Purchased-input share of output (theta_i) = (sum_c PV_ic * colsum(A_d)_c + margins) / purchasers' value (domestic,
    direct; used for contribution version b). The incl.-imports analogue (colsum A) is reported alongside.
  * Summary sensitivity: 2023 summary use/make/import (latest in BEA's AllTablesIO zip retrieved 2026-11-14 and the
    import-matrix file 1997-2023); the 2017 detail bridge is aggregated to summary commodity codes.
"""
import glob
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

import numpy as np
import openpyxl
import pandas as pd

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '17_upstream_io_costs')
OUT = os.path.join(SUB, 'outputs')
RAW_DET = os.path.join(ROOT, '03_Data', 'Raw', 'BEA_IO_shock_tagging_2026-11-14')      # reused, read-only
RAW_SUM = os.path.join(ROOT, '03_Data', 'Raw', 'BEA_IO_summary_2026-11-17')
RAW_PPI = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_io_inputs_2026-11-17')
PC_SERIES = os.path.join(ROOT, '03_Data', 'Raw', 'bls_pc_series_2026-11-11.txt')
TAGS = os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging', 'proposed_tags.csv')
SUM_IMP_URL = 'https://apps.bea.gov/industry/xls/io-annual/ImportMatrices_Before_Redefinitions_SUM_1997-2023.xlsx'
SUM_IMP = os.path.join(RAW_SUM, 'ImportMatrices_Before_Redefinitions_SUM_1997-2023_retrieved_2026-11-17.xlsx')
SUM_YEAR = '2023'
FETCH = '--fetch' in sys.argv
os.makedirs(OUT, exist_ok=True)

sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402  (read-only import; same leaf set/weights as G)

GROUPS = ['energy', 'tariff', 'AI', 'untagged']
GLABEL = {'energy': 'Energy-exposed', 'tariff': 'Tariff-exposed', 'AI': 'AI-related', 'untagged': 'Everything else'}
M_START, M_END = pd.Period('2017-01', 'M'), pd.Period('2026-10', 'M')
BASE = pd.period_range('2018-01', '2019-12', freq='M')
PATH = pd.period_range('2018-01', '2026-10', freq='M')
KEY_MONTHS = [pd.Period(m, 'M') for m in ('2025-03', '2026-02', '2026-10')]
MARGINS = {'MRG_WHOLESALE': 'PCUAWHLTRAWHLTR', 'MRG_RETAIL': 'PCUARETTRARETTR', 'MRG_TRANSPORT': 'PCUATRNWRATRNWR'}
SECTOR_AGG = {'42': 'PCUAWHLTRAWHLTR', '44': 'PCUARETTRARETTR', '48': 'PCUATRNWRATRNWR', '51': 'PCUAINFO-AINFO-',
              '21': 'PCUOMIN--OMIN--', '31': 'PCUOMFG--OMFG--'}
# NAICS 2017 -> NAICS 2022 prefix renames used by current PPI codes (retail and information sectors)
XWALK = {'446': '456', '447': '457', '448': '458', '451': '459', '452': '455', '453': '459', '442': '449', '443': '449',
         '5111': '5131', '5112': '5132', '5151': '5161', '5152': '5162', '5173': '5171', '51913': '51621', '5191': '5192'}


def code(x):
    return None if x is None else str(x).strip()


def num(v):
    return float(v) if isinstance(v, (int, float)) else 0.0


def read_matrix(wb_or_path, sheet, hdr_row=5):
    wb = openpyxl.load_workbook(wb_or_path, read_only=True, data_only=True) if isinstance(wb_or_path, str) else wb_or_path
    rows = list(wb[sheet].iter_rows(values_only=True))
    cols = [code(c) for c in rows[hdr_row]]
    data = {}
    for r in rows[hdr_row + 1:]:
        if r[0] is None:
            continue
        data[code(r[0])] = {cols[j]: num(r[j]) for j in range(2, len(cols)) if cols[j]}
    return data, [c for c in cols[2:] if c]


def build_A(use, make, make_cols, imp):
    """commodity-by-commodity, industry technology: A = (U/g)(V/q); domestic uses U - M."""
    inds =[k for k in make if not k.startswith('T') and k != 'IOCode']
    comms = [c for c in make_cols if not c.startswith('T')]
    V = np.array([[make[i].get(c, 0) for c in comms] for i in inds])
    g, q = V.sum(1), V.sum(0)
    U = np.array([[use.get(c, {}).get(i, 0) for i in inds] for c in comms])
    M = np.array([[imp.get(c, {}).get(i, 0) for i in inds] for c in comms])
    gs, qs = np.where(g > 0, g, 1.0), np.where(q > 0, q, 1.0)
    D = V / qs
    A = (U / gs) @ D
    Ad = (np.clip(U - M, 0, None) / gs) @ D     # domestic use clipped at 0 (BEA cells with imports > use, negative used-goods entries)
    return comms, A, Ad


# ------------------------------------------------------------------ BEA detail (2017)
print('reading BEA 2017 detail tables ...')
det_use, _ = read_matrix(os.path.join(RAW_DET, 'AllTablesIO', 'IOUse_Before_Redefinitions_PRO_2017_Detail.xlsx'), '2017')
det_make, det_mc = read_matrix(os.path.join(RAW_DET, 'AllTablesIO', 'IOMake_Before_Redefinitions_2017_Detail.xlsx'), '2017')
det_imp, _ = read_matrix(os.path.join(RAW_DET, 'ImportMatrices_Before_Redefinitions_DET_2017_retrieved_2026-11-14.xlsx'), '2017')
det_tr, det_trc = read_matrix(os.path.join(RAW_DET, 'CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx'), '2017', hdr_row=4)
DC, DA, DAd = build_A(det_use, det_make, det_mc, det_imp)
nD = len(DC)
DL = np.linalg.inv(np.eye(nD) - DAd)
DLt = np.linalg.inv(np.eye(nD) - DA)
Lb = np.array([[det_tr.get(r, {}).get(c, 0) for c in DC] for r in DC])
tr_check = dict(median_absdiff_colsum_vs_total=float(np.median(np.abs(DLt.sum(0) - Lb.sum(0)))),
                median_absdiff_colsum_vs_domestic=float(np.median(np.abs(DL.sum(0) - Lb.sum(0)))),
                mean_colsum_bea=float(Lb.sum(0).mean()), mean_colsum_total=float(DLt.sum(0).mean()),
                mean_colsum_domestic=float(DL.sum(0).mean()))
print('BEA published TR vs built:', {k: round(v, 4) for k, v in tr_check.items()})
assert tr_check['median_absdiff_colsum_vs_total'] < tr_check['median_absdiff_colsum_vs_domestic']
assert (DAd >= 0).all() and (DL >= -1e-12).all()

# NAICS sheet: detail code -> NAICS 2017 codes; detail -> summary
naics_rows = list(openpyxl.load_workbook(os.path.join(RAW_DET, 'CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx'),
                                         read_only=True)['NAICS Codes'].iter_rows(values_only=True))


def parse_naics(s):
    out = set()
    if s is None:
        return out
    for tok in re.split(r'[,\n]', str(s)):
        tok = tok.strip().replace('*', '')
        if not tok or not re.match(r'^\d', tok):
            continue
        if '-' in tok:
            base, end = tok.split('-', 1)
            k = len(end)
            lo, hi = int(base[-k:]), int(end)
            out |= {base[:-k] + str(d).zfill(k) for d in range(lo, hi + 1)}
        else:
            out.add(tok)
    return out


DET_NAICS, DET2SUM, cur_sum = {}, {}, None
for r in naics_rows[5:]:
    if r[0] is None and r[1] is not None and re.match(r'^[0-9A-Z]{2,7}$', str(r[1]).strip()):
        cur_sum = str(r[1]).strip()
    if r[3] not in (None, ''):
        d = str(r[3]).strip()
        DET_NAICS[d] = parse_naics(r[6])
        DET2SUM[d] = cur_sum

# PCE bridge 2017 detail
bridge = {}
for r in list(openpyxl.load_workbook(os.path.join(RAW_DET, 'PCEBridge_2017_DET_retrieved_2026-11-14.xlsx'),
                                     read_only=True)['2017'].iter_rows(values_only=True))[5:]:
    if r[0] is not None and str(r[0]).strip().isdigit():
        bridge.setdefault(int(r[0]), []).append((code(r[2]), *(num(x) for x in r[4:9])))   # c, PV, T, W, R, PUR

# ------------------------------------------------------------------ BEA summary (latest annual)
if FETCH and not os.path.exists(SUM_IMP):
    os.makedirs(RAW_SUM, exist_ok=True)
    req = urllib.request.Request(SUM_IMP_URL, headers={'User-Agent': 'Mozilla/5.0'})
    open(SUM_IMP, 'wb').write(urllib.request.urlopen(req, timeout=120).read())
print('reading BEA summary tables', SUM_YEAR, '...')
zf = zipfile.ZipFile(os.path.join(RAW_DET, 'AllTablesIO_retrieved_2026-11-14.zip'))
sum_use, _ = read_matrix(openpyxl.load_workbook(io.BytesIO(zf.read('IOUse_Before_Redefinitions_PRO_1997-2023_Summary.xlsx')),
                                                read_only=True, data_only=True), SUM_YEAR)
sum_make, sum_mc = read_matrix(openpyxl.load_workbook(io.BytesIO(zf.read('IOMake_Before_Redefinitions_PRO_1997-2023_Summary.xlsx')),
                                                      read_only=True, data_only=True), SUM_YEAR)
sum_imp, _ = read_matrix(SUM_IMP, SUM_YEAR)
sum_make = {k: v for k, v in sum_make.items() if k != 'IOCode'}
SC, SA, SAd = build_A(sum_use, sum_make, sum_mc, sum_imp)
nS = len(SC)
SL = np.linalg.inv(np.eye(nS) - SAd)
assert (SAd >= 0).all() and (SL >= -1e-12).all()
SUM_NAICS = {}
for d, s in DET2SUM.items():
    SUM_NAICS.setdefault(s, set()).update(DET_NAICS.get(d, set()))
# summary codes used by BEA for scrap/used/other/government are not in the NAICS sheet hierarchy
det2sum_fix = {'S00401': 'Other', 'S00402': 'Used', 'S00300': 'Other', 'S00900': 'Other'}

# ------------------------------------------------------------------ PPI availability and concordance
pcs = pd.read_csv(PC_SERIES, sep='\t', dtype=str)
pcs.columns = [c.strip() for c in pcs.columns]
for c in pcs.columns:
    pcs[c] = pcs[c].str.strip()
ind = pcs[(pcs.industry_code == pcs.product_code) & (pcs.seasonal == 'U')].copy()
ind['ok_span'] = ((ind.begin_year.astype(int) < 2017) | ((ind.begin_year.astype(int) == 2017) & (ind.begin_period == 'M01'))) & \
                 (ind.end_year.astype(int) >= 2026)
TITLE = dict(zip(ind.series_id, ind.series_title))
BAD_DATA = set()          # series dropped after loading data (incomplete 2017-01..2026-10)


def avail():
    a = ind[ind.ok_span & ~ind.series_id.isin(BAD_DATA)]
    return {ic.rstrip('-'): sid for ic, sid in zip(a.industry_code, a.series_id) if re.match(r'^\d', ic)}


def sector_of(n):
    s = n[:2]
    return {'45': '44', '49': '48', '32': '31', '33': '31'}.get(s, s)


def xw(p):
    for k in sorted(XWALK, key=len, reverse=True):
        if p.startswith(k):
            return XWALK[k] + p[len(k):]
    return None


def match(naics):
    """rule 4: returns (series_id, level_label, matched_code) or (None, 'dropped', '')"""
    AV = avail()
    if not naics:
        return None, 'dropped (no NAICS)', ''
    codes = sorted(naics)
    p = os.path.commonprefix(codes)
    single = len(codes) == 1
    for L in range(len(p), 2, -1):
        for cand, tag in ((p[:L], ''), (xw(p[:L]), ' via NAICS-2022 crosswalk')):
            if cand and cand in AV and (cand in ind.industry_code.str.rstrip('-').values):
                exact = single and L == len(p)
                return AV[cand], ('exact' if exact else f'broader ({L}-digit)') + tag, cand
    secs = {sector_of(c) for c in codes}
    if len(secs) == 1 and next(iter(secs)) in SECTOR_AGG and SECTOR_AGG[next(iter(secs))] not in BAD_DATA:
        return SECTOR_AGG[next(iter(secs))], 'sector aggregate', next(iter(secs))
    return None, 'dropped (no PPI)', ''


def concord(level):
    names = DC if level == 'detail' else SC
    nmap = DET_NAICS if level == 'detail' else SUM_NAICS
    rows = []
    for c in names:
        sid, lab, m = match(nmap.get(c, set()))
        rows.append(dict(level=level, bea_code=c, naics_2017=','.join(sorted(nmap.get(c, set()))), ppi_series=sid,
                         match=lab, matched_naics=m, ppi_title=TITLE.get(sid, sid)))
    for k, sid in MARGINS.items():
        rows.append(dict(level=level, bea_code=k, naics_2017='margin', ppi_series=sid if sid not in BAD_DATA else None,
                         match='margin index', matched_naics='', ppi_title=TITLE.get(sid, sid)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ PPI data: reuse saved raw, fetch the rest
def load_raw():
    obs = {}
    files = sorted(glob.glob(os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_*', '*.json')))
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for s in d.get('Results', {}).get('series', []):
            if not s['seriesID'].startswith('PCU'):
                continue
            for o in s['data']:
                if o['period'].startswith('M') and o['period'] != 'M13':
                    try:
                        v = float(o['value'])
                    except ValueError:
                        continue
                    obs.setdefault(s['seriesID'], {})[pd.Period(f"{o['year']}-{o['period'][1:]}", 'M')] = (v, os.path.relpath(f, ROOT))
    return obs


def complete(obs, sid):
    have = obs.get(sid, {})
    return all(m in have for m in pd.period_range(M_START, M_END, freq='M'))


def bls_key():
    for line in open(os.path.expanduser('.env')):
        line = line.strip()
        if line.startswith('export '):
            line = line[7:].strip()
        if line.startswith('BLS_API_KEY='):
            return line.split('=', 1)[1].strip().strip('"\'')
    raise SystemExit('BLS_API_KEY not found in .env')


def fetch(ids):
    os.makedirs(RAW_PPI, exist_ok=True)
    key = bls_key()
    n0 = len(glob.glob(os.path.join(RAW_PPI, '*.json')))
    for k in range(0, len(ids), 50):
        body = {'seriesid': ids[k:k + 50], 'startyear': '2016', 'endyear': '2026', 'registrationkey': key}
        req = urllib.request.Request('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=json.dumps(body).encode(),
                                     headers={'Content-type': 'application/json'})
        d = json.load(urllib.request.urlopen(req, timeout=180))
        assert d['status'] == 'REQUEST_SUCCEEDED' and not any('limit' in x for x in d.get('message', [])), d.get('message')
        assert {x['seriesID'] for x in d['Results']['series']} == set(ids[k:k + 50])
        n0 += 1
        json.dump(d, open(os.path.join(RAW_PPI, f'bls_api_pcu_io_inputs_2016_2026_batch{n0}_2026-11-17.json'), 'w'))
    print(f'fetched {len(ids)} series')


obs = load_raw()
for it in range(6):
    CON = pd.concat([concord('detail'), concord('summary')], ignore_index=True)
    need = sorted(set(CON.ppi_series.dropna()))
    missing = [s for s in need if s not in obs]
    if missing and FETCH:
        fetch(missing)
        obs = load_raw()
    if [s for s in need if s not in obs]:
        raise SystemExit(f'PPI series not in raw; rerun with --fetch: {[s for s in need if s not in obs][:10]}')
    bad = {s for s in need if not complete(obs, s)}
    if not bad - BAD_DATA:
        break
    print(f'iteration {it}: {len(bad - BAD_DATA)} series incomplete 2017-01..2026-10 -> walking up: {sorted(bad - BAD_DATA)}')
    BAD_DATA |= bad
CON.to_csv(os.path.join(OUT, 'ppi_concordance.csv'), index=False)
need = sorted(set(CON.ppi_series.dropna()))
LEVEL = pd.DataFrame({s: {m: obs[s][m][0] for m in pd.period_range(M_START, M_END, freq='M')} for s in need})
SRCFILE = {s: obs[s][M_END][1] for s in need}
R12 = (LEVEL / LEVEL.shift(12) - 1) * 100
R12 = R12.loc[PATH]
assert not R12.isna().any().any()
R12.to_csv(os.path.join(OUT, 'ppi_12m_rates.csv'))
pd.Series(SRCFILE, name='raw_file').to_csv(os.path.join(OUT, 'ppi_raw_file_by_series.csv'))

# ------------------------------------------------------------------ leaves, tags, weights
t = pd.read_csv(TAGS)
t['leaf'] = t.component_id.str.extract(r'line (\d+)').astype(int)
TAG = dict(zip(t.leaf, t.tag_final))
BLINES = {lf: [int(x) for x in str(b).split(';')] for lf, b in zip(t.leaf, t.bridge_lines)}
LEAVES = sorted(cc.LEAVES_CORE)
assert set(LEAVES) == set(TAG) and len(LEAVES) == 149


def leaf_weights(m):
    """start-of-window (t-12) nominal PCE weights of the 149 core leaves, as in G (cc.unit_table, leaf granularity)."""
    return pd.Series({lf: cc.bn.at[m - 12, lf] for lf in LEAVES})


def leaf_inputs(version):
    """returns X (leaves x inputs, $ of purchased inputs per leaf, from 2017 bridge), input names, theta table"""
    if version in ('central', 'direct'):
        names, Mx, Ad, At, idx = DC, (DL - np.eye(nD) if version == 'central' else DAd), DAd, DA, {c: i for i, c in enumerate(DC)}
        tomap = lambda c: c  # noqa: E731
    else:
        names, Mx, Ad, At, idx = SC, SL - np.eye(nS), SAd, SA, {c: i for i, c in enumerate(SC)}
        tomap = lambda c: det2sum_fix.get(c, DET2SUM.get(c))  # noqa: E731
    a_d, a_t = Ad.sum(0), At.sum(0)
    inputs = list(names) + list(MARGINS)
    X = pd.DataFrame(0.0, index=LEAVES, columns=inputs)
    th, unmapped = [], {}
    for lf in LEAVES:
        flat = [r for b in BLINES[lf] for r in bridge.get(b, [])]
        pur = sum(r[5] for r in flat)
        assert pur > 0, lf
        vec = np.zeros(len(names))
        num_d = num_t = 0.0
        for c, pv, tr_, wh, rt, _ in flat:
            k = idx.get(tomap(c))
            if k is None:
                unmapped[c] = unmapped.get(c, 0) + pv
                continue
            vec += pv * Mx[:, k]
            num_d += pv * a_d[k]
            num_t += pv * a_t[k]
        X.loc[lf, list(names)] = vec
        mw, mr, mt = (sum(r[3] for r in flat), sum(r[4] for r in flat), sum(r[2] for r in flat))
        X.loc[lf, ['MRG_WHOLESALE', 'MRG_RETAIL', 'MRG_TRANSPORT']] = [mw, mr, mt]
        th.append(dict(leaf=lf, purch_value_2017=pur, theta_domestic=(num_d + mw + mr + mt) / pur,
                       theta_incl_imports=(num_t + mw + mr + mt) / pur, margin_share_of_purch=(mw + mr + mt) / pur))
    return X, pd.DataFrame(th).set_index('leaf'), unmapped


def run(version):
    level = 'summary' if version == 'summary' else 'detail'
    con = CON[CON.level == level].set_index('bea_code')
    X, TH, unmapped = leaf_inputs(version)
    priced = [c for c in X.columns if pd.notna(con.ppi_series.get(c))]
    Xs = X.div(X.sum(axis=1), axis=0)                         # leaf shares over all purchased inputs (incl. unpriced)
    dropped_leaf = 1 - Xs[priced].sum(axis=1)                 # unpriced share per leaf (before renormalising)
    Sh = X[priced].div(X[priced].sum(axis=1), axis=0)         # renormalised priced shares, sum to 1 per leaf
    assert np.allclose(Sh.sum(axis=1), 1), Sh.sum(axis=1)[~np.isclose(Sh.sum(axis=1), 1)]
    sid = con.ppi_series.reindex(priced)
    Rin = pd.DataFrame({c: R12[sid[c]] for c in priced})  # months x inputs
    leaf_rate = Rin @ Sh.T                               # months x leaves
    recs, gshare = [], {}
    for m in PATH:
        w = leaf_weights(m)
        for g in GROUPS:
            L_ = [lf for lf in LEAVES if TAG[lf] == g]
            wg = w[L_] / w[L_].sum()
            recs.append(dict(month=str(m), group=g, rate=float((wg * leaf_rate.loc[m, L_]).sum()),
                             pce_share=float(w[L_].sum() / w.sum()), theta_d=float((wg * TH.theta_domestic[L_]).sum()),
                             theta_t=float((wg * TH.theta_incl_imports[L_]).sum()),
                             dropped=float((wg * dropped_leaf[L_]).sum())))
            if m in KEY_MONTHS or m in BASE:
                gshare[(str(m), g)] = (Sh.loc[L_].T @ wg)       # input shares within group
    P_ = pd.DataFrame(recs)
    base = P_[P_.month.isin([str(m) for m in BASE])].groupby('group').rate.mean()
    P_['baseline'] = P_.group.map(base)
    P_['excess'] = P_.rate - P_.baseline
    P_['contrib_plain_pp'] = P_.pce_share * P_.excess
    P_['contrib_scaled_pp'] = P_.pce_share * P_.theta_d * P_.excess
    P_['version'] = version
    # top inputs by contribution to the Oct 2026 excess: share_now*r_now - mean_base(share_t*r_t); sums to the excess
    top = []
    mo = str(M_END)
    for g in GROUPS:
        now = gshare[(mo, g)] * R12.loc[M_END, sid].values
        bmean = sum(gshare[(str(b), g)] * R12.loc[b, sid].values for b in BASE) / len(BASE)
        contrib = now - bmean
        ex = P_[(P_.month == mo) & (P_.group == g)].excess.iloc[0]
        assert abs(contrib.sum() - ex) < 1e-8, (g, contrib.sum(), ex)
        s_g = P_[(P_.month == mo) & (P_.group == g)].pce_share.iloc[0]
        for c in contrib.abs().sort_values(ascending=False).index[:10]:
            top.append(dict(version=version, group=g, input=c, input_name=con.ppi_title.get(c) if c.startswith('MRG') else c,
                            ppi_series=sid[c], ppi_title=TITLE.get(sid[c], sid[c]), share_oct26=float(gshare[(mo, g)][c]),
                            r12_oct26=float(R12.loc[M_END, sid[c]]),
                            r12_base_avg=float(R12.loc[BASE, sid[c]].mean()),
                            contrib_to_excess_pp=float(contrib[c]), contrib_plain_pp=float(contrib[c] * s_g)))
    # diagnostics
    level_w = []
    for g in GROUPS:
        L_ = [lf for lf in LEAVES if TAG[lf] == g]
        w = leaf_weights(M_END)
        wg = w[L_] / w[L_].sum()
        gs_all = Xs.loc[L_].T @ wg                                  # group shares over all inputs (sum 1)
        assert abs(gs_all.sum() - 1) < 1e-9 and abs(gshare[(mo, g)].sum() - 1) < 1e-9
        for lab, v in gs_all.groupby(con.match.reindex(gs_all.index).fillna('dropped (unmapped)')).sum().items():
            level_w.append(dict(version=version, group=g, match=lab, weight=float(v)))
        unp = gs_all.drop(priced).sort_values(ascending=False)[:8]
        for c, v in unp.items():
            DROPPED.append(dict(version=version, group=g, bea_code=c, naics_2017=con.naics_2017.get(c), share_of_all_inputs=float(v)))
    return P_, pd.DataFrame(top), pd.DataFrame(level_w), Sh, TH, unmapped, gshare


ALL, TOP, LEV, UNM, DROPPED = [], [], [], {}, []
SAVED = {}
for v in ('central', 'direct', 'summary'):
    print('running', v)
    P_, T_, L_, Sh, TH, unm, gsh = run(v)
    ALL.append(P_), TOP.append(T_), LEV.append(L_)
    UNM[v] = unm
    SAVED[v] = (Sh, TH, gsh)
    Sh.to_csv(os.path.join(OUT, f'leaf_input_shares_{v}.csv'))
    TH.to_csv(os.path.join(OUT, f'leaf_theta_{v}.csv'))
ALL = pd.concat(ALL, ignore_index=True)
TOP = pd.concat(TOP, ignore_index=True)
LEV = pd.concat(LEV, ignore_index=True)
ALL.to_csv(os.path.join(OUT, 'group_monthly_all_versions.csv'), index=False)
ALL[ALL.version == 'central'].to_csv(os.path.join(OUT, 'group_monthly_path_central.csv'), index=False)
TOP.to_csv(os.path.join(OUT, 'top10_inputs_oct2026.csv'), index=False)
LEV.to_csv(os.path.join(OUT, 'diag_match_level_weights_oct2026.csv'), index=False)
pd.DataFrame(DROPPED).to_csv(os.path.join(OUT, 'diag_top_dropped_inputs_oct2026.csv'), index=False)
pd.DataFrame({lf: leaf_weights(m) for m in PATH for lf in [str(m)]}).to_csv(os.path.join(OUT, 'leaf_pce_weights_start_of_window.csv'))
pd.Series(TAG, name='tag_final').to_csv(os.path.join(OUT, 'leaf_tags.csv'))

# ------------------------------------------------------------------ summary tables
rows = []
for v in ('central', 'direct', 'summary'):
    d = ALL[ALL.version == v]
    for g in GROUPS:
        x = d[d.group == g].set_index('month')
        rec = dict(version=v, group=g, baseline_2018_19=x.baseline.iloc[0])
        for m in KEY_MONTHS:
            k = str(m)
            rec.update({f'rate_{k}': x.at[k, 'rate'], f'excess_{k}': x.at[k, 'excess'], f'pce_share_{k}': x.at[k, 'pce_share'],
                        f'contrib_plain_{k}': x.at[k, 'contrib_plain_pp'], f'contrib_scaled_{k}': x.at[k, 'contrib_scaled_pp']})
        rec.update(theta_domestic_oct26=x.at['2026-10', 'theta_d'], theta_incl_imports_oct26=x.at['2026-10', 'theta_t'],
                   dropped_share_oct26=x.at['2026-10', 'dropped'], dropped_flag=x.at['2026-10', 'dropped'] > 0.15)
        rows.append(rec)
    tot = dict(version=v, group='TOTAL')
    for m in KEY_MONTHS:
        k = str(m)
        y = d[d.month == k]
        tot.update({f'contrib_plain_{k}': y.contrib_plain_pp.sum(), f'contrib_scaled_{k}': y.contrib_scaled_pp.sum(),
                    f'pce_share_{k}': y.pce_share.sum()})
    rows.append(tot)
SUMM = pd.DataFrame(rows)
SUMM.to_csv(os.path.join(OUT, 'summary_table.csv'), index=False)

# diagnostics: spot checks of 3 PPI values against the raw JSON, coverage counts
spot = []
for sid_, m in (('PCUAWHLTRAWHLTR', '2026-10'), ('PCU32411-32411-', '2025-10'), (need[len(need) // 2], '2019-06')):
    if sid_ not in LEVEL.columns:
        continue
    f = os.path.join(ROOT, obs[sid_][pd.Period(m, 'M')][1])
    raw = None
    for s in json.load(open(f))['Results']['series']:
        if s['seriesID'] == sid_:
            for o in s['data']:
                if f"{o['year']}-{o['period'][1:]}" == m:
                    raw = float(o['value'])
    spot.append(dict(series=sid_, month=m, used=LEVEL.at[pd.Period(m, 'M'), sid_], raw_json=raw, file=obs[sid_][pd.Period(m, 'M')][1]))
SPOT = pd.DataFrame(spot)
SPOT.to_csv(os.path.join(OUT, 'diag_ppi_spot_checks.csv'), index=False)
assert (SPOT.used == SPOT.raw_json).all()
cov = CON.groupby(['level', 'match']).size().rename('n_inputs').reset_index()
cov.to_csv(os.path.join(OUT, 'diag_concordance_counts.csv'), index=False)
json.dump(dict(tr_check=tr_check, n_ppi_series=len(need), bad_data_series=sorted(BAD_DATA),
               unmapped_bridge_commodities={k: {c: round(x, 1) for c, x in v.items()} for k, v in UNM.items()},
               ppi_prelim_note='BLS PPI: last 4 months (Jul-Oct 2026) preliminary at retrieval',
               n_detail_commodities=nD, n_summary_commodities=nS),
          open(os.path.join(OUT, 'diagnostics.json'), 'w'), indent=1)

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
print(tr_check)
print(cov.to_string(index=False))
cols = ['version', 'group', 'baseline_2018_19'] + [f'rate_{m}' for m in KEY_MONTHS] + [f'excess_{m}' for m in KEY_MONTHS] + \
       ['theta_domestic_oct26', 'dropped_share_oct26']
print(SUMM[[c if isinstance(c, str) else str(c) for c in cols]].round(3).to_string(index=False))
print(SUMM[['version', 'group'] + [f'contrib_plain_{m}' for m in KEY_MONTHS] + [f'contrib_scaled_{m}' for m in KEY_MONTHS]].round(3).to_string(index=False))
print('unmapped bridge commodities:', {k: len(v) for k, v in UNM.items()})
print('bad data series:', sorted(BAD_DATA))
