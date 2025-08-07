#!/usr/bin/env python3
"""
Script de teste para verificar email no PythonAnywhere
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)

# Configurações de email (usando variáveis de ambiente)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'ogordogamer2@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'ylmu lcyn khlp ckpd')

mail = Mail(app)

def testar_configuracao_email():
    """Testa a configuração de email"""
    print("=== TESTE DE EMAIL PARA PYTHONANYWHERE ===")
    print(f"Servidor: {app.config['MAIL_SERVER']}")
    print(f"Porta: {app.config['MAIL_PORT']}")
    print(f"TLS: {app.config['MAIL_USE_TLS']}")
    print(f"SSL: {app.config['MAIL_USE_SSL']}")
    print(f"Usuário: {app.config['MAIL_USERNAME']}")
    print(f"Senha: {'*' * len(app.config['MAIL_PASSWORD'])}")
    
    # Verificar se as variáveis de ambiente estão sendo lidas
    print("\n=== VERIFICANDO VARIÁVEIS DE AMBIENTE ===")
    variaveis = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USE_SSL', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    
    for var in variaveis:
        valor = os.getenv(var)
        if valor:
            print(f"✅ {var}: {valor}")
        else:
            print(f"❌ {var}: Não definida (usando valor padrão)")

def testar_envio_email():
    """Testa o envio de email"""
    try:
        print("\n=== TESTANDO ENVIO DE EMAIL ===")
        
        with app.app_context():
            msg = Message(
                subject="Teste PythonAnywhere - Sistema iPhone",
                sender=('Sistema iPhone', app.config['MAIL_USERNAME']),
                recipients=['alfredo_gi@hotmail.com']
            )
            
            msg.body = f"""
            Teste de email do sistema iPhone no PythonAnywhere.
            
            Configurações utilizadas:
            - Servidor: {app.config['MAIL_SERVER']}
            - Porta: {app.config['MAIL_PORT']}
            - TLS: {app.config['MAIL_USE_TLS']}
            - SSL: {app.config['MAIL_USE_SSL']}
            
            Se você receber este email, a configuração está funcionando!
            """
            
            print("Enviando email de teste...")
            mail.send(msg)
            print("✅ Email enviado com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def gerar_relatorio():
    """Gera um relatório completo"""
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DE CONFIGURAÇÃO")
    print("=" * 50)
    
    # Testar configuração
    testar_configuracao_email()
    
    # Testar envio
    sucesso = testar_envio_email()
    
    print("\n" + "=" * 50)
    if sucesso:
        print("🎉 CONFIGURAÇÃO FUNCIONANDO!")
        print("O sistema de email está pronto para uso.")
    else:
        print("⚠️  PROBLEMA DETECTADO!")
        print("Verifique as configurações no PythonAnywhere.")
    
    print("=" * 50)

if __name__ == "__main__":
    gerar_relatorio()
