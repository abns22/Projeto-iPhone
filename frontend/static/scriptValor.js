// ===================================================================
// VERSÃO COMPLETA E CORRIGIDA - Substitua todo o seu script por este.
// ===================================================================

// O 'ouvinte' principal que garante que todo o HTML foi carregado antes de o JavaScript rodar.
// TODO o nosso código ficará aqui dentro.
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado. Iniciando script definitivo.");

    // ===================================================================
    // 1. SELEÇÃO DE TODOS OS ELEMENTOS DA PÁGINA
    // ===================================================================
    const dashboardLayout = document.querySelector('.dashboard-layout');
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const gridModelos = document.querySelector('.grid-modelos');
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    const btnVoltar = document.getElementById('btn-voltar-selecao');
    const btnCalcular = document.getElementById('btn-calcular-valor');
    const divResultado = document.getElementById('resultado-final');

    // ===================================================================
    // 2. DEFINIÇÃO DE TODAS AS FUNÇÕES AUXILIARES
    // ===================================================================

    function fetchOpcoes(modeloId, cardClicado) {
        const url = `/api/modelo/${modeloId}/opcoes`;
        const opcoesCorDiv = cardClicado.querySelector('.opcoes-cor');
        const opcoesArmazenamentoDiv = cardClicado.querySelector('.opcoes-armazenamento');
        if (!opcoesCorDiv || !opcoesArmazenamentoDiv) return;

        opcoesCorDiv.innerHTML = '<p class="loading-text">Carregando...</p>';
        opcoesArmazenamentoDiv.innerHTML = '<p class="loading-text">Carregando...</p>';
        
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`Erro de rede: ${response.status}`);
                return response.json();
            })
            .then(data => {
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
                opcoesArmazenamentoDiv.appendChild(btn);
            });
            })
            .catch(error => console.error('Erro na função fetchOpcoes:', error));
    }

    function fetchEExibePerguntas(modeloId) {
        const url = `/api/modelo/${modeloId}/perguntas`;
        const listaPerguntasDiv = document.getElementById('lista-perguntas');
        if (!listaPerguntasDiv) return;

        listaPerguntasDiv.innerHTML = '<p>Carregando perguntas...</p>';
        fetch(url)
            .then(response => response.json())
            .then(perguntas => {
                listaPerguntasDiv.innerHTML = '';
                perguntas.forEach(pergunta => {
                    const divPergunta = document.createElement('div');
                    divPergunta.className = 'item-pergunta';
                    divPergunta.dataset.perguntaId = pergunta.pergunta_id;

                    const textoP = document.createElement('p');
                    textoP.textContent = pergunta.texto_pergunta;
                    divPergunta.appendChild(textoP);

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
            })
            .catch(error => console.error("Erro ao buscar ou exibir perguntas:", error));
    }

    function transicaoParaTelaDeAvaliacao(cardClicado) {
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
        fetchEExibePerguntas(cardClicado.dataset.modeloId);
    }

    function resetarEstadoAvaliacao() {
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

    // ===================================================================
    // 3. CONFIGURAÇÃO DOS EVENT LISTENERS (OS "OUVINTES" DE AÇÕES)
    // ===================================================================

    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', () => {
            dashboardLayout?.classList.toggle('sidebar-ativa');
        });
    }

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
                const armazenamentoSelecionado = secaoAvaliacao.dataset.armazenamentoSelecionado;
                const cardModelo = document.querySelector('.card-modelo[data-modelo-id]');
                
                if (cardModelo && armazenamentoSelecionado) {
                    // Buscar o modificador do armazenamento selecionado
                    const armazenamentoBtn = cardModelo.querySelector('.btn-armazenamento.selecionado');
                    if (armazenamentoBtn && armazenamentoBtn.dataset.modificadorValor) {
                        const modificador = parseFloat(armazenamentoBtn.dataset.modificadorValor);
                        if (!isNaN(modificador)) {
                            valorComArmazenamento += modificador;
                            console.log(`Aplicando modificador de armazenamento: ${modificador}, valor final: ${valorComArmazenamento}`);
                        }
                    }
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
                const bodyElement = document.querySelector('body');
                const nomeCliente = bodyElement.dataset.nomeUsuario || 'Não informado';
                const telefoneCliente = bodyElement.dataset.telefoneUsuario || 'Não informado';

                const dadosDoOrcamento = {
                    nomeCliente, telefoneCliente, modelo: nomeModelo, cor: nomeCor,
                    armazenamento: capacidadeArmazenamento, imei, valor: valorFinal.toFixed(2), resumo: resumoDiagnostico
                };

                if(divResultado) {
                    divResultado.innerHTML = `
                        <h3>Valor Estimado do Aparelho:</h3>
                        <h2 class="valor-calculado">R$ ${dadosDoOrcamento.valor.replace('.', ',')}</h2>
                        <button id="btn-imprimir-orcamento" class="btn-secundario">Imprimir Orçamento</button>
                    `;
                }
                
                if (typeof enviarOrcamentoPorEmail === "function") {
                   enviarOrcamentoPorEmail(dadosDoOrcamento);
                }

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

function enviarOrcamentoPorEmail(dados) {
    console.log("Enviando dados para o servidor:", dados);
    fetch('/api/enviar-orcamento', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta do servidor:', data);
        alert(data.mensagem || "Orçamento enviado para nossa equipe!");
    })
    .catch((error) => {
        console.error('Erro ao enviar e-mail:', error);
        alert("Ocorreu um erro ao tentar notificar nossa equipe. Por favor, guarde seu orçamento.");
    });
}

function gerarPaginaDeImpressao(dados) {
    const dataAtual = new Date().toLocaleDateString('pt-BR', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
    
    const bodyElement = document.querySelector('body');
    const nomeCliente = bodyElement.dataset.nomeUsuario || 'Não informado';
    const telefoneCliente = bodyElement.dataset.telefoneUsuario || 'Não informado';
    
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
                    <p class="item"><strong>Data de Emissão:</strong> ${dataAtual}</p>
                </div>
                <div class="info-aparelho">
                    <h2>Detalhes do Aparelho</h2>
                    <p class="item"><strong>Modelo:</strong> ${dados.modelo}</p>
                    <p class="item"><strong>Detalhes:</strong> ${dados.detalhes}</p>
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