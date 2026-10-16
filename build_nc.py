#!/usr/bin/env python3
"""NC early vote: /workspace/nc-earlyvote/agg/<year>.csv (from aggregate_nc.py on NCSBE statewide files)
-> site/nc-data.csv + site/nc-data.js. Daily counts by date ballot was cast/accepted; cumulative computed in page."""
import pandas as pd, json, os, glob, datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__)); A='/workspace/nc-earlyvote/agg'
ED={2018:'2018-11-06',2022:'2022-11-08',2024:'2024-11-05',2026:'2026-11-03'}
URL={y:f"https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/{e.replace('-','_')}/absentee_{e.replace('-','')}.zip" for y,e in ED.items()}
EV={2018:'2018-10-17',2022:'2022-10-20',2024:'2024-10-17',2026:'2026-10-15'}
P={'DEM':'D','REP':'R','UNA':'U'}
# race/ethnicity groups (self-reported on registration). Hispanic = ethnicity HISPANIC (any race); other groups non-Hispanic or ethnicity undesignated.
# 2018 file has no ethnicity column -> race_H is blank (None) for 2018.
RK='WBHAOU'
def reth(race,eth):
    if eth=='HISP': return 'H'
    return {'WHITE':'W','BLACK':'B','ASIAN':'A','UNDESIGNATED':'U','OTHER/UNDESIGNATED':'O'}.get(race,'O')
out=[]
for y,e in ED.items():
    a=pd.read_csv(f'{A}/{y}.csv'); a=a[a.metric.isin(['onestop','mail_ret'])].copy()
    a['do']=(pd.to_datetime(e)-pd.to_datetime(a.date)).dt.days
    a['p']=a.party.map(P).fillna('O')
    if 'eth' not in a: a['eth']='NA'
    a['r']=[reth(r,e) for r,e in zip(a.race,a.eth.fillna('NA'))]
    # everything earlier than 40 days out is rolled into day 40 (early UOCAVA/odd dates) so cumulative totals stay exact
    a.loc[a.do>40,'do']=40; a=a[a.do>=-30]
    for (m,do),g in a.groupby(['metric','do']):
        row=dict(year=y,metric=m,days_out=int(do),date=(pd.to_datetime(e)-pd.Timedelta(days=int(do))).date().isoformat(),n=int(g.n.sum()))
        row.update({k:int(g[g.p==k].n.sum()) for k in 'DRUO'}); row.update({'race_'+k:int(g[g.r==k].n.sum()) for k in RK})
        out.append(row)
df=pd.DataFrame(out).sort_values(['year','metric','days_out'],ascending=[True,True,False])
df.to_csv(ROOT+'/site/nc-data.csv',index=False)
snap=os.path.realpath('/workspace/nc-earlyvote/snapshots/cur.zip')
meta=dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed=ED,ev_start=EV,urls=URL,snapshot=os.path.basename(snap),
  file_posted=dt.datetime.strptime(os.path.basename(snap).split('_')[2][:8],'%Y%m%d').date().isoformat())
open(ROOT+'/site/nc-data.js','w').write('window.NCDATA='+json.dumps(dict(meta,rows=df.to_dict('records')))+';')
print(len(df),'rows')
