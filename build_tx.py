#!/usr/bin/env python3
"""Texas early voting (in-person + mail ballots received) from TX Secretary of State.
2022/2024: legacy SOS EV app (earlyvoting.texas-election.com) statewide 'turnout by date' tables, all 254 counties, scraped once
  by /workspace/tx-earlyvote/scrape_tx_legacy.py. 2018: SOS daily pages covering only the 30 largest counties (scrape_tx_2018.py).
2026: Civix IVIS EVR JSON snapshots captured by /workspace/tx-earlyvote/capture_tx.py (latest snapshot per report date).
-> site/tx-data.csv + site/tx-data.js. Two scopes: 'state' (254 counties; 2022+) and 'top30' (2018's 30 largest counties; all years)."""
import csv,json,gzip,glob,os,datetime as dt,collections
ROOT=os.path.dirname(os.path.abspath(__file__)); TX='/workspace/tx-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
EVSTART={2018:'2018-10-22',2022:'2022-10-24',2024:'2024-10-21',2026:'2026-10-19'}
SRC={2018:'https://www.sos.texas.gov/elections/earlyvoting/2018/index.shtml',
     2022:'https://earlyvoting.texas-election.com/Elections/getElectionEVDates.do (2022 Nov 8 General)',
     2024:'https://earlyvoting.texas-election.com/Elections/getElectionEVDates.do (2024 Nov 5 General)',
     2026:'https://goelect.txelections.civixapps.com/ivis-evr-ui/evr (2026 November General)'}
I=lambda s:int(str(s).replace(',','') or 0)
county=collections.defaultdict(dict)   # (year,date) -> {county: rec}
for r in csv.DictReader(open(TX+'/legacy_2018_30co.csv')):
    county[(2018,r['date'])][r['county']]=dict(reg=I(r['registered']),ipd=I(r['inperson_day']),ip=I(r['cum_inperson']),mail=I(r['cum_mail']))
for y in (2022,2024):
    for r in csv.DictReader(open(f'{TX}/legacy_{y}.csv')):
        county[(y,r['date'])][r['county']]=dict(reg=I(r['registered']),ipd=I(r['inperson_day']),ip=I(r['cum_inperson']),mail=I(r['cum_mail']))
snap={}
for f in sorted(glob.glob(TX+'/2026/evr_*.json.gz')): snap[os.path.basename(f)[4:14]]=f   # sorted -> latest capture wins
for d,f in snap.items():
    j=json.load(gzip.open(f))
    for c in j['turnout_by_county']:
        county[(2026,d)][c['name']]=dict(reg=c['registered_voters'],ipd=c['in_person_votes_on_date'],ip=c['total_in_person_votes_for_election'],mail=c['total_mail_votes_for_election'])
TOP30=[c for c in county[(2018,'2018-11-02')] if c!='TOTAL']
rows=[]
for (y,d),cs in sorted(county.items()):
    cs={k:v for k,v in cs.items() if k!='TOTAL'}
    for scope,keys in (('state',list(cs)),('top30',TOP30)):
        if scope=='state' and y==2018: continue
        s={k:sum(cs[c][k] for c in keys if c in cs) for k in ('reg','ipd','ip','mail')}
        rows.append(dict(year=y,scope=scope,report_date=d,days_out=(ED[y]-dt.date.fromisoformat(d)).days,counties=sum(c in cs for c in keys),
            registered=s['reg'],inperson_day=s['ipd'],cum_inperson=s['ip'],cum_mail=s['mail'],cum_total=s['ip']+s['mail'],source_url=SRC[y]))
# check legacy TOTAL rows match our sums
for (y,d),cs in county.items():
    if 'TOTAL' in cs:
        r=[x for x in rows if x['year']==y and x['report_date']==d and x['scope']==('top30' if y==2018 else 'state')][0]
        if r['cum_inperson']!=cs['TOTAL']['ip'] or r['cum_mail']!=cs['TOTAL']['mail']: print('TOTAL mismatch',y,d)
# county table: latest 2026 date vs same days-out 2024/2022
last=max(d for (y,d) in county if y==2026); D=(ED[2026]-dt.date.fromisoformat(last)).days
def at(y):
    ds=[d for (yy,d) in county if yy==y and (ED[y]-dt.date.fromisoformat(d)).days>=D]; return max(ds) if ds else None
ct=[]
for c,v in sorted(county[(2026,last)].items(),key=lambda kv:-kv[1]['reg'])[:15]:
    rec=dict(county=c,reg=v['reg'],t26=v['ip']+v['mail'])
    for y in (2024,2022):
        p=county.get((y,at(y)),{}).get(c); rec[f't{y%100}']=p['ip']+p['mail'] if p else None
    ct.append(rec)
cols=list(rows[0])
with open(ROOT+'/site/tx-data.csv','w',newline='') as f: w=csv.DictWriter(f,cols); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/tx-data.js','w').write('window.TXDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed={k:v.isoformat() for k,v in ED.items()},ev_start=EVSTART,src=SRC,top30=TOP30,ctab=dict(date=last,days_out=D,d24=at(2024),d22=at(2022),rows=ct),rows=rows))+';')
print(len(rows),'rows; latest 2026',last,D,'days out')
for y in ED:
    for sc in ('state','top30'):
        p=[r for r in rows if r['year']==y and r['scope']==sc and r['days_out']>=D]
        if p: r=p[-1]; print(y,sc,r['report_date'],r['days_out'],r['cum_inperson'],r['cum_mail'],r['cum_total'],r['registered'])
