import sqlite3

NOME_BANCO = 'frontend/banco.db'
NOME_TABELA = 'usuarios'
NOME_COLUNA = 'senha_hash'
hash_gerado = "scrypt:32768:8:1$z8uH1Htfm6iaT6Lk$469aefb9878ce11cab8a9ca89ddba2075e53be98b9da115f42148b0325532995650556a9854d9bfca0484d33ad2bdef0c94021718ebc76e13f0a58a3c0242c69"
usuario_alvo = "admin"

def colocar_senha_hash():
    conexao = None
    try:
        conexao = sqlite3.connect(NOME_BANCO)
        cursor = conexao.cursor()

        comando_sql = f"UPDATE {NOME_TABELA} SET {NOME_COLUNA} = ? WHERE usuario = ?"
        print(f"Tentando executar: {comando_sql}")
        cursor.execute(comando_sql, (hash_gerado, usuario_alvo))

        conexao.commit()
        print(f"Coluna {NOME_COLUNA} do usuario {usuario_alvo} alterada (ou tentativa de alteracao.")
        if cursor.rowcount > 0:
            print(f"{cursor.rowcount} linha(s) foram atualizadas com sucesso.")
        else:
            print(f"Nenhuma linha foi atualizada. Verifique se o usuario {usuario_alvo} existe.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro do SQLite: {e}")
        if conexao:
            conexao.rollback()
    finally:
        if conexao:
            conexao.close()

if __name__ == '__main__':
    colocar_senha_hash()
