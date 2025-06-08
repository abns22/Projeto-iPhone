from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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
        usuario_form = request.form['usuario'].strip().lower()
        senha_form = request.form['senha']
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            sql_query = "SELECT id, senha_hash, nome_completo, is_admin FROM usuarios WHERE usuario = ?"
            cursor.execute(sql_query, (usuario_form,))
            registro_usuario_db = cursor.fetchone() 

            if registro_usuario_db:
                id_do_usuario_logado = registro_usuario_db[0]
                hash_armazenado = registro_usuario_db[1]
                nome_completo_do_usuario = registro_usuario_db[2]
                status_admin_do_usuario = bool(registro_usuario_db[3])

                if check_password_hash(hash_armazenado, senha_form):
                    session['user_id'] = id_do_usuario_logado
                    session['username'] = usuario_form
                    session['nome_completo'] = nome_completo_do_usuario
                    session['is_admin'] = status_admin_do_usuario
                    return redirect(url_for('avaliador'))
                else:
                    return render_template('index.html', erro='Usuário ou senha inválidos')
            else:
                erro = 'Usuário ou senha inválidos.'
        except sqlite3.Error as e_db:
            erro = "Ocorreu um erro ao processar sua solicitação."
        finally:
            if conn:
                conn.close()
        return render_template('index.html', erro=erro)

    return render_template('index.html')

@app.route('/valor')
def avaliador():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.')
        return redirect(url_for('login'))
    id_do_usuario_logado = session['user_id']
    nome_do_usuario = session.get('username', 'Usuário Desconhecido')
    print(f"Usuário {nome_do_usuario} (ID: {id_do_usuario_logado}) acessou /valor")
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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/calcular')
def calcular():
    if 'user_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    conn = None
    modelos = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT id, nome_modelo, imagem_padrao_url FROM modelos_iphone ORDER BY id")
        modelos = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Erro ao buscar modelos na rota /calcular: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('calcular.html', modelos=modelos)

@app.route('/api/modelo/<int:modelo_id>/opcoes')
def get_opcoes_modelo(modelo_id):

    if 'user_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401
    
    opcoes = {
        "cores": [],
        "armazenamentos": []
    }
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Buscar cores para o modelo_id
        sql_cores = """
            SELECT c.id, c.nome_cor, c.codigo_hex, mc.imagem_url 
            FROM cores c
            JOIN modelos_cores mc ON c.id = mc.cor_id
            WHERE mc.modelo_id = ?
        """
        cursor.execute(sql_cores, (modelo_id,))
        for row in cursor.fetchall():
            opcoes["cores"].append(dict(row))

        # Buscar armazenamentos para o modelo_id
        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = ?
        """
        cursor.execute(sql_armazenamentos, (modelo_id,))
        for row in cursor.fetchall():
            opcoes["armazenamentos"].append(dict(row))

    except sqlite3.Error as e:
        print(f"Erro ao buscar opções: {e}")
        return jsonify({"erro": "Erro no servidor"}), 500
    finally:
        if conn:
            conn.close()
    
    return jsonify(opcoes)

if __name__ == '__main__':
    app.run(debug=True)