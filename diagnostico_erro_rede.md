# Diagnóstico: Erro de Rede - Network is unreachable

## Erro Reportado

```
❌ ERRO NO ENVIO DE EMAIL
Tipo do erro: OSError
Mensagem: [Errno 101] Network is unreachable
```

## Análise do Erro

O erro `[Errno 101] Network is unreachable` indica que o sistema não consegue estabelecer conexão com o servidor SMTP. Este é um problema de conectividade de rede, não relacionado ao código da aplicação.

## Possíveis Causas

### 1. **Problemas de Internet**
- Conexão com internet instável ou interrompida
- Firewall bloqueando conexões SMTP
- Proxy ou VPN interferindo na conexão

### 2. **Configurações de Rede**
- Porta 587 bloqueada pelo provedor de internet
- Restrições de rede corporativa
- DNS não resolvendo o domínio smtp.gmail.com

### 3. **Configurações do Gmail**
- Autenticação de 2 fatores ativada sem senha de app
- Conta do Gmail com restrições de segurança
- Necessidade de "Less secure app access" (descontinuado)

### 4. **Problemas do Servidor**
- Servidor SMTP temporariamente indisponível
- Rate limiting do Gmail
- Configurações de segurança do Gmail

## Soluções Recomendadas

### 1. **Verificar Conectividade Básica**
```bash
# Testar conectividade com o Gmail
ping smtp.gmail.com

# Testar conectividade com a porta 587
telnet smtp.gmail.com 587
```

### 2. **Verificar Configurações do .env**
Certifique-se de que as configurações estão corretas:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=ogordogamer2@gmail.com
MAIL_PASSWORD=sua_senha_de_app
```

### 3. **Configurar Senha de App do Gmail**
1. Acesse https://myaccount.google.com/security
2. Ative a verificação em 2 etapas
3. Gere uma senha de app específica para a aplicação
4. Use essa senha no arquivo .env

### 4. **Testar Configurações Alternativas**
```python
# Configuração alternativa com SSL
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
```

### 5. **Verificar Firewall/Antivírus**
- Desative temporariamente firewall/antivírus para teste
- Configure exceções para a aplicação Python
- Verifique se a porta 587 está liberada

## Teste de Diagnóstico

### Script de Teste de Conectividade
```python
import socket
import smtplib

def test_smtp_connection():
    try:
        # Teste 1: Resolução DNS
        print("Testando resolução DNS...")
        socket.gethostbyname('smtp.gmail.com')
        print("✅ DNS resolvido com sucesso")
        
        # Teste 2: Conexão TCP
        print("Testando conexão TCP...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 587))
        sock.close()
        
        if result == 0:
            print("✅ Conexão TCP estabelecida")
        else:
            print("❌ Falha na conexão TCP")
            
        # Teste 3: Conexão SMTP
        print("Testando conexão SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        print("✅ Conexão SMTP estabelecida")
        server.quit()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_smtp_connection()
```

## Configurações Recomendadas para Gmail

### Opção 1: TLS (Recomendado)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=senha_de_app_gerada
```

### Opção 2: SSL
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=senha_de_app_gerada
```

## Próximos Passos

1. **Execute o script de diagnóstico** para identificar o problema específico
2. **Verifique as configurações do .env**
3. **Configure senha de app do Gmail**
4. **Teste conectividade básica**
5. **Verifique firewall/antivírus**

## Status

🔄 **EM INVESTIGAÇÃO** - Problema de conectividade de rede identificado, necessita diagnóstico específico.
