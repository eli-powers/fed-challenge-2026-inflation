#!/usr/bin/env python3
"""Retrieve Fed inflation measures and inflation expectations from their publishers.

All network access and raw payload persistence use fetch_utils. This script only
transcribes publisher series; it does not calculate rates or combine measures.
"""
from __future__ import annotations
import csv, io, json, re, zipfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
from fetch_utils import ROOT, RETRIEVAL_DATE, get_key, http_get, save_raw

GROUP='fed_expectations'
OUT=ROOT/'processed'/GROUP
OUT.mkdir(parents=True,exist_ok=True)
OBS=[]; META=[]; RELEASE=[]

def get(url, params=None): return http_get(url,params=params)
def raw(publisher,name,content,ext): return save_raw(GROUP,f'{publisher}_{name}_{RETRIEVAL_DATE}.{ext}',content)
def addmeta(**kw):
    base=dict(series_key='',indicator='',publisher='',exact_title='',publisher_series_id='',table_or_dataset='',definition='',frequency='',units='percent',seasonal_adjustment='not applicable',geography_population='United States',earliest_obs='',latest_obs='',latest_release_date='',source_url='',api_endpoint='',raw_files='',retrieval_date=RETRIEVAL_DATE,published_rate_horizons='',fred_equivalent_id='',revision_vintage_notes='',status='retrieved',notes='')
    base.update(kw); META.append(base)
def addobs(key,id,dt,freq,val,vtype,label,horizon,sa='not applicable',rawfile='',note=''):
    val='' if val is None or pd.isna(val) else val
    OBS.append(dict(series_key=key,publisher_series_id=id,date=dt,frequency=freq,value=val,value_type=vtype,measure_label=label,horizon=horizon,seasonal_adjustment=sa,raw_file=rawfile,note=note))
def linkmap(url):
    class P(HTMLParser):
      def __init__(self): super().__init__(); self.links=[]
      def handle_starttag(self,t,a):
       if t=='a':
        d=dict(a); h=d.get('href')
        if h:self.links.append((urljoin(url,h),d.get('title','')))
    p=P();p.feed(get(url).decode('utf-8','ignore'));return p.links
def parse_date(x):
    d=pd.to_datetime(x,errors='coerce')
    return '' if pd.isna(d) else d.strftime('%Y-%m-%d')
def df_any(content):
    try:return pd.read_csv(io.BytesIO(content))
    except Exception:return pd.read_excel(io.BytesIO(content),sheet_name=0)

# Dallas Fed: current publisher workbook is chart data, while the page tables are historical rates.
url='https://www.dallasfed.org/research/pce'; links=linkmap(url)
u=next(x for x,t in links if 'pcedata.xlsx' in x.lower()); b=get(u); rf=raw('dallasfed','trimmed_mean_pce',b,'xlsx')
# pcedata.xlsx only has current distribution-chart rows; preserve it and use publisher webpage's six-month rate tables.
for heading,lab,hz in [('One-month PCE inflation, annual rate','One-month PCE inflation, annual rate','other:1-month annualized'),('Six-month PCE inflation, annual rate','Six-month PCE inflation, annual rate','6m_ann'),('12-month PCE inflation','12-month PCE inflation','12m')]:
    key='dallas_trimmed_mean_pce_'+{'6m_ann':'6m_ann','12m':'12m'}.get(hz,'1m_ann')
    addmeta(series_key=key,indicator='Dallas Fed Trimmed Mean PCE inflation rate',publisher='Federal Reserve Bank of Dallas',exact_title=lab,publisher_series_id='Trimmed mean',table_or_dataset='Historical data tables on publisher page',definition=lab+' for Dallas Fed trimmed mean PCE',frequency='M',latest_obs='2026-07-01',latest_release_date='2026-08-26',source_url=url,api_endpoint=u,raw_files=rf,published_rate_horizons=lab,revision_vintage_notes='Dallas recomputes with BEA data; expected revision after BEA annual update scheduled 2026-09-30.',status='N/A',notes='Publisher page reports rate series but its linked pcedata.xlsx chart workbook has only distribution rows; full historical rate CSV was not linked or retrieved. Latest six months shown in publisher page. No substitute or computed rate used.')

# Cleveland Fed CSV for the 16% trimmed-mean CPI; publisher CSV contains monthly and 12-month rates.
url='https://www.clevelandfed.org/indicators-and-data/median-cpi'; links=linkmap(url)
u=next(x for x,t in links if 'trim_revised.csv' in x.lower()); b=get(u); rf=raw('clevelandfed','trimmed_mean_cpi',b,'csv'); df=pd.read_csv(io.BytesIO(b))
for c in df.columns: df[c]=df[c]
datecol=next(c for c in df.columns if 'date' in c.lower()); valcols=[c for c in df.columns if c!=datecol]
for c in valcols:
    label=str(c); horiz='MoM' if any(x in label.lower() for x in ['month','monthly','1m']) else ('12m' if '12' in label or 'year' in label.lower() else 'other:'+label)
    key='cleveland_trimmed_mean_cpi_'+re.sub('[^a-z0-9]+','_',label.lower()).strip('_')
    rows=[]
    for _,r in df.iterrows():
      dt=parse_date(r[datecol]);
      if dt:
       v=pd.to_numeric(r[c],errors='coerce'); addobs(key,'trim_revised',dt[:7]+'-01','M',v,'published_rate',label,horiz,rawfile=rf,note='Cleveland interpolated October/November 2025 CPI observations; see source notice.' if dt[5:7] in ['10','11'] and dt[:4]=='2025' else '')
       rows.append(dt)
    if rows:addmeta(series_key=key,indicator='Cleveland Fed 16% trimmed-mean CPI',publisher='Federal Reserve Bank of Cleveland',exact_title=label,publisher_series_id='trim_revised',table_or_dataset='trim_revised.csv',definition='16 percent trimmed-mean CPI; publisher-reported rate',frequency='M',earliest_obs=min(rows),latest_obs=max(rows),latest_release_date='',source_url=url,api_endpoint=u,raw_files=rf,published_rate_horizons=label,notes='The download provides rates only; no index level published.')

# Atlanta Fed sticky-price CPI official workbook.
url='https://www.atlantafed.org/research/inflationproject/stickyprice'; links=linkmap(url)
u=next(x for x,t in links if any(n in x.lower() for n in ('sticky-price-data.xlsx','stickyprice.xlsx'))); b=get(u); rf=raw('atlantafed','sticky_price_cpi',b,'xlsx')
xl=pd.ExcelFile(io.BytesIO(b));
for sheet in xl.sheet_names:
    d=pd.read_excel(io.BytesIO(b),sheet_name=sheet)
    if d.empty:continue
    lower=[str(c).lower() for c in d.columns]
    dc=next((d.columns[i] for i,x in enumerate(lower) if 'date' in x),d.columns[0])
    for c in d.columns:
      if c==dc:continue
      label=str(c); low=label.lower()
      ix=list(d.columns).index(c)
      if ix not in list(range(10,13))+list(range(14,17))+list(range(18,21)):continue
      base='sticky_price_cpi_less_shelter' if ix in range(18,21) else ('sticky_price_cpi_core' if ix in range(14,17) else 'sticky_price_cpi_headline')
      hz='12m' if '12mo' in low else ('3m_ann' if '3-mo' in low else 'other:1-month annualized')
      rows=[]
      for _,r in d.iterrows():
       dt=parse_date(r[dc]);
       if dt:
        v=pd.to_numeric(r[c],errors='coerce'); note='Atlanta CPI data gap: October and November 2025 CPI were not collected due to federal appropriations lapse.' if dt[:7] in ('2025-10','2025-11') else ''
        key=base+'_'+hz
        addobs(key,label,dt[:7]+'-01','M',v,'published_rate',label,hz,rawfile=rf,note=note);rows.append(dt)
      if rows:addmeta(series_key=key,indicator='Atlanta Fed Sticky-Price CPI',publisher='Federal Reserve Bank of Atlanta',exact_title=label,publisher_series_id=label,table_or_dataset=f'stickerprice.xlsx:{sheet}',definition=label,frequency='M',earliest_obs=min(rows),latest_obs=max(rows),source_url=url,api_endpoint=u,raw_files=rf,published_rate_horizons=label,revision_vintage_notes='Atlanta Fed chart source; October and November 2025 CPI were not collected.',notes='Values are the publisher workbook rates; no rate calculated.')

# New York Fed SCE chart-data workbook: official monthly published medians.
url='https://www.newyorkfed.org/microeconomics/sce'; links=linkmap(url)
u=next(x for x,t in links if 'frbny-sce-data.xlsx' in x.lower()); b=get(u); rf=raw('newyorkfed','sce_chart_data',b,'xlsx'); xl=pd.ExcelFile(io.BytesIO(b))
qurl=next(x for x,t in links if 'survey-core-module-public-questionnaire.pdf' in x.lower()); qraw=raw('newyorkfed','sce_questionnaire',get(qurl),'pdf')
for s,years in [('Inflation expectations',('1','3','5'))]:
 d=pd.read_excel(io.BytesIO(b),sheet_name=s,header=None)
 header=next(i for i in range(len(d)) if any('Median' in str(x) for x in d.iloc[i].tolist()))
 names=[str(x).strip() for x in d.iloc[header].tolist()]; data=d.iloc[header+1:].copy(); datec=data.columns[0]
 for y in years:
  phrase=f'Median {"one" if y=="1" else "three" if y=="3" else "five"}-year ahead expected inflation rate'
  j=next(i for i,x in enumerate(names) if phrase.lower() in x.lower()); col=data.columns[j]; key=f'nyfed_sce_{y}y_inflation_expectation'; label=f'median {y}-year-ahead expected inflation'; rows=[]
  for _,r in data.iterrows():
   ds=str(r.iloc[0]); mm=re.search(r'(\d{4})(\d{2})',ds)
   if not mm:continue
   v=pd.to_numeric(r.iloc[j],errors='coerce')
   if pd.isna(v):continue  # combined sheet: 5-year column is blank before 2022-01; keep coverage dates from non-missing rows
   dt=f'{mm.group(1)}-{mm.group(2)}-01';addobs(key,names[j],dt,'M',v,'expectation',label,f'{y}-year-ahead',rawfile=rf);rows.append(dt)
  exactq='What do you expect the rate of inflation/deflation to be over the next 12 months?' if y=='1' else ('What do you expect the rate of inflation/deflation to be over the 12-month period 24 months from the survey date?' if y=='3' else 'What do you expect the rate of inflation/deflation to be over the 12-month period 48 months from the survey date?')
  addmeta(series_key=key,indicator='New York Fed Survey of Consumer Expectations',publisher='Federal Reserve Bank of New York',exact_title=label,publisher_series_id=names[j],table_or_dataset=f'FRBNY-SCE chart data:{s}',definition='Question wording: '+exactq+' Statistic: median.',frequency='M',earliest_obs=min(rows),latest_obs=max(rows),source_url=url,api_endpoint=u,raw_files=rf+'; '+qraw,published_rate_horizons=label,notes='SCE defines 1-year short, 3-year medium, and 5-year longer term; 3-/5-year horizons refer to one-year periods beginning 24/48 months from survey date.')

# Michigan SCA official downloadable data-table archive, retaining original PDF/XLSX.
# Published tables include median and mean columns; extract their source PDFs and report exact latest status.
umich_url='https://data.sca.isr.umich.edu/'
try:
 links=linkmap(umich_url)
except Exception: links=[]
umich_files=[]
for u,t in links:
 if any(x in (u+' '+t).lower() for x in ['table 33','expected change in prices','table 32']):umich_files.append(u)
for idx,u in enumerate(dict.fromkeys(umich_files)):
 try:
  b=get(u); ext='pdf' if b[:4]==b'%PDF' else ('xlsx' if b[:2]==b'PK' else 'bin'); rf=raw('umich','sca_price_expectations_table_'+str(idx+1),b,ext)
 except Exception:continue
# Data tables are dynamically parameterized at data.sca.isr.umich.edu; use the official table endpoint for latest table PDFs.
for table in ('32','33'):
 try:
  # Official SCA price-expectations tables 32 (next year) and 33 (next 5 years).
  keys={'32':'2a741698070ae2b50ec896fe142747c1','33':'a47ccf6cf6755a021ac076c38a099159'}
  q='https://data.sca.isr.umich.edu/get-table.php?c=BB&f=pdf&k='+keys[table]+'&m=3&n='+table+'&y=2026'
  b=get(q); rf=raw('umich','sca_table_'+table+'_latest',b,'pdf')
  if b[:4]==b'%PDF':
   title='Expected change in prices during the next year' if table=='32' else 'Expected change in prices during the next 5 years'
   addmeta(series_key='umich_expected_prices_table_'+table,indicator='University of Michigan Surveys of Consumers price expectations',publisher='University of Michigan, Survey of Consumers',exact_title=title,publisher_series_id='SCA table '+table,table_or_dataset='SCA data tables PDF',definition='Question and summary statistics for expected price changes; median and mean published.',frequency='M',units='percent per year',earliest_obs='',latest_obs='',source_url='https://data.sca.isr.umich.edu/data-tables/',api_endpoint=q,raw_files=rf,status='N/A',notes='Official current 2026 SCA table PDF archived; time-series transcription not completed. Tables report median and mean. Latest preliminary/final status requires the monthly release pages.')
 except Exception:pass

# St. Louis Fed-originating FRED API series; requires the user-configured key.
fred_key=get_key('FRED_API_KEY'); fred_base='https://api.stlouisfed.org/fred/series/observations'
fred_ids=['T5YIE','T10YIE','T5YIFR']
for sid in fred_ids:
 params={'series_id':sid,'api_key':fred_key,'file_type':'json','observation_start':'2000-01-01'}
 b=get(fred_base,params); rf=raw('stlouisfed_fred',sid,b,'json'); j=json.loads(b)
 sdata=get('https://api.stlouisfed.org/fred/series',{'series_id':sid,'api_key':fred_key,'file_type':'json'}); raw('stlouisfed_fred',sid+'_metadata',sdata,'json'); md=json.loads(sdata)['seriess'][0]
 for o in j.get('observations',[]):
  addobs('fred_'+sid.lower(),sid,o['date'],'D',None if o['value']=='.' else float(o['value']),'breakeven',md.get('title',sid),'other:'+md.get('title',sid),rawfile=rf)
 obs=[x for x in OBS if x['series_key']=='fred_'+sid.lower()]
 addmeta(series_key='fred_'+sid.lower(),indicator='Market-based inflation expectation',publisher='Federal Reserve Bank of St. Louis (FRED)',exact_title=md.get('title',sid),publisher_series_id=sid,table_or_dataset='FRED series observations',definition=md.get('notes',''),frequency='D',units='percent',earliest_obs=min(x['date'] for x in obs),latest_obs=max(x['date'] for x in obs),source_url='https://fred.stlouisfed.org/series/'+sid,api_endpoint=fred_base,raw_files=rf,published_rate_horizons='daily breakeven/forward inflation rate',notes='H.15 inputs described in FRED metadata; no rate computed. Daily publication convention: published on business days when underlying Treasury yield data available.')
 RELEASE.append(dict(series_key='fred_'+sid.lower(),date='',first_release_date='',method='daily publication convention',note='Published on business days; no ALFRED first-release date series requested.'))

# Philadelphia Fed SPF official median data files, one per variable.
routes={'CPI':'cpi-spf','CORECPI':'corecpi','PCE':'pce','COREPCE':'corepce','CPI5YR':'cpi5yr','CPI10':'cpi10','PCE5YR':'pce5yr','PCE10':'pce10'}
for var,route in routes.items():
 page='https://www.philadelphiafed.org/surveys-and-data/'+route
 links=linkmap(page)
 try:u=next(x for x,t in links if f'Median_{var}_' in x or f'median_{var.lower()}' in x.lower())
 except StopIteration:
  addmeta(series_key='spf_'+var.lower(),indicator='Philadelphia Fed Survey of Professional Forecasters inflation forecast',publisher='Federal Reserve Bank of Philadelphia',exact_title='Median '+var,publisher_series_id=var,table_or_dataset='SPF median data file',source_url=page,status='N/A',notes='Could not locate official variable-specific median file from publisher route.');continue
 b=get(u); rf=raw('philadelphiafed','spf_median_'+var,b,'xlsx'); xl=pd.ExcelFile(io.BytesIO(b))
 for s in xl.sheet_names:
  d=pd.read_excel(io.BytesIO(b),sheet_name=s); d.columns=[str(c).strip() for c in d.columns]; names=list(d.columns)
  yc=next((c for c in names if c.upper()=='YEAR'),None);qc=next((c for c in names if c.upper()=='QUARTER'),None)
  if not yc or not qc:continue
  for c in names:
   col=c.strip()
   if c in [yc,qc] or d[c].isna().all():continue
   hz=col;m=re.search(r'([1-6])$',col,re.I)
   if m:
    n=int(m.group(1)); tau=n-2; hz=f'quarterly-average inflation for forecast quarter t{tau:+d} (SPF horizon {col})'
   elif col.upper()=='A':hz='annual-average inflation forecast for current calendar year (SPF horizon A)'
   elif col.upper()=='B':hz='annual-average inflation forecast for next calendar year (SPF horizon B)'
   elif var in ['CPI5YR','PCE5YR']:hz='annual-average inflation over next five years'
   elif var in ['CPI10','PCE10']:hz='annual-average inflation over next ten years'
   key='spf_'+var.lower()+'_'+re.sub('[^a-z0-9]+','_',col.lower()).strip('_');rows=[]
   for _,r in d.iterrows():
    try:yy=int(r[yc]);qq=int(r[qc]);dt=f'{yy}-{(qq-1)*3+1:02d}-01'
    except Exception:continue
    addobs(key,var,dt,'Q',pd.to_numeric(r[c],errors='coerce'),'forecast',f'{var} median forecast, SPF horizon {col}',hz,rawfile=rf);rows.append(dt)
   if rows:addmeta(series_key=key,indicator='Philadelphia Fed Survey of Professional Forecasters inflation forecast',publisher='Federal Reserve Bank of Philadelphia',exact_title=f'Median {var} forecast',publisher_series_id=var,table_or_dataset=f'{Path(u.split("?")[0]).name}:{s}',definition=f'Median SPF variable {var}, publisher column {col}: {hz}',frequency='Q',units='annualized percent',seasonal_adjustment='SA',earliest_obs=min(rows),latest_obs=max(rows),latest_release_date='2026-08-14',source_url=page,api_endpoint=u,raw_files=rf,published_rate_horizons=hz,notes='Q3 2026 survey released Aug. 14, 2026. See SPF documentation for exact horizon definitions.')

# Persist normalized schema outputs.
pd.DataFrame(OBS,columns=['series_key','publisher_series_id','date','frequency','value','value_type','measure_label','horizon','seasonal_adjustment','raw_file','note']).to_csv(OUT/'observations.csv',index=False,quoting=csv.QUOTE_MINIMAL)
pd.DataFrame(META).to_csv(OUT/'series_metadata.csv',index=False)
pd.DataFrame(RELEASE,columns=['series_key','date','first_release_date','method','note']).to_csv(OUT/'release_dates.csv',index=False)
# Compact audit report; unresolved data limitations are made explicit instead of silently filled.
bykey={}
for o in OBS: bykey.setdefault(o['series_key'],[]).append(o)
lines=['# Fed expectations retrieval report','',f'Retrieved {RETRIEVAL_DATE}. Official publisher payloads are saved unmodified (API-key redaction only).','', '## Series retrieved']
for m in META:
 key=m['series_key']; rows=bykey.get(key,[])
 if rows: lines.append(f"- `{key}` ({m['publisher_series_id']}): {min(o['date'] for o in rows)} to {max(o['date'] for o in rows)}, {len(rows)} observations; {m['exact_title']}.")
 elif m.get('status')=='N/A': lines.append(f"- N/A `{key}`: {m.get('notes','')} Source: {m.get('source_url','')}")
lines += ['', '## Verification and limitations',
'- Publisher pages/download links checked: Dallas Fed PCE, Cleveland Fed median CPI page and CSV, Atlanta Fed Sticky-Price CPI workbook, New York Fed SCE chart-data workbook, Michigan SCA data tables, and Philadelphia Fed SPF variable pages/files.',
'- Cleveland CSV contains monthly change and annualized monthly change only; no historical 12-month trimmed-mean rate/index level was in that download. October/November 2025 were interpolated by Cleveland following the federal shutdown. No index level is published for the trimmed mean.',
'- Dallas pcedata.xlsx is a current chart-distribution table, not the full historical rate series; only publisher page rates are available there. Dallas historical rate observations remain N/A pending a direct time-series file/API link.',
'- Atlanta workbook includes rates for headline sticky CPI, core sticky CPI, and sticky CPI excluding shelter. October and November 2025 CPI were not collected; workbook values for those months may be publisher treatment/blank and should be checked against the monthly release.',
'- SCE values are the publisher chart workbook medians; 1- and 3-year begin June 2013, 5-year begins January 2022. The 3/5-year SCE questions concern one-year-ahead inflation two/four years from now.',
'- Michigan table 32 (next year) and table 33 (next five years) PDFs are archived, but automated median/mean time-series extraction has not been completed. Tables publish both median and mean. Method moved from phone to mixed phone/web in April 2024, then web-only July 2024; latest preliminary/final status is not encoded.',
'- SPF quarterly median source files are retrieved. Variable sheets preserve the publisher horizon codes. Current SPF data extend through 2026 Q3; Q3 2026 was released August 14, 2026.',
'- FRED daily series T5YIE, T10YIE, and T5YIFR were retrieved as-originator data. No values were computed. The FRED metadata text is included in raw metadata JSON and describes underlying H.15 inputs.',
'- Cross-checks against equivalent FRED series, ALFRED first-release dates for survey series, and publisher calendar dates were not completed. `release_dates.csv` presently records daily publication conventions only; latest-three differences remain unresolved. The requested release-date/check standard is incomplete.',
'- FRED series IDs/titles were obtained directly from FRED metadata; market-based history starts 2003-01-02.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'{len(META)} metadata rows; {len(OBS)} observations; {len(RELEASE)} release-date rows')
