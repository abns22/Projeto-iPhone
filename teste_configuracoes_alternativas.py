#!/usr/bin/env python3
"""
Teste de configurações SMTP alternativas para PythonAnywhere
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def testar_configuracao(config):
    """Testa uma configuração SMTP específica"""
    print(f"\n🔧 Testando: {config['nome']}")
    print(f"   Servidor: {config['servidor']}")
    print(f"   Porta: {config['porta']}")
    print(f"   SSL: {config['ssl']}")
    print(f"   TLS: {config['tls']}")
    
    try:
        # Cria contexto SSL
        context = ssl.create_default_context()
        
        # Conecta ao servidor
        if config['ssl']:
            server = smtplib.SMTP_SSL(config['servidor'], config['porta'], context=context, timeout=15)
        else:
            server = smtplib.SMTP(config['servidor'], config['porta'], timeout=15)
            if config['tls']:
                server.starttls(context=context)
        
        print("   ✅ Conexão estabelecida")
        
        # Autentica
        server.login('ogordogamer2@gmail.com', 'ylmu lcyn khlp ckpd')
        print("   ✅ Autenticação bem-sucedida")
        
        # Prepara mensagem de teste
        msg = MIMEMultipart()
        msg['From'] = 'ogordogamer2@gmail.com'
        msg['To'] = 'alfredo_gi@hotmail.com'
        msg['Subject'] = f'Teste {config["nome"]} - PythonAnywhere'
        
        body = f"""
        Teste de configuração: {config['nome']}
        
        Se você receber este email, esta configuração funciona no PythonAnywhere.
        
        Configurações:
        - Servidor: {config['servidor']}
        - Porta: {config['porta']}
        - SSL: {config['ssl']}
        - TLS: {config['tls']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Envia o email
        server.send_message(msg)
        print("   ✅ Email enviado com sucesso!")
        
        # Fecha conexão
        server.quit()
        print("   ✅ Conexão fechada")
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ ERRO DE AUTENTICAÇÃO: {e}")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"   ❌ ERRO DE CONEXÃO: {e}")
        return False
        
    except smtplib.SMTPServerDisconnected as e:
        print(f"   ❌ SERVIDOR DESCONECTADO: {e}")
        return False
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False

def main():
    """Função principal"""
    print("=== TESTE DE CONFIGURAÇÕES SMTP ALTERNATIVAS ===")
    print("Testando diferentes configurações para PythonAnywhere")
    
    # Configurações para testar
    configuracoes = [
        {
            'nome': 'Gmail TLS (Padrão)',
            'servidor': 'smtp.gmail.com',
            'porta': 587,
            'ssl': False,
            'tls': True
        },
        {
            'nome': 'Gmail SSL',
            'servidor': 'smtp.gmail.com',
            'porta': 465,
            'ssl': True,
            'tls': False
        },
        {
            'nome': 'Gmail TLS Alternativo',
            'servidor': 'smtp.gmail.com',
            'porta': 2525,
            'ssl': False,
            'tls': True
        },
        {
            'nome': 'Gmail Sem TLS',
            'servidor': 'smtp.gmail.com',
            'porta': 25,
            'ssl': False,
            'tls': False
        },
        {
            'nome': 'Outlook TLS',
            'servidor': 'smtp-mail.outlook.com',
            'porta': 587,
            'ssl': False,
            'tls': True
        },
        {
            'nome': 'Outlook SSL',
            'servidor': 'smtp-mail.outlook.com',
            'porta': 465,
            'ssl': True,
            'tls': False
        }
    ]
    
    resultados = []
    
    # Testa cada configuração
    for config in configuracoes:
        sucesso = testar_configuracao(config)
        resultados.append({
            'config': config,
            'sucesso': sucesso
        })
    
    # Resumo final
    print("\n" + "="*60)
    print("=== RESUMO DOS TESTES ===")
    
    sucessos = [r for r in resultados if r['sucesso']]
    falhas = [r for r in resultados if not r['sucesso']]
    
    print(f"✅ Configurações que funcionaram: {len(sucessos)}")
    for resultado in sucessos:
        config = resultado['config']
        print(f"   - {config['nome']} ({config['servidor']}:{config['porta']})")
    
    print(f"\n❌ Configurações que falharam: {len(falhas)}")
    for resultado in falhas:
        config = resultado['config']
        print(f"   - {config['nome']} ({config['servidor']}:{config['porta']})")
    
    # Recomendações
    print("\n=== RECOMENDAÇÕES ===")
    
    if sucessos:
        melhor_config = sucessos[0]['config']
        print(f"🎯 Use esta configuração no .env:")
        print(f"MAIL_SERVER={melhor_config['servidor']}")
        print(f"MAIL_PORT={melhor_config['porta']}")
        print(f"MAIL_USE_SSL={melhor_config['ssl']}")
        print(f"MAIL_USE_TLS={melhor_config['tls']}")
    else:
        print("❌ Nenhuma configuração funcionou!")
        print("🔧 Possíveis soluções:")
        print("   1. Verificar App Password do Gmail")
        print("   2. Contatar suporte do PythonAnywhere")
        print("   3. Considerar upgrade do plano")
        print("   4. Usar serviço de email alternativo")

if __name__ == "__main__":
    main()
