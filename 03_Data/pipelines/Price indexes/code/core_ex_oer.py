"""Core PCE excluding owner-occupied housing (OER), derived from BEA published aggregates.

Removes one component from a BEA chain-type Fisher index exactly at the two-part level:
each month, the aggregate's Fisher price relative F satisfies F^2 = L * P with
  L = s_R,t-1 * r_R + s_X,t-1 * r_X          (Laspeyres, prior-month nominal shares)
  P = 1 / (w_R,t / r_R + w_X,t / r_X)         (Paasche, current-month nominal shares)
where X is the excluded component (published price relative r_X) and R the remainder.
Solve for r_R, then chain. Inputs: U20404 (Fisher price indexes), U20405 (nominal $).
Validation: (PCE services ex energy, line 376) minus (housing, line 153) vs BEA's
published PCE services excluding energy and housing (T20804 line 28).
"""
import json, glob, sys
from pathlib import Path
from scipy.optimize import brentq
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "PCE" / "raw"
OUT = Path(__file__).resolve().parents[1] / "Cross-index analysis" / "processed"

def load(table, vintage):
    rows = json.load(open(RAW / f"BEA_NIUnderlyingDetail_{table}_{vintage}.json"))["BEAAPI"]["Results"]["Data"]
    df = pd.DataFrame(rows)
    df["v"] = df.DataValue.str.replace(",", "").astype(float)
    df["t"] = pd.PeriodIndex(df.TimePeriod.str.replace("M", "-"), freq="M")
    return df.pivot_table(index="t", columns="LineNumber", values="v")

def remove(price, nom, agg, excl):
    """Return chained price index of agg minus the list of excluded lines."""
    pa, na = price[agg], nom[agg]
    px = price[excl[0]] if len(excl) == 1 else None
    nx = nom[excl].sum(axis=1)
    if px is None:  # combine excluded lines into one Fisher component first
        px = remove_combine(price, nom, excl)
    idx = [100.0]
    for t in range(1, len(pa)):
        F = pa.iloc[t] / pa.iloc[t - 1]
        rx = px.iloc[t] / px.iloc[t - 1]
        sx0 = nx.iloc[t - 1] / na.iloc[t - 1]; sr0 = 1 - sx0
        wx1 = nx.iloc[t] / na.iloc[t]; wr1 = 1 - wx1
        f = lambda r: (sr0 * r + sx0 * rx) / (wr1 / r + wx1 / rx) - F * F
        idx.append(idx[-1] * brentq(f, 0.5, 1.5))
    return pd.Series(idx, index=pa.index)

def remove_combine(price, nom, lines):
    # Fisher aggregate of a few lines (only used if several excluded lines are passed)
    idx = [100.0]
    for t in range(1, len(price)):
        r = price[lines].iloc[t] / price[lines].iloc[t - 1]
        n0, n1 = nom[lines].iloc[t - 1], nom[lines].iloc[t]
        L = (n0 * r).sum() / n0.sum(); P = n1.sum() / (n1 / r).sum()
        idx.append(idx[-1] * (L * P) ** 0.5)
    return pd.Series(idx, index=price.index)

def rates(s):
    return {"12m": (s.iloc[-1] / s.iloc[-13] - 1) * 100,
            "6m_ann": ((s.iloc[-1] / s.iloc[-7]) ** 2 - 1) * 100,
            "3m_ann": ((s.iloc[-1] / s.iloc[-4]) ** 4 - 1) * 100,
            "mom": (s.iloc[-1] / s.iloc[-2] - 1) * 100}

if __name__ == "__main__":
    vintage = sys.argv[1] if len(sys.argv) > 1 else "2026-10-01"
    p, n = load("U20404", vintage), load("U20405", vintage)
    # validation against published supercore
    t28 = json.load(open(RAW / f"BEA_NIPA_T20804_{vintage}.json"))["BEAAPI"]["Results"]["Data"]
    sc = pd.Series({pd.Period(r["TimePeriod"].replace("M", "-"), "M"): float(r["DataValue"].replace(",", ""))
                    for r in t28 if r["LineNumber"] == "28"}).sort_index().reindex(p.index)
    test = remove(p, n, "376", ["153"])
    out = []
    for name, s in [("Core PCE (published, line 374)", p["374"]),
                    ("Core PCE excl. owner-occupied housing (derived: 374 minus 160)", remove(p, n, "374", ["160"])),
                    ("Core PCE excl. all housing (derived: 374 minus 153)", remove(p, n, "374", ["153"])),
                    ("VALIDATION derived: 376 minus 153", test),
                    ("VALIDATION published supercore (T20804 line 28)", sc)]:
        r = rates(s); r["series"] = name; r["latest"] = str(s.index[-1]); out.append(r)
    # history of 12m rates for the derived ex-OER series
    exo = remove(p, n, "374", ["160"])
    hist = pd.DataFrame({"core_12m": p["374"].pct_change(12) * 100, "core_ex_oer_12m": exo.pct_change(12) * 100,
                         "core_ex_oer_index": exo, "oer_share_of_core": n["160"] / n["374"] * 100})
    hist.index = hist.index.astype(str)
    hist.to_csv(OUT / f"core_pce_ex_oer_{vintage}.csv")
    res = pd.DataFrame(out).set_index("series")
    res.to_csv(OUT / f"core_pce_ex_oer_summary_{vintage}.csv")
    print(res.round(3).to_string())
    print("OER share of core nominal, latest:", round(n['160'].iloc[-1] / n['374'].iloc[-1] * 100, 2))
    print("2018-19 avg 12m: core", round(hist.loc['2018-01':'2019-12', 'core_12m'].mean(), 2),
          "core ex OER", round(hist.loc['2018-01':'2019-12', 'core_ex_oer_12m'].mean(), 2))
    print(hist.tail(13).round(2).to_string())
