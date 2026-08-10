# Pendências — Migração Day 1 → Day 2 → Day 3

**Projeto:** `databricks-lakebase-app-day-1`  
**Fork original:** `https://github.com/Roberton003/databricks-lakebase-app-day-1`  
**Day 2:** `https://github.com/EcZachly/databricks-lakebase-app-day-2`  
**Day 3:** `https://github.com/EcZachly/databricks-lakebase-app-day-3`  
**Data:** 2026-08-08  
**Status:** Day 3 planejado e arquivos criados

---

## Status da Execução

| Etapa | Status | Notas |
|-------|--------|-------|
| Day 1 → Day 2 (arquivos) | ✅ Concluída | 15 arquivos copiados/alterados |
| Day 2 → Day 3 (arquivos) | ✅ Concluída | `dashboard/` e `mcp_server/` criados |
| Validação sintaxe Python | ✅ PASS | `compileall -q` em todos os módulos |
| Validação YAML | ✅ PASS | PyYAML safe_load em todos os arquivos |
| SQLs gerados | ✅ Concluída | 01-04 (04 estava vazio, corrigido) |
| Setup secrets atualizado | ✅ Concluída | Agora inclui Alpaca credentials |
| Documentação | ✅ Concluída | README.md atualizado |

---

## Day 2 — O que falta executar (no workspace)

### P0 — Bloqueiam execução

- [ ] **Executar SQLs no Lakebase** (na ordem)
  - `sql/01_setup_news_table.sql` → `ticker_news_documents`
  - `sql/02_setup_embeddings_table.sql` → `ticker_news_embeddings` (ajustar `{{EMBEDDING_DIM}}` para 384)
  - `sql/03_setup_chunk_embeddings_table.sql` → `ticker_news_chunk_embeddings`
  - `sql/04_cast_arrays_to_vectors.sql` → após o notebook

- [ ] **Deploy e testar endpoints Day 2**
  - Subir `app.py` como Databricks App
  - Testar `/healthz`, `/watchlist`, `/news/sync`

- [ ] **Executar notebook manualmente**
  - `notebooks/ingest_ticker_news_embeddings.py`
  - Verificar 3 tabelas de saída

### P1 — Antes de ativar schedule

- [ ] Testar falhas parciais (URL inválida, paywall)
- [ ] Confirmar `max_concurrent_runs: 1` e notificações
- [ ] Manter `pause_status: PAUSED` até validar

### P2 — Melhorias pós-execução Day 2

- [ ] Testes automatizados para `get_news()`
- [ ] Testes para `/news/sync`
- [ ] Lockfile em `requirements.txt`
- [ ] Revisão de segurança (ACLs, XSS, nomes de tabela)

---

## Day 3 — O que falta executar (no workspace)

### P0 — Bloqueiam deploy Day 3

- [ ] **Criar Alpaca Markets paper-trading account**
  - Sign up em https://alpaca.markets
  - Criar **paper-trading** account (não real money)
  - Copiar API Key ID e Secret Key

- [ ] **Executar setup_secrets.py**
  ```bash
  python setup_secrets.py
  ```
  - Massive API key → `massive/api-key`
  - Lakebase URL → `database/lakebase-url`
  - Alpaca Key ID → `database/alpaca-key-id`
  - Alpaca Secret Key → `database/alpaca-secret-key`

- [ ] **Deploy MCP Server como Databricks App**
  - Nome: `alpaca-mcp-server`
  - Source: `mcp_server/app.yaml`
  - Porta: 8000

- [ ] **Deploy Dashboard como Databricks App**
  - Nome: `dashboard-watchlist`
  - Source: `dashboard/app.yaml`
  - Porta: 8001

- [ ] **Testar ambos os apps**
  - MCP Server: `GET /healthz` deve retornar `{"status": "ok"}`
  - Dashboard: `GET /healthz` deve retornar `{"status": "ok"}`

### P1 — Antes de usar Agent Bricks

- [ ] Configurar Agent Bricks (opcional)
  - Adicionar MCP Server URL como external tool
  - Testar com prompt: *"Check my watchlist and place a small order"*

### P2 — Melhorias pós-execução Day 3

- [ ] Testes para MCP tools
- [ ] Testes para dashboard endpoints
- [ ] Add `alpaca-py` aos requirements se for usar localmente

---

## Day 3 — Estrutura criada

```
databricks-lakebase-app-day-1/
├── mcp_server/
│   ├── __init__.py
│   ├── alpaca_mcp_server.py   # FastMCP server
│   ├── alpaca_broker.py       # Alpaca wrapper
│   ├── massive_broker.py      # Massive quotes wrapper
│   ├── lakebase.py
│   ├── app.yaml
│   └── requirements.txt       # fastmcp, requests
├── dashboard/
│   ├── __init__.py
│   ├── app.py                 # Read-only Flask app
│   ├── app.yaml
│   ├── requirements.txt       # flask, databricks-sdk
│   └── templates/index.html
├── setup_secrets.py           # Atualizado com Alpaca
├── README.md                  # Atualizado com Day 3
└── databricks.yml             # Atualizado
```

---

## Ordem de execução recomendada

**Fase 1 (hoje):**
1. Executar SQLs no Lakebase (Day 2)
2. Deploy app Day 2 e testar endpoints
3. Executar notebook manualmente
4. Criar Alpaca paper-trading account
5. Executar `setup_secrets.py`
6. Deploy MCP Server e Dashboard

**Fase 2 (após validação):**
7. Configurar Agent Bricks (opcional)
8. Implementar testes
9. Adicionar lockfile

---

## Fora do escopo

- Não reescrever arquitetura
- Não transformar em plataforma de produção
- Não implementar RAG (exigido apenas para Day 3)
- Não ativar schedule sem validação manual
- Não expor secrets no código ou Git

---

## Entendimento do escopo da entrega final

- [ ] Confirmar e documentar a proposta escolhida no capstone oficial da Databricks.
- [ ] Tratar os três dias de treinamento como conteúdo de apresentação, teoria e aplicação prática, não como a entrega final completa.
- [ ] Mapear cada requisito do capstone contra evidências no código, no workspace Databricks e na documentação.
- [ ] Completar e validar a aplicação final ponta a ponta: pipeline Spark, API externa, conteúdo não estruturado, embeddings/RAG, Databricks App com frontend e agente com leitura e escrita persistente no Lakebase.

**Interpretação registrada:** o projeto `databricks-ai-bootcamp-capstone` é a entrega final do bootcamp de IA/Data Engineering da Databricks; os materiais Day 1–Day 3 servem como base de aprendizagem e exemplos de implementação para cumprir os requisitos do capstone.

---

## Fora do escopo adicional

- Não adicionar funcionalidades fora dos requisitos do capstone sem necessidade demonstrada

---

## Day 1 Lakebase Homework — Feedback e Pendências

**Data do Feedback:** 2026-08-10  
**Nota Final:** 87/100  
**Instructor:** Databricks AI Bootcamp

### Rubric Breakdown

| Category | Score | Max | Feedback |
|----------|-------|-----|----------|
| Lakebase schema | 20 | 20 | Well-modeled schema with UUID PKs, foreign keys, ON DELETE CASCADE |
| Sample data | 10 | 10 | 3 tickets with different statuses, 2+ messages each |
| Reading from Lakebase | 20 | 20 | App queries Lakebase via psycopg2 |
| Creating data | 20 | 20 | Routes perform INSERTs with commits |
| Updating ticket status | 10 | 10 | Implemented with NOW() for updated_at |
| Deployment | 5 | 10 | No App URL or deployment screenshot |
| Submission and reflection | 2 | 10 | No App URL, repo URL, or screenshots |

### O Que Está Bom

- Schema relacional forte com UUIDs, foreign keys e indexes
- CRUD completo implementado contra Lakebase
- Secret handling seguro com Databricks Secrets
- Código limpo e bem estruturado

### O Que Precisa Melhorar

#### 1. Scripts de Sample Data Inconsistentes

**Problema:** `sample_data.sql` e scripts Python usam abordagens diferentes:

- `sample_data.sql`: Usa `gen_random_uuid()` para `ticket_id` nas mensagens — isso cria UUIDs aleatórios que **não referenciam** os tickets inseridos
- `setup_tickets.py` e `setup_tickets_databricks.py`: Usa IDs 1/2/3 para tickets — falha com UUIDs

**Solução:** Usar o padrão de `initialize_db.sql`:
```sql
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    ((SELECT ticket_id FROM tickets WHERE title = '...'), '...', '...');
```

Ou recuperar os UUIDs programaticamente antes de inserir mensagens.

#### 2. evidência de Deploy ausente

Falta:
- [ ] Databricks App URL
- [ ] Screenshot do app rodando
- [ ] Screenshot das tabelas no Lakebase com dados
- [ ] Repository URL (GitHub ou Workspace path)

#### 3. Submissão incompleta

Falta no documento de entrega:
- [ ] Fonte do código (link do repositório)

---

## Pendências do Day 1

- [ ] Corrigir scripts de sample data (usar SELECT subquery para ticket_id)
- [ ] Fazer deploy da aplicação no Databricks Apps
- [ ] Capturar screenshots (app rodando + tabelas Lakebase)
- [ ] Criar repository GitHub público
- [ ] Adicionar App URL e screenshots ao README.md
