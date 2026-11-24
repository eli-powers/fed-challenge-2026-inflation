"""Extract text from source PDFs to outputs/text/ (page-tagged). Run from project root: python3 -I <this>."""
from pathlib import Path
import pypdf
ROOT = Path.cwd()
OUT = ROOT / "02_Research/Subtasks/11_slide3a_research/outputs/text"
OUT.mkdir(parents=True, exist_ok=True)
SRC = {
 "bb2023": "02_Research/External_views/Literature/2023_Bernanke_Blanchard_pandemic_inflation_NBER_w31417.pdf",
 "pace_qa": "02_Research/External_views/Previous_Finalists_copy/2025 /PACE/fed-challenge-winner-qa-transcript-20251121.pdf",
}
for k, p in SRC.items():
    r = pypdf.PdfReader(str(ROOT / p))
    with open(OUT / f"{k}.txt", "w") as f:
        for i, pg in enumerate(r.pages, 1):
            f.write(f"\n=====PAGE {i}=====\n")
            f.write(pg.extract_text() or "")
    print(k, len(r.pages))
# Added: Dolmas (2005) Dallas Fed WP 0506 (downloaded to S3A raw folder)
p = "03_Data/Raw/S3A_A_dallas_trimmed_2026-11-15/dallasfed_wp0506_Dolmas_2005.pdf"
if (ROOT / p).exists():
    r = pypdf.PdfReader(str(ROOT / p))
    with open(OUT / "dolmas_wp0506.txt", "w") as f:
        for i, pg in enumerate(r.pages, 1):
            f.write(f"\n=====PAGE {i}=====\n"); f.write(pg.extract_text() or "")
    print("dolmas", len(r.pages))
