"""Compare pre-refresh (archive/pre_refresh_2026-11-10) and refreshed Price indexes outputs.

Run from the project root:  python3 -I "02_Research/Subtasks/02_refresh_baskets/code/compare_vintages.py"
Prints, per basket: row counts, latest_period, components dropped/added (by index_name + component_id),
components that gained/lost a usable 12m contribution, and old-vs-new published-aggregate reconciliation gaps.
Also prints revisions to overlapping months of core PCE ex OER and the published core PCE index (line 374).
Read-only: writes nothing.
"""
from pathlib import Path
import pandas as pd

PI = Path("03_Data/pipelines/Price indexes")
OLD = PI / "archive" / "pre_refresh_2026-11-10"
FOLDERS = ["CPI", "PPI", "PCE", "Market-based PCE", "Trimmed mean", "Sticky CPI"]
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 80)

for f in FOLDERS:
    o = pd.read_csv(OLD / f / "processed" / "components.csv")
    n = pd.read_csv(PI / f / "processed" / "components.csv")
    print(f"\n=== {f}: rows old {len(o)} -> new {len(n)}; latest {sorted(o.latest_period.astype(str).unique())} -> {sorted(n.latest_period.astype(str).unique())}")
    key = ["index_name", "component_id"]
    ko = set(map(tuple, o[key].astype(str).values)); kn = set(map(tuple, n[key].astype(str).values))
    for lab, s in (("dropped", ko - kn), ("added", kn - ko)):
        if s:
            nm = (o if lab == "dropped" else n).set_index(key)
            for k in sorted(s):
                try:
                    name = nm.loc[k, "component_name"]
                    name = name.iloc[0] if hasattr(name, "iloc") else name
                except KeyError:
                    name = ""
                print(f"  {lab}: {k} {name}")
    if "contrib_12m_calc" in o and o.contrib_12m_calc.notna().any():
        m = o.merge(n, on=key, suffixes=("_o", "_n"))
        gain = m[m.contrib_12m_calc_o.isna() & m.contrib_12m_calc_n.notna()]
        lost = m[m.contrib_12m_calc_o.notna() & m.contrib_12m_calc_n.isna()]
        for lab, d in (("gained 12m contribution", gain), ("lost 12m contribution", lost)):
            for r in d.itertuples():
                print(f"  {lab}: {r.index_name} | {r.component_id} | {r.component_name_n}")
    if f in ("CPI", "PPI", "Trimmed mean"):
        ro = pd.read_csv(OLD / f / "processed" / "reconciliation.csv")
        rn = pd.read_csv(PI / f / "processed" / "reconciliation.csv")
        cols = [c for c in ro.columns if c in ("aggregate", "period", "horizon", "published_change", "publisher_rate_pct", "component_contributions_calc", "gap_pp_calc")]
        print("  reconciliation OLD:\n" + ro[cols].to_string(index=False))
        print("  reconciliation NEW:\n" + rn[cols].to_string(index=False))

# Market-based and PCE closure reconciliation
for f in ("Market-based PCE", "PCE"):
    for lab, root in (("OLD", OLD), ("NEW", PI)):
        p = root / f / "processed" / "reconciliation.csv"
        if p.exists():
            r = pd.read_csv(p)
            print(f"\n--- {f} reconciliation {lab} ({len(r)} rows)")
            print(r.iloc[:, :7].to_string(index=False, max_colwidth=70))

# Revisions: core PCE ex OER and core PCE, overlapping months
xo = pd.read_csv(OLD / "Cross-index analysis" / "processed" / "core_pce_ex_oer_2026-10-01.csv", index_col=0)
xn = pd.read_csv(PI / "Cross-index analysis" / "processed" / "core_pce_ex_oer_2026-11-10.csv", index_col=0)
j = xo.join(xn, lsuffix="_old", rsuffix="_new", how="inner")
j["rev_core_12m"] = j.core_12m_new - j.core_12m_old
j["rev_exoer_12m"] = j.core_ex_oer_12m_new - j.core_ex_oer_12m_old
print("\n--- Revisions to 12m rates (new vintage minus old), last 8 overlapping months")
print(j[["core_12m_old", "core_12m_new", "rev_core_12m", "core_ex_oer_12m_old", "core_ex_oer_12m_new", "rev_exoer_12m"]].dropna().tail(8).round(3).to_string())
print("max |revision| over all months: core", round(j.rev_core_12m.abs().max(), 3), "ex OER", round(j.rev_exoer_12m.abs().max(), 3))
