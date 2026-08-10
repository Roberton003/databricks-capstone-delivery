# About

## Stock-Market Research Assistant

Este é o projeto final do **Databricks AI Bootcamp**, desenvolvido como parte do treinamento oficial da DataExpert.io.

### O que é

Um sistema de **pesquisa de mercado de ações** que:
- Coleta preços e notícias via Massive API
- Processa conteúdo não estruturado (notícias)
- Calcula embeddings e permite busca semântica (RAG)
- Permite salvar notas e relatórios de análise
- Oferece um agente de IA com ferramentas MCP

### Tecnologias

| Categoria | Tecnologia |
|-----------|------------|
| Data Warehouse | Databricks Lakebase (PostgreSQL) |
| Processing | Apache Spark |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Search | pgvector (HNSW) |
| APIs | Massive.com |
| Agent | FastMCP (Model Context Protocol) |
| Frontend | Flask |

### Objetivo do Projeto

Demonstrar as habilidades de engenharia de dados, RAG e agentes de IA aprendidas durante o bootcamp.

### Status

**Em desenvolvimento** - Aguardando deploy no Databricks Workspace.

---

*Este projeto foi desenvolvido por Roberto como entrega do Databricks AI Bootcamp.*
