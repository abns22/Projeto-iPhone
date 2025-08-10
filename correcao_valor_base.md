# Correção do Erro "Unknown column 'valor_base' in 'field list'"

## Problema Identificado

O erro `1054 (42S22): Unknown column 'valor_base' in 'field list'` estava ocorrendo porque:

1. **Código incorreto**: A função `enviar_orcamento` em `frontend/app.py` estava tentando selecionar uma coluna chamada `valor_base` da tabela `modelos_iphone`
2. **Schema correto**: A tabela `modelos_iphone` tem uma coluna chamada `valor_base_novo`, não `valor_base`

## Localização do Erro

**Arquivo**: `frontend/app.py`  
**Linha**: 577  
**Função**: `enviar_orcamento`

```python
# ❌ CÓDIGO INCORRETO (antes da correção)
cursor.execute("SELECT valor_base FROM modelos_iphone WHERE id = %s", (modelo_id,))

# ✅ CÓDIGO CORRIGIDO (após a correção)
cursor.execute("SELECT valor_base_novo FROM modelos_iphone WHERE id = %s", (modelo_id,))
```

## Schema da Tabela

A tabela `modelos_iphone` tem a seguinte estrutura (conforme `frontend/setup_database.py`):

```sql
CREATE TABLE IF NOT EXISTS modelos_iphone (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nome_modelo VARCHAR(100) NOT NULL,
    valor_base_novo DECIMAL(10, 2) NOT NULL,  -- ← Esta é a coluna correta
    imagem_padrao_url VARCHAR(255),
    empresa_id INT NOT NULL,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
    UNIQUE(id, empresa_id)
);
```

## Correção Aplicada

A correção foi simples: alterar a query SQL para usar o nome correto da coluna:

```python
# Buscar valor base do modelo
cursor.execute("SELECT valor_base_novo FROM modelos_iphone WHERE id = %s", (modelo_id,))
```

## Verificação

Para verificar se a correção funcionou:

1. **Teste local**: Execute o script `teste_fix_valor_base.py`
2. **Teste no sistema**: Tente enviar um orçamento através da interface web
3. **Verificação de logs**: Os logs não devem mais mostrar o erro `Unknown column 'valor_base'`

## Impacto

Esta correção resolve:
- ✅ O erro 500 ao enviar orçamentos
- ✅ A falha na inserção de dados no banco
- ✅ O problema de "Erro interno do servidor"

## Notas Adicionais

- A função `enviar_orcamento_convite` já estava usando o nome correto da coluna (`valor_base_novo`)
- Outras partes do código que usam `valor_base_novo` estão corretas
- Esta foi uma inconsistência específica na função `enviar_orcamento`

## Status

✅ **CORRIGIDO** - O problema foi identificado e resolvido.
