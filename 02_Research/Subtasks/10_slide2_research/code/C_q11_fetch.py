"""Q11 fetch: CPI airline fares / food away from home / services; PPI airline passenger services, jet fuel, diesel, truck freight;
EIA monthly jet fuel and diesel spot. Raw -> 03_Data/Raw/BLS_CPI_PPI_q11_2026-11-15/ and EIA_fuel_spot_2026-11-15/.
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q11_fetch.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
ids = ["CUSR0000SETG01", "CUUR0000SETG01", "CUSR0000SEFV", "CUUR0000SEFV", "CUSR0000SAS", "CUSR0000SETG", "CUSR0000SEFV01", "CUSR0000SEFV02",
       "WPU3022", "WPSFD3022", "WPU057203", "WPU057303", "WPU3012", "WPSFD3012", "WPSFD422", "WPU0571", "WPS3022", "WPS3012", "WPS057203", "WPS057303"]
data, msgs = bls_fetch(ids, 2017, 2026, RAW / "BLS_CPI_PPI_q11_2026-11-15", "q11_2017_2026")
print(msgs[:6])
for k, v in data.items():
    print(k, len(v), max(v) if v else None)
e = RAW / "EIA_fuel_spot_2026-11-15"; e.mkdir(exist_ok=True, parents=True)
for name, url in [("EIA_EER_EPJK_PF4_RGC_DPGm.xls", "https://www.eia.gov/dnav/pet/hist_xls/EER_EPJK_PF4_RGC_DPGm.xls"),
                  ("EIA_EER_EPD2DXL0_PF4_RGC_DPGm.xls", "https://www.eia.gov/dnav/pet/hist_xls/EER_EPD2DXL0_PF4_RGC_DPGm.xls"),
                  ("EIA_EER_EPJK_PF4_RGC_DPGd.xls", "https://www.eia.gov/dnav/pet/hist_xls/EER_EPJK_PF4_RGC_DPGd.xls")]:
    try:
        b = http_get(url, timeout=60); (e / name).write_bytes(b); print("ok", name, len(b))
    except Exception as ex:
        print("ERR", name, ex)
