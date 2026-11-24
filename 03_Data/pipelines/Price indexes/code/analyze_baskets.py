"""Manager analysis for the price-basket stage.

Reads the subagent outputs in "Price indexes/<index>/processed/", tags AI / Energy / Asset-price
items, ranks movers, builds the hypothesis baskets, and writes CSVs to Cross-index analysis/processed/.
All changes/contributions come from the subagent component files (flagged _calc there); basket
aggregates here are weight-averages of those component rates (calculated, flagged in outputs).
"""
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Cross-index analysis" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

TAGS = [
    ("Energy", r"\bfuels?\b|lubricants|gasoline|motor fuel|fuel oil|electricity|natural gas|utility gas|propane|energy|diesel|jet fuel|electric power|household fuels"),
    ("Energy spillover", r"air transport|airline|freight|delivery|postage|postal|moving|truck transportation|intercity|railway|water transportation|"
                         r"road transportation|public transportation|courier|motor vehicle rental|car and truck rental|transportation of|warehousing"),
    ("AI", r"software|computer|electronic components|semiconductor|data processing|hosting|information processing|telephone hardware|"
           r"telephone and related communication|video equipment|smart home"),
    ("Asset-price", r"portfolio|financial service charges|securities|commissions|investment advice|trust, fiduciary"),
]


def tag(name):
    n = str(name).lower()
    # remove exclusion phrases so "less foods and energy" / "less trade, transportation, and warehousing" are not tagged
    n = re.sub(r"\b(less|excluding|except)\b.*$", "", n)  # ignore everything a name excludes (e.g. "excluding foods, energy, and capital equipment")
    return ", ".join(t for t, pat in TAGS if re.search(pat, n)) or ""


def clean(name):
    return re.sub(r"^PPI (Commodity|industry) data for (Final demand-|Intermediate demand by commodity type-)?", "", str(name)).replace(
        ", seasonally adjusted", "").replace(", not seasonally adjusted", "")


def load(folder):
    c = pd.read_csv(ROOT / folder / "processed" / "components.csv")
    c["component_name"] = c["component_name"].map(clean)
    c["tag"] = c["component_name"].map(tag)
    return c


cpi, ppi, pce, mb = load("CPI"), load("PPI"), load("PCE"), load("Market-based PCE")


def rebuild_core(df, head, core):
    """Manager fix (2026-09-27): the subagent's PCE core membership mixed food items into core.
    BEA's PCE ex food & energy excludes U20404 lines 73-103 (food & beverages off-premises; lines 104-112 are clothing and stay in core),
    113-119 (gasoline & other energy goods) and 169-171 (electricity & gas). Rebuild core rows
    from the headline rows with nominal-share weights rescaled to that membership."""
    h = df[df.index_name == head].copy()
    ln = h.component_id.str.extract(r"line (\d+)")[0].astype(float)
    excl = ln.between(73, 103) | ln.between(113, 119) | ln.between(169, 171)  # food 73-103 (NOT clothing 104-112), energy goods 113-119, electricity & gas 169-171
    c = h[~excl & ln.notna()].copy()
    for col in ["weight_latest", "weight_base_12m", "weight_base_3m", "weight_base_1m"]:
        c[col] = c[col] / c[col].sum()
    c["contrib_12m_calc"] = c.weight_base_12m * c.pct_12m_calc
    c["contrib_3m_ann_calc"] = c.weight_base_3m * c.pct_3m_ann_calc
    c["contrib_1m_calc"] = c.weight_base_1m * c.pct_1m_calc
    c["excess_contrib_12m_calc"] = c.weight_latest * (c.pct_12m_calc - c.avg_pct_12m_2018_19_calc)
    c["index_name"], c["in_core"] = core, "Y"
    return pd.concat([df[df.index_name != core], c], ignore_index=True)


def fix_3m(df):
    """3m contributions: weight x raw (non-annualized) 3-month change, then scaled so they sum to the
    annualized total of those raw contributions: k = ((1+S/100)^4-1)/(S/100), S = sum of raw contributions.
    Avoids the overstatement from summing individually annualized rates of volatile items."""
    out = []
    for name, g in df.groupby("index_name", sort=False):
        g = g.copy()
        raw = ((1 + g.pct_3m_ann_calc / 100) ** 0.25 - 1) * 100
        c = g.weight_base_3m / g.weight_base_3m[raw.notna()].sum() * raw * (g.weight_base_3m[raw.notna()].sum() if str(g.weight_units.dropna().iloc[0]).lower().startswith("fraction") else g.weight_base_3m[raw.notna()].sum() / 100)
        S = c.sum()
        k = ((1 + S / 100) ** 4 - 1) / (S / 100) if S else 1
        g["contrib_3m_ann_calc"] = c * k
        out.append(g)
    return pd.concat(out, ignore_index=True)


pce = rebuild_core(pce, "PCE headline", "PCE core")
mb = rebuild_core(mb, "Market-based headline", "Market-based core")
def supercore(df, head, name):
    """PCE services excluding energy and housing (BEA 'supercore'): headline leaves in services
    (U20404 line >= 150) excluding housing (153-164) and electricity & gas (169-171)."""
    h = df[df.index_name == head].copy()
    ln = h.component_id.str.extract(r"line (\d+)")[0].astype(float)
    c = h[(ln >= 150) & ~ln.between(153, 164) & ~ln.between(169, 171)].copy()
    for col in ["weight_latest", "weight_base_12m", "weight_base_3m", "weight_base_1m"]:
        c[col] = c[col] / c[col].sum()
    c["contrib_12m_calc"] = c.weight_base_12m * c.pct_12m_calc
    c["contrib_1m_calc"] = c.weight_base_1m * c.pct_1m_calc
    c["excess_contrib_12m_calc"] = c.weight_latest * (c.pct_12m_calc - c.avg_pct_12m_2018_19_calc)
    c["index_name"] = name
    return pd.concat([df, c], ignore_index=True)


pce = supercore(pce, "PCE headline", "PCE services ex energy & housing")
cpi, ppi, pce, mb = fix_3m(cpi), fix_3m(ppi), fix_3m(pce), fix_3m(mb)
for nm, d in (("PCE core", pce), ("Market-based core", mb)):
    x = d[d.index_name == nm]
    print(f"{nm}: {len(x)} components; sum 12m contrib {x.contrib_12m_calc.sum():.3f}; 3m {x.contrib_3m_ann_calc.sum():.3f}")


def weight_pct(df):
    u = str(df["weight_units"].dropna().iloc[0]).lower()
    return df["weight_latest"] * (100 if "fraction" in u else 1)


def direction(r):
    a, b = r["pct_3m_ann_calc"], r["pct_12m_calc"]
    if pd.isna(a) or pd.isna(b):
        return "n/a"
    return "Accelerating" if a > b + 1 else "Easing" if a < b - 1 else "Steady"


INDEXES = [("CPI headline", cpi, "CPI-U headline"), ("CPI core", cpi, "CPI-U core"),
           ("PCE headline", pce, "PCE headline"), ("PCE core", pce, "PCE core"),
           ("PCE supercore (services ex energy & housing)", pce, "PCE services ex energy & housing"),
           ("Market-based PCE headline", mb, None), ("Market-based PCE core", mb, None),
           ("PPI final demand", ppi, "PPI Final Demand"), ("PPI intermediate: processed goods", ppi, "PPI Intermediate Demand ID61"),
           ("PPI intermediate: unprocessed goods", ppi, "PPI Intermediate Demand ID62"), ("PPI intermediate: services", ppi, "PPI Intermediate Demand ID63")]
movers, flagged, summary = [], [], []
for label, df, name in INDEXES:
    if name is None:
        names = sorted(df.index_name.unique())
        name = [n for n in names if ("core" in n.lower()) == ("core" in label.lower())][0]
    d = df[df.index_name == name].dropna(subset=["contrib_12m_calc"]).copy()
    d["weight_pct"] = weight_pct(d)
    d["weight_base_pct"] = d["weight_base_12m"] * (d["weight_pct"] / d["weight_latest"]).fillna(1)
    d["direction"] = d.apply(direction, axis=1)
    keep = ["component_name", "tag", "weight_pct", "weight_base_pct", "pct_12m_calc", "contrib_12m_calc", "pct_3m_ann_calc", "contrib_3m_ann_calc",
            "direction", "excess_contrib_12m_calc", "component_id", "raw_file"]
    # Sign rule (audit fix 2026-09-28): upward = positive contributors only, downward = negative only;
    # show fewer than five when a basket has fewer movers of that sign.
    up = d[d.contrib_12m_calc > 0].nlargest(5, "contrib_12m_calc")[keep]
    up = up.assign(side="Top 5 upward", rank=range(1, len(up) + 1))
    dn = d[d.contrib_12m_calc < 0].nsmallest(5, "contrib_12m_calc")[keep]
    dn = dn.assign(side="Top 5 downward", rank=range(1, len(dn) + 1))
    movers.append(pd.concat([up, dn]).assign(index=label))
    shown = set(up.component_name) | set(dn.component_name)
    f = d[(d.tag != "") & ~d.component_name.isin(shown)]
    f = f.reindex(f.contrib_12m_calc.abs().sort_values(ascending=False).index).head(8)
    flagged.append(f[keep].assign(index=label))
    summary.append(dict(index=label, source_name=name, n_components=len(d), weight_covered_pct=d.weight_pct.sum(),
                        sum_contrib_12m=d.contrib_12m_calc.sum(), sum_contrib_3m_ann=d.contrib_3m_ann_calc.sum()))
movers = pd.concat(movers)
flagged = pd.concat(flagged)
movers.to_csv(OUT / "movers_top5.csv", index=False)
flagged.to_csv(OUT / "flagged_items.csv", index=False)
pd.DataFrame(summary).to_csv(OUT / "index_coverage.csv", index=False)


# ---------------------------------------------------------------- baskets
def basket(df, name, pattern, core_only=True, exclude=None):
    d = df[df.index_name == name].dropna(subset=["pct_12m_calc"]).copy()
    d["w"] = d["weight_base_12m"]
    m = d.component_name.str.lower().str.contains(pattern, regex=True)
    if exclude:
        m &= ~d.component_name.str.lower().str.contains(exclude, regex=True)
    b, rest = d[m], d[~m]
    agg = lambda x, col: (x["w"] * x[col]).sum() / x["w"].sum() if x["w"].sum() else float("nan")
    return dict(items="; ".join(b.component_name), weight_share_pct=b.w.sum() / d.w.sum() * 100,
                pct_12m=agg(b, "pct_12m_calc"), pct_3m_ann=agg(b.dropna(subset=["pct_3m_ann_calc"]), "pct_3m_ann_calc"),
                contrib_12m=b.contrib_12m_calc.sum(), contrib_3m_ann=b.contrib_3m_ann_calc.sum(),
                control_pct_12m=agg(rest, "pct_12m_calc"), control_pct_3m_ann=agg(rest.dropna(subset=["pct_3m_ann_calc"]), "pct_3m_ann_calc"))


SPILL = r"air transport|airline|delivery|postage|postal|moving|intercity|railway|water transportation|road transportation|public transportation|motor vehicle rental|car and truck rental"
AI_CONS = r"software|computer|telephone hardware|telephone and related communication|information processing|video equipment|smart home"
ASSET = r"portfolio|financial service charges|securities|commissions|investment advice|trust, fiduciary"
rows = []
for idx, df, name in [("CPI core", cpi, "CPI-U core"), ("PCE core", pce, "PCE core")]:
    for bname, pat in [("Energy spillover (transport & delivery services)", SPILL), ("AI-exposed consumer items", AI_CONS),
                       ("Asset-price-linked financial services", ASSET)]:
        rows.append(dict(index=idx, basket=bname, **basket(df, name, pat)))
baskets = pd.DataFrame(rows)
baskets.to_csv(OUT / "hypothesis_baskets.csv", index=False)

# ------------------------------------------------ PCE drill-down (financial services, software)
def newest(pattern):
    """Newest raw file by the YYYY-MM-DD retrieval date in its name."""
    fs = sorted((ROOT / "PCE" / "raw").glob(pattern), key=lambda f: re.findall(r"\d{4}-\d{2}-\d{2}", f.name)[-1])
    return fs[-1]


u4 = json.load(open(newest("BEA_NIUnderlyingDetail_U20404_*.json")))["BEAAPI"]["Results"]["Data"]
u5 = json.load(open(newest("BEA_NIUnderlyingDetail_U20405_*.json")))["BEAAPI"]["Results"]["Data"]
num = lambda s: float(s.replace(",", ""))
px = {(int(r["LineNumber"]), r["TimePeriod"]): num(r["DataValue"]) for r in u4}
nom = {(int(r["LineNumber"]), r["TimePeriod"]): num(r["DataValue"]) for r in u5}
desc = {int(r["LineNumber"]): (r["LineDescription"], r["SeriesCode"]) for r in u4}
LATEST = max({t for (_, t) in px}, key=lambda t: (int(t[:4]), int(t[5:])))
_ly, _lm = int(LATEST[:4]), int(LATEST[5:])
per = lambda k: f"{_ly + (_lm - k - 1) // 12}M{(_lm - k - 1) % 12 + 1:02d}"
B12, B3 = per(12), per(3)
tot = {t: nom[(1, t)] for t in (B12, B3)}
# BEA core denominator: U20405 line 374 "PCE excluding food and energy" (verified by description)
core_line = [k for k, (dname, _) in desc.items() if dname.strip() == "PCE excluding food and energy"][0]
core_tot = {t: nom[(core_line, t)] for t in (B12, B3)}
drill = []
for ln in [258, 268, 260, 264, 269, 254, 255, 50, 49, 71, 207, 115]:
    name, code = desc[ln]
    p12 = (px[(ln, LATEST)] / px[(ln, B12)] - 1) * 100
    p3 = ((px[(ln, LATEST)] / px[(ln, B3)]) ** 4 - 1) * 100
    w = nom[(ln, B12)] / tot[B12]
    wc = nom[(ln, B12)] / core_tot[B12]
    drill.append(dict(line=ln, series=code, component=name.strip(), tag=tag(name), weight_pce_pct=w * 100, weight_core_pct=wc * 100, pct_12m=p12, pct_3m_ann=p3,
                      contrib_pce_12m=w * p12, contrib_core_12m=wc * p12 if ln not in (115,) else float("nan"),
                      latest_period=LATEST, source=f"BEA U20404/U20405 line {ln} ({code})"))
drill = pd.DataFrame(drill)
drill.to_csv(OUT / "pce_drilldown.csv", index=False)

# ------------------------------------------------------------ breadth
br = []
for idx, df, name in [("CPI core", cpi, "CPI-U core"), ("PCE core", pce, "PCE core"), ("CPI headline", cpi, "CPI-U headline"), ("PCE headline", pce, "PCE headline")]:
    d = df[df.index_name == name].dropna(subset=["pct_12m_calc"])
    w = d.weight_base_12m
    br.append(dict(index=idx, share_weight_12m_above_3=(w[d.pct_12m_calc > 3].sum() / w.sum() * 100),
                   share_weight_3m_ann_above_3=(w[d.pct_3m_ann_calc > 3].sum() / w[d.pct_3m_ann_calc.notna()].sum() * 100),
                   share_weight_12m_above_2018_19_avg=(w[d.pct_12m_calc > d.avg_pct_12m_2018_19_calc].sum() / w[d.avg_pct_12m_2018_19_calc.notna()].sum() * 100)))
breadth = pd.DataFrame(br)
breadth.to_csv(OUT / "breadth.csv", index=False)

# ------------------------------------------------------------ CPI-PCE wedge (BEA Table 9.1U)
r = pd.read_csv(ROOT / "Cross-index analysis" / "processed" / "cpi_pce_reconciliation.csv")
r["v"] = pd.to_numeric(r.DataValue, errors="coerce")
# Continuous stretch after the Oct/Nov 2025 CPI gap: Dec 2025 through the latest month BEA publishes
months = sorted(t for t in r.TimePeriod.unique() if t >= "2025M12")
wedge = r[r.TimePeriod.isin(months)].groupby(["LineNumber", "LineDescription"]).v.sum().reset_index().rename(columns={"v": "sum_pp"})
wedge["period"] = f"{months[0]}-{months[-1]}"
wedge.to_csv(OUT / "cpi_pce_wedge_bea_9_1U.csv", index=False)

# ------------------------------------------------------------ PPI named series
named = pd.read_csv(ROOT / "PPI" / "processed" / "named_series.csv")
named["tag"] = named["requested_name"].map(tag)
named.to_csv(OUT / "ppi_named_series_tagged.csv", index=False)

pd.set_option("display.width", 250)
print(pd.DataFrame(summary).round(2).to_string())
print(baskets.drop(columns="items").round(2).to_string())
print(drill.round(2).to_string())
print(breadth.round(1).to_string())
print(wedge[wedge.LineNumber.isin([1, 2, 13, 14, 18, 20, 21, 23, 24, 27, 28, 32, 39])].round(2).to_string())

# ------------------------------------------- Dallas published trimming detail (audit fix 2026-10-01)
# Dallas publishes "Components included and excluded from this month's Trimmed Mean" (workbook linked from
# dallasfed.org/research/pce). Trim status is encoded by the publisher's cell colors (legend in column F).
# Read verbatim; nothing is reconstructed.
import openpyxl  # noqa: E402
_dfile = sorted((ROOT / "PCE" / "raw").glob("Dallas_trimmed_mean_components_*.xlsx"), key=lambda f: re.findall(r"\d{4}-\d{2}-\d{2}", f.name)[-1])[-1]
_ws = openpyxl.load_workbook(_dfile).active
_legend = {str(_ws.cell(r, 6).fill.fgColor.rgb): _ws.cell(r, 6).value for r in range(3, 7) if _ws.cell(r, 6).value}
_rows = []
for r in range(3, _ws.max_row + 1):
    nm = _ws.cell(r, 1).value
    if not nm:
        continue
    status = _legend.get(str(_ws.cell(r, 1).fill.fgColor.rgb)) or _legend.get(str(_ws.cell(r, 2).fill.fgColor.rgb)) or "not color-coded"
    _rows.append(dict(component=nm, published_1m_annualized_pct=_ws.cell(r, 2).value, published_weight_pct=_ws.cell(r, 3).value,
                      published_cumulative_weight_pct=_ws.cell(r, 4).value, publisher_status=status,
                      raw_file=str(_dfile.relative_to(ROOT.parent))))
pd.DataFrame(_rows).to_csv(ROOT / "Trimmed mean" / "processed" / "dallas_trimmed_components_published.csv", index=False)
print("Dallas published trim status:", pd.DataFrame(_rows).publisher_status.value_counts().to_dict())

# ------------------------------------------- Oct 2026 CPI views (added 2026-11-10, approved by Eli)
# Separate files only; nothing above is changed. BLS published no Oct 2025 CPI, so Oct 2026 has no official 12m.
#  (1) short horizon: 1m / 3m ann. from components_2026-10_short_horizon.csv; movers ranked by 3m ann. contribution
#      (same sign rule as above); 3m breadth uses 12m-base weights, which exist only on the interpolated base, so the
#      breadth weights come from the approx. file (labelled), with an exact 3m-base-weight variant alongside.
#  (2) approx. 12m: components_2026-10_approx_interp_oct2025_base.csv (Oct 2025 = sqrt(Sep 2025 x Nov 2025), NSA);
#      movers and breadth by exactly the rules used above for the official basket. Labelled "approx., interpolated Oct 2025 base".
APPROX_LBL = "approx., interpolated Oct 2025 base"


def _cpi_view(fname):
    p = ROOT / "CPI" / "processed" / fname
    if not p.exists():
        return None
    c = pd.read_csv(p)
    c["component_name"] = c["component_name"].map(clean)
    c["tag"] = c["component_name"].map(tag)
    return fix_3m(c)


def _ranked(d, col, label, keep):
    up = d[d[col] > 0].nlargest(5, col)[keep]
    up = up.assign(side="Top 5 upward", rank=range(1, len(up) + 1))
    dn = d[d[col] < 0].nsmallest(5, col)[keep]
    dn = dn.assign(side="Top 5 downward", rank=range(1, len(dn) + 1))
    return pd.concat([up, dn]).assign(index=label)


_sh = _cpi_view("components_2026-10_short_horizon.csv")
_ap = _cpi_view("components_2026-10_approx_interp_oct2025_base.csv")
if _sh is not None and _ap is not None:
    mv_s, br_s, mv_a = [], [], []
    for label, name in [("CPI headline", "CPI-U headline"), ("CPI core", "CPI-U core")]:
        # (1) short horizon
        d = _sh[_sh.index_name == name].dropna(subset=["contrib_3m_ann_calc"]).copy()
        d["weight_pct"] = d["weight_latest"]
        d["weight_base_3m_pct"] = d["weight_base_3m"]
        keep = ["component_name", "tag", "weight_pct", "weight_base_3m_pct", "pct_1m_calc", "contrib_1m_calc", "pct_3m_ann_calc",
                "contrib_3m_ann_calc", "component_id", "raw_file"]
        mv_s.append(_ranked(d, "contrib_3m_ann_calc", label, keep))
        # both files are written from the same node list in the same order; align by row (component_id is not unique: "N/A")
        a_rows, s = _ap[_ap.index_name == name].reset_index(drop=True), _sh[_sh.index_name == name].reset_index(drop=True)
        assert (a_rows.component_name.fillna("") == s.component_name.fillna("")).all() and (a_rows.component_id.fillna("") == s.component_id.fillna("")).all()
        keep_rows = s.pct_3m_ann_calc.notna()
        s, wa = s[keep_rows], a_rows.weight_base_12m[keep_rows]
        ok = wa.notna()
        w3 = s.weight_base_3m
        br_s.append(dict(index=label, period="2026-10",
                         share_weight_3m_ann_above_3=wa[ok & (s.pct_3m_ann_calc > 3)].sum() / wa[ok].sum() * 100,
                         weights_used="12m-base weights at Oct 2025 (" + APPROX_LBL + ")",
                         share_weight_3m_ann_above_3_w3mbase=w3[s.pct_3m_ann_calc > 3].sum() / w3[w3.notna()].sum() * 100,
                         n_components=int(ok.sum())))
        # (2) approx. 12m: same rules as the official movers / breadth above
        d = _ap[_ap.index_name == name].dropna(subset=["contrib_12m_calc"]).copy()
        d["weight_pct"] = weight_pct(d)
        d["weight_base_pct"] = d["weight_base_12m"] * (d["weight_pct"] / d["weight_latest"]).fillna(1)
        d["direction"] = d.apply(direction, axis=1)
        keep = ["component_name", "tag", "weight_pct", "weight_base_pct", "pct_12m_calc", "contrib_12m_calc", "pct_3m_ann_calc", "contrib_3m_ann_calc",
                "direction", "excess_contrib_12m_calc", "component_id", "raw_file"]
        mv_a.append(_ranked(d, "contrib_12m_calc", label, keep).assign(basis=APPROX_LBL))
    pd.concat(mv_s).to_csv(OUT / "cpi_movers_2026-10_short_horizon.csv", index=False)
    pd.DataFrame(br_s).to_csv(OUT / "cpi_breadth_2026-10_short_horizon.csv", index=False)
    pd.concat(mv_a).to_csv(OUT / "cpi_movers_2026-10_approx_interp_oct2025_base.csv", index=False)
    br_a = []
    for idx, name in [("CPI core", "CPI-U core"), ("CPI headline", "CPI-U headline")]:
        d = _ap[_ap.index_name == name].dropna(subset=["pct_12m_calc"])
        w = d.weight_base_12m
        br_a.append(dict(index=idx, period="2026-10", basis=APPROX_LBL,
                         share_weight_12m_above_3=(w[d.pct_12m_calc > 3].sum() / w.sum() * 100),
                         share_weight_3m_ann_above_3=(w[d.pct_3m_ann_calc > 3].sum() / w[d.pct_3m_ann_calc.notna()].sum() * 100),
                         share_weight_12m_above_2018_19_avg=(w[d.pct_12m_calc > d.avg_pct_12m_2018_19_calc].sum() / w[d.avg_pct_12m_2018_19_calc.notna()].sum() * 100)))
    pd.DataFrame(br_a).to_csv(OUT / "cpi_breadth_2026-10_approx_interp_oct2025_base.csv", index=False)
    print("Oct 2026 CPI views written (short horizon; " + APPROX_LBL + ")")
    print(pd.DataFrame(br_s).round(1).to_string()); print(pd.DataFrame(br_a).round(1).to_string())


# ------------------------------- Sep 2026 3m breadth on 3m-base weights (added 2026-11-10, approved by Eli)
# Same weighting as the Oct "share_weight_3m_ann_above_3_w3mbase" column (weights at the start of the 3-month window,
# rows with a 3m rate), so Sep and Oct compare like with like on published data only. The 12m-base column restates the
# official breadth.csv value as a check. Separate file; breadth.csv is unchanged.
br_w3 = []
for label, name in [("CPI headline", "CPI-U headline"), ("CPI core", "CPI-U core")]:
    d12 = cpi[cpi.index_name == name].dropna(subset=["pct_12m_calc"])
    w12 = d12.weight_base_12m
    s = cpi[(cpi.index_name == name) & cpi.pct_3m_ann_calc.notna()]
    w3 = s.weight_base_3m
    br_w3.append(dict(index=label, period=str(s.latest_period.dropna().iloc[0]) if s.latest_period.notna().any() else "",
                      share_weight_3m_ann_above_3_w12mbase_official=w12[d12.pct_3m_ann_calc > 3].sum() / w12[d12.pct_3m_ann_calc.notna()].sum() * 100,
                      share_weight_3m_ann_above_3_w3mbase=w3[s.pct_3m_ann_calc > 3].sum() / w3[w3.notna()].sum() * 100,
                      weights_note="w3mbase: published weights at the start of the 3-month window (exact); w12mbase_official: as in breadth.csv",
                      n_components=int(w3.notna().sum())))
pd.DataFrame(br_w3).to_csv(OUT / "cpi_breadth_2026-09_w3mbase.csv", index=False)
print("Sep 2026 CPI 3m breadth on 3m-base weights written"); print(pd.DataFrame(br_w3).round(2).to_string())
