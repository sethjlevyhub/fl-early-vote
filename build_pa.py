#!/usr/bin/env python3
"""Pennsylvania mail ballots (mail-in + absentee) returned, by days before Election Day, with party.
Official PA Department of State 'General Election Mail Ballot Requests' datasets on data.pa.gov (voter-level), aggregated by
/workspace/pa-earlyvote/capture_pa.py. Counts every request with a ballot-returned date (2022's dataset has no status column, so
cancelled ballots are counted in all years for consistency; ~0.2% in 2026). No 2018: no-excuse mail voting began with Act 77 (2019).
-> site/pa-data.csv + site/pa-data.js"""
import json,csv,os,datetime as dt,collections
ROOT=os.path.dirname(os.path.abspath(__file__)); PA='/workspace/pa-earlyvote'
ED={2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
DS={2022:'uhfm-zhus',2024:'3q5t-ddp8',2026:'nbwd-pfn4'}
SRC={y:f'https://data.pa.gov/d/{d}' for y,d in DS.items()}
PT=lambda p:'D' if p in('D','DEM') else 'R' if p in('R','REP') else 'O'
rows=[];meta={}
for y in ED:
    J=json.load(open(f'{PA}/raw/pa{y}.json' if y!=2026 else f'{PA}/snapshots/pa2026_latest.json'))
    upd=dt.datetime.fromisoformat(J['updated']); end=upd.date() if y==2026 else ED[y]; meta[y]=J['updated']
    ret=collections.defaultdict(collections.Counter); app=collections.Counter()
    for r in J['returned']:
        d=dt.date.fromisoformat(r['d'][:10])
        if d<end: ret[(ED[y]-d).days][PT(r.get('party'))]+=int(r['n'])
    for r in J['apps']:
        d=dt.date.fromisoformat(r['d'][:10])
        if d<end: app[max((ED[y]-d).days,0)]+=int(r['n'])
    c=collections.Counter(); ca=sum(v for k,v in app.items() if k>60)+sum(v for k,v in ret.items() if False)
    for k in ret:
        if k>60: c.update(ret[k])
    for i in range(60,0,-1):
        d=ED[y]-dt.timedelta(i)
        if d>=end: break
        c.update(ret[i]); ca+=app[i]
        if i<=45: n=sum(c.values()); rows.append(dict(year=y,date=d.isoformat(),days_out=i,returned=n,dem=c['D'],rep=c['R'],oth=c['O'],day=sum(ret[i].values()),
            applications=ca,dem_pct=round(c['D']/n*100,1) if n else None,rep_pct=round(c['R']/n*100,1) if n else None,source=SRC[y]))
with open(ROOT+'/site/pa-data.csv','w',newline='') as f: w=csv.DictWriter(f,list(rows[0])); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/pa-data.js','w').write('window.PADATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),updated=meta,src=SRC,ed={k:v.isoformat() for k,v in ED.items()},rows=rows))+';')
L=[r for r in rows if r['year']==2026][-1]; print(L)
for y in (2022,2024): print([r for r in rows if r['year']==y and r['days_out']==L['days_out']])
