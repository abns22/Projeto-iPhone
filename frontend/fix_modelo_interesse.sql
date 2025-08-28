-- Comando para adicionar a coluna modelo_interesse à tabela links_convidados
-- Execute este comando no MySQL do PythonAnywhere

ALTER TABLE links_convidados ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente;

