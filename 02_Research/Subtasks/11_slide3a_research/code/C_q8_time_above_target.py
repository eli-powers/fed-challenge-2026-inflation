"""Q8: time above 2% (PCE, core PCE, CPI, core CPI) and the 2020-26 FOMC policy timeline.
Run from project root: python3 -I 02_Research/Subtasks/11_slide3a_research/code/C_q8_time_above_target.py
"""
import importlib.util, glob, html, re, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
spec = importlib.util.spec_from_file_location("C_common", Path.cwd() / "02_Research/Subtasks/11_slide3a_research/code/C_common.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
P = lambda s: pd.Period(s, "M")
STM = C.ROOT / "03_Data/Raw/S3A_fomc_statements_2026-11-15"

# ======================= Part 1: time above target =======================
ser = {}
for key, sid in [("pce", "PCEPI"), ("core_pce", "PCEPILFE"), ("cpi", "CPIAUCNS"), ("core_cpi", "CPILFENS")]:
    s = C.monthly_period(C.fred(sid)); ser[key] = C.pct(s, 12)
    ser[key].attrs["file"] = s.attrs.get("file")
est = pd.read_csv(C.ROOT / "02_Research/Subtasks/04_oct_pce_build/outputs/D_build_2026-10_summary.csv")
oct_est = {"core_pce": float(est[est.measure == "core"].rate_12m.iloc[0]), "pce": float(est[est.measure == "headline"].rate_12m.iloc[0])}
OCT = P("2026-10")
df = pd.DataFrame({"pce_12m": ser["pce"], "core_12m": ser["core_pce"], "cpi_12m": ser["cpi"], "core_cpi_12m": ser["core_cpi"]})
df = df[df.index >= P("2019-01")]
df.loc[OCT, "pce_12m"] = oct_est["pce"]; df.loc[OCT, "core_12m"] = oct_est["core_pce"]
df["pce_status"] = np.where(df.index == OCT, "est. (Oct PCE not released; due 2026-11-25)", "actual")
df["cpi_status"] = "actual (Oct CPI released 2026-11-10)"
for c in ["pce_12m", "core_12m", "cpi_12m", "core_cpi_12m"]:
    df[c.replace("_12m", "") + "_above2_raw"] = df[c] > 2.0
    df[c.replace("_12m", "") + "_above2_rounded1dp"] = df[c].round(1) > 2.0
out = df.copy(); out.index = out.index.astype(str); out.index.name = "month"
out.round(4).to_csv(C.OUTD / "C_q8_time_above_target.csv")

LAST = P("2026-09")
summ = []
for c, nm, sid, srcf in [("pce_12m", "Headline PCE (PCEPI)", "PCEPI", "FRED_PCEPI_2026-11-15.json (vintage 2026-10-29)"),
                         ("core_12m", "Core PCE (PCEPILFE)", "PCEPILFE", "FRED_PCEPILFE_2026-11-15.json (vintage 2026-10-29)"),
                         ("cpi_12m", "Headline CPI-U NSA (CPIAUCNS)", "CPIAUCNS", "FRED_CPIAUCNS_2026-11-15.json"),
                         ("core_cpi_12m", "Core CPI NSA (CPILFENS)", "CPILFENS", "FRED_CPILFENS_2026-11-15.json")]:
    s = df[c]                      # keeps NaN months (CPI Oct 2025 not collected -> y/y missing for Oct 2025 and Oct 2026)
    for thr_name, x in [("raw > 2.0", s), ("rounded to 1dp > 2.0", s.round(1))]:
        flag = x > 2.0; miss = s.isna()
        run = 0; p_ = LAST
        while p_ in s.index and (flag[p_] or miss[p_]):
            run += 1; p_ -= 1
        run_start = LAST - run + 1; last_below = LAST - run
        n_obs_run = int((~miss[run_start:LAST]).sum()); missing_months = [str(k) for k in s[run_start:LAST].index if miss[k]]
        below = [(str(k), round(float(s[k]), 3)) for k in s.index if k >= P("2021-01") and k <= LAST and (not miss[k]) and (not flag[k])]
        first_above_2021 = next((str(k) for k in s.index if k >= P("2021-01") and flag[k]), "n/a")
        oct_flag = bool(flag.get(OCT, False)); oct_val = s.get(OCT, np.nan)
        runO = run + (1 if (oct_flag or pd.isna(oct_val)) else 0) if run > 0 else 0
        summ.append(dict(measure=nm, series_id=sid, threshold=thr_name, first_month_above_since_2021=first_above_2021,
                         current_run_start=str(run_start), last_month_at_or_below_2_before_run=str(last_below), value_in_that_month=round(float(s.get(last_below, np.nan)), 3),
                         run_months_through_2026_09=run, run_years_through_2026_09=round(run / 12, 2), observed_months_in_run=n_obs_run, months_missing_in_run="; ".join(missing_months),
                         run_months_through_2026_10=runO, run_years_through_2026_10=round(runO / 12, 2),
                         oct_2026_value=(round(float(oct_val), 3) if not pd.isna(oct_val) else "n/a (Oct 2025 base missing)"), oct_status="est." if ("pce" in c and "cpi" not in c) else "actual",
                         months_at_or_below_2_since_2021_01=len(below), list_of_those_months="; ".join(f"{a}={b}" for a, b in below),
                         month_six_years_reached=str(run_start + 72), months_short_of_72_at_2026_10=72 - runO,
                         min_12m_in_current_run=round(float(s[run_start:LAST].min()), 3), min_month=str(s[run_start:LAST].idxmin()), source_file=srcf))
pd.DataFrame(summ).to_csv(C.OUTD / "C_q8_time_above_summary.csv", index=False)
print(pd.DataFrame(summ)[["measure", "threshold", "first_month_above_since_2021", "current_run_start", "last_month_at_or_below_2_before_run", "value_in_that_month", "run_months_through_2026_09", "observed_months_in_run", "run_years_through_2026_09", "run_years_through_2026_10", "oct_2026_value", "months_at_or_below_2_since_2021_01", "list_of_those_months", "month_six_years_reached", "min_12m_in_current_run", "min_month"]].to_string())

# vintage sensitivity: Mar/Apr 2021 12m PCE inflation as first published vs current vintage
import json
vint = []
for sid, key in [("PCEPI", "pce"), ("PCEPILFE", "core_pce")]:
    for rt in ["2021-05-01", "2021-06-01", "2026-09-29", "current (2026-11-15 fetch)"]:
        f = C.RAWC / (f"ALFRED_{sid}_asof_{rt}.json" if rt[0] == "2" else f"FRED_{sid}_2026-11-15.json")
        o = {pd.Period(a["date"][:7], "M"): float(a["value"]) for a in json.load(open(f))["observations"] if a["value"] != "."}
        for mth in ["2021-02", "2021-03", "2021-04"]:
            if P(mth) in o and (P(mth) - 12) in o:
                vint.append(dict(series=sid, vintage=rt, month=mth, yoy_pct=round((o[P(mth)] / o[P(mth) - 12] - 1) * 100, 3), source_file=C.rel(f)))
pd.DataFrame(vint).to_csv(C.OUTD / "C_q8_vintage_check.csv", index=False)
print(pd.DataFrame(vint).to_string())
# months at/below 2.0 listing for current-run vintage check, 2020-2021
print(df.loc[P("2020-10"):P("2021-06"), ["pce_12m", "core_12m", "cpi_12m", "core_cpi_12m"]].round(3))

# ======================= Part 2: policy timeline =======================
def frac(s):
    s = s.replace("‑", "-").replace("‐", "-").strip()
    m = re.fullmatch(r"(?:(\d+)-)?(\d+)/(\d+)", s)
    if m: return (int(m.group(1)) if m.group(1) else 0) + int(m.group(2)) / int(m.group(3))
    return float(s)

def text(f):
    t = open(f, errors="ignore").read()
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", t); return html.unescape(re.sub(r"\s+", " ", t))

meet = []
for f in sorted(glob.glob(str(STM / "FOMC_statement_*.htm"))):
    d = re.search(r"(\d{8})", f).group(1); t = text(f)
    m = re.search(r"target range for the federal funds rate (?:by (\d+/\d+|\d+) percentage points?,? )?(?:to|at) ([\d‑\-/ ]+?) to ([\d‑\-/ ]+?) percent", t.replace("‑", "-"))
    verb = None
    mm = re.search(r"decided (?:today )?to (raise|lower|maintain|keep)", t); verb = mm.group(1) if mm else None
    if not m:
        continue
    lo, hi = frac(m.group(2).strip()), frac(m.group(3).strip())
    vote = re.search(r"by a (\d+) [–—\-–] (\d+) vote", t)
    against = re.search(r"Voting against[^.]*?(?:\.\s?[A-Z]\.)?[^.]*?\.(?=\s+(?:Implementation|Last Update|Voting|Patrick|For media))", t)
    ag = re.search(r"Voting against (?:this|the monetary policy) action (?:was|were) (.*?)(?: Implementation Note| Last Update| Patrick Harker voted| For media)", t)
    meet.append(dict(statement_date=f"{d[:4]}-{d[4:6]}-{d[6:]}", verb=verb, lower=lo, upper=hi, vote=f"{vote.group(1)}-{vote.group(2)}" if vote else "see statement",
                     dissent=ag.group(1)[:300] if ag else "", url=f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{d}a.htm"))
M = pd.DataFrame(meet)
# Mar 23 2020 / Aug 22 2025 etc. have no rate sentence and are handled separately
M["prev_lower"] = M.lower.shift(1); M["prev_upper"] = M.upper.shift(1)
# prior to Mar 3, 2020: 1.50-1.75 (Board table, Oct 31 2019 level)
M.loc[M.index[0], "prev_lower"] = 1.50; M.loc[M.index[0], "prev_upper"] = 1.75
M["change_bp"] = ((M.upper - M.prev_upper) * 100).round().astype(int)
M["effective_date_candidate"] = pd.to_datetime(M.statement_date) + pd.Timedelta(days=1)
# FRED target (effective dates)
u = C.fred("DFEDTARU").dropna(); l = C.fred("DFEDTARL").dropna()
chg = u[u.diff().fillna(0) != 0]
chg = chg[chg.index >= "2020-01-01"]
fred_chg = pd.DataFrame({"fred_date": chg.index, "fred_upper": chg.values, "fred_lower": l.reindex(chg.index).values})
# Board table (effective dates) from saved page
bt = text(C.RAWC / "FRB_openmarket_2026-11-15.htm")
bt = bt[bt.find("2026 | 2025 |"):bt.find("2015 Date Increase")]
board = []
for ym in re.finditer(r"(20(?:2[0-6]|1[89]))\s+Date Increase Decrease Level \(%\)(.*?)(?=Back to year navigation)", bt):
    yr = ym.group(1)
    for r in re.finditer(r"([A-Z][a-z]+) (\d{1,2}) (?:\* )?(\d+) (\d+) ([\d.]+-[\d.]+)", ym.group(2)):
        board.append(dict(board_effective_date=pd.to_datetime(f"{r.group(1)} {r.group(2)} {yr}"), board_inc=int(r.group(3)), board_dec=int(r.group(4)), board_level=r.group(5)))
B = pd.DataFrame(board); B = B[B.board_effective_date >= "2020-01-01"]
rows = []
chg_m = M[(M.change_bp != 0) & (M.statement_date >= "2020-03-01")].copy()
for r in chg_m.itertuples():
    eff = pd.Timestamp(r.effective_date_candidate)
    fm = fred_chg[(fred_chg.fred_date >= pd.Timestamp(r.statement_date)) & (fred_chg.fred_date <= pd.Timestamp(r.statement_date) + pd.Timedelta(days=4))]
    bm = B[(B.board_effective_date >= pd.Timestamp(r.statement_date)) & (B.board_effective_date <= pd.Timestamp(r.statement_date) + pd.Timedelta(days=4))]
    fred_ok = (len(fm) == 1 and abs(fm.fred_upper.iloc[0] - r.upper) < 1e-9 and abs(fm.fred_lower.iloc[0] - r.lower) < 1e-9)
    board_level = bm.board_level.iloc[0] if len(bm) else ""
    board_ok = board_level == f"{r.lower:.2f}-{r.upper:.2f}".replace("0.00-", "0-") or board_level.replace("0-0.25", "0-0.25") == f"{r.lower:.2f}-{r.upper:.2f}"
    rows.append(dict(date=r.statement_date, effective_date=fm.fred_date.iloc[0].strftime("%Y-%m-%d") if len(fm) else "", action=("Cut" if r.change_bp < 0 else "Hike") + f" {abs(r.change_bp)} bp" + (" (inter-meeting)" if r.statement_date in ("2020-03-03", "2020-03-15") else ""),
                     change_bp=r.change_bp, lower=r.lower, upper=r.upper, vote=r.vote, dissent=r.dissent, source_url=r.url,
                     fred_dfedtaru_dfedtarl_match=bool(fred_ok), board_openmarket_level=board_level, board_level_match=bool(board_ok), board_effective_date=bm.board_effective_date.iloc[0].strftime("%Y-%m-%d") if len(bm) else ""))
T = pd.DataFrame(rows)
T["cumulative_change_bp_since_2020-03-03"] = T.change_bp.cumsum()
# balance sheet rows (dates and wording verified in saved statements; see notes)
bs = [
 ("2020-03-15", "QE restart: Treasury purchases of at least $500bn and agency MBS of at least $200bn 'over coming months'", "monetary20200315a.htm"),
 ("2020-03-23", "QE uncapped: purchase Treasuries and agency MBS 'in the amounts needed to support smooth market functioning' (adds agency CMBS)", "monetary20200323a.htm"),
 ("2020-12-16", "QE guidance: at least $80bn/month Treasuries and $40bn/month agency MBS until 'substantial further progress'", "monetary20201216a.htm"),
 ("2021-11-03", "Taper announced: net purchases cut by $10bn Treasuries and $5bn MBS from mid-Nov, further cut from Dec", "monetary20211103a.htm"),
 ("2021-12-15", "Taper doubled: cut by $20bn Treasuries and $10bn MBS; Jan pace $40bn/$20bn", "monetary20211215a.htm"),
 ("2022-01-26", "Net asset purchases to end 'in early March' 2022 (Feb pace $20bn/$10bn)", "monetary20220126a.htm"),
 ("2022-03-16", "Statement says Committee 'expects to begin reducing its holdings ... at a coming meeting' (no purchase language; net purchases had been scheduled to end early March per Jan 26 statement)", "monetary20220316a.htm"),
 ("2022-05-04", "QT announced: begin reducing holdings June 1; caps $30bn/month Treasuries, $17.5bn agency, rising to $60bn/$35bn after 3 months (per Plans for Reducing the Size of the Fed's Balance Sheet, monetary20220504b)", "monetary20220504a.htm"),
 ("2025-03-19", "QT slowed from April 1: Treasury redemption cap cut from $25bn to $5bn/month; agency cap stays $35bn", "monetary20250319a.htm"),
 ("2025-10-29", "QT to end: Committee 'decided to conclude the reduction of its aggregate securities holdings on December 1' (2025)", "monetary20251029a.htm"),
 ("2025-12-10", "Reserve management: 'initiate purchases of shorter-term Treasury securities as needed to maintain an ample supply of reserves'", "monetary20251210a.htm"),
]
for d, a, u_ in bs:
    T = pd.concat([T, pd.DataFrame([dict(date=d, effective_date="", action="Balance sheet: " + a, change_bp=np.nan, lower=np.nan, upper=np.nan, vote="", dissent="",
                                         source_url="https://www.federalreserve.gov/newsevents/pressreleases/" + u_)])], ignore_index=True)
last = M.iloc[-1]
T = pd.concat([T, pd.DataFrame([dict(date=last.statement_date, effective_date="", action="Hold (latest meeting)", change_bp=0, lower=last.lower, upper=last.upper, vote=last.vote, dissent=last.dissent, source_url=last.url)])], ignore_index=True)
T = T.sort_values("date").reset_index(drop=True)
T.to_csv(C.OUTD / "C_q8_policy_timeline.csv", index=False)
M[M.statement_date >= "2020-03-01"].drop(columns=["prev_lower", "prev_upper", "effective_date_candidate"]).to_csv(C.OUTD / "C_q8_fomc_meetings_all.csv", index=False)
print(T[["date", "effective_date", "action", "change_bp", "lower", "upper", "vote", "fred_dfedtaru_dfedtarl_match", "board_level_match"]].to_string())
print("rate changes:", int((T.change_bp.fillna(0) != 0).sum()), "net bp:", T.change_bp.fillna(0).sum())
print(M[M.dissent != ""][["statement_date", "vote", "dissent"]].tail(6).to_string())
print("FRED changes unmatched:", [str(x.date()) for x in fred_chg.fred_date if not any(abs((x - pd.Timestamp(d)).days) <= 4 for d in chg_m.statement_date)])
print("Board changes unmatched:", [str(x.date()) for x in B.board_effective_date if not any(abs((x - pd.Timestamp(d)).days) <= 4 for d in chg_m.statement_date)])
