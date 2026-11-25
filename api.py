"""
API do Rodomax HUB.

    http://localhost:5000
"""

import math

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy import text

from src.banco import engine
from src.config import BASE_DIR
from src.ia_classificacao import classificar_anomalias

PASTA_FRONTEND = BASE_DIR / "frontend"

FONTES_VALIDAS = ["CSV", "JSON", "XLSX"]
CLASSIFICACOES_VALIDAS = ["NORMAL", "REVISAR", "HISTORICO_INSUFICIENTE"]

app = Flask(__name__, static_folder=None)


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def numero(valor):
    """Converte NUMERIC (Decimal) do PostgreSQL em float para o JSON."""
    return None if valor is None else float(valor)


def data_iso(valor):
    if valor is None:
        return None
    return valor.isoformat() if hasattr(valor, "isoformat") else str(valor)


def demanda_para_json(linha):
    return {
        "id": linha["id"],
        "cliente": linha["cliente"],
        "email": linha["email"] or "",
        "telefone": linha["telefone"] or "",
        "origem": linha["origem"],
        "destino": linha["destino"],
        "valor": numero(linha["valor_frete"]),
        "fonte": linha["fonte"],
        "classificacao": linha["classificacao_ia"],
        "score": numero(linha["score_ia"]),
        "data_importacao": data_iso(linha["data_importacao"]),
    }


def erro(mensagem, status):
    return jsonify({"erro": mensagem}), status


# ==========================================
# CORS (permite abrir o index.html direto do disco)
# ==========================================

@app.after_request
def liberar_cors(resposta):
    resposta.headers["Access-Control-Allow-Origin"] = "*"
    resposta.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resposta


@app.errorhandler(Exception)
def erro_inesperado(excecao):
    # Deixa o Flask tratar erros HTTP normais (404, 405...)
    from werkzeug.exceptions import HTTPException

    if isinstance(excecao, HTTPException):
        return excecao

    print(f"Erro na API: {excecao}")
    return erro("Erro interno ao acessar o banco de dados.", 500)


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/api/saude")
def saude():
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))
    return jsonify({"status": "ok"})


@app.get("/api/demandas")
def listar_demandas():
    """
    Lista as demandas, da mais recente para a mais antiga.
    Filtros opcionais: ?fonte=CSV  ?classificacao=REVISAR
    """

    filtros = []
    parametros = {}

    fonte = request.args.get("fonte", "").upper()
    classificacao = request.args.get("classificacao", "").upper()

    if fonte:
        if fonte not in FONTES_VALIDAS:
            return erro("Fonte inválida.", 400)
        filtros.append("fonte = :fonte")
        parametros["fonte"] = fonte

    if classificacao:
        if classificacao not in CLASSIFICACOES_VALIDAS:
            return erro("Classificação inválida.", 400)
        filtros.append("classificacao_ia = :classificacao")
        parametros["classificacao"] = classificacao

    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    sql = f"""
        SELECT id, cliente, email, telefone, origem, destino,
               valor_frete, fonte, classificacao_ia, score_ia,
               data_importacao
        FROM rodomax.demandas
        {where}
        ORDER BY id DESC
    """

    with engine.connect() as conexao:
        linhas = conexao.execute(text(sql), parametros).mappings().all()

    return jsonify([demanda_para_json(linha) for linha in linhas])


@app.get("/api/resumo")
def resumo():
    with engine.connect() as conexao:

        geral = conexao.execute(text("""
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(valor_frete), 0) AS valor_total
            FROM rodomax.demandas
        """)).mappings().one()

        por_fonte = conexao.execute(text("""
            SELECT fonte, COUNT(*) AS quantidade
            FROM rodomax.demandas
            GROUP BY fonte
        """)).mappings().all()

        por_classificacao = conexao.execute(text("""
            SELECT classificacao_ia, COUNT(*) AS quantidade
            FROM rodomax.demandas
            GROUP BY classificacao_ia
        """)).mappings().all()

    return jsonify({
        "total": geral["total"],
        "valor_total": numero(geral["valor_total"]),
        "por_fonte": {
            (linha["fonte"] or "SEM_FONTE"): linha["quantidade"]
            for linha in por_fonte
        },
        "por_classificacao": {
            (linha["classificacao_ia"] or "PENDENTE"): linha["quantidade"]
            for linha in por_classificacao
        },
    })


@app.get("/api/historico")
def historico():
    with engine.connect() as conexao:
        linhas = conexao.execute(text("""
            SELECT id, data_hora, arquivos_processados,
                   registros_recebidos, registros_incompletos,
                   duplicados_removidos, registros_finais,
                   registros_inseridos, registros_ignorados
            FROM rodomax.importacoes
            ORDER BY id DESC
            LIMIT 50
        """)).mappings().all()

    resultado = []

    for linha in linhas:
        item = dict(linha)
        item["data_hora"] = data_iso(item["data_hora"])
        resultado.append(item)

    return jsonify(resultado)


@app.post("/api/demandas")
def criar_demanda():
    """Cadastra uma demanda manualmente (formulário 'Nova demanda')."""

    dados = request.get_json(silent=True) or {}

    cliente = str(dados.get("cliente", "")).strip().upper()
    origem = str(dados.get("origem", "")).strip().upper()
    destino = str(dados.get("destino", "")).strip().upper()
    email = str(dados.get("email", "")).strip().lower()
    telefone = "".join(
        caractere for caractere in str(dados.get("telefone", ""))
        if caractere.isdigit()
    )
    fonte = str(dados.get("fonte", "")).strip().upper()

    erros = []

    for nome, valor in [
        ("cliente", cliente), ("origem", origem), ("destino", destino)
    ]:
        if not valor:
            erros.append(f"{nome} é obrigatório")

    if fonte not in FONTES_VALIDAS:
        erros.append("fonte inválida")

    try:
        valor_frete = float(
            str(dados.get("valor", "")).strip().replace(",", ".")
        )
        if not math.isfinite(valor_frete) or not 0 < valor_frete < 10**10:
            raise ValueError
    except (ValueError, TypeError):
        valor_frete = None
        erros.append("valor do frete deve ser um número maior que zero")

    if erros:
        return jsonify({"erro": "; ".join(erros)}), 400

    with engine.begin() as conexao:

        # Classifica a nova demanda em relação ao histórico existente
        existentes = conexao.execute(text("""
            SELECT valor_frete FROM rodomax.demandas
            WHERE valor_frete IS NOT NULL
        """)).fetchall()

        classificacao = None
        score = None

        try:
            valores = [float(linha[0]) for linha in existentes]
            df = pd.DataFrame({"valor_frete": valores + [valor_frete]})
            ultima = classificar_anomalias(df).iloc[-1]

            classificacao = ultima["classificacao_ia"]

            if not pd.isna(ultima["score_ia"]):
                score = float(ultima["score_ia"])

        except Exception as falha:
            print(f"Não foi possível classificar a nova demanda: {falha}")

        criada = conexao.execute(text("""
            INSERT INTO rodomax.demandas (
                cliente, email, telefone, origem, destino,
                valor_frete, fonte, classificacao_ia, score_ia
            )
            VALUES (
                :cliente, :email, :telefone, :origem, :destino,
                :valor_frete, :fonte, :classificacao_ia, :score_ia
            )
            ON CONFLICT DO NOTHING
            RETURNING id
        """), {
            "cliente": cliente,
            "email": email,
            "telefone": telefone,
            "origem": origem,
            "destino": destino,
            "valor_frete": valor_frete,
            "fonte": fonte,
            "classificacao_ia": classificacao,
            "score_ia": score,
        }).first()

    if criada is None:
        return erro("Já existe uma demanda idêntica cadastrada.", 409)

    return jsonify({
        "id": criada[0],
        "classificacao": classificacao,
        "mensagem": "Demanda cadastrada com sucesso.",
    }), 201


# ==========================================
# FRONTEND
# ==========================================

@app.get("/")
def pagina_inicial():
    return send_from_directory(PASTA_FRONTEND, "index.html")


@app.get("/<path:arquivo>")
def arquivos_estaticos(arquivo):
    return send_from_directory(PASTA_FRONTEND, arquivo)


if __name__ == "__main__":
    print("Rodomax HUB - API rodando em http://localhost:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
