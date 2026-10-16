#!/usr/bin/env python3
"""Maine absentee voting from the SOS Statewide Absentee Voter Data File (voter-level, with party).
Past cycles (2018/2022/2024) are rebuilt day by day from each final file's request and received dates; 2026 from the
latest posted file (captured by /workspace/me-earlyvote/capture_me.sh). -> site/me-data.csv + site/me-data.js"""
import csv,gzip,glob,re,json,os,io,datetime as dt,collections
ROOT=os.path.dirname(os.path.abspath(__file__)); ME='/workspace/me-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
B='https://www.maine.gov/sos/sites/maine.gov.sos/files/'
PAST={2018:('raw/me2018.txt',B+'data-text/absentee-voter-file11618.txt'),2022:('raw/me2022.txt',B+'inline-files/Absentee%20Voter%20File11822_0.txt'),
      2024:('raw/me2024.txt',B+'inline-files/2024-11-05%20Final%20AB%20Voter%20File.txt')}
def asof(p): m=re.search(r'as_of_(\d+)-(\d+)-(\d+)',p); return dt.date(2000+int(m[3]),int(m[1]),int(m[2]))
snaps=sorted(glob.glob(ME+'/snapshots/*.txt.gz'),key=asof); latest=snaps[-1]; A26=asof(latest)
FILES={y:(open(ME+'/'+p,encoding='latin-1'),u) for y,(p,u) in PAST.items()}
FILES[2026]=(io.TextIOWrapper(gzip.open(latest),encoding='latin-1'),B+'inline-files/'+os.path.basename(latest)[:-3].replace('_','%20'))
def pd(s):
    try: return dt.datetime.strptime((s or '').split(' ')[0],'%m/%d/%Y').date()
    except ValueError: return None
PT=lambda p:p if p in('D','R','U') else 'O'
def g(r,*k): return next((r[x] for x in k if x in r and r[x] is not None),'')
rows=[];cd={}
for y,(fh,url) in FILES.items():
    req=collections.Counter();ret=collections.defaultdict(collections.Counter);bad=0
    end=A26 if y==2026 else ED[y]
    for r in csv.DictReader(fh,delimiter='|'):
        p=r.get('P')
        if not p: continue
        q=pd(g(r,'REQDATE','Req Date'))
        if q: req[min(max(q,ED[y]-dt.timedelta(120)),ED[y])]+=1
        rd=pd(g(r,'RECDATE','Rec Date')); st=g(r,'ACC OR REJ','Status')
        if rd and st not in('REJ','RNC'):
            if not(ED[y]-dt.timedelta(120)<=rd<=end): bad+=1; continue
            t=g(r,'RECTYPE','Rec Type'); c=ret[rd]; c['all']+=1; c[PT(p)]+=1; c['inperson' if t=='VP' else 'other']+=1
            c['cd'+g(r,'CG')]+=1; c['cd'+g(r,'CG')+PT(p)]+=1
    cum=collections.Counter();cq=0
    for i in range(120,-1,-1):
        d=ED[y]-dt.timedelta(i)
        if d>end: break
        cq+=req[d]; cum.update(ret[d])
        if i<=45: rows.append(dict(year=y,date=d.isoformat(),days_out=i,requested=cq,returned=cum['all'],in_person=cum['inperson'],other=cum['other'],
            dem=cum['D'],rep=cum['R'],unenr=cum['U'],oth=cum['O'],cd1=cum['cd1'],cd2=cum['cd2'],day=ret[d]['all'],day_inperson=ret[d]['inperson'],source=url))
    print(y,'out-of-range received dates skipped:',bad)
snapt=[]
for s in snaps:
    n=0
    for r in csv.DictReader(io.TextIOWrapper(gzip.open(s),encoding='latin-1'),delimiter='|'):
        if r.get('P') and r.get('Rec Date') and r.get('Status') not in('REJ','RNC'): n+=1
    snapt.append(dict(asof=asof(s).isoformat(),returned=n,file=os.path.basename(s)[:-3]))
cols=list(rows[0])
with open(ROOT+'/site/me-data.csv','w',newline='') as f: w=csv.DictWriter(f,cols); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/me-data.js','w').write('window.MEDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),asof=A26.isoformat(),
  ed={k:v.isoformat() for k,v in ED.items()},snaps=snapt,rows=rows))+';')
D=(ED[2026]-A26).days; print(len(rows),'rows; 2026 as of',A26,D,'days out')
for r in rows:
    if r['days_out']==D: print({k:v for k,v in r.items() if k!='source'})
