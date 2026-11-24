"""A Q3: tagged vs untagged breadth (weighted leaf, >3%, start-of-window weights), time series, sensitivities, Oct 12m decomposition.

Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/A_q3_breadth.py  (from the project root)
Notation per leaf i: s_i = start-of-window share of core spending, r_i annualized k-month rate, 1[r_i>3].
  breadth_all      = 100 * sum_i s_i 1[r_i>3]                      (pp of core weight; slide 1 leaf definition)
  contribution_g   = 100 * sum_{i in g} s_i 1[r_i>3]               (pp of core weight; sum_g = breadth_all)
  breadth_within_g = 100 * contribution_g / (100 * sum_{i in g} s_i) = share of the group's own weight with r>3
Oct 12m decomposition (window Sep: base 2025-09 shares s^S, rates r^S; Oct: base 2025-10 shares s^O, rates r^O):
  change_g = contrib^O_g - contrib^S_g = flip_g + wshift_g
  flip_g   = 100 * sum_{i in g} s^O_i (1[r^O_i>3] - 1[r^S_i>3])     rate crossings at October weights
  wshift_g = 100 * sum_{i in g} (s^O_i - s^S_i) 1[r^S_i>3]          weight shift holding Sep status
  (exact: s^O 1^O - s^S 1^S = s^O(1^O - 1^S) + (s^O - s^S) 1^S)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *

check_mapping(); slide1_checks()
PER = [('2026-09', 'BEA published'), ('2026-10', 'UMD estimate (est.)')]
HZ = [(12, '12m'), (3, '3m_ann')]


def group_stats(d, groups=GROUPS):
    out = {}
    for g in groups:
        x = d[d.tag == g]
        out[g] = dict(n=len(x), n_over3=int(x.over3.sum()), ws=x.ws.sum(), contrib=100 * x.ws[x.over3].sum(),
                      within=(100 * x.ws[x.over3].sum() / x.ws.sum()) if len(x) else np.nan)
    return out


# ------------------------------------------------------------------ 1. period table
rows = []
for per, st in PER:
    for back, hz in HZ:
        d = leaf_table(per, back)
        gs = group_stats(d)
        tot = 100 * d.ws[d.over3].sum()
        assert abs(sum(v['contrib'] for v in gs.values()) - tot) < 1e-9
        for g in GROUPS:
            v = gs[g]
            rows.append(dict(period=per, status=st, horizon=hz, group=g, n_leaves=v['n'], n_leaves_over_3pct=v['n_over3'],
                             weight_share_pct=round(100 * v['ws'], 3), breadth_within_group_pct=round(v['within'], 3),
                             contribution_to_core_breadth_pp=round(v['contrib'], 3), core_breadth_pp=round(tot, 3),
                             share_of_core_breadth_pct=round(100 * v['contrib'] / tot, 2), vintage=VINTAGE))
        rows.append(dict(period=per, status=st, horizon=hz, group='ALL_core', n_leaves=len(d), n_leaves_over_3pct=int(d.over3.sum()),
                         weight_share_pct=100.0, breadth_within_group_pct=round(tot, 3), contribution_to_core_breadth_pp=round(tot, 3),
                         core_breadth_pp=round(tot, 3), share_of_core_breadth_pct=100.0, vintage=VINTAGE))
# supplementary: untagged excluding the three hospital leaves (184-186), which all price off one PPI series
for per, st in PER:
    for back, hz in HZ:
        d = leaf_table(per, back)
        x = d[(d.tag == 'untagged') & ~d.leaf.isin([184, 185, 186])]
        tot = 100 * d.ws[d.over3].sum()
        rows.append(dict(period=per, status=st, horizon=hz, group='untagged_ex_hospital_184_186 (supplementary, not additive)', n_leaves=len(x),
                         n_leaves_over_3pct=int(x.over3.sum()), weight_share_pct=round(100 * x.ws.sum(), 3),
                         breadth_within_group_pct=round(100 * x.ws[x.over3].sum() / x.ws.sum(), 3),
                         contribution_to_core_breadth_pp=round(100 * x.ws[x.over3].sum(), 3), core_breadth_pp=round(tot, 3),
                         share_of_core_breadth_pct=round(100 * 100 * x.ws[x.over3].sum() / tot / 100, 2), vintage=VINTAGE))
t1 = pd.DataFrame(rows)
t1.to_csv(os.path.join(OUT, 'A_q3_tagged_breadth.csv'), index=False)
print(t1[['period', 'horizon', 'group', 'weight_share_pct', 'breadth_within_group_pct', 'contribution_to_core_breadth_pp']].to_string())

# ------------------------------------------------------------------ 2. monthly time series 2018-01 .. 2026-10
months = [P(f'{y}-{m:02d}') for y in range(2018, 2027) for m in range(1, 13) if (y, m) <= (2026, 10)]
ts = []
for mth in months:
    rec = dict(month=str(mth), status='BEA published' if mth <= P('2026-09') else 'UMD estimate (est.)')
    for back, hz in HZ:
        d = leaf_table(str(mth), back)
        gs = group_stats(d)
        tot = 100 * d.ws[d.over3].sum()
        rec[f'core_breadth_{hz}'] = tot
        for g in GROUPS:
            rec[f'{g}_within_{hz}'] = gs[g]['within']
            rec[f'{g}_contrib_{hz}'] = gs[g]['contrib']
            rec[f'{g}_weight_pct_{hz}'] = 100 * gs[g]['ws']
    ts.append(rec)
ts = pd.DataFrame(ts)
# cross-check vs the audited slide 1 time series (leaf columns)
c = pd.read_csv(os.path.join(ROOT, '02_Research/Subtasks/09_slide1_research/outputs/C_breadth_ts.csv')).set_index('month')
m = ts.set_index('month')
assert np.abs(m.core_breadth_12m - c.core_breadth_12m_leaf).max() < 6e-4
assert np.abs(m.core_breadth_3m_ann - c.core_breadth_3m_ann_leaf).max() < 6e-4
print('time series core breadth matches C_breadth_ts.csv leaf columns (max diff < 0.0006)')
avg = ts[(ts.month >= '2018-01') & (ts.month <= '2019-12')].drop(columns=['month', 'status']).mean()
avg['month'] = 'AVG_2018-01_to_2019-12'; avg['status'] = 'average of 24 months'
ts_out = pd.concat([ts, pd.DataFrame([avg])], ignore_index=True)
ts_out = ts_out.round(3)
ts_out.insert(2, 'vintage', VINTAGE)
ts_out.to_csv(os.path.join(OUT, 'A_q3_tagged_breadth_ts.csv'), index=False)
print(avg.drop(['month', 'status']).astype(float).round(2).to_string())

# ------------------------------------------------------------------ 3. sensitivities
schemes = {'final (top-quartile energy, E>=3.47%)': tag_scheme(),
           'a: strict 5% energy cutoff (E>=5%)': tag_scheme(energy_cut=0.05),
           'b1: all-transport counted as energy (union with final energy)': tag_scheme(transport_union=True),
           'b3: all-transport in the energy block, same top-quartile rule on energy_alt_transport': tag_scheme(transport_quartile=True),
           'b2: transport-inclusive energy_transport_sens>=0.10 replaces energy rule': tag_scheme(transport_replace=True)}
sens = []
for name, (tm, cut) in schemes.items():
    for per, st in PER:
        for back, hz in HZ:
            d = leaf_table(per, back, tm)
            gs = group_stats(d)
            tot = 100 * d.ws[d.over3].sum()
            d['c'] = d.ws * d.r
            S = d.c.sum()
            gg = d.groupby('tag').agg(s=('ws', 'sum'), C=('c', 'sum')).reindex(GROUPS)
            A = gg.C - gg.s * 2.0
            for g in GROUPS:
                v = gs[g]
                sens.append(dict(scheme=name, energy_cutoff=round(cut if 'strict' not in name else 0.05, 5), period=per, status=st, horizon=hz, group=g,
                                 n_leaves=v['n'], weight_share_pct=round(100 * v['ws'], 3), breadth_within_group_pct=round(v['within'], 3),
                                 contribution_to_core_breadth_pp=round(v['contrib'], 3), core_breadth_pp=round(tot, 3),
                                 above_target_a_pp=round(A[g], 4), share_of_above_target_a=round(A[g] / A.sum(), 4), vintage=VINTAGE))
sens = pd.DataFrame(sens)
sens.to_csv(os.path.join(OUT, 'A_q3_sensitivity.csv'), index=False)
for name in schemes:
    x = sens[(sens.scheme == name) & (sens.period == '2026-09') & (sens.horizon == '12m')]
    print(name, dict(zip(x.group, zip(x.n_leaves, x.weight_share_pct, x.breadth_within_group_pct))))
chg = {name: {g: TAG_FINAL for g in []} for name in schemes}
for name, (tm, cut) in schemes.items():
    diff = [l for l in tm if tm[l] != TAG_FINAL[l]]
    print(name, 'leaves changed vs final:', diff)

# ------------------------------------------------------------------ 4. Oct 12m breadth change by tag
dS = leaf_table('2026-09', 12).set_index('leaf')
dO = leaf_table('2026-10', 12).set_index('leaf')
assert (dS.index == dO.index).all()
iS, iO = dS.over3.astype(float), dO.over3.astype(float)
flip = 100 * dO.ws * (iO - iS)
wsh = 100 * (dO.ws - dS.ws) * iS
tot_change = 100 * (dO.ws * iO).sum() - 100 * (dS.ws * iS).sum()
assert abs(tot_change - (flip.sum() + wsh.sum())) < 1e-9
print('Oct-Sep 12m breadth change', tot_change, 'flip', flip.sum(), 'weight shift', wsh.sum())
rows = []
for g in GROUPS + ['ALL_core']:
    mask = (dS.tag == g) if g != 'ALL_core' else pd.Series(True, index=dS.index)
    rows.append(dict(group=g, n_leaves=int(mask.sum()), weight_share_sep_window_pct=round(100 * dS.ws[mask].sum(), 3),
                     weight_share_oct_window_pct=round(100 * dO.ws[mask].sum(), 3),
                     contribution_sep_pp=round(100 * (dS.ws * iS)[mask].sum(), 3), contribution_oct_pp=round(100 * (dO.ws * iO)[mask].sum(), 3),
                     change_pp=round(100 * (dO.ws * iO)[mask].sum() - 100 * (dS.ws * iS)[mask].sum(), 3),
                     flip_crossings_pp=round(flip[mask].sum(), 3), weight_shift_pp=round(wsh[mask].sum(), 3),
                     n_down_crossings=int(((iS == 1) & (iO == 0) & mask).sum()), n_up_crossings=int(((iS == 0) & (iO == 1) & mask).sum()),
                     breadth_within_sep_pct=round(100 * (dS.ws * iS)[mask].sum() / dS.ws[mask].sum(), 3),
                     breadth_within_oct_pct=round(100 * (dO.ws * iO)[mask].sum() / dO.ws[mask].sum(), 3),
                     detail='', vintage=VINTAGE))
t4 = pd.DataFrame(rows)
assert abs(t4[t4.group != 'ALL_core'].change_pp.sum() - t4[t4.group == 'ALL_core'].change_pp.iloc[0]) < 2e-3
# hospital leaves
for l in (184, 185, 186):
    rows.append(dict(group=f'leaf {l} (hospital)', n_leaves=1, weight_share_sep_window_pct=round(100 * dS.ws[l], 3), weight_share_oct_window_pct=round(100 * dO.ws[l], 3),
                     contribution_sep_pp=round(100 * dS.ws[l] * iS[l], 3), contribution_oct_pp=round(100 * dO.ws[l] * iO[l], 3),
                     change_pp=round(100 * dO.ws[l] * iO[l] - 100 * dS.ws[l] * iS[l], 3), flip_crossings_pp=round(flip[l], 3), weight_shift_pp=round(wsh[l], 3),
                     n_down_crossings=int(iS[l] == 1 and iO[l] == 0), n_up_crossings=int(iS[l] == 0 and iO[l] == 1),
                     breadth_within_sep_pct=np.nan, breadth_within_oct_pct=np.nan,
                     detail=f"tag_final={dS.tag[l]}; Sep 12m rate {dS.r[l]:.3f}%, Oct est {dO.r[l]:.3f}%", vintage=VINTAGE))
hosp = [184, 185, 186]
rows.append(dict(group='hospital leaves 184-186 (sum)', n_leaves=3, weight_share_sep_window_pct=round(100 * dS.ws[hosp].sum(), 3), weight_share_oct_window_pct=round(100 * dO.ws[hosp].sum(), 3),
                 contribution_sep_pp=round(100 * (dS.ws * iS)[hosp].sum(), 3), contribution_oct_pp=round(100 * (dO.ws * iO)[hosp].sum(), 3),
                 change_pp=round(100 * (dO.ws * iO)[hosp].sum() - 100 * (dS.ws * iS)[hosp].sum(), 3), flip_crossings_pp=round(flip[hosp].sum(), 3), weight_shift_pp=round(wsh[hosp].sum(), 3),
                 n_down_crossings=int(((iS[hosp] == 1) & (iO[hosp] == 0)).sum()), n_up_crossings=0,
                 breadth_within_sep_pct=np.nan, breadth_within_oct_pct=np.nan, detail='all three priced off PPI PCU622---622---; tags: ' + ','.join(dS.tag[hosp]), vintage=VINTAGE))
# non-hospital untagged
nh = (dS.tag == 'untagged') & ~dS.index.isin(hosp)
rows.append(dict(group='untagged excluding hospital leaves', n_leaves=int(nh.sum()), weight_share_sep_window_pct=round(100 * dS.ws[nh].sum(), 3), weight_share_oct_window_pct=round(100 * dO.ws[nh].sum(), 3),
                 contribution_sep_pp=round(100 * (dS.ws * iS)[nh].sum(), 3), contribution_oct_pp=round(100 * (dO.ws * iO)[nh].sum(), 3),
                 change_pp=round(100 * (dO.ws * iO)[nh].sum() - 100 * (dS.ws * iS)[nh].sum(), 3), flip_crossings_pp=round(flip[nh].sum(), 3), weight_shift_pp=round(wsh[nh].sum(), 3),
                 n_down_crossings=int(((iS == 1) & (iO == 0) & nh).sum()), n_up_crossings=int(((iS == 0) & (iO == 1) & nh).sum()),
                 breadth_within_sep_pct=np.nan, breadth_within_oct_pct=np.nan, detail='untagged less leaves 184-186', vintage=VINTAGE))
t4 = pd.DataFrame(rows)
t4.to_csv(os.path.join(OUT, 'A_q3_oct12m_drop_by_tag.csv'), index=False)
print(t4.drop(columns=['vintage']).to_string())
assert all(TAG_FINAL[l] == 'untagged' for l in hosp)
print('hospital leaves 184-186 are untagged: OK')
