# consertar_impactos.py

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO ---
# Coloque aqui os IDs dos seus "modelos padrão" que precisam ser corrigidos.
# Você pode encontrá-los no seu painel de admin ou diretamente no banco.
modelos_a_corrigir = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24] # <--- EDITE ESTA LISTA COM OS IDs CORRETOS!
# --------------------

def get_db_connection():
    """Estabelece e retorna uma nova conexão com o banco de dados."""
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
        print(f"ERRO DE CONEXÃO: {e}")
        return None

def consertar_dados():
    print("Iniciando script de correção de dados...")
    conn = get_db_connection()
    if not conn:
        print("Não foi possível conectar ao banco de dados. Abortando.")
        return

    # Usamos 'with' para garantir que o cursor e a transação sejam bem gerenciados
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # 1. Pega todas as perguntas de avaliação existentes
            cursor.execute("SELECT id FROM perguntas_avaliacao")
            todas_perguntas = cursor.fetchall()
            if not todas_perguntas:
                print("Nenhuma pergunta de avaliação encontrada.")
                return

            print(f"Encontradas {len(todas_perguntas)} perguntas de avaliação.")
            
            # Itera sobre cada modelo que precisa ser corrigido
            for modelo_id in modelos_a_corrigir:
                print(f"\n--- Verificando Modelo ID: {modelo_id} ---")
                empresa_id_do_modelo = None
                
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
                    
                    # Verifica as respostas existentes para esta combinação de modelo e pergunta
                    cursor.execute("""
                        SELECT resposta_que_gera_impacto FROM impacto_respostas
                        WHERE modelo_id = %s AND pergunta_id = %s AND empresa_id = %s
                    """, (modelo_id, pergunta_id, empresa_id_do_modelo))
                    
                    respostas_existentes = [row['resposta_que_gera_impacto'] for row in cursor.fetchall()]
                    
                    # Se já existem 2 ou mais respostas, está tudo certo, pula para a próxima
                    if len(respostas_existentes) >= 2:
                        continue
                    
                    # Se não existe a resposta "Sim", cria ela com impacto 0
                    if "Sim" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Sim' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute("""
                            INSERT INTO impacto_respostas 
                            (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id)
                            VALUES (%s, %s, 'Sim', 0.00, %s)
                        """, (modelo_id, pergunta_id, empresa_id_do_modelo))

                    # Se não existe a resposta "Não", cria ela com impacto 0
                    if "Não" not in respostas_existentes:
                        print(f"  -> Adicionando resposta 'Não' (impacto 0) para pergunta ID {pergunta_id}")
                        cursor.execute("""
                            INSERT INTO impacto_respostas 
                            (modelo_id, pergunta_id, resposta_que_gera_impacto, valor_do_impacto, empresa_id)
                            VALUES (%s, %s, 'Não', 0.00, %s)
                        """, (modelo_id, pergunta_id, empresa_id_do_modelo))

    print("\nScript de correção concluído!")
    conn.close()

# Roda a função principal
if __name__ == '__main__':
    consertar_dados()