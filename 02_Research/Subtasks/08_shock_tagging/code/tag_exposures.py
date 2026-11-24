"""Subtask 08 (full version): I-O energy and import exposure per core PCE item. DRAFT for Eli's approval.

Differences from io_exposures.py (written concurrently by another process, kept unchanged):
  * maps the 13 current-vintage aggregate lines (e.g. 281 Communication, 123/124 drugs) to their
    2017-bridge leaf lines, so all 149 items get numbers;
  * pipeline transport (486000) is NOT in the main energy block; it enters the alternative
    "transport as energy channel" block with the other transport commodities;
  * builds A from use/make (industry technology) and validates against BEA's published CxC TR;
  * adds first-round (direct) energy share and the transport-inclusive alternative.

Inputs: 03_Data/Raw/BEA_IO_shock_tagging_2026-11-14/ (BEA 2017 benchmark detail tables, retrieved 2026-11-14)
Output: 02_Research/Subtasks/08_shock_tagging/item_exposures_full.csv
Run:    python3 -I code/tag_exposures.py "<project root>"
Method: see docstring of io_exposures.py; same formulas. Energy: E_c = 1' A_EN (I - A_NN)^-1 [.,c].
        Imports: direct s_c (PCE imports / PCE use, goods only); embodied u_c = 1'_goods A_M (I - A_D)^-1.
        Item = producers'-value-weighted commodities + margins at output-weighted margin-commodity averages,
        divided by purchasers' value.
"""
import csv, re, sys
from pathlib import Path
import numpy as np, openpyxl

ROOT = Path(sys.argv[1])
RAW = ROOT / "03_Data/Raw/BEA_IO_shock_tagging_2026-11-14"
OUT = ROOT / "02_Research/Subtasks/08_shock_tagging/item_exposures_full.csv"
COMP = ROOT / "03_Data/pipelines/Price indexes/PCE/processed/components.csv"


def code(x):
    return None if x is None else str(x).strip()


def read_matrix(path, hdr_row=5):
    rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True)["2017"].iter_rows(values_only=True))
    cols = [code(c) for c in rows[hdr_row]]
    data = {}
    for r in rows[hdr_row + 1:]:
        if r[0] is None:
            continue
        data[code(r[0])] = {cols[j]: (float(r[j]) if isinstance(r[j], (int, float)) else 0.0)
                            for j in range(2, len(cols)) if cols[j]}
    return data, [c for c in cols[2:] if c]


use, _ = read_matrix(RAW / "AllTablesIO/IOUse_Before_Redefinitions_PRO_2017_Detail.xlsx")
make, make_cols = read_matrix(RAW / "AllTablesIO/IOMake_Before_Redefinitions_2017_Detail.xlsx")
imp, _ = read_matrix(RAW / "ImportMatrices_Before_Redefinitions_DET_2017_retrieved_2026-11-14.xlsx")
tr, tr_cols = read_matrix(RAW / "CxC_TR_2017_PRO_DET_retrieved_2026-11-14.xlsx", hdr_row=4)

inds = [k for k in make if not k.startswith("T")]
comms = [c for c in make_cols if not c.startswith("T")]
ci = {c: i for i, c in enumerate(comms)}
nC = len(comms)
g = np.array([make[i]["T008"] for i in inds])
q = np.array([make["T007"][c] for c in comms])
V = np.array([[make[i].get(c, 0) for c in comms] for i in inds])
U = np.array([[use.get(c, {}).get(i, 0) for i in inds] for c in comms])
M = np.array([[imp.get(c, {}).get(i, 0) for i in inds] for c in comms])
gs = np.where(g > 0, g, 1.0); qs = np.where(q > 0, q, 1.0)
D = V / qs
A = (U / gs) @ D
Am = (M / gs) @ D
Ad = A - Am

# validation vs BEA published total requirements (BEA TR may differ: scrap/used-goods treatment, redefinitions)
common = [c for c in comms if c in tr and c in tr_cols]
ix = [ci[c] for c in common]
Lm = np.linalg.inv(np.eye(nC) - A)[np.ix_(ix, ix)]
Lb = np.array([[tr[r].get(c, 0) for c in common] for r in common])
cs = np.abs(Lm.sum(0) - Lb.sum(0))
assert len(common) == nC
print(f"TR validation: {len(common)} commodities; max cell diff {np.abs(Lm-Lb).max():.4f}; "
      f"colsum diff median {np.median(cs):.4f}, 95th pct {np.percentile(cs,95):.4f}, max {cs.max():.4f}")

ENERGY = ({"211000", "212100", "221100", "221200", "S00101", "S00202"} | {c for c in comms if c.startswith("3241")}) & set(comms)
TRANSPORT = {c for c in comms if c[:3] in ("481", "482", "483", "484", "485", "486", "48A", "492")}
GOODS = {c for c in comms if c[:2] in ("11", "21", "31", "32", "33")}
print("energy block:", sorted(ENERGY)); print("transport block:", sorted(TRANSPORT))


def exposure(Amat, block):
    X = [ci[c] for c in comms if c in block]
    N = [ci[c] for c in comms if c not in block]
    e = np.ones(nC)
    e[N] = Amat[np.ix_(X, N)].sum(0) @ np.linalg.inv(np.eye(len(N)) - Amat[np.ix_(N, N)])
    return e


# main energy measures use BEA's published total requirements (A_bea = I - TR^-1, after redefinitions);
# the before-redefinitions A built above (needed for imports) gives a robustness column.
A_bea = np.zeros((nC, nC))
A_bea[np.ix_(ix, ix)] = np.eye(len(ix)) - np.linalg.inv(Lb)
E_main = exposure(A_bea, ENERGY)
E_alt = exposure(A_bea, ENERGY | TRANSPORT)
E_bef = exposure(A, ENERGY)
EI = [ci[c] for c in ENERGY]
E_dir = A_bea[EI, :].sum(0); E_dir[EI] = 1.0

pu = np.array([use.get(c, {}).get("F01000", 0) for c in comms])
pm = np.array([imp.get(c, {}).get("F01000", 0) for c in comms])
s = np.clip(np.where(pu > 0, pm / np.where(pu > 0, pu, 1), 0.0), 0, 1)
s_g = np.array([s[ci[c]] if c in GOODS else 0.0 for c in comms])
gi = [ci[c] for c in comms if c in GOODS]
u = Am[gi, :].sum(0) @ np.linalg.inv(np.eye(nC) - Ad)
Mtot = s_g + (1 - s) * u


def wavg(vec, codes):
    k = [ci[c] for c in codes if c in ci]
    return float((vec[k] * q[k]).sum() / q[k].sum())


TRM = ["482000", "483000", "484000"]
WHM = [c for c in comms if c.startswith("42")]
RTM = [c for c in comms if c[:2] in ("44", "45") or c == "4B0000"]
RTM = [c for c in RTM if c != "447000"]
meas = {"energy_main": E_main, "energy_alt_transport": E_alt, "energy_direct_only": E_dir, "energy_before_redef": E_bef,
        "import_direct_goods": s_g, "import_total_goods": Mtot}
marg = {k: tuple(wavg(v, cc) for cc in (TRM, WHM, RTM)) for k, v in meas.items()}
marg["import_direct_goods"] = (0.0, 0.0, 0.0)
marg["import_total_goods"] = tuple(wavg(u, cc) for cc in (TRM, WHM, RTM))
print("margin values (transport, wholesale, retail):", {k: tuple(round(x, 4) for x in v) for k, v in marg.items()})

br = {}
for r in list(openpyxl.load_workbook(RAW / "PCEBridge_2017_DET_retrieved_2026-11-14.xlsx", read_only=True)["2017"]
              .iter_rows(values_only=True))[5:]:
    if r[0] is not None:
        br.setdefault(int(r[0]), []).append((code(r[2]), *(float(x or 0) for x in r[4:9])))
brname = {}
for r in list(openpyxl.load_workbook(RAW / "PCEBridge_2017_DET_retrieved_2026-11-14.xlsx", read_only=True)["2017"]
              .iter_rows(values_only=True))[5:]:
    if r[0] is not None:
        brname.setdefault(int(r[0]), r[1])

AGG = {123: [122], 124: [122], 176: [177, 178, 180, 181], 187: [188, 189], 194: [195, 196],
       218: [219, 220, 221, 222, 223], 241: [242, 243, 244], 247: [246], 248: [246],
       275: [276, 277, 278]}
for k, (lo, hi) in {258: (259, 270), 281: (282, 290), 317: (318, 323)}.items():
    AGG[k] = sorted(l for l in br if lo <= l <= hi)

items = [x for x in csv.DictReader(open(COMP)) if x["index_name"] == "PCE core" and x["in_core"] == "Y"]
rows = []
for x in items:
    ln = int(re.search(r"line (\d+)", x["component_id"]).group(1))
    lines = AGG.get(ln, [ln])
    flat = [t for l in lines for t in br.get(l, [])]
    pur = sum(t[5] for t in flat); pvs = sum(t[1] for t in flat)
    rec = {"component_id": x["component_id"], "component_name": x["component_name"],
           "weight_latest": float(x["weight_latest"]), "bridge_lines": ";".join(map(str, lines)),
           "bridge_names": " | ".join(brname.get(l, "?") for l in lines), "bridge_purch_value_2017_musd": pur}
    for k, v in meas.items():
        tm, wm, rm = marg[k]
        rec[k] = sum(pv * v[ci[c]] + t * tm + w * wm + rr * rm for c, pv, t, w, rr, _ in flat) / pur
    rec["import_direct_goods_pv_basis"] = (sum(pv * s_g[ci[c]] for c, pv, *_ in flat) / pvs) if pvs else 0.0
    rec["goods_share_of_producer_value"] = sum(t[1] for t in flat if t[0] in GOODS) / pvs if pvs else 0
    top = {}
    for t in flat:
        top[t[0]] = top.get(t[0], 0) + t[5]
    rec["top_commodity"] = max(top, key=top.get); rec["top_commodity_share"] = top[rec["top_commodity"]] / pur
    rows.append(rec)
print("items", len(rows), "weight", round(sum(r["weight_latest"] for r in rows), 6),
      "missing bridge", [r["component_name"] for r in rows if r["bridge_purch_value_2017_musd"] <= 0])
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    for r in rows:
        w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
print("wrote", OUT)
