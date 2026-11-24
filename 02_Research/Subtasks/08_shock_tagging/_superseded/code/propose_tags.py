"""Apply draft tag rules to item_exposures.csv -> proposed_tags.csv + summary printout.
Rules are DRAFT pending Eli's approval. No price data used. Run: python3 -I propose_tags.py
"""
import csv
import numpy as np

D = "./02_Research/Subtasks/08_shock_tagging/"
rows = list(csv.DictReader(open(D + "item_exposures.csv")))
for r in rows:
    r["w"] = float(r["weight_latest"])
    r["line"] = int(r["bridge_line"])
    for k in ("energy_share", "direct_import_share", "total_import_content", "goods_share_of_PV"):
        r[k] = float(r[k])
    r["is_goods"] = r["line"] < 150   # PCE goods block (durable + nondurable lines) in U20404

AI_MAIN = {49: "PCs/tablets/peripherals: semiconductor + memory content; AI data-center demand competes for DRAM/NAND",
           50: "Software and accessories: the product category most directly repriced by AI features/subscriptions",
           51: "Other information processing equipment: same chip/memory input channel as PCs",
           71: "Telephones/smartphones: memory- and chip-intensive; on-device AI hardware upgrades"}
AI_ALT = {41: "Televisions: semiconductor/display-chip content", 42: "Other video equipment: chip content",
          43: "Audio equipment: chip content", 47: "Photographic equipment: image sensors/chips",
          281: "Communication (cellular, internet access): network/data-center capex pass-through",
          218: "AV and information processing equipment services (incl. streaming)",
          258: "Financial service charges/fees: portfolio-management fees track AI-driven equity valuations"}
TRANSPORT_LINES = {197, 198, 201, 203, 204, 205, 206, 207, 208, 329}

w = np.array([r["w"] for r in rows])


def wq(vals, q):
    o = np.argsort(vals)
    cw = np.cumsum(w[o]) / w.sum()
    return float(np.array(vals)[o][np.searchsorted(cw, q)])


en = [r["energy_share"] for r in rows]
EN_FIXED, EN_Q75 = 0.05, wq(en, 0.75)
goods_imp = [r["direct_import_share"] for r in rows if r["is_goods"]]
TAR_MAIN, TAR_ALT_TOTAL = 0.20, 0.20


def flags(r, energy_rule, tariff_rule, ai_set):
    f = []
    if r["line"] in ai_set:
        f.append("AI")
    if tariff_rule(r):
        f.append("tariff")
    if energy_rule(r):
        f.append("energy")
    return f


rules = {
    "main": (lambda r: r["energy_share"] >= EN_FIXED,
             lambda r: r["is_goods"] and r["direct_import_share"] >= TAR_MAIN, AI_MAIN),
    "alt_energy_q75": (lambda r: r["energy_share"] >= EN_Q75,
                       lambda r: r["is_goods"] and r["direct_import_share"] >= TAR_MAIN, AI_MAIN),
    "alt_energy_plus_transport": (lambda r: r["energy_share"] >= EN_FIXED or r["line"] in TRANSPORT_LINES,
                                  lambda r: r["is_goods"] and r["direct_import_share"] >= TAR_MAIN, AI_MAIN),
    "alt_tariff_total_content": (lambda r: r["energy_share"] >= EN_FIXED,
                                 lambda r: r["total_import_content"] >= TAR_ALT_TOTAL, AI_MAIN),
    "alt_tariff_30pct": (lambda r: r["energy_share"] >= EN_FIXED,
                         lambda r: r["is_goods"] and r["direct_import_share"] >= 0.30, AI_MAIN),
    "alt_ai_broad": (lambda r: r["energy_share"] >= EN_FIXED,
                     lambda r: r["is_goods"] and r["direct_import_share"] >= TAR_MAIN, {**AI_MAIN, **AI_ALT}),
}
PRIORITY = ["AI", "tariff", "energy"]
print(f"energy weighted 75th pct = {EN_Q75:.4f}")
for name, (er, tr, ai) in rules.items():
    tally = {}
    for r in rows:
        f = flags(r, er, tr, ai)
        tag = next((p for p in PRIORITY if p in f), "untagged")
        t = tally.setdefault(tag, [0, 0.0])
        t[0] += 1; t[1] += r["w"]
        if name == "main":
            r["tag"], r["overlap"] = tag, "+".join(f) if len(f) > 1 else ""
    print(name, {k: (v[0], round(100 * v[1] / w.sum(), 1)) for k, v in sorted(tally.items())})

with open(D + "proposed_tags.csv", "w", newline="") as fh:
    wr = csv.writer(fh)
    wr.writerow(["component_id", "component_name", "weight_latest", "proposed_tag", "basis", "overlap_flag",
                 "energy_share", "direct_import_share", "total_import_content", "is_goods"])
    for r in sorted(rows, key=lambda r: (PRIORITY + ["untagged"]).index(r["tag"])):
        b = (AI_MAIN[r["line"]] if r["tag"] == "AI" else
             f"direct import share {r['direct_import_share']:.3f}" if r["tag"] == "tariff" else
             f"energy cost share {r['energy_share']:.3f}" if r["tag"] == "energy" else
             f"en {r['energy_share']:.3f}; imp {r['direct_import_share']:.3f}")
        wr.writerow([r["component_id"], r["component_name"], r["weight_latest"], r["tag"], b, r["overlap"],
                     r["energy_share"], r["direct_import_share"], r["total_import_content"], r["is_goods"]])
