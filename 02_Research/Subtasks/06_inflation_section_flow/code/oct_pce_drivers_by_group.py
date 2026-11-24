"""Group the October 2026 PCE estimate's component contributions by BEA category.

Input:  02_Research/Subtasks/04_oct_pce_build/outputs/W_pce_oct_tab_lines.csv (the lines behind
        the 'PCE Oct 2026 estimate' workbook tab) and A_hierarchy.csv (BEA Table 2.4.4U tree).
Output: ../outputs/oct_pce_drivers_by_group.csv, printed table.
Contributions are the build's own (fixed-share, rescaled over covered lines), so groups sum to the
build's component sums (1m exact; 3m/12m carry the convexity/aggregation gap noted on the tab).
Excess vs 2018-19 = weight12 x (pct_12m - own 2018-19 avg y/y), a rough "above-normal" split.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "02_Research/Subtasks/04_oct_pce_build/outputs"
OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)

lines = pd.read_csv(SRC / "W_pce_oct_tab_lines.csv")
hier = pd.read_csv(SRC / "A_hierarchy.csv").set_index("line")

# Groups: an ancestor line -> label. Housing split from utilities; energy services pulled out.
GROUP_ANCESTORS = {
    113: "Energy goods (gasoline, fuel oil)",
    73: "Food at home",
    4: "Core goods: motor vehicles & parts",
    23: "Core goods: furnishings & household equip.",
    38: "Core goods: recreational goods (incl. software, computers)",
    62: "Core goods: other durables",
    104: "Core goods: clothing & footwear",
    120: "Core goods: other nondurables (incl. Rx drugs)",
    172: "Services: health care",
    190: "Services: transportation (incl. airfares, insurance)",
    209: "Services: recreation",
    234: "Services: food services & accommodations",
    252: "Services: financial services & insurance",
    280: "Services: other",
    342: "Services: nonprofits (NPISH)",
}


def ancestors(line):
    out = []
    while line in hier.index and not pd.isna(hier.loc[line, "parent"]):
        out.append(line)
        line = int(hier.loc[line, "parent"])
    return out


def group(row):
    anc = ancestors(int(row.line))
    name = str(row["name"]).lower()
    if 152 in anc:  # housing and utilities
        if int(row.line) in (170, 171):
            return "Energy services (electricity, natural gas)"
        if int(row.line) in (167, 168):
            return "Services: water, sewer, trash"
        return "Housing (rent, OER)"
    for a in anc:
        if a in GROUP_ANCESTORS:
            return GROUP_ANCESTORS[a]
    return "Unclassified"


lines["group"] = lines.apply(group, axis=1)
lines["xs12_h"] = lines.w12_h / 100 * (lines.pct_12m - lines.avg_12m_2018_19)
lines["xs12_c"] = lines.w12_c / 100 * (lines.pct_12m - lines.avg_12m_2018_19)

agg = lines.groupby("group").agg(
    w_h=("w_h", "sum"), w_c=("w_c", "sum"),
    c1_h=("c1_h", "sum"), c3_h=("c3_h", "sum"), c12_h=("c12_h", "sum"), xs12_h=("xs12_h", "sum"),
    c1_c=("c1_c", "sum"), c3_c=("c3_c", "sum"), c12_c=("c12_c", "sum"), xs12_c=("xs12_c", "sum"),
    n=("line", "count"),
).sort_values("c12_h", ascending=False)
agg.loc["TOTAL"] = agg.sum()
agg.round(3).to_csv(OUT / "oct_pce_drivers_by_group.csv")

# Flagged themes (the tab's own flags)
flags = lines.groupby(lines.flag.fillna("(none)"))[["w_h", "c1_h", "c3_h", "c12_h", "c1_c", "c3_c", "c12_c"]].sum()
flags.round(3).to_csv(OUT / "oct_pce_drivers_by_flag.csv")

pd.set_option("display.width", 220)
print(agg.round(3))
print()
print(flags.round(3))
print()
print(lines[lines.group == "Unclassified"][["line", "name"]])
print(lines[lines.flag.notna()][["line", "name", "flag", "w_h", "pct_3m_ann", "pct_12m", "c12_h"]].round(3))
