#!/usr/bin/env python3
"""
Script de diagnóstico para testar conectividade SMTP
"""

import socket
import smtplib
import os
from datetime import datetime

def test_dns_resolution():
    """Testa resolução DNS do servidor SMTP"""
    print("🔍 Teste 1: Resolução DNS")
    try:
        ip = socket.gethostbyname('smtp.gmail.com')
        print(f"✅ DNS resolvido com sucesso: smtp.gmail.com -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ Falha na resolução DNS: {e}")
        return False

def test_tcp_connection():
    """Testa conexão TCP com o servidor SMTP"""
    print("\n🔍 Teste 2: Conexão TCP")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('smtp.gmail.com', 587))
        sock.close()
        
        if result == 0:
            print("✅ Conexão TCP estabelecida na porta 587")
            return True
        else:
            print(f"❌ Falha na conexão TCP: código de erro {result}")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão TCP: {e}")
        return False

def test_smtp_connection():
    """Testa conexão SMTP básica"""
    print("\n🔍 Teste 3: Conexão SMTP")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        print("✅ Conexão SMTP inicial estabelecida")
        
        # Testar STARTTLS
        server.starttls()
        print("✅ STARTTLS ativado com sucesso")
        
        server.quit()
        print("✅ Conexão SMTP fechada corretamente")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão SMTP: {e}")
        return False

def test_smtp_authentication():
    """Testa autenticação SMTP (se credenciais estiverem disponíveis)"""
    print("\n🔍 Teste 4: Autenticação SMTP")
    
    # Verificar se as variáveis de ambiente estão configuradas
    username = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')
    
    if not username or not password:
        print("⚠️ Credenciais não encontradas no .env")
        print("   Configure MAIL_USERNAME e MAIL_PASSWORD para testar autenticação")
        return False
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        
        # Tentar login
        server.login(username, password)
        print(f"✅ Autenticação SMTP bem-sucedida para {username}")
        
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Erro de autenticação: {e}")
        print("   Verifique se a senha de app está configurada corretamente")
        return False
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False

def test_alternative_ports():
    """Testa portas alternativas"""
    print("\n🔍 Teste 5: Portas Alternativas")
    
    ports = [465, 587, 25]
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('smtp.gmail.com', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Porta {port} acessível")
            else:
                print(f"❌ Porta {port} bloqueada")
        except Exception as e:
            print(f"❌ Erro testando porta {port}: {e}")

def check_environment_variables():
    """Verifica variáveis de ambiente"""
    print("\n🔍 Teste 6: Variáveis de Ambiente")
    
    env_vars = [
        'MAIL_SERVER',
        'MAIL_PORT', 
        'MAIL_USE_TLS',
        'MAIL_USE_SSL',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mascarar senha
            if var == 'MAIL_PASSWORD':
                masked_value = '*' * len(value) if value else 'Não configurado'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Não configurado")

def main():
    """Função principal de diagnóstico"""
    print("=" * 60)
    print("DIAGNÓSTICO DE CONECTIVIDADE SMTP")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Executar testes
    tests = [
        test_dns_resolution,
        test_tcp_connection,
        test_smtp_connection,
        test_smtp_authentication,
        test_alternative_ports,
        check_environment_variables
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result if result is not None else False)
        except Exception as e:
            print(f"❌ Erro executando teste: {e}")
            results.append(False)
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes aprovados: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A conectividade SMTP está funcionando.")
    elif passed >= total - 1:
        print("⚠️ A maioria dos testes passou. Verifique as configurações.")
    else:
        print("❌ Muitos testes falharam. Verifique a conectividade de rede.")
    
    print("\n💡 RECOMENDAÇÕES:")
    if not results[0]:  # DNS
        print("- Verifique sua conexão com a internet")
        print("- Configure DNS alternativos (8.8.8.8, 1.1.1.1)")
    
    if not results[1]:  # TCP
        print("- Verifique se a porta 587 não está bloqueada")
        print("- Desative temporariamente firewall/antivírus")
    
    if not results[2]:  # SMTP
        print("- O servidor SMTP pode estar temporariamente indisponível")
        print("- Tente usar porta 465 com SSL")
    
    if not results[3]:  # Auth
        print("- Configure senha de app do Gmail")
        print("- Verifique se a verificação em 2 etapas está ativada")

if __name__ == "__main__":
    main()
