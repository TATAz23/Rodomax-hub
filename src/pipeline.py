
import pandas as pd
from pathlib import Path

from .logs import registrar_log
from .config import DATA_PROCESSED

from src.banco import (
    inserir_dados,
    registrar_importacao
)

from src.limpeza import (
    remover_registros_incompletos,
    remover_duplicados,
    validar_dados
)

from src.normalizacao import (
    normalizar_textos,
    normalizar_email,
    normalizar_telefone
)

from .ia_classificacao import classificar_anomalias
from .separacao import separar_demandas


# ==========================================
# LEITURA DOS DADOS
# ==========================================

def ler_dados(caminho):

    extensao = caminho.suffix.lower()

    if extensao == ".csv":
        df = pd.read_csv(caminho)

    elif extensao == ".xlsx":
        df = pd.read_excel(caminho)

    elif extensao == ".json":
        df = pd.read_json(caminho)

    else:
        return None

    return df


# ==========================================
# BUSCA DOS ARQUIVOS
# ==========================================

def encontrar_arquivos(pasta):

    pasta = Path(pasta)

    arquivos = []

    for arquivo in pasta.iterdir():

        if arquivo.suffix.lower() in [".csv", ".xlsx", ".json"]:
            arquivos.append(arquivo)

    return arquivos


# ==========================================
# AUDITORIA INICIAL
# ==========================================

def auditoria_inicial(df):

    print("\n========== AUDITORIA INICIAL ==========")

    print(
        f"Total de registros: {len(df)}"
    )

    print("\nValores nulos por coluna:")

    print(
        df.isnull().sum()
    )

    print("\nRegistros duplicados:")

    print(
        df.duplicated().sum()
    )


# ==========================================
# SALVAR DADOS PROCESSADOS
# ==========================================

def salvar_dados_processados(df):

    caminho = Path(
        DATA_PROCESSED / "demandas_tratadas.csv"
    )

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "\n========== ARQUIVO PROCESSADO =========="
    )

    print(
        f"Arquivo salvo em: {caminho}"
    )


# ==========================================
# SALVAR DADOS REJEITADOS
# ==========================================

def salvar_dados_rejeitados(df):

    caminho = Path(
        DATA_PROCESSED / "demandas_rejeitadas.csv"
    )

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if df.empty:

        print("\nNenhum registro rejeitado.")

        return

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "\n========== REGISTROS REJEITADOS =========="
    )

    print(
        f"Total rejeitado: {len(df)}"
    )

    print(
        f"Arquivo salvo em: {caminho}"
    )


# ==========================================
# SALVAR DADOS DUPLICADOS
# ==========================================

def salvar_dados_duplicados(df):

    caminho = Path(
        DATA_PROCESSED / "demandas_duplicadas.csv"
    )

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Duplicados salvos em: {caminho} ({len(df)} registros)"
    )


# ==========================================
# AUDITORIA FINAL
# ==========================================

def auditoria_final(
    registros_iniciais,
    registros_incompletos,
    duplicados,
    registros_rejeitados,
    registros_finais
):

    print("\n========== AUDITORIA FINAL ==========")

    print(
        f"Registros recebidos:       {registros_iniciais}"
    )

    print(
        f"Registros incompletos:     {registros_incompletos}"
    )

    print(
        f"Duplicados removidos:      {duplicados}"
    )

    print(
        f"Registros rejeitados:      {registros_rejeitados}"
    )

    print(
        f"Registros aptos:           {registros_finais}"
    )

    if registros_iniciais > 0:

        aproveitamento = (
            registros_finais /
            registros_iniciais
        ) * 100

        print(
            f"Taxa de aproveitamento:    {aproveitamento:.2f}%"
        )


# ==========================================
# CLASSIFICAÇÃO COM IA
# ==========================================

def aplicar_classificacao_ia(df):

    print("\n========== CLASSIFICAÇÃO COM IA ==========")

    df = classificar_anomalias(df)

    print("\nResultado da classificação:")

    print(
        df["classificacao_ia"].value_counts()
    )

    print("\nRegistros sinalizados para revisão:")

    registros_revisar = df[
        df["classificacao_ia"] == "REVISAR"
    ]

    if registros_revisar.empty:

        print("Nenhum registro sinalizado.")

    else:

        print(
            registros_revisar.to_string(index=False)
        )

    return df


# ==========================================
# PROCESSAMENTO PRINCIPAL
# ==========================================

def processar_arquivos(pasta):

    print(
        "\n========== BUSCA DE ARQUIVOS =========="
    )

    # --------------------------------------
    # BUSCAR ARQUIVOS
    # --------------------------------------

    arquivos = encontrar_arquivos(pasta)

    if not arquivos:

        print("Nenhum arquivo encontrado.")

        return

    print(
        f"Arquivos encontrados: {len(arquivos)}"
    )

    for arquivo in arquivos:

        print(
            f"- {arquivo.name}"
        )

    # ======================================
    # LEITURA DOS ARQUIVOS
    # ======================================

    print(
        "\n========== LEITURA DAS FONTES =========="
    )

    lista_dados = []

    for arquivo in arquivos:

        print(
            f"Lendo: {arquivo.name}"
        )

        df = ler_dados(arquivo)

        if df is not None:

            print(
                f"Registros encontrados: {len(df)}"
            )

            # Identifica a origem do arquivo
            df["fonte"] = (
                arquivo
                .suffix
                .replace(".", "")
                .upper()
            )

            lista_dados.append(df)

    # --------------------------------------
    # VERIFICAR SE EXISTEM DADOS
    # --------------------------------------

    if not lista_dados:

        print(
            "Nenhum dado válido encontrado."
        )

        return

    # ======================================
    # UNIFICAÇÃO DOS LOTES
    # ======================================

    print(
        "\n========== UNIFICAÇÃO DOS LOTES =========="
    )

    df = pd.concat(
        lista_dados,
        ignore_index=True
    )

    # Guarda a quantidade original
    registros_iniciais = len(df)

    print(
        f"Total de registros recebidos: {registros_iniciais}"
    )

    # ======================================
    # AUDITORIA INICIAL
    # ======================================

    auditoria_inicial(df)

    # ======================================
    # LIMPEZA
    # ======================================

    print(
        "\n========== LIMPEZA DOS DADOS =========="
    )

    df, registros_incompletos = (
        remover_registros_incompletos(df)
    )

    # ======================================
    # NORMALIZAÇÃO
    # ======================================

    print(
        "\n========== NORMALIZAÇÃO =========="
    )

    df = normalizar_textos(df)

    df = normalizar_email(df)

    df = normalizar_telefone(df)

    print(
        "Textos normalizados."
    )

    print(
        "E-mails normalizados."
    )

    print(
        "Telefones normalizados."
    )

    # ======================================
    # REMOÇÃO DE DUPLICADOS
    # ======================================

    print(
        "\n========== REMOÇÃO DE DUPLICADOS =========="
    )

    df, df_duplicados, duplicados = remover_duplicados(df)

    salvar_dados_duplicados(df_duplicados)

    # ======================================
    # VALIDAÇÃO DOS DADOS
    # ======================================

    print(
        "\n========== VALIDAÇÃO DOS DADOS =========="
    )

    # A validação retorna dois DataFrames:
    # 1. Registros válidos
    # 2. Registros rejeitados

    df, df_rejeitados = validar_dados(df)

    registros_rejeitados = len(df_rejeitados)

    print(
        f"\nRegistros válidos: {len(df)}"
    )

    print(
        f"Registros rejeitados: {registros_rejeitados}"
    )

    # ======================================
    # SALVAR REGISTROS REJEITADOS
    # ======================================

    salvar_dados_rejeitados(df_rejeitados)


    # ======================================
    # CLASSIFICAÇÃO COM IA
    # ======================================

    if not df.empty:

        df = aplicar_classificacao_ia(df)

    else:

        print(
            "\nNenhum registro válido para classificação."
        )

    # ======================================
    # SEPARAÇÃO AUTOMÁTICA DAS DEMANDAS
    # ======================================

    if not df.empty:

        grupos_demandas = separar_demandas(df)

    # ======================================
    # MOSTRAR DADOS TRATADOS
    # ======================================

    print(
        "\n========== DADOS TRATADOS =========="
    )

    if not df.empty:

        print(
            df.to_string(index=False)
        )

    else:

        print("Nenhum registro válido restante.")

    # ======================================
    # SALVAR ARQUIVO PROCESSADO
    # ======================================

    salvar_dados_processados(df)

    # ======================================
    # INSERIR NO POSTGRESQL
    # ======================================

    print(
        "\n========== POSTGRESQL =========="
    )

    if not df.empty:

        registros_inseridos, registros_ignorados = (
            inserir_dados(df)
        )

    else:

        registros_inseridos = 0
        registros_ignorados = 0

        print(
            "Nenhum registro válido para inserir."
        )

    # ======================================
    # AUDITORIA FINAL
    # ======================================

    auditoria_final(
        registros_iniciais,
        registros_incompletos,
        duplicados,
        registros_rejeitados,
        len(df)
    )

    # ======================================
    # REGISTRAR LOG
    # ======================================

    registrar_log(
        arquivos_processados=len(arquivos),
        registros_recebidos=registros_iniciais,
        registros_incompletos=registros_incompletos,
        duplicados_removidos=duplicados,
        registros_finais=len(df),
        registros_inseridos=registros_inseridos,
        registros_ignorados=registros_ignorados
    )

    # ======================================
    # REGISTRAR HISTÓRICO DE IMPORTAÇÃO
    # ======================================

    registrar_importacao(
        arquivos_processados=len(arquivos),
        registros_recebidos=registros_iniciais,
        registros_incompletos=registros_incompletos,
        duplicados_removidos=duplicados,
        registros_finais=len(df),
        registros_inseridos=registros_inseridos,
        registros_ignorados=registros_ignorados
    )
