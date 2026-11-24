"""Q8 fetch part 2: BLS Oct 2026 PPI news release (HTML) and daily Brent/WTI (FRED mirror of EIA, plus EIA direct).
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q8_fetch_oil_release.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *

d = RAW / "BLS_PPI_stages_2026-11-15"; d.mkdir(exist_ok=True, parents=True)
o = RAW / "EIA_FRED_oil_daily_2026-11-15"; o.mkdir(exist_ok=True, parents=True)
for name, url in [("bls_ppi_news_release_nr0_2026-11-15.htm", "https://www.bls.gov/news.release/ppi.nr0.htm"),
                  ("bls_ppi_news_release_t05_2026-11-15.htm", "https://www.bls.gov/news.release/ppi.t05.htm"),
                  ("bls_ppi_news_release_t06_2026-11-15.htm", "https://www.bls.gov/news.release/ppi.t06.htm"),
                  ("bls_ppi_news_release_t07_2026-11-15.htm", "https://www.bls.gov/news.release/ppi.t07.htm"),
                  ("bls_ppi_release_schedule_2026-11-15.htm", "https://www.bls.gov/schedule/news_release/ppi.htm")]:
    try:
        (d / name).write_bytes(http_get(url, timeout=60)); print("ok", name)
    except Exception as e:
        print("ERR", name, e)
for sid in ["DCOILBRENTEU", "DCOILWTICO"]:
    raw = http_get("https://api.stlouisfed.org/fred/series/observations",
                   {"series_id": sid, "api_key": KEYS["FRED_API_KEY"], "file_type": "json", "observation_start": "2018-01-01"}).decode()
    (o / f"FRED_{sid}_obs_{TODAY}.json").write_text(redact(raw)); print("ok", sid, len(raw))
    raw = http_get("https://api.stlouisfed.org/fred/series", {"series_id": sid, "api_key": KEYS["FRED_API_KEY"], "file_type": "json"}).decode()
    (o / f"FRED_{sid}_seriesinfo_{TODAY}.json").write_text(redact(raw))
for name, url in [("EIA_RBRTEd_2026-11-15.xls", "https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls"),
                  ("EIA_RWTCd_2026-11-15.xls", "https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls")]:
    try:
        b = http_get(url, timeout=60); (o / name).write_bytes(b); print("ok", name, len(b), b[:8])
    except Exception as e:
        print("ERR", name, e)
