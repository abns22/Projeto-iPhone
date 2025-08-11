# Guia para Resolver Problema de Email no PythonAnywhere

## 📋 Passos para Executar no PythonAnywhere

### 1. **Acesse o Console do PythonAnywhere**

1. Faça login no PythonAnywhere
2. Vá para "Consoles" no menu lateral
3. Clique em "Bash" para abrir um console
4. Navegue até o diretório do seu projeto:
   ```bash
   cd ~/projeto-iphone/frontend
   ```

### 2. **Faça Upload dos Scripts de Teste**

Você pode copiar e colar os scripts diretamente no console ou usar o editor de arquivos do PythonAnywhere.

**Opção A - Usando o Editor:**
1. Vá para "Files" no menu lateral
2. Navegue até `~/projeto-iphone/frontend/`
3. Crie os arquivos:
   - `diagnostico_pythonanywhere.py`
   - `teste_pythonanywhere_email.py`
   - `teste_configuracoes_alternativas.py`

**Opção B - Usando o Console:**
```bash
# Crie os arquivos diretamente
nano diagnostico_pythonanywhere.py
# Cole o conteúdo e salve (Ctrl+X, Y, Enter)

nano teste_pythonanywhere_email.py
# Cole o conteúdo e salve

nano teste_configuracoes_alternativas.py
# Cole o conteúdo e salve
```

### 3. **Execute os Testes em Ordem**

#### **Teste 1 - Diagnóstico Geral**
```bash
python diagnostico_pythonanywhere.py
```

**O que este teste faz:**
- Verifica se está no ambiente PythonAnywhere
- Testa resolução DNS para smtp.gmail.com
- Testa conexão TCP na porta 587
- Testa SMTP básico e completo
- Testa portas alternativas (465, 2525, 25)

#### **Teste 2 - Email com Configurações Atuais**
```bash
python teste_pythonanywhere_email.py
```

**O que este teste faz:**
- Usa as configurações exatas do seu `.env`
- Tenta enviar um email real
- Se falhar, testa portas alternativas automaticamente

#### **Teste 3 - Configurações Alternativas**
```bash
python teste_configuracoes_alternativas.py
```

**O que este teste faz:**
- Testa 6 configurações diferentes de SMTP
- Gmail com TLS (587), SSL (465), TLS alternativo (2525)
- Outlook com TLS (587) e SSL (465)
- Identifica qual configuração funciona

### 4. **Interpretação dos Resultados**

#### **Se o Teste 1 falhar no DNS:**
```
❌ DNS FALHOU - smtp.gmail.com: [Errno -2] Name or service not known
```
**Solução:** Problema de rede do PythonAnywhere - contate o suporte

#### **Se o Teste 1 falhar no TCP:**
```
❌ TCP FALHOU - smtp.gmail.com:587 (código: 101)
```
**Solução:** Porta bloqueada - tente porta 465 ou 2525

#### **Se o Teste 1 falhar no SMTP:**
```
❌ SMTP básico FALHOU - smtp.gmail.com:587: [Errno 101] Network is unreachable
```
**Solução:** Restrição de firewall - tente configurações alternativas

#### **Se o Teste 2 funcionar:**
```
✅ Email enviado com sucesso!
```
**Solução:** O problema está no código Flask, não na conectividade

#### **Se o Teste 3 encontrar uma configuração que funciona:**
```
✅ Gmail SSL funcionando!
```
**Solução:** Atualize o `.env` com as configurações que funcionaram

### 5. **Atualizar Configurações (Se Necessário)**

Se algum teste encontrar uma configuração que funciona, atualize o `.env`:

#### **Para Gmail SSL (Porta 465):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=ogordogamer2@gmail.com
MAIL_PASSWORD=ylmu lcyn khlp ckpd
```

#### **Para Gmail TLS Alternativo (Porta 2525):**
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=2525
MAIL_USE_SSL=False
MAIL_USE_TLS=True
MAIL_USERNAME=ogordogamer2@gmail.com
MAIL_PASSWORD=ylmu lcyn khlp ckpd
```

### 6. **Reiniciar a Aplicação**

Após atualizar o `.env`:
1. Vá para "Web" no menu lateral
2. Clique em "Reload" na sua aplicação
3. Teste o envio de orçamento novamente

### 7. **Se Nenhuma Configuração Funcionar**

#### **Opção A - Contatar Suporte PythonAnywhere**
Envie um ticket com:
- Logs dos testes executados
- Configurações do `.env` (sem senhas)
- Descrição do problema
- Plano atual (gratuito/pago)

#### **Opção B - Usar Serviço de Email Alternativo**
Configure um serviço como:
- SendGrid
- Mailgun
- Amazon SES
- Outlook/Hotmail

#### **Opção C - Upgrade do Plano**
O plano gratuito pode ter restrições. Considere upgrade para:
- Hacker Plan ($5/mês)
- Developer Plan ($12/mês)

### 8. **Comandos Úteis no Console**

```bash
# Verificar se está no PythonAnywhere
echo $HOME

# Verificar variáveis de ambiente
env | grep MAIL

# Testar conectividade básica
ping smtp.gmail.com

# Verificar logs da aplicação
tail -f ~/logs/user/error.log

# Verificar status da aplicação web
ls -la ~/webapps/
```

### 9. **Verificação Final**

Após aplicar as correções:
1. Execute um orçamento de teste
2. Verifique se o email foi enviado
3. Confirme se não há mais erro 500
4. Teste com diferentes empresas

## 🎯 Resultado Esperado

Com os testes e correções, você deve conseguir:
- ✅ Enviar emails do PythonAnywhere
- ✅ Não ter mais erro `[Errno 101] Network is unreachable`
- ✅ Sistema funcionando completamente

## 📞 Suporte

Se precisar de ajuda adicional:
1. Execute todos os testes
2. Cole os resultados completos
3. Descreva qual passo falhou
4. Inclua logs de erro se houver
