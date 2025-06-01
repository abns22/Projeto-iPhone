import sqlite3

NOME_BANCO_DE_DADOS = 'frontend/banco.db'
NOME_TABELA = 'usuarios'
NOME_ANTIGO_COLUNA = 'senha'
NOME_NOVO_COLUNA = 'senha_hash'
COLUNA_NOME = 'nome_completo'
COLUNA_TELEFONE = 'telefone'
COLUNA_ADMIN = "is_admin"

def renomear_coluna_no_banco():
    conexao = None
    try:
        conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
        cursor = conexao.cursor()

        comando_sql = f"ALTER TABLE usuarios ADD COLUMN is_admin INTEGER DEFAULT 0;"

        print(f"Tentando executar: {comando_sql}")
        cursor.execute(comando_sql)

        conexao.commit()
        print(f"Coluna '{COLUNA_ADMIN}'adicionada com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro do SQLite ao tentar renomear a coluna: {e}")
        print("Possíveis causas:")
        print("- A coluna antiga não existe ou já foi renomeada.")
        print("- A nova coluna já existe.")
        print("- Sua versão do SQLite pode ser muito antiga e não suportar RENAME COLUMN diretamente.")
        if conexao:
            conexao.rollback()

    finally:
        if conexao:
            conexao.close()
            print("Conexao com o banco de dados fechada!")

if __name__ == '__main__':
    print("ATENÇÃO: Este script alterará a estrutura do seu banco de dados.")
    print(f"Ele tentará renomear a coluna '{NOME_ANTIGO_COLUNA}' para '{NOME_NOVO_COLUNA}' na tabela '{NOME_TABELA}'.")

    confirmacao = input("Você fez um backup do seu arquivo 'banco.db'? (sim/não): ")

    if confirmacao.lower() == 'sim':
        renomear_coluna_no_banco()
    else:
        print("Operação cancelada. Por favor, faça um backup do seu banco de dados antes de executar este script.")