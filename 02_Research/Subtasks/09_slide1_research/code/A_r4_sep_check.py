"""A_r4_sep_check.csv: Sep 2026 PCE y/y from (a) BEA index levels, (b) BEA release text, (c) officials' saved speeches."""
import sys, re
sys.path.insert(0, './02_Research/Subtasks/09_slide1_research/code')
from A_common import *
from bs4 import BeautifulSoup
import pypdf

norm = lambda s: re.sub(r'\s+', ' ', s).strip()
lv = load_levels()
rows = []
BEA_H, BEA_C = {}, {}

# (b) BEA release text
html = open(BEA_REL, encoding='utf-8', errors='replace').read()
bt = norm(BeautifulSoup(html, 'html.parser').get_text(' '))
mm = re.search(r'From the preceding month, the PCE price index for September increased ([\d.]+) percent\s*\. Excluding food and energy, the PCE price index increased ([\d.]+) percent\.', bt)
yy = re.search(r'From the same month one year ago, the PCE price index for September increased ([\d.]+) percent\s*\. Excluding food and energy, the PCE price index increased ([\d.]+) percent from one year ago\.', bt)
assert mm and yy
bea_sent = norm(re.search(r'From the same month one year ago.*?from one year ago\.', bt).group(0)).replace(' .', '.').replace(' percent .', ' percent.')
rel = re.search(r'EMBARGOED UNTIL RELEASE AT [^,]*, ([A-Za-z]+, [A-Za-z]+ \d+, \d{4})', bt).group(1)
BEA_H, BEA_C = float(yy.group(1)), float(yy.group(2))

def add(src_id, who, measure, metric, value, basis_note, quote, location, vintage, source_file, tag, bea_val=None):
    diff = ''
    if bea_val is not None and value is not None:
        cv = round(value, 1)  # compare at BEA's published 1 dp
        diff = 'same as BEA text at 1 dp' if abs(cv - bea_val) < 1e-9 else f'DIFFERS from BEA text ({bea_val}): {cv - bea_val:+.1f}'
    rows.append(dict(item=src_id, source=who, measure=measure, metric=metric, value=('' if value is None else value),
                     compare_to_bea_text=diff, quote=quote, location=location, vintage=vintage, source_file=source_file,
                     verification=tag, basis=basis_note))

for meas, bea in (('headline', BEA_H), ('core', BEA_C)):
    r = rates(lv[meas], (2026, 9))
    add('a', 'BEA index levels (T20804)', meas, 'Sep 2026 y/y %, 3 dp', round(r['r12m'], 3),
        f'12m % = (L Sep26 / L Sep25 - 1)*100; levels {lv[meas][(2026,9)]:.3f} / {lv[meas][(2025,9)]:.3f}; SA index 2017=100; line {"1 (DPCERG)" if meas=="headline" else "25 (DPCCRG)"}',
        '', 'T20804 line ' + ('1' if meas == 'headline' else '25') + ', periods 2025M09 and 2026M09', T20804_VINTAGE, T20804.replace(ROOT + '/', ''), '[O] opened (JSON)', bea)
add('b', 'BEA news release text', 'headline', 'Sep 2026 y/y %, 1 dp', BEA_H, 'as published, 1 dp; SA; reference period Sep 2026', bea_sent, 'Highlights paragraph, "From the same month one year ago..."', f'BEA release, embargo {rel}', BEA_REL.replace(ROOT + '/', ''), '[O] opened (HTML)')
add('b', 'BEA news release text', 'core', 'Sep 2026 y/y %, 1 dp', BEA_C, 'as published, 1 dp; SA; reference period Sep 2026', bea_sent, 'same sentence', f'BEA release, embargo {rel}', BEA_REL.replace(ROOT + '/', ''), '[O] opened (HTML)')
add('b', 'BEA news release text', 'headline', 'Sep 2026 m/m %, 1 dp', float(mm.group(1)), 'as published, 1 dp; SA', 'From the preceding month, the PCE price index for September increased %s percent.' % mm.group(1), 'Highlights paragraph', f'BEA release, embargo {rel}', BEA_REL.replace(ROOT + '/', ''), '[O] opened (HTML)')
add('b', 'BEA news release text', 'core', 'Sep 2026 m/m %, 1 dp', float(mm.group(2)), 'as published, 1 dp; SA', 'Excluding food and energy, the PCE price index increased %s percent.' % mm.group(2), 'Highlights paragraph', f'BEA release, embargo {rel}', BEA_REL.replace(ROOT + '/', ''), '[O] opened (HTML)')

# (c) officials
def html_text(fn):
    return norm(BeautifulSoup(open(f'{SPEECHES}/{fn}', encoding='utf-8', errors='replace').read(), 'html.parser').get_text(' '))
def sent_around(text, pat, lo=0, hi=0):
    m = re.search(pat, text)
    assert m, pat
    return m
def sentence(text, m):
    a = max(text.rfind('. ', 0, m.start()) + 2, 0)
    b = text.find('. ', m.end())
    return text[a:b + 1]

# Waller (PDF)
wf = '2026-11-10_Waller_economic_outlook.pdf'
pages = [norm(p.extract_text()) for p in pypdf.PdfReader(f'{SPEECHES}/{wf}').pages]
wt = ' '.join(pages)
m = sent_around(wt, r'rose at a monthly rate of 0\.5 percent in September and 3\.7 percent over the previous 12 months')
q = sentence(wt, m)
pg = [i + 1 for i, p in enumerate(pages) if '3.7 percent over the previous 12 months' in p]
q2 = re.search(r'Core PCE inflation, excluding food and energy prices, rose 0\.3 percent in September and 3\.1 percent from that time last year\.', wt).group(0)
loc = f'PDF page {pg[0]} (pypdf page index), paragraph beginning "Let\'s just say it. September\'s inflation data were bad."'
V = 'Speech delivered 2026-11-10 (before Oct CPI), Waller, BoE Watchers conference'
sf = f'02_Research/External_views/Fed_officials_2026-11/speeches/{wf}'
add('c', 'Waller (Governor)', 'headline', 'Sep 2026 y/y % as stated', 3.7, 'as stated in speech; he also states m/m 0.5', q, loc, V, sf, '[O] opened (PDF text via pypdf)', BEA_H)
add('c', 'Waller (Governor)', 'core', 'Sep 2026 y/y % as stated', 3.1, 'as stated in speech; he also states m/m 0.3', q2, loc, V, sf, '[O] opened (PDF text via pypdf)', BEA_C)

def official(fn, name, pat_h, pat_c, venue):
    t = html_text(fn)
    sfp = f'02_Research/External_views/Fed_officials_2026-11/speeches/{fn}'
    if pat_h:
        m = sent_around(t, pat_h); add('c', name, 'headline', 'Sep 2026 y/y % as stated', float(re.search(r'(\d\.\d)', m.group(0)).group(1)), 'as stated in speech', sentence(t, m), 'HTML body text, sentence containing the figure', venue, sfp, '[O] opened (saved HTML)', BEA_H)
    else:
        add('c', name, 'headline', 'Sep 2026 y/y % as stated', None, 'not stated', '', '', venue, sfp, '[O] opened (saved HTML)')
    if pat_c:
        m = sent_around(t, pat_c); add('c', name, 'core', 'Sep 2026 y/y % as stated', float(re.search(r'(\d\.\d)', m.group(0)).group(1)), 'as stated in speech', sentence(t, m), 'HTML body text, sentence containing the figure', venue, sfp, '[O] opened (saved HTML)', BEA_C)
    else:
        n_core = len(re.findall(r'(?i)\bcore\b', t))
        add('c', name, 'core', 'Sep 2026 y/y % as stated', None, f'no core PCE figure in speech text (word "core" occurs {n_core} times)', '', '', venue, sfp, '[O] opened (saved HTML)')

official('2026-11-10_Logan_economic_monetary_policy_outlook.html', 'Logan (Dallas Fed)',
         r'the price index for personal consumption expenditures \(PCE\) rose 3\.6 percent', r'Core PCE inflation was 3\.1 percent over the 12 months through September', 'Speech 2026-11-10 (after Oct CPI that morning)')
official('2026-11-10_Paulson_economic_outlook.html', 'Paulson (Philadelphia Fed)',
         r'PCE inflation, the Fed\'s preferred measure, was 3\.6 percent over the 12 months ending in September', None, 'Speech 2026-11-10 (after Oct CPI that morning)')
official('2026-11-13_Jefferson_productivity_puzzles.html', 'Jefferson (Vice Chair)',
         r'The 12-month change in the personal consumption expenditures price index, the blue line in figure 6 , was 3\.6 percent in September', r'The 12-month change in core PCE inflation, which excludes volatile food and energy prices and is shown by the dashed red dashed line, was 3\.1 percent in September', 'Speech 2026-11-13')
cols = ['item', 'source', 'measure', 'metric', 'value', 'compare_to_bea_text', 'quote', 'location', 'vintage', 'source_file', 'verification', 'basis']
write_csv(f'{OUT}/A_r4_sep_check.csv', rows, cols)
for r in rows: print(r['item'], r['source'][:28], r['measure'], r['value'], '|', r['compare_to_bea_text'])
