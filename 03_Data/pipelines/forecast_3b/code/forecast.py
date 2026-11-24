"""forecast.py: slide-3B core PCE scenario grid (oil path x pass-through regime) on an SPF baseline.

Run from the project root:
    python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py                 # latest SPF survey in the latest raw folder
    python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --spf 2026Q3    # pick the SPF vintage
    python3 -I 03_Data/pipelines/forecast_3b/code/forecast.py --compare       # also write vintage_compare.csv
Options: --raw <folder name under raw/> (default: latest dated folder).

Method (locked by Eli, Nov 14; every step labelled in the outputs):
  1. Baseline = SPF median core PCE path (q/q annualized, SA) for the chosen survey; quarters that are
     already actual in the core PCE index (FRED PCEPILFE) are replaced by the actual. A missing 2027Q4
     (Q3 survey) is derived from the 2027 Q4/Q4 median.
  2. Oil gap g_s = 100*ln(Brent_scenario_s / Brent_assumed_s) for s from the survey quarter to 2027Q4.
     Assumed path = EIA STEO vintage released on/before the SPF deadline (proxy; SPF publishes none).
  3. Core price-level adjustment L_t = sum_{s<=t} R_{t-s} * (g_s - g_{s-1}) / 10, R_k = the oil note's
     cumulative level response to a permanent 10% oil rise (Fig. 2 table), by regime.
  4. Scenario q/q ann. for a forecast quarter: (1 + s_t/100) = (1 + b_t/100) * exp(4*(L_t - L_{t-1})/100).
     Actual quarters are not adjusted (their oil effect, if any, is already in the data).
  5. Q4/Q4 = built from the quarterly path (actual quarters + scenario quarters); the SPF's own published
     annual Q4/Q4 median is shown alongside for comparison.
Scenarios, not probabilities: no weighting unless Eli sets REGIME_WEIGHT_POST below.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parsers as P  # noqa: E402

# ---------------------------------------------------------------------------------------------------
REGIME_WEIGHT_POST = None  # Eli's input after slide 3A; None = no weighting
# If set to a number w in [0, 1], an extra regime row "weighted_post_w" is produced with
# L = w * L_post + (1 - w) * L_pre for each oil path. Leave None: scenarios are shown as equals.
# ---------------------------------------------------------------------------------------------------

PIPE = Path(__file__).resolve().parents[1]
ROOT = PIPE.parents[2]
SHOW_START, END = "2026Q1", "2027Q4"
CENTRAL_REGIMES = ["pre", "post"]
BACKUP_REGIMES = ["persistence_only"]
REGIME_LABEL = {"pre": "pre-pandemic",
                "post": "post-pandemic (stronger persistence and pass-through)",
                "persistence_only": "post-pandemic persistence only (backup)"}


# =================================================================================== core math
def level_adjustment(gaps: list[float], R: list[float]) -> list[float]:
    """L_t = sum_{s<=t} R_{t-s} * dg_s / 10, dg_s = g_s - g_{s-1}, g_{-1} = 0. R held at R_K beyond K."""
    K = len(R) - 1
    dg = [gaps[0]] + [gaps[s] - gaps[s - 1] for s in range(1, len(gaps))]
    return [sum(R[min(t - s, K)] * dg[s] / 10.0 for s in range(t + 1)) for t in range(len(gaps))]


def apply_adjustment(baseline_qq: float, dL: float) -> float:
    """Scenario q/q ann. = baseline compounded with the quarterly level change dL (pp, log points).
    Written as b + adj so that dL == 0 returns the baseline bit-for-bit."""
    adj = (100.0 + baseline_qq) * (math.exp(4.0 * dL / 100.0) - 1.0)
    return baseline_qq + adj


def q4q4(path: dict, year: int) -> float:
    """Q4/Q4 % from a dict quarter -> q/q annualized %, using the four quarters of `year`."""
    prod = 1.0
    for q in (1, 2, 3, 4):
        prod *= (1 + path[f"{year}Q{q}"] / 100.0) ** 0.25
    return 100.0 * (prod - 1.0)


# =================================================================================== inputs
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def latest_raw() -> Path:
    ds = sorted(p for p in (PIPE / "raw").iterdir() if p.is_dir() and not p.name.startswith("."))
    if not ds:
        sys.exit("No raw folder. Run code/fetch_inputs.py first.")
    return ds[-1]


class Inputs:
    def __init__(self, raw: Path):
        self.raw, self.used = raw, {}
        self.med = P.read_spf_median(self.f("medianLevel.xlsx"))
        self.disp = P.read_dispersion_d1(self.f("Dispersion_1.xlsx"))
        self.steo_rel = P.parse_steo_release_dates(self.f("page_steo_outlook.html"))
        core = P.load_fred_obs(self.f("PCEPILFE_observations.json"))
        self.core_rt = json.loads(self.f("PCEPILFE_observations.json").read_text()).get("realtime_start")
        self.core_q = P.quarterly_avg(core)
        self.brent = P.read_eia_daily(self.f("EIA_RBRTEd.xls"))
        self.rules = json.loads(self.cfg("oil_path_rules.json").read_text())
        r = pd.read_csv(self.cfg("regime_response.csv"))
        self.R = {g: d.sort_values("k").level_response_pct_per_10pct.tolist() for g, d in r.groupby("regime")}
        self._steo = {}

    def f(self, name) -> Path:
        p = self.raw / name
        if not p.exists():
            sys.exit(f"Missing raw input {p}. Rerun fetch_inputs.py.")
        self.used[rel(p)] = sha(p)
        return p

    def cfg(self, name) -> Path:
        p = PIPE / "config" / name
        self.used[rel(p)] = sha(p)
        return p

    def steo(self, v):
        if v not in self._steo:
            p = self.f(f"{v}_base.xlsx")
            m = P.read_steo_series(p)
            self._steo[v] = (m, P.steo_quarterly(m), P.read_steo_meta(p))
        return self._steo[v]


# =================================================================================== baseline
def build_baseline(I: Inputs, spf: str):
    row = P.median_row(I.med, spf)
    hm = P.horizon_map(spf)
    spf_q = {hm[v]: float(row[v]) for v in P.SPF_Q_VARS if not np.isnan(row[v])}
    spf_src = {q: "SPF median, published" for q in spf_q}
    spf_a = {hm[v]: float(row[v]) for v in P.SPF_A_VARS if not np.isnan(row[v])}
    # derive a missing Q4 of a year from that year's Q4/Q4 median if Q1-Q3 are all present
    for y, a in spf_a.items():
        qs = [f"{y}Q{k}" for k in (1, 2, 3)]
        if f"{y}Q4" not in spf_q and all(q in spf_q for q in qs) and P.qidx(f"{y}Q4") <= P.qidx(END):
            spf_q[f"{y}Q4"] = float(P.derive_q4_from_annual(*[spf_q[q] for q in qs], a))
            spf_src[f"{y}Q4"] = f"derived from SPF {y} Q4/Q4 median {a:.4f} and SPF {y}Q1-Q3 (not published)"
    act = ((I.core_q / I.core_q.shift(1)) ** 4 - 1) * 100
    last_actual = act.dropna().index[-1]
    survey_q = hm["COREPCE2"]
    quarters = P.qrange(SHOW_START, END)
    base, status, src = {}, {}, {}
    for q in quarters:
        if P.qidx(q) <= P.qidx(last_actual):
            base[q], status[q], src[q] = float(act[q]), "actual", f"actual, FRED PCEPILFE realtime {I.core_rt}"
        elif q in spf_q:
            base[q], status[q], src[q] = spf_q[q], "forecast", spf_src[q]
        else:
            sys.exit(f"SPF {spf} has no forecast for {q}; cannot build the baseline through {END}.")
    # 2025 quarters for Q4/Q4 of 2026 (actual)
    for q in P.qrange("2025Q1", "2025Q4"):
        base[q], status[q] = float(act[q]), "actual"
    deadline = P.parse_release_dates(I.f("spf-release-dates.txt"), spf)
    if deadline is None:
        sys.exit(f"SPF {spf}: deadline not found in spf-release-dates.txt")
    disp = I.disp.get(spf, {})
    iqr = {P.qlabel(P.qidx(survey_q) + k): v for k, v in disp.items()}
    return dict(spf=spf, base=base, status=status, src=src, spf_q=spf_q, spf_src=spf_src, spf_a=spf_a,
                survey_q=survey_q, last_actual=last_actual, deadline=deadline[0], release=deadline[1], iqr=iqr)


# =================================================================================== oil
def us_holidays_dropped(d: pd.Timestamp) -> bool:
    """EIA Brent series gaps assumed on Dec 25, Jan 1 and U.S. Thanksgiving (Agent B's convention)."""
    if (d.month, d.day) in ((12, 25), (1, 1)):
        return True
    return d.month == 11 and d.weekday() == 3 and 22 <= d.day <= 28


def brent_paths(I: Inputs, need_quarters: list[str]):
    s = I.brent
    last = s.index[-1]
    lastq = P.quarter_of(last)
    qmean = s.groupby([P.quarter_of(d) for d in s.index]).mean()
    obs_cur = s[[P.quarter_of(d) == lastq for d in s.index]]
    qend = (pd.Period(lastq, "Q").end_time).normalize()
    rem = [d for d in pd.bdate_range(last + pd.Timedelta(days=1), qend) if not us_holidays_dropped(d)]
    rem_m = pd.Series([d.strftime("%Y-%m") for d in rem]).value_counts().to_dict() if rem else {}
    n_obs, n_rem = len(obs_cur), len(rem)
    latest = P.latest_steo(I.steo_rel)
    out, meta = {}, {"last_brent_date": str(last.date()), "last_brent_usd": float(s.iloc[-1]),
                     "splice_quarter": lastq, "n_observed_days": n_obs, "n_remaining_weekdays": n_rem,
                     "remaining_by_month": rem_m, "weight_observed": n_obs / (n_obs + n_rem) if n_rem else 1.0,
                     "latest_steo": latest}

    def splice(monthly_rule):
        return (obs_cur.sum() + sum(monthly_rule(m) * n for m, n in rem_m.items())) / (n_obs + n_rem)

    for v in I.rules["variants"]:
        t = v["type"]
        if t == "steo_latest":
            m, qv, _ = I.steo(latest)
            mr = lambda mm, m=m: float(m[pd.Timestamp(mm + "-01")])
            fq = lambda q, qv=qv: float(qv[q])
            src = f"EIA STEO {latest} BREPUUS"
        elif t == "futures_curve":
            fc = pd.read_csv(I.cfg(Path(v["file"]).name))
            front = float(fc[fc.contract_month.isna()].close.iloc[0])
            fc = fc.dropna(subset=["contract_month"])
            fcq = fc.assign(q=fc.contract_month.map(lambda x: P.quarter_of(x + "-01"))).groupby("q").close.mean()
            mr = lambda mm, front=front: front
            fq = lambda q, fcq=fcq: float(fcq[q])
            src = v["source"]
        elif t == "flat":
            mr = lambda mm, u=v["usd"]: u
            fq = lambda q, u=v["usd"]: u
            src = v["source"]
        elif t == "flat_month_mean":
            u = float(s[[d.strftime("%Y-%m") == v["month"] for d in s.index]].mean())
            mr = lambda mm, u=u: u
            fq = lambda q, u=u: u
            src = f"{v['source']} = ${u:.2f}"
        elif t == "steo_plus":
            m, qv, _ = I.steo(v["vintage"])
            mr = lambda mm, m=m, p=v["premium"]: float(m[pd.Timestamp(mm + "-01")]) + p
            fq = lambda q, qv=qv, p=v["premium"]: float(qv[q]) + p
            src = v["source"]
        elif t == "spot_mean_plus":
            u = float(s.loc[v["start"]:v["end"]].mean()) + v["premium"]
            mr = lambda mm, u=u: u
            fq = lambda q, u=u: u
            src = f"{v['source']} = ${u:.2f}"
        else:
            raise ValueError(t)
        path, kind = {}, {}
        for q in need_quarters:
            if P.qidx(q) < P.qidx(lastq):
                path[q], kind[q] = float(qmean[q]), "actual (EIA RBRTE quarterly mean of trading days)"
            elif q == lastq:
                path[q] = float(splice(mr)) if n_rem else float(qmean[q])
                kind[q] = f"splice: {n_obs} observed days to {last.date()} + {n_rem} remaining weekdays at rule"
            else:
                path[q], kind[q] = fq(q), "rule/forecast"
        out[v["variant_id"]] = dict(path=path, kind=kind, src=src, **{k: v[k] for k in ("path_id", "central", "label")})
    return out, meta


def assumption_paths(I: Inputs, B: dict, quarters: list[str]):
    """Central proxy = STEO released on/before the SPF deadline; sensitivity = previous STEO; futures hybrid."""
    matched, prev = P.steo_vintage_for(B["deadline"], I.steo_rel)
    out = {}
    _, qv, meta = I.steo(matched)
    out["steo_matched"] = dict(vintage=matched, central=True, path={q: float(qv[q]) for q in quarters},
                               label=f"EIA STEO {matched} (released {I.steo_rel[matched]}, completed {meta.get('completed')}); "
                                     f"latest STEO released on/before SPF deadline {B['deadline']}")
    if prev:
        try:
            _, qp, mp = I.steo(prev)
            out["steo_previous"] = dict(vintage=prev, central=False, path={q: float(qp[q]) for q in quarters},
                                        label=f"EIA STEO {prev} (released {I.steo_rel[prev]}); one vintage earlier")
        except SystemExit:
            print(f"  note: {prev}_base.xlsx not in raw folder; previous-STEO sensitivity skipped")
    fpath = PIPE / "config" / f"assumption_futures_{B['spf']}.csv"
    if fpath.exists():
        fa = pd.read_csv(I.cfg(fpath.name)).set_index("quarter").brent_usd
        hyb = {q: (float(fa[q]) if q in fa.index else float(qv[q])) for q in quarters}
        out["futures_hybrid"] = dict(vintage="NYMEX BZ closes at deadline [2] + matched STEO where no contract",
                                     central=False, path=hyb,
                                     label=f"Brent futures on {B['deadline']} for {', '.join(q for q in quarters if q in fa.index)} "
                                           f"(Yahoo [2]); matched STEO for {', '.join(q for q in quarters if q not in fa.index)}")
    else:
        print(f"  note: no config/assumption_futures_{B['spf']}.csv; futures-proxy sensitivity skipped")
    return out


# =================================================================================== grid
def run_cell(B, oil_path, assumed, R, gap_quarters):
    gaps = [100.0 * math.log(oil_path[q] / assumed[q]) for q in gap_quarters]
    L = level_adjustment(gaps, R)
    Ld = dict(zip(gap_quarters, L))
    return gaps, Ld


def cell_rows(B, I, spf, vid, V, regime, Ld, gaps, assumed, proxy_id, weighted=False):
    gap_q = list(Ld)
    gd = dict(zip(gap_q, gaps))
    scen, rows = dict(B["base"]), []
    prevL = 0.0
    for q in P.qrange(SHOW_START, END):
        L = Ld.get(q)
        dL = (L - prevL) if L is not None else None
        if L is not None:
            prevL = L
        b = B["base"][q]
        if B["status"][q] == "forecast" and dL is not None:
            s = apply_adjustment(b, dL)
            adj = s - b
        else:
            s, adj = b, (np.nan if B["status"][q] == "actual" else 0.0)
        scen[q] = s
        rows.append(dict(spf_vintage=spf, oil_path=V["path_id"], oil_variant=vid, is_central=bool(V["central"]) and regime in CENTRAL_REGIMES and proxy_id == "steo_matched",
                         regime=regime, assumption_proxy=proxy_id, horizon="qq_ann", quarter=q, status=B["status"][q],
                         brent_usd=V["path"].get(q), assumed_brent_usd=assumed.get(q) if q in gd else np.nan,
                         baseline_qq_ann=b, spf_median_qq_ann=B["spf_q"].get(q, np.nan),
                         oil_gap_pct=gd.get(q, np.nan),
                         oil_gap_simple_pct=(100 * (V["path"][q] / assumed[q] - 1)) if q in gd else np.nan,
                         level_adj_pct=L if L is not None else np.nan,
                         adj_qq_ann_pp=adj, scenario_qq_ann=s, spf_published_q4q4=np.nan))
    for y in (2026, 2027):
        bq, sq = q4q4(B["base"], y), q4q4(scen, y)
        Lq4 = Ld.get(f"{y}Q4", np.nan)
        Lq4p = Ld.get(f"{y - 1}Q4", 0.0)
        rows.append(dict(spf_vintage=spf, oil_path=V["path_id"], oil_variant=vid, is_central=rows[0]["is_central"], regime=regime,
                         assumption_proxy=proxy_id, horizon="q4q4", quarter=f"{y}Q4/{y - 1}Q4", status="built from quarterly path",
                         brent_usd=np.nan, assumed_brent_usd=np.nan, baseline_qq_ann=bq, spf_median_qq_ann=np.nan,
                         oil_gap_pct=np.nan, oil_gap_simple_pct=np.nan, level_adj_pct=Lq4 - Lq4p,
                         adj_qq_ann_pp=sq - bq, scenario_qq_ann=sq, spf_published_q4q4=B["spf_a"].get(y, np.nan)))
    return rows


def build_grid(I, B, oils, assum):
    gap_quarters = P.qrange(B["survey_q"], END)
    regimes = CENTRAL_REGIMES + BACKUP_REGIMES
    grid, sens = [], []
    for pid, A in assum.items():
        for vid, V in oils.items():
            if not A["central"] and not V["central"]:
                continue  # proxy sensitivity only on the central oil paths
            Ls = {}
            for g in regimes:
                gaps, Ld = run_cell(B, V["path"], A["path"], I.R[g], gap_quarters)
                Ls[g] = Ld
                rows = cell_rows(B, I, B["spf"], vid, V, g, Ld, gaps, A["path"], pid)
                (grid if A["central"] else sens).extend(rows)
            if REGIME_WEIGHT_POST is not None and A["central"]:
                w = float(REGIME_WEIGHT_POST)
                assert 0 <= w <= 1, "REGIME_WEIGHT_POST must be in [0, 1]"
                Lw = {q: w * Ls["post"][q] + (1 - w) * Ls["pre"][q] for q in gap_quarters}
                grid.extend(cell_rows(B, I, B["spf"], vid, V, f"weighted_post_{w:g}", Lw, gaps, A["path"], pid))
    return pd.DataFrame(grid), pd.DataFrame(sens)


def build_fan(B, grid):
    c = grid[grid.is_central]
    rows = []
    for (h, q), d in c.groupby(["horizon", "quarter"], sort=False):
        iqr = B["iqr"].get(q) if h == "qq_ann" else None
        is_act = d.status.iloc[0] == "actual"
        rows.append(dict(spf_vintage=B["spf"], horizon=h, quarter=q, status=d.status.iloc[0],
                         baseline=d.baseline_qq_ann.iloc[0],
                         scenario_range_min=d.scenario_qq_ann.min(), scenario_range_max=d.scenario_qq_ann.max(),
                         cell_at_min="actual (all cells equal)" if is_act else f"{d.loc[d.scenario_qq_ann.idxmin(), 'oil_variant']} x {d.loc[d.scenario_qq_ann.idxmin(), 'regime']}",
                         cell_at_max="actual (all cells equal)" if is_act else f"{d.loc[d.scenario_qq_ann.idxmax(), 'oil_variant']} x {d.loc[d.scenario_qq_ann.idxmax(), 'regime']}",
                         n_cells=len(d),
                         spf_p25=iqr[0] if iqr else np.nan, spf_p75=iqr[1] if iqr else np.nan,
                         spf_iqr_note=(("SPF published P25/P75 (Dispersion_1.xlsx), survey " + B["spf"]) +
                                       ("; quarter now actual, IQR shown for reference" if is_act else "")) if iqr else
                         ("not published for this horizon" if not is_act else "actual quarter"),
                         label="SCENARIO RANGE across the 6 central cells (min/max), NOT a probability fan"))
    return pd.DataFrame(rows)


# =================================================================================== main
def run(I: Inputs, spf: str, write=True):
    B = build_baseline(I, spf)
    oil_q = P.qrange("2025Q1", END)
    oils, ometa = brent_paths(I, oil_q)
    assum = assumption_paths(I, B, P.qrange(B["survey_q"], END))
    grid, sens = build_grid(I, B, oils, assum)
    fan = build_fan(B, grid)
    if write:
        out = PIPE / "processed"
        out.mkdir(exist_ok=True)
        grid.to_csv(out / f"scenario_grid_{spf}.csv", index=False, float_format="%.6f")
        sens.to_csv(out / f"sensitivity_proxy_{spf}.csv", index=False, float_format="%.6f")
        fan.to_csv(out / f"fan_{spf}.csv", index=False, float_format="%.6f")
        paths = pd.DataFrame([dict(oil_variant=k, oil_path=v["path_id"], is_central=v["central"], label=v["label"], source=v["src"],
                                   quarter=q, brent_usd=v["path"][q], kind=v["kind"][q]) for k, v in oils.items() for q in oil_q])
        paths.to_csv(out / f"oil_paths_{spf}.csv", index=False, float_format="%.4f")
        pd.DataFrame([dict(proxy=k, central=a["central"], vintage=a["vintage"], label=a["label"], quarter=q, assumed_brent_usd=x)
                      for k, a in assum.items() for q, x in a["path"].items()]).to_csv(out / f"oil_assumption_{spf}.csv", index=False, float_format="%.4f")
        meta = dict(
            run_timestamp=dt.datetime.now().isoformat(timespec="seconds"), script="03_Data/pipelines/forecast_3b/code/forecast.py",
            raw_folder=rel(I.raw), spf_vintage=spf, spf_deadline=B["deadline"], spf_release=B["release"],
            survey_quarter=B["survey_q"], last_actual_quarter=B["last_actual"], core_pce_vintage=f"FRED PCEPILFE realtime {I.core_rt}",
            baseline_sources={q: B["src"][q] for q in P.qrange(SHOW_START, END)},
            spf_published_q4q4=B["spf_a"], assumption_proxies={k: a["label"] for k, a in assum.items()},
            oil=ometa, regimes=REGIME_LABEL, central_regimes=CENTRAL_REGIMES, backup_regimes=BACKUP_REGIMES,
            REGIME_WEIGHT_POST=REGIME_WEIGHT_POST,
            parameters=dict(gap="100*ln(scenario/assumed), from survey quarter", response="cumulative level % per permanent 10% oil rise, held at k=12 beyond",
                            compounding="(1+s/100)=(1+b/100)*exp(4*dL/100)", actual_quarters="not adjusted",
                            q4q4="product of quarterly path incl. actual quarters"),
            inputs=I.used,
            outputs=[f"processed/{n}" for n in (f"scenario_grid_{spf}.csv", f"fan_{spf}.csv", f"sensitivity_proxy_{spf}.csv",
                                                 f"oil_paths_{spf}.csv", f"oil_assumption_{spf}.csv")],
            caveats=["Oil note = five-economy panel average (not U.S.-specific); authors treat the post-pandemic projection as an upper bound.",
                     "The SPF publishes no oil assumption; the STEO vintage is a proxy.",
                     "Scenarios, not probabilities; the scenario range is not a probability fan.",
                     "The note is not evidence of changed price-setting behaviour."])
        (out / f"metadata_{spf}.json").write_text(json.dumps(meta, indent=1, default=str))
    return B, grid, fan, sens


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--spf", help="SPF survey, e.g. 2026Q3 (default: latest in the raw SPF file)")
    ap.add_argument("--raw", help="raw folder name under raw/ (default: latest)")
    ap.add_argument("--compare", action="store_true", help="also run the previous survey and write vintage_compare.csv")
    a = ap.parse_args()
    raw = PIPE / "raw" / a.raw if a.raw else latest_raw()
    I = Inputs(raw)
    present = P.surveys_present(I.med)
    spf = a.spf or present[-1]
    if spf not in present:
        sys.exit(f"SPF {spf} not in {raw.name}/medianLevel.xlsx (latest present: {present[-1]}). Run fetch_inputs.py.")
    print(f"raw={raw.name}  spf={spf}  REGIME_WEIGHT_POST={REGIME_WEIGHT_POST}")
    B, grid, fan, _ = run(I, spf)
    c = grid[grid.is_central]
    show = c[(c.quarter.isin(["2026Q4", "2027Q4", "2026Q4/2025Q4", "2027Q4/2026Q4"]))]
    print(show.pivot_table(index=["oil_variant", "regime"], columns="quarter", values="scenario_qq_ann").round(2).to_string())
    print(f"wrote processed/scenario_grid_{spf}.csv, fan_{spf}.csv, metadata_{spf}.json")
    if a.compare:
        others = [s for s in ("2026Q3", "2026Q4") if s in present and s != spf]
        if not others:
            sys.exit("--compare needs both the 2026Q3 and 2026Q4 surveys in the raw SPF file; only "
                     f"{[s for s in ('2026Q3', '2026Q4') if s in present]} present.")
        frames = [grid] + [run(I, s)[1] for s in others]
        write_compare(frames)
        print("wrote processed/vintage_compare.csv")


def write_compare(frames, path=None):
    """Side-by-side central cells (baseline, adjustment, scenario) for each SPF vintage, plus later-minus-earlier."""
    allg = pd.concat(frames)
    allg = allg[allg.is_central]
    key = ["oil_variant", "regime", "horizon", "quarter"]
    vals = ["baseline_qq_ann", "adj_qq_ann_pp", "scenario_qq_ann"]
    wide = allg.pivot_table(index=key, columns="spf_vintage", values=vals, dropna=False)
    vs = sorted(allg.spf_vintage.unique())
    wide.columns = [f"{v}_{s}" for v, s in wide.columns]
    wide = wide.reset_index()
    for v in vals:
        wide[f"{v}_{vs[-1]}_minus_{vs[0]}"] = wide[f"{v}_{vs[-1]}"] - wide[f"{v}_{vs[0]}"]
    wide.to_csv(path or PIPE / "processed" / "vintage_compare.csv", index=False, float_format="%.6f")
    return wide


if __name__ == "__main__":
    main()
