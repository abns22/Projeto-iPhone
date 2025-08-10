#!/usr/bin/env python3
"""
Script para testar se o problema do valor_base foi corrigido
"""

import mysql.connector
import os

def get_db_connection():
    """Cria conexão com o banco de dados"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'alfredo22$default'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'alfredo22$default')
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def test_valor_base_query():
    """Testa a query que estava causando erro"""
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Testa a query corrigida
        print("🔍 Testando query corrigida...")
        cursor.execute("SELECT valor_base_novo FROM modelos_iphone WHERE id = 1")
        resultado = cursor.fetchone()
        
        if resultado:
            print(f"✅ Query funcionou! valor_base_novo = {resultado['valor_base_novo']}")
            return True
        else:
            print("⚠️ Query retornou nenhum resultado (modelo ID 1 não encontrado)")
            return True
            
    except mysql.connector.Error as e:
        print(f"❌ Erro na query: {e}")
        return False
    finally:
        if conn:
            conn.close()

def test_old_query():
    """Testa a query antiga que causava erro"""
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Testa a query antiga (deve falhar)
        print("🔍 Testando query antiga (deve falhar)...")
        cursor.execute("SELECT valor_base FROM modelos_iphone WHERE id = 1")
        resultado = cursor.fetchone()
        
        print("❌ Query antiga funcionou (não deveria)")
        return False
            
    except mysql.connector.Error as e:
        print(f"✅ Query antiga falhou como esperado: {e}")
        return True
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🧪 Testando correção do problema valor_base")
    print("=" * 50)
    
    # Testa a query corrigida
    success1 = test_valor_base_query()
    
    # Testa a query antiga
    success2 = test_old_query()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ Teste passou! O problema foi corrigido.")
        print("📝 A query agora usa 'valor_base_novo' em vez de 'valor_base'")
    else:
        print("❌ Teste falhou! Verifique o problema.")
