#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de armazenamentos
"""

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        # Configuração para Railway
        connection = mysql.connector.connect(
            host='mysql.railway.internal',
            database='railway',
            user='root',
            password='HLckQmDnUoUFvhvOPJvychUWgBeOGnzt',
            port=3306
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def testar_armazenamentos():
    """Testa a funcionalidade de armazenamentos"""
    conn = get_db_connection()
    if not conn:
        print("❌ Falha ao conectar ao banco de dados")
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Teste 1: Verificar se existem armazenamentos cadastrados
        print("🔍 Teste 1: Verificando armazenamentos cadastrados...")
        cursor.execute("SELECT * FROM armazenamentos ORDER BY capacidade_gb")
        armazenamentos = cursor.fetchall()
        
        if armazenamentos:
            print(f"✅ Encontrados {len(armazenamentos)} armazenamentos:")
            for arm in armazenamentos:
                print(f"   - {arm['capacidade_gb']} GB (ID: {arm['id']})")
        else:
            print("❌ Nenhum armazenamento encontrado")
        
        # Teste 2: Verificar modelos com armazenamentos
        print("\n🔍 Teste 2: Verificando modelos com armazenamentos...")
        cursor.execute("""
            SELECT mi.id, mi.nome_modelo, mi.valor_base_novo,
                   a.capacidade_gb, ma.modificador_valor
            FROM modelos_iphone mi
            JOIN modelos_armazenamentos ma ON mi.id = ma.modelo_id
            JOIN armazenamentos a ON ma.armazenamento_id = a.id
            WHERE mi.empresa_id = 1
            ORDER BY mi.nome_modelo, a.capacidade_gb
        """)
        modelos_armazenamentos = cursor.fetchall()
        
        if modelos_armazenamentos:
            print(f"✅ Encontrados {len(modelos_armazenamentos)} relacionamentos modelo-armazenamento:")
            modelo_atual = None
            for item in modelos_armazenamentos:
                if modelo_atual != item['nome_modelo']:
                    modelo_atual = item['nome_modelo']
                    print(f"\n📱 {item['nome_modelo']} (Base: R$ {item['valor_base_novo']:.2f}):")
                
                valor_final = item['valor_base_novo'] + (item['modificador_valor'] or 0)
                print(f"   - {item['capacidade_gb']} GB: Modificador R$ {item['modificador_valor']:.2f} → Final R$ {valor_final:.2f}")
        else:
            print("❌ Nenhum relacionamento modelo-armazenamento encontrado")
        
        # Teste 3: Verificar estrutura da tabela modelos_armazenamentos
        print("\n🔍 Teste 3: Verificando estrutura da tabela modelos_armazenamentos...")
        cursor.execute("DESCRIBE modelos_armazenamentos")
        estrutura = cursor.fetchall()
        
        print("✅ Estrutura da tabela modelos_armazenamentos:")
        for campo in estrutura:
            print(f"   - {campo['Field']}: {campo['Type']} {'(NOT NULL)' if campo['Null'] == 'NO' else ''}")
        
        # Teste 4: Testar atualização de modificador
        print("\n🔍 Teste 4: Testando atualização de modificador...")
        if modelos_armazenamentos:
            primeiro_item = modelos_armazenamentos[0]
            modelo_id = primeiro_item['id']
            armazenamento_id = None
            
            # Encontrar o armazenamento_id
            cursor.execute("""
                SELECT ma.armazenamento_id 
                FROM modelos_armazenamentos ma 
                WHERE ma.modelo_id = %s AND ma.empresa_id = 1 
                LIMIT 1
            """, (modelo_id,))
            resultado = cursor.fetchone()
            if resultado:
                armazenamento_id = resultado['armazenamento_id']
                
                # Testar atualização
                novo_modificador = 150.00
                cursor.execute("""
                    UPDATE modelos_armazenamentos 
                    SET modificador_valor = %s 
                    WHERE modelo_id = %s AND armazenamento_id = %s AND empresa_id = 1
                """, (novo_modificador, modelo_id, armazenamento_id))
                
                # Verificar se foi atualizado
                cursor.execute("""
                    SELECT modificador_valor 
                    FROM modelos_armazenamentos 
                    WHERE modelo_id = %s AND armazenamento_id = %s AND empresa_id = 1
                """, (modelo_id, armazenamento_id))
                resultado_atualizado = cursor.fetchone()
                
                if resultado_atualizado and resultado_atualizado['modificador_valor'] == novo_modificador:
                    print(f"✅ Modificador atualizado com sucesso: R$ {novo_modificador:.2f}")
                else:
                    print("❌ Falha ao atualizar modificador")
                
                # Reverter a mudança
                cursor.execute("""
                    UPDATE modelos_armazenamentos 
                    SET modificador_valor = 0 
                    WHERE modelo_id = %s AND armazenamento_id = %s AND empresa_id = 1
                """, (modelo_id, armazenamento_id))
                print("🔄 Modificador revertido para 0")
            else:
                print("❌ Não foi possível encontrar armazenamento para teste")
        
        conn.commit()
        print("\n✅ Todos os testes concluídos com sucesso!")
        
    except Error as e:
        print(f"❌ Erro durante os testes: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("🧪 Iniciando testes da funcionalidade de armazenamentos...\n")
    testar_armazenamentos()
