#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import mysql.connector
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Criar conexão com o banco de dados"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_configuracao_email(empresa_id):
    """Verificar qual configuração de email será usada para uma empresa específica"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Buscar configurações da empresa
        cursor.execute("""
            SELECT email_empresa, senha_email_empresa, servidor_smtp, porta_smtp, 
                   usar_tls, usar_ssl, nome_empresa
            FROM empresas WHERE id = %s
        """, (empresa_id,))
        
        config_email = cursor.fetchone()
        
        if not config_email:
            print(f"❌ Empresa ID {empresa_id} não encontrada")
            return
        
        email_empresa, senha_email, servidor_smtp, porta_smtp, usar_tls, usar_ssl, nome_empresa = config_email
        
        print(f"🏢 Empresa: {nome_empresa} (ID: {empresa_id})")
        print("=" * 60)
        print(f"Email da empresa: {email_empresa}")
        print(f"Senha do email: {'***' if senha_email else 'Não definida'}")
        print(f"Servidor SMTP: {servidor_smtp}")
        print(f"Porta SMTP: {porta_smtp}")
        print(f"Usar TLS: {usar_tls}")
        print(f"Usar SSL: {usar_ssl}")
        print()
        
        # Verificar se as configurações estão completas
        configuracoes_completas = servidor_smtp and porta_smtp and senha_email
        
        if configuracoes_completas:
            print("✅ Configurações da empresa estão completas")
            print("📧 O sistema usará:")
            print(f"   - Remetente: {email_empresa}")
            print(f"   - Servidor: {servidor_smtp}")
            print(f"   - Porta: {porta_smtp}")
            print(f"   - TLS: {usar_tls}")
            print(f"   - SSL: {usar_ssl}")
        else:
            print("⚠️ Configurações da empresa estão incompletas")
            print("📧 O sistema usará fallback do .env:")
            print(f"   - Remetente: {os.getenv('MAIL_USERNAME', 'ogordogamer2@gmail.com')}")
            print(f"   - Servidor: {os.getenv('MAIL_SERVER', 'smtp.gmail.com')}")
            print(f"   - Porta: {os.getenv('MAIL_PORT', '587')}")
            print(f"   - TLS: {os.getenv('MAIL_USE_TLS', 'True')}")
            print(f"   - SSL: {os.getenv('MAIL_USE_SSL', 'False')}")
        
        print()
        print("🔧 Para corrigir:")
        if not configuracoes_completas:
            print("1. Acesse o painel super-admin")
            print("2. Edite a empresa")
            print("3. Configure:")
            print("   - Email da Empresa: obaoba.center@outlook.com")
            print("   - Senha do Email: [senha do outlook]")
            print("   - Servidor SMTP: smtp-mail.outlook.com")
            print("   - Porta SMTP: 587")
            print("   - Usar TLS: Sim")
            print("   - Usar SSL: Não")
        
    except Exception as e:
        print(f"❌ Erro ao consultar empresa: {e}")
    finally:
        cursor.close()
        conn.close()

def listar_todas_empresas():
    """Listar todas as empresas para identificar o ID correto"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nome_empresa FROM empresas ORDER BY id")
        empresas = cursor.fetchall()
        
        print("📋 Empresas cadastradas:")
        print("=" * 40)
        for empresa_id, nome in empresas:
            print(f"ID: {empresa_id} - {nome}")
        
    except Exception as e:
        print(f"❌ Erro ao listar empresas: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔍 Verificando configurações de email...")
    print()
    
    # Listar todas as empresas primeiro
    listar_todas_empresas()
    print()
    
    # Verificar empresa específica (substitua pelo ID correto)
    empresa_id = input("Digite o ID da empresa para verificar (ou Enter para sair): ")
    
    if empresa_id.strip():
        try:
            verificar_configuracao_email(int(empresa_id))
        except ValueError:
            print("❌ ID inválido")
