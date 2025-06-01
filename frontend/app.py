from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'banco.db')

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        sql_query = "SELECT senha_hash FROM usuarios WHERE usuario = ?"
        cursor.execute(sql_query, (usuario_form,))
        registro_usuario_db = cursor.fetchone() 

        if registro_usuario_db:
            hash_armazenado = registro_usuario_db[0]
            if check_password_hash(hash_armazenado, senha_form):
                return redirect(url_for('avaliador'))
            else:
                conn.close()
                return render_template('index.html', erro='Usuário ou senha inválidos')
        else:
            erro = 'Usuário ou senha inválidos.'
        conn.close()

        return render_template('index.html', erro=erro)

    return render_template('index.html')

@app.route('/valor')
def avaliador():
    return render_template('valor.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['usuario'].strip().lower()
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar-senha']
        telefone = request.form['telefone']
        nome_completo = request.form['nome-usuario']

        print(f"--- Novo Cadastro Tentativa ---")
        print(f"Email recebido do form: '{email}'") # Veja se tem espaços ou caixa diferente

        erro = None

        if not email or not senha or not confirmar_senha or not nome_completo or not telefone:
            erro = "Todos os campos obrigatórios devem ser preenchidos."
        elif senha != confirmar_senha:
            erro = "As senhas nao coincidem."
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (email,))
            usuario_existente = cursor.fetchone()
            print(f"Resultado da busca por email existente (usuario_existente): {usuario_existente}")
            if usuario_existente:
                erro = f"O e-mail {email} já está cadastrado."
                print(f"DEBUG: Dentro do 'if usuario_existente'. 'erro' foi definido como: '{erro}'")
            conn.close()
        print(f"DEBUG: Antes de verificar 'if erro:'. Valor atual de 'erro': '{erro}'")
        if erro: 
            print(f"DEBUG: Condição 'if erro:' é VERDADEIRA. Renderizando com erro.")
            return render_template('cadastro.html', erro=erro)
        else: 
            print(f"DEBUG: Condição 'if erro:' é FALSA. Prosseguindo para inserir novo usuário.")
            hash_da_senha = generate_password_hash(senha)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (usuario, senha_hash, nome_completo, telefone, is_admin) VALUES (?, ?, ?, ?, ?)",
                               (email, hash_da_senha, nome_completo, telefone, 0))
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                return render_template('cadastro.html', erro="Ocorreu um erro ao realizar o cadastro, tente novamente.")
            finally:
                conn.close()

            return redirect(url_for('login'))
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)