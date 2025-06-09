from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from flask_mail import Mail, Message

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'banco.db')

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'abns22.gemi@gmail.com' 
app.config['MAIL_PASSWORD'] = 'fouz wqzk qsju zjpn'    

mail = Mail(app)

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
        print(f"Email recebido do form: '{email}'") 

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
        return redirect(url_for('login'))

    conn = None
    modelos = []
    dados_usuario_logado = None 

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        
        id_usuario = session['user_id']
        cursor.execute("SELECT nome_completo, telefone FROM usuarios WHERE id = ?", (id_usuario,))
        dados_usuario_logado = cursor.fetchone() 
        
        
        
        cursor.execute("SELECT * FROM modelos_iphone ORDER BY id") 
        modelos = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Erro ao buscar dados na rota /calcular: {e}")
    finally:
        if conn:
            conn.close()

    
    return render_template('calcular.html', modelos=modelos, usuario=dados_usuario_logado)

@app.route('/api/modelo/<int:modelo_id>/opcoes')
def get_opcoes_modelo(modelo_id):
    if 'user_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401
    
   
    opcoes = {
        "modelo_info": None, 
        "cores": [],
        "armazenamentos": []
    }
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        sql_modelo = "SELECT nome_modelo, valor_base FROM modelos_iphone WHERE id = ?"
        cursor.execute(sql_modelo, (modelo_id,))
        modelo_info_row = cursor.fetchone()
        if modelo_info_row:
            
            opcoes['modelo_info'] = dict(modelo_info_row)
       

        sql_cores = """
            SELECT c.id, c.nome_cor, c.codigo_hex, mc.imagem_url 
            FROM cores c
            JOIN modelos_cores mc ON c.id = mc.cor_id
            WHERE mc.modelo_id = ?
        """
        cursor.execute(sql_cores, (modelo_id,))
        for row in cursor.fetchall():
            opcoes["cores"].append(dict(row))

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

@app.route('/api/enviar-orcamento', methods=['POST'])
def enviar_orcamento():
    if 'user_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    dados = request.json
    nome_usuario = session.get('nome_completo', 'Não informado')
    email_usuario = session.get('username', 'Não informado')

    try:
        corpo_email = f"""
        Novo Orçamento Recebido!
        -------------------------
        Cliente: {nome_usuario}
        E-mail do Cliente: {email_usuario}

        Detalhes do Aparelho:
        - Modelo: {dados.get('modelo')}
        - Detalhes: {dados.get('detalhes')}
        - IMEI: {dados.get('imei')}

        Diagnóstico:
        """
        for item in dados.get('resumo', []):
            corpo_email += f"- {item['pergunta']}: {item['resposta']}\n"
        
        corpo_email += f"""
        -------------------------
        VALOR FINAL ESTIMADO: R$ {dados.get('valor')}
        """

        msg = Message(
            subject=f"Novo Orçamento de Avaliação para {dados.get('modelo')}",
            sender=('Nome da Sua Empresa', app.config['MAIL_USERNAME']),
            recipients=['alfredo_gi@hotmail.com']
        )
        msg.body = corpo_email
        mail.send(msg)
        
        return jsonify({"mensagem": "Orçamento enviado com sucesso para a nossa equipe!"})

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({"mensagem": "Falha ao enviar o e-mail."}), 500

@app.route('/api/modelo/<int:modelo_id>/perguntas')
def get_perguntas_modelo(modelo_id):

    if 'user_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    perguntas_com_impacto = []
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        
        sql = """
            SELECT 
                p.id as pergunta_id, 
                p.texto_pergunta,
                ir.resposta_que_gera_impacto,
                ir.valor_do_impacto
            FROM perguntas_avaliacao p
            JOIN impacto_respostas ir ON p.id = ir.pergunta_id
            WHERE ir.modelo_id = ?
        """
        cursor.execute(sql, (modelo_id,))
        for row in cursor.fetchall():
            perguntas_com_impacto.append(dict(row))

    except sqlite3.Error as e:
        print(f"Erro ao buscar perguntas para o modelo {modelo_id}: {e}")
        return jsonify({"erro": "Erro no servidor"}), 500
    finally:
        if conn:
            conn.close()

   
    return jsonify(perguntas_com_impacto)

if __name__ == '__main__':
    app.run(debug=True)