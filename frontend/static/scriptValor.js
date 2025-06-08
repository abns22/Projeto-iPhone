document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM carregado. Script iniciado.");

    // --- LÓGICA DO MENU HAMBÚRGUER (Sidebar) ---
    const dashboardLayout = document.querySelector('.dashboard-layout');
    const hamburgerBtn = document.getElementById('hamburgerBtn');

    if (hamburgerBtn && dashboardLayout) {
        hamburgerBtn.addEventListener('click', function() {
            // Este código controla apenas a classe do layout principal para mostrar/esconder o menu
            dashboardLayout.classList.toggle('sidebar-ativa');
        });
    }

    // --- LÓGICA DOS CARDS DE IPHONE (Expansão e Seleção) ---
    const gridModelos = document.querySelector('.grid-modelos');

    // Usaremos um único event listener no grid para gerenciar todos os cliques internos
    if (gridModelos) {
        gridModelos.addEventListener('click', function(event) {
            const clicado = event.target;
            const cardClicado = clicado.closest('.card-modelo');

            if (!cardClicado) return; // Se o clique foi fora de um card, não faz nada

            // 1. Lógica de EXPANDIR/RECOLHER o card
            // Só executa se o clique foi na área principal do card (e não em botões internos)
            if (!clicado.closest('.conteudo-expandido')) {
                const isAlreadyActive = cardClicado.classList.contains('card-expandido');
                
                // Fecha todos os outros cards
                document.querySelectorAll('.card-modelo').forEach(card => {
                    card.classList.remove('card-expandido');
                    card.querySelector('.conteudo-expandido').style.display = 'none';
                });

                // Se o card clicado não estava ativo, abre ele
                if (!isAlreadyActive) {
                    cardClicado.classList.add('card-expandido');
                    const conteudoExpandido = cardClicado.querySelector('.conteudo-expandido');
                    conteudoExpandido.style.display = 'block';

                    const modeloId = cardClicado.dataset.modeloId;
                    fetchOpcoes(modeloId, cardClicado); // Passa o card como argumento
                }
            }

            // 2. Lógica de SELECIONAR UMA COR (e mudar a imagem)
            if (clicado.matches('.btn-cor')) {
                cardClicado.querySelectorAll('.btn-cor').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
                
                const novaImagemUrl = clicado.dataset.imagemUrl;
                const imagemDoCard = cardClicado.querySelector('img');

                if (novaImagemUrl && imagemDoCard) {
                    imagemDoCard.src = `/static/${novaImagemUrl}`;
                }
            }

            // 3. Lógica de SELECIONAR UM ARMAZENAMENTO
            if (clicado.matches('.btn-armazenamento')) {
                cardClicado.querySelectorAll('.btn-armazenamento').forEach(btn => btn.classList.remove('selecionado'));
                clicado.classList.add('selecionado');
            }

            // 4. Lógica para o botão "AVANÇAR"
            if (clicado.matches('.btn-selecionar-modelo')) {
                event.stopPropagation(); // Impede que o clique no botão feche o card

                const modeloId = cardClicado.dataset.modeloId;
                const corSelecionada = cardClicado.querySelector('.btn-cor.selecionado');
                const armazenamentoSelecionado = cardClicado.querySelector('.btn-armazenamento.selecionado');

                if (!corSelecionada || !armazenamentoSelecionado) {
                    alert("Por favor, selecione uma cor e uma capacidade de armazenamento.");
                    return;
                }
                
                gridModelos.style.display = 'none';
                document.getElementById('secao-questionario').style.display = 'block';
                
                fetchEExibePerguntas(modeloId);
            }
        });
    }

    // --- Função para buscar e popular as OPÇÕES (Cores e Armazenamentos) ---
    function fetchOpcoes(modeloId, cardClicado) {
        const url = `/api/modelo/${modeloId}/opcoes`;
        const opcoesCorDiv = cardClicado.querySelector('.opcoes-cor');
        const opcoesArmazenamentoDiv = cardClicado.querySelector('.opcoes-armazenamento');

        if (!opcoesCorDiv || !opcoesArmazenamentoDiv) return;

        opcoesCorDiv.innerHTML = '<p>Carregando...</p>';
        opcoesArmazenamentoDiv.innerHTML = '<p>Carregando...</p>';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                opcoesCorDiv.innerHTML = '';
                opcoesArmazenamentoDiv.innerHTML = '';

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
                opcoesCorDiv.innerHTML = '<p>Erro ao carregar.</p>';
                opcoesArmazenamentoDiv.innerHTML = '<p>Erro ao carregar.</p>';
            });
    }

    // --- Função para buscar e popular as PERGUNTAS do questionário ---
    function fetchEExibePerguntas(modeloId) {
        const url = `/api/modelo/${modeloId}/perguntas`;
        const listaPerguntasDiv = document.getElementById('lista-perguntas');
        
        listaPerguntasDiv.innerHTML = '<p>Carregando perguntas...</p>';

        fetch(url)
            .then(response => response.json())
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
                        </div>
                    `;
                    listaPerguntasDiv.appendChild(divPergunta);
                });
            })
            .catch(error => {
                console.error("Erro ao buscar perguntas:", error);
                listaPerguntasDiv.innerHTML = '<p>Erro ao carregar as perguntas.</p>';
            });
    }
});