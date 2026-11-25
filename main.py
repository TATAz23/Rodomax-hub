from src.banco import testar_conexao
from src.config import DATA_RAW
from src.pipeline import processar_arquivos


def main():

    print("================================")
    print("       RODOMAX HUB")
    print("================================")

    testar_conexao()

    pasta = DATA_RAW

    processar_arquivos(pasta)


if __name__ == "__main__":
    main()