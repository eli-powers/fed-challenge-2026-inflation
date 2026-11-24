"""Q3 fetch: Brent/WTI daily spot (EIA + FRED), NYMEX WTI futures RCLC1-4 (EIA), STEO vintages (Nov, Aug, Feb 2026),
and the FEDS oil note accessible version. Saves raw files only (never edited) to new 03_Data/Raw/*_2026-11-15/ folders.
Run: python3 -I 02_Research/Subtasks/12_slide3b_research/code/B_q3_fetch.py"""
import sys, json
sys.path.insert(0, "./02_Research/Subtasks/12_slide3b_research/code")
from B_common import *

log = []


def save(folder, name, url, params=None):
    f = RAW / folder
    f.mkdir(parents=True, exist_ok=True)
    if (f / name).exists():  # raw files are never overwritten; delete the folder to refetch
        log.append((folder, name, url, (f / name).stat().st_size, "cached")); return
    try:
        b = http_get(url, params)
        if params:  # API call: redact any key
            b = redact(b.decode("utf-8", "replace")).encode()
        (f / name).write_bytes(b)
        log.append((folder, name, url, len(b), "ok"))
        print("ok", name, len(b))
    except Exception as e:
        log.append((folder, name, url, 0, f"FAIL {e}"))
        print("FAIL", name, url, e)


# 1. Daily spot
D = "EIA_Brent_daily_2026-11-15"
for s in ["RBRTEd", "RWTCd"]:
    save(D, f"EIA_{s}.xls", f"https://www.eia.gov/dnav/pet/hist_xls/{s}.xls")
for s in ["DCOILBRENTEU", "DCOILWTICO"]:
    save(D, f"FRED_{s}_obs.json", "https://api.stlouisfed.org/fred/series/observations",
         {"series_id": s, "api_key": KEYS["FRED_API_KEY"], "file_type": "json", "observation_start": "2024-01-01"})
    save(D, f"FRED_{s}_seriesinfo.json", "https://api.stlouisfed.org/fred/series",
         {"series_id": s, "api_key": KEYS["FRED_API_KEY"], "file_type": "json"})

# 2. NYMEX WTI futures (EIA)
F = "EIA_NYMEX_futures_2026-11-15"
for c in range(1, 5):
    save(F, f"EIA_RCLC{c}d.xls", f"https://www.eia.gov/dnav/pet/hist_xls/RCLC{c}d.xls")
save(F, "EIA_pet_pri_fut_s1_d.htm", "https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm")

# 3. STEO vintages
for vint, folder in [("nov26", "EIA_STEO_Nov2026_2026-11-15"), ("aug26", "EIA_STEO_Aug2026_2026-11-15"),
                     ("feb26", "EIA_STEO_prewar_Jan-Feb2026_2026-11-15"), ("jan26", "EIA_STEO_prewar_Jan-Feb2026_2026-11-15"), ("mar26", "EIA_STEO_prewar_Jan-Feb2026_2026-11-15")]:
    save(folder, f"{vint}_base.xlsx", f"https://www.eia.gov/outlooks/steo/archives/{vint}_base.xlsx")
save("EIA_STEO_Nov2026_2026-11-15", "STEO_m_current.xlsx", "https://www.eia.gov/outlooks/steo/xls/STEO_m.xlsx")
save("EIA_STEO_Nov2026_2026-11-15", "steo_report_global_oil.htm", "https://www.eia.gov/outlooks/steo/report/global_oil.php")
save("EIA_STEO_Nov2026_2026-11-15", "steo_home.htm", "https://www.eia.gov/outlooks/steo/")

# 4. FEDS note accessible version
A = "FEDS_oil_note_accessible_2026-11-15"
save(A, "DeMichelis_oil_core_accessible_20261109.htm",
     "https://www.federalreserve.gov/econres/notes/feds-notes/the-effect-of-oil-prices-on-core-inflation-recent-evidence-from-the-advanced-economies-accessible-20261109.htm")

(RAW / "EIA_Brent_daily_2026-11-15" / "_fetch_log_B.json").write_text(json.dumps(log, indent=1))
