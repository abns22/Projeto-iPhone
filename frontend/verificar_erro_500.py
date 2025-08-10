#!/usr/bin/env python3
"""
Script para verificar se a coluna modelo_interesse existe e identificar problemas
"""

import os
import sys

# Adicionar o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import get_db_connection
    print("✅ Módulo app importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulo app: {e}")
    sys.exit(1)

def verificar_coluna_modelo_interesse():
    """
    Verifica se a coluna modelo_interesse existe na tabela avaliacoes_concluidas
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Não foi possível conectar ao banco de dados")
            return False

        cursor = conn.cursor()

        # Verificar se a coluna existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'avaliacoes_concluidas' 
            AND COLUMN_NAME = 'modelo_interesse'
        """)
        
        campo_existe = cursor.fetchone()
        
        if campo_existe:
            print("✅ Campo 'modelo_interesse' existe na tabela avaliacoes_concluidas")
            return True
        else:
            print("❌ Campo 'modelo_interesse' NÃO existe na tabela avaliacoes_concluidas")
            print("🔧 Isso pode estar causando o erro 500!")
            return False

    except Exception as e:
        print(f"❌ Erro ao verificar coluna: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def verificar_estrutura_tabela():
    """
    Verifica a estrutura completa da tabela avaliacoes_concluidas
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Não foi possível conectar ao banco de dados")
            return False

        cursor = conn.cursor()

        # Verificar estrutura da tabela
        cursor.execute("DESCRIBE avaliacoes_concluidas")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura atual da tabela avaliacoes_concluidas:")
        print("=" * 60)
        for coluna in colunas:
            print(f"  {coluna[0]} - {coluna[1]}")
        print("=" * 60)
        
        return True

    except Exception as e:
        print(f"❌ Erro ao verificar estrutura da tabela: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

def adicionar_coluna_se_necessario():
    """
    Adiciona a coluna modelo_interesse se ela não existir
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Não foi possível conectar ao banco de dados")
            return False

        cursor = conn.cursor()

        # Verificar se a coluna existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'avaliacoes_concluidas' 
            AND COLUMN_NAME = 'modelo_interesse'
        """)
        
        campo_existe = cursor.fetchone()
        
        if campo_existe:
            print("✅ Campo 'modelo_interesse' já existe")
            return True
        
        # Adicionar o campo se não existir
        print("🔄 Adicionando campo 'modelo_interesse' à tabela avaliacoes_concluidas...")
        
        cursor.execute("""
            ALTER TABLE avaliacoes_concluidas 
            ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente_final
        """)
        
        print("✅ Campo 'modelo_interesse' adicionado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("🔍 Verificando problemas no banco de dados...")
    print("=" * 50)
    
    # Verificar estrutura atual
    verificar_estrutura_tabela()
    
    # Verificar se a coluna existe
    if not verificar_coluna_modelo_interesse():
        print("\n🔧 Tentando adicionar a coluna...")
        adicionar_coluna_se_necessario()
    else:
        print("\n✅ Tudo parece estar correto com a estrutura do banco")
    
    print("\n" + "=" * 50)
    print("Verificação concluída!")
