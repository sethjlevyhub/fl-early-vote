#!/usr/bin/env python3
"""Ohio early/absentee data -> site/ohio-data.csv + site/ohio-data.js.
Input: ohio_sources.csv (hand-curated, every row has a source URL) + any box snapshots in
/workspace/oh-earlyvote/snapshots (parsed when the SOS site is reachable). No interpolation."""
import csv, json, os, datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__))
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
EV_START={2018:'2018-10-10',2022:'2022-10-12',2024:'2024-10-08',2026:'2026-10-06'}
rows=[]
for r in csv.DictReader(open(ROOT+'/ohio_sources.csv')):
    y=int(r['year']); d=dt.date.fromisoformat(r['date'])
    rows.append(dict(year=y,election_date=ED[y].isoformat(),report_date=r['date'],days_out=(ED[y]-d).days,metric=r['metric'],
      value=int(r['value']),approx=r['approx'],date_basis=r['date_basis'],source_type=r['source_type'],source_url=r['source_url'],note=r['note']))
# total_early = mail returned + early in-person, only when both are sourced for the same date and no total was given
key={(r['year'],r['report_date'],r['metric']):r for r in rows}
for (y,d,m),r in list(key.items()):
    if m!='abs_returned' or (y,d,'total_early') in key: continue
    e=key.get((y,d,'early_in_person'))
    if e and not r['approx'] and not e['approx']:
        rows.append(dict(r,metric='total_early',value=r['value']+e['value'],source_type='Computed sum of sourced figures',
          note=f"Mail returned {r['value']:,} + early in-person {e['value']:,} (both from {r['source_url']})"))
rows.sort(key=lambda r:(r['year'],r['metric'],r['report_date']))
cols=['year','election_date','report_date','days_out','metric','value','approx','date_basis','source_type','source_url','note']
with open(ROOT+'/site/ohio-data.csv','w',newline='') as f:
    w=csv.DictWriter(f,cols,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/ohio-data.js','w').write('window.OHDATA='+json.dumps({'built':dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),'ev_start':EV_START,'rows':rows})+';')
print(len(rows),'rows')
