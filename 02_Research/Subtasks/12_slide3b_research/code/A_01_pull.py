"""A_01_pull: record of every download for Agent A (slide 3B). Idempotent: skips files that exist.
Run from project root: python3 -I 02_Research/Subtasks/12_slide3b_research/code/A_01_pull.py
Uses curl via subprocess (network). FRED key read from .env, never written out.
For a new SPF (e.g. Q4 2026) change SPF_FOLDER date/label, or pass: A_01_pull.py spf <label> <yyyy-mm-dd>."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "03_Data/Raw"
UA = "Mozilla/5.0"
PHI = "https://www.philadelphiafed.org"
M = "/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters"


def curl(url, dest, force=False):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        print("skip", dest.name)
        return
    r = subprocess.run(["curl", "-s", "-L", "-m", "180", "-A", UA, "-o", str(dest), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    print(r.stdout, dest.name)


def pull_spf(label="2026Q3", date="2026-11-15", page_slug="spf-q3-2026", pdf="2026/spfQ326.pdf"):
    d = RAW / f"PhilFed_SPF_{label}_{date}"
    # NB: the xlsx 'hash' query strings are copied from the site's links on the pull date and may change.
    for name, path in [("medianLevel.xlsx", "historical-data/medianLevel.xlsx"),
                       ("Dispersion_1.xlsx", "historical-data/Dispersion_1.xlsx"),
                       ("Dispersion_2.xlsx", "historical-data/Dispersion_2.xlsx"),
                       ("SPFmicrodata.xlsx", "historical-data/SPFmicrodata.xlsx"),
                       ("spf-release-dates.txt", "spf-release-dates.txt"),
                       ("spf-documentation.pdf", "spf-documentation.pdf"),
                       (Path(pdf).name, pdf)]:
        curl(f"{PHI}{M}/{path}", d / name)
    curl(f"{PHI}/surveys-and-data/real-time-data-research/{page_slug}", d / f"page_{page_slug}.html")
    curl(f"{PHI}/surveys-and-data/real-time-data-research/survey-of-professional-forecasters", d / "page_spf_main.html")


def pull_fred():
    keys = Path(".env")
    key = re.search(r"FRED_API_KEY=(\S+)", keys.read_text()).group(1)
    d = RAW / "FRED_PCEPILFE_latest_2026-11-15"
    curl("https://api.stlouisfed.org/fred/series/observations?series_id=PCEPILFE&api_key=%s&file_type=json"
         "&observation_start=2019-01-01" % key, d / "PCEPILFE_observations.json")
    curl("https://api.stlouisfed.org/fred/series?series_id=PCEPILFE&api_key=%s&file_type=json" % key,
         d / "PCEPILFE_metadata.json")


def pull_sep():
    d = RAW / "FOMC_SEP_2026-09_2026-11-15"
    curl("https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm", d / "fomcprojtabl20260916.htm")
    curl("https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl20260916.pdf", d / "fomcprojtabl20260916.pdf")


def pull_steo():
    d = RAW / "EIA_STEO_2026-11-15"
    curl("https://www.eia.gov/outlooks/steo/outlook.php", d / "page_steo_outlook.html")
    for f in ["jul26", "aug26", "sep26", "oct26", "nov26"]:
        curl(f"https://www.eia.gov/outlooks/steo/archives/{f}.pdf", d / f"{f}.pdf")
        curl(f"https://www.eia.gov/outlooks/steo/archives/{f}_base.xlsx", d / f"{f}_base.xlsx")


def pull_eia_futures():
    d = RAW / "EIA_NYMEX_WTI_futures_RCLC_2026-11-15"
    for n in (1, 2, 3, 4):
        curl(f"https://www.eia.gov/dnav/pet/hist_xls/RCLC{n}d.xls", d / f"RCLC{n}d.xls")
    curl("https://www.eia.gov/dnav/pet/pet_pri_fut_s1_d.htm", d / "page_pet_pri_fut_s1_d.htm")


def pull_yahoo_brent():
    """Free secondary source (Yahoo Finance chart API) for NYMEX Brent Last-Day futures BZ<month><yy>.
    Only unexpired contracts exist, so 2026 contracts are not retrievable after expiry."""
    d = RAW / "Yahoo_BZ_futures_curve_2026-11-15"
    d.mkdir(parents=True, exist_ok=True)
    syms = ["BZ=F"] + [f"BZ{c}{y}.NYM" for y in (26, 27, 28) for c in "FGHJKMNQUVXZ"]
    for s in syms:
        dest = d / f"{s.replace('=', '_')}.json"
        if dest.exists():
            continue
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=1783000000&period2=1786800000&interval=1d"
        r = subprocess.run(["curl", "-s", "-m", "30", "-A", UA, "-o", str(dest), url], capture_output=True)
        time.sleep(0.3)


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "spf":
        lab, date = sys.argv[2], sys.argv[3]
        yr, qq = lab[:4], lab[-1]
        pull_spf(lab, date, f"spf-q{qq}-{yr}", f"{yr}/spfQ{qq}{yr[2:]}.pdf")
    else:
        pull_spf()
        pull_fred()
        pull_sep()
        pull_steo()
        pull_eia_futures()
        pull_yahoo_brent()
