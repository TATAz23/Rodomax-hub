from pathlib import Path
from datetime import datetime
import json

from .config import DATA_PROCESSED


# ==========================================
# CONFIGURAÇÃO DO ARQUIVO DE LOG
# ==========================================

CAMINHO_LOG = DATA_PROCESSED / "logs.json"


# ==========================================
# REGISTRAR LOG
# ==========================================

def registrar_log(
    arquivos_processados,
    registros_recebidos,
    registros_incompletos,
    duplicados_removidos,
    registros_finais,
    registros_inseridos,
    registros_ignorados
):

    # Cria a pasta caso ela não exista
    CAMINHO_LOG.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Cria o registro da execução
    log = {
        "data_hora": datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
        "arquivos_processados": arquivos_processados,
        "registros_recebidos": registros_recebidos,
        "registros_incompletos": registros_incompletos,
        "duplicados_removidos": duplicados_removidos,
        "registros_finais": registros_finais,
        "registros_inseridos": registros_inseridos,
        "registros_ignorados": registros_ignorados
    }

    # Lista onde serão armazenados os logs
    logs = []

    # Verifica se já existe um arquivo de log
    if CAMINHO_LOG.exists():

        try:

            with open(
                CAMINHO_LOG,
                "r",
                encoding="utf-8"
            ) as arquivo:

                logs = json.load(arquivo)

        except (json.JSONDecodeError, FileNotFoundError):

            logs = []

    # Adiciona o novo log
    logs.append(log)

    # Salva os logs
    with open(
        CAMINHO_LOG,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            logs,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== LOG ==========")

    print(
        f"Log registrado em: {CAMINHO_LOG}"
    )