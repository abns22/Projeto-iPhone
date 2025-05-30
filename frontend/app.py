from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        conn = sqlite3.connect('frontend/banco.db')
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

if __name__ == '__main__':
    app.run(debug=True)