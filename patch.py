import sys
path = 'index.html'
s = open(path, encoding='utf-8').read()

old1 = '''  let rows = played.map(g => {
    const r=RES[String(g.game)]; const pred=p.games[String(g.game)];
    const pts=scoreG(p,g.game);
    const cls=pts>0?'gp':pts<0?'gn':'gz';
    const fsMatch = r&&r.fs&&pred&&pred.fs&&eq(pred.fs,r.fs) ? '⚽' : '';
    return `<tr>
      <td style="color:var(--text3);font-size:11px">${g.game}</td>
      <td style="font-size:12px">${g.home} vs ${g.away}</td>
      <td>${r?r.hg+'-'+r.ag:'?'}</td>
      <td style="color:var(--text2)">${pred?pred.hg+'-'+pred.ag:'?'}</td>
      <td style="color:var(--text3);font-size:11px">${r&&r.fs&&r.fs!=='NO GOALS'?r.fs:'—'} ${fsMatch}</td>
      <td class="${cls}">${pts>=0?'+':''}${pts}</td>
    </tr>`;
  }).join('');'''

new1 = '''  let rows = GAMES.map(g => {
    const r=RES[String(g.game)]; const pred=p.games[String(g.game)];
    const isPlayed = r && r.hg!=null && r.ag!=null;
    if (isPlayed) {
      const pts=scoreG(p,g.game);
      const cls=pts>0?'gp':pts<0?'gn':'gz';
      const fsMatch = r&&r.fs&&pred&&pred.fs&&eq(pred.fs,r.fs) ? '⚽' : '';
      return `<tr>
        <td style="color:var(--text3);font-size:11px">${g.game}</td>
        <td style="font-size:12px">${g.home} vs ${g.away}</td>
        <td>${r.hg+'-'+r.ag}</td>
        <td style="color:var(--text2)">${pred?pred.hg+'-'+pred.ag:'?'}</td>
        <td style="color:var(--text3);font-size:11px">${r.fs&&r.fs!=='NO GOALS'?r.fs:'—'} ${fsMatch}</td>
        <td class="${cls}">${pts>=0?'+':''}${pts}</td>
      </tr>`;
    }
    // Jogo ainda por jogar — mostra a aposta do jogador
    const predScore = pred && pred.hg!=null ? pred.hg+'-'+pred.ag : '—';
    const predFs = pred && pred.fs && pred.fs!=='NO GOALS' ? pred.fs
                 : (pred && pred.fs==='NO GOALS' ? 'Sem golos' : '—');
    return `<tr style="opacity:.5">
      <td style="color:var(--text3);font-size:11px">${g.game}</td>
      <td style="font-size:12px">${g.home} vs ${g.away}</td>
      <td style="color:var(--text3)">—</td>
      <td style="color:var(--text2)">${predScore}</td>
      <td style="color:var(--text3);font-size:11px">${predFs}</td>
      <td style="color:var(--text3)">—</td>
    </tr>`;
  }).join('');'''

old2 = '''    ${played.length
      ? `<table style="width:100%;font-size:12px"><thead><tr><th>#</th><th>Jogo</th><th>Resultado</th><th>Prev.</th><th>1.º golo</th><th>Pts</th></tr></thead><tbody>${rows}</tbody></table>`
      : '<div class="empty">Sem resultados ainda</div>'}'''

new2 = '''    <table style="width:100%;font-size:12px"><thead><tr><th>#</th><th>Jogo</th><th>Resultado</th><th>Aposta</th><th>1.º golo</th><th>Pts</th></tr></thead><tbody>${rows}</tbody></table>'''

for tag, old in [('bloco 1', old1), ('bloco 2', old2)]:
    if s.count(old) != 1:
        print('ERRO: ' + tag + ' encontrado ' + str(s.count(old)) + ' vezes. Nada alterado.')
        sys.exit(1)

s = s.replace(old1, new1).replace(old2, new2)
open(path, 'w', encoding='utf-8').write(s)
print('OK - alteracao aplicada com sucesso.')
