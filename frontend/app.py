from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from flask_mail import Mail
from flask import jsonify

load_dotenv()
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
SECRET_KEY = os.getenv('SECRET_KEY')

app.secret_key = SECRET_KEY

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'images')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'abns22.gemi@gmail.com'
app.config['MAIL_PASSWORD'] = 'fouz wqzk qsju zjpn'

mail = Mail(app)

def get_db_connection():
    """
    Estabelece e retorna uma nova conexão com o banco de dados.
    Esta função garante que as variáveis de ambiente sejam lidas no momento certo.
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except psycopg2.OperationalError as e:

        print(f"ERRO DE CONEXÃO COM O BANCO DE DADOS: {e}")

        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        conn = None
        usuario_form = request.form['usuario'].strip().lower()
        senha_form = request.form['senha']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            sql_query = "SELECT id, usuario, senha_hash, nome_completo, is_admin, empresa_id FROM usuarios WHERE usuario = %s"
            cursor.execute(sql_query, (usuario_form,))

            registro_usuario_db = cursor.fetchone() 

            if registro_usuario_db:
                
                hash_armazenado = registro_usuario_db['senha_hash']

                if check_password_hash(hash_armazenado, senha_form):
                    session['user_id'] = registro_usuario_db['id']
                    session['username'] = registro_usuario_db['usuario']
                    session['nome_completo'] = registro_usuario_db['nome_completo']
                    session['is_admin'] = registro_usuario_db['is_admin']
                    session['empresa_id'] = registro_usuario_db['empresa_id']
                    
                    return redirect(url_for('calcular'))
                else:
                    erro = 'Usuário ou senha inválidos'
            else:
                erro = 'Usuário ou senha inválidos.'

        except psycopg2.Error as e_db:
            erro = "Ocorreu um erro ao processar sua solicitação."
            print(f"Erro de PostgreSQL no login: {e_db}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        return render_template('index.html', erro=erro) 

    return render_template('index.html', erro=None)

def get_info_empresa_logada():
    """Busca no banco os dados da empresa do usuário logado."""
    if 'empresa_id' not in session:
        return None
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT nome_empresa, logo_url FROM empresas WHERE id = %s", (session['empresa_id'],))
        info_empresa = cursor.fetchone()
        return info_empresa
    except psycopg2.Error as e:
        print(f"Erro ao buscar info da empresa: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

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
        flash('Por favor, faça login para acessar o avaliador.', 'warning')
        return redirect(url_for('login'))
    info_empresa = get_info_empresa_logada()
    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Ocorreu um erro com a identificação da sua empresa. Por favor, faça login novamente.", "danger")
        return redirect(url_for('logout'))
    
    conn = None
    modelos = []
    dados_usuario_logado = None 

    try:
        
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        id_usuario = session['user_id']
        
        cursor.execute("SELECT nome_completo, telefone FROM usuarios WHERE id = %s AND empresa_id = %s", (id_usuario, empresa_id_logada))
        dados_usuario_logado = cursor.fetchone() 

        cursor.execute(
            "SELECT id, nome_modelo, imagem_padrao_url FROM modelos_iphone WHERE empresa_id = %s ORDER BY id",
            (empresa_id_logada,) 
        )
        modelos = cursor.fetchall()
        
    except psycopg2.Error as e:
        flash('Não foi possível carregar os dados da página. Tente novamente mais tarde.', 'danger')
        print(f"Erro de PostgreSQL na rota /calcular: {e}")
    finally:
        
        if conn:
            cursor.close()
            conn.close()

    return render_template('calcular.html', modelos=modelos, usuario=dados_usuario_logado, info_empresa=info_empresa)


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
        
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        sql_modelo = "SELECT nome_modelo, valor_base_novo FROM modelos_iphone WHERE id = %s AND empresa_id = %s"
        cursor.execute(sql_modelo, (modelo_id, empresa_id_logada))
        modelo_info_row = cursor.fetchone()
        
        if not modelo_info_row:
             return jsonify({"erro": "Modelo não encontrado ou não pertence a esta empresa"}), 404
        
        opcoes['modelo_info'] = modelo_info_row 

        sql_cores = """
            SELECT c.id, c.nome_cor, c.codigo_hex, mc.imagem_url 
            FROM cores c
            JOIN modelos_cores mc ON c.id = mc.cor_id
            WHERE mc.modelo_id = %s AND mc.empresa_id = %s
        """
        cursor.execute(sql_cores, (modelo_id, empresa_id_logada))
        opcoes["cores"] = cursor.fetchall()

        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = %s AND ma.empresa_id = %s
        """
        cursor.execute(sql_armazenamentos, (modelo_id, empresa_id_logada))
        opcoes["armazenamentos"] = cursor.fetchall()

    except psycopg2.Error as e:
        print(f"Erro de PostgreSQL ao buscar opções: {e}")
        return jsonify({"erro": "Erro no servidor ao buscar opções"}), 500
    finally:
        
        if conn:
            cursor.close()
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

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)


        modelo_nome = dados.get('modelo')

        cursor.execute(
            "SELECT id, valor_base_novo FROM modelos_iphone WHERE nome_modelo = %s AND empresa_id = %s",
            (modelo_nome, empresa_id_logada)
        )
        modelo_row = cursor.fetchone()
        
        if not modelo_row:
            return jsonify({"mensagem": "Erro: Modelo não encontrado para esta empresa."}), 400
        
        modelo_id = modelo_row['id']
        valor_base_db = modelo_row['valor_base_novo']

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
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (
            empresa_id_logada, usuario_id_logado, nome_cliente_final, email_usuario_logado, telefone_cliente_final,
            modelo_id, cor_selecionada, armazenamento_selecionado, imei,
            valor_base_db, valor_final_calculado, resumo_json
        ))
        
        conn.commit()
        print("Avaliação salva com sucesso no banco de dados PostgreSQL.")

    except psycopg2.Error as e:
        if conn: conn.rollback()
        print(f"Erro de PostgreSQL ao salvar avaliação: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

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

    if 'user_id' not in session or 'empresa_id' not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    empresa_id_logada = session['empresa_id']
    perguntas_com_impacto = []
    conn = None
    try:
   
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        sql = """
            SELECT 
                p.id as pergunta_id, 
                p.texto_pergunta,
                ir.resposta_que_gera_impacto,
                ir.valor_do_impacto
            FROM perguntas_avaliacao p
            JOIN impacto_respostas ir ON p.id = ir.pergunta_id
            WHERE ir.modelo_id = %s AND ir.empresa_id = %s
        """
        cursor.execute(sql, (modelo_id, empresa_id_logada))

        perguntas_com_impacto = cursor.fetchall()
            
    except psycopg2.Error as e:
        print(f"Erro de PostgreSQL ao buscar perguntas para o modelo {modelo_id}: {e}")
        return jsonify({"erro": "Erro no servidor ao buscar perguntas"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()
    
    return jsonify(perguntas_com_impacto)

@app.route('/admin/ajustes')
def gerenciar_modelos_admin():

    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado. Esta página é apenas para administradores.', 'danger')
        return redirect(url_for('login'))

    empresa_id_logada = session['empresa_id']
    is_super_admin = (empresa_id_logada == 1) 

    conn = None
    modelos_da_empresa = []
    info_empresa = None 

    try:

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)


        cursor.execute("SELECT nome_empresa, logo_url FROM empresas WHERE id = %s", (empresa_id_logada,))
        info_empresa = cursor.fetchone()
        

        cursor.execute(
            "SELECT * FROM modelos_iphone WHERE empresa_id = %s ORDER BY nome_modelo",
            (empresa_id_logada,)
        )
        modelos_da_empresa = cursor.fetchall()
        
    except psycopg2.Error as e:
        flash('Ocorreu um erro ao buscar os dados para administração.', 'danger')
        print(f"Erro de PostgreSQL ao buscar para admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    return render_template('admin_ajustes.html', 
                           modelos=modelos_da_empresa, 
                           is_super_admin=is_super_admin, 
                           info_empresa=info_empresa)

@app.route('/admin/editar-modelo/<int:modelo_id>', methods=['GET', 'POST'])
def editar_modelo_admin(modelo_id):
   
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada()
    
    empresa_id_logada = session['empresa_id']
    conn = None

    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
          
            novo_nome = request.form['nome_modelo']
            novo_valor_base = request.form['valor_base_novo']
            
            cursor.execute(
                """UPDATE modelos_iphone SET nome_modelo = %s, valor_base_novo = %s
                   WHERE id = %s AND empresa_id = %s""",
                (novo_nome, novo_valor_base, modelo_id, empresa_id_logada)
            )
           
            for key, value in request.form.items():
                if key.startswith('impacto_'):
                    impacto_id = int(key.split('_')[1])
                    novo_valor_impacto = value
                    
                    cursor.execute(
                        """UPDATE impacto_respostas SET valor_do_impacto = %s
                           WHERE id = %s AND empresa_id = %s""",
                        (novo_valor_impacto, impacto_id, empresa_id_logada)
                    )

            conn.commit()
            flash('Modelo e valores atualizados com sucesso!', 'success')

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            flash('Ocorreu um erro ao salvar as alterações.', 'danger')
            print(f"Erro de PostgreSQL ao atualizar: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        return redirect(url_for('ajustar_valores_admin'))

    modelo_para_editar = None
    impactos_do_modelo = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM modelos_iphone WHERE id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        modelo_para_editar = cursor.fetchone()

        if modelo_para_editar:
            sql_impactos = """
                SELECT p.texto_pergunta, ir.id as impacto_id, ir.valor_do_impacto
                FROM impacto_respostas ir
                JOIN perguntas_avaliacao p ON ir.pergunta_id = p.id
                WHERE ir.modelo_id = %s AND ir.empresa_id = %s
                ORDER BY p.id
            """
            cursor.execute(sql_impactos, (modelo_id, empresa_id_logada))
            impactos_do_modelo = cursor.fetchall()
        
    except psycopg2.Error as e:
        flash('Erro ao buscar dados para edição.', 'danger')
        print(f"Erro de PostgreSQL ao buscar para edição: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    
    if modelo_para_editar:
        return render_template('editar_modelo.html', modelo=modelo_para_editar, impactos=impactos_do_modelo, info_empresa=info_empresa)
    else:
        flash('Modelo não encontrado ou não pertence à sua empresa.', 'warning')
        return redirect(url_for('ajustar_valores_admin'))

@app.route('/admin/adicionar-modelo', methods=['GET', 'POST'])
def adicionar_modelo_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    empresa_id_logada = session['empresa_id']

    if request.method == 'POST':
        nome_modelo = request.form['nome_modelo']
        valor_base = request.form['valor_base']

        imagem_arquivo = request.files.get('imagem_modelo')
        imagem_url_para_db = 'images/placeholder.png'

        if imagem_arquivo and imagem_arquivo.filename != '':
            filename = secure_filename(imagem_arquivo.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            caminho_para_salvar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem_arquivo.save(caminho_para_salvar)
            imagem_url_para_db = f'images/{filename}'

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            sql_insert_modelo = """
                INSERT INTO modelos_iphone (nome_modelo, valor_base_novo, empresa_id, imagem_padrao_url)
                VALUES (%s, %s, %s, %s) RETURNING id;
            """
            cursor.execute(sql_insert_modelo, (nome_modelo, valor_base, empresa_id_logada, imagem_url_para_db))
            id_novo_modelo = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM perguntas_avaliacao")
            todas_perguntas = cursor.fetchall()

            impactos = []
            for pergunta in todas_perguntas:
                pergunta_id = pergunta[0]
                impactos.append((id_novo_modelo, pergunta_id, 'Sim', 0.00, empresa_id_logada))
                impactos.append((id_novo_modelo, pergunta_id, 'Não', 0.00, empresa_id_logada))

            sql_insert_impactos = """
                INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.executemany(sql_insert_impactos, impactos)

            cores_selecionadas = request.form.getlist('cores')
            for cor_id in cores_selecionadas:
                cursor.execute(
                    "INSERT INTO modelos_cores (modelo_id, cor_id, empresa_id, imagem_url) VALUES (%s, %s, %s, %s)",
                    (id_novo_modelo, int(cor_id), empresa_id_logada, 'images/placeholder.png')
                )

            armazenamentos_selecionados = request.form.getlist('armazenamentos')
            for armazenamento_id in armazenamentos_selecionados:
                cursor.execute(
                    "INSERT INTO modelos_armazenamentos (modelo_id, armazenamento_id, empresa_id) VALUES (%s, %s, %s)",
                    (id_novo_modelo, int(armazenamento_id), empresa_id_logada)
                )

            conn.commit()
            flash(f'Modelo "{nome_modelo}" adicionado com sucesso!', 'success')

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            flash('Erro ao adicionar o modelo.', 'danger')
            print(f"Erro ao adicionar modelo: {e}")

        finally:
            if conn:
                cursor.close()
                conn.close()

        return redirect(url_for('gerenciar_modelos_admin'))
    cores = []
    armazenamentos = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT id, nome_cor FROM cores ORDER BY nome_cor")
        cores = cursor.fetchall()

        cursor.execute("SELECT id, capacidade_gb FROM armazenamentos ORDER BY capacidade_gb")
        armazenamentos = cursor.fetchall()

    except psycopg2.Error as e:
        flash('Erro ao carregar cores e armazenamentos.', 'danger')
        print(f"Erro: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('adicionar_modelo.html', cores=cores, armazenamentos=armazenamentos)



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

        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        
        print(f"Deletando dependências para o modelo ID: {modelo_id} da empresa ID: {empresa_id_logada}")
        cursor.execute("DELETE FROM impacto_respostas WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        cursor.execute("DELETE FROM modelos_cores WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        cursor.execute("DELETE FROM modelos_armazenamentos WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        
        print(f"Deletando o modelo principal ID: {modelo_id}")
        cursor.execute("DELETE FROM modelos_iphone WHERE id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        
        conn.commit()
        flash('Modelo deletado com sucesso.', 'success')

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        flash('Erro ao deletar o modelo.', 'danger')
        print(f"Erro de PostgreSQL ao deletar modelo: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('gerenciar_modelos_admin'))

@app.route('/admin/usuarios')
def gerenciar_usuarios_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado. Esta página é apenas para administradores.', 'danger')
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada()
    empresa_id_logada = session['empresa_id']
    usuarios_da_empresa = []
    id_do_admin_logado = session['user_id'] 
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(
            "SELECT id, nome_completo, usuario as email, is_admin FROM usuarios WHERE empresa_id = %s AND id != %s ORDER BY nome_completo",
            (empresa_id_logada, id_do_admin_logado)
        )
        usuarios_da_empresa = cursor.fetchall()
        
    except psycopg2.Error as e:
        flash('Ocorreu um erro ao buscar os usuários.', 'danger')
        print(f"Erro ao buscar usuários para admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('admin_usuarios.html', usuarios=usuarios_da_empresa, info_empresa=info_empresa)


@app.route('/admin/adicionar-usuario', methods=['GET', 'POST'])
def adicionar_usuario_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada()
    
    if request.method == 'POST':
        empresa_id_logada = session['empresa_id']
        email = request.form['email'].strip().lower()
        nome = request.form['nome_completo']
        telefone = request.form['telefone']
        senha = request.form['senha']
        is_admin = 'is_admin' in request.form 

        hash_da_senha = generate_password_hash(senha)
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO usuarios (usuario, senha_hash, nome_completo, telefone, is_admin, empresa_id)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (email, hash_da_senha, nome, telefone, is_admin, empresa_id_logada)
            )
            conn.commit()
            flash(f'Usuário "{nome}" criado com sucesso!', 'success')
        except psycopg2.Error as e:
            if conn: conn.rollback()
            flash('Erro ao criar o usuário. O e-mail já pode estar em uso.', 'danger')
            print(f"Erro ao criar usuário: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        return redirect(url_for('gerenciar_usuarios_admin'))

    return render_template('admin_adicionar_usuario.html', info_empresa=info_empresa)


@app.route('/admin/deletar-usuario/<int:usuario_id>', methods=['POST'])
def deletar_usuario_admin(usuario_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    if usuario_id == session['user_id']:
        flash('Você não pode deletar sua própria conta.', 'danger')
        return redirect(url_for('gerenciar_usuarios_admin'))

    empresa_id_logada = session['empresa_id']
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM usuarios WHERE id = %s AND empresa_id = %s", (usuario_id, empresa_id_logada))
        
        conn.commit()
        flash('Usuário deletado com sucesso.', 'success')
    except psycopg2.Error as e:
        if conn: conn.rollback()
        flash('Erro ao deletar o usuário.', 'danger')
        print(f"Erro ao deletar usuário: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('gerenciar_usuarios_admin'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada()

    return render_template('admin_dashboard.html', info_empresa=info_empresa)

@app.route('/super-admin')
def super_admin_dashboard():

    if 'user_id' not in session or not session.get('is_admin') or session.get('empresa_id') != 1:
        flash('Acesso restrito ao Super Administrador.', 'danger')
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada() 
    empresas_clientes = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM empresas ORDER BY nome_empresa")
        empresas_clientes = cursor.fetchall()
        
    except psycopg2.Error as e:
        flash('Ocorreu um erro ao buscar os dados do Super Admin.', 'danger')
        print(f"Erro ao buscar empresas para super admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('super_admin_dashboard.html', empresas=empresas_clientes, info_empresa=info_empresa)

@app.route('/super-admin/adicionar-empresa', methods=['GET', 'POST'])
def adicionar_empresa_super_admin():

    if 'user_id' not in session or not session.get('is_admin') or session.get('empresa_id') != 1:
        flash('Acesso restrito ao Super Administrador.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':

        nome_empresa = request.form['nome_empresa']
        cnpj = request.form.get('cnpj') 
        nome_responsavel = request.form['nome_responsavel']
        email_admin = request.form['email_admin'].strip().lower()
        senha_admin = request.form['senha_admin']
        limite_usuarios = request.form['max_usuarios']

        permite_ajustes = 'permite_ajuste_valores' in request.form
        permite_link = 'permite_link_convidado' in request.form

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            sql_insert_empresa = """
                INSERT INTO empresas (nome_empresa, cnpj, nome_responsavel, email_contato_principal, max_usuarios, permite_ajuste_valores, permite_link_convidado)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """
            cursor.execute(sql_insert_empresa, (
                nome_empresa, cnpj, nome_responsavel, email_admin, limite_usuarios, permite_ajustes, permite_link
            ))
            nova_empresa_id = cursor.fetchone()['id']
            print(f"Empresa '{nome_empresa}' criada com ID: {nova_empresa_id}")
            hash_senha_admin = generate_password_hash(senha_admin)

            sql_insert_admin = """
                INSERT INTO usuarios (usuario, senha_hash, nome_completo, is_admin, empresa_id)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(sql_insert_admin, (email_admin, hash_senha_admin, nome_responsavel, True, nova_empresa_id))
            print(f"Usuário admin '{email_admin}' criado para a empresa ID: {nova_empresa_id}")

            print("Copiando dados de avaliação padrão para a nova empresa...")
            
            copiar_dados_mestre_para_empresa(cursor, nova_empresa_id)

            conn.commit()
            flash(f'Empresa "{nome_empresa}" e seu usuário administrador foram criados com sucesso!', 'success')

        except psycopg2.Error as e:
            if conn: conn.rollback() 
            flash(f'Erro ao criar empresa: {e}', 'danger')
            print(f"Erro ao criar empresa: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()
        
        return redirect(url_for('super_admin_dashboard'))

    info_empresa = get_info_empresa_logada()
    return render_template('super_admin_adicionar_empresa.html', info_empresa=info_empresa)


def copiar_dados_mestre_para_empresa(cursor, nova_empresa_id):
    """
    Copia os dados de avaliação da empresa mestre (ID=1) para uma nova empresa.
    VERSÃO CORRIGIDA PARA IGNORAR IDs ANTIGOS.
    """
    empresa_mestre_id = 1 

    cursor.execute("""
        INSERT INTO modelos_iphone (nome_modelo, valor_base_novo, imagem_padrao_url, empresa_id)
        SELECT nome_modelo, valor_base_novo, imagem_padrao_url, %s
        FROM modelos_iphone WHERE empresa_id = %s;
    """, (nova_empresa_id, empresa_mestre_id))
    
    cursor.execute("SELECT id, nome_modelo FROM modelos_iphone WHERE empresa_id = %s", (empresa_mestre_id,))
    mapa_id_antigo_para_nome = {row['id']: row['nome_modelo'] for row in cursor.fetchall()}

    cursor.execute("SELECT id, nome_modelo FROM modelos_iphone WHERE empresa_id = %s", (nova_empresa_id,))
    mapa_nome_para_id_novo = {row['nome_modelo']: row['id'] for row in cursor.fetchall()}

    tabelas_de_ligacao = ['modelos_cores', 'modelos_armazenamentos', 'impacto_respostas']
    
    for tabela in tabelas_de_ligacao:
        cursor.execute(f"SELECT * FROM {tabela} WHERE empresa_id = %s", (empresa_mestre_id,))
        dados_mestre = cursor.fetchall()
        
        if not dados_mestre:
            continue

        colunas_originais = [desc[0] for desc in cursor.description]

        colunas_para_inserir = [col for col in colunas_originais if col != 'id']
        colunas_str = ", ".join(colunas_para_inserir)
        placeholders_str = ", ".join(["%s"] * len(colunas_para_inserir))
        sql_insert = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders_str})"

        for linha_mestre in dados_mestre:
            id_modelo_antigo = linha_mestre.get('modelo_id')
            if id_modelo_antigo is None:
                continue 

            nome_modelo = mapa_id_antigo_para_nome.get(id_modelo_antigo)
            if not nome_modelo:
                continue

            id_modelo_novo = mapa_nome_para_id_novo.get(nome_modelo)
            if not id_modelo_novo:
                continue

            nova_linha_dict = dict(linha_mestre)
            nova_linha_dict['modelo_id'] = id_modelo_novo
            nova_linha_dict['empresa_id'] = nova_empresa_id

            valores_para_inserir = [nova_linha_dict[col] for col in colunas_para_inserir]

            cursor.execute(sql_insert, valores_para_inserir)

if __name__ == '__main__':
    app.run(debug=True)


