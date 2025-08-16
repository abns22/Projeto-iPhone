#!/usr/bin/env python3
"""
Script para adicionar a coluna modelo_interesse à tabela links_convidados
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Cria conexão com o banco de dados."""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'iphone_breakdown')
    )

def verificar_coluna_existe(cursor, tabela, coluna):
    """Verifica se uma coluna existe na tabela."""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = %s 
        AND COLUMN_NAME = %s
    """, (tabela, coluna))
    return cursor.fetchone()[0] > 0

def adicionar_coluna_modelo_interesse():
    """Adiciona a coluna modelo_interesse à tabela links_convidados se ela não existir."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        if verificar_coluna_existe(cursor, 'links_convidados', 'modelo_interesse'):
            print("✅ Coluna 'modelo_interesse' já existe na tabela links_convidados")
            return
        
        # Adiciona a coluna
        print("🔄 Adicionando coluna 'modelo_interesse' à tabela links_convidados...")
        cursor.execute("""
            ALTER TABLE links_convidados 
            ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente
        """)
        conn.commit()
        print("✅ Coluna 'modelo_interesse' adicionada com sucesso!")
        
    except mysql.connector.Error as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("🔧 Adicionando coluna modelo_interesse à tabela links_convidados...")
    adicionar_coluna_modelo_interesse()
    print("✅ Processo concluído!")
