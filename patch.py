import sys
path = 'index.html'
s = open(path, encoding='utf-8').read()
NL = chr(10)
OLD_CHAN = '''const WC_CHAN = {"1":2,"3":2,"6":2,"9":2,"13":2,"18":2,"21":2,"26":2,"32":2,"35":2,"37":2,"41":2,"45":2,"51":2,"55":1,"61":1,"69":1};'''
NEW_CHAN = '''const WC_CHAN = {"1":["TVI",1],"3":["SIC",1],"6":["",1],"9":["",1],"13":["",1],"18":["RTP",1],"21":["SIC",1],"26":["RTP",1],"32":["",1],"35":["TVI",1],"37":["",1],"41":["",1],"45":["TVI",1],"51":["",1],"55":["SIC",0],"61":["TVI",0],"69":["RTP",0]};'''
OLD_CH = '''    const _c=WC_CHAN[String(g.game)]; const chHtml=_c?`<div class="match-chan">📺 Sinal aberto${_c===2?' · ▶️ YouTube':''}</div>`:'';'''
NEW_CH = '    const _c=WC_CHAN[String(g.game)];' + NL + "    let chHtml='';" + NL + '''    if(_c){ const p=[]; if(_c[0])p.push('📺 '+_c[0]+' (previsto)'); if(_c[1])p.push('▶️ YouTube'); if(!p.length)p.push('📺 Sinal aberto'); chHtml=`<div class="match-chan">${p.join(' · ')}</div>`; }'''
reps = [(OLD_CHAN, NEW_CHAN), (OLD_CH, NEW_CH)]
for i,(old,new) in enumerate(reps,1):
    c=s.count(old)
    if c!=1:
        print('ERRO passo '+str(i)+': ancora '+str(c)+' vezes. Nada alterado.'); sys.exit(1)
    s=s.replace(old,new)
open(path,'w',encoding='utf-8').write(s)
print('OK - canais previstos por jogo adicionados.')
