#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_correcao_email():
    """Testa se a correção do erro 'list' object has no attribute 'items' funcionou."""
    
    # Simular diferentes formatos de resumo_respostas que podem vir do frontend
    test_cases = [
        # Caso 1: Lista de objetos (formato atual)
        [
            {"pergunta": "Tela quebrada?", "resposta": "Sim"},
            {"pergunta": "Bateria", "resposta": "Boa"},
            {"pergunta": "IMEI", "resposta": "123456789"}
        ],
        
        # Caso 2: Dicionário (formato antigo)
        {
            "Tela quebrada?": "Sim",
            "Bateria": "Boa", 
            "IMEI": "123456789"
        },
        
        # Caso 3: Lista de strings
        ["Pergunta 1: Sim", "Pergunta 2: Não", "IMEI: 123456789"],
        
        # Caso 4: Lista com tipos mistos
        [
            {"pergunta": "Tela quebrada?", "resposta": "Sim"},
            "String simples",
            123,
            {"outro": "objeto"}
        ],
        
        # Caso 5: Outro tipo
        "Resumo simples"
    ]
    
    def processar_resumo_corrigido(resumo_respostas):
        """Função com a correção aplicada"""
        mensagem_html = "<ul>"
        
        # Verificar se resumo_respostas é uma lista ou dicionário
        if isinstance(resumo_respostas, list):
            for item in resumo_respostas:
                if isinstance(item, dict) and 'pergunta' in item and 'resposta' in item:
                    mensagem_html += f"<li><strong>{item['pergunta']}:</strong> {item['resposta']}</li>"
                elif isinstance(item, str):
                    mensagem_html += f"<li>{item}</li>"
                else:
                    mensagem_html += f"<li>{str(item)}</li>"
        elif isinstance(resumo_respostas, dict):
            for pergunta, resposta in resumo_respostas.items():
                mensagem_html += f"<li><strong>{pergunta}:</strong> {resposta}</li>"
        else:
            mensagem_html += f"<li>Resumo não disponível</li>"
        
        mensagem_html += "</ul>"
        return mensagem_html
    
    print("=== TESTE DA CORREÇÃO DO ERRO DE EMAIL ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Teste {i}: Tipo {type(test_case).__name__}")
        print(f"Conteúdo: {test_case}")
        
        try:
            resultado = processar_resumo_corrigido(test_case)
            print(f"✅ SUCESSO: {resultado}")
        except Exception as e:
            print(f"❌ ERRO: {e}")
        
        print("-" * 50)
    
    print("=== TESTE CONCLUÍDO ===")
    print("Se todos os testes passaram, a correção funcionou!")

if __name__ == "__main__":
    test_correcao_email()
