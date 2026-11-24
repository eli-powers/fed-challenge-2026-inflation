"""BEA 2017 detail import shares: imports / total U.S. supply, by BEA detail commodity.
Source (read-only, saved by subtask 08): 03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/AllTablesIO/
IOUse_Before_Redefinitions_PRO_2017_Detail.xlsx (sheet 2017): imports = -F05000 ("Imports of goods and services",
entered negative), domestic commodity output = "Total Commodity Output" column (code T007; blank code cell in the file). Total supply = T007 + imports.
NAICS -> BEA detail via the 'NAICS Codes' sheet of CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx (same parser as
subtask 17). A NAICS code matches a BEA detail commodity when either code is a prefix of the other; several matched
BEA codes are pooled (sum imports / sum supply). No match -> retry one NAICS digit shorter, down to 3 digits.
"""
import os
import re

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RAW = os.path.join(ROOT, '03_Data', 'Raw', 'BEA_IO_shock_tagging_2026-11-14')
USE = os.path.join(RAW, 'AllTablesIO', 'IOUse_Before_Redefinitions_PRO_2017_Detail.xlsx')
CXC = os.path.join(RAW, 'CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx')


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


def load():
    rows = list(openpyxl.load_workbook(USE, read_only=True, data_only=True)['2017'].iter_rows(values_only=True))
    cols = [None if c is None else str(c).strip() for c in rows[5]]
    titles = [None if c is None else str(c).strip() for c in rows[4]]
    jm = cols.index('F05000')
    jt = cols.index('T007') if 'T007' in cols else titles.index('Total Commodity Output')
    sup = {}
    for r in rows[6:]:
        if r[0] is None or str(r[0]).strip().startswith('T'):
            continue
        imp = -float(r[jm]) if isinstance(r[jm], (int, float)) else 0.0
        out = float(r[jt]) if isinstance(r[jt], (int, float)) else 0.0
        sup[str(r[0]).strip()] = (str(r[1]).strip(), imp, out + imp)
    naics = {}
    for r in list(openpyxl.load_workbook(CXC, read_only=True)['NAICS Codes'].iter_rows(values_only=True))[5:]:
        if r[3] not in (None, ''):
            naics[str(r[3]).strip()] = parse_naics(r[6])
    return sup, naics


SUP, DET_NAICS = load()


def share_for_naics(code_list):
    """code_list: NAICS strings (or 'SCRAP'). Returns (share, matched BEA codes, naics level used, note)."""
    if code_list == ['SCRAP']:
        c = 'S00401'
        _, i, s = SUP[c]
        return (i / s if s else 0.0), [c], 'SCRAP', 'BEA scrap commodity S00401'
    matched, note = set(), ''
    for n in code_list:
        m, k = set(), n
        while len(k) >= 3:
            m = {d for d, ns in DET_NAICS.items() if d in SUP and any(x.startswith(k) or k.startswith(x) for x in ns)}
            if m:
                break
            k = k[:-1]
        if m and k != n:
            note += f'{n}->broadened to {k}; '
        matched |= m
    if not matched:
        return None, [], '', 'unmatched'
    i = sum(SUP[d][1] for d in matched)
    s = sum(SUP[d][2] for d in matched)
    return (i / s if s else None), sorted(matched), '', note.strip()
