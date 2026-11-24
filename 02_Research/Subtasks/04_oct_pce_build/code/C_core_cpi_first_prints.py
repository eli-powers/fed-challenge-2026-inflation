"""C_core_cpi_first_prints.py: first-print and current-vintage m/m for CPILFESL (core CPI, SA) from ALFRED vintages.
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_core_cpi_first_prints.py"""
import csv, sys, calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
sys.path.insert(0, "02_Research/Subtasks/04_oct_pce_build/code")
from C_alfred_lib import *
OUT = "02_Research/Subtasks/04_oct_pce_build/outputs/"
obs = load("03_Data/Raw/ALFRED_CPILFESL_all_vintages_2026-11-11.json")
def r1(x): return float(Decimal(repr(x)).quantize(Decimal("0.1"), ROUND_HALF_UP))
fr = {m: first_release(obs, m) for m in obs}
# vintage when a '.' (missing) first appeared, to document Oct 2025
months = [m for m in sorted(obs) if m >= "2017-02"]
rows = []
for mm in months:
    v = fr[mm]; flags = []
    if v is None:
        # never published (Oct 2025)
        miss = [rs for rs, re_, val in obs[mm]]
        rows.append(dict(series_id="CPILFESL", ref_month=mm, in_pce_backtest_window=("2024-01" <= mm <= "2026-10"),
            first_release_vintage="", level_first_print="", level_prior_month_same_vintage="", mm_first_print_pct="", mm_first_print_1dp="",
            mm_current_vintage_pct="", revision_cur_minus_first_pp="", yy_first_print_pct="",
            flag=f"NOT PUBLISHED: ALFRED shows '.' (missing) from vintage {min(miss)} to present"))
        continue
    L = level_asof(obs, mm, v); Lp = level_asof(obs, add_months(mm, -1), v); Ly = level_asof(obs, add_months(mm, -12), v)
    cur = level_asof(obs, mm, CURRENT); curp = level_asof(obs, add_months(mm, -1), CURRENT)
    mfp = (L/Lp-1)*100 if Lp else None
    mcur = (cur/curp-1)*100 if (cur and curp) else None
    yy = (L/Ly-1)*100 if Ly else None
    if Lp is None: flags.append(f"first-print m/m not computable: {add_months(mm,-1)} level missing in that vintage")
    if mcur is None: flags.append(f"current-vintage m/m not computable: {add_months(mm,-1)} level missing")
    y, mo = int(mm[:4]), int(mm[5:]); me = date(y, mo, calendar.monthrange(y, mo)[1])
    lag = (v-me).days
    if lag > 25: flags.append(f"late release (lag {lag}d from month-end; typical ~10-20d)")
    f = lambda x, p=4: "" if x is None else f"{x:.{p}f}"
    rows.append(dict(series_id="CPILFESL", ref_month=mm, in_pce_backtest_window=("2024-01" <= mm <= "2026-10"),
        first_release_vintage=v.isoformat(), level_first_print=L, level_prior_month_same_vintage=Lp if Lp else "",
        mm_first_print_pct=f(mfp), mm_first_print_1dp="" if mfp is None else f"{r1(mfp):.1f}",
        mm_current_vintage_pct=f(mcur), revision_cur_minus_first_pp="" if (mfp is None or mcur is None) else f"{mcur-mfp:+.4f}",
        yy_first_print_pct=f(yy), flag="; ".join(flags)))
cols = list(rows[0].keys())
with open(OUT+"core_cpi_first_prints.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)
meta = [
 ("series_id", "CPILFESL = CPI-U All items less food and energy, U.S. city average, SA, index 1982-84=100 (BLS series CUSR0000SA0L1E via FRED/ALFRED)"),
 ("seasonal_adjustment", "Seasonally adjusted. NB: BLS revises SA factors each February (Jan CPI release), so within-vintage and current-vintage m/m differ partly for that reason, not only data revision"),
 ("units", "Index level; m/m and y/y in percent, (L_t/L_t-1 - 1)*100 from 3-decimal levels"),
 ("ref_period", "Feb 2017 .. Oct 2026 monthly (Jan 2017 omitted: Dec 2016 not pulled). in_pce_backtest_window = Jan 2024..Oct 2026"),
 ("first_release_vintage", "Earliest ALFRED realtime_start with a non-missing value (ALFRED vintage date treated as BLS release date)"),
 ("first_print_calc", "m/m and y/y use only levels as they stood in that first-release vintage"),
 ("mm_current_vintage", "Both levels as of latest vintage in ALFRED pulled 2026-11-11 (vintage 2026-11-10 contains Oct 2026)"),
 ("raw_file", "03_Data/Raw/ALFRED_CPILFESL_all_vintages_2026-11-11.json (output_type=1)"),
 ("script", "02_Research/Subtasks/04_oct_pce_build/code/C_core_cpi_first_prints.py (+C_alfred_lib.py)"),
]
with open(OUT+"core_cpi_first_prints_meta.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["field", "description"]); w.writerows(meta)
for r in rows:
    if r["ref_month"] >= "2025-07": print(r["ref_month"], r["first_release_vintage"], r["mm_first_print_pct"], r["mm_current_vintage_pct"], r["yy_first_print_pct"], r["flag"])
print("late-flag months:", [r["ref_month"] for r in rows if "late" in r["flag"]])
# raw Oct/Nov 2025 history
for m in ("2025-10", "2025-11"): print(m, [(str(a), str(b), c) for a, b, c in obs[m]])
import collections
print(sorted([(abs(float(r["revision_cur_minus_first_pp"])), r["ref_month"]) for r in rows if r["revision_cur_minus_first_pp"] and r["ref_month"]>="2024-01"])[-6:])
