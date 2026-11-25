import pandas as pd
import re
import math


def remover_registros_incompletos(df):

    registros_antes = len(df)

    colunas_obrigatorias = [
        "cliente",
        "origem",
        "destino"
    ]

    df = df.dropna(subset=colunas_obrigatorias)

    registros_depois = len(df)

    removidos = registros_antes - registros_depois

    print(f"Registros antes da limpeza: {registros_antes}")
    print(f"Registros incompletos removidos: {removidos}")
    print(f"Registros restantes: {registros_depois}")

    return df, removidos




def remover_duplicados(df):
    registros_antes = len(df)

    colunas_comparacao = [
        "cliente",
        "email",
        "telefone",
        "origem",
        "destino"
    ]

    colunas_comparacao = [
        coluna for coluna in colunas_comparacao
        if coluna in df.columns
    ]

    df = df.copy()

    # O valor do frete pode vir como texto (CSV) ou número (JSON/XLSX).
    # Cria uma chave numérica para que "1659.23" e 1659.23 sejam iguais.
    # Valores que não viram número mantêm o texto original.
    if "valor_frete" in df.columns:
        texto = df["valor_frete"].astype(str).str.strip().str.replace(",", ".", regex=False)
        numerico = pd.to_numeric(texto, errors="coerce").round(2)
        df["_chave_valor"] = numerico.astype(object).where(numerico.notna(), texto)
        colunas_comparacao.append("_chave_valor")

    mascara_duplicados = df.duplicated(
        subset=colunas_comparacao,
        keep="first"
    )

    df_duplicados = df[mascara_duplicados].drop(columns=["_chave_valor"], errors="ignore").copy()

    df = df.drop_duplicates(
        subset=colunas_comparacao,
        keep="first"
    ).drop(columns=["_chave_valor"], errors="ignore")

    duplicados_removidos = registros_antes - len(df)

    print(f"Registros antes: {registros_antes}")
    print(f"Duplicados removidos: {duplicados_removidos}")
    print(f"Registros restantes: {len(df)}")

    return df, df_duplicados, duplicados_removidos



def validar_email(email):

    if email == "":
        return True

    padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return bool(re.match(padrao, email))


def validar_telefone(telefone):

    if telefone == "":
        return True

    return len(telefone) in [10, 11]


def validar_valor(valor):
    try:
        valor = float(str(valor).strip())

        if not math.isfinite(valor):
            return False

        return valor > 0

    except (ValueError, TypeError):
        return False


def validar_dados(df):
    validos = []
    rejeitados = []

    for _, linha in df.iterrows():
        erros = []

        # Campos obrigatórios
        for campo in ["cliente", "origem", "destino"]:
            if pd.isna(linha[campo]) or str(linha[campo]).strip() == "":
                erros.append(f"{campo} vazio")

        # Validar valor do frete
        try:
            valor = float(str(linha["valor_frete"]).strip().replace(",", "."))
            if valor <= 0:
                erros.append("frete deve ser maior que zero")
        except (ValueError, TypeError):
            erros.append("frete inválido")

        registro = linha.to_dict()

        # Validar e-mail sem rejeitar a demanda
        if not validar_email(linha["email"]):
            registro["email_invalido"] = True
        else:
            registro["email_invalido"] = False

        # Validar telefone sem rejeitar a demanda
        if not validar_telefone(linha["telefone"]):
            registro["telefone_invalido"] = True
        else:
            registro["telefone_invalido"] = False

        if erros:
            registro["motivo_rejeicao"] = "; ".join(erros)
            rejeitados.append(registro)
        else:
            registro["valor_frete"] = valor
            validos.append(registro)

    df_validos = pd.DataFrame(validos)
    df_rejeitados = pd.DataFrame(rejeitados)

    return df_validos, df_rejeitados