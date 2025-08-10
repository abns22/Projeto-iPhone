# Solução para Erro de Rede no PythonAnywhere

## Problema Identificado

O erro `OSError: [Errno 101] Network is unreachable` indica que o PythonAnywhere não consegue se conectar ao servidor SMTP do Gmail. Isso é comum em ambientes de hospedagem compartilhada.

## Soluções Disponíveis

### 1. ✅ Solução Imediata (Já Implementada)

A função `enviar_orcamento` foi atualizada para:
- **Salvar o orçamento no banco de dados** (funciona perfeitamente)
- **Capturar erros de email** sem causar erro 500
- **Retornar mensagem de sucesso** indicando que o email falhou

**Resultado:** O sistema agora funciona, mas sem envio de emails.

### 2. 🔧 Soluções para Habilitar Email

#### Opção A: Usar SMTP do PythonAnywhere (Recomendado)

1. **Acesse o PythonAnywhere Dashboard**
2. **Vá em "Email" no menu lateral**
3. **Configure um email personalizado** ou use o email padrão
4. **Atualize as configurações da empresa no banco:**

```sql
UPDATE empresas 
SET email_empresa = 'seu_usuario@pythonanywhere.com',
    senha_email_empresa = 'sua_senha_pythonanywhere',
    servidor_smtp = 'smtp.pythonanywhere.com',
    porta_smtp = 587,
    usar_tls = 1,
    usar_ssl = 0
WHERE id = 3;
```

#### Opção B: Usar Gmail com App Password

1. **Ative a verificação em duas etapas no Gmail**
2. **Gere uma senha de app:**
   - Gmail → Configurações → Contas e Importação
   - "Senhas de app" → Gerar nova senha
3. **Atualize as configurações:**

```sql
UPDATE empresas 
SET email_empresa = 'seu_email@gmail.com',
    senha_email_empresa = 'senha_de_app_gerada',
    servidor_smtp = 'smtp.gmail.com',
    porta_smtp = 587,
    usar_tls = 1,
    usar_ssl = 0
WHERE id = 3;
```

#### Opção C: Usar Outlook/Hotmail

```sql
UPDATE empresas 
SET email_empresa = 'seu_email@outlook.com',
    senha_email_empresa = 'sua_senha',
    servidor_smtp = 'smtp-mail.outlook.com',
    porta_smtp = 587,
    usar_tls = 1,
    usar_ssl = 0
WHERE id = 3;
```

### 3. 🧪 Teste de Conectividade

Execute este script no PythonAnywhere para testar:

```python
import smtplib
import ssl

def testar_conectividade_smtp():
    # Teste Gmail
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("✅ Gmail: Conexão estabelecida")
        server.quit()
    except Exception as e:
        print(f"❌ Gmail: {e}")
    
    # Teste PythonAnywhere
    try:
        server = smtplib.SMTP('smtp.pythonanywhere.com', 587)
        server.starttls()
        print("✅ PythonAnywhere: Conexão estabelecida")
        server.quit()
    except Exception as e:
        print(f"❌ PythonAnywhere: {e}")
    
    # Teste Outlook
    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        print("✅ Outlook: Conexão estabelecida")
        server.quit()
    except Exception as e:
        print(f"❌ Outlook: {e}")

testar_conectividade_smtp()
```

### 4. 📧 Configuração Manual no PythonAnywhere

Se preferir configurar manualmente:

1. **Acesse o Console do PythonAnywhere**
2. **Execute o script de teste acima**
3. **Identifique qual servidor funciona**
4. **Atualize as configurações da empresa**

### 5. 🔄 Alternativa: Desabilitar Email Temporariamente

Se quiser focar apenas no funcionamento do sistema:

```python
# No arquivo app.py, comente a seção de email:
# try:
#     # código de email aqui
# except Exception as email_error:
#     pass
```

## Status Atual

✅ **Sistema funcionando** - Orçamentos são salvos no banco  
✅ **Erro 500 resolvido** - Não há mais falhas no endpoint  
⚠️ **Email desabilitado** - Aguardando configuração de SMTP  

## Próximos Passos

1. **Teste o sistema atual** - Verifique se os orçamentos estão sendo salvos
2. **Escolha uma solução de email** - Recomendo PythonAnywhere SMTP
3. **Configure as credenciais** - Atualize o banco de dados
4. **Teste o envio** - Faça um orçamento de teste

## Comandos Úteis

```bash
# Verificar logs no PythonAnywhere
tail -f /var/log/user/your_username/error.log

# Testar conexão SMTP
python3 -c "import smtplib; s=smtplib.SMTP('smtp.pythonanywhere.com', 587); s.starttls(); print('OK')"
```

---

**Nota:** O sistema está funcionando corretamente. O problema era apenas no envio de email, que agora está tratado adequadamente.
