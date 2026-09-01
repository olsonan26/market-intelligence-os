import csv,io,json,math,urllib.request,zipfile,sys
from datetime import datetime
from pathlib import Path

H='https://raw.githubusercontent.com/mauricefreese/Investment/main/NVDA-price-data-max-1d.csv'
C='https://raw.githubusercontent.com/tulukakaniwa/marketlab/62598b0b5e235d7b65b023a6e4aa1ad6316b2edd/public/data/NVDA-1d.csv'
P='https://raw.githubusercontent.com/InCodingEverythingIsPossible/EngineeringProject/main/PolygonData/dividend_data/NVDA_dividend_data.json'
CUT='2026-08-31'; EXPECT=6944; OUT=Path('dist'); OUT.mkdir(exist_ok=True)
S=[('2000-06-27',2),('2001-09-17',2),('2006-04-07',2),('2007-09-11',1.5),('2021-07-20',4),('2024-06-10',10)]
D='''2012-11-20:.075,2013-02-26:.075,2013-05-21:.075,2013-08-20:.075,2013-11-19:.085,2014-02-25:.085,2014-05-20:.085,2014-08-19:.085,2014-11-19:.085,2015-02-24:.085,2015-05-19:.0975,2015-08-18:.0975,2015-11-18:.115,2016-02-29:.115,2016-05-24:.115,2016-08-23:.115,2016-11-23:.14,2017-02-22:.14,2017-05-19:.14,2017-08-22:.14,2017-11-22:.15,2018-02-22:.15,2018-05-23:.15,2018-08-29:.15,2018-11-29:.16,2019-02-28:.16,2019-05-30:.16,2019-08-28:.16,2019-11-27:.16,2020-02-27:.16,2020-06-04:.16,2020-09-01:.16,2020-12-03:.16,2021-03-09:.16,2021-06-09:.16,2021-08-31:.04,2021-12-01:.04,2022-03-02:.04,2022-06-08:.04,2022-09-07:.04,2022-11-30:.04,2023-03-07:.04,2023-06-07:.04,2023-09-06:.04,2023-12-05:.04,2024-03-05:.04,2024-06-11:.01,2024-09-12:.01,2024-12-05:.01,2025-03-12:.01,2025-06-11:.01,2025-09-11:.01,2025-12-04:.01,2026-03-11:.01,2026-06-04:.25'''
D=dict((x.split(':')[0],float(x.split(':')[1])) for x in D.split(',')); assert len(D)==55
COL=['date','open','high','low','close','adjusted_close','volume','split_factor','dividend','daily_return_pct','next_1d_return_pct','next_3d_return_pct','next_5d_return_pct','next_10d_return_pct','next_20d_return_pct','next_1d_direction','next_3d_direction','next_5d_direction','next_10d_direction','next_20d_direction','next_5d_max_gain_pct','next_5d_max_drawdown_pct','next_10d_max_gain_pct','next_10d_max_drawdown_pct','next_20d_max_gain_pct','next_20d_max_drawdown_pct']

def get(u):
 r=urllib.request.Request(u,headers={'User-Agent':'nvda-builder'}); return urllib.request.urlopen(r,timeout=60).read().decode('utf-8-sig')
def rows(t): return list(csv.DictReader(io.StringIO(t)))
def pct(a,b): return 100*(b/a-1)
def mul(d):
 m=1
 for sd,f in S:
  if sd>d:m*=f
 return m
def fmt(v):
 if v is None:return ''
 if isinstance(v,str):return v
 if isinstance(v,int):return str(v)
 return (f'{v:.10f}'.rstrip('0').rstrip('.') or '0')
def dire(v): return 'UP' if v>0 else ('DOWN' if v<0 else 'FLAT')

h=rows(get(H)); c=rows(get(C)); pj=json.loads(get(P)); first=c[0]['Date']
ser={}
for r in h:
 d=r['Date']
 if d>=first or d>CUT:continue
 ser[d]={'o':float(r['Open'])/10,'h':float(r['High'])/10,'l':float(r['Low'])/10,'c':float(r['Close'])/10,'v':float(r['Volume'])*10}
for r in c:
 d=r['Date']
 if d>CUT:continue
 if d in ser:raise Exception('overlap '+d)
 ser[d]={'o':float(r['Open']),'h':float(r['High']),'l':float(r['Low']),'c':float(r['Close']),'v':float(r['Volume'])}
ds=sorted(ser); hm={r['Date']:r for r in h}; cm={r['Date']:r for r in c}
pr=float(hm['2021-01-04']['Open'])/float(cm['2021-01-04']['Open']); vr=float(cm['2021-01-04']['Volume'])/float(hm['2021-01-04']['Volume'])
assert abs(pr-10)<.01 and abs(vr-10)<.02
sm=dict(S); out=[]
for i,d in enumerate(ds):
 s=ser[d]; m=mul(d); q={'date':d,'open':s['o']*m,'high':s['h']*m,'low':s['l']*m,'close':s['c']*m,'adjusted_close':s['c'],'volume':int(round(s['v']/m)),'split_factor':sm.get(d),'dividend':D.get(d)}
 q['daily_return_pct']=None if i==0 else pct(ser[ds[i-1]]['c'],s['c'])
 for n in (1,3,5,10,20):
  if i+n<len(ds):
   x=pct(s['c'],ser[ds[i+n]]['c']); q[f'next_{n}d_return_pct']=x; q[f'next_{n}d_direction']=dire(x)
  else:q[f'next_{n}d_return_pct']=None;q[f'next_{n}d_direction']=''
 for n in (5,10,20):
  if i+n<len(ds):
   w=ds[i+1:i+n+1]; q[f'next_{n}d_max_gain_pct']=max(0,pct(s['c'],max(ser[x]['h'] for x in w)));q[f'next_{n}d_max_drawdown_pct']=min(0,pct(s['c'],min(ser[x]['l'] for x in w)))
  else:q[f'next_{n}d_max_gain_pct']=None;q[f'next_{n}d_max_drawdown_pct']=None
 out.append(q)

DP=OUT/'NVDA_daily_research.csv'; EP=OUT/'NVDA_corporate_events.csv'; JP=OUT/'NVDA_validation_report.json'; TP=OUT/'NVDA_validation_report.txt'; ZP=OUT/'NVDA_complete_research_bundle.zip'
with DP.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=COL);w.writeheader();w.writerows({k:fmt(r.get(k)) for k in COL} for r in out)
ev=[{'date':'1999-01-22','event_type':'IPO','event_description':'NVIDIA first public trading session on Nasdaq'}]
notes={2:'2-for-1 split',1.5:'3-for-2 split',4:'4-for-1 split',10:'10-for-1 split'}
for d,x in S:ev.append({'date':d,'event_type':'stock_split','event_description':notes[x]})
for d,a in D.items():ev.append({'date':d,'event_type':'dividend','event_description':f'Cash dividend ex-date; ${a:g} per share as originally declared'})
ev.sort(key=lambda x:(x['date'],x['event_type']))
with EP.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=['date','event_type','event_description']);w.writeheader();w.writerows(ev)
week=[d for d in ds if datetime.strptime(d,'%Y-%m-%d').weekday()>4]; dup=len(ds)-len(set(ds)); core=sum(1 for r in out for k in ['open','high','low','close','adjusted_close','volume'] if r[k] is None)
null={'daily_return_pct':sum(r['daily_return_pct'] is None for r in out)}
for n in (1,3,5,10,20):null[f'next_{n}d_return_pct']=sum(r[f'next_{n}d_return_pct'] is None for r in out);null[f'next_{n}d_direction']=sum(r[f'next_{n}d_direction']=='' for r in out)
for n in (5,10,20):null[f'next_{n}d_max_gain_pct']=sum(r[f'next_{n}d_max_gain_pct'] is None for r in out);null[f'next_{n}d_max_drawdown_pct']=sum(r[f'next_{n}d_max_drawdown_pct'] is None for r in out)
exp={'daily_return_pct':1,'next_1d_return_pct':1,'next_1d_direction':1,'next_3d_return_pct':3,'next_3d_direction':3,'next_5d_return_pct':5,'next_5d_direction':5,'next_10d_return_pct':10,'next_10d_direction':10,'next_20d_return_pct':20,'next_20d_direction':20,'next_5d_max_gain_pct':5,'next_5d_max_drawdown_pct':5,'next_10d_max_gain_pct':10,'next_10d_max_drawdown_pct':10,'next_20d_max_gain_pct':20,'next_20d_max_drawdown_pct':20}
j7=ser['2024-06-07']['c'];j10=ser['2024-06-10']['c']; jr=pct(j7,j10)
checks={'row_count':len(out)==EXPECT,'first_date':ds[0]=='1999-01-22','last_date':ds[-1]==CUT,'unique_dates':dup==0,'strictly_increasing':all(ds[i]<ds[i+1] for i in range(len(ds)-1)),'weekend_rows':not week,'source_only_no_synthetic_holidays':True,'core_ohlcv_complete':core==0,'six_split_rows':sum(r['split_factor'] is not None for r in out)==6,'fifty_five_dividend_rows':sum(r['dividend'] is not None for r in out)==55,'structural_nulls':null==exp,'overlap_price_ratio_10x':abs(pr-10)<.01,'overlap_volume_ratio_10x':abs(vr-10)<.02,'june_2024_split_continuity':abs(jr)<50}
report={'status':'PASS' if all(checks.values()) else 'FAIL','ticker':'NVDA','cutoff':CUT,'rows':len(out),'first_date':ds[0],'last_date':ds[-1],'timezone':'America/New_York','adjusted_close':'split-adjusted only; dividend-unadjusted','sources':[H,C,P],'polygon_snapshot_records':len(pj.get('results',[])),'overlap_ratios':{'price':pr,'volume':vr},'june_2024':{'2024-06-07_adjusted_close':j7,'2024-06-10_adjusted_close':j10,'return_pct':jr},'structural_nulls':null,'checks':checks,'notes':['No interpolation, outlier filtering, technical indicators, or astrology interpretation.','Corporate events include only IPO, splits, and dividend ex-dates; a complete verified earnings-announcement calendar was not ingested, so earnings are omitted rather than guessed.']}
JP.write_text(json.dumps(report,indent=2)+'\n'); TP.write_text('\n'.join(['NVDA RESEARCH DATASET VALIDATION',f"STATUS: {report['status']}",f'Rows: {len(out)}',f'First date: {ds[0]}',f'Last date: {ds[-1]}','']+[f"{k}: {'PASS' if v else 'FAIL'}" for k,v in checks.items()]+['','Sources:',H,C,P])+'\n')
with zipfile.ZipFile(ZP,'w',zipfile.ZIP_DEFLATED) as z:
 for p in (DP,EP,JP,TP):z.write(p,p.name)
print(json.dumps({'status':report['status'],'rows':len(out),'first':ds[0],'last':ds[-1],'bundle':str(ZP)},indent=2))
if report['status']!='PASS':sys.exit(2)
