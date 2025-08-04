import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """
    Estabelece e retorna uma nova conexão com o banco de dados MySQL.
    """
    try:
        # Configurações do banco de dados (mesmas do app.py)
        DB_NAME = 'iphone_breakdown_db'
        DB_USER = 'alfredo'
        DB_PASS = 'icloudbz12031994@lF'
        DB_HOST = 'localhost'
        DB_PORT = '3306'
        
        conn_args = {
            'database': DB_NAME,
            'user': DB_USER,
            'password': DB_PASS,
            'host': DB_HOST,
            'port': DB_PORT
        }
        
        if DB_HOST and 'pythonanywhere' in DB_HOST:
            conn_args['ssl_ca'] = "/etc/ssl/certs/ca-certificates.crt"
            conn_args['ssl_verify_cert'] = True

        conn = mysql.connector.connect(**conn_args)
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

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

if __name__ == "__main__":
    print("Script iniciado!")
    garantir_respostas_completas()
    print("Script finalizado!") 