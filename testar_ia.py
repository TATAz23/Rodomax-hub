
import pandas as pd

from src.ia_classificacao import classificar_anomalias
from src.config import DATA_PROCESSED


def main():

    print("================================")
    print("     TESTE DA IA - RODOMAX")
    print("================================")

    # Ler os dados tratados pelo pipeline
    caminho = DATA_PROCESSED / "demandas_tratadas.csv"

    df = pd.read_csv(
        caminho,
        encoding="utf-8-sig"
    )

    print(f"\nDemandas encontradas: {len(df)}")

    # Executar a classificação da IA
    resultado = classificar_anomalias(df)

    # Mostrar resultados
    print("\n========== RESULTADO DA IA ==========")

    print(
        resultado[
            [
                "cliente",
                "origem",
                "destino",
                "valor_frete",
                "classificacao_ia"
            ]
        ].to_string(index=False)
    )

    # Contabilizar classificações
    print("\n========== RESUMO ==========")

    print(
        resultado["classificacao_ia"].value_counts()
    )

    # Salvar resultado separado
    resultado.to_csv(
        DATA_PROCESSED / "demandas_classificadas.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nResultado salvo com sucesso!")


if __name__ == "__main__":
    main()
