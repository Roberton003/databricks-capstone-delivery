-- Sample data for Support Ticket System
-- Run this after creating the schema

-- Insert sample tickets
WITH inserted_tickets AS (
    INSERT INTO tickets (title, status, created_by) VALUES
        ('Sistema de autenticação não funciona', 'open', 'joao.silva@empresa.com'),
        ('Relatório de vendas não carrega', 'in_progress', 'maria.santos@empresa.com'),
        ('Acesso ao dashboard negado', 'resolved', 'pedro.oliveira@empresa.com')
    RETURNING ticket_id, title
)
-- Insert messages using ticket titles to link correctly
INSERT INTO ticket_messages (ticket_id, message_text, author) VALUES
    -- Ticket 1: Sistema de autenticação não funciona
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Sistema de autenticação não funciona'),
     'Não consigo fazer login no sistema. A tela fica carregando e não avança.', 'joao.silva@empresa.com'),
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Sistema de autenticação não funciona'),
     'Vamos verificar os logs do servidor. Já tentou limpar o cache do navegador?', 'suporte@empresa.com'),

    -- Ticket 2: Relatório de vendas não carrega
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Relatório de vendas não carrega'),
     'O relatório de vendas do mês passado não está carregando.', 'maria.santos@empresa.com'),
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Relatório de vendas não carrega'),
     'Verificamos e há um erro de timeout na query. Estamos otimizando.', 'suporte@empresa.com'),
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Relatório de vendas não carrega'),
     'O relatório demorou mas acabou de carregar. Obrigado!', 'maria.santos@empresa.com'),

    -- Ticket 3: Acesso ao dashboard negado
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Acesso ao dashboard negado'),
     'Não tenho acesso ao dashboard financeiro.', 'pedro.oliveira@empresa.com'),
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Acesso ao dashboard negado'),
     'Verificado - permissões foram removidas acidentalmente. Restaurando.', 'suporte@empresa.com'),
    ((SELECT ticket_id FROM inserted_tickets WHERE title = 'Acesso ao dashboard negado'),
     'Acesso restaurado. Obrigado pela rapidez!', 'pedro.oliveira@empresa.com');
