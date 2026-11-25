from pathlib import Path

# Raiz do projeto (pasta que contém main.py), independente de onde o terminal foi aberto
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
