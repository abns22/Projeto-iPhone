import mysql.connector
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', 3306))

hash_da_senha = "scrypt:32768:8:1$eOcMg8AHKU2dAOke$6e3af04979bfb24cd1d947435056b76d9e5c5e0046e481d6728e60a828eb3780640b770e1595a4bf1376c8bd982ef3c1b3b38350e2cc25cbde9b853f28090efb"
email_admin = "alfredo_gi@hotmail.com"
nome_completo_admin = "admin"
telefone_admin = "41998698980"
empresa_id_admin = 1
is_admin_status = True
usuario_admin = "admin"  # ou o nome de usuário desejado

def adicionar_super_admin():
    conn = None
    try:
        conn = mysql.connector.connect(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        with conn.cursor() as cursor:
            sql_insert_admin = """
                INSERT IGNORE INTO usuarios 
                (usuario, senha_hash, nome_completo, telefone, is_admin, empresa_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert_admin, (
                usuario_admin, hash_da_senha, nome_completo_admin, telefone_admin, is_admin_status, empresa_id_admin
            ))
            conn.commit()
            print("Super admin criado com sucesso!")
    except mysql.connector.Error as e:
        print(f"Erro ao inserir super admin: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    adicionar_super_admin()