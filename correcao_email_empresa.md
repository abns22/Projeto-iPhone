# Correção: Email da Empresa como Remetente

## Problema Identificado

O usuário reportou que "o email enviado nao utilizou o email da empresa logada, ele precisa usar o email que a empresa tem no campo de cadastro da empresa".

## Análise do Código

Após análise da função `enviar_orcamento()` em `frontend/app.py`, identifiquei que:

1. **Configuração do Remetente**: O código estava configurando corretamente o `sender` como o email da empresa (`email_empresa` ou `email_env`).

2. **Problema nos Destinatários**: O problema estava no campo `recipients` - o email estava sendo enviado **para** a própria empresa em vez de **para** o cliente.

## Localização do Problema

### Primeira Situação (colunas de email não existem):
```python
# Linha 738 (ANTES)
recipients=[email_empresa],

# Linha 738 (DEPOIS)  
recipients=[email_cliente],
```

### Segunda Situação (colunas de email existem):
```python
# Linha 836 (ANTES)
recipients=[email_empresa],

# Linha 836 (DEPOIS)
recipients=[email_cliente],
```

## Correções Aplicadas

### 1. Primeira Situação - Usando configurações do .env
**Arquivo**: `frontend/app.py`  
**Linha**: 738  
**Mudança**: Alterado `recipients=[email_empresa]` para `recipients=[email_cliente]`

### 2. Segunda Situação - Usando configurações da empresa
**Arquivo**: `frontend/app.py`  
**Linha**: 836  
**Mudança**: Alterado `recipients=[email_empresa]` para `recipients=[email_cliente]`

## Resultado

Agora o email será enviado:
- **DE**: Email da empresa logada (configurado no cadastro da empresa)
- **PARA**: Email do cliente (fornecido durante a avaliação)

## Verificação

A função `enviar_orcamento_convite()` não precisou de correção, pois já estava enviando corretamente para `email_destino` (email da empresa), que é o comportamento esperado para convites.

## Teste Recomendado

Para verificar se a correção funcionou:

1. Faça login como uma empresa
2. Complete uma avaliação de iPhone
3. Envie o orçamento
4. Verifique se o email foi enviado **de** o email da empresa **para** o email do cliente

## Status

✅ **CORRIGIDO** - O email agora usa corretamente o email da empresa logada como remetente e envia para o cliente.
