/* Renders the "Data as of" bar from the data_asof block that asof_stamp.py writes into each data file during the daily build.
   <div class="asofbar" id="dataasof" data-var="FLDATA"></div> ; overview uses data-var="OVDATA". Staleness is checked against today's date in ET. */
(function(){
var el=document.getElementById('dataasof');if(!el)return;var D=window[el.dataset.var];var A=D&&D.data_asof;
if(!A){el.style.display='none';return}
var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function md(s){return M[+s.slice(5,7)-1]+' '+(+s.slice(8,10))}
function t12(h){var a=+h.slice(0,2),m=h.slice(3,5);return (a%12||12)+':'+m+(a<12?' AM':' PM')}
function todayET(){try{return new Intl.DateTimeFormat('en-CA',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())}catch(e){return new Date().toISOString().slice(0,10)}}
function age(s){return Math.round((Date.parse(todayET()+'T12:00:00Z')-Date.parse(s.slice(0,10)+'T12:00:00Z'))/864e5)}
function esc(s){return String(s).replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
if(A.states){ // overview
  var S=A.states,ks=Object.keys(S),ok=ks.filter(function(k){return S[k].status=='ok'}),ds=ok.map(function(k){return S[k].date}).sort();
  var h='<b>Data as of '+(ds.length?(ds[0]==ds[ds.length-1]?md(ds[0]):(ds[0].slice(5,7)==ds[ds.length-1].slice(5,7)?md(ds[0])+'–'+(+ds[ds.length-1].slice(8,10)):md(ds[0])+' – '+md(ds[ds.length-1])))+', '+ds[0].slice(0,4):'—')+'</b> · each state reports on its own schedule; latest report by state:<div class="asofchips">';
  h+=ks.map(function(k){var a=S[k],st=a.status!='ok'?' none':(age(a.date)>a.cadence_days?' stale':'');
    return '<a class="chip'+st+'" href="'+a.page+'" title="'+esc(a.name+': '+(a.status=='ok'?a.label:'2026 data not yet posted')+' · '+a.source)+'">'+k+' '+(a.status=='ok'?md(a.date):'not posted')+(st==' stale'?' ⚠':'')+'</a>'}).join('')+'</div>';
  el.innerHTML=h;return}
if(A.status!='ok'){el.classList.add('none');el.innerHTML='<b>'+esc(A.label)+'</b> · '+esc(A.source)+(A.note?' · '+esc(A.note):'');return}
var n=age(A.date),h='';
if(n>A.cadence_days){el.classList.add('stale');h+='<span class="stalewarn">⚠ Not updated in '+n+' days.</span> '}
h+='<b>Data as of '+esc(A.label)+'</b>';
if(A.time&&A.time_kind=='checked')h+=' (checked '+t12(A.time)+' ET)';
if(A.through&&A.through!=A.date)h+=' · ballots through '+md(A.through);
h+=' · '+esc(A.source)+(A.secondary?' <span title="secondary source">†</span>':'');
if(A.note)h+=' · '+esc(A.note);
el.innerHTML=h;
})();
