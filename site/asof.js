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
var W=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];function wd(s){return W[new Date(s.slice(0,10)+'T12:00:00Z').getUTCDay()]+' '+md(s)}
(function(){var st=document.createElement('style');st.textContent='.lastposted{font-size:.8rem;color:#667085;margin-top:3px}.lastposted b{font-size:.8rem;font-weight:600;color:#1d2330}.lpgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:4px 10px;margin-top:6px}.lpgrid a{font-size:.76rem;line-height:1.3;color:#1d2330;text-decoration:none;border-left:3px solid #d0d5dd;padding:1px 0 1px 6px}.lpgrid a.stale{border-left-color:#e0a94a;background:#fff7e0}.lpgrid a.none{color:#667085}.lpgrid small{display:block;color:#667085;font-size:.72rem}.lphint{font-size:.78rem;color:#667085;margin-top:4px}';document.head.appendChild(st)})();
// "State last posted" text from data_asof.lastposted (asof_stamp.py). Post date shown only when the file carries one.
function lpText(L,short){if(!L||L.status!='ok')return short?['not posted yet','']:'2026 data not posted yet';
  var th=L.through?'data through '+md(L.through):'',sec=L.who=='Source'?' †':'';
  if(L.posted){var p=wd(L.posted)+(L.posted_time&&!short?', '+t12(L.posted_time)+' ET':'');
    return short?[(L.prefix&&L.prefix.indexOf('Official')==0?'file loaded ':'posted ')+wd(L.posted)+sec,th]:'<b>'+esc(L.prefix)+':</b> '+p+(th?' ('+th+')':'')+sec}
  var dd=L.through||L.data_date;return short?['data '+wd(dd)+sec,'post date not published']:'<b>Latest data:</b> '+(L.through?'through ':'')+wd(dd)+sec+' <span title="'+esc(L.basis)+'">(post date not published)</span>'}
// Business-day staleness: count weekdays after the file date up to today (ET), so weekend gaps don't count. Daily/frequent sources
// (cadence <= 3 days) are flagged at 2+ business days; slower ones (Maine, Minnesota) after their cadence in business days.
// Also flagged: an official file when a newer secondary total exists (Georgia). Federal holidays are not excluded.
function bizAge(s){var d=new Date(s.slice(0,10)+'T12:00:00Z'),t=new Date(todayET()+'T12:00:00Z'),n=0;while(d<t){d.setUTCDate(d.getUTCDate()+1);var w=d.getUTCDay();if(w&&w<6)n++}return n}
function lim(a){return a.cadence_days<=3?1:Math.ceil(a.cadence_days*5/7)}
function staleOf(a){if(a.status!='ok')return '';var L=a.lastposted||{};if(L.secondary_newer)return 'newer';return bizAge(a.date)>lim(a)?'old':''}
function esc(s){return String(s).replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
if(A.states){ // overview
  var S=A.states,ks=Object.keys(S),ok=ks.filter(function(k){return S[k].status=='ok'}),ds=ok.map(function(k){return S[k].date}).sort();
  var h='<b>Data as of '+(ds.length?(ds[0]==ds[ds.length-1]?md(ds[0]):(ds[0].slice(5,7)==ds[ds.length-1].slice(5,7)?md(ds[0])+'–'+(+ds[ds.length-1].slice(8,10)):md(ds[0])+' – '+md(ds[ds.length-1])))+', '+ds[0].slice(0,4):'—')+'</b> · each state reports on its own schedule. Latest file by state:<div class="lpgrid">';
  h+=ks.map(function(k){var a=S[k],st=a.status!='ok'?' none':(staleOf(a)?' stale':'');
    var t=lpText(a.lastposted,true),sn=a.lastposted&&a.lastposted.secondary_newer;
    return '<a class="'+st.trim()+'" href="'+a.page+'" title="'+esc(a.name+': '+(a.status=='ok'?a.label:'2026 data not yet posted')+' · '+a.source+(a.lastposted&&a.lastposted.basis?' · post date = '+a.lastposted.basis:''))+'"><b>'+k+'</b> '+t[0]+(st==' stale'?' ⚠':'')+(t[1]?'<small>'+t[1]+'</small>':'')+(sn?'<small>newer secondary total: through '+md(sn.through)+' †</small>':'')+'</a>'}).join('')+'</div><div class="lphint">Some states and sources don\'t post on weekends, so a Friday date can still be the newest file. † = secondary source.</div>';
  el.innerHTML=h;return}
if(A.status!='ok'){el.classList.add('none');el.innerHTML='<b>'+esc(A.label)+'</b> · '+esc(A.source)+(A.note?' · '+esc(A.note):'');return}
var n=bizAge(A.date),h='',sv=staleOf(A);
if(sv=='newer'){el.classList.add('stale');h+='<span class="stalewarn">⚠ Newer data exists than this official file (secondary total through '+md(A.lastposted.secondary_newer.through)+').</span> '}
else if(sv){el.classList.add('stale');h+='<span class="stalewarn">⚠ Not updated in '+n+' business days.</span> '}
h+='<b>Data as of '+esc(A.label)+'</b>';
if(A.time&&A.time_kind=='checked')h+=' (checked '+t12(A.time)+' ET)';
if(A.through&&A.through!=A.date)h+=' · ballots through '+md(A.through);
h+=' · '+esc(A.source)+(A.secondary?' <span title="secondary source">†</span>':'');
if(A.note)h+=' · '+esc(A.note);
if(A.lastposted)h+='<div class="lastposted">'+lpText(A.lastposted,false)+'</div>';
el.innerHTML=h;
})();
