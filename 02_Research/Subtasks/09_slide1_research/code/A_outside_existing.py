"""A_outside_existing.csv: every row of R_forecaster_oct2026_2026-11-14.csv, plus tier and pre_or_post_PPI columns.
Bowman upgraded to primary by quoting the sentence from the saved speech (RTF, converted with macOS textutil).
Cleveland labelled 'model nowcast, no PPI'. No web access."""
import sys, re, subprocess
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *

src = rd(f'{BUILD}/R_forecaster_oct2026_2026-11-14.csv')
rtf = f'{SPEECHES}/2026-11-10_Bowman_US_economy_monetary_policy.rtf'
txt = subprocess.run(['textutil', '-convert', 'txt', '-stdout', rtf], capture_output=True, text=True, check=True).stdout
txt = re.sub(r'\s+', ' ', txt)
m = re.search(r"Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3\.3 percent in October[^.]*\.[^.]*\.", txt)
assert m, 'Bowman sentence not found'
# the sentence as printed (ends at 'services prices.')
sent = re.search(r"Today's consumer price index suggests that 12-month core PCE inflation likely moved up further to 3\.3 percent in October, as upward pressures from higher energy prices and AI-related demand continue to flow through to core goods and services prices\.", txt).group(0)

TIER = {'UMD bottom-up (ours)': ('model', 'post-PPI (built Nov 13 after 8:30 ET PPI)', 'our build (UMD)'),
        'Cleveland Fed nowcast': ('model', 'n/a: model does not use PPI (chart updated Nov 13; unchanged since Nov 10 CPI)', 'model nowcast, no PPI')}
rows = []
for r in src:
    f = r['forecaster']
    o = dict(r)
    o['orig_source_type'] = r['source_type']
    o['label'] = ''
    if f in TIER:
        o['tier'], o['pre_or_post_PPI'], o['label'] = TIER[f]
    elif f.startswith('Michelle Bowman'):
        o['tier'] = 'primary'
        o['pre_or_post_PPI'] = 'pre-PPI (speech Nov 10, after Oct CPI that morning; before PPI Nov 13 8:30 ET)'
        o['source_type'] = 'primary (Fed speech text, saved copy opened)'
        o['outlet_and_date'] = 'Federal Reserve Board, speech at Council on Foreign Relations, 2026-11-10'
        o['url'] = 'https://www.federalreserve.gov/newsevents/speech/bowman20261110a.htm'
        o['quote_or_note'] = ('"' + sent + '" [O: saved text, 02_Research/External_views/Fed_officials_2026-11/speeches/2026-11-10_Bowman_US_economy_monetary_policy.rtf; '
                              'URL taken from the saved file\'s own footnote links, page itself not re-fetched]. '
                              'Prior row quoted StockTitan as "core PCE inflation likely moved up to 3.3% over the 12 months to October"; that wording is a paraphrase, not the speech text. '
                              'Speech gives 12m core only (no m/m, no headline).')
        o['label'] = 'official, 12m core only'
    elif r['timing'].startswith('before PPI'):
        o['tier'], o['pre_or_post_PPI'] = 'press-reported', 'pre-PPI (superseded)'
    elif r['timing'].startswith('after PPI'):
        o['tier'], o['pre_or_post_PPI'] = 'press-reported', 'post-PPI'
    else:
        raise SystemExit(f'unclassified timing for {f}: {r["timing"]}')
    o['source_file'] = '02_Research/Subtasks/04_oct_pce_build/outputs/R_forecaster_oct2026_2026-11-14.csv'
    o['vintage'] = 'compiled 2026-11-14; PPI released 2026-11-13 08:30 ET'
    o['basis'] = 'Oct 2026 PCE price index, SA; core_mm/headline_mm = 1m %, *_yy = 12m % (as stated by source)'
    rows.append(o)
cols = ['forecaster', 'tier', 'pre_or_post_PPI', 'label', 'timing', 'core_mm', 'core_yy', 'headline_mm', 'headline_yy', 'revised_from',
        'source_type', 'orig_source_type', 'outlet_and_date', 'url', 'quote_or_note', 'source_file', 'vintage', 'basis']
write_csv(f'{OUT}/A_outside_existing.csv', rows, cols)
print('Bowman sentence:', sent)
print('rows in source:', len(src), 'rows out:', len(rows))
