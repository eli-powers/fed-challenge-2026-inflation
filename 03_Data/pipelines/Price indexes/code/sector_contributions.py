"""Exact contributions of BEA major product categories to headline and core PCE inflation.

Monthly Fisher contributions (exact additive decomposition):
  F - 1 = sum_i c_i,  c_i = [sqrt(P) s0_i (r_i-1) + sqrt(L) P s1_i (r_i-1)/r_i] / (sqrt(L)+sqrt(P))
with r_i the category price relative, s0/s1 prior/current nominal shares, L/P the Laspeyres/Paasche.
Multi-month: P_T/P_0 - 1 = sum_t (P_{t-1}/P_0) * sum_i c_{i,t}  (exact, additive).
3m annualized: 3m contributions scaled by k = ((1+S)^4-1)/S (S = 3m aggregate change).
Inputs: BEA U20404 (Fisher price indexes) and U20405 (nominal $), current vintage.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "PCE" / "raw", ROOT / "Cross-index analysis" / "processed"

HEADLINE = {4: "Motor vehicles and parts", 23: "Furnishings and durable household equipment",
            38: "Recreational goods and vehicles", 62: "Other durable goods",
            73: "Food and beverages (off-premises)", 104: "Clothing and footwear",
            113: "Gasoline and other energy goods", 120: "Other nondurable goods",
            152: "Housing and utilities", 172: "Health care", 190: "Transportation services",
            209: "Recreation services", 234: "Food services and accommodations",
            252: "Financial services and insurance", 280: "Other services", 342: "Nonprofit institutions (NPISH)"}
CORE = {k: v for k, v in HEADLINE.items() if k not in (73, 113, 152)}
CORE.update({153: "Housing", 166: "Water supply and sanitation"})

def load(table, vintage):
    rows = json.load(open(RAW / f"BEA_NIUnderlyingDetail_{table}_{vintage}.json"))["BEAAPI"]["Results"]["Data"]
    df = pd.DataFrame(rows)
    df["v"] = df.DataValue.str.replace(",", "").astype(float)
    df["t"] = pd.PeriodIndex(df.TimePeriod.str.replace("M", "-"), freq="M")
    df["LineNumber"] = df.LineNumber.astype(int)
    return df.pivot_table(index="t", columns="LineNumber", values="v").sort_index()

def monthly_contrib(p, n, lines):
    r = p[lines] / p[lines].shift(1)
    s = n[lines].div(n[lines].sum(axis=1), axis=0)
    s0, s1 = s.shift(1), s
    L = (s0 * r).sum(axis=1); P = 1 / (s1 / r).sum(axis=1)
    c = (np.sqrt(P).values[:, None] * s0 * (r - 1) + (np.sqrt(L) * P).values[:, None] * s1 * (r - 1) / r)
    c = c.div(np.sqrt(L) + np.sqrt(P), axis=0)
    F = np.sqrt(L * P)
    return c.iloc[1:], F.iloc[1:]

def window(c, F, end, months):
    i = c.index.get_loc(end)
    cw, Fw = c.iloc[i - months + 1:i + 1], F.iloc[i - months + 1:i + 1]
    lvl = Fw.cumprod().shift(1).fillna(1.0)          # P_{t-1}/P_0
    contrib = cw.mul(lvl, axis=0).sum() * 100          # pp of the cumulative change
    S = (Fw.prod() - 1) * 100
    return contrib, S

def run(vintage="2026-10-01", end="2026-08"):
    p, n = load("U20404", vintage), load("U20405", vintage)
    end = pd.Period(end, "M")
    out = []
    for label, comp, agg in [("Headline PCE", HEADLINE, 1), ("Core PCE", CORE, 374)]:
        lines = list(comp)
        gap = (n[lines].sum(axis=1) - n[agg]).abs().max()
        assert gap < 5, f"{label}: nominal components do not sum to line {agg} (max gap {gap})"
        c, F = monthly_contrib(p, n, lines)
        c12, S12 = window(c, F, end, 12)
        c3, S3 = window(c, F, end, 3)
        k = ((1 + S3 / 100) ** 4 - 1) / (S3 / 100)
        c3a = c3 * k
        # 2018-19 average 12m contribution
        base = pd.concat([window(c, F, t, 12)[0] for t in pd.period_range("2018-01", "2019-12", freq="M")], axis=1).mean(axis=1)
        pub12 = (p[agg][end] / p[agg][end - 12] - 1) * 100
        pub3 = ((p[agg][end] / p[agg][end - 3]) ** 4 - 1) * 100
        share = n[lines].loc[end] / n[agg][end] * 100
        share0 = n[lines].loc[end - 12] / n[agg][end - 12] * 100
        rate12 = (p[lines].loc[end] / p[lines].loc[end - 12] - 1) * 100
        rate3 = ((p[lines].loc[end] / p[lines].loc[end - 3]) ** 4 - 1) * 100
        for ln in lines:
            out.append(dict(index=label, line=ln, category=comp[ln], weight_now=share[ln], weight_start=share0[ln],
                            rate_12m=rate12[ln], contrib_12m=c12[ln], rate_3m_ann=rate3[ln], contrib_3m_ann=c3a[ln],
                            contrib_12m_2018_19_avg=base[ln], excess_vs_2018_19=c12[ln] - base[ln]))
        out.append(dict(index=label, line=agg, category=f"TOTAL (sum of contributions)", weight_now=share.sum(),
                        weight_start=share0.sum(), rate_12m=pub12, contrib_12m=c12.sum(), rate_3m_ann=pub3,
                        contrib_3m_ann=c3a.sum(), contrib_12m_2018_19_avg=base.sum(), excess_vs_2018_19=c12.sum() - base.sum()))
        print(f"{label}: sum 12m {c12.sum():.3f} vs published {pub12:.3f}; 3m ann {c3a.sum():.3f} vs published {pub3:.3f}")
    df = pd.DataFrame(out)
    df.to_csv(OUT / f"pce_sector_contributions_{end}.csv", index=False)
    return df

if __name__ == "__main__":
    df = run(*sys.argv[1:])
    pd.set_option("display.width", 220)
    print(df.round(3).to_string(index=False))
