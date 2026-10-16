#!/usr/bin/env python3
"""Arizona early ballots. 2026: Maricopa County official ArcGIS 'Early Voting Returns In Hand' layer (captured by
/workspace/az-earlyvote/capture_az.py, one row per county data update). Past cycles: only scattered official counts quoted
in news (no archived same-day series found). -> site/az-data.csv + site/az-data.js"""
import csv,json,os,datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__))
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
L='https://data-maricopa.opendata.arcgis.com/datasets/dc5277d6072045ab81fe0a776a8aab5d_0/explore'
rows=[]
for r in csv.DictReader(open('/workspace/az-earlyvote/snapshots/totals.csv')):
    d=dt.datetime.strptime(r['data_edit'],'%Y%m%d-%H%M').date()
    rows.append(dict(year=2026,scope='Maricopa',measure='in_hand',date=d.isoformat(),days_out=(ED[2026]-d).days,returned=int(r['returns']),requested=int(r['requests']),
        dem=None,rep=None,oth=None,approx='',source='Maricopa County Early Voting Returns In Hand (official ArcGIS layer): '+L))
PAST=[(2022,'2022-10-25','Maricopa','county daily return file',178664,None,71063,66077,41484,'','Arizona Republic (azcentral), Oct 25, 2022, analysis of county early-ballot return data','https://www.azcentral.com/story/news/politics/elections/2022/10/25/arizona-ballot-returns-midterm-2022-election-voting/10591778002/'),
 (2024,'2024-10-23','Maricopa','county daily return file',600000,None,None,None,None,'"more than 600,000" (rounded)','Arizona Republic (via USA Today network), Oct 24, 2024','https://eu.livingstondaily.com/story/news/politics/elections/2024/10/24/maricopa-county-early-ballot-2024-election-returns/75816374007/'),
 (2024,'2024-10-29','Maricopa','Recorder count',1095632,None,405026,326132,222407,'party split as of that morning (953,565 total)','Maricopa County Recorder Stephen Richer, Oct 29, 2024, via AZFamily','https://www.azfamily.com/2024/10/30/record-early-voting-numbers-maricopa-county-so-far-officials-say/')]
for y,d,sc,m,ret,req,D,R,O,ap,who,u in PAST:
    rows.append(dict(year=y,scope=sc,measure=m,date=d,days_out=(ED[y]-dt.date.fromisoformat(d)).days,returned=ret,requested=req,dem=D,rep=R,oth=O,approx=ap,source=who+': '+u))
with open(ROOT+'/site/az-data.csv','w',newline='') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/az-data.js','w').write('window.AZDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),
  statewide=dict(date='2026-10-16',returned=165881,issued=3245843,maricopa=99625,src='https://www.stealth-analytics.com/early-ballots'),rows=rows))+';')
for r in rows: print(r['year'],r['date'],r['days_out'],r['returned'])
