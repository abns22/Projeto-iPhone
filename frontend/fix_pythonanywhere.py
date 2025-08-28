#!/usr/bin/env python3
"""
Script para corrigir erro modelo_interesse no PythonAnywhere
Execute este script no Python console do PythonAnywhere
"""

import mysql.connector
import os

def fix_modelo_interesse_pythonanywhere():
    """Adiciona a coluna modelo_interesse à tabela links_convidados no PythonAnywhere."""
    
    # Configurações típicas do PythonAnywhere
    # Ajuste conforme suas configurações
    config = {
        'host': 'localhost',
        'user': os.getenv('DB_USER', 'SEU_USUARIO'),  # Substitua pelo seu usuário
        'password': os.getenv('DB_PASSWORD', 'SUA_SENHA'),  # Substitua pela sua senha
        'database': os.getenv('DB_NAME', 'SEU_BANCO_DE_DADOS')  # Substitua pelo nome do seu banco
    }
    
    print("🔧 Iniciando correção da coluna modelo_interesse...")
    print(f"📊 Conectando ao banco: {config['database']}")
    
    conn = None
    try:
        # Conecta ao banco
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
            
        print("\n🎉 Correção concluída com sucesso!")
        print("💡 Lembre-se de reiniciar sua aplicação web no PythonAnywhere")
            
    except mysql.connector.Error as e:
        print(f"❌ Erro: {e}")
        print("\n💡 Dicas para resolver:")
        print("1. Verifique se as credenciais do banco estão corretas")
        print("2. Substitua SEU_USUARIO, SUA_SENHA e SEU_BANCO_DE_DADOS pelos valores reais")
        print("3. Verifique se a tabela links_convidados existe")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("\n🔌 Conexão fechada")

# Para executar diretamente no Python console do PythonAnywhere
if __name__ == "__main__":
    fix_modelo_interesse_pythonanywhere()
else:
    # Para executar como função
    fix_modelo_interesse_pythonanywhere()

