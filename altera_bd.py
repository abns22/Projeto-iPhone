import sqlite3

NOME_BANCO_DE_DADOS = 'frontend/banco.db'
NOME_TABELA = 'usuarios'
NOME_ANTIGO_COLUNA = 'senha'
NOME_NOVO_COLUNA = 'senha_hash'
COLUNA_NOME = 'nome_completo'
COLUNA_TELEFONE = 'telefone'
COLUNA_ADMIN = "is_admin"
EMAIL_USUARIO = "ogordogamer2@gmail.com"
NOVO_STATUS = ''

def renomear_coluna_no_banco():
    conexao = None
    conexao = sqlite3.connect(NOME_BANCO_DE_DADOS)
    cursor = conexao.cursor()

    comando_sql = f"UPDATE usuarios SET is_admin = ? WHERE usuario = ?"

    cursor.execute(comando_sql, (NOVO_STATUS, EMAIL_USUARIO)) 
