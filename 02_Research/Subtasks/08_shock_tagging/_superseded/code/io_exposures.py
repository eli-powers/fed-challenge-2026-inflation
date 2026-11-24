"""Energy cost share and import content per core PCE item, BEA 2017 detail I-O.

Run: python3 -I io_exposures.py   (from anywhere; paths are absolute-from-root)
Inputs (03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/):
  PCEBridge_2017_DET, CxC_TR_2017_PRO_DET, ImportMatrices_Before_Redefinitions_DET_2017,
  AllTablesIO/{IOUse_Before_Redefinitions_PRO_2017_Detail, IOMake_Before_Redefinitions_2017_Detail}
Output: 02_Research/Subtasks/08_shock_tagging/item_exposures.csv
Method:
  Energy: cost-push price model with energy prices exogenous. A = I - inv(TR).
    e_c = sum_{e in E} [A_EN (I - A_NN)^-1]_{e,c}  (energy cost per $ of non-energy commodity c,
    direct + indirect, no double counting across energy stages). Energy commodities get e=1.
  Imports: s_c = PCE imports of c / PCE use of c (2017, F01000, producers' prices).
    Embodied goods-import content of domestic output u_c = sum_{goods r} [A_imp (I-A_dom)^-1]_{r,c},
    A_imp = (import matrix / industry output) x market shares; A_dom = A - A_imp.
  PCE item p (bridge, purchasers' value PV): weighted by producers' value of each commodity, plus
    margins (transport -> output-weighted rail/truck/water mix; wholesale/retail -> output-weighted
    averages of those commodities). Direct import share = sum PV_c*s_c / PV_p.
"""
import os, csv, re
import numpy as np, openpyxl

ROOT = "."
RAW = ROOT + "/03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/"
OUT = ROOT + "/02_Research/Subtasks/08_shock_tagging/item_exposures.csv"
ENERGY = ["211000", "212100", "324110", "324121", "324122", "324190", "221100", "221200", "486000"]
TRANSPORT = ["481000", "482000", "483000", "484000", "485000", "486000", "48A000", "492000", "493000"]


def code(x):
    return None if x is None else str(x).strip()


def sheet(f, name="2017"):
    return list(openpyxl.load_workbook(RAW + f, read_only=True, data_only=True)[name].iter_rows(values_only=True))


def matrix(rows, hdr_row=5):
    cols = [code(c) for c in rows[hdr_row]]
    out = {}
    for r in rows[hdr_row + 1:]:
        if r[0] is None:
            continue
        out[code(r[0])] = {cols[j]: (float(v) if isinstance(v, (int, float)) else 0.0)
                           for j, v in enumerate(r) if j >= 2 and cols[j]}
    return cols, out


# Total requirements, commodity x commodity
tr = sheet("CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx")
trcols = [code(c) for c in tr[4]][2:]
trcols = [c for c in trcols if c]
trrows = [r for r in tr[5:] if r[0] is not None and code(r[0]) in trcols]
idx = {c: i for i, c in enumerate(trcols)}
L = np.zeros((len(trcols), len(trcols)))
for r in trrows:
    for j, c in enumerate(trcols):
        v = r[2 + j]
        L[idx[code(r[0])], j] = float(v) if isinstance(v, (int, float)) else 0.0
A = np.eye(len(trcols)) - np.linalg.inv(L)
n = len(trcols)
E = [idx[c] for c in ENERGY if c in idx]
missing_energy = [c for c in ENERGY if c not in idx]
N = [i for i in range(n) if i not in E]
LNN = np.linalg.inv(np.eye(len(N)) - A[np.ix_(N, N)])
energy = np.ones(n)
energy[N] = (A[np.ix_(E, N)] @ LNN).sum(axis=0)

# Imports: use, make, import matrix (before redefinitions, producers' prices)
_, use = matrix(sheet("AllTablesIO/IOUse_Before_Redefinitions_PRO_2017_Detail.xlsx"))
mkcols, make = matrix(sheet("AllTablesIO/IOMake_Before_Redefinitions_2017_Detail.xlsx"))
_, imp = matrix(sheet("ImportMatrices_Before_Redefinitions_DET_2017_retrieved_2026-11-14.xlsx"))
inds = [c for c in make if c not in ("T007",) and c in use.get("T008", {})]
indout = np.array([use["T008"][i] for i in inds])
comout = np.array([make["T007"].get(c, 0.0) for c in trcols])
Bimp = np.array([[imp.get(c, {}).get(i, 0.0) for i in inds] for c in trcols]) / np.where(indout > 0, indout, 1)
D = np.array([[make[i].get(c, 0.0) for c in trcols] for i in inds]) / np.where(comout > 0, comout, 1)
Aimp = Bimp @ D
Adom = A - Aimp
goods = np.array([c[:2] in ("11", "21", "31", "32", "33") or c[:3] == "S00" and c in ("S00401", "S00402") for c in trcols])
u = (Aimp[goods] @ np.linalg.inv(np.eye(n) - Adom)).sum(axis=0)
s = np.array([(imp.get(c, {}).get("F01000", 0.0) / use[c]["F01000"]) if use.get(c, {}).get("F01000", 0) > 0 else 0.0
              for c in trcols])
s = np.clip(s, 0, 1)
total_imp = s + (1 - s) * u


def wavg(vec, codes):
    ii = [idx[c] for c in codes if c in idx]
    w = comout[ii]
    return float((vec[ii] * w).sum() / w.sum())


wh = [c for c in trcols if c.startswith("42")]
rt = [c for c in trcols if c.startswith("4") and c[:2] in ("44", "45", "4B")]
tmix = ["482000", "483000", "484000"]
marg = {k: (wavg(energy, cs), wavg(u, cs)) for k, cs in (("T", tmix), ("W", wh), ("R", rt))}

# Bridge
br = sheet("PCEBridge_2017_DET_retrieved_2026-11-14.xlsx")
items = {}
unmatched = set()
for r in br[5:]:
    if r[0] is None:
        continue
    line, name, c = int(r[0]), r[1], code(r[2])
    pv, tc, w, rtl, pur = [float(x or 0) for x in r[4:9]]
    d = items.setdefault(line, {"name": name, "PV": 0, "en": 0, "dimp": 0, "timp": 0, "goods_pv": 0, "top": []})
    if c not in idx:
        unmatched.add(c)
        continue
    i = idx[c]
    d["PV"] += pur
    d["en"] += pv * energy[i] + tc * marg["T"][0] + w * marg["W"][0] + rtl * marg["R"][0]
    d["dimp"] += pv * s[i]
    d["timp"] += pv * total_imp[i] + tc * marg["T"][1] + w * marg["W"][1] + rtl * marg["R"][1]
    d["goods_pv"] += pv if goods[i] else 0
    d["top"].append((pv, c))


# Dallas-basket aggregates / renumbered lines -> 2017 bridge lines (bridge predates 2023 line renumbering)
AGG = {123: [122], 124: [122], 281: [283, 284, 285, 287, 288, 289], 176: [177, 178, 180, 181],
       241: [242, 243, 244], 275: [276, 277, 278], 194: [195, 196], 247: [246], 248: [246],
       218: [219, 220, 221, 222, 223], 187: [188, 189], 317: [318, 319, 320, 321, 322, 323],
       258: [259, 262, 263]}


def norm(x):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", x.lower()))


comp = [x for x in csv.DictReader(open(ROOT + "/03_Data/pipelines/Price indexes/PCE/processed/components.csv"))
        if x["index_name"] == "PCE core" and x["in_core"] == "Y"]
with open(OUT, "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["component_id", "component_name", "weight_latest", "bridge_line", "bridge_name", "name_match",
                 "bridge_PV_2017_musd", "energy_share", "direct_import_share", "total_import_content",
                 "goods_share_of_PV", "top_commodity"])
    for x in comp:
        line = int(re.search(r"line (\d+)", x["component_id"]).group(1))
        kids = AGG.get(line, [line])
        parts = [items[k] for k in kids if k in items]
        d = None
        if parts:
            d = {"name": " + ".join(q["name"] for q in parts), "top": sum((q["top"] for q in parts), [])}
            for k in ("PV", "en", "dimp", "timp", "goods_pv"):
                d[k] = sum(q[k] for q in parts)
        if not d or d["PV"] <= 0:
            wr.writerow([x["component_id"], x["component_name"], x["weight_latest"], line, "", "NO_BRIDGE_ROW"] + [""] * 6)
            continue
        m = "AGG" if line in AGG else "Y" if norm(d["name"])[:12] == norm(x["component_name"])[:12] else "CHECK"
        top = max(d["top"])[1] if d["top"] else ""
        wr.writerow([x["component_id"], x["component_name"], x["weight_latest"], line, d["name"], m, round(d["PV"]),
                     round(d["en"] / d["PV"], 4), round(d["dimp"] / d["PV"], 4), round(d["timp"] / d["PV"], 4),
                     round(d["goods_pv"] / d["PV"], 3), top])
print("commodities", n, "energy codes missing:", missing_energy, "bridge codes unmatched:", sorted(unmatched))
print("margin (energy, embodied import) T/W/R:", {k: tuple(round(v, 4) for v in t) for k, t in marg.items()})
