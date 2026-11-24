#!/usr/bin/env python
"""Rebuild the BEA market-based PCE component basket from BEA's composition tables.

Inputs (all local):
  Market-based PCE/raw/BEA_MktBasedComposition_2026-09-28.xls, BEA_nonMktBasedComposition_2026-09-28.xls (2009 vintage)
  PCE/raw/BEA_NIUnderlyingDetail_U20404 / U20405 _<newest date in filename>.json (auto-selected)
  PCE/processed/components.csv (Dallas Fed leaf set, index_name == 'PCE headline')
Outputs: Market-based PCE/processed/{components,category_components,pce_market_membership,reconciliation}.csv
(REPORT.md is written by hand from these outputs.)
Run with a python that has pandas + xlrd.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]  # .../Price indexes
RAW_MB = ROOT / "Market-based PCE" / "raw"
OUT = ROOT / "Market-based PCE" / "processed"
def newest(pattern):
    fs = sorted((ROOT / "PCE" / "raw").glob(pattern), key=lambda f: re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1))
    return fs[-1]


def pshift(p, n):
    y, m = int(p[:4]), int(p[5:])
    k = y * 12 + m - 1 + n
    return "%04dM%02d" % (k // 12, k % 12 + 1)


F404 = newest("BEA_NIUnderlyingDetail_U20404_*.json")
F405 = newest("BEA_NIUnderlyingDetail_U20405_*.json")
F2804 = newest("BEA_NIPA_T20804_*.json")
RAWSTR = "Price indexes/PCE/raw/%s; Price indexes/PCE/raw/%s" % (F404.name, F405.name)


# ---------------------------------------------------------------- inputs
def read_comp(fname):
    d = pd.read_excel(RAW_MB / fname, header=None, dtype=str).iloc[3:]
    d = d[d[0].notna() & d[1].notna()]
    return {a.strip(): b.strip() for a, b in zip(d[0], d[1])}


MKT = read_comp("BEA_MktBasedComposition_2026-09-28.xls")
NON = read_comp("BEA_nonMktBasedComposition_2026-09-28.xls")


def load(p):
    df = pd.DataFrame(json.load(open(p))["BEAAPI"]["Results"]["Data"])
    df["line"] = df.LineNumber.astype(int)
    df["v"] = df.DataValue.str.replace(",", "").astype(float)
    pv = df.pivot_table(index="line", columns="TimePeriod", values="v")
    meta = df.drop_duplicates("line").set_index("line")[["LineDescription", "SeriesCode"]]
    return pv, meta


P, META4 = load(F404)   # price indexes
S, META5 = load(F405)   # nominal $ millions SAAR
_pc = {tuple(map(int, (c[:4], c[5:]))) for c in P.columns} & {tuple(map(int, (c[:4], c[5:]))) for c in S.columns}
LATEST = "%04dM%02d" % max(_pc)
B12, B3, B1 = pshift(LATEST, -12), pshift(LATEST, -3), pshift(LATEST, -1)
MONTHS = [B12, B3, B1, LATEST]
NAME = META4.LineDescription.to_dict()
SCODE = META4.SeriesCode.to_dict()


def code3(line):
    sc = SCODE.get(line, "")
    return sc[1:4] if re.fullmatch(r"D[A-Z]{3}R[CG]", sc) else None


# ------------------------------------------------------------ leaf set
comp = pd.read_csv(ROOT / "PCE" / "processed" / "components.csv")
head = comp[comp.index_name == "PCE headline"].copy()
head["line"] = head.component_id.str.extract(r"U20404 line (\d+)")[0]
unmapped = head[head.line.isna()]
leaves = head[head.line.notna()].copy()
leaves["line"] = leaves.line.astype(int)
LEAF_LINES = sorted(leaves.line)
assert len(LEAF_LINES) == 177  # 176 until 2026-11-14; line 218 (AV/photo/info-processing equipment services) now mapped

# Ancestry evidence used for leaves whose own 3-letter code is not in either table.
# Each is verified below with nominal additivity (parent == sum of children, all months).
ANCESTOR = {
    21: (20, "MVP", "child of line 20 'Motor vehicle parts and accessories' (line order; 20 = 21+22 nominal)"),
    22: (20, "MVP", "child of line 20 'Motor vehicle parts and accessories' (line order; 20 = 21+22 nominal)"),
}
# Partial leaves: (market sub-lines published by BEA, non-market sub-lines, relation checked)
PARTIAL = {
    13: dict(market=[14], nonmkt=[15, 16], check=(13, [14, 15, 16]),
             desc="Used autos = net transactions (NET, market; line 14) + used auto margin (MAR, non-mkt; line 15) + employee reimbursement (REE, non-mkt; line 16)"),
    17: dict(market=[18], nonmkt=[19], check=(17, [18, 19]),
             desc="Used light trucks = net transactions (UTN, market; line 18) + used truck margin (UTM, non-mkt; line 19)"),
    258: dict(market=[259, 261, 264], nonmkt=[267, 268, 269], check=None,
              desc="Fin. service charges, fees & commissions = fees (FEE, mkt; 259) + securities commissions (260 = direct DCT mkt 261 + indirect ICT mkt 264 + mutual fund sales charges MUT non-mkt 267) + portfolio mgmt (PMI, non-mkt; 268) + trust/fiduciary (TRU, non-mkt; 269)"),
}
ADD_CHECKS = [(258, [259, 260, 268, 269]), (260, [261, 264, 267]), (275, [276, 277, 278]),
              (20, [21, 22]), (13, [14, 15, 16]), (17, [18, 19])]


def additivity(parent, kids):
    d = [abs(S.loc[parent, m] - S.loc[kids, m].sum()) for m in S.columns]
    return max(d)


ADD_RES = {(p, tuple(k)): additivity(p, k) for p, k in ADD_CHECKS}
assert all(v <= 3 for v in ADD_RES.values()), ADD_RES  # rounding only ($ millions)

member_rows = []
LEAF_STATUS = {}
for l in LEAF_LINES:
    c = code3(l)
    nm = NAME[l]
    r = dict(leaf_line=l, leaf_name=nm, series_code=SCODE[l], code3=c or "", classification="", matched_code="",
             matched_description="", method="", in_basket="", note="")
    if l in PARTIAL:
        p = PARTIAL[l]
        r.update(classification="market_partial", matched_code=c or "",
                 matched_description=(MKT.get(c) or NON.get(c) or "(code absent from both tables)"),
                 method="descendants: sub-lines carry listed codes; classification differs across sub-lines",
                 in_basket="N (replaced by market sub-lines %s)" % p["market"],
                 note=p["desc"] + "; non-market $ (%s) = %s mn of leaf %s mn; additivity max diff $%s mn" % (
                     LATEST, f"{S.loc[p['nonmkt'], LATEST].sum():,.0f}", f"{S.loc[l, LATEST]:,.0f}",
                     ADD_RES.get((l, tuple(p['check'][1]))) if p['check'] else max(ADD_RES[(258, (259, 260, 268, 269))], ADD_RES[(260, (261, 264, 267))])))
        LEAF_STATUS[l] = "partial"
    elif c in MKT and c not in NON:
        r.update(classification="market", matched_code=c, matched_description=MKT[c], method="own 3-letter code in market table",
                 in_basket="Y")
        LEAF_STATUS[l] = "market"
    elif c in NON and c not in MKT:
        r.update(classification="non-market", matched_code=c, matched_description=NON[c],
                 method="own 3-letter code in non-market table", in_basket="N")
        LEAF_STATUS[l] = "non"
    elif l in ANCESTOR:
        a, ac, why = ANCESTOR[l]
        r.update(classification="market", matched_code=ac, matched_description=MKT[ac],
                 method="nearest listed ancestor line %d (%s)" % (a, ac), in_basket="Y", note=why)
        LEAF_STATUS[l] = "market"
    elif l == 156:
        r.update(classification="market", matched_code="TSP+TLD (parent TEN)",
                 matched_description="%s + %s (parent: %s)" % (MKT["TSP"], MKT["TLD"], MKT["TEN"]),
                 method="renamed/merged line: 2009 codes TSP and TLD (both market) combined in current LA000629; parent TEN (line 154) market",
                 in_basket="Y", note="SeriesCode LA000629 has no 3-letter code; components.csv shows 'IA000629' (typo)")
        LEAF_STATUS[l] = "market"
    elif l == 275:
        kids = [276, 277, 278]
        cs = [code3(k) for k in kids]
        assert all(x in NON for x in cs)
        r.update(classification="non-market", matched_code="+".join(cs),
                 matched_description="; ".join(NON[x] for x in cs),
                 method="own code (HIN) absent; every child (lines 276-278, listed MIN/IIN/PWC) is non-market; 275 = sum of children (nominal check)",
                 in_basket="N", note="additivity max diff $%s mn" % ADD_RES[(275, (276, 277, 278))])
        LEAF_STATUS[l] = "non"
    else:
        r.update(classification="unclassified", method="no code match, no ancestor rule", in_basket="N")
        LEAF_STATUS[l] = "unclassified"
    if l == 328:
        r["note"] = ("Market per DMS listing, but BEA footnote 1: table excludes unpublished in-kind domestic service (DMI, non-market), "
                     "~7%% of domestic services; current line 328 likely includes it (approx %s mn in %s at 7%%; not verifiable, no split made)" %
                     (f"{0.07 * S.loc[328, LATEST]:,.0f}", LATEST))
    if l in (325, 326, 184, 188):
        r["note"] = "code also appears on a later NPISH sub-block line (359-365); leaf's own line used"
    member_rows.append(r)

# unmapped Dallas rows
for _, u in unmapped.iterrows():
    member_rows.append(dict(leaf_line="", leaf_name=u.component_name, series_code="", code3="", classification="unclassified",
                            matched_code="", matched_description="", method="Dallas row with no BEA line in components.csv",
                            in_basket="N", note=str(u.component_id)))
# substitute lines
for pl, p in PARTIAL.items():
    for m in p["market"]:
        member_rows.append(dict(leaf_line=m, leaf_name=NAME[m], series_code=SCODE[m], code3=code3(m), classification="market",
                                matched_code=code3(m), matched_description=MKT[code3(m)],
                                method="published BEA sub-line substituted for partial Dallas leaf %d" % pl, in_basket="Y",
                                note="not in Dallas leaf set; own U20404/U20405 line"))
MEMBERSHIP = pd.DataFrame(member_rows)

MARKET_LEAVES = []  # (line, parent_note)
for l in LEAF_LINES:
    if LEAF_STATUS[l] == "market":
        MARKET_LEAVES.append((l, "Dallas Fed 178-component basket"))
    elif LEAF_STATUS[l] == "partial":
        for m in PARTIAL[l]["market"]:
            MARKET_LEAVES.append((m, "Market-only BEA sub-line replacing partial Dallas leaf line %d (%s)" % (l, NAME[l])))
LINES_MKT = [l for l, _ in MARKET_LEAVES]
assert len(set(LINES_MKT)) == len(LINES_MKT)

# composition codes with no current line
NOLINE = []
allcodes = {}
for l in META4.index:
    c = code3(l)
    if c:
        allcodes.setdefault(c, []).append(l)
for tag, T in (("market", MKT), ("non-market", NON)):
    for c, dsc in T.items():
        if c not in allcodes:
            NOLINE.append((tag, c, dsc))


def is_core(l):
    # NOTE: brief said lines 73-119, but 104-112 is clothing and footwear (core). Food = 73-103, energy goods = 113-119
    # (verified: category core with these exclusions reproduces BEA line 402 exactly).
    return not (73 <= l <= 103 or 113 <= l <= 119 or 169 <= l <= 171)


# ------------------------------------------------------------ calc engine
def pct(l, a, b):
    return (P.loc[l, a] / P.loc[l, b] - 1) * 100


def build(lines, index_name, meta, weight_note):
    """meta: line -> dict(name, parent, incore, note)."""
    tot = {m: S.loc[lines, m].sum() for m in (LATEST, B12, B3, B1)}
    rows = []
    raw3 = {}
    for l in lines:
        raw3[l] = S.loc[l, B3] / tot[B3] * pct(l, LATEST, B3)
    Ssum = sum(raw3.values())
    k = ((1 + Ssum / 100) ** 4 - 1) / (Ssum / 100)
    for l in lines:
        w = {m: S.loc[l, m] / tot[m] for m in tot}
        p1, p12 = pct(l, LATEST, B1), pct(l, LATEST, B12)
        p3a = ((P.loc[l, LATEST] / P.loc[l, B3]) ** 4 - 1) * 100
        y12 = (P.loc[l].reindex(P.columns) / P.loc[l].shift(12) - 1) * 100
        avg = y12["2018M01":"2019M12"].mean()
        mt = meta[l]
        rows.append(dict(
            index_name=index_name, component_id="U20404 line %d / U20405 line %d (%s)" % (l, l, SCODE[l]) if mt.get("leaf", True)
            else "U20404/U20405 line %d" % l,
            component_name=NAME[l], level_or_parent=mt["parent"], in_core="Y" if mt["incore"] else "N",
            weight_latest=w[LATEST], weight_base_12m=w[B12], weight_base_3m=w[B3], weight_base_1m=w[B1],
            weight_units="fraction of market-based nominal PCE expenditure",
            pct_1m_calc=p1, pct_3m_ann_calc=p3a, pct_12m_calc=p12,
            contrib_1m_calc=w[B1] * p1, contrib_3m_ann_calc=raw3[l] * k, contrib_12m_calc=w[B12] * p12,
            avg_pct_12m_2018_19_calc=avg, excess_contrib_12m_calc=w[LATEST] * (p12 - avg),
            latest_period=LATEST, sa_basis="SA; BEA U20404 monthly Fisher price indexes",
            source_ids="BEA NIUnderlyingDetail U20404 line %d; U20405 line %d" % (l, l), raw_file=RAWSTR,
            note=(mt.get("note", "") + " | " if mt.get("note") else "") + weight_note))
    return pd.DataFrame(rows), tot, k, Ssum


def pub_rates(line):
    return dict(r12=pct(line, LATEST, B12), r3a=((P.loc[line, LATEST] / P.loc[line, B3]) ** 4 - 1) * 100,
                r1=pct(line, LATEST, B1))


# ----------------------------------------------------- leaf-level version
leaf_meta = {}
for l, par in MARKET_LEAVES:
    n = ""
    if l == 328:
        n = "partial: may include unpublished in-kind domestic service (non-market, ~7% per BEA footnote)"
    if l == 156:
        n = "market via TSP+TLD merge"
    leaf_meta[l] = dict(name=NAME[l], parent=par, incore=is_core(l), note=n)
_cov = S.loc[LINES_MKT, LATEST].sum() / S.loc[377, LATEST] * 100
weight_note_leaf = "weights = share of summed market-leaf nominal spending (covers about %.1f%% of BEA line 377 in %s; see reconciliation.csv)" % (_cov, LATEST)
leaf_head, tot_h, k_h, S_h = build(LINES_MKT, "Market-based headline", leaf_meta, weight_note_leaf)
core_lines = [l for l in LINES_MKT if is_core(l)]
leaf_core, tot_c, k_c, S_c = build(core_lines, "Market-based core", leaf_meta, weight_note_leaf)
COMPS = pd.concat([leaf_head, leaf_core], ignore_index=True)

# ---------------------------------------------------- category version
CAT_HEAD = [378, 379, 380, 381, 382, 383, 385, 386, 387, 388, 389, 390, 391, 393, 394, 395, 396, 397, 398]
CAT_OVERLAP = {384: "Market-based PCE services = 385-391 + 392", 392: "Market-based PCE other services = 393-398"}
CAT_CORE = [378, 379, 381, 383, 385, 166, 387, 388, 389, 390, 391, 393, 394, 395, 396, 397, 398]
cat_meta = {}
for l in CAT_HEAD + [166]:
    cat_meta[l] = dict(name=NAME[l], parent="BEA-published market-based subcategory (U20404 lines 378-398)", incore=(l not in (380, 382, 386)),
                       leaf=False, note="")
cat_meta[166] = dict(name=NAME[166], parent="Water supply and sanitation (market; line 166), substitutes for line 386 in core because 386 = 166 + electricity & gas (169)",
                     incore=True, leaf=False, note="core-only substitute; %s in composition tables (WRS, market)" % NAME[166])
cat_meta[386]["note"] = "contains electricity & gas (169-171), excluded from core; core uses line 166 instead"
cat_meta[380]["note"] = "food and beverages (market portion; excludes farm-produced food); excluded from core"
cat_meta[382]["note"] = "gasoline and other energy goods (market); excluded from core"
wn_cat = "weights = share of summed non-overlapping BEA market-based subcategory nominal spending; uses only BEA-published lines"
cat_head, ctot_h, ck_h, cS_h = build(CAT_HEAD, "Market-based headline", cat_meta, wn_cat)
cat_core, ctot_c, ck_c, cS_c = build(CAT_CORE, "Market-based core", cat_meta, wn_cat)
CATS = pd.concat([cat_head, cat_core], ignore_index=True)

# --------------------------------------------------- reconciliation
REC = []


def add(check_type, version, period, item, computed, bench, note=""):
    gap = computed - bench
    REC.append(dict(check_type=check_type, version=version, period=period, item=item, computed=computed, benchmark=bench,
                    gap=gap, gap_pct_of_benchmark=(gap / bench * 100) if bench else np.nan, note=note))


# subcategory mapping of leaf lines by U20405 line ranges (line order = BEA table hierarchy)
CATRANGE = {378: (4, 22), 379: (23, 71), 380: (73, 103), 381: (104, 112), 382: (113, 119), 383: (120, 149),
            385: (153, 164), 386: (165, 171), 387: (172, 189), 388: (190, 208), 389: (209, 233), 390: (234, 251),
            391: (252, 279), 393: (281, 289), 394: (290, 297), 395: (298, 306), 396: (307, 314), 397: (316, 316), 398: (327, 332)}


def cat_of(l):
    for c, (a, b) in CATRANGE.items():
        if a <= l <= b:
            return c
    return None


for m in MONTHS:
    ml = S.loc[LINES_MKT, m].sum()
    mc = S.loc[core_lines, m].sum()
    add("nominal_total", "leaf", m, "sum market leaves vs line 377 Market-based PCE", ml, S.loc[377, m], "$ millions SAAR")
    add("nominal_total", "leaf", m, "sum market core leaves vs line 402 MB core", mc, S.loc[402, m], "$ millions SAAR")
    # sensitivity: Dallas leaves as-is incl. whole mixed leaves 13,17,258
    alt = ml - S.loc[[14, 18, 259, 261, 264], m].sum() + S.loc[[13, 17, 258], m].sum()
    add("nominal_total", "leaf_variant_whole_partial_leaves", m, "Dallas leaves as-is (13,17,258 counted whole) vs line 377", alt,
        S.loc[377, m], "sensitivity only; not the delivered basket")
    if 218 not in LINES_MKT:
        add("nominal_total", "leaf", m, "gap explained by line 218 (AV/photo/streaming services; Dallas row N/A)",
            ml + S.loc[218, m], S.loc[377, m], "computed = leaf sum + line 218; residual = remaining gap")
    add("nominal_total", "leaf", m, "domestic services in-kind (approx 7% of line 328; non-market, included in leaf sum)",
        0.07 * S.loc[328, m], np.nan if False else 0.0, "BEA footnote 1 approximation; benchmark 0 = correct treatment")
    lm398 = [l for l in LINES_MKT if cat_of(l) == 398]
    add("nominal_total", "leaf", m, "implied in-kind domestic service in line 328 (leaf sum line 398 minus BEA line 398) as % of line 328",
        (S.loc[lm398, m].sum() - S.loc[398, m]) / S.loc[328, m] * 100, 7.0,
        "benchmark = BEA 2009 footnote '~7%'; computed is inference from the residual, not published")
    for c in sorted(CATRANGE):
        lm = [l for l in LINES_MKT if cat_of(l) == c]
        add("nominal_category", "leaf", m, "leaves mapped to line %d %s" % (c, NAME[c]), S.loc[lm, m].sum(), S.loc[c, m],
            "%d leaves; mapping by U20405 line ranges" % len(lm))
    for c, why in CAT_OVERLAP.items():
        kids = [x for x in CATRANGE if (385 <= x <= 391 if c == 384 else 393 <= x <= 398)]
        lm = [l for l in LINES_MKT if cat_of(l) in kids]
        add("nominal_category", "leaf", m, "leaves mapped to line %d %s" % (c, NAME[c]) + (" (+lines 393-398)" if False else ""),
            S.loc[lm, m].sum() + (S.loc[[l for l in LINES_MKT if cat_of(l) in range(393, 399) and c == 384], m].sum() if c == 384 else 0),
            S.loc[c, m], why)
    add("nominal_total", "category", m, "sum of non-overlapping lines 378-383,385-391,393-398 vs line 377",
        S.loc[CAT_HEAD, m].sum(), S.loc[377, m], "$ millions SAAR")
    add("nominal_total", "category", m, "sum of core category set (386 replaced by line 166) vs line 402",
        S.loc[CAT_CORE, m].sum(), S.loc[402, m], "$ millions SAAR")

pubh, pubc = pub_rates(377), pub_rates(402)


def sums(df, idx):
    d = df[df.index_name == idx]
    return dict(r12=d.contrib_12m_calc.sum(), r3a=d.contrib_3m_ann_calc.sum(), r1=d.contrib_1m_calc.sum())


for ver, dfh, dfc in (("leaf", leaf_head, leaf_core), ("category", cat_head, cat_core)):
    for nm, df, pub, l in (("headline vs line 377", dfh, pubh, 377), ("core vs line 402", dfc, pubc, 402)):
        s = dict(r12=df.contrib_12m_calc.sum(), r3a=df.contrib_3m_ann_calc.sum(), r1=df.contrib_1m_calc.sum())
        for key, lab in (("r12", "12m pct (%s->%s)" % (B12, LATEST)), ("r3a", "3m annualized pct (%s->%s)" % (B3, LATEST)),
                         ("r1", "1m pct (%s->%s)" % (B1, LATEST))):
            add("rate", ver, LATEST, "sum contributions, %s: %s" % (nm, lab), s[key], pub[key],
                "benchmark = U20404 line %d index ratio" % l)
        # identity sanity: weighted-average with latest weights
        add("rate", ver, LATEST, "sum weight_latest*pct_12m (Paasche-style), %s" % nm,
            (df.weight_latest * df.pct_12m_calc).sum(), pub["r12"], "diagnostic: latest-month weights")
        add("rate", ver, LATEST, "sum excess_contrib_12m_calc, %s" % nm, df.excess_contrib_12m_calc.sum(), np.nan,
            "no BEA benchmark; = sum wL*(pct12 - avg 2018-19)")
# check Dallas values match project components.csv
dal = head[head.line.notna()].copy()
dal["line"] = dal.line.astype(int)
dal = dal.set_index("line")
diffs = {}
for col, f in (("pct_1m_calc", lambda l: pct(l, LATEST, B1)), ("pct_3m_ann_calc", lambda l: ((P.loc[l, LATEST] / P.loc[l, B3]) ** 4 - 1) * 100),
               ("pct_12m_calc", lambda l: pct(l, LATEST, B12))):
    diffs[col] = max(abs(dal.loc[l, col] - f(l)) for l in dal.index)
    add("input_check", "leaf", LATEST, "max abs diff recomputed vs PCE/processed/components.csv %s (%d Dallas leaves)" % (col, len(LEAF_LINES)), diffs[col], 0.0)
RECDF = pd.DataFrame(REC)

# ---------------------------------------------------- write
COLS = ["index_name", "component_id", "component_name", "level_or_parent", "in_core", "weight_latest", "weight_base_12m",
        "weight_base_3m", "weight_base_1m", "weight_units", "pct_1m_calc", "pct_3m_ann_calc", "pct_12m_calc", "contrib_1m_calc",
        "contrib_3m_ann_calc", "contrib_12m_calc", "avg_pct_12m_2018_19_calc", "excess_contrib_12m_calc", "latest_period",
        "sa_basis", "source_ids", "raw_file", "note"]
COMPS[COLS].to_csv(OUT / "components.csv", index=False, float_format="%.8f")
CATS[COLS].to_csv(OUT / "category_components.csv", index=False, float_format="%.8f")
MEMBERSHIP.to_csv(OUT / "pce_market_membership.csv", index=False)
RECDF.to_csv(OUT / "reconciliation.csv", index=False, float_format="%.6f")

# ---------------------------------------------------- console summary
print("codes: market table", len(MKT), "non-market", len(NON))
print("leaf status counts:", pd.Series(LEAF_STATUS).value_counts().to_dict())
print("market leaves in basket:", len(LINES_MKT), "core:", len(core_lines))
print("codes with no current line:", NOLINE)
print("additivity:", ADD_RES)
print("published:", pubh, pubc)
print(RECDF[RECDF.check_type.isin(["rate", "nominal_total", "input_check"])].to_string(max_colwidth=70))
print("k factors", k_h, k_c, ck_h, ck_c)
print("weight sum", leaf_head.weight_latest.sum(), leaf_core.weight_latest.sum())


# ---------------------------------------------------- report appendix (written at run time)
T = pd.DataFrame(json.load(open(F2804))["BEAAPI"]["Results"]["Data"])
T["line"] = T.LineNumber.astype(int)
T["v"] = T.DataValue.str.replace(",", "").astype(float)
TP = T.pivot_table(index="line", columns="TimePeriod", values="v")
tpub = {ln: dict(r12=(TP.loc[ln, LATEST] / TP.loc[ln, B12] - 1) * 100, r3a=((TP.loc[ln, LATEST] / TP.loc[ln, B3]) ** 4 - 1) * 100,
                 r1=(TP.loc[ln, LATEST] / TP.loc[ln, B1] - 1) * 100) for ln in (1, 25, 30, 31)}
rl = RECDF[RECDF.check_type == "rate"]
L = ["", "<!-- rebuild_market_based.py section -->", "## Rebuilt market-based basket (BEA 2009 composition tables), run-time results",
     "Latest %s; bases 12m %s, 3m %s, 1m %s. Inputs: %s; %s." % (LATEST, B12, B3, B1, F404.name, F405.name),
     "T20804 published (%s): " % F2804.name + "; ".join("line %d: 12m %.3f, 3m ann %.3f, 1m %.3f" % (k, v["r12"], v["r3a"], v["r1"]) for k, v in tpub.items()),
     "U20404 lines 377/402 vs T20804 lines 30/31 (12m): %.3f/%.3f vs %.3f/%.3f." % (pubh["r12"], pubc["r12"], tpub[30]["r12"], tpub[31]["r12"]),
     "Core rule: exclude U20404 lines 73-103, 113-119, 169-171 (clothing 104-112 stays core); category core substitutes line 166 for 386.",
     "Rate reconciliation (sum of contributions vs BEA U20404 line 377/402 index ratio):"]
for _, r in rl[~rl.item.str.contains("Paasche|excess")].iterrows():
    L.append("- %s | %s: computed %.3f vs BEA %.3f, gap %.3f pp" % (r.version, r["item"], r.computed, r.benchmark, r.gap))
L.append("Nominal reconciliation (%s):" % LATEST)
for _, r in RECDF[(RECDF.period == LATEST) & RECDF.check_type.isin(["nominal_total", "nominal_category"])].iterrows():
    if r.version in ("leaf", "category") and r.check_type == "nominal_total":
        L.append("- %s | %s: computed %.0f vs BEA %.0f, gap %.0f (%.2f%%)" % (r.version, r["item"], r.computed, r.benchmark, r.gap, r.gap_pct_of_benchmark))
cg = RECDF[(RECDF.period == LATEST) & (RECDF.check_type == "nominal_category")]
L.append("Category-level nominal gaps, max abs: $%.0f mn (%s)" % (cg.gap.abs().max(), cg.loc[cg.gap.abs().idxmax(), "item"]))
L.append("Composition codes with no current line: %s" % (NOLINE or "none"))
rp = OUT / "REPORT.md"
old = rp.read_text(encoding="utf-8") if rp.exists() else ""
old = old.split("\n<!-- rebuild_market_based.py section -->")[0].rstrip("\n")
rp.write_text(old + "\n" + "\n".join(L) + "\n", encoding="utf-8")
