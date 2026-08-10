# 🧠 Sistema Heurístico

Este projeto incorpora um sistema de validação baseado em heurísticas e gates para garantir qualidade e evitar erros comuns de engenharia de dados.

## Data Contract Gate

**Objetivo:** Evitar schema não documentado e inconsistência de dados.

### Verificações Obrigatórias

Antes de considerar uma tabela pronta para produção:

| Check | Descrição | Implementação |
|-------|-----------|---------------|
| Schema esperado | Colunas, tipos, nullability definidos | `sql/01_setup_news_table.sql` |
| Regras de qualidade | Cardinalidade, unicidade, validações | Constraints no CREATE TABLE |
| SLA de volume/latência | Volume esperado e freshness | Documentado no schema |
| Contrato versionado | Mudanças são breaking/warning/safe | Versionamento em commits |

### Exemplo de Contrato

```sql
CREATE TABLE research_notes (
    id SERIAL PRIMARY KEY,        -- NOT NULL + UNIQUE
    ticker TEXT NOT NULL,         -- NOT NULL constraint
    title TEXT NOT NULL,
    content TEXT,                 -- Nullable permitido
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## Idempotency Gate

**Objetivo:** Evitar reprocessamento que cause duplicação de dados.

### Verificações Obrigatórias

| Check | Descrição | Implementação |
|-------|-----------|---------------|
| UPSERT definido | `ON CONFLICT DO UPDATE` ou `INSERT ... ON CONFLICT DO NOTHING` | Todas as tabelas |
| Nenhum append cego | Sem `INSERT INTO ... SELECT` sem verificação | Verificado em SQLs |
| Custo estimado | Estimativa de reprocessamento | Documentado no schema |

### Strategy por Tabela

| Tabela | Strategy | Chave |
|--------|----------|-------|
| `ticker_news_documents` | UPSERT | `id` (artigo único) |
| `ticker_news_embeddings` | UPSERT | `id, model_name` |
| `ticker_news_chunk_embeddings` | UPSERT | `document_id, chunk_index` |
| `research_notes` | INSERT | Auto-increment ID |
| `analysis_reports` | INSERT | Auto-increment ID |

---

## Heurísticas Principais

### 1. Check antes de escrita

**Regra:** Valide toda entrada antes de persistir no banco.

```python
def save_research_note(symbol: str, title: str, content: str | None = None) -> dict:
    # Validação de entrada
    symbol = symbol.strip().upper()
    if not symbol or not title:
        return {"status": "error", "message": "Symbol e title são obrigatórios"}
    # ... persistência
```

**Benefício:** Evita dados inválidos no banco.

---

### 2. Rastreabilidade de evidência

**Regra:** Toda conclusão indica SOURCE/INFERENCE/IMPLEMENTED/VALIDATED/UNKNOWN.

**Aplicação no PRD:**
- `SOURCE`: Diretamente do NotebookLM ou código existente
- `INFERENCE`: Derivado de múltiplos SOURCEs
- `IMPLEMENTED`: Código/config existe
- `VALIDATED`: Reproduzível no ambiente
- `UNKNOWN`: Insuficiente para classificar

**Benefício:** Evita confundir o que foi ensinado com o que foi implementado.

---

### 3. Gates antes de deploy

**Regra:** Dois checklists obrigatórios antes de considerar pronto.

**Data Contract Gate:**
- Schema documentado?
- Regras de qualidade definidas?
- SLA estabelecido?
- Contrato versionado?

**Idempotency Gate:**
- UPSERT definido?
- Nenhum append cego?
- Custo estimado?

**Benefício:** Evita deploy de código não validado.

---

### 4. Falsos positivos vs falsos negativos (RAG)

**Regra:** Avalie balanceadamente ambos os tipos de erro.

| Erro | Impacto | Como medir |
|------|---------|------------|
| **Falso positivo (alucinação)** | Resposta errada, perda de confiança | Revisão humana, golden test |
| **Falso negativo (recusa útil)** | Cliente insatisfeito, trust degrade | Log de queries não respondidas |

**Benefício:** Evita foco excessivo em apenas um tipo de erro.

---

## Checklist de Sucesso

Antes de considerar o projeto "pronto":

- [ ] Data Contract Gate passado (todas as tabelas)
- [ ] Idempotency Gate passado (pipeline reexecutável)
- [ ] Heurística 1: Checks antes de escrita
- [ ] Heurística 2: Rastreabilidade de evidência
- [ ] Heurística 3: Gates antes de deploy
- [ ] Heurística 4: Avaliação balanceada de RAG
- [ ] Teste RAG (`test_rag.py`) passando
- [ ] Wiki completa

---

## Referências

- [openf1-data-platform](https://github.com/Roberton003/openf1-data-platform) - Pattern de gates
- [copa-challenger-dados-por-todos](https://github.com/Roberton003/copa-challenger-dados-por-todos) - Heurísticas aplicadas
