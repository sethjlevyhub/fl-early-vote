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
day=collections.defaultdict(collections.Counter); cty=collections.Counter(); apps=0; issued=0
for r in csv.DictReader(io.TextIOWrapper(zf.open(zi),encoding='latin-1')):
    if r['Application Status']=='A' and r['Ballot Style']!='EARLY IN-PERSON': apps+=1
    if r['Ballot Issued Date'] and r['Ballot Style']!='EARLY IN-PERSON': issued+=1
    if r['Ballot Status']!='A' or not r['Ballot Return Date']: continue
    d=dt.datetime.strptime(r['Ballot Return Date'],'%m/%d/%Y').date()
    if d>=asof.date(): continue  # file is pulled early on the as-of date; that day is incomplete
    k='inperson' if r['Ballot Style']=='EARLY IN-PERSON' else 'mail'
    day[d][k]+=1; cty[r['County']]+=1
rows=[];ci=cm=0
for d in sorted(day):
    ci+=day[d]['inperson']; cm+=day[d]['mail']
    if (ED[2026]-d).days>45: continue
    rows.append(dict(year=2026,date=d.isoformat(),days_out=(ED[2026]-d).days,ev_day=(d-EV1[2026]).days+1 if d>=EV1[2026] else None,
        inperson_day=day[d]['inperson'],mail_day=day[d]['mail'],inperson_cum=ci,mail_cum=cm,total_cum=ci+cm,rounded=0,
        source='Georgia SOS statewide absentee voter file, 11/3/2026 General and Special Elections (mvp.sos.ga.gov/s/voter-absentee-files), file dated '+asof.strftime('%Y-%m-%d %H:%M')))
# Past cycles: official SOS figures as reported (rounded where marked). (year, ev_day, measure, value, rounded, note, url)
PAST=[(2018,1,'inperson_day',70849,0,'2018 first day of early voting, per SOS (cited in 2022 coverage)','https://truthout.org/articles/the-first-2-days-of-early-voting-in-georgia-midterms-have-been-record-breaking/'),
 (2022,1,'inperson_day',134045,0,'Day 1 in-person, SOS website (reconciled; initial report 131,318)','https://www.atlantanewsfirst.com/2022/10/19/record-turnout-keeps-pace-day-2-early-voting-georgia/'),
 (2022,2,'inperson_day',134005,0,'Day 2 in-person, SOS website','https://www.atlantanewsfirst.com/2022/10/19/record-turnout-keeps-pace-day-2-early-voting-georgia/'),
 (2022,2,'inperson_cum',268050,0,'In-person through day 2, SOS figures','https://truthout.org/articles/the-first-2-days-of-early-voting-in-georgia-midterms-have-been-record-breaking/'),
 (2024,1,'total_cum',328000,1,'"over 328,000 total votes" incl. accepted absentees, Gabriel Sterling (SOS COO)','https://thehill.com/homenews/campaign/4935954-georgia-early-voting-record-shattered/'),
 (2024,2,'inperson_cum',581902,0,'Two-day early in-person total','https://www.washingtonpost.com/politics/2024/10/16/georgia-early-voting-numbers-record-election-2024/'),
 (2024,2,'total_cum',620000,1,'"nearly 620,000 total votes" (~590,000 early + 34,272 accepted absentees), Sterling','https://thehill.com/homenews/campaign/4938585-georgia-early-voting-records-set/')]
past=[dict(year=y,ev_day=e,days_out=(ED[y]-(EV1[y]+dt.timedelta(e-1))).days,date=(EV1[y]+dt.timedelta(e-1)).isoformat(),measure=m,value=v,rounded=rd,note=n,source=u) for y,e,m,v,rd,n,u in PAST]
gv=[json.loads(l) for l in open(GA+'/snapshots/georgiavotes.jsonl')] if os.path.exists(GA+'/snapshots/georgiavotes.jsonl') else []
with open(ROOT+'/site/ga-data.csv','w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0])+['measure','value','note']); w.writeheader(); w.writerows(rows)
    for p in past: w.writerow(dict(year=p['year'],date=p['date'],days_out=p['days_out'],ev_day=p['ev_day'],measure=p['measure'],value=p['value'],rounded=p['rounded'],note=p['note'],source=p['source']))
open(ROOT+'/site/ga-data.js','w').write('window.GADATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),asof=asof.strftime('%Y-%m-%d %H:%M'),zip=os.path.basename(Z),
  ed={k:v.isoformat() for k,v in ED.items()},ev1={k:v.isoformat() for k,v in EV1.items()},mail_apps=apps,mail_issued=issued,counties=cty.most_common(15),rows=rows,past=past,gv=gv))+';')
for r in rows[-5:]: print(r['date'],r['days_out'],r['ev_day'],r['inperson_day'],r['mail_day'],r['total_cum'])
print('mail apps',apps,'issued',issued,cty.most_common(5))
