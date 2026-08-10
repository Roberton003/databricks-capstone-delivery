# Day 1 Lakebase Homework - Status Final

**Data:** 2026-08-10
**Tarefa:** Support Ticket System
**Feedback Original:** 87/100

---

## Resumo das Correções Aplicadas

### Bugs Identificados pelo Instrutor

1. **sample_data.sql** - Usava `gen_random_uuid()` para `ticket_id` nas mensagens, criando UUIDs que não referenciavam os tickets
2. **setup_tickets.py** - Usava IDs hardcoded (1, 2, 3) que não existiam com UUIDs
3. **setup_tickets_databricks.py** - Mesmo problema do setup_tickets.py

### Correções Implementadas

| Arquivo | Antes | Depois |
|---------|-------|--------|
| `sample_data.sql` | `gen_random_uuid()` | CTE com `RETURNING` + `SELECT ticket_id` |
| `setup_tickets.py` | IDs hardcoded (1, 2, 3) | Lookup por título via `RETURNING` |
| `setup_tickets_databricks.py` | IDs hardcoded (1, 2, 3) | Lookup por título via `RETURNING` |
| `initialize_db.sql` | Subqueries corretas | Mantido (já estava OK) |

### Padrão de Correção

A solução segue o padrão do `initialize_db.sql`:
- Inserir tickets com UUIDs gerados automaticamente
- Capturar os UUIDs via `RETURNING` (em Python) ou `SELECT` (em SQL)
- Usar os UUIDs reais para inserir mensagens

---

## Arquivos do Projeto

### Código Principal
- `app.py` - Flask app principal
- `lakebase.py` - Helper de conexão Lakebase
- `requirements.txt` - Dependências

### SQL (Schema e Dados)
- `schema.sql` - DDL (CREATE TABLE)
- `sample_data.sql` - DML corrigido
- `initialize_db.sql` - Script único (DDL + DML)

### Scripts Python
- `setup_tickets.py` - Setup local corrigido
- `setup_tickets_databricks.py` - Setup via Notebook corrigido
- `test_app_local.py` - Testes sem Databricks

### Configuração
- `app.yaml` - Configuração Databricks Apps
- `databricks.yml` - Bundle config

### Documentação
- `TICKETS_README.md` - Documentação completa
- `docs/DAY1_LAKEBASE_FEEDBACK.md` - Feedback do instrutor
- `docs/EVIDENCIAS_DEPLOY.md` - Template para evidências
- `docs/DAY1_STATUS_FINAL.md` - Este arquivo

### Artefatos
- `support-ticket-system.zip` - Arquivo de entrega

---

## Validação Executada

### Sintaxe
- [x] Python (py_compile): OK
- [x] YAML (safe_load): OK
- [x] SQL: Verificado manualmente

### Testes Locais
- [x] test_app_local.py: PASS
  - Imports OK
  - Rotas OK
  - Validação OK
  - Configuração OK

### Consistência dos Scripts
- [x] sample_data.sql: Agora usa CTE com RETURNING
- [x] setup_tickets.py: Agora usa lookup por título
- [x] setup_tickets_databricks.py: Agora usa lookup por título
- [x] initialize_db.sql: Já estava correto

---

## Estatísticas do Sistema

| Item | Valor |
|------|-------|
| Tickets | 3 |
| Status diferentes | 3 (open, in_progress, resolved) |
| Mensagens | 7 (2-3 por ticket) |
| Usuários | 4 (joao.silva, maria.santos, pedro.oliveira, suporte) |
| Endpoints | 5 (GET /, POST /tickets, GET /tickets/<id>, POST /tickets/<id>/messages, POST /tickets/<id>/status) |
| Tabelas | 2 (tickets, ticket_messages) |
| Indices | 2 (idx_ticket_messages_ticket_id, idx_tickets_status) |

---

## Pendências Após Correção

### Prontas para Submissão
- [x] Schema do banco (tickets + ticket_messages)
- [x] Dados de exemplo (3 tickets, 7 mensagens, 3 status)
- [x] Aplicação Flask com CRUD completo
- [x] Leitura via psycopg2
- [x] Escrita via psycopg2
- [x] Update via SQL
- [x] Validação de entrada
- [x] Testes locais passando
- [x] Documentação completa
- [x] Feedback salvo
- [x] Scripts de sample data corrigidos

### Requer Deploy no Databricks
- [ ] URL do Databricks App (gerada após deploy)
- [ ] Screenshot do app funcionando
- [ ] Screenshot das tabelas no Lakebase
- [ ] Capturar logs de execução

### Pode Ser Feito Depois
- [ ] Adicionar filtro por status
- [ ] Adicionar prioridade dos tickets
- [ ] Notificações por email
- [ ] Exportação CSV

---

## Próxima Ação

Execute o deploy no Databricks Workspace:

```bash
# 1. Configurar secret
databricks secrets create-scope database
databricks secrets put --scope database --key lakebase-url

# 2. Executar schema + dados
# Importar setup_tickets_databricks.py como notebook e executar

# 3. Deploy da aplicação
databricks apps deploy --app-name support-ticket-app
```

Após deploy, capture as evidências conforme `docs/EVIDENCIAS_DEPLOY.md`.

---

## GitHub

Repositório: https://github.com/Roberton003/databricks-capstone-delivery

Último commit:
```
feat(tickets): corrigir bugs de UUID identificados pelo instrutor
```

---

*Status atualizado em 2026-08-10*