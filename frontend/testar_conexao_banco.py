#!/usr/bin/env python3
"""
Script para testar conexão com banco de dados MySQL no PythonAnywhere
"""

import mysql.connector

def testar_conexao(config):
    """Testa uma configuração de conexão"""
    try:
        print(f"\nTentando conectar com: {config['host']}")
        print(f"Usuário: {config['user']}")
        print(f"Database: {config['database']}")

        conn = mysql.connector.connect(**config)
        print("✅ Conexão bem-sucedida!")

        # Testa uma query simples
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM empresas")
        count = cursor.fetchone()[0]
        print(f"✅ Query testada com sucesso! Empresas encontradas: {count}")

        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Testa diferentes configurações de banco"""
    print("=== TESTE DE CONEXÃO COM BANCO DE DADOS ===")

    # Configurações possíveis para PythonAnywhere
    configuracoes = [
        {
            'name': 'Configuração 1 - Senha padrão',
            'config': {
                'database': 'abns22$default',
                'user': 'abns22',
                'password': 'icloudbz12031994@lF',
                'host': 'abns22.mysql.pythonanywhere-services.com',
                'port': 3306,
                'ssl_disabled': False,
                'ssl_verify_cert': False,
                'ssl_verify_identity': False
            }
        },
        {
            'name': 'Configuração 2 - Sem SSL',
            'config': {
                'database': 'abns22$default',
                'user': 'abns22',
                'password': 'icloudbz12031994@lF',
                'host': 'abns22.mysql.pythonanywhere-services.com',
                'port': 3306
            }
        },
        {
            'name': 'Configuração 3 - Host alternativo',
            'config': {
                'database': 'abns22$default',
                'user': 'abns22',
                'password': 'icloudbz12031994@lF',
                'host': 'abns22.mysql.pythonanywhere-services.com',
                'port': 3306,
                'ssl_disabled': True
            }
        },
        {
            'name': 'Configuração 4 - Sem especificar database',
            'config': {
                'user': 'abns22',
                'password': 'icloudbz12031994@lF',
                'host': 'abns22.mysql.pythonanywhere-services.com',
                'port': 3306,
                'ssl_disabled': False,
                'ssl_verify_cert': False,
                'ssl_verify_identity': False
            }
        }
    ]

    sucessos = []

    for config_info in configuracoes:
        print(f"\n{'='*50}")
        print(f"TESTANDO: {config_info['name']}")
        print(f"{'='*50}")

        if testar_conexao(config_info['config']):
            sucessos.append(config_info)

    print(f"\n{'='*50}")
    print("RESUMO DOS TESTES")
    print(f"{'='*50}")

    if sucessos:
        print(f"✅ {len(sucessos)} configuração(ões) funcionaram:")
        for i, config in enumerate(sucessos, 1):
            print(f"{i}. {config['name']}")
            print(f"   Host: {config['config']['host']}")
            print(f"   User: {config['config']['user']}")
            print(f"   Database: {config['config'].get('database', 'N/A')}")
    else:
        print("❌ Nenhuma configuração funcionou!")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("1. Verifique se o banco MySQL está ativo no PythonAnywhere")
        print("2. Confirme o nome do usuário e senha do banco")
        print("3. Verifique se o banco 'abns22$default' existe")
        print("4. Tente acessar o banco via interface web do PythonAnywhere")

if __name__ == '__main__':
    main()