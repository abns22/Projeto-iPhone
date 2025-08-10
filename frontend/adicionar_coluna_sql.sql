-- Script para adicionar a coluna modelo_interesse à tabela avaliacoes_concluidas
-- Execute esta query no seu banco de dados MySQL no PythonAnywhere

-- Primeiro, verificar se a coluna já existe
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'avaliacoes_concluidas' 
AND COLUMN_NAME = 'modelo_interesse';

-- Se a query acima não retornar nenhum resultado, execute a query abaixo:
ALTER TABLE avaliacoes_concluidas 
ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente_final;

-- Verificar se a coluna foi adicionada corretamente
DESCRIBE avaliacoes_concluidas;
