import pandas as pd


def normalizar_textos(df):

    colunas_texto = [
        "cliente",
        "origem",
        "destino"
    ]

    for coluna in colunas_texto:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    return df


def normalizar_email(df):

    if "email" in df.columns:

        df["email"] = (
            df["email"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    return df


def normalizar_telefone(df):

    if "telefone" in df.columns:

        df["telefone"] = (
            df["telefone"]
            .fillna("")
            .astype(str)
            .str.replace(r"\D", "", regex=True)
        )

    return df