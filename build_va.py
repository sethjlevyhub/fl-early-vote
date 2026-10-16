#!/usr/bin/env python3
"""Virginia early votes (in person 'on machine' + mail returned), by days before Election Day. No party registration.
Official source (ELECT Daily Absentee List) is sold, not posted, so secondary sources built from it:
 2024, 2026: EPEC / Digital Poll Watchers daily DAL metrics (COUNTABLE = ON_MACHINE + MAIL_IN). A file pulled the morning of day X
   covers ballots through day X-1, so it's dated X-1 (matches VPAP's 'as of' dates).
 2022, 2026: VPAP early-voting page daily totals by days until election (ELECT file).
-> site/va-data.csv + site/va-data.js"""
import csv,re,json,os,datetime as dt,collections
ROOT=os.path.dirname(os.path.abspath(__file__)); VA='/workspace/va-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
DPW='https://digitalpollwatchers.org/files/DALTracker/%d_November_General/metrics/'
VP='https://www.vpap.org/elections/early-voting/'
def fd(s):
    for f in ('%Y-%m-%dT%H:%M:%S','%d-%b-%Y %H:%M:%S'):
        try: return dt.datetime.strptime(s,f)
        except ValueError: pass
rows={}
for y,p in ((2024,VA+'/raw/va2024.csv'),(2026,VA+'/snapshots/dpw2026.csv')):
    for r in csv.DictReader(open(p)):
        t=fd(r['FILEDATE'])
        if not t: continue
        d=t.date()-dt.timedelta(1); i=(ED[y]-d).days
        if not(0<i<=45): continue
        rows[(y,i)]=dict(year=y,date=d.isoformat(),days_out=i,total=int(r['COUNTABLE']),in_person=int(r['ON_MACHINE']),mail=int(r['MAIL_IN']),issued=int(r['ISSUED']),
            source=DPW%y,source_who='EPEC / Digital Poll Watchers (ELECT Daily Absentee List)')
t=open(VA+'/snapshots/vpap.html').read()
V=collections.defaultdict(dict)
for d,e,n in re.findall(r'days:\s*(-?\d+),\s*election_id:\s*(\d+),\s*total:\s*(\d+)',t): V[int(e)][int(d)]=int(n)
foc=int(re.search(r"focus: \{ name: '2026 November General', id: (\d+)",t)[1]); base=[e for e in V if e!=foc][0]
vp26={}
for i,n in V[base].items():
    if 0<i<=45: rows[(2022,i)]=dict(year=2022,date=(ED[2022]-dt.timedelta(i)).isoformat(),days_out=i,total=n,in_person=None,mail=None,issued=None,source=VP,source_who='VPAP (ELECT early-voting file)')
for i,n in V[foc].items(): vp26[i]=n
out=sorted(rows.values(),key=lambda r:(r['year'],-r['days_out']))
with open(ROOT+'/site/va-data.csv','w',newline='') as f: w=csv.DictWriter(f,list(out[0])); w.writeheader(); w.writerows(out)
open(ROOT+'/site/va-data.js','w').write('window.VADATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed={k:v.isoformat() for k,v in ED.items()},vpap26=vp26,
  final2018=dict(total=345000,src='https://dcist.com/story/22/10/20/va-early-voter-turnout/',note='2018 final early/absentee total "about 345,000" (VPAP via DCist); excuse required in 2018'),rows=out))+';')
L=[r for r in out if r['year']==2026][-1]; print(L,'vpap',vp26.get(L['days_out']))
for y in (2022,2024): print([r for r in out if r['year']==y and r['days_out']==L['days_out']])
