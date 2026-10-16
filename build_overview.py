#!/usr/bin/env python3
"""Multi-state overview: reads each state's site/*-data.csv, puts every state on the same days-before-Election-Day point,
and computes 2026 pace vs 2018/2022/2024, a combined total, and party-share shifts. -> site/overview-data.js"""
import csv,json,os,datetime as dt,collections
S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'site')
rd=lambda f:list(csv.DictReader(open(os.path.join(S,f))))
I=lambda v:int(float(v)) if v not in(None,'') else None
def cum_daily(rows):  # rows: (year,days_out,n,D,R,date) daily -> cumulative by days_out
    out=collections.defaultdict(dict)
    for y in set(r[0] for r in rows):
        rs=sorted([r for r in rows if r[0]==y],key=lambda r:-r[1]); c=[0,0,0]
        for _,d,n,D,R,date in rs:
            c=[c[0]+n,c[1]+(D or 0),c[2]+(R or 0)]; out[y][d]=dict(total=c[0],D=c[1],R=c[2],date=date)
    return out
ST={}
# Florida: mail ballots returned (early in-person not open yet)
s=collections.defaultdict(dict)
for r in rd('data.csv'):
    if r['method']=='vbm_returned' and int(r['days_out'])>0: s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['total']),D=I(r['dem']),R=I(r['rep']),date=r['report_date'])
ST['FL']=dict(name='Florida',page='index.html',metric='Mail ballots returned',series=s,note='FL early in-person voting had not started at this point. Past-cycle points are from news reports citing FL DOS.')
# Ohio: total early votes (absentee returned + early in person)
s=collections.defaultdict(dict)
for r in rd('ohio-data.csv'):
    if r['metric']=='total_early' and not r['approx']: s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['value']),D=None,R=None,date=r['report_date'])
ST['OH']=dict(name='Ohio',page='ohio.html',metric='Total early votes (mail + in person)',series=s,note='OH SOS releases are sporadic; 2026 has one statewide point so far. SB 293 (2026) requires mail ballots to arrive by Election Day.')
# North Carolina: daily mail returned + one-stop -> cumulative
nc=[(int(r['year']),int(r['days_out']),I(r['n']),I(r['D']),I(r['R']),r['date']) for r in rd('nc-data.csv')]
TODAY=dt.date.today().isoformat()
s=cum_daily([r for r in nc if not(r[0]==2026 and r[5]>TODAY)])
ST['NC']=dict(name='North Carolina',page='nc.html',metric='Mail returned + early in person (one-stop)',series=s,note='NC one-stop early voting started Oct 15, 2026 (Oct 20 in 2022, Oct 17 in 2018 and 2024).')
# Iowa
s=collections.defaultdict(dict)
for r in rd('ia-data.csv'):
    if I(r['received']) is not None: s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['received']),D=I(r['rec_D']),R=I(r['rec_R']),date=r['report_date'])
ST['IA']=dict(name='Iowa',page='ia.html',metric='Absentee ballots received (mail + in person)',series=s,note='Iowa cut early voting from 29 to 20 days in 2021, so 2018 started earlier.')
# Texas: statewide (2018: 30 largest counties only)
s=collections.defaultdict(dict);t30=collections.defaultdict(dict)
for r in rd('tx-data.csv'):
    tgt=s if r['scope']=='state' else t30
    tgt[int(r['year'])][int(r['days_out'])]=dict(total=I(r['cum_total']),D=None,R=None,date=r['report_date'])
ST['TX']=dict(name='Texas',page='tx.html',metric='Mail + early in-person votes (statewide)',series=s,alt={2018:t30},note='TX early in-person voting starts Oct 19, 2026; mail only so far. 2018 comparison uses the 30 largest counties. No party registration.')
# Michigan
s=collections.defaultdict(dict)
for r in rd('mi-data.csv'):
    s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['total']),D=None,R=None,date=r['date'])
ST['MI']=dict(name='Michigan',page='mi.html',metric='Absentee returned + early in person',series=s,note='2022 = SOS press-release points. Permanent absentee list (2022 Prop 2) sends ballots automatically. No party registration.')
# Maine
s=collections.defaultdict(dict)
for r in rd('me-data.csv'):
    s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['returned']),D=I(r['dem']),R=I(r['rep']),date=r['date'])
ST['ME']=dict(name='Maine',page='me.html',metric='Absentee ballots returned (mail + in person at clerk)',series=s,note='SOS posts the file every few days; latest 2026 point is older than other states. Past years rebuilt from final files.')
# Kansas
s=collections.defaultdict(dict)
for r in rd('ks-data.csv'):
    s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['total']) if r['total'] else I(r['mail_ret']),D=(I(r['mail_ret_d']) or 0)+(I(r['ev_d']) or 0) if r['mail_ret_d'] else None,R=(I(r['mail_ret_r']) or 0)+(I(r['ev_r']) or 0) if r['mail_ret_r'] else None,date=r['date'])
ST['KS']=dict(name='Kansas',page='ks.html',metric='Mail returned + early in person',series=s,note='Early voting began this week. SB 4 (2025) ended the 3-day mail grace period. 2018 has only a 4-days-out point.')
# Arizona: early ballots returned statewide (2018 AZ SOS via Garrett Archer; 2022/2024 Sam Almy tracker; 2026 Stealth Analytics) - secondary sources
s=collections.defaultdict(dict)
for r in rd('az-data.csv'):
    s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['returned']),D=None,R=None,date=r['date'],m=float(r['d_minus_r_pts']) if r['d_minus_r_pts'] else None,dp=float(r['dem_pct']) if r['dem_pct'] else None,rp=float(r['rep_pct']) if r['rep_pct'] else None)
ST['AZ']=dict(name='Arizona',page='az.html',metric='Early ballots returned (mail, all counties)',series=s,secondary=True,note='Secondary sources: 2018 AZ SOS daily update via Garrett Archer; 2022/2024 Sam Almy\'s county-file tracker (AZ Dem. Party), rounded; 2026 Stealth Analytics county-file totals (some county files 1-8 days old).')
# Georgia: accepted mail + early in-person ballots, official SOS absentee files (all years); no party registration
s=collections.defaultdict(dict)
for r in rd('ga-data.csv'):
    if r['total_cum']: s[int(r['year'])][int(r['days_out'])]=dict(total=I(r['total_cum']),D=None,R=None,date=r['date'])
ST['GA']=dict(name='Georgia',page='ga.html',metric='Mail returned + early in person (accepted)',series=s,note='Official SOS voter files for every year; 2026 file loaded by hand (as-of date on page). Early voting began Oct 13, 2026 (Oct 15 in 2018/2024, Oct 17 in 2022). No party registration.')
PRES={2024}
out=[];comb={}
for k,st in ST.items():
    s=st['series']; d26=min(s[2026]); cur=s[2026][d26]; comps={}
    for y in (2018,2022,2024):
        ser26,past=s[2026],s.get(y,{})
        if y in st.get('alt',{}): ser26=st['alt'][y][2026] if 2026 in st['alt'][y] else {}; past=st['alt'][y].get(y,{})
        common=[d for d in past if d in ser26 and d26<=d<=d26+3]
        if common: d=min(common); a,b=ser26[d],past[d]; ex=True
        else:
            near=[d for d in past if abs(d-d26)<=2]
            if not near: continue
            d=min(near,key=lambda x:(abs(x-d26),x)); a,b=ser26[d26],past[d]; ex=False
        c=dict(days26=[x for x in ser26 if ser26[x] is a][0],days_past=d,v26=a['total'],vpast=b['total'],date26=a['date'],datepast=b['date'],pct=round((a['total']/b['total']-1)*100,1),exact=ex,
               scope='30 largest counties' if y in st.get('alt',{}) else 'statewide')
        # party: D-R share of ballots. Use the matched day if both sides have it; else nearest pair (each within 2 days of the
        # 2026 latest point, past within 2 days of the 2026 day) where both sides have party data, flagged party_exact=False.
        M=lambda e:e.get('m') if e.get('m') is not None else (round((e['D']-e['R'])/e['total']*100,1) if e.get('D') is not None and e.get('R') is not None else None)
        pairs=[(abs(x-d26)+abs(z-x),x!=z,x,z) for x in ser26 if x-d26<=2 and M(ser26[x]) is not None for z in past if abs(z-x)<=2 and M(past[z]) is not None]
        if pairs:
            _,_,x,z=min(pairs); A,Bp=ser26[x],past[z]
            c.update(m26=M(A),mpast=M(Bp),party_days26=x,party_dayspast=z,party_date26=A['date'],party_datepast=Bp['date'],party_exact=(x==z))
            if A.get('D') is not None: c.update(d26=round(A['D']/A['total']*100,1),r26=round(A['R']/A['total']*100,1))
            if Bp.get('D') is not None: c.update(dpast=round(Bp['D']/Bp['total']*100,1),rpast=round(Bp['R']/Bp['total']*100,1))
        comps[y]=c
    out.append(dict(code=k,secondary=st.get('secondary',False),name=st['name'],page=st['page'],metric=st['metric'],note=st['note'],days_out=d26,date=cur['date'],v26=cur['total'],comps=comps))
for y in (2018,2022,2024):
    inc=[o for o in out if y in o['comps'] and o['comps'][y]['exact'] and o['comps'][y]['scope']=='statewide']
    comb[y]=dict(states=[o['code'] for o in inc],v26=sum(o['comps'][y]['v26'] for o in inc),vpast=sum(o['comps'][y]['vpast'] for o in inc))
    if comb[y]['vpast']: comb[y]['pct']=round((comb[y]['v26']/comb[y]['vpast']-1)*100,1)
open(os.path.join(S,'overview-data.js'),'w').write('window.OVDATA='+json.dumps(dict(built=dt.datetime.now().strftime('%b %-d, %Y %-I:%M %p ET'),states=out,combined=comb))+';')
for o in out: print(o['code'],o['days_out'],o['v26'],{y:(c['days_past'],c['days26'],c['pct'],c['exact'],c.get('m26'),c.get('mpast'),c.get('party_days26'),c.get('party_dayspast')) for y,c in o['comps'].items()})
print(comb)
