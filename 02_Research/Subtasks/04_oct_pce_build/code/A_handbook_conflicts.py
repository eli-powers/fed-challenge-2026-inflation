"""Brief A step 6: compare BEA Table 2.4.4U-D sources with NIPA Handbook ch.5 Tables 5.A/5.B (Dec 2021 vintage).
Checks PPI-sourced, composite, imputed lines and any line where wording differs. Each handbook phrase is
asserted to exist in the pypdf-extracted text of PDF pages 105-130 (whitespace-normalized).
Run from project root: python3 02_Research/Subtasks/04_oct_pce_build/code/A_handbook_conflicts.py"""
import os, re, sys
import pandas as pd
from pypdf import PdfReader
sys.path.insert(0, os.path.dirname(__file__))
from A_common import *

rd = PdfReader(HANDBOOK)
text = {p + 1: rd.pages[p].extract_text() for p in range(104, 130)}
flat = lambda s: re.sub(r'\s+', ' ', s.replace('’', "'")).lower()
ftext = {p: flat(t) for p, t in text.items()}
t244 = {r['line']: r for r in load_t244() if r['line']}
cm = pd.read_csv(os.path.join(OUT, 'component_mapping.csv'))
w = dict(zip(cm.pricing_bea_line, cm.share_of_headline_sep2026))

# (lines, handbook phrase as printed, classification, note)
CHECKS = [
    ((15, 19), 'Dealers\' margins: PPI for used vehicle sales at new car dealers', 'conflict',
     'Handbook prices used-vehicle dealer margins with a PPI; T244 uses CPI Used cars and trucks'),
    ((50,), 'CPI for computer software and accessories', 'conflict',
     'Handbook lists CPI only; T244 adds PPIs for game software publishing and hosting/ASP (composite)'),
    ((299,), 'Legal services Commodity-flow method', 'context', 'row anchor'),
    ((299, 305), 'CPI for legal services', 'conflict',
     'Handbook: CPI for legal services (legal services and professional association dues); T244: fixed-weighted composite of five PPIs'),
    ((268,), 'Fixed-weighted average of PPI for Portfolio management and PPI for investment advice', 'conflict',
     'Handbook names two PPIs; T244 says implicit (quantity extrapolation, QSS) and out months from market indicators and judgmental trend'),
    ((302,), 'PPI for employment placement agencies', 'wording',
     'Handbook: employment placement agencies-primary services; T244: Employment placement services'),
    ((211,), 'CPI for club dues and fees for participant sports and group exercises', 'wording',
     'Older CPI item name; T244 uses current BLS item SERF01'),
    ((219,), 'CPI for cable and satellite television service', 'wording', 'Older CPI item name (now includes live streaming)'),
    ((220,), 'Photo processing: CPI for film processing', 'wording', 'Older CPI item name'),
    ((224,), 'Video streaming and rental: CPI for rental of video discs and other media', 'conflict',
     'Different CPI item: T244 uses Subscription and rental of video and video games'),
    ((216,), 'Spectator sports: CPI for admission to sporting events', 'wording', 'T244 adds "& judgmental trend"'),
    ((301,), 'CPI for tax return preparation and other accounting fees', 'wording', 'T244 adds "& judgmental trend"'),
    ((296,), 'Nursery: CPI for child care and nursery school', 'wording', 'Older CPI item name (now Day care and preschool)'),
    ((316,), 'Child care: CPI for child care and nursery school', 'wording', 'Older CPI item name'),
    ((240,), 'Meals at schools: CPI for food at employee sites and schools', 'conflict',
     'Handbook prices all meals at schools with food at employee sites and schools; T244 line 240 (higher education lunches) uses Full service meals and snacks'),
    ((247, 248), 'CPI for food at employee sites and schools', 'conflict',
     'Handbook (food furnished to employees incl. military) uses food at employee sites and schools; T244 uses Full service meals and snacks'),
    ((163,), "For current quarterly based on CPI for owners' equivalent rent of primary residence", 'consistent', ''),
    ((255,), 'Commercial banks: for annual, quantity extrapolation, using BLS banking output indexes; for quarterly, judgmental trend', 'consistent', ''),
    ((256,), 'PCE deflator for services furnished without payment by commercial banks', 'consistent', ''),
    ((174,), 'PPI for offices of physicians', 'consistent', ''),
    ((177,), 'Home health care: PPI for home health care services', 'consistent', ''),
    ((178,), 'Medical laboratories: PPI for medical laboratories and PPI for diagnostic imaging centers', 'consistent', 'weights not stated in either'),
    ((184, 185, 186), 'PPI for hospitals', 'consistent', ''),
    ((188, 189), 'PPI for nursing care facilities', 'consistent', ''),
    ((207,), 'PPI for domestic scheduled passenger air transportation', 'consistent', ''),
    ((262, 263, 265, 266, 267), 'PPI for brokerage services, equities and ETFs', 'consistent', 'securities commissions block'),
    ((269,), 'PPI for Commercial bank trust services', 'consistent', ''),
    ((271,), 'BEA composite index of input costs', 'consistent', 'life insurance; also labor org dues, NPISH'),
    ((272,), "PPI for homeowners' insurance", 'consistent', ''),
    ((276,), 'PPI for direct health and medical insurance carriers', 'consistent', ''),
    ((277,), 'Income loss: CPI for all items', 'consistent', ''),
    ((279,), 'PPI for private passenger auto insurance', 'consistent', ''),
    ((285,), 'Fixed-weighted average of CPI for wireless telephone services and CPI for smartphones', 'consistent', 'weights not stated in either'),
    ((283, 284), 'CPI for land line telephone services', 'consistent', 'BLS item now appears as Residential telephone services (SEED04) - unverified rename'),
    ((328,), 'Domestic services: CPI for domestic services, CPI for food at home, and CPI for laundry and dry cleaning services', 'consistent', ''),
    ((103,), 'BEA composite index of USDA prices received by farmers', 'consistent', ''),
    ((111,), 'Standard clothing issued military: PPI for apparel', 'consistent', ''),
    ((227, 228, 229), 'CPI for all items', 'consistent', 'gambling'),
    ((251,), 'Housing at schools: CPI for housing at school, excluding board', 'consistent', 'BLS item is Lodging while at school (SEHB01)'),
    ((54,), 'CPI for new motorcycles', 'consistent', 'but BLS US-average series ended 2000M05 (see A_stale_series.csv)'),
    ((342,), 'Calculated as line 112 minus line 113', 'consistent', 'NPISH = gross output less receipts'),
]
rows = []
for lines, phrase, cls, note in CHECKS:
    fp = flat(phrase)
    pages = [p for p, t in ftext.items() if fp in t]
    if not pages:  # allow for column run-together: require all words in order within one page
        words = fp.split()
        pages = [p for p, t in ftext.items() if re.search(r'.{0,40}'.join(map(re.escape, words)), t)]
    for l in lines:
        rows.append(dict(bea_line=l, t244_source=t244[l]['source'], handbook_phrase=phrase,
                         handbook_pdf_pages=';'.join(map(str, pages)) or 'NOT FOUND', classification=cls, note=note,
                         share_of_headline_sep2026=w.get(l)))
df = pd.DataFrame(rows)
df = df[df.classification != 'context']
df.to_csv(os.path.join(OUT, 'A_conflicts.csv'), index=False)
print(df[['bea_line', 'classification', 'handbook_pdf_pages', 'share_of_headline_sep2026']].to_string())
assert not (df.handbook_pdf_pages == 'NOT FOUND').any(), df[df.handbook_pdf_pages == 'NOT FOUND']
c = df[df.classification == 'conflict']
print('conflict lines:', sorted(c.bea_line.unique()), 'headline weight of conflict lines:', c.drop_duplicates('bea_line').share_of_headline_sep2026.sum())
