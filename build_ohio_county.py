#!/usr/bin/env python3
"""Partial-county Ohio aggregate from latest captured county BOE voter lists.
-> site/ohio-county-data.csv (+ .js). Cumulative by date (from each voter's return/vote date in the latest file),
party = party of last partisan primary ballot as recorded by the county (Ohio has no party registration)."""
import csv,gzip,glob,json,os,collections,datetime as dt
C='/workspace/oh-earlyvote/county'; ROOT=os.path.dirname(os.path.abspath(__file__))
P={'DEM':'D','D':'D','DEMOCRATIC':'D','REP':'R','R':'R','REPUBLICAN':'R','NON':'U','U':'U','UNAFFILIATED':'U','NONPARTISAN':'U','':'U'}
pt=lambda s:P.get(s.strip().upper(),'O')
def d(s):
    s=s.strip().split()[0] if s.strip() else ''
    try: return dt.datetime.strptime(s,'%m/%d/%Y').date() if s else None
    except ValueError: BAD[0]+=1; return None
def latest(pat): f=sorted(glob.glob(pat)); return f[-1] if f else None
def rd(f,delim=','): return csv.DictReader(gzip.open(f,'rt',encoding='latin-1'),delimiter=delim,skipinitialspace=True)
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
SRC={'cuyahoga':'https://boe.cuyahogacounty.gov/candidates/Get-Vote-by-Mail-Labels-and-Lists','franklin':'https://electionlink.franklincountyohio.gov/portals/ElectionVault/PublicRecords.aspx','butler':'https://electionlink.bcohio.gov/portals/ElectionVault/PublicRecords.aspx'}
BAD=[0]
ev=[]  # (county,year,metric,date,party)  metric: mail_req / mail_ret / eip
def cuy(f,y):
    for r in rd(f):
        c=r['Category'].strip(); p=pt(r['Party'])
        if c=='TR': continue
        if c=='I':
            if d(r['DateReturned']): ev.append(('cuyahoga',y,'eip',d(r['DateReturned']),p))
        else:
            ev.append(('cuyahoga',y,'mail_req',d(r['DateIssued']),p))
            if d(r['DateReturned']): ev.append(('cuyahoga',y,'mail_ret',d(r['DateReturned']),p))
snap={}
f=latest(C+'/cuyahoga/av2026_*.gz'); snap['cuyahoga']=f; cuy(f,2026)
for y in (2018,2022,2024):
    f=latest(C+f'/cuyahoga/hist{y}_*.gz')
    if f: cuy(f,y)
f=latest(C+'/franklin/mail_*.gz'); snap['franklin']=f
for r in rd(f,'\t'):
    p=pt(r['PARTY']); ev.append(('franklin',2026,'mail_req',d(r['DATE_REQUESTED']),p))
    if d(r['DATE RETURNED']): ev.append(('franklin',2026,'mail_ret',d(r['DATE RETURNED']),p))
for r in rd(latest(C+'/franklin/eip_*.gz'),'\t'):
    if d(r['DATE VOTED']): ev.append(('franklin',2026,'eip',d(r['DATE VOTED']),pt(r['PARTY'])))
f=latest(C+'/butler/mail_*.gz'); snap['butler']=f
for r in rd(f):
    p=pt(r['Party']); ev.append(('butler',2026,'mail_req',d(r['Requested Date']),p))
    if d(r['Ballot Returned']): ev.append(('butler',2026,'mail_ret',d(r['Ballot Returned']),p))
for r in rd(latest(C+'/butler/eip_*.gz')):
    if d(r['Ballot Returned']) or d(r['Ballot Issued']): ev.append(('butler',2026,'eip',d(r['Ballot Returned']) or d(r['Ballot Issued']),pt(r['Party'])))
# cumulative by date per (scope,year,metric)
rows=[]
TODAY=dt.date.today()
def cum(sel,scope,y):
    for m in ('mail_req','mail_ret','eip'):
        es=[e for e in sel if e[1]==y and e[2]==m and e[3] and e[3]<=TODAY]
        if not es: continue
        byd=collections.defaultdict(collections.Counter)
        for e in es: byd[e[3]][e[4]]+=1
        run=collections.Counter()
        start=ED[y]-dt.timedelta(days=35)
        pre=sum((byd[k] for k in byd if k<start),collections.Counter()); run+=pre
        for k in sorted(x for x in byd if x>=start):
            run+=byd[k]
            rows.append(dict(scope=scope,year=y,metric=m,date=k.isoformat(),days_out=(ED[y]-k).days,total=sum(run.values()),D=run['D'],R=run['R'],U=run['U'],O=run['O']))
cum(ev,'partial_aggregate_cuyahoga_franklin_butler',2026)
for c in SRC: cum([e for e in ev if e[0]==c],c,2026)
for y in (2018,2022,2024): cum([e for e in ev if e[0]=='cuyahoga'],'cuyahoga',y)
cols=['scope','year','metric','date','days_out','total','D','R','U','O']
with open(ROOT+'/site/ohio-county-data.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,cols); w.writeheader(); w.writerows(rows)
meta=dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),snapshots={k:os.path.basename(v) for k,v in snap.items()},sources=SRC,
  label='PARTIAL: Cuyahoga + Franklin + Butler counties only (about 1 in 4 Ohio registered voters). Not a statewide total.')
open(ROOT+'/site/ohio-county-data.js','w').write('window.OHCOUNTY='+json.dumps(dict(meta,rows=rows))+';')
print(len(rows),'rows; unparseable dates',BAD[0])
for s in ['partial_aggregate_cuyahoga_franklin_butler','cuyahoga','franklin','butler']:
    for m in ('mail_req','mail_ret','eip'):
        x=[r for r in rows if r['scope']==s and r['year']==2026 and r['metric']==m]
        if x: print(s,m,x[-1]['date'],x[-1]['total'],'D',x[-1]['D'],'R',x[-1]['R'],'U',x[-1]['U'])
for y in (2018,2022,2024):
    for m in ('mail_ret','eip'):
        x=[r for r in rows if r['scope']=='cuyahoga' and r['year']==y and r['metric']==m and r['days_out']>=17]
        if x: print('cuy',y,m,'@',x[-1]['days_out'],x[-1]['total'])
