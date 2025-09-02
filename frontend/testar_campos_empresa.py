#!/usr/bin/env python3
"""
Script para testar se os novos campos de endereço da empresa foram criados corretamente.
Execute este script após executar as queries SQL no PythonAnywhere.
"""

import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório atual ao path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carrega as variáveis de ambiente
load_dotenv()

def testar_campos_empresa():
    """Testa se os novos campos de endereço da empresa existem no banco."""
    
    try:
        # Importa a função de conexão do app
        from app import get_db_connection
        
        print("🔍 Testando conexão com o banco de dados...")
        conn = get_db_connection()
        
        if not conn:
            print("❌ Falha na conexão com o banco de dados")
            return False
            
        print("✅ Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor(dictionary=True)
        
        # Verifica se as novas colunas existem
        print("\n🔍 Verificando se as novas colunas existem na tabela empresas...")
        
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'empresas'
            ORDER BY ORDINAL_POSITION
        """)
        
        colunas = cursor.fetchall()
        
        print(f"\n📋 Colunas encontradas na tabela 'empresas':")
        print("-" * 80)
        print(f"{'Coluna':<20} {'Tipo':<15} {'Nulo':<8} {'Padrão':<15}")
        print("-" * 80)
        
        campos_esperados = {
            'id': 'INT',
            'nome_empresa': 'VARCHAR',
            'cnpj': 'VARCHAR',
            'endereco_rua': 'VARCHAR',
            'endereco_numero': 'VARCHAR',
            'endereco_bairro': 'VARCHAR',
            'endereco_cidade': 'VARCHAR',
            'endereco_estado': 'VARCHAR',
            'logo_url': 'VARCHAR'
        }
        
        campos_encontrados = {}
        
        for coluna in colunas:
            nome = coluna['COLUMN_NAME']
            tipo = coluna['DATA_TYPE']
            nulo = coluna['IS_NULLABLE']
            padrao = coluna['COLUMN_DEFAULT'] or 'NULL'
            
            print(f"{nome:<20} {tipo:<15} {nulo:<8} {padrao:<15}")
            campos_encontrados[nome] = tipo
        
        # Verifica se todos os campos esperados existem
        print("\n🔍 Verificando campos obrigatórios...")
        campos_faltando = []
        
        for campo, tipo_esperado in campos_esperados.items():
            if campo in campos_encontrados:
                print(f"✅ {campo} - {campos_encontrados[campo]}")
            else:
                print(f"❌ {campo} - NÃO ENCONTRADO")
                campos_faltando.append(campo)
        
        if campos_faltando:
            print(f"\n⚠️  Campos faltando: {', '.join(campos_faltando)}")
            print("Execute as queries SQL no PythonAnywhere para criar esses campos.")
            return False
        else:
            print("\n🎉 Todos os campos esperados foram encontrados!")
        
        # Testa inserção de dados de exemplo
        print("\n🧪 Testando inserção de dados de exemplo...")
        
        try:
            # Insere uma empresa de teste
            sql_insert = """
                INSERT INTO empresas (
                    nome_empresa, cnpj, endereco_rua, endereco_numero, 
                    endereco_bairro, endereco_cidade, endereco_estado, 
                    email_contato_principal, max_usuarios, permite_ajuste_valores,
                    permite_link_convidado, envia_email_orcamento, 
                    envia_email_orcamento_link, plano_ativo
                ) VALUES (
                    'Empresa Teste', '12.345.678/0001-90', 'Rua das Flores', '123',
                    'Centro', 'São Paulo', 'SP', 'teste@empresa.com', 5, 1, 1, 1, 1, 1
                )
            """
            
            cursor.execute(sql_insert)
            empresa_teste_id = cursor.lastrowid
            print(f"✅ Empresa de teste inserida com ID: {empresa_teste_id}")
            
            # Busca os dados inseridos
            cursor.execute("""
                SELECT nome_empresa, cnpj, endereco_rua, endereco_numero, 
                       endereco_bairro, endereco_cidade, endereco_estado
                FROM empresas WHERE id = %s
            """, (empresa_teste_id,))
            
            empresa = cursor.fetchone()
            print(f"📋 Dados da empresa inserida:")
            print(f"   Nome: {empresa['nome_empresa']}")
            print(f"   CNPJ: {empresa['cnpj']}")
            print(f"   Endereço: {empresa['endereco_rua']}, {empresa['endereco_numero']}")
            print(f"   Bairro: {empresa['endereco_bairro']}")
            print(f"   Cidade: {empresa['endereco_cidade']} - {empresa['endereco_estado']}")
            
            # Remove a empresa de teste
            cursor.execute("DELETE FROM empresas WHERE id = %s", (empresa_teste_id,))
            print("✅ Empresa de teste removida")
            
        except Exception as e:
            print(f"❌ Erro ao testar inserção: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Teste concluído com sucesso!")
        print("✅ Os novos campos de endereço da empresa estão funcionando corretamente.")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste dos campos de endereço da empresa...")
    print("=" * 60)
    
    sucesso = testar_campos_empresa()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("🎉 TESTE PASSOU! Os campos estão funcionando corretamente.")
    else:
        print("❌ TESTE FALHOU! Verifique as queries SQL e tente novamente.")
    
    print("\n💡 Próximos passos:")
    print("1. Execute as queries SQL no PythonAnywhere")
    print("2. Execute este script novamente para verificar")
    print("3. Teste o sistema no navegador")
