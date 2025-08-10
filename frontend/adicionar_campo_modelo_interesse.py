#!/usr/bin/env python3
"""
Script para adicionar o campo modelo_interesse à tabela avaliacoes_concluidas
"""

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Estabelece e retorna uma nova conexão com o banco de dados MySQL.
    """
    try:
        # Verificar se estamos no Railway (tem DATABASE_URL)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Configuração para Railway
            import urllib.parse
            url = urllib.parse.urlparse(database_url)
            
            conn_args = {
                'database': url.path[1:],  # Remove a barra inicial
                'user': url.username,
                'password': url.password,
                'host': url.hostname,
                'port': url.port or 3306,
                'autocommit': True
            }
        else:
            # Configuração para PythonAnywhere ou local
            db_host = os.getenv('DB_HOST')
            db_user = os.getenv('DB_USER')
            db_name = os.getenv('DB_NAME')
            if not all([db_host, db_user, db_name]):
                raise ValueError("Variáveis de ambiente do banco de dados (DB_HOST, DB_USER, DB_NAME) não estão configuradas para ambiente não-Railway.")

            conn_args = {
                'database': db_name,
                'user': db_user,
                'password': os.getenv('DB_PASS'), # DB_PASS pode ser vazio para conexões locais
                'host': db_host,
                'port': int(os.getenv('DB_PORT', 3306)), # Porta padrão 3306 se não especificada
                'autocommit': True
            }

        conn = mysql.connector.connect(**conn_args)
        return conn

    except mysql.connector.Error as e:
        print(f"ERRO DE CONEXÃO COM O MYSQL: {e}")
        return None
    except Exception as e:
        print(f"ERRO GERAL DE CONEXÃO: {e}")
        return None

def adicionar_campo_modelo_interesse():
    """
    Adiciona o campo modelo_interesse à tabela avaliacoes_concluidas se ele não existir.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Não foi possível conectar ao banco de dados")
            return False

        cursor = conn.cursor()

        # Verificar se o campo já existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'avaliacoes_concluidas' 
            AND COLUMN_NAME = 'modelo_interesse'
        """)
        
        campo_existe = cursor.fetchone()
        
        if campo_existe:
            print("✅ Campo 'modelo_interesse' já existe na tabela avaliacoes_concluidas")
            return True
        
        # Adicionar o campo se não existir
        print("🔄 Adicionando campo 'modelo_interesse' à tabela avaliacoes_concluidas...")
        
        cursor.execute("""
            ALTER TABLE avaliacoes_concluidas 
            ADD COLUMN modelo_interesse VARCHAR(255) AFTER telefone_cliente_final
        """)
        
        print("✅ Campo 'modelo_interesse' adicionado com sucesso!")
        return True

    except mysql.connector.Error as e:
        print(f"❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("Iniciando adição do campo modelo_interesse...")
    sucesso = adicionar_campo_modelo_interesse()
    if sucesso:
        print("✅ Processo concluído com sucesso!")
    else:
        print("❌ Processo falhou!")
