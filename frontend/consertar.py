import os
import mysql.connector
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do seu arquivo .env local
load_dotenv()

# --- CONFIGURAÇÃO ---
# Lista dos IDs dos seus "modelos padrão" que precisam ser corrigidos.
# Estes são os modelos que foram criados pelo seu script de setup inicial.
modelos_a_corrigir = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
# --------------------

def get_db_connection():
    """Estabelece e retorna uma nova conexão com o banco de dados MySQL local."""
    try:
        # Usa as credenciais carregadas do arquivo .env
        conn = mysql.connector.connect(
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)) # Usa 3306 se a porta não for definida
        )
        return conn
    except mysql.connector.Error as e:
        print(f"ERRO DE CONEXÃO COM O MYSQL: {e}")
        return None

def consertar_dados():
    print("Iniciando script de correção de dados de impacto...")
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados. Abortando.")
        return

    try:
        # Usando 'with' para garantir que a conexão e o cursor sejam fechados
        with conn.cursor(dictionary=True) as cursor:
            
            # Pega todas as perguntas de avaliação existentes
            cursor.execute("SELECT id FROM perguntas_avaliacao")
            todas_perguntas = cursor.fetchall()
            if not todas_perguntas:
                print("Nenhuma pergunta de avaliação encontrada.")
                return

            print(f"Encontradas {len(todas_perguntas)} perguntas de avaliação.")
            
            # Itera sobre cada modelo que precisa ser corrigido
            for modelo_id in modelos_a_corrigir:
                print(f"\n--- Verificando Modelo ID: {modelo_id} ---")
                
                # Pega o empresa_id do modelo atual para usar nos inserts
                cursor.execute("SELECT empresa_id FROM modelos_iphone WHERE id = %s", (modelo_id,))
                resultado_empresa = cursor.fetchone()
                if not resultado_empresa:
                    print(f"AVISO: Modelo ID {modelo_id} não encontrado. Pulando.")
                    continue
                empresa_id_do_modelo = resultado_empresa['empresa_id']

                # Itera sobre cada pergunta para o modelo atual
                for pergunta in todas_perguntas:
                    pergunta_id = pergunta['id']
                    
                    # Verifica as respostas existentes para esta combinação
                    cursor.execute(
                        "SELECT resposta_que_gera_impacto FROM impacto_respostas WHERE modelo_id = %s AND pergunta_id = %s AND empresa_id = %s",
                        (modelo_id, pergunta_id, empresa_id_do_modelo)
                    )
                    respostas_existentes = {row['resposta_que_gera_impacto'] for row in cursor.fetchall()}
                    
                    # Se já existem as duas respostas ("Sim" e "Não"), está tudo certo.
                    if len(respostas_existentes) >= 2:
                        continue
                    
                    # Se não existe a resposta "Sim", cria ela com impacto 0
                    if "Sim" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Sim' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute(
                            "INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (%s, %s, 'Sim', 0.00, %s)",
                            (modelo_id, pergunta_id, empresa_id_do_modelo)
                        )

                    # Se não existe a resposta "Não", cria ela com impacto 0
                    if "Não" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Não' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute(
                            "INSERT INTO impacto_respostas (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id) VALUES (%s, %s, 'Não', 0.00, %s)",
                            (modelo_id, pergunta_id, empresa_id_do_modelo)
                        )

            # Salva todas as alterações feitas no banco de dados
            conn.commit()
            print("\nScript de correção concluído com sucesso!")

    except mysql.connector.Error as e:
        print(f"Ocorreu um erro com o MySQL durante a correção: {e}")
        print("Desfazendo alterações (rollback)...")
        conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Conexão com o MySQL fechada.")

# Roda a função principal quando o script é executado
if __name__ == '__main__':
    consertar_dados()