"""Shared loaders for brief A (source mapping). Run scripts from the project root with python3.
Inputs are read-only local files; nothing under 03_Data is modified."""
import json, re, os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
PI = os.path.join(ROOT, '03_Data', 'pipelines', 'Price indexes')
T244 = os.path.join(ROOT, '03_Data', 'Raw', 'BEA_Table244UD_PCE_price_source_data_2026-11-11.xlsx')
U20405 = os.path.join(PI, 'PCE', 'raw', 'BEA_NIUnderlyingDetail_U20405_2026-11-10.json')
U20404 = os.path.join(PI, 'PCE', 'raw', 'BEA_NIUnderlyingDetail_U20404_2026-11-10.json')
DALLAS = os.path.join(PI, 'PCE', 'processed', 'dallas_component_mapping.csv')
COMPONENTS = os.path.join(PI, 'PCE', 'processed', 'components.csv')
CU_ITEM = os.path.join(PI, 'CPI', 'raw', 'bls_cu_item_2026-09-27.txt')
CU_SERIES = os.path.join(PI, 'CPI', 'raw', 'bls_cu_series_2026-09-27.txt')
PC_SERIES = os.path.join(PI, 'PPI', 'raw', 'bls_pc_series_2026-09-27.txt')
WP_SERIES = os.path.join(PI, 'PPI', 'raw', 'bls_wp_series_2026-09-27.txt')
CPI_RI = os.path.join(PI, 'CPI', 'raw', 'bls_cpi_relative_importance_2025_2026-11-10.xlsx')
HANDBOOK = os.path.join(PI, 'Cross-index analysis', 'raw', 'BEA_NIPA_Handbook_Chapter5_2026-11-10.pdf')
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build')
CODE = os.path.join(SUB, 'code')
OUT = os.path.join(SUB, 'outputs')
PERIOD = '2026M09'


def norm(s):
    """Exact-match normalization: case, punctuation and whitespace only (no word changes)."""
    s = str(s).lower().replace('&', ' and ')
    s = re.sub(r"[^a-z0-9 ]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def load_t244():
    """Return list of dict rows from Table 2.4.4U-D in sheet order. Unnumbered sub-rows
    (lines 95, 276-279 detail) get line=None and parent_line = last numbered line."""
    x = pd.read_excel(T244, header=None)
    hdr = x.index[x[0].astype(str).str.strip() == 'Item'][0]
    rows, last = [], None
    for i in range(hdr + 1, len(x)):
        item, name, code, src, seas = x.iloc[i, :5].tolist()
        if isinstance(item, str) and item.startswith('*'):
            break
        if pd.isna(name) and pd.isna(src):
            continue
        clean = lambda v: None if pd.isna(v) else re.sub(r'\s+', ' ', str(v)).strip()
        if pd.notna(item):
            last = int(item)
            rows.append(dict(line=last, parent_line=None, name=clean(name), code=clean(code),
                             source=clean(src), seasonal=clean(seas), xlsx_row=i + 1))
        else:
            rows.append(dict(line=None, parent_line=last, name=clean(name), code=None,
                             source=clean(src), seasonal=clean(seas), xlsx_row=i + 1))
    return rows


def load_bea(path, periods=None):
    d = json.load(open(path))['BEAAPI']['Results']['Data']
    rec = {}
    names = {}
    for r in d:
        ln = int(r['LineNumber'])
        names[ln] = r['LineDescription']
        if periods is None or r['TimePeriod'] in periods:
            rec[(ln, r['TimePeriod'])] = float(r['DataValue'].replace(',', ''))
    return rec, names


def load_bls_list(path):
    d = pd.read_csv(path, sep='\t', dtype=str)
    d.columns = [c.strip() for c in d.columns]
    return d.apply(lambda s: s.str.strip())
