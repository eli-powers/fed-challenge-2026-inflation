"""Gap sensitivity: 2027 gaps (log pts x100) vs Agent A's Aug-11-2026 NYMEX Brent futures quarterly means, compared with the
provisional Aug-2026 STEO basis. Reads outputs/B_q3_oil_paths.csv and outputs/A_q2_oil_assumption.csv (read only).
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q3_gap_sensitivity.py"""
import sys, math
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *
import pandas as pd
P = pd.read_csv(OUT / "B_q3_oil_paths.csv"); A = pd.read_csv(OUT / "A_q2_oil_assumption.csv")
fut = A[A.proxy.str.startswith("NYMEX Brent futures (BZ), quarterly")].set_index("quarter").brent_usd
P = P[P.quarter.isin(fut.index)].copy()
P["fut_aug11"] = P.quarter.map(fut)
P["gap_vs_fut_aug11"] = (100 * (P.brent_usd / P.fut_aug11).apply(math.log)).round(1)
out = P.pivot(index="variant_id", columns="quarter", values="gap_vs_fut_aug11")
out2 = P.pivot(index="variant_id", columns="quarter", values="gap_logpts_x100").round(1)
print("assumption (Aug-11 futures, A):", fut.round(2).to_dict())
print("gap vs Aug-11 futures:\n", out.to_string()); print("gap vs Aug STEO (provisional):\n", out2.to_string())
P[["variant_id", "quarter", "brent_usd", "fut_aug11", "gap_vs_fut_aug11", "assumption_usd", "gap_logpts_x100"]].to_csv(OUT / "B_q3_gap_sensitivity.csv", index=False)
