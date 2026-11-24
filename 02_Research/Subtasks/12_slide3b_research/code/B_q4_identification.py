"""Q4 identification check: are the Fig.2 lines consistent with Table 2 persistence if lag splits are free?
Fixes g1+g2 at the Table-2 value (grid over the split) and fits d0..d4 freely by least squares; reports RMSE vs the table
and the condition number of the unconstrained fit. Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q4_identification.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *
import numpy as np, pandas as pd
R = pd.read_csv(OUT / "B_q4_response.csv"); R = R[R.provenance == "table"]
X = 10.0
out = []
for reg, gsum in [("pre", 0.347), ("persistence_only", 0.645), ("post", 0.645)]:
    L = R[R.regime == reg].sort_values("k").level_response_pct_per_10pct.values
    pi = np.diff(np.r_[0, L]); K = len(L)
    lag = lambda k, m: pi[k - m] if k - m >= 0 else 0.0
    Afull = np.array([[lag(k, 1), lag(k, 2)] + [(X if k == j else 0) - lag(k, j) for j in range(5)] for k in range(K)])
    cond = np.linalg.cond(Afull)
    best = None
    for share in np.linspace(0, 1, 101):
        g1, g2 = share * gsum, (1 - share) * gsum
        y = pi - np.array([g1 * lag(k, 1) + g2 * lag(k, 2) for k in range(K)])
        A = Afull[:, 2:]
        d, *_ = np.linalg.lstsq(A, y, rcond=None)
        rm = float(np.sqrt(np.mean((np.cumsum(A @ d + (pi - y)) - L) ** 2)))  # one-step fitted, cumulated
        if best is None or rm < best[0]:
            best = (rm, share, d.sum(), d)
    out.append({"regime": reg, "g_sum_fixed": gsum, "best_g1_share": best[1], "fitted_d_sum": round(best[2], 5),
                "rmse_level_pct": round(best[0], 5), "table_R12": L[-1], "cond_unconstrained": round(cond, 1)})
df = pd.DataFrame(out); print(df.to_string()); df.to_csv(OUT / "B_q4_identification.csv", index=False)
