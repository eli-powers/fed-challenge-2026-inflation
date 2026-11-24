"""Q11b fetch: CPI food, transportation services components; PPI diesel/truck (reuse q11 raw), EIA retail diesel, BLS CPI Oct release, BLS CPI motor vehicle insurance info.
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q11b_fetch.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
d = RAW / "CPI_q11b_2026-11-15b"; d.mkdir(exist_ok=True, parents=True)
ids = ["CUSR0000SAF11", "CUUR0000SAF11", "CUSR0000SEFV", "CUSR0000SAF1", "CUSR0000SAS4", "CUSR0000SETA03", "CUSR0000SETA04", "CUSR0000SETD", "CUSR0000SETD01", "CUSR0000SETD02",
       "CUSR0000SETE", "CUUR0000SETE", "CUSR0000SETF", "CUSR0000SETG", "CUSR0000SETG01", "CUSR0000SETG02", "CUSR0000SETG03", "CUSR0000SETA01", "CUSR0000SETA02", "CUSR0000SAS", "CUSR0000SA0L1E"]
data, msgs = bls_fetch(ids, 2017, 2026, d, "cpi_q11b")
print([m for m in msgs if "not exist" in m or "No Data" in m][:10])
print({k: (len(v), max(v)) for k, v in data.items() if v})
for name, url in [("bls_cpi_news_release_nr0_2026-11-15.htm", "https://www.bls.gov/news.release/cpi.nr0.htm"),
                  ("bls_cpi_news_release_t02_2026-11-15.htm", "https://www.bls.gov/news.release/cpi.t02.htm"),
                  ("bls_cpi_motor_vehicle_insurance_2026-11-15.htm", "https://www.bls.gov/cpi/factsheets/motor-vehicle-insurance.htm"),
                  ("eia_retail_diesel_monthly.xls", "https://www.eia.gov/dnav/pet/hist_xls/EMD_EPD2D_PTE_NUS_DPGm.xls")]:
    try:
        b = http_get(url, timeout=60); (d / name).write_bytes(b); print("ok", name, len(b))
    except Exception as e:
        print("ERR", name, e)
