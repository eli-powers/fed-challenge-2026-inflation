"""A Q2: extract Bowman's decomposition paragraph from the saved RTF (macOS textutil -> text, then Python search) and
write outputs/A_q2_bowman_quote.md with a comparison to A_q2_attribution.csv. Run from the project root with python3 -I."""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
RTF = os.path.join(ROOT, '02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf')
OUT = os.path.join(ROOT, '02_Research/Subtasks/10_slide2_research/outputs')
txt = subprocess.run(['textutil', '-convert', 'txt', '-stdout', RTF], capture_output=True, text=True, check=True).stdout
paras = [p.strip() for p in txt.split('\n') if p.strip()]
idx = [i for i, p in enumerate(paras) if 'one-fourth' in p]
assert len(idx) == 1
para = paras[idx[0]]
prev = paras[idx[0] - 1]
nxt = paras[idx[0] + 1]
foot = [p for p in paras if re.match(r'^\d+\. ', p)]
decomp_footnote = [p for p in foot if re.search(r'(?i)tariff|decompos|attribut|one-fourth|energy', p)]
a = pd.read_csv(os.path.join(OUT, 'A_q2_attribution.csv'))


def tab(method):
    s = a[(a.method == method) & (a.horizon == '12m')]
    lines = ['| Period | Energy | Tariff | AI | Untagged | Total above-target (pp) |', '|---|---|---|---|---|---|']
    for per in ('2026-09', '2026-10'):
        x = s[s.period == per].set_index('group')
        lines.append(f'| {per}{" (est.)" if per == "2026-10" else ""} | ' + ' | '.join(f'{100*x.share_of_above_target[g]:.1f}%' for g in ('energy', 'tariff', 'AI', 'untagged'))
                     + f' | {x.total_above_target_allocated.iloc[0]:.3f} |')
    return '\n'.join(lines)


md = f"""# Bowman's decomposition: exact words and comparison

**Source (opened, local primary copy):** `02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf` (Vice Chair for Supervision Michelle W. Bowman, "The U.S. Economy and Considerations for Monetary Policy", Council on Foreign Relations, Nov 10, 2026; original https://www.federalreserve.gov/newsevents/speech/bowman20261110a.htm). Text extracted with `textutil` and searched in Python (`code/A_q2_bowman.py`). [O: local copy; the federalreserve.gov original was not re-fetched by this agent]

## The paragraph (section "Inflation", 2nd paragraph of that section)

> {para}

Preceding paragraph (context): "{prev}"

Following paragraph: "{nxt}"

**Footnotes in the speech:** {len(foot)} footnotes (1-{len(foot)}). None gives a method, data source or breakdown for the one-fourth split. Footnote-search hits for tariff/decompos/attribut/energy: {decomp_footnote if decomp_footnote else 'none'}. So the method behind the split is not disclosed in the speech. The speech also says 12m core PCE "likely moved up further to 3.3 percent in October" (our Oct estimate: {a[(a.period=='2026-10')&(a.horizon=='12m')].published_or_est_core_rate_R.iloc[0]:.2f}%).

## What Bowman says vs our tag-scheme shares (12m, share of above-target core PCE)

Bowman, 12 months to September: tariffs ~25%, energy ~25%, AI ~25%, "persistent effects from the inflationary shocks in recent years" ~25%.

**Method a (central): each group owes 2% on its own weight** (above-target = contribution - weight share x 2)
{tab('a')}

**Method b: excess over 2% only (leaves running above 2%; below-target leaves do not offset)**
{tab('b')}

**Method c: the whole 2% charged to the untagged group**
{tab('c')}

Weights (core, start of Sep-2026 12m window): energy {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='energy')].weight_share.iloc[0]:.1f}%, tariff {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='tariff')].weight_share.iloc[0]:.1f}%, AI {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='AI')].weight_share.iloc[0]:.1f}%, untagged {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='untagged')].weight_share.iloc[0]:.1f}%.

## Her fourth piece vs the tag scheme
- Bowman's fourth piece ("persistent effects from the inflationary shocks in recent years") is a **cause**, not a group of items. A tag scheme assigns each leaf to one group; it has no residual cause. The nearest analogue in our scheme is **untagged** (items with no energy, tariff or AI link), but untagged items can also carry second-round effects of the three shocks and effects of the earlier shocks (2021-22). Whether untagged = her fourth is a mapping assumption, not something the speech supports. [interpretation flag, not a finding]
- Her split is by cause (each of the 3 shocks ~25% of above-target), ours is by item exposure; an AI-demand shock can lift untagged services (e.g. via wages or rents), and an energy shock lifts non-energy items through costs. Item tags can't see this.
- Our untagged group is {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='untagged')].weight_share.iloc[0]:.0f}% of core weight and carries {100*a[(a.period=='2026-09')&(a.horizon=='12m')&(a.method=='a')&(a.group=='untagged')].share_of_above_target.iloc[0]:.0f}% of above-target core PCE under method a, about double her 25% for the fourth piece.
"""
open(os.path.join(OUT, 'A_q2_bowman_quote.md'), 'w').write(md)
print(md)
