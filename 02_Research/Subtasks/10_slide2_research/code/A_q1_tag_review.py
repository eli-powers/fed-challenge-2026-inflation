"""A Q1.3: tag robustness review -> outputs/A_q1_tag_robustness.csv (data for A_q1_tag_proposals.csv).
Checks (data only): (1) leaves within a narrow band of the energy cutoff; (2) which energy-tagged leaves fall out under alternative energy
measures in item_exposures_full.csv (energy_before_redef, energy_direct_only top-quartile); (3) leaf concentration in the energy group;
(4) AI-group composition and rates; (5) 12m Sep/Oct rates of the leaves discussed.
Run from the project root: python3 -I 02_Research/Subtasks/10_slide2_research/code/A_q1_tag_review.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *
ex = pd.read_csv(os.path.join(TAGDIR, 'item_exposures_full.csv'))
ex['leaf'] = ex.component_id.str.extract(r'U20404 line (\d+)')[0].astype(int)
ex = ex.set_index('leaf')
tg = TAGS.set_index('leaf')
def p75(col):
    o = np.argsort(ex[col].values); cw = np.cumsum(ex.weight_latest.values[o]); return float(ex[col].values[o][np.searchsorted(cw, 0.75)])
rows = []
cuts = {c: p75(c) for c in ('energy_main', 'energy_before_redef', 'energy_direct_only')}
print(cuts)
en = tg[tg.tag_final == 'energy']
for l in en.index:
    r = ex.loc[l]
    rows.append(dict(leaf=l, name=r.component_name, weight_pct=round(100 * r.weight_latest, 3), energy_main=r.energy_main,
                     dist_to_cutoff_pp=round(100 * (r.energy_main - cuts['energy_main']), 3),
                     above_before_redef_q4=bool(r.energy_before_redef >= cuts['energy_before_redef']),
                     above_direct_only_q4=bool(r.energy_direct_only >= cuts['energy_direct_only']),
                     above_strict5=bool(r.energy_main >= 0.05)))
d = pd.DataFrame(rows).sort_values('weight_pct', ascending=False)
d.to_csv(os.path.join(OUT, 'A_q1_tag_robustness.csv'), index=False)
print(d.head(12).to_string())
print('energy group weight', d.weight_pct.sum(), 'n', len(d))
print('weight still energy-tagged under before-redef q4:', d[d.above_before_redef_q4].weight_pct.sum(), 'n', int(d.above_before_redef_q4.sum()))
print('weight energy-tagged also in direct-only q4:', d[d.above_direct_only_q4].weight_pct.sum(), 'n', int(d.above_direct_only_q4.sum()))
print('weight strict5:', d[d.above_strict5].weight_pct.sum(), 'n', int(d.above_strict5.sum()))
print('top3 (241,187,207) weight', d[d.leaf.isin([241, 187, 207])].weight_pct.sum())
# rates of selected leaves
for per, back in (('2026-09', 12), ('2026-10', 12), ('2026-09', 3), ('2026-10', 3)):
    t = leaf_table(per, back).set_index('leaf')
    sel = [50, 49, 71, 51, 241, 187, 207, 184, 123, 124, 9, 228]
    print(per, back, {l: round(t.r[l], 2) for l in sel}, 'ws', {l: round(100*t.ws[l], 2) for l in (50, 49, 71)})
# AI group rate decomposition (12m Sep)
t = leaf_table('2026-09', 12).set_index('leaf')
a = t[t.tag == 'AI']; print(a[['ws', 'r']])
print('energy group ex 241:', 100*t.ws[(t.tag=='energy') & (t.index != 241)].sum(), 'rate', (t.ws*t.r)[(t.tag=='energy') & (t.index != 241)].sum()/t.ws[(t.tag=='energy') & (t.index != 241)].sum())
print('leaf 241 rate', t.r[241], 'tariff group top leaves'); tt=t[t.tag=='tariff'].sort_values('ws',ascending=False).head(6); print(tt[['ws','r']])
print('tariff group rate ex leaf 9', (t.ws*t.r)[(t.tag=='tariff')&(t.index!=9)].sum()/t.ws[(t.tag=='tariff')&(t.index!=9)].sum())
