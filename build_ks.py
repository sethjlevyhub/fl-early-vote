#!/usr/bin/env python3
"""Kansas advance voting (mail + early in person), by days before Election Day, with party.
2022/2024/2026 daily: IKE Lab (Wichita State Univ.) statewide tables compiled from the KS SOS daily advance-voting reports;
2026 cross-checked against the official KS SOS Power BI dashboard. 2018: one SOS press-release point.
Rows are dated by report date (issued each weekday morning, covering the prior day). -> site/ks-data.csv + ks-data.js"""
import re,html,gzip,json,csv,os,datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__)); KS='/workspace/ks-earlyvote'
ED={2018:dt.date(2018,11,6),2022:dt.date(2022,11,8),2024:dt.date(2024,11,5),2026:dt.date(2026,11,3)}
IKE={2022:(KS+'/raw/ike_221108_Statewide.html','https://ike-lab.com/dailyev_221108_Statewide.html'),
     2024:(KS+'/raw/ike_241105_Statewide.html','https://ike-lab.com/dailyev_241105_Statewide.html'),
     2026:(KS+'/snapshots/ike_latest.gz','https://ike-lab.com/dailyev_261103_Statewide.html')}
MO={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
N=lambda s:int(s.replace(',',''))
rows={}
for y,(p,u) in IKE.items():
    t=(gzip.open(p).read() if p.endswith('.gz') else open(p,'rb').read()).decode('utf-8','replace')
    t=html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<style.*?</style>','',t,flags=re.S))); t=re.sub(r'\s+',' ',t)
    mail,ev=t.split('Early In-Person Ballots')[0].split('Mail-in Ballots')[1],t.split('Early In-Person Ballots')[1]
    for m in re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d+) ([\d,]+) ([\d,]+) [\d.]+% ([\d,]+) ([\d,]+) [\d.]+% ([\d,]+) ([\d,]+) [\d.]+% ([\d,]+) ([\d,]+) [\d.]+%',mail):
        d=dt.date(y,MO[m[1]],int(m[2]))
        if d>ED[y]: continue
        r=rows.setdefault((y,d),dict(year=y,date=d.isoformat(),days_out=(ED[y]-d).days))
        r.update(mail_ret=N(m[3]),mail_sent=N(m[4]),mail_ret_d=N(m[5]),mail_ret_r=N(m[7]),mail_ret_u=N(m[9]),source=u)
    for m in re.finditer(r'(October|November|September) (\d+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)(?= (?:October|November|September|$)| *$)',ev.split('Support')[0]+' '):
        d=dt.date(y,MO[m[1]],int(m[2]))
        if d>ED[y]: continue
        r=rows.setdefault((y,d),dict(year=y,date=d.isoformat(),days_out=(ED[y]-d).days,source=u))
        r.update(ev=N(m[3]),ev_d=N(m[4]),ev_r=N(m[5]),ev_u=N(m[6]))
PR='https://www.sos.ks.gov/media/press-releases/2022/11-04-22-secretary-of-state-announces-general-election-voter-turnout-prediction.html'
rows[(2018,0)]=dict(year=2018,date='2018-11-02',days_out=4,mail_sent=193627,mail_ret=122089,source=PR+' ("during the 2018 general election", same period as Nov 4, 2022)')
K=['year','date','days_out','mail_sent','mail_ret','mail_ret_d','mail_ret_r','mail_ret_u','ev','ev_d','ev_r','ev_u','total','source']
out=[]
for r in sorted(rows.values(),key=lambda r:(r['year'],r['date'])):
    r={k:r.get(k) for k in K}
    if r['year']!=2018: r['ev']=r['ev'] or 0; r['ev_d']=r['ev_d'] or 0; r['ev_r']=r['ev_r'] or 0; r['ev_u']=r['ev_u'] or 0
    if r['mail_ret'] is not None and r['ev'] is not None: r['total']=r['mail_ret']+r['ev']
    out.append(r)
sos=json.loads(gzip.open(KS+'/snapshots/sos_latest.gz').read())
sos=[dict(date=dt.datetime.fromtimestamp(x['DATE']/1000,dt.timezone.utc).date().isoformat(),sent=x['sum_ADVANCE VOTING BALLOTS SENT'],returned=x['sum_ADVANCE VOTING BALLOTS RETURNED'],in_person=x['sum_IN PERSON ADVANCE']) for x in sos]
with open(ROOT+'/site/ks-data.csv','w',newline='') as f: w=csv.DictWriter(f,K); w.writeheader(); w.writerows(out)
open(ROOT+'/site/ks-data.js','w').write('window.KSDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),ed={k:v.isoformat() for k,v in ED.items()},sos=sos,rows=out))+';')
c=[r for r in out if r['year']==2026][-1]; D=c['days_out']; print(len(out),'rows; 2026 latest',c)
for y in (2022,2024): print(y,[r for r in out if r['year']==y and r['days_out']>=D][-1:], [r for r in out if r['year']==y][:1])
print('SOS',sos)
