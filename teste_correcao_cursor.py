#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a correção do problema "Cursor is not connected" (2055)
"""

import os
import sys

def test_cursor_management():
    """Testa o gerenciamento de cursor"""
    print("=== TESTE DE GERENCIAMENTO DE CURSOR ===")
    
    try:
        # Importar a função get_db_connection
        sys.path.append('frontend')
        from app import get_db_connection
        
        # Testar fluxo similar ao da função enviar_orcamento
        conn = get_db_connection()
        if not conn:
            print("❌ Falha ao conectar com o banco")
            return False
            
        cursor = conn.cursor()
        print("✅ Conexão e cursor criados")
        
        # Simular operações do banco
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Query de teste: {result}")
        
        # Simular commit
        conn.commit()
        print("✅ Commit realizado")
        
        # Agora simular busca de configurações de email (sem fechar conexão)
        cursor.execute("SELECT 2")
        result2 = cursor.fetchone()
        print(f"✅ Segunda query: {result2}")
        
        # Fechar no final
        cursor.close()
        conn.close()
        print("✅ Conexão e cursor fechados corretamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de gerenciamento: {e}")
        return False

def check_code_changes():
    """Verifica se as mudanças no código foram aplicadas corretamente"""
    print("\n=== VERIFICAÇÃO DAS MUDANÇAS NO CÓDIGO ===")
    
    try:
        with open('frontend/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se as mudanças foram aplicadas
        checks = [
            ("Finally block adicionado", "finally:" in content),
            ("Fechamento seguro no finally", "if 'cursor' in locals():" in content),
            ("Fechamento seguro no finally", "if 'conn' in locals():" in content)
        ]
        
        passed = 0
        for check_name, condition in checks:
            if condition:
                print(f"✅ {check_name}")
                passed += 1
            else:
                print(f"❌ {check_name}")
        
        print(f"\n📊 Verificações passaram: {passed}/{len(checks)}")
        
        return passed == len(checks)
        
    except Exception as e:
        print(f"❌ Erro ao verificar código: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE DA CORREÇÃO DO PROBLEMA 'CURSOR IS NOT CONNECTED'")
    print("=" * 60)
    
    # Executar testes
    tests = [
        test_cursor_management,
        check_code_changes
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro ao executar teste {test.__name__}: {e}")
            results.append(False)
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes passaram: {passed}/{total}")
    
    if passed == total:
        print("✅ Todos os testes passaram!")
        print("🎉 A correção do problema do cursor foi aplicada com sucesso")
    else:
        print("❌ Alguns testes falharam")
        print("🔧 Verificar se todas as mudanças foram aplicadas corretamente")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Reiniciar o servidor Flask")
    print("2. Testar o envio de orçamento real")
    print("3. Verificar se o erro 2055 não aparece mais")

if __name__ == "__main__":
    main()
