"""C_q6_results: Q6 scenario results from the forecast_3b pipeline outputs (Agent C, 2026-11-15).

Run from the project root after the pipeline:
    python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q3
    python3 -I 02_Research/Subtasks/12_slide3b_research/code/C_q6_results.py [2026Q3]
Reads processed/scenario_grid_<spf>.csv, sensitivity_proxy_<spf>.csv, metadata_<spf>.json; the jump-off section
also reads the pipeline raw core PCE file and the Oct m/m estimate in 01_Finals/data/Slide1_Inflation_Data.xlsx
(raw_Oct_build!B7). Writes outputs/C_q6_results.csv, C_q6_axis_compare.csv, C_q6_sensitivity.csv, C_q6_jumpoff.md.
Units: core PCE price index, SA; qq_ann = q/q annualized %; q4q4 = Q4/Q4 %. Scenarios, not probabilities.
"""
import json
import math
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
PIPE = ROOT / "03_Data/pipelines/forecast_3b"
OUT = ROOT / "02_Research/Subtasks/12_slide3b_research/outputs"
sys.path.insert(0, str(PIPE / "code"))
import forecast as F  # noqa: E402
import parsers as P  # noqa: E402

spf = sys.argv[1] if len(sys.argv) > 1 else "2026Q3"
G = pd.read_csv(PIPE / f"processed/scenario_grid_{spf}.csv")
S = pd.read_csv(PIPE / f"processed/sensitivity_proxy_{spf}.csv")
M = json.loads((PIPE / f"processed/metadata_{spf}.json").read_text())
KEYS = [("qq_ann", "2026Q4"), ("qq_ann", "2027Q4"), ("q4q4", "2026Q4/2025Q4"), ("q4q4", "2027Q4/2026Q4")]
KEYNAME = {"2026Q4": "2026Q4 q/q ann.", "2027Q4": "2027Q4 q/q ann.", "2026Q4/2025Q4": "2026 Q4/Q4", "2027Q4/2026Q4": "2027 Q4/Q4"}
LABEL = f"SPF {spf} median baseline (deadline {M['spf_deadline']}); oil assumption proxy {M['assumption_proxies']['steo_matched'].split(';')[0]}; " \
        f"core PCE actuals {M['core_pce_vintage']}; Brent to {M['oil']['last_brent_date']}"


def keyrows(df):
    return df[[ (h, q) in KEYS for h, q in zip(df.horizon, df.quarter)]]


# ------------------------------------------------------------------ 1. six cells
c = keyrows(G[G.is_central])
rows = []
for r in c.itertuples():
    rows.append(dict(spf_vintage=spf, oil_path=r.oil_path, oil_variant=r.oil_variant, regime=r.regime, measure=KEYNAME[r.quarter],
                     horizon=r.horizon, period=r.quarter, baseline=r.baseline_qq_ann, adjustment_pp=r.adj_qq_ann_pp,
                     scenario=r.scenario_qq_ann, spf_published_q4q4=r.spf_published_q4q4, oil_gap_logpts=r.oil_gap_pct,
                     note="central cell", basis=LABEL))
res = pd.DataFrame(rows)
spread = []
for m, d in res.groupby("measure", sort=False):
    spread.append(dict(spf_vintage=spf, oil_path="ALL", oil_variant="spread across 6 cells", regime="ALL", measure=m,
                       horizon=d.horizon.iloc[0], period=d.period.iloc[0], baseline=d.baseline.iloc[0],
                       adjustment_pp=d.adjustment_pp.max() - d.adjustment_pp.min(), scenario=d.scenario.max() - d.scenario.min(),
                       spf_published_q4q4=d.spf_published_q4q4.iloc[0], oil_gap_logpts=float("nan"),
                       note=f"min {d.scenario.min():.3f} ({d.loc[d.scenario.idxmin(), 'oil_variant']} x {d.loc[d.scenario.idxmin(), 'regime']}); "
                            f"max {d.scenario.max():.3f} ({d.loc[d.scenario.idxmax(), 'oil_variant']} x {d.loc[d.scenario.idxmax(), 'regime']}); "
                            "scenario = max-min (pp)", basis=LABEL))
res = pd.concat([res, pd.DataFrame(spread)], ignore_index=True)
res.to_csv(OUT / "C_q6_results.csv", index=False, float_format="%.4f")
print(res.pivot_table(index=["oil_variant", "regime"], columns="measure", values="scenario", sort=False).round(3).to_string())

# ------------------------------------------------------------------ 2. axis comparison
ax = []
cc = res[res.note == "central cell"]
for m in ["2026Q4 q/q ann.", "2027Q4 q/q ann.", "2026 Q4/Q4", "2027 Q4/Q4"]:
    d = cc[cc.measure == m]
    for g in ["pre", "post"]:
        x = d[d.regime == g].scenario
        ax.append(dict(measure=m, comparison="across oil paths (P1,P2,P3), regime held", held=g, min=x.min(), max=x.max(), range_pp=x.max() - x.min()))
    for p in ["P1", "P2", "P3"]:
        x = d[d.oil_path == p].scenario
        ax.append(dict(measure=m, comparison="across regimes (pre,post), oil path held", held=p, min=x.min(), max=x.max(), range_pp=x.max() - x.min()))
axd = pd.DataFrame(ax)
axd["basis"] = LABEL
axd.to_csv(OUT / "C_q6_axis_compare.csv", index=False, float_format="%.4f")
print(axd.round(3).drop(columns="basis").to_string())

# ------------------------------------------------------------------ 3. sensitivity rows (non-central)
nc = keyrows(G[~G.is_central])
sens = []
for r in nc.itertuples():
    why = "alt oil variant" if r.regime in F.CENTRAL_REGIMES else ("backup regime (persistence only)" if r.oil_variant in
                                                                   ("P1_steo_latest", "P2_110_flat", "P3_feb26steo_plus25") else "alt oil variant x backup regime")
    sens.append(dict(kind=why, assumption_proxy=r.assumption_proxy, oil_variant=r.oil_variant, regime=r.regime, measure=KEYNAME[r.quarter],
                     baseline=r.baseline_qq_ann, adjustment_pp=r.adj_qq_ann_pp, scenario=r.scenario_qq_ann, oil_gap_logpts=r.oil_gap_pct))
for r in keyrows(S).itertuples():
    sens.append(dict(kind="alt assumption proxy", assumption_proxy=r.assumption_proxy, oil_variant=r.oil_variant, regime=r.regime,
                     measure=KEYNAME[r.quarter], baseline=r.baseline_qq_ann, adjustment_pp=r.adj_qq_ann_pp, scenario=r.scenario_qq_ann,
                     oil_gap_logpts=r.oil_gap_pct))
sd = pd.DataFrame(sens)
sd["central"] = False
sd["flag"] = "NON-CENTRAL sensitivity row"
sd["basis"] = LABEL
sd.to_csv(OUT / "C_q6_sensitivity.csv", index=False, float_format="%.4f")
print(sd[sd.regime.isin(["pre", "post"]) & sd.measure.isin(["2027 Q4/Q4"])].pivot_table(
    index=["kind", "assumption_proxy", "oil_variant"], columns="regime", values="scenario").round(3).to_string())

# ------------------------------------------------------------------ 4. jump-off and the 2026H2 part of the adjustment
raw = ROOT / M["raw_folder"]
core = P.load_fred_obs(raw / "PCEPILFE_observations.json")
wb = openpyxl.load_workbook(ROOT / "01_Finals/data/Slide1_Inflation_Data.xlsx", data_only=False)
oct_mm = float(wb["raw_Oct_build"]["B7"].value)
sep, oct25 = float(core[pd.Timestamp("2026-09-01")]), float(core[pd.Timestamp("2025-10-01")])
q3 = float(core["2026-07-01":"2026-09-01"].mean())
q4_25 = float(core["2025-10-01":"2025-12-01"].mean())
octl = sep * (1 + oct_mm / 100)
oct_yy = 100 * (octl / oct25 - 1)


def q4_from_m(m):
    q4 = (octl + octl * (1 + m / 100) + octl * (1 + m / 100) ** 2) / 3
    return 100 * ((q4 / q3) ** 4 - 1), 100 * (q4 / q4_25 - 1)


def m_for_q4(target):
    lo, hi = -2.0, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if q4_from_m(mid)[0] < target else (lo, mid)
    return (lo + hi) / 2


I = F.Inputs(raw)
B = F.build_baseline(I, spf)
gap_q = P.qrange(B["survey_q"], F.END)
A = F.assumption_paths(I, B, gap_q)["steo_matched"]["path"]
oils, _ = F.brent_paths(I, P.qrange("2025Q1", F.END))


def scen(gaps, R):
    L = dict(zip(gap_q, F.level_adjustment(gaps, R)))
    path, prev = dict(B["base"]), 0.0
    for q in P.qrange(F.SHOW_START, F.END):
        if q in L:
            dL, prev = L[q] - prev, L[q]
            if B["status"][q] == "forecast":
                path[q] = F.apply_adjustment(B["base"][q], dL)
    return path


dec = []
b26, b27 = F.q4q4(B["base"], 2026), F.q4q4(B["base"], 2027)
for vid in ("P1_steo_latest", "P2_110_flat", "P3_feb26steo_plus25"):
    g = [100 * math.log(oils[vid]["path"][q] / A[q]) for q in gap_q]
    i4 = gap_q.index("2026Q4")
    variants = {"full": g,
                "2026H2 steps only (gap frozen at its 2026Q4 level from 2027Q1)": g[:i4 + 1] + [g[i4]] * (len(g) - i4 - 1),
                "2026Q3 step only (gap frozen at its 2026Q3 level)": [g[0]] * len(g)}
    for reg in ("pre", "post"):
        out = {}
        for name, gg in variants.items():
            p = scen(gg, I.R[reg])
            out[name] = (p["2026Q4"] - B["base"]["2026Q4"], p["2027Q4"] - B["base"]["2027Q4"],
                         F.q4q4(p, 2026) - b26, F.q4q4(p, 2027) - b27)
        for name, v in out.items():
            dec.append(dict(oil_variant=vid, regime=reg, gap_steps=name, adj_2026Q4_qq=v[0], adj_2027Q4_qq=v[1],
                            adj_2026_q4q4=v[2], adj_2027_q4q4=v[3],
                            share_of_full_2027_q4q4=(v[3] / out["full"][3]) if abs(out["full"][3]) >= 0.05 else float("nan")))  # share undefined when the full adj is ~0
    dec.append(dict(oil_variant=vid, regime="gap", gap_steps="gap path, log pts: " + ", ".join(f"{q} {x:.1f}" for q, x in zip(gap_q, g))))
dd = pd.DataFrame(dec)
dd.to_csv(OUT / "C_q6_jumpoff_decomposition.csv", index=False, float_format="%.4f")

cen = res[(res.note == "central cell") & (res.measure == "2026Q4 q/q ann.")]
lines = [f"# Q6.4 Jump-off check (Agent C, 2026-11-15)", "",
         f"Basis: {LABEL}. Numbers from `code/C_q6_results.py`; decomposition table in `outputs/C_q6_jumpoff_decomposition.csv`.",
         "Units: core PCE price index, SA. q/q ann. = quarterly-average index, annualized; Q4/Q4 = Q4 average over prior-year Q4 average.", "",
         "## 1. Baseline 2026Q4 vs our October estimate",
         f"- Oct estimate: core m/m {oct_mm:.5f}% (`01_Finals/data/Slide1_Inflation_Data.xlsx` raw_Oct_build!B7, UMD build of Nov 13) on BEA Sep index {sep:.3f}"
         f" (PCEPILFE, realtime {I.core_rt}) -> Oct index {octl:.3f}, **Oct y/y {oct_yy:.3f}%** (matches Headline!C10 3.24 est.; the cell is a formula with no cached value).",
         f"- Actual 2026Q3 q/q ann. {B['base']['2026Q3']:.3f} (SPF {spf} median for 2026Q3 was {B['spf_q'].get('2026Q3', float('nan')):.2f}).",
         f"- SPF {spf} median 2026Q4 q/q ann.: **{B['base']['2026Q4']:.4f}**. Given our Oct estimate, it requires Nov and Dec core m/m of "
         f"**{m_for_q4(B['base']['2026Q4']):.3f}% each** (vs Oct est. {oct_mm:.3f}%).",
         f"- If Nov = Dec = Oct m/m ({oct_mm:.3f}%): 2026Q4 q/q ann. {q4_from_m(oct_mm)[0]:.3f}, 2026 Q4/Q4 {q4_from_m(oct_mm)[1]:.3f}.",
         f"- Baseline 2026 Q4/Q4 built from actual Q1-Q3 + SPF Q4: {b26:.3f} (SPF published 2026 Q4/Q4 median {B['spf_a'][2026]:.4f}; gap = vintage break and Q3 miss, see A).", "",
         "| Cell (central) | 2026Q4 q/q ann. | Nov = Dec m/m needed given Oct est. | 2026 Q4/Q4 |", "|---|---|---|---|"]
for r in cen.itertuples():
    q4 = res[(res.oil_variant == r.oil_variant) & (res.regime == r.regime) & (res.measure == "2026 Q4/Q4")].scenario.iloc[0]
    lines.append(f"| {r.oil_variant} x {r.regime} | {r.scenario:.3f} | {m_for_q4(r.scenario):.3f}% | {q4:.3f} |")
lines += ["", "## 2. Size of the 2026Q3-Q4 part of the adjustment",
          "Decomposition by the date of the oil-gap step (the mapping is linear in the gap steps; tiny compounding cross-terms aside).",
          "`2026H2 steps only` = gap held at its 2026Q4 level from 2027Q1 on (only the realized/near-realized 2026Q3-Q4 oil moves); "
          "`2026Q3 step only` = gap held at its 2026Q3 level (fully realized quarter).", "",
          "| Oil path | Regime | Gap steps | adj 2026Q4 q/q (pp) | adj 2027Q4 q/q (pp) | adj 2026 Q4/Q4 (pp) | adj 2027 Q4/Q4 (pp) | share of full 2027 Q4/Q4 adj |",
          "|---|---|---|---|---|---|---|---|"]
for r in dd[dd.regime != "gap"].itertuples():
    lines.append(f"| {r.oil_variant} | {r.regime} | {r.gap_steps.split(' (')[0]} | {r.adj_2026Q4_qq:+.3f} | {r.adj_2027Q4_qq:+.3f} | {r.adj_2026_q4q4:+.3f} | {r.adj_2027_q4q4:+.3f} | {r.share_of_full_2027_q4q4:.2f} |")
lines += [""] + [f"- {r.oil_variant}: {r.gap_steps}" for r in dd[dd.regime == "gap"].itertuples()]
(OUT / "C_q6_jumpoff.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
