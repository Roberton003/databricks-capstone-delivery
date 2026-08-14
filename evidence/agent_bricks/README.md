# Agent Bricks write tool evidence

## Current status: VALIDATED

The fresh run on 2026-08-14 completed the required write chain against endpoint `mas-581396aa-endpoint`:

1. Agent Bricks emitted an `mcp_approval_request` for `save_weather_note`.
2. The approved continuation returned a real `function_call_output`.
3. An authenticated owner-scoped `SELECT` returned the same persisted row.

The complete redacted evidence is in `live_write_20260814.txt`.

Validated note ID:

```text
3075257bb28e0e5a5d38932909d18b06a842bee6c172270e2f61ddcd2ef2c686
```

The tool result and query both identify:

```text
owner_email: roberto.m0010@gmail.com
location: Lisbon
title: agent-bricks-live-evidence
content_length: 37
```

## Historical negative example

`attempt_1786526938.json` and `approval_1786526977.json` document an earlier approval request followed by a greeting rather than a tool result. They are retained as a negative example demonstrating that an approval request alone is not persistence evidence.

## Reproduction template

Use a fresh token at execution time; never commit the resolved token or request headers:

```bash
TOKEN=$(databricks auth token --output json | python3 -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')
curl -sS -X POST https://dbc-ab479437-b1bb.cloud.databricks.com/serving-endpoints/mas-581396aa-endpoint/invocations \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d @evidence/agent_bricks/attempt_1786526938.json
```

The historical fixture is diagnostic only. Use `live_write_20260814.txt` as the completion evidence.

No access token, cookie, authorization header, password, or secret value is stored in the evidence output.
