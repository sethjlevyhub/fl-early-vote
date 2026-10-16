#!/usr/bin/env python3
"""Arizona early ballots returned, statewide, by days before Election Day (dated by report/post date, Arizona time).
2018: AZ Secretary of State daily 'Early Ballot Update' posted by Garrett Archer (then at the SOS) on X.
2022, 2024: Sam Almy's daily statewide tracker (Arizona Democratic Party ballot-return tracker built from each county's daily
  early-ballot file) as posted on X; last post of each day.
2026: Stealth Analytics statewide page (each county's daily early-ballot file), captured by /workspace/az-earlyvote/capture_az.py;
  Maricopa official ArcGIS 'in hand' layer as a cross-check. -> site/az-data.csv + site/az-data.js"""
import csv,json,os,datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__)); AZ='/workspace/az-earlyvote/snapshots'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
X='https://x.com/'
# (year, report date, returned, rounded?, gop%, dem%, oth%, dem_minus_rep_ballots, source url, who)
P=[(2018,'2018-10-17',121000,1,45.7,31.4,22.3,None,X+'Garrett_Archer/status/1052642115887321088','AZ SOS via Garrett Archer'),
 (2018,'2018-10-18',204000,1,45.3,31.9,22.3,None,X+'Garrett_Archer/status/1052995580488609792','AZ SOS via Garrett Archer'),
 (2018,'2018-10-19',287000,1,45.0,32.1,22.3,None,X+'Garrett_Archer/status/1053357210535845888','AZ SOS via Garrett Archer'),
 (2018,'2018-10-22',399000,1,44.7,32.4,22.4,None,X+'Garrett_Archer/status/1054441346671403008','AZ SOS via Garrett Archer'),
 (2018,'2018-10-23',508000,1,44.8,32.4,22.3,None,X+'Garrett_Archer/status/1054797564535402496','AZ SOS via Garrett Archer'),
 (2018,'2018-10-24',657000,1,44.4,32.7,22.4,None,X+'Garrett_Archer/status/1055176892515401728','AZ SOS via Garrett Archer'),
 (2018,'2018-10-25',761000,1,44.2,32.8,22.5,None,X+'Garrett_Archer/status/1055525307472433152','AZ SOS via Garrett Archer'),
 (2018,'2018-10-31',1230000,1,42.7,33.6,23.0,None,X+'Garrett_Archer/status/1057707301912535040','AZ SOS via Garrett Archer'),
 (2018,'2018-11-05',1590000,1,41.4,33.9,23.9,None,X+'Garrett_Archer/status/1059524470979739648','AZ SOS via Garrett Archer'),
 (2022,'2022-10-17',2500,1,None,None,None,451,X+'sfalmy/status/1582103640323391488','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-18',15400,1,None,None,None,1800,X+'sfalmy/status/1582483775237197824','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-19',55000,1,None,None,None,2800,X+'sfalmy/status/1582752450854850560','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-20',137000,1,None,None,None,11000,X+'sfalmy/status/1583184334621532165','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-21',222000,1,None,None,None,9200,X+'sfalmy/status/1583564448203096064','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-22',264000,1,None,None,None,13000,X+'sfalmy/status/1583860016389365762','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-24',313000,1,None,None,None,16000,X+'sfalmy/status/1584568981771337733','Sam Almy (AZ Dem. Party tracker)'),
 (2022,'2022-10-25',426000,1,None,None,None,18800,X+'sfalmy/status/1584998116620906496','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-15',20700,1,10.5/20.7*100,5.5/20.7*100,4.6/20.7*100,None,X+'sfalmy/status/1846295379203314133','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-16',72800,1,34.2/72.8*100,23/72.8*100,15.5/72.8*100,None,X+'sfalmy/status/1846583772642517187','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-17',172000,1,77.9/172*100,58/172*100,36/172*100,None,X+'sfalmy/status/1847048210688495696','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-18',323000,1,143/323*100,112/323*100,68/323*100,None,X+'sfalmy/status/1847391694997672404','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-20',398000,1,172/398*100,141/398*100,84/398*100,None,X+'sfalmy/status/1848020883140714685','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-21',494000,1,212/494*100,177/494*100,105/494*100,None,X+'sfalmy/status/1848402304191369324','Sam Almy (AZ Dem. Party tracker)'),
 (2024,'2024-10-22',689000,1,289/689*100,250/689*100,150/689*100,None,X+'sfalmy/status/1848824926146597132','Sam Almy (AZ Dem. Party tracker)')]
rows=[]
for y,d,n,rd,g,dm,o,adv,u,who in P:
    marg=round(dm-g,1) if g is not None else (round(adv/n*100,1) if adv is not None else None)
    rows.append(dict(year=y,date=d,days_out=(ED[y]-dt.date.fromisoformat(d)).days,returned=n,rounded=rd,rep_pct=round(g,1) if g else None,dem_pct=round(dm,1) if dm else None,oth_pct=round(o,1) if o else None,d_minus_r_pts=marg,issued=None,source=u,source_who=who))
for r in csv.DictReader(open(AZ+'/stealth_totals.csv')):
    d=dt.date.fromisoformat(r['asof'])
    rows.append(dict(year=2026,date=r['asof'],days_out=(ED[2026]-d).days,returned=int(r['returned']),rounded=0,rep_pct=None,dem_pct=None,oth_pct=None,d_minus_r_pts=None,issued=int(r['issued']),
        source='https://www.stealth-analytics.com/early-ballots',source_who='Stealth Analytics (county daily files)'))
mar=[dict(date=dt.datetime.strptime(r['data_edit'],'%Y%m%d-%H%M').date().isoformat(),returned=int(r['returns']),requested=int(r['requests'])) for r in csv.DictReader(open(AZ+'/totals.csv'))]
mpast=[dict(year=2022,date='2022-10-19',days_out=20,returned=55543,y2018_same_day=92000,src=X+'Garrett_Archer/status/1582846620315492357',note='Maricopa County Elections press conference, via Garrett Archer; 2018 same day "~92,000"')]
# 2026 party split of returned early ballots, statewide, from Stealth Analytics (@StealthPolling) daily tracker posts on X
PARTY26=[('2026-10-13',31.5,46.0,22.5,'statewide','https://x.com/StealthPolling/status/2110048076295778385'),
 ('2026-10-14',33.8,43.9,22.4,'statewide','https://x.com/StealthPolling/status/2110397081198469411'),
 ('2026-10-15',36.7,40.9,22.3,'Maricopa','https://x.com/StealthPolling/status/2110776228819169369'),
 ('2026-10-16',36.9,40.8,22.3,'statewide','https://x.com/StealthPolling/status/2111127598822740242')]
party26=[dict(date=d,days_out=(ED[2026]-dt.date.fromisoformat(d)).days,rep_pct=r,dem_pct=dm,oth_pct=o,d_minus_r_pts=round(dm-r,1),scope=sc,source=u) for d,r,dm,o,sc,u in PARTY26]
for r in rows:
    m=[q for q in party26 if q['date']==r['date'] and q['scope']=='statewide' and r['year']==2026]
    if m: r.update(rep_pct=m[0]['rep_pct'],dem_pct=m[0]['dem_pct'],oth_pct=m[0]['oth_pct'],d_minus_r_pts=m[0]['d_minus_r_pts'])
rows.sort(key=lambda r:(r['year'],r['date']))
with open(ROOT+'/site/az-data.csv','w',newline='') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/az-data.js','w').write('window.AZDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed={k:v.isoformat() for k,v in ED.items()},maricopa=mar,maricopa_past=mpast,party26=party26,rows=rows))+';')
for r in rows:
    if r['days_out'] in(18,19,20): print(r['year'],r['date'],r['days_out'],r['returned'],r['d_minus_r_pts'])
