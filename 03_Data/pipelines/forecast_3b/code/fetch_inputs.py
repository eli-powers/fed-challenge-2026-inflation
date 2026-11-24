"""fetch_inputs.py: download every raw input of the slide-3B forecast into a NEW dated folder.

Run from the project root:
    python3 -I 03_Data/pipelines/forecast_3b/code/fetch_inputs.py

Writes 03_Data/pipelines/forecast_3b/raw/<YYYY-MM-DD>/ (or <YYYY-MM-DD>_2, _3 ... if today's folder exists;
nothing is ever overwritten) containing:
  SPF (Philadelphia Fed):  medianLevel.xlsx, Dispersion_1.xlsx, spf-release-dates.txt
  EIA STEO:                page_steo_outlook.html (vintage release dates), <vintage>_base.xlsx for
                           - the latest vintage (oil path P1),
                           - for the latest TWO SPF surveys: the vintage matching the survey deadline
                             (latest STEO released on/before it) and the one before (proxy sensitivity),
                           - the pre-war vintage(s) in config/oil_path_rules.json (path P3)
  EIA Brent daily spot:    EIA_RBRTEd.xls
  Core PCE index (FRED):   PCEPILFE_observations.json (API key read from .env,
                           never written; any echo of it is redacted)
  manifest.json:           url, bytes, sha256, retrieval time per file.

Everything is downloaded to a hidden staging folder first and validated (files parse; SPF survey and
deadline found; STEO has BREPUUS). Only then is the staging folder renamed to the dated folder. If
anything fails, the script deletes the staging folder, prints what failed, and exits with status 1:
the previous dated raw folder stays the input that forecast.py uses.

The SPF files are cumulative (every survey is a row), so the same URLs work for the Q4 survey unchanged.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parsers as P  # noqa: E402

PIPE = Path(__file__).resolve().parents[1]
RAWDIR = PIPE / "raw"
UA = "Mozilla/5.0 (university research)"
PHI = "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters"
SPF_FILES = {"medianLevel.xlsx": f"{PHI}/historical-data/medianLevel.xlsx",
             "Dispersion_1.xlsx": f"{PHI}/historical-data/Dispersion_1.xlsx",
             "spf-release-dates.txt": f"{PHI}/spf-release-dates.txt"}
STEO_PAGE = "https://www.eia.gov/outlooks/steo/outlook.php"
STEO_ARCH = "https://www.eia.gov/outlooks/steo/archives/{v}_base.xlsx"
BRENT = "https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls"
FRED = "https://api.stlouisfed.org/fred/series/observations"


def fred_key() -> str:
    p = Path(".env")
    for line in p.read_text().splitlines():
        line = line.strip().removeprefix("export ")
        if line.startswith("FRED_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("FRED_API_KEY not found in .env")


class Fetcher:
    def __init__(self, folder: Path, secrets=()):
        self.folder, self.secrets, self.manifest = folder, [s for s in secrets if s], []

    def get(self, name: str, url: str, params: dict | None = None):
        full = f"{url}?{urllib.parse.urlencode(params)}" if params else url
        req = urllib.request.Request(full, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r:
            b = r.read()
            status = r.status
        if status != 200 or not b:
            raise RuntimeError(f"HTTP {status} / {len(b)} bytes for {url}")
        if params:  # API response: redact any echo of the key
            t = b.decode("utf-8", "replace")
            for s in self.secrets:
                t = t.replace(s, "REDACTED")
            b = t.encode()
        (self.folder / name).write_bytes(b)
        self.manifest.append({"file": name, "url": url, "params": {k: ("REDACTED" if k == "api_key" else v)
                                                                   for k, v in (params or {}).items()},
                              "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                              "retrieved_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
        print(f"  ok  {name:32s} {len(b):>10,d} bytes")


def new_folder_name() -> Path:
    base = dt.date.today().isoformat()
    cand, n = RAWDIR / base, 2
    while cand.exists():
        cand, n = RAWDIR / f"{base}_{n}", n + 1
    return cand


def previous_input() -> str:
    ds = sorted(p.name for p in RAWDIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    return ds[-1] if ds else "(none)"


def main():
    RAWDIR.mkdir(parents=True, exist_ok=True)
    stage = RAWDIR / f".staging_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}"
    stage.mkdir()
    key = fred_key()
    F = Fetcher(stage, secrets=[key])
    step = "start"
    try:
        step = "SPF files"
        print("SPF (Philadelphia Fed):")
        for n, u in SPF_FILES.items():
            F.get(n, u)
        med = P.read_spf_median(stage / "medianLevel.xlsx")
        surveys = P.surveys_present(med)
        latest_two = surveys[-2:]
        deadlines = {}
        for s in latest_two:
            rd = P.parse_release_dates(stage / "spf-release-dates.txt", s)
            if rd is None:
                raise RuntimeError(f"survey {s} is in medianLevel.xlsx but not in spf-release-dates.txt")
            deadlines[s] = rd[0]
        print(f"  latest surveys {latest_two}; deadlines {deadlines}")
        disp = P.read_dispersion_d1(stage / "Dispersion_1.xlsx")
        if latest_two[-1] not in disp:
            print(f"  NOTE: Dispersion_1.xlsx has no row for {latest_two[-1]} yet (fan will omit the SPF IQR)")

        step = "STEO"
        print("EIA STEO:")
        F.get("page_steo_outlook.html", STEO_PAGE)
        rel = P.parse_steo_release_dates(stage / "page_steo_outlook.html")
        if not rel:
            raise RuntimeError("could not parse STEO release dates from outlook.php")
        rules = json.loads((PIPE / "config/oil_path_rules.json").read_text())
        need = [P.latest_steo(rel)]
        for s in latest_two:
            m, prev = P.steo_vintage_for(deadlines[s], rel)
            need += [m] + ([prev] if prev else [])
        need += rules["prewar_steo_vintages"]
        need = list(dict.fromkeys(need))
        for v in need:
            F.get(f"{v}_base.xlsx", STEO_ARCH.format(v=v))
            if P.read_steo_series(stage / f"{v}_base.xlsx").empty:
                raise RuntimeError(f"{v}_base.xlsx has no BREPUUS data")

        step = "Brent daily"
        print("EIA Brent daily:")
        F.get("EIA_RBRTEd.xls", BRENT)
        b = P.read_eia_daily(stage / "EIA_RBRTEd.xls")
        print(f"  last Brent observation {b.index[-1].date()} ${b.iloc[-1]:.2f}")

        step = "FRED PCEPILFE"
        print("FRED core PCE price index:")
        F.get("PCEPILFE_observations.json", FRED,
              {"series_id": "PCEPILFE", "api_key": key, "file_type": "json", "observation_start": "2019-01-01"})
        c = P.load_fred_obs(stage / "PCEPILFE_observations.json")
        rt = json.loads((stage / "PCEPILFE_observations.json").read_text()).get("realtime_start")
        print(f"  last core PCE month {c.index[-1].date():%Y-%m} (FRED realtime {rt})")
    except Exception as e:  # noqa: BLE001
        shutil.rmtree(stage, ignore_errors=True)
        print(f"\nFETCH FAILED at step '{step}': {e}\nNo new raw folder was created. "
              f"forecast.py will keep using the previous input: raw/{previous_input()}", file=sys.stderr)
        sys.exit(1)

    (stage / "manifest.json").write_text(json.dumps(
        {"fetched_by": "code/fetch_inputs.py", "surveys": latest_two, "deadlines": deadlines,
         "steo_vintages": need, "steo_release_dates": {v: rel.get(v) for v in need}, "files": F.manifest}, indent=1))
    dest = new_folder_name()
    stage.rename(dest)
    print(f"\nDone: {dest.relative_to(PIPE.parents[2])}")


if __name__ == "__main__":
    main()
