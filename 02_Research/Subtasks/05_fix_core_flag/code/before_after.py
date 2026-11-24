"""Before/after table for the core-flag fix (2026-11-14). Before = archive/pre_corefix_2026-11-14, after = live processed files.
Both use BEA vintage 2026-11-10 (Sep 2026 data). Run from repo root or anywhere."""
from pathlib import Path
import filecmp, pandas as pd
PI = Path(__file__).resolve().parents[4] / "03_Data/pipelines/Price indexes"
B, A = PI / "archive/pre_corefix_2026-11-14", PI
OUT = Path(__file__).resolve().parents[1]
rows = []
def add(metric, before, after, src):
    rows.append(dict(metric=metric, before=before, after=after, change=(after - before) if isinstance(before, float) else "", source=src))
for tag, root in (("before", B), ("after", A)):
    pass
def comp(root):
    return pd.read_csv(root / "PCE/processed/components.csv")
cb, ca = comp(B), comp(A)
for name, f in (("components.csv", "PCE/processed/components.csv"),):
    pass
def core_stats(c):
    h, k = c[c.index_name == "PCE headline"], c[c.index_name == "PCE core"]
    return dict(n=len(k), w=h[h.in_core == "Y"].weight_latest.sum() * 100,
                c1=k.contrib_1m_calc.sum(), c3=k.contrib_3m_ann_calc.sum(), c12=k.contrib_12m_calc.sum(),
                hn=h.component_id.str.contains("line").sum())
sb, sa = core_stats(cb), core_stats(ca)
add("PCE headline: mapped leaves (count)", float(sb["hn"]), float(sa["hn"]), "PCE/processed/components.csv")
add("RETRIEVAL-stage PCE core: leaves (count)", float(sb["n"]), float(sa["n"]), "PCE/processed/components.csv")
add("Core weight, % of total PCE (Sep 2026; BEA line 374/1 = 88.88)", sb["w"], sa["w"], "components.csv weight_latest, PCE headline rows in_core=Y")
for h, k in (("1m", "c1"), ("3m ann.", "c3"), ("12m", "c12")):
    add(f"RETRIEVAL-stage PCE core: sum of component contributions, {h} (pp)", sb[k], sa[k], "components.csv PCE core rows")
def recon(root):
    r = pd.read_csv(root / "PCE/processed/reconciliation.csv")
    return r
rb, ra = recon(B), recon(A)
for nm in ("PCE core", "PCE headline"):
    for h in ("1m", "3m_ann", "12m"):
        g = lambda r: float(r[(r.index_name == nm) & (r.horizon == h)].gap_publisher_less_components_pp_calc.iloc[0])
        try: add(f"RETRIEVAL-stage {nm}: published less sum of contributions, {h} (pp)", g(rb), g(ra), "PCE/processed/reconciliation.csv")
        except IndexError: pass
ic = lambda root: pd.read_csv(root / "Cross-index analysis/processed/index_coverage.csv").set_index("index").loc["PCE core"]
ib, ia = ic(B), ic(A)
add("DOWNSTREAM (analysis/workbook) PCE core: leaves (count)", float(ib.n_components), float(ia.n_components), "Cross-index analysis/processed/index_coverage.csv")
for col, h, pub in (("sum_contrib_12m_calc" if "sum_contrib_12m_calc" in ib else "sum_contrib_12m", "12m", "12m"), ("sum_contrib_3m_ann", "3m ann.", "3m_ann")):
    pr = float(rb[(rb.index_name == "PCE core") & (rb.horizon == pub)].publisher_aggregate_pct_change.iloc[0])
    add(f"DOWNSTREAM PCE core: sum of contributions, {h} (pp)", float(ib[col]), float(ia[col]), "index_coverage.csv")
    add(f"DOWNSTREAM PCE core: published less sum, {h} (pp)", pr - float(ib[col]), pr - float(ia[col]), "index_coverage.csv; published from reconciliation.csv")
br = lambda root: pd.read_csv(root / "Cross-index analysis/processed/breadth.csv").set_index("index")
bb, ba = br(B), br(A)
for idx in ("PCE core", "PCE headline", "CPI core"):
    for col, lab in (("share_weight_12m_above_3", "12m > 3%"), ("share_weight_3m_ann_above_3", "3m ann. > 3%"), ("share_weight_12m_above_2018_19_avg", "12m > 2018-19 avg")):
        add(f"Breadth {idx}: % of basket weight {lab}", float(bb.loc[idx, col]), float(ba.loc[idx, col]), "Cross-index analysis/processed/breadth.csv")
mb = lambda root: pd.read_csv(root / "Market-based PCE/processed/components.csv")
for root, tag in ((B, "b"), (A, "a")):
    pass
mbb, mba = mb(B), mb(A)
for nm in sorted(mbb.index_name.unique()):
    for h in ("contrib_12m_calc", "contrib_3m_ann_calc"):
        add(f"{nm}: sum of contributions {h.split('_')[1]} (pp)", mbb[mbb.index_name == nm][h].sum(), mba[mba.index_name == nm][h].sum(), "Market-based PCE/processed/components.csv")
t = pd.DataFrame(rows); t.to_csv(OUT / "before_after.csv", index=False, float_format="%.4f")
print(t.drop(columns="source").to_string(float_format=lambda x: f"{x:.3f}"))
# which processed files changed
print("\nChanged processed files:")
for d in ("PCE", "Market-based PCE", "Cross-index analysis", "Trimmed mean"):
    for f in sorted((B / d / "processed").glob("*")):
        g = A / d / "processed" / f.name
        if not g.exists() or not filecmp.cmp(f, g, shallow=False): print(" ", d, f.name)
# component-level weight changes, core
k = lambda c: c[c.index_name == "PCE core"].set_index("component_name")
kb, ka = k(cb), k(ca)
moved = pd.concat([kb[["weight_base_12m", "contrib_12m_calc", "contrib_3m_ann_calc"]].add_suffix("_b"), ka[["weight_base_12m", "contrib_12m_calc", "contrib_3m_ann_calc", "pct_12m_calc", "pct_3m_ann_calc"]].add_suffix("_a")], axis=1)
inout = moved[moved.weight_base_12m_b.isna() | moved.weight_base_12m_a.isna()]
inout.to_csv(OUT / "core_membership_changes.csv", float_format="%.5f")
print("\nCore membership changes:\n", inout.round(3).to_string())
