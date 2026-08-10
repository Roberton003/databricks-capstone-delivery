-- Initialize Database for Support Ticket System
-- Run this single script to create schema and add sample data

-- Create schema
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    created_by TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);

-- Add sample data
-- Tickets
INSERT INTO tickets (title, status, created_by) VALUES
    ('Sistema de autenticação não funciona', 'open', 'joao.silva@empresa.com'),
    ('Relatório de vendas não carrega', 'in_progress', 'maria.santos@empresa.com'),
    ('Acesso ao dashboard negado', 'resolved', 'pedro.oliveira@empresa.com');

-- Messages for ticket 1
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    ((SELECT ticket_id FROM tickets WHERE title = 'Sistema de autenticação não funciona'),
     'Não consigo fazer login no sistema. A tela fica carregando e não avança.',
     'joao.silva@empresa.com'),
    ((SELECT ticket_id FROM tickets WHERE title = 'Sistema de autenticação não funciona'),
     'Vamos verificar os logs do servidor. Já tentou limpar o cache do navegador?',
     'suporte@empresa.com');

-- Messages for ticket 2
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    ((SELECT ticket_id FROM tickets WHERE title = 'Relatório de vendas não carrega'),
     'O relatório de vendas do mês passado não está carregando.',
     'maria.santos@empresa.com'),
    ((SELECT ticket_id FROM tickets WHERE title = 'Relatório de vendas não carrega'),
     'Verificamos e há um erro de timeout na query. Estamos otimizando.',
     'suporte@empresa.com'),
    ((SELECT ticket_id FROM tickets WHERE title = 'Relatório de vendas não carrega'),
     'O relatório demorou mas acabou de carregar. Obrigado!',
     'maria.santos@empresa.com');

-- Messages for ticket 3
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    ((SELECT ticket_id FROM tickets WHERE title = 'Acesso ao dashboard negado'),
     'Não tenho acesso ao dashboard financeiro.',
     'pedro.oliveira@empresa.com'),
    ((SELECT ticket_id FROM tickets WHERE title = 'Acesso ao dashboard negado'),
     'Verificado - permissões foram removidas acidentalmente. Restaurando.',
     'suporte@empresa.com'),
    ((SELECT ticket_id FROM tickets WHERE title = 'Acesso ao dashboard negado'),
     'Acesso restaurado. Obrigado pela rapidez!',
     'pedro.oliveira@empresa.com');

-- Verify data
SELECT 'Database initialized successfully!' as status;
SELECT COUNT(*) as ticket_count FROM tickets;
SELECT COUNT(*) as message_count FROM ticket_messages;
SELECT DISTINCT status as ticket_statuses FROM tickets;
