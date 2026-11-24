"""Shared engine for brief C (breadth and component-sum gap), slide 1 research.

Run the C_ scripts from the project root with `python3 -I`, e.g.
    python3 -I "02_Research/Subtasks/09_slide1_research/code/C_breadth.py"
Reads only saved files (BEA U20404/U20405 vintage 2026-11-10 and the audited October build outputs).
Imports the audited engine in 04_oct_pce_build/code/D_common.py (read-only); the breadth logic below follows
07_breadth_reconciliation/code/recon.py (that code is not edited), and C_breadth.py checks that it reproduces
recon.py's September numbers.

Definitions
  unit        = one pricing line. 'sub' = 184 core sub-line units (13 leaves split into 48 BEA sub-lines; the
                other core leaves stay whole); 'leaf' = 149 core leaves. Headline: 212 sub-line units / 177 leaves.
  rate        = annualized k-month rate, 100*((I_t/I_{t-k})**(12/k)-1), BEFORE the 3% cutoff (strictly > 3).
  weight      = nominal spending share (U20405) of the unit in the BASE month of the window (t-k): start-of-window
                weights. For a sub-line: leaf nominal x (sub-line nominal / sum of the leaf's sub-line nominals).
                Rescaling cancels in the breadth ratio.
  October     = estimate: BEA's Sep index extended by the build's October m/m (D_build_2026-10_lines.csv, pi).
"""
import os
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SUBTASK = os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research')
OUTDIR = os.path.join(SUBTASK, 'outputs')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'code'))
import D_common as dc  # noqa: E402

OCT_LINES = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'D_build_2026-10_lines.csv')
OCT_SUMMARY = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'D_build_2026-10_summary.csv')
W_FILE = os.path.join(ROOT, '02_Research', 'Subtasks', '04_oct_pce_build', 'outputs', 'W_pce_oct_tab_lines.csv')
U20404_REL = '03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20404_2026-11-10.json'
U20405_REL = '03_Data/pipelines/Price indexes/PCE/raw/BEA_NIUnderlyingDetail_U20405_2026-11-10.json'

P = dc.P
SEP, OCT = P('2026-09'), P('2026-10')
TENANT, NPISH = dc.TENANT_LEAF, dc.NPISH_LEAF

eng = dc.Engine()
bp, bn = eng.bea_p, eng.bea_n
specs = eng.specs('2026-09-30')           # 212 pricing lines (184 core), current BEA source table
LEAVES_ALL = sorted(eng.leaves)           # 177
LEAVES_CORE = sorted(l for l in LEAVES_ALL if eng.leaf_core[l])   # 149


def is_supercore_leaf(l):
    """PCE services excluding energy and housing, as in 03_Data/pipelines/.../analyze_baskets.py supercore():
    line >= 150, excluding housing 153-164 and electricity and gas 169-171. Taken within the core set."""
    return l >= 150 and not (153 <= l <= 164) and not (169 <= l <= 171)


def is_core_services_leaf(l):
    """Core PCE services = services (line >= 150) in the core set (energy services 169-171 are not core)."""
    return l >= 150


SCOPES = {
    'core': set(LEAVES_CORE),
    'headline': set(LEAVES_ALL),
    'supercore': set(l for l in LEAVES_CORE if is_supercore_leaf(l)),
    'core_services': set(l for l in LEAVES_CORE if is_core_services_leaf(l)),
}

# ---- October estimate: pricing-line m/m (%) and within-leaf shares from the audited build
_L = pd.read_csv(OCT_LINES)
OCT_PI = _L.set_index('line').pi.to_dict()
OCT_TIER = _L.set_index('line').cat.to_dict()       # assumed / observed_published / observed_needs_seasonal / blend / proxied
OCT_SUBSHARE = _L.set_index('line').sub_share.to_dict()
OCT_LEAFOF = _L.set_index('line').leaf.to_dict()
_leaf_pi = _L.groupby('leaf').apply(lambda g: (g.sub_share * g.pi).sum() / g.sub_share.sum(), include_groups=False)
OCT_LEAF_PI = _leaf_pi.to_dict()                    # fixed-share (Sep shares) roll-up of sub-line m/m to the leaf


def bl(line):
    return 156 if line == 157 else line             # sub-line 157 (CPI rent) is priced on the leaf-156 index


def index_level(line, month, gran):
    """BEA index level; for October 2026 the estimate. gran='sub' uses the pricing-line m/m, 'leaf' the roll-up."""
    month = P(month)
    if month <= SEP:
        return bp.at[month, bl(line)]
    if month == OCT:
        pi = OCT_PI[line] if gran == 'sub' else OCT_LEAF_PI[line]
        return bp.at[SEP, bl(line)] * (1 + pi / 100)
    raise ValueError(month)


def rate(line, end, back, gran):
    end = P(end)
    return 100 * ((index_level(line, end, gran) / index_level(line, end - back, gran)) ** (12 / back) - 1)


def units(gran, leafset):
    """list of (line, leaf) pricing units"""
    if gran == 'leaf':
        return [(l, l) for l in sorted(leafset)]
    return [(ln, s['leaf']) for ln, s in specs.items() if s['leaf'] in leafset]


_SUBS_BY_LEAF = {}
for _ln, _s in specs.items():
    _SUBS_BY_LEAF.setdefault(_s['leaf'], []).append(_ln)


def nominal_weight(line, leaf, month, gran):
    """nominal spending share (level, not rescaled) of the unit in `month` (as recon.py weight())."""
    month = P(month)
    if gran == 'leaf' or line == leaf:
        return bn.at[month, leaf]
    if leaf in (TENANT, NPISH):
        return bn.at[month, leaf]
    subs = _SUBS_BY_LEAF[leaf]
    tot = sum(bn.at[month, l] for l in subs)
    return bn.at[month, leaf] * bn.at[month, line] / tot


def unit_table(gran, leafset, end, back):
    """one row per unit: line, leaf, w (start-of-window weight, level), r (annualized rate), w_end"""
    end = P(end)
    rows = []
    for line, leaf in units(gran, leafset):
        rows.append((line, leaf, nominal_weight(line, leaf, end - back, gran), rate(line, end, back, gran)))
    return pd.DataFrame(rows, columns=['line', 'leaf', 'w', 'r']).dropna()


def breadth(gran, scope, end, back, thr=3.0):
    d = unit_table(gran, SCOPES[scope], end, back)
    return 100 * d.w[d.r > thr].sum() / d.w.sum(), len(d)


def count_share(gran, scope, end, back, thr=3.0):
    d = unit_table(gran, SCOPES[scope], end, back)
    return 100 * (d.r > thr).sum() / len(d), int((d.r > thr).sum()), len(d)
