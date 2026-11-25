// ========================================
// DADOS (carregados da API / PostgreSQL)
// ========================================

let demandas = [];

// Quando aberto pela API (http://localhost:5000) usa caminho relativo.
// Se o index.html for aberto direto do disco, aponta para a API local.
const API_URL = window.location.protocol === "file:"
    ? "http://localhost:5000/api"
    : "/api";



// ========================================
// VARIÁVEIS
// ========================================

let mostrarTodas = false;



// ========================================
// ELEMENTOS
// ========================================

const tabelaDemandas =
    document.getElementById("tabelaDemandas");

const tabelaTodasDemandas =
    document.getElementById("tabelaTodasDemandas");

const contadorDemandas =
    document.getElementById("contadorDemandas");

const btnVerTodas =
    document.getElementById("btnVerTodas");

const modal =
    document.getElementById("modalNovaDemanda");

const formDemanda =
    document.getElementById("formDemanda");



// ========================================
// FORMATAR MOEDA
// ========================================

function formatarMoeda(valor) {

    return valor.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });

}



// ========================================
// PEGAR INICIAIS
// ========================================

function pegarIniciais(nome) {

    const palavras =
        nome.trim().split(" ");

    if (palavras.length >= 2) {

        return (
            palavras[0][0] +
            palavras[1][0]
        ).toUpperCase();

    }

    return nome
        .substring(0, 2)
        .toUpperCase();

}



// ========================================
// CRIAR LINHA
// ========================================

function escaparHtml(texto) {
    return String(texto ?? "").replace(/[&<>"']/g, caractere => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[caractere]));
}

function criarBadgeStatus(demanda) {
    if (demanda.classificacao === "REVISAR") {
        return `<span class="badge-status badge-revisar">Revisar</span>`;
    }

    return `<span class="badge-status">Integrado</span>`;
}

function criarLinha(demanda) {

    const linha =
        document.createElement("tr");

    linha.innerHTML = `
        <td>
            <div class="cliente-info">
                <div class="cliente-avatar">
                    ${escaparHtml(pegarIniciais(demanda.cliente))}
                </div>
                <div>
                    <strong>${escaparHtml(demanda.cliente)}</strong>
                    <span>${escaparHtml(demanda.email || "—")}</span>
                </div>
            </div>
        </td>
        <td>${escaparHtml(demanda.origem)}</td>
        <td>${escaparHtml(demanda.destino)}</td>
        <td>
            <strong>${formatarMoeda(demanda.valor)}</strong>
        </td>
        <td>
            <span class="badge-fonte">${escaparHtml(demanda.fonte)}</span>
        </td>
        <td>${criarBadgeStatus(demanda)}</td>
    `;

    return linha;
}


// ========================================
// RENDERIZAR TABELA PRINCIPAL
// ========================================

function renderizarDemandas() {

    if (!tabelaDemandas) {
        return;
    }


    tabelaDemandas.innerHTML = "";


    const quantidade =
        mostrarTodas
            ? demandas.length
            : Math.min(5, demandas.length);


    const lista =
        demandas.slice(0, quantidade);


    lista.forEach(demanda => {

        tabelaDemandas.appendChild(
            criarLinha(demanda)
        );

    });


    if (contadorDemandas) {

        contadorDemandas.textContent =
            `Exibindo ${quantidade} de ${demandas.length} demandas`;

    }


    if (btnVerTodas) {

        if (mostrarTodas) {

            btnVerTodas.textContent =
                "Mostrar menos ↑";

        } else {

            btnVerTodas.textContent =
                "Ver todas as demandas →";

        }

    }

}



// ========================================
// RENDERIZAR TODAS AS DEMANDAS
// ========================================

function renderizarTodasDemandas() {

    if (!tabelaTodasDemandas) {
        return;
    }


    tabelaTodasDemandas.innerHTML = "";


    demandas.forEach(demanda => {

        tabelaTodasDemandas.appendChild(
            criarLinha(demanda)
        );

    });

}



// ========================================
// ATUALIZAR DASHBOARD
// ========================================

function atualizarDashboard() {

    // TOTAL

    const total =
        document.getElementById("totalDemandas");

    if (total) {

        total.textContent =
            demandas.length;

    }



    // INTEGRADAS

    const integradas =
        document.getElementById("demandasIntegradas");

    if (integradas) {

        integradas.textContent =
            demandas.length;

    }



    // VALOR TOTAL

    const valorTotal =
        document.getElementById("valorTotal");

    if (valorTotal) {

        const soma =
            demandas.reduce(
                (total, demanda) =>
                    total + demanda.valor,
                0
            );

        valorTotal.textContent =
            formatarMoeda(soma);

    }



    // CSV

    const contadorCSV =
        document.getElementById("contadorCSV");

    if (contadorCSV) {

        const quantidadeCSV =
            demandas.filter(
                demanda => demanda.fonte === "CSV"
            ).length;

        contadorCSV.textContent =
            `${quantidadeCSV} registros`;

    }



    // JSON

    const contadorJSON =
        document.getElementById("contadorJSON");

    if (contadorJSON) {

        const quantidadeJSON =
            demandas.filter(
                demanda => demanda.fonte === "JSON"
            ).length;

        contadorJSON.textContent =
            `${quantidadeJSON} registros`;

    }



    // XLSX

    const contadorXLSX =
        document.getElementById("contadorXLSX");

    if (contadorXLSX) {

        const quantidadeXLSX =
            demandas.filter(
                demanda => demanda.fonte === "XLSX"
            ).length;

        contadorXLSX.textContent =
            `${quantidadeXLSX} registros`;

    }

}



// ========================================
// BOTÃO VER TODAS
// ========================================

if (btnVerTodas) {

    btnVerTodas.addEventListener(
        "click",
        function () {

            mostrarTodas =
                !mostrarTodas;

            renderizarDemandas();

        }
    );

}



// ========================================
// MENU LATERAL
// ========================================

const menuItems =
    document.querySelectorAll(".menu-item");

const sections =
    document.querySelectorAll(".section");

const tituloPagina =
    document.getElementById("tituloPagina");


menuItems.forEach(item => {

    item.addEventListener(
        "click",
        function () {

            const sectionId =
                this.dataset.section;


            // Remove ativo

            menuItems.forEach(menu => {

                menu.classList.remove("active");

            });


            // Ativa botão

            this.classList.add("active");


            // Esconde seções

            sections.forEach(section => {

                section.classList.remove("active");

            });


            // Mostra seção escolhida

            const section =
                document.getElementById(sectionId);


            if (section) {

                section.classList.add("active");

            }


            // Atualiza título

            const nomes = {

                dashboard: "Dashboard",
                demandas: "Demandas",
                fontes: "Fontes de dados",
                historico: "Histórico"

            };


            if (tituloPagina) {

                tituloPagina.textContent =
                    nomes[sectionId];

            }


            // Se abriu demandas,
            // mostra todas

            if (sectionId === "demandas") {

                renderizarTodasDemandas();

            }

        }
    );

});



// ========================================
// MODAL
// ========================================

function abrirModal() {

    if (modal) {

        modal.classList.add("show");

    }

}



function fecharModal() {

    if (modal) {

        modal.classList.remove("show");

    }

}



// ========================================
// BOTÃO NOVA DEMANDA
// ========================================

const btnNovaDemanda3 =
    document.getElementById("btnNovaDemanda3");


if (btnNovaDemanda3) {

    btnNovaDemanda3.addEventListener(
        "click",
        abrirModal
    );

}



// ========================================
// FECHAR MODAL
// ========================================

const btnFecharModal =
    document.getElementById("btnFecharModal");

const btnCancelar =
    document.getElementById("btnCancelar");


if (btnFecharModal) {

    btnFecharModal.addEventListener(
        "click",
        fecharModal
    );

}


if (btnCancelar) {

    btnCancelar.addEventListener(
        "click",
        fecharModal
    );

}



// ========================================
// CLICAR FORA DO MODAL
// ========================================

if (modal) {

    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                fecharModal();

            }

        }
    );

}



// ========================================
// NOVA DEMANDA
// ========================================

if (formDemanda) {

    formDemanda.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            const dados = {
                cliente: document.getElementById("cliente").value.trim(),
                origem: document.getElementById("origem").value.trim(),
                destino: document.getElementById("destino").value.trim(),
                valor: document.getElementById("valor").value,
                fonte: document.getElementById("fonte").value
            };

            if (!dados.fonte) {
                alert("Selecione a fonte da demanda.");
                return;
            }

            try {

                const resposta = await fetch(`${API_URL}/demandas`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(dados)
                });

                const resultado = await resposta.json();

                if (!resposta.ok) {
                    alert(resultado.erro || "Não foi possível salvar a demanda.");
                    return;
                }

                fecharModal();
                formDemanda.reset();

                await carregarDados();

                if (resultado.classificacao === "REVISAR") {
                    alert("Demanda cadastrada. O valor foge do padrão e foi marcado para revisão.");
                } else {
                    alert("Demanda adicionada com sucesso!");
                }

            } catch (erro) {
                alert("Não foi possível conectar à API. Verifique se o servidor está rodando.");
            }
        }
    );
}


// ========================================
// CARREGAR DADOS DA API
// ========================================

async function carregarDados() {

    let falhou = false;

    try {

        const resposta = await fetch(`${API_URL}/demandas`);

        if (!resposta.ok) {
            throw new Error("Falha ao buscar demandas");
        }

        demandas = await resposta.json();

    } catch (erro) {

        demandas = [];
        falhou = true;
    }

    renderizarDemandas();
    renderizarTodasDemandas();
    atualizarDashboard();

    if (falhou && contadorDemandas) {
        contadorDemandas.textContent =
            "Não foi possível conectar à API. Execute: python api.py";
    }
}


// ========================================
// HISTÓRICO DE IMPORTAÇÕES
// ========================================

async function carregarHistorico() {

    const lista = document.getElementById("listaHistorico");

    if (!lista) {
        return;
    }

    try {

        const resposta = await fetch(`${API_URL}/historico`);

        if (!resposta.ok) {
            throw new Error("Falha ao buscar histórico");
        }

        const importacoes = await resposta.json();

        if (importacoes.length === 0) {
            lista.innerHTML =
                `<div class="history-item">Nenhuma importação registrada.</div>`;
            return;
        }

        lista.innerHTML = importacoes.map(item => {

            const aproveitamento = item.registros_recebidos > 0
                ? (item.registros_finais / item.registros_recebidos * 100).toFixed(1)
                : "0.0";

            const data = new Date(item.data_hora)
                .toLocaleString("pt-BR");

            return `
                <div class="history-item">
                    <div class="history-icon">✓</div>
                    <div class="history-info">
                        <strong>Importação concluída</strong>
                        <span>${item.arquivos_processados} arquivos · ${item.registros_inseridos} novos · ${item.duplicados_removidos} duplicados</span>
                    </div>
                    <div class="history-data">
                        <strong>${item.registros_finais}</strong>
                        <span>registros</span>
                    </div>
                    <div class="history-data">
                        <strong>${aproveitamento}%</strong>
                        <span>aproveitamento</span>
                    </div>
                    <div class="history-date">${escaparHtml(data)}</div>
                </div>
            `;

        }).join("");

    } catch (erro) {

        lista.innerHTML =
            `<div class="history-item">Não foi possível carregar o histórico.</div>`;
    }
}


// ========================================
// INICIALIZAÇÃO
// ========================================

carregarDados();
carregarHistorico();
