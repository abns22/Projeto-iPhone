import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'frontend', 'banco.db')

def criar_tabelas():
    
    sql_criar_tabela_avaliacoes_concluidas = """

    CREATE TABLE IF NOT EXISTS avaliacoes_concluidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER NOT NULL,
        usuario_id INTEGER, 
        nome_cliente_final TEXT, 
        email_cliente_final TEXT,
        telefone_cliente_final TEXT,
        modelo_iphone_id INTEGER NOT NULL,
        cor_selecionada TEXT NOT NULL,
        armazenamento_selecionado TEXT NOT NULL,
        imei TEXT,
        valor_base_calculado REAL NOT NULL,
        valor_final_calculado REAL NOT NULL,
        resumo_respostas TEXT NOT NULL,
        data_avaliacao DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (empresa_id) REFERENCES empresas (id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (modelo_iphone_id) REFERENCES modelos_iphone (id)
    );
    """

    sql_criar_tabela_modelos = """
    CREATE TABLE IF NOT EXISTS modelos_iphone (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_modelo TEXT NOT NULL UNIQUE,
        cor_modelo INTEGER,
        valor_base REAL NOT NULL,
        imagem_padrao_url TEXT
    );
    """

    sql_criar_tabela_componentes = """
    CREATE TABLE IF NOT EXISTS componentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_componente TEXT NOT NULL UNIQUE,
        descricao_avaliacao TEXT
    );
    """

    sql_criar_tabela_cores = """
    CREATE TABLE IF NOT EXISTS cores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cor TEXT NOT NULL UNIQUE,
        codigo_hex TEXT -- Adicione esta linha
    );
    """

    sql_criar_tabela_modelos_cores = """
    CREATE TABLE IF NOT EXISTS modelos_cores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo_id INTEGER NOT NULL,
        cor_id INTEGER NOT NULL,
        imagem_url TEXT NOT NULL,
        FOREIGN KEY (modelo_id) REFERENCES modelos_iphone (id),
        FOREIGN KEY (cor_id) REFERENCES cores (id)
    );
    """

    sql_criar_tabela_armazenamento = """
    CREATE TABLE IF NOT EXISTS armazenamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        capacidade_gb INTEGER NOT NULL UNIQUE
    );
    """
    sql_criar_tabela_modelos_armazenamento = """
    CREATE TABLE IF NOT EXISTS modelos_armazenamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo_id INTEGER NOT NULL,
        armazenamento_id INTEGER NOT NULL,
        modificador_valor REAL DEFAULT 0,
        FOREIGN KEY (modelo_id) REFERENCES modelos_iphone (id),
        FOREIGN KEY (armazenamento_id) REFERENCES armazenamentos (id)
    );
    """
    sql_criar_tabela_pergunta_avaliacao = """
    CREATE TABLE IF NOT EXISTS perguntas_avaliacao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto_pergunta TEXT NOT NULL UNIQUE,
        componente_id INTEGER,
        FOREIGN KEY (componente_id) REFERENCES componentes (id)
    );
    """

    sql_criar_tabela_impacto_respostas = """
    CREATE TABLE IF NOT EXISTS impacto_respostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modelo_id INTEGER NOT NULL,
        pergunta_id INTEGER NOT NULL,
        resposta_que_gera_impacto TEXT NOT NULL,
        valor_do_impacto REAL NOT NULL,
        FOREIGN KEY (modelo_id) REFERENCES modelos_iphone (id),
        FOREIGN KEY (pergunta_id) REFERENCES perguntas_avaliacao (id)
    );
    """

    conexao = None
    try:
        
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()

        print("Criando tabela avaliacoes_concluidas")
        cursor.execute(sql_criar_tabela_avaliacoes_concluidas)

        print("Criando tabela 'modelos_iphone'...")
        cursor.execute(sql_criar_tabela_modelos)

        print("Criando tabela 'componentes'...")
        cursor.execute(sql_criar_tabela_componentes)

        print("Criando tabela 'tabela_cores'...")
        cursor.execute(sql_criar_tabela_cores)

        print("Criando tabela 'tabela_modelos_cores'...")
        cursor.execute(sql_criar_tabela_modelos_cores)

        print("Criando tabela 'tabela_armazenamento'...")
        cursor.execute(sql_criar_tabela_armazenamento)

        print("Criando tabela 'tabela_modelos_armazenamento'...")
        cursor.execute(sql_criar_tabela_modelos_armazenamento)

        print("Criando tabela 'tabela_pergunta_avaliacao'...")
        cursor.execute(sql_criar_tabela_pergunta_avaliacao)

        print("Criando tabela 'tabela_impacto_respostas...")
        cursor.execute(sql_criar_tabela_impacto_respostas)

        conexao.commit()
        print("Tabelas criadas com sucesso (ou já existiam).")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar as tabelas: {e}")
    
    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")

def popular_tabelas():

    modelos_para_inserir = [
        (1, 'iPhone 11', 0, 1300.00, 'images/ip11branco.jpg'),
        (2, 'iPhone 11 Pro', 0, 1600.00, 'images/ip11prodourado.PNG'),
        (3, 'iPhone 11 Pro Max', 0, 1900.00, 'images/ip11promaxverde.jpg'),
        (4, 'iPhone 12 Mini', 0, 1400.00, 'images/ip12miniazul.PNG'),
        (5, 'iPhone 12', 0, 1500.00, 'images/ip12preto.PNG'),
        (6, 'iPhone 12 Pro', 0, 1900.00, 'images/ip12prodourado.PNG'),
        (7, 'iPhone 12 Pro Max', 0, 2300.00, 'images/ip12promaxbranco.PNG'),
        (8, 'iPhone 13 Mini', 0, 1500.00, 'images/ip13minivermelho.PNG'),
        (9, 'iPhone 13', 0, 1800.00, 'images/ip13branco.PNG'),
        (10, 'iPhone 13 Pro', 0, 2500.00, 'images/ip13prodourado.PNG'),
        (11, 'iPhone 13 Pro Max', 0, 2900.00, 'images/ip13promaxpreto.PNG'),
        (12, 'iPhone 14 Plus', 0, 2000.00, 'images/ip14pluspreto.PNG'),
        (13, 'iPhone 14', 0, 2200.00, 'images/ip14azul.PNG'),
        (14, 'iPhone 14 Pro', 0, 2500.00, 'images/ip14proroxo.PNG'),
        (15, 'iPhone 14 Pro Max', 0, 3000.00, 'images/ip14promaxdourado.PNG'),
        (16, 'iPhone 15 Plus', 0, 2300.00, 'images/ip15plusbranco.PNG'),
        (17, 'iPhone 15', 0, 2500.00, 'images/ip15branco.PNG'),
        (18, 'iPhone 15 Pro', 0, 3000.00, 'images/ip15protitanio.PNG'),
        (19, 'iPhone 15 Pro Max', 0, 3500.00, 'images/ip15promaxazul.PNG'),
        (20, 'iPhone 16e', 0, 2500.00, 'images/ip16epreto.PNG'),
        (21, 'iPhone 16 Plus', 0, 2500.00, 'images/ip16plusazul.PNG'),
        (22, 'iPhone 16', 0, 2800.00, 'images/ip16verde.PNG'),
        (23, 'iPhone 16 Pro', 0, 3400.00, 'images/ip16protitanio.PNG'),
        (24, 'iPhone 16 Pro Max', 0, 4000.00, 'images/ip16promaxdourado.PNG')

    ]

    # Para a tabela 'cores'
    # Estrutura da tupla: (id, nome_cor)
    cores_para_inserir = [
        (1, 'Preto', '#000000'),
        (2, 'Branco', '#FFFFFF'),
        (3, 'Azul', '#0000FF'),
        (4, 'Roxo-Profundo', '#4B0082'),
        (5, 'Meia-Noite', '#000033'),
        (6, 'Titanio', '#878681'),
        (7, 'Amarelo', '#FFFF00'),
        (8, 'Roxo', '#800080'),
        (9, 'Vermelho', '#FF0000'),
        (10, 'Verde', '#008000'),
        (11, 'Dourado', '#FFD700'),
        (12, 'Rosa', '#FFC0CB'),
    ]

    # Para a tabela 'armazenamentos'
    # Estrutura da tupla: (id, capacidade_gb).
    armazenamentos_para_inserir = [
        (1, 64),
        (2, 128),
        (3, 256),
        (4, 512),
        (5, 1024)
    ]

    # Para a tabela de ligação 'modelos_cores'
    # Estrutura da tupla: (modelo_id, cor_id, imagem_url)
    modelos_cores_para_inserir = [
         # iPhone 11 (ID 1)
        (1, 1, 'images/ip11preto.PNG'),
        (1, 2, 'images/ip11branco.jpg'),
        (1, 7, 'images/ip11amarelo.PNG'),
        (1, 8, 'images/mip11roxo.PNG'),
        (1, 10, 'images/ip11verde.PNG'),
        (1, 9, 'images/ip11vermelho.PNG'),

        # iPhone 11 Pro (ID 2)
        (2, 1, 'images/ip11propreto.PNG'),
        (2, 10, 'images/ip11proverde.jpg'),
        (2, 11, 'images/ip11prodourado.PNG'),
        (2, 2, 'images/ip11probranco.PNG'),

        # iPhone 11 Pro Max (ID 3)
        (3, 1, 'images/ip11promaxpreto.PNG'),
        (3, 10, 'images/ip11promaxverde.jpg'),
        (3, 11, 'images/ip11promaxdourado.PNG'),
        (3, 2, 'images/ip11promaxbranco.PNG'),

        # iPhone 12 Mini (ID 4)
        (4, 1, 'images/ip12minipreto.PNG'),
        (4, 2, 'images/ip12minibranco.PNG'),
        (4, 3, 'images/ip12miniazul.PNG'),
        (4, 9, 'images/ip12minivermelho.PNG'),

        # iPhone 12 (ID 5)
        (5, 1, 'images/ip12preto.PNG'),
        (5, 2, 'images/ip12branco.PNG'),
        (5, 3, 'images/ip12azul.PNG'),
        (5, 9, 'images/ip12vermelho.PNG'),

        # iPhone 12 Pro (ID 6)
        (6, 11, 'images/ip12prodourado.PNG'),
        (6, 3, 'images/ip12proazul.PNG'),
        (6, 1, 'images/ip12propreto.PNG'),

        # iPhone 12 Pro Max (ID 7)
        (7, 11, 'images/ip12promaxdourado.PNG'),
        (7, 3, 'images/ip12promaxazul.PNG'),
        (7, 1, 'images/ip12promaxpreto.PNG'),

        # iPhone 13 Mini (ID 8)
        (8, 2, 'images/ip13minibranco.PNG'),
        (8, 5, 'images/ip13minimeianoite.PNG'),
        (8, 9, 'images/ip13minivermelho.PNG'),
        (8, 12, 'images/ip13minirosa.PNG'),
        (8, 3, 'images/ip13miniazul.PNG'), 

        # iPhone 13 (ID 9)
        (9, 2, 'images/ip13branco.PNG'),
        (9, 5, 'images/ip13meianoite.PNG'),
        (9, 9, 'images/ip13vermelho.PNG'),
        (9, 3, 'images/ip13azul.PNG'),
        (9, 12, 'images/ip13rosa.PNG'),

        # iPhone 13 Pro (ID 10)
        (10, 11, 'images/ip13prodourado.PNG'),
        (10, 3, 'images/ip13proazul.PNG'),
        (10, 2, 'images/ip13probranco.PNG'),
        (10, 1, 'images/ip13propreto.PNG'),

        # iPhone 13 Pro Max (ID 11)
        (11, 11, 'images/ip13promaxdourado.PNG'),
        (11, 3, 'images/ip13promaxazul.PNG'),
        (11, 2, 'images/ip13promaxbranco.PNG'),
        (11, 1, 'images/ip13promaxpreto.PNG'),

        # iPhone 14 (ID 13)
        (13, 3, 'images/ip14azul.PNG'),
        (13, 5, 'images/ip14meianoite.PNG'),
        (13, 9, 'images/ip14vermelho.PNG'),
        (13, 2, 'images/ip14branco.PNG'),

        # iPhone 14 Plus (ID 12)
        (12, 3, 'images/ip14plusazul.PNG'),
        (12, 5, 'images/ip14plusmeianoite.PNG'),
        (12, 2, 'images/ip14plusbranco.PNG'),

        # iPhone 14 Pro (ID 14)
        (14, 11, 'images/ip14prodourado.PNG'),
        (14, 4, 'images/ip14proroxo.PNG'),
        (14, 2, 'images/ip14probranco.PNG'),

        # iPhone 14 Pro Max (ID 15)
        (15, 11, 'images/ip14promaxdourado.PNG'),
        (15, 4, 'images/ip14promaxroxo.PNG'),
        (15, 2, 'images/ip14promaxbranco.PNG'),

        # iPhone 15 (ID 17)
        (17, 2, 'images/ip15branco.PNG'),
        (17, 12, 'images/ip15rosa.PNG'),
        (17, 1, 'images/ip15preto.PNG'),
        (17, 10, 'images/ip15verde.PNG'),
        (17, 7, 'images/ip15amarelo.PNG'),
        
        # iPhone 15 Plus (ID 16)
        (16, 12, 'images/ip15plusrosa.PNG'),
        (16, 2, 'images/ip15plusbranco.PNG'),
        (16, 1, 'images/ip15pluspreto.PNG'),
        (16, 7, 'images/ip15plusamarelo.PNG'),
        (16, 10, 'images/ip15plusverde.PNG'),

        # iPhone 15 Pro (ID 18)
        (18, 6, 'images/ip15protitanio.PNG'),
        (18, 2, 'images/ip15probranco.PNG'),
        (18, 1, 'images/ip15propreto.PNG'), 

        # iPhone 15 Pro Max (ID 19)
        (19, 6, 'images/ip15promaxtitanio.PNG'),
        (19, 2, 'images/ip15promaxbranco.PNG'),
        (19, 1, 'images/ip15promaxpreto.PNG'),

        # iPhone 16 (ID 22)
        (22, 10, 'images/ip16verde.PNG'),
        (22, 3, 'images/ip16azul.PNG'),
        (22, 2, 'images/ip16branco.PNG'),
        (22, 1, 'images/ip16preto.PNG'),
        (22, 12, 'images/ip16rosa.PNG'),
        
        # iPhone 16e (ID 20)
        (20, 1, 'images/ip16epreto.PNG'),
        (20, 2, 'images/ip16ebranco.PNG'),

        # iPhone 16 Plus (ID 21)
        (21, 3, 'images/ip16plusazul.PNG'),
        (21, 12, 'images/ip16plusrosa.PNG'),
        (21, 10, 'images/ip16plusverde.PNG'),
        (21, 1, 'images/ip16pluspreto.PNG'),
        (21, 2, 'images/ip16plusbranco.PNG'),

        # iPhone 16 Pro (ID 23)
        (23, 6, 'images/ip16protitanio.PNG'),
        (23, 1, 'images/ip16propreto.PNG'),
        (23, 11, 'images/ip16prodourado.PNG'),
        (23, 2, 'images/ip16probranco.PNG'),

        # iPhone 16 Pro Max (ID 24)
        (24, 1, 'images/ip16promaxpreto.PNG'),
        (24, 6, 'images/ip16promaxtitanio.PNG'),
        (24, 11, 'images/ip16promaxdourado.PNG'),
        (24, 2, 'images/ip16promaxbranco.PNG')
    ]


    # Para a tabela de ligação 'modelos_armazenamentos'
    # Estrutura da tupla: (modelo_id, armazenamento_id, modificador_valor)
    modelos_armazenamentos_para_inserir = [
    (1, 1, 0.00), # iPhone 11 (ID 1) com 64GB (ID 1)
    (1, 2, 0.00), # iPhone 11 (ID 1) com 128GB (ID 2)
    (1, 3, 100.00), # iPhone 11 (ID 1) com 256GB (ID 3)

    # --- iPhone 11 Pro (até 512GB) ---
    (2, 1, 0.00), # iPhone 11 Pro (ID 2) com 64GB (ID 1)
    (2, 3, 150.00), # iPhone 11 Pro (ID 2) com 256GB (ID 3)
    (2, 4, 200.00), # iPhone 11 Pro (ID 2) com 512GB (ID 4)

    # --- iPhone 11 Pro Max (até 512GB) ---
    (3, 1, 0.00), # iPhone 11 Pro Max (ID 3) com 64GB (ID 1)
    (3, 3, 150.00), # iPhone 11 Pro Max (ID 3) com 256GB (ID 3)
    (3, 4, 200.00), # iPhone 11 Pro Max (ID 3) com 512GB (ID 4)

    # --- iPhone 12 Mini (até 256GB) ---
    (4, 1, 0.00), # iPhone 12 Mini (ID 4) com 64GB (ID 1)
    (4, 2, 0.00), # iPhone 12 Mini (ID 4) com 128GB (ID 2)
    (4, 3, 100.00), # iPhone 12 Mini (ID 4) com 256GB (ID 3)

    # --- iPhone 12 (até 256GB) ---
    (5, 1, 0.00), # iPhone 12 (ID 5) com 64GB (ID 1)
    (5, 2, 0.00), # iPhone 12 (ID 5) com 128GB (ID 2)
    (5, 3, 100.00), # iPhone 12 (ID 5) com 256GB (ID 3)

    # --- iPhone 12 Pro (até 1024GB/1TB) ---
    (6, 2, 0.00), # iPhone 12 Pro (ID 6) com 128GB (ID 2)
    (6, 3, 100.00), # iPhone 12 Pro (ID 6) com 256GB (ID 3)
    (6, 4, 200.00), # iPhone 12 Pro (ID 6) com 512GB (ID 4)
    (6, 5, 250.00), # iPhone 12 Pro (ID 6) com 1TB (ID 5)

    # --- iPhone 12 Pro Max (até 1024GB/1TB) ---
    (7, 2, 0.00), # iPhone 12 Pro Max (ID 7) com 128GB (ID 2)
    (7, 3, 100.00), # iPhone 12 Pro Max (ID 7) com 256GB (ID 3)
    (7, 4, 200.00), # iPhone 12 Pro Max (ID 7) com 512GB (ID 4)
    (7, 5, 250.00), # iPhone 12 Pro Max (ID 7) com 1TB (ID 5)

    # --- iPhone 13 Mini (até 512GB) ---
    (8, 2, 0.00), # iPhone 13 Mini (ID 8) com 128GB (ID 2)
    (8, 3, 150.00), # iPhone 13 Mini (ID 8) com 256GB (ID 3)
    (8, 4, 200.00), # iPhone 13 Mini (ID 8) com 512GB (ID 4)

    # --- iPhone 13 (até 512GB) ---
    (9, 2, 0.00), # iPhone 13 (ID 9) com 128GB (ID 2)
    (9, 3, 150.00), # iPhone 13 (ID 9) com 256GB (ID 3)
    (9, 4, 250.00), # iPhone 13 (ID 9) com 512GB (ID 4)

    # --- iPhone 13 Pro (até 1024GB/1TB) ---
    (10, 2, 0.00), # iPhone 13 Pro (ID 10) com 128GB (ID 2)
    (10, 3, 150.00), # iPhone 13 Pro (ID 10) com 256GB (ID 3)
    (10, 4, 250.00), # iPhone 13 Pro (ID 10) com 512GB (ID 4)
    (10, 5, 300.00), # iPhone 13 Pro (ID 10) com 1TB (ID 5)

    # --- iPhone 13 Pro Max (até 1024GB/1TB) ---
    (11, 2, 0.00), # iPhone 13 Pro Max (ID 11) com 128GB (ID 2)
    (11, 3, 150.00), # iPhone 13 Pro Max (ID 11) com 256GB (ID 3)
    (11, 4, 250.00), # iPhone 13 Pro Max (ID 11) com 512GB (ID 4)
    (11, 5, 300.00), # iPhone 13 Pro Max (ID 11) com 1TB (ID 5)

    # --- iPhone 14 (até 512GB) ---
    (13, 2, 0.00), # iPhone 14 (ID 13) com 128GB (ID 2)
    (13, 3, 150.00), # iPhone 14 (ID 13) com 256GB (ID 3)
    (13, 4, 200.00), # iPhone 14 (ID 13) com 512GB (ID 4)

    # --- iPhone 14 Plus (até 512GB) ---
    (12, 2, 0.00), # iPhone 14 Plus (ID 12) com 128GB (ID 2)
    (12, 3, 100.00), # iPhone 14 Plus (ID 12) com 256GB (ID 3)
    (12, 4, 200.00), # iPhone 14 Plus (ID 12) com 512GB (ID 4)

    # --- iPhone 14 Pro (até 1024GB/1TB) ---
    (14, 2, 0.00), # iPhone 14 Pro (ID 14) com 128GB (ID 2)
    (14, 3, 150.00), # iPhone 14 Pro (ID 14) com 256GB (ID 3)
    (14, 4, 250.00), # iPhone 14 Pro (ID 14) com 512GB (ID 4)
    (14, 5, 300.00), # iPhone 14 Pro (ID 14) com 1TB (ID 5)

    # --- iPhone 14 Pro Max (até 1024GB/1TB) ---
    (15, 2, 0.00), # iPhone 14 Pro Max (ID 15) com 128GB (ID 2)
    (15, 3, 150.00), # iPhone 14 Pro Max (ID 15) com 256GB (ID 3)
    (15, 4, 250.00), # iPhone 14 Pro Max (ID 15) com 512GB (ID 4)
    (15, 5, 300.00), # iPhone 14 Pro Max (ID 15) com 1TB (ID 5)

    # --- iPhone 15 (até 1024GB/1TB) ---
    (17, 2, 0.00), # iPhone 15 (ID 17) com 128GB (ID 2)
    (17, 3, 150.00), # iPhone 15 (ID 17) com 256GB (ID 3)
    (17, 4, 200.00), # iPhone 15 (ID 17) com 512GB (ID 4)
    (17, 5, 250.00), # iPhone 15 (ID 17) com 1TB (ID 5)

    # --- iPhone 15 Plus (até 1024GB/1TB) ---
    (16, 2, 0.00), # iPhone 15 Plus (ID 16) com 128GB (ID 2)
    (16, 3, 150.00), # iPhone 15 Plus (ID 16) com 256GB (ID 3)
    (16, 4, 200.00), # iPhone 15 Plus (ID 16) com 512GB (ID 4)
    (16, 5, 250.00), # iPhone 15 Plus (ID 16) com 1TB (ID 5)

    # --- iPhone 15 Pro (até 1024GB/1TB) ---
    (18, 2, 0.00), # iPhone 15 Pro (ID 18) com 128GB (ID 2)
    (18, 3, 150.00), # iPhone 15 Pro (ID 18) com 256GB (ID 3)
    (18, 4, 250.00), # iPhone 15 Pro (ID 18) com 512GB (ID 4)
    (18, 5, 350.00), # iPhone 15 Pro (ID 18) com 1TB (ID 5)

    # --- iPhone 15 Pro Max (até 1024GB/1TB) ---
    (19, 2, 0.00), # iPhone 15 Pro Max (ID 19) com 128GB (ID 2)
    (19, 3, 150.00), # iPhone 15 Pro Max (ID 19) com 256GB (ID 3)
    (19, 4, 250.00), # iPhone 15 Pro Max (ID 19) com 512GB (ID 4)
    (19, 5, 350.00), # iPhone 15 Pro Max (ID 19) com 1TB (ID 5)

    # --- iPhone 16e (até 512GB) ---
    (20, 2, 0.00), # iPhone 16e (ID 20) com 128GB (ID 2)
    (20, 3, 200.00), # iPhone 16e (ID 20) com 256GB (ID 3)
    (20, 4, 250.00), # iPhone 16e (ID 20) com 512GB (ID 4)

    # --- iPhone 16 (até 1024GB/1TB) ---
    (22, 2, 0.00), # iPhone 16 (ID 22) com 128GB (ID 2)
    (22, 3, 200.00), # iPhone 16 (ID 22) com 256GB (ID 3)
    (22, 4, 250.00), # iPhone 16 (ID 22) com 512GB (ID 4)
    (22, 5, 350.00), # iPhone 16 (ID 22) com 1TB (ID 5)

    # --- iPhone 16 Plus (até 1024GB/1TB) ---
    (21, 2, 0.00), # iPhone 16 Plus (ID 21) com 128GB (ID 2)
    (21, 3, 150.00), # iPhone 16 Plus (ID 21) com 256GB (ID 3)
    (21, 4, 200.00), # iPhone 16 Plus (ID 21) com 512GB (ID 4)
    (21, 5, 250.00), # iPhone 16 Plus (ID 21) com 1TB (ID 5)

    # --- iPhone 16 Pro (até 1024GB/1TB) ---
    (23, 2, 0.00), # iPhone 16 Pro (ID 23) com 128GB (ID 2)
    (23, 3, 150.00), # iPhone 16 Pro (ID 23) com 256GB (ID 3)
    (23, 4, 250.00), # iPhone 16 Pro (ID 23) com 512GB (ID 4)
    (23, 5, 350.00), # iPhone 16 Pro (ID 23) com 1TB (ID 5)

    # --- iPhone 16 Pro Max (até 1024GB/1TB) ---
    (24, 2, 0.00), # iPhone 16 Pro Max (ID 24) com 128GB (ID 2)
    (24, 3, 150.00), # iPhone 16 Pro Max (ID 24) com 256GB (ID 3)
    (24, 4, 250.00), # iPhone 16 Pro Max (ID 24) com 512GB (ID 4)
    (24, 5, 350.00)  # iPhone 16 Pro Max (ID 24) com 1TB (ID 5)
    ]

    # Para a tabela 'componentes'
    # Estrutura: (id, nome_componente)
    componentes_para_inserir = [
        (1, 'Tela Ruim'),
        (2, 'Tela não Funcional'),
        (3, 'Face-iD'),
        (4, 'Bateria'),
        (5, 'Câmera Traseira'),
        (6, 'Camera Frontal'),
        (7, 'Tampa Traseira'),
        (8, 'Alto Falantes'),
        (9, 'Carregamento'),
        (10, 'Peça desconhecida')
    ]

    # Para a tabela 'perguntas_avaliacao'
    # Estrutura: (id, texto_pergunta, componente_id)
    perguntas_para_inserir = [
        (1, 'A tela tem alguma marca severa, mancha, trincado ou riscados profundos?', 1),
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
    
    # Lista de impactos para inserir na tabela 'impacto_respostas'
    # Estrutura da tupla: (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto)

    impactos_para_inserir = [
        # --- iPhone 11 (ID 1) ---
        (1, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -150.00),
        (1, PERGUNTA_TELA_RUIM, 'Sim', -100.00),
        (1, PERGUNTA_BATERIA_RUIM, 'Não', -50.00),
        (1, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (1, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (1, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -200.00),
        (1, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (1, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (1, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (1, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -100.00),

        # --- iPhone 11 Pro (ID 2) ---
        (2, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -200.00),
        (2, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (2, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (2, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (2, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (2, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (2, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (2, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (2, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (2, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -150.00),

        # --- iPhone 11 Pro Max (ID 3) ---
        (3, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -200.00),
        (3, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (3, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (3, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (3, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (3, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (3, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (3, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (3, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (3, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -150.00),

        # --- iPhone 12 Mini (ID 4) ---
        (4, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -250.00),
        (4, PERGUNTA_TELA_RUIM, 'Sim', -100.00),
        (4, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (4, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (4, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (4, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (4, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (4, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (4, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (4, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 12 (ID 5) ---
        (5, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -250.00),
        (5, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (5, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (5, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (5, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (5, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (5, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (5, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (5, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (5, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 12 Pro (ID 6) ---
        (6, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -250.00),
        (6, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (6, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (6, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (6, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (6, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (6, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (6, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (6, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (6, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

         # --- iPhone 12 Pro Max (ID 7) ---
        (7, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00),
        (7, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (7, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (7, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (7, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (7, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (7, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (7, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (7, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (7, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 13 Mini (ID 8) ---
        (8, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -250.00),
        (8, PERGUNTA_TELA_RUIM, 'Sim', -200.00),
        (8, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (8, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (8, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (8, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (8, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (8, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (8, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (8, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 13 (ID 9) ---
        (9, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -300.00),
        (9, PERGUNTA_TELA_RUIM, 'Sim', -150.00),
        (9, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (9, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (9, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (9, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (9, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (9, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (9, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (9, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 13 Pro (ID 10) ---
        (10, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -800.00),
        (10, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (10, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (10, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (10, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (10, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (10, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (10, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (10, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (10, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 13 Pro Max (ID 11) ---
        (11, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1000.00),
        (11, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (11, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (11, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (11, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (11, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (11, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (11, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (11, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (11, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 14 Plus (ID 12) ---
        (12, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -400.00),
        (12, PERGUNTA_TELA_RUIM, 'Sim', -200.00),
        (12, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (12, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (12, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (12, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (12, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (12, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (12, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (12, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 14 (ID 13) ---
        (13, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', 500.00),
        (13, PERGUNTA_TELA_RUIM, 'Sim', -250.00),
        (13, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (13, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (13, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (13, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (13, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (13, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (13, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (13, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -200.00),

        # --- iPhone 14 Pro (ID 14) ---
        (14, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1000.00),
        (14, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (14, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (14, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (14, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (14, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (14, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (14, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (14, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (14, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 14 Pro Max (ID 15) ---
        (15, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1200.00),
        (15, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (15, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (15, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (15, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (15, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (15, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (15, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (15, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (15, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 15 Plus (ID 16) ---
        (16, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00),
        (16, PERGUNTA_TELA_RUIM, 'Sim', -350.00),
        (16, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (16, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (16, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (16, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (16, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (16, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (16, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (16, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -250.00),

        # --- iPhone 15 (ID 17) ---
        (17, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -600.00),
        (17, PERGUNTA_TELA_RUIM, 'Sim', -350.00),
        (17, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (17, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (17, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (17, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (17, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (17, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (17, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (17, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 15 Pro (ID 18) ---
        (18, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1400.00),
        (18, PERGUNTA_TELA_RUIM, 'Sim', -600.00),
        (18, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (18, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (18, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (18, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (18, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (18, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (18, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (18, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 15 Pro Max (ID 19) ---
        (19, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1200.00),
        (19, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (19, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (19, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (19, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (19, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (19, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (19, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (19, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (19, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 16e (ID 20) ---
        (20, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -700.00),
        (20, PERGUNTA_TELA_RUIM, 'Sim', -300.00),
        (20, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (20, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (20, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (20, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (20, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (20, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (20, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (20, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 16 Plus (ID 21) ---
        (21, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -800.00),
        (21, PERGUNTA_TELA_RUIM, 'Sim', -400.00),
        (21, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (21, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (21, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (21, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (21, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (21, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (21, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (21, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),
        
        # --- iPhone 16 (ID 22) ---
        (22, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -800.00),
        (22, PERGUNTA_TELA_RUIM, 'Sim', -400.00),
        (22, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (22, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (22, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (22, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (22, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (22, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (22, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (22, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -300.00),

        # --- iPhone 16 Pro (ID 23) ---
        (23, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1500.00),
        (23, PERGUNTA_TELA_RUIM, 'Sim', -500.00),
        (23, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (23, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (23, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (23, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (23, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (23, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (23, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (23, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -400.00),

        # --- iPhone 16 Pro Max (ID 24) ---
        (24, PERGUNTA_TELA_NAO_FUNCIONA, 'Não', -1800.00),
        (24, PERGUNTA_TELA_RUIM, 'Sim', -600.00),
        (24, PERGUNTA_BATERIA_RUIM, 'Não', -80.00),
        (24, PERGUNTA_FACEID_NAO_FUNCIONA, 'Não', -200.00),
        (24, PERGUNTA_TAMPA_QUEBRADA, 'Sim', -100.00),
        (24, PERGUNTA_CAMERA_TRASEIRA_RUIM, 'Não', -250.00),
        (24, PERGUNTA_CAMERA_FRONTAL_RUIM, 'Não', -100.00),
        (24, PERGUNTA_SOM_RUIM, 'Não', -50.00),
        (24, PERGUNTA_CARREGAMENTO_RUIM, 'Não', -100.00),
        (24, PERGUNTA_PECA_DESCONHECIDA, 'Sim', -400.00),

    ]
    
    # --- LÓGICA DE INSERÇÃO ---
    conexao = None
    try:
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()

        # O comando "INSERT OR IGNORE" é útil para não dar erro se você rodar este script várias vezes.
        
        print("\nPopulando tabelas mestras...")
        cursor.executemany("INSERT OR IGNORE INTO modelos_iphone (id, nome_modelo, cor_modelo, valor_base, imagem_padrao_url) VALUES (?, ?, ?, ?, ?)", modelos_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO cores (id, nome_cor, codigo_hex) VALUES (?, ?, ?)", cores_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO armazenamentos (id, capacidade_gb) VALUES (?, ?)", armazenamentos_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO componentes (id, nome_componente) VALUES (?, ?)", componentes_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO perguntas_avaliacao (id, texto_pergunta, componente_id) VALUES (?, ?, ?)", perguntas_para_inserir)

        print("Populando tabelas de ligação e de impacto...")
        cursor.executemany("INSERT OR IGNORE INTO modelos_cores (modelo_id, cor_id, imagem_url) VALUES (?, ?, ?)", modelos_cores_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO modelos_armazenamentos (modelo_id, armazenamento_id, modificador_valor) VALUES (?, ?, ?)", modelos_armazenamentos_para_inserir)
        cursor.executemany("INSERT OR IGNORE INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto) VALUES (?, ?, ?, ?)", impactos_para_inserir)

        conexao.commit()
        print("\nTodas as tabelas foram populadas com os dados fornecidos.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao popular as tabelas: {e}")
        if conexao:
            conexao.rollback() # Desfaz alterações em caso de erro

    finally:
        if conexao:
            conexao.close()
            print("Conexão com o banco de dados fechada.")


# --- Bloco de Execução Principal ---
# Garante que o código só será executado quando você rodar 'python setup_database.py'
if __name__ == '__main__':
    # Primeiro, garanta que as tabelas existam
    criar_tabelas() 
    
    # Depois, popule as tabelas com os dados
    popular_tabelas()
    
    print("\nScript de setup do banco de dados concluído!")
