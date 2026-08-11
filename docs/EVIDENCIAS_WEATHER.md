# Evidências — Weather Intelligence

Este documento mapeia as evidências reproduzíveis para as três atividades do portal:

- **Vector Weather Retrieval Service**
- **Build your own weather MCP server**
- **Capstone Project Submission**

As imagens em `evidence/` são capturas renderizadas das saídas reais dos comandos executados. Elas não simulam a interface Databricks e não substituem uma captura autenticada do Workspace quando o portal exigir esse formato.

## 1. Vector Weather Retrieval Service

| Requisito | Evidência |
|---|---|
| Dados NWS normalizados | `evidence/02_lakebase_vectors.png` |
| Documentos carregados no Lakebase | `weather_documents = 14` |
| Embeddings armazenados | `weather_embeddings = 14` |
| Dimensão compatível | `vector(384)` |
| Busca vetorial | `<=>` validado no código e executado no Lakebase |
| Job remoto | `evidence/03_remote_services.png` |

Arquivos principais:

- `dashboard/weather_client.py`
- `dashboard/weather_sync.py`
- `dashboard/weather_search.py`
- `notebooks/ingest_weather_embeddings.py`
- `sql/05_setup_weather_documents.sql`
- `sql/06_setup_weather_embeddings.sql`

## 2. Build your own weather MCP server

| Requisito | Evidência |
|---|---|
| App MCP implantado | `evidence/03_remote_services.png` |
| Transporte HTTP | `weather_mcp_server.py` usa `streamable-http` |
| Ferramentas registradas | `get_current_weather`, `get_forecast`, `predict_umbrella_needed` |
| Testes locais | `evidence/01_local_validation.png` |
| App em execução | `weather-mcp` em estado RUNNING |

Arquivos principais:

- `weather_mcp_server/weather_mcp_server.py`
- `weather_mcp_server/weather_broker.py`
- `weather_mcp_server/weather_service.py`
- `weather_mcp_server/SYSTEM_PROMPT.md`

## 3. Capstone Project Submission

| Item | Evidência |
|---|---|
| Repositório e código | Branch/repositório do projeto |
| Dashboard App | `evidence/03_remote_services.png` |
| Weather MCP App | `evidence/03_remote_services.png` |
| Lakebase e pgvector | `evidence/02_lakebase_vectors.png` |
| Testes e compilação | `evidence/01_local_validation.png` |
| Conversas Agent Bricks | `evidence/04_agent_bricks_conversations.png` |
| Instruções do agente | `weather_mcp_server/SYSTEM_PROMPT.md` |
| Lista de ferramentas | `weather_mcp_server/README.md` |

URLs:

- Dashboard: https://weather-dashboard-7474651435966335.aws.databricksapps.com
- Weather MCP: https://weather-mcp-7474651435966335.aws.databricksapps.com
- Agent endpoint: `mas-581396aa-endpoint`

## Evidência end-to-end do Agent Bricks

As três chamadas foram executadas pelo endpoint Agent Bricks e usaram a ferramenta MCP correspondente:

1. Lisbon — `get_current_weather` — retornou temperatura e precipitação reais.
2. Porto — `get_forecast` — retornou previsão para três dias.
3. London — `predict_umbrella_needed` — retornou recomendação baseada na precipitação.

A captura renderizada está em `evidence/04_agent_bricks_conversations.png`.

## Capturas autenticadas da interface

O Chrome local não possuía uma sessão autenticada reutilizável do Workspace no momento da coleta. Portanto, não foi anexada uma tela de login como evidência. Se o portal exigir especificamente uma captura da interface Databricks, abrir o Workspace autenticado e substituir/adicionar as imagens correspondentes:

- Dashboard App em execução;
- tabelas `weather_documents` e `weather_embeddings` no Lakebase;
- conversa do `Weather Intelligence Agent` no Agent Bricks.
