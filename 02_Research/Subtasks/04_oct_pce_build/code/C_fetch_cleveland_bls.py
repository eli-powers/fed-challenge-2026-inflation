"""C_fetch_cleveland_bls.py: save raw Cleveland Fed nowcast JSONs, BLS concordance HTML, BLS series lists (dated 2026-11-11).
Run from project root: python3 -I 02_Research/Subtasks/04_oct_pce_build/code/C_fetch_cleveland_bls.py
BLS requests use BLS_CONTACT_UA from .env (header only; never printed or saved)."""
import re, urllib.request, hashlib
from pathlib import Path
DATE = "2026-11-11"; RAW = Path("03_Data/Raw")
env = {}
for l in open(Path(".env")):
    m = re.match(r"\s*(?:export\s+)?(\w+)=(.*)", l)
    if m: env[m.group(1)] = m.group(2).strip().strip("'\"")
GEN = "Mozilla/5.0 (UMD College Fed Challenge research; inflation_data retrieval)"
def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    try:
        with urllib.request.urlopen(req, timeout=120) as r: return r.status, r.read()
    except Exception as e:
        return getattr(e, "code", str(type(e).__name__)), b""
base = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/"
for n in ("nowcast_month", "nowcast_year", "nowcast_quarter"):
    s, b = get(base+n+".json", GEN); print(n, s, len(b))
    if s == 200: (RAW/f"ClevelandFed_{n}_{DATE}.json").write_bytes(b)
ua = env.get("BLS_CONTACT_UA", GEN)
s, b = get("https://www.bls.gov/cpi/additional-resources/pce-cpi-code-mapping.htm", ua); print("concordance", s, len(b))
if s == 200: (RAW/f"BLS_pce_cpi_code_mapping_{DATE}.html").write_bytes(b)
for name in ("cu/cu.item", "cu/cu.series", "pc/pc.series", "wp/wp.series"):
    s, b = get(f"https://download.bls.gov/pub/time.series/{name}", ua); print(name, s, len(b))
    if s == 200:
        fn = "bls_" + name.split("/")[1].replace(".", "_") + f"_{DATE}.txt"
        (RAW/fn).write_bytes(b); print(" ->", fn)
