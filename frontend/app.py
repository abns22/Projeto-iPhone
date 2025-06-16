from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import json 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'banco.db')

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'images', 'modelos')

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
            sql_query = "SELECT id, senha_hash, nome_completo, is_admin, empresa_id FROM usuarios WHERE usuario = ?"
            cursor.execute(sql_query, (usuario_form,))
            registro_usuario_db = cursor.fetchone() 

            if registro_usuario_db:
                id_do_usuario_logado = registro_usuario_db[0]
                hash_armazenado = registro_usuario_db[1]
                nome_completo_do_usuario = registro_usuario_db[2]
                status_admin_do_usuario = bool(registro_usuario_db[3])

                if check_password_hash(hash_armazenado, senha_form):
                    
                    id_do_usuario_logado = registro_usuario_db[0]
                    
                    nome_completo_do_usuario = registro_usuario_db[2]
                    status_admin_do_usuario = bool(registro_usuario_db[3])
                    id_da_empresa = registro_usuario_db[4] 

                    session['user_id'] = id_do_usuario_logado
                    session['username'] = usuario_form
                    session['nome_completo'] = nome_completo_do_usuario
                    session['is_admin'] = status_admin_do_usuario
                    session['empresa_id'] = id_da_empresa 

                    return redirect(url_for('avaliador')) 
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
    return redirect(url_for('login'))
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
    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Ocorreu um erro com sua sessão. Por favor, faça login novamente.", "danger")
        return redirect(url_for('logout'))
    
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

        cursor.execute(
            "SELECT id, nome_modelo, imagem_padrao_url FROM modelos_iphone WHERE empresa_id = ? ORDER BY id",
            (empresa_id_logada,) 
        )
        modelos = cursor.fetchall()
        
    except sqlite3.Error as e:
        print(f"Erro ao buscar dados na rota /calcular: {e}")
    finally:
        if conn:
            conn.close()

    
    return render_template('calcular.html', modelos=modelos, usuario=dados_usuario_logado)

@app.route('/api/modelo/<int:modelo_id>/opcoes')
def get_opcoes_modelo(modelo_id):
    if 'user_id' not in session or 'empresa_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401
    
    empresa_id_logada = session['empresa_id']

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

        sql_modelo = "SELECT nome_modelo, valor_base FROM modelos_iphone WHERE id = ? AND empresa_id = ?"
        cursor.execute(sql_modelo, (modelo_id, empresa_id_logada))
        modelo_info_row = cursor.fetchone()
        if not modelo_info_row:
            return jsonify({"erro": "Modelo não encontrado ou não pertence a esta empresa"}), 404
        
        opcoes['modelo_info'] = dict(modelo_info_row)

        sql_cores = """
            SELECT c.id, c.nome_cor, mc.imagem_url 
            FROM cores c
            JOIN modelos_cores mc ON c.id = mc.cor_id
            WHERE mc.modelo_id = ? AND mc.empresa_id = ? 
        """
        cursor.execute(sql_cores, (modelo_id, empresa_id_logada))
        for row in cursor.fetchall():
            opcoes["cores"].append(dict(row))

        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = ? AND ma.empresa_id = ?
        """
        cursor.execute(sql_armazenamentos, (modelo_id, empresa_id_logada))
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
    
    empresa_id_logada = session['empresa_id']
    usuario_id_logado = session['user_id']
    email_usuario_logado = session.get('username')

    conn = None
    try:
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        modelo_nome = dados.get('modelo')
        cursor.execute("SELECT id, valor_base FROM modelos_iphone WHERE nome_modelo = ? AND empresa_id = ?", (modelo_nome, empresa_id_logada))
        modelo_row = cursor.fetchone()
        
        if not modelo_row:
            return jsonify({"mensagem": "Erro: Modelo não encontrado para esta empresa."}), 400
        
        modelo_id = modelo_row['id']
        valor_base_db = modelo_row['valor_base']

        nome_cliente_final = dados.get('nomeCliente', 'Não informado')
        telefone_cliente_final = dados.get('telefoneCliente', 'Não informado')
        
        cor_selecionada = dados.get('cor', 'N/A')
        armazenamento_selecionado = dados.get('armazenamento', 'N/A')
        imei = dados.get('imei', 'N/A')
        valor_final_calculado = float(dados.get('valor', 0.0))
        resumo_json = json.dumps(dados.get('resumo', []))

        sql_insert = """
            INSERT INTO avaliacoes_concluidas (
                empresa_id, usuario_id, nome_cliente_final, email_cliente_final, telefone_cliente_final,
                modelo_iphone_id, cor_selecionada, armazenamento_selecionado, imei, 
                valor_base_calculado, valor_final_calculado, resumo_respostas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql_insert, (
            empresa_id_logada, usuario_id_logado, nome_cliente_final, email_usuario_logado, telefone_cliente_final,
            modelo_id, cor_selecionada, armazenamento_selecionado, imei,
            valor_base_db, valor_final_calculado, resumo_json
        ))
        
        conn.commit()
        print("Avaliação salva com sucesso no banco de dados.")

    except sqlite3.Error as e:
        if conn: conn.rollback()
        print(f"Erro ao salvar avaliação no banco: {e}")
        
    finally:
        if conn: conn.close()

    
    try:
        
        corpo_email = f"""
        Novo Orçamento Recebido!
        -------------------------
        Cliente: {dados.get('nomeCliente', 'Não informado')}
        E-mail do Cliente: {email_usuario_logado}
        Telefone do Cliente: {dados.get('telefoneCliente', 'Não informado')}

        Detalhes do Aparelho:
        - Modelo: {dados.get('modelo')}
        - Cor: {dados.get('cor')}
        - Armazenamento: {dados.get('armazenamento')}
        - IMEI: {dados.get('imei')}

        Diagnóstico:
        """
        for item in dados.get('resumo', []):
            if 'pergunta' in item and 'resposta' in item: 
                corpo_email += f"- {item['pergunta']}: {item['resposta']}\n"
        
        corpo_email += f"""
        -------------------------
        VALOR FINAL ESTIMADO: R$ {dados.get('valor')}
        """

        msg = Message(
            subject=f"Novo Orçamento de Avaliação para {dados.get('modelo')}",
            sender=('Sua Calculadora de iPhones', app.config['MAIL_USERNAME']),
            recipients=['alfredo_gi@hotmail.com'] 
        )
        msg.body = corpo_email
        mail.send(msg)
        
        return jsonify({"mensagem": "Orçamento enviado com sucesso para a nossa equipe e registrado!"})

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({"mensagem": "Avaliação registrada, mas falha ao enviar o e-mail."}), 500

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

@app.route('/admin/ajustes')
def ajustar_valores_admin():

    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado. Esta página é apenas para administradores.', 'danger')
        return redirect(url_for('login')) 

    empresa_id_logada = session['empresa_id']
    modelos_da_empresa = []
    is_super_admin = (empresa_id_logada == 1)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM modelos_iphone WHERE empresa_id = ? ORDER BY nome_modelo",
            (empresa_id_logada,)
        )
        modelos_da_empresa = cursor.fetchall()
        
    except sqlite3.Error as e:
        flash('Ocorreu um erro ao buscar os dados para administração.', 'danger')
        print(f"Erro ao buscar modelos para admin: {e}")
    finally:
        if conn:
            conn.close()

        return render_template('admin_ajustes.html', modelos=modelos_da_empresa, is_super_admin=is_super_admin)

@app.route('/admin/editar-modelo/<int:modelo_id>', methods=['GET', 'POST'])
def editar_modelo_admin(modelo_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado. Esta página é apenas para administradores.', 'danger')
        return redirect(url_for('login'))
    
    if session.get('empresa_id') != 1:
        flash('Ação não permitida. Apenas o administrador geral pode deletar modelos.', 'danger')
        return redirect(url_for('ajustar_valores_admin'))
    
    empresa_id_logada = session['empresa_id']
    conn = None 

    if request.method == 'POST':
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            novo_nome = request.form['nome_modelo']
            novo_valor_base = request.form['valor_base']
            cursor.execute(
                """UPDATE modelos_iphone SET nome_modelo = ?, valor_base = ?
                   WHERE id = ? AND empresa_id = ?""",
                (novo_nome, novo_valor_base, modelo_id, empresa_id_logada)
            )

            for key, value in request.form.items():
                if key.startswith('impacto_'):
                    impacto_id = int(key.split('_')[1])
                    novo_valor_impacto = value
                    
                    cursor.execute(
                        """UPDATE impacto_respostas SET valor_do_impacto = ?
                           WHERE id = ? AND empresa_id = ?""",
                        (novo_valor_impacto, impacto_id, empresa_id_logada)
                    )

            conn.commit()
            flash('Modelo e valores atualizados com sucesso!', 'success')

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            flash('Ocorreu um erro ao salvar as alterações.', 'danger')
            print(f"Erro ao atualizar no banco: {e}")
        finally:
            if conn:
                conn.close()
        
        return redirect(url_for('ajustar_valores_admin'))

    modelo_para_editar = None
    impactos_do_modelo = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM modelos_iphone WHERE id = ? AND empresa_id = ?", (modelo_id, empresa_id_logada))
        modelo_para_editar = cursor.fetchone()

        if modelo_para_editar:
            sql_impactos = """
                SELECT p.texto_pergunta, ir.id as impacto_id, ir.valor_do_impacto
                FROM impacto_respostas ir
                JOIN perguntas_avaliacao p ON ir.pergunta_id = p.id
                WHERE ir.modelo_id = ? AND ir.empresa_id = ?
                ORDER BY p.id
            """
            cursor.execute(sql_impactos, (modelo_id, empresa_id_logada))
            impactos_do_modelo = cursor.fetchall()
        
    except sqlite3.Error as e:
        flash('Erro ao buscar dados para edição.', 'danger')
        print(f"Erro ao buscar modelo/impactos para edição: {e}")
    finally:
        if conn:
            conn.close()
    
    if modelo_para_editar:
        return render_template('editar_modelo.html', modelo=modelo_para_editar, impactos=impactos_do_modelo)
    else:
        flash('Modelo não encontrado ou não pertence à sua empresa.', 'warning')
        return redirect(url_for('ajustar_valores_admin'))


@app.route('/admin/adicionar-modelo', methods=['GET', 'POST'])
def adicionar_modelo_admin():
   
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        empresa_id_logada = session['empresa_id']
        nome_modelo = request.form['nome_modelo']
        valor_base = request.form['valor_base']

        imagem_arquivo = request.files.get('imagem_modelo')
        imagem_url_para_db = None 

        if imagem_arquivo and imagem_arquivo.filename != '':
            filename = secure_filename(imagem_arquivo.filename)
        
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            caminho_para_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            imagem_arquivo.save(caminho_para_salvar)
            
            imagem_url_para_db = f'images/modelos/{filename}'
        else:
            imagem_url_para_db = 'images/placeholder.png'

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO modelos_iphone (nome_modelo, valor_base, empresa_id, imagem_padrao_url)
                   VALUES (?, ?, ?, ?)""",
                (nome_modelo, valor_base, empresa_id_logada, imagem_url_para_db)
            )

            id_novo_modelo = cursor.lastrowid
            cursor.execute("SELECT id FROM perguntas_avaliacao")
            todas_as_perguntas = cursor.fetchall()

            for pergunta in todas_as_perguntas:
                pergunta_id = pergunta[0]
                cursor.execute("INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (?, ?, ?, ?, ?)",
                               (id_novo_modelo, pergunta_id, 'Sim', 0.00, empresa_id_logada))
                cursor.execute("INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (?, ?, ?, ?, ?)",
                               (id_novo_modelo, pergunta_id, 'Não', 0.00, empresa_id_logada))

            conn.commit()
            flash(f'Modelo "{nome_modelo}" adicionado com sucesso!', 'success')
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            flash('Erro ao adicionar o novo modelo.', 'danger')
            print(f"Erro ao adicionar modelo: {e}")
        finally:
            if conn:
                conn.close()

        return redirect(url_for('ajustar_valores_admin'))

    return render_template('adicionar_modelo.html')


@app.route('/admin/deletar-modelo/<int:modelo_id>', methods=['POST'])
def deletar_modelo_admin(modelo_id):
    
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    
    if session.get('empresa_id') != 1:
        flash('Ação não permitida. Apenas o administrador geral pode deletar modelos.', 'danger')
        return redirect(url_for('ajustar_valores_admin'))

    empresa_id_logada = session['empresa_id']
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
      
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        print(f"Deletando dependências para o modelo ID: {modelo_id} da empresa ID: {empresa_id_logada}")
        cursor.execute("DELETE FROM impacto_respostas WHERE modelo_id = ? AND empresa_id = ?", (modelo_id, empresa_id_logada))
        cursor.execute("DELETE FROM modelos_cores WHERE modelo_id = ? AND empresa_id = ?", (modelo_id, empresa_id_logada))
        cursor.execute("DELETE FROM modelos_armazenamentos WHERE modelo_id = ? AND empresa_id = ?", (modelo_id, empresa_id_logada))
        
        print(f"Deletando o modelo principal ID: {modelo_id}")
        cursor.execute("DELETE FROM modelos_iphone WHERE id = ? AND empresa_id = ?", (modelo_id, empresa_id_logada))
        
        conn.commit()
        flash('Modelo deletado com sucesso.', 'success')

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        flash('Erro ao deletar o modelo.', 'danger')
        print(f"Erro ao deletar modelo: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('ajustar_valores_admin'))

if __name__ == '__main__':
    app.run(debug=True)


