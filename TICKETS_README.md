# Support Ticket System - Databricks App

Este é um sistema de tickets de suporte construído com Databricks Apps e alimentado por Lakebase (PostgreSQL gerenciado pelo Databricks).

## Arquitetura

```
┌─────────────────┐
│  Databricks App │
│     (Flask)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Lakebase     │
│  (PostgreSQL)   │
└─────────────────┘
```

## Estrutura de Dados

### Tabela: tickets
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| ticket_id | UUID | ID único do ticket (PK) |
| title | TEXT | Título do ticket |
| status | TEXT | Status (open, in_progress, resolved) |
| created_by | TEXT | Usuário que criou |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Última atualização |

### Tabela: ticket_messages
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| message_id | UUID | ID único da mensagem (PK) |
| ticket_id | UUID | FK → tickets(ticket_id) ON DELETE CASCADE |
| message_text | TEXT | Conteúdo da mensagem |
| author | TEXT | Autor da mensagem |
| created_at | TIMESTAMP | Data de criação |

### Indices
- `idx_ticket_messages_ticket_id` - Performance para busca de mensagens
- `idx_tickets_status` - Performance para filtro por status

## Requisitos

- Python 3.10+
- Databricks Workspace com Lakebase habilitado
- Secrets configurados no Databricks

## Instalação

### 1. Configurar Secrets no Databricks

```python
# Execute no Databricks Notebook
# Criar scope
databricks secrets create-scope database

# Adicionar Lakebase URL (base64 encoded)
databricks secrets put --scope database --key lakebase-url
# Cole o URL base64 encoded quando solicitado
```

### 2. Criar Schema e Dados de Exemplo

**Opção A - Script único (recomendado):**
```bash
psql $LAKEBASE_URL -f initialize_db.sql
```

**Opção B - Scripts separados:**
```bash
psql $LAKEBASE_URL -f schema.sql
psql $LAKEBASE_URL -f sample_data.sql
```

**Opção C - Via Databricks Notebook:**
Importe e execute `setup_tickets_databricks.py`

**Opção D - Via Python local:**
```bash
python setup_tickets.py
```

## Deploy no Databricks

### Opção 1: Databricks CLI

```bash
databricks apps deploy --app-name support-ticket-app \
    --source-code-path ./databricks-capstone-delivery \
    --config-file app.yaml
```

### Opção 2: UI do Databricks

1. Acesse **Databricks Apps** no workspace
2. Clique em **Create App**
3. Configure:
   - **App name**: `support-ticket-app`
   - **Source**: Select workspace folder containing `app.py`
   - **App file**: `app.py`
   - **Env vars**:
     - `LAKEBASE_SECRET_SCOPE` = `database`
     - `LAKEBASE_SECRET_KEY` = `lakebase-url`
4. Clique em **Deploy**

### 3. Verificar Deploy

Após o deploy, a URL do app estará disponível em:
- Databricks UI → Apps → support-ticket-app → URL

## Funcionalidades

### 1. Visualizar Tickets (`GET /`)
- Lista todos os tickets com status
- Exibe estatísticas (total, open, in_progress, resolved)
- Formulário inline para criar novo ticket

### 2. Criar Ticket (`POST /tickets`)
- Validação: title não vazio, max 200 caracteres
- Validação: created_by não vazio
- Status inicial automático: `open`
- UUID gerado automaticamente

### 3. Ver Detalhes (`GET /tickets/<ticket_id>`)
- Lista todas as mensagens do ticket
- Histórico completo ordenado por data
- Forms inline para adicionar mensagem e atualizar status

### 4. Adicionar Mensagem (`POST /tickets/<ticket_id>/messages`)
- Validação: message_text não vazio
- UUID gerado automaticamente
- Vinculado ao ticket via FK

### 5. Atualizar Status (`POST /tickets/<ticket_id>/status`)
- Valores válidos: `open`, `in_progress`, `resolved`
- Atualiza `updated_at` automaticamente

## Desenvolvimento Local

```bash
# Install dependencies
pip install -r requirements.txt

# Test without Databricks (uses mock)
python test_app_local.py

# Run locally with real Lakebase
export LAKEBASE_SECRET_SCOPE=database
export LAKEBASE_SECRET_KEY=lakebase-url
export LAKEBASE_URL_BASE64=<base64-encoded-url>
python app.py
```

## Estrutura do Projeto

```
databricks-capstone-delivery/
├── app.py                          # Flask app principal
├── app.yaml                        # Configuração de deploy
├── schema.sql                      # Schema do banco (DDL)
├── sample_data.sql                 # Sample data (DML)
├── initialize_db.sql                # Script único (DDL + DML)
├── setup_tickets.py                # Setup via Python (local)
├── setup_tickets_databricks.py     # Setup via Notebook (Databricks)
├── test_app_local.py               # Testes locais
├── requirements.txt                # Dependências Python
├── TICKETS_README.md               # Esta documentação
├── docs/
│   └── DAY1_LAKEBASE_FEEDBACK.md   # Feedback do instrutor
└── support-ticket-system.zip        # Arquivo para entrega
```

## Solução de Problemas

### Erro de Conexão
- Verifique se o Lakebase URL está correto
- Verifique se o secret foi criado corretamente no scope `database`
- Confirme permissões de READ/WRITE para o papel

### Erro de Foreign Key
- Verifique se as tabelas foram criadas com `schema.sql` ou `initialize_db.sql`
- Confirme que `tickets` existe antes de inserir mensagens

### Erro de UUID
- Confirme que `gen_random_uuid()` está disponível (PostgreSQL 13+)
- Ou habilite a extensão `pgcrypto`

## Validação

Execute os testes locais antes de fazer deploy:

```bash
python test_app_local.py
```

Saída esperada:
```
✓ All imports and functions present
✓ All required routes present
✓ Validation working correctly
✓ App configuration correct
✓ All tests passed!
```

## Entrega

### Checklist para submissão

- [x] Schema do banco criado
- [x] Dados de exemplo (3 tickets, 7 mensagens, 3 status)
- [x] Aplicação Flask implementada
- [x] Leitura via psycopg2
- [x] Escrita via psycopg2
- [x] Update via SQL
- [x] Validação de entrada
- [x] Testes locais
- [x] Documentação completa
- [ ] Deploy no Databricks Apps (executar manualmente)
- [ ] Screenshot do app deployado
- [ ] URL do app (gerada após deploy)

### Arquivos para Submissão

**Obrigatórios:**
1. `support-ticket-system.zip` - Código-fonte completo
2. URL do Databricks App (após deploy)
3. Screenshot do app funcionando

**Recomendados:**
1. Link do repositório GitHub
2. Screenshot das tabelas no Lakebase
3. Transcript da execução do `setup_tickets.py`

## Reflexão da Entrega

### O que foi mais difícil?
Implementar a conexão segura com Lakebase usando Databricks Secrets, garantindo que as credenciais nunca sejam expostas no código. O segredo é base64-encoded e recuperado via `WorkspaceClient().secrets.get_secret()`.

### Como Lakebase é diferente de tabelas analíticas tradicionais?

| Lakebase | Tabelas Tradicionais (Delta/Parquet) |
|----------|--------------------------------------|
| PostgreSQL gerenciado | Parquet/Delta Lake |
| OLTP (transações) | OLAP (análise) |
| Baixa latência | Batch processing |
| ACID guarantees | Append-only log |
| Aplicações interativas | BI, relatórios |
| Foreign keys | Sem constraints |
| UPDATE/DELETE eficiente | Inefficient mutations |

### Próximas funcionalidades?
- **Filtro por status** na listagem de tickets
- **Prioridade dos tickets** (low, medium, high, urgent)
- **Atribuição** a usuários específicos
- **Exportação de relatórios** CSV/PDF
- **Notificações por email** quando status muda
- **Dashboard de estatísticas** mais detalhado
- **Autenticação** com Databricks SSO

---

*Este sistema foi desenvolvido como parte do Databricks AI Bootcamp Day 1 Homework.*