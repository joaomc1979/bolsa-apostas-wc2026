import sys
path = 'index.html'
s = open(path, encoding='utf-8').read()
NL = chr(10)
WC_CHAN = '{"1":2,"3":2,"6":2,"9":2,"13":2,"18":2,"21":2,"26":2,"32":2,"35":2,"37":2,"41":2,"45":2,"51":2,"55":1,"61":1,"69":1}'
B1OLD = '''badge='<span class="match-status-badge status-scheduled">Agendado</span>'; }'''
B1NEW = B1OLD + NL + '''    const _c=WC_CHAN[String(g.game)]; const chHtml=_c?`<div class="match-chan">📺 Sinal aberto${_c===2?' · ▶️ YouTube':''}</div>`:'';'''
reps = [
  ('let wcSelDate = null;', 'let wcSelDate = null;' + NL + 'const WC_CHAN = ' + WC_CHAN + ';'),
  ('.group-qual{background:rgba(46,204,113,0.16);}', '.group-qual{background:rgba(46,204,113,0.16);}' + NL + '.match-chan{margin-top:8px;padding-top:8px;border-top:.5px solid var(--border);font-size:11px;color:#1D9E75;font-weight:600;}'),
  (B1OLD, B1NEW),
  ('<div class="match-team-name">${g.away}</div></div></div></div>', '<div class="match-team-name">${g.away}</div></div></div>${chHtml}</div>'),
]
for i,(old,new) in enumerate(reps,1):
    c=s.count(old)
    if c!=1:
        print('ERRO passo '+str(i)+': ancora '+str(c)+' vezes. Nada alterado.'); sys.exit(1)
    s=s.replace(old,new)
open(path,'w',encoding='utf-8').write(s)
print('OK - etiquetas de canal (jogos gratis) adicionadas.')
