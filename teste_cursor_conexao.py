#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para diagnosticar o problema "Cursor is not connected" (2055)
"""

import os
import sys
import mysql.connector
from datetime import datetime

# Adicionar o diretório frontend ao path
sys.path.append('frontend')

def test_db_connection():
    """Testa a conexão com o banco de dados"""
    print("=== TESTE DE CONEXÃO COM BANCO DE DADOS ===")
    
    try:
        # Importar a função get_db_connection do app.py
        from app import get_db_connection
        
        # Testar conexão
        conn = get_db_connection()
        if conn is None:
            print("❌ Falha ao estabelecer conexão com o banco")
            return False
            
        print("✅ Conexão estabelecida com sucesso")
        
        # Testar cursor
        cursor = conn.cursor()
        print("✅ Cursor criado com sucesso")
        
        # Testar query simples
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Query de teste executada: {result}")
        
        # Fechar cursor e conexão
        cursor.close()
        conn.close()
        print("✅ Conexão e cursor fechados corretamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {e}")
        return False

def test_cursor_reuse():
    """Testa o reuso de cursor após fechamento"""
    print("\n=== TESTE DE REUSO DE CURSOR ===")
    
    try:
        from app import get_db_connection
        
        # Primeira conexão
        conn1 = get_db_connection()
        cursor1 = conn1.cursor()
        
        print("✅ Primeira conexão e cursor criados")
        
        # Executar query
        cursor1.execute("SELECT 1")
        result1 = cursor1.fetchone()
        print(f"✅ Primeira query: {result1}")
        
        # Fechar cursor e conexão
        cursor1.close()
        conn1.close()
        print("✅ Primeira conexão fechada")
        
        # Segunda conexão (nova)
        conn2 = get_db_connection()
        cursor2 = conn2.cursor()
        
        print("✅ Segunda conexão e cursor criados")
        
        # Executar query
        cursor2.execute("SELECT 2")
        result2 = cursor2.fetchone()
        print(f"✅ Segunda query: {result2}")
        
        # Fechar cursor e conexão
        cursor2.close()
        conn2.close()
        print("✅ Segunda conexão fechada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de reuso: {e}")
        return False

def test_cursor_after_close():
    """Testa o que acontece ao tentar usar cursor após fechamento"""
    print("\n=== TESTE DE CURSOR APÓS FECHAMENTO ===")
    
    try:
        from app import get_db_connection
        
        # Criar conexão e cursor
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("✅ Conexão e cursor criados")
        
        # Fechar cursor
        cursor.close()
        print("✅ Cursor fechado")
        
        # Tentar usar cursor fechado
        try:
            cursor.execute("SELECT 1")
            print("❌ ERRO: Cursor funcionou após fechamento (não deveria)")
        except mysql.connector.Error as e:
            if e.errno == 2055:  # Cursor is not connected
                print("✅ Comportamento esperado: Cursor não conectado após fechamento")
            else:
                print(f"❌ Erro inesperado: {e}")
        
        # Fechar conexão
        conn.close()
        print("✅ Conexão fechada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_connection_timeout():
    """Testa timeout de conexão"""
    print("\n=== TESTE DE TIMEOUT DE CONEXÃO ===")
    
    try:
        from app import get_db_connection
        
        # Criar conexão
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("✅ Conexão criada")
        
        # Simular tempo de espera (se possível)
        print("⏳ Aguardando 5 segundos...")
        import time
        time.sleep(5)
        
        # Tentar usar cursor após espera
        try:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Cursor ainda funciona após espera: {result}")
        except mysql.connector.Error as e:
            if e.errno == 2055:
                print("❌ Cursor desconectado após timeout")
            else:
                print(f"❌ Erro inesperado: {e}")
        
        # Fechar conexão
        cursor.close()
        conn.close()
        print("✅ Conexão fechada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de timeout: {e}")
        return False

def test_multiple_connections():
    """Testa múltiplas conexões simultâneas"""
    print("\n=== TESTE DE MÚLTIPLAS CONEXÕES ===")
    
    try:
        from app import get_db_connection
        
        connections = []
        cursors = []
        
        # Criar 3 conexões
        for i in range(3):
            conn = get_db_connection()
            cursor = conn.cursor()
            connections.append(conn)
            cursors.append(cursor)
            print(f"✅ Conexão {i+1} criada")
        
        # Usar todas as conexões
        for i, (conn, cursor) in enumerate(zip(connections, cursors)):
            cursor.execute(f"SELECT {i+1}")
            result = cursor.fetchone()
            print(f"✅ Query {i+1}: {result}")
        
        # Fechar todas as conexões
        for i, (conn, cursor) in enumerate(zip(connections, cursors)):
            cursor.close()
            conn.close()
            print(f"✅ Conexão {i+1} fechada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de múltiplas conexões: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO DO PROBLEMA 'CURSOR IS NOT CONNECTED' (2055)")
    print("=" * 60)
    
    # Executar todos os testes
    tests = [
        test_db_connection,
        test_cursor_reuse,
        test_cursor_after_close,
        test_connection_timeout,
        test_multiple_connections
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro ao executar teste {test.__name__}: {e}")
            results.append(False)
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✅ Todos os testes passaram - problema pode estar em outro lugar")
    else:
        print("❌ Alguns testes falharam - verificar configurações de banco")
    
    print("\n💡 POSSÍVEIS CAUSAS DO ERRO 2055:")
    print("1. Cursor fechado prematuramente")
    print("2. Conexão perdida por timeout")
    print("3. Múltiplas operações no mesmo cursor após fechamento")
    print("4. Problemas de configuração do MySQL")
    print("5. Problemas de rede/conectividade")

if __name__ == "__main__":
    main()
