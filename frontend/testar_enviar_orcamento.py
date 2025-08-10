#!/usr/bin/env python3
"""
Script para testar a função enviar_orcamento e identificar o erro 500
"""

import os
import sys
import json

# Adicionar o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def testar_enviar_orcamento():
    """
    Testa a função enviar_orcamento com dados simulados
    """
    try:
        from app import app, get_db_connection
        
        print("✅ Módulos importados com sucesso")
        
        # Testar conexão com banco
        print("\n🔄 Testando conexão com banco de dados...")
        conn = get_db_connection()
        if conn:
            print("✅ Conexão com banco estabelecida")
            conn.close()
        else:
            print("❌ Falha na conexão com banco")
            return
        
        # Verificar se a coluna modelo_interesse existe
        print("\n🔄 Verificando estrutura da tabela...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DESCRIBE avaliacoes_concluidas")
        colunas = cursor.fetchall()
        
        print("📋 Colunas da tabela avaliacoes_concluidas:")
        for coluna in colunas:
            print(f"  - {coluna[0]}: {coluna[1]}")
        
        # Verificar se modelo_interesse existe
        colunas_nomes = [coluna[0] for coluna in colunas]
        if 'modelo_interesse' in colunas_nomes:
            print("✅ Coluna modelo_interesse existe")
        else:
            print("❌ Coluna modelo_interesse NÃO existe")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Teste concluído com sucesso!")
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Testando função enviar_orcamento...")
    print("=" * 50)
    testar_enviar_orcamento()
    print("=" * 50)
    print("Teste concluído!")
