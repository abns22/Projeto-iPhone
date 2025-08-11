from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from flask import jsonify
import json
import secrets
import datetime
from PIL import Image
from io import BytesIO

load_dotenv()
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações do banco de dados com valores padrão para PythonAnywhere
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
SECRET_KEY = os.getenv('SECRET_KEY', 'icloudbz12031994@lF')

app.secret_key = SECRET_KEY

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'images')

# Configurações de email com fallback para variáveis de ambiente
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'ogordogamer2@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'ylmu lcyn khlp ckpd')

mail = Mail(app)

def get_db_connection():
    """
    Estabelece e retorna uma nova conexão com o banco de dados MySQL.
    Funciona tanto no Railway quanto no PythonAnywhere.
    """
    try:
        # Verificar se estamos no Railway (tem DATABASE_URL)
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Configuração para Railway
            import urllib.parse
            url = urllib.parse.urlparse(database_url)
            
            conn_args = {
                'database': url.path[1:],  # Remove a barra inicial
                'user': url.username,
                'password': url.password,
                'host': url.hostname,
                'port': url.port or 3306,
                'autocommit': True
            }
        else:
            # Configuração para PythonAnywhere ou local
            db_host = os.getenv('DB_HOST')
            db_user = os.getenv('DB_USER')
            db_name = os.getenv('DB_NAME')
            if not all([db_host, db_user, db_name]):
                raise ValueError("Variáveis de ambiente do banco de dados (DB_HOST, DB_USER, DB_NAME) não estão configuradas para ambiente não-Railway.")

            conn_args = {
                'database': db_name,
                'user': db_user,
                'password': os.getenv('DB_PASS'), # DB_PASS pode ser vazio para conexões locais
                'host': db_host,
                'port': int(os.getenv('DB_PORT', 3306)), # Porta padrão 3306 se não especificada
                'autocommit': True
            }

        conn = mysql.connector.connect(**conn_args)
        return conn

    except mysql.connector.Error as e:
        print(f"ERRO DE CONEXÃO COM O MYSQL: {e}")
        return None
    except Exception as e:
        print(f"ERRO GERAL DE CONEXÃO: {e}")
        return None

def require_login():
    if 'user_id' not in session:
        flash('Faça login para acessar.', 'warning')
        return redirect(url_for('login'))
    return None

def require_admin():
    if not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('login'))
    return None

def require_super_admin():
    if not session.get('is_admin') or session.get('empresa_id') != 1:
        flash('Acesso restrito ao Super Admin.', 'danger')
        return redirect(url_for('login'))
    return None

def require_empresa_permissao():
    # Verifica se o usuário é admin E se a empresa tem permissão para gerenciar
    # Apenas usuários admin de empresas com permissão podem acessar
    if not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('login'))

    # Verificar se o plano da empresa está ativo
    if not session.get('plano_ativo', True):
        flash('Seu plano está desativado. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('logout'))

    # Atualiza as permissões da empresa na sessão
    get_info_empresa_logada()

    if not session.get('empresa_pode_gerir'):
        flash('Sua empresa não tem permissão para acessar esta funcionalidade.', 'warning')
        return redirect(url_for('calcular'))

    return None

def require_plano_ativo():
    """Verifica se o plano da empresa está ativo"""
    if not session.get('plano_ativo', True):
        return jsonify({"erro": "Seu plano está desativado. Entre em contato com o administrador."}), 403
    return None

@app.route('/')
def rota_principal():
    """
    Esta é a página inicial. Redireciona para a página de login.
    """
    return redirect(url_for('login'))

@app.route('/corrigir-respostas')
def corrigir_respostas():
    """
    Rota para corrigir as respostas das perguntas.
    """
    garantir_respostas_completas()
    return "Respostas corrigidas com sucesso!"

@app.route('/index', methods=['GET', 'POST'])
def login():
    erro = None

    if request.method == 'POST':
        conn = None

        try:

            conn = get_db_connection()

            if conn is None:

                erro = "Erro interno no servidor. Tente novamente mais tarde."
                flash(erro, "danger")

                return render_template('index.html', erro=erro)

            cursor = conn.cursor(dictionary=True)

            usuario = request.form.get('usuario')
            senha = request.form.get('senha')

            if not usuario or not senha:
                erro = "Usuário e senha são obrigatórios."
            else:

                cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
                registro_usuario_db = cursor.fetchone()

                if registro_usuario_db and check_password_hash(registro_usuario_db['senha_hash'], senha):
                    # Verificar se empresa_id não é None
                    empresa_id = registro_usuario_db.get('empresa_id')
                    if empresa_id is None:
                        erro = "Usuário não está associado a uma empresa válida."
                        flash(erro, "danger")
                        return render_template('index.html', erro=erro)

                    cursor.execute("SELECT permite_ajuste_valores, permite_link_convidado, envia_email_orcamento, envia_email_orcamento_link, plano_ativo FROM empresas WHERE id = %s", (empresa_id,))
                    info_empresa = cursor.fetchone()
                
                    # Verificar se o plano da empresa está ativo
                    if info_empresa and not info_empresa['plano_ativo']:
                        erro = "Seu plano está desativado. Entre em contato com o administrador."
                        flash(erro, "danger")
                        return render_template('index.html', erro=erro)
                    
                    session.clear()
                    session['user_id'] = registro_usuario_db['id']
                    session['nome_completo'] = registro_usuario_db['nome_completo']
                    session['usuario_email'] = registro_usuario_db['usuario']  # Armazena o email do usuário
                    session['is_admin'] = registro_usuario_db['is_admin']
                    session['empresa_id'] = empresa_id
                    if info_empresa:
                        session['empresa_pode_gerir'] = info_empresa['permite_ajuste_valores']
                        session['permite_link_convidado'] = info_empresa['permite_link_convidado']
                        session['envia_email_orcamento'] = info_empresa['envia_email_orcamento']
                        session['envia_email_orcamento_link'] = info_empresa['envia_email_orcamento_link']
                        session['plano_ativo'] = info_empresa['plano_ativo']
                    else:
                        session['empresa_pode_gerir'] = False
                        session['permite_link_convidado'] = False
                        session['envia_email_orcamento'] = False
                        session['envia_email_orcamento_link'] = False
                        session['plano_ativo'] = False
                    print('DEBUG LOGIN SESSION:', dict(session))
                    return redirect(url_for('calcular'))
                else:
                    erro = "Usuário ou senha inválidos."

            if erro:
                flash(erro, "danger")

        except Exception as e:

            print(f"ERRO INESPERADO NA ROTA DE LOGIN: {e}")
            flash("Ocorreu um erro inesperado durante o login.", "danger")
        finally:

            if conn:
                conn.close()

    return render_template('index.html', erro=erro)

def get_info_empresa_logada():
    if 'empresa_id' not in session or session['empresa_id'] is None:
        return None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome_empresa, logo_url, permite_ajuste_valores, permite_link_convidado, envia_email_orcamento, envia_email_orcamento_link, plano_ativo FROM empresas WHERE id = %s", (session['empresa_id'],))
        info_empresa = cursor.fetchone()

        # Atualiza as permissões na sessão se necessário
        if info_empresa:
            session['empresa_pode_gerir'] = info_empresa['permite_ajuste_valores']
            session['permite_link_convidado'] = info_empresa['permite_link_convidado']
            session['envia_email_orcamento'] = info_empresa['envia_email_orcamento']
            session['envia_email_orcamento_link'] = info_empresa['envia_email_orcamento_link']
            session['plano_ativo'] = info_empresa['plano_ativo']

        return info_empresa
    except mysql.connector.Error as e:
        print(f"Erro ao buscar info da empresa: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def garantir_respostas_completas():
    """
    Garante que todas as perguntas tenham as duas respostas (Sim e Não)
    para todos os modelos de todas as empresas.
    """
    print("Iniciando verificação e correção de respostas...")
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados. Abortando.")
        return

    try:
        with conn.cursor(dictionary=True) as cursor:

            # Busca todas as perguntas de avaliação
            cursor.execute("SELECT id FROM perguntas_avaliacao")
            todas_perguntas = cursor.fetchall()
            if not todas_perguntas:
                print("Nenhuma pergunta de avaliação encontrada.")
                return

            print(f"Encontradas {len(todas_perguntas)} perguntas de avaliação.")

            # Busca todos os modelos de todas as empresas
            cursor.execute("SELECT id, empresa_id FROM modelos_iphone")
            todos_modelos = cursor.fetchall()
            if not todos_modelos:
                print("Nenhum modelo encontrado.")
                return

            print(f"Encontrados {len(todos_modelos)} modelos.")

            # Itera sobre cada modelo
            for modelo in todos_modelos:
                modelo_id = modelo['id']
                empresa_id = modelo['empresa_id']

                print(f"\n--- Verificando Modelo ID: {modelo_id} (Empresa ID: {empresa_id}) ---")

                # Itera sobre cada pergunta para o modelo atual
                for pergunta in todas_perguntas:
                    pergunta_id = pergunta['id']

                    # Verifica as respostas existentes para esta combinação
                    cursor.execute(
                        "SELECT resposta_que_gera_impacto FROM impacto_respostas WHERE modelo_id = %s AND pergunta_id = %s AND empresa_id = %s",
                        (modelo_id, pergunta_id, empresa_id)
                    )
                    respostas_existentes = {row['resposta_que_gera_impacto'] for row in cursor.fetchall()}

                    # Se já existem as duas respostas ("Sim" e "Não"), está tudo certo
                    if len(respostas_existentes) >= 2:
                        continue

                    # Se não existe a resposta "Sim", cria ela com impacto 0
                    if "Sim" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Sim' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute(
                            "INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (%s, %s, 'Sim', 0.00, %s)",
                            (modelo_id, pergunta_id, empresa_id)
                        )

                    # Se não existe a resposta "Não", cria ela com impacto 0
                    if "Não" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Não' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute(
                            "INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (%s, %s, 'Não', 0.00, %s)",
                            (modelo_id, pergunta_id, empresa_id)
                        )

            # Salva todas as alterações feitas no banco de dados
            conn.commit()
            print("\nVerificação e correção de respostas concluída com sucesso!")

    except mysql.connector.Error as e:
        print(f"Ocorreu um erro com o MySQL durante a correção: {e}")
        print("Desfazendo alterações (rollback)...")
        conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Conexão com o MySQL fechada.")

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
    
    # Verificar se o plano da empresa está ativo
    if not session.get('plano_ativo', True):
        flash('Seu plano está desativado. Entre em contato com o administrador.', 'danger')
        return redirect(url_for('logout'))
    
    info_empresa = get_info_empresa_logada()
    if info_empresa:
        session['permite_ajuste_valores'] = info_empresa.get('permite_ajuste_valores', 0)
        session['permite_link_convidado'] = info_empresa.get('permite_link_convidado', 0)
    print('DEBUG SESSION IN CALCULAR:', dict(session))
    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Ocorreu um erro com a identificação da sua empresa. Por favor, faça login novamente.", "danger")
        return redirect(url_for('logout'))

    conn = None
    modelos = []
    dados_usuario_logado = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        id_usuario = session['user_id']

        cursor.execute("SELECT nome_completo, telefone FROM usuarios WHERE id = %s AND empresa_id = %s", (id_usuario, empresa_id_logada))
        dados_usuario_logado = cursor.fetchone()

        cursor.execute(
            "SELECT id, nome_modelo, imagem_padrao_url FROM modelos_iphone WHERE empresa_id = %s ORDER BY id",
            (empresa_id_logada,)
        )
        modelos = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Não foi possível carregar os dados da página. Tente novamente mais tarde.', 'danger')
        print(f"Erro de PostgreSQL na rota /calcular: {e}")
    finally:

        if conn:
            cursor.close()
            conn.close()

    return render_template('calcular_modern.html', modelos=modelos, usuario=dados_usuario_logado, info_empresa=info_empresa, is_admin=session.get('is_admin'), empresa_pode_gerir=session.get('empresa_pode_gerir'), permite_link_convidado=session.get('permite_link_convidado'), permite_ajuste_valores=session.get('permite_ajuste_valores'))


@app.route('/api/modelo/<int:modelo_id>/opcoes')
def get_opcoes_modelo(modelo_id):
    resp = require_login()
    if resp: return resp
    
    # Verificar se o plano da empresa está ativo
    resp = require_plano_ativo()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        return jsonify({"erro": "Usuário não está associado a uma empresa válida"}), 400

    opcoes = {
        "modelo_info": None,
        "cores": [],
        "armazenamentos": []
    }

    conn = None
    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

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

    except mysql.connector.Error as e:
        print(f"Erro de PostgreSQL ao buscar opções: {e}")
        return jsonify({"erro": "Erro no servidor ao buscar opções"}), 500
    finally:

        if conn:
            cursor.close()
            conn.close()

    return jsonify(opcoes)

# --- ENVIAR ORÇAMENTO PADRÃO ---
@app.route('/api/enviar-orcamento', methods=['POST'])
def enviar_orcamento():
    try:
        print("=== INÍCIO DA FUNÇÃO enviar_orcamento ===")
        
        # Verificar se o usuário está logado
        if 'user_id' not in session:
            return jsonify({"mensagem": "Usuário não está logado"}), 401
        
        # Obter dados do request
        dados = request.get_json()
        print(f"DEBUG - Dados recebidos: {dados}")
        
        # Extrair dados do cliente
        nome_cliente = dados.get('nomeCliente', '').strip()
        telefone_cliente = dados.get('telefoneCliente', '').strip()
        email_cliente = dados.get('emailCliente', '').strip()
        modelo_interesse = dados.get('modeloInteresse', '').strip()
        
        # Verificar se os dados do cliente foram preenchidos
        dados_preenchidos = bool(nome_cliente and telefone_cliente and email_cliente and modelo_interesse)
        print(f"DEBUG - Dados preenchidos: {dados_preenchidos}")
        
        if dados_preenchidos:
            print(f"DEBUG - Dados do frontend: nomeCliente={nome_cliente}, telefoneCliente={telefone_cliente}")
            print(f"DEBUG - Email cliente: {email_cliente}, Modelo interesse: {modelo_interesse}")
        else:
            # Se não foram preenchidos, usar dados do usuário logado
            nome_cliente = session.get('nome_completo', '')
            telefone_cliente = session.get('telefone_usuario', '')
            email_cliente = session.get('usuario_email', '')
            modelo_interesse = dados.get('modeloSelecionado', '')
        
        print(f"DEBUG - Dados finais: nome={nome_cliente}, telefone={telefone_cliente}")
        
        # Obter outros dados necessários
        modelo_id = dados.get('modeloId')
        cor_selecionada = dados.get('cor', '')
        armazenamento_selecionado = dados.get('armazenamento', '')
        imei = dados.get('imei', '000000000')
        valor_final_calculado = dados.get('valor', 0)
        resumo_respostas = dados.get('resumo', {})
        
        # Obter dados da sessão
        empresa_id = session.get('empresa_id')
        usuario_id = session.get('user_id')
        
        # Converter resumo para JSON
        resumo_json = json.dumps(resumo_respostas, ensure_ascii=False)
        
        # Obter valor base do banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar valor base do modelo
        cursor.execute("SELECT valor_base_novo FROM modelos_iphone WHERE id = %s", (modelo_id,))
        resultado = cursor.fetchone()
        valor_base_db = resultado[0] if resultado else 0
        
        print("DEBUG - Valores para INSERT:")
        print(f"empresa_id_logada: {empresa_id}")
        print(f"usuario_id_logado: {usuario_id}")
        print(f"nome_cliente_final: {nome_cliente}")
        print(f"email_cliente_final: {email_cliente}")
        print(f"telefone_cliente_final: {telefone_cliente}")
        print(f"modelo_interesse: {modelo_interesse}")
        print(f"modelo_id: {modelo_id}")
        print(f"cor_selecionada: {cor_selecionada}")
        print(f"armazenamento_selecionado: {armazenamento_selecionado}")
        print(f"imei: {imei}")
        print(f"valor_base_db: {valor_base_db}")
        print(f"valor_final_calculado: {valor_final_calculado}")
        
        # Inserir no banco de dados
        sql_insert = """
            INSERT INTO avaliacoes_concluidas (
                empresa_id, usuario_id, nome_cliente_final, email_cliente_final, telefone_cliente_final,
                modelo_interesse, modelo_iphone_id, cor_selecionada, armazenamento_selecionado, imei,
                valor_base_calculado, valor_final_calculado, resumo_respostas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql_insert, (
            empresa_id, usuario_id, nome_cliente, email_cliente, telefone_cliente,
            modelo_interesse, modelo_id, cor_selecionada, armazenamento_selecionado, imei,
            valor_base_db, valor_final_calculado, resumo_json
        ))
        
        conn.commit()
        print("✅ Avaliação salva com sucesso no banco de dados.")
        
        # === ENVIO DE EMAIL ===
        print("\n=== PREPARANDO ENVIO DE EMAIL ===")
        
        try:
            # Buscar configurações de email da empresa (reutilizar conexão existente)
            # Não fechar a conexão aqui, pois ainda precisamos dela para buscar configurações
            
            # Primeiro, verificar se as colunas de email existem
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'empresas' 
                AND COLUMN_NAME IN ('email_empresa', 'senha_email_empresa', 'servidor_smtp', 'porta_smtp', 'usar_tls', 'usar_ssl')
            """)
            
            colunas_existentes = [row[0] for row in cursor.fetchall()]
            
            # Se as colunas não existem, usar apenas email_contato_principal
            if not colunas_existentes:
                cursor.execute("""
                    SELECT email_contato_principal, nome_empresa
                    FROM empresas WHERE id = %s
                """, (empresa_id,))
                
                config_email = cursor.fetchone()
                
                if not config_email:
                    print("❌ Configurações de email não encontradas para a empresa")
                    return jsonify({"mensagem": "Orçamento salvo com sucesso! (Email não enviado - configurações não encontradas)"})
                
                email_empresa, nome_empresa = config_email
                
                # Usar configurações do arquivo .env
                servidor_smtp = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
                porta_smtp = int(os.getenv('MAIL_PORT', '587'))
                usar_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
                usar_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
                senha_email = os.getenv('MAIL_PASSWORD', '')
                email_env = os.getenv('MAIL_USERNAME', '')
                
                # Se não há email configurado no .env, usar o email da empresa
                if not email_env:
                    email_env = email_empresa
                
                print("⚠️ Usando configurações de email do arquivo .env")
                print("Configurações:")
                print(f"- Servidor: {servidor_smtp}")
                print(f"- Porta: {porta_smtp}")
                print(f"- TLS: {usar_tls}")
                print(f"- SSL: {usar_ssl}")
                print(f"- Email remetente: {email_env}")
                print(f"- Destinatário: {email_empresa}")
                
                if not senha_email:
                    print("⚠️ Senha de email não configurada no .env - email não será enviado")
                    return jsonify({"mensagem": "Orçamento salvo com sucesso! (Email não enviado - senha não configurada)"})
                
                # Configurar Flask-Mail
                app.config['MAIL_SERVER'] = servidor_smtp
                app.config['MAIL_PORT'] = porta_smtp
                app.config['MAIL_USE_TLS'] = usar_tls
                app.config['MAIL_USE_SSL'] = usar_ssl
                app.config['MAIL_USERNAME'] = email_env
                app.config['MAIL_PASSWORD'] = senha_email
                
                mail = Mail(app)
                
                # Preparar email
                modelo_nome = dados.get('modeloSelecionado', 'iPhone')
                assunto = f"Novo Orçamento de Avaliação para {modelo_nome}"
                
                # Criar mensagem HTML
                try:
                    valor_formatado = f"{float(valor_final_calculado):.2f}"
                except (ValueError, TypeError):
                    valor_formatado = str(valor_final_calculado)
                
                mensagem_html = f"""
                <html>
                <body>
                    <h2>Novo Orçamento de Avaliação</h2>
                    <p><strong>Empresa:</strong> {nome_empresa}</p>
                    <p><strong>Cliente:</strong> {nome_cliente}</p>
                    <p><strong>Telefone:</strong> {telefone_cliente}</p>
                    <p><strong>Email:</strong> {email_cliente}</p>
                    <p><strong>Modelo de Interesse:</strong> {modelo_interesse}</p>
                    <p><strong>Modelo Avaliado:</strong> {dados.get('modeloSelecionado', '')}</p>
                    <p><strong>Cor:</strong> {cor_selecionada}</p>
                    <p><strong>Armazenamento:</strong> {armazenamento_selecionado}</p>
                    <p><strong>IMEI:</strong> {imei}</p>
                    <p><strong>Valor Final:</strong> R$ {valor_formatado}</p>
                    
                    <h3>Resumo das Respostas:</h3>
                    <ul>
                """
                
                # Verificar se resumo_respostas é uma lista ou dicionário
                if isinstance(resumo_respostas, list):
                    for item in resumo_respostas:
                        if isinstance(item, dict) and 'pergunta' in item and 'resposta' in item:
                            mensagem_html += f"<li><strong>{item['pergunta']}:</strong> {item['resposta']}</li>"
                        elif isinstance(item, str):
                            mensagem_html += f"<li>{item}</li>"
                        else:
                            mensagem_html += f"<li>{str(item)}</li>"
                elif isinstance(resumo_respostas, dict):
                    for pergunta, resposta in resumo_respostas.items():
                        mensagem_html += f"<li><strong>{pergunta}:</strong> {resposta}</li>"
                else:
                    mensagem_html += f"<li>Resumo não disponível</li>"
                
                mensagem_html += """
                    </ul>
                </body>
                </html>
                """
                
                print(f"Assunto preparado: {assunto}")
                print("Mensagem preparada, tentando enviar...")
                
                # Enviar email
                msg = Message(
                    subject=assunto,
                    sender=email_env,
                    recipients=[email_empresa],
                    html=mensagem_html
                )
                
                mail.send(msg)
                print("✅ Email enviado com sucesso!")
                
                return jsonify({"mensagem": "Orçamento enviado com sucesso para a nossa equipe e registrado!"})
            
            # Se as colunas existem, usar a query original
            cursor.execute("""
                SELECT email_empresa, senha_email_empresa, servidor_smtp, porta_smtp, 
                       usar_tls, usar_ssl, nome_empresa
                FROM empresas WHERE id = %s
            """, (empresa_id,))
            
            config_email = cursor.fetchone()
            
            if not config_email:
                print("❌ Configurações de email não encontradas para a empresa")
                return jsonify({"mensagem": "Orçamento salvo com sucesso! (Email não enviado - configurações não encontradas)"})
            
            email_empresa, senha_email, servidor_smtp, porta_smtp, usar_tls, usar_ssl, nome_empresa = config_email
            
            print("Configurações:")
            print(f"- Servidor: {servidor_smtp}")
            print(f"- Porta: {porta_smtp}")
            print(f"- TLS: {usar_tls}")
            print(f"- SSL: {usar_ssl}")
            print(f"- Destinatário: {email_empresa}")
            
            # Configurar Flask-Mail
            app.config['MAIL_SERVER'] = servidor_smtp
            app.config['MAIL_PORT'] = porta_smtp
            app.config['MAIL_USE_TLS'] = usar_tls
            app.config['MAIL_USE_SSL'] = usar_ssl
            app.config['MAIL_USERNAME'] = email_empresa
            app.config['MAIL_PASSWORD'] = senha_email
            
            mail = Mail(app)
            
            # Preparar email
            modelo_nome = dados.get('modeloSelecionado', 'iPhone')
            assunto = f"Novo Orçamento de Avaliação para {modelo_nome}"
            
            # Criar mensagem HTML
            try:
                valor_formatado = f"{float(valor_final_calculado):.2f}"
            except (ValueError, TypeError):
                valor_formatado = str(valor_final_calculado)
            
            mensagem_html = f"""
            <html>
            <body>
                <h2>Novo Orçamento de Avaliação</h2>
                <p><strong>Empresa:</strong> {nome_empresa}</p>
                <p><strong>Cliente:</strong> {nome_cliente}</p>
                <p><strong>Telefone:</strong> {telefone_cliente}</p>
                <p><strong>Email:</strong> {email_cliente}</p>
                <p><strong>Modelo de Interesse:</strong> {modelo_interesse}</p>
                <p><strong>Modelo Avaliado:</strong> {dados.get('modeloSelecionado', '')}</p>
                <p><strong>Cor:</strong> {cor_selecionada}</p>
                <p><strong>Armazenamento:</strong> {armazenamento_selecionado}</p>
                <p><strong>IMEI:</strong> {imei}</p>
                <p><strong>Valor Final:</strong> R$ {valor_formatado}</p>
                
                <h3>Resumo das Respostas:</h3>
                <ul>
            """
            
            # Verificar se resumo_respostas é uma lista ou dicionário
            if isinstance(resumo_respostas, list):
                for item in resumo_respostas:
                    if isinstance(item, dict) and 'pergunta' in item and 'resposta' in item:
                        mensagem_html += f"<li><strong>{item['pergunta']}:</strong> {item['resposta']}</li>"
                    elif isinstance(item, str):
                        mensagem_html += f"<li>{item}</li>"
                    else:
                        mensagem_html += f"<li>{str(item)}</li>"
            elif isinstance(resumo_respostas, dict):
                for pergunta, resposta in resumo_respostas.items():
                    mensagem_html += f"<li><strong>{pergunta}:</strong> {resposta}</li>"
            else:
                mensagem_html += f"<li>Resumo não disponível</li>"
            
            mensagem_html += """
                </ul>
            </body>
            </html>
            """
            
            print(f"Assunto preparado: {assunto}")
            print("Mensagem preparada, tentando enviar...")
            
            # Enviar email
            msg = Message(
                subject=assunto,
                sender=email_empresa,
                recipients=[email_empresa],
                html=mensagem_html
            )
            
            mail.send(msg)
            print("✅ Email enviado com sucesso!")
            
            return jsonify({"mensagem": "Orçamento enviado com sucesso para a nossa equipe e registrado!"})
            
        except Exception as email_error:
            print(f"\n❌ ERRO NO ENVIO DE EMAIL")
            print(f"")
            print(f"Tipo do erro: {type(email_error).__name__}")
            print(f"Mensagem: {email_error}")
            print(f"Detalhes:")
            print(f"- Email destino: {email_empresa if 'email_empresa' in locals() else 'N/A'}")
            print(f"- Empresa ID: {empresa_id}")
            print(f"Erro ao enviar e-mail: {email_error}")
            
            # Retornar sucesso para o banco, mas indicar falha no email
            return jsonify({
                "mensagem": f"Orçamento salvo com sucesso! (Email não enviado - {str(email_error)})"
            })
            
    except Exception as e:
        print(f"❌ ERRO GERAL na função enviar_orcamento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"mensagem": "Erro interno do servidor"}), 500
    finally:
        # Fechar conexão e cursor no final da função
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/api/modelo/<int:modelo_id>/perguntas')
def get_perguntas_modelo(modelo_id):
    resp = require_login()
    if resp: return resp
    
    # Verificar se o plano da empresa está ativo
    resp = require_plano_ativo()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        return jsonify({"erro": "Usuário não está associado a uma empresa válida"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"erro": "Erro ao conectar ao banco"}), 500

        cursor = conn.cursor(dictionary=True)

        # Busca todas as perguntas de avaliação incluindo informações condicionais (GLOBAIS)
        # Ordena de forma que perguntas condicionais apareçam logo após suas perguntas pai
        cursor.execute("""
            SELECT
                p.id AS pergunta_id,
                p.texto_pergunta,
                p.pergunta_pai_id,
                p.resposta_pai_requerida,
                CASE 
                    WHEN p.pergunta_pai_id IS NULL THEN p.id
                    ELSE p.pergunta_pai_id + 0.5
                END as ordem_exibicao
            FROM perguntas_avaliacao p
            ORDER BY ordem_exibicao, p.id
        """)

        todas_perguntas = cursor.fetchall()
        perguntas = []

        for pergunta in todas_perguntas:
            pergunta_id = pergunta['pergunta_id']

            # Busca as respostas existentes para esta pergunta e modelo
            cursor.execute("""
                SELECT
                    ir.resposta_que_gera_impacto,
                    ir.valor_do_impacto
                FROM impacto_respostas ir
                WHERE ir.pergunta_id = %s AND ir.modelo_id = %s AND ir.empresa_id = %s
            """, (pergunta_id, modelo_id, empresa_id_logada))

            respostas_existentes = cursor.fetchall()

            # Cria um dicionário para facilitar a busca
            respostas_dict = {r['resposta_que_gera_impacto']: r['valor_do_impacto'] for r in respostas_existentes}

            # Garante que sempre tenha as duas opções
            respostas = []

            # Adiciona resposta "Sim"
            impacto_sim = respostas_dict.get('Sim', 0.0)
            respostas.append({
                'texto': 'Sim',
                'impacto': float(impacto_sim)
            })

            # Adiciona resposta "Não"
            impacto_nao = respostas_dict.get('Não', 0.0)
            respostas.append({
                'texto': 'Não',
                'impacto': float(impacto_nao)
            })

            pergunta_obj = {
                'pergunta_id': pergunta_id,
                'texto_pergunta': pergunta['texto_pergunta'],
                'respostas': respostas
            }
            
            # Adicionar informações condicionais se existirem
            if pergunta['pergunta_pai_id']:
                pergunta_obj['pergunta_pai_id'] = pergunta['pergunta_pai_id']
                pergunta_obj['resposta_pai_requerida'] = pergunta['resposta_pai_requerida']
            
            perguntas.append(pergunta_obj)

        return jsonify(perguntas)

    except Exception as e:
        print(f"Erro ao buscar perguntas: {e}")
        return jsonify({"erro": "Falha ao buscar perguntas"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# Exemplo para as principais rotas sensíveis:

@app.route('/admin/ajustes')
def gerenciar_modelos_admin():
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    is_super_admin = (empresa_id_logada == 1)

    conn = None
    modelos_da_empresa = []
    info_empresa = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        cursor.execute("SELECT nome_empresa, logo_url FROM empresas WHERE id = %s", (empresa_id_logada,))
        info_empresa = cursor.fetchone()


        cursor.execute(
            "SELECT * FROM modelos_iphone WHERE empresa_id = %s ORDER BY nome_modelo",
            (empresa_id_logada,)
        )
        modelos_da_empresa = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Ocorreu um erro ao buscar os dados para administração.', 'danger')
        print(f"Erro de PostgreSQL ao buscar para admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    return render_template(
        'admin_ajustes.html',
        modelos=modelos_da_empresa,
        is_super_admin=is_super_admin,
        info_empresa=info_empresa,
        is_admin=session.get('is_admin'),
        empresa_pode_gerir=session.get('empresa_pode_gerir'),
        permite_link_convidado=session.get('permite_link_convidado'),
        permite_ajuste_valores=session.get('permite_ajuste_valores')
    )

@app.route('/admin/editar-modelo/<int:modelo_id>', methods=['GET', 'POST'])
def editar_modelo_admin(modelo_id):
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    conn = None

    try:
        conn = get_db_connection()
        if not conn:
            flash("Erro de conexão com o banco de dados.", "danger")
            return redirect(url_for('gerenciar_modelos_admin'))

        cursor = conn.cursor(dictionary=True)

        # --- LÓGICA PARA SALVAR OS DADOS (MÉTODO POST) ---
        if request.method == 'POST':
            # 1. Atualiza os dados principais do modelo
            novo_nome = request.form.get('nome_modelo')
            novo_valor_base = request.form.get('valor_base_novo')
            cursor.execute(
                "UPDATE modelos_iphone SET nome_modelo = %s, valor_base_novo = %s WHERE id = %s AND empresa_id = %s",
                (novo_nome, novo_valor_base, modelo_id, empresa_id_logada)
            )

            # 2. Processa os modificadores de armazenamento
            for key, value in request.form.items():
                if key.startswith('modificador_armazenamento_'):
                    armazenamento_id = key.replace('modificador_armazenamento_', '')
                    novo_modificador = float(value) if value else 0.0
                    
                    cursor.execute(
                        "UPDATE modelos_armazenamentos SET modificador_valor = %s WHERE modelo_id = %s AND armazenamento_id = %s AND empresa_id = %s",
                        (novo_modificador, modelo_id, armazenamento_id, empresa_id_logada)
                    )

            # 3. Itera sobre os dados do formulário para encontrar e salvar os valores de impacto
            for key, value in request.form.items():
                resposta_texto = None
                if key.startswith('impacto_sim_'):
                    pergunta_id = key.replace('impacto_sim_', '')
                    resposta_texto = 'Sim'
                elif key.startswith('impacto_nao_'):
                    pergunta_id = key.replace('impacto_nao_', '')
                    resposta_texto = 'Não'
                else:
                    continue

                novo_valor_impacto = float(value) if value else 0.0

                cursor.execute(
                    "UPDATE impacto_respostas SET valor_do_impacto = %s WHERE modelo_id = %s AND pergunta_id = %s AND resposta_que_gera_impacto = %s AND empresa_id = %s",
                    (novo_valor_impacto, modelo_id, pergunta_id, resposta_texto, empresa_id_logada)
                )

            conn.commit()
            flash('Modelo atualizado com sucesso!', 'success')
            return redirect(url_for('gerenciar_modelos_admin'))

        # --- LÓGICA PARA CARREGAR OS DADOS (MÉTODO GET) ---

        # 1. Busca os dados do modelo APENAS UMA VEZ
        cursor.execute("SELECT * FROM modelos_iphone WHERE id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
        modelo = cursor.fetchone()
        if not modelo:
            flash("Modelo não encontrado.", "danger")
            return redirect(url_for('gerenciar_modelos_admin'))

        # 2. Busca os armazenamentos associados ao modelo
        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = %s AND ma.empresa_id = %s
            ORDER BY a.capacidade_gb
        """
        cursor.execute(sql_armazenamentos, (modelo_id, empresa_id_logada))
        armazenamentos = cursor.fetchall()

        # 3. CONSULTA SQL INTELIGENTE QUE RESOLVE A DUPLICAÇÃO
        sql_perguntas = """
            SELECT
                p.id, p.texto_pergunta,
                MAX(CASE WHEN ir.resposta_que_gera_impacto = 'Sim' THEN ir.valor_do_impacto END) AS impacto_sim,
                MAX(CASE WHEN ir.resposta_que_gera_impacto = 'Não' THEN ir.valor_do_impacto END) AS impacto_nao
            FROM perguntas_avaliacao p
            LEFT JOIN impacto_respostas ir ON p.id = ir.pergunta_id AND ir.modelo_id = %s AND ir.empresa_id = %s
            GROUP BY p.id, p.texto_pergunta
            ORDER BY p.id;
        """
        cursor.execute(sql_perguntas, (modelo_id, empresa_id_logada))
        perguntas_com_impactos = cursor.fetchall()

        return render_template(
            'editar_modelo.html',
            modelo=modelo,                  # Passa o objeto do modelo
            armazenamentos=armazenamentos,  # Passa a lista de armazenamentos
            perguntas=perguntas_com_impactos  # Passa a lista de perguntas únicas
        )

    except mysql.connector.Error as e:
        if conn: conn.rollback()
        print(f"ERRO DE MYSQL NA ROTA DE EDIÇÃO: {e}")
        flash("Ocorreu um erro de banco de dados.", "danger")
        return redirect(url_for('gerenciar_modelos_admin'))
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/admin/adicionar-modelo', methods=['GET', 'POST'])
def adicionar_modelo_admin():
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

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
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(sql_insert_modelo, (nome_modelo, valor_base, empresa_id_logada, imagem_url_para_db))
            id_novo_modelo = cursor.lastrowid

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
                (id_novo_modelo, int(cor_id), empresa_id_logada, imagem_url_para_db)
            )

            armazenamentos_selecionados = request.form.getlist('armazenamentos')
            for armazenamento_id in armazenamentos_selecionados:
                cursor.execute(
                    "INSERT INTO modelos_armazenamentos (modelo_id, armazenamento_id, empresa_id) VALUES (%s, %s, %s)",
                    (id_novo_modelo, int(armazenamento_id), empresa_id_logada)
                )

            conn.commit()
            flash(f'Modelo "{nome_modelo}" adicionado com sucesso!', 'success')

        except mysql.connector.Error as e:
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
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, nome_cor FROM cores ORDER BY nome_cor")
        cores = cursor.fetchall()

        cursor.execute("SELECT id, capacidade_gb FROM armazenamentos ORDER BY capacidade_gb")
        armazenamentos = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar cores e armazenamentos.', 'danger')
        print(f"Erro: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('adicionar_modelo.html', cores=cores, armazenamentos=armazenamentos)

@app.route('/admin/deletar-modelo/<int:modelo_id>', methods=['POST'])
def deletar_modelo_admin(modelo_id):
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp


    empresa_id_logada = session.get('empresa_id')
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            flash("Erro de conexão.", "danger")
            return redirect(url_for('gerenciar_modelos_admin'))

        with conn.cursor() as cursor:

            print(f"--- INICIANDO DELETE ---")
            print(f"Tentando deletar modelo ID: {modelo_id} para a empresa ID: {empresa_id_logada}")

            cursor.execute("DELETE FROM avaliacoes_concluidas WHERE modelo_iphone_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
            cursor.execute("DELETE FROM impacto_respostas WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
            cursor.execute("DELETE FROM modelos_cores WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))
            cursor.execute("DELETE FROM modelos_armazenamentos WHERE modelo_id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))

            cursor.execute("DELETE FROM modelos_iphone WHERE id = %s AND empresa_id = %s", (modelo_id, empresa_id_logada))

            linhas_afetadas = cursor.rowcount
            print(f"Comando DELETE no modelo principal executado. Linhas afetadas: {linhas_afetadas}")
            print(f"--- FIM DO DELETE ---")

            if linhas_afetadas == 0:
                flash("Atenção: O modelo não foi encontrado com as permissões da sua empresa e não pôde ser deletado.", "warning")
            else:
                flash('Modelo e suas dependências foram deletados com sucesso!', 'success')

        conn.commit()

    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        flash('Erro de banco de dados ao deletar o modelo.', 'danger')
        print(f"Erro de PostgreSQL ao deletar modelo: {e}")

    finally:
        if conn:
            conn.close()

    return redirect(url_for('gerenciar_modelos_admin'))

@app.route('/admin/usuarios')
def gerenciar_usuarios_admin():
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    info_empresa = get_info_empresa_logada()
    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    usuarios_da_empresa = []
    id_do_admin_logado = session.get('user_id')
    if not id_do_admin_logado:
        flash("Usuário não autenticado", "danger")
        return redirect(url_for('login'))
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, nome_completo, usuario as email, is_admin FROM usuarios WHERE empresa_id = %s AND id != %s ORDER BY nome_completo",
            (empresa_id_logada, id_do_admin_logado)
        )
        usuarios_da_empresa = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Ocorreu um erro ao buscar os usuários.', 'danger')
        print(f"Erro ao buscar usuários para admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template(
        'admin_usuarios.html',
        usuarios=usuarios_da_empresa,
        info_empresa=info_empresa,
        is_admin=session.get('is_admin'),
        empresa_pode_gerir=session.get('empresa_pode_gerir'),
        permite_link_convidado=session.get('permite_link_convidado'),
        permite_ajuste_valores=session.get('permite_ajuste_valores')
    )


@app.route('/admin/adicionar-usuario', methods=['GET', 'POST'])
def adicionar_usuario_admin():
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    info_empresa = get_info_empresa_logada()

    if request.method == 'POST':
        empresa_id_logada = session.get('empresa_id')
        if not empresa_id_logada:
            flash("Usuário não está associado a uma empresa válida", "danger")
            return redirect(url_for('login'))

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
        except mysql.connector.Error as e:
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
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    if usuario_id == session['user_id']:
        flash('Você não pode deletar sua própria conta.', 'danger')
        return redirect(url_for('gerenciar_usuarios_admin'))

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('gerenciar_usuarios_admin'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM usuarios WHERE id = %s AND empresa_id = %s", (usuario_id, empresa_id_logada))

        conn.commit()
        flash('Usuário deletado com sucesso.', 'success')
    except mysql.connector.Error as e:
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
    print('DEBUG SESSION:', dict(session))
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    info_empresa = get_info_empresa_logada()
    return render_template(
        'admin_dashboard.html',
        info_empresa=info_empresa,
        is_admin=session.get('is_admin'),
        empresa_pode_gerir=session.get('empresa_pode_gerir')
    )

@app.route('/super-admin')
def super_admin_dashboard():
    print("Rota /super-admin foi chamada")
    resp = require_login() or require_super_admin()
    if resp: return resp

    info_empresa = get_info_empresa_logada()
    empresas_clientes = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM empresas ORDER BY nome_empresa")
        empresas_clientes = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Ocorreu um erro ao buscar os dados do Super Admin.', 'danger')
        print(f"Erro ao buscar empresas para super admin: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('super_admin_dashboard.html', empresas=empresas_clientes, info_empresa=info_empresa)

@app.route('/super-admin/adicionar-empresa', methods=['GET', 'POST'])
def adicionar_empresa_super_admin():
    resp = require_login() or require_super_admin()
    if resp: return resp

    if request.method == 'POST':

        nome_empresa = request.form['nome_empresa']
        cnpj = request.form.get('cnpj')
        email_contato_principal = request.form.get('email_contato_principal')
        nome_responsavel = request.form['nome_responsavel']
        email_admin = request.form['email_admin'].strip().lower()
        senha_admin = request.form['senha_admin']
        limite_usuarios = request.form['max_usuarios']

        plano_ativo = 'plano_ativo' in request.form
        permite_ajustes = 'permite_ajuste_valores' in request.form
        permite_link = 'permite_link_convidado' in request.form
        envia_email = 'envia_email_orcamento' in request.form
        envia_email_link = 'envia_email_orcamento_link' in request.form

        logo_url = None
        if 'logo_empresa' in request.files:
            file = request.files['logo_empresa']
            if file and file.filename:
                filename = secure_filename(file.filename)
                extensao = filename.rsplit('.', 1)[-1].lower()
                tipos_permitidos = {'png', 'jpg', 'jpeg'}
                tamanho_max = 2 * 1024 * 1024  # 2MB
                if extensao not in tipos_permitidos:
                    flash('Apenas arquivos PNG, JPG ou JPEG são permitidos.', 'danger')
                    return redirect(request.url)
                file_bytes = file.read()
                file.seek(0)
                try:
                    img = Image.open(BytesIO(file_bytes))
                    tipo_real = img.format.lower()  # 'jpeg', 'png', etc.
                except Exception:
                    tipo_real = None
                if tipo_real not in tipos_permitidos:
                    flash('O arquivo enviado não é uma imagem válida.', 'danger')
                    return redirect(request.url)
                logos_dir = os.path.join(app.static_folder, 'images', 'logos')
                os.makedirs(logos_dir, exist_ok=True)
                file.save(os.path.join(logos_dir, filename))
                logo_url = f'images/logos/{filename}'

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            sql_insert_empresa = """
                INSERT INTO empresas (nome_empresa, cnpj, nome_responsavel, email_contato_principal, max_usuarios, permite_ajuste_valores, permite_link_convidado, envia_email_orcamento, envia_email_orcamento_link, plano_ativo, logo_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(sql_insert_empresa, (
                nome_empresa, cnpj, nome_responsavel, email_contato_principal, limite_usuarios, permite_ajustes, permite_link, envia_email, envia_email_link, plano_ativo, logo_url
            ))
            nova_empresa_id = cursor.lastrowid
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

        except mysql.connector.Error as e:
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

@app.route('/super-admin/editar-empresa/<int:empresa_id>', methods=['GET', 'POST'])
def editar_empresa_admin(empresa_id):
    # Verificação de segurança para garantir que apenas o Super Admin (empresa ID 1) aceda
    resp = require_login() or require_super_admin()
    if resp: return resp

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            # Pega todos os dados do formulário
            nome_empresa = request.form.get('nome_empresa')
            cnpj = request.form.get('cnpj')
            email_contato = request.form.get('email_contato_principal')
            max_usuarios = request.form.get('max_usuarios', 1, type=int)

            permite_ajustes = int('permite_ajuste_valores' in request.form)
            permite_link = int('permite_link_convidado' in request.form)
            envia_email = 'envia_email_orcamento' in request.form
            envia_email_link = 'envia_email_orcamento_link' in request.form
            plano_ativo = 'plano_ativo' in request.form

            # Processa alteração de senha se fornecida
            nova_senha = request.form.get('nova_senha_admin')
            confirmar_senha = request.form.get('confirmar_senha_admin')

            if nova_senha:
                if nova_senha != confirmar_senha:
                    flash('As senhas não coincidem!', 'danger')
                    return redirect(url_for('editar_empresa_admin', empresa_id=empresa_id))

                if len(nova_senha) < 6:
                    flash('A senha deve ter pelo menos 6 caracteres!', 'danger')
                    return redirect(url_for('editar_empresa_admin', empresa_id=empresa_id))

                # Busca o administrador da empresa
                cursor.execute("SELECT id FROM usuarios WHERE empresa_id = %s AND is_admin = 1 LIMIT 1", (empresa_id,))
                admin = cursor.fetchone()

                if admin:
                    hash_nova_senha = generate_password_hash(nova_senha)
                    cursor.execute("UPDATE usuarios SET senha_hash = %s WHERE id = %s", (hash_nova_senha, admin['id']))
                    flash('Senha do administrador alterada com sucesso!', 'success')
                else:
                    flash('Administrador da empresa não encontrado!', 'warning')

            # Executa o comando UPDATE completo
            sql_update = """
                UPDATE empresas SET
                    nome_empresa = %s, cnpj = %s, email_contato_principal = %s,
                    max_usuarios = %s, permite_ajuste_valores = %s, permite_link_convidado = %s,
                    envia_email_orcamento = %s, envia_email_orcamento_link = %s, plano_ativo = %s
                WHERE id = %s
            """
            cursor.execute(sql_update, (
                nome_empresa, cnpj, email_contato, max_usuarios, permite_ajustes,
                permite_link, envia_email, envia_email_link, plano_ativo, empresa_id
            ))

            conn.commit()
            flash('Empresa atualizada com sucesso!', 'success')
            if session.get('empresa_id') == empresa_id:
                session['permite_ajuste_valores'] = int(permite_ajustes)
                session['permite_link_convidado'] = int(permite_link)
                print('DEBUG SESSION UPDATE:', dict(session))
            return redirect(url_for('super_admin_dashboard'))

        # Lógica GET: Busca os dados atuais da empresa para preencher o formulário
        cursor.execute("SELECT * FROM empresas WHERE id = %s", (empresa_id,))
        empresa = cursor.fetchone()

        if not empresa:
            flash('Empresa não encontrada.', 'warning')
            return redirect(url_for('super_admin_dashboard'))

        return render_template('editar_empresa.html', empresa=empresa)

    except mysql.connector.Error as e:
        if conn: conn.rollback()
        flash('Ocorreu um erro ao interagir com o banco de dados.', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return redirect(url_for('super_admin_dashboard'))

# ===== SISTEMA DE LINKS DE CONVITE =====

@app.route('/admin/gerar-link-convite', methods=['GET', 'POST'])
def gerar_link_convite():
    """Gera um link de convite único para a empresa logada."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id = session['empresa_id']
    usuario_id = session['user_id']

    # Verifica se a empresa permite links de convite
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT permite_link_convidado FROM empresas WHERE id = %s", (empresa_id,))
        empresa = cursor.fetchone()

        if not empresa or not empresa['permite_link_convidado']:
            flash('Sua empresa não tem permissão para gerar links de convite.', 'danger')
            return redirect(url_for('admin_dashboard'))

        if request.method == 'POST':
            # Gera token único
            token = secrets.token_urlsafe(32)

            # Define expiração (30 minutos)
            data_expiracao = datetime.datetime.now() + datetime.timedelta(minutes=30)

            # Insere no banco
            sql_insert = """
                INSERT INTO links_convidados
                (empresa_id, usuario_id, token_unico, data_expiracao)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (empresa_id, usuario_id, token, data_expiracao))
            conn.commit()

            # Gera o link completo
            link_completo = request.host_url.rstrip('/') + url_for('usar_link_convite', token=token)

            flash('Link de convite gerado com sucesso! Válido por 30 minutos.', 'success')
            return redirect(url_for('link_convite_gerado', token=token))

        return render_template('gerar_link_convite.html')

    except mysql.connector.Error as e:
        flash(f'Erro ao gerar link: {e}', 'danger')
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/link-convite-gerado/<token>')
def link_convite_gerado(token):
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp
    return render_template('link_convite_gerado.html', link=request.host_url.rstrip('/') + url_for('usar_link_convite', token=token), token=token)

@app.route('/convite/<token>', methods=['GET', 'POST'])
def usar_link_convite(token):
    """Página para o convidado usar o link e fazer o orçamento."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Busca o link no banco
        cursor.execute("""
            SELECT lc.*, e.nome_empresa, e.email_contato_principal
            FROM links_convidados lc
            JOIN empresas e ON lc.empresa_id = e.id
            WHERE lc.token_unico = %s
        """, (token,))
        link = cursor.fetchone()

        if not link:
            flash('Link de convite inválido ou expirado.', 'danger')
            return redirect(url_for('login'))

        # Verifica se já foi usado
        if link['usado']:
            flash('Este link já foi utilizado.', 'warning')
            return redirect(url_for('login'))

        # Verifica se expirou
        if datetime.datetime.now() > link['data_expiracao']:
            flash('Este link expirou.', 'warning')
            return redirect(url_for('login'))
            
        # Verifica se o plano da empresa está ativo
        cursor.execute("SELECT plano_ativo FROM empresas WHERE id = %s", (link['empresa_id'],))
        empresa = cursor.fetchone()
        if empresa and not empresa['plano_ativo']:
            flash('O plano da empresa está desativado. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('login'))

        if request.method == 'POST':
            # Salva dados do cliente
            nome_cliente = request.form.get('nome_cliente')
            email_cliente = request.form.get('email_cliente')
            telefone_cliente = request.form.get('telefone_cliente')
            modelo_interesse = request.form.get('modelo_interesse')

            # Atualiza o link com os dados do cliente
            cursor.execute("""
                UPDATE links_convidados
                SET nome_cliente = %s, email_cliente = %s, telefone_cliente = %s
                WHERE token_unico = %s
            """, (nome_cliente, email_cliente, telefone_cliente, token))
            conn.commit()
            
            # Armazena o modelo de interesse na sessão para usar no email
            session[f'modelo_interesse_{token}'] = modelo_interesse
            
            # Debug: verificar se os dados foram salvos
            print(f"DEBUG - Dados salvos no link: nome={nome_cliente}, email={email_cliente}, telefone={telefone_cliente}")
            print(f"DEBUG - Modelo de interesse: {modelo_interesse}")

            # Redireciona para a página de cálculo
            return redirect(url_for('calcular_convite', token=token))

        # Busca informações da empresa
        cursor.execute("SELECT nome_empresa, logo_url FROM empresas WHERE id = %s", (link['empresa_id'],))
        empresa = cursor.fetchone()

        return render_template('formulario_convite_modern.html', token=token, empresa=empresa)

    except mysql.connector.Error as e:
        flash(f'Erro ao acessar link: {e}', 'danger')
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))

@app.route('/convite/<token>/calcular', methods=['GET', 'POST'])
def calcular_convite(token):
    """Página de cálculo para convidados."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Busca o link e verifica se é válido
        cursor.execute("""
            SELECT lc.*, e.nome_empresa, e.email_contato_principal, e.logo_url
            FROM links_convidados lc
            JOIN empresas e ON lc.empresa_id = e.id
            WHERE lc.token_unico = %s
        """, (token,))
        link = cursor.fetchone()

        if not link or link['usado'] or datetime.datetime.now() > link['data_expiracao']:
            flash('Link inválido, usado ou expirado.', 'danger')
            return redirect(url_for('login'))
            
        # Verifica se o plano da empresa está ativo
        cursor.execute("SELECT plano_ativo FROM empresas WHERE id = %s", (link['empresa_id'],))
        empresa = cursor.fetchone()
        if empresa and not empresa['plano_ativo']:
            flash('O plano da empresa está desativado. Entre em contato com o administrador.', 'danger')
            return redirect(url_for('login'))

        # Busca modelos da empresa
        cursor.execute("""
            SELECT id, nome_modelo, imagem_padrao_url
            FROM modelos_iphone
            WHERE empresa_id = %s
            ORDER BY id
        """, (link['empresa_id'],))
        modelos = cursor.fetchall()

        return render_template('calcular_convite.html', token=token, modelos=modelos, link=link)

    except mysql.connector.Error as e:
        flash(f'Erro ao carregar dados: {e}', 'danger')
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))

@app.route('/convite/<token>/api/modelo/<int:modelo_id>/perguntas')
def get_perguntas_modelo_convite(token, modelo_id):
    """API para buscar perguntas do modelo (versão para convidados)."""
    print(f"DEBUG: Acessando rota de perguntas para token={token}, modelo_id={modelo_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verifica se o link é válido
        cursor.execute("SELECT empresa_id FROM links_convidados WHERE token_unico = %s AND usado = FALSE", (token,))
        link = cursor.fetchone()
        
        # Consumir resultados pendentes para evitar "Unread result found"
        cursor.fetchall()

        if not link:
            print(f"DEBUG: Link inválido para token={token}")
            return jsonify({"erro": "Link inválido"}), 401

        empresa_id = link['empresa_id']
        print(f"DEBUG: Empresa ID encontrada: {empresa_id}")
        
        # Verifica se o plano da empresa está ativo
        cursor.execute("SELECT plano_ativo FROM empresas WHERE id = %s", (empresa_id,))
        empresa = cursor.fetchone()
        
        # Consumir resultados pendentes para evitar "Unread result found"
        cursor.fetchall()
        
        if empresa and not empresa['plano_ativo']:
            print(f"DEBUG: Plano da empresa {empresa_id} está desativado")
            return jsonify({"erro": "O plano da empresa está desativado"}), 403

        # Busca todas as perguntas de avaliação incluindo informações condicionais (GLOBAIS)
        # Ordena de forma que perguntas condicionais apareçam logo após suas perguntas pai
        cursor.execute("""
            SELECT
                p.id AS pergunta_id,
                p.texto_pergunta,
                p.pergunta_pai_id,
                p.resposta_pai_requerida,
                CASE 
                    WHEN p.pergunta_pai_id IS NULL THEN p.id
                    ELSE p.pergunta_pai_id + 0.5
                END as ordem_exibicao
            FROM perguntas_avaliacao p
            ORDER BY ordem_exibicao, p.id
        """)

        todas_perguntas = cursor.fetchall()
        print(f"DEBUG: Encontradas {len(todas_perguntas)} perguntas (globais) ordenadas")
        
        # Consumir resultados pendentes para evitar "Unread result found"
        cursor.fetchall()
        
        perguntas = []

        for pergunta in todas_perguntas:
            pergunta_id = pergunta['pergunta_id']

            # Busca as respostas existentes para esta pergunta e modelo
            cursor.execute("""
                SELECT
                    ir.resposta_que_gera_impacto,
                    ir.valor_do_impacto
                FROM impacto_respostas ir
                WHERE ir.pergunta_id = %s AND ir.modelo_id = %s AND ir.empresa_id = %s
            """, (pergunta_id, modelo_id, empresa_id))

            respostas_existentes = cursor.fetchall()
            
            # Consumir resultados pendentes para evitar "Unread result found"
            cursor.fetchall()

            # Cria um dicionário para facilitar a busca
            respostas_dict = {r['resposta_que_gera_impacto']: r['valor_do_impacto'] for r in respostas_existentes}

            # Garante que sempre tenha as duas opções
            respostas = []

            # Adiciona resposta "Sim"
            impacto_sim = respostas_dict.get('Sim', 0.0)
            respostas.append({
                'texto': 'Sim',
                'impacto': float(impacto_sim)
            })

            # Adiciona resposta "Não"
            impacto_nao = respostas_dict.get('Não', 0.0)
            respostas.append({
                'texto': 'Não',
                'impacto': float(impacto_nao)
            })

            pergunta_obj = {
                'pergunta_id': pergunta_id,
                'texto_pergunta': pergunta['texto_pergunta'],
                'respostas': respostas
            }
            
            # Adicionar informações condicionais se existirem
            if pergunta['pergunta_pai_id']:
                pergunta_obj['pergunta_pai_id'] = pergunta['pergunta_pai_id']
                pergunta_obj['resposta_pai_requerida'] = pergunta['resposta_pai_requerida']
            
            perguntas.append(pergunta_obj)

        print(f"DEBUG: Retornando {len(perguntas)} perguntas")
        return jsonify(perguntas)

    except Exception as e:
        print(f"Erro ao buscar perguntas: {e}")
        return jsonify({"erro": "Falha ao buscar perguntas"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/convite/<token>/api/modelo/<int:modelo_id>/opcoes')
def get_opcoes_modelo_convite(token, modelo_id):
    """API para buscar opções do modelo (versão para convidados)."""
    print(f"DEBUG: Acessando rota de opções para token={token}, modelo_id={modelo_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verifica se o link é válido
        cursor.execute("SELECT empresa_id FROM links_convidados WHERE token_unico = %s AND usado = FALSE", (token,))
        link = cursor.fetchone()

        if not link:
            print(f"DEBUG: Link inválido para token={token}")
            return jsonify({"erro": "Link inválido"}), 401

        empresa_id = link['empresa_id']
        print(f"DEBUG: Empresa ID encontrada: {empresa_id}")
        
        # Verifica se o plano da empresa está ativo
        cursor.execute("SELECT plano_ativo FROM empresas WHERE id = %s", (empresa_id,))
        empresa = cursor.fetchone()
        if empresa and not empresa['plano_ativo']:
            print(f"DEBUG: Plano da empresa {empresa_id} está desativado")
            return jsonify({"erro": "O plano da empresa está desativado"}), 403

        opcoes = {
            "modelo_info": None,
            "cores": [],
            "armazenamentos": []
        }

        # Busca informações do modelo
        sql_modelo = "SELECT nome_modelo, valor_base_novo FROM modelos_iphone WHERE id = %s AND empresa_id = %s"
        cursor.execute(sql_modelo, (modelo_id, empresa_id))
        modelo_info_row = cursor.fetchone()

        if not modelo_info_row:
            print(f"DEBUG: Modelo {modelo_id} não encontrado para empresa {empresa_id}")
            return jsonify({"erro": "Modelo não encontrado"}), 404

        opcoes['modelo_info'] = modelo_info_row
        print(f"DEBUG: Modelo encontrado: {modelo_info_row}")

        # Busca cores
        sql_cores = """
            SELECT c.id, c.nome_cor, c.codigo_hex, mc.imagem_url
            FROM cores c
            JOIN modelos_cores mc ON c.id = mc.cor_id
            WHERE mc.modelo_id = %s AND mc.empresa_id = %s
        """
        cursor.execute(sql_cores, (modelo_id, empresa_id))
        opcoes["cores"] = cursor.fetchall()
        print(f"DEBUG: Encontradas {len(opcoes['cores'])} cores")

        # Busca armazenamentos
        sql_armazenamentos = """
            SELECT a.id, a.capacidade_gb, ma.modificador_valor
            FROM armazenamentos a
            JOIN modelos_armazenamentos ma ON a.id = ma.armazenamento_id
            WHERE ma.modelo_id = %s AND ma.empresa_id = %s
        """
        cursor.execute(sql_armazenamentos, (modelo_id, empresa_id))
        opcoes["armazenamentos"] = cursor.fetchall()
        print(f"DEBUG: Encontrados {len(opcoes['armazenamentos'])} armazenamentos")

        return jsonify(opcoes)

    except mysql.connector.Error as e:
        print(f"DEBUG: Erro MySQL: {e}")
        return jsonify({"erro": "Erro no servidor"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

# ===== SISTEMA DE RELATÓRIOS =====

@app.route('/admin/relatorios')
def relatorios_dashboard():
    """Dashboard principal de relatórios com resumo geral."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    info_empresa = get_info_empresa_logada()
    
    conn = None
    dados_dashboard = {
        'total_avaliacoes': 0,
        'valor_medio': 0,
        'modelo_mais_avaliado': 'N/A',
        'crescimento_mensal': 0,
        'avaliacoes_por_modelo': [],
        'avaliacoes_recentes': [],
        'kpis': {}
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Total de avaliações
        cursor.execute("""
            SELECT COUNT(*) as total FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        dados_dashboard['total_avaliacoes'] = cursor.fetchone()['total']

        # Valor médio das avaliações
        cursor.execute("""
            SELECT AVG(valor_final_calculado) as media FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        resultado = cursor.fetchone()
        dados_dashboard['valor_medio'] = float(resultado['media']) if resultado['media'] else 0

        # Modelo mais avaliado
        cursor.execute("""
            SELECT mi.nome_modelo, COUNT(*) as quantidade
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            WHERE ac.empresa_id = %s
            GROUP BY mi.nome_modelo
            ORDER BY quantidade DESC
            LIMIT 1
        """, (empresa_id_logada,))
        modelo_top = cursor.fetchone()
        if modelo_top:
            dados_dashboard['modelo_mais_avaliado'] = modelo_top['nome_modelo']

        # Avaliações por modelo para o gráfico pizza
        cursor.execute("""
            SELECT mi.nome_modelo, COUNT(*) as quantidade
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            WHERE ac.empresa_id = %s
            GROUP BY mi.nome_modelo
            ORDER BY quantidade DESC
        """, (empresa_id_logada,))
        dados_dashboard['avaliacoes_por_modelo'] = cursor.fetchall()

        # Crescimento mensal (comparação com mês anterior)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN MONTH(data_avaliacao) = MONTH(NOW()) AND YEAR(data_avaliacao) = YEAR(NOW()) THEN 1 END) as mes_atual,
                COUNT(CASE WHEN MONTH(data_avaliacao) = MONTH(NOW() - INTERVAL 1 MONTH) AND YEAR(data_avaliacao) = YEAR(NOW() - INTERVAL 1 MONTH) THEN 1 END) as mes_anterior
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        crescimento = cursor.fetchone()
        if crescimento and crescimento['mes_anterior'] > 0:
            dados_dashboard['crescimento_mensal'] = round(
                ((crescimento['mes_atual'] - crescimento['mes_anterior']) / crescimento['mes_anterior']) * 100, 1
            )

        # Avaliações recentes (últimas 5)
        cursor.execute("""
            SELECT ac.nome_cliente_final, mi.nome_modelo, ac.valor_final_calculado, 
                   ac.data_avaliacao, ac.cor_selecionada
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            WHERE ac.empresa_id = %s
            ORDER BY ac.data_avaliacao DESC
            LIMIT 5
        """, (empresa_id_logada,))
        dados_dashboard['avaliacoes_recentes'] = cursor.fetchall()

        # KPIs adicionais
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                AVG(valor_final_calculado) as valor_medio,
                MIN(valor_final_calculado) as menor_valor,
                MAX(valor_final_calculado) as maior_valor,
                COUNT(DISTINCT modelo_iphone_id) as modelos_diferentes,
                COUNT(CASE WHEN DATE(data_avaliacao) = CURDATE() THEN 1 END) as avaliacoes_hoje,
                COUNT(CASE WHEN WEEK(data_avaliacao) = WEEK(NOW()) AND YEAR(data_avaliacao) = YEAR(NOW()) THEN 1 END) as avaliacoes_semana
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        dados_dashboard['kpis'] = cursor.fetchone()

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados dos relatórios.', 'danger')
        print(f"Erro ao buscar dados do dashboard: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template('admin_relatorios_dashboard.html', 
                         dados=dados_dashboard, 
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

@app.route('/admin/relatorios/api/dados-grafico')
def api_dados_grafico():
    """API para fornecer dados do gráfico pizza."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        return jsonify({"erro": "Usuário não está associado a uma empresa válida"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT mi.nome_modelo as label, COUNT(*) as value
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            WHERE ac.empresa_id = %s
            GROUP BY mi.nome_modelo
            ORDER BY value DESC
        """, (empresa_id_logada,))
        
        dados = cursor.fetchall()
        return jsonify(dados)

    except mysql.connector.Error as e:
        return jsonify({"erro": "Erro ao buscar dados"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

@app.route('/admin/relatorios/avaliacoes')
def relatorios_avaliacoes():
    """Relatório detalhado de avaliações concluídas."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    # Parâmetros de filtro
    modelo_filtro = request.args.get('modelo', '')
    usuario_filtro = request.args.get('usuario', '')
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    conn = None
    avaliacoes = []
    modelos_disponiveis = []
    usuarios_disponiveis = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar modelos para filtro
        cursor.execute("""
            SELECT DISTINCT nome_modelo FROM modelos_iphone 
            WHERE empresa_id = %s ORDER BY nome_modelo
        """, (empresa_id_logada,))
        modelos_disponiveis = cursor.fetchall()

        # Buscar usuários para filtro
        cursor.execute("""
            SELECT DISTINCT u.nome_completo, u.id 
            FROM usuarios u
            JOIN avaliacoes_concluidas ac ON u.id = ac.usuario_id
            WHERE u.empresa_id = %s ORDER BY u.nome_completo
        """, (empresa_id_logada,))
        usuarios_disponiveis = cursor.fetchall()

        # Construir query com filtros
        where_conditions = ["ac.empresa_id = %s"]
        params = [empresa_id_logada]

        if modelo_filtro:
            where_conditions.append("mi.nome_modelo = %s")
            params.append(modelo_filtro)

        if usuario_filtro:
            where_conditions.append("u.nome_completo = %s")
            params.append(usuario_filtro)

        if data_inicio:
            where_conditions.append("DATE(ac.data_avaliacao) >= %s")
            params.append(data_inicio)

        if data_fim:
            where_conditions.append("DATE(ac.data_avaliacao) <= %s")
            params.append(data_fim)

        where_clause = " AND ".join(where_conditions)

        # Buscar avaliações com filtros
        cursor.execute(f"""
            SELECT ac.*, mi.nome_modelo, u.nome_completo as nome_usuario,
                   DATE_FORMAT(ac.data_avaliacao, '%d/%m/%Y %H:%i') as data_formatada
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            LEFT JOIN usuarios u ON ac.usuario_id = u.id
            WHERE {where_clause}
            ORDER BY ac.data_avaliacao DESC
            LIMIT 100
        """, params)
        
        avaliacoes = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar avaliações.', 'danger')
        print(f"Erro ao buscar avaliações: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    return render_template('admin_relatorios_avaliacoes.html',
                         avaliacoes=avaliacoes,
                         modelos_disponiveis=modelos_disponiveis,
                         usuarios_disponiveis=usuarios_disponiveis,
                         filtros={
                             'modelo': modelo_filtro,
                             'usuario': usuario_filtro,
                             'data_inicio': data_inicio,
                             'data_fim': data_fim
                         },
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

@app.route('/admin/relatorios/usuarios')
def relatorios_usuarios():
    """Relatório de performance por usuário."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    conn = None
    dados_usuarios = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                u.nome_completo,
                u.usuario as email,
                COUNT(ac.id) as total_avaliacoes,
                AVG(ac.valor_final_calculado) as valor_medio,
                MIN(ac.valor_final_calculado) as menor_valor,
                MAX(ac.valor_final_calculado) as maior_valor,
                MAX(ac.data_avaliacao) as ultima_avaliacao
            FROM usuarios u
            LEFT JOIN avaliacoes_concluidas ac ON u.id = ac.usuario_id
            WHERE u.empresa_id = %s
            GROUP BY u.id, u.nome_completo, u.usuario
            ORDER BY total_avaliacoes DESC
        """, (empresa_id_logada,))
        
        dados_usuarios = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados dos usuários.', 'danger')
        print(f"Erro MySQL ao buscar dados de usuários: {e}")
    except Exception as e:
        flash('Erro inesperado ao carregar relatório de usuários.', 'danger')
        print(f"Erro inesperado na rota relatorios_usuarios: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    
    try:
        return render_template('admin_relatorios_usuarios.html',
                             dados_usuarios=dados_usuarios,
                             info_empresa=info_empresa,
                             is_admin=session.get('is_admin'),
                             empresa_pode_gerir=session.get('empresa_pode_gerir'))
    except Exception as e:
        print(f"Erro no template admin_relatorios_usuarios.html: {e}")
        flash('Erro ao carregar template de relatórios.', 'danger')
        return redirect(url_for('relatorios_dashboard'))

@app.route('/admin/relatorios/financeiro')
def relatorios_financeiro():
    """Relatório de análise financeira."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    conn = None
    dados_financeiros = {
        'resumo_geral': {},
        'por_modelo': [],
        'evolucao_mensal': []
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Resumo geral
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                SUM(valor_final_calculado) as valor_total,
                AVG(valor_final_calculado) as valor_medio,
                MIN(valor_final_calculado) as menor_valor,
                MAX(valor_final_calculado) as maior_valor,
                AVG(valor_base_calculado) as valor_base_medio,
                AVG(valor_final_calculado - valor_base_calculado) as depreciacao_media
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        dados_financeiros['resumo_geral'] = cursor.fetchone()

        # Análise por modelo
        cursor.execute("""
            SELECT 
                mi.nome_modelo,
                COUNT(*) as quantidade,
                AVG(ac.valor_final_calculado) as valor_medio,
                AVG(ac.valor_base_calculado) as valor_base_medio,
                AVG(ac.valor_final_calculado - ac.valor_base_calculado) as depreciacao_media,
                (AVG(ac.valor_final_calculado - ac.valor_base_calculado) / AVG(ac.valor_base_calculado)) * 100 as percentual_depreciacao
            FROM avaliacoes_concluidas ac
            JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
            WHERE ac.empresa_id = %s
            GROUP BY mi.nome_modelo
            ORDER BY quantidade DESC
        """, (empresa_id_logada,))
        dados_financeiros['por_modelo'] = cursor.fetchall()

        # Evolução mensal
        cursor.execute("""
            SELECT 
                DATE_FORMAT(data_avaliacao, '%Y-%m') as mes,
                COUNT(*) as quantidade,
                AVG(valor_final_calculado) as valor_medio,
                SUM(valor_final_calculado) as valor_total
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
            GROUP BY DATE_FORMAT(data_avaliacao, '%Y-%m')
            ORDER BY mes DESC
            LIMIT 12
        """, (empresa_id_logada,))
        dados_financeiros['evolucao_mensal'] = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados financeiros.', 'danger')
        print(f"Erro ao buscar dados financeiros: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    return render_template('admin_relatorios_financeiro.html',
                         dados=dados_financeiros,
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

@app.route('/admin/relatorios/tendencias')
def relatorios_tendencias():
    """Relatório de tendências temporais."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    conn = None
    dados_tendencias = {
        'avaliacoes_por_dia': [],
        'cores_populares': [],
        'armazenamentos_populares': [],
        'horarios_pico': []
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Avaliações por dia (últimos 30 dias)
        cursor.execute("""
            SELECT 
                DATE(data_avaliacao) as data,
                COUNT(*) as quantidade
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s AND data_avaliacao >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(data_avaliacao)
            ORDER BY data DESC
        """, (empresa_id_logada,))
        dados_tendencias['avaliacoes_por_dia'] = cursor.fetchall()

        # Cores mais populares
        cursor.execute("""
            SELECT 
                cor_selecionada,
                COUNT(*) as quantidade
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
            GROUP BY cor_selecionada
            ORDER BY quantidade DESC
            LIMIT 10
        """, (empresa_id_logada,))
        dados_tendencias['cores_populares'] = cursor.fetchall()

        # Armazenamentos mais populares
        cursor.execute("""
            SELECT 
                armazenamento_selecionado,
                COUNT(*) as quantidade
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
            GROUP BY armazenamento_selecionado
            ORDER BY quantidade DESC
        """, (empresa_id_logada,))
        dados_tendencias['armazenamentos_populares'] = cursor.fetchall()

        # Horários de pico
        cursor.execute("""
            SELECT 
                HOUR(data_avaliacao) as hora,
                COUNT(*) as quantidade
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s
            GROUP BY HOUR(data_avaliacao)
            ORDER BY quantidade DESC
        """, (empresa_id_logada,))
        dados_tendencias['horarios_pico'] = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados de tendências.', 'danger')
        print(f"Erro ao buscar dados de tendências: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    return render_template('admin_relatorios_tendencias.html',
                         dados=dados_tendencias,
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

# ===== SISTEMA DE EXPORTAÇÃO DE RELATÓRIOS =====

@app.route('/admin/relatorios/exportar/<tipo>')
def exportar_relatorio(tipo):
    """Exporta relatórios em diferentes formatos."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        return jsonify({"erro": "Usuário não está associado a uma empresa válida"}), 400

    formato = request.args.get('formato', 'csv')  # csv, excel, pdf
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if tipo == 'avaliacoes':
            # Aplicar filtros da URL
            modelo_filtro = request.args.get('modelo', '')
            usuario_filtro = request.args.get('usuario', '')
            data_inicio = request.args.get('data_inicio', '')
            data_fim = request.args.get('data_fim', '')
            
            where_conditions = ["ac.empresa_id = %s"]
            params = [empresa_id_logada]

            if modelo_filtro:
                where_conditions.append("mi.nome_modelo = %s")
                params.append(modelo_filtro)
            if usuario_filtro:
                where_conditions.append("u.nome_completo = %s")
                params.append(usuario_filtro)
            if data_inicio:
                where_conditions.append("DATE(ac.data_avaliacao) >= %s")
                params.append(data_inicio)
            if data_fim:
                where_conditions.append("DATE(ac.data_avaliacao) <= %s")
                params.append(data_fim)

            where_clause = " AND ".join(where_conditions)

            cursor.execute(f"""
                SELECT 
                    ac.nome_cliente_final as 'Cliente',
                    ac.email_cliente_final as 'Email',
                    ac.telefone_cliente_final as 'Telefone',
                    mi.nome_modelo as 'Modelo',
                    ac.cor_selecionada as 'Cor',
                    ac.armazenamento_selecionado as 'Armazenamento',
                    ac.valor_base_calculado as 'Valor Base',
                    ac.valor_final_calculado as 'Valor Final',
                    u.nome_completo as 'Usuário',
                    DATE_FORMAT(ac.data_avaliacao, '%d/%m/%Y %H:%i') as 'Data',
                    ac.imei as 'IMEI'
                FROM avaliacoes_concluidas ac
                JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
                LEFT JOIN usuarios u ON ac.usuario_id = u.id
                WHERE {where_clause}
                ORDER BY ac.data_avaliacao DESC
                LIMIT 1000
            """, params)
            
        elif tipo == 'usuarios':
            cursor.execute("""
                SELECT 
                    u.nome_completo as 'Usuário',
                    u.usuario as 'Email',
                    COUNT(ac.id) as 'Total Avaliações',
                    COALESCE(AVG(ac.valor_final_calculado), 0) as 'Valor Médio',
                    COALESCE(MIN(ac.valor_final_calculado), 0) as 'Menor Valor',
                    COALESCE(MAX(ac.valor_final_calculado), 0) as 'Maior Valor',
                    MAX(ac.data_avaliacao) as 'Última Avaliação'
                FROM usuarios u
                LEFT JOIN avaliacoes_concluidas ac ON u.id = ac.usuario_id
                WHERE u.empresa_id = %s
                GROUP BY u.id, u.nome_completo, u.usuario
                ORDER BY COUNT(ac.id) DESC
            """, (empresa_id_logada,))

        elif tipo == 'financeiro':
            cursor.execute("""
                SELECT 
                    mi.nome_modelo as 'Modelo',
                    COUNT(*) as 'Quantidade',
                    AVG(ac.valor_final_calculado) as 'Valor Médio Final',
                    AVG(ac.valor_base_calculado) as 'Valor Base Médio',
                    AVG(ac.valor_final_calculado - ac.valor_base_calculado) as 'Depreciação Média',
                    (AVG(ac.valor_final_calculado - ac.valor_base_calculado) / AVG(ac.valor_base_calculado)) * 100 as 'Percentual Depreciação'
                FROM avaliacoes_concluidas ac
                JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id
                WHERE ac.empresa_id = %s
                GROUP BY mi.nome_modelo
                ORDER BY COUNT(*) DESC
            """, (empresa_id_logada,))

        dados = cursor.fetchall()

        if formato == 'csv':
            return gerar_csv(dados, tipo)
        elif formato == 'excel':
            return gerar_excel(dados, tipo)
        elif formato == 'pdf':
            return gerar_pdf(dados, tipo)
        else:
            return jsonify({"erro": "Formato não suportado"}), 400

    except mysql.connector.Error as e:
        print(f"Erro ao exportar dados: {e}")
        return jsonify({"erro": "Erro ao buscar dados"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

def gerar_csv(dados, tipo):
    """Gera arquivo CSV."""
    from flask import Response
    import csv
    from io import StringIO
    
    output = StringIO()
    
    if dados:
        writer = csv.DictWriter(output, fieldnames=dados[0].keys())
        writer.writeheader()
        
        for linha in dados:
            # Converter valores None e formatar números
            linha_limpa = {}
            for key, value in linha.items():
                if value is None:
                    linha_limpa[key] = ''
                elif isinstance(value, float):
                    linha_limpa[key] = f"{value:.2f}"
                else:
                    linha_limpa[key] = str(value)
            writer.writerow(linha_limpa)
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=relatorio_{tipo}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )

def gerar_excel(dados, tipo):
    """Gera arquivo Excel (simulado como CSV por simplicidade)."""
    # Para implementação completa, usar openpyxl
    return gerar_csv(dados, tipo)

def gerar_pdf(dados, tipo):
    """Gera arquivo PDF (simulado como texto por simplicidade)."""
    from flask import Response
    
    conteudo = f"RELATÓRIO {tipo.upper()}\n"
    conteudo += f"Gerado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
    conteudo += "="*50 + "\n\n"
    
    if dados:
        # Cabeçalhos
        headers = list(dados[0].keys())
        conteudo += " | ".join(headers) + "\n"
        conteudo += "-" * (len(" | ".join(headers))) + "\n"
        
        # Dados
        for linha in dados:
            valores = []
            for value in linha.values():
                if value is None:
                    valores.append("N/A")
                elif isinstance(value, float):
                    valores.append(f"{value:.2f}")
                else:
                    valores.append(str(value))
            conteudo += " | ".join(valores) + "\n"
    
    return Response(
        conteudo,
        mimetype='text/plain',
        headers={
            'Content-Disposition': f'attachment; filename=relatorio_{tipo}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        }
    )

# ===== RELATÓRIO DE LINKS DE CONVITE =====

@app.route('/admin/relatorios/convites')
def relatorios_convites():
    """Relatório de links de convite."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    conn = None
    dados_convites = {
        'resumo': {},
        'links_ativos': [],
        'links_usados': [],
        'links_expirados': [],
        'estatisticas': {}
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Resumo geral
        cursor.execute("""
            SELECT 
                COUNT(*) as total_links,
                COUNT(CASE WHEN usado = 1 THEN 1 END) as links_usados,
                COUNT(CASE WHEN usado = 0 AND data_expiracao > NOW() THEN 1 END) as links_ativos,
                COUNT(CASE WHEN usado = 0 AND data_expiracao <= NOW() THEN 1 END) as links_expirados,
                (COUNT(CASE WHEN usado = 1 THEN 1 END) / COUNT(*)) * 100 as taxa_conversao
            FROM links_convidados 
            WHERE empresa_id = %s
        """, (empresa_id_logada,))
        dados_convites['resumo'] = cursor.fetchone()

        # Links ativos
        cursor.execute("""
            SELECT lc.*, u.nome_completo as criado_por,
                   TIMESTAMPDIFF(HOUR, NOW(), lc.data_expiracao) as horas_restantes
            FROM links_convidados lc
            JOIN usuarios u ON lc.usuario_id = u.id
            WHERE lc.empresa_id = %s AND lc.usado = 0 AND lc.data_expiracao > NOW()
            ORDER BY lc.data_expiracao ASC
        """, (empresa_id_logada,))
        dados_convites['links_ativos'] = cursor.fetchall()

        # Links usados (últimos 20)
        cursor.execute("""
            SELECT lc.*, u.nome_completo as criado_por
            FROM links_convidados lc
            JOIN usuarios u ON lc.usuario_id = u.id
            WHERE lc.empresa_id = %s AND lc.usado = 1
            ORDER BY lc.data_uso DESC
            LIMIT 20
        """, (empresa_id_logada,))
        dados_convites['links_usados'] = cursor.fetchall()

        # Estatísticas por usuário
        cursor.execute("""
            SELECT 
                u.nome_completo,
                COUNT(lc.id) as links_criados,
                COUNT(CASE WHEN lc.usado = 1 THEN 1 END) as links_convertidos,
                (COUNT(CASE WHEN lc.usado = 1 THEN 1 END) / COUNT(lc.id)) * 100 as taxa_conversao_usuario
            FROM usuarios u
            LEFT JOIN links_convidados lc ON u.id = lc.usuario_id
            WHERE u.empresa_id = %s
            GROUP BY u.id, u.nome_completo
            HAVING COUNT(lc.id) > 0
            ORDER BY links_convertidos DESC
        """, (empresa_id_logada,))
        dados_convites['estatisticas'] = cursor.fetchall()

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados dos convites.', 'danger')
        print(f"Erro ao buscar dados de convites: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    return render_template('admin_relatorios_convites.html',
                         dados=dados_convites,
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

# ===== SISTEMA DE COMPARATIVOS =====

@app.route('/admin/relatorios/comparativos')
def relatorios_comparativos():
    """Relatório de comparativos entre períodos."""
    resp = require_login() or require_admin() or require_empresa_permissao()
    if resp: return resp

    empresa_id_logada = session.get('empresa_id')
    if not empresa_id_logada:
        flash("Usuário não está associado a uma empresa válida", "danger")
        return redirect(url_for('login'))

    # Parâmetros de comparação
    periodo1_inicio = request.args.get('periodo1_inicio', '')
    periodo1_fim = request.args.get('periodo1_fim', '')
    periodo2_inicio = request.args.get('periodo2_inicio', '')
    periodo2_fim = request.args.get('periodo2_fim', '')

    # Se não especificado, comparar mês atual vs mês anterior
    if not all([periodo1_inicio, periodo1_fim, periodo2_inicio, periodo2_fim]):
        hoje = datetime.datetime.now()
        primeiro_dia_mes_atual = hoje.replace(day=1)
        ultimo_dia_mes_atual = hoje
        
        primeiro_dia_mes_anterior = (primeiro_dia_mes_atual - datetime.timedelta(days=1)).replace(day=1)
        ultimo_dia_mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)
        
        periodo1_inicio = primeiro_dia_mes_atual.strftime('%Y-%m-%d')
        periodo1_fim = ultimo_dia_mes_atual.strftime('%Y-%m-%d')
        periodo2_inicio = primeiro_dia_mes_anterior.strftime('%Y-%m-%d')
        periodo2_fim = ultimo_dia_mes_anterior.strftime('%Y-%m-%d')

    conn = None
    dados_comparativos = {
        'periodo1': {'inicio': periodo1_inicio, 'fim': periodo1_fim, 'dados': {}},
        'periodo2': {'inicio': periodo2_inicio, 'fim': periodo2_fim, 'dados': {}},
        'comparacao': {}
    }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Dados do período 1
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                AVG(valor_final_calculado) as valor_medio,
                SUM(valor_final_calculado) as valor_total,
                COUNT(DISTINCT modelo_iphone_id) as modelos_diferentes,
                COUNT(DISTINCT CASE WHEN usuario_id IS NOT NULL THEN usuario_id END) as usuarios_ativos
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s AND DATE(data_avaliacao) BETWEEN %s AND %s
        """, (empresa_id_logada, periodo1_inicio, periodo1_fim))
        dados_comparativos['periodo1']['dados'] = cursor.fetchone()

        # Dados do período 2
        cursor.execute("""
            SELECT 
                COUNT(*) as total_avaliacoes,
                AVG(valor_final_calculado) as valor_medio,
                SUM(valor_final_calculado) as valor_total,
                COUNT(DISTINCT modelo_iphone_id) as modelos_diferentes,
                COUNT(DISTINCT CASE WHEN usuario_id IS NOT NULL THEN usuario_id END) as usuarios_ativos
            FROM avaliacoes_concluidas 
            WHERE empresa_id = %s AND DATE(data_avaliacao) BETWEEN %s AND %s
        """, (empresa_id_logada, periodo2_inicio, periodo2_fim))
        dados_comparativos['periodo2']['dados'] = cursor.fetchone()

        # Calcular comparações percentuais
        p1 = dados_comparativos['periodo1']['dados']
        p2 = dados_comparativos['periodo2']['dados']
        
        dados_comparativos['comparacao'] = {
            'avaliacoes': calcular_variacao(p1['total_avaliacoes'], p2['total_avaliacoes']),
            'valor_medio': calcular_variacao(p1['valor_medio'] or 0, p2['valor_medio'] or 0),
            'valor_total': calcular_variacao(p1['valor_total'] or 0, p2['valor_total'] or 0),
            'modelos': calcular_variacao(p1['modelos_diferentes'], p2['modelos_diferentes']),
            'usuarios': calcular_variacao(p1['usuarios_ativos'], p2['usuarios_ativos'])
        }

    except mysql.connector.Error as e:
        flash('Erro ao carregar dados comparativos.', 'danger')
        print(f"Erro ao buscar dados comparativos: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

    info_empresa = get_info_empresa_logada()
    return render_template('admin_relatorios_comparativos.html',
                         dados=dados_comparativos,
                         info_empresa=info_empresa,
                         is_admin=session.get('is_admin'),
                         empresa_pode_gerir=session.get('empresa_pode_gerir'))

def calcular_variacao(valor_atual, valor_anterior):
    """Calcula a variação percentual entre dois valores."""
    if valor_anterior == 0:
        return {'percentual': 0, 'tipo': 'neutro', 'valor_atual': valor_atual, 'valor_anterior': valor_anterior}
    
    variacao = ((valor_atual - valor_anterior) / valor_anterior) * 100
    tipo = 'positivo' if variacao > 0 else 'negativo' if variacao < 0 else 'neutro'
    
    return {
        'percentual': round(variacao, 1),
        'tipo': tipo,
        'valor_atual': valor_atual,
        'valor_anterior': valor_anterior
    }

@app.route('/admin/relatorios/detalhes-avaliacao/<int:avaliacao_id>')
def detalhes_avaliacao(avaliacao_id):
    """Retorna detalhes completos de uma avaliação específica."""
    if not session.get('user_id') or not session.get('is_admin'):
        return jsonify({'erro': 'Acesso negado'}), 403
    
    empresa_id_logada = session.get('empresa_id')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Primeiro, vamos verificar se a avaliação existe
        cursor.execute("SELECT * FROM avaliacoes_concluidas WHERE id = %s AND empresa_id = %s", 
                      (avaliacao_id, empresa_id_logada))
        avaliacao_basica = cursor.fetchone()
        
        if not avaliacao_basica:
            return jsonify({'erro': 'Avaliação não encontrada'}), 404
        
        # Agora buscar dados completos com joins
        query = """
            SELECT 
                ac.*,
                mi.nome_modelo as modelo_nome,
                mi.valor_base_novo as modelo_valor_base,
                u.nome_completo as usuario_nome,
                e.nome_empresa
            FROM avaliacoes_concluidas ac
            LEFT JOIN modelos_iphone mi ON ac.modelo_iphone_id = mi.id AND ac.empresa_id = mi.empresa_id
            LEFT JOIN usuarios u ON ac.usuario_id = u.id
            LEFT JOIN empresas e ON ac.empresa_id = e.id
            WHERE ac.id = %s AND ac.empresa_id = %s
        """
        cursor.execute(query, (avaliacao_id, empresa_id_logada))
        avaliacao = cursor.fetchone()
        
        if not avaliacao:
            # Se não encontrou com joins, usar dados básicos
            avaliacao = avaliacao_basica
            avaliacao['modelo_nome'] = 'N/A'
            avaliacao['usuario_nome'] = None
            avaliacao['nome_empresa'] = 'N/A'
        
        # Buscar histórico de modificações de preço (se existir)
        historico_precos = []
        try:
            if avaliacao['valor_base_calculado'] != avaliacao['valor_final_calculado']:
                historico_precos.append({
                    'tipo': 'Valor Base',
                    'valor': float(avaliacao['valor_base_calculado']),
                    'descricao': 'Valor inicial do modelo'
                })
                historico_precos.append({
                    'tipo': 'Valor Final',
                    'valor': float(avaliacao['valor_final_calculado']),
                    'descricao': 'Valor após aplicação dos impactos'
                })
        except (TypeError, ValueError) as e:
            print(f"Erro ao processar valores: {e}")
            historico_precos = []
        
        # Processar resumo de respostas
        try:
            if avaliacao['resumo_respostas']:
                resumo_respostas = json.loads(avaliacao['resumo_respostas'])
                
                # Verificar se é uma lista ou dicionário
                if isinstance(resumo_respostas, list):
                    # Se for uma lista, converter para dicionário
                    resumo_respostas_limpo = {}
                    for i, item in enumerate(resumo_respostas):
                        if isinstance(item, dict):
                            # Se cada item da lista for um dicionário, tentar extrair pergunta e resposta
                            if 'pergunta' in item and 'resposta' in item:
                                resumo_respostas_limpo[item['pergunta']] = str(item['resposta'])
                            elif 'resposta' in item:
                                resumo_respostas_limpo[f'Pergunta {i+1}'] = str(item['resposta'])
                            else:
                                resumo_respostas_limpo[f'Pergunta {i+1}'] = str(item)
                        else:
                            resumo_respostas_limpo[f'Pergunta {i+1}'] = str(item)
                elif isinstance(resumo_respostas, dict):
                    # Se for um dicionário, processar normalmente
                    resumo_respostas_limpo = {}
                    for pergunta, resposta in resumo_respostas.items():
                        if isinstance(resposta, dict):
                            # Se for um objeto, extrair a resposta principal
                            if 'resposta' in resposta:
                                resumo_respostas_limpo[pergunta] = resposta['resposta']
                            elif 'valor' in resposta:
                                resumo_respostas_limpo[pergunta] = str(resposta['valor'])
                            else:
                                resumo_respostas_limpo[pergunta] = str(resposta)
                        else:
                            resumo_respostas_limpo[pergunta] = str(resposta)
                else:
                    # Se for outro tipo, converter para string
                    resumo_respostas_limpo = {'Resposta': str(resumo_respostas)}
                
                resumo_respostas = resumo_respostas_limpo
            else:
                resumo_respostas = {}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Erro ao processar resumo de respostas: {e}")
            resumo_respostas = {}
        
        # Calcular diferença de valores
        try:
            valor_base = float(avaliacao['valor_base_calculado']) if avaliacao['valor_base_calculado'] else 0
            valor_final = float(avaliacao['valor_final_calculado']) if avaliacao['valor_final_calculado'] else 0
            diferenca_valor = valor_final - valor_base
            percentual_variacao = (diferenca_valor / valor_base) * 100 if valor_base > 0 else 0
        except (TypeError, ValueError) as e:
            print(f"Erro ao calcular valores: {e}")
            diferenca_valor = 0
            percentual_variacao = 0
            valor_base = 0
            valor_final = 0
        
        # Formatar data
        try:
            data_formatada = avaliacao['data_avaliacao'].strftime('%d/%m/%Y às %H:%M') if avaliacao['data_avaliacao'] else 'N/A'
        except AttributeError:
            data_formatada = 'N/A'
        
        dados_detalhes = {
            'avaliacao': {
                'id': avaliacao['id'],
                'data_avaliacao': data_formatada,
                'modelo': avaliacao.get('modelo_nome', 'N/A') or 'N/A',
                'cor': avaliacao.get('cor_selecionada', 'N/A') or 'N/A',
                'armazenamento': avaliacao.get('armazenamento_selecionado', 'N/A') or 'N/A',
                'imei': avaliacao.get('imei') or None,
                'valor_base': valor_base,
                'valor_final': valor_final,
                'diferenca': diferenca_valor,
                'percentual_variacao': percentual_variacao,
                'usuario': avaliacao.get('usuario_nome') or 'Sistema',
                'empresa': avaliacao.get('nome_empresa', 'N/A') or 'N/A'
            },
            'cliente': {
                'nome': avaliacao.get('nome_cliente_final') or None,
                'email': avaliacao.get('email_cliente_final') or None,
                'telefone': avaliacao.get('telefone_cliente_final') or None,
                'modelo_interesse': avaliacao.get('modelo_interesse') or None
            },
            'respostas': resumo_respostas,
            'historico_precos': historico_precos
        }
        
        cursor.close()
        conn.close()
        return jsonify(dados_detalhes)
        
    except Exception as e:
        print(f"Erro ao buscar detalhes da avaliação: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': f'Erro interno do servidor: {str(e)}'}), 500


@app.route('/convite/<token>/api/enviar-orcamento', methods=['POST'])
def enviar_orcamento_convite(token):
    """Envia orçamento do convidado."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verifica link
        cursor.execute("""
            SELECT lc.*, e.nome_empresa, e.email_contato_principal, e.logo_url,
                   lc.nome_cliente, lc.email_cliente, lc.telefone_cliente
            FROM links_convidados lc
            JOIN empresas e ON lc.empresa_id = e.id
            WHERE lc.token_unico = %s AND lc.usado = FALSE
        """, (token,))
        link = cursor.fetchone()

        if not link or datetime.datetime.now() > link['data_expiracao']:
            return jsonify({"erro": "Link inválido ou expirado"}), 401

        dados = request.json
        empresa_id = link['empresa_id']
        
        # Verifica se o plano da empresa está ativo
        cursor.execute("SELECT plano_ativo FROM empresas WHERE id = %s", (empresa_id,))
        empresa = cursor.fetchone()
        
        # Consumir resultados pendentes para evitar "Unread result found"
        cursor.fetchall()
        
        if empresa and not empresa['plano_ativo']:
            return jsonify({"erro": "O plano da empresa está desativado"}), 403

        # Busca modelo
        modelo_id = dados.get('modeloId')
        modelo_nome = dados.get('modelo')
        
        if modelo_id:
            # Se modeloId foi fornecido, usar diretamente
            cursor.execute("""
                SELECT id, valor_base_novo FROM modelos_iphone
                WHERE id = %s AND empresa_id = %s
            """, (modelo_id, empresa_id))
        else:
            # Fallback: buscar pelo nome do modelo
            cursor.execute("""
                SELECT id, valor_base_novo FROM modelos_iphone
                WHERE nome_modelo = %s AND empresa_id = %s
            """, (modelo_nome, empresa_id))
            
        modelo_row = cursor.fetchone()
        
        # Consumir resultados pendentes para evitar "Unread result found"
        cursor.fetchall()

        if not modelo_row:
            return jsonify({"erro": "Modelo não encontrado"}), 404

        modelo_id = modelo_row['id']
        valor_base_db = modelo_row['valor_base_novo']

        # Dados do orçamento
        nome_cliente = link['nome_cliente']
        email_cliente = link['email_cliente']
        telefone_cliente = link['telefone_cliente']
        
        # Buscar modelo de interesse da sessão
        modelo_interesse = session.get(f'modelo_interesse_{token}', 'Não informado')
        
        # Debug: verificar dados do link
        print(f"DEBUG - Dados do link: nome={nome_cliente}, email={email_cliente}, telefone={telefone_cliente}")
        print(f"DEBUG - Modelo de interesse: {modelo_interesse}")
        print(f"DEBUG - Link completo: {link}")
        cor_selecionada = dados.get('cor', 'N/A')
        armazenamento_selecionado = dados.get('armazenamento', 'N/A')
        imei = dados.get('imei', 'N/A')
        valor_final_calculado = float(dados.get('valor', 0.0))
        resumo_json = json.dumps(dados.get('resumo', []))

        # Salva avaliação
        sql_insert = """
            INSERT INTO avaliacoes_concluidas (
                empresa_id, nome_cliente_final, email_cliente_final, telefone_cliente_final,
                modelo_interesse, modelo_iphone_id, cor_selecionada, armazenamento_selecionado, imei,
                valor_base_calculado, valor_final_calculado, resumo_respostas
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insert, (
            empresa_id, nome_cliente, email_cliente, telefone_cliente,
            modelo_interesse, modelo_id, cor_selecionada, armazenamento_selecionado, imei,
            valor_base_db, valor_final_calculado, resumo_json
        ))

        # Marca link como usado
        cursor.execute("""
            UPDATE links_convidados
            SET usado = TRUE, data_uso = NOW()
            WHERE token_unico = %s
        """, (token,))

        conn.commit()

        # Envia email para a empresa
        email_destino = link.get('email_contato_principal', '')

        # Verifica se deve enviar email (padrão: sim)
        envia_email = True
        if 'envia_email_orcamento_link' in link:
            envia_email = bool(link['envia_email_orcamento_link'])

        if envia_email and email_destino and email_destino.strip():
            # Buscar modelo de interesse da sessão
            modelo_interesse = session.get(f'modelo_interesse_{token}', 'Não informado')
            print(f"\nDEBUG - Dados do Email:")
            print(f"- Nome: {nome_cliente}")
            print(f"- Email: {email_cliente}")
            print(f"- Telefone: {telefone_cliente}")
            print(f"- Modelo de Interesse: {modelo_interesse}")
            print(f"- Modelo Avaliado: {dados.get('modelo')}")
            
            corpo_email = f"""
            Novo Orçamento via Link de Convite!
            ------------------------------------
            Dados do Cliente:
            - Nome: {nome_cliente}
            - E-mail: {email_cliente}
            - Telefone: {telefone_cliente}
            
            Preferência do Cliente:
            - Modelo de Interesse: {modelo_interesse}
            
            Detalhes do Aparelho Avaliado:
            - Modelo: {dados.get('modelo')}
            - Cor: {cor_selecionada}
            - Armazenamento: {armazenamento_selecionado}
            - IMEI: {imei}

            Diagnóstico:
            """
            for item in dados.get('resumo', []):
                if 'pergunta' in item and 'resposta' in item:
                    corpo_email += f"- {item['pergunta']}: {item['resposta']}\n"

            corpo_email += f"""
            ------------------------------------
            VALOR FINAL ESTIMADO: R$ {dados.get('valor')}
            """

            try:
                # Limpa caracteres especiais do assunto
                assunto_limpo = f"Novo Orçamento via Convite - {dados.get('modelo')}".encode('ascii', 'ignore').decode('ascii')

                msg = Message(
                    subject=assunto_limpo,
                    sender=("Sistema de Convites", app.config['MAIL_USERNAME']),
                    recipients=[email_destino.strip()]
                )
                # Limpa caracteres especiais do corpo
                corpo_limpo = corpo_email.encode('utf-8', 'ignore').decode('utf-8')
                msg.body = corpo_limpo
                mail.send(msg)
                print(f"Email enviado com sucesso para: {email_destino}")
            except Exception as e:
                print(f"Erro ao enviar email para {email_destino}: {e}")
        else:
            print(f"Email não enviado: permissão={envia_email}, email={email_destino}")
        
        # Limpar dados da sessão após o envio
        session.pop(f'modelo_interesse_{token}', None)

        # Gera link do WhatsApp
        telefone_empresa = link.get('telefone_cliente', '')  # Você pode adicionar telefone da empresa na tabela
        if telefone_empresa:
            # Limpa o telefone para o formato do WhatsApp
            telefone_limpo = telefone_empresa.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            # Remove o código do país se já estiver presente
            if telefone_limpo.startswith('55'):
                telefone_whatsapp = telefone_limpo
            else:
                telefone_whatsapp = f"55{telefone_limpo}"

            mensagem_whatsapp = f"Olá! Gostaria de mais informações sobre o orçamento do {dados.get('modelo')} que acabei de fazer. Valor: R$ {dados.get('valor')}"
            link_whatsapp = f"https://wa.me/{telefone_whatsapp}?text={mensagem_whatsapp}"
        else:
            link_whatsapp = ""

        return jsonify({
            "mensagem": "Orçamento enviado com sucesso!",
            "link_whatsapp": link_whatsapp
        })

    except mysql.connector.Error as e:
        if conn: conn.rollback()
        return jsonify({"erro": f"Erro ao salvar: {e}"}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    print("Iniciando correção automática das respostas...")
    garantir_respostas_completas()
    print("Correção concluída. Iniciando servidor...")
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
