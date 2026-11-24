"""Subtask 08: apply DRAFT tagging rules to core PCE items (no prices used). For Eli's approval.

Input : item_exposures_full.csv (from tag_exposures.py)
Output: proposed_tags.csv, tag_summary.csv  (in 02_Research/Subtasks/08_shock_tagging/)
Run   : python3 -I code/tag_rules.py "<project root>"

Rules (main / alternative) -- all thresholds are proposals:
  ENERGY  main: energy_main >= 0.05 (about 2x the core-weighted mean 0.026)
          alt : energy_main >= weighted 75th percentile of core (top quartile by weight)
          transport sensitivity: energy_alt_transport (transport services counted as energy) >= 0.10
  TARIFF  main: goods item (goods >= 50% of bridge producers' value) and direct import share of
                purchasers' value >= 0.15
          alt : total import content (direct + embodied imported goods) >= 0.20, any item
  AI      main: explicit list AI_MAIN; alt: AI_MAIN + AI_ALT_ADD
  Priority: AI > tariff > energy > untagged (alt priority swaps AI and tariff: reported as overlap flag)

FINAL (Eli-approved 2026-11-14) -> column tag_final:
  AI     = AI_MAIN (narrow list; line 258 and TVs/audio/video stay in the alt sensitivity only)
  TARIFF = tariff main rule EXCEPT Rx/non-Rx drugs (lines 123, 124): realized pharma tariffs ~0
           (Minneapolis Fed, Apr 8 2026), so untagged in final; kept in main/alt sensitivity
  ENERGY = top quartile by core weight (energy_main >= weighted p75); strict 5% is the robustness check
  OVERRIDES: line 228 lotteries -> untagged (energy share is an I-O mapping artifact, S00203)
  Transport: fuel-only (main energy measure). Used vehicles untagged.
  Priority AI > tariff > energy (AI>tariff pending verification of 2025 reciprocal-tariff exemption
  for computers/smartphones)
"""
import csv, sys
from pathlib import Path
import numpy as np

ROOT = Path(sys.argv[1]); D = ROOT / "02_Research/Subtasks/08_shock_tagging"
rows = list(csv.DictReader(open(D / "item_exposures_full.csv")))
for r in rows:
    for k in r:
        if k not in ("component_id", "component_name", "bridge_lines", "bridge_names", "top_commodity"):
            r[k] = float(r[k])
line = lambda r: int(r["component_id"].split("line ")[1].split(" ")[0])

AI_MAIN = {49: "PCs/tablets/peripherals: DRAM/NAND and processors are core inputs; AI data-center demand competes for the same memory and chip supply",
           50: "Software (incl. 2017-bridge data processing/hosting 518200): direct AI product/feature pricing and cloud compute",
           51: "Other information processing equipment: same semiconductor/memory input channel as PCs (tiny weight)",
           71: "Telephones/smartphones: memory- and chip-intensive; same AI-driven component-cost channel"}
AI_ALT_ADD = {41: "Televisions: semiconductor/memory content (consumer-electronics channel)",
              42: "Other video equipment (incl. game consoles): memory-intensive; Minneapolis Fed flags high inflation without large tariffs",
              43: "Audio equipment: semiconductor content",
              258: "Financial service charges/fees/commissions: contains portfolio management fees that move with equity prices; AI-driven equity rally channel (asset-price, not cost)"}

w = np.array([r["weight_latest"] for r in rows]); e = np.array([r["energy_main"] for r in rows])
o = np.argsort(e); cw = np.cumsum(w[o]); E_P75 = float(e[o][np.searchsorted(cw, 0.75)])
print("energy weighted p75 =", round(E_P75, 4), "core-weighted mean =", round(float(e @ w), 4))


FINAL_TARIFF_EXCLUDE = {123, 124}
FINAL_UNTAG = {228}


def tags_final(r):
    ln = line(r)
    if ln in FINAL_UNTAG:
        return []
    q = []
    if ln in AI_MAIN:
        q.append("AI")
    if r["goods_share_of_producer_value"] >= 0.5 and r["import_direct_goods"] >= 0.15 and ln not in FINAL_TARIFF_EXCLUDE:
        q.append("tariff")
    if r["energy_main"] >= E_P75:
        q.append("energy")
    return q


def tags(r, alt=False):
    q = []
    ln = line(r)
    if ln in AI_MAIN or (alt and ln in AI_ALT_ADD):
        q.append("AI")
    goods = r["goods_share_of_producer_value"] >= 0.5
    if (not alt and goods and r["import_direct_goods"] >= 0.15) or (alt and r["import_total_goods"] >= 0.20):
        q.append("tariff")
    if r["energy_main"] >= (E_P75 if alt else 0.05):
        q.append("energy")
    return q


out = []
for r in rows:
    qm, qa = tags(r), tags(r, alt=True)
    ln = line(r)
    tag_m = qm[0] if qm else "untagged"
    tag_a = qa[0] if qa else "untagged"
    if tag_m == "AI":
        basis = AI_MAIN[ln]
    elif tag_m == "tariff":
        basis = f"direct import share {r['import_direct_goods']:.3f} (goods)"
    elif tag_m == "energy":
        basis = f"energy cost share {r['energy_main']:.3f}"
    else:
        basis = f"E={r['energy_main']:.3f}; Mdir={r['import_direct_goods']:.3f}; Mtot={r['import_total_goods']:.3f}"
    qf = tags_final(r)
    out.append({"component_id": r["component_id"], "component_name": r["component_name"],
                "tag_final": qf[0] if qf else "untagged", "overlap_final": "+".join(qf) if len(qf) > 1 else "",
                "weight_latest": r["weight_latest"], "tag_main": tag_m, "basis_main": basis,
                "overlap_main": "+".join(qm) if len(qm) > 1 else "", "tag_alt": tag_a,
                "overlap_alt": "+".join(qa) if len(qa) > 1 else "",
                "energy_transport_sens": "energy" if r["energy_alt_transport"] >= 0.10 else "",
                "energy_main": r["energy_main"], "energy_alt_transport": r["energy_alt_transport"],
                "import_direct_goods": r["import_direct_goods"], "import_total_goods": r["import_total_goods"],
                "goods_share": r["goods_share_of_producer_value"], "bridge_lines": r["bridge_lines"]})
out.sort(key=lambda x: (["AI", "tariff", "energy", "untagged"].index(x["tag_main"]), -x["weight_latest"]))
with open(D / "proposed_tags.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(out[0])); wr.writeheader()
    for x in out:
        wr.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in x.items()})

summ = []
for col in ("tag_final", "tag_main", "tag_alt"):
    for t in ("AI", "tariff", "energy", "untagged"):
        s = [x for x in out if x[col] == t]
        summ.append({"scheme": col, "tag": t, "n_items": len(s), "core_weight_share": round(sum(x["weight_latest"] for x in s), 4)})
# one-at-a-time sensitivities (alt rule for one tag, main rules for others) and pre-priority counts
for name, fn in {"energy_alt_only": lambda r: r["energy_main"] >= E_P75,
                 "energy_transport_sens": lambda r: r["energy_alt_transport"] >= 0.10,
                 "energy_main_raw": lambda r: r["energy_main"] >= 0.05,
                 "tariff_main_raw": lambda r: r["goods_share_of_producer_value"] >= 0.5 and r["import_direct_goods"] >= 0.15,
                 "tariff_alt_raw": lambda r: r["import_total_goods"] >= 0.20}.items():
    s = [r for r in rows if fn(r)]
    summ.append({"scheme": "pre-priority " + name, "tag": "", "n_items": len(s),
                 "core_weight_share": round(sum(r["weight_latest"] for r in s), 4)})
for name, L in (("ai_main_raw", AI_MAIN), ("ai_alt_raw", {**AI_MAIN, **AI_ALT_ADD})):
    s = [r for r in rows if line(r) in L]
    summ.append({"scheme": "pre-priority " + name, "tag": "", "n_items": len(s),
                 "core_weight_share": round(sum(r["weight_latest"] for r in s), 4)})
with open(D / "tag_summary.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(summ[0])); wr.writeheader(); wr.writerows(summ)
for s in summ:
    print(s)
