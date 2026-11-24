"""Check whether the Q4 2026 SPF has been released (run last). python3 -I from project root. Output: outputs/C_q4_spf_q4_check.csv"""
import re, urllib.request, datetime, csv, html
from pathlib import Path
ROOT = Path.cwd(); OUT = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs/C_q4_spf_q4_check.csv"
RAW = ROOT / "03_Data/Raw/S3A_expectations_underlying_2026-11-15"
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
rows = []
for name, url in [("landing", "https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters"),
                  ("q4_2026_probe", "https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-q4-2026")]:
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (UMD research)"}), timeout=60).read().decode("utf-8", "ignore")
        (RAW / f"PhillyFed_SPF_{name}_recheck_{datetime.date.today().isoformat()}.html").write_text(d)
        t = html.unescape(re.sub(r"\s+", " ", re.sub(r"(?s)<script.*?</script>|<style.*?</style>|<[^>]+>", " ", d)))
        recent = re.search(r"Recent Releases (.{0,260})", t)
        q4 = bool(re.search(r"Fourth Quarter 2026 Survey of Professional Forecasters", t))
        rows.append(dict(checked_at=now, url=url, q4_2026_listed=q4, page_title_404="Error - 404" in d, recent_releases_snippet=(recent.group(1) if recent else "")[:260]))
    except Exception as e:
        rows.append(dict(checked_at=now, url=url, q4_2026_listed="error", page_title_404="", recent_releases_snippet=str(e)[:200]))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(rows)
