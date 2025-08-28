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
    const secaoDadosCliente = document.getElementById('secao-dados-cliente');
    const secaoAvaliacao = document.getElementById('secao-avaliacao');
    const btnVoltar = document.getElementById('btn-voltar-selecao');
    const btnVoltarModelos = document.getElementById('btn-voltar-modelos');
    const btnAvancarDados = document.getElementById('btn-avancar-dados');
    const btnContinuarSemDados = document.getElementById('btn-continuar-sem-dados');
    const btnCalcular = document.getElementById('btn-calcular-valor');
    const divResultado = document.getElementById('resultado-final');
    
    // Variáveis para armazenar dados do cliente
    let dadosClientePreenchidos = {
        nome: '',
        telefone: '',
        email: '',
        modeloInteresse: '',
        preenchido: false
    };

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
                configurarPerguntasCondicionais();
            })
            .catch(error => console.error("Erro ao buscar ou exibir perguntas:", error));
    }
    
    function configurarPerguntasCondicionais() {
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

    function transicaoParaDadosCliente(cardClicado) {
        if (!gridModelos || !secaoDadosCliente) return;
        const nomeModelo = cardClicado.dataset.nomeModelo || '';
        const valorBase = cardClicado.dataset.valorBase || '';
        const corBtn = cardClicado.querySelector('.btn-cor.selecionado');
        const armBtn = cardClicado.querySelector('.btn-armazenamento.selecionado');
        const imagemParaAtualizar = cardClicado.querySelector('img');
        const imagemUrl = imagemParaAtualizar ? imagemParaAtualizar.src : '';

        gridModelos.style.display = 'none';

        // Atualizar destaque na seção de dados do cliente
        const divDestaqueDados = document.getElementById('aparelho-em-destaque-dados');
        if (divDestaqueDados) {
            divDestaqueDados.innerHTML = `
                <img src="${imagemUrl}" alt="${nomeModelo}">
                <h2>${nomeModelo}</h2>
                <div class="info-pills">
                    <p>Cor: ${corBtn ? corBtn.textContent : ''}</p>
                    <p>Armazenamento: ${armBtn ? armBtn.textContent : ''}</p>
                </div>`;
        }
        
        // Armazenar dados do modelo selecionado
        secaoDadosCliente.dataset.valorBase = valorBase;
        secaoDadosCliente.dataset.corSelecionada = corBtn ? corBtn.textContent : '';
        secaoDadosCliente.dataset.armazenamentoSelecionado = armBtn ? armBtn.textContent : '';
        secaoDadosCliente.dataset.modificadorArmazenamento = armBtn ? armBtn.dataset.modificadorValor || '0' : '0';
        secaoDadosCliente.dataset.nomeModelo = nomeModelo;
        secaoDadosCliente.dataset.modeloId = cardClicado.dataset.modeloId || '';
        secaoDadosCliente.dataset.imagemUrl = imagemUrl;
        
        secaoDadosCliente.style.display = 'flex';
        
        // Limpar campos do formulário
        document.getElementById('nome-cliente-input').value = '';
        document.getElementById('telefone-cliente-input').value = '';
        document.getElementById('email-cliente-input').value = '';
        document.getElementById('modelo-interesse-input').value = '';
    }

    function transicaoParaTelaDeAvaliacao(usarDadosArmazenados = false) {
        if (!secaoAvaliacao) return;
        
        let valorBase = '', corSelecionada = '', armazenamentoSelecionado = '', nomeModelo = '', modeloId = '', imagemUrl = '';
        
        if (usarDadosArmazenados && secaoDadosCliente) {
            // Usar dados armazenados da seção de dados do cliente
            valorBase = secaoDadosCliente.dataset.valorBase || '';
            corSelecionada = secaoDadosCliente.dataset.corSelecionada || '';
            armazenamentoSelecionado = secaoDadosCliente.dataset.armazenamentoSelecionado || '';
            nomeModelo = secaoDadosCliente.dataset.nomeModelo || '';
            modeloId = secaoDadosCliente.dataset.modeloId || '';
            imagemUrl = secaoDadosCliente.dataset.imagemUrl || '';
        }
        
        // Obter modificador de armazenamento
        const modificadorArmazenamento = secaoDadosCliente ? secaoDadosCliente.dataset.modificadorArmazenamento || '0' : '0';

        // Esconder seção de dados do cliente se estiver visível
        if (secaoDadosCliente) {
            secaoDadosCliente.style.display = 'none';
        }

        const divDestaque = document.getElementById('aparelho-em-destaque');
        if (divDestaque) {
            divDestaque.innerHTML = `
                <img src="${imagemUrl}" alt="${nomeModelo}">
                <h2>${nomeModelo}</h2>
                <div class="info-pills">
                    <p>Cor: ${corSelecionada}</p>
                    <p>Armazenamento: ${armazenamentoSelecionado}</p>
                </div>`;
        }
        
        secaoAvaliacao.style.display = 'flex';
        secaoAvaliacao.dataset.valorBase = valorBase;
        secaoAvaliacao.dataset.corSelecionada = corSelecionada;
        secaoAvaliacao.dataset.armazenamentoSelecionado = armazenamentoSelecionado;
        secaoAvaliacao.dataset.modificadorArmazenamento = modificadorArmazenamento;
        secaoAvaliacao.dataset.modeloId = modeloId || '';
        
        if (modeloId) {
            fetchEExibePerguntas(modeloId);
        }
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

    // Event listeners para os botões da seção de dados do cliente
    if (btnVoltarModelos) {
        btnVoltarModelos.addEventListener('click', function() {
            if (secaoDadosCliente) secaoDadosCliente.style.display = 'none';
            if (gridModelos) gridModelos.style.display = 'grid';
        });
    }

    if (btnAvancarDados) {
        btnAvancarDados.addEventListener('click', function() {
            // Validar campos obrigatórios
            const nomeInput = document.getElementById('nome-cliente-input');
            const telefoneInput = document.getElementById('telefone-cliente-input');
            const emailInput = document.getElementById('email-cliente-input');
            const modeloInteresseInput = document.getElementById('modelo-interesse-input');

            if (!nomeInput.value.trim()) {
                alert('Por favor, preencha o nome completo.');
                nomeInput.focus();
                return;
            }

            if (!telefoneInput.value.trim()) {
                alert('Por favor, preencha o telefone.');
                telefoneInput.focus();
                return;
            }

            if (!modeloInteresseInput.value.trim()) {
                alert('Por favor, preencha o modelo de interesse.');
                modeloInteresseInput.focus();
                return;
            }

            // Armazenar dados do cliente
            dadosClientePreenchidos = {
                nome: nomeInput.value.trim(),
                telefone: telefoneInput.value.trim(),
                email: emailInput.value.trim(),
                modeloInteresse: modeloInteresseInput.value.trim(),
                preenchido: true
            };

            // Avançar para tela de avaliação
            transicaoParaTelaDeAvaliacao(true);
        });
    }

    if (btnContinuarSemDados) {
        btnContinuarSemDados.addEventListener('click', function() {
            // Resetar dados do cliente
            dadosClientePreenchidos = {
                nome: '',
                telefone: '',
                email: '',
                modeloInteresse: '',
                preenchido: false
            };

            // Avançar para tela de avaliação
            transicaoParaTelaDeAvaliacao(true);
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
                transicaoParaDadosCliente(cardClicado);
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
                const modificadorArmazenamento = secaoAvaliacao.dataset.modificadorArmazenamento;
                
                if (modificadorArmazenamento) {
                    const modificador = parseFloat(modificadorArmazenamento);
                    if (!isNaN(modificador)) {
                        valorComArmazenamento += modificador;
                        console.log(`Aplicando modificador de armazenamento: ${modificador}, valor final: ${valorComArmazenamento}`);
                    }
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
                
                // Usar dados do cliente preenchidos ou dados do usuário logado como fallback
                const bodyElement = document.querySelector('body');
                let nomeCliente, telefoneCliente, emailCliente, modeloInteresse;
                
                if (dadosClientePreenchidos.preenchido) {
                    nomeCliente = dadosClientePreenchidos.nome;
                    telefoneCliente = dadosClientePreenchidos.telefone;
                    emailCliente = dadosClientePreenchidos.email;
                    modeloInteresse = dadosClientePreenchidos.modeloInteresse;
                } else {
                    nomeCliente = bodyElement.dataset.nomeUsuario || 'Não informado';
                    telefoneCliente = bodyElement.dataset.telefoneUsuario || 'Não informado';
                    emailCliente = '';
                    modeloInteresse = '';
                }

                const dadosDoOrcamento = {
                    nomeCliente, 
                    telefoneCliente, 
                    emailCliente,
                    modeloInteresse,
                    dadosClientePreenchidos: dadosClientePreenchidos.preenchido,
                    modelo: nomeModelo, 
                    modeloId: modeloId,
                    cor: nomeCor,
                    armazenamento: capacidadeArmazenamento, 
                    imei, 
                    valor: valorFinal.toFixed(2), 
                    resumo: resumoDiagnostico
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
    
    // Usar dados do cliente do objeto dados, com fallback para dados do usuário
    const nomeCliente = dados.nomeCliente || 'Não informado';
    const telefoneCliente = dados.telefoneCliente || 'Não informado';
    const emailCliente = dados.emailCliente || '';
    const modeloInteresse = dados.modeloInteresse || '';
    
    let diagnosticoItensHtml = '';
    dados.resumo.forEach(item => {
        if (item.pergunta.toLowerCase() !== 'imei') {
            diagnosticoItensHtml += `<p class="item"><strong>${item.pergunta}</strong> Resposta: ${item.resposta}</p>`;
        }
    });

    // Montar seção de dados do cliente baseado se foram preenchidos ou não
    let secaoClienteHtml = '';
    if (dados.dadosClientePreenchidos) {
        secaoClienteHtml = `
            <p class="item"><strong>Cliente:</strong> ${nomeCliente}</p>
            <p class="item"><strong>Telefone:</strong> ${telefoneCliente}</p>
            <p class="item"><strong>E-mail:</strong> ${emailCliente || 'Não informado'}</p>
            <p class="item"><strong>Modelo de Interesse:</strong> ${modeloInteresse || 'Não informado'}</p>
        `;
    } else {
        secaoClienteHtml = `
            <p class="item"><strong>Dados do cliente não foram informados</strong></p>
            <p class="item"><strong>Usuário do sistema:</strong> ${nomeCliente}</p>
            <p class="item"><strong>Telefone do usuário:</strong> ${telefoneCliente}</p>
        `;
    }

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
                    ${secaoClienteHtml}
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