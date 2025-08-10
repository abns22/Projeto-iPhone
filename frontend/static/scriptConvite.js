// Função para enviar orçamento via link de convite
function enviarOrcamentoPorEmail(dados) {
    console.log("Enviando dados para o servidor (Link de Convite):", dados);
    
    // Buscar token do convite da variável global
    const token = window.CONVITE_TOKEN;
    if (!token) {
        console.error("Token do convite não encontrado!");
        return;
    }

    fetch(`/convite/${token}/api/enviar-orcamento`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta do servidor:', data);
        alert(data.mensagem || "Orçamento enviado para nossa equipe!");
        
        // Se tiver link do WhatsApp, abre em nova aba
        if (data.link_whatsapp) {
            window.open(data.link_whatsapp, '_blank');
        }
    })
    .catch((error) => {
        console.error('Erro ao enviar orçamento:', error);
        alert("Ocorreu um erro ao tentar enviar o orçamento. Por favor, tente novamente.");
    });
}

// Função para buscar opções do modelo (cores e armazenamentos)
function fetchOpcoes(modeloId, cardClicado) {
    const token = window.CONVITE_TOKEN;
    const url = `/convite/${token}/api/modelo/${modeloId}/opcoes`;
    console.log(`DEBUG: Tentando acessar opções URL: ${url}`);
    console.log(`DEBUG: Token: ${token}`);
    console.log(`DEBUG: Modelo ID: ${modeloId}`);
    
    const opcoesCorDiv = cardClicado.querySelector('.opcoes-cor');
    const opcoesArmazenamentoDiv = cardClicado.querySelector('.opcoes-armazenamento');
    if (!opcoesCorDiv || !opcoesArmazenamentoDiv) return;

    opcoesCorDiv.innerHTML = '<p class="loading-text">Carregando...</p>';
    opcoesArmazenamentoDiv.innerHTML = '<p class="loading-text">Carregando...</p>';
    
    fetch(url)
        .then(response => {
            console.log(`DEBUG: Resposta do servidor (opções): ${response.status} ${response.statusText}`);
            if (!response.ok) throw new Error(`Erro de rede: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log(`DEBUG: Dados de opções recebidos:`, data);
            opcoesCorDiv.innerHTML = '';
            opcoesArmazenamentoDiv.innerHTML = '';
            if (data.modelo_info) {
                cardClicado.dataset.valorBase = data.modelo_info.valor_base_novo;
                cardClicado.dataset.nomeModelo = data.modelo_info.nome_modelo;
            }
            data.cores.forEach(cor => {
                const btn = document.createElement('button');
                btn.className = 'opcao-btn btn-cor';
                btn.textContent = cor.nome_cor;
                btn.dataset.corId = cor.id;
                btn.dataset.imagemUrl = cor.imagem_url;
                opcoesCorDiv.appendChild(btn);
            });
            data.armazenamentos.forEach(arm => {
                const btn = document.createElement('button');
                btn.className = 'opcao-btn btn-armazenamento';
                btn.textContent = `${arm.capacidade_gb} GB`;
                btn.dataset.armazenamentoId = arm.id;
                btn.dataset.modificadorValor = arm.modificador_valor || '0';
                console.log(`Criando botão de armazenamento: ${arm.capacidade_gb}GB, modificador: ${arm.modificador_valor}`);
                opcoesArmazenamentoDiv.appendChild(btn);
            });
        })
        .catch(error => console.error('Erro na função fetchOpcoes:', error));
}

// Função para buscar perguntas do modelo
function fetchEExibePerguntas(modeloId) {
    const token = window.CONVITE_TOKEN;
    const url = `/convite/${token}/api/modelo/${modeloId}/perguntas`;
    console.log(`DEBUG: Tentando acessar URL: ${url}`);
    console.log(`DEBUG: Token: ${token}`);
    console.log(`DEBUG: Modelo ID: ${modeloId}`);
    
    const listaPerguntasDiv = document.getElementById('lista-perguntas');
    if (!listaPerguntasDiv) return;

    listaPerguntasDiv.innerHTML = '<p>Carregando perguntas...</p>';
    fetch(url)
        .then(response => {
            console.log(`DEBUG: Resposta do servidor: ${response.status} ${response.statusText}`);
            if (!response.ok) {
                throw new Error(`Erro de rede: ${response.status}`);
            }
            return response.json();
        })
        .then(perguntas => {
            console.log(`DEBUG: Perguntas recebidas:`, perguntas);
            listaPerguntasDiv.innerHTML = '';
            perguntas.forEach(pergunta => {
                const divPergunta = document.createElement('div');
                divPergunta.className = 'item-pergunta';
                divPergunta.dataset.perguntaId = pergunta.pergunta_id;
                
                // Verificar se é pergunta condicional
                if (pergunta.pergunta_pai_id) {
                    divPergunta.dataset.perguntaPaiId = pergunta.pergunta_pai_id;
                    divPergunta.dataset.respostaPaiRequerida = pergunta.resposta_pai_requerida;
                    divPergunta.style.display = 'none'; // Inicialmente oculta
                    divPergunta.classList.add('pergunta-condicional');
                }

                const textoP = document.createElement('p');
                textoP.textContent = pergunta.texto_pergunta;
                divPergunta.appendChild(textoP);
                
                // Adicionar texto explicativo para pergunta de marcas leves
                if (pergunta.texto_pergunta.includes('marcas de uso leves')) {
                    const textoExplicativo = document.createElement('div');
                    textoExplicativo.className = 'texto-explicativo-leves';
                    textoExplicativo.innerHTML = `
                        <small class="text-muted">
                            <i class="fas fa-info-circle"></i>
                            Se responder "Não", uma pergunta sobre marcas severas aparecerá logo abaixo
                        </small>
                    `;
                    divPergunta.appendChild(textoExplicativo);
                }
                
                // Adicionar texto explicativo para perguntas condicionais
                if (pergunta.pergunta_pai_id) {
                    const textoExplicativo = document.createElement('div');
                    textoExplicativo.className = 'texto-explicativo';
                    textoExplicativo.innerHTML = `
                        <small class="text-muted">
                            <i class="fas fa-info-circle"></i>
                            Esta pergunta aparece apenas se a pergunta anterior for respondida com "${pergunta.resposta_pai_requerida}"
                        </small>
                    `;
                    divPergunta.appendChild(textoExplicativo);
                }

                const divOpcoes = document.createElement('div');
                divOpcoes.className = 'opcoes-resposta';
                pergunta.respostas.forEach(resposta => {
                    const btn = document.createElement('button');
                    btn.className = 'btn-resposta';
                    btn.textContent = resposta.texto;
                    btn.dataset.resposta = resposta.texto;
                    btn.dataset.impacto = resposta.impacto;
                    divOpcoes.appendChild(btn);
                });
                divPergunta.appendChild(divOpcoes);
                listaPerguntasDiv.appendChild(divPergunta);
            });
            
            // Configurar lógica de perguntas condicionais
            configurarPerguntasCondicionaisConvite();
        })
        .catch(error => {
            console.error("Erro ao buscar ou exibir perguntas:", error);
            listaPerguntasDiv.innerHTML = '<p>Erro ao carregar perguntas. Por favor, tente novamente.</p>';
        });
}

function configurarPerguntasCondicionaisConvite() {
    const todasPerguntas = document.querySelectorAll('.item-pergunta');
    
    todasPerguntas.forEach(pergunta => {
        const botoes = pergunta.querySelectorAll('.btn-resposta');
        
        botoes.forEach(botao => {
            botao.addEventListener('click', function() {
                const perguntaId = pergunta.dataset.perguntaId;
                const resposta = this.dataset.resposta;
                
                // Verificar se existem perguntas condicionais dependentes desta
                const perguntasDependentes = document.querySelectorAll(`[data-pergunta-pai-id="${perguntaId}"]`);
                
                perguntasDependentes.forEach(perguntaDependente => {
                    const respostaNecessaria = perguntaDependente.dataset.respostaPaiRequerida;
                    
                    if (resposta === respostaNecessaria) {
                        // Mostrar pergunta condicional
                        perguntaDependente.style.display = 'block';
                        perguntaDependente.classList.add('pergunta-ativa');
                    } else {
                        // Ocultar pergunta condicional e limpar resposta
                        perguntaDependente.style.display = 'none';
                        perguntaDependente.classList.remove('pergunta-ativa');
                        
                        // Limpar seleção da pergunta oculta
                        const botoesDependentes = perguntaDependente.querySelectorAll('.btn-resposta');
                        botoesDependentes.forEach(btn => btn.classList.remove('selecionado'));
                    }
                });
            });
        });
    });
}

// Função para transição para tela de avaliação
function transicaoParaTelaDeAvaliacao(cardClicado) {
    const gridModelos = document.querySelector('.grid-modelos');
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    if (!gridModelos || !secaoAvaliacao) return;
    
    const nomeModelo = cardClicado.dataset.nomeModelo;
    const valorBase = cardClicado.dataset.valorBase;
    const corBtn = cardClicado.querySelector('.btn-cor.selecionado');
    const armBtn = cardClicado.querySelector('.btn-armazenamento.selecionado');
    const imagemParaAtualizar = cardClicado.querySelector('img');
    const imagemUrl = imagemParaAtualizar ? imagemParaAtualizar.src : '';

    gridModelos.style.display = 'none';

    const divDestaque = document.getElementById('aparelho-em-destaque');
    if (divDestaque) {
        divDestaque.innerHTML = `
            <img src="${imagemUrl}" alt="${nomeModelo}">
            <h2>${nomeModelo}</h2>
            <div class="info-pills">
                <p>Cor: ${corBtn.textContent}</p>
                <p>Armazenamento: ${armBtn.textContent}</p>
            </div>`;
    }
    
    secaoAvaliacao.style.display = 'flex';
    secaoAvaliacao.dataset.valorBase = valorBase;
    secaoAvaliacao.dataset.corSelecionada = corBtn.textContent;
    secaoAvaliacao.dataset.armazenamentoSelecionado = armBtn.textContent;
    secaoAvaliacao.dataset.modificadorArmazenamento = armBtn.dataset.modificadorValor || '0';
    
    // Debug: verificar dados passados para a seção de avaliação
    console.log("Dados passados para seção de avaliação:");
    console.log("- Valor base:", valorBase);
    console.log("- Cor:", corBtn.textContent);
    console.log("- Armazenamento:", armBtn.textContent);
    console.log("- Modificador:", armBtn.dataset.modificadorValor);
    
    fetchEExibePerguntas(cardClicado.dataset.modeloId);
}

// Função para resetar estado da avaliação
function resetarEstadoAvaliacao() {
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    const divResultado = document.getElementById('resultado-final');
    
    if (secaoAvaliacao) {
        document.querySelectorAll('#lista-perguntas .item-pergunta').forEach(item => {
            item.querySelector('.btn-resposta.selecionado')?.classList.remove('selecionado');
            delete item.dataset.respostaSelecionada;
        });
        const imeiInput = document.getElementById('imei-input');
        if (imeiInput) imeiInput.value = '';
        if (divResultado) divResultado.innerHTML = '';
    }
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado. Iniciando script de convite.");
    console.log("DEBUG: CONVITE_TOKEN =", window.CONVITE_TOKEN);
    console.log("DEBUG: DADOS_CLIENTE =", window.DADOS_CLIENTE);
    
    const gridModelos = document.querySelector('.grid-modelos');
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    const btnVoltar = document.getElementById('btn-voltar-selecao');
    const btnCalcular = document.getElementById('btn-calcular-valor');
    const divResultado = document.getElementById('resultado-final');

    if (btnVoltar) {
        btnVoltar.addEventListener('click', () => {
            if (secaoAvaliacao) secaoAvaliacao.style.display = 'none';
            if (gridModelos) gridModelos.style.display = 'grid';
            resetarEstadoAvaliacao();
        });
    }

    if (gridModelos) {
        gridModelos.addEventListener('click', function(event) {
            const clicado = event.target;
            const cardClicado = clicado.closest('.card-modelo');
            if (!cardClicado) return;

            if (clicado.matches('.btn-cor')) {
                event.stopPropagation();
                cardClicado.querySelectorAll('.btn-cor').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
                const novaImagemUrl = clicado.dataset.imagemUrl;
                const imagemParaAtualizar = cardClicado.querySelector('img');
                if (novaImagemUrl && imagemParaAtualizar) {
                    imagemParaAtualizar.src = `/static/${novaImagemUrl}`;
                }
            } else if (clicado.matches('.btn-armazenamento')) {
                event.stopPropagation();
                cardClicado.querySelectorAll('.btn-armazenamento').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
            } else if (clicado.matches('.btn-selecionar-modelo')) {
                event.stopPropagation();
                const corSelecionada = cardClicado.querySelector('.btn-cor.selecionado');
                const armazenamentoSelecionado = cardClicado.querySelector('.btn-armazenamento.selecionado');
                if (!corSelecionada || !armazenamentoSelecionado) {
                    alert("Por favor, selecione uma cor e uma capacidade de armazenamento.");
                    return;
                }
                transicaoParaTelaDeAvaliacao(cardClicado);
            } else {
                const cardAtivoAnteriormente = document.querySelector('.card-modelo.ativo');
                if (cardAtivoAnteriormente && cardAtivoAnteriormente !== cardClicado) {
                    cardAtivoAnteriormente.classList.remove('ativo');
                    cardAtivoAnteriormente.querySelector('.conteudo-expandido').style.display = 'none';
                }
                cardClicado.classList.toggle('ativo');
                const conteudoExpandido = cardClicado.querySelector('.conteudo-expandido');
                const isAtivo = cardClicado.classList.contains('ativo');
                if (conteudoExpandido) {
                    conteudoExpandido.style.display = isAtivo ? 'block' : 'none';
                    const opcoesCorDiv = conteudoExpandido.querySelector('.opcoes-cor');
                    if (isAtivo && opcoesCorDiv && opcoesCorDiv.children.length === 0) {
                        fetchOpcoes(cardClicado.dataset.modeloId, cardClicado);
                    }
                }
            }
        });
    }

    if (secaoAvaliacao) {
        secaoAvaliacao.addEventListener('click', (event) => {
            if (event.target.matches('.btn-resposta')) {
                const botaoClicado = event.target;
                const divPerguntaPai = botaoClicado.closest('.item-pergunta');
                if (divPerguntaPai) {
                    divPerguntaPai.querySelectorAll('.btn-resposta').forEach(btn => btn.classList.remove('selecionado'));
                    botaoClicado.classList.add('selecionado');
                }
            }
        });

        if (btnCalcular) {
            btnCalcular.addEventListener('click', () => {
                const valorBase = parseFloat(secaoAvaliacao.dataset.valorBase);
                if (isNaN(valorBase)) {
                    alert("Erro: Não foi possível encontrar o valor base do aparelho.");
                    return;
                }
                
                // Aplicar modificador de armazenamento se disponível
                let valorComArmazenamento = valorBase;
                const modificadorArmazenamento = parseFloat(secaoAvaliacao.dataset.modificadorArmazenamento || '0');
                
                // Debug: verificar dados do armazenamento
                console.log("Valor base:", valorBase);
                console.log("Modificador de armazenamento:", modificadorArmazenamento);
                
                if (!isNaN(modificadorArmazenamento)) {
                    valorComArmazenamento += modificadorArmazenamento;
                    console.log(`Aplicando modificador de armazenamento: ${modificadorArmazenamento}, valor final: ${valorComArmazenamento}`);
                } else {
                    console.log("Modificador de armazenamento inválido");
                }
                
                let todasRespondidas = true;
                let valorFinal = valorComArmazenamento;
                const resumoDiagnostico = [];
                const todasAsPerguntasDivs = document.querySelectorAll('#lista-perguntas .item-pergunta');
                todasAsPerguntasDivs.forEach(divPergunta => {
                    const respostaSelecionadaEl = divPergunta.querySelector('.btn-resposta.selecionado');
                    if (!respostaSelecionadaEl) {
                        todasRespondidas = false;
                    } else {
                        const textoPergunta = divPergunta.querySelector('p').textContent;
                        const respostaTexto = respostaSelecionadaEl.dataset.resposta;
                        resumoDiagnostico.push({ pergunta: textoPergunta, resposta: respostaTexto });
                        const impacto = parseFloat(respostaSelecionadaEl.dataset.impacto);
                        if (!isNaN(impacto)) {
                            valorFinal += impacto;
                        }
                    }
                });

                if (!todasRespondidas) {
                    alert("Por favor, responda a todas as perguntas de avaliação.");
                    return;
                }

                const imei = document.getElementById('imei-input').value;
                if (!imei) {
                    alert("Por favor, digite o IMEI do aparelho.");
                    return;
                }
                resumoDiagnostico.push({ pergunta: "IMEI", resposta: imei });

                const nomeModelo = document.querySelector('#aparelho-em-destaque h2').textContent;
                const nomeCor = secaoAvaliacao.dataset.corSelecionada;
                const capacidadeArmazenamento = secaoAvaliacao.dataset.armazenamentoSelecionado;

                // Debug: verificar dados do cliente
                console.log("Dados do cliente:", window.DADOS_CLIENTE);
                
                const dadosDoOrcamento = {
                    nomeCliente: window.DADOS_CLIENTE.nome,
                    emailCliente: window.DADOS_CLIENTE.email,
                    telefoneCliente: window.DADOS_CLIENTE.telefone,
                    modelo: nomeModelo,
                    cor: nomeCor,
                    armazenamento: capacidadeArmazenamento,
                    imei: imei,
                    valor: valorFinal.toFixed(2),
                    resumo: resumoDiagnostico
                };
                
                // Debug: verificar dados do orçamento
                console.log("Dados do orçamento:", dadosDoOrcamento);

                if(divResultado) {
                    divResultado.innerHTML = `
                        <h3>Valor Estimado do Aparelho:</h3>
                        <h2 class="valor-calculado">R$ ${dadosDoOrcamento.valor.replace('.', ',')}</h2>
                        <button id="btn-imprimir-orcamento" class="btn-secundario">Imprimir Orçamento</button>
                    `;
                }
                
                enviarOrcamentoPorEmail(dadosDoOrcamento);

                const btnImprimir = document.getElementById('btn-imprimir-orcamento');
                if (btnImprimir) {
                    btnImprimir.addEventListener('click', () => {
                        if (typeof gerarPaginaDeImpressao === "function") {
                           gerarPaginaDeImpressao(dadosDoOrcamento);
                        }
                    });
                }
            });
        }
    }
});

// Função para gerar página de impressão para convites
function gerarPaginaDeImpressao(dados) {
    const dataAtual = new Date().toLocaleDateString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
    
    // Usar dados do cliente do objeto dados
    const nomeCliente = dados.nomeCliente || 'Não informado';
    const telefoneCliente = dados.telefoneCliente || 'Não informado';
    const emailCliente = dados.emailCliente || '';
    
    let diagnosticoItensHtml = '';
    dados.resumo.forEach(item => {
        if (item.pergunta.toLowerCase() !== 'imei') {
            diagnosticoItensHtml += `<p class="item"><strong>${item.pergunta}</strong> Resposta: ${item.resposta}</p>`;
        }
    });

    let conteudoHtmlCompleto = `
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <title>Orçamento de Avaliação - ${dados.modelo}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.4; color: #333; }
                .container { width: 90%; max-width: 800px; margin: auto; padding-top: 20px; }
                h1 { text-align: center; color: #2c3e50; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
                h2 { color: #34495e; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 20px; margin-bottom: 10px; }
                .item { margin: 4px 0; }
                .footer { margin-top: 30px; text-align: center; font-style: italic; color: #777; font-size: 0.8em; }
                .info-cliente, .info-aparelho, .diagnostico { border: 1px solid #ddd; padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; }
                strong { color: #000; }
                @media print {
                    body { font-size: 10pt; background-color: #fff; }
                    .container { width: 100%; margin: 0; padding: 0; border: none; }
                    h1 { font-size: 18pt; } h2 { font-size: 14pt; }
                    .info-cliente, .info-aparelho, .diagnostico { border: none; box-shadow: none; padding: 5px 0; margin-bottom: 10px; }
                    h2, .footer { page-break-after: avoid; }
                    p, .item { page-break-inside: avoid; }
                    a { text-decoration: none; color: #000; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Orçamento de Avaliação de Aparelho</h1>
                <div class="info-cliente">
                    <h2>Dados do Cliente</h2>
                    <p class="item"><strong>Cliente:</strong> ${nomeCliente}</p>
                    <p class="item"><strong>Telefone:</strong> ${telefoneCliente}</p>
                    <p class="item"><strong>E-mail:</strong> ${emailCliente || 'Não informado'}</p>
                    <p class="item"><strong>Data de Emissão:</strong> ${dataAtual}</p>
                </div>
                <div class="info-aparelho">
                    <h2>Detalhes do Aparelho</h2>
                    <p class="item"><strong>Modelo:</strong> ${dados.modelo}</p>
                    <p class="item"><strong>Cor:</strong> ${dados.cor}</p>
                    <p class="item"><strong>Armazenamento:</strong> ${dados.armazenamento}</p>
                    <p class="item"><strong>IMEI:</strong> ${dados.imei}</p>
                </div>
                <div class="diagnostico">
                    <h2>Diagnóstico Realizado</h2>
                    ${diagnosticoItensHtml}
                </div>
                <h2>Valor Estimado para Troca: R$ ${dados.valor}</h2>
                <div class="footer">
                    <p>Validade do orçamento por 7 dias.</p>
                </div>
            </div>
        </body>
        </html>`;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(conteudoHtmlCompleto);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
}
