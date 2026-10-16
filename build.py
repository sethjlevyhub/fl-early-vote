#!/usr/bin/env python3
"""Fetch/parse FL DOS early-vote & VBM data -> data.csv + site/data.js.
Only sourced numbers. Days-out = Election Day minus date the state report was posted/compiled (morning)."""
import csv, glob, json, re, subprocess, datetime as dt, os, html
ROOT=os.path.dirname(os.path.abspath(__file__))
SNAP='/workspace/fl-earlyvote/2026/snapshots'; TEAM='/workspace/fl-earlyvote/2026'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
PORTAL='https://countyfilesvbm-ev.floridados.gov/VoteByMailEarlyVotingReports/PublicStats'
TSV='https://electionfiles.floridados.gov/countyballotreportfiles/Stats_49894_{}.txt'
FIN={2018:'https://dos.fl.gov/media/700669/early-voting-and-vote-by-mail-report-2018-genpdf.pdf',
     2022:'https://dos.fl.gov/media/706191/2022-ge-rptstatuscountsarchive-ev-vbm.pdf',
     2024:'https://dos.fl.gov/media/708648/2024gen_vbm-ev_statuscounts.pdf'}
FCOLS=['year','election_date','report_date','days_out','method','rep','dem','oth','npa','total','source_type','source_url','note']
rows=[]
def add(y,d,method,tot,rep='',dem='',oth='',npa='',st='',url='',note=''):
    d=dt.date.fromisoformat(d) if isinstance(d,str) else d
    rows.append(dict(year=y,election_date=ED[y].isoformat(),report_date=d.isoformat(),days_out=(ED[y]-d).days,
      method=method,rep=rep,dem=dem,oth=oth,npa=npa,total=tot,source_type=st,source_url=url,note=note))
n=lambda s:int(s.replace(',','').strip())
# --- 2026: official TSV versions (deduped by CompileDate) + PublicStats HTML snapshots
seen={}
for f in glob.glob(SNAP+'/Stats_49894_*.txt')+glob.glob(TEAM+'/Stats_49894_*.txt'):
    for r in csv.DictReader(open(f,encoding='utf-8-sig'),delimiter='\t'):
        if r['CountyName']!='State Totals': continue
        m={'Voted Vote-by-Mail':'vbm_returned','Vote-by-Mail Provided (Not Yet Returned)':'vbm_outstanding','Voted Early':'early_in_person'}.get(r['StatType'])
        if not m: continue
        d=dt.datetime.strptime(r['CompileDate'].split()[0],'%m/%d/%Y').date()
        key=(m,d); kind=os.path.basename(f).split('_')[2].split('.')[0]
        seen[key]=dict(tot=n(r['GrandTotal']),rep=n(r['TotalRep']),dem=n(r['TotalDem']),oth=n(r['TotalOth']),npa=n(r['TotalNpa']),url=TSV.format(kind),st='FL DOS daily statewide file',note='CompileDate '+r['CompileDate'].strip())
for f in sorted(glob.glob(SNAP+'/PublicStats_*.html')):
    t=re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',open(f,encoding='utf-8',errors='ignore').read()))
    t=t.split('Statewide Totals',1)[-1].split('County Totals')[0]
    for lab,m in [(r'Vote-by-Mail Provided \(Not Yet Returned\)','vbm_outstanding'),('Voted Vote-by-Mail','vbm_returned'),('Voted Early','early_in_person')]:
        g=re.search(lab+r' ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)(?: (\d+/\d+/\d{4}))?',t)
        if not g: continue
        if not g.group(6):  # no compile date = no activity reported yet
            continue
        d=dt.datetime.strptime(g.group(6),'%m/%d/%Y').date()
        if (m,d) in seen: continue
        seen[(m,d)]=dict(tot=n(g.group(5)),rep=n(g.group(1)),dem=n(g.group(2)),oth=n(g.group(3)),npa=n(g.group(4)),url=PORTAL,st='FL DOS portal (box snapshot)',note='snapshot '+os.path.basename(f))
for (m,d),v in sorted(seen.items(),key=lambda x:x[0][1]):
    add(2026,d,m,v['tot'],v['rep'],v['dem'],v['oth'],v['npa'],v['st'],v['url'],v['note'])
# --- historical daily points: only figures quoted from DOS data in dated news reports
NSF22='https://www.cltampa.com/news/so-far-almost-1-million-vote-by-mail-ballots-have-been-cast-in-florida-14405034/'
H=[(2018,'2018-10-17',554350,247530,207171,3020,96629,'https://www.orlandoweekly.com/news/mail-in-ballots-top-500000-across-florida-for-november-election-19842081/','News Service of Florida: "posted Wednesday morning" (Oct 17); 8 Hurricane Michael counties not reporting'),
 (2022,'2022-10-17',602949,'','','','',NSF22,'NSF: "602,949 on Monday"'),
 (2022,'2022-10-18',733067,'','','','',NSF22,'NSF: "733,067 ballots on Tuesday"'),
 (2022,'2022-10-19',837980,'','','','',NSF22,'NSF: "837,980 on Wednesday"'),
 (2022,'2022-10-20',947736,363101,397495,13911,173229,NSF22,'NSF: as of Thursday morning'),
 (2022,'2022-10-21',1041384,'','','','','https://www.tampafp.com/florida-mail-in-ballots-top-1-16m-as-early-voting-starts/','NSF: "up from 1,041,384 on Friday"'),
 (2022,'2022-10-24',1164753,444954,491708,16790,211301,'https://www.tampafp.com/florida-mail-in-ballots-top-1-16m-as-early-voting-starts/','NSF: as of Monday morning'),
 (2024,'2024-10-16',709359,262136,303597,'','','https://floridapolitics.com/archives/701864-dems-lead-republicans-in-mail-ballots-returned-with-room-to-stretch-lead-further/','Florida Politics: as of Wednesday morning (20 days out); NPA/other not given'),
 (2024,'2024-10-18',990989,'','','','','https://www.pnj.com/story/news/politics/elections/2024/10/18/florida-vote-by-mail-ballot-numbers-2024-election/75735044007/','Pensacola News Journal: as of Friday morning; shares D 42.7% / R 36.7% only')]
for y,d,t,r,dm,o,np,u,no in H: add(y,d,'vbm_returned',t,r,dm,o,np,'News report citing FL DOS data',u,no)
# --- finals from official archive PDFs
for y,u in FIN.items():
    txt=subprocess.run(['pdftotext','-layout','-l','1',glob.glob(ROOT+'/raw/'+os.path.basename(u))[0],'-'],capture_output=True,text=True).stdout
    for lab,m in [('Voted Vote.by.Mail','vbm_returned'),('Voted Early','early_in_person')]:
        g=re.search(lab+r'\s+(?:(\d+/\d+/\d{4})\s+)?([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)',txt)
        asof=dt.datetime.strptime(g.group(1),'%m/%d/%Y').date() if g.group(1) else ED[y]
        add(y,asof,m,n(g.group(6)),n(g.group(2)),n(g.group(3)),n(g.group(4)),n(g.group(5)),'FL DOS final archive PDF',u,'Final cycle total (as of '+asof.isoformat()+')'+('' if g.group(1) else '; PDF gives no as-of date, placed at Election Day'))
rows.sort(key=lambda r:(r['year'],r['method'],r['report_date']))
with open(ROOT+'/data.csv','w',newline='') as f:
    w=csv.DictWriter(f,FCOLS); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/data.js','w').write('window.FLDATA='+json.dumps({'built':dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),'rows':rows})+';')
print(len(rows),'rows')
