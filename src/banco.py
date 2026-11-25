from sqlalchemy import create_engine, text
import pandas as pd

# ==========================================
# CONFIGURAÇÃO DO POSTGRESQL
# ==========================================

USUARIO = "postgres"
SENHA = "banco123"
HOST = "localhost"
PORTA = "5432"
BANCO = "rodomax_hub"

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{USUARIO}:{SENHA}@{HOST}:{PORTA}/{BANCO}"
)

engine = create_engine(DATABASE_URL)


# ==========================================
# TESTAR CONEXÃO
# ==========================================

def testar_conexao():
    try:
        with engine.connect() as conexao:
            print("Conexão com PostgreSQL realizada com sucesso!")

    except Exception as erro:
        print("Erro ao conectar com PostgreSQL:")
        print(erro)


# ==========================================
# INSERIR DEMANDAS
# ==========================================


def inserir_dados(df):


    registros_inseridos = 0
    registros_ignorados = 0

    try:

        with engine.begin() as conexao:

            for _, registro in df.iterrows():

                dados = registro.to_dict()

                # Converter valores NaN para None
                for campo, valor in dados.items():

                    if pd.isna(valor):
                        dados[campo] = None

                resultado = conexao.execute(
                    text("""
                        INSERT INTO rodomax.demandas (
                            cliente,
                            email,
                            telefone,
                            origem,
                            destino,
                            valor_frete,
                            fonte,
                            classificacao_ia,
                            score_ia
                        )
                        VALUES (
                            :cliente,
                            :email,
                            :telefone,
                            :origem,
                            :destino,
                            :valor_frete,
                            :fonte,
                            :classificacao_ia,
                            :score_ia
                        )
                        ON CONFLICT DO NOTHING
                    """),
                    dados
                )

                if resultado.rowcount > 0:

                    registros_inseridos += 1

                else:

                    registros_ignorados += 1

                    # Atualizar a classificação dos registros existentes
                    conexao.execute(
                        text("""
                            UPDATE rodomax.demandas
                            SET
                                classificacao_ia = :classificacao_ia,
                                score_ia = :score_ia
                            WHERE cliente = :cliente
                              AND email IS NOT DISTINCT FROM :email
                              AND telefone IS NOT DISTINCT FROM :telefone
                              AND origem = :origem
                              AND destino = :destino
                              AND valor_frete IS NOT DISTINCT FROM :valor_frete
                              AND fonte = :fonte
                        """),
                        dados
                    )

        print(
            f"Novos registros inseridos: {registros_inseridos}"
        )

        print(
            f"Registros já existentes ignorados: {registros_ignorados}"
        )

        return registros_inseridos, registros_ignorados

    except Exception as erro:

        print("Erro ao inserir dados no PostgreSQL:")
        print(erro)

        return 0, 0


# ==========================================
# REGISTRAR HISTÓRICO DA IMPORTAÇÃO
# ==========================================

def registrar_importacao(
    arquivos_processados,
    registros_recebidos,
    registros_incompletos,
    duplicados_removidos,
    registros_finais,
    registros_inseridos,
    registros_ignorados
):

    try:

        with engine.begin() as conexao:

            conexao.execute(
                text("""
                    INSERT INTO rodomax.importacoes (
                        arquivos_processados,
                        registros_recebidos,
                        registros_incompletos,
                        duplicados_removidos,
                        registros_finais,
                        registros_inseridos,
                        registros_ignorados
                    )
                    VALUES (
                        :arquivos_processados,
                        :registros_recebidos,
                        :registros_incompletos,
                        :duplicados_removidos,
                        :registros_finais,
                        :registros_inseridos,
                        :registros_ignorados
                    )
                """),
                {
                    "arquivos_processados": arquivos_processados,
                    "registros_recebidos": registros_recebidos,
                    "registros_incompletos": registros_incompletos,
                    "duplicados_removidos": duplicados_removidos,
                    "registros_finais": registros_finais,
                    "registros_inseridos": registros_inseridos,
                    "registros_ignorados": registros_ignorados
                }
            )

        print(
            "Histórico da importação registrado com sucesso!"
        )

    except Exception as erro:

        print("Erro ao registrar histórico da importação:")
        print(erro)