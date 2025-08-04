import psycopg2
import sys

# --- INFORMAÇÕES DE CONEXÃO ---
# Substitua os valores abaixo pelos dados do seu banco de dados PostgreSQL.
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iphone_breakdown_db"
DB_USER = "alfredo"
DB_PASSWORD = "icloudbz12031994@lF"

def modificar_tabela_empresas():
    """
    Conecta-se ao banco de dados PostgreSQL e adiciona as colunas
    'cnpj' e 'nome_responsavel' à tabela 'empresas'.
    """
    conn = None  # Inicializa a variável de conexão
    try:
        # Tenta estabelecer a conexão com o banco de dados
        print("Tentando conectar ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Conexão bem-sucedida!")

        # O uso de 'with' garante que o cursor seja fechado automaticamente
        with conn.cursor() as cur:
            # --- COMANDO SQL PARA ALTERAR A TABELA ---
            # Comando 1: Adiciona a coluna 'cnpj'
            print("Adicionando a coluna 'cnpj'...")
            alter_query_cnpj = """
            ALTER TABLE empresas
            ADD COLUMN IF NOT EXISTS cnpj VARCHAR(20) UNIQUE;
            """
            cur.execute(alter_query_cnpj)
            print("Coluna 'cnpj' adicionada com sucesso ou já existente.")

            # Comando 2: Adiciona a coluna 'nome_responsavel'
            print("Adicionando a coluna 'nome_responsavel'...")
            alter_query_responsavel = """
            ALTER TABLE empresas
            ADD COLUMN IF NOT EXISTS nome_responsavel VARCHAR(255);
            """
            cur.execute(alter_query_responsavel)
            print("Coluna 'nome_responsavel' adicionada com sucesso ou já existente.")

            # Efetiva as alterações no banco de dados
            conn.commit()
            print("\nAlterações na tabela 'empresas' foram salvas com sucesso!")

    except psycopg2.OperationalError as e:
        # Erro comum quando o banco de dados está fora do ar ou as credenciais estão erradas
        print(f"Erro de conexão: {e}", file=sys.stderr)
        print("Verifique se o PostgreSQL está rodando e se as credenciais (host, porta, nome, usuário, senha) estão corretas.", file=sys.stderr)
    except psycopg2.Error as e:
        # Captura outros erros do psycopg2
        print(f"Ocorreu um erro do PostgreSQL: {e}", file=sys.stderr)
    except Exception as e:
        # Captura qualquer outro erro inesperado
        print(f"Ocorreu um erro inesperado: {e}", file=sys.stderr)
    finally:
        # Garante que a conexão seja sempre fechada, mesmo se ocorrer um erro
        if conn is not None:
            conn.close()
            print("\nConexão com o PostgreSQL foi fechada.")

if __name__ == "__main__":
    modificar_tabela_empresas()
