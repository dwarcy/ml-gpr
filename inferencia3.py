import os
from ultralytics import RTDETR
import cv2
import numpy as np
import re

# ================================
# CONFIGURAÇÕES DO USUÁRIO
# ================================
modelo_path = "/home/renata/ml-gpr/best.pt"
imagens_dir = "/home/renata/ml-gpr/imagens/dzt_125_xyzcoordinates"
saida_dir = "/home/renata/ml-gpr/imagens/dzt_125_xyzcoordinates/resultados_inferencia"

print(f"Carregando modelo RT-DETR: {modelo_path}")
model = RTDETR(modelo_path)

# ================================
# CONFIGURAÇÃO DE CORTE (CROPPING)
# ================================
Y_START_CROP = 171
Y_END_CROP = -157 

X_START_CROP = 238
X_END_CROP = -190 

os.makedirs(saida_dir, exist_ok=True)

# ================================
# CORES POR CLASSE (OpenCV usa BGR)
# ================================
CORES = {
    0: (0, 255, 0),     # armadura = verde
    1: (0, 0, 255),     # ruim     = vermelho
    2: (255, 0, 0),     # vazio    = azul
}
COR_PADRAO = (255, 255, 255)  # caso apareça classe fora dessas 3

# ================================
# FUNÇÃO PARA EXTRAR X DO NOME 
# ================================
def extrair_x_inicial(nome_arquivo):
    match = re.search(r'_x(\d+\.\d+)m', nome_arquivo)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            print(f"Aviso: Não foi possível converter '{match.group(1)}' para float.")
            return 0.0
    return 0.0

# ================================
# FUNÇÃO PARA CALCULAR CENTRO
# ================================
def calcular_centro(x1, y1, x2, y2):
    return (x1 + x2) / 2, (y1 + y2) / 2

# ================================
# PROCESSAR IMAGENS DO DIRETÓRIO
# ================================
lista_imagens = sorted([f for f in os.listdir(imagens_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))])

print(f"{len(lista_imagens)} imagens encontradas para inferência.\n")

for img_nome in lista_imagens:

    img_caminho = os.path.join(imagens_dir, img_nome)
    print(f"Inferindo: {img_nome}")

    x_inicial_metros = extrair_x_inicial(img_nome)

    img_original = cv2.imread(img_caminho)
    if img_original is None:
        print(f"Erro ao abrir imagem: {img_caminho}")
        continue

    W_orig = img_original.shape[1]

    # === APLICAR CORTE ===
    try:
        img_cortada = img_original[Y_START_CROP:Y_END_CROP, X_START_CROP:X_END_CROP]
        img_para_inferencia = img_cortada.copy()
        print(f"  -> Imagem cortada para dimensão: {img_cortada.shape[1]}x{img_cortada.shape[0]}")
    except Exception as e:
        print(f"  ERRO ao cortar a imagem {img_nome}: {e}")
        img_cortada = img_original.copy()
        img_para_inferencia = img_original.copy()

    # === INFERÊNCIA ===
    results = model.predict(img_para_inferencia, conf=0.25)
    dets = results[0].boxes

    saida_txt = os.path.join(saida_dir, img_nome.rsplit(".", 1)[0] + ".txt")

    PIXELS_POR_METRO = W_orig

    with open(saida_txt, "w") as f:

        if dets is None or len(dets) == 0:
            f.write("Nenhuma detecção encontrada.\n")
            print("  -> Nenhuma detecção.")
            cv2.imwrite(os.path.join(saida_dir, img_nome), img_cortada)
            continue

        for caixa in dets:

            x1, y1, x2, y2 = caixa.xyxy[0].tolist()
            cx, cy = calcular_centro(x1, y1, x2, y2)

            classe = int(caixa.cls[0])
            conf = float(caixa.conf[0])

            # ========================
            # CÁLCULO EM METROS
            # ========================
            cx_pixel_na_original = cx + X_START_CROP
            distancia_metros_no_frame = cx_pixel_na_original / PIXELS_POR_METRO
            X_ABSOLUTO_METROS = x_inicial_metros + distancia_metros_no_frame

            # ========================
            # DESENHAR ANOTAÇÕES
            # ========================
            cor = CORES.get(classe, COR_PADRAO)

            # Retângulo da bbox
            cv2.rectangle(
                img_cortada,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                cor, 2
            )

            # Texto da classe/confiança
            texto = f"{classe} ({conf:.2f})"
            cv2.putText(
                img_cortada,
                texto,
                (int(x1), int(y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                cor,
                1,
                cv2.LINE_AA
            )

            # ========================
            # DESENHAR PONTO NO CENTRO
            # ========================
            cv2.circle(
                img_cortada,
                (int(cx), int(cy)),
                3,
                cor,
                -1
            )

            # ========================
            # SALVAR TXT
            # ========================
            f.write(
                f"classe={classe}, conf={conf:.3f}, "
                f"x_abs_m={X_ABSOLUTO_METROS:.3f}, "
                f"x1={x1:.2f}, y1={y1:.2f}, x2={x2:.2f}, y2={y2:.2f}, "
                f"centro=({cx:.2f}, {cy:.2f})\n"
            )

        print(f"  -> {len(dets)} detecções salvas em {saida_txt}")

    # SALVAR IMAGEM FINAL
    saida_img = os.path.join(saida_dir, img_nome)
    cv2.imwrite(saida_img, img_cortada)
    print(f"  -> Imagem anotada salva em {saida_img}")

print("\nProcessamento concluído!")
print(f"Resultados salvos em: {saida_dir}")