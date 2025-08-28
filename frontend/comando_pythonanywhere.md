# Comandos para PythonAnywhere - Corrigir Erro modelo_interesse

## Problema
Erro: `1054 (42S22): Unknown column 'modelo_interesse' in 'field list'`

## Solução

### 1. Acesse o Console do PythonAnywhere
- Vá para a aba "Consoles" no PythonAnywhere
- Clique em "Bash console"

### 2. Conecte ao MySQL
```bash
mysql -u SEU_USUARIO -p SEU_BANCO_DE_DADOS
```

### 3. Execute o comando SQL
```sql
ALTER TABLE links_convidados ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente;
```

### 4. Verifique se foi adicionada
```sql
DESCRIBE links_convidados;
```

### 5. Saia do MySQL
```sql
EXIT;
```

## Comando Completo (uma linha)
```bash
mysql -u SEU_USUARIO -p SEU_BANCO_DE_DADOS -e "ALTER TABLE links_convidados ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente;"
```

## Verificação Completa (uma linha)
```bash
mysql -u SEU_USUARIO -p SEU_BANCO_DE_DADOS -e "DESCRIBE links_convidados;"
```

## Alternativa via Python Console
Se preferir usar o Python console:

1. Vá para "Consoles" → "Python 3.x console"
2. Execute:
```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='SEU_USUARIO',
    password='SUA_SENHA',
    database='SEU_BANCO_DE_DADOS'
)

cursor = conn.cursor()
cursor.execute("ALTER TABLE links_convidados ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente")
conn.commit()
cursor.close()
conn.close()

print("Coluna modelo_interesse adicionada com sucesso!")
```

## Notas
- Substitua `SEU_USUARIO`, `SUA_SENHA` e `SEU_BANCO_DE_DADOS` pelos valores reais
- Se a coluna já existir, o comando retornará um erro, mas isso é normal
- Após executar, reinicie sua aplicação web no PythonAnywhere

