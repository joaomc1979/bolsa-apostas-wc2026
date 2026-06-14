import sys
path = 'index.html'
s = open(path, encoding='utf-8').read()
WC_FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">'''
WC_CSS = '''
/* ===== TAB MUNDIAL (estilo Roadtrip) ===== */
#p-w{--accent:#e8421a;--accent2:#f5a623;--blue:#3498db;}
.wc-sec-label{font-size:11px;text-transform:uppercase;letter-spacing:2px;color:var(--text2);margin:18px 0 10px;font-weight:600;}
.wc-date-nav{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;margin-bottom:14px;padding-bottom:4px;}
.wc-date-nav::-webkit-scrollbar{display:none;}
.wc-date-btn{background:var(--bg3);border:.5px solid var(--border);border-radius:8px;padding:8px 12px;font-size:12px;cursor:pointer;white-space:nowrap;color:var(--text2);}
.wc-date-btn.active{background:#e8421a;border-color:#e8421a;color:#fff;}
.match-card{background:var(--bg2);border:.5px solid var(--border);border-radius:12px;padding:14px;margin-bottom:8px;}
.match-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
.match-group{font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:1px;}
.match-status-badge{font-size:10px;font-weight:700;padding:3px 8px;border-radius:6px;}
.status-live{background:#e8421a;color:#fff;animation:wcpulse 1.5s infinite;}
.status-finished{background:rgba(46,204,113,0.15);color:#1D9E75;}
.status-scheduled{background:rgba(52,152,219,0.15);color:#3498db;}
@keyframes wcpulse{0%,100%{opacity:1}50%{opacity:.5}}
.match-teams-row{display:flex;align-items:center;gap:8px;}
.match-team{flex:1;min-width:0;}
.match-team-name{font-size:14px;font-weight:600;margin-bottom:2px;}
.match-team-flag{font-size:22px;}
.match-team.away{text-align:right;}
.match-score-big{font-family:'Bebas Neue',sans-serif;font-size:30px;color:#e8421a;text-align:center;min-width:58px;line-height:1.05;}
.groups-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.group-card{background:var(--bg2);border:.5px solid var(--border);border-radius:10px;padding:12px;}
.group-title{font-family:'Bebas Neue',sans-serif;font-size:18px;color:#e8421a;margin-bottom:8px;letter-spacing:1px;}
.group-team{display:flex;align-items:center;gap:6px;padding:4px 2px;border-bottom:.5px solid var(--border);font-size:12px;border-radius:4px;}
.group-team:last-child{border-bottom:none;}
.group-pos{font-family:'DM Mono',monospace;font-size:11px;color:var(--text2);width:14px;text-align:center;}
.group-flag{font-size:14px;}
.group-name{flex:1;font-weight:500;}
.group-pts{font-family:'DM Mono',monospace;font-size:12px;font-weight:700;color:#f5a623;}
.group-qual{background:rgba(46,204,113,0.16);}
@media(max-width:520px){.groups-grid{grid-template-columns:1fr;}}
'''
WC_PANEL = '''<div id="p-w" class="panel">
  <div class="wc-sec-label">📅 Jogos do dia</div>
  <div class="wc-date-nav" id="wc-date-nav"></div>
  <div id="wc-matches"></div>
  <div class="wc-sec-label">📊 Grupos</div>
  <div id="wc-groups"></div>
</div>
'''
WC_JS = '''// ── TAB MUNDIAL (grupos + jogos do dia, estilo Roadtrip) ──
const WCFLAGS = {
 'mexico':'🇲🇽','africa do sul':'🇿🇦','coreia do sul':'🇰🇷','chequia':'🇨🇿','canada':'🇨🇦',
 'bosnia':'🇧🇦','eua':'🇺🇸','paraguai':'🇵🇾','catar':'🇶🇦','suica':'🇨🇭','brasil':'🇧🇷',
 'marrocos':'🇲🇦','haiti':'🇭🇹','escocia':'🏴󠁧󠁢󠁳󠁣󠁴󠁿','australia':'🇦🇺','turquia':'🇹🇷','alemanha':'🇩🇪',
 'curacau':'🇨🇼','costa de marfim':'🇨🇮','equador':'🇪🇨','paises baixos':'🇳🇱','japao':'🇯🇵',
 'suecia':'🇸🇪','tunisia':'🇹🇳','espanha':'🇪🇸','cabo verde':'🇨🇻','arabia saudita':'🇸🇦',
 'uruguai':'🇺🇾','belgica':'🇧🇪','egipto':'🇪🇬','irao':'🇮🇷','nova zelandia':'🇳🇿',
 'austria':'🇦🇹','jordania':'🇯🇴','franca':'🇫🇷','senegal':'🇸🇳','iraque':'🇮🇶','noruega':'🇳🇴',
 'argentina':'🇦🇷','argelia':'🇩🇿','portugal':'🇵🇹','congo':'🇨🇩','inglaterra':'🏴󠁧󠁢󠁥󠁮󠁧󠁿',
 'croacia':'🇭🇷','gana':'🇬🇭','panama':'🇵🇦','uzbequistao':'🇺🇿','colombia':'🇨🇴',
};
function flagPT(name){ return WCFLAGS[canon(name)] || '🏳️'; }
const WC_FIN  = new Set(['FT','AET','PEN']);
const WC_LIVE = new Set(['1H','2H','ET','BT','P','INT','LIVE']);
let wcSelDate = null;
function wcDateKey(g){
  const r = RES[String(g.game)] || {};
  if (r.kickoff) return new Date(r.kickoff).toLocaleDateString('en-CA',{timeZone:'Europe/Lisbon'});
  return g.date;
}
function wcDateLabel(key){
  const [y,m,d] = key.split('-').map(Number);
  return new Date(Date.UTC(y,m-1,d)).toLocaleDateString('pt-PT',{day:'2-digit',month:'short'});
}
function wcPick(d){ wcSelDate=d; renderWC(); }
function renderWC(){
  const gc = document.getElementById('wc-groups');
  if (gc){
    const order = [...new Set(GAMES.map(g=>g.group))].sort();
    let html = '<div class="groups-grid">';
    for (const grp of order){
      const tbl = {};
      const ensure = nm => { const k=canon(nm); if(!tbl[k]) tbl[k]={name:nm,P:0,GF:0,GA:0,pts:0}; return tbl[k]; };
      for (const g of GAMES.filter(x=>x.group===grp)){
        const A=ensure(g.home), B=ensure(g.away);
        const r=RES[String(g.game)];
        if (!r || r.hg==null || r.ag==null) continue;
        const h=+r.hg, a=+r.ag;
        A.P++;B.P++;A.GF+=h;A.GA+=a;B.GF+=a;B.GA+=h;
        if (h>a){A.pts+=3;} else if (h<a){B.pts+=3;} else {A.pts++;B.pts++;}
      }
      const teams = Object.values(tbl).sort((x,y)=> y.pts-x.pts || (y.GF-y.GA)-(x.GF-x.GA) || y.GF-x.GF || x.name.localeCompare(y.name));
      html += '<div class="group-card"><div class="group-title">Grupo '+grp+'</div>' +
        teams.map((t,i)=>`<div class="group-team ${i<2?'group-qual':''}"><div class="group-pos">${i+1}</div><div class="group-flag">${flagPT(t.name)}</div><div class="group-name">${t.name}</div><div class="group-pts">${t.pts}pts</div></div>`).join('') +
        '</div>';
    }
    gc.innerHTML = html + '</div>';
  }
  const nav = document.getElementById('wc-date-nav');
  if (!nav) return;
  const dates = [...new Set(GAMES.map(wcDateKey))].sort();
  if (!wcSelDate || !dates.includes(wcSelDate)){
    const today = new Date().toLocaleDateString('en-CA',{timeZone:'Europe/Lisbon'});
    wcSelDate = dates.includes(today) ? today : (dates.find(d=>d>=today) || dates[dates.length-1]);
  }
  nav.innerHTML = dates.map(d=>`<button class="wc-date-btn ${d===wcSelDate?'active':''}" onclick="wcPick('${d}')">${wcDateLabel(d)}</button>`).join('');
  wcRenderMatches();
}
function wcRenderMatches(){
  const box=document.getElementById('wc-matches'); if(!box) return;
  const list=GAMES.filter(g=>wcDateKey(g)===wcSelDate);
  if(!list.length){ box.innerHTML='<div class="empty">Sem jogos neste dia</div>'; return; }
  box.innerHTML=list.map(g=>{
    const r=RES[String(g.game)]||{};
    const live=WC_LIVE.has(r.status), fin=WC_FIN.has(r.status);
    let mid, badge;
    if (fin){ mid=`<div class="match-score-big">${r.hg}<br><span style="font-size:15px;color:var(--text3)">—</span><br>${r.ag}</div>`; badge='<span class="match-status-badge status-finished">FIM</span>'; }
    else if (live){ mid=`<div class="match-score-big">${r.hg}<br><span style="font-size:15px;color:var(--text3)">—</span><br>${r.ag}</div>`; badge=`<span class="match-status-badge status-live">🔴 ${r.min||'AO VIVO'}</span>`; }
    else { const t=r.kickoff?new Date(r.kickoff).toLocaleTimeString('pt-PT',{hour:'2-digit',minute:'2-digit',timeZone:'Europe/Lisbon'}):'—'; mid=`<div class="match-score-big" style="font-size:20px;color:var(--text2)">${t}<br><span style="font-size:10px">PT</span></div>`; badge='<span class="match-status-badge status-scheduled">Agendado</span>'; }
    return `<div class="match-card"><div class="match-header"><div class="match-group">Grupo ${g.group} · Jogo ${g.game}</div>${badge}</div><div class="match-teams-row"><div class="match-team"><div class="match-team-flag">${flagPT(g.home)}</div><div class="match-team-name">${g.home}</div></div>${mid}<div class="match-team away"><div class="match-team-flag">${flagPT(g.away)}</div><div class="match-team-name">${g.away}</div></div></div></div>`;
  }).join('');
}
'''
TITLE = '''<title>Bolsa de Apostas — Mundial 2026</title>'''
BTNF = '''  <button class="tab" onclick="goTab('f')">🏅 Fase Final</button>'''
BTNW = '''  <button class="tab" onclick="goTab('w')">🌍 Mundial</button>'''
NL = chr(10)
reps = [
  (TITLE, TITLE + NL + WC_FONTS),
  ('</style>', WC_CSS + '</style>'),
  (BTNF, BTNF + NL + BTNW),
  ('''  <div id="fp"></div>
</div>''', '''  <div id="fp"></div>
</div>''' + NL+NL + WC_PANEL),
  ('  const map={r:0,j:1,f:2};', '  const map={r:0,j:1,f:2,w:3};'),
  ("  if (id==='j') renderJ();"+NL+'}', "  if (id==='j') renderJ();"+NL+"  if (id==='w') renderWC();"+NL+'}'),
  ('    renderR(); renderJ();'+NL+'    scheduleRefresh();', '    renderR(); renderJ(); renderWC();'+NL+'    scheduleRefresh();'),
  ('// ── INIT', WC_JS + NL + '// ── INIT'),
  ('renderR(); renderJ();'+NL+'loadResults();', 'renderR(); renderJ();'+NL+'renderWC();'+NL+'loadResults();'),
]
for i,(old,new) in enumerate(reps,1):
    c=s.count(old)
    if c!=1:
        print('ERRO passo '+str(i)+': ancora '+str(c)+' vezes. Nada alterado.'); sys.exit(1)
    s=s.replace(old,new)
open(path,'w',encoding='utf-8').write(s)
print('OK - tab Mundial adicionada com sucesso.')
