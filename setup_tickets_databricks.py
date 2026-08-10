# Databricks notebook source
# Setup script for Support Ticket System
# Run this in a Databricks Notebook (Python)
#
# CORRECTED VERSION (2026-08-10): Fixes the bug from instructor feedback
# where messages were inserted with hardcoded IDs (1, 2, 3) that did not
# match the actual UUID ticket IDs.

# Configuration
LAKEBASE_SECRET_SCOPE = "database"
LAKEBASE_SECRET_KEY = "lakebase-url"

# COMMAND ----------

# Setup Lakebase connection
import base64
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from databricks.sdk import WorkspaceClient

_w = WorkspaceClient()
secret = _w.secrets.get_secret(scope=LAKEBASE_SECRET_SCOPE, key=LAKEBASE_SECRET_KEY)
LAKEBASE_URL = base64.b64decode(secret.value).decode("utf-8")

@contextmanager
def get_connection():
    """Yield a raw psycopg2 connection with a RealDictCursor factory."""
    conn = psycopg2.connect(LAKEBASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

# COMMAND ----------

# Create schema
def setup_schema():
    """Create the required tables."""
    schema_sql = """
    -- Table: tickets
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        created_by TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Table: ticket_messages
    CREATE TABLE IF NOT EXISTS ticket_messages (
        message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
        message_text TEXT NOT NULL,
        author TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
    CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
            conn.commit()
            print("✓ Schema created successfully!")

# COMMAND ----------

# Add sample data - FIXED to use real UUIDs from inserted tickets
def add_sample_data():
    """Add sample tickets and messages."""
    # Sample tickets with title as identifier (UUIDs are auto-generated)
    tickets = [
        ('Sistema de autenticação não funciona', 'open', 'joao.silva@empresa.com'),
        ('Relatório de vendas não carrega', 'in_progress', 'maria.santos@empresa.com'),
        ('Acesso ao dashboard negado', 'resolved', 'pedro.oliveira@empresa.com'),
    ]

    # Map tickets to their messages by title (FIX: was using hardcoded IDs 1, 2, 3)
    messages_by_ticket = [
        {
            'ticket_title': 'Sistema de autenticação não funciona',
            'messages': [
                ('Não consigo fazer login no sistema. A tela fica carregando e não avança.', 'joao.silva@empresa.com'),
                ('Vamos verificar os logs do servidor. Já tentou limpar o cache do navegador?', 'suporte@empresa.com'),
            ],
        },
        {
            'ticket_title': 'Relatório de vendas não carrega',
            'messages': [
                ('O relatório de vendas do mês passado não está carregando.', 'maria.santos@empresa.com'),
                ('Verificamos e há um erro de timeout na query. Estamos otimizando.', 'suporte@empresa.com'),
                ('O relatório demorou mas acabou de carregar. Obrigado!', 'maria.santos@empresa.com'),
            ],
        },
        {
            'ticket_title': 'Acesso ao dashboard negado',
            'messages': [
                ('Não tenho acesso ao dashboard financeiro.', 'pedro.oliveira@empresa.com'),
                ('Verificado - permissões foram removidas acidentalmente. Restaurando.', 'suporte@empresa.com'),
                ('Acesso restaurado. Obrigado pela rapidez!', 'pedro.oliveira@empresa.com'),
            ],
        },
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Step 1: Insert tickets and collect their UUIDs
            ticket_uuids = {}
            for title, status, created_by in tickets:
                cur.execute(
                    """
                    INSERT INTO tickets (title, status, created_by)
                    VALUES (%s, %s, %s)
                    RETURNING ticket_id, title
                    """,
                    (title, status, created_by)
                )
                result = cur.fetchone()
                ticket_uuids[result['title']] = result['ticket_id']
                print(f"✓ Created ticket: {title[:40]}... (ID: {result['ticket_id']})")

            # Step 2: Insert messages using the actual UUIDs from Step 1
            for ticket_group in messages_by_ticket:
                ticket_title = ticket_group['ticket_title']
                ticket_id = ticket_uuids[ticket_title]

                for message_text, author in ticket_group['messages']:
                    cur.execute(
                        """
                        INSERT INTO ticket_messages (ticket_id, message_text, author)
                        VALUES (%s, %s, %s)
                        """,
                        (ticket_id, message_text, author)
                    )
                    print(f"  ✓ Added message to '{ticket_title[:30]}...'")

            conn.commit()
            print("\n✓ Sample data added successfully!")

# COMMAND ----------

# Verify setup
def check_setup():
    """Verify setup is complete."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tickets")
            ticket_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) FROM ticket_messages")
            message_count = cur.fetchone()['count']

            cur.execute("SELECT DISTINCT status FROM tickets")
            statuses = [r['distinct'] for r in cur.fetchall()]

            # Verify all messages have valid ticket_ids
            cur.execute("""
                SELECT COUNT(*) FROM ticket_messages m
                WHERE NOT EXISTS (SELECT 1 FROM tickets t WHERE t.ticket_id = m.ticket_id)
            """)
            orphan_count = cur.fetchone()['count']

            print("\n=== Setup Verification ===")
            print(f"Tickets: {ticket_count}")
            print(f"Messages: {message_count}")
            print(f"Statuses: {statuses}")
            print(f"Orphan messages: {orphan_count}")

            if orphan_count > 0:
                print("\n✗ Orphan messages found! (Data integrity issue)")
                return False

            if ticket_count >= 3 and message_count >= 6 and len(statuses) >= 2:
                print("\n✓ Setup complete!")
                return True
            else:
                print("\n✗ Setup incomplete.")
                return False

# COMMAND ----------

# Main execution
print("Setting up Support Ticket System...")
setup_schema()
add_sample_data()
check_setup()

# COMMAND ----------

# Query to verify data (run separately)
# %sql
# SELECT * FROM tickets ORDER BY created_at DESC
# SELECT * FROM ticket_messages ORDER BY created_at DESC
