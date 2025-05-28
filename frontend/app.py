from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for('avaliador'))
        else:
            return render_template('index.html', erro='Usuário ou senha inválidos')

    return render_template('index.html')

@app.route('/valor')
def avaliador():
    return render_template('valor.html')

if __name__ == '__main__':
    app.run(debug=True)