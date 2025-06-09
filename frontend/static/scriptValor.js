document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado. Script completo iniciado.");

    const dashboardLayout = document.querySelector('.dashboard-layout');
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const gridModelos = document.querySelector('.grid-modelos');
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    const btnVoltar = document.getElementById('btn-voltar-selecao');
    const btnCalcular = document.getElementById('btn-calcular-valor');

    if (hamburgerBtn && dashboardLayout) {
        hamburgerBtn.addEventListener('click', function() {
            dashboardLayout.classList.toggle('sidebar-ativa');
        });
    }

    if (btnVoltar && gridModelos && secaoAvaliacao) {
        btnVoltar.addEventListener('click', function() {
            secaoAvaliacao.style.display = 'none';
            gridModelos.style.display = 'grid';
        });
    }

    if (gridModelos) {
        gridModelos.addEventListener('click', function(event) {
            const clicado = event.target;
            const cardClicado = clicado.closest('.card-modelo');
            if (!cardClicado) return;

            if (!clicado.closest('.conteudo-expandido')) {
                const isAlreadyActive = cardClicado.classList.contains('card-expandido');
                document.querySelectorAll('.card-modelo').forEach(card => {
                    card.classList.remove('card-expandido');
                    if (card.querySelector('.conteudo-expandido')) {
                        card.querySelector('.conteudo-expandido').style.display = 'none';
                    }
                });
                if (!isAlreadyActive) {
                    cardClicado.classList.add('card-expandido');
                    if (cardClicado.querySelector('.conteudo-expandido')) {
                        cardClicado.querySelector('.conteudo-expandido').style.display = 'block';
                    }
                    fetchOpcoes(cardClicado.dataset.modeloId, cardClicado);
                }
            }

            if (clicado.matches('.btn-cor')) {
                cardClicado.querySelectorAll('.btn-cor').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
                const novaImagemUrl = clicado.dataset.imagemUrl;
                const imagemDoCard = cardClicado.querySelector('img');
                if (novaImagemUrl && imagemDoCard) {
                    imagemDoCard.src = `/static/${novaImagemUrl}`;
                }
            }

            if (clicado.matches('.btn-armazenamento')) {
                cardClicado.querySelectorAll('.btn-armazenamento').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
            }

            
            if (clicado.matches('.btn-selecionar-modelo')) {
                event.stopPropagation();
                const corSelecionada = cardClicado.querySelector('.btn-cor.selecionado');
                const armazenamentoSelecionado = cardClicado.querySelector('.btn-armazenamento.selecionado');
                if (!corSelecionada || !armazenamentoSelecionado) {
                    alert("Por favor, selecione uma cor e uma capacidade de armazenamento.");
                    return;
                }
                transicaoParaTelaDeAvaliacao(cardClicado);
            }
        });
    }

    if (secaoAvaliacao) {
        secaoAvaliacao.addEventListener('click', function(event) {
            if (event.target.matches('.btn-resposta')) {
                const botaoClicado = event.target;
                const divPerguntaPai = botaoClicado.closest('.item-pergunta');
                divPerguntaPai.querySelectorAll('.btn-resposta').forEach(btn => btn.classList.remove('selecionado'));
                botaoClicado.classList.add('selecionado');
                divPerguntaPai.dataset.respostaSelecionada = botaoClicado.dataset.resposta;
            }
        });
    }
    
    if (btnCalcular) {
        btnCalcular.addEventListener('click', function() {
            const valorBase = parseFloat(secaoAvaliacao.dataset.valorBase);
            if (isNaN(valorBase)) {
                alert("Erro: Não foi possível encontrar o valor base do aparelho.");
                return;
            }

            let valorFinal = valorBase;
            const resumoDiagnostico = [];
            const todasAsPerguntas = document.querySelectorAll('#lista-perguntas .item-pergunta');
            let todasRespondidas = true;

            todasAsPerguntas.forEach(itemPergunta => {
                const respostaSelecionadaEl = itemPergunta.querySelector('.btn-resposta.selecionado');
                if (!respostaSelecionadaEl) {
                    todasRespondidas = false;
                } else {
                    const textoPergunta = itemPergunta.querySelector('p').textContent;
                    const resposta = respostaSelecionadaEl.dataset.resposta;
                    resumoDiagnostico.push({ pergunta: textoPergunta, resposta: resposta });
                    if (resposta === itemPergunta.dataset.respostaImpacto) {
                        valorFinal += parseFloat(itemPergunta.dataset.valorImpacto);
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

            const divResultado = document.getElementById('resultado-final');
            divResultado.innerHTML = `
                <h3>Valor Estimado do Aparelho:</h3>
                <h2 class="valor-calculado">R$ ${valorFinal.toFixed(2).replace('.', ',')}</h2>
                <button id="btn-imprimir-orcamento" class="btn-secundario">Imprimir Orçamento</button>
            `;
            
            const dadosDoOrcamento = {
                modelo: document.querySelector('#aparelho-em-destaque h2').textContent,
                detalhes: document.querySelector('#aparelho-em-destaque .info-pills').innerText.replace(/\n/g, ', '),
                imei: imei,
                valor: valorFinal.toFixed(2),
                resumo: resumoDiagnostico
            };

            enviarOrcamentoPorEmail(dadosDoOrcamento);

            document.getElementById('btn-imprimir-orcamento').addEventListener('click', function() {
                gerarPaginaDeImpressao(dadosDoOrcamento);
            });
        });
    }
});

function fetchOpcoes(modeloId, cardClicado) {
    const url = `/api/modelo/${modeloId}/opcoes`;
    const opcoesCorDiv = cardClicado.querySelector('.opcoes-cor');
    const opcoesArmazenamentoDiv = cardClicado.querySelector('.opcoes-armazenamento');

    if (!opcoesCorDiv || !opcoesArmazenamentoDiv) {
        console.error("Elementos para opções de cor ou armazenamento não encontrados no card.");
        return;
    }

    opcoesCorDiv.innerHTML = '<p>Carregando...</p>';
    opcoesArmazenamentoDiv.innerHTML = '<p>Carregando...</p>';
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Erro na rede: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            opcoesCorDiv.innerHTML = '';
            opcoesArmazenamentoDiv.innerHTML = '';

            if (data.modelo_info) {
                cardClicado.dataset.valorBase = data.modelo_info.valor_base;
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
                opcoesArmazenamentoDiv.appendChild(btn);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar opções:', error);
            opcoesCorDiv.innerHTML = '<p>Erro ao carregar opções.</p>';
            opcoesArmazenamentoDiv.innerHTML = '<p>Erro ao carregar opções.</p>';
        });
}

function fetchEExibePerguntas(modeloId) {
    const url = `/api/modelo/${modeloId}/perguntas`;
    const listaPerguntasDiv = document.getElementById('lista-perguntas');
    
    listaPerguntasDiv.innerHTML = '<p>Carregando perguntas...</p>';

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Erro na rede: ${response.statusText}`);
            return response.json();
        })
        .then(perguntas => {
            listaPerguntasDiv.innerHTML = '';
            perguntas.forEach(pergunta => {
                const divPergunta = document.createElement('div');
                divPergunta.className = 'item-pergunta';
                divPergunta.dataset.perguntaId = pergunta.pergunta_id;
                divPergunta.dataset.respostaImpacto = pergunta.resposta_que_gera_impacto;
                divPergunta.dataset.valorImpacto = pergunta.valor_do_impacto;
                divPergunta.innerHTML = `
                    <p>${pergunta.texto_pergunta}</p>
                    <div class="opcoes-resposta">
                        <button class="btn-resposta" data-resposta="Sim">Sim</button>
                        <button class="btn-resposta" data-resposta="Não">Não</button>
                    </div>`;
                listaPerguntasDiv.appendChild(divPergunta);
            });
        })
        .catch(error => {
            console.error("Erro ao buscar perguntas:", error);
            listaPerguntasDiv.innerHTML = '<p>Erro ao carregar as perguntas. Tente novamente.</p>';
        });
}

function transicaoParaTelaDeAvaliacao(cardClicado) {
    const nomeModelo = cardClicado.dataset.nomeModelo;
    const valorBase = cardClicado.dataset.valorBase;
    const corBtn = cardClicado.querySelector('.btn-cor.selecionado');
    const armBtn = cardClicado.querySelector('.btn-armazenamento.selecionado');
    const imagemUrl = corBtn.dataset.imagemUrl;
    
    document.querySelector('.grid-modelos').style.display = 'none';

    const divDestaque = document.getElementById('aparelho-em-destaque');
    divDestaque.innerHTML = `
        <img src="/static/${imagemUrl}" alt="${nomeModelo}">
        <h2>${nomeModelo}</h2>
        <div class="info-pills">
            <p>Cor: ${corBtn.textContent}</p>
            <p>Armazenamento: ${armBtn.textContent}</p>
        </div>
    `;

    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    secaoAvaliacao.style.display = 'flex';
    secaoAvaliacao.dataset.valorBase = valorBase;

    fetchEExibePerguntas(cardClicado.dataset.modeloId);
}

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