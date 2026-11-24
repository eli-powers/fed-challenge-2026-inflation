"""Shared retrieval helpers for inflation_data.

API keys are read from environment variables (BEA_API_KEY, BLS_API_KEY,
FRED_API_KEY) and are never written to disk: every saved payload passes
through redact() first. Redaction is the only modification made to raw files.
"""
import json
import os
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETRIEVAL_DATE = date.today().isoformat()
USER_AGENT = "Mozilla/5.0 (UMD College Fed Challenge research; inflation_data retrieval)"
KEY_VARS = ("BEA_API_KEY", "BLS_API_KEY", "FRED_API_KEY")


def get_key(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set in the environment")
    return value


def redact(content):
    """Remove every API key value from str/bytes content."""
    is_bytes = isinstance(content, bytes)
    text = content.decode("utf-8", errors="surrogateescape") if is_bytes else content
    for var in KEY_VARS:
        value = os.environ.get(var)
        if value:
            text = text.replace(value, "REDACTED")
    return text.encode("utf-8", errors="surrogateescape") if is_bytes else text


def http_get(url, params=None, headers=None, timeout=120):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def http_post_json(url, payload, timeout=120):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def save_raw(group, filename, content):
    """Save a publisher payload under raw/<group>/ with keys redacted. Returns the relative path."""
    path = ROOT / "raw" / group / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(redact(content if isinstance(content, bytes) else content.encode()))
    return str(path.relative_to(ROOT.parent))


def fred_initial_release(series_id):
    """ALFRED first-release observations (output_type=4): realtime_start = first release date."""
    raw = http_get(
        "https://api.stlouisfed.org/fred/series/observations",
        {
            "series_id": series_id,
            "api_key": get_key("FRED_API_KEY"),
            "file_type": "json",
            "output_type": 4,
            "realtime_start": "1776-07-04",
            "realtime_end": "9999-12-31",
        },
    )
    return raw
