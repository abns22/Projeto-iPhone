#!/usr/bin/env python3
"""
Script de teste para verificar se os modificadores de armazenamento estão funcionando corretamente.
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        # Configuração para Railway
        database_url = "mysql://root:HLckQmDnUoUFvhvOPJvychUWgBeOGnzt@mysql.railway.internal:3306/railway"
        
        import urllib.parse
        url = urllib.parse.urlparse(database_url)
        
        conn_args = {
            'database': url.path[1:],
            'user': url.username,
            'password': url.password,
            'host': url.hostname,
            'port': url.port or 3306,
            'autocommit': True
        }

        conn = mysql.connector.connect(**conn_args)
        return conn

    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
        return None

def testar_modificadores():
    """Testa se os modificadores de armazenamento estão sendo aplicados corretamente"""
    conn = get_db_connection()
    if not conn:
        print("❌ Não foi possível conectar ao banco de dados")
        return

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar um modelo com modificadores
        sql = """
            SELECT 
                m.id as modelo_id,
                m.nome_modelo,
                m.valor_base_novo,
                a.capacidade_gb,
                ma.modificador_valor
            FROM modelos_iphone m
            JOIN modelos_armazenamentos ma ON m.id = ma.modelo_id
            JOIN armazenamentos a ON ma.armazenamento_id = a.id
            WHERE ma.modificador_valor IS NOT NULL AND ma.modificador_valor != 0
            LIMIT 5
        """
        
        cursor.execute(sql)
        resultados = cursor.fetchall()
        
        if not resultados:
            print("❌ Nenhum modificador de armazenamento encontrado no banco de dados")
            return
        
        print("✅ Modificadores encontrados:")
        print("-" * 60)
        
        for resultado in resultados:
            modelo_id = resultado['modelo_id']
            nome_modelo = resultado['nome_modelo']
            valor_base = resultado['valor_base_novo']
            capacidade = resultado['capacidade_gb']
            modificador = resultado['modificador_valor']
            valor_final = valor_base + modificador
            
            print(f"Modelo: {nome_modelo}")
            print(f"Valor Base: R$ {valor_base:.2f}")
            print(f"Armazenamento: {capacidade} GB")
            print(f"Modificador: {modificador:+.2f}")
            print(f"Valor Final: R$ {valor_final:.2f}")
            print("-" * 60)
        
        # Testar a API de opções
        print("\n🔍 Testando API de opções...")
        
        # Buscar um modelo específico
        cursor.execute("SELECT id FROM modelos_iphone LIMIT 1")
        modelo = cursor.fetchone()
        
        if modelo:
            modelo_id = modelo['id']
            print(f"Testando modelo ID: {modelo_id}")
            
            # Simular a consulta da API
            sql_opcoes = """
                SELECT 
                    m.nome_modelo, m.valor_base_novo,
                    a.id as armazenamento_id,
                    a.capacidade_gb,
                    ma.modificador_valor
                FROM modelos_iphone m
                JOIN modelos_armazenamentos ma ON m.id = ma.modelo_id
                JOIN armazenamentos a ON ma.armazenamento_id = a.id
                WHERE m.id = %s
                ORDER BY a.capacidade_gb
            """
            
            cursor.execute(sql_opcoes, (modelo_id,))
            opcoes = cursor.fetchall()
            
            if opcoes:
                print("✅ Opções encontradas:")
                for opcao in opcoes:
                    print(f"  - {opcao['capacidade_gb']} GB: modificador {opcao['modificador_valor']:+.2f}")
            else:
                print("❌ Nenhuma opção encontrada")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("🧪 Testando sistema de modificadores de armazenamento...")
    testar_modificadores()
    print("\n✅ Teste concluído!")
