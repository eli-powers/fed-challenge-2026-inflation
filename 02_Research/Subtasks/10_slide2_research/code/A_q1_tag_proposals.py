"""A Q1.3: write outputs/A_q1_tag_proposals.csv (proposals for Eli; tag_final is NOT changed). Numbers computed here.
Run from the project root: python3 -I 02_Research/Subtasks/10_slide2_research/code/A_q1_tag_proposals.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *
ex = pd.read_csv(os.path.join(TAGDIR, 'item_exposures_full.csv'))
ex['leaf'] = ex.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
ex = ex.set_index('leaf')
rob = pd.read_csv(os.path.join(OUT, 'A_q1_tag_robustness.csv')).set_index('leaf')
t12 = leaf_table('2026-09', 12).set_index('leaf')
tO = leaf_table('2026-10', 12).set_index('leaf')
W = lambda ls: round(100 * ex.weight_latest[list(ls)].sum(), 3)
en_tot = W(rob.index)
def tagshare(l): return round(100 * ex.weight_latest[l] / ex.weight_latest[rob.index].sum(), 1)
ai_contrib = (t12.ws * t12.r)[t12.tag == 'AI']
rows = []
def add(kind, leaves, name, cur, prop, reason):
    rows.append(dict(type=kind, leaves=';'.join(map(str, leaves)), component=name, current_tag=cur, proposed_tag=prop,
                     weight_affected_pct_of_core=W(leaves), reason=reason))
add('proposal (Eli to decide)', [187], 'Nursing homes (52)', 'energy', 'untagged',
    f"Knife-edge: energy share {ex.energy_main[187]:.5f} vs cutoff 0.03468 (+{rob.dist_to_cutoff_pp[187]:.3f} pp). Drops out of the top quartile under the before-redefinitions measure (energy_before_redef) in item_exposures_full.csv; the only energy-tagged leaf to do so (41 of 42 stay). Its 12m rate is {t12.r[187]:.2f}% (Sep), {tO.r[187]:.2f}% (Oct est.). 1.46% of core weight = {tagshare(187)}% of the energy group.")
add('flag (no change proposed)', [241], 'Other purchased meals', 'energy', 'energy (keep)',
    f"Largest energy-tagged leaf: {W([241])}% of core = {tagshare(241)}% of the energy group (energy share {ex.energy_main[241]:.3f}, I-O total including indirect inputs; first-round (direct-only) share {ex.energy_direct_only[241]:.3f}). Energy group ex leaf 241 = {W([l for l in rob.index if l != 241])}% of core. Top 3 (241, 187, 207) = {W([241,187,207])}% of the {en_tot}% group.")
add('flag (no change proposed)', [309, 125], 'Hairdressing salons (309); Other medical products (125)', 'untagged', 'untagged (keep)',
    f"Just below the cutoff: 309 at {100*(ex.energy_main[309]-0.03468):+.3f} pp, 125 at {100*(ex.energy_main[125]-0.03468):+.3f} pp. Mirror image of 187 and 26 (+{rob.dist_to_cutoff_pp[26]:.3f} pp): four leaves within 0.1 pp of the cutoff.")
add('flag (no change proposed)', [50], 'Computer software and accessories', 'AI', 'AI (keep)',
    f"Leaf 50 is {W([50])}% of core and {100*ai_contrib[50]/ai_contrib.sum():.0f}% of the AI group's 12m (Sep) contribution (leaf 50 rate {t12.r[50]:.1f}% 12m Sep, {tO.r[50]:.1f}% Oct est.; 3m ann. {leaf_table('2026-09',3).set_index('leaf').r[50]:.1f}% Sep, {leaf_table('2026-10',3).set_index('leaf').r[50]:.1f}% Oct est.). AI-group results are close to a one-leaf result. Software appears in the narrow list via the 2017-bridge data-processing/hosting mapping, not as AI-specific pricing.")
add('flag (no change proposed)', [49, 71, 51], 'PCs/peripherals; telephones; other info. processing equipment', 'AI', 'AI (keep)',
    "AI+tariff overlap flag is on import share only: these HTS headings (8471, 8517.13) were excepted from the 2025 reciprocal tariffs (Apr 11, 2025 memo), from the Section 122 surcharge and from the Section 301 forced-labor tariffs; see A_q1_tariff_exemption.md. Priority AI > tariff is consistent with the exemption.")
add('flag (no change proposed)', [123, 124], 'Prescription and nonprescription drugs', 'untagged', 'untagged (keep; Eli decision Nov 14)',
    f"Direct import share {ex.import_direct_goods[123]:.3f} would trip the tariff rule; Eli's override cites realized pharma tariffs ~0. Pharmaceuticals are in the Section 122 exempt list (Proclamation 11012 para 14(f)) [O] and the Section 301 notice lists certain pharmaceuticals among exemptions [O]. 12m rates: Rx {t12.r[123]:.2f}%, non-Rx {t12.r[124]:.2f}% (Sep). A Section 232 pharma action was reported for July-Sept 2026 [S]; not verified here.")
add('flag (no change proposed)', [7, 8, 9], 'New domestic autos, new foreign autos, new light trucks', 'tariff', 'tariff (keep)',
    f"{W([7,8,9])}% of core ({100*ex.weight_latest[[7,8,9]].sum()/ex.weight_latest[ex.index.isin(TAGS[TAGS.tag_final=='tariff'].leaf)].sum():.0f}% of the tariff group). Passenger vehicles and certain light trucks appear in the Section 122 exemption list (Proclamation 11012 para 14(h)) and Section 232-covered articles are exempt from both the Section 122 and Section 301 layers (para 14(k); FR 2026-15181 preamble) [O]; any tariff on these goods therefore comes through Section 232 (not itself verified here). Leaf 9 (new light trucks, {W([9])}%) runs {t12.r[9]:.2f}% 12m (Sep), which holds the tariff group's rate down: group rate ex leaf 9 = {(t12.ws*t12.r)[(t12.tag=='tariff')&(t12.index!=9)].sum()/t12.ws[(t12.tag=='tariff')&(t12.index!=9)].sum():.2f}% vs {(t12.ws*t12.r)[t12.tag=='tariff'].sum()/t12.ws[t12.tag=='tariff'].sum():.2f}% with it.")
add('flag (no change proposed)', [228], 'Lotteries', 'untagged', 'untagged (keep)',
    f"Recomputed energy share {ex.energy_main[228]:.4f} matches the file and is above the cutoff, so the untagging is an override, not a rule outcome. The tag_rules.py note calls it an I-O mapping artifact (S00203); this agent did not verify that claim.")
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'A_q1_tag_proposals.csv'), index=False)
print(pd.DataFrame(rows)[['type', 'component', 'weight_affected_pct_of_core']])
for r in rows: print(r['component'], '|', r['reason'][:400]); print()
