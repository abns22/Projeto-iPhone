#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_resumo_formatos():
    """Testa diferentes formatos de resumo_respostas para verificar se a lógica funciona corretamente."""
    
    # Teste 1: Lista de objetos (formato atual do frontend)
    resumo_lista = [
        {"pergunta": "Tela quebrada?", "resposta": "Sim"},
        {"pergunta": "Bateria", "resposta": "Boa"},
        {"pergunta": "IMEI", "resposta": "123456789"}
    ]
    
    # Teste 2: Dicionário (formato antigo)
    resumo_dict = {
        "Tela quebrada?": "Sim",
        "Bateria": "Boa", 
        "IMEI": "123456789"
    }
    
    # Teste 3: Lista de strings
    resumo_strings = ["Pergunta 1: Sim", "Pergunta 2: Não", "IMEI: 123456789"]
    
    # Teste 4: Outro tipo
    resumo_outro = "Resumo simples"
    
    def processar_resumo(resumo_respostas):
        """Função que simula a lógica do backend para processar resumo_respostas"""
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
    
    print("=== TESTE DE FORMATOS DE RESUMO ===\n")
    
    print("1. Teste com lista de objetos (formato atual):")
    resultado1 = processar_resumo(resumo_lista)
    print(resultado1)
    print()
    
    print("2. Teste com dicionário (formato antigo):")
    resultado2 = processar_resumo(resumo_dict)
    print(resultado2)
    print()
    
    print("3. Teste com lista de strings:")
    resultado3 = processar_resumo(resumo_strings)
    print(resultado3)
    print()
    
    print("4. Teste com outro tipo:")
    resultado4 = processar_resumo(resumo_outro)
    print(resultado4)
    print()
    
    print("=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_resumo_formatos()
