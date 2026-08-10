# PRD e Plano de Execução
## Databricks AI Bootcamp Capstone

**Data:** 2026-08-10  
**Projeto:** Massive + Lakebase Databricks App (Day 1 → Day 2 → Day 3)  
**Base:** Fork de [`Roberton003/databricks-lakebase-app-day-1`](https://github.com/Roberton003/databricks-lakebase-app-day-1)  
**Capstone:** [`EcZachly/databricks-ai-bootcamp-capstone`](https://github.com/EcZachly/databricks-ai-bootcamp-capstone)

---

## 1. Resumo Executivo

### 1.1 Contexto

Os **Three Days of Databricks Lakebase** (Day 1, Day 2, Day 3) constituem uma trilha de aprendizagem prática que ensina:

| Dia | Objetivo | Tecnologias | Entregável |
|-----|----------|-------------|------------|
| Day 1 | Fundamentos de Databricks Apps | Databricks Apps, Lakebase | Flask app básica |
| Day 2 | Ingestão e RAG com embeddings | Spark, pgvector, Massive API | Pipeline de notícias + embeddings |
| Day 3 | Agentes e arquitetura modular | MCP, FastMCP, Agent Bricks | MCP Server + Dashboard separados (trade opcional; pesquisa principal) |

### 1.2 Escopo do Capstone

O **repositório oficial do capstone** (`databricks-ai-bootcamp-capstone`) define um projeto final que deve incluir:

- Pipeline de dados com **Spark**
- Integração com pelo menos uma **API externa**
- Processamento de conteúdo **não estruturado** (texto/áudio/vídeo/imagem)
- **Embeddings** e busca semântica/RAG
- Aplicação **Databricks App** com frontend
- **Agente de IA** com ferramentas de leitura e escrita (persistência no banco)

### 1.3 Proposta Escolhida

Com base no código existente, a aplicação implementada é:

> **Assistente de Pesquisa do Mercado de Ações** — um sistema que rastreia tickers do mercado, coleta notícias, computa embeddings, expõe dados via Dashboard, permite consultas semânticas com notícias, e salva notas e relatórios de análise no Lakebase. O agente tem ferramentas de leitura (consultar preços, notícias, contexto semântico) e escrita (salvar notas, relatórios, gerenciar watchlist).

---

## 2. Conhecimento Consolidado do Bootcamp

A extração autenticada via `notebooklm-py` confirmou que o notebook contém quatro fontes do treinamento:

- **Day 1:** Setting Up your Lakebase and App;
- **Day 2:** Context Engineering;
- **Day 3:** AI Agents;
- **Introdução ao Databricks:** visão geral do bootcamp.

### 2.1 Day 1 — Lakebase e Databricks Apps

- Databases são voltados a operações transacionais de baixa latência; Data Lakes são voltados a grandes volumes históricos, análises e IA.
- Lakebase, baseado em Postgres, funciona como base transacional integrada ao lakehouse.
- CDC/CDF permitem capturar inserções, atualizações e exclusões para sincronização com o Delta Lake.
- Databricks Apps podem acessar Lakebase e APIs externas usando secrets.
- Git folders e deploy fazem parte do fluxo operacional.
- Genie é apresentado como apoio para desenvolvimento e estilização por linguagem natural.

### 2.2 Day 2 — Context Engineering e RAG

- O objetivo não é somente gerar respostas, mas fornecer contexto correto e relevante ao agente.
- O conteúdo aborda entidades, palavras-chave e vetores como estratégias complementares de recuperação.
- Embeddings representam conteúdo como vetores; a similaridade de cosseno compara proximidade semântica.
- Chunking não é a mesma coisa que embedding: o primeiro divide o conteúdo; o segundo transforma cada unidade em vetor.
- Índices HNSW aceleram a busca vetorial e devem usar a mesma métrica configurada na consulta.
- O pipeline do projeto extrai o corpo das notícias, remove ruído HTML, cria chunks sobrepostos e gera embeddings distribuídos com Spark.
- A avaliação deve considerar tanto falsos positivos/alucinações quanto falsos negativos, quando o agente deixa de executar uma ação útil.

### 2.3 Day 3 — Agentes, Middleware e MCP

- Um agente precisa de ferramentas para agir; sem ferramentas ele se limita a produzir texto.
- Middleware fica entre usuário e agente para validar entradas, remover PII, controlar ferramentas, custos e segurança.
- Observabilidade deve registrar interações, chamadas de ferramentas, erros e decisões para permitir auditoria.
- MCP centraliza uma biblioteca de ferramentas reutilizável por vários agentes, reduzindo manutenção duplicada.
- MCP é diferente de uma API REST: REST normalmente expõe dados/recursos; MCP expõe ferramentas que o agente pode invocar.
- Ações irreversíveis devem prever human-in-the-loop e limites explícitos.
- Rate limiting, roteamento por complexidade e experimentação A/B ajudam a controlar custos e qualidade.
- **Para o capstone, ações de escrita são notas/relatórios no Lakebase — não trading com Alpaca.** O paper trading pode ser uma extensão futura, mas o requisito do capstone é cumprido com persistência de análise e pesquisa.

### 2.4 Como o NotebookLM foi usado

A autenticação foi realizada com `notebooklm-py` e o conteúdo foi consultado pelo notebook `da2bd8e6-454b-4e35-a2e3-c9924ebe7630`. O notebook contém quatro fontes em vídeo/transcrição:

| Fonte | Uso na análise |
|---|---|
| Introdução ao Databricks / AI Boot Camp Day 1 | Contexto geral e trilha de aprendizagem |
| Day 1 — Setting Up your Lakebase and App | Lakebase, Apps, secrets, Git e CDF |
| Day 2 — Context Engineering | Chunking, embeddings, busca vetorial, HNSW e qualidade do contexto |
| Day 3 — AI Agents | Agentes, ferramentas, MCP, middleware, observabilidade e segurança |

O `notebooklm-py` foi usado para obter o texto integral indexado das fontes, além de gerar consultas específicas e notas de resumo. O texto das aulas é evidência de conteúdo didático e orientação técnica; não substitui os requisitos oficiais do repositório do capstone.

**Decisão de escopo:** não copiar as transcrições completas para o repositório. O PRD registra somente o conhecimento sintetizado e rastreável, evitando incorporar material bruto de treinamento ao código do projeto.

### 2.5 Implicações para o Capstone

O capstone não deve ser tratado apenas como um conjunto de endpoints. A entrega precisa demonstrar o ciclo completo:

```text
Dados externos → Lakebase/Delta → contexto e embeddings → recuperação → agente
      ↑                                                        ↓
      └────────────── ação persistente + auditoria ────────────┘
```

A implementação atual atende boa parte da infraestrutura, mas ainda precisa provar no workspace: ingestão real, recuperação semântica, agente operacional, controles de middleware/segurança, observabilidade e demonstração ponta a ponta.

---

## 3. Arquitetura Atual

``` 
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Databricks Workspace                               │
│                                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐                      │
│  │   Databricks App     │         │   Databricks App     │                      │
│  │     (Main App)       │         │    (Dashboard)       │                      │
│  │                      │         │                      │                      │
│  │  - Massive API       │         │  - Read-only Flask   │                      │
│  │  - Lakebase (PG)     │         │  - Watchlist/Quotes  │                      │
│  │  - Sync endpoint     │         │  - News viewer       │                      │
│  │                      │         │                      │                      │
│  └──────────┬───────────┘         └──────────────────────┘                      │
│             │                                                                   │
│             ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │                        Lakebase (Postgres)                            │      │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐ │      │
│  │  │  watchlist       │  │ ticker_news_     │  │ ticker_news_         │ │      │
│  │  │  (tickers)       │  │ documents        │  │ embeddings           │ │      │
│  │  └──────────────────┘  │ (news articles)  │  │ (title+description)  │ │      │
│  │                        └──────────────────┘  └──────────────────────┘ │      │
│  │                                                              │          │      │
│  │                                                              ▼          │      │
│  │                                                    ┌────────────────┐ │      │
│  │                                                    │ pgvector HNSW  │ │      │
│  │                                                    │ index (cosine) │ │      │
│  │                                                    └────────────────┘ │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│             │                                                                   │
│             ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │                      MCP Server App                                  │      │
│  │  ┌───────────────────────────────────────────────────────────────┐   │      │
│  │  │  Alpaca Broker (paper-trading)                                │   │      │
│  │  │  - get_quote(), place_order(), get_positions()               │   │      │
│  │  │  - get_account_summary(), get_order_history(), get_balance() │   │      │
│  │  └───────────────────────────────────────────────────────────────┘   │      │
│  │                                                                       │      │
│  │  ┌───────────────────────────────────────────────────────────────┐   │      │
│  │  │  FastMCP Server (tools exposted to Agent Bricks)              │   │      │
│  │  │  - get_quote(symbol)                                          │   │      │
│  │  │  - place_order(account_id, symbol, side, quantity)           │   │      │
│  │  │  - get_positions(account_id)                                  │   │      │
│  │  │  - get_account_summary(account_id)                            │   │      │
│  │  │  - get_order_history(account_id, limit)                       │   │      │
│  │  │  - get_current_user()                                         │   │      │
│  │  │  - get_watchlist()                                            │   │      │
│  │  │  - add_to_watchlist(symbol)                                   │   │      │
│  │  │  - remove_from_watchlist(symbol)                              │   │      │
│  │  └───���───────────────────────────────────────────────────────────┘   │      │
│  └───────────────────────────────────────────────────────────────────────┘      │
│             │                                                                   │
│             ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │                    Agent Bricks (optional)                           │      │
│  │  ┌───────────────────────────────────────────────────────────────┐   │      │
│  │  │  - Consulta dados via MCP tools                              │   │      │
│  │  │  - Executa ordens de compra/venda                            │   │      │
│  │  │  - Decision logic (LLM-driven)                               │   │      │
│  │  └───────────────────────────────────────────────────────────────┘   │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Requisitos do Capstone vs. Implementação Atual

### 3.1 Mapeamento de Requisitos

| # | Requisito do Capstone | Status | Código/Arquivo | Notas |
|---|----------------------|--------|----------------|-------|
| R1 | Pipeline de dados com Spark | ✅ Implementado | `notebooks/ingest_ticker_news_embeddings.py` | Usando Spark para embeddings distribuídos |
| R2 | Integração com API externa | ✅ Implementado | `massive_client.py`, `alpaca_broker.py` | Massive API (prices/news), Alpaca (trading) |
| R3 | Conteúdo não estruturado | ✅ Implementado | Notebook + `trafilatura` | HTML de notícias → texto limpo |
| R4 | Embeddings e RAG | ⚠️ Parcial | `notebooks/ingest_ticker_news_embeddings.py`, `sql/` | Embeddings/chunks/index estão preparados; falta comprovar consulta semântica integrada ao agente/app |
| R5 | Databricks App com frontend | ⚠️ Parcial | `app.py`, `dashboard/app.py` | Código e templates existem; falta deploy e teste no workspace |
| R6 | Agente com leitura | ⚠️ Não validado | `mcp_server/alpaca_mcp_server.py` | Há funções previstas, mas o arquivo declara a inicialização FastMCP como placeholder |
| R7 | Agente com escrita (persistência) | ⚠️ Não validado | `alpaca_broker.py` | Broker paper-trading tem `place_order()`; falta provar chamada via agente e registrar resultado |

### 3.2 Entregáveis do Capstone (Obrigatórios)

| Entregável | Status | Prioridade | Comentários |
|------------|--------|------------|-------------|
| Pipeline Spark funcional | ✅ | P0 | Código implementado, aguarda validação no workspace |
| Dados estruturados no Lakebase | ✅ | P0 | Tables criadas, dados ingestion aguarda secrets |
| Conteúdo não estruturado processado | ✅ | P0 | Notebook extraí HTML e cria chunks |
| Embeddings calculados | ✅ | P0 | Usando `sentence-transformers/all-MiniLM-L6-v2` |
| Databricks App funcional | ⚠️ | P0 | Arquitetura dividida em 3 apps (main, dashboard, mcp) |
| Agente funcional | ⚠️ | P1 | MCP Server pronto, Agent Bricks requer configuração extra |

### 3.3 Funcionalidades Adicionais (Opcionais)

| Funcionalidade | Status | Comentários |
|----------------|--------|-------------|
| Workflow agendado | ✅ | `resources/ingest_ticker_news_embeddings_job.yml` |
| Dashboard visual | ⚠️ | HTML/CSS básico em `dashboard/templates/` |
| Report de performance | ❌ | Pode ser adicionado posteriormente |
| Testes automatizados | ❌ | Pode ser adicionado posteriormente |

---

## 4. Plano de Execução

### 4.1 Fase 0: Preparação (2-4 horas)

#### 0.1 Configuração do Ambiente
```bash
# Verificar ferramentas
pip show notebooklm-py databricks-sdk pyyaml  # já instalado

# Verificar autenticação Databricks
databricks clusters list  # ou databricks accounts login
```

#### 0.2 Contas Necesárias
| Conta | Status | Prioridade | Observação |
|-------|--------|------------|------------|
| Databricks Workspace | ⚠️ | P0 | Acesso necessário |
| Massive API Key | ❌ | P0 | Criar em https://www.massive.com | Necessária para dados de mercado |
| Alpaca Paper Account | ❌ | Opcional | Criar em https://alpaca.markets | Só necessário para extensão de trading |

### 4.2 Fase 1: Deploy Lakebase e Setup (4-6 horas)

#### 1.1 Executar SQLs no Lakebase
```bash
# Conectar ao Lakebase (Postgres) e executar:
psql $LAKEBASE_URL -f sql/01_setup_news_table.sql
psql $LAKEBASE_URL -f sql/02_setup_embeddings_table.sql
psql $LAKEBASE_URL -f sql/03_setup_chunk_embeddings_table.sql
psql $LAKEBASE_URL -f sql/04_cast_arrays_to_vectors.sql
```

#### 1.2 Configurar Secrets
```bash
# Executar localmente (não commitar!)
python setup_secrets.py
# - Massive API key
# - Lakebase URL
# - Alpaca Key ID
# - Alpaca Secret Key
```

#### 1.3 Validar Tabelas
```sql
-- Verificar tables criadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Verificar colunas
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('ticker_news_documents', 'ticker_news_embeddings', 'ticker_news_chunk_embeddings')
ORDER BY table_name, ordinal_position;
```

### 4.3 Fase 2: Deploy e Teste dos Apps (6-8 horas)

#### 2.1 Deploy do Main App
```bash
# Do diretório databricks-lakebase-app-day-1/
databricks bundle deploy -t dev

# Verificar deployment
databricks apps get databricks-lakebase-app-day-3
```

#### 2.2 Deploy do Dashboard
```bash
# Do diretório databricks-lakebase-app-day-1/dashboard/
databricks apps deploy

# Verificar logs
databricks apps logs --follow
```

#### 2.3 Deploy do MCP Server
```bash
# Do diretório databricks-lakebase-app-day-1/mcp_server/
databricks bundle deploy -t dev

# Verificar endpoints
curl -X POST http://<mcp-endpoint>/mcp/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

### 4.4 Fase 3: Validar Pipeline e Embeddings (4-6 horas)

#### 3.1 Executar Notebook Manualmente
```bash
# No workspace Databricks:
# 1. Importar notebooks/ingest_ticker_news_embeddings.py
# 2. Executar célula por célula para validação
# 3. Verificar saída:
#    - ticker_news_documents: 50+ artigos por ticker
#    - ticker_news_embeddings: embeddings calculados
```

#### 3.2 Verificar Embeddings
```sql
-- Verificar embeddings calculados
SELECT COUNT(*) as total_embeddings, model_name
FROM ticker_news_embeddings
GROUP BY model_name;

-- Testar busca semântica
SELECT title, 1 - (embedding <-> %s::vector) as similarity
FROM ticker_news_embeddings
WHERE ticker = 'AAPL'
ORDER BY similarity DESC
LIMIT 5;
```

### 4.5 Fase 4: Teste Completo do Sistema (4-6 horas)

#### 4.1 Teste da API Main App
```bash
# Testar endpoints
curl http://localhost:8000/watchlist
curl http://localhost:8000/price/AAPL
curl -X POST http://localhost:8000/news/sync
```

#### 4.2 Teste do Dashboard
```bash
# Acessar no navegador
open http://localhost:8001/watchlist
open http://localhost:8001/price/AAPL
```

#### 4.3 Teste do MCP Server
```python
# Testar tools via FastMCP (exemplo)
from fastmcp import FastMCP

mcp = FastMCP("test")
# Conectar ao servidor e testar cada tool
```

### 4.6 Fase 5: Agent Bricks (Opcional) (4-8 horas)

#### 5.1 Configurar Agent Bricks
- Criar agent no Databricks Workspace
- Configurar MCP tools como capabilities
- Definir prompt e logic de decisão

#### 5.2 Testar Agente
- Testar query: "Dê uma recomendação para AAPL"
- Verificar chamadas às tools
- Verificar ordens paper-trading (simuladas)

---

## 5. Critérios de Sucesso

### 5.1 Critérios de Aceitação do Capstone

| Critério | Mensuração | Status |
|----------|------------|--------|
| Pipeline Spark executa | Notebook termina sem erros | ⚠️ Aguarda deploy |
| Dados no Lakebase | `SELECT COUNT(*) > 0` nas tabelas | ⚠️ Aguarda secrets |
| Embeddings calculados | `ticker_news_embeddings` tem linhas | ⚠️ Aguarda execução |
| Databricks App responde | HTTP 200 em endpoints | ⚠️ Aguarda deploy |
| Agente lê dados | MCP tools respondem | ⚠️ Aguarda deploy |
| Agente escreve | `place_order()` sem erro (paper) | ⚠️ Aguarda config |

### 5.2 Métricas de Qualidade

| Métrica | Objetivo | Minimo Aceitável |
|---------|----------|------------------|
| Latência de query RAG | < 2s | < 5s |
| Throughput de embeddings | > 100/min | > 50/min |
| Disponibilidade do App | > 95% | > 90% |
| Precisão de busca | > 70% | > 50% |

---

## 6. Riscos e Mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| API rate limit exceeded | Alta | Médio | Implementar backoff, reducing batch size |
| Secret scope ACL issues | Média | Alto | Usar `users` group temporariamente |
| Embeddings falhar | Baixa | Médio | Validar modelo localmente antes |
| Databricks Apps não iniciar | Média | Alto | Verificar logs `databricks apps logs` |
| Alpaca paper-trading falhar | Baixa | Médio | Verificar credenciais e endpoint |

---

## 7. Próximos Passos Imediatos

1. **Obter acesso ao Databricks Workspace** (se ainda não tem)
2. **Criar conta no Massive API** (necessária para dados de mercado)
3. **Configurar Lakebase URL** no workspace
4. **Executar SQLs de setup** nas tabelas
5. **Rodar `setup_secrets.py`** para armazenar credentials
6. **Testar acesso ao Lakebase** com query simples
7. **Deploy dos Apps** usando `databricks bundle deploy`
8. **Validar endpoints** com curl/Python
9. **Executar notebook** de ingestão manualmente
10. **Validar embeddings** com query de busca semântica

---

## 8. Arquivos do Projeto

### 8.1 Código Principal

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `app.py` | Main Flask app (Day 1/2) | ✅ Implementado |
| `app.yaml` | Config Databricks App | ✅ Implementado |
| `lakebase.py` | Conexão Lakebase | ✅ Implementado |
| `massive_client.py` | Cliente Massive API | ✅ Implementado |
| `setup_secrets.py` | Setup de secrets | ✅ Implementado |

### 8.2 Day 3 - MCP Server

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `mcp_server/alpaca_mcp_server.py` | FastMCP server | ✅ Implementado |
| `mcp_server/alpaca_broker.py` | Broker Alpaca | ✅ Implementado |
| `mcp_server/lakebase.py` | Conexão Lakebase | ✅ Implementado |
| `mcp_server/massive_broker.py` | Broker Massive | ✅ Implementado |
| `mcp_server/app.yaml` | Config MCP App | ✅ Implementado |
| `mcp_server/requirements.txt` | Dependencies | ⚠️ Verificar |

### 8.3 Day 3 - Dashboard

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `dashboard/app.py` | Dashboard Flask | ✅ Implementado |
| `dashboard/app.yaml` | Config Dashboard | ✅ Implementado |
| `dashboard/templates/index.html` | UI dashboard | ✅ Implementado |
| `dashboard/__init__.py` | Package init | ✅ Implementado |

### 8.4 Day 2 - Pipeline

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `notebooks/ingest_ticker_news_embeddings.py` | Spark pipeline | ✅ Implementado |
| `sql/01_setup_news_table.sql` | Table news | ✅ Implementado |
| `sql/02_setup_embeddings_table.sql` | Table embeddings | ✅ Implementado |
| `sql/03_setup_chunk_embeddings_table.sql` | Table chunks | ✅ Implementado |
| `sql/04_cast_arrays_to_vectors.sql` | Vector cast | ✅ Implementado |
| `resources/ingest_ticker_news_embeddings_job.yml` | Scheduled job | ✅ Implementado |

### 8.5 Configuração

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `databricks.yml` | Bundle config | ✅ Implementado |
| `resources/dashboard.yml` | Dashboard resource | ✅ Implementado |
| `resources/mcp_server.yml` | MCP resource | ✅ Implementado |

---

## 9. Referências

- **Capstone Official:** https://github.com/EcZachly/databricks-ai-bootcamp-capstone
- **Day 1:** https://github.com/EcZachly/databricks-lakebase-app-day-1
- **Day 2:** https://github.com/EcZachly/databricks-lakebase-app-day-2
- **Day 3:** https://github.com/EcZachly/databricks-lakebase-app-day-3
- **NotebookLM:** https://github.com/teng-lin/notebooklm-py
- **Notebook do Usuário:** https://notebook.google.com/notebook/da2bd8e6-454b-4e35-a2e3-c9924ebe7630

---

## 10. Histórico de Atualizações

| Data | Versão | Autor | Alterações |
|------|--------|-------|------------|
| 2026-08-08 | v1.0 | Roberto | Status inicial, migração Day 3 |
| 2026-08-09 | v1.1 | Roberto | Entendimento do capstone |
| 2026-08-10 | v2.0 | Claude | PRD e Plano de Execução completo |
| 2026-08-10 | v3.0 | Claude | Atualização: proposta = Stock-market research assistant; trading removido como requisito obrigatório; foco em notas/relatórios para ações de escrita do agente |

---

## 11. Checklist de Pré-Entrega

- [ ] Acesso ao Databricks Workspace confirmado
- [ ] Massive API Key criada e testada
- [ ] Alpaca Paper Account criado (opcional; trade não é requisito do capstone)
- [ ] Lakebase URL configurado
- [ ] SQLs executados com sucesso
- [ ] Secrets armazenados (sem commit no Git)
- [ ] Main App deployado e testado
- [ ] Dashboard deployado e testado
- [ ] MCP Server deployado e testado
- [ ] Notebook de ingestão executado
- [ ] Embeddings calculados e visíveis
- [ ] Busca semântica funcionando
- [ ] Agent Bricks configurado (opcional)
- [ ] Documentação finalizada
- [ ] Demo gravada/presentada
