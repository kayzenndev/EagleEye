import json
import re
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from banco import buscar_pessoas, registrar_captura


PASTA_REGISTROS = Path("dados/registros")
LIMIAR_SIMILARIDADE = 0.55
INTERVALO_REGISTRO_CAMERA = 5
PULAR_FRAMES_VIDEO = 5


def iniciar_analisador():
    analisador = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )

    analisador.prepare(ctx_id=0, det_size=(640, 800))

    return analisador

def normalizar_embedding(embedding):
    embedding = np.array(embedding, dtype=np.float32)
    norma = np.linalg.norm(embedding)

    if norma == 0:
        return embedding

    return embedding / norma

def carregar_pessoas():
    pessoas_banco = buscar_pessoas()
    pessoas = []

    for pessoa in pessoas_banco:
        id_pessoa, nome, idade, cpf, foto, embedding_json = pessoa

        pessoas.append({
            'id': id_pessoa,
            'nome': nome,
            'idade': idade,
            'cpf': cpf,
            'embedding': normalizar_embedding(
                json.loads(embedding_json)
            )
        })

    return pessoas

def encontrar_pessoa(embedding_atual, pessoas):
    embedding_atual = normalizar_embedding(embedding_atual)

    melhor_pessoa = None
    melhor_similaridade = -1

    for pessoa in pessoas:
        similaridade = float(
            np.dot(embedding_atual, pessoa["embedding"])
        )

        if similaridade > melhor_similaridade:
            melhor_similaridade = similaridade
            melhor_pessoa = pessoa

    if melhor_similaridade >= LIMIAR_SIMILARIDADE:
        return melhor_pessoa, melhor_similaridade

    return None, melhor_similaridade

def mascarar_cpf(cpf):
    if len(cpf) <= 4:
        return cpf

    return "*" * (len(cpf) - 4) + cpf[-4:] 

def nome_seguro(texto):
    return re.sub(r"[^a-zA-Z0-9_-]", "_", texto)

def salvar_rosto(frame, rosto, pessoa, origem, arquivo_origem):
    x1, y1, x2, y2 = rosto.bbox.astype(int)

    altura, largura = frame.shape[:2]

    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(largura, x2)
    y2 = min(altura, y2)

    recorte_rosto = frame[y1:y2, x1:x2]

    if recorte_rosto.size == 0:
        return

    PASTA_REGISTROS.mkdir(parents=True, exist_ok=True)

    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = nome_seguro(pessoa["nome"])

    nome_arquivo = f"{nome}_{origem}_{data_hora}.jpg"
    caminho_foto = PASTA_REGISTROS / nome_arquivo

    foto_salva = cv2.imwrite(str(caminho_foto), recorte_rosto)

    if foto_salva:
        registrar_captura(
            pessoa["id"],
            str(caminho_foto),
            origem,
            arquivo_origem
        )

        print(f"Registro salvo: {caminho_foto}")

def desenhar_resultado(frame, rosto, pessoa, similaridade):
    x1, y1, x2, y2 = rosto.bbox.astype(int)

    if pessoa is None:
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,0,255), 2)

        cv2.putText(
            frame,
            "Desconhecido",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,0,255),
            2
        )

        return

    cv2.rectangle(frame, (x1,y1), (x2, y2), (0,255,0), 2)

    texto_1 = pessoa["nome"]
    texto_2 = f"Idade: {pessoa['idade']}"
    texto_3 = f"CPF: {mascarar_cpf(pessoa['cpf'])}"
    texto_4 = f"Similaridade: {similaridade:.2f}"

    cv2.putText(
        frame,
        texto_1,
        (x1, y1 - 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        texto_2,
        (x1, y1 - 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        texto_3,
        (x1, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        texto_4,
        (x1, y2 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0,255,0),
        1
    )

def processar_frame(
    frame,
    analisador,
    pessoas,
    origem,
    arquivo_origem,
    instante,
    ultimos_registros
):
    tela = frame.copy()
    rostos = analisador.get(frame)

    for rosto in rostos:
        pessoa, similaridade, = encontrar_pessoa(
            rosto.embedding,
            pessoas
        )

        desenhar_resultado(tela, rosto, pessoa, similaridade)

        if pessoa is None:
            continue

        chave_registro = f"{origem}_{pessoa['id']}"
        ultimo_instante = ultimos_registros.get(chave_registro, -9999)

        if instante - ultimo_instante >= INTERVALO_REGISTRO_CAMERA:
            salvar_rosto(
                frame,
                rosto,
                pessoa,
                origem,
                arquivo_origem
            )

            ultimos_registros[chave_registro] = instante

    return tela

def reconhecer_webcam(analisador, pessoas):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print('Não foi possível acessar a câmera.')
        return

    ultimos_registros = {}

    print('Webcam aberta. Pressione Q para sair.')

    while True:
        sucesso, frame = camera.read()

        if not sucesso:
            break

        tela = processar_frame(
            frame,
            analisador,
            pessoas,
            "camera",
            None,
            time.monotonic(),
            ultimos_registros
        )

        cv2.imshow("Reconhecimento por webcam - Q sai", tela)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

def analisar_foto(caminho, analisador, pessoas):
    frame = cv2.imread(caminho)

    if frame is None:
        print("Não foi possível abrir a foto.")
        return

    tela = processar_frame(
        frame, 
        analisador,
        pessoas,
        "foto",
        caminho,
        0,
        {}
    )

    cv2.imshow("Resultado da foto - qualquer tecla fecha", tela)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def analisar_video(caminho, analisador, pessoas):
    video = cv2.VideoCapture(caminho)

    if not video.isOpened():
        print("Não foi possível abrir o vídeo.")
        return

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    indice_frame = 0
    ultimos_registros = {}

    print('Vídeo aberto. Pressione Q para sair.')

    while True:
        sucesso, frame = video.read()

        if not sucesso:
            break

        indice_frame += 1

        if indice_frame % PULAR_FRAMES_VIDEO == 0:
            instante_video = indice_frame / fps

            tela = processar_frame(
                frame,
                analisador,
                pessoas,
                "video",
                caminho,
                instante_video,
                ultimos_registros
            )

        else:
            tela = frame

        cv2.imshow("Analise de vídeo - Q sai", tela)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()

def menu_identificacao():
    pessoas = carregar_pessoas()

    if not pessoas:
        print('Não há pessoas cadastradas.')
        return

    analisador = iniciar_analisador()

    while True:
        print("""
[01] - Reconhecer pela Webcam
[02] - Analisar uma foto
[03] - Analisar um vídeo
[00] - Voltar
        """)

        opcao = float(input('Escolha uma opção: '))

        if opcao == 1:
            reconhecer_webcam(analisador, pessoas)

        elif opcao == 2:
            caminho = input('Caminho da foto: ').strip()
            analisar_foto(caminho, analisador, pessoas)

        elif opcao == 3:
            caminho = input('Caminho do vídeo: ').strip()
            analisar_video(caminho, analisador, pessoas)

        elif opcao == 0:
            break

        else:
            print('Opção inválida.')