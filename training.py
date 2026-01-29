import torch
import torchvision
import torchaudio
import os
import yaml
import matplotlib.pyplot as plt
from ultralytics import RTDETR
from collections import defaultdict

# ==============================================================================
# FUNÇÕES DE ANÁLISE DE DATASET
# ==============================================================================

def get_absolute_path(relative_path, yaml_path):
    """Converte caminho relativo para absoluto baseado na localização do YAML"""
    yaml_dir = os.path.dirname(yaml_path)
    return os.path.abspath(os.path.join(yaml_dir, relative_path))

def analyze_images_in_split(split_path, class_names):
    """Analisa a distribuição de classes em cada imagem individualmente"""
    # Assume que a pasta 'labels' está no mesmo nível da pasta 'images'
    labels_dir = split_path.replace('images', 'labels')

    if not os.path.exists(labels_dir):
        print(f"--- Erro: Diretório de labels não encontrado: {labels_dir}")
        return {}

    image_stats = {}
    for label_file in sorted(os.listdir(labels_dir)):
        if label_file.endswith('.txt'):
            image_name = label_file.replace('.txt', '.jpg')
            class_counts = defaultdict(int)

            with open(os.path.join(labels_dir, label_file), 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            class_id = int(line.split()[0])
                            class_counts[class_id] += 1
                        except (IndexError, ValueError):
                            continue
            image_stats[image_name] = class_counts
    return image_stats

def analyze_dataset_per_image(dataset_yaml):
    """Analisa a distribuição de classes por imagem em todo o dataset"""
    if not os.path.exists(dataset_yaml):
        return None, None

    with open(dataset_yaml, 'r') as f:
        dataset_info = yaml.safe_load(f)

    class_names = dataset_info['names']
    results = {}

    for split in ['train', 'val', 'test']:
        relative_path = dataset_info.get(split)
        if not relative_path:
            continue

        split_path = get_absolute_path(relative_path, dataset_yaml)
        print(f"Analisando split: {split}...")
        results[split] = analyze_images_in_split(split_path, class_names)

    return results, class_names

def plot_image_class_distribution(results, class_names):
    """Cria gráficos de barras empilhadas para cada split"""
    for split, images in results.items():
        if not images:
            continue

        plt.figure(figsize=(12, 6))
        plt.title(f"Distribuição de Classes por Imagem - {split.upper()}")

        image_names = list(images.keys())
        data = {i: [] for i in range(len(class_names))}

        for image, counts in images.items():
            for class_id in range(len(class_names)):
                data[class_id].append(counts.get(class_id, 0))

        bottom = [0] * len(image_names)
        for class_id in range(len(class_names)):
            plt.bar(image_names, data[class_id], label=f'ID {class_id}: {class_names[class_id]}', bottom=bottom)
            bottom = [bottom[i] + data[class_id][i] for i in range(len(image_names))]

        plt.xlabel('Imagens')
        plt.ylabel('Quantidade de Objetos')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        print(f"Exibindo gráfico do split {split}. Feche a janela para continuar.")
        plt.show()

# ==============================================================================
# FUNÇÃO PRINCIPAL DE TREINAMENTO
# ==============================================================================

def start_training(yaml_path, save_dir):
    """Configura o dispositivo e inicia o treinamento do RT-DETR"""
    # Define o dispositivo de hardware
    if torch.cuda.is_available():
        device_name = 0 # Usa a primeira GPU
        print(f"🚀 Iniciando treino na GPU: {torch.cuda.get_device_name(0)}")
    else:
        device_name = 'cpu'
        print("⚠️ CUDA não disponível. Treinando na CPU (será muito lento!).")

    # Carrega o modelo RT-DETR Large
    model = RTDETR("rtdetr-l.pt")

    # Garante que a pasta de resultados exista
    os.makedirs(save_dir, exist_ok=True)

    # Inicia o treinamento com os parâmetros de aumento de dados (Augmentation)
    model.train(
        data=yaml_path,
        name='rtdetr_large_upsampling_350epoch',
        epochs=350,
        batch=16,
        augment=True,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        fliplr=0.5,
        device=device_name,
        project=save_dir,
        save_period=50
    )

# ==============================================================================
# BLOCO DE EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    # CONFIGURAÇÕES DE CAMINHO (Altere aqui!)
    PATH_TO_YAML = "/home/renata/ml-gpr/gprDataset.yaml"
    PATH_TO_SAVE = "/home/renata/ml-gpr/results"

    # 1. Verificações de Versão
    print(f"--- Sistema: PyTorch {torch.version.cuda if torch.cuda.is_available() else 'CPU'}")
    
    # 2. Análise Detalhada
    if not os.path.exists(PATH_TO_YAML):
        print(f"❌ Erro: O arquivo {PATH_TO_YAML} não foi encontrado.")
    else:
        print("--- Iniciando análise de dados ---")
        results, names = analyze_dataset_per_image(PATH_TO_YAML)
        
        if results and any(results.values()):
            plot_image_class_distribution(results, names)
            
            # 3. Treinamento
            print("\n--- Iniciando fase de treinamento ---")
            start_training(PATH_TO_YAML, PATH_TO_SAVE)
        else:
            print("❌ Erro: Falha ao ler imagens ou labels. Verifique os caminhos dentro do seu YAML.")

    print("\nProcesso finalizado.")