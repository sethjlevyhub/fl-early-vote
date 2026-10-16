#!/usr/bin/env python3
"""Georgia absentee + advance in-person voting from the official SOS statewide absentee voter file (mvp.sos.ga.gov,
'11/3/2026 General and Special Elections'), downloaded by hand into /workspace/ga-earlyvote/raw/ (bot check blocks automation).
Uses STATEWIDE.csv only (the zip also holds per-county copies). Counts ballots with Ballot Status A (accepted) and a return date.
Race/age: the SOS file has none; unofficial georgiavotes.com summaries captured by capture_ga.py. -> site/ga-data.csv + ga-data.js"""
import csv,io,zipfile,glob,os,json,datetime as dt,collections
ROOT=os.path.dirname(os.path.abspath(__file__)); GA='/workspace/ga-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
EV1={2018:dt.date(2018,10,15),2022:dt.date(2022,10,17),2024:dt.date(2024,10,15),2026:dt.date(2026,10,13)}
Z=sorted(glob.glob(GA+'/raw/A-*.zip'),key=os.path.getmtime)[-1]; zf=zipfile.ZipFile(Z); zi=zf.getinfo('STATEWIDE.csv')
asof=dt.datetime(*zi.date_time)
FILES={2018:(GA+'/past/GA-2018-general.zip','November 6, 2018 General/Special Election'),2022:(GA+'/past/A-12054.zip','November 8, 2022 General Election'),
       2024:(GA+'/past/A-12311.zip','November 5, 2024 General Election'),2026:(Z,'November 3, 2026 General and Special Elections')}
INP={'EARLY IN-PERSON','IN PERSON'}  # 2018 file labels styles IN PERSON / MAIL IN
def agg(y,path):
    """Same acceptance logic every year: Ballot Status A with a return date, STATEWIDE.csv only. Past files are final, so ballots
    later rejected/cancelled are excluded there; 2026 status is as of the file date. Cached per zip."""
    cp=GA+'/past/cache_%d.json'%y
    if y!=2026 and os.path.exists(cp) and os.path.getmtime(cp)>os.path.getmtime(path): return json.load(open(cp))
    day=collections.defaultdict(lambda:[0,0]); cty=collections.defaultdict(collections.Counter); end=asof.date() if y==2026 else ED[y]
    for r in csv.DictReader(io.TextIOWrapper(zipfile.ZipFile(path).open('STATEWIDE.csv'),encoding='latin-1')):
        if r['Ballot Status']!='A' or not r['Ballot Return Date']: continue
        try: d=dt.datetime.strptime(r['Ballot Return Date'],'%m/%d/%Y').date()
        except ValueError: continue
        if d>=end or (ED[y]-d).days>60: continue   # early period only (before Election Day; 2026 before the file date)
        i=(ED[y]-d).days; day[i][0 if r['Ballot Style'] in INP else 1]+=1; cty[i][r['County'] or '?']+=1
    o=dict(day={str(k):v for k,v in day.items()},cty={str(k):dict(v) for k,v in cty.items()})
    if y!=2026: json.dump(o,open(cp,'w'))
    return o
rows=[];CTY={}
for y,(path,ename) in FILES.items():
    A=agg(y,path); ci=cm=0; cc=collections.Counter()
    for i in range(60,0,-1):
        v=A['day'].get(str(i),[0,0]); ci+=v[0]; cm+=v[1]; cc.update(A['cty'].get(str(i),{}))
        d=ED[y]-dt.timedelta(i)
        if y==2026 and d>=asof.date(): break
        if i<=45: rows.append(dict(year=y,date=d.isoformat(),days_out=i,ev_day=(d-EV1[y]).days+1 if d>=EV1[y] else None,inperson_day=v[0],mail_day=v[1],
            inperson_cum=ci,mail_cum=cm,total_cum=ci+cm,rounded=0,source=f'Georgia SOS statewide absentee voter file, {ename} ({os.path.basename(path)}, STATEWIDE.csv)'))
        CTY.setdefault(y,{})[i]=dict(cc)
R26=[r for r in rows if r['year']==2026]; D26=R26[-1]['days_out']; N26=R26[-1]['ev_day']
def cty_at(y,i): return CTY[y].get(i,{})
top=[c for c,_ in collections.Counter(cty_at(2026,D26)).most_common(12)]
cmp_cty=[dict(county=c,v26=cty_at(2026,D26).get(c,0),**{f'v{y}':cty_at(y,D26).get(c,0) for y in (2018,2022,2024)},
  **{f'e{y}':cty_at(y,(ED[y]-EV1[y]).days-N26+1).get(c,0) for y in (2018,2022,2024)}) for c in top]
past=[]
gv=[json.loads(l) for l in open(GA+'/snapshots/georgiavotes.jsonl')] if os.path.exists(GA+'/snapshots/georgiavotes.jsonl') else []
with open(ROOT+'/site/ga-data.csv','w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0])+['measure','value','note']); w.writeheader(); w.writerows(rows)
    for p in past: w.writerow(dict(year=p['year'],date=p['date'],days_out=p['days_out'],ev_day=p['ev_day'],measure=p['measure'],value=p['value'],rounded=p['rounded'],note=p['note'],source=p['source']))
open(ROOT+'/site/ga-data.js','w').write('window.GADATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),asof=asof.strftime('%Y-%m-%d %H:%M'),zip=os.path.basename(Z),
  ed={k:v.isoformat() for k,v in ED.items()},ev1={k:v.isoformat() for k,v in EV1.items()},files={y:[os.path.basename(p),n] for y,(p,n) in FILES.items()},cmp_cty=cmp_cty,d26=D26,n26=N26,rows=rows,past=past,gv=gv))+';')
for y in ED:
    for r in rows:
        if r['year']==y and (r['days_out']==D26 or r['ev_day'] in(1,2,N26)): print(y,r['date'],r['days_out'],r['ev_day'],r['inperson_day'],r['inperson_cum'],r['mail_cum'],r['total_cum'])
print(cmp_cty[:5])
