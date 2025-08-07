# 🔧 Configuração de Email para PythonAnywhere

## 📋 Problema Identificado
O sistema de email está falhando no PythonAnywhere devido à falta de configuração das variáveis de ambiente.

## ✅ Solução Implementada
O código foi atualizado para usar variáveis de ambiente com fallback para valores padrão.

## 🛠️ Passos para Configurar no PythonAnywhere

### 1. Acessar o Painel do PythonAnywhere
- Faça login no PythonAnywhere
- Vá para a seção **Web**

### 2. Configurar Variáveis de Ambiente
1. Clique em **Code** no seu aplicativo web
2. Role até a seção **Environment variables**
3. Adicione as seguintes variáveis:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=ogordogamer2@gmail.com
MAIL_PASSWORD=ylmu lcyn khlp ckpd
```

### 3. Configuração Alternativa (se a porta 587 falhar)
Se houver problemas com a porta 587, use:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=ogordogamer2@gmail.com
MAIL_PASSWORD=ylmu lcyn khlp ckpd
```

### 4. Reiniciar o Aplicativo
1. Clique em **Reload** no painel do PythonAnywhere
2. Aguarde alguns segundos para o aplicativo reiniciar

## 🔍 Verificação

### Teste Local (já realizado)
✅ Conexão SMTP: Funcionando  
✅ Autenticação: Funcionando  
✅ Envio de email: Funcionando  

### Teste no PythonAnywhere
Após configurar as variáveis de ambiente:
1. Acesse o sistema
2. Faça um teste de orçamento
3. Verifique se o email é enviado

## 📝 Logs de Erro Comuns

### Erro: "SMTPAuthenticationError"
- Verifique se a senha do app está correta
- Certifique-se de que a autenticação de 2 fatores está ativada

### Erro: "SMTPConnectError"
- Tente usar a porta 465 com SSL
- Verifique se o PythonAnywhere não está bloqueando a conexão

### Erro: "Connection timeout"
- Verifique se as variáveis de ambiente estão configuradas corretamente
- Tente reiniciar o aplicativo

## 🎯 Resultado Esperado
Após a configuração, o sistema deve:
- ✅ Enviar emails de orçamento automaticamente
- ✅ Funcionar tanto para usuários logados quanto para convites
- ✅ Mostrar mensagens de sucesso no frontend

## 📞 Suporte
Se ainda houver problemas após seguir este guia:
1. Verifique os logs de erro no PythonAnywhere
2. Teste com a configuração alternativa (porta 465)
3. Entre em contato para suporte adicional
