#!/usr/bin/env python3
"""Iowa absentee (mail + in-person early) from Iowa SOS 'Absentee Ballot Statistics' PDFs.
History: official SOS archive PDFs that bundle every daily report (2018, 2022, 2024). 2026: box snapshots of the daily file.
-> site/ia-data.csv + site/ia-data.js. Days-out = Election Day minus report date (report pulled ~3-4 AM ET, data through prior day)."""
import sys,glob,os,json,csv,datetime as dt,re,subprocess
sys.path.insert(0,'/workspace/ia-earlyvote'); from parse_ia import parse
ROOT=os.path.dirname(os.path.abspath(__file__)); IA='/workspace/ia-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
EVSTART={2018:'2018-10-08',2022:'2022-10-19',2024:'2024-10-16',2026:'2026-10-14'}
SRC={y:f'https://sos.iowa.gov/elections/pdf/{y}/general/AbsenteeCounty{y}.pdf' for y in (2018,2022,2024)}
SRC[2026]='https://sos.iowa.gov/iowans/election-results-statistics'
reps={}
def add(y,r,src,note):
    k=(y,r['report_date'])
    if k in reps and reps[k]['received']>=r['received']: return
    pk={'Democrat':'D','Republican':'R','No Party':'NP'}
    ok=sum(v['rec'] for v in r['party'].values())==r['received'] and sum(v['req'] for v in r['party'].values())==r['requested']
    row=dict(year=y,report_date=r['report_date'],days_out=(ED[y]-dt.date.fromisoformat(r['report_date'])).days,requested=r['requested'],issued=r['issued'],received=r['received'],source_url=src,note=note)
    for p,c in pk.items():
        row['rec_'+c]=r['party'].get(p,{}).get('rec') if ok else None; row['req_'+c]=r['party'].get(p,{}).get('req') if ok else None
    row['rec_O']=r['received']-sum(row['rec_'+c] for c in pk.values()) if ok else None
    row['req_O']=r['requested']-sum(row['req_'+c] for c in pk.values()) if ok else None
    reps[k]=row
for y in (2018,2022,2024):
    for r in parse(f'{IA}/ref/AbsenteeCounty{y}_final.pdf'): add(y,r,SRC[y],'Iowa SOS archive PDF (all daily reports bundled)')
for f in sorted(glob.glob(IA+'/snapshots/AbsenteeCounty_*.pdf')):
    for r in parse(f): add(2026,r,SRC[2026],'Iowa SOS daily file, box snapshot '+os.path.basename(f))
rows=sorted(reps.values(),key=lambda r:(r['year'],r['report_date']))
# 2026 receipt-method breakdown from latest statewide PDF
meth={}
sw=sorted(glob.glob(IA+'/snapshots/AbsenteeStateWide_*.pdf'))
if sw:
    t=subprocess.run(['pdftotext','-layout',sw[-1],'-'],capture_output=True,text=True).stdout
    for m in re.finditer(r'^\s{3,}([A-Za-z /-]+?)\s{2,}(\d+)\s+(\d+)(?:\s+(\d+))?\s*$',t,re.M):
        k=m.group(1).strip()
        if k.startswith('Ballot not yet') or k in ('Democrat','Republican','No Party','Other','Libertarian','Green'): continue
        meth[k]=meth.get(k,0)+int(m.group(4) or 0)
    meth={'_file':os.path.basename(sw[-1]),**meth}
cols=['year','report_date','days_out','requested','issued','received','rec_D','rec_R','rec_NP','rec_O','req_D','req_R','req_NP','req_O','source_url','note']
with open(ROOT+'/site/ia-data.csv','w',newline='') as f:
    w=csv.DictWriter(f,cols); w.writeheader(); w.writerows(rows)
open(ROOT+'/site/ia-data.js','w').write('window.IADATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed={k:v.isoformat() for k,v in ED.items()},ev_start=EVSTART,src=SRC,methods26=meth,rows=rows))+';')
print(len(rows),'rows'); print(meth)
for y in ED: print(y,[(r['days_out'],r['received']) for r in rows if r['year']==y and 15<=r['days_out']<=21])
