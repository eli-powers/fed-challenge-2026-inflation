"""Q8 fetch part 3: NSA versions of the headline series (BLS publishes 12-month changes on an NSA basis) for a y/y cross-check.
Run: python3 -I 02_Research/Subtasks/10_slide2_research/code/C_q8_fetch_nsa.py"""
import sys
sys.path.insert(0, "./02_Research/Subtasks/10_slide2_research/code")
from C_common import *
ids = ["WPUID51", "WPUID52", "WPUID53", "WPUID54", "WPUFD4", "WPUID61", "WPUID62", "WPUID63", "WPUID64"]
data, msgs = bls_fetch(ids, 2017, 2026, RAW / "BLS_PPI_stages_2026-11-15", "ppi_nsa_check_2017_2026")
print(msgs[:3], {k: max(v) for k, v in data.items()})
