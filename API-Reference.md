# API Reference

Este documento descreve os endpoints da API principal e as ferramentas MCP disponíveis para o agente.

---

## API Endpoints

### Watchlist

#### GET `/watchlist`
Retorna a lista de tickers na watchlist.

**Response:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

#### POST `/watchlist/add`
Adiciona um ticker à watchlist.

**Body:**
```json
{
  "symbol": "TSLA"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "TSLA added to watchlist",
  "watchlist_size": 4
}
```

#### POST `/watchlist/remove`
Remove um ticker da watchlist.

**Body:**
```json
{
  "symbol": "TSLA"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "TSLA removed from watchlist",
  "watchlist_size": 3
}
```

---

### Price Data

#### GET `/price`
Retorna o preço atual de um ticker.

**Query Params:**
- `symbol` (required): Ticker symbol (e.g., AAPL)

**Response:**
```json
{
  "symbol": "AAPL",
  "price": 178.45,
  "change": 2.35,
  "change_percent": 1.33,
  "volume": 52438921,
  "previous_close": 176.10
}
```

---

### News

#### GET `/news`
Busca notícias por ticker.

**Query Params:**
- `symbol` (required): Ticker symbol
- `query` (optional): Search query
- `limit` (optional, default: 10): Max results

**Response:**
```json
{
  "articles": [
    {
      "id": "12345",
      "title": "Apple Reports Record Earnings",
      "description": "Apple announces record quarterly earnings...",
      "article_url": "https://example.com/news/12345",
      "published_utc": "2026-08-09T20:00:00Z",
      "publisher_name": "Financial Times"
    }
  ]
}
```

---

### Search

#### GET `/search`
Busca semântica de contexto (RAG).

**Query Params:**
- `query` (required): Search query
- `symbol` (optional): Filter by ticker
- `limit` (optional, default: 5): Max results

**Response:**
```json
{
  "results": [
    {
      "text": "Analysts maintain neutral stance on Tesla...",
      "ticker": "TSLA",
      "title": "Tesla Q3 2026 Preview",
      "similarity": 0.89
    }
  ]
}
```

---

## MCP Tools

### Leitura

| Tool | Description |
|------|-------------|
| `get_quote` | Get current stock price for a ticker |
| `search_news` | Search recent news for a ticker |
| `search_research_context` | Semantic search on stock news |
| `get_watchlist` | Get user's watchlist |

### Escrita (Agent)

| Tool | Description |
|------|-------------|
| `add_to_watchlist` | Add ticker to watchlist |
| `remove_from_watchlist` | Remove ticker from watchlist |
| `save_research_note` | Save research note for a ticker |
| `save_analysis_report` | Save analysis report for a ticker |

---

## Erros

Todos os endpoints返回 `status: error` com mensagem descritiva em caso de falha:

```json
{
  "status": "error",
  "message": "Invalid ticker symbol"
}
```
