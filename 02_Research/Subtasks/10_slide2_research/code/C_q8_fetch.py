"""Q8 fetch: PPI intermediate demand by production flow (WPSID5*), by commodity type (WPSID6*), final demand (WPSFD4*).
Series list comes from the saved BLS wp series file (pipeline raw, read only). Saves raw JSON to 03_Data/Raw/BLS_PPI_stages_2026-11-15/.
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q8_fetch.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
import shutil

WP = ROOT / "03_Data/pipelines/Price indexes/PPI/raw/bls_wp_series_2026-09-27.txt"
folder = RAW / "BLS_PPI_stages_2026-11-15"
folder.mkdir(parents=True, exist_ok=True)
rows = [[x.strip() for x in l.rstrip("\n").split("\t")] for l in WP.read_text().splitlines()]
sel = [r for r in rows[1:] if r[0].startswith(("WPSID5", "WPSID6")) or r[0] in
       ("WPSFD4", "WPSFD41", "WPSFD42", "WPSFD49104", "WPSFD49116", "WPSFD49100", "WPSFD4121", "WPSFD49115")]
meta = {r[0]: r[5] for r in sel}
ids = sorted(meta)
print(len(ids), "series")
# copy the series-title file used (provenance) - it is a read-only copy into the new raw folder
shutil.copy(WP, folder / "bls_wp_series_2026-09-27_copy.txt")
data, msgs = bls_fetch(ids, 2017, 2026, folder, "ppi_stages_2017_2026")
print("messages:", msgs[:5])
missing = [s for s in ids if s not in data]
print("missing:", missing)
for s in ids[:3]:
    print(s, max(data[s]) if s in data else None)
