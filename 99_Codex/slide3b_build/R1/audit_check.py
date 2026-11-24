from pathlib import Path
import sys,json,csv,math,datetime as D,zipfile,io,posixpath,xml.etree.ElementTree as E,hashlib
from openpyxl import load_workbook
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'audit_lib'));import xlrd
raw=R/'03_Data/pipelines/forecast_3b/raw/2026-11-16'
out={}
f=json.loads((raw/'PCEPILFE_observations.json').read_text());obs={o['date']:float(o['value']) for o in f['observations'] if o['value']!='.'}
quarters=['2025Q3','2025Q4','2026Q1','2026Q2','2026Q3']
means=[]
for q in quarters:
 y=int(q[:4]);m=(int(q[-1])-1)*3+1;means.append(sum(obs[f'{y}-{i:02d}-01'] for i in range(m,m+3))/3)
a=[100*((means[i]/means[i-1])**4-1) for i in range(1,5)];out['actuals']=dict(zip(quarters[1:],a));out['fred_realtime']=f.get('realtime_start')
s=load_workbook(raw/'medianLevel.xlsx',data_only=True)['COREPCE'];row=next(r for r in s.values if r[0:2]==(2026,4));base=list(row[3:8]);out['spf_row']=row;out['spf_headers']=list(next(s.values))
def steo(name):
 s=load_workbook(raw/name,data_only=True)['2tab'];years=[c.value for c in s[3]];months=[c.value for c in s[4]];vs=next([c.value for c in row] for row in s if row[0].value=='BREPUUS');y=None;result={}
 for j in range(2,len(years)):
  y=years[j] or y
  if months[j] in 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split() and isinstance(vs[j],(int,float)):
   result[D.date(int(y),'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split().index(months[j])+1,1)]=vs[j]
 return result
nov=steo('nov26_base.xlsx');feb=steo('feb26_base.xlsx')
x=xlrd.open_workbook(str(raw/'EIA_RBRTEd.xls'));s=x.sheet_by_name('Data 1');daily={xlrd.xldate_as_datetime(s.cell_value(i,0),x.datemode).date():float(s.cell_value(i,1)) for i in range(3,s.nrows) if s.cell_value(i,0) and isinstance(s.cell_value(i,1),(int,float))}
last=max(daily);cur=[v for d,v in daily.items() if d>=D.date(2026,10,1)];rem=[];d=last+D.timedelta(days=1)
while d<=D.date(2026,12,31):
 if d.weekday()<5 and d!=D.date(2026,12,25) and not(d.month==11 and d.weekday()==3 and 22<=d.day<=28):rem.append(d)
 d+=D.timedelta(days=1)
qs=['2026Q4','2027Q1','2027Q2','2027Q3','2027Q4'];ass=[]
for q in qs:
 y=int(q[:4]);m=(int(q[-1])-1)*3+1;ass.append(sum(nov[D.date(y,i,1)] for i in range(m,m+3))/3)
rs=[float(r['level_response_pct_per_10pct']) for r in csv.DictReader((R/'03_Data/pipelines/forecast_3b/config/regime_response.csv').open()) if r['regime']=='post']
out['oil_splice']={'last':str(last),'last_value':daily[last],'n_observed':len(cur),'n_remaining':len(rem),'observed_sum':sum(cur),'assumed':ass}
scens={'SPF median':base}
for name in ['Oil to $110','Hormuz reopens']:
 def mr(d):return 110 if name=='Oil to $110' else feb[D.date(d.year,d.month,1)]+25
 prices=[(sum(cur)+sum(mr(d) for d in rem))/(len(cur)+len(rem))]
 for q in qs[1:]:
  y=int(q[:4]);m=(int(q[-1])-1)*3+1;prices.append(sum(mr(D.date(y,i,1)) for i in range(m,m+3))/3)
 gaps=[100*math.log(p/b) for p,b in zip(prices,ass)];dg=[gaps[0]]+[gaps[i]-gaps[i-1] for i in range(1,5)];lev=[sum(rs[t-j]*dg[j]/10 for j in range(t+1)) for t in range(5)];prev=[0]+lev[:-1];scens[name]=[100*((1+b/100)*math.exp(4*(l-p)/100)-1) for b,l,p in zip(base,lev,prev)];out[name]={'prices':prices,'gaps':gaps,'levels':lev,'qq':scens[name]}
out['q4q4']={k:100*(math.prod((1+v/100)**.25 for v in vs[1:])-1) for k,vs in scens.items()}
w=load_workbook(R/'01_Finals/Slide data/Inflation Slide 3B.xlsx',data_only=True);wf=load_workbook(R/'01_Finals/Slide data/Inflation Slide 3B.xlsx',data_only=False)
import re
cache={}
def value(sheet,cell):
 key=(sheet,cell)
 if key in cache:return cache[key]
 v=wf[sheet][cell].value
 if isinstance(v,str) and v.startswith('='):
  expression=v[1:]
  if expression.startswith('TEXT('):return None
  expression=re.sub(r"(?:(\w+)!)?([A-Z]+[0-9]+)",lambda m: str(value(m[1] or sheet,m[2])),expression).replace('^','**')
  v=eval(expression,{"__builtins__":{}},{})
 cache[key]=v;return v
for i,val in enumerate(a,2):assert abs(value('Forecast',f'B{i}')-val)<1e-10
for col,(name,vals) in enumerate(scens.items(),3):
 for i,v in enumerate(vals,6):assert abs(value('Forecast',f'{chr(64+col)}{i}')-v)<6e-7
 assert abs(value('Q4Q4_2027',f'B{col-1}')-out['q4q4'][name])<6e-7
out['formulas']={s.title:{c.coordinate:c.value for row in s for c in row if c.data_type=='f'} for s in wf}
z=zipfile.ZipFile(R/'01_Finals/slides/Inflation Slides (working).pptx');ns={'c':'http://schemas.openxmlformats.org/drawingml/2006/chart','a':'http://schemas.openxmlformats.org/drawingml/2006/main'};slide=E.fromstring(z.read('ppt/slides/slide400.xml'));out['slide_text']=[t.text for t in slide.findall('.//a:t',ns)]
c=E.fromstring(z.read('ppt/charts/chart21.xml'));out['chart_series']=[]
for ser in c.findall('.//c:lineChart/c:ser',ns):
 name=ser.find('.//c:tx//c:v',ns).text;pts={int(pt.attrib['idx']):float(pt.find('c:v',ns).text) for pt in ser.findall('.//c:val//c:pt',ns)};col=['Actual','SPF median','Oil to $110','Hormuz reopens'].index(name)+2
 expected={i-2:value('Forecast',f'{chr(64+col)}{i}') for i in range(2,11) if wf['Forecast'].cell(i,col).value is not None};assert pts.keys()==expected.keys();assert all(abs(pts[i]-expected[i])<1e-10 for i in pts);out['chart_series'].append({'name':name,'points':pts})
rel=E.fromstring(z.read('ppt/charts/_rels/chart21.xml.rels'));target=next(x.attrib['Target'] for x in rel if x.attrib['Type'].endswith('/package'));emb=posixpath.normpath('ppt/charts/'+target);ew=load_workbook(io.BytesIO(z.read(emb)),data_only=True);out['embedded_workbook']={s.title:list(s.values) for s in ew}
z0=zipfile.ZipFile(R/'comparison/slide3a_final.pptx');changed=[n for n in z0.namelist() if n not in z.namelist() or z0.read(n)!=z.read(n)];out['prior_parts_changed']=changed;out['added_parts']=[n for n in z.namelist() if n not in z0.namelist()]
out['prior_slide_parts']=[n for n in z0.namelist() if n.startswith('ppt/slides/') and n.endswith('.xml')]
(R/'audit_results.json').write_text(json.dumps(out,indent=2,default=str));print(json.dumps({k:v for k,v in out.items() if k not in ['formulas','embedded_workbook','slide_text']},indent=2))
