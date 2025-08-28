#!/usr/bin/env python3
"""
Script simples para adicionar a coluna modelo_interesse à tabela links_convidados
"""

import mysql.connector

def fix_modelo_interesse():
    """Adiciona a coluna modelo_interesse à tabela links_convidados."""
    
    # Configurações do banco - ajuste conforme necessário
    config = {
        'host': 'localhost',  # ou seu host
        'user': 'root',       # ou seu usuário
        'password': '',       # sua senha
        'database': 'iphone_breakdown'  # ou seu nome de banco
    }
    
    conn = None
    try:
        print("🔌 Conectando ao banco de dados...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Verifica se a coluna já existe
        print("🔍 Verificando se a coluna modelo_interesse já existe...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'links_convidados' 
            AND COLUMN_NAME = 'modelo_interesse'
        """)
        
        coluna_existe = cursor.fetchone()[0] > 0
        
        if coluna_existe:
            print("✅ Coluna 'modelo_interesse' já existe na tabela links_convidados")
        else:
            print("🔄 Adicionando coluna 'modelo_interesse' à tabela links_convidados...")
            cursor.execute("""
                ALTER TABLE links_convidados 
                ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente
            """)
            conn.commit()
            print("✅ Coluna 'modelo_interesse' adicionada com sucesso!")
        
        # Mostra a estrutura da tabela
        print("\n📋 Estrutura atual da tabela links_convidados:")
        cursor.execute("DESCRIBE links_convidados")
        colunas = cursor.fetchall()
        for coluna in colunas:
            print(f"  - {coluna[0]} ({coluna[1]})")
            
    except mysql.connector.Error as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Dicas para resolver:")
        print("1. Verifique se as credenciais do banco estão corretas")
        print("2. Verifique se o banco de dados existe")
        print("3. Verifique se a tabela links_convidados existe")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("\n🔌 Conexão fechada")

if __name__ == "__main__":
    print("🔧 Iniciando correção da coluna modelo_interesse...")
    fix_modelo_interesse()
    print("✅ Processo concluído!")

