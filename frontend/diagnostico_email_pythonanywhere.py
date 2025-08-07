#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir problemas de email no PythonAnywhere
"""

import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def testar_conexao_smtp():
    """Testa a conexão SMTP com diferentes configurações"""
    print("=== DIAGNÓSTICO DE EMAIL PARA PYTHONANYWHERE ===\n")
    
    # Configurações do Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = 'ogordogamer2@gmail.com'
    password = 'ylmu lcyn khlp ckpd'
    
    print(f"🔍 Testando conexão SMTP...")
    print(f"Servidor: {smtp_server}")
    print(f"Porta: {smtp_port}")
    print(f"Usuário: {username}")
    
    try:
        # Teste 1: Conexão básica
        print("\n1️⃣ Testando conexão básica...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        print("✅ Conexão SMTP estabelecida com sucesso!")
        
        # Teste 2: Autenticação
        print("\n2️⃣ Testando autenticação...")
        server.login(username, password)
        print("✅ Autenticação realizada com sucesso!")
        
        # Teste 3: Envio de email de teste
        print("\n3️⃣ Testando envio de email...")
        
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = 'alfredo_gi@hotmail.com'
        msg['Subject'] = 'Teste PythonAnywhere - Sistema iPhone'
        
        body = """
        Este é um email de teste do sistema iPhone no PythonAnywhere.
        
        Se você receber este email, significa que a configuração está funcionando.
        
        Configurações testadas:
        - Servidor: smtp.gmail.com
        - Porta: 587
        - TLS: Habilitado
        - Autenticação: OAuth2/App Password
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        text = msg.as_string()
        server.sendmail(username, 'alfredo_gi@hotmail.com', text)
        print("✅ Email de teste enviado com sucesso!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erro de autenticação: {e}")
        print("\n💡 SOLUÇÕES POSSÍVEIS:")
        print("1. Verifique se a senha do app está correta")
        print("2. Certifique-se de que a autenticação de 2 fatores está ativada")
        print("3. Gere uma nova senha de app no Google")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ Erro de conexão: {e}")
        print("\n💡 SOLUÇÕES POSSÍVEIS:")
        print("1. Verifique se a porta 587 não está bloqueada")
        print("2. PythonAnywhere pode ter restrições de rede")
        print("3. Tente usar porta 465 com SSL")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def testar_configuracoes_alternativas():
    """Testa configurações alternativas para PythonAnywhere"""
    print("\n=== TESTANDO CONFIGURAÇÕES ALTERNATIVAS ===")
    
    # Configuração alternativa 1: Porta 465 com SSL
    print("\n🔄 Testando porta 465 com SSL...")
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
        server.login('ogordogamer2@gmail.com', 'ylmu lcyn khlp ckpd')
        print("✅ Porta 465 com SSL funciona!")
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Porta 465 falhou: {e}")
    
    return False

def verificar_variaveis_ambiente():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print("\n=== VERIFICANDO VARIÁVEIS DE AMBIENTE ===")
    
    variaveis = [
        'MAIL_SERVER',
        'MAIL_PORT', 
        'MAIL_USE_TLS',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    for var in variaveis:
        valor = os.getenv(var)
        if valor:
            print(f"✅ {var}: {valor}")
        else:
            print(f"❌ {var}: Não definida")
    
    print("\n💡 RECOMENDAÇÃO:")
    print("Configure as variáveis de ambiente no PythonAnywhere:")
    print("- Vá em 'Web' > 'Code' > 'Environment variables'")
    print("- Adicione as variáveis MAIL_* com os valores corretos")

def gerar_configuracao_pythonanywhere():
    """Gera configuração específica para PythonAnywhere"""
    print("\n=== CONFIGURAÇÃO PARA PYTHONANYWHERE ===")
    
    config = """
# Configuração recomendada para PythonAnywhere
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ogordogamer2@gmail.com'
app.config['MAIL_PASSWORD'] = 'ylmu lcyn khlp ckpd'

# Configuração alternativa se a porta 587 falhar
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USE_TLS'] = False
"""
    
    print(config)
    
    print("📝 PASSOS PARA CONFIGURAR NO PYTHONANYWHERE:")
    print("1. Acesse o painel do PythonAnywhere")
    print("2. Vá em 'Web' > 'Code' > 'Environment variables'")
    print("3. Adicione as seguintes variáveis:")
    print("   MAIL_SERVER=smtp.gmail.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USE_TLS=True")
    print("   MAIL_USERNAME=ogordogamer2@gmail.com")
    print("   MAIL_PASSWORD=ylmu lcyn khlp ckpd")
    print("4. Salve e reinicie o aplicativo")

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO DE EMAIL PARA PYTHONANYWHERE")
    print("=" * 50)
    
    # 1. Verificar variáveis de ambiente
    verificar_variaveis_ambiente()
    
    # 2. Testar conexão SMTP
    sucesso_smtp = testar_conexao_smtp()
    
    # 3. Se falhar, testar configurações alternativas
    if not sucesso_smtp:
        sucesso_alternativo = testar_configuracoes_alternativas()
        if sucesso_alternativo:
            print("\n✅ CONFIGURAÇÃO ALTERNATIVA FUNCIONA!")
            print("Use a porta 465 com SSL no PythonAnywhere")
    
    # 4. Gerar configuração recomendada
    gerar_configuracao_pythonanywhere()
    
    print("\n" + "=" * 50)
    if sucesso_smtp:
        print("🎉 PROBLEMA RESOLVIDO! Email funcionando corretamente.")
    else:
        print("⚠️  PROBLEMA DETECTADO! Siga as recomendações acima.")

if __name__ == "__main__":
    main()
