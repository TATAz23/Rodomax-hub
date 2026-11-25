
import pandas as pd
from pathlib import Path
from .config import DATA_PROCESSED


def separar_demandas(df):

    print("\n========== SEPARAÇÃO DAS DEMANDAS ==========")

    # Verificar se a classificação existe
    if "classificacao_ia" not in df.columns:

        raise ValueError(
            "A coluna classificacao_ia não foi encontrada."
        )

    # Criar os grupos
    grupos = {
        "normais": df[
            df["classificacao_ia"] == "NORMAL"
        ].copy(),

        "revisar": df[
            df["classificacao_ia"] == "REVISAR"
        ].copy(),

        "historico_insuficiente": df[
            df["classificacao_ia"] == "HISTORICO_INSUFICIENTE"
        ].copy()
    }

    # Pasta onde os arquivos serão salvos
    pasta = DATA_PROCESSED

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    # Nomes dos arquivos
    arquivos = {
        "normais": "demandas_normais.csv",
        "revisar": "demandas_revisar.csv",
        "historico_insuficiente": "demandas_historico_insuficiente.csv"
    }

    # Salvar cada grupo
    for categoria, dados in grupos.items():

        caminho = pasta / arquivos[categoria]

        dados.to_csv(
            caminho,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            f"{categoria.upper()}: {len(dados)} registros"
        )

        print(
            f"Arquivo salvo: {caminho}"
        )

    print("\nSeparação concluída.")

    return grupos
