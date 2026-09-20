import json
import re
from datetime import datetime
from pathlib import Path

import cv2
from insightface.app import FaceAnalysis

from banco import cadastrar_pessoa


PASTA_FOTOS_CADASTRO = Path("dados/fotos_cadastro")
TECLA_CAPTURAR = ord("c")
TECLA_SAIR = ord("q")


def criar_nome_arquivo(nome):
    nome_seguro = re.sub(r"[^a-zA-Z0-9_-]", "_", nome.strip())
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{nome_seguro}_{data_hora}.jpg"


def iniciar_analisador():
    analisador = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    analisador.prepare(ctx_id=0, det_size=(640, 800))

    return analisador


def desenhar_rosto(frame, rosto, cor, mensagem):
    x1, y1, x2, y2 = rosto.bbox.astype(int)

    cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
    cv2.putText(
        frame,
        mensagem,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        cor,
        2
    )


def capturar_foto_cadastro(analisador):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Nao foi possivel acessar a camera.")
        return None, None

    print("Posicione apenas um rosto na camera.")
    print("Pressione C para capturar ou Q para cancelar.")

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            print("Nao foi possivel ler a imagem da camera.")
            break

        rostos = analisador.get(frame)
        tela = frame.copy()

        if len(rostos) == 1:
            rosto = rostos[0]
            desenhar_rosto(
                tela,
                rosto,
                (0, 255, 0),
                "Rosto detectado - pressione C"
            )
        else:
            rosto = None

            if len(rostos) == 0:
                mensagem = "Nenhum rosto detectado"
            else:
                mensagem = "Deixe somente uma pessoa na imagem"

            cv2.putText(
                tela,
                mensagem,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        cv2.imshow("Cadastro - C captura | Q cancela", tela)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == TECLA_SAIR:
            break

        if tecla == TECLA_CAPTURAR:
            if rosto is None:
                print("A foto precisa conter exatamente um rosto.")
                continue

            brilho = frame.mean()

            if brilho < 50:
                print("Imagem muito escura. Melhore a iluminacao.")
                continue

            camera.release()
            cv2.destroyAllWindows()

            return frame, rosto.embedding

    camera.release()
    cv2.destroyAllWindows()

    return None, None


def cadastrar():
    consentimento = input(
        "Voce autoriza o cadastro da foto e biometria facial? [S/N]: "
    ).strip().upper()

    if consentimento != "S":
        print("Cadastro cancelado: consentimento nao fornecido.")
        return

    analisador = iniciar_analisador()
    foto, embedding = capturar_foto_cadastro(analisador)

    if foto is None:
        print("Cadastro cancelado.")
        return

    nome = input("Nome: ").strip()
    idade = input("Idade: ").strip()
    cpf = input("CPF ou identificador ficticio: ").strip()

    if not nome or not idade.isdigit() or not cpf:
        print("Dados invalidos. Cadastro cancelado.")
        return

    PASTA_FOTOS_CADASTRO.mkdir(parents=True, exist_ok=True)

    nome_arquivo = criar_nome_arquivo(nome)
    caminho_foto = PASTA_FOTOS_CADASTRO / nome_arquivo

    foto_salva = cv2.imwrite(str(caminho_foto), foto)

    if not foto_salva:
        print("Nao foi possivel salvar a foto de cadastro.")
        return

    embedding_json = json.dumps(embedding.tolist())

    try:
        cadastrar_pessoa(
            nome,
            int(idade),
            cpf,
            str(caminho_foto),
            embedding_json
        )

        print(f"{nome} foi cadastrado com sucesso.")

    except Exception as erro:
        print(f"Erro ao salvar o cadastro: {erro}")