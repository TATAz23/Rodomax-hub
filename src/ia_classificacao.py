import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest


# Limites usados na classificação
Z_EXTREMO = 3.5      # desvio robusto a partir do qual o valor é sempre suspeito
Z_SUSPEITO = 2.5     # desvio mínimo para confirmar o alerta do IsolationForest
MIN_REGISTROS = 10   # histórico mínimo para classificar


def classificar_anomalias(df):
    """
    Classifica cada demanda como NORMAL, REVISAR ou HISTORICO_INSUFICIENTE
    com base no valor do frete.

    Duas camadas:
    1. Regra estatística robusta (mediana + MAD sobre o log do valor):
       valores muito distantes da mediana são sempre marcados.
    2. IsolationForest: pontua o quão isolado o valor está. Só gera alerta
       quando o valor também está moderadamente distante da mediana,
       evitando marcar fretes baixos/altos que são normais.
    """

    df = df.copy()

    if "valor_frete" not in df.columns:
        raise ValueError("Coluna valor_frete não encontrada.")

    valores = pd.to_numeric(df["valor_frete"], errors="coerce")

    validos = valores.notna() & (valores > 0)

    if validos.sum() < MIN_REGISTROS:
        df["classificacao_ia"] = "HISTORICO_INSUFICIENTE"
        df["score_ia"] = None
        df["motivo_ia"] = ""
        return df

    log_valores = np.log(valores[validos])

    # ----- Camada 1: desvio robusto (mediana e MAD) -----
    mediana = log_valores.median()
    mad = (log_valores - mediana).abs().median() * 1.4826

    if mad == 0:
        z = pd.Series(0.0, index=log_valores.index)
    else:
        z = (log_valores - mediana) / mad

    # ----- Camada 2: IsolationForest sobre o valor -----
    modelo = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )

    X = log_valores.to_numpy().reshape(-1, 1)

    modelo.fit(X)

    alerta_forest = pd.Series(
        modelo.predict(X) == -1,
        index=log_valores.index
    )

    pontuacao = pd.Series(
        -modelo.decision_function(X),
        index=log_valores.index
    )

    # ----- Decisão final -----
    extremo = z.abs() >= Z_EXTREMO
    suspeito = alerta_forest & (z.abs() >= Z_SUSPEITO)

    revisar = extremo | suspeito

    df["classificacao_ia"] = "NORMAL"
    df["score_ia"] = None
    df["motivo_ia"] = ""

    df.loc[pontuacao.index, "score_ia"] = pontuacao

    df.loc[revisar[revisar].index, "classificacao_ia"] = "REVISAR"

    mediana_real = float(np.exp(mediana))

    for indice in revisar[revisar].index:

        direcao = "acima" if z[indice] > 0 else "abaixo"

        df.loc[indice, "motivo_ia"] = (
            f"valor muito {direcao} da mediana "
            f"(R$ {mediana_real:,.2f})"
        )

    # Valores inválidos (não numéricos ou <= 0) sempre vão para revisão
    df.loc[~validos, "classificacao_ia"] = "REVISAR"
    df.loc[~validos, "motivo_ia"] = "valor de frete inválido"

    return df
