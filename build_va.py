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

# ---- Partisan-lean proxy by locality (geographic, NOT voter party) ----
import zipfile,io
ENR='https://enr.elections.virginia.gov/results/public/Virginia/elections/2024NovemberGeneral/ballot-items/01000000-c7a0-1ae0-1363-08dcde4d9d9f'
T22='https://results.elections.virginia.gov/vaelections/2022%20November%20General/Site/Statistics/Turnout.html'
P=json.load(open(VA+'/raw/enr2024_president.json')); lean={}
for b in P['breakdownResults']:
    nm=b['locality']['name'][0]['text']; v={o['name'][0]['text']:o['voteCount'] for o in b['ballotOptions']}
    h=v.get('Kamala D. Harris',0); t=v.get('Donald J. Trump',0); lean[nm]=dict(harris=h,trump=t,total=b['voteTotal'],margin=round((h-t)/b['voteTotal']*100,1))
G=lambda m:'Strong D' if m>=20 else 'Lean D' if m>=0 else 'Lean R' if m>-20 else 'Strong R'
def locs(zp,y):
    z=zipfile.ZipFile(zp); out={}
    for n in z.namelist():
        if not(n.startswith('byLOCALITY_NAME/') and n.endswith('WPVisPro.csv')): continue
        nm=n.split('/')[1]; s={}
        for r in csv.DictReader(io.TextIOWrapper(z.open(n))):
            t=fd(r['FILEDATE'])
            if t: s[(ED[y]-(t.date()-dt.timedelta(1))).days]=int(r['COUNTABLE'] or 0)
        out[nm]=s
    return out
L24=locs(VA+'/raw/dpw2024.zip',2024); L26=locs(VA+'/snapshots/dpw2026.zip' if os.path.exists(VA+'/snapshots/dpw2026.zip') else VA+'/raw/dpw2026.zip',2026)
import re as _re
t22=open(VA+'/raw/va2022_turnout.html').read(); F22={}
for nm,ev,ed_,ml in _re.findall(r'\.html">([^<]+)</a></td><td>([\d,]+)</td><td>([\d,]+)</td><td>([\d,]+)</td>',t22):
    F22[__import__('html').unescape(nm).strip()]=int(ev.replace(',',''))+int(ml.replace(',',''))
NM=lambda s:s.replace(' AND ',' & ')
L24={NM(k):v for k,v in L24.items()}; L26={NM(k):v for k,v in L26.items()}
D=max(i for i in L26['FAIRFAX COUNTY'])  # placeholder, replaced below
D=min(i for i in set.intersection(*[set(v) for v in L26.values() if v]))
def at_(s,i):
    k=[x for x in s if x>=i]; return s[min(k)] if k else 0
fin24=lambda s:s[min(x for x in s if x>=1)] if s else 0
LT=[]
for nm,l in lean.items():
    LT.append(dict(locality=nm,margin24=l['margin'],group=G(l['margin']),v26=at_(L26.get(nm,{}),D),v24=at_(L24.get(nm,{}),D),f24=fin24(L24.get(nm,{})),f22=F22.get(nm,0)))
miss=[(x['locality'],x['v26'],x['v24'],x['f22']) for x in LT if not x['v26'] or not x['f22'] or not x['v24']]; print('missing',miss)
GR=['Strong D','Lean D','Lean R','Strong R']; tot={k:sum(x[k] for x in LT) for k in ('v26','v24','f24','f22')}
groups=[dict(group=g,n=sum(1 for x in LT if x['group']==g),**{k:sum(x[k] for x in LT if x['group']==g) for k in ('v26','v24','f24','f22')}) for g in GR]
for g in groups:
    for k in ('v26','v24','f24','f22'): g['s'+k]=round(g[k]/tot[k]*100,1)
    g['pace24']=round((g['v26']/g['v24']-1)*100,1)
print('D',D,tot); [print(g) for g in groups]
with open(ROOT+'/site/va-localities.csv','w',newline='') as f: w=csv.DictWriter(f,list(LT[0])); w.writeheader(); w.writerows(sorted(LT,key=lambda x:-x['v26']))
js=open(ROOT+'/site/va-data.js').read().rstrip(';')
open(ROOT+'/site/va-data.js','w').write(js[:-1]+',"lean":'+json.dumps(dict(days_out=D,groups=groups,tot=tot,top=sorted(LT,key=lambda x:-x['v26'])[:15],src_enr=ENR,src_t22=T22))+'};')
