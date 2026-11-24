"""Shared helpers for Agent C scripts (slide 2 research). Run scripts from the project root with python3 -I."""
import json, os, re, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(".")
TASK = ROOT / "02_Research/Subtasks/10_slide2_research"
OUT = TASK / "outputs"
RAW = ROOT / "03_Data/Raw"
TODAY = "2026-11-15"


def load_keys():
    env = {}
    p = Path(".env")
    for line in p.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


KEYS = load_keys()


def redact(text):
    for v in KEYS.values():
        if v:
            text = text.replace(v, "REDACTED")
    return text


def ua(url):
    if "bls.gov" in url and KEYS.get("BLS_CONTACT_UA"):
        return KEYS["BLS_CONTACT_UA"]
    return "Mozilla/5.0 (UMD College Fed Challenge research)"


def http_get(url, params=None, timeout=120):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": ua(url)})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def http_post_json(url, payload, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"User-Agent": ua(url), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def bls_fetch(series, start, end, folder, tag):
    """Fetch BLS API v2 in batches of 50, save redacted raw JSON to folder; return merged {sid: {(y,m): (val, footnotes)}}."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    out, msgs = {}, []
    for i in range(0, len(series), 50):
        batch = series[i:i + 50]
        payload = {"seriesid": batch, "startyear": str(start), "endyear": str(end),
                   "registrationkey": KEYS["BLS_API_KEY"]}
        raw = http_post_json("https://api.bls.gov/publicAPI/v2/timeseries/data/", payload).decode()
        (folder / f"bls_api_{tag}_batch{i//50+1}_{TODAY}.json").write_text(redact(raw))
        j = json.loads(raw)
        msgs += j.get("message", [])
        for s in j["Results"]["series"]:
            d = {}
            for o in s["data"]:
                if o["period"].startswith("M") and o["period"] != "M13":
                    d[(int(o["year"]), int(o["period"][1:]))] = (float(o["value"]) if o["value"] not in ("-", "") else None,
                                                                   "; ".join(f.get("code", "") + ":" + f.get("text", "") for f in o.get("footnotes", []) if f))
            out[s["seriesID"]] = d
    return out, msgs
