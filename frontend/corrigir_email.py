#!/usr/bin/env python3
"""
Script para corrigir problemas de configuração de email
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail, Message
import mysql.connector

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)

# Configurações de email (mesmas do app.py)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ogordogamer2@gmail.com'
app.config['MAIL_PASSWORD'] = 'ylmu lcyn khlp ckpd'

mail = Mail(app)

def get_db_connection():
    """Conecta ao banco de dados MySQL"""
    try:
        port_para_conectar = int(os.getenv('DB_PORT', 3306))

        if not all([os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_HOST')]):
            print("ERRO DE CONFIGURAÇÃO: Variáveis de ambiente não definidas.")
            return None

        conn = mysql.connector.connect(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=port_para_conectar
        )
        return conn
    except mysql.connector.Error as e:
        print(f"ERRO DE CONEXÃO COM O MYSQL: {e}")
        return None

def verificar_emails_empresas():
    """Verifica se as empresas têm emails configurados"""
    print("\n=== VERIFICANDO EMAILS DAS EMPRESAS ===")

    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return

    try:
        cursor = conn.cursor(dictionary=True)

        # Busca todas as empresas
        cursor.execute("SELECT id, nome_empresa, email_contato_principal FROM empresas")
        empresas = cursor.fetchall()

        print(f"Encontradas {len(empresas)} empresas:")

        empresas_sem_email = []
        for empresa in empresas:
            print(f"- {empresa['nome_empresa']} (ID: {empresa['id']})")
            if not empresa['email_contato_principal']:
                empresas_sem_email.append(empresa)
                print(f"  ❌ SEM EMAIL CONFIGURADO")
            else:
                print(f"  ✓ Email: {empresa['email_contato_principal']}")

        if empresas_sem_email:
            print(f"\n⚠️  {len(empresas_sem_email)} empresas sem email configurado!")
            return empresas_sem_email
        else:
            print("\n✅ Todas as empresas têm email configurado!")
            return []

    except Exception as e:
        print(f"Erro ao verificar empresas: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def corrigir_emails_empresas(empresas_sem_email):
    """Corrige emails de empresas que não têm email configurado"""
    if not empresas_sem_email:
        print("Nenhuma empresa precisa de correção.")
        return

    print(f"\n=== CORRIGINDO EMAILS DE {len(empresas_sem_email)} EMPRESAS ===")

    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return

    try:
        cursor = conn.cursor(dictionary=True)

        for empresa in empresas_sem_email:
            print(f"\nCorrigindo empresa: {empresa['nome_empresa']}")

            # Define um email padrão
            email_padrao = 'alfredo_gi@hotmail.com'

            # Atualiza o email da empresa
            cursor.execute(
                "UPDATE empresas SET email_contato_principal = %s WHERE id = %s",
                (email_padrao, empresa['id'])
            )

            print(f"  ✓ Email atualizado para: {email_padrao}")

        conn.commit()
        print(f"\n✅ {len(empresas_sem_email)} empresas corrigidas!")

    except Exception as e:
        print(f"Erro ao corrigir emails: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

def testar_envio_email():
    """Testa o envio de email"""
    try:
        print("\n=== TESTE DE ENVIO DE EMAIL ===")

        with app.app_context():
            msg = Message(
                subject="Teste de Email - Correção Sistema iPhone",
                sender=('Sistema de Correção', app.config['MAIL_USERNAME']),
                recipients=['alfredo_gi@hotmail.com']
            )
            msg.body = """
            Este é um email de teste após correção do sistema.

            Se você receber este email, significa que o problema foi resolvido.
            """

            print("Tentando enviar email...")
            mail.send(msg)
            print("✅ Email enviado com sucesso!")
            return True

    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def main():
    """Função principal"""
    print("=== CORREÇÃO DE PROBLEMAS DE EMAIL ===")

    # 1. Verifica emails das empresas
    empresas_sem_email = verificar_emails_empresas()

    # 2. Corrige emails se necessário
    if empresas_sem_email:
        corrigir_emails_empresas(empresas_sem_email)

    # 3. Testa envio de email
    if testar_envio_email():
        print("\n🎉 Correção concluída com sucesso!")
        print("\n=== PRÓXIMOS PASSOS ===")
        print("1. Teste a funcionalidade de orçamento no sistema")
        print("2. Verifique se os emails estão sendo enviados")
        print("3. Se ainda houver problemas, verifique os logs do servidor")
    else:
        print("\n⚠️  Problema de email não resolvido!")
        print("\n=== POSSÍVEIS CAUSAS ===")
        print("1. Senha do Gmail incorreta")
        print("2. App Password não configurado")
        print("3. Autenticação de 2 fatores não habilitada")
        print("4. Firewall bloqueando porta 587")
        print("5. Problemas de rede no PythonAnywhere")

if __name__ == '__main__':
    main()