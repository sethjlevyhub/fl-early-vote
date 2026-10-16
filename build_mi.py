#!/usr/bin/env python3
"""Michigan absentee + early in-person voting from the MI SOS Voter Participation Dashboard (public Power BI; captured by
/workspace/mi-earlyvote/capture_mi.py). The dashboard holds daily county series for the 2024 November general and 2026 elections.
2022: three SOS press-release data points (no daily series survives). -> site/mi-data.csv + site/mi-data.js"""
import json,gzip,csv,datetime as dt,collections,os
ROOT=os.path.dirname(os.path.abspath(__file__)); MI='/workspace/mi-earlyvote'
ED={2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
D2Y={1730764800000:2024,1793664000000:2026}
SRC={2024:'https://www.michigan.gov/sos/elections/election-results-and-data/voter-participation-dashboard (2024 November General)',
     2026:'https://www.michigan.gov/sos/elections/election-results-and-data/voter-participation-dashboard (2026 November General)'}
BAD={(2024,'2024-10-09')}  # dashboard glitch: returned jumps to 1.20M then back to 468K next day, sent drops 400K
S=json.load(gzip.open(MI+'/snapshots/latest.json.gz'))
day=lambda ms:dt.datetime.fromtimestamp(ms/1000,dt.timezone.utc).date().isoformat()
st=collections.defaultdict(lambda:collections.Counter()); co=collections.defaultdict(lambda:collections.Counter())
for r in S['av_ballot']:
    y=D2Y.get(r['ELECTION_DATE']); 
    if not y: continue
    k=(y,day(r['COUNT_DATE'])); st[k]['returned']+=r['sum_AV_BALLOT_COUNT'] or 0; st[k]['sent']+=r['sum_AV_BALLOT_SENT_COUNT'] or 0
    co[k+(r['COUNTY_NAME'],)]['returned']+=r['sum_AV_BALLOT_COUNT'] or 0
for r in S['av_app']:
    y=D2Y.get(r['ELECTION_DATE'])
    if y: k=(y,day(r['COUNT_DATE'])); st[k]['requested']+=r['sum_AV_APP_COUNT'] or 0; st[k]['perm']+=(r['sum_AV_APP_COUNT'] or 0) if r['IS_PERM_BALLOT']=='Y' else 0
evd=collections.Counter(); evc=collections.Counter()
for r in S['ev']:
    y=D2Y.get(r['ELECTION_DATE'])
    if y: k=(y,day(r['COUNT_DATE'])); evd[k]+=r['sum_IN_PERSON_VOTE_COUNT'] or 0; evc[k+(r['COUNTY_NAME'],)]+=r['sum_IN_PERSON_VOTE_COUNT'] or 0
vot=sorted((day(r['COUNT_DATE']),r['sum_VOTER_COUNT']) for r in S['voters'])
def reg(d): p=[v for dd,v in vot if dd<=d]; return p[-1] if p else None
rows=[]
for y in (2024,2026):
    cum=0
    for d in sorted(set(dd for (yy,dd) in st if yy==y)|set(dd for (yy,dd) in evd if yy==y)):
        cum+=evd[(y,d)]
        if (y,d) in BAD or dt.date.fromisoformat(d)>ED[y]: continue
        s=st[(y,d)]
        rows.append(dict(year=y,date=d,days_out=(ED[y]-dt.date.fromisoformat(d)).days,requested=s['requested'] or None,perm=s['perm'] or None,sent=s['sent'] or None,
            returned=s['returned'] or None,ev_day=evd[(y,d)],ev_cum=cum,total=(s['returned'] or 0)+cum,registered=reg(d),approx='',source=SRC[y]))
PR=[('2022-10-18',432960,None,'','https://www.michigan.gov/sos/resources/news/2022/10/18/three-weeks-remain-until-nov-8-general-election'),
    ('2022-10-25',771967,1800000,'requested "more than 1.8 million"','https://www.michigan.gov/sos/resources/news/2022/10/25/two-weeks-before-election-day-1-point-8-million-absentee-ballots'),
    ('2022-11-01',1100000,2000000,'returned "1.1 million", requested "nearly 2 million" (rounded)','https://www.michigan.gov/sos/resources/news/2022/11/01/one-week-before-election-day-nearly-2-million-michiganders-have-requested-absentee-ballots')]
for d,ret,req,ap,u in PR:
    rows.append(dict(year=2022,date=d,days_out=(ED[2022]-dt.date.fromisoformat(d)).days,requested=req,perm=None,sent=None,returned=ret,ev_day=0,ev_cum=0,total=ret,registered=None,approx=ap,source=u))
rows.sort(key=lambda r:(r['year'],r['date']))
last=max(r['date'] for r in rows if r['year']==2026); D=(ED[2026]-dt.date.fromisoformat(last)).days
d24=max(r['date'] for r in rows if r['year']==2024 and r['days_out']>=D)
ct=[]
for (y,d,c),v in co.items():
    if y==2026 and d==last:
        p=co.get((2024,d24,c),{}).get('returned',0)+0; ct.append(dict(county=c,r26=v['returned']+0,r24=p))
ct=sorted(ct,key=lambda r:-r['r24'])[:15]
cols=list(rows[0])
with open(ROOT+'/site/mi-data.csv','w',newline='') as f: w=csv.DictWriter(f,cols); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/mi-data.js','w').write('window.MIDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),fetched=S['fetched'],ed={k:v.isoformat() for k,v in ED.items()},
  ev_start={2024:'2024-10-26',2026:'2026-10-24'},ctab=dict(date=last,d24=d24,days_out=D,rows=ct),rows=rows))+';')
print(len(rows),'rows; latest',last,D)
for r in rows:
    if r['days_out'] in (D,21,14,7,4,1) : print(r['year'],r['date'],r['days_out'],r['requested'],r['perm'],r['sent'],r['returned'],r['ev_cum'],r['total'],r['registered'])
