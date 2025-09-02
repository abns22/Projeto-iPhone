# Queries SQL para PythonAnywhere

## Adicionar Campos de Endereço da Empresa

Execute as seguintes queries SQL no seu banco de dados MySQL no PythonAnywhere para adicionar os novos campos de endereço da empresa.

### 1. Adicionar Novas Colunas na Tabela empresas

```sql
ALTER TABLE empresas 
ADD COLUMN cnpj VARCHAR(18) AFTER nome_empresa,
ADD COLUMN endereco_rua VARCHAR(255) AFTER cnpj,
ADD COLUMN endereco_numero VARCHAR(20) AFTER endereco_rua,
ADD COLUMN endereco_bairro VARCHAR(100) AFTER endereco_numero,
ADD COLUMN endereco_cidade VARCHAR(100) AFTER endereco_bairro,
ADD COLUMN endereco_estado VARCHAR(2) AFTER endereco_cidade;
```

### 2. Verificar se as Colunas Foram Criadas

```sql
DESCRIBE empresas;
```

### 3. Verificar Estrutura Completa da Tabela

```sql
SHOW CREATE TABLE empresas;
```

### 4. Atualizar Empresas Existentes (Opcional)

Se você quiser definir um CNPJ padrão para empresas existentes:

```sql
UPDATE empresas SET cnpj = '00.000.000/0000-00' WHERE cnpj IS NULL;
```

## Como Executar no PythonAnywhere

### Opção 1: Via Console MySQL
1. Acesse o console MySQL no PythonAnywhere
2. Conecte ao seu banco de dados
3. Execute as queries uma por vez

### Opção 2: Via Python Script
1. Crie um arquivo Python no PythonAnywhere
2. Execute as queries via código Python
3. Exemplo:

```python
import mysql.connector

# Conectar ao banco
conn = mysql.connector.connect(
    host='seu_host',
    user='seu_usuario',
    password='sua_senha',
    database='seu_banco'
)

cursor = conn.cursor()

# Executar ALTER TABLE
cursor.execute("""
    ALTER TABLE empresas 
    ADD COLUMN cnpj VARCHAR(18) AFTER nome_empresa,
    ADD COLUMN endereco_rua VARCHAR(255) AFTER cnpj,
    ADD COLUMN endereco_numero VARCHAR(20) AFTER endereco_rua,
    ADD COLUMN endereco_bairro VARCHAR(100) AFTER endereco_numero,
    ADD COLUMN endereco_cidade VARCHAR(100) AFTER endereco_bairro,
    ADD COLUMN endereco_estado VARCHAR(2) AFTER endereco_cidade
""")

conn.commit()
cursor.close()
conn.close()
```

## Verificação

Após executar as queries, você pode verificar se tudo funcionou:

1. **Execute o script de teste**: `python testar_campos_empresa.py`
2. **Verifique no painel admin**: Acesse o painel super admin e tente criar/editar uma empresa
3. **Teste os orçamentos**: Verifique se as informações da empresa aparecem nos emails

## Campos Adicionados

- **`cnpj`**: CNPJ da empresa (VARCHAR 18)
- **`endereco_rua`**: Nome da rua (VARCHAR 255)
- **`endereco_numero`**: Número do endereço (VARCHAR 20)
- **`endereco_bairro`**: Nome do bairro (VARCHAR 100)
- **`endereco_cidade`**: Nome da cidade (VARCHAR 100)
- **`endereco_estado`**: UF do estado (VARCHAR 2)

## Funcionalidades Implementadas

✅ **Painel Super Admin**: Campos de endereço no cadastro e edição de empresas  
✅ **Orçamentos**: Informações da empresa (nome, logo, CNPJ, endereço) aparecem nos emails  
✅ **Links de Convite**: Mesmas informações da empresa nos orçamentos via convite  
✅ **Formatação**: Endereço formatado de forma resumida e profissional  

## Próximos Passos

1. Execute as queries SQL no PythonAnywhere
2. Execute o script de teste: `python testar_campos_empresa.py`
3. Teste o sistema no navegador
4. Verifique se as informações da empresa aparecem nos orçamentos

## Suporte

Se encontrar algum problema:
1. Verifique os logs do PythonAnywhere
2. Execute o script de teste para diagnosticar
3. Verifique se todas as colunas foram criadas corretamente
