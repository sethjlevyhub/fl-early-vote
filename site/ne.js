(function(){
const N=NEDATA,f=n=>n==null?'—':Number(n).toLocaleString('en-US'),kf=v=>Math.abs(v)>=1e6?(v/1e6)+'M':(v/1e3)+'K',ps=v=>`${v>0?'+':''}${v.toFixed(1)}%`,lead=v=>v==null?'—':(v>=0?'D+':'R+')+Math.abs(v).toFixed(1);
const COL={2026:'#e4572e',2024:'#4c6ef5',2022:'#2b9348',2018:'#9c6ade'};Chart.defaults.font.family='system-ui,sans-serif';
const kpi=(lab,val,sub,c='')=>`<div class="card kpi"><div class="lab">${lab}</div><div class="val ${c}">${val}</div><div class="sub">${sub}</div></div>`;
const opt=(ylab,max=36,min=-1)=>({maintainAspectRatio:false,parsing:false,scales:{x:{type:'linear',reverse:true,min,max,title:{display:true,text:'Days before Election Day'}},y:{ticks:{callback:kf},title:{display:!!ylab,text:ylab}}},plugins:{tooltip:{callbacks:{title:c=>c[0].parsed.x+' days out'}}}});
const M=v=>(v.D-v.R)/v.T*100;
const C=N.civic.state.filter(x=>x.cast),cur=C[C.length-1],cc=cur.cast,rq=cur.req;
const n2=(sc,y)=>N.ne2.filter(r=>r.scope==sc&&r.year==y).sort((a,b)=>b.days_out-a.days_out);
const s26=n2('state',2026),s22=n2('state',2022),l26=s26[s26.length-1],l22=s22.find(r=>r.days_out==l26.days_out);
const e26=n2('NE-2',2026),e22=n2('NE-2',2022),m26=e26[e26.length-1],m22=e22.find(r=>r.days_out==m26.days_out);
const O=(y,met,sc='state')=>N.official.find(r=>r.year==y&&r.metric==met&&r.scope==sc);
const pct=(a,b)=>(a/b-1)*100,reg=N.reg.state,rn2=N.reg['NE-2'];
document.getElementById('asof').textContent=`State file of ${cur.date} (votes through ${cur.through}, ${cur.days_out} days out) · 2026 via civicAPI † · 2022 via @NE2EarlyVote † · official SOS checkpoints`;
document.getElementById('built').textContent=N.built;
const rr=k=>(cur.cast[k]/rq[k]*100);
document.getElementById('kpis').innerHTML=
 kpi('2026 early votes cast †',`<span style="color:${COL[2026]}">${f(cc.T)}</span>`,`mail ${f(cur.ret.T)} + in person ${f(cur.ip.T)} · D ${f(cc.D)} · R ${f(cc.R)} · other ${f(cc.O)}`)+
 kpi('2026 party lead †',lead(M(cc)),`at this point in 2022: ${lead(l22.dem_minus_rep_pts)} (@NE2EarlyVote †)`)+
 kpi('vs 2022, same day †',`<span class="${l26.total_cast>=l22.total_cast?'up':'down'}">${ps(pct(l26.total_cast,l22.total_cast))}</span>`,`${f(l26.total_cast)} vs ${f(l22.total_cast)}, ${l26.days_out} days out (@NE2EarlyVote's counts for both years)`)+
 kpi('2026 ballots requested †',f(rq.T),`D ${f(rq.D)} · R ${f(rq.R)} · other ${f(rq.O)} · ${(cc.T/rq.T*100).toFixed(0)}% returned`)+
 kpi('NE-2 early votes cast †',f(m26.total_cast),`${lead(m26.dem_minus_rep_pts)} vs ${lead(m22.dem_minus_rep_pts)} in 2022 (${f(m22.total_cast)} votes)`)+
 kpi('Registered voters (official)',`R ${(reg.rep/reg.total*100).toFixed(0)}% · D ${(reg.dem/reg.total*100).toFixed(0)}%`,`nonpartisan/other ${((reg.nonpartisan+reg.other)/reg.total*100).toFixed(0)}% · SOS, ${reg.asof}`);
const fin=y=>O(y,'final_early').value+O(y,'final_allmail').value;
document.getElementById('take').innerHTML=[
 `Nebraskans have cast <b>${f(cc.T)}</b> early votes (mail returned plus in person) through ${cur.through}, ${cur.days_out} days out †. Registered Democrats lead Republicans by <b>${M(cc).toFixed(1)} points</b> of those votes, in a state where Republicans outnumber Democrats on the rolls about 49% to 26%.`,
 `Against 2022 at the same point, @NE2EarlyVote's state-file counts show early votes <b>${ps(pct(l26.total_cast,l22.total_cast))}</b> (${f(l26.total_cast)} vs ${f(l22.total_cast)}) and the party lead at ${lead(l26.dem_minus_rep_pts)} vs ${lead(l22.dem_minus_rep_pts)} †. The 2026 Democratic lead has been shrinking since Oct 12 (${lead(s26.find(r=>r.days_out==21).dem_minus_rep_pts)}), which @NE2EarlyVote attributes to ballots from all-mail precincts starting to come back.`,
 `In <b>NE-2 (Omaha)</b>, volume is even with 2022 (${f(m26.total_cast)} vs ${f(m22.total_cast)}) but the lead is ${lead(m26.dem_minus_rep_pts)} vs ${lead(m22.dem_minus_rep_pts)} †.`,
 `Requests by party: Republicans ${f(rq.R)}, Democrats ${f(rq.D)}, other ${f(rq.O)} †. Democrats have returned ${rr('D').toFixed(0)}% of theirs and Republicans ${rr('R').toFixed(0)}%, so the gap may narrow as more Republican ballots come back.`,
 `For scale, the official canvass counted ${f(fin(2018))} early ballots in 2018, ${f(fin(2022))} in 2022 and ${f(fin(2024))} in 2024 (presidential).`,
 `<b>Senate race:</b> Osborn is an independent, so these party splits don't show his support. Nonpartisan and minor-party voters cast ${(cc.O/cc.T*100).toFixed(0)}% of early votes so far †.`].map(s=>`<li>${s}</li>`).join('');
const ds=(lab,pts,col,o={})=>Object.assign({label:lab,data:pts,borderColor:col,backgroundColor:col,borderWidth:2,pointRadius:3},o);
const sc=(pts)=>pts.map(r=>({x:r.days_out,y:r.total_cast}));
const o24=N.official.filter(r=>r.year==2024&&r.metric=='cast'&&r.scope=='state').map(r=>({x:r.days_out,y:r.value}));
const r18=O(2018,'requested'),nr18=O(2018,'not_returned');
new Chart(document.getElementById('cum'),{type:'line',data:{datasets:[
 ds('2026 † civicAPI',C.map(x=>({x:x.days_out,y:x.cast.T})),COL[2026],{borderWidth:4}),
 ds('2026 † @NE2EarlyVote',sc(s26),COL[2026],{showLine:false,pointRadius:5,pointStyle:'rectRot'}),
 ds('2022 † @NE2EarlyVote',sc(s22),COL[2022],{pointRadius:5}),
 ds('2024 official (SOS)',o24,COL[2024],{pointRadius:6}),
 ds('2018 † derived (AP/SOS)',[{x:r18.days_out,y:r18.value-nr18.value}],COL[2018],{showLine:false,pointRadius:6,backgroundColor:'#fff'})]},
 options:(o=>{o.plugins.tooltip.callbacks.label=c=>`${c.dataset.label}: ${f(c.parsed.y)}`;return o})(opt('Early votes cast',35))});
new Chart(document.getElementById('lead'),{type:'line',data:{datasets:[
 ds('2026 † civicAPI',C.filter(x=>x.cast.T>=5000).map(x=>({x:x.days_out,y:+M(x.cast).toFixed(2)})),COL[2026],{borderWidth:4}),
 ds('2026 † @NE2EarlyVote',s26.map(r=>({x:r.days_out,y:r.dem_minus_rep_pts})),COL[2026],{showLine:false,pointRadius:5,pointStyle:'rectRot'}),
 ds('2022 † @NE2EarlyVote',s22.map(r=>({x:r.days_out,y:r.dem_minus_rep_pts})),COL[2022],{pointRadius:5})]},
 options:(o=>{o.scales.y.ticks.callback=v=>(v>=0?'D+':'R+')+Math.abs(v);o.scales.y.title.text='D minus R, points';return o})(opt('pts',30))});
new Chart(document.getElementById('party'),{type:'bar',data:{labels:['Democrats','Republicans','Other / nonpartisan'],datasets:[
 {label:'Requested',data:['D','R','O'].map(k=>rq[k]),backgroundColor:'#c7d2fe'},
 {label:'Returned + in person',data:['D','R','O'].map(k=>cc[k]),backgroundColor:['#2f6fdb','#d64545','#8a8f98']}]},
 options:{maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${f(c.parsed.y)}`+(c.datasetIndex==1?` (${rr(['D','R','O'][c.dataIndex]).toFixed(0)}% of requests)`:'')}}},scales:{y:{ticks:{callback:kf}}}}});
// NE-2
const ip=N.ne2_extra,gx=(y,m)=>(ip.find(r=>r.year==y&&r.metric==m)||{}).value;
const DG=N.civic.Douglas.filter(x=>x.cast),dl=DG[DG.length-1];
document.getElementById('n2kpis').innerHTML=
 kpi('NE-2 votes cast †',f(m26.total_cast),`2022 same day: ${f(m22.total_cast)} · through ${m26.through}`)+
 kpi('NE-2 party lead †',lead(m26.dem_minus_rep_pts),`2022: ${lead(m22.dem_minus_rep_pts)}`)+
 kpi('NE-2 independents returned †',f(gx('2026','independent_returned')),`${gx('2026','independent_share_pct')}% of returns (2022: ${f(gx('2022','independent_returned'))}, ${gx('2022','independent_share_pct')}%) · 19 days out`)+
 kpi('Douglas County cast †',f(dl.cast.T),`${lead(M(dl.cast))} · ${(dl.cast.T/dl.req.T*100).toFixed(0)}% of ${f(dl.req.T)} requests · file ${dl.date}`)+
 kpi('NE-2 registered (official)',`R ${(rn2.rep/rn2.total*100).toFixed(1)}% · D ${(rn2.dem/rn2.total*100).toFixed(1)}%`,`nonpartisan ${(rn2.nonpartisan/rn2.total*100).toFixed(1)}% · SOS ${rn2.asof}`);
new Chart(document.getElementById('n2cum'),{type:'line',data:{datasets:[ds('2026 †',sc(e26),COL[2026],{borderWidth:4}),ds('2022 †',sc(e22),COL[2022])]},options:(o=>{o.plugins.tooltip.callbacks.label=c=>`${c.dataset.label}: ${f(c.parsed.y)}`;return o})(opt('Early votes cast',28,16))});
new Chart(document.getElementById('n2lead'),{type:'line',data:{datasets:[ds('2026 †',e26.map(r=>({x:r.days_out,y:r.dem_minus_rep_pts})),COL[2026],{borderWidth:4}),ds('2022 †',e22.map(r=>({x:r.days_out,y:r.dem_minus_rep_pts})),COL[2022])]},options:(o=>{o.scales.y.ticks.callback=v=>'D+'+v;o.scales.y.beginAtZero=true;return o})(opt('D minus R, points',28,16))});
new Chart(document.getElementById('doug'),{type:'bar',data:{labels:DG.map(x=>x.date.slice(5)),datasets:[['D','Democrats','#2f6fdb'],['R','Republicans','#d64545'],['O','Other / nonpartisan','#8a8f98']].map(([k,l,c])=>({label:l,data:DG.map(x=>x.cast[k]),backgroundColor:c,stack:'s'}))},options:{maintainAspectRatio:false,plugins:{tooltip:{callbacks:{footer:it=>{const x=DG[it[0].dataIndex];return`Total ${f(x.cast.T)} · ${lead(M(x.cast))} · ${(x.cast.T/x.req.T*100).toFixed(0)}% of requests`}}}},scales:{x:{stacked:true,title:{display:true,text:'State file date'}},y:{stacked:true,ticks:{callback:kf}}}}});
document.getElementById('n2tab').innerHTML='<table><tr><th>Days out (votes through)</th><th>2026 cast</th><th>2026 lead</th><th>2022 cast</th><th>2022 lead</th><th>Volume</th></tr>'+e26.slice().reverse().map(r=>{const p=e22.find(z=>z.days_out==r.days_out);return`<tr><td>${r.days_out} (${r.through.slice(5)})</td><td>${f(r.total_cast)}</td><td>${lead(r.dem_minus_rep_pts)}</td><td>${f(p.total_cast)}</td><td>${lead(p.dem_minus_rep_pts)}</td><td>${ps(pct(r.total_cast,p.total_cast))}</td></tr>`}).join('')+'</table><p class="hint">All figures @NE2EarlyVote (†). Douglas County checkpoints from news reports (†): 2024, 28 days out: 97,495 mail ballots sent, 12,960 returned (KETV). 2022, 5 days out: about 102,000 sent, more than 72,000 back (WOWT). Final Douglas early votes (official canvass): '+[2018,2022,2024].map(y=>`${y} ${f(O(y,'final_early','Douglas').value)}`).join(', ')+'.</p>';
new Chart(document.getElementById('fin'),{type:'bar',data:{labels:['2018','2022','2024 (pres.)'],datasets:[{label:'Early voting',data:[2018,2022,2024].map(y=>O(y,'final_early').value),backgroundColor:[COL[2018],COL[2022],COL[2024]],stack:'a'},{label:'All-mail precincts',data:[2018,2022,2024].map(y=>O(y,'final_allmail').value),backgroundColor:'#c9a227',stack:'a'},{label:'Douglas County early',data:[2018,2022,2024].map(y=>O(y,'final_early','Douglas').value),backgroundColor:'#14213d',stack:'b'}]},options:{maintainAspectRatio:false,plugins:{tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${f(c.parsed.y)}`}}},scales:{x:{stacked:true},y:{stacked:true,ticks:{callback:kf}}}}});
// counties
const CT=Object.entries(N.counties).map(([c,v])=>{const r=v.returned||{},i=v.inperson||{},q=v.requested||{},T=o=>(o.D||0)+(o.R||0)+(o.O||0),k={D:(r.D||0)+(i.D||0),R:(r.R||0)+(i.R||0),O:(r.O||0)+(i.O||0)};k.T=T(k);return{c,q:T(q),k}}).sort((a,b)=>b.k.T-a.k.T);
const NE2C={Douglas:'NE-2',Saunders:'NE-2',Sarpy:'NE-1/NE-2 split'};
document.getElementById('ctab').innerHTML='<table><tr><th>County</th><th>Requested</th><th>Cast</th><th>% back</th><th>D−R</th></tr>'+CT.filter((x,i)=>i<12||NE2C[x.c]).map(x=>`<tr><td>${x.c}${NE2C[x.c]?` <span class="pill">${NE2C[x.c]}</span>`:''}</td><td>${f(x.q)}</td><td>${f(x.k.T)}</td><td>${x.q?(x.k.T/x.q*100).toFixed(0)+'%':'—'}</td><td>${x.k.T?lead(M(x.k)):'—'}</td></tr>`).join('')+`</table><p class="hint">civicAPI county file of ${(Object.values(N.counties)[0]||{}).date}. Counties with all-mail precincts list those ballots as requested. All 93 counties are in <a href="ne-data.js">ne-data.js</a>.</p>`;
document.getElementById('xtab').innerHTML='<table class="xc"><tr><th>State file date</th><th>civicAPI cast</th><th>@NE2EarlyVote cast</th><th>Diff</th><th>Lead (civicAPI / @NE2EarlyVote)</th></tr>'+N.xcheck.map(x=>`<tr><td>${x.date}</td><td>${f(x.civic)}</td><td>${f(x.ne2)}</td><td>${ps(x.diff_pct)}</td><td>${lead(x.civic_m)} / ${lead(x.ne2_m)}</td></tr>`).join('')+'</table>';
})();
