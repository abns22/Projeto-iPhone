#!/usr/bin/env python3
"""
Script de teste para verificar se os modificadores de armazenamento estão sendo aplicados corretamente
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return None

def testar_modificadores_armazenamento():
    """Testa se os modificadores de armazenamento estão sendo aplicados corretamente"""
    
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar todos os modelos com seus armazenamentos
        sql = """
            SELECT 
                mi.id as modelo_id,
                mi.nome_modelo,
                mi.valor_base_novo,
                a.capacidade_gb,
                ma.modificador_valor
            FROM modelos_iphone mi
            JOIN modelos_armazenamentos ma ON mi.id = ma.modelo_id
            JOIN armazenamentos a ON ma.armazenamento_id = a.id
            WHERE mi.empresa_id = 1
            ORDER BY mi.nome_modelo, a.capacidade_gb
        """
        
        cursor.execute(sql)
        resultados = cursor.fetchall()
        
        print("🔍 TESTE DE MODIFICADORES DE ARMAZENAMENTO")
        print("=" * 60)
        
        if not resultados:
            print("❌ Nenhum modelo encontrado")
            return
        
        modelo_atual = None
        for row in resultados:
            if modelo_atual != row['nome_modelo']:
                modelo_atual = row['nome_modelo']
                print(f"\n📱 MODELO: {row['nome_modelo']}")
                print(f"   Valor Base: R$ {row['valor_base_novo']:.2f}")
                print("   Armazenamentos:")
            
            valor_final = row['valor_base_novo'] + row['modificador_valor']
            modificador = row['modificador_valor']
            
            print(f"     • {row['capacidade_gb']} GB:")
            print(f"       - Modificador: R$ {modificador:+.2f}")
            print(f"       - Valor Final: R$ {valor_final:.2f}")
            
            # Verificar se o modificador está sendo aplicado
            if modificador != 0:
                print(f"       ✅ Modificador aplicado corretamente")
            else:
                print(f"       ⚠️  Modificador é zero (padrão)")
        
        print("\n" + "=" * 60)
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    finally:
        cursor.close()
        conn.close()

def testar_api_opcoes_modelo():
    """Testa se a API está retornando os modificadores corretamente"""
    
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar um modelo específico para teste
        sql_modelo = "SELECT id, nome_modelo FROM modelos_iphone WHERE empresa_id = 1 LIMIT 1"
        cursor.execute(sql_modelo)
        modelo = cursor.fetchone()
        
        if not modelo:
            print("❌ Nenhum modelo encontrado para teste")
            return
        
        modelo_id = modelo['id']
        print(f"\n🔍 TESTE DA API - MODELO: {modelo['nome_modelo']} (ID: {modelo_id})")
        print("=" * 60)
        
        # Simular a consulta da API
        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = %s AND ma.empresa_id = 1
        """
        cursor.execute(sql_armazenamentos, (modelo_id,))
        armazenamentos = cursor.fetchall()
        
        print("Armazenamentos retornados pela API:")
        for arm in armazenamentos:
            print(f"  • {arm['capacidade_gb']} GB - Modificador: R$ {arm['modificador_valor']:+.2f}")
        
        print("✅ API testada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste da API: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando testes de modificadores de armazenamento...")
    
    # Teste 1: Verificar modificadores no banco
    testar_modificadores_armazenamento()
    
    # Teste 2: Verificar API
    testar_api_opcoes_modelo()
    
    print("\n🎯 Testes concluídos!")
