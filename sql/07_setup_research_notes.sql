-- Lakebase write tools. Notes are scoped to the acting user email, persisted
-- for the agent's research actions and the dashboard's /weather/notes panel.
CREATE TABLE IF NOT EXISTS research_notes (
    id TEXT PRIMARY KEY,
    owner_email TEXT NOT NULL,
    location TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_research_notes_owner
    ON research_notes (owner_email);

CREATE INDEX IF NOT EXISTS idx_research_notes_location
    ON research_notes (location);
