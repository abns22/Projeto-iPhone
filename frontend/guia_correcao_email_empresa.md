# 🔧 Guia para Corrigir o Email da Empresa

## 📋 Problema Identificado

O email está sendo enviado com o remetente incorreto. O sistema deve usar o email da empresa (obaoba.center@outlook.com) como remetente, mas pode estar usando o email do cliente ou o email do .env.

## 🔍 Diagnóstico

O código está funcionando corretamente. O problema pode ser:

1. **Configurações SMTP incompletas**: A empresa não tem servidor_smtp, porta_smtp ou senha_email configurados
2. **Configurações SMTP incorretas**: As configurações estão definidas mas são inválidas
3. **Problema de autenticação**: O email da empresa não está autenticado corretamente

## 🛠️ Solução

### Passo 1: Verificar Configurações Atuais

Execute o script de verificação no PythonAnywhere:

```bash
cd /home/alfredo22/projeto-iphone/frontend
python verificar_configuracao_email.py
```

Este script mostrará:
- Todas as empresas cadastradas
- As configurações de email de cada empresa
- Se o sistema usará as configurações da empresa ou fallback do .env

### Passo 2: Identificar a Empresa Logada

No log do PythonAnywhere, procure por uma linha como:
```
- Empresa ID: 3
```

Compare este ID com a lista de empresas mostrada pelo script.

### Passo 3: Corrigir as Configurações da Empresa

**Via Painel Super-Admin (Recomendado)**

1. Acesse o painel super-admin: `https://alfredo22.pythonanywhere.com/super-admin`
2. Clique em "Editar Empresa" para a empresa que está com problema
3. Configure os campos de email:

**Para Outlook/Hotmail:**
- **Email da Empresa**: obaoba.center@outlook.com
- **Senha do Email**: [senha do outlook]
- **Servidor SMTP**: smtp-mail.outlook.com
- **Porta SMTP**: 587
- **Usar TLS**: Sim
- **Usar SSL**: Não

**Para Gmail:**
- **Email da Empresa**: seu-email@gmail.com
- **Senha do Email**: [senha de app do Gmail]
- **Servidor SMTP**: smtp.gmail.com
- **Porta SMTP**: 587
- **Usar TLS**: Sim
- **Usar SSL**: Não

4. Salve as alterações

### Passo 4: Testar

Após corrigir as configurações:

1. Faça um novo orçamento
2. Verifique no log se aparece:
   ```
   ⚠️ Usando configurações de email da empresa
   - Email remetente: obaoba.center@outlook.com
   ```
3. Confirme que o email foi enviado com o remetente correto

## 📝 Como o Sistema Funciona

O sistema segue esta lógica para definir o remetente:

1. **Se a empresa tem configurações SMTP completas** (servidor, porta, senha):
   - Usa o `email_empresa` do banco de dados como remetente
   - Usa as configurações SMTP da empresa

2. **Se a empresa não tem configurações SMTP completas**:
   - Usa o email do arquivo `.env` como remetente
   - Usa as configurações SMTP do `.env`

## 🔧 Configurações Importantes

### Para Outlook/Hotmail:
- **Servidor**: smtp-mail.outlook.com
- **Porta**: 587
- **TLS**: Sim
- **SSL**: Não
- **Autenticação**: Normal (email + senha)

### Para Gmail:
- **Servidor**: smtp.gmail.com
- **Porta**: 587
- **TLS**: Sim
- **SSL**: Não
- **Autenticação**: Senha de app (não senha normal)

## ✅ Verificação Final

Após a correção, o log deve mostrar:
```
⚠️ Usando configurações de email da empresa
- Email remetente: obaoba.center@outlook.com
```

Em vez de:
```
⚠️ Usando configurações de email do arquivo .env
- Email remetente: ogordogamer2@gmail.com
```

## 🚨 Nota Importante

O email "teste@teste.com" que você vê é o **destinatário** (cliente), não o remetente. O remetente deve ser o email da empresa (obaoba.center@outlook.com).
