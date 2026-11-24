"""Q4: oil-to-core response function (FEDS note Fig. 2 accessible-version table), reconstruction test from Table 2 sums,
implied lag coefficients, superposition-vs-direct-simulation check, feedback-term check, and a worked mapping example.
Inputs: 03_Data/Raw/FEDS_oil_note_accessible_2026-11-15/ (raw, read only); outputs/B_q3_oil_paths.csv (from B_q3_build.py).
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q4_response.py"""
import sys, re, html, math, json, itertools
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *
import numpy as np
import pandas as pd

ACC = RAW / "FEDS_oil_note_accessible_2026-11-15/DeMichelis_oil_core_accessible_20261109.htm"
t = ACC.read_text(encoding="utf-8", errors="replace")
i0 = t.find("Figure 2: Effects on Core Prices")
i1 = t.find("Figure 3:", i0)
cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", t[i0:i1], flags=re.S)]
hdr, body = cells[:4], cells[4:]
assert hdr[0].startswith("Quarters"), hdr
REG = {"Pre-pandemic persistence and pass-through": "pre", "Stronger persistence": "persistence_only",
       "Stronger persistence and pass-through": "post"}
regs = [REG[h] for h in hdr[1:]]
tab = {r: [] for r in regs}
for j in range(0, len(body), 4):
    k = int(body[j])
    assert k == j // 4
    for r, v in zip(regs, body[j + 1:j + 4]):
        tab[r].append(float(v))
K = len(tab["post"]) - 1
print("Fig.2 table header:", hdr, "| k = 0 ..", K)

rows = []
for r in regs:
    for k, v in enumerate(tab[r]):
        rows.append({"regime": r, "k": k, "level_response_pct_per_10pct": v, "provenance": "table",
                     "source": "FEDS Note De Michelis et al. 2026-11-09, accessible version, Figure 2 data table; five-economy average"})

# ---------------- Reconstruction from Table 2 sums -----------------
SUMS = {"pre": (0.347, 0.001), "persistence_only": (0.347 + 0.298, 0.001), "post": (0.347 + 0.298, 0.001 + 0.013)}


def simulate(g1, g2, d, oil_infl, feedback=True):
    """pi_t = g1 pi_{t-1} + g2 pi_{t-2} + sum_j d_j (o_{t-j} - fb*pi_{t-j}); returns cumulative level (sum of pi)."""
    T = len(oil_infl)
    pi = np.zeros(T)
    for tt in range(T):
        v = (g1 * pi[tt - 1] if tt >= 1 else 0) + (g2 * pi[tt - 2] if tt >= 2 else 0)
        for j, dj in enumerate(d):
            if tt - j >= 0:
                # the contemporaneous term contains pi_t itself: solve pi_t (1 + fb*d0) = rest
                v += dj * oil_infl[tt - j] - (dj * pi[tt - j] if (feedback and j > 0) else 0)
        pi[tt] = v / (1 + (d[0] if feedback else 0))
    return np.cumsum(pi)


X = 10.0  # permanent 10 log-point oil rise at k=0 -> oil inflation 10 at k=0, 0 after
oil = np.zeros(K + 1); oil[0] = X
recon = []
splits_g = {"g_equal": lambda s: (s / 2, s / 2), "g_all_lag1": lambda s: (s, 0.0), "g_70_30": lambda s: (0.7 * s, 0.3 * s)}
splits_d = {"d_equal5": lambda s: [s / 5] * 5, "d_all_current": lambda s: [s, 0, 0, 0, 0],
            "d_declining": lambda s: list(np.array([5, 4, 3, 2, 1]) / 15 * s)}
for r in regs:
    gs, ds = SUMS[r]
    for (gn, gf), (dn, dfn) in itertools.product(splits_g.items(), splits_d.items()):
        L = simulate(*gf(gs), dfn(ds), oil)
        recon.append({"regime": r, "split": f"{gn}|{dn}", "R8": L[8], "R11": L[11], "R12": L[12],
                      "table_R12": tab[r][12], "err_R12": L[12] - tab[r][12], "rel_err_R12_pct": 100 * (L[12] / tab[r][12] - 1),
                      "rmse_k0_12": float(np.sqrt(np.mean((L - np.array(tab[r])) ** 2))), "path": L})
rec = pd.DataFrame(recon)
print(rec.drop(columns="path").round(4).to_string())
# long-run level effect implied by sums (no feedback approx and with): sum_d*X/(1-g+sum_d)
for r in regs:
    gs, ds = SUMS[r]
    print(r, "long-run level implied by Table-2 sums:", round(ds * X / (1 - gs + ds), 4), "| table R12:", round(tab[r][12], 4),
          "| implied pass-through sum needed to hit R12 given persistence (long-run approx):", round(tab[r][12] * (1 - gs) / (X - tab[r][12]), 4))

# best reconstruction for the post regime, saved as provenance 'reconstruction' for comparison
best_post = rec[rec.regime == "post"].sort_values("rmse_k0_12").iloc[0]
for r in regs:
    b = rec[rec.regime == r].sort_values("rmse_k0_12").iloc[0]
    for k, v in enumerate(b.path):
        rows.append({"regime": r, "k": k, "level_response_pct_per_10pct": round(float(v), 6), "provenance": "reconstruction",
                     "source": f"Simulated from Table 2 sums with split {b.split} (best-RMSE of 9 tested); NOT the note's numbers; see B_q4_mapping_math.md"})
resp = pd.DataFrame(rows)
resp.to_csv(OUT / "B_q4_response.csv", index=False)

# ---------------- Implied lag coefficients: exact OLS fit of the model to the table ---------------
# pi_k = R_k - R_{k-1}; pi_k = g1 pi_{k-1} + g2 pi_{k-2} + sum_j d_j (X 1[k=j] - pi_{k-j})   (linear in g1,g2,d0..d4)
implied = {}
for r in regs:
    R = np.array(tab[r]); pi = np.diff(np.r_[0, R])
    A, y = [], []
    for k in range(K + 1):
        lag = lambda m: pi[k - m] if k - m >= 0 else 0.0
        A.append([lag(1), lag(2)] + [(X if k == j else 0.0) - lag(j) for j in range(5)])
        y.append(pi[k])
    A, y = np.array(A), np.array(y)
    coef, res, rk, sv = np.linalg.lstsq(A, y, rcond=None)
    fit = np.cumsum(A @ coef)  # approx (uses actual lags)
    Lsim = simulate(coef[0], coef[1], coef[2:], oil)
    implied[r] = {"g1": coef[0], "g2": coef[1], "g_sum": coef[0] + coef[1], "d": list(coef[2:]), "d_sum": coef[2:].sum(),
                  "max_abs_err_sim_vs_table": float(np.max(np.abs(Lsim - R)))}
    print(r, {k: (np.round(v, 4) if not isinstance(v, list) else np.round(v, 5).tolist()) for k, v in implied[r].items()})

# ---------------- Mapping checks on actual oil paths ---------------
P = pd.read_csv(OUT / "B_q3_oil_paths.csv")
P = P[P.quarter >= "2026Q3"]
QS = quarters("2026Q3", "2027Q4")
checks, example = [], []
for vid in ["P1_steo_nov26", "P2_110_flat", "P3_feb26steo_plus25"]:
    g = P[P.variant_id == vid].set_index("quarter").loc[QS, "gap_logpts_x100"].tolist()
    for r in regs:
        R = tab[r]
        m = map_gap_to_core(g, R)
        mapx = map_gap_to_core(g, R, exact=False)
        # direct simulation using the implied coefficients (oil inflation = change in gap)
        c = implied[r]
        dg = np.diff(np.r_[0, g])
        Ldir = simulate(c["g1"], c["g2"], c["d"], dg)
        Lsup_fit = map_gap_to_core(g, list(simulate(c["g1"], c["g2"], c["d"], oil)))["L"]
        Lnofb = simulate(c["g1"], c["g2"], c["d"], dg, feedback=False)
        checks.append({"variant_id": vid, "regime": r,
                       "max_abs_superposition_minus_direct_sim_same_coefs": float(np.max(np.abs(np.array(Lsup_fit) - Ldir))),
                       "max_abs_table_superposition_minus_direct_sim": float(np.max(np.abs(np.array(m["L"]) - Ldir))),
                       "max_abs_feedback_effect_on_L": float(np.max(np.abs(Ldir - Lnofb))),
                       "L_2027Q4_table": m["L"][-1], "L_2027Q4_direct": Ldir[-1]})
        for q, L, dL, a, ax, gg in zip(QS, m["L"], m["dL"], m["a_qa"], mapx["a_qa"], g):
            example.append({"variant_id": vid, "regime": r, "quarter": q, "gap_logpts_x100": gg, "L_level_pct": round(L, 4),
                            "a_qa_pp_exact": round(a, 4), "a_qa_pp_approx": round(ax, 4)})
        L = dict(zip(QS, m["L"]))
        example.append({"variant_id": vid, "regime": r, "quarter": "Q4/Q4 2026 (L_2026Q4 - 0)", "L_level_pct": round(L["2026Q4"], 4)})
        example.append({"variant_id": vid, "regime": r, "quarter": "Q4/Q4 2027 (L_2027Q4 - L_2026Q4)", "L_level_pct": round(L["2027Q4"] - L["2026Q4"], 4)})
ck = pd.DataFrame(checks); ex = pd.DataFrame(example)
print(ck.round(5).to_string()); print(ex.to_string())
ck.to_csv(OUT / "B_q4_mapping_checks.csv", index=False)
ex.to_csv(OUT / "B_q4_worked_example.csv", index=False)
rec.drop(columns="path").to_csv(OUT / "B_q4_reconstruction_tests.csv", index=False)
(OUT / "B_q4_implied_coefs.json").write_text(json.dumps(implied, indent=1))
# 10% vs 10 log points sensitivity
print("scale factor if Fig.2 shock is 10% simple (=9.531 log pts) rather than 10 log pts:", round(10 / (100 * math.log(1.1)), 4))
# monotonicity notes
for r in regs:
    d = np.diff(tab[r]); print(r, "quarters with falling level:", [k + 1 for k, v in enumerate(d) if v < 0])
