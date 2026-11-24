"""A: Q1 mapping check + slide 1 reproduction checks + tag rule re-derivation. Prints results and writes outputs/A_q1_mapping_check.csv"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *

check_mapping()
print('149 core leaves map one-to-one onto proposed_tags rows: OK')
slide1_checks()
print('slide 1 reproduction (leaf core 12m Sep 60.626, Oct 54.038; 3m Sep 44.814, Oct 45.467): OK')
summ = pd.read_csv(os.path.join(TAGDIR, 'tag_summary.csv'))
summ = summ[summ.scheme == 'tag_final'].set_index('tag')
rows = []
for g in GROUPS:
    s = TAGS[TAGS.tag_final == g]
    # weights from U20405 nominal shares in Sep 2026 (latest) and from file weight_latest
    nom = pd.Series({l: bn.at[P('2026-09'), l] for l in LEAVES_CORE}); nom = nom / nom.sum()
    wn = nom[s.leaf].sum()
    rows.append(dict(tag=g, n_items=len(s), n_items_summary=int(summ.at[g, 'n_items']),
                     weight_latest_file=round(s.weight_latest.sum(), 4), weight_summary=summ.at[g, 'core_weight_share'],
                     weight_U20405_Sep2026=round(float(wn), 4)))
    assert len(s) == summ.at[g, 'n_items'] and abs(round(s.weight_latest.sum(), 4) - summ.at[g, 'core_weight_share']) < 1e-9
df = pd.DataFrame(rows)
print(df)
# re-derive tag_final from rules
tf, p75 = tag_scheme()
bad = [l for l in TAG_FINAL if tf[l] != TAG_FINAL[l]]
print('E_P75 =', round(p75, 5), '; leaves where re-derived rule != tag_final:', bad)
assert not bad
df.to_csv(os.path.join(OUT, 'A_q1_mapping_check.csv'), index=False)
