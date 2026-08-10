# 🔌 API Reference

Documentação da API e tools do MCP Server.

## Endpoints da API Principal

### Watchlist

```
GET /watchlist
```

Retorna lista de tickers rastreados.

### Preços

```
GET /price/<symbol>
```

Retorna preço atual de um ticker.

### Notícias

```
GET /news/<symbol>
```

Retorna notícias recentes de um ticker.

```
POST /news/sync
```

Sincroniza notícias para todos os tickers da watchlist.

### Busca Semântica

```
POST /search/context
Content-Type: application/json

{
  "query": "cotação da AAPL",
  "symbol": "AAPL",
  "limit": 5
}
```

Retorna chunks semânticamente relevantes.

## Tools do MCP Server

### Leitura

| Tool | Parâmetros | Retorna |
|------|------------|---------|
| `get_quote` | `symbol` | Preço atual |
| `search_news` | `symbol, query, limit` | Lista de notícias |
| `search_research_context` | `query, symbol` | Top-k chunks |
| `get_watchlist` | - | Lista de tickers |
| `add_to_watchlist` | `symbol` | Status da operação |
| `remove_from_watchlist` | `symbol` | Status da operação |

### Escrita (Agente)

| Tool | Parâmetros | Retorna |
|------|------------|---------|
| `save_research_note` | `symbol, title, content` | ID, ticker, title |
| `save_analysis_report` | `symbol, report, sources` | ID, ticker |

## Erros

Todos os endpoints retornam JSON com estrutura:

```json
{
  "status": "ok" | "error",
  "message": "Descrição do erro",
  "data": { ... } | null
}
```
