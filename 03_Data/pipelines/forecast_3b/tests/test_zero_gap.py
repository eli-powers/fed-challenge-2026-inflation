"""Unit tests for the forecast_3b pipeline (plain asserts). Run from the project root:
    python3 -I 03_Data/pipelines/forecast_3b/tests/test_zero_gap.py [--spf 2026Q3]

1. Zero oil gap returns the baseline EXACTLY (==, every quarter and both Q4/Q4 rows, every regime),
   using the real inputs of the latest raw folder: the scenario oil path is set equal to the assumed path.
2. A constant +10% (10 log points) gap from the first gap quarter reproduces the oil note's response
   function: L_k == R_k (Agent B's table), and matches B's map_gap_to_core().
3. Linearity: doubling the gap path doubles the level adjustment L and the log-approx q/q adjustment
   4*dL; the exact-compounding q/q adjustment is reported (it is linear to second order only).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "code"))
import forecast as F  # noqa: E402
import parsers as P  # noqa: E402

spf = sys.argv[sys.argv.index("--spf") + 1] if "--spf" in sys.argv else None
I = F.Inputs(F.latest_raw())
spf = spf or P.surveys_present(I.med)[-1]
B = F.build_baseline(I, spf)
gap_q = P.qrange(B["survey_q"], F.END)
assum = F.assumption_paths(I, B, gap_q)["steo_matched"]["path"]
oils, _ = F.brent_paths(I, P.qrange("2025Q1", F.END))
regimes = F.CENTRAL_REGIMES + F.BACKUP_REGIMES
print(f"raw={I.raw.name} spf={spf} gap quarters={gap_q[0]}..{gap_q[-1]} regimes={regimes}")

# ---------------------------------------------------------------- 1. zero gap -> baseline exactly
n = 0
for g in regimes:
    V = dict(path_id="TEST", central=True, label="zero gap", path={q: assum[q] for q in gap_q})
    gaps, Ld = F.run_cell(B, V["path"], assum, I.R[g], gap_q)
    assert all(x == 0.0 for x in gaps), gaps
    assert all(x == 0.0 for x in Ld.values()), Ld
    rows = F.cell_rows(B, I, spf, "TEST", V, g, Ld, gaps, assum, "steo_matched")
    for r in rows:
        assert r["scenario_qq_ann"] == r["baseline_qq_ann"], (g, r["quarter"], r["scenario_qq_ann"], r["baseline_qq_ann"])
        n += 1
print(f"PASS 1 zero gap: scenario == baseline exactly in {n} rows ({len(rows)} per regime x {len(regimes)} regimes; "
      f"{len(rows) - 2} quarters {F.SHOW_START}..{F.END} + 2 Q4/Q4 rows)")
assert F.apply_adjustment(2.6158, 0.0) == 2.6158

# ---------------------------------------------------------------- 2. constant +10% gap -> R_k
sys.path.insert(0, str(F.ROOT / "02_Research/Subtasks/12_slide3b_research/code"))
try:
    from B_common import map_gap_to_core
except Exception as e:  # noqa: BLE001
    map_gap_to_core = None
    print("  (B_common not importable, skipping the cross-check against B's function:", e, ")")
T = 13
for g in regimes:
    R = I.R[g]
    path = {q: assum[q] * math.exp(0.10) for q in gap_q}
    gaps, Ld = F.run_cell(B, path, assum, R, gap_q)
    assert all(abs(x - 10.0) < 1e-9 for x in gaps)
    L = F.level_adjustment([10.0] * T, R)
    assert max(abs(L[k] - R[k]) for k in range(T)) < 1e-12, g
    assert max(abs(list(Ld.values())[k] - R[k]) for k in range(len(gap_q))) < 1e-9, g
    if map_gap_to_core:
        LB = map_gap_to_core([10.0] * T, R)["L"]
        assert max(abs(L[k] - LB[k]) for k in range(T)) < 1e-12
    print(f"PASS 2 constant +10% gap, {g:16s}: L_k == R_k for k=0..12 (L_4={L[4]:.6f}, L_8={L[8]:.6f}, L_12={L[12]:.6f})"
          + ("; matches B's map_gap_to_core" if map_gap_to_core else ""))

# ---------------------------------------------------------------- 3. linearity
for vid in ("P1_steo_latest", "P2_110_flat", "P3_feb26steo_plus25"):
    for g in F.CENTRAL_REGIMES:
        gaps, Ld = F.run_cell(B, oils[vid]["path"], assum, I.R[g], gap_q)
        L1 = F.level_adjustment(gaps, I.R[g])
        L2 = F.level_adjustment([2 * x for x in gaps], I.R[g])
        assert max(abs(b - 2 * a) for a, b in zip(L1, L2)) < 1e-12
        d1 = [4 * (L1[t] - (L1[t - 1] if t else 0)) for t in range(len(L1))]
        d2 = [4 * (L2[t] - (L2[t - 1] if t else 0)) for t in range(len(L2))]
        assert max(abs(b - 2 * a) for a, b in zip(d1, d2)) < 1e-12
        b27 = B["base"][F.END]
        dl = L1[-1] - L1[-2]
        a1 = F.apply_adjustment(b27, dl) - b27
        a2 = F.apply_adjustment(b27, 2 * dl) - b27
        print(f"PASS 3 linearity {vid:20s} {g:4s}: L(2g)=2L(g), 4dL(2g)=2*4dL(g); exact-compounding {F.END} adj "
              f"{a1:.4f} -> {a2:.4f} pp (ratio {a2 / a1 if a1 else float('nan'):.4f}; second-order only)")
print("ALL TESTS PASSED")
