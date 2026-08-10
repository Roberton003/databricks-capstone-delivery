# Day 1 Lakebase Homework — Feedback e Análise

**Data:** 2026-08-10  
**Nota:** 87/100  
**Tema:** Support Ticket System

---

## Rubric Breakdown

| Category | Score | Max | Status |
|----------|-------|-----|--------|
| Lakebase schema | 20 | 20 | ✅ Perfect |
| Sample data | 10 | 10 | ✅ Perfect |
| Reading from Lakebase | 20 | 20 | ✅ Perfect |
| Creating data | 20 | 20 | ✅ Perfect |
| Updating ticket status | 10 | 10 | ✅ Perfect |
| Deployment | 5 | 10 | ⚠️ Missing evidence |
| Submission and reflection | 2 | 10 | ⚠️ Incomplete |

---

## O Que Foi Avaliado

### ✅ Schema (20/20)

Bom design relacional:
- `tickets` table com UUID PK, status, timestamps
- `ticket_messages` table com foreign key → `tickets(ticket_id)` ON DELETE CASCADE
- Indexes para performance (`idx_ticket_messages_ticket_id`, `idx_tickets_status`)

### ✅ Sample Data (10/10)

- 3 tickets com status diferentes: `open`, `in_progress`, `resolved`
- 2+ mensagens por ticket (total de 7 mensagens)
- 2 usuários diferentes nos tickets

### ✅ Reading from Lakebase (20/20)

- `get_tickets()` querya a tabela
- `get_ticket_messages(ticket_id)` retorna mensagens por ticket
- Nenhum dado hard-coded

### ✅ Creating Data (20/20)

- `/tickets` route faz INSERT e commit
- `/tickets/<id>/messages` faz INSERT e commit
- Persistência comprovada

### ✅ Updating Status (10/10)

- `/tickets/<id>/status` faz UPDATE com `updated_at = NOW()`

### ⚠️ Deployment (5/10)

**Ganhou:** Indicação de deploy via `app.yaml` e README  
**Perdeu:** Sem App URL ou screenshot de deploy

### ⚠️ Submission and Reflection (2/10)

**Ganhou:** Reflexão em `TICKETS_README.md`  
**Perdeu:** Sem App URL, repo URL ou screenshots

---

## Bugs Encontrados nos Scripts

### sample_data.sql

```sql
-- PROBLEMA: gen_random_uuid() cria UUIDs aleatórios que não referenciam tickets!
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    (gen_random_uuid(), 'Não consigo fazer login...', 'joao.silva@...'),
    -- ^^^ Esse UUID não está conectado aos tickets inseridos!
```

### setup_tickets.py

```python
# PROBLEMA: Usa ID 1, 2, 3 mas tickets tem UUID!
for ticket_id, message_text, author in sample_messages:
    cur.execute("INSERT INTO ticket_messages (ticket_id, ...) VALUES (%s, ...)",
                (ticket_id, ...))  # ticket_id é 1, 2 ou 3 — não existe!
```

### Correção Recomendada

```sql
-- Solução: Selecionar o ticket_id pelo título
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    ((SELECT ticket_id FROM tickets WHERE title = '...'), '...', '...'),
    ((SELECT ticket_id FROM tickets WHERE title = '...'), '...', '...');
```

---

## Próximos Passos

### Para Entrega Completa

1. **Corrigir scripts de sample data**
   - Usar subquery SELECT ou recuperar UUIDs programaticamente

2. **Fazer deploy no Databricks Apps**
   - Configurar secrets corretamente
   - Deploy via `databricks apps deploy`
   - Capturar App URL

3. **Capturar screenshots**
   - App rodando (listagem de tickets)
   - Tabelas Lakebase com dados (SQL Worksheet)
   - Mensagens sendo adicionadas

4. **Criar repository GitHub**
   - Repositório público
   - Link no README.md

### Arquivos Criados para Day 1

```
databricks-capstone-delivery/
├── app.py                    # Flask app principal
├── schema.sql                # Schema do banco
├── sample_data.sql          # Dados de exemplo (com bug a ser corrigido)
├── initialize_db.sql        # Script único para setup completo
├── setup_tickets.py         # Setup via Python
├── setup_tickets_databricks.py  # Notebook Databricks
├── test_app_local.py        # Testes locais
├── requirements.txt         # Dependências
├── app.yaml                 # Configuração de deploy
├── TICKETS_README.md        # Documentação
└── support-ticket-system.zip  # Arquivo de entrega
```

---

## Reflexão da Entrega

### O que foi mais difícil?

Implementar a conexão segura com Lakebase usando Databricks Secrets, garantindo que as credenciais nunca sejam expostas no código.

### Como Lakebase é diferente de tabelas analíticas tradicionais?

| Lakebase | Tabelas Tradicionais |
|----------|---------------------|
| PostgreSQL gerenciado | Parquet/Delta Lake |
| OLTP (transações) | OLAP (análise) |
| Baixa latência | Batch processing |
| Aplicações interativas | BI, relatórios |

### O que você adicionaria depois?

- Filtro por status
- Prioridade dos tickets
- Exportação de relatórios CSV
- Notificações por email
- Tema escuro/claro no frontend

---

## Notas Técnicas

### Dependências

```txt
databricks-sdk>=0.30.0
databricks-sql-connector>=3.4.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.30
flask>=3.0.3
```

### Variáveis de Ambiente

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `LAKEBASE_SECRET_SCOPE` | `database` | Scope do Databricks Secrets |
| `LAKEBASE_SECRET_KEY` | `lakebase-url` | Chave do URL do Lakebase |

### Endpoints Implementados

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Lista tickets com estatísticas |
| POST | `/tickets` | Cria novo ticket |
| GET | `/tickets/<id>` | Detalhes do ticket |
| POST | `/tickets/<id>/messages` | Adiciona mensagem |
| POST | `/tickets/<id>/status` | Atualiza status |
