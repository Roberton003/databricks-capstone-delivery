---
title: Support Ticket System
---

# Support Ticket System

This is a support ticket management system powered by Lakebase.

## Features
- View all support tickets
- View messages for each ticket
- Create new tickets
- Add messages to tickets
- Update ticket status
- View ticket statistics

## Ticket Statistics
{{statistics}}

## Tickets
{{tickets}}

---
title: Create New Ticket
---

# Create New Ticket

<form method="POST" action="/tickets">
    <div>
        <label for="title">Title:</label>
        <input type="text" id="title" name="title" required maxlength="200">
    </div>
    <div>
        <label for="created_by">Your Name/Email:</label>
        <input type="text" id="created_by" name="created_by" required>
    </div>
    <div>
        <button type="submit">Create Ticket</button>
    </div>
</form>

---
title: Ticket Details
---

# {{ticket.title}}

**Status:** {{ticket.status}}
**Created by:** {{ticket.created_by}}
**Created at:** {{ticket.created_at}}

## Messages
{{messages}}

## Add Message
<form method="POST" action="/tickets/{{ticket.ticket_id}}/messages">
    <div>
        <label for="message_text">Message:</label>
        <textarea id="message_text" name="message_text" required></textarea>
    </div>
    <div>
        <label for="author">Your Name/Email:</label>
        <input type="text" id="author" name="author" required>
    </div>
    <div>
        <button type="submit">Add Message</button>
    </div>
</form>

## Update Status
<form method="POST" action="/tickets/{{ticket.ticket_id}}/status">
    <div>
        <label for="status">New Status:</label>
        <select id="status" name="status">
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
        </select>
    </div>
    <div>
        <button type="submit">Update Status</button>
    </div>
</form>
