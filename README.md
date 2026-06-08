# Bolsa de Apostas — Mundial 2026

Ranking automático para o campeonato de apostas do Mundial 2026.

## Estrutura

```
.github/workflows/fetch-results.yml   ← GitHub Actions cron (30 min)
scripts/fetch_results.py              ← Script que chama a API-Football
data/results.json                     ← Resultados (actualizado automaticamente)
index.html                            ← Site público (lê o JSON acima)
```

## Setup (5 minutos)

### 1. Criar repositório no GitHub
Cria um repositório público (ex: `bolsa-apostas-wc2026`) e faz push de todos estes ficheiros.

### 2. Obter API key gratuita
Registo em https://dashboard.api-football.com/register (sem cartão de crédito).  
Plano gratuito: 100 requests/dia — o script usa ~48/dia (1 a cada 30 min).

### 3. Adicionar a API key como Secret no GitHub
No teu repositório: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `API_FOOTBALL_KEY`
- Value: a tua chave da API-Football

### 4. Activar GitHub Pages
**Settings → Pages → Source: Deploy from a branch → Branch: main → / (root)**

O site fica disponível em `https://TEUUSERNAME.github.io/NOMEREPO/`

### 5. Activar o GitHub Actions
O workflow corre automaticamente a partir do momento em que está no repo.  
Para forçar uma execução imediata: **Actions → Fetch WC2026 Results → Run workflow**.

## Como funciona

- O GitHub Actions corre de 30 em 30 minutos e chama a API-Football
- Busca todos os jogos do Mundial (`/fixtures?league=1&season=2026`)
- Para jogos terminados sem marcador, faz uma segunda chamada batch com os IDs
- Guarda o resultado em `data/results.json` e faz commit automático
- O `index.html` lê esse JSON e calcula o ranking no browser dos utilizadores
- Os teus amigos não precisam de API key — só abrem o link

## Gestão manual

Se precisar de corrigir um resultado: edita directamente o `data/results.json`  
e adiciona `"manual_overrides": {"NUM_JOGO": true}` para o script não sobrescrever.

## Consumo de requests API-Football (estimativa)

| Situação | Calls por execução | Calls/dia |
|---|---|---|
| Sem jogos | 1 | 48 |
| Com jogos terminados (scorer) | 1 + 1 batch | ~48–96 |

Dentro do limite gratuito de 100/dia durante quase todo o torneio.  
Nos dias com muitos jogos (ex: últimos dias da fase de grupos) pode aproximar-se do limite.
