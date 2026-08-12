# Agent Bricks write tool evidence

Captured 2026-08-12 (UTC) against endpoint `mas-581396aa-endpoint` (host `dbc-ab479437-b1bb.cloud.databricks.com`) using `databricks auth token`.

The supervisor accepted the user instruction to call `save_weather_note` and emitted a `mcp_approval_request` block that names `weather-mcp` and carries the full arguments the agent intended to write:

```json
{"tool_choice": null, "truncation": null, "id": "resp_b990f171633146f59915c172e6fff522", "created_at": null, "error": null, "incomplete_details": null, "instructions": null, "metadata": null, "model": null, "object": "response", "output": [{"type": "message", "id": "msg_bdrk_018MvTDUSTpCfJvWPxpULDRD", "role": "assistant", "content": [{"type": "output_text", "text": "I'll call the save_weather_note function with the specified parameters for Lisbon."}]}, {"type": "mcp_approval_request", "id": "toolu_bdrk_013oivy1jfvH9iSY1GNcJrba", "arguments": "{\"location\": \"Lisbon\", \"title\": \"agent-bricks-evidence 1786526938\", \"content\": \"transcript attempt 1786526938\", \"owner_email\": \"user@example.com\"}", "name": "save_weather_note", "server_label": "weather-mcp"}], "parallel_tool_calls": null, "temperature": null, "tools": null, "top_p": null, "max_output_tokens": null, "previous_response_id": null, "reasoning": null, "status": "completed", "text": null, "usage": null, "user": null, "custom_outputs": null}
```

## Status of the approval flow

- `POST /invocations` → 200 with `status: completed` and a single `mcp_approval_request` block.
- The follow-up approval POST returned 200 but produced an assistant greeting instead of the tool result. The endpoint contract here does not accept `previous_response_id` as a continuation cursor; the supervisor emits a fresh response cycle on resubmission. This means the write tool is reachable from the supervisor, but persisting the result through the same endpoint requires driving the approval response inside the same call (no separate approval step), which is what produced the captured `mcp_approval_request`.
- Dashboard authenticated POST/DELETE (`evidence/05_dashboard_authenticated_calls.txt`) already proves that the same `save_research_note` and `add/remove_from_watchlist` helpers mutate Lakebase via dynamic OAuth; the supervisor wires those same helpers via the MCP server.

## Reproduction commands

```bash
TOKEN=$(databricks auth token --output json | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')
curl -sS -X POST https://dbc-ab479437-b1bb.cloud.databricks.com/serving-endpoints/mas-581396aa-endpoint/invocations \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @evidence/agent_bricks/attempt_1786526938.json
```
