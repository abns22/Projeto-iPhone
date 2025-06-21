import psycopg2
import os

DB_NAME = "iphone_breakdown_db"
DB_USER = "alfredo"
DB_PASS = "icloudbz12031994@lF"  
DB_HOST = "localhost"
DB_PORT = "5432"

def criar_tabelas():
    """
    Cria toda a estrutura de tabelas no banco de dados PostgreSQL.
    A sintaxe está adaptada com SERIAL, VARCHAR, NUMERIC, e restrições de integridade.
    """
    comandos_sql_criar = [
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nome_empresa VARCHAR(255) NOT NULL UNIQUE,
            logo_url VARCHAR(255),
            email_contato_principal VARCHAR(255),
            plano_ativo BOOLEAN DEFAULT TRUE,
            permite_ajuste_valores BOOLEAN DEFAULT FALSE,
            envia_email_orcamento BOOLEAN DEFAULT TRUE,
            permite_link_convidado BOOLEAN DEFAULT FALSE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(255) NOT NULL,
            senha_hash VARCHAR(255) NOT NULL,
            nome_completo VARCHAR(255),
            telefone VARCHAR(20),
            is_admin BOOLEAN DEFAULT FALSE,
            empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            UNIQUE(usuario, empresa_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS modelos_iphone (
            id SERIAL PRIMARY KEY,
            nome_modelo VARCHAR(100) NOT NULL,
            valor_base_novo NUMERIC(10, 2) NOT NULL,
            imagem_padrao_url VARCHAR(255),
            empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            UNIQUE(id, empresa_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS cores (
            id SERIAL PRIMARY KEY,
            nome_cor VARCHAR(50) NOT NULL UNIQUE,
            codigo_hex VARCHAR(7)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS armazenamentos (
            id SERIAL PRIMARY KEY,
            capacidade_gb INTEGER NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS componentes (
            id SERIAL PRIMARY KEY,
            nome_componente VARCHAR(255) NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS perguntas_avaliacao (
            id SERIAL PRIMARY KEY,
            texto_pergunta TEXT NOT NULL UNIQUE,
            componente_id INTEGER REFERENCES componentes(id) ON DELETE SET NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS modelos_cores (
            id SERIAL PRIMARY KEY,
            modelo_id INTEGER NOT NULL,
            cor_id INTEGER NOT NULL,
            imagem_url VARCHAR(255) NOT NULL,
            empresa_id INTEGER NOT NULL,
            FOREIGN KEY (modelo_id, empresa_id) REFERENCES modelos_iphone(id, empresa_id) ON DELETE CASCADE,
            FOREIGN KEY (cor_id) REFERENCES cores(id) ON DELETE CASCADE,
            UNIQUE(modelo_id, cor_id, empresa_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS modelos_armazenamentos (
            id SERIAL PRIMARY KEY,
            modelo_id INTEGER NOT NULL,
            armazenamento_id INTEGER NOT NULL,
            modificador_valor NUMERIC(10, 2) DEFAULT 0,
            empresa_id INTEGER NOT NULL,
            FOREIGN KEY (modelo_id, empresa_id) REFERENCES modelos_iphone(id, empresa_id) ON DELETE CASCADE,
            FOREIGN KEY (armazenamento_id) REFERENCES armazenamentos(id) ON DELETE CASCADE,
            UNIQUE(modelo_id, armazenamento_id, empresa_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS impacto_respostas (
            id SERIAL PRIMARY KEY,
            modelo_id INTEGER NOT NULL,
            pergunta_id INTEGER NOT NULL,
            resposta_que_gera_impacto VARCHAR(50) NOT NULL,
            valor_do_impacto NUMERIC(10, 2) NOT NULL,
            empresa_id INTEGER NOT NULL,
            FOREIGN KEY (modelo_id, empresa_id) REFERENCES modelos_iphone(id, empresa_id) ON DELETE CASCADE,
            FOREIGN KEY (pergunta_id) REFERENCES perguntas_avaliacao(id) ON DELETE CASCADE,
            UNIQUE(modelo_id, pergunta_id, resposta_que_gera_impacto, empresa_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS avaliacoes_concluidas (
            id SERIAL PRIMARY KEY,
            empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            nome_cliente_final VARCHAR(255),
            email_cliente_final VARCHAR(255),
            telefone_cliente_final VARCHAR(255),
            modelo_iphone_id INTEGER NOT NULL,
            cor_selecionada VARCHAR(100) NOT NULL,
            armazenamento_selecionado VARCHAR(100) NOT NULL,
            imei VARCHAR(50),
            valor_base_calculado NUMERIC(10, 2) NOT NULL,
            valor_final_calculado NUMERIC(10, 2) NOT NULL,
            resumo_respostas TEXT NOT NULL,
            data_avaliacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (modelo_iphone_id, empresa_id) REFERENCES modelos_iphone(id, empresa_id)
        );
        """
    ]
    
    conexao = None
    try:
        conexao = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        cursor = conexao.cursor()
        print("Conectado ao PostgreSQL. Criando todas as tabelas...")

        for comando in comandos_sql_criar:
            cursor.execute(comando)

        conexao.commit()
        print("Tabelas criadas com sucesso no PostgreSQL.")
        
    except psycopg2.Error as e:
        print(f"Ocorreu um erro com o PostgreSQL ao criar tabelas: {e}")
        if conexao: conexao.rollback()
    finally:
        if conexao:
            cursor.close()
            conexao.close()
            print("Conexão de criação de tabelas fechada.")


def popular_tabelas():
    """
    Popula todas as tabelas com dados iniciais para a empresa padrão (ID 1).
    ON CONFLICT DO NOTHING impede a inserção de duplicatas.
    """
    empresa_id_padrao = 1

    empresas_para_inserir = [
        (empresa_id_padrao, 'Minha Empresa Principal', '/static/images/logo_padrao.png', 'contato@minhaempresa.com', True, True, True, True)
    ]

    modelos_para_inserir = [
        (1, 'iPhone 11', 1300.00, 'images/ip11branco.jpg', empresa_id_padrao),
        (2, 'iPhone 11 Pro', 1600.00, 'images/ip11prodourado.PNG', empresa_id_padrao),
        (3, 'iPhone 11 Pro Max', 1900.00, 'images/ip11promaxverde.jpg', empresa_id_padrao),
        (4, 'iPhone 12 Mini', 1400.00, 'images/ip12miniazul.PNG', empresa_id_padrao),
        (5, 'iPhone 12', 1500.00, 'images/ip12preto.PNG', empresa_id_padrao),
        (6, 'iPhone 12 Pro', 1900.00, 'images/ip12prodourado.PNG', empresa_id_padrao),
        (7, 'iPhone 12 Pro Max', 2300.00, 'images/ip12promaxbranco.PNG', empresa_id_padrao),
        (8, 'iPhone 13 Mini', 1500.00, 'images/ip13minivermelho.PNG', empresa_id_padrao),
        (9, 'iPhone 13', 1800.00, 'images/ip13branco.PNG', empresa_id_padrao),
        (10, 'iPhone 13 Pro', 2500.00, 'images/ip13prodourado.PNG', empresa_id_padrao),
        (11, 'iPhone 13 Pro Max', 2900.00, 'images/ip13promaxpreto.PNG', empresa_id_padrao),
        (12, 'iPhone 14 Plus', 2000.00, 'images/ip14pluspreto.PNG', empresa_id_padrao),
        (13, 'iPhone 14', 2200.00, 'images/ip14azul.PNG', empresa_id_padrao),
        (14, 'iPhone 14 Pro', 2500.00, 'images/ip14proroxo.PNG', empresa_id_padrao),
        (15, 'iPhone 14 Pro Max', 3000.00, 'images/ip14promaxdourado.PNG', empresa_id_padrao),
        (16, 'iPhone 15 Plus', 2300.00, 'images/ip15plusbranco.PNG', empresa_id_padrao),
        (17, 'iPhone 15', 2500.00, 'images/ip15branco.PNG', empresa_id_padrao),
        (18, 'iPhone 15 Pro', 3000.00, 'images/ip15protitanio.PNG', empresa_id_padrao),
        (19, 'iPhone 15 Pro Max', 3500.00, 'images/ip15promaxazul.PNG', empresa_id_padrao),
        (20, 'iPhone 16e', 2500.00, 'images/ip16epreto.PNG', empresa_id_padrao),
        (21, 'iPhone 16 Plus', 2500.00, 'images/ip16plusazul.PNG', empresa_id_padrao),
        (22, 'iPhone 16', 2800.00, 'images/ip16verde.PNG', empresa_id_padrao),
        (23, 'iPhone 16 Pro', 3400.00, 'images/ip16protitanio.PNG', empresa_id_padrao),
        (24, 'iPhone 16 Pro Max', 4000.00, 'images/ip16promaxdourado.PNG', empresa_id_padrao)
    ]
    
    cores_para_inserir = [
        (1, 'Preto', '#000000'), (2, 'Branco', '#FFFFFF'), (3, 'Azul', '#0000FF'),
        (4, 'Roxo-Profundo', '#5E5266'), (5, 'Meia-Noite', '#000033'), (6, 'Titanio', '#878681'),
        (7, 'Amarelo', '#FFFF00'), (8, 'Roxo', '#800080'), (9, 'Vermelho', '#FF0000'),
        (10, 'Verde', '#008000'), (11, 'Dourado', '#FFD700'), (12, 'Rosa', '#FFC0CB')
    ]

    armazenamentos_para_inserir = [
        (1, 64), (2, 128), (3, 256), (4, 512), (5, 1024)
    ]
    
    componentes_para_inserir = [
        (1, 'Tela Ruim'), (2, 'Tela não Funcional'), (3, 'Face-iD'), (4, 'Bateria'),
        (5, 'Câmera Traseira'), (6, 'Camera Frontal'), (7, 'Tampa Traseira'), (8, 'Alto Falantes'),
        (9, 'Carregamento'), (10, 'Peça desconhecida')
    ]

    perguntas_para_inserir = [
        (1, 'A tela tem marcas de uso severas? (como riscados profundos ou arranhões)', 1),
        (2, 'A tela esta funcionando?', 2),
        (3, 'O Reconhecimento facial esta funcionando?', 3),
        (4, 'A saude da bateria está acima de 85%?', 4),
        (5, 'A camera traseira está funcionando normalmente sem manchas ou problemas?', 5),
        (6, 'A camera frontal está funcionando normalmente sem manchas ou problemas?', 6),
        (7, 'A tampa traseira está quebrada?', 7),
        (8, 'O som (alto falante) esta funcionando normalmente?', 8),
        (9, 'O aparelho esta carregando normalmente?', 9),
        (10, 'O aparelho tem alguma mensagem de peça desconhecida (não genuína)?', 10)
    ]
    
    
    modelos_cores_para_inserir = [
        # iPhone 11 (ID 1)
        (1, 1, 'images/ip11preto.PNG', empresa_id_padrao),
        (1, 2, 'images/ip11branco.jpg', empresa_id_padrao),
        (1, 7, 'images/ip11amarelo.PNG', empresa_id_padrao),
        (1, 8, 'images/mip11roxo.PNG', empresa_id_padrao),
        (1, 10, 'images/ip11verde.PNG', empresa_id_padrao),
        (1, 9, 'images/ip11vermelho.PNG', empresa_id_padrao),

        # iPhone 11 Pro (ID 2)
        (2, 1, 'images/ip11propreto.PNG', empresa_id_padrao),
        (2, 10, 'images/ip11proverde.jpg', empresa_id_padrao),
        (2, 11, 'images/ip11prodourado.PNG', empresa_id_padrao),
        (2, 2, 'images/ip11probranco.PNG', empresa_id_padrao),

        # iPhone 11 Pro Max (ID 3)
        (3, 1, 'images/ip11promaxpreto.PNG', empresa_id_padrao),
        (3, 10, 'images/ip11promaxverde.jpg', empresa_id_padrao),
        (3, 11, 'images/ip11promaxdourado.PNG', empresa_id_padrao),
        (3, 2, 'images/ip11promaxbranco.PNG', empresa_id_padrao),

        # iPhone 12 Mini (ID 4)
        (4, 1, 'images/ip12minipreto.PNG', empresa_id_padrao),
        (4, 2, 'images/ip12minibranco.PNG', empresa_id_padrao),
        (4, 3, 'images/ip12miniazul.PNG', empresa_id_padrao),
        (4, 9, 'images/ip12minivermelho.PNG', empresa_id_padrao),

        # iPhone 12 (ID 5)
        (5, 1, 'images/ip12preto.PNG', empresa_id_padrao),
        (5, 2, 'images/ip12branco.PNG', empresa_id_padrao),
        (5, 3, 'images/ip12azul.PNG', empresa_id_padrao),
        (5, 9, 'images/ip12vermelho.PNG', empresa_id_padrao),

        # iPhone 12 Pro (ID 6)
        (6, 11, 'images/ip12prodourado.PNG', empresa_id_padrao),
        (6, 3, 'images/ip12proazul.PNG', empresa_id_padrao),
        (6, 1, 'images/ip12propreto.PNG', empresa_id_padrao),

        # iPhone 12 Pro Max (ID 7)
        (7, 11, 'images/ip12promaxdourado.PNG', empresa_id_padrao),
        (7, 3, 'images/ip12promaxazul.PNG', empresa_id_padrao),
        (7, 1, 'images/ip12promaxpreto.PNG', empresa_id_padrao),

        # iPhone 13 Mini (ID 8)
        (8, 2, 'images/ip13minibranco.PNG', empresa_id_padrao),
        (8, 5, 'images/ip13minimeianoite.PNG', empresa_id_padrao),
        (8, 9, 'images/ip13minivermelho.PNG', empresa_id_padrao),
        (8, 12, 'images/ip13minirosa.PNG', empresa_id_padrao),
        (8, 3, 'images/ip13miniazul.PNG', empresa_id_padrao), 

        # iPhone 13 (ID 9)
        (9, 2, 'images/ip13branco.PNG', empresa_id_padrao),
        (9, 5, 'images/ip13meianoite.PNG', empresa_id_padrao),
        (9, 9, 'images/ip13vermelho.PNG', empresa_id_padrao),
        (9, 3, 'images/ip13azul.PNG', empresa_id_padrao),
        (9, 12, 'images/ip13rosa.PNG', empresa_id_padrao),

        # iPhone 13 Pro (ID 10)
        (10, 11, 'images/ip13prodourado.PNG', empresa_id_padrao),
        (10, 3, 'images/ip13proazul.PNG', empresa_id_padrao),
        (10, 2, 'images/ip13probranco.PNG', empresa_id_padrao),
        (10, 1, 'images/ip13propreto.PNG', empresa_id_padrao),

        # iPhone 13 Pro Max (ID 11)
        (11, 11, 'images/ip13promaxdourado.PNG', empresa_id_padrao),
        (11, 3, 'images/ip13promaxazul.PNG', empresa_id_padrao),
        (11, 2, 'images/ip13promaxbranco.PNG', empresa_id_padrao),
        (11, 1, 'images/ip13promaxpreto.PNG', empresa_id_padrao),

        # iPhone 14 (ID 13)
        (13, 3, 'images/ip14azul.PNG', empresa_id_padrao),
        (13, 5, 'images/ip14meianoite.PNG', empresa_id_padrao),
        (13, 9, 'images/ip14vermelho.PNG', empresa_id_padrao),
        (13, 2, 'images/ip14branco.PNG', empresa_id_padrao),

        # iPhone 14 Plus (ID 12)
        (12, 3, 'images/ip14plusazul.PNG', empresa_id_padrao),
        (12, 5, 'images/ip14plusmeianoite.PNG', empresa_id_padrao),
        (12, 2, 'images/ip14plusbranco.PNG', empresa_id_padrao),

        # iPhone 14 Pro (ID 14)
        (14, 11, 'images/ip14prodourado.PNG', empresa_id_padrao),
        (14, 4, 'images/ip14proroxo.PNG', empresa_id_padrao),
        (14, 2, 'images/ip14probranco.PNG', empresa_id_padrao),

        # iPhone 14 Pro Max (ID 15)
        (15, 11, 'images/ip14promaxdourado.PNG', empresa_id_padrao),
        (15, 4, 'images/ip14promaxroxo.PNG', empresa_id_padrao),
        (15, 2, 'images/ip14promaxbranco.PNG', empresa_id_padrao),

        # iPhone 15 (ID 17)
        (17, 2, 'images/ip15branco.PNG', empresa_id_padrao),
        (17, 12, 'images/ip15rosa.PNG', empresa_id_padrao),
        (17, 1, 'images/ip15preto.PNG', empresa_id_padrao),
        (17, 10, 'images/ip15verde.PNG', empresa_id_padrao),
        (17, 7, 'images/ip15amarelo.PNG', empresa_id_padrao),
        
        # iPhone 15 Plus (ID 16)
        (16, 12, 'images/ip15plusrosa.PNG', empresa_id_padrao),
        (16, 2, 'images/ip15plusbranco.PNG', empresa_id_padrao),
        (16, 1, 'images/ip15pluspreto.PNG', empresa_id_padrao),
        (16, 7, 'images/ip15plusamarelo.PNG', empresa_id_padrao),
        (16, 10, 'images/ip15plusverde.PNG', empresa_id_padrao),

        # iPhone 15 Pro (ID 18)
        (18, 6, 'images/ip15protitanio.PNG', empresa_id_padrao),
        (18, 2, 'images/ip15probranco.PNG', empresa_id_padrao),
        (18, 1, 'images/ip15propreto.PNG', empresa_id_padrao), 

        # iPhone 15 Pro Max (ID 19)
        (19, 6, 'images/ip15promaxtitanio.PNG', empresa_id_padrao),
        (19, 2, 'images/ip15promaxbranco.PNG', empresa_id_padrao),
        (19, 1, 'images/ip15promaxpreto.PNG', empresa_id_padrao),

        # iPhone 16 (ID 22)
        (22, 10, 'images/ip16verde.PNG', empresa_id_padrao),
        (22, 3, 'images/ip16azul.PNG', empresa_id_padrao),
        (22, 2, 'images/ip16branco.PNG', empresa_id_padrao),
        (22, 1, 'images/ip16preto.PNG', empresa_id_padrao),
        (22, 12, 'images/ip16rosa.PNG', empresa_id_padrao),
        
        # iPhone 16e (ID 20)
        (20, 1, 'images/ip16epreto.PNG', empresa_id_padrao),
        (20, 2, 'images/ip16ebranco.PNG', empresa_id_padrao),

        # iPhone 16 Plus (ID 21)
        (21, 3, 'images/ip16plusazul.PNG', empresa_id_padrao),
        (21, 12, 'images/ip16plusrosa.PNG', empresa_id_padrao),
        (21, 10, 'images/ip16plusverde.PNG', empresa_id_padrao),
        (21, 1, 'images/ip16pluspreto.PNG', empresa_id_padrao),
        (21, 2, 'images/ip16plusbranco.PNG', empresa_id_padrao),

        # iPhone 16 Pro (ID 23)
        (23, 6, 'images/ip16protitanio.PNG', empresa_id_padrao),
        (23, 1, 'images/ip16propreto.PNG', empresa_id_padrao),
        (23, 11, 'images/ip16prodourado.PNG', empresa_id_padrao),
        (23, 2, 'images/ip16probranco.PNG', empresa_id_padrao),

        # iPhone 16 Pro Max (ID 24)
        (24, 1, 'images/ip16promaxpreto.PNG', empresa_id_padrao),
        (24, 6, 'images/ip16promaxtitanio.PNG', empresa_id_padrao),
        (24, 11, 'images/ip16promaxdourado.PNG', empresa_id_padrao),
        (24, 2, 'images/ip16promaxbranco.PNG', empresa_id_padrao)
    ]

    modelos_armazenamentos_para_inserir = [
        (1, 1, 0.00, empresa_id_padrao), (1, 2, 0.00, empresa_id_padrao), (1, 3, 100.00, empresa_id_padrao),
        (2, 1, 0.00, empresa_id_padrao), (2, 3, 150.00, empresa_id_padrao), (2, 4, 200.00, empresa_id_padrao),
        (3, 1, 0.00, empresa_id_padrao), (3, 3, 150.00, empresa_id_padrao), (3, 4, 200.00, empresa_id_padrao),
        (4, 1, 0.00, empresa_id_padrao), (4, 2, 0.00, empresa_id_padrao), (4, 3, 100.00, empresa_id_padrao),
        (5, 1, 0.00, empresa_id_padrao), (5, 2, 0.00, empresa_id_padrao), (5, 3, 100.00, empresa_id_padrao),
        (6, 2, 0.00, empresa_id_padrao), (6, 3, 100.00, empresa_id_padrao), (6, 4, 200.00, empresa_id_padrao),
        (6, 5, 250.00, empresa_id_padrao), (7, 2, 0.00, empresa_id_padrao), (7, 3, 100.00, empresa_id_padrao),
        (7, 4, 200.00, empresa_id_padrao), (7, 5, 250.00, empresa_id_padrao), (8, 2, 0.00, empresa_id_padrao),
        (8, 3, 150.00, empresa_id_padrao), (8, 4, 200.00, empresa_id_padrao), (9, 2, 0.00, empresa_id_padrao),
        (9, 3, 150.00, empresa_id_padrao), (9, 4, 250.00, empresa_id_padrao), (10, 2, 0.00, empresa_id_padrao),
        (10, 3, 150.00, empresa_id_padrao), (10, 4, 250.00, empresa_id_padrao), (10, 5, 300.00, empresa_id_padrao),
        (11, 2, 0.00, empresa_id_padrao), (11, 3, 150.00, empresa_id_padrao), (11, 4, 250.00, empresa_id_padrao),
        (11, 5, 300.00, empresa_id_padrao), (12, 2, 0.00, empresa_id_padrao), (12, 3, 100.00, empresa_id_padrao),
        (12, 4, 200.00, empresa_id_padrao), (13, 2, 0.00, empresa_id_padrao), (13, 3, 150.00, empresa_id_padrao),
        (13, 4, 200.00, empresa_id_padrao), (14, 2, 0.00, empresa_id_padrao), (14, 3, 150.00, empresa_id_padrao),
        (14, 4, 250.00, empresa_id_padrao), (14, 5, 300.00, empresa_id_padrao), (15, 2, 0.00, empresa_id_padrao),
        (15, 3, 150.00, empresa_id_padrao), (15, 4, 250.00, empresa_id_padrao), (15, 5, 300.00, empresa_id_padrao),
        (16, 2, 0.00, empresa_id_padrao), (16, 3, 150.00, empresa_id_padrao), (16, 4, 200.00, empresa_id_padrao),
        (16, 5, 250.00, empresa_id_padrao), (17, 2, 0.00, empresa_id_padrao), (17, 3, 150.00, empresa_id_padrao),
        (17, 4, 200.00, empresa_id_padrao), (17, 5, 250.00, empresa_id_padrao), (18, 2, 0.00, empresa_id_padrao),
        (18, 3, 150.00, empresa_id_padrao), (18, 4, 250.00, empresa_id_padrao), (18, 5, 350.00, empresa_id_padrao),
        (19, 2, 0.00, empresa_id_padrao), (19, 3, 150.00, empresa_id_padrao), (19, 4, 250.00, empresa_id_padrao),
        (19, 5, 350.00, empresa_id_padrao), (20, 2, 0.00, empresa_id_padrao), (20, 3, 200.00, empresa_id_padrao),
        (20, 4, 250.00, empresa_id_padrao), (21, 2, 0.00, empresa_id_padrao), (21, 3, 150.00, empresa_id_padrao),
        (21, 4, 200.00, empresa_id_padrao), (21, 5, 250.00, empresa_id_padrao), (22, 2, 0.00, empresa_id_padrao),
        (22, 3, 200.00, empresa_id_padrao), (22, 4, 250.00, empresa_id_padrao), (22, 5, 350.00, empresa_id_padrao),
        (23, 2, 0.00, empresa_id_padrao), (23, 3, 150.00, empresa_id_padrao), (23, 4, 250.00, empresa_id_padrao),
        (23, 5, 350.00, empresa_id_padrao), (24, 2, 0.00, empresa_id_padrao), (24, 3, 150.00, empresa_id_padrao),
        (24, 4, 250.00, empresa_id_padrao), (24, 5, 350.00, empresa_id_padrao)
    ]
    
    # Mapeamento dos IDs de pergunta para facilitar a leitura
    PERGUNTA_TELA_RUIM = 1
    PERGUNTA_TELA_NAO_FUNCIONA = 2
    PERGUNTA_FACEID_NAO_FUNCIONA = 3
    PERGUNTA_BATERIA_RUIM = 4
    PERGUNTA_CAMERA_TRASEIRA_RUIM = 5
    PERGUNTA_CAMERA_FRONTAL_RUIM = 6
    PERGUNTA_TAMPA_QUEBRADA = 7
    PERGUNTA_SOM_RUIM = 8
    PERGUNTA_CARREGAMENTO_RUIM = 9
    PERGUNTA_PECA_DESCONHECIDA = 10 

    # Lista de impactos completa com 'empresa_id_padrao' adicionado
    # Estrutura da tupla: (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id)
    impactos_para_inserir = [
        # --- iPhone 11 (ID 1) ---
        (1, PERGUNTA_TELA_RUIM, 'Sim', -150.00, empresa_id_padrao), 
        (1, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -100.00, empresa_id_padrao), 
        (1, PERGUNTA_BATERIA_RUIM, 'Não', -50.00, empresa_id_padrao),
        (1, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (1, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (1, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -200.00, empresa_id_padrao),
        (1, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (1, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (1, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao),
        (1, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -100.00, empresa_id_padrao),

        # --- iPhone 11 Pro (ID 2) ---
        (2, PERGUNTA_TELA_RUIM, 'Sim', -200.00, empresa_id_padrao), 
        (2, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -150.00, empresa_id_padrao), 
        (2, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (2, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (2, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (2, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00, empresa_id_padrao),
        (2, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (2, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (2, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (2, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -150.00, empresa_id_padrao),

        # --- iPhone 11 Pro Max (ID 3) ---
        (3, PERGUNTA_TELA_RUIM, 'Sim', -250.00, empresa_id_padrao), 
        (3, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -150.00, empresa_id_padrao), 
        (3, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (3, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (3, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (3, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00, empresa_id_padrao),
        (3, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (3, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (3, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (3, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -150.00, empresa_id_padrao),

        # --- iPhone 12 Mini (ID 4) ---
        (4, PERGUNTA_TELA_RUIM, 'Sim', -200.00, empresa_id_padrao), 
        (4, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -250.00, empresa_id_padrao), 
        (4, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (4, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (4, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (4, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -200.00, empresa_id_padrao),
        (4, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (4, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (4, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (4, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 12 (ID 5) ---
        (5, PERGUNTA_TELA_RUIM, 'Sim', -250.00, empresa_id_padrao), 
        (5, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -150.00, empresa_id_padrao), 
        (5, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (5, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (5, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (5, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00, empresa_id_padrao),
        (5, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (5, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (5, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (5, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 12 Pro (ID 6) ---
        (6, PERGUNTA_TELA_RUIM, 'Sim', -250.00, empresa_id_padrao), 
        (6, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -150.00, empresa_id_padrao), 
        (6, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (6, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (6, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (6, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (6, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (6, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (6, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (6, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 12 Pro Max (ID 7) ---
        (7, PERGUNTA_TELA_RUIM, 'Sim', -250.00, empresa_id_padrao), 
        (7, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00, empresa_id_padrao), 
        (7, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (7, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (7, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (7, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (7, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (7, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (7, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (7, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 13 Mini (ID 8) ---
        (8, PERGUNTA_TELA_RUIM, 'Sim', -250.00, empresa_id_padrao), 
        (8, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (8, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (8, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (8, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (8, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -200.00, empresa_id_padrao),
        (8, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (8, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (8, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (8, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 13 (ID 9) ---
        (9, PERGUNTA_TELA_RUIM, 'Sim', -350.00, empresa_id_padrao), 
        (9, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00, empresa_id_padrao), 
        (9, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (9, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (9, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (9, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00, empresa_id_padrao),
        (9, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (9, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (9, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (9, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 13 Pro (ID 10) ---
        (10, PERGUNTA_TELA_RUIM, 'Sim', -800.00, empresa_id_padrao), 
        (10, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -500.00, empresa_id_padrao), 
        (10, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (10, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (10, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (10, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -400.00, empresa_id_padrao),
        (10, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (10, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (10, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (10, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 13 Pro Max (ID 11) ---
        (11, PERGUNTA_TELA_RUIM, 'Sim', -1000.00, empresa_id_padrao), 
        (11, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -500.00, empresa_id_padrao), 
        (11, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (11, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (11, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (11, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -400.00, empresa_id_padrao),
        (11, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (11, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (11, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (11, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 14 Plus (ID 12) ---
        (12, PERGUNTA_TELA_RUIM, 'Sim', -400.00, empresa_id_padrao), 
        (12, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00, empresa_id_padrao), 
        (12, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (12, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (12, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (12, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (12, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (12, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (12, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (12, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 14 (ID 13) ---
        (13, PERGUNTA_TELA_RUIM, 'Sim', -400.00, empresa_id_padrao), 
        (13, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00, empresa_id_padrao), 
        (13, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (13, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (13, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (13, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (13, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (13, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (13, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (13, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00, empresa_id_padrao),

        # --- iPhone 14 Pro (ID 14) ---
        (14, PERGUNTA_TELA_RUIM, 'Sim', -1000.00, empresa_id_padrao), 
        (14, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00, empresa_id_padrao), 
        (14, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (14, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (14, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (14, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -500.00, empresa_id_padrao),
        (14, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (14, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (14, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (14, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 14 Pro Max (ID 15) ---
        (15, PERGUNTA_TELA_RUIM, 'Sim', -1000.00, empresa_id_padrao), 
        (15, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00, empresa_id_padrao), 
        (15, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (15, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (15, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (15, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -500.00, empresa_id_padrao),
        (15, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (15, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (15, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (15, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 15 Plus (ID 16) ---
        (16, PERGUNTA_TELA_RUIM, 'Sim', -500.00, empresa_id_padrao), 
        (16, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -350.00, empresa_id_padrao), 
        (16, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (16, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (16, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (16, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (16, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (16, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (16, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (16, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -250.00, empresa_id_padrao),

        # --- iPhone 15 (ID 17) ---
        (17, PERGUNTA_TELA_RUIM, 'Sim', -500.00, empresa_id_padrao), 
        (17, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -350.00, empresa_id_padrao), 
        (17, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (17, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (17, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (17, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -300.00, empresa_id_padrao),
        (17, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (17, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (17, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (17, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 15 Pro (ID 18) ---
        (18, PERGUNTA_TELA_RUIM, 'Sim', -1200.00, empresa_id_padrao), 
        (18, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00, empresa_id_padrao), 
        (18, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (18, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (18, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (18, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -600.00, empresa_id_padrao),
        (18, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (18, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (18, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (18, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 15 Pro Max (ID 19) ---
        (19, PERGUNTA_TELA_RUIM, 'Sim', -1400.00, empresa_id_padrao), 
        (19, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00, empresa_id_padrao), 
        (19, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (19, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (19, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (19, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -600.00, empresa_id_padrao),
        (19, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (19, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (19, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (19, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 16e (ID 20) ---
        (20, PERGUNTA_TELA_RUIM, 'Sim', -1000.00, empresa_id_padrao), 
        (20, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -500.00, empresa_id_padrao), 
        (20, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (20, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (20, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (20, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -350.00, empresa_id_padrao),
        (20, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (20, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (20, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (20, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 16 Plus (ID 21) ---
        (21, PERGUNTA_TELA_RUIM, 'Sim', -1000.00, empresa_id_padrao), 
        (21, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -500.00, empresa_id_padrao), 
        (21, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (21, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (21, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (21, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -350.00, empresa_id_padrao),
        (21, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (21, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (21, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (21, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 16 (ID 22) ---
        (22, PERGUNTA_TELA_RUIM, 'Sim', -800.00, empresa_id_padrao), 
        (22, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -400.00, empresa_id_padrao), 
        (22, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (22, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (22, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (22, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -350.00, empresa_id_padrao),
        (22, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (22, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (22, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (22, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00, empresa_id_padrao),

        # --- iPhone 16 Pro (ID 23) ---
        (23, PERGUNTA_TELA_RUIM, 'Sim', -1500.00, empresa_id_padrao), 
        (23, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -700.00, empresa_id_padrao), 
        (23, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (23, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (23, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao), 
        (23, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -700.00, empresa_id_padrao),
        (23, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (23, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (23, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (23, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -400.00, empresa_id_padrao),

        # --- iPhone 16 Pro Max (ID 24) ---
        (24, PERGUNTA_TELA_RUIM, 'Sim', -1800.00, empresa_id_padrao), 
        (24, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -800.00, empresa_id_padrao), 
        (24, PERGUNTA_BATERIA_RUIM, 'Não', -80.00, empresa_id_padrao),
        (24, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00, empresa_id_padrao), 
        (24, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00, empresa_id_padrao),
        (24, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -700.00, empresa_id_padrao),
        (24, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (24, PERGUNTA_SOM_RUIM, 'Não', -50.00, empresa_id_padrao), 
        (24, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00, empresa_id_padrao), 
        (24, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -400.00, empresa_id_padrao)
    ]
    conexao = None
    try:
        conexao = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        cursor = conexao.cursor()
        print("\nPopulando tabelas no PostgreSQL...")

        cursor.executemany("INSERT INTO empresas (id, nome_empresa, logo_url, email_contato_principal, plano_ativo, permite_ajuste_valores, envia_email_orcamento, permite_link_convidado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING", empresas_para_inserir)
        cursor.executemany("INSERT INTO cores (id, nome_cor, codigo_hex) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", cores_para_inserir)
        cursor.executemany("INSERT INTO armazenamentos (id, capacidade_gb) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", armazenamentos_para_inserir)
        cursor.executemany("INSERT INTO componentes (id, nome_componente) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", componentes_para_inserir)
        cursor.executemany("INSERT INTO perguntas_avaliacao (id, texto_pergunta, componente_id) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", perguntas_para_inserir)
        
        cursor.executemany("INSERT INTO modelos_iphone (id, nome_modelo, valor_base_novo, imagem_padrao_url, empresa_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING", modelos_para_inserir)
        
        cursor.executemany("INSERT INTO modelos_cores (modelo_id, cor_id, imagem_url, empresa_id) VALUES (%s, %s, %s, %s) ON CONFLICT (modelo_id, cor_id, empresa_id) DO NOTHING", modelos_cores_para_inserir)
        cursor.executemany("INSERT INTO modelos_armazenamentos (modelo_id, armazenamento_id, modificador_valor, empresa_id) VALUES (%s, %s, %s, %s) ON CONFLICT (modelo_id, armazenamento_id, empresa_id) DO NOTHING", modelos_armazenamentos_para_inserir)
        cursor.executemany("INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (modelo_id, pergunta_id, resposta_que_gera_impacto, empresa_id) DO NOTHING", impactos_para_inserir)

        conexao.commit()
        print("\nTabelas populadas com os dados fornecidos.")

    except psycopg2.Error as e:
        print(f"Ocorreu um erro ao popular as tabelas no PostgreSQL: {e}")
        if conexao: conexao.rollback()
    finally:
        if conexao:
            cursor.close()
            conexao.close()
            print("Conexão de população de tabelas fechada.")


# --- Bloco de Execução Principal ---
if __name__ == '__main__':
    # 1. Cria a estrutura de tabelas no PostgreSQL
    criar_tabelas()
    
    # 2. Popula as tabelas com dados iniciais
    popular_tabelas()
    
    print("\nScript de setup para PostgreSQL concluído!")
    