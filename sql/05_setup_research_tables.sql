-- Setup script for research_notes and analysis_reports tables
-- Run this manually in your Lakebase Postgres database before using agent writing tools

-- Create research_notes table for agent notes
CREATE TABLE IF NOT EXISTS research_notes (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create analysis_reports table for agent analysis reports
CREATE TABLE IF NOT EXISTS analysis_reports (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    report JSONB NOT NULL,
    sources JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes for ticker lookups
CREATE INDEX IF NOT EXISTS idx_research_notes_ticker ON research_notes (ticker);
CREATE INDEX IF NOT EXISTS idx_analysis_reports_ticker ON analysis_reports (ticker);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_research_notes_updated_at
    BEFORE UPDATE ON research_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the tables were created
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name IN ('research_notes', 'analysis_reports')
ORDER BY table_name, ordinal_position;
