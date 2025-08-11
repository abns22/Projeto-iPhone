#!/usr/bin/env python3
"""
Teste específico de email para PythonAnywhere
Usa as configurações corretas do .env
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

def testar_email_pythonanywhere():
    """Testa envio de email usando configurações do PythonAnywhere"""
    
    print("=== TESTE DE EMAIL PYTHONANYWHERE ===")
    
    # Configurações do .env
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_username = os.getenv('MAIL_USERNAME', 'ogordogamer2@gmail.com')
    mail_password = os.getenv('MAIL_PASSWORD', 'ylmu lcyn khlp ckpd')
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    
    print(f"📧 Configurações:")
    print(f"  Servidor: {mail_server}")
    print(f"  Porta: {mail_port}")
    print(f"  Usuário: {mail_username}")
    print(f"  TLS: {mail_use_tls}")
    print(f"  SSL: {mail_use_ssl}")
    
    try:
        print(f"\n🔌 Conectando ao servidor SMTP...")
        
        # Cria contexto SSL
        context = ssl.create_default_context()
        
        # Conecta ao servidor
        if mail_use_ssl:
            print(f"Usando SSL na porta {mail_port}")
            server = smtplib.SMTP_SSL(mail_server, mail_port, context=context, timeout=30)
        else:
            print(f"Usando TLS na porta {mail_port}")
            server = smtplib.SMTP(mail_server, mail_port, timeout=30)
            if mail_use_tls:
                server.starttls(context=context)
        
        print("✅ Conexão SMTP estabelecida")
        
        # Autentica
        print(f"🔐 Autenticando...")
        server.login(mail_username, mail_password)
        print("✅ Autenticação bem-sucedida")
        
        # Prepara mensagem de teste
        msg = MIMEMultipart()
        msg['From'] = mail_username
        msg['To'] = 'alfredo_gi@hotmail.com'  # Email de teste
        msg['Subject'] = 'Teste PythonAnywhere - Sistema iPhone'
        
        body = """
        Este é um email de teste do sistema PythonAnywhere.
        
        Se você receber este email, significa que:
        1. A conectividade SMTP está funcionando
        2. As credenciais estão corretas
        3. O PythonAnywhere permite envio de emails
        
        Data/Hora: {}
        """.format(os.popen('date').read().strip())
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Envia o email
        print(f"📤 Enviando email de teste...")
        server.send_message(msg)
        print("✅ Email enviado com sucesso!")
        
        # Fecha conexão
        server.quit()
        print("✅ Conexão fechada")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ ERRO DE AUTENTICAÇÃO: {e}")
        print("💡 Verifique se o App Password está correto")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print("💡 Verifique se a porta e servidor estão corretos")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ DESTINATÁRIO RECUSADO: {e}")
        print("💡 Verifique o email de destino")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ SERVIDOR DESCONECTADO: {e}")
        print("💡 Problema de conectividade com o servidor")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ ERRO SMTP: {e}")
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def testar_portas_alternativas():
    """Testa portas SMTP alternativas no PythonAnywhere"""
    print("\n=== TESTE DE PORTAS ALTERNATIVAS ===")
    
    mail_server = 'smtp.gmail.com'
    mail_username = 'ogordogamer2@gmail.com'
    mail_password = 'ylmu lcyn khlp ckpd'
    
    # Portas para testar
    portas_config = [
        {'porta': 587, 'ssl': False, 'tls': True, 'nome': 'TLS'},
        {'porta': 465, 'ssl': True, 'tls': False, 'nome': 'SSL'},
        {'porta': 2525, 'ssl': False, 'tls': True, 'nome': 'TLS Alternativo'}
    ]
    
    for config in portas_config:
        print(f"\n🔌 Testando porta {config['porta']} ({config['nome']})...")
        
        try:
            context = ssl.create_default_context()
            
            if config['ssl']:
                server = smtplib.SMTP_SSL(mail_server, config['porta'], context=context, timeout=10)
            else:
                server = smtplib.SMTP(mail_server, config['porta'], timeout=10)
                if config['tls']:
                    server.starttls(context=context)
            
            server.login(mail_username, mail_password)
            print(f"✅ Porta {config['porta']} funcionando!")
            server.quit()
            
        except Exception as e:
            print(f"❌ Porta {config['porta']} falhou: {e}")

def verificar_ambiente_pythonanywhere():
    """Verifica se estamos no ambiente PythonAnywhere"""
    print("=== VERIFICAÇÃO DO AMBIENTE ===")
    
    # Verifica variáveis de ambiente
    username = os.getenv('USER')
    home = os.getenv('HOME')
    pwd = os.getcwd()
    
    print(f"👤 Usuário: {username}")
    print(f"🏠 Home: {home}")
    print(f"📁 Diretório atual: {pwd}")
    
    # Verifica se é PythonAnywhere
    if 'pythonanywhere' in str(home).lower() or 'pythonanywhere' in str(pwd).lower():
        print("✅ Ambiente PythonAnywhere detectado")
        return True
    else:
        print("⚠️ Ambiente local detectado")
        return False

def main():
    """Função principal"""
    print("=== DIAGNÓSTICO COMPLETO PYTHONANYWHERE ===")
    
    # 1. Verifica ambiente
    is_pythonanywhere = verificar_ambiente_pythonanywhere()
    
    # 2. Testa email principal
    print("\n" + "="*50)
    sucesso = testar_email_pythonanywhere()
    
    # 3. Se falhou, testa portas alternativas
    if not sucesso:
        testar_portas_alternativas()
    
    # 4. Resumo final
    print("\n" + "="*50)
    print("=== RESUMO FINAL ===")
    
    if sucesso:
        print("🎉 EMAIL FUNCIONANDO!")
        print("✅ O problema não é de conectividade SMTP")
        print("💡 Verifique o código da aplicação Flask")
    else:
        print("❌ EMAIL NÃO FUNCIONANDO")
        print("🔧 Possíveis soluções:")
        print("   1. Verificar App Password do Gmail")
        print("   2. Tentar porta 465 (SSL) em vez de 587 (TLS)")
        print("   3. Verificar restrições de firewall do PythonAnywhere")
        print("   4. Contatar suporte do PythonAnywhere")

if __name__ == "__main__":
    main()
