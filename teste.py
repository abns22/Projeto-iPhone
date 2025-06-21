import sqlite3

# Conecta ao banco de dados
conexao = sqlite3.connect("banco.db")
cursor = conexao.cursor()

# Consulta para listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Recupera e imprime os resultados
tabelas = cursor.fetchall()
print("Tabelas encontradas no banco:")
for tabela in tabelas:
    print(tabela[0])

conexao.close()