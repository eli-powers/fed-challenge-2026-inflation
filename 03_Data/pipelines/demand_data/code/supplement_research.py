"""Manager supplement: Conference Board values transcribed from official press releases
(proprietary data; headline values only). Run after retrieve_research.py.

Each REL entry is month -> (source document URL or demand_data/raw/... path, note, (headline, present situation, expectations)).
A month that is revised in a later release is stored once, at its latest published vintage; the earlier print is named in the note.
Where a later release gives a revised headline plus changes for the sub-indices, the sub-index level is that release's
current level minus its stated change (same convention as the Aug 2026 and Jun 2026 rows)."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "processed" / "research" / "observations.csv"
CB_PAGE_0210 = "demand_data/raw/research/conferenceboard_consumer_confidence_latest_release_page_2026-10-02.html"
REL = {
    "2025-08-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-little-changed-in-august-302538912.html",
                   "Aug 26, 2025 release (original vintage; later revisions not verified)", (97.4, 131.2, 74.8)),
    "2025-09-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-declines-again-in-september-302570940.html",
                   "Sept 30, 2025 release (original vintage; later revisions not verified).", (94.2, 125.4, 73.4)),
    "2026-05-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-edged-downward-in-may-302781849.html",
                   "May 2026 release (original vintage; later revisions not verified)", (93.1, 121.2, 74.4)),
    "2026-06-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-edged-down-in-july-302836484.html",
                   "June 2026 as revised in the July 28, 2026 release (headline 92.2; PS = 114.9+3.6; Exp = 74.7 unchanged).", (92.2, 118.5, 74.7)),
    "2026-07-01": ("http://www.prnewswire.com/news-releases/us-consumer-confidence-edged-down-slightly-in-august-302859371.html",
                   "July 2026 as revised in the Aug 25, 2026 release (headline 90.2; PS = 121.2-6.8; Exp = 68.2+5.8)", (90.2, 114.4, 74.0)),
    "2026-08-01": (CB_PAGE_0210,
                   "Aug 2026 as revised in the Sept 29, 2026 release (was 89.4 / 121.2 / 68.2).", (88.6, 117.2, 69.5)),
    "2026-09-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-increased-in-october-302920731.html",
                   "Sept 2026 as revised in the Oct 27, 2026 release (headline 84.2 'a slight upward revision'; PS = 120.4-8.6; Exp = 72.6-6.9; "
                   "first print Sept 29 was 81.9 / 109.3 / 63.6).", (84.2, 111.8, 65.7)),
    "2026-10-01": ("https://www.prnewswire.com/news-releases/us-consumer-confidence-increased-in-october-302920731.html",
                   "Oct 2026 as published in the Oct 27, 2026 release (first print).", (91.7, 120.4, 72.6)),
}
LATEST_RELEASE = ("2026-10-27", "https://www.prnewswire.com/news-releases/us-consumer-confidence-increased-in-october-302920731.html")
KEYS = ["conference_board_confidence", "conference_board_present_situation", "conference_board_expectations"]

if __name__ == "__main__":
    o = pd.read_csv(P, dtype=str)
    o = o[~(o.series_key.isin(KEYS) & o.date.isin(REL))]
    o.loc[o.series_key.isin(KEYS), "seasonal_adjustment"] = "SA"  # CB indexes are seasonally adjusted (technical note)
    rows = []
    for d, (url, note, vals) in REL.items():
        for k, v in zip(KEYS, vals):
            rows.append({"series_key": k, "date": d, "frequency": "M", "value": v, "units": "Index (1985=100)", "seasonal_adjustment": "SA",
                         "source_id": "The Conference Board press release", "raw_file": url, "note": "Manager transcription: " + note})
    pd.concat([o, pd.DataFrame(rows)]).sort_values(["series_key", "date"]).to_csv(P, index=False)
    # Keep metadata in step with the transcribed observations (retrieve_research.py leaves the scrape's fallback values).
    M = P.with_name("series_metadata.csv")
    meta = pd.read_csv(M, dtype=str).fillna("")
    allobs = pd.read_csv(P, dtype=str)
    for k in KEYS:
        i = meta.index[meta.series_key == k]
        d = allobs.loc[allobs.series_key == k, "date"]
        meta.loc[i, "earliest_obs"], meta.loc[i, "latest_obs"] = d.min(), d.max()
        meta.loc[i, "latest_release_date"] = LATEST_RELEASE[0]
        meta.loc[i, "seasonal_adjustment"] = "SA"
        meta.loc[i, "raw_files"] = "; ".join(sorted({u for u, _, _ in REL.values()}))
        meta.loc[i, "notes"] = (f"Headline values transcribed from official Conference Board press releases (see each observation's raw_file). "
                                f"Latest release {LATEST_RELEASE[0]}: {LATEST_RELEASE[1]}. Seasonally adjusted per the Conference Board technical note. "
                                "Sub-index levels for revised months are derived (latest level minus stated change), as noted per row.")
    meta.to_csv(M, index=False)
    print("added", len(rows))
