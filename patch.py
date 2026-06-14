import sys
path = 'index.html'
s = open(path, encoding='utf-8').read()
old = '"name":"BODEGAO"'
new = '"name":"Daniel Sol"'
if s.count(old) != 1:
    print('ERRO: encontrado ' + str(s.count(old)) + ' vezes (esperava 1). Nada alterado.')
    sys.exit(1)
s = s.replace(old, new)
open(path, 'w', encoding='utf-8').write(s)
print('OK - nome alterado: BODEGAO -> Daniel Sol')
