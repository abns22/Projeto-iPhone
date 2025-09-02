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
                cardClicado.dataset.valorBase = data.modelo_info.valor_base_novo || '';
                cardClicado.dataset.nomeModelo = data.modelo_info.nome_modelo || '';
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
                            perguntaDependente.classList.add('pergunta-condicional-oculta');
                            
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
    
    const nomeModelo = cardClicado.dataset.nomeModelo || '';
    const valorBase = cardClicado.dataset.valorBase || '';
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
                <p>Cor: ${corBtn ? corBtn.textContent : ''}</p>
                <p>Armazenamento: ${armBtn ? armBtn.textContent : ''}</p>
            </div>`;
    }
    
    secaoAvaliacao.style.display = 'flex';
    secaoAvaliacao.dataset.valorBase = valorBase;
    secaoAvaliacao.dataset.corSelecionada = corBtn ? corBtn.textContent : '';
    secaoAvaliacao.dataset.armazenamentoSelecionado = armBtn ? armBtn.textContent : '';
    secaoAvaliacao.dataset.modificadorArmazenamento = armBtn ? (armBtn.dataset.modificadorValor || '0') : '0';
    secaoAvaliacao.dataset.modeloId = cardClicado.dataset.modeloId || '';
    
    // Debug: verificar dados passados para a seção de avaliação
    console.log("Dados passados para seção de avaliação:");
    console.log("- Valor base:", valorBase);
    console.log("- Cor:", corBtn ? corBtn.textContent : '');
    console.log("- Armazenamento:", armBtn ? armBtn.textContent : '');
    console.log("- Modificador:", armBtn ? armBtn.dataset.modificadorValor : '');
    
    fetchEExibePerguntas(cardClicado.dataset.modeloId || '');
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
                    // Verificar se a pergunta está visível (não oculta por lógica condicional)
                    const isVisible = divPergunta.style.display !== 'none' && !divPergunta.classList.contains('pergunta-condicional-oculta');
                    
                    if (isVisible) {
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
                const modeloId = secaoAvaliacao.dataset.modeloId || '';

                // Debug: verificar dados do cliente
                console.log("Dados do cliente:", window.DADOS_CLIENTE);
                
                const dadosDoOrcamento = {
                    nomeCliente: window.DADOS_CLIENTE.nome,
                    emailCliente: window.DADOS_CLIENTE.email,
                    telefoneCliente: window.DADOS_CLIENTE.telefone,
                    modelo: nomeModelo,
                    modeloId: modeloId,
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

    // Obter dados da empresa do template
    const dadosEmpresa = window.dadosEmpresa || {};
    
    // Formatar endereço da empresa
    let enderecoEmpresa = '';
    if (dadosEmpresa.endereco && dadosEmpresa.endereco.rua && dadosEmpresa.endereco.numero) {
        enderecoEmpresa = `${dadosEmpresa.endereco.rua}, ${dadosEmpresa.endereco.numero}`;
        if (dadosEmpresa.endereco.bairro) {
            enderecoEmpresa += `, ${dadosEmpresa.endereco.bairro}`;
        }
        if (dadosEmpresa.endereco.cidade && dadosEmpresa.endereco.estado) {
            enderecoEmpresa += ` - ${dadosEmpresa.endereco.cidade} - ${dadosEmpresa.endereco.estado}`;
        }
    } else {
        enderecoEmpresa = 'Endereço não informado';
    }
    
    // Seção de informações da empresa
    const secaoEmpresaHtml = `
        <div class="info-empresa">
            <h2>Informações da Empresa</h2>
            <p class="item"><strong>Empresa:</strong> ${dadosEmpresa.nome || 'Sistema'}</p>
            <p class="item"><strong>CNPJ:</strong> ${dadosEmpresa.cnpj || 'Não informado'}</p>
            <p class="item"><strong>Endereço:</strong> ${enderecoEmpresa}</p>
        </div>
    `;
    
    let conteudoHtmlCompleto = `
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <title>Orçamento de Avaliação - ${dados.modelo}</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: Arial, sans-serif; font-size: 10px; line-height: 1.2; color: #333; }
                .container { max-width: 100%; padding: 10px; }
                h1 { font-size: 16px; text-align: center; margin-bottom: 15px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
                h2 { font-size: 12px; margin: 8px 0 5px 0; color: #34495e; }
                .info-empresa, .info-cliente, .info-aparelho, .diagnostico { border: 1px solid #ddd; padding: 8px 10px; border-radius: 3px; margin-bottom: 10px; }
                .logo-empresa { text-align: center; margin: 10px 0; }
                .logo-empresa img { max-width: 150px; max-height: 80px; object-fit: contain; }
                .item { margin: 3px 0; font-size: 9px; }
                .item strong { color: #2c3e50; }
                .valor-total { font-size: 14px; font-weight: bold; text-align: center; margin: 10px 0; padding: 8px; background-color: #ecf0f1; border-radius: 3px; color: #2c3e50; }
                .observacoes { margin-top: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 3px; border-left: 3px solid #3498db; }
                .observacoes h3 { font-size: 11px; margin-bottom: 5px; color: #2c3e50; }
                .observacoes p { font-size: 9px; margin: 2px 0; }
                .data-geracao { text-align: center; margin-top: 10px; font-size: 8px; color: #7f8c8d; font-style: italic; }
                
                @media print {
                    body { font-size: 9px; }
                    .container { padding: 5px; }
                    h1 { font-size: 14px; margin-bottom: 10px; }
                    h2 { font-size: 11px; margin: 5px 0 3px 0; }
                    .info-empresa, .info-cliente, .info-aparelho, .diagnostico { border: none; box-shadow: none; padding: 3px 0; margin-bottom: 8px; }
                    .logo-empresa { margin: 5px 0; }
                    .logo-empresa img { max-width: 120px; max-height: 60px; }
                    .item { margin: 2px 0; font-size: 8px; }
                    .valor-total { font-size: 12px; margin: 8px 0; padding: 5px; }
                    .observacoes { margin-top: 8px; padding: 5px; }
                    .observacoes h3 { font-size: 10px; margin-bottom: 3px; }
                    .observacoes p { font-size: 8px; margin: 1px 0; }
                    .data-geracao { margin-top: 8px; font-size: 7px; }
                    @page { margin: 1cm; size: A4; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Orçamento de Avaliação de Aparelho</h1>
                ${dadosEmpresa.logo ? `<div class="logo-empresa"><img src="${dadosEmpresa.logo}" alt="Logo ${dadosEmpresa.nome}" /></div>` : ''}
                ${secaoEmpresaHtml}
                <div class="info-cliente">
                    <h2>Dados do Cliente</h2>
                    <p class="item"><strong>Nome:</strong> ${nomeCliente}</p>
                    <p class="item"><strong>Email:</strong> ${emailCliente}</p>
                    <p class="item"><strong>Telefone:</strong> ${telefoneCliente}</p>
                </div>
                <div class="info-aparelho">
                    <h2>Informações do Aparelho</h2>
                    <p class="item"><strong>Modelo:</strong> ${dados.modelo}</p>
                    <p class="item"><strong>IMEI:</strong> ${dados.imei}</p>
                    <p class="item"><strong>Cor:</strong> ${dados.cor}</p>
                    <p class="item"><strong>Capacidade:</strong> ${dados.armazenamento}</p>
                </div>
                <div class="diagnostico">
                    <h2>Diagnóstico e Avaliação</h2>
                    ${diagnosticoItensHtml}
                </div>
                <div class="valor-total">
                    <strong>Valor da Avaliação: R$ ${dados.valor}</strong>
                </div>
                <div class="observacoes">
                    <h3>Observações Importantes:</h3>
                    <p>• Este orçamento é válido por 30 dias a partir da data de emissão.</p>
                    <p>• O valor pode variar conforme a disponibilidade de peças e complexidade do reparo.</p>
                    <p>• Após a aprovação, o prazo para conclusão será informado.</p>
                    <p>• Garantia de 90 dias para peças e serviços.</p>
                </div>
                <div class="data-geracao">
                    Orçamento gerado em: ${dataAtual}
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
