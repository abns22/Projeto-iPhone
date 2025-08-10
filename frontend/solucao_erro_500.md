# Solução para o Erro 500 na Rota /api/enviar-orcamento

## Problema Identificado

O erro 500 está ocorrendo na função `enviar_orcamento` no PythonAnywhere. Baseado na análise do código, as possíveis causas são:

1. **Problema de sintaxe na função** - Há um bloco `try` sem `except` correspondente
2. **Problema com a coluna `modelo_interesse`** - A coluna já existe no banco, mas pode haver algum problema na query
3. **Problema de configuração de email** - Erro no envio de email pode estar causando o erro 500

## Soluções

### 1. Verificar Logs do PythonAnywhere

Primeiro, verifique os logs de erro no PythonAnywhere:

1. Acesse o PythonAnywhere
2. Vá em "Web" → Seu site
3. Clique em "Error log" para ver os erros detalhados

### 2. Corrigir a Função enviar_orcamento

O problema principal está na estrutura da função. Você precisa corrigir o bloco `try-except`. 

**Substitua a função `enviar_orcamento` no arquivo `app.py` por esta versão corrigida:**

```python
@app.route('/api/enviar-orcamento', methods=['POST'])
def enviar_orcamento():
    try:
        print("=== INÍCIO DA FUNÇÃO enviar_orcamento ===")
        
        resp = require_login()
        if resp: 
            print("❌ Usuário não está logado")
            return resp
        
        # Verificar se o plano da empresa está ativo
        resp = require_plano_ativo()
        if resp: 
            print("❌ Plano da empresa não está ativo")
            return resp

        dados = request.json
        print(f"✅ Dados recebidos: {dados}")

        empresa_id_logada = session.get('empresa_id')
        if not empresa_id_logada:
            print("❌ Usuário não está associado a uma empresa válida")
            return jsonify({"mensagem": "Usuário não está associado a uma empresa válida"}), 400

        usuario_id_logado = session.get('user_id')
        if not usuario_id_logado:
            print("❌ Usuário não autenticado")
            return jsonify({"mensagem": "Usuário não autenticado"}), 400
        email_usuario_logado = session.get('usuario_email')

        print(f"✅ Dados da sessão: empresa_id={empresa_id_logada}, usuario_id={usuario_id_logado}")

        conn = None
        try:
            print("🔄 Conectando ao banco de dados...")
            conn = get_db_connection()
            if not conn:
                print("❌ Falha ao conectar ao banco de dados")
                return jsonify({"mensagem": "Erro de conexão com o banco de dados"}), 500
                
            cursor = conn.cursor(dictionary=True)
            print("✅ Conexão com banco estabelecida")

            modelo_nome = dados.get('modelo')

            cursor.execute(
                "SELECT id, valor_base_novo FROM modelos_iphone WHERE nome_modelo = %s AND empresa_id = %s",
                (modelo_nome, empresa_id_logada)
            )
            modelo_row = cursor.fetchone()

            if not modelo_row:
                return jsonify({"mensagem": "Erro: Modelo não encontrado para esta empresa."}), 400

            modelo_id = modelo_row['id']
            valor_base_db = modelo_row['valor_base_novo']

            try:
                # Buscar dados do usuário logado no banco de dados
                cursor.execute("SELECT nome_completo, telefone FROM usuarios WHERE id = %s", (usuario_id_logado,))
                dados_usuario = cursor.fetchone()
                
                if dados_usuario is None:
                    dados_usuario = {'nome_completo': 'Não informado', 'telefone': 'Não informado'}
                
                # Verificar se dados do cliente foram preenchidos na nova tela
                dados_cliente_preenchidos = dados.get('dadosClientePreenchidos', False)
                
                if dados_cliente_preenchidos:
                    # Usar dados preenchidos pelo cliente
                    nome_cliente_final = dados.get('nomeCliente', 'Não informado')
                    telefone_cliente_final = dados.get('telefoneCliente', 'Não informado')
                    email_cliente_final = dados.get('emailCliente', '')
                    modelo_interesse = dados.get('modeloInteresse', '')
                else:
                    # Usar dados do usuário logado como fallback
                    nome_cliente_final = dados.get('nomeCliente')
                    if not nome_cliente_final or nome_cliente_final == 'None':
                        nome_cliente_final = dados_usuario.get('nome_completo', 'Não informado')
                    
                    telefone_cliente_final = dados.get('telefoneCliente')
                    if not telefone_cliente_final or telefone_cliente_final == 'None':
                        telefone_cliente_final = dados_usuario.get('telefone', 'Não informado')
                    
                    email_cliente_final = ''
                    modelo_interesse = ''
                
                # Debug: verificar dados coletados
                print(f"DEBUG - Dados preenchidos: {dados_cliente_preenchidos}")
                print(f"DEBUG - Dados do frontend: nomeCliente={dados.get('nomeCliente')}, telefoneCliente={dados.get('telefoneCliente')}")
                print(f"DEBUG - Email cliente: {email_cliente_final}, Modelo interesse: {modelo_interesse}")
                print(f"DEBUG - Dados finais: nome={nome_cliente_final}, telefone={telefone_cliente_final}")
                
                # Garantir que cursor.fetchone() foi chamado antes de qualquer outra operação
                cursor.fetchall()  # Limpa qualquer resultado pendente
                
                cor_selecionada = dados.get('cor', 'N/A')
            except Exception as e:
                print(f"Erro ao processar dados do cliente: {e}")
                nome_cliente_final = "Não informado"
                telefone_cliente_final = "Não informado"
                email_cliente_final = ""
                modelo_interesse = ""
                cor_selecionada = dados.get('cor', 'N/A')
                
            armazenamento_selecionado = dados.get('armazenamento', 'N/A')
            imei = dados.get('imei', 'N/A')
            valor_final_calculado = float(dados.get('valor', 0.0))
            resumo_json = json.dumps(dados.get('resumo', []))

            try:
                # Limpar qualquer resultado pendente antes de executar o INSERT
                cursor.fetchall()
                
                sql_insert = """
                    INSERT INTO avaliacoes_concluidas (
                        empresa_id, usuario_id, nome_cliente_final, email_cliente_final, telefone_cliente_final,
                        modelo_interesse, modelo_iphone_id, cor_selecionada, armazenamento_selecionado, imei,
                        valor_base_calculado, valor_final_calculado, resumo_respostas
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Debug dos valores antes do INSERT
                print("\nDEBUG - Valores para INSERT:")
                print(f"empresa_id_logada: {empresa_id_logada}")
                print(f"usuario_id_logado: {usuario_id_logado}")
                print(f"nome_cliente_final: {nome_cliente_final}")
                print(f"email_cliente_final: {email_cliente_final}")
                print(f"telefone_cliente_final: {telefone_cliente_final}")
                print(f"modelo_interesse: {modelo_interesse}")
                print(f"modelo_id: {modelo_id}")
                print(f"cor_selecionada: {cor_selecionada}")
                print(f"armazenamento_selecionado: {armazenamento_selecionado}")
                print(f"imei: {imei}")
                print(f"valor_base_db: {valor_base_db}")
                print(f"valor_final_calculado: {valor_final_calculado}")
                
                cursor.execute(sql_insert, (
                    empresa_id_logada, usuario_id_logado, nome_cliente_final, email_cliente_final, telefone_cliente_final,
                    modelo_interesse, modelo_id, cor_selecionada, armazenamento_selecionado, imei,
                    valor_base_db, valor_final_calculado, resumo_json
                ))
                
                conn.commit()
                print("✅ Avaliação salva com sucesso no banco de dados.")
                
            except mysql.connector.Error as e:
                print(f"❌ Erro MySQL ao salvar avaliação: {e}")
                if conn:
                    conn.rollback()
                raise
            except Exception as e:
                print(f"❌ Erro inesperado ao salvar avaliação: {e}")
                if conn:
                    conn.rollback()
                raise

        except mysql.connector.Error as e:
            if conn: conn.rollback()
            print(f"Erro de MySQL ao salvar avaliação: {e}")
            return jsonify({"mensagem": "Erro de banco de dados"}), 500
        finally:
            if conn:
                cursor.close()
                conn.close()

        try:
            # Montar seção de dados do cliente baseado se foram preenchidos ou não
            secao_cliente = ""
            if dados.get('dadosClientePreenchidos', False):
                secao_cliente = f"""
            Dados do Cliente:
            - Nome: {nome_cliente_final}
            - Telefone: {telefone_cliente_final}
            - E-mail: {email_cliente_final if email_cliente_final else 'Não informado'}
            - Modelo de Interesse: {modelo_interesse if modelo_interesse else 'Não informado'}
            """
            else:
                secao_cliente = f"""
            Dados do Cliente:
            - Dados do cliente não foram informados
            - Usuário do sistema: {nome_cliente_final}
            - Telefone do usuário: {telefone_cliente_final}
            """

            corpo_email = f"""
            Novo Orçamento Recebido!
            -------------------------
            {secao_cliente}
            Detalhes do Aparelho:
            - Modelo: {dados.get('modelo')}
            - Cor: {dados.get('cor')}
            - Armazenamento: {dados.get('armazenamento')}
            - IMEI: {dados.get('imei')}

            Diagnóstico:
            """
            for item in dados.get('resumo', []):
                if 'pergunta' in item and 'resposta' in item:
                    corpo_email += f"- {item['pergunta']}: {item['resposta']}\n"

            corpo_email += f"""
            -------------------------
            VALOR FINAL ESTIMADO: R$ {dados.get('valor')}
            """

            # Verificar se a empresa tem permissão para enviar email
            envia_email = session.get('envia_email_orcamento', True)  # Padrão: True para manter compatibilidade

            if envia_email:
                # Buscar email de contato da empresa
                conn_email = get_db_connection()
                if conn_email:
                    try:
                        cursor_email = conn_email.cursor(dictionary=True)
                        cursor_email.execute("SELECT email_contato_principal FROM empresas WHERE id = %s", (empresa_id_logada,))
                        empresa = cursor_email.fetchone()
                        email_destino = empresa['email_contato_principal'] if empresa and empresa['email_contato_principal'] else None
                        cursor_email.close()
                    except Exception as e:
                        print(f"Erro ao buscar email da empresa: {e}")
                        email_destino = None
                    finally:
                        conn_email.close()
                else:
                    email_destino = None

                if email_destino and email_destino.strip():
                    try:
                        print("\n=== PREPARANDO ENVIO DE EMAIL ===")
                        print(f"Configurações:")
                        print(f"- Servidor: {app.config['MAIL_SERVER']}")
                        print(f"- Porta: {app.config['MAIL_PORT']}")
                        print(f"- TLS: {app.config['MAIL_USE_TLS']}")
                        print(f"- SSL: {app.config['MAIL_USE_SSL']}")
                        print(f"- Destinatário: {email_destino}")
                        
                        # Limpa caracteres especiais do assunto
                        assunto_limpo = f"Novo Orçamento de Avaliação para {dados.get('modelo')}".encode('ascii', 'ignore').decode('ascii')
                        print(f"Assunto preparado: {assunto_limpo}")

                        msg = Message(
                            subject=assunto_limpo,
                            sender=("Sua Calculadora de iPhones", app.config['MAIL_USERNAME']),
                            recipients=[email_destino.strip()]
                        )
                        
                        # Limpa caracteres especiais do corpo
                        corpo_limpo = corpo_email.encode('utf-8', 'ignore').decode('utf-8')
                        msg.body = corpo_limpo
                        
                        print("Mensagem preparada, tentando enviar...")
                        
                        with app.app_context():
                            mail.send(msg)
                        print("✅ Email enviado com sucesso!")
                        
                    except Exception as e:
                        print("\n❌ ERRO NO ENVIO DE EMAIL")
                        print(f"Tipo do erro: {type(e).__name__}")
                        print(f"Mensagem: {str(e)}")
                        print(f"Detalhes:")
                        print(f"- Email destino: {email_destino}")
                        print(f"- Empresa ID: {empresa_id_logada}")
                        # Não fazer raise aqui, apenas logar o erro
                else:
                    print(f"❌ Email da empresa não encontrado ou vazio para empresa ID: {empresa_id_logada}")

            return jsonify({"mensagem": "Orçamento enviado com sucesso para a nossa equipe e registrado!"})

        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return jsonify({"mensagem": "Avaliação registrada, mas falha ao enviar o e-mail."}), 500
            
    except Exception as e:
        print(f"❌ ERRO GERAL na função enviar_orcamento: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"mensagem": "Erro interno do servidor"}), 500
```

### 3. Verificar Configuração de Email

Se o problema persistir, pode ser um problema com a configuração de email. Você pode temporariamente desabilitar o envio de email alterando esta linha:

```python
envia_email = session.get('envia_email_orcamento', False)  # Mudar para False
```

### 4. Testar a Correção

Após fazer as alterações:

1. Salve o arquivo `app.py`
2. No PythonAnywhere, vá em "Web" → "Reload"
3. Teste novamente a funcionalidade

### 5. Verificar Logs

Se ainda houver erro, verifique os logs de erro no PythonAnywhere para ver a mensagem específica do erro.

## Resumo

O erro 500 provavelmente está sendo causado por:
1. **Problema de sintaxe** na função (bloco try sem except)
2. **Erro no envio de email** que está causando exceção não tratada

A correção acima deve resolver o problema adicionando tratamento adequado de erros e logging detalhado.
