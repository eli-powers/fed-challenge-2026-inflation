"""Parse PPI stage units (commodity rows) and Dec 2025 relative importance from the BLS ID production-flow RI file.
Shared by ppi_tagged_excess.py. Run from anywhere; paths are absolute from this file.
Unit = commodity code (col C). A commodity listed under several producer-type blocks of one stage is one unit; its RI is
the sum across blocks (same price index). Col B sometimes holds a stray '#REF!' in the BLS file; only cols C/D/F are used.
RI '-' (not published) is treated as 0.
"""
import collections
import os

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
RI = os.path.join(ROOT, '03_Data', 'Raw', 'BLS_PPI_stages_2026-11-15',
                  'bls_ppi_id_production_flow_relative_importance_2026_2026-11-15.xlsx')
CAT = os.path.join(ROOT, '03_Data', 'Raw', 'bls_wp_series_2026-11-11.txt')


def stage_units(stage, col=5):
    """stage in ('54','51') -> {code: dict(name, ri, blocks)}; detail block only (stops at next 'ID5x' stage header).
    col=5: RI Dec 2025 (col F, central); col=4: RI Dec 2024 (col E) with its OWN unit universe."""
    rows = list(openpyxl.load_workbook(RI, read_only=True)['idpgrouprel26'].iter_rows(values_only=True))
    out, cur, on = collections.OrderedDict(), None, False
    for r in rows:
        k = str(r[1]).strip() if r[1] not in (None, '') else ''
        if k.startswith('ID5'):
            if k == 'ID' + stage:
                if on:          # second occurrence = summary hierarchy at end of file
                    break
                on = True
            elif len(k) == 4 and k != 'ID' + stage and on:
                break           # next stage header
            cur = k
            continue
        if on and r[2] not in (None, '') and isinstance(r[col], (int, float)):
            c = str(r[2]).strip()
            u = out.setdefault(c, dict(name=r[3], ri=0.0, blocks=[]))
            u['ri'] += r[col]
            u['blocks'].append(cur)
    return out


def catalog():
    """series_id -> (title, end_year, end_period) from the BLS wp.series file."""
    d = {}
    with open(CAT) as f:
        next(f)
        for line in f:
            p = [x.strip() for x in line.rstrip('\n').split('\t')]
            d[p[0]] = (p[5], p[-2], p[-1])
    return d


if __name__ == '__main__':
    for s in ('54', '51'):
        u = stage_units(s)
        print(s, len(u), round(sum(v['ri'] for v in u.values()), 3))
