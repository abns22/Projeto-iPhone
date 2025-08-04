import sqlite3

NOME_BANCO_DE_DADOS = 'frontend/banco.db'
NAME_TABELA_PARA_INSPECIONAR = 'usuarios'

def mostrar_informacoes_colunas():
    conexao = None

    try: 
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()

        comando_sql = f"PRAGMA table_info({NAME_TABELA_PARA_INSPECIONAR})"

        print(f"Consultando informações da tabela '{NAME_TABELA_PARA_INSPECIONAR} com o comando: {comando_sql}")
        cursor.execute(comando_sql)

        colunas_info = cursor.fetchall()

        if colunas_info:
            print(f"\n--- Informações das Colunas da Tabela '{NAME_TABELA_PARA_INSPECIONAR}' ---")
            # Imprime o cabeçalho para clareza
            print(f"{'ID':<5} {'Nome':<20} {'Tipo':<10} {'Not Null?':<10} {'Default':<10} {'PK?':<5}")
            print("-" * 70)
            for coluna in colunas_info:
                cid, nome, tipo, not_null, default_val, pk = coluna
                print(f"{cid:<5} {nome:<20} {tipo:<10} {str(bool(not_null)):<10} {str(default_val):<10} {str(bool(pk)):<5}")

            # Verificação específica pela coluna 'senha_hash'
            nomes_das_colunas = [col[1] for col in colunas_info] # Pega todos os nomes de coluna
            if 'senha_hash' in nomes_das_colunas:
                print(f"\n[SUCESSO] A coluna 'senha_hash' FOI encontrada na tabela '{NAME_TABELA_PARA_INSPECIONAR}'.")
            else:
                print(f"\n[ATENÇÃO] A coluna 'senha_hash' NÃO foi encontrada.")
                if 'senha' in nomes_das_colunas:
                    print(f"          A coluna 'senha' AINDA existe.")
                else:
                    print(f"          A coluna 'senha' também NÃO foi encontrada.")
        else:
            print(f"Nenhuma informação encontrada para a tabela '{NAME_TABELA_PARA_INSPECIONAR}'. Verifique se o nome da tabela está correto.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro do SQLite ao tentar inspecionar a tabela: {e}")

    finally:
        # 5. Feche a conexão
        if conexao:
            conexao.close()
            print("\nConexão com o banco de dados fechada.")

# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    mostrar_informacoes_colunas()