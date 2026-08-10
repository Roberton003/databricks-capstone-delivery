# Relatório de Status e Pendências

**Projeto:** `databricks-lakebase-app-day-1`  
**Base:** fork de `Roberton003/databricks-lakebase-app-day-1`  
**Treinamento:** Databricks Lakebase Day 1 → Day 2 → Day 3  
**Data do relatório:** 2026-08-08  
**Estado:** migração de arquivos realizada; validação no workspace Databricks ainda não executada

---

## 1. Onde estamos

O fork local foi clonado e atualizado incrementalmente com os arquivos dos treinamentos:

- Day 1: fork original;
- Day 2: notícias, embeddings, notebook Spark, SQL e Workflow;
- Day 3: estrutura inicial para MCP Server, Alpaca paper-trading e Dashboard.

O trabalho foi realizado localmente, sem commit e sem push.

### Estado do Git

A branch local é `main`, baseada em `origin/main`.

Existem alterações locais não commitadas:

- modificados: `README.md`, `app.py`, `massive_client.py`, `setup_secrets.py`, `templates/index.html`;
- novos: `PENDENCIAS.md`, `STATUS_E_PENDENCIAS.md`, `dashboard/`, `mcp_server/`, `databricks.yml`, `docs/`, `notebooks/`, `resources/`, `sql/`.

O `git diff --check` não apontou erros de whitespace.

> Não fazer commit ou push automaticamente antes de revisar o diff completo.

---

## 2. O que foi concluído

### 2.1 Day 1 → Day 2

Arquivos do Day 2 foram incorporados:

- `app.py` com operações de watchlist e sincronização de notícias;
- `massive_client.py` com `get_news()`;
- notebook `notebooks/ingest_ticker_news_embeddings.py`;
- SQLs em `sql/`;
- Asset Bundle e Workflow em `databricks.yml` e `resources/`;
- documentação atualizada.

### 2.2 Correção encontrada durante a validação

O arquivo abaixo estava vazio e foi preenchido:

```text
sql/04_cast_arrays_to_vectors.sql
```

Ele contém os `UPDATE`s para converter os arrays de embeddings para `VECTOR` após a execução do notebook.

### 2.3 Day 2 → Day 3

Foi criada a estrutura inicial:

```text
mcp_server/
├── __init__.py
├── alpaca_broker.py
├── alpaca_mcp_server.py
├── app.yaml
├── lakebase.py
├── massive_broker.py
└── requirements.txt

dashboard/
├── __init__.py
├── app.py
├── app.yaml
├── requirements.txt
└── templates/index.html
```

Também foram atualizados:

- `setup_secrets.py` para incluir credenciais Alpaca;
- `README.md` com a arquitetura Day 3;
- `databricks.yml`;
- `resources/` com arquivos iniciais para MCP Server e Dashboard.

### 2.4 Checks locais aprovados

- `python3 -m compileall -q`: PASS;
- YAML validado com PyYAML: PASS;
- `git diff --check`: PASS;
- estrutura comparada com os repositórios públicos de referência: realizada.

---

## 3. Pendências bloqueadoras

### P0 — Corrigir antes de executar o Day 3

#### P0.1 — Implementar o FastMCP real

`mcp_server/alpaca_mcp_server.py` atualmente contém funções Python e um `run_mcp_server()` de placeholder, mas não registra as funções com `FastMCP` nem inicia transporte HTTP MCP.

Falta:

- importar e instanciar `FastMCP`;
- registrar as ferramentas com `@mcp.tool`;
- expor as ferramentas esperadas pelo Agent Bricks;
- iniciar o servidor com transporte HTTP/streamable HTTP;
- validar o endpoint MCP com um cliente compatível.

Sem isso, o app não é um MCP Server funcional.

#### P0.2 — Tornar o Dashboard executável como app independente

`dashboard/app.py` usa imports relativos:

```python
from . import lakebase
from . import massive_client
```

Mas o `dashboard/` não contém `lakebase.py` nem `massive_client.py`, e o `app.yaml` executa `python app.py`. Nesse modo, os imports relativos podem falhar.

Falta decidir e implementar uma opção consistente:

- copiar os módulos necessários para `dashboard/` e usar imports diretos; ou
- transformar o dashboard em pacote executado com `python -m`; ou
- criar uma camada compartilhada com layout compatível com Databricks Apps.

A opção mais simples para o treinamento é copiar/adaptar os módulos necessários dentro de `dashboard/`.

#### P0.3 — Corrigir o modelo de deploy

Os arquivos `resources/mcp_server.yml` e `resources/dashboard.yml` estão modelados como Jobs com `spark_python_task`, mas Databricks Apps são normalmente implantados por seus próprios `app.yaml`.

Antes do deploy, revisar se esses recursos devem existir. Não usar Jobs para simular o processo de execução dos Apps sem confirmar a necessidade no workspace.

#### P0.4 — Corrigir dependências do notebook

O notebook Day 2 usa imports como:

- `sentence_transformers`;
- `trafilatura`;
- `pandas`;
- `psycopg2`.

Essas dependências não estão todas declaradas no `requirements.txt` principal do App. O notebook deve usar o ambiente do cluster ou declarar suas bibliotecas no Job/cluster.

Falta confirmar no workspace quais bibliotecas já estão disponíveis e declarar as ausentes no local correto.

---

## 4. Pendências do Day 2 no Databricks

Estas não foram executadas porque exigem workspace, rede e credenciais reais:

- [ ] executar `sql/01_setup_news_table.sql`;
- [ ] substituir `{{EMBEDDING_DIM}}` por `384` nos SQLs 02 e 03;
- [ ] executar `sql/02_setup_embeddings_table.sql`;
- [ ] executar `sql/03_setup_chunk_embeddings_table.sql`;
- [ ] executar o notebook manualmente com uma watchlist pequena;
- [ ] executar `sql/04_cast_arrays_to_vectors.sql` após o notebook;
- [ ] validar `pgvector`, dimensões e índices HNSW;
- [ ] fazer deploy do app Day 2;
- [ ] testar `/healthz`, `/watchlist` e `/news/sync`;
- [ ] testar o limite de requisições da API Massive;
- [ ] validar o Asset Bundle com `databricks bundle validate -t dev`;
- [ ] executar o Workflow manualmente;
- [ ] manter o schedule pausado até a execução manual passar.

O Databricks CLI não estava instalado no ambiente local durante a validação anterior.

---

## 5. Pendências do Day 3 no Databricks

- [ ] criar uma conta Alpaca de **paper-trading**;
- [ ] criar/obter Alpaca API Key ID;
- [ ] criar/obter Alpaca Secret Key;
- [ ] armazenar os secrets:
  - `database/alpaca-key-id`;
  - `database/alpaca-secret-key`;
- [ ] revisar ACLs dos Secret Scopes;
- [ ] corrigir e validar o MCP Server real;
- [ ] corrigir e validar o Dashboard independente;
- [ ] criar o App do MCP Server;
- [ ] criar o App do Dashboard;
- [ ] testar health checks;
- [ ] testar leitura de conta, posições e ordens;
- [ ] testar quote;
- [ ] testar `place_order` somente na conta paper;
- [ ] configurar Agent Bricks como etapa opcional;
- [ ] conectar o Agent Bricks ao endpoint MCP;
- [ ] testar primeiro com operações de leitura;
- [ ] só depois testar uma ordem pequena de paper-trading.

---

## 6. Riscos conhecidos

### Segurança

- `setup_secrets.py` concede leitura ao principal amplo `users`; restringir em ambiente real;
- operações de trade não devem aceitar credenciais live;
- `X-Forwarded-Email` só deve ser confiado atrás do proxy Databricks;
- nomes de tabelas interpolados em SQL precisam ser restritos/validados;
- não registrar API keys, secrets ou URLs completas com senha nos logs;
- revisar uso de `innerHTML` no frontend antes de exposição externa.

### Arquitetura

- O Day 3 não é apenas uma extensão do Flask Day 2: são dois Apps independentes;
- `account_id` é aceito pelas funções Alpaca, mas a API key seleciona efetivamente uma única conta;
- o MCP Server pode executar ordens reais no ambiente paper, portanto `place_trade` exige validação explícita;
- duplicação de módulos entre Apps é aceitável para acompanhar o treinamento, mas deve ser documentada.

### Operação

- não ativar schedule antes de execução manual;
- `max_concurrent_runs: 1` deve ser mantido para o Workflow;
- registrar custo, tempo, número de artigos e número de chunks antes de dimensionar cluster;
- dependências com apenas versões mínimas ainda não estão lockadas.

---

## 7. Próxima sequência recomendada

### Etapa A — corrigir localmente antes do Databricks

1. Implementar FastMCP real em `mcp_server/alpaca_mcp_server.py`.
2. Corrigir imports e módulos independentes do Dashboard.
3. Remover ou revisar os recursos de Job que não correspondem ao deploy de Apps.
4. Adicionar testes unitários sem chamadas externas.
5. Rodar `compileall`, YAML validation e testes.

### Etapa B — validar Day 2 no workspace

1. Executar SQLs.
2. Executar notebook com um ticker.
3. Converter arrays para vectors.
4. Testar endpoints.
5. Validar Workflow manualmente.

### Etapa C — validar Day 3 no workspace

1. Configurar Alpaca paper-trading.
2. Configurar secrets.
3. Deploy MCP Server.
4. Deploy Dashboard.
5. Validar ferramentas de leitura.
6. Testar paper order pequena.
7. Configurar Agent Bricks opcionalmente.

---

## 8. Arquivos principais para retomada

- `PENDENCIAS.md` — checklist operacional;
- `STATUS_E_PENDENCIAS.md` — este relatório;
- `README.md` — documentação geral;
- `mcp_server/alpaca_mcp_server.py` — próximo ponto de correção prioritário;
- `dashboard/app.py` — próximo ponto de correção prioritário;
- `mcp_server/app.yaml` — configuração do App MCP;
- `dashboard/app.yaml` — configuração do App Dashboard;
- `sql/` — setup do Lakebase/pgvector;
- `notebooks/ingest_ticker_news_embeddings.py` — pipeline Day 2.

---

## Critério para retomar

A próxima sessão deve começar pela correção local dos itens **P0.1**, **P0.2** e **P0.3**, antes de qualquer deploy ou configuração do Agent Bricks.
