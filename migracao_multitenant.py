import sqlite3
import os

# Define o caminho para o banco de dados, garantindo que seja o correto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'frontend', 'banco.db')

def migrar_banco_para_multi_empresa():
    """
    Executa a migração do banco de dados para suportar múltiplas empresas (inquilinos).
    1. Cria a tabela 'empresas'.
    2. Adiciona a coluna 'empresa_id' às tabelas relevantes.
    3. Cria uma empresa padrão e associa todos os dados existentes a ela.
    """

    # --- 1. COMANDO PARA CRIAR A NOVA TABELA 'EMPRESAS' ---
    # Esta tabela guardará as informações de cada empresa cliente.
    sql_criar_tabela_empresas = """
    CREATE TABLE IF NOT EXISTS empresas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_empresa TEXT NOT NULL UNIQUE,
        logo_url TEXT,
        email_contato_principal TEXT,
        plano_ativo BOOLEAN DEFAULT TRUE,
        permite_ajuste_valores BOOLEAN DEFAULT FALSE,
        envia_email_orcamento BOOLEAN DEFAULT TRUE
    );
    """

    # --- 2. LISTA DE TABELAS QUE PRECISAM DA COLUNA 'empresa_id' ---
    # Todas as tabelas que guardam dados que pertencem a uma empresa específica.
    tabelas_para_alterar = [
        "usuarios",
        "modelos_iphone",
        "impacto_respostas",
        "modelos_cores",
        "modelos_armazenamentos"
        # Nota: Por enquanto, 'perguntas_avaliacao', 'cores' e 'armazenamentos' 
        # são globais para todas as empresas. Poderíamos mudar isso no futuro se necessário.
    ]

    conexao = None
    try:
        # Conecta ao banco de dados
        conexao = sqlite3.connect(DB_PATH)
        cursor = conexao.cursor()

        print("--- Iniciando migração do banco de dados para Multi-Empresa ---")

        # ETAPA A: Criar a tabela de empresas
        print("\n[ETAPA A] Criando a tabela 'empresas'...")
        cursor.execute(sql_criar_tabela_empresas)
        print(" -> Tabela 'empresas' pronta.")

        # ETAPA B: Adicionar a coluna 'empresa_id' às tabelas existentes
        print("\n[ETAPA B] Adicionando a coluna 'empresa_id' às tabelas...")
        for tabela in tabelas_para_alterar:
            try:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN empresa_id INTEGER REFERENCES empresas(id)")
                print(f" -> Coluna adicionada com sucesso à tabela '{tabela}'.")
            except sqlite3.OperationalError as e:
                # Este erro é esperado se a coluna já existir.
                if "duplicate column name" in str(e):
                    print(f" -> A coluna 'empresa_id' já existe na tabela '{tabela}'. Nenhuma ação necessária.")
                else:
                    raise e # Se for outro erro, queremos que o script pare.
        
        # ETAPA C: Adicionar uma empresa padrão para os dados existentes
        print("\n[ETAPA C] Inserindo uma empresa padrão para os dados atuais...")
        # INSERT OR IGNORE garante que não tentaremos inserir se o ID 1 já existir.
        cursor.execute("INSERT OR IGNORE INTO empresas (id, nome_empresa, permite_ajuste_valores) VALUES (1, 'Minha Empresa Principal', TRUE)")
        print(" -> Empresa padrão (ID 1) garantida.")

        # ETAPA D: Associar todos os dados existentes a esta primeira empresa
        print("\n[ETAPA D] Associando todos os dados existentes à empresa padrão...")
        for tabela in tabelas_para_alterar:
            # Atualiza apenas as linhas onde 'empresa_id' ainda não foi definido.
            cursor.execute(f"UPDATE {tabela} SET empresa_id = 1 WHERE empresa_id IS NULL")
        print(" -> Dados existentes associados com sucesso.")

        # Salva todas as alterações no banco de dados
        conexao.commit()
        print("\n--- Migração concluída com sucesso! ---")
        print("Seu banco de dados agora está pronto para a arquitetura multi-empresa.")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro crítico durante a migração: {e}")
        print("As alterações foram revertidas (rollback).")
        if conexao:
            conexao.rollback()

    finally:
        if conexao:
            conexao.close()
            print("\nConexão com o banco de dados fechada.")

# --- Bloco que executa a função quando o script é chamado diretamente ---
if __name__ == '__main__':
    migrar_banco_para_multi_empresa() 
