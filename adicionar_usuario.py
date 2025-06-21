import psycopg2
from psycopg2 import sql

DB_NAME = "iphone_breakdown_db"
DB_USER = "alfredo"
DB_PASS = "icloudbz12031994@lF" 
DB_HOST = "localhost"
DB_PORT = "5432"

def adicionar_super_admin():
    """
    Insere o primeiro usuário Super Admin no banco de dados,
    associado à empresa principal (ID 1).
    """
    
    hash_da_senha = "scrypt:32768:8:1$eOcMg8AHKU2dAOke$6e3af04979bfb24cd1d947435056b76d9e5c5e0046e481d6728e60a828eb3780640b770e1595a4bf1376c8bd982ef3c1b3b38350e2cc25cbde9b853f28090efb"
    
    email_admin = "alfredo_gi@hotmail.com"
    nome_completo_admin = "Alfredo (Super Admin)" 
    telefone_admin = "41 9 98698980" 
    empresa_id_admin = 1 
    is_admin_status = True 

    if "COLE_O_HASH_COMPLETO_AQUI" in hash_da_senha or len(hash_da_senha) < 20:
        print("\nERRO: Por favor, edite o script e cole o hash gerado na variável 'hash_da_senha'.")
        return

    sql_insert_admin = """
        INSERT INTO usuarios 
        (usuario, senha_hash, nome_completo, telefone, is_admin, empresa_id) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (usuario, empresa_id) DO NOTHING;
    """

    conexao = None
    try:
        conexao = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        cursor = conexao.cursor()

        print(f"\nTentando inserir/verificar o Super Admin com e-mail: {email_admin}...")
        
        cursor.execute(sql_insert_admin, (
            email_admin, 
            hash_da_senha, 
            nome_completo_admin, 
            telefone_admin, 
            is_admin_status, 
            empresa_id_admin
        ))

        conexao.commit()

        if cursor.rowcount > 0:
            print(">>> Usuário Super Admin inserido com sucesso!")
        else:
            print(">>> Usuário Super Admin já existia no banco de dados. Nenhuma alteração feita.")

    except psycopg2.Error as e:
        print(f"Ocorreu um erro com o PostgreSQL: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            cursor.close()
            conexao.close()
            print("Conexão com o PostgreSQL fechada.")


if __name__ == '__main__':
    adicionar_super_admin()