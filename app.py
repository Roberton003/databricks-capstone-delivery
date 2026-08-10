"""
Databricks App - Support Ticket System
Built for Lakebase-powered support ticket management.
"""

import os
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from flask import Flask, request, redirect, url_for, session
from databricks.sdk import WorkspaceClient

import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", str(uuid.uuid4()))

# Configuration
_SCOPE = os.environ.get("LAKEBASE_SECRET_SCOPE", "database")
_KEY = os.environ.get("LAKEBASE_SECRET_KEY", "lakebase-url")


def _lakebase_url() -> str:
    """Fetch and decode the Lakebase connection URL from the Databricks secret scope."""
    _w = WorkspaceClient()
    secret = _w.secrets.get_secret(scope=_SCOPE, key=_KEY)
    import base64
    return base64.b64decode(secret.value).decode("utf-8")


@contextmanager
def get_connection():
    """Yield a raw psycopg2 connection with a RealDictCursor factory."""
    conn = psycopg2.connect(_lakebase_url(), cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def get_tickets() -> list[dict]:
    """Get all tickets from the database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    ticket_id,
                    title,
                    status,
                    created_by,
                    created_at,
                    updated_at
                FROM tickets
                ORDER BY created_at DESC
            """)
            return cur.fetchall()


def get_ticket(ticket_id: str) -> Optional[dict]:
    """Get a specific ticket by ID."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM tickets WHERE ticket_id = %s",
                (ticket_id,)
            )
            return cur.fetchone()


def get_ticket_messages(ticket_id: str) -> list[dict]:
    """Get all messages for a specific ticket."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    message_id,
                    ticket_id,
                    message_text,
                    author,
                    created_at
                FROM ticket_messages
                WHERE ticket_id = %s
                ORDER BY created_at ASC
                """,
                (ticket_id,)
            )
            return cur.fetchall()


def create_ticket(title: str, created_by: str) -> dict:
    """Create a new ticket."""
    ticket_id = str(uuid.uuid4())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tickets (ticket_id, title, status, created_by)
                VALUES (%s, %s, %s, %s)
                RETURNING ticket_id, title, status, created_by, created_at, updated_at
                """,
                (ticket_id, title, 'open', created_by)
            )
            conn.commit()
            return cur.fetchone()


def add_message(ticket_id: str, message_text: str, author: str) -> dict:
    """Add a message to a ticket."""
    message_id = str(uuid.uuid4())
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ticket_messages (message_id, ticket_id, message_text, author)
                VALUES (%s, %s, %s, %s)
                RETURNING message_id, ticket_id, message_text, author, created_at
                """,
                (message_id, ticket_id, message_text, author)
            )
            conn.commit()
            return cur.fetchone()


def update_ticket_status(ticket_id: str, status: str) -> dict:
    """Update the status of a ticket."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tickets
                SET status = %s, updated_at = NOW()
                WHERE ticket_id = %s
                RETURNING ticket_id, title, status, created_by, created_at, updated_at
                """,
                (status, ticket_id)
            )
            conn.commit()
            return cur.fetchone()


def get_ticket_statistics() -> dict:
    """Get ticket statistics."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tickets")
            total = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
            open_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) FROM tickets WHERE status = 'in_progress'")
            in_progress_count = cur.fetchone()['count']

            cur.execute("SELECT COUNT(*) FROM tickets WHERE status = 'resolved'")
            resolved_count = cur.fetchone()['count']

            return {
                'total': total,
                'open': open_count,
                'in_progress': in_progress_count,
                'resolved': resolved_count
            }


def validate_ticket_input(title: Optional[str], created_by: Optional[str]) -> tuple[bool, str]:
    """Validate ticket creation input."""
    if not title or not title.strip():
        return False, "Title is required"
    if len(title.strip()) > 200:
        return False, "Title must be 200 characters or less"
    if not created_by or not created_by.strip():
        return False, "Your name/email is required"
    return True, ""


@app.route('/')
def index():
    """Home page - list all tickets."""
    tickets = get_tickets()
    stats = get_ticket_statistics()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support Ticket System</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            .stats {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .stats div {{ display: inline-block; margin-right: 20px; }}
            .ticket-list {{ list-style: none; padding: 0; }}
            .ticket-item {{ background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #ddd; }}
            .ticket-item h3 {{ margin-top: 0; }}
            .status-open {{ color: #28a745; }}
            .status-in_progress {{ color: #ffc107; }}
            .status-resolved {{ color: #6c757d; }}
            .btn {{ padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            .message {{ background: #f8f9fa; padding: 10px; margin-bottom: 10px; border-radius: 4px; border-left: 3px solid #007bff; }}
            .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
            .success {{ color: #155724; background: #d4edda; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <h1>Support Ticket System</h1>

        <div class="stats">
            <strong>Statistics:</strong>
            <div>Total: {stats['total']}</div>
            <div class="status-open">Open: {stats['open']}</div>
            <div class="status-in_progress">In Progress: {stats['in_progress']}</div>
            <div class="status-resolved">Resolved: {stats['resolved']}</div>
        </div>

        <h2>Create New Ticket</h2>
        <form method="POST" action="/tickets" style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <div class="form-group">
                <label for="title">Title:</label>
                <input type="text" id="title" name="title" required maxlength="200" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div class="form-group">
                <label for="created_by">Your Name/Email:</label>
                <input type="text" id="created_by" name="created_by" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <button type="submit" class="btn btn-primary">Create Ticket</button>
        </form>

        <h2>All Tickets</h2>
        <ul class="ticket-list">
    """

    for ticket in tickets:
        status_class = f"status-{ticket['status']}"
        html += f"""
            <li class="ticket-item">
                <h3><a href="/tickets/{ticket['ticket_id']}">{ticket['title']}</a> <span class="{status_class}">[{ticket['status']}]</span></h3>
                <p><strong>Created by:</strong> {ticket['created_by']}</p>
                <p><strong>Created at:</strong> {str(ticket['created_at'])}</p>
            </li>
        """

    html += """
        </ul>
    </body>
    </html>
    """
    return html


@app.route('/tickets', methods=['POST'])
def create_ticket_route():
    """Create a new ticket."""
    title = request.form.get('title', '').strip()
    created_by = request.form.get('created_by', '').strip()

    valid, error = validate_ticket_input(title, created_by)
    if not valid:
        session['error'] = error
        return redirect(url_for('index'))

    try:
        create_ticket(title, created_by)
        session['success'] = 'Ticket created successfully!'
    except Exception as e:
        session['error'] = f'Error creating ticket: {str(e)}'

    return redirect(url_for('index'))


@app.route('/tickets/<ticket_id>')
def ticket_detail(ticket_id):
    """Show ticket details and messages."""
    ticket = get_ticket(ticket_id)
    if not ticket:
        return "<h1>Ticket not found</h1>", 404

    messages = get_ticket_messages(ticket_id)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{ticket['title']} - Support Ticket System</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #333; }}
            .ticket-info {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }}
            .status-open {{ color: #28a745; }}
            .status-in_progress {{ color: #ffc107; }}
            .status-resolved {{ color: #6c757d; }}
            .btn {{ padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .btn-danger {{ background: #dc3545; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
            .message {{ background: #f8f9fa; padding: 15px; margin-bottom: 10px; border-radius: 4px; border-left: 3px solid #007bff; }}
            .message .author {{ font-weight: bold; color: #666; }}
            .message .date {{ font-size: 0.85em; color: #999; }}
            .error {{ color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
            .success {{ color: #155724; background: #d4edda; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
            .nav {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/" class="btn btn-secondary">Back to Tickets</a>
        </div>

        <div class="ticket-info">
            <h1>{ticket['title']} <span class="status-{ticket['status']}">[{ticket['status'].replace('_', ' ')}]</span></h1>
            <p><strong>Created by:</strong> {ticket['created_by']}</p>
            <p><strong>Created at:</strong> {str(ticket['created_at'])}</p>
            <p><strong>Last updated:</strong> {str(ticket['updated_at'])}</p>
        </div>

        <h2>Messages</h2>
    """

    for msg in messages:
        html += f"""
            <div class="message">
                <div class="author">{msg['author']}</div>
                <div class="date">{str(msg['created_at'])}</div>
                <div style="margin-top: 10px;">{msg['message_text']}</div>
            </div>
        """

    html += f"""
        <h2>Add Message</h2>
        <form method="POST" action="/tickets/{ticket_id}/messages" style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <div class="form-group">
                <label for="message_text">Message:</label>
                <textarea id="message_text" name="message_text" required rows="4" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"></textarea>
            </div>
            <div class="form-group">
                <label for="author">Your Name/Email:</label>
                <input type="text" id="author" name="author" required style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <button type="submit" class="btn btn-primary">Add Message</button>
        </form>

        <h2>Update Status</h2>
        <form method="POST" action="/tickets/{ticket_id}/status" style="background: white; padding: 15px; border-radius: 8px;">
            <div class="form-group">
                <label for="status">New Status:</label>
                <select id="status" name="status" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;">
                    <option value="open"{' selected' if ticket['status'] == 'open' else ''}>Open</option>
                    <option value="in_progress"{' selected' if ticket['status'] == 'in_progress' else ''}>In Progress</option>
                    <option value="resolved"{' selected' if ticket['status'] == 'resolved' else ''}>Resolved</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success">Update Status</button>
        </form>
    </body>
    </html>
    """
    return html


@app.route('/tickets/<ticket_id>/messages', methods=['POST'])
def add_message_route(ticket_id):
    """Add a message to a ticket."""
    message_text = request.form.get('message_text', '').strip()
    author = request.form.get('author', '').strip()

    if not message_text:
        session['error'] = 'Message text is required'
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))

    try:
        add_message(ticket_id, message_text, author)
        session['success'] = 'Message added successfully!'
    except Exception as e:
        session['error'] = f'Error adding message: {str(e)}'

    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/tickets/<ticket_id>/status', methods=['POST'])
def update_status_route(ticket_id):
    """Update ticket status."""
    status = request.form.get('status', 'open')

    if status not in ['open', 'in_progress', 'resolved']:
        session['error'] = 'Invalid status'
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))

    try:
        update_ticket_status(ticket_id, status)
        session['success'] = 'Ticket status updated successfully!'
    except Exception as e:
        session['error'] = f'Error updating status: {str(e)}'

    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.errorhandler(Exception)
def handle_exception(err):
    """Handle all unhandled exceptions."""
    return f"<h1>Error</h1><p>{str(err)}</p>", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)
