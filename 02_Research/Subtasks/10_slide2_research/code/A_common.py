"""Shared helpers for agent A (slide 2 research). Imports the audited slide 1 breadth engine read-only.

Run A_ scripts from the project root with `python3 -I`.
Tag source: 08_shock_tagging/proposed_tags.csv, column tag_final (Eli, Nov 14). Leaf key = BEA U20404/U20405 line number,
parsed from component_id ("U20404 line N / ...").
"""
import os
import re
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
SUB = os.path.join(ROOT, '02_Research', 'Subtasks', '10_slide2_research')
OUT = os.path.join(SUB, 'outputs')
TAGDIR = os.path.join(ROOT, '02_Research', 'Subtasks', '08_shock_tagging')
sys.path.insert(0, os.path.join(ROOT, '02_Research', 'Subtasks', '09_slide1_research', 'code'))
import C_common as cc  # noqa: E402  (audited engine, read-only)
from C_common import P, SCOPES, unit_table, breadth, rate, nominal_weight, LEAVES_CORE, bp, bn  # noqa: E402,F401

GROUPS = ['energy', 'tariff', 'AI', 'untagged']
VINTAGE = 'BEA U20404/U20405 vintage 2026-11-10 (data through Sep 2026); Oct 2026 = UMD audited estimate (04_oct_pce_build)'


def load_tags():
    t = pd.read_csv(os.path.join(TAGDIR, 'proposed_tags.csv'))
    t['leaf'] = t.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
    assert t.leaf.is_unique
    return t


TAGS = load_tags()
TAG_FINAL = TAGS.set_index('leaf').tag_final.to_dict()


def check_mapping():
    assert set(TAG_FINAL) == set(LEAVES_CORE), (set(TAG_FINAL) ^ set(LEAVES_CORE))
    assert len(TAG_FINAL) == 149


def slide1_checks():
    exp = {('leaf', 12, '2026-09'): 60.626, ('leaf', 12, '2026-10'): 54.038,
           ('leaf', 3, '2026-09'): 44.814, ('leaf', 3, '2026-10'): 45.467}
    for (g, back, m), want in exp.items():
        got = breadth(g, 'core', m, back)[0]
        assert abs(got - want) < 0.01, (g, back, m, got, want)
    return True


def leaf_table(end, back, tagmap=None):
    """unit_table('leaf') plus tag and weight share. w = start-of-window nominal weight; ws = share of core."""
    tagmap = tagmap or TAG_FINAL
    d = unit_table('leaf', SCOPES['core'], end, back).copy()
    d['tag'] = d.leaf.map(tagmap)
    d['ws'] = d.w / d.w.sum()
    d['over3'] = d.r > 3.0
    return d


def tag_scheme(energy_cut=None, transport_union=False, transport_replace=False, transport_quartile=False):
    """Re-apply the final rules (tag_rules.py tags_final) with a different energy rule. Returns {leaf: tag}.
    energy_cut=None -> top-quartile cutoff E_P75 (final); 0.05 -> strict. Priority AI > tariff > energy."""
    t = TAGS.copy()
    ex = pd.read_csv(os.path.join(TAGDIR, 'item_exposures_full.csv'))
    ex['leaf'] = ex.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
    ex = ex.set_index('leaf')
    w = ex.weight_latest.values
    e = ex.energy_main.values
    o = np.argsort(e)
    cw = np.cumsum(w[o])
    e_p75 = float(e[o][np.searchsorted(cw, 0.75)])
    cut = e_p75 if energy_cut is None else energy_cut
    ea = ex.energy_alt_transport.values
    oa = np.argsort(ea)
    ea_p75 = float(ea[oa][np.searchsorted(np.cumsum(w[oa]), 0.75)])
    ai = {49, 50, 51, 71}
    out = {}
    for ln, r in ex.iterrows():
        if ln == 228:
            out[ln] = 'untagged'
            continue
        if ln in ai:
            out[ln] = 'AI'
        elif r.goods_share_of_producer_value >= 0.5 and r.import_direct_goods >= 0.15 and ln not in {123, 124}:
            out[ln] = 'tariff'
        else:
            en = r.energy_main >= cut
            if transport_union:
                en = en or (r.energy_alt_transport >= 0.10)
            if transport_replace:
                en = r.energy_alt_transport >= 0.10
            if transport_quartile:
                en = r.energy_alt_transport >= ea_p75
            out[ln] = 'energy' if en else 'untagged'
    return out, e_p75
