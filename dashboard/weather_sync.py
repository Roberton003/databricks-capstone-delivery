import json
from psycopg2.extras import execute_values

try:
    from . import lakebase
    from .weather_client import parse_timestamp
except ImportError:
    import lakebase
    from weather_client import parse_timestamp


UPSERT_SQL = """
    INSERT INTO weather_documents
        (id, location, source_type, headline, narrative_text,
         issued_at, effective_at, payload)
    VALUES %s
    ON CONFLICT (id) DO UPDATE SET
        location = EXCLUDED.location,
        source_type = EXCLUDED.source_type,
        headline = EXCLUDED.headline,
        narrative_text = EXCLUDED.narrative_text,
        issued_at = EXCLUDED.issued_at,
        effective_at = EXCLUDED.effective_at,
        payload = EXCLUDED.payload,
        synced_at = EXCLUDED.synced_at
"""


def sync_locations(client, locations, limit=50):
    if not isinstance(locations, list) or not locations or not all(
        isinstance(location, str) and location.strip() for location in locations
    ):
        raise ValueError("locations must be a non-empty list of strings")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("limit must be an integer between 1 and 200")

    documents = []
    for location in locations:
        documents.extend(client.get_documents(location))
        if len(documents) >= limit:
            break
    documents = documents[:limit]
    if not documents:
        return 0

    rows = [
        (
            document["id"],
            document["location"],
            document["source_type"],
            document["headline"],
            document["narrative_text"],
            parse_timestamp(document.get("issued_at")),
            parse_timestamp(document.get("effective_at")),
            json.dumps(document["payload"]),
        )
        for document in documents
    ]
    with lakebase.get_connection() as connection:
        with connection.cursor() as cursor:
            execute_values(
                cursor,
                UPSERT_SQL.replace(")\n    ON CONFLICT", ", now())\n    ON CONFLICT"),
                rows,
            )
        connection.commit()
    return len(documents)
