# Evidências de Deploy - Day 1 Lakebase Homework

Este arquivo contém as evidências de deploy e execução do sistema de tickets de suporte.

---

## Como Capturar Evidências

### 1. Deploy no Databricks Apps

**Comando:**
```bash
databricks apps deploy \
    --app-name support-ticket-app \
    --source-code-path /Workspace/Users/<seu-usuario>/databricks-capstone-delivery \
    --config-file app.yaml
```

**Capturar:**
- [ ] URL do app (formato: https://<workspace>.cloud.databricks.com/apps/support-ticket-app)
- [ ] Screenshot do terminal mostrando o deploy
- [ ] Screenshot da página do Databricks Apps

### 2. Inicializar o Banco de Dados

**Opção A - Via SQL Worksheet:**
1. Abrir Databricks SQL
2. Conectar ao Lakebase
3. Executar `initialize_db.sql`

**Opção B - Via Notebook:**
1. Importar `setup_tickets_databricks.py`
2. Executar todas as células
3. Verificar saída com:
```
✓ Schema created successfully!
✓ Created ticket: ...
✓ Sample data added successfully!
✓ Setup complete!
```

**Capturar:**
- [ ] Screenshot do SQL Worksheet com saída do `initialize_db.sql`
- [ ] Screenshot do Notebook com setup completo
- [ ] Screenshot da query de verificação:
```sql
SELECT * FROM tickets;
SELECT * FROM ticket_messages;
```

### 3. Testar a Aplicação

**Checklist de Testes:**

#### 3.1 Listar Tickets
- Acessar a URL do app
- [ ] Screenshot da página inicial com 3 tickets
- [ ] Verificar que estatísticas mostram: Total=3, Open=1, In Progress=1, Resolved=1

#### 3.2 Criar Ticket
- Preencher formulário:
  - Title: "Teste de deploy"
  - Created by: seu-email@empresa.com
- Clicar em "Create Ticket"
- [ ] Screenshot do ticket criado aparecendo na lista

#### 3.3 Ver Mensagens
- Clicar no ticket "Sistema de autenticação não funciona"
- [ ] Screenshot das mensagens existentes (2 mensagens)

#### 3.4 Adicionar Mensagem
- Preencher formulário de mensagem
- [ ] Screenshot da mensagem adicionada

#### 3.5 Atualizar Status
- Selecionar novo status
- [ ] Screenshot do status atualizado

---

## Template para Capturar Evidências

```
DATABRICKS_APP_URL: <preencher>
DATABRICKS_WORKSPACE: <preencher>
DATA_DEPLOY: <preencher>

LOGS_DEPLOY:
<comando> + <output>

LOGS_SETUP:
<comando> + <output>

SCREENSHOTS:
- app_home.png
- tickets_list.png
- ticket_detail.png
- message_added.png
- status_updated.png
- lake_tables.png
```

---

## Entrega Completa

Após coletar as evidências, enviar:

1. **Código-fonte:**
   - `support-ticket-system.zip` (já criado)

2. **Evidências:**
   - Screenshots das 6 telas acima
   - Logs de deploy e setup
   - URL do Databricks App

3. **Documentação:**
   - `TICKETS_README.md` (já criado)
   - `docs/DAY1_LAKEBASE_FEEDBACK.md` (já criado)

---

## Próximos Passos Após Deploy

1. **Verificar persistência:**
   - Recarregar a página do app
   - Confirmar que os tickets criados anteriormente ainda existem
   - Isso valida que dados estão sendo lidos/escritos no Lakebase

2. **Testar refresh:**
   - Pressionar F5 no navegador
   - Verificar que dados permanecem após refresh

3. **Capturar evidência final:**
   - Screenshot mostrando o ticket criado anteriormente
   - Isso comprova que dados são persistidos

---

*Este arquivo deve ser preenchido após o deploy no Databricks Apps.*