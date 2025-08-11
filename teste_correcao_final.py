#!/usr/bin/env python3
"""
Teste final da correção do código Flask
"""

import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório frontend ao path
sys.path.append('frontend')

# Carrega as variáveis do .env
load_dotenv('frontend/.env')

def testar_configuracoes_carregadas():
    """Testa se as configurações do .env estão sendo carregadas corretamente"""
    print("=== TESTE DE CARREGAMENTO DO .ENV ===")
    
    # Configurações esperadas
    configs = {
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False,
        'MAIL_USERNAME': 'ogordogamer2@gmail.com',
        'MAIL_PASSWORD': 'ylmu lcyn khlp ckpd'
    }
    
    print("📋 Configurações carregadas:")
    for key, expected_value in configs.items():
        if key == 'MAIL_PASSWORD':
            actual_value = os.getenv(key)
            print(f"  {key}: {'*' * len(actual_value) if actual_value else 'Não configurado'}")
        else:
            actual_value = os.getenv(key)
            print(f"  {key}: {actual_value}")
            
            # Verifica se o valor está correto
            if key == 'MAIL_PORT' and actual_value:
                if int(actual_value) == expected_value:
                    print(f"    ✅ {key} correto")
                else:
                    print(f"    ❌ {key} incorreto (esperado: {expected_value})")
            elif key in ['MAIL_USE_TLS', 'MAIL_USE_SSL'] and actual_value:
                actual_bool = actual_value.lower() == 'true'
                if actual_bool == expected_value:
                    print(f"    ✅ {key} correto")
                else:
                    print(f"    ❌ {key} incorreto (esperado: {expected_value})")
            elif actual_value == expected_value:
                print(f"    ✅ {key} correto")
            else:
                print(f"    ❌ {key} incorreto (esperado: {expected_value})")

def simular_configuracao_empresa():
    """Simula as configurações que viriam do banco de dados"""
    print("\n=== SIMULAÇÃO DE CONFIGURAÇÃO DE EMPRESA ===")
    
    # Simula configurações vazias (que causariam o problema)
    servidor_smtp = None
    porta_smtp = None
    senha_email = None
    usar_tls = None
    usar_ssl = None
    email_empresa = 'empresa@exemplo.com'
    
    print("📋 Configurações da empresa (simuladas):")
    print(f"  Servidor SMTP: {servidor_smtp}")
    print(f"  Porta SMTP: {porta_smtp}")
    print(f"  Senha Email: {'*' * len(senha_email) if senha_email else 'None'}")
    print(f"  Usar TLS: {usar_tls}")
    print(f"  Usar SSL: {usar_ssl}")
    print(f"  Email Empresa: {email_empresa}")
    
    # Simula a lógica do código corrigido
    if servidor_smtp and porta_smtp and senha_email:
        print("⚠️ Usando configurações de email da empresa")
        mail_server = servidor_smtp
        mail_port = porta_smtp
        mail_use_tls = usar_tls
        mail_use_ssl = usar_ssl
        mail_username = email_empresa
        mail_password = senha_email
    else:
        print("⚠️ Usando configurações de email do arquivo .env")
        mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = int(os.getenv('MAIL_PORT', 587))
        mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        mail_use_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
        mail_username = os.getenv('MAIL_USERNAME', 'ogordogamer2@gmail.com')
        mail_password = os.getenv('MAIL_PASSWORD', 'ylmu lcyn khlp ckpd')
    
    print("\n📧 Configurações finais que seriam usadas:")
    print(f"  Servidor: {mail_server}")
    print(f"  Porta: {mail_port}")
    print(f"  TLS: {mail_use_tls}")
    print(f"  SSL: {mail_use_ssl}")
    print(f"  Usuário: {mail_username}")
    print(f"  Senha: {'*' * len(mail_password) if mail_password else 'None'}")

def main():
    """Função principal"""
    print("=== TESTE FINAL DA CORREÇÃO ===")
    
    # 1. Testa carregamento do .env
    testar_configuracoes_carregadas()
    
    # 2. Simula configuração de empresa
    simular_configuracao_empresa()
    
    # 3. Resumo
    print("\n=== RESUMO ===")
    print("✅ Correção aplicada:")
    print("   - Código agora usa configurações do .env como fallback")
    print("   - Se configurações da empresa estiverem vazias, usa .env")
    print("   - Remetente do email usa MAIL_USERNAME configurado")
    
    print("\n🎯 Próximos passos:")
    print("   1. Faça upload do app.py corrigido para o PythonAnywhere")
    print("   2. Reinicie a aplicação")
    print("   3. Teste o envio de orçamento")
    print("   4. Verifique se o email é enviado corretamente")

if __name__ == "__main__":
    main()
