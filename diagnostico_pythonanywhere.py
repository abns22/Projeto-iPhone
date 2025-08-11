#!/usr/bin/env python3
"""
Diagnóstico específico para problemas de email no PythonAnywhere
"""

import os
import socket
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import sys

def testar_dns(hostname):
    """Testa resolução DNS"""
    try:
        print(f"🔍 Testando DNS para: {hostname}")
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS OK - {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS FALHOU - {hostname}: {e}")
        return False

def testar_conexao_tcp(hostname, porta):
    """Testa conexão TCP"""
    try:
        print(f"🔌 Testando conexão TCP: {hostname}:{porta}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, porta))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP OK - {hostname}:{porta}")
            return True
        else:
            print(f"❌ TCP FALHOU - {hostname}:{porta} (código: {result})")
            return False
    except Exception as e:
        print(f"❌ TCP ERRO - {hostname}:{porta}: {e}")
        return False

def testar_smtp_basico(hostname, porta):
    """Testa conexão SMTP básica"""
    try:
        print(f"📧 Testando SMTP básico: {hostname}:{porta}")
        server = smtplib.SMTP(hostname, porta, timeout=10)
        server.quit()
        print(f"✅ SMTP básico OK - {hostname}:{porta}")
        return True
    except Exception as e:
        print(f"❌ SMTP básico FALHOU - {hostname}:{porta}: {e}")
        return False

def testar_smtp_completo(username, password, hostname, porta):
    """Testa SMTP completo com autenticação"""
    try:
        print(f"🔐 Testando SMTP completo: {username}@{hostname}:{porta}")
        
        # Cria contexto SSL
        context = ssl.create_default_context()
        
        # Conecta ao servidor
        server = smtplib.SMTP(hostname, porta, timeout=10)
        server.starttls(context=context)
        
        # Autentica
        server.login(username, password)
        
        # Testa envio (sem realmente enviar)
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = 'teste@exemplo.com'
        msg['Subject'] = 'Teste PythonAnywhere'
        msg.attach(MIMEText('Teste de conectividade', 'plain'))
        
        # Não envia realmente, apenas testa a preparação
        print(f"✅ SMTP completo OK - Autenticação e preparação funcionando")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP AUTH FALHOU - {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP CONNECT FALHOU - {e}")
        return False
    except Exception as e:
        print(f"❌ SMTP completo FALHOU - {e}")
        return False

def verificar_configuracoes_pythonanywhere():
    """Verifica configurações específicas do PythonAnywhere"""
    print("\n=== CONFIGURAÇÕES PYTHONANYWHERE ===")
    
    # Verifica se estamos no PythonAnywhere
    username = os.getenv('USER')
    home = os.getenv('HOME')
    
    print(f"👤 Usuário: {username}")
    print(f"🏠 Home: {home}")
    
    if 'pythonanywhere' in str(home).lower():
        print("✅ Detectado ambiente PythonAnywhere")
    else:
        print("⚠️ Não detectado como PythonAnywhere")
    
    # Verifica variáveis de ambiente
    print("\n📋 Variáveis de ambiente:")
    env_vars = [
        'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 
        'MAIL_PASSWORD', 'MAIL_USE_TLS', 'MAIL_USE_SSL'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                print(f"  {var}: {'*' * len(value)}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: Não configurado")

def testar_portas_alternativas():
    """Testa portas SMTP alternativas"""
    print("\n=== TESTE DE PORTAS ALTERNATIVAS ===")
    
    portas = [587, 465, 25, 2525]
    hostname = 'smtp.gmail.com'
    
    for porta in portas:
        testar_conexao_tcp(hostname, porta)

def verificar_restricoes_pythonanywhere():
    """Verifica possíveis restrições do PythonAnywhere"""
    print("\n=== RESTRIÇÕES PYTHONANYWHERE ===")
    
    # Verifica se há arquivos de configuração específicos
    config_files = [
        '/etc/hosts',
        '/etc/resolv.conf',
        '/proc/net/tcp'
    ]
    
    for file_path in config_files:
        try:
            if os.path.exists(file_path):
                print(f"✅ {file_path} existe")
            else:
                print(f"❌ {file_path} não existe")
        except:
            print(f"❌ Não foi possível verificar {file_path}")

def main():
    """Função principal"""
    print("=== DIAGNÓSTICO PYTHONANYWHERE - EMAIL ===")
    
    # Configurações do .env
    mail_server = 'smtp.gmail.com'
    mail_port = 587
    mail_username = 'ogordogamer2@gmail.com'
    mail_password = 'ylmu lcyn khlp ckpd'
    
    # 1. Verifica configurações
    verificar_configuracoes_pythonanywhere()
    
    # 2. Testa DNS
    print("\n=== TESTE DNS ===")
    dns_ok = testar_dns(mail_server)
    
    # 3. Testa TCP
    print("\n=== TESTE TCP ===")
    tcp_ok = testar_conexao_tcp(mail_server, mail_port)
    
    # 4. Testa SMTP básico
    print("\n=== TESTE SMTP BÁSICO ===")
    smtp_basico_ok = testar_smtp_basico(mail_server, mail_port)
    
    # 5. Testa SMTP completo
    print("\n=== TESTE SMTP COMPLETO ===")
    smtp_completo_ok = testar_smtp_completo(mail_username, mail_password, mail_server, mail_port)
    
    # 6. Testa portas alternativas
    testar_portas_alternativas()
    
    # 7. Verifica restrições
    verificar_restricoes_pythonanywhere()
    
    # Resumo
    print("\n=== RESUMO ===")
    print(f"DNS: {'✅' if dns_ok else '❌'}")
    print(f"TCP: {'✅' if tcp_ok else '❌'}")
    print(f"SMTP Básico: {'✅' if smtp_basico_ok else '❌'}")
    print(f"SMTP Completo: {'✅' if smtp_completo_ok else '❌'}")
    
    if not dns_ok:
        print("\n🔧 POSSÍVEL SOLUÇÃO: Problema de DNS - verificar configurações de rede")
    elif not tcp_ok:
        print("\n🔧 POSSÍVEL SOLUÇÃO: Porta bloqueada - tentar porta 465 (SSL) ou 2525")
    elif not smtp_basico_ok:
        print("\n🔧 POSSÍVEL SOLUÇÃO: Servidor SMTP não acessível - verificar firewall")
    elif not smtp_completo_ok:
        print("\n🔧 POSSÍVEL SOLUÇÃO: Problema de autenticação - verificar App Password")
    else:
        print("\n🎉 Todos os testes passaram! O problema pode estar no código da aplicação.")

if __name__ == "__main__":
    main()
